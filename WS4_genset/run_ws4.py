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
    revision=("KX round per WS4_genset/KX_DIRECTIVE.md (rulings R22, R23): "
              "the R23 errata F1-F5 are corrected and checker-pinned, the "
              "R22a verification run (pure series V2 at the delivered "
              "11.08 kWh pack, three ordered cases, 8 seeds) is executed "
              "as series_duty_v2, and interface_ws4 -> gate_g1 becomes an "
              "ARCHIVED record block (status executed_kill_2026-08-30). "
              "The gate itself is NOT re-run or re-argued: its numbers "
              "reproduce bit-identically. See REPORT_WS4.md changelog "
              "s0-KX; the G1-R changelog s0-R is retained as history."),
    against=("BASELINE_v3.md (ratified 2026-08-30; kill executed, R22/R23) "
             "and BASELINE_v5.md (ratified 2026-08-30; R34 program "
             "hygiene - 10 Hz trace export). The gate numbers below were "
             "computed against BASELINE_v2.md and are archived, not "
             "recomputed."),
    reads=["../BASELINE_v3.md", "../BASELINE_v5.md",
           "../WS1_loads_duty_cycles/REPORT_WS1.md",
           "../WS1_loads_duty_cycles/results.json",
           "../WS2_traction_motor/results.json",
           "../WS2_traction_motor/data/cycle_loss_summary.csv",
           "../WS2_traction_motor/data/effmap_motor_inverter_*.csv",
           "../WS3_battery/results.json",
           "../WS3_battery/regen_acceptance.csv"],
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
    # R23 erratum F4: the owner-relative path WS2 exports, plus the
    # WS4-relative path every other *_file field in this workstream's
    # interface resolves against. Downstream consumers use the latter.
    map_file_owner="WS2_traction_motor",
    map_file_ws4_relative=os.path.join("..", "WS2_traction_motor",
                                       WS2X["map_file_rel"]).replace(
                                           os.sep, "/"),
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
            # R23/F1 erratum: the per-seed SIGN split is now an exported
            # number, not report prose. Counted over the enumerated
            # 8-seed case set with the governing set labeled inline
            # (R14). The r3 report claimed "two" positive seeds at
            # CdA 5.4 where the data has four.
            seeds_total=len(m),
            seeds_margin_positive_n=int(sum(1 for x in m if x > 0.0)),
            seeds_margin_positive=[REG_SEEDS[k] for k, x in enumerate(m)
                                   if x > 0.0],
            seeds_margin_positive_governing_case=(
                "count over the enumerated 8-seed VOLT-REG ensemble "
                f"[{tag}]; positive = mode (a) beats mode (b) on that "
                "seed"),
            per_seed_margin_sign=[("+" if x > 0.0 else "-") for x in m],
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


# ===========================================================================
# 5-KX. KX_DIRECTIVE.md — R23 errata instrumentation + R22a verification run
#
# The gate above is ARCHIVED: BASELINE_v3 executed G1's kill clause. Nothing
# below re-runs or re-argues it. This section (a) instruments the four
# record-precision errata the adjudicator raised (F2-F5; F1 is exported in
# g1_config above), and (b) executes the R22a verification run the directive
# orders: PURE SERIES V2 at the DELIVERED pack.
# ===========================================================================
import csv as _csv                                                # noqa: E402

WS3_DIR = os.path.join("..", "WS3_battery")
WS1_DIR = os.path.join("..", "WS1_loads_duty_cycles")

# --- KX input provenance: every input this section consumes, SHA-256 pinned
# on disk (the discipline G1-R used for the WS2 chain, extended to WS3's
# delivered-pack and R16 exports and to WS1's cycle builders).
_KX_INPUTS = {
    "WS2/results.json": os.path.join("..", "WS2_traction_motor",
                                     "results.json"),
    "WS2/data/cycle_loss_summary.csv": os.path.join(
        "..", "WS2_traction_motor", "data", "cycle_loss_summary.csv"),
    "WS2/" + WS2X["map_file_rel"]: WS2X["map_path"],
    "WS3/results.json": os.path.join(WS3_DIR, "results.json"),
    "WS3/regen_acceptance.csv": os.path.join(WS3_DIR,
                                             "regen_acceptance.csv"),
    "WS1/results.json": os.path.join(WS1_DIR, "results.json"),
    "WS1/volt_cycles.py": os.path.join(WS1_DIR, "volt_cycles.py"),
    "WS1/volt_params.py": os.path.join(WS1_DIR, "volt_params.py"),
    "WS1/volt_physics.py": os.path.join(WS1_DIR, "volt_physics.py"),
}
with open(os.path.join(WS3_DIR, "results.json")) as _f:
    _WS3 = json.load(_f)
with open(os.path.join(WS1_DIR, "results.json")) as _f:
    _WS1 = json.load(_f)
USABLE_KX_KWH = float(_WS3["interface_WS3"]["packs"]["V2"]["usable_bus_kWh"])
_WS3_SOC = _WS3["interface_WS3"]["soc_strategy"]
R["kx_input_provenance"] = dict(
    ruling="KX_DIRECTIVE.md item 2 (SHA-pin the inputs as for G1-R)",
    input_sha256={k: _sha256(p) for k, p in sorted(_KX_INPUTS.items())},
    vintages=dict(
        ws2_rework_round=WS2X["ws2_rework_round"],
        ws2_results_date=WS2X["ws2_results_date"],
        ws2_map_file=WS2X["map_file_rel"],
        ws2_map_voltage_V=WS2X["map_voltage_V"],
        ws3_results_date=(_WS3.get("_meta", {}).get("date")
                          or "not exported by WS3 (no _meta block); the "
                             "SHA-256 above IS the vintage - WS3 is "
                             "CLOSED-RATIFIED per BASELINE_v3"),
        ws3_delivered_usable_bus_kWh=USABLE_KX_KWH,
        ws3_regen_acceptance_file="regen_acceptance.csv (R16 interface "
                                  "of record)",
        ws1_results_date=(_WS1.get("_meta", {}).get("date")
                          or "not exported by WS1 (no _meta block); the "
                             "SHA-256 above IS the vintage - WS1 is "
                             "CLOSED per BASELINE_v3"),
        vintage_basis=("byte-level: mtimes are not used anywhere in this "
                       "block (r3 adjudication note). Where a producer "
                       "exports a round or date, it is carried; otherwise "
                       "the hash stands alone.")),
    note=("the R22a run consumes WS2 r4 maps + spin member, WS3's delivered "
          "288s1p pack (usable_bus_kWh read from WS3's own interface block, "
          "not transcribed), WS3's R16 regen_acceptance.csv, and WS1's "
          "seeded VOLT-REG builders. WS2 r4 is adjudicated clean "
          "(BASELINE_v3); WS3 is CLOSED-RATIFIED; WS1 is CLOSED."))


# ---------------------------------------------------------------- F2 erratum
# Measure the map-boundary convention's exposure per condition, and bound the
# loss it does not book. The r3 report claimed the convention is mode-
# neutral; it is mode-neutral only where the exposure lands on unlocked
# samples. Locked-sample exposure is one-sided in mode (b)'s favour, because
# mode (a) serves those samples on the engine.
def boundary_exposure_case(chain, cyc, veh, m=None, regen_cap_kw=75.0):
    m = VEH.m_gvw if m is None else m
    t, v = cyc["t"], cyc["v"]
    dt = float(np.median(np.diff(t)))
    p_wheel = wheel_power_trace(cyc, m, veh) / 1e3
    locked = lockup_state(v, p_wheel * 1e3)
    drive = p_wheel > 0.0
    rpm, trq = chain.motor_rpm_and_torque(v, np.clip(p_wheel, 0.0, None),
                                          motoring=True)
    ob = chain.boundary_exposure(rpm, trq) & drive
    ob_strict = chain.boundary_exposure_strict(rpm, trq) & drive
    excess = chain.boundary_excess_loss_kw(rpm, trq) * ob
    blend = np.clip((v - CTL.v_regen_blend_lo)
                    / (CTL.v_regen_blend_hi - CTL.v_regen_blend_lo), 0.0, 1.0)
    p_capt0 = np.minimum(np.clip(-p_wheel, 0.0, None), regen_cap_kw) * blend
    rpm_g, trq_g = chain.motor_rpm_and_torque(v, p_capt0, motoring=False)
    ob_g = chain.boundary_exposure(rpm_g, trq_g) & (p_capt0 > 1e-9)
    vk = v * 3.6
    return dict(
        exposure_s_motoring=float(ob.sum()) * dt,
        exposure_s_motoring_strict=float(ob_strict.sum()) * dt,
        exposure_s_motoring_strict_on_locked_samples=float(
            (ob_strict & locked).sum()) * dt,
        exposure_s_motoring_on_locked_samples=float((ob & locked).sum()) * dt,
        exposure_s_motoring_on_unlocked_samples=float(
            (ob & ~locked).sum()) * dt,
        exposure_s_regen=float(ob_g.sum()) * dt,
        exposed_speed_kmh_min=float(vk[ob].min()) if ob.any() else 0.0,
        exposed_speed_kmh_max=float(vk[ob].max()) if ob.any() else 0.0,
        exposed_speed_kmh_median=float(np.median(vk[ob])) if ob.any() else 0.0,
        over_boundary_wheel_kWh=float((p_wheel * ob).sum()) * dt / 3600.0,
        unbooked_bus_kWh_linear=float(excess.sum()) * dt / 3600.0,
        unbooked_bus_kWh_linear_locked_only=float(
            (excess * locked).sum()) * dt / 3600.0)


