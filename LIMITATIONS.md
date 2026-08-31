# LIMITATIONS

Read this before you believe anything in [FINDINGS.md](FINDINGS.md) or
[METHOD.md](METHOD.md). It is written to be unsparing, because a program whose
whole argument is that structure makes output falsifiable has to be the first
thing falsified.

Every item below is on disk in this repository, cited to the file that carries
it. Nothing here is a new finding; it is the record's own list of what it does
not know, collected in one place.

---

## 1. No hardware. Nothing was measured.

Not one physical measurement exists anywhere in this program. No coastdown, no
dynamometer run, no thermal soak, no prototype, no component sample. Every
number is the output of a simulation whose parameters were sourced from spec
sheets, published maps, and declared assumptions with their direction of error
stated.

The consequence is the first-order limitation and it is not softened anywhere
in this publication: the method
**catches internal inconsistency, never wrong physics**.
**Consistency is not validity.** A model can be byte-reproducible, three-way
verified, adversarially adjudicated, and modelling the wrong truck.

## 2. The Vehicle Zero ruler is uncalibrated (ESC-1)

Every Vehicle Zero verdict is a comparison against a *modelled* stock Isuzu
NPR-HD. That model was built from the manufacturer's own spec sheet and a
sourced transmission ratio set, and it was validated — not fitted — against a
public in-use fuel-economy aggregate. It failed that validation by a wide
margin:

| | value |
|---|---|
| the model, on the suburban duty, 8-seed median | **19.18 L/100 km** [ruler_model_lp100] |
| sourced in-use anchor, all model years | **28.07 L/100 km** [anchor_all_years] over **179,702 miles** [anchor_miles] and **1,044 fuel-ups** [anchor_fuelups] |
| sourced anchor, era-correct subset (the governing member) | **32.01 L/100 km** [anchor_era] |
| residual against the all-years anchor | **-31.69%** [anchor_resid_all] |
| residual against the era-correct anchor | **-40.10%** [anchor_resid_era] |

The workstream states plainly that the calibration order it was given was not
carried out: `calibrate_order_satisfied: false` [calibrate_satisfied]. It did
not tune the model to close the residual, on the argument that an in-use
aggregate over an unknown duty, load, body and driver mix cannot resolve a
cycle-specific level. That is a defensible modelling position and it is not
compliance with the order, and the workstream says so.

**Why it matters asymmetrically.** The residual is in the ruler's favour on
every setting, which makes candidate margins *lower bounds*. A lower bound is
the safe direction for an ADVANCE and the wrong guarantee for a KILL — doctrine
D21: "A LOWER-BOUND RULER IS THE WRONG GUARANTEE FOR A KILL" [d21_ruler], since
kills "require the ruler at its unfavourable end; advances require it" [d21_rule]
at its favourable end. V2 Trucker's FROZEN-KILL flips to a draw on a
**+6.93%** [v2_flip_pct] ruler-fuel error, and the anchor says the real fleet is
thirstier than the model by far more than that.

Source: `WS11_vehicle_zero_ruler/results_ws11.json` → `interface_ws11.ruler.anchor`;
`WS11_vehicle_zero_ruler/REPORT_WS11.md` §1.2, ESC-1.

## 3. Every Vehicle Zero verdict is model-relative, by ruling

Not a caveat added here. The freeze baseline itself carries
"Ruler uncalibrated" [v7_uncalibrated] (ESC-1) beside the verdicts, and the
program's ruling R44 says why: a crowdsourced in-use aggregate cannot
"calibrate a cycle" [r44_cannot], so
"Verdicts are MODEL-RELATIVE until WS7 measures a" [r44_modelrelative] stock
NPR-HD on the program cycles, with no external
"efficiency claim before it" [r44_noclaim]. That measurement is a mandatory
task in a workstream that was never cut. Until it exists, "V1 Postal is 20%
better than a stock NPR-HD" is not a statement this record supports; "V1 Postal
is 20% better than this model of a stock NPR-HD, on this duty, on this metric"
is.

## 4. The two figures the baseline does not carry

