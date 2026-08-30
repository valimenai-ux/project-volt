#!/usr/bin/env python3
"""
Project Volt - WS4 (genset + Gate G1). Single entry point.

    python3 run_ws4.py

Regenerates, deterministically (all stochastic inputs are WS1's seeded
cycle builders, 8-seed ensembles per R9):
  data/bsfc_map_*.csv, data/gen_eff_map_*.csv   - published maps
  figs/fig*_ws4.png                             - figures
  results_ws4.json                              - every number in the report
  run_output.txt                                - console summary

Reads WS1's code and parameters from ../WS1_loads_duty_cycles (read-only).
Nothing outside this folder is modified.
"""
import dataclasses
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import hashlib                                                   # noqa: E402

from ws4_models import (VEH, DL, AUX, CTL, G,                    # noqa: E402
                        derate_factor, R6_CORNER, R6_CORNER_REQUIRED_KW,
                        ENG_REF, ENG_V2, ENG_V1, GEN_V2, GEN_V1, PMGenerator,
                        MOTOR_RATED_KW, part_load_factor, LHV_KJ_PER_G,
                        engine_energy_split, USABLE_V2_KWH, USABLE_V1_KWH,
                        CHG_CONT_BUS_KW)
import ws4_sim as sim                                            # noqa: E402
from ws4_sim import (run_g1_mode, run_v1_startstop, pinned_point,  # noqa: E402
                     _bsfc_fast, wheel_power_trace, lockup_state)
from ws4_chain import load_ws2_exports, WS2TractionChain         # noqa: E402
import volt_cycles as vc                                         # noqa: E402
import volt_physics as vp                                        # noqa: E402

t0 = time.time()
os.makedirs("data", exist_ok=True)
os.makedirs("figs", exist_ok=True)
R = {"_meta": dict(
    workstream="WS4 genset + Gate G1",
    revision=("G1-R recompute per WS4_genset/G1R_DIRECTIVE.md (rulings "
              "R10/R11/R12/R18): gate margins re-derived under the R12 "
              "chain convention with WS2's measured maps and spin-drag "
              "member; non-gate sections carry the ratified r2 values. "
              "See REPORT_WS4.md changelog s0-R."),
    against="BASELINE_v2.md (ratified 2026-08-29)",
    reads=["../WS1_loads_duty_cycles/REPORT_WS1.md",
           "../WS1_loads_duty_cycles/results.json",
           "../WS2_traction_motor/results.json",
           "../WS2_traction_motor/data/cycle_loss_summary.csv",
           "../WS2_traction_motor/data/effmap_motor_inverter_*.csv"],
    conventions=("R9: 8-seed ensembles for stochastic extrema; part-load "
                 "maps/derates everywhere; heat by component and case. "
                 "BSFC maps are WS4-CONSTRUCTED Willans-line maps, "
                 "clearly labeled, not measured. R12: G1 traction chain "
                 "= WS2 measured maps x 0.97 reduction, no scalar PE "
                 "member; genset-side PE/rectifier in WS4's generator "
                 "model; all cross-WS electrical quantities bus-side."),
    fuel="diesel, LHV 42.8 MJ/kg, 832 g/L")}

REG_SEEDS = [23, 3, 4, 5, 6, 7, 8, 9]      # WS1 ensemble incl. reference 23
SUB_SEEDS = [11, 3, 4, 5, 6, 7, 8, 9]      # WS1 ensemble incl. reference 11


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# WS2 traction chain of record (R12) - hot-swappable per the G1-R directive:
# the loader picks the map keyed nearest WS2's own exported bus nominal, so
# when WS2 r4 lands (432/662/749 V maps on the R10 bus) a re-run consumes
# them with no code change. The vintage actually used is recorded here and
# in the interface block.
WS2X = load_ws2_exports()
CHAIN = WS2TractionChain(WS2X["map_path"], WS2X["ratio"], VEH.r_dyn)
SPIN_SH = WS2X["spin"]["rate_shaft_kW_while_locked"]
SPIN_BUS = WS2X["spin"]["rate_bus_kW_while_locked"]
_R4_LANDED = bool(abs(WS2X["ws2_bus_nominal_V"] - 662.4) < 1.0)
R["ws2_chain_of_record"] = dict(
    ruling="R12 + G1-R directive 1a/1b",
    map_file=WS2X["map_file_rel"], map_voltage_V=WS2X["map_voltage_V"],
    ws2_bus_nominal_V=WS2X["ws2_bus_nominal_V"],
    ws2_rework_round=WS2X["ws2_rework_round"],
    ws2_results_date=WS2X["ws2_results_date"],
    reduction_flat=0.97,
    vintage=("WS2 round-4 maps on the R10 662.4 V bus (chain of record)"
             if _R4_LANDED else
             "WS2 round-3 maps at the superseded 370 V bus - the r4 maps "
             "at 432/662/749 V had NOT landed when this run was made; the "
             "pipeline hot-swaps them on re-run (G1-R directive preamble)"),
    spin_drag_member=WS2X["spin"],
    eta_mot_avg_VOLT_REG=WS2X["eta_mot_avg_VOLT_REG"],
    eta_gen_avg_VOLT_REG=WS2X["eta_gen_avg_VOLT_REG"],
    map_feasible_points=CHAIN.n_feasible,
    # byte-level provenance of the consumed WS2 inputs (pre-adjudication
    # finding: the vintage claim should not rest on mtimes alone)
    input_sha256={
        "map_file": _sha256(WS2X["map_path"]),
        "results.json": _sha256(os.path.join(
            "..", "WS2_traction_motor", "results.json")),
        "cycle_loss_summary.csv": _sha256(os.path.join(
            "..", "WS2_traction_motor", "data", "cycle_loss_summary.csv"))})

# HISTORICAL RECORD (not regenerable): the interim G1-R nominal margins
# from the run made on WS2's round-3 exports (370 V map; same spin
# integrals) before WS2 r4 landed mid-round. The r4 exports replaced the
# 370 V map on disk, so that run cannot be reproduced from the current
# tree; recorded as a literal so the vintage statement is on the
# machine-readable record and verifiable in the report. Gate of record:
# gate_g1 (r4).
R["gate_g1_interim_r3_vintage_record"] = dict(
    _note=("historical, hand-recorded from the interim r3-vintage run of "
           "2026-08-30 (pre-r4-landing); unreproducible - WS2 r4 removed "
           "the 370 V exports. Not a verify target beyond rendering; the "
           "gate of record is gate_g1."),
    margin_pct_min=-2.9798310816318927,
    margin_pct_median=-2.876323333484512,
    margin_pct_max=-2.744412023685285)


def log(msg=""):
    print(msg)
    _LOG.append(str(msg))


_LOG = []

# ---------------------------------------------------------------------------
# 0. model self-checks
# ---------------------------------------------------------------------------
rr = np.linspace(750, 2950, 23)
tt = np.linspace(40, 700, 23)
err = 0.0
for N in rr:
    tm = float(ENG_V2.t_max(N))
    for T in tt:
        if T <= tm:
            err = max(err, abs(_bsfc_fast(ENG_V2, N, T, tm)
                               - float(ENG_V2.bsfc(N, T))))
assert err < 0.05, f"fast BSFC path diverges from map: {err}"

# WS1 regression: reproduce the 107.8 kW grade floor with baseline scalars
_v = 60 / 3.6
_f = vp.road_load_force(np.array([_v]), np.array([0.06]), VEH.m_gvw)[0][0]
_shaft = (_f * _v / DL.eta_bus_to_wheel + AUX.p_aux_nom) / DL.eta_gen
R["sanity_ws1_regression"] = dict(
    grade_floor_engine_shaft_kW=_shaft / 1e3,
    ws1_value_kW=107.8077950219109,
    match=bool(abs(_shaft / 1e3 - 107.8077950219109) < 0.01))
assert R["sanity_ws1_regression"]["match"]

# ---------------------------------------------------------------------------
# 1. candidates and the R6 corner derate math
# ---------------------------------------------------------------------------
DER = derate_factor(**R6_CORNER)


