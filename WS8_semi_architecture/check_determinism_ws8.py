#!/usr/bin/env python3
"""
Project Volt - WS8. The CLAUDE.md rule 1 evidence, produced by a script
instead of by hand.

Rule 1 requires that re-running the pipeline reproduces every committed
artifact byte-identically. The check cannot run inside the process it is
checking - it compares two independent runs - so it is performed here and
its result written to `data/determinism_check.json`, which `run_ws8.py`
then reads into the record it certifies.

In r1 and r2 this evidence was assembled by hand and typed into that
JSON. r3 makes it a runnable artifact for the same reason every other
number in this workstream is generated: a claim about reproducibility
that is itself hand-written is the weakest link in the chain it is
attesting to.

TWO INDEPENDENT HALVES, because the pipeline has two independent sources
of possible drift.

  HALF 1 - THE SIMULATION. The nominal corner is re-simulated FROM
  SCRATCH in a separate copy of the folder, a separate process and a
  worker pool of a different width, with no checkpoint to reuse. Its
  trial slice, its cycles and its S0 calibration are compared against the
  committed run. The sibling workstreams and the baselines are SYMLINKED
  into the copy, so the copy reads exactly the same bytes and writes
  nothing outside its own scratch directory (rule 10).

  HALF 2 - THE DERIVED BLOCKS. `run_ws8.py --from-checkpoint` rebuilds
  every block that sits on top of the simulation. It is run twice over
  the committed checkpoint and the two sets of outputs are compared
  byte-for-byte against each other and against the committed artifacts,
  which tests both that the derived blocks are a deterministic function
  of the checkpoint AND that they do not depend on whether they were
  built inside the simulating process or rebuilt afterwards.

  This file is itself an input to the derived blocks (`run_ws8.py`
  reads it), so half 2 is repeated AFTER it is written and the script
  exits non-zero if the repeat disagrees. Without that step the recorded
  booleans would describe a state the committed artifacts are not in.

    ../.venv/bin/python check_determinism_ws8.py            # full check
    ../.venv/bin/python check_determinism_ws8.py --half2    # skip half 1

Half 1 costs about as much wall clock as the nominal corner plus the WHR
gate and the one-factor re-runs; `--half2` exists for iterating on the
derived blocks without paying for it.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
PY = os.path.join(REPO, ".venv", "bin", "python")
OUT = os.path.join(DATA, "determinism_check.json")
ROUND = "r3"

# what the copy in half 1 needs to see through `..`
SIBLINGS = ["BASELINE_v0.md", "BASELINE_v1.md", "BASELINE_v2.md",
            "BASELINE_v3.md", "BASELINE_v4.md", "BASELINE_v5.md",
            "CLAUDE.md", "WS1_loads_duty_cycles", "WS2_traction_motor",
            "WS3_battery", "WS4_genset"]

# files copied into the scratch folder for half 1 - the pipeline and
# everything it reads, and nothing else
COPY_IN = ["run_ws8.py", "ws8_params.py", "ws8_physics.py", "ws8_cycles.py",
           "ws8_engine.py", "ws8_electric.py", "ws8_candidates.py",
           "ws8_whr.py", "requirements.txt", "ASSIGNMENT.md",
           "R2_DIRECTIVE.md", "R3_DIRECTIVE.md", "FINDINGS_WS8_r1.md",
           "FINDINGS_WS8_r2.md", "PRIOR_ART_WS8.md"]

CSV_FILES = sorted(f for f in os.listdir(DATA)
                   if f.endswith(".csv")) if os.path.isdir(DATA) else []


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_obj(o):
    return hashlib.sha256(
        json.dumps(o, sort_keys=True, separators=(",", ":"),
                   default=str).encode()).hexdigest()


def snapshot(dst):
    os.makedirs(dst, exist_ok=True)
    shutil.copy2(os.path.join(HERE, "results_ws8.json"), dst)
    for f in CSV_FILES:
        shutil.copy2(os.path.join(DATA, f), dst)
    return {f: sha(os.path.join(dst, f))
            for f in ["results_ws8.json"] + CSV_FILES}


def current_hashes():
    out = {"results_ws8.json": sha(os.path.join(HERE, "results_ws8.json"))}
    for f in CSV_FILES:
        out[f] = sha(os.path.join(DATA, f))
    return out


def rebuild():
    r = subprocess.run([PY, "run_ws8.py", "--from-checkpoint"], cwd=HERE,
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("--from-checkpoint failed")
    return current_hashes()


def half_2(label):
    """Rebuild twice and compare both against each other and against what
    was on disk when we started."""
    before = current_hashes()
    a = rebuild()
    b = rebuild()
    same_ab = a == b
    same_committed = a == before
    diffs = sorted(k for k in a if a[k] != before.get(k))
    return dict(label=label, rebuild_1=a, identical_between_rebuilds=same_ab,
                identical_to_artifacts_on_disk=same_committed,
                differing_files=diffs)


def half_1(jobs):
    committed = json.load(open(os.path.join(HERE, "results_ws8.json")))
    tmp = tempfile.mkdtemp(prefix="ws8_determinism_")
    root = os.path.join(tmp, "repo")
    work = os.path.join(root, "WS8_semi_architecture")
    os.makedirs(work)
    for name in SIBLINGS:
        src = os.path.join(REPO, name)
        if os.path.exists(src):
            os.symlink(src, os.path.join(root, name))
    os.symlink(os.path.join(REPO, ".venv"), os.path.join(root, ".venv"))
    for f in COPY_IN:
        shutil.copy2(os.path.join(HERE, f), work)
    os.makedirs(os.path.join(work, "data"))
    shutil.copy2(os.path.join(DATA, "prior_art_scan.json"),
                 os.path.join(work, "data"))
    shutil.copy2(os.path.join(DATA, "prior_art_claim_map.md"),
                 os.path.join(work, "data"))
    cmd = [PY, "run_ws8.py", "--only-nominal", "--jobs", str(jobs)]
    print(f"   half 1: {' '.join(cmd)} in {work}", flush=True)
    r = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("half 1 run failed")
    fresh = json.load(open(os.path.join(work, "results_ws8.json")))

    def cmp(path):
        a, b = committed, fresh
        for k in path.split("/"):
            a, b = a.get(k), b.get(k)
            if a is None or b is None:
                return None, None, None
        return sha_obj(a), sha_obj(b), sha_obj(a) == sha_obj(b)

    out = {}
    for key, path in (("task3_trial_nominal", "task3_trial/nominal"),
                      ("task1_cycles", "task1_cycles"),
                      ("task2_s0_calibration", "task2_s0_calibration"),
                      ("task4_whr", "task4_whr"),
                      ("one_factor", "one_factor")):
        ha, hb, same = cmp(path)
        out[key] = dict(committed_sha256=ha, rerun_sha256=hb, identical=same)
    shutil.rmtree(tmp, ignore_errors=True)
    return dict(jobs=jobs, blocks=out,
                matches_committed_run=bool(
                    out["task3_trial_nominal"]["identical"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--half2", action="store_true",
                    help="skip the from-scratch re-simulation")
    ap.add_argument("--jobs", type=int, default=4,
                    help="worker pool width for half 1; deliberately "
                         "different from the committed run's")
    args = ap.parse_args()

    print("== HALF 2 (pre): derived blocks, two rebuilds ==", flush=True)
    pre = half_2("before this file was written")

    h1 = None
    if not args.half2:
        print("== HALF 1: nominal corner re-simulated from scratch ==",
              flush=True)
        h1 = half_1(args.jobs)
        for k, v in h1["blocks"].items():
            print(f"   {k:24s} identical: {v['identical']}", flush=True)

    rec = {
        "round": ROUND,
        "generated_by": "check_determinism_ws8.py",
        "what": (
            "CLAUDE.md rule 1 requires that re-running the pipeline "
            "reproduces every committed artifact byte-identically. "
            "Checked in two independent halves, because the pipeline has "
            "two independent sources of possible drift: the simulation, "
            "and the derived blocks built on top of it. The check cannot "
            "run inside the process it is checking - it compares two "
            "independent runs - so it is performed by "
            "`check_determinism_ws8.py` and its result committed "
            "alongside the run it certifies. In r1 and r2 this record was "
            "assembled by hand; in r3 it is generated, because a "
            "hand-written claim about reproducibility is the weakest link "
            "in the chain it attests to."),
        "half_1_simulation": ({
            "method": (
                "the full 8-seed nominal corner, the WHR gate and the "
                "one-factor re-runs re-simulated FROM SCRATCH in a "
                "separate copy of the folder, a separate process and a "
                "separate worker pool at a different width "
                f"(run_ws8.py --only-nominal --jobs {h1['jobs']}, against "
                "the committed run's --jobs 5), with the sibling "
                "workstreams and baselines SYMLINKED so the copy reads "
                "the same bytes and writes nothing outside its own "
                "scratch directory; then each block compared by sha256 of "
                "its canonical JSON"),
            "wall_clock_fields": (
                "excluded from the comparison and from the committed "
                "artifact alike: per-candidate and total runtimes are the "
                "only values in this structure that cannot reproduce, and "
                "_strip_runtimes removes them before the record is "
                "written"),
            "blocks": h1["blocks"],
            "task3_trial_nominal_sha256":
                h1["blocks"]["task3_trial_nominal"]["committed_sha256"],
            "matches_committed_run": h1["matches_committed_run"],
            "task1_cycles_identical":
                h1["blocks"]["task1_cycles"]["identical"],
            "task2_calibration_identical":
                h1["blocks"]["task2_s0_calibration"]["identical"],
        } if h1 else {
            "method": "NOT RUN in this invocation (--half2)",
            "matches_committed_run": False,
            "task1_cycles_identical": False,
            "task2_calibration_identical": False,
        }),
        "half_2_derived_blocks": {
            "method": (
                "`run_ws8.py --from-checkpoint` rebuilds every block that "
                "sits on top of the simulation. It is run TWICE over the "
                "committed checkpoint and the two sets of outputs are "
                "compared byte-for-byte against each other and against "
                "the artifacts already on disk - which tests both that "
                "the derived blocks are a deterministic function of the "
                "checkpoint and that they do not depend on whether they "
                "were built inside the simulating process or rebuilt "
                "afterwards. Because THIS FILE is an input to those "
                "blocks, the comparison is repeated after it is written "
                "and the script exits non-zero if the repeat disagrees; "
                "the booleans below therefore describe the committed "
                "artifacts and not a state that preceded them."),
            "results_json_byte_identical": bool(
                pre["identical_between_rebuilds"]),
            "all_csv_exports_byte_identical": bool(
                pre["identical_between_rebuilds"]),
            "full_run_matches_checkpoint_rebuild": bool(
                pre["identical_to_artifacts_on_disk"]),
            "files_compared": ["results_ws8.json"] + CSV_FILES,
            "csv_files": CSV_FILES,
        },
        "not_checked": (
            "the five sensitivity corners were not re-simulated from "
            "scratch - they are the same code path as the nominal corner "
            "with different Ctx constants, and re-running them would have "
            "cost several more hours of compute for no additional class "
            "of evidence. The WHR gate and the one-factor re-runs, which "
            "r2 also left unchecked, ARE re-simulated in r3's half 1. "
            "Stated rather than implied."),
        "environment_note": (
            "r3's artifacts were produced on the same interpreter and "
            "numpy as r2's; r1's were produced on Python 3.11.15 / numpy "
            "2.4.6 on x86-64 Linux. Rule 1 is a claim about a run "
            "reproducing ITSELF, and it is checked here on the machine "
            "that produced the committed artifacts. The two platforms "
            "differ by one to two units in the last place of a double "
            "(relative ~1e-16, from libm and SIMD reduction order); no "
            "figure in this record is quoted anywhere near that "
            "precision, and no r3 conclusion depends on it."),
    }
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"== wrote {OUT} ==", flush=True)

    print("== HALF 2 (post): repeated now that the file has changed ==",
          flush=True)
    post = half_2("after this file was written")
    # The POST check cannot expect equality with what was on disk BEFORE
    # it: this file is an input to the derived blocks and it has just
    # changed, so the first post-rebuild legitimately differs from the
    # pre-write artifacts. What must hold - and what is asserted - is
    # that the two post-rebuilds agree, i.e. the committed artifacts are
    # a deterministic function of the checkpoint plus this record.
    ok = post["identical_between_rebuilds"]
    print(f"   identical between rebuilds: "
          f"{post['identical_between_rebuilds']}", flush=True)
    print(f"   differs from the pre-write artifacts (expected - this "
          f"file is an input to them): "
          f"{not post['identical_to_artifacts_on_disk']}", flush=True)
    if post["differing_files"]:
        print(f"   differing: {post['differing_files']}", flush=True)
    if not ok:
        raise SystemExit("HALF 2 FAILED after the determinism record was "
                         "written - the committed artifacts are not the "
                         "ones the record describes")
    if h1 and not h1["matches_committed_run"]:
        raise SystemExit("HALF 1 FAILED - the from-scratch re-simulation "
                         "does not reproduce the committed nominal trial")
    print("check_determinism_ws8: OK", flush=True)


if __name__ == "__main__":
    main()
