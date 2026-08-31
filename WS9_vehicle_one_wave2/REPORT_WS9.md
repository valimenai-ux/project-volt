# REPORT WS9 - VEHICLE ONE, WAVE TWO: THE TWO WALLS AND THE COLD WALL

Workstream WS9, Vehicle One. Executes `WS9_vehicle_one_wave2/ASSIGNMENT.md` against `BASELINE_v4.md`.

**Nothing here is ratified.** The lead ratifies (CLAUDE.md rule 11). This report states what the physics gave and what it cost; the execute-or-spare decision is the lead's.

**This report is generated**, not written: every number below is formatted out of `results_ws9.json` by `make_report_ws9.py`, and `verify_ws9.py` asserts independently that each rendered figure appears verbatim and that the interface block equals `results_ws9.json['interface_ws9']` (rule 2).

| | |
|---|---|
| Entry point | `run_ws9.py` (fixed seeds 8101..8108, 8 seeds) |
| Baseline of record | BASELINE_v4.md |
| Python / numpy | 3.14.3 / 2.5.2 |
| Metric of record | **primary energy per PAYLOAD tonne-km** [MJ/(t.km)] |
| Design duty (R29) | **GH-REG-165** - gates the verdicts |
| Control duty (R29) | LH-520 - reported alongside, never gates |
| Inherited WS8 code round | `r2` (SHA-pinned in section 12) |

---

## 0. What this trial found

**S4p, S5-13L, S6, S7 ADVANCE. S5 KILL.**

Four things decided this trial, and three of them are not fuel numbers.

1. **Naming the duty changed the answer, exactly as R29 said it would.** The design duty is a grade-heavy regional corridor - 10.6 m of climb per kilometre against the control duty's 7.1, and 20.6% of its distance at 2% or steeper against 11.9%. Every candidate's margin moves, and for some of them it changes sign between the two duties. A fleet average would have hidden all of it, which is why the assignment forbids one.

2. **The zero-mass stack is the cleanest result in the report, and it rests on one cited number.** S6 is mass-neutral with the ruler TO THE KILOGRAM - same gearbox, same retarder, same axles, same aftertreatment - so on a metric that divides by payload its margin IS its fuel margin, with no payload term at all. It clears the bar on both duties. The whole of that margin comes from a peak brake thermal efficiency of 0.492 taken from a manufacturer's demonstration document, against the incumbent's 0.4547. The break-even peak BTE at which S6 exactly clears the +3% criterion is **0.4688** - so the claim has 2.32 points of headroom, and the lead can see exactly how much of it has to be true (ESC-WS9-1).

3. **The two walls are not the whole story: a 2-speed dog box meets a THIRD constraint, and the design duty is what exposes it.** Two ratios do span 105 km/h cruise under the rpm ceiling and the assignment's 6% grade - S5 clears both walls BY CONSTRUCTION, in closed form. But the low gear's coupling floor sits above the crawl speed a steeper grade forces, and below that floor the dogs are open and the engine is not connected at all. The steepest grade a CONTIGUOUS 2-speed can carry is 6% on the 11 L and 8% on the 13 L - and the design duty carries grades to 10.7%. The assignment's 6% wall sits almost exactly on the frontier of what two ratios can do, which is why S5 clears it and fails one point above it.

4. **Mass is still payload, and it still decides everything else.** Every electrified candidate here is more efficient per kilometre than the ruler and every one of them is heavier. The payload each gives up is in section 4.3, to the kilogram. Of the candidates that advance on the design duty, only S6 also clears the ruler on the CONTROL duty - and it is the one that adds no mass at all. Every other advance is a bet on the operator's duty being the design duty.

| candidate | payload | vs ruler | GH-REG-165 margin (min / median) | LH-520 margin (min / median) | verdict |
|---|---|---|---|---|---|
| **S0R** | 20,655 kg | - | - (ruler) | - (ruler) | **RULER** |
| **S5** | 19,970 kg | -685 kg | +1.90% / +4.64% | -5.75% / -3.49% | **KILL** |
| **S5-13L** | 19,706 kg | -949 kg | +5.36% / +7.07% | -1.38% / -0.66% | **ADVANCE** |
| **S6** | 20,655 kg | +0 kg | +7.50% / +7.61% | +7.26% / +7.39% | **ADVANCE** |
| **S7** | 19,846 kg | -809 kg | +4.51% / +5.90% | -1.45% / -0.21% | **ADVANCE** |
| **S4p** | 20,134 kg | -521 kg | +11.95% / +15.83% | -6.81% / -2.75% | **ADVANCE** |

Margins are computed **per seed against the ruler on the same seed and the same duty**, then enveloped. The seed sets the corridor, the wind and the driver, so pairing removes the cycle draw from the comparison instead of leaving it in the variance.

---

## 1. The design duty (R29), defined

R29: *"Vehicle One is specified for GRADE-HEAVY REGIONAL duty, with the flat line-haul corridor retained as a control on which the incumbent is CONCEDED near-optimal."*

**GH-REG-165** - DESIGN DUTY (R29) - the duty Vehicle One is specified for

- built by `ws8_cycles.build_regional(seed, grade_heavy=True)`
- WS8's REG-165 regional mixed urban/rural/highway cycle, built with the grade-heavy terrain construction - i.e. the REGIONAL leg of WS8's own grade-heavy corner, taken verbatim
- ADVANCE/KILL is read on THIS duty

**LH-520** - CONTROL DUTY (R29) - the duty on which the incumbent is CONCEDED near-optimal

- built by `ws8_cycles.build_linehaul(seed, grade_heavy=<corner>)`
- WS8's LH-520 line-haul corridor, taken verbatim. R29 calls it 'flat' BY CONTRAST with the grade-heavy design duty; it is not a flat road - it carries the assignment-ordered 6% mountain and about 3,704 m of climb over 520 km - and R29's own supporting figures (0.72 of moving time in top gear, 196.8 g/kWh duty-averaged) are WS8's LH-520-as-ordered numbers. A genuinely grade-zeroed LH-520 appears in exactly one place in WS9: the F7 calibration cross-check of the ruler, where WS8 also used it.
- reported alongside, NEVER gating

| | GH-REG-165 (design) | LH-520 (control) |
|---|---|---|
| distance, median [km] | 165 | 520 |
| total climb, median [m] | 1748 | 3704 |
| climb per km, median [m/km] | 10.60 | 7.12 |
| max grade, worst seed | 0.1074 | 0.0605 |
| min grade, worst seed | -0.1024 | -0.0605 |
| net elevation change, worst seed [m] | 0.0984 | 0.0417 |
| distance at >=2% grade, median | 0.2061 | 0.1186 |
| distance at >=5% grade, median | 0.0402 | 0.0336 |
| mean corridor demand speed, median [km/h] | 79.0 | 91.6 |

**There is no fleet blend anywhere in this report.** WS8 reported a 70/30 fleet mission; the assignment forbids one here, because R29's whole finding is that the sign of a margin flips between duties and a fleet average hides it (D15).

The design duty is grade-heavy by construction, so R28's `grade_heavy` corner is a **null operation** on it. WS9 runs that corner anyway and asserts the identity (`sanity.design_duty_null_at_grade_heavy_corner`: identical = `True`), which turns a redundancy into a free consistency check on the whole corner machinery. The consequence - that the design duty is gated on four corners rather than five - is escalated as ESC-WS9-3.

---

## 2. The ruler, restated (ESC-6)

ESC-6, ruled in R27: *"S0 gains a hydraulic retarder in WS9 with its mass charged - the ruler gets the equipment the duty demands."* A grade-heavy regional design duty is exactly the duty a retarder is bought for.

| | |
|---|---|
| engine | WS8-CONSTRUCTED Willans, 13 L class |
| peak power | 352.0 kW |
| island BSFC | 185.0 g/kWh |
| retarder | max 3250 Nm at the propshaft, 350 kW continuous |
| retarder mass CHARGED | **130 kg** (105 kg installation weight including oil, cited, + 25 kg of cooling package, declared) |
| retarding force at 90 / 50 km/h | 14000 N / 11878 N |
| ruler payload | **20,655 kg** |

The retarder moves the answer BOTH ways and only the simulation can say which wins: the ruler loses 130 kg of payload and gains its descent speed back. Its torque characteristic is the manufacturer's, read verbatim from a primary OEM fact sheet (section 12).

### 2.1 Calibration cross-check, as an ENSEMBLE (finding F7)

WS8's adjudication finding F7 (material, rule 4): the report's only external anchor was asserted on a MEDIAN while its own 8-seed envelope spanned the entire reference band, and the comparison was not mass-matched. WS9's ruler is a different vehicle - it carries the retarder - so the cross-check is re-run, and it is rendered as an envelope.

| | L/100 km |
|---|---|
| **S0R, LH-520 with grade zeroed - ensemble min** | **29.82** |
| **S0R, same - ensemble median** | **33.08** |
| **S0R, same - ensemble max** | **39.36** |
| same, mass-matched to the reference payload (19.3 t) - median | 32.62 |
| ICCT / TUV NORD, typical EU tractor-trailer | 32.6 |
| ICCT / TUV NORD, at that cycle's regulatory payload | 33.1 |
| ICCT / TUV NORD, best-in-class EU | 29.9 |

Median residual against the typical figure: +1.48%. Mass-matched residual against the regulatory-payload figure: -1.44%. The 8-seed envelope is WIDER than the published band it is being compared against (29.9-33.1), and that is stated here rather than left out - which is precisely what F7 asked for. No claim of agreement is made beyond what the envelope supports.

---

## 3. The two walls, addressed by construction - and the third

- **WALL 1** - a single fixed engine ratio cannot span 105 km/h cruise under the 2,100 rpm ceiling AND the 6% grade at 36,300 kg (R25, D8)
- **WALL 2** - at fixed GCW every powertrain kilogram displaces payload 1:1, so the objective function is efficiency per added kilogram (D8)

### 3.1 Wall 1, in closed form

WS8's adjudication finding F12: WS8 reported the single-ratio ceiling as 3.60 because that was the largest entry in a swept grid. A bound that is a property of somebody's grid resolution is not a bound. WS9 solves each wall algebraically and keeps the sweep as the illustration.

Ratio ceiling at 105 km/h under the 2,100 rpm limit, closed form: **3.7699**.

| engine | ratio required for 6% | span needed vs the ceiling | force available at the ceiling | force required | single ratio feasible |
|---|---|---|---|---|---|
| ENG-11L | 7.209 | 1.912 | 12.4 kN | 23.8 kN | **False** |
| ENG-13L | 5.468 | 1.450 | 16.4 kN | 23.8 kN | **False** |

### 3.2 Two ratios, solved

Three constraints, all physical, none of them a preference: Wall 1 caps the HIGH ratio, Wall 2 floors the LOW ratio, and CONTIGUITY caps the step between them - at the shift speed the low gear must be at or under its over-speed ceiling exactly when the high gear is at or above its lugging floor, or there is a band of road speed in which the engine has no gear at all.

| engine | R high | R low | span used (bound) | cruise rpm at 100 km/h | shift speed | coupling floor | holds 6% | band contiguous |
|---|---|---|---|---|---|---|---|---|
| ENG-11L | 3.608 | 7.425 | 2.058 (2.100) | 1914 | 52.2 km/h | 25.4 km/h | **True** | True |
| ENG-13L | 2.737 | 5.632 | 2.058 (2.100) | 1452 | 68.9 km/h | 33.5 km/h | **True** | True |

**A law falls out of that algebra, and it inverts the usual instinct.** with contiguity tight and Wall 2 tight, cruise engine speed x engine peak torque is a CONSTANT at fixed GCW and grade requirement: n_cruise = v * k * F_6% * (1+margin) * r_dyn / (T_peak * eta_low * span)

a minimal transmission wants a BIG-TORQUE engine: torque is what buys back the ratio span, so downsizing the engine of a 2-speed truck raises its cruise engine speed in exact proportion. That inverts the usual downsizing instinct and is why S5 is run on two engines.

### 3.3 The third constraint, which the design duty exposes

a 2-speed dog box clears the specified 6% grade by construction and then meets a THIRD constraint on the design duty: the low gear's coupling floor sits above the crawl speed a grade steeper than about 6-7% forces, and below that floor the engine is not connected at all

**ENG-11L** - coupling floor 25.4 km/h, machine sustained contribution 24.5 kW

| grade | engine holds it at | reachable above the coupling floor | machine alone sustains to | holds on either |
|---|---|---|---|---|
| 3% | 53.3 km/h | **True** | 6.3 km/h | **True** |
| 4% | 49.7 km/h | **True** | 4.9 km/h | **True** |
| 5% | 43.6 km/h | **True** | 4.0 km/h | **True** |
| 6% | 37.2 km/h | **True** | 0.0 km/h | **True** |
| 7% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 8% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 9% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 10% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 11% | 0.0 km/h | **False** | 0.0 km/h | **False** |

**ENG-13L** - coupling floor 33.5 km/h, machine sustained contribution 31.7 kW

| grade | engine holds it at | reachable above the coupling floor | machine alone sustains to | holds on either |
|---|---|---|---|---|
| 3% | 70.3 km/h | **True** | 8.1 km/h | **True** |
| 4% | 64.2 km/h | **True** | 6.3 km/h | **True** |
| 5% | 56.4 km/h | **True** | 5.2 km/h | **True** |
| 6% | 48.3 km/h | **True** | 4.4 km/h | **True** |
| 7% | 0.0 km/h | **False** | 3.8 km/h | **True** |
| 8% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 9% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 10% | 0.0 km/h | **False** | 0.0 km/h | **False** |
| 11% | 0.0 km/h | **False** | 0.0 km/h | **False** |

### 3.4 The frontier: the steep grade OR a contiguous band

a 2-speed dog box may have the steep grade OR a contiguous engine band. The assignment's 6% wall sits almost exactly on the frontier, which is why S5 clears it by construction and fails one point above it.

**ENG-11L** - steepest CONTIGUOUS grade: **6%**

| grade | R low required | span needed | contiguous | cruise rpm at 100 km/h if contiguous | gap left if not |
|---|---|---|---|---|---|
| 6% | 7.425 | 1.970 | **True** | 1914 | - |
| 7% | 8.529 | 2.262 | **False** | - | 46.4-50.0 km/h (3.6 wide) |
| 8% | 9.630 | 2.554 | **False** | - | 41.1-50.0 km/h (8.9 wide) |
| 9% | 10.729 | 2.846 | **False** | - | 36.9-50.0 km/h (13.1 wide) |
| 10% | 11.824 | 3.137 | **False** | - | 33.5-50.0 km/h (16.5 wide) |
| 11% | 12.917 | 3.426 | **False** | - | 30.6-50.0 km/h (19.4 wide) |

**ENG-13L** - steepest CONTIGUOUS grade: **8%**

| grade | R low required | span needed | contiguous | cruise rpm at 100 km/h if contiguous | gap left if not |
|---|---|---|---|---|---|
| 6% | 5.632 | 1.494 | **True** | 1452 | - |
| 7% | 6.469 | 1.716 | **True** | 1668 | - |
| 8% | 7.305 | 1.938 | **True** | 1883 | - |
| 9% | 8.138 | 2.159 | **False** | - | 48.6-50.0 km/h (1.4 wide) |
| 10% | 8.969 | 2.379 | **False** | - | 44.1-50.0 km/h (5.9 wide) |
| 11% | 9.798 | 2.599 | **False** | - | 40.4-50.0 km/h (9.6 wide) |

---

## 4. Candidate results - the headline, per duty class

All at **36,300 kg GCW**. Because GCW is fixed, the road-load physics is identical for every candidate: mass does not change how the truck drives, it changes what the truck may carry.

### 4.1 GH-REG-165 - THE DESIGN DUTY (gates)

| | architecture | payload | L/100 km | grid kWh | MJ_primary/payload-tkm (min / median / max) | margin vs ruler (min / median) | correction share (min..max) | verdict |
|---|---|---|---|---|---|---|---|---|
| **S0R** | Conventional 13 L diesel + 12-speed AMT with a direct top gear, + hydraulic retarder (ESC-6) | 20,655 kg | 44.83 | 0.0 | 0.9011 / 0.9196 / 1.0218 | - (ruler) | 0.0..0.0% | **RULER** |
| **S5** | Minimal transmission - 2-speed dog box, motor-synchronised shifts, torque-fill through the shift | 19,970 kg | 41.77 | 0.0 | 0.8597 / 0.8863 / 0.9746 | +1.90% / +4.64% | -0.2..18.9% | **KILL** |
| **S5-13L** | Minimal transmission with the 13 L engine - the other end of the ratio law | 19,706 kg | 39.73 | 0.0 | 0.8400 / 0.8544 / 0.9489 | +5.36% / +7.07% | -0.7..15.7% | **ADVANCE** |
| **S6** | Zero-mass stack - opposed-piston-class engine + predictive energy management, mechanical drive as S0 | 20,655 kg | 41.46 | 0.0 | 0.8328 / 0.8506 / 0.9440 | +7.50% / +7.61% | 0.0..0.0% | **ADVANCE** |
| **S7** | Marginal-mass electrification - one EXISTING trailer axle motorised, tractor untouched | 19,846 kg | 40.48 | 0.0 | 0.8261 / 0.8644 / 0.9757 | +4.51% / +5.90% | 1.2..2.5% | **ADVANCE** |
| **S4p** | Range-extended BEV re-posed - cited external energy cell (ESC-1c), electricity term (ESC-3) | 20,134 kg | 24.77 | 110.8 | 0.7194 / 0.7741 / 0.8996 | +11.95% / +15.83% | 15.6..30.5% | **ADVANCE** |

### 4.2 LH-520 - the control duty (does not gate)

| | architecture | payload | L/100 km | grid kWh | MJ_primary/payload-tkm (min / median / max) | margin vs ruler (min / median) | correction share (min..max) | verdict |
|---|---|---|---|---|---|---|---|---|
| **S0R** | Conventional 13 L diesel + 12-speed AMT with a direct top gear, + hydraulic retarder (ESC-6) | 20,655 kg | 39.56 | 0.0 | 0.7541 / 0.8116 / 0.9159 | - (ruler) | 0.0..0.0% | **RULER** |
| **S5** | Minimal transmission - 2-speed dog box, motor-synchronised shifts, torque-fill through the shift | 19,970 kg | 39.53 | 0.0 | 0.7703 / 0.8387 / 0.9685 | -5.75% / -3.49% | -0.2..18.9% | **KILL** |
| **S5-13L** | Minimal transmission with the 13 L engine - the other end of the ratio law | 19,706 kg | 37.88 | 0.0 | 0.7553 / 0.8145 / 0.9286 | -1.38% / -0.66% | -0.7..15.7% | **ADVANCE** |
| **S6** | Zero-mass stack - opposed-piston-class engine + predictive energy management, mechanical drive as S0 | 20,655 kg | 36.65 | 0.0 | 0.6989 / 0.7518 / 0.8467 | +7.26% / +7.39% | 0.0..0.0% | **ADVANCE** |
| **S7** | Marginal-mass electrification - one EXISTING trailer axle motorised, tractor untouched | 19,846 kg | 38.09 | 0.0 | 0.7494 / 0.8133 / 0.9292 | -1.45% / -0.21% | 1.2..2.5% | **ADVANCE** |
| **S4p** | Range-extended BEV re-posed - cited external energy cell (ESC-1c), electricity term (ESC-3) | 20,134 kg | 35.88 | 110.7 | 0.7570 / 0.8351 / 0.9783 | -6.81% / -2.75% | 15.6..30.5% | **ADVANCE** |