def corner_row(name, disp_l, rated_kw, cont_kw, mass_kg, note):
    corner = cont_kw * DER
    return dict(name=name, displacement_l=disp_l,
                rated_peak_kW=rated_kw, continuous_shaft_kW_SL=cont_kw,
                derate_factor_R6_corner=DER,
                corner_delivered_kW=corner,
                corner_required_kW=R6_CORNER_REQUIRED_KW,
                corner_margin_kW=corner - R6_CORNER_REQUIRED_KW,
                meets_R6_corner=bool(corner >= R6_CORNER_REQUIRED_KW),
                dry_mass_kg=mass_kg, note=note)


R["derate_model"] = dict(
    basis=("WS4-DECLARED, class-typical ISO 3046 / SAE J1349 practice for "
           "turbocharged charge-air-cooled diesels; confirm against the "
           "procured candidate datasheet"),
    altitude="none to 1,000 m, then 4% per 1,000 m",
    temperature="none to 30 C, then 1% per 5 C",
    r6_corner=R6_CORNER,
    factor_at_r6_corner=DER,
    consequence=("a '125 kW continuous' engine delivers "
                 f"{125.0 * DER:.1f} kW at the corner - the R6 corner "
                 "requirement, not the 125 kW label, must size the engine"))

R["candidates_v2"] = [
    corner_row("4HK1-TC stock reference", 5.193, 153.0, 130.0, 500.0,
               "donor's own engine, baseline reference curve (700 Nm @ "
               "1,600); continuous 130 kW is a class-typical 85% prime "
               "rating of the 153 kW automotive peak"),
    corner_row("4HK1-V2C (SELECTED): 4HK1-TC genset recalibration", 5.193,
               153.0, 132.0, 500.0,
               "same production hardware, torque peak moved to 750 Nm @ "
               "1,400 rpm (the E3-compliant curve WS1 tested in s4.5), "
               "continuous 132 kW @ 2,200 rpm"),
    corner_row("Cummins B4.5-class (downsized-from-stock)", 4.5, 168.0,
               129.0, 390.0,
               "4.5 L production engine, auxiliary/continuous format tops "
               "out ~129 kWm; 110 kg lighter than the 4HK1"),
    corner_row("Isuzu 4JJ1-class 3.0 L (examined)", 3.0, 130.0, 110.0,
               350.0, "cannot reach the 125 kW continuous floor at all"),
]
R["candidates_v1"] = [
    corner_row("V3307-V1C (SELECTED): Kubota V3307-CR-T class", 3.331,
               55.4, 50.0, 305.0,
               "production Tier 4F/Stage V industrial engine, 55.4 kW @ "
               "2,600, 265 Nm @ 1,500; lands inside R5's 50-60 kW window"),
    corner_row("Hatz 4H50TIC class", 1.981, 55.8, 49.0, 173.0,
               "132 kg lighter but 2,800 rpm rated speed and thinner "
               "service network; kept as mass-critical fallback"),
    corner_row("Isuzu 4LE2T class", 2.179, 48.0, 44.0, 245.0,
               "below the 50 kW class at continuous rating"),
]

# ---------------------------------------------------------------------------
# 2. BSFC + generator maps (published artefacts)
# ---------------------------------------------------------------------------
MAPS = {}
for eng, fn in ((ENG_REF, "data/bsfc_map_4HK1_ref.csv"),
                (ENG_V2, "data/bsfc_map_V2_candidate.csv"),
                (ENG_V1, "data/bsfc_map_V1_candidate.csv")):
    eng.export_map_csv(fn)
    mp = eng.min_bsfc_point()
    mpc = eng.min_bsfc_point(p_cap_kw=eng.rated_cont_kw)
    MAPS[eng.name] = dict(file=fn, label=eng.label,
                          map_min=mp, map_min_within_continuous=mpc,
                          peak_power_kW=eng.peak_power_kw(),
                          bsfc_at_rated_continuous=float(eng.bsfc(
                              eng.rated_cont_rpm,
                              eng.rated_cont_kw * 1e3 /
                              (eng.rated_cont_rpm * 2 * np.pi / 60))))
R["bsfc_maps"] = MAPS
GEN_V2.export_map_csv("data/gen_eff_map_V2.csv")
GEN_V1.export_map_csv("data/gen_eff_map_V1.csv")

# G1-R directive 1c: the generator/rectifier spec is restated on the R10
# pack-native window (662.4 V nominal). The machine winding (kV) and the
# rectifier DC side follow the window; the rectifier devices move from the
# 750 V class (370 V bus) to the 1200 V class (749/778 V ceilings) - same
# direction WS2 r4 takes for the traction inverter.
R10_DC_WINDOW = dict(
    ruling="R10 (BASELINE_v2)",
    bus_class="650 V class, pack-native",
    nominal_V=662.4, operating_V=[432.0, 748.8],
    charge_transient_10s_V=777.6, granularity="12 cells (27.6 V)",
    rectifier_device_class=("1200 V SiC (was 750 V class at the "
                            "superseded 370 V bus)"),
    loss_model_at_new_window=(
        "WS4-DECLARED: the exported loss model (iron+windage prop. to "
        "speed, copper prop. to T^2, rectifier 1% of P_elec + fixed) is "
        "carried unchanged at the new window - at this fidelity the "
        "voltage change trades conduction current for switching stress "
        "roughly evenly across a rewound machine + 1200 V SiC stage; "
        "confirm coefficients at procurement"))


def _gen_block(gen, eng, type_str, map_file):
    pin = pinned_point(eng, gen, 1.0)
    return dict(name=gen.name, type=type_str,
                cont_kW_shaft_in=gen.cont_kw_in,
                peak_kW_shaft_in=gen.peak_kw_in,
                mass_kg=gen.mass_kg, map_file=map_file,
                eta_at_pinned_point=float(gen.eta(pin["rpm"],
                                                  pin["p_shaft_kw"])),
                spin_loss_at_1800rpm_kW=float(gen.fe_kw(1800.0)),
                dc_output_window=R10_DC_WINDOW)


R["generators"] = {
    "V2": _gen_block(GEN_V2, ENG_V2,
                     "crank-mounted IPM PM synchronous + active SiC "
                     "rectifier (1200 V-class devices, R10 window), "
                     "liquid-cooled", "data/gen_eff_map_V2.csv"),
    "V1": _gen_block(GEN_V1, ENG_V1,
                     "genset-mounted IPM PM synchronous + active SiC "
                     "rectifier (1200 V-class devices, R10 window), "
                     "liquid-cooled", "data/gen_eff_map_V1.csv"),
}

# 1c: pinned points re-placed on the restated spec. The restatement moves
# no loss-model coefficient, so the re-derived points must land on the
# ratified coordinates - computed, not assumed:
_pin_check = {}
for _tag, _eng, _gen, _ref_rpm, _ref_kw in (
        ("V2", ENG_V2, GEN_V2, 1287.96992481203, 84.69969589648574),
        ("V1", ENG_V1, GEN_V1, 1300.501253132832, 29.5118746401605)):
    _p = pinned_point(_eng, _gen, 1.0)
    _pin_check[_tag] = dict(
        rpm=_p["rpm"], p_shaft_kw=_p["p_shaft_kw"],
        moved_by_rectifier_restatement=bool(
            abs(_p["rpm"] - _ref_rpm) > 1e-6
            or abs(_p["p_shaft_kw"] - _ref_kw) > 1e-6))
    assert not _pin_check[_tag]["moved_by_rectifier_restatement"], \
        f"pinned point {_tag} moved unexpectedly under the R10 restatement"
R["generator_rectifier_r10_restatement"] = dict(
    **R10_DC_WINDOW, pinned_points_replaced=_pin_check,
    note=("directive 1c: spec restated on the R10 window; pinned points "
          "re-placed and verified unmoved (the rectifier stage carries "
          "the same declared loss coefficients at the new voltage)"))

# ---------------------------------------------------------------------------
# 3. direct-path grade capability of the candidate curve (E3 closure data)
# ---------------------------------------------------------------------------


