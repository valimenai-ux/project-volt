# WS9 - Vehicle One, wave two: the two walls and the cold wall

Executes `ASSIGNMENT.md` (written against `../BASELINE_v4.md`, whose rulings
R25-R33 and doctrine D13-D15 govern the trial unchanged) with
`../BASELINE_v5.md` as the **baseline of record**. This folder is
self-contained and deterministic; it reads WS8's **models** read-only and
modifies nothing outside itself (CLAUDE.md rule 10).

**Current round: `r3-concordant re-run`** (`NIGHT_SHIFT.md` step A3, under
BASELINE_v5 R39/ESC-8). The pin is on WS8 code round **r3**, and that round
was itself adjudicated **NOT CLEAN** - see `CHANGELOG_WS9_r3.md` section
17.2 and ESC-WS9-10. WS9's verdicts are PROVISIONAL under R37 and this round
reopens none of them. R38's trip-time gate is **exported, not applied**: the
lead applies it (section 12.3, `data/trip_time_r38.csv`).

## Run it

```
cd WS9_vehicle_one_wave2
../.venv/bin/python run_ws9.py --jobs 6         # -> results_ws9.json + data/*.csv
../.venv/bin/python check_determinism_ws9.py    # -> data/determinism_check.json
../.venv/bin/python run_ws9.py --from-checkpoint  # folds the check into the record
../.venv/bin/python make_report_ws9.py          # -> REPORT_WS9.md
../.venv/bin/python verify_ws9.py               # asserts report == results, and re-checks the pin
```

The determinism check runs between the simulation and the report because it
compares two independent runs and so cannot run inside the process it is
checking - the same posture WS8 takes.

`make_report_ws9.py` also emits `CHANGELOG_WS9_r3.md` from the same lines as
the report's section 17, so the two cannot disagree.

`run_ws9.py --quick` runs the nominal corner only, for development.
`--resume` reuses corners already checkpointed; `--from-checkpoint` rebuilds
every derived block against a saved trial without re-simulating, so a defect
in a reporting block cannot cost a simulation. The committed artifacts are
from a full 8-seed run.

Dependencies: `requirements.txt` (numpy only). The repository venv at
`../.venv` has it.

## Files

| file | what it is |
|---|---|
| `ASSIGNMENT.md` | the order, executed exactly as written |
| `run_ws9.py` | **single entry point** (rule 1): corners, the trial, the gates, the exports |
| `ws9_params.py` | what WS9 ADDS to WS8's parameters, every number provenance-tagged, plus the citations and their evidence quality |
| `ws9_duty.py` | the two duty classes (R29) and predictive energy management |
| `ws9_walls.py` | the two walls solved in CLOSED FORM, the third constraint the design duty exposes, and the two-speed frontier |
| `ws9_engines.py` | the opposed-piston-class engine on a cited basis, the two spark-ignition prime movers, the inherited ambient derate |
| `ws9_fuels.py` | fuel properties, tank-system mass, and CO2 DERIVED from a carbon balance |
| `ws9_storage.py` | the buffer and resistor SIZING RULES, and ESC-1(c)'s cited external pack |
| `ws9_thermal.py` | R30: pack preconditioning and the waste-heat cab path, as a state |
| `ws9_candidates.py` | S0R (the ruler), S5, S6, S7, S4' and the brackets |
| `ws9_corrections.py` | r2's pricing rule and ESC-3's electricity term |
| `ws9_primemover.py` | the prime-mover-at-the-pin task |
| `ws9_blocks.py` | sanity checks, escalations, the R14 interface, the CSV exports |
| `ws9_concordance.py` | **ESC-WS9-8 executed**: the field-by-field concordance against WS8 r3, EXTRACTED FROM SOURCE by `ast` and compared, plus WS9's WS8 import surface and its r2 -> r3 delta |
| `sources/ws8_import_surface_r2.json` | an INPUT, never regenerated: the r2 fingerprints of every WS8 symbol WS9 imports, generated once from the r2 tree, which is what makes the r2 -> r3 delta a measured fact |
| `make_report_ws9.py` | renders `REPORT_WS9.md` from `results_ws9.json` |
| `check_determinism_ws9.py` | the rule-1 regeneration evidence: re-simulates one job from scratch at zero tolerance and diffs every regenerated export byte for byte |
| `verify_ws9.py` | asserts every headline number renders a results value verbatim (rule 2) AND re-checks the vintage pin |
| `results_ws9.json` | the data file of record |
| `data/*.csv` | per-run tables, margins, duty statistics, mass ledgers, the heat ledger, the pin task, the two-walls sweep, `trip_time_r38.csv` (R38's gate input), `concordance_ws8_r3.csv`, `ws8_import_surface.csv` |
| `data/trace_*_10Hz.csv` | **R34**: 10 Hz traces, one per candidate on the design duty at the nominal corner, first seed. Regenerated and diffed byte for byte by `check_determinism_ws9.py` half 3. Scope escalated as ESC-WS9-12 |
| `CHANGELOG_WS9_r3.md` | the round's changelog, generated from the same lines as report section 17 |

## What is inherited, and from where

Nothing ratified is re-derived (assignment: *"Inherit the WS8 pipeline ... do
not re-derive what is ratified; extend it"*).

- **WS8** - the duty cycles and their 8-seed construction, the
  achieved-speed integrator, the road load, the mass ledger, the HD Willans
  engines and the AMT, the genset line, the WS2 machine stretch, the WS3
  pack construction, the startability specification, the sustained-climb
  rule, the regen blend-out, the friction-brake allowance, and - from ROUND
  TWO - the wired cold charge acceptance (F2), the ambient/altitude derate
  and its corner (F11), the one spin rule and its thresholds (F5), the
  duty-averaged correction pricing (F6) and the signed charge-sustaining
  convention (F4).
- **WS2 r4 / WS3 / WS4**, through WS8's own ruled loaders.

Every inherited source file is **sha256-pinned** in
`results_ws9.json['inherited_vintage']` - WS8's seven models, `run_ws8.py`
as a rule source that is hashed and NOT imported, and (new in this round)
the six **sibling-workstream sources WS9 reaches through WS8**: WS4's
`ws4_models.py` and `ws4_chain.py`, WS3's `ws3_cells.py`, and the three WS2
export files the chain loader reads. `verify_ws9.py` re-hashes all of them
and reports DRIFT. That is the hot-swap signal the assignment asks for: WS9
ran while WS8's round two was in flight, so the record states exactly which
WS8 it was run against.

**WS9 reads no WS8 numeric artifact** - not `results_ws8.json`, not
`REPORT_WS8.md`, not one exported figure. It re-derives its own ruler from
the same models and compares everything to that, and asserts the fact in
`sanity.no_ws8_artifact_read`. So WS8's r1/r2 artifact split cannot move a
WS9 number.

## Reading the result

The metric of record is **primary energy per payload tonne-km** (ESC-3, as
ruled in R27). For every candidate that burns only diesel the primary-energy
factor is a common multiplier and the margin is identical to the
tank-energy margin - asserted, not claimed - so the metric changes exactly
one thing: how the plug-in candidate is scored against the rest.

Read section 1 first (what the design duty actually contains), then section
3 (the two walls and the third one), then the section-4 table. Read section
8 before believing any margin with a large correction share.

There is **no fleet average anywhere in this report**. The assignment
forbids one, because R29's finding is that the sign of a margin flips
between the two duties and a fleet average hides it (D15).

Escalations are in section 13. They cite the rulings they challenge and are
not self-resolved (rule 8) - they go to the lead.