def _fuel_g_for_bus_kwh(kwh, pin):
    """Marginal fuel [g] for bus energy served from the pinned point."""
    return kwh / pin["eta_gen"] * pin["bsfc"]


_F2_CASES = {
    "nominal": VEH,
    "cda_5.4": dataclasses.replace(VEH, CdA=5.4),
    "aux_4kW": VEH,
    "hot_45C_sea_level": dataclasses.replace(VEH, rho_air=1.1097),
    "alt2000m_45C": dataclasses.replace(VEH, rho_air=0.8706),
    "reference_curve": VEH,
}
_f2 = {}
for _case, _veh in _F2_CASES.items():
    _rows = {}
    _pin = G1[_case]["pinned_point"]
    for sd in REG_SEEDS:
        _r = boundary_exposure_case(CHAIN, REG[sd], _veh)
        _fb = G1[_case]["per_seed"][str(sd)]["b"]["fuel_kg"] * 1e3
        _r["one_sided_pp_locked_linear"] = 100.0 * _fuel_g_for_bus_kwh(
            _r["unbooked_bus_kWh_linear_locked_only"], _pin) / _fb
        _r["one_sided_pp_locked_hostile_2x"] = \
            2.0 * _r["one_sided_pp_locked_linear"]
        _r["total_pp_linear"] = 100.0 * _fuel_g_for_bus_kwh(
            _r["unbooked_bus_kWh_linear"], _pin) / _fb
        _rows[str(sd)] = _r
    _env = {}
    for _k in ("exposure_s_motoring", "exposure_s_motoring_strict",
               "exposure_s_motoring_strict_on_locked_samples",
               "exposure_s_motoring_on_locked_samples",
               "exposure_s_motoring_on_unlocked_samples",
               "exposure_s_regen", "over_boundary_wheel_kWh",
               "exposed_speed_kmh_max",
               "unbooked_bus_kWh_linear",
               "unbooked_bus_kWh_linear_locked_only",
               "one_sided_pp_locked_linear",
               "one_sided_pp_locked_hostile_2x", "total_pp_linear"):
        _vals = [_rows[str(sd)][_k] for sd in REG_SEEDS]
        _env[_k + "_min"] = min(_vals)
        _env[_k + "_max"] = max(_vals)
        _env[_k + "_max_governing_case"] = (
            f"seed {REG_SEEDS[int(np.argmax(_vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{_case}]")
    _f2[_case] = dict(per_seed=_rows, envelope=_env)
R["chain_boundary_exposure"] = dict(
    ruling="R23 erratum F2",
    definition=("a sample is EXPOSED when the bilinear stencil the loss "
                "lookup uses touches an originally-infeasible map cell, or "
                "when its (rpm, torque) coordinate is clamped to the grid - "
                "i.e. it is served at a boundary loss rather than a measured "
                "one. Counted on WS2's 662 V map with the identical (rpm, "
                "signed torque) coordinates the chain queries."),
    strict_definition=("*_strict counts only queries whose TORQUE lies "
                       "outside the feasible envelope of its own rpm column "
                       "(or with a clamped coordinate) - the criterion the "
                       "r3 adjudicator measured against. The stencil "
                       "criterion above is a superset of it, so WS4's "
                       "headline exposure is the more conservative count."),
    unbooked_loss_model=("[WS4-DECLARED] the loss surface is extended past "
                         "each rpm column's feasible torque boundary with "
                         "that column's own one-sided torque gradient; "
                         "copper loss grows as T^2, so the linear extension "
                         "is a LOWER bound and the hostile row doubles the "
                         "gradient"),
    one_sided_basis=("mode (a) serves LOCKED samples on the engine, so only "
                     "the locked-sample exposure is one-sided in mode (b)'s "
                     "favour; it is priced at the pinned point's marginal "
                     "fuel rate and expressed as percentage points of mode "
                     "(b)'s cycle fuel"),
    supersedes=("REPORT_WS4.md s4.1 r3 wording 'the convention is "
                "mode-neutral and negligible (~0.001 kWh)' - true at the "
                "reference seed, false as a general claim"),
    cases=_f2)

# ---------------------------------------------------------------- F3 erratum
# The printed map-vintage spread, computed - not asserted. Two spans: the
# 432-749 V exported window alone, and that window plus the r3-interim
# figure the r3 sentence's parenthetical swept in.
_vint = [G1["nominal"]["ensemble"]["margin_pct_min"]] + \
    [v["min"] for v in R["gate_g1_map_vintage_check"].values()]
_vint_r3 = _vint + [R["gate_g1_interim_r3_vintage_record"]["margin_pct_min"]]
R["gate_g1_map_vintage_spread"] = dict(
    ruling="R23 erratum F3",
    members_432_749V_window=sorted(_vint),
    spread_pp_432_749V_window=max(_vint) - min(_vint),
    members_incl_r3_interim=sorted(_vint_r3),
    spread_pp_incl_r3_interim=max(_vint_r3) - min(_vint_r3),
    governing_case=("max minus min over the enumerated set {nominal 662 V, "
                    "432 V map, 749 V map} and, for the second span, that "
                    "set plus the r3-interim 370 V-vintage historical "
                    "record"),
    note=("the r3 report printed 'under 0.6 pp' for a sentence whose "
          "parenthetical included the r3-interim figure: that span is "
          "0.63 pp as printed. The 432-749 V window alone is the smaller "
          "span. Both are now rendered from this block."))

# ---------------------------------------------------------------- F5 erratum
# 0.9005 is 0.97 x WS2's eta_mot_avg, energy-weighted over WS2's own i-MMD
# VOLT-REG run (launch-heavy, mostly unlocked). The series duty mode (b)
# actually realises weights the same map differently. Both are now stated.
def series_duty_chain_eta(chain, cyc, veh, m=None):
    m = VEH.m_gvw if m is None else m
    t, v = cyc["t"], cyc["v"]
    dt = float(np.median(np.diff(t)))
    p_wheel = wheel_power_trace(cyc, m, veh) / 1e3
    drive = p_wheel > 0.0
    eta = chain.eta_bus_to_wheel(v, np.clip(p_wheel, 0.0, None))
    e_wheel = float(p_wheel[drive].sum()) * dt / 3600.0
    e_bus = float((p_wheel[drive] / eta[drive]).sum()) * dt / 3600.0
    return e_wheel / e_bus, e_wheel, e_bus


_pinKX = G1["nominal"]["pinned_point"]
_eta_cycle_share = 0.97 * WS2X["eta_mot_avg_VOLT_REG"]
_sd_eta = {}
for sd in REG_SEEDS:
    _e, _ew, _eb = series_duty_chain_eta(CHAIN, REG[sd], VEH)
    _sd_eta[str(sd)] = dict(eta=_e, wheel_kWh=_ew, bus_kWh=_eb)
