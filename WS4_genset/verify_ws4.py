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

if fails:
    print(f"VERIFY FAILED ({len(fails)} of {STRUCT} checks):")
    print("\n".join(fails))
    sys.exit(1)
print(f"VERIFIED: {len(CHECKS)} headline renderings + interface block + "
      f"{STRUCT - len(CHECKS) - 1} structural/errata pins match "
      "results_ws4.json and the artefacts on disk.")
