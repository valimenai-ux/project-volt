# REPORT WS8 - VEHICLE ONE: SEMI-SCALE ARCHITECTURE TRIAL

Workstream WS8, Vehicle One. Executes `WS8_semi_architecture/ASSIGNMENT.md` against `BASELINE_v3.md`.

**Nothing here is ratified.** The lead ratifies in a separate chat (CLAUDE.md rule 11). This report states what the physics gave and what it cost; the execute-or-spare decision is the lead's.

**This report is generated**, not written: every number below is formatted out of `results_ws8.json` by `make_report_ws8.py`, and `verify_ws8.py` asserts independently that each rendered figure appears verbatim and that the interface block equals `results_ws8.json['interface_ws8']`. Nothing was transcribed by hand (rule 2).

| | |
|---|---|
| Entry point | `run_ws8.py` (fixed seeds 8101..8108, 8 seeds) |
| Baseline of record | BASELINE_v3.md |
| Python / numpy | 3.11.15 / 2.4.6 |
| Metric of record | fuel energy per **payload** tonne-km [MJ/(t.km)] |
| Fleet mission | 70% LH-520 + 30% REG-165 by distance |

---

## 0. What this trial found

**No candidate advances.** S1, S2, S3, S4 all fail the pre-committed criteria.

The trial is decided by a single structural fact, and it is worth stating before any table: **at fixed gross combination weight, powertrain mass is payload.** Every candidate here is more efficient per kilometre than the conventional truck. Every candidate here is also heavier. The metric of record divides one by the other, and that division is what the assignment ordered precisely because it is where the argument actually lives.

S0, the ruler, burns **38.78 L/100 km** on the fleet mission. That is above the assignment's 30-38 L/100 km corridor, and the reason is the corridor itself rather than the model: run over the same road with the grade zeroed, S0 burns **33.08 L/100 km** against a published 32.6 L/100 km for a typical EU tractor-trailer over the regulatory Long Haul cycle - a match to about one percent, with nothing fitted to it. Task 1 ordered ~3,800 m of climb; a 30-38 band describes a freeway. Reported, not tuned away, and escalated as ESC-WS8-7.

- **S1** burns 7.2% less fuel per kilometre than S0 and carries 1,387 kg less payload. Net on the metric of record: +0.75% (median), -0.66% (ensemble min). **KILL**.
- **S2** burns 9.6% less fuel per kilometre than S0 and carries 1,679 kg less payload. Net on the metric of record: +1.70% (median), +0.36% (ensemble min). **KILL**.
- **S3** burns 1.8% less fuel per kilometre than S0 and carries 1,226 kg less payload. Net on the metric of record: -3.83% (median), -6.22% (ensemble min). **KILL**.
- **S4** burns 6.0% less fuel per kilometre than S0 and carries 1,441 kg less payload. Net on the metric of record: -0.95% (median), -3.67% (ensemble min). **KILL**.

S3 fails for a reason that has nothing to do with fuel, and it is the most useful result in this report: **no fixed ratio exists that lets a diesel axle both cruise at 105 km/h and hold the 6% mountain grade at 36,300 kg.** The two requirements are not close; they are separated by a factor of two in ratio. That is not a tuning problem, and it is the answer to the question S3 was posed to ask.

---

## 1. Prior-art map (Task 0)

**Task 0: DELIVERED-BOUNDED** - see `PRIOR_ART_WS8.md` (sha256 `469c28c502108e5d...`, 239,614 bytes), pinned to this run.

**Evidence quality.** SEARCH-SUMMARY LEVEL ONLY. This environment's egress policy denies direct HTTPS CONNECT to external hosts - patent databases, SAE, NREL, NACFE and OEM sites all return 403 at the gateway (verified against the proxy's own status endpoint). Server-side web SEARCH does work and returned substantive, sourced results, so the scan was RUN rather than deferred; but no patent claim text and no primary document was read verbatim. Every finding in the claim map is therefore a lead, flagged provisional per the E13 precedent, and is NOT a freedom-to-operate opinion. Any decision that turns on claim scope needs a re-run with database access or outside counsel.

**Why not deferred.** The assignment permits DEFERRED if the environment restricts web access. It restricts it partially, not wholly. Deferring would have thrown away a real and convergent result - so the scan is reported with its evidence limit stated instead.

The S3 verdict in this report rests on the physics in Task 5, not on the scan. The scan corroborates it independently (section 8), which is worth something, but no verdict in section 9 depends on it.

---

## 2. Duty cycles (Task 1)

Two constructed, distance-indexed cycles at 10 Hz, each an 8-seed ensemble. Grade belongs to the road, not to the clock, so the cycles are indexed on distance and the speed trace is integrated **forward against each candidate's own tractive envelope**. That is a deliberate departure from WS1's flat-road-then-apply-grade method, and the reason is arithmetic: at 36,300 kg no candidate in this trial can hold 85 km/h on 6%, so a demand trace applied after the fact would hand every candidate a speed it does not have and would hide the one quantity Task 5 asks for.

| | LH-520 | REG-165 |
|---|---|---|
| distance, median | 520.0 km | 165.0 km |
| max grade | 0.0605 | 0.0537 |
| min grade | -0.0605 | -0.0512 |
| total climb, median | 3,704 m | 874 m |
| net elevation change, worst seed | +0.04 m | +0.05 m |
| distance at 2-3% grade | 0.067 | 0.041 |
| distance at >=5% grade | 0.034 | 0.000 |

Assignment conformance, checked in code rather than asserted:

- sampled at 10 Hz: **True**
- line-haul >= 500 km: **True**
- sustained 2-3% sections present: **True**
- 6% mountain segment present: **True**
- descent gives back the full climb: **True**

Net elevation change over 520 km is under a metre on every seed (matched +/- feature pairs), so no candidate is handed potential energy by the corridor. The seed varies the per-trip cruise speed inside the assignment's 85-105 km/h band, a constant headwind component, the rolling-terrain amplitude and phase, and stop dwells. The SPECIFIED features - the 2-3% sustained sections and the 6% mountain - are not jittered, because the assignment fixes them.

---

## 3. S0 baseline, calibrated (Task 2)

S0 is the ruler. Every candidate is judged against it; nothing in this report is a self-referential comparison.

### 3.1 The engine

A 12.8 L six on WS4's ruled Willans construction, re-calibrated for the heavy-duty class. Peak power **352.0 kW** at 2,373 Nm - inside the assignment's 330-370 kW band.

The calibration has exactly one knob and it is solved, not tuned: `eta_i0` is bisected until the map's minimum BSFC lands on the declared island target of 185.0 g/kWh. The solve returns **0.4788**, and the achieved island is **185.0 g/kWh** at **1141 rpm** / 2,016 Nm (241 kW) - a peak brake thermal efficiency of **0.455**, which is where a modern production on-highway heavy-duty diesel sits.

The speed term was re-anchored for this class: `1 - 0.08*((rpm-1250)/1000)^2  [WS8 HD re-anchor]`. WS4's own form centres the optimum at 1,600 rpm, which is right for the medium-duty engine WS4 calibrated and wrong for a 600-2,100 rpm Class 8 six. This is a change to an inherited model and it is escalated, not assumed (ESC-WS8-5).

### 3.2 The transmission, stated

- 12-speed AMT, direct top gear, 12 ratios, top gear 1.00 (direct), axle 2.47:1
- direct top gear efficiency 0.985; indirect gears 0.965 (a direct top has no countershaft power path - which is exactly why line-haul trucks are specified this way, and it is the honest size of the prize any gearbox-deleting candidate can claim)
- tandem axle 0.955, driveshafts 0.995
- cruise chain 0.9360; engine at 1310 rpm at 100 km/h

### 3.3 Calibration against the reference band

Reference: assignment Task 2, quoted verbatim: 'sanity corridor: 30-38 L/100 km loaded line-haul'

| | min | median | max |
|---|---|---|---|
| line-haul LH-520 [L/100 km] | 36.79 | 39.57 | 44.69 |
| regional REG-165 [L/100 km] | 33.17 | 35.14 | 39.35 |
| **fleet mission** [L/100 km] | 36.27 | 38.78 | 41.23 |

Fleet fuel is inside the 30-38 L/100 km corridor on every seed: **False**. Fudge factor applied: **False**. eta_i0 is SOLVED so the map minimum lands exactly on the declared 185.0 g/kWh island; nothing else is tuned. The fleet fuel that comes out is whatever the physics gives, and it is checked - not fitted - against the corridor.

### 3.4 Cross-check against the public reference band

The corridor this trial runs is not a regulatory cycle - Task 1 ordered a 6% mountain and sustained 2-3% sections, about 3,800 m of climb over 520 km. Comparing its fuel directly against a freeway-dominated published figure would compare two different roads. So the cross-check runs S0 over the **same corridor with the grade zeroed** - same distance, same speeds, same wind, same driver, same vehicle, nothing else touched - which isolates terrain and makes the comparison like-for-like.

| | L/100 km |
|---|---|
| S0, LH-520 as ordered (median) | 39.57 |
| **S0, same corridor with grade zeroed (median)** | **33.08** |
| ICCT / TUV NORD, typical EU tractor-trailer, regulatory Long Haul | 32.6 |
| ICCT / TUV NORD, at that cycle's regulatory payload (19.3 t) | 33.1 |
| ICCT / TUV NORD, best-in-class EU | 29.9 |