_sd_vals = [_sd_eta[str(sd)]["eta"] for sd in REG_SEEDS]
_eta_series_ref = _sd_eta["23"]["eta"]
R["chain_weighting_convention"] = dict(
    ruling="R23 erratum F5",
    ws2_cycle_share_weighted=dict(
        eta_bus_to_wheel=_eta_cycle_share,
        series_fuel_to_wheel_g_per_kWh=_pinKX["bsfc"] / (
            _pinKX["eta_gen"] * _eta_cycle_share),
        basis=("0.97 reduction x WS2's exported eta_mot_avg, which is "
               "energy-weighted over WS2's i-MMD VOLT-REG run - the motor "
               "handles the launch-heavy, mostly-unlocked share there. This "
               "is the right weighting for the BANKING REDEPLOY rate (s10 "
               "check 5), which is spent on that same share.")),
    series_duty_weighted=dict(
        eta_bus_to_wheel_ref_seed=_eta_series_ref,
        eta_bus_to_wheel_min=min(_sd_vals),
        eta_bus_to_wheel_max=max(_sd_vals),
        eta_bus_to_wheel_min_governing_case=(
            f"seed {REG_SEEDS[int(np.argmin(_sd_vals))]} of the enumerated "
            "8-seed VOLT-REG ensemble [nominal]"),
        series_fuel_to_wheel_g_per_kWh_ref_seed=_pinKX["bsfc"] / (
            _pinKX["eta_gen"] * _eta_series_ref),
        per_seed=_sd_eta,
        basis=("wheel energy / bus energy through the SAME WS2 map over the "
               "full VOLT-REG motoring trace - the weighting mode (b) "
               "actually realises in pure series")),
    note=("the simulation is unaffected: it uses the map per sample, and its "
          "(b) delivers the realised wheel rate. The r3 report presented the "
          "cycle-share number as the trace-weighted chain; the series-duty "
          "companion is LARGER, so the r3 arithmetic understated the series "
          "advantage - the imprecision leaned conservative, toward the "
          "clutch."))


# ===========================================================================
# R22a VERIFICATION RUN — series_duty_v2 (KX_DIRECTIVE.md item 2)
# ===========================================================================
def load_r16_curve(path, col="V2pack_chg_cont_kW_bus"):
    """WS3's R16 charge-acceptance curve (the interface of record):
    cell temperature -> continuous pack charge acceptance, bus-side."""
    T, P, hdr = [], [], None
    with open(path) as f:
        for row in _csv.reader(f):
            if not row or row[0].startswith("#"):
                continue
            if hdr is None:
                hdr = row
                continue
            T.append(float(row[0]))
            P.append(float(row[hdr.index(col)]))
    return np.array(T), np.array(P)


R16_T, R16_P = load_r16_curve(os.path.join(WS3_DIR, "regen_acceptance.csv"))
COAST_SH_KW = float(WS2X["spin"]["point_check_shaft_drag_85kmh_W"]) / 1e3
COAST_BUS_KW = float(WS2X["spin"]["point_check_bus_draw_85kmh_W"]) / 1e3

KX_CASES = {
    "nominal": dict(
        veh=VEH, derate=1.0, t_cell_C=25.0,
        condition=("sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, 2 kW aux, "
                   "GVW 6,600 kg, VOLT-REG")),
    "cda_5.4": dict(
        veh=dataclasses.replace(VEH, CdA=5.4), derate=1.0, t_cell_C=25.0,
        condition=("E13 high-drag body, CdA 5.4 m^2, otherwise nominal")),
    "alt2000m_45C": dict(
        veh=dataclasses.replace(VEH, rho_air=0.8706), derate=DER,
        t_cell_C=45.0,
        condition=("2,000 m / +45 C: rho 0.8706 kg/m^3 and engine derate "
                   f"{DER:.4f}. IDENTICAL to the archived gate's "
                   "alt2000m_45C case (GVW, CdA 4.2, 2 kW aux) - NOT the "
                   "stricter R6 RATING corner, which additionally carries "
                   "+20% payload, CdA 5.4 and 4 kW aux and is used to size "
                   "the engine, not to run the duty")),
}
_ACCEPT = {k: float(np.interp(c["t_cell_C"], R16_T, R16_P))
           for k, c in KX_CASES.items()}

SD = dict(
    _basis=("R22a verification run ordered by KX_DIRECTIVE.md item 2: PURE "
            "SERIES V2 at the DELIVERED pack. Mode (b) - the genset pinned "
            "at its best-BSFC point with SOC-hysteresis start-stop - is the "
            "block of record; mode (b') - the same genset load-following "
            "along its best-BSFC locus - is carried as a COMPANION so WS5's "
            "R22b dispatch question has both endpoints on the same trace. "
            "WS4 does not choose the dispatch; R22b assigns that to WS5."),
    _inputs=dict(
        usable_bus_kWh=USABLE_KX_KWH,
        usable_source=("WS3 results.json -> interface_WS3.packs.V2."
                       "usable_bus_kWh (delivered 288s1p LTO pack), read "
                       "at run time, not transcribed"),
        superseded_floor_kWh=USABLE_V2_KWH,
        superseded_floor_note=("the archived gate ran on the R8 3.5 kWh "
                               "floor, which ESC-5/R22a identify as an "
                               "i-MMD-era sizing; this run is at the "
                               "delivered pack"),
        traction_chain=("R12: WS2 r4 measured inverter+motor map x 0.97 "
                        "reduction, both directions, no scalar PE member"),
        r10_window=R10_DC_WINDOW,
        r16_curve_file="../WS3_battery/regen_acceptance.csv",
        r16_column="V2pack_chg_cont_kW_bus",
        r16_declared_cell_temperature_C={k: c["t_cell_C"]
                                         for k, c in KX_CASES.items()},
        r16_accept_kW_bus=_ACCEPT,
        r16_declaration_basis=("cell temperature declared equal to ambient "
                               "for each case; WS3's pack-loop sizing line "
                               "holds cells at or below 55 C at +45 C "
                               "ambient, so 45 C is the tracking value and "
                               "55 C the loop's design ceiling - see "
                               "r16_binding_analysis"),
        supervisor=("unchanged from the ratified simulator: SOC target "
                    f"{sim.SOC_START:.2f}, series hysteresis "
                    f"{sim.SER_LO:.2f}-{sim.SER_HI:.2f} of usable, "
                    f"emergency load-follow band {sim.EMERG_LO:.2f}-"
                    f"{sim.EMERG_HI:.2f}. Nothing was tuned for this run; "
                    "the hysteresis sensitivity below runs WS3's own "
                    "allocated genset band instead."),
        spin_member=("none charged: modes (b)/(b') never lock, and loaded "
                     "series machine losses are inside WS2's maps (R22d). "
                     "The true-COAST member R22d names is measured and "
                     "reported separately, and is NOT charged to fuel."),
        seeds=REG_SEEDS),
    cases={})

SD_KEYS = ("fuel_kg", "fuel_energy_kWh", "fuel_energy_kWh_per_km",
           "fuel_energy_kWh_per_payload_tonne_km", "l_per_100km",
           "distance_km", "duration_s", "unserved_bus_kWh",
           "above_pin_demand_s", "above_pin_demand_kWh",
           "above_pin_engine_s", "above_pin_transitions_per_h",
           "emergency_band_s", "genset_starts", "genset_stops",
           "genset_starts_per_h", "genset_on_frac", "soc_min", "soc_max",
           "soc_end", "soc_drift_kWh", "motor_over_rating_s",
           "regen_bus_peak_kW", "regen_shed_by_r16_kWh", "pack_chg_peak_kW",
           "pack_dis_peak_kW", "pack_chg_over_r8_110kW_s",
           "pack_dis_over_r8_125kW_s", "coast_no_regen_s",
           "r22d_coast_spin_shaft_kWh", "r22d_coast_spin_bus_kWh",
           "r8_envelope_dis_clip_s", "r8_envelope_chg_clip_s",
           "r8_envelope_chg_shed_kWh",
           "mean_bsfc_eff_g_per_kWh", "engine_reject_kWh",
           "generator_loss_kWh", "chain_loss_kWh", "friction_brake_kWh",
           "bus_energy_kWh")
PAYLOAD_T = VEH.m_payload_at_gvw / 1000.0


