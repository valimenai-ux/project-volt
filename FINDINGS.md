# FINDINGS — the engineering results

The case study for [METHOD.md](METHOD.md). Eight claims, each with the status
`BASELINE_v7_FREEZE.md` gives it, the numbers behind it, the files those numbers
live in, the command that regenerates them, and what would change the claim.

Written so that a drivetrain engineer can check every line. Every number below
resolves to a results file and a path into it, or to a report line; the index is
[`WS13_publication/CITATIONS.md`](WS13_publication/CITATIONS.md) and
`WS13_publication/verify_ws13.py` asserts the resolution.

**The boundary this whole file sits inside.** The method that produced these
results **catches internal inconsistency, never wrong physics**. No hardware was
built. The Vehicle Zero ruler is **-31.69%** [anchor_resid_all] below its own
sourced in-use anchor and **-40.10%** [anchor_resid_era] below that anchor's
era-correct member, and the workstream records `calibrate_order_satisfied: false` [calibrate_satisfied].
**Consistency is not validity.** Every verdict here is model-relative, which is
the baseline's own ruling — "all Vehicle Zero verdicts are model-relative" [v7_model_relative].
That does not make the results empty: the boundary laws below are physics
results, several of them closed-form, and they are stated at the status the
program gave them, not below it.

**Statuses are not moved by this file.** R52 of the freeze:
"Every verdict and number keeps the status it holds at freeze" [v7_r52],
"Nothing is promoted; nothing is quietly" [v7_r52b] demoted. Where v7 renders a
verdict as `FROZEN-<status>`, that is what appears here.

---

## How to read a claim

- **Statement** is quoted verbatim from `BASELINE_v7_FREEZE.md` §"What the
  program found". Nothing is paraphrased.
- **Status** is v7's own parenthetical, verbatim, plus the `FROZEN-<status>`
  label v7 applies to the underlying verdict where it applies one.
- **Numbers** are ensemble statistics over 8 seeds unless stated otherwise, and
  every margin is a *paired per-seed* statistic (formed seed by seed, then
  enveloped) per ruling R36.
- **Metric of record** for both vehicles is fuel (or primary) energy per
  **payload** tonne-km. At fixed gross weight, powertrain mass is payload:
  "Per-km efficiency flatters; per-payload judges" [d13_perkm].

---

## Claim 1 — Electric torque-fill replaces the gearbox entirely at 6.6 t

**Statement (v7, verbatim).** "Electric torque-fill replaces the gearbox entirely at 6.6 t" [v7_claim1]

**Status (v7, verbatim).** "(ratified, model-relative)" [v7_claim1_status]

**What it means.** On a 6,600 kg GVW delivery truck, a single fixed reduction
plus an electric machine covers the whole tractive envelope, and the program
tested the one place a mechanical path might still pay — a lockup clutch onto a
fixed 2.8:1 top ratio — and killed it on a criterion written before the numbers
existed.

**The numbers.** Gate G1 asked whether the locked mechanical path beats pure
series by at least **5%** [g1_criterion] net energy over the regional cycle,
with load-point shifting on a real BSFC map and part-load derates on both sides.

| | ensemble-min | note |
|---|---|---|
| first pass, superseded chain convention | **+6.26%** [g1_prior_min] | passed the gate |
| G1-R, after ruling R12's one-chain correction | **-2.58%** [g1r_min] | median **-2.50%** [g1r_median] |
| missed the criterion by | **7.58 pp** [g1_missed_pp] | sign reversed |
| seeds on which the locked path won | **0 of 8** [g1_seeds_positive] | |

One-factor attribution of the reversal: replacing WS1's scalar efficiency chain
with WS2's measured inverter+motor maps is worth **-7.01 pp** [g1_map_vs_scalar_pp],
and charging the permanent-magnet machine's spin drag to the locked samples is
worth a further **-1.77 pp** [g1_spin_pp]. The only near-break-even condition is
the larger frontal area, at **-0.09%** [g1_cda54_min] with **4 of 8** [g1_cda54_positive_seeds]
seeds positive; the hot-and-high corner is the worst at **-5.90%** [g1_alt_min].

The gate was executed: "GATE G1: EXECUTED. THE CLUTCH IS DELETED." [clutch_deleted]
Both variants became pure series, and the whole downstream program — controls,
packaging, the semi work — was re-scoped on that.

**Evidence.**
`WS4_genset/results_ws4.json` → `interface_ws4.gate_g1` (archived, `status: executed_kill_2026-08-30`);
`WS4_genset/REPORT_WS4.md`; `BASELINE_v3.md` (the ruling);
`WS4_genset/FINDINGS_WS4_r1.md`, `FINDINGS_WS4_r2.md`, `FINDINGS_WS4_r3.md`,
`FINDINGS_KX_r1.md`, `FINDINGS_KX_r2.md`, `FINDINGS_KX_r3.md`.

