# FINDINGS — WS4 (genset) — KX round, review round 2 (`FINDINGS_KX_r2.md`)

Adjudicator: fresh context, disk only, independent re-derivation. Judged
against **BASELINE_v5.md** (authoritative — R34, R36, and the R14/R9/rule-5/
rule-7 conventions carried from v2/v3), **BASELINE_v3.md** (R22, R23 — the
executed kill), `WS4_genset/KX_DIRECTIVE.md`, and **`FINDINGS_KX_r1.md`**,
read in full first. Artifacts read on disk as of 2026-08-31: `REPORT_WS4.md`,
`results_ws4.json`, `run_ws4.py` / `ws4_sim.py` / `ws4_chain.py` /
`ws4_models.py` / `make_report_ws4.py` / `verify_ws4.py`, `data/*.csv`
(including all three new 10 Hz traces), `run_output.txt`, prior rounds
`FINDINGS_WS4_r1/r2/r3.md`, plus the read-only WS1/WS2/WS3 imports and the
pre-rework artifacts at commit `b1c32cd` for the delta claims.

Scope as fixed by the lead: the R23 errata pins (F1–F5), the `series_duty_v2`
block, and interface consistency, widened by round 1's findings. **The G1
gate decision is not reopened** — it is an executed kill (BASELINE_v3
R22/R23) and `gate_g1` is treated only as an archived record block. I did not
re-establish byte-stability; the foreman's mechanical gate passed and I
confirmed `verify_ws4.py` exit 0 (231 renderings + interface block + 614
structural/errata pins) independently.

---

## Verdict

**NOT CLEAN. No blocking findings. Three MATERIAL, four MINOR.**

All thirteen round-1 findings are **closed at root cause**, and I could not
break any of them by re-derivation. The worker's central claim survives the
hardest test I could put to it: the KX-B1 correction really did add
measurement without moving dispatch, and it really is wired into the run —
I reproduced the new pack-side R16 counters, the new engine-over-rating
counters and the new transient-heat counters **from the committed 10 Hz
traces alone, with no simulator in the loop**, to full trace precision, on
all three ordered cases. The zero-unserved headline is invariant under every
bracket the worker built and under twenty further combinations I ran that
nobody has run before.

The three material findings are all **new defects introduced by the rework
itself**, all in the same family: a machine-readable summary field whose
construction does not match the quantity its name asserts, sitting next to
per-case data that is correct. In each case the report prose is careful and
the JSON summary is not — which is the mirror image of round 1's KX-M3, and
the reason none of them is caught by a checker that only pins renderings.
Two of the three feed live escalations (ESC-8, ESC-9) and one feeds the WS6
ledger and a live ruling (R20/ESC-4).

---

## Verification record — what I re-derived independently

- **V1 — full re-run of every ordered and bracketed configuration.** Rebuilt
  the run outside `run_ws4.py` from `ws4_models` / `ws4_sim` / `ws4_chain` +
  WS1's `volt_cycles`, reading WS3's usable-pack figure and the R16 curve
  from source rather than from WS4's JSON, and re-implementing `_sd_record`
  and `_sd_envelope` from the export contract. Ran **15 configurations**
  (3 cases × {ordered (b), companion (b′), R8 bracket, R16-pack bracket,
  engine-continuous-rating bracket}) × 8 seeds × 57 fields. **6,840 per-seed
  values and 4,275 ensemble fields: 0 mismatches**, all to exact float
  equality. Every governing-seed label re-derives by argmin/argmax.
- **V2 — the three R34 traces as independent witnesses of the NEW counters.**
  Recomputed, from the CSVs alone: `pack_chg_above_r16_accept_s` /`_kWh` /
  `_longest_s` (42.1 s / 0.157198 kWh / 14.0 s at nominal; 41.4 / 0.164756 /
  13.7 at CdA 5.4; 23.5 / 0.083453 / 11.4 at the corner), `pack_chg_peak_kW`
  (147.5056 / 147.5056 / 147.4733), `pack_dis_peak_kW`, both R8 exceedance
  counters, `engine_shaft_peak_kW` (84.6997 / 147.8845 / 133.5956),
  `engine_reject_peak_kW` and both rolling-window maxima, distance, SOC
  envelope, bus energy and engine-on time. **Every one matches the per-seed
  JSON to trace precision.** The B1/M1/m7 fixes are genuinely in the
  dispatch of record, not bolted onto the export.