def _sd_record(o):
    """The per-seed export set KX_DIRECTIVE.md item 2 orders, plus the
    pack-power and heat members the program rules require."""
    return dict(
        fuel_kg=o["fuel_corrected_g"] / 1e3,
        fuel_energy_kWh=o["fuel_energy_kwh"],
        fuel_energy_kWh_per_km=o["fuel_energy_kWh_per_km"],
        fuel_energy_kWh_per_payload_tonne_km=(
            o["fuel_energy_kWh_per_km"] / PAYLOAD_T),
        l_per_100km=o["l_per_100km"],
        distance_km=o["distance_km"], duration_s=o["duration_s"],
        unserved_bus_kWh=o["unserved_kwh"],
        above_pin_demand_s=o["above_pin_demand_s"],
        above_pin_demand_kWh=o["above_pin_demand_kwh"],
        above_pin_engine_s=o["above_pin_engine_s"],
        above_pin_transitions_per_h=o["above_pin_transitions_per_h"],
        emergency_band_s=o["emerg_s"],
        genset_starts=o["starts"], genset_stops=o["eng_stops"],
        genset_starts_per_h=o["starts_per_h"],
        genset_on_frac=o["eng_on_frac"],
        soc_min=o["soc_min"], soc_max=o["soc_max"], soc_end=o["soc_end"],
        soc_drift_kWh=o["soc_drift_kwh_cells"],
        motor_over_rating_s=o["over_rating_s"],
        regen_bus_peak_kW=o["regen_bus_peak_kw"],
        regen_shed_by_r16_kWh=o["regen_shed_r16_kwh"],
        pack_chg_peak_kW=o["pack_chg_peak_kw"],
        pack_dis_peak_kW=o["pack_dis_peak_kw"],
        pack_chg_over_r8_110kW_s=o["pack_chg_over_r8_110kW_s"],
        pack_dis_over_r8_125kW_s=o["pack_dis_over_r8_125kW_s"],
        coast_no_regen_s=o["coast_no_regen_s"],
        r22d_coast_spin_shaft_kWh=o["coast_spin_shaft_kwh_r22d"],
        r22d_coast_spin_bus_kWh=o["coast_spin_bus_kwh_r22d"],
        r8_envelope_dis_clip_s=o["r8_dis_clip_s"],
        r8_envelope_chg_clip_s=o["r8_chg_clip_s"],
        r8_envelope_chg_shed_kWh=o["r8_chg_shed_kwh"],
        mean_bsfc_eff_g_per_kWh=o["mean_bsfc_eff_g_per_kwh"],
        engine_reject_kWh=o["eng_reject_kwh"],
        generator_loss_kWh=o["e_gen_loss_kwh"],
        chain_loss_kWh=o["e_chain_loss_kwh"],
        friction_brake_kWh=o["e_fric_kwh"],
        bus_energy_kWh=o["e_bus_kwh"])


def _sd_envelope(per_seed, tag):
    """R14: every exported extremum is an explicit min/max over the
    enumerated 8-seed case set with its governing seed labeled inline."""
    env = {}
    for k in SD_KEYS:
        vals = [per_seed[str(sd)][k] for sd in REG_SEEDS]
        env[k + "_min"] = min(vals)
        env[k + "_max"] = max(vals)
        env[k + "_median"] = float(np.median(vals))
        env[k + "_min_governing_case"] = (
            f"seed {REG_SEEDS[int(np.argmin(vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{tag}]")
        env[k + "_max_governing_case"] = (
            f"seed {REG_SEEDS[int(np.argmax(vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{tag}]")
    return env


_SD_TRACE = None
_SD_SOC = []
for _case, _cfg in KX_CASES.items():
    log(f"R22a series_duty_v2: {_case} (delivered pack "
        f"{USABLE_KX_KWH:.3f} kWh usable, R16 accept "
        f"{_ACCEPT[_case]:.1f} kW bus) ...")
    _per_seed = {"b": {}, "bp": {}}
    _pin_case = None
    for sd in REG_SEEDS:
        for md in ("b", "bp"):
            _o = run_g1_mode(
                REG[sd], md, ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
                veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
                chg_accept_bus_kw=_ACCEPT[_case],
                spin_coast_shaft_kw_85=COAST_SH_KW,
                spin_coast_bus_kw_85=COAST_BUS_KW,
                trace=(md == "b" and sd == 23 and _case == "nominal"),
                soc_trace_stride=(50 if md == "b" else None))
            if md == "b":
                if _pin_case is None:
                    _pin_case = _o["pinned"]
                if "trace" in _o:
                    _SD_TRACE = _o.pop("trace")
                _SD_SOC.append((_case, sd, _o.pop("soc_trace")))
            _per_seed[md][str(sd)] = _sd_record(_o)
        _b = _per_seed["b"][str(sd)]
        log(f"  [{_case}] seed {sd}: b={_b['fuel_kg']:.2f}kg, "
            f"unserved={_b['unserved_bus_kWh']:.3f} kWh, above-pin demand "
            f"{_b['above_pin_demand_s']:.0f}s, starts {_b['genset_starts']:.0f}"
            f", SOC {_b['soc_min']:.3f}-{_b['soc_max']:.3f}")
    SD["cases"][_case] = dict(
        condition=_cfg["condition"],
        declared_cell_temperature_C=_cfg["t_cell_C"],
        r16_accept_kW_bus=_ACCEPT[_case],
        pinned_point=_pin_case,
        per_seed=_per_seed["b"],
        ensemble=_sd_envelope(_per_seed["b"], _case),
        companion_bp=dict(
            _note=("load-following companion for R22b - NOT the block of "
                   "record; WS5 owns the dispatch choice"),
            per_seed=_per_seed["bp"],
            ensemble=_sd_envelope(_per_seed["bp"], _case + "/bp")))

# --- unserved-energy verdict (the directive: expected zero; nonzero is a
# finding, not a tuning knob)
_uns = {c: SD["cases"][c]["ensemble"]["unserved_bus_kWh_max"]
        for c in KX_CASES}
SD["unserved_energy_verdict"] = dict(
    ruling="R22a / ESC-5",
    per_case_max_kWh=_uns,
    worst_case_kWh=max(_uns.values()),
    worst_case_governing_case=(
        "no governing case - every ordered case is exactly zero on all "
        "8 seeds" if max(_uns.values()) <= 1e-9
        else max(_uns, key=lambda c: _uns[c])),
    all_cases_zero=bool(max(_uns.values()) <= 1e-9),
    criterion=("zero unserved bus energy on every seed of every ordered "
               "case; a nonzero value is a finding, not a tuning knob"),
    archived_gate_comparison=dict(
        r8_floor_kWh=USABLE_V2_KWH,
        nominal_max_kWh=R["gate_g1"]["nominal"]["ensemble"][
            "b_unserved_kwh_max"],
        cda_5_4_max_kWh=R["gate_g1"]["cda_5.4"]["ensemble"][
            "b_unserved_kwh_max"],
        note=("the archived gate's mode (b) on the 3.5 kWh R8 floor shed up "
              "to this much at CdA 5.4 - the ESC-5 buffer problem R22a "
              "sends to the delivered pack")))

# --- SOC-window check against WS3's declared R8 discharge gate. WS3
# declares the 120 kW discharge peak over SOC 40-90 and states plainly
# that full power below SOC 40 is NOT guaranteed ("WS5 dispatch limit").
# WS3's SOC there is on NAMEPLATE; this sim's SOC is a fraction of
# USABLE, so the two are mapped through WS3's own end stops before
# being compared. Measured off the 5 s decimated SOC trajectories.
_END = _WS3_SOC["allocation"]["V2"]["end_stops_pct_nameplate"]
_NP_LO, _NP_HI = _END[0] / 100.0, 1.0 - _END[1] / 100.0
_GATE_NP = 0.40
_GATE_US = (_GATE_NP - _NP_LO) / (_NP_HI - _NP_LO)
_gate_rows = {}
for _case, _sd, _tr in _SD_SOC:
    _n = sum(1 for x in _tr["SOC"] if x < _GATE_US)
    _gate_rows.setdefault(_case, []).append(
        (_n * 5.0, min(_tr["SOC"]),
         _NP_LO + min(_tr["SOC"]) * (_NP_HI - _NP_LO)))
SD["soc_window_check"] = dict(
    ruling="WS3 interface_WS3.bus_voltage_window.soc15_note / r8_compliance",
    ws3_statement=_WS3["interface_WS3"]["bus_voltage_window"]["soc15_note"],
    ws3_end_stops_pct_nameplate=_END,
    gate_soc_nameplate=_GATE_NP,
    gate_soc_usable_equivalent=_GATE_US,
    mapping=("SOC_nameplate = end_stop_lo + SOC_usable x (1 - end_stop_hi "
             "- end_stop_lo); WS4-DECLARED reading of WS3's convention"),
    resolution_s=5.0,
    cases={c: dict(
        t_below_gate_s_min=min(r[0] for r in rows),
        t_below_gate_s_max=max(r[0] for r in rows),
        t_below_gate_s_max_governing_case=(
            f"seed {REG_SEEDS[max(range(len(rows)), key=lambda i: rows[i][0])]}"
            f" of the enumerated 8-seed VOLT-REG ensemble [{c}]"),
        soc_usable_min=min(r[1] for r in rows),
        soc_nameplate_min=min(r[2] for r in rows))
        for c, rows in _gate_rows.items()},
    reading=("the ordered run spends real time below the SOC band over "
             "which WS3 declares the R8 discharge peak, on every case. "
             "Combined with the bus-side power exceedance, that is the "
             "substance of ESC-9: it is a dispatch question, and WS4 does "
             "not answer it."))

