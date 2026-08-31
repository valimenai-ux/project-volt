# FINDINGS — WS9 PRE-ADJUDICATION, ROUND 1

**THIS IS NOT THE ADJUDICATION OF RECORD FOR WS9.** BASELINE_v5 R37 designates WS9's adjudication as the lead's Fable seat (`WS9_vehicle_one_wave2/ADJUDICATION_DIRECTIVE.md`), and that round has not been run. This file was produced under `NIGHT_SHIFT.md` step A4 as a pre-adjudication pass, by an Opus ws-adjudicator with no history of the work, reading artifacts on disk only. **Nothing here disposes of anything.** No finding is settled, no verdict is read, no escalation is ruled on, and R38's trip-time gate is NOT applied — R38 reserves it to the lead and this round respects that. Where a finding touches one of the ADJUDICATION_DIRECTIVE's nine designated questions, it is flagged for the Fable round rather than answered on its behalf.

- Artifact under review: WS9 as committed at `827c16a` ("WS9 r3-concordant re-run"). `git status` shows WS9 clean in the working tree; nothing in this review edited any WS9 file.
- Baselines read in full: `BASELINE_v5.md` (of record) and `BASELINE_v4.md` (what WS9 was built under). Also read: `ASSIGNMENT.md`, `ADJUDICATION_DIRECTIVE.md`, `CHANGELOG_WS9_r3.md`, `REPORT_WS9.md`, `results_ws9.json`, every `data/*.csv`, and every `ws9_*.py` / `run_ws9.py` / `verify_ws9.py` / `check_determinism_ws9.py`.
- WS8 was read strictly read-only. All mutation testing was done on a throwaway copy of WS8 and WS9 in a scratch directory; the repository copies were never modified.

**RESULT: NOT CLEAN. Four blocking, six material, nine minor.**

---

## What I re-derived independently, and what reproduced

| # | quantity | method | result |
|---|---|---|---|
| 1 | all 60 design- and control-duty margins (5 candidates x 6 corners x 2 duties), per-seed and ensemble min/median | recomputed `(S0R - cand)/S0R` from the raw `MJ_primary_per_payload_tkm` per-seed values in `results_ws9.json`, paired by seed | **exact match, 0 of 60 mismatches** to 1e-9; the five headline ensemble-mins (S4p +11.954, S5 +1.903, S5-13L +5.359, S6 +7.502, S7 +4.509) and every worst corner reproduce |
| 2 | the five verdicts | re-applied the pre-committed criteria (`>=3%` nominal ensemble-min on GH-REG-165, `>=0%` every corner) to my own margins | **all five reproduce** (S4p/S5-13L/S6/S7 ADVANCE, S5 KILL) |
| 3 | all four exported trip-time statistics, every (candidate, corner, duty) | recomputed from per-seed `duration_s` against the ruler's same-seed `duration_s` | **exact match on all 72 cases** for median-of-medians, paired min, paired median, paired max; candidate and ruler distances agree to 3e-6 %, so the ratio is a clean time ratio |
| 4 | S4' grid-factor flip point | recomputed `margins_grid_hi` from per-seed `MJ_primary_per_payload_tkm_grid_hi` | **-0.38094%** at +50%, exactly as exported; every other candidate is grid-invariant (`grid_kWh = 0`) |
| 5 | S6 break-even peak BTE | closed form from the medians: `x = m_S6 * 0.492 / (m_S0R * 0.97)` | **0.469155**, against the exported `at_median` value of **0.469155**; the min-basis 0.468776 and the 2.32 pp headroom against the cited 0.492 are confirmed |
| 6 | the metric itself | `e_primary_MJ / (payload_t * distance_km)` from first principles for a sample run | reproduces to the last printed digit; `e_primary_fuel_MJ = e_tank_MJ * 1.19` exact; fuel LHV closes at 42.80 MJ/kg |
| 7 | ETC gate | `net_margin_pct` ensemble-min 1.6673 vs the 2.5% gate | reproduces; DROPPED is correct |
| 8 | mass ledgers | summed every candidate's rows and checked `36300 - tare - powertrain = PAYLOAD` | close to the kilogram for all six; S6 is mass-neutral with S0R at exactly 0 kg delta |
| 9 | three-way interface identity | parsed the JSON block out of REPORT §15 and compared object-wise **and byte-wise** against `results_ws9.json.interface_ws9` | **byte-identical**; `trip_time_r38.csv`, `margins.csv` and `heat_ledger_ws6.csv` agree with the JSON |
| 10 | `verify_ws9.py` | ran it | **593 checks PASS** (563 assertions + 30 pin hashes), reproducing the foreman's gate |
| 11 | determinism, beyond the committed check | re-simulated **5** (corner, candidate) jobs x 8 seeds x 2 duties from scratch in a clean sandbox and compared **every scalar field** of the per-seed record, not the committed checker's 10 | **9,051 scalar values, 0 real mismatches.** The only differences are `NaN` re-read as `null` (`top_gear_fraction`, `mean_bsfc_g_per_kWh`), a JSON serialisation artifact |

On the A3 worker's disclosed conduct deviation (mid-flight `_measure_pack` and artifact-scanner corrections, then a `--from-checkpoint` rebuild): **the claim holds as far as I could test it.** `_measure_pack` lives in `ws9_concordance.py` and reads `R["trial"]`, so it is a derived block that `--from-checkpoint` genuinely regenerates. And my re-simulation above compared the full per-seed record **including every `pack_thermal` field** — which the committed checker's `COMPARE_KEYS` does not — across five jobs and four corners, and found no drift. A checkpoint/fresh-run disagreement of the kind the foreman was right to worry about did not occur in anything I could reach.

