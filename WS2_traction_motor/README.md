# WS2 — traction motor / inverter / reduction / brake resistor / DC bus

Regenerate everything:

    python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
    ./.venv/bin/python run_ws2.py        # writes data/*.csv, results.json, run_output.txt (~15 s)
    ./.venv/bin/python check_report.py   # verifies REPORT_WS2.md against results.json

Deterministic: no RNG anywhere; consumed WS1 extrema are its published
8-seed ensemble envelopes (R9). Inputs read from ../WS1_loads_duty_cycles/
(results.json + 10 Hz reference traces); nothing outside this folder is
written.

Deliverable: REPORT_WS2.md. Interface for WS3/WS4/WS5: `interface` block
in results.json (mirrored verbatim in the report), efficiency maps and
derate curves under data/.
