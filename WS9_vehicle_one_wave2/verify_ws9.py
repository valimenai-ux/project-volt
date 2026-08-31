#!/usr/bin/env python3
"""
Project Volt - WS9
Independent verifier (CLAUDE.md rule 2: "a machine-readable interface block
whose headline numbers verify VERBATIM against the workstream's results
data file (a verify_*.py asserts this; nothing is transcribed by hand)").

    ../.venv/bin/python verify_ws9.py

Four families of check, and the fourth is new to WS9:

  A  the report's JSON interface block is byte-identical to
     results_ws9.json['interface_ws9']
  B  every headline number rendered in REPORT_WS9.md appears verbatim,
     re-formatted from the results by this script independently of
     make_report_ws9.py
  C  the results are internally consistent - margins recomputed from the
     per-seed data, mass closure, the advance/kill verdicts re-derived
     against the pre-committed criteria
  D  THE VINTAGE PIN STILL HOLDS. WS9 inherits WS8's models read-only while
     WS8's round 2 is in flight. Every inherited source file was
     sha256-pinned at run time; this re-hashes them and reports DRIFT. That
     is the hot-swap signal the assignment asks for: if WS8's code has moved
     since this run, the record says so instead of pretending it has not.

Exit code 0 if every check passes and the pin holds; 1 otherwise. A pin
DRIFT is reported as a WARNING and does not on its own fail the run - the
numbers were correct for the code they were run against, and the drift is
information for the lead, not an error in this artifact.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS8 = os.path.join(HERE, "..", "WS8_semi_architecture")
RESULTS = os.path.join(HERE, "results_ws9.json")
REPORT = os.path.join(HERE, "REPORT_WS9.md")

FAILS = []
WARNS = []
N = 0


def check(cond, what):
    global N
    N += 1
    if not cond:
        FAILS.append(what)


def infile(txt, s, what):
    check(s in txt, f"{what}: '{s}' not found verbatim in REPORT_WS9.md")


def f(x, n=2, plus=False):
    if x is None:
        return "n/a"
    return f"{x:+.{n}f}" if plus else f"{x:.{n}f}"


def pct(x, n=2):
    return "n/a" if x is None else f"{x:+.{n}f}%"


def kg(x):
    return "n/a" if x is None else f"{x:,.0f}"


def sha(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def main():
    R = json.load(open(RESULTS))
    txt = open(REPORT).read()
    design = R["_meta"]["design_duty"]
    control = R["_meta"]["control_duty"]
    T = R["trial"]["nominal"]
    M = R["margins"]["nominal"]
    AK = R["advance_kill"]["candidates"]
    ruler = "S0R"

    # ---------------------------------------------------------- A
    m = re.search(r"```json\n(.*?)\n```", txt, re.S)
    check(m is not None, "A: no json block found in the report")
    if m:
        try:
            rendered = json.loads(m.group(1))
        except ValueError as e:
            rendered = None
            FAILS.append(f"A: interface block is not valid JSON ({e})")
        check(rendered == R["interface_ws9"],
              "A: rendered interface block != results_ws9.json"
              "['interface_ws9']")
        check(m.group(1) == json.dumps(R["interface_ws9"], indent=1),
              "A: interface block is not byte-identical to "
              "json.dumps(results['interface_ws9'], indent=1)")

    # ---------------------------------------------------------- B
    for cname, blob in T.items():
        s = blob["spec"]
        infile(txt, kg(s["payload_kg"]) + " kg",
               f"B/payload/{cname}")
        infile(txt, f"{s['powertrain_mass_kg']:,.0f}",
               f"B/powertrain_mass/{cname}")
        for duty in (design, control):
            e = blob["per_duty"][duty]["ensemble"]
            for stat in ("min", "median", "max"):
                infile(txt, f(e["MJ_primary_per_payload_tkm"][stat], 4),
                       f"B/metric/{cname}/{duty}/{stat}")
            infile(txt, f(e["fuel_L_per_100km"]["median"]),
                   f"B/L100/{cname}/{duty}")
            mm = M[duty].get(cname)
            if mm:
                infile(txt, pct(mm["ensemble"]["min"]),
                       f"B/margin_min/{cname}/{duty}")
                infile(txt, pct(mm["ensemble"]["median"]),
                       f"B/margin_median/{cname}/{duty}")
        for k, v in s["mass_rows_kg"].items():
            infile(txt, f"{v:,.0f}", f"B/mass_row/{cname}/{k}")

    for cname, v in AK.items():
        infile(txt, pct(v["nominal_margin_pct_min"]),
               f"B/ak_nominal/{cname}")
        infile(txt, v["verdict"], f"B/verdict/{cname}")
        if v["worst_corner"]:
            infile(txt, v["worst_corner"], f"B/worst_corner/{cname}")
            infile(txt, pct(v["worst_corner_margin_pct_min"]),
                   f"B/worst_corner_margin/{cname}")

    be = R["_s6_break_even"]
    infile(txt, f(be["break_even_peak_BTE"], 4), "B/break_even_BTE")
    infile(txt, f(be["claimed_peak_BTE"], 3), "B/claimed_BTE")

    eg = R["etc_gate"]
    infile(txt, pct(eg["design_duty_net_margin_pct_min"]),
           "B/etc_gate_min")
    infile(txt, eg["verdict"], "B/etc_gate_verdict")
    infile(txt, f(eg["fuel_gain_needed_to_clear_gate_pct"]) + "%",
           "B/etc_gate_bar")

    ev = R["f7_crosscheck"]["envelope_vs_band"]
    for k in ("model_min", "model_median", "model_max",
              "mass_matched_median"):
        infile(txt, f(ev[k]), f"B/f7/{k}")

    tw = R["two_walls"]
    infile(txt, f(tw["two_speed_solve"]["ENG-13L"]["solve"]
                  ["wall1_ratio_ceiling"], 4), "B/wall1_ceiling")
    for k, v in tw["two_speed_solve"].items():
        infile(txt, f(v["solve"]["ratio_high"], 3), f"B/ratio_high/{k}")
        infile(txt, f(v["solve"]["ratio_low"], 3), f"B/ratio_low/{k}")
        infile(txt, f(v["solve"]["rpm_at_cruise_100kmh"], 0),
               f"B/cruise_rpm/{k}")

    for k, v in R["prime_mover"]["prime_movers"].items():
        infile(txt, kg(v["equal_range"]["TOTAL_CHARGED_kg"]) + " kg",
               f"B/pm_mass/{k}")
        infile(txt, f(v["efficiency"]["at_the_pin"]["eta_fuel_to_bus"], 4),
               f"B/pm_eta_pin/{k}")

    un = R["interface_ws9"]["unserved_energy_kWh"]
    infile(txt, f(un["value"], 2), "B/unserved_worst")
    infile(txt, un["governing_case"], "B/unserved_governing")

    ret = T[ruler]["spec"]["retarder"]
    infile(txt, f(ret["mass_charged_kg"], 0) + " kg", "B/retarder_mass")
    infile(txt, f(ret["t_max_propshaft_Nm"], 0), "B/retarder_torque")

    for e in R["escalations"]:
        infile(txt, e["id"], f"B/escalation/{e['id']}")

    # ---------------------------------------------------------- C
    for cname, blob in T.items():
        s = blob["spec"]
        total = sum(s["mass_rows_kg"].values())
        check(abs(total - s["powertrain_mass_kg"]) < 1e-6,
              f"C: {cname} mass rows do not sum to the powertrain total")
        check(abs(s["tare_common_kg"] + s["powertrain_mass_kg"]
                  + s["payload_kg"] - s["gcw_kg"]) < 1e-6,
              f"C: {cname} mass closure fails")

    for corner, mm in R["margins"].items():
        for duty, d in mm.items():
            base = {r["seed"]: r["MJ_primary_per_payload_tkm"]
                    for r in R["trial"][corner][ruler]["per_duty"][duty]
                    ["per_seed"]}
            for cname, blob in d.items():
                rows = R["trial"][corner][cname]["per_duty"][duty][
                    "per_seed"]
                recomputed = sorted(
                    (base[r["seed"]] - r["MJ_primary_per_payload_tkm"])
                    / base[r["seed"]] * 100.0 for r in rows)
                stored = sorted(p["margin_pct"] for p in blob["per_seed"])
                check(all(abs(a - b) < 1e-9
                          for a, b in zip(recomputed, stored)),
                      f"C: {cname}/{corner}/{duty} per-seed margins do not "
                      f"recompute from the per-seed metric")
                ens = blob["ensemble"]
                check(abs(min(stored) - ens["min"]) < 1e-9
                      and abs(max(stored) - ens["max"]) < 1e-9,
                      f"C: {cname}/{corner}/{duty} envelope does not match "
                      f"its own per-seed values")

    crit = R["advance_kill"]["criteria"]
    for cname, v in AK.items():
        pn = v["nominal_margin_pct_min"] >= crit["nominal_pct"]
        wc = v["worst_corner_margin_pct_min"]
        pc = wc is None or wc >= crit["every_corner_pct"]
        check(v["passes_nominal_3pct"] == pn,
              f"C: {cname} nominal pass flag disagrees with the criterion")
        check(v["passes_all_corners_0pct"] == pc,
              f"C: {cname} corner pass flag disagrees with the criterion")
        check(v["verdict"] == ("ADVANCE" if (pn and pc) else "KILL"),
              f"C: {cname} verdict disagrees with its own pass flags")
    check(crit["duty"] == design,
          "C: advance/kill is not read on the design duty")
    check(crit["control_duty_gates"] is False,
          "C: the control duty is marked as gating")

    check(R["sanity"]["all_pass"] is True,
          "C: sanity.all_pass is not True")
    det = R.get("determinism", {})
    check(det.get("status") == "PASS",
          f"C: the rule-1 regeneration check is "
          f"'{det.get('status')}', not PASS")
    infile(txt, det.get("status", "NOT RUN"), "B/determinism_status")
    check(R["sanity"]["no_ws8_artifact_read"]["passes"] is True,
          "C: WS9 reads a WS8 numeric artifact")
    check(R["sanity"]["machine_basis_gate_ESC2"]["all_pass"] is True,
          "C: a machine exceeds the ESC-2 k <= 2.0 gate")
    check(R["sanity"]["primary_energy_invariance"]["all_pass"] is True,
          "C: the primary-energy metric moved a diesel-only margin")

    # no fleet blend anywhere
    check("fleet" not in json.dumps(R["headline"]).lower(),
          "C: a fleet average appears in the headline")

    # ---------------------------------------------------------- D
    iv = R["inherited_vintage"]
    drift = []
    for name, rec in iv["ws8_source_files"].items():
        now = sha(os.path.join(WS8, name))
        if now != rec["sha256"]:
            drift.append(name)
    if drift:
        WARNS.append(
            "D: WS8 SOURCE DRIFT since this run - " + ", ".join(drift)
            + ". WS9's numbers were correct for the code they were run "
              "against; re-run `run_ws9.py` to hot-swap onto the new "
              "vintage. This is information for the lead, not an error in "
              "this artifact.")
    own_drift = [n for n, rec in iv["ws9_own_files"].items()
                 if rec["sha256"] is not None
                 and sha(os.path.join(HERE, n)) != rec["sha256"]]
    if own_drift:
        WARNS.append("D: WS9 OWN-SOURCE DRIFT since this run - "
                     + ", ".join(own_drift)
                     + ". Re-run `run_ws9.py` to re-pin.")
    N_extra = len(iv["ws8_source_files"]) + len(iv["ws9_own_files"])

    # ---------------------------------------------------------- out
    print(f"verify_ws9: {N + N_extra} checks "
          f"({N} assertions + {N_extra} pin hashes)")
    for wmsg in WARNS:
        print("  WARNING  " + wmsg)
    if FAILS:
        print(f"  FAIL ({len(FAILS)}):")
        for x in FAILS[:60]:
            print("    - " + x)
        if len(FAILS) > 60:
            print(f"    ... and {len(FAILS) - 60} more")
        sys.exit(1)
    print("  PASS - every rendered figure verifies verbatim against "
          "results_ws9.json, the interface block is byte-identical, and "
          "the results are internally consistent.")
    sys.exit(0)


if __name__ == "__main__":
    main()