---

# BLOCKING

## PRE-B1 — The concordance's trip-wire cannot fire on two thirds of its fields, and one hard-coded verdict demonstrably suppresses a real extracted difference

**Severity: BLOCKING.** This is ADJUDICATION_DIRECTIVE item 8's subject matter, so the Fable round rules; but the machinery is testable now and it does not do what the artifact says it does.

**What is wrong.** `ws9_concordance.py`'s docstring states: *"Nothing in this module asserts agreement; it measures it."* REPORT §12.2 repeats it: *"every verdict is computed by comparing the two extractions - nothing here is a hand-written concordance claim, which is the defect WS8's own r2 and r3 adjudications found three times."* Of the 15 fields across the three implementations, only **5** are two-sided comparisons capable of returning `DIFFERS`:

| category | fields | count |
|---|---|---|
| genuine computed WS8-vs-WS9 comparison (can fire) | `eta_sanity_bounds`, `corrected_fuel_formula`, `kWh_to_grams_conversion`, `correction_share_of_fuel`, `cold_factor_interpolation_breakpoints_C` | 5 |
| **verdict is a hard-coded string literal** — no extraction can change it | `charged_only_when_geared_and_unloaded`, `priority_ladder_basis_strings`, `credit_free_variant_formula`, `clamped_to_warm_value_above_target`, `discharge_limit_derated_in_the_cold` | 5 |
| tautology — WS9 *binds* WS8's constant (`ws9_candidates.py:72-73`), so the two sides are the same object | `unloaded_force_threshold_N`, `minimum_speed_threshold_m_per_s` | 2 |
| not a WS8-vs-WS9 comparison at all — the "WS8 r3" column is a prose string and the verdict tests only WS9's own source | `threshold_application_sites_in_ws9` | 1 |
| hard-coded `DIFFERS_BY_DESIGN` (declared, so not a defect, but also not measured) | 6 fields | 6 |

`discharge_limit_derated_in_the_cold` extracts nothing at all: both sides are the Python literal `False`.

**Evidence — mutation test, run on a scratch copy of WS8 and WS9, never on the repository.** I injected changes into the WS8 copy and re-ran `concordance_block`:

- Changed WS8's `apply_energy_corrections` so that `acc["fuel_g_corrected"] = acc["fuel_g"] + g_soc + g_uns * 1.5`. `corrected_fuel_formula` correctly flipped to **DIFFERS** and `any_undeclared_difference` went **True**. The genuine fields work.
- In the same run I changed `acc["fuel_g_corrected_deficit_only"] = acc["fuel_g"] * 2.0 + g_soc_def + g_uns`. `credit_free_variant_formula` stayed **CONSISTENT**. Blind.
- Removed the `min(..., 1.0)` clamp from `Pack8.cold_chg_factor_at`. The extraction correctly recorded `ws8_r3=False, ws9=True` — **a real, extracted, undeclared difference** — and the verdict was still **CONSISTENT**, with `any_undeclared_difference = False`. The trip-wire did not fire on a difference the module itself had already measured.
- Changed `SPIN_IDLE_FORCE_N` from `1.0` to `7.0` in the WS8 copy. The concordance reported `ws8=7.0, ws9=7.0, CONSISTENT`. It cannot differ.

The rendered report makes one of these visible to any reader: REPORT §12.2's `priority_ladder_basis_strings` row prints two visibly different string sets in the WS8 and WS9 columns and labels the verdict **CONSISTENT**.

**Why it matters.** ESC-WS9-8's whole point, and §17.5's claim that the computed concordance "replaces a prose concordance with a computed one", rest on this module. Two thirds of it is prose with a verdict column. The defect class WS8's r2/r3 adjudications found three times has been reintroduced one level down, inside the module built to eliminate it.

**What would resolve it.** Compute every verdict from the two extractions (no literal `verdict=` strings); for the fields where the two sides are not comparable by construction, either delete the field or label it explicitly as `NOT_A_COMPARISON` and exclude it from the "consistent" tallies in §12.2 and §17.3; and add a self-test that mutates a copy of each WS8 source and asserts the trip-wire fires. Restate the §12.2/§17.3 counts on the fields that can actually fire.

---

## PRE-B2 — "The (b) denominator difference is worth exactly 0.0 over 96 genset-branch runs" is a tautology of a missing key, not a measurement

**Severity: BLOCKING.** Same directive item; same reason to raise it now.

**What is wrong.** `ws9_concordance._measure_correction` (line ~763) computes the difference between WS8's correction denominator (`fuel_g_genset`) and WS9's (`fuel_g`):

```python
f_tot = r.get("fuel_g") or 0.0
f_gen = r.get("fuel_g_genset")
if f_gen is None:
    f_gen = f_tot
rel = abs(f_tot - f_gen) / max(f_tot, 1e-9)
```

**`fuel_g_genset` exists in 0 of the 576 per-seed records in `results_ws9.json`.** I checked every one. The fallback therefore fires on every run, `rel` is identically `0.0` by construction, and the exported `worst_case_relative_difference = 0.0` over `n_runs_on_the_genset_branch = 96` measures nothing. A denominator difference of any size would have produced the same 0.0.

