## 17. Changelog - r3-concordant re-run

**Generated**, not written: every figure in this section is formatted out of `results_ws9.json` by `make_report_ws9.py`, which emits this section and `CHANGELOG_WS9_r3.md` from the same lines.

| | |
|---|---|
| Entry | **r3-concordant re-run** |
| Order executed | `NIGHT_SHIFT.md` step A3, under BASELINE_v5 R39/ESC-8 |
| Escalation executed | ESC-WS9-8 (EXECUTED, NOT RESOLVED) |
| Baseline of record | BASELINE_v5.md |
| WS8 code round pinned | **r3** |
| Seeds | 8101..8108 (8 seeds) |
| Python / numpy | 3.14.3 / 2.5.2 |
| Verdicts | PROVISIONAL under R37; **not reopened, not re-derived, not touched** |

### 17.1 What this round was ordered to do, and what it did

| ordered | done |
|---|---|
| update the sha256 pin table so it pins r3 | the fingerprint ladder is r1 -> r2 -> r3 on 8 features that exist in WS8's code ONLY after round three; `code_round` reads `r3` |
| re-run all corners x 8 seeds | 6 corners x 6 candidates x 2 duties x 8 seeds |
| regenerate report, verify, determinism | this report; `verify_ws9.py`; `check_determinism_ws9.py` -> **PASS** |
| changelog entry "r3-concordant re-run" | this section, and `CHANGELOG_WS9_r3.md` from the same lines |
| the concordance ESC-WS9-8 asks for | section 12.2, computed field by field from WS8 r3's source |

### 17.2 THE ROUND PINNED IS AN ADJUDICATED-NOT-CLEAN ROUND

NOT CLEAN - FINDINGS_WS8_r3.md: 'NOT CLEAN. Two blocking, six material, twelve minor.' No WS8 verdict moved and `all_unchanged = True`; the adjudicator places both blocking findings in the round's ACCOUNT OF ITSELF rather than its physics. WS9 pins this round because BASELINE_v5 R39/ESC-8 orders it, not because it is clean. IF THE LEAD BOUNCES WS8 TO AN r4 THIS PIN IS STALE AGAIN. WS9 neither resolves nor softens any WS8 finding (ESC-WS9-10).

This is stated here and not only in the escalations because a changelog is what a baseline quotes. **If the lead bounces WS8 to an r4, this pin is stale again** and WS9 re-runs - the same operation this round has now demonstrated costs one flag. See ESC-WS9-10.

### 17.3 The concordance, per implementation

| implementation ESC-WS9-8 names | result against WS8 r3 |
|---|---|
| `spin_rule_on_the_machines_shaft` | **CONSISTENT WITH WS8 r3 (no undeclared difference)** (4 consistent, 1 declared differences, 0 undeclared) |
| `correction_pricing_on_ws9_own_energy_keys` | **CONSISTENT WITH WS8 r3 (no undeclared difference)** (6 consistent, 3 declared differences, 0 undeclared) |
| `pack_temperature_as_a_state` | **CONSISTENT WITH WS8 r3 (no undeclared difference)** (3 consistent, 2 declared differences, 0 undeclared) |

`any_undeclared_difference = False`, and `sanity.concordance_with_ws8_r3_ESC_WS9_8.passes = True` gates the run on it.

### 17.4 What moved, and why almost nothing could

Of the **62** WS8 symbols on WS9's import surface, **0** changed between r2 and r3. r3's edits to `ws8_candidates.py` are eight new top-level objects plus changes inside `S0`, `S2` and `S3` - candidates WS9 does not instantiate - and the correction rule WS9 re-implements is byte-identical between the two rounds. So the structural expectation was that no WS9 number could move through the import boundary. **The re-run measures it rather than resting on it**, which is the whole reason ESC-WS9-8 asked for a re-run and not just a comparison.

