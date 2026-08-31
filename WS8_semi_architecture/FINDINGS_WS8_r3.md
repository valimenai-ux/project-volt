# FINDINGS — WS8 (Vehicle One) — round 3

> **Provenance of this file.** Authored by the `ws-adjudicator` agent (fresh context, Opus, round 3) launched per CLAUDE.md rule 9. That agent's harness prohibits it from writing `.md` files to disk, so it returned its findings as text and the WS8 worker session persisted them here **verbatim and unedited**. The worker neither authored, softened, nor acted on any finding below. Nothing in this folder was changed by the adjudicator.

**Verdict: NOT CLEAN. Two blocking, six material, twelve minor.**

Nothing found moves a verdict. `all_unchanged = True` is correct on the r3 numbers, and I re-derived all four kills and the three WHR drops independently against the pre-committed criteria. B1's control rule is genuinely and correctly applied, the retarding envelope is genuinely untouched, and rule-1 determinism holds — I tested all three rather than accepting them. Both blocking findings are in the round's *account of itself*: the changelog's central claim about what moved is wrong for the candidate that moved most, and the round's own new R14 export names a statistic it does not carry.

---

## 0. Independently re-derived, and agreeing

| quantity | report / interface | my re-derivation |
|---|---|---|
| **all 24 corner ensemble min / median / max** | §6.1, `worst_case_margin_pct.cases` | rebuilt from per-cycle `e_fuel_MJ_corrected` and `distance_km`, 70/30 rate mix, paired per seed: **max abs error 3.6e-15 pp** |
| **all 24 corner per-km paired margins** | §0, `per_km_margin_paired` | same rebuild on the other denominator: **3.6e-15 pp** |
| `fuel_g_corrected` decomposition | — | `raw + charge_correction + unserved_correction` reproduces every one of 480 values, **max rel err 0.0** |
| four worst-case margins + governing case | `worst_case_margin_pct` | explicit min over the six-corner set; all four agree exactly, all four govern at `cold_minus10C` |
| ADVANCE/KILL, all four | §9 | criteria re-applied from raw: KILL ×4, `any_advance = False` |
| WHR gate, all three | §5 | ensemble-min against 2.5%: +1.65 / +1.57 / +1.93 → DROPPED ×3 |
| heat ledger, 225 component cells + 45 worst-case rows | §12, both CSVs | **zero mismatches**; R14 max-over-enumerated-set and the governing-case label hold for every (candidate, component) pair |
| escalations | §11 | 10 escalations, **all** cite a ruling, **all** carry `why_not_self_resolved` and `asks` (rule 8) |

**Interface integrity (three-way), checked independently of `verify_ws8.py`.** The JSON block extracted from §13 is **byte-identical** to `results_ws8.json['interface_ws8']` at `json.dumps(..., indent=1)` (186,925 bytes) and equal again after parsing. `heat_ledger` equals `interface_ws8.heat_ledger_WS6` exactly. `verify_ws8.py` passes **240** checks (151 in r2).

**Determinism (rule 1) — tested, not accepted.**
- **Half 2, my own sandbox copy:** `run_ws8.py --from-checkpoint` reproduced `results_ws8.json` and **all ten** CSVs **byte-identically** against the committed artifacts.
- **Half 1, my own from-scratch re-simulation:** separate folder, separate process, `--jobs 6` (against the committed run's 5 and the checker's 4), sibling workstreams symlinked. `task3_trial/nominal` reproduced with sha256 `5b16957caeb3a7f4…` — **the same sha the committed record names**. `task1_cycles`, `task2_s0_calibration`, `task4_whr` and `one_factor` also identical.
- **The concurrent WS4 edit does not reach WS8's numbers, and I verified it two ways.** `run_ws8.py:560` uses `mp.get_context("fork")`, so every worker inherits the parent's single import of `ws4_chain`; and my from-scratch half-1 run read the *post-edit* WS4 tree and still reproduced the committed nominal trial bit for bit. (The pin itself is a separate problem — see **M6**.)

**The B1 rule is real, and the "envelope untouched" claim verifies structurally.** I mapped every `errata_on()` call site by AST: all seven live inside `S0.account`, `S2.account` or `S3.account`. None is reachable from `envelope()`, `v_cap()`, `_retard_channels()` or `retard_split_arrays()`, and `run_one` computes the trace *before* calling `account()`. No achieved speed, trip time or descent case can move with the switch. The per-run assertion is hard, runs on all 480 runs, and `examined_every_run` closes the r2-m5(a) skip-by-omission hole. `samples_brake_and_shaft = 0` everywhere.

**ESC-WS8-8's central claim is correct.** `ScaledEDrive.eta_wheel_to_bus` (`ws8_electric.py:201`) returns exactly `0.0` when `p_capt_kw <= 1e-9`, and S3 prices its charging headroom as `p_chg_head_bus = f_a_head * v/1e3 * eta_g` with `eta_g = eta_wheel_to_bus(v, F_regen*v/1e3)`. On every non-braking sample `F_regen = 0`, so the headroom is identically zero. r2's through-the-road charging was therefore exclusively a braking-sample phenomenon, exactly as the escalation says. Correctly raised, correctly not self-resolved.

**M4 / ESC-WS8-1 is properly closed.** Both directions of the cell substitution are stated and measured; the WS9 citation carries status, commensurability and vintage caveats. I checked all eight hand-declared `WS9_S4P_CITATION` values against `../WS9_vehicle_one_wave2/results_ws9.json` — **all eight match to full double precision** (see m9 for the pinning caveat).

