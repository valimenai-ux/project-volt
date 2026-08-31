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

# --- KX r3 / adjudication KX2-m3. The member set OF RECORD of the
# ARCHIVED gate's raw reference-seed dump, frozen in the record's own key
# order. `gate_g1` is an archived block (KX_DIRECTIVE item 3) whose
# values may not move; before this freeze its raw dump also could not
# stop GROWING, because it was built from `everything run_g1_mode
# returns`. Any simulator field added after 2026-08-30 belongs to the
# LIVE block (series_duty_v2), never to the archive.
G1_RAW_KEYS_OF_RECORD = (
    'mode', 'fuel_g', 'fuel_corrected_g', 'soc_drift_kwh_cells',
    'fuel_energy_kwh', 'fuel_l', 'starts', 'sync_starts',
    'ramp_starts', 'duration_s', 'distance_km', 'e_fric_kwh',
    'e_gen_loss_kwh', 'e_chain_loss_kwh', 'e_dl_loss_kwh',
    'eng_kwh', 'eng_on_s', 'locked_s', 'bank_kwh',
    'over_rating_s', 'e_bus_kwh', 'eng_reject_kwh',
    'e_dir_wheel_kwh', 'emerg_s', 'unserved_kwh',
    'e_spin_shaft_kwh', 'e_spin_bus_kwh', 'above_pin_demand_s',
    'above_pin_demand_kwh', 'above_pin_engine_s',
    'above_pin_transitions', 'eng_stops', 'pack_chg_peak_kw',
    'pack_dis_peak_kw', 'pack_chg_over_r8_110kW_s',
    'pack_dis_over_r8_125kW_s', 'regen_shed_r16_kwh',
    'regen_bus_peak_kw', 'r8_dis_clip_s', 'r8_chg_clip_s',
    'r8_chg_shed_kwh', 'coast_no_regen_s',
    'coast_spin_shaft_kwh_r22d', 'coast_spin_bus_kwh_r22d',
    'l_per_100km', 'mean_bsfc_eff_g_per_kwh', 'soc_min',
    'soc_max', 'soc_end', 'starts_per_h',
    'above_pin_transitions_per_h', 'fuel_energy_kWh_per_km',
    'eng_on_frac')


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
            # R14 (adjudication KX-m3): the _max sibling, labelled too
            margin_pct_max_governing_case=(
                f"seed {REG_SEEDS[int(np.argmax(m))]} of 8-seed VOLT-REG "
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
    # KX r3 / adjudication KX2-m3: the ARCHIVED gate's raw reference-seed
    # dump used to be `everything the simulator returns`, so it gained 234
    # members the moment the KX r2 rework added diagnostics to the
    # simulator - including over-rating counters for mode (a), a mode the
    # block's own notice says exists in no live architecture, measured by
    # a counter that did not exist when the gate was run. An archived
    # record that mutates whenever the simulator gains a field is not
    # archived. The dump is now projected through the explicit member set
    # OF RECORD below, in the record's own key order, so the block is
    # frozen against every future simulator change.
    out["_raw_reference_seed"] = {
        md: {k: rows[23][md][k] for k in G1_RAW_KEYS_OF_RECORD}
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


def _DELTA_GOV(cfg):
    """R14 label for a one-factor delta_pp_min (adjudication KX-m3): the
    delta is a difference of two ensemble MINIMA, so both governing seeds
    are named."""
    return (f"difference of ensemble minima over the enumerated 8-seed "
            f"VOLT-REG set: row min at "
            f"{cfg['ensemble']['margin_pct_min_governing_case']} minus "
            f"prior-convention min at "
            f"{G1_PRIOR['ensemble']['margin_pct_min_governing_case']}")


# KX r3 / construction sweep (KX2-M3 family). The two attribution deltas
# are DIFFERENCES OF ENSEMBLE STATISTICS, not extrema of the paired
# per-seed delta. Their names say so (`delta_pp_min` = delta of the min)
# and `_DELTA_GOV` states it inline for the min; the median sibling
# carried no such statement, so it gets one here. The VALUES are
# BASELINE_v3-ratified record (-7.01 pp map-vs-scalar, -1.77 pp spin) and
# are NOT recomputed; the paired per-seed companion is measured and
# exported OUTSIDE this archived block, at
# results_ws4.json -> construction_sweep_kx_r3.
_DELTA_MEDIAN_CONSTRUCTION = (
    "difference of ensemble MEDIANS over the enumerated 8-seed VOLT-REG "
    "set (row median minus prior-convention median) - NOT the median of "
    "the paired per-seed deltas. Stated explicitly under the KX r3 "
    "construction sweep; the value is the BASELINE_v3-ratified record "
    "and is not recomputed. Paired companion: results_ws4.json -> "
    "construction_sweep_kx_r3 -> examined -> gate_g1_one_factor.")


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
        delta_pp_min_governing_case=_DELTA_GOV(G1_SPIN),
        delta_pp_median=G1_SPIN["ensemble"]["margin_pct_median"]
        - G1_PRIOR["ensemble"]["margin_pct_median"],
        delta_pp_median_construction=_DELTA_MEDIAN_CONSTRUCTION),
    map_vs_scalar_alone=dict(
        **_mrg(G1_MAPS),
        delta_pp_min=G1_MAPS["ensemble"]["margin_pct_min"]
        - G1_PRIOR["ensemble"]["margin_pct_min"],
        delta_pp_min_governing_case=_DELTA_GOV(G1_MAPS),
        delta_pp_median=G1_MAPS["ensemble"]["margin_pct_median"]
        - G1_PRIOR["ensemble"]["margin_pct_median"],
        delta_pp_median_construction=_DELTA_MEDIAN_CONSTRUCTION),
    both_g1r=dict(
        min=None, median=None))   # filled below once G1 nominal is final
R["gate_g1_one_factor"]["both_g1r"] = dict(
    **_mrg(G1["nominal"]),
    delta_pp_min=G1["nominal"]["ensemble"]["margin_pct_min"]
    - G1_PRIOR["ensemble"]["margin_pct_min"],
    delta_pp_min_governing_case=_DELTA_GOV(G1["nominal"]),
    delta_pp_median=G1["nominal"]["ensemble"]["margin_pct_median"]
    - G1_PRIOR["ensemble"]["margin_pct_median"],
    delta_pp_median_construction=_DELTA_MEDIAN_CONSTRUCTION)

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
    # KX r2 / adjudication KX-m2 (closes D5): the same strict criterion
    # evaluated by LINEAR INTERPOLATION of the feasible envelope between
    # bracketing rpm columns (the r3 adjudicator's implementation), and
    # the nearest-column count with the degenerate rpm = 0 column's
    # samples excluded. The gap between WS4's published count and the r3
    # adjudicator's is exactly that one column.
    ob_strict_lin = chain.boundary_exposure_strict_linear(rpm, trq) & drive
    deg = chain.nearest_col_is_degenerate(rpm)
    ob_strict_nodeg = ob_strict & ~deg
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
        exposure_s_motoring_strict_linear_envelope=float(
            ob_strict_lin.sum()) * dt,
        exposure_s_motoring_strict_excl_degenerate_rpm0_col=float(
            ob_strict_nodeg.sum()) * dt,
        exposure_s_motoring_strict_on_degenerate_rpm0_col=float(
            (ob_strict & deg).sum()) * dt,
        exposed_speed_kmh_max_strict_linear=(
            float((v * 3.6)[ob_strict_lin].max())
            if ob_strict_lin.any() else 0.0),
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
               "exposure_s_motoring_strict_linear_envelope",
               "exposure_s_motoring_strict_excl_degenerate_rpm0_col",
               "exposure_s_motoring_strict_on_degenerate_rpm0_col",
               "exposed_speed_kmh_max_strict_linear",
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
        # R14 (adjudication KX2-m2): the `_min` siblings were unlabelled
        # where the `_max` siblings in the same object were labelled.
        _env[_k + "_min_governing_case"] = (
            f"seed {REG_SEEDS[int(np.argmin(_vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{_case}]")
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
    # -------------------------------------------------------------------
    # KX r2 / adjudication KX-m2: D5 is CLOSED. The KX round disclosed
    # that its strict count (nearest rpm column) did not match the r3
    # adjudicator's (3.6-7.6 s at nominal) and declined to reconcile. The
    # reconciliation is arithmetic, and it is one map column.
    # -------------------------------------------------------------------
    d5_reconciliation=dict(
        status="CLOSED (was: disclosed as unreconciled, D5)",
        finding=("the entire gap is WS2's rpm = 0 map column. It has "
                 "exactly ONE feasible cell, at T = 0, so its feasible "
                 "torque envelope has ZERO WIDTH. Under the nearest-column "
                 "rule every motoring sample below 50 rpm - road speed "
                 "below 0.70 km/h, i.e. the instant of a standing start - "
                 "is tested against that zero-width envelope and flagged. "
                 "Evaluating the same envelope by LINEAR INTERPOLATION "
                 "between bracketing rpm columns, as the r3 adjudicator "
                 "did, removes the degeneracy and reproduces that "
                 "adjudicator's published counts."),
        degenerate_rpm_columns=[float(CHAIN.rpms[k])
                                for k in CHAIN.degenerate_rpm_columns()],
        degenerate_column_speed_ceiling_kmh=float(
            50.0 / CHAIN.ratio * CHAIN.r_dyn * 2 * np.pi / 60.0 * 3.6),
        counts_s_per_cycle={
            _c: dict(
                stencil_criterion_ws4_headline=[
                    _f2[_c]["envelope"]["exposure_s_motoring_min"],
                    _f2[_c]["envelope"]["exposure_s_motoring_max"]],
                strict_nearest_column=[
                    _f2[_c]["envelope"]["exposure_s_motoring_strict_min"],
                    _f2[_c]["envelope"]["exposure_s_motoring_strict_max"]],
                strict_linear_envelope_r3_adjudicator_criterion=[
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_linear_envelope_min"],
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_linear_envelope_max"]],
                strict_nearest_column_excl_rpm0=[
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_excl_"
                        "degenerate_rpm0_col_min"],
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_excl_"
                        "degenerate_rpm0_col_max"]],
                attributable_to_rpm0_column=[
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_on_"
                        "degenerate_rpm0_col_min"],
                    _f2[_c]["envelope"][
                        "exposure_s_motoring_strict_on_"
                        "degenerate_rpm0_col_max"]])
            for _c in ("nominal", "cda_5.4")},
        nothing_moves=("those samples book ZERO unbooked loss: "
                       "unbooked_bus_kWh_linear equals "
                       "unbooked_bus_kWh_linear_locked_only at nominal, "
                       "confirming the unlocked launch exposure "
                       "contributes nothing to the pp bound. Every "
                       "exported pp figure is unchanged by this "
                       "reconciliation; what changes is that the printed "
                       "exposure SECONDS are now stated with the "
                       "artefact separated out."),
        disclosure=("the KX round printed the stencil count as 'the "
                    "measured exposure' without saying that roughly four "
                    "fifths of the strict count is a boundary artefact of "
                    "the grid's first column. s4.1, F-9 and D5 now carry "
                    "both counts.")),
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
        # R14 (adjudication KX-m3): the _max sibling was unlabelled
        eta_bus_to_wheel_max_governing_case=(
            f"seed {REG_SEEDS[int(np.argmax(_sd_vals))]} of the enumerated "
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
# KX r2 / KX-B1: WS3's 10-s PULSE column. The previous round never
# consulted it; the adjudicator's point is that every measured pack-charge
# excursion is LONGER than the 10 s window it would excuse, so the pulse
# rating is the right column to state and the wrong one to hide behind.
R16_T_PULSE, R16_P_PULSE = load_r16_curve(
    os.path.join(WS3_DIR, "regen_acceptance.csv"),
    col="V2pack_chg_pulse10s_kW_bus")
COAST_SH_KW = float(WS2X["spin"]["point_check_shaft_drag_85kmh_W"]) / 1e3
COAST_BUS_KW = float(WS2X["spin"]["point_check_bus_draw_85kmh_W"]) / 1e3

# --- KX r2 / KX-M3: the payload denominator, exported as a first-class
# member with its basis and its caveat, never as a bare number. The
# denominator is IDENTICAL in all three ordered cases (all run at GVW),
# so the payload-denominated field is the per-km field divided by this
# constant and carries no information the per-km field does not.
PAYLOAD_T = VEH.m_payload_at_gvw / 1000.0
PAYLOAD_BASIS = dict(
    payload_basis_t=PAYLOAD_T,
    payload_basis_kg=VEH.m_payload_at_gvw,
    payload_basis_source=("WS1 volt_params.Vehicle: m_gvw 6,600 kg minus "
                          "m_curb_operating 3,700 kg [WS1-ASSUMPTION: "
                          "'NPR-HD chassis-cab + 16 ft dry-freight body + "
                          "driver + full fuel/DEF']"),
    payload_basis_is_preconversion=True,
    identical_in_all_ordered_cases=True,
    _caveat=("PRE-CONVERSION WS1 CURB. This denominator is the CONVENTIONAL "
             "truck's payload at GVW. It does NOT charge the series "
             "powertrain's mass (WS3 pack, WS4 genset + generator, WS2 "
             "spine, less the deleted engine and gearbox), and it is the "
             "same constant in all three ordered cases - so "
             "fuel_energy_kWh_per_payload_tonne_km is EXACTLY the per-km "
             "value divided by "
             f"{PAYLOAD_T:.1f} and carries no information the per-km field "
             "does not. It is NOT the R32 metric: R32's payload "
             "denomination exists precisely to charge conversion mass "
             "(D13/R36: 'won 6-10% per km and gave 6-8% back in freight'), "
             "and a denominator that does not charge it cannot discharge "
             "R32. Do not denominate any candidate comparison on this "
             "field. ESC-7 asks the lead to ratify a Vehicle Zero payload "
             "basis or hold R32 open; WS4 does not invent one."))

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
        # ---------------------------------------------------------------
        # KX r2 / adjudication KX-M2. The KX round carried the resolvable
        # chain of record ONLY inside interface_ws4 -> gate_g1, whose own
        # archival notice forbids consuming any of its fields. A consumer
        # obeying that notice could not resolve the map, voltage or
        # reduction the LIVE numbers were produced with. The chain is
        # duplicated here, WS4-relative, so the live block resolves on its
        # own; verify_ws4.py asserts that it does, without reading gate_g1.
        # ---------------------------------------------------------------
        chain_of_record=dict(
            map_file=R["ws2_chain_of_record"]["map_file_ws4_relative"],
            map_file_owner=R["ws2_chain_of_record"]["map_file_owner"],
            map_file_as_exported_by_owner=R["ws2_chain_of_record"][
                "map_file"],
            map_voltage_V=R["ws2_chain_of_record"]["map_voltage_V"],
            map_feasible_points=R["ws2_chain_of_record"][
                "map_feasible_points"],
            reduction_flat=R["ws2_chain_of_record"]["reduction_flat"],
            vintage=R["ws2_chain_of_record"]["vintage"],
            ws2_rework_round=R["ws2_chain_of_record"]["ws2_rework_round"],
            ws2_bus_nominal_V=R["ws2_chain_of_record"]["ws2_bus_nominal_V"],
            map_file_sha256=R["ws2_chain_of_record"]["input_sha256"][
                "map_file"],
            _note=("resolvable from THIS block. Duplicated from "
                   "results_ws4.json -> ws2_chain_of_record so that "
                   "series_duty_v2 does not depend on the ARCHIVED "
                   "gate_g1 block for its own chain (adjudication "
                   "KX-M2). Same map, same run, same numbers.")),
        boundary_convention_exposure=dict(
            _note=("the map-boundary convention described in the archived "
                   "gate's block is ACTIVE in this live run - same map, "
                   "same chain, same _interp_loss clamping - so its "
                   "measured exposure travels with the live block too "
                   "(adjudication KX-M2). Full tables in "
                   "results_ws4.json -> chain_boundary_exposure. The "
                   "linear-interpolation and rpm=0-excluded counts that "
                   "close D5 are there as well (adjudication KX-m2)."),
            definition=R["chain_boundary_exposure"]["definition"],
            cases={_c: dict(
                exposure_s_motoring_min=R["chain_boundary_exposure"][
                    "cases"][_c]["envelope"]["exposure_s_motoring_min"],
                # R14 (adjudication KX2-m2)
                exposure_s_motoring_min_governing_case=R[
                    "chain_boundary_exposure"]["cases"][_c]["envelope"][
                        "exposure_s_motoring_min_governing_case"],
                exposure_s_motoring_max=R["chain_boundary_exposure"][
                    "cases"][_c]["envelope"]["exposure_s_motoring_max"],
                exposure_s_motoring_max_governing_case=R[
                    "chain_boundary_exposure"]["cases"][_c]["envelope"][
                        "exposure_s_motoring_max_governing_case"],
                one_sided_pp_locked_linear_max=R["chain_boundary_exposure"][
                    "cases"][_c]["envelope"][
                        "one_sided_pp_locked_linear_max"],
                one_sided_pp_locked_linear_max_governing_case=R[
                    "chain_boundary_exposure"]["cases"][_c]["envelope"][
                        "one_sided_pp_locked_linear_max_governing_case"],
                total_pp_linear_max=R["chain_boundary_exposure"]["cases"][
                    _c]["envelope"]["total_pp_linear_max"],
                total_pp_linear_max_governing_case=R[
                    "chain_boundary_exposure"]["cases"][_c]["envelope"][
                        "total_pp_linear_max_governing_case"])
                for _c in ("nominal", "cda_5.4", "alt2000m_45C")},
            one_sided_note=("the one-sided pp figure prices the LOCKED "
                            "share, which exists only in the archived "
                            "mode (a). In this pure-series block no "
                            "sample is locked, so the relevant figure for "
                            "series_duty_v2 is total_pp_linear_max - the "
                            "whole unbooked bound, which is what a "
                            "pure-series fuel number is exposed to.")),
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
        # KX r2 / adjudication KX-M3: the payload denominator, its basis
        # and its caveat travel WITH the JSON, not only in report prose.
        payload_metric_basis=PAYLOAD_BASIS,
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
           # KX r2 / KX-B1: the R16 curve read as a PACK charge limit
           "pack_chg_above_r16_accept_s", "pack_chg_above_r16_accept_kWh",
           "pack_chg_above_r16_accept_longest_s",
           "r16_pack_cap_shed_kWh", "r16_pack_cap_clip_s",
           # KX r2 / KX-M1: the genset's own continuous rating
           "engine_over_continuous_rating_s",
           "engine_over_continuous_rating_kWh",
           "engine_over_continuous_rating_longest_s",
           "engine_shaft_peak_kW", "generator_over_continuous_input_s",
           "generator_shaft_input_peak_kW",
           # KX r2 / KX-m7: transient heat for the WS6 ledger
           "engine_reject_peak_kW", "engine_reject_2min_max_kW",
           "engine_reject_10min_max_kW",
           "mean_bsfc_eff_g_per_kWh", "engine_reject_kWh",
           "generator_loss_kWh", "chain_loss_kWh", "friction_brake_kWh",
           "bus_energy_kWh", "engine_reject_avg_kW",
           "generator_loss_avg_kW", "chain_loss_avg_kW")


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
        # KX r2 / KX-B1: WS3's R16 acceptance tested against the PACK's
        # total bus-side charge power (regen AND genset), not only the
        # regen leg the simulator caps.
        pack_chg_above_r16_accept_s=o["pack_chg_above_r16_s"],
        pack_chg_above_r16_accept_kWh=o["pack_chg_above_r16_kwh"],
        pack_chg_above_r16_accept_longest_s=o["pack_chg_above_r16_longest_s"],
        r16_pack_cap_shed_kWh=o["r16_pack_shed_kwh"],
        r16_pack_cap_clip_s=o["r16_pack_clip_s"],
        # KX r2 / KX-M1: the 132 kW continuous flat-rating this
        # workstream owns, x the case derate.
        engine_over_continuous_rating_s=o["eng_over_cont_s"],
        engine_over_continuous_rating_kWh=o["eng_over_cont_kwh"],
        engine_over_continuous_rating_longest_s=o["eng_over_cont_longest_s"],
        engine_shaft_peak_kW=o["eng_shaft_peak_kw"],
        generator_over_continuous_input_s=o["gen_shaft_in_over_cont_s"],
        generator_shaft_input_peak_kW=o["gen_shaft_in_peak_kw"],
        # KX r2 / KX-m7: transient rejection for the WS6 ledger
        engine_reject_peak_kW=o["eng_reject_peak_kw"],
        engine_reject_2min_max_kW=o["eng_reject_roll120s_max_kw"],
        engine_reject_10min_max_kW=o["eng_reject_roll600s_max_kw"],
        mean_bsfc_eff_g_per_kWh=o["mean_bsfc_eff_g_per_kwh"],
        engine_reject_kWh=o["eng_reject_kwh"],
        generator_loss_kWh=o["e_gen_loss_kwh"],
        chain_loss_kWh=o["e_chain_loss_kwh"],
        friction_brake_kWh=o["e_fric_kwh"],
        bus_energy_kWh=o["e_bus_kwh"],
        # KX r2 / KX-m6: THIS seed's own cycle averages. Each ledger row
        # must be the max of these per component, not max(energy) divided
        # by one seed's duration - and each component's governing seed is
        # its own.
        engine_reject_avg_kW=o["eng_reject_kwh"] / (o["duration_s"] / 3600.0),
        generator_loss_avg_kW=o["e_gen_loss_kwh"] / (o["duration_s"] / 3600.0),
        chain_loss_avg_kW=o["e_chain_loss_kwh"] / (o["duration_s"] / 3600.0))


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


