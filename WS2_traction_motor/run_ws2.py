#!/usr/bin/env python3
"""WS2 entry point. Run:  python3 run_ws2.py

Deterministic (no RNG). Writes: data/*.csv, results.json, run_output.txt.
Everything REPORT_WS2.md quotes as a headline is generated here and stored
in results.json (see `headline`); check_report.py verifies the report.
"""

import contextlib
import csv
import io
import json
import math
import os
import sys
import time

import ws2_params as P
from ws2_params import (VEH, REQ, BUS, MACH, INV, THERM, RES, MAP,
                        RATIO_SWEEP, RATIO_NOM)
import ws2_machine as mc
import ws2_thermal as th
import ws2_bus as bus
import ws2_resistor as resistor
import ws2_traction as traction
import ws2_cycles as cycles

DATA = P.DATA_DIR
os.makedirs(DATA, exist_ok=True)

KMH = 3.6
RESULTS = dict(_meta=dict(
    workstream="WS2",
    generated_by="run_ws2.py",
    seed=P.SEED,
    date="2026-08-30",
    inputs=["../BASELINE_v2.md (rulings R10-R15 govern this round)",
            "R4_DIRECTIVE.md",
            "../WS1_loads_duty_cycles/results.json requirements_summary",
            "../WS1_loads_duty_cycles/data/trace_VOLT-SUB_V1_10Hz.csv",
            "../WS1_loads_duty_cycles/data/trace_VOLT-REG_V2_10Hz.csv"],
    conventions=("R9: no stochastic inputs introduced; consumed WS1 extrema "
                 "are 8-seed ensemble envelopes. Efficiencies are maps, "
                 "never scalars. Torques/speeds at motor shaft; "
                 "amplitude-invariant dq. R12: all cross-workstream "
                 "electrical quantities are BUS-SIDE; the traction chain "
                 "of record is these maps x 0.97 reduction, with NO scalar "
                 "PE member. R14: every worst-case export is an explicit "
                 "max/min over an enumerated case set, governing case "
                 "labeled inline."),
    rework=dict(round=4,
                findings_files=["FINDINGS_WS2_r1.md", "FINDINGS_WS2_r2.md",
                                "FINDINGS_WS2_r3.md"],
                addressed_r1=["WS2-F1", "WS2-F2", "WS2-F3", "WS2-F4",
                              "WS2-F5", "WS2-F6", "WS2-F7"],
                addressed_r2=["WS2-F8", "WS2-F9", "WS2-F10"],
                addressed_r3=["WS2-F11", "WS2-F12"],
                rulings_executed=["R10", "R12", "R13", "R14", "R15"]),
))


def rpm_of_kmh(v_kmh, ratio=RATIO_NOM):
    return v_kmh / KMH / VEH["r_dyn"] * ratio * 60.0 / (2 * math.pi)


def kmh_of_rpm(rpm, ratio=RATIO_NOM):
    return rpm * 2 * math.pi / 60.0 / ratio * VEH["r_dyn"] * KMH


def road_load_W(v_kmh, m, grade=0.0, CdA=None, aux_frac=1.0):
    v = v_kmh / KMH
    CdA = CdA if CdA else VEH["CdA"]
    th_ = math.atan(grade)
    F = (VEH["Crr"] * m * VEH["g"] * math.cos(th_)
         + 0.5 * VEH["rho_air"] * CdA * v * v
         + m * VEH["g"] * math.sin(th_))
    return F * v


def _max_torque_hot(omega_m, v_dc, T_wind):
    """Max |shaft torque| at omega_m, v_dc with the winding at T_wind
    (mc.max_torque uses the 120 C map convention; the R13 corner is
    judged at the 170 C crawl bookkeeping convention)."""
    hi = mc.mtpa_torque(MACH["I_peak"])
    if mc.solve_point(hi, omega_m, v_dc, T_wind=T_wind) is not None:
        return hi
    lo = 0.0
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        if mc.solve_point(mid, omega_m, v_dc, T_wind=T_wind) is None:
            hi = mid
        else:
            lo = mid
    return lo


# --------------------------------------------------------------------------
def spec_checks():
    print("== 1. Machine spec checks (VM250-HV rewind, ratio %.0f:1) =="
          % RATIO_NOM)
    out = {}
    out["params"] = {k: MACH[k] for k in
                     ("p", "psi_m", "Ld", "Lq", "Rs_20C", "I_peak")}
    out["rewind_factor"] = P.REWIND
    out["T_peak_at_Ipeak_Nm"] = mc.mtpa_torque(MACH["I_peak"])
    out["T_req_launch_Nm"] = VEH["F_trac_max"] * VEH["r_dyn"] / (
        RATIO_NOM * VEH["eta_red"])
    pp = {}
    for v in (BUS["v_min"], BUS["v_nom"], BUS["v_max"]):
        _, pk = mc.peak_power_curve(v, n=49)
        pp[str(round(v))] = pk / 1e3
    out["P_peak_kW_vs_V"] = pp
    # R3 peak >=120 kW must hold EVERYWHERE in the ruled window; the
    # capability curve is monotone in voltage, so the floor is the test.
    out["P_peak_at_floor_ok_120kW"] = bool(pp[str(round(BUS["v_min"]))]
                                           >= REQ["peak_kW"])
    out["P_peak_at_vnom_ok_150kW_target"] = bool(
        pp[str(round(BUS["v_nom"]))] >= REQ["peak_target_kW"])
    om_20kmh = rpm_of_kmh(20.0) * 2 * math.pi / 60.0
    out["T_max_at_20kmh_vmin_Nm"] = mc.max_torque(om_20kmh, BUS["v_min"])
    # R13/R4-directive winding corner: 515 Nm at the crawl band TOP
    # (25 km/h) at the 432.0 V floor, 170 C winding — this is the case
    # that BINDS the rewind factor. Verified feasible, capability stated.
    om_band = rpm_of_kmh(REQ["crawl_band_kmh"][1]) * 2 * math.pi / 60.0
    s_corner = mc.solve_point(REQ["crawl_cont_Nm"], om_band, BUS["v_min"],
                              T_wind=170.0)
    out["R13_corner_515Nm_25kmh_vmin_ok"] = bool(s_corner is not None)
    out["R13_corner_I_Apk"] = round(s_corner["I_amp"], 1)
    out["R13_corner_v_req_V"] = round(s_corner["v_req"], 1)
    out["R13_corner_v_lim_V"] = round(
        BUS["v_margin_ctrl"] * BUS["v_min"] / math.sqrt(3.0), 1)
    out["T_max_at_bandtop_vmin_170C_Nm"] = round(_max_torque_hot(
        om_band, BUS["v_min"], 170.0), 1)
    # R13: the continuous electrical basis = crawl phase current at the
    # new winding, computed as the max over the enumerated crawl cases
    # (R14). MTPA current is voltage-independent below base speed, and
    # the band-top 515 Nm case is verified same-current at the floor.
    crawl_cases = {}
    for tag, T, vk in (("crawl_510Nm_V1_10p6kmh", REQ["crawl_Nm"],
                        REQ["crawl_v_kmh"][0]),
                       ("crawl_510Nm_V2_23p6kmh", REQ["crawl_Nm"],
                        REQ["crawl_v_kmh"][1]),
                       ("R13_band_top_515Nm_25kmh", REQ["crawl_cont_Nm"],
                        REQ["crawl_band_kmh"][1])):
        s = mc.solve_point(T, rpm_of_kmh(vk) * 2 * math.pi / 60.0,
                           BUS["v_nom"], T_wind=170.0)
        s_fl = mc.solve_point(T, rpm_of_kmh(vk) * 2 * math.pi / 60.0,
                              BUS["v_min"], T_wind=170.0)
        crawl_cases[tag] = dict(
            I_Apk=round(s["I_amp"], 1),
            I_Arms=round(s["I_amp"] / math.sqrt(2.0), 1),
            same_current_at_floor=bool(
                s_fl is not None
                and abs(s_fl["I_amp"] - s["I_amp"]) < 1.0))
    out["I_cont_cases"] = crawl_cases
    gov = max(crawl_cases, key=lambda k: crawl_cases[k]["I_Apk"])
    out["I_cont_governing_case"] = gov
    out["I_cont_Apk"] = crawl_cases[gov]["I_Apk"]
    out["I_cont_Arms"] = crawl_cases[gov]["I_Arms"]
    out["I_cont_vs_455Arms_r3_ratio"] = round(
        crawl_cases[gov]["I_Arms"] / 455.0, 3)
    out["rpm_at_100kmh"] = rpm_of_kmh(100.0)
    out["emf_ll_peak_at_7200_V"] = mc.back_emf_ll_peak(7200.0)
    out["char_current_A"] = mc.char_current()
    # UCG threshold speeds: EMF(ll,pk) == bus voltage
    for v in (BUS["v_min"], BUS["v_nom"], BUS["v_max"]):
        rpm_u = v / (MACH["p"] * MACH["psi_m"] * math.sqrt(3.0)
                     * 2 * math.pi / 60.0)
        out[f"ucg_onset_rpm_at_{round(v)}V"] = rpm_u
        out[f"ucg_onset_kmh_at_{round(v)}V"] = kmh_of_rpm(rpm_u)
    # bus voltage above which no UCG exposure exists below the 7,200 rpm
    # spec speed (EMF at 7,200 rpm)
    out["v_bus_no_ucg_below_7200rpm_V"] = mc.back_emf_ll_peak(7200.0)
    # generating envelope feasibility
    om_8 = rpm_of_kmh(8.0) * 2 * math.pi / 60.0
    out["gen_370Nm_at_8kmh_ok"] = bool(
        mc.max_torque(om_8, BUS["v_min"]) >= REQ["gen_env_Nm"])
    g73 = mc.point_full(-73e3 / (7200 * 2 * math.pi / 60.0), 7200.0,
                        BUS["v_min"])
    out["gen_73kW_at_7200rpm_vmin_ok"] = bool(g73 is not None)
    # F-1 fault spec (R4): clutch open, S2 ratings.  Checked at BOTH the
    # provisional CdA 4.2 and the E13 CdA 5.4 case the baseline says motor
    # sizing must carry (F4).
    p70 = road_load_W(70.0, VEH["m_gvw"]) + 0.0
    out["F1_70kmh_flat_wheel_kW"] = p70 / 1e3
    out["F1_70kmh_shaft_kW"] = p70 / VEH["eta_red"] / 1e3
    out["F1_ok"] = bool(p70 / VEH["eta_red"] / 1e3 < REQ["S2_10min_kW"])
    p70_54 = road_load_W(70.0, VEH["m_gvw"], CdA=VEH["CdA_hi"])
    out["F1_70kmh_shaft_kW_CdA5p4"] = p70_54 / VEH["eta_red"] / 1e3
    out["F1_ok_CdA5p4"] = bool(p70_54 / VEH["eta_red"] / 1e3
                               < REQ["S2_10min_kW"])
    # actual peak DC draw at the window floor (F7b): max over the peak-
    # torque envelope of P_dc from the dq model — the operating envelope
    # the cables really see (the 160 kW bounding figure lives in bus.trade)
    best_dc = 0.0
    for k in range(60):
        rpm = 200.0 + (7400.0 - 200.0) * k / 59.0
        om = rpm * 2 * math.pi / 60.0
        tq = mc.max_torque(om, BUS["v_min"])
        r = mc.point_full(tq, rpm, BUS["v_min"])
        if r is not None and r["P_dc_W"] > best_dc:
            best_dc = r["P_dc_W"]
    out["P_dc_peak_draw_at_vmin_kW"] = round(best_dc / 1e3, 1)
    out["I_dc_peak_draw_at_vmin_A"] = round(best_dc / BUS["v_min"], 0)
    # rotor mechanical sanity
    out["rotor_tip_speed_at_7400_ms"] = (MACH["rotor_D"] / 2) * 7400 * 2 * math.pi / 60.0
    out["airgap_shear_at_peak_kPa"] = out["T_peak_at_Ipeak_Nm"] / (
        2 * (math.pi / 4) * MACH["rotor_D"] ** 2 * MACH["rotor_L"]) / 1e3

    for k, v in out.items():
        if k != "params":
            print(f"  {k}: {v if not isinstance(v, float) else round(v, 2)}")
    RESULTS["machine"] = out