**Evidence.** `python3` over `results_ws9.json`: 576 per-seed rows total, `fuel_g_genset` present in 0, `e_genset_bus_kWh > 1e-6` in 96 (all S4p) — so the 96 is real and the 0.0 is not. REPORT §12.2's own `energy_keys_read_to_price_the_correction` row confirms WS8's side does read `fuel_g_genset`, so the key difference is real in WS8's source.

**Note on the underlying physics.** The *claim* is probably true — S4' is the only WS9 candidate with a genset and it burns fuel for nothing else, so `fuel_g == fuel_g_genset` for it. But that is the argument WS9 already states in the `note` field. The artifact presents it as measured ("measured in `measured` below, not assumed"), in the section built specifically to stop unmeasured concordance claims, and it is not.

**What would resolve it.** Export `fuel_g_genset` from the S4' run (it is computable — the sustainer's fuel is a separate array), and let the measurement actually compare two numbers. Until then, remove the "measured, not assumed" framing from §12.2, §17.3 and the escalation, and state it as the argument it is.

---

## PRE-B3 — The heat ledger's 6% climb case for S5-13L is evaluated on the wrong branch of a non-monotone envelope; the row WS6 consumes understates the sustained case by ~25x

**Severity: BLOCKING.** Rule 7 export, consumed by WS6, for a candidate carrying an ADVANCE, and it is the WS8-F1 defect class (governing case outside/wrong within the enumerated set).

**What is wrong.** `run_ws9._steady_climb_speed` (line 892) finds the sustained climb speed by bisection on `[1.0, 33.0] m/s`, which assumes the excess tractive force `f_t(v) - f_r(v)` has a single sign change. For a 2-speed dog box with a coupling floor it does not: below the floor the engine is disconnected (D16, the third wall), so the envelope **jumps up** at the floor and the holding set is two disjoint bands.

I evaluated `cand.envelope(v)` against `PH8.road_load_force` on a 0.25 m/s grid at 6% grade and GCW, for every candidate:

| candidate | speeds at which the 6% grade is held [km/h] | `_steady_climb_speed` returns |
|---|---|---|
| S0R | 3.6 – 47.7 (one band) | 48.48 — correct |
| S6 | 3.6 – 47.7 (one band) | 48.48 — correct |
| S7 | 3.6 – 49.5 (one band) | 49.70 — correct |
| S4p | 3.6 – 65.7 (one band) | 66.48 — correct |
| S5 (11 L) | **3.6 – 17.1** and **26.1 – 39.6** | 40.12 — lands on the upper band, correct by luck |
| **S5-13L** | **3.6 – 22.5** and **34.2 – 51.3** | **23.37 — lands on the LOWER, motor-only band** |

The consequence, from the committed `data/heat_ledger_ws6.csv` and `results_ws9.json`:

| S5-13L, `climb_6pct` | as exported | correct (engine coupled) |
|---|---|---|
| road speed | 23.37 km/h | **52.14 km/h** |
| `engine_coolant_kW` | **0.0** | **199.0** |
| `engine_exhaust_kW` | **0.0** | **274.8** |
| `driveline_kW` | 0.0 | 29.2 |
| `total_rejected_kW` | **20.1** | **507.3** |

I obtained the right-hand column by re-running `component_heat_kw` at the top of the upper holding band (refined by bisection inside that band) — same function, same candidate, same context, only the speed corrected.

Because the climb row is zero, the exported worst case for S5-13L becomes the cruise case: `heat_ledger.S5-13L.worst_case.engine_coolant_kW = 70.72 kW @ cruise_95kmh_flat`, and `worst_case_sustained` the same. WS6 is therefore told to size S5-13L's cooling package on 70.7 kW when the comparable ruler figure is 207.1 kW and S5's is 155.1 kW.

**A second defect rides on the same row.** Every analytic case is stamped `duration_class: "sustained"` and the `duration_convention` field says the vehicle "holds that speed on that grade **indefinitely**". On the motor-only branch that is false by construction — the buffer is finite. The row is both the wrong branch *and* mislabelled as indefinite.

**Third: the report contradicts itself here.** REPORT §3.3 states that ENG-13L holds the 6% grade at **48.3 km/h** with the engine above its 33.5 km/h coupling floor ("reachable above the coupling floor: **True**"). The heat ledger says 23.37 km/h with the engine off. Two blocks derived from the same model disagree about the same physical case.

**What would resolve it.** Replace the bisection with a scan of the whole speed range and take the **highest** speed at which the envelope holds the grade (or, better, the highest speed on the *engine-coupled* branch, declared as such); re-emit the ledger; and re-check whether any other analytic case (`descent_*` uses `cand.v_cap(grade)`) has the same non-monotonicity exposure. Then reconcile §3.3 and §14 explicitly.

---

## PRE-B4 — The artifact gives the lead two incompatible accounts of which two trip-time statistics it exports, and its headline count of over-bar cases is false on the pair its own table names

**Severity: BLOCKING**, because R38 is a gate the lead applies from this export and the accounts differ on the case R38 turns on. **I do not apply R38 and I do not rule on the statistic.** The numbers below are re-derived, not adjudicated.

**What is wrong — three separate things in one place.**

**(a) "The two exported statistics" means different things in §12.3 and §17.6.** The interface field `trip_time_R38_gate_input.statistic_note` and REPORT §12.3 both define the pair as *median-of-medians* and *`paired_cases_max`* ("the 8-seed envelope of the PER-SEED PAIRED ratio … which is the convention every margin in this report uses and which rule 4 asks of a stochastic extremum"), and §12.3 accordingly reports S5-13L as **"OVER on both"**. `CHANGELOG_WS9_r3.md` §17.6 — and REPORT §17.6, which is generated from the same lines — defines the pair as *median-of-medians* and *paired **median***, and reports S5-13L as "over on the median-of-medians, **under on the paired median**". A lead reading §12.3 and a lead reading §17.6 come away with opposite impressions of the same candidate.

