#!/usr/bin/env python3
"""
Project Volt - WS8 - Vehicle One semi-scale architecture trial.
SINGLE ENTRY POINT (CLAUDE.md rule 1).

    ../.venv/bin/python run_ws8.py            full deterministic run
    ../.venv/bin/python run_ws8.py --quick    2 seeds, nominal only (dev)
    ../.venv/bin/python run_ws8.py --jobs 3   parallel across corners

Writes results_ws8.json plus data/*.csv. Fixed seeds throughout; re-running
reproduces every artifact byte-identically (CLAUDE.md rule 1), which
verify_ws8.py checks along with the report's headline numbers.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
from collections import OrderedDict

import numpy as np

import ws8_candidates as CD
import ws8_cycles as CY
import ws8_electric as EL
import ws8_engine as EN
import ws8_physics as PH
import ws8_whr as WHR
from ws8_params import (
    VEH, ADH, AUX, DL, ML, SC, CY as CYP, G,
    LHV_KJ_PER_G, DIESEL_DENSITY_KG_PER_L, params_dump,
    ENGINE_HEAT_TO_COOLANT_FRAC as PARAM_ENGINE_HEAT_TO_COOLANT_FRAC)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

# --------------------------------------------------------------- fleet mix
FLEET_MIX = OrderedDict([("LH-520", 0.70), ("REG-165", 0.30)])
"""The FLEET MISSION, declared. [WS8-PROV] 70% of distance on the line-haul
corridor, 30% on the regional cycle. The advance/kill criteria are written
against "fleet-mission fuel", so this blend has to be stated before the
numbers are read, not chosen after. It is applied identically to every
candidate and to S0, so it cannot decide which candidate wins - it can only
decide by how much."""

CAL_BAND_L_PER_100KM = (30.0, 38.0)
"""The assignment's sanity corridor for loaded line-haul, quoted verbatim
from Task 2. S0's simulated fleet fuel is checked against this; no fudge
factor sits between the physics and the check."""


# =====================================================================
#  corners (Task 5)
# =====================================================================
def corners(quick=False):
    c = OrderedDict()
    c["nominal"] = CD.Ctx("nominal", label="20 C, sea level, nominal payload")
    if quick:
        return c
    c["payload_plus20"] = CD.Ctx(
        "payload_plus20", payload_factor=1.20,
        label="payload +20% (GCW rises with it: fixed GCW is a Task-3 "
              "condition, not a Task-5 one)")
    c["payload_minus20"] = CD.Ctx(
        "payload_minus20", payload_factor=0.80,
        label="payload -20%")
    c["grade_heavy"] = CD.Ctx(
        "grade_heavy", grade_heavy=True,
        label="grade-heavy corridor: sustained sections at the top of the "
              "2-3% band, rolling background doubled, mountain unchanged")
    c["cold_minus10C"] = CD.Ctx(
        "cold_minus10C", rho_air=VEH.rho_air_cold, t_amb_c=-10.0, cold=True,
        label="-10 C: denser air, electrified accessory load up, WS3 cold "
              "charge acceptance APPLIED (r2 - it was not, in r1: finding "
              "F2), tyre Crr up 8%")
    # R28: the corner set of record for Vehicle One includes 2,000 m /
    # +45 C, on the Vehicle Zero precedent that the altitude/hot corner
    # is the one that became worst. It is also the corner that exercises
    # WS4's ruled `derate_factor`, which r1 listed in its provenance and
    # never called (finding F11).
    c["hot_alt_2000m_45C"] = CD.Ctx(
        "hot_alt_2000m_45C", rho_air=VEH.rho_air_hot_alt,
        t_amb_c=VEH.t_amb_c_hot_alt, alt_m=VEH.alt_m_hot_alt, hot=True,
        label="2,000 m / +45 C (R28): WS4 derate_factor 0.9312 on every "
              "engine's full-load curve and therefore on every R18 "
              "continuous rating, thinner air (rho 0.871), cab COOLING "
              "charged to crank and bus alike")
    return c


def corner_crr(ctx):
    """Rolling resistance at the corner. [WS8-PROV] Crr rises in the cold
    (stiffer compound, colder inflation); +8% at -10 C is class-typical."""
    return VEH.Crr * (1.08 if ctx.cold else 1.0)


def make_candidate(name, ctx, whr=None, **kw):
    return CD.CANDIDATES[name](ctx=ctx, whr=whr, **kw)


def candidate_gcw(cand):
    """GCW at this corner. At nominal it is exactly the assignment's fixed
    36,300 kg; the payload sensitivities move payload, and the combination
    mass moves with it."""
    return cand.tare_common_kg() + cand.powertrain_mass_kg() \
        + cand.payload_kg()


def candidate_drive_axle_kg(cand):
    """Drive-axle load, scaled with GCW from the nominal legal split."""
    return VEH.m_axle_drive_tandem_kg * candidate_gcw(cand) / VEH.m_gcw


# =====================================================================
#  one (candidate, corner, cycle, seed) run
# =====================================================================
def run_one(cand, cycle, seed, tables=None):
    m = candidate_gcw(cand)
    crr = corner_crr(cand.ctx)
    dp = PH.DriverParams()
    tr = PH.integrate_achieved(
        cycle, cand.envelope, m, cand.lam, dp, seed,
        cda=VEH.CdA, crr=crr, rho=cand.ctx.rho_air,
        v_wind=cycle["v_wind"], v_cap_fn=cand.v_cap, env_tables=tables)
    met = PH.trace_metrics(tr, m, cda=VEH.CdA, crr=crr, rho=cand.ctx.rho_air)
    acc = cand.account(tr)
    # THE PER-RUN ASSERTION R3_DIRECTIVE item 1 ORDERS, at the only place
    # that sees every run before anything aggregates it. It is HARD: on
    # the run of record a violation is a bug in the control law, not a
    # number to report. It is skipped only when the B1 errata switch is
    # deliberately reverted, which is the one-factor row that exists to
    # measure what the violation was worth.
    ex = acc.get("exclusivity")
    if ex is None:
        raise AssertionError(
            f"{cand.name}: account() returned no `exclusivity` block - "
            "the B1 assertion cannot be skipped by omission")
    if CD.errata_on("b1_overrun_exclusivity") and not ex["holds"]:
        raise AssertionError(
            f"{cand.name}: {ex['samples_brake_and_shaft']} samples carry "
            f"BOTH compression-brake power (max "
            f"{ex['max_simultaneous_engine_brake_kW']:.1f} kW) and "
            f"positive engine shaft power (max "
            f"{ex['max_simultaneous_shaft_kW']:.1f} kW). One crankshaft "
            "cannot be in both states (finding B1).")
    acc = apply_energy_corrections(cand, acc)
    out = dict(met)
    out.update(acc)
    out["gcw_kg"] = m
    out["payload_kg"] = cand.payload_kg()
    out["fuel_L_per_100km"] = EN.fuel_L_per_100km(acc["fuel_g_corrected"],
                                                  tr["distance_m"])
    out["MJ_per_km"] = acc["e_fuel_MJ_corrected"] / met["distance_km"]
    out["MJ_per_payload_tkm"] = (acc["e_fuel_MJ_corrected"]
                                 / (cand.payload_kg() / 1000.0)
                                 / met["distance_km"])
    # exact re-pricings of THIS run, for the one-factor rows: F4 (the
    # charge-sustaining credit suppressed) and F6 (corrections priced at
    # r1's peak-point efficiency). Neither needs a re-simulation.
    for suffix in ("deficit_only", "r1_pricing"):
        out[f"MJ_per_km_{suffix}"] = (
            acc[f"e_fuel_MJ_corrected_{suffix}"] / met["distance_km"])
        out[f"MJ_per_payload_tkm_{suffix}"] = (
            acc[f"e_fuel_MJ_corrected_{suffix}"]
            / (cand.payload_kg() / 1000.0) / met["distance_km"])
    return out


CORRECTION_ETA_BOUNDS = (0.10, 0.50)
"""Sanity bounds on the duty-averaged correction efficiency [-]. A
marginal duty-average can be noisy on a run where the genset barely ran;
the bounds stop a degenerate denominator from turning a small correction
into a large one, and every clipped case is flagged in the record."""


def genset_eta_for_correction(cand, acc=None):
    """Fuel-to-bus efficiency used to price stored and unserved energy.

    r1 finding F6 (material, rule 5): this used to return the MAXIMUM of
    the fuel-to-bus efficiency curve - `line.best_point()` - and for S3,
    which has no genset, the engine's ISLAND BSFC times the axle-A
    driveline. A peak-point scalar, sitting on the largest single
    correction in the trial (23.4% of S3's fuel on one case). Rule 5
    forbids exactly that.

    r2: the correction is priced at the candidate's OWN DUTY-AVERAGED
    efficiency over the run being corrected.

      S1, S2, S4 - genset path: bus energy the genset actually delivered
        over the fuel it actually burned to deliver it (for S2, the
        MARGINAL crank fuel while locked, since the engine is burning
        fuel to drive the wheels there regardless).
      S3 - no genset: the mechanical path it actually has, axle A's own
        duty-averaged fuel-to-WHEEL efficiency. Note the direction: the
        shortfall being priced is BUS-side, so a fuel-to-wheel
        efficiency is the GENEROUS end, and it is still far below the
        island. The capability statement stands separately and is not
        replaced by this number - section 6.2 shows the mechanical path
        cannot deliver that energy on the grade AT ANY RATIO, so the
        fuel equivalent is a bookkeeping device for comparing missions,
        not a claim that S3 could have done it.

    Returns (eta, basis_string, clipped_flag)."""
    lo, hi = CORRECTION_ETA_BOUNDS
    if acc is not None:
        f_gen = acc.get("fuel_g_genset", 0.0) or 0.0
        e_bus = acc.get("e_genset_bus_kWh", 0.0) or 0.0
        if f_gen > 1.0 and e_bus > 1e-6:
            eta = e_bus * 3600.0 / (f_gen * LHV_KJ_PER_G)
            return (float(np.clip(eta, lo, hi)),
                    "duty-averaged genset fuel-to-bus over this run",
                    bool(eta < lo or eta > hi))
        e_wheel = acc.get("e_mech_wheel_kWh", 0.0) or 0.0
        f_tot = acc.get("fuel_g", 0.0) or 0.0
        if e_wheel > 1e-6 and f_tot > 1.0:
            eta = e_wheel * 3600.0 / (f_tot * LHV_KJ_PER_G)
            return (float(np.clip(eta, lo, hi)),
                    "duty-averaged mechanical fuel-to-wheel over this run "
                    "(no genset exists; bus-side shortfall priced on the "
                    "wheel-side path, the generous direction)",
                    bool(eta < lo or eta > hi))
    # Fallbacks, used only where the candidate's own path did not run at
    # all on this cycle (so there is no duty average to take). Declared
    # rather than silently substituted.
    line = getattr(cand, "line", None)
    if line is not None:
        return (line.best_point()["genset_eta_fuel_to_bus"],
                "FALLBACK: genset best point (the path did not run on "
                "this cycle, so there is no duty average)", False)
    eng = getattr(cand, "engine", None)
    if eng is not None:
        eta_eng = 3600.0 / (eng.min_bsfc_point()["bsfc"] * LHV_KJ_PER_G)
        return (eta_eng * getattr(cand, "eta_A", DL.eta_axle_tandem),
                "FALLBACK: island BSFC x axle-A driveline (the path did "
                "not run on this cycle)", False)
    return 0.40, "FALLBACK: default", False


def apply_energy_corrections(cand, acc):
    """Two corrections, both stated, both applied to every candidate that
    has a pack so no candidate is flattered by bookkeeping.

    1. CHARGE-SUSTAINING CORRECTION. A hybrid that finishes the mission
       with a flatter pack than it started has imported propulsion energy
       the fuel figure never saw. The deficit is priced back into fuel at
       the candidate's own fuel-to-bus efficiency (SAE J1711 in spirit).
       S4 is the candidate this exists for, and it is applied to S1, S2
       and S3 identically.

    2. UNSERVED-ENERGY CORRECTION. Where a candidate's prime mover and
       pack together could not deliver the demanded power, the shortfall
       is charged as fuel at the same efficiency, so that EVERY candidate
       is compared having completed the SAME mission at the SAME speeds.
       The raw shortfall is reported alongside, because a large one is a
       capability finding in its own right and must not be allowed to
       disappear into a fuel number.

    THE CONVENTION ON DIRECTION, DECLARED (r1 finding F4). Correction 1
    is SYMMETRIC, in the spirit of SAE J1711: a pack that ends FLATTER
    than it started is charged the make-up, and a pack that ends FULLER
    than it started earns the corresponding CREDIT. That is the
    convention of record and it is applied identically to every
    candidate that has a pack. It matters, and r1 did not say so: S2
    ends the dominant LH-520 cycle well above its 0.60 target - regen
    put the surplus there, not fuel, and its dispatch has no mechanism
    to spend a pack that sits above target - so its symmetric correction
    is a CREDIT worth about a point of its fuel, and about half of its
    headline advantage over S1.

    So that the credit can never again be invisible, r2 exports:
      * `fuel_g_charge_correction` SIGNED (negative = credit), with the
        share exported min AND max rather than max alone;
      * `fuel_g_corrected_deficit_only`, the same run with the credit
        suppressed and the deficit make-up kept - the credit-free
        variant, reported alongside the margin of record so the
        S1-vs-S2 ordering is visible for what it is.
    """
    eta, eta_basis, eta_clipped = genset_eta_for_correction(cand, acc)
    usable = getattr(getattr(cand, "pack", None), "usable_kwh", 0.0)
    d_soc = acc.get("soc_end", 0.0) - acc.get("soc_start", 0.0)
    e_deficit_kwh = -d_soc * usable                 # >0 => pack ran down
    e_unserved_kwh = acc.get("unserved_kWh", 0.0)
    # kWh -> g of fuel at eta (bus-side) : kWh*3600 kJ / (eta * LHV kJ/g)
    to_g = 3600.0 / max(eta * LHV_KJ_PER_G, 1e-9)
    g_soc = e_deficit_kwh * to_g
    g_uns = e_unserved_kwh * to_g
    acc = dict(acc)
    acc["fuel_g_raw"] = acc["fuel_g"]
    acc["charge_sustain_deficit_kWh"] = e_deficit_kwh
    acc["fuel_g_charge_correction"] = g_soc
    acc["fuel_g_charge_correction_is_credit"] = bool(g_soc < 0.0)
    acc["fuel_g_unserved_correction"] = g_uns
    acc["correction_eta_fuel_to_bus"] = eta
    acc["correction_eta_basis"] = eta_basis
    acc["correction_eta_clipped"] = eta_clipped
    # r1's pricing, carried alongside so the F6 one-factor row is an
    # EXACT re-pricing of this same run rather than a re-simulation.
    eta_r1, eta_r1_basis, _ = genset_eta_for_correction(cand, None)
    acc["correction_eta_r1_peak_point"] = eta_r1
    acc["correction_eta_r1_basis"] = eta_r1_basis
    to_g_r1 = 3600.0 / max(eta_r1 * LHV_KJ_PER_G, 1e-9)
    acc["fuel_g_corrected_r1_pricing"] = (
        acc["fuel_g"] + (e_deficit_kwh + e_unserved_kwh) * to_g_r1)
    acc["fuel_g_corrected"] = acc["fuel_g"] + g_soc + g_uns
    acc["e_fuel_MJ_corrected"] = EN.fuel_energy_MJ(acc["fuel_g_corrected"])
    acc["correction_share_of_fuel"] = (
        (g_soc + g_uns) / acc["fuel_g_corrected"]
        if acc["fuel_g_corrected"] > 0 else 0.0)
    # credit-free variant (F4), reported alongside, never substituted
    g_soc_def = max(g_soc, 0.0)
    acc["fuel_g_corrected_deficit_only"] = acc["fuel_g"] + g_soc_def + g_uns
    acc["e_fuel_MJ_corrected_deficit_only"] = EN.fuel_energy_MJ(
        acc["fuel_g_corrected_deficit_only"])
    acc["e_fuel_MJ_corrected_r1_pricing"] = EN.fuel_energy_MJ(
        acc["fuel_g_corrected_r1_pricing"])
    return acc


def ensemble(vals):
    a = np.asarray([v for v in vals if v is not None and np.isfinite(v)],
                   float)
    if a.size == 0:
        return dict(n=0, min=None, median=None, max=None, mean=None)
    return dict(n=int(a.size), min=float(np.min(a)),
                median=float(np.median(a)), max=float(np.max(a)),
                mean=float(np.mean(a)))


# =====================================================================
#  the trial
# =====================================================================
def run_candidate(corner_name, cname, whr_name, seeds, errata=None):
    """One (corner, candidate) job. Self-contained and deterministic, so it
    can be run in a worker process without changing a single digit: it
    reconstructs its own context and candidate from names rather than
    receiving live objects, and every random draw is seeded."""
    # the errata set is passed IN and applied at the start of the job,
    # so a worker process cannot inherit a stale one (the run of record
    # passes None and gets the full set).
    CD.set_errata(errata)
    ctx = corners(quick=False)[corner_name] if corner_name in corners(False) \
        else CD.NOMINAL
    whr = WHR.SYSTEMS[whr_name] if whr_name else None
    t0 = time.time()
    cand = make_candidate(cname, ctx, whr=whr)
    if whr is not None and cname not in whr.applies_to:
        return cname, None
    cycles = {
        "LH-520": [CY.build_linehaul(sd, grade_heavy=ctx.grade_heavy)
                   for sd in seeds],
        "REG-165": [CY.build_regional(sd, grade_heavy=ctx.grade_heavy)
                    for sd in seeds],
    }
    tables = PH.build_env_tables(cand.envelope, cand.lam)
    per_cycle = OrderedDict()
    for cyname, cyl in cycles.items():
        rows = []
        for sd, cyc in zip(seeds, cyl):
            r = run_one(cand, cyc, sd, tables=tables)
            r["seed"] = int(sd)
            rows.append(r)
        per_cycle[cyname] = rows
    fleet = []
    for i, sd in enumerate(seeds):
        mj_per_km = sum(FLEET_MIX[c] * per_cycle[c][i]["MJ_per_km"]
                        for c in FLEET_MIX)
        mj_per_km_do = sum(FLEET_MIX[c]
                           * per_cycle[c][i]["MJ_per_km_deficit_only"]
                           for c in FLEET_MIX)
        mj_per_km_r1 = sum(FLEET_MIX[c]
                           * per_cycle[c][i]["MJ_per_km_r1_pricing"]
                           for c in FLEET_MIX)
        l_per_100 = sum(FLEET_MIX[c] * per_cycle[c][i]["fuel_L_per_100km"]
                        for c in FLEET_MIX)
        payload_t = per_cycle["LH-520"][i]["payload_kg"] / 1000.0
        fleet.append(dict(seed=int(sd), MJ_per_km=mj_per_km,
                          L_per_100km=l_per_100, payload_t=payload_t,
                          MJ_per_payload_tkm=mj_per_km / payload_t,
                          MJ_per_payload_tkm_deficit_only=(mj_per_km_do
                                                           / payload_t),
                          MJ_per_payload_tkm_r1_pricing=(mj_per_km_r1
                                                         / payload_t)))
    return cname, dict(
        spec=cand.spec(), per_cycle=per_cycle, fleet=fleet,
        fleet_ensemble=dict(
            MJ_per_payload_tkm=ensemble(
                [f["MJ_per_payload_tkm"] for f in fleet]),
            L_per_100km=ensemble([f["L_per_100km"] for f in fleet]),
            MJ_per_km=ensemble([f["MJ_per_km"] for f in fleet])),
        runtime_s=time.time() - t0)


def _job(args):
    return run_candidate(*args)


def run_corner(corner_name, ctx, seeds, whr=None, cand_names=None,
               verbose=True, pool=None, whr_name=None, errata=None):
    """Every candidate over both cycles over the seed ensemble.

    Jobs are independent by construction (each reconstructs its own
    context and is fully seeded), so they may be run in a process pool.
    Results are re-ordered into `cand_names` order before use, so the
    output - and therefore results_ws8.json - is byte-identical whether
    the run was parallel or serial."""
    cand_names = cand_names or ["S0", "S1", "S2", "S3", "S4"]
    jobs = [(corner_name, c, whr_name, tuple(seeds),
             None if errata is None else tuple(errata))
            for c in cand_names]
    if pool is not None:
        results = dict(r for r in pool.map(_job, jobs) if r[1] is not None)
    else:
        results = dict(r for r in (_job(j) for j in jobs) if r[1] is not None)
    out = OrderedDict()
    for cname in cand_names:
        if cname not in results:
            continue
        out[cname] = results[cname]
        if verbose:
            e = out[cname]["fleet_ensemble"]["MJ_per_payload_tkm"]
            print(f"    {cname}: payload "
                  f"{out[cname]['spec']['payload_kg']:7.0f} kg  "
                  f"fleet {e['median']:.4f} MJ/payload-tkm  "
                  f"({out[cname]['runtime_s']:.0f} s)", flush=True)
    return out


def margins_vs_s0(corner_result, seeds):
    """Per-seed margin against S0 on the SAME seed, then the ensemble.

    Paired by seed deliberately: the seed sets the corridor, the wind and
    the driver, so comparing candidate seed i against S0 seed i removes
    the cycle draw from the comparison instead of leaving it in the
    variance. The ensemble envelope that results is a spread of
    ARCHITECTURE differences, not of weather."""
    if "S0" not in corner_result:
        return {}
    s0 = {f["seed"]: f["MJ_per_payload_tkm"]
          for f in corner_result["S0"]["fleet"]}
    s0_do = {f["seed"]: f["MJ_per_payload_tkm_deficit_only"]
             for f in corner_result["S0"]["fleet"]}
    s0_r1 = {f["seed"]: f["MJ_per_payload_tkm_r1_pricing"]
             for f in corner_result["S0"]["fleet"]}
    s0_km = {f["seed"]: f["MJ_per_km"] for f in corner_result["S0"]["fleet"]}
    s0_km_med = float(np.median(list(s0_km.values())))
    out = OrderedDict()
    for cname, r in corner_result.items():
        if cname == "S0":
            continue
        per_seed = []
        for f in r["fleet"]:
            base = s0.get(f["seed"])
            if base:
                per_seed.append(dict(
                    seed=f["seed"],
                    margin_pct=(base - f["MJ_per_payload_tkm"]) / base * 100.0,
                    margin_pct_deficit_only=(
                        (s0_do[f["seed"]]
                         - f["MJ_per_payload_tkm_deficit_only"])
                        / s0_do[f["seed"]] * 100.0),
                    # r2 finding M2: the per-km headline was a RATIO OF
                    # MEDIANS while every margin in the report is the
                    # median of PAIRED PER-SEED margins, and for S3 the
                    # two differ in SIGN. The paired statistic is
                    # computed here, on the same seeds and the same rule
                    # as the metric of record.
                    margin_pct_per_km=(
                        (s0_km[f["seed"]] - f["MJ_per_km"])
                        / s0_km[f["seed"]] * 100.0),
                    # F6's one-factor variant, available at EVERY corner
                    # because it is an exact re-pricing of the same run
                    margin_pct_r1_pricing=(
                        (s0_r1[f["seed"]]
                         - f["MJ_per_payload_tkm_r1_pricing"])
                        / s0_r1[f["seed"]] * 100.0)))
        km_vals = [p["margin_pct_per_km"] for p in per_seed]
        cand_km_med = float(np.median([f["MJ_per_km"] for f in r["fleet"]]))
        out[cname] = dict(
            per_seed=per_seed,
            ensemble=ensemble([p["margin_pct"] for p in per_seed]),
            # F4: the same margin with the charge-sustaining CREDIT
            # suppressed (the deficit make-up is kept). Reported
            # alongside, never substituted for the metric of record.
            ensemble_deficit_only=ensemble(
                [p["margin_pct_deficit_only"] for p in per_seed]),
            ensemble_r1_pricing=ensemble(
                [p["margin_pct_r1_pricing"] for p in per_seed]),
            per_km=dict(
                basis=("PAIRED per-seed margin on fleet-mission MJ per "
                       "KILOMETRE, then the 8-seed envelope - the same "
                       "statistic as the metric of record, on the other "
                       "denominator. Per M2, the ratio of medians is "
                       "exported alongside for disclosure and is NOT the "
                       "statistic any claim in this report is made on."),
                ensemble=ensemble(km_vals),
                n_seeds=len(km_vals),
                n_seeds_below_zero=int(sum(1 for x in km_vals if x < 0.0)),
                seeds_below_zero=[p["seed"] for p in per_seed
                                  if p["margin_pct_per_km"] < 0.0],
                wins_on_every_seed=bool(all(x > 0.0 for x in km_vals)),
                ratio_of_medians_pct=((s0_km_med - cand_km_med)
                                      / s0_km_med * 100.0),
                ratio_of_medians_sign_differs=bool(
                    (s0_km_med - cand_km_med) * float(np.median(km_vals))
                    < 0.0)))
    return out


# =====================================================================
#  main
# =====================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--from-checkpoint", action="store_true",
                    help="skip the simulation and rebuild the derived "
                         "blocks from data/_checkpoint.json. The "
                         "checkpoint holds the raw trial data, so this "
                         "reproduces exactly what a full run would "
                         "produce - it exists so that a bug in a "
                         "reporting block cannot cost an hour of "
                         "simulation.")
    ap.add_argument("--only-nominal", action="store_true",
                    help="run the full 8-seed nominal corner and stop "
                         "before the sensitivities. Used for the "
                         "determinism check: re-running this and diffing "
                         "the nominal slice proves the simulation is "
                         "byte-reproducible without paying for all five "
                         "corners twice.")
    ap.add_argument("--resume", action="store_true",
                    help="reuse corners already present in "
                         "data/_checkpoint.json instead of re-simulating "
                         "them. Each corner is checkpointed as it "
                         "completes, so an interrupted run resumes at the "
                         "corner it was on rather than from the start. "
                         "The results are identical either way - every "
                         "job is seeded and independent.")
    ap.add_argument("--jobs", type=int, default=0,
                    help="worker processes; 0 = serial. Results are "
                         "identical either way (every job is seeded and "
                         "independent); this only changes wall-clock.")
    args = ap.parse_args()

    t_start = time.time()
    if args.from_checkpoint:
        return _rebuild_from_checkpoint(args)
    seeds = CY.seeds()
    if args.quick:
        seeds = seeds[:2]
    if args.seeds:
        seeds = seeds[:args.seeds]

    pool = None
    if args.jobs and args.jobs > 1:
        import multiprocessing as mp
        pool = mp.get_context("fork").Pool(args.jobs)

    ckpt = {}
    if args.resume and os.path.exists(CHECKPOINT):
        try:
            ckpt = json.load(open(CHECKPOINT), object_pairs_hook=OrderedDict)
            done = list(ckpt.get("task3_trial", {}))
            print(f"== resuming; corners already on disk: {done} ==",
                  flush=True)
        except (ValueError, OSError) as e:
            print(f"== checkpoint unreadable ({e}); starting fresh ==",
                  flush=True)
            ckpt = {}

    R = OrderedDict()
    R["_meta"] = OrderedDict(
        workstream="WS8",
        vehicle="Vehicle One (Class 8 6x4 tractor + van trailer)",
        assignment="WS8_semi_architecture/ASSIGNMENT.md",
        baseline_of_record="BASELINE_v5.md",
        errata_round="WS8_semi_architecture/R3_DIRECTIVE.md (R35); numbers r3, verdicts executed under R25",
        errata_round_id="r3",
        supersedes_round="r2 (R2_DIRECTIVE.md under R26)",
        python=platform.python_version(),
        numpy=np.__version__,
        seeds=[int(s) for s in seeds],
        n_seeds=len(seeds),
        quick=bool(args.quick),
        fleet_mix=dict(FLEET_MIX),
        conventions=[
            "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6)",
            "part-load models everywhere, no peak-point scalars (rule 5)",
            "stochastic extrema are 8-seed ensemble envelopes (rule 4)",
            "R14: every machine-readable worst-case field is an explicit "
            "max/min over an enumerated case set with the governing case "
            "labelled inline",
            "R12 chain: traction side = WS2 r4 measured maps x 0.97 "
            "reduction, no scalar PE member; genset-side rectifier in the "
            "generator model",
            "metric of record: fuel energy per PAYLOAD tonne-km",
        ])
    R["params"] = params_dump()

    # ---------------------------------------------------------- Task 0
    print("== TASK 0: prior-art claim map ==", flush=True)
    R["task0_prior_art"] = load_prior_art()
    print(f"   status: {R['task0_prior_art']['status']}", flush=True)

    # ---------------------------------------------------------- Task 1
    print("== TASK 1: duty cycles, 10 Hz, 8-seed ensembles ==", flush=True)
    R["task1_cycles"] = build_cycle_record(seeds)
    for cn, cd in R["task1_cycles"]["cycles"].items():
        print(f"   {cn}: {cd['ensemble']['distance_km']['median']:.1f} km, "
              f"grade max {cd['ensemble']['grade_max']['max']:+.4f} / "
              f"min {cd['ensemble']['grade_min']['min']:+.4f}, "
              f"climb {cd['ensemble']['total_climb_m']['median']:.0f} m",
              flush=True)

    # ---------------------------------------------------------- Task 2/3
    print("== TASK 2/3: S0 calibration + candidate trial (nominal) ==",
          flush=True)
    cs = corners(quick=args.quick)
    if args.only_nominal:
        cs = OrderedDict([("nominal", cs["nominal"])])
    trial = OrderedDict()
    _ck_trial = ckpt.get("task3_trial", {})
    if "nominal" in _ck_trial:
        print("    [nominal from checkpoint]", flush=True)
        trial["nominal"] = _ck_trial["nominal"]
    else:
        trial["nominal"] = run_corner("nominal", cs["nominal"], seeds,
                                      pool=pool)
    R["task3_trial"] = trial
    R["task3_margins"] = OrderedDict()
    R["task3_margins"]["nominal"] = margins_vs_s0(trial["nominal"], seeds)

    R["task2_s0_calibration"] = (
        ckpt.get("task2_s0_calibration")
        or s0_calibration_record(trial["nominal"]))
    if "flat_corridor_crosscheck" not in R["task2_s0_calibration"]:
        R["task2_s0_calibration"]["flat_corridor_crosscheck"] = \
            s0_flat_crosscheck(seeds, cs["nominal"])
    _save_checkpoint(R)
    _fx = R["task2_s0_calibration"]["flat_corridor_crosscheck"]
    print(f"   S0 flat-corridor cross-check "
          f"{_fx['L_per_100km']['median']:.2f} L/100 km vs ICCT typical "
          f"{ICCT_TYPICAL_L_PER_100KM} / at-regulatory-payload "
          f"{ICCT_AT_REG_PAYLOAD_L_PER_100KM}", flush=True)
    print(f"   S0 fleet fuel "
          f"{R['task2_s0_calibration']['fleet_L_per_100km']['median']:.2f} "
          f"L/100 km  (corridor {CAL_BAND_L_PER_100KM[0]}-"
          f"{CAL_BAND_L_PER_100KM[1]}): "
          f"{R['task2_s0_calibration']['in_corridor_all_seeds']}", flush=True)

    # ---------------------------------------------------------- Task 4
    print("== TASK 4: WHR gate ==", flush=True)
    R["task4_whr"] = (ckpt.get("task4_whr")
                      or run_whr_gate(seeds, cs["nominal"], trial["nominal"],
                                      pool=pool))
    _save_checkpoint(R)
    for k, v in R["task4_whr"]["results"].items():
        print(f"   {k}: best net {v['best_net_margin_pct_median']:+.2f}% "
              f"-> {v['verdict']}", flush=True)

    # ---------------------------------------------------------- Task 5
    print("== TASK 5: sensitivities ==", flush=True)
    for cname, ctx in cs.items():
        if cname == "nominal":
            continue
        if cname in _ck_trial:
            print(f"  corner {cname} [from checkpoint]", flush=True)
            trial[cname] = _ck_trial[cname]
        else:
            print(f"  corner {cname}", flush=True)
            trial[cname] = run_corner(cname, ctx, seeds, pool=pool)
        R["task3_margins"][cname] = margins_vs_s0(trial[cname], seeds)
        # checkpoint after EVERY corner: an interrupted run then resumes
        # at the corner it was on, not from the start.
        _save_checkpoint(R)

    _save_checkpoint(R)

    R["task5_s3_specific"] = s3_specific_risks()
    R["two_speed_bracket"] = two_speed_bracket(trial["nominal"])

    # ---- one-factor rows: which correction decides S1 vs S2 ----------
    print("== one-factor rows (S1 vs S2, R2_DIRECTIVE item 3) ==",
          flush=True)
    R["one_factor"] = (ckpt.get("one_factor")
                       or one_factor_rows(trial["nominal"], cs["nominal"],
                                          seeds, pool=pool))
    _save_checkpoint(R)
    for k, v in R["one_factor"]["rows"].items():
        print(f"   {k:34s} S1 {v['S1']['median']:+.2f}%  "
              f"S2 {v['S2']['median']:+.2f}%  -> "
              f"{v['ordering_on_median']}", flush=True)

    # ------------------------------------------------- advance / kill
    R["advance_kill"] = advance_kill(R["task3_margins"])
    R["correction_directions"] = correction_directions(R)
    R["corner_derate_scope"] = corner_derate_scope()
    print("== correction directions (r2 finding M1, generated) ==",
          flush=True)
    for k, v in R["correction_directions"].items():
        if k.startswith("_"):
            continue
        print(f"   {k:11s} {v['direction']}", flush=True)
    print("== ADVANCE/KILL ==", flush=True)
    for k, v in R["advance_kill"]["candidates"].items():
        wc = v["worst_corner_margin_pct_min"]
        wtxt = (f"{wc:+.2f}% @ {v['worst_corner']}" if wc is not None
                else "no corners run")
        print(f"   {k}: {v['verdict']}  (nominal min "
              f"{v['nominal_margin_pct_min']:+.2f}%, worst corner "
              f"{wtxt})", flush=True)

    print("== heat ledger (rule 7, for WS6) ==", flush=True)
    R["heat_ledger"] = heat_ledger(seeds, cs["nominal"], trial=trial)
    _hl = R["heat_ledger"]
    print(f"   cases {_hl['cases']}; all close and within rating: "
          f"{_hl['all_cases_close_and_within_rating']}", flush=True)
    for k, v in _hl["candidates"].items():
        wc = v["worst_case"]["brake_resistor_kW"]
        print(f"   {k}: resistor worst {wc['value']:.1f} kW "
              f"({wc['governing_case']})", flush=True)

    R["verdict_stability"] = verdict_stability(R)
    _vs = R["verdict_stability"]
    print("== verdict stability (R2_DIRECTIVE item 3, R3_DIRECTIVE item 1) "
          "==", flush=True)
    for k, v in _vs["candidates"].items():
        print(f"   {k}: executed {v['executed_verdict']}, r3 on the same "
              f"criteria {v['verdict_on_same_criteria']} -> "
              f"{'unchanged' if v['unchanged'] else 'CHANGED - STOP'}",
              flush=True)
    print(f"   WHR on r3 numbers: {_vs['whr_on_current_numbers']} -> "
          f"{'unchanged' if _vs['whr_unchanged'] else 'CHANGED - STOP'}",
          flush=True)
    _sc = _vs["r3_stop_condition"]
    print(f"   R3 trip-wire: S3 nominal min "
          f"{_sc['S3_nominal_margin_pct_min']:+.2f}% vs "
          f"+{_sc['bar_pct']:.0f}% bar -> "
          f"{'CROSSED - STOP' if _sc['crossed'] else 'not crossed'}",
          flush=True)
    if not _vs["all_unchanged"]:
        print("!! A VERDICT FLIPPED, OR S3 CROSSED THE BAR, ON THE r3 "
              "NUMBERS. R2_DIRECTIVE item 3 and R3_DIRECTIVE item 1 say "
              "STOP and report; the verdict is NOT touched here and the "
              "artifacts carry the flag for the lead.", flush=True)

    R["sanity"] = sanity_checks(R)
    R["retard_overcommitment"] = retard_overcommitment(R)
    R["s3_ttr_path_status"] = s3_ttr_path_status(R)
    R["s4_cell_substitution_direction"] = s4_cell_substitution_direction(R)
    R["determinism"] = _load_determinism()
    R["escalations"] = escalations(R)
    R["interface_ws8"] = _clean_nan(interface_block(R))
    R["headline"] = headline(R)

    write_csvs(R)
    if pool is not None:
        pool.close()
        pool.join()
    elapsed = round(time.time() - t_start, 1)
    path = os.path.join(HERE, "results_ws8.json")
    # BYTE-STABLE REGENERATION (CLAUDE.md rule 1). Wall-clock timings are
    # the one thing in this structure that cannot be reproduced, so they
    # are stripped from the committed artifact rather than left to make
    # every re-run differ. They are still printed to run_output.txt,
    # where they inform without being part of the record.
    R = _strip_runtimes(_clean_nan(R))
    with open(path, "w") as f:
        json.dump(R, f, indent=1, sort_keys=False, default=_jsonable,
                  allow_nan=False)
        f.write("\n")
    print(f"== wrote {path} "
          f"({os.path.getsize(path)/1e6:.2f} MB, {elapsed:.0f} s) ==",
          flush=True)


CHECKPOINT = os.path.join(DATA, "_checkpoint.json")


DETERMINISM_FILE = os.path.join(DATA, "determinism_check.json")


def _load_determinism():
    """The rule-1 regeneration evidence, recorded as an artifact.

    The check itself cannot run inside the process it is checking - it
    compares two independent runs - so it is performed outside and its
    result committed alongside the run it certifies."""
    if not os.path.exists(DETERMINISM_FILE):
        return dict(status="NOT RUN",
                    note="data/determinism_check.json absent")
    d = json.load(open(DETERMINISM_FILE))
    d["status"] = ("PASS" if (d["half_1_simulation"]["matches_committed_run"]
                              and d["half_2_derived_blocks"]
                              ["results_json_byte_identical"]
                              and d["half_2_derived_blocks"]
                              ["all_csv_exports_byte_identical"])
                   else "FAIL")
    return d


def _rebuild_from_checkpoint(args):
    """Re-run only the derived blocks against a saved trial."""
    R = json.load(open(CHECKPOINT), object_pairs_hook=OrderedDict)
    print(f"== rebuilding derived blocks from {CHECKPOINT} ==", flush=True)
    seeds = R["_meta"]["seeds"]
    # The Task 0 artifact is hashed into the record, and it may have been
    # regenerated since the simulation ran. Re-read it so the committed
    # hash is the hash of the committed file.
    R["task0_prior_art"] = load_prior_art()
    print(f"   task 0: {R['task0_prior_art']['status']} "
          f"({R['task0_prior_art']['bytes']:,} bytes)", flush=True)
    R["task5_s3_specific"] = s3_specific_risks()
    R["two_speed_bracket"] = two_speed_bracket(R["task3_trial"]["nominal"])
    # margins are a DERIVED block: recompute them from the saved trial so
    # a rebuild cannot ship a margin block older than the code that
    # renders it.
    R["task3_margins"] = OrderedDict(
        (cn, margins_vs_s0(t, seeds)) for cn, t in R["task3_trial"].items())
    if "one_factor" not in R:
        R["one_factor"] = one_factor_rows(R["task3_trial"]["nominal"],
                                          corners()["nominal"], seeds)
    R["advance_kill"] = advance_kill(R["task3_margins"])
    R["correction_directions"] = correction_directions(R)
    R["corner_derate_scope"] = corner_derate_scope()
    for k, v in R["advance_kill"]["candidates"].items():
        wc = v["worst_corner_margin_pct_min"]
        wtxt = (f"{wc:+.2f}% @ {v['worst_corner']}" if wc is not None
                else "no corners run")
        print(f"   {k}: {v['verdict']}  (nominal min "
              f"{v['nominal_margin_pct_min']:+.2f}%, worst corner {wtxt})",
              flush=True)
    R["heat_ledger"] = heat_ledger(seeds, corners()["nominal"],
                                   trial=R["task3_trial"])
    R["verdict_stability"] = verdict_stability(R)
    R["sanity"] = sanity_checks(R)
    R["retard_overcommitment"] = retard_overcommitment(R)
    R["s3_ttr_path_status"] = s3_ttr_path_status(R)
    R["s4_cell_substitution_direction"] = s4_cell_substitution_direction(R)
    R["determinism"] = _load_determinism()
    R["escalations"] = escalations(R)
    R["interface_ws8"] = _clean_nan(interface_block(R))
    R["headline"] = headline(R)
    write_csvs(R)
    path = os.path.join(HERE, "results_ws8.json")
    with open(path, "w") as f:
        json.dump(_strip_runtimes(_clean_nan(R)), f, indent=1,
                  sort_keys=False, default=_jsonable, allow_nan=False)
        f.write("\n")
    print(f"== wrote {path} "
          f"({os.path.getsize(path)/1e6:.2f} MB) ==", flush=True)


def _save_checkpoint(R):
    with open(CHECKPOINT, "w") as f:
        json.dump(_clean_nan(R), f, default=_jsonable, allow_nan=False)
    print(f"   [checkpoint written: {os.path.getsize(CHECKPOINT)/1e6:.1f} MB]",
          flush=True)


def _strip_runtimes(o):
    """Remove wall-clock fields so the artifact regenerates byte-identically."""
    drop = {"runtime_s"}
    if isinstance(o, dict):
        return {k: _strip_runtimes(v) for k, v in o.items() if k not in drop}
    if isinstance(o, list):
        return [_strip_runtimes(v) for v in o]
    return o


def _clean_nan(o):
    """NaN and Inf are not JSON. They occur here legitimately - a field
    that does not apply to a candidate (S1 has no top gear, S3 has no
    genset) - and the right JSON spelling of "does not apply" is null.
    Converting them also makes the interface block round-trip exactly,
    which matters because verify_ws8.py asserts the report's copy equals
    this one and NaN never equals itself."""
    if isinstance(o, dict):
        return {k: _clean_nan(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean_nan(v) for v in o]
    if isinstance(o, float):
        return None if (o != o or o in (float("inf"), float("-inf"))) else o
    if isinstance(o, (np.floating,)):
        f = float(o)
        return None if (f != f or f in (float("inf"), float("-inf"))) else f
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return _clean_nan(o.tolist())
    return o


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serialisable: {type(o)}")




# =====================================================================
#  Task 0 - prior-art claim map
# =====================================================================
PRIOR_ART_FILE = "PRIOR_ART_WS8.md"


def load_prior_art():
    """Task 0 deliverable, held as a separate markdown artifact.

    The assignment permits DEFERRED with an explicit stub if the
    environment restricts web access. It does not, so the scan was run
    and the claim map is a real artifact; this function records its
    presence, size and hash so results_ws8.json pins the version the run
    was made against."""
    path = os.path.join(HERE, PRIOR_ART_FILE)
    if not os.path.exists(path):
        return dict(
            status="DEFERRED",
            stub=("Task 0 not executed in this run: " + PRIOR_ART_FILE
                  + " is absent. Physics does not wait on it (assignment, "
                    "Task 0), so Tasks 1-5 proceed and every conclusion "
                    "below stands on the physics alone. Nothing in this "
                    "report depends on a prior-art finding."),
            file=PRIOR_ART_FILE, sha256=None, bytes=0)
    raw = open(path, "rb").read()
    return dict(
        status="DELIVERED-BOUNDED", file=PRIOR_ART_FILE,
        sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
        evidence_quality=(
            "SEARCH-SUMMARY LEVEL ONLY. This environment's egress policy "
            "denies direct HTTPS CONNECT to external hosts - patent "
            "databases, SAE, NREL, NACFE and OEM sites all return 403 at "
            "the gateway (verified against the proxy's own status "
            "endpoint). Server-side web SEARCH does work and returned "
            "substantive, sourced results, so the scan was RUN rather than "
            "deferred; but no patent claim text and no primary document "
            "was read verbatim. Every finding in the claim map is "
            "therefore a lead, flagged provisional per the E13 precedent, "
            "and is NOT a freedom-to-operate opinion. Any decision that "
            "turns on claim scope needs a re-run with database access or "
            "outside counsel."),
        why_not_deferred=(
            "The assignment permits DEFERRED if the environment restricts "
            "web access. It restricts it partially, not wholly. Deferring "
            "would have thrown away a real and convergent result - so the "
            "scan is reported with its evidence limit stated instead."),
        note=("The S3 verdict in this report rests on the physics in "
              "Task 5, not on the scan. The scan corroborates it "
              "independently (section 8), which is worth something, but "
              "no verdict in section 9 depends on it."))


# =====================================================================
#  Task 1 - cycle record
# =====================================================================
def build_cycle_record(seeds):
    rec = OrderedDict()
    cyc = OrderedDict()
    for name, builder in (("LH-520", CY.build_linehaul),
                          ("REG-165", CY.build_regional)):
        rows = []
        for sd in seeds:
            c = builder(sd)
            st = CY.grade_statistics(c)
            st["seed"] = int(sd)
            st["v_wind_ms"] = c["v_wind"]
            st["n_stops"] = len(c["stops"])
            st["v_tgt_max_kmh"] = float(np.max(c["v_tgt_grid"])) * 3.6
            st["v_tgt_mean_corridor_kmh"] = float(
                np.mean(c["v_tgt_grid"][c["v_tgt_grid"] > 20.0 / 3.6])) * 3.6
            rows.append(st)
        keys = [k for k in rows[0] if isinstance(rows[0][k], float)]
        cyc[name] = dict(
            per_seed=rows,
            ensemble={k: ensemble([r[k] for r in rows]) for k in keys},
            spec=dict(dt_s=CYP.dt, sample_rate_Hz=1.0 / CYP.dt,
                      distance_grid_m=CY.DS_GRID))
    rec["cycles"] = cyc
    rec["assignment_checks"] = dict(
        sampled_at_10Hz=bool(abs(CYP.dt - 0.1) < 1e-12),
        n_seeds=len(seeds),
        linehaul_at_least_500km=bool(
            cyc["LH-520"]["ensemble"]["distance_km"]["min"] >= 500.0),
        linehaul_demand_band_kmh=[CYP.linehaul_v_lo_kmh,
                                  CYP.linehaul_v_hi_kmh],
        has_sustained_2_to_3pct=bool(
            cyc["LH-520"]["ensemble"]["frac_dist_grade_2_to_3pct"]["min"]
            > 0.02),
        has_6pct_mountain=bool(
            cyc["LH-520"]["ensemble"]["grade_max"]["max"] >= 0.059),
        mountain_descent_is_full=bool(
            abs(cyc["LH-520"]["ensemble"]["net_elevation_change_m"]["max"])
            < 1.0),
        net_elevation_zero_note=(
            "matched +/- feature pairs give net elevation change < 1 m over "
            "520 km, so no candidate is handed potential energy"))
    return rec


# =====================================================================
#  Task 2 - S0 calibration record
# =====================================================================
def s0_calibration_record(nominal_trial):
    s0 = nominal_trial["S0"]
    fleet_L = [f["L_per_100km"] for f in s0["fleet"]]
    lh = [r["fuel_L_per_100km"] for r in s0["per_cycle"]["LH-520"]]
    reg = [r["fuel_L_per_100km"] for r in s0["per_cycle"]["REG-165"]]
    lo, hi = CAL_BAND_L_PER_100KM
    eng = EN.ENG_13L
    isl = eng.min_bsfc_point()
    return dict(
        engine=dict(
            name=eng.name, label=eng.label,
            displacement_L=eng.disp_m3 * 1e3,
            peak_power_kW=eng.peak_power_kw(),
            peak_torque_Nm=float(max(EN.TRQ_13L)),
            eta_i0_solved=eng.eta_i0,
            island_bsfc_target_g_per_kWh=EN.BSFC_ISLAND_TARGET["ENG-13L"],
            island_bsfc_achieved_g_per_kWh=isl["bsfc"],
            island_rpm=isl["rpm"], island_torque_Nm=isl["trq_Nm"],
            island_power_kW=isl["p_kw"],
            peak_brake_thermal_efficiency=3600.0 / (isl["bsfc"]
                                                    * LHV_KJ_PER_G),
            fmep_coefficients_bar=list(EN.FMEP_HD),
            f_n_form="1 - 0.08*((rpm-1250)/1000)^2  [WS8 HD re-anchor]",
            construction="Willans line, WS4's ruled construction, "
                         "re-calibrated for the 13 L class"),
        transmission=dict(
            type="12-speed AMT, direct top gear",
            ratios=list(EN.AMT.RATIOS), axle_ratio=EN.AMT.AXLE,
            eta_direct_top=DL.eta_amt_direct,
            eta_indirect=DL.eta_amt_indirect,
            eta_axle_tandem=DL.eta_axle_tandem,
            eta_driveshaft=DL.eta_driveshaft,
            eta_cruise_chain=DL.eta_amt_direct * DL.eta_axle_tandem
                             * DL.eta_driveshaft,
            engine_rpm_at_100kmh=float(
                EN.AMT(EN.ENG_13L).rpm_at(100 / 3.6, 11))),
        reference_band_L_per_100km=list(CAL_BAND_L_PER_100KM),
        reference_band_source=(
            "assignment Task 2, quoted verbatim: 'sanity corridor: "
            "30-38 L/100 km loaded line-haul'"),
        linehaul_L_per_100km=ensemble(lh),
        regional_L_per_100km=ensemble(reg),
        fleet_L_per_100km=ensemble(fleet_L),
        in_corridor_all_seeds=bool(all(lo <= x <= hi for x in fleet_L)),
        in_corridor_linehaul_all_seeds=bool(all(lo <= x <= hi for x in lh)),
        corridor_excess_L_per_100km=max(
            0.0, max(fleet_L) - hi),
        fudge_factor_applied=False,
        calibration_note=(
            "eta_i0 is SOLVED so the map minimum lands exactly on the "
            "declared 185.0 g/kWh island; nothing else is tuned. The fleet "
            "fuel that comes out is whatever the physics gives, and it is "
            "checked - not fitted - against the corridor."),
        mean_cruise_bsfc_g_per_kWh=ensemble(
            [r["mean_bsfc_g_per_kWh"] for r in s0["per_cycle"]["LH-520"]]),
        top_gear_fraction=ensemble(
            [r["top_gear_fraction"] for r in s0["per_cycle"]["LH-520"]]),
    )


# =====================================================================
#  Task 2 - flat-corridor cross-check against the public reference
# =====================================================================
# Public reference band located by the Task 0 scan (search-summary level,
# flagged provisional per E13):
#   ICCT / TUV NORD chassis+track testing of tractor-trailers over the EU
#   regulatory Long Haul cycle - typical EU tractor-trailer 32.6 L/100 km,
#   best-in-class 29.9 L/100 km, and 33.1 L/100 km at the regulatory
#   Long Haul payload of 19.3 t.
#   https://theicct.org/publication/fuel-consumption-testing-of-tractor-
#   trailers-in-the-european-union-and-the-united-states/
#
# WS8's LH-520 corridor is NOT that cycle: it carries several thousand
# metres of climb (the figure is formatted from `task1_cycles`, never
# written by hand - r1 finding F13),
# because the assignment ordered a 6% mountain segment and sustained 2-3%
# sections. Comparing WS8's corridor fuel directly against a
# freeway-dominated regulatory cycle would be comparing two different
# roads. So the cross-check runs S0 over the SAME corridor with the grade
# zeroed - same distance, same speeds, same wind, same driver, same
# vehicle - which isolates terrain and makes the comparison to the public
# band an actual like-for-like.
ICCT_TYPICAL_L_PER_100KM = 32.6
ICCT_BEST_IN_CLASS_L_PER_100KM = 29.9
ICCT_AT_REG_PAYLOAD_L_PER_100KM = 33.1


ICCT_REGULATORY_PAYLOAD_KG = 19300.0
"""The payload of the EU regulatory Long Haul cycle the reference figures
were measured on. Stated because r1 compared a 20.8 t-payload result
against a 19.3 t-payload reference without saying so (finding F7)."""

EU_REGULATORY_GCW_KG = 40000.0
"""EU regulatory maximum combination mass, carried as the third mass case
so the reader can see how much of the agreement is mass."""


def _flat_crosscheck_rows(seeds, ctx, payload_factor=1.0):
    cand = make_candidate("S0", CD.Ctx(
        ctx.name, rho_air=ctx.rho_air, t_amb_c=ctx.t_amb_c,
        payload_factor=payload_factor, cold=ctx.cold, hot=ctx.hot,
        alt_m=ctx.alt_m, grade_heavy=ctx.grade_heavy, label=ctx.label))
    tables = PH.build_env_tables(cand.envelope, cand.lam)
    rows = []
    for sd in seeds:
        cyc = dict(CY.build_linehaul(sd))
        cyc["grade_grid"] = np.zeros_like(cyc["grade_grid"])
        rows.append(run_one(cand, cyc, sd, tables=tables))
    return cand, rows


def s0_flat_crosscheck(seeds, ctx):
    """S0 over the same corridor with the grade zeroed, against the
    public band.

    r1 finding F7 (material, rule 4): this - the report's ONLY external
    anchor - was asserted on a MEDIAN ("a match to about one percent")
    while its own 8-seed envelope, already computed and stored in the
    same results file, spanned 29.82 to 39.36 L/100 km, wider than the
    entire public band it was being compared against. And the comparison
    was not mass-matched: WS8 runs 20.8 t of payload, the reference cycle
    19.3 t, and neither figure was stated.

    r2 renders the ENVELOPE, and runs the cross-check at three
    enumerated combination masses so the reader can see how much of the
    agreement is the model and how much is the mass."""
    base, rows = _flat_crosscheck_rows(seeds, ctx, 1.0)
    pay_nom = base.payload_kg()
    f_match = ICCT_REGULATORY_PAYLOAD_KG / pay_nom
    f_eu = (pay_nom + (EU_REGULATORY_GCW_KG - VEH.m_gcw)) / pay_nom
    mass_cases = OrderedDict()
    for label, fac, rws in (
            ("as_reported_36300kg_GCW", 1.0, rows),
            ("mass_matched_to_ICCT_19p3t_payload", f_match, None),
            ("EU_regulatory_40000kg_GCW", f_eu, None)):
        if rws is None:
            cand_i, rws = _flat_crosscheck_rows(seeds, ctx, fac)
        else:
            cand_i = base
        mass_cases[label] = dict(
            payload_kg=cand_i.payload_kg(),
            gcw_kg=candidate_gcw(cand_i),
            L_per_100km=ensemble([r["fuel_L_per_100km"] for r in rws]))
    ens = mass_cases["as_reported_36300kg_GCW"]["L_per_100km"]
    band_lo = min(ICCT_BEST_IN_CLASS_L_PER_100KM, ICCT_TYPICAL_L_PER_100KM,
                  ICCT_AT_REG_PAYLOAD_L_PER_100KM)
    band_hi = max(ICCT_BEST_IN_CLASS_L_PER_100KM, ICCT_TYPICAL_L_PER_100KM,
                  ICCT_AT_REG_PAYLOAD_L_PER_100KM)
    return dict(
        cycle="LH-520 with grade zeroed (terrain isolated)",
        L_per_100km=ens,
        avg_speed_kmh=ensemble([r["avg_speed_kmh"] for r in rows]),
        statistic_of_record=("8-seed ensemble envelope (rule 4). The "
                             "median is quoted only alongside the min and "
                             "the max, never instead of them."),
        public_band_L_per_100km=dict(min=band_lo, max=band_hi),
        envelope_vs_band=dict(
            median_offset_pct_vs_typical=(
                (ens["median"] - ICCT_TYPICAL_L_PER_100KM)
                / ICCT_TYPICAL_L_PER_100KM * 100.0),
            envelope_width_L_per_100km=ens["max"] - ens["min"],
            band_width_L_per_100km=band_hi - band_lo,
            envelope_wider_than_band=bool((ens["max"] - ens["min"])
                                          > (band_hi - band_lo)),
            envelope_contains_band=bool(ens["min"] <= band_lo
                                        and ens["max"] >= band_hi),
            what_it_supports=(
                "the MEDIAN of the grade-zeroed ensemble lands close to "
                "the public typical figure, but the 8-seed envelope is "
                "wider than the public band itself, so the honest claim "
                "is that the model is CONSISTENT WITH the band - not that "
                "it matches it to one percent. Nothing was fitted to it "
                "either way: the single calibration knob is solved "
                "against a declared BSFC island.")),
        mass_cases=mass_cases,
        mass_matching_note=(
            "the reference cycle carries "
            f"{ICCT_REGULATORY_PAYLOAD_KG/1000:.1f} t of payload; WS8's "
            f"S0 carries {pay_nom/1000:.1f} t at the assignment's fixed "
            "36,300 kg GCW. The three mass cases are enumerated rather "
            "than reconciled, because the assignment fixed the GCW and "
            "WS8 does not get to move it."),
        reference=dict(
            source=("ICCT / TUV NORD, fuel consumption testing of "
                    "tractor-trailers in the EU and US, over the EU "
                    "regulatory Long Haul cycle"),
            typical_EU_L_per_100km=ICCT_TYPICAL_L_PER_100KM,
            best_in_class_EU_L_per_100km=ICCT_BEST_IN_CLASS_L_PER_100KM,
            at_regulatory_payload_L_per_100km=ICCT_AT_REG_PAYLOAD_L_PER_100KM,
            regulatory_payload_t=19.3,
            evidence_quality=("located via server-side search only; the "
                              "primary document could not be fetched in "
                              "this environment, so the figure is "
                              "provisional per E13 precedent")),
        note=("A model that lands near the public band on flat ground and "
              "above it on a mountain corridor is behaving; one that "
              "matched the public band on a mountain corridor would be "
              "wrong."))


# =====================================================================
#  Task 4 - WHR gate
# =====================================================================
WHR_CANDIDATES = ("S1", "S2", "S3")
"""The assignment scopes WHR to "S1-S3's steady engine operating point".
S0 and S4 are not ordered and are not run, so no WHR result is reported
for them."""


def run_whr_gate(seeds, ctx, baseline_trial, pool=None):
    res = OrderedDict()
    per_system = OrderedDict()
    for sysname in ("ETC", "ORC", "ETC+ORC"):
        system = WHR.SYSTEMS[sysname]
        trial = run_corner("nominal", ctx, seeds,
                           cand_names=list(WHR_CANDIDATES), verbose=False,
                           pool=pool, whr_name=sysname)
        per_system[sysname] = dict(spec=system.spec(), trial=trial)
    for cname in WHR_CANDIDATES:
        base = {f["seed"]: f["MJ_per_payload_tkm"]
                for f in baseline_trial[cname]["fleet"]}
        by_sys = OrderedDict()
        for sysname, blob in per_system.items():
            rows = blob["trial"].get(cname)
            if rows is None:
                continue
            per_seed = []
            for f in rows["fleet"]:
                b = base.get(f["seed"])
                if b:
                    per_seed.append(dict(
                        seed=f["seed"],
                        net_margin_pct=(b - f["MJ_per_payload_tkm"])
                        / b * 100.0))
            ens = ensemble([p["net_margin_pct"] for p in per_seed])
            pay0 = baseline_trial[cname]["spec"]["payload_kg"]
            pay1 = rows["spec"]["payload_kg"]
            # The mass charge alone costs (pay0-pay1)/pay1 in the metric,
            # because the metric divides by payload. So the fuel gain has
            # to clear the gate PLUS that, and this is the number that
            # decides the verdict before any thermodynamics is discussed.
            payload_penalty_pct = (pay0 - pay1) / pay1 * 100.0
            by_sys[sysname] = dict(
                mass_charge_kg=WHR.SYSTEMS[sysname].mass_kg,
                payload_after_kg=pay1, payload_before_kg=pay0,
                payload_penalty_pct=payload_penalty_pct,
                fuel_gain_needed_to_clear_gate_pct=(
                    WHR.GATE_PCT + payload_penalty_pct),
                per_seed=per_seed, ensemble=ens,
                passes_gate=bool(ens["min"] is not None
                                 and ens["min"] >= WHR.GATE_PCT))
        best = max(by_sys, key=lambda k: (by_sys[k]["ensemble"]["median"]
                                          or -1e9)) if by_sys else None
        any_pass = any(v["passes_gate"] for v in by_sys.values())
        res[cname] = dict(
            systems=by_sys, best_system=best,
            best_net_margin_pct_median=(by_sys[best]["ensemble"]["median"]
                                        if best else float("nan")),
            best_net_margin_pct_min=(by_sys[best]["ensemble"]["min"]
                                     if best else float("nan")),
            verdict=("ADOPT" if any_pass else "DROPPED"),
            gate_pct=WHR.GATE_PCT)
    return dict(
        gate=dict(threshold_pct=WHR.GATE_PCT,
                  basis="net fleet-mission fuel per payload tonne-km, "
                        "AFTER the mass charge, ensemble-min against the "
                        "threshold (the same statistic G1 was read on)",
                  pre_committed=True,
                  scope=list(WHR_CANDIDATES)),
        systems={k: WHR.SYSTEMS[k].spec() for k in WHR.SYSTEMS},
        results=res)


# =====================================================================
#  Two-speed traction bracket (informative; not the metric of record)
# =====================================================================
TWO_SPEED_BOX_KG = 130.0
"""Mass of a heavy-duty two-speed traction reduction. [WS8-PROV]"""


def two_speed_bracket(trial_nominal):
    """What a two-speed traction reduction would return in payload.

    WHY THIS IS HERE. The Task 0 product sweep found that every heavy
    truck that actually deleted its AMT - Hyliion Hypertruck ERX, ePower,
    ReVolt, Edison, Wrightspeed, BAE - went series AND STILL fitted a
    two-, three- or five-speed gearbox on the traction side, and the
    heavy-duty e-truck transmission literature finds a three-speed gives
    the lowest energy consumption that still meets gradeability. WS8's
    electric candidates were sized on a SINGLE fixed reduction, because
    WS2's carried 7,200 rpm rotor limit caps the ratio at 12:1 and the
    12% startability specification then sets the machine size. That is a
    defensible reading of the assignment, but it is not what the industry
    does, and it costs mass.

    THE BRACKET. With a two-speed (24:1 low / 12:1 high) the startability
    torque is met at half the stretch factor, so the machine halves under
    WS2's own mass law, while the box itself is added back. Cruise happens
    in the same 12:1 high ratio on the same part of the same map, so fuel
    per kilometre is held at the single-speed value - which makes this
    bracket CONSERVATIVE, since a smaller machine at a higher per-unit
    load is slightly more efficient at cruise, not less.

    This is an INFORMATIVE BRACKET. It is not the metric of record and it
    does not change any verdict in this report.
    """
    out = OrderedDict()
    for cname in ("S1", "S2", "S4"):
        blob = trial_nominal.get(cname)
        if blob is None:
            continue
        cand = make_candidate(cname, CD.NOMINAL)
        n = cand.edrive.n
        k_1sp = cand.edrive.k
        k_2sp = CD.size_edrive_for_startability(2.0 * CD.EDRIVE_RATIO, n)
        m1 = EL.ScaledEDrive(k_1sp, CD.EDRIVE_RATIO, n_machines=n).mass_kg()
        m2 = EL.ScaledEDrive(k_2sp, CD.EDRIVE_RATIO, n_machines=n).mass_kg()
        d_mass = (m2["total_kg"] - m1["total_kg"]) + TWO_SPEED_BOX_KG
        pay0 = blob["spec"]["payload_kg"]
        pay1 = pay0 - d_mass
        # r1 finding F10: this used to be a RATIO OF MEDIANS while every
        # other margin in the report is the MEDIAN OF PER-SEED PAIRED
        # margins, so the same quantity appeared as +0.57% here and
        # +0.75% in the headline with no statement of the difference.
        # It is now computed on the paired per-seed basis, which is the
        # program's statistic, and the basis is stated in the export.
        s0_by_seed = {f["seed"]: f["MJ_per_payload_tkm"]
                      for f in trial_nominal["S0"]["fleet"]}
        per_seed = []
        for f in blob["fleet"]:
            base = s0_by_seed.get(f["seed"])
            if not base:
                continue
            m0 = f["MJ_per_payload_tkm"]
            m1v = m0 * pay0 / pay1
            per_seed.append(dict(
                seed=f["seed"],
                margin_pct_single=(base - m0) / base * 100.0,
                margin_pct_two_speed=(base - m1v) / base * 100.0))
        ens0 = ensemble([p["margin_pct_single"] for p in per_seed])
        ens1 = ensemble([p["margin_pct_two_speed"] for p in per_seed])
        met0 = blob["fleet_ensemble"]["MJ_per_payload_tkm"]["median"]
        met1 = met0 * pay0 / pay1
        out[cname] = dict(
            k_single_speed=k_1sp, k_two_speed=k_2sp,
            edrive_mass_single_kg=m1["total_kg"],
            edrive_mass_two_speed_kg=m2["total_kg"],
            two_speed_box_kg=TWO_SPEED_BOX_KG,
            net_mass_change_kg=d_mass,
            payload_single_kg=pay0, payload_two_speed_kg=pay1,
            MJ_per_payload_tkm_single=met0,
            MJ_per_payload_tkm_two_speed=met1,
            per_seed=per_seed,
            margin_basis=("median of PER-SEED PAIRED margins against S0 "
                          "on the same seed - the same statistic as the "
                          "headline table"),
            margin_vs_S0_pct_single=ens0["median"],
            margin_vs_S0_pct_two_speed=ens1["median"],
            margin_vs_S0_pct_single_ensemble=ens0,
            margin_vs_S0_pct_two_speed_ensemble=ens1,
            margin_gain_pp=ens1["median"] - ens0["median"])
    return dict(
        basis=("informative bracket, fuel per km held at the single-speed "
               "value; not the metric of record"),
        margin_basis=("median of per-seed paired margins vs S0, the same "
                      "statistic as the headline (r1 finding F10: this "
                      "was a ratio of medians and the basis was not "
                      "stated)"),
        two_speed_ratios="24:1 low / 12:1 high",
        prior_art_motivation=(
            "every heavy truck in the Task 0 product sweep that deleted "
            "its AMT still fitted a multi-speed traction gearbox"),
        candidates=out)


# =====================================================================
#  Task 5 - S3-specific risks
# =====================================================================
def ratio_needed_for_grade(grade, ratios=None):
    """The lowest fixed ratio at which axle A holds `grade` anywhere in
    its coupled band, and the engine speed that ratio implies at
    105 km/h. This is the other half of F12's closed-form answer: the
    ceiling alone does not close the design space - what closes it is
    that the ratio the GRADE demands sits far above the ratio the CRUISE
    permits."""
    ratios = np.arange(2.0, 12.001, 0.01) if ratios is None else ratios

    def _solve(rs, dv):
        for ra in rs:
            s3 = CD.S3(ratio_a=float(ra))
            if s3.grade_hold(grade, dv=dv)["status"] == "holds":
                return float(ra), float(s3._rpm_at_v(105.0 / 3.6))
        return None, None

    ra, rpm = _solve(ratios, 0.1)
    if ra is None:
        return dict(grade=grade, ratio=None,
                    note="no ratio in [2.0, 12.0] holds this grade")
    # r2 minor m1: this half of F12 is NOT closed form - it is the first
    # hit on a 0.01 ratio grid whose own hold test scans speed on a
    # 0.1 m/s grid - and r2's report nevertheless said "No swept grid is
    # doing any work in that conclusion". Rather than restate the claim,
    # the RESOLUTION SENSITIVITY is solved: the same answer on a grid ten
    # times finer in BOTH dimensions, so the reader can see how much the
    # grid is worth instead of being told it is worth nothing.
    fine_lo = max(2.0, ra - 0.01)
    ra_f, rpm_f = _solve(np.arange(fine_lo, ra + 1e-9, 0.001), 0.01)
    if ra_f is None:
        ra_f, rpm_f = ra, rpm
    ceiling = CD.S3.RPM_MAX
    return dict(grade=grade, ratio=float(ra),
                engine_rpm_at_105kmh=rpm,
                rpm_ceiling=ceiling,
                over_ceiling_by_rpm=rpm - ceiling,
                rule=("lowest ratio on a 0.01 grid in [2.0, 12.0] whose "
                      "axle A balances road load somewhere above its own "
                      "lugging floor, with the hold test scanning road "
                      "speed on a 0.1 m/s grid. This is a SWEPT result, "
                      "not a closed form - see `resolution_sensitivity`."),
                resolution_sensitivity=dict(
                    coarse=dict(ratio_step=0.01, speed_step_ms=0.1,
                                ratio=float(ra),
                                engine_rpm_at_105kmh=rpm),
                    fine=dict(ratio_step=0.001, speed_step_ms=0.01,
                              ratio=float(ra_f),
                              engine_rpm_at_105kmh=rpm_f),
                    d_ratio=float(ra_f - ra),
                    d_rpm_at_105kmh=float(rpm_f - rpm),
                    over_ceiling_by_rpm_fine=float(rpm_f - ceiling),
                    conclusion_unchanged=bool((rpm - ceiling > 0)
                                              == (rpm_f - ceiling > 0)),
                    note=(
                        "the conclusion is that this ratio puts the "
                        "engine over its rpm ceiling at 105 km/h. Ten "
                        "times the resolution in both dimensions moves "
                        f"the ratio by {abs(ra_f - ra):.3f} and the "
                        f"engine speed by {abs(rpm_f - rpm):.0f} rpm, "
                        f"against a gap of {rpm - ceiling:,.0f} rpm. The "
                        "grid decides a decimal place; it does not decide "
                        "the answer.")))


def s3_specific_risks():
    """The three S3 risks the assignment names, answered as numbers.

    These are CAPABILITY questions, not fuel questions, so they are
    computed directly from the envelope rather than read off a cycle: a
    cycle can only tell you what happened on that cycle, and the question
    is what the architecture can and cannot do."""
    out = OrderedDict()

    # --- fixed-ratio grade-hold floor, swept over the ratio ----------
    sweep = []
    for ra in (2.40, 2.60, 2.80, 3.00, 3.20, 3.40, 3.60, 3.77, 4.00, 4.50,
               5.00):
        s3 = CD.S3(ratio_a=ra)
        row = dict(ratio_A=ra,
                   coupling_floor_kmh=s3.v_couple_min * 3.6,
                   cruise=s3.cruise_overspeed_check(105.0))
        for g in (0.01, 0.02, 0.03, 0.04, 0.05, 0.06):
            row[f"grade_{int(g*100)}pct"] = s3.grade_hold(g)
        row["climb_6pct"] = s3.climb_energy_check(0.06, 16.0)
        sweep.append(row)
    feasible = [r for r in sweep
                if r["cruise"]["ok"] and r["grade_6pct"]["status"] == "holds"]
    # r1 finding F12: `max_ratio_without_overspeed = 3.60` was a property
    # of the SWEPT GRID, not of the physics - the next ratio in the
    # enumerated list, 3.77, lands at 2,100.05 rpm, five hundredths of an
    # rpm over the ceiling. The report's section 6.2 then stated it flatly
    # as if it were the physical limit. The physics bound is closed-form:
    #     rpm = v / r_dyn * ratio * 60 / (2 pi)  <=  RPM_MAX
    #  => ratio <= RPM_MAX * 2 pi * r_dyn / (60 * v)
    v_cruise = 105.0 / 3.6
    ratio_ceiling = (CD.S3.RPM_MAX * 2 * np.pi * VEH.r_dyn
                     / (60.0 * v_cruise))
    ratio_ceiling_check = CD.S3(ratio_a=ratio_ceiling)
    out["fixed_ratio_grade_hold"] = dict(
        sweep=sweep,
        constraint=("a fixed ratio must simultaneously (a) keep the engine "
                    "below its 2,100 rpm ceiling at 105 km/h and (b) put "
                    "enough torque at the contact patch to hold the grade "
                    "at a speed above its own lugging floor. Those two pull "
                    "in opposite directions and that is the whole of the S3 "
                    "design space."),
        ratio_ceiling_closed_form=dict(
            value=float(ratio_ceiling),
            rule=("PHYSICS BOUND, solved in closed form: "
                  "ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)"),
            rpm_ceiling=CD.S3.RPM_MAX, v_cruise_kmh=105.0,
            r_dyn_m=VEH.r_dyn,
            rpm_at_v_cruise=ratio_ceiling_check.cruise_overspeed_check(
                105.0)["engine_rpm_at_v_max"],
            note=("this is the ratio ceiling. The swept-set figure below "
                  "is the highest ratio the ENUMERATED SWEEP happens to "
                  "contain under it, and is an illustration, not the "
                  "limit.")),
        max_ratio_without_overspeed=max(
            [r["ratio_A"] for r in sweep if r["cruise"]["ok"]], default=None),
        max_ratio_without_overspeed_rule=(
            "max over the ENUMERATED swept ratio set; see "
            "ratio_ceiling_closed_form for the physics bound"),
        ratio_needed_to_hold_6pct=ratio_needed_for_grade(0.06),
        any_ratio_holds_6pct=bool(feasible),
        feasible_ratios_for_6pct=[r["ratio_A"] for r in feasible])

    # --- regulatory startability, tandem vs single driven axle -------
    s3 = CD.S3()
    f_start = CD.startability_force_N()
    start_rows = []
    for label, mu in (("dry", ADH.mu_dry), ("wet", ADH.mu_wet),
                      ("snow", ADH.mu_snow), ("ice", ADH.mu_ice)):
        f_tandem = s3.adhesion_force_N(mu)
        f_single = s3.adhesion_axleA(mu)
        start_rows.append(dict(
            surface=label, mu=mu,
            required_force_kN=f_start / 1e3,
            mu_required_single_axle=f_start / (
                VEH.m_axle_drive_tandem_kg / 2.0 * G),
            mu_required_tandem=f_start / (VEH.m_axle_drive_tandem_kg * G),
            single_axle_available_kN=f_single / 1e3,
            tandem_available_kN=f_tandem / 1e3,
            single_axle_can_start=bool(f_single >= f_start),
            tandem_can_start=bool(f_tandem >= f_start)))
    out["regulatory_startability_adhesion"] = dict(
        requirement=("Regulation (EU) No 1230/2012: five starts within "
                     "five minutes at >= 12% gradient, laden to the "
                     "combination's technically permissible maximum laden "
                     "mass. Located by the Task 0 scan at search-summary "
                     "level; provisional per E13 precedent."),
        required_force_N=f_start,
        rule="min over the enumerated surface case set (R14)",
        rows=start_rows,
        single_axle_surfaces_ok=[r["surface"] for r in start_rows
                                 if r["single_axle_can_start"]],
        tandem_surfaces_ok=[r["surface"] for r in start_rows
                            if r["tandem_can_start"]],
        finding=("S3 assigns the whole of launch to axle B, a SINGLE "
                 "driven axle carrying half the tandem load. The "
                 "regulatory start therefore asks that one axle for "
                 "roughly twice the friction coefficient a 6x4 tandem "
                 "needs for the same start - the difference between a "
                 "requirement comfortably met on most surfaces and one "
                 "met on dry pavement only."),
        repeat_duty_not_modelled=(
            "the five-starts-in-five-minutes clause is a THERMAL "
            "requirement on the traction machine; WS8 checks torque and "
            "adhesion only and does not model the repeat-duty temperature "
            "rise. Stated, not hidden."))

    # --- diesel-axle-only adhesion on cruise grades ------------------
    adh = []
    for label, mu in (("dry", ADH.mu_dry), ("wet", ADH.mu_wet),
                      ("snow", ADH.mu_snow), ("ice", ADH.mu_ice)):
        f_adh = s3.adhesion_axleA(mu)
        # steepest grade axle A alone can hold at 90 km/h on adhesion
        v = 90.0 / 3.6
        rows = []
        for g in np.arange(0.0, 0.0801, 0.0025):
            f_req, _, _, _ = CD.road_load_force(np.array([v]), float(g),
                                                VEH.m_gcw)
            rows.append((float(g), float(f_req[0])))
        ok = [g for g, f in rows if f <= f_adh]
        adh.append(dict(surface=label, mu=mu,
                        axleA_load_kg=VEH.m_axle_drive_tandem_kg / 2.0,
                        F_adhesion_kN=f_adh / 1e3,
                        max_grade_held_on_adhesion=max(ok) if ok else 0.0,
                        note=("one driven axle carries half the tandem "
                              "load, so S3's cruise traction sits on half "
                              "the adhesion a 6x4 has")))
    tandem = []
    for label, mu in (("dry", ADH.mu_dry), ("wet", ADH.mu_wet),
                      ("snow", ADH.mu_snow), ("ice", ADH.mu_ice)):
        f_adh = s3.adhesion_force_N(mu)
        v = 90.0 / 3.6
        ok = []
        for g in np.arange(0.0, 0.0801, 0.0025):
            f_req, _, _, _ = CD.road_load_force(np.array([v]), float(g),
                                                VEH.m_gcw)
            if float(f_req[0]) <= f_adh:
                ok.append(float(g))
        tandem.append(dict(surface=label, mu=mu,
                           F_adhesion_kN=f_adh / 1e3,
                           max_grade_held_on_adhesion=max(ok) if ok else 0.0))
    out["diesel_axle_adhesion"] = dict(
        single_axle_A=adh, tandem_reference_6x4=tandem,
        rule=("max over the enumerated surface cases of the grade at which "
              "required tractive force at 90 km/h exceeds available "
              "adhesion; R14"),
        worst_case_surface="ice",
        governing_case="ice, mu 0.10, axle A alone")

    # --- e-axle-fault limp capability --------------------------------
    s3 = CD.S3()
    f_launch_without_eaxle = s3.f_axleA_max(0.5)
    out["fault_limp"] = dict(
        e_axle_fault=dict(
            can_launch_from_rest=bool(f_launch_without_eaxle > 0.0),
            F_available_at_rest_kN=f_launch_without_eaxle / 1e3,
            coupling_floor_kmh=s3.v_couple_min * 3.6,
            verdict=("IMMOBILE FROM REST. With axle B failed the only "
                     "remaining prime mover is the diesel on a fixed ratio "
                     "behind a rev-matched clutch that is specified for "
                     "SYNCHRONISATION, not for launch slip. Below the "
                     "coupling floor the engine cannot be connected at all, "
                     "so the combination cannot be started from rest and "
                     "cannot be recovered under its own power. This is a "
                     "TOW event, not a limp-home."),
            note=("S3 is the only candidate in the trial with no launch "
                  "device on the engine side. S0 has a slipping clutch and "
                  "12 gears; S1, S2 and S4 launch electrically and can "
                  "still make bus power from the genset with the pack "
                  "down.")),
        engine_fault=dict(
            available_energy_kWh=s3.pack.usable_kwh
            * (s3.SOC_TARGET - s3.SOC_FLOOR),
            note=("with the engine down S3 runs on axle B until the buffer "
                  "is empty; at line-haul bus demand that is a few minutes, "
                  "not a limp-home range")),
        program_precedent=("R22(c): with no mechanical path BOTH Vehicle "
                           "Zero variants share the genset-or-pack-fault = "
                           "tow asymmetry. S3 inherits a STRICTER version - "
                           "an e-axle fault alone is a tow - because its "
                           "mechanical path cannot launch."))
    return out


# =====================================================================
#  advance / kill (pre-committed)
# =====================================================================
ADVANCE_NOMINAL_PCT = 3.0
ADVANCE_CORNER_PCT = 0.0
ADVANCE_STATISTIC = "ensemble_min"
"""The criteria, quoted from the assignment: "a candidate ADVANCES only if
it beats S0 by >=3% fleet-mission fuel per payload tonne-km at nominal AND
is >=0% at every sensitivity corner, margins reported as ensemble
envelopes."

WHICH STATISTIC. The assignment says envelopes, not which end of them. WS8
reads the criteria on the ENSEMBLE MIN, following the program's own
precedent: BASELINE_v3 records G1 as "nominal ensemble-min -2.58% ...
against the armed >=5% criterion". Median and max are reported alongside
for every case, so a reader who prefers a different statistic can apply
it to the same numbers without re-running anything."""


def advance_kill(margins):
    out = OrderedDict()
    cands = sorted({c for m in margins.values() for c in m})
    for cname in cands:
        nom = margins.get("nominal", {}).get(cname)
        if nom is None:
            continue
        nom_min = nom["ensemble"]["min"]
        corner_rows = []
        for corner, m in margins.items():
            if corner == "nominal" or cname not in m:
                continue
            corner_rows.append(dict(corner=corner,
                                    **{k: m[cname]["ensemble"][k]
                                       for k in ("min", "median", "max")}))
        worst = min(corner_rows, key=lambda r: r["min"]) if corner_rows \
            else None
        passes_nominal = nom_min >= ADVANCE_NOMINAL_PCT
        passes_corners = (worst is None) or (worst["min"]
                                             >= ADVANCE_CORNER_PCT)
        out[cname] = dict(
            nominal_margin_pct_min=nom_min,
            nominal_margin_pct_median=nom["ensemble"]["median"],
            nominal_margin_pct_max=nom["ensemble"]["max"],
            corners=corner_rows,
            worst_corner=worst["corner"] if worst else None,
            worst_corner_margin_pct_min=worst["min"] if worst else None,
            passes_nominal_3pct=bool(passes_nominal),
            passes_all_corners_0pct=bool(passes_corners),
            verdict=("ADVANCE" if (passes_nominal and passes_corners)
                     else "KILL"),
            binding_reason=(
                "meets both criteria" if (passes_nominal and passes_corners)
                else ("fails the nominal >=3% criterion"
                      if not passes_nominal
                      else f"fails the >=0% corner criterion at "
                           f"{worst['corner']}")))
    return dict(
        criteria=dict(nominal_pct=ADVANCE_NOMINAL_PCT,
                      every_corner_pct=ADVANCE_CORNER_PCT,
                      statistic=ADVANCE_STATISTIC,
                      metric="fleet-mission fuel energy per payload tonne-km",
                      pre_committed=True,
                      precedent="BASELINE_v3 reads G1 on the ensemble min"),
        candidates=out,
        any_advance=bool(any(v["verdict"] == "ADVANCE"
                             for v in out.values())))


# =====================================================================
#  heat ledger (CLAUDE.md rule 7 - by component and case, for WS6)
# =====================================================================
ENGINE_HEAT_TO_COOLANT_FRAC = PARAM_ENGINE_HEAT_TO_COOLANT_FRAC
"""Of the heat a heavy-duty diesel rejects (fuel power less brake power),
the share that leaves through the coolant and charge-air cooler rather
than the exhaust and surface radiation. Declared in ws8_params so the
analytic ledger cases and the simulated peaks cannot use two different
splits."""

HEAT_ROWS = CD.HEAT_ROWS
RESISTOR_RATING_ROW = "brake_resistor_kW"


def heat_ledger(seeds, ctx, trial=None):
    """Rejected heat by COMPONENT and by CASE, per candidate (rule 7).

    REBUILT IN r2. r1's blocking finding F1 was three separate defects in
    one export, and the case set was the root of two of them:

      (a) THE GOVERNING CASE WAS OUTSIDE THE ENUMERATED SET. The three
          analytic cases priced the 6% descent with the pack accepting
          its full 240 kW throughout. The pack has ~16.8 kWh of headroom
          from its 0.60 target and fills in about 4.2 minutes of a
          9.6-minute descent, after which the whole retarding duty is
          the resistor's. The export said 210.71 kW; the trial's own
          simulated runs recorded 314.6 / 503.4 / 284.1 kW for S1 / S2 /
          S3 in the same results file. Two new members close that hole:
          a PACK-SATURATED descent case, and the SIMULATED WORST RUN,
          read from the trial itself with the (candidate, corner, cycle,
          seed) that governs labelled inline.
      (b) COMPRESSION-BRAKE HEAT WAS BOOKED AS RESISTOR HEAT and the
          exhaust row explicitly zeroed, so S1, S2 and S3 exported the
          identical 210.71 kW despite three different retarder
          architectures - and S3's exported resistor heat exceeded the
          200 kW resistor whose mass it had been charged. The retard
          channel is now split at source (`Candidate.retard_split`) and
          each half is booked where it physically goes.
      (c) FOUNDATION-BRAKE HEAT HAD NO ROW AT ALL, so 83.6 kW of S0's
          descent rejection went missing and the case did not close.
          There is now a friction-brake row, an accessory row, and an
          explicit CLOSURE RESIDUAL asserted on every case; and every
          component's exported worst case is checked against the RATING
          of the hardware whose mass was charged.

    Enumerated case set (R14), per candidate:
      cruise_95kmh_flat             what the radiator sees all day
      climb_6pct                    the peak engine and machine heat case
      descent_6pct_pack_accepting   the descent with pack headroom left
      descent_6pct_pack_saturated   the same descent once the pack is
                                    full - the resistor sizing case
      simulated_worst_run           max sustained 60-s rejection over the
                                    whole trial, per component
    """
    cases = OrderedDict([
        ("cruise_95kmh_flat", dict(v=95 / 3.6, grade=0.0, saturated=False)),
        ("climb_6pct", dict(v=None, grade=0.06, saturated=False)),
        ("descent_6pct_pack_accepting",
         dict(v=None, grade=-0.06, saturated=False)),
        ("descent_6pct_pack_saturated",
         dict(v=None, grade=-0.06, saturated=True)),
    ])
    sim = simulated_heat_peaks(trial) if trial else {}
    out = OrderedDict()
    for cname in ("S0", "S1", "S2", "S3", "S4"):
        cand = make_candidate(cname, ctx)
        m = candidate_gcw(cand)
        rows = OrderedDict()
        for case, spec in cases.items():
            grade = spec["grade"]
            if spec["v"] is not None:
                v = spec["v"]
            elif grade > 0:
                lo, hi = 1.0, 33.0
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    f_t, _, _ = cand.envelope(mid)
                    f_r, _, _, _ = PH.road_load_force(
                        np.array([mid]), grade, m, rho=ctx.rho_air)
                    if f_t >= float(f_r[0]):
                        lo = mid
                    else:
                        hi = mid
                v = lo
            else:
                v = descent_speed(cand, grade, saturated=spec["saturated"])
                v = min(v, 100.0 / 3.6)
            comp = component_heat_kw(cand, v, grade, m, ctx,
                                     saturated=spec["saturated"])
            comp["road_speed_kmh"] = v * 3.6
            comp["pack_saturated"] = bool(spec["saturated"])
            if grade < 0:
                comp["speed_step_sensitivity"] = descent_step_probe(
                    cand, v, grade, m, ctx, spec["saturated"])
            rows[case] = comp
        if cname in sim:
            rows["simulated_worst_run"] = sim[cname]
        worst = {}
        for k in HEAT_ROWS:
            vals = OrderedDict(
                (c, rows[c].get(k)) for c in rows if rows[c].get(k) is not None)
            gov = max(vals, key=lambda c: vals[c])
            sim_row = rows.get("simulated_worst_run", {})
            worst[k] = dict(
                rule=("max over the enumerated case set "
                      f"{list(rows)}; the simulated member is the maximum "
                      f"{CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second mean over "
                      "every (corner, cycle, seed) run in the trial"),
                cases=vals, value=vals[gov], governing_case=gov,
                governing_run=rows[gov].get(k + "_run"),
                # r2 finding m4: what the 60-second window averages away,
                # exported beside the figure it averages (simulated
                # member only - the analytic cases ARE instantaneous).
                simulated_instantaneous_kW=sim_row.get(
                    k + "_instantaneous_kW"),
                instantaneous_note=(
                    "the exported `value` is a SUSTAINED "
                    f"{CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second mean, which "
                    "is what sizes a cooling package; "
                    "`simulated_instantaneous_kW` is the largest single "
                    "10 Hz sample of the same component anywhere in the "
                    "trial. A large gap is a snub, not a cooling load."))
        tot = OrderedDict()
        for c in rows:
            if c != "simulated_worst_run":
                # the analytic cases are single operating points, so the
                # total IS the sum of the rows
                rows[c]["total_rejected_kW"] = sum(rows[c].get(k) or 0.0
                                                   for k in HEAT_ROWS)
            tot[c] = rows[c]["total_rejected_kW"]
        gov_t = max(tot, key=lambda c: tot[c])
        worst["total_rejected_kW"] = dict(
            rule=("max over the enumerated case set; for the simulated "
                  "member the total is the peak of the per-sample SUM, "
                  "not the sum of the component peaks, because those do "
                  "not occur at the same moment"),
            cases=tot, value=tot[gov_t], governing_case=gov_t,
            governing_run=rows[gov_t].get("total_rejected_kW_run"))
        out[cname] = dict(cases=rows, worst_case=worst,
                          ratings_check=heat_rating_check(cand, worst),
                          closure=heat_closure_check(rows))
    excl = exclusivity_check(trial) if trial else dict(
        rule="no trial supplied", candidates={}, all_hold=True, note="")
    all_close = all(
        r["closure"]["all_close"] and r["ratings_check"]["all_within_rating"]
        for r in out.values()) and excl["all_hold"]
    advisory = {c: r["ratings_check"]["advisory_exceedances"]
                for c, r in out.items()
                if r["ratings_check"]["advisory_exceedances"]}
    return dict(
        convention=("component heat rejection [kW], bus-side electrical "
                    "quantities per R12; engine heat split "
                    f"{ENGINE_HEAT_TO_COOLANT_FRAC:.2f} coolant+CAC / "
                    f"{1-ENGINE_HEAT_TO_COOLANT_FRAC:.2f} exhaust+radiation; "
                    "compression-brake heat is booked to the EXHAUST and "
                    "resistor heat to the RESISTOR, because they go to "
                    "different places in a packaging study; the simulated "
                    "member is a sustained "
                    f"{CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second mean, not an "
                    "instantaneous spike, and it is a MEASURED PEAK rather "
                    "than a balanced operating point. EVERY member now "
                    "carries a closure residual and every member is "
                    "asserted (r3, R3_DIRECTIVE item 1): the four "
                    "analytic cases are scaled on the case's own wheel "
                    "power, and the simulated member carries the WORST "
                    f"{CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second residual of "
                    "any run of that candidate in the trial, scaled on "
                    "the accounted energy input at that window. In r2 the "
                    "simulated member was exempt, and that exemption is "
                    "what finding B1 came through. The `brake_resistor_kW` "
                    "row is what the resistor TOOK, capped at the rating "
                    "whose mass was charged; retarding power the run "
                    "commanded that no sink could absorb is a CAPABILITY "
                    "shortfall and is exported separately as "
                    "`retard_overcommitment`, never as a cooling load"),
        cases=list(cases) + ["simulated_worst_run"],
        components=list(HEAT_ROWS),
        sustained_window_s=CD.HEAT_SUSTAINED_WINDOW_S,
        for_workstream="WS6 heat ledger (CLAUDE.md rule 7)",
        ledger_version=LEDGER_VERSION,
        supersedes_ledger_version="r2",
        consumer_rule=("R3_DIRECTIVE item 7: WS6 consumes ONLY the r3 "
                       "ledger. The r2 ledger is superseded, not amended: "
                       "its `simulated_worst_run` member was exempt from "
                       "the closure assertion and its largest row - S3's "
                       "396.87 kW exhaust - was a state one crankshaft "
                       "cannot be in (finding B1). A consumer holding a "
                       "ledger whose `ledger_version` is not 'r3' is "
                       "holding numbers this workstream has withdrawn."),
        overrun_exclusivity=excl,
        all_cases_close_and_within_rating=bool(all_close),
        what_all_cases_close_and_within_rating_tests=(
            "TRUE requires all three of: (a) every enumerated case "
            "closes, INCLUDING the simulated member, which carries the "
            "worst 60-second residual of any run of that candidate in "
            "the trial - in r2 the simulated member was exempt and that "
            "exemption is what finding B1 came through; (b) every "
            "component stays inside the rating of the hardware whose "
            "mass was charged, which is one HARD row - the brake "
            "resistor - the advisory rows being findings rather than "
            "gates; (c) no run carries a sample with both "
            "compression-brake power and positive engine shaft power."),
        advisory_exceedances=advisory,
        advisory_note=(
            "an ADVISORY exceedance is a declared policy allowance "
            "exceeded, not a component rating: it is a finding about the "
            "architecture that WS6 needs, not an error in this ledger. "
            "S0's foundation brakes are the case that matters - a "
            "compression-brake-only tractor snubs repeatedly on a long "
            "descent, and the sustained figure is the physical evidence "
            "behind ESC-WS8-6."),
        candidates=out)


DESCENT_CASE_BACKOFF_MS = 1e-4
"""How far BELOW the solved descent cap the analytic case is evaluated
[m/s]. S0's retarding capability is a SAWTOOTH in road speed - the AMT
picks the highest gear that keeps the engine under 2,200 rpm, so the
brake steps down at every upshift - and the bisection converges exactly
onto one of those steps. r1's descent case landed on the discontinuity
and exported the LOWER side of it (234.0 kW where 303.8 kW is what
actually holds the speed). Backing off by a tenth of a millimetre per
second puts the case unambiguously on the side the truck can hold, and
`descent_step_probe` reports both sides of the step regardless."""


def descent_speed(cand, grade, saturated=False):
    """Speed the candidate can hold on `grade`, with the pack either
    accepting regen or saturated. Same construction as `Candidate.v_cap`
    - the declared friction allowance plus its own retarding channels -
    but with the regen channel removed when the pack is full, which is
    the state the sizing case is actually in."""
    if not saturated:
        return max(2.0, cand.v_cap(grade) - DESCENT_CASE_BACKOFF_MS)

    def excess(v):
        f_res, _, _, _ = PH.road_load_force(
            np.array([v]), grade, VEH.m_gcw, None, None, cand.ctx.rho_air)
        need = -float(f_res[0])
        if need <= 0.0:
            return 1.0
        f_rs, f_eb = cand.retard_split(v, pack_saturated=True)
        allow = CD.FRICTION_BRAKE_CONT_ALLOWANCE_KW * 1e3 / max(v, 0.5)
        return (f_rs + f_eb + allow) - need

    return max(2.0, CD._bisect_speed(excess, 2.0, 35.0)
               - DESCENT_CASE_BACKOFF_MS)


def descent_step_probe(cand, v, grade, m, ctx, saturated):
    """r1 finding F1(c), second artefact: S0's descent case lands exactly
    on the AMT's gear-jump discontinuity, so the exported figure was the
    LOWER side of a step. Both sides are reported here, and the exported
    worst case is a max over a set that also contains a simulated run, so
    the step can no longer decide the answer on its own."""
    out = {}
    for label, dv in (("minus_0p5_ms", -0.5), ("plus_0p5_ms", +0.5)):
        vv = max(1.0, v + dv)
        c = component_heat_kw(cand, vv, grade, m, ctx, saturated=saturated)
        out[label] = dict(road_speed_kmh=vv * 3.6,
                          total_rejected_kW=sum(c.get(k) or 0.0
                                                for k in HEAT_ROWS))
    base = sum(component_heat_kw(cand, v, grade, m, ctx,
                                 saturated=saturated).get(k) or 0.0
               for k in HEAT_ROWS)
    span = max(r["total_rejected_kW"] for r in out.values()) - base
    out["at_case_kW"] = base
    out["step_above_case_kW"] = span
    out["on_a_step"] = bool(abs(span) > 0.05 * max(base, 1e-9))
    return out


def heat_rating_check(cand, worst):
    """Assert every exported component heat against the RATING of the
    hardware whose mass was charged against this candidate's payload
    (r1 finding F1, resolution iv). S3 exported 210.71 kW of resistor
    heat against a 200 kW resistor it had been charged 71.8 kg for.

    Two kinds of row, and they are not the same kind of statement:

      HARD - a hardware rating whose MASS WAS CHARGED to this candidate.
        Exceeding it is an internal inconsistency in WS8's own model (the
        truck is being credited with dissipating heat in a component it
        did not buy), and it gates the ledger.
      ADVISORY - a declared policy allowance rather than a component
        rating. Exceeding it is a FINDING about the architecture, not an
        error in the ledger, and it is reported rather than gating."""
    hard, advisory = [], []
    rating = getattr(cand, "resistor_kw", None)
    if rating:
        v = worst[RESISTOR_RATING_ROW]["value"]
        hard.append(dict(component="brake_resistor", kind="hard",
                         rated_kW=float(rating), worst_case_kW=v,
                         governing_case=worst[RESISTOR_RATING_ROW]
                         ["governing_case"],
                         within_rating=bool(v <= rating * 1.001),
                         note=("the resistor's mass was charged at this "
                               "rating; a worst case above it is a sizing "
                               "error, not a cooling load")))
    fr = worst["friction_brake_kW"]
    advisory.append(dict(
        component="foundation_brakes", kind="advisory",
        rated_kW=CD.FRICTION_BRAKE_CONT_ALLOWANCE_KW,
        worst_case_kW=fr["value"], governing_case=fr["governing_case"],
        governing_run=fr.get("governing_run"),
        within_rating=bool(fr["value"]
                           <= CD.FRICTION_BRAKE_CONT_ALLOWANCE_KW * 1.001),
        note=("`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous "
              "GRADE-HOLDING allowance the descent governor is built on, "
              "not a brake rating, and the integrator does not cap "
              "transient braking with it. A sustained figure above it on "
              "a simulated run therefore means repeated snub braking, "
              "which is a real thermal duty on the foundation brakes and "
              "is exactly what a candidate with a weak retarder does. It "
              "is reported, not gated - and for S0 it is the physical "
              "evidence behind ESC-WS8-6.")))
    line = getattr(cand, "line", None)
    if line is not None:
        advisory.append(dict(component="genset_electrical", kind="advisory",
                             rated_kW=float(line.p_elec_max_kw),
                             worst_case_kW=worst["generator_rectifier_kW"]
                             ["value"],
                             governing_case=worst["generator_rectifier_kW"]
                             ["governing_case"],
                             within_rating=True,
                             note="loss row, not an output; the rating is "
                                  "shown for context only"))
    rows = hard + advisory
    return dict(rows=rows,
                all_within_rating=bool(all(r["within_rating"]
                                           for r in hard)),
                advisory_exceedances=[
                    dict(component=r["component"], rated_kW=r["rated_kW"],
                         worst_case_kW=r["worst_case_kW"],
                         governing_case=r["governing_case"])
                    for r in advisory if not r["within_rating"]])


def heat_closure_check(rows):
    """EVERY case must close - including the simulated one (R3_DIRECTIVE
    item 1).

    On a descent the retarding duty at the wheel equals what is stored
    plus what is rejected; when driving, fuel power in equals wheel power
    out plus everything rejected. r1's S0 descent case left 83.6 kW with
    no row at all.

    r2 closed only the four ANALYTIC cases: `simulated_worst_run` carried
    no residual and was skipped by the loop below, and that exemption is
    what let B1 through - at the window the export named, nine rows
    summed to 630.5 kW against 1,060.2 kW of accounted input. In r3 the
    simulated member carries the WORST per-run residual any run of that
    candidate produced (`ws8_candidates.run_closure`), so the assertion
    is per run rather than per exported case, and it is scaled on the
    accounted input at that window rather than on a single operating
    point's wheel power."""
    out = OrderedDict()
    for case, r in rows.items():
        if "_closure_residual_kW" not in r:
            continue
        res = r["_closure_residual_kW"]
        scale = max(abs(r.get("_closure_scale_kW",
                              r.get("case_wheel_power_kW", 0.0))), 1.0)
        out[case] = dict(residual_kW=res, relative=res / scale,
                         closes=bool(abs(res) / scale < CD.CLOSURE_TOL),
                         basis=r.get("_closure_basis", "analytic operating "
                                     "point; scale = case wheel power"),
                         governing_run=r.get("_closure_run"))
    return dict(cases=out, tolerance=CD.CLOSURE_TOL,
                all_close=bool(all(c["closes"] for c in out.values()))
                if out else True)


