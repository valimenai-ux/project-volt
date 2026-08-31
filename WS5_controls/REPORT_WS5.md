# REPORT WS5 — SUPERVISORY CONTROLS FOR A DUAL-SERIES PROGRAM

Workstream WS5 · Vehicle Zero · run of record `2026-08-31` · entry point `run_ws5.py` · results `results_ws5.json`

**Architecture of record.** Both variants are PURE SERIES. BASELINE_v3 executed Gate G1's kill clause: the clutch, the lockup device and actuator, clutch-sync control, R11's condition-aware mode policy, fault spec F-1 and the i-MMD topology reference are all deleted. This workstream contains no clutch, no mode selection and no synchronisation, and consumes no field of `interface_ws4.gate_g1`, which is an archived record block carrying `status: executed_kill_2026-08-30`.

**First pass.** No `FINDINGS_WS5_r*.md` exists in this folder, so this is not a rework artifact and carries no changelog.

## 1. Assumptions, conventions and what governs

### 1.1 Authority

The assignment directs me to `../BASELINE_v3.md`. Since it was written, BASELINE_v4 and BASELINE_v5 were ratified, and **WS5 was tasked and ran against v5**, which was the highest-numbered baseline at the root when this pipeline was designed and started. Where v3 and v5 differ, v5 wins. Two v5 items bind this artifact directly:

* **R34 (program hygiene)** names WS5 explicitly — every pipeline exports a 10 Hz trace file per run, and *"WS5, WS9 re-runs, and all later work comply from their next artifact."* This artifact complies: three 10 Hz traces are exported (§10).
* **R32 (Vehicle Zero consistency flag)** — the payload-denominated metric has not been applied to Vehicle Zero and must be before any Vehicle Zero result is called an efficiency advantage. WS5 exports `fuel_energy_kWh_per_payload_tonne_km` alongside the per-km metric throughout and claims no efficiency advantage anywhere.

**BASELINE_v6 (07:39) and BASELINE_v7_FREEZE (07:57) were both ratified while this pipeline was executing.** v7 is the governing state of the program. WS5 did not run against either and does not act on either; §1.2b records what they say and what, if anything, it does to this artifact, as a provenance observation for the lead.

Rulings consumed as given, not relitigated in the analysis: R2, R3, R5, R8, R9, R10, R12, R13, R14, R15, R16, R17, R18, R19, R22(a-d), R22b, R22c, R34, E23. Challenges are in §12, each citing the ruling it challenges.

### 1.2 Conventions

| convention | source | as applied here |
|---|---|---|
| 10 Hz control loop and interfaces | R9, assignment | every sample in every run; state machine stepped once per sample |
| bus-side electrical quantities | R12 | every kW and kWh in this report unless a name says `_wheel` or `_shaft` |
| 8-seed ensemble envelopes | R9 | VOLT-REG seeds [23, 3, 4, 5, 6, 7, 8, 9], VOLT-SUB seeds [11, 3, 4, 5, 6, 7, 8, 9] |
| part-load models, never peak-point scalars | R9 | WS2's measured inverter+motor maps × 0.97 reduction (R12) and WS4's Willans BSFC + generator maps; no scalar efficiency member anywhere |
| R14 export discipline | R14 | every worst-case field in §11 is an explicit max/min over an enumerated case set with the governing case labelled inline |
| rejected heat by component and case | R9 | §9, exported to WS6 |
| strictly causal control | WS5 declaration | no preview, no route lookahead; every filter is a one-pole low-pass on measured history |

