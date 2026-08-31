# REPORT WS4 — GENSET, THE ARCHIVED GATE G1, AND THE R22a PURE-SERIES DUTY

Project Volt · workstream 4 · against **BASELINE_v3.md** (ratified
2026-08-30 — G1's kill EXECUTED; R22, R23) and **BASELINE_v5.md**
(ratified 2026-08-30 — R34 program hygiene). The gate sections below
were computed against BASELINE_v2.md and are **archived, not
recomputed**.
Author: WS4 (engine & generator). Status: **for adjudication — KX
round** per the lead directive `KX_DIRECTIVE.md` (rulings R22, R23).
KX changelog in §0-KX; the G1-R changelog (§0-R) and the round-2
changelog (§0) are retained as history.

**The clutch is dead.** BASELINE_v3 executed Gate G1's kill clause on
the numbers this report carries. Nothing in this round re-runs or
re-argues the gate: its margins reproduce bit-identically, the four
record-precision errata R23 ordered are corrected and checker-pinned,
and `interface_ws4 → gate_g1` is now an **ARCHIVED record block**
(`status: executed_kill_2026-08-30`) whose fields may not be consumed as live
requirements. The live V2 design input is the new §4-KX block,
`series_duty_v2`.

Everything below is produced by runnable code in this folder.
`./.venv/bin/python run_ws4.py` regenerates every number, map, table,
trace and figure in ~3 min (`pip install -r requirements.txt` into any
Python ≥3.12 venv first); `results_ws4.json` is the machine-readable
form; `make_report_ws4.py` generates this report with the Interfaces
block and every headline injected from that JSON; and `verify_ws4.py`
asserts that every headline number here matches `results_ws4.json`
verbatim — no *current* number is transcribed by hand, and the R23
errata carry their own checker pins (including an occurrence count, so
a corrected phrase cannot be corrected in only three of four places
again). (Historical values quoted in the changelogs — the r2 record and
the unreproducible r3-interim run — are quotations of the prior record;
the r3-interim margins are carried as a literal historical block in
`results_ws4.json` and rendered from it.) All stochastic inputs are
WS1's seeded cycle builders; extrema are 8-seed ensemble envelopes
(R9). WS1's, WS2's and WS3's folders are imported read-only, and every
consumed input is recorded by SHA-256 in `results_ws4.json →
kx_input_provenance → input_sha256` (and, for the archived gate,
`ws2_chain_of_record → input_sha256`).

> **KX headline (R22a): PURE SERIES V2 AT THE DELIVERED PACK COMPLETES
> EVERY ORDERED CASE WITH ZERO UNSERVED BUS ENERGY.** On WS3's
> delivered 11.08 kWh usable at the bus — not the R8 3.5 kWh
> floor the archived gate ran on — the pinned pure-series V2 follows
> VOLT-REG at nominal, at CdA 5.4 and at the 2,000 m/+45 °C corner on
> all eight seeds with worst-case unserved bus energy **0.0000
> kWh** (all cases zero: True; no governing case - every ordered case is exactly zero on all 8 seeds), against the
> 0.52 kWh the 3.5 kWh floor shed at CdA 5.4.
> ESC-5's energy-side buffer worry is **closed at the delivered pack**.
> Two things it does *not* close, both reported not tuned: the pack's
> bus-side **power** envelope is exceeded — discharge peaks to
> 192.5 kW against R8's 125 kW, and enforcing the envelope costs
> 0.613 kWh of unserved energy at the corner (§4-KX, ESC-9) — and
> the R3 motor rating is still exceeded, unchanged from the gate
> record. R16's cold curves are consumed and are **not binding** at any
> ordered (warm) case; the hot end is escalated (ESC-8). Fuel energy
> per km, above-pin duty, SOC trajectories, genset cycling and the
> per-seed tables are exported for WS5's R22b dispatch question.
>
> **Archived headline (Gate G1, decided): GATE G1 FAILED under the
> ruled conventions and BASELINE_v3 executed the kill. Recomputed per
> the G1-R directive (R12 chain convention + WS2's measured spin-drag
> member), the locked path with charge-bias load-point shifting now
> TRAILS pure series at the pinned BSFC point: margin -2.58% (ensemble
> minimum) / -2.50% (median) / -2.37% (max) at the nominal condition —
> the sign of the comparison is reversed, and the ≥5% kill criterion is
> missed by 7.58 points. The ensemble-minimum margin is negative at
> every tested condition; CdA 5.4 is break-even (min -0.09% / median
> 0.02% / max 0.12%, 4 of 8 seeds marginally positive —
> seeds 4, 7, 8, 9), every
> other condition is negative on all eight seeds. Attribution (§6): the
> R12 map-vs-scalar swap alone moves the margin -7.01 pp; the
> spin-drag member alone -1.77 pp. The sign is additionally
> bracketed against the one declared-not-measured genset member (§6):
> replacing the rectifier/conditioning model with a hostile 3%-class
> stage gives -0.79% min, and stacking WS1's full 3% stage on top —
> the most hostile defensible accounting — gives 0.09% min:
> break-even, still 4.91 points short of the criterion. **The kill
> outcome is invariant under every accounting.** Chain vintage: **WS2
> round-4 maps
> on the R10 bus (662 V nominal map) — the traction chain of record
> the directive names**; WS2 r4 landed mid-round and the directive's
> hot-swap pipeline consumed it (§0-R), and the verdict is insensitive
> to map voltage across WS2's full exported window (§6). The kill
> clause was armed at ≥5% on these numbers (BASELINE_v2); BASELINE_v3
> executed it. WS4 reported the number; the lead executed.**

---

## 0-KX. KX changelog (response to KX_DIRECTIVE.md — R22, R23)

The directive's scope is exhaustive and is executed exactly. **The gate
is not re-run or re-argued.** Its margins, ensembles, attribution rows
and bracket reproduce bit-identically under this round's code (the
prior-convention anchor assertion to 1e-9 still runs live, §10 check
9), and the only gate-side changes are the R23 errata and the
archival restatement of the interface block.

### R23 errata (directive item 1) — all five corrected and pinned

- **F1 (MATERIAL) — CdA 5.4 positive-seed count.** The data shows
  **4 of 8 seeds** positive (seeds 4, 7, 8, 9); the r3
  report said "two" in four places. Corrected in all four (headline,
  §0-R, §6 table, ESC-2). The count is no longer prose: it is computed
  in `run_ws4.py` for *every* condition and exported as
  `gate_g1/<case>/ensemble/seeds_margin_positive_n` +
  `seeds_margin_positive` with an R14 governing-case label, mirrored
  into `interface_ws4 → gate_g1 → verdict`. **Pin:**
  `verify_ws4.py` renders the count from JSON *and* asserts the
  corrected phrase occurs exactly four times and that the superseded
  wordings occur zero times — the failure mode was a partial
  correction, so the checker counts occurrences.
- **F2 (minor) — boundary-convention mode-neutrality.** The r3 claim
  ("mode-neutral and negligible") was true at the reference seed and
  false as a general claim. Exposure is now **measured per condition**
  by a counter in `ws4_chain.py` (`boundary_exposure`,
  `boundary_exposure_strict`) and the unbooked loss is **bounded** by
  extending the loss surface past each rpm column's feasible boundary
  with its own torque gradient (`boundary_excess_loss_kw`; copper loss
  goes as T², so the linear extension is a lower bound and a hostile
  2× row is carried). §4.1 is restated. **Pin:** the exposure
  envelopes and the one-sided pp bound are exported to
  `chain_boundary_exposure` and rendered; `verify_ws4.py` pins them
  and asserts the superseded wording is gone.
- **F3 (minor) — map-vintage spread.** Computed, not asserted:
  **0.51 pp** across the 432–749 V exported window and
  **0.63 pp** once the r3-interim figure the sentence's
  parenthetical swept in is included — the 0.63 pp the adjudicator
  read off the printed record. §4.2 now states both spans separately.
  **Pin:** `gate_g1_map_vintage_spread`, both fields.
- **F4 (minor) — traction-map path resolution.** The interface field
  now resolves against *this* workstream's folder like every other
  `*_file` field: `../WS2_traction_motor/data/effmap_motor_inverter_662V.csv`, with `map_file_owner` and
  `map_file_as_exported_by_owner` carried alongside. **Pin:**
  `verify_ws4.py` now resolves **every** `*_file` field in
  `interface_ws4` against the WS4 folder and fails if any is missing —
  a structural pin, not a one-off fix.
- **F5 (minor) — the 0.9005 chain figure's weighting.** Labelled:
  0.9005 is 0.97 × WS2's `eta_mot_avg`, energy-weighted over WS2's
  **i-MMD** VOLT-REG run. The **series-duty** companion — wheel energy
  ÷ bus energy through the same map over the full motoring trace — is
  **0.9160** (8-seed 0.9160–0.9165), giving **233.5 g/kWh**
  ideal series fuel-to-wheel against the 0.9005-weighted 237.6.
  §4.3 and §10 checks 3 and 5 are restated. The direction is
  confirmed: the r3 arithmetic *understated* the series advantage, so
  the imprecision leaned toward the clutch. **Pin:** both weightings
  and both fuel-to-wheel rates.

### R22a verification run (directive item 2) — §4-KX, `series_duty_v2`

Pure series V2 at the **delivered** pack (11.08 kWh usable at the
bus, read from WS3's own interface block at run time), three ordered
cases × 8 seeds, R16 cold curves consumed, R10 window, WS2 r4 maps, all
inputs SHA-pinned in `kx_input_provenance`. Unserved bus energy is
**0.0000 kWh** worst case. Exports: unserved energy, above-pin
duty (demand-side *and* engine-side), SOC trajectories (per-seed CSV +
figure + the 10 Hz trace), genset on/off and load-point cycling rates,
and fuel energy per km. Three checks WS4 added on its own initiative
because the ordered numbers rest on them (all labelled as such, D6):
the R8 **power**-envelope bracket, the SOC-window check against WS3's
declared discharge gate (both ESC-9), and WS3's allocated
genset-hysteresis band. A load-following companion (b′) is carried for
R22b; WS4 does not choose the dispatch.

### Escalations raised this round (§12)

- **ESC-7 (R32, D13/R36)** — the ordered metric is per km; R32's
  payload denomination for Vehicle Zero is not ratified. WS4 exports a
  payload companion and denominates no comparison on it.
- **ESC-8 (R16, R15, R2)** — R16's hot end crosses WS3's pack-loop
  sizing ceiling: at 55 °C cells the pack accepts less than this run's
  peak regen.
- **ESC-9 (R8 per R12/ES-4, R4/E24)** — the delivered pack has the
  energy, not the rated power, and the ordered run spends real time
  below the SOC band over which WS3 declares the discharge peak.

ESC-5's energy half is closed by this round; ESC-1 through ESC-6 are
otherwise unchanged or disposed by BASELINE_v3.

### Interface restatement (directive item 3)

`interface_ws4 → gate_g1` carries `status: executed_kill_2026-08-30`, an explicit
archival notice ("no field of this block may be consumed as a live
requirement"), and is reorganised into the four members the directive
names — **verdict**, **attribution_rows**, **bracket_result**,
**provenance_hashes** — with the map-vintage robustness and the F2/F5
errata blocks attached. Nothing previously exported was dropped. The
R22d spin-drag operational note is added as a named member,
`interface_ws4 → spin_drag_operational_note_r22d`, carrying WS2's
1,109 W shaft / 371 W bus point drag at 85 km/h, the
coast-without-regen condition, the WS5 guidance, this run's measured
exposure, and an explicit double-count warning.

### Program hygiene (BASELINE_v5 R34)

Complied with from this artefact: `data/trace_series_duty_v2_nominal_seed23_10Hz.csv` (66,143 rows at
10 Hz — WS1's builders integrate at 0.1 s, so the trace is native, not
resampled) plus `data/series_duty_v2_soc_trajectories.csv` for the per-seed SOC trajectories.

---

## 0-R. G1-R changelog (response to G1R_DIRECTIVE.md)

Scope executed exactly as directed; every previously reported gate
number is restated below with its old and new value. The prior-
convention configuration is retained in `results_ws4.json →
gate_g1_prior_convention` and is reproduced exactly by the refactored
code before the ruled corrections are applied — the legacy code path is
float-identical by construction and the nominal ensemble statistics are
asserted against the ratified r2 values to 1e-9 in `run_ws4.py` (§10
check 9) — so the entire G1-R shift is the two ruled corrections, not
code drift.

- **Directive 1a (R12 chain convention, both modes): DONE.** The G1
  traction chain is now WS2's measured inverter+motor map × the flat
  0.97 reduction, applied identically to modes (a), (b) and (b′); no
  scalar PE member exists on the traction side, and WS1's
  `part_load_factor` no longer touches any G1 quantity (the map *is*
  the part-load reality). The genset-side PE/rectifier lives in WS4's
  ledger as the explicit generator+rectifier loss model it always was
  (§2, restated on R10 per 1c). All cross-workstream electrical
  quantities are stated bus-side. **Line-111 exclusion-set removals
  documented in §1.**
- **Directive 1b (spin drag charged to case (a)): DONE.** WS2's
  exported member: 1.4851 kWh engine-side + 0.5017 kWh bus-side
  per VOLT-REG (round-4 vintage; WS2's r4 re-derivation at
  the R10 winding left the cycle-level member numerically unchanged
  from r3, so the directive's "expect the r4 value to differ" resolved
  to "it did not"). Charged to mode (a) during
  locked samples at the mean locked-time rates 1.153 kW shaft +
  0.390 kW bus, so each seed pays for its actual locked time
  (envelope actually charged: 1.458–1.495 kWh shaft,
  0.493–0.505 kWh bus). The r2 report's mode-neutrality claim
  (line 111) is **withdrawn** — WS2's measurement distinguishes
  unloaded lockup spin from loaded series operation.
- **Directive 1c (generator/rectifier on the R10 window): DONE.** Both
  generator specs restated on the pack-native window (662.4 V nominal,
  432.0–748.8 V operating, 777.6 V 10-s transient), 1200 V-class SiC
  rectifier devices (were 750 V-class at the superseded 370 V bus);
  loss-model coefficients carried unchanged at the new window
  [WS4-DECLARED, confirm at procurement]. **Pinned points re-placed and
  verified unmoved** (the restatement moves no loss coefficient;
  asserted in `run_ws4.py`).
- **Directive 2 (margins, same condition table, interface): DONE.**
  All six configurations recomputed (8-seed ensembles, R9); §6 table.
  Old → new (min/median): nominal **6.26/6.45 → -2.58/-2.50%**; CdA 5.4
  **8.22/8.36 → -0.09/0.02%**; aux 4 kW **6.46/6.63 →
  -2.25/-1.98%**; hot-alone **5.94/6.08 → -3.49/-3.31%**;
  2,000 m + 45 °C **3.75/3.92 → -5.90/-5.66%**; reference curve
  **6.58/6.76 → -2.23/-2.02%**. Kill criterion ≥5% nominal
  ensemble-min: **FAILS** (-2.58%). `interface_ws4 → gate_g1` exports
  the full condition set (F2 pattern), the convention, the chain
  vintage, the spin member and the one-factor rows; worst-case fields
  carry their governing case inline (R14).
- **Directive 3 (one-factor attribution): DONE.** Spin-drag member
  alone: margin 4.49% min (-1.77 pp vs the prior convention).
  Map-vs-scalar swap alone: -0.75% min (-7.01 pp). Together
  (G1-R): -8.84 pp. The map swap is the dominant correction; §6.
- **Vintage statement (directive preamble): the hot-swap contingency
  was exercised.** This round started on WS2's round-3 exports (370 V
  maps, the only ones on disk) with the pipeline built to hot-swap;
  WS2 r4 landed mid-round and a re-run consumed the 432/662/749 V
  maps and the r4 spin member automatically, with no code change. The
  gate of record above is the **r4 (662 V nominal-map) run**. For the
  record, the interim r3-vintage run read -2.98/-2.88/-2.74%
  (min/median/max) at nominal (before the deficit-fill correction
  below) — within ~0.4 pp of the r4 verdict, the same sign and the
  same kill outcome, consistent with the map-vintage robustness rows
  in §6. Those figures are carried as a literal historical block in
  `results_ws4.json → gate_g1_interim_r3_vintage_record`: they are NOT
  regenerable, because WS2 r4 replaced the 370 V exports on disk.
- **Pre-adjudication adversarial pass (WS4-initiated, disclosed §9):**
  before launching the adjudicator, three independent adversarial
  reviews were run against this delivery. The physics review could not
  refute the reversal (map lookups verified against the CSV's own
  P_dc/P_shaft identities in both quadrants; regen through the chain
  reproduces WS2's exported 3.73 kWh to the last digit; an independent
  reconstruction reproduces the −7.0/−1.8 pp decomposition). Three
  real defects it and the consistency review found are fixed in this
  revision: (i) a spin-vs-map no-load **double-count** on locked
  torque-fill samples overcharged mode (a) by ~0.03–0.06 pp — fills
  now use the marginal map loss (loss(rpm,T) − loss(rpm,0)) when the
  spin member is active, moving the nominal margin -2.58% (was −2.67%
  before the fix); (ii) the "conservative boundary-loss" claim
  conflated R3 over-*rating* exposure with map over-*envelope*
  exposure — corrected in §4.1, where the r3 round then claimed the
  convention was "mode-neutral and negligible". *KX/R23-F2 corrects
  that replacement claim in turn: it is mode-neutral at the reference
  seed only, and one-sided in mode (b)'s favour at CdA 5.4 — measured
  and bounded in §4.1.*; (iii) categorical
  "sign reversed everywhere" language overstated the CdA 5.4 ensemble,
  which is break-even. *KX/R23-F1 corrects that replacement claim in
  turn: the r3 round printed "two" where the data has 4 of 8
  seeds marginally positive (seeds 4, 7, 8, 9) — corrected in the
  headline, §6, ESC-2 and ESC-6.* Additionally the sign's
  dependence on the declared rectifier member is now bracketed
  in-pipeline (§6): the kill outcome is invariant.
- **Directive 4 (R18 datasheet confirmation task): DONE.** §2.1 states
  precisely which 4HK1-V2C figures require procured-datasheet
  confirmation and the witnessed dyno test that substantiates the
  132 kW flat-rating if the datasheet is silent; exported at
  `interface_ws4 → v2_genset → r18_datasheet_confirmation`.
- **Secondary restatements** (all consequences of the two ruled
  corrections): reference-seed fuels (a) 19.41 → 19.51 kg, (b) 20.72 →
  19.04 kg; (a) banking envelope 1.5–3.3 → 2.3–3.0 kWh;
  (b) emergency load-follow 484–805 → 505–631 s nominal and
  1,504–1,734 → 1,128–1,400 s at CdA 5.4; (b) unserved energy
  ≤0.12 → 0.00 kWh at nominal (the R12 chain lets pure series
  complete the nominal cycle cleanly) and 0.46–0.77 →
  0.00–0.52 kWh at CdA 5.4; G1(a) ledger row §7. Unchanged
  (trace-determined): (b) over-rating exposure 42.1–71.5 s
  nominal / 110.4–137.5 s CdA 5.4; (a) exposure 0.0 s.
  Unchanged (outside G1-R scope, ratified r2 record): candidates and
  the R6 corner (+0.82 kW PROVISIONAL), BSFC maps and pinned points,
  V1 start-stop, grade holds, heat-ledger seeds (except the G1(a)
  cycle-average row, which is a gate quantity).

## 0. Rework changelog (round 2 — response to FINDINGS_WS4_r1.md)

*(Historical — retained verbatim from the ratified r2 report; the gate
numbers it re-affirms are superseded by §0-R above.)*

Adjudication round 1 returned no blocking findings, two material (F1,
F2) and five minor (F3–F7): F1 ESC-5's unsupported 1.9 kWh withdrawn
(verified 0.77 kWh worst-seed); F2 the interface now exports the full
gate condition set; F3 findings-register envelopes restated per R9;
F4 standalone hot-day case added; F5 R6 corner margin labeled
PROVISIONAL; F6 two prose/data drifts fixed; F7 rating-exposure counter
extended to locked torque-fill and `run_output.txt` made byte-stable.

## 1. Assumptions

| Assumption | Value | Basis |
|---|---|---|
| Genset rating basis | **engine shaft** power, everywhere | E15 pinned down; the conservative reading, and the one WS1/R6 used (107.8/122.1 kW are shaft figures) |
| Fuel | diesel, LHV 42.8 MJ/kg, 832 g/L | EN590 class values |
| BSFC maps | **WS4-CONSTRUCTED Willans-line maps, not measured** | no public measured map exists for these exact calibrations; construction in §3, every coefficient declared in `ws4_models.py`, calibration anchors in §10 |
| **G1 traction chain (R12)** | WS2 measured inverter+motor map (`data/effmap_motor_inverter_662V.csv`, 662 V, WS2 round 4 — the R10-window chain of record) × flat 0.97 reduction, both directions, both modes; **no scalar PE member, no `part_load_factor`**; demands beyond the map's feasible envelope reuse the boundary loss (exposure measured per condition under KX/R23-F2: mode-neutral at the reference seed, one-sided by at most 0.0158 pp in mode (b)'s favour at CdA 5.4; §4.1); locked torque-fill at marginal map loss when the spin member is active (§4.1) | R12 + G1-R directive 1a; the loader keys on WS2's exported nominal bus voltage, so any future WS2 re-export hot-swaps on re-run |
| **PM spin drag (G1-R)** | 1.153 kW shaft + 0.390 kW bus charged to mode (a) while locked (WS2 export 1.4851 + 0.5017 kWh per VOLT-REG, round-4 vintage) | directive 1b; WS2 measured, lockup-only tax |
| Part-load derates (non-G1 sections) | WS1's ratified `part_load_factor` retained for the ratified r2 capability/V1 sections (V1 start-stop, grade holds, top speeds — outside G1-R scope); WS4 loss-model maps for both generators; load-dependent direct-path model (2.8% proportional + 0.9·(rpm/1800) kW churning) | R9; bounded rework — those numbers are ratified |
| Generator parasitic | crank-mounted PM generator spins whenever the engine spins: 1.2 kW iron/windage at 1,800 rpm charged to the engine in lockup even at zero output | topology consequence, part of the honest locked-path cost |
| Battery — archived gate | 0.97/0.97 per direction; usable 3.5 kWh (V2) / 1.5 kWh (V1) at the bus — the R8 floors; banking limited to 50 kW continuous charge (R2/R8) | WS1 convention + R8 |
| **Battery — KX/R22a run (§4-KX)** | same round-trip efficiencies; usable **11.083608 kWh at the bus**, WS3's DELIVERED 288s1p pack, read from WS3's interface at run time; regen-to-pack capped by WS3's R16 acceptance curve at a declared cell temperature per case; R8's bus-side power envelope measured and reported, **not** enforced (bracketed separately, §4-KX.3) | R22a + R16 + WS3 `interface_WS3.packs.V2` |
| Engine start costs | series start = 12 g; lockup re-engagement = 1.5 g (motor-synchronised bump start) | declared; identical rules in every G1 mode |
| Supervisor (WS5 preview) | causal, deterministic, tuned once, identical across seeds/modes: series start-stop hysteresis 35–75% SOC; emergency load-follow below 25% SOC; charge-bias band 55–65% SOC; lockup 65±3 km/h, clutch opens on negative wheel power | §4.1 |
| Cycle basis | VOLT-REG at GVW, 10 Hz, WS1 seeds [23,3–9]; VOLT-SUB seeds [11,3–9]; demand traces fixed, loads recomputed per sensitivity | R9 |
| Derate model | turbo+CAC diesel: none to 1,000 m then 4%/1,000 m; none to 30 °C then 1%/5 °C ⇒ factor **0.9312** at the R6 corner | class-typical ISO 3046 / SAE J1349 practice, WS4-DECLARED; **R18 blocker — §2.1** |
| Engine heat split | of (fuel − shaft): exhaust 49%, coolant+oil 38%, CAC 10%, radiation 3%; radiator package = 48% | class-typical MD diesel balance, WS4-DECLARED |
| Candidate data | production-engine figures are datasheet-class values; to be confirmed at procurement | public sources, flagged TBC; §2.1 |