def direct_capability(engine, grade, aux_w=2000.0, m=VEH.m_gvw, veh=VEH,
                      derate=1.0):
    """Speed band on `grade` the locked path holds alone (aux carried
    through the generator off the same crank; WS4 direct-path loss
    model)."""
    vs = np.linspace(35.5, 110.0, 400) / 3.6
    ok = []
    for v in vs:
        rpm = v / veh.r_dyn * veh.fd_ratio * 60 / (2 * np.pi)
        if rpm < engine.idle_rpm:
            ok.append(False)
            continue
        p_max = float(engine.t_max(rpm)) * derate * rpm * 2 * np.pi / 60 / 1e3
        p_gen = float(GEN_V2.shaft_from_elec(rpm, aux_w / 1e3))
        p_avail_wheel = max(0.0, (p_max - p_gen) * 0.972
                            - 0.9 * rpm / 1800.0)
        need = float(vp.road_load_force(np.array([v]), np.array([grade]),
                                        m, veh)[0][0]) * v / 1e3
        ok.append(p_avail_wheel >= need)
    ok = np.array(ok)
    if not ok.any():
        return None
    return [float(vs[ok][0] * 3.6), float(vs[ok][-1] * 3.6)]


def max_direct_grade(engine, **kw):
    lo, hi = 0.0, 0.12
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if direct_capability(engine, mid, **kw) is not None:
            lo = mid
        else:
            hi = mid
    return lo


R["direct_path_6pct"] = {
    "reference_curve_band_at_6pct_kmh": direct_capability(ENG_REF, 0.06),
    "candidate_band_at_6pct_kmh": direct_capability(ENG_V2, 0.06),
    "candidate_max_grade_pct": 100 * max_direct_grade(ENG_V2),
    "reference_max_grade_pct": 100 * max_direct_grade(ENG_REF),
    "candidate_band_at_6pct_20pct_payload_kmh": direct_capability(
        ENG_V2, 0.06, m=7180.0),
    "candidate_band_at_6pct_CdA5.4_kmh": direct_capability(
        ENG_V2, 0.06, veh=dataclasses.replace(VEH, CdA=5.4)),
    "note": ("WS1 s4.5 found 59-67 km/h for this torque curve with the "
             "0.95 scalar; WS4's load-dependent direct-path loss model "
             "narrows it slightly. E3's requirement is hereby made a "
             "candidate spec: >= 750 Nm at 1,400 rpm.")}


# ---------------------------------------------------------------------------
# 4. series grade-hold speed with the candidate (velocity solve)
# ---------------------------------------------------------------------------


def series_hold_speed(engine_cont_kw, gen, grade=0.06, aux_kw=2.0,
                      m=VEH.m_gvw, veh=VEH, derate=1.0):
    """Sustained speed in series with the engine at its continuous rating,
    generator map conversion, part-load chain, buffer flat."""
    p_shaft = engine_cont_kw * derate
    loc = ENG_V2.opt_locus()
    okm = np.isfinite(loc["bsfc"])
    rpm = float(np.interp(p_shaft, loc["p_kw"][okm], loc["rpm"][okm]))
    p_bus = float(gen.elec_from_shaft(rpm, p_shaft)) - aux_kw

    def wheel_avail(pw_guess):
        k = float(part_load_factor(pw_guess / MOTOR_RATED_KW))
        return p_bus * DL.eta_bus_to_wheel * k

    vs = np.linspace(5, 130, 2000) / 3.6
    need = np.array([float(vp.road_load_force(
        np.array([v]), np.array([grade]), m, veh)[0][0]) * v / 1e3
        for v in vs])
    pw = p_bus * DL.eta_bus_to_wheel
    for _ in range(4):
        pw = wheel_avail(pw)
    idx = np.where(need <= pw)[0]
    return float(vs[idx[-1]] * 3.6) if idx.size else 0.0, rpm, p_bus + aux_kw


hold_nom, hold_rpm, hold_bus = series_hold_speed(132.0, GEN_V2)
hold_corner, _, _ = series_hold_speed(132.0, GEN_V2, m=7180.0,
                                      veh=dataclasses.replace(
                                          VEH, CdA=5.4, rho_air=0.8706),
                                      aux_kw=4.0, derate=DER)
R["series_grade_hold_candidate"] = dict(
    engine_shaft_kW=132.0,
    hold_speed_6pct_GVW_CdA42_aux2_kmh=hold_nom,
    genset_rpm=hold_rpm, genset_bus_kW=hold_bus,
    hold_speed_6pct_corner_20pct_payload_CdA54_aux4_2000m45C_kmh=hold_corner,
    ws1_110kW_reference_kmh=61.0)

# ---------------------------------------------------------------------------
# 5. GATE G1
# ---------------------------------------------------------------------------
log("building VOLT-REG ensemble ...")
REG = {sd: vc.build_cycle_B(seed=sd) for sd in REG_SEEDS}
log(f"  built {len(REG)} cycles")


def g1_config(tag, engine, veh=VEH, aux=2.0, derate=1.0, modes=("a", "b"),
              chain=None, spin=(0.0, 0.0), convention=None, gen=GEN_V2):
    """One G1 configuration over the 8-seed ensemble.

    chain/spin: G1-R controls (see run_g1_mode). chain=None + spin=(0,0)
    + gen=GEN_V2 reproduces the ratified r2 (BASELINE_v1 scalar-chain)
    configuration exactly (float-identical legacy path) - used for the
    regression anchor and the one-factor attribution rows (directive
    item 3). gen: the genset-conditioning bracket swaps in stressed
    generator variants."""
    rows = {}
    for sd in REG_SEEDS:
        rows[sd] = {}
        for md in modes:
            rows[sd][md] = run_g1_mode(REG[sd], md, engine, gen,
                                       USABLE_V2_KWH, p_aux_kw=aux,
                                       veh=veh, derate=derate, chain=chain,
                                       spin_shaft_kw=spin[0],
                                       spin_bus_kw=spin[1])
        log(f"  [{tag}] seed {sd}: " + ", ".join(
            f"{md}={rows[sd][md]['fuel_corrected_g']/1e3:.2f}kg"
            for md in modes))
    out = dict(per_seed={}, ensemble={})
    if convention is not None:
        out["_convention"] = convention
    for sd in REG_SEEDS:
        e = rows[sd]
        rec = {md: dict(fuel_kg=e[md]["fuel_corrected_g"] / 1e3,
                        fuel_energy_kWh=e[md]["fuel_energy_kwh"],
                        l_per_100km=e[md]["l_per_100km"],
                        starts=e[md]["starts"],
                        soc_drift_kWh=e[md]["soc_drift_kwh_cells"],
                        eng_on_frac=e[md]["eng_on_s"] / e[md]["duration_s"],
                        locked_frac=e[md]["locked_s"] / e[md]["duration_s"],
                        mean_bsfc_eff=e[md]["mean_bsfc_eff_g_per_kwh"],
                        fric_kWh=e[md]["e_fric_kwh"],
                        bank_kWh=e[md]["bank_kwh"],
                        over_rating_s=e[md]["over_rating_s"],
                        emerg_s=e[md]["emerg_s"],
                        unserved_kWh=e[md]["unserved_kwh"],
                        spin_shaft_kWh=e[md]["e_spin_shaft_kwh"],
                        spin_bus_kWh=e[md]["e_spin_bus_kwh"])
               for md in modes}
        for md in modes:
            lim = 0.3 if tag == "nominal" else 2.0
            assert e[md]["unserved_kwh"] < lim, \
                f"{tag}/{sd}/{md}: unserved bus energy " \
                f"{e[md]['unserved_kwh']:.2f} kWh - cycle not followed"
        if "a" in modes and "b" in modes:
            rec["margin_pct"] = 100 * (e["b"]["fuel_corrected_g"]
                                       - e["a"]["fuel_corrected_g"]) \
                / e["b"]["fuel_corrected_g"]
        out["per_seed"][str(sd)] = rec
    if "a" in modes and "b" in modes:
        m = [out["per_seed"][str(sd)]["margin_pct"] for sd in REG_SEEDS]
        def _mm(md, key):
            vals = [rows[sd][md][key] for sd in REG_SEEDS]
            return min(vals), max(vals)
        out["ensemble"] = dict(
            margin_pct_min=min(m), margin_pct_median=float(np.median(m)),
            margin_pct_max=max(m),
            # R14: the governing case of the exported worst-case field,
            # labeled inline
            margin_pct_min_governing_case=(
                f"seed {REG_SEEDS[int(np.argmin(m))]} of 8-seed VOLT-REG "
                f"ensemble [{tag}]"),
            fuel_a_kg=[out["per_seed"][str(sd)]["a"]["fuel_kg"]
                       for sd in REG_SEEDS],
            fuel_b_kg=[out["per_seed"][str(sd)]["b"]["fuel_kg"]
                       for sd in REG_SEEDS],
            kill_criterion_pct=5.0,
            passes_kill_criterion=bool(min(m) >= 5.0),
            # 8-seed envelopes of the secondary quantities the report and
            # escalations quote (added in rework r2 so verify_ws4.py can
            # cover them - adjudication r1 F1/F3)
            b_emerg_s_min=_mm("b", "emerg_s")[0],
            b_emerg_s_max=_mm("b", "emerg_s")[1],
            b_unserved_kwh_min=_mm("b", "unserved_kwh")[0],
            b_unserved_kwh_max=_mm("b", "unserved_kwh")[1],
            b_over_rating_s_min=_mm("b", "over_rating_s")[0],
            b_over_rating_s_max=_mm("b", "over_rating_s")[1],
            a_over_rating_s_max=_mm("a", "over_rating_s")[1],
            a_bank_kwh_min=_mm("a", "bank_kwh")[0],
            a_bank_kwh_max=_mm("a", "bank_kwh")[1],
            a_starts_min=_mm("a", "starts")[0],
            a_starts_max=_mm("a", "starts")[1],
            # G1-R 1b: spin-drag energy actually charged to mode (a),
            # per-seed envelope (scales with each seed's locked time)
            a_spin_shaft_kwh_min=_mm("a", "e_spin_shaft_kwh")[0],
            a_spin_shaft_kwh_max=_mm("a", "e_spin_shaft_kwh")[1],
            a_spin_bus_kwh_min=_mm("a", "e_spin_bus_kwh")[0],
            a_spin_bus_kwh_max=_mm("a", "e_spin_bus_kwh")[1])
    out["_raw_reference_seed"] = {md: {k: v for k, v in rows[23][md].items()
                                       if k != "pinned"}
                                  for md in modes} if 23 in REG_SEEDS else {}
    out["pinned_point"] = rows[REG_SEEDS[0]][modes[0]]["pinned"]
    return out