# ---------------------------------------------------------------------------
# KX r3 / adjudication KX2-M1, KX2-M3, KX2-m1 - CONSTRUCTION HELPERS.
#
# Two defect families were re-introduced by the KX r2 rework and are
# closed here at source, for every field in the workstream rather than
# one field at a time:
#
#   (1) An aggregate whose NAME asserts one construction and whose CODE
#       performs another - a "max" built from two independently maximised
#       numbers, a "paired median" built as a ratio of medians, a "max
#       over the case set" filtered down to one case. BASELINE_v5 R36 is
#       on the record precisely because a ratio-of-statistics artefact
#       reached doctrine once already: per-km claims are stated on the
#       PAIRED statistic only. `_paired_pct_delta` below is the only
#       sanctioned way to state a delta between two dispatches in this
#       pipeline.
#   (2) A degenerate extremum labelled with Python's first-key tie-break
#       as though it were a governing case. `_case_worst` refuses to.
# ---------------------------------------------------------------------------
def _case_set_str(cases):
    return "{" + ", ".join(cases) + "}"


def _case_worst(vals, kind="max", gov_by_case=None, case_order=None,
                zero_is_degenerate=True,
                degenerate_zero_label=("no governing case - every ordered "
                                       "case is exactly zero on all 8 seeds"),
                set_name="enumerated ordered case set"):
    """R14 min/max over an ENUMERATED case set, with an honest label.

    Returns (value, label). When every case carries exactly the same
    value the label refuses to name a governing case (adjudication
    KX2-m1: `max(cases, key=...)` over three exact zeros is a first-key
    tie-break, not a measurement); when a strict subset ties, the label
    says so and names them all.
    """
    order = list(case_order if case_order is not None else vals)
    best = max(vals[c] for c in order) if kind == "max" \
        else min(vals[c] for c in order)
    tied = [c for c in order if vals[c] == best]
    cs = _case_set_str(order)
    if len(tied) == len(order):
        if zero_is_degenerate and best == 0.0:
            # the exact degenerate-tie wording `unserved_energy_verdict`
            # already used and round 1 accepted as the right form
            return best, degenerate_zero_label
        return best, (f"no governing case - every case of the {set_name} "
                      f"{cs} is exactly {best:.6g}")
    if len(tied) > 1:
        inner = ("; within them, " + " / ".join(
            f"{c}: {gov_by_case[c]}" for c in tied)) if gov_by_case else ""
        return best, (f"tied at {best:.6g} across cases "
                      f"{_case_set_str(tied)} of the {set_name} "
                      f"{cs}{inner}")
    inner = f"; within it, {gov_by_case[tied[0]]}" if gov_by_case else ""
    return best, (f"case {tied[0]} of the {set_name} {cs}{inner}")


def _paired_pct_delta(alt_cases, base_cases, key, cases, alt_label,
                      base_label, unit_note=""):
    """BASELINE_v5 R36 / adjudication KX2-M3: the PAIRED per-seed
    percentage delta of `key` between two dispatches.

    The two ensembles are paired by construction - same seeds, same
    cycles, same everything but the supervisor - so the paired per-seed
    delta is available at zero cost and is the statistic the program
    requires. A ratio of ensemble statistics (median/median, max/max) is
    a DIFFERENT quantity: at nominal the r2 companion's ratio of medians
    was 2.7x smaller than the median of the paired deltas, and the r2
    R16 bracket's ratio of maxima had the OPPOSITE SIGN to six of its
    eight paired seeds.

    Exports, per case: the eight paired deltas, their min/median/max with
    R14 governing SEEDS, and the sign split; then the worst over the
    enumerated case set with the governing case AND seed inline.
    """
    by_case = {}
    for c in cases:
        vals, dists = [], []
        for sd in REG_SEEDS:
            b = base_cases[c]["per_seed"][str(sd)]
            a = alt_cases[c]["per_seed"][str(sd)]
            # the two runs share the seed's cycle, so distance is
            # identical and a per-km delta is a fuel-mass delta
            dists.append(abs(a["distance_km"] - b["distance_km"]))
            vals.append(100.0 * (a[key] - b[key]) / b[key])
        assert max(dists) < 1e-9, \
            f"paired delta on {key}: {c} distances differ ({max(dists)})"
        by_case[c] = dict(
            per_seed={str(sd): v for sd, v in zip(REG_SEEDS, vals)},
            min=min(vals), median=float(np.median(vals)), max=max(vals),
            min_governing_case=(
                f"seed {REG_SEEDS[int(np.argmin(vals))]} of the enumerated "
                f"8-seed VOLT-REG ensemble [{c}]"),
            max_governing_case=(
                f"seed {REG_SEEDS[int(np.argmax(vals))]} of the enumerated "
                f"8-seed VOLT-REG ensemble [{c}]"),
            seeds_positive_n=int(sum(1 for v in vals if v > 0.0)),
            seeds_total=len(vals))
    wmax, wmax_gov = _case_worst(
        {c: by_case[c]["max"] for c in cases}, "max",
        {c: by_case[c]["max_governing_case"] for c in cases}, cases,
        zero_is_degenerate=False)
    wmin, wmin_gov = _case_worst(
        {c: by_case[c]["min"] for c in cases}, "min",
        {c: by_case[c]["min_governing_case"] for c in cases}, cases,
        zero_is_degenerate=False)
    return dict(
        _statistic=(f"PAIRED per-seed percentage delta of `{key}`: "
                    f"100 x ({alt_label} - {base_label}) / {base_label}, "
                    f"formed SEED BY SEED on the same enumerated 8-seed "
                    f"VOLT-REG ensemble and only then enveloped "
                    f"(BASELINE_v5 R36; adjudication KX2-M3). "
                    f"{unit_note}").strip(),
        by_case=by_case,
        worst_max_pct=wmax, worst_max_pct_governing_case=wmax_gov,
        worst_min_pct=wmin, worst_min_pct_governing_case=wmin_gov,
        seeds_positive_n_by_case={c: by_case[c]["seeds_positive_n"]
                                  for c in cases},
        seeds_total_per_case=len(REG_SEEDS))


# KX r2 / adjudication KX-m4: R34's "one per run" is ambiguous between
# per PIPELINE run and per SIMULATED run. WS4 declares the reading below
# and, rather than leave the gap, emits a full-rate 10 Hz trace for EVERY
# ORDERED CASE at the reference seed (3 files) instead of one. Emitting
# all 24 ordered mode-(b) runs at 10 Hz would be ~132 MB of committed
# artefact; R34_TRACE_ALL_ORDERED_RUNS below makes that a one-constant
# change if the lead rules for the per-simulated-run reading.
R34_TRACE_ALL_ORDERED_RUNS = False
R34_TRACE_SEEDS = REG_SEEDS if R34_TRACE_ALL_ORDERED_RUNS else [23]
_SD_TRACES = {}
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
                trace=(md == "b" and sd in R34_TRACE_SEEDS),
                soc_trace_stride=(50 if md == "b" else None))
            if md == "b":
                if _pin_case is None:
                    _pin_case = _o["pinned"]
                if "trace" in _o:
                    _SD_TRACES[(_case, sd)] = _o.pop("trace")
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

# ---------------------------------------------------------------------------
# KX r2 / adjudication KX-B2. The KX round compared (b) and (b') on fuel,
# starts and unserved energy only - none of the three capability axes on
# which R22b and ESC-9 are actually decided, and two of which are the whole
# substance of ESC-9. Measured, (b') satisfies every envelope (b) violates.
# WS4 still does NOT choose the dispatch (R22b assigns that to WS5); it
# reports that its own companion answers the question ESC-9 asks.
# ---------------------------------------------------------------------------
ENG_CONT_KW_BY_CASE = {c: ENG_V2.rated_cont_kw * cfg["derate"]
                       for c, cfg in KX_CASES.items()}


def _axis(key, limit, limit_label):
    """One capability axis, mode (b) vs mode (b'), as an R14 max over the
    enumerated 3-case x 8-seed set with the governing case inline.
    limit=None -> informational row, no compliance verdict."""
    def _m(which):
        def env(c):
            return (SD["cases"][c]["ensemble"] if which == "b"
                    else SD["cases"][c]["companion_bp"]["ensemble"])
        vals = {c: env(c)[key + "_max"] for c in KX_CASES}
        worst = max(vals, key=lambda c: vals[c])
        return dict(
            per_case_max=vals,
            worst_case_max=vals[worst],
            worst_case_max_governing_case=(
                f"case {worst} of the enumerated ordered case set "
                f"{{{', '.join(KX_CASES)}}}; within it, "
                f"{env(worst)[key + '_max_governing_case']}"),
            within_limit_on_every_ordered_seed=(
                None if limit is None else bool(vals[worst] <= limit)))
    return dict(limit=limit, limit_label=limit_label,
                mode_b_block_of_record=_m("b"),
                mode_bp_companion=_m("bp"))


# KX r3 / adjudication KX2-M3(a). The KX r2 block exported
# `bp_penalty_pct_on_median` - a RATIO OF ENSEMBLE MEDIANS - and the
# report rendered it three times, including in ESC-9, as "on the paired
# per-case median". BASELINE_v5 R36 exists because exactly that artefact
# reached doctrine once. The paired statistic is computed here; the
# ratio-of-medians is retained beside it under a name that says what it
# is, so nothing previously reported is dropped.
# KX r3 / CONSTRUCTION SWEEP. The report rendered "peak shaft X kW = Y %
# of the continuous rating" (ESC-10) as a max over ALL cases divided by
# ONE case's rating. It happens to be right here only because the peak's
# governing cases are the two undereated ones; at the corner the rating
# is derated and the same arithmetic would be wrong. The ratio is now
# formed PER CASE PER SEED against that case's own derated rating, then
# enveloped (R14).
_ENG_PCT = {}
for _c in KX_CASES:
    _rate = ENG_CONT_KW_BY_CASE[_c]
    _v = [100.0 * SD["cases"][_c]["per_seed"][str(_sd)]["engine_shaft_peak_kW"]
          / _rate for _sd in REG_SEEDS]
    _ENG_PCT[_c] = dict(
        continuous_rating_kW=_rate,
        min=min(_v), median=float(np.median(_v)), max=max(_v),
        max_governing_case=(
            f"seed {REG_SEEDS[int(np.argmax(_v))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{_c}]"))
_eng_pct_worst, _eng_pct_worst_gov = _case_worst(
    {c: _ENG_PCT[c]["max"] for c in KX_CASES}, "max",
    {c: _ENG_PCT[c]["max_governing_case"] for c in KX_CASES},
    list(KX_CASES), zero_is_degenerate=False)

_BP_PAIRED = _paired_pct_delta(
    {c: SD["cases"][c]["companion_bp"] for c in KX_CASES},
    {c: SD["cases"][c] for c in KX_CASES},
    "fuel_energy_kWh_per_km", list(KX_CASES),
    "mode (b') load-following companion", "mode (b) block of record",
    "Positive = the companion burns MORE than the pinned mode of record.")

SD["companion_bp_capability_comparison"] = dict(
    ruling="R22b (WS5 owns the dispatch choice) / ESC-9 / KX-B2",
    _status=("MEASUREMENT, NOT A RECOMMENDATION. WS4 does not choose "
             "between (b) and (b'); R22b assigns that to WS5. What the KX "
             "round failed to report is that its own load-following "
             "companion satisfies R8's bus-side envelope, WS3's R16 "
             "acceptance read on the pack, and the engine's own continuous "
             "flat-rating - on every seed of every ordered case - where the "
             "pinned mode of record violates all three. ESC-9 asks the lead "
             "to choose between remedies; one of them is already measured "
             "here, at the fuel deltas in fuel_kWh_per_km_by_case - which "
             "are stated on the PAIRED per-seed statistic BASELINE_v5 R36 "
             "mandates (fuel_delta_paired), not on a ratio of ensemble "
             "statistics."),
    axes=dict(
        pack_discharge_peak_kW_bus=_axis(
            "pack_dis_peak_kW", 125.0,
            "R8 bus-side discharge envelope as restated by R12/ES-4"),
        pack_charge_peak_kW_bus=_axis(
            "pack_chg_peak_kW", 110.0, "R8 bus-side charge envelope"),
        pack_charge_above_r16_accept_s=_axis(
            "pack_chg_above_r16_accept_s", 0.0,
            "WS3 R16 continuous charge acceptance at the declared cells, "
            "read as a PACK limit (KX-B1)"),
        engine_over_continuous_rating_s=_axis(
            "engine_over_continuous_rating_s", 0.0,
            "the 4HK1-V2C 132 kW continuous flat-rating x the case derate "
            "(KX-M1)"),
        engine_shaft_peak_kW=_axis(
            "engine_shaft_peak_kW", None,
            "informational: compare per case against "
            "engine_continuous_rating_kW_by_case below; the compliance "
            "verdict is the derate-aware seconds row above")),
    engine_continuous_rating_kW_by_case=ENG_CONT_KW_BY_CASE,
    # KX r3 / construction sweep: per case, per seed, against THAT case's
    # own derated rating - not a cross-case max over one case's rating.
    engine_shaft_peak_pct_of_continuous_rating_by_case=_ENG_PCT,
    engine_shaft_peak_pct_of_continuous_rating_worst=_eng_pct_worst,
    engine_shaft_peak_pct_of_continuous_rating_worst_governing_case=(
        _eng_pct_worst_gov),
    engine_automotive_peak_kW=ENG_V2.peak_power_kw(),
    generator_continuous_shaft_input_kW=GEN_V2.cont_kw_in,
    r16_accept_kW_bus_by_case=_ACCEPT,
    fuel_kWh_per_km_by_case={
        c: dict(mode_b=[SD["cases"][c]["ensemble"][
                    "fuel_energy_kWh_per_km_min"],
                    SD["cases"][c]["ensemble"]["fuel_energy_kWh_per_km_max"]],
                mode_bp=[SD["cases"][c]["companion_bp"]["ensemble"][
                    "fuel_energy_kWh_per_km_min"],
                    SD["cases"][c]["companion_bp"]["ensemble"][
                        "fuel_energy_kWh_per_km_max"]],
                # --- the statistic R36 requires: PAIRED, per seed
                bp_fuel_delta_pct_paired_min=_BP_PAIRED["by_case"][c]["min"],
                bp_fuel_delta_pct_paired_median=_BP_PAIRED["by_case"][c][
                    "median"],
                bp_fuel_delta_pct_paired_max=_BP_PAIRED["by_case"][c]["max"],
                bp_fuel_delta_pct_paired_min_governing_case=_BP_PAIRED[
                    "by_case"][c]["min_governing_case"],
                bp_fuel_delta_pct_paired_max_governing_case=_BP_PAIRED[
                    "by_case"][c]["max_governing_case"],
                bp_fuel_delta_pct_paired_seeds_positive_n=_BP_PAIRED[
                    "by_case"][c]["seeds_positive_n"],
                # --- the KX r2 field, retained under an honest name
                bp_penalty_pct_ratio_of_ensemble_medians=100.0 * (
                    SD["cases"][c]["companion_bp"]["ensemble"][
                        "fuel_energy_kWh_per_km_median"]
                    - SD["cases"][c]["ensemble"][
                        "fuel_energy_kWh_per_km_median"])
                / SD["cases"][c]["ensemble"]["fuel_energy_kWh_per_km_median"],
                _superseded_field=(
                    "KX r2 exported the line above as "
                    "`bp_penalty_pct_on_median` and rendered it as 'the "
                    "paired per-case median'. It is a ratio of ensemble "
                    "medians, which is a different quantity: withdrawn "
                    "under that name (adjudication KX2-M3(a)); consume "
                    "bp_fuel_delta_pct_paired_*."))
        for c in KX_CASES},
    fuel_delta_paired=_BP_PAIRED,
    genset_starts_by_case={
        c: dict(mode_b=[SD["cases"][c]["ensemble"]["genset_starts_min"],
                        SD["cases"][c]["ensemble"]["genset_starts_max"]],
                mode_bp=[SD["cases"][c]["companion_bp"]["ensemble"][
                    "genset_starts_min"],
                    SD["cases"][c]["companion_bp"]["ensemble"][
                        "genset_starts_max"]])
        for c in KX_CASES},
    reading=("on the three capability axes above, the load-following "
             "companion is inside every limit on every ordered seed and "
             "the pinned mode of record is outside all three. The fuel "
             "cost of that, on the PAIRED per-seed delta (R36), is inside "
             "the ensemble spread at nominal and at CdA 5.4 and about the "
             "corner penalty above at alt2000m_45C. This is one endpoint "
             "of R22b's question "
             "measured on the same trace as the other, which is what the "
             "companion exists for. It is not a WS4 recommendation and it "
             "does not price the axes R22b must also weigh - start "
             "transients, emissions aftertreatment temperature, engine "
             "duty at part load - none of which this run models."))

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
        # R14 (KX r3 construction sweep): the `_min` sibling was unlabelled
        t_below_gate_s_min_governing_case=(
            f"seed {REG_SEEDS[min(range(len(rows)), key=lambda i: rows[i][0])]}"
            f" of the enumerated 8-seed VOLT-REG ensemble [{c}]"),
        t_below_gate_s_max=max(r[0] for r in rows),
        t_below_gate_s_max_governing_case=(
            f"seed {REG_SEEDS[max(range(len(rows)), key=lambda i: rows[i][0])]}"
            f" of the enumerated 8-seed VOLT-REG ensemble [{c}]"),
        soc_usable_min=min(r[1] for r in rows),
        soc_usable_min_governing_case=(
            f"seed {REG_SEEDS[min(range(len(rows)), key=lambda i: rows[i][1])]}"
            f" of the enumerated 8-seed VOLT-REG ensemble [{c}]"),
        soc_nameplate_min=min(r[2] for r in rows),
        soc_nameplate_min_governing_case=(
            f"seed {REG_SEEDS[min(range(len(rows)), key=lambda i: rows[i][2])]}"
            f" of the enumerated 8-seed VOLT-REG ensemble [{c}]"),
        # KX r3 / adjudication note 5 for the lead: soc_usable_min here is
        # measured off the 5 s decimated trajectory this block declares,
        # while cases[*].ensemble.soc_min_min is the same quantity at the
        # full 10 Hz rate. They differ by 0.0002-0.0004 of usable; both
        # are exported and neither is a different SOC.
        soc_usable_min_sampling_note=(
            "computed on the 5 s decimated SOC trajectory declared by "
            "`resolution_s` above. The full-rate value of the SAME "
            "quantity is series_duty_v2 -> cases -> "
            f"{c} -> ensemble -> soc_min_min "
            f"({SD['cases'][c]['ensemble']['soc_min_min']:.6f})."))
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
_pk_pack_chg = max(SD["cases"][c]["ensemble"]["pack_chg_peak_kW_max"]
                   for c in KX_CASES)