The **correction share** column is the one to read sceptically. It is the fraction of a candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: energy its prime mover and buffer could not deliver, charged back as fuel at the run's own duty-averaged efficiency so that every candidate is compared having completed the same mission, plus the charge-sustaining make-up. It is exported SIGNED and with BOTH ends of the range, because WS8's finding F4 was that exporting only the max of a signed quantity hid a credit worth half of a candidate's headline. A large POSITIVE share is a capability finding, not a fuel one.

**A note on S7's one tuned constant, because it is the obvious place to attack the result.** S7's supervisor takes a declared 35% share of the tractive demand while the buffer is above its floor - a number WS9 chose, not derived. It matters less than it looks, and the run says why: on the design duty the trailer machine delivered 35.2 kWh at the wheel while regen returned 38.3 kWh to the bus, and the buffer started at 0.60 state of charge and ended at 0.197 against a floor of 0.15. S7's assist is REGEN-LIMITED, not policy-limited: energy out is energy in, and the share sets only the RATE at which a buffer that is already empty most of the mission gets emptied. A larger share would not deliver more energy; it would deliver the same energy sooner.

### 4.3 Where the mass goes - to the kilogram

| item | S0R | S5 | S5-13L | S6 | S7 | S4p |
|---|---|---|---|---|---|---|
| engine 13l wet | 1,215 | - | 1,215 | - | 1,215 | - |
| aftertreatment | 155 | 155 | 155 | 155 | 155 | 90 |
| amt 12sp | 325 | - | - | 325 | 325 | - |
| hydraulic retarder | 130 | - | - | 130 | 130 | - |
| driveshafts | 65 | 65 | 65 | 65 | 65 | 65 |
| drive axle gearsets | 530 | 530 | 530 | 530 | 530 | 530 |
| fuel | 555 | 555 | 555 | 555 | 555 | 210 |
| engine 11l wet | - | 1,035 | - | - | - | - |
| two speed dog box | - | 205 | 205 | - | - | - |
| traction motors | - | 317 | 317 | - | - | 317 |
| inverters | - | 52 | 52 | - | - | 52 |
| motor reduction stages | - | 115 | 115 | - | - | 115 |
| traction disconnect | - | 42 | 42 | - | - | - |
| brake resistor | - | 61 | 65 | - | - | 126 |
| buffer pack | - | 310 | 390 | - | 181 | - |
| hv cabling | - | 55 | 55 | - | 88 | 55 |
| contactors precharge | - | 18 | 18 | - | 18 | 18 |
| hv misc bms thermal | - | 95 | 95 | - | 95 | 155 |
| pack precondition and cab heat path | - | 50 | 50 | - | 50 | 50 |
| engine opposed piston wet | - | - | - | 1,215 | - | - |
| trailer axle carrier delta | - | - | - | - | 230 | - |
| trailer traction motor | - | - | - | - | 48 | - |
| trailer inverter | - | - | - | - | 8 | - |
| trailer motor reduction | - | - | - | - | 12 | - |
| trailer eaxle disconnect | - | - | - | - | 42 | - |
| trailer hv interface | - | - | - | - | 38 | - |
| sustainer engine wet | - | - | - | - | - | 640 |
| generator | - | - | - | - | - | 135 |
| traction pack | - | - | - | - | - | 938 |
| **powertrain total** | **2,975** | **3,660** | **3,924** | **2,975** | **3,784** | **3,496** |
| **payload** | **20,655** | **19,970** | **19,706** | **20,655** | **19,846** | **20,134** |

### 4.4 Control policies, declared

**S0R** - AMT selects the highest gear that can deliver the demanded wheel force above 1,050 rpm; launch on a slipping clutch at 1,200 rpm with the slip heat charged; overrun fuel cut-off when the wheels drive the engine; accessories crank-driven; cab heat from engine coolant, free. DESCENT: the hydraulic retarder is the primary auxiliary brake and takes the duty first (which is how a retarder-equipped truck is actually driven, and is the conservative direction for the coolant circuit in the heat ledger), the compression brake takes what is left, then the declared continuous friction allowance.

**S5** - Below the low gear's coupling floor the dogs are open, the engine is OFF and the machine launches the combination from the buffer. Above it the engine drives through whichever ratio is legal and the machine fills torque through shifts, assists on transients, regenerates on braking, and is back-driven by the engine to restore the buffer whenever the engine's load fraction is below its BSFC-optimal load and the buffer is under target. Shifts are dog engagements with the ENGINE speed-matched; each is charged its torque-fill energy. Descent: regen to the buffer up to its acceptance AT THE PACK'S ACTUAL TEMPERATURE, then the compression brake, then the resistor, then the declared friction allowance. Spin drag charged by the one WS9 rule whenever the machine is connected and unloaded; the disconnect is open otherwise and its mass is charged.

**S5-13L** - Below the low gear's coupling floor the dogs are open, the engine is OFF and the machine launches the combination from the buffer. Above it the engine drives through whichever ratio is legal and the machine fills torque through shifts, assists on transients, regenerates on braking, and is back-driven by the engine to restore the buffer whenever the engine's load fraction is below its BSFC-optimal load and the buffer is under target. Shifts are dog engagements with the ENGINE speed-matched; each is charged its torque-fill energy. Descent: regen to the buffer up to its acceptance AT THE PACK'S ACTUAL TEMPERATURE, then the compression brake, then the resistor, then the declared friction allowance. Spin drag charged by the one WS9 rule whenever the machine is connected and unloaded; the disconnect is open otherwise and its mass is charged.

**S6** - Driveline, retarder, axles and aftertreatment identical to the ruler - S6 is mass-neutral with S0R to the kilogram. The engine is an opposed-piston-class unit whose island BSFC is solved to a CITED peak brake thermal efficiency of 49.2%, with NO other credit taken from the source (see ws9_engines.WHAT_WS9_DOES_NOT_TAKE). Predictive energy management modifies the DEMANDED SPEED with route preview - slowing before a crest, building speed before a climb, within a declared +/-6% band, renormalised so the mean demanded speed is unchanged - so the saving is energy management and not a speed reduction in disguise.

**S7** - The tractor drives exactly as the ruler does and is never told anything. The trailer machine assists whenever the tractor's demanded wheel force exceeds what the engine can deliver in the gear it is in, and otherwise takes a declared share of the tractive demand while the buffer is above its floor; it regenerates on every braking event up to the buffer's acceptance AT THE PACK'S ACTUAL TEMPERATURE. It has a disconnect and its mass is charged; spin drag is charged by the one WS9 rule whenever it is connected and unloaded. There is no resistor: the tractor's retarder and compression brake own the descent, which is the point of leaving the tractor untouched.

**S4p** - Electric traction only. The pack starts at its plug-in ceiling and the sustainer stays OFF while the pack is above its charge-depleting floor; below it the sustainer holds charge on the engine's BSFC-optimal locus with start-stop hysteresis. The grid energy consumed is metered as the state-of-charge the mission actually spent and is charged at a declared primary-energy factor and CO2 intensity, both swept +/-50%. Descent braking: regen to the pack up to its acceptance AT THE PACK'S ACTUAL TEMPERATURE, then the resistor, then friction. Pack preconditioning is served from the sustainer's coolant when it is running and from an electric heater when it is not - which, for a candidate whose engine is off most of the mission, is the cold wall's sharpest edge and is modelled rather than assumed.

### 4.5 Informative brackets (nominal corner, not the metric of record)

| bracket | payload | vs ruler | GH-REG-165 margin (min / median) | LH-520 margin (min / median) | what it asks |
|---|---|---|---|---|---|
| **S5-P2** | 20,198 kg | -457 kg | +5.25% / +6.95% | -3.52% / -1.92% | what the machine on the gearbox INPUT saves, and what it costs: leaner by construction because it launches through the low ratio, but on the wrong side of the element that opens, so the shift becomes a torque interruption instead of a torque fill |
| **S5-GH** | 19,804 kg | -851 kg | +0.14% / +1.61% | -8.44% / -7.05% | what a minimal transmission solved against the DESIGN DUTY's grade rather than the assignment's 6% would do - the steepest a contiguous 2-speed can carry on the 13 L, paid for in cruise engine speed |
| **S0R-PCC** | 20,655 kg | +0 kg | -0.09% / +0.03% | -0.35% / -0.22% | what predictive energy management - a ZERO-MASS lever - is worth ON THE RULER. If the incumbent may fit it, S6's margin loses whatever it is worth (ESC-WS9-5) |

### 4.6 Sizing rules, stated before the numbers

Every pack and every resistor in WS9 is sized by a RULE evaluated in code, never by a chosen kWh. WS8's S1 carried a 60 kWh buffer with no stated rule and 736 kg of it was payload.

| candidate | cell | sizing rule | binding case | kWh for power | kWh for energy | built | mass |
|---|---|---|---|---|---|---|---|
| **S5** | LTO-23 | max over the enumerated sizing case set {power, energy} | **power** | 16.19 | 10.98 | 17.03 kWh | 310 kg |
| **S5-13L** | LTO-23 | max over the enumerated sizing case set {power, energy} | **power** | 21.37 | 11.71 | 22.01 kWh | 390 kg |
| **S7** | LTO-23 | max over the enumerated sizing case set {power, energy} | **energy** | 0.00 | 8.11 | 9.05 kWh | 181 kg |

| candidate | resistor sizing case | retard required | engine brake | friction allowance | resistor rated | mass |
|---|---|---|---|---|---|---|
| **S5** | -6% at 90 km/h, hold the enumerated descent case with the pack at ZERO charge acceptance | 433 kW | 197 kW | 60 kW | **170 kW** | 61 kg |
| **S5-13L** | -6% at 90 km/h, hold the enumerated descent case with the pack at ZERO charge acceptance | 433 kW | 180 kW | 60 kW | **180 kW** | 65 kg |
| **S4p** | -6% at 90 km/h, hold the enumerated descent case with the pack at ZERO charge acceptance | 433 kW | 0 kW | 60 kW | **350 kW** | 126 kg |

**Chemistry, as a stated bracket rather than a preference.** A buffer is bought for charge acceptance, cold behaviour and cycle life; WS8 used the densest of WS3's three cells for every pack, which is right for an ENERGY pack and wrong for a buffer.

| | cell | charge acceptance | discharge | cold factor at -10 C | equivalent full cycles | mass |
|---|---|---|---|---|---|---|
| of record | LTO-23 | 72 kW | 72 kW | 1.099 | 20,000 | 181 kg |
| bracket | NMC-P-40 | 36 kW | 72 kW | 0.127 | 3,000 | 141 kg |

The chemistry of record costs 40 kg more than the bracket at the same nameplate. same nameplate, same usable fraction, same sizing rule; WS8 used NMC-P-40 for every pack because it was the densest of WS3's three, which is right for an ENERGY pack and wrong for a buffer - a buffer is bought for charge acceptance, cold behaviour and cycle life, and this is what each cell gives on those three

---

## 5. The cold wall (R30), modelled rather than assumed

R30: *"Every WS9 electrified candidate carries pack preconditioning and a coolant/waste-heat cab-heating path as requirements, MODELLED, NOT ASSUMED; the conventional truck heats itself for free and the comparison must charge that."*

Both halves are hardware with mass and physics with a state. The pack temperature is integrated at 10 Hz alongside its state of charge, starting COLD-SOAKED AT AMBIENT, warmed by its own ohmic loss, by engine coolant through a declared heat exchanger whenever an engine is running, and by an electric heater that draws from the bus when one is not. The charge ceiling at each sample is then WS3's own `p_cont_chg_kw_at(T_pack)` - the method WS8's finding F2 found defined and never called. WS8 round 2 wired it to the corner's AMBIENT; WS9 evaluates it at the pack's ACTUAL temperature, which is stricter at the start of a trip and kinder later.

At the -10 C corner, on the design duty:

| | pack at start | pack at end | charge acceptance cold-soaked / warm | collapse factor | seconds below target | coolant waste heat used | electric heater energy |
|---|---|---|---|---|---|---|---|
| **S5** | -10.0 C | 39.2 C | 136.3 / 136.3 kW | 1.000 | 847 s | 1.03 kWh | 0.97 kWh |
| **S5-13L** | -10.0 C | 35.2 C | 176.1 / 176.1 kW | 1.000 | 887 s | 1.21 kWh | 1.28 kWh |
| **S7** | -10.0 C | 58.6 C | 72.4 / 72.4 kW | 1.000 | 584 s | 0.74 kWh | 0.41 kWh |
| **S4p** | -10.0 C | 38.4 C | 22.5 / 150.0 kW | 0.150 | 1948 s | 0.00 kWh | 5.14 kWh |

The asymmetry is physical and it is R30's intended effect: a candidate that runs an engine for most of the mission gets its cab heat free and its pack preconditioned from coolant at no fuel cost; a candidate whose engine is off for most of the mission pays for both out of the bus. That is why the cold corner stops being a common-mode penalty and becomes an architecture-dependent one. The 2.2 / 1.0 kW split of WS8's own 3.2 kW cold delta into cab heat and battery thermal is WS9-declared and is escalated (ESC-WS9-6).

### 5.1 The electricity term and its sensitivity (ESC-3)

ESC-3, ruled in R27, gives Vehicle One's metric an electricity term for any plug-in candidate. Applies to: **S4p**.

| | |
|---|---|
| diesel well-to-tank primary factor | 1.190 |
| grid primary-energy factor | 2.100 |
| grid CO2e intensity at the meter | 0.280 kg/kWh |
| grid to pack efficiency | 0.9215 |
| factor sensitivity | +/-50% |

The diesel factor multiplies every candidate's fuel term identically, so for every candidate that imports no grid energy the primary-energy margin and the tank-energy margin are the SAME NUMBER - asserted in section 11, not claimed. The metric therefore changes exactly one thing in this trial.

Both lenses, on the design duty at nominal, with the grid factors swept +/-50%:

| candidate | MJ_primary/payload-tkm (grid factor -50% / declared / +50%) | margin vs ruler at each | gCO2e/payload-tkm (-50% / declared / +50%) |
|---|---|---|---|
| **S0R** | 0.9196 / 0.9196 / 0.9196 | - (ruler) | 68.1 / 68.1 / 68.1 |
| **S5** | 0.8863 / 0.8863 / 0.8863 | +3.63% / +3.63% / +3.63% | 65.7 / 65.7 / 65.7 |
| **S5-13L** | 0.8544 / 0.8544 / 0.8544 | +7.09% / +7.09% / +7.09% | 63.3 / 63.3 / 63.3 |
| **S6** | 0.8506 / 0.8506 / 0.8506 | +7.50% / +7.50% / +7.50% | 63.0 / 63.0 / 63.0 |
| **S7** | 0.8644 / 0.8644 / 0.8644 | +6.00% / +6.00% / +6.00% | 64.1 / 64.1 / 64.1 |
| **S4p** | 0.6477 / 0.7741 / 0.9004 | +29.57% / +15.83% / +2.09% | 43.3 / 48.0 / 52.7 |

**And the sweep is read against the criteria, not merely reported.** the SAME pre-committed criteria, unchanged, applied to the same runs priced at each end of the +/-50% grid-factor sweep ESC-3 orders:

| candidate | grid factor -50% | declared | grid factor +50% |
|---|---|---|---|
| **S4p** | +24.29% -> **ADVANCE** | +11.95% -> **ADVANCE** | -0.38% -> **KILL** |
| **S5** | +1.90% -> **KILL** | +1.90% -> **KILL** | +1.90% -> **KILL** |
| **S5-13L** | +5.36% -> **ADVANCE** | +5.36% -> **ADVANCE** | +5.36% -> **ADVANCE** |
| **S6** | +7.50% -> **ADVANCE** | +7.50% -> **ADVANCE** | +7.50% -> **ADVANCE** |
| **S7** | +4.51% -> **ADVANCE** | +4.51% -> **ADVANCE** | +4.51% -> **ADVANCE** |

**S4p's verdict MOVES across the swept range.** The grid factor is DECLARED, not sourced from a fetched primary document (ESC-WS9-2), so whatever the lead fixes it at is not a reporting convention - it is part of the verdict. Every candidate that imports no grid energy is invariant across the sweep by construction, which is the same invariance section 11 asserts.

---

## 6. Prime mover at the pin

**Scope, checked rather than assumed:** the only WS9 candidate with a series element is S4'; S5 drives mechanically through a dog box and S7 never touches the tractor's engine, so neither has a pinned point. `sanity.prime_mover_scope.only_S4p` = `True`.

Equal range is priced at **800 km** of the duty that asks most of the sustainer (`LH-520`), at 1.1346 bus kWh per km. Price is out of scope (D12).

| prime mover | displacement | eta at the pin | eta at the duty | engine | aftertreatment | fuel | fuel + tank | **total charged** | gCO2e per bus-kWh |
|---|---|---|---|---|---|---|---|---|---|
| **diesel** | 7.00 L | 0.4064 | 0.4063 | 640 kg | 90 kg | 188 kg | 216 kg | **946 kg** | 657 |
| **petrol** | 9.08 L | 0.3864 | 0.3846 | 804 kg | 30 kg | 196 kg | 231 kg | **1,065 kg** | 683 |
| **natural gas (CNG)** | 8.17 L | 0.3818 | 0.3801 | 723 kg | 35 kg | 172 kg | 2,866 kg | **3,625 kg** | 571 |
| **natural gas (LNG)** | 8.17 L | 0.3818 | 0.3801 | 723 kg | 35 kg | 172 kg | 447 kg | **1,205 kg** | 571 |

- **best efficiency at the pin**: diesel (0.4064), an explicit max over the enumerated prime-mover set (R14)
- **lowest charged mass**: diesel (946), an explicit min over the enumerated prime-mover set (R14)
- **lowest CO2e per bus-kWh**: natural gas (CNG) (571), an explicit min over the enumerated prime-mover set (R14)

**read the three rows together, not the efficiency column alone: the pin rewards the diesel on efficiency, the aftertreatment rewards both spark-ignition engines, and the TANK decides the answer - because at fixed gross combination weight a tank is payload, and compressed methane's vessel weighs many times the fuel it holds.**

Part-load, because rule 5 forbids judging a duty on a peak point and the pin IS a peak point:

| prime mover | 25% | 50% | 75% | 100% of the bus rating |
|---|---|---|---|---|
| diesel | 0.3882 | 0.4023 | 0.4063 | 0.3894 |
| petrol | 0.3605 | 0.3789 | 0.3853 | 0.3846 |
| natural gas (CNG) | 0.3579 | 0.3747 | 0.3807 | 0.3802 |
| natural gas (LNG) | 0.3579 | 0.3747 | 0.3807 | 0.3802 |

