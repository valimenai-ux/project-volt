# REPORT WS4 — GENSET + GATE G1 (G1-R RECOMPUTE)

Project Volt · workstream 4 · against BASELINE_v2.md (ratified 2026-08-29)
Author: WS4 (engine & generator). Status: **for adjudication — G1-R
recompute** per the lead directive `G1R_DIRECTIVE.md` (rulings
R10/R11/R12/R18). G1-R changelog in §0-R; the round-2 changelog (§0) is
retained as history. Non-gate sections carry the ratified r2 record and
were not recomputed (bounded rework).

Everything below is produced by runnable code in this folder.
`./.venv/bin/python run_ws4.py` regenerates every number, map, table and
figure in ~60 s (`pip install -r requirements.txt` into any Python ≥3.12
venv first); `results_ws4.json` is the machine-readable form;
`make_report_ws4.py` generates this report with the Interfaces block and
every G1-R headline injected from that JSON; and `verify_ws4.py` asserts
that every headline number here matches `results_ws4.json` verbatim —
no *current* number is transcribed by hand. (Historical values quoted in
the changelogs — the r2 record and the unreproducible r3-interim run —
are quotations of the prior record; the r3-interim margins are carried
as a literal historical block in `results_ws4.json` and rendered from
it.) All stochastic inputs are WS1's seeded cycle builders; extrema are
8-seed ensemble envelopes (R9). WS1's and WS2's folders are imported
read-only, and the consumed WS2 inputs are recorded by SHA-256 in
`results_ws4.json → ws2_chain_of_record → input_sha256`.

> **Headline: GATE G1 FAILS under the ruled conventions. Recomputed per
> the G1-R directive (R12 chain convention + WS2's measured spin-drag
> member), the locked path with charge-bias load-point shifting now
> TRAILS pure series at the pinned BSFC point: margin -2.58% (ensemble
> minimum) / -2.50% (median) / -2.37% (max) at the nominal condition —
> the sign of the comparison is reversed, and the ≥5% kill criterion is
> missed by 7.58 points. The ensemble-minimum margin is negative at
> every tested condition; CdA 5.4 is break-even (min -0.09% / median
> 0.02% / max 0.12%, two seeds marginally positive), every
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
> clause is armed at ≥5% on these numbers (BASELINE_v2). WS4 reports
> the number; the lead executes or spares.**

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
  exposure — corrected in §4.1 (the convention is mode-neutral and
  negligible, not one-sidedly conservative); (iii) categorical
  "sign reversed everywhere" language overstated the CdA 5.4 ensemble,
  which is break-even with two marginally positive seeds — corrected
  in the headline, §6, ESC-2 and ESC-6. Additionally the sign's
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
| **G1 traction chain (R12)** | WS2 measured inverter+motor map (`data/effmap_motor_inverter_662V.csv`, 662 V, WS2 round 4 — the R10-window chain of record) × flat 0.97 reduction, both directions, both modes; **no scalar PE member, no `part_load_factor`**; demands beyond the map's feasible envelope reuse the boundary loss (mode-neutral and negligible, ~seconds per cycle on shared launch samples; §4.1); locked torque-fill at marginal map loss when the spin member is active (§4.1) | R12 + G1-R directive 1a; the loader keys on WS2's exported nominal bus voltage, so any future WS2 re-export hot-swaps on re-run |
| **PM spin drag (G1-R)** | 1.153 kW shaft + 0.390 kW bus charged to mode (a) while locked (WS2 export 1.4851 + 0.5017 kWh per VOLT-REG, round-4 vintage) | directive 1b; WS2 measured, lockup-only tax |
| Part-load derates (non-G1 sections) | WS1's ratified `part_load_factor` retained for the ratified r2 capability/V1 sections (V1 start-stop, grade holds, top speeds — outside G1-R scope); WS4 loss-model maps for both generators; load-dependent direct-path model (2.8% proportional + 0.9·(rpm/1800) kW churning) | R9; bounded rework — those numbers are ratified |
| Generator parasitic | crank-mounted PM generator spins whenever the engine spins: 1.2 kW iron/windage at 1,800 rpm charged to the engine in lockup even at zero output | topology consequence, part of the honest locked-path cost |
| Battery | 0.97/0.97 per direction; usable 3.5 kWh (V2) / 1.5 kWh (V1) at the bus — the R8 floors; banking limited to 50 kW continuous charge (R2/R8) | WS1 convention + R8 |
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
Two boundary conventions, stated precisely (corrected in this revision
— the earlier draft conflated them): demands beyond the map's
*feasible envelope* reuse the nearest boundary loss — measured
exposure is a few seconds per cycle, on unlocked launch samples both
modes drive identically through this same chain, so the convention is
mode-neutral and negligible (~0.001 kWh). Separately, the R3
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
other two exported maps gives -2.86% (432 V map) and -2.35% (749 V map) ensemble-min — across the full
432–749 V window (and the superseded r3 maps, §0-R) the spread is
under 0.6 pp against a 7.58-point shortfall; the verdict does not
depend on which map vintage the chain uses.

### 4.3 Why the sign flipped

The r2 verdict rested on WS1's scalar electric chain: bus→wheel 0.8656
× a part-load derate — an effective ~0.84 where the traction energy
flows. R12 replaces it with what WS2 measured: no PE stage exists on
the traction side, and the inverter+motor map runs 0.93–0.96 where the
energy actually is, giving an energy-weighted bus→wheel chain of
**0.9005** (map × 0.97 reduction) on the same trace — the electric
path is ~8 points better than the convention G1 was first judged on.
That moves ideal series fuel-to-wheel from **247 → 237.6
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

