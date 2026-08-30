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
from ws8_params import (VEH, ADH, AUX, DL, ML, SC, CY as CYP, G,
                        LHV_KJ_PER_G, DIESEL_DENSITY_KG_PER_L, params_dump)

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
              "charge acceptance, tyre Crr up 8%")
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
    return out


def genset_eta_for_correction(cand):
    """Fuel-to-bus efficiency used to price stored and unserved energy."""
    line = getattr(cand, "line", None)
    if line is not None:
        return line.best_point()["genset_eta_fuel_to_bus"]
    # S3 has no genset: price it through the mechanical path at the
    # engine's own island efficiency times the axle-A driveline.
    eng = getattr(cand, "engine", None)
    if eng is not None:
        eta_eng = 3600.0 / (eng.min_bsfc_point()["bsfc"] * LHV_KJ_PER_G)
        return eta_eng * getattr(cand, "eta_A", DL.eta_axle_tandem)
    return 0.40


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
    """
    eta = genset_eta_for_correction(cand)
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
    acc["fuel_g_unserved_correction"] = g_uns
    acc["correction_eta_fuel_to_bus"] = eta
    acc["fuel_g_corrected"] = acc["fuel_g"] + g_soc + g_uns
    acc["e_fuel_MJ_corrected"] = EN.fuel_energy_MJ(acc["fuel_g_corrected"])
    acc["correction_share_of_fuel"] = (
        (g_soc + g_uns) / acc["fuel_g_corrected"]
        if acc["fuel_g_corrected"] > 0 else 0.0)
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
def run_candidate(corner_name, cname, whr_name, seeds):
    """One (corner, candidate) job. Self-contained and deterministic, so it
    can be run in a worker process without changing a single digit: it
    reconstructs its own context and candidate from names rather than
    receiving live objects, and every random draw is seeded."""
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
        l_per_100 = sum(FLEET_MIX[c] * per_cycle[c][i]["fuel_L_per_100km"]
                        for c in FLEET_MIX)
        payload_t = per_cycle["LH-520"][i]["payload_kg"] / 1000.0
        fleet.append(dict(seed=int(sd), MJ_per_km=mj_per_km,
                          L_per_100km=l_per_100, payload_t=payload_t,
                          MJ_per_payload_tkm=mj_per_km / payload_t))
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
               verbose=True, pool=None, whr_name=None):
    """Every candidate over both cycles over the seed ensemble.

    Jobs are independent by construction (each reconstructs its own
    context and is fully seeded), so they may be run in a process pool.
    Results are re-ordered into `cand_names` order before use, so the
    output - and therefore results_ws8.json - is byte-identical whether
    the run was parallel or serial."""
    cand_names = cand_names or ["S0", "S1", "S2", "S3", "S4"]
    jobs = [(corner_name, c, whr_name, tuple(seeds)) for c in cand_names]
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
                    margin_pct=(base - f["MJ_per_payload_tkm"]) / base * 100.0))
        out[cname] = dict(
            per_seed=per_seed,
            ensemble=ensemble([p["margin_pct"] for p in per_seed]))
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
        baseline_of_record="BASELINE_v3.md",
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

    # ------------------------------------------------- advance / kill
    R["advance_kill"] = advance_kill(R["task3_margins"])
    print("== ADVANCE/KILL ==", flush=True)
    for k, v in R["advance_kill"]["candidates"].items():
        wc = v["worst_corner_margin_pct_min"]
        wtxt = (f"{wc:+.2f}% @ {v['worst_corner']}" if wc is not None
                else "no corners run")
        print(f"   {k}: {v['verdict']}  (nominal min "
              f"{v['nominal_margin_pct_min']:+.2f}%, worst corner "
              f"{wtxt})", flush=True)

    print("== heat ledger (rule 7, for WS6) ==", flush=True)
    R["heat_ledger"] = heat_ledger(seeds, cs["nominal"])

    R["sanity"] = sanity_checks(R)
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
    R["advance_kill"] = advance_kill(R["task3_margins"])
    for k, v in R["advance_kill"]["candidates"].items():
        wc = v["worst_corner_margin_pct_min"]
        wtxt = (f"{wc:+.2f}% @ {v['worst_corner']}" if wc is not None
                else "no corners run")
        print(f"   {k}: {v['verdict']}  (nominal min "
              f"{v['nominal_margin_pct_min']:+.2f}%, worst corner {wtxt})",
              flush=True)
    R["heat_ledger"] = heat_ledger(seeds, corners()["nominal"])
    R["sanity"] = sanity_checks(R)
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
# WS8's LH-520 corridor is NOT that cycle: it carries ~3,800 m of climb,
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


def s0_flat_crosscheck(seeds, ctx):
    cand = make_candidate("S0", ctx)
    tables = PH.build_env_tables(cand.envelope, cand.lam)
    rows = []
    for sd in seeds:
        cyc = CY.build_linehaul(sd)
        cyc = dict(cyc)
        cyc["grade_grid"] = np.zeros_like(cyc["grade_grid"])
        rows.append(run_one(cand, cyc, sd, tables=tables))
    return dict(
        cycle="LH-520 with grade zeroed (terrain isolated)",
        L_per_100km=ensemble([r["fuel_L_per_100km"] for r in rows]),
        avg_speed_kmh=ensemble([r["avg_speed_kmh"] for r in rows]),
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
        met0 = blob["fleet_ensemble"]["MJ_per_payload_tkm"]["median"]
        met1 = met0 * pay0 / pay1
        s0m = trial_nominal["S0"]["fleet_ensemble"][
            "MJ_per_payload_tkm"]["median"]
        out[cname] = dict(
            k_single_speed=k_1sp, k_two_speed=k_2sp,
            edrive_mass_single_kg=m1["total_kg"],
            edrive_mass_two_speed_kg=m2["total_kg"],
            two_speed_box_kg=TWO_SPEED_BOX_KG,
            net_mass_change_kg=d_mass,
            payload_single_kg=pay0, payload_two_speed_kg=pay1,
            MJ_per_payload_tkm_single=met0,
            MJ_per_payload_tkm_two_speed=met1,
            margin_vs_S0_pct_single=(s0m - met0) / s0m * 100.0,
            margin_vs_S0_pct_two_speed=(s0m - met1) / s0m * 100.0,
            margin_gain_pp=((s0m - met1) - (s0m - met0)) / s0m * 100.0)
    return dict(
        basis=("informative bracket, fuel per km held at the single-speed "
               "value; not the metric of record"),
        two_speed_ratios="24:1 low / 12:1 high",
        prior_art_motivation=(
            "every heavy truck in the Task 0 product sweep that deleted "
            "its AMT still fitted a multi-speed traction gearbox"),
        candidates=out)


# =====================================================================
#  Task 5 - S3-specific risks
# =====================================================================
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
    out["fixed_ratio_grade_hold"] = dict(
        sweep=sweep,
        constraint=("a fixed ratio must simultaneously (a) keep the engine "
                    "below its 2,100 rpm ceiling at 105 km/h and (b) put "
                    "enough torque at the contact patch to hold the grade "
                    "at a speed above its own lugging floor. Those two pull "
                    "in opposite directions and that is the whole of the S3 "
                    "design space."),
        max_ratio_without_overspeed=max(
            [r["ratio_A"] for r in sweep if r["cruise"]["ok"]], default=None),
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
ENGINE_HEAT_TO_COOLANT_FRAC = 0.42
"""Of the heat a heavy-duty diesel rejects (fuel power less brake power),
the share that leaves through the coolant and charge-air cooler rather
than the exhaust and surface radiation. [WS8-PROV] class-typical; the
split matters to WS6 because the two go to different places."""


def heat_ledger(seeds, ctx):
    """Rejected heat by COMPONENT and by CASE, per candidate.

    Three enumerated cases, chosen because they are the three that size
    different parts of the cooling system:
      cruise_95kmh_flat   what the radiator sees all day
      climb_6pct          the peak engine and machine heat case
      descent_6pct        the peak SINK case - where a series candidate
                          puts several hundred kW into a resistor
    R14: each component's worst case is an explicit max over this set
    with the governing case labelled.
    """
    cases = OrderedDict([
        ("cruise_95kmh_flat", dict(v=95 / 3.6, grade=0.0)),
        ("climb_6pct", dict(v=None, grade=0.06)),
        ("descent_6pct", dict(v=None, grade=-0.06)),
    ])
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
                v = PH.steady_speed_on_grade(
                    cand.envelope(20.0)[0] * 20.0 / 1e3, grade, m,
                    rho=ctx.rho_air)
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
                v = cand.v_cap(grade)
                v = min(v, 100.0 / 3.6)
            comp = component_heat_kw(cand, v, grade, m, ctx)
            comp["road_speed_kmh"] = v * 3.6
            rows[case] = comp
        comps = sorted({k for r in rows.values() for k in r
                        if k.endswith("_kW")})
        worst = {}
        for k in comps:
            vals = {c: rows[c].get(k, 0.0) for c in rows}
            gov = max(vals, key=lambda c: vals[c])
            worst[k] = dict(rule="max", cases=vals, value=vals[gov],
                            governing_case=gov)
        out[cname] = dict(cases=rows, worst_case=worst)
    return dict(
        convention=("component heat rejection [kW], bus-side electrical "
                    "quantities per R12; engine heat split "
                    f"{ENGINE_HEAT_TO_COOLANT_FRAC:.2f} coolant+CAC / "
                    f"{1-ENGINE_HEAT_TO_COOLANT_FRAC:.2f} exhaust+radiation"),
        cases=list(cases),
        for_workstream="WS6 heat ledger (CLAUDE.md rule 7)",
        candidates=out)


def component_heat_kw(cand, v, grade, m, ctx):
    """Heat rejected by each component at one (speed, grade) case."""
    f_res, _, _, _ = PH.road_load_force(np.array([v]), grade, m,
                                        rho=ctx.rho_air)
    p_wheel_kw = float(f_res[0]) * v / 1e3
    out = OrderedDict()
    out["case_wheel_power_kW"] = p_wheel_kw
    ed = getattr(cand, "edrive", None)
    pack = getattr(cand, "pack", None)
    line = getattr(cand, "line", None)

    if p_wheel_kw >= 0:      # driving
        if cand.name == "S0":
            amt = cand.amt
            gi, _ = amt.select_gear(v, float(f_res[0]))
            rpm = amt.engine_rpm(v, gi)
            p_shaft = p_wheel_kw / max(amt.eta(gi), 1e-6) \
                + ctx.aux_mech_kw
            trq = p_shaft * 1e3 / (rpm * 2 * np.pi / 60.0)
            trq = min(trq, float(cand.engine.t_max(rpm)))
            b = float(cand.engine.bsfc(rpm, trq))
            p_fuel = b * p_shaft / 3600.0 * LHV_KJ_PER_G
            q = max(p_fuel - p_shaft, 0.0)
            out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
            out["engine_exhaust_kW"] = q * (1 - ENGINE_HEAT_TO_COOLANT_FRAC)
            out["driveline_kW"] = p_shaft - p_wheel_kw
            out["traction_machine_inverter_kW"] = 0.0
            out["generator_rectifier_kW"] = 0.0
            out["pack_kW"] = 0.0
            out["brake_resistor_kW"] = 0.0
        else:
            eta = float(ed.eta_bus_to_wheel(v, p_wheel_kw)) if ed else 0.9
            p_bus = p_wheel_kw / max(eta, 1e-6) + ctx.aux_bus_kw
            out["traction_machine_inverter_kW"] = p_wheel_kw \
                / max(eta, 1e-6) - p_wheel_kw
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
            else:
                # S3: engine drives axle A mechanically
                rpm = float(np.clip(cand._rpm_at_v(v), 600.0, cand.RPM_MAX))
                f_a = min(float(f_res[0]), cand.f_axleA_max(v))
                p_a = f_a * v / 1e3 / max(cand.eta_A, 1e-6)
                trq = min(p_a * 1e3 / (rpm * 2 * np.pi / 60.0),
                          float(cand.engine.t_max(rpm)))
                if trq > 1e-6:
                    b = float(cand.engine.bsfc(rpm, trq))
                    p_fuel = b * p_a / 3600.0 * LHV_KJ_PER_G
                    q = max(p_fuel - p_a, 0.0)
                else:
                    q = 0.0
                out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
                out["engine_exhaust_kW"] = q * (1
                                                - ENGINE_HEAT_TO_COOLANT_FRAC)
                out["generator_rectifier_kW"] = 0.0
            out["driveline_kW"] = p_wheel_kw * (1.0 - DL.eta_axle_tandem)
            if pack is not None:
                out["pack_kW"] = abs(p_bus) * (1.0 - pack.eta_dis) * 0.5
            out["brake_resistor_kW"] = 0.0
    else:                    # descending: the SINK case
        need_kw = -p_wheel_kw
        _, f_rg, f_rx = cand.envelope(v)
        p_rg = min(need_kw, f_rg * v / 1e3)
        p_rx = min(max(need_kw - p_rg, 0.0), f_rx * v / 1e3)
        out["engine_coolant_kW"] = 0.0
        out["engine_exhaust_kW"] = 0.0
        out["generator_rectifier_kW"] = 0.0
        out["driveline_kW"] = 0.0
        if cand.name in ("S0",):
            out["engine_exhaust_kW"] = p_rx      # compression brake -> exhaust
            out["traction_machine_inverter_kW"] = 0.0
            out["pack_kW"] = 0.0
            out["brake_resistor_kW"] = 0.0
        else:
            eta = float(ed.eta_wheel_to_bus(v, p_rg + p_rx)) if ed else 0.9
            out["traction_machine_inverter_kW"] = (p_rg + p_rx) * (1.0 - eta)
            out["pack_kW"] = p_rg * eta * (1.0 - pack.eta_chg) \
                if pack is not None else 0.0
            resistor = p_rx * eta
            if cand.name in ("S2", "S3"):
                # engine brake carries part of the descent for these
                out["engine_exhaust_kW"] = max(0.0, resistor * 0.0)
            out["brake_resistor_kW"] = resistor
    for k in ("engine_coolant_kW", "engine_exhaust_kW", "driveline_kW",
              "traction_machine_inverter_kW", "generator_rectifier_kW",
              "pack_kW", "brake_resistor_kW"):
        out.setdefault(k, 0.0)
    out["total_rejected_kW"] = sum(
        out[k] for k in out if k.endswith("_kW")
        and k not in ("case_wheel_power_kW", "total_rejected_kW"))
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
        note=("2,533 N of aero and 1,959 N of rolling at 36.3 t is the "
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
def escalations(R):
    trial = R["task3_trial"]["nominal"]
    s4 = trial.get("S4", {}).get("spec", {})
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
            "charged against S4 in the metric of record."),
        why_not_self_resolved=(
            "Substituting a cell WS3 never characterised would be WS8 "
            "writing WS3's trade study, which rule 10 forbids and which "
            "would put an uncorroborated number into the headline."),
        asks=("Rule on ONE of: (a) S4's result stands on WS3's cell set as "
              "reported; (b) WS3 is reopened to characterise an "
              "energy-optimised cell and S4 is re-run; (c) WS8 is "
              "authorised to carry a cited external energy cell as an "
              "explicitly non-WS3 bracket."),
        materiality="high - it is the difference between S4 advancing or not"))

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
                " L/100 km, against the ICCT / TUV NORD figure of "
                f"{ICCT_TYPICAL_L_PER_100KM} L/100 km for a typical EU "
                f"tractor-trailer over the regulatory Long Haul cycle and "
                f"{ICCT_AT_REG_PAYLOAD_L_PER_100KM} L/100 km at that "
                "cycle's regulatory payload. That is a match to about one "
                "percent, reached with no fitting: the single calibration "
                "knob is solved against a declared BSFC island and nothing "
                "else is tuned.\n"
                "The excess is TERRAIN. Task 1 ordered a corridor carrying "
                "a 6% mountain and sustained 2-3% sections - about 3,800 m "
                "of climb over 520 km - and a 30-38 L/100 km band "
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
                  "fuel figure and none of the margins."),
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
            "necessity."),
        why_not_self_resolved=("Whether the ruler carries a retarder is a "
                              "baseline-specification decision."),
        asks=("Confirm S0's retarder specification, or direct a re-run with "
              "a hydraulic retarder on S0."),
        materiality="low - affects trip time and accessory energy, not "
                    "tractive work"))

    return sorted(esc, key=lambda e: e["id"])


# =====================================================================
#  R14 interface block + headline
# =====================================================================
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
        shares = [x["correction_share_of_fuel"]
                  for cy in blob["per_cycle"].values() for x in cy]
        uns = [x["unserved_kWh"]
               for cy in blob["per_cycle"].values() for x in cy]
        cands[cname] = dict(
            payload_kg=blob["spec"]["payload_kg"],
            powertrain_mass_kg=blob["spec"]["powertrain_mass_kg"],
            fuel_correction_share=dict(
                rule="max over the enumerated (cycle, seed) case set",
                value=max(shares), median=float(np.median(shares)),
                governing_case="worst (cycle, seed) at the nominal corner",
                meaning=("fraction of this candidate's reported fuel that "
                         "is a CORRECTION - unserved energy charged back "
                         "as fuel, plus the charge-sustaining make-up - "
                         "rather than fuel the model watched it burn. A "
                         "large share means the candidate could not "
                         "actually do the mission and was credited with "
                         "doing it anyway, which is a capability finding")),
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
def _w(path, header, rows):
    with open(os.path.join(DATA, path), "w") as f:
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
                        x["correction_share_of_fuel"]])
    _w("candidate_runs.csv",
       ["corner", "candidate", "cycle", "seed", "distance_km", "duration_s",
        "avg_speed_kmh", "power_limited_frac", "payload_kg", "gcw_kg",
        "fuel_g_raw", "fuel_g_corrected", "fuel_L_per_100km", "MJ_per_km",
        "MJ_per_payload_tkm", "unserved_kWh", "charge_deficit_kWh",
        "correction_share"], rows)

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
                rows.append([corner, cname, f["seed"], f["payload_t"],
                             f["L_per_100km"], f["MJ_per_km"],
                             f["MJ_per_payload_tkm"], mv])
    _w("fleet_mission.csv",
       ["corner", "candidate", "seed", "payload_t", "L_per_100km",
        "MJ_per_km", "MJ_per_payload_tkm", "margin_vs_S0_pct"], rows)

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
    rows = []
    for cname, blob in R["heat_ledger"]["candidates"].items():
        for case, comp in blob["cases"].items():
            rows.append([cname, case, comp["road_speed_kmh"],
                         comp["case_wheel_power_kW"],
                         comp["engine_coolant_kW"], comp["engine_exhaust_kW"],
                         comp["traction_machine_inverter_kW"],
                         comp["generator_rectifier_kW"], comp["pack_kW"],
                         comp["brake_resistor_kW"], comp["driveline_kW"],
                         comp["total_rejected_kW"]])
    _w("heat_ledger_ws6.csv",
       ["candidate", "case", "road_speed_kmh", "wheel_power_kW",
        "engine_coolant_kW", "engine_exhaust_kW", "machine_inverter_kW",
        "generator_rectifier_kW", "pack_kW", "brake_resistor_kW",
        "driveline_kW", "total_rejected_kW"], rows)

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
