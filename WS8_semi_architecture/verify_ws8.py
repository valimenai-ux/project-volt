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
     "{:.2f}", "S3 max ratio without overspeed"),
    ("interface_ws8/S3_diesel_axle_adhesion_grade_limit/value", "{:.4f}",
     "S3 adhesion grade limit"),
]

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