- **V3 — first-principles closure on the new CdA 5.4 trace.** `shaft kWh +
  engine rejection = raw fuel energy` (109.218307 + 157.238106 = 266.456412
  vs 266.456391 from ∫ṁ·LHV, i.e. the trace's own print precision); the SOC
  delta from bus flows at 0.97/0.97 reproduces `soc_drift_kWh` exactly
  (0.252303); cycle generator efficiency 0.952866 and implied BSFC
  205.21 g/kWh reproduce the exported means. The books balance on a trace
  that did not exist in round 1.
- **V4 — the R16 curve, read straight from WS3.** Continuous acceptance
  130.752 / 129.144 / 95.048 / 62.203 kW at 25 / 45 / 50 / 55 °C and pulse
  204.173 / 200.553 / 200.151 / 128.786 kW all reproduce; the regen-leg
  crossings at −9.393220 °C and 53.949497 °C reproduce to seven digits.
- **V5 — three-way interface check.** The §11 fenced JSON block in
  `REPORT_WS4.md` is **byte-identical** to `json.dumps(results_ws4.json →
  interface_ws4, indent=1)`. `verify_ws4.py` exits 0. The 24-run SOC CSV
  reproduces `soc_window_check`'s `t_below_gate_s` envelopes exactly
  (290–435 / 825–975 / 175–185 s).
- **V6 — the "no value moved" claim, tested against `b1c32cd`.** Flattening
  both `results_ws4.json` vintages: **exactly 9 numeric values changed in the
  whole file**, all nine the m6 heat-ledger rows; **0 boolean changes**;
  8 string changes (6 heat-ledger labels, 2 copies of the `r16_binding_analysis`
  note); 330 removed keys, of which 328 are the `hysteresis_sensitivity_ref_seed`
  rename and 2 are the `bound_any_sample` rename. The changelog's claim is
  exact, including the sentence "every case ensemble, every per-seed ordered
  export, the unserved-energy verdict, the SOC-window check and the R8 bracket
  is byte-identical to the r1 vintage." The renamed hysteresis block preserves
  all 240 reference-seed fields with **0 diffs** under `cases → <case> →
  ref_seed`.
- **V7 — the m6 recomputation, re-derived.** Taking the maximum of each
  seed's own cycle average from my re-run: engine rejection 73.0407817618 /
  86.8727790093 / 59.9515546045 kW, generator 2.4548907097 / 2.8571153776 /
  2.0130639018, chain 4.2524638982 / 4.7560277897 / 3.8189555039 — matching
  the shipped rows to the last digit, with each component's governing seed
  independently confirmed (engine: 5 / 9 / 6; generator: 9 / 3 / 6; chain:
  5 / 5 / 5 — three different seeds in one row, which is exactly why m6 was
  raised).
- **V8 — the hysteresis sensitivity, re-run 8-seed.** Rebuilt WS3's allocated
  band from `WS3/results.json → soc_strategy` (3.5 kWh about 0.55 →
  0.39210918–0.70789082) and re-ran both bands × 3 cases × 8 seeds:
  **2,223 fields, 0 diffs**. Starts 6–6 / 6–6 / 9–9 (WS3 band) vs 5–6 / 4–4 /
  6–6 (simulator band); unserved 0.0000 on every seed of both bands.
- **V9 — the zero-unserved invariance, stress-tested well beyond the
  brackets.** Zero unserved on all 8 seeds under: ordered (b); companion (b′);
  R16 enforced on the pack; engine capped at its continuous rating. Then, on
  **five cases the ordered set does not contain** — the compound corner
  (CdA 5.4 × 2,000 m/+45 °C), the full R6 rating corner (+20 % payload,
  CdA 5.4, 4 kW aux, 2,000 m/+45 °C), aux 4 kW at nominal, aux 4 kW at
  CdA 5.4, and +20 % payload at CdA 5.4 sea level — under each of four
  dispatch configurations including **engine cap and R16 pack cap enforced
  simultaneously**: **0.0000 kWh unserved on every one of 160 runs**, worst
  SOC minimum 0.1174 of usable. KX-M1's headline-invariance claim is not only
  true, it is true under conditions nobody has asked for. Recorded for the
  lead as a positive result.
- **V10 — errata spot-checks.** F1: the phrase "4 of 8 seeds marginally
  positive" occurs exactly once in each of the four *places* the m5 pin now
  slices (headline, §0-R, §6 table, §12 ESC-2), and the superseded §0-R
  wording naming ESC-6 is absent. F3: 0.5148607848 pp and 0.6324177501 pp
  recompute from the exported member lists. F4/M2: `series_duty_v2 → _inputs
  → chain_of_record → map_file` resolves from the WS4 folder and its SHA-256
  matches `input_sha256`. F5: 78.85485355/86.08403730 = 0.9160217855.
  D5 (m2): the exported interpolated-envelope counts are 3.6–7.6 s nominal
  and 7.4–20.6 s at CdA 5.4 — the r1 adjudicator's published figures to the
  digit — with the rpm = 0 degeneracy (one feasible cell, ceiling 0.697 km/h)
  named and its 18.4–23.6 s share separated out.
- **V11 — wheel / shaft / bus discipline on the new counters.**
  `engine_over_continuous_rating_*` compares engine **shaft** power against
  `rated_cont_kw × derate` (shaft), and §2.1's R18 acceptance test is stated
  as "≥ 122.1 kW **shaft** sustained" — shaft-to-shaft, no conflation.
  `generator_over_continuous_input_s` compares generator **shaft input**
  against GEN-V2's 135 kW shaft-input rating. `pack_chg_above_r16_*` and both
  R8 counters compare **bus-side** pack power against bus-side limits from
  WS3's `*_kW_bus` columns. All four are clean.
- **V12 — the over-rating excursions are what the escalation says they are.**
  On the CdA 5.4 trace the engine sits at 147.83 kW **mean** through its
  155.9 s longest continuous excursion (p10 = p50 = p90 = 147.9 kW; 99 % of
  the excursion above 145 kW). ESC-10's "112 % for ~3 minutes" is literal,
  not a peak borrowed onto a longer window.
- **V13 — the archived gate.** 0 values changed, 0 removed; the archival
  notice, `status: executed_kill_2026-08-30` and the double-count warning are
  intact; the interface projection gained only 6 governing-case/note fields.

---

## Round-1 findings — closure status, one by one

| id | severity (r1) | status | basis |
|---|---|---|---|
| **KX-B1** | blocking | **RESOLVED at root cause** | Remedy (ii) taken in full and remedy (i) additionally bracketed. `bound_any_sample` is gone under that name and pinned gone; `regen_leg_bound_any_sample` (False) and `pack_charge_bound_by_r16_any_sample` (True) both exported; `_two_readings` states both readings and records that a choice exists; WS3's 10-s pulse column loaded and shown not to cover the excursions; per-seed pack-side counters with R14 envelopes on **both** (b) and (b′); `r16_pack_acceptance_bracket` prices enforcement; ESC-8 restated on the pack quantity with the 50 °C and 55 °C continuous *and* pulse values. Verified from the traces (V2). *Residual defect in the same block: KX2-M2 below.* |
| **KX-B2** | blocking | **RESOLVED at root cause** | `IFACE_BP_KEYS` gives the companion the full capability set; `companion_bp_capability_comparison` states five axes as explicit (b) vs (b′) verdicts with R14 governing cases and `within_limit_on_every_ordered_seed`; §4-KX.6 carries the rows; ESC-9 records the result without recommending. Every (b′) number re-derives (V1): discharge peak 115.6 vs 125, charge peak 100.2 vs 110, 0.0 s above R16-on-pack, 0.0 s above the continuous rating, on every seed of every case. *Residual: the fuel-delta statistic, KX2-M3.* |
| **KX-M1** | material | **RESOLVED at root cause** | `emerg_ceiling_kw` is a named, switchable quantity in the simulator and stated in §4-KX.1; the five counters ship per seed with R14 envelopes for both modes; §4-KX.3 carries the row beside the motor and pack rows; `engine_continuous_rating_bracket` confirms invariance; ESC-10 raised against R18/ESC-1 and not self-resolved. All numbers re-derived (V1, V2, V9, V12). *See KX2-m4 for the ordered-set bound.* |
| **KX-M2** | material | **RESOLVED at root cause** | `series_duty_v2 → _inputs → chain_of_record` carries map path (WS4-relative, resolves), owner path, voltage, feasible-cell count, reduction, WS2 round, bus nominal and the map SHA-256; `_inputs → boundary_convention_exposure` carries the convention's measured exposure for all three ordered cases with the D5 pointers; `verify_ws4.py` asserts the live block resolves without reading `gate_g1`. Confirmed by resolving the path myself. |
| **KX-M3** | material | **RESOLVED at root cause** | `_inputs → payload_metric_basis` carries `payload_basis_t` 2.9, `payload_basis_kg`, the WS1 source string, `payload_basis_is_preconversion: true`, `identical_in_all_ordered_cases: true` and an explicit `_caveat` naming the ÷2.9 identity and the R32/D13/R36 argument. ESC-7 restated on which curb the 2.9 t belongs to. Field kept rather than withdrawn, with the reason given. |
| **m1** | minor | **RESOLVED** | The hard-coded "i.e. they are launch samples" clause is deleted from `make_report_ws4.py`; §4.1 now renders the claim that survives from the data (the rpm = 0-column share, 0.697 km/h ceiling) and states explicitly that the 98.4 km/h rendering refuted the old clause. |
| **m2** | minor | **RESOLVED — D5 closed** | `boundary_exposure_strict_linear`, `nearest_col_is_degenerate` and `degenerate_rpm_columns` ship; `chain_boundary_exposure → d5_reconciliation` exports all four counts and the rpm = 0 share; §4.1, §8 F-9 and §9 D5 print both. Reproduces the r3 adjudicator's 3.6–7.6 s and 7.4–20.6 s exactly, and `unbooked_bus_kWh_linear` equality is stated, so no pp figure moves. |
| **m3** | minor | **RESOLVED for all eight named fields** | Labels present on `gate_g1/boundary_convention_exposure/nominal_one_sided_pp_max`, `chain_weighting_convention/series_duty_weighted/eta_bus_to_wheel_max`, the three `r22d_coast_spin_member` maxima **in both places they appear**, `gate_g1/verdict/margin_pct_ensemble_max` and all three `attribution_rows/*/delta_pp_min`. Verified by a whole-interface scan. *New residue introduced elsewhere: KX2-m2.* |
| **m4** | minor | **RESOLVED as far as a workstream may** | `_trace_files → r34_interpretation` declares the per-pipeline-run reading explicitly and marks it `[WS4-DECLARED]`; the trace header no longer asserts an unqualified "one per run"; three traces are emitted (one per ordered case); `R34_TRACE_ALL_ORDERED_RUNS` makes the alternative a one-constant change; the ambiguity is raised as **ESC-11**, not self-resolved. |
| **m5** | minor | **RESOLVED at root cause** | The §0-R sentence is reconciled with §0-KX's and says why; `verify_ws4.py` pins the F1 phrase **per section slice** (headline, §0-R, §6, §12-ESC, exactly 1 each) and additionally pins the superseded wording absent. A count is no longer doing a place check. Confirmed by locating all four occurrences. |
| **m6** | minor | **RESOLVED at root cause** | Each row is now the max of the per-seed cycle averages and each component carries its own governing seed; the superseded rows are retained as a literal at `series_duty_v2_cycle_average_kx_r1_superseded` with an `understatement_pct` block, so the before/after is rendered not transcribed. Independently re-derived (V7), including the three-different-seeds result. |
| **m7** | minor | **RESOLVED in substance** | Peak, 2-min and 10-min rolling maximum engine rejection are exported per case with R14 labels, plus radiator-package rows and an explicit R20 comparison block. Re-derived from the traces (V2). *The verdict field the remedy introduced is defective: KX2-M1.* |
| **m8** | minor | **RESOLVED at root cause** | Both bands now run the full 8-seed ensemble with R14 envelopes; the block is renamed and the r1 reference-seed rows are preserved bit-identically under `ref_seed`. Independently re-run: 2,223 fields, 0 diffs (V8). |

**On the two renames, judged for truthfulness.** Both are truthful.
`regen_leg_bound_any_sample` names exactly what the simulator enforces (the
cap sits inside the `pw < 0.0` branch and is applied to `p_rg_bus`), its
value is unchanged (False), and it is the correct answer to the regen-leg
question. `pack_charge_bound_by_r16_any_sample: true` is computed from the
measured per-case minima of `pack_chg_above_r16_accept_s` — i.e. it is True
because the exceedance is non-zero on **every seed of every case**, which
`verify_ws4.py` separately pins — and it is correctly paired with
`pack_charge_enforced_in_ordered_run: false`. `hysteresis_sensitivity` is no
longer a reference-seed block and the `_ref_seed` suffix would now be false;
the block is genuinely 8-seed and the reference-seed rows survive under a
sub-key. No downstream artifact in the tree (WS5, WS11) references either old
name, so the rename breaks nothing on disk.

---

# BLOCKING

**None.**

---

# MATERIAL

## KX2-M1 — MATERIAL — `r20_survives_on_the_2min_window: true` is a maximum over *one* case, exported beside a three-case worst that is 21 % above the design point it says is survived; the ambient scoping that would make it true is asserted, never measured

**What is wrong.** `run_ws4.py` builds the verdict as

```python
r20_survives_on_the_2min_window=bool(
    max(_r20_rows[c]["radiator_package_2min_max_kW"]
        for c in KX_CASES if c == "alt2000m_45C") <= _R20_DESIGN_KW)
```

The comprehension iterates the three-case set and then filters it down to a
single member. The result is a `max` over one element, written so that it
reads as a max over the enumerated case set. In the same object:

| case | radiator package, 2-min max [kW] | `exceeds_r20_design_point_on_2min` |
|---|---|---|
| nominal | 115.119 | **true** |
| cda_5.4 | 115.119 | **true** |
| alt2000m_45C | 86.347 | false |

with `r20_design_point_radiator_package_kW = 95.018`, `worst_2min_kW =
115.119` and `worst_2min_governing_case = "cda_5.4"`. A machine consumer —
and WS6, the cooling owner, is named in §4-KX.7 as the consumer of exactly
these rows — reads `r20_survives_on_the_2min_window: true` next to
`worst_2min_kW: 115.119` and `design point: 95.018` and has a flat
contradiction with nothing in the field names to resolve it.

**Why the scoping is not sufficient as it stands.** The `reading` string and
§4-KX.7's prose both scope the verdict honestly: `alt2000m_45C` is "the only
ordered case in R20's own +45 °C ambient", so the other two cases are not
apples-to-apples against a +45 °C-air capability figure. That argument is
reasonable — and it is **entirely unquantified**. R20/ESC-4 rules *which case
sizes the radiator*. To sustain "the R6 corner is still the design case" one
must show that no other case demands more capability **relative to its own
ambient**; WS4 instead compares absolute kW against a +45 °C number and
declines the comparison for the two cases that exceed it. WS4 exports no
radiator capability-versus-ambient model anywhere, so the step from "nominal
is at a cooler ambient" to "therefore R20 survives" is carried by assertion.
The gap is 115.1 kW of 2-minute duty against a 95.0 kW +45 °C design point —
21 % — and the direction of the unexamined assumption favours the standing
ruling.

**Why it is material and not blocking.** The per-case flags are exported
truthfully, the `reading` string states the scoping, and §4-KX.7's prose is
careful. Nothing is concealed from a reader who opens the block. What is
wrong is a single machine-readable verdict on a live ruling, whose name and
construction do not carry its scope, in the one block the report tells WS6 to
size against. I considered blocking and did not reach it, because the same
object contains the material that contradicts the field.

**Resolution.** Either (i) rename the field to carry its scope
(`r20_survives_on_the_2min_window_at_the_only_+45C_ordered_case`) and add a
sibling `cases_exceeding_design_point_on_2min: ["nominal", "cda_5.4"]` with
the explicit statement that WS4 has not compared them at their own ambients;
or (ii) export the ambient-normalised comparison that the R20 question
actually needs (required package duty ÷ available capability at each case's
ambient), and let the verdict be a real max over the three-case set with an
R14 governing case. Either way `worst_2min_kW`/`worst_2min_governing_case`
and the verdict must be over the same enumerated set.

## KX2-M2 — MATERIAL — `cold_side_binding_cell_C_pack_quantity: 10.0` is a `np.interp` right-edge clamp, not a crossing; on the pack quantity R16's continuous acceptance is exceeded at **every** tabulated cell temperature, and the field understates ESC-8 for the second round running

**What is wrong.** `interface_ws4 → series_duty_v2 → r16_binding_analysis`
exports, side by side:

```
cold_side_binding_cell_C                 = -9.39321930659508
hot_side_binding_cell_C                  = 53.9494966014262
cold_side_binding_cell_C_pack_quantity   = 10.0
```

The first two are genuine crossings of the regen peak (69.104 kW) with WS3's
curve, and I reproduce both to seven digits. The third is computed as

```python
float(np.interp(_pk_pack_chg, R16_P[R16_T <= 10.0], R16_T[R16_T <= 10.0]))
```

with `_pk_pack_chg = 147.58458351650407`. The cold branch of
`V2pack_chg_cont_kW_bus` runs 15.841 → **135.043** kW over −30 → +10 °C.
147.585 kW is **above the right edge**, so `np.interp` clamps and returns the
last abscissa, 10.0. It is not a crossing; there is none.

**Evidence.** WS3's whole curve, read directly:

| T_cell [°C] | −30 | −10 | 0 | 5 | **10** | 25 | 45 | 50 | 55 | 60 |
|---|---|---|---|---|---|---|---|---|---|---|
| cont [kW bus] | 15.841 | 66.985 | 101.483 | 118.573 | **135.043** | 130.752 | 129.144 | 95.048 | 62.203 | 0.000 |

The global maximum of the continuous column is **135.043 kW at 10 °C**. The
ordered run's peak pack charge is **147.585 kW**. Therefore
`147.585 > acceptance` at **every one of the 19 tabulated cell temperatures**,
with **12.542 kW** of exceedance even at the curve's most favourable point.
There is no cold-side boundary, no window, and no hot-side counterpart field
(which would clamp identically). The block also exports no
`hot_side_binding_cell_C_pack_quantity`, so the asymmetry hides the clamp.

**Why it matters.** This is the block whose round-1 blocking finding was that
a machine-readable field answered one of two questions and was read as
answering both, and whose round-1 diagnosis was that "**ESC-8 as written
understates its own case by roughly a factor of two**". The rework fixes that
and then re-introduces an understatement of the same kind at a smaller scale:
a consumer reading the pair of `cold_side_binding_*` fields will take the
pack constraint to have a non-binding region above 10 °C cells, exactly as
the regen-leg field has one above −9.4 °C. The truth available from the same
CSV is stronger and simpler than anything currently exported: **on the pack
quantity the ordered duty exceeds WS3's continuous acceptance at every cell
temperature WS3 publishes.** ESC-8 asks the lead to rule on which quantity
the curve limits; that sentence is the single most decision-relevant fact
about the pack reading, and it is not in the interface.

*(For completeness, and in the escalation's favour: the 10-s **pulse** column
does cover 147.585 kW between 0 °C and 50 °C cells — max 213.826 kW at 10 °C —
which is why `pulse10s_covers_the_excursions: false` correctly turns on
excursion **duration**, not on magnitude. That reasoning is sound and is
correctly stated.)*

**Resolution.** Withdraw or rename the clamped field, and replace it with the
measured statement: `pack_charge_exceeds_acceptance_at_every_tabulated_cell_C:
true`, `min_exceedance_kW_over_the_curve: 12.542`,
`least_binding_cell_C: 10.0` (the curve's maximum, labelled as such, not as a
boundary), and add the same sentence to ESC-8(b). If any interpolation
against a monotone branch is retained anywhere in this pipeline, assert
in-range before using the result — a clamp and a crossing must not share a
field name.

## KX2-M3 — MATERIAL — every fuel delta between paired dispatches in the new blocks is a ratio of ensemble statistics rather than the paired per-seed statistic BASELINE_v5 R36 mandates; one is *labelled* "the paired per-case median" in three places including ESC-9, one flips sign, and one understates its own "at most"

**What is wrong.** The ensembles are paired by construction — same eight WS1
seeds, same cycles, the two dispatches differing only in the supervisor — so
the paired per-seed delta is available at zero cost and is what the program
requires. **BASELINE_v5 R36**, a ratified doctrine correction, reads: *"The
former wording carried a ratio-of-medians artifact into doctrine. Per-km
claims are stated on the paired statistic only."* Three new exports ignore it,
and one of them claims to obey it.

**(a) `companion_bp_capability_comparison → fuel_kWh_per_km_by_case →
bp_penalty_pct_on_median` is a ratio of medians, described as paired.**

```python
bp_penalty_pct_on_median = 100.0 * (bp_ensemble["..._median"]
                                    - b_ensemble["..._median"])
                           / b_ensemble["..._median"]
```

`make_report_ws4.py` renders it three times — §4-KX.6, §8 and §12 ESC-9 — as
"**on the paired per-case median**". Measured, on `fuel_energy_kWh_per_km`:

| case | exported (ratio of medians) | **median of the paired per-seed deltas** | mean of paired |
|---|---|---|---|
| nominal | **+0.062 %** | **+0.169 %** | +0.088 % |
| cda_5.4 | −0.042 % | −0.022 % | −0.028 % |
| alt2000m_45C | +1.799 % | +1.789 % | +1.793 % |

At nominal the exported figure is 2.7× smaller than the statistic it is
called. The archived gate, by contrast, computes its margins per seed and
then takes the ensemble — `margin_b_vs_bp_pct=[100*(bp-b)/bp for bp, b in
zip(...)]` — so this workstream already has the correct construction in its
own code and did not use it in the new block.

**(b) `r16_pack_acceptance_bracket → fuel_penalty_pct_vs_ordered` is a ratio
of maxima, and it flips sign at nominal.**

| case | exported max/max | paired per-seed: min / median / max |
|---|---|---|
| nominal | **−0.0018 %** | −0.297 % / **+0.169 %** / +0.177 % |
| cda_5.4 | +0.2042 % | +0.147 % / +0.207 % / **+0.249 %** |
| alt2000m_45C | +0.0962 % | +0.067 % / +0.100 % / +0.138 % |

Two defects in one field. At nominal the export reads as a small *saving*
from enforcing the pack reading; paired, it is a cost on six of the eight
seeds and on eight of eight at both other cases. And `fuel_penalty_pct_max = 0.2042`, rendered in §4-KX.4 and in
**ESC-8(c)** as "fuel penalty **at most +0.20 %**", is not an upper bound: the
worst paired seed at CdA 5.4 costs **+0.249 %**. This is the *identical*
construction defect the same round just fixed in the heat ledger under m6 —
a maximum built from two independently maximised numbers is not the maximum
of the quantity — reintroduced in three new blocks by the same rework.

**(c) `engine_continuous_rating_bracket → fuel_penalty_pct_vs_ordered` is the
same construction.** Here the conclusion survives — paired, every seed of
every case is ≤ 0, so ESC-10's "fuel does not rise at all" holds — but
`fuel_penalty_pct_max = −0.0566` is a "max" over three negatives, i.e. the
*least* saving, exported under a name that says penalty.

**Why it is material.** These are machine-readable fields in a
`live_design_input` block, quoted verbatim into the two escalations the lead
is about to rule on. No verdict turns on 0.05 pp of fuel — which is why this
is not blocking — but R36 exists on the record precisely because a
ratio-of-statistics artifact once reached doctrine, and here one is not only
used but *named* as the statistic that was supposed to replace it.

**Resolution.** Compute all three on the paired per-seed delta and export the
8-seed envelope of that delta with R14 governing seeds
(`fuel_delta_pct_paired_{min,median,max}` + `_governing_case`); or keep the
ratio-of-statistics fields under names that say what they are
(`ratio_of_medians`, `ratio_of_ensemble_maxima`) and add the paired envelope
beside them. Correct the three "paired per-case median" renderings, and
restate ESC-8(c)'s "at most +0.20 %" on the paired worst seed (+0.25 %).

---

# MINOR

## KX2-m1 — the two new brackets label an all-zero tie as governed by `nominal`, where the block's own sibling correctly refuses to

`r16_pack_acceptance_bracket → worst_unserved_kWh: 0.0` /
`worst_unserved_governing_case: "nominal"`, and the same pair in
`engine_continuous_rating_bracket`, are produced by
`max(KX_CASES, key=...)` over three exact zeros — i.e. the label is Python's
first-key tie-break presented as a governing case. Ten lines away,
`unserved_energy_verdict → worst_case_governing_case` handles the identical
degeneracy correctly: *"no governing case - every ordered case is exactly
zero on all 8 seeds"*, and round 1 accepted that as the right form.
**Resolution:** use the degenerate-tie string in both brackets.

## KX2-m2 — R14 label residue, all of it in members added this round

The eight fields m3 named are labelled. Six new maxima are not:
`series_duty_v2/_inputs/boundary_convention_exposure/cases/*/exposure_s_motoring_min`
(three; the `_max` siblings in the same object are labelled — the same
asymmetry m3 was raised about, in the block the M2 remedy created), and
`heat_ledger_ws6/series_duty_v2_*_cycle_average/radiator_package_{peak,2min_max,10min_max,avg}_kW`
plus `pm_coast_spin_{shaft,bus}_kWh_per_cycle` (derived from labelled rows,
but exported as bare maxima). Separately,
`r16_binding_analysis → peak_pack_charge_governing_case` and
`peak_regen_governing_case` name a **case only** ("nominal",
"alt2000m_45C"), where the same block's other worst-case fields use the
program's fuller form "case X of the enumerated ordered case set {...};
within it, seed Y". **Resolution:** label the six, and bring the two
case-only labels up to the block's own convention.

## KX2-m3 — the ARCHIVED `gate_g1` block is not frozen: 240 new members leaked into it because the simulator gained fields

`results_ws4.json → gate_g1 → <case> → _raw_reference_seed → {a,b}` gained
every KX-r2 diagnostic (`eng_over_cont_s`, `emerg_ceiling_kw`,
`pack_chg_above_r16_*`, `eng_reject_roll*`, …) — 240 keys, 0 values changed,
0 removed. Two consequences. First, the commit message's "gate_g1 has zero
diffs" is true of values and false of members; the report's changelog does
not claim otherwise, so this is a record-hygiene point, not a false
statement in the artifact. Second, the archived block now carries
`gate_g1/nominal/_raw_reference_seed/**a**/eng_over_cont_s = 178.8` and
`cda_5.4/a = 221.5` — over-rating counters for **mode (a)**, the mode the
block's own notice says "does not exist in any live architecture" — measured
by a counter that did not exist when the gate was run. Nothing is exported to
the interface (only 6 governing-case/note fields were added there) and no
value moved, so the archive's evidentiary content is intact; but an archived
record that mutates whenever the simulator gains a field is not archived.
**Resolution:** freeze `_raw_reference_seed` to the member set of record
(project it through an explicit key list), or state in the archival notice
that raw dumps track the current simulator and only the named members are the
record.

## KX2-m4 — ESC-10's exposure is bounded by the ordered set, and a case one step inside R6's own sizing family is worse than the number the lead is asked to rule on

The escalation's headline is "worst **250.0 s** per cycle above the rating
(case cda_5.4 …)". That is a correct R14 maximum over the enumerated ordered
set and I reproduce it exactly. But R6 — the ruling that sets the 132 kW
rating in the first place — defines its rating basis as +20 % payload,
CdA 5.4, 4 kW aux, +45 °C, 2,000 m. Running mode (b) at cases drawn from that
family, which the directive did not order and nobody has run:

| unordered case | s/cycle above the continuous rating (8-seed max) |
|---|---|
| +20 % payload, CdA 5.4, sea level | **287.1** |
| aux 4 kW, CdA 5.4 | 268.1 |
| aux 4 kW, nominal | 157.7 |
| full R6 rating corner | 188.3 |
| ordered worst (cda_5.4) | 250.0 |

WS4 is compliant — the export is labelled as an ordered-set maximum and the
directive ordered three cases — but ESC-10 asks the lead to rule on whether
short excursions to the automotive curve are acceptable for a genset
installation, and the number in front of the lead is not the worst one
available inside the sizing corner's own family. (All of these still complete
with **0.0000 kWh** unserved, and with the engine capped at its continuous
rating the over-rating goes to 0.0 s everywhere — V9.) **Resolution:** one
sentence in ESC-10 stating that the 250.0 s is the ordered-set maximum and
that milder members of R6's own rating family reach ~290 s, or add the case
to the enumerated set.