# --------------------------------------------------------------------------
def topology_trade():
    """Quantified pieces of the machine-topology and one-vs-two-motor trade."""
    print("== 1b. Topology trade quantities ==")
    out = {}
    # one vs two motors (stack-length mass scaling, same electromagnetics)
    m_single = MACH["mass_kg"]
    m_each = MACH["mass_end_kg"] + (MACH["mass_kg"] - MACH["mass_end_kg"]) * 0.5
    out["mass_single_motor_kg"] = m_single
    out["mass_twin_motors_kg"] = round(2 * m_each, 1)
    out["twin_penalty_motors_kg"] = round(2 * m_each - m_single, 1)
    out["twin_penalty_second_inverter_kg"] = INV["mass_kg"]
    out["twin_penalty_total_kg"] = round(2 * m_each - m_single + INV["mass_kg"], 1)

    # induction machine at the 20% crawl: rotor cage loss with no liquid path
    # P_rotor_cu = T * omega_slip_mech; slip frequency scales with torque
    f_slip_rated = 1.5      # Hz electrical at ~255 Nm rated torque (typical)
    T_rated = 255.0
    f_slip = f_slip_rated * REQ["crawl_Nm"] / T_rated
    w_slip_mech = 2 * math.pi * f_slip / MACH["p"]
    p_rotor = REQ["crawl_Nm"] * w_slip_mech
    out["IM_crawl_rotor_loss_W"] = round(p_rotor, 0)
    out["IM_rotor_dT_over_stator_K"] = round(p_rotor / THERM["G_rs"], 0)
    # IM advantage: zero spin loss in lockup (de-excited)
    sp = mc.spin_loss(rpm_of_kmh(85.0) * 2 * math.pi / 60.0, BUS["v_nom"])
    out["PM_spin_shaft_drag_85kmh_W"] = round(sp["shaft_drag_W"], 0)
    out["PM_spin_bus_draw_85kmh_W"] = round(sp["bus_draw_W"], 0)
    out["PM_spin_total_85kmh_W"] = round(sp["total_W"], 0)
    sp100 = mc.spin_loss(rpm_of_kmh(100.0) * 2 * math.pi / 60.0, BUS["v_nom"])
    out["PM_spin_total_100kmh_W"] = round(sp100["total_W"], 0)
    for k, v in out.items():
        print(f"  {k}: {v}")
    RESULTS["topology"] = out


# --------------------------------------------------------------------------
def export_maps():
    print("== 2. Efficiency maps ==")
    t0 = time.time()
    rpms = [i * MAP["rpm_step"] for i in range(int(7400 / MAP["rpm_step"]) + 1)]
    torques = [round(-540 + i * MAP["T_step"], 1)
               for i in range(int(1080 / MAP["T_step"]) + 1)]
    files = {}
    stats = {}
    for v_dc in MAP["voltages"]:
        fn = os.path.join(DATA, f"effmap_motor_inverter_{round(v_dc)}V.csv")
        n_feas = 0
        best = (0.0, None)
        with open(fn, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rpm", "T_shaft_Nm", "feasible", "P_shaft_kW",
                        "P_dc_kW", "P_cu_kW", "P_fe_kW", "P_fw_kW",
                        "P_inv_kW", "I_amp_A", "eta"])
            for rpm in rpms:
                for T in torques:
                    if rpm == 0 and T != 0:
                        r = None  # standstill handled as dc case in thermal
                    else:
                        r = mc.point_full(T, max(rpm, 1e-3), v_dc)
                    if r is None:
                        w.writerow([rpm, T, 0] + [""] * 8)
                        continue
                    n_feas += 1
                    if r["eta"] > best[0] and T > 0:
                        best = (r["eta"], (rpm, T))
                    w.writerow([rpm, T, 1,
                                round(r["P_shaft_W"] / 1e3, 3),
                                round(r["P_dc_W"] / 1e3, 3),
                                round(r["P_cu_W"] / 1e3, 4),
                                round(r["P_fe_W"] / 1e3, 4),
                                round(r["P_fw_W"] / 1e3, 4),
                                round(r["P_inv_W"] / 1e3, 4),
                                round(r["I_amp"], 1),
                                round(r["eta"], 4)])
        files[str(round(v_dc))] = os.path.relpath(fn, P.HERE)
        stats[str(round(v_dc))] = dict(n_feasible=n_feas,
                                       best_eta=round(best[0], 4),
                                       best_eta_at=best[1])
        print(f"  {fn}: {n_feas} feasible pts, best eta {best[0]:.4f} "
              f"at {best[1]}  [{time.time()-t0:.1f}s]")
    # capability curves. The continuous-electrical column uses the R13
    # continuous current basis (crawl phase current, computed in
    # spec_checks) — the r1-r3 "I_S2 = 500 A" tier is retired (R13/F11).
    i_cont = RESULTS["machine"]["I_cont_Apk"]
    fn = os.path.join(DATA, "capability_vs_rpm.csv")
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rpm", "T_peak_432V_Nm", "T_peak_662V_Nm",
                    "T_peak_749V_Nm", "T_contelec_662V_Nm",
                    "T_cont_oilspray_662V_Nm", "T_cont_jacket_662V_Nm"])
        for rpm in range(0, 7500, 250):
            om = max(rpm, 1) * 2 * math.pi / 60.0
            row = [rpm]
            for v in MAP["voltages"]:
                row.append(round(mc.max_torque(om, v), 1))
            row.append(round(mc.max_torque(om, BUS["v_nom"], I_max=i_cont), 1))
            row.append(round(th.continuous_torque(max(rpm, 1), BUS["v_nom"],
                                                  "oilspray"), 1))
            row.append(round(th.continuous_torque(max(rpm, 1), BUS["v_nom"],
                                                  "jacket"), 1))
            w.writerow(row)
    files["capability"] = os.path.relpath(fn, P.HERE)
    # peak power vs bus voltage across (and a little beyond) the R10
    # window, so WS3/WS5 can read the sag behaviour directly
    fn = os.path.join(DATA, "peak_power_vs_vbus.csv")
    curve = []
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["v_dc_V", "P_peak_1min_kW"])
        v = 400.0
        while v <= 781.0:
            _, pk = mc.peak_power_curve(v, n=37)
            w.writerow([int(v), round(pk / 1e3, 1)])
            curve.append((v, pk / 1e3))
            v += 10.0
    files["peak_power_vs_vbus"] = os.path.relpath(fn, P.HERE)
    RESULTS["maps"] = dict(files=files, stats=stats)
    print(f"  maps done in {time.time()-t0:.1f}s")


