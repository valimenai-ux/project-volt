"""
Project Volt - WS5
Byte-stability check (CLAUDE.md binding rule 1): re-run the whole pipeline
into a scratch tree and compare every committed artifact byte-for-byte.

    ./.venv/bin/python check_determinism_ws5.py

Exits 0 only if every artifact is byte-identical.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = ["results_ws5.json", "REPORT_WS5.md"]
ARTIFACT_DIRS = ["data", "figs"]
SOURCES = ["run_ws5.py", "make_report_ws5.py", "verify_ws5.py",
           "ws5_inputs.py", "ws5_statemachine.py", "ws5_supervisor.py",
           "ws5_scenarios.py", "requirements.txt"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def collect(root):
    out = {}
    for a in ARTIFACTS:
        p = os.path.join(root, a)
        if os.path.exists(p):
            out[a] = sha(p)
    for d in ARTIFACT_DIRS:
        dd = os.path.join(root, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            p = os.path.join(dd, fn)
            if os.path.isfile(p):
                out[f"{d}/{fn}"] = sha(p)
    return out


def main():
    before = collect(HERE)
    if not before:
        print("nothing to compare - run run_ws5.py first")
        return 1
    tmp = tempfile.mkdtemp(prefix="ws5_determinism_")
    scratch = os.path.join(tmp, "WS5_controls")
    os.makedirs(scratch)
    # WS5 resolves its upstream inputs relative to its own parent, so the
    # scratch tree needs the same shape. The upstream folders are symlinked
    # READ-ONLY - nothing outside WS5_controls is written by this check.
    root = os.path.normpath(os.path.join(HERE, ".."))
    for up in ("WS1_loads_duty_cycles", "WS2_traction_motor",
               "WS3_battery", "WS4_genset"):
        src = os.path.join(root, up)
        if os.path.isdir(src):
            os.symlink(src, os.path.join(tmp, up))
    for s in SOURCES:
        shutil.copy2(os.path.join(HERE, s), scratch)
    os.makedirs(os.path.join(scratch, "data"), exist_ok=True)
    os.makedirs(os.path.join(scratch, "figs"), exist_ok=True)
    py = os.path.join(HERE, ".venv", "bin", "python")
    py = py if os.path.exists(py) else sys.executable
    for step in ("run_ws5.py", "make_report_ws5.py"):
        r = subprocess.run([py, step], cwd=scratch, capture_output=True,
                           text=True)
        if r.returncode != 0:
            print(f"{step} failed in the scratch tree:\n{r.stdout[-3000:]}"
                  f"\n{r.stderr[-3000:]}")
            return 1
    after = collect(scratch)
    bad = []
    for k, v in before.items():
        if k not in after:
            bad.append(f"{k}: MISSING in the re-run")
        elif after[k] != v:
            bad.append(f"{k}: {v[:12]} -> {after[k][:12]}")
    for k in after:
        if k not in before:
            bad.append(f"{k}: EXTRA in the re-run")
    print(f"compared {len(before)} artifacts")
    for k in sorted(before):
        mark = "OK " if after.get(k) == before[k] else "DIFF"
        print(f"  {mark} {k}  {before[k][:16]}")
    shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("\nBYTE-STABILITY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print("\nBYTE-STABLE: every artifact reproduced byte-for-byte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