_cold_mask = R16_T <= 10.0
_hot_mask = R16_T >= 45.0


def _r16_case_env(key, fmt_case=True):
    """min/max/governing over the enumerated 3-case x 8-seed set.

    KX r3 / adjudication KX2-m2 + construction sweep: the `_min` siblings
    now carry their R14 governing seeds too, and the worst-case label is
    produced by `_case_worst`, so a degenerate tie cannot be presented as
    a governing case.
    """
    e = {c: SD["cases"][c]["ensemble"] for c in KX_CASES}
    wmax, wmax_gov = _case_worst(
        {c: e[c][key + "_max"] for c in KX_CASES}, "max",
        {c: e[c][key + "_max_governing_case"] for c in KX_CASES},
        list(KX_CASES))
    wmin, wmin_gov = _case_worst(
        {c: e[c][key + "_min"] for c in KX_CASES}, "min",
        {c: e[c][key + "_min_governing_case"] for c in KX_CASES},
        list(KX_CASES))
    return dict(per_case_min={c: e[c][key + "_min"] for c in KX_CASES},
                per_case_min_governing_case={
                    c: e[c][key + "_min_governing_case"] for c in KX_CASES},
                per_case_max={c: e[c][key + "_max"] for c in KX_CASES},
                per_case_max_governing_case={
                    c: e[c][key + "_max_governing_case"] for c in KX_CASES},
                worst_case_max=wmax,
                worst_case_max_governing_case=wmax_gov,
                mildest_case_min=wmin,
                mildest_case_min_governing_case=wmin_gov)


_pack_bound = bool(max(SD["cases"][c]["ensemble"][
    "pack_chg_above_r16_accept_s_max"] for c in KX_CASES) > 0.0)
_pack_bound_every_seed = bool(min(SD["cases"][c]["ensemble"][
    "pack_chg_above_r16_accept_s_min"] for c in KX_CASES) > 0.0)


def _r16_crossing(target, t_branch, p_branch, what):
    """np.interp against a MONOTONE branch of WS3's acceptance curve -
    but only where a crossing genuinely exists.

    KX r3 / adjudication KX2-M2. `np.interp` CLAMPS outside its range and
    returns the branch's own end abscissa. KX r2 exported one such clamp
    (`cold_side_binding_cell_C_pack_quantity = 10.0`) beside two genuine
    crossings, so a consumer read a non-binding region above 10 C cells
    that does not exist. A clamp and a crossing must not share a field
    name: this asserts the target is inside the branch's range before
    interpolating, and returns None when it is not, forcing the caller to
    export the measured statement instead.
    """
    lo, hi = float(np.min(p_branch)), float(np.max(p_branch))
    if not (lo <= target <= hi):
        return None
    order = np.argsort(p_branch)
    return float(np.interp(target, np.asarray(p_branch)[order],
                           np.asarray(t_branch)[order]))


# --- KX r3 / adjudication KX2-M2: the PACK quantity has no crossing on
# either side. WS3's continuous column peaks at its global maximum below
# the ordered run's peak pack charge, so the constraint is exceeded at
# EVERY tabulated cell temperature. That sentence - not a clamped
# interpolation - is the decision-relevant fact for ESC-8.
_R16_CURVE_MAX = float(np.max(R16_P))
_R16_CURVE_MAX_T = float(R16_T[int(np.argmax(R16_P))])
_R16_PULSE_MAX = float(np.max(R16_P_PULSE))
_R16_PULSE_MAX_T = float(R16_T_PULSE[int(np.argmax(R16_P_PULSE))])
_pulse_ok = R16_P_PULSE >= _pk_pack_chg
_PACK_BINDING = dict(
    _statement=("on the PACK quantity the ordered duty's peak charge "
                "EXCEEDS WS3's continuous acceptance at EVERY tabulated "
                "cell temperature WS3 publishes. There is no cold-side "
                "boundary, no hot-side boundary and no non-binding "
                "window - which is why no *_binding_cell_C field is "
                "exported for this quantity (adjudication KX2-M2)."),
    peak_pack_charge_kW_bus=_pk_pack_chg,
    acceptance_curve_max_kW_bus=_R16_CURVE_MAX,
    acceptance_curve_max_at_cell_C=_R16_CURVE_MAX_T,
    least_binding_cell_C=_R16_CURVE_MAX_T,
    least_binding_cell_C_meaning=(
        "the cell temperature at which WS3's CONTINUOUS acceptance column "
        "attains its MAXIMUM, i.e. the most favourable point on the "
        "curve. It is NOT a boundary and NOT a crossing."),
    min_exceedance_kW_over_the_curve=_pk_pack_chg - _R16_CURVE_MAX,
    exceeds_acceptance_at_every_tabulated_cell_C=bool(
        _pk_pack_chg > _R16_CURVE_MAX),
    n_tabulated_cells=int(R16_T.size),
    tabulated_cell_C_min=float(np.min(R16_T)),
    tabulated_cell_C_max=float(np.max(R16_T)),
    cold_side_crossing_exists=False,
    hot_side_crossing_exists=False,
    pulse10s_max_kW_bus=_R16_PULSE_MAX,
    pulse10s_max_at_cell_C=_R16_PULSE_MAX_T,
    pulse10s_covers_peak_between_cell_C=[float(R16_T_PULSE[_pulse_ok].min()),
                                         float(R16_T_PULSE[_pulse_ok].max())],
    pulse10s_note=("the 10-s PULSE column DOES cover the peak magnitude "
                   "over the cell range above; `pulse10s_covers_the_"
                   "excursions` is False on excursion DURATION, not on "
                   "magnitude, and that distinction is correct."),
    _superseded_field=dict(
        name="cold_side_binding_cell_C_pack_quantity",
        kx_r2_value=10.0,
        why_withdrawn=(
            "computed as np.interp(peak_pack_charge, cold branch) with "
            "the peak ABOVE the branch's right edge, so np.interp clamped "
            "and returned the branch's last abscissa. It was not a "
            "crossing; there is none. Exported beside two genuine "
            "crossings, it read as a non-binding region above 10 C cells "
            "(adjudication KX2-M2).")))
SD["r16_binding_analysis"] = dict(
    ruling="R16 (regen_acceptance.csv is the interface of record)",
    # ---------------------------------------------------------------
    # KX r2 / adjudication KX-B1. The previous round exported a single
    # `bound_any_sample: false`. That field answered the REGEN-LEG
    # question and was read as answering the PACK question. Both are now
    # exported, each under a name that says which one it is.
    # ---------------------------------------------------------------
    _two_readings=(
        "WS3's regen_acceptance.csv admits two readings and they differ "
        "MEASURABLY on this duty. (1) REGEN-LEG rule: WS3's REPORT_WS3 "
        "s4.2 presents the curve to WS5 as a regen-blend rule ('regen "
        "follows the acceptance curve at all temperatures with the "
        "resistor as overflow'; 'WS5 should drive the blend from it "
        "directly'). Under that reading the simulator's regen-leg cap is "
        "correct and nothing binds. (2) PACK rule: the file's own header "
        "is 'pack regen-acceptance vs cell temperature' and the column is "
        "V2pack_chg_cont_kW_bus - a PACK charge limit, bus-side. A pack "
        "cannot tell whether its charge current comes from regen or from "
        "the genset. Under that reading the constraint is ACTIVE on every "
        "ordered case, because the genset is on for 0.482-0.685 of cycle "
        "time across the ordered cases and its p_gen_elec is added to the "
        "pack AFTER the regen cap "
        "(ws4_sim.run_g1_mode: the cap sits inside the pw < 0 regen "
        "branch; p_batt_bus = p_gen_elec - p_bus_load is formed "
        "afterwards). The KX round chose reading (1) without recording "
        "that a choice existed. WS4 does not choose between them now "
        "either - the physical quantity the curve names is the pack's and "
        "the conservative reading is the pack one, but the semantics of "
        "WS3's interface are WS3's and the blend order is WS5's. Both are "
        "measured below and the enforcement cost is bracketed; ESC-8 puts "
        "the choice to the lead."),
    # --- reading (1): the regen leg, which is what the run enforces
    regen_leg_bound_any_sample=bool(max(
        SD["cases"][c]["ensemble"]["regen_shed_by_r16_kWh_max"]
        for c in KX_CASES) > 1e-12),
    regen_leg_enforced_in_ordered_run=True,
    peak_regen_to_pack_kW_bus=_pk_regen,
    # KX r3 / adjudication KX2-m2: these two named a CASE only, where the
    # same block's other worst-case fields use the program's fuller form.
    peak_regen_governing_case=_case_worst(
        {c: SD["cases"][c]["ensemble"]["regen_bus_peak_kW_max"]
         for c in KX_CASES}, "max",
        {c: SD["cases"][c]["ensemble"]["regen_bus_peak_kW_max_governing_case"]
         for c in KX_CASES}, list(KX_CASES))[1],
    # --- reading (2): the pack, which is what the run VIOLATES
    pack_charge_bound_by_r16_any_sample=_pack_bound,
    # KX r3 / construction sweep: `any_sample` is a max>0 over the set and
    # is correctly named, but the stronger measured statement - the
    # exceedance is nonzero on EVERY seed of EVERY ordered case - is the
    # one ESC-8 turns on, so it is exported explicitly as a min>0.
    pack_charge_bound_on_every_ordered_seed=_pack_bound_every_seed,
    pack_charge_enforced_in_ordered_run=False,
    peak_pack_charge_kW_bus=_pk_pack_chg,
    peak_pack_charge_governing_case=_case_worst(
        {c: SD["cases"][c]["ensemble"]["pack_chg_peak_kW_max"]
         for c in KX_CASES}, "max",
        {c: SD["cases"][c]["ensemble"]["pack_chg_peak_kW_max_governing_case"]
         for c in KX_CASES}, list(KX_CASES))[1],
    pack_charge_above_r16_accept_s=_r16_case_env(
        "pack_chg_above_r16_accept_s"),
    pack_charge_above_r16_accept_kWh=_r16_case_env(
        "pack_chg_above_r16_accept_kWh"),
    pack_charge_above_r16_accept_longest_s=_r16_case_env(
        "pack_chg_above_r16_accept_longest_s"),
    accept_kW_bus_at_declared_cells=_ACCEPT,
    # --- the pulse column, consulted (KX-B1: it does not excuse these)
    pulse10s_column="V2pack_chg_pulse10s_kW_bus",
    pulse10s_kW_bus_at_declared_cells={
        k: float(np.interp(c["t_cell_C"], R16_T_PULSE, R16_P_PULSE))
        for k, c in KX_CASES.items()},
    pulse10s_window_s=10.0,
    pulse10s_covers_the_excursions=bool(max(
        SD["cases"][c]["ensemble"]["pack_chg_above_r16_accept_longest_s_max"]
        for c in KX_CASES) <= 10.0),
    pulse10s_note=("WS3's 10-s pulse column rates 204.173 kW at 25 C and "
                   "200.553 kW at 45 C cells, both above this run's "
                   "147.6 kW pack-charge peak - but EVERY measured "
                   "excursion above the CONTINUOUS acceptance is longer "
                   "than the 10 s window that column rates (longest "
                   "single excursions above), so the pulse rating does not "
                   "cover them. Stated because the previous round never "
                   "consulted this column."),
    # --- the hot end, on the PACK quantity (KX-B1 re-scopes ESC-8)
    cold_side_binding_cell_C=_r16_crossing(
        _pk_regen, R16_T[_cold_mask], R16_P[_cold_mask], "regen/cold"),
    hot_side_binding_cell_C=_r16_crossing(
        _pk_regen, R16_T[_hot_mask], R16_P[_hot_mask], "regen/hot"),
    # KX r3 / adjudication KX2-M2: the pack quantity has NO crossing.
    pack_quantity_binding_analysis=_PACK_BINDING,
    accept_at_ws3_loop_ceiling_55C_kW=float(np.interp(55.0, R16_T, R16_P)),
    accept_at_50C_kW=float(np.interp(50.0, R16_T, R16_P)),
    pulse10s_at_ws3_loop_ceiling_55C_kW=float(
        np.interp(55.0, R16_T_PULSE, R16_P_PULSE)),
    pulse10s_at_50C_kW=float(np.interp(50.0, R16_T_PULSE, R16_P_PULSE)),
    esc8_scope_note=("ESC-8 was raised in the KX round on the peak REGEN "
                     "quantity (69.1 kW bus vs 62.2 kW continuous "
                     "acceptance at 55 C cells). On the PACK quantity the "
                     "hot end is far worse and the case is roughly twice "
                     "as large: at the 45 C declared cells the ordered run "
                     "already charges at 147.5 kW against 129.1 kW "
                     "continuous; at 50 C the continuous curve falls to "
                     "95.0 kW; and at WS3's 55 C loop ceiling even the "
                     "10-s PULSE rating (128.8 kW) sits below the run's "
                     "147.6 kW peak. ESC-8 is restated on the pack "
                     "quantity in s12. KX r3 (adjudication KX2-M2) adds "
                     "the single most decision-relevant sentence, which "
                     "was missing from both prior rounds: the curve's "
                     "CONTINUOUS column peaks BELOW the run's peak pack "
                     "charge, so on the pack quantity the acceptance is "
                     "exceeded at EVERY tabulated cell temperature - "
                     "there is no favourable cell temperature at all, "
                     "only a least-unfavourable one. See "
                     "pack_quantity_binding_analysis."),
    note=("READ BOTH FIELDS. On the REGEN LEG - the leg the ordered run "
          "enforces - R16's curve is not binding: peak regen-to-pack is "
          "far below acceptance at the declared cell temperatures and "
          "regen_shed_by_r16_kWh is zero on every seed. On the PACK - the "
          "quantity the file's own header names - the SAME curve is "
          "exceeded on every ordered case, for the seconds and energies "
          "above, because regen and the genset charge the pack "
          "simultaneously. The r16_pack_acceptance_bracket below prices "
          "enforcing the pack reading. The hot-end crossing and the choice "
          "of reading are escalated (ESC-8), not resolved here."))

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
_r8b_uns, _r8b_uns_gov = _case_worst(
    {c: _R8B[c]["ensemble"]["unserved_bus_kWh_max"] for c in KX_CASES},
    "max", {c: _R8B[c]["ensemble"]["unserved_bus_kWh_max_governing_case"]
            for c in KX_CASES}, list(KX_CASES))
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
    worst_unserved_kWh=_r8b_uns,
    worst_unserved_governing_case=_r8b_uns_gov,
    reading=("R4/E24's 'the spine is not sized for forced series' record "
             "extends to the PACK's power envelope, not only the motor "
             "rating: the delivered pack has the ENERGY for pure-series "
             "VOLT-REG with margin, and the ordered run confirms that, but "
             "at its rated bus-side power it does not have the POWER on "
             "the hardest samples. This is a dispatch and rating question "
             "for WS5/WS3, not a WS4 tuning knob - escalated as ESC-9."))