# --- R16 binding analysis: the ordered cases are all warm, so state
# plainly whether the curve bound anything and where it would.
_pk_regen = max(SD["cases"][c]["ensemble"]["regen_bus_peak_kW_max"]
                for c in KX_CASES)
_cold_mask = R16_T <= 10.0
_hot_mask = R16_T >= 45.0
SD["r16_binding_analysis"] = dict(
    ruling="R16 (regen_acceptance.csv is the interface of record)",
    peak_regen_to_pack_kW_bus=_pk_regen,
    peak_regen_governing_case=max(
        KX_CASES, key=lambda c: SD["cases"][c]["ensemble"][
            "regen_bus_peak_kW_max"]),
    accept_kW_bus_at_declared_cells=_ACCEPT,
    bound_any_sample=bool(max(
        SD["cases"][c]["ensemble"]["regen_shed_by_r16_kWh_max"]
        for c in KX_CASES) > 1e-12),
    cold_side_binding_cell_C=float(np.interp(
        _pk_regen, R16_P[_cold_mask], R16_T[_cold_mask])),
    hot_side_binding_cell_C=float(np.interp(
        _pk_regen, R16_P[_hot_mask][::-1], R16_T[_hot_mask][::-1])),
    accept_at_ws3_loop_ceiling_55C_kW=float(np.interp(55.0, R16_T, R16_P)),
    note=("all three ordered cases are warm, so R16's curve is NOT binding "
          "in this run: peak regen-to-pack is far below the acceptance at "
          "the declared cell temperatures and regen_shed_by_r16_kWh is zero "
          "on every seed. The curve binds below the cold-side temperature "
          "above, and again above the hot-side one - and WS3's pack-loop "
          "SIZING LINE permits cells to 55 C at +45 C ambient, where "
          "acceptance falls to the value above. That hot-end crossing is "
          "escalated (ESC-8), not resolved here."))

# --- R8 POWER-envelope bracket (WS4 adversarial check, not ordered).
# The ordered run constrains the pack's ENERGY, not its POWER: R8's
# bus-side envelope (125 kW discharge / 110 kW charge, ES-4/R12) is
# measured and reported above but not enforced, and the measurement says
# it is exceeded. This bracket enforces it - discharge above the cap
# cannot be served and is booked as unserved bus energy; charge above the
# cap is shed - so the record shows what "zero unserved energy" costs
# when the pack's rated power is treated as a wall. ESC-9.
log("R22a bracket: R8 bus-side power envelope enforced "
    "(125 kW discharge / 110 kW charge) ...")
_R8B = {}
for _case, _cfg in KX_CASES.items():
    _ps = {}
    for sd in REG_SEEDS:
        _o = run_g1_mode(
            REG[sd], "b", ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
            veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
            chg_accept_bus_kw=_ACCEPT[_case],
            dis_cap_bus_kw=125.0, chg_cap_bus_kw=110.0,
            spin_coast_shaft_kw_85=COAST_SH_KW,
            spin_coast_bus_kw_85=COAST_BUS_KW)
        _ps[str(sd)] = _sd_record(_o)
    _R8B[_case] = dict(per_seed=_ps,
                       ensemble=_sd_envelope(_ps, _case + "/R8-envelope"))
    log(f"  [{_case}] unserved "
        f"{_R8B[_case]['ensemble']['unserved_bus_kWh_min']:.3f}-"
        f"{_R8B[_case]['ensemble']['unserved_bus_kWh_max']:.3f} kWh, "
        f"discharge clipped "
        f"{_R8B[_case]['ensemble']['r8_envelope_dis_clip_s_max']:.1f} s")
SD["r8_power_envelope_bracket"] = dict(
    ruling="R8 as restated by R12/ES-4 (125 kW discharge / 110 kW charge, "
           "bus-side)",
    _status=("WS4 adversarial bracket, NOT an ordered case. The ordered "
             "series_duty_v2 numbers above stand as run; this bracket "
             "prices the assumption they rest on."),
    dis_cap_bus_kW=125.0, chg_cap_bus_kW=110.0,
    enforcement=("discharge demand above the cap is unserved (booked and "
                 "fuel-corrected exactly as the buffer-empty case is); "
                 "charge above the cap is shed"),
    cases=_R8B,
    worst_unserved_kWh=max(_R8B[c]["ensemble"]["unserved_bus_kWh_max"]
                           for c in KX_CASES),
    worst_unserved_governing_case=max(
        KX_CASES,
        key=lambda c: _R8B[c]["ensemble"]["unserved_bus_kWh_max"]),
    reading=("R4/E24's 'the spine is not sized for forced series' record "
             "extends to the PACK's power envelope, not only the motor "
             "rating: the delivered pack has the ENERGY for pure-series "
             "VOLT-REG with margin, and the ordered run confirms that, but "
             "at its rated bus-side power it does not have the POWER on "
             "the hardest samples. This is a dispatch and rating question "
             "for WS5/WS3, not a WS4 tuning knob - escalated as ESC-9."))

# --- hysteresis sensitivity: WS3's own allocated genset band on the
# delivered pack, reference seed. The cycling rate is the export WS5 needs
# and it is band-sensitive, so the band is not left implicit.
_hyst_kwh = float(_WS3_SOC["allocation"]["V2"]["genset_hysteresis_kWh"])
_soc_tgt = float(_WS3_SOC["target"])
_half = 0.5 * _hyst_kwh / USABLE_KX_KWH
SD["hysteresis_sensitivity_ref_seed"] = dict(
    ruling="R19 precedent / WS3 soc_strategy.allocation.V2",
    ws3_allocated_genset_hysteresis_kWh=_hyst_kwh,
    ws3_soc_target=_soc_tgt,
    band_soc_fraction=[_soc_tgt - _half, _soc_tgt + _half],
    simulator_band_soc_fraction=[sim.SER_LO, sim.SER_HI],
    simulator_band_kWh=(sim.SER_HI - sim.SER_LO) * USABLE_KX_KWH,
    cases={})
for _case, _cfg in KX_CASES.items():
    _o = run_g1_mode(
        REG[23], "b", ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
        veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
        chg_accept_bus_kw=_ACCEPT[_case],
        ser_band=(_soc_tgt - _half, _soc_tgt + _half),
        spin_coast_shaft_kw_85=COAST_SH_KW,
        spin_coast_bus_kw_85=COAST_BUS_KW)
    SD["hysteresis_sensitivity_ref_seed"]["cases"][_case] = dict(
        ws3_band=_sd_record(_o),
        simulator_band=SD["cases"][_case]["per_seed"]["23"])

# --- R22d operational member, quantified on this run
_c_sh = [SD["cases"][c]["ensemble"]["r22d_coast_spin_shaft_kWh_max"]
         for c in KX_CASES]
_c_bus = [SD["cases"][c]["ensemble"]["r22d_coast_spin_bus_kWh_max"]
          for c in KX_CASES]
_c_pp = {}
for c in KX_CASES:
    e = SD["cases"][c]["ensemble"]
    # price the coast member at the pinned point's marginal fuel rate:
    # shaft-side drag has to be made up at the wheel through the chain,
    # bus-side draw is served from the bus directly
    _pin_c = SD["cases"][c]["pinned_point"]
    _g = ((e["r22d_coast_spin_shaft_kWh_max"] / _eta_series_ref
           + e["r22d_coast_spin_bus_kWh_max"])
          / _pin_c["eta_gen"] * _pin_c["bsfc"])
    _c_pp[c] = 100.0 * _g / (e["fuel_kg_max"] * 1e3)
SD["r22d_coast_spin_member"] = dict(
    ruling="R22d",
    ws2_point_drag_85kmh_W=dict(shaft=WS2X["spin"][
        "point_check_shaft_drag_85kmh_W"],
        bus=WS2X["spin"]["point_check_bus_draw_85kmh_W"]),
    scaling="[WS4-DECLARED] linear in road speed from WS2's 85 km/h point",
    coast_no_regen_s_max=max(
        SD["cases"][c]["ensemble"]["coast_no_regen_s_max"] for c in KX_CASES),
    coast_spin_shaft_kWh_max=max(_c_sh),
    coast_spin_bus_kWh_max=max(_c_bus),
    unbooked_pp_of_cycle_fuel=_c_pp,
    unbooked_pp_max=max(_c_pp.values()),
    unbooked_pp_max_governing_case=max(_c_pp, key=lambda c: _c_pp[c]),
    charged_to_fuel=False,
    direction_of_error=("series_duty_v2's fuel numbers EXCLUDE this member, "
                        "so they are optimistic by the percentage points "
                        "above. R22d's own remedy - the WS5 supervisor "
                        "preferring light regen over true coast - removes "
                        "the exposure by removing the true-coast samples; "
                        "the member is exported so WS5 can price that "
                        "choice."))

