#!/usr/bin/env python3
"""Verify REPORT_WS2.md's headline numbers against results.json (round 4).

Run after run_ws2.py:  python3 check_report.py
Exits nonzero on any mismatch. Two kinds of check:
1. The embedded machine-readable interface block must deep-equal
   results.json `interface`.
2. Every entry in CHECKS below formats a value straight out of
   results.json and requires that exact string in the report text.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
TXT = open(os.path.join(HERE, "REPORT_WS2.md")).read()


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


CHECKS = [
    # (results.json path, format[, expected-in-report when format None])
    # --- machine / R10 rewind / R13 corner
    ("machine.T_peak_at_Ipeak_Nm", "{:.0f} Nm"),
    ("machine.P_peak_kW_vs_V.432", "{:.0f} kW"),
    ("machine.P_peak_kW_vs_V.662", "{:.0f} kW"),
    ("machine.P_peak_kW_vs_V.749", "{:.0f} kW"),
    ("machine.P_peak_kW_vs_V.432", "{:.1f} kW"),
    ("machine.P_peak_kW_vs_V.662", "{:.1f} kW"),
    ("machine.P_peak_kW_vs_V.749", "{:.1f} kW"),
    ("machine.P_peak_at_floor_ok_120kW", None, "≥120 kW 1-min everywhere"),
    ("machine.R13_corner_I_Apk", "{:.1f} A_pk"),
    ("machine.R13_corner_v_req_V", "{:.1f} V"),
    ("machine.T_max_at_bandtop_vmin_170C_Nm", "{:.1f} Nm"),
    ("machine.I_cont_Arms", "{:.1f} Arms"),
    ("machine.I_cont_vs_455Arms_r3_ratio", "{:.3f}"),
    ("machine.emf_ll_peak_at_7200_V", "{:.0f} V"),
    ("machine.char_current_A", "{:.0f} A"),
    ("machine.ucg_onset_kmh_at_432V", "{:.1f} km/h"),
    ("machine.ucg_onset_kmh_at_662V", "{:.1f} km/h"),
    ("machine.v_bus_no_ucg_below_7200rpm_V", "{:.0f} V"),
    ("machine.F1_70kmh_shaft_kW", "{:.1f} kW"),
    ("machine.F1_70kmh_shaft_kW_CdA5p4", "{:.1f} kW"),
    ("machine.P_dc_peak_draw_at_vmin_kW", "{:.1f} kW"),
    ("machine.I_dc_peak_draw_at_vmin_A", "{:.0f} A"),
    ("machine.rotor_tip_speed_at_7400_ms", "{:.0f} m/s"),
    ("machine.airgap_shear_at_peak_kPa", "{:.0f} kPa"),
    # --- topology
    ("topology.twin_penalty_total_kg", "+{:.0f} kg"),
    ("topology.IM_crawl_rotor_loss_W", None, "2.4 kW"),
    ("topology.IM_rotor_dT_over_stator_K", "+{:.0f} K"),
    ("topology.PM_spin_shaft_drag_85kmh_W", "{:,.0f} W"),
    ("topology.PM_spin_total_100kmh_W", "{:,.0f} W"),
    # --- thermal
    ("thermal.S1_180Nm_oilspray.Tw", "{:.1f} °C"),
    ("thermal.S1_180Nm_jacket.Tw", "{:.1f} °C"),
    ("thermal.S1gen_50kW_70kmh.Tw", "{:.1f} °C"),
    ("thermal.S2_95kW_10min_662V.Tw_end", "{:.0f} °C"),
    ("thermal.S2_95kW_10min_432V.Tw_end", "{:.1f} °C"),
    ("thermal.S2_95kW_steady_Tw", "{:.0f} °C"),
    ("thermal.crawl_510Nm_V1_oilspray.Tw_steady", "{:.1f} °C"),
    ("thermal.crawl_510Nm_V1_jacket.hold_from_S1warm_s", "{:.0f} s"),
    ("thermal.crawl_510Nm_V1_jacket.distance_m", "{:.0f} m"),
    ("thermal.crawl_510Nm_V2_oilspray.Tw_steady", "{:.1f} °C"),
    ("thermal.crawl_510Nm_V2_jacket.hold_from_S1warm_s", "{:.0f} s"),
    ("thermal.crawl_510Nm_V2_jacket.distance_m", "{:.0f} m"),
    ("thermal.crawl_bandtop_515Nm_oilspray.Tw_steady", "{:.1f} °C"),
    ("thermal.crawl_bandtop_515Nm_jacket.hold_from_S1warm_s", "{:.0f} s"),
    ("thermal.crawl_bandtop_515Nm_jacket.distance_m", "{:.0f} m"),
    ("thermal.T_cont_at_crawlspeed_oilspray_Nm", "{:.0f} Nm"),
    ("thermal.T_cont_at_crawlspeed_jacket_Nm", "{:.0f} Nm"),
    ("thermal.grade_cont_GVW_oilspray_pct", "{:.1f}%"),
    ("thermal.grade_cont_GVW_jacket_pct", "{:.1f}%"),
    ("thermal.crawl_Gws_sensitivity.G_ws_60.Tw_steady", "{:.1f} °C"),
    ("thermal.crawl_Gws_sensitivity.G_ws_75.Tw_steady", "{:.1f} °C"),
    ("thermal.crawl_Gws_sensitivity.G_ws_90.Tw_steady", "{:.1f} °C"),
    ("thermal.G_ws_cont_limit_floor_WK", "{:.1f} W/K"),
    ("thermal.hold_148Nm_standstill_oilspray.Tw_steady", "{:.1f} °C"),
    ("thermal.stall_515Nm_hold_s", "{:.0f} s"),
    ("thermal.inverter_Tj_peak_C", "{:.0f} °C"),
    ("thermal.inverter_Tj_cont_at_vmax_C", "{:.0f} °C"),
    ("thermal.gradehold_ledger.P_motor_total_kW", "{:.2f} kW"),
    ("thermal.gradehold_ledger.P_inv_kW", "{:.2f} kW"),
    ("thermal.gradehold_ledger.P_chain_kW", "{:.2f} kW"),
    ("thermal.S2_point_ledger.P_chain_kW", "{:.2f} kW"),
    # --- crawl loss set (R14 members)
    ("thermal.crawl_loss_kW", "{:.2f} kW"),
    ("thermal.crawl_loss_V1speed_kW", "{:.2f} kW"),
    ("thermal.crawl_loss_V2speed_kW", "{:.2f} kW"),
    ("thermal.crawl_loss_bandtop_kW", "{:.2f} kW"),
    ("thermal.crawl_loss_bandtop_at_steadyTw_kW", "{:.2f} kW"),
    ("thermal.crawl_loss_members_kW.bandtop.P_cu_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.bandtop.P_fe_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.bandtop.P_fw_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.bandtop.P_inv_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.V1.P_cu_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.V1.P_fe_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.V2.P_cu_kW", "{:.2f}"),
    ("thermal.crawl_loss_members_kW.V2.P_fe_kW", "{:.2f}"),
    # --- ratio sweep
    ("ratio_sweep.loss_spread_pct_of_10to1", "{:.1f}%"),
    ("ratio_sweep.total_loss_kWh_by_ratio.8", "{:.3f}"),
    ("ratio_sweep.total_loss_kWh_by_ratio.9", "{:.3f}"),
    ("ratio_sweep.total_loss_kWh_by_ratio.10", "{:.3f}"),
    ("ratio_sweep.total_loss_kWh_by_ratio.11", "{:.3f}"),
    ("ratio_sweep.total_loss_kWh_by_ratio.12", "{:.3f}"),
    ("ratio_sweep.delta_9_vs_10_pct", "{:.2f}%"),
    ("ratio_sweep.delta_11_vs_10_pct", "{:.2f}%"),
    ("ratio_sweep.delta_12_vs_10_pct", "{:.2f}%"),
    ("ratio_sweep.mass_delta_9_vs_10_kg", "+{:.1f} kg"),
    ("ratio_sweep.mass_per_point_kg.10_to_11", "{:.1f} kg"),
    ("ratio_sweep.mass_per_point_kg.11_to_12", "{:.1f} kg"),
    # --- bus / cables (R14 sets)
    ("bus.cables.cable_mass_kg", "{:.1f} kg"),
    ("bus.cables.detail.genset_to_bus.i_size_A", "{:.1f} A"),
    ("bus.cables.detail.genset_to_bus.mass_kg", "{:.2f} kg"),
    ("bus.cables.detail.pack_to_bus.i_size_A", "{:.1f} A"),
    ("bus.cables.detail.pack_to_bus.mass_kg", "{:.2f} kg"),
    ("bus.cables.detail.inverter_to_motor.i_size_A", "{:.1f} Arms"),
    ("bus.cables.detail.inverter_to_motor.mass_kg", "{:.2f} kg"),
    ("bus.cables.detail.inverter_to_motor.margin_pct", "{:.1f}%"),
    ("bus.cables.detail.pack_to_bus.transient_cases."
     "R8 125 kW discharge at the floor, undegraded, 60 s.adiabatic_dT_K",
     "{:.1f} K"),
    ("bus.cables.detail.pack_to_bus.transient_cases."
     "R8 125 kW discharge at the floor, undegraded, 60 s.conductor_T_end_C",
     "{:.1f} °C"),
    ("bus.cables.detail.pack_to_bus.conductor_T_steady_C", "{:.1f} °C"),
    ("bus.cables.detail.chopper_to_resistor.i_size_A", "{:.1f} A"),
    ("bus.cables.detail.chopper_to_resistor.mass_kg", "{:.2f} kg"),
    ("bus.s2_phase_current_floor_Arms", "{:.1f} Arms"),
    ("bus.s2_phase_current_Arms", "{:.1f}"),
    # --- resistor
    ("resistor.R_ohm", "{:.2f} Ω"),
    ("resistor.P_fullduty_at_vmax_kW", "{:.1f} kW"),
    ("resistor.P_fullduty_at_vtransient_kW", "{:.1f} kW"),
    ("resistor.assembly_mass_kg", "{:.0f} kg"),
    ("resistor.assembly_volume_L", "{:.0f} L"),
    ("resistor.air_flow_m3_h", "{:,.0f} m³/h"),
    ("resistor.ribbon_length_m", "{:.1f} m"),
    ("resistor.ribbon_mass_kg", "{:.1f} kg"),
    ("resistor.ribbon_area_m2", "{:.2f} m²"),
    ("resistor.ribbon_T_at_design_C", "{:.0f} °C"),
    ("resistor.ribbon_T_at_50kW_C", "{:.0f} °C"),
    ("resistor.ribbon_T_margin_K", "{:.0f} K"),
    ("resistor.ribbon_T_at_design_2000m_C", "{:.0f} °C"),
    ("resistor.ribbon_T_at_50kW_2000m_C", "{:.0f} °C"),
    ("resistor.ribbon_T_margin_2000m_K", "{:.0f} K"),
    ("resistor.P_ribbon_limit_2000m_kW", "{:.1f} kW"),
    ("resistor.ribbon_tau_s", "{:.1f} s"),
    ("resistor.transient_10s_dT_K", "{:.1f} K"),
    ("resistor.chopper_loss_50kW_W", "{:.0f} W"),
    ("resistor.chopper_loss_ceiling_W", "{:.0f} W"),
    ("resistor.cable_limited_ceiling_kW", "{:.1f} kW"),
    # --- traction
    ("traction.mu_required.mu_launch_flat_gvw", "{:.3f}"),
    ("traction.mu_required.mu_launch_flat_curb", "{:.3f}"),
    ("traction.mu_required.mu_launch_20pct_gvw", "{:.3f}"),
    ("traction.mu_required.mu_launch_20pct_curb", "{:.3f}"),
    ("traction.envelope.5.T_motor_brake_Nm", "{:.0f} Nm"),
    # --- cycles (R12 one-chain, bus-side)
    ("cycles.VOLT_SUB_V1.eta_mot_avg", "{:.3f}"),
    ("cycles.VOLT_REG_V2_iMMD_approx.eta_mot_avg", "{:.3f}"),
    ("cycles.VOLT_SUB_V1.eta_gen_avg", "{:.3f}"),
    ("cycles.VOLT_REG_V2_iMMD_approx.eta_gen_avg", "{:.3f}"),
    ("cycles.VOLT_SUB_V1.mean_heat_kW", "{:.2f} kW"),
    ("cycles.VOLT_REG_V2_iMMD_approx.mean_heat_kW", "{:.2f} kW"),
    ("cycles.VOLT_SUB_V1.E_dc_gen_kWh", "{:.2f} kWh"),
    ("cycles.VOLT_REG_V2_iMMD_approx.E_dc_gen_kWh", "{:.2f} kWh"),
    ("cycles.VOLT_REG_V2_iMMD_approx.E_spin_shaft_kWh", "{:.2f} kWh"),
    ("cycles.VOLT_REG_V2_iMMD_approx.E_spin_bus_kWh", "{:.2f} kWh"),
    # --- maps
    ("maps.stats.662.best_eta", "{:.4f}"),
    ("maps.stats.662.n_feasible", "{:,d} feasible"),
    # --- interface (R14 worst-case fields, the numbers consumers take)
    ("interface.mass_kg.total_kg", "{:.1f}"),
    ("interface.coolant.heat_worst_case_kW.value", "{:.2f} kW"),
    ("interface.coolant.heat_at_S2_rating_kW", "{:.2f} kW"),
    ("interface.coolant.heat_at_gradehold_90p5kW_kW", "{:.2f} kW"),
    ("interface.electrical_ratings.continuous_Arms.value", "{:.1f} Arms"),
    ("interface.electrical_ratings.ten_min_Arms.value", "{:.1f} Arms"),
    ("interface.electrical_ratings.peak_60s_Apk", "{:.0f} A_pk"),
    ("interface.electrical_ratings.peak_60s_Arms", "{:.1f} Arms"),
    ("interface.electrical_ratings.inverter_Tj_at_continuous_rating_C.value",
     "{:.0f} °C"),
    ("interface.resistor.P_cont_kW_any_bus_V.value", "{:.0f} kW"),
    ("interface.resistor.second_stage_ceiling_kW.value", "{:.1f} kW"),
    ("interface.ws7_verification.continuous_limit_floor_WK", "{:.1f} W/K"),
    ("interface.ws7_verification.G_ws_heat_run_requirement_WK",
     None, "G_ws ≥ 90 W/K"),
    ("interface.spin_drag.shaft_drag_85kmh_W", "{:,.0f} W"),
    ("interface.spin_drag.E_engine_side_VOLTREG_kWh", "{:.2f} kWh"),
    ("interface.spin_drag.E_bus_side_VOLTREG_kWh", "{:.2f} kWh"),
    ("interface.dc_bus_loads_coexisting.resistor_blower_kW", "{:.2f} kW"),
    ("interface.dc_bus_loads_coexisting.pack_heater_kW", "{:.0f} kW"),
]

fails = []
for entry in CHECKS:
    path, fmt = entry[0], entry[1]
    val = get(path)
    if fmt is None:
        needle = entry[2]
    else:
        needle = fmt.format(val)
    if needle not in TXT:
        fails.append((path, needle))

# interface block deep-equality
m = re.search(r"```json\n(.*?)```", TXT, re.S)
if not m:
    fails.append(("interface block", "MISSING"))
else:
    blk = json.loads(m.group(1))
    if blk != R["interface"]:
        for k in set(blk) | set(R["interface"]):
            if blk.get(k) != R["interface"].get(k):
                fails.append((f"interface.{k}", "BLOCK != results.json"))

# ratio sweep table rows
for row in R["ratio_sweep"]["rows"]:
    for needle in (f"{row['mass_kg']:.1f} kg", f"{row['sub_loss_kWh']:.3f} kWh",
                   f"{row['reg_loss_kWh']:.3f} kWh"):
        if needle not in TXT:
            fails.append((f"ratio_sweep {row['ratio']}", needle))

# R12 hygiene: no scalar-PE member may exist anywhere in the exports
blob = json.dumps(R)
for token in ("pe_convention", "ws1_scalar", "0.8924"):
    if token in blob:
        fails.append(("R12 hygiene", f"'{token}' still present in results.json"))

# R13 hygiene: no WS2-E1 conditioning may remain in the interface
if "WS2-E1" in json.dumps(R["interface"]):
    fails.append(("R13 hygiene", "WS2-E1 conditioning still in interface"))

# cable transient hygiene: every listed transient must actually clear
# its short-term check (a false flag here was the round-4 preflight's
# one material finding — never export a failing check silently again)
for run, d in R["bus"]["cables"]["detail"].items():
    if "transients_ok" in d and not d["transients_ok"]:
        fails.append((f"bus.cables.{run}", "transient check FAILED in export"))

if fails:
    print(f"FAIL: {len(fails)} report numbers do not verify:")
    for p, n in fails:
        print(f"  {p}: expected '{n}' in REPORT_WS2.md")
    sys.exit(1)
print(f"OK: all {len(CHECKS)} headline checks + interface block + "
      f"ratio table + R12/R13 hygiene verify against results.json")
