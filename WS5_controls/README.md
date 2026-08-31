# WS5 — supervisory controls (Vehicle Zero, dual-series)

Assignment: `ASSIGNMENT.md`. Baseline of record: the highest-numbered
`BASELINE_v*.md` at the repository root (BASELINE_v5 at the time of this
artifact; the assignment cites v3, which v4/v5 supersede).

## Regenerate and verify

```
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python run_ws5.py > run_output.txt
./.venv/bin/python make_report_ws5.py
./.venv/bin/python verify_ws5.py
./.venv/bin/python check_determinism_ws5.py
```

`run_ws5.py` is the single entry point. It writes `results_ws5.json`,
`data/*.csv` (including the R34 10 Hz traces) and `figs/*.png`.
`make_report_ws5.py` renders `REPORT_WS5.md` from `results_ws5.json` alone —
no number is transcribed by hand. `verify_ws5.py` re-reads the rendered
report and asserts every headline number against the results file verbatim.
`check_determinism_ws5.py` re-runs the pipeline into a scratch tree and
compares every artifact byte-for-byte.

## Files

| file | role |
|---|---|
| `ws5_inputs.py` | the single hot-swap seam: all upstream consumption + SHA256 provenance |
| `ws5_statemachine.py` | the supervisor state machine — specification **and** implementation |
| `ws5_supervisor.py` | the 10 Hz control loop (dispatch, R15 blend, E23 traction, R16 thermal, faults) |
| `ws5_scenarios.py` | descent (R2/R17), coast (R22d), E23 cases |
| `run_ws5.py` | entry point |
| `make_report_ws5.py` | renders `REPORT_WS5.md` from `results_ws5.json` |
| `verify_ws5.py` | report-vs-results verbatim check |
| `check_determinism_ws5.py` | byte-stability check |

## Consumption

WS1/WS2/WS3/WS4 are read-only. `interface_ws4.gate_g1` is an ARCHIVED
record block (`status: executed_kill_2026-08-30`) and no field of it is
consumed as a live requirement — BASELINE_v3 executed the kill. There is no
clutch, no gate, no mode selection and no synchronisation in this
workstream. `interface_ws4.series_duty_v2` is consumed as a LIVE design
input across one explicit seam so a corrected vintage swaps in by re-running
`run_ws5.py`.

Exactly four members of `interface_ws4` are read: `series_duty_v2`,
`spin_drag_operational_note_r22d`, `v1_start_stop`, and `gate_g1.status`
(provenance only). **Vintage of record: WS4 KX round 3**,
`results_ws4.json` = `b02a6c82fbbe8d3e...`. The concordance assertion in
`run_ws5.py` section 2 is EXACT against that vintage and fails loudly if a
future vintage diverges. The full pin set is in
`results_ws5.json -> vintage.input_sha256` and is rendered in
`REPORT_WS5.md` section 1.3.