# --------------------------------------------------------------------------
def thermal_cases():
    print("== 3. Thermal cases (+45 C ambient, coolant 65 C, 662.4 V) ==")
    V = BUS["v_nom"]
    out = {}

    def _pt(T, rpm):
        return mc.point_full(T, rpm, V, T_wind=150.0)

    # S1 motoring: 180 Nm at the speed giving 45 kW
    rpm_s1 = 45e3 / REQ["S1_Nm"] * 60.0 / (2 * math.pi)
    for build in ("oilspray", "jacket"):
        r = th.steady_analytic(REQ["S1_Nm"], rpm_s1, V, build)
        out[f"S1_180Nm_{build}"] = dict(
            rpm=round(rpm_s1), Tw=round(r[0], 1), Ts=round(r[1], 1),
            Tr=round(r[2], 1), ok=bool(r[0] <= THERM["T_wind_cont"]))
    # S1 generating 50 kW at 70 km/h descent speed
    rpm_70 = rpm_of_kmh(70.0)
    T_gen = -50e3 / (rpm_70 * 2 * math.pi / 60.0)
    r = th.steady_analytic(T_gen, rpm_70, V, "oilspray")
    out["S1gen_50kW_70kmh"] = dict(rpm=round(rpm_70), T_Nm=round(T_gen, 1),
                                   Tw=round(r[0], 1), ok=bool(r[0] <= THERM["T_wind_cont"]))

    # S2-10min: 95 kW at 61 km/h from S1-warm start
    rpm_61 = rpm_of_kmh(61.0)
    T_s2 = 95e3 / (rpm_61 * 2 * math.pi / 60.0)
    s1_state = th.steady_analytic(REQ["S1_Nm"], rpm_s1, V, "oilspray")[:3]
    for vdc in (V, BUS["v_min"]):
        rr = th.run_case(T_s2, rpm_61, vdc, "oilspray", 600.0, dt=0.5,
                         T0=s1_state)
        out[f"S2_95kW_10min_{int(vdc)}V"] = dict(
            rpm=round(rpm_61), T_Nm=round(T_s2, 1),
            Tw_end=round(rr["T_final"][0], 1),
            Tw_max=round(rr["T_max"][0], 1),
            t_limit_s=rr["t_limit_s"],
            ok=bool(rr["t_limit_s"] is None))
    # S2 steady-state (is it actually indefinite?)
    r = th.steady_analytic(T_s2, rpm_61, V, "oilspray")
    out["S2_95kW_steady_Tw"] = round(r[0], 1)
    out["S2_is_S1_at_vnom"] = bool(r[0] <= THERM["T_wind_cont"])

    # WS1 grade-hold operating point for the heat ledger (90.5 kW, 197.7 Nm)
    pt = _pt(197.7, rpm_61)
    out["gradehold_ledger"] = dict(
        rpm=round(rpm_61), T_Nm=197.7,
        P_cu_kW=round(pt["P_cu_W"] / 1e3, 2),
        P_fe_kW=round(pt["P_fe_W"] / 1e3, 2),
        P_fw_kW=round(pt["P_fw_W"] / 1e3, 2),
        P_inv_kW=round(pt["P_inv_W"] / 1e3, 2),
        P_motor_total_kW=round((pt["P_cu_W"] + pt["P_fe_W"] + pt["P_fw_W"]) / 1e3, 2),
        P_chain_kW=round((pt["P_cu_W"] + pt["P_fe_W"] + pt["P_fw_W"]
                          + pt["P_inv_W"]) / 1e3, 2),
        ws1_assumed_inv_motor_kW=7.87)

    # S2 rating point proper (95 kW / 207.4 Nm), same convention (F2):
    # the grade-hold row above is 90.5 kW / 197.7 Nm and is NOT the S2 point
    pt2 = _pt(T_s2, rpm_61)
    out["S2_point_ledger"] = dict(
        rpm=round(rpm_61), T_Nm=round(T_s2, 1),
        P_cu_kW=round(pt2["P_cu_W"] / 1e3, 2),
        P_fe_kW=round(pt2["P_fe_W"] / 1e3, 2),
        P_fw_kW=round(pt2["P_fw_W"] / 1e3, 2),
        P_inv_kW=round(pt2["P_inv_W"] / 1e3, 2),
        P_chain_kW=round((pt2["P_cu_W"] + pt2["P_fe_W"] + pt2["P_fw_W"]
                          + pt2["P_inv_W"]) / 1e3, 2))

    # Peak 1-min: 515 Nm at 20 km/h from S1-warm
    rpm_20 = rpm_of_kmh(20.0)
    t_lim, _ = th.hold_time_from(REQ["peak_Nm"], rpm_20, V, "oilspray",
                                 s1_state, t_cap=1200.0)
    out["peak_515Nm_20kmh_hold_s"] = t_lim if t_lim else ">1200"
    out["peak_515Nm_20kmh_ok_60s"] = bool(t_lim is None or t_lim >= 60.0)
    # 150 kW peak hold at max-power speed
    rpm_pp = 3400.0
    T_pp = 150e3 / (rpm_pp * 2 * math.pi / 60.0)
    t_lim2, _ = th.hold_time_from(T_pp, rpm_pp, V, "oilspray", s1_state,
                                  t_cap=1200.0)
    out["peak_150kW_hold_s"] = t_lim2 if t_lim2 else ">1200"

    # 20% crawl: 510 Nm at V1 and V2 crawl speeds, both builds.
    # F5: "sustainable" for a minutes-long-to-indefinite crawl is judged
    # against the 165 C continuous-life limit; the 180 C hard limit is
    # reported alongside, never as the compliance criterion.
    for tag, v_kmh in (("V1", REQ["crawl_v_kmh"][0]), ("V2", REQ["crawl_v_kmh"][1])):
        rpm_c = rpm_of_kmh(v_kmh)
        for build in ("oilspray", "jacket"):
            r = th.steady_analytic(REQ["crawl_Nm"], rpm_c, V, build)
            key = f"crawl_510Nm_{tag}_{build}"
            out[key] = dict(rpm=round(rpm_c), v_kmh=v_kmh,
                            Tw_steady=round(r[0], 1),
                            within_cont_165C=bool(r[0] <= THERM["T_wind_cont"]),
                            within_hard_180C=bool(r[0] <= THERM["T_wind_max"]))
            if r[0] > THERM["T_wind_max"]:
                tl, _ = th.hold_time_from(REQ["crawl_Nm"], rpm_c, V, build,
                                          s1_state, t_cap=3600.0)
                out[key]["hold_from_S1warm_s"] = tl
                out[key]["distance_m"] = round(tl * v_kmh / 3.6, 0) if tl else None
    # R13: the crawl band TOP (515 Nm at 25 km/h) is also continuous
    # duty. Steady state both builds, plus a floor-voltage identity
    # check: the crawl is MTPA everywhere in the ruled window, so the
    # loss set — and therefore the steady temperature — must not depend
    # on the bus voltage. Verified, not assumed.
    rpm_bt = rpm_of_kmh(REQ["crawl_band_kmh"][1])
    for build in ("oilspray", "jacket"):
        r = th.steady_analytic(REQ["crawl_cont_Nm"], rpm_bt, V, build)
        key = f"crawl_bandtop_515Nm_{build}"
        out[key] = dict(rpm=round(rpm_bt), v_kmh=REQ["crawl_band_kmh"][1],
                        Tw_steady=round(r[0], 1),
                        within_cont_165C=bool(r[0] <= THERM["T_wind_cont"]),
                        within_hard_180C=bool(r[0] <= THERM["T_wind_max"]))
        if r[0] > THERM["T_wind_max"]:
            tl, _ = th.hold_time_from(REQ["crawl_cont_Nm"], rpm_bt, V, build,
                                      s1_state, t_cap=3600.0)
            out[key]["hold_from_S1warm_s"] = tl
            out[key]["distance_m"] = (round(
                tl * REQ["crawl_band_kmh"][1] / 3.6, 0) if tl else None)
    r_fl = th.steady_analytic(REQ["crawl_cont_Nm"], rpm_bt, BUS["v_min"],
                              "oilspray")
    out["crawl_bandtop_Tw_same_at_432V"] = bool(
        abs(r_fl[0] - out["crawl_bandtop_515Nm_oilspray"]["Tw_steady"]) < 0.2)

    # continuous torque at crawl speed, both builds (the derate floor)
    rpm_c1 = rpm_of_kmh(REQ["crawl_v_kmh"][0])
    for build in ("oilspray", "jacket"):
        tcont = th.continuous_torque(rpm_c1, V, build)
        out[f"T_cont_at_crawlspeed_{build}_Nm"] = round(tcont, 0)
        # continuous grade capability at GVW from that torque
        F = tcont * RATIO_NOM * VEH["eta_red"] / VEH["r_dyn"]
        # solve grade: F = Crr m g cos + m g sin  (low speed, no aero)
        m, g = VEH["m_gvw"], VEH["g"]
        lo, hi = 0.0, 0.30
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            t_ = math.atan(mid)
            need = VEH["Crr"] * m * g * math.cos(t_) + m * g * math.sin(t_)
            if need > F:
                hi = mid
            else:
                lo = mid
        out[f"grade_cont_GVW_{build}_pct"] = round(lo * 100, 1)

    # crawl sustainability sensitivity to the oil-spray conductance G_ws
    # (R13: G_ws >= 90 W/K is a WS7 heat-run verification requirement;
    # 75 W/K is the declared continuous-limit floor). Judged at the R13
    # band-top case, the hottest continuous member.
    sens = {}
    g_saved = THERM["G_ws"]["oilspray"]
    for g in (60.0, 75.0, 90.0, 120.0):
        THERM["G_ws"]["oilspray"] = g
        r = th.steady_analytic(REQ["crawl_cont_Nm"], rpm_bt, V, "oilspray")
        sens[f"G_ws_{int(g)}"] = dict(
            Tw_steady=round(r[0], 1),
            within_cont_165C=bool(r[0] <= THERM["T_wind_cont"]),
            within_hard_180C=bool(r[0] <= THERM["T_wind_max"]))
    THERM["G_ws"]["oilspray"] = g_saved
    out["crawl_Gws_sensitivity"] = sens
    # the continuous-limit floor: G_ws at which the hottest continuous
    # case sits exactly on the 165 C line. r3 declared 75 W/K — but that
    # was the V1-speed 510 Nm member; R13's band-top case is hotter
    # (more iron at 119.5 Hz), so the floor is RE-DERIVED, not inherited.
    lo_g, hi_g = 40.0, 200.0
    for _ in range(40):
        mid = 0.5 * (lo_g + hi_g)
        THERM["G_ws"]["oilspray"] = mid
        r = th.steady_analytic(REQ["crawl_cont_Nm"], rpm_bt, V, "oilspray")
        if r[0] > THERM["T_wind_cont"]:
            lo_g = mid
        else:
            hi_g = mid
    THERM["G_ws"]["oilspray"] = g_saved
    out["G_ws_cont_limit_floor_WK"] = round(hi_g, 1)

    # standstill: 148 Nm hold (E16) and 515 Nm stall
    for build in ("oilspray", "jacket"):
        r = th.steady_analytic(REQ["hold_6pct_Nm"], 0.0, V, build,
                               standstill=True)
        out[f"hold_148Nm_standstill_{build}"] = dict(
            Tw_steady=round(r[0], 1),
            sustainable=bool(r[0] <= THERM["T_wind_cont"]))
    tl, _ = th.hold_time_from(REQ["peak_Nm"], 0.0, V, "oilspray", s1_state,
                              standstill=True, t_cap=600.0)
    out["stall_515Nm_hold_s"] = tl if tl else ">600"

    # inverter junction at peak current (simple check)
    p_inv_pk = mc.inverter_loss(MACH["I_peak"], V)
    out["inverter_loss_peak_W"] = round(p_inv_pk, 0)
    out["inverter_Tj_peak_C"] = round(
        THERM["T_cool_in"] + (p_inv_pk / 6.0) * INV["Rth_jc_module"], 0)
    # inverter junction at the R13 CONTINUOUS rating current (the crawl
    # basis) — F11's rating-statement leg: the continuous rating is
    # thermally substantiated, not asserted. Enumerated over the window
    # voltages (R14): switching loss rises with bus voltage, so the
    # ceiling governs.
    i_cont = RESULTS["machine"]["I_cont_Apk"]
    tj_cases = {}
    for v in (BUS["v_min"], BUS["v_nom"], BUS["v_max"]):
        p = mc.inverter_loss(i_cont, v)
        tj_cases[f"{round(v)}V"] = round(
            THERM["T_cool_in"] + (p / 6.0) * INV["Rth_jc_module"], 0)
    out["inverter_Tj_cont_cases_C"] = tj_cases
    p_inv_cont = mc.inverter_loss(i_cont, BUS["v_max"])
    out["inverter_loss_cont_at_vmax_W"] = round(p_inv_cont, 0)
    out["inverter_Tj_cont_at_vmax_C"] = round(
        THERM["T_cool_in"] + (p_inv_cont / 6.0) * INV["Rth_jc_module"], 0)

    for k, v in out.items():
        print(f"  {k}: {v}")
    RESULTS["thermal"] = out

    # thermal trace exports
    fn = os.path.join(DATA, "thermal_S2_10min_662V.csv")
    rr = th.run_case(T_s2, rpm_61, V, "oilspray", 600.0, dt=0.5, T0=s1_state)
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "T_winding_C", "T_stator_C", "T_rotor_C"])
        w.writerows(rr["trace"])
    fn2 = os.path.join(DATA, "thermal_crawl_510Nm_jacket.csv")
    rr2 = th.run_case(REQ["crawl_Nm"], rpm_of_kmh(REQ["crawl_v_kmh"][0]), V,
                      "jacket", 1800.0, dt=0.5, T0=s1_state)
    with open(fn2, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "T_winding_C", "T_stator_C", "T_rotor_C"])
        w.writerows(rr2["trace"])
    RESULTS["maps"]["files"]["thermal_S2"] = os.path.relpath(fn, P.HERE)
    RESULTS["maps"]["files"]["thermal_crawl"] = os.path.relpath(fn2, P.HERE)


