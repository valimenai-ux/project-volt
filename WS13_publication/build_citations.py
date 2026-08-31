#!/usr/bin/env python3
"""WS13 citation ledger builder.

Project Volt binding rule 2: no number in a publication file is transcribed by
hand.  This script is WS13's single entry point.  It resolves every number and
every quoted phrase used in the root publication files (README.md, METHOD.md,
FINDINGS.md, LIMITATIONS.md, REPRODUCE.md) from the file that owns it, formats
it, and writes `citations.json`.

Two locator kinds:

* ``json``  -- a path into another workstream's results data file.  The raw
  value is read, then rendered with the citation's own format spec.  The
  rendered string is what must appear in the prose.
* ``line``  -- a line number in a report, findings file, baseline or log, plus
  the exact substring that must be present on that line.  Used for verdict
  counts, ruling text and status labels, which are prose facts rather than
  exported numbers.

`verify_ws13.py` re-resolves every entry from source and asserts (a) the
rendered string still matches and (b) it appears verbatim in at least one
publication file.  Nothing here is stochastic and nothing is timestamped, so
re-running reproduces `citations.json` byte for byte (binding rule 1).

Run from anywhere:  python3 WS13_publication/build_citations.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "WS13_publication")
OUT = os.path.join(HERE, "citations.json")


# --------------------------------------------------------------------------
# locator helpers
# --------------------------------------------------------------------------

_JSON_CACHE: dict[str, object] = {}
_TEXT_CACHE: dict[str, list[str]] = {}


def _load_json(rel: str):
    if rel not in _JSON_CACHE:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            _JSON_CACHE[rel] = json.load(fh)
    return _JSON_CACHE[rel]


def _load_lines(rel: str) -> list[str]:
    if rel not in _TEXT_CACHE:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            _TEXT_CACHE[rel] = fh.read().split("\n")
    return _TEXT_CACHE[rel]


def _sha256(rel: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_json(rel: str, path: list, fmt: str):
    node = _load_json(rel)
    for key in path:
        node = node[key]
    if fmt == "!raw":
        return node, json.dumps(node)
    if fmt.startswith("!json:"):
        return node, fmt[len("!json:"):].format(json.dumps(node))
    return node, fmt.format(node)


def resolve_line(rel: str, line: int, quote: str):
    lines = _load_lines(rel)
    if line < 1 or line > len(lines):
        raise AssertionError(f"{rel}: line {line} out of range (file has {len(lines)})")
    text = lines[line - 1]
    if quote not in text:
        raise AssertionError(
            f"{rel}:{line} does not contain the cited phrase.\n"
            f"  expected substring: {quote!r}\n"
            f"  line reads:         {text!r}"
        )
    return quote


# --------------------------------------------------------------------------
# the ledger
#
# id                -- stable key, used in prose footnotes as [id]
# what              -- one line saying what the number is
# rel / path / fmt  -- json locator
# rel / line/ quote -- line locator
# --------------------------------------------------------------------------

# Sources that are legitimately still being written while this publication is
# reviewed. Their hashes are recorded but are advisory; the line-and-quote check
# on each citation stays binding. Appends to a log do not move earlier lines.
LIVE_SOURCES = {"PM_LOG.md"}

WS4 = "WS4_genset/results_ws4.json"
WS8 = "WS8_semi_architecture/results_ws8.json"
WS9 = "WS9_vehicle_one_wave2/results_ws9.json"
WS11 = "WS11_vehicle_zero_ruler/results_ws11.json"

PCT2 = "{:+.2f}%"
PCT2U = "{:.2f}%"
PP2 = "{:+.2f} pp"
PPA = "{:.2f} pp"
KG = "{:,.0f} kg"
LP100 = "{:.2f} L/100 km"

NUMBERS = [
    # ---------------- Gate G1, the clutch trial (WS4) ----------------------
    ("g1_prior_min", "G1 first pass, nominal ensemble-min, superseded chain convention",
     WS4, ["interface_ws4", "gate_g1", "attribution_rows", "prior_convention", "min"], PCT2),
    ("g1r_min", "G1-R nominal ensemble-min after R12's chain correction",
     WS4, ["interface_ws4", "gate_g1", "verdict", "margin_pct_ensemble_min"], PCT2),
    ("g1r_median", "G1-R nominal ensemble median",
     WS4, ["interface_ws4", "gate_g1", "verdict", "margin_pct_ensemble_median"], PCT2),
    ("g1_criterion", "G1 pre-committed kill criterion",
     WS4, ["interface_ws4", "gate_g1", "verdict", "kill_criterion_pct"], "{:.0f}%"),
    ("g1_missed_pp", "how far G1-R missed its own criterion",
     WS4, ["interface_ws4", "gate_g1", "verdict", "missed_by_pp"], PPA),
    ("g1_map_vs_scalar_pp", "one-factor: measured maps replacing WS1's scalar chain",
     WS4, ["interface_ws4", "gate_g1", "attribution_rows", "map_vs_scalar_alone", "delta_pp_min"], PP2),
    ("g1_spin_pp", "one-factor: PM spin-drag member",
     WS4, ["interface_ws4", "gate_g1", "attribution_rows", "spin_drag_alone", "delta_pp_min"], PP2),
    ("g1_cda54_min", "G1-R at CdA 5.4, ensemble-min (the sole near-break-even case)",
     WS4, ["interface_ws4", "gate_g1", "verdict", "condition_dependence",
           "margin_pct_ensemble_min_CdA_5.4"], PCT2),
    ("g1_cda54_positive_seeds", "seeds on which the locked path beat series at CdA 5.4",
     WS4, ["interface_ws4", "gate_g1", "verdict", "condition_dependence",
           "seeds_margin_positive_n_CdA_5.4"], "{:d} of 8"),
    ("g1_alt_min", "G1-R at the 2,000 m / +45 C corner, ensemble-min",
     WS4, ["interface_ws4", "gate_g1", "verdict", "condition_dependence",
           "margin_pct_ensemble_min_at_2000m_45C"], PCT2),
    ("g1_seeds_positive", "seeds on which the locked path beat series at nominal",
     WS4, ["interface_ws4", "gate_g1", "verdict", "seeds_margin_positive_n"], "{:d} of 8"),

    # ---------------- WS11, Vehicle Zero on the honest metric --------------
    ("v1_nominal_min", "V1 Postal nominal margin, per payload tonne-km, ensemble-min",
     WS11, ["interface_ws11", "verdicts", "V1_on_VOLT-SUB", "nominal_margin_pct_min"], PCT2),
    ("v1_worst_corner", "V1 Postal worst corner (cold -10 C)",
     WS11, ["interface_ws11", "verdicts", "V1_on_VOLT-SUB", "worst_corner_margin_pct"], PCT2),
    ("v2_nominal_min", "V2 Trucker nominal margin, per payload tonne-km, ensemble-min",
     WS11, ["interface_ws11", "verdicts", "V2_on_VOLT-REG", "nominal_margin_pct_min"], PCT2),
    ("v2_worst_corner", "V2 Trucker worst corner (10 km / 6% climb)",
     WS11, ["interface_ws11", "verdicts", "V2_on_VOLT-REG", "worst_corner_margin_pct"], PCT2),
    ("v2_pessimistic_min", "V2 at the pessimistic end of all eight ruler-modelling levers",
     WS11, ["interface_ws11", "verdict_robustness", "rows", "V2_on_VOLT-REG", "pessimistic_min"], PCT2),
    ("v2_pessimistic_median", "the same row, median",
     WS11, ["interface_ws11", "verdict_robustness", "rows", "V2_on_VOLT-REG", "pessimistic_median"], PCT2),
    ("v1_pessimistic_min", "V1 at the pessimistic end of the same eight levers",
     WS11, ["interface_ws11", "verdict_robustness", "rows", "V1_on_VOLT-SUB", "pessimistic_min"], PCT2),
    ("v2_flip_pct", "ruler-fuel error at which V2's KILL becomes a draw",
     WS11, ["interface_ws11", "ruler_fuel_flip_points", "V2_on_VOLT-REG",
            "pct_ruler_fuel_error_to_draw"], PCT2),
    ("v1_flip_pct", "ruler-fuel error at which V1 falls to the 3% bar",
     WS11, ["interface_ws11", "ruler_fuel_flip_points", "V1_on_VOLT-SUB",
            "pct_ruler_fuel_error_to_3pct_bar"], PCT2),
    ("anchor_all_years", "sourced NPR-HD in-use anchor, all model years",
     WS11, ["interface_ws11", "ruler", "anchor", "all_model_years", "l_per_100km"], LP100),
    ("anchor_era", "the same anchor restricted to the 4HK1-era subset",
     WS11, ["interface_ws11", "ruler", "anchor", "fourhk1_era", "l_per_100km"], LP100),
    ("anchor_miles", "anchor distance",
     WS11, ["interface_ws11", "ruler", "anchor", "all_model_years", "miles"], "{:,d} miles"),
    ("anchor_fuelups", "anchor fuel-ups",
     WS11, ["interface_ws11", "ruler", "anchor", "all_model_years", "fuel_ups"], "{:,d} fuel-ups"),
    ("anchor_resid_all", "model residual against the all-years anchor",
     WS11, ["interface_ws11", "ruler", "anchor", "all_model_years", "residual_vs_model_pct"], PCT2),
    ("anchor_resid_era", "model residual against the era-correct anchor",
     WS11, ["interface_ws11", "ruler", "anchor", "fourhk1_era", "residual_vs_model_pct"], PCT2),
    ("calibrate_satisfied", "whether the assignment's calibration order was satisfied",
     WS11, ["interface_ws11", "ruler", "anchor", "calibrate_order_satisfied"], "!json:calibrate_order_satisfied: {}"),
    ("ruler_model_lp100", "the modelled ruler on VOLT-SUB, 8-seed median",
     WS11, ["interface_ws11", "ruler", "l_per_100km_VOLT_SUB", "median"], LP100),
    ("v1_cold_both", "V1 cold corner with ESC-2 and ESC-4 both applied",
     WS11, ["interface_ws11", "cold_corner_pending_items", "V1_on_VOLT-SUB",
            "with_cab_heat_and_CdA_5p4_pct"], PCT2),
    ("v1_cold_cabheat_fp", "V1 cold corner with the fixed-point cab-heat member alone",
     WS11, ["cold_cab_heat_bracket", "V1_on_VOLT-SUB",
            "margin_pct_per_payload_tkm_paired", "min"], PCT2),
    ("v1_cold_cabheat_r1", "V1 cold corner on round 1's single-pass cab-heat smear",
     WS11, ["cold_cab_heat_bracket", "V1_on_VOLT-SUB",
            "margin_pct_per_payload_tkm_paired_r1_single_pass_smear", "min"], PCT2),
    ("v1_cold_no_credit", "V1 cold corner under the harshest cab-heat reading",
     WS11, ["cold_cab_heat_bracket", "V1_on_VOLT-SUB",
            "margin_pct_per_payload_tkm_paired_no_waste_heat_credit_worst", "min"], PCT2),
    ("v1_cold_ordered", "V1 cold corner exactly as ordered (the gated number)",
     WS11, ["cold_cab_heat_bracket", "V1_on_VOLT-SUB", "margin_ordered_corner"], PCT2),
    ("payload_ruler", "stock NPR-HD payload at 6,600 kg GVW",
     WS11, ["interface_ws11", "masses", "payload_at_gvw_kg", "ruler"], KG),
    ("payload_v1", "V1 Postal payload at the same GVW",
     WS11, ["interface_ws11", "masses", "payload_at_gvw_kg", "V1"], KG),
    ("payload_v2", "V2 Trucker payload at the same GVW",
     WS11, ["interface_ws11", "masses", "payload_at_gvw_kg", "V2"], KG),
    ("curb_v1", "V1 Postal operating curb",
     WS11, ["interface_ws11", "masses", "curb_kg", "V1"], KG),
    ("curb_v2", "V2 Trucker operating curb",
     WS11, ["interface_ws11", "masses", "curb_kg", "V2"], KG),
    ("curb_ruler", "stock NPR-HD operating curb",
     WS11, ["interface_ws11", "masses", "curb_kg", "ruler"], KG),
    ("v2_breakeven_curb", "the curb at which V2 would exactly draw",
     WS11, ["interface_ws11", "break_even_curb_kg", "V2_on_VOLT-REG", "worst"], KG),
    ("v2_breakeven_headroom", "V2's distance from its own break-even curb",
     WS11, ["interface_ws11", "break_even_curb_kg", "V2_on_VOLT-REG", "headroom_kg_worst"],
     "{:+,.0f} kg"),
    ("v1_breakeven_headroom", "V1's distance from its own break-even curb",
     WS11, ["interface_ws11", "break_even_curb_kg", "V1_on_VOLT-SUB", "headroom_kg_worst"],
     "{:+,.0f} kg"),
    ("v2_perkm_min", "V2 per-kilometre margin, paired per-seed, ensemble-min",
     WS11, ["one_factor", "rows", "V2_on_VOLT-REG", "mass_payload_denominator",
            "margin_pct_per_km_min"], PCT2),
    ("v2_mass_cost_pp", "freight V2 gives back, in margin points",
     WS11, ["one_factor", "rows", "V2_on_VOLT-REG", "mass_payload_denominator", "cost_pp"], PPA),
    ("v1_perkm_min", "V1 per-kilometre margin, paired per-seed, ensemble-min",
     WS11, ["one_factor", "rows", "V1_on_VOLT-SUB", "mass_payload_denominator",
            "margin_pct_per_km_min"], PCT2),
    ("v1_mass_cost_pp", "freight V1 gives back, in margin points",
     WS11, ["one_factor", "rows", "V1_on_VOLT-SUB", "mass_payload_denominator", "cost_pp"], PPA),
    ("v1_regen_pp", "what regen alone is worth to V1 on VOLT-SUB",
     WS11, ["one_factor", "rows", "V1_on_VOLT-SUB", "regen", "worth_pp"], PPA),
    ("v1_engineoff_pp", "what engine-off alone is worth to V1 vs a load-following genset",
     WS11, ["one_factor", "rows", "V1_on_VOLT-SUB", "start_stop_engine_off", "worth_pp"], PPA),
    ("v1_oppoint_pp", "what the pinned operating point alone is worth to V1 (upper bound)",
     WS11, ["one_factor", "rows", "V1_on_VOLT-SUB", "engine_operating_point", "worth_pp"], PPA),
    ("v2_regen_pp", "what regen alone is worth to V2 on VOLT-REG",
     WS11, ["one_factor", "rows", "V2_on_VOLT-REG", "regen", "worth_pp"], PPA),
    ("v2_engineoff_pp", "what engine-off alone is worth to V2 vs a load-following genset",
     WS11, ["one_factor", "rows", "V2_on_VOLT-REG", "start_stop_engine_off", "worth_pp"], PPA),
    ("v1_sustained_6pct", "V1's sustained speed on a 6% grade with no buffer contribution",
     WS11, ["interface_ws11", "sustained_6pct_capability_kmh", "V1"], "{:.2f} km/h"),
    ("ruler_sustained_6pct", "the ruler's sustained speed on the same grade",
     WS11, ["interface_ws11", "sustained_6pct_capability_kmh", "ruler"], "{:.2f} km/h"),
    ("v2_unserved", "worst unserved bus energy on V2's governing corner",
     WS11, ["interface_ws11", "capability_and_limit_worst_case", "V2_on_VOLT-REG",
            "candidate_worst_unserved_bus_kWh"], "{:.4f} kWh"),
    ("ws4_seam", "WS11's hot-swap assertion against WS4's exported series duty",
     WS11, ["interface_ws11", "ws4_hot_swap_seam", "max_abs_difference"], "{:.1e}"),

    # ---------------- WS8, Vehicle One wave one ---------------------------
    ("s0_fleet_lp100", "the Class 8 ruler's fleet-mission consumption, 8-seed median",
     WS8, ["headline", "s0_fleet_L_per_100km"], LP100),
    ("ws8_bar_nominal", "WS8/WS9 pre-committed advance bar at nominal",
     WS8, ["interface_ws8", "advance_kill", "nominal_pct"], "{:.0f}%"),
    ("ws8_bar_corner", "WS8/WS9 pre-committed corner bar",
     WS8, ["interface_ws8", "advance_kill", "every_corner_pct"], "{:.0f}%"),
    ("s1_min", "S1 pure series, fleet mission per payload tonne-km, ensemble-min",
     WS8, ["headline", "table", 1, "margin_vs_S0_pct_min"], PCT2),
    ("s1_med", "S1 median", WS8, ["headline", "table", 1, "margin_vs_S0_pct_median"], PCT2),
    ("s2_min", "S2 single cruise ratio + torque-fill, ensemble-min",
     WS8, ["headline", "table", 2, "margin_vs_S0_pct_min"], PCT2),
    ("s2_med", "S2 median", WS8, ["headline", "table", 2, "margin_vs_S0_pct_median"], PCT2),
    ("s3_min", "S3 tandem split, ensemble-min",
     WS8, ["headline", "table", 3, "margin_vs_S0_pct_min"], PCT2),
    ("s3_med", "S3 median", WS8, ["headline", "table", 3, "margin_vs_S0_pct_median"], PCT2),
    ("s4_min", "S4 range-extended BEV, ensemble-min",
     WS8, ["headline", "table", 4, "margin_vs_S0_pct_min"], PCT2),
    ("s4_med", "S4 median", WS8, ["headline", "table", 4, "margin_vs_S0_pct_median"], PCT2),
    ("s1_perkm_min", "S1 per-kilometre margin, paired per-seed, ensemble-min",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S1",
           "ensemble", "min"], PCT2),
    ("s2_perkm_min", "S2 per-kilometre margin, paired per-seed, ensemble-min",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S2",
           "ensemble", "min"], PCT2),
    ("s3_perkm_min", "S3 per-kilometre margin, paired per-seed, ensemble-min",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S3",
           "ensemble", "min"], PCT2),
    ("s4_perkm_min", "S4 per-kilometre margin, paired per-seed, ensemble-min",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S4",
           "ensemble", "min"], PCT2),
    ("s2_perkm_max", "S2 per-kilometre margin, ensemble-max (top of the per-km band)",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S2",
           "ensemble", "max"], PCT2),
    ("s3_wins_every_seed", "whether S3 wins per km on every seed at r3",
     WS8, ["interface_ws8", "per_km_margin_paired", "corners", "nominal", "S3",
           "wins_on_every_seed"], "!json:wins_on_every_seed = {}"),
    ("payload_s0", "Class 8 ruler payload at 36,300 kg GCW",
     WS8, ["headline", "table", 0, "payload_kg"], KG),
    ("payload_s1", "S1 payload", WS8, ["headline", "table", 1, "payload_kg"], KG),
    ("payload_s2", "S2 payload", WS8, ["headline", "table", 2, "payload_kg"], KG),
    ("payload_s3", "S3 payload", WS8, ["headline", "table", 3, "payload_kg"], KG),
    ("payload_s4", "S4 payload", WS8, ["headline", "table", 4, "payload_kg"], KG),
    ("gcw", "Vehicle One gross combination weight",
     WS8, ["interface_ws8", "gcw_kg"], KG),
    ("ratio_ceiling", "highest single ratio that keeps the engine under its rpm ceiling at 105 km/h",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_ceiling_closed_form", "value"],
     "{:.4f}"),
    ("ratio_needed", "lowest single ratio that holds the 6% grade at GCW",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_needed_to_hold_6pct", "ratio"],
     "{:.2f}"),
    ("ratio_rpm_over", "how far over the rpm ceiling that ratio puts the engine at 105 km/h",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_needed_to_hold_6pct",
           "over_ceiling_by_rpm"], "{:,.0f} rpm"),
    ("ratio_any_feasible", "whether any swept single ratio satisfies both constraints",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "any_feasible"], "!json:any_feasible = {}"),
    ("whr_gate", "the pre-committed waste-heat-recovery gate",
     WS8, ["interface_ws8", "whr_gate", "threshold_pct"], "{:.1f}%"),
    ("whr_s1", "best WHR system on S1, net of its mass charge, ensemble-min",
     WS8, ["interface_ws8", "whr_gate", "best_net_margin_pct", "S1"], PCT2),
    ("whr_s2", "best WHR system on S2, net of its mass charge, ensemble-min",
     WS8, ["interface_ws8", "whr_gate", "best_net_margin_pct", "S2"], PCT2),
    ("whr_s3", "best WHR system on S3, net of its mass charge, ensemble-min",
     WS8, ["interface_ws8", "whr_gate", "best_net_margin_pct", "S3"], PCT2),
    # -- M2: the two archived G1 attribution rows and their paired companions --
    ("g1_map_construction", "how the archived map-vs-scalar row is constructed, in its own field",
     WS4, ["interface_ws4", "gate_g1", "attribution_rows", "map_vs_scalar_alone",
           "delta_pp_min_governing_case"], "{}"),
    ("g1_map_paired", "the paired companion of that row, exported outside the archive",
     WS4, ["construction_sweep_kx_r3", "gate_g1_one_factor_paired_companion",
           "map_vs_scalar_alone", "paired_delta_pp_min"], PP2),
    ("g1_spin_paired", "the paired companion of the spin-drag row",
     WS4, ["construction_sweep_kx_r3", "gate_g1_one_factor_paired_companion",
           "spin_drag_alone", "paired_delta_pp_min"], PP2),

    # -- M3: declared constants and requirement strings the prose renders -----
    ("gvw_kg", "Vehicle Zero gross vehicle weight",
     WS11, ["interface_ws11", "masses", "gvw_kg"], KG),
    ("v_cruise", "the cruise speed the Class 8 ratio ceiling is solved at",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_ceiling_closed_form",
           "v_cruise_kmh"], "{:.0f} km/h"),
    ("rpm_ceiling", "the engine rpm ceiling that bound is solved against",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_ceiling_closed_form",
           "rpm_ceiling"], "{:,.0f} rpm"),
    ("ratio_d_res", "how far a tenfold grid refinement moves the required ratio",
     WS8, ["interface_ws8", "S3_fixed_ratio_feasibility", "ratio_needed_to_hold_6pct",
           "resolution_sensitivity", "d_ratio"], "{:+.3f}"),
    ("s3_startability_req", "the regulatory startability requirement, as the workstream states it",
     WS8, ["task5_s3_specific", "regulatory_startability_adhesion", "requirement"], "{}"),

    # -- m4: the reading the harshest cab-heat figure actually belongs to -----
    ("no_credit_direction", "what the harshest cab-heat reading charges, in its own field",
     WS11, ["cold_cab_heat_bracket", "V1_on_VOLT-SUB", "no_waste_heat_credit_direction"], "{}"),

    ("s1_cold_corner", "S1's worst corner, the -10 C cold wall, ensemble-min",
     WS8, ["advance_kill", "candidates", "S1", "worst_corner_margin_pct_min"], PCT2),
    ("s1_gradeheavy", "the same candidate on the grade-heavy corner, ensemble-min",
     WS8, ["advance_kill", "candidates", "S1", "corners", 2, "min"], PCT2),
    ("ws8_fleet_mix", "the fleet mission the Class 8 metric of record is read on",
     WS8, ["interface_ws8", "metric_of_record"], "{}"),
    ("ws8_r_dyn", "the tyre radius the ratio ceiling is solved at",
     WS8, ["interface_ws8", "vehicle", "r_dyn_m"], "{:.1f} m"),
    ("mu_single_axle", "adhesion S3's single driven axle needs at 12% startability",
     WS8, ["task5_s3_specific", "regulatory_startability_adhesion", "rows", 0,
           "mu_required_single_axle"], "{:.3f}"),
    ("mu_tandem", "what a 6x4 tandem needs for the same start",
     WS8, ["task5_s3_specific", "regulatory_startability_adhesion", "rows", 0,
           "mu_required_tandem"], "{:.3f}"),

    # ---------------- WS9, Vehicle One wave two ---------------------------
    ("s6_design", "S6 zero-mass stack on the grade-heavy design duty, ensemble-min",
     WS9, ["headline", "table", 3, "design_margin_pct_min"], PCT2),
    ("s6_control", "S6 on the flat line-haul control duty, ensemble-min",
     WS9, ["headline", "table", 3, "control_margin_pct_min"], PCT2),
    ("s4p_design", "S4' range-extended BEV on the design duty, ensemble-min",
     WS9, ["headline", "table", 5, "design_margin_pct_min"], PCT2),
    ("s4p_control", "S4' on the control duty, ensemble-min",
     WS9, ["headline", "table", 5, "control_margin_pct_min"], PCT2),
    ("s513_design", "S5-13L minimal transmission on the design duty, ensemble-min",
     WS9, ["headline", "table", 2, "design_margin_pct_min"], PCT2),
    ("s513_control", "S5-13L on the control duty, ensemble-min",
     WS9, ["headline", "table", 2, "control_margin_pct_min"], PCT2),
    ("s7_design", "S7 motorised trailer axle on the design duty, ensemble-min",
     WS9, ["headline", "table", 4, "design_margin_pct_min"], PCT2),
    ("s7_control", "S7 on the control duty, ensemble-min",
     WS9, ["headline", "table", 4, "control_margin_pct_min"], PCT2),
    ("s5_design", "S5 as ordered (11 L) on the design duty, ensemble-min",
     WS9, ["headline", "table", 1, "design_margin_pct_min"], PCT2),
    ("s5_control", "S5 as ordered (11 L) on the control duty, ensemble-min",
     WS9, ["headline", "table", 1, "control_margin_pct_min"], PCT2),
    ("payload_s0r", "the wave-two ruler's payload, retarder mass charged",
     WS9, ["headline", "table", 0, "payload_kg"], KG),
    ("payload_s6", "S6 payload (nothing added)",
     WS9, ["headline", "table", 3, "payload_kg"], KG),
    ("payload_s513", "S5-13L payload", WS9, ["headline", "table", 2, "payload_kg"], KG),
    ("payload_s7", "S7 payload", WS9, ["headline", "table", 4, "payload_kg"], KG),
    ("payload_s4p", "S4' payload", WS9, ["headline", "table", 5, "payload_kg"], KG),
    ("etc_gate", "the pre-committed waste-heat gate on the design duty",
     WS9, ["etc_gate", "gate", "threshold_pct"], "{:.1f}%"),
    ("etc_min", "electric turbocompound on the design duty, net of mass, ensemble-min",
     WS9, ["etc_gate", "by_duty", "GH-REG-165", "ensemble", "min"], PCT2),
    ("etc_mass", "the mass electric turbocompound charges",
     WS9, ["etc_gate", "mass_charge_kg"], "{:.0f} kg"),
    ("etc_needed", "gross fuel gain electric turbocompound needed to clear its gate",
     WS9, ["etc_gate", "fuel_gain_needed_to_clear_gate_pct"], PCT2U),
    ("etc_payload_penalty", "the payload electric turbocompound's mass costs",
     WS9, ["etc_gate", "payload_penalty_pct"], PCT2U),
    ("pem_design_min", "predictive energy management fitted to the ruler, design duty, ensemble-min",
     WS9, ["bracket_margins", "GH-REG-165", "S0R-PCC", "ensemble", "min"], PCT2),
    ("pem_design_med", "the same, median",
     WS9, ["bracket_margins", "GH-REG-165", "S0R-PCC", "ensemble", "median"], PCT2),
    ("pem_control_min", "the same lever on the control duty, ensemble-min",
     WS9, ["bracket_margins", "LH-520", "S0R-PCC", "ensemble", "min"], PCT2),
    ("pem_control_med", "the same, median",
     WS9, ["bracket_margins", "LH-520", "S0R-PCC", "ensemble", "median"], PCT2),
    ("wall3_11l", "steepest grade a contiguous 2-speed can hold on the 11 L engine",
     WS9, ["two_walls", "third_constraint_coupling_floor", "ENG-11L", "frontier",
           "steepest_contiguous_grade"], "{:.0%}"),
    ("wall3_13l", "steepest grade a contiguous 2-speed can hold on the 13 L engine",
     WS9, ["two_walls", "third_constraint_coupling_floor", "ENG-13L", "frontier",
           "steepest_contiguous_grade"], "{:.0%}"),
    ("wall3_floor_11l", "the 11 L low gear's coupling floor",
     WS9, ["two_walls", "third_constraint_coupling_floor", "ENG-11L", "coupling_floor_kmh"],
     "{:.1f} km/h"),
    ("wall3_floor_13l", "the 13 L low gear's coupling floor",
     WS9, ["two_walls", "third_constraint_coupling_floor", "ENG-13L", "coupling_floor_kmh"],
     "{:.1f} km/h"),
    ("duty_grade_max", "steepest grade the design duty contains, 8-seed max",
     WS9, ["duties", "GH-REG-165", "ensemble", "grade_max", "max"], "{:.2%}"),
    ("span_bound", "the ratio span a contiguous two-speed engine band allows",
     WS9, ["two_walls", "third_constraint_coupling_floor", "ENG-11L", "frontier",
           "contiguity_span_bound"], "{:.3f}"),
]

QUOTES = [
    # -------- BASELINE_v7_FREEZE: the eight claims, verbatim ---------------
    ("v7_claim1", "publishable claim 1, as v7 labels it", "BASELINE_v7_FREEZE.md", 48,
     "Electric torque-fill replaces the gearbox entirely at 6.6 t"),
    ("v7_claim1_status", "claim 1 status", "BASELINE_v7_FREEZE.md", 49,
     "(ratified, model-relative)"),
    ("v7_claim2", "publishable claim 2", "BASELINE_v7_FREEZE.md", 50,
     "The transmissionless premise has a MASS boundary between ~7 and"),
    ("v7_claim2_body", "claim 2's second line, carrying the first half of its status",
     "BASELINE_v7_FREEZE.md", 51,
     "36 t: no single ratio spans cruise and grade at 36.3 t (ratified,"),
    ("v7_claim2_status", "claim 2 status", "BASELINE_v7_FREEZE.md", 52,
     "closed-form and simulated)"),
    ("v7_claim3", "publishable claim 3", "BASELINE_v7_FREEZE.md", 53,
     "It has a DUTY boundary: the same truck wins +20% on stop-go and"),
    ("v7_claim3_status", "claim 3 status", "BASELINE_v7_FREEZE.md", 54,
     "(V1 provisional, V2 kill)"),
    ("v7_claim4", "publishable claim 4", "BASELINE_v7_FREEZE.md", 55,
     "A 2-speed under torque-fill meets a third wall"),
    ("v7_claim4_status", "claim 4 status", "BASELINE_v7_FREEZE.md", 56,
     "coupling floor vs crawl speed (provisional)"),
    ("v7_claim5", "publishable claim 5", "BASELINE_v7_FREEZE.md", 57,
     "At fixed gross weight, efficiency per added kilogram is the"),
    ("v7_claim5_status", "claim 5 status", "BASELINE_v7_FREEZE.md", 59,
     "gave 6-8% back in freight (S3 excepted) (ratified, r3 numbers)"),
    ("v7_claim6", "publishable claim 6", "BASELINE_v7_FREEZE.md", 60,
     "Waste-heat recovery is a full-load technology on a part-load duty"),
    ("v7_claim6_status", "claim 6 status", "BASELINE_v7_FREEZE.md", 61,
     "(ratified at semi scale)"),
    ("v7_claim7", "publishable claim 7", "BASELINE_v7_FREEZE.md", 62,
     "Zero-mass levers are symmetric; predictive energy management is"),
    ("v7_claim7_status", "claim 7 status", "BASELINE_v7_FREEZE.md", 63,
     "worth ~0 when the incumbent gets it too (provisional, PRE-B2)"),
    ("v7_claim8", "publishable claim 8", "BASELINE_v7_FREEZE.md", 64,
     "The method: pre-registration, pre-committed kill criteria, fresh-"),
    ("v7_claim8_disc", "claim 8's discipline list", "BASELINE_v7_FREEZE.md", 65,
     "context disk-only adjudication, three-way verification, export"),
    ("v7_claim8_rate", "claim 8's stated first-pass detection rate",
     "BASELINE_v7_FREEZE.md", 66,
     "five-for-five first-pass defect detection"),
    ("v7_claim8_status", "claim 8 status", "BASELINE_v7_FREEZE.md", 67,
     "the lead's own errors (ratified by its record)"),

    # -------- BASELINE_v7_FREEZE: freeze rules and frozen state -----------
    ("v7_r51", "R51, the mid-flight rule", "BASELINE_v7_FREEZE.md", 14,
     "Anything mid-flight at the moment of freeze completes its"),
    ("v7_r52", "R52, the status rule", "BASELINE_v7_FREEZE.md", 17,
     "Every verdict and number keeps the status it holds at freeze"),
    ("v7_r52b", "R52, second half", "BASELINE_v7_FREEZE.md", 18,
     "Nothing is promoted; nothing is quietly"),
    ("v7_r53", "R53, the cancelled Fable pass", "BASELINE_v7_FREEZE.md", 20,
     "The Fable adjudication of WS9 is CANCELLED"),
    ("v7_r54", "R54, the open frontier", "BASELINE_v7_FREEZE.md", 25,
     "WS6, WS7, WS10, Vehicle Zero wave two (R48) and Vehicle One"),
    ("v7_v1_state", "V1's frozen status", "BASELINE_v7_FREEZE.md", 31,
     "FROZEN-PROVISIONAL ADVANCE, +20.11% nominal"),
    ("v7_v1_conditions", "the four conditions V1's status is conditional on",
     "BASELINE_v7_FREEZE.md", 33,
     "conditional on R43(a)-(d) (cab heat,"),
    ("v7_v1_notrun", "that those conditions were ordered and not run",
     "BASELINE_v7_FREEZE.md", 34,
     "warm-up model, corner convention, CdA bracket), which were ordered"),
    ("v7_v2_state", "V2's frozen status", "BASELINE_v7_FREEZE.md", 35,
     "V2 Trucker: FROZEN-KILL, -7.93% headline, a draw at the"),
    ("v7_uncalibrated", "the ruler's calibration status", "BASELINE_v7_FREEZE.md", 36,
     "Ruler uncalibrated"),
    ("v7_model_relative", "the model-relative qualifier", "BASELINE_v7_FREEZE.md", 37,
     "all Vehicle Zero verdicts are model-relative"),
    ("v7_ws8_state", "WS8's frozen status", "BASELINE_v7_FREEZE.md", 38,
     "WS8 S1-S4 KILLED (final), WHR DROPPED (final); numbers"),
    ("v7_ws8_r4", "that WS8 r4 was ordered and not run", "BASELINE_v7_FREEZE.md", 39,
     "r3 adjudication not clean, r4 ordered and"),
    ("v7_ws9_state", "WS9's frozen status", "BASELINE_v7_FREEZE.md", 40,
     "WS9: S6 / S4' / S5-13L / S7 FROZEN-PROVISIONAL ADVANCE on"),
    ("v7_ws9_open", "WS9's open findings and the S5-13L expectation",
     "BASELINE_v7_FREEZE.md", 42, "findings PRE-B1..B3; S5-13L expected to convert to KILL-ON-TIME under"),
    ("v7_kx_state", "KX's frozen status", "BASELINE_v7_FREEZE.md", 43,
     "KX: NOT CONVERGED after three rounds (radiator sizing case"),
    ("v7_ws5_state", "WS5's frozen status as v7 states it", "BASELINE_v7_FREEZE.md", 44,
     "WS5: status per its packet at freeze"),
    ("v7_why", "the principal's stated reason for the freeze", "BASELINE_v7_FREEZE.md", 9,
     "The trials have mostly validated why the status quo is what it is"),

    # -------- the two facts WS11 carries and v7 does not -------------------
    ("ws11_366", "V1's governing corner under ESC-2 and ESC-4 together",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 39,
     "which take its governing corner to +3.66%"),
    ("ws11_negative", "the harshest cab-heat reading taking that corner negative",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 35,
     "the harshest one takes V1's governing corner negative"),
    ("ws11_negative_body", "the same fact stated in the corner section",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 284,
     "under the harshest cab-heat reading V1's governing corner goes NEGATIVE"),

    # -------- the defect record, one citation per first pass ---------------
    ("ws1_review", "WS1's pre-submission adversarial review",
     "WS1_loads_duty_cycles/REPORT_WS1.md", 15,
     "Seventeen defects were found and fixed and nine analysis"),
    ("ws2_r1", "WS2 round-1 adjudication verdict",
     "WS2_traction_motor/FINDINGS_WS2_r1.md", 3,
     "Verdict: no blocking findings. Two material findings (WS2-F1, WS2-F2), five minor."),
    ("ws3_r1", "WS3 round-1 adjudication verdict",
     "WS3_battery/FINDINGS_WS3_r1.md", 12,
     "Two findings of consequence (one blocking, one material), then minors."),
    ("ws4_r1", "WS4 round-1 adjudication verdict",
     "WS4_genset/FINDINGS_WS4_r1.md", 9,
     "Verdict: no blocking findings. Two material findings (F1, F2) and"),
    ("ws8_r1", "WS8 round-1 adjudication verdict",
     "WS8_semi_architecture/FINDINGS_WS8_r1.md", 7,
     "Verdict: NOT CLEAN. Two blocking findings, five material, six minor."),
    ("ws9_pre", "WS9 pre-adjudication verdict",
     "WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md", 9,
     "RESULT: NOT CLEAN. Four blocking, six material, nine minor."),
    ("ws11_r1", "WS11 round-1 adjudication verdict",
     "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md", 3,
     "Verdict on the round: NOT CLEAN"),
    ("ws8_r2", "WS8 round-2 adjudication verdict",
     "WS8_semi_architecture/FINDINGS_WS8_r2.md", 11,
     "Verdict: NOT CLEAN. One blocking, four material, seven minor."),
    ("ws8_r3", "WS8 round-3 adjudication verdict",
     "WS8_semi_architecture/FINDINGS_WS8_r3.md", 5,
     "Verdict: NOT CLEAN. Two blocking, six material, twelve minor."),
    ("ws2_notconverged", "WS2 stopped at the round cap",
     "PM_LOG.md", 45, "3 rounds exhausted, final round not clean"),
    ("kx_notconverged", "KX stopped at the round cap",
     "PM_LOG.md", 121, "3 rework rounds exhausted, final round not clean"),
    ("kx_r1_result", "KX round-1 adjudication verdict",
     "PM_LOG.md", 78, "NOT CLEAN — 2 blocking, 3 material, 8 minor"),
    ("kx_r2_result", "KX round-2 adjudication verdict",
     "PM_LOG.md", 95, "NOT CLEAN — 0 blocking, 3 material, 4 minor"),
    ("kx_r3_result", "KX round-3 adjudication verdict",
     "PM_LOG.md", 119, "NOT CLEAN — 1 blocking, 3 material, 6 minor"),

    # -------- the failure-modes catalogue ---------------------------------
    ("fm_partial_pmlog", "the m6 defect class reintroduced by its own fix",
     "PM_LOG.md", 95,
     "the same construction defect this very round just fixed as m6, reintroduced in three new blocks"),
    ("fm_partial_findings", "the adjudicator's own statement of the same",
     "WS4_genset/FINDINGS_KX_r2.md", 369,
     "construction defect the same round just fixed in the heat ledger under m6"),
    ("fm_partial_sweep", "what the family sweep then found that the adjudication had not named",
     "PM_LOG.md", 110,
     "found TWO MORE instances of the same defect family the adjudication had not named"),
    ("fm_statofstat", "the statistic-of-statistics finding, KX2-M3",
     "WS4_genset/FINDINGS_KX_r2.md", 321,
     "every fuel delta between paired dispatches in the new blocks is a ratio of ensemble statistics"),
    ("fm_statofstat_row", "the exported figure beside the paired one",
     "WS4_genset/FINDINGS_KX_r2.md", 345,
     "| nominal | **+0.062 %** | **+0.169 %** | +0.088 % |"),
    ("fm_r36", "R36, the doctrine correction that made the paired statistic binding",
     "BASELINE_v5.md", 19, "DOCTRINE CORRECTION (from M2). D13 is restated"),
    ("fm_r36_why", "why R36 exists", "BASELINE_v5.md", 22,
     "ratio-of-medians artifact into doctrine. Per-km claims are stated on"),
    ("fm_falseclean", "the false clean certifications, adjudicator's wording",
     "WS4_genset/FINDINGS_KX_r3.md", 47,
     "Two of the sixteen areas the construction sweep certifies as"),
    ("fm_falseclean_pmlog", "the same, in the production log",
     "PM_LOG.md", 119,
     "TWO are false, including one block that contains the very defect it certifies clean"),
    ("fm_unrun", "the unrun robustness claim that falsified a KILL's robustness",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 21,
     "the KILL's robustness claim was false"),
    ("fm_sweep_ws11", "what WS11's own sweep found beyond its adjudication",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 33,
     "six further name/construction defects, two further unrun claims and seven further statistic-of-statistics constructions found"),
    ("fm_inert_provenance", "an inherited input the report claimed and the pipeline never called",
     "WS8_semi_architecture/FINDINGS_WS8_r1.md", 12,
     "an inherited WS3 input the report states it uses and the pipeline"),
    ("fm_governing_case", "a governing case enumerated outside the ruling's own design case",
     "PM_LOG.md", 119,
     "the R20/ESC-12 analysis is enumerated over a case set that EXCLUDES R20's own declared design case"),
    ("fm_tautology", "a concordance check that could not fire",
     "PM_LOG.md", 116,
     "the concordance module cannot fire on two thirds of its fields"),
    ("fm_wrong_branch", "an exported heat-ledger row on the wrong branch of a two-band envelope",
     "PM_LOG.md", 116,
     "exported 20.1 kW total rejection against a correct engine-coupled 507.3 kW"),
    ("fm_selfratification", "the rule the foreman/adjudicator split exists to enforce",
     "PM_COWORK.md", 18,
     "You MAY NOT: ratify or reject work on its merits; resolve, soften,"),
    ("fm_selfratification2", "the same rule, second half",
     "PM_COWORK.md", 19,
     "filter, or summarize-in-place any escalation"),

    # -------- supporting figures quoted in the case study -----------------
    ("ws11_braking_share", "why regen is worth little on the regional duty",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 248,
     "braking is 5.84% of tractive energy"),
    ("ws11_aftertreatment", "the aftertreatment mass bracket excluded from V2's headline",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 170,
     "WS4's `aftertreatment_extra: 60 kg` is EXCLUDED from the headline"),
    ("ws11_cabheat_kw", "the cab-heat load the bracket charges",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 272,
     "3.0 kW of cab heat during the engine-off windows only"),
    ("ws9_corridor_speed", "the corridor speed that makes pre-boost a poor trade",
     "WS9_vehicle_one_wave2/REPORT_WS9.md", 921,
     "on a corridor averaging over 90 km/h"),
    ("d16_vz_miniature", "Vehicle Zero's version of the third wall",
     "BASELINE_v5.md", 73, "Vehicle Zero's 35 km/h"),
    ("r45_b1_size", "how much of a candidate's move the unmeasured branch carries",
     "BASELINE_v6.md", 58, "+1.64 pp of S3's move without a one-factor row"),
    ("d3_band", "the pre-registered band G1-R missed, and by how much",
     "LEAD_HANDOVER.md", 38, "pre-registered G1-R at +4 to +6% and it came in at -2.58%"),

    # -------- B1: the three rounds that returned nothing ------------------
    ("ws2_r4_clean", "WS2 round 4, a review that found nothing",
     "WS2_traction_motor/FINDINGS_WS2_r4.md", 3,
     "Verdict: no blocking or material findings."),
    ("ws3_r2_clean", "WS3 round 2, likewise",
     "WS3_battery/FINDINGS_WS3_r2.md", 48,
     "No blocking or material findings."),
    ("ws4_r2_clean", "WS4 round 2, likewise",
     "WS4_genset/FINDINGS_WS4_r2.md", 9,
     "Verdict: no blocking or material findings. No new findings of any"),

    # -------- M1: what WS2's efficiency maps actually are ------------------
    ("ws2_analytic", "the model the inverter+motor loss maps are computed from",
     "WS2_traction_motor/ws2_thermal.py", 88,
     "Analytic steady state with resistance feedback"),

    # -------- M2: the ruling that left the archived rows alone -------------
    ("g1_restraint_correct", "the round-3 adjudicator on leaving the archived rows alone",
     "PM_LOG.md", 119,
     "The r3 restraint on the ratified gate_g1_one_factor rows was confirmed CORRECT"),

    # -------- M3: verifier and determinism counts REPRODUCE renders ---------
    ("ws4_verify_count", "what WS4's verifier asserts",
     "PM_LOG.md", 113, "252 headline renderings"),
    ("ws5_verify_count", "what WS5's verifier asserts",
     "PM_LOG.md", 131, "934/934 rendered numbers verified verbatim"),
    ("ws5_determinism_count", "WS5's own determinism evidence",
     "PM_LOG.md", 131, "19 artifacts byte-for-byte"),
    ("ws9_verify_count", "what WS9's verifier asserts",
     "PM_LOG.md", 105, "verify PASS at 593 checks"),
    ("ws9_seeds", "Vehicle One's seed set",
     "PM_LOG.md", 105, "seeds 8101-8108"),
    ("ws11_verify_count", "what WS11's verifier asserts",
     "PM_LOG.md", 127, "609/609 verbatim across 16 assertion sections"),
    ("ws11_determinism", "WS11's measured byte-stability for the round of record",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 628,
     "every file byte-identical, zero differing hashes"),
    ("vz_seeds", "Vehicle Zero's two seed sets",
     "WS11_vehicle_zero_ruler/REPORT_WS11.md", 187,
     "Ensemble = 8 seeds (VOLT-REG 23,3,4,5,6,7,8,9; VOLT-SUB 11,3,4,5,6,7,8,9"),
    ("ws1_13agent", "the review WS1 ran in place of an adjudicator round",
     "WS1_loads_duty_cycles/REPORT_WS1.md", 12,
     "13-agent adversarial review: seven agents recomputed the headline numbers"),
    ("cda_provisional", "the aerodynamic bracket, and why it is a bracket",
     "BASELINE_v1.md", 17,
     "CdA 4.2 m^2 and rho 1.20 kg/m^3 are PROVISIONAL fitted values pending"),
    ("s6_bte_headroom", "how much headroom the best semi candidate's engine bet has",
     "BASELINE_v5.md", 45, "S6 is an engine bet with ~2.3 BTE points of"),
    ("ratio_2p8", "the Vehicle Zero final drive whose rationale the G1 kill voided",
     "BASELINE_v3.md", 52, "(3.571:1 motor stage x 2.8:1 final). The 2.8:1's engine-sync"),

    # -------- the frozen open findings ------------------------------------
    ("kx_radiator_v7", "the KX sizing case v7 leaves open",
     "BASELINE_v7_FREEZE.md", 44, "103.5 vs 95.0 kW)"),
    ("kx_radiator_v6", "the same case, to the figure the round measured",
     "BASELINE_v6.md", 90, "CORNER (103.522 kW two-minute maximum), not its ambient"),
    ("r45_b1", "WS8 round-3 blocking finding 1, never closed",
     "BASELINE_v6.md", 57, "B1: throttle-back branch on the pack power ceiling unmeasured,"),
    ("r45_b2", "WS8 round-3 blocking finding 2, never closed",
     "BASELINE_v6.md", 59,
     'commitment exports the instantaneous max under a "60-second" label,'),
    ("r46_preb1", "WS9 PRE-B1 as the lead recorded it",
     "BASELINE_v6.md", 68,
     "module cannot fire on 10 of 15 fields — hard-coded verdict literals"),
    ("r46_preb2", "WS9 PRE-B2 as the lead recorded it",
     "BASELINE_v6.md", 69, 'PRE-B2 (PEM "exactly 0.0" is an'),
    ("r46_preb3", "WS9 PRE-B3 as the lead recorded it",
     "BASELINE_v6.md", 70, "PRE-B3 (S5-13L 6% climb ledger row on the"),
    ("preb2_actual", "what PRE-B2 is actually about, in the findings file itself",
     "WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md", 66,
     "is a tautology of a missing key, not a measurement"),
    ("prem2_packtemp", "an unbounded pack thermal state at a gating corner",
     "WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md", 187,
     "modelled pack temperatures reach 153 °C, including at a corner that gates"),

    # -------- the closest thing to a physics catch in the record ----------
    ("escws810_lead", "the one defect the lead labelled a physics defect",
     "BASELINE_v6.md", 63,
     "ESC-WS8-10 is a PHYSICS DEFECT of record: the retard envelope never"),
    ("escws810_effect", "what that defect does to every simulated descent",
     "BASELINE_v6.md", 65,
     "harder than the resistor can absorb — fix ordered in WS8 r4 and"),
    ("escws810_ws8", "the workstream's own statement of it, escalated not self-resolved",
     "WS8_semi_architecture/REPORT_WS8.md", 600,
     "The retard envelope does not re-solve when the buffer pack fills, so every simulated descent lets a candidate brake harder than its resistor can absorb"),

    # -------- the natural experiment --------------------------------------
    ("nx_decision", "the principal's 07:40 decision to cut two adjudication rounds",
     "PM_LOG.md", 124, "SKIP their adjudication rounds"),
    ("nx_consequence", "the consequence the foreman recorded at the time",
     "PM_LOG.md", 124,
     "WS11's round-2 rework closes 3 blocking + 8 material + 13 minor findings and NOTHING WILL HAVE CHECKED THAT WORK"),
    ("nx_gate_meaning", "what a gate pass is and is not evidence of",
     "PM_LOG.md", 124,
     "a gate PASS on r2 is evidence of reproducibility only and is NOT evidence the findings are closed"),
    ("nx_ws5", "WS5, the workstream with no adjudication round at all",
     "PM_LOG.md", 132,
     "WS5 is the only workstream of the night with ZERO adjudication rounds"),
    ("nx_number_moved", "the one number that moved in the unchecked rework",
     "PM_LOG.md", 127,
     "ONE NUMBER MOVED: V1's cold+cab-heat bracket"),

    # -------- method scaffolding -------------------------------------------
    ("d2_prereg", "D2, pre-registration in a context workers cannot read",
     "LEAD_HANDOVER.md", 30, "Pre-register acceptance bands before reading any report"),
    ("d5_baserate", "D5, the first-pass base rate as the lead recorded it",
     "LEAD_HANDOVER.md", 47, "Every first-pass adjudication in this program (WS1-WS4) found"),
    ("d5_where", "D5, where those defects lived",
     "LEAD_HANDOVER.md", 48, "material or blocking defects, almost all in interfaces, member"),
    ("d5_notphysics", "D5, and where they did not",
     "LEAD_HANDOVER.md", 49, "selection, and definitional blurs, not physics"),
    ("d1_precommit", "D1, pre-commit then measure",
     "LEAD_HANDOVER.md", 25, "Pre-commit, then measure. Every gate has a numeric kill criterion"),
    ("d1_notnegotiable", "D1, the criterion could not be negotiated with",
     "LEAD_HANDOVER.md", 28, "The criterion could not be"),
    ("d3_convention", "D3, convention swaps are level shifts",
     "LEAD_HANDOVER.md", 37, "Convention swaps are level shifts, not perturbations"),
    ("d2_private", "D2, bands kept where workers cannot read them",
     "LEAD_HANDOVER.md", 31, "keep them where workers cannot read them"),
    ("d4_ondisk", "D4, artifacts on disk are the record",
     "LEAD_HANDOVER.md", 42, "Artifacts on disk are the record; prose is not"),
    ("r14_export", "R14, the export discipline",
     "BASELINE_v2.md", 73, "EXPORT DISCIPLINE"),
    ("r14_body", "what R14 requires of every worst-case field",
     "BASELINE_v2.md", 74,
     "Every machine-readable worst-case field is computed as an"),
    ("r14_body2", "R14, second half",
     "BASELINE_v2.md", 75,
     "explicit max/min over an enumerated case set, with the governing case"),
    ("adj_mandate", "where the adjudicator's mandate comes from",
     ".claude/agents/ws-adjudicator.md", 10,
     "only what is on disk. Your mandate comes from how WS1's two blocking"),
    ("adj_mandate2", "the two WS1 defects that shaped that mandate",
     ".claude/agents/ws-adjudicator.md", 11,
     "defects were found — a wrong machine-readable interface and single-draw"),
    ("adj_never", "what the adjudicator may never do",
     ".claude/agents/ws-adjudicator.md", 38,
     "You never fix anything, never soften an escalation, never rule on one,"),
    ("adj_threeway", "the three-way verification the adjudicator performs",
     ".claude/agents/ws-adjudicator.md", 22,
     "agrees with the report prose AND the data file — three-way, verbatim."),
    ("worker_rule2", "the worker's no-hand-transcription rule",
     ".claude/agents/ws-worker.md", 25,
     "your results data file — nothing transcribed by hand."),
    ("clutch_deleted", "the moment the program killed its own premise's favourite part",
     "BASELINE_v3.md", 7, "GATE G1: EXECUTED. THE CLUTCH IS DELETED."),
    ("d20_stopgo", "D20, the duty boundary as doctrine",
     "BASELINE_v6.md", 44,
     "THE TRANSMISSIONLESS SERIES ARCHITECTURE IS A STOP-GO-DUTY"),
    ("d20_why", "D20, why the duty decides it",
     "BASELINE_v6.md", 46,
     "duty at the same mass, because regen and engine-off pay for its"),
    ("d21_ruler", "D21, why a lower-bound ruler is the wrong guarantee for a kill",
     "BASELINE_v6.md", 49, "A LOWER-BOUND RULER IS THE WRONG GUARANTEE FOR A KILL"),
    ("d21_rule", "D21, the rule it states",
     "BASELINE_v6.md", 50, "require the ruler at its unfavourable end; advances require it"),
    ("d13_perkm", "D13, per-km flatters and per-payload judges",
     "BASELINE_v4.md", 87, "Per-km efficiency flatters; per-payload judges"),
    ("d14_whr", "D14, waste-heat recovery as a full-load technology",
     "BASELINE_v4.md", 89, "Waste-heat recovery is a full-load technology; line-haul cruise"),
    ("d14_partload", "the load fraction line-haul cruise actually runs at",
     "BASELINE_v4.md", 90, "is a part-load condition (~1/3 rated)"),
    ("d15_duty", "D15, architecture is duty-indexed",
     "BASELINE_v4.md", 92, "Architecture is duty-indexed. Name the duty before the number"),
    ("d16_thirdwall", "D16, the third wall",
     "BASELINE_v5.md", 69, "THE THIRD WALL"),
    ("d17_zeromass", "D17, zero-mass levers are symmetric",
     "BASELINE_v5.md", 75, "Zero-mass levers are symmetric"),
    ("r44_modelrelative", "R44, verdicts are model-relative until hardware measures the ruler",
     "BASELINE_v6.md", 37, "Verdicts are MODEL-RELATIVE until WS7 measures a"),
    ("r44_noclaim", "R44, no external efficiency claim before that measurement",
     "BASELINE_v6.md", 39, "efficiency claim before it"),
    ("r44_cannot", "R44, why the anchor cannot calibrate",
     "BASELINE_v6.md", 37, "calibrate a cycle"),
    ("r32_order", "R32, the order that produced the honest-metric trial",
     "BASELINE_v4.md", 81,
     "Vehicle Zero consistency flag: the payload-denominated metric"),
    ("r32_order2", "R32, before any Vehicle Zero result is called an advantage",
     "BASELINE_v4.md", 84, "described as an efficiency advantage. Not executed now."),
]


def build() -> dict:
    entries = {}
    sources = set()

    for cid, what, rel, path, fmt in NUMBERS:
        if cid in entries:
            raise AssertionError(f"duplicate citation id: {cid}")
        value, display = resolve_json(rel, path, fmt)
        entries[cid] = {
            "what": what,
            "display": display,
            "value": value,
            "source": rel,
            "locator": {"kind": "json", "path": path, "format": fmt},
        }
        sources.add(rel)

    for cid, what, rel, line, quote in QUOTES:
        if cid in entries:
            raise AssertionError(f"duplicate citation id: {cid}")
        display = resolve_line(rel, line, quote)
        entries[cid] = {
            "what": what,
            "display": display,
            "value": None,
            "source": rel,
            "locator": {"kind": "line", "line": line, "quote": quote},
        }
        sources.add(rel)

    return {
        "_meta": {
            "workstream": "WS13_publication",
            "live_sources": sorted(LIVE_SOURCES),
            "live_sources_note": (
                "PM_LOG.md is the production log and is appended to by the "
                "foreman while this publication is being reviewed. Appends do "
                "not move the line numbers cited here, so verify_ws13.py treats "
                "a SHA-256 change on a live source as a WARNING and keeps the "
                "line-and-quote resolution as a hard check. Every other source "
                "is frozen and its hash is binding."
            ),
            "purpose": (
                "Every number and quoted phrase that carries a [marker] in "
                "README.md, METHOD.md, FINDINGS.md, LIMITATIONS.md and "
                "REPRODUCE.md, resolved from the file that owns it. This is the "
                "enforced set: verify_ws13.py checks a marker's value against "
                "its source, so nothing carrying a marker is transcribed by hand "
                "(CLAUDE.md rule 2). It is NOT every numeral in the prose - "
                "declared specification constants and figures restated within a "
                "sentence or two of their own cited instance are deliberately "
                "left unmarked, and the coverage claims in the publication say "
                "'carries a marker' rather than 'every number' for that reason."
            ),
            "baseline_of_record": "BASELINE_v7_FREEZE.md",
            "entry_point": "WS13_publication/build_citations.py",
            "verifier": "WS13_publication/verify_ws13.py",
            "publication_files": [
                "README.md", "METHOD.md", "FINDINGS.md",
                "LIMITATIONS.md", "REPRODUCE.md",
            ],
            "n_citations": len(entries),
            "n_numbers": len(NUMBERS),
            "n_quotes": len(QUOTES),
            "determinism": (
                "No wall-clock, no randomness, no environment dependence: "
                "re-running reproduces this file byte for byte."
            ),
        },
        "source_sha256": {rel: _sha256(rel) for rel in sorted(sources)},
        "citations": {k: entries[k] for k in sorted(entries)},
    }


INDEX = os.path.join(HERE, "CITATIONS.md")

INDEX_HEADER = """# CITATIONS — the publication's number ledger

