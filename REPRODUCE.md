# REPRODUCE

Every number in [FINDINGS.md](FINDINGS.md) that carries a `[marker]` is
regenerable from this repository, and so is every result the unmarked
specification constants describe.
Each workstream is self-contained: one entry point, fixed seeds, a
`requirements.txt`, a results data file, a report generated from that file, and
a verifier that asserts the two agree.

Binding rule 1 of `CLAUDE.md`: re-running a pipeline must reproduce every
committed artefact **byte-identically**. Where a workstream measured that, the
measurement is committed beside the report.

---

## 0. Environment

Python 3 with `numpy`. Some workstreams also use `matplotlib` for figures.
Nothing needs a GPU, a network connection at run time, or more than a laptop.

```
python3 -m venv .venv
./.venv/bin/pip install -r WS1_loads_duty_cycles/requirements.txt
```

Per-workstream requirements files, so you can install only what you need:

| workstream | requirements |
|---|---|
| WS1 loads & duty cycles | `numpy>=2.0`, `matplotlib>=3.8`, `scipy>=1.11` |
| WS2 traction motor | `numpy>=2.0` |
| WS3 battery | `numpy>=2.0`, `matplotlib>=3.8` |
| WS4 genset | `numpy>=2.0`, `matplotlib>=3.8` |
| WS5 controls | `numpy>=2.0`, `matplotlib>=3.8` |
| WS8 semi architecture | `numpy>=2.0` |
| WS9 wave two | `numpy>=2.0` |
| WS11 ruler trial | `numpy==2.5.2` |
| WS13 publication | none — standard library only |

WS11 pins numpy exactly because its adjudication was performed against that
version; the others declare floors.

---

## 1. One command per workstream

Each block runs the pipeline, regenerates the report from the results file, and
verifies the report against it. Run them from the repository root with the venv
python, or `cd` into the folder as shown.

### WS1 — loads and duty cycles

```
cd WS1_loads_duty_cycles
python run_ws1.py          # ~25 s -> data/, figs/, results.json, run_output.txt
python make_tables.py      # -> tables.md, generated from results.json
```

### WS2 — traction motor, inverter, reduction, brake resistor

```
cd WS2_traction_motor
python run_ws2.py          # -> results.json, data/
python check_report.py     # the round-4 checker: report == results.json
```

### WS3 — battery pack

```
cd WS3_battery
python run_ws3.py          # -> results.json, data/, figs/
python make_report.py      # -> REPORT_WS3.md, tables_ws3.md, regen_acceptance.csv
```

### WS4 — genset, and Gate G1

```
cd WS4_genset
python run_ws4.py
python make_report_ws4.py
python verify_ws4.py       # "252 headline renderings" + interface block + structural pins
```

This is the pipeline that carries the G1 record: the first pass at
**+6.26%** [g1_prior_min], the corrected recompute at **-2.58%** [g1r_min], and
the archived `interface_ws4.gate_g1` block whose `status` field reads
`executed_kill_2026-08-30`.

### WS5 — supervisory controls

```
cd WS5_controls
python run_ws5.py
python make_report_ws5.py
python verify_ws5.py                # "934/934 rendered numbers verified verbatim"
python check_determinism_ws5.py     # -> determinism_check.txt, "19 artifacts byte-for-byte"
```

### WS8 — Vehicle One, semi-scale architecture trial

```
cd WS8_semi_architecture
python run_ws8.py                   # --jobs N for parallel candidates, identical results
python make_report_ws8.py
python verify_ws8.py
python check_determinism_ws8.py
```

`run_ws8.py --quick` runs 2 seeds at the nominal corner for development;
`--resume` reuses checkpointed corners. The committed artefacts are from a full
serial-equivalent run.

### WS9 — Vehicle One, wave two

```
cd WS9_vehicle_one_wave2
python run_ws9.py --jobs 6          # -> results_ws9.json, data/
python check_determinism_ws9.py     # -> data/determinism_check.json
python run_ws9.py --from-checkpoint # folds the determinism check into the record
python make_report_ws9.py           # also emits CHANGELOG_WS9_r3.md
python verify_ws9.py                # "verify PASS at 593 checks", and re-checks the upstream pin
```

The determinism check runs *between* the simulation and the report because it
compares two independent runs and cannot run inside the process it is checking.

### WS11 — Vehicle Zero on the honest metric

```
cd WS11_vehicle_zero_ruler
python run_ws11.py                  # ~22 min
python make_report_ws11.py
python verify_ws11.py               # "609/609 verbatim across 16 assertion sections"
python check_determinism_ws11.py    # ~1 min, optional
```

This is the pipeline behind V1's **+20.11%** [v1_nominal_min] and V2's
**-7.93%** [v2_nominal_min]. `check_determinism_ws11.py` recomputes the two
headline blocks from scratch in about a minute for a reviewer who does not want
to wait out the full run.

The four verifier counts quoted in the command blocks above are the foreman's
recorded gate results, not this file's arithmetic:
"252 headline renderings" [ws4_verify_count] (WS4),
"934/934 rendered numbers verified verbatim" [ws5_verify_count] and
"19 artifacts byte-for-byte" [ws5_determinism_count] (WS5),
"verify PASS at 593 checks" [ws9_verify_count] (WS9), and
"609/609 verbatim across 16 assertion sections" [ws11_verify_count] (WS11).