# --------------------------------------------------------------------------
@contextlib.contextmanager
def scaled_machine(ratio):
    """Scale the reference design (stack-length rule) to another ratio."""
    s = RATIO_NOM / ratio
    keys = ("psi_m", "Ld", "Lq", "Rs_20C", "k_h", "k_e", "psi_ref", "fw_b")
    saved_m = {k: MACH[k] for k in keys}
    saved_fa = MACH["f_ac_ref"]
    saved_t = (dict(THERM["G_ws"]), THERM["G_sc"], THERM["C_w"], THERM["C_s"])
    try:
        for k in keys:
            MACH[k] = saved_m[k] * s
        MACH["f_ac_ref"] = saved_fa * ratio / RATIO_NOM  # own top frequency
        gscale = 0.25 + 0.75 * s
        THERM["G_ws"] = {k: v * gscale for k, v in saved_t[0].items()}
        THERM["G_sc"] = saved_t[1] * gscale
        THERM["C_w"] = saved_t[2] * s
        THERM["C_s"] = saved_t[3] * s
        yield s
    finally:
        for k in keys:
            MACH[k] = saved_m[k]
        MACH["f_ac_ref"] = saved_fa
        THERM["G_ws"], THERM["G_sc"], THERM["C_w"], THERM["C_s"] = \
            saved_t[0], saved_t[1], saved_t[2], saved_t[3]