# --- G1-R (directive): every gate configuration runs under the ruled
# convention: R12 chain (WS2 maps x 0.97, both modes) + spin-drag member
# charged to (a). The prior-convention nominal is kept as a regression
# anchor (must reproduce the ratified r2 numbers bit-identically) and as
# the baseline for the two one-factor attribution rows (directive item 3).
G1R = dict(chain=CHAIN, spin=(SPIN_SH, SPIN_BUS),
           convention=("G1-R (R12): traction = WS2 measured map "
                       f"[{WS2X['map_file_rel']}, {WS2X['map_voltage_V']:.0f}"
                       " V] x 0.97 reduction, no scalar PE member, no "
                       "part_load_factor; PM spin drag charged to (a) "
                       f"locked samples at {SPIN_SH:.4f} kW shaft + "
                       f"{SPIN_BUS:.4f} kW bus (WS2 export)"))
PRIOR = dict(chain=None, spin=(0.0, 0.0),
             convention=("prior convention (ratified r2 / BASELINE_v1): "
                         "WS1 scalar chain 0.8656 x part_load_factor, no "
                         "spin member - regression anchor + one-factor "
                         "baseline, NOT the gate of record"))

log("G1-R regression anchor: prior convention, nominal ...")
G1_PRIOR = g1_config("prior-nominal", ENG_V2, **PRIOR)
_pe = G1_PRIOR["ensemble"]
assert abs(_pe["margin_pct_min"] - 6.261345943773722) < 1e-9 \
    and abs(_pe["margin_pct_median"] - 6.445177253781505) < 1e-9 \
    and abs(_pe["margin_pct_max"] - 6.78407493099628) < 1e-9, \
    "prior-convention anchor no longer reproduces the ratified r2 " \
    "margins - the G1-R refactor changed the legacy path"

log("G1-R nominal (a, b, bp) ...")
G1 = {"nominal": g1_config("nominal", ENG_V2, modes=("a", "b", "bp"),
                           **G1R)}
log("G1-R sensitivity: CdA 5.4 ...")
G1["cda_5.4"] = g1_config("cda5.4", ENG_V2,
                          veh=dataclasses.replace(VEH, CdA=5.4), **G1R)
log("G1-R sensitivity: aux 4 kW ...")
G1["aux_4kW"] = g1_config("aux4", ENG_V2, aux=4.0, **G1R)
log("G1-R sensitivity: hot day +45 C, sea level ...")
# standalone hot-day case (adjudication r1 F4): sea-level pressure at
# 45 C -> rho = 101325/(287*318.15) = 1.1097 kg/m^3; derate 0.97
G1["hot_45C_sea_level"] = g1_config(
    "hot45", ENG_V2, veh=dataclasses.replace(VEH, rho_air=1.1097),
    derate=derate_factor(0.0, 45.0), **G1R)
log("G1-R sensitivity: 2,000 m / +45 C ...")
G1["alt2000m_45C"] = g1_config(
    "alt", ENG_V2, veh=dataclasses.replace(VEH, rho_air=0.8706), derate=DER,
    **G1R)
log("G1-R sensitivity: reference 4HK1 torque curve ...")
G1["reference_curve"] = g1_config("refcurve", ENG_REF, **G1R)

# --- one-factor attribution rows (directive item 3): each correction
# alone, at nominal, vs the prior-convention anchor - so the record shows
# which correction moved the margin.
log("G1-R one-factor: spin drag alone (scalar chain) ...")
G1_SPIN = g1_config("spin-only", ENG_V2, chain=None,
                    spin=(SPIN_SH, SPIN_BUS),
                    convention="one-factor: spin-drag member alone on the "
                               "prior scalar chain")
log("G1-R one-factor: map-vs-scalar swap alone (no spin) ...")
G1_MAPS = g1_config("maps-only", ENG_V2, chain=CHAIN, spin=(0.0, 0.0),
                    convention="one-factor: R12 map-vs-scalar swap alone, "
                               "no spin member")


def _mrg(cfg):
    e = cfg["ensemble"]
    return dict(min=e["margin_pct_min"], median=e["margin_pct_median"],
                max=e["margin_pct_max"])


# --- genset-conditioning bracket (pre-adjudication adversarial finding):
# the SIGN of the G1-R margin is sensitive to the WS4-DECLARED (not
# measured) rectifier/conditioning member (pe0 0.15 kW + 1% of P_elec).
# Two hostile readings of R12's "genset-side PE/rectifier in WS4's
# ledger" bound it: REPLACEMENT treats the member as a 3%-class stage
# (pe0 dropped); STACKED adds WS1's full 3%-class stage on top of the
# declared member (~4% total conditioning). The pinned point re-derives
# inside each config, so mode (b) pays the stressed conversion too.
GEN_V2_R3PCT = PMGenerator("GEN-V2 IPM 135 [bracket: 3%-class conditioning]",
                           cont_kw_in=135.0, peak_kw_in=155.0,
                           c_h=0.5, c_e=0.7, k_cu=0.0612,
                           pe0=0.0, pe_frac=0.03, mass_kg=90.0)
GEN_V2_STACK = PMGenerator("GEN-V2 IPM 135 [bracket: declared + 3% stacked]",
                           cont_kw_in=135.0, peak_kw_in=155.0,
                           c_h=0.5, c_e=0.7, k_cu=0.0612,
                           pe0=0.15, pe_frac=0.04, mass_kg=90.0)
log("G1-R genset-conditioning bracket: 3%-class replacement ...")
G1_RECT_REPL = g1_config("rect-repl", ENG_V2, gen=GEN_V2_R3PCT, chain=CHAIN,
                         spin=(SPIN_SH, SPIN_BUS),
                         convention="bracket: rectifier member replaced by "
                                    "a 3%-class conditioning stage")
log("G1-R genset-conditioning bracket: declared + 3% stacked ...")
G1_RECT_STACK = g1_config("rect-stack", ENG_V2, gen=GEN_V2_STACK,
                          chain=CHAIN, spin=(SPIN_SH, SPIN_BUS),
                          convention="bracket: WS1's 3%-class stage stacked "
                                     "on the declared member (most hostile)")