**(b) §17.6's headline sentence is false on the pair it names.** It says *"12 design-duty case(s) sit above R38's +5% trip-time bar on at least one of the two exported statistics"* and then lists twelve values — every one of which is a **paired-max** value, not a median-of-medians or a paired median. On the pair the very next table names (median-of-medians and paired median), the count is **11**, not 12: `S5-13L/payload_minus20/GH-REG-165` is +2.483% on the median-of-medians and +2.165% on the paired median — under the bar on both — and is in the list only because its paired **max** is +5.742%. The interface itself carries both counts correctly (`n_design_duty_cases_above_gate = 11`, `n_design_duty_cases_above_gate_paired_max = 12`); the prose merges them.

**(c) Both counts double-count a corner BASELINE_v5 dropped.** R39/ESC-3 rules that "the null grade-heavy corner is dropped", and WS9's own sanity block asserts `design_duty_null_at_grade_heavy_corner.identical = True` — the `grade_heavy` and `nominal` rows on the design duty are numerically identical. Both appear as separate cases in the 11 and the 12, and in §17.6's "disagree on **2** of its design-duty corners" (they are one corner, counted twice). On distinct corners the figures are 9 and 10, and the disagreement is on **one** corner, nominal.

**Evidence — re-derived from per-seed `duration_s`, all four statistics, S5-13L on the design duty (5 distinct corners):**

| corner | median-of-medians | paired min | paired **median** | paired **max** |
|---|---|---|---|---|
| nominal (= grade_heavy) | **+6.072** | +2.809 | +4.949 | **+7.936** |
| payload_plus20 | **+7.704** | +4.570 | **+6.816** | **+9.223** |
| payload_minus20 | +2.483 | +0.110 | +2.165 | **+5.742** |
| cold_minus10C | **+6.627** | +3.655 | **+5.484** | **+8.379** |
| hot_alt_2000m_45C | **+6.482** | +3.649 | **+5.521** | **+7.873** |

(bold = over +5%. All twenty numbers reproduce exactly from the per-seed durations; the ruler and candidate cover the same distance to 3e-6 %.)

**The thing the lead most needs and the artifact does not say.** The "statistic decides it" framing is true **only at the nominal corner**. On *every* statistic WS9 exports, S5-13L is over +5% at payload_plus20, cold_minus10C and hot_alt_2000m_45C. If R38's "design-duty trip time" is read the way the pre-committed ADVANCE criteria are read — nominal *and* every corner — the choice of statistic changes nothing for S5-13L. It matters only if R38 is a nominal-only gate. §17.6 puts the spotlight on the one corner where the statistic decides and calls the rest "the two agree", which is true but reads as reassurance.

**On which statistic is defensible on this program's own conventions — offered as analysis for the lead, not as a ruling.** Three facts point the same way. (i) Every margin in WS9 is a *paired per-seed* ratio enveloped afterwards: `margins[...].per_seed[i].margin_pct` is computed seed-by-seed and `advance_kill` reads `ensemble.min` — I verified this reproduces exactly. (ii) R36 restated D13 onto "the paired per-seed statistic" precisely because "the former wording carried a **ratio-of-medians artifact** into doctrine". A trip-time ratio is the same object as a per-km energy ratio in construction — candidate over ruler on the same stochastic realisation of the same duty — and the pairing argument transfers without modification; if anything more strongly, because trip time is dominated by the same random cycle events in numerator and denominator. The median-of-medians is exactly the construction R36 deprecated. (iii) CLAUDE.md rule 4 asks a stochastic extremum to be an 8-seed ensemble **envelope**; the advance criterion takes the conservative end of that envelope (min, for a benefit). The conservative end for a *penalty* is the **max**. That chain leads to paired-max, on which S5-13L is over the bar at all five distinct design-duty corners (+5.742 to +9.223).

Against that: R38 was pre-committed as a plain "trip time <= +5% of S0R" and one may read "trip time" as the ordinary median trip time rather than an envelope. **That is the lead's call and I make none.** What I can say is that the *median-of-medians* has no support anywhere in this program's conventions after R36, and it is the statistic the interface's `design_duty_nominal_pct_vs_ruler` — the unsuffixed, most prominent field a consumer would read — actually carries. See PRE-m3.

**What would resolve it.** Make §17.6 use one named pair consistently with §12.3 and the interface; recompute the counts on the distinct design-duty corner set after R39/ESC-3 drops `grade_heavy`; state plainly that no exported statistic puts S5-13L under +5% at payload_plus20, cold_minus10C or hot_alt_2000m_45C; and put the R36 argument in front of the lead rather than leaving "R38 names a bar and not a statistic" as the whole of it.

---

# MATERIAL

## PRE-M1 — The r3 pin is still incomplete: at least three more sibling sources reach WS9's numbers and none of them is pinned, while the artifact claims the set is complete

**Severity: MATERIAL.** No number is currently wrong — I checked — but the completeness claim is false and WS4 is being modified in this tree tonight.