**Cold behaviour and fixed-point durability** - one entry per ENGINE, because the two natural-gas rows are the same engine differing only in the vessel:

**diesel - cold behaviour.** Worst of the three. Compression ignition needs a hot charge: grid heaters or glow plugs at start, and a long warm-up during which combustion is poor. The aftertreatment is the harder half - SCR needs roughly 200 C before urea can be dosed at all, so a cold sustainer emits NOx it cannot treat, and the DEF itself freezes at -11 C and needs heated lines and tank. A PINNED point mitigates much of this: the engine goes to a high-load point immediately and gets the catalyst hot fast, which is one of the real arguments for a series layout.

**diesel - fixed-point durability.** Excellent, and it is the incumbent for a reason. Heavy-duty diesels are designed for a B10 life measured in the millions of kilometres under FAR harsher duty than a pinned point: no transients, no cold cycling once warm, one speed, one load. A genset diesel is a diesel doing the easiest job it will ever be asked to do.

**petrol - cold behaviour.** Best of the three. Spark ignition starts cold without assistance; a three-way catalyst lights off in the order of 20 seconds; there is no urea to freeze and no filter to regenerate. The cost is cold-start enrichment - a stoichiometric engine runs rich until the oxygen sensor is hot - which is a fuel penalty of a few hundred grams per start, not a capability limit.

**petrol - fixed-point durability.** THE OPEN QUESTION, and it is the finding of this task rather than an aside. There is no heavy-duty petrol engine in service to point at. Pinned operation removes the two things that usually kill a petrol engine in heavy service - knock under transient load, and valve-seat recession from repeated cold cycling - and a fixed low-BMEP point is benign. But the absence of a product means the 1,000,000 km claim has no evidence behind it, and WS9 will not manufacture one. The efficiency numbers below stand; the durability row is a RISK, stated as one.

**natural gas - cold behaviour.** Good at the engine, awkward at the catalyst and at the tank. Spark ignition starts cold; there is no urea and no filter. But METHANE IS THE HARDEST HYDROCARBON A THREE-WAY CATALYST HAS TO CONVERT and needs roughly 450 C to do it, so a cold start passes unburned methane straight through - and methane's GWP makes that slip count for far more than its mass. On the tank side, CNG pressure and therefore usable mass fall with temperature, and LNG in a vehicle tank boils off when the vehicle stands.

**natural gas - fixed-point durability.** Demonstrated in service. Stoichiometric heavy-duty gas engines are production products (the Cummins ISX12 G lineage and the X15N) with fleet hours behind them. The known wear mechanisms are exhaust valve and seat recession at stoichiometric exhaust temperature, and shorter oil life; both are maintenance items, not capability limits, and both are milder at a pinned point than on the road.

---

## 7. Corners (R28)

Margins vs the ruler [%] on the **design duty**, ensemble min / median, at every corner. The control-duty result is reported after it and does not gate.

| candidate | nominal | payload_plus20 | payload_minus20 | grade_heavy | cold_minus10C | hot_alt_2000m_45C |
|---|---|---|---|---|---|---|
| **S4p** | +11.95% / +15.83% | +10.95% / +14.59% | +12.93% / +16.93% | +11.95% / +15.83% | +7.40% / +10.56% | +13.57% / +16.77% |
| **S5** | +1.90% / +4.64% | +1.39% / +4.25% | +2.68% / +4.56% | +1.90% / +4.64% | +0.27% / +3.14% | +0.49% / +3.89% |
| **S5-13L** | +5.36% / +7.07% | +4.89% / +6.44% | +5.69% / +6.31% | +5.36% / +7.07% | +3.93% / +5.14% | +4.85% / +7.01% |
| **S6** | +7.50% / +7.61% | +7.54% / +7.71% | +7.29% / +7.52% | +7.50% / +7.61% | +7.47% / +7.63% | +7.54% / +7.72% |
| **S7** | +4.51% / +5.90% | +4.44% / +5.91% | +4.21% / +5.91% | +4.51% / +5.90% | +3.58% / +4.97% | +4.85% / +5.94% |

Same table on the **control duty** (informative):

| candidate | nominal | payload_plus20 | payload_minus20 | grade_heavy | cold_minus10C | hot_alt_2000m_45C |
|---|---|---|---|---|---|---|
| **S4p** | -6.81% / -2.75% | -6.66% / -2.87% | -7.76% / -3.27% | -3.55% / +1.87% | -9.50% / -5.56% | -3.49% / +0.06% |
| **S5** | -5.75% / -3.49% | -4.61% / -2.96% | -8.13% / -5.02% | -0.48% / +0.47% | -6.60% / -3.74% | -4.95% / -3.00% |
| **S5-13L** | -1.38% / -0.66% | -1.00% / +0.04% | -3.26% / -2.18% | +0.56% / +0.91% | -3.21% / -0.97% | -0.00% / +1.11% |
| **S6** | +7.26% / +7.39% | +7.40% / +7.44% | +7.19% / +7.37% | +7.26% / +7.38% | +7.36% / +7.39% | +7.35% / +7.42% |
| **S7** | -1.45% / -0.21% | -1.14% / +0.10% | -1.92% / -0.53% | +0.41% / +2.63% | -1.98% / -0.77% | +0.59% / +1.75% |

---

## 8. Capability shortfalls, reported rather than absorbed

Energy the prime movers and the buffer together could not deliver. It is charged back as fuel so every candidate completes the same mission, priced at the run's own DUTY-AVERAGED efficiency per r2's rule, and reported here RAW because a large value is a CAPABILITY finding, not a fuel one.

**Where the largest ones come from, said plainly.** The tractive ENVELOPE each candidate is integrated against is built from its prime mover's continuous rating plus the pack contribution that survives a 15-minute climb (WS8's `SUSTAINED_CLIMB_S` rule, carried unchanged). The DISPATCH then has to feed that envelope sample by sample out of a pack with a finite state of charge. For a candidate whose pack is large but is deliberately being DEPLETED - S4' runs charge-depleting until its floor - the envelope is generous late in a long mission, when only the sustainer is left. That gap is exactly what this table measures, and it is why the correction share in section 4 is the column to read before the margin.

Worst case **257.10 kWh** (governing case: `S4p/grade_heavy/LH-520`), an explicit max over the enumerated (candidate, corner, duty) case set per R14.

Cases above 1 kWh:

| case | unserved kWh |
|---|---|
| `S4p/grade_heavy/LH-520` | 257.10 |
| `S4p/cold_minus10C/LH-520` | 228.80 |
| `S4p/payload_plus20/LH-520` | 226.77 |
| `S4p/nominal/LH-520` | 190.10 |
| `S4p/hot_alt_2000m_45C/LH-520` | 166.74 |
| `S4p/payload_minus20/LH-520` | 153.69 |
| `S5/payload_plus20/GH-REG-165` | 67.55 |
| `S5/hot_alt_2000m_45C/GH-REG-165` | 59.88 |
| `S5/cold_minus10C/GH-REG-165` | 58.37 |
| `S4p/payload_plus20/GH-REG-165` | 57.90 |
| `S5-13L/payload_plus20/GH-REG-165` | 57.50 |
| `S5/grade_heavy/GH-REG-165` | 54.22 |
| `S5/nominal/GH-REG-165` | 54.22 |
| `S4p/cold_minus10C/GH-REG-165` | 50.33 |
| `S5-13L/hot_alt_2000m_45C/GH-REG-165` | 49.62 |
| `S5-13L/cold_minus10C/GH-REG-165` | 48.90 |
| `S4p/grade_heavy/GH-REG-165` | 45.80 |
| `S4p/nominal/GH-REG-165` | 45.80 |
| `S5-13L/grade_heavy/GH-REG-165` | 44.84 |
| `S5-13L/nominal/GH-REG-165` | 44.84 |
| `S4p/hot_alt_2000m_45C/GH-REG-165` | 44.03 |
| `S5/payload_minus20/GH-REG-165` | 37.06 |
| `S4p/payload_minus20/GH-REG-165` | 35.00 |
| `S5-13L/payload_minus20/GH-REG-165` | 28.07 |
| `S7/grade_heavy/LH-520` | 13.51 |
| `S5/hot_alt_2000m_45C/LH-520` | 13.15 |
| `S5/cold_minus10C/LH-520` | 13.07 |
| `S5/payload_plus20/LH-520` | 12.16 |
| `S7/payload_plus20/LH-520` | 10.94 |
| `S5/nominal/LH-520` | 10.32 |
| `S7/nominal/LH-520` | 9.12 |
| `S5/grade_heavy/LH-520` | 7.32 |
| `S7/payload_minus20/LH-520` | 7.24 |
| `S5/payload_minus20/LH-520` | 6.97 |
| `S7/hot_alt_2000m_45C/LH-520` | 6.81 |
| `S7/cold_minus10C/LH-520` | 6.66 |
| `S5-13L/cold_minus10C/LH-520` | 4.51 |
| `S7/payload_plus20/GH-REG-165` | 4.04 |
| `S5-13L/payload_plus20/LH-520` | 3.96 |
| `S5-13L/hot_alt_2000m_45C/LH-520` | 3.64 |
| `S7/grade_heavy/GH-REG-165` | 3.49 |
| `S7/nominal/GH-REG-165` | 3.49 |
| `S5-13L/payload_minus20/LH-520` | 3.09 |
| `S7/payload_minus20/GH-REG-165` | 2.98 |
| `S5-13L/nominal/LH-520` | 2.74 |
| `S7/hot_alt_2000m_45C/GH-REG-165` | 2.74 |
| `S7/cold_minus10C/GH-REG-165` | 2.56 |

**Power-limited fraction** - a capability metric, not a fuel one. The integrator gives a candidate that cannot hold the demanded speed the speed it CAN hold, charges it the extra time in accessory energy, and records the shortfall - so a large value here and a good margin together mean the margin was earned on a slower truck.

| candidate | GH-REG-165 | LH-520 |
|---|---|---|
| **S0R** | 0.1909 | 0.1902 |
| **S5** | 0.3597 | 0.3057 |
| **S5-13L** | 0.2655 | 0.1704 |
| **S6** | 0.1930 | 0.1944 |
| **S7** | 0.1802 | 0.1793 |
| **S4p** | 0.0857 | 0.0714 |

**Retarding shortfall** - worst case 13.804 kWh (governing case: `S5-13L/payload_plus20/LH-520`). energy the envelope granted as retarding force that neither the pack nor the resistor could actually absorb. The resistor sizing rule is written to make this zero at the enumerated descent case; a non-zero value elsewhere means the descent-speed governor let the candidate run faster than its sink supports, and it is reported rather than absorbed.

**Trip time, which the metric of record cannot see.** the metric of record is energy per payload tonne-km and it is BLIND TO TIME. A candidate that completes the same mission 10% slower delivers 10% fewer tonne-km per driver-day, and nothing in the headline says so. The integrator charges the extra time in accessory energy, which is a small fraction of what it actually costs an operator. Escalated as ESC-WS9-9. Worst case +15.7% (governing case: `S5/payload_plus20/GH-REG-165`).

| candidate | GH-REG-165 trip time vs ruler | LH-520 trip time vs ruler |
|---|---|---|
| **S0R** | +0.0% | +0.0% |
| **S5** | +12.8% | +3.4% |
| **S5-13L** | +6.1% | -0.1% |
| **S6** | +0.2% | +0.4% |
| **S7** | -0.3% | -0.3% |
| **S4p** | -2.5% | -2.6% |

**R22(d) spin drag, disclosed.** Rule: geared AND the machine's own commanded force <= 1.0 N AND v > 0.5 m/s (WS8 r2's rule and r2's thresholds, applied to the machine's shaft). R22(d) cost Vehicle Zero 1.77 pp. It costs almost nothing here, and the reason is the driver model rather than the hardware: this integrator's driver is either pulling or braking on nearly every sample, so the unloaded test is rarely true. Candidates that fit a disconnect pay nothing while it is open, and its mass IS charged - so the disconnect is a mass cost with almost no measured benefit on this duty, which is itself worth the lead's attention.

| candidate | spin charged (design duty, median) | as a share of bus traction |
|---|---|---|
| **S5** | 1.0633 kWh | 1.586% |
| **S5-13L** | 1.1335 kWh | 1.775% |
| **S7** | 0.0002 kWh | 0.001% |
| **S4p** | 0.0011 kWh | 0.000% |

---

## 9. Electric turbocompound, on the design duty (R31)

Gate, pre-committed: **R31 / assignment: 'electric turbocompound ONLY if it clears the 2.5% net gate on the design duty'**

