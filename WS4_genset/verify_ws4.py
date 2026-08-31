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

    # =====================================================================
    # KX — R23 errata pins (F1-F5) and the R22a series_duty_v2 run
    # =====================================================================
    # F1: the CdA 5.4 positive-seed count, rendered from the export.
    # (The four-occurrence pin that stops a partial correction is the
    # structural check below, not this rendering.)
    ("gate_g1/cda_5.4/ensemble/seeds_margin_positive_n",
     "{:.0f} of 8 seeds marginally positive", "F1 CdA 5.4 positive count"),
    ("gate_g1/cda_5.4/ensemble/seeds_total", "{:.0f} seeds marginally",
     "F1 seed-set size"),
    ("interface_ws4/gate_g1/verdict/condition_dependence/"
     "seeds_margin_positive_n_CdA_5.4", "{:.0f} of 8 seeds",
     "F1 interface mirror"),
    # F2: measured boundary exposure and the one-sided bound
    ("chain_boundary_exposure/cases/nominal/envelope/"
     "exposure_s_motoring_min", "{:.1f}–", "F2 nominal exposure min"),
    ("chain_boundary_exposure/cases/nominal/envelope/"
     "exposure_s_motoring_max", "{:.1f} s/cycle", "F2 nominal exposure max"),
    ("chain_boundary_exposure/cases/nominal/envelope/"
     "exposure_s_motoring_on_locked_samples_max", "{:.1f} s are locked",
     "F2 nominal locked exposure max"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "exposure_s_motoring_min", "{:.1f}–", "F2 CdA exposure min"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "exposure_s_motoring_max", "{:.1f}", "F2 CdA exposure max"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "exposure_s_motoring_on_locked_samples_max", "{:.1f} s of it on",
     "F2 CdA locked exposure max"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "one_sided_pp_locked_linear_max", "**{:.4f} pp**", "F2 one-sided pp"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "one_sided_pp_locked_hostile_2x_max", "{:.4f} pp on a hostile",
     "F2 one-sided pp hostile"),
    ("chain_boundary_exposure/cases/cda_5.4/envelope/"
     "over_boundary_wheel_kWh_max", "{:.4f} kWh", "F2 over-boundary energy"),
    # F3: the printed vintage spread, both spans
    ("gate_g1_map_vintage_spread/spread_pp_432_749V_window",
     "**{:.2f} pp**", "F3 window spread"),
    ("gate_g1_map_vintage_spread/spread_pp_incl_r3_interim",
     "**{:.2f} pp**", "F3 spread incl. r3-interim"),
    # F4: the WS4-relative traction-map path (structural check below too)
    ("ws2_chain_of_record/map_file_ws4_relative", "{}", "F4 map path"),
    ("interface_ws4/gate_g1/traction_chain_of_record/map_file", "{}",
     "F4 interface map path"),
    # F5: both chain weightings and both fuel-to-wheel rates
    ("sanity/eta_chain_bus_to_wheel_series_duty_weighted", "**{:.4f}**",
     "F5 series-duty chain eta"),
    ("sanity/series_fuel_to_wheel_g_per_kWh_series_duty", "**{:.1f} g/kWh**",
     "F5 series-duty fuel-to-wheel"),
    ("chain_weighting_convention/series_duty_weighted/eta_bus_to_wheel_min",
     "{:.4f}–", "F5 series-duty eta min"),
    ("chain_weighting_convention/series_duty_weighted/eta_bus_to_wheel_max",
     "{:.4f}", "F5 series-duty eta max"),
    # --- interface archival status (KX item 3)
    ("interface_ws4/gate_g1/status", "{}", "gate archival status"),
    # --- R22a series_duty_v2 headlines
    ("series_duty_v2/_inputs/usable_bus_kWh", "{:.2f} kWh",
     "delivered pack usable"),
    ("series_duty_v2/_inputs/usable_bus_kWh", "{:.6f} kWh",
     "delivered pack usable, full precision"),
    ("series_duty_v2/_inputs/superseded_floor_kWh", "R8 {:.1f} kWh",
     "superseded R8 floor"),
    ("series_duty_v2/unserved_energy_verdict/worst_case_kWh",
     "{:.4f}\n> kWh", "R22a unserved worst case"),
    ("series_duty_v2/unserved_energy_verdict/worst_case_governing_case",
     "{}", "R22a unserved governing case"),
    ("series_duty_v2/r22d_coast_spin_member/unbooked_pp_max",
     "**{:.4f} pp**", "R22d unbooked pp"),
    ("series_duty_v2/r16_binding_analysis/peak_regen_to_pack_kW_bus",
     "**{:.1f} kW bus**", "R16 peak regen"),
    ("series_duty_v2/r16_binding_analysis/cold_side_binding_cell_C",
     "**{:.1f} °C**", "R16 cold-side binding temperature"),
    ("series_duty_v2/r16_binding_analysis/hot_side_binding_cell_C",
     "**{:.1f} °C**", "R16 hot-side binding temperature"),
    ("series_duty_v2/r16_binding_analysis/"
     "accept_at_ws3_loop_ceiling_55C_kW", "**{:.1f} kW**",
     "R16 acceptance at the WS3 loop ceiling"),
    ("series_duty_v2/soc_window_check/gate_soc_usable_equivalent",
     "SOC {:.4f} of *usable*", "SOC gate in usable terms"),
    ("series_duty_v2/soc_window_check/gate_soc_nameplate",
     "SOC {:.2f} nameplate", "SOC gate in nameplate terms"),
    *[(f"series_duty_v2/soc_window_check/cases/{c}/{k}", fmt,
       f"SOC window {c} {k}")
      for c in ("nominal", "cda_5.4", "alt2000m_45C")
      for k, fmt in (("t_below_gate_s_min", "{:.1f}–"),
                     ("t_below_gate_s_max", "{:.1f}"),
                     ("soc_nameplate_min", "{:.4f}"))],
    ("series_duty_v2/r8_power_envelope_bracket/worst_unserved_kWh",
     "**{:.3f} kWh**", "R8 bracket worst unserved"),
    ("series_duty_v2/r8_power_envelope_bracket/"
     "worst_unserved_governing_case", "{}", "R8 bracket governing case"),
    ("series_duty_v2/_trace_files/trace_10Hz", "{}", "R34 trace file"),
    ("series_duty_v2/_trace_files/trace_10Hz_rows", "{:,.0f} rows",
     "R34 trace rows"),
    ("series_duty_v2/_trace_files/soc_trajectories", "{}",
     "SOC trajectory file"),
    # per-case ordered exports rendered in the s4-KX table
    *[(f"series_duty_v2/cases/{c}/ensemble/{k}", fmt, f"R22a {c} {k}")
      for c in ("nominal", "cda_5.4", "alt2000m_45C")
      for k, fmt in (("fuel_energy_kWh_per_km_min", "{:.3f}–"),
                     ("fuel_energy_kWh_per_km_max", "{:.3f}"),
                     ("unserved_bus_kWh_max", "{:.4f}"),
                     ("above_pin_demand_s_min", "{:,.1f}–"),
                     ("above_pin_demand_s_max", "{:,.1f}"),
                     ("genset_starts_per_h_min", "{:.1f}–"),
                     ("genset_starts_per_h_max", "{:.1f}"),
                     ("soc_min_min", "{:.3f}–"),
                     ("soc_max_max", "{:.3f}"),
                     ("pack_dis_peak_kW_max", "{:.1f}"),
                     ("motor_over_rating_s_max", "{:.1f}"),
                     ("fuel_energy_kWh_per_payload_tonne_km_max", "{:.4f}"))],
    # =====================================================================
    # KX r2 headline renderings (rework against FINDINGS_KX_r1.md)
    # =====================================================================
    # KX-B1: the two readings of R16
    ("series_duty_v2/r16_binding_analysis/peak_pack_charge_kW_bus",
     "**{:.1f} kW bus**", "B1 peak pack charge"),
    ("series_duty_v2/r16_binding_analysis/"
     "pack_charge_above_r16_accept_longest_s/worst_case_max", "**{:.1f} s**",
     "B1 longest excursion"),
    ("series_duty_v2/r16_binding_analysis/pulse10s_at_ws3_loop_ceiling_55C_kW",
     "**{:.1f} kW**", "B1 55C pulse rating"),
    ("series_duty_v2/r16_binding_analysis/accept_at_50C_kW", "**{:.1f} kW**",
     "B1 50C continuous acceptance"),
    *[(f"series_duty_v2/r16_binding_analysis/"
       f"pack_charge_above_r16_accept_s/per_case_{mm}/{c}", fmt,
       f"B1 above-acceptance {c} {mm}")
      for c in ("nominal", "cda_5.4", "alt2000m_45C")
      for mm, fmt in (("min", "{:.1f}\u2013"), ("max", "{:.1f}"))],
    ("series_duty_v2/r16_pack_acceptance_bracket/worst_shed_kWh",
     "**{:.3f} kWh**", "B1 bracket worst shed"),
    ("series_duty_v2/r16_pack_acceptance_bracket/worst_shed_governing_case",
     "{}", "B1 bracket shed governing case"),
    ("series_duty_v2/r16_pack_acceptance_bracket/worst_unserved_kWh",
     "**{:.4f} kWh**", "B1 bracket unserved"),
    ("series_duty_v2/r16_pack_acceptance_bracket/"
     "fuel_delta_pct_paired_worst_max", "**{:+.3f} %**",
     "KX2-M3(b) bracket paired worst fuel delta"),
    # KX-M1: the genset above its own continuous rating
    *[(f"series_duty_v2/cases/{c}/ensemble/"
       f"engine_over_continuous_rating_s_{mm}", fmt,
       f"M1 over-rating {c} {mm}")
      for c in ("nominal", "cda_5.4", "alt2000m_45C")
      for mm, fmt in (("min", "{:.1f}\u2013"), ("max", "{:.1f}"))],
    ("series_duty_v2/companion_bp_capability_comparison/axes/"
     "engine_over_continuous_rating_s/mode_b_block_of_record/worst_case_max",
     "**{:.1f} s**", "M1 worst over-rating seconds"),
    ("series_duty_v2/companion_bp_capability_comparison/axes/"
     "engine_shaft_peak_kW/mode_b_block_of_record/worst_case_max",
     "**{:.1f} kW", "M1 peak engine shaft"),
    ("series_duty_v2/companion_bp_capability_comparison/"
     "engine_automotive_peak_kW", "{:.1f} kW", "M1 automotive peak"),
    ("series_duty_v2/engine_continuous_rating_bracket/worst_unserved_kWh",
     "{:.4f}", "M1 bracket unserved"),
    # KX-B2: the companion on the capability axes
    ("series_duty_v2/companion_bp_capability_comparison/axes/"
     "pack_discharge_peak_kW_bus/mode_bp_companion/worst_case_max",
     "{:.1f} kW vs 125", "B2 bp discharge peak"),
    ("series_duty_v2/companion_bp_capability_comparison/axes/"
     "pack_charge_peak_kW_bus/mode_bp_companion/worst_case_max",
     "{:.1f} kW vs 110", "B2 bp charge peak"),
    # KX-M3: the payload denominator
    ("series_duty_v2/_inputs/payload_metric_basis/payload_basis_t",
     "**{:.1f} t**", "M3 payload basis t"),
    ("series_duty_v2/_inputs/payload_metric_basis/payload_basis_kg",
     "{:,.0f} kg", "M3 payload basis kg"),
    # KX-M2: the live block's own chain of record
    ("series_duty_v2/_inputs/chain_of_record/map_file", "`{}`",
     "M2 live chain map path"),
    # KX-m2: D5 closed
    *[(f"chain_boundary_exposure/d5_reconciliation/counts_s_per_cycle/{c}/"
       f"strict_linear_envelope_r3_adjudicator_criterion/{i}", fmt,
       f"m2 linear count {c}[{i}]")
      for c in ("nominal", "cda_5.4")
      for i, fmt in ((0, "{:.1f}\u2013"), (1, "{:.1f}"))],
    ("chain_boundary_exposure/d5_reconciliation/"
     "degenerate_column_speed_ceiling_kmh", "{:.2f} km/h",
     "m2 degenerate column speed ceiling"),
    # KX-m6: the corrected ledger rows
    *[(f"heat_ledger_ws6/series_duty_v2_{c}_cycle_average/"
       "engine_rejection_avg_kW", "**{:.4f}**", f"m6 ledger row {c}")
      for c in ("nominal", "cda_5.4", "alt2000m_45C")],
    # KX-m7: transient heat vs R20
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "r20_design_point_radiator_package_kW", "**{:.1f} kW**",
     "m7 R20 design point"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/cases/"
     "alt2000m_45C/radiator_package_2min_max_kW", "**{:.1f} kW**",
     "m7 corner 2-min radiator"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/cases/"
     "alt2000m_45C/radiator_package_peak_kW", "**{:.1f} kW**",
     "m7 corner peak radiator"),
    # KX-m6: the superseded r1 rows, rendered from the historical literal
    *[(f"heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
       f"engine_rejection_avg_kW/{k}", "{:.4f} \u2192", f"m6 r1 row {k}")
      for k in ("nominal", "cda_5_4", "alt2000m_45C")],
    # KX-M1 bracket
    ("series_duty_v2/engine_continuous_rating_bracket/soc_min_worst",
     "**{:.3f}**", "M1 bracket SOC min"),
    ("series_duty_v2/engine_continuous_rating_bracket/"
     "fuel_delta_pct_paired_worst_max", "worst paired seed {:+.3f} %",
     "KX2-M3(c) bracket paired worst fuel delta"),
    # KX-m4: R34
    ("series_duty_v2/_trace_files/traces_emitted_n", "{:.0f} traces",
     "m4 traces emitted"),
    ("series_duty_v2/_trace_files/ordered_mode_b_runs", "{:.0f} ordered",
     "m4 ordered runs"),
    # =====================================================================
    # KX r3 headline renderings (rework against FINDINGS_KX_r2.md)
    # =====================================================================
    # KX2-M2: the pack quantity has no crossing, only a least-bad point
    ("series_duty_v2/r16_binding_analysis/pack_quantity_binding_analysis/"
     "acceptance_curve_max_kW_bus", "**{:.3f} kW bus", "KX2-M2 curve max"),
    ("series_duty_v2/r16_binding_analysis/pack_quantity_binding_analysis/"
     "peak_pack_charge_kW_bus", "**{:.3f} kW**", "KX2-M2 peak pack charge"),
    ("series_duty_v2/r16_binding_analysis/pack_quantity_binding_analysis/"
     "min_exceedance_kW_over_the_curve", "**{:.3f} kW**",
     "KX2-M2 minimum exceedance over the curve"),
    ("series_duty_v2/r16_binding_analysis/pack_quantity_binding_analysis/"
     "n_tabulated_cells", "every one of the {:.0f} tabulated cell",
     "KX2-M2 tabulated cell count"),
    # KX2-M1: the absolute comparison over the whole enumerated set
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "absolute_kW_comparison/worst_2min_kW", "**{:.3f} kW**",
     "KX2-M1 worst 2-min radiator package"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "absolute_kW_comparison/exceedance_pct_of_design_point_worst",
     "**{:+.1f} %**", "KX2-M1 exceedance over the design point"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "ambient_normalised_sensitivity/break_even_top_tank_C",
     "**{:.0f} °C** top tank", "KX2-M1 declared-ITD break-even top tank"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "ambient_normalised_sensitivity/design_case_crossover_top_tank_C",
     "**{:.1f} °C**", "KX2-M1 declared-ITD design-case crossover"),
    ("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point/"
     "ambient_normalised_sensitivity/case_air_temperature_C/alt2000m_45C",
     "**{:.2f} °C**", "KX2-M1 derived corner air temperature"),
    # KX2-M3: the paired per-seed fuel deltas
    ("series_duty_v2/companion_bp_capability_comparison/fuel_delta_paired/"
     "by_case/nominal/median", "median **{:+.3f} %**",
     "KX2-M3(a) companion paired median at nominal"),
    ("series_duty_v2/companion_bp_capability_comparison/fuel_delta_paired/"
     "worst_max_pct", "**{:+.3f} %**",
     "KX2-M3(a) companion worst paired seed"),
    ("series_duty_v2/r16_pack_acceptance_bracket/fuel_delta_paired/by_case/"
     "nominal/seeds_positive_n", "{:.0f} of 8 seeds at nominal",
     "KX2-M3(b) nominal seeds where enforcement costs fuel"),
    # KX2-m4: the R6 rating-family probe
    ("series_duty_v2/r6_rating_family_probe/r6_family_worst_over_rating_s",
     "**{:.1f} s/cycle**", "KX2-m4 R6-family worst over-rating"),
    ("series_duty_v2/r6_rating_family_probe/union_worst_over_rating_s",
     "**{:.1f} s/cycle**", "KX2-m4 union worst over-rating"),
    ("series_duty_v2/r6_rating_family_probe/ordered_set_worst_over_rating_s",
     "the ordered set's {:.1f} s", "KX2-m4 ordered-set worst over-rating"),
    ("series_duty_v2/r6_rating_family_probe/worst_unserved_kWh",
     "{:.4f} kWh unserved", "KX2-m4 probe unserved"),
    # the sweep's own counts
    ("construction_sweep_kx_r3/counts/fields_corrected", "**{:.0f}** fields",
     "sweep fields corrected"),
    ("construction_sweep_kx_r3/counts/areas_examined_clean",
     "**{:.0f}** areas were examined", "sweep clean areas"),
    ("series_duty_v2/r22d_coast_spin_member/unbooked_pp_max",
     "**{:.6f}** pp", "sweep r22d corrected unbooked pp"),
    ("series_duty_v2/r22d_coast_spin_member/"
     "unbooked_pp_of_cycle_fuel_ratio_of_ensemble_extrema_kx_r2/"
     "alt2000m_45C", "{:.6f} →", "sweep r22d superseded unbooked pp"),
    ("series_duty_v2/companion_bp_capability_comparison/"
     "engine_shaft_peak_pct_of_continuous_rating_worst", "= {:.0f} %",
     "sweep engine peak percent of its own rating"),
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