**Exclusion set, restated per directive 1a (the r2 report's line-111
list shrinks; each removal documented):**

- **REMOVED — "motor spin drag at zero torque"**: now *included*,
  charged to mode (a) from WS2's measured export (directive 1b; rates
  above). The r2 parenthetical "nearly identical in both G1 modes" is
  **withdrawn** — WS2's measurement shows it is a lockup-only tax
  (unloaded spin ≠ loaded series operation), worth -1.77 pp of gate
  margin on its own (§6).
- **REMOVED — "absent from the WS1 chain convention" (the framing)**:
  moot; the WS1 scalar chain convention itself is superseded by R12
  for every G1 quantity. The traction-side scalar PE member is gone
  program-wide; the genset-side rectifier/conditioning is explicit in
  WS4's generator model and ledger.
- **Remaining exclusions (unchanged, disclosed)**: transient thermal
  states (warm engine assumed; cold-start penalties would hit both G1
  modes roughly equally but hurt V1 start-stop specifically, §5);
  DPF-regeneration fuel.

## 2. Candidates and selection

*(Ratified r2 record — unchanged by G1-R; retained for completeness.)*

Derate math to the R6 corner (45 °C, 2,000 m): every continuous rating
is multiplied by **0.9312** (altitude 0.96 × temperature 0.97). The
corner requirement is **122.1 kW shaft** (R6, locked).

### V2 (125 kW floor, R6)

| Candidate | Disp. | Peak | Continuous (SL) | At R6 corner | Margin | Mass (dry) |
|---|---|---|---|---|---|---|
| 4HK1-TC stock reference | 5.19 L | 153 kW | 130 kW | 121.1 kW | **−1.0 kW** | ~500 kg |
| **4HK1-V2C (SELECTED)** — 4HK1-TC genset recalibration | 5.19 L | 153 kW | **132 kW** | **122.9 kW** | **+0.82 kW** | ~500 kg |
| Cummins B4.5-class (downsized-from-stock) | 4.5 L | 168 kW | ~129 kW | 120.1 kW | −2.0 kW | ~390 kg |
| Isuzu 4JJ1-class (examined) | 3.0 L | 130 kW | ~110 kW | 102.4 kW | −19.7 kW | ~350 kg |

**Selection: 4HK1-V2C** — the donor's own production 4HK1-TC hardware
with a genset/continuous recalibration: continuous rating 132 kW @
2,200 rpm, torque curve reshaped to peak **750 Nm @ 1,400 rpm** (E3's
requirement made a specification — the only curve of WS1's four that
holds 6% on the direct path). Compliance status: **PROVISIONAL**
(adjudication r1 F5; R18) — the +0.82 kW corner margin rests on two
TBC figures; see §2.1. Selection reasoning unchanged from r2.

### 2.1 R18 datasheet-confirmation task (directive 4)

R18 holds two blockers on WS6 release: this confirmation and G1-R
itself. Precisely, the figures on the **4HK1-V2C** requiring
procured-datasheet confirmation are:

1. **BLOCKING — the 132 kW continuous flat-rating** @ 2,200 rpm as an
   unlimited-hours prime/COP-class rating (ISO 8528-1 / ISO 3046-1
   basis, no 10%-overload dependency). The published 4HK1-TC figures
   are automotive (153 kW peak / ~130 kW continuous-class); the 132 kW
   continuous is a WS4-proposed genset recalibration and appears on no
   public sheet.
2. **BLOCKING — the derate model in corner-delivery form** (R18's own
   label): the datasheet must state either "no derate to 2,000 m /
   +45 °C" or its derate curve. WS4 assumed 4%/1,000 m above 1,000 m
   and 1%/5 °C above 30 °C (factor 0.9312 ⇒ 122.9 kW delivered). The
   +0.82 kW margin flips if the confirmed rating is 1 kW lower or the
   slope 1%/1,000 m steeper (r1 F5).
3. Non-blocking (affect G1 margins, not the WS6 release): the 750 Nm @
   1,400 rpm torque respec on production hardware (E3); the
   Willans-constructed BSFC surface (island 203.6 / rated-continuous
   215.4 g/kWh — the gate is re-runnable on a measured map in this
   pipeline); the 10.7 kW motoring-drag anchor; the 49/38/10/3 heat
   split; ~500 kg dry mass.

**Test substantiating the 132 kW flat-rating if the datasheet is
silent** (witnessed, per ISO 3046-1 with corrections per ISO 15550 /
SAE J1349): (i) sea-level leg — 132 kW @ 2,200 rpm held continuously
to thermal steady state (coolant/oil dT/dt < 1 K per 10 min, ≥ 4 h),
fuel stop untouched, smoke/EGT/boost/coolant inside the manufacturer's
continuous limits; (ii) simulated-corner leg — inlet conditions set to
2,000 m / +45 °C equivalents (~79.5 kPa inlet depression + 45 °C cell,
or an altitude chamber), same fuel stop, acceptance = **≥ 122.1 kW
shaft sustained to steady state** (the corner-delivery form is the
requirement; the label is not the test); (iii) a third point at
~1,000 m equivalent to pin the two derate coefficients separately.
Exported machine-readably at `interface_ws4 → v2_genset →
r18_datasheet_confirmation`.

### V1 (~50 kW class, R5)

*(Unchanged r2 record: V3307-V1C selected, 76.5 km/h charge-sustain —
inside R5's sub-80 ruling; now also R18's V1 figure of record.)*

### Generators (restated on R10 — directive 1c)

Both are crank-/genset-mounted IPM PM synchronous machines with active
**SiC rectifiers on the R10 pack-native window: 662.4 V nominal,
432.0–748.8 V operating, 777.6 V 10-s transient, 1200 V-class devices**
(were 750 V-class at the superseded 370 V bus). Per R12 this
genset-side rectifier/conditioning stage lives in WS4's ledger — it is
the explicit loss model in the exported maps (iron+windage ∝ speed,
copper ∝ T², rectifier 1% + fixed), not a scalar; no PE member exists
on the traction side. Loss coefficients are carried unchanged at the
new window [WS4-DECLARED: at this fidelity the voltage change trades
conduction current for switching stress roughly evenly across a rewound
machine + 1200 V SiC stage; confirm at procurement].

- **GEN-V2 "IPM 135"**: 135 kW continuous shaft input, 155 kW peak,
  ~90 kg, η = 0.952 at the pinned series point, 1.2 kW spin loss at
  1,800 rpm. Doubles as the engine starter (ISG). `data/gen_eff_map_V2.csv`
- **GEN-V1 "IPM 60"**: 60 kW continuous input, 70 kW peak, ~48 kg,
  η = 0.939 at the pinned point. Doubles as the starter. `data/gen_eff_map_V1.csv`

**Pinned points re-placed under the restated spec: unmoved** — the
restatement changes no loss coefficient, so the re-derived points land
on the ratified coordinates (asserted in `run_ws4.py`; would move only
if procured rectifier data changes the model).

## 3. BSFC maps and operating points

*(Maps and pinned points unchanged from the ratified r2 record.)*

Three maps are published, all **WS4-CONSTRUCTED Willans-line maps**:
`data/bsfc_map_4HK1_ref.csv`, `data/bsfc_map_V2_candidate.csv`,
`data/bsfc_map_V1_candidate.csv`. Construction: η_b = η_i0 · f_N(rpm) ·
f_φ(load) · BMEP/(BMEP+FMEP), BSFC = 84.11/η_b; anchors in §10.

| Map | Island minimum | At rated continuous |
|---|---|---|
| 4HK1 reference | **205.2 g/kWh** @ 1,403 rpm / 583 Nm | — |
| 4HK1-V2C (candidate) | **203.6 g/kWh** @ 1,288 rpm / 628 Nm | **215.4 g/kWh** @ 2,200 rpm |
| V3307-V1C | **228.7 g/kWh** @ 1,301 rpm / 217 Nm | 249.3 g/kWh @ 2,200 rpm |

### Fixed series operating points (task 4)

- **V2 pinned point: 1,288 rpm / 628 Nm / 84.7 kW shaft → 80.6 kW at
  the bus, BSFC 203.6 g/kWh** — the map minimum, inside the 132 kW
  continuous rating; re-placed unmoved under the R10 rectifier
  restatement (§2).
- **V1 pinned point: 1,301 rpm / 29.5 kW shaft → 27.7 kW at the bus,
  BSFC 228.7 g/kWh** — also the map minimum.
- **Locked-path residency** (fig. 1): rpm welded to road speed,
  1,414–2,005 rpm p05–p95, median 48% load. The fuel-weighted
  effective BSFC of mode (a) over VOLT-REG is 221.9–223.3
  g/kWh (now inclusive of the spin-drag energy) — a 9–10% penalty vs
  the pinned island. **This is E20's question answered with a map, and
  under the ruled chain it is fatal: §4.3.**

## 4. GATE G1-R — the direct path on trial under the ruled conventions

### 4.1 What was compared

Both modes drive the identical VOLT-REG wheel-power trace (WS1
four_numbers convention), same battery (3.5 kWh usable), same start
rules, 8 seeds ([23, 3–9]), and — per directive 1a — the identical R12
traction chain: **WS2's measured inverter+motor map
(`data/effmap_motor_inverter_662V.csv`, 662 V, WS2 round 4) × the flat 0.97
reduction, both directions, no scalar PE member, no part-load scalar.**
Two boundary conventions, stated precisely (corrected in the G1-R
revision — the earlier draft conflated them; the first is restated
again here under KX/R23-F2): demands beyond the map's *feasible
envelope* reuse the nearest boundary loss. **That convention is
mode-neutral at the reference seed only, and it is one-sided in mode
(b)'s favour at CdA 5.4** — the r3 wording ("mode-neutral and
negligible") is withdrawn. Measured, per condition, by a counter in
`ws4_chain.py` over the identical (rpm, torque) coordinates the loss
lookup queries: at **nominal**, exposure is 22.7–31.3 s/cycle
(18.9–24.5 s on the stricter outside-the-envelope test), of which
22.2–28.2 s are *unlocked* samples both modes drive identically and only
0.0–6.0 s are locked; the exposed samples top out at 98.4 km/h,
i.e. they are launch samples. At **CdA 5.4** exposure rises to 27.8–46.4
s/cycle (24.0–39.3 s strict) with 4.8–23.1 s of it on *locked* ~94–98
km/h cruise samples reaching 98.5 km/h — samples mode (a) serves on
the engine and mode (b) serves through the clamped chain, so the
convention flatters pure series there. Bounded: at most 1.1362 kWh
of over-boundary wheel energy, worth **0.0079 pp** of mode (b)'s
cycle fuel (0.0158 pp on a hostile 2× loss gradient) at CdA 5.4 and
0.0013 pp at nominal — an order of magnitude below the ~0.05 pp the
directive characterised it as, itself two orders below the 7.58-point
shortfall, and pointing the way the r3 conclusion already pointed.
Full tables: `results_ws4.json → chain_boundary_exposure`. WS4's count
is larger than the r3 adjudicator's independently measured 3.6–7.6
s/cycle at nominal; the two use different boundary criteria and WS4's
is the more inclusive, so its pp bound is the conservative one (D5).
Separately, the R3
over-*rating* counter (>150 kW motor shaft) fires 42.1–71.5 s
per cycle in mode (b) (mode (a): 0.0 s) — those samples lie
*inside* the map envelope (feasible to ~175–185 kW at cruise rpm) and
receive true interpolated losses; they stay energy-bookkept, not
clipped. During locked torque-fill, the fill uses the *marginal* map
loss (loss at fill torque minus no-load loss), because the spin-drag
member already charges the machine's no-load losses on those samples
(double-count fix, §0-R/§9). The genset side of both modes is WS4's
generator+rectifier model (R12; restated on R10, §2; sign-bracketed
in §6).

- **(a) locked + charge-bias load-point shifting** — locked 2.8:1 path
  above 65±3 km/h, rpm welded to road speed; charge-bias banking up to
  the min-BSFC torque (≤50 kW at the bus, R2/R8); series pinned-point
  start-stop when unlocked; clutch opens on negative wheel power.
  **Now also carries WS2's measured PM spin drag while locked
  (directive 1b): 1.153 kW shaft + 0.390 kW bus** — per cycle
  that is 1.458–1.495 kWh engine-side + 0.493–0.505
  kWh bus-side across seeds (WS2's export scaled by each seed's actual
  locked time).
- **(b) pure series at the pinned best-BSFC point** — 84.7 kW shaft /
  80.6 kW bus at 203.6 g/kWh, SOC-hysteresis start-stop; below 25% SOC
  the engine load-follows up to the full-load curve (D2's correction,
  unchanged).
- **(b′) series load-following along the best-BSFC locus** — robustness
  check on (b), not the G1 metric.

### 4.2 Result

**Net fuel energy over VOLT-REG, (a) vs (b), 8-seed ensemble: (a)
TRAILS (b) by -2.58% (min) / -2.50% (median) / -2.37% (max) — the
margin is negative at every seed (governing case: seed 4 of 8-seed VOLT-REG ensemble [nominal]). Kill
criterion ≥5%: FAILED at the nominal condition, by 7.58 points, with
the sign of the comparison reversed.**

Reference seed: (a) 19.51 kg = 17.77 L/100 km; (b) 19.04 kg =
17.34 L/100 km. Mode (a) locks for 69.2% of cycle time (WS1's own
lockup fraction, reproduced), banks 2.3–3.0 kWh per cycle,
and starts the engine 46–62 times per cycle (reference
seed: 46, of which 42 are motor-synchronised lockup
re-engagements at 1.5 g). Mode (b) spends 505–631 s per cycle
in emergency load-follow above the pin and — under the R12 chain — now
completes the nominal cycle with **0.00 kWh** of unserved bus
energy on every seed (at CdA 5.4: 0.00–0.52 kWh on hard
seeds, fuel-corrected as before); it still demands more than the
150 kW motor rating for 42.1–71.5 s per cycle (energy-bookkept,
not clipped — R3/E24; the spine remains not sized for pure series).
Mode (a)'s rating exposure is 0.0 s on every seed.

Robustness: (a) trails (b′) by -2.80% to -2.48% as well, and (b)
and (b′) land within -0.36–+0.05% of each other — the pinned point
is still not a strawman, and the reversed verdict is a property of the
architecture comparison under the ruled chain, not of supervisor
tuning. Map-vintage robustness: rerunning the nominal gate on WS2's
other two exported maps gives -2.86% (432 V map) and -2.35% (749 V map) ensemble-min. Restated under
KX/R23-F3, computed rather than asserted: the spread across the
432–749 V exported window is **0.51 pp**, and **0.63 pp**
once the superseded r3-interim figure (§0-R) is swept in — the r3
report's "under 0.6 pp" was true of the first span and not of the
second, which is what it printed. Both are trivial against a
7.58-point shortfall; the verdict does not depend on which map
vintage the chain uses.

### 4.3 Why the sign flipped

The r2 verdict rested on WS1's scalar electric chain: bus→wheel 0.8656
× a part-load derate — an effective ~0.84 where the traction energy
flows. R12 replaces it with what WS2 measured: no PE stage exists on
the traction side, and the inverter+motor map runs 0.93–0.96 where the
energy actually is, giving an energy-weighted bus→wheel chain of
**0.9005** (map × 0.97 reduction) — the electric path is ~8 points
better than the convention G1 was first judged on. **Weighting,
restated under KX/R23-F5:** 0.9005 is WS2's `eta_mot_avg` × 0.97,
energy-weighted over WS2's *i-MMD* VOLT-REG run — the launch-heavy,
mostly-unlocked share the motor handles there. The **series-duty**
weighting mode (b) actually realises — wheel energy ÷ bus energy
through the same map over the full motoring trace — is **0.9160**
(8-seed 0.9160–0.9165), i.e. **233.5 g/kWh** ideal series
fuel-to-wheel. Both are quoted because they weight different things,
and the direction matters: the r3 report used the smaller one as the
trace-weighted chain, which *understated* the series advantage.
On the cycle-share weighting, ideal series fuel-to-wheel moves from
**247 → 237.6
g/kWh** (203.6 / (0.952 × 0.9005)) — *below* mode (a)'s realised
247 g/kWh at the wheel, because the welded rpm still pays E20's
9–10% BSFC penalty (fuel-weighted 221.9–223.3 g/kWh vs the
203.6 pin). The chain advantage that used to survive the BSFC penalty
(~6 points of 14) is now smaller than the penalty itself: the direct
path's 0.972 beats the electric path's ~0.90 by only ~7 points at the
wheel, the map's regen advantage credits both modes equally, and the
spin-drag member (-1.77 pp) plus the crank generator's parasitic
finish the locked path below series everywhere. Load-point shifting
cannot buy it back: banked energy redeploys at 0.8065 (gen × battery
round trip × map chain) ≈ 237.6 g/kWh at the wheel — still almost
exactly the series wheel rate (§10 check 5), so banking remains
fuel-neutral, not a lever.