**r2's m2, m3, m4 and m7 are genuinely closed.** All 30 unserved cases above 1 kWh are listed; `heat_ledger_ws6.csv` carries `basis`, `components_sum_kW`, `ledger_version` and `governing_run`; a per-component label file exists; instantaneous peaks are exported beside the sustained figures; §4.2 renders the measured R22(d) charge and its coast-permitting bracket for all five.

---

## BLOCKING

### B1 — An unmeasured control-law change to S3's charge throttle-back is worth +1.64 pp of S3's +6.90 pp movement, and the changelog states that it does not exist

**What is wrong.** §15.1 and `CHANGELOG_WS8_r3.md` say, of the r2 → r3 movement:

> **Almost all of that movement is one correction, and it is measured rather than inferred.** … FOR S2 (+0.085 pp), S3 (+5.262 pp) … Everything r3 changed besides that rule is an ACCOUNTING correction … Only one of those moves a margin at all, because it moves THE RULER … **Every other r3 correction is a heat row, and no margin reads the heat ledger.**

That statement is exactly right for S1, S2 and S4 and false for S3. There is a second r3 change that moves S3's fuel, it is not B1, it is not the launch-fuel fix, it is not a heat row, it has no one-factor row, and its direction is nowhere measured.

**Evidence — I rebuilt r2 and differenced it.** I checked out the r2 pipeline from `git HEAD` into a scratch tree (with WS4 also at HEAD, so the concurrent edit cannot pollute the comparison) and re-ran the nominal corner. It reproduces r2's numbers of record exactly, which also validates the hand-typed `R2_MARGINS` literals as accurate citations:

| | r2 re-run, min / median | hand-typed `R2_MARGINS` | r3 as reported, median | move | B1 + launch, measured | **residual** |
|---|---|---|---|---|---|---|
| S1 | −0.6912 / **+0.7309** | −0.69 / +0.73 | +0.7337 | +0.0028 pp | +0.0028 | **+0.0000 pp** |
| S2 | +0.4753 / **+1.7999** | +0.48 / +1.80 | +1.8879 | +0.0880 pp | +0.0880 | **+0.0000 pp** |
| **S3** | −7.6546 / **−5.2626** | −7.65 / −5.26 | **+1.6381** | **+6.9007 pp** | +5.2652 | **+1.6355 pp** |
| S4 | −3.8446 / **−1.0626** | −3.84 / −1.06 | −1.0597 | +0.0029 pp | +0.0029 | **+0.0000 pp** |

The residual is zero to four decimals for three candidates and **+1.6355 pp — 24% of the whole move — for the one candidate the round says moved because of B1.** It is also larger than the entire r2 → r3 movement of S1, S2 and S4 combined (0.094 pp).

**The mechanism, located and measured.** `git diff` on S3's SOC loop shows r2's pack-overflow branch:

```python
if de > room:                                   # pack ENERGY full
    pc = room / self.pack.eta_chg / h ...
    de = max(room, 0.0)
    chg = max(0.0, chg - ((-net) - pc))         # r2: throttle charging back
```

replaced in r3 by an **unconditional** block outside the `if de > room:` guard:

```python
over = surplus - pc                             # pc = min(surplus, p_chg_max)
if over > 0.0:
    cut = min(chg, over)
    chg -= cut
    over -= cut
    p_shed[i] = over
```

Because `pc = min(surplus, p_chg_max)`, `over > 0` now also fires when the surplus exceeds the pack's charge **power** ceiling, not only when the pack is energy-full. `chg` sets `f_chg_wheel`, which sets `t_a`, which sets S3's fuel. This is a change to *when the engine stops charging the pack* — a control law, not bookkeeping.

I isolated it on S3 / nominal / LH-520 / seed 8101 with the B1 switch reverted, running the two throttle-back rules side by side over the identical trace:

| rule | through-the-road charge | unserved | samples throttled on the power ceiling alone |
|---|---|---|---|
| r2 (pack **energy** full only) | **25.664 kWh** | 117.910 kWh | 0 |
| r3 (energy full **or** power ceiling) | **20.246 kWh** | 117.910 kWh | **2,485** |

**5.418 kWh of engine charging withheld on one cycle of one seed, on a branch r2 did not have, with unserved energy bit-identical** — so the withheld charging is a pure fuel reduction with no capability penalty. That is the direction and roughly the magnitude of the missing +1.64 pp.

**Why blocking.**
1. It is the round's headline deliverable. R3_DIRECTIVE ordered the direction of every correction measured (item 2, M1) and the changelog says every DIRECTION cell is generated. This one is neither generated nor stated; the changelog affirmatively denies it exists.
2. It is outside the directive's declared-exhaustive scope. Item 1 orders the *gate*; item 6 orders errata. Re-specifying when S3's engine stops charging is neither — and the round escalated ESC-WS8-8 rather than re-specify the charging law, while having already re-specified part of it here.
3. It is booked in §15.2b as margin-neutral. The S3 row and the `resistor_and_overcommitment` row both carry the CONSEQUENCE cell "**no margin can move**: the heat ledger is built from the completed runs … and no margin reads it". For S3 that is false by 1.64 pp.
4. It moves S3 **toward** R3_DIRECTIVE item 1's own STOP condition. The trip-wire (`nominal ensemble-min ≥ +3%`) is evaluated at −1.09% and is not close, so nothing is triggered — but the round is asserting it checked a trip-wire on a number that contains 1.6 pp it did not know was there.
5. It is invisible to every check the round built. `one_factor` has no row for it; `verify_ws8.py` cannot reach it; the run closure passes because the change conserves energy; the exclusivity assertion passes. It surfaced only on re-running the superseded round and differencing — the class this seat exists to catch.