**Reproduce.**
```
cd WS4_genset && python run_ws4.py && python make_report_ws4.py && python verify_ws4.py
```

**What would change it.** (a) A hardware measurement of the reference truck —
R44 makes this mandatory before any external efficiency claim. (b) A different
total ratio: the 2.8:1's engine-sync rationale died with the clutch, and
BASELINE_v3 records the total ratio as a free parameter for future revisions
that was deliberately not reopened. (c) The workstream that carries these
numbers is NOT CONVERGED — see §10 — so the surrounding heat-ledger and
capability numbers are open even though the gate verdict is not.

---

## Claim 2 — The mass boundary: no single ratio spans cruise and grade at 36.3 t

**Statement (v7, verbatim).** "The transmissionless premise has a MASS boundary between ~7 and" [v7_claim2]
"36 t: no single ratio spans cruise and grade at 36.3 t (ratified," [v7_claim2_body]
"closed-form and simulated)" [v7_claim2_status]

**Status (v7, verbatim).** ratified, closed-form and simulated.

**What it means.** The premise that killed the gearbox at 6.6 t does not survive
scaling. At **36,300 kg** [gcw] gross combination weight, the ratio that lets the
engine cruise at 105 km/h under its rpm ceiling and the ratio that lets it hold
a 6% grade are not the same ratio, and they are not close.

**The numbers.** This is a closed-form result, not a search:

| quantity | value | basis |
|---|---|---|
| highest ratio that keeps the engine under 2,100 rpm at 105 km/h | **3.7699** [ratio_ceiling] | closed form, `ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)` |
| lowest ratio that balances road load on a 6% grade at GCW | **6.88** [ratio_needed] | swept on a 0.01 grid, resolution-tested |
| that ratio's overspeed at 105 km/h | **1,732 rpm** [ratio_rpm_over] | above the 2,100 rpm ceiling |
| feasible single ratios in the swept set | `any_feasible = false` [ratio_any_feasible] | eleven ratios from 2.4 to 5.0 |

The implied span is about 1.83:1, and a ten-fold refinement of both sweep grids
moves the required ratio by 0.009 against a 1,732 rpm gap — the grid decides a
decimal place, not the answer.

The same candidate (S3, the tandem split with no gearbox anywhere) is
independently infeasible on adhesion: the regulatory 12% start needs
**0.587** [mu_single_axle] on a single driven axle, against **0.293** [mu_tandem]
for a 6x4 tandem, so a single-axle launch is out on anything but dry pavement.

**Evidence.**
`WS8_semi_architecture/results_ws8.json` → `interface_ws8.S3_fixed_ratio_feasibility`
and `task5_s3_specific.regulatory_startability_adhesion`;
`WS8_semi_architecture/REPORT_WS8.md` §6.2; `WS9_vehicle_one_wave2/results_ws9.json` → `two_walls`.

**Reproduce.**
```
cd WS8_semi_architecture && python run_ws8.py && python make_report_ws8.py && python verify_ws8.py
```

**What would change it.** The ratio ceiling is a function of the declared rpm
ceiling (2,100), the cruise speed (105 km/h) and the tyre radius,
**0.5 m** [ws8_r_dyn]. Move
any of the three and the bound moves with it, in closed form — an engine family
that cruises at 1,400 rpm at 105 km/h changes the arithmetic, not the argument.
The grade requirement (6% at GCW) is the other half, and it is a duty choice.

---

## Claim 3 — The duty boundary: the same truck wins on stop-go and loses on regional

**Statement (v7, verbatim).** "It has a DUTY boundary: the same truck wins +20% on stop-go and" [v7_claim3]
loses on regional duty.

**Status (v7, verbatim).** "(V1 provisional, V2 kill)" [v7_claim3_status] — and in
v7's statement of the frozen research state, V1 is
"FROZEN-PROVISIONAL ADVANCE, +20.11% nominal" [v7_v1_state] ensemble-min per
payload tonne-km, while "V2 Trucker: FROZEN-KILL, -7.93% headline, a draw at the" [v7_v2_state]
ruler's pessimistic end, never reaching the bar.

**Where the question came from.** The payload-denominated metric decided Vehicle
One before it was ever applied to Vehicle Zero, and the lead flagged that gap
against himself rather than letting it stand — R32:
"Vehicle Zero consistency flag: the payload-denominated metric" [r32_order] has
not been applied to Vehicle Zero, and shall be before any Vehicle Zero result is
"described as an efficiency advantage. Not executed now." [r32_order2] It was
executed a day later, and it reversed one of the two variants.