def exclusivity_check(trial):
    """THE ASSERTION R3_DIRECTIVE item 1 ORDERS, aggregated over the whole
    trial: no sample of any run may carry both compression-brake power
    and positive engine shaft power.

    Every run of every candidate at every corner is examined - S1 and S4
    included, where the statement is vacuous because neither has a
    mechanical path from engine to road, because a check that runs only
    where the error was already found is not a check.

    `fuel_fraction_while_braking` is REPORTED, not gated, and it is not
    the same statement: a series genset may legitimately charge a pack
    while the vehicle brakes, because its crankshaft is not geared to the
    road. It is the pairing of that fuel with compression-brake power
    through ONE crankshaft that is impossible, and that is what
    `samples_brake_and_shaft` counts."""
    out = OrderedDict()
    for cname in ("S0", "S1", "S2", "S3", "S4"):
        worst = None
        n_bad = 0
        n_runs = 0
        f_brake_max = 0.0
        f_brake_run = None
        ttr_braking = 0.0
        for corner, blob in trial.items():
            if cname not in blob:
                continue
            for cy, rows in blob[cname]["per_cycle"].items():
                for row in rows:
                    ex = row.get("exclusivity")
                    if not ex:
                        continue
                    n_runs += 1
                    label = f"{corner}/{cy}/seed{row['seed']}"
                    n_bad += ex["samples_brake_and_shaft"]
                    if ex["samples_brake_and_shaft"] and (
                            worst is None
                            or ex["samples_brake_and_shaft"] > worst[1]):
                        worst = (label, ex["samples_brake_and_shaft"])
                    if ex["fuel_fraction_while_braking"] > f_brake_max:
                        f_brake_max = ex["fuel_fraction_while_braking"]
                        f_brake_run = label
                    ttr_braking += ex.get("ttr_charge_while_braking_kWh",
                                          0.0)
        out[cname] = dict(
            runs_examined=n_runs,
            # a candidate with NO runs examined FAILS. r2's
            # `heat_closure_check` passed by skipping what it could not
            # see (minor m5a); an aggregator that skipped rows without an
            # `exclusivity` key would do the same thing one level up.
            examined_every_run=bool(n_runs > 0),
            samples_brake_and_shaft=int(n_bad),
            worst_run=worst[0] if worst else None,
            fuel_fraction_while_braking_max=f_brake_max,
            fuel_fraction_while_braking_max_run=f_brake_run,
            ttr_charge_while_braking_kWh_total=ttr_braking,
            holds=bool(n_bad == 0 and n_runs > 0))
    return dict(
        rule=("per run, over every (corner, cycle, seed) in the trial: no "
              "10 Hz sample may carry both compression-brake power > 1 kW "
              "and positive engine shaft power > 1 kW. One crankshaft "
              "cannot be in both states."),
        candidates=out,
        all_hold=bool(all(c["holds"] for c in out.values())),
        note=("`fuel_fraction_while_braking` is reported, not gated, and "
              "a non-zero value is not by itself a defect. S1 and S4 have "
              "no mechanical path from engine to road at all, so a genset "
              "charging the pack while the vehicle brakes is simply a "
              "legitimate state for them. S2's is legitimate too, on a "
              "narrower ground: under its declared coupling law the "
              "lockup clutch is open while regen alone is doing the "
              "retarding, so the crank is free and the genset may run - "
              "and the fraction of the band that covers is exported as "
              "`inband_overrun_no_engine_brake_fraction_moving`. What is "
              "impossible, and what `samples_brake_and_shaft` counts, is "
              "an engine carrying compression-brake power and positive "
              "shaft power at the same instant."))