def ratio_sweep():
    print("== 4. Reduction-ratio sweep 8:1..12:1 (1 Hz decimated cycles) ==")
    rows = []
    for r in RATIO_SWEEP:
        with scaled_machine(r) as s:
            mass = MACH["mass_end_kg"] + (MACH["mass_kg"] - MACH["mass_end_kg"]) * s
            t_req = VEH["F_trac_max"] * VEH["r_dyn"] / (r * VEH["eta_red"])
            t_avail = mc.mtpa_torque(MACH["I_peak"])
            rpm_100 = rpm_of_kmh(100.0, r)
            sub = cycles.cycle_losses(P.WS1_TRACE_SUB, "V1", BUS["v_nom"], r,
                                      decimate=10, lockup=False)
            reg = cycles.cycle_losses(P.WS1_TRACE_REG, "V2", BUS["v_nom"], r,
                                      decimate=10, lockup=True)
            rpm_c = rpm_of_kmh(REQ["crawl_v_kmh"][0], r)
            cr = th.steady_analytic(t_req * 510.0 / 515.0, rpm_c, BUS["v_nom"],
                                    "oilspray")
            sp = mc.spin_loss(rpm_of_kmh(85.0, r) * 2 * math.pi / 60.0,
                              BUS["v_nom"])
            rows.append(dict(
                ratio=r, scale=round(s, 3), mass_kg=round(mass, 1),
                T_req_Nm=round(t_req, 0), T_avail_Nm=round(t_avail, 0),
                rpm_at_100kmh=round(rpm_100, 0),
                within_R3_7200rpm=bool(rpm_100 <= REQ["rpm_max"]),
                sub_loss_kWh=round(sub["E_loss_mach_kWh"]
                                   + sub["E_loss_inv_kWh"], 3),
                sub_eta_mot=round(sub["eta_mot_avg"], 4),
                reg_loss_kWh=round(reg["E_loss_mach_kWh"]
                                   + reg["E_loss_inv_kWh"]
                                   + reg["E_spin_shaft_kWh"]
                                   + reg["E_spin_bus_kWh"], 3),
                reg_eta_mot=round(reg["eta_mot_avg"], 4),
                spin85_shaft_W=round(sp["shaft_drag_W"], 0),
                crawl_Tw_steady=round(cr[0], 1) if cr else None,
            ))
            print("  " + str(rows[-1]))
    fn = os.path.join(DATA, "ratio_sweep.csv")
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # decision metric: total cycle loss (SUB + REG) + mass penalty
    best = min(rows, key=lambda x: x["sub_loss_kWh"] + x["reg_loss_kWh"])
    RESULTS["ratio_sweep"] = dict(
        rows=rows, file=os.path.relpath(fn, P.HERE),
        min_total_cycle_loss_ratio=best["ratio"],
        decision="retain 10:1 unless sweep shows >5% total-loss advantage")
    losses = {x["ratio"]: x["sub_loss_kWh"] + x["reg_loss_kWh"] for x in rows}
    l10 = losses[10.0]
    spread = (max(losses.values()) - min(losses.values())) / l10 * 100
    RESULTS["ratio_sweep"]["loss_spread_pct_of_10to1"] = round(spread, 1)
    # F3: state the within-rpm-line comparison honestly — 9:1 also edges
    # 10:1 on total cycle loss (noise-level), and say by how much.
    totals = {str(int(x["ratio"])): round(x["sub_loss_kWh"] + x["reg_loss_kWh"], 3)
              for x in rows}
    RESULTS["ratio_sweep"]["total_loss_kWh_by_ratio"] = totals
    RESULTS["ratio_sweep"]["inside_rpm_line_beating_10to1"] = [
        x["ratio"] for x in rows
        if x["within_R3_7200rpm"] and x["ratio"] != 10.0
        and totals[str(int(x["ratio"]))] < totals["10"]]
    RESULTS["ratio_sweep"]["delta_9_vs_10_pct"] = round(
        (totals["10"] - totals["9"]) / totals["10"] * 100, 2)
    m9 = next(x["mass_kg"] for x in rows if x["ratio"] == 9.0)
    m10 = next(x["mass_kg"] for x in rows if x["ratio"] == 10.0)
    RESULTS["ratio_sweep"]["mass_delta_9_vs_10_kg"] = round(m9 - m10, 1)
    # F9: the above-the-line clauses, computed instead of transcribed —
    # per-ratio-point mass savings and the 11:1 / 12:1 loss deltas vs 10:1.
    m11 = next(x["mass_kg"] for x in rows if x["ratio"] == 11.0)
    m12 = next(x["mass_kg"] for x in rows if x["ratio"] == 12.0)
    RESULTS["ratio_sweep"]["delta_11_vs_10_pct"] = round(
        (totals["10"] - totals["11"]) / totals["10"] * 100, 2)
    RESULTS["ratio_sweep"]["delta_12_vs_10_pct"] = round(
        (totals["10"] - totals["12"]) / totals["10"] * 100, 2)
    RESULTS["ratio_sweep"]["mass_per_point_kg"] = {
        "10_to_11": round(m10 - m11, 1),
        "11_to_12": round(m11 - m12, 1)}
    print(f"  loss spread across sweep: {spread:.1f}% of the 10:1 value; "
          f"9:1 edges 10:1 by {RESULTS['ratio_sweep']['delta_9_vs_10_pct']}% "
          f"at +{RESULTS['ratio_sweep']['mass_delta_9_vs_10_kg']} kg")
    print(f"  beyond the rpm line: 11:1 {RESULTS['ratio_sweep']['delta_11_vs_10_pct']}%"
          f" / 12:1 {RESULTS['ratio_sweep']['delta_12_vs_10_pct']}% below 10:1; "
          f"mass/point {RESULTS['ratio_sweep']['mass_per_point_kg']}")


# --------------------------------------------------------------------------
def bus_and_resistor():
    print("== 5. DC bus (R10 ruled window) + brake resistor ==")
    m = RESULTS["machine"]
    # S2 phase currents across the window (10-min cases for the R14
    # enumeration; the R13 crawl current is the continuous basis)
    s2_nom = mc.point_full(207.4, rpm_of_kmh(61.0), BUS["v_nom"],
                           T_wind=150.0)
    s2_floor = mc.point_full(207.4, rpm_of_kmh(61.0), BUS["v_min"],
                             T_wind=150.0)
    s2_nom_arms = s2_nom["I_amp"] / math.sqrt(2.0)
    s2_floor_arms = s2_floor["I_amp"] / math.sqrt(2.0)
    i_crawl_cont = m["I_cont_Arms"]
    i_crawl_ws1 = max(m["I_cont_cases"]["crawl_510Nm_V1_10p6kmh"]["I_Arms"],
                      m["I_cont_cases"]["crawl_510Nm_V2_23p6kmh"]["I_Arms"])
    i_peak_arms = MACH["I_peak"] / math.sqrt(2.0)
    RESULTS["bus"] = dict(
        ruling=dict(
            basis="R10 (BASELINE v2) — pack-native window, ruled, not "
                  "a WS2 proposal; the r1-r3 400V-vs-800V trade is "
                  "superseded on the record",
            nominal_V=BUS["v_nom"], window_V=[BUS["v_min"], BUS["v_max"]],
            transient_10s_V=BUS["v_transient"],
            device_class_V=BUS["v_dev_class"],
            granularity_V=BUS["v_granularity"]),
        string=bus.string_check(),
        cables=bus.cable_table(
            i_crawl_cont_arms=i_crawl_cont,
            i_crawl_ws1_arms=i_crawl_ws1,
            i_s2_floor_arms=s2_floor_arms,
            i_s2_nom_arms=s2_nom_arms,
            i_peak_arms=i_peak_arms),
        s2_phase_current_Arms=round(s2_nom_arms, 1),
        s2_phase_current_floor_Arms=round(s2_floor_arms, 1),
        I_dc_genset_at_floor_A=round(125e3 / BUS["v_min"], 1),
        I_dc_genset_at_vnom_A=round(125e3 / BUS["v_nom"], 1),
        I_dc_pack_125kW_at_floor_A=round(125e3 / BUS["v_min"], 1),
    )
    assert RESULTS["bus"]["string"]["matches_R10_window"], \
        "288s string arithmetic does not reproduce the R10 window"
    print(f"  string: {RESULTS['bus']['string']}")
    ct = RESULTS["bus"]["cables"]
    for run, d in ct["detail"].items():
        print(f"  cable {run}: {d['i_size_A']} A ({d['governing_case']}) "
              f"-> {d['mm2']} mm2 ({d['ampacity_A']} A), {d['mass_kg']} kg")
    print(f"  cable mass total: {ct['cable_mass_kg']} kg")
    res = resistor.design()
    # F12 closure (R14): the cable-limited continuous ceiling of the
    # chopper->resistor run, restated against the element ceiling
    mm2 = ct["detail"]["chopper_to_resistor"]["mm2"]
    amp = ct["detail"]["chopper_to_resistor"]["ampacity_A"]
    res["cable_limited_ceiling_kW"] = round(amp ** 2 * RES["R_ohm"] / 1e3, 1)
    res["cable_limited_ceiling_note"] = (
        f"{mm2} mm2 run at {amp} A ampacity; sits ABOVE every element "
        "operating point, so the bank is element-limited (voltage-"
        "limited), never cable-limited — F12 closed by construction")
    RESULTS["resistor"] = res
    for k, v in res.items():
        print(f"  resistor.{k}: {v if not isinstance(v, float) else round(v, 2)}")