**What it means.** Two variants on one electric spine, same mass class, same
components, judged against a modelled stock Isuzu NPR-HD on the honest metric.
The suburban-delivery variant wins by twenty points. The regional-delivery
variant loses by eight. The architecture is not good or bad; it is duty-indexed —
"Architecture is duty-indexed. Name the duty before the number" [d15_duty] means
anything.

**The numbers.** Criterion, pre-committed: advance only at **3%** [ws8_bar_nominal]
or better at nominal, ensemble-min, and **0%** [ws8_bar_corner] or better at every
corner.

| | V1 Postal on VOLT-SUB | V2 Trucker on VOLT-REG |
|---|---|---|
| nominal, per payload tonne-km, ensemble-min | **+20.11%** [v1_nominal_min] | **-7.93%** [v2_nominal_min] |
| worst corner | **+19.12%** [v1_worst_corner] (cold -10 C) | **-9.98%** [v2_worst_corner] (6% climb) |
| per kilometre, same paired statistic | **+25.29%** [v1_perkm_min] | **+8.41%** [v2_perkm_min] |
| freight given back, in margin points | **5.11 pp** [v1_mass_cost_pp] | **16.19 pp** [v2_mass_cost_pp] |
| operating curb | **3,888 kg** [curb_v1] | **4,139 kg** [curb_v2] |
| payload at 6,600 kg GVW | **2,712 kg** [payload_v1] | **2,461 kg** [payload_v2] |
| break-even curb (exact, not searched) | headroom **+545 kg** [v1_breakeven_headroom] | **3,944 kg** [v2_breakeven_curb], headroom **-195 kg** [v2_breakeven_headroom] |

The ruler carries **3,700 kg** [curb_ruler] curb and **2,900 kg** [payload_ruler]
payload at the same GVW. **V2 wins on fuel and loses on freight**, which is the
entire content of the claim: it is 195 kg over the curb at which it would exactly
draw.

Where V1's twenty points come from, as independent one-factor re-runs (they do
not sum): regen on a 30-stop cycle **23.59 pp** [v1_regen_pp]; engine-off against
a load-following genset **72.58 pp** [v1_engineoff_pp]; the pinned operating point
**11.15 pp** [v1_oppoint_pp] (an upper bound — it absorbs idle). On the regional
duty the same rows read **4.32 pp** [v2_regen_pp] for regen and **0.25 pp** [v2_engineoff_pp]
for engine-off, because "braking is 5.84% of tractive energy" [ws11_braking_share]
there and the genset rarely stops. The doctrine entry is D20:
"THE TRANSMISSIONLESS SERIES ARCHITECTURE IS A STOP-GO-DUTY" [d20_stopgo]
ARCHITECTURE — it won on postal duty and lost on regional
"duty at the same mass, because regen and engine-off pay for its" [d20_why] mass
only where stops dominate.

**The V2 KILL is not robust, and the workstream says so.** With all eight
ruler-modelling levers at the pessimistic end each one's own declaration names,
V2 goes to **+0.13%** [v2_pessimistic_min] ensemble-min / **+0.59%** [v2_pessimistic_median]
median — a draw, still short of the 3% bar. And the KILL flips on a
**+6.93%** [v2_flip_pct] ruler-fuel error, against a ruler that was never
calibrated and reads **19.18 L/100 km** [ruler_model_lp100] against a sourced
in-use anchor of **28.07 L/100 km** [anchor_all_years] over
**179,702 miles** [anchor_miles] and **1,044 fuel-ups** [anchor_fuelups]
(**32.01 L/100 km** [anchor_era] on the era-correct subset). D21 names the
asymmetry: "A LOWER-BOUND RULER IS THE WRONG GUARANTEE FOR A KILL" [d21_ruler] —
kills "require the ruler at its unfavourable end; advances require it" [d21_rule]
at its favourable end. V1's ADVANCE runs the safe way: at the same pessimistic
end it improves to **+37.78%** [v1_pessimistic_min], and the ruler would have to
be **-17.64%** [v1_flip_pct] leaner than modelled before V1 fell to the 3% bar.

**V1's ADVANCE is conditional, and the conditions were never run.** v7:
"conditional on R43(a)-(d) (cab heat," [v7_v1_conditions]
"warm-up model, corner convention, CdA bracket), which were ordered" [v7_v1_notrun]
and not run. See §9 for the two figures that price those conditions.

