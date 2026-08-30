# WS8 - Vehicle One, semi-scale architecture trial

Executes `ASSIGNMENT.md` against `../BASELINE_v3.md`. This folder is
self-contained and deterministic; it reads Vehicle Zero's workstreams
**read-only** and modifies nothing outside itself (CLAUDE.md rule 10).

## Run it

```
cd WS8_semi_architecture
../.venv/bin/python run_ws8.py          # -> results_ws8.json + data/*.csv
../.venv/bin/python make_report_ws8.py  # -> REPORT_WS8.md
../.venv/bin/python verify_ws8.py       # asserts report == results
```

`run_ws8.py --quick` runs 2 seeds at the nominal corner only, for
development. The committed artifacts are from a full run.

Dependencies: `requirements.txt` (numpy only). The repository venv at
`../.venv` has it.

## Files

| file | what it is |
|---|---|
| `ASSIGNMENT.md` | the order, executed exactly as written |
| `run_ws8.py` | **single entry point** (rule 1); all five tasks, the gates, the exports |
| `ws8_params.py` | vehicle, mass ledger, scaling laws, cycle constants - every number tagged with its provenance |
| `ws8_physics.py` | road load and the achieved-speed integrator |
| `ws8_cycles.py` | LH-520 and REG-165 construction, 8-seed ensembles |
| `ws8_engine.py` | 13/11/7/5 L Willans engines and the 12-speed AMT |
| `ws8_electric.py` | WS2 map stretch, generator stretch, WS3-based packs, resistor |
| `ws8_candidates.py` | S0-S4: mass ledgers, envelopes, control policies, accounting |
| `ws8_whr.py` | waste-heat-recovery systems and the pre-committed gate |
| `make_report_ws8.py` | renders `REPORT_WS8.md` from `results_ws8.json` |
| `verify_ws8.py` | asserts every headline number renders a results value verbatim (rule 2) |
| `results_ws8.json` | the data file of record |
| `data/*.csv` | per-seed tables, the S3 ratio sweep, the WS6 heat ledger |
| `PRIOR_ART_WS8.md` | Task 0 claim map |

## What is inherited, and from where

Nothing electrical or thermodynamic is re-invented here.

- **WS2 r4** - the measured inverter+motor loss map
  (`effmap_motor_inverter_662V.csv`, 4,203 feasible cells), the
  capability envelope, the stack-length scaling rule and its
  `mass_end_kg = 18.0` split, the 7,200 rpm rotor limit, the brake
  resistor's kg-per-kW.
- **WS3** - cell definitions, the `1.55 x cell + 35 kg` pack overhead
  model, the chemistry trade, cold charge acceptance.
- **WS4** - `WillansEngine`, `PMGenerator`, `derate_factor`,
  `WS2TractionChain` (the ruled map loader), the R12 chain convention,
  the R18 flat-rating ratio.
- **WS1** - the road-load formulation and the cycle-construction method,
  mirrored rather than imported (the vehicle is a different one).

## Reading the result

The metric of record is **fuel energy per payload tonne-km**. At fixed
GCW that means powertrain mass is payload, and every candidate's margin
is the difference between two effects pulling opposite ways. Read
section 4 of the report for the table and section 9 for the verdicts;
read section 6.2 first if you only read one thing, because it is the
finding that does not depend on any efficiency assumption.

Escalations are in section 11. They cite the rulings they challenge and
are not self-resolved (rule 8) - they go to the lead.
