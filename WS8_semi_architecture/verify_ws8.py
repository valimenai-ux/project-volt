#!/usr/bin/env python3
"""
Project Volt - WS8. Verifies that every headline number in REPORT_WS8.md is
exactly the rendering of the corresponding value in results_ws8.json - that
nothing was transcribed by hand (CLAUDE.md rule 2) - and that the report's
machine-readable interface block is byte-identical to
results_ws8.json -> interface_ws8.

    ../.venv/bin/python verify_ws8.py        (exit 0 = verified)

Structure follows WS4's verify_ws4.py, which is the program's pattern for
this check.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_ws8.json")))
REPORT = open(os.path.join(HERE, "REPORT_WS8.md")).read()


def get(path):
    o = R
    for k in path.split("/"):
        o = o[int(k)] if isinstance(o, list) and k.lstrip("-").isdigit() \
            else o[k]
    return o


def cand_margin(cand, corner="nominal", stat="min"):
    return f"task3_margins/{corner}/{cand}/ensemble/{stat}"


def cand_metric(cand, stat="median"):
    return (f"task3_trial/nominal/{cand}/fleet_ensemble/"
            f"MJ_per_payload_tkm/{stat}")


CHECKS = []

# --- S0 calibration (Task 2) ----------------------------------------
CHECKS += [
    ("task2_s0_calibration/fleet_L_per_100km/median", "{:.2f} L/100 km",
     "S0 fleet fuel median"),
    ("task2_s0_calibration/fleet_L_per_100km/min", "{:.2f}",
     "S0 fleet fuel min"),
    ("task2_s0_calibration/fleet_L_per_100km/max", "{:.2f}",
     "S0 fleet fuel max"),
    ("task2_s0_calibration/linehaul_L_per_100km/median", "{:.2f}",
     "S0 line-haul fuel median"),
    ("task2_s0_calibration/regional_L_per_100km/median", "{:.2f}",
     "S0 regional fuel median"),
    ("task2_s0_calibration/engine/island_bsfc_achieved_g_per_kWh",
     "{:.1f} g/kWh", "S0 island BSFC"),
    ("task2_s0_calibration/engine/island_rpm", "{:.0f} rpm",
     "S0 island rpm"),
    ("task2_s0_calibration/engine/peak_power_kW", "{:.1f} kW",
     "13 L peak power"),
    ("task2_s0_calibration/engine/eta_i0_solved", "{:.4f}",
     "solved eta_i0"),
    ("task2_s0_calibration/engine/peak_brake_thermal_efficiency", "{:.3f}",
     "peak BTE"),
]

# --- candidate table (Task 3 headline) -------------------------------
for c in ("S0", "S1", "S2", "S3", "S4"):
    CHECKS += [
        (f"task3_trial/nominal/{c}/spec/payload_kg", "{:,.0f} kg",
         f"{c} payload"),
        (f"task3_trial/nominal/{c}/spec/powertrain_mass_kg", "{:,.0f} kg",
         f"{c} powertrain mass"),
        (cand_metric(c, "median"), "{:.4f}", f"{c} MJ/payload-tkm median"),
        (cand_metric(c, "min"), "{:.4f}", f"{c} MJ/payload-tkm min"),
        (cand_metric(c, "max"), "{:.4f}", f"{c} MJ/payload-tkm max"),
    ]
for c in ("S1", "S2", "S3", "S4"):
    CHECKS += [
        (cand_margin(c, "nominal", "min"), "{:+.2f}%", f"{c} nominal min"),
        (cand_margin(c, "nominal", "median"), "{:+.2f}%",
         f"{c} nominal median"),
        (cand_margin(c, "nominal", "max"), "{:+.2f}%", f"{c} nominal max"),
    ]

# --- sensitivities (Task 5) -----------------------------------------
for corner in ("payload_plus20", "payload_minus20", "grade_heavy",
               "cold_minus10C"):
    for c in ("S1", "S2", "S3", "S4"):
        CHECKS.append((cand_margin(c, corner, "min"), "{:+.2f}%",
                       f"{c} {corner} min"))

# --- WHR gate (Task 4) ----------------------------------------------
for c in ("S1", "S2", "S3"):
    CHECKS += [
        (f"task4_whr/results/{c}/best_net_margin_pct_median", "{:+.2f}%",
         f"WHR {c} best median"),
        (f"task4_whr/results/{c}/best_net_margin_pct_min", "{:+.2f}%",
         f"WHR {c} best min"),
    ]

# --- cycles (Task 1) -------------------------------------------------
CHECKS += [
    ("task1_cycles/cycles/LH-520/ensemble/distance_km/median", "{:.1f} km",
     "LH-520 distance"),
    ("task1_cycles/cycles/LH-520/ensemble/grade_max/max", "{:.4f}",
     "LH-520 max grade"),
    ("task1_cycles/cycles/LH-520/ensemble/total_climb_m/median", "{:,.0f} m",
     "LH-520 total climb"),
    ("task1_cycles/cycles/REG-165/ensemble/distance_km/median", "{:.1f} km",
     "REG-165 distance"),
]

# --- S3 capability, the reason for its verdict -----------------------
CHECKS += [
    ("task5_s3_specific/fixed_ratio_grade_hold/max_ratio_without_overspeed",
     "{:.2f}", "S3 max ratio without overspeed (swept set)"),
    # r1 finding F12: the report must render the PHYSICS bound, not only
    # the swept-set property.
    ("task5_s3_specific/fixed_ratio_grade_hold/ratio_ceiling_closed_form/"
     "value", "{:.4f}", "S3 ratio ceiling, closed form"),
    ("task5_s3_specific/fixed_ratio_grade_hold/ratio_needed_to_hold_6pct/"
     "ratio", "{:.2f}", "S3 ratio needed to hold 6%"),
    ("interface_ws8/S3_diesel_axle_adhesion_grade_limit/value", "{:.4f}",
     "S3 adhesion grade limit"),
]

# --- r2 errata: the fields the round exists to correct ---------------
# F7: the cross-check is an ENSEMBLE, not a median.
CHECKS += [
    ("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/min",
     "{:.2f}", "S0 flat cross-check min"),
    ("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/median",
     "{:.2f}", "S0 flat cross-check median"),
    ("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/max",
     "{:.2f}", "S0 flat cross-check max"),
    ("task2_s0_calibration/flat_corridor_crosscheck/mass_cases/"
     "mass_matched_to_ICCT_19p3t_payload/L_per_100km/median", "{:.2f}",
     "S0 flat cross-check, mass-matched to the reference payload"),
    ("task2_s0_calibration/flat_corridor_crosscheck/mass_cases/"
     "EU_regulatory_40000kg_GCW/L_per_100km/median", "{:.2f}",
     "S0 flat cross-check at 40 t GCW"),
]
# F13: the climb figure is formatted from the ensemble, never a literal.
CHECKS += [
    ("task1_cycles/cycles/LH-520/ensemble/total_climb_m/min", "{:,.0f} m",
     "LH-520 climb min"),
    ("task1_cycles/cycles/LH-520/ensemble/total_climb_m/max", "{:,.0f} m",
     "LH-520 climb max"),
]
# F1: the rebuilt heat ledger's worst cases, per candidate.
for c in ("S0", "S1", "S2", "S3", "S4"):
    CHECKS += [
        (f"heat_ledger/candidates/{c}/worst_case/brake_resistor_kW/value",
         "{:.0f}", f"{c} worst resistor heat"),
        (f"heat_ledger/candidates/{c}/worst_case/engine_exhaust_kW/value",
         "{:.0f}", f"{c} worst exhaust heat"),
        (f"heat_ledger/candidates/{c}/worst_case/friction_brake_kW/value",
         "{:.0f}", f"{c} worst friction-brake heat"),
    ]
# F3/F4/F5/F6/B1: the one-factor rows every DIRECTION statement in the
# record is now generated from (r2 finding M1). All four candidates, so a
# correction that does not reach one is PROVED not to rather than said
# not to.
for row in ("r3_as_reported", "F4_reverted_credit_removed",
            "F6_reverted_peak_point_pricing",
            "F3_reverted_engine_dual_use", "F5_reverted_spin_rule",
            "F3_and_F5_reverted", "B1_reverted_brake_and_fuel",
            "R3_S0_launch_fuel_reverted"):
    for c in ("S1", "S2", "S3", "S4"):
        CHECKS.append((f"one_factor/rows/{row}/{c}/median", "{:+.2f}%",
                       f"one-factor {row} {c} median"))

# r2 finding M2: the PAIRED per-km statistic, which every per-km claim in
# the report is now made on.
for c in ("S1", "S2", "S3", "S4"):
    for stat in ("min", "median", "max"):
        CHECKS.append((
            f"interface_ws8/per_km_margin_paired/corners/nominal/{c}/"
            f"ensemble/{stat}", "{:+.2f}%",
            f"{c} paired per-km margin {stat}"))

# r2 finding M4: ESC-WS8-1's power-side half is a rendering of measured
# values, not a paragraph. These formats must match the escalation's own
# f-strings character for character.
CHECKS += [
    ("s4_cell_substitution_direction/p_cont_chg_kW", "{:.1f} kW",
     "S4 pack continuous charge ceiling"),
    ("s4_cell_substitution_direction/p_cont_dis_kW", "{:.1f} kW",
     "S4 pack continuous discharge ceiling"),
    ("s4_cell_substitution_direction/c_cont_chg", "{:.1f} C",
     "S4 pack charge C-rate"),
    ("s4_cell_substitution_direction/f_machine_N", "{:,.0f} N",
     "S4 machine retard force at cruise"),
    ("s4_cell_substitution_direction/f_regen_N", "{:,.0f} N",
     "S4 regen force the pack ceiling allows at cruise"),
    ("s4_cell_substitution_direction/pack_ceiling_cost_pct", "{:.1f}%",
     "what the pack ceiling costs S4's retard capability"),
    # the power-half's speed statement. r3's first cut rendered a null
    # as "0 km/h" - the inverse of the truth - so it is pinned.
    ("s4_cell_substitution_direction/pack_ceiling_binds_above_kmh",
     "{:.1f} km/h", "speed above which S4's pack ceiling binds"),
    ("s4_cell_substitution_direction/descent_resistor_kW", "{:.1f} kW",
     "S4 resistor on the enumerated 6% descent, pack accepting"),
    ("s4_cell_substitution_direction/descent_friction_kW", "{:.1f} kW",
     "S4 foundation brakes on the same case"),
    ("s4_cell_substitution_direction/c_cont_dis", "{:.1f} C",
     "S4 pack discharge C-rate"),
    # the braking-side capability shortfall (r3, raised by review)
    ("interface_ws8/retard_overcommitment/value_kW", "{:.1f} kW",
     "worst retard overcommitment"),
    ("s4_cell_substitution_direction/retard_needed_6pct_90kmh_kW",
     "{:.0f} kW", "6% descent retard demand at 90 km/h"),
    ("s4_cell_substitution_direction/LH520_regen_kWh_median/nominal",
     "{:.1f}", "S4 LH-520 regen median, nominal"),
    ("s4_cell_substitution_direction/LH520_regen_kWh_median/"
     "cold_minus10C", "{:.1f}", "S4 LH-520 regen median, cold"),
    ("s4_cell_substitution_direction/LH520_resistor_kWh_median/"
     "cold_minus10C", "{:.1f}", "S4 LH-520 resistor median, cold"),
]

# r3 / B1: S3's through-the-road path, measured over the whole trial.
CHECKS += [
    ("s3_ttr_path_status/e_ttr_charge_bus_kWh_total", "{:.3f}",
     "S3 through-the-road charge, whole trial"),
    ("s3_ttr_path_status/e_ttr_blocked_by_load_policy_kWh_total",
     "{:.3f}", "what S3's 0.72 BSFC policy withheld"),
]

# m1: the grade-hold ratio is a SWEPT result and its resolution
# sensitivity is solved rather than dismissed.
CHECKS += [
    ("task5_s3_specific/fixed_ratio_grade_hold/ratio_needed_to_hold_6pct/"
     "resolution_sensitivity/fine/ratio_step", "{}",
     "fine ratio grid step"),
    ("task5_s3_specific/fixed_ratio_grade_hold/ratio_needed_to_hold_6pct/"
     "resolution_sensitivity/d_rpm_at_105kmh", "{:.0f}",
     "rpm shift at ten times the resolution"),
]
# F2: the cold corner now applies WS3's cold charge acceptance.
CHECKS += [
    ("task3_trial/cold_minus10C/S1/spec/pack/p_cont_chg_kW_at_corner",
     "{:.1f} kW", "S1 pack charge acceptance at -10 C"),
    ("task3_trial/cold_minus10C/S1/spec/pack/p_cont_chg_kW", "{:.1f} kW",
     "S1 pack charge acceptance, warm"),
]
# F11/R28: the added altitude/hot corner, and the derate it exercises.
CHECKS += [
    ("task3_trial/hot_alt_2000m_45C/S0/spec/corner/engine_derate_factor",
     "{:.4f}", "WS4 derate factor at the R28 corner"),
]
for c in ("S1", "S2", "S3", "S4"):
    CHECKS.append((f"task3_margins/hot_alt_2000m_45C/{c}/ensemble/min",
                   "{:+.2f}%", f"{c} hot/altitude corner min"))

# --- sanity ----------------------------------------------------------
CHECKS += [
    ("sanity/road_load_95kmh_flat/model_aero_N", "{:,.0f} N", "aero at 95"),
    ("sanity/road_load_95kmh_flat/model_roll_N", "{:,.0f} N", "roll at 95"),
    ("sanity/mountain_6pct/grade_force_kN", "{:.1f} kN", "6% grade force"),
    ("sanity/mountain_6pct/power_at_90kmh_kW", "{:.0f} kW",
     "6% climb power at 90"),
]


def main():
    fails = []
    checked = 0
    for path, fmt, desc in CHECKS:
        try:
            val = get(path)
        except (KeyError, IndexError, TypeError):
            fails.append(f"MISSING IN RESULTS: {path} ({desc})")
            continue
        if val is None:
            fails.append(f"NULL IN RESULTS: {path} ({desc})")
            continue
        rendered = fmt.format(val)
        checked += 1
        if rendered not in REPORT:
            fails.append(f"NOT IN REPORT: {desc}\n"
                         f"    path     {path}\n"
                         f"    expected {rendered!r}")

    # interface block must appear verbatim in the report
    m = re.search(r"```json\s*\n(\{.*?\n\})\n```", REPORT, re.S)
    if not m:
        fails.append("NO JSON INTERFACE BLOCK FOUND IN REPORT")
    else:
        try:
            in_report = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            in_report = None
            fails.append(f"INTERFACE BLOCK IS NOT VALID JSON: {e}")
        if in_report is not None:
            if in_report != R["interface_ws8"]:
                fails.append(
                    "INTERFACE BLOCK != results_ws8.json['interface_ws8']")
            else:
                checked += 1

    # r1 finding F8: class TITLES are rendered verbatim into the headline
    # table and were not checked, so S4's "~170 kW sustainer genset" sat
    # in the report against a model running ~194 kW shaft / ~185 kW bus.
    for c in ("S0", "S1", "S2", "S3", "S4"):
        title = get(f"task3_trial/nominal/{c}/spec/title")
        if title not in REPORT:
            fails.append(f"TITLE NOT IN REPORT: {c}\n"
                         f"    expected {title!r}")
        else:
            checked += 1
        policy = get(f"task3_trial/nominal/{c}/spec/policy")
        if policy not in REPORT:
            fails.append(f"POLICY NOT IN REPORT: {c}")
        else:
            checked += 1

    # r2: the verdicts block must carry the executed status, the numbers
    # block must be versioned, and the inputs must be SHA-pinned.
    iface = R.get("interface_ws8", {})
    if iface.get("numbers_version") != "r3":
        fails.append("INTERFACE numbers_version is not 'r3'")
    else:
        checked += 1
    # R3_DIRECTIVE item 7: the heat ledger is versioned and WS6 consumes
    # ONLY the r3 one.
    if R.get("heat_ledger", {}).get("ledger_version") != "r3":
        fails.append("HEAT LEDGER ledger_version is not 'r3'")
    else:
        checked += 1
    if iface.get("verdicts", {}).get("status") != "executed_kill_2026-08-30":
        fails.append("INTERFACE verdicts.status is not "
                     "'executed_kill_2026-08-30'")
    else:
        checked += 1
    shas = iface.get("inputs_sha256") or {}
    missing = [k for k, v in shas.items() if not v]
    if not shas or missing:
        fails.append(f"INPUT SHA PINS MISSING: {missing or 'block absent'}")
    else:
        checked += 1

    # no verdict may have flipped (R2_DIRECTIVE item 3), and S3's
    # nominal ensemble-min may not have crossed the bar (R3_DIRECTIVE
    # item 1's own trip-wire, asserted rather than eyeballed).
    vs = R.get("verdict_stability", {})
    if not vs:
        fails.append("VERDICT STABILITY BLOCK MISSING")
    elif not vs.get("all_unchanged"):
        fails.append("A VERDICT FLIPPED, OR S3 CROSSED THE +3% BAR, ON "
                     "THE r3 NUMBERS - the round must STOP and report "
                     "rather than publish")
    else:
        checked += 1
    sc = vs.get("r3_stop_condition") or {}
    if not sc:
        fails.append("R3 STOP-CONDITION BLOCK MISSING")
    elif sc.get("crossed"):
        fails.append(
            f"R3_DIRECTIVE item 1 TRIP-WIRE: S3's nominal ensemble-min "
            f"{sc.get('S3_nominal_margin_pct_min')} has crossed the "
            f"+{sc.get('bar_pct')}% bar - STOP and report")
    else:
        checked += 1
    ak3 = R.get("advance_kill", {}).get("candidates", {}).get("S3", {})
    if ak3.get("verdict") != "KILL":
        fails.append("S3's verdict is no longer KILL on the r3 numbers")
    else:
        checked += 1

    # ---- B1: the crankshaft assertion, named on its own --------------
    ex = R.get("heat_ledger", {}).get("overrun_exclusivity") or {}
    if not ex:
        fails.append("OVERRUN EXCLUSIVITY BLOCK MISSING (finding B1)")
    else:
        if not ex.get("all_hold"):
            fails.append("A RUN CARRIES BOTH COMPRESSION-BRAKE POWER AND "
                         "POSITIVE ENGINE SHAFT POWER - one crankshaft "
                         "cannot be in both states (finding B1)")
        else:
            checked += 1
        n_expect = len(R["_meta"]["seeds"]) * 2 * len(R["task3_trial"])
        for c in ("S0", "S1", "S2", "S3", "S4"):
            e = ex.get("candidates", {}).get(c)
            if not e:
                fails.append(f"EXCLUSIVITY: {c} not examined at all")
                continue
            if not e.get("examined_every_run") or \
                    e["runs_examined"] != n_expect:
                fails.append(
                    f"EXCLUSIVITY: {c} examined {e.get('runs_examined')} "
                    f"runs, expected {n_expect} - a check that skips what "
                    f"it cannot see is not a check (r2 minor m5a)")
            elif e["samples_brake_and_shaft"] != 0:
                fails.append(
                    f"EXCLUSIVITY: {c} has "
                    f"{e['samples_brake_and_shaft']} violating samples "
                    f"(worst run {e.get('worst_run')})")
            else:
                checked += 1
        if ex.get("rule") and ex["rule"] not in REPORT:
            fails.append("THE ONE RULE IS NOT RENDERED VERBATIM IN THE "
                         "REPORT")
        else:
            checked += 1

    # ---- the simulated member is no longer exempt from the closure ---
    for c in ("S0", "S1", "S2", "S3", "S4"):
        cases = ((R.get("heat_ledger", {}).get("candidates", {})
                  .get(c, {}).get("closure", {}) or {}).get("cases") or {})
        row = cases.get("simulated_worst_run")
        if row is None:
            fails.append(
                f"CLOSURE: {c}'s simulated_worst_run carries no residual "
                f"- r2's exemption is what finding B1 came through")
        elif not row.get("closes"):
            fails.append(
                f"CLOSURE: {c}'s simulated_worst_run does not close "
                f"({row.get('residual_kW')} kW, "
                f"{row.get('relative')} relative)")
        else:
            checked += 1

    # ---- the braking-side shortfall must be a capability field, not
    # a heat row: no component may be exported above its rating, and the
    # overcommitment must be present whenever a resistor saturates.
    ovb = R.get("interface_ws8", {}).get("retard_overcommitment")
    if ovb is None:
        fails.append("RETARD OVERCOMMITMENT BLOCK MISSING")
    else:
        checked += 1
        for c in ("S1", "S2", "S3", "S4"):
            rating = R["task3_trial"]["nominal"][c]["spec"].get(
                "brake_resistor_rating_kW")
            wc = (R["heat_ledger"]["candidates"][c]["worst_case"]
                  ["brake_resistor_kW"]["value"])
            if rating and wc > rating * 1.001:
                fails.append(
                    f"{c} exports {wc:.1f} kW of resistor heat against a "
                    f"{rating:.0f} kW rating - the cap in "
                    f"`resistor_and_overcommitment` is not being applied")
            else:
                checked += 1

    # ---- M1: every direction is generated, and rendered verbatim -----
    cd_ = R.get("correction_directions") or {}
    if not cd_:
        fails.append("CORRECTION DIRECTIONS BLOCK MISSING (finding M1)")
    for k, v in cd_.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        if not v.get("measurable"):
            continue
        if v["direction"] not in REPORT:
            fails.append(f"GENERATED DIRECTION NOT IN REPORT: {k}\n"
                         f"    expected {v['direction']!r}")
        else:
            checked += 1

    # ---- M3: the R28 scope statement is measured and rendered --------
    ds = (R.get("corner_derate_scope") or {}).get("R28_corner") or {}
    if not ds:
        fails.append("CORNER DERATE SCOPE BLOCK MISSING (finding M3)")
    else:
        if not ds.get("electric_side_unchanged"):
            fails.append(
                "R28 SCOPE: an electric-side quantity moves at the R28 "
                "corner, so the exported scope statement is stale: "
                f"{ds.get('does_not_derate')}")
        else:
            checked += 1
        for key in ("statement", "direction_of_error"):
            if ds.get(key) and ds[key] not in REPORT:
                fails.append(f"R28 SCOPE {key} NOT RENDERED IN REPORT")
            else:
                checked += 1

    # ---- M4: ESC-WS8-1 must state BOTH halves ------------------------
    esc1 = next((e for e in R.get("escalations", [])
                 if e["id"] == "ESC-WS8-1"), None)
    if esc1 is None:
        fails.append("ESC-WS8-1 MISSING")
    else:
        for token, where in (("BOTH WAYS", "finding"),
                             ("R27/ESC-1", "asks"),
                             ("TWO-DIRECTIONAL", "materiality")):
            if token not in esc1[where]:
                fails.append(
                    f"ESC-WS8-1 {where} does not carry {token!r} - "
                    f"finding M4 is that only one half was on the record")
            else:
                checked += 1
    # direction-of-error invariants the restatement rests on
    csd = R.get("s4_cell_substitution_direction") or {}
    if csd:
        if not (csd["f_regen_N"] < csd["f_machine_N"]
                and csd["pack_ceiling_cost_pct"] < 15.0):
            fails.append("ESC-WS8-1: the pack ceiling is no longer "
                         "co-binding with the machine at cruise - the "
                         "restated wording is stale")
        else:
            checked += 1
        _cold = csd["LH520_resistor_kWh_median"].get("cold_minus10C")
        _nom = csd["LH520_resistor_kWh_median"].get("nominal")
        if _cold is None or _nom is None:
            # a --quick run has no cold corner; the check is not skipped
            # silently, it is reported as not applicable
            print("verify_ws8: NOTE - cold corner absent, the ESC-WS8-1 "
                  "transfer invariant is not applicable to this run")
        elif not (_cold > 100.0 * max(_nom, 1e-9)):
            fails.append("ESC-WS8-1: the cold corner no longer shows the "
                         "harvest transferring to the resistor")
        else:
            checked += 1

    # the heat ledger must close, stay inside its ratings, AND satisfy
    # the crankshaft assertion (F1, B1)
    hl = R.get("heat_ledger", {})
    if not hl.get("all_cases_close_and_within_rating"):
        fails.append("HEAT LEDGER does not close, or a component exceeds "
                     "the rating of the hardware whose mass was charged")
    else:
        checked += 1

    # r2: cold charge acceptance must actually bite in the cold corner
    # (F2 - in r1 the envelope was identical at nominal and at -10 C)
    try:
        warm = get("task3_trial/nominal/S1/spec/pack/p_cont_chg_kW_at_corner")
        cold = get("task3_trial/cold_minus10C/S1/spec/pack/"
                   "p_cont_chg_kW_at_corner")
        if not (cold < warm * 0.2):
            fails.append(f"COLD CHARGE ACCEPTANCE NOT APPLIED: warm {warm}, "
                         f"cold {cold}")
        else:
            checked += 1
    except (KeyError, TypeError):
        fails.append("COLD CHARGE ACCEPTANCE FIELDS MISSING")

    # the standalone changelog is generated from the same lines as
    # report section 15, so every line of it (bar its own header) must
    # appear in the report verbatim
    # the changelog filename is DERIVED from the round in the data file,
    # the same way make_report_ws8.py derives it - a round that retyped
    # it would overwrite the previous round's only surviving copy.
    _round = R["_meta"].get("errata_round_id", "r2")
    cpath = os.path.join(HERE, f"CHANGELOG_WS8_{_round}.md")
    if not os.path.exists(cpath):
        fails.append(f"CHANGELOG_WS8_{_round}.md MISSING")
    else:
        body = open(cpath).read().split("\n---\n", 1)
        drifted = []
        if len(body) == 2:
            for ln in body[1].split("\n"):
                t = ln.strip()
                if len(t) < 40 or t.startswith("### ") or t.startswith("## "):
                    continue
                if t not in REPORT:
                    drifted.append(t[:70])
        if drifted:
            fails.append(f"CHANGELOG DRIFTED FROM THE REPORT: "
                         f"{len(drifted)} lines, e.g. {drifted[:2]}")
        else:
            checked += 1

    # every escalation must be named in the report
    for e in R.get("escalations", []):
        if e["id"] not in REPORT:
            fails.append(f"ESCALATION NOT IN REPORT: {e['id']}")
        else:
            checked += 1

    # verdicts must be rendered
    for c, v in R["advance_kill"]["candidates"].items():
        if f"{c}" not in REPORT or v["verdict"] not in REPORT:
            fails.append(f"VERDICT NOT IN REPORT: {c} {v['verdict']}")
        else:
            checked += 1

    print(f"verify_ws8: {checked} checks")
    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print("verify_ws8: OK - every headline number renders a results_ws8.json "
          "value verbatim; interface block matches; all escalations and "
          "verdicts present.")


if __name__ == "__main__":
    main()