# --- map-vintage robustness (supports the directive's vintage statement):
# the gate above runs on the single map keyed at WS2's exported nominal
# bus voltage. Re-running the nominal gate on WS2's other two exported
# voltage maps bounds how sensitive the verdict is to which map the
# chain uses (the sim does not resolve bus-voltage excursion within a
# cycle; this bracket bounds what that could be worth).
R["gate_g1_map_vintage_check"] = {}
for _vk, _rel in sorted(
        (float(k), rel) for k, rel in
        __import__("json").load(open(os.path.join(
            "..", "WS2_traction_motor", "results.json")))
        ["interface"]["efficiency_maps"].items()
        if k.replace(".", "").isdigit()):
    if abs(_vk - WS2X["map_voltage_V"]) < 0.5:
        continue
    log(f"G1-R map-vintage robustness: {_vk:.0f} V map ...")
    _alt_chain = WS2TractionChain(
        os.path.normpath(os.path.join("..", "WS2_traction_motor", _rel)),
        WS2X["ratio"], VEH.r_dyn)
    _alt = g1_config(f"vmap{_vk:.0f}", ENG_V2, chain=_alt_chain,
                     spin=(SPIN_SH, SPIN_BUS),
                     convention=f"robustness: alternate exported "
                                f"{_vk:.0f} V map, spin member on")
    R["gate_g1_map_vintage_check"][f"{_vk:.0f}V"] = _mrg(_alt)

R["gate_g1_genset_conditioning_bracket"] = dict(
    _note=("pre-adjudication adversarial finding: the G1-R SIGN rests on "
           "the WS4-DECLARED rectifier/conditioning member (pe0 0.15 kW + "
           "1% of P_elec, TBC at procurement). Bracketed here by two "
           "hostile readings of R12; the KILL-CRITERION outcome is "
           "invariant - even the most hostile stacked reading leaves the "
           "nominal ensemble-min far below the +5% criterion."),
    declared_member=_mrg(G1["nominal"]),
    replacement_3pct_class=_mrg(G1_RECT_REPL),
    stacked_declared_plus_3pct=_mrg(G1_RECT_STACK))


R["gate_g1_prior_convention"] = G1_PRIOR
R["gate_g1_one_factor"] = dict(
    _note=("directive item 3: one-factor rows at nominal. delta = "
           "row margin minus prior-convention margin, in percentage "
           "points; the two deltas plus their interaction close to the "
           "full G1-R shift"),
    prior_convention=_mrg(G1_PRIOR),
    spin_drag_alone=dict(
        **_mrg(G1_SPIN),
        delta_pp_min=G1_SPIN["ensemble"]["margin_pct_min"]
        - G1_PRIOR["ensemble"]["margin_pct_min"],
        delta_pp_median=G1_SPIN["ensemble"]["margin_pct_median"]
        - G1_PRIOR["ensemble"]["margin_pct_median"]),
    map_vs_scalar_alone=dict(
        **_mrg(G1_MAPS),
        delta_pp_min=G1_MAPS["ensemble"]["margin_pct_min"]
        - G1_PRIOR["ensemble"]["margin_pct_min"],
        delta_pp_median=G1_MAPS["ensemble"]["margin_pct_median"]
        - G1_PRIOR["ensemble"]["margin_pct_median"]),
    both_g1r=dict(
        min=None, median=None))   # filled below once G1 nominal is final
R["gate_g1_one_factor"]["both_g1r"] = dict(
    **_mrg(G1["nominal"]),
    delta_pp_min=G1["nominal"]["ensemble"]["margin_pct_min"]
    - G1_PRIOR["ensemble"]["margin_pct_min"],
    delta_pp_median=G1["nominal"]["ensemble"]["margin_pct_median"]
    - G1_PRIOR["ensemble"]["margin_pct_median"])

# bp comparison (nominal only): pure-series-done-well vs pinned
bp_fuel = [G1["nominal"]["per_seed"][str(sd)]["bp"]["fuel_kg"]
           for sd in REG_SEEDS]
b_fuel = [G1["nominal"]["per_seed"][str(sd)]["b"]["fuel_kg"]
          for sd in REG_SEEDS]
a_fuel = [G1["nominal"]["per_seed"][str(sd)]["a"]["fuel_kg"]
          for sd in REG_SEEDS]
G1["bp_vs_b_pct"] = dict(
    note=("bp = series load-following on the best-BSFC locus, the honest "
          "V1-with-125kW-genset; NOT the G1 metric"),
    margin_a_vs_bp_pct=[100 * (bp - a) / bp for bp, a in zip(bp_fuel, a_fuel)],
    margin_b_vs_bp_pct=[100 * (bp - b) / bp for bp, b in zip(bp_fuel, b_fuel)])
R["gate_g1"] = G1

# ---------------------------------------------------------------------------
# 6. V1 start-stop (VOLT-SUB)
# ---------------------------------------------------------------------------
log("building VOLT-SUB ensemble ...")
SUB = {sd: vc.build_cycle_A(seed=sd) for sd in SUB_SEEDS}

SS = {"fixed_point": pinned_point(ENG_V1, GEN_V1, 1.0),
      "map_min": ENG_V1.min_bsfc_point()}
log("V1 start-stop sweeps ...")
SS["hysteresis_sweep_ref_seed"] = {}
for hyst in (0.5, 0.8, 1.1):
    SS["hysteresis_sweep_ref_seed"][f"{hyst:.1f}kWh"] = run_v1_startstop(
        SUB[11], ENG_V1, GEN_V1, USABLE_V1_KWH, hyst)
SS["usable_3.0_hyst_1.6"] = run_v1_startstop(SUB[11], ENG_V1, GEN_V1,
                                             3.0, 1.6)
ens = [run_v1_startstop(SUB[sd], ENG_V1, GEN_V1, USABLE_V1_KWH, 0.8)
       for sd in SUB_SEEDS]
SS["ensemble_hyst_0.8kWh"] = dict(
    starts_per_8h_shift=[e["starts_per_8h_shift"] for e in ens],
    starts_per_8h_min=min(e["starts_per_8h_shift"] for e in ens),
    starts_per_8h_max=max(e["starts_per_8h_shift"] for e in ens),
    fuel_l_per_h=[e["fuel_l_per_h"] for e in ens],
    fuel_l_per_h_min=min(e["fuel_l_per_h"] for e in ens),
    fuel_l_per_h_max=max(e["fuel_l_per_h"] for e in ens))
SS["continuous_ref_seed"] = run_v1_startstop(SUB[11], ENG_V1, GEN_V1,
                                             USABLE_V1_KWH, 0.8,
                                             strategy="continuous")
SS["cold_regen0_aux4_ref_seed"] = run_v1_startstop(
    SUB[11], ENG_V1, GEN_V1, USABLE_V1_KWH, 0.8, p_aux_kw=4.0,
    regen_cap_kw=0.0)
SS["aux4_ref_seed"] = run_v1_startstop(SUB[11], ENG_V1, GEN_V1,
                                       USABLE_V1_KWH, 0.8, p_aux_kw=4.0)
ss_ref = SS["hysteresis_sweep_ref_seed"]["0.8kWh"]
SS["fuel_saving_vs_continuous_pct"] = 100 * (
    SS["continuous_ref_seed"]["fuel_l_per_h"] - ss_ref["fuel_l_per_h"]) \
    / SS["continuous_ref_seed"]["fuel_l_per_h"]
R["v1_start_stop"] = SS

# V1 charge-sustaining top speed with the candidate + maps


def v1_top_speed(p_shaft_kw, aux_kw=2.0):
    """Charge-sustaining top speed with the V1 engine at `p_shaft_kw` on
    its best-BSFC locus, generator map, part-load chain."""
    locv = ENG_V1.opt_locus()
    okv = np.isfinite(locv["bsfc"])
    rpm = float(np.interp(p_shaft_kw, locv["p_kw"][okv], locv["rpm"][okv]))
    p_bus = float(GEN_V1.elec_from_shaft(rpm, p_shaft_kw)) - aux_kw
    pw = p_bus * DL.eta_bus_to_wheel
    for _ in range(4):
        pw = p_bus * DL.eta_bus_to_wheel * float(
            part_load_factor(pw / MOTOR_RATED_KW))
    vs = np.linspace(5, 130, 2000) / 3.6
    need = 0.5 * VEH.rho_air * VEH.CdA * vs ** 3 \
        + VEH.Crr * VEH.m_gvw * G * vs
    idx = np.where(need / 1e3 <= pw)[0]
    return float(vs[idx[-1]] * 3.6)