Source: ICCT / TUV NORD, fuel consumption testing of tractor-trailers in the EU and US, over the EU regulatory Long Haul cycle. Evidence quality: located via server-side search only; the primary document could not be fetched in this environment, so the figure is provisional per E13 precedent.

**The model lands on the public band to about one percent, with nothing fitted to it.** A model that lands near the public band on flat ground and above it on a mountain corridor is behaving; one that matched the public band on a mountain corridor would be wrong.

On the corridor as ordered, S0 exceeds the assignment's 30-38 L/100 km band by 3.23 L/100 km. That is reported, not tuned away, and escalated as ESC-WS8-7: the excess is terrain, and every candidate drives the same road, so no margin in this report is affected by it.

Duty-averaged BSFC on the line-haul corridor is 196.8 g/kWh against the 185.0 g/kWh island - the gap between the two is the whole of the hybrid opportunity, and it is smaller than it is at Vehicle Zero scale because a line-haul truck already spends 0.72 of its moving time in top gear near its best point.

---

## 4. Candidate results (Task 3) - the headline

All five at **36,300 kg GCW**, the assignment's fixed condition. Because GCW is fixed, the road-load physics is identical for every candidate: mass does not change how the truck drives, it changes what the truck may carry. Payload is stated explicitly for each.

| | architecture | payload | powertrain | fleet L/100 km | MJ/payload-tkm (min / median / max) | margin vs S0 (min / median / max) | fuel that is correction | verdict |
|---|---|---|---|---|---|---|---|---|
| **S0** | Conventional 13 L diesel + 12-speed AMT, direct top gear | 20,785 kg | 2,845 kg | 38.78 | 0.6215 / 0.6643 / 0.7064 | - (ruler) | 0.0% | **RULER** |
| **S1** | Pure series - Vehicle Zero's architecture scaled to Class 8 | 19,398 kg | 4,232 kg | 35.98 | 0.6094 / 0.6606 / 0.7111 | -0.66% / +0.75% / +2.58% | 2.6% | **KILL** |
| **S2** | Single cruise-ratio + torque-fill, traction machine on a disconnect | 19,106 kg | 4,524 kg | 35.04 | 0.6045 / 0.6531 / 0.7038 | +0.36% / +1.70% / +2.74% | 1.7% | **KILL** |
| **S3** | Tandem split - diesel axle on ONE fixed ratio (no gearbox anywhere) + disconnectable e-axle | 19,559 kg | 4,071 kg | 38.07 | 0.6262 / 0.6932 / 0.7504 | -6.22% / -3.83% / -0.76% | 23.4% | **KILL** |
| **S4** | Range-extended BEV - large pack + ~170 kW sustainer genset | 19,344 kg | 4,286 kg | 36.45 | 0.6141 / 0.6709 / 0.7324 | -3.67% / -0.95% / +2.05% | 8.6% | **KILL** |

The last column before the verdict is the one to read sceptically. It is the fraction of a candidate's reported fuel that is a **correction** rather than fuel the model watched it burn: energy its prime mover and pack could not deliver, charged back as fuel so that every candidate is compared having completed the same mission at the same speeds, plus the make-up for any pack it finished flatter than it started. A small share is bookkeeping. A large share means the candidate did not really do the mission, and the fuel number is flattering it - which is why the raw shortfall is reported separately in section 7 rather than left inside a single figure.

Margins are computed **per seed against S0 on the same seed**, then enveloped. The seed sets the corridor, the wind and the driver, so pairing removes the cycle draw from the comparison instead of leaving it in the variance: the envelope below is a spread of architecture differences, not of weather.

### 4.1 Where the mass goes

| item | S0 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| engine 13L wet | 1,215 | 1,215 | 1,215 | - | - |
| aftertreatment | 155 | 155 | 155 | 155 | 90 |
| amt 12sp | 325 | - | - | - | - |
| driveshafts | 65 | 65 | 65 | 65 | 65 |
| drive axle gearsets | 530 | 530 | 530 | 530 | 530 |
| fuel | 555 | 555 | 555 | 555 | 210 |
| generator | - | 202 | 202 | - | 129 |
| traction motors | - | 317 | 317 | - | 317 |
| inverters | - | 52 | 52 | - | 52 |
| motor reduction stages | - | 115 | 115 | - | 115 |
| brake resistor | - | 122 | 122 | 72 | 122 |
| buffer pack | - | 736 | 736 | 736 | - |
| hv cabling | - | 55 | 55 | 55 | 55 |
| contactors precharge | - | 18 | 18 | 18 | 18 |
| hv misc bms thermal | - | 95 | 95 | 95 | 155 |
| fixed cruise ratio box | - | - | 145 | - | - |
| lockup clutch and actuator | - | - | 105 | - | - |
| traction disconnect | - | - | 42 | - | - |
| engine 11l wet | - | - | - | 1,035 | - |
| fixed ratio box axleA | - | - | - | 145 | - |
| revmatch clutch | - | - | - | 105 | - |
| traction motor axleB | - | - | - | 299 | - |
| inverter axleB | - | - | - | 49 | - |
| motor reduction axleB | - | - | - | 115 | - |
| eaxle disconnect | - | - | - | 42 | - |
| sustainer engine wet | - | - | - | - | 640 |
| traction pack | - | - | - | - | 1,788 |
| **powertrain total** | **2,845** | **4,232** | **4,524** | **4,071** | **4,286** |
| **payload** | **20,785** | **19,398** | **19,106** | **19,559** | **19,344** |

### 4.2 Control policies, declared

**S0** - AMT selects the highest gear that can deliver the demanded wheel force above 1,050 rpm; launch on a slipping clutch at 1,200 rpm with the slip heat charged; overrun fuel cut-off when the wheels drive the engine; compression brake on descents; accessories crank-driven.

**S1** - No mechanical path. Genset follows a 180 s route-preview average of bus demand on the engine's BSFC-optimal locus (engine speed free), start-stop below 45 kW, buffer pack holds SOC 0.15-0.95 about a 0.60 target. Descent braking: regen to the pack up to its charge acceptance, then the brake resistor, then friction. PM spin drag charged on unloaded samples (R22d) - the machines are permanently geared and there is no disconnect.

**S2** - One fixed reduction (2.60:1 overall) couples the engine to the wheels ONLY inside a cruise lockup band; outside it the truck is pure series. The traction machine sits behind a DISCONNECT, so while locked and not filling it is stationary and its spin drag is zero - the G1(b) tax deleted by hardware. Every remaining tax is charged: the machine's losses whenever it IS connected (measured, from WS2's map, not a scalar), and the engine's off-best-point operation at band edges, where road speed - not the supervisor - sets engine speed.

**S3** - Axle A: downsized diesel through a single fixed reduction and a rev-matched clutch. There is NO gearbox and NO generator, so the engine can do exactly one thing - turn axle A - and only above the road speed at which the fixed ratio puts it above its lugging limit. Below that speed the clutch opens and the engine SHUTS DOWN, because with no generator there is nothing else for it to drive. Axle B: a disconnectable e-axle owning launch, low speed, regen and peak assist, fed by a buffer pack that can only be refilled by regen or by through-the-road charging (engine pushes axle A, e-axle harvests on axle B) - a lossy path taken only when the engine is lightly loaded and the pack is below target.
BOTH G1 TAXES DELETED BY CONSTRUCTION, not by assumption: (a) the map-vs-scalar member cannot recur because no scalar chain efficiency exists anywhere in WS8 - every electric sample goes through WS2 r4's measured loss surface; (b) the spin-drag member is deleted by the e-axle's disconnect, and the code charges spin drag ONLY on samples where that disconnect is closed, so the deletion is auditable rather than asserted.

**S4** - Electric traction only; a small sustainer genset holds charge. Run CHARGE-SUSTAINING over the mission (the pack ends where it started), because the metric of record is FUEL energy and no electricity accounting was ordered: crediting a plug-in start would let S4 import propulsion energy the metric cannot see. That choice is stated, and its consequence - that S4 is judged as a series hybrid with a small engine and a heavy pack, not as a plug-in - is escalated rather than buried.

---

### 4.3 Two-speed traction bracket (informative)

The Task 0 product sweep found something that bears directly on how these candidates were sized: **every heavy truck that actually deleted its AMT still fitted a multi-speed gearbox on the traction side** - Hyliion Hypertruck ERX, ePower, ReVolt, Edison, Wrightspeed, BAE - and the heavy-duty e-truck transmission literature finds a three-speed gives the lowest energy consumption that still meets gradeability. WS8's electric candidates were sized on a SINGLE fixed reduction, because WS2's carried 7,200 rpm rotor limit caps the ratio at 12:1 and the 12% startability specification then sets the machine size.

With a two-speed (24:1 low / 12:1 high) the startability torque is met at half the stretch factor, so the machine halves under WS2's own mass law while the box is added back:

| | k, single-speed | k, two-speed | e-drive mass | + box | net mass | payload gain | margin vs S0 | gain |
|---|---|---|---|---|---|---|---|---|
| **S1** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +0.57% -> +1.03% | +0.46 pp |
| **S2** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +1.70% -> +2.17% | +0.47 pp |
| **S4** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | -0.99% -> -0.52% | +0.47 pp |

**informative bracket, fuel per km held at the single-speed value; not the metric of record.** Fuel per kilometre is held at the single-speed value, which makes the bracket conservative: a smaller machine at a higher per-unit load is slightly more efficient at cruise, not less. It changes no verdict in this report - the gains are fractions of a point - but it says where the next mass is, and it says the industry already knew.

---

## 5. Waste-heat recovery (Task 4)