def simulated_heat_peaks(trial):
    """The trial's own worst sustained rejection per component, as an
    enumerated member of the R14 max (r1 finding F1a).

    Each component's maximum is taken independently over the enumerated
    (corner, cycle, seed) set and carries the run and road speed at which
    it occurred, because they are not the same run for every component.
    The TOTAL is not a sum of these - it is the peak of the per-sample
    sum, computed inside the run, because the peaks are not simultaneous.
    """
    keys = list(HEAT_ROWS) + ["total_rejected_kW"]
    # r2 finding m4: `heat_peaks` has always computed the INSTANTANEOUS
    # maximum beside the 60-second mean - its docstring says it is
    # "reported alongside so nothing is hidden" - and this function
    # enumerated only the sustained keys, so it died here and reached
    # neither the ledger nor the interface. It is enveloped now, on the
    # same enumerated case set, and exported beside the sustained figure.
    inst_keys = [k + "_instantaneous_kW" for k in HEAT_ROWS]
    out = {}
    for corner, blob in trial.items():
        for cname, r in blob.items():
            for cy, seed_rows in r["per_cycle"].items():
                for row in seed_rows:
                    hp = row.get("heat_peaks_kW")
                    if not hp:
                        continue
                    cur = out.setdefault(
                        cname, OrderedDict((k, 0.0)
                                           for k in keys + inst_keys))
                    for k in inst_keys:
                        if hp.get(k, 0.0) > cur[k]:
                            cur[k] = hp[k]
                    for k in keys:
                        if hp.get(k, 0.0) > cur[k]:
                            cur[k] = hp[k]
                            cur[k + "_run"] = (
                                f"{corner}/{cy}/seed{row['seed']}"
                                f" @ {hp.get(k + '_at_kmh', 0.0):.0f} km/h")
    # R3_DIRECTIVE item 1: the simulated member is no longer exempt from
    # the closure. It carries the WORST per-run residual any run of this
    # candidate produced, so `heat_closure_check` asserts PER RUN rather
    # than per exported case.
    worst_res = {}
    for corner, blob in trial.items():
        for cname, r in blob.items():
            for cy, seed_rows in r["per_cycle"].items():
                for row in seed_rows:
                    rc = row.get("run_closure")
                    if not rc or cname not in out:
                        continue
                    wc = rc["worst_window"]
                    prev = worst_res.get(cname)
                    if prev is None or abs(wc["relative"]) > abs(
                            prev["relative"]):
                        worst_res[cname] = dict(
                            relative=wc["relative"],
                            residual_kW=wc["residual_kW"],
                            scale_kW=abs(wc["p_in_kW"]),
                            run=(f"{corner}/{cy}/seed{row['seed']}"
                                 f" @ {wc['road_speed_kmh']:.0f} km/h"))
    for cname, cur in out.items():
        gov = max(HEAT_ROWS, key=lambda k: cur[k])
        cur["_governing_run"] = cur.get(gov + "_run")
        cur["road_speed_kmh"] = None
        cur["case_wheel_power_kW"] = None
        wr = worst_res.get(cname)
        if wr is not None:
            cur["_closure_residual_kW"] = wr["residual_kW"]
            cur["_closure_scale_kW"] = wr["scale_kW"]
            cur["_closure_run"] = wr["run"]
            cur["_closure_basis"] = (
                "WORST 60-second window of ANY run of this candidate in "
                "the trial; scale = accounted energy input at that "
                "window. Per run, not per exported case (R3_DIRECTIVE "
                "item 1).")
    return out