Read on net PRIMARY energy per payload tonne-km on the DESIGN DUTY, AFTER the mass charge, ensemble-min against the threshold (the statistic G1 and WS8's own WHR gate were read on).

| | |
|---|---|
| mass charge | 85 kg |
| payload penalty | +0.41% |
| fuel gain needed to clear the gate | **2.91%** |
| net margin on the design duty, ensemble-min | **+1.67%** |
| net margin on the design duty, median | +1.80% |
| gate | >= 2.5% |
| **verdict** | **DROPPED** |

R31 admitted electric turbocompound to S6 only if it cleared the same 2.5% gate on the design duty, whose load fraction is higher than the fleet average WS8 tested against. The mass charge sets the real bar above the gate, because the metric divides by payload - which is the same arithmetic that dropped waste-heat recovery in WS8, and D14 is why: waste-heat recovery is a full-load technology and even a grade-heavy regional duty is a part-load condition for most of its distance.

---

## 10. Recommendation

Criteria, pre-committed. assignment, quoted verbatim: 'ADVANCE only if >=3% better than S0 on the DESIGN DUTY at nominal, ensemble-min, AND >=0% at every R28 corner; report the control-duty result alongside without it gating.' Read on the **ensemble_min**, on the **GH-REG-165** duty; the **LH-520** result is reported alongside and does not gate.

| candidate | design nominal min | worst design corner | worst corner min | control duty (informative) | passes nominal | passes corners | verdict |
|---|---|---|---|---|---|---|---|
| **S4p** | +11.95% | cold_minus10C | +7.40% | -6.81% | True | True | **ADVANCE** |
| **S5** | +1.90% | cold_minus10C | +0.27% | -5.75% | False | True | **KILL** |
| **S5-13L** | +5.36% | cold_minus10C | +3.93% | -1.38% | True | True | **ADVANCE** |
| **S6** | +7.50% | payload_minus20 | +7.29% | +7.26% | True | True | **ADVANCE** |
| **S7** | +4.51% | cold_minus10C | +3.58% | -1.45% | True | True | **ADVANCE** |

- **S4p: ADVANCE** - meets both criteria.
- **S5: KILL** - fails the nominal >=3% criterion on the design duty.
- **S5-13L: ADVANCE** - meets both criteria.
- **S6: ADVANCE** - meets both criteria.
- **S7: ADVANCE** - meets both criteria.

**What WS9 recommends.** The numbers are above and the execute-or-spare decision is the lead's. What WS9 will say is this:

1. **Read S6's verdict together with ESC-WS9-1 and ESC-WS9-5.** S6 is the cleanest arithmetic in the report - mass-neutral with the ruler to the kilogram, so its margin is its fuel margin and nothing else - and it is also the candidate most exposed on evidence. Its whole margin is one cited peak brake thermal efficiency, and part of it is a zero-mass control lever the incumbent could fit tomorrow. The break-even BTE (0.4688 against a claimed 0.492) says how much of the claim must hold; the S0R-PCC bracket says how much of the margin is the engine.

2. **S5 clears the numeric bar on the design duty and fails a capability test the numeric bar cannot see.** Its two ratios do span cruise and the assignment's 6% grade, in closed form. They do not span the design duty's 10.7% grades, because the low gear's coupling floor is above the crawl speed those grades force and below that floor the engine is not connected at all. That shows up in the fuel number only as a correction - which is exactly the shape of WS8's S3 finding, and WS8's own conclusion applies: the fuel result is not the finding, the capability result is.

3. **The duty decides the architecture, and now there is a number for it.** Section 7's corner tables and the design/control pair in section 4 span the sign change R29 predicted. An operator running loaded over mountains and one running a flat corridor are not looking at the same vehicle.

4. **Mass is still the binding constraint, and the ranking follows the payload column.** Section 4.3 is the argument. The candidate that adds no mass wins; the candidates that add 500-1,000 kg have to find 3-5% of fuel before they have found anything at all.

5. **S4' advances by the widest margin on the design duty and carries the largest correction in the trial.** Up to 30.5% of its reported fuel is a correction rather than fuel the model watched it burn - energy its sustainer and pack could not deliver on the mountain, charged back so it completes the same mission. It also LOSES to the ruler on the control duty (-6.81% ensemble-min), and its primary-energy advantage is an accounting consequence of ESC-3's grid factor, which is declared rather than sourced (ESC-WS9-2). **AND ITS VERDICT DOES NOT SURVIVE THE SWEEP ESC-3 ITSELF ORDERS**: re-applying the pre-committed criteria unchanged at the +50% end of the grid-factor range turns its design-duty ensemble-min from +11.95% into -0.38% and its verdict from ADVANCE into KILL (section 5.1). Every other candidate is invariant across the sweep. S4' is therefore not a candidate the lead can execute or spare without first fixing the grid factor of record.

6. **The escalations in section 13 change the answer if ruled the other way**, ESC-WS9-1 and ESC-WS9-5 especially. They are not footnotes.

---

## 11. First-principles sanity checks

**Road load at 95 km/h, flat, 36,300 kg.** By hand: aero 2290 N; rolling 1959 N; total 4249 N = 112.1 kW at the wheel. Model agrees: **True**. 2290 N of aero and 1959 N of rolling at 36.3 t and 95 km/h is the whole line-haul problem in two numbers: the air is already the bigger bill, which is why every candidate here wins or loses on driveline efficiency and mass, not on regenerative braking. [formatted from the computed values, per F9]

**Mass closure.** tare + payload = 36,300 kg for every candidate: **True**. at fixed GCW, powertrain mass IS payload - that is WALL 2 and it is the denominator of the metric of record

**S6 is mass-neutral with the ruler.** ruler 20,655 kg, S6 20,655 kg, delta 0.000000 kg: **True**.

**Primary-energy invariance.** the diesel well-to-tank factor multiplies every candidate's fuel term identically, so for every candidate that imports no grid energy the primary-energy margin and the tank-energy margin are the same number. Asserted, not claimed - and it is what makes the metric change exactly one thing in this trial. All pass: **True**.

**ESC-2 machine gate (k <= 2.0).** S5 k=1.800, S5-13L k=1.800, S7 k=0.379, S4p k=1.800, S5-P2 k=1.916, S5-GH k=1.800. All pass: **True**.

**12% startability.** Requires 44373 N at the contact patch; dry tandem adhesion ceiling 105903 N. All candidates meet it: **True**. Regulation (EU) No 1230/2012, five starts within five minutes at >=12% laden to the combination's maximum. WS9 checks torque and adhesion only; the five-in-five clause is a THERMAL requirement on the machine and is NOT modelled - stated, as WS8 stated it.

**Scaling-law implementation.** Per-unit efficiency at k=1.0 and k=1.8 at matched per-unit load agree to 0.0000 pp: **True**. loss(k; n, T) = k * loss_ws2(n, T/k) is per-unit invariant BY CONSTRUCTION, so this confirms the implementation, not the physics - exactly as WS8 said of the same check

**Ruler energy closure.** Fuel energy 2035 kWh, engine shaft work 867 kWh - an implied engine efficiency of 0.4263 against 0.4273 implied by the duty-averaged BSFC of 196.8 g/kWh. Agree: **True**.

**Heat-ledger closure and ratings (finding F1).** F1(c): every descent case must close - the sum of the component rows equals the retarding power the case demands. F1(d): every exported component heat is checked against the rating of the hardware whose mass was charged. WS8 r1's ledger did neither and exported 210.71 kW of resistor heat for a candidate whose resistor was rated 200 kW. All descent cases close: **True**. No rating violations: **True**.

**CO2 factors are a carbon balance, not a lookup.** diesel 74.10, petrol 72.97, methane 54.86 g CO2/MJ, derived from H:C and LHV. Against published spot values: **True**.

**The ambient/altitude derate is exercised (finding F11).** WS4's ruled factor at 2,000 m / +45 C is 0.9312. WS9's own ISA computation of the air density gives 0.8705 kg/m3 against the inherited 0.8710: agree **True**.

**No WS8 numeric artifact is read.** WS9 imports WS8's MODELS and reads none of its NUMBERS. run_ws9.py names both artifacts in one place only - the vintage block, where they are hashed and not opened. So WS8's r1/r2 artifact split cannot move a WS9 number. Passes: **True**.

**Envelope tabulation.** The integrator interpolates each candidate's envelope on a 0.05 m/s grid; worst relative error against direct evaluation 1.20e-03.

**Predictive energy management is not a speed reduction.** the modulated demand trace is renormalised so its distance-weighted mean equals the unmodulated one and is clipped to the assignment's 85-105 km/h band. The ACHIEVED speed and trip time are reported here beside the ruler's, because achieved speed is the integrator's business: if a preview candidate were quietly arriving late, this is where it would show.

| case | mean demand preserved to | max target delta | achieved trip time | ruler trip time | achieved mean speed | ruler mean speed |
|---|---|---|---|---|---|---|
| `S6/GH-REG-165` | 2.49e-14 | 5.95 km/h | 9798 s | 9776 s | 60.63 km/h | 60.76 km/h |
| `S6/LH-520` | 6.36e-13 | 5.86 km/h | 21992 s | 21896 s | 85.12 km/h | 85.50 km/h |
| `S0R-PCC/GH-REG-165` | 2.49e-14 | 5.95 km/h | 9798 s | 9776 s | 60.63 km/h | 60.76 km/h |
| `S0R-PCC/LH-520` | 6.36e-13 | 5.86 km/h | 21992 s | 21896 s | 85.12 km/h | 85.50 km/h |

**All checks pass: True**

---

## 12. Inherited vintage, and the r2 concordance

WS9 imports WS8's MODELS read-only and reads NO WS8 numeric artifact (asserted in sanity.no_ws8_artifact_read). The hashes above pin exactly which WS8 the models came from. If WS8's round 2 regenerates its artifacts after this run, none of WS9's numbers move: WS9 re-derives its own ruler from the same models. If WS8's round 2 changes its CODE after this run, the hashes above will not match and verify_ws9.py says so - that is the hot-swap signal the assignment asks for.

**WS8 code round detected: `r2`.** Fingerprints: cold_charge_acceptance_wired = `True`, derated_engine_present = `True`, one_spin_rule_present = `True`, errata_switches_present = `True`, hot_altitude_corner_present = `True`, heat_split_in_params = `True`.

| inherited WS8 source | bytes | sha256 |
|---|---|---|
| `ws8_params.py` | 15,812 | `d729fc7cb7323dbf...` |
| `ws8_physics.py` | 16,544 | `79f93610de6fd1e5...` |
| `ws8_cycles.py` | 14,784 | `bd5b444294b5034b...` |
| `ws8_engine.py` | 18,002 | `61cc29d04c6a56a3...` |
| `ws8_electric.py` | 18,592 | `74a932dbc7956989...` |
| `ws8_candidates.py` | 106,340 | `e3a741f4097f13d8...` |
| `ws8_whr.py` | 5,986 | `674f91016f31cd29...` |

| WS8 artifact - hashed, NOT read | bytes | sha256 |
|---|---|---|
| `results_ws8.json` | 3,036,230 | `c1b21b0b91b14d4d...` |
| `REPORT_WS8.md` | 176,516 | `9cbfa9336075d6dd...` |
| `R2_DIRECTIVE.md` | 2,179 | `e3040204e8f70f0f...` |
| `FINDINGS_WS8_r1.md` | 28,937 | `b3db6878367b39f1...` |

### 12.1 What WS9 inherits from round 2, and what it implements itself

| WS8 r1 finding | round 2's remedy | WS9's position |
|---|---|---|
| F1 - heat ledger wrong in magnitude and attribution | ledger rebuilt with the simulated peaks in the case set and the retard channel split | WS9 builds its OWN ledger (section 14) on the same principle: an enumerated case set that INCLUDES a pack-saturated descent and the simulated peaks over every run; rows booked by physical location, with the hydraulic retarder to the coolant circuit and the compression brake to the exhaust; a friction-brake row; closure and rating assertions |
| F2 - cold charge acceptance defined and never called | `Pack8.p_cont_chg_kw_at` wired to the CORNER'S AMBIENT | INHERITED, and extended as R30 requires: the pack temperature is a STATE and the ceiling is evaluated at the pack's actual temperature sample by sample. Stricter than r2 at a cold start, kinder once the coolant has warmed it |
| F3 - S2's engine run locked and as a free-speed genset at once | the generator priced at the road-imposed speed out of the torque traction left behind | NOT APPLICABLE - WS9 has no S2. The lesson binds anyway: S5's engine is always at the speed its gear imposes and is never priced on a free-speed locus |
| F4 - the charge-sustaining credit was invisible | symmetric convention DECLARED, share exported signed with min AND max, credit-free variant carried alongside | INHERITED verbatim as the rule; implemented on WS9's own energy keys. Both ends of the signed share are in the R14 block and `fuel_g_corrected_deficit_only` is carried per run |
| F5 - three inconsistent spin-drag treatments | one rule, one threshold, for every candidate | INHERITED - r2's rule and r2's own 1 N / 0.5 m/s thresholds - applied to the MACHINE'S OWN SHAFT rather than the vehicle's force channels, because two WS9 candidates have a machine that is not the only traction path |
| F6 - corrections priced at a peak-point scalar | priced at the run's own duty-averaged efficiency | INHERITED as the rule, on the ENGINE's own wheel work rather than the vehicle's, so regenerated energy is not credited to the engine - the direction that would have flattered the hybrids |
| F7 - the external anchor asserted on a median | restated as an ensemble against the band | RE-RUN for WS9's own ruler as an ensemble AND mass-matched to the reference payload (section 2.1) |
| F8 - a headline specification wrong by 14% | computed ratings rendered instead of literals | every rating in this report is formatted from the computed value; `verify_ws9.py` checks the rendered figures against the results |
| F9 - a hand-written note contradicting the value above it | notes formatted from computed values | INHERITED as a practice - see the road-load note in section 11, which is generated from the numbers it quotes |
| F10 - two margin statistics under one name | one basis, labelled | ONE margin statistic in WS9: per-seed paired against the ruler on the same seed and duty, then enveloped. Nothing else is called a margin |
| F11 - `derate_factor` imported and never called | `derated_engine` added and a 2,000 m / +45 C corner added | INHERITED - WS9 calls r2's function and carries an independent ISA computation of the air density as a check |
| F12 - a swept-grid property reported as a physics bound | the ratio ceiling solved in closed form | INHERITED as the practice: every ratio bound in section 3 is closed form, with the sweep kept as the illustration |
| F13 - a literal climb figure at the top of its ensemble | formatted from the data | every duty statistic in section 1 is an 8-seed envelope formatted from `duties` |

---

## 13. Escalations

Escalations cite the ruling they challenge and are never self-resolved (CLAUDE.md rule 8). They go to the lead.

### ESC-WS9-1 - S6's verdict rests on a manufacturer's demonstration claim, and it is the only candidate that clears the bar

**Cites:** Assignment: 'opposed-piston-class engine on a CITED efficiency basis (state the BTE claim and its evidence quality, mass-neutral or better)'; R31; D7 (novelty is not merit); D5 (nothing kill-bearing is ratified unadjudicated)

**Finding.** S6's engine is calibrated to a peak brake thermal efficiency of 0.492, read verbatim from a PRIMARY document that WS9 fetched and read in full - a strictly better evidence class than anything external in WS8, whose environment blocked egress. It is nonetheless a MANUFACTURER'S document about its own demonstration programme. WS9 has taken the single peak-BTE number and NOTHING else from it (see engines.ENG-OP.cited_claim.what_ws9_does_not_take): not the flatter map, not the 30% lower heat rejection, not the absent pumping loop, not the measured 4-21% route advantages. Every one of those would make S6 better. The break-even peak BTE at which S6 exactly clears the >=3% criterion on the design duty is 0.4688, against the incumbent's 0.4547 - so the lead can see exactly how much of the claim has to be true.

**Why this is not self-resolved.** Whether a manufacturer's demonstration document is sufficient evidence to ADVANCE a candidate is an evidence-standard decision, not a modelling one. WS9 may not set the program's evidence bar.

**Asks.** Rule on ONE of: (a) the cited peak BTE stands as the basis and S6 advances on it; (b) S6 advances CONDITIONALLY, subject to an independent BSFC map before any hardware decision; (c) the claim is discounted to a stated peak BTE and S6 is re-read against the break-even figure.

**Materiality:** high - it is the difference between the only ADVANCE in this trial and no advance at all

### ESC-WS9-2 - The grid primary-energy factor and CO2 intensity are declared, not sourced from a fetched primary document

**Cites:** ESC-3 as ruled in R27; assignment: 'electricity term per ESC-3 with a declared grid primary-energy factor and a CO2 lens, factor sensitivity +/-50%'

**Finding.** WS9 declares PEF_grid = 2.1 (the EU Energy Efficiency Directive default as amended by Directive (EU) 2018/2002) and a grid intensity of 0.28 kg CO2e/kWh at the meter. Both are RECALLED, not fetched: the EEA indicator page was retrieved but publishes its figure only in a chart. The intensity was chosen to sit BETWEEN the EU average (about 0.21 in 2024) and the US average (about 0.37), and Vehicle One has no declared market, so the +/-50% sensitivity ESC-3 orders (0.14 to 0.42) is not decoration here - it spans the entire geographic question, and S4's CO2 verdict moves with it.

**Why this is not self-resolved.** Choosing the grid of record is a program-level metric decision.

**Asks.** Fix the factors of record, or declare Vehicle One's market so they can be sourced. THE SWEEP IS NOT DECORATION: WS9 re-applies the pre-committed criteria unchanged at each end of it (`verdict_robustness_ESC3`), and the verdict of S4p MOVES across the swept range. Whatever the lead fixes the factor at is therefore not a reporting convention but part of the verdict.

**Materiality:** high - it does not move any diesel-only candidate, and it decides a verdict

### ESC-WS9-3 - R28's grade-heavy corner is a null operation on a design duty that is already grade-heavy

**Cites:** R28 (corner set of record); R29 (design duty)

**Finding.** R28 lists 'grade-heavy' among the corners; R29 makes the GRADE-HEAVY REGIONAL corridor the design duty. Applying the grade-heavy terrain construction to a cycle built with it already on changes nothing, and WS9 asserts the identity (sanity.design_duty_null_at_grade_heavy_corner) rather than reporting the same run twice under two names. On the CONTROL duty the corner is real and is reported. The consequence is that the design duty is gated on FOUR corners, not five.

**Why this is not self-resolved.** Inventing a heavier-than-specified terrain corner would be WS9 writing R28.

**Asks.** Confirm that four corners gate the design duty, or specify what a heavier terrain corner should be for a duty whose nominal case already carries 7.9-10.7% grades.

**Materiality:** low for the verdicts, medium for the record

### ESC-WS9-4 - WS9 has replaced R18's transferred flat-rating ratio with an ISO 8528-1 prime-power basis, as ESC-4 directed

**Cites:** ESC-4 as ruled in R27: 'the R18 flat-rating transfer stands as a bracket; WS9 sources a Class 8 prime-power derating basis'; R18; R24

**Finding.** WS9 sources PRP = 0.9 x automotive peak from the ISO 8528-1 rating structure (prime: unlimited hours, 10% overload for one hour in twelve, 70-75% 24-hour average load factor), corroborated by the Cummins QSX15/X15 correspondence. R18's transferred ratio is 0.8611 and is carried alongside as the declared bracket. DIRECTION OF ERROR, stated: PRP is 4.5% MORE genset power, so it FLATTERS the only candidate it touches (S4'). The evidence is search-summary plus one fetched secondary page - the rating STRUCTURE is standard and not in dispute, the 0.90 ratio is an industry rule of thumb rather than a figure read out of the standard.

**Why this is not self-resolved.** R18 is a ruling; only the lead amends it.

**Asks.** Ratify the PRP basis for Vehicle One, or direct WS9 to carry R18's 0.861 and re-run S4'. Both numbers are exported so the bracket is readable either way.

**Materiality:** low - it touches one candidate and moves its climb rate, not its ranking

### ESC-WS9-5 - Predictive energy management is a ZERO-MASS lever the incumbent can fit too - and it turns out to be worth almost nothing

**Cites:** D8 ('zero-mass levers first'); R29 (the incumbent is CONCEDED near-optimal on the control duty); assignment ('predictive energy management (zero mass)')

**Finding.** The assignment gives predictive energy management to S6 alone. It costs no mass, needs no hardware beyond a map and a controller, and can be fitted to the RULER as easily as to a new engine - so reporting S6-with-preview against a ruler-without-preview would compare two control strategies and call the difference an engine. WS9 therefore measured the same lever ON THE RULER (bracket S0R-PCC). THE MEASUREMENT DOES NOT SUPPORT THE CONCERN THAT PROMPTED IT: on the design duty preview is worth +0.03% (median) / -0.09% (ensemble-min), and on the control duty -0.22% / -0.35%. The reason is physical and worth recording: this integrator's driver ALREADY cuts fuel on overrun and already governs its own descent speed against its retarding capability, so the crest half of the law is largely already there; and the pre-boost half buys kinetic energy at an aerodynamic cost that scales with the cube of speed, which on a corridor averaging over 90 km/h is a poor trade. The consequence for the trial is that S6's margin is its ENGINE and essentially nothing else, which makes ESC-WS9-1 the only question about S6 that matters.

**Why this is not self-resolved.** Whether the ruler carries preview is a baseline-specification decision, exactly as ESC-WS8-6 was for the retarder - and the fact that WS9's particular preview law is worth nothing does not establish that a better one would be.

**Asks.** Confirm the ruler's control specification: S0R without preview (as run), or S0R-PCC as the ruler of record - the two are within 0.03 pp of each other on the design duty, so the choice is presentational rather than material AS MODELLED. If the lead wants preview credited properly, the ask is a SEPARATE one: a preview law tuned against this duty rather than the symmetric +/-6% band WS9 declared before measuring.

**Materiality:** low as measured - the lever is worth under half a point on either duty, and it is reported that way rather than left as an open worry

### ESC-WS9-6 - R30's waste-heat cab path partially disarms the cold wall for engine-carrying candidates and not for S4'

**Cites:** R30 (THE COLD WALL); ESC-WS8-6 precedent on accessory asymmetry; WS8 finding F2

**Finding.** R30 orders preconditioning and a coolant/waste-heat cab path to be MODELLED, and the conventional truck's free cab heat to be charged to the others. WS9 models both. The consequence is an asymmetry that is physical and large: S5, S6 and S7 run an engine for most of the mission, so their cab heat is free and their packs are preconditioned from coolant at no fuel cost, while S4' runs its sustainer for a minority of the mission and must heat its cab and its pack from the bus. The cold corner therefore stops being a common-mode penalty and becomes an architecture-dependent one. That is R30's intended effect - but the SPLIT of WS8's 3.2 kW cold delta into 2.2 kW of cab heat and 1.0 kW of battery thermal is WS9-declared, and it decides how much of the effect there is.

**Why this is not self-resolved.** The split is a modelling convention that changes a corner every candidate is judged on; WS9 declares it and puts it up.

**Asks.** Confirm the 2.2 / 1.0 kW split, or supply one. Note that the pack-thermal half is no longer a flat allowance in WS9 - it is computed from a modelled pack temperature - so only the cab-heat half is a declared constant.

**Materiality:** medium - it moves the cold corner, which was binding for all four WS8 candidates

### ESC-WS9-7 - S5 has no launch device on the engine side: an inverter or machine fault is a tow, not a limp-home

