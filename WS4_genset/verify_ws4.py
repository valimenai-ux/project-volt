#!/usr/bin/env python3
"""
Project Volt - WS4. Verifies that every headline number in REPORT_WS4.md
is exactly the rendering of the corresponding value in results_ws4.json
(nothing transcribed by hand), and that the report's machine-readable
interface block is byte-identical to results_ws4.json -> interface_ws4.

    python3 verify_ws4.py        (exit 0 = verified)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_ws4.json")))
REPORT = open(os.path.join(HERE, "REPORT_WS4.md")).read()


def get(path):
    o = R
    for k in path.split("/"):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


# (json path, format, description) -> the rendered string must appear
# verbatim in REPORT_WS4.md.
CHECKS = [
    # gate G1-R headline
    ("gate_g1/nominal/ensemble/margin_pct_min", "{:.2f}%", "G1 min margin"),
    ("gate_g1/nominal/ensemble/margin_pct_median", "{:.2f}%", "G1 median"),
    ("gate_g1/nominal/ensemble/margin_pct_max", "{:.2f}%", "G1 max margin"),
    # G1-R: prior-convention anchor + one-factor attribution (directive 3)
    ("gate_g1_prior_convention/ensemble/margin_pct_min", "{:.2f}%",
     "prior anchor min"),
    ("gate_g1_prior_convention/ensemble/margin_pct_median", "{:.2f}%",
     "prior anchor median"),
    ("gate_g1_one_factor/spin_drag_alone/min", "{:.2f}%",
     "one-factor spin min"),
    ("gate_g1_one_factor/spin_drag_alone/delta_pp_min", "{:+.2f} pp",
     "one-factor spin delta"),
    ("gate_g1_one_factor/map_vs_scalar_alone/min", "{:.2f}%",
     "one-factor maps min"),
    ("gate_g1_one_factor/map_vs_scalar_alone/delta_pp_min", "{:+.2f} pp",
     "one-factor maps delta"),
    ("gate_g1_one_factor/both_g1r/delta_pp_min", "{:+.2f} pp",
     "one-factor combined delta"),
    # G1-R: map-vintage robustness (keys follow WS2's exports) + chain
    # of record + spin member
    *[(f"gate_g1_map_vintage_check/{k}/min", "{:.2f}%",
       f"vintage {k} min")
      for k in sorted(R.get("gate_g1_map_vintage_check", {}))],
    ("ws2_chain_of_record/spin_drag_member/rate_shaft_kW_while_locked",
     "{:.3f} kW", "spin shaft rate"),
    ("ws2_chain_of_record/spin_drag_member/rate_bus_kW_while_locked",
     "{:.3f} kW", "spin bus rate"),
    ("ws2_chain_of_record/spin_drag_member/e_spin_shaft_kWh_per_VOLT_REG",
     "{:.4f}", "spin shaft export kWh"),
    ("ws2_chain_of_record/spin_drag_member/e_spin_bus_kWh_per_VOLT_REG",
     "{:.4f} kWh", "spin bus export kWh"),
    ("gate_g1/nominal/ensemble/a_spin_shaft_kwh_min", "{:.3f}–",
     "a spin shaft min"),
    ("gate_g1/nominal/ensemble/a_spin_shaft_kwh_max", "{:.3f} kWh",
     "a spin shaft max"),
    ("gate_g1/nominal/ensemble/a_spin_bus_kwh_min", "{:.3f}–",
     "a spin bus min"),
    ("gate_g1/nominal/ensemble/a_spin_bus_kwh_max", "{:.3f} kWh",
     "a spin bus max"),
    # G1-R: genset-conditioning bracket + CdA break-even + r3 record
    ("gate_g1/cda_5.4/ensemble/margin_pct_max", "{:.2f}%", "cda54 max"),
    ("gate_g1_genset_conditioning_bracket/replacement_3pct_class/min",
     "{:.2f}%", "bracket replacement min"),
    ("gate_g1_genset_conditioning_bracket/replacement_3pct_class/median",
     "{:.2f}%", "bracket replacement median"),
    ("gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/min",
     "{:.2f}%", "bracket stacked min"),
    ("gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/median",
     "{:.2f}%", "bracket stacked median"),
    ("gate_g1_interim_r3_vintage_record/margin_pct_min", "{:.2f}",
     "r3 interim min"),
    ("gate_g1_interim_r3_vintage_record/margin_pct_median", "{:.2f}",
     "r3 interim median"),
    ("gate_g1_interim_r3_vintage_record/margin_pct_max", "{:.2f}",
     "r3 interim max"),
    # G1-R: R12 chain sanity restatements
    ("sanity/series_fuel_to_wheel_g_per_kWh_R12", "{:.1f} g/kWh",
     "series fuel-to-wheel R12"),
    ("sanity/eta_chain_bus_to_wheel_R12_energy_weighted", "{:.4f}",
     "R12 chain eta"),
    ("sanity/banking_redeploy_eta_R12", "{:.4f}", "R12 banking eta"),
    # G1-R: heat ledger spin rows
    ("heat_ledger_ws6/G1a_VOLT_REG_cycle_average/pm_spin_shaft_kWh_per_cycle",
     "{:.2f} kWh", "G1a spin shaft heat"),
    ("heat_ledger_ws6/G1a_VOLT_REG_cycle_average/pm_spin_bus_kWh_per_cycle",
     "{:.2f} kWh", "G1a spin bus heat"),
    ("gate_g1/nominal/per_seed/23/a/l_per_100km", "{:.2f} L/100 km",
     "mode a fuel ref seed"),
    ("gate_g1/nominal/per_seed/23/b/l_per_100km", "{:.2f} L/100 km",
     "mode b fuel ref seed"),
    ("gate_g1/nominal/per_seed/23/a/fuel_kg", "{:.2f} kg", "a fuel kg"),
    ("gate_g1/nominal/per_seed/23/b/fuel_kg", "{:.2f} kg", "b fuel kg"),
    ("gate_g1/cda_5.4/ensemble/margin_pct_min", "{:.2f}%", "cda54 min"),
    ("gate_g1/cda_5.4/ensemble/margin_pct_median", "{:.2f}%", "cda54 med"),
    ("gate_g1/aux_4kW/ensemble/margin_pct_min", "{:.2f}%", "aux4 min"),
    ("gate_g1/hot_45C_sea_level/ensemble/margin_pct_min", "{:.2f}%",
     "hot-day min (r2/F4)"),
    ("gate_g1/hot_45C_sea_level/ensemble/margin_pct_median", "{:.2f}%",
     "hot-day median (r2/F4)"),
    ("gate_g1/hot_45C_sea_level/ensemble/margin_pct_max", "{:.2f}%",
     "hot-day max (r2/F4)"),
    ("gate_g1/alt2000m_45C/ensemble/margin_pct_min", "{:.2f}%", "alt min"),
    ("gate_g1/alt2000m_45C/ensemble/margin_pct_median", "{:.2f}%",
     "alt median"),
    ("gate_g1/reference_curve/ensemble/margin_pct_min", "{:.2f}%",
     "refcurve min"),
    # secondary G1 envelopes quoted in s4.2 / F-4 / ESC-5 (r2: F1, F3)
    ("gate_g1/nominal/ensemble/b_emerg_s_min", "{:.0f}", "b emerg min nom"),
    ("gate_g1/nominal/ensemble/b_emerg_s_max", "{:.0f} s", "b emerg max nom"),
    ("gate_g1/cda_5.4/ensemble/b_emerg_s_min", "{:,.0f}", "b emerg min cda"),
    ("gate_g1/cda_5.4/ensemble/b_emerg_s_max", "{:,.0f} s",
     "b emerg max cda"),
    ("gate_g1/nominal/ensemble/b_unserved_kwh_max", "{:.2f} kWh",
     "b unserved max nom"),
    ("gate_g1/cda_5.4/ensemble/b_unserved_kwh_min", "{:.2f}–",
     "b unserved min cda"),
    ("gate_g1/cda_5.4/ensemble/b_unserved_kwh_max", "{:.2f} kWh",
     "b unserved max cda"),
    ("gate_g1/nominal/ensemble/b_over_rating_s_min", "{:.1f}–",
     "b over-rating min nom"),
    ("gate_g1/nominal/ensemble/b_over_rating_s_max", "{:.1f} s",
     "b over-rating max nom"),
    ("gate_g1/cda_5.4/ensemble/b_over_rating_s_min", "{:.1f}–",
     "b over-rating min cda"),
    ("gate_g1/cda_5.4/ensemble/b_over_rating_s_max", "{:.1f} s",
     "b over-rating max cda"),
    ("gate_g1/nominal/ensemble/a_over_rating_s_max", "{:.1f} s",
     "a over-rating max (r2/F7)"),
    ("gate_g1/nominal/ensemble/a_bank_kwh_min", "{:.1f}–", "a bank min"),
    ("gate_g1/nominal/ensemble/a_bank_kwh_max", "{:.1f} kWh", "a bank max"),
    ("gate_g1/nominal/ensemble/a_starts_min", "{:.0f}", "a starts min"),
    ("gate_g1/nominal/ensemble/a_starts_max", "{:.0f}", "a starts max"),
    # R6 corner
    ("derate_model/factor_at_r6_corner", "{:.4f}", "derate factor"),
    ("interface_ws4/v2_genset/r6_corner/delivered_shaft_kW", "{:.1f} kW",
     "corner delivered"),
    ("interface_ws4/v2_genset/r6_corner/margin_kW", "{:+.2f} kW",
     "corner margin"),
    # pinned points and maps
    ("gate_g1/nominal/pinned_point/rpm", "{:,.0f} rpm", "V2 pin rpm"),
    ("gate_g1/nominal/pinned_point/trq_Nm", "{:.0f} Nm", "V2 pin trq"),
    ("gate_g1/nominal/pinned_point/p_shaft_kw", "{:.1f} kW", "V2 pin kW"),
    ("gate_g1/nominal/pinned_point/bsfc", "{:.1f} g/kWh", "V2 pin bsfc"),
    ("gate_g1/nominal/pinned_point/p_bus_kw", "{:.1f} kW", "V2 pin bus"),
    ("v1_start_stop/fixed_point/rpm", "{:,.0f} rpm", "V1 pin rpm"),
    ("v1_start_stop/fixed_point/p_shaft_kw", "{:.1f} kW", "V1 pin kW"),
    ("v1_start_stop/fixed_point/bsfc", "{:.1f} g/kWh", "V1 pin bsfc"),
    ("v1_start_stop/fixed_point/p_bus_kw", "{:.1f} kW", "V1 pin bus"),
    ("bsfc_maps/4HK1-TC-ref-W/map_min/bsfc", "{:.1f} g/kWh", "ref map min"),
    ("bsfc_maps/4HK1-V2C-W/bsfc_at_rated_continuous", "{:.1f} g/kWh",
     "V2 rated-cont bsfc"),
    ("bsfc_maps/V3307-V1C-W/bsfc_at_rated_continuous", "{:.1f} g/kWh",
     "V1 rated-cont bsfc (r2/F6)"),
    # direct path / grade holds
    ("direct_path_6pct/candidate_band_at_6pct_kmh/0", "{:.1f}", "band lo"),
    ("direct_path_6pct/candidate_band_at_6pct_kmh/1", "{:.1f} km/h",
     "band hi"),
    ("direct_path_6pct/candidate_max_grade_pct", "{:.2f}%", "max grade"),
    ("direct_path_6pct/reference_max_grade_pct", "{:.2f}%",
     "ref max grade"),
    ("series_grade_hold_candidate/hold_speed_6pct_GVW_CdA42_aux2_kmh",
     "{:.1f} km/h", "series hold nominal"),
    ("series_grade_hold_candidate/"
     "hold_speed_6pct_corner_20pct_payload_CdA54_aux4_2000m45C_kmh",
     "{:.1f} km/h", "series hold corner"),
    ("v1_capability/charge_sustaining_top_speed_at_50kW_cont_kmh",
     "{:.1f} km/h", "V1 top speed"),
    # V1 start-stop
    ("v1_start_stop/hysteresis_sweep_ref_seed/0.8kWh/starts_per_8h_shift",
     "{:.0f} starts", "V1 starts ref"),
    ("v1_start_stop/ensemble_hyst_0.8kWh/starts_per_8h_min", "{:.0f}",
     "V1 starts min"),
    ("v1_start_stop/ensemble_hyst_0.8kWh/starts_per_8h_max", "{:.0f}",
     "V1 starts max"),
    ("v1_start_stop/usable_3.0_hyst_1.6/starts_per_8h_shift",
     "{:.0f} starts", "V1 starts 3kWh"),
    ("v1_start_stop/fuel_saving_vs_continuous_pct", "{:.1f}%",
     "V1 fuel saving"),
    ("v1_start_stop/hysteresis_sweep_ref_seed/0.8kWh/fuel_l_per_h",
     "{:.2f} L/h", "V1 fuel/h"),
    ("v1_start_stop/hysteresis_sweep_ref_seed/0.5kWh/fuel_l_per_h",
     "{:.2f} L/h", "V1 fuel/h 0.5 row"),
    ("v1_start_stop/usable_3.0_hyst_1.6/fuel_l_per_h", "{:.2f} L/h",
     "V1 fuel/h 3.0-usable row (r2/F6)"),
    ("v1_start_stop/cold_regen0_aux4_ref_seed/fuel_l_per_h", "{:.2f} L/h",
     "V1 cold fuel/h"),
    # heat ledger
    ("heat_ledger_ws6/V2_grade_hold_6pct_61kmh_series_10min/"
     "electrical_chain_kW_ws4_maps", "{:.1f} kW", "elec chain ws4"),
    ("heat_ledger_ws6/V2_grade_hold_6pct_61kmh_series_10min/"
     "engine_radiator_package_kW", "{:.1f} kW", "grade hold radiator"),
    ("heat_ledger_ws6/V2_R6_corner_continuous/engine_radiator_package_kW",
     "{:.1f} kW", "corner radiator"),
    ("heat_ledger_ws6/V2_R6_corner_continuous/engine_exhaust_kW",
     "{:.1f} kW", "corner exhaust"),
    ("heat_ledger_ws6/V1_fixed_point_running/engine_radiator_package_kW",
     "{:.1f} kW", "V1 radiator"),
    ("heat_ledger_ws6/G1a_VOLT_REG_cycle_average/engine_rejection_avg_kW",
     "{:.1f} kW", "G1a engine avg"),
    # sanity
    ("sanity/series_fuel_to_wheel_g_per_kWh", "{:.0f} g/kWh",
     "series fuel-to-wheel"),
    ("sanity/motoring_drag_1706rpm_kW", "{:.1f} kW", "motoring drag"),
]

fails = []
for path, fmt, desc in CHECKS:
    s = fmt.format(get(path))
    if s not in REPORT:
        fails.append(f"  MISSING [{desc}]: expected verbatim '{s}' "
                     f"(from {path})")

# machine-readable interface block must be byte-identical
iface = json.dumps(R["interface_ws4"], indent=1, default=float)
if iface not in REPORT:
    fails.append("  MISSING: interface block is not byte-identical to "
                 "results_ws4.json -> interface_ws4")

if fails:
    print(f"VERIFY FAILED ({len(fails)} of {len(CHECKS)+1} checks):")
    print("\n".join(fails))
    sys.exit(1)
print(f"VERIFIED: {len(CHECKS)} headline renderings + interface block "
      "match results_ws4.json verbatim.")