The physics of the r3 rule is arguably *better* than r2's. That is not the finding. The finding is that a fuel-moving control change is on the record as a heat row.

**Resolution.** (i) Add a one-factor row that reverts the S3 charge throttle-back to r2's energy-full-only rule and re-run S3 at nominal, so the +1.64 pp is measured like every other correction. (ii) Move it out of the §15.2b "no margin can move" column and into §15.1's account of what moved. (iii) Decompose the worst-corner column too, or state that it is not decomposed — the r2 → r3 corner moves (S3 +7.81 pp) are attributed to B1 with no measurement at all. (iv) If re-specifying the throttle-back was outside the order, say so and let the lead rule on it.

---

### B2 — `retard_overcommitment` exports an instantaneous spike under an R14 rule string that says "sustained 60-second", and the governing case it labels is not the governing case on the statistic it names

**What is wrong.** The export's own rule reads:

> "max over the enumerated (candidate, corner, cycle, seed) case set of the **sustained 60-second** retarding power the run COMMANDED and no sink could absorb"

The value it maxes over, `retard_overcommitted_peak_kW`, is computed as **`float(np.max(_over))`** at `ws8_candidates.py:1639, 2128, 2707, 2890` — the maximum single 10 Hz sample. The genuine 60-second mean is computed in the same object, at `ws8_candidates.py:1233` inside `run_closure`, as `np.max(_moving_average(p_over, n_win))` — and that one is discarded.

**Evidence — the report refutes itself in one sentence.** §7.1: "Worst case **254.3 kW** sustained (governing case: `S4/grade_heavy/LH-520/seed8101`, **0.13 kWh** on that run)". 0.1267 kWh at 254.3 kW is **1.79 seconds**. A genuine 60-second mean of 254.3 kW would be 4.24 kWh.

Measured across all 120 affected runs, exported figure against the true 60-second sustained figure the same run already carries:

| run | exported "sustained" | true 60-s sustained | ratio |
|---|---|---|---|
| `S4/grade_heavy/LH-520/seed8101` (**the governing case**) | 254.3 kW | **7.6 kW** | **33.4×** |
| `S4/payload_plus20/LH-520/seed8101` | 252.7 kW | 7.6 kW | 33.3× |
| `S3/nominal/LH-520/seed8106` | 200.3 kW | 62.2 kW | 3.2× |
| `S3/nominal/LH-520/seed8101` | 200.3 kW | 34.1 kW | 5.9× |

**The true worst 60-second sustained overcommitment anywhere in the trial is 166.7 kW, on a different run.** The exported headline is 1.53× too high and the governing case named inline is one of the *least* sustained members of the set.

**Why blocking.** R14 is binding and this field violates both halves of it: the max is taken over the wrong statistic, and the case labelled inline is wrong on the statistic the rule names. The whole ledger is built on `HEAT_SUSTAINED_WINDOW_S`, whose docstring argues at length that "a Class 8 snubbing to a stop puts 600 kW into the foundation brakes for a moment, and reporting that as the sizing case would be as wrong in one direction as r1's 211 kW resistor figure was in the other" — and this field does exactly that, in the round that wrote the docstring. The number is the entire quantitative content of ESC-WS8-10, a live escalation whose three options the lead is being asked to price on its magnitude, and it is quoted again in §15.2b. It is the "interface exports the wrong member of a set the prose describes correctly" class that opened this seat.

**Scope, stated so the lead can calibrate.** No margin reads it, no verdict depends on it, and WS6 is explicitly told not to size on it. The defect is confined to the record and to ESC-WS8-10's evidence — but it is a defect the round created this round, in a new R14 export, with the correct quantity sitting unused in the same dict.

**Resolution.** Export `run_closure.retard_overcommitted_peak_kW` (the 60-second mean) as `retard_overcommitment.value_kW`, re-derive the governing case and the per-candidate table from it, and keep the instantaneous maximum beside it labelled as such — the same convention `heat_peaks` already uses for every other component. Restate §7.1, §15.2b and ESC-WS8-10's materiality on the corrected figure.

---

## MATERIAL

### M1 — R3_DIRECTIVE item 2 is not discharged: a hand-written direction-and-count claim survives, is factually wrong, and is contradicted by this report's own generated sentence

`make_report_ws8.py:884-885`, rendered at `REPORT_WS8.md:355`:

> "…the R28 half of that is contradicted by the table below, in which **S1, S2 and S4 all GAIN** at that corner relative to nominal. The claim is withdrawn rather than restated (**r2 finding M1**)."

**All four gain.** S3 nominal min −1.085 → R28 min −0.559; median +1.638 → +2.156. And the same report says so, generated, at `REPORT_WS8.md:4850`: "**S1, S2, S3, S4** gain at the R28 corner relative to nominal."