R["v1_capability"] = dict(
    charge_sustaining_top_speed_at_50kW_cont_kmh=v1_top_speed(50.0),
    charge_sustaining_top_speed_at_pinned_point_kmh=v1_top_speed(
        pinned_point(ENG_V1, GEN_V1, 1.0)["p_shaft_kw"]),
    ws1_scalar_chain_value_kmh=78.6,
    note=("50 kW continuous with the generator map and part-load chain; "
          "R5 sub-80 km/h ruling stands - capability, not a dispatch "
          "case. The part-load chain derate costs ~2 km/h vs WS1's "
          "peak-point scalars."))

# ---------------------------------------------------------------------------
# 7. heat ledger (WS6), by component and case
# ---------------------------------------------------------------------------
pinV2 = pinned_point(ENG_V2, GEN_V2, 1.0)
pinV1 = pinned_point(ENG_V1, GEN_V1, 1.0)

# case: V2 grade hold, series, engine 110 kW shaft (WS1 ledger case)
loc = ENG_V2.opt_locus()
okm = np.isfinite(loc["bsfc"])
rpm110 = float(np.interp(110.0, loc["p_kw"][okm], loc["rpm"][okm]))
trq110 = float(np.interp(110.0, loc["p_kw"][okm], loc["trq"][okm]))
b110 = float(ENG_V2.bsfc(rpm110, trq110))
split110 = engine_energy_split(110.0, b110)
gen110_loss = 110.0 - float(GEN_V2.elec_from_shaft(rpm110, 110.0))
# WS1's grade-hold bus power is 99.34 kW; chain loss bus->wheel at that
# point (motor ~60% load -> part-load factor 1.0)
elec_chain_ws4 = gen110_loss + 99.34 * (1 - DL.eta_bus_to_wheel)

# case: R6 corner continuous
b_corner = float(ENG_V2.bsfc(2200.0, 132.0 * DER * 1e3
                             / (2200.0 * 2 * np.pi / 60))) * 1.02
split_corner = engine_energy_split(132.0 * DER, b_corner)
gen_corner_loss = 132.0 * DER - float(GEN_V2.elec_from_shaft(
    2200.0, 132.0 * DER))

# case: engine at full continuous rating, sea level (long climb, series)
b_cont = float(ENG_V2.bsfc(2200.0, 132.0 * 1e3 / (2200.0 * 2 * np.pi / 60)))
split_cont = engine_energy_split(132.0, b_cont)

# case: V1 fixed point
split_v1 = engine_energy_split(pinV1["p_shaft_kw"], pinV1["bsfc"])
gen_v1_loss = pinV1["p_shaft_kw"] - pinV1["p_bus_kw"]

# case: G1(a) cycle average (reference seed)
ra = R["gate_g1"]["nominal"]["_raw_reference_seed"]["a"]
Th = ra["duration_s"] / 3600.0
R["heat_ledger_ws6"] = dict(
    _split_model=("WS4-DECLARED split of (fuel-shaft): exhaust 49%, "
                  "coolant+oil 38%, CAC 10%, radiation 3%; radiator "
                  "package = coolant+oil+CAC = 48%"),
    V2_grade_hold_6pct_61kmh_series_10min=dict(
        electrical_chain_kW_WS1_of_record=20.2,
        electrical_chain_kW_ws4_maps=elec_chain_ws4,
        generator_loss_kW_ws4=gen110_loss,
        engine_shaft_kW=110.0, engine_bsfc_g_per_kWh=b110,
        engine_fuel_kW=split110["fuel_kW"],
        engine_radiator_package_kW=split110["radiator_package_kW"],
        engine_exhaust_kW=split110["exhaust_kW"],
        ws1_engine_estimate_kW=99.0,
        note="WS1 ledger seed said ~99 kW engine rejection; energy-balance "
             "radiator package is smaller because ~half leaves as exhaust"),
    V2_R6_corner_continuous=dict(
        engine_shaft_kW=132.0 * DER, ambient_C=45.0, altitude_m=2000.0,
        bsfc_g_per_kWh_incl_2pct_altitude_adder=b_corner,
        engine_fuel_kW=split_corner["fuel_kW"],
        engine_radiator_package_kW=split_corner["radiator_package_kW"],
        engine_exhaust_kW=split_corner["exhaust_kW"],
        generator_loss_kW=gen_corner_loss,
        note="cooling sizing point: 45 C ambient, thin air, full "
             "continuous load - THE radiator design case"),
    V2_continuous_max_sea_level=dict(
        engine_shaft_kW=132.0,
        engine_radiator_package_kW=split_cont["radiator_package_kW"],
        engine_exhaust_kW=split_cont["exhaust_kW"],
        generator_loss_kW=132.0 - float(GEN_V2.elec_from_shaft(2200.0,
                                                               132.0))),
    V1_fixed_point_running=dict(
        engine_shaft_kW=pinV1["p_shaft_kw"],
        engine_radiator_package_kW=split_v1["radiator_package_kW"],
        engine_exhaust_kW=split_v1["exhaust_kW"],
        generator_loss_kW=gen_v1_loss,
        duty_cycle_VOLT_SUB=ss_ref["duty"],
        duty_averaged_radiator_kW=split_v1["radiator_package_kW"]
        * ss_ref["duty"]),
    G1a_VOLT_REG_cycle_average=dict(
        engine_rejection_avg_kW=ra["eng_reject_kwh"] / Th,
        generator_loss_avg_kW=ra["e_gen_loss_kwh"] / Th,
        electric_chain_loss_avg_kW=ra["e_chain_loss_kwh"] / Th,
        direct_path_loss_avg_kW=ra["e_dl_loss_kwh"] / Th,
        friction_brake_kWh_per_cycle=ra["e_fric_kwh"],
        pm_spin_shaft_kWh_per_cycle=ra["e_spin_shaft_kwh"],
        pm_spin_bus_kWh_per_cycle=ra["e_spin_bus_kwh"],
        pm_spin_note=("G1-R: the spin-drag energy is charged to (a)'s "
                      "fuel here; the heat itself lands in the traction "
                      "machine, on WS2's LT-loop ledger line")),
    brake_resistor_50kW=dict(owner="WS2 (R2)",
                             note="listed to avoid a ledger gap; heat is on "
                                  "WS2's line, cooling packaging on WS6"))

# ---------------------------------------------------------------------------
# 8. machine-readable interface block
# ---------------------------------------------------------------------------
g1n = R["gate_g1"]["nominal"]["ensemble"]

# R18 blocker (directive item 4): precisely which 4HK1-V2C figures need
# procured-datasheet confirmation, and the test that substantiates the
# 132 kW flat-rating if the datasheet is silent.
R["r18_datasheet_confirmation"] = {
    "blocking_figures": {
        "continuous_flat_rating": (
            "132 kW continuous shaft @ 2,200 rpm as an unlimited-hours "
            "prime/COP-class rating (ISO 8528-1 / ISO 3046-1 basis, no "
            "10%-overload dependency). The published 4HK1-TC figures are "
            "automotive (153 kW peak); the 132 kW continuous is a "
            "WS4-proposed genset recalibration and exists on no public "
            "sheet."),
        "derate_model": (
            "the flat-rating boundary in corner-delivery form (R18 label): "
            "either 'no derate to 2,000 m / +45 C' or the datasheet derate "
            "curve. WS4 assumed 4%/1,000 m above 1,000 m and 1%/5 C above "
            "30 C (factor 0.9312); the +0.82 kW R6 margin flips if the "
            "confirmed rating is 1 kW lower or the slope 1%/1,000 m "
            "steeper.")},
    "non_blocking_figures": {
        "torque_respec": ("750 Nm @ 1,400 rpm full-load curve (E3 spec) "
                          "on production hardware"),
        "bsfc_map": ("Willans-constructed island 203.6 g/kWh / rated-"
                     "continuous 215.4 g/kWh (G1 margins move with the "
                     "map, the gate verdict is re-runnable on a measured "
                     "map in this pipeline)"),
        "motoring_fmep_anchor": "10.7 kW at 1,706 rpm",
        "heat_split": "49/38/10/3 exhaust/coolant+oil/CAC/radiation",
        "mass": "~500 kg dry"},
    "substantiating_test_if_datasheet_silent": (
        "witnessed dynamometer heat-run per ISO 3046-1 (corrections per "
        "ISO 15550 / SAE J1349), two legs: (i) sea level: 132 kW @ 2,200 "
        "rpm held continuously to thermal steady state (coolant/oil dT/dt "
        "< 1 K per 10 min, >= 4 h), fuel stop untouched, smoke/EGT/boost "
        "inside the manufacturer's continuous limits; (ii) simulated R6 "
        "corner: inlet conditions set to 2,000 m / +45 C equivalents "
        "(~79.5 kPa inlet depression + 45 C cell or altitude chamber), "
        "same fuel stop, acceptance >= 122.1 kW shaft sustained to steady "
        "state. A third point at ~1,000 m equivalent pins the two derate "
        "coefficients separately. The corner leg tests delivery, not the "
        "label - R18's corner-delivery form is the requirement."),
    "gates": "these two blocking figures + G1-R are the WS6 release "
             "blockers (R18)"}