def component_heat_kw(cand, v, grade, m, ctx, saturated=False):
    """Heat rejected by each component at one (speed, grade) case.

    Every row of `CD.HEAT_ROWS` is filled, and the case is closed against
    the energy that entered it: `_closure_residual_kW` is what the rows
    fail to account for, and it is asserted, not hoped for."""
    f_res, _, _, _ = PH.road_load_force(np.array([v]), grade, m,
                                        rho=ctx.rho_air)
    p_wheel_kw = float(f_res[0]) * v / 1e3
    out = OrderedDict()
    out["case_wheel_power_kW"] = p_wheel_kw
    for k in HEAT_ROWS:
        out[k] = 0.0
    ed = getattr(cand, "edrive", None)
    pack = getattr(cand, "pack", None)
    line = getattr(cand, "line", None)

    if p_wheel_kw >= 0:      # driving
        if cand.name == "S0":
            amt = cand.amt
            gi, _ = amt.select_gear(v, float(f_res[0]))
            rpm = amt.engine_rpm(v, gi)
            p_shaft = p_wheel_kw / max(amt.eta(gi), 1e-6) + ctx.aux_mech_kw
            trq = p_shaft * 1e3 / (rpm * 2 * np.pi / 60.0)
            trq = min(trq, float(cand.engine.t_max(rpm)))
            b = float(cand.engine.bsfc(rpm, trq))
            p_fuel = b * p_shaft / 3600.0 * LHV_KJ_PER_G
            q = max(p_fuel - p_shaft, 0.0)
            out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
            out["engine_exhaust_kW"] = q * (1 - ENGINE_HEAT_TO_COOLANT_FRAC)
            out["driveline_kW"] = p_shaft - ctx.aux_mech_kw - p_wheel_kw
            out["accessory_kW"] = ctx.aux_mech_kw
            out["_p_in_kW"] = p_fuel
        else:
            eta = float(ed.eta_bus_to_wheel(v, p_wheel_kw)) if ed else 0.9
            p_bus_trac = p_wheel_kw / max(eta, 1e-6)
            p_bus = p_bus_trac + ctx.aux_bus_kw
            gear, mach = CD.edrive_heat_split(p_wheel_kw, p_bus_trac,
                                              ed.eta_red)
            out["traction_machine_inverter_kW"] = float(mach)
            out["driveline_kW"] = float(gear)
            out["accessory_kW"] = ctx.aux_bus_kw
            if line is not None:
                p_e = min(p_bus, line.p_elec_max_kw)
                rpm = float(line.rpm(p_e))
                p_shaft = float(line.generator.shaft_from_elec(
                    np.array([rpm]), np.array([p_e]))[0])
                out["generator_rectifier_kW"] = max(p_shaft - p_e, 0.0)
                b = float(np.interp(p_e, line.p_grid, line.bsfc))
                p_fuel = b * p_shaft / 3600.0 * LHV_KJ_PER_G
                q = max(p_fuel - p_shaft, 0.0)
                out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
                out["engine_exhaust_kW"] = q * (1
                                                - ENGINE_HEAT_TO_COOLANT_FRAC)
                # whatever the genset cannot cover comes off the pack,
                # and the pack's own loss is charged where it happens
                p_from_pack = max(p_bus - p_e, 0.0)
                eta_d = pack.eta_dis if pack is not None else 1.0
                out["pack_kW"] = p_from_pack * (1.0 / eta_d - 1.0)
                out["_p_in_kW"] = p_fuel + p_from_pack / eta_d
            else:
                # S3: engine drives axle A mechanically, e-axle from bus
                rpm = float(np.clip(cand._rpm_at_v(v), 600.0, cand.RPM_MAX))
                f_a = min(float(f_res[0]), cand.f_axleA_max(v))
                p_a_wheel = f_a * v / 1e3
                p_a = p_a_wheel / max(cand.eta_A, 1e-6)
                trq = min(p_a * 1e3 / (rpm * 2 * np.pi / 60.0),
                          float(cand.engine.t_max(rpm)))
                if trq > 1e-6:
                    b = float(cand.engine.bsfc(rpm, trq))
                    p_fuel = b * p_a / 3600.0 * LHV_KJ_PER_G
                    q = max(p_fuel - p_a, 0.0)
                else:
                    p_fuel = 0.0
                    q = 0.0
                out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
                out["engine_exhaust_kW"] = q * (1
                                                - ENGINE_HEAT_TO_COOLANT_FRAC)
                # axle B carries only what axle A could not
                p_b_wheel = max(p_wheel_kw - p_a_wheel, 0.0)
                eta_b = float(ed.eta_bus_to_wheel(v, p_b_wheel)) \
                    if p_b_wheel > 0 else 1.0
                p_b_bus = p_b_wheel / max(eta_b, 1e-6)
                gear_b, mach_b = CD.edrive_heat_split(p_b_wheel, p_b_bus,
                                                      ed.eta_red)
                out["traction_machine_inverter_kW"] = float(mach_b)
                out["driveline_kW"] = float(gear_b) + (p_a - p_a_wheel)
                p_from_pack = p_b_bus + ctx.aux_bus_kw
                eta_d = pack.eta_dis if pack is not None else 1.0
                out["pack_kW"] = p_from_pack * (1.0 / eta_d - 1.0)
                out["_p_in_kW"] = p_fuel + p_from_pack / eta_d
    else:                    # descending: the SINK case
        need_kw = -p_wheel_kw
        f_rs, f_eb = cand.retard_split(v, pack_saturated=saturated)
        f_rg = 0.0 if saturated else cand.envelope(v)[1]
        p_rg_wheel = min(need_kw, f_rg * v / 1e3)
        rest = max(need_kw - p_rg_wheel, 0.0)
        # declared draw order (Candidate.retard_split): engine brake,
        # then resistor, then the friction allowance
        p_eb_wheel = min(rest, f_eb * v / 1e3)
        rest -= p_eb_wheel
        p_rx_wheel = min(rest, f_rs * v / 1e3)
        rest -= p_rx_wheel
        p_fric_wheel = rest
        out["engine_exhaust_kW"] = p_eb_wheel
        out["friction_brake_kW"] = p_fric_wheel
        out["accessory_kW"] = (ctx.aux_mech_kw if cand.name == "S0"
                               else ctx.aux_bus_kw)
        if cand.name == "S0":
            out["_stored_kW"] = 0.0
            out["_p_in_kW"] = need_kw + ctx.aux_mech_kw
        else:
            gear_g, mach_g = CD.edrive_heat_split(
                p_rg_wheel, p_rg_wheel * float(ed.eta_wheel_to_bus(
                    v, p_rg_wheel)) if p_rg_wheel > 0 else 0.0,
                ed.eta_red, generating=True)
            eta_x = float(ed.eta_wheel_to_bus(v, p_rx_wheel)) \
                if p_rx_wheel > 0 else 0.0
            gear_x, mach_x = CD.edrive_heat_split(
                p_rx_wheel, p_rx_wheel * eta_x, ed.eta_red, generating=True)
            p_rg_bus = p_rg_wheel * float(ed.eta_wheel_to_bus(v, p_rg_wheel)) \
                if p_rg_wheel > 0 else 0.0
            out["traction_machine_inverter_kW"] = float(mach_g + mach_x)
            out["driveline_kW"] = float(gear_g + gear_x)
            out["brake_resistor_kW"] = p_rx_wheel * eta_x
            out["pack_kW"] = (p_rg_bus * (1.0 - pack.eta_chg)
                              if pack is not None else 0.0)
            out["_stored_kW"] = (p_rg_bus * pack.eta_chg
                                 if pack is not None else 0.0)
            # the accessories are served from that captured energy
            out["_p_in_kW"] = need_kw + ctx.aux_bus_kw
    rejected = sum(out[k] for k in HEAT_ROWS)
    stored = out.pop("_stored_kW", 0.0)
    p_in = out.pop("_p_in_kW", 0.0)
    out["_closure_residual_kW"] = p_in - stored - rejected - max(p_wheel_kw,
                                                                 0.0)
    out["total_rejected_kW"] = rejected
    return out


