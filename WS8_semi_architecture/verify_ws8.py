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
# F3/F4/F5/F6: the one-factor rows that decide the S1-vs-S2 ordering.
for row in ("r2_as_reported", "F4_reverted_credit_removed",
            "F6_reverted_peak_point_pricing",
            "F3_reverted_engine_dual_use", "F5_reverted_spin_rule",
            "F3_and_F5_reverted"):
    for c in ("S1", "S2"):
        CHECKS.append((f"one_factor/rows/{row}/{c}/median", "{:+.2f}%",
                       f"one-factor {row} {c} median"))
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
    if iface.get("numbers_version") != "r2":
        fails.append("INTERFACE numbers_version is not 'r2'")
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

    # r2: no verdict may have flipped (R2_DIRECTIVE item 3)
    vs = R.get("verdict_stability", {})
    if not vs:
        fails.append("VERDICT STABILITY BLOCK MISSING")
    elif not vs.get("all_unchanged"):
        fails.append("A VERDICT FLIPPED ON THE r2 NUMBERS - the round must "
                     "STOP and report rather than publish")
    else:
        checked += 1

    # r2: the heat ledger must close and stay inside its ratings (F1)
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
    cpath = os.path.join(HERE, "CHANGELOG_WS8_r2.md")
    if not os.path.exists(cpath):
        fails.append("CHANGELOG_WS8_r2.md MISSING")
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
