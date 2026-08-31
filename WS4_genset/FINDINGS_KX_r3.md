# FINDINGS — WS4 (genset) — KX round, review round 3 (`FINDINGS_KX_r3.md`)

Adjudicator: fresh context, disk only, independent re-derivation. Judged against
**BASELINE_v5.md** (authoritative — R34, R36, and the R14 / R9 / rule-5 /
rule-7 / rule-8 conventions carried from v2/v3), **BASELINE_v3.md** (R22, R23 —
the executed kill; R20/ESC-4 as carried from BASELINE_v2), `WS4_genset/
KX_DIRECTIVE.md`, and **`FINDINGS_KX_r1.md`** and **`FINDINGS_KX_r2.md`**, all
read in full first. Artefacts read on disk at commit `90c5bc2`: `REPORT_WS4.md`,
`results_ws4.json`, `run_ws4.py` / `ws4_sim.py` / `ws4_chain.py` /
`ws4_models.py` / `make_report_ws4.py` / `verify_ws4.py`, all `data/*.csv`
(including the three 10 Hz traces), `run_output.txt`, plus the read-only
WS2/WS3 imports and the `b1c32cd` (r1) and `479dbce` (r2) vintages for the
delta claims.

Scope as fixed by the lead in `KX_DIRECTIVE.md` ("Exit"): the R23 errata pins
(F1–F5), the `series_duty_v2` block, and interface consistency. **The G1 gate
decision is not reopened** — it is an executed kill (BASELINE_v3 R22/R23) and
`gate_g1` is treated only as an archived record block. I did not re-establish
byte-stability of the full pipeline; the foreman's mechanical gate passed. I did
independently confirm that `make_report_ws4.py` regenerates `REPORT_WS4.md`
**byte-identically** and that `verify_ws4.py` exits 0 (252 headline renderings +
interface block + 1,585 structural/errata pins), with a clean `git status` for
the folder afterwards.

---

## Verdict

**NOT CLEAN. One BLOCKING finding, three MATERIAL, six MINOR.**

All seven KX2 findings are addressed, five of them at root cause and verified by
independent re-derivation; two (KX2-M1, KX2-m1) are addressed in the field the
adjudication named and left uncorrected elsewhere. The round's arithmetic is
sound everywhere I could test it: every paired fuel delta, every errata pin,
every trace-derived counter, the archive freeze and the "three values changed"
claim all reproduce exactly, several of them to the last float bit.

The blocking finding is not an arithmetic error. It is the class this program
exists to catch: **the R20/ESC-12 evidence base is enumerated over a case set
that excludes the case the ruling names, while a run of that exact case sits in
the same results file, produced by this same round.** Included, it reverses both
of ESC-12's headline sensitivity results and turns a machine-readable
`all_cases_within_capability: true` into false at every declared coolant
temperature. The comparison that shows this needs no capability model, no
assumption and no ruling — it is two numbers at the same ambient.

Two of the sixteen areas the construction sweep certifies as **examined and
clean** are demonstrably not clean, and one of them contains the exact defect
the same round claims to have closed at source across the whole workstream.

---

## Verification record — what I re-derived independently

- **V1 — R20's two crossings, from first principles.** Rebuilt the ISA pressure
  model, the ideal-gas air temperature from each case's own `rho_air`, and the
  ITD capability ratio outside `run_ws4.py`. `design_case_crossover_top_tank_C`
  = **116.80962076727431 °C** and `break_even_top_tank_C` =
  **158.41996907947066 °C** reproduce to full float precision, as do all twelve
  `duty_over_capability_2min_by_top_tank_C` ratios and the corner's validation
  temperature (44.95073916789022 °C against its declared +45.0). The algebra
  `T_x = (Q_i·T_j − Q_j·T_i)/(Q_i − Q_j)` and `T_be = (T_a − q·45)/(1 − q)` is
  correct for the declared model.
- **V2 — every paired fuel delta, re-computed from the per-seed exports.** All
  three corrected blocks: companion (b′), the R16 pack bracket and the engine
  continuous-rating bracket, 3 cases × 8 seeds each. **72 per-seed values and 27
  envelope fields: 0 mismatches**, exact float equality, governing seeds
  re-derived by argmin/argmax. The medians (+0.169 / −0.022 / +1.789 %) and the
  worst paired seed (**+0.24877343356341006 %**, cda_5.4, seed 5) match
  `FINDINGS_KX_r2.md`'s own independent re-run to the digit, and the sign split
  (6 of 8 positive at nominal on the R16 bracket) reproduces.
- **V3 — the R6 rating-family probe against r2's independent re-run.** 287.1 /
  268.1 / 157.7 / 188.3 s against the ordered 250.0 s: **all five reproduce
  exactly** from the shipped per-seed data, and all five equal the numbers the
  r2 adjudicator obtained by re-running the simulator himself. Zero unserved on
  every seed of every probe case confirmed.
- **V4 — ESC-10's percent-of-rating, per case per seed.** 112.03367674921526 %
  at nominal and cda_5.4 (132.0 kW rating) and 108.68641251055598 % at the
  corner (122.9184 kW derated rating) reproduce from `engine_shaft_peak_kW` and
  `ENG_CONT_KW_BY_CASE`. The sweep's claim that the r2 form was "correct only by
  luck" is right: the max's governing case is one of the two underated cases.