# =====================================================================
#  first-principles sanity checks
# =====================================================================
def sanity_checks(R):
    """Independent arithmetic against the model, not a re-run of it."""
    ck = OrderedDict()

    # 1. closed-form road load at 95 km/h, flat, nominal GCW
    v = 95.0 / 3.6
    f_aero = 0.5 * VEH.rho_air * VEH.CdA * v * v
    f_roll = VEH.Crr * VEH.m_gcw * G
    f_model, fa, fr, fg = PH.road_load_force(np.array([v]), 0.0, VEH.m_gcw)
    ck["road_load_95kmh_flat"] = dict(
        hand_aero_N=f_aero, model_aero_N=float(fa[0]),
        hand_roll_N=f_roll, model_roll_N=float(fr[0]),
        hand_total_N=f_aero + f_roll, model_total_N=float(f_model[0]),
        wheel_power_kW=float(f_model[0]) * v / 1e3,
        agree=bool(abs(f_aero + f_roll - float(f_model[0])) < 1e-6),
        # r1 finding F9: this note was hand-written prose sitting INSIDE
        # the data file, quoting 2,533 N (the 100 km/h aero figure)
        # against the 2,290 N computed two lines above it - and because
        # it lived in the data, verify_ws8.py could not catch it. It is
        # now formatted from the computed values.
        note=(f"{float(fa[0]):,.0f} N of aero and {float(fr[0]):,.0f} N "
              f"of rolling at {VEH.m_gcw/1000:.1f} t and 95 km/h is the "
              "whole line-haul problem in two numbers: above ~80 km/h the "
              "air is the bigger bill, which is why every candidate here "
              "wins or loses on driveline efficiency and mass, not on "
              "regenerative braking"))

    # 2. gravity on the 6% mountain, closed form
    th = np.arctan(0.06)
    f_grade = VEH.m_gcw * G * np.sin(th)
    ck["mountain_6pct"] = dict(
        grade_force_kN=f_grade / 1e3,
        power_at_90kmh_kW=f_grade * 25.0 / 1e3,
        retard_needed_at_90kmh_kW=(f_grade - f_roll
                                   - 0.5 * VEH.rho_air * VEH.CdA * 625) * 25.0
        / 1e3,
        note=("21.4 kN of gravity on a 6% grade is 535 kW at 90 km/h. No "
              "candidate in this trial has that much continuous power, so "
              "every one of them climbs the mountain slower than it "
              "cruises - and the descent needs the same number back as "
              "RETARDING power, which is the case that sizes the sink."))

    # 3. the e-drive scaling law: per-unit efficiency invariance
    ref = EL.ScaledEDrive(1.0, 12.0, n_machines=1)
    big = EL.ScaledEDrive(3.6, 12.0, n_machines=1)
    rows = []
    for vv, pu in ((60 / 3.6, 0.3), (85 / 3.6, 0.5), (95 / 3.6, 0.7)):
        p_ref = ref.wheel_power_max_kw(vv) * pu
        p_big = big.wheel_power_max_kw(vv) * pu
        e_ref = float(ref.eta_bus_to_wheel(vv, p_ref))
        e_big = float(big.eta_bus_to_wheel(vv, p_big))
        rows.append(dict(v_kmh=vv * 3.6, per_unit_load=pu,
                         eta_k1=e_ref, eta_k3p6=e_big,
                         delta_pp=(e_big - e_ref) * 100.0))
    ck["scaling_law_per_unit_invariance"] = dict(
        rows=rows,
        max_abs_delta_pp=max(abs(r["delta_pp"]) for r in rows),
        claim=("loss(k; n, T) = k * loss_ws2(n, T/k) is per-unit "
               "invariant BY CONSTRUCTION, so this check confirms the "
               "implementation, not the physics. The physics claim is "
               "escalated separately (ESC-WS8-2)."),
        agree=bool(max(abs(r["delta_pp"]) for r in rows) < 0.05))

    # 4. generator scaling: same test on WS4's model
    g_ref, _ = EL.scaled_generator("chk-ref", 135.0)
    g_big, _ = EL.scaled_generator("chk-big", 303.1)
    grow = []
    for pu in (0.3, 0.6, 0.9):
        e1 = float(g_ref.eta(1500.0, g_ref.cont_kw_in * pu))
        e2 = float(g_big.eta(1500.0, g_big.cont_kw_in * pu))
        grow.append(dict(per_unit_load=pu, eta_135kW=e1, eta_303kW=e2,
                         delta_pp=(e2 - e1) * 100.0))
    ck["generator_scaling_invariance"] = dict(
        rows=grow, max_abs_delta_pp=max(abs(r["delta_pp"]) for r in grow),
        agree=bool(max(abs(r["delta_pp"]) for r in grow) < 0.5))

    # 5. mass closure: tare + payload == GCW at nominal
    rows = []
    for cname, blob in R["task3_trial"]["nominal"].items():
        sp = blob["spec"]
        tot = sp["combination_tare_kg"] + sp["payload_kg"]
        rows.append(dict(candidate=cname, tare_kg=sp["combination_tare_kg"],
                         payload_kg=sp["payload_kg"], sum_kg=tot,
                         gcw_kg=VEH.m_gcw, closes=bool(abs(tot - VEH.m_gcw)
                                                       < 1e-6)))
    ck["mass_closure_at_fixed_gcw"] = dict(
        rows=rows, all_close=bool(all(r["closes"] for r in rows)),
        note="the whole point of the metric: at fixed GCW, powertrain "
             "mass IS payload")

    # 6. envelope tabulation error
    worst = 0.0
    for cname in ("S0", "S1", "S2", "S3", "S4"):
        cand = make_candidate(cname, CD.NOMINAL)
        tb = PH.build_env_tables(cand.envelope, cand.lam)
        for vv in np.arange(1.0, 30.0, 0.37):
            exact = cand.envelope(float(vv))
            j = vv / tb["dv"]
            j0 = int(j)
            f = j - j0
            approx = (tb["F_trac"][j0] + f * (tb["F_trac"][j0 + 1]
                                              - tb["F_trac"][j0]))
            if exact[0] > 1.0:
                worst = max(worst, abs(approx - exact[0]) / exact[0])
    ck["envelope_tabulation_error"] = dict(
        max_relative_error=worst,
        grid_dv_ms=PH.V_TABLE_DV,
        agree=bool(worst < 0.02))

    # 7. energy closure on S0's line-haul, seed 0
    s0 = R["task3_trial"]["nominal"]["S0"]["per_cycle"]["LH-520"][0]
    e_fuel_kwh = s0["e_fuel_MJ_corrected"] / 3.6
    ck["s0_energy_closure"] = dict(
        fuel_energy_kWh=e_fuel_kwh,
        engine_shaft_kWh=s0["e_engine_shaft_kWh"],
        implied_engine_efficiency=s0["e_engine_shaft_kWh"] / e_fuel_kwh,
        mean_bsfc_g_per_kWh=s0["mean_bsfc_g_per_kWh"],
        bsfc_implied_efficiency=3600.0 / (s0["mean_bsfc_g_per_kWh"]
                                          * LHV_KJ_PER_G),
        tractive_wheel_kWh=s0["E_tractive_kWh"],
        driveline_chain=DL.eta_amt_direct * DL.eta_axle_tandem
        * DL.eta_driveshaft,
        agree=bool(abs(s0["e_engine_shaft_kWh"] / e_fuel_kwh
                       - 3600.0 / (s0["mean_bsfc_g_per_kWh"]
                                   * LHV_KJ_PER_G)) < 0.03))

    # 8. BSFC island lands on its calibration target
    ck["bsfc_island_calibration"] = dict(
        rows=[dict(engine=k,
                   target=EN.BSFC_ISLAND_TARGET[k],
                   achieved=EN.ENGINES[k].min_bsfc_point()["bsfc"],
                   rpm=EN.ENGINES[k].min_bsfc_point()["rpm"])
              for k in EN.ENGINES],
        agree=bool(all(abs(EN.ENGINES[k].min_bsfc_point()["bsfc"]
                           - EN.BSFC_ISLAND_TARGET[k]) < 0.05
                       for k in EN.ENGINES)))

    # 9. cycles return to their starting elevation
    ck["cycle_net_elevation"] = dict(
        LH520_max_abs_m=max(abs(r["net_elevation_change_m"]) for r in
                            R["task1_cycles"]["cycles"]["LH-520"]["per_seed"]),
        REG165_max_abs_m=max(abs(r["net_elevation_change_m"]) for r in
                             R["task1_cycles"]["cycles"]["REG-165"]
                             ["per_seed"]),
        agree=True)
    ck["cycle_net_elevation"]["agree"] = bool(
        ck["cycle_net_elevation"]["LH520_max_abs_m"] < 1.0
        and ck["cycle_net_elevation"]["REG165_max_abs_m"] < 1.0)

    # 10. the startability sizing actually delivers what it claims
    s1 = CD.S1()
    f_need = CD.startability_force_N()
    ck["startability_sizing"] = dict(
        required_grade=CD.STARTABILITY_GRADE,
        required_force_kN=f_need / 1e3,
        S1_available_at_2kmh_kN=s1.envelope(2 / 3.6)[0] / 1e3,
        adhesion_dry_tandem_kN=s1.adhesion_force_N() / 1e3,
        adhesion_limited=bool(f_need > s1.adhesion_force_N()),
        agree=bool(s1.envelope(2 / 3.6)[0] >= f_need * 0.98))

    ck["all_pass"] = bool(all(v.get("agree", True) for v in ck.values()
                              if isinstance(v, dict)))
    return ck


# =====================================================================
#  escalations (CLAUDE.md rule 8 - cite the ruling, never self-resolve)
# =====================================================================
def _s0_friction_worst(R):
    """S0's worst sustained foundation-brake dissipation from the rebuilt
    heat ledger [kW]. Formatted from the data, never written by hand."""
    try:
        return R["heat_ledger"]["candidates"]["S0"]["worst_case"][
            "friction_brake_kW"]["value"]
    except (KeyError, TypeError):
        return float("nan")


WS9_S4P_CITATION = dict(
    source="WS9_vehicle_one_wave2 (Vehicle One wave two), as reported",
    status=("PROVISIONAL - BASELINE_v5 R37: WS9's verdicts are NOT "
            "ratified (no findings file exists and its adjudication is "
            "the lead-designated Fable seat), and R39/ESC-2 keeps S4' at "
            "PROVISIONAL-ADVANCE with its grid-factor flip point on the "
            "record"),
    candidate="S4' (S4p) - RE-BEV re-posed on a CITED EXTERNAL energy cell",
    cell_basis=("ESC-1(c): a cited external energy-optimised Class 8 "
                "traction pack, explicitly NOT a WS3 cell"),
    pack_Wh_per_kg=160.0,
    pack_mass_kg=937.5,
    c_cont_chg=1.0,
    c_cont_dis=2.0,
    p_cont_chg_kW=150.0,
    p_cont_dis_kW=300.0,
    resistor_rating_kW=350.0,
    payload_delta_vs_ruler_kg=-520.6296906751959,
    nominal_margin_pct_min=11.953945283686181,
    control_duty_nominal_margin_pct_min=-6.807699516392367,
    verdict="ADVANCE (PROVISIONAL)",
    not_commensurable=("WS9's metric is PRIMARY ENERGY per payload "
                       "tonne-km with an electricity term (ESC-3), not "
                       "WS8's fuel-energy metric. S4' +11.95% and WS8's "
                       "S4 are NOT the same quantity and must not be "
                       "differenced."),
    vintage=("WS9's numbers were produced against WS8 r2 sources; "
             "BASELINE_v5 R39/ESC-8 orders WS9 re-run against WS8 r3 when "
             "it lands"))
"""S4' as WS9 reports it, CITED as an external figure the way
`ICCT_TYPICAL_L_PER_100KM` is cited (r2 finding M4).

DELIBERATELY A DECLARED CONSTANT, NOT A LIVE READ. Reading
`../WS9_vehicle_one_wave2/results_ws9.json` at run time - or SHA-pinning
it - would make this workstream's data file change whenever WS9 re-runs,
and R39/ESC-8 orders exactly that re-run against these very numbers. That
is a two-way dependency and it would break rule 1's byte-stable
regeneration in both directions. WS9's folder is read-only to WS8 (rule
10) and its figures are quoted here, with their provisional status
attached, the same way any external citation is."""


def s3_ttr_path_status(R):
    """Whether S3's through-the-road charging path fires at all, measured
    over the whole trial (ESC-WS8-8, raised by r3).

    S3's policy says the buffer pack is refilled by regen OR by
    through-the-road charging. With R3_DIRECTIVE item 1's gate applied,
    the second half is measured here rather than assumed."""
    tot = 0.0
    blocked = 0.0
    runs = 0
    with_ttr = 0
    for corner, blob in R["task3_trial"].items():
        r = blob.get("S3")
        if not r:
            continue
        for cy, rows in r["per_cycle"].items():
            for row in rows:
                runs += 1
                e = row.get("e_ttr_charge_bus_kWh", 0.0)
                tot += e
                blocked += row.get("e_ttr_blocked_by_load_policy_kWh", 0.0)
                if e > 1e-9:
                    with_ttr += 1
    return dict(
        runs_examined=runs, runs_with_any_ttr=with_ttr,
        e_ttr_charge_bus_kWh_total=tot,
        e_ttr_blocked_by_load_policy_kWh_total=blocked,
        path_is_inert=bool(with_ttr == 0),
        rule=("summed over every (corner, cycle, seed) run of S3 in the "
              "trial; `e_ttr_blocked_by_load_policy_kWh` is what the 0.72 "
              "BSFC threshold withheld, so the reader can see that the "
              "threshold is not what makes the path inert"))


V_REGEN_BLEND_HI_MS = CD.V_REGEN_BLEND_HI
"""Road speed above which the low-speed regen blend-out is complete
[m/s], read from the control constant rather than retyped."""


def s4_cell_substitution_direction(R):
    """r2 finding M4, R3_DIRECTIVE item 5: 'restate ESC-WS8-1 with BOTH
    halves of the cell-substitution direction'.

    ESC-WS8-1 argued - correctly - that WS3's power-optimised NMC-P-40
    penalises S4 on MASS. It did not say that the same cell hands S4 a
    charge ceiling no energy cell would give it, and that S4's descent
    regen is effectively unconstrained by its pack because of it. The
    substitution moves S4 BOTH ways, and only the favourable half was on
    the record - the half WS9's S4' was then sized on under R27/ESC-1(c).

    Every number below is MEASURED here from the same model the margins
    come from, so the restated escalation is a rendering of data rather
    than a paragraph."""
    ctx = corners()["nominal"]
    cand = make_candidate("S4", ctx)
    pack = cand.pack
    v_cruise = 95.0 / 3.6
    f_machine = min(float(cand.edrive.wheel_force_max(v_cruise)),
                    float(cand.adhesion_force_N()))
    f_regen, f_res, f_eb = cand._retard_channels(v_cruise)
    # THE SPEED ABOVE WHICH THE PACK CEILING BINDS THE MACHINE.
    # Compared on ONE basis: `_retard_channels` computes
    # `min(f_gen, chg*1e3/v) * blend`, so the ceiling binds exactly when
    # `chg*1e3/v < f_gen`, and the low-speed regen blend-out - which
    # multiplies BOTH sides - cannot decide it. The first cut of this
    # block compared a blended regen force against an unblended machine
    # force and so reported "binds nowhere", which is the inverse of the
    # truth; it is written this way so the two sides are one quantity.
    chg_kw = float(cand.pack_chg_limit_kw())
    v_cross = None
    for x in np.arange(V_REGEN_BLEND_HI_MS, 33.0, 0.01):
        f_gen_x = min(float(cand.edrive.wheel_force_max(float(x))),
                      float(cand.adhesion_force_N()))
        if chg_kw * 1e3 / float(x) < f_gen_x - 1e-6:
            v_cross = float(x)
            break
    hl = R["heat_ledger"]["candidates"]["S4"]["cases"]
    desc = hl.get("descent_6pct_pack_accepting", {})

    def med(corner, key):
        rows = (R["task3_trial"].get(corner, {}).get("S4", {})
                .get("per_cycle", {}).get("LH-520", []))
        vals = [r.get(key, 0.0) for r in rows]
        return float(np.median(vals)) if vals else float("nan")

    return dict(
        rule=("measured at the nominal corner from the same envelope the "
              "integrator was given; forces are stated AT THE CONTACT "
              "PATCH on both sides, because the pack ceiling is a "
              "BUS-SIDE kW applied as a wheel-side force cap (r2 minor "
              "m6) and comparing it to a wheel-side demand without "
              "saying so is that same slippage"),
        cell=pack.cell_name if hasattr(pack, "cell_name")
        else cand.PACK_CELL,
        pack_mass_kg=float(pack.mass_kg),
        p_cont_chg_kW=float(pack.p_cont_chg_kw),
        p_cont_dis_kW=float(pack.p_cont_dis_kw),
        c_cont_chg=float(pack.p_cont_chg_kw
                         / max(pack.nameplate_kwh, 1e-9)),
        c_cont_dis=float(pack.p_cont_dis_kw
                         / max(pack.nameplate_kwh, 1e-9)),
        cruise_speed_kmh=95.0,
        f_machine_N=f_machine,
        f_regen_N=float(f_regen),
        pack_ceiling_cost_pct=float((f_machine - f_regen)
                                    / max(f_machine, 1e-9) * 100.0),
        pack_ceiling_binds_above_kmh=(v_cross * 3.6
                                      if v_cross is not None else None),
        pack_ceiling_binds_anywhere=bool(v_cross is not None),
        pack_ceiling_rule=(
            "the ceiling binds at road speeds where "
            "`p_cont_chg_kW * 1e3 / v` falls below the machine's own "
            "wheel-force limit; both sides at the CONTACT PATCH, the "
            "regen blend-out applied to neither because it multiplies "
            "both"),
        descent_resistor_kW=desc.get("brake_resistor_kW"),
        descent_friction_kW=desc.get("friction_brake_kW"),
        descent_speed_kmh=desc.get("road_speed_kmh"),
        retard_needed_6pct_90kmh_kW=R["sanity"]["mountain_6pct"][
            "retard_needed_at_90kmh_kW"],
        LH520_regen_kWh_median={
            "nominal": med("nominal", "e_regen_bus_kWh"),
            "cold_minus10C": med("cold_minus10C", "e_regen_bus_kWh")},
        LH520_resistor_kWh_median={
            "nominal": med("nominal", "e_resistor_kWh"),
            "cold_minus10C": med("cold_minus10C", "e_resistor_kWh")},
        cited_energy_cell=WS9_S4P_CITATION,
        note=("the cold corner is WS8's own in-model measurement of what "
              "a LOWER charge ceiling does to this candidate: the same "
              "pack, the same descents, a ceiling cut by "
              "COLD_CHG_FACTOR, and the harvest transfers from the pack "
              "to the resistor. It is not the energy cell - it is the "
              "direction the energy cell points."))


def retard_overcommitment(R):
    """The braking-side capability shortfall, enveloped over the trial.

    Raised inside r3 by review, and it is the same class as B1: a real
    power flow that had no home. See
    `ws8_candidates.resistor_and_overcommitment` for why it is exported
    as a capability shortfall rather than as resistor heat, and
    ESC-WS8-10 for the envelope limitation behind it."""
    ov, ove = {}, {}
    for corner, blob in R["task3_trial"].items():
        for cname, r in blob.items():
            for cy, rows in r["per_cycle"].items():
                for x in rows:
                    key = f"{cname}/{corner}/{cy}/seed{x.get('seed')}"
                    pk = x.get("retard_overcommitted_peak_kW", 0.0) or 0.0
                    e = x.get("e_retard_overcommitted_kWh", 0.0) or 0.0
                    if pk > 0.0 or e > 0.0:
                        ov[key], ove[key] = pk, e
    gov_o = max(ov, key=lambda k: ov[k]) if ov else None
    return dict(
        rule=("max over the enumerated (candidate, corner, cycle, seed) "
              "case set of the sustained "
              f"{CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second retarding power "
              "the run COMMANDED and no sink could absorb"),
        value_kW=(ov[gov_o] if gov_o else 0.0),
        governing_case=gov_o,
        energy_kWh_at_governing_case=(ove[gov_o] if gov_o else 0.0),
        cases_kW=dict(sorted(ov.items())),
        meaning=(
            "THE BRAKING-SIDE MIRROR OF `unserved_energy_kWh`, and read "
            "it the same way: it is a CAPABILITY statement, not a heat "
            "one. The traction and retard envelope is a function of road "
            "speed alone and does not re-solve when the buffer pack "
            "fills, so on a long descent the integrator keeps commanding "
            "the regen channel at its warm charge ceiling after the pack "
            "has stopped accepting. `series_dispatch` and S3's SOC loop "
            "then send that power to the brake resistor - which is where "
            "it physically goes - and the sum can exceed the resistor "
            "rating whose mass was charged. What the resistor TOOK is "
            "booked in `brake_resistor_kW`, capped at that rating; the "
            "remainder is this field. It is NOT a cooling load and WS6 "
            "must not size on it. What it measures is that the simulated "
            "descent lets the candidate retard harder than its hardware "
            "can, so its simulated descent speed is optimistic by that "
            "much. The physically correct member for the pack-full state "
            "is the enumerated `descent_6pct_pack_saturated` analytic "
            "case, which respects the rating and holds a LOWER speed. "
            "Escalated as ESC-WS8-10, not self-resolved."),
        never_absorbed=("no margin reads this field; it is reported raw, "
                        "on the convention WS4's ESC-5 established"))



def _n_simulated_runs(R):
    """Every (candidate, cycle, seed) simulation the pipeline performs,
    counted rather than estimated - the corner trial, the WHR gate and
    the one-factor re-runs. Used by ESC-WS8-9, where an undercount would
    understate what R34 is asking for."""
    n_seeds = len(R["_meta"]["seeds"])
    n = len(R["task3_trial"]) * 5 * 2 * n_seeds
    for label, row in (R.get("one_factor", {}).get("rows") or {}).items():
        if "Re-simulated" not in (row.get("_note") or ""):
            continue
        n += len([c for c in row if c in ("S0", "S1", "S2", "S3", "S4")]) \
            * 2 * n_seeds
    for cname, r in (R.get("task4_whr", {}).get("results") or {}).items():
        n += len(r.get("systems") or {}) * 2 * n_seeds
    return n