# --- R16 PACK-ACCEPTANCE bracket (KX r2, adjudication KX-B1 remedy (i)).
# The ordered run applies WS3's acceptance curve to the REGEN LEG only.
# This bracket applies the same curve to the PACK's total bus-side charge
# power - the reading the file's own header supports - so the record shows
# what the conservative reading costs. WS4 does not choose the reading;
# ESC-8 does.
log("R22a bracket: R16 acceptance enforced on the PACK charge "
    "(WS3 V2pack_chg_cont_kW_bus at declared cells) ...")
_R16B = {}
for _case, _cfg in KX_CASES.items():
    _ps = {}
    for sd in REG_SEEDS:
        _o = run_g1_mode(
            REG[sd], "b", ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
            veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
            chg_accept_bus_kw=_ACCEPT[_case],
            r16_pack_cap_bus_kw=_ACCEPT[_case],
            spin_coast_shaft_kw_85=COAST_SH_KW,
            spin_coast_bus_kw_85=COAST_BUS_KW)
        _ps[str(sd)] = _sd_record(_o)
    _R16B[_case] = dict(per_seed=_ps,
                        ensemble=_sd_envelope(_ps, _case + "/R16-pack"))
    log(f"  [{_case}] shed "
        f"{_R16B[_case]['ensemble']['r16_pack_cap_shed_kWh_min']:.3f}-"
        f"{_R16B[_case]['ensemble']['r16_pack_cap_shed_kWh_max']:.3f} kWh, "
        f"clipped "
        f"{_R16B[_case]['ensemble']['r16_pack_cap_clip_s_max']:.1f} s, "
        f"unserved "
        f"{_R16B[_case]['ensemble']['unserved_bus_kWh_max']:.4f} kWh")
# KX r3 / adjudication KX2-M3(b). The KX r2 field was a RATIO OF
# ENSEMBLE MAXIMA - two independently maximised numbers, which is not the
# maximum of the quantity: the identical construction defect the same
# round had just fixed in the heat ledger under KX-m6. At nominal it also
# FLIPPED SIGN (-0.0018% exported, +0.169% on the paired median, a cost
# on six of the eight seeds), and `fuel_penalty_pct_max` was rendered in
# ESC-8(c) as "at most +0.20%" while the worst paired seed at CdA 5.4
# costs +0.249%. The paired statistic is computed here; the
# ratio-of-maxima is retained beside it under an honest name.
_R16B_PAIRED = _paired_pct_delta(
    _R16B, {c: SD["cases"][c] for c in KX_CASES},
    "fuel_energy_kWh_per_km", list(KX_CASES),
    "R16 acceptance enforced on the pack", "the ordered mode-(b) run",
    "Positive = enforcing the pack reading COSTS fuel on that seed.")
_r16b_fuel_pp = {
    c: 100.0 * (_R16B[c]["ensemble"]["fuel_kg_max"]
                - SD["cases"][c]["ensemble"]["fuel_kg_max"])
    / SD["cases"][c]["ensemble"]["fuel_kg_max"] for c in KX_CASES}
_r16b_uns, _r16b_uns_gov = _case_worst(
    {c: _R16B[c]["ensemble"]["unserved_bus_kWh_max"] for c in KX_CASES},
    "max", {c: _R16B[c]["ensemble"]["unserved_bus_kWh_max_governing_case"]
            for c in KX_CASES}, list(KX_CASES))
_r16b_shed, _r16b_shed_gov = _case_worst(
    {c: _R16B[c]["ensemble"]["r16_pack_cap_shed_kWh_max"] for c in KX_CASES},
    "max", {c: _R16B[c]["ensemble"][
        "r16_pack_cap_shed_kWh_max_governing_case"] for c in KX_CASES},
    list(KX_CASES))
_r16b_clip, _r16b_clip_gov = _case_worst(
    {c: _R16B[c]["ensemble"]["r16_pack_cap_clip_s_max"] for c in KX_CASES},
    "max", {c: _R16B[c]["ensemble"]["r16_pack_cap_clip_s_max_governing_case"]
            for c in KX_CASES}, list(KX_CASES))
SD["r16_pack_acceptance_bracket"] = dict(
    ruling="R16 read as a PACK charge limit (adjudication KX-B1)",
    _status=("WS4 bracket in response to adjudication KX-B1, NOT an ordered "
             "case and NOT a WS4 choice of reading. The ordered "
             "series_duty_v2 numbers above stand as run, with the regen-leg "
             "reading; this bracket prices the pack reading so ESC-8 is "
             "decided on measured cost rather than on assertion."),
    cap_kW_bus_at_declared_cells=_ACCEPT,
    enforcement=("pack charge above the acceptance is SHED (booked as "
                 "r16_pack_cap_shed_kWh / r16_pack_cap_clip_s). This is the "
                 "crudest of the available remedies: it discards surplus "
                 "rather than not generating it. A supervisor that instead "
                 "backs the genset off is exactly the load-following "
                 "companion (b'), which stays inside the acceptance on "
                 "every seed of every ordered case with no shed energy at "
                 "all - see companion_bp and s4-KX.6."),
    cases=_R16B,
    worst_shed_kWh=_r16b_shed,
    worst_shed_governing_case=_r16b_shed_gov,
    worst_clip_s=_r16b_clip,
    worst_clip_governing_case=_r16b_clip_gov,
    worst_unserved_kWh=_r16b_uns,
    worst_unserved_governing_case=_r16b_uns_gov,
    # --- R36: the PAIRED per-seed fuel delta (adjudication KX2-M3(b))
    fuel_delta_paired=_R16B_PAIRED,
    fuel_delta_pct_paired_worst_max=_R16B_PAIRED["worst_max_pct"],
    fuel_delta_pct_paired_worst_max_governing_case=_R16B_PAIRED[
        "worst_max_pct_governing_case"],
    fuel_delta_pct_paired_worst_min=_R16B_PAIRED["worst_min_pct"],
    fuel_delta_pct_paired_worst_min_governing_case=_R16B_PAIRED[
        "worst_min_pct_governing_case"],
    # --- the KX r2 fields, retained under names that say what they are
    fuel_penalty_pct_vs_ordered_ratio_of_ensemble_maxima=_r16b_fuel_pp,
    fuel_penalty_pct_ratio_of_ensemble_maxima_max=max(_r16b_fuel_pp.values()),
    _superseded_fields=(
        "KX r2 exported the two lines above as "
        "`fuel_penalty_pct_vs_ordered` / `fuel_penalty_pct_max` and "
        "ESC-8(c) rendered the latter as 'fuel penalty at most +0.20%'. "
        "Both are ratios of two INDEPENDENTLY MAXIMISED ensemble numbers, "
        "which is not the maximum of the quantity and is not a bound: at "
        "nominal the ratio-of-maxima has the OPPOSITE SIGN to six of the "
        "eight paired seeds, and the true worst paired seed at CdA 5.4 "
        "costs more than the 'at most'. Withdrawn under those names "
        "(adjudication KX2-M3(b)); consume fuel_delta_pct_paired_*."),
    reading=("enforcing WS3's acceptance curve on the PACK costs the shed "
             "energy and fuel above and does NOT reopen the zero-unserved "
             "headline. The headline therefore does not depend on which "
             "reading of R16 the lead rules for. The fuel cost is a cost "
             "on every seed of both other cases and on the majority of "
             "seeds at nominal - see fuel_delta_paired.seeds_positive_n_"
             "by_case."))

# --- ENGINE CONTINUOUS-RATING bracket (KX r2, adjudication KX-M1).
# The ordered run's emergency band caps the engine at the AUTOMOTIVE
# full-load curve, not at the 132 kW continuous flat-rating WS4 specifies
# and R18 blocks WS6's release on. This bracket caps it at the genset's
# own rating, so the record shows what the rating costs - and, in
# particular, whether the zero-unserved headline depends on the
# over-rating. It does not.
log("R22a bracket: engine capped at its OWN continuous flat-rating in "
    "the emergency band ...")
_M1B = {}
for _case, _cfg in KX_CASES.items():
    _ps = {}
    for sd in REG_SEEDS:
        _o = run_g1_mode(
            REG[sd], "b", ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
            veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
            chg_accept_bus_kw=_ACCEPT[_case],
            emerg_cap_cont_rating=True,
            spin_coast_shaft_kw_85=COAST_SH_KW,
            spin_coast_bus_kw_85=COAST_BUS_KW)
        _ps[str(sd)] = _sd_record(_o)
    _M1B[_case] = dict(per_seed=_ps,
                       ensemble=_sd_envelope(_ps, _case + "/cont-rating"))
    log(f"  [{_case}] unserved "
        f"{_M1B[_case]['ensemble']['unserved_bus_kWh_max']:.4f} kWh, "
        f"SOC min {_M1B[_case]['ensemble']['soc_min_min']:.3f}, over-rating "
        f"{_M1B[_case]['ensemble']['engine_over_continuous_rating_s_max']:.1f} s, "
        f"fuel {_M1B[_case]['ensemble']['fuel_kg_max']:.2f} kg")
# KX r3 / adjudication KX2-M3(c): same construction defect. Here the
# conclusion survives the correction - paired, every seed of every case
# is <= 0, so ESC-10's "fuel does not rise at all" holds - but a "max"
# over three negatives is the LEAST saving, exported under a name that
# says penalty.
_M1B_PAIRED = _paired_pct_delta(
    _M1B, {c: SD["cases"][c] for c in KX_CASES},
    "fuel_energy_kWh_per_km", list(KX_CASES),
    "the engine held to its own continuous flat-rating",
    "the ordered mode-(b) run",
    "Positive = holding the engine to its rating COSTS fuel on that seed.")
_m1b_fuel_pp = {
    c: 100.0 * (_M1B[c]["ensemble"]["fuel_kg_max"]
                - SD["cases"][c]["ensemble"]["fuel_kg_max"])
    / SD["cases"][c]["ensemble"]["fuel_kg_max"] for c in KX_CASES}
_m1b_uns, _m1b_uns_gov = _case_worst(
    {c: _M1B[c]["ensemble"]["unserved_bus_kWh_max"] for c in KX_CASES},
    "max", {c: _M1B[c]["ensemble"]["unserved_bus_kWh_max_governing_case"]
            for c in KX_CASES}, list(KX_CASES))
_m1b_soc, _m1b_soc_gov = _case_worst(
    {c: _M1B[c]["ensemble"]["soc_min_min"] for c in KX_CASES},
    "min", {c: _M1B[c]["ensemble"]["soc_min_min_governing_case"]
            for c in KX_CASES}, list(KX_CASES), zero_is_degenerate=False)
SD["engine_continuous_rating_bracket"] = dict(
    ruling="R18 / ESC-1 (the 132 kW continuous flat-rating); KX-M1",
    _status=("WS4 bracket in response to adjudication KX-M1, NOT an "
             "ordered case. The ordered series_duty_v2 numbers above stand "
             "as run, with the emergency band's automotive full-load "
             "ceiling; this bracket prices the genset's own rating."),
    ordered_emergency_ceiling=("engine.peak_power_kw() x derate x 0.97 = "
                              "the 4HK1-TC AUTOMOTIVE full-load curve"),
    bracket_emergency_ceiling=("engine.rated_cont_kw x derate = the "
                               "WS4-specified continuous flat-rating"),
    engine_automotive_peak_kW=ENG_V2.peak_power_kw(),
    engine_continuous_rating_kW_by_case={
        c: ENG_V2.rated_cont_kw * cfg["derate"]
        for c, cfg in KX_CASES.items()},
    cases=_M1B,
    worst_unserved_kWh=_m1b_uns,
    worst_unserved_governing_case=_m1b_uns_gov,
    unserved_stays_zero=bool(max(
        _M1B[c]["ensemble"]["unserved_bus_kWh_max"]
        for c in KX_CASES) <= 1e-9),
    soc_min_by_case={c: _M1B[c]["ensemble"]["soc_min_min"]
                     for c in KX_CASES},
    soc_min_worst=_m1b_soc,
    soc_min_worst_governing_case=_m1b_soc_gov,
    # --- R36: the PAIRED per-seed fuel delta (adjudication KX2-M3(c))
    fuel_delta_paired=_M1B_PAIRED,
    fuel_delta_pct_paired_worst_max=_M1B_PAIRED["worst_max_pct"],
    fuel_delta_pct_paired_worst_max_governing_case=_M1B_PAIRED[
        "worst_max_pct_governing_case"],
    fuel_delta_pct_paired_worst_min=_M1B_PAIRED["worst_min_pct"],
    fuel_delta_pct_paired_worst_min_governing_case=_M1B_PAIRED[
        "worst_min_pct_governing_case"],
    fuel_rises_on_no_ordered_seed=bool(_M1B_PAIRED["worst_max_pct"] <= 0.0),
    # --- the KX r2 fields, retained under names that say what they are
    fuel_penalty_pct_vs_ordered_ratio_of_ensemble_maxima=_m1b_fuel_pp,
    fuel_penalty_pct_ratio_of_ensemble_maxima_max=max(_m1b_fuel_pp.values()),
    _superseded_fields=(
        "KX r2 exported the two lines above as "
        "`fuel_penalty_pct_vs_ordered` / `fuel_penalty_pct_max`. Both are "
        "ratios of two independently maximised ensemble numbers, and the "
        "'max' was a maximum over three NEGATIVE numbers - i.e. the LEAST "
        "saving - under a name that says penalty. Withdrawn under those "
        "names (adjudication KX2-M3(c)); consume "
        "fuel_delta_pct_paired_*. ESC-10's conclusion is unchanged: "
        "paired, every seed of every ordered case is <= 0."),
    reading=("the zero-unserved headline does NOT rest on the emergency "
             "band's automotive ceiling: with the engine held to its own "
             "continuous flat-rating the run still completes every "
             "ordered case with zero unserved bus energy, at a deeper SOC "
             "minimum and the fuel delta above. What the over-rating buys "
             "is SOC margin, not feasibility. Escalated as ESC-10 against "
             "R18/ESC-1, whose +0.82 kW corner margin is a CONTINUOUS-"
             "rating figure."))

# ---------------------------------------------------------------------------
# R6 RATING-FAMILY PROBE (KX r3, adjudication KX2-m4).
#
# ESC-10 asks the lead to rule on whether short excursions above the
# genset's own continuous flat-rating are acceptable. KX r2 put a
# correctly-constructed ORDERED-SET maximum in front of the lead
# (250.0 s/cycle at cda_5.4) - but R6, the ruling that SETS the 132 kW
# rating, defines its rating basis as +20% payload, CdA 5.4, 4 kW aux,
# +45 C, 2,000 m, and members of that family that the directive did not
# order are WORSE. A lead ruling on an exposure should see the worst
# exposure available inside the sizing corner's own family, so it is
# measured here.
#
# These are NOT ordered cases and do NOT join series_duty_v2's case set:
# the ordered-set maximum stays exported, unchanged, as an ordered-set
# maximum. This block is a second, explicitly-named enumerated set and
# every extremum over it says which set it is over (R14).
# ---------------------------------------------------------------------------
R6_FAMILY = {
    "payload+20pct_cda5.4_sea_level": dict(
        veh=dataclasses.replace(VEH, CdA=5.4), m=7180.0, aux=2.0,
        derate=1.0, t_cell_C=25.0,
        condition="+20% payload (7,180 kg), CdA 5.4, 2 kW aux, sea level"),
    "aux4kW_cda5.4": dict(
        veh=dataclasses.replace(VEH, CdA=5.4), m=None, aux=4.0,
        derate=1.0, t_cell_C=25.0,
        condition="CdA 5.4, 4 kW aux, GVW, sea level"),
    "aux4kW_nominal": dict(
        veh=VEH, m=None, aux=4.0, derate=1.0, t_cell_C=25.0,
        condition="CdA 4.2, 4 kW aux, GVW, sea level"),
    "r6_rating_corner_full": dict(
        veh=dataclasses.replace(VEH, CdA=5.4, rho_air=0.8706), m=7180.0,
        aux=4.0, derate=DER, t_cell_C=45.0,
        condition=("the full R6 rating corner: +20% payload, CdA 5.4, "
                   "4 kW aux, 2,000 m / +45 C")),
}
log("ESC-10 widening: R6 rating-family probe (unordered, 4 cases) ...")
_R6F = {}
for _case, _cfg in R6_FAMILY.items():
    _acc = float(np.interp(_cfg["t_cell_C"], R16_T, R16_P))
    _ps = {}
    for sd in REG_SEEDS:
        _o = run_g1_mode(
            REG[sd], "b", ENG_V2, GEN_V2, USABLE_KX_KWH,
            p_aux_kw=_cfg["aux"], veh=_cfg["veh"], m=_cfg["m"],
            derate=_cfg["derate"], chain=CHAIN, chg_accept_bus_kw=_acc,
            spin_coast_shaft_kw_85=COAST_SH_KW,
            spin_coast_bus_kw_85=COAST_BUS_KW)
        _ps[str(sd)] = _sd_record(_o)
    _R6F[_case] = dict(condition=_cfg["condition"],
                       declared_cell_temperature_C=_cfg["t_cell_C"],
                       engine_continuous_rating_kW=(
                           ENG_V2.rated_cont_kw * _cfg["derate"]),
                       per_seed=_ps,
                       ensemble=_sd_envelope(_ps, _case + "/R6-family"))
    log(f"  [{_case}] above rating "
        f"{_R6F[_case]['ensemble']['engine_over_continuous_rating_s_min']:.1f}"
        f"-{_R6F[_case]['ensemble']['engine_over_continuous_rating_s_max']:.1f}"
        f" s, unserved "
        f"{_R6F[_case]['ensemble']['unserved_bus_kWh_max']:.4f} kWh")

_R6F_KEYS = list(R6_FAMILY)
_r6f_over, _r6f_over_gov = _case_worst(
    {c: _R6F[c]["ensemble"]["engine_over_continuous_rating_s_max"]
     for c in _R6F_KEYS}, "max",
    {c: _R6F[c]["ensemble"]["engine_over_continuous_rating_s_max_governing_case"]
     for c in _R6F_KEYS}, _R6F_KEYS, zero_is_degenerate=False,
    set_name="enumerated R6 rating-family probe set")
