#!/usr/bin/env python3
"""
Project Volt - WS4. Generates REPORT_WS4.md (G1-R revision).

The report body lives here as a template; the machine-readable interface
block AND every G1-R headline number are injected directly from
results_ws4.json (token substitution, no hand transcription), and
verify_ws4.py asserts the renderings against results_ws4.json.

    python3 run_ws4.py          # produce results_ws4.json
    python3 make_report_ws4.py  # produce REPORT_WS4.md
    python3 verify_ws4.py       # assert report == results, verbatim
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_ws4.json")))
IFACE = json.dumps(R["interface_ws4"], indent=1, default=float)


def g(path):
    o = R
    for k in path.split("/"):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


OF = R["gate_g1_one_factor"]
T = {
    "IFACE": IFACE,
    # G1-R nominal ensemble
    "MIN": f"{g('gate_g1/nominal/ensemble/margin_pct_min'):.2f}",
    "MED": f"{g('gate_g1/nominal/ensemble/margin_pct_median'):.2f}",
    "MAX": f"{g('gate_g1/nominal/ensemble/margin_pct_max'):.2f}",
    "GAP": f"{5.0 - g('gate_g1/nominal/ensemble/margin_pct_min'):.2f}",
    "GOV": g("gate_g1/nominal/ensemble/margin_pct_min_governing_case"),
    # prior anchor + one-factor rows
    "PMIN": f"{OF['prior_convention']['min']:.2f}",
    "PMED": f"{OF['prior_convention']['median']:.2f}",
    "PMAX": f"{OF['prior_convention']['max']:.2f}",
    "SPMIN": f"{OF['spin_drag_alone']['min']:.2f}",
    "SPMED": f"{OF['spin_drag_alone']['median']:.2f}",
    "SPDMIN": f"{OF['spin_drag_alone']['delta_pp_min']:+.2f}",
    "SPDMED": f"{OF['spin_drag_alone']['delta_pp_median']:+.2f}",
    "MPMIN": f"{OF['map_vs_scalar_alone']['min']:.2f}",
    "MPMED": f"{OF['map_vs_scalar_alone']['median']:.2f}",
    "MPDMIN": f"{OF['map_vs_scalar_alone']['delta_pp_min']:+.2f}",
    "MPDMED": f"{OF['map_vs_scalar_alone']['delta_pp_median']:+.2f}",
    "BODMIN": f"{OF['both_g1r']['delta_pp_min']:+.2f}",
    "BODMED": f"{OF['both_g1r']['delta_pp_median']:+.2f}",
    "INTMIN": f"{OF['both_g1r']['delta_pp_min'] - OF['spin_drag_alone']['delta_pp_min'] - OF['map_vs_scalar_alone']['delta_pp_min']:+.2f}",
    "INTMED": f"{OF['both_g1r']['delta_pp_median'] - OF['spin_drag_alone']['delta_pp_median'] - OF['map_vs_scalar_alone']['delta_pp_median']:+.2f}",
    # sensitivity conditions
    "CDAMIN": f"{g('gate_g1/cda_5.4/ensemble/margin_pct_min'):.2f}",
    "CDAMED": f"{g('gate_g1/cda_5.4/ensemble/margin_pct_median'):.2f}",
    "CDAMAX": f"{g('gate_g1/cda_5.4/ensemble/margin_pct_max'):.2f}",
    # genset-conditioning bracket + interim r3 record
    "BRMIN": f"{g('gate_g1_genset_conditioning_bracket/replacement_3pct_class/min'):.2f}",
    "BRMED": f"{g('gate_g1_genset_conditioning_bracket/replacement_3pct_class/median'):.2f}",
    "BSMIN": f"{g('gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/min'):.2f}",
    "BSMED": f"{g('gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/median'):.2f}",
    "BSMAX": f"{g('gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/max'):.2f}",
    "R3MIN": f"{g('gate_g1_interim_r3_vintage_record/margin_pct_min'):.2f}",
    "R3MED": f"{g('gate_g1_interim_r3_vintage_record/margin_pct_median'):.2f}",
    "R3MAX": f"{g('gate_g1_interim_r3_vintage_record/margin_pct_max'):.2f}",
    "BSGAP": f"{5.0 - g('gate_g1_genset_conditioning_bracket/stacked_declared_plus_3pct/min'):.2f}",
    "AUXMIN": f"{g('gate_g1/aux_4kW/ensemble/margin_pct_min'):.2f}",
    "AUXMED": f"{g('gate_g1/aux_4kW/ensemble/margin_pct_median'):.2f}",
    "HOTMIN": f"{g('gate_g1/hot_45C_sea_level/ensemble/margin_pct_min'):.2f}",
    "HOTMED":
        f"{g('gate_g1/hot_45C_sea_level/ensemble/margin_pct_median'):.2f}",
    "HOTMAX":
        f"{g('gate_g1/hot_45C_sea_level/ensemble/margin_pct_max'):.2f}",
    "ALTMIN": f"{g('gate_g1/alt2000m_45C/ensemble/margin_pct_min'):.2f}",
    "ALTMED": f"{g('gate_g1/alt2000m_45C/ensemble/margin_pct_median'):.2f}",
    "REFMIN": f"{g('gate_g1/reference_curve/ensemble/margin_pct_min'):.2f}",
    "REFMED":
        f"{g('gate_g1/reference_curve/ensemble/margin_pct_median'):.2f}",
    # map-vintage robustness (keys follow whatever WS2 exports)
    "VCPAIR": " and ".join(
        f"{v['min']:.2f}% ({k.replace('V', ' V')} map)"
        for k, v in sorted(R["gate_g1_map_vintage_check"].items())),
    # reference seed + secondary envelopes
    "AKG": f"{g('gate_g1/nominal/per_seed/23/a/fuel_kg'):.2f}",
    "BKG": f"{g('gate_g1/nominal/per_seed/23/b/fuel_kg'):.2f}",
    "AL100": f"{g('gate_g1/nominal/per_seed/23/a/l_per_100km'):.2f}",
    "BL100": f"{g('gate_g1/nominal/per_seed/23/b/l_per_100km'):.2f}",
    "ALOCK": f"{100*g('gate_g1/nominal/per_seed/23/a/locked_frac'):.1f}",
    "ASTARTS23": f"{g('gate_g1/nominal/per_seed/23/a/starts'):.0f}",
    "SYNC23":
        f"{g('gate_g1/nominal/_raw_reference_seed/a/sync_starts'):.0f}",
    "ASTMIN": f"{g('gate_g1/nominal/ensemble/a_starts_min'):.0f}",
    "ASTMAX": f"{g('gate_g1/nominal/ensemble/a_starts_max'):.0f}",
    "ABKMIN": f"{g('gate_g1/nominal/ensemble/a_bank_kwh_min'):.1f}",
    "ABKMAX": f"{g('gate_g1/nominal/ensemble/a_bank_kwh_max'):.1f}",
    "BEMMIN": f"{g('gate_g1/nominal/ensemble/b_emerg_s_min'):.0f}",
    "BEMMAX": f"{g('gate_g1/nominal/ensemble/b_emerg_s_max'):.0f}",
    "BEMCMIN": f"{g('gate_g1/cda_5.4/ensemble/b_emerg_s_min'):,.0f}",
    "BEMCMAX": f"{g('gate_g1/cda_5.4/ensemble/b_emerg_s_max'):,.0f}",
    "BUNMAX": f"{g('gate_g1/nominal/ensemble/b_unserved_kwh_max'):.2f}",
    "BUNCMIN": f"{g('gate_g1/cda_5.4/ensemble/b_unserved_kwh_min'):.2f}",
    "BUNCMAX": f"{g('gate_g1/cda_5.4/ensemble/b_unserved_kwh_max'):.2f}",
    "BORMIN": f"{g('gate_g1/nominal/ensemble/b_over_rating_s_min'):.1f}",
    "BORMAX": f"{g('gate_g1/nominal/ensemble/b_over_rating_s_max'):.1f}",
    "BORCMIN": f"{g('gate_g1/cda_5.4/ensemble/b_over_rating_s_min'):.1f}",
    "BORCMAX": f"{g('gate_g1/cda_5.4/ensemble/b_over_rating_s_max'):.1f}",
    "AORMAX": f"{g('gate_g1/nominal/ensemble/a_over_rating_s_max'):.1f}",
    "ASPSMIN": f"{g('gate_g1/nominal/ensemble/a_spin_shaft_kwh_min'):.3f}",
    "ASPSMAX": f"{g('gate_g1/nominal/ensemble/a_spin_shaft_kwh_max'):.3f}",
    "ASPBMIN": f"{g('gate_g1/nominal/ensemble/a_spin_bus_kwh_min'):.3f}",
    "ASPBMAX": f"{g('gate_g1/nominal/ensemble/a_spin_bus_kwh_max'):.3f}",
    # b' robustness
    "ABPLO": f"{min(g('gate_g1/bp_vs_b_pct/margin_a_vs_bp_pct')):.2f}",
    "ABPHI": f"{max(g('gate_g1/bp_vs_b_pct/margin_a_vs_bp_pct')):.2f}",
    "BBPLO": f"{min(g('gate_g1/bp_vs_b_pct/margin_b_vs_bp_pct')):.2f}",
    "BBPHI": f"{max(g('gate_g1/bp_vs_b_pct/margin_b_vs_bp_pct')):+.2f}",
    # chain of record / spin member
    "MAPFILE": g("ws2_chain_of_record/map_file"),
    "MAPV": f"{g('ws2_chain_of_record/map_voltage_V'):.0f}",
    "WS2ROUND": f"{g('ws2_chain_of_record/ws2_rework_round')}",
    "SPINSH":
        f"{g('ws2_chain_of_record/spin_drag_member/rate_shaft_kW_while_locked'):.3f}",
    "SPINBUS":
        f"{g('ws2_chain_of_record/spin_drag_member/rate_bus_kW_while_locked'):.3f}",
    "SPINESH":
        f"{g('ws2_chain_of_record/spin_drag_member/e_spin_shaft_kWh_per_VOLT_REG'):.4f}",
    "SPINEBUS":
        f"{g('ws2_chain_of_record/spin_drag_member/e_spin_bus_kWh_per_VOLT_REG'):.4f}",
    # sanity / effective rates
    "AWR": f"{g('gate_g1/nominal/per_seed/23/a/fuel_kg')*1e3/78.85:.0f}",
    "BWR": f"{g('gate_g1/nominal/per_seed/23/b/fuel_kg')*1e3/78.85:.0f}",
    "M23": f"{g('gate_g1/nominal/per_seed/23/margin_pct'):.1f}",
    "FTWR12": f"{g('sanity/series_fuel_to_wheel_g_per_kWh_R12'):.1f}",
    "FTWOLD": f"{g('sanity/series_fuel_to_wheel_g_per_kWh'):.0f}",
    "ETAR12":
        f"{g('sanity/eta_chain_bus_to_wheel_R12_energy_weighted'):.4f}",
    "BANKETA": f"{g('sanity/banking_redeploy_eta_R12'):.4f}",
    "ABSFCLO": (lambda v: f"{min(v):.1f}")(
        [g(f"gate_g1/nominal/per_seed/{s}/a/mean_bsfc_eff")
         for s in ("23", "3", "4", "5", "6", "7", "8", "9")]),
    "ABSFCHI": (lambda v: f"{max(v):.1f}")(
        [g(f"gate_g1/nominal/per_seed/{s}/a/mean_bsfc_eff")
         for s in ("23", "3", "4", "5", "6", "7", "8", "9")]),
    # heat ledger G1a
    "G1AREJ":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/engine_rejection_avg_kW'):.1f}",
    "G1AGEN":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/generator_loss_avg_kW'):.1f}",
    "G1ACHN":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/electric_chain_loss_avg_kW'):.1f}",
    "G1ADIR":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/direct_path_loss_avg_kW'):.1f}",
    "G1AFRIC":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/friction_brake_kWh_per_cycle'):.2f}",
    "G1ASPS":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/pm_spin_shaft_kWh_per_cycle'):.2f}",
    "G1ASPB":
        f"{g('heat_ledger_ws6/G1a_VOLT_REG_cycle_average/pm_spin_bus_kWh_per_cycle'):.2f}",
}

# ---------------------------------------------------------------------------
# KX tokens: R23 errata (F1-F5) + the R22a series_duty_v2 verification run.
# Every one of these is a rendering of results_ws4.json - verify_ws4.py pins
# them, including the F1 occurrence count.
# ---------------------------------------------------------------------------
CBE = R["chain_boundary_exposure"]["cases"]
SDC = R["series_duty_v2"]["cases"]
SDORD = ["nominal", "cda_5.4", "alt2000m_45C"]
SDLBL = {"nominal": "Nominal (CdA 4.2, 2 kW aux, SL, GVW)",
         "cda_5.4": "CdA 5.4 (E13)",
         "alt2000m_45C": "2,000 m / +45 °C corner"}


def _rng(block, key, fmt, sep="–"):
    return (fmt.format(block[key + "_min"]) + sep
            + fmt.format(block[key + "_max"]))


def _sdrow(label, key, fmt, block=("ensemble",)):
    def _blk(c):
        o = SDC[c]
        for k in block:
            o = o[k]
        return o
    cells = " | ".join(_rng(_blk(c), key, fmt) for c in SDORD)
    return f"| {label} | {cells} |"


T.update({
    # --- F1: the CdA 5.4 positive-seed count, exported and rendered
    "CDAPOSN": f"{g('gate_g1/cda_5.4/ensemble/seeds_margin_positive_n'):.0f}",
    "CDAPOSTOT": f"{g('gate_g1/cda_5.4/ensemble/seeds_total'):.0f}",
    "CDAPOSSEEDS": ", ".join(
        f"{int(s)}" for s in g("gate_g1/cda_5.4/ensemble/"
                               "seeds_margin_positive")),
    # --- F2: measured boundary-convention exposure
    "BEXN": _rng(CBE["nominal"]["envelope"], "exposure_s_motoring", "{:.1f}"),
    "BEXNU": _rng(CBE["nominal"]["envelope"],
                  "exposure_s_motoring_on_unlocked_samples", "{:.1f}"),
    "BEXNL": _rng(CBE["nominal"]["envelope"],
                  "exposure_s_motoring_on_locked_samples", "{:.1f}"),
    "BEXNS": _rng(CBE["nominal"]["envelope"], "exposure_s_motoring_strict",
                  "{:.1f}"),
    "BEXNV": f"{CBE['nominal']['envelope']['exposed_speed_kmh_max_max']:.1f}",
    "BEXC": _rng(CBE["cda_5.4"]["envelope"], "exposure_s_motoring", "{:.1f}"),
    "BEXCL": _rng(CBE["cda_5.4"]["envelope"],
                  "exposure_s_motoring_on_locked_samples", "{:.1f}"),
    "BEXCS": _rng(CBE["cda_5.4"]["envelope"], "exposure_s_motoring_strict",
                  "{:.1f}"),
    "BEXCV": f"{CBE['cda_5.4']['envelope']['exposed_speed_kmh_max_max']:.1f}",
    "BEXPPN":
        f"{CBE['nominal']['envelope']['one_sided_pp_locked_linear_max']:.4f}",
    "BEXPPC":
        f"{CBE['cda_5.4']['envelope']['one_sided_pp_locked_linear_max']:.4f}",
    "BEXPPC2": f"{CBE['cda_5.4']['envelope']['one_sided_pp_locked_hostile_2x_max']:.4f}",
    "BEXKWHC": f"{CBE['cda_5.4']['envelope']['over_boundary_wheel_kWh_max']:.4f}",
    # --- F3: the printed vintage spread, computed
    "VSPREAD":
        f"{g('gate_g1_map_vintage_spread/spread_pp_432_749V_window'):.2f}",
    "VSPREADR3":
        f"{g('gate_g1_map_vintage_spread/spread_pp_incl_r3_interim'):.2f}",
    # --- F4: the WS4-relative traction-map path
    "MAPPATHW4": g("ws2_chain_of_record/map_file_ws4_relative"),
    # --- F5: both chain weightings
    "ETASD":
        f"{g('sanity/eta_chain_bus_to_wheel_series_duty_weighted'):.4f}",
    "FTWSD":
        f"{g('sanity/series_fuel_to_wheel_g_per_kWh_series_duty'):.1f}",
    "ETASDLO":
        f"{g('chain_weighting_convention/series_duty_weighted/eta_bus_to_wheel_min'):.4f}",
    "ETASDHI":
        f"{g('chain_weighting_convention/series_duty_weighted/eta_bus_to_wheel_max'):.4f}",
    # --- R22a series_duty_v2
    "SDUSABLE": f"{g('series_duty_v2/_inputs/usable_bus_kWh'):.2f}",
    "SDUSABLE6": f"{g('series_duty_v2/_inputs/usable_bus_kWh'):.6f}",
    "SDFLOOR": f"{g('series_duty_v2/_inputs/superseded_floor_kWh'):.1f}",
    "SDUNSERVED":
        f"{g('series_duty_v2/unserved_energy_verdict/worst_case_kWh'):.4f}",
    "SDUNSGOV":
        g("series_duty_v2/unserved_energy_verdict/worst_case_governing_case"),
    "SDUNSALL":
        f"{g('series_duty_v2/unserved_energy_verdict/all_cases_zero')}",
    "SDDISPK": "{:.1f}".format(max(
        SDC[c]["ensemble"]["pack_dis_peak_kW_max"] for c in SDORD)),
    "SDCHGPK": "{:.1f}".format(max(
        SDC[c]["ensemble"]["pack_chg_peak_kW_max"] for c in SDORD)),
    "SDGATEUNS": f"{g('series_duty_v2/unserved_energy_verdict/archived_gate_comparison/cda_5_4_max_kWh'):.2f}",
    # tables
    "SDTABLE": "\n".join([
        "| Export (8-seed envelope, mode (b)) | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        _sdrow("Fuel energy **kWh/km**", "fuel_energy_kWh_per_km", "{:.3f}"),
        _sdrow("Fuel L/100 km", "l_per_100km", "{:.2f}"),
        _sdrow("Fuel per cycle [kg]", "fuel_kg", "{:.2f}"),
        _sdrow("**Unserved bus energy [kWh]**", "unserved_bus_kWh",
               "{:.4f}"),
        _sdrow("Above-pin **demand** [s/cycle]", "above_pin_demand_s",
               "{:,.1f}"),
        _sdrow("Above-pin demand energy [kWh]", "above_pin_demand_kWh",
               "{:.1f}"),
        _sdrow("Above-pin **engine** duty [s/cycle]", "above_pin_engine_s",
               "{:.1f}"),
        _sdrow("Emergency-band time [s/cycle]", "emergency_band_s", "{:.1f}"),
        _sdrow("Genset starts per cycle", "genset_starts", "{:.0f}"),
        _sdrow("Genset starts per hour", "genset_starts_per_h", "{:.1f}"),
        _sdrow("Genset on-fraction", "genset_on_frac", "{:.3f}"),
        _sdrow("Above-pin transitions per hour",
               "above_pin_transitions_per_h", "{:.1f}"),
        _sdrow("SOC minimum (frac usable)", "soc_min", "{:.3f}"),
        _sdrow("SOC maximum (frac usable)", "soc_max", "{:.3f}"),
        _sdrow("Pack **discharge** peak [kW bus]", "pack_dis_peak_kW",
               "{:.1f}"),
        _sdrow("Pack **charge** peak [kW bus]", "pack_chg_peak_kW", "{:.1f}"),
        _sdrow("Time above R8 125 kW discharge [s]",
               "pack_dis_over_r8_125kW_s", "{:.1f}"),
        _sdrow("Time above R8 110 kW charge [s]", "pack_chg_over_r8_110kW_s",
               "{:.1f}"),
        _sdrow("Peak regen to pack [kW bus]", "regen_bus_peak_kW", "{:.1f}"),
        _sdrow("Regen shed by the R16 curve [kWh]", "regen_shed_by_r16_kWh",
               "{:.4f}"),
        _sdrow("Motor over-rating exposure [s]", "motor_over_rating_s",
               "{:.1f}"),
        _sdrow("Fuel energy per payload t·km \u2014 **companion, not the "
               "R32 metric** (§4-KX.1, ESC-7)",
               "fuel_energy_kWh_per_payload_tonne_km", "{:.4f}"),
    ]),
    "SDBPTABLE": "\n".join([
        "| Companion (b′) load-following | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        _sdrow("Fuel energy kWh/km", "fuel_energy_kWh_per_km", "{:.3f}",
               block=("companion_bp", "ensemble")),
        _sdrow("Genset starts per cycle", "genset_starts", "{:.0f}",
               block=("companion_bp", "ensemble")),
        _sdrow("Unserved bus energy [kWh]", "unserved_bus_kWh", "{:.4f}",
               block=("companion_bp", "ensemble")),
    ]),
    # R16 binding
    "R16NOM": f"{g('series_duty_v2/_inputs/r16_accept_kW_bus/nominal'):.1f}",
    "R16ALT":
        f"{g('series_duty_v2/_inputs/r16_accept_kW_bus/alt2000m_45C'):.1f}",
    "R16PK":
        f"{g('series_duty_v2/r16_binding_analysis/peak_regen_to_pack_kW_bus'):.1f}",
    "R16COLD":
        f"{g('series_duty_v2/r16_binding_analysis/cold_side_binding_cell_C'):.1f}",
    "R16HOT":
        f"{g('series_duty_v2/r16_binding_analysis/hot_side_binding_cell_C'):.1f}",
    "R1655":
        f"{g('series_duty_v2/r16_binding_analysis/accept_at_ws3_loop_ceiling_55C_kW'):.1f}",
    "R16BOUND":
        f"{g('series_duty_v2/r16_binding_analysis/regen_leg_bound_any_sample')}",
    # R8 power-envelope bracket
    "R8WORST":
        f"{g('series_duty_v2/r8_power_envelope_bracket/worst_unserved_kWh'):.3f}",
    "R8WORSTGOV":
        g("series_duty_v2/r8_power_envelope_bracket/"
          "worst_unserved_governing_case"),
    "R8TABLE": "\n".join([
        "| R8 envelope enforced (125 kW dis / 110 kW chg, bus) | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Unserved bus energy [kWh] | " + " | ".join(
            _rng(g(f"series_duty_v2/r8_power_envelope_bracket/cases/{c}/"
                   "ensemble"), "unserved_bus_kWh", "{:.4f}")
            for c in SDORD) + " |",
        "| Discharge clipped [s/cycle] | " + " | ".join(
            _rng(g(f"series_duty_v2/r8_power_envelope_bracket/cases/{c}/"
                   "ensemble"), "r8_envelope_dis_clip_s", "{:.1f}")
            for c in SDORD) + " |",
        "| Charge shed [kWh/cycle] | " + " | ".join(
            _rng(g(f"series_duty_v2/r8_power_envelope_bracket/cases/{c}/"
                   "ensemble"), "r8_envelope_chg_shed_kWh", "{:.3f}")
            for c in SDORD) + " |",
        "| Fuel per cycle [kg] | " + " | ".join(
            _rng(g(f"series_duty_v2/r8_power_envelope_bracket/cases/{c}/"
                   "ensemble"), "fuel_kg", "{:.2f}")
            for c in SDORD) + " |",
    ]),
    # R22d coast member
    "R22DS": _rng(SDC["nominal"]["ensemble"], "coast_no_regen_s", "{:.1f}"),
    "R22DPP":
        f"{g('series_duty_v2/r22d_coast_spin_member/unbooked_pp_max'):.4f}",
    "R22DW": f"{g('interface_ws4/spin_drag_operational_note_r22d/ws2_point_drag_85kmh_W_shaft'):,.0f}",
    "R22DWB": f"{g('interface_ws4/spin_drag_operational_note_r22d/ws2_point_draw_85kmh_W_bus'):.0f}",
    # hysteresis sensitivity
    "HYSTWS3": f"{g('series_duty_v2/hysteresis_sensitivity/ws3_allocated_genset_hysteresis_kWh'):.1f}",
    "HYSTSIM": f"{g('series_duty_v2/hysteresis_sensitivity/simulator_band_kWh'):.2f}",
    "HYSTTABLE": "\n".join([
        "| Reference seed 23 | " + " | ".join(SDLBL[c] for c in SDORD)
        + " |",
        "|---|---|---|---|",
        "| Genset starts — simulator band | " + " | ".join(
            f"{g(f'series_duty_v2/hysteresis_sensitivity/cases/{c}/ref_seed/simulator_band/genset_starts'):.0f}"
            for c in SDORD) + " |",
        "| Genset starts — WS3 allocated band | " + " | ".join(
            f"{g(f'series_duty_v2/hysteresis_sensitivity/cases/{c}/ref_seed/ws3_band/genset_starts'):.0f}"
            for c in SDORD) + " |",
        "| kWh/km — simulator band | " + " | ".join(
            f"{g(f'series_duty_v2/hysteresis_sensitivity/cases/{c}/ref_seed/simulator_band/fuel_energy_kWh_per_km'):.3f}"
            for c in SDORD) + " |",
        "| kWh/km — WS3 allocated band | " + " | ".join(
            f"{g(f'series_duty_v2/hysteresis_sensitivity/cases/{c}/ref_seed/ws3_band/fuel_energy_kWh_per_km'):.3f}"
            for c in SDORD) + " |",
    ]),
    # heat rows for WS6
    "SDHEATTABLE": "\n".join([
        "| Case (VOLT-REG cycle average, 8-seed max) | Engine rejection "
        "[kW] | Generator+rectifier [kW] | Electric chain [kW] | Friction "
        "brake [kWh/cycle] |",
        "|---|---|---|---|---|",
        *[f"| {SDLBL[c]} | "
          f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/engine_rejection_avg_kW'):.1f} | "
          f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/generator_loss_avg_kW'):.2f} | "
          f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/electric_chain_loss_avg_kW'):.2f} | "
          f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/friction_brake_kWh_per_cycle'):.2f} |"
          for c in SDORD]]),
    # pinned point of the ordered run + per-case prose numbers
    "V2PINKW":
        f"{g('series_duty_v2/cases/nominal/pinned_point/p_shaft_kw'):.1f}",
    "V2PINBUS":
        f"{g('series_duty_v2/cases/nominal/pinned_point/p_bus_kw'):.1f}",
    "V2PINBSFC":
        f"{g('series_duty_v2/cases/nominal/pinned_point/bsfc'):.1f}",
    "SDNOMONFRAC": _rng(SDC["nominal"]["ensemble"], "genset_on_frac",
                        "{:.3f}"),
    "SDNOMSTARTS": _rng(SDC["nominal"]["ensemble"], "genset_starts",
                        "{:.0f}"),
    "SDNOMAPD": _rng(SDC["nominal"]["ensemble"], "above_pin_demand_s",
                     "{:,.1f}"),
    "SDNOMAPDKWH": _rng(SDC["nominal"]["ensemble"], "above_pin_demand_kWh",
                        "{:.1f}"),
    "SDNOMOR": _rng(SDC["nominal"]["ensemble"], "motor_over_rating_s",
                    "{:.1f}"),
    "SDCDAOR": _rng(SDC["cda_5.4"]["ensemble"], "motor_over_rating_s",
                    "{:.1f}"),
    "SDCDASOCMIN": _rng(SDC["cda_5.4"]["ensemble"], "soc_min", "{:.3f}"),
    "SDCDAEMERG": _rng(SDC["cda_5.4"]["ensemble"], "emergency_band_s",
                       "{:.1f}"),
    "SDCDAAPE": _rng(SDC["cda_5.4"]["ensemble"], "above_pin_engine_s",
                     "{:.1f}"),
    "SOCGATEUS":
        f"{g('series_duty_v2/soc_window_check/gate_soc_usable_equivalent'):.4f}",
    "SOCGATENP":
        f"{g('series_duty_v2/soc_window_check/gate_soc_nameplate'):.2f}",
    "SOCGATECDA": _rng(g("series_duty_v2/soc_window_check/cases/cda_5.4"),
                       "t_below_gate_s", "{:.1f}"),
    "SOCGATETABLE": "\n".join([
        "| Time below WS3's declared R8 discharge SOC band | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Seconds per cycle below SOC "
        + f"{g('series_duty_v2/soc_window_check/gate_soc_nameplate'):.2f}"
        + " nameplate | " + " | ".join(
            _rng(g(f"series_duty_v2/soc_window_check/cases/{c}"),
                 "t_below_gate_s", "{:.1f}") for c in SDORD) + " |",
        "| Minimum SOC reached (nameplate) | " + " | ".join(
            f"{g(f'series_duty_v2/soc_window_check/cases/{c}/soc_nameplate_min'):.4f}"
            for c in SDORD) + " |",
    ]),
    "TRACEFILE": g("series_duty_v2/_trace_files/trace_10Hz"),
    "TRACEROWS": f"{g('series_duty_v2/_trace_files/trace_10Hz_rows'):,.0f}",
    "SOCFILE": g("series_duty_v2/_trace_files/soc_trajectories"),
    "GATESTATUS": g("interface_ws4/gate_g1/status"),
})

# ---------------------------------------------------------------------------
# KX r2 tokens (rework against FINDINGS_KX_r1.md). Every one of these is a
# rendering of results_ws4.json; verify_ws4.py pins them.
# ---------------------------------------------------------------------------
R16A = R["series_duty_v2"]["r16_binding_analysis"]
R16B = R["series_duty_v2"]["r16_pack_acceptance_bracket"]
BPC = R["series_duty_v2"]["companion_bp_capability_comparison"]
D5R = R["chain_boundary_exposure"]["d5_reconciliation"]
HYS = R["series_duty_v2"]["hysteresis_sensitivity"]
TR20 = R["heat_ledger_ws6"]["series_duty_v2_transient_vs_R20_design_point"]
TRF = R["series_duty_v2"]["_trace_files"]


def _r16rng(block, c, fmt="{:.1f}"):
    return (fmt.format(R16A[block]["per_case_min"][c]) + "\u2013"
            + fmt.format(R16A[block]["per_case_max"][c]))


def _bprow(label, key, fmt, blk="companion_bp"):
    cells = " | ".join(
        _rng(SDC[c][blk]["ensemble"] if blk == "companion_bp"
             else SDC[c]["ensemble"], key, fmt) for c in SDORD)
    return f"| {label} | {cells} |"


T.update({
    # --- KX-B1: the two readings of R16
    "R16LEGBOUND": f"{R16A['regen_leg_bound_any_sample']}",
    "R16PACKBOUND": f"{R16A['pack_charge_bound_by_r16_any_sample']}",
    "R16PACKPK": f"{R16A['peak_pack_charge_kW_bus']:.1f}",
    "R16PACKPKA": f"{SDC['alt2000m_45C']['ensemble']['pack_chg_peak_kW_max']:.1f}",
    "R16PACKPKGOV": R16A["peak_pack_charge_governing_case"],
    "R16ABOVEN": _r16rng("pack_charge_above_r16_accept_s", "nominal"),
    "R16ABOVEC": _r16rng("pack_charge_above_r16_accept_s", "cda_5.4"),
    "R16ABOVEA": _r16rng("pack_charge_above_r16_accept_s", "alt2000m_45C"),
    "R16LONGEST":
        f"{R16A['pack_charge_above_r16_accept_longest_s']['worst_case_max']:.1f}",
    "R16LONGESTGOV":
        R16A["pack_charge_above_r16_accept_longest_s"][
            "worst_case_max_governing_case"],
    "R16EXCESSKWH":
        f"{R16A['pack_charge_above_r16_accept_kWh']['worst_case_max']:.3f}",
    "R16EXCESSGOV":
        R16A["pack_charge_above_r16_accept_kWh"][
            "worst_case_max_governing_case"],
    "R16PULSE25": f"{R16A['pulse10s_kW_bus_at_declared_cells']['nominal']:.1f}",
    "R16PULSE45":
        f"{R16A['pulse10s_kW_bus_at_declared_cells']['alt2000m_45C']:.1f}",
    "R16PULSECOVERS": f"{R16A['pulse10s_covers_the_excursions']}",
    "R1650": f"{R16A['accept_at_50C_kW']:.1f}",
    "R16PULSE55": f"{R16A['pulse10s_at_ws3_loop_ceiling_55C_kW']:.1f}",
    "R16TABLE": "\n".join([
        "| R16 read as a PACK charge limit (measured, NOT enforced) | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| R16 continuous acceptance at declared cells [kW bus] | "
        + " | ".join(f"{R16A['accept_kW_bus_at_declared_cells'][c]:.3f}"
                     for c in SDORD) + " |",
        "| **Pack charge above acceptance [s/cycle]** | "
        + " | ".join(_r16rng("pack_charge_above_r16_accept_s", c)
                     for c in SDORD) + " |",
        "| Longest single excursion [s] | "
        + " | ".join(
            f"{R16A['pack_charge_above_r16_accept_longest_s']['per_case_max'][c]:.1f}"
            for c in SDORD) + " |",
        "| Excess energy, worst seed [kWh] | "
        + " | ".join(
            f"{R16A['pack_charge_above_r16_accept_kWh']['per_case_max'][c]:.3f}"
            for c in SDORD) + " |",
        "| Pack charge peak [kW bus] | "
        + " | ".join(f"{SDC[c]['ensemble']['pack_chg_peak_kW_max']:.1f}"
                     for c in SDORD) + " |",
        "| WS3 10-s **pulse** rating at declared cells [kW bus] | "
        + " | ".join(f"{R16A['pulse10s_kW_bus_at_declared_cells'][c]:.3f}"
                     for c in SDORD) + " |",
    ]),
    "R16BTABLE": "\n".join([
        "| R16 acceptance ENFORCED on the pack | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Charge shed [kWh/cycle] | " + " | ".join(
            _rng(g(f"series_duty_v2/r16_pack_acceptance_bracket/cases/{c}/"
                   "ensemble"), "r16_pack_cap_shed_kWh", "{:.3f}")
            for c in SDORD) + " |",
        "| Charge clipped [s/cycle] | " + " | ".join(
            _rng(g(f"series_duty_v2/r16_pack_acceptance_bracket/cases/{c}/"
                   "ensemble"), "r16_pack_cap_clip_s", "{:.1f}")
            for c in SDORD) + " |",
        "| **Unserved bus energy [kWh]** | " + " | ".join(
            _rng(g(f"series_duty_v2/r16_pack_acceptance_bracket/cases/{c}/"
                   "ensemble"), "unserved_bus_kWh", "{:.4f}")
            for c in SDORD) + " |",
        "| Fuel per cycle [kg] | " + " | ".join(
            _rng(g(f"series_duty_v2/r16_pack_acceptance_bracket/cases/{c}/"
                   "ensemble"), "fuel_kg", "{:.2f}")
            for c in SDORD) + " |",
    ]),
    "R16BSHED": f"{R16B['worst_shed_kWh']:.3f}",
    "R16BSHEDGOV": R16B["worst_shed_governing_case"],
    "R16BCLIP": f"{R16B['worst_clip_s']:.1f}",
    "R16BUNS": f"{R16B['worst_unserved_kWh']:.4f}",
    "R16BFUEL": f"{R16B['fuel_penalty_pct_max']:+.2f}",
    "R16BFUELGOV": R16B["fuel_penalty_pct_max_governing_case"],
    # --- KX-M1: the genset above its own continuous rating
    "M1CONTN":
        f"{BPC['engine_continuous_rating_kW_by_case']['nominal']:.1f}",
    "M1CONTA":
        f"{BPC['engine_continuous_rating_kW_by_case']['alt2000m_45C']:.1f}",
    "M1AUTO": f"{BPC['engine_automotive_peak_kW']:.1f}",
    "M1GENCONT": f"{BPC['generator_continuous_shaft_input_kW']:.1f}",
    "M1SN": _rng(SDC["nominal"]["ensemble"],
                 "engine_over_continuous_rating_s", "{:.1f}"),
    "M1SC": _rng(SDC["cda_5.4"]["ensemble"],
                 "engine_over_continuous_rating_s", "{:.1f}"),
    "M1SA": _rng(SDC["alt2000m_45C"]["ensemble"],
                 "engine_over_continuous_rating_s", "{:.1f}"),
    "M1WORSTS":
        f"{BPC['axes']['engine_over_continuous_rating_s']['mode_b_block_of_record']['worst_case_max']:.1f}",
    "M1WORSTGOV":
        BPC["axes"]["engine_over_continuous_rating_s"][
            "mode_b_block_of_record"]["worst_case_max_governing_case"],
    "M1PEAK":
        f"{BPC['axes']['engine_shaft_peak_kW']['mode_b_block_of_record']['worst_case_max']:.1f}",
    "M1PEAKPCT": "{:.0f}".format(
        100.0 * BPC["axes"]["engine_shaft_peak_kW"][
            "mode_b_block_of_record"]["worst_case_max"]
        / BPC["engine_continuous_rating_kW_by_case"]["nominal"]),
    "M1TABLE": "\n".join([
        "| Genset vs its own rating (mode (b), 8-seed) | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Continuous flat-rating x case derate [kW shaft] | "
        + " | ".join(f"{BPC['engine_continuous_rating_kW_by_case'][c]:.1f}"
                     for c in SDORD) + " |",
        "| **Seconds above it [s/cycle]** | "
        + " | ".join(_rng(SDC[c]["ensemble"],
                          "engine_over_continuous_rating_s", "{:.1f}")
                     for c in SDORD) + " |",
        "| Longest continuous excursion [s] | "
        + " | ".join(
            f"{SDC[c]['ensemble']['engine_over_continuous_rating_longest_s_max']:.1f}"
            for c in SDORD) + " |",
        "| Energy delivered above the rating [kWh] | "
        + " | ".join(
            f"{SDC[c]['ensemble']['engine_over_continuous_rating_kWh_max']:.2f}"
            for c in SDORD) + " |",
        "| Peak engine shaft [kW] | "
        + " | ".join(f"{SDC[c]['ensemble']['engine_shaft_peak_kW_max']:.1f}"
                     for c in SDORD) + " |",
        "| Generator above its "
        + f"{BPC['generator_continuous_shaft_input_kW']:.0f}"
        + " kW continuous shaft input [s] | "
        + " | ".join(
            f"{SDC[c]['ensemble']['generator_over_continuous_input_s_max']:.1f}"
            for c in SDORD) + " |",
    ]),
    # --- KX-B2: the companion on the capability axes
    "SDBPTABLE2": "\n".join([
        "| Companion (b\u2032) load-following, 8-seed | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        _bprow("Fuel energy kWh/km", "fuel_energy_kWh_per_km", "{:.3f}"),
        _bprow("Genset starts per cycle", "genset_starts", "{:.0f}"),
        _bprow("Unserved bus energy [kWh]", "unserved_bus_kWh", "{:.4f}"),
        _bprow("**Pack discharge peak [kW bus]** (R8 125)",
               "pack_dis_peak_kW", "{:.1f}"),
        _bprow("**Pack charge peak [kW bus]** (R8 110)",
               "pack_chg_peak_kW", "{:.1f}"),
        _bprow("**Pack charge above R16 acceptance [s]**",
               "pack_chg_above_r16_accept_s", "{:.1f}"),
        _bprow("**Engine above its continuous rating [s]**",
               "engine_over_continuous_rating_s", "{:.1f}"),
        _bprow("Peak engine shaft [kW]", "engine_shaft_peak_kW", "{:.1f}"),
        _bprow("Emergency-band time [s/cycle]", "emergency_band_s", "{:.1f}"),
    ]),
    "BPPENN": "{:+.2f}".format(
        BPC["fuel_kWh_per_km_by_case"]["nominal"]["bp_penalty_pct_on_median"]),
    "BPPENC": "{:+.2f}".format(
        BPC["fuel_kWh_per_km_by_case"]["cda_5.4"]["bp_penalty_pct_on_median"]),
    "BPPENA": "{:+.2f}".format(
        BPC["fuel_kWh_per_km_by_case"]["alt2000m_45C"][
            "bp_penalty_pct_on_median"]),
    "BPDISPK": "{:.1f}".format(
        BPC["axes"]["pack_discharge_peak_kW_bus"]["mode_bp_companion"][
            "worst_case_max"]),
    "BPCHGPK": "{:.1f}".format(
        BPC["axes"]["pack_charge_peak_kW_bus"]["mode_bp_companion"][
            "worst_case_max"]),
    "BPENGPK": "{:.1f}".format(
        BPC["axes"]["engine_shaft_peak_kW"]["mode_bp_companion"][
            "worst_case_max"]),
    "BPINR8DIS": "{}".format(
        BPC["axes"]["pack_discharge_peak_kW_bus"]["mode_bp_companion"][
            "within_limit_on_every_ordered_seed"]),
    "BPINR8CHG": "{}".format(
        BPC["axes"]["pack_charge_peak_kW_bus"]["mode_bp_companion"][
            "within_limit_on_every_ordered_seed"]),
    "BPINR16": "{}".format(
        BPC["axes"]["pack_charge_above_r16_accept_s"]["mode_bp_companion"][
            "within_limit_on_every_ordered_seed"]),
    "BPINENG": "{}".format(
        BPC["axes"]["engine_over_continuous_rating_s"]["mode_bp_companion"][
            "within_limit_on_every_ordered_seed"]),
    # --- KX-M3: the payload denominator
    "PAYT": f"{g('series_duty_v2/_inputs/payload_metric_basis/payload_basis_t'):.1f}",
    "PAYKG": f"{g('series_duty_v2/_inputs/payload_metric_basis/payload_basis_kg'):,.0f}",
    # --- KX-M2: the live block's own chain of record
    "COR_MAP": g("series_duty_v2/_inputs/chain_of_record/map_file"),
    "COR_V": f"{g('series_duty_v2/_inputs/chain_of_record/map_voltage_V'):.0f}",
    "COR_RED": f"{g('series_duty_v2/_inputs/chain_of_record/reduction_flat'):.2f}",
    "COR_RND": f"{g('series_duty_v2/_inputs/chain_of_record/ws2_rework_round'):.0f}",
    "COR_TPPN": "{:.4f}".format(
        g("series_duty_v2/_inputs/boundary_convention_exposure/cases/"
          "nominal/total_pp_linear_max")),
    "COR_TPPC": "{:.4f}".format(
        g("series_duty_v2/_inputs/boundary_convention_exposure/cases/"
          "cda_5.4/total_pp_linear_max")),
    "COR_TPPA": "{:.4f}".format(
        g("series_duty_v2/_inputs/boundary_convention_exposure/cases/"
          "alt2000m_45C/total_pp_linear_max")),
    # --- KX-m2: D5 closed
    "D5LINN": "{:.1f}\u2013{:.1f}".format(
        *D5R["counts_s_per_cycle"]["nominal"][
            "strict_linear_envelope_r3_adjudicator_criterion"]),
    "D5LINC": "{:.1f}\u2013{:.1f}".format(
        *D5R["counts_s_per_cycle"]["cda_5.4"][
            "strict_linear_envelope_r3_adjudicator_criterion"]),
    "D5NODEGN": "{:.1f}\u2013{:.1f}".format(
        *D5R["counts_s_per_cycle"]["nominal"]["strict_nearest_column_excl_rpm0"]),
    "D5NODEGC": "{:.1f}\u2013{:.1f}".format(
        *D5R["counts_s_per_cycle"]["cda_5.4"]["strict_nearest_column_excl_rpm0"]),
    "D5ONRPM0N": "{:.1f}\u2013{:.1f}".format(
        *D5R["counts_s_per_cycle"]["nominal"]["attributable_to_rpm0_column"]),
    "D5RPM0COLS": ", ".join(f"{v:.0f}" for v in D5R["degenerate_rpm_columns"]),
    "D5VCEIL": f"{D5R['degenerate_column_speed_ceiling_kmh']:.2f}",
    "D5TABLE": "\n".join([
        "| Boundary-exposure criterion (motoring, s/cycle, 8-seed) | "
        "Nominal | CdA 5.4 |",
        "|---|---|---|",
        *[f"| {lbl} | "
          + " | ".join("{:.1f}\u2013{:.1f}".format(
              *D5R["counts_s_per_cycle"][c][key]) for c in ("nominal",
                                                            "cda_5.4"))
          + " |"
          for lbl, key in (
              ("Stencil criterion (WS4 headline)",
               "stencil_criterion_ws4_headline"),
              ("Strict, nearest rpm column (WS4 r1)",
               "strict_nearest_column"),
              ("**Strict, linear envelope (r3 adjudicator)**",
               "strict_linear_envelope_r3_adjudicator_criterion"),
              ("Strict, nearest column excl. the rpm = 0 column",
               "strict_nearest_column_excl_rpm0"),
              ("\u2003of which: attributable to the rpm = 0 column",
               "attributable_to_rpm0_column"))]]),
    # --- KX-m7: transient heat
    "HEATTRTABLE": "\n".join([
        "| Engine rejection, mode (b), 8-seed max [kW] | "
        + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Cycle average | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/engine_rejection_avg_kW'):.1f}"
            for c in SDORD) + " |",
        "| 10-min rolling maximum | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/engine_rejection_10min_max_kW'):.1f}"
            for c in SDORD) + " |",
        "| 2-min rolling maximum | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/engine_rejection_2min_max_kW'):.1f}"
            for c in SDORD) + " |",
        "| **Peak (0.1 s)** | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/engine_rejection_peak_kW'):.1f}"
            for c in SDORD) + " |",
        "| Implied radiator package, 2-min max [kW] | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/radiator_package_2min_max_kW'):.1f}"
            for c in SDORD) + " |",
        "| Implied radiator package, peak [kW] | " + " | ".join(
            f"{g(f'heat_ledger_ws6/series_duty_v2_{c}_cycle_average/radiator_package_peak_kW'):.1f}"
            for c in SDORD) + " |",
    ]),
    "R20DESIGN": f"{TR20['r20_design_point_radiator_package_kW']:.1f}",
    "R20ALT2MIN":
        f"{TR20['cases']['alt2000m_45C']['radiator_package_2min_max_kW']:.1f}",
    "R20ALTPEAK":
        f"{TR20['cases']['alt2000m_45C']['radiator_package_peak_kW']:.1f}",
    "R20SURVIVES": f"{TR20['r20_survives_on_the_2min_window']}",
    # --- KX-m8: 8-seed hysteresis
    "HYSTTABLE8": "\n".join([
        "| 8-seed envelope | " + " | ".join(SDLBL[c] for c in SDORD) + " |",
        "|---|---|---|---|",
        "| Genset starts \u2014 simulator band | " + " | ".join(
            _rng(HYS["cases"][c]["simulator_band"]["ensemble"],
                 "genset_starts", "{:.0f}") for c in SDORD) + " |",
        "| Genset starts \u2014 WS3 allocated band | " + " | ".join(
            _rng(HYS["cases"][c]["ws3_band"]["ensemble"],
                 "genset_starts", "{:.0f}") for c in SDORD) + " |",
        "| kWh/km \u2014 simulator band | " + " | ".join(
            _rng(HYS["cases"][c]["simulator_band"]["ensemble"],
                 "fuel_energy_kWh_per_km", "{:.3f}") for c in SDORD) + " |",
        "| kWh/km \u2014 WS3 allocated band | " + " | ".join(
            _rng(HYS["cases"][c]["ws3_band"]["ensemble"],
                 "fuel_energy_kWh_per_km", "{:.3f}") for c in SDORD) + " |",
        "| Unserved bus energy [kWh] \u2014 WS3 band | " + " | ".join(
            _rng(HYS["cases"][c]["ws3_band"]["ensemble"],
                 "unserved_bus_kWh", "{:.4f}") for c in SDORD) + " |",
    ]),
    # --- KX-m4: R34
    "R34N": f"{TRF['traces_emitted_n']:.0f}",
    "R34ORD": f"{TRF['ordered_mode_b_runs']:.0f}",
    "R34FILES": ", ".join(f"`{v}`" for v in TRF["traces_by_case"].values()),
    "R34SOCRUNS": f"{TRF['soc_trajectories_covers_runs']:.0f}",
    # --- KX-m6: the corrected ledger rows
    "HEATPKN": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_nominal_cycle_average/"
          "engine_rejection_peak_kW")),
    "HEATPKC": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_cda_5.4_cycle_average/"
          "engine_rejection_peak_kW")),
    "HEATPKA": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_alt2000m_45C_cycle_average/"
          "engine_rejection_peak_kW")),
    "HEAT2N": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_nominal_cycle_average/"
          "engine_rejection_2min_max_kW")),
    "HEAT2C": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_cda_5.4_cycle_average/"
          "engine_rejection_2min_max_kW")),
    "HEAT2A": "{:.1f}".format(
        g("heat_ledger_ws6/series_duty_v2_alt2000m_45C_cycle_average/"
          "engine_rejection_2min_max_kW")),
    "LEDGER1N": "{:.4f}".format(
        g("heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
          "engine_rejection_avg_kW/nominal")),
    "LEDGER1C": "{:.4f}".format(
        g("heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
          "engine_rejection_avg_kW/cda_5_4")),
    "LEDGER1A": "{:.4f}".format(
        g("heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
          "engine_rejection_avg_kW/alt2000m_45C")),
    "LEDGERUPN": "{:+.2f}".format(
        g("heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
          "understatement_pct/nominal")),
    "LEDGERUPA": "{:+.2f}".format(
        g("heat_ledger_ws6/series_duty_v2_cycle_average_kx_r1_superseded/"
          "understatement_pct/alt2000m_45C")),
    "M1BUNS": "{:.4f}".format(
        g("series_duty_v2/engine_continuous_rating_bracket/"
          "worst_unserved_kWh")),
    "M1BSOC": "{:.3f}".format(
        g("series_duty_v2/engine_continuous_rating_bracket/soc_min_worst")),
    "M1BSOCGOV": g("series_duty_v2/engine_continuous_rating_bracket/"
                   "soc_min_worst_governing_case"),
    "M1BFUEL": "{:+.2f}".format(
        g("series_duty_v2/engine_continuous_rating_bracket/"
          "fuel_penalty_pct_max")),
    "SDCDASOCMINMIN": "{:.3f}".format(
        SDC["cda_5.4"]["ensemble"]["soc_min_min"]),
    "LEDGERN":
        f"{g('heat_ledger_ws6/series_duty_v2_nominal_cycle_average/engine_rejection_avg_kW'):.4f}",
    "LEDGERC":
        f"{g('heat_ledger_ws6/series_duty_v2_cda_5.4_cycle_average/engine_rejection_avg_kW'):.4f}",
    "LEDGERA":
        f"{g('heat_ledger_ws6/series_duty_v2_alt2000m_45C_cycle_average/engine_rejection_avg_kW'):.4f}",
})

BODY = r"""# REPORT WS4 — GENSET, THE ARCHIVED GATE G1, AND THE R22a PURE-SERIES DUTY