# --------------------------------------------------------------------------
def traction_envelope():
    print("== 6. Traction-control envelope (E23) ==")
    rows = traction.envelope()
    fn = os.path.join(DATA, "traction_envelope.csv")
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    mu = traction.mu_required()
    curves = {}
    for mass_case in ("gvw", "curb"):
        for mu_ in (0.8, 0.5, 0.3):
            curves[f"{mass_case}_mu{mu_}"] = traction.regen_power_curve(
                mass_case, mu_)
    fn2 = os.path.join(DATA, "regen_adhesion_curves.csv")
    with open(fn2, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "v_kmh", "P_adhesion_kW", "P_usable_kW", "binding"])
        for case, rs in curves.items():
            for r in rs:
                w.writerow([case, r["v_kmh"], round(r["P_adhesion_kW"], 1),
                            round(r["P_usable_kW"], 1), r["binding"]])
    RESULTS["traction"] = dict(
        envelope=rows, mu_required=mu,
        files=[os.path.relpath(fn, P.HERE), os.path.relpath(fn2, P.HERE)])
    for r in rows:
        print(f"  {r['mass_case']} mu={r['mu']}: F_drive {r['F_drive_flat_N']:.0f} N "
              f"(launch ok {r['launch_spec_ok_flat']}), "
              f"F_brake {r['F_brake_N']:.0f} N -> T_motor "
              f"{r['T_motor_brake_Nm']:.0f} Nm")
    print("  mu_required:", {k: round(v, 3) for k, v in mu.items()})


# --------------------------------------------------------------------------
def cycle_runs():
    print("== 7. Cycle losses through the maps (10 Hz, reference traces) ==")
    sub = cycles.cycle_losses(P.WS1_TRACE_SUB, "V1", BUS["v_nom"], RATIO_NOM,
                              decimate=1, lockup=False)
    reg = cycles.cycle_losses(P.WS1_TRACE_REG, "V2", BUS["v_nom"], RATIO_NOM,
                              decimate=1, lockup=True)
    # R12 (closes WS2-E7): the traction chain of record is THESE MAPS
    # x 0.97 reduction; WS1's 0.97 "PE" stage is the genset-side
    # rectifier/conditioning and lives in WS4's ledger. The r2-r3
    # convention-bridging scaffolding (ws1_scalar_*, pe_convention) is
    # REMOVED from the exports — no scalar PE member exists on the
    # traction side, and all exported energies are BUS-SIDE.
    RESULTS["cycles"] = dict(
        VOLT_SUB_V1=sub, VOLT_REG_V2_iMMD_approx=reg,
        chain_of_record=("R12: bus->wheel = these measured inverter+motor "
                         "maps x 0.97 reduction (declared derate). No "
                         "scalar PE member on the traction side. All "
                         "energies bus-side. WS1's scalar shaft-bus and "
                         "bus-wheel chains are superseded on the record."),
        note=("V2 approximation: lockup engaged whenever v>=65 km/h and "
              "P_wheel>0; regen taken by the motor everywhere (WS1's "
              "regen-priority clutch strategy). Reference traces only — "
              "means, not extrema (stable to a few % per WS1 s.4.8)."))
    fn = os.path.join(DATA, "cycle_loss_summary.csv")
    keys = [k for k in sub.keys() if k not in ("variant",)]
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "VOLT-SUB_V1", "VOLT-REG_V2_iMMD_approx"])
        for k in keys:
            w.writerow([k,
                        round(sub[k], 4) if isinstance(sub[k], float) else sub[k],
                        round(reg[k], 4) if isinstance(reg[k], float) else reg[k]])
    RESULTS["cycles"]["file"] = os.path.relpath(fn, P.HERE)
    for tag, c in (("VOLT-SUB V1", sub), ("VOLT-REG V2", reg)):
        print(f"  {tag}: eta_mot_avg {c['eta_mot_avg']:.3f}, "
              f"eta_gen_avg {c['eta_gen_avg']:.3f}, "
              f"mean heat {c['mean_heat_kW']:.2f} kW, "
              f"lockup spin {c['E_spin_shaft_kWh']:.2f} kWh, "
              f"roll spin {c['E_rollspin_shaft_kWh']:.2f} kWh, "
              f"infeasible steps {c['n_infeasible']}")


# --------------------------------------------------------------------------
def heat_ledger():
    print("== 8. Heat ledger (R9, to WS6) ==")
    t = RESULTS["thermal"]
    c = RESULTS["cycles"]
    res = RESULTS["resistor"]
    gl = t["gradehold_ledger"]
    rows = [
        dict(component="traction motor",
             case="V2 6% grade hold, 90.5 kW shaft, 10 min, +45C "
                  "(restated at the R10 voltage per R12)",
             kW=gl["P_motor_total_kW"], sink="LT coolant loop"),
        dict(component="traction inverter", case="V2 6% grade hold",
             kW=gl["P_inv_kW"], sink="LT coolant loop"),
        dict(component="reduction (motor path)", case="V2 6% grade hold",
             kW=round(90.5 * 0.03, 2), sink="gear oil / case convection"),
        dict(component="motor+inverter", case="S2 rating point 95 kW / 207.4 Nm",
             kW=t["S2_point_ledger"]["P_chain_kW"], sink="LT coolant loop"),
        dict(component="brake resistor", case="6% descent, R2 continuous",
             kW=50.0, sink="ambient air (forced), NOT coolant (R15)"),
        dict(component="brake resistor", case="24-min 25 km/h descent (WS1 4.6)",
             kW=22.0, sink="ambient air; 8.82 kWh total"),
        dict(component="brake resistor",
             case="WS2-E5 second-stage ceiling: full duty at the 748.8 V "
                  "operating ceiling (continuous-capable)",
             kW=round(res["P_design_cont_kW"], 1),
             sink="ambient air (forced), NOT coolant (R15)"),
        dict(component="chopper", case="R2 50 kW continuous",
             kW=round(res["chopper_loss_50kW_W"] / 1e3, 2), sink="LT coolant loop"),
        dict(component="motor+inverter",
             case="20% crawl 510 Nm (V1 speed 10.6 km/h), R13 continuous",
             kW=round(t["crawl_loss_V1speed_kW"], 2),
             sink="LT coolant loop"),
        dict(component="motor+inverter",
             case="20% crawl 510 Nm (V2 speed 23.6 km/h), R13 continuous",
             kW=round(t["crawl_loss_V2speed_kW"], 2),
             sink="LT coolant loop"),
        dict(component="motor+inverter",
             case="R13 crawl band top 515 Nm at 25 km/h — LOOP-SIZING CASE",
             kW=round(t["crawl_loss_bandtop_kW"], 2),
             sink="LT coolant loop"),
        dict(component="motor+inverter", case="VOLT-SUB V1 cycle average",
             kW=round(c["VOLT_SUB_V1"]["mean_heat_kW"], 2),
             sink="LT coolant loop"),
        dict(component="motor+inverter (incl lockup spin)",
             case="VOLT-REG V2 cycle average",
             kW=round(c["VOLT_REG_V2_iMMD_approx"]["mean_heat_kW"], 2),
             sink="LT coolant loop"),
        dict(component="blower (resistor)", case="whenever chopper active",
             kW=round(res["blower_W"] / 1e3, 2), sink="electrical load on bus"),
        dict(component="pack heater (WS3-OWNED, coexisting member per R15)",
             case="R15 blend order: regen -> pack heater (if cold) -> "
                  "resistor -> friction; heater feeds from the DC bus",
             kW=8.0, sink="pack coolant loop; electrical load on bus "
                          "(WS3 owns the heater, WS2 owns the resistor)"),
    ]
    fn = os.path.join(DATA, "heat_ledger_ws2.csv")
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["component", "case", "kW", "sink"])
        w.writeheader()
        w.writerows(rows)
    RESULTS["heat_ledger"] = dict(rows=rows, file=os.path.relpath(fn, P.HERE))
    for r in rows:
        print(f"  {r['component']} | {r['case']} | {r['kW']} kW | {r['sink']}")


