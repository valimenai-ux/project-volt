# CHANGELOG - WS8 round 3 (r3)

**Generated**, not written: every figure below is formatted out of `results_ws8.json` by `make_report_ws8.py`, which emits this file and section 15 of `REPORT_WS8.md` from the same lines. Nothing here is transcribed by hand (rule 2) - including, this round, every DIRECTION cell, which r2 wrote by hand and got wrong three times (finding M1).

| | |
|---|---|
| Order executed | `WS8_semi_architecture/R3_DIRECTIVE.md` (lead-issued 2026-08-30, under R35) |
| Findings closed | `FINDINGS_WS8_r2.md` B1, M1-M4, m1-m7 |
| Baseline of record | BASELINE_v5.md |
| Numbers version | r3 (supersedes r2) |
| Heat ledger version | r3 - WS6 consumes ONLY this one |
| Verdicts | `executed_kill_2026-08-30` - not reopened by this round |
| Seeds | 8101..8108 (8 seeds) |
| Python / numpy | 3.14.3 / 2.5.2 |

Full context, tables and the interface block: `REPORT_WS8.md`.

---

## What moved, and which way

This round executed `R3_DIRECTIVE.md` against `FINDINGS_WS8_r2.md`. The verdicts were **not** reopened: R25 executed all four kills and the WHR drop on the pre-committed criteria, and the directive's instruction was to make the numbers of record correct, to STOP and report if any verdict flipped, and to STOP if S3's nominal ensemble-min crossed the +3% bar. Neither happened.

### 1. Which direction each candidate moved

Against r2's numbers of record as quoted in R35 (BASELINE_v5) and `CHANGELOG_WS8_r2.md`:

| candidate | nominal min, r2 -> r3 | nominal median, r2 -> r3 | worst corner, r2 -> r3 | direction | verdict |
|---|---|---|---|---|---|
| **S1** | -0.69% -> -0.69% | +0.73% -> +0.73% (+0.00 pp) | -12.87% -> -12.87% (+0.00 pp, at `cold_minus10C`) | **UNMOVED** on the nominal median | **KILL** |
| **S2** | +0.48% -> +0.59% | +1.80% -> +1.89% (+0.09 pp) | -9.62% -> -9.23% (+0.39 pp, at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S3** | -7.65% -> -1.09% | -5.26% -> +1.64% (+6.90 pp) | -21.98% -> -14.17% (+7.81 pp, at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S4** | -3.84% -> -3.84% | -1.06% -> -1.06% (+0.00 pp) | -17.21% -> -17.21% (+0.00 pp, at `cold_minus10C`) | **UNMOVED** on the nominal median | **KILL** |

**Almost all of that movement is one correction, and it is measured rather than inferred.** The one-factor row `B1_reverted_brake_and_fuel` in section 4.4 reverts R3's control rule and nothing else: FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical). Everything r3 changed besides that rule is an ACCOUNTING correction - the run closure and the ledger rows it found. Only one of those moves a margin at all, because it moves THE RULER, and it too is measured rather than called small: FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp). Every other r3 correction is a heat row, and no margin reads the heat ledger - which is why S1 and S4 come back at r2's numbers to the precision this table is quoted to.

**A consequence worth stating in the changelog rather than only in the escalations.** With the rule applied, S3 takes 0.000 kWh of through-the-road charge over the whole trial, on 0 of 96 runs, and the 0.72-of-capacity BSFC policy withheld 0.000 kWh of it. Half of S3's declared energy policy is inert, for a reason that is a modelling artefact rather than a control choice - raised as ESC-WS8-8 and not self-resolved.

The worst-corner column IS like-for-like this round: r2 and r3 run the same six corners on the same seeds. r2's own table was not, and said so.

**The R28 corner is still not the worst one, and r3 scopes what that means** (r2 finding M3). At Vehicle One the thin air at 2,000 m takes about 27% off the aerodynamic bill, which is the dominant term on a line-haul corridor, and that outweighs the 6.9% engine derate it also imposes.

| candidate | nominal min | 2,000 m / +45 C min | -10 C min |
|---|---|---|---|
| **S1** | -0.69% | +1.71% | -12.87% |
| **S2** | +0.59% | +2.64% | -9.23% |
| **S3** | -1.09% | -0.56% | -14.17% |
| **S4** | -3.84% | -0.30% | -17.21% |

S1, S2, S3, S4 gain at the R28 corner relative to nominal. Either way the R28 corner is nowhere near the -10 C column. **The cold wall is Vehicle One's binding corner, and nothing in this round moved that.** R30 already reads it that way.

**Scope of that statement, measured** (finding M3). THE R28 CORNER DERATES THE ENGINE'S FULL-LOAD CURVE AND WHAT IS COMPUTED FROM IT, AND NOTHING ELSE. WS4's `derate_factor` is applied to every engine in the trial (S0's included) and therefore to the R18 continuous rating and the genset ceilings behind it. It is NOT applied to the traction machine, the inverter, the pack's charge or discharge ceiling, the brake resistor, or the compression brake - `ws8_electric.py` has no hot-side model at all and `Pack8.cold_chg_factor_at()` clamps to 1.0 above 15 C. The corner's BENEFIT - about 27% off the aerodynamic bill at 2,000 m - is shared by every candidate; its PENALTY falls only on combustion. Any conclusion drawn from this corner is scoped to that: it says the thin air outweighs an ENGINE derate, not that it outweighs a hot day for the whole vehicle. The cab-cooling load IS charged symmetrically (mechanical and bus-side both rise), which is the one hot-side effect the electric path does pay.

*Direction of error.* a missing hot-side electric derate FLATTERS the electrified candidates at this corner relative to S0; the corner is not binding for any of them, so no verdict depends on it, but WS9 inherits the statement under R28.

### 2. The findings, and what each one did

Every cell in the DIRECTION column below is either generated by `correction_directions()` from the one-factor table in section 4.4, or says explicitly that the direction is not separately measured and why. r2's version of this table was thirteen Python literals the verifier structurally could not reach, and `FINDINGS_WS8_r2.md` M1 names three of them as contradicted by that round's own numbers. That is finding M1, and this is its fix.

| finding | severity | what r3 did | direction |
|---|---|---|---|
| **B1** | blocking | THE ONE RULE. An engine geared to the road is in OVERRUN on every sample where the vehicle is moving and commands no tractive force: it burns no fuel, makes no positive shaft power, and its compression brake is available only there. S0 already had this cut-off inline; it is stated once in `overrun_mask` and applied to every candidate. S3's through-the-road charging is GATED ON THE VEHICLE NOT BRAKING (and, a fortiori, on the engine not being in overrun); the axle-A load threshold that used to be the only thing holding it back is no longer the gate and survives only as the BSFC policy it always was - and it is MEASURED to withhold 0.000 kWh over the whole trial, so it decides nothing either way. S2's genset ceiling is forced to zero on any sample where its lockup coupling is drawing the compression brake. The retarding ENVELOPE is untouched, so no achieved speed, trip time or descent case moves. The per-run assertion is hard and runs on every candidate: `heat_ledger.overrun_exclusivity` | FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical) (measured: `B1_reverted_brake_and_fuel`) |
| **M1** | material | every hand-written direction string deleted; this column and section 4.4's direction table are generated by `correction_directions()` from the one-factor rows, and the one-factor set is widened from the S1/S2 pair to all four candidates so that a correction which does not reach a candidate returns a bit-identical row instead of an assertion | record integrity - it moves no number; `FINDINGS_WS8_r2.md` M1 names three r2 direction cells that this file's own numbers contradicted, and the measurement above replaces all thirteen |
| **M2** | material | the per-km bullets, and every other per-km claim in the report, computed on the PAIRED per-seed statistic and labelled; the 'every candidate is more efficient per kilometre' sentence generated from data; the ratio of medians exported beside it for disclosure (`interface_ws8.per_km_margin_paired`) | record integrity - no margin moves; `FINDINGS_WS8_r2.md` M2 records that the r2 sentence was false for S3, whose two statistics differ in SIGN |
| **M3** | material | `corner_derate_scope` measures, leaf by leaf against nominal, what each corner's model actually changes, and the R28 conclusion is scoped by the measurement rather than asserted | record integrity - no number moves; the direction of error is exported |
| **M4** | material | ESC-WS8-1 restated with BOTH halves of the cell-substitution direction, the power half measured at the contact patch and the cold corner used as the in-model measurement of the transfer, and R27/ESC-1(c)'s execution as WS9's S4' cited with its provisional status | record integrity - no number moves |
| **m1** | minor | the ratio the 6% grade demands is a SWEPT result and now says so, with a resolution sensitivity solved at ten times the grid in both dimensions instead of the claim that no grid was doing any work | record precision |
| **m2** | minor | the unserved-energy table lists every case above 1 kWh instead of silently truncating at twenty | record precision |
| **m3** | minor | `heat_ledger_ws6.csv` carries `ledger_version`, a `basis` column, `components_sum_kW` and the governing run, and a per-component label file for the simulated member | record precision |
| **m4** | minor | the instantaneous peaks `heat_peaks` has always computed are enveloped and exported beside the sustained figure, in the ledger and in the CSVs | record precision |
| **m5** | minor | `all_cases_close_and_within_rating` states exactly what it tests, the simulated member is no longer exempt from the closure, and the resistor row's unfailability by construction is stated rather than left to be discovered | record precision - and the exemption it describes is what B1 came through |
| **m6** | minor | the bus-side/wheel-side slippage on the pack charge ceiling is stated where the number is quoted; the physics is unchanged because it is conservative and changing it would move every margin | record precision - deliberately no number moves |
| **m7** | minor | section 4.2 renders the measured R22(d) charge and its coast-permitting bracket for all five candidates instead of calling the disconnect a deleted tax that nobody pays | record precision |

### 2b. Raised and closed inside r3, by the extended closure

R3_DIRECTIVE item 1 ordered `heat_closure_check` extended to the simulated member. Extending it meant building a per-sample energy balance for every run, and the balance did not close until six book-keeping errors were found. None of them was in `FINDINGS_WS8_r2.md`; they are listed here because a correction that is not in the changelog is a silent one. The CONSEQUENCE column is measured, not asserted - where a correction has a one-factor row its direction is rendered from it, and where it cannot move a margin the reason is structural and stated.

| what | where | consequence |
|---|---|---|
| S0 was fuelled at the IDLE rate on the first few tenths of a second of every pull-away, because `stopped` is `v <= 0.1 m/s` and a launch begins inside it - the model credited the engine with about 28 kW of launch shaft power on 13.7 kW of fuel | `S0.account` | it moves THE RULER and therefore every margin, so it is switchable and measured rather than called small: FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp) |
| S0's clutch-slip heat was booked twice: once inside `p_shaft - aux - p_wheel`, which already contains it, and again as `p_slip_kw` | `S0.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S0's accessory row booked the full accessory load even on samples where the crank was at its full-load curve and could not carry it - r1's finding F3 for S2, surviving in the ruler. The row now books what the crank carried and the shortfall is exported | `S0.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S2's standstill idle fuel was added to the fuel total AFTER the fuel series, so the heat ledger never saw it; and its generator's own loss was priced off the free-speed locus while the crank was locked to the road | `S2.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S3's through-the-road path had NO heat rows at all - the engine was charged for the torque and the pack credited with the electricity, with the axle-A box and the e-axle's generating losses booked nowhere - and regen the full pack could not take was dropped with no bookkeeping at all | `S3.account`, `series_dispatch` | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it; and the rows it adds carry 0.000 kWh of through-the-road charge over the whole trial, because the path itself is inert once the B1 gate is applied (ESC-WS8-8) - the correction is real and its measured contribution is zero |
| regen the FULL pack cannot accept is dispatched to the brake resistor by `series_dispatch` and by S3's SOC loop - each says so in its own comment - and r3's first cut of the run closure carried it as an out-term OUTSIDE the component ledger. A real power flow with no component row is r1's F1 and r2's B1 over again. It is now booked to the resistor up to the rating whose mass was charged, and the remainder is exported as a CAPABILITY shortfall | `resistor_and_overcommitment`, `run_closure` | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it; worst overcommitment 254.3 kW sustained at `S4/grade_heavy/LH-520/seed8101` - escalated as ESC-WS8-10 |

### 3. Verdict stability

| candidate | verdict executed under R25 | verdict the same criteria give on the r3 numbers | headroom to the >= 3% nominal bar |
|---|---|---|---|
| **S1** | KILL | KILL | 3.69 pp short |
| **S2** | KILL | KILL | 2.41 pp short |
| **S3** | KILL | KILL | 4.09 pp short |
| **S4** | KILL | KILL | 6.84 pp short |

WHR on the r3 numbers: S1 DROPPED, S2 DROPPED, S3 DROPPED - unchanged.

**R3_DIRECTIVE item 1's own trip-wire, implemented rather than remembered.** R3_DIRECTIVE item 1: S3's fuel correction is expected to improve it by several percent and to leave it far below the bar. If S3's NOMINAL ENSEMBLE-MIN crosses +3%, the round STOPS and reports and does not touch the verdict. S3's nominal ensemble-min on the r3 numbers is -1.09% against the +3% bar: `crossed = false`. S3 is dead on CAPABILITY regardless of fuel - no fixed ratio both cruises at 105 km/h and holds the 6% grade at 36,300 kg - so this trip-wire is about the fuel number the record carries, not about the verdict's reason.

**`all_unchanged = True`.** If `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3, R3_DIRECTIVE item 1). It carries BOTH tests: the four executed verdicts against the pre-committed criteria, and R3_DIRECTIVE's own trip-wire on S3's nominal ensemble-min.

### 4. Environment

r1's artifacts were produced on Python 3.11.15 / numpy 2.4.6 on x86-64 Linux; r2's and r3's are produced on Python 3.14.3 / numpy 2.5.2 on arm64 macOS. The two platforms differ in the last one or two units in the last place of a double - a relative difference around 1e-16, from libm and SIMD reduction order, not from any change here. Byte-stable regeneration (rule 1) is a property of a run reproducing ITSELF on one machine, and it is checked in section 14 on this one. Nothing in the errata depends on that difference, and no reported figure is quoted to anything like that precision.

### 5. Inputs, SHA-pinned

Every source file and every read-only object inherited from another workstream is pinned by sha256 in `interface_ws8.inputs_sha256`, so a consumer can tell from the export alone whether the numbers it holds came from these exact inputs. 23 files are pinned, and r3 adds this round's order, the findings file it closes and the baseline it runs against without dropping r2's - the r2 corrections are still live in the code and the verdicts still cite R25.

---