The string is **r2's fact, carried forward verbatim**: `CHANGELOG_WS8_r2.md:45` reads "S1, S2, S4 gain at the R28 corner relative to nominal; **S3 loses there**" — which was true on r2's numbers and stopped being true when B1 moved S3. Aggravating: the generator fetched the computed directions two lines earlier and discarded them —

```python
877        cdir = (g("correction_directions/F2/direction"),
878                g("correction_directions/F11/direction"))     # never used
```

— and `verify_ws8.py`'s direction check is one-directional containment (`if v["direction"] not in REPORT: fail`), so it proves generated strings are *present* and structurally cannot detect extra prose that contradicts them.

This is r2's M1 failure mode — a hand-written direction claim inside a generated artifact, contradicted by the round's own numbers, unreachable by the verifier — recurring in the sentence that cites M1 as its authority. R3_DIRECTIVE item 2 ("delete every hand-written direction string") is discharged for F3/F6 and not in general.

**Resolution.** Generate the sentence from the same `better`/`worse` computation §15.1 already uses (`make_report_ws8.py:1803-1825`); add it to the verify set.

### M2 — `corner_derate_scope` exports `electric_side_unchanged: true` and "AND NOTHING ELSE", and its own probes show otherwise

M3's fix builds `corner_derate_scope` to measure, "leaf by leaf", what each corner changes, and declares "membership is computed, not declared". I differenced the probes it exports. **23 leaves move** between `nominal` and `hot_alt_2000m_45C`:

| leaves | nominal → R28 |
|---|---|
| 5 × `engine_full_load_torque_at_1300rpm_Nm`, 3 × `genset_bus_ceiling_kW` | derate — listed in `derates` |
| **5 × `accessory_bus_kW`** | **3.4 → 6.0** — a bus-side, i.e. electric-side, quantity under rule 6 |
| 5 × `accessory_mech_kW` | 4.0 → 7.0 |
| 5 × `air_density_kg_m3` | **1.196 → 0.871** — the corner's dominant effect |

Yet `R28_corner.electric_side_unchanged = true`, `R28_corner.does_not_derate = []`, and the exported `statement` — rendered verbatim in §15.1 and in the changelog — says the corner derates the engine curve "AND NOTHING ELSE". The report's §6.1 cell says "no electric-side quantity moves at all", and the statement's *own next-but-one sentence* concedes it: "The cab-cooling load IS charged symmetrically (**mechanical and bus-side both rise**)."

A consumer reads `electric_side_unchanged: true`. Under CLAUDE.md rule 6 that boolean is false on the block's own data. R35/R28 hands this statement to WS9, which is why it matters even though no number moves.

**Resolution.** Derive `electric_side_unchanged` and `does_not_derate` from the probe diff rather than declaring them; scope the statement to "derates *the engine*, and separately changes air density and the cab-conditioning load on both sides".

### M3 — S3's headline margin is 18.6% correction priced on a path the model shows was saturated, and its sign flips on a 10% change in that pricing; the leverage is never bracketed

`correction_eta_basis` for S3 declares the pricing itself: *"duty-averaged mechanical fuel-to-wheel over this run (no genset exists; bus-side shortfall priced on the wheel-side path, **the generous direction**)"*. §4 flags the correction-share column as the one to read sceptically. Neither says how much of S3's answer rests on it.

Nominal LH-520, median over seeds:

| | raw fuel | unserved correction | share | unserved |
|---|---|---|---|---|
| S1 | 159,327 g | 1,574 g | 1.0% | 7.9 kWh |
| S2 | 158,378 g | 868 g | 0.6% | 4.4 kWh |
| **S3** | 130,610 g | **30,461 g** | **18.6%** | **138.8 kWh** |
| S4 | 154,293 g | 7,273 g | 4.5% | 34.3 kWh |

S3's margin as a function of the pricing efficiency (×1.00 reproduces the report exactly):

| multiplier | ×0.80 | ×0.90 | **×1.00** | ×1.10 | ×1.20 |
|---|---|---|---|---|---|
| S3 nominal min / median | −5.32 / −3.00 | −2.97 / −0.42 | **−1.09 / +1.64** | +0.46 / +3.32 | +1.74 / +4.73 |
| S1 nominal min / median | −0.97 / +0.57 | | −0.69 / +0.73 | | |
| S2 | +0.26 / +1.79 | | +0.59 / +1.89 | | |
| S4 | −5.35 / −1.90 | | −3.84 / −1.06 | | |

**S3's reported nominal median crosses zero at ×0.93.** S1, S2 and S4 move by 0.1–0.8 pp under the same perturbation; S3 moves by 4.6 pp.

And the pricing is not merely "generous" — it is priced on a path that was, by construction, unavailable. S3's bus shortfall arises only where `f_b = F_trac − f_a > 0`, which requires `f_a = f_a_cap`: axle A is at its cap on every sample that generates unserved energy. Charging the shortfall back at axle A's own duty-averaged fuel-to-wheel efficiency (0.387) prices it on a saturated path. The physically available alternative — through-the-road charging — is two conversions worse *and* is inert (ESC-WS8-8).

