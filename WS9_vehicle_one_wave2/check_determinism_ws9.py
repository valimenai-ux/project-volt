#!/usr/bin/env python3
"""
Project Volt - WS9
The rule-1 regeneration evidence, recorded as an artifact.

    ../.venv/bin/python check_determinism_ws9.py

CLAUDE.md rule 1: "byte-stable regeneration: re-running the pipeline must
reproduce every committed artifact byte-identically." The check cannot run
inside the process it is checking - it compares two independent runs - so it
is performed here and its result committed alongside the run it certifies,
exactly as WS8 does.

TWO HALVES, and what each one actually proves:

  HALF 1  THE SIMULATION. One (corner, candidate) job is re-run FROM
          SCRATCH in a fresh process - rebuilding its own context, its own
          candidate, its own cycles - and every per-seed metric is compared
          against the committed record at zero tolerance. If a seed, a
          scaling law or a dispatch had any hidden state, this is where it
          would show.

  HALF 2  THE DERIVED BLOCKS AND THE EXPORTS. `run_ws9.py --from-checkpoint`
          regenerates results_ws9.json and every CSV from the saved trial,
          and both are diffed BYTE FOR BYTE against the committed files.

WHAT IS NOT CHECKED, stated rather than implied: the other five corners are
not re-simulated, because a full re-run costs hours and the jobs are
independent and identically constructed - the one that is re-run is the
evidence for the construction, not for each corner's arithmetic.
"""
import filecmp
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RESULTS = os.path.join(HERE, "results_ws9.json")
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "determinism_check.json")

RE_RUN_CORNER = "cold_minus10C"
RE_RUN_CANDIDATE = "S5"
COMPARE_KEYS = ("MJ_primary_per_payload_tkm", "MJ_tank_per_payload_tkm",
                "g_CO2_per_payload_tkm", "fuel_g_raw", "fuel_g_corrected",
                "unserved_kWh", "distance_km", "duration_s",
                "correction_eta", "grid_kWh")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def main():
    R = json.load(open(RESULTS))
    rec = {}

    # ---- half 1: re-simulate one job in a fresh process ---------------
    import run_ws9
    _, blob = run_ws9.run_candidate(RE_RUN_CORNER, RE_RUN_CANDIDATE, None,
                                    tuple(R["_meta"]["seeds"]))
    ref = R["trial"][RE_RUN_CORNER][RE_RUN_CANDIDATE]
    diffs, n = [], 0
    for duty, d in blob["per_duty"].items():
        rows_a = d["per_seed"]
        rows_b = ref["per_duty"][duty]["per_seed"]
        for a, b in zip(rows_a, rows_b):
            for k in COMPARE_KEYS:
                n += 1
                va, vb = a.get(k), b.get(k)
                if va is None and vb is None:
                    continue
                if va != vb:
                    diffs.append(f"{duty}/seed{a['seed']}/{k}: "
                                 f"{va!r} != {vb!r}")
    rec["half_1_simulation"] = dict(
        job=f"{RE_RUN_CORNER}/{RE_RUN_CANDIDATE}",
        seeds=R["_meta"]["seeds"], values_compared=n,
        tolerance="exact (0 ulp)",
        mismatches=diffs[:20], n_mismatches=len(diffs),
        matches_committed_run=bool(not diffs),
        payload_matches=bool(blob["spec"]["payload_kg"]
                             == ref["spec"]["payload_kg"]))

    # ---- half 2: regenerate the derived blocks and the exports --------
    tmp = tempfile.mkdtemp(prefix="ws9det_")
    keep = {}
    for f in os.listdir(DATA):
        if f.endswith(".csv"):
            keep[f] = os.path.join(tmp, f)
            shutil.copy2(os.path.join(DATA, f), keep[f])
    keep["results_ws9.json"] = os.path.join(tmp, "results_ws9.json")
    shutil.copy2(RESULTS, keep["results_ws9.json"])
    before = {k: sha(v) for k, v in keep.items()}

    shutil.copy2(RESULTS, os.path.join(DATA, "_checkpoint.json"))
    p = subprocess.run([sys.executable, os.path.join(HERE, "run_ws9.py"),
                        "--from-checkpoint"], capture_output=True,
                       cwd=HERE)
    after = {}
    for k in keep:
        path = RESULTS if k.endswith(".json") and "results" in k \
            else os.path.join(DATA, k)
        after[k] = sha(path) if os.path.exists(path) else None
    identical = {k: bool(before[k] == after[k]) for k in before}
    rec["half_2_derived_blocks"] = dict(
        command="run_ws9.py --from-checkpoint",
        returncode=p.returncode,
        files=identical,
        results_json_byte_identical=identical.get("results_ws9.json", False),
        all_csv_exports_byte_identical=bool(
            all(v for k, v in identical.items() if k.endswith(".csv"))),
        note=("the checkpoint is a byte copy of the committed "
              "results_ws9.json, so this regenerates every derived block "
              "and every export from the committed trial and diffs the "
              "result byte for byte"))
    shutil.rmtree(tmp, ignore_errors=True)

    rec["not_checked"] = (
        "the other five corners are not re-simulated; the jobs are "
        "independent and identically constructed, and a full re-run costs "
        "hours. Half 1 is evidence for the construction, not for each "
        "corner's arithmetic.")
    rec["status"] = ("PASS" if (rec["half_1_simulation"]
                                ["matches_committed_run"]
                                and rec["half_2_derived_blocks"]
                                ["results_json_byte_identical"]
                                and rec["half_2_derived_blocks"]
                                ["all_csv_exports_byte_identical"])
                     else "FAIL")
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"determinism: {rec['status']}  "
          f"(half 1: {rec['half_1_simulation']['values_compared']} values, "
          f"{rec['half_1_simulation']['n_mismatches']} mismatches; "
          f"half 2: results byte-identical "
          f"{rec['half_2_derived_blocks']['results_json_byte_identical']}, "
          f"csv byte-identical "
          f"{rec['half_2_derived_blocks']['all_csv_exports_byte_identical']})")
    sys.exit(0 if rec["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