- **V5 — the R16 curve, read straight from WS3's CSV.** 19 tabulated cells,
  −30…60 °C; continuous maximum 135.043 kW at 10 °C; peak pack charge
  147.58458351650407 kW; **minimum exceedance 12.541583516504062 kW**; exceeded
  at every tabulated cell; the 10-s pulse column covers the peak between 0 and
  50 °C cells. Both genuine regen-leg crossings (−9.39321930659508 and
  53.9494966014262 °C) reproduce to seven digits. KX2-M2 is closed and the
  replacement statement is exactly true.
- **V6 — the heat rows from the 10 Hz traces, with no simulator in the loop.**
  Recomputed engine rejection as `ṁ·LHV − P_shaft` per sample and re-ran the
  rolling-window maxima: seed 23's peak / 2-min / 10-min reproduce on all three
  ordered cases to the traces' own print precision (e.g. cda_5.4 239.8317 /
  239.8317 / 168.1063 against 239.831846 / 239.831846 / 168.106348), and
  `radiator_package_* = 0.48 × engine_rejection_*` holds exactly. The ledger's
  8-seed maxima and their governing seeds re-derive from the per-seed exports.
- **V7 — fuel books closed against the traces.** For each ordered case,
  `∫ṁ dt + 12 g × starts + SOC-drift correction` reproduces the exported
  `fuel_kg` to **1 mg**: nominal 18 757.233 + 60.0 + 62.815 = 18 880.048 g vs
  18 880.049 exported; cda_5.4 22 412.220 + 48.0 − 52.358 = 22 407.862 vs
  22 407.863; corner 15 515.572 + 72.0 + 97.324 = 15 684.896 vs 15 684.897. The
  trace is a faithful dump of the dispatch loop and the declared correction
  members are the only difference.
- **V8 — the archive, against the r1 vintage.** `gate_g1` at r3 vs r1:
  **2,654 common leaves, 0 changed, 0 removed, 6 added** (all R14 governing
  labels). Every `_raw_reference_seed/{a,b,bp}` dump is back to the record's
  **53-member key list in the record's own key order, 0 value diffs**, on all 13
  case/mode combinations. `gate_g1_one_factor`: 0 numeric changes. KX2-m3 is
  closed exactly, not approximately.
- **V9 — the "no ordered number moved" claim, against the r2 vintage.**
  Flattening both files: **exactly 3 distinct numeric values changed, in 12
  occurrences**, all of them the R22d coast-spin member; **0 boolean changes**;
  29 string changes; 301 removed keys (270 the archive projection, 31 the named
  withdrawals/renames). The changelog's claim is exact.
- **V10 — the R22d per-seed re-pricing.** All 24 per-seed `unbooked_pp` values
  reproduce from `(coast_shaft/η_series + coast_bus)/η_gen × BSFC ÷ fuel_g`;
  `unbooked_pp_max` = 0.00033954581949763416 (alt2000m_45C, seed 23) against the
  r2 ratio-of-extrema 0.000336470735977268. The "at most" phrasing is now true
  of a genuine max over the enumerated 3-case × 8-seed set.
- **V11 — errata pins.** F1: the corrected phrase occurs exactly once in each of
  the four places (headline, §0-R, §6 table, §12 ESC-2) on the whitespace-
  collapsed text, and no superseded wording survives. F3: 0.5148607848362983 and
  0.6324177500894939 pp recompute from the exported member lists. F5:
  78.85485355163588 / 86.08403730455855 = 0.9160217854635886. F2/F4 pins hold.
- **V12 — three-way interface check.** The §11 fenced block in `REPORT_WS4.md`
  is **byte-identical** (259,685 chars) to `json.dumps(results_ws4.json →
  interface_ws4, indent=1)`. `verify_ws4.py` exits 0. `make_report_ws4.py`
  regenerates the report byte-identically.
- **V13 — R14 label sweep over the whole interface.** Every extremum field in
  `interface_ws4` carries a governing-case sibling except the two deliberately
  retained superseded `..._ratio_of_ensemble_maxima_max` fields and one sweep-
  record field (R3-m4). Coverage is otherwise complete.
- **V14 — wheel / shaft / bus discipline on the new members.** The R20
  comparison is engine-package-to-engine-package: `radiator_package_2min_max_kW`
  is 0.48 × engine rejection, and `_R20_DESIGN_KW` = 95.01823316663226 is 0.48 ×
  (fuel − shaft) at 122.918 kW shaft at the R6 corner. No LT-chain, generator or
  pack heat is mixed in on either side. Clean.

---

## Round-2 findings — closure status, one by one

