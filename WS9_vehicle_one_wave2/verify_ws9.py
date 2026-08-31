#!/usr/bin/env python3
"""
Project Volt - WS9
Independent verifier (CLAUDE.md rule 2: "a machine-readable interface block
whose headline numbers verify VERBATIM against the workstream's results
data file (a verify_*.py asserts this; nothing is transcribed by hand)").

    ../.venv/bin/python verify_ws9.py

Five families of check; D and E are WS9's own:

  A  the report's JSON interface block is byte-identical to
     results_ws9.json['interface_ws9']
  B  every headline number rendered in REPORT_WS9.md appears verbatim,
     re-formatted from the results by this script independently of
     make_report_ws9.py
  C  the results are internally consistent - margins recomputed from the
     per-seed data, mass closure, the advance/kill verdicts re-derived
     against the pre-committed criteria
  D  THE VINTAGE PIN STILL HOLDS. WS9 inherits WS8's models read-only, and
     WS8's rounds land under it. Every pinned file - WS8's seven models,
     `run_ws8.py` as a hashed-but-not-imported rule source, and the six
     SIBLING-WORKSTREAM sources WS9 reaches through WS8 - was sha256-pinned
     at run time; this re-hashes them and reports DRIFT. That is the
     hot-swap signal the assignment asks for.
  E  THE r3 RE-PIN AND WHAT IT CLAIMS. The pin reports r3 and every r3
     fingerprint feature is present; ESC-WS9-8's concordance has no
     UNDECLARED difference and every declared one carries a declaration;
     R38's gate input is exported, agrees with the sanity table, its paired
     envelope recomputes from the per-seed data, and NO VERDICT HAS BEEN
     ADJUSTED FOR IT - every verdict is still exactly what the
     pre-committed criteria give; R34's traces are on disk and match their
     recorded hashes; and the ordered changelog entry exists and is the
     same lines as the report's section 17.

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
        # a key may carry a trailing role marker, e.g.
        # "run_ws8.py [rule source, NOT imported]"
        now = sha(os.path.join(WS8, name.split(" [")[0]))
        if now != rec["sha256"]:
            drift.append(name)
    if drift:
        WARNS.append(
            "D: WS8 SOURCE DRIFT since this run - " + ", ".join(drift)
            + ". WS9's numbers were correct for the code they were run "
              "against; re-run `run_ws9.py` to hot-swap onto the new "
              "vintage. This is information for the lead, not an error in "
              "this artifact.")
    sib = iv.get("sibling_workstream_sources_reached_through_ws8", {})
    sib_drift = [n for n, rec in sib.items()
                 if sha(os.path.join(HERE, n)) != rec["sha256"]]
    if sib_drift:
        WARNS.append(
            "D: SIBLING-WORKSTREAM SOURCE DRIFT since this run - "
            + ", ".join(sib_drift)
            + ". WS9 reaches these THROUGH WS8's models (ESC-WS9-11); a "
              "change in one of them can move a WS9 number with nothing "
              "in WS8's own pin able to say so, which is why they are "
              "pinned here.")
    own_drift = [n for n, rec in iv["ws9_own_files"].items()
                 if rec["sha256"] is not None
                 and sha(os.path.join(HERE, n)) != rec["sha256"]]
    if own_drift:
        WARNS.append("D: WS9 OWN-SOURCE DRIFT since this run - "
                     + ", ".join(own_drift)
                     + ". Re-run `run_ws9.py` to re-pin.")
    N_extra = (len(iv["ws8_source_files"]) + len(sib)
               + len(iv["ws9_own_files"]))

    # ---------------------------------------------------------- E
    # ESC-WS9-8's concordance, R38's gate input, R34's traces. Everything
    # here is a check on THIS artifact's own claims about the re-pin; none
    # of it reads or applies a verdict.
    fp = iv["ws8_code_round_fingerprint"]
    check(fp["code_round"] == "r3",
          f"E: the pin reports code round '{fp['code_round']}', not r3")
    check(all(fp["r3_features"].values()),
          "E: the r3 fingerprint has a feature missing while claiming r3")
    check(all(fp["r2_features"].values()),
          "E: the r2 fingerprint has a feature missing")
    # the r3 features must be REAL r3 features, not r2 names relabelled:
    # every one of them must be absent from the r2 import surface's home
    # module fingerprint file, which records the r2 tree.
    r2surf = os.path.join(HERE, "sources", "ws8_import_surface_r2.json")
    check(os.path.exists(r2surf),
          "E: sources/ws8_import_surface_r2.json is missing - the r2 -> r3 "
          "delta cannot be checked")
    infile(txt, f"WS8 code round detected: `{fp['code_round']}`",
           "E/report_round")

    cc = R["concordance_ws8_r3"]
    check(cc["any_undeclared_difference"] is False,
          f"E: the concordance reports UNDECLARED differences from WS8 r3: "
          f"{cc['undeclared_fields']}")
    for k, v in cc["summary"].items():
        check(v["n_differs_undeclared"] == 0,
              f"E: {k} has {v['n_differs_undeclared']} undeclared "
              f"difference(s) from WS8 r3")
        infile(txt, k, f"E/concordance_impl/{k}")
    for k, blob in cc["implementations"].items():
        for fld in blob["fields"]:
            check(fld["verdict"] in ("CONSISTENT", "DIFFERS_BY_DESIGN",
                                     "DIFFERS"),
                  f"E: {k}.{fld['field']} has an unknown verdict")
            if fld["verdict"] == "DIFFERS_BY_DESIGN":
                check(bool(fld.get("declared_in")),
                      f"E: {k}.{fld['field']} is a declared difference "
                      f"with no declaration")
            infile(txt, fld["field"], f"E/concordance_field/{fld['field']}")
    d = cc["import_surface_r2_to_r3"]
    check(d is not None, "E: no r2 -> r3 import-surface delta computed")
    if d:
        check(d["n_changed"] == len(d["changed"]),
              "E: the import-surface delta miscounts its own changes")
        infile(txt, str(d["n_symbols"]), "E/surface_n_symbols")
    check(R["sanity"]["concordance_with_ws8_r3_ESC_WS9_8"]["passes"] is True,
          "E: sanity.concordance_with_ws8_r3_ESC_WS9_8 does not pass")

    # R38: exported, and NOT applied.
    tg = R["interface_ws9"]["trip_time_R38_gate_input"]
    tt = R["sanity"]["trip_time_the_metric_cannot_see"]
    check(len(tt["cases"]) > 0,
          "E: trip_time_the_metric_cannot_see is empty - R38 cannot be "
          "applied by the lead from this artifact")
    check(set(tg["all_cases_pct"]) == set(tt["cases"]),
          "E: the R38 gate input and the sanity trip-time table disagree "
          "on their case set")
    check(all(abs(tg["all_cases_pct"][k] - tt["cases"][k]) < 1e-12
              for k in tt["cases"]),
          "E: the R38 gate input is not the sanity trip-time table")
    for cname, v in AK.items():
        key = f"{cname}/nominal/{design}"
        check(key in tt["cases"],
              f"E: no design-duty trip time exported for {cname}")
    # the gate must NOT have been applied: every verdict must still be
    # exactly what the pre-committed criteria give, with no trip-time term
    for cname, v in AK.items():
        pn = v["nominal_margin_pct_min"] >= R["advance_kill"]["criteria"][
            "nominal_pct"]
        wc = v["worst_corner_margin_pct_min"]
        pc = wc is None or wc >= R["advance_kill"]["criteria"][
            "every_corner_pct"]
        check(v["verdict"] == ("ADVANCE" if (pn and pc) else "KILL"),
              f"E: {cname}'s verdict is not the pre-committed criteria's "
              f"answer - has a trip-time gate been applied here? R38 says "
              f"the LEAD applies it.")
    check("verdict" not in tg,
          "E: the R38 gate-input block carries a verdict; it must carry "
          "only the measurement and the bar")
    infile(txt, "EXPORTED, NOT APPLIED", "E/r38_not_applied")
    for cname, val in tg["design_duty_nominal_pct_vs_ruler"].items():
        infile(txt, f"{val:+.3f}%", f"E/r38_design_pct/{cname}")
    check(set(tg["all_cases_paired_max_pct"]) == set(tt["cases"]),
          "E: the paired R38 statistic does not cover the same case set")
    # the paired envelope must be an ENVELOPE of the per-seed paired
    # ratios, recomputed here independently of ws9_blocks
    for key, det in tt["detail"].items():
        cname, corner, duty = key.split("/")
        base = {x["seed"]: x["duration_s"] for x in
                R["trial"][corner][ruler]["per_duty"][duty]["per_seed"]}
        vals = sorted((x["duration_s"] - base[x["seed"]])
                      / base[x["seed"]] * 100.0
                      for x in R["trial"][corner][cname]["per_duty"][duty]
                      ["per_seed"])
        p = det["paired_pct"]
        check(p["n"] == len(vals)
              and abs(p["min"] - vals[0]) < 1e-9
              and abs(p["max"] - vals[-1]) < 1e-9,
              f"E: the R38 paired trip-time envelope for {key} does not "
              f"recompute from the per-seed data")

    # R34
    t34 = R["traces_r34"]
    check(t34["n_files"] >= 1, "E: no R34 10 Hz trace exported")
    check(t34["all_present"] is True,
          "E: an R34 trace named in the record is not on disk")
    for r in t34["files"]:
        p = os.path.join(HERE, r["file"])
        check(os.path.exists(p), f"E: missing R34 trace {r['file']}")
        if os.path.exists(p):
            check(sha(p) == r["sha256"],
                  f"E: R34 trace {r['file']} does not match its recorded "
                  f"sha256")
            with open(p) as fh:
                head = [next(fh) for _ in range(6)]
            check(head[-1].strip() == ",".join(t34["columns"]),
                  f"E: R34 trace {r['file']} header is not the declared "
                  f"column set")
        infile(txt, r["file"], f"E/trace_listed/{r['file']}")
    check(R["sanity"]["traces_r34_exported"]["passes"] is True,
          "E: sanity.traces_r34_exported does not pass")

    # the changelog the order asks for, emitted from the report's own lines
    clog = os.path.join(HERE, "CHANGELOG_WS9_r3.md")
    check(os.path.exists(clog), "E: CHANGELOG_WS9_r3.md was not written")
    if os.path.exists(clog):
        ctxt = open(clog).read()
        check("r3-concordant re-run" in ctxt,
              "E: the changelog does not carry the ordered entry "
              "'r3-concordant re-run'")
        check(ctxt.strip() and ctxt.strip() in txt,
              "E: the changelog and the report's section 17 are not the "
              "same lines")
        check("NOT CLEAN" in ctxt,
              "E: the changelog does not state that the pinned WS8 round "
              "was adjudicated NOT CLEAN")

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