**What is wrong.** §17.5 says "the pin now covers 6 sibling-workstream sources WS9 reaches through WS8"; ESC-WS9-11 says "This round pins all six"; the interface `statement` says the hashes pin "the sibling-workstream sources WS9 reaches THROUGH WS8". I instrumented `import run_ws9` with an `open()` spy and enumerated `sys.modules`. Three load-bearing sources outside WS9 are reached and are **not** in `inherited_vintage.sibling_workstream_sources_reached_through_ws8`:

| source | how it reaches a WS9 number | pinned by WS8? |
|---|---|---|
| `../WS3_battery/ws3_pack.py` | `ws8_electric.py:39` does `from ws3_pack import MASS_OVERHEAD_FACTOR, MASS_OVERHEAD_FIXED_KG`; `Pack8.__init__` sets `self.mass_kg` from them; `ws9_storage.py:156` builds `EL8.Pack8(...)` for every electrified candidate. Pack mass -> mass ledger -> **payload -> the metric's denominator**. | **yes** — `run_ws8.py:3855` pins it |
| `../WS2_traction_motor/data/capability_vs_rpm.csv` | `ws8_electric._ws2_capability()` reads it; called from `ScaledEDrive.__init__`, i.e. by every electrified candidate; sets `_cap_tpk`/`_cap_tct`, the machine's torque envelope — which is what the two walls, the power-limited fraction and the unserved energy all turn on. | **yes** — `run_ws8.py:3854` pins it |
| `../WS1_loads_duty_cycles/volt_params.py` | `ws4_models.py:24` does `from volt_params import VEH, DL, AUX, ENG, CTL, G`; `ws4_models` is on WS9's own pinned list, so the module WS9 pins depends on a module it does not. | no — WS8 misses it too |

**Evidence.** Module enumeration after `import run_ws9`: outside-WS9 modules loaded are `WS1_loads_duty_cycles/volt_params.py`, `WS3_battery/ws3_cells.py`, `WS3_battery/ws3_pack.py`, `WS4_genset/ws4_chain.py`, `WS4_genset/ws4_models.py`, and WS8's seven. The pin table lists only `ws4_models.py`, `ws4_chain.py`, `ws3_cells.py` and three WS2 data files.

**Current exposure: nil, but not by design.** `git log` shows all three unchanged since `c244234`, so no committed WS9 number is wrong. But `ws4_chain.py` has moved twice since (`b1c32cd`, `479dbce`) — which is exactly what ESC-WS9-11 was raised about — and `WS4_genset/` is dirty in the working tree right now with KX rounds running. If KX touches `ws4_models.py`, `volt_params.py` or WS2's exports, `verify_ws9.py` will report no drift and the "0 of 62 symbols changed, so nothing could move" argument will be silently wrong.

**A related structural weakness worth the lead's attention.** The 62-symbol import surface hashes the *source text of each symbol* inside WS8's files. `Pack8`'s text does not change when `MASS_OVERHEAD_FACTOR` changes in `ws3_pack.py`. So "0 of 62 symbols changed ⇒ no WS9 number can move" is sound only for changes confined to the hashed symbol bodies. The whole-file pins are the stronger instrument, and they are the ones with the holes.