r3 did not create this (F6 is r2's), but r3 **increased S3's exposure to it**: B1 removed the 20–39 kWh per run of through-the-road charge that used to fill the pack, so more of S3's mission now runs on a paper correction than did in r2. The `F6_reverted_peak_point_pricing` row shows S3 at +3.62% and is labelled "AGAINST S3 (−1.978 pp)" — i.e. the round *has* one bracket, in the direction that flatters S3 further, and none in the direction the physics points.

**Resolution.** Export a pricing bracket for S3 in the unfavourable direction (the through-the-road path's own efficiency is the obvious member) beside the `credit_free` bracket §4 already carries, and state the leverage where the +1.64% is quoted. No number of record need move.

### M4 — Trip time is absent from the interface entirely, the report claims the candidates run "at the same speeds", and S3's mission is 20–34% longer

§4, describing how to read the correction column:

> "…charged back as fuel **so that every candidate is compared having completed the same mission at the same speeds**"

That is false, and §2 says why it must be: the trace is integrated forward against each candidate's own envelope, deliberately. Measured, median over 8 seeds:

| | S1 | S2 | **S3** | S4 |
|---|---|---|---|---|
| nominal LH-520 vs S0 | −1.96% | −2.30% | **+20.12%** | −2.56% |
| nominal REG-165 | −0.18% | −0.25% | **+9.10%** | −0.29% |
| grade_heavy LH-520 | −2.42% | −3.02% | **+30.24%** | −3.42% |
| grade_heavy REG-165 | −2.46% | −2.67% | **+33.75%** | −3.11% |

S3's nominal LH-520 average speed is **70.2 km/h against S0's 84.3**, and it is power-limited on **32.9%** of samples against S0's 14.4%.

`duration_s`, `avg_speed_kmh` and `power_limited_frac` are in `data/candidate_runs.csv` and in **none** of `interface_ws8` — I checked for every spelling. So the R14 export that WS6/WS9/WS10 consume cannot see that S3's +7.44% per-km win is bought with a fifth to a third more time on the road, and §0's per-km bullets carry no such scope. BASELINE_v5 **R38** makes design-duty trip time a **gate** for Vehicle One (`trip_time_the_metric_cannot_see`); WS8 r3 runs against BASELINE_v5 and exports no equivalent. ESC-WS8-10 and ESC-WS8-6 mention trip time only as a descent-speed side effect.

S3 is dead on capability either way, so this changes no verdict. It is the largest unreported fact about the trial's numbers, and WS9/WS10 inherit the convention.

**Resolution.** Export a trip-time table to `interface_ws8` (candidate × corner × cycle, 8-seed envelope, % of S0), correct the "at the same speeds" sentence, and state S3's trip-time penalty where its per-km margin is quoted.

### M5 — The rule-1 record's booleans describe the state *before* the file was written, its own method string says the opposite, and the one boolean that records the rule-1 property is exported `false` and never rendered

`data/determinism_check.json` carries:

```json
"full_run_matches_checkpoint_rebuild": false
```

and its `method` string, rendered verbatim into §14, says:

> "…the comparison is repeated after it is written and the script exits non-zero if the repeat disagrees; **the booleans below therefore describe the committed artifacts and not a state that preceded them.**"

All three booleans come from `pre` — the half-2 run performed *before* the file is written (`check_determinism_ws8.py:267-272`). The `post` run is executed and asserted but its result is **never recorded**. The sentence is precisely wrong about what the booleans describe.

Three further defects in the same block:
- `results_json_byte_identical` and `all_csv_exports_byte_identical` are both assigned from the *same* value, `pre["identical_between_rebuilds"]`, which is a single comparison over all eleven files. They cannot disagree; §14 renders one measurement as two results.
- `differing_files` — the only evidence that would let a reader judge the `false` — is computed in `half_2()` and dropped from the record.
- §14 renders `determinism.status = "PASS"` as "Regeneration check (rule 1): **PASS**" and renders the two `true` booleans, and omits the `false` one entirely. A consumer reading the JSON sees a rule-1 failure that the prose does not mention.

**I verified the property actually holds**: my own sandbox `--from-checkpoint` rebuild reproduced `results_ws8.json` and all ten CSVs byte-identically against the committed artifacts. So the exported `false` is a stale pre-write state, not a live failure — but nothing in the record says so, and the round's stated reason for generating this evidence was that "a hand-written claim about reproducibility is the weakest link in the chain it attests to."

**Resolution.** Record `post`, not `pre`; keep `differing_files`; give the CSV boolean its own comparison; render every boolean in §14 including any that is false, with its explanation.

### M6 — The SHA pin for `../WS4_genset/ws4_chain.py` names bytes the simulation never read

All 23 pins recompute correctly against the files on disk — I checked every one. But `INPUT_SHA256` is a **module-level constant evaluated at import time** (`run_ws8.py:3872`), so it is recomputed on every `--from-checkpoint` rebuild rather than captured with the simulation and carried in the checkpoint.

The committed artifacts were rebuilt from the checkpoint at 01:54:26 (after `determinism_check.json` at 01:54:18); the simulation ran 00:42–01:22. `WS4_genset/ws4_chain.py` was modified at **01:13:34** — during the simulation, before the rebuild. The exported pin is therefore `609fd499…` (post-edit) while the simulation read `7162656a…` (the version at `git HEAD`).

`inputs_sha256_scope` states the pin's purpose as "so a consumer can tell **from the export alone** whether the numbers it holds came from these exact inputs." As exported, it certifies bytes the numbers did not come from.

In this instance it is harmless — the WS4 change is additive instrumentation, and I confirmed both that `fork` prevents re-import in the workers and that a from-scratch re-simulation against the *post*-edit tree reproduces the committed nominal trial bit for bit. The mechanism is the finding: any later edit to a pinned input silently re-pins on the next rebuild without re-simulating, and `--from-checkpoint` is the documented rebuild path that the determinism checker itself runs four times per invocation.

**Resolution.** Compute the pins at simulation time and carry them in the checkpoint; on a `--from-checkpoint` rebuild, re-verify them and fail loudly on a mismatch rather than silently re-pinning.

---

## MINOR

**m1 — `R2_MARGINS` is 12 hand-typed result values feeding a rendered table *and* a rendered direction word, under a changelog preamble that says nothing is transcribed by hand.** `make_report_ws8.py:1696-1704`. Its docstring defends them as "citations of superseded rounds rather than results" — and my r2 re-run confirms all twelve are accurate to the printed precision. But the changelog's opening line says "every figure below is formatted out of `results_ws8.json` … Nothing here is transcribed by hand (rule 2)", and §15.1's entire left-hand column is not. Worse, §15.1's DIRECTION word is *derived* from them: `d_med = m["median"] - r2["nom_med"]` with a ±0.005 cut (`:1751-1754`) — a threshold exactly equal to the quantisation of a 2-dp hand transcription. `R1_MARGINS` (12 more literals, `:1688-1695`) is dead code, referenced nowhere.

**m2 — Hand-written numbers in generated prose that contradict rendered values in the same document.** Each is unreachable by the verifier.
- `:687-688` "about **100 kW** at the wheel" for 36,300 kg at 95 km/h level — §10 renders **112.1 kW** for the identical condition (`sanity.road_load_95kmh_flat.wheel_power_kW` = 112.125). The "roughly a third of rated" the WHR argument leans on is true of the rendered figure (0.319) and not of the typed one (0.284).
- `sanity.mountain_6pct.note`, rendered verbatim in §10: "**21.4 kN** … is **535 kW** at 90 km/h" sits beside the computed 21.33 kN / 533.20 kW in the same dict; and "the descent needs **the same number back** as RETARDING power" sits beside `retard_needed_at_90kmh_kW = 432.84` in the same dict — 81%, not 100%. ESC-WS8-1 quotes the correct 433 kW.
- `sanity.road_load_95kmh_flat.note`: "above **~80 km/h** the air is the bigger bill". The crossover is √(Crr·m·g / (0.5·ρ·CdA)) = **87.8 km/h**; at 80 km/h aero is 1,624 N against 1,959 N rolling. The same note's "which is why every candidate here wins or loses on driveline efficiency and mass, **not on regenerative braking**" is contradicted by Recommendation 5, which attributes the binding corner (cold, all four) to descent regen going to the resistor.
- §6.2 "a shortfall of 111 kWh, or **roughly six times the pack**" — 111.15 / 21.60 = **5.15×**. Six is the ratio of the *total* requirement (132.75) to the pack.
- `:924` "it is **3.60** only because…" typed six lines before the same value is rendered from `max_ratio_without_overspeed`; `:445` "**19.3 t** of payload" typed ten lines after the same value is rendered; `:682-683` "the real bar is nearer **3-4%** than **2.5%**" typed beside both values rendered from data; `:1980` "about **28 kW** … on **13.7 kW** of fuel" — neither figure exists in `results_ws8.json`.

**m3 — The S3 adhesion sweep is censored at its own grid ceiling, and the table's thesis is invisible in half its rows.** `run_ws8.py:1572` scans `np.arange(0.0, 0.0801, 0.0025)`, so 0.08 is the top of the grid. Four of eight `max_grade_held_on_adhesion` values are pinned there: dry and wet, for **both** axle A alone and the 6×4 tandem. §6.4's own thesis sentence — "S3's cruise traction sits on half the adhesion a 6×4 has" — is contradicted by its own top two rows, which read 8.00% / 8.00%. Dry axle-A adhesion is 52.95 kN against roughly 32.7 kN needed at 8%, so the true dry limit is far above 8%. The column heading "Steepest grade holdable" is not what was computed for those rows, and the interface exports `dry: 0.08, wet: 0.08` with no censoring note. Separately, `task5_s3_specific.diesel_axle_adhesion.rule` reads "**max** over the enumerated surface case set" where the code takes a min (the interface field `S3_diesel_axle_adhesion_grade_limit.rule` correctly says "min", so this is confined to the task block). S3's kill rests on the ratio, not on adhesion, so nothing turns on it.

**m4 — The run closure has no power over the per-component split, and §12's "exactly what that tests" does not say so.** I measured it on S0, S1 and S3 by perturbing the rows the closure is given:

| perturbation | max abs relative residual | `closes` |
|---|---|---|
| as shipped | 4e-16 (S1) to 3.4e-06 (S3) | True |
| **delete the largest heat row** | 0.51 – 0.98 | **False** — detected |
| **move that row wholly into another (total preserved)** | **unchanged to the last bit** | **True** — invisible |
| inflate that row by 1% | 0.005 – 0.010 | True — inside `CLOSURE_TOL = 0.02` |

The closure is a genuine and useful check for missing or extra power — which is the B1/F1 class, and it did find six real errors. But it is inert against mis-attribution between rows, which is what r1's F1(b) was (compression-brake heat booked as resistor heat), and it tolerates a row wrong by up to ~4% of itself. The per-component split is what WS6 consumes and is precisely what the closure does not test. Relatedly, clause (b) of `all_cases_close_and_within_rating` ("every component stays inside the rating") is now **unfailable by construction**: `resistor_and_overcommitment` clips the row at the rating. r2's m5(b) said the check could not fail; r3's answer makes it strictly less falsifiable while stating the fact honestly ("the resistors SATURATE"). §12's enumeration of what the flag tests should say both things.

**m5 — The 0.72-of-capacity axle-A threshold survives as an AND-condition on the through-the-road gate, and its measured zero is vacuous.** `ttr_gate = coupled & ~braking & ~overrun & ~(f_eb_applied > 0.0)`, and the 0.72 test is applied *inside* the opened gate. `e_ttr_blocked_by_load_policy` can only accumulate when the gate is open; the gate never opens; so "MEASURED to withhold 0.000 kWh" is zero by structure, not by test. The export's `rule` string is careful and correct about what the zero distinguishes ("so the reader can see that the threshold is not what makes the path inert"), and `path_is_inert: true` is stated plainly — so this is disclosed, not hidden. But R3_DIRECTIVE item 1 says to gate "on the VEHICLE NOT BRAKING, **not on axle-A force being small**", and the axle-A test is still an AND-condition on the same gate. If the lead rules ESC-WS8-8(b), the directive's instruction becomes undischarged at exactly the moment it starts to matter.

**m6 — `unserved_energy_kWh.rule` never names the seed dimension.** It reads "max over the enumerated (candidate, corner, cycle) case set". I checked all 30 cases: every one is correctly the 8-seed **max**, so rule 4 is satisfied in fact. The rule string does not say so, and a consumer would read each cell as a single draw. `retard_overcommitment`'s rule does enumerate seed; these two should match.

**m7 — Seven governing-case labels in the heat ledger are decided by ≤2 ULP ties.** S1 `engine_coolant_kW` is 158.57050434954053 at `climb_6pct` and 158.57050434954036 at `simulated_worst_run`; the label goes to `climb_6pct` on a 1.7e-13 difference. The same tie decides S1 `engine_exhaust_kW` (labelled `simulated_worst_run`), S1/S2 `generator_rectifier_kW`, and S4 `engine_coolant_kW`/`engine_exhaust_kW`/`generator_rectifier_kW`. The physics is right — a genset pinned at its ceiling on a sustained climb *is* the analytic climb point — but R14 asks for the governing case labelled inline, and a label decided at 1e-16 relative is not a determination. Report the tie.

**m8 — The surplus retarding power is in no heat row at all, and if the modelled speed is held the foundation-brake row is understated.** §12 explains the universal foundation-brake advisory exceedance by saying "the foundation brakes make up the difference until the truck slows" — but `friction_brake_kW` is built from `tr["F_friction"]`, which comes from the over-committed envelope and never sees the shed. Measured on nominal LH-520 seed 8101: S1's friction row peaks at 20.3 kW sustained and would be **76.5 kW** if the surplus were added; S3's 19.4 → **53.5 kW**, against a 60 kW declared allowance. The two rarely coincide (3 and 50 samples respectively), so the effect is bounded and modest — but WS6 sizes brake cooling on the advisory row, and the direction is under-sizing. The choice to cap the resistor row and export the surplus separately is, on balance, right: booking 450+ kW to a 340 kW resistor would publish a cooling load the hardware cannot produce, and the alternative was considered, rejected in writing, and escalated rather than self-resolved. What the escalation does not state is that the model implements neither of its two physically consistent readings — the truck neither goes faster nor brakes on friction.

**m9 — `WS9_S4P_CITATION` is hand-declared and WS9 is not pinned.** All eight values verify exactly against `../WS9_vehicle_one_wave2/results_ws9.json` (`pack_Wh_per_kg` 160.0, `pack_mass_kg` 937.5, `nominal_margin_pct_min` 11.953945283686181 = WS9's `margins/nominal/GH-REG-165/S4p/ensemble/min`, `control_duty_nominal_margin_pct_min` −6.807699516392367 = WS9's LH-520 ensemble min, `payload_delta_vs_ruler_kg` −520.6296906751959, and the three pack/resistor ratings). The `vintage` caveat is stated. But `results_ws9.json` is not in `inputs_sha256`, and BASELINE_v5 R39/ESC-8 orders WS9 re-run against WS8 r3 — at which point these typed constants go stale with nothing to detect it.

**m10 — Three sanity/report statements weaker than they read.** (a) `make_report_ws8.py:1564` emits "And every candidate exceeds it, not only S0" **outside** the `if adv:` guard, so it would print even with an empty advisory table. (b) `sanity.startability_sizing` has `required_force_kN == S1_available_at_2kmh_kN` **exactly** (44.3725858123714 both), because the machine is sized to the requirement; `agree: true` confirms the sizing code, not a capability, and §10's "the electric paths are sized to deliver it **and do**" reads as the latter. (c) That same check quotes "inside the 105.9 kN dry-tandem adhesion ceiling" while the candidate whose launch adhesion actually binds is S3 on a **single** axle (52.95 kN dry, 34.04 kN wet), which §6.3 reports failing on wet.

**m11 — §0's per-km sentence is generated but scoped to nominal by omission.** "S1, S2, S3, S4 win per kilometre against the conventional truck **on every seed**" is correctly built from `per_km_margin_paired.corners.nominal` (M2's fix is real). It does not say "at nominal", and at `cold_minus10C` S1, S3 and S4 lose per km on every seed (min/median −5.33/−4.91, −7.44/−5.76, −9.08/−8.36) — the corner the same report calls binding for all four. Recommendation 3 repeats the unscoped form.

**m12 — Two claims about the B1 rule's own structure are false as stated, though neither changes a number.** (a) `braking_mask`'s docstring and S3's inline comment both assert that "`braking` is a strict subset of `overrun`", and S3's comment concludes from it that "the conjunction IS `~overrun`". Measured: **451 (nominal), 462 (cold), 460 (grade-heavy)** samples per S2 LH-520 run are braking and *not* in overrun, because `overrun_mask` also carries the `rpm > 1.1 × idle` stall guard. S3's gate ANDs both conditions, so it is harmless there — but the claim is offered as auditable and is wrong. (b) S2's gate is keyed on the compression brake actually applied rather than on lockup-band membership, and the code states plainly that a band-membership gate would fail the per-run assertion on 1–3 samples per cold-corner run. I measured it: exactly **1 sample per run** across nominal, cold and grade-heavy, at 72.43–72.46 km/h against a band floor of 72.5 km/h, carrying ≤77 kW and ≤0.0021 kWh. The root cause is `retard_split_arrays` interpolating the engine-brake cap across the band edge on the 0.05 m/s grid, leaking compression-brake capability just outside the declared band; r3 shaped the gate around the leak rather than fixing the leak, because fixing it would move the envelope. That is a defensible trade given the envelope must not move, it is disclosed in the code comment, and the magnitude is one sample. But the honest description is "the envelope leaks one sample outside the band and the gate follows it", not "the gate is keyed on the quantity the assertion tests, which makes the code and the assertion one statement" — the latter is true and is also what makes the assertion unable to fail.

---

## Things I looked for and did not find

- **Single-draw stochastic extrema (rule 4).** None. I recomputed all 24 corner minima, medians and maxima on both denominators from raw per-cycle fuel, and all 30 unserved-energy cases; every one is an 8-seed envelope and every one agrees.
- **Peak-point scalars (rule 5).** None in a live path. WHR is a genuine load-dependent model and its gate is read against the candidate *without* WHR.
- **A governing case outside the enumerated set.** Not found. The R14 max-over-enumerated-set property holds for all 45 (candidate, component) heat-ledger pairs and for all four worst-case margins. **B2 is the mirror image of this class** — the case set is right and the *statistic* is wrong.
- **Verdict interference.** None. The round did not touch a verdict; `all_unchanged = True` and the r3 trip-wire (`crossed = false`, −1.09% against +3%) are both correct on the numbers as they stand. I checked how far the trip-wire is from firing under M3's pricing sensitivity: it would take a ~35%-more-efficient correction pricing to cross +3%, so the STOP condition's answer is robust upward even though its input is not.
- **Escalations self-resolved (rule 8).** None. Ten escalations, all citing a ruling, all with `why_not_self_resolved` and `asks`. ESC-WS8-8, ESC-WS8-9 and ESC-WS8-10 are all correctly raised rather than absorbed, and ESC-WS8-9 is right that R34 and an exhaustive scope cannot both be satisfied by a workstream session.
- **Assignment coverage.** Tasks 0–5 executed; every ordered sensitivity plus R28's corner; all three S3-specific risks. R3_DIRECTIVE items 1, 3, 4, 5, 7 are discharged; item 2 is partially discharged (**M1**); item 6's errata set is discharged with the exceptions in m1–m3.
- **Optimistic inputs inherited without flags.** The cold charge acceptance, the R18 transfer, the k=3.6 machine stretch, the Willans re-anchoring and the WS3 cell set are all flagged and escalated. **M3 is an optimistic input generated inside WS8 rather than inherited**, and it is the one that is flagged only qualitatively.
- **Mass closure.** tare + payload = 36,300.00 kg for all five, summed independently.

## Suggested disposition

- **B1** should close before the r3 numbers become the record. It is small to fix — one more one-factor row and two corrected changelog cells — and it changes no verdict, but §15.1 is the artifact the baseline will quote and it is wrong for S3 by 24% of S3's movement. The lead should also decide whether re-specifying S3's charge throttle-back was in scope at all.
- **B2** should close before WS6 or WS9 read the export or the lead rules on ESC-WS8-10, whose options are priced on the number. The correct quantity is already computed in the same object.
- **M1, M2, M5** are all the same class the round was convened to eliminate — a hand-written or hand-declared claim inside a generated artifact that the verifier cannot reach, contradicted by the artifact's own data. M2 and M5 additionally put a false boolean in the machine-readable block.
- **M3 and M4** change no number here and are the two statements WS9 and WS10 will most regret inheriting: S3's fuel result is a function of a pricing convention nobody bracketed, and the metric of record cannot see a 20–34% trip-time penalty that R38 has already ruled is a gate.
- **M6** is a mechanism finding, benign in this instance and verified benign; it should be fixed before another round runs in a tree someone else is editing.
- **m1–m12** can travel as a checker-pinned errata set. **m4** and **m5** are the two worth pinning, because both are assertions that read stronger than what they test — which is r2's m5 recurring in a new place, twice.

*Findings only. Nothing here rules on an escalation, nothing reopens a verdict, and nothing in the workstream folder was modified — I verified the folder's git state and the sha256 of `results_ws8.json`, `REPORT_WS8.md` and `ws8_candidates.py` are unchanged from session start. All re-runs were performed in isolated scratch copies under `/private/tmp`.*
