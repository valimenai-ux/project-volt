"""WS12 — the single entry point.

    ../.venv/bin/python3 run_ws12.py [--with-app]

Runs the pipeline in the order the artifacts depend on each other:

  1  build_exhibit_data.py   read the record, emit the data bundle, the
                             decimated traces, the maps and both manifests
  2  exhibit_verify.py       checks 1-12; writes verify_summary.json
  3  make_report_ws12.py     render REPORT_WS12.md from the results data,
                             recording every assertion
  4  exhibit_verify.py       checks 1-13, now including the report
  5  make_report_ws12.py     re-render so the report's own verify table is
                             the run that judged it
  6  exhibit_verify.py       final pass; must be a fixed point

Step 5 exists because the report prints the verifier's own counts, so the
last two passes must agree byte for byte. If they do not, this script
says so and fails.

`--with-app` additionally runs `npm ci`/`npm run build` in `app/` before
the final verify, so that check 7's built-bundle scan has something to
read.
"""

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
APP = os.path.join(HERE, "app")
REPORT = os.path.join(HERE, "REPORT_WS12.md")


def run(script, *args):
    r = subprocess.run([PY, os.path.join(HERE, script), *args], cwd=HERE)
    return r.returncode


def digest(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    with_app = "--with-app" in sys.argv

    print("\n[1/6] build_exhibit_data.py")
    if run("build_exhibit_data.py"):
        return 1

    if with_app:
        print("\n[--] npm run build")
        if not os.path.isdir(os.path.join(APP, "node_modules")):
            subprocess.run(["npm", "ci"], cwd=APP, check=False)
        if subprocess.run(["npm", "run", "build"], cwd=APP).returncode:
            return 1

    print("\n[2/6] exhibit_verify.py (pre-report)")
    run("exhibit_verify.py")

    print("\n[3/6] make_report_ws12.py")
    if run("make_report_ws12.py"):
        return 1

    print("\n[4/6] exhibit_verify.py")
    if run("exhibit_verify.py"):
        return 1

    before = digest(REPORT)
    print("\n[5/6] make_report_ws12.py (fixed point)")
    if run("make_report_ws12.py"):
        return 1
    after = digest(REPORT)

    print("\n[6/6] exhibit_verify.py (final)")
    rc = run("exhibit_verify.py")
    if rc:
        return 1

    if before != after:
        print("\nREPORT_WS12.md did not reach a fixed point: %s -> %s"
              % (before[:12], after[:12]))
        print("re-running once more")
        if run("make_report_ws12.py"):
            return 1
        if run("exhibit_verify.py"):
            return 1
        if digest(REPORT) != after:
            print("\nFAIL: the report is not byte-stable across runs")
            return 1

    print("\nWS12 PIPELINE COMPLETE — report and verifier agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