_UNION_KEYS = list(KX_CASES) + _R6F_KEYS
_union_over = {
    **{c: SD["cases"][c]["ensemble"]["engine_over_continuous_rating_s_max"]
       for c in KX_CASES},
    **{c: _R6F[c]["ensemble"]["engine_over_continuous_rating_s_max"]
       for c in _R6F_KEYS}}
_union_gov = {
    **{c: SD["cases"][c]["ensemble"][
        "engine_over_continuous_rating_s_max_governing_case"]
       for c in KX_CASES},
    **{c: _R6F[c]["ensemble"][
        "engine_over_continuous_rating_s_max_governing_case"]
       for c in _R6F_KEYS}}
_u_over, _u_over_gov = _case_worst(
    _union_over, "max", _union_gov, _UNION_KEYS, zero_is_degenerate=False,
    set_name=("union of the enumerated ordered case set and the R6 "
              "rating-family probe set"))
_r6f_uns, _r6f_uns_gov = _case_worst(
    {c: _R6F[c]["ensemble"]["unserved_bus_kWh_max"] for c in _R6F_KEYS},
    "max", {c: _R6F[c]["ensemble"]["unserved_bus_kWh_max_governing_case"]
            for c in _R6F_KEYS}, _R6F_KEYS,
    degenerate_zero_label=("no governing case - every case of the R6 "
                           "rating-family probe set is exactly zero on all "
                           "8 seeds"),
    set_name="enumerated R6 rating-family probe set")
_r6f_soc, _r6f_soc_gov = _case_worst(
    {c: _R6F[c]["ensemble"]["soc_min_min"] for c in _R6F_KEYS}, "min",
    {c: _R6F[c]["ensemble"]["soc_min_min_governing_case"]
     for c in _R6F_KEYS}, _R6F_KEYS, zero_is_degenerate=False,
    set_name="enumerated R6 rating-family probe set")
SD["r6_rating_family_probe"] = dict(
    ruling="R6 (the rating basis) / ESC-10; adjudication KX2-m4",
    _status=("WS4 probe, NOT ordered cases and NOT part of "
             "series_duty_v2's case set. The KX_DIRECTIVE ordered three "
             "cases and the ordered-set maximum is exported unchanged as "
             "an ordered-set maximum. This block widens the EXPOSURE the "
             "lead is asked to rule on in ESC-10 to R6's own rating "
             "family, because a ruling on an exposure should see the "
             "worst exposure available inside the sizing corner's family "
             "rather than the worst inside a case set chosen for a "
             "different purpose."),
    r6_rating_basis=("R6: 122.1 kW delivered at +20% payload, 4 kW "
                     "accessories, CdA 5.4, +45 C, 2,000 m"),
    cases=_R6F,
    ordered_set_worst_over_rating_s=SD[
        "companion_bp_capability_comparison"]["axes"][
            "engine_over_continuous_rating_s"]["mode_b_block_of_record"][
                "worst_case_max"],
    ordered_set_worst_over_rating_s_governing_case=SD[
        "companion_bp_capability_comparison"]["axes"][
            "engine_over_continuous_rating_s"]["mode_b_block_of_record"][
                "worst_case_max_governing_case"],
    r6_family_worst_over_rating_s=_r6f_over,
    r6_family_worst_over_rating_s_governing_case=_r6f_over_gov,
    union_worst_over_rating_s=_u_over,
    union_worst_over_rating_s_governing_case=_u_over_gov,
    union_case_set=_UNION_KEYS,
    worst_unserved_kWh=_r6f_uns,
    worst_unserved_governing_case=_r6f_uns_gov,
    soc_min_worst=_r6f_soc,
    soc_min_worst_governing_case=_r6f_soc_gov,
    reading=("inside R6's own rating family the genset spends MORE time "
             "above its continuous flat-rating than at any ordered case, "
             "and the worst member is not the full corner - the corner's "
             "derate keeps the engine's ceiling low and its air thin, "
             "while +20% payload at CdA 5.4 and SEA LEVEL has the full "
             "automotive ceiling available and the load to use it. The "
             "zero-unserved headline is unaffected: every probe case "
             "completes on every seed. ESC-10 is restated on the union "
             "maximum, with both set maxima exported so the lead can see "
             "which set each number is over."))

# --- hysteresis sensitivity: WS3's own allocated genset band on the
# delivered pack, reference seed. The cycling rate is the export WS5 needs
# and it is band-sensitive, so the band is not left implicit.
#
# KX r2 / adjudication KX-m8: genset starts are a STOCHASTIC output, so
# R9 requires an 8-seed envelope, not one draw. The whole sensitivity is
# now run over the ordered ensemble; the reference-seed rows are retained
# under `ref_seed` so nothing previously reported is dropped.
_hyst_kwh = float(_WS3_SOC["allocation"]["V2"]["genset_hysteresis_kWh"])
_soc_tgt = float(_WS3_SOC["target"])
_half = 0.5 * _hyst_kwh / USABLE_KX_KWH
log("R22a sensitivity: WS3 allocated genset-hysteresis band, 8 seeds ...")
SD["hysteresis_sensitivity"] = dict(
    ruling="R19 precedent / WS3 soc_strategy.allocation.V2; R9 (8-seed)",
    _basis=("the cycling rate is the export most sensitive to a supervisor "
            "constant, and starts are stochastic - so both bands are run "
            "over the SAME enumerated 8-seed VOLT-REG ensemble as the "
            "ordered block (R9/R14), not on one draw. The KX round ran "
            "this on the reference seed only (adjudication KX-m8); those "
            "rows are retained under ref_seed."),
    ws3_allocated_genset_hysteresis_kWh=_hyst_kwh,
    ws3_soc_target=_soc_tgt,
    band_soc_fraction=[_soc_tgt - _half, _soc_tgt + _half],
    simulator_band_soc_fraction=[sim.SER_LO, sim.SER_HI],
    simulator_band_kWh=(sim.SER_HI - sim.SER_LO) * USABLE_KX_KWH,
    cases={})
for _case, _cfg in KX_CASES.items():
    _ps = {}
    for sd in REG_SEEDS:
        _o = run_g1_mode(
            REG[sd], "b", ENG_V2, GEN_V2, USABLE_KX_KWH, p_aux_kw=2.0,
            veh=_cfg["veh"], derate=_cfg["derate"], chain=CHAIN,
            chg_accept_bus_kw=_ACCEPT[_case],
            ser_band=(_soc_tgt - _half, _soc_tgt + _half),
            spin_coast_shaft_kw_85=COAST_SH_KW,
            spin_coast_bus_kw_85=COAST_BUS_KW)
        _ps[str(sd)] = _sd_record(_o)
    SD["hysteresis_sensitivity"]["cases"][_case] = dict(
        ws3_band=dict(per_seed=_ps,
                      ensemble=_sd_envelope(_ps, _case + "/WS3-band")),
        simulator_band=dict(
            per_seed=SD["cases"][_case]["per_seed"],
            ensemble=SD["cases"][_case]["ensemble"]),
        ref_seed=dict(ws3_band=_ps["23"],
                      simulator_band=SD["cases"][_case]["per_seed"]["23"]))
    log(f"  [{_case}] starts, WS3 band "
        f"{SD['hysteresis_sensitivity']['cases'][_case]['ws3_band']['ensemble']['genset_starts_min']:.0f}"
        f"-{SD['hysteresis_sensitivity']['cases'][_case]['ws3_band']['ensemble']['genset_starts_max']:.0f}"
        f" vs simulator band "
        f"{SD['cases'][_case]['ensemble']['genset_starts_min']:.0f}"
        f"-{SD['cases'][_case]['ensemble']['genset_starts_max']:.0f}")

# --- R22d operational member, quantified on this run
_c_sh = [SD["cases"][c]["ensemble"]["r22d_coast_spin_shaft_kWh_max"]
         for c in KX_CASES]
_c_bus = [SD["cases"][c]["ensemble"]["r22d_coast_spin_bus_kWh_max"]
          for c in KX_CASES]
# KX r3 / CONSTRUCTION SWEEP (KX2-M3 family, found by the sweep and not
# named in the findings file). The KX r2 figure combined THREE
# independently extremised ensemble numbers - a maximised shaft energy,
# a maximised bus energy and a maximised fuel mass in the DENOMINATOR -
# and exported the result as `unbooked_pp_max`, rendered as "worth at
# most X pp of cycle fuel". A ratio of independently extremised numbers
# is not the extremum of the ratio and is not a bound. The member is now
# priced PER SEED, on that seed's own coast energies over that seed's own
# fuel, and only then enveloped (R36 / R9 / R14).
_c_pp_env = {}
for c in KX_CASES:
    # price the coast member at the pinned point's marginal fuel rate:
    # shaft-side drag has to be made up at the wheel through the chain,
    # bus-side draw is served from the bus directly
    _pin_c = SD["cases"][c]["pinned_point"]
    _vals = []
    for _sd in REG_SEEDS:
        _r = SD["cases"][c]["per_seed"][str(_sd)]
        _g_sd = ((_r["r22d_coast_spin_shaft_kWh"] / _eta_series_ref
                  + _r["r22d_coast_spin_bus_kWh"])
                 / _pin_c["eta_gen"] * _pin_c["bsfc"])
        _vals.append(100.0 * _g_sd / (_r["fuel_kg"] * 1e3))
    _c_pp_env[c] = dict(
        per_seed={str(_sd): v for _sd, v in zip(REG_SEEDS, _vals)},
        min=min(_vals), median=float(np.median(_vals)), max=max(_vals),
        max_governing_case=(
            f"seed {REG_SEEDS[int(np.argmax(_vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{c}]"),
        min_governing_case=(
            f"seed {REG_SEEDS[int(np.argmin(_vals))]} of the enumerated "
            f"8-seed VOLT-REG ensemble [{c}]"))
_c_pp = {c: _c_pp_env[c]["max"] for c in KX_CASES}
_c_pp_r2 = {}
for c in KX_CASES:
    e = SD["cases"][c]["ensemble"]
    _pin_c = SD["cases"][c]["pinned_point"]
    _g = ((e["r22d_coast_spin_shaft_kWh_max"] / _eta_series_ref
           + e["r22d_coast_spin_bus_kWh_max"])
          / _pin_c["eta_gen"] * _pin_c["bsfc"])
    _c_pp_r2[c] = 100.0 * _g / (e["fuel_kg_max"] * 1e3)
_c_pp_worst, _c_pp_worst_gov = _case_worst(
    _c_pp, "max", {c: _c_pp_env[c]["max_governing_case"] for c in KX_CASES},
    list(KX_CASES), zero_is_degenerate=False)
def _R22D_GOV(key):
    """R14 label for a max over the enumerated 3-case x 8-seed set."""
    worst = max(KX_CASES,
                key=lambda c: SD["cases"][c]["ensemble"][key + "_max"])
    return (f"case {worst} of the enumerated ordered case set "
            f"{{{', '.join(KX_CASES)}}}; within it, "
            f"{SD['cases'][worst]['ensemble'][key + '_max_governing_case']}")


SD["r22d_coast_spin_member"] = dict(
    ruling="R22d",
    ws2_point_drag_85kmh_W=dict(shaft=WS2X["spin"][
        "point_check_shaft_drag_85kmh_W"],
        bus=WS2X["spin"]["point_check_bus_draw_85kmh_W"]),
    scaling="[WS4-DECLARED] linear in road speed from WS2's 85 km/h point",
    coast_no_regen_s_max=max(
        SD["cases"][c]["ensemble"]["coast_no_regen_s_max"] for c in KX_CASES),
    # R14 (adjudication KX-m3): these three are maxima over the enumerated
    # 3-case x 8-seed set and were exported unlabelled.
    coast_no_regen_s_max_governing_case=_R22D_GOV("coast_no_regen_s"),
    coast_spin_shaft_kWh_max=max(_c_sh),
    coast_spin_shaft_kWh_max_governing_case=_R22D_GOV(
        "r22d_coast_spin_shaft_kWh"),
    coast_spin_bus_kWh_max=max(_c_bus),
    coast_spin_bus_kWh_max_governing_case=_R22D_GOV(
        "r22d_coast_spin_bus_kWh"),
    # KX r3 / construction sweep: per-seed pricing, then the envelope.
    unbooked_pp_of_cycle_fuel=_c_pp,
    unbooked_pp_paired_by_case=_c_pp_env,
    unbooked_pp_max=_c_pp_worst,
    unbooked_pp_max_governing_case=_c_pp_worst_gov,
    unbooked_pp_of_cycle_fuel_ratio_of_ensemble_extrema_kx_r2=_c_pp_r2,
    _superseded_construction=(
        "KX r2 built each case's figure from the 8-seed MAXIMUM coast "
        "shaft energy plus the 8-seed MAXIMUM coast bus energy over the "
        "8-seed MAXIMUM fuel mass - three independently extremised "
        "numbers - and exported max() of that as `unbooked_pp_max`, "
        "rendered as 'at most X pp of cycle fuel'. That is not the "
        "maximum of the quantity and is not a bound. The r2 values are "
        "retained on the line above; the live figures are the per-seed "
        "construction (KX r3 construction sweep, KX2-M3 family)."),
    charged_to_fuel=False,
    direction_of_error=("series_duty_v2's fuel numbers EXCLUDE this member, "
                        "so they are optimistic by the percentage points "
                        "above. R22d's own remedy - the WS5 supervisor "
                        "preferring light regen over true coast - removes "
                        "the exposure by removing the true-coast samples; "
                        "the member is exported so WS5 can price that "
                        "choice."))