def escalations(R):
    trial = R["task3_trial"]["nominal"]
    s4 = trial.get("S4", {}).get("spec", {})
    csd = R.get("s4_cell_substitution_direction") or {}
    cec = csd.get("cited_energy_cell", WS9_S4P_CITATION)
    esc = []

    esc.append(dict(
        id="ESC-WS8-1",
        title=("WS3's cell set is power-optimised and cannot fairly carry "
               "S4's traction pack"),
        cites=("Assignment Task 3: 'battery basis from WS3's cell data'; "
               "WS3 results.json chemistry_trade; BASELINE_v3 'Pack per WS3 "
               "(unchanged, ratified): 288s1p LTO, 11.08 kWh usable'"),
        finding=(
            "WS3 characterised exactly three cells - LTO-23, LFP-P-20 and "
            "NMC-P-40 - all selected for a BUFFER duty on a 6.6 t vehicle, "
            "and all therefore power-oriented (>=3 C continuous). Their "
            "pack-level specific energies asymptote to 62.1, 83.0 and "
            "85.6 Wh/kg. WS8 has used the best of them, NMC-P-40, for "
            "every pack. For S1, S2 and S3 that is defensible: those packs "
            "ARE buffers and the power rating is what they are bought for. "
            "For S4 it is not. A range-extended BEV's pack is an ENERGY "
            "store, and energy-optimised automotive cells sit at roughly "
            "double this pack-level density. S4's 150 kWh pack therefore "
            "masses "
            f"{s4.get('mass_rows_kg', {}).get('traction_pack', 0):.0f} kg "
            "on WS3's basis, and the payload that mass displaces is "
            "charged against S4 in the metric of record.\n"
            "THE SUBSTITUTION MOVES S4 BOTH WAYS, and r2 stated only the "
            "half that hurts it (finding M4). The same power-optimised "
            "cell that costs S4 mass also hands it "
            f"{csd.get('p_cont_chg_kW', 0):.1f} kW continuous CHARGE and "
            f"{csd.get('p_cont_dis_kW', 0):.1f} kW continuous DISCHARGE on "
            f"a 150 kWh pack - {csd.get('c_cont_chg', 0):.1f} C and "
            f"{csd.get('c_cont_dis', 0):.1f} C - and that ceiling is what "
            "makes S4's descent regen effectively unconstrained by its "
            "battery. Measured at the contact patch on both sides (the "
            "ceiling is a bus-side kW applied as a wheel-side force cap, "
            "r2 minor m6, and the comparison is stated in force so that "
            "slippage cannot hide in it): at "
            f"{csd.get('cruise_speed_kmh', 0):.0f} km/h the machine can "
            f"pull {csd.get('f_machine_N', 0):,.0f} N of retarding force "
            f"and the pack ceiling allows {csd.get('f_regen_N', 0):,.0f} N "
            f"of it - the ceiling costs "
            f"{csd.get('pack_ceiling_cost_pct', 0):.1f}% of the machine's "
            "capability, and it binds at all only above "
            f"{csd['pack_ceiling_binds_above_kmh']:.1f} km/h. On "
            "the enumerated 6% descent with the pack accepting, S4 puts "
            "the WHOLE mountain into the battery: brake resistor "
            f"{csd.get('descent_resistor_kW', 0):.1f} kW and foundation "
            f"brakes {csd.get('descent_friction_kW', 0):.1f} kW, against "
            f"{csd.get('retard_needed_6pct_90kmh_kW', 0):.0f} kW of "
            "retarding demand at 90 km/h.\n"
            "WS8's OWN COLD CORNER MEASURES THE TRANSFER an energy cell's "
            "lower ceiling would cause. At -10 C the same pack's charge "
            "acceptance is cut by `COLD_CHG_FACTOR`, and S4's LH-520 "
            "median regen falls from "
            f"{csd.get('LH520_regen_kWh_median', {}).get('nominal', 0):.1f}"
            " to "
            f"{csd.get('LH520_regen_kWh_median', {}).get('cold_minus10C', 0):.1f}"
            " kWh while its resistor energy rises from "
            f"{csd.get('LH520_resistor_kWh_median', {}).get('nominal', 0):.4f}"
            " to "
            f"{csd.get('LH520_resistor_kWh_median', {}).get('cold_minus10C', 0):.1f}"
            " kWh. An energy cell at "
            f"{cec['c_cont_chg']:.1f} C continuous charge - the rate "
            f"WS9's cited external cell carries - would give this pack "
            f"about {cec['p_cont_chg_kW']:.0f} kW, well below what the "
            "descent demands, and would bind S4 hard where WS3's cell "
            "does not bind it at all. The mass half of this escalation "
            "is FOR substituting; the power half is AGAINST, and the "
            "resistor S4 would then have to grow is part of the price."),
        why_not_self_resolved=(
            "Substituting a cell WS3 never characterised would be WS8 "
            "writing WS3's trade study, which rule 10 forbids and which "
            "would put an uncorroborated number into the headline. That "
            "applies to the power half as much as to the mass half: the "
            f"{cec['c_cont_chg']:.1f} C / {cec['c_cont_dis']:.1f} C "
            "figures above are CITED from WS9's ruled external cell, not "
            "WS8's own characterisation of an energy cell."),
        asks=("Rule on ONE of: (a) S4's result stands on WS3's cell set as "
              "reported; (b) WS3 is reopened to characterise an "
              "energy-optimised cell and S4 is re-run; (c) WS8 is "
              "authorised to carry a cited external energy cell as an "
              "explicitly non-WS3 bracket.\n"
              "R27/ESC-1 HAS ALREADY RULED (c), and the ruling is "
              f"executed: {cec['candidate']} ran in {cec['source']} on "
              f"{cec['cell_basis']} at {cec['pack_Wh_per_kg']:.0f} Wh/kg "
              f"({cec['pack_mass_kg']:.0f} kg, "
              f"{cec['payload_delta_vs_ruler_kg']:+,.0f} kg of payload "
              f"against its ruler) and returned "
              f"{cec['nominal_margin_pct_min']:+.2f}% on the design duty "
              f"and {cec['control_duty_nominal_margin_pct_min']:+.2f}% on "
              f"the control duty - {cec['verdict']}. This escalation is "
              "therefore CLOSED for Vehicle One's WS9 work and is carried "
              "here only because WS8's own numbers were computed before "
              "that ruling.\n"
              f"THREE CAVEATS ON THAT CITATION. Status: {cec['status']}. "
              f"Commensurability: {cec['not_commensurable']} "
              f"Vintage: {cec['vintage']}."),
        materiality=("high, and TWO-DIRECTIONAL - it is the difference "
                     "between S4 advancing or not on mass, and the "
                     "difference between a descent the pack absorbs and "
                     "one it does not on power. r2 recorded only the "
                     "first direction (finding M4), and WS9's S4' was "
                     "sized under R27/ESC-1(c) on that half of the "
                     "record.")))

    esc.append(dict(
        id="ESC-WS8-2",
        title=("The traction-machine stretch to k=3.6 is far beyond the "
               "range WS2 validated"),
        cites=("R10, R13, R21 (WS2-E8/E9 accepted); WS2 run_ws2.py "
               "scaled_machine() stack-length rule; REPORT_WS2 section 1 "
               "item 1 (fixed saturated-bulk Ld, Lq, psi_m, no saturation "
               "map)"),
        finding=(
            "WS8's electric paths need a machine of about 3.6x the VM250-HV "
            "active length to meet the 12% startability specification at "
            "36,300 kg on a single-speed reduction. WS8 applies WS2's OWN "
            "stack-length rule and WS2's own mass split (mass_end_kg = "
            "18.0), so the LAW is inherited rather than invented - but WS2 "
            "exercised that rule over an 8:1-12:1 ratio sweep, a scale "
            "range of about 1.5x, not 3.6x. The record also contains a "
            "direct warning: R10 and R13 both predicted the crawl current "
            "would scale x0.56 and the computed answer was x0.685, a 22% "
            "error from reasoning about this machine by proportion. WS8 "
            "charges NO rotor-dynamics, shaft-stiffness or saturation "
            "penalty for the stretch."),
        why_not_self_resolved=(
            "Re-deriving the machine at 3.6x would be doing WS2's work in "
            "WS8's folder."),
        asks=("Rule on whether the stretch may stand as the sizing basis, "
              "or whether WS2 must re-derive at semi scale before any WS8 "
              "electric result is ratified. Note the direction of the "
              "error: every candidate except S0 carries this machine, so "
              "it does not change their RANKING, only their common "
              "distance from S0."),
        materiality="medium - common-mode across S1-S4, so ranking-neutral"))

    esc.append(dict(
        id="ESC-WS8-3",
        title=("The metric of record cannot see grid electricity, which "
               "decides what S4 even is"),
        cites=("Assignment Task 3 metric of record: 'fuel energy per "
               "PAYLOAD tonne-km'; Task 3 S4: 'large pack + sustainer "
               "genset'"),
        finding=(
            "A range-extended BEV is bought to run on grid energy, with the "
            "sustainer covering what the pack cannot. The ordered metric "
            "counts FUEL energy only. WS8 has therefore run S4 "
            "CHARGE-SUSTAINING - it starts and ends the mission at the same "
            "state of charge, and any residual drift is priced back into "
            "fuel - because the alternative would let S4 import propulsion "
            "energy the metric is blind to and post a margin that is "
            "partly an accounting artefact. Under that treatment S4 is "
            "judged as a series hybrid with a small engine and a heavy "
            "pack, which is not the thing the name describes."),
        why_not_self_resolved=(
            "Choosing whether Vehicle One admits an electricity term is a "
            "program-level metric decision, not a modelling choice."),
        asks=("Rule on whether Vehicle One's metric of record acquires an "
              "electricity term (and at what primary-energy or CO2 "
              "equivalence), or whether S4 is to be judged charge-sustaining "
              "as reported."),
        materiality="high - it determines whether S4's result means what it "
                    "appears to mean"))

    esc.append(dict(
        id="ESC-WS8-4",
        title="R18's flat-rating ratio has been transferred to a 13 L class",
        cites="R18, R24 (BASELINE_v3: flat-rating carried as a freeze-hold)",
        finding=(
            "R18 rates the 4HK1-V2C at 132 kW continuous from a 153.3 kW "
            "automotive peak - a ratio of 0.861 - and R24 records that the "
            "datasheet item confirms a RATING, not a geometry. WS8 has "
            "applied the same 0.861 to the 13 L's 352 kW peak to get "
            "303 kW continuous for the S1/S2 genset, and to the 7 L "
            "sustainer. That is a transfer of a ruled number to an engine "
            "class the ruling never contemplated."),
        why_not_self_resolved="R18 is a ruling; only the lead amends it.",
        asks=("Confirm the transfer, or supply a Class 8 prime-power "
              "de-rating basis. The genset rating sets how fast S1 and S2 "
              "climb, so it moves their fuel and their trip time."),
        materiality="medium"))

    esc.append(dict(
        id="ESC-WS8-5",
        title=("WS8 has re-anchored the speed term in WS4's ruled Willans "
               "construction"),
        cites="R12 chain conventions; WS4 ws4_models.WillansEngine._f_n",
        finding=(
            "WS4's f_N is 1 - 0.06*((rpm-1600)/1400)^2, calibrated for a "
            "700-3,000 rpm medium-duty engine. A Class 8 six runs "
            "600-2,100 rpm and is built to be at its best near 1,200-1,300. "
            "Carrying WS4's centre unchanged would have placed the "
            "efficiency optimum 300-400 rpm too high and would have "
            "UNDER-penalised high-speed operation - which is precisely "
            "where S3's fixed ratio is forced to live. WS8 therefore uses "
            "1 - 0.08*((rpm-1250)/1000)^2 and re-solves eta_i0 against it "
            "so the island BSFC target is unmoved. This is a change to an "
            "inherited model, declared here rather than made quietly."),
        why_not_self_resolved=("The Willans construction is WS4's ruled "
                              "object; WS8 may not amend another "
                              "workstream's model on its own authority."),
        asks=("Ratify the HD re-anchor for Vehicle One, or direct WS8 to "
              "carry WS4's medium-duty f_N unchanged and re-run. Note the "
              "direction: the re-anchor makes S3 look WORSE, so reverting "
              "it would not rescue S3."),
        materiality="medium"))

    cal = R["task2_s0_calibration"]
    fx = cal.get("flat_corridor_crosscheck", {})
    # r1 finding F13: "~3,800 m of climb" was a hard-coded literal used
    # twice to justify why S0 misses the fuel corridor, and it is the TOP
    # of the ensemble (min 3,507 / median 3,704 / max 3,838). Formatted
    # from the data here and in the report.
    _cl = R["task1_cycles"]["cycles"]["LH-520"]["ensemble"]["total_climb_m"]
    climb_txt = (f"{_cl['median']:,.0f} m of climb over 520 km "
                 f"(8-seed ensemble {_cl['min']:,.0f} m to "
                 f"{_cl['max']:,.0f} m)")
    if not cal["in_corridor_all_seeds"]:
        esc.append(dict(
            id="ESC-WS8-7",
            title=("S0's fuel exceeds the assignment's 30-38 L/100 km "
                   "sanity corridor, and the model is not the reason"),
            cites=("Assignment Task 2: 'Calibrate fleet fuel to a public "
                   "reference band and state it (sanity corridor: "
                   "30-38 L/100 km loaded line-haul)'; Task 1: 'realistic "
                   "grade distribution including sustained 2-3% and one 6% "
                   "mountain segment with full descent'"),
            finding=(
                "S0's fleet-mission fuel is "
                f"{cal['fleet_L_per_100km']['median']:.2f} L/100 km "
                f"(ensemble {cal['fleet_L_per_100km']['min']:.2f} to "
                f"{cal['fleet_L_per_100km']['max']:.2f}), above the stated "
                "corridor. The calibration is nonetheless sound, and the "
                "cross-check says so directly: run over the SAME corridor "
                "with the grade zeroed - same distance, same speeds, same "
                "wind, same driver, same vehicle, nothing else touched - "
                "S0 burns "
                f"{fx.get('L_per_100km', {}).get('median', float('nan')):.2f}"
                " L/100 km MEDIAN, on an 8-seed envelope of "
                f"{fx.get('L_per_100km', {}).get('min', float('nan')):.2f}"
                " to "
                f"{fx.get('L_per_100km', {}).get('max', float('nan')):.2f}"
                " L/100 km, against the ICCT / TUV NORD figures of "
                f"{ICCT_BEST_IN_CLASS_L_PER_100KM}-"
                f"{ICCT_AT_REG_PAYLOAD_L_PER_100KM} L/100 km "
                f"(typical {ICCT_TYPICAL_L_PER_100KM}) for an EU "
                "tractor-trailer over the regulatory Long Haul cycle.\n"
                "WHAT THAT SUPPORTS, restated in r2 (finding F7). r1 read "
                "this off the median and called it 'a match to about one "
                "percent'. It is not: the ensemble envelope is WIDER than "
                "the public band it is being compared against, and the "
                "comparison is not mass-matched - WS8's S0 carries "
                f"{fx.get('mass_cases', {}).get('as_reported_36300kg_GCW', {}).get('payload_kg', 0)/1000:.1f} t "
                "of payload at the assignment's fixed GCW against the "
                "reference cycle's 19.3 t, and the three enumerated mass "
                "cases in section 3.4 show what that is worth. The claim "
                "the evidence supports is that the model is CONSISTENT "
                "WITH the public band on flat ground, reached with no "
                "fitting: the single calibration knob is solved against a "
                "declared BSFC island and nothing else is tuned.\n"
                "The excess is TERRAIN. Task 1 ordered a corridor carrying "
                f"a 6% mountain and sustained 2-3% sections - {climb_txt} - "
                "and a 30-38 L/100 km band "
                "describes a freeway-dominated regulatory cycle, not that "
                "road. The two orders are in tension, and WS8 has obeyed "
                "the one that governs the physics (Task 1's corridor) "
                "rather than adjusting the vehicle until Task 2's band was "
                "satisfied."),
            why_not_self_resolved=(
                "Reconciling them would mean either flattening a corridor "
                "the assignment specified or tuning a vehicle parameter "
                "until a band was met - and tuning to a band is exactly "
                "what 'no fudge factor' forbids. Either change alters "
                "every candidate's result, so it is the lead's to make."),
            asks=("Rule on which governs: (a) the corridor as specified, "
                  "with S0's fuel reported above the band and the flat "
                  "cross-check standing as the calibration evidence "
                  "(WS8's recommendation - it is the honest reading and "
                  "the comparison between candidates is unaffected, since "
                  "all five drive the same road); or (b) a flatter "
                  "reference corridor, which would move every absolute "
                  "fuel figure and none of the margins. Note that r2 has "
                  "WEAKENED the evidence this escalation rests on, per "
                  "F7: the anchor is an envelope consistent with the "
                  "band, not a one-percent match to a point in it."),
            materiality=("low for the trial, high for the record - it "
                         "changes no margin, because every candidate "
                         "drives the same corridor, but it is a stated "
                         "acceptance criterion not met and must not pass "
                         "silently")))

    esc.append(dict(
        id="ESC-WS8-6",
        title=("S0 is specified with a compression brake only, and that "
               "hands the electric candidates a descent-speed advantage"),
        cites=("R2 (the resistor sink is the only speed-independent "
               "retarder); assignment Task 3 'S0 baseline, calibrated'"),
        finding=(
            "S0's only retarder is its engine brake, which is strong at low "
            "road speed and weak at high. The electric candidates carry a "
            "brake resistor sized in the hundreds of kW and can hold the "
            "6% descent at corridor speed while S0 must slow to about "
            "62 km/h. That is a real architectural difference, and WS8 has "
            "modelled it rather than equalised it - but a line-haul tractor "
            "can be specified with a hydraulic retarder, and many are. The "
            "effect on the metric is small (it moves trip time and "
            "therefore accessory energy, not tractive work) but it is not "
            "zero, and it is a specification choice rather than a physical "
            "necessity.\n"
            "r2 SUPPLIES THE NUMBER. The rebuilt heat ledger carries a "
            "foundation-brake row for the first time, and S0's worst "
            f"sustained {CD.HEAT_SUSTAINED_WINDOW_S:.0f}-second "
            "foundation-brake dissipation over the whole trial is "
            f"{_s0_friction_worst(R):.0f} kW, against the "
            f"{CD.FRICTION_BRAKE_CONT_ALLOWANCE_KW:.0f} kW continuous "
            "grade-holding allowance the descent governor is built on. "
            "That is repeated snub braking on long descents - what a "
            "compression-brake-only tractor actually does - and it is "
            "reported in the ledger as an ADVISORY exceedance rather than "
            "a ledger error, because the allowance is a policy number and "
            "not a brake rating. It is the physical evidence for this "
            "escalation, and it is a thermal duty WS6 should see."),
        why_not_self_resolved=("Whether the ruler carries a retarder is a "
                              "baseline-specification decision."),
        asks=("Confirm S0's retarder specification, or direct a re-run with "
              "a hydraulic retarder on S0. R27/ESC-6 has already ruled "
              "that S0 gains a hydraulic retarder in WS9 with its mass "
              "charged; this escalation is therefore CLOSED for Vehicle "
              "One's WS9 work and is carried here only because WS8's own "
              "numbers were computed before that ruling."),
        materiality="low - affects trip time and accessory energy, not "
                    "tractive work"))

    # ---- raised by r3 -------------------------------------------------
    ttr = R.get("s3_ttr_path_status") or {}
    esc.append(dict(
        id="ESC-WS8-8",
        title=("Once B1's rule is applied, S3's through-the-road charging "
               "path never runs - and the reason is a modelling artefact, "
               "not a control choice"),
        cites=("R3_DIRECTIVE item 1 (gate through-the-road charging on the "
               "VEHICLE NOT BRAKING); FINDINGS_WS8_r2.md B1; assignment "
               "Task 3's S3 specification"),
        finding=(
            "S3's declared policy says its buffer pack 'can only be "
            "refilled by regen or by through-the-road charging (engine "
            "pushes axle A, e-axle harvests on axle B)'. With R3's gate "
            "in place that second mechanism is IDENTICALLY INERT: over "
            "the whole trial S3 takes "
            f"{ttr.get('e_ttr_charge_bus_kWh_total', 0.0):.3f} kWh of "
            "through-the-road charge, on "
            f"{ttr.get('runs_with_any_ttr', 0)} of "
            f"{ttr.get('runs_examined', 0)} runs.\n"
            "THE REASON IS NOT THE GATE. The charging headroom is priced "
            "as `p_chg_head_bus = f_a_head * v * eta_g`, where `eta_g` is "
            "`ScaledEDrive.eta_wheel_to_bus(v, p_regen_wheel)` - the "
            "generating efficiency evaluated AT THE REGEN OPERATING "
            "POINT. That function returns exactly 0.0 when the captured "
            "power is zero (`ws8_electric.py`: `eta = np.where(gen, ..., "
            "0.0)`), and the captured power is zero on every sample where "
            "the integrator is not braking. So the headroom was zero on "
            "every non-braking sample all along, and in r2 the ONLY "
            "samples on which through-the-road charging could fire were "
            "braking samples - which is exactly the impossible state "
            "finding B1 identified. The B1 gate did not disable a working "
            "mechanism; it revealed that the mechanism only ever ran in "
            "the state it must not run in.\n"
            "The 0.72-of-capacity BSFC policy is NOT what holds it back "
            "either, and that is measured rather than argued: the energy "
            "that threshold withheld over the whole trial is "
            f"{ttr.get('e_ttr_blocked_by_load_policy_kWh_total', 0.0):.3f}"
            " kWh."),
        why_not_self_resolved=(
            "Repricing the headroom at the TTR harvest's own operating "
            "point would make the mechanism work, and would move S3's "
            "fuel and unserved energy by an unmeasured amount. "
            "R3_DIRECTIVE's scope is declared exhaustive and orders the "
            "GATE, not a re-specification of the charging law; and item 1 "
            "carries its own STOP condition on S3's nominal ensemble-min. "
            "Changing the law under that condition is the lead's call."),
        asks=("Rule on ONE of: (a) S3's through-the-road path stands as "
              "inert and the record says so - S3 is dead on capability "
              "either way and this changes no verdict; (b) WS8 is "
              "directed to reprice the charging headroom at the harvest's "
              "own operating point and re-run S3 on all corners; (c) the "
              "finding is carried to WS9/WS10 as a design note against "
              "any future through-the-road architecture, since the same "
              "efficiency call would silently disable it there too."),
        materiality=("medium for WS8's record, high as a design note - it "
                     "changes no verdict (S3's kill is on capability), but "
                     "it means half of S3's stated energy policy was never "
                     "exercised by the model that judged it, and any "
                     "future candidate that leans on through-the-road "
                     "charging inherits the same silent zero.")))

    esc.append(dict(
        id="ESC-WS8-9",
        title=("R34 orders a 10 Hz trace file per run from 'all later "
               "work'; R3_DIRECTIVE's scope is declared exhaustive and "
               "does not include it"),
        cites=("BASELINE_v5 R34 ('Every pipeline exports a 10 Hz trace "
               "file per run (feeds the WS10 exhibit/simulator). WS5, WS9 "
               "re-runs, and all later work comply from their next "
               "artifact.'); R3_DIRECTIVE.md '## Scope (exhaustive)'; "
               "CLAUDE.md rule on bounded orders"),
        finding=(
            "R34 is a standing program-hygiene ruling and WS8 r3 is a "
            "next artifact, so it reads as binding here. R3_DIRECTIVE's "
            "scope is declared EXHAUSTIVE in seven numbered items and "
            "does not mention traces, and CLAUDE.md says an assignment or "
            "directive is a bounded order - do what is ordered, nothing "
            "else. The two cannot both be satisfied by a workstream "
            "session deciding for itself.\n"
            "The cost is not incidental. This pipeline runs "
            f"{_n_simulated_runs(R)} "
            "simulated runs (the corner trial, the WHR gate and the "
            "one-factor re-runs, counted); LH-520 is about 520 km at "
            "10 Hz, so a "
            "full-fidelity trace set for every run is of the order of "
            "gigabytes and is not a committable artifact. A bounded "
            "subset - the governing runs the heat ledger and the "
            "worst-case exports actually name - would be a few tens of "
            "megabytes and would serve the WS10 exhibit for the cases "
            "that matter.\n"
            "Nothing in this round depends on the answer: no number here "
            "changes either way."),
        why_not_self_resolved=(
            "Choosing which runs to export, and at what fidelity, is a "
            "program-hygiene decision under R34 and it binds WS5, WS9 and "
            "WS10 as much as WS8. A workstream session picking its own "
            "subset would set that convention by default."),
        asks=("Rule on ONE of: (a) R34 does not reach WS8 r3, whose scope "
              "R3_DIRECTIVE declares exhaustive, and traces come with the "
              "next WS8 artifact if there is one; (b) WS8 r3 exports "
              "traces for a NAMED bounded subset - the ledger's governing "
              "runs plus one nominal run per candidate - and the "
              "convention is written down for WS5/WS9/WS10; (c) full "
              "compliance, with the artifact-size consequence accepted "
              "and a storage convention ruled."),
        materiality=("none for this round's numbers; medium for the "
                     "program, because R34's convention is being set by "
                     "whoever complies first and no one has yet")))

    _ov = R.get("retard_overcommitment") or dict(
        value_kW=0.0, governing_case=None,
        energy_kWh_at_governing_case=0.0)
    esc.append(dict(
        id="ESC-WS8-10",
        title=("The retard envelope does not re-solve when the buffer "
               "pack fills, so every simulated descent lets a candidate "
               "brake harder than its resistor can absorb"),
        cites=("R3_DIRECTIVE item 1 (extend `heat_closure_check` to "
               "`simulated_worst_run`) - the extended closure is what "
               "found this; FINDINGS_WS8_r1.md F1(a), which added the "
               "`descent_6pct_pack_saturated` analytic case for exactly "
               "this state; CLAUDE.md rule 7"),
        finding=(
            "`Candidate.envelope` and `_retard_channels` are functions of "
            "ROAD SPEED ALONE. The regen channel is capped at the pack's "
            "charge ceiling at the corner's ambient - a constant - so the "
            "integrator goes on commanding regen at that ceiling after "
            "the pack has actually filled. On the 6% mountain descent the "
            "pack reaches its 0.95 SOC ceiling part-way down and then "
            "takes nothing, and `series_dispatch` (and S3's SOC loop) "
            "send the whole harvest to the brake resistor, which is where "
            "it physically goes. The sum exceeds the resistor rating "
            "whose mass was charged.\n"
            "r3 books what the resistor TOOK in `brake_resistor_kW`, "
            "capped at that rating, and exports the remainder as "
            f"`retard_overcommitment`: worst case "
            f"{_ov.get('value_kW', 0.0):.1f} kW sustained at "
            f"`{_ov.get('governing_case')}`, "
            f"{_ov.get('energy_kWh_at_governing_case', 0.0):.2f} kWh on "
            "that run. Booking the whole flow as resistor heat instead "
            "would have exported a 450+ kW cooling load for a 340 kW "
            "resistor and told WS6 to size a package for a duty the "
            "hardware cannot produce; that alternative was considered "
            "and rejected, and the choice is stated here rather than "
            "buried.\n"
            "WHAT IT MEANS FOR THE TRIAL: every candidate with a buffer "
            "pack holds its simulated descent at a speed its retarder "
            "cannot actually support once the pack is full, so the "
            "simulated descent speeds - and therefore trip times, and "
            "the accessory energy that rides on them - are optimistic. "
            "The enumerated `descent_6pct_pack_saturated` case is the "
            "physically correct member for that state and it is in the "
            "ledger: it holds a LOWER speed precisely because it "
            "respects the rating. The two members disagreeing IS the "
            "finding."),
        why_not_self_resolved=(
            "Making the envelope re-solve at pack-full changes the "
            "achieved speed, the trip time and the cycle every candidate "
            "drives, and therefore every margin in the trial. "
            "R3_DIRECTIVE's scope is declared exhaustive and orders the "
            "closure extended, not the integrator re-specified; and "
            "R38's trip-time gate for Vehicle One depends on exactly "
            "these speeds. That is a lead decision."),
        asks=("Rule on ONE of: (a) the record stands as it is - the "
              "overcommitment is exported, WS6 sizes on the capped "
              "resistor row and on the analytic pack-saturated case, and "
              "the optimism in the simulated descent speeds is a stated "
              "limitation; (b) WS8 is directed to make the retard "
              "envelope a function of pack state as well as road speed "
              "and re-run every corner, accepting that every margin and "
              "every trip time moves; (c) the finding is carried to WS9 "
              "and WS10 as a design note, since R38 gates ADVANCE on "
              "trip time and every buffer-pack candidate there inherits "
              "the same optimism."),
        materiality=("medium for this round - no verdict depends on it, "
                     "and the four kills are unchanged - but high for "
                     "WS9 and WS10, where R38 makes trip time a gate and "
                     "the trip times all four wave-two candidates were "
                     "judged on come from the same envelope")))

    return sorted(esc, key=lambda e: e["id"])