### 4.4 Recommendation

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
| CdA 5.4 (E13) | **-0.09%** | 0.02% | **break-even** (max 0.12%; two of eight seeds marginally positive) — more road load helps the locked path to parity, nowhere near the criterion |
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

## 10. First-principles sanity checks

1. **WS1 regression**: recomputing the 6%/60 km/h floor through WS1's
   own physics gives 107.81 kW — matches WS1's 107.8077950219109 to
   <0.01 kW (asserted in `run_ws4.py`).
2. **Map anchors** *(unchanged)*: island 203.6–205.2 g/kWh ⇒ η_b ≈
   0.41; rated-continuous 215.4 g/kWh; 25%/1,800 rpm ≈ 260 (published
   240–270); motoring drag at 1,706 rpm = 10.7 kW vs WS1's "~10 kW".
   Fast scalar BSFC path asserted equal to the map to <0.05 g/kWh.
3. **Chain arithmetic, restated under R12**: pinned 203.6 / (η_gen
   0.952 × chain 0.9005) = **237.6 g/kWh** ideal series
   fuel-to-wheel (the r2 convention gave 247 g/kWh — the ruled
   chain is worth ~10 g/kWh at the wheel). The simulation's (b)
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
   almost exactly the series wheel rate. Banking remains fuel-neutral;
   the G1-R margin cannot be tuned upward much, which is why §4.3's
   reversal deserves belief.
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
  "_revision": "G1-R recompute (G1R_DIRECTIVE.md; rulings R10/R11/R12/R18). Supersedes the r2 gate numbers, which are retained under results_ws4.json -> gate_g1_prior_convention as the regression anchor.",
  "condition": "nominal: sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, 2 kW aux, GVW, VOLT-REG",
  "convention": "G1-R (R12): traction = WS2 measured map [data/effmap_motor_inverter_662V.csv, 662 V] x 0.97 reduction, no scalar PE member, no part_load_factor; PM spin drag charged to (a) locked samples at 1.1532 kW shaft + 0.3896 kW bus (WS2 export)",
  "traction_chain_of_record": {
   "map_file": "data/effmap_motor_inverter_662V.csv",
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
  "margin_pct_ensemble_min": -2.5816447179555606,
  "margin_pct_ensemble_min_governing_case": "seed 4 of 8-seed VOLT-REG ensemble [nominal]",
  "margin_pct_ensemble_median": -2.5036598384800866,
  "margin_pct_ensemble_max": -2.3727109656800724,
  "kill_criterion_pct": 5.0,
  "passes": false,
  "one_factor_sensitivity": {
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
  "genset_conditioning_bracket": {
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
  "condition_dependence": {
   "_note": "the pass is condition-dependent inside the R7 envelope - see ESC-2; full ensembles in gate_g1/<case>/ensemble",
   "margin_pct_ensemble_min_at_2000m_45C": -5.897136845667756,
   "passes_at_2000m_45C": false,
   "margin_pct_ensemble_min_hot_45C_sea_level": -3.492671913034174,
   "passes_hot_45C_sea_level": false,
   "margin_pct_ensemble_min_CdA_5.4": -0.09073577982911674,
   "passes_CdA_5.4": false,
   "margin_pct_ensemble_min_aux_4kW": -2.2527522850057573,
   "passes_aux_4kW": false,
   "see": "ESC-2"
  }
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
  the ensemble is break-even (min -0.09% / max 0.12%, two
  seeds marginally positive). BASELINE_v2's R11 note recording the r2
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

## 13. Artefacts in this folder

- `REPORT_WS4.md` (this file, generated by `make_report_ws4.py`),
  `results_ws4.json` (every number, machine-readable; `interface_ws4`
  is the block downstream parses)
- `run_ws4.py` (single entry point), `ws4_models.py`, `ws4_sim.py`,
  `ws4_chain.py` (G1-R: WS2 map chain + spin member, hot-swappable),
  `make_report_ws4.py`, `verify_ws4.py`, `requirements.txt`,
  `run_output.txt`
- `data/bsfc_map_4HK1_ref.csv`, `data/bsfc_map_V2_candidate.csv`,
  `data/bsfc_map_V1_candidate.csv` — Willans BSFC maps (labeled
  constructed)
- `data/gen_eff_map_V2.csv`, `data/gen_eff_map_V1.csv` — generator
  maps (headers carry the R10/1200 V SiC restatement)
- `figs/fig01_bsfc_v2.png`, `figs/fig02_g1_fuel.png` (G1-R fuel by
  seed), `figs/fig03_v1_starts.png`
- `G1R_DIRECTIVE.md` — the lead directive this round executes (input,
  not a WS4 product); `FINDINGS_WS4_r1.md`, `FINDINGS_WS4_r2.md` —
  adjudication findings (inputs to rounds 2 and this one)
- Read-only imports: `../WS1_loads_duty_cycles` (cycles, physics),
  `../WS2_traction_motor` (`results.json`, `data/cycle_loss_summary.csv`,
  `data/effmap_motor_inverter_*.csv` — the R12 chain of record)
- `.venv/` — local Python environment (numpy, matplotlib), reproducible
  from `requirements.txt`