**Cites:** R22(c) (Vehicle Zero's genset-or-pack-fault = tow asymmetry); WS8 section 6.5 and the S3 precedent; assignment ('2-speed dog box (no synchros, no launch clutch, no power-shift)')

**Finding.** The assignment specifies S5 with NO LAUNCH CLUTCH. A dog box cannot slip, so below the low gear's coupling floor (25.4 km/h for S5 as run) the engine cannot be connected at all and the machine is the ONLY prime mover. With the machine, its inverter or its buffer unavailable, the combination cannot be started from rest and cannot be recovered under its own power. This is S3's fault-limp finding in a milder form - milder because S5's engine CAN drive the truck once it is rolling above the coupling floor, so a fault at speed is a limp-home and only a fault at rest is a tow.

**Why this is not self-resolved.** Adding a launch device would be WS9 rewriting the candidate the assignment specified.

**Asks.** Confirm S5's specification, or authorise a launch device (a slipping clutch or a torque converter) and its mass for a re-run. Note the direction: a launch device would ADD mass to a candidate that is already losing on payload.

**Materiality:** medium - it is a capability finding, not a fuel one, and capability findings outlived fuel findings in WS8

### ESC-WS9-9 - The metric of record is blind to trip time, and on the design duty the spread is not small

**Cites:** Assignment: 'metric = primary energy per PAYLOAD tonne-km'; ESC-3 as ruled in R27; D13 (per-km efficiency flatters, per-payload judges)

**Finding.** D13 taught the program that a per-km metric flatters and a per-payload metric judges. There is a third denominator the trial does not carry: TIME. Every candidate here completes the same mission over the same road, but not at the same speed - the integrator gives a candidate that cannot hold the demanded force the speed its envelope supports, and charges it the extra time in accessory energy alone. The worst case in this trial is `S5/payload_plus20/GH-REG-165` at +15.7% of the ruler's trip time on the same duty. An operator paying a driver by the hour and a shipper paying by the tonne-km are looking at two different numbers, and only one of them is in this report.

**Why this is not self-resolved.** Adding a time or productivity term to the metric of record is a program-level metric decision, exactly as ESC-3 was.

**Asks.** Rule on whether Vehicle One's metric acquires a productivity term (payload tonne-km per hour, or energy per payload tonne-km at matched trip time), or whether trip time stays a reported side quantity. The full (candidate, corner, duty) table is exported at `sanity.trip_time_the_metric_cannot_see` either way.

**Materiality:** medium - it does not move a margin as computed, and it would change the RANKING if ruled in

### ESC-WS9-8 - WS9 ran against WS8's round-2 CODE before round 2's ARTIFACTS existed

**Cites:** R26 (errata order: WS8_semi_architecture/R2_DIRECTIVE.md); assignment ('its r2 outputs when they land (build to hot-swap; state vintages)')

**Finding.** When WS9 ran, WS8's round-2 corrections were present in its CODE - the cold-charge-acceptance wiring (F2), the ambient derate (F11), the one spin rule (F5), the duty-averaged correction pricing (F6), the errata switches - but results_ws8.json and REPORT_WS8.md were still at their round-1 vintage, so round 2 had not regenerated. WS9 therefore inherits r2's MODELS and none of its NUMBERS, which is sufficient because WS9 reads no WS8 numeric artifact at all and re-derives its own ruler (sanity.no_ws8_artifact_read). Every inherited source file is sha256-pinned in `inherited_vintage`, and the r2 fingerprint records the code round as 'r2'.

**Why this is not self-resolved.** Whether WS9's implementations of the r2 rules match r2's own is r2's adjudication to settle, not WS9's.

**Asks.** When r2 closes, compare the r2 concordance table in section 12 field by field and confirm that WS9's three own implementations - the spin rule applied to the machine's shaft rather than the vehicle's force channels, the correction pricing on WS9's own energy keys, and the pack temperature as a STATE rather than the corner's ambient - are consistent with r2's. If any differs, WS9 re-runs against r2: the pin makes that a one-flag operation.

**Materiality:** medium for the record, low for the numbers

---

## 14. Heat ledger for WS6 (rule 7)

component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation (inherited from ws8_params, r2)

**Rows are booked by PHYSICAL LOCATION**, which is what WS8's finding F1 said its own ledger did not do:

| row | where the heat goes |
|---|---|
| `engine_coolant_kW` | radiator / charge-air cooler |
| `hydraulic_retarder_coolant_kW` | the SAME coolant circuit - a secondary hydrodynamic retarder rejects through a heat exchanger into the engine cooling system, so WS6 must add this row to the coolant one and size one package for the sum |
| `engine_exhaust_kW` | exhaust and surface radiation |
| `compression_brake_exhaust_kW` | exhaust - a compression brake is an exhaust-side device and its heat does NOT go to the resistor bank (F1(b)) |
| `traction_machine_inverter_kW` | machine jacket and inverter cold plate |
| `generator_rectifier_kW` | generator jacket and rectifier |
| `pack_kW` | pack coolant loop |
| `brake_resistor_kW` | air, through a grid resistor bank |
| `friction_brake_kW` | foundation brakes, to air - a row WS8's ledger did not have at all (F1(c)) |
| `driveline_kW` | gearbox and axle oil |

Worst-case rejection by component, an explicit max over the enumerated case set with the governing case labelled (R14). The case set INCLUDES a pack-saturated descent and the simulated peaks over every (corner, duty, seed) run - the member WS8's r1 ledger did not have, and the reason it understated its own sizing case.

**THE TWO CLASSES ARE NOT INTERCHANGEABLE AND WS6 MUST NOT SIZE ONE THING ON BOTH. The four analytic cases are SUSTAINED - the vehicle holds that speed on that grade indefinitely, and they are what a cooling package and a resistor bank are sized on. `simulated_peak_over_all_runs` is a TRANSIENT PEAK taken over every (corner, duty, seed) run: the friction-brake row there is a single service stop lasting seconds, not a duty. Both are exported - `worst_case` over the full set and `worst_case_sustained` over the sustained set alone - so WS6 can size thermal capacity on the second and structural or energy limits on the first. WS8 r1's finding F1 was that its ledger's governing case sat OUTSIDE its enumerated set; the answering risk is putting a transient inside it without saying so, and this is where that is said.**

SUSTAINED cases only - what a cooling package and a resistor bank are sized on:

| candidate | engine coolant | hydraulic retarder coolant | engine exhaust | compression brake exhaust | traction machine inverter | generator rectifier | pack | brake resistor | friction brake |
|---|---|---|---|---|---|---|---|---|---|
| **S0R** | 207 (climb_6pct) | 350 (descent_6pct_pack_capable) | 286 (climb_6pct) | 118 (descent_6pct_pack_capable) | 0 | 0 | 0 | 0 | 0 |
| **S5** | 155 (climb_6pct) | 0 | 214 (climb_6pct) | 219 (descent_6pct_pack_capable) | 20 (descent_6pct_pack_capable) | 0 | 4 (descent_6pct_pack_capable) | 154 (descent_6pct_pack_saturated) | 79 (descent_6pct_pack_saturated) |
| **S5-13L** | 71 (cruise_95kmh_flat) | 0 | 98 (cruise_95kmh_flat) | 200 (descent_6pct_pack_capable) | 21 (descent_6pct_pack_capable) | 0 | 5 (descent_6pct_pack_capable) | 164 (descent_6pct_pack_saturated) | 87 (descent_6pct_pack_saturated) |
| **S6** | 180 (climb_6pct) | 350 (descent_6pct_pack_capable) | 249 (climb_6pct) | 118 (descent_6pct_pack_capable) | 0 | 0 | 0 | 0 | 0 |
| **S7** | 215 (climb_6pct) | 350 (descent_6pct_pack_capable) | 296 (climb_6pct) | 118 (descent_6pct_pack_capable) | 0 | 0 | 0 | 0 | 0 |
| **S4p** | 124 (climb_6pct) | 0 | 171 (climb_6pct) | 0 | 39 (climb_6pct) | 9 (climb_6pct) | 7 (climb_6pct) | 324 (descent_6pct_pack_saturated) | 118 (descent_6pct_pack_saturated) |

FULL case set, sustained AND the transient simulated peak:

| candidate | engine coolant | hydraulic retarder coolant | engine exhaust | compression brake exhaust | traction machine inverter | generator rectifier | pack | brake resistor | friction brake |
|---|---|---|---|---|---|---|---|---|---|
| **S0R** | 207 (climb_6pct) | 350 (descent_6pct_pack_capable) | 286 (climb_6pct) | 304 (simulated_peak_over_all_runs) | 0 | 0 | 0 | 0 | 834 (simulated_peak_over_all_runs) |
| **S5** | 155 (climb_6pct) | 0 | 214 (climb_6pct) | 238 (simulated_peak_over_all_runs) | 20 (descent_6pct_pack_capable) | 0 | 4 (descent_6pct_pack_capable) | 170 (simulated_peak_over_all_runs) | 813 (simulated_peak_over_all_runs) |
| **S5-13L** | 71 (cruise_95kmh_flat) | 0 | 98 (cruise_95kmh_flat) | 284 (simulated_peak_over_all_runs) | 21 (descent_6pct_pack_capable) | 0 | 5 (descent_6pct_pack_capable) | 180 (simulated_peak_over_all_runs) | 814 (simulated_peak_over_all_runs) |
| **S6** | 180 (climb_6pct) | 350 (descent_6pct_pack_capable) | 249 (climb_6pct) | 304 (simulated_peak_over_all_runs) | 0 | 0 | 0 | 0 | 790 (simulated_peak_over_all_runs) |
| **S7** | 215 (climb_6pct) | 350 (descent_6pct_pack_capable) | 296 (climb_6pct) | 304 (simulated_peak_over_all_runs) | 0 | 0 | 0 | 0 | 832 (simulated_peak_over_all_runs) |
| **S4p** | 124 (climb_6pct) | 0 | 171 (climb_6pct) | 0 | 39 (climb_6pct) | 9 (climb_6pct) | 7 (climb_6pct) | 350 (simulated_peak_over_all_runs) | 827 (simulated_peak_over_all_runs) |

The two coolant rows must be **added** by WS6: a secondary hydrodynamic retarder rejects through a heat exchanger into the engine cooling system, so one package sizes for the sum.

---

## 15. Machine-readable interface (R14)

Every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline. This block is byte-identical to `results_ws9.json['interface_ws9']`; `verify_ws9.py` asserts it.

```json
{
 "_convention": "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); stochastic extrema are 8-seed ensemble envelopes (rule 4); every worst-case field is an explicit max/min over an ENUMERATED case set with the governing case labelled inline (R14)",
 "metric_of_record": "metric of record: PRIMARY ENERGY per payload tonne-km [MJ_primary/(t.km)] (assignment; ESC-3 as ruled in R27). The diesel well-to-tank factor multiplies every candidate's fuel term identically, so for every candidate that burns only diesel the primary-energy margin and the tank-energy margin are the same number to machine precision - asserted in the sanity block, not claimed. The metric therefore changes exactly one thing in this trial: how S4', the only candidate that imports grid energy, is scored against the rest. Tank energy per payload tonne-km is reported alongside throughout, so every WS9 number is directly comparable with WS8's.",
 "duties": {
  "design": "GH-REG-165",
  "control": "LH-520",
  "gating": "ADVANCE/KILL is read on the DESIGN duty; the control duty is reported alongside and NEVER gates",
  "no_fleet_average": "assignment: 'Report every candidate on both, per-class, never only as a fleet average.' WS9 reports no fleet blend anywhere. Every headline is per duty class."
 },
 "gcw_kg": 36300.0,
 "vehicle": {
  "CdA_m2": 5.5,
  "Crr": 0.0055,
  "r_dyn_m": 0.5,
  "provisional_per_E13_precedent": true
 },
 "inherited_vintage": {
  "ws8_source_files": {
   "ws8_params.py": {
    "sha256": "d729fc7cb7323dbfbe725e839519fcf4987e9fec693dadaa8f8b894304cc6353",
    "bytes": 15812
   },
   "ws8_physics.py": {
    "sha256": "79f93610de6fd1e5d42dfcb50dbc4a3d12ce0b3e2486c84bde14046a95309b9b",
    "bytes": 16544
   },
   "ws8_cycles.py": {
    "sha256": "bd5b444294b5034b35f653f317aa1a710dfcb2c7c21a9085d1820c30ce05e6ff",
    "bytes": 14784
   },
   "ws8_engine.py": {
    "sha256": "61cc29d04c6a56a3076ee34d866a566c0beaa80b14a21881c5ff4ad9f3dd85de",
    "bytes": 18002
   },
   "ws8_electric.py": {
    "sha256": "74a932dbc795698986d32105652cc62dbeb6629bad4c3f6b61364aac538f9f6d",
    "bytes": 18592
   },
   "ws8_candidates.py": {
    "sha256": "e3a741f4097f13d8d79545e9196e660ccec829646431d133f5ddaecce0a07c67",
    "bytes": 106340
   },
   "ws8_whr.py": {
    "sha256": "674f91016f31cd29cac55cfdd71a6470d079b5699532809def2682dea49fdf5f",
    "bytes": 5986
   }
  },
  "ws8_artifacts_hashed_but_not_read": {
   "results_ws8.json": {
    "sha256": "c1b21b0b91b14d4d4c25dc25e501bc4afe1a332b31bcfd8b211e74a7e87d706f",
    "bytes": 3036230
   },
   "REPORT_WS8.md": {
    "sha256": "9cbfa9336075d6dd50187585d0f1f8e46c6013ebabef7f8199e1b4f69af04106",
    "bytes": 176516
   },
   "R2_DIRECTIVE.md": {
    "sha256": "e3040204e8f70f0fa431ad4cfdb2af3514a22b4df7dee49a296aece00f25da3d",
    "bytes": 2179
   },
   "FINDINGS_WS8_r1.md": {
    "sha256": "b3db6878367b39f13ce2d430181ffcccd6e8c078308caf5d534b40c8656c3ce8",
    "bytes": 28937
   }
  },
  "ws8_code_round_fingerprint": {
   "cold_charge_acceptance_wired": true,
   "derated_engine_present": true,
   "one_spin_rule_present": true,
   "errata_switches_present": true,
   "hot_altitude_corner_present": true,
   "heat_split_in_params": true,
   "code_round": "r2"
  },
  "ws9_own_files": {
   "run_ws9.py": {
    "sha256": "23c7d3c4b344eb0f930e969aaeb781f8b96bf0a285c6953fcada5cc9addc4c2f"
   },
   "ws9_params.py": {
    "sha256": "927e8584f5c46dbc8b8350e6c6fc8b4ca3f0c99f0a4be6bf6980a395e6f76fb5"
   },
   "ws9_duty.py": {
    "sha256": "86e9d6c18c7b70cc63d66d775d3678220d7e843e04f6979b9b87403127dadc11"
   },
   "ws9_engines.py": {
    "sha256": "407a00ca47413b82427cb2eafbce65fd8f3df0d7b0031484369756af2a77d983"
   },
   "ws9_fuels.py": {
    "sha256": "54dd729fe643875af2592b6a497fe515458a65654455c147561ec6fc7e105ef4"
   },
   "ws9_storage.py": {
    "sha256": "378fef25a1206e4e9ffe0ca9a320bac50b15c5256ddf3a173449189dfe8c4e33"
   },
   "ws9_thermal.py": {
    "sha256": "1b50fe728f3131548ed1def6c3111932fd9db08cb864d0a58ff12eae3037bef8"
   },
   "ws9_walls.py": {
    "sha256": "7a9962cccec308b5bbd236eabc377c1f6cef0be7bae05d1e64b8823f11681fd7"
   },
   "ws9_candidates.py": {
    "sha256": "0cd9b1fe33b955c2d7a9a923c28e7b20f420f7083416bad8a152e13e7509d67e"
   },
   "ws9_corrections.py": {
    "sha256": "8d467421c27e60a38765ece960e63b9c3eee204145a0d352955c5611e3cd4c8c"
   },
   "ws9_primemover.py": {
    "sha256": "532f152c1232fa3fadb8ec0943a7a85fec8f4ea01597ae21656056149990bd8e"
   },
   "ws9_blocks.py": {
    "sha256": "15c2dc9e548accd0bfe5138364caae289e042cd256421ad667740e7f6bb5deb1"
   },
   "make_report_ws9.py": {
    "sha256": "326dff4180de3f928996293b70227f7f3d9005bf9508b66c2ddf4b83aced15a2"
   },
   "verify_ws9.py": {
    "sha256": "8c9789e294333def164dad804f31d71f326000baefae02ec788d0705b9e28727"
   },
   "check_determinism_ws9.py": {
    "sha256": "ffcb0dc03e36efaff5c92ab38f2c4fc387abfbcf3b9f8b9683a3e2c12b1fe86a"
   }
  },
  "statement": "WS9 imports WS8's MODELS read-only and reads NO WS8 numeric artifact (asserted in sanity.no_ws8_artifact_read). The hashes above pin exactly which WS8 the models came from. If WS8's round 2 regenerates its artifacts after this run, none of WS9's numbers move: WS9 re-derives its own ruler from the same models. If WS8's round 2 changes its CODE after this run, the hashes above will not match and verify_ws9.py says so - that is the hot-swap signal the assignment asks for."
 },
 "candidates": {
  "S0R": {
   "title": "Conventional 13 L diesel + 12-speed AMT with a direct top gear, + hydraulic retarder (ESC-6)",
   "payload_kg": 20655.0,
   "powertrain_mass_kg": 2975.0,
   "payload_delta_vs_ruler_kg": 0.0,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.9011416304049882,
     "median": 0.9196360933103048,
     "max": 1.0217909137396843
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.7572618742899059,
     "median": 0.7728034397565587,
     "max": 0.8586478266720037
    },
    "g_CO2_per_payload_tkm": {
     "min": 66.77789936384424,
     "median": 68.14840688564695,
     "max": 75.7184536884996
    },
    "fuel_L_per_100km_median": 44.82570724796605,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": null
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.7540881085462171,
     "median": 0.8116309504973724,
     "max": 0.9159017894006041
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6336874861732917,
     "median": 0.6820428155440106,
     "max": 0.7696653692442051
    },
    "g_CO2_per_payload_tkm": {
     "min": 55.88069413832311,
     "median": 60.1448297406223,
     "max": 67.87168127197853
    },
    "fuel_L_per_100km_median": 39.561226059999385,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": null
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": 2.0805731298264652e-05,
    "max": 0.0003223544494668073,
    "median": 0.0001506754867057247,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "n/a (S0R is the ruler)"
  },
  "S5": {
   "title": "Minimal transmission - 2-speed dog box, motor-synchronised shifts, torque-fill through the shift",
   "payload_kg": 19970.047033385985,
   "powertrain_mass_kg": 3659.9529666140143,
   "payload_delta_vs_ruler_kg": -684.9529666140152,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.8596937920124323,
     "median": 0.8862776636315961,
     "max": 0.9745500839828675
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.7224317579936406,
     "median": 0.7447711459089044,
     "max": 0.818949650405771
    },
    "g_CO2_per_payload_tkm": {
     "min": 63.706462546766915,
     "median": 65.67642491870625,
     "max": 72.21773496801671
    },
    "fuel_L_per_100km_median": 41.767149344304904,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": 1.902903061223159,
     "median": 4.640239852064495,
     "max": 5.232638373030178
    }
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.7703287732024954,
     "median": 0.8387256415758586,
     "max": 0.9685411824251566
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6473351035315088,
     "median": 0.7048114635091249,
     "max": 0.813900153298451
    },
    "g_CO2_per_payload_tkm": {
     "min": 57.08418694503262,
     "median": 62.15264570770893,
     "max": 71.77245332751836
    },
    "fuel_L_per_100km_median": 39.52618978013468,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": -5.747274831617208,
     "median": -3.487308106511131,
     "max": -2.1536826363152897
    }
   },
   "worst_case_margin_pct_design_duty": {
    "rule": "min over the enumerated corner set (R28), ensemble-min within each corner",
    "cases": {
     "nominal": 1.902903061223159,
     "payload_plus20": 1.3894279854209202,
     "payload_minus20": 2.683391574213184,
     "grade_heavy": 1.902903061223159,
     "cold_minus10C": 0.2663407984308728,
     "hot_alt_2000m_45C": 0.4905046774407326
    },
    "value": 0.2663407984308728,
    "governing_case": "cold_minus10C"
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": -0.0015551852585081428,
    "max": 0.18940735142819753,
    "median": 0.041199655525810765,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "KILL"
  },
  "S5-13L": {
   "title": "Minimal transmission with the 13 L engine - the other end of the ratio law",
   "payload_kg": 19706.323484784123,
   "powertrain_mass_kg": 3923.6765152158787,
   "payload_delta_vs_ruler_kg": -948.6765152158769,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.8399680439881233,
     "median": 0.8544340658340954,
     "max": 0.9488637074117431
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.7058554991496835,
     "median": 0.7180118200286517,
     "max": 0.7973644600098682
    },
    "g_CO2_per_payload_tkm": {
     "min": 62.24471228243625,
     "median": 63.31669754915993,
     "max": 70.31428027031565
    },
    "fuel_L_per_100km_median": 39.734715333458425,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": 5.358821363140897,
     "median": 7.073904876803695,
     "max": 9.175470462173504
    }
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.7552612182467243,
     "median": 0.8145272748772174,
     "max": 0.9285680500811481
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6346732926443062,
     "median": 0.6844767015774937,
     "max": 0.7803092857824774
    },
    "g_CO2_per_payload_tkm": {
     "min": 55.967625869007904,
     "median": 60.35945799819754,
     "max": 68.81029763649099
    },
    "fuel_L_per_100km_median": 37.87888462404559,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": -1.3829278233895805,
     "median": -0.6599972999598359,
     "max": -0.04531846231682578
    }
   },
   "worst_case_margin_pct_design_duty": {
    "rule": "min over the enumerated corner set (R28), ensemble-min within each corner",
    "cases": {
     "nominal": 5.358821363140897,
     "payload_plus20": 4.88720878223571,
     "payload_minus20": 5.694386913689942,
     "grade_heavy": 5.358821363140897,
     "cold_minus10C": 3.9303556282370424,
     "hot_alt_2000m_45C": 4.8452562824242404
    },
    "value": 3.9303556282370424,
    "governing_case": "cold_minus10C"
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": -0.00720551031400648,
    "max": 0.15729978398306227,
    "median": 0.015906638864144087,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "ADVANCE"
  },
  "S6": {
   "title": "Zero-mass stack - opposed-piston-class engine + predictive energy management, mechanical drive as S0",
   "payload_kg": 20655.0,
   "powertrain_mass_kg": 2975.0,
   "payload_delta_vs_ruler_kg": 0.0,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.832846124397749,
     "median": 0.8506270807377029,
     "max": 0.9439765432464372
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6998706927712176,
     "median": 0.714812672888826,
     "max": 0.7932575993667539
    },
    "g_CO2_per_payload_tkm": {
     "min": 61.71695192420082,
     "median": 63.034585993030525,
     "max": 69.95212348408583
    },
    "fuel_L_per_100km_median": 41.46200956629309,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": 7.501926011481562,
     "median": 7.613814463880127,
     "max": 7.761723646324153
    }
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.698881025562639,
     "median": 0.7518030335467822,
     "max": 0.8466873375464214
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.5872949794644026,
     "median": 0.6317672550813297,
     "max": 0.7115019643247239
    },
    "g_CO2_per_payload_tkm": {
     "min": 51.789646840916646,
     "median": 55.71136170133147,
     "max": 62.74263657523637
    },
    "fuel_L_per_100km_median": 36.645041375653946,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": 7.26221115026216,
     "median": 7.389343730969061,
     "max": 7.556973100738105
    }
   },
   "worst_case_margin_pct_design_duty": {
    "rule": "min over the enumerated corner set (R28), ensemble-min within each corner",
    "cases": {
     "nominal": 7.501926011481562,
     "payload_plus20": 7.538760625618382,
     "payload_minus20": 7.286067575714271,
     "grade_heavy": 7.501926011481562,
     "cold_minus10C": 7.467500742378921,
     "hot_alt_2000m_45C": 7.539213670415082
    },
    "value": 7.286067575714271,
    "governing_case": "payload_minus20"
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": 2.0867864232822752e-05,
    "max": 0.0003221567747289014,
    "median": 0.00015073880799060024,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "ADVANCE"
  },
  "S7": {
   "title": "Marginal-mass electrification - one EXISTING trailer axle motorised, tractor untouched",
   "payload_kg": 19845.51109083291,
   "powertrain_mass_kg": 3784.48890916709,
   "payload_delta_vs_ruler_kg": -809.4889091670884,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.8260761848538767,
     "median": 0.8644175041299702,
     "max": 0.9757170188979453
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6941816679444343,
     "median": 0.726401263974765,
     "max": 0.8199302679814666
    },
    "g_CO2_per_payload_tkm": {
     "min": 61.21527457814718,
     "median": 64.0565069368668,
     "max": 72.30420912445778
    },
    "fuel_L_per_100km_median": 40.48291567612735,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": 4.509131390991899,
     "median": 5.90484586790757,
     "max": 8.385446162678099
    }
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.7493977370081869,
     "median": 0.8133499942404216,
     "max": 0.9292162342102549
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.6297459974858715,
     "median": 0.6834873901180014,
     "max": 0.7808539783279452
    },
    "g_CO2_per_payload_tkm": {
     "min": 55.53312040742705,
     "median": 60.27221718583864,
     "max": 68.8583304573954
    },
    "fuel_L_per_100km_median": 38.091291620886615,
    "grid_kWh_median": 0.0,
    "margin_vs_ruler_pct": {
     "min": -1.4536978706378807,
     "median": -0.21146373999599255,
     "max": 0.635356575883736
    }
   },
   "worst_case_margin_pct_design_duty": {
    "rule": "min over the enumerated corner set (R28), ensemble-min within each corner",
    "cases": {
     "nominal": 4.509131390991899,
     "payload_plus20": 4.443342141370186,
     "payload_minus20": 4.213724428363932,
     "grade_heavy": 4.509131390991899,
     "cold_minus10C": 3.5839250592339016,
     "hot_alt_2000m_45C": 4.851335987915283
    },
    "value": 3.5839250592339016,
    "governing_case": "cold_minus10C"
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": 0.01236004766782344,
    "max": 0.02547777536883412,
    "median": 0.019065441596583355,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "ADVANCE"
  },
  "S4p": {
   "title": "Range-extended BEV re-posed - cited external energy cell (ESC-1c), electricity term (ESC-3)",
   "payload_kg": 20134.370309324804,
   "powertrain_mass_kg": 3495.629690675194,
   "payload_delta_vs_ruler_kg": -520.6296906751959,
   "GH-REG-165": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.7193824732064176,
     "median": 0.7740821497541438,
     "max": 0.8996465869975654
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.3929106021145668,
     "median": 0.43814442729059366,
     "max": 0.5441791367720779
    },
    "g_CO2_per_payload_tkm": {
     "min": 43.97480289495086,
     "median": 47.995948741949206,
     "max": 57.32359917779742
    },
    "fuel_L_per_100km_median": 24.77355024497846,
    "grid_kWh_median": 110.8091471301623,
    "margin_vs_ruler_pct": {
     "min": 11.953945283686181,
     "median": 15.828826579046801,
     "max": 20.21812814655453
    }
   },
   "LH-520": {
    "MJ_primary_per_payload_tkm": {
     "rule": "8-seed ensemble",
     "min": 0.756954379209227,
     "median": 0.8350886837392899,
     "max": 0.978253631088258
    },
    "MJ_tank_per_payload_tkm": {
     "min": 0.5689764047359631,
     "median": 0.6345973109423035,
     "max": 0.7548959346955162
    },
    "g_CO2_per_payload_tkm": {
     "min": 53.13249247045012,
     "median": 58.92084716612018,
     "max": 69.52953947407174
    },
    "fuel_L_per_100km_median": 35.88138382855769,
    "grid_kWh_median": 110.6779544941615,
    "margin_vs_ruler_pct": {
     "min": -6.807699516392367,
     "median": -2.7496110571916894,
     "max": -0.380097581506188
    }
   },
   "worst_case_margin_pct_design_duty": {
    "rule": "min over the enumerated corner set (R28), ensemble-min within each corner",
    "cases": {
     "nominal": 11.953945283686181,
     "payload_plus20": 10.954709592524809,
     "payload_minus20": 12.92604218651458,
     "grade_heavy": 11.953945283686181,
     "cold_minus10C": 7.3986780758134145,
     "hot_alt_2000m_45C": 13.574810976674046
    },
    "value": 7.3986780758134145,
    "governing_case": "cold_minus10C"
   },
   "fuel_correction_share": {
    "rule": "SIGNED, min AND max over the enumerated (duty, seed) case set - r1 finding F4: exporting the max of a signed quantity hid a credit",
    "min": 0.15641140891795804,
    "max": 0.30541027664974385,
    "median": 0.22506735211915718,
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up (NEGATIVE where the pack finished fuller than it started) - rather than fuel the model watched it burn. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "verdict": "ADVANCE"
  }
 },
 "unserved_energy_kWh": {
  "rule": "max over the enumerated (candidate, corner, duty) case set",
  "value": 257.1027195462594,
  "governing_case": "S4p/grade_heavy/LH-520",
  "cases_over_1kWh": {
   "S4p/cold_minus10C/GH-REG-165": 50.332093193992584,
   "S4p/cold_minus10C/LH-520": 228.80051594985525,
   "S4p/grade_heavy/GH-REG-165": 45.80077112507308,
   "S4p/grade_heavy/LH-520": 257.1027195462594,
   "S4p/hot_alt_2000m_45C/GH-REG-165": 44.033549724517286,
   "S4p/hot_alt_2000m_45C/LH-520": 166.73532750867534,
   "S4p/nominal/GH-REG-165": 45.80077112507308,
   "S4p/nominal/LH-520": 190.09625338998958,
   "S4p/payload_minus20/GH-REG-165": 35.00430323600033,
   "S4p/payload_minus20/LH-520": 153.68611499025826,
   "S4p/payload_plus20/GH-REG-165": 57.90263671377851,
   "S4p/payload_plus20/LH-520": 226.76659897999306,
   "S5-13L/cold_minus10C/GH-REG-165": 48.8987128024926,
   "S5-13L/cold_minus10C/LH-520": 4.509302182004188,
   "S5-13L/grade_heavy/GH-REG-165": 44.83821650694114,
   "S5-13L/hot_alt_2000m_45C/GH-REG-165": 49.624562950764734,
   "S5-13L/hot_alt_2000m_45C/LH-520": 3.64452708493555,
   "S5-13L/nominal/GH-REG-165": 44.83821650694114,
   "S5-13L/nominal/LH-520": 2.7419648833958163,
   "S5-13L/payload_minus20/GH-REG-165": 28.06526298448972,
   "S5-13L/payload_minus20/LH-520": 3.0855945856092832,
   "S5-13L/payload_plus20/GH-REG-165": 57.49881288948204,
   "S5-13L/payload_plus20/LH-520": 3.9634099821053224,
   "S5/cold_minus10C/GH-REG-165": 58.36525318017936,
   "S5/cold_minus10C/LH-520": 13.068097682522401,
   "S5/grade_heavy/GH-REG-165": 54.22142906188656,
   "S5/grade_heavy/LH-520": 7.322171157939376,
   "S5/hot_alt_2000m_45C/GH-REG-165": 59.88195936268821,
   "S5/hot_alt_2000m_45C/LH-520": 13.149623196212262,
   "S5/nominal/GH-REG-165": 54.22142906188656,
   "S5/nominal/LH-520": 10.324845872181223,
   "S5/payload_minus20/GH-REG-165": 37.06315896093076,
   "S5/payload_minus20/LH-520": 6.9729074939190525,
   "S5/payload_plus20/GH-REG-165": 67.54575384134117,
   "S5/payload_plus20/LH-520": 12.157708230208607,
   "S7/cold_minus10C/GH-REG-165": 2.563964974558626,
   "S7/cold_minus10C/LH-520": 6.65890981026506,
   "S7/grade_heavy/GH-REG-165": 3.4874307164817826,
   "S7/grade_heavy/LH-520": 13.506082623400092,
   "S7/hot_alt_2000m_45C/GH-REG-165": 2.741047284190653,
   "S7/hot_alt_2000m_45C/LH-520": 6.8051992383724995,
   "S7/nominal/GH-REG-165": 3.4874307164817826,
   "S7/nominal/LH-520": 9.11510499278463,
   "S7/payload_minus20/GH-REG-165": 2.9759293310140693,
   "S7/payload_minus20/LH-520": 7.241471264802146,
   "S7/payload_plus20/GH-REG-165": 4.037631498605952,
   "S7/payload_plus20/LH-520": 10.941128003866027
  },
  "meaning": "energy the prime movers and the buffer together could not deliver. It is charged back as fuel so every candidate completes the same mission, priced at the run's own DUTY-AVERAGED efficiency per r2's rule, and reported here RAW because a large value is a CAPABILITY finding, not a fuel one."
 },
 "advance_kill": {
  "nominal_pct": 3.0,
  "every_corner_pct": 0.0,
  "statistic": "ensemble_min",
  "duty": "GH-REG-165",
  "metric": "primary energy per payload tonne-km",
  "pre_committed": true,
  "text": "assignment, quoted verbatim: 'ADVANCE only if >=3% better than S0 on the DESIGN DUTY at nominal, ensemble-min, AND >=0% at every R28 corner; report the control-duty result alongside without it gating.'",
  "control_duty": "LH-520",
  "control_duty_gates": false
 },
 "advance_kill_result": {
  "S4p": "ADVANCE",
  "S5": "KILL",
  "S5-13L": "ADVANCE",
  "S6": "ADVANCE",
  "S7": "ADVANCE"
 },
 "advance_kill_robustness_ESC3": {
  "rule": "the SAME pre-committed criteria applied at each end of the +/-50% grid-factor sweep ESC-3 orders; a verdict that moves is reported, not smoothed",
  "cases": {
   "grid_factor_minus50pct": {
    "S4p": "ADVANCE",
    "S5": "KILL",
    "S5-13L": "ADVANCE",
    "S6": "ADVANCE",
    "S7": "ADVANCE"
   },
   "declared": {
    "S4p": "ADVANCE",
    "S5": "KILL",
    "S5-13L": "ADVANCE",
    "S6": "ADVANCE",
    "S7": "ADVANCE"
   },
   "grid_factor_plus50pct": {
    "S4p": "KILL",
    "S5": "KILL",
    "S5-13L": "ADVANCE",
    "S6": "ADVANCE",
    "S7": "ADVANCE"
   }
  },
  "candidates_whose_verdict_moves": [
   "S4p"
  ],
  "value": false,
  "governing_case": "S4p"
 },
 "etc_gate": {
  "threshold_pct": 2.5,
  "duty": "GH-REG-165",
  "net_margin_pct_min": 1.6673369396484603,
  "net_margin_pct_median": 1.7985580615277574,
  "mass_charge_kg": 85.0,
  "payload_penalty_pct": 0.4132231404958678,
  "fuel_gain_needed_to_clear_gate_pct": 2.9132231404958677,
  "verdict": "DROPPED"
 },
 "two_walls": {
  "wall1_single_ratio_infeasible": {
   "rule": "a single fixed ratio is feasible only if it holds 6% at GCW AND keeps the engine under 2,100 rpm at 105 km/h; solved in CLOSED FORM, not swept (F12)",
   "cases": {
    "ENG-11L": false,
    "ENG-13L": false
   },
   "ratio_ceiling": 3.7699111843077517,
   "governing_case": "6% grade at 36,300 kg GCW",
   "value": false
  },
  "wall1_two_speed_feasible": {
   "rule": "the SAME two tests, with two ratios and the contiguity constraint that a 2-speed lives or dies by",
   "cases": {
    "ENG-11L": true,
    "ENG-13L": true
   },
   "value": true,
   "governing_case": "6% grade at 36,300 kg GCW, contiguous engine band"
  },
  "ratio_law": {
   "statement": "with contiguity tight and Wall 2 tight, cruise engine speed x engine peak torque is a CONSTANT at fixed GCW and grade requirement: n_cruise = v * k * F_6% * (1+margin) * r_dyn / (T_peak * eta_low * span)",
   "constant_at_100kmh": 3445285.2736462606,
   "consequence": "a minimal transmission wants a BIG-TORQUE engine: torque is what buys back the ratio span, so downsizing the engine of a 2-speed truck raises its cruise engine speed in exact proportion. That inverts the usual downsizing instinct and is why S5 is run on two engines."
  },
  "wall2_payload_delta_kg": {
   "rule": "min over the enumerated candidate set - the biggest payload a candidate gives up to the ruler",
   "cases": {
    "S0R": 0.0,
    "S5": -684.9529666140152,
    "S5-13L": -948.6765152158769,
    "S6": 0.0,
    "S7": -809.4889091670884,
    "S4p": -520.6296906751959
   },
   "value": -948.6765152158769,
   "governing_case": "S5-13L"
  }
 },
 "prime_mover_at_the_pin": {
  "scope": "the only WS9 candidate with a series element is S4'; S5 drives mechanically through a dog box and S7 never touches the tractor's engine, so neither has a pinned point",
  "basis": {
   "range_km": 800.0,
   "torque_matched": "all three carry WS8's 7 L sustainer torque curve exactly; displacement follows from each fuel's knock-limited BMEP",
   "price": "OUT OF SCOPE (assignment; D12)",
   "duty_points": {
    "GH-REG-165": {
     "e_genset_bus_kWh_median": 120.54182716558057,
     "distance_km_median": 165.00024400958736,
     "bus_kWh_per_km": 0.7305554478972557,
     "mean_on_bus_kW_median": 103.93316121984526,
     "genset_on_fraction_median": 0.43430873239099693
    },
    "LH-520": {
     "e_genset_bus_kWh_median": 589.9838176665985,
     "distance_km_median": 520.0003921182928,
     "bus_kWh_per_km": 1.1345834091840175,
     "mean_on_bus_kW_median": 137.083961153008,
     "genset_on_fraction_median": 0.7345651153742536
    }
   }
  },
  "worst_case": {
   "best_pin_efficiency": {
    "rule": "max",
    "cases": {
     "diesel": 0.40639907059914965,
     "petrol": 0.38642507446280094,
     "natural gas (CNG)": 0.3817911551364529,
     "natural gas (LNG)": 0.3817911551364529
    },
    "value": 0.40639907059914965,
    "governing_case": "diesel"
   },
   "lowest_charged_mass": {
    "rule": "min",
    "cases": {
     "diesel": 946.0876614262361,
     "petrol": 1064.8313300641164,
     "natural gas (CNG)": 3624.617777295839,
     "natural gas (LNG)": 1205.4945056819759
    },
    "value": 946.0876614262361,
    "governing_case": "diesel"
   },
   "lowest_co2e_per_bus_kWh": {
    "rule": "min",
    "cases": {
     "diesel": 656.5823172111471,
     "petrol": 683.0046819744931,
     "natural gas (CNG)": 570.8814113516582,
     "natural gas (LNG)": 570.8814113516582
    },
    "value": 570.8814113516582,
    "governing_case": "natural gas (CNG)"
   }
  },
  "per_prime_mover": {
   "diesel": {
    "eta_at_pin": 0.40639907059914965,
    "engine_kg": 640.0,
    "aftertreatment_kg": 90.0,
    "fuel_plus_tank_kg": 216.08766142623614,
    "total_charged_kg": 946.0876614262361,
    "g_CO2e_per_bus_kWh": 656.5823172111471
   },
   "petrol": {
    "eta_at_pin": 0.38642507446280094,
    "engine_kg": 803.848786918531,
    "aftertreatment_kg": 30.0,
    "fuel_plus_tank_kg": 230.98254314558548,
    "total_charged_kg": 1064.8313300641164,
    "g_CO2e_per_bus_kWh": 683.0046819744931
   },
   "natural gas (CNG)": {
    "eta_at_pin": 0.3817911551364529,
    "engine_kg": 723.4639082266779,
    "aftertreatment_kg": 35.0,
    "fuel_plus_tank_kg": 2866.153869069161,
    "total_charged_kg": 3624.617777295839,
    "g_CO2e_per_bus_kWh": 570.8814113516582
   },
   "natural gas (LNG)": {
    "eta_at_pin": 0.3817911551364529,
    "engine_kg": 723.4639082266779,
    "aftertreatment_kg": 35.0,
    "fuel_plus_tank_kg": 447.030597455298,
    "total_charged_kg": 1205.4945056819759,
    "g_CO2e_per_bus_kWh": 570.8814113516582
   }
  }
 },
 "cold_wall_R30": {
  "rule": "min over the enumerated candidate set of the pack's charge acceptance at the -10 C corner's cold-soaked start, as a fraction of its warm value",
  "cases": {
   "S5": 1.0,
   "S5-13L": 1.0,
   "S7": 1.0,
   "S4p": 0.15
  },
  "value": 0.15,
  "governing_case": "S4p",
  "preconditioning": {
   "S5": {
    "t_pack_start_C": -10.0,
    "t_pack_end_C": 39.19215979896139,
    "seconds_to_reach_target": 782.9000000001095,
    "seconds_below_target": 846.7500000001239,
    "chg_limit_at_ambient_kW": 136.2704,
    "chg_limit_warm_kW": 136.2704,
    "collapse_factor": 1.0,
    "e_coolant_waste_heat_kWh": 1.0266162197454363,
    "e_electric_heater_kWh": 0.9682044057533398
   },
   "S5-13L": {
    "t_pack_start_C": -10.0,
    "t_pack_end_C": 35.17458963434551,
    "seconds_to_reach_target": 872.5500000001298,
    "seconds_below_target": 886.9500000001331,
    "chg_limit_at_ambient_kW": 176.0512,
    "chg_limit_warm_kW": 176.0512,
    "collapse_factor": 1.0,
    "e_coolant_waste_heat_kWh": 1.2119146652955923,
    "e_electric_heater_kWh": 1.2767525569698472
   },
   "S7": {
    "t_pack_start_C": -10.0,
    "t_pack_end_C": 58.63608478330286,
    "seconds_to_reach_target": 583.9500000000642,
    "seconds_below_target": 583.8500000000643,
    "chg_limit_at_ambient_kW": 72.3672,
    "chg_limit_warm_kW": 72.3672,
    "collapse_factor": 1.0,
    "e_coolant_waste_heat_kWh": 0.7365428466222603,
    "e_electric_heater_kWh": 0.40826095864007717
   },
   "S4p": {
    "t_pack_start_C": -10.0,
    "t_pack_end_C": 38.434381291056,
    "seconds_to_reach_target": 1947.9499999993238,
    "seconds_below_target": 1947.849999999324,
    "chg_limit_at_ambient_kW": 22.5,
    "chg_limit_warm_kW": 150.0,
    "collapse_factor": 0.15,
    "e_coolant_waste_heat_kWh": 0.0,
    "e_electric_heater_kWh": 5.141746005562954
   }
  },
  "note": "R30 modelled, not assumed: the pack temperature is a state, cold-soaked at ambient and warmed from engine coolant, its own losses, or a bus-fed heater"
 },
 "retarding_shortfall_kWh": {
  "rule": "max over the enumerated (candidate, corner, duty) case set",
  "cases": {
   "S5/nominal/GH-REG-165": 4.063246216013327,
   "S5/nominal/LH-520": 5.652815754075532,
   "S5-13L/nominal/GH-REG-165": 5.536592069138304,
   "S5-13L/nominal/LH-520": 6.868495670263848,
   "S5/payload_plus20/GH-REG-165": 3.3288000592379503,
   "S5/payload_plus20/LH-520": 12.61337319010894,
   "S5-13L/payload_plus20/GH-REG-165": 6.3861766693066215,
   "S5-13L/payload_plus20/LH-520": 13.80423998330491,
   "S5/payload_minus20/GH-REG-165": 3.7587474000132963,
   "S5/payload_minus20/LH-520": 0.26453365425834574,
   "S5-13L/payload_minus20/GH-REG-165": 4.449069670819753,
   "S5-13L/payload_minus20/LH-520": 1.1658112287361697,
   "S5/grade_heavy/GH-REG-165": 4.063246216013327,
   "S5/grade_heavy/LH-520": 7.088871014659634,
   "S5-13L/grade_heavy/GH-REG-165": 5.536592069138304,
   "S5-13L/grade_heavy/LH-520": 8.39369049944032,
   "S5/cold_minus10C/GH-REG-165": 3.718480386926369,
   "S5/cold_minus10C/LH-520": 4.171431928474119,
   "S5-13L/cold_minus10C/GH-REG-165": 4.877126180913324,
   "S5-13L/cold_minus10C/LH-520": 5.675710542552286,
   "S4p/cold_minus10C/GH-REG-165": 0.05398393335479765,
   "S4p/cold_minus10C/LH-520": 0.022373233855380894,
   "S5/hot_alt_2000m_45C/GH-REG-165": 2.776279205251017,
   "S5/hot_alt_2000m_45C/LH-520": 7.037324361831048,
   "S5-13L/hot_alt_2000m_45C/GH-REG-165": 4.9050666737049236,
   "S5-13L/hot_alt_2000m_45C/LH-520": 8.031125853875285
  },
  "value": 13.80423998330491,
  "governing_case": "S5-13L/payload_plus20/LH-520",
  "meaning": "energy the envelope granted as retarding force that neither the pack nor the resistor could actually absorb. The resistor sizing rule is written to make this zero at the enumerated descent case; a non-zero value elsewhere means the descent-speed governor let the candidate run faster than its sink supports, and it is reported rather than absorbed."
 },
 "power_limited_fraction": {
  "rule": "max over the enumerated (candidate, corner, duty) case set - the fraction of samples on which the candidate could not deliver the demanded tractive force and took the speed its envelope allowed instead",
  "cases": {
   "S0R/nominal/GH-REG-165": 0.19086388105613944,
   "S0R/nominal/LH-520": 0.19024879537732045,
   "S5/nominal/GH-REG-165": 0.3597165494719415,
   "S5/nominal/LH-520": 0.30570513288551404,
   "S5-13L/nominal/GH-REG-165": 0.26553252295482416,
   "S5-13L/nominal/LH-520": 0.1703563547629147,
   "S6/nominal/GH-REG-165": 0.1929693725353983,
   "S6/nominal/LH-520": 0.19438081346691855,
   "S7/nominal/GH-REG-165": 0.1802435083313607,
   "S7/nominal/LH-520": 0.17930603820174373,
   "S4p/nominal/GH-REG-165": 0.08567903538510985,
   "S4p/nominal/LH-520": 0.07143979263215773,
   "S0R/payload_plus20/GH-REG-165": 0.22682914496637507,
   "S0R/payload_plus20/LH-520": 0.22661904581454395,
   "S5/payload_plus20/GH-REG-165": 0.40894835326053536,
   "S5/payload_plus20/LH-520": 0.35493678988638183,
   "S5-13L/payload_plus20/GH-REG-165": 0.3082767006305788,
   "S5-13L/payload_plus20/LH-520": 0.21136242140968203,
   "S6/payload_plus20/GH-REG-165": 0.22913623036543712,
   "S6/payload_plus20/LH-520": 0.22979963501412315,
   "S7/payload_plus20/GH-REG-165": 0.21726459448207233,
   "S7/payload_plus20/LH-520": 0.21468921176241035,
   "S4p/payload_plus20/GH-REG-165": 0.10876182640888524,
   "S4p/payload_plus20/LH-520": 0.09460461485926143,
   "S0R/payload_minus20/GH-REG-165": 0.151860028815158,
   "S0R/payload_minus20/LH-520": 0.15125921006405538,
   "S5/payload_minus20/GH-REG-165": 0.2867887627716547,
   "S5/payload_minus20/LH-520": 0.260126779784167,
   "S5-13L/payload_minus20/GH-REG-165": 0.20656612350244616,
   "S5-13L/payload_minus20/LH-520": 0.13209088711626782,
   "S6/payload_minus20/GH-REG-165": 0.15214018246891614,
   "S6/payload_minus20/LH-520": 0.15766826727045088,
   "S7/payload_minus20/GH-REG-165": 0.14495916204252135,
   "S7/payload_minus20/LH-520": 0.14311364239689167,
   "S4p/payload_minus20/GH-REG-165": 0.06702096558636819,
   "S4p/payload_minus20/LH-520": 0.05662754164443654,
   "S0R/grade_heavy/GH-REG-165": 0.19086388105613944,
   "S0R/grade_heavy/LH-520": 0.320341814923367,
   "S5/grade_heavy/GH-REG-165": 0.3597165494719415,
   "S5/grade_heavy/LH-520": 0.4304128223533325,
   "S5-13L/grade_heavy/GH-REG-165": 0.26553252295482416,
   "S5-13L/grade_heavy/LH-520": 0.2945834133725643,
   "S6/grade_heavy/GH-REG-165": 0.1929693725353983,
   "S6/grade_heavy/LH-520": 0.3233682158850964,
   "S7/grade_heavy/GH-REG-165": 0.1802435083313607,
   "S7/grade_heavy/LH-520": 0.3067919868920803,
   "S4p/grade_heavy/GH-REG-165": 0.08567903538510985,
   "S4p/grade_heavy/LH-520": 0.12632730390393646,
   "S0R/cold_minus10C/GH-REG-165": 0.20307418543290176,
   "S0R/cold_minus10C/LH-520": 0.2077148668464122,
   "S5/cold_minus10C/GH-REG-165": 0.3759664832596109,
   "S5/cold_minus10C/LH-520": 0.35029783393501807,
   "S5-13L/cold_minus10C/GH-REG-165": 0.2835800884871004,
   "S5-13L/cold_minus10C/LH-520": 0.19271901517867815,
   "S6/cold_minus10C/GH-REG-165": 0.20467556279922583,
   "S6/cold_minus10C/LH-520": 0.21245250316645556,
   "S7/cold_minus10C/GH-REG-165": 0.196022348659593,
   "S7/cold_minus10C/LH-520": 0.19934449867429363,
   "S4p/cold_minus10C/GH-REG-165": 0.09176144301518147,
   "S4p/cold_minus10C/LH-520": 0.08158373325359439,
   "S0R/hot_alt_2000m_45C/GH-REG-165": 0.20085139318885448,
   "S0R/hot_alt_2000m_45C/LH-520": 0.19644195740089093,
   "S5/hot_alt_2000m_45C/GH-REG-165": 0.3719041014464038,
   "S5/hot_alt_2000m_45C/LH-520": 0.3029300545602643,
   "S5-13L/hot_alt_2000m_45C/GH-REG-165": 0.2765053015400854,
   "S5-13L/hot_alt_2000m_45C/LH-520": 0.179867324309857,
   "S6/hot_alt_2000m_45C/GH-REG-165": 0.20235036007028734,
   "S6/hot_alt_2000m_45C/LH-520": 0.20216434772267808,
   "S7/hot_alt_2000m_45C/GH-REG-165": 0.19287518277283,
   "S7/hot_alt_2000m_45C/LH-520": 0.18623506987347108,
   "S4p/hot_alt_2000m_45C/GH-REG-165": 0.0877391025176317,
   "S4p/hot_alt_2000m_45C/LH-520": 0.06858783966224011
  },
  "meaning": "a capability metric, not a fuel one. The integrator gives a candidate that cannot hold the demanded speed the speed it CAN hold, charges it the extra time in accessory energy, and records the shortfall - so a large value here and a good margin together mean the margin was earned on a slower truck."
 },
 "heat_ledger_WS6": {
  "convention": "component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation (inherited from ws8_params, r2)",
  "rows_by_physical_location": {
   "engine_coolant_kW": "radiator / charge-air cooler",
   "hydraulic_retarder_coolant_kW": "the SAME coolant circuit - a secondary hydrodynamic retarder rejects through a heat exchanger into the engine cooling system, so WS6 must add this row to the coolant one and size one package for the sum",
   "engine_exhaust_kW": "exhaust and surface radiation",
   "compression_brake_exhaust_kW": "exhaust - a compression brake is an exhaust-side device and its heat does NOT go to the resistor bank (F1(b))",
   "traction_machine_inverter_kW": "machine jacket and inverter cold plate",
   "generator_rectifier_kW": "generator jacket and rectifier",
   "pack_kW": "pack coolant loop",
   "brake_resistor_kW": "air, through a grid resistor bank",
   "friction_brake_kW": "foundation brakes, to air - a row WS8's ledger did not have at all (F1(c))",
   "driveline_kW": "gearbox and axle oil"
  },
  "cases": [
   "cruise_95kmh_flat",
   "climb_6pct",
   "descent_6pct_pack_capable",
   "descent_6pct_pack_saturated",
   "simulated_peak_over_all_runs"
  ],
  "sustained_cases": [
   "cruise_95kmh_flat",
   "climb_6pct",
   "descent_6pct_pack_capable",
   "descent_6pct_pack_saturated"
  ],
  "transient_cases": [
   "simulated_peak_over_all_runs"
  ],
  "duration_convention": "THE TWO CLASSES ARE NOT INTERCHANGEABLE AND WS6 MUST NOT SIZE ONE THING ON BOTH. The four analytic cases are SUSTAINED - the vehicle holds that speed on that grade indefinitely, and they are what a cooling package and a resistor bank are sized on. `simulated_peak_over_all_runs` is a TRANSIENT PEAK taken over every (corner, duty, seed) run: the friction-brake row there is a single service stop lasting seconds, not a duty. Both are exported - `worst_case` over the full set and `worst_case_sustained` over the sustained set alone - so WS6 can size thermal capacity on the second and structural or energy limits on the first. WS8 r1's finding F1 was that its ledger's governing case sat OUTSIDE its enumerated set; the answering risk is putting a transient inside it without saying so, and this is where that is said.",
  "for_workstream": "WS6 heat ledger (CLAUDE.md rule 7)",
  "candidates": {
   "S0R": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 69.7105241630927,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 96.26691432046137,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 173.64772129613934,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 207.08960797752772,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 285.98088720706215,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 29.119826161337528,
      "case_wheel_power_kW": 321.5825451745642,
      "road_speed_kmh": 48.48106964927392,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 522.1903213459274,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 303.6458758853762,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 834.271471275764,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1487.9173471611402,
      "governing_run": {
       "hydraulic_retarder_coolant_kW": "nominal/GH-REG-165/seed8101",
       "compression_brake_exhaust_kW": "payload_plus20/GH-REG-165/seed8105",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 207.08960797752772,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 207.08960797752772,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0,
       "simulated_peak_over_all_runs": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 285.98088720706215,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 285.98088720706215,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412,
       "simulated_peak_over_all_runs": 303.6458758853762
      },
      "value": 303.6458758853762,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 834.271471275764
      },
      "value": 834.271471275764,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 29.119826161337528,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 207.08960797752772,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 207.08960797752772,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 285.98088720706215,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 285.98088720706215,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412
      },
      "value": 117.63792201810412,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 29.119826161337528,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     }
    }
   },
   "S5": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 77.36846018113769,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 106.8421592977616,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 191.88090229148457,
      "checks": {
       "resistor_rating_kW": 170.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 155.08847433545833,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 214.16979789182344,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 3.196118897267489,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 22.25630307166523,
      "case_wheel_power_kW": 264.0203232564237,
      "road_speed_kmh": 40.11900554742124,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 394.7106941962145,
      "checks": {
       "resistor_rating_kW": 170.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 218.7482713426197,
      "traction_machine_inverter_kW": 20.4456222956785,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 3.7522844811474334,
      "brake_resistor_kW": 103.36787900822493,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 121.32386489043357,
      "total_rejected_kW": 346.31405712767054,
      "checks": {
       "resistor_rating_kW": 170.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 121.32386489043357,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 218.7482713426197,
      "traction_machine_inverter_kW": 15.77563558231977,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 154.22436441768022,
      "friction_brake_kW": 78.88965067548443,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 170.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": false,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 237.58748648351906,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 170.0,
      "friction_brake_kW": 812.6480151557529,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1220.235501639272,
      "governing_run": {
       "brake_resistor_kW": "nominal/GH-REG-165/seed8101",
       "compression_brake_exhaust_kW": "grade_heavy/LH-520/seed8102",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 170.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 77.36846018113769,
       "climb_6pct": 155.08847433545833,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 155.08847433545833,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 106.8421592977616,
       "climb_6pct": 214.16979789182344,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 214.16979789182344,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 218.7482713426197,
       "descent_6pct_pack_saturated": 218.7482713426197,
       "simulated_peak_over_all_runs": 237.58748648351906
      },
      "value": 237.58748648351906,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "grade_heavy/LH-520/seed8102"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 3.196118897267489,
       "descent_6pct_pack_capable": 20.4456222956785,
       "descent_6pct_pack_saturated": 15.77563558231977,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 20.4456222956785,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 3.7522844811474334,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 3.7522844811474334,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 103.36787900822493,
       "descent_6pct_pack_saturated": 154.22436441768022,
       "simulated_peak_over_all_runs": 170.0
      },
      "value": 170.0,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "nominal/GH-REG-165/seed8101"
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 78.88965067548443,
       "simulated_peak_over_all_runs": 812.6480151557529
      },
      "value": 812.6480151557529,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 22.25630307166523,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 22.25630307166523,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 77.36846018113769,
       "climb_6pct": 155.08847433545833,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 155.08847433545833,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 106.8421592977616,
       "climb_6pct": 214.16979789182344,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 214.16979789182344,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 218.7482713426197,
       "descent_6pct_pack_saturated": 218.7482713426197
      },
      "value": 218.7482713426197,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 3.196118897267489,
       "descent_6pct_pack_capable": 20.4456222956785,
       "descent_6pct_pack_saturated": 15.77563558231977
      },
      "value": 20.4456222956785,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 3.7522844811474334,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 3.7522844811474334,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 103.36787900822493,
       "descent_6pct_pack_saturated": 154.22436441768022
      },
      "value": 154.22436441768022,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 78.88965067548443
      },
      "value": 78.88965067548443,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 22.25630307166523,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 22.25630307166523,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     }
    }
   },
   "S5-13L": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 70.71558974073622,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 97.65486202292146,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 176.04073457624295,
      "checks": {
       "resistor_rating_kW": 180.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 20.10346925870857,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": 152.0326117115945,
      "road_speed_kmh": 23.36820388664707,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 20.10346925870857,
      "checks": {
       "resistor_rating_kW": 180.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 200.4962031901382,
      "traction_machine_inverter_kW": 21.417969106748295,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 4.858091188083428,
      "brake_resistor_kW": 83.7873767851035,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 157.0782817480307,
      "total_rejected_kW": 310.55964027007343,
      "checks": {
       "resistor_rating_kW": 180.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 157.0782817480307,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 200.4962031901382,
      "traction_machine_inverter_kW": 16.408064171918056,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 163.59193582808194,
      "friction_brake_kW": 87.14171882796592,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 180.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": false,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 284.19842390379614,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 180.0,
      "friction_brake_kW": 813.8068783469033,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1278.0053022506995,
      "governing_run": {
       "brake_resistor_kW": "nominal/GH-REG-165/seed8101",
       "compression_brake_exhaust_kW": "hot_alt_2000m_45C/GH-REG-165/seed8105",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 180.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 70.71558974073622,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 70.71558974073622,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 97.65486202292146,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 97.65486202292146,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 200.4962031901382,
       "descent_6pct_pack_saturated": 200.4962031901382,
       "simulated_peak_over_all_runs": 284.19842390379614
      },
      "value": 284.19842390379614,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "hot_alt_2000m_45C/GH-REG-165/seed8105"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 20.10346925870857,
       "descent_6pct_pack_capable": 21.417969106748295,
       "descent_6pct_pack_saturated": 16.408064171918056,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 21.417969106748295,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 4.858091188083428,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 4.858091188083428,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 83.7873767851035,
       "descent_6pct_pack_saturated": 163.59193582808194,
       "simulated_peak_over_all_runs": 180.0
      },
      "value": 180.0,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "nominal/GH-REG-165/seed8101"
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 87.14171882796592,
       "simulated_peak_over_all_runs": 813.8068783469033
      },
      "value": 813.8068783469033,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 7.6702828125852704,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 70.71558974073622,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 70.71558974073622,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 97.65486202292146,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 97.65486202292146,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 200.4962031901382,
       "descent_6pct_pack_saturated": 200.4962031901382
      },
      "value": 200.4962031901382,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 20.10346925870857,
       "descent_6pct_pack_capable": 21.417969106748295,
       "descent_6pct_pack_saturated": 16.408064171918056
      },
      "value": 21.417969106748295,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 4.858091188083428,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 4.858091188083428,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 83.7873767851035,
       "descent_6pct_pack_saturated": 163.59193582808194
      },
      "value": 163.59193582808194,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 87.14171882796592
      },
      "value": 87.14171882796592,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 7.6702828125852704,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     }
    }
   },
   "S6": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 60.473915423540085,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 83.51159748965061,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 151.65579572577596,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 180.06652470146003,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 248.66329601630198,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 29.119826161337528,
      "case_wheel_power_kW": 321.5825451745642,
      "road_speed_kmh": 48.48106964927392,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 457.8496468790995,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 303.65362791626563,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 790.1255931712791,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1443.7792210875448,
      "governing_run": {
       "hydraulic_retarder_coolant_kW": "nominal/GH-REG-165/seed8101",
       "compression_brake_exhaust_kW": "payload_plus20/LH-520/seed8107",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 60.473915423540085,
       "climb_6pct": 180.06652470146003,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 180.06652470146003,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0,
       "simulated_peak_over_all_runs": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 83.51159748965061,
       "climb_6pct": 248.66329601630198,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 248.66329601630198,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412,
       "simulated_peak_over_all_runs": 303.65362791626563
      },
      "value": 303.65362791626563,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/LH-520/seed8107"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 790.1255931712791
      },
      "value": 790.1255931712791,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 29.119826161337528,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 60.473915423540085,
       "climb_6pct": 180.06652470146003,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 180.06652470146003,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 83.51159748965061,
       "climb_6pct": 248.66329601630198,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 248.66329601630198,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412
      },
      "value": 117.63792201810412,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 29.119826161337528,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     }
    }
   },
   "S7": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 69.7105241630927,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 96.26691432046137,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 173.64772129613934,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 214.69600270861247,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 296.48495612141727,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 29.891040022548736,
      "case_wheel_power_kW": 330.0993857280797,
      "road_speed_kmh": 49.70174387589494,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 541.0719988525784,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 117.63792201810412,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 350.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 303.63379656778903,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 832.2435539731687,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1485.8773505409577,
      "governing_run": {
       "hydraulic_retarder_coolant_kW": "nominal/GH-REG-165/seed8101",
       "compression_brake_exhaust_kW": "hot_alt_2000m_45C/GH-REG-165/seed8106",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 0.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 350.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 214.69600270861247,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 214.69600270861247,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0,
       "simulated_peak_over_all_runs": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 296.48495612141727,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 296.48495612141727,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412,
       "simulated_peak_over_all_runs": 303.63379656778903
      },
      "value": 303.63379656778903,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "hot_alt_2000m_45C/GH-REG-165/seed8106"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 832.2435539731687
      },
      "value": 832.2435539731687,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.891040022548736,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 29.891040022548736,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 214.69600270861247,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 214.69600270861247,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 350.0,
       "descent_6pct_pack_saturated": 350.0
      },
      "value": 350.0,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 296.48495612141727,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 296.48495612141727,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 117.63792201810412,
       "descent_6pct_pack_saturated": 117.63792201810412
      },
      "value": 117.63792201810412,
      "governing_case": "descent_6pct_pack_capable",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.891040022548736,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 29.891040022548736,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     }
    }
   },
   "S4p": {
    "cases": {
     "cruise_95kmh_flat": {
      "engine_coolant_kW": 75.52217514930254,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 104.2925275871321,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 12.1946629399731,
      "generator_rectifier_kW": 7.239983443645087,
      "pack_kW": 1.91579155218859,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 5.04561482426698,
      "case_wheel_power_kW": 112.12477387259945,
      "road_speed_kmh": 95.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 206.2107554965084,
      "checks": {
       "resistor_rating_kW": 350.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "climb_6pct": {
      "engine_coolant_kW": 123.52770433394019,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 170.58587741353648,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 39.44661504477682,
      "generator_rectifier_kW": 9.351498679064974,
      "pack_kW": 7.402504804720108,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "driveline_kW": 20.279416737145368,
      "case_wheel_power_kW": 450.65370526989665,
      "road_speed_kmh": 66.47787395094286,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 370.5936170131839,
      "checks": {
       "resistor_rating_kW": 350.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged."
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_capable": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 34.72869728739207,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 4.165811666601297,
      "brake_resistor_kW": 294.04883584400227,
      "friction_brake_kW": 0.0,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 134.6945772201085,
      "total_rejected_kW": 332.9433447979956,
      "checks": {
       "resistor_rating_kW": 350.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": true,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 134.6945772201085,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "descent_6pct_pack_saturated": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 26.305592846480252,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 323.69440715351976,
      "friction_brake_kW": 117.63792201810412,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": -467.6379220181041,
      "road_speed_kmh": 100.0,
      "pack_stored_not_rejected_kW": 0.0,
      "total_rejected_kW": 467.6379220181041,
      "checks": {
       "resistor_rating_kW": 350.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true,
       "friction_allowance_kW": 60.0,
       "friction_within_allowance": false,
       "friction_note": "friction above the declared continuous allowance is a CAPABILITY finding, not a rating breach: it says the candidate cannot hold the case's speed on its own retarding hardware and must descend more slowly. It is reported as such and is NOT counted among the rating violations, which are about hardware whose mass was charged.",
       "descent_closure_residual_kW": 0.0,
       "descent_stored_in_pack_kW": 0.0,
       "descent_closes": true
      },
      "duration_class": "sustained"
     },
     "simulated_peak_over_all_runs": {
      "engine_coolant_kW": 0.0,
      "hydraulic_retarder_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "compression_brake_exhaust_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 350.0,
      "friction_brake_kW": 827.3857240571083,
      "driveline_kW": 0.0,
      "case_wheel_power_kW": null,
      "road_speed_kmh": null,
      "total_rejected_kW": 1177.3857240571083,
      "governing_run": {
       "brake_resistor_kW": "cold_minus10C/GH-REG-165/seed8101",
       "friction_brake_kW": "payload_plus20/GH-REG-165/seed8105"
      },
      "duration_class": "transient peak",
      "checks": {
       "resistor_rating_kW": 350.0,
       "resistor_within_rating": true,
       "retarder_rating_kW": 0.0,
       "retarder_within_rating": true
      }
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 75.52217514930254,
       "climb_6pct": 123.52770433394019,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 123.52770433394019,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "engine_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 104.2925275871321,
       "climb_6pct": 170.58587741353648,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 170.58587741353648,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained",
      "governing_run": null
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 39.44661504477682,
       "descent_6pct_pack_capable": 34.72869728739207,
       "descent_6pct_pack_saturated": 26.305592846480252,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 39.44661504477682,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "generator_rectifier_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 7.239983443645087,
       "climb_6pct": 9.351498679064974,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 9.351498679064974,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "pack_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 7.402504804720108,
       "descent_6pct_pack_capable": 4.165811666601297,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 7.402504804720108,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     },
     "brake_resistor_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 294.04883584400227,
       "descent_6pct_pack_saturated": 323.69440715351976,
       "simulated_peak_over_all_runs": 350.0
      },
      "value": 350.0,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "cold_minus10C/GH-REG-165/seed8101"
     },
     "friction_brake_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 117.63792201810412,
       "simulated_peak_over_all_runs": 827.3857240571083
      },
      "value": 827.3857240571083,
      "governing_case": "simulated_peak_over_all_runs",
      "duration_class": "transient peak",
      "governing_run": "payload_plus20/GH-REG-165/seed8105"
     },
     "driveline_kW": {
      "rule": "max over the FULL enumerated case set, sustained cases AND the transient simulated peak",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 20.279416737145368,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_peak_over_all_runs": 0.0
      },
      "value": 20.279416737145368,
      "governing_case": "climb_6pct",
      "duration_class": "sustained",
      "governing_run": null
     }
    },
    "worst_case_sustained": {
     "engine_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 75.52217514930254,
       "climb_6pct": 123.52770433394019,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 123.52770433394019,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "hydraulic_retarder_coolant_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "engine_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 104.2925275871321,
       "climb_6pct": 170.58587741353648,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 170.58587741353648,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "compression_brake_exhaust_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "duration_class": "sustained"
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 39.44661504477682,
       "descent_6pct_pack_capable": 34.72869728739207,
       "descent_6pct_pack_saturated": 26.305592846480252
      },
      "value": 39.44661504477682,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "generator_rectifier_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 7.239983443645087,
       "climb_6pct": 9.351498679064974,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 9.351498679064974,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "pack_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 7.402504804720108,
       "descent_6pct_pack_capable": 4.165811666601297,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 7.402504804720108,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     },
     "brake_resistor_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 294.04883584400227,
       "descent_6pct_pack_saturated": 323.69440715351976
      },
      "value": 323.69440715351976,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "friction_brake_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 117.63792201810412
      },
      "value": 117.63792201810412,
      "governing_case": "descent_6pct_pack_saturated",
      "duration_class": "sustained"
     },
     "driveline_kW": {
      "rule": "max over the SUSTAINED case set only - the number a cooling package is sized on",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 20.279416737145368,
       "descent_6pct_pack_capable": 0.0,
       "descent_6pct_pack_saturated": 0.0
      },
      "value": 20.279416737145368,
      "governing_case": "climb_6pct",
      "duration_class": "sustained"
     }
    }
   }
  }
 },
 "electricity_accounting_ESC3": {
  "pef_diesel": 1.19,
  "pef_grid": 2.1,
  "co2_grid_kg_per_kWh": 0.28,
  "eta_charge_grid_to_pack": 0.9215,
  "sensitivity": 0.5,
  "applies_to": [
   "S4p"
  ]
 },
 "escalations": [
  "ESC-WS9-1",
  "ESC-WS9-2",
  "ESC-WS9-3",
  "ESC-WS9-4",
  "ESC-WS9-5",
  "ESC-WS9-6",
  "ESC-WS9-7",
  "ESC-WS9-9",
  "ESC-WS9-8"
 ],
 "ws2_chain_of_record": {
  "map_file": "data/effmap_motor_inverter_662V.csv",
  "map_voltage_V": 662.0,
  "ws2_rework_round": 4,
  "feasible_cells": 4203,
  "loader": "WS4 ws4_chain.WS2TractionChain (ruled), read-only",
  "machine_gate_ESC2": 2.0
 }
}
```

---

## 16. Provenance and reproduction

```
cd WS9_vehicle_one_wave2
../.venv/bin/python run_ws9.py --jobs 6   # -> results_ws9.json + data/*.csv
../.venv/bin/python make_report_ws9.py    # -> REPORT_WS9.md
../.venv/bin/python verify_ws9.py         # asserts report == results
```

**Inherited, read-only (CLAUDE.md rule 10):**

- **WS8** - the duty cycles, the achieved-speed integrator, the road load, the mass ledger, the HD Willans engines and the AMT, the genset line, the WS2 machine stretch, the WS3 pack construction, the startability specification, the sustained-climb rule, the regen blend-out, the friction-brake allowance, the spin-drag rule and its thresholds, the correction-pricing rule, the ambient derate and the hot/altitude corner. SHA-pinned in section 12.
- **WS2 r4** (through WS8) - the measured inverter+motor loss map, the capability envelope, the stack-length scaling rule and its mass split, the 7,200 rpm rotor limit, the resistor's kg per kW.
- **WS3** (through WS8) - cell definitions, the pack overhead model, cold charge acceptance.
- **WS4** (through WS8) - `WillansEngine`, `PMGenerator`, `derate_factor`, `WS2TractionChain` and the R12 chain convention.

**External, cited, with evidence quality stated:**

- **ACHATES_OP** - Achates Power, 'Opposed-Piston Heavy-Duty Diesel Engine Performance and Emissions Summary', 2024-05-13. *Used for:* S6's opposed-piston-class engine island BSFC target. *Evidence quality:* PRIMARY DOCUMENT, FETCHED AND READ IN FULL (not a search summary - this is a strictly better evidence class than any external figure in WS8, whose environment blocked egress). It is nonetheless a MANUFACTURER'S document reporting its own demonstration programme. Mitigating: the programme is led by CALSTART and supported by CARB, in-use emissions were measured by UC-Riverside with PEMS, the fleet comparison was run by Walmart against a competitor's production engine, and dynamometer testing was independently repeated by Aramco Services. Aggravating: no peer-reviewed BSFC map is published, the 49.2% figure is a single peak point, and no engine mass is stated. WS9 therefore uses ONLY the peak-BTE number, carries the engine at the four-stroke's mass, and reports the BREAK-EVEN peak BTE at which S6 exactly clears the gate so the lead can see how much of the claim must be true.
- **ICCT_TUV** - ICCT / TUV NORD, fuel consumption testing of tractor-trailers in the European Union and the United States. *Used for:* the F7 ensemble cross-check of the ruler. *Evidence quality:* INHERITED FROM WS8 unchanged (search-summary level there; not re-fetched here). Carried so that WS9's F7 ensemble cross-check is against the same band WS8 was checked against.
- **VOLVO_RET_TH** - Volvo Truck Corporation, Fact Sheet 'Retarder RET-TH', ENG 1(2)-2(2), version 06, 2014-03-10. *Used for:* ESC-6: the ruler's hydraulic retarder (S0R). *Evidence quality:* PRIMARY OEM FACT SHEET, FETCHED AND READ IN FULL. Torque figures and mass are the manufacturer's own specification for a shipped Class 8 product. The CONTINUOUS thermal rating is NOT stated on the sheet (only that it falls with coolant temperature), so WS9 declares it and flags it.
- **ISO_8528_PRP** - ISO 8528-1 rating definitions as summarised by MTU Onsite Energy (Power Engineering) and by a QSX15 generator-set ratings guide; Cummins X15 published automotive ratings. *Used for:* ESC-4: WS9's Class 8 prime-power derating basis. *Evidence quality:* SEARCH-SUMMARY plus one FETCHED secondary page. The ISO 8528-1 rating STRUCTURE is standard and not in dispute; the 0.90 PRP/ESP ratio is an industry rule of thumb corroborated by the QSX15 guide's 'prime ratings about 10% below', not read from the standard itself. Provisional per E13.
- **PACK_WH_PER_KG** - batterydesign.net, 'Pack Gravimetric Energy Density'. *Used for:* ESC-1(c): S4's cited external energy-optimised cell as an explicitly non-WS3 bracket. *Evidence quality:* FETCHED SECONDARY AGGREGATOR. Road-car packs, not Class 8 packs. WS9 takes a DISCOUNT to 160 Wh/kg for a Class 8 pack (crash structure, larger modules, higher-current busbars, more thermal hardware), which is the conservative direction for S4' - the candidate the cell is being cited for. Provisional per E13.
- **ATKINSON_BTE** - Toyota Motor Corporation engine announcements as reported by SAE Mobility Engineering and Green Car Congress. *Used for:* prime-mover-at-the-pin: Atkinson petrol. *Evidence quality:* SEARCH-SUMMARY level. The figure is for a 2-2.5 L LIGHT-DUTY engine; WS9 applies it to a 7 L-class pinned-point prime mover. Bore-scale and a fixed operating point both argue the larger engine would do at least as well, but no heavy-duty Atkinson petrol product exists to check it against - which is itself the durability finding reported in the prime-mover task.
- **NG_SI_BTE** - Cummins X15N product coverage (Fleet Equipment, CCJ, Cummins Inc.). *Used for:* prime-mover-at-the-pin: natural-gas SI. *Evidence quality:* SEARCH-SUMMARY level, and the '10% more efficient' figure is relative to another gas engine rather than an absolute BTE. WS9 declares 40.5% peak BTE for a pinned-point stoichiometric-EGR HD gas engine and states that the number is WS9's, corroborated by rather than read from the source.

### 16.1 Regeneration check (rule 1)

**Status: PASS**

- **Half 1, the simulation.** `cold_minus10C/S5` re-run FROM SCRATCH in a fresh process over all 8 seeds: 160 per-seed values compared at exact (0 ulp), 0 mismatches. Matches the committed run: **True**.
- **Half 2, the derived blocks and the exports.** `run_ws9.py --from-checkpoint` regenerates every derived block and every CSV from the committed trial. results_ws9.json byte-identical: **True**; all CSV exports byte-identical: **True**.
- **Not checked, stated rather than implied.** the other five corners are not re-simulated; the jobs are independent and identically constructed, and a full re-run costs hours. Half 1 is evidence for the construction, not for each corner's arithmetic.

| WS9 file | sha256 |
|---|---|
| `run_ws9.py` | `23c7d3c4b344eb0f...` |
| `ws9_params.py` | `927e8584f5c46dbc...` |
| `ws9_duty.py` | `86e9d6c18c7b70cc...` |
| `ws9_engines.py` | `407a00ca47413b82...` |
| `ws9_fuels.py` | `54dd729fe643875a...` |
| `ws9_storage.py` | `378fef25a1206e4e...` |
| `ws9_thermal.py` | `1b50fe728f313154...` |
| `ws9_walls.py` | `7a9962cccec308b5...` |
| `ws9_candidates.py` | `0cd9b1fe33b955c2...` |
| `ws9_corrections.py` | `8d467421c27e60a3...` |
| `ws9_primemover.py` | `532f152c1232fa3f...` |
| `ws9_blocks.py` | `15c2dc9e548accd0...` |
| `make_report_ws9.py` | `326dff4180de3f92...` |
| `verify_ws9.py` | `8c9789e294333def...` |
| `check_determinism_ws9.py` | `ffcb0dc03e36efaf...` |