### 4.4 Recommendation *(archived — the lead executed)*

> **Disposed.** BASELINE_v3 executed the kill clause on these numbers.
> The recommendation below is retained verbatim as the record of what
> WS4 put to the lead; (iv)'s fallback caveat is superseded on its
> energy half by §4-KX (zero unserved at the delivered pack) and
> re-raised on its power half as ESC-9.

**The G1-R number is -2.58% nominal ensemble-min against an armed ≥5%
kill criterion; per the directive, WS4 reports the number and the lead
executes or spares.** For that decision, the honest decomposition:
(i) the reversal is driven -7.01 pp by the ruled map-vs-scalar swap
and -1.77 pp by the measured spin member — both corrections were
anticipated to lean against the clutch (BASELINE_v2) and both did;
(i-bis) the *sign* of "series wins" is softer than the kill verdict:
under the most hostile genset-conditioning accounting the two modes
are break-even (0.09% min, §6 bracket) — but the ≥5% criterion
fails by ≥4.91 points under every accounting, so the gate's
disposition does not turn on the declared member;
(ii) the gate ran on the WS2 r4 chain of record — the directive's
r4-vintage contingency is closed (§0-R) and the verdict is insensitive
to map voltage across the full R10 window;
(iii) what the fuel gate no longer supports is the *fuel* case for the
clutch — the capability record is separate and unchanged (R1's cost:
no sustained 6% on the engine path off-nominal; the E3 respec's direct
band at nominal, §6); (iv) if the kill fires, ESC-5's fallback caveat
is *softened but not removed* by the R12 chain — pure series now
completes nominal VOLT-REG cleanly on the R8 floor (0.00 kWh
unserved), but still sheds up to 0.52 kWh at CdA 5.4 and exceeds
the R3 motor rating 42.1–71.5 s per cycle (R4: the spine is
not sized for it).

## 4-KX. R22a verification — pure series V2 at the DELIVERED pack (`series_duty_v2`)

*This is the live block. Everything above it about Gate G1 is an
archived record of a decision already executed.*

### 4-KX.1 What was run, and on what

ESC-5/R22a: the archived gate ran mode (b) on the **R8 3.5 kWh
floor**, a buffer sized for i-MMD duty, and pure series shed energy
there on hard seeds. The directive orders the verification at the
**delivered** pack. Configuration, exhaustively:

- **Pack:** 11.083608 kWh usable at the bus (WS3's 288s1p LTO-23
  pack), read at run time from
  `../WS3_battery/results.json → interface_WS3.packs.V2.usable_bus_kWh`
  — not transcribed. SHA-pinned.
- **Mode:** (b), pure series with the genset pinned at its best-BSFC
  point (84.7 kW shaft / 80.6 kW bus at 203.6 g/kWh),
  SOC-hysteresis start-stop, emergency load-follow below 25 % SOC.
  Mode (b′) — the same genset load-following its best-BSFC locus — is
  carried as a **companion** so R22b has both endpoints; **WS4 does
  not choose the dispatch, R22b assigns that to WS5.**
- **Cases (3):** nominal; CdA 5.4 (E13); and the 2,000 m/+45 °C corner
  — the *identical* case definition the archived gate used
  (ρ 0.8706 kg/m³, derate 0.9312, GVW, CdA 4.2, 2 kW aux). It is **not**
  the stricter R6 *rating* corner (+20 % payload, CdA 5.4, 4 kW aux),
  which sizes the engine rather than running the duty.
- **Seeds:** 8-seed VOLT-REG ensemble [23, 3–9] (R9). Every extremum
  below is an explicit min/max over that enumerated set with its
  governing seed labelled in the interface (R14).
- **Traction chain:** R12 — WS2 r4 measured map (../WS2_traction_motor/data/effmap_motor_inverter_662V.csv, 662 V)
  × 0.97 reduction, both directions. No spin member is charged: modes
  (b)/(b′) never lock and loaded machine losses are inside the map
  (R22d). The true-*coast* member is measured separately, §4-KX.5.
- **R16 cold curves:** WS3's `regen_acceptance.csv` is consumed as the
  bus-side charge-acceptance cap on the regen path
  (`V2pack_chg_cont_kW_bus`), at a declared cell temperature per case
  (25 °C / 25 °C / 45 °C = ambient). §4-KX.4.
- **R10 window:** 662.4 V nominal, 432.0–748.8 V operating, 1200 V-class
  SiC rectifier — the generator/rectifier spec of §2, unchanged.
- **Supervisor:** the ratified simulator's, untouched. Nothing was
  tuned for this run; the hysteresis band is varied only in the
  declared sensitivity of §4-KX.6.

### 4-KX.2 Result — the ordered exports

> **Unserved bus energy is 0.0000 kWh on every seed of every
> ordered case (all cases zero: True — no governing case - every ordered case is exactly zero on all 8 seeds).** The
> delivered pack has the *energy* to run pure-series
> V2 over VOLT-REG at nominal, at CdA 5.4 and at the corner. ESC-5's
> energy-side buffer worry is closed at the delivered pack — the
> archived gate's mode (b) shed up to 0.52 kWh at CdA 5.4 on the
> 3.5 kWh floor.

| Export (8-seed envelope, mode (b)) | Nominal (CdA 4.2, 2 kW aux, SL, GVW) | CdA 5.4 (E13) | 2,000 m / +45 °C corner |
|---|---|---|---|
| Fuel energy **kWh/km** | 1.701–1.728 | 2.019–2.038 | 1.413–1.426 |
| Fuel L/100 km | 17.20–17.47 | 20.41–20.60 | 14.29–14.42 |
| Fuel per cycle [kg] | 18.88–19.18 | 22.41–22.62 | 15.68–15.83 |
| **Unserved bus energy [kWh]** | 0.0000–0.0000 | 0.0000–0.0000 | 0.0000–0.0000 |
| Above-pin **demand** [s/cycle] | 1,201.8–1,274.9 | 1,847.0–1,984.4 | 690.8–741.7 |
| Above-pin demand energy [kWh] | 8.0–8.4 | 13.9–14.4 | 4.3–4.7 |
| Above-pin **engine** duty [s/cycle] | 0.0–274.3 | 418.1–487.0 | 80.4–100.6 |
| Emergency-band time [s/cycle] | 0.0–405.0 | 467.5–644.9 | 187.4–221.9 |
| Genset starts per cycle | 5–6 | 4–4 | 6–6 |
| Genset starts per hour | 2.7–3.3 | 2.2–2.2 | 3.3–3.3 |
| Genset on-fraction | 0.582–0.601 | 0.668–0.685 | 0.482–0.490 |
| Above-pin transitions per hour | 0.0–46.0 | 14.2–41.6 | 6.6–14.2 |
| SOC minimum (frac usable) | 0.228–0.262 | 0.183–0.222 | 0.246–0.250 |
| SOC maximum (frac usable) | 0.751–0.755 | 0.756–0.770 | 0.798–0.809 |
| Pack **discharge** peak [kW bus] | 115.1–184.5 | 126.0–142.2 | 166.2–192.5 |
| Pack **charge** peak [kW bus] | 147.5–147.6 | 147.5–147.6 | 147.5–147.5 |
| Time above R8 125 kW discharge [s] | 0.0–75.0 | 0.2–8.9 | 70.7–80.8 |
| Time above R8 110 kW charge [s] | 56.0–69.9 | 58.1–79.4 | 48.7–68.7 |
| Peak regen to pack [kW bus] | 68.9–69.0 | 68.9–69.0 | 69.1–69.1 |
| Regen shed by the R16 curve [kWh] | 0.0000–0.0000 | 0.0000–0.0000 | 0.0000–0.0000 |
| Motor over-rating exposure [s] | 42.1–71.5 | 110.4–137.5 | 12.0–22.7 |
| Fuel energy per payload t·km (R32 flag) | 0.5866–0.5959 | 0.6962–0.7027 | 0.4873–0.4917 |

Reading, case by case:

- **Nominal.** The genset is on for a fraction 0.582–0.601 of cycle
  time, starting 5–6 times per cycle — an order of magnitude calmer than the
  46–62 starts the archived gate's mode (b) made on the 3.5 kWh floor,
  because the buffer is now large enough to hold a whole hysteresis
  excursion. Above-pin *demand* runs 1,201.8–1,274.9 s/cycle (about a fifth
  of the cycle) worth 8.0–8.4 kWh: the pin covers the duty on
  average and misses it in the peaks, which is exactly the shape of
  R22b's question.
- **CdA 5.4.** The hardest case for the buffer: SOC bottoms at
  0.183–0.222 of usable, the emergency band engages 467.5–644.9
  s/cycle and the engine actually runs above the pin 418.1–487.0
  s/cycle. Still zero unserved.
- **2,000 m/+45 °C corner.** Thin air *helps* the duty (less drag) even
  as it derates the engine: fuel energy is the lowest of the three.
  What it does not help is pack power — see below.

SOC trajectories for all 24 runs: `figs/fig04_series_duty_soc.png`,
`data/series_duty_v2_soc_trajectories.csv` (5 s decimation, every seed and case), and the full-rate
reference trajectory inside `data/trace_series_duty_v2_nominal_seed23_10Hz.csv`.

### 4-KX.3 What the run does NOT establish — the pack POWER envelope (ESC-9)

The ordered run constrains the pack's **energy**, not its **power**.
Measured and reported, not enforced: bus-side pack discharge peaks at
**192.5 kW** against R8's restated **125 kW** bus-side discharge
envelope, and charge peaks at **147.6 kW** against R8's **110 kW** —
the charge peak because regen and the genset can charge the pack at the
same time. The exceedances are short (see the table) but they are real,
and the corner is the worst of them.

A second, independent qualification on the same page: WS3 declares the
R8 discharge peak **over SOC 40–90 % of nameplate** and states in the
same breath that full power below SOC 40 is *not* guaranteed ("WS5
dispatch limit"). Mapped through WS3's own end stops, that gate is
SOC 0.3333 of *usable* — and the ordered run spends real time
below it on every case (measured off the 5 s SOC trajectories):

| Time below WS3's declared R8 discharge SOC band | Nominal (CdA 4.2, 2 kW aux, SL, GVW) | CdA 5.4 (E13) | 2,000 m / +45 °C corner |
|---|---|---|---|
| Seconds per cycle below SOC 0.40 nameplate | 290.0–435.0 | 825.0–975.0 | 175.0–185.0 |
| Minimum SOC reached (nameplate) | 0.3215 | 0.2878 | 0.3345 |

So the pack is asked for its largest currents in precisely the SOC
region where WS3 declines to guarantee them. WS4 does not resolve that;
it reports it.

WS4 therefore ran the obvious adversarial bracket: enforce the envelope
as a wall — discharge above the cap is unserved and booked exactly as
the buffer-empty case is, charge above the cap is shed. Note the
bracket uses R12/ES-4's ruled **125 kW** bus-side discharge figure,
which is the *more permissive* of the two numbers on the record — WS3's
own compliance gates are computed at 120 kW — so the shortfall below is
if anything understated.

| R8 envelope enforced (125 kW dis / 110 kW chg, bus) | Nominal (CdA 4.2, 2 kW aux, SL, GVW) | CdA 5.4 (E13) | 2,000 m / +45 °C corner |
|---|---|---|---|
| Unserved bus energy [kWh] | 0.0000–0.0021 | 0.0000–0.0149 | 0.5194–0.6129 |
| Discharge clipped [s/cycle] | 0.0–2.8 | 0.2–8.9 | 82.2–94.2 |
| Charge shed [kWh/cycle] | 0.376–0.472 | 0.492–0.672 | 0.202–0.347 |
| Fuel per cycle [kg] | 18.98–19.16 | 22.51–22.75 | 15.75–15.89 |

**Worst case 0.613 kWh unserved, at alt2000m_45C.** That is the
finding, and it is a finding, not a tuning knob: R4/E24's record — "the
spine is not sized for forced series" — extends past the R3 motor
rating to the **pack's rated bus-side power**. Pure-series V2 at the
delivered pack has the energy and, at rated power, not quite the power
on the hardest samples. Whether the answer is a dispatch rule (run the
genset earlier so the pack never has to cover the peak alone), a
higher-rated pack interface, or an accepted short-duration overload is
a WS5/WS3 question. Escalated as **ESC-9**. The R3 motor-rating exposure
(42.1–71.5 s/cycle at nominal, 110.4–137.5 s at CdA 5.4) is the same
record as the archived gate's and is unchanged by the larger pack.

### 4-KX.4 R16 cold curves: consumed, and NOT binding here

The R16 curve is wired into the regen path as the bus-side charge
acceptance at the declared cell temperature: 130.8 kW at 25 °C cells
(nominal, CdA 5.4) and 129.1 kW at 45 °C cells (corner). Peak
regen-to-pack over the whole run is **69.1 kW bus**, so the curve
sheds nothing: `regen_shed_by_r16_kWh` is 0.0000 kWh on every seed
(curve bound any sample: False). That is the honest result of
consuming a cold-operation curve at three warm conditions, and it is
stated rather than dressed up.

Where it *would* bind, from the same curve and this run's peak regen:
below **-9.4 °C** cells on the cold side, and above **53.9 °C**
cells on the hot side. The hot side is not hypothetical — WS3's
pack-loop **sizing line** holds cells at or below **55 °C** at +45 °C
ambient, and acceptance at 55 °C is **62.2 kW**, *below* this run's
peak regen. A corner descent on a pack sitting at its loop's design
ceiling would shed regen to the resistor/friction column. Escalated as
**ESC-8**; not resolved here, because the cell-temperature trajectory
belongs to WS3/WS6 and the blend order to WS5.

### 4-KX.5 R22d true-coast spin member — measured, reported, not charged

R22d: the machine is permanently geared, so its zero-torque spin drag
persists whenever the vehicle coasts *without* regen; in driving and
regenerating operation it is inside WS2's maps and must not be added
again. Measured on this run at WS2's 85 km/h point drag (1,109 W
shaft + 371 W bus) scaled linearly with road speed
[WS4-DECLARED]: true-coast exposure is only **22.5–26.1 s/cycle**, and
all of it sits below the regen-blend floor at walking pace, so the
unbooked member is worth at most **0.0003 pp** of cycle fuel. It is
**not** charged to fuel; the fuel numbers above are optimistic by that
amount and by nothing else on this account.

The finding for WS5 is the shape, not the size: VOLT-REG as WS1 builds
it essentially never true-coasts at speed — negative wheel power is
always at least partly captured above the blend floor — so this duty
does not exercise R22d at all. A supervisor that *chooses* to coast at
highway speed would, and R22d's guidance (prefer light regen over true
coast) is the remedy. The member is exported as
`interface_ws4 → spin_drag_operational_note_r22d` with an explicit
double-count warning, so WS5 can price the choice without
double-charging driving samples.

### 4-KX.6 Declared sensitivities

**Genset hysteresis band.** The cycling rate is the export most
sensitive to a supervisor constant, so the constant is not left
implicit. The ratified simulator's band is 0.35–0.75 of usable =
4.43 kWh; WS3's own allocation for V2 is 3.5 kWh of genset
hysteresis about the 0.55 target. Reference seed, both bands:

| Reference seed 23 | Nominal (CdA 4.2, 2 kW aux, SL, GVW) | CdA 5.4 (E13) | 2,000 m / +45 °C corner |
|---|---|---|---|
| Genset starts — simulator band | 5 | 4 | 6 |
| Genset starts — WS3 allocated band | 6 | 6 | 9 |
| kWh/km — simulator band | 1.701 | 2.019 | 1.413 |
| kWh/km — WS3 allocated band | 1.705 | 2.026 | 1.421 |

The tighter WS3 band cycles the genset more and costs a little fuel;
neither band changes any conclusion above. WS5 owns the choice.

**Load-following companion (b′), for R22b.**

| Companion (b′) load-following | Nominal (CdA 4.2, 2 kW aux, SL, GVW) | CdA 5.4 (E13) | 2,000 m / +45 °C corner |
|---|---|---|---|
| Fuel energy kWh/km | 1.706–1.722 | 2.018–2.038 | 1.438–1.451 |
| Genset starts per cycle | 1–1 | 1–1 | 2–2 |
| Unserved bus energy [kWh] | 0.0000–0.0000 | 0.0000–0.0000 | 0.0000–0.0000 |

At nominal and CdA 5.4 the pinned and load-following dispatches are
within a fraction of a percent of each other; at the corner the pin is
better, because load-following drags the derated engine off its island.
That is a data point for R22b, not a verdict.

### 4-KX.7 Heat to the WS6 ledger (program rule 7)

Rejected heat by component and case for the pure-series duty at the
delivered pack — these, not the archived gate's mode-(a) rows, are the
Vehicle Zero V2 rows WS6 should size against:

| Case (VOLT-REG cycle average, 8-seed max) | Engine rejection [kW] | Generator+rectifier [kW] | Electric chain [kW] | Friction brake [kWh/cycle] |
|---|---|---|---|---|
| Nominal (CdA 4.2, 2 kW aux, SL, GVW) | 72.6 | 2.44 | 4.22 | 0.62 |
| CdA 5.4 (E13) | 86.3 | 2.84 | 4.72 | 0.57 |
| 2,000 m / +45 °C corner | 59.7 | 2.01 | 3.79 | 0.67 |

Splits follow §7's declared 49/38/10/3 exhaust/coolant+oil/CAC/radiation
balance; the R22d coast-spin members (≤0.0002 kWh/cycle) land in the
traction machine on WS2's LT-loop line and are exported per case in
`heat_ledger_ws6`.

## 5. Start-stop analysis (V1)

*(Ratified r2 record — outside G1-R scope, not recomputed.)*

Start-stop at the pinned point on VOLT-SUB, R8 1.5 kWh floor, 0.8 kWh
hysteresis share: 66 starts/shift reference seed at 3.41 L/h; 8-seed
envelope **57–74 starts per 8 h shift**; 3.0 kWh usable halves it to
33 (3.37 L/h). Start-stop saves **6.2%** vs continuous load-following
(3.41 vs 3.63 L/h). Cold case (regen off, 4 kW aux): **4.83 L/h**
(+42%), duty 59%. Mitigations and ESC-3 unchanged; R19 has since
ratified the start-count disposition.

| Hysteresis share of the 1.5 kWh floor | Starts per 8 h shift (ref seed) | Fuel |
|---|---|---|
| 0.5 kWh | 116 | 3.50 L/h |
| **0.8 kWh** | **66 starts** | **3.41 L/h** |
| 1.1 kWh | 58 | 3.41 L/h |
| 3.0 kWh usable, 1.6 kWh share | **33 starts** | 3.37 L/h |

## 6. Sensitivities (G1-R condition table + one-factor attribution)

G1-R margin (a vs b), 8-seed min / median, all else nominal — same
condition table as r2, recomputed under the ruled conventions:

| Case | min | median | Reading |
|---|---|---|---|
| **Nominal (CdA 4.2, 2 kW aux, SL)** | **-2.58%** | **-2.50%** | **FAILS the ≥5% criterion; sign reversed** |
| CdA 5.4 (E13) | **-0.09%** | 0.02% | **break-even** (max 0.12%; 4 of 8 seeds marginally positive — seeds 4, 7, 8, 9) — more road load helps the locked path to parity, nowhere near the criterion |
| Accessories 4 kW | **-2.25%** | -1.98% | insensitive vs nominal |
| Hot day +45 °C, sea level | **-3.49%** | -3.31% | fails (8-seed max -3.06%) |
| 2,000 m + 45 °C (R7 corner) | **-5.90%** | -5.66% | **worst case** — thin air pushes the welded engine down its map, as in r2, now from a negative baseline; ESC-2 restated |
| Reference 4HK1 torque curve instead of V2C | **-2.23%** | -2.02% | the verdict does not hinge on the E3 torque respec |

**One-factor attribution (directive 3)** — which correction moved the
gate, at nominal:

| Convention | min | median | Δ min vs prior |
|---|---|---|---|
| Prior (r2 / BASELINE_v1 scalar chain, no spin) — anchor, reproduced bit-identically | 6.26% | 6.45% | — |
| + spin-drag member alone (directive 1b) | 4.49% | 4.68% | **-1.77 pp** |
| + map-vs-scalar swap alone (directive 1a) | -0.75% | -0.64% | **-7.01 pp** |
| **G1-R (both — the gate of record)** | **-2.58%** | **-2.50%** | **-8.84 pp** |

The map swap dominates (-7.01 pp) and alone takes the gate below
zero; the spin member alone (-1.77 pp) takes it below the criterion
but not below zero; their interaction is a further -0.06 pp (min) /
-0.10 pp (median).
Map-vintage robustness: -2.86% (432 V map) and -2.35% (749 V map) ensemble-min (spin on) — the sign is
not a property of the nominal-voltage map.

**Genset-conditioning bracket (sign robustness)** — the one
declared-not-measured member the reversal's *sign* rests on is the
rectifier/conditioning model (pe0 0.15 kW + 1% of P_elec, TBC at
procurement). Two hostile readings of R12's "genset-side PE/rectifier
in WS4's ledger", run through the full 8-seed pipeline with the pinned
point re-derived under each (mode (b) pays the stressed conversion
too):

| Genset conditioning | min | median | Reading |
|---|---|---|---|
| Declared member (gate of record) | **-2.58%** | -2.50% | series wins |
| Replaced by a 3%-class stage | -0.79% | -0.71% | series still wins |
| WS1's 3% stage stacked on the declared member (most hostile) | 0.09% | 0.15% | break-even (max 0.34%) |

The *sign* of "series wins" carries ~1.7–2.7 pp of genset-model
uncertainty; the **kill-criterion outcome does not** — the most
hostile accounting still leaves the nominal ensemble-min 4.91
points short of +5%, and the ratified +6.26% is unrecoverable under
any defensible reading. Exported at `interface_ws4 → gate_g1 →
genset_conditioning_bracket`.

R6 corner delivery (the other sensitivity set — unchanged r2 record):
derate 0.9312 ⇒ 122.9 kW vs 122.1 kW required (+0.82 kW,
PROVISIONAL/R18, §2.1). Direct-path 6% capability with the V2C curve:
band 59.4–61.6 km/h at GVW/CdA 4.2/2 kW aux; max grade 6.02%; the band
vanishes at +20% payload or CdA 5.4 (F-2). Series grade hold with the
candidate: 71.3 km/h nominal, 63.6 km/h at the full R6 corner
(reference curve max direct grade: 5.14%, no 6% capability —
WS1 §4.5 reproduced).

## 7. Heat ledger to WS6 (R9)

Split model declared in §1. Full numbers in `results_ws4.json →
heat_ledger_ws6`. All rows except the G1(a) cycle average are the
ratified r2 record (R20 seeds unchanged); the G1(a) row is a gate
quantity, restated under G1-R.

| Case | Component | kW |
|---|---|---|
| V2 grade hold (6%, 61 km/h, series, 10 min) | electrical chain — WS1 of-record | 20.2 |
| | electrical chain — WS4 maps recompute (R20 seed of record until WS2 r4 lands) | **17.9 kW** (of which generator 4.6) |
| | engine radiator package (coolant+oil+CAC) | **77.2 kW** |
| | engine exhaust | 78.8 |
| **V2 R6 corner continuous (THE radiator sizing case: 45 °C, 2,000 m, 122.9 kW shaft)** | engine radiator package | **95.0 kW** |
| | engine exhaust | **97.0 kW** |
| | generator | 4.7 |
| V2 continuous max, sea level (132 kW) | engine radiator package | 98.9 |
| V1 fixed point (29.5 kW, when running) | engine radiator package | **24.4 kW** (10.1 duty-averaged) |
| | generator | 1.8 |
| G1-R(a) VOLT-REG cycle average | engine rejection (all paths) | **78.3 kW** |
| | generator + electric chain + direct-path losses | 1.1 + 0.8 + 1.7 |
| | PM spin drag (heat lands in the traction machine — WS2's LT-loop ledger line; fuel charged here) | 1.47 kWh/cycle shaft + 0.50 kWh/cycle bus |
| | friction brakes | 0.42 kWh/cycle |
| 50 kW brake resistor | — | on WS2's ledger line (R2); listed to avoid a gap |

Ledger correction flagged to WS6 (ESC-4, unchanged): the radiator
design case is the R6 corner (95.0 kW in 45 °C air), not the grade
hold; R20 recorded the seeds.

**KX addition — the pure-series duty rows (R22a).** The architecture of
record after the kill is pure series, so the cycle-average rows WS6
should size the Vehicle Zero V2 loops against are these, not the
archived mode-(a) row above. Full tables in §4-KX.7 and
`heat_ledger_ws6 → series_duty_v2_*_cycle_average`:

| Case (VOLT-REG cycle average, 8-seed max) | Engine rejection [kW] | Generator+rectifier [kW] | Electric chain [kW] | Friction brake [kWh/cycle] |
|---|---|---|---|---|
| Nominal (CdA 4.2, 2 kW aux, SL, GVW) | 72.6 | 2.44 | 4.22 | 0.62 |
| CdA 5.4 (E13) | 86.3 | 2.84 | 4.72 | 0.57 |
| 2,000 m / +45 °C corner | 59.7 | 2.01 | 3.79 | 0.67 |

## 8. Findings register (non-escalated)

- **F-1** *(unchanged r2)* The E3 torque respec (750 Nm @ 1,400 rpm)
  restores a direct 6% hold band of 59.4–61.6 km/h — nominal only; max
  direct grade 6.02%.
- **F-2** *(unchanged r2)* That band vanishes at +20% payload and at
  CdA 5.4 — R1's recorded cost stands off-nominal.
- **F-3** *(restated under G1-R)* Pinned-point series is within
  -0.36–+0.05% of best-locus series on fuel (b vs b′) — the pinned
  point is not a strawman; the G1 comparison as ruled remains fair
  under the R12 chain, and (a) trails both.
- **F-4** *(numbers unchanged — trace-determined)* Mode (b) exceeds the
  150 kW motor rating for 42.1–71.5 s per cycle at nominal and
  110.4–137.5 s at CdA 5.4 (energy-bookkept, not clipped;
  these samples lie inside the WS2 map envelope and carry true
  interpolated losses, §4.1) — the spine is NOT sized for pure series
  (R4). Mode (a): 0.0 s.
- **F-5** *(unchanged r2)* V1 cold-case fuel +42% at 59% duty (§5).
- **F-6** *(new, G1-R)* Under the R12 chain, mode (b) completes nominal
  VOLT-REG with 0.00 kWh unserved on the R8 3.5 kWh floor — the r2
  buffer-adequacy caveat against pure series is now an off-nominal
  finding only (CdA 5.4: 0.00–0.52 kWh); ESC-5 restated.
- **F-7** *(new, KX/R22a)* At the delivered 11.08 kWh pack, pure
  series completes all three ordered cases with 0.0000 kWh
  unserved — but its bus-side pack **power** reaches 192.5 kW
  discharge / 147.6 kW charge against R8's 125/110 kW envelope, and
  enforcing that envelope costs up to 0.613 kWh of unserved energy
  at alt2000m_45C (§4-KX.3, ESC-9).
- **F-8** *(new, KX/R16)* The R16 charge-acceptance curve is consumed
  and binds nothing at any ordered case (peak regen 69.1 kW bus vs
  130.8 kW accepted at 25 °C cells); it would bind below -9.4 °C
  and above 53.9 °C cells — and WS3's pack-loop sizing ceiling of
  55 °C accepts only 62.2 kW (§4-KX.4, ESC-8).
- **F-9** *(new, KX/R23-F2)* The map-boundary convention's exposure is
  22.7–31.3 s/cycle at nominal (of which only 0.0–6.0 s locked) and
  27.8–46.4 s/cycle at CdA 5.4 (of which 4.8–23.1 s locked, up to
  98.5 km/h) — one-sided in mode (b)'s favour at CdA 5.4 by at most
  0.0158 pp. Immaterial to the archived verdict; the r3
  mode-neutrality wording is withdrawn (§4.1).

## 9. Development disclosures (in the spirit of WS1 §9)

D1–D3 from rounds 1–2 are unchanged and remain part of the record
(early lockup-start over-charging; the D2 unserved-energy defect whose
correction moved the r2 verdict; the Willans light-load recalibration).

- **D4 (G1-R — found by WS4's pre-adjudication adversarial pass and
  fixed)**: the first G1-R build charged the spin-drag member AND the
  full map loss (which includes the machine's no-load losses) on the
  ~2 min/cycle of locked torque-fill samples — a double-count against
  mode (a) worth ~0.03–0.06 pp. Fixed: fills use the marginal map loss
  when the spin member is active (§4.1). Effect of the fix: nominal
  ensemble-min −2.67 → -2.58%. Two prose overstatements were corrected
  in the same pass (boundary-convention conflation; categorical
  sign-reversal language vs the break-even CdA 5.4 ensemble) — §0-R.
- **G1-R validation**: the refactored pipeline reproduces the r2 gate
  margins when run in the prior convention (legacy path
  float-identical; nominal ensemble statistics asserted to 1e-9 in
  `run_ws4.py`), so the G1-R shift (-8.84 pp min) is attributable
  to the ruled corrections plus the disclosed D4 fix, itemised in §6.
  The spin member was validated against WS2's independent 85 km/h
  point measurement (§10 check 10); the chain interpolator reproduces
  WS2's published map cells exactly in both quadrants, with exact
  bilinear midpoints between cells, and its wheel-to-bus direction
  reproduces WS2's independently exported regen-to-bus (3.73 kWh over
  VOLT-REG) to the exported precision.
- **D5 (KX) — WS4's F2 exposure count does not equal the r3
  adjudicator's, and the difference is definitional.** The adjudicator
  measured 3.6–7.6 s/cycle at nominal against the map's feasibility
  boundary; WS4's counter reports 22.7–31.3 s/cycle on the stencil
  criterion (a bilinear stencil touching any originally-infeasible
  cell) and 18.9–24.5 s on the stricter torque-outside-the-envelope test,
  which is still larger. The two criteria are not the same test and WS4
  has not reproduced the adjudicator's implementation. WS4's is the
  more inclusive count, so the pp bound derived from it is the
  conservative one, and the *shape* of the finding — mode-neutral at
  the reference seed, one-sided on locked cruise samples at CdA 5.4,
  immaterial in magnitude — is identical under both. Flagged rather
  than reconciled: reconciling would require re-deriving the
  adjudicator's counter, which is not this round's scope.
- **D6 (KX) — two brackets in §4-KX were NOT ordered.** The KX
  directive's scope is exhaustive and does not ask for them: the R8
  power-envelope bracket (§4-KX.3) and the SOC-window check against
  WS3's declared discharge gate are WS4's own adversarial pass on the
  ordered run, added because the ordered "zero unserved energy" result
  rests on the pack's power envelope not being enforced and that
  assumption deserved a number rather than a caveat. They are labelled
  as brackets everywhere they appear; the ordered numbers are the
  ordered numbers. The load-following companion (b′) and the
  hysteresis sensitivity are in the same category and labelled the
  same way.
- **D7 (KX) — the R22d coast member is measured with a declared
  scaling, not a measured one.** WS2 exports point drag at 85 km/h;
  WS4 scales it linearly with road speed to price true-coast samples.
  PM iron losses grow faster than linearly with speed, so the linear
  scaling understates — but the exposure is 22.5–26.1 s/cycle at walking
  pace, where any scaling gives a number too small to matter
  (0.0003 pp). If WS5 adopts highway coasting, the member needs
  WS2's speed dependence, not this stand-in.

## 10. First-principles sanity checks

1. **WS1 regression**: recomputing the 6%/60 km/h floor through WS1's
   own physics gives 107.81 kW — matches WS1's 107.8077950219109 to
   <0.01 kW (asserted in `run_ws4.py`).
2. **Map anchors** *(unchanged)*: island 203.6–205.2 g/kWh ⇒ η_b ≈
   0.41; rated-continuous 215.4 g/kWh; 25%/1,800 rpm ≈ 260 (published
   240–270); motoring drag at 1,706 rpm = 10.7 kW vs WS1's "~10 kW".
   Fast scalar BSFC path asserted equal to the map to <0.05 g/kWh.
3. **Chain arithmetic, restated under R12 and re-weighted under
   KX/R23-F5**: pinned 203.6 / (η_gen
   0.952 × chain 0.9005) = **237.6 g/kWh** ideal series
   fuel-to-wheel on WS2's i-MMD cycle-share weighting (the r2
   convention gave 247 g/kWh — the ruled chain is worth ~10 g/kWh
   at the wheel). On the **series-duty** weighting the same
   arithmetic gives 203.6 / (0.952 × 0.9160) = **233.5 g/kWh**,
   which is the honest ideal for mode (b)'s own duty and sits closer
   to what the simulation delivers. The simulation's (b)
   delivers 19.04 kg over 78.85 kWh of tractive wheel energy ≈
   241 g/kWh with buffering overheads; mode (a) delivers 19.51 kg ≈
   247 g/kWh. 241 vs 247 ⇒ a -2.5% reference-seed margin — the
   reversed headline reproduced by hand from two ratios.