Gate, pre-committed: **>= 2.5% net fleet-mission fuel per payload tonne-km AFTER the mass charge**, else dropped without ceremony. Read on the net fleet-mission fuel per payload tonne-km, AFTER the mass charge, ensemble-min against the threshold (the same statistic G1 was read on).

Recovery is modelled as a function of engine LOAD, not at a rated point. Both systems live on exhaust enthalpy, which collapses at part load; quoting a rated-point gain against a fleet-average duty is the standard way waste-heat recovery is oversold.

| system | mass | gain at 25% load | at 55% | at 85% | at rated |
|---|---|---|---|---|---|
| electric turbocompound | 85 kg | 0.00% | 0.79% | 2.19% | 3.00% |
| small organic Rankine cycle | 215 kg | 0.00% | 0.68% | 2.96% | 4.50% |
| ETC+ORC | 300 kg | 0.00% | 1.36% | 4.76% | 6.92% |

Before any thermodynamics, the mass charge sets the bar. The metric divides by payload, so a system that costs mass has to win back the gate PLUS the payload it displaced:

| candidate | system | mass | payload penalty | fuel gain needed to clear the gate |
|---|---|---|---|---|
| S1 | ETC | 85 kg | 0.44% | **2.94%** |
| S1 | ORC | 215 kg | 1.12% | **3.62%** |
| S1 | ETC+ORC | 300 kg | 1.57% | **4.07%** |
| S2 | ETC | 85 kg | 0.45% | **2.95%** |
| S2 | ORC | 215 kg | 1.14% | **3.64%** |
| S2 | ETC+ORC | 300 kg | 1.60% | **4.10%** |
| S3 | ETC | 85 kg | 0.44% | **2.94%** |
| S3 | ORC | 215 kg | 1.11% | **3.61%** |
| S3 | ETC+ORC | 300 kg | 1.56% | **4.06%** |

| candidate | best system | net margin, median | net margin, min | gate | verdict |
|---|---|---|---|---|---|
| S1 | ETC+ORC | +1.72% | +1.61% | >= 2.5% | **DROPPED** |
| S2 | ETC+ORC | +1.75% | +1.54% | >= 2.5% | **DROPPED** |
| S3 | ETC+ORC | +1.79% | +1.30% | >= 2.5% | **DROPPED** |

**Dropped, without ceremony.** Two things kill it, and the second is the interesting one.

First, the mass charge: the metric divides by payload, so the systems have to win back the gate plus what their mass displaced - the table above shows the real bar is nearer 3-4% than 2.5%.

Second, and more fundamental: **line-haul cruise is a part-load condition, and waste-heat recovery is a full-load technology.** Holding 36,300 kg at 95 km/h on level road needs about 100 kW at the wheel; on a 350 kW-class engine that is roughly a third of rated. Both systems modelled here are negligible below 30-35% load by construction, because exhaust mass flow and temperature both collapse there. The engine spends most of the mission in exactly the region where there is little enthalpy to recover, and the minutes it spends on the mountain at high load are too few to pay for the mass it carries for the other five hours.

This is not an argument that waste-heat recovery does not work. It is an argument that it does not pay ON THIS METRIC, on this duty, against a payload-denominated criterion that was armed before the numbers were seen.

---

## 6. Sensitivities (Task 5)

### 6.1 Corner sweep

Margins vs S0 [%], ensemble min / median, at every corner. Note that at the payload corners GCW moves with payload: the fixed-GCW condition is a Task-3 condition, not a Task-5 one.

| candidate | nominal | payload +20% | payload -20% | grade-heavy corridor | -10 C |
|---|---|---|---|---|---|
| **S1** | -0.66% / +0.75% | +0.17% / +1.74% | -2.18% / -0.90% | +7.54% / +9.97% | -4.37% / -3.16% |
| **S2** | +0.36% / +1.70% | +1.24% / +2.89% | -0.98% / -0.11% | +7.01% / +7.32% | -1.90% / -0.18% |
| **S3** | -6.22% / -3.83% | -6.42% / -3.10% | -7.56% / -4.88% | -1.86% / +2.47% | -11.17% / -8.22% |
| **S4** | -3.67% / -0.95% | -1.87% / +0.79% | -6.04% / -3.31% | +5.75% / +10.11% | -8.26% / -6.01% |

### 6.2 S3: the fixed-ratio grade-hold floor

a fixed ratio must simultaneously (a) keep the engine below its 2,100 rpm ceiling at 105 km/h and (b) put enough torque at the contact patch to hold the grade at a speed above its own lugging floor. Those two pull in opposite directions and that is the whole of the S3 design space.

| ratio A | coupling floor | engine rpm at 105 km/h | cruise OK | 2% | 3% | 4% | 6% | 6% climb feasible on the pack |
|---|---|---|---|---|---|---|---|---|
| 2.40 | 78.5 km/h | 1337 | yes | no_solution | no_solution | no_solution | no_solution | no |
| 2.60 | 72.5 km/h | 1448 | yes | no_solution | no_solution | no_solution | no_solution | no |
| 2.80 | 67.3 km/h | 1560 | yes | no_solution | no_solution | no_solution | no_solution | no |
| 3.00 | 62.8 km/h | 1671 | yes | no_solution | no_solution | no_solution | no_solution | no |
| 3.20 | 58.9 km/h | 1783 | yes | holds | no_solution | no_solution | no_solution | no |
| 3.40 | 55.4 km/h | 1894 | yes | holds | no_solution | no_solution | no_solution | no |
| 3.60 | 52.4 km/h | 2005 | yes | holds | no_solution | no_solution | no_solution | no |
| 3.77 | 50.0 km/h | 2100 | **OVER-SPEED** | holds | no_solution | no_solution | no_solution | no |
| 4.00 | 47.1 km/h | 2228 | **OVER-SPEED** | holds | holds | no_solution | no_solution | no |
| 4.50 | 41.9 km/h | 2507 | **OVER-SPEED** | holds | holds | no_solution | no_solution | no |
| 5.00 | 37.7 km/h | 2785 | **OVER-SPEED** | holds | holds | holds | no_solution | no |

Highest ratio that does not over-speed the engine at 105 km/h: **3.60**. Ratios that hold the 6% grade: **none**.

The two requirements do not overlap, and the gap is not marginal. At the highest ratio the cruise speed allows, axle A can put **11.7 kN** at the contact patch where the grade demands **24.0 kN**. This is not an engine problem - a 13 L in place of the downsized 11 L does not close a factor-of-two gap - it is the gearbox's problem, and S3 deleted the gearbox. A geared truck answers this by trading speed for torque; a fixed ratio cannot.

With the diesel axle unusable on the grade, the e-axle must carry the climb alone. On the 16 km 6% segment that is **133 kWh** of bus energy against **21.6 kWh** in the buffer - a shortfall of 111 kWh, or roughly six times the pack. S3 does not climb the mountain slowly; it does not climb it.

### 6.3 Regulatory startability, and what one driven axle costs

Requirement: Regulation (EU) No 1230/2012: five starts within five minutes at >= 12% gradient, laden to the combination's technically permissible maximum laden mass. Located by the Task 0 scan at search-summary level; provisional per E13 precedent.

That start needs **44.4 kN** at the contact patch at 36,300 kg. S3 assigns the whole of launch to axle B, a SINGLE driven axle carrying half the tandem load. The regulatory start therefore asks that one axle for roughly twice the friction coefficient a 6x4 tandem needs for the same start - the difference between a requirement comfortably met on most surfaces and one met on dry pavement only.

| surface | mu | mu needed, single axle | mu needed, 6x4 tandem | single axle can start | 6x4 tandem can start |
|---|---|---|---|---|---|
| dry | 0.70 | 0.587 | 0.293 | yes | yes |
| wet | 0.45 | 0.587 | 0.293 | **no** | yes |
| snow | 0.20 | 0.587 | 0.293 | **no** | **no** |
| ice | 0.10 | 0.587 | 0.293 | **no** | **no** |

