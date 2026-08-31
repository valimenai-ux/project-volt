# WS11 — Vehicle Zero ruler trial

Executes **BASELINE_v5 R32**: apply the payload-denominated metric to
Vehicle Zero, against the truck it replaces.

## Layout

| file | what it is |
|---|---|
| `ASSIGNMENT.md` | the order (read-only) |
| `run_ws11.py` | **the single entry point.** Runs everything, writes `results_ws11.json`, `data/`, `run_output.txt` |
| `ws11_params.py` | every declared parameter, each tagged `[SOURCED]` / `[PROGRAM]` / `[WS11-DECLARED]` with a direction of error |
| `ws11_ruler.py` | the ruler: 4HK1-TC + torque converter + Aisin A465id 6-speed + 4.555 axle, shift logic, idle, DFCO |
| `ws11_candidates.py` | thin wrappers around **WS4's own** `ws4_sim.run_g1_mode` (mode b) — WS11 writes no series supervisor |
| `ws11_capability.py` | capability-limited forward pass: trip time (R38), sustained gradeability, the WS1 §4.4 climb splice |
| `make_report_ws11.py` | generates `REPORT_WS11.md` from `results_ws11.json` |
| `verify_ws11.py` | asserts every reported number verbatim against the JSON, plus the structural invariants |
| `check_determinism_ws11.py` | ~1 min: recomputes the two headline blocks from scratch and asserts they reproduce the stored values bit for bit |
| `sources/` | the retrieved public sources, stored verbatim and SHA-256 pinned |
| `data/` | CSV exports and the R34 10 Hz traces |

## Reproduce

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python run_ws11.py          # ~10 min
python make_report_ws11.py
python verify_ws11.py
python check_determinism_ws11.py   # optional, ~1 min
```

Fixed seeds (VOLT-REG 23,3,4,5,6,7,8,9; VOLT-SUB 11,3,4,5,6,7,8,9 — WS1/WS4's
own sets). No wall-clock, no unseeded randomness. Re-running reproduces every
committed artefact byte-identically.

## Read-only upstream

`../WS1_loads_duty_cycles`, `../WS2_traction_motor`, `../WS3_battery`,
`../WS4_genset` are imported read-only. Nothing outside this folder is written.
Vehicle One folders are not read.