4. **Fuel plausibility**: 17.77–17.34 L/100 km for a 6.6 t GVW box
   truck averaging 72 km/h with 6% grades sits inside the published
   15–22 L/100 km band for class 4–5 diesels on regional work (both
   modes; the ordering within the band is the gate's reversal).
5. **Load-point-shifting marginal check, restated**: banking at fixed
   rpm costs ~191 g/kWh marginal, redeployed at 0.8065 (0.952 gen ×
   0.97² battery × 0.9005 chain) ⇒ ~237.6 g/kWh at the wheel —
   almost exactly the series wheel rate. *Weighting note (KX/R23-F5):*
   0.9005 is the right weighting on the redeploy side, because
   banked energy is spent on the unlocked, launch-weighted share the
   figure is averaged over; the series wheel rate it is compared
   against is the sim's realised 241 g/kWh, not the ideal, so the
   comparison does not turn on which weighting the ideal uses. Banking
   remains fuel-neutral; the G1-R margin cannot be tuned upward much,
   which is why §4.3's reversal deserves belief.
6. **Grade holds, closed form** *(unchanged)*: 132 kW ⇒ 71.3 km/h on
   6% nominal; 63.6 km/h at the R6 corner.
7. **Corner heat balance** *(unchanged)*: 122.9 kW shaft at 219.6
   g/kWh ⇒ 320.9 kW fuel; 97.0 kW exhaust / 95.0 kW radiator package —
   sums close exactly.
8. **V1 start count vs WS1 E6** *(unchanged)*: models agree within
   ~10% after window-ratio scaling.
9. **G1-R regression anchor**: the prior-convention nominal reproduces
   the ratified r2 margins (6.26/6.45/6.78%) — the legacy code
   path is float-identical by construction, and the nominal ensemble
   min/median/max are asserted against the ratified values to 1e-9 in
   `run_ws4.py` before any ruled correction is applied.
10. **Spin member cross-check**: the mean locked-time shaft rate
    derived from WS2's cycle integral (1.153 kW) sits within ~4% of
    WS2's independently exported 85 km/h point drag (1.109 kW) —
    VOLT-REG's locked residency centres near 85 km/h, so the mean and
    the point should and do agree.

## 11. Interfaces (machine-readable)

Injected byte-identically from `results_ws4.json → interface_ws4`
(asserted by `verify_ws4.py`):

```json
{
 "_basis": "mirrors WS1 results.json conventions; extrema are 8-seed ensemble envelopes (R9); all shaft powers are engine shaft; all cross-WS electrical quantities bus-side (R12); BSFC maps are WS4-constructed Willans maps; G1 traction chain per R12 = WS2 measured maps x 0.97 reduction, no scalar PE member",
 "v2_genset": {
  "engine": "4HK1-V2C (Isuzu 4HK1-TC hardware, genset recalibration)",
  "displacement_l": 5.193,
  "continuous_shaft_kW_sea_level": 132.0,
  "peak_shaft_kW": 153.30046750225958,
  "low_end_torque_spec_Nm_at_1400rpm": 750.0,
  "r6_corner": {
   "conditions": "45 C, 2,000 m, +20% payload, 4 kW aux, CdA 5.4",
   "derate_factor": 0.9311999999999999,
   "delivered_shaft_kW": 122.91839999999999,
   "required_shaft_kW": 122.1,
   "margin_kW": 0.8183999999999969,
   "status": "PROVISIONAL - the +0.82 kW margin rests on the WS4-proposed 132 kW continuous flat-rating and the WS4-declared class-typical derate model, both TBC against the procured datasheet (ESC-1; adjudication r1 F5). Do not release WS6 packaging against this margin until both are confirmed."
  },
  "r18_datasheet_confirmation": {
   "blocking_figures": {
    "continuous_flat_rating": "132 kW continuous shaft @ 2,200 rpm as an unlimited-hours prime/COP-class rating (ISO 8528-1 / ISO 3046-1 basis, no 10%-overload dependency). The published 4HK1-TC figures are automotive (153 kW peak); the 132 kW continuous is a WS4-proposed genset recalibration and exists on no public sheet.",
    "derate_model": "the flat-rating boundary in corner-delivery form (R18 label): either 'no derate to 2,000 m / +45 C' or the datasheet derate curve. WS4 assumed 4%/1,000 m above 1,000 m and 1%/5 C above 30 C (factor 0.9312); the +0.82 kW R6 margin flips if the confirmed rating is 1 kW lower or the slope 1%/1,000 m steeper."
   },
   "non_blocking_figures": {
    "torque_respec": "750 Nm @ 1,400 rpm full-load curve (E3 spec) on production hardware",
    "bsfc_map": "Willans-constructed island 203.6 g/kWh / rated-continuous 215.4 g/kWh (G1 margins move with the map, the gate verdict is re-runnable on a measured map in this pipeline)",
    "motoring_fmep_anchor": "10.7 kW at 1,706 rpm",
    "heat_split": "49/38/10/3 exhaust/coolant+oil/CAC/radiation",
    "mass": "~500 kg dry"
   },
   "substantiating_test_if_datasheet_silent": "witnessed dynamometer heat-run per ISO 3046-1 (corrections per ISO 15550 / SAE J1349), two legs: (i) sea level: 132 kW @ 2,200 rpm held continuously to thermal steady state (coolant/oil dT/dt < 1 K per 10 min, >= 4 h), fuel stop untouched, smoke/EGT/boost inside the manufacturer's continuous limits; (ii) simulated R6 corner: inlet conditions set to 2,000 m / +45 C equivalents (~79.5 kPa inlet depression + 45 C cell or altitude chamber), same fuel stop, acceptance >= 122.1 kW shaft sustained to steady state. A third point at ~1,000 m equivalent pins the two derate coefficients separately. The corner leg tests delivery, not the label - R18's corner-delivery form is the requirement.",
   "gates": "these two blocking figures + G1-R are the WS6 release blockers (R18)"
  },
  "generator": {
   "name": "GEN-V2 IPM 135",
   "type": "crank-mounted IPM PM synchronous + active SiC rectifier (1200 V-class devices, R10 window), liquid-cooled",
   "cont_kW_shaft_in": 135.0,
   "peak_kW_shaft_in": 155.0,
   "mass_kg": 90.0,
   "map_file": "data/gen_eff_map_V2.csv",
   "eta_at_pinned_point": 0.9517612816135814,
   "spin_loss_at_1800rpm_kW": 1.2,
   "dc_output_window": {
    "ruling": "R10 (BASELINE_v2)",
    "bus_class": "650 V class, pack-native",
    "nominal_V": 662.4,
    "operating_V": [
     432.0,
     748.8
    ],
    "charge_transient_10s_V": 777.6,
    "granularity": "12 cells (27.6 V)",
    "rectifier_device_class": "1200 V SiC (was 750 V class at the superseded 370 V bus)",
    "loss_model_at_new_window": "WS4-DECLARED: the exported loss model (iron+windage prop. to speed, copper prop. to T^2, rectifier 1% of P_elec + fixed) is carried unchanged at the new window - at this fidelity the voltage change trades conduction current for switching stress roughly evenly across a rewound machine + 1200 V SiC stage; confirm coefficients at procurement"
   }
  },
  "pinned_series_point": {
   "rpm": 1287.96992481203,
   "trq_Nm": 627.9824561403509,
   "p_shaft_kw": 84.69969589648574,
   "bsfc": 203.61665610230665,
   "p_bus_kw": 80.61389111871986,
   "fuel_gps": 4.790630236479081,
   "eta_gen": 0.9517612816135814
  },
  "mass_kg": {
   "engine_dry": 500.0,
   "generator": 90.0,
   "rectifier": 12.0,
   "mounts_adaptation": 35.0,
   "total_dry": 637.0,
   "aftertreatment_extra": 60.0
  },
  "volume_m3_envelope": 0.67,
  "bsfc_map_file": "data/bsfc_map_V2_candidate.csv",
  "reference_map_file": "data/bsfc_map_4HK1_ref.csv",
  "gen_map_file": "data/gen_eff_map_V2.csv"
 },
 "v1_genset": {
  "engine": "V3307-V1C (Kubota V3307-CR-T class)",
  "displacement_l": 3.331,
  "continuous_shaft_kW_sea_level": 50.0,
  "rated_shaft_kW": 55.4,
  "generator": {
   "name": "GEN-V1 IPM 60",
   "type": "genset-mounted IPM PM synchronous + active SiC rectifier (1200 V-class devices, R10 window), liquid-cooled",
   "cont_kW_shaft_in": 60.0,
   "peak_kW_shaft_in": 70.0,
   "mass_kg": 48.0,
   "map_file": "data/gen_eff_map_V1.csv",
   "eta_at_pinned_point": 0.9394387395705018,
   "spin_loss_at_1800rpm_kW": 0.7,
   "dc_output_window": {
    "ruling": "R10 (BASELINE_v2)",
    "bus_class": "650 V class, pack-native",
    "nominal_V": 662.4,
    "operating_V": [
     432.0,
     748.8
    ],
    "charge_transient_10s_V": 777.6,
    "granularity": "12 cells (27.6 V)",
    "rectifier_device_class": "1200 V SiC (was 750 V class at the superseded 370 V bus)",
    "loss_model_at_new_window": "WS4-DECLARED: the exported loss model (iron+windage prop. to speed, copper prop. to T^2, rectifier 1% of P_elec + fixed) is carried unchanged at the new window - at this fidelity the voltage change trades conduction current for switching stress roughly evenly across a rewound machine + 1200 V SiC stage; confirm coefficients at procurement"
   }
  },
  "pinned_series_point": {
   "rpm": 1300.501253132832,
   "trq_Nm": 216.69924812030075,
   "p_shaft_kw": 29.5118746401605,
   "bsfc": 228.7200934767799,
   "p_bus_kw": 27.72459831431504,
   "fuel_gps": 1.8749885351034776,
   "eta_gen": 0.9394387395705018
  },
  "mass_kg": {
   "engine_dry": 305.0,
   "generator": 48.0,
   "rectifier": 8.0,
   "mounts_adaptation": 25.0,
   "total_dry": 386.0
  },
  "volume_m3_envelope": 0.35,
  "bsfc_map_file": "data/bsfc_map_V1_candidate.csv",
  "gen_map_file": "data/gen_eff_map_V1.csv"
 },
 "gate_g1": {
  "status": "executed_kill_2026-08-30",
  "_archival_notice": "ARCHIVED. Gate G1's kill clause was EXECUTED in BASELINE_v3 (ratified 2026-08-30): the clutch, the lockup device and actuator, clutch-sync control, R11's condition-aware mode policy, fault spec F-1 and the i-MMD topology reference are all deleted with it. Both variants are pure series. This block is retained as the record of the decision and its provenance. NO FIELD OF THIS BLOCK MAY BE CONSUMED AS A LIVE REQUIREMENT - consume interface_ws4 -> series_duty_v2 instead. Mode (a) does not exist in any live architecture.",
  "executed_by": "BASELINE_v3.md, GATE G1: EXECUTED. THE CLUTCH IS DELETED.",
  "_revision": "G1-R recompute (G1R_DIRECTIVE.md; rulings R10/R11/R12/R18), errata-corrected under R23/KX. Supersedes the r2 gate numbers, which are retained under results_ws4.json -> gate_g1_prior_convention as the regression anchor.",
  "verdict": {
   "condition": "nominal: sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, 2 kW aux, GVW, VOLT-REG",
   "convention": "G1-R (R12): traction = WS2 measured map [data/effmap_motor_inverter_662V.csv, 662 V] x 0.97 reduction, no scalar PE member, no part_load_factor; PM spin drag charged to (a) locked samples at 1.1532 kW shaft + 0.3896 kW bus (WS2 export)",
   "margin_pct_ensemble_min": -2.5816447179555606,
   "margin_pct_ensemble_min_governing_case": "seed 4 of 8-seed VOLT-REG ensemble [nominal]",
   "margin_pct_ensemble_median": -2.5036598384800866,
   "margin_pct_ensemble_max": -2.3727109656800724,
   "kill_criterion_pct": 5.0,
   "passes": false,
   "missed_by_pp": 7.581644717955561,
   "seeds_margin_positive_n": 0,
   "seeds_margin_positive": [],
   "seeds_total": 8,
   "condition_dependence": {
    "_note": "the reversal is condition-dependent inside the R7 envelope - see ESC-2; full ensembles in gate_g1/<case>/ensemble. R23/F1: the positive-seed count at CdA 5.4 is exported here, not described in prose.",
    "margin_pct_ensemble_min_at_2000m_45C": -5.897136845667756,
    "passes_at_2000m_45C": false,
    "margin_pct_ensemble_min_hot_45C_sea_level": -3.492671913034174,
    "passes_hot_45C_sea_level": false,
    "margin_pct_ensemble_min_CdA_5.4": -0.09073577982911674,
    "margin_pct_ensemble_median_CdA_5.4": 0.016771049808426555,
    "margin_pct_ensemble_max_CdA_5.4": 0.11918244997996584,
    "seeds_margin_positive_n_CdA_5.4": 4,
    "seeds_margin_positive_CdA_5.4": [
     4,
     7,
     8,
     9
    ],
    "seeds_margin_positive_governing_case_CdA_5.4": "count over the enumerated 8-seed VOLT-REG ensemble [cda5.4]; positive = mode (a) beats mode (b) on that seed",
    "passes_CdA_5.4": false,
    "margin_pct_ensemble_min_aux_4kW": -2.2527522850057573,
    "passes_aux_4kW": false,
    "see": "ESC-2"
   }
  },
  "attribution_rows": {
   "_note": "directive item 3: one-factor rows at nominal. delta = row margin minus prior-convention margin, in percentage points; the two deltas plus their interaction close to the full G1-R shift",
   "prior_convention": {
    "min": 6.261345943773722,
    "median": 6.445177253781505,
    "max": 6.78407493099628
   },
   "spin_drag_alone": {
    "min": 4.493190881342169,
    "median": 4.679136782287627,
    "max": 4.975566042953862,
    "delta_pp_min": -1.7681550624315525,
    "delta_pp_median": -1.766040471493878
   },
   "map_vs_scalar_alone": {
    "min": -0.7522721079184456,
    "median": -0.6374822551781031,
    "max": -0.4909101286925496,
    "delta_pp_min": -7.013618051692167,
    "delta_pp_median": -7.082659508959608
   },
   "both_g1r": {
    "min": -2.5816447179555606,
    "median": -2.5036598384800866,
    "max": -2.3727109656800724,
    "delta_pp_min": -8.842990661729281,
    "delta_pp_median": -8.948837092261591
   }
  },
  "bracket_result": {
   "_note": "pre-adjudication adversarial finding: the G1-R SIGN rests on the WS4-DECLARED rectifier/conditioning member (pe0 0.15 kW + 1% of P_elec, TBC at procurement). Bracketed here by two hostile readings of R12; the KILL-CRITERION outcome is invariant - even the most hostile stacked reading leaves the nominal ensemble-min far below the +5% criterion.",
   "declared_member": {
    "min": -2.5816447179555606,
    "median": -2.5036598384800866,
    "max": -2.3727109656800724
   },
   "replacement_3pct_class": {
    "min": -0.7916261807090442,
    "median": -0.7066946346203603,
    "max": -0.5220928734765643
   },
   "stacked_declared_plus_3pct": {
    "min": 0.09078950046301505,
    "median": 0.14679322797276648,
    "max": 0.3442197675243981
   }
  },
  "map_vintage_robustness": {
   "432V": {
    "min": -2.862274116378697,
    "median": -2.7450734715314677,
    "max": -2.6106837552715656
   },
   "749V": {
    "min": -2.347413331542399,
    "median": -2.259488965080803,
    "max": -2.131529522984302
   },
   "spread": {
    "ruling": "R23 erratum F3",
    "members_432_749V_window": [
     -2.862274116378697,
     -2.5816447179555606,
     -2.347413331542399
    ],
    "spread_pp_432_749V_window": 0.5148607848362983,
    "members_incl_r3_interim": [
     -2.9798310816318927,
     -2.862274116378697,
     -2.5816447179555606,
     -2.347413331542399
    ],
    "spread_pp_incl_r3_interim": 0.6324177500894939,
    "governing_case": "max minus min over the enumerated set {nominal 662 V, 432 V map, 749 V map} and, for the second span, that set plus the r3-interim 370 V-vintage historical record",
    "note": "the r3 report printed 'under 0.6 pp' for a sentence whose parenthetical included the r3-interim figure: that span is 0.63 pp as printed. The 432-749 V window alone is the smaller span. Both are now rendered from this block."
   }
  },
  "provenance_hashes": {
   "ws2_inputs_sha256": {
    "map_file": "e0f617eafbcead33a8bb5edc07b95174826bd300be3b43b78b1593aa93c8ba4c",
    "results.json": "78266ce69cf6485e471b4e04d2f01c7c085f44730203d5a7a90aeaada1a69beb",
    "cycle_loss_summary.csv": "280f2549950abe3951ff4d9f5ffcd85a44d354f62591c3c6e5a14262ca15d7b9"
   },
   "kx_inputs_sha256": {
    "WS1/results.json": "14cb34639be0aa16a68ff508e4a27ffb714a5079fbe15eb1577e24e833c47f84",
    "WS1/volt_cycles.py": "d5f663d85e38979c7b55bbb7e7881dd0b0a4298a6ccd2d9089d7d60dfee4f2b1",
    "WS1/volt_params.py": "0ab8050a09c665c8b84210acf1218513ff9d4a9048a367113fbfa3a869505283",
    "WS1/volt_physics.py": "c99b5a770558b5a0279e893cc01e8ca2cacfbbf6313df711cb9f84a93d5d6e6c",
    "WS2/data/cycle_loss_summary.csv": "280f2549950abe3951ff4d9f5ffcd85a44d354f62591c3c6e5a14262ca15d7b9",
    "WS2/data/effmap_motor_inverter_662V.csv": "e0f617eafbcead33a8bb5edc07b95174826bd300be3b43b78b1593aa93c8ba4c",
    "WS2/results.json": "78266ce69cf6485e471b4e04d2f01c7c085f44730203d5a7a90aeaada1a69beb",
    "WS3/regen_acceptance.csv": "08cb24a3f8709d6f377c7a5243d7a67388e8917c5cfd0e8191321fadd9828bd1",
    "WS3/results.json": "0f766f86ef39e541506f7a83c576064d84bb3c9ad74b7bc598aa52cec0105a3b"
   }
  },
  "traction_chain_of_record": {
   "map_file": "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv",
   "map_file_owner": "WS2_traction_motor",
   "map_file_as_exported_by_owner": "data/effmap_motor_inverter_662V.csv",
   "map_voltage_V": 662.0,
   "vintage": "WS2 round-4 maps on the R10 662.4 V bus (chain of record)",
   "ws2_rework_round": 4,
   "reduction_flat": 0.97,
   "hot_swap": "re-running run_ws4.py after WS2 r4 lands consumes the 432/662/749 V maps and r4 spin member automatically (map keyed nearest WS2's exported dc_bus.nominal_V)"
  },
  "spin_drag_member": {
   "source": "WS2 data/cycle_loss_summary.csv (VOLT-REG column) + results.json topology PM_spin_* members",
   "e_spin_shaft_kWh_per_VOLT_REG": 1.4851,
   "e_spin_bus_kWh_per_VOLT_REG": 0.5017,
   "ws2_locked_hours": 1.2877635699999999,
   "rate_shaft_kW_while_locked": 1.1532396432056238,
   "rate_bus_kW_while_locked": 0.3895901481356551,
   "point_check_shaft_drag_85kmh_W": 1109.0,
   "point_check_bus_draw_85kmh_W": 371.0
  },
  "boundary_convention_exposure": {
   "_note": "R23/F4-F2: the map-boundary convention's measured exposure and its one-sided magnitude, per condition; full tables in results_ws4.json -> chain_boundary_exposure",
   "nominal_one_sided_pp_max": 0.0013047116643520745,
   "cda_5.4_one_sided_pp_max": 0.007916502468502453,
   "cda_5.4_one_sided_pp_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]"
  },
  "chain_weighting_convention": {
   "ruling": "R23 erratum F5",
   "ws2_cycle_share_weighted": {
    "eta_bus_to_wheel": 0.900548,
    "series_fuel_to_wheel_g_per_kWh": 237.56278147800234,
    "basis": "0.97 reduction x WS2's exported eta_mot_avg, which is energy-weighted over WS2's i-MMD VOLT-REG run - the motor handles the launch-heavy, mostly-unlocked share there. This is the right weighting for the BANKING REDEPLOY rate (s10 check 5), which is spent on that same share."
   },
   "series_duty_weighted": {
    "eta_bus_to_wheel_ref_seed": 0.9160217854635886,
    "eta_bus_to_wheel_min": 0.9160217854635886,
    "eta_bus_to_wheel_max": 0.9165456584568018,
    "eta_bus_to_wheel_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
    "series_fuel_to_wheel_g_per_kWh_ref_seed": 233.5497813801241,
    "per_seed": {
     "23": {
      "eta": 0.9160217854635886,
      "wheel_kWh": 78.85485355163588,
      "bus_kWh": 86.08403730455855
     },
     "3": {
      "eta": 0.9163228518667725,
      "wheel_kWh": 79.50778030559567,
      "bus_kWh": 86.7683045813154
     },
     "4": {
      "eta": 0.916251234852591,
      "wheel_kWh": 79.39046862260392,
      "bus_kWh": 86.64705225240594
     },
     "5": {
      "eta": 0.9162830960361059,
      "wheel_kWh": 79.5153510262148,
      "bus_kWh": 86.78033172302626
     },
     "6": {
      "eta": 0.9163611663115785,
      "wheel_kWh": 79.18399572684868,
      "bus_kWh": 86.41133936913774
     },
     "7": {
      "eta": 0.91623852872889,
      "wheel_kWh": 79.23267583315251,
      "bus_kWh": 86.47603582341496
     },
     "8": {
      "eta": 0.9165456584568018,
      "wheel_kWh": 79.42011242039227,
      "bus_kWh": 86.65156142260584
     },
     "9": {
      "eta": 0.91641298419424,
      "wheel_kWh": 79.45742508029507,
      "bus_kWh": 86.7048224443899
     }
    },
    "basis": "wheel energy / bus energy through the SAME WS2 map over the full VOLT-REG motoring trace - the weighting mode (b) actually realises in pure series"
   },
   "note": "the simulation is unaffected: it uses the map per sample, and its (b) delivers the realised wheel rate. The r3 report presented the cycle-share number as the trace-weighted chain; the series-duty companion is LARGER, so the r3 arithmetic understated the series advantage - the imprecision leaned conservative, toward the clutch."
  }
 },
 "series_duty_v2": {
  "_status": "live_design_input",
  "_basis": "R22a verification run ordered by KX_DIRECTIVE.md item 2: PURE SERIES V2 at the DELIVERED pack. Mode (b) - the genset pinned at its best-BSFC point with SOC-hysteresis start-stop - is the block of record; mode (b') - the same genset load-following along its best-BSFC locus - is carried as a COMPANION so WS5's R22b dispatch question has both endpoints on the same trace. WS4 does not choose the dispatch; R22b assigns that to WS5.",
  "_inputs": {
   "usable_bus_kWh": 11.083607999999998,
   "usable_source": "WS3 results.json -> interface_WS3.packs.V2.usable_bus_kWh (delivered 288s1p LTO pack), read at run time, not transcribed",
   "superseded_floor_kWh": 3.5,
   "superseded_floor_note": "the archived gate ran on the R8 3.5 kWh floor, which ESC-5/R22a identify as an i-MMD-era sizing; this run is at the delivered pack",
   "traction_chain": "R12: WS2 r4 measured inverter+motor map x 0.97 reduction, both directions, no scalar PE member",
   "r10_window": {
    "ruling": "R10 (BASELINE_v2)",
    "bus_class": "650 V class, pack-native",
    "nominal_V": 662.4,
    "operating_V": [
     432.0,
     748.8
    ],
    "charge_transient_10s_V": 777.6,
    "granularity": "12 cells (27.6 V)",
    "rectifier_device_class": "1200 V SiC (was 750 V class at the superseded 370 V bus)",
    "loss_model_at_new_window": "WS4-DECLARED: the exported loss model (iron+windage prop. to speed, copper prop. to T^2, rectifier 1% of P_elec + fixed) is carried unchanged at the new window - at this fidelity the voltage change trades conduction current for switching stress roughly evenly across a rewound machine + 1200 V SiC stage; confirm coefficients at procurement"
   },
   "r16_curve_file": "../WS3_battery/regen_acceptance.csv",
   "r16_column": "V2pack_chg_cont_kW_bus",
   "r16_declared_cell_temperature_C": {
    "nominal": 25.0,
    "cda_5.4": 25.0,
    "alt2000m_45C": 45.0
   },
   "r16_accept_kW_bus": {
    "nominal": 130.752,
    "cda_5.4": 130.752,
    "alt2000m_45C": 129.144
   },
   "r16_declaration_basis": "cell temperature declared equal to ambient for each case; WS3's pack-loop sizing line holds cells at or below 55 C at +45 C ambient, so 45 C is the tracking value and 55 C the loop's design ceiling - see r16_binding_analysis",
   "supervisor": "unchanged from the ratified simulator: SOC target 0.55, series hysteresis 0.35-0.75 of usable, emergency load-follow band 0.25-0.40. Nothing was tuned for this run; the hysteresis sensitivity below runs WS3's own allocated genset band instead.",
   "spin_member": "none charged: modes (b)/(b') never lock, and loaded series machine losses are inside WS2's maps (R22d). The true-COAST member R22d names is measured and reported separately, and is NOT charged to fuel.",
   "seeds": [
    23,
    3,
    4,
    5,
    6,
    7,
    8,
    9
   ]
  },
  "input_sha256": {
   "WS1/results.json": "14cb34639be0aa16a68ff508e4a27ffb714a5079fbe15eb1577e24e833c47f84",
   "WS1/volt_cycles.py": "d5f663d85e38979c7b55bbb7e7881dd0b0a4298a6ccd2d9089d7d60dfee4f2b1",
   "WS1/volt_params.py": "0ab8050a09c665c8b84210acf1218513ff9d4a9048a367113fbfa3a869505283",
   "WS1/volt_physics.py": "c99b5a770558b5a0279e893cc01e8ca2cacfbbf6313df711cb9f84a93d5d6e6c",
   "WS2/data/cycle_loss_summary.csv": "280f2549950abe3951ff4d9f5ffcd85a44d354f62591c3c6e5a14262ca15d7b9",
   "WS2/data/effmap_motor_inverter_662V.csv": "e0f617eafbcead33a8bb5edc07b95174826bd300be3b43b78b1593aa93c8ba4c",
   "WS2/results.json": "78266ce69cf6485e471b4e04d2f01c7c085f44730203d5a7a90aeaada1a69beb",
   "WS3/regen_acceptance.csv": "08cb24a3f8709d6f377c7a5243d7a67388e8917c5cfd0e8191321fadd9828bd1",
   "WS3/results.json": "0f766f86ef39e541506f7a83c576064d84bb3c9ad74b7bc598aa52cec0105a3b"
  },
  "trace_files": {
   "ruling": "R34 (BASELINE_v5 program hygiene)",
   "trace_10Hz": "data/trace_series_duty_v2_nominal_seed23_10Hz.csv",
   "trace_10Hz_rows": 66143,
   "soc_trajectories": "data/series_duty_v2_soc_trajectories.csv",
   "soc_decimation_s": 5.0
  },
  "unserved_energy_verdict": {
   "ruling": "R22a / ESC-5",
   "per_case_max_kWh": {
    "nominal": 0.0,
    "cda_5.4": 0.0,
    "alt2000m_45C": 0.0
   },
   "worst_case_kWh": 0.0,
   "worst_case_governing_case": "no governing case - every ordered case is exactly zero on all 8 seeds",
   "all_cases_zero": true,
   "criterion": "zero unserved bus energy on every seed of every ordered case; a nonzero value is a finding, not a tuning knob",
   "archived_gate_comparison": {
    "r8_floor_kWh": 3.5,
    "nominal_max_kWh": 0.0,
    "cda_5_4_max_kWh": 0.5217643472111702,
    "note": "the archived gate's mode (b) on the 3.5 kWh R8 floor shed up to this much at CdA 5.4 - the ESC-5 buffer problem R22a sends to the delivered pack"
   }
  },
  "r16_binding_analysis": {
   "ruling": "R16 (regen_acceptance.csv is the interface of record)",
   "peak_regen_to_pack_kW_bus": 69.1037568252313,
   "peak_regen_governing_case": "alt2000m_45C",
   "accept_kW_bus_at_declared_cells": {
    "nominal": 130.752,
    "cda_5.4": 130.752,
    "alt2000m_45C": 129.144
   },
   "bound_any_sample": false,
   "cold_side_binding_cell_C": -9.39321930659508,
   "hot_side_binding_cell_C": 53.9494966014262,
   "accept_at_ws3_loop_ceiling_55C_kW": 62.203,
   "note": "all three ordered cases are warm, so R16's curve is NOT binding in this run: peak regen-to-pack is far below the acceptance at the declared cell temperatures and regen_shed_by_r16_kWh is zero on every seed. The curve binds below the cold-side temperature above, and again above the hot-side one - and WS3's pack-loop SIZING LINE permits cells to 55 C at +45 C ambient, where acceptance falls to the value above. That hot-end crossing is escalated (ESC-8), not resolved here."
  },
  "soc_window_check": {
   "ruling": "WS3 interface_WS3.bus_voltage_window.soc15_note / r8_compliance",
   "ws3_statement": "120 kW warm at SOC 15 sits at 527.7 V; the R8 discharge gate is declared over SOC 40-90 and full power below SOC 40 is NOT guaranteed - WS5 dispatch limit",
   "ws3_end_stops_pct_nameplate": [
    15.0,
    9.999999999999998
   ],
   "gate_soc_nameplate": 0.4,
   "gate_soc_usable_equivalent": 0.3333333333333333,
   "mapping": "SOC_nameplate = end_stop_lo + SOC_usable x (1 - end_stop_hi - end_stop_lo); WS4-DECLARED reading of WS3's convention",
   "resolution_s": 5.0,
   "cases": {
    "nominal": {
     "t_below_gate_s_min": 290.0,
     "t_below_gate_s_max": 435.0,
     "t_below_gate_s_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_usable_min": 0.228683585303522,
     "soc_nameplate_min": 0.3215126889776415
    },
    "cda_5.4": {
     "t_below_gate_s_min": 825.0,
     "t_below_gate_s_max": 975.0,
     "t_below_gate_s_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_usable_min": 0.18370094808250353,
     "soc_nameplate_min": 0.2877757110618776
    },
    "alt2000m_45C": {
     "t_below_gate_s_min": 175.0,
     "t_below_gate_s_max": 185.0,
     "t_below_gate_s_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_usable_min": 0.24604432184799024,
     "soc_nameplate_min": 0.3345332413859927
    }
   },
   "reading": "the ordered run spends real time below the SOC band over which WS3 declares the R8 discharge peak, on every case. Combined with the bus-side power exceedance, that is the substance of ESC-9: it is a dispatch question, and WS4 does not answer it."
  },
  "r8_power_envelope_bracket": {
   "ruling": "R8 as restated by R12/ES-4 (125 kW discharge / 110 kW charge, bus-side)",
   "_status": "WS4 adversarial bracket, NOT an ordered case. The ordered series_duty_v2 numbers above stand as run; this bracket prices the assumption they rest on.",
   "dis_cap_bus_kW": 125.0,
   "chg_cap_bus_kW": 110.0,
   "enforcement": "discharge demand above the cap is unserved (booked and fuel-corrected exactly as the buffer-empty case is); charge above the cap is shed",
   "worst_unserved_kWh": 0.6128784190988547,
   "worst_unserved_governing_case": "alt2000m_45C",
   "reading": "R4/E24's 'the spine is not sized for forced series' record extends to the PACK's power envelope, not only the motor rating: the delivered pack has the ENERGY for pure-series VOLT-REG with margin, and the ordered run confirms that, but at its rated bus-side power it does not have the POWER on the hardest samples. This is a dispatch and rating question for WS5/WS3, not a WS4 tuning knob - escalated as ESC-9."
  },
  "r8_power_envelope_bracket_ensembles": {
   "nominal": {
    "unserved_bus_kWh_min": 0.0,
    "unserved_bus_kWh_max": 0.0021489573236746612,
    "unserved_bus_kWh_median": 0.0,
    "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "unserved_bus_kWh_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "r8_envelope_dis_clip_s_min": 0.0,
    "r8_envelope_dis_clip_s_max": 2.7999999999974534,
    "r8_envelope_dis_clip_s_median": 0.0,
    "r8_envelope_dis_clip_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "r8_envelope_dis_clip_s_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "r8_envelope_chg_shed_kWh_min": 0.3757080853860884,
    "r8_envelope_chg_shed_kWh_max": 0.47200450789572956,
    "r8_envelope_chg_shed_kWh_median": 0.42522800794261173,
    "r8_envelope_chg_shed_kWh_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "r8_envelope_chg_shed_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "fuel_kg_min": 18.97979743315774,
    "fuel_kg_max": 19.16224894390789,
    "fuel_kg_median": 19.110212617975797,
    "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "fuel_energy_kWh_per_km_min": 1.709995305406747,
    "fuel_energy_kWh_per_km_max": 1.72645645250984,
    "fuel_energy_kWh_per_km_median": 1.7217299732384896,
    "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "genset_starts_min": 5,
    "genset_starts_max": 5,
    "genset_starts_median": 5.0,
    "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]",
    "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/R8-envelope]"
   },
   "cda_5.4": {
    "unserved_bus_kWh_min": 3.726200263062815e-05,
    "unserved_bus_kWh_max": 0.014911090439962821,
    "unserved_bus_kWh_median": 0.0021266252038784133,
    "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "unserved_bus_kWh_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "r8_envelope_dis_clip_s_min": 0.1999999999998181,
    "r8_envelope_dis_clip_s_max": 8.899999999991905,
    "r8_envelope_dis_clip_s_median": 2.549999999997681,
    "r8_envelope_dis_clip_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "r8_envelope_dis_clip_s_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "r8_envelope_chg_shed_kWh_min": 0.4924101514347299,
    "r8_envelope_chg_shed_kWh_max": 0.6717454365479362,
    "r8_envelope_chg_shed_kWh_median": 0.6187023605098271,
    "r8_envelope_chg_shed_kWh_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "r8_envelope_chg_shed_kWh_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "fuel_kg_min": 22.513803089261778,
    "fuel_kg_max": 22.75472626083551,
    "fuel_kg_median": 22.678597821377927,
    "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "fuel_kg_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "fuel_energy_kWh_per_km_min": 2.028393491820551,
    "fuel_energy_kWh_per_km_max": 2.0501265123047347,
    "fuel_energy_kWh_per_km_median": 2.0432227910077225,
    "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "fuel_energy_kWh_per_km_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "genset_starts_min": 4,
    "genset_starts_max": 4,
    "genset_starts_median": 4.0,
    "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]",
    "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R8-envelope]"
   },
   "alt2000m_45C": {
    "unserved_bus_kWh_min": 0.5193746999437124,
    "unserved_bus_kWh_max": 0.6128784190988547,
    "unserved_bus_kWh_median": 0.5760024861492428,
    "unserved_bus_kWh_min_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "unserved_bus_kWh_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "r8_envelope_dis_clip_s_min": 82.19999999992524,
    "r8_envelope_dis_clip_s_max": 94.19999999991433,
    "r8_envelope_dis_clip_s_median": 86.84999999992101,
    "r8_envelope_dis_clip_s_min_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "r8_envelope_dis_clip_s_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "r8_envelope_chg_shed_kWh_min": 0.20246231374076482,
    "r8_envelope_chg_shed_kWh_max": 0.3471485729042831,
    "r8_envelope_chg_shed_kWh_median": 0.29322097791272744,
    "r8_envelope_chg_shed_kWh_min_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "r8_envelope_chg_shed_kWh_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "fuel_kg_min": 15.745093395619673,
    "fuel_kg_max": 15.8861143048148,
    "fuel_kg_median": 15.835527286203636,
    "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "fuel_energy_kWh_per_km_min": 1.4185628631981115,
    "fuel_energy_kWh_per_km_max": 1.4312873518729619,
    "fuel_energy_kWh_per_km_median": 1.4266907942631972,
    "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "genset_starts_min": 6,
    "genset_starts_max": 6,
    "genset_starts_median": 6.0,
    "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]",
    "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope]"
   }
  },
  "hysteresis_sensitivity_ref_seed": {
   "ruling": "R19 precedent / WS3 soc_strategy.allocation.V2",
   "ws3_allocated_genset_hysteresis_kWh": 3.5,
   "ws3_soc_target": 0.55,
   "band_soc_fraction": [
    0.39210917600117223,
    0.7078908239988279
   ],
   "simulator_band_soc_fraction": [
    0.35,
    0.75
   ],
   "simulator_band_kWh": 4.433443199999999,
   "cases": {
    "nominal": {
     "ws3_band": {
      "fuel_energy_kWh_per_km": 1.7047603676778533,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1214.6999999988952,
      "above_pin_demand_kWh": 8.10222289879555,
      "above_pin_engine_s": 121.19999999988977,
      "above_pin_transitions_per_h": 30.479876629070784,
      "genset_starts": 6,
      "genset_starts_per_h": 3.265701067400441,
      "genset_on_frac": 0.5760333827214984,
      "soc_min": 0.2483605013430112,
      "soc_max": 0.7257439099280615,
      "soc_end": 0.41696328492976426
     },
     "simulator_band": {
      "fuel_energy_kWh_per_km": 1.7010084250276258,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1214.6999999988952,
      "above_pin_demand_kWh": 8.10222289879555,
      "above_pin_engine_s": 0.0,
      "above_pin_transitions_per_h": 0.0,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7214175561670344,
      "genset_on_frac": 0.5919687944114842,
      "soc_min": 0.2571874614998088,
      "soc_max": 0.7548732761748025,
      "soc_end": 0.524303617571101
     }
    },
    "cda_5.4": {
     "ws3_band": {
      "fuel_energy_kWh_per_km": 2.0256847779590705,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1846.9999999983202,
      "above_pin_demand_kWh": 13.927364366523825,
      "above_pin_engine_s": 493.29999999955135,
      "above_pin_transitions_per_h": 17.417072359469017,
      "genset_starts": 6,
      "genset_starts_per_h": 3.265701067400441,
      "genset_on_frac": 0.6749569108883333,
      "soc_min": 0.16505111557726426,
      "soc_max": 0.7080680940889869,
      "soc_end": 0.7074777284814147
     },
     "simulator_band": {
      "fuel_energy_kWh_per_km": 2.018848800489633,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1846.9999999983202,
      "above_pin_demand_kWh": 13.927364366523825,
      "above_pin_engine_s": 468.09999999957427,
      "above_pin_transitions_per_h": 14.151371292068578,
      "genset_starts": 4,
      "genset_starts_per_h": 2.177134044933627,
      "genset_on_frac": 0.6678056303101573,
      "soc_min": 0.18334485346337365,
      "soc_max": 0.7681056509960934,
      "soc_end": 0.572763611256311
     }
    },
    "alt2000m_45C": {
     "ws3_band": {
      "fuel_energy_kWh_per_km": 1.4213951699960017,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 701.3999999993621,
      "above_pin_demand_kWh": 4.55030999200612,
      "above_pin_engine_s": 87.39999999992051,
      "above_pin_transitions_per_h": 8.708536179734509,
      "genset_starts": 9,
      "genset_starts_per_h": 4.898551601100662,
      "genset_on_frac": 0.49674941791857086,
      "soc_min": 0.24740871909053874,
      "soc_max": 0.7901808001721989,
      "soc_end": 0.6868681447623254
     },
     "simulator_band": {
      "fuel_energy_kWh_per_km": 1.4131393969351607,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 701.3999999993621,
      "above_pin_demand_kWh": 4.55030999200612,
      "above_pin_engine_s": 91.99999999991633,
      "above_pin_transitions_per_h": 8.708536179734509,
      "genset_starts": 6,
      "genset_starts_per_h": 3.265701067400441,
      "genset_on_frac": 0.48150947960404933,
      "soc_min": 0.24700156614166152,
      "soc_max": 0.8031287374028468,
      "soc_end": 0.5101868726716788
     }
    }
   }
  },
  "r22d_coast_spin_member": {
   "ruling": "R22d",
   "ws2_point_drag_85kmh_W": {
    "shaft": 1109.0,
    "bus": 371.0
   },
   "scaling": "[WS4-DECLARED] linear in road speed from WS2's 85 km/h point",
   "coast_no_regen_s_max": 26.099999999976262,
   "coast_spin_shaft_kWh_max": 0.00017454623149206134,
   "coast_spin_bus_kWh_max": 5.839193136479234e-05,
   "unbooked_pp_of_cycle_fuel": {
    "nominal": 0.0002776645392806949,
    "cda_5.4": 0.00023546494767478026,
    "alt2000m_45C": 0.000336470735977268
   },
   "unbooked_pp_max": 0.000336470735977268,
   "unbooked_pp_max_governing_case": "alt2000m_45C",
   "charged_to_fuel": false,
   "direction_of_error": "series_duty_v2's fuel numbers EXCLUDE this member, so they are optimistic by the percentage points above. R22d's own remedy - the WS5 supervisor preferring light regen over true coast - removes the exposure by removing the true-coast samples; the member is exported so WS5 can price that choice."
  },
  "cases": {
   "nominal": {
    "condition": "sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, 2 kW aux, GVW 6,600 kg, VOLT-REG",
    "declared_cell_temperature_C": 25.0,
    "r16_accept_kW_bus": 130.752,
    "pinned_point": {
     "rpm": 1287.96992481203,
     "trq_Nm": 627.9824561403509,
     "p_shaft_kw": 84.69969589648574,
     "bsfc": 203.61665610230665,
     "p_bus_kw": 80.61389111871986,
     "fuel_gps": 4.790630236479081,
     "eta_gen": 0.9517612816135814
    },
    "ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_demand_s_min": 1201.799999998907,
     "above_pin_demand_s_max": 1274.8999999988405,
     "above_pin_demand_s_median": 1254.3999999988591,
     "above_pin_demand_s_min_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_demand_s_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_demand_kWh_min": 7.971742215398501,
     "above_pin_demand_kWh_max": 8.381291272280707,
     "above_pin_demand_kWh_median": 8.087501630135147,
     "above_pin_demand_kWh_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_demand_kWh_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_engine_s_min": 0.0,
     "above_pin_engine_s_max": 274.2999999997505,
     "above_pin_engine_s_median": 130.9499999998809,
     "above_pin_engine_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_engine_s_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_transitions_per_h_min": 0.0,
     "above_pin_transitions_per_h_max": 45.955351579715206,
     "above_pin_transitions_per_h_median": 30.676621367553086,
     "above_pin_transitions_per_h_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "above_pin_transitions_per_h_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_starts_min": 5,
     "genset_starts_max": 6,
     "genset_starts_median": 5.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_starts_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_starts_per_h_min": 2.7214175561670344,
     "genset_starts_per_h_max": 3.287721274296412,
     "genset_starts_per_h_median": 2.7381631490460276,
     "genset_starts_per_h_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_starts_per_h_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_on_frac_min": 0.581515700390649,
     "genset_on_frac_max": 0.6008340689775667,
     "genset_on_frac_median": 0.5930244293381869,
     "genset_on_frac_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "genset_on_frac_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_min_min": 0.22837639156920697,
     "soc_min_max": 0.2620142706113847,
     "soc_min_median": 0.24992161448643135,
     "soc_min_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_min_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_max_min": 0.7505793516234933,
     "soc_max_max": 0.7552478645863544,
     "soc_max_median": 0.7542013971094425,
     "soc_max_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_max_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_end_min": 0.5115963213972812,
     "soc_end_max": 0.5583817548716639,
     "soc_end_median": 0.5220461442155716,
     "soc_end_min_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "soc_end_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_energy_kWh_per_km_min": 1.7010084250276258,
     "fuel_energy_kWh_per_km_max": 1.728099220748916,
     "fuel_energy_kWh_per_km_median": 1.7153581462494394,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_energy_kWh_per_payload_tonne_km_min": 0.586554629319871,
     "fuel_energy_kWh_per_payload_tonne_km_max": 0.5958962830168676,
     "fuel_energy_kWh_per_payload_tonne_km_median": 0.5915028090515309,
     "fuel_energy_kWh_per_payload_tonne_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_energy_kWh_per_payload_tonne_km_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "l_per_100km_min": 17.196571514702367,
     "l_per_100km_max": 17.47044952680204,
     "l_per_100km_median": 17.341641935034325,
     "l_per_100km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "l_per_100km_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_kg_min": 18.880049107175545,
     "fuel_kg_max": 19.180486903463734,
     "fuel_kg_median": 19.039339234821135,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "fuel_kg_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "emergency_band_s_min": 0.0,
     "emergency_band_s_max": 404.99999999963165,
     "emergency_band_s_median": 257.64999999976567,
     "emergency_band_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "emergency_band_s_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "motor_over_rating_s_min": 42.09999999996171,
     "motor_over_rating_s_max": 71.49999999993497,
     "motor_over_rating_s_median": 60.89999999994461,
     "motor_over_rating_s_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "motor_over_rating_s_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_dis_peak_kW_min": 115.06812614236642,
     "pack_dis_peak_kW_max": 184.51958532945014,
     "pack_dis_peak_kW_median": 124.10837889026426,
     "pack_dis_peak_kW_min_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_dis_peak_kW_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_chg_peak_kW_min": 147.50564858624014,
     "pack_chg_peak_kW_max": 147.58458351650407,
     "pack_chg_peak_kW_median": 147.5324420842902,
     "pack_chg_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_chg_peak_kW_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_dis_over_r8_125kW_s_min": 0.0,
     "pack_dis_over_r8_125kW_s_max": 74.99999999993179,
     "pack_dis_over_r8_125kW_s_median": 0.8499999999992269,
     "pack_dis_over_r8_125kW_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_dis_over_r8_125kW_s_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_chg_over_r8_110kW_s_min": 55.99999999994907,
     "pack_chg_over_r8_110kW_s_max": 69.89999999993643,
     "pack_chg_over_r8_110kW_s_median": 64.74999999994111,
     "pack_chg_over_r8_110kW_s_min_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "pack_chg_over_r8_110kW_s_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "regen_bus_peak_kW_min": 68.89175746752028,
     "regen_bus_peak_kW_max": 68.9706923977842,
     "regen_bus_peak_kW_median": 68.91855096557035,
     "regen_bus_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "regen_bus_peak_kW_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "regen_shed_by_r16_kWh_min": 0.0,
     "regen_shed_by_r16_kWh_max": 0.0,
     "regen_shed_by_r16_kWh_median": 0.0,
     "regen_shed_by_r16_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "regen_shed_by_r16_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "engine_reject_kWh_min": 130.8823361002044,
     "engine_reject_kWh_max": 133.29739780475987,
     "engine_reject_kWh_median": 131.9582558483683,
     "engine_reject_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]",
     "engine_reject_kWh_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [nominal]"
    },
    "per_seed_ordered_exports": {
     "23": {
      "fuel_energy_kWh_per_km": 1.7010084250276258,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1214.6999999988952,
      "above_pin_demand_kWh": 8.10222289879555,
      "above_pin_engine_s": 0.0,
      "above_pin_transitions_per_h": 0.0,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7214175561670344,
      "genset_on_frac": 0.5919687944114842,
      "soc_min": 0.2571874614998088,
      "soc_max": 0.7548732761748025,
      "soc_end": 0.524303617571101
     },
     "3": {
      "fuel_energy_kWh_per_km": 1.7187444569079067,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1259.8999999988541,
      "above_pin_demand_kWh": 8.381291272280707,
      "above_pin_engine_s": 152.09999999986167,
      "above_pin_transitions_per_h": 39.42984924776001,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7381839755388895,
      "genset_on_frac": 0.595205135615626,
      "soc_min": 0.24991186779707017,
      "soc_max": 0.7532785617421379,
      "soc_end": 0.516177812355362
     },
     "4": {
      "fuel_energy_kWh_per_km": 1.7147353428317693,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1201.799999998907,
      "above_pin_demand_kWh": 8.046101992785177,
      "above_pin_engine_s": 109.79999999990014,
      "above_pin_transitions_per_h": 29.571937083574188,
      "genset_starts": 5,
      "genset_starts_per_h": 2.738142322553166,
      "genset_on_frac": 0.5934315008056911,
      "soc_min": 0.24993136117579257,
      "soc_max": 0.7537076816459853,
      "soc_end": 0.5115963213972812
     },
     "5": {
      "fuel_energy_kWh_per_km": 1.728099220748916,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1274.8999999988405,
      "above_pin_demand_kWh": 8.207239087686897,
      "above_pin_engine_s": 274.2999999997505,
      "above_pin_transitions_per_h": 31.781305651531984,
      "genset_starts": 6,
      "genset_starts_per_h": 3.287721274296412,
      "genset_on_frac": 0.581515700390649,
      "soc_min": 0.22837639156920697,
      "soc_max": 0.7505793516234933,
      "soc_end": 0.5171393460294404
     },
     "6": {
      "fuel_energy_kWh_per_km": 1.7163834903573492,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1248.3999999988646,
      "above_pin_demand_kWh": 7.997852053656372,
      "above_pin_engine_s": 192.2999999998251,
      "above_pin_transitions_per_h": 32.77345350266284,
      "genset_starts": 6,
      "genset_starts_per_h": 3.277345350266284,
      "genset_on_frac": 0.5874186353492767,
      "soc_min": 0.2478407527330907,
      "soc_max": 0.7552478645863544,
      "soc_end": 0.5583817548716639
     },
     "7": {
      "fuel_energy_kWh_per_km": 1.7113322299534086,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1258.899999998855,
      "above_pin_demand_kWh": 8.072780361474747,
      "above_pin_engine_s": 0.0,
      "above_pin_transitions_per_h": 0.0,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7309968138370504,
      "genset_on_frac": 0.5987710514332287,
      "soc_min": 0.2572546396029086,
      "soc_max": 0.7551138928591565,
      "soc_end": 0.5385397895490047
     },
     "8": {
      "fuel_energy_kWh_per_km": 1.7117702107447466,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1274.5999999988408,
      "above_pin_demand_kWh": 7.971742215398501,
      "above_pin_engine_s": 166.19999999984884,
      "above_pin_transitions_per_h": 45.955351579715206,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7354375940306674,
      "genset_on_frac": 0.5926173578706827,
      "soc_min": 0.2498642203155622,
      "soc_max": 0.7515654957280979,
      "soc_end": 0.5321929468801848
     },
     "9": {
      "fuel_energy_kWh_per_km": 1.7159809496671097,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1249.8999999988632,
      "above_pin_demand_kWh": 8.190524505651016,
      "above_pin_engine_s": 0.0,
      "above_pin_transitions_per_h": 0.0,
      "genset_starts": 5,
      "genset_starts_per_h": 2.7396426288393045,
      "genset_on_frac": 0.6008340689775667,
      "soc_min": 0.2620142706113847,
      "soc_max": 0.7546951125728996,
      "soc_end": 0.5197886708600422
     }
    },
    "per_seed_full": "results_ws4.json -> series_duty_v2 -> cases -> nominal -> per_seed (all 37 fields, same run)",
    "companion_bp_ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "r8_envelope_dis_clip_s_min": 0.0,
     "r8_envelope_dis_clip_s_max": 0.0,
     "r8_envelope_dis_clip_s_median": 0.0,
     "r8_envelope_dis_clip_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "r8_envelope_dis_clip_s_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "r8_envelope_chg_shed_kWh_min": 0.0,
     "r8_envelope_chg_shed_kWh_max": 0.0,
     "r8_envelope_chg_shed_kWh_median": 0.0,
     "r8_envelope_chg_shed_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "r8_envelope_chg_shed_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "fuel_kg_min": 18.932891656904445,
     "fuel_kg_max": 19.107458980595702,
     "fuel_kg_median": 19.051397101213446,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "fuel_energy_kWh_per_km_min": 1.7057693036555654,
     "fuel_energy_kWh_per_km_max": 1.7215200545969436,
     "fuel_energy_kWh_per_km_median": 1.7164223947211652,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "genset_starts_min": 1,
     "genset_starts_max": 1,
     "genset_starts_median": 1.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]",
     "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal/bp]"
    }
   },
   "cda_5.4": {
    "condition": "E13 high-drag body, CdA 5.4 m^2, otherwise nominal",
    "declared_cell_temperature_C": 25.0,
    "r16_accept_kW_bus": 130.752,
    "pinned_point": {
     "rpm": 1287.96992481203,
     "trq_Nm": 627.9824561403509,
     "p_shaft_kw": 84.69969589648574,
     "bsfc": 203.61665610230665,
     "p_bus_kw": 80.61389111871986,
     "fuel_gps": 4.790630236479081,
     "eta_gen": 0.9517612816135814
    },
    "ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_demand_s_min": 1846.9999999983202,
     "above_pin_demand_s_max": 1984.3999999981952,
     "above_pin_demand_s_median": 1948.299999998228,
     "above_pin_demand_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_demand_s_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_demand_kWh_min": 13.927364366523825,
     "above_pin_demand_kWh_max": 14.394265499508458,
     "above_pin_demand_kWh_median": 14.114141617562042,
     "above_pin_demand_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_demand_kWh_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_engine_s_min": 418.09999999961974,
     "above_pin_engine_s_max": 486.9999999995571,
     "above_pin_engine_s_median": 430.5499999996084,
     "above_pin_engine_s_min_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_engine_s_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_transitions_per_h_min": 14.151371292068578,
     "above_pin_transitions_per_h_max": 41.61976330280812,
     "above_pin_transitions_per_h_median": 20.786700719169698,
     "above_pin_transitions_per_h_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "above_pin_transitions_per_h_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_starts_min": 4,
     "genset_starts_max": 4,
     "genset_starts_median": 4.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_starts_per_h_min": 2.177134044933627,
     "genset_starts_per_h_max": 2.1918141828642748,
     "genset_starts_per_h_median": 2.189431966633533,
     "genset_starts_per_h_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_starts_per_h_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_on_frac_min": 0.6678056303101573,
     "genset_on_frac_max": 0.6852505400221731,
     "genset_on_frac_median": 0.6811524415087578,
     "genset_on_frac_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "genset_on_frac_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_min_min": 0.18334485346337365,
     "soc_min_max": 0.2222417487425971,
     "soc_min_median": 0.20856748788529494,
     "soc_min_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_min_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_max_min": 0.7563731184232202,
     "soc_max_max": 0.7699315197221807,
     "soc_max_median": 0.7664290169609327,
     "soc_max_min_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_max_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_end_min": 0.550315559390451,
     "soc_end_max": 0.577904541949883,
     "soc_end_median": 0.5737999159643306,
     "soc_end_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "soc_end_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_energy_kWh_per_km_min": 2.018848800489633,
     "fuel_energy_kWh_per_km_max": 2.0378064476340145,
     "fuel_energy_kWh_per_km_median": 2.0320008359694812,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_energy_kWh_per_payload_tonne_km_min": 0.6961547587895286,
     "fuel_energy_kWh_per_payload_tonne_km_max": 0.7026918784944878,
     "fuel_energy_kWh_per_payload_tonne_km_median": 0.7006899434377523,
     "fuel_energy_kWh_per_payload_tonne_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_energy_kWh_per_payload_tonne_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "l_per_100km_min": 20.409821176768844,
     "l_per_100km_max": 20.601476038715553,
     "l_per_100km_median": 20.54278343337227,
     "l_per_100km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "l_per_100km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_kg_min": 22.407863437000717,
     "fuel_kg_max": 22.617978224875632,
     "fuel_kg_median": 22.5540397700572,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "emergency_band_s_min": 467.4999999995748,
     "emergency_band_s_max": 644.8999999994135,
     "emergency_band_s_median": 580.4499999994721,
     "emergency_band_s_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "emergency_band_s_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "motor_over_rating_s_min": 110.39999999989959,
     "motor_over_rating_s_max": 137.49999999987494,
     "motor_over_rating_s_median": 122.5999999998885,
     "motor_over_rating_s_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "motor_over_rating_s_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_dis_peak_kW_min": 125.96166476162736,
     "pack_dis_peak_kW_max": 142.22844638407688,
     "pack_dis_peak_kW_median": 130.01147495956496,
     "pack_dis_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_dis_peak_kW_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_chg_peak_kW_min": 147.50564858624014,
     "pack_chg_peak_kW_max": 147.58458351650407,
     "pack_chg_peak_kW_median": 147.5324420842902,
     "pack_chg_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_chg_peak_kW_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_dis_over_r8_125kW_s_min": 0.1999999999998181,
     "pack_dis_over_r8_125kW_s_max": 8.899999999991905,
     "pack_dis_over_r8_125kW_s_median": 2.549999999997681,
     "pack_dis_over_r8_125kW_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_dis_over_r8_125kW_s_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_chg_over_r8_110kW_s_min": 58.09999999994716,
     "pack_chg_over_r8_110kW_s_max": 79.39999999992779,
     "pack_chg_over_r8_110kW_s_median": 66.79999999993925,
     "pack_chg_over_r8_110kW_s_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "pack_chg_over_r8_110kW_s_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "regen_bus_peak_kW_min": 68.89175746752028,
     "regen_bus_peak_kW_max": 68.9706923977842,
     "regen_bus_peak_kW_median": 68.91855096557035,
     "regen_bus_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "regen_bus_peak_kW_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "regen_shed_by_r16_kWh_min": 0.0,
     "regen_shed_by_r16_kWh_max": 0.0,
     "regen_shed_by_r16_kWh_median": 0.0,
     "regen_shed_by_r16_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "regen_shed_by_r16_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "engine_reject_kWh_min": 157.23810552623436,
     "engine_reject_kWh_max": 158.54764795738947,
     "engine_reject_kWh_median": 158.01311683069966,
     "engine_reject_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]",
     "engine_reject_kWh_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]"
    },
    "per_seed_ordered_exports": {
     "23": {
      "fuel_energy_kWh_per_km": 2.018848800489633,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1846.9999999983202,
      "above_pin_demand_kWh": 13.927364366523825,
      "above_pin_engine_s": 468.09999999957427,
      "above_pin_transitions_per_h": 14.151371292068578,
      "genset_starts": 4,
      "genset_starts_per_h": 2.177134044933627,
      "genset_on_frac": 0.6678056303101573,
      "soc_min": 0.18334485346337365,
      "soc_max": 0.7681056509960934,
      "soc_end": 0.572763611256311
     },
     "3": {
      "fuel_energy_kWh_per_km": 2.0378064476340145,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1937.8999999982375,
      "above_pin_demand_kWh": 14.394265499508458,
      "above_pin_engine_s": 420.59999999961747,
      "above_pin_transitions_per_h": 24.096018984742226,
      "genset_starts": 4,
      "genset_starts_per_h": 2.1905471804311114,
      "genset_on_frac": 0.6836636901589246,
      "soc_min": 0.21005802802766338,
      "soc_max": 0.7669699469246444,
      "soc_end": 0.5704398976887516
     },
     "4": {
      "fuel_energy_kWh_per_km": 2.0311775578879967,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1952.699999998224,
      "above_pin_demand_kWh": 14.03891094244632,
      "above_pin_engine_s": 418.39999999961947,
      "above_pin_transitions_per_h": 41.61976330280812,
      "genset_starts": 4,
      "genset_starts_per_h": 2.1905138580425323,
      "genset_on_frac": 0.6852505400221731,
      "soc_min": 0.20707694774292648,
      "soc_max": 0.7563731184232202,
      "soc_end": 0.5679304617812294
     },
     "5": {
      "fuel_energy_kWh_per_km": 2.0367246464033233,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1978.9999999982,
      "above_pin_demand_kWh": 14.290062971662417,
      "above_pin_engine_s": 432.69999999960646,
      "above_pin_transitions_per_h": 24.109956011507023,
      "genset_starts": 4,
      "genset_starts_per_h": 2.1918141828642748,
      "genset_on_frac": 0.6831306412575079,
      "soc_min": 0.21380869882902365,
      "soc_max": 0.7642091242191806,
      "soc_end": 0.550315559390451
     },
     "6": {
      "fuel_energy_kWh_per_km": 2.0279391988689577,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1984.3999999981952,
      "above_pin_demand_kWh": 13.99919299011322,
      "above_pin_engine_s": 428.3999999996104,
      "above_pin_transitions_per_h": 18.571623651508943,
      "genset_starts": 4,
      "genset_starts_per_h": 2.184896900177523,
      "genset_on_frac": 0.6778035716991556,
      "soc_min": 0.1928383325066672,
      "soc_max": 0.765888086997221,
      "soc_end": 0.5748362206723501
     },
     "7": {
      "fuel_energy_kWh_per_km": 2.0291985345894594,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1930.0999999982446,
      "above_pin_demand_kWh": 14.074268625193247,
      "above_pin_engine_s": 418.09999999961974,
      "above_pin_transitions_per_h": 21.847974510696403,
      "genset_starts": 4,
      "genset_starts_per_h": 2.1847974510696404,
      "genset_on_frac": 0.6819450766192877,
      "soc_min": 0.2222417487425971,
      "soc_max": 0.7687387009173612,
      "soc_end": 0.577904541949883
     },
     "8": {
      "fuel_energy_kWh_per_km": 2.0328241140509657,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1964.799999998213,
      "above_pin_demand_kWh": 14.154014609930838,
      "above_pin_engine_s": 486.9999999995571,
      "above_pin_transitions_per_h": 18.60097563940854,
      "genset_starts": 4,
      "genset_starts_per_h": 2.188350075224534,
      "genset_on_frac": 0.6724769387410106,
      "soc_min": 0.1900333974108523,
      "soc_max": 0.7699315197221807,
      "soc_end": 0.5751446293992108
     },
     "9": {
      "fuel_energy_kWh_per_km": 2.036180383069028,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 1943.899999998232,
      "above_pin_demand_kWh": 14.268554297453921,
      "above_pin_engine_s": 482.5999999995611,
      "above_pin_transitions_per_h": 19.725426927642992,
      "genset_starts": 4,
      "genset_starts_per_h": 2.1917141030714435,
      "genset_on_frac": 0.6803598063982277,
      "soc_min": 0.2123765037347763,
      "soc_max": 0.758147168242584,
      "soc_end": 0.5766936459654762
     }
    },
    "per_seed_full": "results_ws4.json -> series_duty_v2 -> cases -> cda_5.4 -> per_seed (all 37 fields, same run)",
    "companion_bp_ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "r8_envelope_dis_clip_s_min": 0.0,
     "r8_envelope_dis_clip_s_max": 0.0,
     "r8_envelope_dis_clip_s_median": 0.0,
     "r8_envelope_dis_clip_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "r8_envelope_dis_clip_s_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "r8_envelope_chg_shed_kWh_min": 0.0,
     "r8_envelope_chg_shed_kWh_max": 0.0,
     "r8_envelope_chg_shed_kWh_median": 0.0,
     "r8_envelope_chg_shed_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "r8_envelope_chg_shed_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "fuel_kg_min": 22.396448126836976,
     "fuel_kg_max": 22.616163532947123,
     "fuel_kg_median": 22.544487762901635,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "fuel_energy_kWh_per_km_min": 2.0178203318319192,
     "fuel_energy_kWh_per_km_max": 2.0376429497795376,
     "fuel_energy_kWh_per_km_median": 2.031140172889355,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "genset_starts_min": 1,
     "genset_starts_max": 1,
     "genset_starts_median": 1.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]",
     "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/bp]"
    }
   },
   "alt2000m_45C": {
    "condition": "2,000 m / +45 C: rho 0.8706 kg/m^3 and engine derate 0.9312. IDENTICAL to the archived gate's alt2000m_45C case (GVW, CdA 4.2, 2 kW aux) - NOT the stricter R6 RATING corner, which additionally carries +20% payload, CdA 5.4 and 4 kW aux and is used to size the engine, not to run the duty",
    "declared_cell_temperature_C": 45.0,
    "r16_accept_kW_bus": 129.144,
    "pinned_point": {
     "rpm": 1287.96992481203,
     "trq_Nm": 627.9824561403509,
     "p_shaft_kw": 84.69969589648574,
     "bsfc": 203.61665610230665,
     "p_bus_kw": 80.61389111871986,
     "fuel_gps": 4.790630236479081,
     "eta_gen": 0.9517612816135814
    },
    "ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_demand_s_min": 690.7999999993717,
     "above_pin_demand_s_max": 741.6999999993254,
     "above_pin_demand_s_median": 709.6499999993546,
     "above_pin_demand_s_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_demand_s_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_demand_kWh_min": 4.303881117458673,
     "above_pin_demand_kWh_max": 4.686930193971569,
     "above_pin_demand_kWh_median": 4.548251843482976,
     "above_pin_demand_kWh_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_demand_kWh_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_engine_s_min": 80.39999999992688,
     "above_pin_engine_s_max": 100.5999999999085,
     "above_pin_engine_s_median": 89.69999999991842,
     "above_pin_engine_s_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_engine_s_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_transitions_per_h_min": 6.554690700532568,
     "above_pin_transitions_per_h_max": 14.246141669964384,
     "above_pin_transitions_per_h_median": 8.760328516177617,
     "above_pin_transitions_per_h_min_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "above_pin_transitions_per_h_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_starts_min": 6,
     "genset_starts_max": 6,
     "genset_starts_median": 6.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_starts_per_h_min": 3.265701067400441,
     "genset_starts_per_h_max": 3.287721274296412,
     "genset_starts_per_h_median": 3.2841479499502997,
     "genset_starts_per_h_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_starts_per_h_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_on_frac_min": 0.48150947960404933,
     "genset_on_frac_max": 0.48981140091296277,
     "genset_on_frac_median": 0.48827726992177967,
     "genset_on_frac_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "genset_on_frac_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_min_min": 0.24589061524785094,
     "soc_min_max": 0.2499675876076418,
     "soc_min_median": 0.24795810873462198,
     "soc_min_min_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_min_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_max_min": 0.797535825889751,
     "soc_max_max": 0.8085924684419679,
     "soc_max_median": 0.8027119447979026,
     "soc_max_min_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_max_max_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_end_min": 0.4946673303025574,
     "soc_end_max": 0.5605178219174858,
     "soc_end_median": 0.5084957533435268,
     "soc_end_min_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "soc_end_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_energy_kWh_per_km_min": 1.4131393969351607,
     "fuel_energy_kWh_per_km_max": 1.4260734657051741,
     "fuel_energy_kWh_per_km_median": 1.4217595332112802,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_energy_kWh_per_payload_tonne_km_min": 0.48728944721902095,
     "fuel_energy_kWh_per_payload_tonne_km_max": 0.4917494709328187,
     "fuel_energy_kWh_per_payload_tonne_km_median": 0.4902619080038897,
     "fuel_energy_kWh_per_payload_tonne_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_energy_kWh_per_payload_tonne_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "l_per_100km_min": 14.286321185766138,
     "l_per_100km_max": 14.417079878849037,
     "l_per_100km_median": 14.37346760300764,
     "l_per_100km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "l_per_100km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_kg_min": 15.684896568920262,
     "fuel_kg_max": 15.828244449732674,
     "fuel_kg_median": 15.78079225863235,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "emergency_band_s_min": 187.39999999982956,
     "emergency_band_s_max": 221.89999999979818,
     "emergency_band_s_median": 204.499999999814,
     "emergency_band_s_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "emergency_band_s_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "motor_over_rating_s_min": 11.999999999989086,
     "motor_over_rating_s_max": 22.699999999979354,
     "motor_over_rating_s_median": 15.24999999998613,
     "motor_over_rating_s_min_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "motor_over_rating_s_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_dis_peak_kW_min": 166.23803527878812,
     "pack_dis_peak_kW_max": 192.4662473109739,
     "pack_dis_peak_kW_median": 180.2309375895033,
     "pack_dis_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_dis_peak_kW_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_chg_peak_kW_min": 147.4733249946928,
     "pack_chg_peak_kW_max": 147.47335735552923,
     "pack_chg_peak_kW_median": 147.47334269994232,
     "pack_chg_peak_kW_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_chg_peak_kW_max_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_dis_over_r8_125kW_s_min": 70.6999999999357,
     "pack_dis_over_r8_125kW_s_max": 80.79999999992651,
     "pack_dis_over_r8_125kW_s_median": 72.74999999993383,
     "pack_dis_over_r8_125kW_s_min_governing_case": "seed 5 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_dis_over_r8_125kW_s_max_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_chg_over_r8_110kW_s_min": 48.69999999995571,
     "pack_chg_over_r8_110kW_s_max": 68.69999999993752,
     "pack_chg_over_r8_110kW_s_median": 57.64999999994757,
     "pack_chg_over_r8_110kW_s_min_governing_case": "seed 7 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "pack_chg_over_r8_110kW_s_max_governing_case": "seed 4 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "regen_bus_peak_kW_min": 69.09176836568213,
     "regen_bus_peak_kW_max": 69.1037568252313,
     "regen_bus_peak_kW_median": 69.10299339320119,
     "regen_bus_peak_kW_min_governing_case": "seed 8 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "regen_bus_peak_kW_max_governing_case": "seed 9 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "regen_shed_by_r16_kWh_min": 0.0,
     "regen_shed_by_r16_kWh_max": 0.0,
     "regen_shed_by_r16_kWh_median": 0.0,
     "regen_shed_by_r16_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "regen_shed_by_r16_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "engine_reject_kWh_min": 108.53753436798314,
     "engine_reject_kWh_max": 109.75630859221401,
     "engine_reject_kWh_median": 109.32660520835277,
     "engine_reject_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]",
     "engine_reject_kWh_max_governing_case": "seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]"
    },
    "per_seed_ordered_exports": {
     "23": {
      "fuel_energy_kWh_per_km": 1.4131393969351607,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 701.3999999993621,
      "above_pin_demand_kWh": 4.55030999200612,
      "above_pin_engine_s": 91.99999999991633,
      "above_pin_transitions_per_h": 8.708536179734509,
      "genset_starts": 6,
      "genset_starts_per_h": 3.265701067400441,
      "genset_on_frac": 0.48150947960404933,
      "soc_min": 0.24700156614166152,
      "soc_max": 0.8031287374028468,
      "soc_end": 0.5101868726716788
     },
     "3": {
      "fuel_energy_kWh_per_km": 1.4260734657051741,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 739.4999999993274,
      "above_pin_demand_kWh": 4.686930193971569,
      "above_pin_engine_s": 85.79999999992197,
      "above_pin_transitions_per_h": 10.952735902155558,
      "genset_starts": 6,
      "genset_starts_per_h": 3.2858207706466676,
      "genset_on_frac": 0.4881573543053503,
      "soc_min": 0.2475832335242371,
      "soc_max": 0.797535825889751,
      "soc_end": 0.4946673303025574
     },
     "4": {
      "fuel_energy_kWh_per_km": 1.4222549014250376,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 703.3999999993603,
      "above_pin_demand_kWh": 4.496587477258463,
      "above_pin_engine_s": 92.19999999991614,
      "above_pin_transitions_per_h": 9.857312361191397,
      "genset_starts": 6,
      "genset_starts_per_h": 3.285770787063799,
      "genset_on_frac": 0.48735890961043626,
      "soc_min": 0.24589061524785094,
      "soc_max": 0.8040411623464051,
      "soc_end": 0.5023756696473982
     },
     "5": {
      "fuel_energy_kWh_per_km": 1.4254104069454945,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 690.7999999993717,
      "above_pin_demand_kWh": 4.650464541729526,
      "above_pin_engine_s": 100.5999999999085,
      "above_pin_transitions_per_h": 8.767256731457099,
      "genset_starts": 6,
      "genset_starts_per_h": 3.287721274296412,
      "genset_on_frac": 0.4885614697327327,
      "soc_min": 0.24717424626301795,
      "soc_max": 0.7978057946538629,
      "soc_end": 0.5053894961362857
     },
     "6": {
      "fuel_energy_kWh_per_km": 1.4182710279598196,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 715.8999999993489,
      "above_pin_demand_kWh": 4.441756529444092,
      "above_pin_engine_s": 80.39999999992688,
      "above_pin_transitions_per_h": 6.554690700532568,
      "genset_starts": 6,
      "genset_starts_per_h": 3.277345350266284,
      "genset_on_frac": 0.48981140091296277,
      "soc_min": 0.2499675876076418,
      "soc_max": 0.8012490606507927,
      "soc_end": 0.5605178219174858
     },
     "7": {
      "fuel_energy_kWh_per_km": 1.4212641649975226,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 717.2999999993476,
      "above_pin_demand_kWh": 4.546193694959833,
      "above_pin_engine_s": 87.39999999992051,
      "above_pin_transitions_per_h": 7.646791078743742,
      "genset_starts": 6,
      "genset_starts_per_h": 3.277196176604461,
      "genset_on_frac": 0.48804430283675837,
      "soc_min": 0.24927590064322938,
      "soc_max": 0.8085924684419679,
      "soc_end": 0.5324977760380983
     },
     "8": {
      "fuel_energy_kWh_per_km": 1.419373731624,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 692.3999999993703,
      "above_pin_demand_kWh": 4.303881117458673,
      "above_pin_engine_s": 83.39999999992415,
      "above_pin_transitions_per_h": 8.753400300898136,
      "genset_starts": 6,
      "genset_starts_per_h": 3.2825251128368005,
      "genset_on_frac": 0.48839718553820904,
      "soc_min": 0.2499249995108278,
      "soc_max": 0.8025986257289398,
      "soc_end": 0.5237711139390816
     },
     "9": {
      "fuel_energy_kWh_per_km": 1.4247647870556053,
      "unserved_bus_kWh": 0.0,
      "above_pin_demand_s": 741.6999999993254,
      "above_pin_demand_kWh": 4.578751915470788,
      "above_pin_engine_s": 91.99999999991633,
      "above_pin_transitions_per_h": 14.246141669964384,
      "genset_starts": 6,
      "genset_starts_per_h": 3.2875711546071655,
      "genset_on_frac": 0.48863048308987245,
      "soc_min": 0.24833298394500683,
      "soc_max": 0.8028252638668655,
      "soc_end": 0.5068046340153749
     }
    },
    "per_seed_full": "results_ws4.json -> series_duty_v2 -> cases -> alt2000m_45C -> per_seed (all 37 fields, same run)",
    "companion_bp_ensemble": {
     "unserved_bus_kWh_min": 0.0,
     "unserved_bus_kWh_max": 0.0,
     "unserved_bus_kWh_median": 0.0,
     "unserved_bus_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "unserved_bus_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "r8_envelope_dis_clip_s_min": 0.0,
     "r8_envelope_dis_clip_s_max": 0.0,
     "r8_envelope_dis_clip_s_median": 0.0,
     "r8_envelope_dis_clip_s_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "r8_envelope_dis_clip_s_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "r8_envelope_chg_shed_kWh_min": 0.0,
     "r8_envelope_chg_shed_kWh_max": 0.0,
     "r8_envelope_chg_shed_kWh_median": 0.0,
     "r8_envelope_chg_shed_kWh_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "r8_envelope_chg_shed_kWh_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "fuel_kg_min": 15.964849564672425,
     "fuel_kg_max": 16.10929654569777,
     "fuel_kg_median": 16.06474259940504,
     "fuel_kg_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "fuel_kg_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "fuel_energy_kWh_per_km_min": 1.438361916309073,
     "fuel_energy_kWh_per_km_max": 1.4513953475986154,
     "fuel_energy_kWh_per_km_median": 1.4473418448661017,
     "fuel_energy_kWh_per_km_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "fuel_energy_kWh_per_km_max_governing_case": "seed 3 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "genset_starts_min": 2,
     "genset_starts_max": 2,
     "genset_starts_median": 2.0,
     "genset_starts_min_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]",
     "genset_starts_max_governing_case": "seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/bp]"
    }
   }
  }
 },
 "spin_drag_operational_note_r22d": {
  "ruling": "R22d (BASELINE_v3)",
  "statement": "the traction PM machine is permanently geared, so its spin drag at zero torque persists whenever the vehicle coasts WITHOUT regen. In driving and regenerating operation the drag is inside WS2's measured maps and must not be added again.",
  "ws2_point_drag_85kmh_W_shaft": 1109.0,
  "ws2_point_draw_85kmh_W_bus": 371.0,
  "ws5_guidance": "prefer light regen over true coast: the drag is paid either way, and only the regen path recovers anything from it.",
  "measured_on_series_duty_v2": {
   "ruling": "R22d",
   "ws2_point_drag_85kmh_W": {
    "shaft": 1109.0,
    "bus": 371.0
   },
   "scaling": "[WS4-DECLARED] linear in road speed from WS2's 85 km/h point",
   "coast_no_regen_s_max": 26.099999999976262,
   "coast_spin_shaft_kWh_max": 0.00017454623149206134,
   "coast_spin_bus_kWh_max": 5.839193136479234e-05,
   "unbooked_pp_of_cycle_fuel": {
    "nominal": 0.0002776645392806949,
    "cda_5.4": 0.00023546494767478026,
    "alt2000m_45C": 0.000336470735977268
   },
   "unbooked_pp_max": 0.000336470735977268,
   "unbooked_pp_max_governing_case": "alt2000m_45C",
   "charged_to_fuel": false,
   "direction_of_error": "series_duty_v2's fuel numbers EXCLUDE this member, so they are optimistic by the percentage points above. R22d's own remedy - the WS5 supervisor preferring light regen over true coast - removes the exposure by removing the true-coast samples; the member is exported so WS5 can price that choice."
  },
  "double_count_warning": "do NOT apply this member to driving or regenerating samples; the archived gate's lockup spin member (a different quantity, measured over LOCKED time) is in gate_g1.spin_drag_member and applies to no live architecture."
 },
 "v1_start_stop": {
  "pinned_point": {
   "rpm": 1300.501253132832,
   "trq_Nm": 216.69924812030075,
   "p_shaft_kw": 29.5118746401605,
   "bsfc": 228.7200934767799,
   "p_bus_kw": 27.72459831431504,
   "fuel_gps": 1.8749885351034776,
   "eta_gen": 0.9394387395705018
  },
  "starts_per_8h_shift_at_R8_floor_hyst0.8kWh_ensemble": [
   57.412997664749106,
   74.35242821491065
  ]
 },
 "coolant_loads_to_ws6": "see heat_ledger_ws6"
}
```

## 12. Escalations

- **ESC-1 (cites R6)** *(unchanged r2; R18 has since adopted the
  corner-delivery form)* — R6's label vs rating-basis inconsistency
  under class-typical derates; the candidate is specified at 132 kW
  and clears the corner by +0.82 kW (PROVISIONAL, §2.1).
- **ESC-2 (cites G1, R7, R11) — RESTATED under G1-R.** The r2 ESC-2
  reported a condition-dependent PASS. Under the ruled conventions the
  gate **fails the ≥5% criterion at every condition** (§6 table),
  worst at the R7 corner (-5.90%). The r2 sentence "even where (a)
  misses the criterion it still *beats* series by ~3.8%, so the
  altitude case weakens the clutch's payback, never its sign" is
  **withdrawn on the G1-R record**: at nominal the sign is reversed on
  all eight seeds, at every other condition the ensemble-min is
  negative, and the sole exception to the reversal is CdA 5.4, where
  the ensemble is break-even (min -0.09% / max 0.12%,
  4 of 8 seeds marginally positive — seeds 4, 7, 8, 9). BASELINE_v2's R11 note recording the r2
  reading (and the WS5 condition-aware mode-policy remedy premised on
  it) is contradicted by these numbers — flagged to the lead for
  disposition alongside the kill decision; see ESC-6.
- **ESC-3 (cites R8, R5)** *(unchanged r2; R19 has since ratified the
  disposition)* — V1 start counts at the R8 floor; GEN-V1 specified as
  ISG either way.
- **ESC-4 (cites R9 / WS6 ledger)** *(unchanged r2; R20 recorded the
  seeds)* — radiator design case is the R6 corner, not the grade hold.
- **ESC-5 (cites R8, supports the E24/R4 record) — RESTATED under
  G1-R.** Pure series on VOLT-REG with the R8 3.5 kWh floor now needs
  505–631 s/cycle of emergency above-pin operation at
  nominal (1,128–1,400 s at CdA 5.4) and completes the nominal
  cycle with 0.00 kWh unserved (r2: up to 0.12 kWh); at CdA 5.4 it
  still sheds 0.00–0.52 kWh on hard seeds (r2: 0.46–0.77).
  The R12 chain *softens* the fallback's buffer problem but does not
  remove it off-nominal, and the R3 rating exposure
  (42.1–71.5 s nominal) is untouched — if the kill fires, the
  V1-with-125-kW-genset still inherits R4's "spine not sized for
  forced series" record; WS1's 7.32 kWh figure remains the honest
  scale for a buffer that must also cover CdA 5.4.
  **KX disposition (R22a): the ENERGY half is CLOSED.** At the
  delivered 11.08 kWh pack, pure series completes all three
  ordered cases with 0.0000 kWh unserved on every seed (§4-KX).
  The POWER half is not closed and is re-raised as ESC-9; the R3 motor
  rating record is unchanged.
- **ESC-6 (new — cites R11, G1-R; for the lead's kill decision)** —
  G1-R reverses the premise on which R11 recorded the WS5 mode-policy
  remedy ("prefer series at density-derated corners"): under the ruled
  chain, series is the better fuel mode at the ensemble median of
  every tested condition except CdA 5.4 (break-even, 0.02%
  median), by -2.50% at nominal up to -5.66% at the corner. If the
  lead spares the clutch on non-fuel grounds (R1 capability, §6), the
  WS5 mode policy should be re-premised on the G1-R condition table —
  lockup approaches parity only where the welded load fraction is
  high (CdA 5.4), which is a *load*-aware, not altitude-aware, policy.
  If the kill executes, ESC-5's restated fallback record applies.
  Either way R11's "~3.8% even at the corner" figure should be
  corrected on the baseline record to -5.90% (sign reversed).
  **Disposed:** BASELINE_v3 executed the kill and recorded the ESC-6
  contradiction (R11's premise void, "ESC-6 accepted"). Retained as
  history.
- **ESC-7 (new — cites R32, D13/R36; for the lead) — THE VEHICLE ZERO
  METRIC IS STILL PER KM.** The KX directive orders fuel energy **per
  km** and §4-KX exports it. R32 says the payload-denominated metric
  "shall be" applied to Vehicle Zero before any Vehicle Zero result is
  described as an efficiency advantage, and R36/D13 restate that per-km
  numbers flatter. WS4 therefore exports a payload companion alongside
  every per-km figure — fuel energy per payload tonne-km at WS1's
  2.9 t payload at GVW (a WS1 *assumption*: curb 3,700 kg on a 6,600 kg
  GVW). It is a companion, not a ruler: WS4 has no ratified Vehicle
  Zero payload basis and does not invent one, and no candidate
  comparison in this report is denominated on it. The lead should
  either ratify a Vehicle Zero payload basis or hold R32 open; WS4 will
  not describe any Vehicle Zero result as an efficiency advantage on
  the per-km number.
- **ESC-8 (new — cites R16, R15, R2; for WS3/WS5/WS6) — THE R16 CURVE'S
  HOT END CROSSES THE PACK-LOOP SIZING LINE.** R16's curve is consumed
  as ordered and is not binding at any ordered case (§4-KX.4). But the
  same curve gives 62.2 kW of charge acceptance at 55 °C cells, and
  WS3's pack-loop sizing line is precisely "hold cells ≤ 55 °C at
  +45 °C ambient" — so at the loop's *design ceiling* the pack accepts
  less than this run's peak regen (69.1 kW bus), and a corner
  descent would push regen into the R15 blend order's resistor and
  friction columns. WS4 cannot resolve this: the cell-temperature
  trajectory is WS3/WS6's and the blend order is WS5's. Requested
  disposition: either a ruled maximum cell temperature for dispatch at
  full regen, or an explicit acceptance that hot-corner descents run on
  the resistor.
- **ESC-9 (new — cites R8 as restated by R12/ES-4, R4/E24; for
  WS5/WS3) — THE DELIVERED PACK HAS THE ENERGY, NOT THE POWER.** The
  ordered R22a run completes every case with 0.0000 kWh unserved
  **because the pack's bus-side power envelope is not enforced**: pack
  discharge peaks at 192.5 kW against R8's 125 kW and charge at
  147.6 kW against R8's 110 kW. Enforced as a wall, the run sheds
  up to **0.613 kWh** at alt2000m_45C (§4-KX.3). Two aggravations
  on the same record: the bracket uses the *more permissive* 125 kW of
  the two discharge figures on the record (WS3's own compliance gates
  are at 120 kW), and the run spends 825.0–975.0 s/cycle at CdA 5.4
  below the SOC 0.40-of-nameplate band over which WS3 declares
  the discharge peak at all. WS4 reports all of it
  and tunes none of it. Requested disposition: rule whether R8's bus-side
  peaks are a hard envelope (in which case WS5's dispatch must keep the
  pack off the peak, or WS3 must restate the interface rating), or
  whether short excursions of this duration are accepted — and note
  that the archived gate's mode (a) never posed this question, because
  the engine carried the peaks mechanically. This is R4/E24's "spine
  not sized for forced series" record extended from the R3 motor rating
  to the pack.

## 13. Artefacts in this folder

- `REPORT_WS4.md` (this file, generated by `make_report_ws4.py`),
  `results_ws4.json` (every number, machine-readable; `interface_ws4`
  is the block downstream parses)
- `run_ws4.py` (single entry point), `ws4_models.py`, `ws4_sim.py`,
  `ws4_chain.py` (WS2 map chain + spin member, hot-swappable; KX adds
  the F2 boundary counters), `make_report_ws4.py`, `verify_ws4.py`
  (KX adds the R23 errata pins, including occurrence counts and a
  structural resolution check on every interface `*_file`),
  `requirements.txt`, `run_output.txt`
- `data/bsfc_map_4HK1_ref.csv`, `data/bsfc_map_V2_candidate.csv`,
  `data/bsfc_map_V1_candidate.csv` — Willans BSFC maps (labeled
  constructed)
- `data/gen_eff_map_V2.csv`, `data/gen_eff_map_V1.csv` — generator
  maps (headers carry the R10/1200 V SiC restatement)
- `data/trace_series_duty_v2_nominal_seed23_10Hz.csv` — **R34 10 Hz trace** (66,143 rows), one per run:
  the R22a nominal reference-seed run of mode (b), every bus-side and
  engine-side channel plus SOC
- `data/series_duty_v2_soc_trajectories.csv` — R22a SOC trajectories, all 8 seeds × 3 cases, 5 s
  decimation
- `figs/fig01_bsfc_v2.png`, `figs/fig02_g1_fuel.png` (archived-gate
  fuel by seed), `figs/fig03_v1_starts.png`,
  `figs/fig04_series_duty_soc.png` (R22a SOC trajectories)
- `KX_DIRECTIVE.md` — the lead directive this round executes (input,
  not a WS4 product); `G1R_DIRECTIVE.md` — the previous round's;
  `FINDINGS_WS4_r1.md`, `FINDINGS_WS4_r2.md`, `FINDINGS_WS4_r3.md` —
  adjudication findings (inputs to rounds 2, 3 and this one)
- Read-only imports: `../WS1_loads_duty_cycles` (cycles, physics),
  `../WS2_traction_motor` (`results.json`, `data/cycle_loss_summary.csv`,
  `data/effmap_motor_inverter_*.csv` — the R12 chain of record),
  `../WS3_battery` (`results.json` for the delivered pack,
  `regen_acceptance.csv` for the R16 curve). All SHA-256 pinned in
  `results_ws4.json → kx_input_provenance`
- `.venv/` — local Python environment (numpy, matplotlib), reproducible
  from `requirements.txt`