# --- heat rows for the WS6 ledger, by component and case (program rule 7)
SD_HEAT = {}
for _case in KX_CASES:
    _e = SD["cases"][_case]["ensemble"]
    _h = SD["cases"][_case]["per_seed"]["23"]["duration_s"] / 3600.0
    SD_HEAT[f"series_duty_v2_{_case}_cycle_average"] = dict(
        case=f"R22a pure-series V2 at the delivered pack, {_case}, "
             "VOLT-REG cycle average (8-seed max, reference-seed duration)",
        engine_rejection_avg_kW=_e["engine_reject_kWh_max"] / _h,
        generator_loss_avg_kW=_e["generator_loss_kWh_max"] / _h,
        electric_chain_loss_avg_kW=_e["chain_loss_kWh_max"] / _h,
        friction_brake_kWh_per_cycle=_e["friction_brake_kWh_max"],
        pm_coast_spin_shaft_kWh_per_cycle=_e["r22d_coast_spin_shaft_kWh_max"],
        pm_coast_spin_bus_kWh_per_cycle=_e["r22d_coast_spin_bus_kWh_max"],
        governing_case=_e["engine_reject_kWh_max_governing_case"],
        sink=("engine rejection -> HT radiator package + exhaust "
              "(49/38/10/3 split, see _split_model); generator and "
              "rectifier -> LT loop; chain losses -> WS2's LT loop; "
              "friction -> brakes/air"))

R["series_duty_v2"] = SD

# --- 10 Hz trace (R34, BASELINE_v5 program hygiene) + SOC trajectories
_TRACE_COLS = [("t_s", "{:.4f}"), ("v_kmh", "{:.4f}"),
               ("grade_pct", "{:.4f}"), ("P_wheel_kW", "{:.4f}"),
               ("P_bus_load_kW", "{:.4f}"), ("P_gen_bus_kW", "{:.4f}"),
               ("P_batt_bus_kW", "{:.4f}"), ("SOC", "{:.6f}"),
               ("P_shaft_eng_kW", "{:.4f}"), ("fuel_g_per_s", "{:.5f}"),
               ("engine_on", "{:.0f}")]
_trace_file = "data/trace_series_duty_v2_nominal_seed23_10Hz.csv"
with open(_trace_file, "w") as f:
    f.write("# Project Volt WS4 - R34 10 Hz trace, one per run.\n")
    f.write("# series_duty_v2 / nominal / mode (b) pure series at the "
            "pinned point / VOLT-REG seed 23 (reference)\n")
    f.write(f"# delivered pack {USABLE_KX_KWH:.6f} kWh usable at the bus; "
            f"R16 acceptance {_ACCEPT['nominal']:.3f} kW bus at "
            f"{KX_CASES['nominal']['t_cell_C']:.1f} C cells; WS2 r4 662 V "
            "map chain; all electrical quantities bus-side (R12)\n")
    f.write("# SOC is fraction of USABLE bus energy, not of nameplate\n")
    f.write(",".join(c for c, _ in _TRACE_COLS) + "\n")
    _n = len(_SD_TRACE["t_s"])
    _cols = [_SD_TRACE[c] for c, _ in _TRACE_COLS]
    _fmts = [fm for _, fm in _TRACE_COLS]
    for _i in range(_n):
        f.write(",".join(fm.format(col[_i])
                         for col, fm in zip(_cols, _fmts)) + "\n")
_soc_file = "data/series_duty_v2_soc_trajectories.csv"
with open(_soc_file, "w") as f:
    f.write("# Project Volt WS4 - R22a SOC trajectories, mode (b) pure "
            "series at the delivered pack, all 8 VOLT-REG seeds x 3 "
            "ordered cases\n")
    f.write("# decimated to 5.0 s (every 50th 10 Hz sample); the full-rate "
            f"reference trajectory is in {_trace_file}\n")
    f.write("# SOC is fraction of USABLE bus energy "
            f"({USABLE_KX_KWH:.6f} kWh)\n")
    f.write("case,seed,t_s,SOC,P_bus_load_kW,P_batt_bus_kW,engine_on\n")
    for _case, _sd, _tr in _SD_SOC:
        for _i in range(len(_tr["t_s"])):
            f.write(f"{_case},{_sd},{_tr['t_s'][_i]:.1f},"
                    f"{_tr['SOC'][_i]:.6f},{_tr['P_bus_load_kW'][_i]:.4f},"
                    f"{_tr['P_batt_bus_kW'][_i]:.4f},"
                    f"{_tr['engine_on'][_i]:.0f}\n")
SD["_trace_files"] = dict(
    ruling="R34 (BASELINE_v5 program hygiene)",
    trace_10Hz=_trace_file,
    trace_10Hz_rows=len(_SD_TRACE["t_s"]),
    soc_trajectories=_soc_file,
    soc_decimation_s=5.0)

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
                                  "WS2's line, cooling packaging on WS6"),
    # KX/R22a: the pure-series V2 duty at the delivered pack is the
    # architecture of record after the kill, so its rejection rows are
    # the ones WS6 should size the Vehicle Zero V2 loops against.
    **SD_HEAT)

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

# Interface projections of the R22a run (see the note on the block below).
# IFACE_SEED_KEYS is exactly the directive's ordered per-seed export set;
# IFACE_ENV_KEYS adds the quantities this report's findings and
# escalations quote, each carrying its R14 governing-case label.
IFACE_SEED_KEYS = (
    "unserved_bus_kWh", "above_pin_demand_s", "above_pin_demand_kWh",
    "above_pin_engine_s", "above_pin_transitions_per_h", "genset_starts",
    "genset_starts_per_h", "genset_on_frac", "soc_min", "soc_max",
    "soc_end", "fuel_energy_kWh_per_km")
IFACE_ENV_KEYS = IFACE_SEED_KEYS + (
    "fuel_energy_kWh_per_payload_tonne_km", "l_per_100km", "fuel_kg",
    "emergency_band_s", "motor_over_rating_s", "pack_dis_peak_kW",
    "pack_chg_peak_kW", "pack_dis_over_r8_125kW_s",
    "pack_chg_over_r8_110kW_s", "regen_bus_peak_kW",
    "regen_shed_by_r16_kWh", "engine_reject_kWh")
IFACE_R8_KEYS = ("unserved_bus_kWh", "r8_envelope_dis_clip_s",
                 "r8_envelope_chg_shed_kWh", "fuel_kg",
                 "fuel_energy_kWh_per_km", "genset_starts")