# --- heat rows for the WS6 ledger, by component and case (program rule 7)
#
# KX r2 / adjudication KX-m6: each row is now the MAXIMUM OF THE PER-SEED
# CYCLE AVERAGES (each seed's own energy over its own duration), not
# max(energy) divided by the reference seed's duration - which understated
# the true 8-seed maximum by 0.4-0.7%. Every component carries its OWN
# governing seed, because different seeds maximise different components.
# KX r2 / adjudication KX-m7: a cycle mean is not the case. Peak and
# rolling 2-min / 10-min maxima are exported alongside, so a cooling owner
# sizing against these rows sees the transients in the duty.
RAD_PKG_FRAC = 0.48       # ws4_models.engine_energy_split: coolant+oil+CAC
SD_HEAT = {}
for _case in KX_CASES:
    _e = SD["cases"][_case]["ensemble"]
    SD_HEAT[f"series_duty_v2_{_case}_cycle_average"] = dict(
        case=f"R22a pure-series V2 at the delivered pack, {_case}, "
             "VOLT-REG (8-seed max of the per-seed cycle averages; each "
             "component labelled with its own governing seed)",
        engine_rejection_avg_kW=_e["engine_reject_avg_kW_max"],
        engine_rejection_avg_kW_governing_case=_e[
            "engine_reject_avg_kW_max_governing_case"],
        generator_loss_avg_kW=_e["generator_loss_avg_kW_max"],
        generator_loss_avg_kW_governing_case=_e[
            "generator_loss_avg_kW_max_governing_case"],
        electric_chain_loss_avg_kW=_e["chain_loss_avg_kW_max"],
        electric_chain_loss_avg_kW_governing_case=_e[
            "chain_loss_avg_kW_max_governing_case"],
        friction_brake_kWh_per_cycle=_e["friction_brake_kWh_max"],
        friction_brake_kWh_per_cycle_governing_case=_e[
            "friction_brake_kWh_max_governing_case"],
        pm_coast_spin_shaft_kWh_per_cycle=_e["r22d_coast_spin_shaft_kWh_max"],
        # R14 (adjudication KX2-m2): these were exported as bare maxima
        pm_coast_spin_shaft_kWh_per_cycle_governing_case=_e[
            "r22d_coast_spin_shaft_kWh_max_governing_case"],
        pm_coast_spin_bus_kWh_per_cycle=_e["r22d_coast_spin_bus_kWh_max"],
        pm_coast_spin_bus_kWh_per_cycle_governing_case=_e[
            "r22d_coast_spin_bus_kWh_max_governing_case"],
        # --- KX-m7: the transient the cycle mean cannot show
        engine_rejection_peak_kW=_e["engine_reject_peak_kW_max"],
        engine_rejection_peak_kW_governing_case=_e[
            "engine_reject_peak_kW_max_governing_case"],
        engine_rejection_2min_max_kW=_e["engine_reject_2min_max_kW_max"],
        engine_rejection_2min_max_kW_governing_case=_e[
            "engine_reject_2min_max_kW_max_governing_case"],
        engine_rejection_10min_max_kW=_e["engine_reject_10min_max_kW_max"],
        engine_rejection_10min_max_kW_governing_case=_e[
            "engine_reject_10min_max_kW_max_governing_case"],
        # the same three rows through the declared 48% radiator-package
        # share, i.e. the numbers the HT package actually sees
        # R14 (adjudication KX2-m2): each of these four is the labelled
        # engine-rejection maximum above scaled by the declared package
        # share, so it inherits that row's governing seed - which was not
        # exported. It is now.
        radiator_package_avg_kW=RAD_PKG_FRAC * _e["engine_reject_avg_kW_max"],
        radiator_package_avg_kW_governing_case=_e[
            "engine_reject_avg_kW_max_governing_case"],
        radiator_package_peak_kW=RAD_PKG_FRAC * _e[
            "engine_reject_peak_kW_max"],
        radiator_package_peak_kW_governing_case=_e[
            "engine_reject_peak_kW_max_governing_case"],
        radiator_package_2min_max_kW=RAD_PKG_FRAC * _e[
            "engine_reject_2min_max_kW_max"],
        radiator_package_2min_max_kW_governing_case=_e[
            "engine_reject_2min_max_kW_max_governing_case"],
        radiator_package_10min_max_kW=RAD_PKG_FRAC * _e[
            "engine_reject_10min_max_kW_max"],
        radiator_package_10min_max_kW_governing_case=_e[
            "engine_reject_10min_max_kW_max_governing_case"],
        radiator_package_share=RAD_PKG_FRAC,
        transient_note=("SIZE AGAINST THE WINDOWS, NOT THE MEAN. The "
                        "cycle-average row above is a mean over a ~1.5 h "
                        "VOLT-REG realisation; the same duty rejects the "
                        "peak above for the emergency-band excursions "
                        "measured in engine_over_continuous_rating_s. The "
                        "2-min and 10-min rolling maxima are the rows a "
                        "radiator/CAC package is sized against; R20's "
                        "declared design point is 95.0 kW of HT-package "
                        "duty in +45 C air (ESC-4)."),
        governing_case=("PER COMPONENT - see the *_governing_case field "
                        "beside each row. KX r1 carried a single "
                        "governing_case (the engine-rejection seed) "
                        "applied to generator, chain and friction figures "
                        "that different seeds maximise (adjudication "
                        "KX-m6); the field is retained as this pointer so "
                        "nothing previously exported is dropped."),
        _construction=("8-seed max over the enumerated ensemble of each "
                       "seed's OWN cycle average (energy / that seed's "
                       "duration). KX r1 divided the 8-seed max ENERGY by "
                       "the reference seed's duration, which is not the "
                       "maximum of the quantity - adjudication KX-m6."),
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
# KX r2 / adjudication KX-m4: one full-rate trace per ORDERED CASE (see
# R34_TRACE_ALL_ORDERED_RUNS above), each named by case and seed.
_TRACE_FILES = {}
for (_case, _sd), _tr in sorted(_SD_TRACES.items()):
    _tf = f"data/trace_series_duty_v2_{_case}_seed{_sd}_10Hz.csv"
    with open(_tf, "w") as f:
        f.write("# Project Volt WS4 - R34 10 Hz trace. One file per ORDERED "
                "CASE at the reference seed; see results_ws4.json -> "
                "series_duty_v2 -> _trace_files -> r34_interpretation.\n")
        f.write(f"# series_duty_v2 / {_case} / mode (b) pure series at the "
                f"pinned point / VOLT-REG seed {_sd}\n")
        f.write(f"# delivered pack {USABLE_KX_KWH:.6f} kWh usable at the bus; "
                f"R16 acceptance {_ACCEPT[_case]:.3f} kW bus at "
                f"{KX_CASES[_case]['t_cell_C']:.1f} C cells; WS2 r4 "
                f"{WS2X['map_voltage_V']:.0f} V map chain; all electrical "
                "quantities bus-side (R12)\n")
        f.write("# SOC is fraction of USABLE bus energy, not of nameplate\n")
        f.write(",".join(c for c, _ in _TRACE_COLS) + "\n")
        _n = len(_tr["t_s"])
        _cols = [_tr[c] for c, _ in _TRACE_COLS]
        _fmts = [fm for _, fm in _TRACE_COLS]
        for _i in range(_n):
            f.write(",".join(fm.format(col[_i])
                             for col, fm in zip(_cols, _fmts)) + "\n")
    _TRACE_FILES[f"{_case}_seed{_sd}"] = dict(file=_tf, rows=_n)
_trace_file = _TRACE_FILES["nominal_seed23"]["file"]
_SD_TRACE = _SD_TRACES[("nominal", 23)]
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
    # ------------------------------------------------------------------
    # KX r2 / adjudication KX-m4: the interpretation, stated. The KX round
    # asserted "one per run" (R34's own words, and the trace header's)
    # while emitting one trace for 24 ordered mode-(b) runs, and never
    # said which reading it meant.
    # ------------------------------------------------------------------
    r34_interpretation=(
        "[WS4-DECLARED] R34 reads 'every pipeline exports a 10 Hz trace "
        "file per run'. WS4 takes 'run' to mean a PIPELINE run, not each "
        "simulated realisation: this pipeline executes 24 ordered mode-(b) "
        "runs plus 24 companion (b') runs plus the brackets and "
        "sensitivities (168 simulated runs in the KX section alone), and "
        "emitting all of them at 10 Hz would be ~132 MB of committed "
        "artefact for the ordered set alone. Under that reading one trace "
        "would suffice; WS4 emits one per ORDERED CASE at the reference "
        "seed instead, so R34's stated consumer (the WS10 exhibit / "
        "simulator) has a full-rate witness of each ordered CASE, and the "
        "5 s SOC trajectories cover all 24 ordered runs. If the lead rules "
        "for the per-simulated-run reading, run_ws4.py's "
        "R34_TRACE_ALL_ORDERED_RUNS constant emits all 24 with no other "
        "change. Flagged to the lead in s12 as a clarification request, "
        "not self-resolved."),
    r34_all_ordered_runs_emitted=R34_TRACE_ALL_ORDERED_RUNS,
    ordered_mode_b_runs=len(KX_CASES) * len(REG_SEEDS),
    traces_emitted_n=len(_TRACE_FILES),
    traces_by_case={k: v["file"] for k, v in sorted(_TRACE_FILES.items())},
    trace_rows_by_case={k: v["rows"] for k, v in sorted(_TRACE_FILES.items())},
    trace_10Hz=_trace_file,
    trace_10Hz_rows=len(_SD_TRACE["t_s"]),
    trace_10Hz_note=("the nominal reference-seed trace, retained under its "
                     "KX name so consumers pinned to it do not break"),
    soc_trajectories=_soc_file,
    soc_trajectories_covers_runs=len(_SD_SOC),
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
_ss_starts = [e["starts_per_8h_shift"] for e in ens]
_ss_flh = [e["fuel_l_per_h"] for e in ens]


def _ss_gov(vals, kind):
    i = int(np.argmax(vals)) if kind == "max" else int(np.argmin(vals))
    return (f"seed {SUB_SEEDS[i]} of the enumerated "
            f"{len(SUB_SEEDS)}-seed VOLT-SUB ensemble [V1 start-stop, "
            "0.8 kWh hysteresis]")


SS["ensemble_hyst_0.8kWh"] = dict(
    starts_per_8h_shift=_ss_starts,
    starts_per_8h_min=min(_ss_starts),
    # R14 (KX r3 construction sweep): min/max over the enumerated VOLT-SUB
    # seed set, previously exported unlabelled.
    starts_per_8h_min_governing_case=_ss_gov(_ss_starts, "min"),
    starts_per_8h_max=max(_ss_starts),
    starts_per_8h_max_governing_case=_ss_gov(_ss_starts, "max"),
    fuel_l_per_h=_ss_flh,
    fuel_l_per_h_min=min(_ss_flh),
    fuel_l_per_h_min_governing_case=_ss_gov(_ss_flh, "min"),
    fuel_l_per_h_max=max(_ss_flh),
    fuel_l_per_h_max_governing_case=_ss_gov(_ss_flh, "max"))
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

# --- KX r2 / adjudication KX-m6: the SUPERSEDED r1 rows, carried as a
# literal historical record so the changelog's before/after numbers are
# rendered from JSON and pinned, not transcribed by hand.
R["heat_ledger_ws6"]["series_duty_v2_cycle_average_kx_r1_superseded"] = dict(
    _note=("KX round-1 values, SUPERSEDED by adjudication KX-m6. "
           "Constructed as ensemble max ENERGY / the reference seed's "
           "duration, which is not the maximum of the quantity. Retained "
           "as a literal so the r2 changelog's before/after is a rendering "
           "and not a transcription. NOT a live figure - consume the "
           "series_duty_v2_*_cycle_average rows."),
    construction="max(energy over 8 seeds) / per_seed['23'].duration_s",
    engine_rejection_avg_kW=dict(nominal=72.55157571545092,
                                 cda_5_4=86.29487052804603,
                                 alt2000m_45C=59.738549020587584),
    generator_loss_avg_kW=dict(nominal=2.4385599075764177,
                               cda_5_4=2.839620718733693,
                               alt2000m_45C=2.0059115626603305),
    electric_chain_loss_avg_kW=dict(nominal=4.22398212399598,
                                    cda_5_4=4.724173290158409,
                                    alt2000m_45C=3.793377243714757),
    understatement_pct=dict(
        nominal=100.0 * (SD_HEAT["series_duty_v2_nominal_cycle_average"][
            "engine_rejection_avg_kW"] - 72.55157571545092)
        / 72.55157571545092,
        cda_5_4=100.0 * (SD_HEAT["series_duty_v2_cda_5.4_cycle_average"][
            "engine_rejection_avg_kW"] - 86.29487052804603)
        / 86.29487052804603,
        alt2000m_45C=100.0 * (SD_HEAT[
            "series_duty_v2_alt2000m_45C_cycle_average"][
                "engine_rejection_avg_kW"] - 59.738549020587584)
        / 59.738549020587584))

# --- KX r2 / adjudication KX-m7: the transient rows checked against R20's
# declared radiator design point, explicitly, so a cooling owner reading a
# cycle-mean row is not surprised by the duty's transients.
# ---------------------------------------------------------------------------
# KX r3 / adjudication KX2-M1. The KX r2 block exported
# `r20_survives_on_the_2min_window: true`, built as
#     max(rows[c] for c in KX_CASES if c == "alt2000m_45C") <= design
# - a maximum over ONE case, written so that it reads as a maximum over
# the enumerated three-case set, and exported beside a three-case worst
# 21% ABOVE the design point. The scoping that would make it defensible
# (the other two cases are not at R20's +45 C ambient) was stated in
# prose and never quantified, and WS4 exports no ratified radiator
# capability-versus-ambient model.
#
# This round does three separate things and keeps them separate:
#   1. the ABSOLUTE comparison, as a real max/min over the enumerated
#      three-case set, with the exceeding cases enumerated;
#   2. the scoped single-case statement, under a field name that carries
#      its scope;
#   3. a WS4-DECLARED linear-ITD ambient sensitivity that QUANTIFIES the
#      previously-asserted scoping argument, including its break-even -
#      explicitly a sensitivity, not a capability model, and NOT the
#      source of any survival verdict.
# The R20/ESC-4 question itself is escalated (ESC-12), not self-resolved.
# ---------------------------------------------------------------------------
_R20_DESIGN_KW = split_corner["radiator_package_kW"]
_R20_DESIGN_AMB_C = 45.0
_R_AIR = 287.05                       # J/(kg K), dry air
_ISA_P0 = 101325.0                    # Pa


def _isa_pressure_pa(alt_m):
    return _ISA_P0 * (1.0 - 2.25577e-5 * alt_m) ** 5.25588


# [WS4-DECLARED] each ordered case's AIR temperature, derived from the
# case's own air density and its altitude through the ideal gas law -
# i.e. from the same number the road-load model uses, not asserted. The
# derivation is validated by the corner: it reproduces the case's
# declared +45 C to the hundredth of a degree.
_R20_CASE_ALT_M = {"nominal": 0.0, "cda_5.4": 0.0, "alt2000m_45C": 2000.0}
_R20_CASE_AMB_C = {
    c: _isa_pressure_pa(_R20_CASE_ALT_M[c])
    / (KX_CASES[c]["veh"].rho_air * _R_AIR) - 273.15 for c in KX_CASES}
# declared coolant top-tank sensitivity set for the ITD ratio
_R20_TOP_TANK_C = (95.0, 105.0, 115.0, 125.0)

_r20_rows = {}
for c in KX_CASES:
    _row = SD_HEAT[f"series_duty_v2_{c}_cycle_average"]
    _r20_rows[c] = dict(
        air_temperature_C_declared=_R20_CASE_AMB_C[c],
        altitude_m=_R20_CASE_ALT_M[c],
        rho_air_kg_per_m3=KX_CASES[c]["veh"].rho_air,
        radiator_package_peak_kW=_row["radiator_package_peak_kW"],
        radiator_package_peak_kW_governing_case=_row[
            "radiator_package_peak_kW_governing_case"],
        radiator_package_2min_max_kW=_row["radiator_package_2min_max_kW"],
        radiator_package_2min_max_kW_governing_case=_row[
            "radiator_package_2min_max_kW_governing_case"],
        radiator_package_10min_max_kW=_row["radiator_package_10min_max_kW"],
        radiator_package_10min_max_kW_governing_case=_row[
            "radiator_package_10min_max_kW_governing_case"],
        exceeds_r20_design_point_on_peak=bool(
            _row["radiator_package_peak_kW"] > _R20_DESIGN_KW),
        exceeds_r20_design_point_on_2min=bool(
            _row["radiator_package_2min_max_kW"] > _R20_DESIGN_KW),
        # the declared ITD capability ratio, per top-tank temperature
        duty_over_capability_2min_by_top_tank_C={
            f"{tt:.0f}": (_row["radiator_package_2min_max_kW"]
                          / (_R20_DESIGN_KW * (tt - _R20_CASE_AMB_C[c])
                             / (tt - _R20_DESIGN_AMB_C)))
            for tt in _R20_TOP_TANK_C})

_r20_2min = {c: _r20_rows[c]["radiator_package_2min_max_kW"]
             for c in KX_CASES}
_r20_2min_gov = {c: _r20_rows[c]["radiator_package_2min_max_kW_governing_case"]
                 for c in KX_CASES}
_r20_worst_2min, _r20_worst_2min_gov = _case_worst(
    _r20_2min, "max", _r20_2min_gov, list(KX_CASES),
    zero_is_degenerate=False)
_R20_TIE_TOL = 1e-6
_r20_2min_tied = [c for c in KX_CASES
                  if abs(_r20_2min[c] - _r20_worst_2min) <= _R20_TIE_TOL]
_r20_exceeding = [c for c in KX_CASES
                  if _r20_rows[c]["exceeds_r20_design_point_on_2min"]]
_r20_exceeding_peak = [c for c in KX_CASES
                       if _r20_rows[c]["exceeds_r20_design_point_on_peak"]]
# worst declared-ITD ratio over the enumerated set, per top tank
_r20_ratio_worst = {}
for _tt in _R20_TOP_TANK_C:
    _k = f"{_tt:.0f}"
    _v, _gov = _case_worst(
        {c: _r20_rows[c]["duty_over_capability_2min_by_top_tank_C"][_k]
         for c in KX_CASES}, "max", _r20_2min_gov, list(KX_CASES),
        zero_is_degenerate=False)
    _r20_ratio_worst[_k] = dict(worst_ratio=_v, worst_ratio_governing_case=_gov,
                                all_cases_within_capability=bool(_v <= 1.0))
# break-even coolant top tank: the T_top at which the worst EXCEEDING
# case's 2-min duty exactly equals its declared-ITD capability.
_r20_be_case = max(_r20_exceeding, key=lambda c: _r20_2min[c]) \
    if _r20_exceeding else None
if _r20_be_case is not None:
    _q = _r20_2min[_r20_be_case] / _R20_DESIGN_KW
    _ta = _R20_CASE_AMB_C[_r20_be_case]
    _r20_break_even_top_tank_C = (_ta - _q * _R20_DESIGN_AMB_C) / (1.0 - _q)
else:
    _r20_break_even_top_tank_C = None

# --- KX r3, second-order point the sensitivity itself raises: R20/ESC-4
# rules WHICH CASE SIZES the radiator, not merely whether every case is
# inside capability. Under the declared ITD model the ordered cases'
# normalised ratios cross at
#     T_top = (Q_i x T_j - Q_j x T_i) / (Q_i - Q_j),
# and above that top-tank temperature the DESIGN CASE changes hands even
# though every case is still inside capability. This is the number
# R20/ESC-4 actually turns on, and it is NOT the break-even above.
_r20_cross = []
for _i in KX_CASES:
    for _j in KX_CASES:
        if _i >= _j:
            continue
        _qi, _qj = _r20_2min[_i], _r20_2min[_j]
        _ti, _tj = _R20_CASE_AMB_C[_i], _R20_CASE_AMB_C[_j]
        if abs(_qi - _qj) < 1e-9 or abs(_ti - _tj) < 1e-9:
            continue
        _tx = (_qi * _tj - _qj * _ti) / (_qi - _qj)
        if _tx > max(_R20_CASE_AMB_C.values()):
            # which case governs just above the crossing
            _eps = _tx + 1.0
            def _ratio(c, tt):
                return (_r20_2min[c]
                        / (_R20_DESIGN_KW * (tt - _R20_CASE_AMB_C[c])
                           / (tt - _R20_DESIGN_AMB_C)))
            _hi = max((_i, _j), key=lambda c: _ratio(c, _eps))
            _lo = _i if _hi == _j else _j
            _r20_cross.append(dict(top_tank_C=_tx, below=_lo, above=_hi,
                                   pair=[_i, _j]))
_r20_cross.sort(key=lambda d: d["top_tank_C"])
_r20_first_cross = _r20_cross[0] if _r20_cross else None

R["heat_ledger_ws6"]["series_duty_v2_transient_vs_R20_design_point"] = dict(
    ruling="R20 / ESC-4 (radiator design case = the R6 corner)",
    r20_design_point_radiator_package_kW=_R20_DESIGN_KW,
    r20_design_point_air_temperature_C=_R20_DESIGN_AMB_C,
    r20_design_point_basis=("engine at 132 kW x derate continuous, 2,000 m "
                            "/ +45 C, x the declared 48% radiator-package "
                            "share - heat_ledger_ws6 -> "
                            "V2_R6_corner_continuous"),
    cases=_r20_rows,
    # --- (1) THE ABSOLUTE COMPARISON, over the whole enumerated set
    absolute_kW_comparison=dict(
        _construction=("every field in this object is an explicit max/min "
                       "over the SAME enumerated ordered case set "
                       f"{_case_set_str(list(KX_CASES))}, comparing "
                       "absolute package kW against a design point stated "
                       "in +45 C air. It is NOT ambient-normalised, and "
                       "WS4 says so rather than filtering the set."),
        worst_2min_kW=_r20_worst_2min,
        worst_2min_governing_case=_r20_worst_2min_gov,
        worst_2min_tied_cases_within_1e_6_kW=_r20_2min_tied,
        worst_2min_tie_note=("nominal and cda_5.4 both sit at the engine's "
                             "emergency-band ceiling through the window, "
                             "so their 2-min maxima agree to ~4e-12 kW; "
                             "the governing-case label is a float-level "
                             "tie-break and both cases are named."),
        cases_exceeding_design_point_on_2min=_r20_exceeding,
        n_cases_exceeding_design_point_on_2min=len(_r20_exceeding),
        cases_exceeding_design_point_on_peak=_r20_exceeding_peak,
        all_ordered_cases_within_design_point_on_2min=bool(
            not _r20_exceeding),
        exceedance_pct_of_design_point_worst=100.0 * (
            _r20_worst_2min / _R20_DESIGN_KW - 1.0)),
    # --- (2) the scoped single-case statement, named for its scope
    r20_survives_on_the_2min_window_at_alt2000m_45C_only=bool(
        _r20_rows["alt2000m_45C"]["radiator_package_2min_max_kW"]
        <= _R20_DESIGN_KW),
    r20_survives_scope_note=(
        "this field is a statement about ONE case - alt2000m_45C, the "
        "only ordered case in R20's own +45 C ambient - and its name says "
        "so. KX r2 exported the same boolean as "
        "`r20_survives_on_the_2min_window`, built as a max over a "
        "comprehension filtered down to that one case, beside a "
        "three-case worst 21% above the design point (adjudication "
        "KX2-M1). It is NOT a verdict over the ordered case set and must "
        "not be consumed as one."),
    # --- (3) the declared ambient sensitivity that quantifies the scoping
    ambient_normalised_sensitivity=dict(
        _status="[WS4-DECLARED SENSITIVITY - NOT A CAPABILITY MODEL]",
        _model=("a liquid-to-air HT package at FIXED air flow, coolant "
                "flow and geometry rejects Q = UA_eff x ITD, with ITD = "
                "(coolant top tank - inlet air). Anchoring UA_eff on "
                "R20's declared design point (Q_design at +45 C air) "
                "gives capability(T_air) = Q_design x (T_top - T_air) / "
                "(T_top - 45). Air DENSITY is deliberately ignored, which "
                "is conservative: the corner is the thin-air case, so the "
                "sea-level cases would gain further capability that this "
                "ratio does not credit."),
        _assumptions=("(i) the fan/airflow state is the same in all three "
                      "cases; (ii) UA_eff is constant, i.e. the same "
                      "hardware; (iii) linearity over 21-45 C air; (iv) "
                      "the 2-min window is the right thermal window. None "
                      "of the four is WS4's to ratify - the radiator is "
                      "WS6's and the design case is R20/ESC-4's."),
        case_air_temperature_C=_R20_CASE_AMB_C,
        case_air_temperature_basis=(
            "[WS4-DECLARED] T = p_ISA(altitude) / (rho_case x R_air), "
            "R_air 287.05 J/(kg K), from each case's OWN air density. "
            "Validation: the corner returns "
            f"{_R20_CASE_AMB_C['alt2000m_45C']:.2f} C against its declared "
            "+45.0 C, so the derivation reproduces the case definition."),
        top_tank_C_set=list(_R20_TOP_TANK_C),
        duty_over_capability_worst_by_top_tank_C=_r20_ratio_worst,
        # --- WHICH CASE GOVERNS: the question R20/ESC-4 actually asks
        design_case_crossovers=_r20_cross,
        design_case_crossover_top_tank_C=(
            _r20_first_cross["top_tank_C"] if _r20_first_cross else None),
        design_case_below_crossover=(
            _r20_first_cross["below"] if _r20_first_cross else None),
        design_case_above_crossover=(
            _r20_first_cross["above"] if _r20_first_cross else None),
        design_case_crossover_reading=(
            "R20/ESC-4 rules WHICH CASE SIZES the radiator. Under the "
            "declared ITD model the R6 corner governs only while the "
            "coolant top tank is BELOW this temperature; above it the "
            "sea-level high-load cases demand more capability relative to "
            "their own ambient, even though every case is still inside "
            "capability until the separate break-even below. The "
            "crossover sits inside the range a pressurised heavy-duty "
            "coolant system can actually run, so ESC-4's design case is "
            "live, not settled, on WS4's own declared sensitivity. WS4 "
            "does not rule it."),
        break_even_top_tank_C=_r20_break_even_top_tank_C,
        break_even_case=_r20_be_case,
        break_even_reading=(
            "the coolant top-tank temperature at which the worst "
            "EXCEEDING ordered case's 2-min duty would exactly equal its "
            "declared-ITD capability, i.e. where the package would run "
            "out of capability outright. It sits far above any physical "
            "diesel HT coolant cap, which is WHY the r2 scoping argument "
            "pointed the right way ON THE CAPABILITY QUESTION. It is NOT "
            "the answer to R20/ESC-4, which asks which case GOVERNS - see "
            "design_case_crossover_top_tank_C, which is far lower and "
            "inside the physical range. Both are results of this declared "
            "sensitivity, not measurements, and WS4 converts neither into "
            "an R20 verdict."),
        what_ws4_does_not_have=(
            "a ratified radiator capability-versus-ambient model. WS4 "
            "measures DUTY; R20/ESC-4 rules on the design CASE, which is "
            "a capability question. The sensitivity above quantifies the "
            "argument the KX r2 block asserted; it does not settle it.")),
    escalation="ESC-12 (R20 / ESC-4) - raised, not self-resolved",
    _design_case_note=(
        "R20/ESC-4 asks WHICH CASE SIZES the radiator. WS4 measures duty, "
        "not capability, so it cannot answer that - see "
        "ambient_normalised_sensitivity -> design_case_crossover_top_tank_C "
        "and ESC-12."),
    reading=("the ordered duty's INSTANTANEOUS radiator-package peak "
             "exceeds R20's declared design point at EVERY ordered case, "
             "and the 2-MINUTE rolling maximum exceeds it at two of the "
             "three - nominal and cda_5.4, by 21% - while the "
             "alt2000m_45C corner, the only ordered case in R20's own "
             "+45 C ambient, stays under it. On ABSOLUTE kW, therefore, "
             "the ordered set does NOT stay inside R20's design point, "
             "and WS4 exports that plainly. Whether R20/ESC-4's "
             "'radiator design case = the R6 corner' survives depends on "
             "comparing each case against capability AT ITS OWN AMBIENT, "
             "which needs a capability model WS4 does not have and does "
             "not invent: the declared ITD sensitivity above quantifies "
             "the argument and its break-even, and the ruling question "
             "goes to the lead as ESC-12. The rows exist at all because "
             "the KX round gave WS6 a 59.7 kW cycle mean for a case "
             "carrying a >200 kW transient, and program rule 7 asks for "
             "heat by component AND CASE, not by cycle mean "
             "(adjudication KX-m7)."))

# ---------------------------------------------------------------------------
# 7b. CONSTRUCTION SWEEP (KX r3)
#
# The lead's standing diagnosis of this program's repeat failure mode is
# the PARTIAL CORRECTION. Adjudication KX2-M1/M2/M3 are one defect family
# - a machine-readable summary whose CONSTRUCTION does not match its NAME
# - and KX r2 both fixed an instance of it (KX-m6) and re-introduced it in
# three new blocks in the same round. So this round did not stop at the
# three named fields: every machine-readable aggregate in the workstream
# was enumerated and checked. This block is the record of that sweep,
# INCLUDING the places where nothing was wrong, so the next reader does
# not have to redo it.
#
# Method: (i) every max/min/median expression in run_ws4.py that reaches
# an exported field, read against the field's name; (ii) every exported
# field whose name contains max/min/worst/median/penalty/paired/at-most;
# (iii) every arithmetic expression in make_report_ws4.py that builds a
# rendered number from JSON values; (iv) every extremum over an
# enumerated set checked for an R14 governing label and for degenerate
# ties.
# ---------------------------------------------------------------------------
def _paired_one_factor(cfg):
    """The one-factor attribution delta on the PAIRED per-seed statistic,
    computed OUTSIDE the archived block for comparison only. The archived
    values are BASELINE_v3-ratified record and are not recomputed."""
    d = [cfg["per_seed"][str(sd)]["margin_pct"]
         - G1_PRIOR["per_seed"][str(sd)]["margin_pct"] for sd in REG_SEEDS]
    return dict(paired_delta_pp_min=min(d),
                paired_delta_pp_median=float(np.median(d)),
                paired_delta_pp_max=max(d),
                paired_delta_pp_min_governing_case=(
                    f"seed {REG_SEEDS[int(np.argmin(d))]} of the enumerated "
                    "8-seed VOLT-REG ensemble"))


_SWEEP_CORRECTED = {
    "companion_bp_capability_comparison.fuel_kWh_per_km_by_case."
    "bp_penalty_pct_on_median": dict(
        finding="KX2-M3(a)",
        kx_r2_construction="ratio of ensemble medians, named 'paired'",
        corrected_to="paired per-seed delta, 8-seed envelope, R14 labels",
        kx_r2_value={c: SD["companion_bp_capability_comparison"][
            "fuel_kWh_per_km_by_case"][c][
                "bp_penalty_pct_ratio_of_ensemble_medians"]
            for c in KX_CASES},
        corrected_value={c: _BP_PAIRED["by_case"][c]["median"]
                         for c in KX_CASES}),
    "r16_pack_acceptance_bracket.fuel_penalty_pct_vs_ordered": dict(
        finding="KX2-M3(b)",
        kx_r2_construction="ratio of ensemble maxima, named 'penalty'",
        corrected_to="paired per-seed delta, 8-seed envelope, R14 labels",
        kx_r2_value=_r16b_fuel_pp,
        corrected_value={c: _R16B_PAIRED["by_case"][c]["median"]
                         for c in KX_CASES},
        corrected_worst_max=_R16B_PAIRED["worst_max_pct"],
        sign_flip_at_nominal=bool(
            _r16b_fuel_pp["nominal"] < 0.0
            <= _R16B_PAIRED["by_case"]["nominal"]["median"])),
    "engine_continuous_rating_bracket.fuel_penalty_pct_vs_ordered": dict(
        finding="KX2-M3(c)",
        kx_r2_construction=("ratio of ensemble maxima; the 'max' was a "
                            "maximum over three negatives"),
        corrected_to="paired per-seed delta, 8-seed envelope, R14 labels",
        kx_r2_value=_m1b_fuel_pp,
        corrected_value={c: _M1B_PAIRED["by_case"][c]["median"]
                         for c in KX_CASES},
        conclusion_unchanged=bool(_M1B_PAIRED["worst_max_pct"] <= 0.0)),
    "r22d_coast_spin_member.unbooked_pp_max": dict(
        finding="FOUND BY THE SWEEP - not in FINDINGS_KX_r2.md",
        kx_r2_construction=("max over cases of a ratio of THREE "
                            "independently extremised ensemble numbers "
                            "(max shaft kWh + max bus kWh over max fuel "
                            "kg), rendered as 'at most X pp of cycle "
                            "fuel'"),
        corrected_to=("priced per seed on that seed's own coast energies "
                      "over its own fuel, then enveloped (R9/R14/R36)"),
        kx_r2_value=_c_pp_r2,
        corrected_value=_c_pp),
    "heat_ledger_ws6.series_duty_v2_transient_vs_R20_design_point."
    "r20_survives_on_the_2min_window": dict(
        finding="KX2-M1",
        kx_r2_construction=("max over a three-case comprehension filtered "
                            "to ONE case, named as a set-wide verdict"),
        corrected_to=("withdrawn; replaced by an absolute comparison over "
                      "the whole enumerated set, a scope-named "
                      "single-case statement, a declared ambient "
                      "sensitivity, and ESC-12"),
        kx_r2_value=True,
        corrected_value=dict(
            all_ordered_cases_within_design_point_on_2min=bool(
                not _r20_exceeding),
            cases_exceeding_design_point_on_2min=_r20_exceeding)),
    "r16_binding_analysis.cold_side_binding_cell_C_pack_quantity": dict(
        finding="KX2-M2",
        kx_r2_construction=("np.interp RIGHT-EDGE CLAMP presented as a "
                            "curve crossing, beside two genuine "
                            "crossings"),
        corrected_to=("withdrawn; replaced by the measured statement "
                      "(exceeded at every tabulated cell temperature) "
                      "and an in-range assertion on every remaining "
                      "interpolation"),
        kx_r2_value=10.0,
        corrected_value=dict(
            exceeds_acceptance_at_every_tabulated_cell_C=_PACK_BINDING[
                "exceeds_acceptance_at_every_tabulated_cell_C"],
            min_exceedance_kW_over_the_curve=_PACK_BINDING[
                "min_exceedance_kW_over_the_curve"],
            least_binding_cell_C=_PACK_BINDING["least_binding_cell_C"])),
    "report M1PEAKPCT (ESC-10's '% of the continuous rating')": dict(
        finding="FOUND BY THE SWEEP - not in FINDINGS_KX_r2.md",
        kx_r2_construction=("a max over ALL three cases divided by ONE "
                            "case's continuous rating; correct only "
                            "because the peak's governing cases happen to "
                            "be the two underated ones"),
        corrected_to=("per case, per seed, against that case's own "
                      "derated rating, then enveloped (R14)"),
        kx_r2_value=100.0 * SD["companion_bp_capability_comparison"][
            "axes"]["engine_shaft_peak_kW"]["mode_b_block_of_record"][
                "worst_case_max"] / ENG_CONT_KW_BY_CASE["nominal"],
        corrected_value=_eng_pct_worst),
    "brackets: worst_unserved_governing_case (x2)": dict(
        finding="KX2-m1",
        kx_r2_construction=("max(KX_CASES, key=...) over three exact "
                            "zeros - Python's first-key tie-break "
                            "presented as a governing case"),
        corrected_to=("_case_worst() refuses to name a governing case "
                      "for a full tie and names all tied members for a "
                      "partial one; applied to every case-set extremum "
                      "in the workstream"),
        kx_r2_value="nominal",
        corrected_value=SD["r16_pack_acceptance_bracket"][
            "worst_unserved_governing_case"]),
}

_SWEEP_CLEAN = {
    "gate_g1[*].ensemble.margin_pct_{min,median,max}": (
        "CLEAN and is the reference construction. The margin is formed "
        "PER SEED as 100 x (b - a) / b and only then enveloped - the "
        "paired statistic R36 mandates. This is the construction the "
        "adjudicator pointed at as already present in this workstream's "
        "own code, and the three corrected blocks now match it."),
    "gate_g1_one_factor.*.delta_pp_min": (
        "EXAMINED, NOT CHANGED. Construction is a difference of ensemble "
        "MINIMA, the name says 'delta of the min', and _DELTA_GOV states "
        "it inline. The values are BASELINE_v3-ratified record "
        "(-7.01 pp map-vs-scalar, -1.77 pp spin drag) and an archived "
        "block's values may not move. The paired per-seed companion is "
        "measured below for comparison only."),
    "gate_g1_one_factor.*.delta_pp_median": (
        "EXAMINED. Same construction; not a worst-case field, so R14 does "
        "not ask for a governing case. It carried no construction "
        "statement where its `_min` sibling did, so one was added "
        "(`delta_pp_median_construction`). No value moved."),
    "gate_g1_map_vintage_spread.spread_pp_*": (
        "CLEAN. max - min over the enumerated vintage member list, all "
        "members the same statistic (each vintage's ensemble margin_pct_"
        "min). The name says 'spread' and the construction is a spread."),
    "series_duty_v2.cases[*].ensemble.* (_sd_envelope)": (
        "CLEAN. min/median/max over the enumerated 8-seed set of per-seed "
        "values, every extremum carrying its governing seed. 57 fields x "
        "3 cases, plus companion, brackets and probe on the same helper."),
    "companion_bp_capability_comparison.axes[*].worst_case_max": (
        "CLEAN. max over cases of each case's own 8-seed max of the SAME "
        "quantity, i.e. a true max over the 3 x 8 union, with case and "
        "seed inline. A max of maxima IS the max here - unlike a ratio of "
        "maxima, which is not."),
    "unserved_energy_verdict.worst_case_governing_case": (
        "CLEAN, and was the model for the KX2-m1 fix: it already refused "
        "to name a governing case for an all-zero tie."),
    "r16_binding_analysis.{regen_leg_bound_any_sample,"
    "pack_charge_bound_by_r16_any_sample}": (
        "CLEAN. Both are 'any sample' booleans built as max-over-the-set "
        "> 0, which is what 'any' means. The stronger measured statement "
        "(nonzero on EVERY seed of EVERY case) was not exported and now "
        "is, as `pack_charge_bound_on_every_ordered_seed` - a min > 0."),
    "r16_binding_analysis.pulse10s_covers_the_excursions": (
        "CLEAN. A boolean over the worst (longest) excursion in the "
        "enumerated set against the 10 s window; the underlying max and "
        "its governing case are exported separately."),
    "chain_boundary_exposure.*.one_sided_pp_locked_linear / total_pp_linear": (
        "CLEAN. Priced PER SEED (that seed's unbooked bus energy over "
        "that seed's own fuel) and only then enveloped - already the "
        "paired construction. This is why the F2/D5 pp figures did not "
        "move in this round."),
    "r8_power_envelope_bracket.worst_unserved_kWh": (
        "CLEAN as a value - a genuine, non-degenerate max over the "
        "enumerated set (0.61 kWh at alt2000m_45C). Its LABEL was a bare "
        "case name naming neither the set nor the seed; upgraded to the "
        "program's fuller form for consistency."),
    "heat_ledger_ws6.series_duty_v2_*_cycle_average.* (KX-m6 rows)": (
        "CLEAN. Each row is the max of the PER-SEED cycle averages with "
        "its own governing seed - the KX r2 fix, verified independently "
        "by the r2 adjudicator (V7) and untouched here. The derived "
        "radiator-package rows inherit those maxima and now carry the "
        "same labels (KX2-m2)."),
    "sanity.* and *_ref_seed fields": (
        "CLEAN. Reference-seed scalars, named `_ref_seed`; not extrema "
        "over a set, so R14 does not apply."),
    "make_report_ws4.py arithmetic": (
        "SWEPT. Exactly three expressions in the generator build a "
        "rendered number from JSON: GAP and BSGAP (5.0 - an ensemble min, "
        "the kill-criterion gap - name matches construction) and "
        "M1PEAKPCT, which is corrected above. Every other rendered number "
        "is a format of a single JSON value, which verify_ws4.py pins."),
    "v1_start_stop.ensemble_hyst_0.8kWh.*": (
        "CLEAN as values - min/max over the enumerated VOLT-SUB seed set. "
        "R14 governing labels were absent and were added; no value moved."),
    "soc_window_check.*_min": (
        "CLEAN as values. `t_below_gate_s_min`, `soc_usable_min` and "
        "`soc_nameplate_min` are minima over the enumerated 8-seed set "
        "and were unlabelled; labels added, plus an explicit "
        "cross-reference to the full-rate `soc_min_min` for the same "
        "quantity (r2 adjudicator's note 5 for the lead)."),
}

R["construction_sweep_kx_r3"] = dict(
    _purpose=("KX r3 record of the workstream-wide sweep for the defect "
              "family named in adjudication KX2-M1/M2/M3: a "
              "machine-readable summary whose CONSTRUCTION does not match "
              "its NAME. Recorded so the sweep is auditable and so the "
              "clean areas do not have to be re-swept."),
    _rulings="BASELINE_v5 R36; R14; R9",
    corrected=_SWEEP_CORRECTED,
    examined_clean=_SWEEP_CLEAN,
    gate_g1_one_factor_paired_companion=dict(
        _status=("FOR COMPARISON ONLY - the archived attribution rows are "
                 "BASELINE_v3-ratified record and are NOT recomputed. "
                 "Exported outside gate_g1 so the archive stays frozen "
                 "(adjudication KX2-m3)."),
        spin_drag_alone=_paired_one_factor(G1_SPIN),
        map_vs_scalar_alone=_paired_one_factor(G1_MAPS),
        both_g1r=_paired_one_factor(G1["nominal"]),
        archived_delta_pp_min=dict(
            spin_drag_alone=R["gate_g1_one_factor"]["spin_drag_alone"][
                "delta_pp_min"],
            map_vs_scalar_alone=R["gate_g1_one_factor"][
                "map_vs_scalar_alone"]["delta_pp_min"],
            both_g1r=R["gate_g1_one_factor"]["both_g1r"]["delta_pp_min"])),
    counts=dict(
        fields_corrected=len(_SWEEP_CORRECTED),
        areas_examined_clean=len(_SWEEP_CLEAN),
        named_in_findings=sum(
            1 for v in _SWEEP_CORRECTED.values()
            if not v["finding"].startswith("FOUND BY THE SWEEP")),
        found_by_the_sweep=sum(
            1 for v in _SWEEP_CORRECTED.values()
            if v["finding"].startswith("FOUND BY THE SWEEP"))),
    _reading=("five of the seven corrected entries are the findings the "
              "adjudication named; two - the R22d unbooked-pp bound and "
              "ESC-10's percent-of-rating - were found by the sweep and "
              "are the same defect family. No ordered value moved in "
              "either."))

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
IFACE_ENV_KEYS = IFACE_ENV_KEYS + (
    # KX r2 / adjudication KX-B1 + KX-M1 + KX-m7: the capability axes and
    # transient-heat rows the live block must carry, not only the archived
    # one. All R14-labelled by _env_subset.
    "pack_chg_above_r16_accept_s", "pack_chg_above_r16_accept_kWh",
    "pack_chg_above_r16_accept_longest_s",
    "engine_over_continuous_rating_s", "engine_over_continuous_rating_kWh",
    "engine_over_continuous_rating_longest_s", "engine_shaft_peak_kW",
    "generator_over_continuous_input_s", "generator_shaft_input_peak_kW",
    "engine_reject_peak_kW", "engine_reject_2min_max_kW",
    "engine_reject_10min_max_kW", "engine_reject_avg_kW")
IFACE_R8_KEYS = ("unserved_bus_kWh", "r8_envelope_dis_clip_s",
                 "r8_envelope_chg_shed_kWh", "fuel_kg",
                 "fuel_energy_kWh_per_km", "genset_starts")
# KX r2 / adjudication KX-B2: the companion (b') exported only fuel,
# starts and unserved - i.e. none of the three capability axes on which
# R22b and ESC-9 are actually decided. It now carries the SAME capability
# export set as the block of record.
IFACE_BP_KEYS = IFACE_R8_KEYS + (
    "pack_dis_peak_kW", "pack_chg_peak_kW", "pack_dis_over_r8_125kW_s",
    "pack_chg_over_r8_110kW_s", "pack_chg_above_r16_accept_s",
    "pack_chg_above_r16_accept_kWh", "engine_over_continuous_rating_s",
    "engine_over_continuous_rating_kWh", "engine_shaft_peak_kW",
    "generator_over_continuous_input_s", "emergency_band_s",
    "genset_starts_per_h", "genset_on_frac", "soc_min", "soc_max",
    "above_pin_engine_s", "motor_over_rating_s", "regen_bus_peak_kW",
    "engine_reject_avg_kW", "engine_reject_peak_kW",
    "engine_reject_2min_max_kW", "engine_reject_10min_max_kW")
# KX r2 / adjudication KX-m8: the sensitivity's own axes, 8-seed.
IFACE_HYST_KEYS = ("genset_starts", "genset_starts_per_h", "genset_on_frac",
                   "fuel_energy_kWh_per_km", "fuel_kg", "unserved_bus_kWh",
                   "soc_min", "soc_max", "emergency_band_s",
                   "pack_dis_peak_kW", "pack_chg_peak_kW")
IFACE_R16B_KEYS = ("unserved_bus_kWh", "r16_pack_cap_shed_kWh",
                   "r16_pack_cap_clip_s", "fuel_kg",
                   "fuel_energy_kWh_per_km", "genset_starts",
                   "pack_chg_peak_kW")
IFACE_M1B_KEYS = ("unserved_bus_kWh", "fuel_kg", "fuel_energy_kWh_per_km",
                  "soc_min", "emergency_band_s", "genset_starts",
                  "engine_over_continuous_rating_s", "engine_shaft_peak_kW",
                  "pack_dis_peak_kW")
# KX r3 / adjudication KX2-m4: the R6 rating-family probe's own axes.
IFACE_R6F_KEYS = ("engine_over_continuous_rating_s",
                  "engine_over_continuous_rating_kWh",
                  "engine_over_continuous_rating_longest_s",
                  "engine_shaft_peak_kW", "unserved_bus_kWh", "soc_min",
                  "fuel_energy_kWh_per_km", "genset_starts",
                  "pack_dis_peak_kW", "pack_chg_peak_kW")


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
            "not exist in any live architecture. FROZEN MEMBER SET (KX r3, "
            "adjudication KX2-m3): results_ws4.json -> gate_g1 -> <case> -> "
            "_raw_reference_seed is projected through the explicit "
            "53-member key list of record (run_ws4.py "
            "G1_RAW_KEYS_OF_RECORD), in the record's own key order, so "
            "the archive cannot grow when the simulator gains a field. "
            "KX r2 let 234 such members leak in - including mode-(a) "
            "over-rating counters that did not exist when the gate was "
            "run - with 0 values changed; they are withdrawn here. Every "
            "diagnostic added after 2026-08-30 belongs to the LIVE block."),
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
            # R14 (adjudication KX-m3): the _max sibling was unlabelled
            "margin_pct_ensemble_max_governing_case":
                g1n["margin_pct_max_governing_case"],
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
            # R14 (adjudication KX-m3): label present on both siblings
            "nominal_one_sided_pp_max_governing_case":
                R["chain_boundary_exposure"]["cases"]["nominal"]["envelope"]
                 ["one_sided_pp_locked_linear_max_governing_case"],
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
        # KX r2 / adjudication KX-B1: the cost of the PACK reading of R16
        "r16_pack_acceptance_bracket": {
            k: v for k, v in
            R["series_duty_v2"]["r16_pack_acceptance_bracket"].items()
            if k != "cases"},
        "r16_pack_acceptance_bracket_ensembles": {
            _c: _env_subset(
                R["series_duty_v2"]["r16_pack_acceptance_bracket"]["cases"][
                    _c]["ensemble"], IFACE_R16B_KEYS)
            for _c in R["series_duty_v2"]["r16_pack_acceptance_bracket"][
                "cases"]},
        # KX r2 / adjudication KX-M1: what the genset's own rating costs
        "engine_continuous_rating_bracket": {
            k: v for k, v in
            R["series_duty_v2"]["engine_continuous_rating_bracket"].items()
            if k != "cases"},
        "engine_continuous_rating_bracket_ensembles": {
            _c: _env_subset(
                R["series_duty_v2"]["engine_continuous_rating_bracket"][
                    "cases"][_c]["ensemble"], IFACE_M1B_KEYS)
            for _c in R["series_duty_v2"][
                "engine_continuous_rating_bracket"]["cases"]},
        # KX r3 / adjudication KX2-m4: the exposure ESC-10 asks the lead
        # to rule on, widened to R6's own rating family. NOT ordered cases.
        "r6_rating_family_probe": {
            k: v for k, v in
            R["series_duty_v2"]["r6_rating_family_probe"].items()
            if k != "cases"},
        "r6_rating_family_probe_ensembles": {
            _c: dict(
                condition=_cb["condition"],
                engine_continuous_rating_kW=_cb[
                    "engine_continuous_rating_kW"],
                **_env_subset(_cb["ensemble"], IFACE_R6F_KEYS))
            for _c, _cb in R["series_duty_v2"][
                "r6_rating_family_probe"]["cases"].items()},
        # KX r2 / adjudication KX-m8: 8-seed, not one draw. Renamed from
        # `hysteresis_sensitivity_ref_seed` because it is no longer a
        # reference-seed quantity; the reference-seed rows are retained
        # inside each case under `ref_seed` so nothing is dropped.
        "hysteresis_sensitivity": dict(
            {k: v for k, v in
             R["series_duty_v2"]["hysteresis_sensitivity"].items()
             if k != "cases"},
            _renamed_from=("series_duty_v2 -> hysteresis_sensitivity_ref_"
                           "seed (KX r1). Same sensitivity, now over the "
                           "enumerated 8-seed ensemble per R9; the r1 "
                           "reference-seed rows are under cases -> <case> "
                           "-> ref_seed."),
            cases={
                _c: dict(
                    ws3_band_ensemble=_env_subset(
                        _cb["ws3_band"]["ensemble"], IFACE_HYST_KEYS),
                    simulator_band_ensemble=_env_subset(
                        _cb["simulator_band"]["ensemble"], IFACE_HYST_KEYS),
                    ref_seed={_b: {_k: _v for _k, _v in _row.items()
                                   if _k in IFACE_SEED_KEYS}
                              for _b, _row in _cb["ref_seed"].items()})
                for _c, _cb in R["series_duty_v2"][
                    "hysteresis_sensitivity"]["cases"].items()}),
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
                # KX r2 / adjudication KX-B2: the companion now carries the
                # capability axes R22b/ESC-9 turn on, not only fuel and
                # starts. WS4 still does not choose the dispatch.
                "companion_bp_ensemble": _env_subset(
                    R["series_duty_v2"]["cases"][_c]["companion_bp"][
                        "ensemble"], IFACE_BP_KEYS),
                "companion_bp_note": R["series_duty_v2"]["cases"][_c][
                    "companion_bp"]["_note"]}
            for _c in R["series_duty_v2"]["cases"]},
        # KX r2 / adjudication KX-B2: the (b) vs (b') comparison on the
        # three capability axes, as an explicit machine-readable verdict
        # per axis. R14: each row is a max over the enumerated 3-case x
        # 8-seed set with its governing case labelled.
        "companion_bp_capability_comparison":
            R["series_duty_v2"]["companion_bp_capability_comparison"]},
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
    # KX r3: the construction sweep's own record (see 7b). Carried in the
    # interface because it is the auditable answer to "which exported
    # fields were checked, and what was found" for the whole workstream.
    "construction_sweep_kx_r3": R["construction_sweep_kx_r3"],
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
_r16a = R["series_duty_v2"]["r16_binding_analysis"]
log(f"R16 curve, REGEN LEG (enforced): binding "
    f"{_r16a['regen_leg_bound_any_sample']} (peak regen-to-pack "
    f"{_r16a['peak_regen_to_pack_kW_bus']:.1f} kW bus; binds below "
    f"{_r16a['cold_side_binding_cell_C']:.1f} C and above "
    f"{_r16a['hot_side_binding_cell_C']:.1f} C cells)")
