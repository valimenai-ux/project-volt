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
| `determinism_check.txt` | the measured byte-stability record for THIS round: two consecutive full runs, hashed file by file |
| `sources/` | the retrieved public sources, stored verbatim and SHA-256 pinned (all six files, round 2 — round 1 pinned four) |
| `data/` | CSV exports and the R34 10 Hz traces |

## Round 2

This is the rework against `FINDINGS_WS11_r1.md` (3 blocking, 8 material,
13 minor). Neither verdict moved; the report's central robustness claim
about V2's KILL did. The changelog is `REPORT_WS11.md` §0 and the
construction sweep — including the areas that came back clean — is §12
and `results_ws11.json -> construction_sweep_r2`.

New data exports this round:

| file | what it is |
|---|---|
| `data/ruler_fuel_flip_points.csv` | the ruler-fuel multiplier at which each candidate reaches 0% and the 3% bar, per case, with governing seeds (B3) |
| `data/limit_counters.csv` | WS4's capability and limit counters per case — unserved energy, SOC floor, emergency-band time, time above the ratified continuous rating (M3) |

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
committed artefact byte-identically; `determinism_check.txt` is the measured
record for this round rather than a claim carried forward from the last one.

`run_ws11.py` takes about 22 minutes on this round's expanded bracket,
counter and flip-point set.

## Read-only upstream

`../WS1_loads_duty_cycles`, `../WS2_traction_motor`, `../WS3_battery`,
`../WS4_genset` are imported read-only. Nothing outside this folder is written.
Vehicle One folders are not read.

The WS4 vintage of record is pinned in `results_ws11.json ->
_meta.input_sha256`. WS4 KX round 3 landed during this rework; `ws4_sim.py`
is byte-identical across that change and no value inside `series_duty_v2 ->
cases` moved, so the hot-swap assertion passed against the new vintage
without a line of WS11 changing. See `REPORT_WS11.md` §9.