| id | severity (r2) | status | basis |
|---|---|---|---|
| **KX2-M1** | material | **RESOLVED AS NAMED — but the remedy carries R3-B1 and R3-M1** | The one-case-filtered comprehension is gone. `absolute_kW_comparison` is a real max/min over the enumerated three-case set with the exceeding cases listed, `all_ordered_cases_within_design_point_on_2min: false`, worst +21.155 %; the scoped boolean is renamed `r20_survives_on_the_2min_window_at_alt2000m_45C_only` and carries a note saying it is not a set verdict; the scoping argument is quantified. All verified (V1, V6). **However** the quantification is enumerated over a set that excludes R20's own design case (R3-B1) and over one thermal window whose scope its field names do not carry (R3-M1). |
| **KX2-M2** | material | **RESOLVED at root cause** | Clamp withdrawn; replaced by the measured statement, which is stronger and exactly true (V5). `_r16_crossing` asserts in range and returns `None` rather than a clamp. ESC-8(b) restated on the corrected reading. |
| **KX2-M3 (a)(b)(c)** | material | **RESOLVED at root cause** | All three recomputed on the paired per-seed statistic with 8-seed envelopes and R14 governing seeds; the ratio-of-statistics fields retained under names that say what they are, each with a `_superseded_field` note. 72 per-seed and 27 envelope values re-derived, 0 mismatches (V2). The three "paired per-case median" renderings (§4-KX.6, §8, ESC-9) are now true of the number they label; ESC-8(c) is restated on +0.249 %. |
| **KX2-m1** | minor | **PARTIALLY RESOLVED — see R3-M3** | `_case_worst` is correct and is used for both named brackets ("no governing case - every ordered case is exactly zero on all 8 seeds"). But the changelog's claim that it is "applied to **every** case-set extremum in the workstream" is false: 8 case-set governing labels, in 19 exported occurrences, are still raw first-key tie-breaks — including two full three-case ties at exactly 0.0. |
| **KX2-m2** | minor | **RESOLVED** | The six named maxima are labelled; `peak_pack_charge_governing_case` and `peak_regen_governing_case` are raised to the fuller form, and the first correctly discloses the exact nominal/cda_5.4 tie at 147.58458351650407 kW, which I confirmed is a true float-equal tie. |
| **KX2-m3** | minor | **RESOLVED at root cause and exactly** | The archive is byte-restored to the r1 member set, same 53 keys, same order, 0 value diffs, on all 13 case/mode dumps (V8). The archival notice states the freeze. |
| **KX2-m4** | minor | **RESOLVED at root cause** | Measured rather than mentioned: a four-case 8-seed R6 rating-family probe, union maximum 287.0999999997389 s with a fully enumerated union case set and R14 labels, both set maxima exported, ESC-10 restated. Every probe figure reproduces and matches r2's own independent re-run (V3). |

r2's non-finding **Note 5** (the 5 s vs full-rate `soc_usable_min`) is also
addressed: `soc_usable_min_sampling_note` now cross-references `soc_min_min` per
case.

---

# BLOCKING

## R3-B1 — BLOCKING — the R20/ESC-12 analysis is enumerated over a case set that excludes R20's own declared design case; this round ran that case, and including it makes `all_cases_within_capability` false at every declared top tank, deletes the 116.8 °C crossover, and moves the capability break-even from 158.4 °C to 45.6 °C

**What is wrong.** R20 (BASELINE_v2, per ESC-4) reads: *"radiator sizing case =
**R6 corner**, 95.0 kW engine package in +45 C air"*. R6's corner is
**+20 % payload, CdA 5.4, 4 kW accessories, +45 °C, 2,000 m**.

`heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point` enumerates
three cases — `nominal`, `cda_5.4`, `alt2000m_45C` — and **none of them is R6's
corner**. The ordered `alt2000m_45C` case is 2,000 m / +45 °C at **GVW, CdA 4.2,
2 kW aux** (`run_ws4.py`: `veh=dataclasses.replace(VEH, rho_air=0.8706),
derate=DER, t_cell_C=45.0` — CdA and mass at their defaults). It is the corner's
*ambient*, not the corner. The whole R20 conclusion structure rests on it:

- `r20_survives_on_the_2min_window_at_alt2000m_45C_only: true` (86.347 kW);
- `ambient_normalised_sensitivity → duty_over_capability_worst_by_top_tank_C →
  {95,105,115,125} → all_cases_within_capability: **true**` at all four;
- `break_even_top_tank_C: 158.41996907947066`, whose `break_even_reading` says
  *"It sits far above any physical diesel HT coolant cap, which is WHY the r2
  scoping argument pointed the right way ON THE CAPABILITY QUESTION"*;
- `design_case_crossover_top_tank_C: 116.80962076727431`, ESC-12's headline;
- ESC-12 to the lead: *"the capability break-even is a 158 °C top tank, far above
  any physical diesel HT cap — so on the capability question the r2 conclusion
  probably is right."*