`BASELINE_v7_FREEZE.md` reports V1's ADVANCE at **+20.11%** [v1_nominal_min]
nominal and **+19.12%** [v1_worst_corner] at its worst corner, conditional on
four rulings — "conditional on R43(a)-(d) (cab heat," [v7_v1_conditions]
"warm-up model, corner convention, CdA bracket), which were ordered" [v7_v1_notrun]
and not run. The workstream's own report prices two of them, and those figures
are not in the baseline:

1. **With both pending rulings applied together, V1's governing corner falls to
   +3.66%.** `WS11_vehicle_zero_ruler/REPORT_WS11.md` §0, line 39:
   "which take its governing corner to +3.66%" [ws11_366]. Exported as
   `results_ws11.json` → `interface_ws11.cold_corner_pending_items.V1_on_VOLT-SUB.with_cab_heat_and_CdA_5p4_pct`
   = **+3.66%** [v1_cold_both]. Still a pass against the 0% corner bar, by about
   three points instead of nineteen.
2. **Under the harshest defensible cab-heat reading, that same corner goes
   negative.** Same report, §0 line 35 —
   "the harshest one takes V1's governing corner negative" [ws11_negative] — and
   §5 line 284: "under the harshest cab-heat reading V1's governing corner goes NEGATIVE" [ws11_negative_body].
   The figure is **-5.42%** [v1_cold_no_credit], against the fixed-point
   treatment's **+4.72%** [v1_cold_cabheat_fp] and round 1's
   **+2.64%** [v1_cold_cabheat_r1]. A fail against the >=0% corner bar.

Neither reading is ordered and neither is the gated number. The span from -5.42%
to +4.72% is the width of a modelling member that was never ruled on, sitting on
the corner the headline advance is gated on. **The status does not move:** V1
remains "FROZEN-PROVISIONAL ADVANCE, +20.11% nominal" [v7_v1_state]. That is
what its provisionality is carrying.

## 5. Declared brackets: numbers that are ranges, not points

Several load-bearing quantities are declared rather than measured, and are
carried as brackets rather than as values. The honest reading of a bracketed
result is the whole bracket:

- **Aerodynamic drag.** BASELINE_v1 states it outright:
  "CdA 4.2 m^2 and rho 1.20 kg/m^3 are PROVISIONAL fitted values pending" [cda_provisional]
  a coastdown that was never run. It is bracketed at 4.2 and 5.4 m² throughout,
  and it is a change to the *road* both vehicles drive rather than a modelling
  choice, so it lowers both margins.
- **The ruler's driveline.** Eight declared levers (gear mesh, AT pump, final
  drive, lock-up slip, accessories, idle-in-Drive, shift schedule, inertia), all
  set at their ruler-favourable ends in the headline. At their pessimistic ends
  V2 moves from **-7.93%** [v2_nominal_min] to **+0.13%** [v2_pessimistic_min] /
  **+0.59%** [v2_pessimistic_median], and V1 from **+20.11%** [v1_nominal_min] to
  **+37.78%** [v1_pessimistic_min].
- **Cab heat at the cold corner** — §4 above.
- **Aftertreatment mass** on V2:
  "WS4's `aftertreatment_extra: 60 kg` is EXCLUDED from the headline" [ws11_aftertreatment]
  and carried as a bracket instead.
- **The opposed-piston engine** underneath the best semi candidate is an engine
  bet on a cited external basis, exported across three peak-BTE assumptions. The
  lead recorded it plainly: "S6 is an engine bet with ~2.3 BTE points of" [s6_bte_headroom]
  headroom, not a drivetrain result.

## 6. Statuses at freeze are provisional, and several are conditional on rounds that were ordered and never run

R52: "Every verdict and number keeps the status it holds at freeze" [v7_r52],
"Nothing is promoted; nothing is quietly" [v7_r52b] demoted. What that means in
practice:

- V1 Postal: FROZEN-PROVISIONAL ADVANCE, conditional on R43(a)-(d), not run.
- Vehicle One wave one: verdicts final, "WS8 S1-S4 KILLED (final), WHR DROPPED (final); numbers" [v7_ws8_state]
  FROZEN-PROVISIONAL at r3, with "r3 adjudication not clean, r4 ordered and" [v7_ws8_r4] not run.
- Vehicle One wave two: "WS9: S6 / S4' / S5-13L / S7 FROZEN-PROVISIONAL ADVANCE on" [v7_ws9_state]
  the design duty, with "findings PRE-B1..B3; S5-13L expected to convert to KILL-ON-TIME under" [v7_ws9_open]
  R46 — i.e. one of the four advances is expected to become a kill on a gate
  that was clarified and never applied. Its designated adjudication was
  cancelled: "The Fable adjudication of WS9 is CANCELLED" [v7_r53].
- KX (the Vehicle Zero genset round): NOT CONVERGED after three rounds.

## 7. Single-machine simulation

Everything ran on one laptop. There is no independent implementation of any
model, no second solver, no cross-language check. The determinism evidence is
byte-stable regeneration of the same code on the same machine — which proves
reproducibility, not correctness. The nearest thing to independent computation
is the adjudicators' re-derivations, which were written from the reports rather
than from the code and which did catch real defects; that is a genuine second
implementation of specific quantities, not of the pipelines.

## 8. The frozen open findings — defects that were found, ordered fixed, and never fixed

These are known-wrong and on the record. The freeze stopped the rounds that
would have closed them.

| finding | what is wrong | consumer |
|---|---|---|
| **WS8 r3 B1** | "B1: throttle-back branch on the pack power ceiling unmeasured," [r45_b1] — "+1.64 pp of S3's move without a one-factor row" [r45_b1_size] | the r3 numbers of record |
| **WS8 r3 B2** | "commitment exports the instantaneous max under a "60-second" label," [r45_b2] 1.53x high | an R14 export |
| **WS9 PRE-B1** | "module cannot fire on 10 of 15 fields — hard-coded verdict literals" [r46_preb1] and tautologies, proven by mutation | the concordance guarantee |
| **WS9 PRE-B2** | "PRE-B2 (PEM "exactly 0.0" is an" [r46_preb2] unmeasured fallback — though the finding itself is "is a tautology of a missing key, not a measurement" [preb2_actual] about a *concordance denominator*, not the predictive-energy bracket (see §10) | a stated measurement |
| **WS9 PRE-B3** | "PRE-B3 (S5-13L 6% climb ledger row on the" [r46_preb3] wrong branch of a two-band envelope — "exported 20.1 kW total rejection against a correct engine-coupled 507.3 kW" [fm_wrong_branch] | the WS6 heat ledger, which never ran |
| **WS9 PRE-M2** | "modelled pack temperatures reach 153 °C, including at a corner that gates" [prem2_packtemp] — no upper bound, no hot-side derate, no cooling power charged | a gating corner |
| **KX R3-B1** | "the R20/ESC-12 analysis is enumerated over a case set that EXCLUDES R20's own declared design case" [fm_governing_case]; v7 leaves it as "103.5 vs 95.0 kW)" [kx_radiator_v7], and v6 to the measured figure: "CORNER (103.522 kW two-minute maximum), not its ambient" [kx_radiator_v6] | radiator sizing; WS6 never ran |
| **KX sweep** | "Two of the sixteen areas the construction sweep certifies as" [fm_falseclean] examined and clean are not clean | the sweep's own certifications |

## 9. The unverified rework of 2026-08-31

The headline Vehicle Zero number stands on a rework round that nothing checked.
At 07:40 the principal chose to gate two workstreams mechanically and
**"SKIP their adjudication rounds"** [nx_decision]. The foreman recorded the
consequence before the outcome was known:

> "WS11's round-2 rework closes 3 blocking + 8 material + 13 minor findings and NOTHING WILL HAVE CHECKED THAT WORK" [nx_consequence]

and in the commit for that work:

> "a gate PASS on r2 is evidence of reproducibility only and is NOT evidence the findings are closed" [nx_gate_meaning]