def _env_subset(env, keys):
    out = {}
    for k in keys:
        for suf in ("_min", "_max", "_median", "_min_governing_case",
                    "_max_governing_case"):
            if k + suf in env:
                out[k + suf] = env[k + suf]
    return out


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
    # =====================================================================
    # ARCHIVED RECORD BLOCK - KX_DIRECTIVE.md item 3.
    # Gate G1 was decided: BASELINE_v3 executed the kill clause and DELETED
    # the clutch. This block is the historical record of that decision -
    # verdict, attribution rows, bracket result, provenance hashes. NO FIELD
    # OF IT MAY BE CONSUMED AS A LIVE REQUIREMENT. The live V2 duty inputs
    # are interface_ws4 -> series_duty_v2.
    # =====================================================================
    "gate_g1": {
        "status": "executed_kill_2026-08-30",
        "_archival_notice": (
            "ARCHIVED. Gate G1's kill clause was EXECUTED in BASELINE_v3 "
            "(ratified 2026-08-30): the clutch, the lockup device and "
            "actuator, clutch-sync control, R11's condition-aware mode "
            "policy, fault spec F-1 and the i-MMD topology reference are "
            "all deleted with it. Both variants are pure series. This block "
            "is retained as the record of the decision and its provenance. "
            "NO FIELD OF THIS BLOCK MAY BE CONSUMED AS A LIVE REQUIREMENT - "
            "consume interface_ws4 -> series_duty_v2 instead. Mode (a) does "
            "not exist in any live architecture."),
        "executed_by": "BASELINE_v3.md, GATE G1: EXECUTED. THE CLUTCH IS "
                       "DELETED.",
        "_revision": ("G1-R recompute (G1R_DIRECTIVE.md; rulings R10/R11/"
                      "R12/R18), errata-corrected under R23/KX. Supersedes "
                      "the r2 gate numbers, which are retained under "
                      "results_ws4.json -> gate_g1_prior_convention as the "
                      "regression anchor."),
        "verdict": {
            "condition": ("nominal: sea level, rho 1.20 kg/m^3, CdA 4.2 "
                          "m^2, 2 kW aux, GVW, VOLT-REG"),
            "convention": R["gate_g1"]["nominal"]["_convention"],
            "margin_pct_ensemble_min": g1n["margin_pct_min"],
            "margin_pct_ensemble_min_governing_case":
                g1n["margin_pct_min_governing_case"],
            "margin_pct_ensemble_median": g1n["margin_pct_median"],
            "margin_pct_ensemble_max": g1n["margin_pct_max"],
            "kill_criterion_pct": 5.0,
            "passes": g1n["passes_kill_criterion"],
            "missed_by_pp": 5.0 - g1n["margin_pct_min"],
            "seeds_margin_positive_n": g1n["seeds_margin_positive_n"],
            "seeds_margin_positive": g1n["seeds_margin_positive"],
            "seeds_total": g1n["seeds_total"],
            "condition_dependence": {
                "_note": ("the reversal is condition-dependent inside the "
                          "R7 envelope - see ESC-2; full ensembles in "
                          "gate_g1/<case>/ensemble. R23/F1: the positive-"
                          "seed count at CdA 5.4 is exported here, not "
                          "described in prose."),
                "margin_pct_ensemble_min_at_2000m_45C":
                    R["gate_g1"]["alt2000m_45C"]["ensemble"]
                     ["margin_pct_min"],
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
                "margin_pct_ensemble_median_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]["margin_pct_median"],
                "margin_pct_ensemble_max_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]["margin_pct_max"],
                "seeds_margin_positive_n_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]
                     ["seeds_margin_positive_n"],
                "seeds_margin_positive_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]
                     ["seeds_margin_positive"],
                "seeds_margin_positive_governing_case_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]
                     ["seeds_margin_positive_governing_case"],
                "passes_CdA_5.4":
                    R["gate_g1"]["cda_5.4"]["ensemble"]
                     ["passes_kill_criterion"],
                "margin_pct_ensemble_min_aux_4kW":
                    R["gate_g1"]["aux_4kW"]["ensemble"]["margin_pct_min"],
                "passes_aux_4kW":
                    R["gate_g1"]["aux_4kW"]["ensemble"]
                     ["passes_kill_criterion"],
                "see": "ESC-2"}},
        "attribution_rows": R["gate_g1_one_factor"],
        "bracket_result": R["gate_g1_genset_conditioning_bracket"],
        "map_vintage_robustness": dict(
            **R["gate_g1_map_vintage_check"],
            spread=R["gate_g1_map_vintage_spread"]),
        "provenance_hashes": {
            "ws2_inputs_sha256": R["ws2_chain_of_record"]["input_sha256"],
            "kx_inputs_sha256": R["kx_input_provenance"]["input_sha256"]},
        "traction_chain_of_record": {
            # R23/F4: map_file resolves against THIS workstream's folder,
            # like every other *_file field in interface_ws4.
            "map_file": R["ws2_chain_of_record"]["map_file_ws4_relative"],
            "map_file_owner": R["ws2_chain_of_record"]["map_file_owner"],
            "map_file_as_exported_by_owner":
                R["ws2_chain_of_record"]["map_file"],
            "map_voltage_V": R["ws2_chain_of_record"]["map_voltage_V"],
            "vintage": R["ws2_chain_of_record"]["vintage"],
            "ws2_rework_round": R["ws2_chain_of_record"]["ws2_rework_round"],
            "reduction_flat": 0.97,
            "hot_swap": ("re-running run_ws4.py after WS2 r4 lands "
                         "consumes the 432/662/749 V maps and r4 spin "
                         "member automatically (map keyed nearest WS2's "
                         "exported dc_bus.nominal_V)")},
        "spin_drag_member": R["ws2_chain_of_record"]["spin_drag_member"],
        "boundary_convention_exposure": {
            "_note": ("R23/F4-F2: the map-boundary convention's measured "
                      "exposure and its one-sided magnitude, per condition; "
                      "full tables in results_ws4.json -> "
                      "chain_boundary_exposure"),
            "nominal_one_sided_pp_max":
                R["chain_boundary_exposure"]["cases"]["nominal"]["envelope"]
                 ["one_sided_pp_locked_linear_max"],
            "cda_5.4_one_sided_pp_max":
                R["chain_boundary_exposure"]["cases"]["cda_5.4"]["envelope"]
                 ["one_sided_pp_locked_linear_max"],
            "cda_5.4_one_sided_pp_max_governing_case":
                R["chain_boundary_exposure"]["cases"]["cda_5.4"]["envelope"]
                 ["one_sided_pp_locked_linear_max_governing_case"]},
        "chain_weighting_convention": R["chain_weighting_convention"]},
    # =====================================================================
    # LIVE V2 DUTY BLOCK - the R22a verification run (KX item 2). These are
    # WS5's design inputs for the R22b highway dispatch question.
    #
    # The interface carries the directive's ORDERED export set per seed and
    # the R14-labelled envelopes for the quantities this report and its
    # escalations quote. The full 37-field per-seed record, the full
    # envelopes and the companion/bracket per-seed tables live in
    # results_ws4.json -> series_duty_v2 (same run, same numbers) so the
    # parsed block stays a readable interface rather than a data dump.
    # =====================================================================
    "series_duty_v2": {
        "_status": "live_design_input",
        "_basis": R["series_duty_v2"]["_basis"],
        "_inputs": R["series_duty_v2"]["_inputs"],
        "input_sha256": R["kx_input_provenance"]["input_sha256"],
        "trace_files": R["series_duty_v2"]["_trace_files"],
        "unserved_energy_verdict":
            R["series_duty_v2"]["unserved_energy_verdict"],
        "r16_binding_analysis": R["series_duty_v2"]["r16_binding_analysis"],
        "soc_window_check": R["series_duty_v2"]["soc_window_check"],
        "r8_power_envelope_bracket": {
            k: v for k, v in
            R["series_duty_v2"]["r8_power_envelope_bracket"].items()
            if k != "cases"},
        "r8_power_envelope_bracket_ensembles": {
            _c: _env_subset(
                R["series_duty_v2"]["r8_power_envelope_bracket"]["cases"][
                    _c]["ensemble"], IFACE_R8_KEYS)
            for _c in R["series_duty_v2"]["r8_power_envelope_bracket"][
                "cases"]},
        "hysteresis_sensitivity_ref_seed": dict(
            {k: v for k, v in
             R["series_duty_v2"]["hysteresis_sensitivity_ref_seed"].items()
             if k != "cases"},
            cases={
                _c: {_b: {_k: _v for _k, _v in _row.items()
                          if _k in IFACE_SEED_KEYS}
                     for _b, _row in _bands.items()}
                for _c, _bands in R["series_duty_v2"][
                    "hysteresis_sensitivity_ref_seed"]["cases"].items()}),
        "r22d_coast_spin_member":
            R["series_duty_v2"]["r22d_coast_spin_member"],
        "cases": {
            _c: {
                "condition": R["series_duty_v2"]["cases"][_c]["condition"],
                "declared_cell_temperature_C":
                    R["series_duty_v2"]["cases"][_c][
                        "declared_cell_temperature_C"],
                "r16_accept_kW_bus":
                    R["series_duty_v2"]["cases"][_c]["r16_accept_kW_bus"],
                "pinned_point":
                    R["series_duty_v2"]["cases"][_c]["pinned_point"],
                "ensemble": _env_subset(
                    R["series_duty_v2"]["cases"][_c]["ensemble"],
                    IFACE_ENV_KEYS),
                "per_seed_ordered_exports": {
                    _s: {_k: _v for _k, _v in _row.items()
                         if _k in IFACE_SEED_KEYS}
                    for _s, _row in R["series_duty_v2"]["cases"][_c][
                        "per_seed"].items()},
                "per_seed_full": ("results_ws4.json -> series_duty_v2 -> "
                                  f"cases -> {_c} -> per_seed (all 37 "
                                  "fields, same run)"),
                "companion_bp_ensemble": _env_subset(
                    R["series_duty_v2"]["cases"][_c]["companion_bp"][
                        "ensemble"], IFACE_R8_KEYS)}
            for _c in R["series_duty_v2"]["cases"]}},
    # R22d operational note, as a named member for WS5 (KX item 3)
    "spin_drag_operational_note_r22d": {
        "ruling": "R22d (BASELINE_v3)",
        "statement": ("the traction PM machine is permanently geared, so "
                      "its spin drag at zero torque persists whenever the "
                      "vehicle coasts WITHOUT regen. In driving and "
                      "regenerating operation the drag is inside WS2's "
                      "measured maps and must not be added again."),
        "ws2_point_drag_85kmh_W_shaft":
            WS2X["spin"]["point_check_shaft_drag_85kmh_W"],
        "ws2_point_draw_85kmh_W_bus":
            WS2X["spin"]["point_check_bus_draw_85kmh_W"],
        "ws5_guidance": ("prefer light regen over true coast: the drag is "
                         "paid either way, and only the regen path recovers "
                         "anything from it."),
        "measured_on_series_duty_v2":
            R["series_duty_v2"]["r22d_coast_spin_member"],
        "double_count_warning": ("do NOT apply this member to driving or "
                                 "regenerating samples; the archived gate's "
                                 "lockup spin member (a different quantity, "
                                 "measured over LOCKED time) is in "
                                 "gate_g1.spin_drag_member and applies to no "
                                 "live architecture.")},
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
    # R23 erratum F5: name the weighting, and carry the series-duty
    # companion alongside it (full block: chain_weighting_convention)
    eta_chain_bus_to_wheel_R12_weighting=(
        "WS2 i-MMD VOLT-REG cycle-share weighting (eta_mot_avg)"),
    eta_chain_bus_to_wheel_series_duty_weighted=_eta_series_ref,
    series_fuel_to_wheel_g_per_kWh_series_duty=(
        pinV2["bsfc"] / (pinV2["eta_gen"] * _eta_series_ref)),
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