# --------------------------------------------------------------------------
def interface_and_headline():
    print("== 9. Interface block (R14 discipline) ==")
    t = RESULTS["thermal"]
    m = RESULTS["machine"]
    res = RESULTS["resistor"]
    cyc = RESULTS["cycles"]
    topo = RESULTS["topology"]
    mass = dict(
        motor_kg=MACH["mass_kg"], inverter_kg=INV["mass_kg"],
        reduction_motor_stage_kg=32.0,
        resistor_assembly_kg=round(res["assembly_mass_kg"], 1),
        chopper_kg=6.0,
        hv_cables_kg=RESULTS["bus"]["cables"]["cable_mass_kg"],
        contactors_precharge_kg=9.0,
    )
    mass["total_kg"] = round(sum(mass.values()), 1)
    volume = dict(motor_L=21.0, inverter_L=11.0,
                  resistor_L=round(res["assembly_volume_L"], 0),
                  reduction_stage_L=18.0)
    vmin_k = str(round(BUS["v_min"]))
    vnom_k = str(round(BUS["v_nom"]))
    vmax_k = str(round(BUS["v_max"]))

    # R14 helper shapes: every worst-case field is an explicit max/min
    # over an enumerated case set with the governing case labeled inline.
    coolant_cases = {
        "crawl_510Nm_V1_10.6kmh (R13 continuous)": t["crawl_loss_V1speed_kW"],
        "crawl_510Nm_V2_23.6kmh (R13 continuous)": t["crawl_loss_V2speed_kW"],
        "crawl_band_top_515Nm_25.0kmh (R13 continuous)":
            t["crawl_loss_bandtop_kW"],
        "S2_rating_95kW_207.4Nm (10-min)": t["S2_point_ledger"]["P_chain_kW"],
        "grade_hold_90.5kW_197.7Nm (10-min)":
            t["gradehold_ledger"]["P_chain_kW"],
    }
    heat_gov = max(coolant_cases, key=coolant_cases.get)

    inv_cont_cases_arms = {
        "R13_crawl_band_top_515Nm_25kmh": m["I_cont_cases"][
            "R13_band_top_515Nm_25kmh"]["I_Arms"],
        "crawl_510Nm_V1_10.6kmh": m["I_cont_cases"][
            "crawl_510Nm_V1_10p6kmh"]["I_Arms"],
        "crawl_510Nm_V2_23.6kmh": m["I_cont_cases"][
            "crawl_510Nm_V2_23p6kmh"]["I_Arms"],
    }
    inv_10min_cases_arms = {
        "S2_95kW_at_432.0V_floor": RESULTS["bus"][
            "s2_phase_current_floor_Arms"],
        "S2_95kW_at_662.4V_nominal": RESULTS["bus"]["s2_phase_current_Arms"],
    }
    cont_gov = max(inv_cont_cases_arms, key=inv_cont_cases_arms.get)
    tenmin_gov = max(inv_10min_cases_arms, key=inv_10min_cases_arms.get)

    res_ceiling_cases = {
        "element, full duty at 748.8 V operating ceiling (V^2/R)":
            round(res["P_fullduty_at_vmax_kW"], 1),
        "cable-limited (70 mm2 chopper run at 225 A)":
            res["cable_limited_ceiling_kW"],
        "ribbon-limited at the 2,000 m / +45 C corner":
            round(res["P_ribbon_limit_2000m_kW"], 1),
    }
    res_gov = min(res_ceiling_cases, key=res_ceiling_cases.get)

    iface = dict(
        dc_bus=dict(basis="R10 (BASELINE v2), pack-native 288s LTO string "
                          "— ruled, consumed here, no longer a proposal",
                    nominal_V=BUS["v_nom"],
                    window_V=[BUS["v_min"], BUS["v_max"]],
                    transient_10s_V=BUS["v_transient"],
                    granularity_V=BUS["v_granularity"],
                    chopper_hw_overvoltage_backstop_V=RES["v_hw_backstop"],
                    device_class_V=BUS["v_dev_class"]),
        machine=dict(type="IPM-PMSM, 8-pole, hairpin, WEG jacket + oil "
                          "spray (spray build MANDATORY per R13)",
                     name=MACH["name"],
                     rewind_factor_vs_r3=P.REWIND,
                     ratio=RATIO_NOM,
                     ratio_arrangement="3.571:1 motor stage into common "
                                       "2.8:1 final drive",
                     S1_Nm=REQ["S1_Nm"], S1_kW=REQ["S1_kW"],
                     S2_10min_kW=REQ["S2_10min_kW"],
                     T_peak_Nm=round(m["T_peak_at_Ipeak_Nm"], 0),
                     rpm_max=7200,
                     peak_1min_kW=dict(
                         rule="capability vs bus voltage; monotone rising, "
                              "so the window FLOOR is the worst case "
                              "(R14); full curve in "
                              "data/peak_power_vs_vbus.csv",
                         cases={vmin_k: round(m["P_peak_kW_vs_V"][vmin_k], 1),
                                vnom_k: round(m["P_peak_kW_vs_V"][vnom_k], 1),
                                vmax_k: round(m["P_peak_kW_vs_V"][vmax_k], 1)},
                         worst_case_value=round(m["P_peak_kW_vs_V"][vmin_k], 1),
                         governing_case=vmin_k + " V window floor",
                         R3_120kW_met_everywhere_in_window=bool(
                             m["P_peak_at_floor_ok_120kW"])),
                     T_515Nm_available_everywhere_in_window=bool(
                         m["R13_corner_515Nm_25kmh_vmin_ok"]),
                     asc_required=dict(
                         rule="UCG onset (EMF = bus V) vs bus voltage; "
                              "the window FLOOR is the worst case (R14)",
                         cases_kmh={
                             vmin_k: round(m[f"ucg_onset_kmh_at_{vmin_k}V"], 1),
                             vnom_k: round(m[f"ucg_onset_kmh_at_{vnom_k}V"], 1),
                             vmax_k: round(m[f"ucg_onset_kmh_at_{vmax_k}V"], 1)},
                         worst_case_value_kmh=round(
                             m[f"ucg_onset_kmh_at_{vmin_k}V"], 1),
                         governing_case=vmin_k + " V window floor",
                         no_ucg_below_7200rpm_above_V=round(
                             m["v_bus_no_ucg_below_7200rpm_V"], 0))),
        electrical_ratings=dict(
            note="R13/F11: the continuous rating basis IS the crawl phase "
                 "current; R14: each tier is an explicit max over its "
                 "enumerated case set. Crawl currents are MTPA and "
                 "voltage-independent across the window (verified).",
            continuous_Arms=dict(
                rule="max", cases=inv_cont_cases_arms,
                value=inv_cont_cases_arms[cont_gov],
                governing_case=cont_gov),
            ten_min_Arms=dict(
                rule="max", cases=inv_10min_cases_arms,
                value=inv_10min_cases_arms[tenmin_gov],
                governing_case=tenmin_gov,
                note="sits BELOW the continuous rating — subsumed"),
            peak_60s_Apk=round(MACH["I_peak"], 1),
            peak_60s_Arms=round(MACH["I_peak"] / math.sqrt(2.0), 1),
            inverter_Tj_at_continuous_rating_C=dict(
                rule="max over window voltages (switching loss rises "
                     "with bus voltage; R14)",
                cases=t["inverter_Tj_cont_cases_C"],
                value=t["inverter_Tj_cont_at_vmax_C"],
                governing_case=f"{round(BUS['v_max'])}V window ceiling"),
            inverter_Tj_at_peak_C=t["inverter_Tj_peak_C"]),
        mass_kg=mass, volume_L=volume,
        coolant=dict(loop="LT", fluid="WEG 50/50",
                     flow_lpm=THERM["coolant_flow_lpm"],
                     max_inlet_C=THERM["T_cool_in"],
                     order="inverter then motor",
                     heat_worst_case_kW=dict(
                         rule="max", cases=coolant_cases,
                         value=t["crawl_loss_kW"],
                         governing_case=heat_gov,
                         convention="motor+inverter chain loss at the "
                                    "170 C winding bookkeeping convention, "
                                    "662.4 V; size the LT loop to this"),
                     heat_at_S2_rating_kW=t["S2_point_ledger"]["P_chain_kW"],
                     heat_at_gradehold_90p5kW_kW=t["gradehold_ledger"]["P_chain_kW"]),
        ws7_verification=dict(
            G_ws_heat_run_requirement_WK=90.0,
            basis="R13: oil-spray winding->sink conductance G_ws >= 90 W/K "
                  "must be verified by WS7 heat run",
            continuous_limit_floor_WK=t["G_ws_cont_limit_floor_WK"],
            floor_note="G_ws at which the hottest continuous case (R13 "
                       "band top) sits exactly on the 165 C line — "
                       "re-derived this round; r3's 75 W/K was the "
                       "510 Nm V1-speed member"),
        resistor=dict(R_ohm=round(RES["R_ohm"], 4),
                      P_cont_kW_any_bus_V=dict(
                          rule="min over window voltages of full-duty "
                               "V^2/R = the power available at ANY bus "
                               "voltage; R2 requires >= 50 (R14)",
                          cases={
                              "432V window floor":
                                  round(res["P_fullduty_at_vmin_kW"], 1),
                              "662V nominal":
                                  round(res["P_fullduty_at_vnom_kW"], 1),
                              "749V window ceiling":
                                  round(res["P_fullduty_at_vmax_kW"], 1)},
                          value=round(res["P_fullduty_at_vmin_kW"], 1),
                          governing_case="432V window floor"),
                      second_stage_ceiling_kW=dict(
                          rule="min over the limiting mechanisms (R14); "
                               "continuous-capable, not time-boxed",
                          cases=res_ceiling_cases,
                          value=res_ceiling_cases[res_gov],
                          governing_case=res_gov),
                      P_fullduty_at_vtransient_kW=round(
                          res["P_fullduty_at_vtransient_kW"], 1),
                      control=("bus-voltage droop, WS5 setpoint 700-760 V "
                               "(default 745), plus direct 0-100% power "
                               "command at 100 Hz"),
                      sink="forced air, not coolant (R15: retardation "
                           "shall not share a failure domain with the "
                           "pack loop)"),
        spin_drag=dict(
            note="PM lockup spin drag at the R10 winding (R4 directive "
                 "item 7); G1-R charges this to case (a) — it is a "
                 "lockup-only tax the series path does not pay",
            shaft_drag_85kmh_W=topo["PM_spin_shaft_drag_85kmh_W"],
            bus_draw_85kmh_W=topo["PM_spin_bus_draw_85kmh_W"],
            total_100kmh_W=topo["PM_spin_total_100kmh_W"],
            E_engine_side_VOLTREG_kWh=round(
                cyc["VOLT_REG_V2_iMMD_approx"]["E_spin_shaft_kWh"], 2),
            E_bus_side_VOLTREG_kWh=round(
                cyc["VOLT_REG_V2_iMMD_approx"]["E_spin_bus_kWh"], 2)),
        dc_bus_loads_coexisting=dict(
            note="R15: coexisting DC-bus loads for WS5/WS6 bookkeeping",
            resistor_blower_kW=round(res["blower_W"] / 1e3, 2),
            pack_heater_kW=8.0,
            pack_heater_owner="WS3 (WS2 owns the resistor)"),
        efficiency_maps=RESULTS["maps"]["files"],
        traction_control=dict(
            required_day_one=True,
            torque_limit_law="T_wheel <= mu_est*N_r_est*r_dyn/(1 -+ mu_est*h/L)",
            envelope_file="data/traction_envelope.csv"),
    )
    RESULTS["interface"] = iface

    # headline strings — the report quotes these verbatim
    hl = dict(
        bus_window="432.0-748.8 V",
        bus_nominal="662.4 V",
        bus_transient="777.6 V",
        device_class="1200 V",
        peak_power_vnom_kW=f"{m['P_peak_kW_vs_V'][vnom_k]:.0f} kW",
        peak_power_vmin_kW=f"{m['P_peak_kW_vs_V'][vmin_k]:.0f} kW",
        peak_power_vmax_kW=f"{m['P_peak_kW_vs_V'][vmax_k]:.0f} kW",
        peak_torque=f"{m['T_peak_at_Ipeak_Nm']:.0f} Nm",
        i_cont_arms=f"{m['I_cont_Arms']:.0f} Arms",
        i_cont_ratio_vs_r3=f"{m['I_cont_vs_455Arms_r3_ratio']:.3f}",
        s2_Tw_end=f"{t[f'S2_95kW_10min_{int(BUS['v_nom'])}V']['Tw_end']:.0f} C",
        s2_steady_Tw=f"{t['S2_95kW_steady_Tw']:.0f} C",
        crawl_oilspray_Tw=f"{t['crawl_510Nm_V1_oilspray']['Tw_steady']:.0f} C",
        crawl_bandtop_Tw=f"{t['crawl_bandtop_515Nm_oilspray']['Tw_steady']:.0f} C",
        crawl_jacket_hold=(f"{t['crawl_510Nm_V1_jacket'].get('hold_from_S1warm_s', 0):.0f} s"
                           if not t["crawl_510Nm_V1_jacket"]["within_hard_180C"]
                           else "steady"),
        stall_515_hold=f"{t['stall_515Nm_hold_s']:.0f} s"
        if isinstance(t["stall_515Nm_hold_s"], float) else str(t["stall_515Nm_hold_s"]),
        resistor_R=f"{RES['R_ohm']:.2f} ohm",
        resistor_mass=f"{res['assembly_mass_kg']:.0f} kg",
        resistor_fullduty_vmax=f"{res['P_fullduty_at_vmax_kW']:.0f} kW",
        spin_energy_lockup_reg=f"{RESULTS['cycles']['VOLT_REG_V2_iMMD_approx']['E_spin_shaft_kWh']:.2f} kWh",
        spin_drag_85_W=f"{RESULTS['topology']['PM_spin_shaft_drag_85kmh_W']:,.0f} W",
        total_mass=f"{mass['total_kg']:.0f} kg",
        eta_sub=f"{RESULTS['cycles']['VOLT_SUB_V1']['eta_mot_avg']:.3f}",
        eta_reg=f"{RESULTS['cycles']['VOLT_REG_V2_iMMD_approx']['eta_mot_avg']:.3f}",
    )
    RESULTS["headline"] = hl
    for k, v in hl.items():
        print(f"  headline.{k} = {v}")


