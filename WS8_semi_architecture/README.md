# WS8 - Vehicle One, semi-scale architecture trial

Executes `ASSIGNMENT.md`, and the round ordered by `R3_DIRECTIVE.md`
(R35), against `../BASELINE_v5.md`. This folder is self-contained and
deterministic; it reads Vehicle Zero's workstreams **read-only** and
modifies nothing outside itself (CLAUDE.md rule 10).

**Round 3.** The verdicts are `executed_kill_2026-08-30` under R25 and
are **not reopened here**; this round makes the numbers of record
correct against `FINDINGS_WS8_r2.md` (B1 blocking, M1-M4, m1-m7). Read
`CHANGELOG_WS8_r3.md` first if you are returning to this folder - it
says which direction every candidate moved and why, and this round every
direction cell is GENERATED from the one-factor table rather than
written by hand (finding M1). The interface block carries
`numbers_version: r3` and a sha256 pin of every input the numbers depend
on; the heat ledger carries `ledger_version: r3` and **WS6 consumes only
that one** - r2's ledger is withdrawn.

**The one rule this round added.** An engine geared to the road is in
OVERRUN on every sample where the vehicle is moving and commands no
tractive force: it burns no fuel, makes no positive shaft power, and its
compression brake is available only there. It lives in
`ws8_candidates.overrun_mask`, S0's long-standing cut-off is an instance
of it, and a hard per-run assertion in `run_ws8.run_one` fails the run if
any 10 Hz sample carries both compression-brake power and positive engine
shaft power.

## Run it

```
cd WS8_semi_architecture
../.venv/bin/python run_ws8.py          # -> results_ws8.json + data/*.csv
../.venv/bin/python make_report_ws8.py  # -> REPORT_WS8.md
../.venv/bin/python verify_ws8.py       # asserts report == results
```

`run_ws8.py --quick` runs 2 seeds at the nominal corner only, for
development; `--jobs N` runs candidates in parallel (identical results,
less wall clock); `--resume` reuses corners already in the checkpoint.
The committed artifacts are from a full serial-equivalent run.

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
| `R3_DIRECTIVE.md` | the order this round executes |
| `R2_DIRECTIVE.md`, `FINDINGS_WS8_r1.md`, `CHANGELOG_WS8_r2.md` | the previous round, kept as history |
| `FINDINGS_WS8_r2.md` | the round-2 adjudication this round closes |
| `CHANGELOG_WS8_r3.md` | generated: what moved in r3 and which way |
| `results_ws8.json` | the data file of record |
| `data/*.csv` | per-seed tables, the S3 ratio sweep, the WS6 heat ledger (versioned, with per-component labels for the simulated member) and its R14 worst cases, the one-factor rows |
| `PRIOR_ART_WS8.md` | Task 0 claim map |

## What is inherited, and from where

Nothing electrical or thermodynamic is re-invented here.

- **WS2 r4** - the measured inverter+motor loss map
  (`effmap_motor_inverter_662V.csv`, 4,203 feasible cells), the
  capability envelope, the stack-length scaling rule and its
  `mass_end_kg = 18.0` split, the 7,200 rpm rotor limit, the brake
  resistor's kg-per-kW.
- **WS3** - cell definitions, the `1.55 x cell + 35 kg` pack overhead
  model, the chemistry trade, cold charge acceptance (APPLIED at the
  -10 C corner in r2; in r1 it was listed here and never called).
- **WS4** - `WillansEngine`, `PMGenerator`, `derate_factor`,
  `WS2TractionChain` (the ruled map loader), the R12 chain convention,
  the R18 flat-rating ratio. `derate_factor` is APPLIED at the added
  2,000 m / +45 C corner (R28); in r1 it was imported and never called.

Every inherited object in this list is exercised by the pipeline. An
inert entry in a provenance list is a false claim about what the numbers
were built from, and closing two of those was half of this round.
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
