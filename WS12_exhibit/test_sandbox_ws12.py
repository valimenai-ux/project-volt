"""WS12 — the sandbox unit test.

The assignment orders: "re-derive its constants from WS1's ratified
road-load parameters and WS8's engine-rpm ceiling, with a unit test that
reproduces the S3 feasibility result (3.60:1 ceiling, ~half the grade
force) from the same function."

This is that test. Every expected value is READ FROM THE RECORD at run
time — nothing is transcribed. Run it directly:

    ../.venv/bin/python3 test_sandbox_ws12.py

It exits 0 on pass and 1 on any failure, and `exhibit_verify.py` runs
the same assertions as part of the build gate.
"""

import sys

from ws12_record import load_json, resolve
from ws12_sandbox import (G, VEHICLE_ONE_ETA_MEMBERS, ratio_ceiling,
                          ratio_required, resolve_endpoints, road_load_N)

WS1 = "WS1_loads_duty_cycles/results.json"
WS8 = "WS8_semi_architecture/results_ws8.json"
WS9 = "WS9_vehicle_one_wave2/results_ws9.json"

CHECKS = []


def close(name, got, want, tol, note=""):
    ok = abs(got - want) <= tol
    CHECKS.append({"name": name, "got": got, "want": want, "tol": tol,
                   "pass": ok, "note": note})
    return ok


def equal(name, got, want, note=""):
    ok = got == want
    CHECKS.append({"name": name, "got": got, "want": want, "tol": 0.0,
                   "pass": ok, "note": note})
    return ok