# =====================================================================
#  R14 interface block + headline
# =====================================================================
def _paired_margin(cand_fleet, s0_fleet, key="MJ_per_payload_tkm"):
    s0 = {f["seed"]: f[key] for f in s0_fleet}
    vals = [(s0[f["seed"]] - f[key]) / s0[f["seed"]] * 100.0
            for f in cand_fleet if f["seed"] in s0]
    return ensemble(vals)


def one_factor_rows(trial_nominal, ctx, seeds, pool=None):
    """R2_DIRECTIVE item 3 and R3_DIRECTIVE items 1 and 2.

    r3 widens this block from a two-candidate ordering exhibit to the
    MEASUREMENT every direction statement in the record is now generated
    from (r2 finding M1: 'delete every hand-written direction string').
    Two things changed:

      * the candidate set is S1..S4 rather than S1 and S2, so a
        correction that touches only one candidate PROVES it here -
        `f3_s2_engine_budget` and `f5_spin_rule` are gated in S2 and S3
        only, and S1's and S4's rows come back bit-identical rather than
        being asserted to be unaffected;
      * a `B1_reverted_brake_and_fuel` row measures R3_DIRECTIVE item 1's
        own correction, which is what that directive means by 'Report
        S3's fuel change with a one-factor row'.

    R2_DIRECTIVE item 3: 'Report the S1-vs-S2 ordering AFTER these
    corrections with one-factor rows, since they decide it.'

    r1 put S2 ahead of S1 on the nominal median (+1.70 vs +0.75). The
    adjudicator showed that about half of S2's advantage was the
    charge-sustaining CREDIT (F4), and that S2's engine was being run as
    a locked mechanical drive and a free-speed genset at the same time
    (F3). Both were corrected in r2, and both move S2 and not S1, so the
    ordering has to be shown factor by factor rather than only at the
    end.

    Each row reverts EXACTLY ONE correction and leaves the rest applied.
    F4 and F6 are exact re-pricings of the run of record and need no
    re-simulation; F3, F5 and B1 change the dispatch and are re-simulated.
    """
    pair = ["S1", "S2", "S3", "S4"]
    s0_fleet = trial_nominal["S0"]["fleet"]
    rows = OrderedDict()

    def add(label, note, get_fleet, s0=None):
        row = dict(_note=note)
        for c in pair:
            ens = _paired_margin(get_fleet(c), s0 or s0_fleet)
            row[c] = dict(min=ens["min"], median=ens["median"],
                          max=ens["max"])
        row["ordering_on_median"] = (
            "S2 ahead of S1" if row["S2"]["median"] > row["S1"]["median"]
            else "S1 ahead of S2")
        rows[label] = row

    add("r3_as_reported",
        "the margin of record: every r2 and r3 correction applied",
        lambda c: trial_nominal[c]["fleet"])
    add("F4_reverted_credit_removed",
        "the symmetric charge-sustaining CREDIT suppressed (the deficit "
        "make-up kept). Exact re-pricing of the same run.",
        lambda c: [dict(f, MJ_per_payload_tkm=f[
            "MJ_per_payload_tkm_deficit_only"])
            for f in trial_nominal[c]["fleet"]],
        s0=[dict(f, MJ_per_payload_tkm=f["MJ_per_payload_tkm_deficit_only"])
            for f in s0_fleet])
    add("F6_reverted_peak_point_pricing",
        "corrections priced at r1's peak-point efficiency instead of the "
        "candidate's duty average. Exact re-pricing of the same run.",
        lambda c: [dict(f, MJ_per_payload_tkm=f[
            "MJ_per_payload_tkm_r1_pricing"])
            for f in trial_nominal[c]["fleet"]],
        s0=[dict(f, MJ_per_payload_tkm=f["MJ_per_payload_tkm_r1_pricing"])
            for f in s0_fleet])

    # rows re-simulated with one switch reverted. `cands` may widen the
    # set, and `own_s0` says the row must be measured against ITS OWN
    # re-run ruler - which is what the S0 launch-fuel row needs, because
    # that correction moves S0 and therefore every margin.
    reruns = OrderedDict([
        ("F3_reverted_engine_dual_use",
         ("S2's single engine run as a locked mechanical drive AND a "
          "free-speed genset at the same time, uncapped - r1's treatment. "
          "Re-simulated.",
          [n for n in CD.ERRATA_ALL if n != "f3_s2_engine_budget"])),
        ("F5_reverted_spin_rule",
         ("R22(d) charged on r1's two different unloaded tests instead of "
          "the one program-wide rule. Re-simulated.",
          [n for n in CD.ERRATA_ALL if n != "f5_spin_rule"])),
        ("F3_and_F5_reverted",
         ("both r2 re-simulated corrections reverted; F4, F6 and B1 "
          "still applied. Re-simulated.",
          [n for n in CD.ERRATA_ALL
           if n not in ("f3_s2_engine_budget", "f5_spin_rule")])),
        ("B1_reverted_brake_and_fuel",
         ("THE r3 CORRECTION (R3_DIRECTIVE item 1). Reverted: the engine "
          "may fuel while the same crankshaft is compression-braking - "
          "S3's through-the-road charging gated on axle-A force being "
          "small rather than on the vehicle not braking, and S2's "
          "free-speed genset running while its lockup coupling is "
          "drawing the compression brake. Everything else r3 corrected "
          "is UNCONDITIONAL and stays applied in this row, so the row "
          "isolates the control law and nothing else. Re-simulated.",
          [n for n in CD.ERRATA_ALL if n != "b1_overrun_exclusivity"])),
    ])
    reruns["R3_S0_launch_fuel_reverted"] = (
        ("THE RULER'S OWN r3 CORRECTION. Reverted: S0 is fuelled at the "
         "idle rate on the first few tenths of a second of every "
         "pull-away, as it was in r1 and r2, while the model credits it "
         "with launch torque. This row is measured against ITS OWN "
         "re-run S0, so the delta against `r3_as_reported` is the effect "
         "of the RULER moving. Re-simulated, all five candidates.",
         [n for n in CD.ERRATA_ALL if n != "r3_s0_launch_fuel"]))
    own_s0 = {"R3_S0_launch_fuel_reverted"}
    for label, (note, errata) in reruns.items():
        names = (["S0"] + pair) if label in own_s0 else pair
        res = run_corner("nominal", ctx, seeds, cand_names=names,
                         verbose=False, pool=pool, errata=errata)
        add(label, note, lambda c, res=res: res[c]["fleet"],
            s0=res["S0"]["fleet"] if label in own_s0 else None)
    # restore the run of record in THIS process: everything downstream
    # (the heat ledger, the sanity block) builds candidates directly.
    CD.set_errata(None)

    ordering = OrderedDict((k, v["ordering_on_median"])
                           for k, v in rows.items())
    return dict(
        rule=("each row reverts EXACTLY ONE correction and leaves the "
              "rest applied; margins are the same paired per-seed "
              "ensemble as the headline, at the nominal corner. S0 is "
              "unaffected by every correction in this set (no errata "
              "switch reaches it), so the ruler is the same in every "
              "row - which is why a row's DELTA against "
              "`r3_as_reported` IS the direction that correction moved "
              "that candidate."),
        direction_convention=(
            "margin = (S0 - candidate)/S0 x 100, so HIGHER IS BETTER. "
            "delta = median(r3_as_reported) - median(row); delta > 0 "
            "means the correction moved the candidate UP, i.e. it was "
            "FOR that candidate; delta < 0 means AGAINST. A candidate "
            "whose delta is exactly 0.0 in a row is that correction "
            "PROVED not to reach it, not an assertion that it does not."),
        candidates=pair, rows=rows, ordering=ordering,
        ordering_changes=bool(len(set(ordering.values())) > 1))


DIRECTION_EPS_PP = 1e-9
"""Below this a one-factor delta is IDENTICAL, not small [pp]. The
reverted rows are re-simulations of the same seeds through the same code
with one switch flipped, so a candidate the switch does not reach comes
back bit-identical and its delta is exactly 0.0. The threshold exists to
absorb the last bit of a double, not to define a "negligible" band -
every non-zero delta is printed with its magnitude and the reader decides
what is negligible."""


def _direction_phrase(deltas, unit="pp", nil_word="re-run bit-identical"):
    """FOR / AGAINST / PROVED-UNAFFECTED, from measured deltas.

    `nil_word` says HOW a zero delta was obtained, because the rows are
    not all the same kind of measurement: F3, F5, B1 and the S0
    launch-fuel row are RE-SIMULATIONS with one switch flipped, so a
    candidate the switch does not reach comes back bit-identical; F4 and
    F6 are exact RE-PRICINGS of the same run, where a zero delta means
    the candidate carries none of that correction. Calling the second
    kind a bit-identical re-run would describe a run that never
    happened."""
    fav = [c for c, v in deltas.items() if v > DIRECTION_EPS_PP]
    against = [c for c, v in deltas.items() if v < -DIRECTION_EPS_PP]
    nil = [c for c, v in deltas.items() if abs(v) <= DIRECTION_EPS_PP]
    parts = []
    if fav:
        parts.append("FOR " + ", ".join(
            f"{c} ({deltas[c]:+.3f} {unit})" for c in fav))
    if against:
        parts.append("AGAINST " + ", ".join(
            f"{c} ({deltas[c]:+.3f} {unit})" for c in against))
    if nil:
        parts.append("does not reach " + ", ".join(nil)
                     + f" ({nil_word})")
    return "; ".join(parts) if parts else "no candidates measured"


def corner_derate_scope():
    """r2 finding M3, R3_DIRECTIVE item 4: 'state explicitly what the R28
    corner derates (engine only) and scope any conclusion drawn from it
    accordingly.'

    MEASURED, not asserted. Every corner's model is probed at the same
    fixed operating points as the nominal one and the two are compared
    leaf by leaf, so the scope of a corner's effect is a computed
    membership list. r2 concluded "the R28 corner did not become the
    worst one, and that is itself a result" from a corner whose thermal
    derate reaches the engine's full-load curve and nothing else - no
    hot-side model exists for the machine, the inverter, the pack or the
    resistor - and that conclusion has to be scoped by what the corner
    actually does."""
    probes = OrderedDict()
    base = None
    for corner, ctx in corners().items():
        row = OrderedDict()
        for cname in ("S0", "S1", "S2", "S3", "S4"):
            cand = make_candidate(cname, ctx)
            p = OrderedDict()
            p["engine_full_load_torque_at_1300rpm_Nm"] = (
                float(cand.engine.t_max(np.array([1300.0]))[0])
                if getattr(cand, "engine", None) is not None else None)
            p["compression_brake_rating_kW"] = getattr(
                cand, "p_engine_brake_kw", None)
            line = getattr(cand, "line", None)
            p["genset_bus_ceiling_kW"] = (float(line.p_elec_max_kw)
                                          if line is not None else None)
            pack = getattr(cand, "pack", None)
            p["pack_charge_ceiling_kW"] = (float(cand.pack_chg_limit_kw())
                                           if pack is not None else None)
            p["pack_discharge_ceiling_kW"] = (float(pack.p_cont_dis_kw)
                                              if pack is not None else None)
            p["brake_resistor_rating_kW"] = getattr(cand, "resistor_kw", None)
            ed = getattr(cand, "edrive", None)
            if ed is not None:
                p["machine_wheel_force_at_10ms_N"] = float(
                    ed.wheel_force_max(10.0))
                p["machine_eta_bus_to_wheel_at_10ms_200kW"] = float(
                    ed.eta_bus_to_wheel(np.array([10.0]), np.array([200.0]))[0])
                p["machine_spin_drag_at_20ms_kW"] = float(
                    ed.spin_drag_kw(np.array([20.0]))[0])
            p["accessory_mech_kW"] = float(ctx.aux_mech_kw)
            p["accessory_bus_kW"] = float(ctx.aux_bus_kw)
            p["air_density_kg_m3"] = float(ctx.rho_air)
            row[cname] = p
        probes[corner] = row
        if base is None:
            base = row
    scope = OrderedDict()
    for corner, row in probes.items():
        changed, same = [], []
        for cname, p in row.items():
            for k, v in p.items():
                b = probes["nominal"][cname].get(k)
                if v is None or b is None:
                    continue
                tag = f"{cname}.{k}"
                if abs(v - b) > 1e-9 * max(1.0, abs(b)):
                    changed.append(tag)
                else:
                    same.append(tag)
        scope[corner] = dict(
            quantities_that_move=sorted(changed),
            quantities_that_do_not=sorted(same),
            engine_side_moves=sorted(
                t for t in changed
                if any(w in t for w in ("engine_", "genset_",
                                        "compression_brake"))),
            electric_side_moves=sorted(
                t for t in changed
                if any(w in t for w in ("machine_", "pack_",
                                        "brake_resistor"))))
    hot = scope.get("hot_alt_2000m_45C", {})
    return dict(
        rule=("every corner's model probed at the same fixed operating "
              "points as nominal and compared leaf by leaf; membership "
              "is computed, not declared"),
        probes=probes, scope=scope,
        R28_corner=dict(
            corner="hot_alt_2000m_45C",
            derates=hot.get("engine_side_moves", []),
            does_not_derate=hot.get("electric_side_moves", []),
            electric_side_unchanged=bool(
                not hot.get("electric_side_moves")),
            statement=(
                "THE R28 CORNER DERATES THE ENGINE'S FULL-LOAD CURVE AND "
                "WHAT IS COMPUTED FROM IT, AND NOTHING ELSE. WS4's "
                "`derate_factor` is applied to every engine in the trial "
                "(S0's included) and therefore to the R18 continuous "
                "rating and the genset ceilings behind it. It is NOT "
                "applied to the traction machine, the inverter, the "
                "pack's charge or discharge ceiling, the brake resistor, "
                "or the compression brake - `ws8_electric.py` has no "
                "hot-side model at all and `Pack8.cold_chg_factor_at()` "
                "clamps to 1.0 above 15 C. The corner's BENEFIT - about "
                "27% off the aerodynamic bill at 2,000 m - is shared by "
                "every candidate; its PENALTY falls only on combustion. "
                "Any conclusion drawn from this corner is scoped to that: "
                "it says the thin air outweighs an ENGINE derate, not "
                "that it outweighs a hot day for the whole vehicle. The "
                "cab-cooling load IS charged symmetrically (mechanical "
                "and bus-side both rise), which is the one hot-side "
                "effect the electric path does pay."),
            direction_of_error=(
                "a missing hot-side electric derate FLATTERS the "
                "electrified candidates at this corner relative to S0; "
                "the corner is not binding for any of them, so no verdict "
                "depends on it, but WS9 inherits the statement under "
                "R28.")))


def correction_directions(R):
    """r2 finding M1, R3_DIRECTIVE item 2: 'delete every hand-written
    direction string; generate F3/F6 directions from the one-factor
    table.'

    r2's changelog stated the direction of each correction as a Python
    literal that `verify_ws8.py` structurally could not reach, and three
    of the thirteen were contradicted by this file's own numbers: F3 was
    labelled AGAINST S2 when the one-factor row has it +0.046 pp FOR S2,
    and F6 was labelled 'slightly FOR S2' when its row has it 0.013 pp
    AGAINST. That is r1's F9 failure mode - prose inside a generated
    artifact - recurring in the round that closed F9.

    Every direction cell in the record is now MEASURED here and rendered
    from this block; a correction with no one-factor row is labelled
    'not separately measured' with the reason, not given a direction from
    memory. The verifier asserts the rendered strings verbatim."""
    of = R.get("one_factor") or {}
    rows = of.get("rows") or {}
    cands = list(of.get("candidates") or [])
    base = rows.get("r3_as_reported")

    def measured(label, stat="median"):
        row = rows.get(label)
        if row is None or base is None:
            return None
        return OrderedDict((c, base[c][stat] - row[c][stat])
                           for c in cands if c in row and c in base)

    REPRICED = ("F4_reverted_credit_removed",
                "F6_reverted_peak_point_pricing")

    def entry(label, note):
        d = measured(label)
        if d is None:
            return dict(measurable=False, one_factor_row=label,
                        direction=("not separately measured - the "
                                   f"one-factor row `{label}` is not in "
                                   "this run"),
                        why_not=note)
        return dict(measurable=True, one_factor_row=label,
                    deltas_pp=d,
                    direction=_direction_phrase(
                        d, nil_word=("carries none of this correction"
                                     if label in REPRICED
                                     else "re-run bit-identical")),
                    basis=("median of the paired per-seed margin at the "
                           "NOMINAL corner; delta = "
                           "r3_as_reported - this row"),
                    note=note)

    NOT_REVERSIBLE = (
        "no one-factor row: reverting it would not be a one-line switch "
        "on the same run. It either rebuilds an export rather than the "
        "simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it "
        "changes what the corner IS rather than how a run is priced "
        "(F2's cold charge acceptance, F11/R28's added corner), so a "
        "'reverted' number would not be the same trial. The direction is "
        "left unstated rather than asserted.")

    out = OrderedDict()
    out["_rule"] = (
        "every direction below is computed from `one_factor.rows` by "
        "`correction_directions()`; nothing here is written by hand "
        "(r2 finding M1). A correction with no one-factor row is "
        "labelled not separately measured, with the reason.")
    out["_convention"] = of.get("direction_convention", "")
    out["F3"] = entry("F3_reverted_engine_dual_use",
                      "gated in S2 only (ws8_candidates.py, "
                      "`f3_s2_engine_budget`)")
    out["F4"] = entry("F4_reverted_credit_removed",
                      "exact re-pricing of the same run; applies to every "
                      "candidate that has a pack")
    out["F5"] = entry("F5_reverted_spin_rule",
                      "gated in S2 and S3 (`f5_spin_rule`)")
    out["F6"] = entry("F6_reverted_peak_point_pricing",
                      "exact re-pricing of the same run; applies to every "
                      "candidate that carries a correction")
    out["F3_and_F5"] = entry("F3_and_F5_reverted",
                             "both r2 re-simulated corrections together")
    out["R3_S0_launch_fuel"] = entry(
        "R3_S0_launch_fuel_reverted",
        "moves THE RULER, so it moves every margin; measured against its "
        "own re-run S0")
    out["B1"] = entry("B1_reverted_brake_and_fuel",
                      "gated in S2 and S3 (`b1_overrun_exclusivity`); the "
                      "r3 correction R3_DIRECTIVE item 1 orders")
    for k in ("F1", "F2", "F7", "F8", "F9", "F10", "F11", "F12", "F13"):
        out[k] = dict(measurable=False, one_factor_row=None,
                      direction="not separately measured",
                      why_not=NOT_REVERSIBLE)

    # F6 is an exact re-pricing, so its direction can be stated at EVERY
    # corner - and it does not have the same sign at every one, which is
    # exactly why a single hand-written cell was the wrong shape for it.
    per_corner = OrderedDict()
    for corner, mm in R.get("task3_margins", {}).items():
        d = OrderedDict()
        for c, blob in mm.items():
            if "ensemble_r1_pricing" in blob:
                d[c] = (blob["ensemble"]["median"]
                        - blob["ensemble_r1_pricing"]["median"])
        if d:
            per_corner[corner] = dict(
                deltas_pp=d,
                direction=_direction_phrase(
                    d, nil_word="carries none of this correction"))
    if per_corner:
        out["F6"]["per_corner"] = per_corner
        signs = set()
        for corner, blob in per_corner.items():
            for c, v in blob["deltas_pp"].items():
                signs.add((c, v > 0))
        flips = sorted({c for c, _ in signs
                        if (c, True) in signs and (c, False) in signs})
        out["F6"]["sign_flips_across_corners"] = flips
        out["F6"]["corner_caveat"] = (
            ("F6's direction is NOT the same at every corner - it flips "
             "for " + ", ".join(flips) + " - so the direction cell is "
             "stated at the nominal corner and the per-corner table is "
             "exported beside it.")
            if flips else
            "F6's direction has the same sign at every corner.")
    return out


def verdict_stability(R):
    """R2_DIRECTIVE item 3: 'Confirm verdicts unchanged against the
    criteria (expected; if any flips, STOP and report - do not touch the
    verdict).'

    R25 executed the four kills and the WHR drop on the pre-committed
    criteria. This block re-reads those criteria against the r2 numbers
    and states, per candidate, whether the verdict the lead executed is
    still what the criteria give. It does not re-decide anything - it
    only says whether the executed verdict and the corrected numbers
    still agree."""
    executed = {"S1": "KILL", "S2": "KILL", "S3": "KILL", "S4": "KILL"}
    rows = OrderedDict()
    for cname, exp in executed.items():
        v = R["advance_kill"]["candidates"].get(cname)
        if v is None:
            continue
        rows[cname] = dict(
            executed_verdict=exp,
            verdict_on_same_criteria=v["verdict"],
            unchanged=bool(v["verdict"] == exp),
            nominal_margin_pct_min=v["nominal_margin_pct_min"],
            worst_corner=v["worst_corner"],
            worst_corner_margin_pct_min=v["worst_corner_margin_pct_min"],
            headroom_to_advance_pp=(ADVANCE_NOMINAL_PCT
                                    - v["nominal_margin_pct_min"]))
    whr_now = {k: v["verdict"] for k, v in R["task4_whr"]["results"].items()}
    # R3_DIRECTIVE item 1's OWN trip-wire, implemented rather than
    # remembered: "if its nominal ensemble-min crosses +3%, STOP and
    # report, do not touch the verdict".
    s3 = rows.get("S3", {})
    s3_min = s3.get("nominal_margin_pct_min")
    stop = dict(
        rule=("R3_DIRECTIVE item 1: S3's fuel correction is expected to "
              "improve it by several percent and to leave it far below "
              "the bar. If S3's NOMINAL ENSEMBLE-MIN crosses "
              f"+{ADVANCE_NOMINAL_PCT:.0f}%, the round STOPS and reports "
              "and does not touch the verdict."),
        S3_nominal_margin_pct_min=s3_min,
        bar_pct=ADVANCE_NOMINAL_PCT,
        crossed=bool(s3_min is not None and s3_min >= ADVANCE_NOMINAL_PCT),
        note=("S3 is dead on CAPABILITY regardless of fuel - no fixed "
              "ratio both cruises at 105 km/h and holds the 6% grade at "
              "36,300 kg - so this trip-wire is about the fuel number "
              "the record carries, not about the verdict's reason."))
    return dict(
        criteria=R["advance_kill"]["criteria"],
        ruling="R25 (BASELINE_v4)",
        candidates=rows,
        whr_executed="DROPPED",
        whr_on_current_numbers=whr_now,
        whr_unchanged=bool(all(x == "DROPPED" for x in whr_now.values())),
        r3_stop_condition=stop,
        all_unchanged=bool(all(r["unchanged"] for r in rows.values())
                           and all(x == "DROPPED" for x in whr_now.values())
                           and not stop["crossed"]),
        note=("if `all_unchanged` were false the round would STOP and "
              "report rather than touch a verdict the lead has executed "
              "(R2_DIRECTIVE item 3, R3_DIRECTIVE item 1). It carries "
              "BOTH tests: the four executed verdicts against the "
              "pre-committed criteria, and R3_DIRECTIVE's own trip-wire "
              "on S3's nominal ensemble-min."))


NUMBERS_VERSION = "r3"
LEDGER_VERSION = "r3"
VERDICT_STATUS = "executed_kill_2026-08-30"
"""R3_DIRECTIVE item 7. The verdicts block carries the EXECUTED status
from R25 UNCHANGED - r3 does not reopen a verdict and this string is a
constant, not a computed value. The numbers block is versioned r3
because every number in it was regenerated by this round, and the heat
ledger carries its own version because R3_DIRECTIVE says WS6 consumes
ONLY the r3 ledger."""

# Inputs that are SHA-PINNED into the interface (R2_DIRECTIVE item 6):
# every file the NUMBERS depend on - WS8's own model and driver sources,
# the orders it executes, and every read-only object it inherits from
# another workstream. A consumer can then tell, from the export alone,
# whether the numbers it is holding were produced from these exact
# inputs.
#
# `make_report_ws8.py` and `verify_ws8.py` are deliberately NOT pinned:
# they CONSUME these numbers rather than produce them, so pinning them
# would make the export sensitive to a change that cannot move a single
# digit of it. The report's fidelity to the data is the separate thing
# `verify_ws8.py` asserts, and it asserts it against the data file
# itself.
_SHA_PIN_PATHS = [
    "run_ws8.py", "ws8_params.py", "ws8_physics.py", "ws8_cycles.py",
    "ws8_engine.py", "ws8_electric.py", "ws8_candidates.py", "ws8_whr.py",
    "requirements.txt",
    "ASSIGNMENT.md",
    # every order this workstream has executed, and every findings file
    # it has closed: the r2 corrections are still live in `ERRATA_ALL`
    # and the verdicts still cite R25/BASELINE_v4, so the numbers depend
    # on all of them, not only on the newest.
    "R2_DIRECTIVE.md", "R3_DIRECTIVE.md",
    "FINDINGS_WS8_r1.md", "FINDINGS_WS8_r2.md",
    "PRIOR_ART_WS8.md",
    "../BASELINE_v4.md", "../BASELINE_v5.md",
    "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv",
    "../WS2_traction_motor/data/capability_vs_rpm.csv",
    "../WS3_battery/ws3_cells.py", "../WS3_battery/ws3_pack.py",
    "../WS4_genset/ws4_models.py", "../WS4_genset/ws4_chain.py",
]


def _sha256_of(rel):
    path = os.path.join(HERE, rel)
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


INPUT_SHA256 = OrderedDict(
    (p, _sha256_of(p)) for p in _SHA_PIN_PATHS)