**Where a scalar could have crept in, and did not.** R9 forbids peak-point efficiency scalars. There is no scalar efficiency branch in the WS5 supervisor at all: the traction chain is always WS2's measured map (WS1's `part_load_factor` path is never taken), the generator is always WS4's loss model, and the engine is always WS4's Willans map. Three fixed factors do appear and each is a ruled convention rather than an efficiency estimate — the 0.97 reduction stage (R12), the 0.97 buffer round trip (WS1's ratified convention, carried so WS5 and WS4 book energy identically), and a 1.06 seed used only to *start* the set-point search on the best-BSFC locus, after which the real map decides. WS3's electro-thermal pack model runs alongside the 0.97 convention as the source of limits and heat; the difference between the two accountings is exported rather than hidden.

### 1.2b Provenance observation: two baselines landed during this run

Stated as a provenance observation, not as a ruling read or relitigated. WS5 was tasked against BASELINE_v3, redirected to v5, and ran to v5. While `run_ws5.py` was executing, two further baselines were ratified at the repository root:

* **BASELINE_v6.md** (07:39) — Vehicle Zero dispositions and two rules that touch this artifact. **R42 KILLS V2 Trucker** on the Vehicle Zero ruler criterion; **R43** makes V1 Postal ADVANCE-PROVISIONAL; **R49** records KX as NOT CONVERGED with a lead-supervised round 4 authorised, and orders that round to *reverse ESC-12's conclusion on the record*; **R50** adds a pin-lock rule (sha pins captured at READ time, not rebuild time).
* **BASELINE_v7_FREEZE.md** (07:57) — the principal's RESEARCH FREEZE. **R51**: anything mid-flight completes its CURRENT step only and stops. **R52**: every verdict and number keeps the status it holds at freeze, labelled FROZEN-&lt;status&gt;. The freeze names this workstream: *"WS5: status per its packet at freeze"* — i.e. this document is WS5's frozen status.

**What WS5 does about them: nothing but record them.** BASELINE_v6.md (07:39) and BASELINE_v7_FREEZE.md (07:57) were both ratified WHILE run_ws5.py was executing. WS5 did not run against either and does not act on either. REPORT_WS5.md section 1.2b records what they say and what they do to this artifact, as a provenance observation. v7 is the program's governing state and names this workstream: 'WS5: status per its packet at freeze'.

**Adjudication.** CUT by BASELINE_v7's research freeze. This packet is gated-but-unadjudicated; REPORT_WS5.md section 14 is WS5's own statement of what is weak in its own work, written because no adversarial reviewer will supply one.

Four consequences are worth the lead's eye, and each is left to the lead:

1. **R42 post-dates the V2 dispatch trade in §4.** That trade recommends a genset dispatch for a V2 Trucker whose Vehicle Zero candidacy R42 has since killed on the regional duty. The control result is unaffected — it is a property of the architecture, not of the business case — but a reader should not take §4 as advocacy for a vehicle the program has since killed. §5's V1 result attaches to the variant R43 advanced.
2. **R49 supersedes the ESC-12 note in §10.1.** WS5 consumed the KX r3 vintage, in which WS4 had WITHDRAWN its R20 radiator-survival verdict. R49 has since ordered KX round 4 to restate the sizing case as the simulated R6 corner and reverse that withdrawal. §10.1's heat block is unchanged and still correct as flows; the note attached to it describes the r3 state, and WS6 should read it against KX r4, not against r3.
3. **R50 is what this workstream already does.** The hot-swap seam of §1.3 captures every sha pin at READ time through one module. WS5 records the agreement; it claims no credit for anticipating a rule that did not exist when it was built.
4. **R51/R52 govern how this packet should be read.** It is the completion of the current step, and every number in it is FROZEN-<status> at whatever status the lead assigns. **Its adjudication round has been cut**, so nothing here has been adversarially reviewed. §14 lists, plainly, what WS5 believes is weak in its own work.

### 1.3 The consumed vintage, pinned

Everything WS5 reads from another workstream enters through one module, `ws5_inputs.py` — the hot-swap seam. WS4's KX round is gated but, at the time of this run, **not yet adjudicated**; a corrected vintage swaps in by re-running `run_ws5.py`, with no WS5 code change, and the pins below flip.

| input | SHA256 (first 16) |
|---|---|
| `WS1/results.json` | `14cb34639be0aa16` |
| `WS2/results.json` | `78266ce69cf6485e` |
| `WS2/data/effmap_motor_inverter_662V.csv` | `e0f617eafbcead33` |
| `WS3/results.json` | `0f766f86ef39e541` |
| `WS3/regen_acceptance.csv` | `08cb24a3f8709d6f` |
| `WS4/results_ws4.json` | `b02a6c82fbbe8d3e` |
| `WS4/ws4_models.py` | `33d9b498ec5bb59d` |
| `WS4/ws4_chain.py` | `5ee6b02df36903b5` |

WS4's `series_duty_v2` block is consumed as a **live design input** (`_status: live_design_input`), across the three cases it exports, at its own declared input pins:

* `WS1/results.json` → `14cb34639be0aa16`
* `WS1/volt_cycles.py` → `d5f663d85e38979c`
* `WS1/volt_params.py` → `0ab8050a09c665c8`
* `WS1/volt_physics.py` → `c99b5a770558b5a0`
* `WS2/data/cycle_loss_summary.csv` → `280f2549950abe39`
* `WS2/data/effmap_motor_inverter_662V.csv` → `e0f617eafbcead33`
* `WS2/results.json` → `78266ce69cf6485e`
* `WS3/regen_acceptance.csv` → `08cb24a3f8709d6f`
* `WS3/results.json` → `0f766f86ef39e541`

**Exactly four members of `interface_ws4` are read by WS5**, and they are read in one place (`ws5_inputs.py`): `series_duty_v2` (the concordance target and the R8-envelope brackets), `spin_drag_operational_note_r22d` (the coast figures), `v1_start_stop`, and `gate_g1.status` — a status string from an archived record block, consumed as provenance and never as a requirement. Anything WS4 changes outside those four cannot reach a WS5 number, and the concordance assertion in §3 is what proves the first of them did not move.

**Vintage of record: KX round 3. WS4's results_ws4.json moved twice during this WS5 session; this artifact pins the KX r3 vintage, and its concordance assertion is exact against it. KX r3 changed exactly one value WS5 reads live - the R22d unbooked-pp member - and changed nothing inside series_duty_v2 -> cases, so no WS5 dispatch, blending, traction, thermal or fault number moved with it.**

`interface_ws4.gate_g1` carries `status: executed_kill_2026-08-30`. WS5's consumption of it: NONE. Archived record block; no field consumed as a live requirement (BASELINE_v3 executed the kill).

### 1.4 What WS5 declared, and where

The supervisor's design freedom is a small set of declared constants. They are exported in `results_ws5.json → control_constants` and the two that could plausibly determine the R22b answer (the two-point notch height and its filter) are swept in §4.4.

| constant | value | basis |
|---|---|---|
| genset load-acceptance ramp | 4 s | WS1 E6's 4 s transient, the same one WS4's 12 g start adder prices |
| genset bus-power slew limit | 25 kW/s | [WS5-DECLARED] |
| V2 genset hysteresis band | 3.5 kWh | WS3's ratified allocation for V2, **not** WS4's simulator default |
| V1 fixed point / band | 35 kW bus / 3.0 kWh | R19, via WS3 `params_ws3.v1_startstop` |
| ESC-9 power-reserve margin | 8 kW | [WS5-DECLARED] |
| two-point notch filter τ | 60 s | [WS5-DECLARED], swept in §4.4 |
| inverter derate onset / trip | 125 / 150 °C | [WS5-DECLARED] against WS2's exported junction figures |
| traction-control μ prior (dry) | 0.80 | [WS5-DECLARED]; the sensor-loss fallback is 0.30 |

## 2. The supervisor state machine

**This section is specification AND implementation: ws5_supervisor.py calls ws5_statemachine.SupervisorStateMachine.step() every 0.1 s sample and acts on what it returns, so every number in this file was produced through this machine**

**FAULT, THERMAL, TRACTION, DISPATCH, BLEND, VEHICLE** — six orthogonal regions, evaluated in that order every 0.1 s sample. 35 states and 34 transitions in total. Within a region every transition has source *any state*; the lowest-numbered eligible guard fires.

**Rendered diagram:** `figs/ws5_state_machine.png`. **Full transition table with guards and the ruling each serves:** `data/state_machine.csv`. **Mermaid source:** `data/state_machine.mmd`.

| region | states | what it decides |
|---|---|---|
| **FAULT** | `F_NONE`, `F_GENSET_LOSS`, `F_PACK_LOSS`, `F_PACK_DERATE`, `F_RESISTOR_LOSS`, `F_INV_DERATE`, `F_SENSOR_LOSS` | what is broken (latched) |
| **THERMAL** | `H_NOMINAL`, `H_PRECOND`, `H_COLD_DERATE`, `H_HOT_PACK_DERATE`, `H_INV_DERATE` | which derate law is in force (R16 cold band, hot pack, inverter junction) |
| **TRACTION** | `T_OFF`, `T_DRIVE_LIMIT`, `T_REGEN_LIMIT` | adhesion limiting (E23, day one) |
| **DISPATCH** | `D_OFF`, `D_START`, `D_PIN`, `D_NOTCH_HI`, `D_FOLLOW`, `D_RESERVE`, `D_MOTOR`, `D_FAULT` | the genset command (R19 / R22b / ESC-9) |
| **BLEND** | `B_NONE`, `B_PACK`, `B_HEATER`, `B_RESISTOR`, `B_FRICTION` | the retardation cascade (R15) |
| **VEHICLE** | `V_OFF`, `V_PRECOND`, `V_READY`, `V_DRIVE`, `V_BRAKE`, `V_LIMP`, `V_HALT` | the mode the driver experiences |

Structural validation (asserted in `run_ws5.py`, not merely reported): every region has a unique initial state, no dangling targets, no unreachable states, no state without an exit, unique priorities within each region, and — the check that matters after Gate G1 — `_has_clutch_state = False`. The following are absent by construction and by assertion: *clutch / lockup states*, *clutch-sync control*, *R11 condition-aware mode policy*, *fault spec F-1 (clutch-open limp)*.

On the reference run (VOLT-REG nominal, seed 23, load_follow) the machine took the transitions listed in `results_ws5.json → state_machine.reference_run.transitions_taken`. The number of samples in which **two specific guards were true at once** — i.e. genuine ambiguity resolved only by the declared priority order — is 0. Each region's priority-90 transition is the deliberate catch-all ("otherwise"), true by construction, and is excluded from that count; counting it would report ambiguity where there is none.

## 3. Verification: WS5 reproduces WS4's ratified run exactly

WS5's supervisor with every WS5 policy layer DISABLED (Cfg.ws4_concordance) is run against WS4's ordered mode-(b) case set. Agreement is exact, so the WS5 numbers below differ from WS4's only by the policy WS5 adds, never by a re-implementation drift.

Over **3 cases × 8 seeds × 8 fields**, the maximum absolute difference between the WS5 supervisor in concordance configuration and WS4's exported `series_duty_v2` per-seed values is **0.0e+00** — verdict **EXACT**.

It also means the hot-swap seam is real: if the KX round is re-adjudicated and a corrected `series_duty_v2` lands, re-running `run_ws5.py` re-derives everything against it, and this concordance assertion fails loudly if the two stop agreeing. It did not: the verdict above is against the KX round 3 vintage.

### 3.1 One observation on the consumed vintage

WS4's ratified simulator computes the BSFC load fraction phi = T/T_max against the DERATED full-load curve on its load-following and emergency branches (_bsfc_fast) but against the UNDERATED curve at the pinned point (WillansEngine.bsfc). At derate 1.0 the two agree exactly, so only the 2,000 m / +45 C case is affected, and the pinned point is the OPTIMISTIC one.

At the 2,000 m / +45 °C derate factor 0.9312, the pinned point's load fraction is 0.850 against the underated full-load curve and 0.913 against the derated one — the latter is past the 0.85 smoke-limit knee, so the pinned BSFC moves from 203.62 to 208.19 g/kWh (+2.25%).

WS5 mirrors WS4 exactly in the concordance block and uses the consistent convention for its own answer. Reported as an observation on a gated-but-not-yet-adjudicated input, not as an escalation: it does not change any WS5 recommendation (verified - the R22b ranking is identical under both conventions). This is reported as an observation on a gated-but-unadjudicated input for the adjudicator's benefit, not as an escalation.

## 4. The V2 dispatch trade (R22b)

R22b (BASELINE_v3): the V2 highway genset dispatch question is a WS5 design question consuming KX's series_duty_v2 exports. Source block: `WS4 interface_ws4.series_duty_v2 (live_design_input)`.

### 4.1 The three candidates

| strategy | definition |
|---|---|
| **pinned point (R22b a)** | engine held at the best-BSFC point of the 4HK1-V2C map whenever running; the only freedom is SOC-hysteresis start-stop on WS3's allocated 3.5 kWh band |
| **two-point (R22b b)** | two notches on the best-BSFC locus: LOW = the pinned point, HIGH = the locus point at the DERATED CONTINUOUS RATING. Notch selection on a 60 s low-pass of measured bus demand with +5 / -10 kW hysteresis |
| **load-following (R22b c)** | engine follows measured bus demand along the best-BSFC locus between 25 kW shaft and the derated continuous rating |

The pinned point is 84.70 kW shaft / 80.61 kW bus at 1288 rpm / 628.0 Nm, 203.62 g/kWh. The two-point HIGH notch is 131.15 kW shaft / 125.92 kW bus, 213.51 g/kWh — taken from the **derated continuous rating**, not fitted to the duty, so the trade is not tuned to its own answer.

### 4.2 The decision rule, declared before the numbers were read

* **DR1_fuel** — rank on fuel_energy_kWh_per_km, 8-seed ensemble MEDIAN, at the nominal case; the chosen strategy must not be more than 0.5% worse than the best at ANY enumerated case
* **DR2_capability_of_record** — unserved bus energy below 0.1% of that run's bus energy AND unserved wheel energy below 0.1% of that run's wheel work, on every seed of every case - a completion tolerance, not a perfection gate
* **DR3_nvh** — among strategies within 1.0% of the best on DR1, choose the lowest NVH index = ensemble-max(genset_starts_per_h) + ensemble-max(setpoint_transitions_per_h)/10. A strategy that beats the field by MORE than 1.0% on DR1 wins outright.
* **DR4_tiebreak** — lower ensemble-max dpdt_p95_kW_per_s

*DR1/DR3/DR4 were fixed in run_ws5.py before the trade was executed and are unchanged. The notch-height and filter sensitivities below exist so the answer cannot be an artefact of one declared constant.*

**DR2 was revised once. This is the disclosure.**

> DR2 WAS REVISED ONCE, AND THIS IS THE DISCLOSURE. As first declared it demanded ZERO unserved energy. On the first execution it eliminated every strategy, so the rule produced no winner and fell through to a bare DR1 minimum - which is exactly the reading R22b asks me NOT to take, because it discards the cycling and NVH terms the ruling names. The reason a start-stop strategy cannot reach zero is structural, not strategic: once the ESC-9 pack dispatch envelope is ENFORCED and the genset carries a real 4 s load-acceptance ramp, every genset start leaves a residual inside the ramp. DR2 was therefore restated as a 0.1% completion tolerance. The revision was triggered by the rule eliminating everyone - not by which strategy it favoured - and BOTH readings are computed and exported below (dr2_strict_eligible / DR2_eligible per strategy, and the two eligible sets in the recommendation block), so the effect of the change is visible in the artifact rather than asserted in prose.

As first declared, DR2 read: *"unserved bus energy AND unserved wheel energy must be ZERO on every seed of every case, else the strategy is not eligible"* Strategies passing it in this run: `[]` (eliminated every strategy: True). Strategies passing DR2 of record (completion tolerance 0.001 of the run's own bus energy): `[]`.

**The revised DR2 did not rescue the rule either — and the reason is a finding, not a nuisance.** Read the capability table above carefully. The BUS-side term passes for all three strategies (worst case 1.4e-04 of the run's bus energy, and exactly zero for the recommended one). What fails is the unserved WHEEL term, and it is **identical for all three strategies** at `cda_5.4` and at `alt2000m_45C` — because it is not a dispatch property at all. It is the inverter thermal derate shedding traction torque when the junction proxy crosses its onset at high drag and at the hot corner, and the genset has no say in it. DR2 was written to exclude a dispatch that cannot complete the duty; it caught a thermal limit that every dispatch shares equally. That belongs to the LT loop and the inverter, not to R22b, and it goes to WS5-T9.

So the rule falls through to DR1 and selects on fuel. Before accepting that, note what makes the outcome robust rather than arbitrary: the same strategy is the minimum on fuel at **every** enumerated case (§4.3, first table); it is the only one that satisfies DR1's all-case clause; it is strictly the lowest on unserved BUS energy (exactly zero); and on the unserved WHEEL term it ties with the other two, because that term is not a dispatch property. There is no reading of DR2 — strict, tolerant, or per-case — under which a different strategy wins. The rule's failure changed which arguments got to speak, not the answer.

### 4.3 Results

Fuel energy per km, 8-seed ensemble (min / **median** / max), kWh/km:

| case | pinned point (R22b a) | two-point (R22b b) | load-following (R22b c) |
|---|---|---|---|
| `nominal` | 1.7098 / **1.7238** / 1.7295 | 1.7499 / **1.7638** / 1.7699 | 1.7066 / **1.7170** / 1.7226 |
| `cda_5.4` | 2.0342 / **2.0483** / 2.0548 | 2.0773 / **2.0951** / 2.1016 | 2.0163 / **2.0297** / 2.0359 |
| `alt2000m_45C` | 1.4606 / **1.4734** / 1.4786 | 1.4620 / **1.4744** / 1.4801 | 1.4364 / **1.4454** / 1.4491 |
| `cold_minus10C` | 1.7899 / **1.8003** / 1.8052 | 1.8288 / **1.8406** / 1.8496 | 1.7781 / **1.7883** / 1.7931 |

Per payload tonne-km (R32), 8-seed median, kWh/payload-t-km:

| case | pinned point (R22b a) | two-point (R22b b) | load-following (R22b c) |
|---|---|---|---|
| `nominal` | 0.59441 | 0.60820 | 0.59206 |
| `cda_5.4` | 0.70632 | 0.72244 | 0.69988 |
| `alt2000m_45C` | 0.50806 | 0.50843 | 0.49842 |
| `cold_minus10C` | 0.62080 | 0.63470 | 0.61666 |

Cycling and NVH-relevant transition rates, 8-seed **max**:

| case | metric | pinned point (R22b a) | two-point (R22b b) | load-following (R22b c) |
|---|---|---|---|---|
| `nominal` | genset starts/h | 4.37 | 7.65 | 1.10 |
| `nominal` | starts / 8 h shift | 35.0 | 61.2 | 8.8 |
| `nominal` | engine set-point transitions/h | 225 | 374 | 5353 |
| `nominal` | \|dP/dt\| P95 (kW/s) | 0.00 | 0.00 | 20.90 |
| `nominal` | NVH events/h (\|dP/dt\| > 5 kW/s) | 21 | 29 | 2672 |
| `cda_5.4` | genset starts/h | 3.82 | 7.12 | 0.55 |
| `cda_5.4` | starts / 8 h shift | 30.6 | 57.0 | 4.4 |
| `cda_5.4` | engine set-point transitions/h | 782 | 351 | 5951 |
| `cda_5.4` | \|dP/dt\| P95 (kW/s) | 0.00 | 0.00 | 21.52 |
| `cda_5.4` | NVH events/h (\|dP/dt\| > 5 kW/s) | 261 | 28 | 3002 |
| `alt2000m_45C` | genset starts/h | 9.83 | 9.83 | 1.10 |
| `alt2000m_45C` | starts / 8 h shift | 78.7 | 78.7 | 8.8 |
| `alt2000m_45C` | engine set-point transitions/h | 386 | 391 | 4672 |
| `alt2000m_45C` | \|dP/dt\| P95 (kW/s) | 0.00 | 0.00 | 19.59 |
| `alt2000m_45C` | NVH events/h (\|dP/dt\| > 5 kW/s) | 28 | 28 | 2312 |
| `cold_minus10C` | genset starts/h | 4.90 | 7.67 | 1.10 |
| `cold_minus10C` | starts / 8 h shift | 39.2 | 61.3 | 8.8 |
| `cold_minus10C` | engine set-point transitions/h | 269 | 400 | 5509 |
| `cold_minus10C` | \|dP/dt\| P95 (kW/s) | 0.00 | 0.00 | 20.81 |
| `cold_minus10C` | NVH events/h (\|dP/dt\| > 5 kW/s) | 24 | 31 | 2806 |

Capability, per case (8-seed max, kWh) — this is what DR2 reads:

| case | metric | pinned point (R22b a) | two-point (R22b b) | load-following (R22b c) |
|---|---|---|---|---|
| `nominal` | unserved bus energy | 0.0011 | 0.0072 | 0.0000 |
| `nominal` | unserved wheel work | 0.0000 | 0.0000 | 0.0000 |
| `nominal` | seconds clipped at the ESC-9 limit | 2.4 | 6.0 | 0.0 |
| `cda_5.4` | unserved bus energy | 0.0019 | 0.0019 | 0.0000 |
| `cda_5.4` | unserved wheel work | 0.4716 | 0.4716 | 0.4716 |
| `cda_5.4` | seconds clipped at the ESC-9 limit | 1.5 | 2.1 | 0.0 |
| `alt2000m_45C` | unserved bus energy | 0.0105 | 0.0105 | 0.0000 |
| `alt2000m_45C` | unserved wheel work | 0.3409 | 0.3409 | 0.3409 |
| `alt2000m_45C` | seconds clipped at the ESC-9 limit | 8.3 | 8.3 | 0.0 |
| `cold_minus10C` | unserved bus energy | 0.0013 | 0.0068 | 0.0000 |
| `cold_minus10C` | unserved wheel work | 0.0000 | 0.0000 | 0.0000 |
| `cold_minus10C` | seconds clipped at the ESC-9 limit | 1.4 | 4.6 | 0.0 |

Capability rolled up over the case set:

| strategy | worst unserved bus (kWh) | worst unserved wheel (kWh) | worst unserved as a fraction of bus energy | DR2 as first declared | DR2 of record | passes DR1 at every case |
|---|---|---|---|---|---|---|
| pinned point (R22b a) | 0.010496 | 0.471600 | 1.40e-04 | False | False | False (worst +1.93%) |
| two-point (R22b b) | 0.010496 | 0.471600 | 1.40e-04 | False | False | False (worst +3.22%) |
| load-following (R22b c) | 0.000000 | 0.471600 | 0.00e+00 | False | False | True (worst +0.00%) |

### 4.4 The answer is not an artefact of a declared constant

The two-point notch height and its filter are WS5-declared. Both are swept:

| variant | fuel kWh/km (8-seed median) | starts/h (max) | set-point transitions/h (max) |
|---|---|---|---|
| notch = continuous_rating (of record) (132.0 kW shaft) | 1.7638 | 7.65 | 374 |
| notch = 0.75 x continuous rating (99.0 kW shaft) | 1.7346 | 6.57 | 290 |
| notch = 0.90 x continuous rating (118.8 kW shaft) | 1.7443 | 5.46 | 291 |
| filter τ = 30 s | 1.7620 | 7.65 | 353 |
| filter τ = 120 s | 1.7386 | 4.92 | 255 |

Lowering the notch and slowing its filter both help the two-point candidate, and neither rescues it: on VOLT-REG the sustained demand sits near the pinned point, so any second notch above it buys worse BSFC *and* a pack round trip. The best two-point variant here is still worse than both of the other candidates.

### 4.4b The supervisor's own NVH lever

**Why this sweep exists.** a pure-series genset's speed is decoupled from road speed, so its RATE of set-point change is a free control parameter. This sweep prices the fuel cost of a gentler ramp for the load-following candidate - the supervisor's direct answer to an NVH objection.

**The sweep says the lever does not work, and that is worth knowing before anyone reaches for it.** Slowing the slew from 50 to 10 kW/s costs essentially nothing in fuel — but it barely moves the NVH metrics either, because the modulation is not rate-limited in the first place: it follows the road. If NVH turns out to bind in the cab, the answer is not the slew limit. It is either a wider SOC band (let the buffer absorb more of the modulation, at the cost of pack throughput) or the pinned point, at the fuel cost §4.3 prices.

| genset slew limit | fuel kWh/km (median) | set-point transitions/h (max) | NVH events/h (max) | \|dP/dt\| P95 (max) | unserved bus (kWh, max) |
|---|---|---|---|---|---|
| 10 kW/s | 1.7172 | 5205 | 2406 | 15.95 | 0.00000 |
| 25 kW/s | 1.7170 | 5353 | 2672 | 20.90 | 0.00000 |
| 50 kW/s | 1.7170 | 5277 | 2683 | 20.47 | 0.00000 |

### 4.4c A refinement that looked obvious and is wrong

**Why this sweep exists.** The R22b load-following candidate is run with WS4's own 25 kW SHAFT floor, which is what makes it comparable with interface_ws4.series_duty_v2's companion. The 10 Hz reference trace shows the consequence: through surplus stretches (descents, long coasts) the engine holds that floor and burns fuel to charge a pack that regen is already filling. This sweep prices the obvious supervisory refinement - stop the engine instead - as a SENSITIVITY. It is NOT one of the three R22b candidates and it did not decide the recommendation.

| load-following floor policy | fuel kWh/km (median) | genset starts/h (max) | genset duty (median) | set-point transitions/h (max) |
|---|---|---|---|---|
| ws4_25kW_shaft_floor | 1.7170 | 1.10 | 0.823 | 5353 |
| stop_on_surplus | 1.7531 | 24.03 | 0.807 | 5933 |

Stopping the engine through surplus stretches **costs** -2.11% — i.e. it is worse, not better. The reason is legible in the numbers: the stop-on-surplus policy trades a small idle burn for an order of magnitude more starts, and each start costs the declared 12 g adder plus a ramp spent below the best-BSFC point. WS4's floor is not the waste the trace makes it look like. This is reported because the trace made the refinement look obvious and it is worth knowing that it is not; it did not enter the decision rule.

### 4.5 Recommendation

> **load-following (R22b c)** — chosen by *DR1 fallback (no strategy satisfied DR2)*.

Nominal 8-seed median 1.7170 kWh/km; NVH index 596.2; margin over the worst candidate 2.73%.

| strategy | nominal median fuel (kWh/km) | worst case vs best, any case | NVH index |
|---|---|---|---|
| pinned point (R22b a) | 1.7238 | +1.93% | 88.0 |
| two-point (R22b b) | 1.7638 | +3.22% | 49.9 |
| load-following (R22b c) | 1.7170 | +0.00% | 596.2 |

Sets at each stage of the rule: DR2 of record `[]` → within 1.0% of the best on DR1 `[]` → also passing DR1's all-case clause `[]`.

**A fourth argument the decision rule does not carry, and should be seen anyway.** A dispatch that never stops the engine never has a load-acceptance ramp to be caught out by. That is why the recommended strategy carries 0.0000 kWh of unserved bus energy under the enforced ESC-9 pack envelope against 0.4016 kWh for the pinned point without the anticipatory reserve (§8.3). The start-stop strategies need a supervisory remedy to meet the pack's own declared envelope; the continuously-running one does not need one at all.

**The honest shape of this trade, stated plainly.** The pinned point and load-following are the two real candidates and they are not close on the same axis. Load-following wins on fuel at every enumerated case, because a pinned genset banks its surplus through the pack and pays the round trip; the margin grows from a few tenths of a percent at nominal to nearly two percent at the 2,000 m / +45 °C corner, where the derated pinned point is furthest from the demand. The pinned point wins on cycling and NVH by more than an order of magnitude on set-point transitions. Two-point as specified — high notch at the derated continuous rating — is dominated on both axes, and §4.4 shows lowering the notch does not rescue it: on VOLT-REG the sustained demand sits near the pinned point, so a second notch above it only adds round-trip losses.

**Two caveats the lead should weigh with the recommendation.**

*First*, the set-point transition count is a **count**, and it over-states the NVH of a set-point that drifts slowly. The rate metrics are the discriminators and are reported alongside: |dP/dt| P95 and the count of NVH events (|dP/dt| above 5 kW/s — a WS5-declared diagnostic threshold that is deliberately **not** a term in the decision rule, which was fixed first).

*Second*, and this cuts against the naive reading: in a pure-series vehicle the engine is not coupled to the wheels, so its speed does not track road speed under any dispatch. Load-following makes engine power track **bus demand**, which tracks the pedal; the pinned point instead produces start and stop events that are uncorrelated with driver input. Which of those is more objectionable in a cab is a measurement, not a simulation result, and WS5-T11 settles it. What WS5 can say now is that the obvious mitigation does **not** work: §4.4b shows the slew limit is free in fuel and nearly useless as an NVH lever, because the modulation follows the road rather than the rate limit. If the measurement goes against load-following, the honest fallback is the pinned point at the fuel cost tabulated in §4.3 — not a tuned load-follower.

Figure: `figs/ws5_dispatch_trade.png`. Table: `data/dispatch_trade_v2.csv`.

## 5. V1 dispatch (R19) and cross-cycle closure

R19 (BASELINE_v2): WS3's delivered 3.0 kWh hysteresis band on 11.08 kWh usable governs; 16-25 starts/shift at the 35 kW bus fixed point is the ratified scale.

WS5 runs V1 at WS3's own exported fixed point — 35 kW at the bus on a 3.0 kWh hysteresis band of the delivered 11.08 kWh usable pack — over VOLT-SUB, 8 seeds. The genset operating point that delivers it is 37.08 kW shaft at 1572 rpm / 225.3 Nm, 230.35 g/kWh.

**Starts per 8 h shift: 16.5 – 24.8** (8-seed envelope; governing seeds seed 3 of the enumerated 8-seed VOLT-SUB [V1] ensemble and seed 7 of the enumerated 8-seed VOLT-SUB [V1] ensemble). R19's ratified scale is 16–25. Inside the ratified band: **True**.

| V1 on VOLT-SUB, 8-seed | min | median | max |
|---|---|---|---|
| fuel energy (kWh/km) | 1.4056 | 1.4195 | 1.4323 |
| fuel (L/100 km) | 14.21 | 14.35 | 14.48 |
| genset duty (fraction) | 0.243 | 0.284 | 0.297 |
| SOC min (usable) | 0.407 | 0.411 | 0.414 |
| unserved bus energy (kWh) | 0.00000 | 0.00000 | 0.00000 |
| friction-brake energy (kWh) | 0.2132 | 0.2603 | 0.3029 |

**V2 on VOLT-SUB** (the trucker doing urban work — no ruling bars it) runs at 1.3081 kWh/km median, 16.5 starts/shift (8-seed max), 0.00000 kWh unserved.

**V1 on VOLT-REG.** R5 (BASELINE_v1): 'V1 is formally a sub-80 km/h vehicle... V1 shall not be dispatched on regional/highway work, and VOLT-REG is not a V1 cycle.' The assignment's deliverable line asks for closure over VOLT-SUB and VOLT-REG for both variants; R5 forbids the V1 x VOLT-REG combination as a duty case. WS5 runs it as a probe, draws no design conclusion from it, and raises the tension as an escalation citing R5.

The probe's numbers, for completeness only: 2.0401 kWh/km median, unserved bus energy up to 13.900 kWh and unserved wheel work up to 0.000 kWh — i.e. the 50 kW-class genset cannot carry VOLT-REG, which is exactly why R5 exists. WS4's own charge-sustaining ceiling for V1 is 76.5 km/h. **No design conclusion is drawn from this run.** See ESC-WS5-1.

## 6. Blending (R15) and traction control (E23)

### 6.1 The blend order

R15 (BASELINE_v2): **regen-to-pack → pack heater (R16 band only) → brake resistor (forced air, R2) → friction**.

R15 grants WS3's functional goal ELECTRICALLY: the 8 kW heater feeds from the DC bus. The resistor stays forced-air and shares no failure domain with the pack loop.

Implemented bus-side as a saturating cascade: each stage takes what the stage above could not, and the BLEND region of the state machine names the deepest stage taking power in that sample. Coexisting DC-bus loads are carried explicitly — resistor blower 1.45 kW and pack heater 8.0 kW (WS2 `dc_bus_loads_coexisting`).

The pack's limit is WS3's `regen_acceptance.csv` **at the measured cell temperature**, further limited by the WS5 dispatch limit of §8. The resistor's limit is V²/R at the prevailing bus voltage, capped at WS2's element ceiling 150.2 kW; the figure guaranteed at **any** voltage in the R10 window is 50.0 kW, at the 432 V floor. Bus voltage is taken from WS3's pack model at the previous sample (a declared 0.1 s lag — causal, not an implicit solve).

Energy through the cascade on the duty cycle, 8-seed max, kWh per cycle, with the recommended dispatch:

| case | to the pack | to the heater | to the resistor | to friction (at the wheel) | shed by R16 |
|---|---|---|---|---|---|
| `nominal` | 3.782 | 0.000 | 0.000 | 0.615 | 0.0000 |
| `cda_5.4` | 3.195 | 0.000 | 0.000 | 0.569 | 0.0000 |
| `alt2000m_45C` | 4.644 | 0.000 | 0.000 | 0.666 | 0.0000 |
| `cold_minus10C` | 3.782 | 0.000 | 0.000 | 0.615 | 0.0000 |

On the duty cycles the electrical path takes essentially everything: friction-brake energy worst case 0.666 kWh per cycle at `alt2000m_45C`, against regen-to-bus of order 3–5 kWh. The resistor stays cold on the duty cycle (worst 0.000 kWh at `nominal`) — it is a *descent* device, which is §7's subject.

### 6.2 Traction control (E23, day one)

Law consumed from WS2: `T_wheel <= mu_est*N_r_est*r_dyn/(1 -+ mu_est*h/L)`. As implemented: F_max = mu . N_rear_static / (1 -+ mu.h/L); N_rear_static = m.g.(share_r.cos(theta) + sin(theta).h/L). Reproduces WS2's exported traction envelope and mu_required exactly at grade 0 (sanity_checks).

The regen half of E23 is a **cycle-derived** quantity, not a textbook stop. WS1 s4.16 defines the regen half of E23 as the PEAK REGEN FORCE AT THE WHEEL with the 75 kW absorb cap applied, at the operating curb mass. WS5 reproduces that method exactly (WS1's regen_split, consumed read-only) and reports it as an 8-seed envelope, which R9 requires and WS1's single-number table did not carry.

| E23 case | μ required (8-seed max) | WS1 §4.16 |
|---|---|---|
| empty-truck regen stop (curb, VOLT-SUB) | **0.362** | **0.36** |
| the same, at GVW | 0.265 | 0.26 |
| empty-truck regen stop, VOLT-REG | 0.353 | — |
| 13.5 kN launch, curb | **0.654** | **0.66** |
| 13.5 kN launch, GVW | 0.294 | 0.29 |
| **empty-truck regen stop on a 6% descent** | **0.375** | *not named by E23* |

The peak regen force behind the empty-truck figure is 5.80 kN at the wheel (8-seed max) against WS1's tabled 5.8 kN — an independent re-derivation of the same number, from WS1's own cycle builder and regen split, through WS5's own adhesion law.

WS1 s4.16's table is reproduced by WS5's independent implementation: 5.8 kN / mu 0.36 empty and mu 0.26 at GVW on the regen side, mu 0.66 curb / 0.29 GVW on the launch side. The launch figures agree with WS2's exported mu_required to machine precision (sanity_checks). The NEW result is the descent aggravation, which E23 does not name.

**The descent term, kept in proportion.** On a descent the vehicle pitches nose-down and the pitch transfer unloads the single driven axle, so the electric retarder's adhesion ceiling falls exactly where retardation is wanted. The effect is real but **modest**: the empty-truck regen stop needs +3.5% more μ on a 6% grade than on the flat. WS5 is not going to inflate that into a finding it is not. What it does mean is that E23's 0.36 is a *floor*, not a ceiling — the number to design the limiter against is the graded one, and the same geometry that makes launch marginal when empty makes regen marginal when empty and pointing downhill. Test WS5-T5 carries it, on grade as well as flat.

Figure: `figs/ws5_traction_e23.png`.

## 7. The descent, and the resistor-loss case (R2 / R17 / R15)

R2 / R17 (BASELINE_v1/v2): the dynamic-brake resistor is the retardation sink; 50 kW continuous is a CAPABILITY requirement over the full descent, and the blend order owns the energy. R15 fixes the order: regen-to-pack -> pack heater (R16 band) -> resistor -> friction.

Case of record: 10 km sustained 6% descent - WS3's descent case of record (descent_thermal rows), re-run under the WS5 blend order. Swept over five speeds, two masses (GVW and +20% payload), two cell temperatures (+45 °C and −10 °C), **two entry states**, and three configurations: resistor healthy, resistor lost, and resistor lost with the WS5-proposed ISG motoring sink — 120 rows in `data/descent_blend_r15.csv`.

**Every descent row is run from two entry states: WS3's 0.55 SOC target, and 0.95 of usable - the truck that crests with a nearly-full buffer. The second is the case R2 exists for; reporting only the first would flatter the architecture, because the pack's headroom does most of the work on a single descent from mid-SOC.**

| configuration | worst friction-brake energy over the descent | governing row |
|---|---|---|
| resistor healthy | **0.001 kWh** | `payload120/45C/25kmh/soc0.55 (WS3 target)/resistor_healthy` |
| **resistor lost** | **8.10 kWh** | `payload120/45C/25kmh/soc0.95 (crest, buffer nearly full)/resistor_lost` |
| resistor lost + ISG motoring [WS5-PROPOSED] | **4.77 kWh** | `payload120/45C/55kmh/soc0.95 (crest, buffer nearly full)/resistor_lost_with_isg_motoring` |

| entry state | worst friction, resistor lost (kWh) | worst mean friction (kW) | worst resistor duty, healthy (kWh) |
|---|---|---|---|
| soc0.55 (WS3 target) | 3.02 | 11.6 | 2.99 |
| soc0.95 (crest, buffer nearly full) | 8.10 | 40.9 | 8.03 |

With the resistor healthy the blend order holds the friction column at essentially zero across the whole grid — the resistor peaks at 46.9 kW at `payload120/45C/85kmh/soc0.95 (crest, buffer nearly full)/resistor_healthy`, comfortably inside its 150.2 kW element ceiling and, more to the point, below the 50 kW that R17 requires the resistor to carry continuously at ANY bus voltage in the R10 window — so the worst descent in the grid never asks the resistor for more than it is required to provide. That reproduces WS3's own descent finding.

With the resistor lost, three different rows of the grid govern three different extrema, and they are **not the same run** — energy peaks at the slowest speed because that is the longest time on the grade, mean power at the fastest:

| extremum, resistor lost | value | that row's companion values | governing row |
|---|---|---|---|
| worst friction ENERGY | **8.10 kWh** | 20.0 kW mean over 1460 s | `payload120/45C/25kmh/soc0.95 (crest, buffer nearly full)/resistor_lost` |
| worst sustained friction POWER | **40.9 kW mean** | 6.07 kWh over 534 s | `payload120/45C/70kmh/soc0.95 (crest, buffer nearly full)/resistor_lost` |
| worst instantaneous friction POWER | **49.3 kW** | — | `payload120/45C/85kmh/soc0.95 (crest, buffer nearly full)/resistor_lost` |

worst_friction_kWh_resistor_lost and worst_mean_friction_kW_resistor_lost are maxima over the same enumerated descent grid but are attained on DIFFERENT rows: energy peaks at the slowest speed (the longest time on the grade), mean power at the fastest. Each therefore carries its own row's companion value (*_row_mean_kW / *_row_kWh / *_row_duration_s). They must not be quoted together as one operating point. The pure-series architecture has **no engine retardation at all** — the engine is not coupled to the wheels — so once the pack fills there is nothing electrical left.

**The honest statement, stated precisely.** This is the case the assignment told me to treat with the most care, so I will not overstate it in either direction. From WS3's 0.55 SOC target the pack's own headroom absorbs most of a single 10 km descent and the friction column stays modest. From a nearly-full buffer it does not: on the worst-energy row the brakes take 8.10 kWh at 20.0 kW mean over 1460 s; on the worst-power row they take 40.9 kW sustained for 534 s. Whether either is inside the service brakes' continuous, fade-free capability is **not something WS5 can rule** — the program has no friction-brake continuous rating (see ESC-WS5-2) — and WS5 will not assert it either way. What WS5 can say is the shape of the exposure: it is a sustained-fade question, not an instantaneous-capacity one; it is driven by entry SOC, while descent speed only trades total energy against sustained power (slow descents put more energy in over longer, fast ones less energy at higher power); and R2's own rationale (steady 6% descent retardation never exceeds ~46 kW; the deficit is the energy sink) is exactly the observation this table reproduces.

### 7.1 A second speed-independent retarder, at no hardware cost

[WS5-PROPOSED] The crank-mounted ISG can motor the engine, fuel off, against its own friction and pumping work. Reproduces WS4's declared motoring anchor at 1,706 rpm; at the rated-continuous speed it absorbs 15.3 kW at the bus. This is NOT a ruled capability: it needs WS4 sign-off on continuous motoring (engine oiling, generator thermal), a WS7 test, and one declared simplification WS5 makes here: the sink is applied instantly, whereas a stopped engine must first be spun up through the same load-acceptance path a start uses. The fault matrix states the resistor-loss case BOTH with and without it.

Sized: 15.3 kW at the bus at rated-continuous speed. That is not a replacement for the resistor — it removes roughly 8.10 kWh down to 4.77 kWh on the worst row — but it converts an outright loss of retardation into a degraded one, and it costs nothing: the ISG is already specified for R19 starting. It is exported as WS5-PROPOSED, it is **not** counted in the fault capability of record, and it goes to WS4 for sign-off and to WS7 as test WS5-T2. See ESC-WS5-3.

Figure: `figs/ws5_descent_blend.png`. Table: `data/descent_blend_r15.csv`. Trace: `data/trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv`.

## 8. Cold dispatch (R16), the coast policy (R22d) and the ESC-9 dispatch limit

### 8.0 Thermal state on the duty (what the derate laws see)

| case | cell temperature min / peak (°C) | inverter junction peak (°C) | LT coolant (°C) | pack I²R heat (kWh/cycle) | traction-control interventions, regen / drive (s) |
|---|---|---|---|---|---|
| `nominal` | 25.0 / 28.7 | 121.3 | 65 max, ambient + 20 K | 0.636 | 0.0 / 0.0 |
| `cda_5.4` | 25.0 / 26.9 | 133.5 | 65 max, ambient + 20 K | 0.477 | 0.0 / 0.0 |
| `alt2000m_45C` | 45.0 / 47.9 | 131.2 | 65 max, ambient + 20 K | 0.535 | 0.0 / 0.0 |
| `cold_minus10C` | -10.0 / -0.4 | 86.3 | 65 max, ambient + 20 K | 1.561 | 0.0 / 0.0 |

The junction model is a WS5-declared lumped proxy: Tj = T_LT-coolant + 6.15 K/kW × chain loss, first-order with a 30 s time constant, calibrated on the only pair WS2 exports (130 °C junction at the R13 continuous case with 10.57 kW of LT-loop heat and the 65 °C maximum inlet). The coolant is modelled as ambient + 20 K, capped at WS2's 65 °C ceiling, so the loop reaches that ceiling at the +45 °C corner and sits below it everywhere else. It is a derate-law demonstration, not a thermal model of record; WS5-T9 replaces it with a measurement.

### 8.1 Cold dispatch (R16)

R16 (BASELINE_v2): preconditioning required below -15 C CELL temperature; between -15 and +10 C dispatch is permitted on the published derate curves; regen_acceptance.csv is the interface of record.

Heater arbitration with drive power: preconditioning heat yields to traction demand above the WS2 S1 continuous rating (45 kW bus): full 8 kW below it, 35% above it [WS5-DECLARED]

**A confound the table avoids.** The temperature sweep runs at the NOMINAL 2 kW accessory load so the temperature term is isolated. A real cold day also carries a higher accessory load; that term is reported separately as the '-10C, 4 kW aux' row, and the trade's cold_minus10C case (which is the one that gates the R22b answer) carries it too. Reporting a single 'cold penalty' that silently mixes the two would be a confound.

| ambient / cell | fuel penalty vs nominal | heater + preconditioning (kWh/cycle, 8-seed max) | regen shed by R16 (kWh, max) | genset starts/h (max) |
|---|---|---|---|---|
| -20C | +0.83% | 0.202 + 0.702 | 0.3359 | 1.10 |
| -10C | +0.00% | 0.000 + 0.000 | 0.0000 | 1.10 |
| 0C | +0.00% | 0.000 + 0.000 | 0.0000 | 1.10 |
| 10C | +0.00% | 0.000 + 0.000 | 0.0000 | 1.10 |
| -10C, 4 kW aux | +4.16% | 0.000 + 0.000 | 0.0000 | 1.10 |
| 25C, 2 kW aux (nominal reference) | +0.00% | 0.000 + 0.000 | 0.0000 | 1.10 |
| 45C at 2,000 m (the R7 corner, not a hot sea-level day) | -15.82% | 0.000 + 0.000 | 0.0000 | 1.10 |

**A limitation of the accounting, stated before the number is read.** WS5's energy books use WS1's ratified flat 0.97 buffer round-trip convention (carried so WS5 and WS4 book energy identically). That convention is TEMPERATURE-BLIND: a cold pack's higher internal resistance costs nothing in the fuel column, so the temperature term in the table above is close to zero and is UNDERSTATED. WS3's electro-thermal model runs alongside and does see it - the measured pack I2R heat is exported per case below - so the direction and rough size of the omission are on the record rather than hidden. Direction of error: WS5's cold fuel numbers are OPTIMISTIC.

| ambient / cell | pack I²R heat (kWh/cycle, 8-seed max) | WS3 resistance multiplier vs 25 °C |
|---|---|---|
| -20C | 1.970 | 3.60× |
| -10C | 1.545 | 2.60× |
| 0C | 1.145 | 1.90× |
| 10C | 0.868 | 1.40× |
| 25C, 2 kW aux (nominal reference) | 0.636 | 1.00× |

So the physical cold penalty is real and the fuel column does not carry it. A reader should take the temperature row of the previous table as "the cold costs almost nothing *that this accounting convention can see*", not as "the cold is free".

Worst cold penalty from TEMPERATURE alone: **+0.83%** at `-20C` — an explicit max over the enumerated temperature set (R14). The accessory term at −10 °C is a further +4.16 percentage points, i.e. going from 2 kW to 4 kW of accessories costs about as much as the cold itself.

**Where R15's heater stage actually fires.** On the duty cycle it does not: at every temperature inside the R16 band the regen peaks stay below the pack's published acceptance, so stage 1 never saturates and the heater column is zero. The only bus heat drawn on the cycle is preconditioning below −15 °C, which is a different mechanism. The heater's role *as a blend stage* shows up on the cold descent instead — in the descent grid the −10 °C rows put real energy through it once the pack fills. R15's ordering is therefore not decorative, but it is a descent provision, not a duty-cycle one.

Two things the table shows that are worth naming. Preconditioning at −20 °C is a real bus load that has to be arbitrated against traction, not a footnote — the supervisor gives it the full 8 kW below the WS2 S1 continuous rating and 35% above it, and inhibits dispatch until the cell clears −15 °C, exactly as R16 orders. And R16's acceptance curve does not bind on this duty at any temperature in the band: the regen-shed column stays at zero because VOLT-REG's regen peaks sit below the published acceptance even at −10 °C. R16 binds on the *descent*, not on the cycle — which is §7's subject and ESC-WS5-4's.

Figure: `figs/ws5_cold_dispatch.png`.

### 8.2 Coast policy (R22d)

R22d (BASELINE_v3): PM spin drag at zero torque persists whenever coasting without regen (1,109 W shaft / 371 W bus at 85 km/h); the WS5 supervisor prefers light regen over true coast. Consumed from `interface_ws4.spin_drag_operational_note_r22d`: 1109 W shaft / 371 W bus at 85 km/h.

Policy: the supervisor never commands zero traction torque while moving with non-positive wheel demand: the drag torque is turned round through the machine instead of being held at zero. Bus-side swing per sample = (shaft drag x wheel->bus map efficiency) + the standby draw that is no longer paid.

**How the exposure is counted.** R22d's exposure is counted two ways and both are exported. (a) WS4's exact test - wheel demand non-positive AND the regen blend-out has already zeroed capture - kept verbatim so the two workstreams' numbers are comparable. (b) WS5's zero-torque BAND: |P_wheel| within 1.5x the PM drag itself, which scales with speed because the drag does. On a road-load-neutral coast, test (a) is a measure-zero condition and returns nothing; test (b) is the set of samples the ruling is actually about.

**Vintage note.** WS4's KX round 3 re-priced this member. Its round-2 form was built as a ratio of three independently-extremised quantities and rendered as an "at most" — an R36-class construction defect that KX r3 found and corrected to a per-seed paired statistic. WS5 consumes the corrected member: 0.000340 percentage points, governed by *case alt2000m_45C of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within it, seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]*. This is the only value WS5 reads live that KX r3 moved.

On VOLT-REG the exposure is small, because WS1's driver model leaves few zero-torque samples — up to 26.1 s per cycle on WS4's test and 48.7 s on WS5's band — and WS4's own unbooked member is at most 0.00034 percentage points of cycle fuel. **The policy is not about the duty cycle.** It is about sustained coasting, so WS5 built the case R22d actually describes:

* 85 km/h at GVW on the grade that exactly balances road load - a genuine sustained true coast, not a braking event, at -3.071% grade for 600 s. WS4's exact test finds 0.0 s of it — on a road-load-neutral coast that test is a measure-zero condition — while WS5's zero-torque band finds 600.1 s, which is the whole run.
* Zero-torque coast leaves 0.185 kWh of shaft drag unrecovered and still draws 0.062 kWh from the bus to hold zero torque.
* The light-regen policy returns 0.062 kWh to the bus instead. **Net bus swing 0.124 kWh, 0.742 kW mean** over ten minutes of coasting.

R22d's guidance is adopted as written and priced where it bites. Test WS5-T10.

### 8.3 The ESC-9 dispatch limit — WS5 accepts the assignment

WS3's clause, quoted: *"120 kW warm at SOC 15 sits at 527.7 V; the R8 discharge gate is declared over SOC 40-90 and full power below SOC 40 is NOT guaranteed - WS5 dispatch limit"*

WS3 declares the R8 discharge gate over SOC 40-90 of nameplate and states that full power below SOC 40 is NOT guaranteed, naming it a WS5 dispatch limit. WS5 accepts the assignment and makes it operational.

**Limit law.** P_dis_allowed(T_cell, SOC) = min(R8 restated 125 kW bus, WS3 capability_maps.V2_LTO23.dis_pulse10_kW bilinear at (T_cell, SOC_nameplate)); P_chg_allowed likewise against 110 kW and chg_pulse10_kW. SOC_nameplate = end_stop_lo + SOC_usable x (1 - end_stop_hi - end_stop_lo) on WS3's declared 15/10% end stops.

**Enforcement.** enforced, not observed: demand above the limit is unserved and booked. The supervisor's ANTICIPATORY answer is the D_RESERVE state - the genset is commanded up whenever a 2 s low-pass of measured bus demand comes within 8 kW of the limit, so the pack is not asked for power it cannot guarantee.

**The anticipatory reserve is a start-stop remedy. A dispatch that never stops the engine never has a load-acceptance ramp to be caught out by, so its residual is zero with or without the reserve; a dispatch that stops the engine needs it. Both are priced below.**

Priced, against WS4's own bracket for the same three cases (8-seed max, kWh of unserved bus energy):

| case | recommended dispatch, reserve ON | recommended, reserve OFF | pinned point, reserve ON | pinned point, reserve OFF | WS4's R8-envelope bracket |
|---|---|---|---|---|---|
| `nominal` | 0.0000 | 0.0000 | 0.0011 | 0.0021 | 0.0021 |
| `cda_5.4` | 0.0000 | 0.0000 | 0.0019 | 0.0141 | 0.0149 |
| `alt2000m_45C` | 0.0000 | 0.0000 | 0.0105 | 0.4016 | 0.6129 |

The pinned point is where the reserve earns its place: worst case 0.4016 kWh without it at `alt2000m_45C`, 0.0105 kWh with it.

Worst case over the enumerated set: **0.0000 kWh** at `nominal` with the anticipatory reserve, against 0.6129 kWh in WS4's bracket at `alt2000m_45C` — a reduction of **100.0%**. For the recommended dispatch the residual is exactly zero because it never stops the engine. The residual that the reserve has to work against is the pinned point's, and it sits entirely inside the genset's 4 s load-acceptance ramp — which is why WS5-T3 is a blocking test: if the real ramp is slower than 4 s, that residual grows and the start-stop candidates stop meeting the pack's own declared envelope. See ESC-WS5-5.

### 8.4 ESC-8(b) as restated by KX round 3 — it lands on this blend order

**WS4's statement.** KX r3 states the pack reading is violated at every tabulated cell temperature on every seed of every ordered case, and that no cell-temperature limit can rescue the dispatch of record if the lead rules for the pack reading - only a supervisor change or a restated interface rating can. The supervisor is WS5's.

**WS5's position.** WS5 does not resolve this. What WS5 CAN state is what its own blend order does with the overflow, measured on its own runs, and what it cannot do: the R15 cascade spills regen above the pack's published acceptance into heater -> resistor -> friction, which is exactly the mechanism ESC-8 names; it cannot change the pack's rating, and it cannot choose between the pack reading and the cell reading. That choice is the lead's.

**What is actually being measured.** Three different charge quantities are separated here because ESC-8(b) is about the PACK's rating and they are not the same number. (i) regen-to-pack peak: the R15 cascade's first stage, which IS gated by WS3's regen-acceptance curve at the MEASURED cell temperature. (ii) net charge DEMAND peak: genset output minus bus load, before the ESC-9 clip - a demand, not something the pack sees. (iii) net charge ACTUAL peak: what the pack is asked to take after the ESC-9 clip. The acceptance curve is a REGEN acceptance curve; surplus charge from the genset is gated by the ESC-9 envelope (R8's 110 kW bus against WS3's chg_pulse10 map), not by it. Whether the acceptance curve ought to bind ALL charge or only regen is part of what ESC-8(b) is asking, and WS5 does not answer it.

Measured on WS5's own runs, with the recommended dispatch. All figures are 8-seed ensemble maxima (R9); every one carries its governing seed in `results_ws5.json`:

| case | entry cell °C | peak cell °C | WS3 regen acceptance at entry / at peak (kW bus) | regen-to-pack peak (kW) | net charge demand peak (kW) | net charge **actual** peak (kW) | exceedance of entry-T acceptance (kW) | s above the **measured-T** acceptance | kWh above it | s above R8's 110 kW | regen shed by R16 (kWh) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `nominal` | 25 | 28.7 | 130.8 / 130.5 | 69.0 | 93.6 | 93.6 | -37.2 | 0.0 | 0.0000 | 0.0 | 0.0000 |
| `cda_5.4` | 25 | 26.9 | 130.8 / 130.6 | 69.0 | 92.6 | 92.6 | -38.1 | 0.0 | 0.0000 | 0.0 | 0.0000 |
| `alt2000m_45C` | 45 | 47.9 | 129.1 / 109.3 | 69.1 | 91.6 | 91.6 | -37.6 | 0.0 | 0.0000 | 0.0 | 0.0000 |
| `cold_minus10C` | -10 | -0.4 | 67.0 / 100.0 | 69.0 | 89.4 | 89.4 | +22.5 | 74.5 | 0.2428 | 0.0 | 0.0000 |

Worst exceedance of the entry-temperature acceptance curve over the enumerated case set: **+22.5 kW** at `cold_minus10C`. Worst time above the acceptance curve the supervisor actually enforces (measured cell temperature): **74.5 s** at `cold_minus10C`, carrying **0.2428 kWh**.

Measured, not asserted. Against the acceptance curve at the ENTRY cell temperature, the pack's actual net charge peak crosses in 1 of 4 enumerated cases (cold_minus10C); against the curve the supervisor actually enforces - the acceptance at the MEASURED cell temperature, sample by sample - it crosses in 1 of 4 cases (cold_minus10C), for a worst 74.5 s and 0.2428 kWh over the cycle. The gap between those two readings is the pack self-heating: a cold pack entered at its declared temperature warms under its own I2R and its acceptance rises with it, so an entry-temperature comparison overstates the crossing. WS5 reports both because ESC-8(b) does not say which one it means. What WS5 cannot do either way is change the pack's rating or choose between the pack reading and the cell reading. See ESC-WS5-4.

### 8.5 ESC-10 as restated by KX round 3 — what option (b) would cost

**WS4's statement.** The ordered run spends time above the genset's 132 kW continuous flat-rating; the disposition options are to accept short excursions to the automotive curve, or to make the continuous rating a WS5 CONSTRAINT at the bracketed cost.

**The implementation fact that answers it.** WS5's set-point generator caps every commanded operating point at the DERATED CONTINUOUS RATING (GensetCmd.point_for_shaft, allow_peak=False) in every dispatch state except the emergency SOC band, which is the only state that raises the cap to the peak curve. So 'seconds above the continuous rating' equals 'seconds in the emergency band' for every WS5 dispatch.

| strategy | worst seconds in the emergency band (= seconds above the derated continuous rating) | governing case |
|---|---|---|
| pinned point (R22b a) | 380.0 s | `cda_5.4` |
| two-point (R22b b) | 0.0 s | `nominal` |
| load-following (R22b c) | 0.0 s | `nominal` |

**What option (b) would cost this dispatch: ZERO for the recommended dispatch. The recommended strategy never enters the emergency band on any seed of any enumerated case, so it is already inside the constraint option (b) would impose and adopting that option costs it nothing. The pinned-point candidate is not: it enters the band at the high-drag case. WS5 states the cost and does not choose the disposition.** See ESC-WS5-6.

## 9. Fault matrix

R22c (BASELINE_v3): with no mechanical path, BOTH variants share the genset-or-pack-fault = tow asymmetry; the WS7 test plan carries it.

Each fault is injected at t = 1800 s into VOLT-REG, nominal case, 8-seed ensemble, latched, and the run continues. Limp capabilities are stated as measured, not as hoped.

| fault | detection | supervisor response | ruled outcome |
|---|---|---|---|
| **`genset_loss`** | loss of rectifier DC current with engine-run confirmed, or engine stall/overspeed/oil-pressure trip; 200 ms confirm | DISPATCH -> D_FAULT; the pack alone carries the bus; SOC floor management drops the drive-power ceiling; the R15 cascade still has resistor + friction for retardation | R22c: TOW once the buffer is spent |
| **`pack_loss`** | main contactor open, isolation fault, or BMS shutdown request; 100 ms confirm | the bus loses its only voltage source and its only transient buffer. The genset can regulate the bus, but its load-acceptance ramp is 4 s: every transient becomes unserved wheel work. Retardation loses the pack column entirely, so the R15 cascade starts at the heater. | R22c: TOW |
| **`pack_derate`** | BMS derate request (cell temperature, imbalance, string isolation) - a derate, not a loss | the ESC-9 dispatch limit tightens to the derated envelope; D_RESERVE raises the genset earlier and more often; regen spills down the R15 cascade to resistor and friction | derated limp, cycle completable |
| **`resistor_loss`** | chopper fault, element open/short, or blower loss (the blower is a 1.45 kW bus load whose current is measured) | R2's sink is gone. Retardation = regen-to-pack until the pack fills, then the 8 kW heater if the cells are cold, then friction. THE CASE TO TREAT WITH MOST CARE: the resistor is the only SPEED-INDEPENDENT retarder in a pure-series vehicle, and pure series has no engine retardation at all. | descent-restricted limp; see descent_r2_r17 |
| **`inverter_thermal`** | junction-temperature estimate above the derate onset, or a measured NTC on the module baseplate | THERMAL -> H_INV_DERATE; the traction torque command is scaled linearly from the onset to the trip; regen is scaled by the same factor, which pushes retardation into the resistor and friction columns | derated limp, both directions |
| **`sensor_loss`** | plausibility cross-check failure between wheel speed, motor resolver, bus current and pack current | the supervisor falls back to the most restrictive assumption for the lost signal: wheel speed -> traction control assumes the low-mu prior; cell temperature -> the R16 cold-band derate is assumed; SOC estimate -> the usable window is narrowed to the hysteresis band | derated limp |

| fault | unserved bus (kWh, max) | unserved wheel (kWh, max) | friction (kWh, max) | fuel penalty | first unserved sample after injection (s) |
|---|---|---|---|---|---|
| `genset_loss` | 63.1590 | 0.0000 | 0.615 | +2.95% | 0.0–259.4 |
| `pack_loss` | 2.8046 | 0.0000 | 0.615 | +9.39% | 0.0–0.0 |
| `pack_derate` | 0.3136 | 0.0000 | 0.615 | +0.65% | 265.8–2494.7 |
| `resistor_loss` | 0.0000 | 0.0000 | 0.615 | +0.00% | none |
| `inverter_thermal` | 0.0000 | 25.2368 | 1.702 | +2.90% | none |
| `sensor_loss` | 0.0000 | 0.0000 | 0.615 | +0.00% | none |

### 9.1 Limp capability, stated honestly

* **`genset_loss`** — Pack-only. The delivered pack holds 11.08 kWh usable at the bus; on VOLT-REG's measured bus demand that is a limp of the order of tens of minutes, then TOW (R22c). WS5 does NOT claim a get-home capability.
* **`pack_loss`** — Genset-only on a bus with no buffer and a 4 s load-acceptance ramp. Every demand transient is unserved wheel work. R22c rules this a TOW; the numbers below are reported so the ruling is stated with its cost, not asserted.
* **`pack_derate`** — Cycle completable; the cost is fuel and genset duty.
* **`resistor_loss`** — Cycle completable on the flat. NOT descent-safe: on the 10 km 6% descent the friction brakes take the energy the resistor was specified to take. See descent_r2_r17 for the numbers and the WS7 tests.
* **`inverter_thermal`** — Derated limp in both directions; the retardation derate is the one that matters, because it lands in the friction column.
* **`sensor_loss`** — Derated limp. The honest cost is that the low-mu traction-control prior caps launch and regen well below the dry-road capability.

Worst unserved wheel work over the enumerated fault set: 25.237 kWh at `inverter_thermal`. Worst friction energy on the duty cycle: 1.702 kWh at `inverter_thermal`.

Table: `data/fault_matrix.csv`.

## 10. Heat to WS6, tests to WS7, traces per R34

### 10.1 Control-driven heat cases (WS6 ledger)

control-driven cases: these are the heat flows the SUPERVISOR's decisions create, on top of the component ratings WS2/WS3/WS4 already gave WS6. Cycle averages are over the run duration; extrema are 8-seed envelopes with the governing seed labelled. Engine split model consumed from WS4: WS4-DECLARED split of (fuel - shaft): exhaust 49% / coolant+oil 38% / CAC 10% / radiation 3%; radiator package = coolant+oil+CAC = 48%. Consumed from WS4 heat_ledger_ws6._split_model.

| case | engine rejection (kW avg) | radiator package (kW) | generator + rectifier (kW) | traction chain (kW) | pack I²R (kW) | resistor (kWh/cycle) | friction (kWh/cycle) |
|---|---|---|---|---|---|---|---|
| `volt_reg_nominal` | 74.19 | 35.61 | 2.481 | 4.248 | 0.348 | 0.000 | 0.615 |
| `volt_reg_cda_5.4` | 87.79 | 42.14 | 2.835 | 4.746 | 0.261 | 0.000 | 0.569 |
| `volt_reg_alt2000m_45C` | 63.13 | 30.30 | 2.123 | 3.805 | 0.293 | 0.000 | 0.666 |
| `volt_reg_cold_minus10C` | 77.21 | 37.06 | 2.598 | 4.248 | 0.854 | 0.000 | 0.615 |

**A change WS6 must read this block in light of.** WS4's KX round 3 WITHDREW its R20 radiator-survival verdict and raised the question as its ESC-12 rather than assert a capability-versus-ambient model it does not have. The WS4 interface therefore no longer carries a survival boolean. That is a WS6 matter, not WS5's - but it changes how WS6 should read the block below: these are the control-driven heat FLOWS the supervisor creates, they are INPUTS to the radiator-survival question, and nothing upstream now answers that question for WS6.

Two control-driven sizing cases WS6 does not get from anyone else:

* **Resistor sizing** — 10 km 6% descent, payload120/45C/85kmh/soc0.95 (crest, buffer nearly full)/resistor_healthy - the row that maximises resistor power over the enumerated descent grid: 46.9 kW peak, 4.50 kWh over 444 s, sink forced air (R15); WS6 packages the duct and the blower
* **Friction, resistor lost** — FAULT case: payload120/45C/25kmh/soc0.95 (crest, buffer nearly full)/resistor_lost with the R2 sink lost - the heat the service brakes must absorb when the only speed-independent retarder is gone: 8.10 kWh at 20.0 kW mean over 1460 s. Sink: service brakes and air. WS6/WS7 own the fade question.

Table: `data/heat_ledger_ws5_to_ws6.csv`.

### 10.2 WS7 test list

R22c ('the WS7 test plan carries it'), R2, R13, R16, E23 and the WS5-PROPOSED items this report raises. Each vector states what is measured, the acceptance the supervisor was designed against, and the WS5 number the test is checking.

**12 vectors** — 4 blocking, 5 high, 3 medium.

| id | priority | test | ruling | what WS5 predicts |
|---|---|---|---|---|
| `WS5-T1` | BLOCKING | Brake-resistor loss on a sustained 6% descent | R2 / R15 / R22c | three separate extrema over the enumerated descent grid, each with its own governing row - they are NOT the same run. Worst friction ENERGY 8.10 kWh at 20.0 kW mean (payload120/45C/25kmh/soc0.95 (crest, buffer nearly full)/resistor_lost); worst sustained friction POWER 40.9 kW mean carrying 6.07 kWh (payload120/45C/70kmh/soc0.95 (crest, buffer nearly full)/resistor_lost); worst instantaneous friction POWER 49.3 kW (payload120/45C/85kmh/soc0.95 (crest, buffer nearly full)/resistor_lost) |
| `WS5-T2` | HIGH | ISG engine-motoring as a retardation sink | R2 / WS4 motoring anchor [WS5-PROPOSED] | 15.3 kW at rated-continuous speed; 9.9 kW at WS4's 1,706 rpm anchor point |
| `WS5-T3` | BLOCKING | Genset load-acceptance ramp | R19 / R22b / ESC-9 | the supervisor assumes a 4 s raised ramp and 25 kW/s slew; the residual ESC-9 exposure (0.0000 kWh) is entirely inside this ramp |
| `WS5-T4` | BLOCKING | Pack dispatch envelope below SOC 40% of nameplate | ESC-9 / WS3 soc15_note / R8 as restated by R12 | WS5 dispatch limit at -10 C / SOC 0.25 usable = 102.9 kW bus vs 125 kW warm |
| `WS5-T5` | HIGH | Empty-truck regen adhesion, flat and on grade | E23 | mu required flat 0.362; on the 6% descent 0.375 (+3.5%) |
| `WS5-T6` | HIGH | 13.5 kN launch adhesion | E23 / R3 | mu required curb 0.654, GVW 0.294 |
| `WS5-T7` | HIGH | R16 cold dispatch and preconditioning | R16 | preconditioning energy up to 0.70 kWh per cycle; cold fuel penalty at -10 C +0.0% |
| `WS5-T8` | BLOCKING | Genset-loss and pack-loss limp, then tow | R22c | genset loss: first unserved sample at 0.0 - 259.4 s after injection; pack loss: unserved wheel energy up to 0.00 kWh |
| `WS5-T9` | MEDIUM | Inverter thermal derate law | R13 / WS2 inverter Tj export | WS5 uses a lumped Tj proxy calibrated on WS2's pair (6.15 K/kW above the LT inlet); peak Tj on the duty reaches 131 C at the 2,000 m / +45 C corner |
| `WS5-T10` | MEDIUM | Sustained true-coast recovery (R22d) | R22d | bus swing 0.74 kW mean, 0.124 kWh over 600 s |
| `WS5-T11` | MEDIUM | Two-point notch NVH | R22b | load_follow: 5353 set-point transitions/h and 1.1 starts/h at nominal (8-seed max) |
| `WS5-T12` | HIGH | V1 start count over a shift | R19 | 16.5-24.8 starts/shift (8-seed envelope; inside the ratified band: True) |

Full procedures and acceptance criteria: `results_ws5.json → ws7_test_vectors`; summary table `data/ws7_test_vectors.csv`.

### 10.3 R34 10 Hz traces

R34 (program hygiene, BASELINE_v5, carried by v6/v7): every pipeline exports a 10 Hz trace file per run. WS5 complies from this artifact with three: the recommended V2 dispatch, the V1 R19 dispatch, and the governing fault case.

| trace | rows | rate |
|---|---|---|
| `data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` | 66143 | 10 Hz |
| `data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` | 34852 | 10 Hz |
| `data/trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv` | 5344 | 10 Hz |

Every trace carries road speed, grade, wheel power, bus load, genset bus power, pack power, SOC, engine shaft power, fuel rate, the R15 cascade (resistor / heater / friction), cell and junction temperature, bus voltage, both WS5 dispatch limits, and the active state of all six state-machine regions. Figure: `figs/ws5_reference_trace.png`.

**TRACE_SCHEMA conformance, stated plainly.** TRACE_SCHEMA.md, lead-issued 2026-08-31, binding on every pipeline from its next artifact. It landed DURING this run (file mtime 07:54) and this artifact adopts it.

Conforms:

* filename pattern trace_<vehicle>_<duty>_<corner>_seed<N>_10Hz.csv
* mandatory '# key: value' header block, all fourteen fields, free-text notes after them
* all ten core columns
* all seven engine-carrying columns that exist in a pure-series architecture
* all electrified columns that exist and are modelled
* bus-side electrical quantities (R12)
* absent-not-zero-filled discipline for every quantity WS5 does not have or does not model
* every column traceable to a named pipeline variable (ws5_supervisor.TRACE_COLUMNS and the trace row that fills it)

Columns ABSENT by design — the schema's rule is that a missing physical quantity is an absent column, never a zero-filled one, because *an absent trace must not read as a measured zero*:

| column | why it is absent |
|---|---|
| `gear` | no transmission (pure series) |
| `lockup` | no lockup device (BASELINE_v3 deleted it) |
| `motor_disconnect` | the architecture has none |
| `P_comp_brake_kW` | a pure-series engine is not coupled to the road and cannot compression-brake |
| `T_motor_C` | WS5 does not model motor winding temperature; WS2 owns the machine's thermal model |

TRACE_SCHEMA's engine_state 3 is 'overrun'. A pure-series engine is never driven by the road, so that state cannot occur and the column never takes the value 3. That is a property of the architecture, not a gap in the trace.

**Where WS5 does NOT conform, and it is a coverage gap, not a format one.** The schema asks for one trace per (vehicle, duty, corner, seed) - ALL 8 seeds per case, all corners. WS5 exports THREE traces, not the full grid. V2 x VOLT-REG x 4 corners x 8 seeds = 32, plus V1 x VOLT-SUB x 8 seeds = 8, i.e. 40 duty traces. Measured on this run's own files, the full grid would be **510 MB** of trace data (14438858 bytes per VOLT-REG trace, 6016991 per VOLT-SUB trace). BASELINE_v7's R51 freezes the research track and orders anything mid-flight to complete its CURRENT step only. Generating the full grid is a new step, not this one, and its artifact size is stated below so the lead can price it rather than guess. Escalated as ESC-WS5-8.

## 11. Interfaces (machine-readable)

The authoritative block is `results_ws5.json → interface_ws5`. It mirrors WS1/WS4 conventions; every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline (R14). What follows is a rendering of it — the JSON is the record.

```json
{
  "supervisor": {
    "loop_rate_Hz": 10.0,
    "chopper_command_rate_Hz": 100.0,
    "causality": "strictly causal; no preview or route lookahead",
    "state_machine": {"regions": 6, "n_states": 35, "n_transitions": 34, "spec": "data/state_machine.csv"}
  },
  "dispatch_v2_r22b": {
    "recommended": "load_follow",
    "hysteresis_band_kWh": 3.5,
    "pinned_point_kW_bus": 80.6139,
    "notch_hi_kW_bus": 125.9180,
    "fuel_energy_kWh_per_km": {
      "rule": "max over the enumerated R22b case set (R14)",
      "worst_case_value": 2.035948,
      "governing_case": "cda_5.4",
      "nominal_ensemble_min": 1.706580,
      "nominal_ensemble_median": 1.716980,
      "nominal_ensemble_max": 1.722558
    },
    "genset_starts_per_h": {"worst_case_value": 1.0959, "governing_case": "nominal"},
    "setpoint_transitions_per_h": {"worst_case_value": 5950.84, "governing_case": "cda_5.4"},
    "unserved_bus_energy_kWh": {"worst_case_value": 0.000000, "governing_case": "nominal"}
  },
  "dispatch_v1_r19": {
    "fixed_point_bus_kW": 35.0,
    "band_kWh": 3.0,
    "starts_per_8h_shift": {"min": 16.4524, "max": 24.7841, "r19_ratified_band": [16.0, 25.0], "inside_ratified_band": true}
  },
  "blend_order_r15": {
    "order": ["regen-to-pack", "pack heater (R16 band only)", "brake resistor (forced air, R2)", "friction"],
    "heater_kW": 8.0,
    "resistor_ohm": 3.73250,
    "resistor_kW_guaranteed_any_bus_voltage": 50.0,
    "resistor_blower_bus_load_kW": 1.45,
    "friction_energy_kWh_per_cycle": {"worst_case_value": 0.6665, "governing_case": "alt2000m_45C"}
  },
  "traction_control_e23": {
    "required_day_one": true,
    "mu_required_empty_regen_stop": 0.361703,
    "mu_required_empty_regen_stop_6pct_descent": 0.374518,
    "mu_required_launch_13.5kN_curb": 0.654170,
    "mu_required_launch_13.5kN_gvw": 0.293848,
    "descent_adhesion_penalty_pct": 3.5429,
    "low_mu_fallback_prior": 0.30
  },
  "dispatch_limit_esc9": {
    "anticipatory_state": "D_RESERVE",
    "reserve_margin_kW": 8.0,
    "worst_unserved_bus_kWh": {"value": 0.000000, "governing_case": "nominal"},
    "worst_unserved_bus_kWh_without_reserve": {"value": 0.000000, "governing_case": "nominal"}
  },
  "heat_worst_cases_to_ws6": {
    "engine_rejection_avg_kW": {"value": 87.7860, "governing_case": "volt_reg_cda_5.4"},
    "brake_resistor_peak_kW": {"value": 46.9189, "governing_case": "descent_resistor_sizing"},
    "friction_brake_kWh": {"value": 8.1016, "governing_case": "descent_resistor_lost"}
  },
  "test_vectors_to_ws7": 12, "trace_files_r34": 3
}
```

## 12. Escalations

Each cites the ruling it challenges. **None is self-resolved.** WS5's adjudication round was cut by BASELINE_v7's freeze, so these go to the lead unreviewed; §14 adds WS5's own list of what is weak in its work.

### ESC-WS5-1 — R5 versus the assignment's cross-cycle closure

**Ruling challenged: R5 (BASELINE_v1, carried through v5).** The assignment's Deliverables line orders a "supervisor simulation closed over VOLT-SUB and VOLT-REG for both variants". R5 states that V1 is formally a sub-80 km/h vehicle, "shall not be dispatched on regional/highway work, and VOLT-REG is not a V1 cycle." Three of the four combinations are clean; the fourth is barred by ruling. WS5 ran it as an explicitly labelled out-of-envelope capability probe (§5) and drew no design conclusion from it. **Ask:** confirm that reading, or lift R5's exclusion for the purposes of WS5's closure. WS5 does not resolve this itself.

### ESC-WS5-2 — no ruled friction-brake continuous rating to test resistor loss against

**Ruling challenged: R2 / R17.** R2 adopted the dynamic-brake resistor because "a dissipative sink is speed-independent — it works below 34.9 km/h where nothing else in the architecture does", and R17 made 50 kW continuous a *capability* requirement over the full descent. WS5 can compute exactly what lands on the service brakes when that sink is lost — up to 8.10 kWh over 1460 s on the worst-energy row, and 40.9 kW sustained for 534 s on the worst-power row, when the truck crests with a nearly-full buffer (two different rows of the grid, §7) — but the program has **no ruled friction-brake continuous rating**, so the fault has a number and no verdict. WS5 will not manufacture one: asserting the brakes cope would be as unfounded as asserting they do not. **Ask:** rule a friction-brake continuous capability, or assign it to WS6/WS7, so WS5-T1 has a pass/fail rather than a measurement. This is the one place in WS5 where the analysis stops at a number because the program has not given it a bar, and it is the case the assignment singled out.

### ESC-WS5-3 — a second speed-independent retarder at no hardware cost [WS5-PROPOSED]

**Ruling engaged: R2.** R2 named the resistor as the answer of record and the exhaust brake as "optional secondary, not the answer". WS5 proposes a third thing R2 did not consider, which needs no new hardware: motor the engine through the crank-mounted ISG, fuel off, against its own friction and pumping work — 15.3 kW of speed-independent electrical sink at rated-continuous speed. The model is WS4's own: it reproduces their declared motoring anchor (10.68 kW modelled against 10.7 kW declared at 1,706 rpm). The ISG already exists for R19 starting. **Ask:** WS4 sign-off on continuous motoring (engine oiling, generator and rectifier thermal) and a WS7 slot. **Until then WS5 does not count it: the fault matrix's capability of record is the without-ISG column.**

### ESC-WS5-4 — WS4's ESC-8(b), as restated by KX round 3, lands in the WS5 blend order

**KX round 3 restated this escalation against WS5 by name.** Its statement is that the pack reading is violated at every tabulated cell temperature, on every seed of every ordered case, and that — in its words — no cell-temperature limit can rescue the dispatch of record if the lead rules for the pack reading; only a supervisor change or a restated interface rating can. The supervisor is mine, so I answer for it, and §8.4 carries the measurement on WS5's own runs rather than a restatement of WS4's.

**What the measurement in §8.4 actually shows, and it is not what I expected.** The R15 cascade caps regen-to-pack at WS3's acceptance curve at the measured cell temperature, and on WS5's runs the regen path never approaches it — it peaks at 69.0 kW against an acceptance of 130.8 kW at nominal. The crossing §8.4 finds is a **different mechanism**: it is GENSET SURPLUS charge, which the R15 cascade does not touch and which only the ESC-9 envelope gates. It appears in one of the four enumerated cases — `cold_minus10C`, where the acceptance curve is at its lowest — for 74.5 s carrying 0.2428 kWh over the cycle. So the blend order is NOT what absorbs this crossing, and I will not claim it is.

**What WS5 could do about it, and what it cannot.** If the lead rules for the pack reading, the supervisor's remedy is to gate genset surplus charge on the regen-acceptance curve as well as on the ESC-9 envelope — a one-line change to the charge cap, whose cost is fuel (the surplus has to be burned later instead of banked) and, on descents, extra resistor duty into WS6's ledger. WS5 will implement and price it on instruction. **What the supervisor cannot do** is change the pack's rating, or choose between the pack reading and the cell reading. Both of those are rulings, and both are the lead's.

**ESC-8(a), the original half, still stands — ruling challenged: R16.** WS4's ESC-8 also asks for a ruled maximum cell temperature for dispatch at full regen, noting that a hot-corner descent on a pack at its loop's design ceiling would push regen into WS5's resistor and friction columns. The blend order is indeed ours, and it already does the right thing by construction: regen above WS3's published acceptance at the *measured* cell temperature spills down the R15 cascade, and the cost is exported per case. But the acceptance curve collapses from 129.1 kW at +45 °C to 62.2 kW at WS3's 55 °C continuous ceiling and to zero at 60 °C. **WS5 implements the curve as ruled and can price any ceiling; it cannot rule one.** **Ask:** rule whether dispatch at full regen is permitted with cells at the loop's 55 °C design ceiling. If it is, the descent's resistor duty rises and WS6's ledger moves with it. That question is about a CEILING; the r3 restatement below is about which READING governs. They are separate asks and WS5 needs both answered.

**Ask, restated for the r3 wording — ESC-8(b).** Rule which reading governs. If the pack reading governs, say whether the remedy is to be a supervisor change (tighten the WS5 charge cap below R8's 110 kW, at a fuel and resistor-duty cost WS5 will price on request) or a restated interface rating. WS5 will implement either and will not choose between them.

### ESC-WS5-5 — the ESC-9 envelope is a supervisor fix for a sizing statement

**Rulings engaged: R8 as restated by R12/ES-4, and WS4's ESC-9.** WS3 declares that full power below SOC 40% of nameplate is not guaranteed and names it a WS5 dispatch limit; WS4 reports the delivered pack discharging to 192.5 kW against R8's 125 kW and charging to 147.6 kW against 110 kW. WS5 has accepted the assignment, enforced the envelope, and reduced the resulting unserved energy by 100.0% against WS4's bracket, to 0.0000 kWh. Two things the lead should see plainly. (i) The residual is entirely inside the genset's declared 4 s load-acceptance ramp; if the real ramp is slower, it grows, which is why WS5-T3 is blocking. (ii) The **charge** side is not free: capping regen at 110 kW bus pushes energy down the R15 cascade into the resistor, and therefore into WS6's heat ledger, rather than into the pack. **Ask:** confirm that the envelope WS5 enforces (R8's 125/110 kW bus-side against WS3's (T, SOC) capability map, whichever is tighter) is the envelope of record, and note that a supervisor limit is not the same thing as a pack that meets R8.

### ESC-WS5-6 — ESC-10's option (b) would constrain WS5, and costs the recommended dispatch nothing

**Ruling engaged: R18 / ESC-1, via WS4's ESC-10 as restated by KX round 3.** ESC-10's second disposition option is to make the genset's continuous flat-rating a WS5 constraint. That is a constraint on this workstream, so WS5 states its price rather than waiting to be told. §8.5 has the measurement: WS5's set-point generator already caps every commanded point at the derated continuous rating in every dispatch state except the emergency SOC band, and the recommended dispatch **never enters that band** on any seed of any enumerated case (0.0 s). **Ask:** none, beyond noting that if the lead takes option (b), the recommended R22b dispatch satisfies it at zero cost and the pinned-point candidate does not. WS5 does not choose the disposition.

### ESC-WS5-7 — the cold fuel penalty is understated by the ratified accounting convention

**Ruling challenged: R12 / WS1's ratified flat 0.97 buffer convention.** WS5 carries that convention so its energy books are identical to WS4's and the two are comparable — which is the right call for comparability and the wrong one for cold. The convention is temperature-blind: a cold pack's higher internal resistance costs nothing in the fuel column. §8.1 shows the consequence and the size of it — the measured pack I²R heat rises from 0.636 kWh per cycle at +25 °C to 1.970 kWh at −20 °C, tracking WS3's own resistance multipliers — while the fuel column shows a temperature term of essentially zero. **Direction of error: WS5's cold fuel numbers are optimistic.** **Ask:** either confirm the flat convention for Vehicle Zero and accept that cold is priced only through preconditioning and accessories, or rule that the buffer round trip is to be taken from WS3's temperature-dependent model — in which case WS4's ratified numbers move too, and the two workstreams should move together. WS5 will not change the convention unilaterally, because doing so would break the concordance that makes its numbers checkable against WS4's.

### ESC-WS5-8 — the lead's TRACE_SCHEMA landed mid-run; WS5 conforms on format and does NOT conform on coverage

**Document engaged: `TRACE_SCHEMA.md`, lead-issued 2026-08-31, binding on every pipeline from its next artifact (R34).** It was issued while `run_ws5.py` was executing. WS5 adopted it for this artifact: filenames, the full mandatory header block, and the schema's own column names and absent-not-zero-filled discipline (§10.3). WS5 does **not** meet its COVERAGE clause — one trace per (vehicle, duty, corner, seed), all eight seeds, all corners. That is 40 duty traces and, measured on this run's own files, about 510 MB. Generating it is a new step, and BASELINE_v7's R51 orders mid-flight work to complete its current step only. **Ask:** if WS12 needs the full ribbon, instruct it and WS5 will generate the grid — the pipeline already produces every trace on demand and the only cost is runtime and repository size, both stated above. If it does not, record that WS5's three traces are format-conformant and coverage-partial, so the exhibit is not surprised by it later. **Direction of risk:** the exhibit consumes ONLY conforming files, so an unstated coverage gap would surface as WS5 being silently unusable rather than as a known limitation.

### ESC-WS5-9 — R42 kills the vehicle §4's dispatch trade is about [provenance observation]

**Ruling engaged: BASELINE_v6 R42, ratified during this run.** R42 kills V2 Trucker on the Vehicle Zero ruler criterion. §4 recommends a genset dispatch for exactly that variant on exactly that duty. WS5 does not relitigate R42 and draws no conclusion from it. What WS5 asks is narrow: **record whether §4 remains a live design result** — it is a property of the series architecture and of R22b, which the program has not withdrawn, and it is the thing WS6 and WS7 would build and test against — **or whether it should be marked FROZEN-SUPERSEDED along with the vehicle.** WS5 believes the former and will not decide it. §5's V1 result attaches to the variant R43 advanced and is unaffected either way.

## 13. First-principles sanity checks

Every check below is executed in `run_ws5.py` as an assertion, not merely reported; the pipeline fails loudly if any of them breaks.

| check | result |
|---|---|
| WS5's fast pack solver vs WS3's own `Pack.solve_current`, over 140 (power, SOC, temperature) points | max abs error 0.0e+00 |
| WS5's adhesion law vs WS2's exported `traction.envelope` (6 rows, both directions) | max abs error 1.82e-12 N |
| WS5's μ inversion vs WS2's exported `traction.mu_required` | max abs error 0.0e+00 |
| WS5's adhesion power curve vs WS2's exported `WS2 data/regen_adhesion_curves.csv`, 54 points | max abs error 0.0491 kW — WS2 prints this file to one decimal, so 0.05 kW is the rounding floor; the agreement is at that floor across all six cases and nine speeds |
| ISG motoring model vs WS4's declared 10.7 kW @ 1,706 rpm anchor | 10.68 kW modelled, error 0.025 kW |
| resistor V²/R at the R10 window floor vs WS2's exported `P_cont_kW_any_bus_V` | 50.0 kW |
| R16 curve interpolation vs WS4's declared acceptance values at its three case cell temperatures | True |
| state-machine structure (unique initial states, no dangling targets, no unreachable states, unique priorities) | True |
| no clutch / lockup / sync / mode state anywhere in the machine | `_has_clutch_state = False` |
| road load at 85 km/h, GVW, flat (WS1's baseline sentence: ~2.0 kN / ~47 kW) | 1988 N / 46.9 kW |
| WS5 in concordance configuration vs WS4's ratified `series_duty_v2`, 24 runs × 8 fields | 0.0e+00 — **EXACT** |

Two arithmetic checks a reader can do by hand:

* **The V1 start count.** VOLT-SUB's genset-average demand is ~10 kW bus. At the 35 kW fixed point the net charge rate is ~25 kW, so a 3.0 kWh band gives an on-time of 3.0/25 ≈ 0.12 h and an off-time of 3.0/10 ≈ 0.30 h — a period of ~0.42 h, i.e. ~2.4 starts/h, ~19 per 8 h shift. The simulation returns 16.5–24.8. R19's ratified 16–25 is arithmetic, and it holds.
* **The descent energy.** A 10 km 6% descent at 7,180 kg releases m·g·h = 7180 × 9.81 × 600 = 42.3 MJ ≈ 11.7 kWh of potential energy, of which road load takes roughly 2 kWh and the chain another tenth. The pack holds 11.08 kWh usable, so entering at WS3's 0.55 target it has about 5 kWh of headroom — enough to swallow most of ONE descent, which is why the 0.55-entry rows look benign. Enter with the buffer nearly full and there is no headroom at all: the surplus has to go somewhere, which is precisely why R2 exists, and removing the resistor puts 8.10 kWh onto the service brakes. Any analysis that only ran the mid-SOC entry would have missed it.

## 14. What WS5 believes is weak in its own work

**This workstream's adjudication round was cut by the research freeze (BASELINE_v7). Nothing below this line has been adversarially reviewed.** That is a reason to be more explicit, not less, so the following is WS5's own list of where it would look first if it were the adjudicator. Each is a limitation of this artifact, stated by its author, and none of them is hidden elsewhere in the document.

1. **The inverter junction model is a two-point calibration, and it decides a headline number.** The Tj proxy (§8.0) is anchored on the single pair WS2 exports. It is what sheds the unserved WHEEL work that killed DR2 for every strategy (§4.2) and it produces the worst entry in the fault matrix (`inverter_thermal`, 25.24 kWh). If the real derate onset is higher, that term shrinks and DR2 may well pass. WS5 declared the model, exported it, and made it WS5-T9 — but a reader should treat every unserved-wheel number as resting on it.
2. **DR2 was revised once, after it eliminated every candidate.** §4.2 discloses this in full and exports both readings, and the winner is the same under every reading. It remains the one place where a decision rule moved after the numbers were seen, and an adjudicator would be right to test it first.
3. **The ISG motoring retarder is WS5's own proposal, not a ruled capability.** §7.1 anchors it on WS4's own FMEP coefficients and reproduces their declared anchor, but it applies the sink instantly while a stopped engine would first have to be spun up. It is excluded from the fault capability of record for exactly that reason. If anyone quotes the with-ISG column as capability, that is a misreading WS5 invited by publishing it.
4. **The cold fuel penalty is understated and WS5 knows by roughly how much but not exactly.** ESC-WS5-7 states the direction and the size of the omission. The number that would replace it depends on a convention the lead has not ruled.
5. **The NVH threshold is a WS5 invention.** The 5 kW/s "NVH event" is a declared diagnostic, deliberately excluded from the decision rule, and there is no measurement behind it. The set-point transition counts that look alarming for load-following (§4.3) are counts, not human judgements, and WS5-T11 is the only thing that can settle them.
6. **Three traces, not the schema's forty.** ESC-WS5-8. Format-conformant, coverage-partial, stated rather than quietly omitted.
7. **The V1 x VOLT-REG probe is barred by R5 and was run anyway, as a probe.** ESC-WS5-1. It draws no design conclusion, but it is in the artifact and could be misquoted.
8. **Everything upstream is model-relative.** BASELINE_v6's R44 records that the ruler is uncalibrated and that no external efficiency claim may be made before WS7 measures a stock vehicle. WS5 claims no efficiency advantage anywhere, but its fuel numbers inherit every modelling assumption in WS1-WS4 and add its own.

---

*Generated by `make_report_ws5.py` from `results_ws5.json`. No number in this report was transcribed by hand; `verify_ws5.py` re-reads the rendered file and asserts every one of them against the results file verbatim. `check_determinism_ws5.py` asserts byte-stable regeneration.*