log(f"R16 curve, PACK charge (measured, NOT enforced): binding "
    f"{_r16a['pack_charge_bound_by_r16_any_sample']} - pack charge peaks at "
    f"{_r16a['peak_pack_charge_kW_bus']:.1f} kW bus vs "
    f"{min(_ACCEPT.values()):.1f}-{max(_ACCEPT.values()):.1f} kW accepted; "
    "above acceptance for " + ", ".join(
        f"{_c} {_r16a['pack_charge_above_r16_accept_s']['per_case_min'][_c]:.1f}-"
        f"{_r16a['pack_charge_above_r16_accept_s']['per_case_max'][_c]:.1f} s"
        for _c in KX_CASES)
    + f"; longest single excursion "
    f"{_r16a['pack_charge_above_r16_accept_longest_s']['worst_case_max']:.1f} s "
    f"(10-s pulse column covers them: "
    f"{_r16a['pulse10s_covers_the_excursions']}) [KX-B1]")
_pkb = _r16a["pack_quantity_binding_analysis"]
log("R16 curve, PACK charge, on temperature (KX2-M2): acceptance is "
    f"exceeded at ALL {_pkb['n_tabulated_cells']} tabulated cell "
    f"temperatures - the continuous column peaks at "
    f"{_pkb['acceptance_curve_max_kW_bus']:.3f} kW bus at "
    f"{_pkb['acceptance_curve_max_at_cell_C']:.0f} C against the run's "
    f"{_pkb['peak_pack_charge_kW_bus']:.3f} kW, so the minimum exceedance "
    f"over the whole curve is {_pkb['min_exceedance_kW_over_the_curve']:.3f}"
    " kW; there is NO cold-side or hot-side crossing on this quantity")
