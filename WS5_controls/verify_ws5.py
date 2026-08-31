"""
Project Volt - WS5
Verifies REPORT_WS5.md against results_ws5.json VERBATIM.

Nothing in the report is transcribed by hand: make_report_ws5.py records
every rendered number in data/report_number_manifest.csv as
(json_path, format, rendered_string). This script:

  1. re-fetches each value from results_ws5.json by its path,
  2. re-formats it with the recorded format and asserts it reproduces the
     recorded string exactly,
  3. asserts the string actually appears in the rendered report,
  4. runs the structural checks the program rules require (R14 export
     discipline, 8-seed ensembles, the interface block, and the
     post-Gate-G1 absence of any clutch/mode state).

Exit 0 only if every check passes.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEP = "|"
FAIL = []


def fail(msg):
    FAIL.append(msg)


def fetch(R, path):
    node = R
    for k in path.split(SEP):
        if isinstance(node, list):
            node = node[int(k)]
        else:
            node = node[k]
    return node


def main():
    with open(os.path.join(HERE, "results_ws5.json")) as f:
        R = json.load(f)
    with open(os.path.join(HERE, "REPORT_WS5.md")) as f:
        report = f.read()
    man_path = os.path.join(HERE, "data", "report_number_manifest.csv")
    with open(man_path) as f:
        rows = list(csv.DictReader(f))

    # ---- 1-3: every rendered number verifies verbatim -------------------
    n_ok = n_missing = 0
    for row in rows:
        path, fmt, rendered = row["json_path"], row["format"], row["rendered"]
        try:
            val = fetch(R, path)
        except (KeyError, IndexError, TypeError) as e:
            fail(f"path not in results_ws5.json: {path} ({e})")
            continue
        if fmt == "{}#json":
            # a boolean rendered the way JSON spells it, for the fenced
            # ```json interface block in section 11
            again = ("true" if val is True
                     else "false" if val is False else str(val))
        else:
            try:
                again = fmt.format(val)
            except (ValueError, TypeError):
                again = str(val)
        if again != rendered:
            # SHA prefixes and long declared strings are recorded as a
            # prefix / substring of the JSON value; anything else is a
            # genuine mismatch.
            if isinstance(val, str) and (val.startswith(rendered)
                                         or rendered in val):
                pass
            else:
                fail(f"re-format mismatch at {path}: json {val!r} -> "
                     f"{again!r} != report {rendered!r}")
                continue
        if rendered not in report:
            n_missing += 1
            fail(f"rendered value not found in REPORT_WS5.md: {rendered!r} "
                 f"(from {path})")
            continue
        n_ok += 1

    # ---- 4a: R14 export discipline --------------------------------------
    def walk(node, path=""):
        if isinstance(node, dict):
            keys = set(node.keys())
            for k, v in node.items():
                if k == "worst_case_value":
                    if "governing_case" not in keys:
                        fail(f"R14: {path} has worst_case_value with no "
                             f"governing_case")
                    if not (keys & {"cases", "rule", "case_set"}):
                        fail(f"R14: {path} has worst_case_value with no "
                             f"enumerated case set or rule")
                if k == "value" and "governing_case" in keys \
                        and not (keys & {"cases", "case_set"}):
                    fail(f"R14: {path} has value/governing_case but no "
                         f"enumerated case set")
                # any dict that looks like an ensemble export (it carries at
                # least one *_governing_case label) must label EVERY one of
                # its min/max members
                is_ens = any(kk.endswith("_governing_case") for kk in keys)
                if is_ens and (k.endswith("_min") or k.endswith("_max")) \
                        and isinstance(v, (int, float)) \
                        and not isinstance(v, bool):
                    if f"{k}_governing_case" not in keys:
                        fail(f"R14: {path}.{k} has no governing case label")
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(R)

    # ---- 4b: ensembles are 8-seed --------------------------------------
    seeds_reg = R["_meta"]["seeds"]["VOLT_REG"]
    seeds_sub = R["_meta"]["seeds"]["VOLT_SUB"]
    if len(seeds_reg) != 8 or len(seeds_sub) != 8:
        fail("R9: ensembles are not 8-seed")
    for cn, cd in R["dispatch_trade_v2_r22b"]["cases"].items():
        for st, sd in cd["strategies"].items():
            per = sd["per_seed_fuel_energy_kWh_per_km"]
            if len(per) != 8:
                fail(f"R9: {cn}/{st} per-seed export has {len(per)} seeds")
            if sorted(int(k) for k in per) != sorted(seeds_reg):
                fail(f"R9: {cn}/{st} seed set does not match the ensemble")
    v1 = R["v1_dispatch_r19"]["per_seed_starts_per_8h_shift"]
    if sorted(int(k) for k in v1) != sorted(seeds_sub):
        fail("R9: V1 seed set does not match the VOLT-SUB ensemble")

    # ---- 4c: no clutch / mode / sync state anywhere ---------------------
    if R["sanity_checks"]["state_machine_validation"]["_has_clutch_state"]:
        fail("BASELINE_v3: a clutch/lockup/sync/mode state is present")
    if not R["sanity_checks"]["state_machine_validation"]["_all_regions_ok"]:
        fail("state machine structural validation failed")
    for bad in ("clutch", "lockup", "sync", "mode selection"):
        for reg, sts in R["state_machine"]["states"].items():
            for st in sts:
                if bad.split()[0] in st.lower():
                    fail(f"state {reg}.{st} looks like a deleted concept")

    # ---- 4d: the WS4 concordance is exact -------------------------------
    if R["concordance_ws4"]["max_abs_delta_all_fields_all_seeds_all_cases"] \
            != 0.0:
        fail("WS4 concordance is no longer exact")

    # ---- 4e: the interface block exists and is populated ---------------
    IF = R["interface_ws5"]
    for k in ("supervisor", "dispatch_v2_r22b", "dispatch_v1_r19",
              "blend_order_r15", "traction_control_e23",
              "dispatch_limit_esc9", "heat_cases_to_ws6",
              "heat_worst_cases_to_ws6", "test_vectors_to_ws7",
              "trace_files_r34", "consumed_vintage"):
        if k not in IF:
            fail(f"interface_ws5 is missing {k}")
    if len(IF["test_vectors_to_ws7"]) < 1:
        fail("interface_ws5.test_vectors_to_ws7 is empty")

    # ---- 4f: R34 traces exist, are 10 Hz, and are non-trivial ----------
    for k, d in R["trace_files"].items():
        if k.startswith("_"):
            continue
        p = os.path.join(HERE, d["file"])
        if not os.path.exists(p):
            fail(f"R34 trace missing on disk: {d['file']}")
            continue
        if d["rate_Hz"] != 10.0:
            fail(f"R34 trace {d['file']} is not 10 Hz")
        with open(p) as f:
            n = sum(1 for _ in f)
        if n < d["rows"]:
            fail(f"R34 trace {d['file']} has fewer rows than declared")

    # ---- 4g: no wall-clock timestamp leaked into the results -----------
    blob = json.dumps(R)
    for tok in ("2026-08-31T", "GMT", "UTC+"):
        if tok in blob:
            fail(f"a wall-clock timestamp leaked into results_ws5.json: "
                 f"{tok}")

    # ---- report --------------------------------------------------------
    print(f"manifest entries verified verbatim : {n_ok} / {len(rows)}")
    print(f"rendered values not found in report: {n_missing}")
    print(f"R14 / R9 / R34 / interface checks  : "
          f"{'PASS' if not FAIL else 'FAIL'}")
    if FAIL:
        print("\nFAILURES:")
        for m in FAIL[:60]:
            print("  - " + m)
        if len(FAIL) > 60:
            print(f"  ... and {len(FAIL)-60} more")
        return 1
    print("\nVERIFIED: every headline number in REPORT_WS5.md is generated "
          "from, and verifies verbatim against, results_ws5.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