### WS13 — this publication

```
python3 WS13_publication/build_citations.py   # -> citations.json, CITATIONS.md
python3 WS13_publication/verify_ws13.py       # VERIFY OK
```

`build_citations.py` re-reads every workstream results file and every cited
report line, and regenerates the ledger. `verify_ws13.py` then asserts that each
citation still resolves, that each source file's SHA-256 matches the ledger, and
that the value printed in the prose is the value on disk.

---

## 2. What the verifiers actually assert

They are not smoke tests. Each one is a three-way check between the report
prose, the machine-readable interface block, and the results data file — the
same check the adjudicator performs by hand:

> "agrees with the report prose AND the data file — three-way, verbatim." [adj_threeway]

Specifically:

- **Verbatim rendering.** Every headline number in the report is re-resolved
  from its JSON path, re-formatted with the same format spec, and asserted to be
  present in the report as that exact string.
- **R14 export discipline.** Every worst-case field is checked to be an explicit
  max/min over an enumerated case set with the governing case labelled —
  "Every machine-readable worst-case field is computed as an" [r14_body]
  "explicit max/min over an enumerated case set, with the governing case" [r14_body2]
  labeled inline.
- **Ensemble convention.** Stochastic extrema are 8-seed envelopes, and margins
  are paired per-seed (formed seed by seed, then enveloped) rather than ratios
  of ensemble statistics.
- **Upstream pins.** WS9 and WS11 re-hash every inherited source file and report
  drift. WS11 additionally asserts it reproduces WS4's own exported series-duty
  ensemble to **0.0e+00** [ws4_seam].
- **Structural invariants.** Per-km and per-payload identities, verdicts
  re-derived mechanically from the pre-committed criterion, and (in WS11) the
  direction of every bracket row against its declared kind.

## 3. Determinism

| workstream | evidence |
|---|---|
| WS5 | `WS5_controls/determinism_check.txt` — 19 artefacts byte-for-byte |
| WS8 | `check_determinism_ws8.py`, `data/determinism_check.json` |
| WS9 | `check_determinism_ws9.py`, `data/determinism_check.json` — note its own declaration that five of six corners were not re-simulated |
| WS11 | `WS11_vehicle_zero_ruler/determinism_check.txt` — two consecutive full runs hashed file by file: "every file byte-identical, zero differing hashes" [ws11_determinism] |
| WS13 | `build_citations.py` writes no timestamp and reads no clock; re-running reproduces `CITATIONS.md` byte for byte, and `citations.json` byte for byte **except for the `PM_LOG.md` hash line** — see the live-source note below |

Committed `run_output.txt` files deliberately carry no elapsed times: an
artefact stamped with a timer can never be byte-stable.

**One declared exception, so running the command above does not surprise you.**
`PM_LOG.md` is the production log and the foreman writes to it while this
publication is being reviewed. It is one of WS13's cited sources, so its SHA-256
in `citations.json` goes stale by design and re-running `build_citations.py`
rewrites that hash. `verify_ws13.py` reports the hash change as an advisory
warning and keeps the line-and-quote resolution as a hard check.

The line numbers can move too, and once did: on 2026-08-31 a CLOSEOUT §9
hard-blocker notice was inserted at the *top* of `PM_LOG.md` and shifted all 23
cited lines down by 29. The original design assumed the log was append-only;
that assumption was wrong, the hard check caught it, and the locator now
re-resolves a moved citation **only** where the quoted phrase occurs on exactly
one line, recording the new line in the ledger. A quote that vanishes, becomes
ambiguous, or moves inside a source that is *not* declared live still fails the
run. `citations.json` → `_meta.live_sources` names the one live file.

**What determinism proves and does not prove.** It proves the pipeline is a
function of its inputs and its seeds. It does not prove the function is right —
WS11 round 1 passed a byte-stable mechanical gate and was then found NOT CLEAN
with its central robustness claim falsified. See [METHOD.md](METHOD.md) §4. This
is the same boundary the whole publication sits inside: the method
**catches internal inconsistency, never wrong physics**.
**Consistency is not validity.**

## 4. Seeds

8-seed ensembles throughout (ruling R9). The seed sets are declared in each
workstream and are not randomised:

- Vehicle Zero, from the report that uses them:
  "Ensemble = 8 seeds (VOLT-REG 23,3,4,5,6,7,8,9; VOLT-SUB 11,3,4,5,6,7,8,9" [vz_seeds].
- Vehicle One: "seeds 8101-8108" [ws9_seeds].

There is no unseeded randomness anywhere in the program, and no wall-clock
dependence.

## 5. Reading the outputs

Each workstream's `results_*.json` (or `results.json`) is the data file of
record; its `interface_*` block is the machine-readable export other
workstreams consume. The reports are generated from those files, so a
disagreement between a report and its JSON is a bug the verifier will catch
rather than a judgement call.

The publication's own index of every marked number it prints, with the file and
path each came from, is
[`WS13_publication/CITATIONS.md`](WS13_publication/CITATIONS.md).