**What would resolve it.** Add the three sources to the pin table (WS8's own `_SHA_PIN_PATHS` is the model for two of them); or take ESC-WS9-11's own "whole-tree pin" ask seriously and pin by transitive import closure computed at run time rather than by a hand-maintained list.

---

## PRE-M2 — The pack thermal state has no upper bound, no hot-side derate and no cooling power charged; modelled pack temperatures reach 153 °C, including at a corner that gates

**Severity: MATERIAL.** Optimistic for every electrified candidate, including three that carry ADVANCE.

**What is wrong.** `ws9_thermal.PackThermal.step` integrates `Q_ohmic + Q_coolant + Q_heater - UA*(T - T_amb)`. There is no active cooling term, no temperature ceiling, and no high-temperature derate: `ws9_storage.WS9Pack.p_cont_chg_kw_at` (and WS3's `cold_chg_factor_at`) interpolate on `[-10 C, 15 C]` and clamp at 1.0, so every temperature above 15 °C is treated identically. `eta_chg` / `eta_dis` are constants. Pack temperature therefore has **no consequence at all** above 15 °C, and nothing stops it rising.

**Evidence — median and max modelled pack temperatures from `results_ws9.json`:**

| corner | candidate | duty | median end T | max T |
|---|---|---|---|---|
| nominal (20 °C amb) | S7 | LH-520 | 126.1 °C | 134.4 °C |
| nominal | S4p | LH-520 | 86.3 °C | 96.5 °C |
| hot_alt_2000m_45C | S7 | LH-520 | **147.3 °C** | **153.4 °C** |
| hot_alt_2000m_45C | S7 | **GH-REG-165 (gates)** | 99.0 °C | **102.0 °C** |
| hot_alt_2000m_45C | S5 | GH-REG-165 (gates) | 82.6 °C | 87.8 °C |
| cold_minus10C | S7 | LH-520 | 106.9 °C | 116.8 °C |

An LTO pack does not operate at 150 °C; it does not operate at 100 °C. In reality the pack would either be actively cooled — bus power that is never charged here — or derated, or both. Both omissions run in the candidates' favour, and the 2,000 m / +45 C corner is one of the four R28 corners that gate the design duty.

**Second-order consequence for the concordance.** `_measure_pack` hard-codes `corner = "cold_minus10C"` and concludes "*that is the whole measured extent of this declared difference*". It is the whole extent **at the cold corner**. Nothing measures the hot corner, where the modelled pack temperature departs furthest from the corner ambient that WS8 r3 would have used. (In this build the answer happens to be zero because there is no hot-side derate — but that is PRE-M2, not a concordance result.)

**What would resolve it.** Either state explicitly, in the report and in the interface's thermal block, that the pack model is cold-side only and that no hot-side limit, derate or cooling load is modelled — with the direction of error named — or model a cooling loop and charge its bus power. A `t_pack_max_C` sanity assertion with a declared ceiling would have caught this.

---

## PRE-M3 — R14 violation: `power_limited_fraction` states a max rule and exports no max and no governing case

**Severity: MATERIAL.** CLAUDE.md rule 3 / R14: *"Every machine-readable worst-case field is an explicit max/min over an enumerated case set, with the governing case labeled inline."*

**Evidence.** `interface_ws9.power_limited_fraction` has exactly three keys: `rule`, `cases`, `meaning`. Its `rule` reads *"max over the enumerated (candidate, corner, duty) case set"* — and there is no `value` and no `governing_case`. Every other worst-case field in the block (`unserved_energy_kWh`, `retarding_shortfall_kWh`, `cold_wall_R30`, `wall2_payload_delta_kg`, the trip-time block, every heat-ledger row) has both.

The missing number is **0.4304 at `S5/grade_heavy/LH-520`**, and the design-duty maxima are S5 0.4089 (payload_plus20) and S5-13L 0.2655 (nominal) against the ruler's own 0.1909 — i.e. this is the capability field that explains the R38 trip-time story, and it is the one a consumer cannot read a worst case out of.

**What would resolve it.** Add `value` and `governing_case` and make `verify_ws9.py` assert the R14 shape (`rule` + `cases` + `value` + `governing_case`) on every field that carries a `rule` string.

---

## PRE-M4 — The heat ledger's "max over the FULL enumerated case set … AND the transient simulated peak" does not include a simulated peak for six of its ten rows

**Severity: MATERIAL.** Same family as WS8's F1 finding, which was blocking there.

**What is wrong.** `run_ws9.heat_ledger` builds the `simulated_peak_over_all_runs` member by scanning the per-seed record for exactly four fields:

```python
("brake_resistor_kW", "resistor_peak_kW"),
("hydraulic_retarder_coolant_kW", "retarder_peak_kW"),
("compression_brake_exhaust_kW", "engine_brake_peak_kW"),
("friction_brake_kW", "friction_brake_peak_kW")
```

The other six rows — `engine_coolant_kW`, `engine_exhaust_kW`, `traction_machine_inverter_kW`, `generator_rectifier_kW`, `pack_kW`, `driveline_kW` — are initialised to `0.0` and never measured. Each row's `worst_case` field nonetheless declares `rule = "max over the FULL enumerated case set, sustained cases AND the transient simulated peak"`. For six of ten rows the transient member is a placeholder zero, so the stated rule is not the rule that was applied.

This is defensible engineering (a radiator is sized on a sustained case, not a transient) and `worst_case_sustained` exists precisely to say so — but then the `worst_case` field should not claim a membership it does not have. As it stands a WS6 consumer reading `worst_case.engine_coolant_kW` is told it is a max over a set including the simulated peak, and it is not.

**What would resolve it.** Either export the simulated peaks for all ten rows (the per-seed record would need the corresponding peak fields), or change the six rows' `rule` string to say the transient member is not measured for them and why.

---

## PRE-M5 — B1-class co-occurrence is present in S5 and S5-13L, is unmeasured, and the R34 traces cannot support the check

**Severity: MATERIAL.** ADJUDICATION_DIRECTIVE item 5 designates this question to the Fable round. **I am reporting a measurement and flagging it; I am not ruling on whether it is the same defect WS8 r2 called blocking.**

**What I found.** WS8 r2's B1 was "S3's control law lets the engine fuel and compression-brake simultaneously". WS8 r3 answered it with `overrun_mask` / `braking_mask` / `exclusivity_report`, which *measures* the property. WS9 has the overrun fuel cut on its AMT path (`ws9_candidates.py:212-233`, same thresholds as WS8: `F_trac <= 1.0 N`, `rpm > idle*1.1`) but **no equivalent measurement anywhere**, and the S5 family's dispatch reaches fuel by a different route: the engine may charge the buffer whenever it is coupled, the buffer is under target and `load_frac < 0.72` (`ws9_candidates.py:979-982`), which sets `f_chg_wheel > 0`, hence `t_eng > 0`, hence `g > 0` — on the same samples on which the compression brake is retarding.

**Evidence — instrumented run on a scratch copy (never on the repository files), capturing `g` and `f_eb` per sample:**

| candidate / corner | duty | samples with compression brake **and** fuel | fuel on those samples | share of run fuel |
|---|---|---|---|---|
| S5-13L / nominal | GH-REG-165 | 647 (64.7 s) | 111.5 g | **0.223%** |
| S5-13L / nominal | LH-520 | 774 | 140.8 g | 0.088% |
| S5-13L / cold_minus10C | GH-REG-165 | 838 | 142.6 g | 0.274% |
| S5-13L / payload_plus20 | GH-REG-165 | 1,923 | 319.7 g | **0.621%** |
| S5 / nominal | GH-REG-165 | 2,048 | 352.1 g | **0.700%** |
| S5 / nominal | LH-520 | 1,077 | 212.3 g | 0.129% |

**Direction of error: against the candidates.** Removing this fuel would *improve* S5-13L's margin, not create it — the opposite of WS8's S3, where the correction moved toward the bar. The magnitudes (0.09–0.70%) are an order below WS8's S3 (5.67%). So this does not manufacture an ADVANCE. What it does do is leave a known blocking-class property of the program's own making entirely unmeasured in a round that pinned the WS8 code containing the fix.

**And the R34 traces cannot answer it.** The trace columns are `t, v, s, grade, F_trac, F_regen, F_retard, F_friction` — force channels only. The header states *"The integrator never commands traction and a braking channel on the same sample"*, which is a claim about the **demand trace**, not about fuel; the B1 property is fuel-versus-retard and no exported artifact carries the channels to test it. Any future adjudicator has to instrument the code, as I did.

**What would resolve it.** Port WS8 r3's `exclusivity_report` (or an equivalent) into WS9's sanity block and export the fraction of fuel on braking samples per candidate and corner; and consider adding an engine/fuel channel to the R34 trace so the check is possible from artifacts.

---

## PRE-M6 — R39/ESC-2's order to source US-West grid factors is unexecuted, and the artifact still carries the declared 2.1 that decides S4'

**Severity: MATERIAL** for the record; the numbers are correct for the factor declared.

**What is wrong.** BASELINE_v5 R39/ESC-2 rules that "Vehicle One's market is declared as the US West (California corridors …); grid primary-energy and CO2 factors **to be sourced for that market**; S4' stays PROVISIONAL-ADVANCE with its flip point on the record." This re-run executed after R39 was ratified. `interface_ws9.electricity_accounting_ESC3` still carries `pef_grid = 2.1`, `co2_grid_kg_per_kWh = 0.28`, unsourced, with the ±50% bracket, and ESC-WS9-2 still stands as written before R39.

I do not treat this as a compliance failure of the round: NIGHT_SHIFT A3's order was narrowly "re-run against r3 sources", and re-sourcing a market factor is not in it. But D18 makes the flip point part of the result, and the flip point is entirely a function of a factor the baseline has ordered replaced. The lead should see that R39/ESC-2 is still open and that S4' cannot be disposed of until it closes.

**Re-derived, for the record:** at the +50% end (`pef_grid` 3.15) S4's design-duty nominal ensemble-min is **-0.38094%** and the verdict flips to KILL; at the -50% end it is +24.289%. All four other candidates are exactly invariant (`grid_kWh = 0` on every run). Both reproduce exactly.

**One directional note for the lead.** A California grid factor is very likely *lower* than the declared 2.1, i.e. on the side that keeps S4' alive. The flip point sits at the pessimistic end of a bracket the market declaration probably narrows favourably. That is a reason to source the factor, not a reason to assume the answer.

---

# MINOR

**PRE-m1 — The determinism checker compares 10 fields of a ~245-field per-seed record.** `check_determinism_ws9.py`'s `COMPARE_KEYS` is ten names; half 1's "160 values" is 2 duties x 8 seeds x 10. Nothing in `pack_thermal` is compared — which is precisely the block the mid-flight `_measure_pack` correction touched. I ran the wider check myself (5 jobs, 9,051 scalar values, all fields) and found no drift, so the conclusion stands; the *evidence* is narrower than the claim "every per-seed metric is compared against the committed record at zero tolerance" in the module docstring. Widen `COMPARE_KEYS` to the full key set, or restate the docstring.

**PRE-m2 — `interface_ws9.trip_time_R38_gate_input.statistic` contradicts `statistic_note` inside the same object.** `statistic` says "median trip time over the 8-seed ensemble" (one statistic, and the deprecated one); `statistic_note` two keys later says "TWO STATISTICS, both exported". A machine consumer reading `statistic` gets the wrong answer.

**PRE-m3 — The unsuffixed interface field carries the deprecated statistic.** `design_duty_nominal_pct_vs_ruler` is the median-of-medians; the paired distribution is under the longer key `design_duty_nominal_paired_pct_vs_ruler`. After R36, the unsuffixed name should carry the paired statistic and the ratio-of-medians should be the one that needs a suffix. Same for `worst_case_pct` / `governing_case` (median-of-medians) versus `worst_case_paired_max_pct` / `governing_case_paired_max`. This is the "interface exports the wrong member of a set the prose describes correctly" class; the values are all present and correct, only the naming privileges the wrong one.

**PRE-m4 — The interface `_convention` string is not true of one of its own fields.** It asserts "stochastic extrema are 8-seed ensemble envelopes (rule 4)"; `design_duty_nominal_pct_vs_ruler` and `design_duty_cases_above_gate` are ratios of medians, not envelopes.

**PRE-m5 — WS9 re-implements WS8's overrun constants as literals and the concordance does not cover them.** `ws9_candidates.py:212-213` hard-codes `f_trac <= 1.0` and `rpm > engine.idle_rpm * 1.1`; WS8 r3 names the same values `OVERRUN_F_TRAC_EPS_N` and `OVERRUN_RPM_MARGIN`. ESC-WS9-8's field list predates B1, so the overrun rule is not one of the three implementations compared. A change to WS8's constants would not propagate and nothing would report it. (Contrast the spin constants, which WS9 *binds* — see PRE-B1.)

**PRE-m6 — `no_ws8_artifact_read` is a line-level textual heuristic.** It flags a source line that both names a WS8 artifact and contains an opener keyword; a read split across lines, or a path built from a variable, is invisible to it. The claim itself checks out by a stronger method — I ran an `open()` audit over `import run_ws9` and saw no WS8 artifact opened — but the exported evidence is weaker than the exported claim.

**PRE-m7 — Direction-of-error label on the correction pricing may be inverted for the mechanical-path candidates.** `correction_eta_basis` reads "a bus-side shortfall priced on the wheel-side path, **the generous direction**". For S5-13L nominal, `correction_eta = 0.3787` while the engine's shaft efficiency is ~0.419 and a plausible engine-to-bus path is ~0.39–0.40; charging bus kWh at 0.3787 therefore appears to charge *more* fuel, i.e. the strict direction, not the generous one. **Low confidence** — I could not fully pin down the intended semantics of the inherited WS8 rule, and the direction as I read it is the safe one. Flagging so the Fable round can settle the label.

**PRE-m8 — S4's correction share reaches 32.3% of reported fuel and no sensitivity on `correction_eta` is exported.** Disclosed honestly in §8 and recommendation point 5 (`unserved_kWh` up to 257.1 kWh at `S4p/grade_heavy/LH-520`), and `fuel_g_corrected_deficit_only` exists as a variant — but there is no one-factor row showing what S4's +11.95% does if the make-up energy is priced 10% or 20% worse. Given that a quarter to a third of S4's fuel is a modelled construct, that row would be worth more than most of what is exported.

**PRE-m9 — ESC-WS9-12 understates its own evidence.** It says `check_determinism_ws9.py` "re-simulates **one** of these traces from a fresh process"; half 3 re-simulates all six and diffs them byte for byte. Harmless, but an escalation to the lead should describe its own evidence accurately.

---

## What I could not establish in the time available

- **I did not re-simulate the full trial.** 5 of 36 (corner, candidate) jobs were re-run from scratch, covering all five candidates and four of six corners; S0R itself was not re-run standalone. The other 31 jobs are reproduced only by WS9's own committed evidence.
- **I did not re-derive the physical models from first principles** — the WS2 loss surface, the BSFC maps, the duty-cycle generator, the road-load and adhesion models are inherited from WS8/WS2/WS3/WS4 and I checked their *use*, not their content. WS9's own first-principles sanity checks (road load at 95 km/h, CO2 from carbon balance, ruler energy closure, startability) all reproduce, and I re-derived the S6 break-even independently in closed form.
- **I did not verify S6's cited 49.2% peak BTE**, or its evidence quality. That is ADJUDICATION_DIRECTIVE item 2 and ESC-WS9-1's subject. What I can say is that the break-even arithmetic is right (0.469155 recomputed against 0.469155 exported), that the ~2.32 pp headroom in R39/ESC-1 is correct, and that D17's "predictive energy management is worth ~0" holds in this build: the S0R-PCC bracket makes the ruler 0.098% *worse*, so S6's margin is the engine and nothing else.
- **I did not re-derive the third wall in closed form** (directive item 4). I did establish, as a by-product of PRE-B3, that the 6% holding set for S5-13L is genuinely two disjoint bands with a gap from 22.5 to 34.2 km/h, and for S5 from 17.1 to 26.1 km/h — which is the third wall measured directly off the envelope, and consistent with §3.3's coupling floors of 33.5 and 25.4 km/h.
- **I did not audit WS8 r3 or any of its findings**, and nothing here resolves, softens or disposes of any WS8 finding.
- **I did not apply R38**, did not read any verdict as final, and did not rule on any of the twelve escalations. On the escalations I checked only the formal properties the mandate names: all twelve cite the ruling or finding they challenge, all twelve carry a "why this is not self-resolved" clause and an "asks" clause addressed to the lead, and none contains a disposition. ESC-WS9-10, -11 and -12 are new tonight and are correctly characterised; ESC-WS9-11's *finding* is right and its *remedy claim* ("This round pins all six") is what PRE-M1 is about.

## Compliance summary against the standing checklist

| rule | result |
|---|---|
| 1 — deterministic pipeline, byte-stable regeneration | holds; verified more widely than the committed check (see PRE-m1) |
| 2 — interface verifies verbatim against the results file | **byte-identical**, three ways, confirmed independently |
| 3 / R14 — worst-case fields as explicit max/min with governing case | **one violation** (PRE-M3) and **one misdescribed rule on six rows** (PRE-M4) |
| 4 — stochastic extrema are 8-seed envelopes | holds for every margin; **not** for the trip-time field the lead will read (PRE-B4, PRE-m3, PRE-m4) |
| 5 — part-load models, no peak-point scalars | holds — engines run on BSFC maps, machines on the WS2 loss surface, WHR on a load-fraction curve |
| 6 — electrical quantities bus-side | holds as far as I checked; the bus/wheel boundary is declared at each correction site |
| 7 — rejected heat by component and case for WS6 | structurally complete and better than WS8's, but **PRE-B3** makes one candidate's sustained climb row wrong by ~25x |
| 8 — escalations cite their ruling, never self-resolved | holds, all twelve |
| 10 — never modify other workstreams' artifacts | holds; WS8 was read-only and my mutation tests ran on scratch copies |
| R34 — 10 Hz trace per run | complied with as a declared subset, escalated as ESC-WS9-12; traces re-simulate byte-identically; column set cannot support the B1 check (PRE-M5) |
| R37 — verdicts PROVISIONAL, not reopened | holds; verdicts are computed from the pre-committed criteria and reproduce exactly |
| R38 — gate exported, not applied | the gate is genuinely not applied anywhere in the pipeline; **how it is presented is PRE-B4** |