Round 1 had also passed a byte-stable gate, and was then found NOT CLEAN with
its central robustness claim falsified. A number moved inside the unchecked
round: "ONE NUMBER MOVED: V1's cold+cab-heat bracket" [nx_number_moved]. And
WS5 has no adjudication round at all —
"WS5 is the only workstream of the night with ZERO adjudication rounds" [nx_ws5];
v7 points at a packet for its status —
"WS5: status per its packet at freeze" [v7_ws5_state] — that does not exist on
disk.

The same event is the strongest evidence *for* the method, and it is written up
as the program's control condition in [METHOD.md](METHOD.md) §4. Both readings
are true and neither cancels the other.

## 10. Where the record disagrees with itself

Found while grounding this publication's numbers. Recorded, not resolved — this
publication rules on nothing and edits no baseline or report.

1. **Claim 5's "(S3 excepted)" clause carries round-2 numbers under a round-3
   label.** At r3, S3's paired per-km margin is **+4.88%** [s3_perkm_min] with
   `wins_on_every_seed = true` [s3_wins_every_seed], and S4's per-km min is
   **+3.36%** [s4_perkm_min], below the "6-10%" band the claim quotes.
2. **Claim 8's "five-for-five first-pass defect detection" [v7_claim8_rate]
   predates two of the seven first passes now on disk.** The enumerated table is
   [METHOD.md](METHOD.md) §3.
3. **Claim 7 cites PRE-B2 for a measurement PRE-B2 is not about.** The lead's
   summary reads "PRE-B2 (PEM "exactly 0.0" is an" [r46_preb2] unmeasured
   fallback; the finding itself is about a concordance denominator and is
   headed "is a tautology of a missing key, not a measurement" [preb2_actual].
   The predictive-energy bracket is a two-sided measurement of a lever fitted to
   the ruler.
4. **v7 points WS5 at a `PM_PACKET_WS5.md` that does not exist.** §9 above.

These are exactly the class of defect the method is claimed to catch, found in
the method's own summary of itself, which is the only kind of self-validation
available here and is worth precisely that much.

## 11. The closest the record comes to catching wrong physics — and why it still is not validation

One defect in this program was labelled a physics defect by the lead:

> "ESC-WS8-10 is a PHYSICS DEFECT of record: the retard envelope never" [escws810_lead]
> re-solves when the buffer fills, so every simulated descent brakes
> "harder than the resistor can absorb — fix ordered in WS8 r4 and" [escws810_effect]
> inherited by WS9 r2.

The workstream's own escalation states it the same way:
"The retard envelope does not re-solve when the buffer pack fills, so every simulated descent lets a candidate brake harder than its resistor can absorb" [escws810_ws8].

Three things about it, in order of importance:

1. **It is still an internal inconsistency.** The resistor rating is a declared
   parameter of the model, and the model violated it. What was caught is the
   simulation contradicting its own inputs — not the model disagreeing with a
   measurement, because there is no measurement.
2. **It was surfaced by a worker's escalation, not by an adjudicator.** The
   round that found it declined to fix it under an order whose scope was
   declared exhaustive, and escalated it unresolved. That is the escalation path
   working, and it is a different mechanism from adversarial review.
3. **It was never fixed.** The fix was ordered in a round the freeze cancelled.
   Every descent in the affected candidates' results is still optimistic by that
   amount.

So the guard rail stands as stated: the method **catches internal
inconsistency, never wrong physics**, and **Consistency is not validity.** This
case is the boundary being tested, and it lands on the consistency side of it.

---

## What would move any of this

One thing, mostly: hardware. A measured stock NPR-HD on the program cycles
turns every Vehicle Zero verdict from model-relative to measured, and it is
already a mandatory task in an uncut workstream. After that, in order of
leverage: running the four R43 conditions on the headline advance; closing the
eight frozen findings in §8; and an independent implementation of at least the
road-load and chain models by someone who has not read this code.

Until then, the honest summary of this repository is the one in
[README.md](README.md): a program that killed its own favourite ideas on
criteria written before the numbers existed, and mostly explained why the
industry looks the way it does.