def run():
    ws1 = load_json(WS1)
    ws8 = load_json(WS8)
    ws9 = load_json(WS9)
    ends = resolve_endpoints(load_json)

    # -- 1. The same road-load function reproduces WS1's own flat cruise
    #       cross-check at 85 km/h, term by term.
    v = ws1["params"]["vehicle"]
    F = road_load_N(v["m_gvw"], v["CdA"], v["Crr"], v["rho_air"],
                    85.0 / 3.6, 0.0)
    bc = ws1["baseline_crosscheck"]
    close("WS1 cruise85 aero_N", F["aero_N"],
          bc["cruise85_components_N"]["aero"], 1e-9)
    close("WS1 cruise85 roll_N", F["roll_N"],
          bc["cruise85_components_N"]["roll"], 1e-9)
    close("WS1 cruise85 total_N", F["total_N"], bc["cruise85_force_N"], 1e-9)

    # -- 2. And WS1's own 6% grade cross-check at 60 km/h, term by term.
    #       This is the Vehicle Zero end of the sandbox's mass axis.
    g6 = resolve(ws1, ["sensitivity", "climb_10km_6pc", "per_speed",
                       "60kmh"])
    F6 = road_load_N(v["m_gvw"], v["CdA"], v["Crr"], v["rho_air"],
                     60.0 / 3.6, 0.06)
    close("WS1 6% @60 km/h aero_N", F6["aero_N"],
          g6["components_N"]["aero"], 1e-9)
    close("WS1 6% @60 km/h roll_N", F6["roll_N"],
          g6["components_N"]["roll"], 1e-9)
    close("WS1 6% @60 km/h grade_N", F6["grade_N"],
          g6["components_N"]["grade"], 1e-9)
    close("WS1 6% @60 km/h total_N", F6["total_N"], g6["wheel_force_N"], 1e-9)

    # -- 3. The Vehicle One end: the same function reproduces WS9's
    #       exported 6% grade-hold force ledger at 36,300 kg.
    fr = resolve(ws9, ["two_walls", "two_speed_solve", "ENG-13L", "solve",
                       "force_required"])
    v8 = ws8["params"]["vehicle"]
    F1 = road_load_N(v8["m_gcw"], v8["CdA"], v8["Crr"], v8["rho_air"],
                     fr["v_ref_ms"], fr["grade"])
    close("WS9 6% hold aero_N", F1["aero_N"], fr["aero_N"], 1e-9)
    close("WS9 6% hold roll_N", F1["roll_N"], fr["roll_N"], 1e-9)
    close("WS9 6% hold grade_N", F1["grade_N"], fr["grade_N"], 1e-9)
    close("WS9 6% hold total_N", F1["total_N"], fr["total_N"], 1e-9)

    # -- 4. THE CEILING. The same closed form reproduces WS8's published
    #       physics bound: 3.769911184307752, and WS9's to one ulp.
    cf = resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility",
                       "ratio_ceiling_closed_form"])
    ceil8 = ratio_ceiling(cf["rpm_ceiling"], cf["r_dyn_m"],
                          cf["v_cruise_kmh"] / 3.6)
    close("WS8 ratio ceiling (closed form)", ceil8, cf["value"], 1e-12)
    ceil9 = resolve(ws9, ["two_walls", "single_ratio_closed_form",
                          "ENG-13L", "ratio_ceiling_closed_form"])
    close("WS9 ratio ceiling (same bound)", ceil8, ceil9, 1e-12)

    # -- 5. THE SWEPT-SET RESULT. Feeding WS8's own enumerated ratio set
    #       through the same two bounds reproduces `feasible_ratios == []`
    #       and `max_ratio_without_overspeed == 3.6` — the 3.60:1 ceiling.
    s3 = resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility"])
    needed = s3["ratio_needed_to_hold_6pct"]["ratio"]
    under = [r for r in s3["ratios_tested"] if r <= ceil8]
    feasible = [r for r in s3["ratios_tested"] if r <= ceil8 and r >= needed]
    equal("S3 feasible ratios (recomputed)", feasible, s3["feasible_ratios"])
    equal("S3 any_feasible (recomputed)", bool(feasible), s3["any_feasible"])
    close("S3 max ratio without overspeed = 3.60:1", max(under),
          s3["max_ratio_without_overspeed"], 1e-12,
          "the highest member of WS8's enumerated sweep under the bound")

    # -- 6. ~HALF THE GRADE FORCE. The ratio the 6% hold needs, from the
    #       same ratio_required(), reproduces WS9's closed form for both
    #       engines; the force available at the ceiling is then a little
    #       over half of what the grade demands.
    eta = 1.0
    for spec in VEHICLE_ONE_ETA_MEMBERS:
        eta *= resolve(load_json(spec[0]), spec[1])
    for eng, tq_path in (("ENG-11L", ["trial", "nominal", "S5", "spec",
                                      "engine", "peak_torque_Nm"]),
                         ("ENG-13L", ["trial", "nominal", "S5-13L", "spec",
                                      "engine", "peak_torque_Nm"])):
        t_peak = resolve(ws9, tq_path)
        blk = resolve(ws9, ["two_walls", "single_ratio_closed_form", eng])
        req = ratio_required(fr["total_N"], v8["r_dyn"], t_peak, eta)
        close("WS9 %s ratio required for 6%%" % eng, req,
              blk["ratio_required_for_6pct"], 1e-9)
        avail_kN = fr["total_N"] * ceil8 / req / 1000.0
        close("WS9 %s force available at the ceiling, kN" % eng, avail_kN,
              blk["F_available_at_ceiling_kN"], 1e-9)
        frac = avail_kN * 1000.0 / fr["total_N"]
        close("WS9 %s span needed (1/frac)" % eng, 1.0 / frac,
              blk["span_needed"], 1e-9,
              "force available at the ceiling is %.2f%% of the grade force"
              % (100.0 * frac))

    # -- 7. The endpoint set the visitor's sliders interpolate between is
    #       the record's, not an invented one.
    close("sandbox endpoint: Vehicle Zero mass", ends["zero"]["m_kg"],
          v["m_gvw"], 0.0)
    close("sandbox endpoint: Vehicle One mass", ends["one"]["m_kg"],
          v8["m_gcw"], 0.0)
    close("sandbox endpoint: Vehicle One rpm ceiling",
          ends["one"]["rpm_ceiling"], cf["rpm_ceiling"], 0.0)
    close("sandbox endpoint: Vehicle One driveline eta",
          ends["one"]["eta_driveline"], eta, 0.0)
    close("program gravity constant", G, 9.81, 0.0)

    return CHECKS


def main():
    checks = run()
    bad = [c for c in checks if not c["pass"]]
    for c in checks:
        print("%-52s %-4s got=%r want=%r%s"
              % (c["name"], "PASS" if c["pass"] else "FAIL", c["got"],
                 c["want"], ("  [" + c["note"] + "]") if c["note"] else ""))
    print("\n%d checks, %d failed" % (len(checks), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