Single-axle launch (S3's axle B) succeeds on: **dry**. A 6x4 tandem (S0, S1, S2, S4) succeeds on: **dry, wet**.

Not modelled: the five-starts-in-five-minutes clause is a THERMAL requirement on the traction machine; WS8 checks torque and adhesion only and does not model the repeat-duty temperature rise. Stated, not hidden.

### 6.4 S3: diesel-axle-only adhesion on cruise grades

One driven axle carries half the tandem load, so S3's cruise traction sits on half the adhesion a 6x4 has. Steepest grade holdable at 90 km/h on adhesion alone:

| surface | mu | axle A alone | 6x4 tandem (reference) |
|---|---|---|---|
| dry | 0.70 | 8.00% | 8.00% |
| wet | 0.45 | 8.00% | 8.00% |
| snow | 0.20 | 3.00% | 7.25% |
| ice | 0.10 | 0.75% | 3.00% |

Worst case **0.0075** (governing case: ice, mu 0.1), per R14.

### 6.5 S3: e-axle-fault limp capability

**IMMOBILE FROM REST. With axle B failed the only remaining prime mover is the diesel on a fixed ratio behind a rev-matched clutch that is specified for SYNCHRONISATION, not for launch slip. Below the coupling floor the engine cannot be connected at all, so the combination cannot be started from rest and cannot be recovered under its own power. This is a TOW event, not a limp-home.**

S3 is the only candidate in the trial with no launch device on the engine side. S0 has a slipping clutch and 12 gears; S1, S2 and S4 launch electrically and can still make bus power from the genset with the pack down.

Program precedent: R22(c): with no mechanical path BOTH Vehicle Zero variants share the genset-or-pack-fault = tow asymmetry. S3 inherits a STRICTER version - an e-axle fault alone is a tow - because its mechanical path cannot launch.

---

## 7. Capability shortfalls, reported rather than absorbed

bus energy the prime mover and pack together could not deliver. It is charged back as fuel so every candidate completes the same mission, and reported here raw because a large value is a CAPABILITY finding, not a fuel one.

Worst case **204.56 kWh** (governing case: `S3/grade_heavy/LH-520`), an explicit max over the enumerated (candidate, corner, cycle) set per R14.

Cases above 1 kWh:

| case | unserved kWh |
|---|---|
| `S3/grade_heavy/LH-520` | 204.56 |
| `S3/cold_minus10C/LH-520` | 183.78 |
| `S3/payload_plus20/LH-520` | 183.45 |
| `S3/nominal/LH-520` | 149.93 |
| `S3/payload_minus20/LH-520` | 127.35 |
| `S4/cold_minus10C/LH-520` | 112.51 |
| `S4/grade_heavy/LH-520` | 93.26 |
| `S4/payload_plus20/LH-520` | 89.63 |
| `S3/grade_heavy/REG-165` | 85.46 |
| `S4/nominal/LH-520` | 67.61 |
| `S3/cold_minus10C/REG-165` | 59.01 |
| `S3/payload_plus20/REG-165` | 50.59 |
| `S4/payload_minus20/LH-520` | 48.09 |
| `S3/nominal/REG-165` | 39.72 |
| `S1/payload_plus20/LH-520` | 16.61 |
| `S1/grade_heavy/LH-520` | 15.83 |
| `S1/cold_minus10C/LH-520` | 15.17 |
| `S1/nominal/LH-520` | 13.32 |
| `S1/payload_minus20/LH-520` | 9.99 |
| `S2/cold_minus10C/LH-520` | 7.73 |

---

## 8. External corroboration

None of the verdicts above depend on the prior-art scan. But the scan was run, and it is worth recording where it agrees - because three of this report's least comfortable conclusions turn out to be things the industry already knows. All figures in this section are EXTERNAL and search-summary level, provisional per E13 precedent; see `PRIOR_ART_WS8.md` for their evidence limits.

**On the size of the hybrid prize.** Volvo built and ran a long-haul hybrid concept tractor and reported the hybrid path alone at **5-10% fuel saving**, from shutting the engine off for up to 30% of driving time, with topography-optimal control. The widely-quoted 30% for that vehicle is the whole truck including aerodynamics. WS8's electrified candidates land on fuel per kilometre inside that 5-10% band - which is the reassuring outcome, not the disappointing one: a model that had produced 25% would have been wrong.

**On deleting the gearbox.** Across the products and programmes the scan found, the number of on-highway Class 8 vehicles in which a combustion engine drove the road wheels through a single fixed ratio with no gearbox anywhere is **zero**. The specific cases are sharper than the aggregate:

- **Hyliion Hypertruck ERX** is the only production-intent Class 8 that actually deleted the AMT. It did so by going series, decoupling the engine entirely - and still fitted a **two-speed gearbox on each of its two drive axles**.
- **ZF AxTrax 2 dual**, a clean-sheet Class 8 e-axle designed in the 2020s with no legacy constraint, is **three-speed**. **Allison's eGen Power** is two-speed, and Allison states S3's exact design tension in one sentence: the second ratio exists "to enable the high torque required to get heavy loads moving, while also offering superior efficiency at cruise speed".
- **Navistar's SuperTruck II** implemented the closest thing to S3's control law that has been demonstrated - electric owns launch and low speed, diesel takes over above a threshold - on a DOE-funded Class 8, and kept the multi-speed AMT while doing it.
- **Every e-axle overlay product** in the scan - Hyliion 6X4HE, Revoy, Range Energy, Trailer Dynamics - left the tractor's engine and AMT completely untouched. That is the commercial proposition, not an oversight.

Section 6.2 says why, from first principles and without reference to any of this. The two arrive at the same place independently, which is the strongest form of agreement available here.

**On the engine map.** The scan puts the lowest BSFC of mainstream heavy-duty truck diesels in volume commercial use at **182 g/kWh (46% brake thermal efficiency)**, with research engines demonstrating 55.7% BTE. S0's island is calibrated to 185.0 g/kWh - a production-class value, deliberately not a research one.

**A calibration warning the scan supplied.** SuperTruck fuel-economy headlines are frequently quoted at 65,000 lb GCVWR rather than 80,000 lb. WS8 runs at 36,300 kg (80,000 lb) throughout, so those headline figures are not comparable to anything in this report and are not used.

---

## 9. Recommendation

Criteria, pre-committed and quoted from the assignment: a candidate ADVANCES only if it beats S0 by >= 3.0% at nominal AND is >= 0.0% at every sensitivity corner. Read on the **ensemble_min** - the program's own precedent (BASELINE_v3 reads G1 on the ensemble min).

| candidate | nominal min | worst corner | worst corner min | passes nominal | passes corners | verdict |
|---|---|---|---|---|---|---|
| **S1** | -0.66% | cold_minus10C | -4.37% | False | False | **KILL** |
| **S2** | +0.36% | cold_minus10C | -1.90% | False | False | **KILL** |
| **S3** | -6.22% | cold_minus10C | -11.17% | False | False | **KILL** |
| **S4** | -3.67% | cold_minus10C | -8.26% | False | False | **KILL** |

- **S1: KILL** - fails the nominal >=3% criterion.
- **S2: KILL** - fails the nominal >=3% criterion.
- **S3: KILL** - fails the nominal >=3% criterion.
- **S4: KILL** - fails the nominal >=3% criterion.

**What WS8 recommends.** The numbers are above and the execute-or-spare decision is the lead's. What WS8 will say is this:

1. **No candidate clears the bar as specified.** The margins are not catastrophic - several candidates are within a point or two of S0 - but 'within a point or two' is not >= 3%, and the criteria were armed before the numbers were seen.
2. **S3 should be spared further work regardless of its fuel number.** Its fuel result is not the finding; its capability result is. A fixed-ratio diesel axle cannot hold the specified mountain grade at any ratio that also permits highway cruise, and an e-axle fault leaves the combination immobile from rest. Those are structural, not parametric.
3. **The binding constraint on this vehicle is mass, not efficiency.** Every electrified candidate wins on fuel per kilometre and gives it back on payload. Any future work that does not attack the powertrain mass ledger is not attacking the problem.
4. **What decides these architectures is the fleet's duty, not the architecture.** The corner sweep in section 6.1 spans about fourteen points for S1 - from roughly +10% on the grade-heavy corridor to about -4% at -10 C - and the sign flips inside that span. An operator running loaded over mountains and an operator running light in winter are not looking at the same vehicle. If Vehicle One is to be specified for a duty rather than for an average, that duty needs naming before any of these numbers mean much.
5. **The cold corner is the one to attack first.** It is binding for all four candidates, and its cause is specific and fixable rather than fundamental: WS3's cells accept about an eighth of their warm charge power at -10 C, so descent regen goes to the resistor instead of the pack, while the conventional truck heats its cab from engine coolant for free. Pack preconditioning and a heat-recovery path for cab heat are the obvious counters, and neither is modelled here.
6. **The escalations in section 11 change the answer if ruled the other way**, ESC-WS8-1 and ESC-WS8-3 especially. They are not footnotes.

---

## 10. First-principles sanity checks

**Road load at 95 km/h, flat, 36,300 kg.** By hand: aero 0.5 x 1.196 x 5.5 x 26.39^2 = **2,290 N**; rolling 0.0055 x 36,300 x 9.81 = **1,959 N**; total 4,249 N = 112.1 kW at the wheel. Model agrees: **True**.

2,533 N of aero and 1,959 N of rolling at 36.3 t is the whole line-haul problem in two numbers: above ~80 km/h the air is the bigger bill, which is why every candidate here wins or loses on driveline efficiency and mass, not on regenerative braking.

**The 6% mountain.** 21.3 kN of gravity, **533 kW** at 90 km/h. 21.4 kN of gravity on a 6% grade is 535 kW at 90 km/h. No candidate in this trial has that much continuous power, so every one of them climbs the mountain slower than it cruises - and the descent needs the same number back as RETARDING power, which is the case that sizes the sink.

**Scaling-law implementation.** Per-unit efficiency of the k=1.0 and k=3.6 machines at matched per-unit load agree to 0.0000 pp. loss(k; n, T) = k * loss_ws2(n, T/k) is per-unit invariant BY CONSTRUCTION, so this check confirms the implementation, not the physics. The physics claim is escalated separately (ESC-WS8-2).

**Generator scaling.** Same test on WS4's generator model: 0.000 pp across a 135 -> 303 kW stretch.

**Mass closure.** tare + payload = 36,300 kg for every candidate: **True**. the whole point of the metric: at fixed GCW, powertrain mass IS payload.

**S0 energy closure.** Fuel energy 1,960 kWh, engine shaft work 837 kWh - an implied engine efficiency of 0.4273 against 0.4277 implied by the duty-averaged BSFC. Agree: **True**.

**Envelope tabulation.** The integrator interpolates each candidate's envelope on a 0.05 m/s grid; worst relative error against direct evaluation 1.20e-03.

**Startability sizing.** The 12% start needs 44.4 kN; the electric paths are sized to deliver it and do (44.4 kN at 2 km/h), inside the 105.9 kN dry-tandem adhesion ceiling.

All checks pass: **True**.

---

## 11. Escalations

Escalations cite the ruling they challenge and are never self-resolved (CLAUDE.md rule 8). They go to the lead.

### ESC-WS8-1 - WS3's cell set is power-optimised and cannot fairly carry S4's traction pack

**Cites:** Assignment Task 3: 'battery basis from WS3's cell data'; WS3 results.json chemistry_trade; BASELINE_v3 'Pack per WS3 (unchanged, ratified): 288s1p LTO, 11.08 kWh usable'

**Finding.** WS3 characterised exactly three cells - LTO-23, LFP-P-20 and NMC-P-40 - all selected for a BUFFER duty on a 6.6 t vehicle, and all therefore power-oriented (>=3 C continuous). Their pack-level specific energies asymptote to 62.1, 83.0 and 85.6 Wh/kg. WS8 has used the best of them, NMC-P-40, for every pack. For S1, S2 and S3 that is defensible: those packs ARE buffers and the power rating is what they are bought for. For S4 it is not. A range-extended BEV's pack is an ENERGY store, and energy-optimised automotive cells sit at roughly double this pack-level density. S4's 150 kWh pack therefore masses 1788 kg on WS3's basis, and the payload that mass displaces is charged against S4 in the metric of record.

**Why this is not self-resolved.** Substituting a cell WS3 never characterised would be WS8 writing WS3's trade study, which rule 10 forbids and which would put an uncorroborated number into the headline.

**Asks.** Rule on ONE of: (a) S4's result stands on WS3's cell set as reported; (b) WS3 is reopened to characterise an energy-optimised cell and S4 is re-run; (c) WS8 is authorised to carry a cited external energy cell as an explicitly non-WS3 bracket.

**Materiality:** high - it is the difference between S4 advancing or not

### ESC-WS8-2 - The traction-machine stretch to k=3.6 is far beyond the range WS2 validated

**Cites:** R10, R13, R21 (WS2-E8/E9 accepted); WS2 run_ws2.py scaled_machine() stack-length rule; REPORT_WS2 section 1 item 1 (fixed saturated-bulk Ld, Lq, psi_m, no saturation map)

**Finding.** WS8's electric paths need a machine of about 3.6x the VM250-HV active length to meet the 12% startability specification at 36,300 kg on a single-speed reduction. WS8 applies WS2's OWN stack-length rule and WS2's own mass split (mass_end_kg = 18.0), so the LAW is inherited rather than invented - but WS2 exercised that rule over an 8:1-12:1 ratio sweep, a scale range of about 1.5x, not 3.6x. The record also contains a direct warning: R10 and R13 both predicted the crawl current would scale x0.56 and the computed answer was x0.685, a 22% error from reasoning about this machine by proportion. WS8 charges NO rotor-dynamics, shaft-stiffness or saturation penalty for the stretch.

**Why this is not self-resolved.** Re-deriving the machine at 3.6x would be doing WS2's work in WS8's folder.

**Asks.** Rule on whether the stretch may stand as the sizing basis, or whether WS2 must re-derive at semi scale before any WS8 electric result is ratified. Note the direction of the error: every candidate except S0 carries this machine, so it does not change their RANKING, only their common distance from S0.

**Materiality:** medium - common-mode across S1-S4, so ranking-neutral

### ESC-WS8-3 - The metric of record cannot see grid electricity, which decides what S4 even is

**Cites:** Assignment Task 3 metric of record: 'fuel energy per PAYLOAD tonne-km'; Task 3 S4: 'large pack + sustainer genset'

**Finding.** A range-extended BEV is bought to run on grid energy, with the sustainer covering what the pack cannot. The ordered metric counts FUEL energy only. WS8 has therefore run S4 CHARGE-SUSTAINING - it starts and ends the mission at the same state of charge, and any residual drift is priced back into fuel - because the alternative would let S4 import propulsion energy the metric is blind to and post a margin that is partly an accounting artefact. Under that treatment S4 is judged as a series hybrid with a small engine and a heavy pack, which is not the thing the name describes.

**Why this is not self-resolved.** Choosing whether Vehicle One admits an electricity term is a program-level metric decision, not a modelling choice.

**Asks.** Rule on whether Vehicle One's metric of record acquires an electricity term (and at what primary-energy or CO2 equivalence), or whether S4 is to be judged charge-sustaining as reported.

**Materiality:** high - it determines whether S4's result means what it appears to mean

### ESC-WS8-4 - R18's flat-rating ratio has been transferred to a 13 L class

**Cites:** R18, R24 (BASELINE_v3: flat-rating carried as a freeze-hold)

**Finding.** R18 rates the 4HK1-V2C at 132 kW continuous from a 153.3 kW automotive peak - a ratio of 0.861 - and R24 records that the datasheet item confirms a RATING, not a geometry. WS8 has applied the same 0.861 to the 13 L's 352 kW peak to get 303 kW continuous for the S1/S2 genset, and to the 7 L sustainer. That is a transfer of a ruled number to an engine class the ruling never contemplated.

**Why this is not self-resolved.** R18 is a ruling; only the lead amends it.

**Asks.** Confirm the transfer, or supply a Class 8 prime-power de-rating basis. The genset rating sets how fast S1 and S2 climb, so it moves their fuel and their trip time.

**Materiality:** medium

### ESC-WS8-5 - WS8 has re-anchored the speed term in WS4's ruled Willans construction

**Cites:** R12 chain conventions; WS4 ws4_models.WillansEngine._f_n

**Finding.** WS4's f_N is 1 - 0.06*((rpm-1600)/1400)^2, calibrated for a 700-3,000 rpm medium-duty engine. A Class 8 six runs 600-2,100 rpm and is built to be at its best near 1,200-1,300. Carrying WS4's centre unchanged would have placed the efficiency optimum 300-400 rpm too high and would have UNDER-penalised high-speed operation - which is precisely where S3's fixed ratio is forced to live. WS8 therefore uses 1 - 0.08*((rpm-1250)/1000)^2 and re-solves eta_i0 against it so the island BSFC target is unmoved. This is a change to an inherited model, declared here rather than made quietly.

**Why this is not self-resolved.** The Willans construction is WS4's ruled object; WS8 may not amend another workstream's model on its own authority.

**Asks.** Ratify the HD re-anchor for Vehicle One, or direct WS8 to carry WS4's medium-duty f_N unchanged and re-run. Note the direction: the re-anchor makes S3 look WORSE, so reverting it would not rescue S3.

**Materiality:** medium

### ESC-WS8-6 - S0 is specified with a compression brake only, and that hands the electric candidates a descent-speed advantage

**Cites:** R2 (the resistor sink is the only speed-independent retarder); assignment Task 3 'S0 baseline, calibrated'

**Finding.** S0's only retarder is its engine brake, which is strong at low road speed and weak at high. The electric candidates carry a brake resistor sized in the hundreds of kW and can hold the 6% descent at corridor speed while S0 must slow to about 62 km/h. That is a real architectural difference, and WS8 has modelled it rather than equalised it - but a line-haul tractor can be specified with a hydraulic retarder, and many are. The effect on the metric is small (it moves trip time and therefore accessory energy, not tractive work) but it is not zero, and it is a specification choice rather than a physical necessity.

**Why this is not self-resolved.** Whether the ruler carries a retarder is a baseline-specification decision.

**Asks.** Confirm S0's retarder specification, or direct a re-run with a hydraulic retarder on S0.

**Materiality:** low - affects trip time and accessory energy, not tractive work

### ESC-WS8-7 - S0's fuel exceeds the assignment's 30-38 L/100 km sanity corridor, and the model is not the reason

**Cites:** Assignment Task 2: 'Calibrate fleet fuel to a public reference band and state it (sanity corridor: 30-38 L/100 km loaded line-haul)'; Task 1: 'realistic grade distribution including sustained 2-3% and one 6% mountain segment with full descent'

**Finding.** S0's fleet-mission fuel is 38.78 L/100 km (ensemble 36.27 to 41.23), above the stated corridor. The calibration is nonetheless sound, and the cross-check says so directly: run over the SAME corridor with the grade zeroed - same distance, same speeds, same wind, same driver, same vehicle, nothing else touched - S0 burns 33.08 L/100 km, against the ICCT / TUV NORD figure of 32.6 L/100 km for a typical EU tractor-trailer over the regulatory Long Haul cycle and 33.1 L/100 km at that cycle's regulatory payload. That is a match to about one percent, reached with no fitting: the single calibration knob is solved against a declared BSFC island and nothing else is tuned.
The excess is TERRAIN. Task 1 ordered a corridor carrying a 6% mountain and sustained 2-3% sections - about 3,800 m of climb over 520 km - and a 30-38 L/100 km band describes a freeway-dominated regulatory cycle, not that road. The two orders are in tension, and WS8 has obeyed the one that governs the physics (Task 1's corridor) rather than adjusting the vehicle until Task 2's band was satisfied.

**Why this is not self-resolved.** Reconciling them would mean either flattening a corridor the assignment specified or tuning a vehicle parameter until a band was met - and tuning to a band is exactly what 'no fudge factor' forbids. Either change alters every candidate's result, so it is the lead's to make.

**Asks.** Rule on which governs: (a) the corridor as specified, with S0's fuel reported above the band and the flat cross-check standing as the calibration evidence (WS8's recommendation - it is the honest reading and the comparison between candidates is unaffected, since all five drive the same road); or (b) a flatter reference corridor, which would move every absolute fuel figure and none of the margins.

**Materiality:** low for the trial, high for the record - it changes no margin, because every candidate drives the same corridor, but it is a stated acceptance criterion not met and must not pass silently

---

## 12. Heat ledger for WS6 (rule 7)

component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation.

Worst-case rejection by component, an explicit max over the enumerated case set with the governing case labelled (R14):

| candidate | engine coolant | engine exhaust | traction machine inverter | generator rectifier | pack | brake resistor | total rejected |
|---|---|---|---|---|---|---|---|
| **S0** | 207 (climb_6pct) | 286 (climb_6pct) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 526 (climb_6pct) |
| **S1** | 159 (climb_6pct) | 219 (climb_6pct) | 35 (descent_6pct) | 16 (climb_6pct) | 7 (descent_6pct) | 211 (descent_6pct) | 447 (climb_6pct) |
| **S2** | 159 (climb_6pct) | 219 (climb_6pct) | 35 (descent_6pct) | 16 (climb_6pct) | 7 (descent_6pct) | 211 (descent_6pct) | 447 (climb_6pct) |
| **S3** | 74 (cruise_95kmh_flat) | 102 (cruise_95kmh_flat) | 35 (descent_6pct) | 0 (cruise_95kmh_flat) | 7 (descent_6pct) | 211 (descent_6pct) | 252 (descent_6pct) |
| **S4** | 116 (climb_6pct) | 160 (climb_6pct) | 35 (descent_6pct) | 9 (climb_6pct) | 13 (descent_6pct) | 0 (cruise_95kmh_flat) | 342 (climb_6pct) |

The descent case is the one that matters to WS6: a series candidate holding the 6% grade puts several hundred kilowatts into a resistor bank that has to reject it to air, and that is a packaging and airflow problem, not an electrical one.

---

## 13. Machine-readable interface (R14)

Every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline. This block is byte-identical to `results_ws8.json['interface_ws8']`; `verify_ws8.py` asserts it.

```json
{
 "_convention": "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); stochastic extrema are 8-seed ensemble envelopes (rule 4); every worst-case field is an explicit max/min over an enumerated case set with the governing case labelled (R14)",
 "metric_of_record": "fleet-mission fuel energy per PAYLOAD tonne-km [MJ/(t.km)], fleet mission = 70% LH-520 + 30% REG-165 by distance",
 "gcw_kg": 36300.0,
 "vehicle": {
  "CdA_m2": 5.5,
  "Crr": 0.0055,
  "r_dyn_m": 0.5,
  "provisional_per_E13_precedent": true
 },
 "candidates": {
  "S0": {
   "payload_kg": 20785.0,
   "powertrain_mass_kg": 2845.0,
   "fuel_correction_share": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.0,
    "median": 0.0,
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up - rather than fuel the model watched it burn. A large share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding"
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.0
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.621466084068082,
    "median": 0.6643461843959014,
    "max": 0.7064203333218632
   },
   "fleet_L_per_100km": {
    "min": 36.274410713277,
    "median": 38.77728321202376,
    "max": 41.23311305966629
   },
   "margin_vs_S0_pct": null,
   "worst_case_margin_pct": null,
   "verdict": "n/a (S0 is the ruler)"
  },
  "S1": {
   "payload_kg": 19397.719023795536,
   "powertrain_mass_kg": 4232.280976204462,
   "fuel_correction_share": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.02617445992878323,
    "median": 0.012011408699840666,
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up - rather than fuel the model watched it burn. A large share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding"
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 13.315260790597012
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6093614773205752,
    "median": 0.6605748118726468,
    "max": 0.7110855121237729
   },
   "fleet_L_per_100km": {
    "min": 33.19392164188724,
    "median": 35.98368022921403,
    "max": 38.73516401776123
   },
   "margin_vs_S0_pct": {
    "nominal_min": -0.6603970160332543,
    "nominal_median": 0.749159263367646,
    "nominal_max": 2.5844079093645207
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -0.6603970160332543,
     "payload_plus20": 0.17452438052964744,
     "payload_minus20": -2.17735552580396,
     "grade_heavy": 7.541186274978412,
     "cold_minus10C": -4.371889236281245
    },
    "value": -4.371889236281245,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S2": {
   "payload_kg": 19105.719023795536,
   "powertrain_mass_kg": 4524.280976204462,
   "fuel_correction_share": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.016585823098334895,
    "median": 0.0016817827337051116,
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up - rather than fuel the model watched it burn. A large share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding"
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 5.004926864660624
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6044564915649668,
    "median": 0.6530589465634276,
    "max": 0.7038476764354556
   },
   "fleet_L_per_100km": {
    "min": 32.431074457307844,
    "median": 35.03875566986641,
    "max": 37.76373770423473
   },
   "margin_vs_S0_pct": {
    "nominal_min": 0.3641821681872995,
    "nominal_median": 1.7002476992452409,
    "nominal_max": 2.737010584997872
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": 0.3641821681872995,
     "payload_plus20": 1.2396176704497184,
     "payload_minus20": -0.9836012154565411,
     "grade_heavy": 7.012715845172505,
     "cold_minus10C": -1.8964664040938248
    },
    "value": -1.8964664040938248,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S3": {
   "payload_kg": 19559.231387580392,
   "powertrain_mass_kg": 4070.768612419607,
   "fuel_correction_share": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.2339567816875219,
    "median": 0.14136366289568825,
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up - rather than fuel the model watched it burn. A large share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding"
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 149.9288312407515
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6262108325925635,
    "median": 0.6931731050176404,
    "max": 0.7503563181039591
   },
   "fleet_L_per_100km": {
    "min": 34.39578813602883,
    "median": 38.073814793447816,
    "max": 41.21470853064403
   },
   "margin_vs_S0_pct": {
    "nominal_min": -6.219524369505594,
    "nominal_median": -3.833303312350056,
    "nominal_max": -0.7634766636696604
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -6.219524369505594,
     "payload_plus20": -6.4217070625986885,
     "payload_minus20": -7.557200483746664,
     "grade_heavy": -1.8595225173143852,
     "cold_minus10C": -11.167471666325826
    },
    "value": -11.167471666325826,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S4": {
   "payload_kg": 19343.56414646685,
   "powertrain_mass_kg": 4286.4358535331485,
   "fuel_correction_share": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.0862402533630589,
    "median": 0.02786529090653877,
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION - unserved energy charged back as fuel, plus the charge-sustaining make-up - rather than fuel the model watched it burn. A large share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding"
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 67.60819477645745
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6140986357249582,
    "median": 0.6709323617675933,
    "max": 0.7323561704274769
   },
   "fleet_L_per_100km": {
    "min": 33.35857845188799,
    "median": 36.44585498795815,
    "max": 39.782470347110646
   },
   "margin_vs_S0_pct": {
    "nominal_min": -3.6714454386743602,
    "nominal_median": -0.9504424970630321,
    "nominal_max": 2.053361713748736
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -3.6714454386743602,
     "payload_plus20": -1.8665450751919042,
     "payload_minus20": -6.035690908614668,
     "grade_heavy": 5.752995843978538,
     "cold_minus10C": -8.262816427648133
    },
    "value": -8.262816427648133,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  }
 },
 "unserved_energy_kWh": {
  "rule": "max over the enumerated (candidate, corner, cycle) case set",
  "value": 204.56469919100863,
  "governing_case": "S3/grade_heavy/LH-520",
  "cases_over_1kWh": {
   "S1/cold_minus10C/LH-520": 15.171801498896768,
   "S1/grade_heavy/LH-520": 15.826776447536048,
   "S1/nominal/LH-520": 13.315260790597012,
   "S1/payload_minus20/LH-520": 9.990079031886157,
   "S1/payload_plus20/LH-520": 16.61450669184768,
   "S2/cold_minus10C/LH-520": 7.732061323787984,
   "S2/nominal/LH-520": 5.004926864660624,
   "S2/payload_minus20/LH-520": 3.6389883066745714,
   "S2/payload_plus20/LH-520": 7.17114665325612,
   "S3/cold_minus10C/LH-520": 183.78095929479554,
   "S3/cold_minus10C/REG-165": 59.008158312208835,
   "S3/grade_heavy/LH-520": 204.56469919100863,
   "S3/grade_heavy/REG-165": 85.45702696923918,
   "S3/nominal/LH-520": 149.9288312407515,
   "S3/nominal/REG-165": 39.716373446631856,
   "S3/payload_minus20/LH-520": 127.35398522872903,
   "S3/payload_minus20/REG-165": 4.491732620985521,
   "S3/payload_plus20/LH-520": 183.448432944331,
   "S3/payload_plus20/REG-165": 50.591244291216626,
   "S4/cold_minus10C/LH-520": 112.50709574645927,
   "S4/grade_heavy/LH-520": 93.25995103935864,
   "S4/nominal/LH-520": 67.60819477645745,
   "S4/payload_minus20/LH-520": 48.09132516294017,
   "S4/payload_plus20/LH-520": 89.63060373535257
  },
  "meaning": "bus energy the prime mover and pack together could not deliver. It is charged back as fuel so every candidate completes the same mission, and reported here raw because a large value is a CAPABILITY finding, not a fuel one."
 },
 "advance_kill": {
  "nominal_pct": 3.0,
  "every_corner_pct": 0.0,
  "statistic": "ensemble_min",
  "metric": "fleet-mission fuel energy per payload tonne-km",
  "pre_committed": true,
  "precedent": "BASELINE_v3 reads G1 on the ensemble min"
 },
 "advance_kill_result": {
  "S1": "KILL",
  "S2": "KILL",
  "S3": "KILL",
  "S4": "KILL"
 },
 "whr_gate": {
  "threshold_pct": 2.5,
  "result": {
   "S1": "DROPPED",
   "S2": "DROPPED",
   "S3": "DROPPED"
  },
  "best_net_margin_pct": {
   "S1": 1.7189267117781921,
   "S2": 1.754510159695374,
   "S3": 1.7882641374169403
  }
 },
 "S3_fixed_ratio_feasibility": {
  "rule": "a ratio is feasible only if it holds the 6% mountain grade AND keeps the engine under 2,100 rpm at 105 km/h; enumerated over the swept ratio set",
  "ratios_tested": [
   2.4,
   2.6,
   2.8,
   3.0,
   3.2,
   3.4,
   3.6,
   3.77,
   4.0,
   4.5,
   5.0
  ],
  "feasible_ratios": [],
  "any_feasible": false,
  "max_ratio_without_overspeed": 3.6,
  "governing_case": "6% mountain grade at 36,300 kg GCW"
 },
 "S3_diesel_axle_adhesion_grade_limit": {
  "rule": "min over the enumerated surface case set (R14)",
  "cases": {
   "dry": 0.08,
   "wet": 0.08,
   "snow": 0.03,
   "ice": 0.0075
  },
  "value": 0.0075,
  "governing_case": "ice, mu 0.1"
 },
 "S3_eaxle_fault": {
  "can_launch_from_rest": false,
  "verdict": "TOW (immobile from rest)"
 },
 "heat_ledger_WS6": {
  "convention": "component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation",
  "cases": [
   "cruise_95kmh_flat",
   "climb_6pct",
   "descent_6pct"
  ],
  "for_workstream": "WS6 heat ledger (CLAUDE.md rule 7)",
  "candidates": {
   "S0": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 69.7105241630927,
      "engine_exhaust_kW": 96.26691432046137,
      "driveline_kW": 11.67028281258527,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 177.64772129613934,
      "road_speed_kmh": 95.0
     },
     "climb_6pct": {
      "case_wheel_power_kW": 321.5825451745642,
      "engine_coolant_kW": 207.08960797752772,
      "engine_exhaust_kW": 285.98088720706215,
      "driveline_kW": 33.11982616133753,
      "traction_machine_inverter_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 526.1903213459274,
      "road_speed_kmh": 48.48106964927392
     },
     "descent_6pct": {
      "case_wheel_power_kW": -317.671324109552,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 234.04585537918877,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 234.04585537918877,
      "road_speed_kmh": 62.18177092125546
     }
    },
    "worst_case": {
     "brake_resistor_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     },
     "case_wheel_power_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 112.12477387259945,
       "climb_6pct": 321.5825451745642,
       "descent_6pct": -317.671324109552
      },
      "value": 321.5825451745642,
      "governing_case": "climb_6pct"
     },
     "driveline_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 11.67028281258527,
       "climb_6pct": 33.11982616133753,
       "descent_6pct": 0.0
      },
      "value": 33.11982616133753,
      "governing_case": "climb_6pct"
     },
     "engine_coolant_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 207.08960797752772,
       "descent_6pct": 0.0
      },
      "value": 207.08960797752772,
      "governing_case": "climb_6pct"
     },
     "engine_exhaust_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 285.98088720706215,
       "descent_6pct": 234.04585537918877
      },
      "value": 285.98088720706215,
      "governing_case": "climb_6pct"
     },
     "generator_rectifier_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     },
     "pack_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     },
     "total_rejected_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 177.64772129613934,
       "climb_6pct": 526.1903213459274,
       "descent_6pct": 234.04585537918877
      },
      "value": 526.1903213459274,
      "governing_case": "climb_6pct"
     },
     "traction_machine_inverter_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     }
    }
   },
   "S1": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "traction_machine_inverter_kW": 12.1946629399731,
      "generator_rectifier_kW": 7.28339094245689,
      "engine_coolant_kW": 71.5169582775221,
      "engine_exhaust_kW": 98.76151381181624,
      "driveline_kW": 5.04561482426698,
      "pack_kW": 1.91579155218859,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 196.71793234822388,
      "road_speed_kmh": 95.0
     },
     "climb_6pct": {
      "case_wheel_power_kW": 339.2161378353248,
      "traction_machine_inverter_kW": 32.82464034692015,
      "generator_rectifier_kW": 16.20163151924345,
      "engine_coolant_kW": 158.57050434954053,
      "engine_exhaust_kW": 218.9783155303179,
      "driveline_kW": 15.264726202589628,
      "pack_kW": 5.631611672733679,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 447.47142962134535,
      "road_speed_kmh": 51.00345113944995
     },
     "descent_6pct": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 0.0,
      "traction_machine_inverter_kW": 34.72869728739207,
      "pack_kW": 6.665965196428732,
      "brake_resistor_kW": 210.7103848497545,
      "total_rejected_kW": 252.1050473335753,
      "road_speed_kmh": 100.0
     }
    },
    "worst_case": {
     "brake_resistor_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 210.7103848497545
      },
      "value": 210.7103848497545,
      "governing_case": "descent_6pct"
     },
     "case_wheel_power_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 112.12477387259945,
       "climb_6pct": 339.2161378353248,
       "descent_6pct": -467.6379220181041
      },
      "value": 339.2161378353248,
      "governing_case": "climb_6pct"
     },
     "driveline_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 15.264726202589628,
       "descent_6pct": 0.0
      },
      "value": 15.264726202589628,
      "governing_case": "climb_6pct"
     },
     "engine_coolant_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 71.5169582775221,
       "climb_6pct": 158.57050434954053,
       "descent_6pct": 0.0
      },
      "value": 158.57050434954053,
      "governing_case": "climb_6pct"
     },
     "engine_exhaust_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 98.76151381181624,
       "climb_6pct": 218.9783155303179,
       "descent_6pct": 0.0
      },
      "value": 218.9783155303179,
      "governing_case": "climb_6pct"
     },
     "generator_rectifier_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 7.28339094245689,
       "climb_6pct": 16.20163151924345,
       "descent_6pct": 0.0
      },
      "value": 16.20163151924345,
      "governing_case": "climb_6pct"
     },
     "pack_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 5.631611672733679,
       "descent_6pct": 6.665965196428732
      },
      "value": 6.665965196428732,
      "governing_case": "descent_6pct"
     },
     "total_rejected_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 196.71793234822388,
       "climb_6pct": 447.47142962134535,
       "descent_6pct": 252.1050473335753
      },
      "value": 447.47142962134535,
      "governing_case": "climb_6pct"
     },
     "traction_machine_inverter_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 32.82464034692015,
       "descent_6pct": 34.72869728739207
      },
      "value": 34.72869728739207,
      "governing_case": "descent_6pct"
     }
    }
   },
   "S2": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "traction_machine_inverter_kW": 12.1946629399731,
      "generator_rectifier_kW": 7.28339094245689,
      "engine_coolant_kW": 71.5169582775221,
      "engine_exhaust_kW": 98.76151381181624,
      "driveline_kW": 5.04561482426698,
      "pack_kW": 1.91579155218859,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 196.71793234822388,
      "road_speed_kmh": 95.0
     },
     "climb_6pct": {
      "case_wheel_power_kW": 339.2161378353248,
      "traction_machine_inverter_kW": 32.82464034692015,
      "generator_rectifier_kW": 16.20163151924345,
      "engine_coolant_kW": 158.57050434954053,
      "engine_exhaust_kW": 218.9783155303179,
      "driveline_kW": 15.264726202589628,
      "pack_kW": 5.631611672733679,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 447.47142962134535,
      "road_speed_kmh": 51.00345113944995
     },
     "descent_6pct": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 0.0,
      "traction_machine_inverter_kW": 34.72869728739207,
      "pack_kW": 6.665965196428732,
      "brake_resistor_kW": 210.7103848497545,
      "total_rejected_kW": 252.1050473335753,
      "road_speed_kmh": 100.0
     }
    },
    "worst_case": {
     "brake_resistor_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 210.7103848497545
      },
      "value": 210.7103848497545,
      "governing_case": "descent_6pct"
     },
     "case_wheel_power_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 112.12477387259945,
       "climb_6pct": 339.2161378353248,
       "descent_6pct": -467.6379220181041
      },
      "value": 339.2161378353248,
      "governing_case": "climb_6pct"
     },
     "driveline_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 15.264726202589628,
       "descent_6pct": 0.0
      },
      "value": 15.264726202589628,
      "governing_case": "climb_6pct"
     },
     "engine_coolant_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 71.5169582775221,
       "climb_6pct": 158.57050434954053,
       "descent_6pct": 0.0
      },
      "value": 158.57050434954053,
      "governing_case": "climb_6pct"
     },
     "engine_exhaust_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 98.76151381181624,
       "climb_6pct": 218.9783155303179,
       "descent_6pct": 0.0
      },
      "value": 218.9783155303179,
      "governing_case": "climb_6pct"
     },
     "generator_rectifier_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 7.28339094245689,
       "climb_6pct": 16.20163151924345,
       "descent_6pct": 0.0
      },
      "value": 16.20163151924345,
      "governing_case": "climb_6pct"
     },
     "pack_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 5.631611672733679,
       "descent_6pct": 6.665965196428732
      },
      "value": 6.665965196428732,
      "governing_case": "descent_6pct"
     },
     "total_rejected_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 196.71793234822388,
       "climb_6pct": 447.47142962134535,
       "descent_6pct": 252.1050473335753
      },
      "value": 447.47142962134535,
      "governing_case": "climb_6pct"
     },
     "traction_machine_inverter_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 32.82464034692015,
       "descent_6pct": 34.72869728739207
      },
      "value": 34.72869728739207,
      "governing_case": "descent_6pct"
     }
    }
   },
   "S3": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "traction_machine_inverter_kW": 12.1946629399731,
      "engine_coolant_kW": 73.74833103432698,
      "engine_exhaust_kW": 101.84293333311822,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 5.04561482426698,
      "pack_kW": 1.91579155218859,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 194.74733368387388,
      "road_speed_kmh": 95.0
     },
     "climb_6pct": {
      "case_wheel_power_kW": 67.1058365767461,
      "traction_machine_inverter_kW": 15.072274568768705,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 3.0197626459535774,
      "pack_kW": 1.2836716671827233,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 19.375708881905005,
      "road_speed_kmh": 10.363776615838328
     },
     "descent_6pct": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 0.0,
      "traction_machine_inverter_kW": 34.72869728739207,
      "pack_kW": 6.665965196428732,
      "brake_resistor_kW": 210.7103848497545,
      "total_rejected_kW": 252.1050473335753,
      "road_speed_kmh": 100.0
     }
    },
    "worst_case": {
     "brake_resistor_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 210.7103848497545
      },
      "value": 210.7103848497545,
      "governing_case": "descent_6pct"
     },
     "case_wheel_power_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 112.12477387259945,
       "climb_6pct": 67.1058365767461,
       "descent_6pct": -467.6379220181041
      },
      "value": 112.12477387259945,
      "governing_case": "cruise_95kmh_flat"
     },
     "driveline_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 3.0197626459535774,
       "descent_6pct": 0.0
      },
      "value": 5.04561482426698,
      "governing_case": "cruise_95kmh_flat"
     },
     "engine_coolant_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 73.74833103432698,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 73.74833103432698,
      "governing_case": "cruise_95kmh_flat"
     },
     "engine_exhaust_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 101.84293333311822,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 101.84293333311822,
      "governing_case": "cruise_95kmh_flat"
     },
     "generator_rectifier_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     },
     "pack_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 1.2836716671827233,
       "descent_6pct": 6.665965196428732
      },
      "value": 6.665965196428732,
      "governing_case": "descent_6pct"
     },
     "total_rejected_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 194.74733368387388,
       "climb_6pct": 19.375708881905005,
       "descent_6pct": 252.1050473335753
      },
      "value": 252.1050473335753,
      "governing_case": "descent_6pct"
     },
     "traction_machine_inverter_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 15.072274568768705,
       "descent_6pct": 34.72869728739207
      },
      "value": 34.72869728739207,
      "governing_case": "descent_6pct"
     }
    }
   },
   "S4": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "traction_machine_inverter_kW": 12.1946629399731,
      "generator_rectifier_kW": 7.340991641487932,
      "engine_coolant_kW": 75.64238219508125,
      "engine_exhaust_kW": 104.45852779320745,
      "driveline_kW": 5.04561482426698,
      "pack_kW": 1.91579155218859,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 206.5979709462053,
      "road_speed_kmh": 95.0
     },
     "climb_6pct": {
      "case_wheel_power_kW": 362.8436983185366,
      "traction_machine_inverter_kW": 34.58357101912577,
      "generator_rectifier_kW": 9.00150167419477,
      "engine_coolant_kW": 115.74589034316658,
      "engine_exhaust_kW": 159.8395628548491,
      "driveline_kW": 16.32796642433416,
      "pack_kW": 6.012409040064941,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 341.51090135573526,
      "road_speed_kmh": 54.35272739270651
     },
     "descent_6pct": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "driveline_kW": 0.0,
      "traction_machine_inverter_kW": 34.72869728739207,
      "pack_kW": 12.987276741921372,
      "brake_resistor_kW": 0.0,
      "total_rejected_kW": 47.71597402931344,
      "road_speed_kmh": 100.0
     }
    },
    "worst_case": {
     "brake_resistor_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat"
     },
     "case_wheel_power_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 112.12477387259945,
       "climb_6pct": 362.8436983185366,
       "descent_6pct": -467.6379220181041
      },
      "value": 362.8436983185366,
      "governing_case": "climb_6pct"
     },
     "driveline_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 5.04561482426698,
       "climb_6pct": 16.32796642433416,
       "descent_6pct": 0.0
      },
      "value": 16.32796642433416,
      "governing_case": "climb_6pct"
     },
     "engine_coolant_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 75.64238219508125,
       "climb_6pct": 115.74589034316658,
       "descent_6pct": 0.0
      },
      "value": 115.74589034316658,
      "governing_case": "climb_6pct"
     },
     "engine_exhaust_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 104.45852779320745,
       "climb_6pct": 159.8395628548491,
       "descent_6pct": 0.0
      },
      "value": 159.8395628548491,
      "governing_case": "climb_6pct"
     },
     "generator_rectifier_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 7.340991641487932,
       "climb_6pct": 9.00150167419477,
       "descent_6pct": 0.0
      },
      "value": 9.00150167419477,
      "governing_case": "climb_6pct"
     },
     "pack_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 1.91579155218859,
       "climb_6pct": 6.012409040064941,
       "descent_6pct": 12.987276741921372
      },
      "value": 12.987276741921372,
      "governing_case": "descent_6pct"
     },
     "total_rejected_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 206.5979709462053,
       "climb_6pct": 341.51090135573526,
       "descent_6pct": 47.71597402931344
      },
      "value": 341.51090135573526,
      "governing_case": "climb_6pct"
     },
     "traction_machine_inverter_kW": {
      "rule": "max",
      "cases": {
       "cruise_95kmh_flat": 12.1946629399731,
       "climb_6pct": 34.58357101912577,
       "descent_6pct": 34.72869728739207
      },
      "value": 34.72869728739207,
      "governing_case": "descent_6pct"
     }
    }
   }
  }
 },
 "escalations": [
  "ESC-WS8-1",
  "ESC-WS8-2",
  "ESC-WS8-3",
  "ESC-WS8-4",
  "ESC-WS8-5",
  "ESC-WS8-6",
  "ESC-WS8-7"
 ],
 "ws2_chain_of_record": {
  "map_file": "data/effmap_motor_inverter_662V.csv",
  "map_voltage_V": 662.0,
  "ws2_rework_round": 4,
  "feasible_cells": 4203,
  "loader": "WS4 ws4_chain.WS2TractionChain (ruled), read-only"
 }
}
```

---

## 14. Provenance and reproduction

Inherited read-only from Vehicle Zero (CLAUDE.md rule 10 - nothing in another workstream's folder was modified):

- **WS2 r4** measured traction loss map `data/effmap_motor_inverter_662V.csv` at 662 V, 4,203 feasible cells, read through `WS4 ws4_chain.WS2TractionChain (ruled), read-only`
- **WS2** stack-length scaling rule and `mass_end_kg = 18.0` split, used verbatim as WS8's machine mass law
- **WS3** cell definitions, pack overhead model (1.55 x cell + 35 kg) and cold charge-acceptance figures
- **WS4** `WillansEngine`, `PMGenerator`, `derate_factor` and the R12 chain conventions; `WS2TractionChain` as the ruled map loader

Conventions carried:

- SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6)
- part-load models everywhere, no peak-point scalars (rule 5)
- stochastic extrema are 8-seed ensemble envelopes (rule 4)
- R14: every machine-readable worst-case field is an explicit max/min over an enumerated case set with the governing case labelled inline
- R12 chain: traction side = WS2 r4 measured maps x 0.97 reduction, no scalar PE member; genset-side rectifier in the generator model
- metric of record: fuel energy per PAYLOAD tonne-km

Reproduction:

```
cd WS8_semi_architecture
../.venv/bin/python run_ws8.py        # regenerates results_ws8.json
../.venv/bin/python make_report_ws8.py  # regenerates this report
../.venv/bin/python verify_ws8.py     # asserts report == results
```

Fixed seeds [8101, 8102, 8103, 8104, 8105, 8106, 8107, 8108].

### Regeneration check (rule 1): **PASS**

CLAUDE.md rule 1 requires that re-running the pipeline reproduces every committed artifact byte-identically. Checked in two independent halves, because the pipeline has two independent sources of possible drift: the simulation, and the derived blocks built on top of it.

**Half 1 - the simulation.** the full 8-seed nominal corner re-simulated FROM SCRATCH in a separate process with a separate worker pool (run_ws8.py --jobs 3 --only-nominal), then its trial slice compared against the committed run. Result: trial slice **byte-identical** (sha256 `bccb2920a42dfe73...`); cycle ensemble identical; S0 calibration identical.

Wall-clock fields are excluded from the comparison and from the committed artifact alike: per-candidate and total runtimes are the only values in this structure that cannot reproduce, and _strip_runtimes removes them before the record is written.

**Half 2 - the derived blocks.** run_ws8.py --from-checkpoint run twice over the same checkpoint; results_ws8.json and all seven data/*.csv exports compared byte-for-byte. Result: `results_ws8.json` **byte-identical**, and all 7 CSV exports byte-identical.

**Not checked:** the four sensitivity corners and the WHR gate were not re-simulated from scratch — they are the same code path as the nominal corner with different Ctx constants, and re-running them would have cost another hour of compute for no additional class of evidence. Stated rather than implied.