Project Volt · workstream 4 · against **BASELINE_v3.md** (ratified
2026-08-30 — G1's kill EXECUTED; R22, R23) and **BASELINE_v5.md**
(ratified 2026-08-30 — R34 program hygiene). The gate sections below
were computed against BASELINE_v2.md and are **archived, not
recomputed**.
Author: WS4 (engine & generator). Status: **for adjudication — KX
round 2 (rework)** against `FINDINGS_KX_r1.md` (2 blocking, 3 material,
8 minor — all addressed), executing the lead directive
`KX_DIRECTIVE.md` (rulings R22, R23). Rework changelog in **§0-KX2**,
including the exported-member delta for the two workstreams consuming
`series_duty_v2` live; the KX r1 changelog (§0-KX), the G1-R changelog
(§0-R) and the round-2 changelog (§0) are retained as history.

> **KX r2 in one line: no ordered number moved, and the block now says
> what it does.** The two blocking findings were interface-correctness
> defects on a live design-input block — a field asserting a constraint
> was inactive while the pack was charged above it (B1), and a companion
> run that omitted the very axes the escalation it feeds turns on (B2).
> Both are fixed at source and both are now measured, bracketed and
> escalated rather than decided by WS4. Every `series_duty_v2` fuel,
> unserved-energy, above-pin, SOC, starts and pack-peak value is
> byte-identical to the r1 vintage; §0-KX2 lists the member-level delta.

**The clutch is dead.** BASELINE_v3 executed Gate G1's kill clause on
the numbers this report carries. Nothing in this round re-runs or
re-argues the gate: its margins reproduce bit-identically, the four
record-precision errata R23 ordered are corrected and checker-pinned,
and `interface_ws4 → gate_g1` is now an **ARCHIVED record block**
(`status: @GATESTATUS@`) whose fields may not be consumed as live
requirements. The live V2 design input is the new §4-KX block,
`series_duty_v2`.

Everything below is produced by runnable code in this folder.
`./.venv/bin/python run_ws4.py` regenerates every number, map, table,
trace and figure in ~4 min (`pip install -r requirements.txt` into any
Python ≥3.12 venv first); `results_ws4.json` is the machine-readable
form; `make_report_ws4.py` generates this report with the Interfaces
block and every headline injected from that JSON; and `verify_ws4.py`
asserts that every headline number here matches `results_ws4.json`
verbatim — no *current* number is transcribed by hand, and the R23
errata carry their own checker pins (including, from KX r2, a
**per-section** placement pin, so a corrected phrase cannot be corrected
in only three of four *places* again — a count is not a place check). (Historical values quoted in the changelogs — the r2 record and
the unreproducible r3-interim run — are quotations of the prior record;
the r3-interim margins are carried as a literal historical block in
`results_ws4.json` and rendered from it.) All stochastic inputs are
WS1's seeded cycle builders; extrema are 8-seed ensemble envelopes
(R9). WS1's, WS2's and WS3's folders are imported read-only, and every
consumed input is recorded by SHA-256 in `results_ws4.json →
kx_input_provenance → input_sha256` (and, for the archived gate,
`ws2_chain_of_record → input_sha256`).

> **KX headline (R22a): PURE SERIES V2 AT THE DELIVERED PACK COMPLETES
> EVERY ORDERED CASE WITH ZERO UNSERVED BUS ENERGY.** On WS3's
> delivered @SDUSABLE@ kWh usable at the bus — not the R8 @SDFLOOR@ kWh
> floor the archived gate ran on — the pinned pure-series V2 follows
> VOLT-REG at nominal, at CdA 5.4 and at the 2,000 m/+45 °C corner on
> all eight seeds with worst-case unserved bus energy **@SDUNSERVED@
> kWh** (all cases zero: @SDUNSALL@; @SDUNSGOV@), against the
> @SDGATEUNS@ kWh the 3.5 kWh floor shed at CdA 5.4.
> ESC-5's energy-side buffer worry is **closed at the delivered pack**.
> Two things it does *not* close, both reported not tuned: the pack's
> bus-side **power** envelope is exceeded — discharge peaks to
> @SDDISPK@ kW against R8's 125 kW, and enforcing the envelope costs
> @R8WORST@ kWh of unserved energy at the corner (§4-KX, ESC-9) — and
> the R3 motor rating is still exceeded, unchanged from the gate
> record. R16's curve is consumed and is **not binding on the regen
> leg** at any ordered (warm) case — but read as the **pack** charge
> limit its own header names, the same curve is **exceeded on every
> ordered case** (@R16ABOVEN@ / @R16ABOVEC@ / @R16ABOVEA@ s per cycle,
> peak pack charge @R16PACKPK@ kW bus), because regen and the genset
> charge the pack at the same time; both readings and the cost of
> enforcing the pack one are now exported, and the choice between them
> is escalated (ESC-8). The genset also runs above its own
> @M1CONTN@ kW continuous flat-rating for up to @M1WORSTS@ s per cycle
> (ESC-10). Fuel energy
> per km, above-pin duty, SOC trajectories, genset cycling and the
> per-seed tables are exported for WS5's R22b dispatch question.
>
> **Archived headline (Gate G1, decided): GATE G1 FAILED under the
> ruled conventions and BASELINE_v3 executed the kill. Recomputed per
> the G1-R directive (R12 chain convention + WS2's measured spin-drag
> member), the locked path with charge-bias load-point shifting now
> TRAILS pure series at the pinned BSFC point: margin @MIN@% (ensemble
> minimum) / @MED@% (median) / @MAX@% (max) at the nominal condition —
> the sign of the comparison is reversed, and the ≥5% kill criterion is
> missed by @GAP@ points. The ensemble-minimum margin is negative at
> every tested condition; CdA 5.4 is break-even (min @CDAMIN@% / median
> @CDAMED@% / max @CDAMAX@%, @CDAPOSN@ of 8 seeds marginally positive —
> seeds @CDAPOSSEEDS@), every
> other condition is negative on all eight seeds. Attribution (§6): the
> R12 map-vs-scalar swap alone moves the margin @MPDMIN@ pp; the
> spin-drag member alone @SPDMIN@ pp. The sign is additionally
> bracketed against the one declared-not-measured genset member (§6):
> replacing the rectifier/conditioning model with a hostile 3%-class
> stage gives @BRMIN@% min, and stacking WS1's full 3% stage on top —
> the most hostile defensible accounting — gives @BSMIN@% min:
> break-even, still @BSGAP@ points short of the criterion. **The kill
> outcome is invariant under every accounting.** Chain vintage: **WS2
> round-@WS2ROUND@ maps
> on the R10 bus (@MAPV@ V nominal map) — the traction chain of record
> the directive names**; WS2 r4 landed mid-round and the directive's
> hot-swap pipeline consumed it (§0-R), and the verdict is insensitive
> to map voltage across WS2's full exported window (§6). The kill
> clause was armed at ≥5% on these numbers (BASELINE_v2); BASELINE_v3
> executed it. WS4 reported the number; the lead executed.**

---

## 0-KX2. KX rework changelog (response to `FINDINGS_KX_r1.md`)

KX round 1 was adjudicated **NOT CLEAN: 2 blocking, 3 material, 8
minor.** Every finding is addressed below at root cause, with what
changed and where. **No ordered number in `series_duty_v2` moved** —
the block's fuel, unserved-energy, above-pin, SOC, starts and pack-peak
values are byte-for-byte the r1 values, which is the correct outcome
because none of the findings said an ordered number was wrong. What
changed is what the block *says about itself*: three exported member
sets are new, two members are renamed, and the WS6 ledger rows are
recomputed. The member-level delta is listed at the end of this section
for the two workstreams (WS11, WS5) consuming this block live.

### Blocking

- **KX-B1 — R16's cap applied to the regen leg only; `bound_any_sample:
  false` exported while the pack is charged above its own acceptance
  curve.** *Root cause:* `ws4_sim.run_g1_mode` applied
  `chg_accept_bus_kw` inside the `pw < 0.0` regen branch, and
  `p_batt_bus = p_gen_elec - p_bus_load` was formed afterwards and never
  tested. *Fixed at source:* the pack-side exceedance of the same curve
  is now measured on every run
  (`pack_chg_above_r16_accept_s`/`_kWh`/`_longest_s`, per seed, R14
  envelopes, both (b) and (b′)); the misleading field is **renamed**
  `bound_any_sample` → `regen_leg_bound_any_sample` and joined by
  `pack_charge_bound_by_r16_any_sample`; both readings of WS3's
  interface are stated in `r16_binding_analysis → _two_readings`; WS3's
  10-s **pulse** column — never consulted in r1 — is loaded and shown not
  to cover the excursions; and a new bracket
  (`r16_pack_acceptance_bracket`) enforces the pack reading and prices
  it. Measured: @R16ABOVEN@ / @R16ABOVEC@ / @R16ABOVEA@ s per cycle above
  acceptance, longest @R16LONGEST@ s, peak pack charge @R16PACKPK@ kW
  bus. **WS4 does not choose the reading** — that is WS3's interface
  semantics and WS5's blend order — and ESC-8 is restated on the pack
  quantity with the 50 °C and 55 °C continuous *and* pulse values, as
  the adjudicator's remedy (ii) requires. §4-KX.4 rewritten. The
  headline is invariant: enforcing the pack reading leaves unserved
  energy at @R16BUNS@ kWh.
- **KX-B2 — the (b′) companion exported only fuel and starts, omitting
  every axis R22b turns on.** *Root cause:* the interface projected
  `companion_bp` through `IFACE_R8_KEYS` (six fields). *Fixed at
  source:* a dedicated `IFACE_BP_KEYS` gives the companion the **same**
  capability export set as the block of record — pack discharge/charge
  peaks, both R8 exceedance counters, the new R16 pack counter, the new
  engine over-rating counters, emergency-band time, SOC envelope and the
  heat rows — and a new
  `companion_bp_capability_comparison` block states each axis as an
  explicit (b) vs (b′) verdict with R14 governing cases. §4-KX.6 carries
  the rows; ESC-9 now records, **without recommending**, that the
  load-following endpoint satisfies R8, R16-on-the-pack and the engine's
  continuous rating on every ordered seed at the fuel deltas already
  printed.

### Material

- **KX-M1 — the genset runs above its own 132 kW continuous
  flat-rating; no counter, no prose, and §4-KX.3's exceedance list
  omitted the component this workstream owns.** *Root cause:* the
  emergency band capped on `p_peak_kw` = the **automotive** peak.
  *Fixed:* the ceiling is now a named quantity in the simulator
  (`emerg_ceiling_kw`) and stated in §4-KX.1;
  `engine_over_continuous_rating_s`/`_kWh`/`_longest_s`,
  `engine_shaft_peak_kW` and `generator_over_continuous_input_s` are
  exported per seed with R14 envelopes for **both** (b) and (b′);
  §4-KX.3 carries the row alongside the motor and pack rows; a bracket
  (`engine_continuous_rating_bracket`) caps the engine at its own rating
  and confirms the headline does not rest on the over-rating; and it is
  raised as its own escalation, **ESC-10**, against R18/ESC-1.
- **KX-M2 — the live block could not resolve its own chain of record.**
  *Root cause:* the F4 fix landed inside `gate_g1`, whose archival
  notice forbids consumption, and `series_duty_v2` carried only prose
  plus a hash-table label. *Fixed:* `series_duty_v2 → _inputs →
  chain_of_record` now carries the WS4-relative map path, voltage,
  reduction, WS2 round, feasible-cell count and the map's SHA-256, and
  `_inputs → boundary_convention_exposure` carries the convention's
  measured exposure for all three ordered cases. `verify_ws4.py` asserts
  the live block resolves **without reading `gate_g1`**.
- **KX-M3 — the payload-denominated metric carried no denominator,
  basis or caveat into the interface.** *Fixed:* `_inputs →
  payload_metric_basis` carries the tonnage, WS1 source, the fact that
  it is identical in all three cases, and an explicit caveat that the
  field equals per-km ÷ @PAYT@ and is **not** the R32 metric. ESC-7
  restated to say which curb the @PAYT@ t belongs to (WS1's
  **pre-conversion** operating curb) and that it does not charge the
  series powertrain's mass. The field is kept rather than withdrawn, so
  no exported member disappears under live consumers.

### Minor

- **m1** — the hard-coded "*i.e. they are launch samples*" clause in
  `make_report_ws4.py` was refuted by its own rendered @BEXNV@ km/h.
  Clause deleted; the claim that survives is rendered from data (the
  rpm = 0-column share, §4.1).
- **m2 — D5 CLOSED.** The whole gap between WS4's strict count and the
  r3 adjudicator's is WS2's degenerate rpm = 0 map column.
  `ws4_chain.boundary_exposure_strict_linear` (the adjudicator's
  interpolated-envelope criterion) and `nearest_col_is_degenerate` now
  ship; both counts and the artefact share are exported
  (`chain_boundary_exposure → d5_reconciliation`) and printed in §4.1,
  §8 F-9 and §9 D5. Reproduces the adjudicator's published figures
  exactly: @D5LINN@ s nominal, @D5LINC@ s at CdA 5.4. No pp figure moves.
- **m3** — R14 governing-case labels added to the eight fields whose
  siblings had them: `gate_g1/boundary_convention_exposure/
  nominal_one_sided_pp_max`, `chain_weighting_convention/
  series_duty_weighted/eta_bus_to_wheel_max`, the three
  `r22d_coast_spin_member` maxima (which appear twice, and are labelled
  in both places because they are the same object),
  `gate_g1/verdict/margin_pct_ensemble_max`, and the three
  `attribution_rows/*/delta_pp_min`.
- **m4** — R34's interpretation is **declared**
  (`_trace_files → r34_interpretation`), the trace header no longer
  asserts an unqualified "one per run", @R34N@ traces are emitted (one
  per ordered case, up from one), and the ambiguity is flagged to the
  lead as **ESC-11** rather than self-resolved.
- **m5** — §0-R's list of the four F1 locations named ESC-6, which
  carries no seed count; the fourth occurrence is §0-R itself. Sentence
  reconciled with §0-KX's (which was correct), and `verify_ws4.py` now
  pins the phrase **per section slice** — headline, §0-R, §6, ESC-2 —
  instead of counting total occurrences.
- **m6** — the WS6 ledger rows divided the 8-seed maximum energy by the
  reference seed's duration. Each row is now the max of the **per-seed
  cycle averages**, and each component carries **its own** governing
  seed. Engine rejection: @LEDGER1N@ → **@LEDGERN@**, @LEDGER1C@ →
  **@LEDGERC@**, @LEDGER1A@ → **@LEDGERA@** kW (the r1 rows are retained
  as a literal at `heat_ledger_ws6 →
  series_duty_v2_cycle_average_kx_r1_superseded`).
- **m7** — peak and rolling **2-min / 10-min** maximum engine rejection
  are exported per case with R14 labels, plus the implied radiator-
  package rows and an explicit comparison against R20's @R20DESIGN@ kW
  design point (§4-KX.7). R20/ESC-4 survives on the 2-min window at the
  corner (@R20ALT2MIN@ kW): @R20SURVIVES@.
- **m8** — the hysteresis sensitivity now runs both bands over the
  **8-seed** ensemble (R9). The block is renamed
  `hysteresis_sensitivity_ref_seed` → `hysteresis_sensitivity`; the r1
  reference-seed rows are retained unchanged under `cases → <case> →
  ref_seed` and are still printed in §4-KX.6.

### Exported-member delta (for live consumers of `series_duty_v2`)

Two workstreams are consuming this block as a live design input while it
was ungated (WS11's Vehicle Zero ruler trial and WS5's R22b dispatch
question). **No value inside `series_duty_v2` changed. Exactly nine
numbers changed anywhere in `results_ws4.json`, and all nine are the
WS6 ledger rows corrected under m6** (engine / generator / chain cycle
averages, three cases). The changes a consumer must hot-swap for are:

| Kind | Member | Note |
|---|---|---|
| **renamed** | `r16_binding_analysis → bound_any_sample` → `regen_leg_bound_any_sample` | value unchanged (@R16LEGBOUND@); joined by `pack_charge_bound_by_r16_any_sample` = @R16PACKBOUND@ |
| **renamed** | `hysteresis_sensitivity_ref_seed` → `hysteresis_sensitivity` | now 8-seed; r1 rows preserved at `cases → <case> → ref_seed`, values identical |
| **recomputed** | `heat_ledger_ws6 → series_duty_v2_*_cycle_average` (engine / generator / chain rows) | +0.4–0.7 %, m6; `governing_case` is now a pointer to per-component labels |
| **added** | `_inputs → chain_of_record`, `_inputs → boundary_convention_exposure`, `_inputs → payload_metric_basis` | M2, M3 |
| **added** | pack-R16, engine-rating and transient-heat fields in every `cases[*].ensemble` and in `companion_bp_ensemble` | B1, B2, M1, m7 |
| **added** | `r16_pack_acceptance_bracket`, `engine_continuous_rating_bracket`, `companion_bp_capability_comparison` | B1, M1, B2 |
| **added** | two further 10 Hz traces | m4 |

Everything else in `series_duty_v2` — every case ensemble value, every
per-seed ordered export, the unserved-energy verdict, the SOC-window
check and the R8 bracket — is byte-identical to the r1 vintage.

---

## 0-KX. KX changelog (response to KX_DIRECTIVE.md — R22, R23)

The directive's scope is exhaustive and is executed exactly. **The gate
is not re-run or re-argued.** Its margins, ensembles, attribution rows
and bracket reproduce bit-identically under this round's code (the
prior-convention anchor assertion to 1e-9 still runs live, §10 check
9), and the only gate-side changes are the R23 errata and the
archival restatement of the interface block.

### R23 errata (directive item 1) — all five corrected and pinned

- **F1 (MATERIAL) — CdA 5.4 positive-seed count.** The data shows
  **@CDAPOSN@ of 8 seeds** positive (seeds @CDAPOSSEEDS@); the r3
  report said "two" in four places. Corrected in all four (headline,
  §0-R, §6 table, ESC-2). The count is no longer prose: it is computed
  in `run_ws4.py` for *every* condition and exported as
  `gate_g1/<case>/ensemble/seeds_margin_positive_n` +
  `seeds_margin_positive` with an R14 governing-case label, mirrored
  into `interface_ws4 → gate_g1 → verdict`. **Pin:**
  `verify_ws4.py` renders the count from JSON *and* asserts the
  corrected phrase occurs exactly four times and that the superseded
  wordings occur zero times — the failure mode was a partial
  correction, so the checker counts occurrences.
- **F2 (minor) — boundary-convention mode-neutrality.** The r3 claim
  ("mode-neutral and negligible") was true at the reference seed and
  false as a general claim. Exposure is now **measured per condition**
  by a counter in `ws4_chain.py` (`boundary_exposure`,
  `boundary_exposure_strict`) and the unbooked loss is **bounded** by
  extending the loss surface past each rpm column's feasible boundary
  with its own torque gradient (`boundary_excess_loss_kw`; copper loss
  goes as T², so the linear extension is a lower bound and a hostile
  2× row is carried). §4.1 is restated. **Pin:** the exposure
  envelopes and the one-sided pp bound are exported to
  `chain_boundary_exposure` and rendered; `verify_ws4.py` pins them
  and asserts the superseded wording is gone.
- **F3 (minor) — map-vintage spread.** Computed, not asserted:
  **@VSPREAD@ pp** across the 432–749 V exported window and
  **@VSPREADR3@ pp** once the r3-interim figure the sentence's
  parenthetical swept in is included — the 0.63 pp the adjudicator
  read off the printed record. §4.2 now states both spans separately.
  **Pin:** `gate_g1_map_vintage_spread`, both fields.
- **F4 (minor) — traction-map path resolution.** The interface field
  now resolves against *this* workstream's folder like every other
  `*_file` field: `@MAPPATHW4@`, with `map_file_owner` and
  `map_file_as_exported_by_owner` carried alongside. **Pin:**
  `verify_ws4.py` now resolves **every** `*_file` field in
  `interface_ws4` against the WS4 folder and fails if any is missing —
  a structural pin, not a one-off fix.
- **F5 (minor) — the 0.9005 chain figure's weighting.** Labelled:
  0.9005 is 0.97 × WS2's `eta_mot_avg`, energy-weighted over WS2's
  **i-MMD** VOLT-REG run. The **series-duty** companion — wheel energy
  ÷ bus energy through the same map over the full motoring trace — is
  **@ETASD@** (8-seed @ETASDLO@–@ETASDHI@), giving **@FTWSD@ g/kWh**
  ideal series fuel-to-wheel against the 0.9005-weighted @FTWR12@.
  §4.3 and §10 checks 3 and 5 are restated. The direction is
  confirmed: the r3 arithmetic *understated* the series advantage, so
  the imprecision leaned toward the clutch. **Pin:** both weightings
  and both fuel-to-wheel rates.

### R22a verification run (directive item 2) — §4-KX, `series_duty_v2`

Pure series V2 at the **delivered** pack (@SDUSABLE@ kWh usable at the
bus, read from WS3's own interface block at run time), three ordered
cases × 8 seeds, R16 cold curves consumed, R10 window, WS2 r4 maps, all
inputs SHA-pinned in `kx_input_provenance`. Unserved bus energy is
**@SDUNSERVED@ kWh** worst case. Exports: unserved energy, above-pin
duty (demand-side *and* engine-side), SOC trajectories (per-seed CSV +
figure + the 10 Hz trace), genset on/off and load-point cycling rates,
and fuel energy per km. Three checks WS4 added on its own initiative
because the ordered numbers rest on them (all labelled as such, D6):
the R8 **power**-envelope bracket, the SOC-window check against WS3's
declared discharge gate (both ESC-9), and WS3's allocated
genset-hysteresis band. A load-following companion (b′) is carried for
R22b; WS4 does not choose the dispatch.

### Escalations raised this round (§12)

- **ESC-7 (R32, D13/R36)** — the ordered metric is per km; R32's
  payload denomination for Vehicle Zero is not ratified. WS4 exports a
  payload companion and denominates no comparison on it.
- **ESC-8 (R16, R15, R2)** — R16's hot end crosses WS3's pack-loop
  sizing ceiling: at 55 °C cells the pack accepts less than this run's
  peak regen.
- **ESC-9 (R8 per R12/ES-4, R4/E24)** — the delivered pack has the
  energy, not the rated power, and the ordered run spends real time
  below the SOC band over which WS3 declares the discharge peak.

ESC-5's energy half is closed by this round; ESC-1 through ESC-6 are
otherwise unchanged or disposed by BASELINE_v3.

*(KX r2 adds two more and restates three: **ESC-10** (R18/ESC-1 — the
genset above its own continuous flat-rating) and **ESC-11** (R34 — the
"one trace per run" reading); ESC-7 restated on which curb the payload
denominator belongs to, ESC-8 restated on the pack quantity and widened
to the choice of reading, ESC-9 extended with the (b′) measurement. See
§0-KX2 and §12.)*

### Interface restatement (directive item 3)

`interface_ws4 → gate_g1` carries `status: @GATESTATUS@`, an explicit
archival notice ("no field of this block may be consumed as a live
requirement"), and is reorganised into the four members the directive
names — **verdict**, **attribution_rows**, **bracket_result**,
**provenance_hashes** — with the map-vintage robustness and the F2/F5
errata blocks attached. Nothing previously exported was dropped. The
R22d spin-drag operational note is added as a named member,
`interface_ws4 → spin_drag_operational_note_r22d`, carrying WS2's
@R22DW@ W shaft / @R22DWB@ W bus point drag at 85 km/h, the
coast-without-regen condition, the WS5 guidance, this run's measured
exposure, and an explicit double-count warning.

### Program hygiene (BASELINE_v5 R34)

Complied with from this artefact: `@TRACEFILE@` (@TRACEROWS@ rows at
10 Hz — WS1's builders integrate at 0.1 s, so the trace is native, not
resampled) plus `@SOCFILE@` for the per-seed SOC trajectories.
*(Superseded by KX r2: @R34N@ traces are now emitted, one per ordered
case, and R34's interpretation is declared rather than assumed —
§0-KX2 m4 and ESC-11.)*

---

## 0-R. G1-R changelog (response to G1R_DIRECTIVE.md)

Scope executed exactly as directed; every previously reported gate
number is restated below with its old and new value. The prior-
convention configuration is retained in `results_ws4.json →
gate_g1_prior_convention` and is reproduced exactly by the refactored
code before the ruled corrections are applied — the legacy code path is
float-identical by construction and the nominal ensemble statistics are
asserted against the ratified r2 values to 1e-9 in `run_ws4.py` (§10
check 9) — so the entire G1-R shift is the two ruled corrections, not
code drift.

- **Directive 1a (R12 chain convention, both modes): DONE.** The G1
  traction chain is now WS2's measured inverter+motor map × the flat
  0.97 reduction, applied identically to modes (a), (b) and (b′); no
  scalar PE member exists on the traction side, and WS1's
  `part_load_factor` no longer touches any G1 quantity (the map *is*
  the part-load reality). The genset-side PE/rectifier lives in WS4's
  ledger as the explicit generator+rectifier loss model it always was
  (§2, restated on R10 per 1c). All cross-workstream electrical
  quantities are stated bus-side. **Line-111 exclusion-set removals
  documented in §1.**
- **Directive 1b (spin drag charged to case (a)): DONE.** WS2's
  exported member: @SPINESH@ kWh engine-side + @SPINEBUS@ kWh bus-side
  per VOLT-REG (round-@WS2ROUND@ vintage; WS2's r4 re-derivation at
  the R10 winding left the cycle-level member numerically unchanged
  from r3, so the directive's "expect the r4 value to differ" resolved
  to "it did not"). Charged to mode (a) during
  locked samples at the mean locked-time rates @SPINSH@ kW shaft +
  @SPINBUS@ kW bus, so each seed pays for its actual locked time
  (envelope actually charged: @ASPSMIN@–@ASPSMAX@ kWh shaft,
  @ASPBMIN@–@ASPBMAX@ kWh bus). The r2 report's mode-neutrality claim
  (line 111) is **withdrawn** — WS2's measurement distinguishes
  unloaded lockup spin from loaded series operation.
- **Directive 1c (generator/rectifier on the R10 window): DONE.** Both
  generator specs restated on the pack-native window (662.4 V nominal,
  432.0–748.8 V operating, 777.6 V 10-s transient), 1200 V-class SiC
  rectifier devices (were 750 V-class at the superseded 370 V bus);
  loss-model coefficients carried unchanged at the new window
  [WS4-DECLARED, confirm at procurement]. **Pinned points re-placed and
  verified unmoved** (the restatement moves no loss coefficient;
  asserted in `run_ws4.py`).
- **Directive 2 (margins, same condition table, interface): DONE.**
  All six configurations recomputed (8-seed ensembles, R9); §6 table.
  Old → new (min/median): nominal **6.26/6.45 → @MIN@/@MED@%**; CdA 5.4
  **8.22/8.36 → @CDAMIN@/@CDAMED@%**; aux 4 kW **6.46/6.63 →
  @AUXMIN@/@AUXMED@%**; hot-alone **5.94/6.08 → @HOTMIN@/@HOTMED@%**;
  2,000 m + 45 °C **3.75/3.92 → @ALTMIN@/@ALTMED@%**; reference curve
  **6.58/6.76 → @REFMIN@/@REFMED@%**. Kill criterion ≥5% nominal
  ensemble-min: **FAILS** (@MIN@%). `interface_ws4 → gate_g1` exports
  the full condition set (F2 pattern), the convention, the chain
  vintage, the spin member and the one-factor rows; worst-case fields
  carry their governing case inline (R14).
- **Directive 3 (one-factor attribution): DONE.** Spin-drag member
  alone: margin @SPMIN@% min (@SPDMIN@ pp vs the prior convention).
  Map-vs-scalar swap alone: @MPMIN@% min (@MPDMIN@ pp). Together
  (G1-R): @BODMIN@ pp. The map swap is the dominant correction; §6.
- **Vintage statement (directive preamble): the hot-swap contingency
  was exercised.** This round started on WS2's round-3 exports (370 V
  maps, the only ones on disk) with the pipeline built to hot-swap;
  WS2 r4 landed mid-round and a re-run consumed the 432/662/749 V
  maps and the r4 spin member automatically, with no code change. The
  gate of record above is the **r4 (662 V nominal-map) run**. For the
  record, the interim r3-vintage run read @R3MIN@/@R3MED@/@R3MAX@%
  (min/median/max) at nominal (before the deficit-fill correction
  below) — within ~0.4 pp of the r4 verdict, the same sign and the
  same kill outcome, consistent with the map-vintage robustness rows
  in §6. Those figures are carried as a literal historical block in
  `results_ws4.json → gate_g1_interim_r3_vintage_record`: they are NOT
  regenerable, because WS2 r4 replaced the 370 V exports on disk.
- **Pre-adjudication adversarial pass (WS4-initiated, disclosed §9):**
  before launching the adjudicator, three independent adversarial
  reviews were run against this delivery. The physics review could not
  refute the reversal (map lookups verified against the CSV's own
  P_dc/P_shaft identities in both quadrants; regen through the chain
  reproduces WS2's exported 3.73 kWh to the last digit; an independent
  reconstruction reproduces the −7.0/−1.8 pp decomposition). Three
  real defects it and the consistency review found are fixed in this
  revision: (i) a spin-vs-map no-load **double-count** on locked
  torque-fill samples overcharged mode (a) by ~0.03–0.06 pp — fills
  now use the marginal map loss (loss(rpm,T) − loss(rpm,0)) when the
  spin member is active, moving the nominal margin @MIN@% (was −2.67%
  before the fix); (ii) the "conservative boundary-loss" claim
  conflated R3 over-*rating* exposure with map over-*envelope*
  exposure — corrected in §4.1, where the r3 round then claimed the
  convention was "mode-neutral and negligible". *KX/R23-F2 corrects
  that replacement claim in turn: it is mode-neutral at the reference
  seed only, and one-sided in mode (b)'s favour at CdA 5.4 — measured
  and bounded in §4.1.*; (iii) categorical
  "sign reversed everywhere" language overstated the CdA 5.4 ensemble,
  which is break-even. *KX/R23-F1 corrects that replacement claim in
  turn: the r3 round printed "two" where the data has @CDAPOSN@ of 8
  seeds marginally positive (seeds @CDAPOSSEEDS@) — corrected in all
  four places the phrase occurs: the headline, this §0-R entry, the §6
  table and ESC-2. (KX r2, adjudication m5: the r1 wording of this
  sentence said "the headline, §6, ESC-2 and ESC-6"; ESC-6 carries no
  seed count and the fourth occurrence is this sentence. §0-KX's list
  was the correct one, and `verify_ws4.py` now pins the phrase **per
  section**, not by total count.)* Additionally the sign's
  dependence on the declared rectifier member is now bracketed
  in-pipeline (§6): the kill outcome is invariant.
- **Directive 4 (R18 datasheet confirmation task): DONE.** §2.1 states
  precisely which 4HK1-V2C figures require procured-datasheet
  confirmation and the witnessed dyno test that substantiates the
  132 kW flat-rating if the datasheet is silent; exported at
  `interface_ws4 → v2_genset → r18_datasheet_confirmation`.
- **Secondary restatements** (all consequences of the two ruled
  corrections): reference-seed fuels (a) 19.41 → @AKG@ kg, (b) 20.72 →
  @BKG@ kg; (a) banking envelope 1.5–3.3 → @ABKMIN@–@ABKMAX@ kWh;
  (b) emergency load-follow 484–805 → @BEMMIN@–@BEMMAX@ s nominal and
  1,504–1,734 → @BEMCMIN@–@BEMCMAX@ s at CdA 5.4; (b) unserved energy
  ≤0.12 → @BUNMAX@ kWh at nominal (the R12 chain lets pure series
  complete the nominal cycle cleanly) and 0.46–0.77 →
  @BUNCMIN@–@BUNCMAX@ kWh at CdA 5.4; G1(a) ledger row §7. Unchanged
  (trace-determined): (b) over-rating exposure @BORMIN@–@BORMAX@ s
  nominal / @BORCMIN@–@BORCMAX@ s CdA 5.4; (a) exposure @AORMAX@ s.
  Unchanged (outside G1-R scope, ratified r2 record): candidates and
  the R6 corner (+0.82 kW PROVISIONAL), BSFC maps and pinned points,
  V1 start-stop, grade holds, heat-ledger seeds (except the G1(a)
  cycle-average row, which is a gate quantity).

## 0. Rework changelog (round 2 — response to FINDINGS_WS4_r1.md)

*(Historical — retained verbatim from the ratified r2 report; the gate
numbers it re-affirms are superseded by §0-R above.)*

Adjudication round 1 returned no blocking findings, two material (F1,
F2) and five minor (F3–F7): F1 ESC-5's unsupported 1.9 kWh withdrawn
(verified 0.77 kWh worst-seed); F2 the interface now exports the full
gate condition set; F3 findings-register envelopes restated per R9;
F4 standalone hot-day case added; F5 R6 corner margin labeled
PROVISIONAL; F6 two prose/data drifts fixed; F7 rating-exposure counter
extended to locked torque-fill and `run_output.txt` made byte-stable.

## 1. Assumptions

| Assumption | Value | Basis |
|---|---|---|
| Genset rating basis | **engine shaft** power, everywhere | E15 pinned down; the conservative reading, and the one WS1/R6 used (107.8/122.1 kW are shaft figures) |
| Fuel | diesel, LHV 42.8 MJ/kg, 832 g/L | EN590 class values |
| BSFC maps | **WS4-CONSTRUCTED Willans-line maps, not measured** | no public measured map exists for these exact calibrations; construction in §3, every coefficient declared in `ws4_models.py`, calibration anchors in §10 |
| **G1 traction chain (R12)** | WS2 measured inverter+motor map (`@MAPFILE@`, @MAPV@ V, WS2 round @WS2ROUND@ — the R10-window chain of record) × flat 0.97 reduction, both directions, both modes; **no scalar PE member, no `part_load_factor`**; demands beyond the map's feasible envelope reuse the boundary loss (exposure measured per condition under KX/R23-F2: mode-neutral at the reference seed, one-sided by at most @BEXPPC2@ pp in mode (b)'s favour at CdA 5.4; §4.1); locked torque-fill at marginal map loss when the spin member is active (§4.1) | R12 + G1-R directive 1a; the loader keys on WS2's exported nominal bus voltage, so any future WS2 re-export hot-swaps on re-run |
| **PM spin drag (G1-R)** | @SPINSH@ kW shaft + @SPINBUS@ kW bus charged to mode (a) while locked (WS2 export @SPINESH@ + @SPINEBUS@ kWh per VOLT-REG, round-@WS2ROUND@ vintage) | directive 1b; WS2 measured, lockup-only tax |
| Part-load derates (non-G1 sections) | WS1's ratified `part_load_factor` retained for the ratified r2 capability/V1 sections (V1 start-stop, grade holds, top speeds — outside G1-R scope); WS4 loss-model maps for both generators; load-dependent direct-path model (2.8% proportional + 0.9·(rpm/1800) kW churning) | R9; bounded rework — those numbers are ratified |
| Generator parasitic | crank-mounted PM generator spins whenever the engine spins: 1.2 kW iron/windage at 1,800 rpm charged to the engine in lockup even at zero output | topology consequence, part of the honest locked-path cost |
| Battery — archived gate | 0.97/0.97 per direction; usable 3.5 kWh (V2) / 1.5 kWh (V1) at the bus — the R8 floors; banking limited to 50 kW continuous charge (R2/R8) | WS1 convention + R8 |
| **Battery — KX/R22a run (§4-KX)** | same round-trip efficiencies; usable **@SDUSABLE6@ kWh at the bus**, WS3's DELIVERED 288s1p pack, read from WS3's interface at run time; regen-to-pack capped by WS3's R16 acceptance curve at a declared cell temperature per case; R8's bus-side power envelope measured and reported, **not** enforced (bracketed separately, §4-KX.3) | R22a + R16 + WS3 `interface_WS3.packs.V2` |
| Engine start costs | series start = 12 g; lockup re-engagement = 1.5 g (motor-synchronised bump start) | declared; identical rules in every G1 mode |
| Supervisor (WS5 preview) | causal, deterministic, tuned once, identical across seeds/modes: series start-stop hysteresis 35–75% SOC; emergency load-follow below 25% SOC; charge-bias band 55–65% SOC; lockup 65±3 km/h, clutch opens on negative wheel power | §4.1 |
| Cycle basis | VOLT-REG at GVW, 10 Hz, WS1 seeds [23,3–9]; VOLT-SUB seeds [11,3–9]; demand traces fixed, loads recomputed per sensitivity | R9 |
| Derate model | turbo+CAC diesel: none to 1,000 m then 4%/1,000 m; none to 30 °C then 1%/5 °C ⇒ factor **0.9312** at the R6 corner | class-typical ISO 3046 / SAE J1349 practice, WS4-DECLARED; **R18 blocker — §2.1** |
| Engine heat split | of (fuel − shaft): exhaust 49%, coolant+oil 38%, CAC 10%, radiation 3%; radiator package = 48% | class-typical MD diesel balance, WS4-DECLARED |
| Candidate data | production-engine figures are datasheet-class values; to be confirmed at procurement | public sources, flagged TBC; §2.1 |

**Exclusion set, restated per directive 1a (the r2 report's line-111
list shrinks; each removal documented):**

- **REMOVED — "motor spin drag at zero torque"**: now *included*,
  charged to mode (a) from WS2's measured export (directive 1b; rates
  above). The r2 parenthetical "nearly identical in both G1 modes" is
  **withdrawn** — WS2's measurement shows it is a lockup-only tax
  (unloaded spin ≠ loaded series operation), worth @SPDMIN@ pp of gate
  margin on its own (§6).
- **REMOVED — "absent from the WS1 chain convention" (the framing)**:
  moot; the WS1 scalar chain convention itself is superseded by R12
  for every G1 quantity. The traction-side scalar PE member is gone
  program-wide; the genset-side rectifier/conditioning is explicit in
  WS4's generator model and ledger.
- **Remaining exclusions (unchanged, disclosed)**: transient thermal
  states (warm engine assumed; cold-start penalties would hit both G1
  modes roughly equally but hurt V1 start-stop specifically, §5);
  DPF-regeneration fuel.

## 2. Candidates and selection

*(Ratified r2 record — unchanged by G1-R; retained for completeness.)*

Derate math to the R6 corner (45 °C, 2,000 m): every continuous rating
is multiplied by **0.9312** (altitude 0.96 × temperature 0.97). The
corner requirement is **122.1 kW shaft** (R6, locked).

### V2 (125 kW floor, R6)

| Candidate | Disp. | Peak | Continuous (SL) | At R6 corner | Margin | Mass (dry) |
|---|---|---|---|---|---|---|
| 4HK1-TC stock reference | 5.19 L | 153 kW | 130 kW | 121.1 kW | **−1.0 kW** | ~500 kg |
| **4HK1-V2C (SELECTED)** — 4HK1-TC genset recalibration | 5.19 L | 153 kW | **132 kW** | **122.9 kW** | **+0.82 kW** | ~500 kg |
| Cummins B4.5-class (downsized-from-stock) | 4.5 L | 168 kW | ~129 kW | 120.1 kW | −2.0 kW | ~390 kg |
| Isuzu 4JJ1-class (examined) | 3.0 L | 130 kW | ~110 kW | 102.4 kW | −19.7 kW | ~350 kg |

**Selection: 4HK1-V2C** — the donor's own production 4HK1-TC hardware
with a genset/continuous recalibration: continuous rating 132 kW @
2,200 rpm, torque curve reshaped to peak **750 Nm @ 1,400 rpm** (E3's
requirement made a specification — the only curve of WS1's four that
holds 6% on the direct path). Compliance status: **PROVISIONAL**
(adjudication r1 F5; R18) — the +0.82 kW corner margin rests on two
TBC figures; see §2.1. Selection reasoning unchanged from r2.

### 2.1 R18 datasheet-confirmation task (directive 4)

R18 holds two blockers on WS6 release: this confirmation and G1-R
itself. Precisely, the figures on the **4HK1-V2C** requiring
procured-datasheet confirmation are:

1. **BLOCKING — the 132 kW continuous flat-rating** @ 2,200 rpm as an
   unlimited-hours prime/COP-class rating (ISO 8528-1 / ISO 3046-1
   basis, no 10%-overload dependency). The published 4HK1-TC figures
   are automotive (153 kW peak / ~130 kW continuous-class); the 132 kW
   continuous is a WS4-proposed genset recalibration and appears on no
   public sheet.
2. **BLOCKING — the derate model in corner-delivery form** (R18's own
   label): the datasheet must state either "no derate to 2,000 m /
   +45 °C" or its derate curve. WS4 assumed 4%/1,000 m above 1,000 m
   and 1%/5 °C above 30 °C (factor 0.9312 ⇒ 122.9 kW delivered). The
   +0.82 kW margin flips if the confirmed rating is 1 kW lower or the
   slope 1%/1,000 m steeper (r1 F5).
3. Non-blocking (affect G1 margins, not the WS6 release): the 750 Nm @
   1,400 rpm torque respec on production hardware (E3); the
   Willans-constructed BSFC surface (island 203.6 / rated-continuous
   215.4 g/kWh — the gate is re-runnable on a measured map in this
   pipeline); the 10.7 kW motoring-drag anchor; the 49/38/10/3 heat
   split; ~500 kg dry mass.

**Test substantiating the 132 kW flat-rating if the datasheet is
silent** (witnessed, per ISO 3046-1 with corrections per ISO 15550 /
SAE J1349): (i) sea-level leg — 132 kW @ 2,200 rpm held continuously
to thermal steady state (coolant/oil dT/dt < 1 K per 10 min, ≥ 4 h),
fuel stop untouched, smoke/EGT/boost/coolant inside the manufacturer's
continuous limits; (ii) simulated-corner leg — inlet conditions set to
2,000 m / +45 °C equivalents (~79.5 kPa inlet depression + 45 °C cell,
or an altitude chamber), same fuel stop, acceptance = **≥ 122.1 kW
shaft sustained to steady state** (the corner-delivery form is the
requirement; the label is not the test); (iii) a third point at
~1,000 m equivalent to pin the two derate coefficients separately.
Exported machine-readably at `interface_ws4 → v2_genset →
r18_datasheet_confirmation`.

### V1 (~50 kW class, R5)

*(Unchanged r2 record: V3307-V1C selected, 76.5 km/h charge-sustain —
inside R5's sub-80 ruling; now also R18's V1 figure of record.)*

### Generators (restated on R10 — directive 1c)

Both are crank-/genset-mounted IPM PM synchronous machines with active
**SiC rectifiers on the R10 pack-native window: 662.4 V nominal,
432.0–748.8 V operating, 777.6 V 10-s transient, 1200 V-class devices**
(were 750 V-class at the superseded 370 V bus). Per R12 this
genset-side rectifier/conditioning stage lives in WS4's ledger — it is
the explicit loss model in the exported maps (iron+windage ∝ speed,
copper ∝ T², rectifier 1% + fixed), not a scalar; no PE member exists
on the traction side. Loss coefficients are carried unchanged at the
new window [WS4-DECLARED: at this fidelity the voltage change trades
conduction current for switching stress roughly evenly across a rewound
machine + 1200 V SiC stage; confirm at procurement].

- **GEN-V2 "IPM 135"**: 135 kW continuous shaft input, 155 kW peak,
  ~90 kg, η = 0.952 at the pinned series point, 1.2 kW spin loss at
  1,800 rpm. Doubles as the engine starter (ISG). `data/gen_eff_map_V2.csv`
- **GEN-V1 "IPM 60"**: 60 kW continuous input, 70 kW peak, ~48 kg,
  η = 0.939 at the pinned point. Doubles as the starter. `data/gen_eff_map_V1.csv`

**Pinned points re-placed under the restated spec: unmoved** — the
restatement changes no loss coefficient, so the re-derived points land
on the ratified coordinates (asserted in `run_ws4.py`; would move only
if procured rectifier data changes the model).

## 3. BSFC maps and operating points

*(Maps and pinned points unchanged from the ratified r2 record.)*

Three maps are published, all **WS4-CONSTRUCTED Willans-line maps**:
`data/bsfc_map_4HK1_ref.csv`, `data/bsfc_map_V2_candidate.csv`,
`data/bsfc_map_V1_candidate.csv`. Construction: η_b = η_i0 · f_N(rpm) ·
f_φ(load) · BMEP/(BMEP+FMEP), BSFC = 84.11/η_b; anchors in §10.

| Map | Island minimum | At rated continuous |
|---|---|---|
| 4HK1 reference | **205.2 g/kWh** @ 1,403 rpm / 583 Nm | — |
| 4HK1-V2C (candidate) | **203.6 g/kWh** @ 1,288 rpm / 628 Nm | **215.4 g/kWh** @ 2,200 rpm |
| V3307-V1C | **228.7 g/kWh** @ 1,301 rpm / 217 Nm | 249.3 g/kWh @ 2,200 rpm |

### Fixed series operating points (task 4)

- **V2 pinned point: 1,288 rpm / 628 Nm / 84.7 kW shaft → 80.6 kW at
  the bus, BSFC 203.6 g/kWh** — the map minimum, inside the 132 kW
  continuous rating; re-placed unmoved under the R10 rectifier
  restatement (§2).
- **V1 pinned point: 1,301 rpm / 29.5 kW shaft → 27.7 kW at the bus,
  BSFC 228.7 g/kWh** — also the map minimum.
- **Locked-path residency** (fig. 1): rpm welded to road speed,
  1,414–2,005 rpm p05–p95, median 48% load. The fuel-weighted
  effective BSFC of mode (a) over VOLT-REG is @ABSFCLO@–@ABSFCHI@
  g/kWh (now inclusive of the spin-drag energy) — a 9–10% penalty vs
  the pinned island. **This is E20's question answered with a map, and
  under the ruled chain it is fatal: §4.3.**

## 4. GATE G1-R — the direct path on trial under the ruled conventions

### 4.1 What was compared

Both modes drive the identical VOLT-REG wheel-power trace (WS1
four_numbers convention), same battery (3.5 kWh usable), same start
rules, 8 seeds ([23, 3–9]), and — per directive 1a — the identical R12
traction chain: **WS2's measured inverter+motor map
(`@MAPFILE@`, @MAPV@ V, WS2 round @WS2ROUND@) × the flat 0.97
reduction, both directions, no scalar PE member, no part-load scalar.**
Two boundary conventions, stated precisely (corrected in the G1-R
revision — the earlier draft conflated them; the first is restated
again here under KX/R23-F2): demands beyond the map's *feasible
envelope* reuse the nearest boundary loss. **That convention is
mode-neutral at the reference seed only, and it is one-sided in mode
(b)'s favour at CdA 5.4** — the r3 wording ("mode-neutral and
negligible") is withdrawn. Measured, per condition, by a counter in
`ws4_chain.py` over the identical (rpm, torque) coordinates the loss
lookup queries: at **nominal**, exposure is @BEXN@ s/cycle
(@BEXNS@ s on the stricter outside-the-envelope test), of which
@BEXNU@ s are *unlocked* samples both modes drive identically and only
@BEXNL@ s are locked; the exposed samples reach @BEXNV@ km/h. **KX r2
(adjudication m1/m2):** the r1 wording added "i.e. they are launch
samples" to that sentence — a hand-written claim its own rendered
@BEXNV@ km/h refutes — and it is withdrawn. What *is* true, and is now
measured rather than asserted, is that the bulk of the **strict** count
sits on the map's degenerate rpm = 0 column, i.e. below
@D5VCEIL@ km/h. See D5 below, now closed. At **CdA 5.4** exposure rises to @BEXC@
s/cycle (@BEXCS@ s strict) with @BEXCL@ s of it on *locked* ~94–98
km/h cruise samples reaching @BEXCV@ km/h — samples mode (a) serves on
the engine and mode (b) serves through the clamped chain, so the
convention flatters pure series there. Bounded: at most @BEXKWHC@ kWh
of over-boundary wheel energy, worth **@BEXPPC@ pp** of mode (b)'s
cycle fuel (@BEXPPC2@ pp on a hostile 2× loss gradient) at CdA 5.4 and
@BEXPPN@ pp at nominal — an order of magnitude below the ~0.05 pp the
directive characterised it as, itself two orders below the 7.58-point
shortfall, and pointing the way the r3 conclusion already pointed.
Full tables: `results_ws4.json → chain_boundary_exposure`. **D5 is
closed (KX r2, adjudication m2):** WS4's count was larger than the r3
adjudicator's independently measured 3.6–7.6 s/cycle at nominal, and
the whole gap is **one map column**. Evaluating the feasible-torque
envelope by *linear interpolation between bracketing rpm columns* — the
r3 adjudicator's implementation — gives @D5LINN@ s at nominal and
@D5LINC@ s at CdA 5.4, reproducing that adjudicator's two published
figures. WS4's strict counter instead snapped to the *nearest* rpm
column, and WS2's map grid begins at rpm = @D5RPM0COLS@ — the map's
only degenerate column, carrying exactly one feasible cell, at T = 0,
hence a **zero-width envelope**. Every motoring sample below 50 rpm (road speed under
@D5VCEIL@ km/h, the instant of a standing start) was therefore tested
against it and flagged: @D5ONRPM0N@ s/cycle at nominal, i.e. about four
fifths of the strict count. Excluding that column the nearest-column
count falls to @D5NODEGN@ s at nominal and @D5NODEGC@ s at CdA 5.4.

@D5TABLE@

Nothing moves: those samples book **zero** unbooked loss
(`unbooked_bus_kWh_linear` equals `..._locked_only`), so every pp bound
below is unchanged; what changes is that the printed *seconds* now carry
the artefact separated out.
Separately, the R3
over-*rating* counter (>150 kW motor shaft) fires @BORMIN@–@BORMAX@ s
per cycle in mode (b) (mode (a): @AORMAX@ s) — those samples lie
*inside* the map envelope (feasible to ~175–185 kW at cruise rpm) and
receive true interpolated losses; they stay energy-bookkept, not
clipped. During locked torque-fill, the fill uses the *marginal* map
loss (loss at fill torque minus no-load loss), because the spin-drag
member already charges the machine's no-load losses on those samples
(double-count fix, §0-R/§9). The genset side of both modes is WS4's
generator+rectifier model (R12; restated on R10, §2; sign-bracketed
in §6).

- **(a) locked + charge-bias load-point shifting** — locked 2.8:1 path
  above 65±3 km/h, rpm welded to road speed; charge-bias banking up to
  the min-BSFC torque (≤50 kW at the bus, R2/R8); series pinned-point
  start-stop when unlocked; clutch opens on negative wheel power.
  **Now also carries WS2's measured PM spin drag while locked
  (directive 1b): @SPINSH@ kW shaft + @SPINBUS@ kW bus** — per cycle
  that is @ASPSMIN@–@ASPSMAX@ kWh engine-side + @ASPBMIN@–@ASPBMAX@
  kWh bus-side across seeds (WS2's export scaled by each seed's actual
  locked time).
- **(b) pure series at the pinned best-BSFC point** — 84.7 kW shaft /
  80.6 kW bus at 203.6 g/kWh, SOC-hysteresis start-stop; below 25% SOC
  the engine load-follows up to the full-load curve (D2's correction,
  unchanged).
- **(b′) series load-following along the best-BSFC locus** — robustness
  check on (b), not the G1 metric.

### 4.2 Result

**Net fuel energy over VOLT-REG, (a) vs (b), 8-seed ensemble: (a)
TRAILS (b) by @MIN@% (min) / @MED@% (median) / @MAX@% (max) — the
margin is negative at every seed (governing case: @GOV@). Kill
criterion ≥5%: FAILED at the nominal condition, by @GAP@ points, with
the sign of the comparison reversed.**

Reference seed: (a) @AKG@ kg = @AL100@ L/100 km; (b) @BKG@ kg =
@BL100@ L/100 km. Mode (a) locks for @ALOCK@% of cycle time (WS1's own
lockup fraction, reproduced), banks @ABKMIN@–@ABKMAX@ kWh per cycle,
and starts the engine @ASTMIN@–@ASTMAX@ times per cycle (reference
seed: @ASTARTS23@, of which @SYNC23@ are motor-synchronised lockup
re-engagements at 1.5 g). Mode (b) spends @BEMMIN@–@BEMMAX@ s per cycle
in emergency load-follow above the pin and — under the R12 chain — now
completes the nominal cycle with **@BUNMAX@ kWh** of unserved bus
energy on every seed (at CdA 5.4: @BUNCMIN@–@BUNCMAX@ kWh on hard
seeds, fuel-corrected as before); it still demands more than the
150 kW motor rating for @BORMIN@–@BORMAX@ s per cycle (energy-bookkept,
not clipped — R3/E24; the spine remains not sized for pure series).
Mode (a)'s rating exposure is @AORMAX@ s on every seed.

Robustness: (a) trails (b′) by @ABPLO@% to @ABPHI@% as well, and (b)
and (b′) land within @BBPLO@–@BBPHI@% of each other — the pinned point
is still not a strawman, and the reversed verdict is a property of the
architecture comparison under the ruled chain, not of supervisor
tuning. Map-vintage robustness: rerunning the nominal gate on WS2's
other two exported maps gives @VCPAIR@ ensemble-min. Restated under
KX/R23-F3, computed rather than asserted: the spread across the
432–749 V exported window is **@VSPREAD@ pp**, and **@VSPREADR3@ pp**
once the superseded r3-interim figure (§0-R) is swept in — the r3
report's "under 0.6 pp" was true of the first span and not of the
second, which is what it printed. Both are trivial against a
@GAP@-point shortfall; the verdict does not depend on which map
vintage the chain uses.

### 4.3 Why the sign flipped

The r2 verdict rested on WS1's scalar electric chain: bus→wheel 0.8656
× a part-load derate — an effective ~0.84 where the traction energy
flows. R12 replaces it with what WS2 measured: no PE stage exists on
the traction side, and the inverter+motor map runs 0.93–0.96 where the
energy actually is, giving an energy-weighted bus→wheel chain of
**@ETAR12@** (map × 0.97 reduction) — the electric path is ~8 points
better than the convention G1 was first judged on. **Weighting,
restated under KX/R23-F5:** @ETAR12@ is WS2's `eta_mot_avg` × 0.97,
energy-weighted over WS2's *i-MMD* VOLT-REG run — the launch-heavy,
mostly-unlocked share the motor handles there. The **series-duty**
weighting mode (b) actually realises — wheel energy ÷ bus energy
through the same map over the full motoring trace — is **@ETASD@**
(8-seed @ETASDLO@–@ETASDHI@), i.e. **@FTWSD@ g/kWh** ideal series
fuel-to-wheel. Both are quoted because they weight different things,
and the direction matters: the r3 report used the smaller one as the
trace-weighted chain, which *understated* the series advantage.
On the cycle-share weighting, ideal series fuel-to-wheel moves from
**@FTWOLD@ → @FTWR12@
g/kWh** (203.6 / (0.952 × @ETAR12@)) — *below* mode (a)'s realised
@AWR@ g/kWh at the wheel, because the welded rpm still pays E20's
9–10% BSFC penalty (fuel-weighted @ABSFCLO@–@ABSFCHI@ g/kWh vs the
203.6 pin). The chain advantage that used to survive the BSFC penalty
(~6 points of 14) is now smaller than the penalty itself: the direct
path's 0.972 beats the electric path's ~0.90 by only ~7 points at the
wheel, the map's regen advantage credits both modes equally, and the
spin-drag member (@SPDMIN@ pp) plus the crank generator's parasitic
finish the locked path below series everywhere. Load-point shifting
cannot buy it back: banked energy redeploys at @BANKETA@ (gen × battery
round trip × map chain) ≈ @FTWR12@ g/kWh at the wheel — still almost
exactly the series wheel rate (§10 check 5), so banking remains
fuel-neutral, not a lever.

### 4.4 Recommendation *(archived — the lead executed)*

> **Disposed.** BASELINE_v3 executed the kill clause on these numbers.
> The recommendation below is retained verbatim as the record of what
> WS4 put to the lead; (iv)'s fallback caveat is superseded on its
> energy half by §4-KX (zero unserved at the delivered pack) and
> re-raised on its power half as ESC-9.

**The G1-R number is @MIN@% nominal ensemble-min against an armed ≥5%
kill criterion; per the directive, WS4 reports the number and the lead
executes or spares.** For that decision, the honest decomposition:
(i) the reversal is driven @MPDMIN@ pp by the ruled map-vs-scalar swap
and @SPDMIN@ pp by the measured spin member — both corrections were
anticipated to lean against the clutch (BASELINE_v2) and both did;
(i-bis) the *sign* of "series wins" is softer than the kill verdict:
under the most hostile genset-conditioning accounting the two modes
are break-even (@BSMIN@% min, §6 bracket) — but the ≥5% criterion
fails by ≥@BSGAP@ points under every accounting, so the gate's
disposition does not turn on the declared member;
(ii) the gate ran on the WS2 r4 chain of record — the directive's
r4-vintage contingency is closed (§0-R) and the verdict is insensitive
to map voltage across the full R10 window;
(iii) what the fuel gate no longer supports is the *fuel* case for the
clutch — the capability record is separate and unchanged (R1's cost:
no sustained 6% on the engine path off-nominal; the E3 respec's direct
band at nominal, §6); (iv) if the kill fires, ESC-5's fallback caveat
is *softened but not removed* by the R12 chain — pure series now
completes nominal VOLT-REG cleanly on the R8 floor (@BUNMAX@ kWh
unserved), but still sheds up to @BUNCMAX@ kWh at CdA 5.4 and exceeds
the R3 motor rating @BORMIN@–@BORMAX@ s per cycle (R4: the spine is
not sized for it).

## 4-KX. R22a verification — pure series V2 at the DELIVERED pack (`series_duty_v2`)

*This is the live block. Everything above it about Gate G1 is an
archived record of a decision already executed.*

### 4-KX.1 What was run, and on what

ESC-5/R22a: the archived gate ran mode (b) on the **R8 @SDFLOOR@ kWh
floor**, a buffer sized for i-MMD duty, and pure series shed energy
there on hard seeds. The directive orders the verification at the
**delivered** pack. Configuration, exhaustively:

- **Pack:** @SDUSABLE6@ kWh usable at the bus (WS3's 288s1p LTO-23
  pack), read at run time from
  `../WS3_battery/results.json → interface_WS3.packs.V2.usable_bus_kWh`
  — not transcribed. SHA-pinned.
- **Mode:** (b), pure series with the genset pinned at its best-BSFC
  point (@V2PINKW@ kW shaft / @V2PINBUS@ kW bus at @V2PINBSFC@ g/kWh),
  SOC-hysteresis start-stop, emergency load-follow below 25 % SOC.
  Mode (b′) — the same genset load-following its best-BSFC locus — is
  carried as a **companion** so R22b has both endpoints; **WS4 does
  not choose the dispatch, R22b assigns that to WS5.**
- **Emergency-band ceiling [stated explicitly, KX r2 / adjudication
  M1]:** in the emergency band the engine is capped at the
  **automotive full-load curve** (`engine.peak_power_kw() × derate ×
  0.97` = @M1AUTO@ kW × derate), **not** at the @M1CONTN@ kW continuous
  flat-rating this workstream specifies. The r1 round did not say so
  anywhere. What that permits is measured in §4-KX.3 and bracketed;
  the escalation is ESC-10.
- **Traction chain of record [KX r2 / adjudication M2]:** the live block
  now carries its own resolvable chain — `@COR_MAP@`, @COR_V@ V, WS2
  round @COR_RND@, × the flat @COR_RED@ reduction, with the map's
  SHA-256 — under `series_duty_v2 → _inputs → chain_of_record`. The r1
  round carried it only inside the **archived** `gate_g1` block, whose
  own notice forbids consuming any of its fields, so a consumer obeying
  that notice could not resolve the chain the live numbers were made
  with. The map-boundary convention's exposure travels with the live
  block too (`_inputs → boundary_convention_exposure`); on the whole
  unbooked bound it is at most @COR_TPPN@ / @COR_TPPC@ / @COR_TPPA@ pp
  of cycle fuel across the three ordered cases.
- **Payload denominator [KX r2 / adjudication M3]:** the payload
  companion is denominated on **@PAYT@ t** (@PAYKG@ kg = WS1's
  m_gvw − m_curb_operating), and that basis, its source and its
  caveat now travel in the JSON at `_inputs → payload_metric_basis`,
  not only in ESC-7's prose. It is the **pre-conversion** curb: it does
  not charge the series powertrain's mass, it is identical in all three
  cases, and the exported field is therefore exactly the per-km field
  ÷ @PAYT@. **It is not the R32 metric** — see ESC-7.
- **Cases (3):** nominal; CdA 5.4 (E13); and the 2,000 m/+45 °C corner
  — the *identical* case definition the archived gate used
  (ρ 0.8706 kg/m³, derate 0.9312, GVW, CdA 4.2, 2 kW aux). It is **not**
  the stricter R6 *rating* corner (+20 % payload, CdA 5.4, 4 kW aux),
  which sizes the engine rather than running the duty.
- **Seeds:** 8-seed VOLT-REG ensemble [23, 3–9] (R9). Every extremum
  below is an explicit min/max over that enumerated set with its
  governing seed labelled in the interface (R14).
- **Traction chain:** R12 — WS2 r4 measured map (@MAPPATHW4@, @MAPV@ V)
  × 0.97 reduction, both directions. No spin member is charged: modes
  (b)/(b′) never lock and loaded machine losses are inside the map
  (R22d). The true-*coast* member is measured separately, §4-KX.5.
- **R16 cold curves:** WS3's `regen_acceptance.csv` is consumed as the
  bus-side charge-acceptance cap on the regen path
  (`V2pack_chg_cont_kW_bus`), at a declared cell temperature per case
  (25 °C / 25 °C / 45 °C = ambient). §4-KX.4.
- **R10 window:** 662.4 V nominal, 432.0–748.8 V operating, 1200 V-class
  SiC rectifier — the generator/rectifier spec of §2, unchanged.
- **Supervisor:** the ratified simulator's, untouched. Nothing was
  tuned for this run; the hysteresis band is varied only in the
  declared sensitivity of §4-KX.6.

### 4-KX.2 Result — the ordered exports

> **Unserved bus energy is @SDUNSERVED@ kWh on every seed of every
> ordered case (all cases zero: @SDUNSALL@ — @SDUNSGOV@).** The
> delivered pack has the *energy* to run pure-series
> V2 over VOLT-REG at nominal, at CdA 5.4 and at the corner. ESC-5's
> energy-side buffer worry is closed at the delivered pack — the
> archived gate's mode (b) shed up to @SDGATEUNS@ kWh at CdA 5.4 on the
> @SDFLOOR@ kWh floor.

@SDTABLE@

Reading, case by case:

- **Nominal.** The genset is on for a fraction @SDNOMONFRAC@ of cycle
  time, starting @SDNOMSTARTS@ times per cycle — an order of magnitude calmer than the
  46–62 starts the archived gate's mode (b) made on the 3.5 kWh floor,
  because the buffer is now large enough to hold a whole hysteresis
  excursion. Above-pin *demand* runs @SDNOMAPD@ s/cycle (about a fifth
  of the cycle) worth @SDNOMAPDKWH@ kWh: the pin covers the duty on
  average and misses it in the peaks, which is exactly the shape of
  R22b's question.
- **CdA 5.4.** The hardest case for the buffer: SOC bottoms at
  @SDCDASOCMIN@ of usable, the emergency band engages @SDCDAEMERG@
  s/cycle and the engine actually runs above the pin @SDCDAAPE@
  s/cycle. Still zero unserved.
- **2,000 m/+45 °C corner.** Thin air *helps* the duty (less drag) even
  as it derates the engine: fuel energy is the lowest of the three.
  What it does not help is pack power — see below.

SOC trajectories for all @R34SOCRUNS@ ordered runs:
`figs/fig04_series_duty_soc.png` and `@SOCFILE@` (5 s decimation, every
seed and case). Full-rate **10 Hz R34 traces, one per ordered case** at
the reference seed (KX r2, adjudication m4 — r1 emitted one, for
nominal): @R34FILES@. The R34 interpretation WS4 is working to is
declared in `series_duty_v2 → _trace_files → r34_interpretation` and
flagged to the lead as **ESC-11**.

### 4-KX.3 What the run does NOT establish — the pack POWER envelope (ESC-9)

The ordered run constrains the pack's **energy**, not its **power**.
Measured and reported, not enforced: bus-side pack discharge peaks at
**@SDDISPK@ kW** against R8's restated **125 kW** bus-side discharge
envelope, and charge peaks at **@SDCHGPK@ kW** against R8's **110 kW** —
the charge peak because regen and the genset can charge the pack at the
same time. The exceedances are short (see the table) but they are real,
and the corner is the worst of them.

A second, independent qualification on the same page: WS3 declares the
R8 discharge peak **over SOC 40–90 % of nameplate** and states in the
same breath that full power below SOC 40 is *not* guaranteed ("WS5
dispatch limit"). Mapped through WS3's own end stops, that gate is
SOC @SOCGATEUS@ of *usable* — and the ordered run spends real time
below it on every case (measured off the 5 s SOC trajectories):

@SOCGATETABLE@

So the pack is asked for its largest currents in precisely the SOC
region where WS3 declines to guarantee them. WS4 does not resolve that;
it reports it.

WS4 therefore ran the obvious adversarial bracket: enforce the envelope
as a wall — discharge above the cap is unserved and booked exactly as
the buffer-empty case is, charge above the cap is shed. Note the
bracket uses R12/ES-4's ruled **125 kW** bus-side discharge figure,
which is the *more permissive* of the two numbers on the record — WS3's
own compliance gates are computed at 120 kW — so the shortfall below is
if anything understated.

@R8TABLE@

**The third exceedance, and it is this workstream's own component
(KX r2, adjudication M1).** The r1 §4-KX.3 enumerated the R3 motor
rating and the R8 pack envelope and read as a complete list. It was not.
In the emergency band the simulator caps the engine at the **automotive
full-load curve** (`p_peak_kw × derate × 0.97`, where `p_peak_kw` =
@M1AUTO@ kW is the 4HK1-TC's automotive peak, which §2.1 itself
identifies as automotive and *not* the continuous rating) — not at the
@M1CONTN@ kW continuous flat-rating WS4 specifies and R18 blocks WS6's
release on:

@M1TABLE@

Worst **@M1WORSTS@ s** per cycle above the rating (@M1WORSTGOV@), peak shaft
**@M1PEAK@ kW** — @M1PEAKPCT@ % of the continuous rating. That also
exceeds the 10 %/1 h overload an ISO 8528-1 prime rating allows, and the
generator is exposed on the same samples against its @M1GENCONT@ kW
continuous shaft input. `above_pin_engine_s` counts time above the
**pin** (@V2PINKW@ kW), not above the **rating**, and no r1 field
distinguished them. The counters
`engine_over_continuous_rating_s`/`_kWh`/`_longest_s`,
`engine_shaft_peak_kW` and `generator_over_continuous_input_s` are now
exported per seed with R14 envelopes, for **both** (b) and (b′).

This does **not** touch the zero-unserved headline: capping the engine
at its continuous rating in the emergency band leaves unserved energy at
zero on every seed of every ordered case — WS4 ran that bracket itself:
worst unserved **@M1BUNS@ kWh**, at the cost of a deeper SOC minimum
(CdA 5.4: @SDCDASOCMINMIN@ → **@M1BSOC@** of usable, @M1BSOCGOV@) and no
fuel cost at all (worst case @M1BFUEL@ %)
(`engine_continuous_rating_bracket`; ESC-10). It
is an unexported capability exposure on the component this workstream
owns, and it is escalated as **ESC-10** against R18/ESC-1, whose
+0.82 kW corner margin is a *continuous*-rating figure.

**Worst case @R8WORST@ kWh unserved, at @R8WORSTGOV@.** That is the
finding, and it is a finding, not a tuning knob: R4/E24's record — "the
spine is not sized for forced series" — extends past the R3 motor
rating to the **pack's rated bus-side power**. Pure-series V2 at the
delivered pack has the energy and, at rated power, not quite the power
on the hardest samples. Whether the answer is a dispatch rule (run the
genset earlier so the pack never has to cover the peak alone), a
higher-rated pack interface, or an accepted short-duration overload is
a WS5/WS3 question. Escalated as **ESC-9**. The R3 motor-rating exposure
(@SDNOMOR@ s/cycle at nominal, @SDCDAOR@ s at CdA 5.4) is the same
record as the archived gate's and is unchanged by the larger pack.

### 4-KX.4 R16: the curve binds nothing on the regen leg and is exceeded on the pack — both readings, measured

**KX r2 (adjudication B1). The r1 round exported one field,
`bound_any_sample: false`, that answered one of two questions and was
read as answering both. Both are now measured, each under a name that
says which it is.**

WS3's `regen_acceptance.csv` admits two readings, and on this duty they
differ *measurably*:

1. **Regen-leg rule.** WS3's REPORT_WS3 §4.2 presents the curve to WS5
   as a regen-blend rule ("regen follows the acceptance curve at all
   temperatures with the resistor as overflow"; "WS5 should drive the
   blend from it directly"). This is the reading the ordered run
   enforces.
2. **Pack rule.** The file's own header line is *"pack regen-acceptance
   vs cell temperature"* and the column is `V2pack_chg_cont_kW_bus` — a
   **pack** charge limit, bus-side. A pack cannot tell whether its
   charge current comes from regen or from the genset.

**On reading (1) nothing binds.** The curve is wired into the regen path
as the bus-side charge acceptance at the declared cell temperature:
@R16NOM@ kW at 25 °C cells (nominal, CdA 5.4) and @R16ALT@ kW at 45 °C
cells (corner). Peak regen-to-pack over the whole run is
**@R16PK@ kW bus**, so the regen leg sheds nothing: `regen_shed_by_r16_kWh` is
0.0000 kWh on every seed (`regen_leg_bound_any_sample`:
@R16LEGBOUND@).

**On reading (2) it is exceeded on every ordered case.** The r1
simulator applies the cap inside the regen branch, as a cap on the
regen leg only; the genset's output is added afterwards, at
`p_batt_bus = p_gen_elec - p_bus_load`, and was never tested against the
curve. The genset is on for a fraction @SDNOMONFRAC@ of cycle time at
nominal, so regen-while-charging is **structural** to the dispatch of
record, not incidental (across the three ordered cases the on-fraction
spans 0.482–0.685). Measured against the pack's own total charge
power (`pack_charge_bound_by_r16_any_sample`: @R16PACKBOUND@):

@R16TABLE@

Peak pack charge is **@R16PACKPK@ kW bus** (@R16PACKPKGOV@) against
@R16NOM@ / @R16ALT@ kW of continuous acceptance. **The 10-s pulse column
does not excuse these.** WS3 rates @R16PULSE25@ kW at 25 °C and
@R16PULSE45@ kW at 45 °C for 10 s — above the peak — but the longest
single excursion above the *continuous* acceptance is **@R16LONGEST@ s**
(@R16LONGESTGOV@), longer than the window that column rates
(`pulse10s_covers_the_excursions`: @R16PULSECOVERS@). The r1 round never
consulted this column; it is consulted here.

**What enforcing the pack reading costs.** WS4 ran the bracket rather
than argue the point — pack charge above the acceptance is shed:

@R16BTABLE@

Worst shed **@R16BSHED@ kWh** at @R16BSHEDGOV@, up to @R16BCLIP@ s of
clipping, fuel penalty at most **@R16BFUEL@ %** (@R16BFUELGOV@), and
**unserved bus energy stays @R16BUNS@ kWh**. So the §4-KX.2 headline
does not depend on which reading the lead rules for. Note the shed
formulation is the crudest remedy available — it discards surplus rather
than not generating it; the supervisor that instead backs the genset off
is the load-following companion (b′), which stays inside the acceptance
on every seed of every ordered case (§4-KX.6).

**WS4 does not choose the reading.** The physical quantity the curve
names is the pack's and the conservative reading is the pack one, but
the semantics of WS3's interface are WS3's and the blend order is WS5's.
The r1 round chose the permissive reading without recording that a
choice existed; that is the defect, and the choice goes to the lead.

**Where the curve would bind on temperature**, from the same curve and
this run's peak regen: below **@R16COLD@ °C** cells on the cold side, and
above **@R16HOT@ °C** cells on the hot side. The hot side is not
hypothetical — WS3's pack-loop **sizing line** holds cells at or below
**55 °C** at +45 °C ambient, and acceptance at 55 °C is **@R1655@ kW**,
*below* this run's peak regen. On the **pack** quantity the hot end is
worse by roughly a factor of two: at the 45 °C declared cells (the corner
case) the ordered run already charges at @R16PACKPKA@ kW against
@R16ALT@ kW continuous; at
50 °C the continuous curve falls to **@R1650@ kW**; and at the 55 °C loop
ceiling even the **10-s pulse** rating is **@R16PULSE55@ kW**, still
below the run's peak. Escalated as **ESC-8**, now stated on the pack
quantity; not resolved here, because the cell-temperature trajectory
belongs to WS3/WS6 and the blend order to WS5.

### 4-KX.5 R22d true-coast spin member — measured, reported, not charged

R22d: the machine is permanently geared, so its zero-torque spin drag
persists whenever the vehicle coasts *without* regen; in driving and
regenerating operation it is inside WS2's maps and must not be added
again. Measured on this run at WS2's 85 km/h point drag (@R22DW@ W
shaft + @R22DWB@ W bus) scaled linearly with road speed
[WS4-DECLARED]: true-coast exposure is only **@R22DS@ s/cycle**, and
all of it sits below the regen-blend floor at walking pace, so the
unbooked member is worth at most **@R22DPP@ pp** of cycle fuel. It is
**not** charged to fuel; the fuel numbers above are optimistic by that
amount and by nothing else on this account.

The finding for WS5 is the shape, not the size: VOLT-REG as WS1 builds
it essentially never true-coasts at speed — negative wheel power is
always at least partly captured above the blend floor — so this duty
does not exercise R22d at all. A supervisor that *chooses* to coast at
highway speed would, and R22d's guidance (prefer light regen over true
coast) is the remedy. The member is exported as
`interface_ws4 → spin_drag_operational_note_r22d` with an explicit
double-count warning, so WS5 can price the choice without
double-charging driving samples.

### 4-KX.6 Declared sensitivities

**Genset hysteresis band.** The cycling rate is the export most
sensitive to a supervisor constant, so the constant is not left
implicit. The ratified simulator's band is 0.35–0.75 of usable =
@HYSTSIM@ kWh; WS3's own allocation for V2 is @HYSTWS3@ kWh of genset
hysteresis about the 0.55 target. **KX r2 (adjudication m8): both bands
are now run over the full 8-seed ensemble**, because genset starts are a
stochastic output and R9 requires an envelope, not one draw:

@HYSTTABLE8@

The r1 reference-seed rows are retained (`hysteresis_sensitivity →
cases → <case> → ref_seed`) and reproduce unchanged:

@HYSTTABLE@

Over the ensemble the picture is the r1 picture: the tighter WS3 band
cycles the genset more and costs a little fuel; unserved energy stays
zero on both bands at every case; neither band changes any conclusion
above. WS5 owns the choice. What the r1 round could not say, and now
can, is that this holds across the ensemble rather than on seed 23.

**Load-following companion (b′), for R22b.**

**KX r2 (adjudication B2). The r1 round compared (b) and (b′) on fuel,
starts and unserved energy only — none of the three capability axes on
which R22b and ESC-9 are actually decided, and two of which are the whole
substance of ESC-9.** The companion now carries the same capability
export set as the block of record:

@SDBPTABLE2@

**Measured, mode (b′) is inside every envelope that mode (b) is outside
of, on every seed of every ordered case:**

| Capability axis | limit | mode (b), block of record | mode (b′), companion |
|---|---|---|---|
| Pack discharge peak [kW bus] | R8 125 | **@SDDISPK@ — outside** | @BPDISPK@ — inside: @BPINR8DIS@ |
| Pack charge peak [kW bus] | R8 110 | **@SDCHGPK@ — outside** | @BPCHGPK@ — inside: @BPINR8CHG@ |
| Pack charge above R16 acceptance [s] | 0 | **@R16ABOVEN@ / @R16ABOVEC@ / @R16ABOVEA@ — outside** | 0.0 on every seed: @BPINR16@ |
| Engine above its continuous rating [s] | 0 | **@M1SN@ / @M1SC@ / @M1SA@ — outside** | 0.0 on every seed: @BPINENG@ |
| Peak engine shaft [kW] | @M1CONTN@ / @M1CONTA@ by case | **@M1PEAK@** | @BPENGPK@ |

The fuel cost of that, on the paired per-case median: @BPPENN@ % at
nominal, @BPPENC@ % at CdA 5.4, @BPPENA@ % at the corner — inside the
ensemble spread at nominal and CdA 5.4, and a real penalty only at the
corner, where load-following drags the derated engine off its island.

**This is a measurement, not a recommendation.** WS4 does not choose the
dispatch; R22b assigns that to WS5, and this table does not price the
axes R22b must also weigh — start transients, aftertreatment
temperature, engine duty at part load — none of which this run models.
But ESC-9 asks the lead to rule between remedies, one of which is "run
the genset earlier so the pack never has to cover the peak alone", and
WS4's own companion demonstrates that remedy on the same trace. Saying
so is the difference between an escalation and a leading question.

### 4-KX.7 Heat to the WS6 ledger (program rule 7)

Rejected heat by component and case for the pure-series duty at the
delivered pack — these, not the archived gate's mode-(a) rows, are the
Vehicle Zero V2 rows WS6 should size against:

@SDHEATTABLE@

**KX r2 (adjudication m6): the construction of these rows is corrected.**
The r1 rows divided the 8-seed maximum *energy* by the **reference
seed's** duration, which is not the maximum of the quantity. Each row is
now the maximum of the **per-seed cycle averages** (each seed's own
energy over its own duration), and each component carries **its own**
governing seed rather than borrowing the engine-rejection seed's. Engine
rejection moves @LEDGER1N@ → **@LEDGERN@** kW at nominal, @LEDGER1C@ →
**@LEDGERC@** at CdA 5.4 and @LEDGER1A@ → **@LEDGERA@** at the corner:
the r1 rows understated the true 8-seed maximum by @LEDGERUPN@ % to
@LEDGERUPA@ %. Generator and chain rows move by the same construction.
The superseded rows are retained as a literal historical block
(`heat_ledger_ws6 → series_duty_v2_cycle_average_kx_r1_superseded`), so
this before/after is a rendering and not a transcription.

**KX r2 (adjudication m7): a cycle mean is not the case.** Program rule 7
asks for heat by component *and case*, and the r1 §4-KX.7 gave WS6 a
@LEDGER1A@ kW cycle mean for a case that carries a >200 kW transient. The
windows a cooling package is actually sized against are now exported:

@HEATTRTABLE@

Read against **R20/ESC-4's declared radiator design point of
@R20DESIGN@ kW** of HT-package duty in +45 °C air: the instantaneous
radiator-package peak exceeds it at every case, and at `alt2000m_45C` —
the only ordered case in R20's own +45 °C ambient — it reaches
**@R20ALTPEAK@ kW**. The **2-minute** rolling average there is
**@R20ALT2MIN@ kW**, which stays *under* the design point, so
**R20/ESC-4's "radiator design case = the R6 corner" survives**
(`r20_survives_on_the_2min_window`: @R20SURVIVES@) — the finding is that
the rows WS6 was pointed at could not have shown this either way.

Splits follow §7's declared 49/38/10/3 exhaust/coolant+oil/CAC/radiation
balance (radiator package = 48 %); the R22d coast-spin members
(≤0.0002 kWh/cycle) land in the traction machine on WS2's LT-loop line
and are exported per case in `heat_ledger_ws6`.

## 5. Start-stop analysis (V1)

*(Ratified r2 record — outside G1-R scope, not recomputed.)*

Start-stop at the pinned point on VOLT-SUB, R8 1.5 kWh floor, 0.8 kWh
hysteresis share: 66 starts/shift reference seed at 3.41 L/h; 8-seed
envelope **57–74 starts per 8 h shift**; 3.0 kWh usable halves it to
33 (3.37 L/h). Start-stop saves **6.2%** vs continuous load-following
(3.41 vs 3.63 L/h). Cold case (regen off, 4 kW aux): **4.83 L/h**
(+42%), duty 59%. Mitigations and ESC-3 unchanged; R19 has since
ratified the start-count disposition.

| Hysteresis share of the 1.5 kWh floor | Starts per 8 h shift (ref seed) | Fuel |
|---|---|---|
| 0.5 kWh | 116 | 3.50 L/h |
| **0.8 kWh** | **66 starts** | **3.41 L/h** |
| 1.1 kWh | 58 | 3.41 L/h |
| 3.0 kWh usable, 1.6 kWh share | **33 starts** | 3.37 L/h |

## 6. Sensitivities (G1-R condition table + one-factor attribution)

G1-R margin (a vs b), 8-seed min / median, all else nominal — same
condition table as r2, recomputed under the ruled conventions:

| Case | min | median | Reading |
|---|---|---|---|
| **Nominal (CdA 4.2, 2 kW aux, SL)** | **@MIN@%** | **@MED@%** | **FAILS the ≥5% criterion; sign reversed** |
| CdA 5.4 (E13) | **@CDAMIN@%** | @CDAMED@% | **break-even** (max @CDAMAX@%; @CDAPOSN@ of 8 seeds marginally positive — seeds @CDAPOSSEEDS@) — more road load helps the locked path to parity, nowhere near the criterion |
| Accessories 4 kW | **@AUXMIN@%** | @AUXMED@% | insensitive vs nominal |
| Hot day +45 °C, sea level | **@HOTMIN@%** | @HOTMED@% | fails (8-seed max @HOTMAX@%) |
| 2,000 m + 45 °C (R7 corner) | **@ALTMIN@%** | @ALTMED@% | **worst case** — thin air pushes the welded engine down its map, as in r2, now from a negative baseline; ESC-2 restated |
| Reference 4HK1 torque curve instead of V2C | **@REFMIN@%** | @REFMED@% | the verdict does not hinge on the E3 torque respec |

**One-factor attribution (directive 3)** — which correction moved the
gate, at nominal:

| Convention | min | median | Δ min vs prior |
|---|---|---|---|
| Prior (r2 / BASELINE_v1 scalar chain, no spin) — anchor, reproduced bit-identically | @PMIN@% | @PMED@% | — |
| + spin-drag member alone (directive 1b) | @SPMIN@% | @SPMED@% | **@SPDMIN@ pp** |
| + map-vs-scalar swap alone (directive 1a) | @MPMIN@% | @MPMED@% | **@MPDMIN@ pp** |
| **G1-R (both — the gate of record)** | **@MIN@%** | **@MED@%** | **@BODMIN@ pp** |

The map swap dominates (@MPDMIN@ pp) and alone takes the gate below
zero; the spin member alone (@SPDMIN@ pp) takes it below the criterion
but not below zero; their interaction is a further @INTMIN@ pp (min) /
@INTMED@ pp (median).
Map-vintage robustness: @VCPAIR@ ensemble-min (spin on) — the sign is
not a property of the nominal-voltage map.

**Genset-conditioning bracket (sign robustness)** — the one
declared-not-measured member the reversal's *sign* rests on is the
rectifier/conditioning model (pe0 0.15 kW + 1% of P_elec, TBC at
procurement). Two hostile readings of R12's "genset-side PE/rectifier
in WS4's ledger", run through the full 8-seed pipeline with the pinned
point re-derived under each (mode (b) pays the stressed conversion
too):

| Genset conditioning | min | median | Reading |
|---|---|---|---|
| Declared member (gate of record) | **@MIN@%** | @MED@% | series wins |
| Replaced by a 3%-class stage | @BRMIN@% | @BRMED@% | series still wins |
| WS1's 3% stage stacked on the declared member (most hostile) | @BSMIN@% | @BSMED@% | break-even (max @BSMAX@%) |

The *sign* of "series wins" carries ~1.7–2.7 pp of genset-model
uncertainty; the **kill-criterion outcome does not** — the most
hostile accounting still leaves the nominal ensemble-min @BSGAP@
points short of +5%, and the ratified +6.26% is unrecoverable under
any defensible reading. Exported at `interface_ws4 → gate_g1 →
genset_conditioning_bracket`.

R6 corner delivery (the other sensitivity set — unchanged r2 record):
derate 0.9312 ⇒ 122.9 kW vs 122.1 kW required (+0.82 kW,
PROVISIONAL/R18, §2.1). Direct-path 6% capability with the V2C curve:
band 59.4–61.6 km/h at GVW/CdA 4.2/2 kW aux; max grade 6.02%; the band
vanishes at +20% payload or CdA 5.4 (F-2). Series grade hold with the
candidate: 71.3 km/h nominal, 63.6 km/h at the full R6 corner
(reference curve max direct grade: 5.14%, no 6% capability —
WS1 §4.5 reproduced).

## 7. Heat ledger to WS6 (R9)

Split model declared in §1. Full numbers in `results_ws4.json →
heat_ledger_ws6`. All rows except the G1(a) cycle average are the
ratified r2 record (R20 seeds unchanged); the G1(a) row is a gate
quantity, restated under G1-R.

| Case | Component | kW |
|---|---|---|
| V2 grade hold (6%, 61 km/h, series, 10 min) | electrical chain — WS1 of-record | 20.2 |
| | electrical chain — WS4 maps recompute (R20 seed of record until WS2 r4 lands) | **17.9 kW** (of which generator 4.6) |
| | engine radiator package (coolant+oil+CAC) | **77.2 kW** |
| | engine exhaust | 78.8 |
| **V2 R6 corner continuous (THE radiator sizing case: 45 °C, 2,000 m, 122.9 kW shaft)** | engine radiator package | **95.0 kW** |
| | engine exhaust | **97.0 kW** |
| | generator | 4.7 |
| V2 continuous max, sea level (132 kW) | engine radiator package | 98.9 |
| V1 fixed point (29.5 kW, when running) | engine radiator package | **24.4 kW** (10.1 duty-averaged) |
| | generator | 1.8 |
| G1-R(a) VOLT-REG cycle average | engine rejection (all paths) | **@G1AREJ@ kW** |
| | generator + electric chain + direct-path losses | @G1AGEN@ + @G1ACHN@ + @G1ADIR@ |
| | PM spin drag (heat lands in the traction machine — WS2's LT-loop ledger line; fuel charged here) | @G1ASPS@ kWh/cycle shaft + @G1ASPB@ kWh/cycle bus |
| | friction brakes | @G1AFRIC@ kWh/cycle |
| 50 kW brake resistor | — | on WS2's ledger line (R2); listed to avoid a gap |

Ledger correction flagged to WS6 (ESC-4, unchanged): the radiator
design case is the R6 corner (95.0 kW in 45 °C air), not the grade
hold; R20 recorded the seeds.

**KX addition — the pure-series duty rows (R22a).** The architecture of
record after the kill is pure series, so the cycle-average rows WS6
should size the Vehicle Zero V2 loops against are these, not the
archived mode-(a) row above. Full tables in §4-KX.7 and
`heat_ledger_ws6 → series_duty_v2_*_cycle_average`:

@SDHEATTABLE@

## 8. Findings register (non-escalated)

- **F-1** *(unchanged r2)* The E3 torque respec (750 Nm @ 1,400 rpm)
  restores a direct 6% hold band of 59.4–61.6 km/h — nominal only; max
  direct grade 6.02%.
- **F-2** *(unchanged r2)* That band vanishes at +20% payload and at
  CdA 5.4 — R1's recorded cost stands off-nominal.
- **F-3** *(restated under G1-R)* Pinned-point series is within
  @BBPLO@–@BBPHI@% of best-locus series on fuel (b vs b′) — the pinned
  point is not a strawman; the G1 comparison as ruled remains fair
  under the R12 chain, and (a) trails both.
- **F-4** *(numbers unchanged — trace-determined)* Mode (b) exceeds the
  150 kW motor rating for @BORMIN@–@BORMAX@ s per cycle at nominal and
  @BORCMIN@–@BORCMAX@ s at CdA 5.4 (energy-bookkept, not clipped;
  these samples lie inside the WS2 map envelope and carry true
  interpolated losses, §4.1) — the spine is NOT sized for pure series
  (R4). Mode (a): @AORMAX@ s.
- **F-5** *(unchanged r2)* V1 cold-case fuel +42% at 59% duty (§5).
- **F-6** *(new, G1-R)* Under the R12 chain, mode (b) completes nominal
  VOLT-REG with @BUNMAX@ kWh unserved on the R8 3.5 kWh floor — the r2
  buffer-adequacy caveat against pure series is now an off-nominal
  finding only (CdA 5.4: @BUNCMIN@–@BUNCMAX@ kWh); ESC-5 restated.
- **F-7** *(new, KX/R22a)* At the delivered @SDUSABLE@ kWh pack, pure
  series completes all three ordered cases with @SDUNSERVED@ kWh
  unserved — but its bus-side pack **power** reaches @SDDISPK@ kW
  discharge / @SDCHGPK@ kW charge against R8's 125/110 kW envelope, and
  enforcing that envelope costs up to @R8WORST@ kWh of unserved energy
  at @R8WORSTGOV@ (§4-KX.3, ESC-9).
- **F-8** *(new, KX/R16; RESTATED KX r2, adjudication B1)* The R16
  charge-acceptance curve binds nothing **on the regen leg** — the leg
  the ordered run enforces (peak regen @R16PK@ kW bus vs @R16NOM@ kW
  accepted at 25 °C cells). Read as the **pack** charge limit its own
  header names, the same curve is **exceeded on every ordered case**:
  @R16ABOVEN@ / @R16ABOVEC@ / @R16ABOVEA@ s per cycle above continuous
  acceptance, longest single excursion @R16LONGEST@ s — longer than
  WS3's 10-s pulse window — peak pack charge @R16PACKPK@ kW bus, because
  regen and the genset charge the pack simultaneously. Enforcing the
  pack reading sheds at most @R16BSHED@ kWh and leaves unserved energy
  at @R16BUNS@ kWh. On temperature the curve would bind below
  @R16COLD@ °C and above @R16HOT@ °C cells, and WS3's pack-loop sizing
  ceiling of 55 °C accepts only @R1655@ kW continuous / @R16PULSE55@ kW
  for 10 s (§4-KX.4, ESC-8). *The r1 wording — "consumed and binds
  nothing at any ordered case" — is withdrawn: it was true of the
  regen leg and false of the pack.*
- **F-10** *(new, KX r2 — for WS6/R20)* The pure-series duty's engine
  rejection is @LEDGERN@ / @LEDGERC@ / @LEDGERA@ kW as a **cycle mean**
  but @HEATPKN@ / @HEATPKC@ / @HEATPKA@ kW at the **peak**, with 2-min
  rolling maxima of @HEAT2N@ / @HEAT2C@ / @HEAT2A@ kW. Through the
  declared 48 % radiator-package share the corner's 2-min figure is
  @R20ALT2MIN@ kW against R20's @R20DESIGN@ kW design point, so
  **R20/ESC-4 survives** (@R20SURVIVES@) — but the r1 ledger gave WS6
  only the cycle mean, which could not have shown that either way
  (§4-KX.7, adjudication m7).
- **F-11** *(new, KX r2 — for WS5/R22b)* The load-following companion
  (b′) is inside R8's bus-side envelope in both directions
  (@BPDISPK@ / @BPCHGPK@ kW vs 125/110), inside WS3's R16 acceptance
  read on the pack (0.0 s), and inside the engine's own continuous
  flat-rating (0.0 s, peak @BPENGPK@ kW) on **every seed of every
  ordered case**, where the pinned mode of record is outside all three.
  Fuel delta @BPPENN@ / @BPPENC@ / @BPPENA@ % on the paired per-case
  median (§4-KX.6, ESC-9, adjudication B2). Reported, not recommended.
- **F-9** *(new, KX/R23-F2; restated KX r2)* The map-boundary
  convention's exposure is @BEXN@ s/cycle at nominal (of which only
  @BEXNL@ s locked) and @BEXC@ s/cycle at CdA 5.4 (of which @BEXCL@ s
  locked, up to @BEXCV@ km/h) on the **stencil** criterion — one-sided
  in mode (b)'s favour at CdA 5.4 by at most @BEXPPC2@ pp. On the
  **strict** criterion with the map's degenerate rpm = 0
  column excluded it is @D5NODEGN@ s at nominal and @D5NODEGC@ s at
  CdA 5.4; on the r3 adjudicator's interpolated-envelope criterion,
  @D5LINN@ s and @D5LINC@ s. All three are printed because roughly four
  fifths of the r1 strict count was that one column (D5, now closed —
  adjudication m2). Immaterial to the archived verdict under every
  criterion; the r3 mode-neutrality wording is withdrawn (§4.1).

## 9. Development disclosures (in the spirit of WS1 §9)

D1–D3 from rounds 1–2 are unchanged and remain part of the record
(early lockup-start over-charging; the D2 unserved-energy defect whose
correction moved the r2 verdict; the Willans light-load recalibration).

- **D4 (G1-R — found by WS4's pre-adjudication adversarial pass and
  fixed)**: the first G1-R build charged the spin-drag member AND the
  full map loss (which includes the machine's no-load losses) on the
  ~2 min/cycle of locked torque-fill samples — a double-count against
  mode (a) worth ~0.03–0.06 pp. Fixed: fills use the marginal map loss
  when the spin member is active (§4.1). Effect of the fix: nominal
  ensemble-min −2.67 → @MIN@%. Two prose overstatements were corrected
  in the same pass (boundary-convention conflation; categorical
  sign-reversal language vs the break-even CdA 5.4 ensemble) — §0-R.
- **G1-R validation**: the refactored pipeline reproduces the r2 gate
  margins when run in the prior convention (legacy path
  float-identical; nominal ensemble statistics asserted to 1e-9 in
  `run_ws4.py`), so the G1-R shift (@BODMIN@ pp min) is attributable
  to the ruled corrections plus the disclosed D4 fix, itemised in §6.
  The spin member was validated against WS2's independent 85 km/h
  point measurement (§10 check 10); the chain interpolator reproduces
  WS2's published map cells exactly in both quadrants, with exact
  bilinear midpoints between cells, and its wheel-to-bus direction
  reproduces WS2's independently exported regen-to-bus (3.73 kWh over
  VOLT-REG) to the exported precision.
- **D5 (KX) — CLOSED in KX r2 (adjudication m2).** *r1 text: "WS4's F2
  exposure count does not equal the r3 adjudicator's, and the
  difference is definitional… flagged rather than reconciled."* It is
  now reconciled, and the reconciliation is arithmetic. WS4's strict
  counter evaluated the feasible-torque envelope at the **nearest** rpm
  column; the r3 adjudicator **interpolated linearly** between
  bracketing columns. WS2's 662 V map grid begins at
  rpm = @D5RPM0COLS@ — the map's only degenerate column, carrying
  exactly one feasible cell, at T = 0, hence a zero-width envelope — so
  under the nearest-column rule every motoring sample below 50 rpm
  (< @D5VCEIL@ km/h) is tested against nothing and flagged.
  Switching to the interpolated envelope reproduces the adjudicator's
  published figures exactly: @D5LINN@ s/cycle at nominal and @D5LINC@ s
  at CdA 5.4. Excluding the degenerate column from the nearest-column
  test gives @D5NODEGN@ s and @D5NODEGC@ s. **No exported number
  moves** — those samples book zero unbooked loss, so every pp bound is
  unchanged — but §4.1, §8 F-9 and this entry now print the artefact
  separately instead of carrying it inside "the measured exposure".
  Both counters ship (`ws4_chain.boundary_exposure_strict` and
  `boundary_exposure_strict_linear`); the reconciliation table is
  `results_ws4.json → chain_boundary_exposure → d5_reconciliation`.
- **D6 (KX) — two brackets in §4-KX were NOT ordered.** The KX
  directive's scope is exhaustive and does not ask for them: the R8
  power-envelope bracket (§4-KX.3) and the SOC-window check against
  WS3's declared discharge gate are WS4's own adversarial pass on the
  ordered run, added because the ordered "zero unserved energy" result
  rests on the pack's power envelope not being enforced and that
  assumption deserved a number rather than a caveat. They are labelled
  as brackets everywhere they appear; the ordered numbers are the
  ordered numbers. The load-following companion (b′) and the
  hysteresis sensitivity are in the same category and labelled the
  same way.
- **D7 (KX) — the R22d coast member is measured with a declared
  scaling, not a measured one.** WS2 exports point drag at 85 km/h;
  WS4 scales it linearly with road speed to price true-coast samples.
  PM iron losses grow faster than linearly with speed, so the linear
  scaling understates — but the exposure is @R22DS@ s/cycle at walking
  pace, where any scaling gives a number too small to matter
  (@R22DPP@ pp). If WS5 adopts highway coasting, the member needs
  WS2's speed dependence, not this stand-in.

## 10. First-principles sanity checks

1. **WS1 regression**: recomputing the 6%/60 km/h floor through WS1's
   own physics gives 107.81 kW — matches WS1's 107.8077950219109 to
   <0.01 kW (asserted in `run_ws4.py`).
2. **Map anchors** *(unchanged)*: island 203.6–205.2 g/kWh ⇒ η_b ≈
   0.41; rated-continuous 215.4 g/kWh; 25%/1,800 rpm ≈ 260 (published
   240–270); motoring drag at 1,706 rpm = 10.7 kW vs WS1's "~10 kW".
   Fast scalar BSFC path asserted equal to the map to <0.05 g/kWh.
3. **Chain arithmetic, restated under R12 and re-weighted under
   KX/R23-F5**: pinned 203.6 / (η_gen
   0.952 × chain @ETAR12@) = **@FTWR12@ g/kWh** ideal series
   fuel-to-wheel on WS2's i-MMD cycle-share weighting (the r2
   convention gave @FTWOLD@ g/kWh — the ruled chain is worth ~10 g/kWh
   at the wheel). On the **series-duty** weighting the same
   arithmetic gives 203.6 / (0.952 × @ETASD@) = **@FTWSD@ g/kWh**,
   which is the honest ideal for mode (b)'s own duty and sits closer
   to what the simulation delivers. The simulation's (b)
   delivers @BKG@ kg over 78.85 kWh of tractive wheel energy ≈
   @BWR@ g/kWh with buffering overheads; mode (a) delivers @AKG@ kg ≈
   @AWR@ g/kWh. @BWR@ vs @AWR@ ⇒ a @M23@% reference-seed margin — the
   reversed headline reproduced by hand from two ratios.
4. **Fuel plausibility**: @AL100@–@BL100@ L/100 km for a 6.6 t GVW box
   truck averaging 72 km/h with 6% grades sits inside the published
   15–22 L/100 km band for class 4–5 diesels on regional work (both
   modes; the ordering within the band is the gate's reversal).
5. **Load-point-shifting marginal check, restated**: banking at fixed
   rpm costs ~191 g/kWh marginal, redeployed at @BANKETA@ (0.952 gen ×
   0.97² battery × @ETAR12@ chain) ⇒ ~@FTWR12@ g/kWh at the wheel —
   almost exactly the series wheel rate. *Weighting note (KX/R23-F5):*
   @ETAR12@ is the right weighting on the redeploy side, because
   banked energy is spent on the unlocked, launch-weighted share the
   figure is averaged over; the series wheel rate it is compared
   against is the sim's realised @BWR@ g/kWh, not the ideal, so the
   comparison does not turn on which weighting the ideal uses. Banking
   remains fuel-neutral; the G1-R margin cannot be tuned upward much,
   which is why §4.3's reversal deserves belief.
6. **Grade holds, closed form** *(unchanged)*: 132 kW ⇒ 71.3 km/h on
   6% nominal; 63.6 km/h at the R6 corner.
7. **Corner heat balance** *(unchanged)*: 122.9 kW shaft at 219.6
   g/kWh ⇒ 320.9 kW fuel; 97.0 kW exhaust / 95.0 kW radiator package —
   sums close exactly.
8. **V1 start count vs WS1 E6** *(unchanged)*: models agree within
   ~10% after window-ratio scaling.
9. **G1-R regression anchor**: the prior-convention nominal reproduces
   the ratified r2 margins (@PMIN@/@PMED@/@PMAX@%) — the legacy code
   path is float-identical by construction, and the nominal ensemble
   min/median/max are asserted against the ratified values to 1e-9 in
   `run_ws4.py` before any ruled correction is applied.
10. **Spin member cross-check**: the mean locked-time shaft rate
    derived from WS2's cycle integral (@SPINSH@ kW) sits within ~4% of
    WS2's independently exported 85 km/h point drag (1.109 kW) —
    VOLT-REG's locked residency centres near 85 km/h, so the mean and
    the point should and do agree.

## 11. Interfaces (machine-readable)

Injected byte-identically from `results_ws4.json → interface_ws4`
(asserted by `verify_ws4.py`):

**Consumers, read this first.** `interface_ws4 → series_duty_v2` is the
live design-input block (`_status: live_design_input`);
`interface_ws4 → gate_g1` is an **archived record** of an executed
decision and no field of it may be consumed as a live requirement. The
live block now resolves its own chain of record — map path, voltage,
reduction, WS2 round, SHA-256 — at `series_duty_v2 → _inputs →
chain_of_record`, without reading the archived block (KX r2,
adjudication M2). Three fields answer questions that look alike and are
not: `r16_binding_analysis → regen_leg_bound_any_sample` (@R16LEGBOUND@)
is about the **regen leg** the run enforces, `pack_charge_bound_by_r16_
any_sample` (@R16PACKBOUND@) is about the **pack's total charge power**
and is the constraint ESC-8 is about, and
`fuel_energy_kWh_per_payload_tonne_km` is a companion carrying its own
`_inputs → payload_metric_basis → _caveat` and is **not** the R32
metric. `hysteresis_sensitivity` was named `hysteresis_sensitivity_ref_
seed` in KX r1; the r1 rows are preserved at `cases → <case> →
ref_seed`. §0-KX2 carries the full member-level delta.

```json
@IFACE@
```

## 12. Escalations

- **ESC-1 (cites R6)** *(unchanged r2; R18 has since adopted the
  corner-delivery form)* — R6's label vs rating-basis inconsistency
  under class-typical derates; the candidate is specified at 132 kW
  and clears the corner by +0.82 kW (PROVISIONAL, §2.1).
- **ESC-2 (cites G1, R7, R11) — RESTATED under G1-R.** The r2 ESC-2
  reported a condition-dependent PASS. Under the ruled conventions the
  gate **fails the ≥5% criterion at every condition** (§6 table),
  worst at the R7 corner (@ALTMIN@%). The r2 sentence "even where (a)
  misses the criterion it still *beats* series by ~3.8%, so the
  altitude case weakens the clutch's payback, never its sign" is
  **withdrawn on the G1-R record**: at nominal the sign is reversed on
  all eight seeds, at every other condition the ensemble-min is
  negative, and the sole exception to the reversal is CdA 5.4, where
  the ensemble is break-even (min @CDAMIN@% / max @CDAMAX@%,
  @CDAPOSN@ of 8 seeds marginally positive — seeds @CDAPOSSEEDS@). BASELINE_v2's R11 note recording the r2
  reading (and the WS5 condition-aware mode-policy remedy premised on
  it) is contradicted by these numbers — flagged to the lead for
  disposition alongside the kill decision; see ESC-6.
- **ESC-3 (cites R8, R5)** *(unchanged r2; R19 has since ratified the
  disposition)* — V1 start counts at the R8 floor; GEN-V1 specified as
  ISG either way.
- **ESC-4 (cites R9 / WS6 ledger)** *(unchanged r2; R20 recorded the
  seeds)* — radiator design case is the R6 corner, not the grade hold.
- **ESC-5 (cites R8, supports the E24/R4 record) — RESTATED under
  G1-R.** Pure series on VOLT-REG with the R8 3.5 kWh floor now needs
  @BEMMIN@–@BEMMAX@ s/cycle of emergency above-pin operation at
  nominal (@BEMCMIN@–@BEMCMAX@ s at CdA 5.4) and completes the nominal
  cycle with @BUNMAX@ kWh unserved (r2: up to 0.12 kWh); at CdA 5.4 it
  still sheds @BUNCMIN@–@BUNCMAX@ kWh on hard seeds (r2: 0.46–0.77).
  The R12 chain *softens* the fallback's buffer problem but does not
  remove it off-nominal, and the R3 rating exposure
  (@BORMIN@–@BORMAX@ s nominal) is untouched — if the kill fires, the
  V1-with-125-kW-genset still inherits R4's "spine not sized for
  forced series" record; WS1's 7.32 kWh figure remains the honest
  scale for a buffer that must also cover CdA 5.4.
  **KX disposition (R22a): the ENERGY half is CLOSED.** At the
  delivered @SDUSABLE@ kWh pack, pure series completes all three
  ordered cases with @SDUNSERVED@ kWh unserved on every seed (§4-KX).
  The POWER half is not closed and is re-raised as ESC-9; the R3 motor
  rating record is unchanged.
- **ESC-6 (new — cites R11, G1-R; for the lead's kill decision)** —
  G1-R reverses the premise on which R11 recorded the WS5 mode-policy
  remedy ("prefer series at density-derated corners"): under the ruled
  chain, series is the better fuel mode at the ensemble median of
  every tested condition except CdA 5.4 (break-even, @CDAMED@%
  median), by @MED@% at nominal up to @ALTMED@% at the corner. If the
  lead spares the clutch on non-fuel grounds (R1 capability, §6), the
  WS5 mode policy should be re-premised on the G1-R condition table —
  lockup approaches parity only where the welded load fraction is
  high (CdA 5.4), which is a *load*-aware, not altitude-aware, policy.
  If the kill executes, ESC-5's restated fallback record applies.
  Either way R11's "~3.8% even at the corner" figure should be
  corrected on the baseline record to @ALTMIN@% (sign reversed).
  **Disposed:** BASELINE_v3 executed the kill and recorded the ESC-6
  contradiction (R11's premise void, "ESC-6 accepted"). Retained as
  history.
- **ESC-7 (new — cites R32, D13/R36; for the lead) — THE VEHICLE ZERO
  METRIC IS STILL PER KM.** The KX directive orders fuel energy **per
  km** and §4-KX exports it. R32 says the payload-denominated metric
  "shall be" applied to Vehicle Zero before any Vehicle Zero result is
  described as an efficiency advantage, and R36/D13 restate that per-km
  numbers flatter. WS4 therefore exports a payload companion alongside
  every per-km figure — fuel energy per payload tonne-km at WS1's
  2.9 t payload at GVW (a WS1 *assumption*: curb 3,700 kg on a 6,600 kg
  GVW). It is a companion, not a ruler: WS4 has no ratified Vehicle
  Zero payload basis and does not invent one, and no candidate
  comparison in this report is denominated on it. The lead should
  either ratify a Vehicle Zero payload basis or hold R32 open; WS4 will
  not describe any Vehicle Zero result as an efficiency advantage on
  the per-km number.
  **RESTATED, KX r2 (adjudication M3).** Two corrections. (i) *Which
  curb the 2.9 t belongs to:* it is WS1's **pre-conversion** operating
  curb — @PAYKG@ kg of payload at GVW behind a 3,700 kg
  [WS1-ASSUMPTION] "NPR-HD chassis-cab + 16 ft dry-freight body + driver
  + full fuel/DEF". The **series conversion's** mass (WS3's pack, WS4's
  genset + generator, WS2's spine, less the deleted engine and gearbox)
  is not charged against it. A denominator that does not charge
  conversion mass cannot discharge R32, whose whole purpose — per
  D13/R36, "won 6–10 % per km and gave 6–8 % back in freight" — is to
  charge exactly that. (ii) *The prose now travels with the JSON:* the
  r1 round exported `fuel_energy_kWh_per_payload_tonne_km` with full
  R14 labels and **no** `payload_t`, basis or caveat anywhere in
  `interface_ws4`, so a machine consumer saw a payload-denominated
  metric with no denominator. `_inputs → payload_metric_basis` now
  carries the tonnage, its WS1 source, the fact that it is identical in
  all three cases, and an explicit caveat that the field is the per-km
  field ÷ @PAYT@ and is not the R32 metric. WS4 keeps the field rather
  than withdrawing it (withdrawal would silently remove an exported
  member two live consumers are reading), and denominates nothing on it.
- **ESC-8 (cites R16, R15, R2; for WS3/WS5/WS6) — RESTATED IN KX r2 ON
  THE PACK QUANTITY, AND WIDENED TO THE READING ITSELF.** *r1 form: the
  curve's hot end crosses WS3's pack-loop sizing line, stated on peak
  **regen** (@R16PK@ kW bus vs @R1655@ kW accepted at 55 °C cells).*
  That form understated its own case by roughly a factor of two, and it
  rested on a choice WS4 had made without recording that a choice
  existed (adjudication B1). Restated:

  **(a) Which quantity the curve limits.** WS3's file header says *"pack
  regen-acceptance"* and the column is `V2pack_chg_cont_kW_bus` — a
  **pack** limit; WS3's REPORT_WS3 §4.2 presents the same curve to WS5
  as a **regen-blend** rule. The r1 simulator implemented the blend
  reading, capping the regen leg only, and added the genset's output to
  the pack afterwards without testing it. On the pack quantity the
  constraint is **active on every ordered case**: @R16ABOVEN@ /
  @R16ABOVEC@ / @R16ABOVEA@ s per cycle above continuous acceptance,
  longest single excursion @R16LONGEST@ s — longer than the 10-s pulse
  window that would excuse it — peak pack charge **@R16PACKPK@ kW bus**
  against @R16NOM@ / @R16ALT@ kW accepted. A pack cannot tell where its
  charge current comes from, and the genset is on for a fraction
  @SDNOMONFRAC@ of cycle time, so this is structural to the dispatch of
  record, not incidental.

  **(b) The hot end, on the pack quantity.** At the 45 °C declared cells
  the ordered run already charges at @R16PACKPKA@ kW against @R16ALT@ kW
  continuous. At 50 °C the continuous curve falls to **@R1650@ kW**. At
  WS3's 55 °C loop ceiling the continuous rating is **@R1655@ kW** and
  even the **10-s pulse** rating is **@R16PULSE55@ kW** — still below
  this run's peak charge.

  **(c) What enforcing the pack reading costs**, measured, not asserted:
  worst shed **@R16BSHED@ kWh** at @R16BSHEDGOV@, up to @R16BCLIP@ s of
  clipping, fuel penalty at most **@R16BFUEL@ %**, and unserved bus
  energy stays **@R16BUNS@ kWh** (§4-KX.4). The §4-KX.2 headline is
  invariant under either reading.

  WS4 cannot resolve this and does not: the semantics of WS3's interface
  are WS3's, the cell-temperature trajectory is WS3/WS6's, and the blend
  order is WS5's. **Requested disposition, three parts:** (1) rule which
  quantity R16's continuous column limits — the regen leg or the pack —
  and, if the pack, whether WS5's supervisor must trim the genset or shed
  to the resistor; (2) a ruled maximum cell temperature for dispatch at
  full charge, or an explicit acceptance that hot-corner descents run on
  the resistor; (3) note that WS4's own load-following companion (b′)
  stays inside the acceptance on every seed of every ordered case
  (§4-KX.6) — reported, not recommended.
- **ESC-9 (new — cites R8 as restated by R12/ES-4, R4/E24; for
  WS5/WS3) — THE DELIVERED PACK HAS THE ENERGY, NOT THE POWER.** The
  ordered R22a run completes every case with @SDUNSERVED@ kWh unserved
  **because the pack's bus-side power envelope is not enforced**: pack
  discharge peaks at @SDDISPK@ kW against R8's 125 kW and charge at
  @SDCHGPK@ kW against R8's 110 kW. Enforced as a wall, the run sheds
  up to **@R8WORST@ kWh** at @R8WORSTGOV@ (§4-KX.3). Two aggravations
  on the same record: the bracket uses the *more permissive* 125 kW of
  the two discharge figures on the record (WS3's own compliance gates
  are at 120 kW), and the run spends @SOCGATECDA@ s/cycle at CdA 5.4
  below the SOC @SOCGATENP@-of-nameplate band over which WS3 declares
  the discharge peak at all. WS4 reports all of it
  and tunes none of it. Requested disposition: rule whether R8's bus-side
  peaks are a hard envelope (in which case WS5's dispatch must keep the
  pack off the peak, or WS3 must restate the interface rating), or
  whether short excursions of this duration are accepted — and note
  that the archived gate's mode (a) never posed this question, because
  the engine carried the peaks mechanically **on the pack axis** (in
  mode (b) the engine carries peaks too, above its own rating — see
  ESC-10; the r1 closing sentence was incomplete and is corrected here).
  This is R4/E24's "spine not sized for forced series" record extended
  from the R3 motor rating to the pack.
  **ADDED IN KX r2 (adjudication B2), without recommendation:** the
  load-following companion (b′) that this block already carried for
  R22b **satisfies R8's bus-side envelope in both directions, WS3's R16
  acceptance read on the pack, and the engine's own continuous
  flat-rating — on every seed of every ordered case** (pack discharge
  peak @BPDISPK@ kW vs 125; charge peak @BPCHGPK@ kW vs 110; 0.0 s above
  R16 acceptance; 0.0 s above the continuous rating), at a fuel delta of
  @BPPENN@ % / @BPPENC@ % / @BPPENA@ % on the paired per-case median
  (§4-KX.6). The r1 round named "run the genset earlier so the pack
  never has to cover the peak alone" as an abstract remedy and did not
  report that its own companion demonstrates it. WS4 still does not
  choose the dispatch — that is R22b's, and the table does not price
  start transients, aftertreatment temperature or part-load engine duty
  — but the lead should not be asked to rule on this without the
  measurement.

- **ESC-10 (new, KX r2 — cites R18 and ESC-1; for the lead/WS6) — THE
  GENSET RUNS ABOVE ITS OWN CONTINUOUS FLAT-RATING.** In the emergency
  band the simulator caps the engine at the **automotive** full-load
  curve (@M1AUTO@ kW × derate — the 4HK1-TC hardware figure §2.1 itself
  identifies as automotive), not at the **@M1CONTN@ kW continuous
  flat-rating** WS4 specifies. Measured over the ordered run: @M1SN@ /
  @M1SC@ / @M1SA@ s per cycle above the rating, worst @M1WORSTS@ s
  (@M1WORSTGOV@), peak shaft **@M1PEAK@ kW = @M1PEAKPCT@ %** of the
  continuous rating, and the generator exposed on the same samples
  against its @M1GENCONT@ kW continuous shaft input (§4-KX.3).
  Why it matters to the lead specifically: the 132 kW flat-rating is a
  **blocking** R18 datasheet figure and a WS6 release blocker, specified
  as an unlimited-hours prime/COP-class rating with **+0.82 kW** of
  margin at the R6 corner (ESC-1, PROVISIONAL) — and @M1PEAKPCT@ % for
  ~3 minutes also exceeds the 10 %/1 h overload an ISO 8528-1 prime
  rating allows. **This does not touch the §4-KX.2 headline:** WS4 ran
  the bracket, and with the engine held to its own continuous rating in
  the emergency band the run still completes every ordered case with
  **@M1BUNS@ kWh** unserved on every seed. What the over-rating buys is
  SOC margin, not feasibility: the CdA 5.4 SOC minimum deepens from
  @SDCDASOCMINMIN@ to @M1BSOC@ of usable, and fuel does not rise at all
  (the worst case is @M1BFUEL@ %, i.e. every ordered case burns slightly
  *less*, because the capped engine stays nearer its island).
  `engine_continuous_rating_bracket`. Requested disposition: either
  rule that short excursions to the automotive curve are accepted for a
  genset installation — in which case R18's datasheet task should
  confirm the *automotive* curve too, not only the flat-rating — or rule
  that the supervisor must hold the engine to its continuous rating, in
  which case the emergency band's ceiling is a WS5 constraint and the
  bracket above is the cost. WS4 does not choose.

- **ESC-11 (new, KX r2 — cites R34; a clarification request, for the
  lead) — WHAT "ONE TRACE PER RUN" MEANS.** R34 reads "every pipeline
  exports a 10 Hz trace file per run". This pipeline executes
  @R34ORD@ ordered mode-(b) runs plus their (b′) companions plus the
  brackets and sensitivities; the per-**simulated**-run reading would be
  ~132 MB of committed artefact for the ordered set alone, and the
  per-**pipeline**-run reading is satisfied by a single file. The r1
  round emitted one trace and asserted "one per run" without saying
  which reading it meant (adjudication m4). WS4 now **declares** the
  per-pipeline-run reading and, rather than sit on the ambiguity, emits
  @R34N@ traces — one per **ordered case** at the reference seed — so
  R34's stated consumer (the WS10 exhibit/simulator) has a full-rate
  witness of each ordered case, with all @R34SOCRUNS@ ordered runs
  covered at 5 s in `@SOCFILE@`. Requested disposition: confirm the
  reading. If the per-simulated-run reading is intended,
  `run_ws4.py`'s `R34_TRACE_ALL_ORDERED_RUNS` constant emits all
  @R34ORD@ with no other change, and the lead should say whether ~132 MB
  of trace belongs in the repository.

## 13. Artefacts in this folder

- `FINDINGS_KX_r1.md` — the adjudication this round reworks against
  (input, not a WS4 product; not modified)
- `REPORT_WS4.md` (this file, generated by `make_report_ws4.py`),
  `results_ws4.json` (every number, machine-readable; `interface_ws4`
  is the block downstream parses)
- `run_ws4.py` (single entry point), `ws4_models.py`, `ws4_sim.py`,
  `ws4_chain.py` (WS2 map chain + spin member, hot-swappable; KX adds
  the F2 boundary counters), `make_report_ws4.py`, `verify_ws4.py`
  (KX adds the R23 errata pins, including occurrence counts and a
  structural resolution check on every interface `*_file`),
  `requirements.txt`, `run_output.txt`
- `data/bsfc_map_4HK1_ref.csv`, `data/bsfc_map_V2_candidate.csv`,
  `data/bsfc_map_V1_candidate.csv` — Willans BSFC maps (labeled
  constructed)
- `data/gen_eff_map_V2.csv`, `data/gen_eff_map_V1.csv` — generator
  maps (headers carry the R10/1200 V SiC restatement)
- **R34 10 Hz traces**, @R34N@ files — one per ordered case at the
  reference seed, @TRACEROWS@ rows each, every bus-side and engine-side
  channel plus SOC: @R34FILES@. The reading of R34 these satisfy is
  declared in `series_duty_v2 → _trace_files → r34_interpretation` and
  put to the lead as ESC-11.
- `@SOCFILE@` — R22a SOC trajectories, all 8 seeds × 3 cases
  (@R34SOCRUNS@ ordered runs), 5 s decimation
- `figs/fig01_bsfc_v2.png`, `figs/fig02_g1_fuel.png` (archived-gate
  fuel by seed), `figs/fig03_v1_starts.png`,
  `figs/fig04_series_duty_soc.png` (R22a SOC trajectories)
- `KX_DIRECTIVE.md` — the lead directive this round executes (input,
  not a WS4 product); `G1R_DIRECTIVE.md` — the previous round's;
  `FINDINGS_WS4_r1.md`, `FINDINGS_WS4_r2.md`, `FINDINGS_WS4_r3.md` —
  adjudication findings (inputs to rounds 2, 3 and this one)
- Read-only imports: `../WS1_loads_duty_cycles` (cycles, physics),
  `../WS2_traction_motor` (`results.json`, `data/cycle_loss_summary.csv`,
  `data/effmap_motor_inverter_*.csv` — the R12 chain of record),
  `../WS3_battery` (`results.json` for the delivered pack,
  `regen_acceptance.csv` for the R16 curve). All SHA-256 pinned in
  `results_ws4.json → kx_input_provenance`
- `.venv/` — local Python environment (numpy, matplotlib), reproducible
  from `requirements.txt`
"""

out = BODY
for k in sorted(T, key=len, reverse=True):
    out = out.replace(f"@{k}@", T[k])
import re                                                        # noqa: E402
_left = re.findall(r"@[A-Z0-9]+@", out)
assert not _left, f"unreplaced report tokens: {_left[:10]}"
with open(os.path.join(HERE, "REPORT_WS4.md"), "w") as f:
    f.write(out)
print(f"REPORT_WS4.md written ({len(out):,} bytes)")