**Evidence.**
`WS11_vehicle_zero_ruler/results_ws11.json` → `interface_ws11.verdicts`,
`interface_ws11.verdict_robustness`, `interface_ws11.ruler_fuel_flip_points`,
`interface_ws11.break_even_curb_kg`, `one_factor.rows`;
`WS11_vehicle_zero_ruler/REPORT_WS11.md` §3, §4, §7;
`WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md`;
sources under `WS11_vehicle_zero_ruler/sources/` (the NPR-HD spec sheet and the
anchor page, stored verbatim and SHA-256 pinned).

**Reproduce.**
```
cd WS11_vehicle_zero_ruler && python run_ws11.py && python make_report_ws11.py && python verify_ws11.py
```

**What would change it.** (a) Calibrating the ruler — the order was given and
`calibrate_order_satisfied: false` [calibrate_satisfied] records that it was not
carried out. (b) Running R43(a)-(d). (c) For V2 specifically: nothing about the
architecture, only 195 kg of curb, or a ruler that is more than **+6.93%** [v2_flip_pct]
thirstier than modelled — and the anchor says the real fleet is thirstier than
that by a wide margin, which is why the KILL is the exposed verdict rather than
the safe one.

---

## Claim 4 — The third wall: a 2-speed's low gear cannot reach the crawl speed a steep grade forces

**Statement (v7, verbatim).** "A 2-speed under torque-fill meets a third wall" [v7_claim4]
— the low gear's coupling floor vs crawl speed.

**Status (v7, verbatim).** the low gear's "coupling floor vs crawl speed (provisional)" [v7_claim4_status]

**What it means.** Give the semi two ratios instead of one and the mass wall
(claim 2) is cleared by construction. A third constraint then appears that the
two walls do not name: the low gear's coupling floor — the road speed below
which the engine cannot stay connected at its idle-plus-margin speed — sits
*above* the crawl speed a steep grade forces. Below that speed the engine is
disconnected and the vehicle is on its machine alone.

**The numbers.**

| | 11 L engine | 13 L engine |
|---|---|---|
| low-gear coupling floor | **25.4 km/h** [wall3_floor_11l] | **33.5 km/h** [wall3_floor_13l] |
| steepest grade a *contiguous* two-speed can hold | **6%** [wall3_11l] | **8%** [wall3_13l] |
| ratio span a contiguous engine band allows | **2.058** [span_bound] | same bound |

Against a design duty whose steepest grade is **10.74%** [duty_grade_max] over the
8-seed ensemble. The assignment's 6% wall sits almost exactly on the 11 L
frontier, which is why the candidate clears it by construction and fails one
point above it.

The candidates that carry the wall: S5 as ordered on the 11 L engine scores
**+1.90%** [s5_design] on the design duty and **-5.75%** [s5_control] on the flat
control duty and is a KILL; S5-13L scores **+5.36%** [s513_design] and
**-1.38%** [s513_control] and carries an ADVANCE. Doctrine D16 records the
frontier: "THE THIRD WALL" [d16_thirdwall], and records that
"Vehicle Zero's 35 km/h" [d16_vz_miniature] engine-path idle floor was the same
physics in miniature at a quarter of the mass.

**Evidence.**
`WS9_vehicle_one_wave2/results_ws9.json` → `two_walls.third_constraint_coupling_floor`
(both engines, per-grade rows and the frontier), `duties.GH-REG-165.ensemble.grade_max`;
`WS9_vehicle_one_wave2/REPORT_WS9.md` §3; `BASELINE_v5.md` D16.

**Reproduce.**
```
cd WS9_vehicle_one_wave2 && python run_ws9.py --jobs 6 && python make_report_ws9.py && python verify_ws9.py
```

**What would change it.** The floor is set by the engine's idle speed, its
lugging margin and the low ratio, so a launch device (clutch or converter) on the
engine side dissolves it and buys back mass — which is the trade the whole
premise exists to avoid. The candidate's specification was confirmed *without*
an engine-side launch device (ruling ESC-7 of WS9), so the wall is a consequence
of that ruling as much as of the physics. The claim is labelled provisional and
the workstream carries open blocking findings — §10.

---

## Claim 5 — At fixed gross weight, the objective is efficiency per added kilogram

**Statement (v7, verbatim).** "At fixed gross weight, efficiency per added kilogram is the" [v7_claim5]
objective; every electrified semi candidate won 6-10% per km and gave 6-8% back
in freight (S3 excepted).

**Status (v7, verbatim).** "gave 6-8% back in freight (S3 excepted) (ratified, r3 numbers)" [v7_claim5_status]

**The metric, stated exactly.** `interface_ws8.metric_of_record` reads
"fleet-mission fuel energy per PAYLOAD tonne-km [MJ/(t.km)], fleet mission = 70% LH-520 + 30% REG-165 by distance" [ws8_fleet_mix].