def interface_block(R):
    """Machine-readable export. R14: every worst-case field is an explicit
    max/min over an ENUMERATED case set with the governing case labelled
    inline. Nothing here is transcribed by hand; verify_ws8.py asserts the
    report renders exactly these values."""
    iface = OrderedDict()
    iface["_convention"] = (
        "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); "
        "stochastic extrema are 8-seed ensemble envelopes (rule 4); every "
        "worst-case field is an explicit max/min over an enumerated case "
        "set with the governing case labelled (R14)")
    # --- versioning and verdict status (R2_DIRECTIVE item 6) -----------
    iface["numbers_version"] = NUMBERS_VERSION
    iface["numbers_status"] = (
        "r3 - the round ordered by WS8_semi_architecture/R3_DIRECTIVE.md "
        "under R35, closing FINDINGS_WS8_r2.md (B1 blocking, M1-M4, "
        "m1-m7). Every number in this block is regenerated; r2's numbers "
        "are superseded, not amended in place, and r2's heat ledger is "
        "WITHDRAWN - see `heat_ledger_WS6.ledger_version`.")
    iface["supersedes"] = dict(
        numbers_version="r2", ledger_version="r2",
        why=("r2's control law let an engine fuel while the same "
             "crankshaft was compression-braking (B1), so r2's S2 and S3 "
             "fuel numbers and its largest ledger row are withdrawn. S0, "
             "S1 and S4 are re-run unchanged in control law; their small "
             "movements are the r3 accounting corrections the extended "
             "run closure found, and they are measured in "
             "`one_factor_S1_vs_S2`."))
    iface["verdicts"] = dict(
        status=VERDICT_STATUS,
        ruling="R25 (BASELINE_v4): WS8 verdicts EXECUTED on the "
               "pre-committed criteria",
        reopened_by_this_round=False,
        note=("the kills and the WHR drop are EXECUTED and are not "
              "reopened by r2; this round makes the NUMBERS of record "
              "correct. Every r2 correction was checked against the "
              "pre-committed criteria and none flips a verdict - see "
              "`verdict_stability`."),
        result={k: v["verdict"]
                for k, v in R["advance_kill"]["candidates"].items()},
        whr="DROPPED")
    iface["inputs_sha256"] = INPUT_SHA256
    iface["inputs_sha256_scope"] = (
        "every file the numbers depend on: WS8's model and driver "
        "sources, the orders this round executes, and the read-only "
        "objects inherited from WS2, WS3 and WS4. The report generator "
        "and the verifier are excluded because they consume these "
        "numbers rather than produce them.")
    iface["metric_of_record"] = (
        "fleet-mission fuel energy per PAYLOAD tonne-km [MJ/(t.km)], "
        "fleet mission = 70% LH-520 + 30% REG-165 by distance")
    iface["gcw_kg"] = VEH.m_gcw
    iface["vehicle"] = dict(CdA_m2=VEH.CdA, Crr=VEH.Crr,
                            r_dyn_m=VEH.r_dyn,
                            provisional_per_E13_precedent=True)

    # --- per-candidate headline ---------------------------------------
    cands = OrderedDict()
    for cname, blob in R["task3_trial"]["nominal"].items():
        ens = blob["fleet_ensemble"]["MJ_per_payload_tkm"]
        m = R["task3_margins"]["nominal"].get(cname)
        corner_cases = {}
        for corner, mm in R["task3_margins"].items():
            if cname in mm:
                corner_cases[corner] = mm[cname]["ensemble"]["min"]
        gov = (min(corner_cases, key=lambda k: corner_cases[k])
               if corner_cases else None)
        rows_all = [x for cy in blob["per_cycle"].values() for x in cy]
        shares = [x["correction_share_of_fuel"] for x in rows_all]
        uns = [x["unserved_kWh"] for x in rows_all]
        etas = [x["correction_eta_fuel_to_bus"] for x in rows_all]
        soc_g = [x["fuel_g_charge_correction"] for x in rows_all]
        spin_c = [x.get("e_spin_kWh", 0.0) for x in rows_all]
        spin_b = [x.get("e_spin_coast_bracket_kWh", 0.0) for x in rows_all]
        i_max = int(np.argmax(shares))
        i_min = int(np.argmin(shares))
        keys = [f"{cy}/seed{x['seed']}"
                for cy, rows in blob["per_cycle"].items() for x in rows]
        cands[cname] = dict(
            title=blob["spec"]["title"],
            payload_kg=blob["spec"]["payload_kg"],
            powertrain_mass_kg=blob["spec"]["powertrain_mass_kg"],
            # r1 finding F4: this exported only the MAX of a SIGNED
            # quantity, so S2's dominant cycle - which carries a CREDIT
            # of about a point of its fuel - was invisible to a consumer
            # of the interface, and the `meaning` string described only
            # the deficit direction. Both ends are exported now.
            fuel_correction_share=dict(
                rule="max AND min over the enumerated (cycle, seed) case "
                     "set; the quantity is SIGNED - negative is a CREDIT",
                value=max(shares), max=max(shares), min=min(shares),
                median=float(np.median(shares)),
                governing_case_max=keys[i_max],
                governing_case_min=keys[i_min],
                governing_case="worst (cycle, seed) at the nominal corner",
                meaning=("fraction of this candidate's reported fuel that "
                         "is a CORRECTION rather than fuel the model "
                         "watched it burn: unserved energy charged back as "
                         "fuel, plus the SYMMETRIC charge-sustaining "
                         "correction. The charge-sustaining term is signed "
                         "- a pack that ends FLATTER than it started is "
                         "charged the make-up, a pack that ends FULLER "
                         "earns the credit - so a NEGATIVE share means "
                         "this candidate's fuel figure is being reduced by "
                         "a pack surplus that regen put there. A large "
                         "POSITIVE share means the candidate could not "
                         "actually do the mission and was credited with "
                         "doing it anyway, which is a capability finding.")),
            charge_correction_direction=dict(
                rule="sign of the charge-sustaining correction over the "
                     "enumerated (cycle, seed) case set",
                credit_cases=[k for k, gsoc in zip(keys, soc_g)
                              if gsoc < 0.0],
                deficit_cases=[k for k, gsoc in zip(keys, soc_g)
                               if gsoc > 0.0],
                convention="symmetric, SAE J1711 in spirit; declared"),
            margin_vs_S0_pct_credit_free=(
                dict(rule="the same paired per-seed margin with the "
                          "charge-sustaining CREDIT suppressed and the "
                          "deficit make-up kept (F4)",
                     **{k: m["ensemble_deficit_only"][k]
                        for k in ("min", "median", "max")})
                if m else None),
            correction_eta_fuel_to_bus=dict(
                rule="duty-averaged over the run being corrected, min/"
                     "median/max over the enumerated (cycle, seed) set "
                     "(rule 5: r1 used the locus MAXIMUM)",
                min=min(etas), median=float(np.median(etas)),
                max=max(etas),
                basis=rows_all[0].get("correction_eta_basis")),
            spin_drag_R22d_kWh=dict(
                rule="max over the enumerated (cycle, seed) case set",
                charged=max(spin_c),
                coast_permitting_bracket=max(spin_b),
                meaning=("R22(d). `charged` is what this candidate paid; "
                         "`coast_permitting_bracket` is what the same "
                         "measured zero-torque loss would cost if it were "
                         "charged on every geared moving sample. This "
                         "integrator's driver is always either pulling or "
                         "braking, so the charged figure is near zero for "
                         "every candidate - that is a property of the "
                         "DRIVER MODEL, not of the architecture, and the "
                         "bracket is the honest statement of what R22(d) "
                         "is worth here. The bracket is NOT in any margin.")),
            unserved_kWh_nominal=dict(
                rule="max over the enumerated (cycle, seed) case set",
                value=max(uns)),
            fleet_MJ_per_payload_tkm=dict(
                rule="8-seed ensemble", min=ens["min"], median=ens["median"],
                max=ens["max"]),
            fleet_L_per_100km=dict(
                **{k: blob["fleet_ensemble"]["L_per_100km"][k]
                   for k in ("min", "median", "max")}),
            margin_vs_S0_pct=(dict(
                nominal_min=m["ensemble"]["min"],
                nominal_median=m["ensemble"]["median"],
                nominal_max=m["ensemble"]["max"]) if m else None),
            worst_case_margin_pct=(dict(
                rule="min over the enumerated corner set, ensemble-min "
                     "within each corner",
                cases=corner_cases, value=corner_cases[gov],
                governing_case=gov) if corner_cases else None),
            verdict=R["advance_kill"]["candidates"].get(cname, {})
            .get("verdict", "n/a (S0 is the ruler)"))
    iface["candidates"] = cands

    # --- worst-case unserved energy -----------------------------------
    uns = {}
    for corner, blob in R["task3_trial"].items():
        for cname, r in blob.items():
            for cy, rows in r["per_cycle"].items():
                key = f"{cname}/{corner}/{cy}"
                uns[key] = max(x["unserved_kWh"] for x in rows)
    gov = max(uns, key=lambda k: uns[k])
    iface["unserved_energy_kWh"] = dict(
        rule="max over the enumerated (candidate, corner, cycle) case set",
        value=uns[gov], governing_case=gov,
        cases_over_1kWh={k: v for k, v in sorted(uns.items()) if v > 1.0},
        meaning=("bus energy the prime mover and pack together could not "
                 "deliver. It is charged back as fuel so every candidate "
                 "completes the same mission, and reported here raw because "
                 "a large value is a CAPABILITY finding, not a fuel one."))

    iface["retard_overcommitment"] = R["retard_overcommitment"]

    iface["advance_kill"] = R["advance_kill"]["criteria"]
    iface["advance_kill_result"] = {
        k: v["verdict"] for k, v in R["advance_kill"]["candidates"].items()}
    iface["whr_gate"] = dict(
        threshold_pct=WHR.GATE_PCT,
        result={k: v["verdict"] for k, v in R["task4_whr"]["results"].items()},
        best_net_margin_pct={
            k: v["best_net_margin_pct_median"]
            for k, v in R["task4_whr"]["results"].items()})

    # --- S3 capability, the reason it is killed -----------------------
    fr = R["task5_s3_specific"]["fixed_ratio_grade_hold"]
    iface["S3_fixed_ratio_feasibility"] = dict(
        rule=("a ratio is feasible only if it holds the 6% mountain grade "
              "AND keeps the engine under 2,100 rpm at 105 km/h; "
              "enumerated over the swept ratio set"),
        ratios_tested=[r["ratio_A"] for r in fr["sweep"]],
        feasible_ratios=fr["feasible_ratios_for_6pct"],
        any_feasible=fr["any_ratio_holds_6pct"],
        max_ratio_without_overspeed=fr["max_ratio_without_overspeed"],
        max_ratio_without_overspeed_rule=fr[
            "max_ratio_without_overspeed_rule"],
        # F12: the PHYSICS bound, in closed form. The swept figure above
        # is a property of the enumerated grid, and r1's report stated it
        # as though it were the limit.
        ratio_ceiling_closed_form=fr["ratio_ceiling_closed_form"],
        ratio_needed_to_hold_6pct=fr["ratio_needed_to_hold_6pct"],
        governing_case="6% mountain grade at 36,300 kg GCW")
    adh = R["task5_s3_specific"]["diesel_axle_adhesion"]["single_axle_A"]
    worst = min(adh, key=lambda r: r["max_grade_held_on_adhesion"])
    iface["S3_diesel_axle_adhesion_grade_limit"] = dict(
        rule="min over the enumerated surface case set (R14)",
        cases={r["surface"]: r["max_grade_held_on_adhesion"] for r in adh},
        value=worst["max_grade_held_on_adhesion"],
        governing_case=f"{worst['surface']}, mu {worst['mu']}")
    iface["S3_eaxle_fault"] = dict(
        can_launch_from_rest=R["task5_s3_specific"]["fault_limp"]
        ["e_axle_fault"]["can_launch_from_rest"],
        verdict="TOW (immobile from rest)")

    # --- r2 finding M2: the per-km statistic, labelled ----------------
    iface["per_km_margin_paired"] = dict(
        rule=("PAIRED per-seed margin on fleet-mission MJ per KILOMETRE - "
              "candidate seed i against S0 seed i - then the 8-seed "
              "envelope. This is the statistic every per-km claim in the "
              "report is made on. The RATIO OF MEDIANS is exported "
              "beside it for disclosure only: r2's headline bullets were "
              "computed that way while every margin in the report was "
              "paired, and for S3 the two statistics differ in SIGN."),
        corners=OrderedDict(
            (corner, OrderedDict(
                (c, blob["per_km"]) for c, blob in mm.items()
                if "per_km" in blob))
            for corner, mm in R["task3_margins"].items()),
        every_candidate_wins_per_km_at_nominal=bool(all(
            blob["per_km"]["wins_on_every_seed"]
            for blob in R["task3_margins"]["nominal"].values()
            if "per_km" in blob)))

    # --- r2 finding M1: directions, generated ------------------------
    iface["correction_directions"] = R.get("correction_directions", {})
    # --- r2 finding M3: what each corner actually derates -------------
    iface["corner_derate_scope"] = dict(
        rule=R["corner_derate_scope"]["rule"],
        scope=R["corner_derate_scope"]["scope"],
        R28_corner=R["corner_derate_scope"]["R28_corner"])

    # --- do the corrections flip anything? (R2_DIRECTIVE item 3) ------
    iface["verdict_stability"] = R["verdict_stability"]
    if R.get("one_factor"):
        iface["one_factor_S1_vs_S2"] = dict(
            rule=R["one_factor"]["rule"],
            direction_convention=R["one_factor"]["direction_convention"],
            candidates=R["one_factor"]["candidates"],
            ordering=R["one_factor"]["ordering"],
            rows={k: {c: v.get(c) for c in R["one_factor"]["candidates"]}
                  for k, v in R["one_factor"]["rows"].items()})

    iface["heat_ledger_WS6"] = R["heat_ledger"]
    iface["escalations"] = [e["id"] for e in R["escalations"]]
    iface["ws2_chain_of_record"] = dict(
        map_file=EL.ScaledEDrive(1.0, 12.0).ws2_map_file,
        map_voltage_V=EL.ScaledEDrive(1.0, 12.0).ws2_map_voltage_V,
        ws2_rework_round=EL.ScaledEDrive(1.0, 12.0).ws2_rework_round,
        feasible_cells=EL.ScaledEDrive(1.0, 12.0).n_feasible_cells,
        loader="WS4 ws4_chain.WS2TractionChain (ruled), read-only")
    return iface


def headline(R):
    nom = R["task3_trial"]["nominal"]
    rows = []
    for cname, blob in nom.items():
        e = blob["fleet_ensemble"]["MJ_per_payload_tkm"]
        m = R["task3_margins"]["nominal"].get(cname)
        rows.append(OrderedDict(
            candidate=cname, title=blob["spec"]["title"],
            payload_kg=blob["spec"]["payload_kg"],
            fleet_L_per_100km_median=blob["fleet_ensemble"]["L_per_100km"]
            ["median"],
            MJ_per_payload_tkm_min=e["min"],
            MJ_per_payload_tkm_median=e["median"],
            MJ_per_payload_tkm_max=e["max"],
            margin_vs_S0_pct_min=m["ensemble"]["min"] if m else None,
            margin_vs_S0_pct_median=m["ensemble"]["median"] if m else None,
            margin_vs_S0_pct_max=m["ensemble"]["max"] if m else None,
            verdict=R["advance_kill"]["candidates"].get(cname, {})
            .get("verdict", "RULER")))
    return dict(table=rows,
                any_advance=R["advance_kill"]["any_advance"],
                s0_fleet_L_per_100km=R["task2_s0_calibration"]
                ["fleet_L_per_100km"]["median"],
                whr={k: v["verdict"] for k, v in
                     R["task4_whr"]["results"].items()})


# =====================================================================
#  CSV exports
# =====================================================================
def _w(path, header, rows, preamble=None):
    """Write a CSV. `preamble` is a list of `#`-comment lines written
    above the header - used by the heat ledger to carry its version and
    the basis of each row into the file a consumer actually opens
    (R3_DIRECTIVE item 7, and r2 finding m3)."""
    with open(os.path.join(DATA, path), "w") as f:
        for line in (preamble or []):
            f.write("# " + line + "\n")
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(
                (f"{x:.6g}" if isinstance(x, float) else str(x))
                for x in r) + "\n")


def write_csvs(R):
    # per-seed candidate results, every corner, every cycle
    rows = []
    for corner, blob in R["task3_trial"].items():
        for cname, r in blob.items():
            for cy, per in r["per_cycle"].items():
                for x in per:
                    rows.append([
                        corner, cname, cy, int(x.get("seed", 0) or 0),
                        x["distance_km"], x["duration_s"],
                        x["avg_speed_kmh"], x["power_limited_fraction"],
                        x["payload_kg"], x["gcw_kg"],
                        x["fuel_g_raw"], x["fuel_g_corrected"],
                        x["fuel_L_per_100km"], x["MJ_per_km"],
                        x["MJ_per_payload_tkm"], x["unserved_kWh"],
                        x["charge_sustain_deficit_kWh"],
                        x["fuel_g_charge_correction"],
                        x["correction_share_of_fuel"],
                        x["correction_eta_fuel_to_bus"],
                        x.get("e_spin_kWh", 0.0),
                        x.get("e_spin_coast_bracket_kWh", 0.0),
                        x.get("e_resistor_kWh", 0.0),
                        x.get("e_engine_brake_kWh", 0.0),
                        x.get("e_friction_brake_kWh", 0.0),
                        x.get("resistor_peak_kW", 0.0),
                        x.get("engine_brake_peak_kW", 0.0)])
    _w("candidate_runs.csv",
       ["corner", "candidate", "cycle", "seed", "distance_km", "duration_s",
        "avg_speed_kmh", "power_limited_frac", "payload_kg", "gcw_kg",
        "fuel_g_raw", "fuel_g_corrected", "fuel_L_per_100km", "MJ_per_km",
        "MJ_per_payload_tkm", "unserved_kWh", "charge_deficit_kWh",
        "fuel_g_charge_correction_signed", "correction_share",
        "correction_eta_fuel_to_bus", "e_spin_kWh",
        "e_spin_coast_bracket_kWh", "e_resistor_kWh", "e_engine_brake_kWh",
        "e_friction_brake_kWh", "resistor_peak_kW",
        "engine_brake_peak_kW"], rows)

    # fleet-mission summary + margins
    rows = []
    for corner, blob in R["task3_trial"].items():
        for cname, r in blob.items():
            for f in r["fleet"]:
                mm = R["task3_margins"][corner].get(cname)
                mv = ""
                if mm:
                    mv = next((p["margin_pct"] for p in mm["per_seed"]
                               if p["seed"] == f["seed"]), "")
                mv_do = ""
                mv_km = ""
                if mm:
                    mv_do = next((p["margin_pct_deficit_only"]
                                  for p in mm["per_seed"]
                                  if p["seed"] == f["seed"]), "")
                    mv_km = next((p["margin_pct_per_km"]
                                  for p in mm["per_seed"]
                                  if p["seed"] == f["seed"]), "")
                rows.append([corner, cname, f["seed"], f["payload_t"],
                             f["L_per_100km"], f["MJ_per_km"],
                             f["MJ_per_payload_tkm"],
                             f["MJ_per_payload_tkm_deficit_only"], mv,
                             mv_do, mv_km])
    _w("fleet_mission.csv",
       ["corner", "candidate", "seed", "payload_t", "L_per_100km",
        "MJ_per_km", "MJ_per_payload_tkm",
        "MJ_per_payload_tkm_credit_free", "margin_vs_S0_pct",
        "margin_vs_S0_pct_credit_free", "margin_vs_S0_per_km_pct"], rows,
       preamble=["`margin_vs_S0_per_km_pct` is the PAIRED per-seed per-km "
                 "margin (r2 finding M2): candidate seed i against S0 seed "
                 "i. The report's per-km claims are made on the median of "
                 "this column, never on a ratio of medians."])

    # cycle statistics
    rows = []
    for cy, blob in R["task1_cycles"]["cycles"].items():
        for s in blob["per_seed"]:
            rows.append([cy, s["seed"], s["distance_km"], s["grade_max"],
                         s["grade_min"], s["net_elevation_change_m"],
                         s["total_climb_m"],
                         s["frac_dist_grade_2_to_3pct"],
                         s["frac_dist_grade_ge_5pct"], s["v_wind_ms"],
                         s["n_stops"]])
    _w("cycle_stats.csv",
       ["cycle", "seed", "distance_km", "grade_max", "grade_min",
        "net_elev_m", "total_climb_m", "frac_2_3pct", "frac_ge_5pct",
        "v_wind_ms", "n_stops"], rows)

    # S3 fixed-ratio sweep - the table that kills S3
    rows = []
    for r in R["task5_s3_specific"]["fixed_ratio_grade_hold"]["sweep"]:
        rows.append([r["ratio_A"], r["coupling_floor_kmh"],
                     r["cruise"]["engine_rpm_at_v_max"],
                     int(r["cruise"]["ok"]),
                     r["grade_2pct"]["status"],
                     r["grade_3pct"]["status"],
                     r["grade_4pct"]["status"],
                     r["grade_6pct"]["status"],
                     r["grade_6pct"]["F_required_at_ref_kN"],
                     r["grade_6pct"]["F_axleA_at_ref_kN"],
                     r["climb_6pct"].get("e_required_bus_kWh") or 0.0,
                     r["climb_6pct"]["e_pack_available_kWh"],
                     int(bool(r["climb_6pct"]["feasible"]))])
    _w("s3_fixed_ratio_sweep.csv",
       ["ratio_A", "coupling_floor_kmh", "engine_rpm_at_105kmh",
        "cruise_ok", "hold_2pct", "hold_3pct", "hold_4pct", "hold_6pct",
        "F_required_6pct_kN", "F_axleA_6pct_kN", "climb_energy_req_kWh",
        "pack_available_kWh", "climb_feasible"], rows)

    # WHR gate
    rows = []
    for cname, r in R["task4_whr"]["results"].items():
        for sysname, v in r["systems"].items():
            rows.append([cname, sysname, v["mass_charge_kg"],
                         v["payload_before_kg"], v["payload_after_kg"],
                         v["ensemble"]["min"], v["ensemble"]["median"],
                         v["ensemble"]["max"], int(v["passes_gate"])])
    _w("whr_gate.csv",
       ["candidate", "system", "mass_kg", "payload_before_kg",
        "payload_after_kg", "net_margin_min_pct", "net_margin_median_pct",
        "net_margin_max_pct", "passes_2p5pct_gate"], rows)

    # heat ledger for WS6
    hlv = R["heat_ledger"]["ledger_version"]
    rows = []
    labels = []
    for cname, blob in R["heat_ledger"]["candidates"].items():
        for case, comp in blob["cases"].items():
            sim = case == "simulated_worst_run"
            csum = sum(comp.get(k) or 0.0 for k in CD.HEAT_ROWS)
            rows.append([hlv, cname, case,
                         "envelope_over_runs" if sim
                         else "single_operating_point",
                         comp.get("road_speed_kmh"),
                         comp.get("case_wheel_power_kW"),
                         comp["engine_coolant_kW"], comp["engine_exhaust_kW"],
                         comp["traction_machine_inverter_kW"],
                         comp["generator_rectifier_kW"], comp["pack_kW"],
                         comp["brake_resistor_kW"],
                         comp["friction_brake_kW"], comp["accessory_kW"],
                         comp["driveline_kW"], comp["total_rejected_kW"],
                         csum, comp.get("_governing_run") or ""])
            if sim:
                for k in CD.HEAT_ROWS:
                    labels.append([hlv, cname, k, comp.get(k) or 0.0,
                                   comp.get(k + "_instantaneous_kW") or 0.0,
                                   comp.get(k + "_run") or ""])
    _w("heat_ledger_ws6.csv",
       ["ledger_version", "candidate", "case", "basis", "road_speed_kmh",
        "wheel_power_kW",
        "engine_coolant_kW", "engine_exhaust_kW", "machine_inverter_kW",
        "generator_rectifier_kW", "pack_kW", "brake_resistor_kW",
        "friction_brake_kW", "accessory_kW", "driveline_kW",
        "total_rejected_kW", "components_sum_kW", "governing_run"], rows,
       preamble=[
           f"WS8 heat ledger, version {hlv}. "
           + R["heat_ledger"]["consumer_rule"],
           "READ `basis` BEFORE `total_rejected_kW` (r2 finding m3). The "
           "four analytic cases are SINGLE OPERATING POINTS, so their "
           "total IS the sum of their component columns. The "
           "`simulated_worst_run` row is not a case the truck is ever in: "
           "each component column is that component's own maximum "
           "60-second mean over every (corner, cycle, seed) run in the "
           "trial, and its `total_rejected_kW` is the peak of the "
           "per-sample SUM - a different moment. `components_sum_kW` is "
           "printed so the difference is visible rather than looking like "
           "an arithmetic error; per-component run labels are in "
           "heat_ledger_ws6_simulated_labels.csv."])
    if labels:
        _w("heat_ledger_ws6_simulated_labels.csv",
           ["ledger_version", "candidate", "component", "sustained_kW",
            "instantaneous_kW", "governing_run"], labels,
           preamble=[
               "Per-component labels for the `simulated_worst_run` member "
               "(r2 findings m3 and m4). `sustained_kW` is the maximum "
               "60-second mean and is the exported figure; "
               "`instantaneous_kW` is the maximum single 10 Hz sample of "
               "the same component on the same run, computed since r2 and "
               "exported since r3 so that what the averaging window hides "
               "is visible. `governing_run` is corner/cycle/seed and the "
               "road speed at the window."])

    # the R14 worst case per component, with the governing case named -
    # this is the field WS6 actually consumes (rule 7)
    rows = []
    for cname, blob in R["heat_ledger"]["candidates"].items():
        for k, wc in blob["worst_case"].items():
            rows.append([cname, k, wc["value"], wc["governing_case"],
                         wc.get("governing_run") or ""])
        for rc in blob["ratings_check"]["rows"]:
            rows.append([cname, f"RATING[{rc['component']}]",
                         rc["rated_kW"], rc["governing_case"],
                         "within_rating" if rc["within_rating"]
                         else "OVER RATING"])
    _w("heat_ledger_ws6_worst_case.csv",
       ["ledger_version", "candidate", "component", "value_kW",
        "governing_case", "governing_run_or_rating_status"],
       [[hlv] + r for r in rows],
       preamble=[f"WS8 heat ledger, version {hlv}. "
                 + R["heat_ledger"]["consumer_rule"]])

    # one-factor rows: which correction decides S1 vs S2 (R2 directive)
    rows = []
    for label, r in R.get("one_factor", {}).get("rows", {}).items():
        for c in R["one_factor"]["candidates"]:
            rows.append([label, c, r[c]["min"], r[c]["median"], r[c]["max"],
                         r["ordering_on_median"]])
    if rows:
        _w("one_factor_s1_vs_s2.csv",
           ["row", "candidate", "margin_min_pct", "margin_median_pct",
            "margin_max_pct", "ordering_on_median"], rows,
           preamble=[R["one_factor"]["direction_convention"]])

    # mass ledgers
    rows = []
    for cname, blob in R["task3_trial"]["nominal"].items():
        for k, v in blob["spec"]["mass_rows_kg"].items():
            rows.append([cname, k, v])
        rows.append([cname, "TOTAL_powertrain",
                     blob["spec"]["powertrain_mass_kg"]])
        rows.append([cname, "tare_common", blob["spec"]["tare_common_kg"]])
        rows.append([cname, "PAYLOAD", blob["spec"]["payload_kg"]])
    _w("mass_ledger.csv", ["candidate", "item", "kg"], rows)


if __name__ == "__main__":
    main()