---

## Notes for the lead (not findings)

1. **The rework's central claim is true and I tested it in both directions.**
   "No value inside `series_duty_v2` changed while a blocking finding about
   R16 was fixed" is not a contradiction here: the KX-B1 remedy the worker
   took is remedy (ii) — measure, rename, escalate — and the enforcement
   remedy (i) is carried as a *bracket* that runs beside the ordered case
   rather than replacing it. The new counters are pure diagnostics computed
   from `p_batt_raw` and `p_shaft_eng`, which is why dispatch does not move.
   That they are genuinely in the run, and not a decoration on the export, is
   established independently by V2: the 10 Hz traces — which are dumps of the
   dispatch loop, not of the export — carry the exceedances and reproduce
   every counter.
2. **The escalations, on their merits.** ESC-10 is correctly characterised,
   correctly cites the ruling it challenges (R18 / ESC-1 and the +0.82 kW
   corner margin, which is indeed a continuous-rating figure), correctly
   states that the headline does not depend on it, and is correctly not
   self-resolved; its one weakness is KX2-m4. ESC-11 is a clarification
   request, correctly cites R34, correctly declares WS4's reading as
   `[WS4-DECLARED]` rather than asserting it, offers a one-constant remedy,
   and asks the lead rather than deciding. ESC-8 and ESC-9 are correctly
   restated and correctly not self-resolved; ESC-8(c) and ESC-9's fuel figures
   carry KX2-M3, and ESC-8(b) is weaker than the data supports (KX2-M2).
   None of the four is self-resolved and none softens the choice it puts up.
