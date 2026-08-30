# WS1 — Loads & Duty Cycles (Project Volt)

Runnable analysis behind `REPORT_WS1.md`. Read `../BASELINE_v0.md` first.

## Run

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python run_ws1.py          # ~25 s, writes data/, figs/, results.json, run_output.txt
./.venv/bin/python make_tables.py      # writes tables.md
```

Everything is deterministic (seeded); re-running reproduces every number in
the report exactly.

## Modules

| file | contents |
|---|---|
| `volt_params.py` | vehicle, driveline, accessory, engine and control parameters. Baseline values vs `[WS1-ASSUMPTION]` are marked inline. |
| `volt_cycles.py` | the two reference cycles, built by forward-integrating a driver model over a list of route legs; the VOLT-REG grade profile; the sustained-climb scenario. |
| `volt_physics.py` | road load, wheel power, cycle metrics, regen split, time-at-power histogram, RMS / rolling-RMS, DC-bus balance, battery trajectory, constant-genset solve, rolling-window energy swing, engine curve. |
| `volt_variants.py` | V1 series and V2 i-MMD powertrain models, energy management, The Four Numbers, and the capability-limited forward simulation. |
| `run_ws1.py` | the study: metrics, The Four Numbers, all sensitivities, figures, CSVs, `results.json`. |
| `make_tables.py` | regenerates `tables.md` from `results.json`, so no number in the report is transcribed by hand. Run it after `run_ws1.py`. |

## Outputs

- `REPORT_WS1.md` — the workstream report.
- `tables.md` — the report's tables, generated from `results.json`.
- `results.json` — every number quoted in the report, machine-readable.
- `run_output.txt` — the console summary of the last run.
- `data/cycle_*_1Hz.csv` — the two reference cycles at 1 Hz (t, v, grade, distance, wheel power).
- `data/trace_*_10Hz.csv` — full 10 Hz traces with bus / battery / regen channels.
- `data/four_numbers.csv` — The Four Numbers per variant/cycle.
- `data/time_at_power_*.csv` — time-at-power histograms, 10 kW bins.
- `data/regen_sweep_*.csv` — recoverable fraction vs regen absorb limit.
- `figs/fig01..fig10` — traces, histograms, sensitivity sweeps, operating maps.

Cycles are analysed at their native 10 Hz. The 1 Hz CSVs are for exchange with
other workstreams; see the `time_resolution` sensitivity in `results.json` for
what sampling rate costs you (peaks mostly).