**What it means.** At a legally fixed gross combination weight, every kilogram of
powertrain displaces a kilogram of freight one-for-one. A candidate that is more
efficient per kilometre and heavier can be *less* efficient per payload tonne-km,
and at semi scale all four wave-one candidates were exactly that. This is the
result that decided Vehicle One, and it needs no efficiency assumption to state.

**The numbers (round 3, the numbers v7 freezes).** Per-kilometre margins are the
paired per-seed statistic, ensemble-min at nominal:

| | per km, min | per payload t-km, min | per payload t-km, median | payload | verdict |
|---|---|---|---|---|---|
| S0 ruler | — | — | — | **20,785 kg** [payload_s0] | ruler |
| S1 pure series | **+6.03%** [s1_perkm_min] | **-0.69%** [s1_min] | **+0.73%** [s1_med] | **19,398 kg** [payload_s1] | KILL |
| S2 single ratio + torque-fill | **+8.62%** [s2_perkm_min] | **+0.59%** [s2_min] | **+1.89%** [s2_med] | **19,106 kg** [payload_s2] | KILL |
| S3 tandem split | **+4.88%** [s3_perkm_min] | **-1.09%** [s3_min] | **+1.64%** [s3_med] | **19,559 kg** [payload_s3] | KILL |
| S4 range-extended BEV | **+3.36%** [s4_perkm_min] | **-3.84%** [s4_min] | **-1.06%** [s4_med] | **19,344 kg** [payload_s4] | KILL |

S2's per-km band tops out at **+11.06%** [s2_perkm_max]. The ruler burns
**38.78 L/100 km** [s0_fleet_lp100] on the fleet mission. Not one candidate
reached the **3%** [ws8_bar_nominal] bar at nominal, and the corner bar of
**0%** [ws8_bar_corner] was missed by more. The verdicts are final:
"WS8 S1-S4 KILLED (final), WHR DROPPED (final); numbers" [v7_ws8_state]
FROZEN-PROVISIONAL at r3.

**A consistency note on this claim's own wording, which this publication may not
resolve.** The statement's "(S3 excepted)" clause describes round-2 numbers,
where S3's per-km figure was negative on the ratio-of-medians construction R36
subsequently outlawed. At round 3 — the numbers v7's status line names — S3's
paired per-km margin is **+4.88%** [s3_perkm_min] with `wins_on_every_seed = true` [s3_wins_every_seed],
so it is not an exception to winning per km; and S4's per-km min of
**+3.36%** [s4_perkm_min] sits below the "6-10%" band the statement quotes. The
claim's substance — mass displaces payload one-for-one, and per-km wins are
handed back as freight — holds on every row of the table. Its numeric wording
belongs to an earlier round. The baseline is frozen and this file does not edit
it; the discrepancy is recorded in §11 for the lead.

**Evidence.**
`WS8_semi_architecture/results_ws8.json` → `headline.table`,
`interface_ws8.per_km_margin_paired.corners.nominal`, `interface_ws8.advance_kill`;
`WS8_semi_architecture/REPORT_WS8.md` §4, §6.2, §9;
`WS8_semi_architecture/CHANGELOG_WS8_r3.md`; `BASELINE_v4.md` D13, `BASELINE_v5.md` R36.

**Reproduce.**
```
cd WS8_semi_architecture && python run_ws8.py && python make_report_ws8.py && python verify_ws8.py
```

**What would change it.** A weight allowance for the powertrain — which is a
policy lever, not a physics one, and was run as a sensitivity rather than a
salvation. Or a mass ledger that is wrong: the payloads above are summed from a
component-level ledger and were re-derived by hand in adjudication.

---

## Claim 6 — Waste-heat recovery is a full-load technology on a part-load duty

**Statement (v7, verbatim).** "Waste-heat recovery is a full-load technology on a part-load duty" [v7_claim6]

**Status (v7, verbatim).** "(ratified at semi scale)" [v7_claim6_status]

**What it means.** Bottoming cycles recover a useful fraction of exhaust energy
near rated load and almost nothing below about a third of it. Line-haul cruise
is a part-load condition. So the hardware's mass is carried for the whole
mission to harvest energy on the few minutes of climb — and at fixed GCW that
mass is freight. D14: "Waste-heat recovery is a full-load technology; line-haul cruise" [d14_whr]
"is a part-load condition (~1/3 rated)" [d14_partload].

**The numbers.** The gate was pre-committed at **2.5%** [whr_gate] net of the mass
charge, ensemble-min, the same statistic G1 was read on. Best system per
candidate, wave one:

| candidate | best net margin | clears 2.5%? |
|---|---|---|
| S1 | **+1.75%** [whr_s1] | no |
| S2 | **+1.83%** [whr_s2] | no |
| S3 | **+2.38%** [whr_s3] | no |