# --------------------------------------------------------------------------
def main():
    t0 = time.time()
    spec_checks()
    topology_trade()
    export_maps()
    thermal_cases()
    # crawl chain loss for the ledger, under the identical 170 C
    # bookkeeping convention. R13 makes the WHOLE 10-25 km/h band
    # continuous duty at 515 Nm, so the enumerated case set (R14) is the
    # two WS1 settle-speed members (510 Nm — the F8 pair, retained) PLUS
    # the band-top member (515 Nm at 25 km/h), and the exported worst
    # case is the max over all three with the governing case named.
    # The WS2-E1 conditioning of rounds 2-3 is REMOVED: R13 has landed,
    # and these fields are re-derived at the R10 voltage, not relabeled.
    crawl_loss = {}
    crawl_members = {}
    for tag, T_c, v_kmh in (
            ("V1", REQ["crawl_Nm"], REQ["crawl_v_kmh"][0]),
            ("V2", REQ["crawl_Nm"], REQ["crawl_v_kmh"][1]),
            ("bandtop", REQ["crawl_cont_Nm"], REQ["crawl_band_kmh"][1])):
        pt = mc.point_full(T_c, rpm_of_kmh(v_kmh),
                           BUS["v_nom"], T_wind=170.0)
        crawl_loss[tag] = round(
            (pt["P_cu_W"] + pt["P_fe_W"] + pt["P_fw_W"] + pt["P_inv_W"]) / 1e3, 2)
        crawl_members[tag] = dict(
            P_cu_kW=round(pt["P_cu_W"] / 1e3, 2),
            P_fe_kW=round(pt["P_fe_W"] / 1e3, 2),
            P_fw_kW=round(pt["P_fw_W"] / 1e3, 2),
            P_inv_kW=round(pt["P_inv_W"] / 1e3, 2))
    RESULTS["thermal"]["crawl_loss_V1speed_kW"] = crawl_loss["V1"]
    RESULTS["thermal"]["crawl_loss_V2speed_kW"] = crawl_loss["V2"]
    RESULTS["thermal"]["crawl_loss_bandtop_kW"] = crawl_loss["bandtop"]
    RESULTS["thermal"]["crawl_loss_members_kW"] = crawl_members
    RESULTS["thermal"]["crawl_loss_worst_case"] = max(
        crawl_loss, key=crawl_loss.get)
    RESULTS["thermal"]["crawl_loss_kW"] = max(crawl_loss.values())
    # self-consistent variant: the governing loss evaluated AT its own
    # published steady winding temperature (170 C is the conservative
    # bookkeeping convention)
    tw_bt = RESULTS["thermal"]["crawl_bandtop_515Nm_oilspray"]["Tw_steady"]
    pt_sc = mc.point_full(REQ["crawl_cont_Nm"],
                          rpm_of_kmh(REQ["crawl_band_kmh"][1]),
                          BUS["v_nom"], T_wind=tw_bt)
    RESULTS["thermal"]["crawl_loss_bandtop_at_steadyTw_kW"] = round(
        (pt_sc["P_cu_W"] + pt_sc["P_fe_W"] + pt_sc["P_fw_W"]
         + pt_sc["P_inv_W"]) / 1e3, 2)
    ratio_sweep()
    bus_and_resistor()
    traction_envelope()
    cycle_runs()
    heat_ledger()
    interface_and_headline()
    with open(os.path.join(P.HERE, "results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1, default=str)
    print(f"\nDone in {time.time()-t0:.1f} s. results.json written.")


if __name__ == "__main__":
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, s):
            buf.write(s)
            sys.__stdout__.write(s)
            return len(s)

    sys.stdout = Tee()
    try:
        main()
    finally:
        sys.stdout = sys.__stdout__
        with open(os.path.join(P.HERE, "run_output.txt"), "w") as f:
            f.write(buf.getvalue())