# ===========================================================================
# KX structural pins. The r3 defect class was a HAND-TRANSCRIBED current
# number corrected in three places out of four, and an interface path that
# resolved against nobody's folder. A rendering check cannot catch either,
# so these are counted and resolved, not merely matched.
# ===========================================================================
STRUCT = len(CHECKS) + 1
FLAT = " ".join(REPORT.split())          # whitespace-collapsed report


def _flat(s):
    return " ".join(s.split())


# --- R23/F1: the corrected phrase must appear in ALL FOUR places the
# adjudicator named (headline, s0-R, s6 table, ESC-2), and no superseded
# wording may survive anywhere.
_n_pos = get("gate_g1/cda_5.4/ensemble/seeds_margin_positive_n")
_phrase = _flat(f"{_n_pos:.0f} of 8 seeds marginally positive")
_occ = FLAT.count(_phrase)
STRUCT += 1
if _occ != 4:
    fails.append(f"  F1 OCCURRENCE PIN: '{_phrase}' appears {_occ} times, "
                 "expected 4 (headline, s0-R, s6 table, ESC-2) - a partial "
                 "correction is exactly the r3 defect")
_SUPERSEDED = {
    "F1": ["two seeds marginally positive", "two marginally positive seeds",
           "two of eight seeds marginally positive"],
    "F2": ["so the convention is mode-neutral and negligible",
           "mode-neutral and negligible, ~seconds per cycle",
           "the convention is mode-neutral and negligible"],
    "F3": ["the spread is under 0.6 pp"],
}
for _fid, _bad_list in _SUPERSEDED.items():
    for _bad in _bad_list:
        STRUCT += 1
        if _flat(_bad) in FLAT:
            fails.append(f"  {_fid} SUPERSEDED WORDING still present: "
                         f"'{_bad}'")