Wave two re-tested electric turbocompound alone on the grade-heavy design duty,
where the load fraction is higher and the case is strongest. Same gate,
**2.5%** [etc_gate]: the result is **+1.67%** [etc_min] ensemble-min. The
**85 kg** [etc_mass] it adds costs **0.41%** [etc_payload_penalty] of payload, so it needed
**2.91%** [etc_needed] gross to clear a 2.5% net bar, and it recovered less than
that. Dropped on both waves.

**Evidence.**
`WS8_semi_architecture/results_ws8.json` → `interface_ws8.whr_gate`, `task4_whr`;
`WS9_vehicle_one_wave2/results_ws9.json` → `etc_gate`;
`WS8_semi_architecture/REPORT_WS8.md` §7; `BASELINE_v4.md` D14.

**Reproduce.** Both commands above; the gate is `task4_whr` in WS8 and `etc_gate`
in WS9.

**What would change it.** A duty with a higher sustained load fraction — the
claim is scoped "at semi scale" on these two duties and says nothing about a
pinned-point genset, which is the one host where a bottoming cycle sees constant
rated load. That case was flagged by the principal, ruled signal, and never
run: it is part of the open frontier (§10).

---

## Claim 7 — Zero-mass levers are symmetric

**Statement (v7, verbatim).** "Zero-mass levers are symmetric; predictive energy management is" [v7_claim7]
worth ~0 when the incumbent gets it too.

**Status (v7, verbatim).** "worth ~0 when the incumbent gets it too (provisional, PRE-B2)" [v7_claim7_status]

**What it means.** A lever that costs no mass and needs no new hardware can be
fitted to the incumbent as easily as to the candidate. Scoring a candidate that
has it against a ruler that does not compares two control strategies and calls
the difference an architecture. So the trial fitted predictive energy management
to the ruler and measured what it was worth there.

**The numbers.** Preview fitted to the ruler, paired per-seed, per payload
tonne-km:

| duty | ensemble-min | median |
|---|---|---|
| grade-heavy design duty | **-0.09%** [pem_design_min] | **+0.03%** [pem_design_med] |
| flat line-haul control duty | **-0.35%** [pem_control_min] | **-0.22%** [pem_control_med] |

It is worth approximately nothing, and the reason is physical rather than
numerical: the integrator's driver already cuts fuel on overrun and already
governs its descent speed against its retarding capability, so the crest half of
the preview law is largely already there; and the pre-boost half buys kinetic
energy at an aerodynamic cost scaling with the cube of speed,
"on a corridor averaging over 90 km/h" [ws9_corridor_speed]. Doctrine D17: "Zero-mass levers are symmetric" [d17_zeromass].

The consequence for the trial is the useful part: the candidate carrying preview
(S6, **+7.50%** [s6_design] design duty / **+7.26%** [s6_control] control duty at
**20,655 kg** [payload_s6] payload — nothing added) has a margin that is its
engine and essentially nothing else. S6 is an engine bet, not a drivetrain
result, and the lead recorded it that way when the verdict was taken.

**Evidence.**
`WS9_vehicle_one_wave2/results_ws9.json` → `bracket_margins.GH-REG-165.S0R-PCC`
and `bracket_margins.LH-520.S0R-PCC`; `WS9_vehicle_one_wave2/REPORT_WS9.md` §8
(bracket table) and its ESC-5 discussion; `BASELINE_v5.md` D17.

**Reproduce.** The WS9 command above.

**What would change it.** A duty with more elevation change per kilometre, or a
ruler whose driver model is less capable — this measurement is against a ruler
that already does most of what preview would add, and a weaker ruler would make
preview look better. Note also that the status v7 attaches, PRE-B2, is a
blocking finding about a *different* measurement in the same workstream (a
concordance denominator that was tautologically zero); the PEM bracket itself is
a two-sided measurement. The status is carried here exactly as v7 writes it and
is not adjusted — see §11.

---

## Claim 8 — The method

**Statement (v7, verbatim).** "The method: pre-registration, pre-committed kill criteria, fresh-" [v7_claim8]
"context disk-only adjudication, three-way verification, export" [v7_claim8_disc]
discipline — "five-for-five first-pass defect detection" [v7_claim8_rate],
including "the lead's own errors (ratified by its record)" [v7_claim8_status].

**Status (v7, verbatim).** ratified by its record.

**The evidence is [METHOD.md](METHOD.md)**, which enumerates seven first passes
with a citation each, the failure-modes catalogue those passes produced, and the
one occasion on which the structure was removed. The wording difference between
v7's "five-for-five" and the enumerated seven is recorded in §11 and in
METHOD.md §3; the baseline is frozen and neither file edits it.