R["interface_ws4"] = {
    "_basis": ("mirrors WS1 results.json conventions; extrema are 8-seed "
               "ensemble envelopes (R9); all shaft powers are engine "
               "shaft; all cross-WS electrical quantities bus-side (R12); "
               "BSFC maps are WS4-constructed Willans maps; G1 traction "
               "chain per R12 = WS2 measured maps x 0.97 reduction, no "
               "scalar PE member"),
    "v2_genset": {
        "engine": "4HK1-V2C (Isuzu 4HK1-TC hardware, genset recalibration)",
        "displacement_l": 5.193,
        "continuous_shaft_kW_sea_level": 132.0,
        "peak_shaft_kW": ENG_V2.peak_power_kw(),
        "low_end_torque_spec_Nm_at_1400rpm": 750.0,
        "r6_corner": {
            "conditions": "45 C, 2,000 m, +20% payload, 4 kW aux, CdA 5.4",
            "derate_factor": DER,
            "delivered_shaft_kW": 132.0 * DER,
            "required_shaft_kW": R6_CORNER_REQUIRED_KW,
            "margin_kW": 132.0 * DER - R6_CORNER_REQUIRED_KW,
            "status": ("PROVISIONAL - the +0.82 kW margin rests on the "
                       "WS4-proposed 132 kW continuous flat-rating and the "
                       "WS4-declared class-typical derate model, both TBC "
                       "against the procured datasheet (ESC-1; adjudication "
                       "r1 F5). Do not release WS6 packaging against this "
                       "margin until both are confirmed.")},
        "r18_datasheet_confirmation": R["r18_datasheet_confirmation"],
        "generator": R["generators"]["V2"],
        "pinned_series_point": pinV2,
        "mass_kg": dict(engine_dry=500.0, generator=90.0, rectifier=12.0,
                        mounts_adaptation=35.0, total_dry=637.0,
                        aftertreatment_extra=60.0),
        "volume_m3_envelope": 0.67,
        "bsfc_map_file": "data/bsfc_map_V2_candidate.csv",
        "reference_map_file": "data/bsfc_map_4HK1_ref.csv",
        "gen_map_file": "data/gen_eff_map_V2.csv"},
    "v1_genset": {
        "engine": "V3307-V1C (Kubota V3307-CR-T class)",
        "displacement_l": 3.331,
        "continuous_shaft_kW_sea_level": 50.0,
        "rated_shaft_kW": 55.4,
        "generator": R["generators"]["V1"],
        "pinned_series_point": pinV1,
        "mass_kg": dict(engine_dry=305.0, generator=48.0, rectifier=8.0,
                        mounts_adaptation=25.0, total_dry=386.0),
        "volume_m3_envelope": 0.35,
        "bsfc_map_file": "data/bsfc_map_V1_candidate.csv",
        "gen_map_file": "data/gen_eff_map_V1.csv"},
    "gate_g1": {
        "_revision": ("G1-R recompute (G1R_DIRECTIVE.md; rulings R10/R11/"
                      "R12/R18). Supersedes the r2 gate numbers, which are "
                      "retained under results_ws4.json -> "
                      "gate_g1_prior_convention as the regression anchor."),
        "condition": ("nominal: sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, "
                      "2 kW aux, GVW, VOLT-REG"),
        "convention": R["gate_g1"]["nominal"]["_convention"],
        "traction_chain_of_record": {
            "map_file": R["ws2_chain_of_record"]["map_file"],
            "map_voltage_V": R["ws2_chain_of_record"]["map_voltage_V"],
            "vintage": R["ws2_chain_of_record"]["vintage"],
            "ws2_rework_round": R["ws2_chain_of_record"]["ws2_rework_round"],
            "reduction_flat": 0.97,
            "hot_swap": ("re-running run_ws4.py after WS2 r4 lands "
                         "consumes the 432/662/749 V maps and r4 spin "
                         "member automatically (map keyed nearest WS2's "
                         "exported dc_bus.nominal_V)")},
        "spin_drag_member": R["ws2_chain_of_record"]["spin_drag_member"],
        "margin_pct_ensemble_min": g1n["margin_pct_min"],
        "margin_pct_ensemble_min_governing_case":
            g1n["margin_pct_min_governing_case"],
        "margin_pct_ensemble_median": g1n["margin_pct_median"],
        "margin_pct_ensemble_max": g1n["margin_pct_max"],
        "kill_criterion_pct": 5.0,
        "passes": g1n["passes_kill_criterion"],
        "one_factor_sensitivity": R["gate_g1_one_factor"],
        "genset_conditioning_bracket":
            R["gate_g1_genset_conditioning_bracket"],
        "condition_dependence": {
            "_note": ("the pass is condition-dependent inside the R7 "
                      "envelope - see ESC-2; full ensembles in "
                      "gate_g1/<case>/ensemble"),
            "margin_pct_ensemble_min_at_2000m_45C":
                R["gate_g1"]["alt2000m_45C"]["ensemble"]["margin_pct_min"],
            "passes_at_2000m_45C":
                R["gate_g1"]["alt2000m_45C"]["ensemble"]
                 ["passes_kill_criterion"],
            "margin_pct_ensemble_min_hot_45C_sea_level":
                R["gate_g1"]["hot_45C_sea_level"]["ensemble"]
                 ["margin_pct_min"],
            "passes_hot_45C_sea_level":
                R["gate_g1"]["hot_45C_sea_level"]["ensemble"]
                 ["passes_kill_criterion"],
            "margin_pct_ensemble_min_CdA_5.4":
                R["gate_g1"]["cda_5.4"]["ensemble"]["margin_pct_min"],
            "passes_CdA_5.4":
                R["gate_g1"]["cda_5.4"]["ensemble"]["passes_kill_criterion"],
            "margin_pct_ensemble_min_aux_4kW":
                R["gate_g1"]["aux_4kW"]["ensemble"]["margin_pct_min"],
            "passes_aux_4kW":
                R["gate_g1"]["aux_4kW"]["ensemble"]["passes_kill_criterion"],
            "see": "ESC-2"}},
    "v1_start_stop": {
        "pinned_point": pinV1,
        "starts_per_8h_shift_at_R8_floor_hyst0.8kWh_ensemble":
            [SS["ensemble_hyst_0.8kWh"]["starts_per_8h_min"],
             SS["ensemble_hyst_0.8kWh"]["starts_per_8h_max"]]},
    "coolant_loads_to_ws6": "see heat_ledger_ws6",
}