**This round ran R6's corner.** `series_duty_v2 → r6_rating_family_probe →
cases → r6_rating_corner_full` is defined in `run_ws4.py` as
`veh=dataclasses.replace(VEH, CdA=5.4, rho_air=0.8706), m=7180.0, aux=4.0,
derate=DER, t_cell_C=45.0` — +20 % payload (7,180 kg = 6,600 + 0.2 × 2,900),
CdA 5.4, 4 kW aux, 2,000 m, +45 °C. That is R6's corner exactly. Its per-seed
`engine_reject_*` values are in `results_ws4.json`. Taking the 8-seed maxima and
applying the block's own 0.48 radiator-package share:

| case | 2-min radiator package [kW] | vs 95.018 kW design point | air [°C] |
|---|---|---|---|
| `nominal` (ordered) | 115.119 | +21.15 % | 21.006 |
| `cda_5.4` (ordered) | 115.119 | +21.15 % | 21.006 |
| `alt2000m_45C` (ordered) | 86.347 | −9.13 % | 44.951 |
| **`r6_rating_corner_full` = R20's own design case** | **103.522** | **+8.95 %** | **44.951** |

The R6 corner exceeds R20's design point by **+8.95 % on the 2-minute rolling
window** — and by the same margin on the instantaneous peak — **at the same
+45 °C ambient the design point is stated in**. No ambient normalisation, no ITD
model, no assumption and no ruling is needed to make that comparison: it is the
same arithmetic the block's own `absolute_kW_comparison` object already performs
for the other three cases.

**What including it does to every exported conclusion.** Running WS4's own
declared ITD model with the R6 corner in the enumerated set:

| duty ÷ ambient-normalised capability, 2-min window | 95 °C | 105 °C | 115 °C | 125 °C |
|---|---|---|---|---|
| `nominal` / `cda_5.4` | 0.8187 | 0.8655 | 0.9023 | 0.9320 |
| `alt2000m_45C` (ordered) | 0.9078 | 0.9080 | 0.9081 | 0.9082 |
| **`r6_rating_corner_full`** | **1.0884** | **1.0886** | **1.0887** | **1.0888** |

- `all_cases_within_capability` becomes **false at every one of the four declared
  top-tank temperatures**, not true at all four.
- The R6 corner is the worst case at **every** top tank, so there is **no
  design-case crossover at all** — the 116.8 °C number, ESC-12's headline and the
  basis of "ESC-4's design case is live rather than settled", does not exist as a
  result of the model once the ruling's own case is in the set.
- The capability break-even for the R6 corner is a **45.55 °C** top tank, not
  158.4 °C — i.e. under WS4's own model the package is out of capability at any
  coolant temperature a diesel actually runs, which is the exact opposite of what
  `break_even_reading` and ESC-12 tell the lead.

**Why it is blocking and not material.**

1. It is a machine-readable verdict on a live ruling (`all_cases_within_capability`,
   four instances) that reverses on this round's own data, in the one block the
   report tells WS6 to size against, for a workstream that has not yet run.
2. The number that reverses it is **unreachable from the interface**. The probe's
   interface projection (`interface_ws4 → series_duty_v2 →
   r6_rating_family_probe_ensembles`) carries only over-rating seconds, shaft
   peak, unserved, SOC, fuel/km, starts and pack peaks — **no engine-rejection or
   radiator field**. It is absent from `heat_ledger_ws6`, absent from the R20
   comparison's `cases` object, and absent from ESC-12. A consumer reading
   `interface_ws4` or the heat ledger cannot find it.
3. R14 requires every machine-readable worst-case field to be an explicit max/min
   **over an enumerated case set**. This is an R14 defect at the level of set
   *selection*: the set chosen to answer "is the R6 corner still the design case"
   omits the R6 corner. That is precisely the failure mode R14 exists to prevent
   and the one a rendering checker cannot catch — `verify_ws4.py` pins all of
   these fields and passes.
4. ESC-12 puts a three-part disposition to the lead whose part (1) is *"rule
   whether R20/ESC-4's 'radiator design case = the R6 corner' is retained on the
   ambient-normalised reading"*. The single most direct answer to that question is
   on disk, was computed by this round, needs no model, and is not in front of the
   lead. Both halves of what ESC-12 does present lean toward the standing ruling.

I considered material and did not stop there. The withdrawal of the r2 boolean and
the escalation were correct (see the note below), and no exported field states a
falsehood about a case it names — but a correct withdrawal followed by a
replacement analysis built on a set that excludes the ruling's own case leaves the
lead and WS6 worse informed on the point that matters than the raw data in the
same file.

**Resolution.** Add `r6_rating_corner_full` — or a case defined at R6's corner —
to the enumerated set of `series_duty_v2_transient_vs_R20_design_point`, with its
`radiator_package_{peak,2min_max,10min_max}_kW` rows, their governing seeds, its
`exceeds_r20_design_point_on_{peak,2min}` flags and its ambient-normalised ratios;
recompute `absolute_kW_comparison`, `duty_over_capability_worst_by_top_tank_C`,
`design_case_crossovers` and `break_even_*` over that set; project the probe's
heat rows into `interface_ws4`; and restate ESC-12 on the result. If the lead
instead rules that the probe must stay out of the R20 set, the block must say so
explicitly and export the R6-corner row beside it as a declared out-of-set
comparison, because the number exists and it points the other way.

---

# MATERIAL

## R3-M1 — MATERIAL — the ambient-normalised sensitivity exists on one thermal window only, its verdict fields carry no window in their names, and on windows ≤ 60 s the corner is 8.9 % over its own ambient-normalised capability at every declared top tank

**What is wrong.** The sensitivity sweeps four coolant top-tank temperatures and
**one** thermal window. `duty_over_capability_2min_by_top_tank_C` (per case)
names its window; the aggregates that carry the verdicts do not:

```
ambient_normalised_sensitivity/duty_over_capability_worst_by_top_tank_C/*/worst_ratio
ambient_normalised_sensitivity/duty_over_capability_worst_by_top_tank_C/*/all_cases_within_capability
ambient_normalised_sensitivity/design_case_crossover_top_tank_C
ambient_normalised_sensitivity/design_case_below_crossover / _above_crossover
ambient_normalised_sensitivity/break_even_top_tank_C / break_even_case
```

The window is stated only inside the `_assumptions` prose string, as item (iv),
and ESC-12 part (3) asks the lead to rule on it — so the ambiguity is disclosed.
What is not disclosed is that the answer **changes sign** across the windows the
pipeline already computes. Rolling the `alt2000m_45C` trace (seed 23) at
increasing window lengths and normalising on WS4's own model:

| window | corner radiator package [kW] | ratio @95 °C | ratio @105 °C | design-case crossover |
|---|---|---|---|---|
| peak (0.1 s) | 103.522 | **1.0884** | **1.0886** | 258.7 °C |
| 30 s | 103.522 | **1.0884** | **1.0886** | 258.7 °C |
| 60 s | 103.410 | **1.0872** | **1.0874** | 256.4 °C |
| 90 s | 94.702 | 0.9957 | 0.9959 | 156.0 °C |
| **120 s (exported)** | 86.129 | 0.9056 | 0.9057 | **116.1 °C** |
| 600 s | 63.746 | 0.6702 | 0.6703 | 135.0 °C |

The corner's instantaneous radiator peak, 103.5216 kW, is an **exact 8-way seed
tie** in the export — every seed of the corner reaches it — so the ≤ 60 s reading
is a property of the ensemble, not of one draw. On any window up to about 85 s the
ordered corner is **over** its ambient-normalised capability at every declared top
tank, and the design case does not change hands until 256–259 °C. The exported
120 s window is the first one at which the reassuring answer appears, and it is
the only one exported.

**Why it matters.** `all_cases_within_capability: true` is a set-wide capability
assertion with no window in its name, and it is the machine-readable form of the
sentence ESC-12 gives the lead — *"on the capability question the r2 conclusion
probably is right"*. That sentence is window-conditional in a way neither the field
name nor the escalation states. This is r2's KX2-M1 pattern one level down: the
prose is careful, the JSON summary is not, and the omission points toward the
standing ruling. The sweep's own declared method (ii) — "every exported field
whose name contains max/min/worst/median/penalty/paired" — does not cover a
boolean called `all_cases_within_capability`, which is why a workstream-wide sweep
did not catch a scope defect of exactly the kind it was run to find.

**Resolution.** Either put the window in the names
(`..._on_the_2min_window`, `design_case_crossover_top_tank_C_2min`,
`break_even_top_tank_C_2min`) and export the same aggregates for the peak and
10-min windows the ledger already carries, or export
`duty_over_capability_by_window_and_top_tank_C` as a two-axis table and let the
verdict be a max over both enumerated axes with R14 labels. Add the ≤ 60 s result
to ESC-12 part (3), because it is the answer to the question that part asks.

## R3-M2 — MATERIAL — the sensitivity's sea-level air temperature (21.006 °C) contradicts the same interface's declared ambient for the same cases (25.0 °C); on the second reading the crossover moves from 116.8 °C to 104.8 °C and the break-even from 158.4 °C to 139.5 °C

**What is wrong.** The R20 block derives each case's air temperature from the
case's own `rho_air` through the ideal gas law and exports:

```
ambient_normalised_sensitivity/case_air_temperature_C:
  nominal 21.00607037101554 / cda_5.4 21.00607037101554 / alt2000m_45C 44.95073916789022