# fig 4 (KX/R22a): SOC trajectories of the ordered pure-series run at the
# delivered pack - the export the directive names, drawn.
fig, axs = plt.subplots(len(KX_CASES), 1, figsize=(8.4, 7.2), sharex=True)
_by_case = {}
for _case, _sd, _tr in _SD_SOC:
    _by_case.setdefault(_case, []).append((_sd, _tr))
for ax, (_case, _series) in zip(axs, _by_case.items()):
    for _sd, _tr in _series:
        ax.plot(np.array(_tr["t_s"]) / 60.0, _tr["SOC"], lw=0.8,
                label=f"seed {_sd}")
    _e = SD["cases"][_case]["ensemble"]
    ax.axhline(sim.SER_LO, color="k", ls=":", lw=0.8)
    ax.axhline(sim.SER_HI, color="k", ls=":", lw=0.8)
    ax.axhline(sim.EMERG_LO, color="r", ls="--", lw=0.8)
    ax.set_ylabel("SOC (frac usable)")
    ax.set_ylim(0.10, 0.90)
    _st = (f"{_e['genset_starts_min']:.0f}"
           if _e["genset_starts_min"] == _e["genset_starts_max"]
           else f"{_e['genset_starts_min']:.0f}-"
                f"{_e['genset_starts_max']:.0f}")
    ax.set_title(f"{_case}: SOC {_e['soc_min_min']:.3f}-"
                 f"{_e['soc_max_max']:.3f}, unserved "
                 f"{_e['unserved_bus_kWh_max']:.2f} kWh, "
                 f"{_st} genset starts/cycle", fontsize=9)
axs[-1].set_xlabel("time [min]")
axs[0].legend(fontsize=6, ncol=4, loc="upper right")
fig.suptitle(f"R22a: pure series V2 at the delivered pack "
             f"({USABLE_KX_KWH:.2f} kWh usable at the bus), 8 seeds",
             fontsize=10)
fig.tight_layout()
fig.savefig("figs/fig04_series_duty_soc.png", dpi=140)
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
log("")
log("==== KX (R23 errata + R22a verification) ====")
_ce = R["chain_boundary_exposure"]["cases"]
log(f"F1 CdA 5.4 positive seeds: "
    f"{R['gate_g1']['cda_5.4']['ensemble']['seeds_margin_positive_n']:.0f} "
    f"of {R['gate_g1']['cda_5.4']['ensemble']['seeds_total']:.0f} "
    f"{R['gate_g1']['cda_5.4']['ensemble']['seeds_margin_positive']}")
log(f"F2 boundary exposure nominal "
    f"{_ce['nominal']['envelope']['exposure_s_motoring_min']:.1f}-"
    f"{_ce['nominal']['envelope']['exposure_s_motoring_max']:.1f} s/cycle, "
    f"CdA 5.4 {_ce['cda_5.4']['envelope']['exposure_s_motoring_min']:.1f}-"
    f"{_ce['cda_5.4']['envelope']['exposure_s_motoring_max']:.1f} s/cycle; "
    f"one-sided at CdA 5.4 <= "
    f"{_ce['cda_5.4']['envelope']['one_sided_pp_locked_hostile_2x_max']:.3f}"
    " pp")
log(f"F3 map-vintage spread: "
    f"{R['gate_g1_map_vintage_spread']['spread_pp_432_749V_window']:.2f} pp "
    f"(432-749 V window) / "
    f"{R['gate_g1_map_vintage_spread']['spread_pp_incl_r3_interim']:.2f} pp "
    "(incl. r3-interim, as printed)")
log(f"F4 interface traction map path: "
    f"{R['ws2_chain_of_record']['map_file_ws4_relative']}")
log(f"F5 chain weighting: WS2 cycle-share "
    f"{R['sanity']['eta_chain_bus_to_wheel_R12_energy_weighted']:.4f} "
    f"({R['sanity']['series_fuel_to_wheel_g_per_kWh_R12']:.1f} g/kWh) vs "
    f"series-duty {R['sanity']['eta_chain_bus_to_wheel_series_duty_weighted']:.4f} "
    f"({R['sanity']['series_fuel_to_wheel_g_per_kWh_series_duty']:.1f} g/kWh)")
_uv = R["series_duty_v2"]["unserved_energy_verdict"]
log(f"R22a series_duty_v2 at {USABLE_KX_KWH:.3f} kWh usable: unserved bus "
    f"energy worst case {_uv['worst_case_kWh']:.4f} kWh "
    f"({_uv['worst_case_governing_case']}) - all cases zero: "
    f"{_uv['all_cases_zero']}")
for _c in R["series_duty_v2"]["cases"]:
    _e = R["series_duty_v2"]["cases"][_c]["ensemble"]
    log(f"  [{_c}] fuel energy {_e['fuel_energy_kWh_per_km_min']:.3f}-"
        f"{_e['fuel_energy_kWh_per_km_max']:.3f} kWh/km; above-pin demand "
        f"{_e['above_pin_demand_s_min']:.0f}-"
        f"{_e['above_pin_demand_s_max']:.0f} s; starts/h "
        f"{_e['genset_starts_per_h_min']:.1f}-"
        f"{_e['genset_starts_per_h_max']:.1f}; SOC "
        f"{_e['soc_min_min']:.3f}-{_e['soc_max_max']:.3f}; pack peak "
        f"{_e['pack_dis_peak_kW_max']:.1f} kW dis / "
        f"{_e['pack_chg_peak_kW_max']:.1f} kW chg")
log(f"R16 curve binding in this run: "
    f"{R['series_duty_v2']['r16_binding_analysis']['bound_any_sample']} "
    f"(peak regen-to-pack "
    f"{R['series_duty_v2']['r16_binding_analysis']['peak_regen_to_pack_kW_bus']:.1f}"
    f" kW bus; binds below "
    f"{R['series_duty_v2']['r16_binding_analysis']['cold_side_binding_cell_C']:.1f}"
    f" C and above "
    f"{R['series_duty_v2']['r16_binding_analysis']['hot_side_binding_cell_C']:.1f}"
    " C cells)")
_r8b = R["series_duty_v2"]["r8_power_envelope_bracket"]
log(f"R8 power-envelope bracket (125/110 kW bus enforced): worst unserved "
    f"{_r8b['worst_unserved_kWh']:.3f} kWh "
    f"[{_r8b['worst_unserved_governing_case']}] - the ordered run's pack "
    f"discharge peaks at "
    f"{max(R['series_duty_v2']['cases'][c]['ensemble']['pack_dis_peak_kW_max'] for c in R['series_duty_v2']['cases']):.1f}"
    " kW bus")
log(f"R22d true-coast spin member (reported, not charged): up to "
    f"{R['series_duty_v2']['r22d_coast_spin_member']['unbooked_pp_max']:.3f}"
    " pp of cycle fuel")
log(f"R34 10 Hz trace: {R['series_duty_v2']['_trace_files']['trace_10Hz']} "
    f"({R['series_duty_v2']['_trace_files']['trace_10Hz_rows']:,} rows)")

with open("run_output.txt", "w") as f:
    f.write("\n".join(_LOG) + "\n")

# wall-clock goes to the console only, never into the committed artefact
# (adjudication r1 F7: run_output.txt is now byte-stable under re-run)
print(f"elapsed {time.time()-t0:.0f}s")