| candidate | design-duty nominal ensemble-min | worst corner | control duty | verdict (NOT reopened) |
|---|---|---|---|---|
| **S4p** | +11.95% | +7.40% @ `cold_minus10C` | -6.81% | ADVANCE |
| **S5** | +1.90% | +0.27% @ `cold_minus10C` | -5.75% | KILL |
| **S5-13L** | +5.36% | +3.93% @ `cold_minus10C` | -1.38% | ADVANCE |
| **S6** | +7.50% | +7.29% @ `payload_minus20` | +7.26% | ADVANCE |
| **S7** | +4.51% | +3.58% @ `cold_minus10C` | -1.45% | ADVANCE |

Those verdicts are reproduced from this round's numbers by the pre-committed criteria in `advance_kill.criteria`; they are NOT re-derived judgements. R37 leaves them PROVISIONAL and their adjudication is the lead-designated Fable seat.

### 17.5 What this round added beyond the order, and why

| addition | authority |
|---|---|
| the pin now covers 6 sibling-workstream sources WS9 reaches through WS8 | the round-1 pin could not see that `../WS4_genset/ws4_chain.py` changed under WS9 between the two runs; ESC-WS9-11 |
| `run_ws8.py` pinned as a rule source, hashed and NOT imported | WS9 re-implements WS8's correction pricing rather than calling it, so a restatement of that rule would otherwise be invisible to the pin |
| 6 10 Hz traces (`data/trace_*_10Hz.csv`) | R34, which names WS9 RE-RUNS explicitly and applies from their next artifact - this one; scope escalated as ESC-WS9-12 |
| `interface_ws9.trip_time_R38_gate_input` and `data/trip_time_r38.csv` | R38 pre-commits a trip-time gate the LEAD applies at ratification; the gate's input belongs in the R14 block beside the bar. **The gate is not applied here.** |
| section 12.2 replaces a prose concordance with a computed one | the prose table is the defect class WS8's own r2 and r3 adjudications found three times |

### 17.6 The one thing a reader must not miss

**12 design-duty case(s) sit above R38's +5% trip-time bar on at least one of the two exported statistics:** `S5-13L/cold_minus10C/GH-REG-165` at +8.379%, `S5-13L/grade_heavy/GH-REG-165` at +7.936%, `S5-13L/hot_alt_2000m_45C/GH-REG-165` at +7.873%, `S5-13L/nominal/GH-REG-165` at +7.936%, `S5-13L/payload_minus20/GH-REG-165` at +5.742%, `S5-13L/payload_plus20/GH-REG-165` at +9.223%, `S5/cold_minus10C/GH-REG-165` at +15.708%, `S5/grade_heavy/GH-REG-165` at +14.680%, `S5/hot_alt_2000m_45C/GH-REG-165` at +15.100%, `S5/nominal/GH-REG-165` at +14.680%, `S5/payload_minus20/GH-REG-165` at +11.430%, `S5/payload_plus20/GH-REG-165` at +17.151%.

**Of those, S5-13L currently carries an ADVANCE verdict.** R38 says the lead applies the gate at ratification and WS9 does not; this changelog's job is to make sure the lead sees the number before applying it, not to apply it. Nothing in this artifact has been adjusted for R38.

**And the two exported statistics DISAGREE about S5-13L on 2 of its design-duty corners**, which means R38's answer depends on which statistic the ruling means. R38 names a bar and not a statistic; WS9 exports both and rules on neither:

| case | median-of-medians | 8-seed paired median | which side of the bar |
|---|---|---|---|
| `S5-13L/grade_heavy/GH-REG-165` | +6.072% | +4.949% | **over on the median-of-medians, under on the paired median** |
| `S5-13L/nominal/GH-REG-165` | +6.072% | +4.949% | **over on the median-of-medians, under on the paired median** |

On its other design-duty corners the two agree, so this is not a statistic that rescues the candidate everywhere - it is a statistic that decides two corners. The lead rules.