The claim's limitation is the first line of this file and of METHOD.md. What was
detected, seven times out of seven, was internal inconsistency. No instance of a
wrong physical model being caught appears anywhere in this record.

---

## 9. Two facts the baseline does not carry, and this file must

`BASELINE_v7_FREEZE.md` states V1's ADVANCE at **+20.11%** [v1_nominal_min] with
worst corner **+19.12%** [v1_worst_corner], conditional on four rulings that were
never run. The workstream's own report prices two of those conditions, and those
figures are not in the baseline. They are load-bearing for anyone reading the
+20.11% headline.

**Fact 1 — V1's governing corner falls to +3.66% when both pending rulings apply
together.** `WS11_vehicle_zero_ruler/REPORT_WS11.md` §0 (line 39), on V1:
"which take its governing corner to +3.66%" [ws11_366] — i.e. ESC-2 (does the
cab-heat member extend to Vehicle Zero?) and ESC-4 (CdA 4.2 or 5.4?) applied at
once. The exported field is
`WS11_vehicle_zero_ruler/results_ws11.json` → `interface_ws11.cold_corner_pending_items.V1_on_VOLT-SUB.with_cab_heat_and_CdA_5p4_pct`
= **+3.66%** [v1_cold_both]. It still clears the 0% corner bar. It clears it by
about three points rather than nineteen.

**Fact 2 — the harshest defensible cab-heat reading takes that same corner
negative.** `WS11_vehicle_zero_ruler/REPORT_WS11.md` §0 (line 35):
"the harshest one takes V1's governing corner negative" [ws11_negative], and §5
(line 284): "under the harshest cab-heat reading V1's governing corner goes NEGATIVE" [ws11_negative_body],
which is a fail against the >=0% corner bar. The three readings side by side, on
V1's cold corner, from `results_ws11.json` → `cold_cab_heat_bracket.V1_on_VOLT-SUB`:

| cab-heat treatment | V1 cold corner, ensemble-min |
|---|---|
| as ordered — the gated number | **+19.12%** [v1_cold_ordered] |
| round 1's single-pass smear | **+2.64%** [v1_cold_cabheat_r1] |
| fixed-point smear (round 2) | **+4.72%** [v1_cold_cabheat_fp] |
| no waste-heat credit at all — the harshest reading | **-5.42%** [v1_cold_no_credit] |

Neither reading is ordered: the assignment specified no cab-heat member at all,
and both Vehicle Zero candidates carry a running diesel whose coolant genuinely
is free while it runs, so charging the full
"3.0 kW of cab heat during the engine-off windows only" [ws11_cabheat_kw] as an
electric load across the whole cycle is deliberately pessimistic. But the span
from -5.42% to +4.72% is the honest width of a member that is not modelled at
the right time resolution, on the corner V1's ADVANCE is gated on. The ruling that would close it, ESC-2, was
never made.

**Status is unchanged by both facts.** V1 remains exactly what v7 labels it:
"FROZEN-PROVISIONAL ADVANCE, +20.11% nominal" [v7_v1_state]. These figures are
what "provisional" is carrying.

---

## 10. The frozen state, workstream by workstream

Exactly as `BASELINE_v7_FREEZE.md` records it. R51:
"Anything mid-flight at the moment of freeze completes its" [v7_r51] CURRENT step
only. R53: "The Fable adjudication of WS9 is CANCELLED" [v7_r53].

| workstream | state at freeze |
|---|---|
| WS1 loads & duty cycles | closed, ratified with amendments (BASELINE_v1) |
| WS2 traction motor | closed-ratified at round 4; round 3 had stopped NOT CONVERGED |
| WS3 battery | closed-ratified |
| WS4 genset / G1 | gate executed; the KX round is "KX: NOT CONVERGED after three rounds (radiator sizing case" [v7_kx_state] "103.5 vs 95.0 kW)" [kx_radiator_v7] |
| WS5 controls | "WS5: status per its packet at freeze" [v7_ws5_state] — gated, no adjudication round was ever run, and no `PM_PACKET_WS5.md` exists on disk (§11) |
| WS6 packaging | never started; blocked on two upstream blocking findings |
| WS8 semi architecture | verdicts final; numbers FROZEN-PROVISIONAL at r3, "r3 adjudication not clean, r4 ordered and" [v7_ws8_r4] not run |
| WS9 wave two | "WS9: S6 / S4' / S5-13L / S7 FROZEN-PROVISIONAL ADVANCE on" [v7_ws9_state] grade-heavy regional duty; S5-11L KILL; ETC dropped; known open "findings PRE-B1..B3; S5-13L expected to convert to KILL-ON-TIME under" [v7_ws9_open] R46 |
| WS11 ruler trial | V1 FROZEN-PROVISIONAL ADVANCE, V2 FROZEN-KILL; round 2 gated but never adjudicated |

