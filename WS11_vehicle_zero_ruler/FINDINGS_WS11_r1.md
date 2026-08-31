# FINDINGS — WS11 VEHICLE ZERO RULER TRIAL, ADJUDICATION ROUND 1

**Verdict on the round: NOT CLEAN — 3 blocking, 8 material, 13 minor.**

Adjudicator: fresh context, disk only, independent re-derivation. Byte-stability was **not** re-established (the foreman's mechanical gate passed; effort was spent on whether the numbers are right). Nothing in the workstream folder was modified. All re-derivation was done in a scratchpad against the committed code and the repo venv (`numpy 2.5.2`).

The two verdicts are **not** symmetric in their exposure. **V1's ADVANCE is real and robust in the direction the report claims** — but its binding corner has 1.05 points of headroom once the two pending items the report itself escalates are both applied (M1). **V2's KILL is not robust**, and the report's central claim that it is (§1.3: *"V2's KILL does not turn on how the ruler was modelled"*) is falsified by a bracket the report should have run and did not (B1).

---

## What was independently re-derived and found CORRECT

Recorded so the lead can see what is solid.

| check | result |
|---|---|
| Ruler VOLT-SUB seed 11 | re-ran `run_ruler`: 19.18537 L/100 km, 1.8977315 kWh/km — matches `results_ws11.json` per-seed exactly |
| Ruler VOLT-REG seed 23 | 18.95032 L/100 km — matches exactly |
| V1 VOLT-SUB seed 11 | 1.4139443 kWh/km — matches exactly |
| V2 VOLT-REG seed 23 | 1.7010084250276258 kWh/km — matches WS4's `series_duty_v2[nominal]` min bit-for-bit; the hot-swap seam is real |
| Anchor, re-derived from `sources/fuelly_npr_hd_all.txt` | table matches the stored page row-for-row; 179,702 mi ÷ 21,448.76 gal = **8.3782 mpg = 28.075 L/100 km**; 4HK1-era subset 7.3472 mpg = **32.014 L/100 km**; 1,044 fuel-ups. Distance-weighting is correct (miles ÷ gallons, not a mean of means). **No parameter appears to have been fitted to the corridor**: every free parameter is declared ruler-favourable with a stated direction of error, which produces a systematically lean ruler without being a fit. The claim `is_a_fit: false` is credible. |
| Gear ratios / transmission mass | `sources/as68rc_transmissionrepaircostguide.md` states 3.74/1.96/1.34/1.00/0.77/0.63, reverse 3.54, 500 lb w/ converter, 730 lb-ft max input, and explicitly identifies the AS68RC as "the A465 transmission" as fitted to the Isuzu NPR. All match `ws11_params.py` |
| Spec-sheet items | `sources/isuzucv_npr-hd_diesel_specs.txt` confirms 14,500/20,500 lb, 7,545–8,511 lb allowance, 4.555 axle, Aisin A465id lock-up 2nd–6th, 4HK1-TC 5.2 L, 215 hp @ 2,500 / 452 lb-ft @ 1,850, 140 A, 215/85R16E, WB 109/132.5/150/176 |
| Mass ledgers, to the kilogram | ruler 2985+545+90+75+5 = **3700**; V1 3700−250−500+552.32+386 = 3888.32 → **3888**; V2 3700−250+552.32+137 = 4139.32 → **4139**. Every upstream figure verified against source: WS2 `interface.mass_kg.total_kg` = 230.8; WS3 `packs.V2.mass_kg` = 280.52; WS4 `v1_genset.mass_kg` 305+48+8+25 = 386; `v2_genset` 500+90+12+35 = 637 with `aftertreatment_extra` 60. Chassis-cab: allowance at 150″ = 7,919.87 lb → 2,984.70 kg. All arithmetic closes. |
| Paired statistic (R36/D13) | 128 seed-cases re-derived from `data/per_seed_margins.csv`: every margin recomputes from its own four columns to 1.7e-6 pp; every headline min/median/max is the min/median/max **of the per-seed paired margins**, not of enveloped ratios. Pairing is genuine — `run_pair()` hands the *same* cycle object to ruler and candidate at each seed. **No ratio-of-medians artefact in any headline number.** |
| Ensembles | 8 seeds everywhere, per R9; seed sets are WS1/WS4's own |
| Three-way verbatim | interface ↔ `results` ↔ `data/headline_margins.csv` ↔ report prose agree on all four verdict-carrying numbers (+20.114012 / +19.124037 / −7.925180 / −9.978769) and on all masses |
| `verify_ws11.py` | runs clean: 396/396 asserted values verify verbatim |
| Sustained 6% capability | hand-derived: at 82.01 km/h the 6% road load at GVW is 5,767 N / 131.4 kW, and the ruler's best gear (5th, 2,062 rpm, 675.7 Nm) delivers 131.4 kW at the wheel through 0.995×0.965×0.96. **Exact.** V1 31.76 and V2 74.63 also reconcile against their genset bus powers |
| Sanity checks | 85 km/h: F = 1,987.6 N, P = 46.93 kW; top-gear rpm 1,748.7 @ 85 and 2,057.3 @ 100 — all re-derived |
| Corner physics | ρ(−10 °C) = 1.34163, ρ(2,000 m/45 °C) = 0.8706, derate 0.96×0.97 = 0.9312, WS3 acceptance at −10 °C = 66.985 kW bus — all re-derived and correct |
| Break-even curbs | V1 4,433.5 kg and V2 3,944.1 kg re-derived from the per-km margins and the payload identity — exact |
| Cold cab-heat bracket | independently reproduced: V1 cold + cab heat = **+2.640%** min / +3.532% median — matches |
| Verdict logic | both verdicts follow mechanically from the pre-committed criterion; the corner sets are correct (V1 correctly excludes the climb per R5) |

Assignment coverage is otherwise complete: ruler converter/gear/shift/idle/DFCO all stated; per-km and per-payload both on the paired statistic and labelled; all four ordered corners run; all four ordered one-factor rows run; trip-time ratio reported and the gate left to the lead; heat reported by component and case; WS4 vintage stated; seven escalations, none self-resolved.

---

# BLOCKING

## B1 — The bracket named "all ruler-favourable choices reversed" does not reverse the four largest ruler-favourable choices, and the KILL does not survive them

**What is wrong.** `ws11_params.py` declares four ruler driveline parameters as RULER-FAVOURABLE, each with an explicit statement of how far the true value lies:

- `ETA_GEAR = (0.960, 0.965, 0.970, 0.985, 0.965, 0.960)` — *"at the generous end of published MD planetary-AT figures"*
- `PUMP_KW_AT_1800 = 1.2` — *"a real A465 pump at line pressure is 1.5-2.5 kW at 1,800 rpm"*
- `ETA_FINAL = 0.96` — declared as the favourable share of WS1's ratified 0.95
- `LOCKUP_SLIP_LOSS = 0.005` — *"0.5% is at the optimistic end"*

**None of the four appears in `BRACKETS`** (`run_ws11.py` ~line 855). The bracket set reverses only accessories, neutral idle, CdA, shift schedule and rotating inertia. The row exported as `all_ruler_favourable_choices_reversed`, and reported in §1.3 as *"all of the above at once"*, therefore does not reverse all ruler-favourable choices — it omits the four that dominate a highway duty, and it substitutes CdA 5.4, which the report's own prose says is *"a change to the ROAD … not a ruler modelling choice."*

**Evidence (re-run, 8 seeds, VOLT-REG, candidate untouched):**

| ruler setting | ruler L/100 km (median) | V2 per-payload margin, ensemble-min |
|---|---|---|
| headline (as delivered) | 19.033 | **−7.925%** |
| gear mesh −2 pts → (0.940…0.970) | 19.353 | −6.079% |
| AT pump 2.0 kW @1,800 (midpoint of the file's own stated real range) | 19.235 | −6.779% |
| final drive 0.94 instead of 0.96 | 19.355 | −6.064% |
| lock-up slip debit 2.0% instead of 0.5% | 19.265 | −6.582% |
| **all four driveline levers together** | **20.135** | **−1.877%** |
| **those four + physical accessories + idle-in-Drive** | **20.497** | **−0.083% min / +0.389% median** |

For contrast, the report's own `all_ruler_favourable_choices_reversed` row with the road change removed (the honest form of that row) gives ruler 19.422 L/100 km and V2 −5.755% — the ~2 pp the report's bracket set is capable of moving.

**Why it is blocking.** V2's KILL is put to the lead as a decision to execute. The report's stated basis for its robustness is §1.3: *"The most V2-favourable single bracket in the table is the belt/alternator accessory model, and it leaves V2 at -6.91% … **V2's KILL does not turn on how the ruler was modelled.**"* That sentence is false. Six ruler-modelling levers, every one of them set to a value the workstream's own parameter file declares to be inside the plausible range and merely at the optimistic end, take V2 from a 7.9-point KILL to a **draw** (−0.08% ensemble-min, +0.39% median). V1 is unaffected and moves the other way (+20.11% → **+36.84%**), which confirms the lower-bound framing works for the ADVANCE and only for the ADVANCE.

**What would resolve it.** Add the four driveline levers to `BRACKETS`; rename the combined row so it excludes the CdA road change; export a genuine "all ruler-modelling choices at their pessimistic declared end" row for both duties and both vehicles; and restate §1.3's robustness claim against that row. If the lead still wishes to execute the KILL, it should do so on the record that the KILL survives only the ruler as modelled at its most favourable settings, not the ruler as bounded by its own declared parameter ranges. Individual lever contributions are given above so any single lever the lead disputes can be discounted; dropping the lock-up lever entirely still leaves V2 within ~1.2 points of a draw.

---

## B2 — The R38 trip-time model never enforces steady-state capability; it limits acceleration only. The exported settled-climb speeds are physically impossible and contradict the same results file

**What is wrong.** In `ws11_capability.py`, `_loop()`:

```python
a_cap = (f_av - f_res) / (lam * m)
a_des = (v_tgt - v) / dt
if a_des > 0.0:
    if a_des <= a_cap:
        a = a_des
    else:
        a = a_cap
        n_limited += 1
else:
    a = a_des
```

The capability limit `a_cap` is consulted **only when the vehicle is trying to accelerate**. Once the vehicle is tracking the demanded speed (`a_des == 0`), the `else` branch holds that speed regardless of how negative `a_cap` is. On a sustained grade the vehicle therefore never slows down, no matter how far the demand exceeds its capability.

**Evidence (instrumented replay of the climb corner, seed 23):**

- Climb insert: 10 km at 6%, demanded speed **94.95 km/h**, 3,791 samples.
- At that speed on 6%: ruler force available **5,229.1 N**, road load **6,212.5 N**, deficit **−983.4 N**, `a_cap = −0.1433 m/s²`.
- `a_cap < 0` on **3,752 of the 3,791** inserted samples.
- Actual speed through the whole insert: **min 94.95, max 94.95 km/h.** The ruler never slows by one decimal place.
- Consequence: `ruler_distance_shortfall_m` on the climb corner is 121 m (median) — barely more than the 116 m on the *unmodified* cycle. The 10 km climb is essentially invisible to the export.
- `ruler_settled_speed_on_6pct_kmh` is **identical (88.226 / 88.401 / 89.321)** between `V2_on_VOLT-REG[nominal]` and `V2_on_VOLT-REG[climb_10km_6pct]`. It is not a settled speed at all — it is the minimum *demanded* speed on any grade ≥ 5.5% anywhere in the cycle.

**Internal contradiction.** `results_ws11.json` exports both:
- `trip_time_r38["V2_on_VOLT-REG[climb_10km_6pct]"].ruler_settled_speed_on_6pct_kmh = 88.40`, `candidate_settled_speed_on_6pct_kmh = 94.33`
- `sustained_6pct_capability_kmh = {ruler: 82.01, V2: 74.63}`

Both are steady speeds on a 6% grade at GVW. They cannot both be true. The second is correct (I re-derived 82.01 km/h by hand to three figures); the first is an artefact of the defect.

**Corrected re-run.** Enforcing capability on every sample (`a = min(a_des, a_cap)`), 8 seeds, climb corner:

| | as delivered | capability enforced |
|---|---|---|
| ruler trip time, median | 6,963.13 s | **7,029.65 s** |
| V2 trip time, median | 6,963.39 s | **7,026.81 s** |
| ratio worst | 1.00044 (+0.044%) | **0.99985 (−0.015%)** |
| settled speed on the 6% climb, ruler | 88.40 km/h | **82.01 km/h** (matches `sustained_6pct_capability_kmh` exactly) |
| settled speed on the 6% climb, V2 | 94.33 km/h | **74.93 km/h** (matches 74.63) |
| R38 gate ≤ +5% | PASS | **PASS** |

**Verdict impact: none.** The gate outcome is unchanged for all three exported rows, and V1's ADVANCE is judged on a flat 50 km/h duty where neither vehicle is capability-limited at all (zero shortfall for both, ratio exactly 1.000000).

**Why it is blocking anyway.** R38 is a hard ADVANCE requirement that **the lead applies from this exported table**, and the table is produced by a model that does not do what its own docstring says (*"the vehicle tracks it exactly wherever capability allows; where it does not, the vehicle falls behind"*). Two fields in one results file contradict each other. And the report builds substantive narrative on it — §6's *"V2 passes the 10 km climb because its buffer lasts almost exactly 10 km"* describes a mechanism the trip-time pass never exercises: in that pass V2 never needs the buffer, because the pass never asks it to hold a speed it cannot hold. This is the WS8-B1 severity precedent (a wrong control/physics law in an exported artefact, verdicts unaffected).

**What would resolve it.** Apply `a = min(a_des, a_cap)` unconditionally; re-export all three trip-time rows and the settled-climb speeds; assert in `verify_ws11.py` that `settled_speed_on_sustained_climb_kmh` agrees with `sustained_6pct_capability_kmh` on any corner carrying a sustained 6% grade; and restate §6.

---

## B3 — The ruler is 32–40% below its own mandatory anchor; V2's KILL flips at +7%, and that flip point is neither computed nor exported

**What is wrong.** The assignment ordered: *"Calibrate to a public NPR fuel-economy reference and state it … a sourced anchor is mandatory, a fit to the corridor is not."* WS11 obtained an anchor and did not calibrate to it. The delivered ruler reads **19.177 L/100 km** on VOLT-SUB against a distance-weighted in-use anchor of **28.075** (all years, −31.69%) and **32.014** for the 4HK1-era subset that actually corresponds to the modelled engine (**−40.10%**). Even with every bracket the report runs, the ruler reaches only 24.20 L/100 km (−13.8%), and with the road change removed only 23.47.

The report's defence is that the residual is *"in the ruler's favour … so every candidate margin in this report is a lower bound."* That is true and sufficient for V1's ADVANCE. **It is the wrong guarantee for a KILL**, and the report says so once (§1.3) and then argues robustness from single-lever brackets instead of from the flip point.

**Evidence — the flip point, computed from the committed per-seed data (candidate held fixed, ruler per-km fuel scaled by k):**

| target | k, ensemble range | ruler VOLT-REG L/100 km |
|---|---|---|
| V2 per-payload margin = 0% (draw) | **1.0693 – 1.0793** | **20.35 – 20.54** |
| V2 per-payload margin = +3% (ADVANCE) | **1.1024 – 1.1126** | **20.98 – 21.18** |
| V2 climb corner = 0% | 1.0927 – 1.0998 | — |
| V2 cold corner = 0% | 1.0817 – 1.0877 | — |
| V1 falls to +3% (ADVANCE lost) | **0.8131 – 0.8236** | ruler would have to be **18% leaner** |

So: **V2's KILL requires only that the ruler not be more than ~7% thirstier than modelled.** The ruler's own mandatory anchor says the real fleet is 46% thirstier (all-years) or 67% thirstier (era-correct subset). B1 shows that the workstream's own declared parameter ranges are enough to close the 7%.

**The asymmetry in what is exported.** `results_ws11.json` exports `break_even_curb_kg` — the mass flip point, which *supports* the KILL (V2 is 195 kg over). It exports no equivalent for the ruler's fuel level — the flip point that *threatens* it. A lead reading the interface block sees a hard KILL and a hard 195 kg overshoot, and nothing telling it the whole result turns on a 7% error in an unvalidated absolute.

**A further point on the anchor's own reading.** §1.2 presents the era note as a caveat weakening the anchor (*"MY2002 … carries 56% of the tracked miles"*). But MY2002 reads **9.4 mpg — the *best* row on the page**. Removing it makes the anchor *worse* for the model, not better: the era-correct subset is 32.014 L/100 km. ESC-1 states this honestly; §1.2's framing does not, and the interface exports only the milder residual (see M5).

**Why it is blocking.** A KILL is an irreversible program decision. ESC-1 correctly escalates the calibration gap, but an escalation does not make a number usable, and the report affirmatively claims a robustness it has not tested. The lead cannot weigh the KILL without the flip point.

**What would resolve it.** Compute and export, as first-class R14 fields, the ruler-fuel multiplier at which each candidate's per-payload margin reaches 0% and the 3% bar, on the paired per-seed statistic with the governing seed labelled — the exact analogue of `break_even_curb_kg`. State the anchor residual against both members of the anchor set. Restate §1.2's era note so it reads in the direction the data actually points. Either satisfy the assignment's "calibrate" order or record explicitly that it was not satisfied and that the KILL is being executed on an uncalibrated ruler.

---

# MATERIAL

## M1 — V1's ADVANCE has 1.05 points of headroom at its binding corner once both of the report's own pending items are applied, and the combination is never run

`cold_-10C` is V1's governing corner (+19.124%). Two open items each move it, and the report reports them only separately:

| V1, cold_−10 °C | ensemble-min | median |
|---|---|---|
| as ordered (CdA 4.2, no cab heat) — **the gated number** | **+19.124%** | +19.808% |
| + R30 cab-heat member (ESC-2) | **+2.640%** | +3.532% |
| + CdA 5.4 (ESC-4 / E13) instead | **+16.561%** | +17.152% |
| **+ both** (re-run by this adjudication) | **+1.054%** | +2.262% |

Both are live: ESC-2 asks the lead to rule whether R30 extends to Vehicle Zero, and ESC-4 asks for the WS7 coastdown *"before any Vehicle Zero efficiency claim is ratified"*. If R30 extends and the coastdown lands anywhere near CdA 5.4, V1's ADVANCE clears the ≥0% corner bar by one point. The report gives +2.64% and +18.06% in separate places and never the combination; `interface_ws11` exports only +19.124037.

**Resolve:** run and export the combined corner; state in §7 that V1's ADVANCE is conditional on ESC-2 and ESC-4 with the combined figure named.

## M2 — R14's pending-ruling requirement is not honoured anywhere in the interface block

R14: *"Fields conditioned on a pending ruling carry the ruling ID."* The string `ESC` does not appear anywhere in `interface_ws11`. At least four exported fields are conditioned on pending rulings:

- `verdicts.V1_on_VOLT-SUB.worst_corner_margin_pct` ← ESC-2 (moves 19.12 → 2.64, or → 1.05 with M1)
- `masses.*.V2` and every V2 margin ← ESC-3 (aftertreatment; the bracket value is exported but carries no ruling ID)
- both payload corners in `verdicts.*.corner_margins_pct_min` ← ESC-7
- `ruler.l_per_100km_*` and every margin ← ESC-1 and ESC-4

`cold_cab_heat_bracket` exists in `results_ws11.json` but is not reachable from the interface block at all. A downstream consumer reading only the interface gets unconditioned numbers.

## M3 — No capability or limit diagnostics are exported, and the V2 numbers of record are produced by runs that exceed the ratified continuous rating and empty the pack

`grep` of `results_ws11.json` returns **zero** occurrences of `unserved`, `soc_min`, `emerg_s`, `eng_over_cont`, `above_pin`, `over_rating`, `pack_chg_above_r16`, `starts`, `infeasible`. WS4's simulator computes every one of them and WS11 discards them all. Re-running the candidate and ruler and reading those counters (worst over seeds 23 and 5 for VOLT-REG, 11 and 4 for VOLT-SUB):

| case | V2 unserved kWh | V2 SOC min | V2 emergency-band s | V2 above 132 kW cont. s | ruler unserved kWh | ruler infeasible s |
|---|---|---|---|---|---|---|
| **nominal** (the headline −7.93%) | 0 | 0.228 | **405.0** | **146.5** | **0.371** | **174.3** |
| payload_p20 | 0 | 0.173 | 461.8 | 180.4 | 0.658 | 192.7 |
| payload_m20 | 0 | 0.265 | 0 | 0 | 0.171 | 143.3 |
| cold_−10 °C | 0 | 0.250 | 287.2 | 12.1 | 0.541 | 190.6 |
| alt2000m_45C | 0 | 0.247 | 210.5 | 66.1 | 0.294 | 157.8 |
| **climb_10km_6pct** (the governing corner, −9.98%) | **1.720** | **0.000** | **847.1** | **616.8** | **3.258** | **553.5** |
| V1, all five cases | 0 | ≥0.408 | 0 | 0 | 0 | 0 |

Three facts the report does not state:

1. **V2 exceeds its R18-ratified 132 kW continuous flat-rating in four of six cases, including the nominal case that produces the headline number.** The emergency band's ceiling is the *automotive* full-load curve (≈148.7 kW for ENG_V2) — WS4's own KX-M1 issue. WS4 ships an `emerg_cap_cont_rating=True` bracket for exactly this and WS11 never exercises it.
2. **On the governing climb corner V2's pack reaches SOC 0 with 1.72 kWh of unserved bus energy.** §6's *"V2 passes the 10 km climb because its buffer lasts almost exactly 10 km"* is not what the model shows: the buffer is exhausted and the emergency band carries the remainder.
3. **The ruler is capability-infeasible on every VOLT-REG case** (143–553 s), with its shortfall charged to fuel at its own cycle-mean BSFC. On the climb corner that correction is 2.9% of the ruler's fuel.

Direction of all three is *toward* the candidate (they make the ruler thirstier and let V2 deliver more energy at good BSFC), so none changes the KILL. But they are undisclosed, and they mean the exported V2 numbers are not achievable inside V2's own ratified rating.

**Resolve:** export the WS4 counters per case; state in §3.2 and §5 that the V2 result of record involves operation above the R18 continuous rating and, on the climb corner, pack exhaustion; run WS4's `emerg_cap_cont_rating` bracket.

## M4 — A machine-readable note asserts something the data contradicts, and the prose gets it right

`results_ws11.json → ruler_bracket_effect_on_margin.note`:

> *"…every other row raises the candidate's margin, which is what 'lower bound' means."*

False for `CdA_5.4` on **both** vehicles: V1 +20.114 → **+18.060**, V2 −7.925 → **−10.525** (`data/bracket_margins.csv`). §1.3's prose handles the CdA row correctly (*"moves V2 the other way … a change to the ROAD"*). The JSON note does not. This is the exact class the mandate names: the interface asserting something the prose describes correctly.

## M5 — The interface exports the milder member of the enumerated anchor set, and no bracket range at all

`interface_ws11.ruler.anchor` exports `distance_weighted_l_per_100km: 28.075` and `residual_vs_model_pct: −31.69` — the **all-years** anchor. The 4HK1-era subset (32.014 L/100 km, residual **−40.10%**) is the era-correct member for the modelled engine; it appears in `ruler_calibration` and `data/ruler_anchor.csv` and in ESC-1, but not in the interface. Under R14 a worst-case field is an explicit max/min over an enumerated set with the governing case labelled; the anchor set has two members and the interface exports the one that flatters the model.

Separately, `interface_ws11.ruler.l_per_100km_VOLT_SUB` / `_VOLT_REG` carry only the ruler-favourable bracket. Given B1 and B3, the interface should carry the bracket range and the governing setting.

## M6 — The one-factor rows are a statistic-of-statistics, and one row's stated meaning is wrong

**(a) Not paired.** Every `worth_pp` is `base["min"] − counterfactual["min"]` — a min-of-A minus min-of-B, governed by **different seeds**:

| row | base min seed | counterfactual min seed | reported pp | paired per-seed min / median / max | error vs paired min |
|---|---|---|---|---|---|
| V1 regen | 4 | 8 | 24.023 | 23.589 / 23.810 / 25.038 | 0.434 |
| V1 start-stop (b′) | 4 | 9 | 74.883 | 72.585 / 74.385 / 75.655 | 2.298 |
| V1 operating point | 4 | 4 | 11.407 | 11.152 / 11.359 / 11.475 | 0.254 |
| V1 start-stop (pinned) | 4 | 9 | 103.837 | 101.797 / 102.640 / 104.609 | 2.041 |
| V2 regen | 5 | 8 | 4.375 | 4.320 / 4.901 / 5.143 | 0.055 |
| V2 start-stop (b′) | 5 | 9 | 0.313 | 0.250 / 0.899 / 1.009 | 0.062 |
| V2 operating point | 5 | 5 | 12.588 | 12.341 / 12.491 / 12.598 | 0.246 |
| V2 start-stop (pinned) | 5 | 23 | 65.748 | 63.420 / 64.677 / 66.740 | 2.328 |

This is the R36 defect class in miniature. Magnitudes are 0.06–2.33 pp and nothing load-bearing turns on them, but §4 presents these as the decomposition of a paired statistic. The `mass_payload_denominator` row is correct (the two mins share a seed by monotonicity).

**(b) The engine-operating-point row's description is wrong.** The counterfactual is `fuel_alt_g = ru["eng_kwh"] * pin_bsfc + ru["unserved_fuel_g"]`. `eng_kwh` includes the ruler's **idle** shaft work, so the counterfactual re-prices idle fuel (≈500 g/kWh at 700 rpm) at the candidate's island BSFC (228.72 / 203.62 g/kWh). The exported description says *"What survives is everything that is not the operating point — driveline, regen, **idle** and the payload denominator."* Idle does not survive; it is absorbed into this row. On VOLT-SUB idle is 13.7% of the ruler's fuel, so the row conflates two of §4's four mechanisms.

## M7 — The payload corners as gated depart from WS8/WS9 precedent, and ESC-7 does not say so

`WS8_semi_architecture/ws8_candidates.py`:

```python
def payload_kg(self):
    p = VEH.m_gcw - self.tare_common_kg() - self.powertrain_mass_kg()
    return p * self.ctx.payload_factor
```

WS8 — and WS9 after it, under the R28/ESC-3 corner set the assignment mirrors — scales **each vehicle's own** payload. That is precisely WS11's `payload_p20_own` / `payload_m20_own`, which WS11 exports as a *"VARIANT READING, not in the gate"*. WS11 gated on the literal reading, which puts identical freight on both vehicles, cancels the denominators, and turns the per-payload metric into the per-km metric at two of the four corners.

ESC-7 identifies the symptom correctly and states plainly that nothing turns on it tonight (true — V2 fails at nominal, V1 passes under both readings). But it characterises the issue as the assignment's wording, when the ordered reading is also a **departure from the convention the program has been running**, and it does not cite WS8's implementation. Meanwhile `interface_ws11.verdicts.V2_on_VOLT-REG.corner_margins_pct_min` exports `payload_p20: +6.27, payload_m20: +7.21`, which reads on its face as V2 winning at those corners.

**Resolve:** ESC-7 should cite WS8's `payload_kg()` and R28/ESC-3 as the precedent, and say which reading is the novel one.

## M8 — The stop-start thermal asymmetry is dismissed on reasoning that does not address it

§10.1: *"no cold-engine friction/warm-up model on either vehicle — **roughly neutral** — the ruler and V2 share an engine; V1's is smaller and would warm faster."*

That reasoning addresses initial cold start. The asymmetry that matters is duty-cycle thermal cycling: on VOLT-SUB V1's genset is **off ~69% of the time in 2–3 blocks** (measured: `eng_on_frac` 0.314, `starts` 2 per 58-minute cycle, i.e. off-blocks averaging ~20 minutes), while the ruler's engine runs continuously and stays hot. WS4's `fmep_bar()` is a function of rpm only and is documented as a *"warm engine"* model, so the simulator **cannot express** the penalty; `START_FUEL_G = 12.0` covers a load-acceptance ramp, not a thermal state. The omission systematically flatters the single mechanism V1's ADVANCE rests on (§4 attributes 74.88 pp to engine-off), and it is larger at the −10 °C corner, which is V1's binding corner.

I cannot quantify it without a thermal model. The finding is that it is not "roughly neutral" and the stated justification does not support the classification.

---

# MINOR

**m1 — The report's opening claim overstates the verification.** *"Everything below is generated from `results_ws11.json`; `verify_ws11.py` asserts every number in this file against it."* 396 values are asserted; **105 distinct numeric tokens in the report are outside the assertion set.** Most are section numbers and quoted parameters, but several are substantive and have no JSON home at all: the "44%-idle duty" (measured 44.70%), "braking is 5.9% of tractive energy" (measured 5.898%), WS1's 30.2 km/h, WS2's 1.45 kW blower, WS4's ≤0.0004 pp. Others (230.8 / 280.5 / 386 / 637 / 60.0 kg, 7,920 lb, 195 kg, 82.0 / 74.6 km/h) exist in the JSON but were typed into prose at a different precision. The headline numbers do verify verbatim; the sentence should be narrowed to that.

**m2 — §2.2 / ESC-3 arithmetic.** *"60 kg is 2.4% of V2's payload and therefore 2.4 points of the metric of record."* 60/2,461 = 2.44%, but the metric moves from −7.925% to −10.622%, i.e. **2.70 pp**.

**m3 — §1.1's engine-curve claim is asserted, not run — but it is true.** *"Both effects are inside the brackets in §1.3"* — no bracket varies the engine curve. I built the sourced 2023 curve (612.8 Nm plateau, 160.4 kW peak) and a uniformly-scaled variant and re-ran both duties: the ruler moves **+0.2% to +0.4%** and the margins by **<0.6 pp** (V2 −7.925 → −7.827 / −7.353; V1 +20.114 → +20.086 / +20.077). The claim stands; it should carry the run.

**m4 — ESC-5 mis-cites its ruling.** It cites *"R9 (ensembles)"*; R9 is the ensembles / part-load / 10 Hz / heat-ledger ruling. The convention actually challenged is Gate G1's net-energy demand-trace convention (BASELINE_v1), which ESC-5 also names. Drop the R9 citation.

**m5 — The idle fuel rate is never stated.** The assignment orders *"idle fuel modelled"*. The model gives **0.2778 g/s = 1.202 L/h** at 700 rpm carrying 2.0 kW, which is **13.68% of the ruler's VOLT-SUB fuel** across 44.70% of the cycle time. A reviewer cannot sanity-check the ruler's single most consequential number on a stop-start duty without running the code.

**m6 — R34 partial compliance.** The assignment says *"export a 10 Hz trace file per run."* Seven traces were exported against ~270 runs, declared and justified by WS4 precedent. Notably **neither candidate's governing corner is traced** — there is no trace at V1's `cold_-10C`, which decides its ADVANCE. Traces themselves are correct: 10 Hz, correct columns, R12-labelled headers.

**m7 — Heat ledger hands WS6 a weaker product than upstream already computes.** `data/heat_ledger_ws6.csv` exports `mean_kW_over_cycle_max` — a cycle mean, the statistic WS4's own KX-m7 finding says *"a cooling owner sizes against a window, not against a cycle mean."* WS4 already computes `eng_reject_peak_kw` and `eng_reject_roll120s_max_kw` / `roll600s` on every one of these runs and WS11 discards them. Also: the brake resistor is lumped with friction in "R15 blend overflow (resistor + friction)" though WS6 owns the resistor's 50 kW as a separate sizing case; and the ruler's engine rejection is not split into exhaust / coolant / CAC (WS4's `engine_energy_split` exists). Ruler rows on VOLT-SUB are duplicated (once under each candidate pass). Coverage of cases is complete (112 rows, every vehicle × duty × case).

**m8 — Undeclared derated-load-fraction asymmetry at the altitude corner.** WS4's `_bsfc_fast(engine, rpm, trq, tmax)` is passed the **derated** full-load torque, so the candidate's load fraction φ (and hence the smoke-limit term) is referenced to the derated curve. `ws11_ruler.py` calls `engine.bsfc(n, t)`, which computes φ against the **underated** curve. At `alt2000m_45C` the two vehicles are therefore on different conventions. Quantified by re-running the ruler on a pre-derated curve: ruler 16.380 → 16.397 L/100 km, V2 margin −3.521% → −3.408%, i.e. **0.11 pp**. Immaterial, but undeclared, and it favours the ruler.

**m9 — Unpinned, unused, unmentioned sources.** `sources/isuzu_za_NPR400_spec_sheet.pdf` and `.txt` sit in `sources/`, are not in `_meta.input_sha256`, are not referenced in any code, and are not mentioned in the report. The ZA sheet carries a *sourced* NPR chassis-cab tare of **2,620 kg** (7.5 t GVM, manual box) — a data point directly relevant to §2.1's derived 2,985 kg that the report neither uses nor dismisses. `sources/isuzucv_npr-hd_diesel_specs.txt` (the extraction a reader actually reads) is also unpinned; only the PDF is.

**m10 — The chassis-cab line is labelled [SOURCED] but is an interpolation, and the 545 kg body is a residual by construction.** The spec sheet publishes a *range* (7,545–8,511 lb) across four wheelbases without saying which end belongs to which; `ws11_params.py` assumes it falls linearly with wheelbase (physically right) and interpolates to 150″. The 545 kg body is then defined as whatever closes to WS1's `m_curb_operating`, which is itself marked `[WS1-ASSUMPTION]` in `volt_params.py`, not sourced. **I checked whether this matters and it does not:** ±100 kg of body mass moves V2's margin by ~±0.65 pp and V1's by ~±0.3 pp, and 545 kg (1,202 lb) sits inside the published range for a 16 ft aluminium dry-freight body with subframe and rear door. The report declares the item honestly. Recorded so the lead has the sensitivity, and so the "[SOURCED]" tag on an interpolated figure is on the record.

**m11 — The cab-heat bracket smears the load.** `aux = 2.0 + 3.0 * (1 - eng_on_frac)` applies a cycle-average adder for the whole run rather than switching 3.0 kW on during the actual engine-off samples, and `eng_on_frac` is taken from the base run without iterating (the added load itself changes it). Total energy is right; the timing is not, and the exported description (*"electric at the bus otherwise"*) implies a time-resolved treatment.

**m12 — The climb splice point is an unbracketed WS11 choice that sets the corner's severity.** Splicing at 30% of route distance fixes the demanded climb speed at **94.95 km/h**, needing ~164 kW at the wheel. WS1 §4.4 — the case the assignment names — poses the climb at **85 km/h** and states that *"holding 85 km/h up a 10 km 6% grade is not achievable on any buffer."* WS11's corner is therefore materially harder than its own reference, which is why both vehicles run off their capability curves in it (M3). Declared in `climb_insert`, but not bracketed and not compared to WS1's own posing.

**m13 — Dead code.** In `ws11_ruler.py`, `coupled` requires a gear with `n_e_lock >= N_LUG_MIN_RPM (1100)`, and `dfco = coupled & (n_b >= N_DFCO_RPM (1000))` is therefore always true wherever `coupled` is. The `coupled_fuelled` branch (`f_cf`, `t_cf`, `p_cf`) can never execute.

---

# Escalations — characterisation review

I judge characterisation only. I rule on nothing.

| ESC | cites | correctly characterised? | not self-resolved? |
|---|---|---|---|
| ESC-1 anchor is in-use, cannot calibrate a cycle | the assignment's anchor requirement | **Partly.** The facts are stated honestly, including the 32.01 era subset. But it does not tell the lead the *consequence*: that V2's KILL flips at +7% of ruler fuel (B3). An escalation that omits the sensitivity understates its own stakes. | Yes |
| ESC-2 cold corner does not charge cab heat | R30 / D19 | **Yes**, and correctly directed (the reading taken for the gate is the one favourable to the candidate). Understates the exposure: the combined cab-heat + CdA case leaves V1 at +1.05% (M1). | Yes |
| ESC-3 `aftertreatment_extra` ambiguity | WS4 `interface_ws4.v2_genset.mass_kg` | **Yes.** Correct direction (excluding 60 kg is favourable to the candidate, i.e. conservative for a KILL). Arithmetic slip at m2. | Yes |
| ESC-4 CdA 4.2 is provisional | BASELINE_v1 vehicle parameters | **Yes**, and correctly directed (a bigger CdA moves the comparison against the candidates). | Yes |
| ESC-5 the metric cannot see time | *"R9 (ensembles)"* + the G1 demand-trace convention | **Substance correct, citation wrong** (m4). And undermined by B2: the capability pass it offers as the remedy does not enforce steady-state capability, so the sustained-climb numbers it points the lead at are wrong in the export. | Yes |
| ESC-6 the answer is duty-indexed | R32's framing | **Yes.** Well posed. | Yes |
| ESC-7 payload corners erase the metric's penalty | the assignment's corner definition | **Partly** — see M7. Correct symptom, correct conclusion that nothing turns on it tonight, but it does not cite the WS8/WS9 precedent or say that the *gated* reading is the departure. | Yes |

None is self-resolved. Where a reading had to be chosen to run, the choice is stated, the alternative is exported, and a ruling is requested — that is correct practice.

---

# Summary for the lead

- **V1 Postal ADVANCE on VOLT-SUB: sound as a lower bound, conditional in one place.** Every headline number re-derives. The lower-bound framing is real and works in V1's favour: with the ruler at its most pessimistic defensible settings V1 goes to +36.84%. Its exposure is not the ruler — it is that its **binding corner falls to +1.05%** once both of its own escalated pending items apply (M1), and that the mechanism carrying the margin (engine-off, 74.9 pp) has an unmodelled thermal asymmetry dismissed on the wrong grounds (M8).
- **V2 Trucker KILL on VOLT-REG: not established at the confidence claimed.** The report's robustness claim is falsified — six ruler-modelling levers, all inside the workstream's own declared ranges, take V2 to a **draw** (B1). The flip point is +6.9–7.9% of ruler fuel and is neither computed nor exported, while the ruler sits 32–40% below its own mandatory anchor (B3). Separately, the V2 numbers of record are produced by runs that exceed the R18 continuous rating and, at the governing corner, empty the pack — none of it exported (M3).
- **The R38 trip-time export is wrong** (B2): it limits acceleration only, never steady-state capability, and its settled-climb speeds contradict the capability numbers in the same file. The gate outcome does not change; the export cannot be relied on.
- The machine-readable interface verifies verbatim against the data file and the prose on every headline number, and the paired statistic is genuinely paired throughout. **R36's defect class does not appear in any headline number**; it does appear in the one-factor decomposition (M6) and in one false JSON note (M4).

Round 1 is **NOT CLEAN**. Findings on disk; no work product was altered and nothing was committed.