```

The same interface block, ~200 lines earlier, states:

```
series_duty_v2/_inputs/r16_declared_cell_temperature_C: nominal 25.0, cda_5.4 25.0, alt2000m_45C 45.0
series_duty_v2/_inputs/r16_declaration_basis:
  "cell temperature declared equal to AMBIENT for each case; ..."
```

Both cannot be right. `r16_declaration_basis` asserts cells are declared equal to
ambient and then declares 25.0 °C for the two cases the R20 block computes at
21.006 °C. I verified the derivation is internally consistent with the vehicle
model (`rho_air` 1.1097 at sea level → 44.94 °C; 0.8706 at 2,000 m → 44.95 °C, so
the corner's validation is real), which makes the R16 block's 25 °C the outlier —
but the workstream now states two different ambients for the same ordered case and
neither block cross-references the other.

**Why it matters.** The crossover is the round's headline new number and it is
highly sensitive to exactly this input — about **−3 °C of crossover per +1 °C of
declared sea-level ambient**:

| sea-level ambient | design-case crossover | capability break-even |
|---|---|---|
| **21.006 °C (exported)** | **116.81 °C** | **158.42 °C** |
| 25.0 °C (the R16 block's declared ambient) | **104.82 °C** | **139.54 °C** |

ESC-12's argument turns on the claim that 116.8 °C is *"inside the range a
pressurised heavy-duty coolant system can actually run"* — a defensible but
edge-of-range statement. At 104.8 °C the same claim is not at the edge; it is
squarely inside ordinary heavy-duty HT operation, and ESC-4's design case would
read as clearly unsettled rather than marginally so. The unflagged inconsistency
therefore leans toward the standing ruling, the same direction as R3-B1 and
R3-M1. The declared-sensitivity block sweeps the top tank (the input the answer is
least sensitive to, ~0.001 of ratio across 30 °C) and does not sweep the case
ambient (the input it is most sensitive to).

**Resolution.** Reconcile the two declarations — either correct
`r16_declaration_basis` and `r16_declared_cell_temperature_C` to the model's own
21.006 °C, or state why the cells are declared 4 °C above the case ambient — and
add the case-ambient axis to the sensitivity, exporting the crossover and
break-even under both readings with the direction of the difference stated. (For
completeness and in WS4's favour: at 21 °C the R16 continuous acceptance is
~131.9 kW rather than 130.752 kW, so the declared 25 °C is marginally conservative
for the pack-charge exceedance, and nothing in ESC-8 turns on it — the peak
exceeds acceptance at every tabulated cell either way.)

## R3-M3 — MATERIAL — KX2-m1's tie-break remedy is a partial correction: 8 case-set governing labels in 19 exported occurrences are still Python first-key tie-breaks, two of them full three-case ties at exactly 0.0 — and both affected blocks are certified by the sweep

**What is wrong.** `_case_worst` is correct and I could not break it: it refuses
to name a governing case for a full tie and names all members of a partial one.
But it was not applied everywhere. Two hand-rolled label builders survive:

- **`_axis()`** (`run_ws4.py` ~line 1673): `worst = max(vals, key=lambda c: vals[c])`
- **`_R22D_GOV()`** (`run_ws4.py` ~line 2665): `worst = max(KX_CASES, key=lambda c: ...)`

Measured against the exported per-case values:

| field | per-case values | tie | exported label |
|---|---|---|---|
| `axes/pack_charge_above_r16_accept_s/mode_bp_companion/worst_case_max` | 0.0 / 0.0 / 0.0 | **full 3-case tie at 0.0** | "case **nominal** …; within it, seed 23" |
| `axes/engine_over_continuous_rating_s/mode_bp_companion/worst_case_max` | 0.0 / 0.0 / 0.0 | **full 3-case tie at 0.0** | "case **nominal** …; within it, seed 23" |
| `axes/pack_charge_peak_kW_bus/mode_b_block_of_record/worst_case_max` | 147.58458351650407 / 147.58458351650407 / 147.4734 | 2-case float-exact tie | "case **nominal** …" |
| `axes/engine_shaft_peak_kW/mode_b_block_of_record/worst_case_max` | 147.88445330896414 / 147.88445330896414 / 133.5956 | 2-case float-exact tie | "case **nominal** …" |
| `axes/engine_shaft_peak_kW/mode_bp_companion/worst_case_max` | 131.1465762318337 / 131.1465762318337 / 121.9277 | 2-case float-exact tie | "case **nominal** …" |
| `r22d_coast_spin_member/coast_no_regen_s_max` | 26.099999999976262 ×3 | **full 3-case tie** | "case **nominal** …" |
| `r22d_coast_spin_member/coast_spin_shaft_kWh_max` | 0.00017454623149206134 ×3 | **full 3-case tie** | "case **nominal** …" |
| `r22d_coast_spin_member/coast_spin_bus_kWh_max` | 5.839193136479234e-05 ×3 | **full 3-case tie** | "case **nominal** …" |

The three R22d ties are structural, not float accidents: the coast member is
scaled from the speed trace alone, so it is identical in all three cases by
construction. The two mode-(b′) zero ties are the *exact* pattern KX2-m1 named —
"`max(cases, key=...)` over three exact zeros is a first-key tie-break, not a
measurement" — and they sit in the block ESC-9 quotes.

Each of the 8 fields is exported 2–3 times (results, interface projection, and for
R22d also `spin_drag_operational_note_r22d`): **19 mislabelled occurrences**.

**Why it is material rather than minor.** Three things compound:

1. `§0-KX3` states the remedy is "produced by a single helper, `_case_worst`,
   applied to **every** case-set extremum in the workstream". That is false, and
   it is the kind of totality claim the lead is being asked to rely on when
   deciding whether the family is closed.
2. `§4-KX.9` states the sweep's method (iv) as "every extremum over an enumerated
   set checked for an R14 label **and for degenerate ties**". Two full degenerate
   zero ties survive in a block the same sweep certifies.
3. `construction_sweep_kx_r3 → examined_clean` certifies
   *"`companion_bp_capability_comparison.axes[*].worst_case_max` — CLEAN … with
   case and seed inline"*. The **value** is a true max; the **label** is the
   defect the round claims to have closed at source. And
   `r22d_coast_spin_member` is listed under `corrected`, so a reader concludes
   the whole member was swept.

By consequence alone this would be minor — no number is wrong, and the per-case
values sit beside every label. It is material because it falsifies the round's
central claim about itself, in the round that exists to close that claim, in the
workstream's fourth consecutive partial correction.

**Resolution.** Route `_axis()` and `_R22D_GOV()` through `_case_worst`, and add a
checker assertion that no `*_governing_case` naming a single case may be emitted
when the underlying per-case values contain a tie at the extremum. Correct the
`§0-KX3` and `§4-KX.9` totality sentences and the `examined_clean` entry for
`axes[*]`.

---

# MINOR

## R3-m1 — the sweep's certification of `make_report_ws4.py` arithmetic is false, and one rendered number divides by a hand-transcribed literal

`construction_sweep_kx_r3 → examined_clean` states: *"`make_report_ws4.py`
arithmetic — SWEPT. **Exactly three** expressions in the generator build a
rendered number from JSON: GAP and BSGAP … and M1PEAKPCT … Every other rendered
number is a format of a single JSON value, which `verify_ws4.py` pins."* There are
at least **seven**:

```python
"INTMIN": f"{OF['both_g1r']['delta_pp_min'] - OF['spin_drag_alone']['delta_pp_min'] - OF['map_vs_scalar_alone']['delta_pp_min']:+.2f}",
"INTMED": ...same on the medians...
"ALOCK":  f"{100*g('gate_g1/nominal/per_seed/23/a/locked_frac'):.1f}",
"AWR":    f"{g('gate_g1/nominal/per_seed/23/a/fuel_kg')*1e3/78.85:.0f}",
"BWR":    f"{g('gate_g1/nominal/per_seed/23/b/fuel_kg')*1e3/78.85:.0f}",
```

`AWR`/`BWR` (rendered as 247 and 241 g/kWh at the wheel in §4.3 and §10) divide by
a hard-coded **78.85**, which is a rounded hand transcription of
`chain_weighting_convention → series_duty_weighted → per_seed → 23 → wheel_kWh` =
78.85485355163588. The module docstring says the report is built "token
substitution, no hand transcription", and `verify_ws4.py` cannot pin a literal.
The numeric error is 0.006 % and the rows are archived G1 sanity checks, so
nothing turns on the value — but the certification is wrong and the transcription
is real. **Resolution:** read the denominator from JSON, and correct the
certification's count.

## R3-m2 — the sweep block miscounts its own enumerated set

`construction_sweep_kx_r3 → _reading` reads *"**five of the seven** corrected
entries are the findings the adjudication named"*, while the same block's
`corrected` map has **8** entries and `counts` says
`fields_corrected: 8, named_in_findings: 6, found_by_the_sweep: 2` (which is what
§0-KX3's prose and the §0-KX3 table also say, and which is correct). A
machine-readable summary that does not match its own enumerated set, inside the
block whose subject is machine-readable summaries not matching their construction.
**Resolution:** render `_reading` from `counts`.

## R3-m3 — the tie discipline stops at the case level: 562 seed-level extremum labels are first-seed tie-breaks, 322 of them on all-zero data

`_case_worst` handles case-set ties; `_sd_envelope`'s seed labels do not. Scanning
every ensemble against its own per-seed data (ordered, companion, all four
bracket/probe blocks): **562 exported `*_{min,max}_governing_case` fields name a
single seed where the extremum is tied**, of which **476 are full 8-seed ties** and
**322 of those are ties at exactly 0.0**. Examples:
`cases/nominal/ensemble/unserved_bus_kWh_max_governing_case = "seed 23 …"` on data
that is 0.0 on all eight seeds — while `unserved_energy_verdict` correctly refuses
to name a governing case for the identical data one level up. Also at the ledger
level: `engine_rejection_peak_kW` is an 8-way seed tie at cda_5.4 and a 5-way tie
at nominal, each labelled with one seed.

The round's totality claim is scoped to case-set extrema, so this is not falsified
by it — but the sweep's declared method (iv) says "every extremum over an
**enumerated set**", and the 8-seed ensemble is one. Pre-existing since r1 and not
raised in either prior round; no value is wrong. **Resolution:** apply the same
tie discipline in `_sd_envelope`, or state in the block that seed labels are
"a governing seed", not "the" governing seed.

## R3-m4 — three case-set maxima exported without an R14 governing case

`series_duty_v2/r16_pack_acceptance_bracket/fuel_penalty_pct_ratio_of_ensemble_maxima_max`
(0.2041717020260965),
`series_duty_v2/engine_continuous_rating_bracket/fuel_penalty_pct_ratio_of_ensemble_maxima_max`
(−0.05660754578494485) and
`construction_sweep_kx_r3/corrected/…/corrected_worst_max` (0.24877343356341006)
are maxima over the enumerated case set exported live in `interface_ws4` with no
governing-case sibling. The first two are deliberately retained superseded fields
carrying `_superseded_fields` notes, which is why this is minor; R14 does not
exempt them. Every other extremum field in the interface is labelled.
**Resolution:** label the three, or move the two superseded ones under a
`_superseded` sub-object.

## R3-m5 — the WS6 rows the block tells WS6 to size against are not inside the interface block

`interface_ws4 → coolant_loads_to_ws6` is the bare string `"see heat_ledger_ws6"`,
which points at a *sibling top-level key* of `results_ws4.json`, not into
`interface_ws4`. No radiator-package, engine-rejection or R20 field exists anywhere
inside `interface_ws4`. Program rule 2 makes the interface block the
machine-readable contract and rule 7 makes rejected heat a WS6 deliverable; the
one consumer that has not yet run is the one whose rows sit outside the contract.
Pre-existing and byte-identical since the r1 vintage, and the data is present,
rendered and pinned — hence minor — but this round restructured that ledger
substantially and R3-B1 turns on a row that would have gone there.
**Resolution:** project `heat_ledger_ws6` (or at least the per-case radiator rows
and the R20 comparison) into `interface_ws4`, and make the pointer a full path.

## R3-m6 — "every remaining interpolation asserts in range" is broader than the code

§0-KX3 states: *"Every remaining interpolation against a monotone branch now
**asserts in range before use** (`_r16_crossing`)."* `_r16_crossing` is used
twice, both on WS3's acceptance curve. The other nine `np.interp` calls that reach
an export — `_ACCEPT`, the pulse lookups, `accept_at_*`, the probe's `_acc`, and
the engine best-BSFC locus lookups in `series_hold_speed`, `v1_top_speed` and the
110 kW ledger point — do not assert. I checked each and none clamps on the shipped
inputs, so there is no measured consequence; the sentence is simply wider than the
remedy. **Resolution:** scope the sentence to the R16 curve, or apply an in-range
assertion generally.

---

## Notes for the lead (not findings)

1. **The `gate_g1_one_factor` restraint was correct, and for a better reason than
   the one given.** The round declined to recompute
   `gate_g1_one_factor.*.delta_pp_min` on the paired statistic, arguing that the
   name says "delta of the min", that `_DELTA_GOV` states the construction inline
   (it does — it names both endpoint seeds, 4 and 5, and says they differ), and
   that the values are BASELINE_v3-ratified record. All true. The stronger reason
   is arithmetic: the block's stated purpose is that *"the two deltas plus their
   interaction close to the full G1-R shift"*, and the G1-R shift of record is
   min-to-min. The archived construction closes exactly —
   6.261345943773722 + (−8.842990661729281) = **−2.5816447179555597**, the
   ratified ensemble-min to 15 digits — while the paired construction gives
   6.261346 + (−9.202903) = −2.9416, which is not the record's minimum and would
   not close. A difference of minima is the *right* statistic for an attribution
   of a min-to-min shift. R36 governs per-km claims on paired dispatches; this is
   neither. The paired companion (−1.8085 / −7.3213 pp) is measured outside the
   archive so the lead can see the size of the artifact, which is the correct
   handling. **No finding.**
2. **The R20 withdrawal and ESC-12 were the right call, not an over-correction.**
   WS4 measures duty; R20/ESC-4 is a capability ruling; rule 8 forbids
   self-resolution. Asserting a survival verdict on an unquantified scoping
   argument was r2's KX2-M1 and withdrawing it was correct. What is wrong is not
   the withdrawal but the replacement evidence base (R3-B1, R3-M1, R3-M2). The
   `absolute_kW_comparison` object, taken on its own, is exemplary: a real max
   over the enumerated set, the exceeding cases listed, the float-level tie
   disclosed and both members named, `all_ordered_cases_within_design_point_on_2min:
   false` stated plainly, and a `reading` that tells WS6 to size against the
   absolute rows and not against any boolean. Keep that object exactly as it is
   and fix the set it enumerates.
3. **Do the replacement exports give WS6 what it needs? Not yet.** WS6 gets:
   per-case radiator-package peak / 2-min / 10-min with governing seeds; the
   absolute comparison against 95.018 kW; a declared ITD sensitivity; and ESC-12.
   It does not get: R6's corner (R3-B1), any window other than 2-min in normalised
   form (R3-M1), a consistent case ambient (R3-M2), or any of it inside
   `interface_ws4` (R3-m5). The one thing WS4 correctly says it cannot supply — a
   radiator capability-versus-ambient curve — is correctly directed to WS6 in
   ESC-12 part (2).
4. **The escalations, on their merits.** ESC-8 is correctly restated: (b) is now
   the strongest true statement available from WS3's data and I verified it
   exactly; (c)'s "+0.20 % at most" is correctly withdrawn and replaced by the
   paired worst seed **+0.249 %** with its R14 label, and the note that the r2
   figure "carried the opposite sign to six of its own eight seeds" is
   independently confirmed (6 of 8 positive at nominal, exported ratio −0.0018 %).
   ESC-9 is correctly restated: the three "paired per-case median" renderings are
   now true of the number they label (+0.169 / −0.022 / +1.789 %), and the
   before/after (+0.062 → +0.169 % at nominal) is exact. ESC-10 is correctly
   restated on the union maximum **287.1 s** with both set maxima exported, the
   union case set fully enumerated, and the probe explicitly excluded from
   `series_duty_v2`'s case set — the KX2-m4 remedy is better than the finding
   asked for. ESC-11 correctly cites R34, declares WS4's reading as
   `[WS4-DECLARED]`, and offers a one-constant remedy. **None of the seven is
   self-resolved and none softens the choice it puts up.** ESC-12's
   characterisation is where R3-B1/M1/M2 bite: it correctly declines to rule, and
   the half of the evidence it presents is the half favourable to the standing
   ruling.
5. **What this round got right, recorded so it is not lost in a NOT-CLEAN
   verdict.** The KX2-M2 replacement is stronger than the finding asked for. The
   KX2-M3 correction is complete across all three blocks with paired envelopes and
   R14 seeds, and it moved the escalations rather than only the JSON. The archive
   freeze is exact to the r1 member set and key order. The "three values changed"
   claim is exact. The two sweep-found defects (`unbooked_pp_max`, ESC-10's
   percent-of-rating) are real defects of the named family, honestly reported
   including the fact that the second produced the right number by luck. The
   R22d re-pricing, the R6-family probe and the paired one-factor companion are
   all measurement added where the round could have argued instead.
6. **`ws4_sim.py` is byte-identical to the r2 vintage**
   (`de25e3da1fd2bb1ae5c8be3b590bd7f51c7cbba3143306957e0965b87a191632`), so no
   dispatch moved this round; every change is in the export and report layers.
   `results_ws4.json` changed and must be re-pinned by WS11 as the changelog says.
7. **Nothing in this round touches the archived G1 verdict** (0 values changed
   since r1) **or the F1–F5 errata**, all five of which I re-verified.

---

Key paths (absolute):
`/Users/valimenai/Documents/Project Volt/WS4_genset/results_ws4.json`
(R3-B1: `heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point` vs
`series_duty_v2 → r6_rating_family_probe → cases → r6_rating_corner_full`;
R3-M1/M2: `… → ambient_normalised_sensitivity` vs `series_duty_v2 → _inputs →
r16_declared_cell_temperature_C` / `r16_declaration_basis`;
R3-M3: `series_duty_v2 → companion_bp_capability_comparison → axes` and
`series_duty_v2 → r22d_coast_spin_member`;
R3-m1/m2: `construction_sweep_kx_r3 → examined_clean` and `_reading`),
`/Users/valimenai/Documents/Project Volt/WS4_genset/run_ws4.py`
(R3-B1 at the `_r20_rows`/`_R20_CASE_AMB_C` comprehensions over `KX_CASES` and at
the `r6_rating_corner_full` probe definition; R3-M1 at
`duty_over_capability_2min_by_top_tank_C` and `_r20_cross`; R3-M3 at `_axis()`
and `_R22D_GOV()`),
`/Users/valimenai/Documents/Project Volt/WS4_genset/make_report_ws4.py`
(R3-m1 at `INTMIN`/`INTMED`/`ALOCK`/`AWR`/`BWR`),
`/Users/valimenai/Documents/Project Volt/WS4_genset/REPORT_WS4.md`
(§0-KX3, §4-KX.7, §4-KX.9, §12 ESC-12),
`/Users/valimenai/Documents/Project Volt/WS4_genset/verify_ws4.py`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/data/trace_series_duty_v2_alt2000m_45C_seed23_10Hz.csv`
(the independent witness for the window sweep in R3-M1),
`/Users/valimenai/Documents/Project Volt/WS3_battery/regen_acceptance.csv`
(the independent witness for the KX2-M2 closure).
