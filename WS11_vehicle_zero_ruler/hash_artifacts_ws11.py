"""
Project Volt - WS11
Hashes the committed artefact set, for the byte-stability record.

    python hash_artifacts_ws11.py > determinism_check.txt

Run it after two consecutive full `run_ws11.py` + `make_report_ws11.py`
passes and diff the two outputs. The report's byte-stability claim is the
measured result of doing exactly that, for THIS round's code - it is not
carried forward from a previous round.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

FILES = ["results_ws11.json", "REPORT_WS11.md", "run_output.txt"]
FILES += sorted("data/" + f for f in os.listdir("data") if f.endswith(".csv"))

for f in FILES:
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    print(f"{h.hexdigest()}  {os.path.getsize(f):>10}  {f}")