3. **The zero-unserved headline is stronger than the report claims.** 160
   runs across five unordered cases and four dispatch configurations,
   including the engine held to its continuous rating and R16 enforced on the
   pack *simultaneously*, produce 0.0000 kWh unserved on every seed. The only
   configuration in which the duty fails is the R8 power-envelope bracket
   (0.519–0.613 kWh at `alt2000m_45C`), which is ESC-9 and is already on the
   record.
4. **The one place the ordered case set is genuinely the governing set.**
   The worst pack-discharge case (192.5 kW) is `alt2000m_45C`, inside the
   ordered set, for the reason round 1 gave: thin air keeps the genset off and
   leaves the pack covering transients. The compound corner is *milder* on
   every axis I measured (SOC minimum 0.290) because the derate keeps the
   engine running.
5. **A definitional inconsistency too small to be a finding.**
   `soc_window_check` reports `soc_usable_min` computed off the 5 s decimated
   trajectory (0.228684 / 0.183701 / 0.246044) while `cases[*].ensemble →
   soc_min_min` reports the full-rate value (0.228376 / 0.183345 / 0.245891)
   for the same runs — a 0.0002–0.0004 offset, in a block that declares
   `resolution_s: 5.0`. §4-KX.2 and §4-KX.3 print the two side by side without
   noting they are the same quantity at two sampling rates. Worth one word of
   cross-reference at the next artifact touch; nothing turns on it.
