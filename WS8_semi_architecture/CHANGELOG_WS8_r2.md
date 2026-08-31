# CHANGELOG - WS8 round 2 (errata)

**Generated**, not written: every figure below is formatted out of `results_ws8.json` by `make_report_ws8.py`, which emits this file and section 15 of `REPORT_WS8.md` from the same lines. Nothing here is transcribed by hand (rule 2).

| | |
|---|---|
| Order executed | `WS8_semi_architecture/R2_DIRECTIVE.md` (lead-issued 2026-08-30, under R26) |
| Findings closed | `FINDINGS_WS8_r1.md` F1-F13 |
| Baseline of record | BASELINE_v4.md |
| Numbers version | r2 |
| Verdicts | `executed_kill_2026-08-30` - not reopened by this round |
| Seeds | 8101..8108 (8 seeds) |
| Python / numpy | 3.14.3 / 2.5.2 |

Full context, tables and the interface block: `REPORT_WS8.md`.

---

## What moved, and which way

This round executed `R2_DIRECTIVE.md` against `FINDINGS_WS8_r1.md`. The verdicts were **not** reopened: R25 executed all four kills and the WHR drop on the pre-committed criteria, and the directive's instruction was to make the numbers of record correct and to STOP and report if any verdict flipped. None did.

### 1. Which direction each candidate moved

Against r1's numbers of record as quoted in R25 (BASELINE_v4):

| candidate | nominal min, r1 -> r2 | nominal median, r1 -> r2 | worst corner, r1 -> r2 | direction | verdict |
|---|---|---|---|---|---|
| **S1** | -0.66% -> -0.69% | +0.75% -> +0.73% (-0.02 pp) | -4.37% -> -12.87% (-8.50 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |
| **S2** | +0.36% -> +0.48% | +1.70% -> +1.80% (+0.10 pp) | -1.90% -> -9.62% (-7.72 pp, now at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S3** | -6.22% -> -7.65% | -3.83% -> -5.26% (-1.43 pp) | -11.17% -> -21.98% (-10.81 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |
| **S4** | -3.67% -> -3.84% | -0.95% -> -1.06% (-0.11 pp) | -8.26% -> -17.21% (-8.95 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |

The worst-corner column is not like-for-like and should not be read as one: r1's worst corner was -10 C for every candidate, and r2 both made that corner harder (F2, the cold charge acceptance that was never applied) and added a corner that did not exist (R28's 2,000 m / +45 C). Both changes can only move a worst corner down.

**The R28 corner did not become the worst one, and that is itself a result.** R28 named 2,000 m / +45 C on the Vehicle Zero precedent that the altitude/hot corner became worst there. At Vehicle One it does not: the thin air at 2,000 m takes about 27% off the aerodynamic bill, which is the dominant term on a line-haul corridor, and that outweighs the 6.9% engine derate it also imposes.

| candidate | nominal min | 2,000 m / +45 C min | -10 C min |
|---|---|---|---|
| **S1** | -0.69% | +1.70% | -12.87% |
| **S2** | +0.48% | +2.50% | -9.62% |
| **S3** | -7.65% | -8.69% | -21.98% |
| **S4** | -3.84% | -0.31% | -17.21% |

S1, S2, S4 gain at the R28 corner relative to nominal; S3 loses there, because the derate falls on a mechanical path that has no genset behind it and pushes the shortfall onto the pack. Either way the R28 corner is nowhere near the -10 C column. **The cold wall is Vehicle One's binding corner, and nothing in this round moved that** - it deepened it. R30 already reads it that way.

### 2. The findings, and what each one did

| finding | severity | what r2 did | direction |
|---|---|---|---|
| **F1** | blocking | heat ledger rebuilt: a pack-saturated descent case and the simulated worst run added to the enumerated set, the retard channel split so compression-brake heat is booked to the exhaust and resistor heat to the resistor, foundation-brake and accessory rows added, every case closed against the energy that entered it, and every component asserted against the rating of the hardware whose mass was charged | no fuel number moves; the exported sink case rises substantially and the attribution changes for S2 and S3 |
| **F2** | blocking | `Pack8.p_cont_chg_kw_at()` / `COLD_CHG_FACTOR` wired into every regen envelope, every dispatch charge limit and S3's own SOC loop, at the corner's ambient | AGAINST every electrified candidate, at the cold corner only |
| **F3** | material | S2's single engine given one crankshaft: traction torque first, then accessories, then the generator on what is left, priced at the road-imposed speed; accessory duty the crank cannot carry moves to the bus | AGAINST S2 |
| **F4** | material | the symmetric charge-sustaining convention declared, the correction share exported signed with min AND max, and the credit-free margin reported alongside (section 4.4) | disclosure only - no number of record moves |
| **F5** | material | R22(d) charged on one rule for every candidate - geared AND unloaded - which removes S3's double count, and the coast-permitting bracket reported so the near-zero charge is not mistaken for a result | FOR S3 (it was paying twice); negligible elsewhere |
| **F6** | material | unserved and stored energy priced at the candidate's own duty-averaged fuel-to-bus efficiency over the run being corrected, not at the locus maximum (rule 5) | AGAINST S1, S3 and S4; slightly FOR S2, whose correction is a credit |
| **F7** | material | the S0 grade-zeroed cross-check restated as an 8-seed envelope against the public band, with three enumerated combination masses and the reference payload stated | weakens the evidence ESC-WS8-7 rests on; no margin moves |
| **F8** | minor | S4's headline specification rendered from the rating the model built, and class titles and policies added to the verify set | record precision |
| **F9** | minor | the road-load sanity note formatted from the computed values instead of hand-written prose inside the data file | record precision |
| **F10** | minor | the two-speed bracket computed on paired per-seed margins, the same statistic as the headline, with the basis stated | record precision |
| **F11** | minor | `derate_factor` exercised in an added 2,000 m / +45 C corner (R28) rather than removed from the provenance list | AGAINST every candidate with an engine on the load |
| **F12** | minor | the ratio ceiling solved in closed form as a physics bound, with the swept set kept as the illustration, and the ratio the 6% grade demands solved too | record precision; S3's conclusion is unchanged and now rests on no grid at all |
| **F13** | minor | the LH-520 climb figure formatted from the ensemble everywhere it appears | record precision |

### 3. Verdict stability

| candidate | verdict executed under R25 | verdict the same criteria give on the r2 numbers | headroom to the >= 3% nominal bar |
|---|---|---|---|
| **S1** | KILL | KILL | 3.69 pp short |
| **S2** | KILL | KILL | 2.52 pp short |
| **S3** | KILL | KILL | 10.65 pp short |
| **S4** | KILL | KILL | 6.84 pp short |

WHR on the r2 numbers: S1 DROPPED, S2 DROPPED, S3 DROPPED - unchanged.

**`all_unchanged = True`.** If `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3).

### 4. Environment

r1's artifacts were produced on Python 3.11.15 / numpy 2.4.6 on x86-64 Linux; r2's are produced on Python 3.14.3 / numpy 2.5.2 on arm64 macOS. The two platforms differ in the last one or two units in the last place of a double - a relative difference around 1e-16, from libm and SIMD reduction order, not from any change here. Byte-stable regeneration (rule 1) is a property of a run reproducing ITSELF on one machine, and it is checked in section 14 on this one. Nothing in the errata depends on that difference, and no reported figure is quoted to anything like that precision.

### 5. Inputs, SHA-pinned

Every source file and every read-only object inherited from another workstream is pinned by sha256 in `interface_ws8.inputs_sha256`, so a consumer can tell from the export alone whether the numbers it holds came from these exact inputs. 20 files are pinned.

---