# --- R23/F4: EVERY file path exported by the interface must resolve
# against THIS workstream's folder (the one exception is the field
# explicitly labelled as the owner's own relative path).
_FILE_KEYS_EXTRA = {"trace_10Hz", "soc_trajectories"}
_OWNER_RELATIVE = {"map_file_as_exported_by_owner"}


def _is_hash(v):
    return len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _walk_files(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if "sha256" in k:
                continue                     # hash tables, not file fields
            if (isinstance(v, str) and k not in _OWNER_RELATIVE
                    and not _is_hash(v)
                    and (k.endswith("_file") or k in _FILE_KEYS_EXTRA)):
                yield f"{path}/{k}", v
            else:
                yield from _walk_files(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_files(v, f"{path}/{i}")


_seen_files = 0
for _jp, _fp in _walk_files(R["interface_ws4"], "interface_ws4"):
    _seen_files += 1
    STRUCT += 1
    if not os.path.exists(os.path.join(HERE, _fp)):
        fails.append(f"  F4 PATH PIN: {_jp} = '{_fp}' does not resolve "
                     "against the WS4 folder (every interface *_file must)")
if _seen_files < 8:
    fails.append(f"  F4 PATH PIN: only {_seen_files} interface file fields "
                 "found - the walker is not seeing the block")

# --- KX item 3: the archived gate must be labelled as archived and must
# not be presented as a live requirement.
STRUCT += 1
if get("interface_ws4/gate_g1/status") != "executed_kill_2026-08-30":
    fails.append("  ARCHIVAL PIN: interface_ws4 -> gate_g1 -> status is not "
                 "executed_kill_2026-08-30")
STRUCT += 1
if "NO FIELD OF THIS BLOCK MAY BE CONSUMED AS A LIVE REQUIREMENT" not in \
        get("interface_ws4/gate_g1/_archival_notice"):
    fails.append("  ARCHIVAL PIN: the gate_g1 archival notice is missing its "
                 "no-live-consumption clause")
STRUCT += 1
for _member in ("verdict", "attribution_rows", "bracket_result",
                "provenance_hashes"):
    if _member not in R["interface_ws4"]["gate_g1"]:
        fails.append(f"  ARCHIVAL PIN: gate_g1 is missing the '{_member}' "
                     "member the KX directive names")
STRUCT += 1
if "spin_drag_operational_note_r22d" not in R["interface_ws4"]:
    fails.append("  R22d PIN: the spin-drag operational note is not a named "
                 "interface member")

# --- KX item 2: the ordered per-seed export set must actually be present
# for every seed of every ordered case.
_ORDERED = ("unserved_bus_kWh", "above_pin_demand_s", "above_pin_engine_s",
            "soc_min", "soc_max", "soc_end", "genset_starts",
            "genset_starts_per_h", "above_pin_transitions_per_h",
            "fuel_energy_kWh_per_km")
for _c, _cb in R["interface_ws4"]["series_duty_v2"]["cases"].items():
    _ps = _cb["per_seed_ordered_exports"]
    STRUCT += 1
    if len(_ps) != 8:
        fails.append(f"  R22a EXPORT PIN: case {_c} exports {len(_ps)} "
                     "seeds, expected 8 (R9)")
    for _sd, _row in _ps.items():
        for _k in _ORDERED:
            STRUCT += 1
            if _k not in _row:
                fails.append(f"  R22a EXPORT PIN: {_c}/seed {_sd} is "
                             f"missing the ordered export '{_k}'")

# --- R9/R14: every exported extremum in the R22a envelopes carries its
# governing case inline.
for _c, _cb in R["interface_ws4"]["series_duty_v2"]["cases"].items():
    for _k in list(_cb["ensemble"]):
        if _k.endswith("_min") or _k.endswith("_max"):
            STRUCT += 1
            if _k + "_governing_case" not in _cb["ensemble"]:
                fails.append(f"  R14 PIN: {_c}/{_k} has no inline "
                             "governing-case label")

# ===========================================================================
# KX r2 STRUCTURAL PINS (rework against FINDINGS_KX_r1.md). Each of these
# guards the ROOT CAUSE of one finding, not its rendering - so the defect
# cannot come back through a different door.
# ===========================================================================

# --- m5: the F1 phrase must appear in all four PLACES, not merely four
# times. The r1 pin counted occurrences; a count is not a place check, and
# the r3 failure mode was a correction landing in three of four PLACES.
_SEC_BOUNDS = [("headline", "\n## 0-KX2."),
               ("s0-R", "\n## 0-R.", "\n## 0."),
               ("s6", "\n## 6.", "\n## 7."),
               ("s12-ESC", "\n## 12.", "\n## 13.")]


def _slice(name):
    if name == "headline":
        return REPORT[:REPORT.index("\n## 0-KX2.")]
    for row in _SEC_BOUNDS:
        if row[0] == name:
            a = REPORT.index(row[1])
            b = REPORT.index(row[2], a + 1)
            return REPORT[a:b]
    raise KeyError(name)


for _sec in ("headline", "s0-R", "s6", "s12-ESC"):
    STRUCT += 1
    _n = _flat(_slice(_sec)).count(_phrase)
    if _n != 1:
        fails.append(f"  m5 SECTION PIN: the F1 phrase '{_phrase}' occurs "
                     f"{_n} times in the {_sec} slice, expected exactly 1 - "
                     "a count is not a place check (adjudication KX-m5)")
STRUCT += 1
if _flat("corrected in the headline, \u00a76, ESC-2 and ESC-6") in FLAT:
    fails.append("  m5 SUPERSEDED WORDING: \u00a70-R still names ESC-6 as an "
                 "F1 location; ESC-6 carries no seed count")

# --- M2: the LIVE block must resolve its own chain of record WITHOUT
# reading the archived gate_g1 block. This is the F4 defect class,
# reintroduced by the archival restructure; a path pin cannot catch a
# field that is ABSENT from the block that needs it.
_LIVE = R["interface_ws4"]["series_duty_v2"]
STRUCT += 1
if "chain_of_record" not in _LIVE["_inputs"]:
    fails.append("  M2 PIN: series_duty_v2 -> _inputs has no "
                 "chain_of_record - the live block cannot resolve the "
                 "chain its numbers were produced with")
else:
    _cor = _LIVE["_inputs"]["chain_of_record"]
    for _k in ("map_file", "map_voltage_V", "reduction_flat",
               "ws2_rework_round", "map_file_sha256"):
        STRUCT += 1
        if _k not in _cor:
            fails.append(f"  M2 PIN: chain_of_record is missing '{_k}'")
    STRUCT += 1
    if not os.path.exists(os.path.join(HERE, _cor["map_file"])):
        fails.append("  M2 PIN: chain_of_record -> map_file does not "
                     "resolve against the WS4 folder")
    STRUCT += 1
    if _cor["map_file"] != get("interface_ws4/gate_g1/"
                               "traction_chain_of_record/map_file"):
        fails.append("  M2 PIN: the live chain_of_record and the archived "
                     "one disagree on map_file - same run, same map")
STRUCT += 1
if "boundary_convention_exposure" not in _LIVE["_inputs"]:
    fails.append("  M2 PIN: the boundary-convention exposure is exported "
                 "only inside the archived gate_g1 block")
else:
    for _c in ("nominal", "cda_5.4", "alt2000m_45C"):
        STRUCT += 1
        if _c not in _LIVE["_inputs"]["boundary_convention_exposure"]["cases"]:
            fails.append(f"  M2 PIN: live boundary exposure missing case "
                         f"{_c}")

# --- B1: the misleading field must be gone under its old name, both
# readings must be exported, and the pack reading must be MEASURED.
_R16 = _LIVE["r16_binding_analysis"]
STRUCT += 1
if "bound_any_sample" in _R16:
    fails.append("  B1 PIN: 'bound_any_sample' still present unqualified - "
                 "it answers the regen-leg question and reads as answering "
                 "the pack question (adjudication KX-B1)")
for _k in ("regen_leg_bound_any_sample", "pack_charge_bound_by_r16_any_sample",
           "pack_charge_above_r16_accept_s", "pack_charge_above_r16_accept_kWh",
           "pack_charge_above_r16_accept_longest_s", "peak_pack_charge_kW_bus",
           "pulse10s_kW_bus_at_declared_cells",
           "pulse10s_covers_the_excursions", "_two_readings"):
    STRUCT += 1
    if _k not in _R16:
        fails.append(f"  B1 PIN: r16_binding_analysis is missing '{_k}'")
STRUCT += 1
if _R16.get("pack_charge_bound_by_r16_any_sample") is not True:
    fails.append("  B1 PIN: the measured pack-charge exceedance is not "
                 "reported as binding, but the run charges above the curve")
# the pack exceedance must be non-zero on EVERY ordered case, or the
# finding's own evidence has silently vanished
for _c in ("nominal", "cda_5.4", "alt2000m_45C"):
    STRUCT += 1
    if _R16["pack_charge_above_r16_accept_s"]["per_case_min"][_c] <= 0.0:
        fails.append(f"  B1 PIN: pack charge above R16 acceptance is zero "
                     f"on some seed of {_c} - re-check the counter")
STRUCT += 1
if "r16_pack_acceptance_bracket" not in _LIVE:
    fails.append("  B1 PIN: the pack-reading bracket is not exported")

# --- B2: the companion must carry the capability axes, not only fuel.
for _c, _cb in _LIVE["cases"].items():
    for _k in ("pack_dis_peak_kW_max", "pack_chg_peak_kW_max",
               "pack_chg_above_r16_accept_s_max",
               "engine_over_continuous_rating_s_max",
               "engine_shaft_peak_kW_max"):
        STRUCT += 1
        if _k not in _cb["companion_bp_ensemble"]:
            fails.append(f"  B2 PIN: {_c}/companion_bp_ensemble is missing "
                         f"the capability export '{_k}' - the companion "
                         "exists to give R22b both endpoints on the SAME "
                         "axes")
STRUCT += 1
if "companion_bp_capability_comparison" not in _LIVE:
    fails.append("  B2 PIN: the (b) vs (b') capability comparison is not "
                 "exported")
else:
    for _ax, _row in _LIVE["companion_bp_capability_comparison"][
            "axes"].items():
        for _side in ("mode_b_block_of_record", "mode_bp_companion"):
            STRUCT += 1
            if "worst_case_max_governing_case" not in _row[_side]:
                fails.append(f"  B2/R14 PIN: axis {_ax}/{_side} has no "
                             "inline governing-case label")

# --- M1: the engine over-rating counters must exist for BOTH modes, and
# the ordered run must actually exceed the rating (the finding's evidence).
for _c, _cb in _LIVE["cases"].items():
    STRUCT += 1
    if "engine_over_continuous_rating_s_max" not in _cb["ensemble"]:
        fails.append(f"  M1 PIN: {_c} exports no engine over-rating counter")
STRUCT += 1
if "engine_continuous_rating_bracket" not in _LIVE:
    fails.append("  M1 PIN: the continuous-rating bracket is not exported")
elif not _LIVE["engine_continuous_rating_bracket"]["unserved_stays_zero"]:
    fails.append("  M1 PIN: the continuous-rating bracket no longer shows "
                 "zero unserved - the headline claim in s4-KX.3 is stale")

# --- M3: the payload denominator must travel with the JSON.
STRUCT += 1
if "payload_metric_basis" not in _LIVE["_inputs"]:
    fails.append("  M3 PIN: the payload-denominated metric is exported with "
                 "no denominator, basis or caveat in interface_ws4")
else:
    _pb = _LIVE["_inputs"]["payload_metric_basis"]
    for _k in ("payload_basis_t", "payload_basis_source", "_caveat"):
        STRUCT += 1
        if _k not in _pb:
            fails.append(f"  M3 PIN: payload_metric_basis missing '{_k}'")
    # the exported field must in fact BE per-km / payload_t, or the caveat
    # is wrong
    for _c, _cb in _LIVE["cases"].items():
        STRUCT += 1
        _lhs = _cb["ensemble"]["fuel_energy_kWh_per_payload_tonne_km_min"]
        _rhs = (_cb["ensemble"]["fuel_energy_kWh_per_km_min"]
                / _pb["payload_basis_t"])
        if abs(_lhs - _rhs) > 1e-12:
            fails.append(f"  M3 PIN: {_c} payload metric is not per-km / "
                         "payload_basis_t; the exported caveat is wrong")

# --- m3: the eight fields the adjudicator named must carry R14 labels.
_M3_LABELS = [
    ("interface_ws4/gate_g1/boundary_convention_exposure",
     "nominal_one_sided_pp_max"),
    ("interface_ws4/gate_g1/chain_weighting_convention/series_duty_weighted",
     "eta_bus_to_wheel_max"),
    ("interface_ws4/gate_g1/verdict", "margin_pct_ensemble_max"),
    ("interface_ws4/series_duty_v2/r22d_coast_spin_member",
     "coast_no_regen_s_max"),
    ("interface_ws4/series_duty_v2/r22d_coast_spin_member",
     "coast_spin_shaft_kWh_max"),
    ("interface_ws4/series_duty_v2/r22d_coast_spin_member",
     "coast_spin_bus_kWh_max"),
    ("interface_ws4/spin_drag_operational_note_r22d/"
     "measured_on_series_duty_v2", "coast_no_regen_s_max"),
    ("interface_ws4/spin_drag_operational_note_r22d/"
     "measured_on_series_duty_v2", "coast_spin_shaft_kWh_max"),
    ("interface_ws4/spin_drag_operational_note_r22d/"
     "measured_on_series_duty_v2", "coast_spin_bus_kWh_max"),
    ("interface_ws4/gate_g1/attribution_rows/spin_drag_alone",
     "delta_pp_min"),
    ("interface_ws4/gate_g1/attribution_rows/map_vs_scalar_alone",
     "delta_pp_min"),
    ("interface_ws4/gate_g1/attribution_rows/both_g1r", "delta_pp_min"),
]
for _blk, _fld in _M3_LABELS:
    STRUCT += 1
    _o = get(_blk)
    if _fld not in _o:
        fails.append(f"  m3 PIN: {_blk}/{_fld} is absent")
    elif _fld + "_governing_case" not in _o:
        fails.append(f"  m3/R14 PIN: {_blk}/{_fld} carries no inline "
                     "governing-case label")

# --- m6: each ledger row must be the MAX OF THE PER-SEED CYCLE AVERAGES,
# recomputed here from per_seed - not max(energy) / one seed's duration.
for _c in ("nominal", "cda_5.4", "alt2000m_45C"):
    _row = get(f"heat_ledger_ws6/series_duty_v2_{_c}_cycle_average")
    _ps = get(f"series_duty_v2/cases/{_c}/per_seed")
    for _rk, _ek in (("engine_rejection_avg_kW", "engine_reject_kWh"),
                     ("generator_loss_avg_kW", "generator_loss_kWh"),
                     ("electric_chain_loss_avg_kW", "chain_loss_kWh")):
        STRUCT += 1
        _want = max(v[_ek] / (v["duration_s"] / 3600.0)
                    for v in _ps.values())
        if abs(_row[_rk] - _want) > 1e-9:
            fails.append(f"  m6 PIN: heat row {_c}/{_rk} = {_row[_rk]:.6f} "
                         f"is not the max of the per-seed cycle averages "
                         f"({_want:.6f})")
        STRUCT += 1
        if _rk + "_governing_case" not in _row:
            fails.append(f"  m6/R14 PIN: heat row {_c}/{_rk} carries no "
                         "component-specific governing case")

# --- m7: the transient rows must be present and >= the cycle mean.
for _c in ("nominal", "cda_5.4", "alt2000m_45C"):
    _row = get(f"heat_ledger_ws6/series_duty_v2_{_c}_cycle_average")
    for _k in ("engine_rejection_peak_kW", "engine_rejection_2min_max_kW",
               "engine_rejection_10min_max_kW"):
        STRUCT += 1
        if _k not in _row:
            fails.append(f"  m7 PIN: heat row {_c} has no '{_k}' - program "
                         "rule 7 asks for heat by component AND CASE, and a "
                         "cycle mean is not the case")
    STRUCT += 1
    if not (_row["engine_rejection_peak_kW"]
            >= _row["engine_rejection_2min_max_kW"]
            >= _row["engine_rejection_10min_max_kW"]
            >= _row["engine_rejection_avg_kW"]):
        fails.append(f"  m7 PIN: heat row {_c} rolling windows are not "
                     "monotone peak >= 2min >= 10min >= mean")

# --- m8: the hysteresis sensitivity must be an 8-seed ensemble (R9), and
# the r1 reference-seed rows must still be there.
STRUCT += 1
if "hysteresis_sensitivity_ref_seed" in _LIVE:
    fails.append("  m8 PIN: the block is still named "
                 "hysteresis_sensitivity_ref_seed but is no longer a "
                 "reference-seed quantity")
STRUCT += 1
if "hysteresis_sensitivity" not in _LIVE:
    fails.append("  m8 PIN: hysteresis_sensitivity is absent")
else:
    for _c, _cb in _LIVE["hysteresis_sensitivity"]["cases"].items():
        STRUCT += 1
        if "ref_seed" not in _cb:
            fails.append(f"  m8 PIN: {_c} dropped the r1 reference-seed rows")
        STRUCT += 1
        if "genset_starts_min" not in _cb["ws3_band_ensemble"]:
            fails.append(f"  m8/R9 PIN: {_c}/ws3_band has no 8-seed envelope")
    for _c in ("nominal", "cda_5.4", "alt2000m_45C"):
        STRUCT += 1
        _n = len(get(f"series_duty_v2/hysteresis_sensitivity/cases/{_c}/"
                     "ws3_band/per_seed"))
        if _n != 8:
            fails.append(f"  m8/R9 PIN: {_c}/ws3_band ran {_n} seeds, "
                         "expected 8")

# --- R34: the 10 Hz trace must exist and actually be at 10 Hz.
STRUCT += 1
_tr = os.path.join(HERE, get("series_duty_v2/_trace_files/trace_10Hz"))
if not os.path.exists(_tr):
    fails.append("  R34 PIN: the 10 Hz trace file is missing")
else:
    with open(_tr) as _f:
        _rows = [ln for ln in _f if not ln.startswith("#")]
    STRUCT += 1
    if len(_rows) - 1 != int(get("series_duty_v2/_trace_files/"
                                 "trace_10Hz_rows")):
        fails.append("  R34 PIN: trace row count does not match the "
                     "exported trace_10Hz_rows")
    _t0 = float(_rows[1].split(",")[0])
    _t1 = float(_rows[2].split(",")[0])
    STRUCT += 1
    if abs((_t1 - _t0) - 0.1) > 1e-9:
        fails.append(f"  R34 PIN: trace step is {_t1-_t0:.4f} s, not 0.1 s")

# ===========================================================================
# KX r3 STRUCTURAL PINS (rework against FINDINGS_KX_r2.md).
#
# The r2 defect family was: a machine-readable summary whose CONSTRUCTION
# does not match its NAME. A rendering pin cannot catch that - the
# rendering of a wrong construction is faithful. So each pin below
# RE-DERIVES the quantity from the per-seed data and compares, or asserts
# that the misnamed field is gone under its old name.
# ===========================================================================
_KXC = ("nominal", "cda_5.4", "alt2000m_45C")

# --- KX2-M3: every paired fuel delta must BE the paired per-seed delta,
# re-derived here from per_seed. This is the R36 guard.
_PAIRED_SPECS = [
    ("companion (b')",
     "series_duty_v2/companion_bp_capability_comparison/fuel_delta_paired",
     lambda c: get(f"series_duty_v2/cases/{c}/companion_bp/per_seed"),
     lambda c: get(f"series_duty_v2/cases/{c}/per_seed")),
    ("R16 pack bracket",
     "series_duty_v2/r16_pack_acceptance_bracket/fuel_delta_paired",
     lambda c: get(f"series_duty_v2/r16_pack_acceptance_bracket/cases/{c}/"
                   "per_seed"),
     lambda c: get(f"series_duty_v2/cases/{c}/per_seed")),
    ("engine-rating bracket",
     "series_duty_v2/engine_continuous_rating_bracket/fuel_delta_paired",
     lambda c: get(f"series_duty_v2/engine_continuous_rating_bracket/cases/"
                   f"{c}/per_seed"),
     lambda c: get(f"series_duty_v2/cases/{c}/per_seed")),
]
for _name, _path, _altf, _basef in _PAIRED_SPECS:
    _blk = get(_path)
    for _c in _KXC:
        _alt, _base = _altf(_c), _basef(_c)
        _d = sorted(100.0 * (_alt[k]["fuel_energy_kWh_per_km"]
                             - _base[k]["fuel_energy_kWh_per_km"])
                    / _base[k]["fuel_energy_kWh_per_km"] for k in _base)
        _med = (_d[len(_d) // 2 - 1] + _d[len(_d) // 2]) / 2.0
        for _stat, _want in (("min", _d[0]), ("max", _d[-1]),
                             ("median", _med)):
            STRUCT += 1
            if abs(_blk["by_case"][_c][_stat] - _want) > 1e-12:
                fails.append(
                    f"  KX2-M3 PIN: {_name}/{_c} exported {_stat} "
                    f"{_blk['by_case'][_c][_stat]!r}, but the PAIRED "
                    f"per-seed delta re-derived from per_seed is {_want!r}. "
                    "R36 requires the paired statistic, not a ratio of "
                    "ensemble statistics.")
        STRUCT += 1
        if _blk["by_case"][_c]["seeds_positive_n"] != sum(
                1 for v in _d if v > 0.0):
            fails.append(f"  KX2-M3 PIN: {_name}/{_c} seeds_positive_n "
                         "does not match the paired deltas")
    # the exported "worst" must be a genuine bound over the whole set
    _allmax = max(_blk["by_case"][c]["max"] for c in _KXC)
    STRUCT += 1
    if abs(_blk["worst_max_pct"] - _allmax) > 1e-12:
        fails.append(f"  KX2-M3 PIN: {_name} worst_max_pct is not the max "
                     "over the enumerated case set")
    STRUCT += 1
    if "; within it, seed" not in _blk["worst_max_pct_governing_case"] and \
            "tied at" not in _blk["worst_max_pct_governing_case"]:
        fails.append(f"  KX2-M3/R14 PIN: {_name} worst_max_pct carries no "
                     "case+seed governing label")
# the misnamed r2 fields must be gone under their old names
for _p, _f in (("series_duty_v2/r16_pack_acceptance_bracket",
                "fuel_penalty_pct_max"),
               ("series_duty_v2/engine_continuous_rating_bracket",
                "fuel_penalty_pct_max"),
               ("series_duty_v2/r16_pack_acceptance_bracket",
                "fuel_penalty_pct_vs_ordered"),
               ("series_duty_v2/engine_continuous_rating_bracket",
                "fuel_penalty_pct_vs_ordered")):
    STRUCT += 1
    if _f in get(_p):
        fails.append(f"  KX2-M3 PIN: {_p}/{_f} is a ratio of ensemble "
                     "maxima and must not stand under a name that says "
                     "'penalty'/'max' (adjudication KX2-M3)")
for _c in _KXC:
    STRUCT += 1
    if "bp_penalty_pct_on_median" in get(
            "series_duty_v2/companion_bp_capability_comparison/"
            f"fuel_kWh_per_km_by_case/{_c}"):
        fails.append("  KX2-M3 PIN: bp_penalty_pct_on_median is a ratio of "
                     "ensemble medians and must not stand under a name the "
                     "report renders as 'the paired per-case median'")
STRUCT += 1
if "paired per-case median" in FLAT and \
        get("series_duty_v2/companion_bp_capability_comparison/"
            "fuel_delta_paired/_statistic")[:6] != "PAIRED":
    fails.append("  KX2-M3 PIN: the report claims a paired per-case median "
                 "but the exported statistic does not declare itself paired")

# --- KX2-M2: a clamp and a crossing must not share a field name.
STRUCT += 1
if "cold_side_binding_cell_C_pack_quantity" in _R16:
    fails.append("  KX2-M2 PIN: cold_side_binding_cell_C_pack_quantity is "
                 "an np.interp right-edge clamp, not a crossing, and must "
                 "not stand beside two genuine crossings")
STRUCT += 1
if "pack_quantity_binding_analysis" not in _R16:
    fails.append("  KX2-M2 PIN: the measured pack-quantity statement is not "
                 "exported")
else:
    _PKB = _R16["pack_quantity_binding_analysis"]
    # re-derive from WS3's CSV directly, not from WS4's loader
    _r16csv = os.path.join(HERE, "..", "WS3_battery", "regen_acceptance.csv")
    _rows = [ln.strip().split(",") for ln in open(_r16csv)
             if ln.strip() and not ln.startswith("#")]
    _hdr = _rows[0]
    _ti, _pi = _hdr.index("T_cell_C"), _hdr.index("V2pack_chg_cont_kW_bus")
    _T = [float(r[_ti]) for r in _rows[1:]]
    _P = [float(r[_pi]) for r in _rows[1:]]
    STRUCT += 1
    if _PKB["n_tabulated_cells"] != len(_T):
        fails.append("  KX2-M2 PIN: n_tabulated_cells disagrees with WS3's "
                     "own curve")
    STRUCT += 1
    if abs(_PKB["acceptance_curve_max_kW_bus"] - max(_P)) > 1e-12:
        fails.append("  KX2-M2 PIN: acceptance_curve_max_kW_bus is not the "
                     "maximum of WS3's continuous column")
    STRUCT += 1
    _pk = _PKB["peak_pack_charge_kW_bus"]
    if abs(_PKB["min_exceedance_kW_over_the_curve"]
           - (_pk - max(_P))) > 1e-12:
        fails.append("  KX2-M2 PIN: min_exceedance_kW_over_the_curve is not "
                     "peak - max(curve)")
    STRUCT += 1
    if _PKB["exceeds_acceptance_at_every_tabulated_cell_C"] != all(
            _pk > v for v in _P):
        fails.append("  KX2-M2 PIN: the every-cell statement disagrees with "
                     "WS3's curve")
    STRUCT += 1
    if _PKB["cold_side_crossing_exists"] or _PKB["hot_side_crossing_exists"]:
        fails.append("  KX2-M2 PIN: a crossing is claimed on the pack "
                     "quantity where none exists")
# the two genuine regen-leg crossings must still be genuine (in range)
for _k in ("cold_side_binding_cell_C", "hot_side_binding_cell_C"):
    STRUCT += 1
    if _R16.get(_k) is None:
        fails.append(f"  KX2-M2 PIN: {_k} is None - the in-range assertion "
                     "fired, so the field must be replaced by a measured "
                     "statement rather than left null")

# --- KX2-M1: the R20 verdict must be a max/min over the SAME enumerated
# set as the worst it sits beside.
_TR = get("heat_ledger_ws6/series_duty_v2_transient_vs_R20_design_point")
STRUCT += 1
if "r20_survives_on_the_2min_window" in _TR:
    fails.append("  KX2-M1 PIN: r20_survives_on_the_2min_window was a max "
                 "over ONE case written as a set-wide verdict and must not "
                 "stand under that name")
STRUCT += 1
if "absolute_kW_comparison" not in _TR:
    fails.append("  KX2-M1 PIN: the absolute comparison over the enumerated "
                 "set is not exported")
else:
    _AB = _TR["absolute_kW_comparison"]
    _design = _TR["r20_design_point_radiator_package_kW"]
    _w = max(_TR["cases"][c]["radiator_package_2min_max_kW"] for c in _KXC)
    STRUCT += 1
    if abs(_AB["worst_2min_kW"] - _w) > 1e-12:
        fails.append("  KX2-M1 PIN: worst_2min_kW is not the max over the "
                     "enumerated ordered case set")
    _exc = [c for c in _KXC
            if _TR["cases"][c]["radiator_package_2min_max_kW"] > _design]
    STRUCT += 1
    if _AB["cases_exceeding_design_point_on_2min"] != _exc:
        fails.append("  KX2-M1 PIN: cases_exceeding_design_point_on_2min "
                     f"is {_AB['cases_exceeding_design_point_on_2min']}, "
                     f"re-derived {_exc}")
    STRUCT += 1
    if _AB["all_ordered_cases_within_design_point_on_2min"] != (not _exc):
        fails.append("  KX2-M1 PIN: the set-wide verdict disagrees with its "
                     "own enumerated exceedance list")
    STRUCT += 1
    if len(_AB["worst_2min_tied_cases_within_1e_6_kW"]) < 1:
        fails.append("  KX2-M1 PIN: the tie disclosure is empty")
STRUCT += 1
if "r20_survives_on_the_2min_window_at_alt2000m_45C_only" not in _TR:
    fails.append("  KX2-M1 PIN: the scope-named single-case statement is "
                 "absent")
STRUCT += 1
if _TR["ambient_normalised_sensitivity"]["_status"][:16] != \
        "[WS4-DECLARED SE":
    fails.append("  KX2-M1 PIN: the ambient sensitivity is not labelled as "
                 "a WS4-DECLARED sensitivity")
# the crossover must sit above every case ambient and be the FIRST one
_AMB = _TR["ambient_normalised_sensitivity"]
STRUCT += 1
if _AMB.get("design_case_crossover_top_tank_C") is None:
    fails.append("  KX2-M1 PIN: the ambient sensitivity answers the "
                 "capability question but not R20's own question - which "
                 "case governs; export design_case_crossover_top_tank_C")
else:
    STRUCT += 1
    if _AMB["design_case_crossover_top_tank_C"] <= max(
            _AMB["case_air_temperature_C"].values()):
        fails.append("  KX2-M1 PIN: the design-case crossover is below the "
                     "hottest case ambient - the ITD model is not valid "
                     "there")
    STRUCT += 1
    if _AMB["design_case_crossover_top_tank_C"] != min(
            d["top_tank_C"] for d in _AMB["design_case_crossovers"]):
        fails.append("  KX2-M1 PIN: the reported crossover is not the "
                     "lowest one in the enumerated crossover set")
STRUCT += 1
if "ESC-12" not in _TR["escalation"]:
    fails.append("  KX2-M1 PIN: the R20 question is not escalated")
STRUCT += 1
if "ESC-12" not in REPORT:
    fails.append("  KX2-M1 PIN: ESC-12 is not raised in the report")

# --- KX2-m1: no governing-case label anywhere in the live block may be a
# bare case name, and an all-equal set must refuse to name one.
_DEGEN = get("series_duty_v2/unserved_energy_verdict/"
             "worst_case_governing_case")


def _walk_gov(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.endswith("_governing_case") and isinstance(v, str):
                yield f"{path}/{k}", v
            else:
                yield from _walk_gov(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_gov(v, f"{path}/{i}")


_bare = 0
for _jp, _lbl in _walk_gov(R["interface_ws4"]["series_duty_v2"],
                           "series_duty_v2"):
    STRUCT += 1
    if _lbl in _KXC:
        _bare += 1
        fails.append(f"  KX2-m1/R14 PIN: {_jp} = '{_lbl}' is a bare case "
                     "name; R14 asks for the enumerated set and the "
                     "governing seed inline")
for _blk in ("r16_pack_acceptance_bracket", "engine_continuous_rating_bracket"):
    _b = get(f"series_duty_v2/{_blk}")
    STRUCT += 1
    if _b["worst_unserved_kWh"] == 0.0 and \
            _b["worst_unserved_governing_case"] != _DEGEN:
        fails.append(f"  KX2-m1 PIN: {_blk} labels an all-zero tie as "
                     f"'{_b['worst_unserved_governing_case']}' instead of "
                     "the degenerate-tie string")

# --- KX2-m2: the six named fields must carry R14 labels.
_M2R3 = [(f"series_duty_v2/_inputs/boundary_convention_exposure/cases/{c}",
          "exposure_s_motoring_min") for c in _KXC]
_M2R3 += [(f"heat_ledger_ws6/series_duty_v2_{c}_cycle_average", k)
          for c in _KXC
          for k in ("radiator_package_avg_kW", "radiator_package_peak_kW",
                    "radiator_package_2min_max_kW",
                    "radiator_package_10min_max_kW",
                    "pm_coast_spin_shaft_kWh_per_cycle",
                    "pm_coast_spin_bus_kWh_per_cycle")]
for _blk, _fld in _M2R3:
    STRUCT += 1
    _o = get(_blk)
    if _fld not in _o or _fld + "_governing_case" not in _o:
        fails.append(f"  KX2-m2/R14 PIN: {_blk}/{_fld} carries no inline "
                     "governing-case label")

# --- KX2-m3: the ARCHIVED raw reference-seed dump must be frozen to the
# member set of record and must not track the current simulator.
_G1_RAW_OF_RECORD = 53
for _case, _cb in R["gate_g1"].items():
    if not isinstance(_cb, dict) or "_raw_reference_seed" not in _cb:
        continue
    for _md, _row in _cb["_raw_reference_seed"].items():
        STRUCT += 1
        if len(_row) != _G1_RAW_OF_RECORD:
            fails.append(
                f"  KX2-m3 PIN: gate_g1/{_case}/_raw_reference_seed/{_md} "
                f"has {len(_row)} members, expected the frozen "
                f"{_G1_RAW_OF_RECORD} of record - an archived record that "
                "grows when the simulator gains a field is not archived")
        STRUCT += 1
        for _leak in ("eng_over_cont_s", "emerg_ceiling_kw",
                      "pack_chg_above_r16_s", "eng_reject_roll120s_max_kw"):
            if _leak in _row:
                fails.append(f"  KX2-m3 PIN: post-2026-08-30 diagnostic "
                             f"'{_leak}' has leaked into the archive at "
                             f"gate_g1/{_case}/_raw_reference_seed/{_md}")
STRUCT += 1
if "FROZEN MEMBER SET" not in get("interface_ws4/gate_g1/_archival_notice"):
    fails.append("  KX2-m3 PIN: the archival notice does not declare the "
                 "frozen member set")

# --- KX2-m4: ESC-10's exposure must be bounded by a set that includes
# R6's own rating family, and both set maxima must be exported.
STRUCT += 1
if "r6_rating_family_probe" not in _LIVE:
    fails.append("  KX2-m4 PIN: the R6 rating-family probe is not exported")
else:
    _R6 = _LIVE["r6_rating_family_probe"]
    _ens = _LIVE["r6_rating_family_probe_ensembles"]
    _fam = max(v["engine_over_continuous_rating_s_max"]
               for v in _ens.values())
    STRUCT += 1
    if abs(_R6["r6_family_worst_over_rating_s"] - _fam) > 1e-12:
        fails.append("  KX2-m4 PIN: r6_family_worst_over_rating_s is not "
                     "the max over the probe set")
    STRUCT += 1
    if abs(_R6["union_worst_over_rating_s"]
           - max(_fam, _R6["ordered_set_worst_over_rating_s"])) > 1e-12:
        fails.append("  KX2-m4 PIN: union_worst_over_rating_s is not the "
                     "max over the union of the two enumerated sets")
    STRUCT += 1
    if _R6["union_worst_over_rating_s"] < \
            _R6["ordered_set_worst_over_rating_s"]:
        fails.append("  KX2-m4 PIN: the union maximum is below the "
                     "ordered-set maximum, which is impossible")
    STRUCT += 1
    if len(_ens) != 4:
        fails.append(f"  KX2-m4 PIN: the probe exports {len(_ens)} cases, "
                     "expected 4")
    for _c, _v in _ens.items():
        STRUCT += 1
        if _v["unserved_bus_kWh_max"] > 1e-9:
            fails.append(f"  KX2-m4 PIN: probe case {_c} has nonzero "
                         "unserved energy - that is a finding, not a note")

# --- the sweep record itself must be present and self-consistent.
STRUCT += 1
if "construction_sweep_kx_r3" not in R["interface_ws4"]:
    fails.append("  SWEEP PIN: the construction sweep record is not in the "
                 "interface")
else:
    _SW = R["construction_sweep_kx_r3"]
    STRUCT += 1
    if _SW["counts"]["fields_corrected"] != len(_SW["corrected"]):
        fails.append("  SWEEP PIN: fields_corrected does not match the "
                     "corrected table")
    STRUCT += 1
    if _SW["counts"]["areas_examined_clean"] != len(_SW["examined_clean"]):
        fails.append("  SWEEP PIN: areas_examined_clean does not match the "
                     "clean table")
    STRUCT += 1
    if _SW["counts"]["named_in_findings"] + _SW["counts"][
            "found_by_the_sweep"] != _SW["counts"]["fields_corrected"]:
        fails.append("  SWEEP PIN: named + found does not equal corrected")

if fails:
    print(f"VERIFY FAILED ({len(fails)} of {STRUCT} checks):")
    print("\n".join(fails))
    sys.exit(1)
print(f"VERIFIED: {len(CHECKS)} headline renderings + interface block + "
      f"{STRUCT - len(CHECKS) - 1} structural/errata pins match "
      "results_ws4.json and the artefacts on disk.")