6. **Nothing in this round touches the archived G1 verdict**, which is
   unchanged in every value, or the F1–F5 errata, which the directive placed
   under checker verification and which the checker now pins per *place*
   rather than by count.

---

Key paths (absolute):
`/Users/valimenai/Documents/Project Volt/WS4_genset/results_ws4.json`
(KX2-M1: `heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point`;
KX2-M2: `interface_ws4 → series_duty_v2 → r16_binding_analysis →
cold_side_binding_cell_C_pack_quantity`; KX2-M3: the three
`fuel_penalty_pct_vs_ordered` / `bp_penalty_pct_on_median` fields),
`/Users/valimenai/Documents/Project Volt/WS4_genset/run_ws4.py`
(KX2-M1 at the `if c == "alt2000m_45C"` comprehension; KX2-M2 at the
`np.interp` against `R16_P[_cold_mask]`; KX2-M3 at `_r16b_fuel_pp`,
`_m1b_fuel_pp` and `bp_penalty_pct_on_median`; KX2-m1 at the two
`worst_unserved_governing_case` expressions),
`/Users/valimenai/Documents/Project Volt/WS4_genset/make_report_ws4.py`
(KX2-M3: `BPPENN`/`BPPENC`/`BPPENA` and the three "paired per-case median"
renderings),
`/Users/valimenai/Documents/Project Volt/WS4_genset/REPORT_WS4.md`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/verify_ws4.py`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/data/trace_series_duty_v2_cda_5.4_seed23_10Hz.csv`
(the independent witness for the KX-B1 and KX-M1 counters).