The wave-two candidates that carry provisional advances, for completeness:
S6 **+7.50%** [s6_design] / **+7.26%** [s6_control];
S4' **+11.95%** [s4p_design] / **-6.81%** [s4p_control] at **20,134 kg** [payload_s4p];
S5-13L **+5.36%** [s513_design] / **-1.38%** [s513_control] at **19,706 kg** [payload_s513];
S7 **+4.51%** [s7_design] / **-1.45%** [s7_control] at **19,846 kg** [payload_s7];
against a ruler carrying **20,655 kg** [payload_s0r] with its retarder mass
charged. Every one of them wins on the grade-heavy design duty and all but S6
lose on the flat control duty, which is claim 3's duty boundary appearing again
at four times the mass.

**The open frontier (R54).** Not cut, not killed, listed:
"WS6, WS7, WS10, Vehicle Zero wave two (R48) and Vehicle One" [v7_r54] wave three.
Their intents, from the assignments and rulings on disk: WS6 is packaging and the
program heat ledger (`WS6_packaging/ASSIGNMENT.md`); WS7 is the prototype and
test plan, and carries the mandatory ruler calibration that would make any
Vehicle Zero verdict more than model-relative; WS10 is the combination trial
(S6's engine with S5-13L's two-speed and lean motors); R48's Vehicle Zero wave
two poses an Atkinson-petrol genset for Postal and a mass-lean hybrid for
regional delivery; Vehicle One wave three was never scoped.

---

## 11. Where the record disagrees with itself

Recorded, not resolved. This publication may not edit a baseline or a report,
and does not rule on anything. Each item is a place where two artefacts on disk
say different things, found while grounding this file's numbers.

1. **Claim 5's "(S3 excepted)" clause is a round-2 fact carrying a round-3
   label.** At r3, S3's paired per-km margin is **+4.88%** [s3_perkm_min] with
   `wins_on_every_seed = true` [s3_wins_every_seed]; and S4's **+3.36%** [s4_perkm_min]
   sits below the claim's quoted "6-10%" band. Source:
   `WS8_semi_architecture/results_ws8.json` → `interface_ws8.per_km_margin_paired.corners.nominal`.
2. **Claim 8's "five-for-five" predates two of the first passes it describes.**
   Seven first-pass reviews are enumerated with citations in METHOD.md §3; two of
   them (WS9's pre-adjudication and WS11 r1) returned findings before v7 was
   written.
3. **Claim 7's status cites PRE-B2, which is about a different measurement.**
   PRE-B2 in `WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md` concerns a
   concordance denominator that was tautologically zero; the predictive-energy
   bracket is measured two-sidedly. The claim may still be provisional for other
   reasons — the workstream carries PRE-B1..B3 open — but the specific citation
   does not resolve to the specific measurement.
4. **v7 points WS5 at a packet that does not exist.**
   "WS5: status per its packet at freeze" [v7_ws5_state]; there is no
   `PM_PACKET_WS5.md` in the tree. The nearest artefact is `WS5_controls/REPORT_WS5.md`,
   whose §1.2b reads v7 as making that report WS5's frozen status, and whose §14
   is the workstream's own weakness list, written because
   "WS5 is the only workstream of the night with ZERO adjudication rounds" [nx_ws5].

These four are the product of the method working on itself, which is the only
kind of finding it is entitled to produce.

---

## Provenance

Every number above is generated by `WS13_publication/build_citations.py` from the
workstream results files and verified by `WS13_publication/verify_ws13.py`, which
re-resolves each citation from its source, checks the source's SHA-256 against
the ledger, and asserts that the value printed to you is the value on disk. The
full index is [`WS13_publication/CITATIONS.md`](WS13_publication/CITATIONS.md).
The WS11 hot-swap seam figure — WS11 reproducing WS4's own exported series-duty
ensemble to **0.0e+00** [ws4_seam] — is an example of the same discipline applied
between workstreams rather than between a report and its data file.

Two figures that a reviewer should not have to hunt for, because they qualify
capability claims rather than energy claims: V1's sustained speed on a 6% grade
with no buffer contribution is **31.76 km/h** [v1_sustained_6pct] against the
ruler's **82.01 km/h** [ruler_sustained_6pct], and V2's worst unserved bus energy
on its governing corner is **1.7204 kWh** [v2_unserved] — it empties the pack on
the climb. Neither is a gate; both are on the record and are escalations ESC-5
and ESC-9 of WS11.