Generated by `WS13_publication/build_citations.py` from the files that own the
numbers. Do not edit by hand; edit the builder and re-run it.

Every marker of the form `[id]` in `README.md`, `METHOD.md`, `FINDINGS.md`,
`LIMITATIONS.md` and `REPRODUCE.md` resolves to a row below.
`WS13_publication/verify_ws13.py` re-resolves every row from its source, asserts
the rendered string still matches, and asserts that the rendered string appears
in the prose immediately before its marker. No number in the publication is
transcribed by hand (CLAUDE.md rule 2).

`json` rows cite a results data file and a path into it. `line` rows cite a
report, findings file, baseline or log, a line number, and the substring that
must be on that line.

| id | as printed | what it is | source | locator |
|---|---|---|---|---|
"""


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def write_index(ledger: dict) -> None:
    rows = []
    for cid, entry in ledger["citations"].items():
        loc = entry["locator"]
        if loc["kind"] == "json":
            locator = "`" + ".".join(str(k) for k in loc["path"]) + "`"
        else:
            locator = "line " + str(loc["line"])
        rows.append("| `{}` | `{}` | {} | `{}` | {} |".format(
            cid, _cell(entry["display"]), _cell(entry["what"]),
            entry["source"], _cell(locator)))
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(INDEX_HEADER)
        fh.write("\n".join(rows))
        fh.write("\n")


def main() -> int:
    ledger = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    write_index(ledger)
    meta = ledger["_meta"]
    print(f"citations.json + CITATIONS.md written: {meta['n_citations']} citations "
          f"({meta['n_numbers']} numbers, {meta['n_quotes']} quotes) "
          f"over {len(ledger['source_sha256'])} source files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