# ---------------------------------------------------------------------------
# 9. first-principles sanity numbers used in the report
# ---------------------------------------------------------------------------
_ref = R["gate_g1"]["nominal"]["_raw_reference_seed"]
# R12-restated chain arithmetic: the traction chain is the WS2 map x 0.97
# reduction; the energy-weighted VOLT-REG motoring efficiency WS2 exports
# (cycle_loss_summary eta_mot_avg) is the honest single-number stand-in
_eta_chain_r12 = 0.97 * WS2X["eta_mot_avg_VOLT_REG"]
R["sanity"] = dict(
    direct_path_eta_at_85kmh_cruise=float(
        46.9 / ((46.9 + 0.9 * 1706 / 1800.0) / 0.972)),
    series_fuel_to_wheel_g_per_kWh=pinV2["bsfc"] / (
        pinV2["eta_gen"] * DL.eta_bus_to_wheel),
    series_fuel_to_wheel_g_per_kWh_R12=pinV2["bsfc"] / (
        pinV2["eta_gen"] * _eta_chain_r12),
    eta_chain_bus_to_wheel_R12_energy_weighted=_eta_chain_r12,
    banking_redeploy_eta_R12=float(
        pinV2["eta_gen"] * 0.97 * 0.97 * _eta_chain_r12),
    locked_fuel_to_wheel_at_median_load_g_per_kWh=float(
        ENG_V2.bsfc(1805.0, 0.48 * ENG_V2.t_max(1805.0))) / 0.95,
    fuel_b_l_per_100km_ref_seed=_ref["b"]["l_per_100km"],
    fuel_a_l_per_100km_ref_seed=_ref["a"]["l_per_100km"],
    locked_fraction_ref_seed_a=_ref["a"]["locked_s"] / _ref["a"]["duration_s"],
    ws1_locked_time_fraction=0.692,
    motoring_drag_1706rpm_kW=float(
        ENG_V2.fmep_bar(1706.0) * 1e5 * ENG_V2.disp_m3 * 1706.0 / 120 / 1e3),
    spin_rate_check_vs_85kmh_point_W=dict(
        mean_locked_shaft_rate_W=SPIN_SH * 1e3,
        ws2_85kmh_shaft_point_W=WS2X["spin"][
            "point_check_shaft_drag_85kmh_W"],
        note=("the mean locked-time rate derived from WS2's cycle "
              "integral should sit near the 85 km/h point drag - "
              "VOLT-REG's locked residency centres there")),
    bsfc_selfcheck_max_err=err)

# ---------------------------------------------------------------------------
# 10. figures
# ---------------------------------------------------------------------------
import matplotlib                                                # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                  # noqa: E402

# fig 1: V2 candidate BSFC map with operating points
rg = np.linspace(700, 3000, 180)
tg = np.linspace(20, 760, 180)
RG, TG = np.meshgrid(rg, tg)
B = ENG_V2.bsfc(RG, TG)
B = np.where(TG <= ENG_V2.t_max(RG), B, np.nan)
fig, ax = plt.subplots(figsize=(8, 5.2))
cs = ax.contourf(RG, TG, B, levels=[200, 205, 210, 215, 220, 230, 245,
                                    260, 290, 330, 400], cmap="viridis_r")
fig.colorbar(cs, label="BSFC [g/kWh] (WS4 Willans construction)")
ax.plot(rg, ENG_V2.t_max(rg), "k-", lw=2, label="full-load (4HK1-V2C)")
ax.plot(rg, ENG_REF.t_max(rg), "k--", lw=1, label="reference 4HK1 curve")
ax.plot([pinV2["rpm"]], [pinV2["trq_Nm"]], "r*", ms=16,
        label=f"pinned series point ({pinV2['bsfc']:.0f} g/kWh)")
# locked-path residency band (WS1: rpm p05-p95 1,414-2,005, load 19-78%)
ax.axvspan(1414, 2005, color="orange", alpha=0.15,
           label="locked-path residency (WS1 p05-p95)")
ax.set_xlabel("engine speed [rpm]")
ax.set_ylabel("torque [Nm]")
ax.legend(loc="upper right", fontsize=8)
ax.set_title("4HK1-V2C constructed BSFC map, series pin vs locked residency")
fig.tight_layout()
fig.savefig("figs/fig01_bsfc_v2.png", dpi=140)
plt.close(fig)

# fig 2: G1 fuel per seed
fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(len(REG_SEEDS))
ax.bar(x - 0.22, a_fuel, 0.2, label="(a) locked + load-point shift")
ax.bar(x, b_fuel, 0.2, label="(b) pure series, pinned point")
ax.bar(x + 0.22, bp_fuel, 0.2, label="(b') series, best-BSFC locus")
ax.set_xticks(x)
ax.set_xticklabels([str(s) for s in REG_SEEDS])
ax.set_xlabel("VOLT-REG seed")
ax.set_ylabel("fuel per cycle [kg]")
ax.set_title(f"GATE G1-R: margin min {g1n['margin_pct_min']:.1f}% / median "
             f"{g1n['margin_pct_median']:.1f}% (kill criterion 5%)")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("figs/fig02_g1_fuel.png", dpi=140)
plt.close(fig)

# fig 3: V1 starts vs hysteresis window
fig, ax = plt.subplots(figsize=(7, 4))
hs = [0.5, 0.8, 1.1]
st = [SS["hysteresis_sweep_ref_seed"][f"{h:.1f}kWh"]["starts_per_8h_shift"]
      for h in hs]
ax.plot(hs, st, "o-", label="usable 1.5 kWh (R8 floor)")
ax.plot([1.6], [SS["usable_3.0_hyst_1.6"]["starts_per_8h_shift"]], "s",
        label="usable 3.0 kWh, hyst 1.6 kWh")
ax.set_xlabel("start-stop hysteresis window [kWh]")
ax.set_ylabel("starts per 8 h shift")
ax.set_title("V1 start-stop: starts vs buffer window (VOLT-SUB ref seed)")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("figs/fig03_v1_starts.png", dpi=140)
plt.close(fig)

# ---------------------------------------------------------------------------
with open("results_ws4.json", "w") as f:
    json.dump(R, f, indent=1, default=float)

log("")
log("==== WS4 summary (G1-R) ====")
log(f"traction chain vintage: WS2 round {WS2X['ws2_rework_round']}, "
    f"{WS2X['map_file_rel']} ({WS2X['map_voltage_V']:.0f} V map, WS2 bus "
    f"nominal {WS2X['ws2_bus_nominal_V']:.1f} V)"
    + ("" if _R4_LANDED else "  [r4 NOT landed - hot-swap on re-run]"))
log(f"spin member: {SPIN_SH*1e3:.0f} W shaft + {SPIN_BUS*1e3:.0f} W bus "
    f"while locked (WS2 export {WS2X['spin']['e_spin_shaft_kWh_per_VOLT_REG']:.4f}"
    f" + {WS2X['spin']['e_spin_bus_kWh_per_VOLT_REG']:.4f} kWh/VOLT-REG)")
log(f"R6 corner: derate {DER:.4f}; candidate delivers {132*DER:.1f} kW "
    f"vs required {R6_CORNER_REQUIRED_KW} kW")
log(f"G1-R nominal margin (a beats b by): min {g1n['margin_pct_min']:.2f}% "
    f"median {g1n['margin_pct_median']:.2f}% max "
    f"{g1n['margin_pct_max']:.2f}%  (kill criterion >= 5.0%; passes: "
    f"{g1n['passes_kill_criterion']})")
_of = R["gate_g1_one_factor"]
log(f"  prior convention (anchor, reproduced): "
    f"min {_of['prior_convention']['min']:.2f}% "
    f"median {_of['prior_convention']['median']:.2f}%")
log(f"  one-factor spin drag alone:     min {_of['spin_drag_alone']['min']:.2f}% "
    f"(delta {_of['spin_drag_alone']['delta_pp_min']:+.2f} pp)")
log(f"  one-factor map-vs-scalar alone: min {_of['map_vs_scalar_alone']['min']:.2f}% "
    f"(delta {_of['map_vs_scalar_alone']['delta_pp_min']:+.2f} pp)")
_br = R["gate_g1_genset_conditioning_bracket"]
log(f"  genset-conditioning bracket: 3%-replacement min "
    f"{_br['replacement_3pct_class']['min']:.2f}%, stacked min "
    f"{_br['stacked_declared_plus_3pct']['min']:.2f}% "
    f"(kill outcome invariant)")
for tag in ("cda_5.4", "aux_4kW", "hot_45C_sea_level", "alt2000m_45C",
            "reference_curve"):
    e = R["gate_g1"][tag]["ensemble"]
    log(f"G1-R {tag}: min {e['margin_pct_min']:.2f}% "
        f"median {e['margin_pct_median']:.2f}%")
log(f"V1 starts/8h shift at R8 floor (0.8 kWh hyst): "
    f"{SS['ensemble_hyst_0.8kWh']['starts_per_8h_min']:.0f}-"
    f"{SS['ensemble_hyst_0.8kWh']['starts_per_8h_max']:.0f}")
log(f"V1 fuel saving vs continuous: {SS['fuel_saving_vs_continuous_pct']:.1f}%")

with open("run_output.txt", "w") as f:
    f.write("\n".join(_LOG) + "\n")

# wall-clock goes to the console only, never into the committed artefact
# (adjudication r1 F7: run_output.txt is now byte-stable under re-run)
print(f"elapsed {time.time()-t0:.0f}s")