_r16b = R["series_duty_v2"]["r16_pack_acceptance_bracket"]
log(f"R16 PACK-acceptance bracket (enforced): worst shed "
    f"{_r16b['worst_shed_kWh']:.3f} kWh, "
    f"worst clip {_r16b['worst_clip_s']:.1f} s, worst unserved "
    f"{_r16b['worst_unserved_kWh']:.4f} kWh, PAIRED fuel delta "
    f"{_r16b['fuel_delta_pct_paired_worst_min']:+.3f}% to "
    f"{_r16b['fuel_delta_pct_paired_worst_max']:+.3f}% "
    f"(KX r2 ratio-of-maxima said at most "
    f"{_r16b['fuel_penalty_pct_ratio_of_ensemble_maxima_max']:+.2f}%) "
    "[KX2-M3]")
_m1 = R["series_duty_v2"]["companion_bp_capability_comparison"]["axes"][
    "engine_over_continuous_rating_s"]
log("Genset above its OWN 132 kW continuous flat-rating x derate: "
    + ", ".join(
        f"{_c} {R['series_duty_v2']['cases'][_c]['ensemble']['engine_over_continuous_rating_s_min']:.1f}-"
        f"{R['series_duty_v2']['cases'][_c]['ensemble']['engine_over_continuous_rating_s_max']:.1f} s"
        for _c in KX_CASES)
    + f"; worst {_m1['mode_b_block_of_record']['worst_case_max']:.1f} s at "
    f"{_m1['mode_b_block_of_record']['worst_case_max_governing_case'].split(';')[0]}"
    f"; engine shaft peak "
    f"{max(R['series_duty_v2']['cases'][_c]['ensemble']['engine_shaft_peak_kW_max'] for _c in KX_CASES):.1f} kW "
    f"vs automotive peak {ENG_V2.peak_power_kw():.1f} kW [KX-M1]")
_cmp = R["series_duty_v2"]["companion_bp_capability_comparison"]["axes"]
log("Companion (b') on the capability axes (KX-B2): "
    + ", ".join(
        f"{_k}: b={'in' if _v['mode_b_block_of_record']['within_limit_on_every_ordered_seed'] else 'OUT'}"
        f"/bp={'in' if _v['mode_bp_companion']['within_limit_on_every_ordered_seed'] else 'OUT'}"
        for _k, _v in _cmp.items()
        if _v["mode_b_block_of_record"]["within_limit_on_every_ordered_seed"]
        is not None))
_r8b = R["series_duty_v2"]["r8_power_envelope_bracket"]
log(f"R8 power-envelope bracket (125/110 kW bus enforced): worst unserved "
    f"{_r8b['worst_unserved_kWh']:.3f} kWh "
    f"[{_r8b['worst_unserved_governing_case']}] - the ordered run's pack "
    f"discharge peaks at "
    f"{max(R['series_duty_v2']['cases'][c]['ensemble']['pack_dis_peak_kW_max'] for c in R['series_duty_v2']['cases']):.1f}"
    " kW bus")
_r6f = R["series_duty_v2"]["r6_rating_family_probe"]
log("ESC-10 widening (KX2-m4): ordered-set worst above the continuous "
    f"rating {_r6f['ordered_set_worst_over_rating_s']:.1f} s; R6 "
    f"rating-family worst {_r6f['r6_family_worst_over_rating_s']:.1f} s "
    f"({_r6f['r6_family_worst_over_rating_s_governing_case'].split(';')[0]})"
    f"; union worst {_r6f['union_worst_over_rating_s']:.1f} s; every probe "
    f"case unserved {_r6f['worst_unserved_kWh']:.4f} kWh")
_tr20 = R["heat_ledger_ws6"]["series_duty_v2_transient_vs_R20_design_point"]
log("R20/ESC-4 vs the ordered duty (KX2-M1): design point "
    f"{_tr20['r20_design_point_radiator_package_kW']:.3f} kW in +45 C air; "
    f"2-min worst {_tr20['absolute_kW_comparison']['worst_2min_kW']:.3f} kW "
    f"(+{_tr20['absolute_kW_comparison']['exceedance_pct_of_design_point_worst']:.1f}%); "
    "cases exceeding on the 2-min window: "
    + ", ".join(_tr20["absolute_kW_comparison"][
        "cases_exceeding_design_point_on_2min"])
    + "; all ordered cases within the design point on 2 min: "
    f"{_tr20['absolute_kW_comparison']['all_ordered_cases_within_design_point_on_2min']}"
    "; ambient-normalised capability model NOT held by WS4 - escalated as "
    "ESC-12")
log(f"R22d true-coast spin member (reported, not charged): up to "
    f"{R['series_duty_v2']['r22d_coast_spin_member']['unbooked_pp_max']:.3f}"
    " pp of cycle fuel")
_tf = R["series_duty_v2"]["_trace_files"]
log(f"R34 10 Hz traces ({_tf['traces_emitted_n']}, one per ordered case at "
    f"the reference seed; all {_tf['ordered_mode_b_runs']} ordered runs at "
    f"5 s in {_tf['soc_trajectories']}): "
    + ", ".join(f"{k} ({v:,} rows)"
                for k, v in zip(_tf["traces_by_case"].values(),
                                _tf["trace_rows_by_case"].values())))

with open("run_output.txt", "w") as f:
    f.write("\n".join(_LOG) + "\n")

# wall-clock goes to the console only, never into the committed artefact
# (adjudication r1 F7: run_output.txt is now byte-stable under re-run)
print(f"elapsed {time.time()-t0:.0f}s")
