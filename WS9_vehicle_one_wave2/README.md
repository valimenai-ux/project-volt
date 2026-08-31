# WS9 - Vehicle One, wave two: the two walls and the cold wall

Executes `ASSIGNMENT.md` against `../BASELINE_v4.md` (rulings R25-R33,
doctrine D13-D15). This folder is self-contained and deterministic; it reads
WS8's **models** read-only and modifies nothing outside itself (CLAUDE.md
rule 10).

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
| `make_report_ws9.py` | renders `REPORT_WS9.md` from `results_ws9.json` |
| `check_determinism_ws9.py` | the rule-1 regeneration evidence: re-simulates one job from scratch at zero tolerance and diffs every regenerated export byte for byte |
| `verify_ws9.py` | asserts every headline number renders a results value verbatim (rule 2) AND re-checks the vintage pin |
| `results_ws9.json` | the data file of record |
| `data/*.csv` | per-run tables, margins, duty statistics, mass ledgers, the heat ledger, the pin task, the two-walls sweep |

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
`results_ws9.json['inherited_vintage']`, and `verify_ws9.py` re-hashes them
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
