# REPORT WS8 - VEHICLE ONE: SEMI-SCALE ARCHITECTURE TRIAL

Workstream WS8, Vehicle One. Executes `WS8_semi_architecture/ASSIGNMENT.md`, and the round ordered by `WS8_semi_architecture/R3_DIRECTIVE.md (R35); numbers r3, verdicts executed under R25`, against `BASELINE_v5.md`.

**Numbers version r3.** The verdicts are `executed_kill_2026-08-30` - R25 executed all four kills and the WHR drop on the pre-committed criteria, and **this round does not reopen them**. What r3 does is make the NUMBERS of record correct: the blocking finding B1 and the eleven material and minor ones from `FINDINGS_WS8_r2.md` are closed here, every corner is re-simulated, and section 15 states which direction each candidate moved and why - measured, not asserted (finding M1).

**The r2 numbers and the r2 heat ledger are SUPERSEDED, not amended.** r2's control law let an engine fuel while the same crankshaft was compression-braking (B1), so r2's S2 and S3 fuel numbers and its largest ledger row are withdrawn. S0, S1 and S4 are re-run unchanged in control law; their small movements are the r3 accounting corrections the extended run closure found, and they are measured in `one_factor_S1_vs_S2`. WS6 consumes only the `ledger_version: r3` ledger (R3_DIRECTIVE item 7).

**Nothing here is ratified.** The lead ratifies in a separate chat (CLAUDE.md rule 11). This report states what the physics gave and what it cost; the execute-or-spare decision is the lead's.

**This report is generated**, not written: every number below is formatted out of `results_ws8.json` by `make_report_ws8.py`, and `verify_ws8.py` asserts independently that each rendered figure appears verbatim and that the interface block equals `results_ws8.json['interface_ws8']`. Nothing was transcribed by hand (rule 2).

| | |
|---|---|
| Entry point | `run_ws8.py` (fixed seeds 8101..8108, 8 seeds) |
| Baseline of record | BASELINE_v5.md |
| Python / numpy | 3.14.3 / 2.5.2 |
| Metric of record | fuel energy per **payload** tonne-km [MJ/(t.km)] |
| Fleet mission | 70% LH-520 + 30% REG-165 by distance |

---

## 0. What this trial found

**No candidate advances.** S1, S2, S3, S4 all fail the pre-committed criteria.

The trial is decided by a single structural fact, and it is worth stating before any table: **at fixed gross combination weight, powertrain mass is payload.** S1, S2, S3, S4 win per kilometre against the conventional truck on every seed. Every candidate here is also heavier. The metric of record divides one by the other, and that division is what the assignment ordered precisely because it is where the argument actually lives.

*(r2 finding M2: the sentence above used to read "Every candidate here is more efficient per kilometre than the conventional truck" as a hard-coded literal, and it was false for S3. It is generated from `interface_ws8.per_km_margin_paired` now, on the PAIRED per-seed statistic - the same statistic as every margin in this report.)*

S0, the ruler, burns **38.78 L/100 km** on the fleet mission. That is above the assignment's 30-38 L/100 km corridor, and the reason is the corridor itself rather than the model: run over the same road with the grade zeroed, S0 burns **33.08 L/100 km** median on an 8-seed envelope of 29.82 to 39.36, against a published 32.6 L/100 km for a typical EU tractor-trailer over the regulatory Long Haul cycle - consistent with the public band, with nothing fitted to it (section 3.4 states what that envelope does and does not support). Task 1 ordered 3,704 m of climb over 520 km (8-seed ensemble 3,507 m to 3,838 m); a 30-38 band describes a freeway. Reported, not tuned away, and escalated as ESC-WS8-7.

- **S1**: per-kilometre energy against S0 +7.36% (PAIRED per-seed median, positive = less energy per km; envelope +6.03% to +9.07%), and it carries 1,387 kg less payload. Net on the metric of record: +0.73% (median), -0.69% (ensemble min). **KILL**.
- **S2**: per-kilometre energy against S0 +9.81% (PAIRED per-seed median, positive = less energy per km; envelope +8.62% to +11.06%), and it carries 1,679 kg less payload. Net on the metric of record: +1.89% (median), +0.59% (ensemble min). **KILL**.
- **S3**: per-kilometre energy against S0 +7.44% (PAIRED per-seed median, positive = less energy per km; envelope +4.88% to +9.05%), and it carries 1,226 kg less payload. Net on the metric of record: +1.64% (median), -1.09% (ensemble min). **KILL**.
- **S4**: per-kilometre energy against S0 +5.95% (PAIRED per-seed median, positive = less energy per km; envelope +3.36% to +8.78%), and it carries 1,441 kg less payload. Net on the metric of record: -1.06% (median), -3.84% (ensemble min). **KILL**.

S3 fails for a reason that has nothing to do with fuel, and it is the most useful result in this report: **no fixed ratio exists that lets a diesel axle both cruise at 105 km/h and hold the 6% mountain grade at 36,300 kg.** The two requirements are not close: the cruise ceiling is **3.77:1**, solved in closed form as an rpm limit at a road speed (finding F12), and the grade needs **6.88:1**, a factor of 1.8. The second of those is a SWEPT result and r3 says so (r2 minor m1) - ten times the grid resolution in both dimensions moves it by 0.009 and the engine speed at 105 km/h by 5 rpm, against a gap of 1,732 rpm over the ceiling. That is not a tuning problem, and it is the answer to the question S3 was posed to ask.

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
| regional REG-165 [L/100 km] | 33.17 | 35.15 | 39.35 |
| **fleet mission** [L/100 km] | 36.28 | 38.78 | 41.23 |

Fleet fuel is inside the 30-38 L/100 km corridor on every seed: **False**. Fudge factor applied: **False**. eta_i0 is SOLVED so the map minimum lands exactly on the declared 185.0 g/kWh island; nothing else is tuned. The fleet fuel that comes out is whatever the physics gives, and it is checked - not fitted - against the corridor.

### 3.4 Cross-check against the public reference band

The corridor this trial runs is not a regulatory cycle - Task 1 ordered a 6% mountain and sustained 2-3% sections, 3,704 m of climb over 520 km (8-seed ensemble 3,507 m to 3,838 m). Comparing its fuel directly against a freeway-dominated published figure would compare two different roads. So the cross-check runs S0 over the **same corridor with the grade zeroed** - same distance, same speeds, same wind, same driver, same vehicle, nothing else touched - which isolates terrain and makes the comparison like-for-like.

**This is stated as an ENSEMBLE, not a median** (rule 4, and r1 finding F7: r1 rested the whole calibration argument on a single median while the envelope for the same quantity was already computed, stored, and wider than the public band).

| | L/100 km, 8-seed min / median / max |
|---|---|
| S0, LH-520 as ordered | 36.79 / 39.57 / 44.69 |
| **S0, same corridor with grade zeroed** | **29.82 / 33.08 / 39.36** |
| ICCT / TUV NORD, typical EU tractor-trailer, regulatory Long Haul | 32.6 |
| ICCT / TUV NORD, at that cycle's regulatory payload (19.3 t) | 33.1 |
| ICCT / TUV NORD, best-in-class EU | 29.9 |

Source: ICCT / TUV NORD, fuel consumption testing of tractor-trailers in the EU and US, over the EU regulatory Long Haul cycle. Evidence quality: located via server-side search only; the primary document could not be fetched in this environment, so the figure is provisional per E13 precedent.

**And it is not mass-matched.** The reference cycle carries 19.3 t of payload; WS8's S0 carries more, at the assignment's fixed 36,300 kg GCW. The three enumerated mass cases say what that is worth:

| combination | payload | GCW | L/100 km, min / median / max |
|---|---|---|---|
| as reported 36300kg GCW | 20,785 kg | 36,300 kg | 29.82 / 33.08 / 39.36 |
| mass matched to ICCT 19p3t payload | 19,300 kg | 34,815 kg | 29.31 / 32.58 / 38.83 |
| EU regulatory 40000kg GCW | 24,485 kg | 40,000 kg | 31.06 / 34.34 / 40.67 |

**What the evidence supports.** The grade-zeroed median sits +1.5% from the published typical figure - but the 8-seed envelope spans 9.54 L/100 km against a public band 3.20 L/100 km wide, so the envelope is wider than the band it is being compared against. the MEDIAN of the grade-zeroed ensemble lands close to the public typical figure, but the 8-seed envelope is wider than the public band itself, so the honest claim is that the model is CONSISTENT WITH the band - not that it matches it to one percent. Nothing was fitted to it either way: the single calibration knob is solved against a declared BSFC island.

A model that lands near the public band on flat ground and above it on a mountain corridor is behaving; one that matched the public band on a mountain corridor would be wrong.

On the corridor as ordered, S0 exceeds the assignment's 30-38 L/100 km band by 3.23 L/100 km. That is reported, not tuned away, and escalated as ESC-WS8-7: the excess is terrain, and every candidate drives the same road, so no margin in this report is affected by it.

Duty-averaged BSFC on the line-haul corridor is 196.8 g/kWh against the 185.0 g/kWh island - the gap between the two is the whole of the hybrid opportunity, and it is smaller than it is at Vehicle Zero scale because a line-haul truck already spends 0.72 of its moving time in top gear near its best point.

---

## 4. Candidate results (Task 3) - the headline

All five at **36,300 kg GCW**, the assignment's fixed condition. Because GCW is fixed, the road-load physics is identical for every candidate: mass does not change how the truck drives, it changes what the truck may carry. Payload is stated explicitly for each.

| | architecture | payload | powertrain | fleet L/100 km | MJ/payload-tkm (min / median / max) | margin vs S0 (min / median / max) | fuel that is correction | verdict |
|---|---|---|---|---|---|---|---|---|
| **S0** | Conventional 13 L diesel + 12-speed AMT, direct top gear | 20,785 kg | 2,845 kg | 38.78 | 0.6215 / 0.6644 / 0.7064 | - (ruler) | 0.0% | **RULER** |
| **S1** | Pure series - Vehicle Zero's architecture scaled to Class 8 | 19,398 kg | 4,232 kg | 35.99 | 0.6095 / 0.6607 / 0.7113 | -0.69% / +0.73% / +2.57% | 2.7% | **KILL** |
| **S2** | Single cruise-ratio + torque-fill, traction machine on a disconnect | 19,106 kg | 4,524 kg | 34.97 | 0.6018 / 0.6518 / 0.7023 | +0.59% / +1.89% / +3.24% | 2.3% | **KILL** |
| **S3** | Tandem split - diesel axle on ONE fixed ratio (no gearbox anywhere) + disconnectable e-axle | 19,559 kg | 4,071 kg | 36.01 | 0.6007 / 0.6556 / 0.7141 | -1.09% / +1.64% / +3.35% | 38.5% | **KILL** |
| **S4** | Range-extended BEV - large pack + 194 kW-shaft / 185 kW-bus sustainer genset | 19,344 kg | 4,286 kg | 36.48 | 0.6146 / 0.6715 / 0.7336 | -3.84% / -1.06% / +1.98% | 8.8% | **KILL** |

The last column before the verdict is the one to read sceptically. It is the fraction of a candidate's reported fuel that is a **correction** rather than fuel the model watched it burn: energy its prime mover and pack could not deliver, charged back as fuel so that every candidate is compared having completed the same mission at the same speeds, plus the charge-sustaining correction. A small share is bookkeeping. A large positive share means the candidate did not really do the mission, and the fuel number is flattering it - which is why the raw shortfall is reported separately in section 7 rather than left inside a single figure.

**The charge-sustaining correction is SYMMETRIC, and r1 did not say so** (finding F4). A pack that ends the mission FLATTER than it started is charged the make-up; a pack that ends FULLER earns the corresponding **credit**. That is the convention of record - SAE J1711 in spirit - applied identically to every candidate with a pack, and it is declared here rather than left for a reader to discover. It matters:

| | correction share, min / median / max | charge-sustaining direction over the (cycle, seed) set | margin of record | margin with the CREDIT suppressed |
|---|---|---|---|---|
| **S1** | +0.7% / +1.2% / +2.7% | make-up on 16/16 cases | -0.69% / +0.73% | -0.69% / +0.73% |
| **S2** | -1.7% / +0.8% / +2.3% | **credit** on 7/16 (cycle, seed) cases | +0.59% / +1.89% | +0.51% / +1.07% |
| **S3** | +15.8% / +19.2% / +38.5% | **credit** on 4/16 (cycle, seed) cases | -1.09% / +1.64% | -1.09% / +1.20% |
| **S4** | +0.2% / +2.9% / +8.8% | make-up on 16/16 cases | -3.84% / -1.06% | -3.84% / -1.06% |

Section 4.4 takes that apart one factor at a time, because the round-1 adjudication found these corrections were what decided the order of the two leading candidates.

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

**S2** - One fixed reduction (2.60:1 overall) can couple the engine to the wheels inside a cruise lockup band; outside that band the truck is pure series. THE COUPLING LAW, declared: the lockup clutch is CLOSED when the engine is pulling inside the band, and when its compression brake is being drawn; it is OPEN otherwise, including while coasting or while regen alone is doing the retarding. Whenever it is closed and the vehicle asks for no traction the engine is in OVERRUN - the wheels turn it, the compression brake is what they turn it against, and the genset makes nothing and burns nothing, because one crankshaft cannot be locked to the road and on a free-speed BSFC locus at the same time (the one rule, r2 finding B1). How much of the band that leaves alone is measured, not argued: see `inband_overrun_no_engine_brake_fraction_moving`. The traction machine sits behind a DISCONNECT, so while locked and not filling it is stationary and its spin drag is zero - which deletes the G1(b) member by hardware, a member that costs almost nothing here in any case (section 4.2 gives the measured charge and its bracket). Every remaining tax is charged: the machine's losses whenever it IS connected (measured, from WS2's map, not a scalar), and the engine's off-best-point operation at band edges, where road speed - not the supervisor - sets engine speed. There is ONE crankshaft and it has one speed and one full-load curve: while locked, traction torque is allocated first, then accessories, then the generator gets whatever torque is left and its fuel is priced at the ROAD-IMPOSED speed, not on the free-speed BSFC locus. Accessory duty the crank has no torque left to carry moves to the bus.

**S3** - Axle A: downsized diesel through a single fixed reduction and a rev-matched clutch. There is NO gearbox and NO generator, so the engine can do exactly one thing - turn axle A - and only above the road speed at which the fixed ratio puts it above its lugging limit. Below that speed the clutch opens and the engine SHUTS DOWN, because with no generator there is nothing else for it to drive. Axle B: a disconnectable e-axle owning launch, low speed, regen and peak assist, fed by a buffer pack that can only be refilled by regen or by through-the-road charging (engine pushes axle A, e-axle harvests on axle B) - a lossy path taken only when the engine is lightly loaded and the pack is below target.
BOTH G1 TAXES DELETED BY CONSTRUCTION, not by assumption: (a) the map-vs-scalar member cannot recur because no scalar chain efficiency exists anywhere in WS8 - every electric sample goes through WS2 r4's measured loss surface; (b) the spin-drag member is deleted by the e-axle's disconnect, and the code charges spin drag ONLY on samples where that disconnect is closed, so the deletion is auditable rather than asserted.

**S4** - Electric traction only; a small sustainer genset holds charge. Run CHARGE-SUSTAINING over the mission (the pack ends where it started), because the metric of record is FUEL energy and no electricity accounting was ordered: crediting a plug-in start would let S4 import propulsion energy the metric cannot see. That choice is stated, and its consequence - that S4 is judged as a series hybrid with a small engine and a heavy pack, not as a plug-in - is escalated rather than buried.

**What R22(d) actually costs here, measured** (r2 minor m7). S2's traction disconnect and S3's e-axle disconnect are real hardware and they are charged for in mass. What they delete is a tax that this driver model barely levies on anyone: the integrator is always either pulling or braking, so the unloaded-and-geared test almost never fires. The charge is reported with the COAST-PERMITTING BRACKET beside it - what the same measured zero-torque loss would cost if it were charged on every geared moving sample - so the near-zero is read as a property of the driver model rather than as an architectural win:

| candidate | R22(d) charged kWh | coast-permitting bracket kWh | disconnect fitted |
|---|---|---|---|
| **S0** | 0.0000 | 0.00 | none |
| **S1** | 0.0041 | 38.06 | none |
| **S2** | 0.0026 | 13.83 | `traction_disconnect` (42 kg) |
| **S3** | 0.0044 | 18.16 | `eaxle_disconnect` (42 kg) |
| **S4** | 0.0048 | 38.12 | none |

The bracket is NOT in any margin. Read the two columns together: the charged column is what the trial priced, and the difference between the columns is what a coasting duty cycle would have priced.

---

### 4.3 Two-speed traction bracket (informative)

The Task 0 product sweep found something that bears directly on how these candidates were sized: **every heavy truck that actually deleted its AMT still fitted a multi-speed gearbox on the traction side** - Hyliion Hypertruck ERX, ePower, ReVolt, Edison, Wrightspeed, BAE - and the heavy-duty e-truck transmission literature finds a three-speed gives the lowest energy consumption that still meets gradeability. WS8's electric candidates were sized on a SINGLE fixed reduction, because WS2's carried 7,200 rpm rotor limit caps the ratio at 12:1 and the 12% startability specification then sets the machine size.

With a two-speed (24:1 low / 12:1 high) the startability torque is met at half the stretch factor, so the machine halves under WS2's own mass law while the box is added back:

| | k, single-speed | k, two-speed | e-drive mass | + box | net mass | payload gain | margin vs S0 | gain |
|---|---|---|---|---|---|---|---|---|
| **S1** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +0.73% -> +1.20% | +0.46 pp |
| **S2** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +1.89% -> +2.35% | +0.47 pp |
| **S4** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | -1.06% -> -0.59% | +0.47 pp |

Margins here are on the **median of per-seed paired margins vs S0, the same statistic as the headline (r1 finding F10: this was a ratio of medians and the basis was not stated)**.

**informative bracket, fuel per km held at the single-speed value; not the metric of record.** Fuel per kilometre is held at the single-speed value, which makes the bracket conservative: a smaller machine at a higher per-unit load is slightly more efficient at cruise, not less. It changes no verdict in this report - the gains are fractions of a point - but it says where the next mass is, and it says the industry already knew.

---

### 4.4 One factor at a time: what each correction was worth

r1 put S2 ahead of S1 on the nominal median. The round-1 adjudication showed that about half of S2's advantage was the charge-sustaining **credit** (F4), and that S2's single engine was being run as a locked mechanical drive and a free-speed genset at the same time, with nothing capping their sum at the full-load curve (F3). r3 widens the table from the S1-vs-S2 pair to all four candidates and adds rows for its own corrections - the control rule B1, and the launch-fuel fix that moves THE RULER - because r2 finding M1 is that the DIRECTION of every correction must be measured here rather than written into a changelog cell by hand. On a RE-SIMULATED row, a candidate the switch does not reach comes back bit-identical, which is a proof rather than an assertion; on the two exact RE-PRICING rows a zero means the candidate carries none of that correction, and the direction cells say which kind of zero they are.

each row reverts EXACTLY ONE correction and leaves the rest applied; margins are the same paired per-seed ensemble as the headline, at the nominal corner. S0 is unaffected by every correction in this set (no errata switch reaches it), so the ruler is the same in every row - which is why a row's DELTA against `r3_as_reported` IS the direction that correction moved that candidate.

*Direction convention.* margin = (S0 - candidate)/S0 x 100, so HIGHER IS BETTER. delta = median(r3_as_reported) - median(row); delta > 0 means the correction moved the candidate UP, i.e. it was FOR that candidate; delta < 0 means AGAINST. A candidate whose delta is exactly 0.0 in a row is that correction PROVED not to reach it, not an assertion that it does not.

| row | S1 min / median / max | S2 min / median / max | S3 min / median / max | S4 min / median / max | ordering |
|---|---|---|---|---|---|
| `r3_as_reported` | -0.69% / **+0.73%** / +2.57% | +0.59% / **+1.89%** / +3.24% | -1.09% / **+1.64%** / +3.35% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `F4_reverted_credit_removed` | -0.69% / **+0.73%** / +2.57% | +0.51% / **+1.07%** / +2.45% | -1.09% / **+1.20%** / +2.31% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `F6_reverted_peak_point_pricing` | -0.66% / **+0.75%** / +2.59% | +0.64% / **+1.90%** / +3.26% | +1.04% / **+3.62%** / +4.91% | -3.67% / **-0.95%** / +2.06% | S2 ahead of S1 |
| `F3_reverted_engine_dual_use` | -0.69% / **+0.73%** / +2.57% | +0.47% / **+1.82%** / +2.83% | -1.09% / **+1.64%** / +3.35% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `F5_reverted_spin_rule` | -0.69% / **+0.73%** / +2.57% | +0.54% / **+1.84%** / +3.19% | -3.28% / **-0.42%** / +1.18% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `F3_and_F5_reverted` | -0.69% / **+0.73%** / +2.57% | +0.41% / **+1.77%** / +2.80% | -3.28% / **-0.42%** / +1.18% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `B1_reverted_brake_and_fuel` | -0.69% / **+0.73%** / +2.57% | +0.48% / **+1.80%** / +3.18% | -5.80% / **-3.62%** / +0.99% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |
| `R3_S0_launch_fuel_reverted` | -0.69% / **+0.73%** / +2.57% | +0.59% / **+1.89%** / +3.24% | -1.09% / **+1.64%** / +3.35% | -3.84% / **-1.06%** / +1.98% | S2 ahead of S1 |

- **`r3_as_reported`** - the margin of record: every r2 and r3 correction applied
- **`F4_reverted_credit_removed`** - the symmetric charge-sustaining CREDIT suppressed (the deficit make-up kept). Exact re-pricing of the same run.
- **`F6_reverted_peak_point_pricing`** - corrections priced at r1's peak-point efficiency instead of the candidate's duty average. Exact re-pricing of the same run.
- **`F3_reverted_engine_dual_use`** - S2's single engine run as a locked mechanical drive AND a free-speed genset at the same time, uncapped - r1's treatment. Re-simulated.
- **`F5_reverted_spin_rule`** - R22(d) charged on r1's two different unloaded tests instead of the one program-wide rule. Re-simulated.
- **`F3_and_F5_reverted`** - both r2 re-simulated corrections reverted; F4, F6 and B1 still applied. Re-simulated.
- **`B1_reverted_brake_and_fuel`** - THE r3 CORRECTION (R3_DIRECTIVE item 1). Reverted: the engine may fuel while the same crankshaft is compression-braking - S3's through-the-road charging gated on axle-A force being small rather than on the vehicle not braking, and S2's free-speed genset running while its lockup coupling is drawing the compression brake. Everything else r3 corrected is UNCONDITIONAL and stays applied in this row, so the row isolates the control law and nothing else. Re-simulated.
- **`R3_S0_launch_fuel_reverted`** - THE RULER'S OWN r3 CORRECTION. Reverted: S0 is fuelled at the idle rate on the first few tenths of a second of every pull-away, as it was in r1 and r2, while the model credits it with launch torque. This row is measured against ITS OWN re-run S0, so the delta against `r3_as_reported` is the effect of the RULER moving. Re-simulated, all five candidates.

**The direction of each correction, MEASURED** (r2 finding M1). Every cell below is computed from the rows above by `correction_directions()`; nothing in it is written by hand, and `verify_ws8.py` asserts the rendered strings verbatim.

| correction | direction | basis |
|---|---|---|
| **F3** | FOR S2 (+0.070 pp); does not reach S1, S3, S4 (re-run bit-identical) | `F3_reverted_engine_dual_use` |
| **F4** | FOR S2 (+0.821 pp), S3 (+0.434 pp); does not reach S1, S4 (carries none of this correction) | `F4_reverted_credit_removed` |
| **F5** | FOR S2 (+0.052 pp), S3 (+2.055 pp); does not reach S1, S4 (re-run bit-identical) | `F5_reverted_spin_rule` |
| **F6** | AGAINST S1 (-0.018 pp), S2 (-0.014 pp), S3 (-1.978 pp), S4 (-0.112 pp) | `F6_reverted_peak_point_pricing` |
| **F3_and_F5** | FOR S2 (+0.113 pp), S3 (+2.055 pp); does not reach S1, S4 (re-run bit-identical) | `F3_and_F5_reverted` |
| **R3_S0_launch_fuel** | FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp) | `R3_S0_launch_fuel_reverted` |
| **B1** | FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical) | `B1_reverted_brake_and_fuel` |

*F6's direction is NOT the same at every corner - it flips for S2 - so the direction cell is stated at the nominal corner and the per-corner table is exported beside it.*

**The ordering is robust to these corrections**: it is the same in every row above.

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
| S1 | ETC+ORC | +1.75% | +1.65% | >= 2.5% | **DROPPED** |
| S2 | ETC+ORC | +1.83% | +1.57% | >= 2.5% | **DROPPED** |
| S3 | ETC+ORC | +2.38% | +1.93% | >= 2.5% | **DROPPED** |

**Dropped, without ceremony.** Two things kill it, and the second is the interesting one.

First, the mass charge: the metric divides by payload, so the systems have to win back the gate plus what their mass displaced - the table above shows the real bar is nearer 3-4% than 2.5%.

Second, and more fundamental: **line-haul cruise is a part-load condition, and waste-heat recovery is a full-load technology.** Holding 36,300 kg at 95 km/h on level road needs about 100 kW at the wheel; on a 350 kW-class engine that is roughly a third of rated. Both systems modelled here are negligible below 30-35% load by construction, because exhaust mass flow and temperature both collapse there. The engine spends most of the mission in exactly the region where there is little enthalpy to recover, and the minutes it spends on the mountain at high load are too few to pay for the mass it carries for the other five hours.

This is not an argument that waste-heat recovery does not work. It is an argument that it does not pay ON THIS METRIC, on this duty, against a payload-denominated criterion that was armed before the numbers were seen.

---

## 6. Sensitivities (Task 5)

### 6.1 Corner sweep

Margins vs S0 [%], ensemble min / median, at every corner. Note that at the payload corners GCW moves with payload: the fixed-GCW condition is a Task-3 condition, not a Task-5 one.

**Two things about this table changed in r2.** The **-10 C** corner now applies WS3's cold charge acceptance, which r1 named in the corner label, in the provenance list and in Recommendation 5 but never called: S1's buffer takes 30.5 kW there against 240.0 kW warm - both BUS-SIDE continuous ratings, and the envelope applies that bus-side number as a wheel-side force cap (`min(f_gen, chg*1e3/v)`), which is conservative and is r2 minor m6's point: the two boundaries are one number here and the name should say so. Descent regen goes to the resistor instead of the pack and every cold margin below is worse than r1's. And **2,000 m / +45 C** is a new corner, added under R28: it is the one that exercises WS4's ruled `derate_factor` (=0.9312 here), which r1 listed as inherited and never called.

**What the R28 corner derates, measured** (r2 finding M3). THE R28 CORNER DERATES THE ENGINE'S FULL-LOAD CURVE AND WHAT IS COMPUTED FROM IT, AND NOTHING ELSE. WS4's `derate_factor` is applied to every engine in the trial (S0's included) and therefore to the R18 continuous rating and the genset ceilings behind it. It is NOT applied to the traction machine, the inverter, the pack's charge or discharge ceiling, the brake resistor, or the compression brake - `ws8_electric.py` has no hot-side model at all and `Pack8.cold_chg_factor_at()` clamps to 1.0 above 15 C. The corner's BENEFIT - about 27% off the aerodynamic bill at 2,000 m - is shared by every candidate; its PENALTY falls only on combustion. Any conclusion drawn from this corner is scoped to that: it says the thin air outweighs an ENGINE derate, not that it outweighs a hot day for the whole vehicle. The cab-cooling load IS charged symmetrically (mechanical and bus-side both rise), which is the one hot-side effect the electric path does pay.

| moves at this corner | does not move |
|---|---|
| `S0.engine_full_load_torque_at_1300rpm_Nm`, `S1.engine_full_load_torque_at_1300rpm_Nm`, `S1.genset_bus_ceiling_kW`, `S2.engine_full_load_torque_at_1300rpm_Nm`, `S2.genset_bus_ceiling_kW`, `S3.engine_full_load_torque_at_1300rpm_Nm`, `S4.engine_full_load_torque_at_1300rpm_Nm`, `S4.genset_bus_ceiling_kW` | **no electric-side quantity moves at all** |

*Direction of error.* a missing hot-side electric derate FLATTERS the electrified candidates at this corner relative to S0; the corner is not binding for any of them, so no verdict depends on it, but WS9 inherits the statement under R28.

The DIRECTION of each of those two corrections is not separately measured - neither has a one-factor row, because reverting either changes what the corner IS rather than how a run is priced. r2's changelog asserted 'Both corrections cut AGAINST the candidates' anyway, and the R28 half of that is contradicted by the table below, in which S1, S2 and S4 all GAIN at that corner relative to nominal. The claim is withdrawn rather than restated (r2 finding M1).

| candidate | nominal | payload +20% | payload -20% | grade-heavy corridor | -10 C | 2,000 m / +45 C |
|---|---|---|---|---|---|---|
| **S1** | -0.69% / +0.73% | +0.15% / +1.73% | -2.21% / -0.92% | +7.52% / +9.96% | -12.87% / -12.42% | +1.71% / +3.12% |
| **S2** | +0.59% / +1.89% | +1.48% / +2.97% | -0.81% / +0.29% | +7.92% / +9.25% | -9.23% / -8.70% | +2.64% / +3.45% |
| **S3** | -1.09% / +1.64% | -0.93% / +2.24% | -2.27% / +0.49% | +5.63% / +9.68% | -14.17% / -12.39% | -0.56% / +2.16% |
| **S4** | -3.84% / -1.06% | -2.07% / +0.68% | -6.17% / -3.38% | +5.55% / +9.98% | -17.21% / -16.43% | -0.30% / +2.33% |

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

**The ratio ceiling is a physics bound, not a property of the table above** (r1 finding F12: r1 stated the swept-set figure flatly, and it is 3.60 only because the next ratio in the enumerated list lands five hundredths of an rpm over the ceiling). Solved in closed form from `ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)` at 2100 rpm, 0.50 m and 105 km/h, the ceiling is **3.7699**. The highest ratio the enumerated sweep contains under it is **3.60**, and that is an illustration. Ratios in the sweep that hold the 6% grade: **none**.

**And the gap is closed in closed form too.** The lowest ratio at which axle A holds the 6% grade anywhere above its own lugging floor is **6.88**, which puts the engine at **3,832 rpm** at 105 km/h - 1,732 rpm over the 2100 rpm ceiling. The ratio the grade demands and the ratio the cruise permits differ by a factor of about 1.8.

**What is closed form here, and what is not** (r2 minor m1). The CEILING is closed form: it is an rpm limit at a road speed and it is solved as one. The ratio the grade DEMANDS is not - it is the first hit on a 0.01 ratio grid whose hold test scans road speed on a 0.1 m/s grid - and r2's report said 'No swept grid is doing any work in that conclusion', which was the wrong claim to make about a swept result. So the sweep is priced instead of dismissed: at ten times the resolution in BOTH dimensions (0.001 and 0.01 m/s) the ratio moves by 0.009 and the engine speed at 105 km/h by 5 rpm, against a gap of 1,732 rpm over the ceiling. The conclusion is unchanged: `conclusion_unchanged: true`. The grid decides a decimal place; it does not decide the answer.

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

Worst case **275.18 kWh** (governing case: `S3/cold_minus10C/LH-520`), an explicit max over the enumerated (candidate, corner, cycle) set per R14.

All **30** cases above 1 kWh (r2 minor m2: this table was silently truncated to the top 20, so the cases between the twentieth and the smallest were absent and the table read as though the candidates in that range had almost no unserved energy):

| case | unserved kWh |
|---|---|
| `S3/cold_minus10C/LH-520` | 275.18 |
| `S3/grade_heavy/LH-520` | 241.73 |
| `S3/payload_plus20/LH-520` | 212.87 |
| `S3/nominal/LH-520` | 171.09 |
| `S4/cold_minus10C/LH-520` | 170.80 |
| `S3/hot_alt_2000m_45C/LH-520` | 168.89 |
| `S3/payload_minus20/LH-520` | 144.85 |
| `S3/cold_minus10C/REG-165` | 105.38 |
| `S3/grade_heavy/REG-165` | 100.05 |
| `S4/grade_heavy/LH-520` | 93.26 |
| `S4/payload_plus20/LH-520` | 89.63 |
| `S3/payload_plus20/REG-165` | 73.39 |
| `S4/nominal/LH-520` | 67.61 |
| `S3/hot_alt_2000m_45C/REG-165` | 63.54 |
| `S3/nominal/REG-165` | 62.67 |
| `S4/hot_alt_2000m_45C/LH-520` | 51.68 |
| `S4/payload_minus20/LH-520` | 48.09 |
| `S2/cold_minus10C/LH-520` | 21.56 |
| `S1/cold_minus10C/LH-520` | 21.45 |
| `S3/payload_minus20/REG-165` | 20.87 |
| `S2/payload_plus20/LH-520` | 17.70 |
| `S1/payload_plus20/LH-520` | 16.61 |
| `S1/grade_heavy/LH-520` | 15.83 |
| `S2/nominal/LH-520` | 15.59 |
| `S1/hot_alt_2000m_45C/LH-520` | 13.55 |
| `S1/nominal/LH-520` | 13.32 |
| `S2/grade_heavy/LH-520` | 12.60 |
| `S2/hot_alt_2000m_45C/LH-520` | 12.12 |
| `S2/payload_minus20/LH-520` | 12.00 |
| `S1/payload_minus20/LH-520` | 9.99 |

### 7.1 The same question on the braking side

THE BRAKING-SIDE MIRROR OF `unserved_energy_kWh`, and read it the same way: it is a CAPABILITY statement, not a heat one. The traction and retard envelope is a function of road speed alone and does not re-solve when the buffer pack fills, so on a long descent the integrator keeps commanding the regen channel at its warm charge ceiling after the pack has stopped accepting. `series_dispatch` and S3's SOC loop then send that power to the brake resistor - which is where it physically goes - and the sum can exceed the resistor rating whose mass was charged. What the resistor TOOK is booked in `brake_resistor_kW`, capped at that rating; the remainder is this field. It is NOT a cooling load and WS6 must not size on it. What it measures is that the simulated descent lets the candidate retard harder than its hardware can, so its simulated descent speed is optimistic by that much. The physically correct member for the pack-full state is the enumerated `descent_6pct_pack_saturated` analytic case, which respects the rating and holds a LOWER speed. Escalated as ESC-WS8-10, not self-resolved.

Worst case **254.3 kW** sustained (governing case: `S4/grade_heavy/LH-520/seed8101`, 0.13 kWh on that run), an explicit max over the enumerated (candidate, corner, cycle, seed) set per R14. No margin reads this field; it is reported raw, on the convention WS4's ESC-5 established.

| candidate | runs with any overcommitment | worst kW | resistor rating kW |
|---|---|---|---|
| **S1** | 39 | 190.9 | 340 |
| **S2** | 42 | 191.5 | 340 |
| **S3** | 36 | 200.3 | 200 |
| **S4** | 3 | 254.3 | 340 |

The 15 largest of **120** affected runs (labelled truncation, r2 minor m2 - the full set is `interface_ws8.retard_overcommitment.cases_kW`, and the smallest shown here is 199.0 kW against 14.0 kW at the bottom of the list):

| case | overcommitted kW |
|---|---|
| `S4/grade_heavy/LH-520/seed8101` | 254.3 |
| `S4/payload_plus20/LH-520/seed8101` | 252.7 |
| `S3/nominal/LH-520/seed8106` | 200.3 |
| `S3/grade_heavy/LH-520/seed8106` | 200.3 |
| `S3/payload_plus20/LH-520/seed8106` | 200.3 |
| `S3/payload_minus20/LH-520/seed8106` | 200.3 |
| `S3/nominal/LH-520/seed8101` | 200.3 |
| `S3/payload_plus20/LH-520/seed8101` | 200.2 |
| `S3/grade_heavy/LH-520/seed8103` | 199.6 |
| `S3/grade_heavy/LH-520/seed8101` | 199.5 |
| `S3/payload_minus20/LH-520/seed8104` | 199.4 |
| `S3/nominal/LH-520/seed8104` | 199.3 |
| `S3/grade_heavy/LH-520/seed8104` | 199.1 |
| `S3/payload_minus20/LH-520/seed8101` | 199.1 |
| `S3/payload_plus20/LH-520/seed8105` | 199.0 |

---

## 8. External corroboration

None of the verdicts above depend on the prior-art scan. But the scan was run, and it is worth recording where it agrees - because three of this report's least comfortable conclusions turn out to be things the industry already knows. All figures in this section are EXTERNAL and search-summary level, provisional per E13 precedent; see `PRIOR_ART_WS8.md` for their evidence limits.

**On the size of the hybrid prize.** Volvo built and ran a long-haul hybrid concept tractor and reported the hybrid path alone at **5-10% fuel saving**, from shutting the engine off for up to 30% of driving time, with topography-optimal control. The widely-quoted 30% for that vehicle is the whole truck including aerodynamics. S1, S2, S3, S4 land inside that 5-10% band on the paired per-seed per-km margin. For the candidates that do, that is the reassuring outcome, not the disappointing one: a model that had produced 25% would have been wrong. (r2 finding M2: this sentence used to assert the whole set was inside the band, on a statistic the report did not use.)

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
| **S1** | -0.69% | cold_minus10C | -12.87% | False | False | **KILL** |
| **S2** | +0.59% | cold_minus10C | -9.23% | False | False | **KILL** |
| **S3** | -1.09% | cold_minus10C | -14.17% | False | False | **KILL** |
| **S4** | -3.84% | cold_minus10C | -17.21% | False | False | **KILL** |

- **S1: KILL** - fails the nominal >=3% criterion.
- **S2: KILL** - fails the nominal >=3% criterion.
- **S3: KILL** - fails the nominal >=3% criterion.
- **S4: KILL** - fails the nominal >=3% criterion.

**What WS8 recommends.** The numbers are above and the execute-or-spare decision is the lead's. What WS8 will say is this:

1. **No candidate clears the bar as specified.** The margins are not catastrophic - several candidates are within a point or two of S0 - but 'within a point or two' is not >= 3%, and the criteria were armed before the numbers were seen.
2. **S3 should be spared further work regardless of its fuel number.** Its fuel result is not the finding; its capability result is. A fixed-ratio diesel axle cannot hold the specified mountain grade at any ratio that also permits highway cruise, and an e-axle fault leaves the combination immobile from rest. Those are structural, not parametric.
3. **The binding constraint on this vehicle is mass, not efficiency.** S1, S2, S3, S4 win per kilometre on every seed and give it back on payload. Any future work that does not attack the powertrain mass ledger is not attacking the problem.
4. **What decides these architectures is the fleet's duty, not the architecture.** The corner sweep in section 6.1 spans **26 percentage points** for S4 alone - from +9.98% at `grade_heavy` to -16.43% at `cold_minus10C` - and the sign flips inside that span for every candidate. An operator running loaded over mountains and an operator running light in winter are not looking at the same vehicle. R29 has since named the duty (grade-heavy regional) for exactly this reason; these numbers are the evidence it was named on, and r2 widened the span rather than narrowing it, because the cold corner the sweep now models honestly is far harsher than the one r1 reported.
5. **The cold corner is the one to attack first.** It is binding for all four candidates, and its cause is specific and fixable rather than fundamental. In r1 this recommendation described a mechanism the model did not contain (finding F2, blocking): `Pack8.p_cont_chg_kw_at()` and `COLD_CHG_FACTOR` were defined and never called, so every corner ran on the warm nameplate. **In r2 the mechanism is in the model.** S1's buffer accepts **30.5 kW** at -10 C against **240.0 kW** warm - a factor of 7.9 - so descent regen goes to the resistor instead of the pack, and every cold-corner margin in section 6.1 is computed with that collapse applied rather than asserted beside it. The conventional truck still heats its cab from engine coolant for free. Pack preconditioning and a heat-recovery path for cab heat are the obvious counters; neither is modelled here, and R30 now requires both of every WS9 electrified candidate.
6. **The escalations in section 11 change the answer if ruled the other way**, ESC-WS8-1 and ESC-WS8-3 especially. They are not footnotes.

---

## 10. First-principles sanity checks

**Road load at 95 km/h, flat, 36,300 kg.** By hand: aero 0.5 x 1.196 x 5.5 x 26.39^2 = **2,290 N**; rolling 0.0055 x 36,300 x 9.81 = **1,959 N**; total 4,249 N = 112.1 kW at the wheel. Model agrees: **True**.

2,290 N of aero and 1,959 N of rolling at 36.3 t and 95 km/h is the whole line-haul problem in two numbers: above ~80 km/h the air is the bigger bill, which is why every candidate here wins or loses on driveline efficiency and mass, not on regenerative braking.

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
THE SUBSTITUTION MOVES S4 BOTH WAYS, and r2 stated only the half that hurts it (finding M4). The same power-optimised cell that costs S4 mass also hands it 600.4 kW continuous CHARGE and 1200.7 kW continuous DISCHARGE on a 150 kWh pack - 4.0 C and 8.0 C - and that ceiling is what makes S4's descent regen effectively unconstrained by its battery. Measured at the contact patch on both sides (the ceiling is a bus-side kW applied as a wheel-side force cap, r2 minor m6, and the comparison is stated in force so that slippage cannot hide in it): at 95 km/h the machine can pull 24,772 N of retarding force and the pack ceiling allows 22,750 N of it - the ceiling costs 8.2% of the machine's capability, and it binds at all only above 52.0 km/h. On the enumerated 6% descent with the pack accepting, S4 puts the WHOLE mountain into the battery: brake resistor 0.0 kW and foundation brakes 0.0 kW, against 433 kW of retarding demand at 90 km/h.
WS8's OWN COLD CORNER MEASURES THE TRANSFER an energy cell's lower ceiling would cause. At -10 C the same pack's charge acceptance is cut by `COLD_CHG_FACTOR`, and S4's LH-520 median regen falls from 145.8 to 48.0 kWh while its resistor energy rises from 0.0911 to 80.7 kWh. An energy cell at 1.0 C continuous charge - the rate WS9's cited external cell carries - would give this pack about 150 kW, well below what the descent demands, and would bind S4 hard where WS3's cell does not bind it at all. The mass half of this escalation is FOR substituting; the power half is AGAINST, and the resistor S4 would then have to grow is part of the price.

**Why this is not self-resolved.** Substituting a cell WS3 never characterised would be WS8 writing WS3's trade study, which rule 10 forbids and which would put an uncorroborated number into the headline. That applies to the power half as much as to the mass half: the 1.0 C / 2.0 C figures above are CITED from WS9's ruled external cell, not WS8's own characterisation of an energy cell.

**Asks.** Rule on ONE of: (a) S4's result stands on WS3's cell set as reported; (b) WS3 is reopened to characterise an energy-optimised cell and S4 is re-run; (c) WS8 is authorised to carry a cited external energy cell as an explicitly non-WS3 bracket.
R27/ESC-1 HAS ALREADY RULED (c), and the ruling is executed: S4' (S4p) - RE-BEV re-posed on a CITED EXTERNAL energy cell ran in WS9_vehicle_one_wave2 (Vehicle One wave two), as reported on ESC-1(c): a cited external energy-optimised Class 8 traction pack, explicitly NOT a WS3 cell at 160 Wh/kg (938 kg, -521 kg of payload against its ruler) and returned +11.95% on the design duty and -6.81% on the control duty - ADVANCE (PROVISIONAL). This escalation is therefore CLOSED for Vehicle One's WS9 work and is carried here only because WS8's own numbers were computed before that ruling.
THREE CAVEATS ON THAT CITATION. Status: PROVISIONAL - BASELINE_v5 R37: WS9's verdicts are NOT ratified (no findings file exists and its adjudication is the lead-designated Fable seat), and R39/ESC-2 keeps S4' at PROVISIONAL-ADVANCE with its grid-factor flip point on the record. Commensurability: WS9's metric is PRIMARY ENERGY per payload tonne-km with an electricity term (ESC-3), not WS8's fuel-energy metric. S4' +11.95% and WS8's S4 are NOT the same quantity and must not be differenced. Vintage: WS9's numbers were produced against WS8 r2 sources; BASELINE_v5 R39/ESC-8 orders WS9 re-run against WS8 r3 when it lands.

**Materiality:** high, and TWO-DIRECTIONAL - it is the difference between S4 advancing or not on mass, and the difference between a descent the pack absorbs and one it does not on power. r2 recorded only the first direction (finding M4), and WS9's S4' was sized under R27/ESC-1(c) on that half of the record.

### ESC-WS8-10 - The retard envelope does not re-solve when the buffer pack fills, so every simulated descent lets a candidate brake harder than its resistor can absorb

**Cites:** R3_DIRECTIVE item 1 (extend `heat_closure_check` to `simulated_worst_run`) - the extended closure is what found this; FINDINGS_WS8_r1.md F1(a), which added the `descent_6pct_pack_saturated` analytic case for exactly this state; CLAUDE.md rule 7

**Finding.** `Candidate.envelope` and `_retard_channels` are functions of ROAD SPEED ALONE. The regen channel is capped at the pack's charge ceiling at the corner's ambient - a constant - so the integrator goes on commanding regen at that ceiling after the pack has actually filled. On the 6% mountain descent the pack reaches its 0.95 SOC ceiling part-way down and then takes nothing, and `series_dispatch` (and S3's SOC loop) send the whole harvest to the brake resistor, which is where it physically goes. The sum exceeds the resistor rating whose mass was charged.
r3 books what the resistor TOOK in `brake_resistor_kW`, capped at that rating, and exports the remainder as `retard_overcommitment`: worst case 254.3 kW sustained at `S4/grade_heavy/LH-520/seed8101`, 0.13 kWh on that run. Booking the whole flow as resistor heat instead would have exported a 450+ kW cooling load for a 340 kW resistor and told WS6 to size a package for a duty the hardware cannot produce; that alternative was considered and rejected, and the choice is stated here rather than buried.
WHAT IT MEANS FOR THE TRIAL: every candidate with a buffer pack holds its simulated descent at a speed its retarder cannot actually support once the pack is full, so the simulated descent speeds - and therefore trip times, and the accessory energy that rides on them - are optimistic. The enumerated `descent_6pct_pack_saturated` case is the physically correct member for that state and it is in the ledger: it holds a LOWER speed precisely because it respects the rating. The two members disagreeing IS the finding.

**Why this is not self-resolved.** Making the envelope re-solve at pack-full changes the achieved speed, the trip time and the cycle every candidate drives, and therefore every margin in the trial. R3_DIRECTIVE's scope is declared exhaustive and orders the closure extended, not the integrator re-specified; and R38's trip-time gate for Vehicle One depends on exactly these speeds. That is a lead decision.

**Asks.** Rule on ONE of: (a) the record stands as it is - the overcommitment is exported, WS6 sizes on the capped resistor row and on the analytic pack-saturated case, and the optimism in the simulated descent speeds is a stated limitation; (b) WS8 is directed to make the retard envelope a function of pack state as well as road speed and re-run every corner, accepting that every margin and every trip time moves; (c) the finding is carried to WS9 and WS10 as a design note, since R38 gates ADVANCE on trip time and every buffer-pack candidate there inherits the same optimism.

**Materiality:** medium for this round - no verdict depends on it, and the four kills are unchanged - but high for WS9 and WS10, where R38 makes trip time a gate and the trip times all four wave-two candidates were judged on come from the same envelope

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
r2 SUPPLIES THE NUMBER. The rebuilt heat ledger carries a foundation-brake row for the first time, and S0's worst sustained 60-second foundation-brake dissipation over the whole trial is 313 kW, against the 60 kW continuous grade-holding allowance the descent governor is built on. That is repeated snub braking on long descents - what a compression-brake-only tractor actually does - and it is reported in the ledger as an ADVISORY exceedance rather than a ledger error, because the allowance is a policy number and not a brake rating. It is the physical evidence for this escalation, and it is a thermal duty WS6 should see.

**Why this is not self-resolved.** Whether the ruler carries a retarder is a baseline-specification decision.

**Asks.** Confirm S0's retarder specification, or direct a re-run with a hydraulic retarder on S0. R27/ESC-6 has already ruled that S0 gains a hydraulic retarder in WS9 with its mass charged; this escalation is therefore CLOSED for Vehicle One's WS9 work and is carried here only because WS8's own numbers were computed before that ruling.

**Materiality:** low - affects trip time and accessory energy, not tractive work

### ESC-WS8-7 - S0's fuel exceeds the assignment's 30-38 L/100 km sanity corridor, and the model is not the reason

**Cites:** Assignment Task 2: 'Calibrate fleet fuel to a public reference band and state it (sanity corridor: 30-38 L/100 km loaded line-haul)'; Task 1: 'realistic grade distribution including sustained 2-3% and one 6% mountain segment with full descent'

**Finding.** S0's fleet-mission fuel is 38.78 L/100 km (ensemble 36.28 to 41.23), above the stated corridor. The calibration is nonetheless sound, and the cross-check says so directly: run over the SAME corridor with the grade zeroed - same distance, same speeds, same wind, same driver, same vehicle, nothing else touched - S0 burns 33.08 L/100 km MEDIAN, on an 8-seed envelope of 29.82 to 39.36 L/100 km, against the ICCT / TUV NORD figures of 29.9-33.1 L/100 km (typical 32.6) for an EU tractor-trailer over the regulatory Long Haul cycle.
WHAT THAT SUPPORTS, restated in r2 (finding F7). r1 read this off the median and called it 'a match to about one percent'. It is not: the ensemble envelope is WIDER than the public band it is being compared against, and the comparison is not mass-matched - WS8's S0 carries 20.8 t of payload at the assignment's fixed GCW against the reference cycle's 19.3 t, and the three enumerated mass cases in section 3.4 show what that is worth. The claim the evidence supports is that the model is CONSISTENT WITH the public band on flat ground, reached with no fitting: the single calibration knob is solved against a declared BSFC island and nothing else is tuned.
The excess is TERRAIN. Task 1 ordered a corridor carrying a 6% mountain and sustained 2-3% sections - 3,704 m of climb over 520 km (8-seed ensemble 3,507 m to 3,838 m) - and a 30-38 L/100 km band describes a freeway-dominated regulatory cycle, not that road. The two orders are in tension, and WS8 has obeyed the one that governs the physics (Task 1's corridor) rather than adjusting the vehicle until Task 2's band was satisfied.

**Why this is not self-resolved.** Reconciling them would mean either flattening a corridor the assignment specified or tuning a vehicle parameter until a band was met - and tuning to a band is exactly what 'no fudge factor' forbids. Either change alters every candidate's result, so it is the lead's to make.

**Asks.** Rule on which governs: (a) the corridor as specified, with S0's fuel reported above the band and the flat cross-check standing as the calibration evidence (WS8's recommendation - it is the honest reading and the comparison between candidates is unaffected, since all five drive the same road); or (b) a flatter reference corridor, which would move every absolute fuel figure and none of the margins. Note that r2 has WEAKENED the evidence this escalation rests on, per F7: the anchor is an envelope consistent with the band, not a one-percent match to a point in it.

**Materiality:** low for the trial, high for the record - it changes no margin, because every candidate drives the same corridor, but it is a stated acceptance criterion not met and must not pass silently

### ESC-WS8-8 - Once B1's rule is applied, S3's through-the-road charging path never runs - and the reason is a modelling artefact, not a control choice

**Cites:** R3_DIRECTIVE item 1 (gate through-the-road charging on the VEHICLE NOT BRAKING); FINDINGS_WS8_r2.md B1; assignment Task 3's S3 specification

**Finding.** S3's declared policy says its buffer pack 'can only be refilled by regen or by through-the-road charging (engine pushes axle A, e-axle harvests on axle B)'. With R3's gate in place that second mechanism is IDENTICALLY INERT: over the whole trial S3 takes 0.000 kWh of through-the-road charge, on 0 of 96 runs.
THE REASON IS NOT THE GATE. The charging headroom is priced as `p_chg_head_bus = f_a_head * v * eta_g`, where `eta_g` is `ScaledEDrive.eta_wheel_to_bus(v, p_regen_wheel)` - the generating efficiency evaluated AT THE REGEN OPERATING POINT. That function returns exactly 0.0 when the captured power is zero (`ws8_electric.py`: `eta = np.where(gen, ..., 0.0)`), and the captured power is zero on every sample where the integrator is not braking. So the headroom was zero on every non-braking sample all along, and in r2 the ONLY samples on which through-the-road charging could fire were braking samples - which is exactly the impossible state finding B1 identified. The B1 gate did not disable a working mechanism; it revealed that the mechanism only ever ran in the state it must not run in.
The 0.72-of-capacity BSFC policy is NOT what holds it back either, and that is measured rather than argued: the energy that threshold withheld over the whole trial is 0.000 kWh.

**Why this is not self-resolved.** Repricing the headroom at the TTR harvest's own operating point would make the mechanism work, and would move S3's fuel and unserved energy by an unmeasured amount. R3_DIRECTIVE's scope is declared exhaustive and orders the GATE, not a re-specification of the charging law; and item 1 carries its own STOP condition on S3's nominal ensemble-min. Changing the law under that condition is the lead's call.

**Asks.** Rule on ONE of: (a) S3's through-the-road path stands as inert and the record says so - S3 is dead on capability either way and this changes no verdict; (b) WS8 is directed to reprice the charging headroom at the harvest's own operating point and re-run S3 on all corners; (c) the finding is carried to WS9/WS10 as a design note against any future through-the-road architecture, since the same efficiency call would silently disable it there too.

**Materiality:** medium for WS8's record, high as a design note - it changes no verdict (S3's kill is on capability), but it means half of S3's stated energy policy was never exercised by the model that judged it, and any future candidate that leans on through-the-road charging inherits the same silent zero.

### ESC-WS8-9 - R34 orders a 10 Hz trace file per run from 'all later work'; R3_DIRECTIVE's scope is declared exhaustive and does not include it

**Cites:** BASELINE_v5 R34 ('Every pipeline exports a 10 Hz trace file per run (feeds the WS10 exhibit/simulator). WS5, WS9 re-runs, and all later work comply from their next artifact.'); R3_DIRECTIVE.md '## Scope (exhaustive)'; CLAUDE.md rule on bounded orders

**Finding.** R34 is a standing program-hygiene ruling and WS8 r3 is a next artifact, so it reads as binding here. R3_DIRECTIVE's scope is declared EXHAUSTIVE in seven numbered items and does not mention traces, and CLAUDE.md says an assignment or directive is a bounded order - do what is ordered, nothing else. The two cannot both be satisfied by a workstream session deciding for itself.
The cost is not incidental. This pipeline runs 944 simulated runs (the corner trial, the WHR gate and the one-factor re-runs, counted); LH-520 is about 520 km at 10 Hz, so a full-fidelity trace set for every run is of the order of gigabytes and is not a committable artifact. A bounded subset - the governing runs the heat ledger and the worst-case exports actually name - would be a few tens of megabytes and would serve the WS10 exhibit for the cases that matter.
Nothing in this round depends on the answer: no number here changes either way.

**Why this is not self-resolved.** Choosing which runs to export, and at what fidelity, is a program-hygiene decision under R34 and it binds WS5, WS9 and WS10 as much as WS8. A workstream session picking its own subset would set that convention by default.

**Asks.** Rule on ONE of: (a) R34 does not reach WS8 r3, whose scope R3_DIRECTIVE declares exhaustive, and traces come with the next WS8 artifact if there is one; (b) WS8 r3 exports traces for a NAMED bounded subset - the ledger's governing runs plus one nominal run per candidate - and the convention is written down for WS5/WS9/WS10; (c) full compliance, with the artifact-size consequence accepted and a storage convention ruled.

**Materiality:** none for this round's numbers; medium for the program, because R34's convention is being set by whoever complies first and no one has yet

---

## 12. Heat ledger for WS6 (rule 7)

**Rebuilt in r2, and closed in r3.** Round 1's blocking finding F1 was three defects in one export: the governing case sat OUTSIDE the enumerated case set (the ledger priced the 6% descent with the pack accepting its full charge power throughout, when the pack fills in about four minutes of a ten-minute descent); compression-brake heat was booked as resistor heat with the exhaust row explicitly zeroed, so S1, S2 and S3 exported the identical figure despite three different retarder architectures; and foundation-brake heat had no row at all, so the S0 descent case did not close. All three are closed here.

**This ledger is `ledger_version: r3`, and it supersedes `r2`.** R3_DIRECTIVE item 7: WS6 consumes ONLY the r3 ledger. The r2 ledger is superseded, not amended: its `simulated_worst_run` member was exempt from the closure assertion and its largest row - S3's 396.87 kW exhaust - was a state one crankshaft cannot be in (finding B1). A consumer holding a ledger whose `ledger_version` is not 'r3' is holding numbers this workstream has withdrawn.

component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation; compression-brake heat is booked to the EXHAUST and resistor heat to the RESISTOR, because they go to different places in a packaging study; the simulated member is a sustained 60-second mean, not an instantaneous spike, and it is a MEASURED PEAK rather than a balanced operating point. EVERY member now carries a closure residual and every member is asserted (r3, R3_DIRECTIVE item 1): the four analytic cases are scaled on the case's own wheel power, and the simulated member carries the WORST 60-second residual of any run of that candidate in the trial, scaled on the accounted energy input at that window. In r2 the simulated member was exempt, and that exemption is what finding B1 came through. The `brake_resistor_kW` row is what the resistor TOOK, capped at the rating whose mass was charged; retarding power the run commanded that no sink could absorb is a CAPABILITY shortfall and is exported separately as `retard_overcommitment`, never as a cooling load.

Enumerated case set (R14): `cruise_95kmh_flat`, `climb_6pct`, `descent_6pct_pack_accepting`, `descent_6pct_pack_saturated`, `simulated_worst_run`.

Worst-case rejection by component [kW], an explicit max over that set with the governing case labelled:

| candidate | engine coolant | engine exhaust | traction machine inverter | generator rectifier | pack | brake resistor | friction brake | total rejected |
|---|---|---|---|---|---|---|---|---|
| **S0** | 208 (simulated_worst_run) | 304 (descent_6pct_pack_accepting) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 313 (simulated_worst_run) | 569 (simulated_worst_run) |
| **S1** | 159 (climb_6pct) | 219 (simulated_worst_run) | 32 (simulated_worst_run) | 16 (climb_6pct) | 8 (simulated_worst_run) | 340 (simulated_worst_run) | 205 (simulated_worst_run) | 575 (simulated_worst_run) |
| **S2** | 196 (simulated_worst_run) | 271 (simulated_worst_run) | 32 (simulated_worst_run) | 16 (climb_6pct) | 10 (simulated_worst_run) | 317 (simulated_worst_run) | 66 (simulated_worst_run) | 553 (simulated_worst_run) |
| **S3** | 163 (simulated_worst_run) | 225 (simulated_worst_run) | 24 (simulated_worst_run) | 0 (cruise_95kmh_flat) | 7 (descent_6pct_pack_accepting) | 200 (simulated_worst_run) | 148 (simulated_worst_run) | 564 (simulated_worst_run) |
| **S4** | 116 (simulated_worst_run) | 160 (simulated_worst_run) | 37 (simulated_worst_run) | 9 (simulated_worst_run) | 18 (simulated_worst_run) | 315 (simulated_worst_run) | 134 (simulated_worst_run) | 461 (simulated_worst_run) |

**The resistor and the compression brake are now separate rows, because they reject to different places.** An air-cooled grid resistor is a packaging and airflow problem; an exhaust-side compression brake is not. On the pack-saturated 6% descent:

| candidate | resistor kW | compression brake kW | foundation brakes kW | resistor rating kW |
|---|---|---|---|---|
| **S0** | 0 | 304 | 14 | - |
| **S1** | 313 | 0 | 60 | 340 |
| **S2** | 255 | 190 | 0 | 340 |
| **S3** | 182 | 204 | 60 | 200 |
| **S4** | 313 | 0 | 60 | 340 |

**`all_cases_close_and_within_rating = True`, and here is exactly what that tests** (r2 minor m5: r2's bolded sentence read 'Every case closes and every component stays inside the rating', which is stronger than what the flag examined - the simulated member carried no residual and was skipped, and that exemption is what finding B1 came through):

TRUE requires all three of: (a) every enumerated case closes, INCLUDING the simulated member, which carries the worst 60-second residual of any run of that candidate in the trial - in r2 the simulated member was exempt and that exemption is what finding B1 came through; (b) every component stays inside the rating of the hardware whose mass was charged, which is one HARD row - the brake resistor - the advisory rows being findings rather than gates; (c) no run carries a sample with both compression-brake power and positive engine shaft power.

**The crankshaft assertion (finding B1), per run.** per run, over every (corner, cycle, seed) in the trial: no 10 Hz sample may carry both compression-brake power > 1 kW and positive engine shaft power > 1 kW. One crankshaft cannot be in both states. `all_hold = True`.

| candidate | runs examined | samples with brake AND shaft power | fuel while the vehicle brakes (max over runs) |
|---|---|---|---|
| **S0** | 96 | 0 | 0.00% |
| **S1** | 96 | 0 | 8.79% |
| **S2** | 96 | 0 | 2.40% |
| **S3** | 96 | 0 | 0.00% |
| **S4** | 96 | 0 | 15.12% |

`fuel_fraction_while_braking` is reported, not gated, and a non-zero value is not by itself a defect. S1 and S4 have no mechanical path from engine to road at all, so a genset charging the pack while the vehicle brakes is simply a legitimate state for them. S2's is legitimate too, on a narrower ground: under its declared coupling law the lockup clutch is open while regen alone is doing the retarding, so the crank is free and the genset may run - and the fraction of the band that covers is exported as `inband_overrun_no_engine_brake_fraction_moving`. What is impossible, and what `samples_brake_and_shaft` counts, is an engine carrying compression-brake power and positive shaft power at the same instant.

**The simulated member is no longer exempt from the closure** (R3_DIRECTIVE item 1). Every candidate's `simulated_worst_run` carries the WORST 60-second energy residual any run of that candidate produced, against a tolerance of 2% of the accounted input at that window:

| candidate | worst residual kW | relative | closes | governing run |
|---|---|---|---|---|
| **S0** | -0.000 | -0.0008% | True | `payload_plus20/LH-520/seed8108 @ 90 km/h` |
| **S1** | +0.000 | 0.0000% | True | `grade_heavy/LH-520/seed8105 @ 104 km/h` |
| **S2** | -0.000 | -0.0000% | True | `payload_minus20/LH-520/seed8103 @ 86 km/h` |
| **S3** | -0.001 | -0.0009% | True | `cold_minus10C/LH-520/seed8108 @ 90 km/h` |
| **S4** | -0.000 | -0.0000% | True | `grade_heavy/REG-165/seed8106 @ 93 km/h` |

In r1 S3 exported 210.71 kW of resistor heat against the 200 kW resistor it had been charged 71.8 kg for (`FINDINGS_WS8_r1.md`, F1b); that check now exists and runs, and the brake resistor is still the ONLY hard row.

**r2 minor m5(b) said that row could not fail by construction, and r3 found the path that reaches it.** m5(b)'s argument was that `_retard_channels` caps resistor force at the rating divided by road speed AT THE WHEEL, so the bus-side figure is at most the wheel-side rating times the generating efficiency - and it added that the check would bind the moment a case appeared that did not go through that cap. Such a case exists: regen the FULL pack cannot accept is sent to the resistor by `series_dispatch` and by S3's SOC loop, outside the retard-channel split entirely. Booked where the code says it goes, S1, S3 now sit AT their ratings (S1 340 of 340 kW, S3 200 of 200 kW). The row is capped at the rating in `resistor_and_overcommitment`, because a figure above it would not be a cooling load; what would have exceeded it is exported as `retard_overcommitment` in section 7.1 and escalated as ESC-WS8-10. The honest statement is therefore not that the check passes - it is that the resistors SATURATE, and that the surplus is a capability shortfall rather than heat.

**5 ADVISORY exceedances, and they are a finding rather than an error.** An ADVISORY exceedance is a declared policy allowance exceeded, not a component rating: it is a finding about the architecture that WS6 needs, not an error in this ledger. S0's foundation brakes are the case that matters - a compression-brake-only tractor snubs repeatedly on a long descent, and the sustained figure is the physical evidence behind ESC-WS8-6.

| candidate | component | declared allowance kW | worst sustained kW | governing case |
|---|---|---|---|---|
| **S0** | foundation_brakes | 60 | 313 | simulated_worst_run |
| **S1** | foundation_brakes | 60 | 205 | simulated_worst_run |
| **S2** | foundation_brakes | 60 | 66 | simulated_worst_run |
| **S3** | foundation_brakes | 60 | 148 | simulated_worst_run |
| **S4** | foundation_brakes | 60 | 134 | simulated_worst_run |

**And every candidate exceeds it, not only S0.** That is the same mechanism F1(a) named, seen from the other end: the descent governor sets the speed a candidate may descend at from the retarding capability of a pack that has not yet filled, so once the buffer saturates part-way down the grade the retarding channel it was counting on is gone and the foundation brakes make up the difference until the truck slows. A pack-saturated governor would have every electrified candidate descending slower. That is a WS9 requirement rather than a WS8 correction - it changes trip time and therefore the metric - and r3 ESCALATES it as **ESC-WS8-10** rather than changing it under an order whose scope is declared exhaustive. Section 7.1 puts a number on it: the retarding power the runs commanded that no sink could absorb.

The descent case is the one that matters to WS6: a series candidate holding the 6% grade puts several hundred kilowatts into a resistor bank that has to reject it to air, and that is a packaging and airflow problem, not an electrical one. The number to size on is the PACK-SATURATED one, not the pack-accepting one, because a buffer with a few tens of kWh of headroom does not survive a mountain descent.

---

## 13. Machine-readable interface (R14)

Every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline. This block is byte-identical to `results_ws8.json['interface_ws8']`; `verify_ws8.py` asserts it.

```json
{
 "_convention": "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); stochastic extrema are 8-seed ensemble envelopes (rule 4); every worst-case field is an explicit max/min over an enumerated case set with the governing case labelled (R14)",
 "numbers_version": "r3",
 "numbers_status": "r3 - the round ordered by WS8_semi_architecture/R3_DIRECTIVE.md under R35, closing FINDINGS_WS8_r2.md (B1 blocking, M1-M4, m1-m7). Every number in this block is regenerated; r2's numbers are superseded, not amended in place, and r2's heat ledger is WITHDRAWN - see `heat_ledger_WS6.ledger_version`.",
 "supersedes": {
  "numbers_version": "r2",
  "ledger_version": "r2",
  "why": "r2's control law let an engine fuel while the same crankshaft was compression-braking (B1), so r2's S2 and S3 fuel numbers and its largest ledger row are withdrawn. S0, S1 and S4 are re-run unchanged in control law; their small movements are the r3 accounting corrections the extended run closure found, and they are measured in `one_factor_S1_vs_S2`."
 },
 "verdicts": {
  "status": "executed_kill_2026-08-30",
  "ruling": "R25 (BASELINE_v4): WS8 verdicts EXECUTED on the pre-committed criteria",
  "reopened_by_this_round": false,
  "note": "the kills and the WHR drop are EXECUTED and are not reopened by r2; this round makes the NUMBERS of record correct. Every r2 correction was checked against the pre-committed criteria and none flips a verdict - see `verdict_stability`.",
  "result": {
   "S1": "KILL",
   "S2": "KILL",
   "S3": "KILL",
   "S4": "KILL"
  },
  "whr": "DROPPED"
 },
 "inputs_sha256": {
  "run_ws8.py": "3b667eb825164299bb19c43dd0461e4424c079763476d29666de2d3be2174f5d",
  "ws8_params.py": "d729fc7cb7323dbfbe725e839519fcf4987e9fec693dadaa8f8b894304cc6353",
  "ws8_physics.py": "79f93610de6fd1e5d42dfcb50dbc4a3d12ce0b3e2486c84bde14046a95309b9b",
  "ws8_cycles.py": "bd5b444294b5034b35f653f317aa1a710dfcb2c7c21a9085d1820c30ce05e6ff",
  "ws8_engine.py": "61cc29d04c6a56a3076ee34d866a566c0beaa80b14a21881c5ff4ad9f3dd85de",
  "ws8_electric.py": "74a932dbc795698986d32105652cc62dbeb6629bad4c3f6b61364aac538f9f6d",
  "ws8_candidates.py": "66ec2ec831c735bc2e001a4fdb309b48d5c984eef09d0ae1830ae048fc1910fa",
  "ws8_whr.py": "674f91016f31cd29cac55cfdd71a6470d079b5699532809def2682dea49fdf5f",
  "requirements.txt": "23bf63c77db7c14b9e04f686f9cb9c319c5067d5e6935299b6dcb1ca521f4a7d",
  "ASSIGNMENT.md": "88be8fcce3509764a6e13842ccff09f11eaf397adb26c3452c9aaadf3d8a2b09",
  "R2_DIRECTIVE.md": "e3040204e8f70f0fa431ad4cfdb2af3514a22b4df7dee49a296aece00f25da3d",
  "R3_DIRECTIVE.md": "a55b093776ab6a053bc677524c13dd80a64659026f23e698ee1e5a829ead9a5b",
  "FINDINGS_WS8_r1.md": "b3db6878367b39f13ce2d430181ffcccd6e8c078308caf5d534b40c8656c3ce8",
  "FINDINGS_WS8_r2.md": "08924729469d8d719bc94348c7636dce15d3031d7950aa8f36381c96e52dfd56",
  "PRIOR_ART_WS8.md": "469c28c502108e5d56b450ff52991deb25485a18ae9370ddbeed1cf507cf64c3",
  "../BASELINE_v4.md": "6c51f25ab2d4b9fd776a2aa8df8779b94ba40e1558da0fe5e9c52478a5c78fd7",
  "../BASELINE_v5.md": "41331e1ab86cc2fbc7d441e1007370aed62db03f9c41697cf388164626ce03d6",
  "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv": "e0f617eafbcead33a8bb5edc07b95174826bd300be3b43b78b1593aa93c8ba4c",
  "../WS2_traction_motor/data/capability_vs_rpm.csv": "1496c7123355877ed3fa20bc51a6596312c2ee0e56d048f3af2d974b54cbc746",
  "../WS3_battery/ws3_cells.py": "4253ec9d29df101ac2107df469e1b62b710564bef429ddfda7e501a39b0c7f6e",
  "../WS3_battery/ws3_pack.py": "78ca3dfcb8e7f0a9c3733364e724e76fcce947df7920fd66c508937fcf8d79f2",
  "../WS4_genset/ws4_models.py": "33d9b498ec5bb59da92330ad25da7ce3d8899c2e80b1e937b92394e0dc5f9716",
  "../WS4_genset/ws4_chain.py": "609fd499b1198af209f5e2a8f90d977716441c1f88612e97b1e61461d71c44d6"
 },
 "inputs_sha256_scope": "every file the numbers depend on: WS8's model and driver sources, the orders this round executes, and the read-only objects inherited from WS2, WS3 and WS4. The report generator and the verifier are excluded because they consume these numbers rather than produce them.",
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
   "title": "Conventional 13 L diesel + 12-speed AMT, direct top gear",
   "payload_kg": 20785.0,
   "powertrain_mass_kg": 2845.0,
   "fuel_correction_share": {
    "rule": "max AND min over the enumerated (cycle, seed) case set; the quantity is SIGNED - negative is a CREDIT",
    "value": 0.0,
    "max": 0.0,
    "min": 0.0,
    "median": 0.0,
    "governing_case_max": "LH-520/seed8101",
    "governing_case_min": "LH-520/seed8101",
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: unserved energy charged back as fuel, plus the SYMMETRIC charge-sustaining correction. The charge-sustaining term is signed - a pack that ends FLATTER than it started is charged the make-up, a pack that ends FULLER earns the credit - so a NEGATIVE share means this candidate's fuel figure is being reduced by a pack surplus that regen put there. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "charge_correction_direction": {
    "rule": "sign of the charge-sustaining correction over the enumerated (cycle, seed) case set",
    "credit_cases": [],
    "deficit_cases": [],
    "convention": "symmetric, SAE J1711 in spirit; declared"
   },
   "margin_vs_S0_pct_credit_free": null,
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.37298117119383584,
    "median": 0.38298506564748047,
    "max": 0.3910260870096982,
    "basis": "duty-averaged mechanical fuel-to-wheel over this run (no genset exists; bus-side shortfall priced on the wheel-side path, the generous direction)"
   },
   "spin_drag_R22d_kWh": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "charged": 0.0,
    "coast_permitting_bracket": 0.0,
    "meaning": "R22(d). `charged` is what this candidate paid; `coast_permitting_bracket` is what the same measured zero-torque loss would cost if it were charged on every geared moving sample. This integrator's driver is always either pulling or braking, so the charged figure is near zero for every candidate - that is a property of the DRIVER MODEL, not of the architecture, and the bracket is the honest statement of what R22(d) is worth here. The bracket is NOT in any margin."
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 0.0
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6214857416133291,
    "median": 0.6643656083478131,
    "max": 0.7064391214853513
   },
   "fleet_L_per_100km": {
    "min": 36.27555810633382,
    "median": 38.77841697044982,
    "max": 41.23420970769969
   },
   "margin_vs_S0_pct": null,
   "worst_case_margin_pct": null,
   "verdict": "n/a (S0 is the ruler)"
  },
  "S1": {
   "title": "Pure series - Vehicle Zero's architecture scaled to Class 8",
   "payload_kg": 19397.719023795536,
   "powertrain_mass_kg": 4232.280976204462,
   "fuel_correction_share": {
    "rule": "max AND min over the enumerated (cycle, seed) case set; the quantity is SIGNED - negative is a CREDIT",
    "value": 0.026877212425328117,
    "max": 0.026877212425328117,
    "min": 0.007116905269305126,
    "median": 0.012277274086607382,
    "governing_case_max": "REG-165/seed8105",
    "governing_case_min": "REG-165/seed8102",
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: unserved energy charged back as fuel, plus the SYMMETRIC charge-sustaining correction. The charge-sustaining term is signed - a pack that ends FLATTER than it started is charged the make-up, a pack that ends FULLER earns the credit - so a NEGATIVE share means this candidate's fuel figure is being reduced by a pack surplus that regen put there. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "charge_correction_direction": {
    "rule": "sign of the charge-sustaining correction over the enumerated (cycle, seed) case set",
    "credit_cases": [],
    "deficit_cases": [
     "LH-520/seed8101",
     "LH-520/seed8102",
     "LH-520/seed8103",
     "LH-520/seed8104",
     "LH-520/seed8105",
     "LH-520/seed8106",
     "LH-520/seed8107",
     "LH-520/seed8108",
     "REG-165/seed8101",
     "REG-165/seed8102",
     "REG-165/seed8103",
     "REG-165/seed8104",
     "REG-165/seed8105",
     "REG-165/seed8106",
     "REG-165/seed8107",
     "REG-165/seed8108"
    ],
    "convention": "symmetric, SAE J1711 in spirit; declared"
   },
   "margin_vs_S0_pct_credit_free": {
    "rule": "the same paired per-seed margin with the charge-sustaining CREDIT suppressed and the deficit make-up kept (F4)",
    "min": -0.6884959422473613,
    "median": 0.7337463427837478,
    "max": 2.569898327809644
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.41449332211216894,
    "median": 0.4190914150820708,
    "max": 0.4226752775798883,
    "basis": "duty-averaged genset fuel-to-bus over this run"
   },
   "spin_drag_R22d_kWh": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "charged": 0.004135114175379598,
    "coast_permitting_bracket": 38.06201648325889,
    "meaning": "R22(d). `charged` is what this candidate paid; `coast_permitting_bracket` is what the same measured zero-torque loss would cost if it were charged on every geared moving sample. This integrator's driver is always either pulling or braking, so the charged figure is near zero for every candidate - that is a property of the DRIVER MODEL, not of the architecture, and the bracket is the honest statement of what R22(d) is worth here. The bracket is NOT in any margin."
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 13.315260790597016
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6095044911397823,
    "median": 0.6607199643704494,
    "max": 0.7113029261712258
   },
   "fleet_L_per_100km": {
    "min": 33.20171207447143,
    "median": 35.99158716264765,
    "max": 38.74700727520954
   },
   "margin_vs_S0_pct": {
    "nominal_min": -0.6884959422473613,
    "nominal_median": 0.7337463427837478,
    "nominal_max": 2.569898327809644
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -0.6884959422473613,
     "payload_plus20": 0.14826115654603808,
     "payload_minus20": -2.205497383472892,
     "grade_heavy": 7.5212697961006905,
     "cold_minus10C": -12.866708553446385,
     "hot_alt_2000m_45C": 1.7076604041225378
    },
    "value": -12.866708553446385,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S2": {
   "title": "Single cruise-ratio + torque-fill, traction machine on a disconnect",
   "payload_kg": 19105.719023795536,
   "powertrain_mass_kg": 4524.280976204462,
   "fuel_correction_share": {
    "rule": "max AND min over the enumerated (cycle, seed) case set; the quantity is SIGNED - negative is a CREDIT",
    "value": 0.02273009446188268,
    "max": 0.02273009446188268,
    "min": -0.016796470753665218,
    "median": 0.008167215817389963,
    "governing_case_max": "REG-165/seed8105",
    "governing_case_min": "LH-520/seed8108",
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: unserved energy charged back as fuel, plus the SYMMETRIC charge-sustaining correction. The charge-sustaining term is signed - a pack that ends FLATTER than it started is charged the make-up, a pack that ends FULLER earns the credit - so a NEGATIVE share means this candidate's fuel figure is being reduced by a pack surplus that regen put there. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "charge_correction_direction": {
    "rule": "sign of the charge-sustaining correction over the enumerated (cycle, seed) case set",
    "credit_cases": [
     "LH-520/seed8101",
     "LH-520/seed8102",
     "LH-520/seed8103",
     "LH-520/seed8104",
     "LH-520/seed8106",
     "LH-520/seed8107",
     "LH-520/seed8108"
    ],
    "deficit_cases": [
     "LH-520/seed8105",
     "REG-165/seed8101",
     "REG-165/seed8102",
     "REG-165/seed8103",
     "REG-165/seed8104",
     "REG-165/seed8105",
     "REG-165/seed8106",
     "REG-165/seed8107",
     "REG-165/seed8108"
    ],
    "convention": "symmetric, SAE J1711 in spirit; declared"
   },
   "margin_vs_S0_pct_credit_free": {
    "rule": "the same paired per-seed margin with the charge-sustaining CREDIT suppressed and the deficit make-up kept (F4)",
    "min": 0.5124372542877277,
    "median": 1.0674463396108331,
    "max": 2.4487590772876913
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.3968106376750855,
    "median": 0.4146269234821586,
    "max": 0.42531755750296996,
    "basis": "duty-averaged genset fuel-to-bus over this run"
   },
   "spin_drag_R22d_kWh": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "charged": 0.002629161608103409,
    "coast_permitting_bracket": 13.829876997780561,
    "meaning": "R22(d). `charged` is what this candidate paid; `coast_permitting_bracket` is what the same measured zero-torque loss would cost if it were charged on every geared moving sample. This integrator's driver is always either pulling or braking, so the charged figure is near zero for every candidate - that is a property of the DRIVER MODEL, not of the architecture, and the bracket is the honest statement of what R22(d) is worth here. The bracket is NOT in any margin."
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 15.585890940691655
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6017720784384069,
    "median": 0.6518292582454155,
    "max": 0.7022632887002268
   },
   "fleet_L_per_100km": {
    "min": 32.287046883451794,
    "median": 34.972778856055584,
    "max": 37.67873010264968
   },
   "margin_vs_S0_pct": {
    "nominal_min": 0.5911100699440873,
    "nominal_median": 1.8879465349681643,
    "nominal_max": 3.2431626584081483
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": 0.5911100699440873,
     "payload_plus20": 1.4766316520959766,
     "payload_minus20": -0.8120442856919871,
     "grade_heavy": 7.924063200301153,
     "cold_minus10C": -9.227055078976527,
     "hot_alt_2000m_45C": 2.6395010588900925
    },
    "value": -9.227055078976527,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S3": {
   "title": "Tandem split - diesel axle on ONE fixed ratio (no gearbox anywhere) + disconnectable e-axle",
   "payload_kg": 19559.231387580392,
   "powertrain_mass_kg": 4070.768612419607,
   "fuel_correction_share": {
    "rule": "max AND min over the enumerated (cycle, seed) case set; the quantity is SIGNED - negative is a CREDIT",
    "value": 0.38488104185438,
    "max": 0.38488104185438,
    "min": 0.15837754626305905,
    "median": 0.192093401741028,
    "governing_case_max": "REG-165/seed8102",
    "governing_case_min": "REG-165/seed8108",
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: unserved energy charged back as fuel, plus the SYMMETRIC charge-sustaining correction. The charge-sustaining term is signed - a pack that ends FLATTER than it started is charged the make-up, a pack that ends FULLER earns the credit - so a NEGATIVE share means this candidate's fuel figure is being reduced by a pack surplus that regen put there. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "charge_correction_direction": {
    "rule": "sign of the charge-sustaining correction over the enumerated (cycle, seed) case set",
    "credit_cases": [
     "LH-520/seed8101",
     "LH-520/seed8102",
     "LH-520/seed8106",
     "LH-520/seed8108"
    ],
    "deficit_cases": [
     "LH-520/seed8103",
     "LH-520/seed8104",
     "LH-520/seed8105",
     "LH-520/seed8107",
     "REG-165/seed8101",
     "REG-165/seed8102",
     "REG-165/seed8103",
     "REG-165/seed8104",
     "REG-165/seed8105",
     "REG-165/seed8106",
     "REG-165/seed8107",
     "REG-165/seed8108"
    ],
    "convention": "symmetric, SAE J1711 in spirit; declared"
   },
   "margin_vs_S0_pct_credit_free": {
    "rule": "the same paired per-seed margin with the charge-sustaining CREDIT suppressed and the deficit make-up kept (F4)",
    "min": -1.085394090482248,
    "median": 1.204603366677171,
    "max": 2.3054583653529326
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.3780796043061614,
    "median": 0.3891005632452811,
    "max": 0.39487456062631143,
    "basis": "duty-averaged mechanical fuel-to-wheel over this run (no genset exists; bus-side shortfall priced on the wheel-side path, the generous direction)"
   },
   "spin_drag_R22d_kWh": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "charged": 0.004408960261944974,
    "coast_permitting_bracket": 18.156849222919114,
    "meaning": "R22(d). `charged` is what this candidate paid; `coast_permitting_bracket` is what the same measured zero-torque loss would cost if it were charged on every geared moving sample. This integrator's driver is always either pulling or braking, so the charged figure is near zero for every candidate - that is a property of the DRIVER MODEL, not of the architecture, and the bracket is the honest statement of what R22(d) is worth here. The bracket is NOT in any margin."
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 171.09314753818566
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6006759320859523,
    "median": 0.6555958562411144,
    "max": 0.714106769962808
   },
   "fleet_L_per_100km": {
    "min": 32.993236499763185,
    "median": 36.00981490653882,
    "max": 39.22363505667069
   },
   "margin_vs_S0_pct": {
    "nominal_min": -1.085394090482248,
    "nominal_median": 1.6381290929839507,
    "nominal_max": 3.3483969356008414
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -1.085394090482248,
     "payload_plus20": -0.929107318564778,
     "payload_minus20": -2.272955788620288,
     "grade_heavy": 5.631506555489104,
     "cold_minus10C": -14.174316723180722,
     "hot_alt_2000m_45C": -0.5589602039722611
    },
    "value": -14.174316723180722,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  },
  "S4": {
   "title": "Range-extended BEV - large pack + 194 kW-shaft / 185 kW-bus sustainer genset",
   "payload_kg": 19343.56414646685,
   "powertrain_mass_kg": 4286.435853533148,
   "fuel_correction_share": {
    "rule": "max AND min over the enumerated (cycle, seed) case set; the quantity is SIGNED - negative is a CREDIT",
    "value": 0.08812032873737356,
    "max": 0.08812032873737356,
    "min": 0.002064450876536177,
    "median": 0.028529673013820346,
    "governing_case_max": "LH-520/seed8105",
    "governing_case_min": "REG-165/seed8108",
    "governing_case": "worst (cycle, seed) at the nominal corner",
    "meaning": "fraction of this candidate's reported fuel that is a CORRECTION rather than fuel the model watched it burn: unserved energy charged back as fuel, plus the SYMMETRIC charge-sustaining correction. The charge-sustaining term is signed - a pack that ends FLATTER than it started is charged the make-up, a pack that ends FULLER earns the credit - so a NEGATIVE share means this candidate's fuel figure is being reduced by a pack surplus that regen put there. A large POSITIVE share means the candidate could not actually do the mission and was credited with doing it anyway, which is a capability finding."
   },
   "charge_correction_direction": {
    "rule": "sign of the charge-sustaining correction over the enumerated (cycle, seed) case set",
    "credit_cases": [],
    "deficit_cases": [
     "LH-520/seed8101",
     "LH-520/seed8102",
     "LH-520/seed8103",
     "LH-520/seed8104",
     "LH-520/seed8105",
     "LH-520/seed8106",
     "LH-520/seed8107",
     "LH-520/seed8108",
     "REG-165/seed8101",
     "REG-165/seed8102",
     "REG-165/seed8103",
     "REG-165/seed8104",
     "REG-165/seed8105",
     "REG-165/seed8106",
     "REG-165/seed8107",
     "REG-165/seed8108"
    ],
    "convention": "symmetric, SAE J1711 in spirit; declared"
   },
   "margin_vs_S0_pct_credit_free": {
    "rule": "the same paired per-seed margin with the charge-sustaining CREDIT suppressed and the deficit make-up kept (F4)",
    "min": -3.8418443085956486,
    "median": -1.059736946707445,
    "max": 1.9783883737854224
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.3949179736678972,
    "median": 0.3958640248208973,
    "max": 0.39673319272654706,
    "basis": "duty-averaged genset fuel-to-bus over this run"
   },
   "spin_drag_R22d_kWh": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "charged": 0.004803986992596305,
    "coast_permitting_bracket": 38.11964503312203,
    "meaning": "R22(d). `charged` is what this candidate paid; `coast_permitting_bracket` is what the same measured zero-torque loss would cost if it were charged on every geared moving sample. This integrator's driver is always either pulling or braking, so the charged figure is near zero for every candidate - that is a property of the DRIVER MODEL, not of the architecture, and the bracket is the honest statement of what R22(d) is worth here. The bracket is NOT in any margin."
   },
   "unserved_kWh_nominal": {
    "rule": "max over the enumerated (cycle, seed) case set",
    "value": 67.6081947764574
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6146392253176963,
    "median": 0.6715338311955045,
    "max": 0.7335794126678293
   },
   "fleet_L_per_100km": {
    "min": 33.38794393047816,
    "median": 36.478527532611665,
    "max": 39.84891834074979
   },
   "margin_vs_S0_pct": {
    "nominal_min": -3.8418443085956486,
    "nominal_median": -1.059736946707445,
    "nominal_max": 1.9783883737854224
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -3.8418443085956486,
     "payload_plus20": -2.0743816904664394,
     "payload_minus20": -6.1689875825129175,
     "grade_heavy": 5.549247875085047,
     "cold_minus10C": -17.206366772152812,
     "hot_alt_2000m_45C": -0.3022564005707669
    },
    "value": -17.206366772152812,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  }
 },
 "unserved_energy_kWh": {
  "rule": "max over the enumerated (candidate, corner, cycle) case set",
  "value": 275.1792730595762,
  "governing_case": "S3/cold_minus10C/LH-520",
  "cases_over_1kWh": {
   "S1/cold_minus10C/LH-520": 21.4520756174574,
   "S1/grade_heavy/LH-520": 15.826776447536048,
   "S1/hot_alt_2000m_45C/LH-520": 13.548095405017767,
   "S1/nominal/LH-520": 13.315260790597016,
   "S1/payload_minus20/LH-520": 9.99007903188616,
   "S1/payload_plus20/LH-520": 16.614506691847673,
   "S2/cold_minus10C/LH-520": 21.562779119971847,
   "S2/grade_heavy/LH-520": 12.601268461389637,
   "S2/hot_alt_2000m_45C/LH-520": 12.124722944244336,
   "S2/nominal/LH-520": 15.585890940691655,
   "S2/payload_minus20/LH-520": 11.996531882297953,
   "S2/payload_plus20/LH-520": 17.69572262884129,
   "S3/cold_minus10C/LH-520": 275.1792730595762,
   "S3/cold_minus10C/REG-165": 105.38347474031002,
   "S3/grade_heavy/LH-520": 241.7298336536963,
   "S3/grade_heavy/REG-165": 100.04512105552523,
   "S3/hot_alt_2000m_45C/LH-520": 168.89255000086027,
   "S3/hot_alt_2000m_45C/REG-165": 63.53910754295639,
   "S3/nominal/LH-520": 171.09314753818566,
   "S3/nominal/REG-165": 62.6671610123646,
   "S3/payload_minus20/LH-520": 144.85227549166848,
   "S3/payload_minus20/REG-165": 20.874116470749613,
   "S3/payload_plus20/LH-520": 212.87479264352788,
   "S3/payload_plus20/REG-165": 73.38790635128787,
   "S4/cold_minus10C/LH-520": 170.7991090899651,
   "S4/grade_heavy/LH-520": 93.2599510393586,
   "S4/hot_alt_2000m_45C/LH-520": 51.67534181033989,
   "S4/nominal/LH-520": 67.6081947764574,
   "S4/payload_minus20/LH-520": 48.091325162940166,
   "S4/payload_plus20/LH-520": 89.63060373535244
  },
  "meaning": "bus energy the prime mover and pack together could not deliver. It is charged back as fuel so every candidate completes the same mission, and reported here raw because a large value is a CAPABILITY finding, not a fuel one."
 },
 "retard_overcommitment": {
  "rule": "max over the enumerated (candidate, corner, cycle, seed) case set of the sustained 60-second retarding power the run COMMANDED and no sink could absorb",
  "value_kW": 254.31185405331928,
  "governing_case": "S4/grade_heavy/LH-520/seed8101",
  "energy_kWh_at_governing_case": 0.12673970287277164,
  "cases_kW": {
   "S1/grade_heavy/LH-520/seed8101": 190.7304542170666,
   "S1/grade_heavy/LH-520/seed8102": 113.07787944228278,
   "S1/grade_heavy/LH-520/seed8103": 43.505796947154806,
   "S1/grade_heavy/LH-520/seed8104": 42.778318366830035,
   "S1/grade_heavy/LH-520/seed8105": 55.31548680633853,
   "S1/grade_heavy/LH-520/seed8106": 68.56744950176608,
   "S1/grade_heavy/LH-520/seed8107": 68.94980627750681,
   "S1/grade_heavy/LH-520/seed8108": 190.15723043907087,
   "S1/hot_alt_2000m_45C/LH-520/seed8101": 188.130463674186,
   "S1/hot_alt_2000m_45C/LH-520/seed8102": 126.99095997296536,
   "S1/hot_alt_2000m_45C/LH-520/seed8103": 55.84636197347646,
   "S1/hot_alt_2000m_45C/LH-520/seed8104": 58.72562893163422,
   "S1/hot_alt_2000m_45C/LH-520/seed8105": 78.47374302542335,
   "S1/hot_alt_2000m_45C/LH-520/seed8106": 75.24374259410934,
   "S1/hot_alt_2000m_45C/LH-520/seed8107": 81.21771285925792,
   "S1/hot_alt_2000m_45C/LH-520/seed8108": 56.135848454343204,
   "S1/nominal/LH-520/seed8101": 190.7317622186647,
   "S1/nominal/LH-520/seed8102": 110.63116885055098,
   "S1/nominal/LH-520/seed8103": 190.3240022771604,
   "S1/nominal/LH-520/seed8104": 43.498822416808366,
   "S1/nominal/LH-520/seed8105": 55.80512297496409,
   "S1/nominal/LH-520/seed8106": 65.10114200173882,
   "S1/nominal/LH-520/seed8107": 65.76678892590292,
   "S1/nominal/LH-520/seed8108": 46.817958259763714,
   "S1/payload_minus20/LH-520/seed8101": 132.76039407452924,
   "S1/payload_minus20/LH-520/seed8102": 53.0241937753417,
   "S1/payload_minus20/LH-520/seed8103": 190.32400227716244,
   "S1/payload_minus20/LH-520/seed8105": 190.86035181093132,
   "S1/payload_minus20/LH-520/seed8106": 15.555903242286206,
   "S1/payload_minus20/LH-520/seed8107": 14.320909498481228,
   "S1/payload_minus20/LH-520/seed8108": 190.18787235718526,
   "S1/payload_plus20/LH-520/seed8101": 190.7304541919708,
   "S1/payload_plus20/LH-520/seed8102": 167.9085488396821,
   "S1/payload_plus20/LH-520/seed8103": 90.14389073795667,
   "S1/payload_plus20/LH-520/seed8104": 92.42895013232823,
   "S1/payload_plus20/LH-520/seed8105": 110.1376016063299,
   "S1/payload_plus20/LH-520/seed8106": 114.45646088018401,
   "S1/payload_plus20/LH-520/seed8107": 117.68023756134369,
   "S1/payload_plus20/LH-520/seed8108": 190.15723060036646,
   "S2/grade_heavy/LH-520/seed8101": 190.39802527022403,
   "S2/grade_heavy/LH-520/seed8102": 191.4648730398667,
   "S2/grade_heavy/LH-520/seed8104": 190.26640122150638,
   "S2/grade_heavy/LH-520/seed8106": 190.69139055887024,
   "S2/grade_heavy/LH-520/seed8108": 101.50971928026974,
   "S2/grade_heavy/REG-165/seed8101": 45.02031918083469,
   "S2/grade_heavy/REG-165/seed8104": 92.64688446364431,
   "S2/grade_heavy/REG-165/seed8105": 160.67271980295095,
   "S2/grade_heavy/REG-165/seed8106": 96.02829003693427,
   "S2/grade_heavy/REG-165/seed8108": 187.81854273160366,
   "S2/hot_alt_2000m_45C/LH-520/seed8101": 187.79802528652385,
   "S2/hot_alt_2000m_45C/LH-520/seed8102": 188.88636390782892,
   "S2/hot_alt_2000m_45C/LH-520/seed8103": 187.72400227716037,
   "S2/hot_alt_2000m_45C/LH-520/seed8104": 187.7798732687089,
   "S2/hot_alt_2000m_45C/LH-520/seed8105": 95.81253458742344,
   "S2/hot_alt_2000m_45C/LH-520/seed8106": 188.02086279786954,
   "S2/hot_alt_2000m_45C/LH-520/seed8107": 188.39925558734444,
   "S2/hot_alt_2000m_45C/LH-520/seed8108": 85.44711119561549,
   "S2/nominal/LH-520/seed8101": 190.39546424590367,
   "S2/nominal/LH-520/seed8102": 191.5003716538282,
   "S2/nominal/LH-520/seed8103": 190.32400227716357,
   "S2/nominal/LH-520/seed8104": 188.70172612883084,
   "S2/nominal/LH-520/seed8105": 87.51504564902189,
   "S2/nominal/LH-520/seed8106": 190.60316382984126,
   "S2/nominal/LH-520/seed8107": 190.8163012241473,
   "S2/nominal/LH-520/seed8108": 81.62778515647608,
   "S2/payload_minus20/LH-520/seed8101": 188.69129835673243,
   "S2/payload_minus20/LH-520/seed8102": 164.23341985148875,
   "S2/payload_minus20/LH-520/seed8103": 140.11826079772635,
   "S2/payload_minus20/LH-520/seed8104": 147.41574791100732,
   "S2/payload_minus20/LH-520/seed8105": 38.1583124872198,
   "S2/payload_minus20/LH-520/seed8106": 173.31865768019486,
   "S2/payload_minus20/LH-520/seed8107": 160.77031860463853,
   "S2/payload_minus20/LH-520/seed8108": 190.18787969930156,
   "S2/payload_plus20/LH-520/seed8101": 190.3980249786307,
   "S2/payload_plus20/LH-520/seed8102": 191.50033229912844,
   "S2/payload_plus20/LH-520/seed8103": 188.69583079901554,
   "S2/payload_plus20/LH-520/seed8104": 190.35892087023035,
   "S2/payload_plus20/LH-520/seed8105": 136.5329300128194,
   "S2/payload_plus20/LH-520/seed8106": 190.8085647819123,
   "S2/payload_plus20/LH-520/seed8107": 190.99925551002366,
   "S2/payload_plus20/LH-520/seed8108": 190.15733001049557,
   "S3/grade_heavy/LH-520/seed8101": 199.46825130490652,
   "S3/grade_heavy/LH-520/seed8103": 199.56094639529977,
   "S3/grade_heavy/LH-520/seed8104": 199.14558221837513,
   "S3/grade_heavy/LH-520/seed8105": 16.619455721509297,
   "S3/grade_heavy/LH-520/seed8106": 200.33829855817862,
   "S3/grade_heavy/LH-520/seed8107": 22.8452458421186,
   "S3/grade_heavy/LH-520/seed8108": 16.65465092871574,
   "S3/hot_alt_2000m_45C/LH-520/seed8101": 196.15309589555147,
   "S3/hot_alt_2000m_45C/LH-520/seed8103": 19.171734942017906,
   "S3/hot_alt_2000m_45C/LH-520/seed8104": 39.21377560195015,
   "S3/hot_alt_2000m_45C/LH-520/seed8105": 13.993490454229999,
   "S3/hot_alt_2000m_45C/LH-520/seed8106": 197.7386381585062,
   "S3/hot_alt_2000m_45C/LH-520/seed8107": 34.60442420200198,
   "S3/hot_alt_2000m_45C/LH-520/seed8108": 24.72789354510951,
   "S3/nominal/LH-520/seed8101": 200.25175085222588,
   "S3/nominal/LH-520/seed8103": 16.663672137550293,
   "S3/nominal/LH-520/seed8104": 199.2891512873814,
   "S3/nominal/LH-520/seed8105": 16.594168810974992,
   "S3/nominal/LH-520/seed8106": 200.33852194976993,
   "S3/nominal/LH-520/seed8107": 19.178235432595443,
   "S3/nominal/LH-520/seed8108": 125.15560836615128,
   "S3/payload_minus20/LH-520/seed8101": 199.13580830911144,
   "S3/payload_minus20/LH-520/seed8102": 52.830847259468555,
   "S3/payload_minus20/LH-520/seed8103": 71.41617398058764,
   "S3/payload_minus20/LH-520/seed8104": 199.41250597020928,
   "S3/payload_minus20/LH-520/seed8105": 83.89631160998613,
   "S3/payload_minus20/LH-520/seed8106": 200.25239302831153,
   "S3/payload_minus20/LH-520/seed8107": 189.41821726168132,
   "S3/payload_minus20/LH-520/seed8108": 88.5453073653295,
   "S3/payload_plus20/LH-520/seed8101": 200.15092488769994,
   "S3/payload_plus20/LH-520/seed8103": 54.927396545513545,
   "S3/payload_plus20/LH-520/seed8104": 149.29312364732652,
   "S3/payload_plus20/LH-520/seed8105": 198.97392339037492,
   "S3/payload_plus20/LH-520/seed8106": 200.3381045628496,
   "S3/payload_plus20/LH-520/seed8107": 73.19812868149108,
   "S3/payload_plus20/LH-520/seed8108": 162.97305603881233,
   "S4/grade_heavy/LH-520/seed8101": 254.31185405331928,
   "S4/payload_plus20/LH-520/seed8101": 252.73526528048217,
   "S4/payload_plus20/LH-520/seed8106": 108.19543419685778
  },
  "meaning": "THE BRAKING-SIDE MIRROR OF `unserved_energy_kWh`, and read it the same way: it is a CAPABILITY statement, not a heat one. The traction and retard envelope is a function of road speed alone and does not re-solve when the buffer pack fills, so on a long descent the integrator keeps commanding the regen channel at its warm charge ceiling after the pack has stopped accepting. `series_dispatch` and S3's SOC loop then send that power to the brake resistor - which is where it physically goes - and the sum can exceed the resistor rating whose mass was charged. What the resistor TOOK is booked in `brake_resistor_kW`, capped at that rating; the remainder is this field. It is NOT a cooling load and WS6 must not size on it. What it measures is that the simulated descent lets the candidate retard harder than its hardware can, so its simulated descent speed is optimistic by that much. The physically correct member for the pack-full state is the enumerated `descent_6pct_pack_saturated` analytic case, which respects the rating and holds a LOWER speed. Escalated as ESC-WS8-10, not self-resolved.",
  "never_absorbed": "no margin reads this field; it is reported raw, on the convention WS4's ESC-5 established"
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
   "S1": 1.751782303438002,
   "S2": 1.834617721374109,
   "S3": 2.378908568404933
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
  "max_ratio_without_overspeed_rule": "max over the ENUMERATED swept ratio set; see ratio_ceiling_closed_form for the physics bound",
  "ratio_ceiling_closed_form": {
   "value": 3.769911184307752,
   "rule": "PHYSICS BOUND, solved in closed form: ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)",
   "rpm_ceiling": 2100.0,
   "v_cruise_kmh": 105.0,
   "r_dyn_m": 0.5,
   "rpm_at_v_cruise": 2100.0000000000005,
   "note": "this is the ratio ceiling. The swept-set figure below is the highest ratio the ENUMERATED SWEEP happens to contain under it, and is an illustration, not the limit."
  },
  "ratio_needed_to_hold_6pct": {
   "grade": 0.06,
   "ratio": 6.879999999999896,
   "engine_rpm_at_105kmh": 3832.4510296527815,
   "rpm_ceiling": 2100.0,
   "over_ceiling_by_rpm": 1732.4510296527815,
   "rule": "lowest ratio on a 0.01 grid in [2.0, 12.0] whose axle A balances road load somewhere above its own lugging floor, with the hold test scanning road speed on a 0.1 m/s grid. This is a SWEPT result, not a closed form - see `resolution_sensitivity`.",
   "resolution_sensitivity": {
    "coarse": {
     "ratio_step": 0.01,
     "speed_step_ms": 0.1,
     "ratio": 6.879999999999896,
     "engine_rpm_at_105kmh": 3832.4510296527815
    },
    "fine": {
     "ratio_step": 0.001,
     "speed_step_ms": 0.01,
     "ratio": 6.8709999999998965,
     "engine_rpm_at_105kmh": 3827.437648945387
    },
    "d_ratio": -0.008999999999999453,
    "d_rpm_at_105kmh": -5.01338070739439,
    "over_ceiling_by_rpm_fine": 1727.437648945387,
    "conclusion_unchanged": true,
    "note": "the conclusion is that this ratio puts the engine over its rpm ceiling at 105 km/h. Ten times the resolution in both dimensions moves the ratio by 0.009 and the engine speed by 5 rpm, against a gap of 1,732 rpm. The grid decides a decimal place; it does not decide the answer."
   }
  },
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
 "per_km_margin_paired": {
  "rule": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE - candidate seed i against S0 seed i - then the 8-seed envelope. This is the statistic every per-km claim in the report is made on. The RATIO OF MEDIANS is exported beside it for disclosure only: r2's headline bullets were computed that way while every margin in the report was paired, and for S3 the two statistics differ in SIGN.",
  "corners": {
   "nominal": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 6.031890631883995,
      "median": 7.359206303223637,
      "max": 9.072805547414962,
      "mean": 7.480790388784736
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 7.18654866681587,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 8.622645202258077,
      "median": 9.81470645414946,
      "max": 11.060430701008329,
      "mean": 9.951642914185575
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 9.81380471847065,
     "ratio_of_medians_sign_differs": false
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 4.875986869353187,
      "median": 7.438893779858603,
      "max": 9.04830077858276,
      "mean": 7.317006640631306
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 7.139543798347265,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 3.3595681274600055,
      "median": 5.948736865349945,
      "max": 8.776168764409787,
      "mean": 6.3066382128711
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 5.930849213341338,
     "ratio_of_medians_sign_differs": false
    }
   },
   "payload_plus20": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 6.812798935639627,
      "median": 8.28720964158641,
      "max": 9.935058173807787,
      "mean": 8.399228720963418
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 8.178329752627175,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 9.436622904355783,
      "median": 10.813499554006134,
      "max": 12.051301301862727,
      "mean": 10.948363793819453
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 10.812919342890433,
     "ratio_of_medians_sign_differs": false
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 5.023056830130286,
      "median": 8.001634669238033,
      "max": 9.606210482828157,
      "mean": 7.838511011043626
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 7.684079637796904,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 5.004457544359917,
      "median": 7.570825104248362,
      "max": 9.808021297912113,
      "mean": 7.7713746502305785
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 7.573486243955157,
     "ratio_of_medians_sign_differs": false
    }
   },
   "payload_minus20": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 4.616140441093234,
      "median": 5.817825067504271,
      "max": 7.541127849429932,
      "mean": 6.035808140970573
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 5.794508712438512,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 7.332855793270943,
      "median": 8.345983879507177,
      "max": 9.302470574700902,
      "mean": 8.373024795675946
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 8.344728297806531,
     "ratio_of_medians_sign_differs": false
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 3.7584600932689995,
      "median": 6.357296955347122,
      "max": 8.067658728898735,
      "mean": 6.304865261307729
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 6.081348702082447,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 1.1938118033302165,
      "median": 3.788571459836598,
      "max": 6.511807852935679,
      "mean": 4.152655589073022
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 3.79117454398322,
     "ratio_of_medians_sign_differs": false
    }
   },
   "grade_heavy": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 13.693701026094182,
      "median": 15.972420116465045,
      "max": 18.798033460772178,
      "mean": 16.335490602433886
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 15.948441479411867,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 15.363147589713645,
      "median": 16.581118036986858,
      "max": 17.778582580196733,
      "mean": 16.64062891404074
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 16.58273823659939,
     "ratio_of_medians_sign_differs": false
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 11.196766948349667,
      "median": 15.005040157116312,
      "max": 17.376319612115342,
      "mean": 15.053905321144585
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 15.00051611131046,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 12.099389828706636,
      "median": 16.222667755979177,
      "max": 19.795987939651543,
      "mean": 16.299790038883778
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 15.878261126251664,
     "ratio_of_medians_sign_differs": false
    }
   },
   "cold_minus10C": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": -5.333495292777162,
      "median": -4.913081516822521,
      "max": -4.679521271981328,
      "mean": -4.954879300750733
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 8,
     "seeds_below_zero": [
      8101,
      8102,
      8103,
      8104,
      8105,
      8106,
      8107,
      8108
     ],
     "wins_on_every_seed": false,
     "ratio_of_medians_pct": -5.034186042244777,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": -0.40228165193961646,
      "median": 0.08277109427341248,
      "max": 0.6508115880496167,
      "mean": 0.1590828844213328
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 4,
     "seeds_below_zero": [
      8102,
      8103,
      8105,
      8107
     ],
     "wins_on_every_seed": false,
     "ratio_of_medians_pct": -0.09566008132900927,
     "ratio_of_medians_sign_differs": true
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": -7.441033404261803,
      "median": -5.762301655858897,
      "max": -4.653686408112164,
      "mean": -5.907953769417805
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 8,
     "seeds_below_zero": [
      8101,
      8102,
      8103,
      8104,
      8105,
      8106,
      8107,
      8108
     ],
     "wins_on_every_seed": false,
     "ratio_of_medians_pct": -6.054311808727592,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": -9.078127208634049,
      "median": -8.355831841581775,
      "max": -7.195587702582474,
      "mean": -8.215911474512161
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 8,
     "seeds_below_zero": [
      8101,
      8102,
      8103,
      8104,
      8105,
      8106,
      8107,
      8108
     ],
     "wins_on_every_seed": false,
     "ratio_of_medians_pct": -8.437053879747507,
     "ratio_of_medians_sign_differs": false
    }
   },
   "hot_alt_2000m_45C": {
    "S1": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 8.268117119445591,
      "median": 9.582221665676244,
      "max": 11.191788506883617,
      "mean": 9.660722876982701
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 9.426356756832677,
     "ratio_of_medians_sign_differs": false
    },
    "S2": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 10.505540688699117,
      "median": 11.246928091366492,
      "max": 12.20974800641912,
      "mean": 11.292817521626942
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 11.24645756356955,
     "ratio_of_medians_sign_differs": false
    },
    "S3": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 5.371374995237816,
      "median": 7.9264537368221655,
      "max": 9.860764108928779,
      "mean": 7.943971798749726
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 7.589332244816653,
     "ratio_of_medians_sign_differs": false
    },
    "S4": {
     "basis": "PAIRED per-seed margin on fleet-mission MJ per KILOMETRE, then the 8-seed envelope - the same statistic as the metric of record, on the other denominator. Per M2, the ratio of medians is exported alongside for disclosure and is NOT the statistic any claim in this report is made on.",
     "ensemble": {
      "n": 8,
      "min": 6.6536862776133905,
      "median": 9.099450030584993,
      "max": 11.594854231672544,
      "mean": 9.341941266670824
     },
     "n_seeds": 8,
     "n_seeds_below_zero": 0,
     "seeds_below_zero": [],
     "wins_on_every_seed": true,
     "ratio_of_medians_pct": 9.022342272789022,
     "ratio_of_medians_sign_differs": false
    }
   }
  },
  "every_candidate_wins_per_km_at_nominal": true
 },
 "correction_directions": {
  "_rule": "every direction below is computed from `one_factor.rows` by `correction_directions()`; nothing here is written by hand (r2 finding M1). A correction with no one-factor row is labelled not separately measured, with the reason.",
  "_convention": "margin = (S0 - candidate)/S0 x 100, so HIGHER IS BETTER. delta = median(r3_as_reported) - median(row); delta > 0 means the correction moved the candidate UP, i.e. it was FOR that candidate; delta < 0 means AGAINST. A candidate whose delta is exactly 0.0 in a row is that correction PROVED not to reach it, not an assertion that it does not.",
  "F3": {
   "measurable": true,
   "one_factor_row": "F3_reverted_engine_dual_use",
   "deltas_pp": {
    "S1": 0.0,
    "S2": 0.06986662532569232,
    "S3": 0.0,
    "S4": 0.0
   },
   "direction": "FOR S2 (+0.070 pp); does not reach S1, S3, S4 (re-run bit-identical)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "gated in S2 only (ws8_candidates.py, `f3_s2_engine_budget`)"
  },
  "F4": {
   "measurable": true,
   "one_factor_row": "F4_reverted_credit_removed",
   "deltas_pp": {
    "S1": 0.0,
    "S2": 0.8205001953573312,
    "S3": 0.43352572630677977,
    "S4": 0.0
   },
   "direction": "FOR S2 (+0.821 pp), S3 (+0.434 pp); does not reach S1, S4 (carries none of this correction)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "exact re-pricing of the same run; applies to every candidate that has a pack"
  },
  "F5": {
   "measurable": true,
   "one_factor_row": "F5_reverted_spin_rule",
   "deltas_pp": {
    "S1": 0.0,
    "S2": 0.05209758404496467,
    "S3": 2.0546949909547987,
    "S4": 0.0
   },
   "direction": "FOR S2 (+0.052 pp), S3 (+2.055 pp); does not reach S1, S4 (re-run bit-identical)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "gated in S2 and S3 (`f5_spin_rule`)"
  },
  "F6": {
   "measurable": true,
   "one_factor_row": "F6_reverted_peak_point_pricing",
   "deltas_pp": {
    "S1": -0.01824177313851949,
    "S2": -0.014192091670700568,
    "S3": -1.9784114933026922,
    "S4": -0.11217174060994584
   },
   "direction": "AGAINST S1 (-0.018 pp), S2 (-0.014 pp), S3 (-1.978 pp), S4 (-0.112 pp)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "exact re-pricing of the same run; applies to every candidate that carries a correction",
   "per_corner": {
    "nominal": {
     "deltas_pp": {
      "S1": -0.01824177313851949,
      "S2": -0.014192091670700568,
      "S3": -1.9784114933026922,
      "S4": -0.11217174060994584
     },
     "direction": "AGAINST S1 (-0.018 pp), S2 (-0.014 pp), S3 (-1.978 pp), S4 (-0.112 pp)"
    },
    "payload_plus20": {
     "deltas_pp": {
      "S1": -0.018734392539394573,
      "S2": -0.01476221741410777,
      "S3": -2.054865818436979,
      "S4": -0.1104491339894027
     },
     "direction": "AGAINST S1 (-0.019 pp), S2 (-0.015 pp), S3 (-2.055 pp), S4 (-0.110 pp)"
    },
    "payload_minus20": {
     "deltas_pp": {
      "S1": -0.018233261854287197,
      "S2": -0.010872118093745387,
      "S3": -1.5291220950824769,
      "S4": -0.06894613976346253
     },
     "direction": "AGAINST S1 (-0.018 pp), S2 (-0.011 pp), S3 (-1.529 pp), S4 (-0.069 pp)"
    },
    "grade_heavy": {
     "deltas_pp": {
      "S1": -0.011956944785158186,
      "S2": 0.008283615370464403,
      "S3": -2.2644640973476857,
      "S4": -0.13173367361112298
     },
     "direction": "FOR S2 (+0.008 pp); AGAINST S1 (-0.012 pp), S3 (-2.264 pp), S4 (-0.132 pp)"
    },
    "cold_minus10C": {
     "deltas_pp": {
      "S1": -0.04340509126739356,
      "S2": -0.057501777038297064,
      "S3": -2.929997153892792,
      "S4": -0.3271286368855897
     },
     "direction": "AGAINST S1 (-0.043 pp), S2 (-0.058 pp), S3 (-2.930 pp), S4 (-0.327 pp)"
    },
    "hot_alt_2000m_45C": {
     "deltas_pp": {
      "S1": -0.021092190538970268,
      "S2": -0.012546878561302766,
      "S3": -2.329267416587385,
      "S4": -0.11252274712757426
     },
     "direction": "AGAINST S1 (-0.021 pp), S2 (-0.013 pp), S3 (-2.329 pp), S4 (-0.113 pp)"
    }
   },
   "sign_flips_across_corners": [
    "S2"
   ],
   "corner_caveat": "F6's direction is NOT the same at every corner - it flips for S2 - so the direction cell is stated at the nominal corner and the per-corner table is exported beside it."
  },
  "F3_and_F5": {
   "measurable": true,
   "one_factor_row": "F3_and_F5_reverted",
   "deltas_pp": {
    "S1": 0.0,
    "S2": 0.11335162529327558,
    "S3": 2.0546949909547987,
    "S4": 0.0
   },
   "direction": "FOR S2 (+0.113 pp), S3 (+2.055 pp); does not reach S1, S4 (re-run bit-identical)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "both r2 re-simulated corrections together"
  },
  "R3_S0_launch_fuel": {
   "measurable": true,
   "one_factor_row": "R3_S0_launch_fuel_reverted",
   "deltas_pp": {
    "S1": 0.002829372759294957,
    "S2": 0.0028689579999228165,
    "S3": 0.002918369912301877,
    "S4": 0.002880489905809247
   },
   "direction": "FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "moves THE RULER, so it moves every margin; measured against its own re-run S0"
  },
  "B1": {
   "measurable": true,
   "one_factor_row": "B1_reverted_brake_and_fuel",
   "deltas_pp": {
    "S1": 0.0,
    "S2": 0.08513340054260832,
    "S3": 5.26231542162744,
    "S4": 0.0
   },
   "direction": "FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical)",
   "basis": "median of the paired per-seed margin at the NOMINAL corner; delta = r3_as_reported - this row",
   "note": "gated in S2 and S3 (`b1_overrun_exclusivity`); the r3 correction R3_DIRECTIVE item 1 orders"
  },
  "F1": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F2": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F7": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F8": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F9": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F10": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F11": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F12": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  },
  "F13": {
   "measurable": false,
   "one_factor_row": null,
   "direction": "not separately measured",
   "why_not": "no one-factor row: reverting it would not be a one-line switch on the same run. It either rebuilds an export rather than the simulation (F1, F7, F8-F10, F12, F13, and every m-row), or it changes what the corner IS rather than how a run is priced (F2's cold charge acceptance, F11/R28's added corner), so a 'reverted' number would not be the same trial. The direction is left unstated rather than asserted."
  }
 },
 "corner_derate_scope": {
  "rule": "every corner's model probed at the same fixed operating points as nominal and compared leaf by leaf; membership is computed, not declared",
  "scope": {
   "nominal": {
    "quantities_that_move": [],
    "quantities_that_do_not": [
     "S0.accessory_bus_kW",
     "S0.accessory_mech_kW",
     "S0.air_density_kg_m3",
     "S0.compression_brake_rating_kW",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_bus_kW",
     "S1.accessory_mech_kW",
     "S1.air_density_kg_m3",
     "S1.brake_resistor_rating_kW",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_charge_ceiling_kW",
     "S1.pack_discharge_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.accessory_mech_kW",
     "S2.air_density_kg_m3",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_charge_ceiling_kW",
     "S2.pack_discharge_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.accessory_mech_kW",
     "S3.air_density_kg_m3",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_charge_ceiling_kW",
     "S3.pack_discharge_ceiling_kW",
     "S4.accessory_bus_kW",
     "S4.accessory_mech_kW",
     "S4.air_density_kg_m3",
     "S4.brake_resistor_rating_kW",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_charge_ceiling_kW",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [],
    "electric_side_moves": []
   },
   "payload_plus20": {
    "quantities_that_move": [],
    "quantities_that_do_not": [
     "S0.accessory_bus_kW",
     "S0.accessory_mech_kW",
     "S0.air_density_kg_m3",
     "S0.compression_brake_rating_kW",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_bus_kW",
     "S1.accessory_mech_kW",
     "S1.air_density_kg_m3",
     "S1.brake_resistor_rating_kW",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_charge_ceiling_kW",
     "S1.pack_discharge_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.accessory_mech_kW",
     "S2.air_density_kg_m3",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_charge_ceiling_kW",
     "S2.pack_discharge_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.accessory_mech_kW",
     "S3.air_density_kg_m3",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_charge_ceiling_kW",
     "S3.pack_discharge_ceiling_kW",
     "S4.accessory_bus_kW",
     "S4.accessory_mech_kW",
     "S4.air_density_kg_m3",
     "S4.brake_resistor_rating_kW",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_charge_ceiling_kW",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [],
    "electric_side_moves": []
   },
   "payload_minus20": {
    "quantities_that_move": [],
    "quantities_that_do_not": [
     "S0.accessory_bus_kW",
     "S0.accessory_mech_kW",
     "S0.air_density_kg_m3",
     "S0.compression_brake_rating_kW",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_bus_kW",
     "S1.accessory_mech_kW",
     "S1.air_density_kg_m3",
     "S1.brake_resistor_rating_kW",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_charge_ceiling_kW",
     "S1.pack_discharge_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.accessory_mech_kW",
     "S2.air_density_kg_m3",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_charge_ceiling_kW",
     "S2.pack_discharge_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.accessory_mech_kW",
     "S3.air_density_kg_m3",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_charge_ceiling_kW",
     "S3.pack_discharge_ceiling_kW",
     "S4.accessory_bus_kW",
     "S4.accessory_mech_kW",
     "S4.air_density_kg_m3",
     "S4.brake_resistor_rating_kW",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_charge_ceiling_kW",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [],
    "electric_side_moves": []
   },
   "grade_heavy": {
    "quantities_that_move": [],
    "quantities_that_do_not": [
     "S0.accessory_bus_kW",
     "S0.accessory_mech_kW",
     "S0.air_density_kg_m3",
     "S0.compression_brake_rating_kW",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_bus_kW",
     "S1.accessory_mech_kW",
     "S1.air_density_kg_m3",
     "S1.brake_resistor_rating_kW",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_charge_ceiling_kW",
     "S1.pack_discharge_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.accessory_mech_kW",
     "S2.air_density_kg_m3",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_charge_ceiling_kW",
     "S2.pack_discharge_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.accessory_mech_kW",
     "S3.air_density_kg_m3",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_charge_ceiling_kW",
     "S3.pack_discharge_ceiling_kW",
     "S4.accessory_bus_kW",
     "S4.accessory_mech_kW",
     "S4.air_density_kg_m3",
     "S4.brake_resistor_rating_kW",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_charge_ceiling_kW",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [],
    "electric_side_moves": []
   },
   "cold_minus10C": {
    "quantities_that_move": [
     "S0.accessory_bus_kW",
     "S0.air_density_kg_m3",
     "S1.accessory_bus_kW",
     "S1.air_density_kg_m3",
     "S1.pack_charge_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.air_density_kg_m3",
     "S2.pack_charge_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.air_density_kg_m3",
     "S3.pack_charge_ceiling_kW",
     "S4.accessory_bus_kW",
     "S4.air_density_kg_m3",
     "S4.pack_charge_ceiling_kW"
    ],
    "quantities_that_do_not": [
     "S0.accessory_mech_kW",
     "S0.compression_brake_rating_kW",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_mech_kW",
     "S1.brake_resistor_rating_kW",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_discharge_ceiling_kW",
     "S2.accessory_mech_kW",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_discharge_ceiling_kW",
     "S3.accessory_mech_kW",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_discharge_ceiling_kW",
     "S4.accessory_mech_kW",
     "S4.brake_resistor_rating_kW",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [],
    "electric_side_moves": [
     "S1.pack_charge_ceiling_kW",
     "S2.pack_charge_ceiling_kW",
     "S3.pack_charge_ceiling_kW",
     "S4.pack_charge_ceiling_kW"
    ]
   },
   "hot_alt_2000m_45C": {
    "quantities_that_move": [
     "S0.accessory_bus_kW",
     "S0.accessory_mech_kW",
     "S0.air_density_kg_m3",
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.accessory_bus_kW",
     "S1.accessory_mech_kW",
     "S1.air_density_kg_m3",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S2.accessory_bus_kW",
     "S2.accessory_mech_kW",
     "S2.air_density_kg_m3",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S3.accessory_bus_kW",
     "S3.accessory_mech_kW",
     "S3.air_density_kg_m3",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S4.accessory_bus_kW",
     "S4.accessory_mech_kW",
     "S4.air_density_kg_m3",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW"
    ],
    "quantities_that_do_not": [
     "S0.compression_brake_rating_kW",
     "S1.brake_resistor_rating_kW",
     "S1.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S1.machine_spin_drag_at_20ms_kW",
     "S1.machine_wheel_force_at_10ms_N",
     "S1.pack_charge_ceiling_kW",
     "S1.pack_discharge_ceiling_kW",
     "S2.brake_resistor_rating_kW",
     "S2.compression_brake_rating_kW",
     "S2.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S2.machine_spin_drag_at_20ms_kW",
     "S2.machine_wheel_force_at_10ms_N",
     "S2.pack_charge_ceiling_kW",
     "S2.pack_discharge_ceiling_kW",
     "S3.brake_resistor_rating_kW",
     "S3.compression_brake_rating_kW",
     "S3.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S3.machine_spin_drag_at_20ms_kW",
     "S3.machine_wheel_force_at_10ms_N",
     "S3.pack_charge_ceiling_kW",
     "S3.pack_discharge_ceiling_kW",
     "S4.brake_resistor_rating_kW",
     "S4.machine_eta_bus_to_wheel_at_10ms_200kW",
     "S4.machine_spin_drag_at_20ms_kW",
     "S4.machine_wheel_force_at_10ms_N",
     "S4.pack_charge_ceiling_kW",
     "S4.pack_discharge_ceiling_kW"
    ],
    "engine_side_moves": [
     "S0.engine_full_load_torque_at_1300rpm_Nm",
     "S1.engine_full_load_torque_at_1300rpm_Nm",
     "S1.genset_bus_ceiling_kW",
     "S2.engine_full_load_torque_at_1300rpm_Nm",
     "S2.genset_bus_ceiling_kW",
     "S3.engine_full_load_torque_at_1300rpm_Nm",
     "S4.engine_full_load_torque_at_1300rpm_Nm",
     "S4.genset_bus_ceiling_kW"
    ],
    "electric_side_moves": []
   }
  },
  "R28_corner": {
   "corner": "hot_alt_2000m_45C",
   "derates": [
    "S0.engine_full_load_torque_at_1300rpm_Nm",
    "S1.engine_full_load_torque_at_1300rpm_Nm",
    "S1.genset_bus_ceiling_kW",
    "S2.engine_full_load_torque_at_1300rpm_Nm",
    "S2.genset_bus_ceiling_kW",
    "S3.engine_full_load_torque_at_1300rpm_Nm",
    "S4.engine_full_load_torque_at_1300rpm_Nm",
    "S4.genset_bus_ceiling_kW"
   ],
   "does_not_derate": [],
   "electric_side_unchanged": true,
   "statement": "THE R28 CORNER DERATES THE ENGINE'S FULL-LOAD CURVE AND WHAT IS COMPUTED FROM IT, AND NOTHING ELSE. WS4's `derate_factor` is applied to every engine in the trial (S0's included) and therefore to the R18 continuous rating and the genset ceilings behind it. It is NOT applied to the traction machine, the inverter, the pack's charge or discharge ceiling, the brake resistor, or the compression brake - `ws8_electric.py` has no hot-side model at all and `Pack8.cold_chg_factor_at()` clamps to 1.0 above 15 C. The corner's BENEFIT - about 27% off the aerodynamic bill at 2,000 m - is shared by every candidate; its PENALTY falls only on combustion. Any conclusion drawn from this corner is scoped to that: it says the thin air outweighs an ENGINE derate, not that it outweighs a hot day for the whole vehicle. The cab-cooling load IS charged symmetrically (mechanical and bus-side both rise), which is the one hot-side effect the electric path does pay.",
   "direction_of_error": "a missing hot-side electric derate FLATTERS the electrified candidates at this corner relative to S0; the corner is not binding for any of them, so no verdict depends on it, but WS9 inherits the statement under R28."
  }
 },
 "verdict_stability": {
  "criteria": {
   "nominal_pct": 3.0,
   "every_corner_pct": 0.0,
   "statistic": "ensemble_min",
   "metric": "fleet-mission fuel energy per payload tonne-km",
   "pre_committed": true,
   "precedent": "BASELINE_v3 reads G1 on the ensemble min"
  },
  "ruling": "R25 (BASELINE_v4)",
  "candidates": {
   "S1": {
    "executed_verdict": "KILL",
    "verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "nominal_margin_pct_min": -0.6884959422473613,
    "worst_corner": "cold_minus10C",
    "worst_corner_margin_pct_min": -12.866708553446385,
    "headroom_to_advance_pp": 3.6884959422473615
   },
   "S2": {
    "executed_verdict": "KILL",
    "verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "nominal_margin_pct_min": 0.5911100699440873,
    "worst_corner": "cold_minus10C",
    "worst_corner_margin_pct_min": -9.227055078976527,
    "headroom_to_advance_pp": 2.4088899300559126
   },
   "S3": {
    "executed_verdict": "KILL",
    "verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "nominal_margin_pct_min": -1.085394090482248,
    "worst_corner": "cold_minus10C",
    "worst_corner_margin_pct_min": -14.174316723180722,
    "headroom_to_advance_pp": 4.085394090482248
   },
   "S4": {
    "executed_verdict": "KILL",
    "verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "nominal_margin_pct_min": -3.8418443085956486,
    "worst_corner": "cold_minus10C",
    "worst_corner_margin_pct_min": -17.206366772152812,
    "headroom_to_advance_pp": 6.841844308595649
   }
  },
  "whr_executed": "DROPPED",
  "whr_on_current_numbers": {
   "S1": "DROPPED",
   "S2": "DROPPED",
   "S3": "DROPPED"
  },
  "whr_unchanged": true,
  "r3_stop_condition": {
   "rule": "R3_DIRECTIVE item 1: S3's fuel correction is expected to improve it by several percent and to leave it far below the bar. If S3's NOMINAL ENSEMBLE-MIN crosses +3%, the round STOPS and reports and does not touch the verdict.",
   "S3_nominal_margin_pct_min": -1.085394090482248,
   "bar_pct": 3.0,
   "crossed": false,
   "note": "S3 is dead on CAPABILITY regardless of fuel - no fixed ratio both cruises at 105 km/h and holds the 6% grade at 36,300 kg - so this trip-wire is about the fuel number the record carries, not about the verdict's reason."
  },
  "all_unchanged": true,
  "note": "if `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3, R3_DIRECTIVE item 1). It carries BOTH tests: the four executed verdicts against the pre-committed criteria, and R3_DIRECTIVE's own trip-wire on S3's nominal ensemble-min."
 },
 "one_factor_S1_vs_S2": {
  "rule": "each row reverts EXACTLY ONE correction and leaves the rest applied; margins are the same paired per-seed ensemble as the headline, at the nominal corner. S0 is unaffected by every correction in this set (no errata switch reaches it), so the ruler is the same in every row - which is why a row's DELTA against `r3_as_reported` IS the direction that correction moved that candidate.",
  "direction_convention": "margin = (S0 - candidate)/S0 x 100, so HIGHER IS BETTER. delta = median(r3_as_reported) - median(row); delta > 0 means the correction moved the candidate UP, i.e. it was FOR that candidate; delta < 0 means AGAINST. A candidate whose delta is exactly 0.0 in a row is that correction PROVED not to reach it, not an assertion that it does not.",
  "candidates": [
   "S1",
   "S2",
   "S3",
   "S4"
  ],
  "ordering": {
   "r3_as_reported": "S2 ahead of S1",
   "F4_reverted_credit_removed": "S2 ahead of S1",
   "F6_reverted_peak_point_pricing": "S2 ahead of S1",
   "F3_reverted_engine_dual_use": "S2 ahead of S1",
   "F5_reverted_spin_rule": "S2 ahead of S1",
   "F3_and_F5_reverted": "S2 ahead of S1",
   "B1_reverted_brake_and_fuel": "S2 ahead of S1",
   "R3_S0_launch_fuel_reverted": "S2 ahead of S1"
  },
  "rows": {
   "r3_as_reported": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.5911100699440873,
     "median": 1.8879465349681643,
     "max": 3.2431626584081483
    },
    "S3": {
     "min": -1.085394090482248,
     "median": 1.6381290929839507,
     "max": 3.3483969356008414
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "F4_reverted_credit_removed": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.5124372542877277,
     "median": 1.0674463396108331,
     "max": 2.4487590772876913
    },
    "S3": {
     "min": -1.085394090482248,
     "median": 1.204603366677171,
     "max": 2.3054583653529326
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "F6_reverted_peak_point_pricing": {
    "S1": {
     "min": -0.657719893633907,
     "median": 0.7519881159222673,
     "max": 2.5874414204481546
    },
    "S2": {
     "min": 0.6376970316220224,
     "median": 1.902138626638865,
     "max": 3.25703186935442
    },
    "S3": {
     "min": 1.0435146469455518,
     "median": 3.616540586286643,
     "max": 4.9052591651269655
    },
    "S4": {
     "min": -3.66868823567314,
     "median": -0.9475652060974991,
     "max": 2.0564117615539304
    }
   },
   "F3_reverted_engine_dual_use": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.47237804521747234,
     "median": 1.818079909642472,
     "max": 2.828808191163669
    },
    "S3": {
     "min": -1.085394090482248,
     "median": 1.6381290929839507,
     "max": 3.3483969356008414
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "F5_reverted_spin_rule": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.5367536647610485,
     "median": 1.8358489509231997,
     "max": 3.193330264696421
    },
    "S3": {
     "min": -3.2768280495244295,
     "median": -0.4165658979708481,
     "max": 1.183162579757844
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "F3_and_F5_reverted": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.4135821947921229,
     "median": 1.7745949096748888,
     "max": 2.8001011608492963
    },
    "S3": {
     "min": -3.2768280495244295,
     "median": -0.4165658979708481,
     "max": 1.183162579757844
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "B1_reverted_brake_and_fuel": {
    "S1": {
     "min": -0.6884959422473613,
     "median": 0.7337463427837478,
     "max": 2.569898327809644
    },
    "S2": {
     "min": 0.47789760629832745,
     "median": 1.802813134425556,
     "max": 3.1846841801674484
    },
    "S3": {
     "min": -5.802224908469612,
     "median": -3.6241863286434888,
     "max": 0.9902540648601595
    },
    "S4": {
     "min": -3.8418443085956486,
     "median": -1.059736946707445,
     "max": 1.9783883737854224
    }
   },
   "R3_S0_launch_fuel_reverted": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.5884661617946799,
     "median": 1.8850775769682415,
     "max": 3.240149567049397
    },
    "S3": {
     "min": -1.0880825874306592,
     "median": 1.6352107230716488,
     "max": 3.3453397562805973
    },
    "S4": {
     "min": -3.844606116906859,
     "median": -1.0626174366132541,
     "max": 1.9753358962646956
    }
   }
  }
 },
 "heat_ledger_WS6": {
  "convention": "component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation; compression-brake heat is booked to the EXHAUST and resistor heat to the RESISTOR, because they go to different places in a packaging study; the simulated member is a sustained 60-second mean, not an instantaneous spike, and it is a MEASURED PEAK rather than a balanced operating point. EVERY member now carries a closure residual and every member is asserted (r3, R3_DIRECTIVE item 1): the four analytic cases are scaled on the case's own wheel power, and the simulated member carries the WORST 60-second residual of any run of that candidate in the trial, scaled on the accounted energy input at that window. In r2 the simulated member was exempt, and that exemption is what finding B1 came through. The `brake_resistor_kW` row is what the resistor TOOK, capped at the rating whose mass was charged; retarding power the run commanded that no sink could absorb is a CAPABILITY shortfall and is exported separately as `retard_overcommitment`, never as a cooling load",
  "cases": [
   "cruise_95kmh_flat",
   "climb_6pct",
   "descent_6pct_pack_accepting",
   "descent_6pct_pack_saturated",
   "simulated_worst_run"
  ],
  "components": [
   "engine_coolant_kW",
   "engine_exhaust_kW",
   "generator_rectifier_kW",
   "traction_machine_inverter_kW",
   "driveline_kW",
   "pack_kW",
   "brake_resistor_kW",
   "friction_brake_kW",
   "accessory_kW"
  ],
  "sustained_window_s": 60.0,
  "for_workstream": "WS6 heat ledger (CLAUDE.md rule 7)",
  "ledger_version": "r3",
  "supersedes_ledger_version": "r2",
  "consumer_rule": "R3_DIRECTIVE item 7: WS6 consumes ONLY the r3 ledger. The r2 ledger is superseded, not amended: its `simulated_worst_run` member was exempt from the closure assertion and its largest row - S3's 396.87 kW exhaust - was a state one crankshaft cannot be in (finding B1). A consumer holding a ledger whose `ledger_version` is not 'r3' is holding numbers this workstream has withdrawn.",
  "overrun_exclusivity": {
   "rule": "per run, over every (corner, cycle, seed) in the trial: no 10 Hz sample may carry both compression-brake power > 1 kW and positive engine shaft power > 1 kW. One crankshaft cannot be in both states.",
   "candidates": {
    "S0": {
     "runs_examined": 96,
     "examined_every_run": true,
     "samples_brake_and_shaft": 0,
     "worst_run": null,
     "fuel_fraction_while_braking_max": 0.0,
     "fuel_fraction_while_braking_max_run": null,
     "ttr_charge_while_braking_kWh_total": 0.0,
     "holds": true
    },
    "S1": {
     "runs_examined": 96,
     "examined_every_run": true,
     "samples_brake_and_shaft": 0,
     "worst_run": null,
     "fuel_fraction_while_braking_max": 0.08793441523542732,
     "fuel_fraction_while_braking_max_run": "hot_alt_2000m_45C/REG-165/seed8103",
     "ttr_charge_while_braking_kWh_total": 0.0,
     "holds": true
    },
    "S2": {
     "runs_examined": 96,
     "examined_every_run": true,
     "samples_brake_and_shaft": 0,
     "worst_run": null,
     "fuel_fraction_while_braking_max": 0.023983902770315754,
     "fuel_fraction_while_braking_max_run": "grade_heavy/REG-165/seed8103",
     "ttr_charge_while_braking_kWh_total": 0.0,
     "holds": true
    },
    "S3": {
     "runs_examined": 96,
     "examined_every_run": true,
     "samples_brake_and_shaft": 0,
     "worst_run": null,
     "fuel_fraction_while_braking_max": 0.0,
     "fuel_fraction_while_braking_max_run": null,
     "ttr_charge_while_braking_kWh_total": 0.0,
     "holds": true
    },
    "S4": {
     "runs_examined": 96,
     "examined_every_run": true,
     "samples_brake_and_shaft": 0,
     "worst_run": null,
     "fuel_fraction_while_braking_max": 0.15124065901369046,
     "fuel_fraction_while_braking_max_run": "grade_heavy/REG-165/seed8103",
     "ttr_charge_while_braking_kWh_total": 0.0,
     "holds": true
    }
   },
   "all_hold": true,
   "note": "`fuel_fraction_while_braking` is reported, not gated, and a non-zero value is not by itself a defect. S1 and S4 have no mechanical path from engine to road at all, so a genset charging the pack while the vehicle brakes is simply a legitimate state for them. S2's is legitimate too, on a narrower ground: under its declared coupling law the lockup clutch is open while regen alone is doing the retarding, so the crank is free and the genset may run - and the fraction of the band that covers is exported as `inband_overrun_no_engine_brake_fraction_moving`. What is impossible, and what `samples_brake_and_shaft` counts, is an engine carrying compression-brake power and positive shaft power at the same instant."
  },
  "all_cases_close_and_within_rating": true,
  "what_all_cases_close_and_within_rating_tests": "TRUE requires all three of: (a) every enumerated case closes, INCLUDING the simulated member, which carries the worst 60-second residual of any run of that candidate in the trial - in r2 the simulated member was exempt and that exemption is what finding B1 came through; (b) every component stays inside the rating of the hardware whose mass was charged, which is one HARD row - the brake resistor - the advisory rows being findings rather than gates; (c) no run carries a sample with both compression-brake power and positive engine shaft power.",
  "advisory_exceedances": {
   "S0": [
    {
     "component": "foundation_brakes",
     "rated_kW": 60.0,
     "worst_case_kW": 312.8381728182537,
     "governing_case": "simulated_worst_run"
    }
   ],
   "S1": [
    {
     "component": "foundation_brakes",
     "rated_kW": 60.0,
     "worst_case_kW": 205.16919719822718,
     "governing_case": "simulated_worst_run"
    }
   ],
   "S2": [
    {
     "component": "foundation_brakes",
     "rated_kW": 60.0,
     "worst_case_kW": 65.55340909899944,
     "governing_case": "simulated_worst_run"
    }
   ],
   "S3": [
    {
     "component": "foundation_brakes",
     "rated_kW": 60.0,
     "worst_case_kW": 147.95195002768787,
     "governing_case": "simulated_worst_run"
    }
   ],
   "S4": [
    {
     "component": "foundation_brakes",
     "rated_kW": 60.0,
     "worst_case_kW": 133.6863171466989,
     "governing_case": "simulated_worst_run"
    }
   ]
  },
  "advisory_note": "an ADVISORY exceedance is a declared policy allowance exceeded, not a component rating: it is a finding about the architecture that WS6 needs, not an error in this ledger. S0's foundation brakes are the case that matters - a compression-brake-only tractor snubs repeatedly on a long descent, and the sustained figure is the physical evidence behind ESC-WS8-6.",
  "candidates": {
   "S0": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 69.7105241630927,
      "engine_exhaust_kW": 96.26691432046137,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 7.6702828125852704,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 4.0,
      "_closure_residual_kW": -1.4210854715202004e-14,
      "total_rejected_kW": 177.64772129613934,
      "road_speed_kmh": 95.0,
      "pack_saturated": false
     },
     "climb_6pct": {
      "case_wheel_power_kW": 321.5825451745642,
      "engine_coolant_kW": 207.08960797752772,
      "engine_exhaust_kW": 285.98088720706215,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 29.119826161337528,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 4.0,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 526.1903213459274,
      "road_speed_kmh": 48.48106964927392,
      "pack_saturated": false
     },
     "descent_6pct_pack_accepting": {
      "case_wheel_power_kW": -317.6696812091077,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 303.807764910944,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 13.861916298163692,
      "accessory_kW": 4.0,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 321.6696812091077,
      "road_speed_kmh": 62.18141092125546,
      "pack_saturated": false,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 60.381410921255465,
        "total_rejected_kW": 313.4129743700672
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 63.98141092125547,
        "total_rejected_kW": 329.84117360626476
       },
       "at_case_kW": 321.6696812091077,
       "step_above_case_kW": 8.171492397157067,
       "on_a_step": false
      }
     },
     "descent_6pct_pack_saturated": {
      "case_wheel_power_kW": -317.6696812091077,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 303.807764910944,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 0.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 13.861916298163692,
      "accessory_kW": 4.0,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 321.6696812091077,
      "road_speed_kmh": 62.18141092125546,
      "pack_saturated": true,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 60.381410921255465,
        "total_rejected_kW": 313.4129743700672
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 63.98141092125547,
        "total_rejected_kW": 329.84117360626476
       },
       "at_case_kW": 321.6696812091077,
       "step_above_case_kW": 8.171492397157067,
       "on_a_step": false
      }
     },
     "simulated_worst_run": {
      "engine_coolant_kW": 208.4325933587437,
      "engine_exhaust_kW": 302.26220078784286,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 29.229241864447168,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 312.8381728182537,
      "accessory_kW": 7.000000000000025,
      "total_rejected_kW": 569.2674116972692,
      "engine_coolant_kW_instantaneous_kW": 208.4332765112242,
      "engine_exhaust_kW_instantaneous_kW": 303.68756411852314,
      "generator_rectifier_kW_instantaneous_kW": 0.0,
      "traction_machine_inverter_kW_instantaneous_kW": 0.0,
      "driveline_kW_instantaneous_kW": 66.05456833302034,
      "pack_kW_instantaneous_kW": 0.0,
      "brake_resistor_kW_instantaneous_kW": 0.0,
      "friction_brake_kW_instantaneous_kW": 834.2194780800769,
      "accessory_kW_instantaneous_kW": 7.0000000000000355,
      "engine_coolant_kW_run": "nominal/LH-520/seed8104 @ 85 km/h",
      "engine_exhaust_kW_run": "grade_heavy/REG-165/seed8107 @ 49 km/h",
      "driveline_kW_run": "payload_plus20/LH-520/seed8101 @ 44 km/h",
      "friction_brake_kW_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "accessory_kW_run": "hot_alt_2000m_45C/LH-520/seed8107 @ 103 km/h",
      "total_rejected_kW_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "_governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null,
      "_closure_residual_kW": -9.95399934078556e-05,
      "_closure_scale_kW": 12.095901258087943,
      "_closure_run": "payload_plus20/LH-520/seed8108 @ 90 km/h",
      "_closure_basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1)."
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 69.7105241630927,
       "climb_6pct": 207.08960797752772,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 208.4325933587437
      },
      "value": 208.4325933587437,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8104 @ 85 km/h",
      "simulated_instantaneous_kW": 208.4332765112242,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 96.26691432046137,
       "climb_6pct": 285.98088720706215,
       "descent_6pct_pack_accepting": 303.807764910944,
       "descent_6pct_pack_saturated": 303.807764910944,
       "simulated_worst_run": 302.26220078784286
      },
      "value": 303.807764910944,
      "governing_case": "descent_6pct_pack_accepting",
      "governing_run": null,
      "simulated_instantaneous_kW": 303.68756411852314,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "generator_rectifier_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "governing_run": null,
      "simulated_instantaneous_kW": 0.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "governing_run": null,
      "simulated_instantaneous_kW": 0.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 29.229241864447168
      },
      "value": 29.229241864447168,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8101 @ 44 km/h",
      "simulated_instantaneous_kW": 66.05456833302034,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "governing_run": null,
      "simulated_instantaneous_kW": 0.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "governing_run": null,
      "simulated_instantaneous_kW": 0.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "friction_brake_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 13.861916298163692,
       "descent_6pct_pack_saturated": 13.861916298163692,
       "simulated_worst_run": 312.8381728182537
      },
      "value": 312.8381728182537,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "simulated_instantaneous_kW": 834.2194780800769,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 4.0,
       "climb_6pct": 4.0,
       "descent_6pct_pack_accepting": 4.0,
       "descent_6pct_pack_saturated": 4.0,
       "simulated_worst_run": 7.000000000000025
      },
      "value": 7.000000000000025,
      "governing_case": "simulated_worst_run",
      "governing_run": "hot_alt_2000m_45C/LH-520/seed8107 @ 103 km/h",
      "simulated_instantaneous_kW": 7.0000000000000355,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 177.64772129613934,
       "climb_6pct": 526.1903213459274,
       "descent_6pct_pack_accepting": 321.6696812091077,
       "descent_6pct_pack_saturated": 321.6696812091077,
       "simulated_worst_run": 569.2674116972692
      },
      "value": 569.2674116972692,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "foundation_brakes",
       "kind": "advisory",
       "rated_kW": 60.0,
       "worst_case_kW": 312.8381728182537,
       "governing_case": "simulated_worst_run",
       "governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
       "within_rating": false,
       "note": "`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous GRADE-HOLDING allowance the descent governor is built on, not a brake rating, and the integrator does not cap transient braking with it. A sustained figure above it on a simulated run therefore means repeated snub braking, which is a real thermal duty on the foundation brakes and is exactly what a candidate with a weak retarder does. It is reported, not gated - and for S0 it is the physical evidence behind ESC-WS8-6."
      }
     ],
     "all_within_rating": true,
     "advisory_exceedances": [
      {
       "component": "foundation_brakes",
       "rated_kW": 60.0,
       "worst_case_kW": 312.8381728182537,
       "governing_case": "simulated_worst_run"
      }
     ]
    },
    "closure": {
     "cases": {
      "cruise_95kmh_flat": {
       "residual_kW": -1.4210854715202004e-14,
       "relative": -1.267414347818345e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "simulated_worst_run": {
       "residual_kW": -9.95399934078556e-05,
       "relative": -8.229233298452897e-06,
       "closes": true,
       "basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1).",
       "governing_run": "payload_plus20/LH-520/seed8108 @ 90 km/h"
      }
     },
     "tolerance": 0.02,
     "all_close": true
    }
   },
   "S1": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 71.5169582775221,
      "engine_exhaust_kW": 98.76151381181624,
      "generator_rectifier_kW": 7.28339094245689,
      "traction_machine_inverter_kW": 8.726886428449404,
      "driveline_kW": 3.467776511523695,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -1.4210854715202004e-14,
      "total_rejected_kW": 193.15652597176833,
      "road_speed_kmh": 95.0,
      "pack_saturated": false
     },
     "climb_6pct": {
      "case_wheel_power_kW": 339.2161378353248,
      "engine_coolant_kW": 158.57050434954053,
      "engine_exhaust_kW": 218.9783155303179,
      "generator_rectifier_kW": 16.20163151924345,
      "traction_machine_inverter_kW": 22.333419589126606,
      "driveline_kW": 10.491220757793542,
      "pack_kW": 2.658917297035896,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 432.6340090430579,
      "road_speed_kmh": 51.00345113944995,
      "pack_saturated": false
     },
     "descent_6pct_pack_accepting": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 25.30327882517014,
      "driveline_kW": 14.029137660543142,
      "pack_kW": 6.601106533201006,
      "brake_resistor_kW": 208.2686210923575,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -5.684341886080802e-14,
      "total_rejected_kW": 257.6021441112718,
      "road_speed_kmh": 100.0,
      "pack_saturated": false,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 98.2,
        "total_rejected_kW": 251.70470384799003
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 101.80000000000001,
        "total_rejected_kW": 263.3228851351234
       },
       "at_case_kW": 257.6021441112718,
       "step_above_case_kW": 5.720741023851588,
       "on_a_step": false
      }
     },
     "descent_6pct_pack_saturated": {
      "case_wheel_power_kW": -399.99856712560626,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 17.078672074216797,
      "driveline_kW": 10.199999999999989,
      "pack_kW": 0.0,
      "brake_resistor_kW": 312.7213279257832,
      "friction_brake_kW": 59.99856712560626,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 403.39856712560623,
      "road_speed_kmh": 81.3950140134991,
      "pack_saturated": true,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 79.5950140134991,
        "total_rejected_kW": 396.17882258529727
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 83.19501401349909,
        "total_rejected_kW": 410.5067665821276
       },
       "at_case_kW": 403.39856712560623,
       "step_above_case_kW": 7.10819945652139,
       "on_a_step": false
      }
     },
     "simulated_worst_run": {
      "engine_coolant_kW": 158.57050434954036,
      "engine_exhaust_kW": 218.97831553031833,
      "generator_rectifier_kW": 16.20163151924342,
      "traction_machine_inverter_kW": 31.88972803981339,
      "driveline_kW": 17.40073164341576,
      "pack_kW": 7.7579575232563975,
      "brake_resistor_kW": 340.00000000000034,
      "friction_brake_kW": 205.16919719822718,
      "accessory_kW": 6.600000000000004,
      "total_rejected_kW": 574.9274100108137,
      "engine_coolant_kW_instantaneous_kW": 158.57050434954053,
      "engine_exhaust_kW_instantaneous_kW": 218.9783155303179,
      "generator_rectifier_kW_instantaneous_kW": 16.20163151924345,
      "traction_machine_inverter_kW_instantaneous_kW": 35.53929697404624,
      "driveline_kW_instantaneous_kW": 17.400776408556908,
      "pack_kW_instantaneous_kW": 11.64028958371446,
      "brake_resistor_kW_instantaneous_kW": 340.0,
      "friction_brake_kW_instantaneous_kW": 685.7959647173861,
      "accessory_kW_instantaneous_kW": 6.6,
      "engine_coolant_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "engine_exhaust_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "generator_rectifier_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "driveline_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "pack_kW_run": "grade_heavy/LH-520/seed8108 @ 87 km/h",
      "brake_resistor_kW_run": "nominal/LH-520/seed8101 @ 97 km/h",
      "friction_brake_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "accessory_kW_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h",
      "total_rejected_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "_governing_run": "nominal/LH-520/seed8101 @ 97 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null,
      "_closure_residual_kW": 2.5099922140725544e-14,
      "_closure_scale_kW": 37.86223899087113,
      "_closure_run": "grade_heavy/LH-520/seed8105 @ 104 km/h",
      "_closure_basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1)."
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 71.5169582775221,
       "climb_6pct": 158.57050434954053,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 158.57050434954036
      },
      "value": 158.57050434954053,
      "governing_case": "climb_6pct",
      "governing_run": null,
      "simulated_instantaneous_kW": 158.57050434954053,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 98.76151381181624,
       "climb_6pct": 218.9783155303179,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 218.97831553031833
      },
      "value": 218.97831553031833,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "simulated_instantaneous_kW": 218.9783155303179,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "generator_rectifier_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 7.28339094245689,
       "climb_6pct": 16.20163151924345,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 16.20163151924342
      },
      "value": 16.20163151924345,
      "governing_case": "climb_6pct",
      "governing_run": null,
      "simulated_instantaneous_kW": 16.20163151924345,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 8.726886428449404,
       "climb_6pct": 22.333419589126606,
       "descent_6pct_pack_accepting": 25.30327882517014,
       "descent_6pct_pack_saturated": 17.078672074216797,
       "simulated_worst_run": 31.88972803981339
      },
      "value": 31.88972803981339,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "simulated_instantaneous_kW": 35.53929697404624,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.467776511523695,
       "climb_6pct": 10.491220757793542,
       "descent_6pct_pack_accepting": 14.029137660543142,
       "descent_6pct_pack_saturated": 10.199999999999989,
       "simulated_worst_run": 17.40073164341576
      },
      "value": 17.40073164341576,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "simulated_instantaneous_kW": 17.400776408556908,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 2.658917297035896,
       "descent_6pct_pack_accepting": 6.601106533201006,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 7.7579575232563975
      },
      "value": 7.7579575232563975,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/LH-520/seed8108 @ 87 km/h",
      "simulated_instantaneous_kW": 11.64028958371446,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 208.2686210923575,
       "descent_6pct_pack_saturated": 312.7213279257832,
       "simulated_worst_run": 340.00000000000034
      },
      "value": 340.00000000000034,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 97 km/h",
      "simulated_instantaneous_kW": 340.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "friction_brake_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 59.99856712560626,
       "simulated_worst_run": 205.16919719822718
      },
      "value": 205.16919719822718,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "simulated_instantaneous_kW": 685.7959647173861,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.4,
       "climb_6pct": 3.4,
       "descent_6pct_pack_accepting": 3.4,
       "descent_6pct_pack_saturated": 3.4,
       "simulated_worst_run": 6.600000000000004
      },
      "value": 6.600000000000004,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h",
      "simulated_instantaneous_kW": 6.6,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 193.15652597176833,
       "climb_6pct": 432.6340090430579,
       "descent_6pct_pack_accepting": 257.6021441112718,
       "descent_6pct_pack_saturated": 403.39856712560623,
       "simulated_worst_run": 574.9274100108137
      },
      "value": 574.9274100108137,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 340.0,
       "worst_case_kW": 340.00000000000034,
       "governing_case": "simulated_worst_run",
       "within_rating": true,
       "note": "the resistor's mass was charged at this rating; a worst case above it is a sizing error, not a cooling load"
      },
      {
       "component": "foundation_brakes",
       "kind": "advisory",
       "rated_kW": 60.0,
       "worst_case_kW": 205.16919719822718,
       "governing_case": "simulated_worst_run",
       "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
       "within_rating": false,
       "note": "`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous GRADE-HOLDING allowance the descent governor is built on, not a brake rating, and the integrator does not cap transient braking with it. A sustained figure above it on a simulated run therefore means repeated snub braking, which is a real thermal duty on the foundation brakes and is exactly what a candidate with a weak retarder does. It is reported, not gated - and for S0 it is the physical evidence behind ESC-WS8-6."
      },
      {
       "component": "genset_electrical",
       "kind": "advisory",
       "rated_kW": 289.4691189114179,
       "worst_case_kW": 16.20163151924345,
       "governing_case": "climb_6pct",
       "within_rating": true,
       "note": "loss row, not an output; the rating is shown for context only"
      }
     ],
     "all_within_rating": true,
     "advisory_exceedances": [
      {
       "component": "foundation_brakes",
       "rated_kW": 60.0,
       "worst_case_kW": 205.16919719822718,
       "governing_case": "simulated_worst_run"
      }
     ]
    },
    "closure": {
     "cases": {
      "cruise_95kmh_flat": {
       "residual_kW": -1.4210854715202004e-14,
       "relative": -1.267414347818345e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "simulated_worst_run": {
       "residual_kW": 2.5099922140725544e-14,
       "relative": 6.629275713667468e-16,
       "closes": true,
       "basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1).",
       "governing_run": "grade_heavy/LH-520/seed8105 @ 104 km/h"
      }
     },
     "tolerance": 0.02,
     "all_close": true
    }
   },
   "S2": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 71.5169582775221,
      "engine_exhaust_kW": 98.76151381181624,
      "generator_rectifier_kW": 7.28339094245689,
      "traction_machine_inverter_kW": 8.726886428449404,
      "driveline_kW": 3.467776511523695,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -1.4210854715202004e-14,
      "total_rejected_kW": 193.15652597176833,
      "road_speed_kmh": 95.0,
      "pack_saturated": false
     },
     "climb_6pct": {
      "case_wheel_power_kW": 339.2161378353248,
      "engine_coolant_kW": 158.57050434954053,
      "engine_exhaust_kW": 218.9783155303179,
      "generator_rectifier_kW": 16.20163151924345,
      "traction_machine_inverter_kW": 22.333419589126606,
      "driveline_kW": 10.491220757793542,
      "pack_kW": 2.658917297035896,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 432.6340090430579,
      "road_speed_kmh": 51.00345113944995,
      "pack_saturated": false
     },
     "descent_6pct_pack_accepting": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 190.48067792268114,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 20.3573222087702,
      "driveline_kW": 8.314717322862705,
      "pack_kW": 6.601106533201006,
      "brake_resistor_kW": 28.448320123756744,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -5.684341886080802e-14,
      "total_rejected_kW": 257.6021441112718,
      "road_speed_kmh": 100.0,
      "pack_saturated": false,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 98.2,
        "total_rejected_kW": 251.70470384799003
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 101.80000000000001,
        "total_rejected_kW": 263.3228851351234
       },
       "at_case_kW": 257.6021441112718,
       "step_above_case_kW": 5.720741023851588,
       "on_a_step": false
      }
     },
     "descent_6pct_pack_saturated": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 190.48067792268114,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 13.659822986065336,
      "driveline_kW": 8.314717322862691,
      "pack_kW": 0.0,
      "brake_resistor_kW": 255.18270378649495,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 471.0379220181041,
      "road_speed_kmh": 100.0,
      "pack_saturated": true,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 98.2,
        "total_rejected_kW": 465.09013835542027
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 101.80000000000001,
        "total_rejected_kW": 476.8486640141213
       },
       "at_case_kW": 471.0379220181041,
       "step_above_case_kW": 5.810741996017214,
       "on_a_step": false
      }
     },
     "simulated_worst_run": {
      "engine_coolant_kW": 196.46232260565236,
      "engine_exhaust_kW": 271.30511216971047,
      "generator_rectifier_kW": 16.20163151924342,
      "traction_machine_inverter_kW": 31.889715716892184,
      "driveline_kW": 25.120679912470102,
      "pack_kW": 10.18279675268955,
      "brake_resistor_kW": 316.69292730695145,
      "friction_brake_kW": 65.55340909899944,
      "accessory_kW": 7.000000000000011,
      "total_rejected_kW": 552.7138670820167,
      "engine_coolant_kW_instantaneous_kW": 196.4623226056522,
      "engine_exhaust_kW_instantaneous_kW": 271.3051121697102,
      "generator_rectifier_kW_instantaneous_kW": 16.20163151924345,
      "traction_machine_inverter_kW_instantaneous_kW": 35.55075775289612,
      "driveline_kW_instantaneous_kW": 25.158282564426987,
      "pack_kW_instantaneous_kW": 11.636532433820626,
      "brake_resistor_kW_instantaneous_kW": 340.0,
      "friction_brake_kW_instantaneous_kW": 637.0873901566545,
      "accessory_kW_instantaneous_kW": 7.000000000000001,
      "engine_coolant_kW_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "engine_exhaust_kW_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "generator_rectifier_kW_run": "nominal/LH-520/seed8101 @ 51 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "driveline_kW_run": "payload_plus20/LH-520/seed8102 @ 107 km/h",
      "pack_kW_run": "grade_heavy/REG-165/seed8101 @ 53 km/h",
      "brake_resistor_kW_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "friction_brake_kW_run": "cold_minus10C/REG-165/seed8106 @ 97 km/h",
      "accessory_kW_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 80 km/h",
      "total_rejected_kW_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "_governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null,
      "_closure_residual_kW": -3.1823827289182797e-06,
      "_closure_scale_kW": 524.8737223399617,
      "_closure_run": "payload_minus20/LH-520/seed8103 @ 86 km/h",
      "_closure_basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1)."
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 71.5169582775221,
       "climb_6pct": 158.57050434954053,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 196.46232260565236
      },
      "value": 196.46232260565236,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "simulated_instantaneous_kW": 196.4623226056522,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 98.76151381181624,
       "climb_6pct": 218.9783155303179,
       "descent_6pct_pack_accepting": 190.48067792268114,
       "descent_6pct_pack_saturated": 190.48067792268114,
       "simulated_worst_run": 271.30511216971047
      },
      "value": 271.30511216971047,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "simulated_instantaneous_kW": 271.3051121697102,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "generator_rectifier_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 7.28339094245689,
       "climb_6pct": 16.20163151924345,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 16.20163151924342
      },
      "value": 16.20163151924345,
      "governing_case": "climb_6pct",
      "governing_run": null,
      "simulated_instantaneous_kW": 16.20163151924345,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 8.726886428449404,
       "climb_6pct": 22.333419589126606,
       "descent_6pct_pack_accepting": 20.3573222087702,
       "descent_6pct_pack_saturated": 13.659822986065336,
       "simulated_worst_run": 31.889715716892184
      },
      "value": 31.889715716892184,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "simulated_instantaneous_kW": 35.55075775289612,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.467776511523695,
       "climb_6pct": 10.491220757793542,
       "descent_6pct_pack_accepting": 8.314717322862705,
       "descent_6pct_pack_saturated": 8.314717322862691,
       "simulated_worst_run": 25.120679912470102
      },
      "value": 25.120679912470102,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 107 km/h",
      "simulated_instantaneous_kW": 25.158282564426987,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 2.658917297035896,
       "descent_6pct_pack_accepting": 6.601106533201006,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 10.18279675268955
      },
      "value": 10.18279675268955,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8101 @ 53 km/h",
      "simulated_instantaneous_kW": 11.636532433820626,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 28.448320123756744,
       "descent_6pct_pack_saturated": 255.18270378649495,
       "simulated_worst_run": 316.69292730695145
      },
      "value": 316.69292730695145,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "simulated_instantaneous_kW": 340.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "friction_brake_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 65.55340909899944
      },
      "value": 65.55340909899944,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/REG-165/seed8106 @ 97 km/h",
      "simulated_instantaneous_kW": 637.0873901566545,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.4,
       "climb_6pct": 3.4,
       "descent_6pct_pack_accepting": 3.4,
       "descent_6pct_pack_saturated": 3.4,
       "simulated_worst_run": 7.000000000000011
      },
      "value": 7.000000000000011,
      "governing_case": "simulated_worst_run",
      "governing_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 80 km/h",
      "simulated_instantaneous_kW": 7.000000000000001,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 193.15652597176833,
       "climb_6pct": 432.6340090430579,
       "descent_6pct_pack_accepting": 257.6021441112718,
       "descent_6pct_pack_saturated": 471.0379220181041,
       "simulated_worst_run": 552.7138670820167
      },
      "value": 552.7138670820167,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 340.0,
       "worst_case_kW": 316.69292730695145,
       "governing_case": "simulated_worst_run",
       "within_rating": true,
       "note": "the resistor's mass was charged at this rating; a worst case above it is a sizing error, not a cooling load"
      },
      {
       "component": "foundation_brakes",
       "kind": "advisory",
       "rated_kW": 60.0,
       "worst_case_kW": 65.55340909899944,
       "governing_case": "simulated_worst_run",
       "governing_run": "cold_minus10C/REG-165/seed8106 @ 97 km/h",
       "within_rating": false,
       "note": "`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous GRADE-HOLDING allowance the descent governor is built on, not a brake rating, and the integrator does not cap transient braking with it. A sustained figure above it on a simulated run therefore means repeated snub braking, which is a real thermal duty on the foundation brakes and is exactly what a candidate with a weak retarder does. It is reported, not gated - and for S0 it is the physical evidence behind ESC-WS8-6."
      },
      {
       "component": "genset_electrical",
       "kind": "advisory",
       "rated_kW": 289.4691189114179,
       "worst_case_kW": 16.20163151924345,
       "governing_case": "climb_6pct",
       "within_rating": true,
       "note": "loss row, not an output; the rating is shown for context only"
      }
     ],
     "all_within_rating": true,
     "advisory_exceedances": [
      {
       "component": "foundation_brakes",
       "rated_kW": 60.0,
       "worst_case_kW": 65.55340909899944,
       "governing_case": "simulated_worst_run"
      }
     ]
    },
    "closure": {
     "cases": {
      "cruise_95kmh_flat": {
       "residual_kW": -1.4210854715202004e-14,
       "relative": -1.267414347818345e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "simulated_worst_run": {
       "residual_kW": -3.1823827289182797e-06,
       "relative": -6.063139748606131e-09,
       "closes": true,
       "basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1).",
       "governing_run": "payload_minus20/LH-520/seed8103 @ 86 km/h"
      }
     },
     "tolerance": 0.02,
     "all_close": true
    }
   },
   "S3": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 73.74833103432698,
      "engine_exhaust_kW": 101.84293333311822,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 0.0,
      "driveline_kW": 5.817781936010249,
      "pack_kW": 0.10515463917525811,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 1.4210854715202004e-14,
      "total_rejected_kW": 184.9142009426307,
      "road_speed_kmh": 95.0,
      "pack_saturated": false
     },
     "climb_6pct": {
      "case_wheel_power_kW": 67.1058365767461,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 12.996836324127074,
      "driveline_kW": 2.0754382446416315,
      "pack_kW": 2.6467457055313957,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 21.1190202743001,
      "road_speed_kmh": 10.363776615838328,
      "pack_saturated": false
     },
     "descent_6pct_pack_accepting": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 206.14354533807398,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 20.255955053940866,
      "driveline_kW": 7.844831300400923,
      "pack_kW": 6.601106533201006,
      "brake_resistor_kW": 13.356705885655021,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -5.684341886080802e-14,
      "total_rejected_kW": 257.6021441112718,
      "road_speed_kmh": 100.0,
      "pack_saturated": false,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 98.2,
        "total_rejected_kW": 251.70470384799003
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 101.80000000000001,
        "total_rejected_kW": 263.3228851351234
       },
       "at_case_kW": 257.6021441112718,
       "step_above_case_kW": 5.720741023851588,
       "on_a_step": false
      }
     },
     "descent_6pct_pack_saturated": {
      "case_wheel_power_kW": -463.63910604783473,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 203.63955824659462,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 11.651821236771013,
      "driveline_kW": 6.0,
      "pack_kW": 0.0,
      "brake_resistor_kW": 182.348178763229,
      "friction_brake_kW": 59.99954780124011,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 467.0391060478347,
      "road_speed_kmh": 98.78531870237664,
      "pack_saturated": true,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 96.98531870237665,
        "total_rejected_kW": 461.0002374957811
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 100.58531870237664,
        "total_rejected_kW": 472.94259755271685
       },
       "at_case_kW": 467.0391060478347,
       "step_above_case_kW": 5.90349150488214,
       "on_a_step": false
      }
     },
     "simulated_worst_run": {
      "engine_coolant_kW": 162.57714233960758,
      "engine_exhaust_kW": 224.51129180231555,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 24.395114824094073,
      "driveline_kW": 15.515656550929226,
      "pack_kW": 6.5078318415715035,
      "brake_resistor_kW": 199.99999999999986,
      "friction_brake_kW": 147.95195002768787,
      "accessory_kW": 6.600000000000004,
      "total_rejected_kW": 564.2292606279833,
      "engine_coolant_kW_instantaneous_kW": 162.5771646930856,
      "engine_exhaust_kW_instantaneous_kW": 224.51132267140395,
      "generator_rectifier_kW_instantaneous_kW": 0.0,
      "traction_machine_inverter_kW_instantaneous_kW": 31.178415323210885,
      "driveline_kW_instantaneous_kW": 15.515838707028818,
      "pack_kW_instantaneous_kW": 8.409074962973502,
      "brake_resistor_kW_instantaneous_kW": 200.0,
      "friction_brake_kW_instantaneous_kW": 671.7766359742553,
      "accessory_kW_instantaneous_kW": 6.6,
      "engine_coolant_kW_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "engine_exhaust_kW_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 5 km/h",
      "driveline_kW_run": "nominal/LH-520/seed8107 @ 88 km/h",
      "pack_kW_run": "payload_plus20/LH-520/seed8102 @ 107 km/h",
      "brake_resistor_kW_run": "nominal/LH-520/seed8103 @ 89 km/h",
      "friction_brake_kW_run": "grade_heavy/REG-165/seed8105 @ 101 km/h",
      "accessory_kW_run": "cold_minus10C/LH-520/seed8101 @ 33 km/h",
      "total_rejected_kW_run": "grade_heavy/REG-165/seed8105 @ 101 km/h",
      "_governing_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null,
      "_closure_residual_kW": -0.0005453675975739452,
      "_closure_scale_kW": 58.87448662653715,
      "_closure_run": "cold_minus10C/LH-520/seed8108 @ 90 km/h",
      "_closure_basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1)."
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 73.74833103432698,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 162.57714233960758
      },
      "value": 162.57714233960758,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "simulated_instantaneous_kW": 162.5771646930856,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 101.84293333311822,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 206.14354533807398,
       "descent_6pct_pack_saturated": 203.63955824659462,
       "simulated_worst_run": 224.51129180231555
      },
      "value": 224.51129180231555,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "simulated_instantaneous_kW": 224.51132267140395,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "generator_rectifier_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 0.0
      },
      "value": 0.0,
      "governing_case": "cruise_95kmh_flat",
      "governing_run": null,
      "simulated_instantaneous_kW": 0.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 12.996836324127074,
       "descent_6pct_pack_accepting": 20.255955053940866,
       "descent_6pct_pack_saturated": 11.651821236771013,
       "simulated_worst_run": 24.395114824094073
      },
      "value": 24.395114824094073,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8106 @ 5 km/h",
      "simulated_instantaneous_kW": 31.178415323210885,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 5.817781936010249,
       "climb_6pct": 2.0754382446416315,
       "descent_6pct_pack_accepting": 7.844831300400923,
       "descent_6pct_pack_saturated": 6.0,
       "simulated_worst_run": 15.515656550929226
      },
      "value": 15.515656550929226,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8107 @ 88 km/h",
      "simulated_instantaneous_kW": 15.515838707028818,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.10515463917525811,
       "climb_6pct": 2.6467457055313957,
       "descent_6pct_pack_accepting": 6.601106533201006,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 6.5078318415715035
      },
      "value": 6.601106533201006,
      "governing_case": "descent_6pct_pack_accepting",
      "governing_run": null,
      "simulated_instantaneous_kW": 8.409074962973502,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 13.356705885655021,
       "descent_6pct_pack_saturated": 182.348178763229,
       "simulated_worst_run": 199.99999999999986
      },
      "value": 199.99999999999986,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8103 @ 89 km/h",
      "simulated_instantaneous_kW": 200.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "friction_brake_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 59.99954780124011,
       "simulated_worst_run": 147.95195002768787
      },
      "value": 147.95195002768787,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 101 km/h",
      "simulated_instantaneous_kW": 671.7766359742553,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.4,
       "climb_6pct": 3.4,
       "descent_6pct_pack_accepting": 3.4,
       "descent_6pct_pack_saturated": 3.4,
       "simulated_worst_run": 6.600000000000004
      },
      "value": 6.600000000000004,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 33 km/h",
      "simulated_instantaneous_kW": 6.6,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 184.9142009426307,
       "climb_6pct": 21.1190202743001,
       "descent_6pct_pack_accepting": 257.6021441112718,
       "descent_6pct_pack_saturated": 467.0391060478347,
       "simulated_worst_run": 564.2292606279833
      },
      "value": 564.2292606279833,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 101 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 200.0,
       "worst_case_kW": 199.99999999999986,
       "governing_case": "simulated_worst_run",
       "within_rating": true,
       "note": "the resistor's mass was charged at this rating; a worst case above it is a sizing error, not a cooling load"
      },
      {
       "component": "foundation_brakes",
       "kind": "advisory",
       "rated_kW": 60.0,
       "worst_case_kW": 147.95195002768787,
       "governing_case": "simulated_worst_run",
       "governing_run": "grade_heavy/REG-165/seed8105 @ 101 km/h",
       "within_rating": false,
       "note": "`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous GRADE-HOLDING allowance the descent governor is built on, not a brake rating, and the integrator does not cap transient braking with it. A sustained figure above it on a simulated run therefore means repeated snub braking, which is a real thermal duty on the foundation brakes and is exactly what a candidate with a weak retarder does. It is reported, not gated - and for S0 it is the physical evidence behind ESC-WS8-6."
      }
     ],
     "all_within_rating": true,
     "advisory_exceedances": [
      {
       "component": "foundation_brakes",
       "rated_kW": 60.0,
       "worst_case_kW": 147.95195002768787,
       "governing_case": "simulated_worst_run"
      }
     ]
    },
    "closure": {
     "cases": {
      "cruise_95kmh_flat": {
       "residual_kW": 1.4210854715202004e-14,
       "relative": 1.267414347818345e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "simulated_worst_run": {
       "residual_kW": -0.0005453675975739452,
       "relative": -9.263224680555017e-06,
       "closes": true,
       "basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1).",
       "governing_run": "cold_minus10C/LH-520/seed8108 @ 90 km/h"
      }
     },
     "tolerance": 0.02,
     "all_close": true
    }
   },
   "S4": {
    "cases": {
     "cruise_95kmh_flat": {
      "case_wheel_power_kW": 112.12477387259945,
      "engine_coolant_kW": 75.64238219508125,
      "engine_exhaust_kW": 104.45852779320745,
      "generator_rectifier_kW": 7.340991641487932,
      "traction_machine_inverter_kW": 8.726886428449404,
      "driveline_kW": 3.467776511523695,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -1.4210854715202004e-14,
      "total_rejected_kW": 203.03656456974974,
      "road_speed_kmh": 95.0,
      "pack_saturated": false
     },
     "climb_6pct": {
      "case_wheel_power_kW": 362.8436983185366,
      "engine_coolant_kW": 115.74589034316658,
      "engine_exhaust_kW": 159.8395628548491,
      "generator_rectifier_kW": 9.00150167419477,
      "traction_machine_inverter_kW": 23.36160096803701,
      "driveline_kW": 11.22197005108876,
      "pack_kW": 6.670741272770168,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": -5.684341886080802e-14,
      "total_rejected_kW": 329.2412671641064,
      "road_speed_kmh": 54.35272739270651,
      "pack_saturated": false
     },
     "descent_6pct_pack_accepting": {
      "case_wheel_power_kW": -467.6379220181041,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 20.699559626848952,
      "driveline_kW": 14.029137660543142,
      "pack_kW": 12.987276741921372,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 0.0,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 51.11597402931346,
      "road_speed_kmh": 100.0,
      "pack_saturated": false,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 98.2,
        "total_rejected_kW": 50.539040831318154
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 101.80000000000001,
        "total_rejected_kW": 51.69633251724298
       },
       "at_case_kW": 51.11597402931346,
       "step_above_case_kW": 0.5803584879295158,
       "on_a_step": false
      }
     },
     "descent_6pct_pack_saturated": {
      "case_wheel_power_kW": -399.99856712560626,
      "engine_coolant_kW": 0.0,
      "engine_exhaust_kW": 0.0,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 17.078672074216797,
      "driveline_kW": 10.199999999999989,
      "pack_kW": 0.0,
      "brake_resistor_kW": 312.7213279257832,
      "friction_brake_kW": 59.99856712560626,
      "accessory_kW": 3.4,
      "_closure_residual_kW": 0.0,
      "total_rejected_kW": 403.39856712560623,
      "road_speed_kmh": 81.3950140134991,
      "pack_saturated": true,
      "speed_step_sensitivity": {
       "minus_0p5_ms": {
        "road_speed_kmh": 79.5950140134991,
        "total_rejected_kW": 396.17882258529727
       },
       "plus_0p5_ms": {
        "road_speed_kmh": 83.19501401349909,
        "total_rejected_kW": 410.5067665821276
       },
       "at_case_kW": 403.39856712560623,
       "step_above_case_kW": 7.10819945652139,
       "on_a_step": false
      }
     },
     "simulated_worst_run": {
      "engine_coolant_kW": 115.74589034316668,
      "engine_exhaust_kW": 159.8395628548493,
      "generator_rectifier_kW": 9.001501674194786,
      "traction_machine_inverter_kW": 36.68785466890659,
      "driveline_kW": 19.34623103031585,
      "pack_kW": 17.573499223461614,
      "brake_resistor_kW": 314.5062638995942,
      "friction_brake_kW": 133.6863171466989,
      "accessory_kW": 6.600000000000004,
      "total_rejected_kW": 461.09101710219886,
      "engine_coolant_kW_instantaneous_kW": 115.74589034316658,
      "engine_exhaust_kW_instantaneous_kW": 159.8395628548491,
      "generator_rectifier_kW_instantaneous_kW": 9.00150167419477,
      "traction_machine_inverter_kW_instantaneous_kW": 41.47592754530046,
      "driveline_kW_instantaneous_kW": 19.67891109592921,
      "pack_kW_instantaneous_kW": 18.010560000000016,
      "brake_resistor_kW_instantaneous_kW": 340.0,
      "friction_brake_kW_instantaneous_kW": 703.060128157147,
      "accessory_kW_instantaneous_kW": 6.6,
      "engine_coolant_kW_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "engine_exhaust_kW_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "generator_rectifier_kW_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "driveline_kW_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "pack_kW_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "brake_resistor_kW_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h",
      "friction_brake_kW_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "accessory_kW_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h",
      "total_rejected_kW_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h",
      "_governing_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null,
      "_closure_residual_kW": -5.706842406046539e-14,
      "_closure_scale_kW": 72.00977003637789,
      "_closure_run": "grade_heavy/REG-165/seed8106 @ 93 km/h",
      "_closure_basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1)."
     }
    },
    "worst_case": {
     "engine_coolant_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 75.64238219508125,
       "climb_6pct": 115.74589034316658,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 115.74589034316668
      },
      "value": 115.74589034316668,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "simulated_instantaneous_kW": 115.74589034316658,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 104.45852779320745,
       "climb_6pct": 159.8395628548491,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 159.8395628548493
      },
      "value": 159.8395628548493,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "simulated_instantaneous_kW": 159.8395628548491,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "generator_rectifier_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 7.340991641487932,
       "climb_6pct": 9.00150167419477,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 9.001501674194786
      },
      "value": 9.001501674194786,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h",
      "simulated_instantaneous_kW": 9.00150167419477,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "traction_machine_inverter_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 8.726886428449404,
       "climb_6pct": 23.36160096803701,
       "descent_6pct_pack_accepting": 20.699559626848952,
       "descent_6pct_pack_saturated": 17.078672074216797,
       "simulated_worst_run": 36.68785466890659
      },
      "value": 36.68785466890659,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "simulated_instantaneous_kW": 41.47592754530046,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.467776511523695,
       "climb_6pct": 11.22197005108876,
       "descent_6pct_pack_accepting": 14.029137660543142,
       "descent_6pct_pack_saturated": 10.199999999999989,
       "simulated_worst_run": 19.34623103031585
      },
      "value": 19.34623103031585,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "simulated_instantaneous_kW": 19.67891109592921,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 6.670741272770168,
       "descent_6pct_pack_accepting": 12.987276741921372,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 17.573499223461614
      },
      "value": 17.573499223461614,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "simulated_instantaneous_kW": 18.010560000000016,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 312.7213279257832,
       "simulated_worst_run": 314.5062638995942
      },
      "value": 314.5062638995942,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h",
      "simulated_instantaneous_kW": 340.0,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "friction_brake_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 59.99856712560626,
       "simulated_worst_run": 133.6863171466989
      },
      "value": 133.6863171466989,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "simulated_instantaneous_kW": 703.060128157147,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 3.4,
       "climb_6pct": 3.4,
       "descent_6pct_pack_accepting": 3.4,
       "descent_6pct_pack_saturated": 3.4,
       "simulated_worst_run": 6.600000000000004
      },
      "value": 6.600000000000004,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h",
      "simulated_instantaneous_kW": 6.6,
      "instantaneous_note": "the exported `value` is a SUSTAINED 60-second mean, which is what sizes a cooling package; `simulated_instantaneous_kW` is the largest single 10 Hz sample of the same component anywhere in the trial. A large gap is a snub, not a cooling load."
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 203.03656456974974,
       "climb_6pct": 329.2412671641064,
       "descent_6pct_pack_accepting": 51.11597402931346,
       "descent_6pct_pack_saturated": 403.39856712560623,
       "simulated_worst_run": 461.09101710219886
      },
      "value": 461.09101710219886,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 340.0,
       "worst_case_kW": 314.5062638995942,
       "governing_case": "simulated_worst_run",
       "within_rating": true,
       "note": "the resistor's mass was charged at this rating; a worst case above it is a sizing error, not a cooling load"
      },
      {
       "component": "foundation_brakes",
       "kind": "advisory",
       "rated_kW": 60.0,
       "worst_case_kW": 133.6863171466989,
       "governing_case": "simulated_worst_run",
       "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
       "within_rating": false,
       "note": "`FRICTION_BRAKE_CONT_ALLOWANCE_KW` is the continuous GRADE-HOLDING allowance the descent governor is built on, not a brake rating, and the integrator does not cap transient braking with it. A sustained figure above it on a simulated run therefore means repeated snub braking, which is a real thermal duty on the foundation brakes and is exactly what a candidate with a weak retarder does. It is reported, not gated - and for S0 it is the physical evidence behind ESC-WS8-6."
      },
      {
       "component": "genset_electrical",
       "kind": "advisory",
       "rated_kW": 185.13996818476105,
       "worst_case_kW": 9.001501674194786,
       "governing_case": "simulated_worst_run",
       "within_rating": true,
       "note": "loss row, not an output; the rating is shown for context only"
      }
     ],
     "all_within_rating": true,
     "advisory_exceedances": [
      {
       "component": "foundation_brakes",
       "rated_kW": 60.0,
       "worst_case_kW": 133.6863171466989,
       "governing_case": "simulated_worst_run"
      }
     ]
    },
    "closure": {
     "cases": {
      "cruise_95kmh_flat": {
       "residual_kW": -1.4210854715202004e-14,
       "relative": -1.267414347818345e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "climb_6pct": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.5666089592909447e-16,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true,
       "basis": "analytic operating point; scale = case wheel power",
       "governing_run": null
      },
      "simulated_worst_run": {
       "residual_kW": -5.706842406046539e-14,
       "relative": -7.925094613083137e-16,
       "closes": true,
       "basis": "WORST 60-second window of ANY run of this candidate in the trial; scale = accounted energy input at that window. Per run, not per exported case (R3_DIRECTIVE item 1).",
       "governing_run": "grade_heavy/REG-165/seed8106 @ 93 km/h"
      }
     },
     "tolerance": 0.02,
     "all_close": true
    }
   }
  }
 },
 "escalations": [
  "ESC-WS8-1",
  "ESC-WS8-10",
  "ESC-WS8-2",
  "ESC-WS8-3",
  "ESC-WS8-4",
  "ESC-WS8-5",
  "ESC-WS8-6",
  "ESC-WS8-7",
  "ESC-WS8-8",
  "ESC-WS8-9"
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
- **WS3** cell definitions, pack overhead model (1.55 x cell + 35 kg) and cold charge-acceptance figures - the last of these APPLIED since r2 at the -10 C corner (30.5 kW against 240.0 kW warm), where in r1 it was listed here and never called (finding F2)
- **WS4** `WillansEngine`, `PMGenerator`, `derate_factor` and the R12 chain conventions; `WS2TractionChain` as the ruled map loader. `derate_factor` is APPLIED since r2 at the added 2,000 m / +45 C corner (R28), where it returns 0.9312 and shrinks every engine's full-load curve and therefore every R18 continuous rating; in r1 it was imported, re-exported and never called (finding F11)

**Every inherited object listed above is now exercised by the pipeline.** That is the point of the two corrections just named: a provenance list is a claim about what the numbers were built from, and an inert entry in it is a false claim.

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

CLAUDE.md rule 1 requires that re-running the pipeline reproduces every committed artifact byte-identically. Checked in two independent halves, because the pipeline has two independent sources of possible drift: the simulation, and the derived blocks built on top of it. The check cannot run inside the process it is checking - it compares two independent runs - so it is performed by `check_determinism_ws8.py` and its result committed alongside the run it certifies. In r1 and r2 this record was assembled by hand; in r3 it is generated, because a hand-written claim about reproducibility is the weakest link in the chain it attests to.

**Half 1 - the simulation.** the full 8-seed nominal corner, the WHR gate and the one-factor re-runs re-simulated FROM SCRATCH in a separate copy of the folder, a separate process and a separate worker pool at a different width (run_ws8.py --only-nominal --jobs 4, against the committed run's --jobs 5), with the sibling workstreams and baselines SYMLINKED so the copy reads the same bytes and writes nothing outside its own scratch directory; then each block compared by sha256 of its canonical JSON. Result: trial slice **byte-identical** (sha256 `5b16957caeb3a7f4...`); cycle ensemble identical; S0 calibration identical.

Wall-clock fields are excluded from the comparison and from the committed artifact alike: per-candidate and total runtimes are the only values in this structure that cannot reproduce, and _strip_runtimes removes them before the record is written.

**Half 2 - the derived blocks.** `run_ws8.py --from-checkpoint` rebuilds every block that sits on top of the simulation. It is run TWICE over the committed checkpoint and the two sets of outputs are compared byte-for-byte against each other and against the artifacts already on disk - which tests both that the derived blocks are a deterministic function of the checkpoint and that they do not depend on whether they were built inside the simulating process or rebuilt afterwards. Because THIS FILE is an input to those blocks, the comparison is repeated after it is written and the script exits non-zero if the repeat disagrees; the booleans below therefore describe the committed artifacts and not a state that preceded them.. Result: `results_ws8.json` **byte-identical**, and all 10 CSV exports byte-identical.

**Not checked:** the five sensitivity corners were not re-simulated from scratch - they are the same code path as the nominal corner with different Ctx constants, and re-running them would have cost several more hours of compute for no additional class of evidence. The WHR gate and the one-factor re-runs, which r2 also left unchecked, ARE re-simulated in r3's half 1. Stated rather than implied.

## 15. r3 changelog - what moved, and which way

This round executed `R3_DIRECTIVE.md` against `FINDINGS_WS8_r2.md`. The verdicts were **not** reopened: R25 executed all four kills and the WHR drop on the pre-committed criteria, and the directive's instruction was to make the numbers of record correct, to STOP and report if any verdict flipped, and to STOP if S3's nominal ensemble-min crossed the +3% bar. Neither happened.

### 15.1 Which direction each candidate moved

Against r2's numbers of record as quoted in R35 (BASELINE_v5) and `CHANGELOG_WS8_r2.md`:

| candidate | nominal min, r2 -> r3 | nominal median, r2 -> r3 | worst corner, r2 -> r3 | direction | verdict |
|---|---|---|---|---|---|
| **S1** | -0.69% -> -0.69% | +0.73% -> +0.73% (+0.00 pp) | -12.87% -> -12.87% (+0.00 pp, at `cold_minus10C`) | **UNMOVED** on the nominal median | **KILL** |
| **S2** | +0.48% -> +0.59% | +1.80% -> +1.89% (+0.09 pp) | -9.62% -> -9.23% (+0.39 pp, at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S3** | -7.65% -> -1.09% | -5.26% -> +1.64% (+6.90 pp) | -21.98% -> -14.17% (+7.81 pp, at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S4** | -3.84% -> -3.84% | -1.06% -> -1.06% (+0.00 pp) | -17.21% -> -17.21% (+0.00 pp, at `cold_minus10C`) | **UNMOVED** on the nominal median | **KILL** |

**Almost all of that movement is one correction, and it is measured rather than inferred.** The one-factor row `B1_reverted_brake_and_fuel` in section 4.4 reverts R3's control rule and nothing else: FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical). Everything r3 changed besides that rule is an ACCOUNTING correction - the run closure and the ledger rows it found. Only one of those moves a margin at all, because it moves THE RULER, and it too is measured rather than called small: FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp). Every other r3 correction is a heat row, and no margin reads the heat ledger - which is why S1 and S4 come back at r2's numbers to the precision this table is quoted to.

**A consequence worth stating in the changelog rather than only in the escalations.** With the rule applied, S3 takes 0.000 kWh of through-the-road charge over the whole trial, on 0 of 96 runs, and the 0.72-of-capacity BSFC policy withheld 0.000 kWh of it. Half of S3's declared energy policy is inert, for a reason that is a modelling artefact rather than a control choice - raised as ESC-WS8-8 and not self-resolved.

The worst-corner column IS like-for-like this round: r2 and r3 run the same six corners on the same seeds. r2's own table was not, and said so.

**The R28 corner is still not the worst one, and r3 scopes what that means** (r2 finding M3). At Vehicle One the thin air at 2,000 m takes about 27% off the aerodynamic bill, which is the dominant term on a line-haul corridor, and that outweighs the 6.9% engine derate it also imposes.

| candidate | nominal min | 2,000 m / +45 C min | -10 C min |
|---|---|---|---|
| **S1** | -0.69% | +1.71% | -12.87% |
| **S2** | +0.59% | +2.64% | -9.23% |
| **S3** | -1.09% | -0.56% | -14.17% |
| **S4** | -3.84% | -0.30% | -17.21% |

S1, S2, S3, S4 gain at the R28 corner relative to nominal. Either way the R28 corner is nowhere near the -10 C column. **The cold wall is Vehicle One's binding corner, and nothing in this round moved that.** R30 already reads it that way.

**Scope of that statement, measured** (finding M3). THE R28 CORNER DERATES THE ENGINE'S FULL-LOAD CURVE AND WHAT IS COMPUTED FROM IT, AND NOTHING ELSE. WS4's `derate_factor` is applied to every engine in the trial (S0's included) and therefore to the R18 continuous rating and the genset ceilings behind it. It is NOT applied to the traction machine, the inverter, the pack's charge or discharge ceiling, the brake resistor, or the compression brake - `ws8_electric.py` has no hot-side model at all and `Pack8.cold_chg_factor_at()` clamps to 1.0 above 15 C. The corner's BENEFIT - about 27% off the aerodynamic bill at 2,000 m - is shared by every candidate; its PENALTY falls only on combustion. Any conclusion drawn from this corner is scoped to that: it says the thin air outweighs an ENGINE derate, not that it outweighs a hot day for the whole vehicle. The cab-cooling load IS charged symmetrically (mechanical and bus-side both rise), which is the one hot-side effect the electric path does pay.

*Direction of error.* a missing hot-side electric derate FLATTERS the electrified candidates at this corner relative to S0; the corner is not binding for any of them, so no verdict depends on it, but WS9 inherits the statement under R28.

### 15.2 The findings, and what each one did

Every cell in the DIRECTION column below is either generated by `correction_directions()` from the one-factor table in section 4.4, or says explicitly that the direction is not separately measured and why. r2's version of this table was thirteen Python literals the verifier structurally could not reach, and `FINDINGS_WS8_r2.md` M1 names three of them as contradicted by that round's own numbers. That is finding M1, and this is its fix.

| finding | severity | what r3 did | direction |
|---|---|---|---|
| **B1** | blocking | THE ONE RULE. An engine geared to the road is in OVERRUN on every sample where the vehicle is moving and commands no tractive force: it burns no fuel, makes no positive shaft power, and its compression brake is available only there. S0 already had this cut-off inline; it is stated once in `overrun_mask` and applied to every candidate. S3's through-the-road charging is GATED ON THE VEHICLE NOT BRAKING (and, a fortiori, on the engine not being in overrun); the axle-A load threshold that used to be the only thing holding it back is no longer the gate and survives only as the BSFC policy it always was - and it is MEASURED to withhold 0.000 kWh over the whole trial, so it decides nothing either way. S2's genset ceiling is forced to zero on any sample where its lockup coupling is drawing the compression brake. The retarding ENVELOPE is untouched, so no achieved speed, trip time or descent case moves. The per-run assertion is hard and runs on every candidate: `heat_ledger.overrun_exclusivity` | FOR S2 (+0.085 pp), S3 (+5.262 pp); does not reach S1, S4 (re-run bit-identical) (measured: `B1_reverted_brake_and_fuel`) |
| **M1** | material | every hand-written direction string deleted; this column and section 4.4's direction table are generated by `correction_directions()` from the one-factor rows, and the one-factor set is widened from the S1/S2 pair to all four candidates so that a correction which does not reach a candidate returns a bit-identical row instead of an assertion | record integrity - it moves no number; `FINDINGS_WS8_r2.md` M1 names three r2 direction cells that this file's own numbers contradicted, and the measurement above replaces all thirteen |
| **M2** | material | the per-km bullets, and every other per-km claim in the report, computed on the PAIRED per-seed statistic and labelled; the 'every candidate is more efficient per kilometre' sentence generated from data; the ratio of medians exported beside it for disclosure (`interface_ws8.per_km_margin_paired`) | record integrity - no margin moves; `FINDINGS_WS8_r2.md` M2 records that the r2 sentence was false for S3, whose two statistics differ in SIGN |
| **M3** | material | `corner_derate_scope` measures, leaf by leaf against nominal, what each corner's model actually changes, and the R28 conclusion is scoped by the measurement rather than asserted | record integrity - no number moves; the direction of error is exported |
| **M4** | material | ESC-WS8-1 restated with BOTH halves of the cell-substitution direction, the power half measured at the contact patch and the cold corner used as the in-model measurement of the transfer, and R27/ESC-1(c)'s execution as WS9's S4' cited with its provisional status | record integrity - no number moves |
| **m1** | minor | the ratio the 6% grade demands is a SWEPT result and now says so, with a resolution sensitivity solved at ten times the grid in both dimensions instead of the claim that no grid was doing any work | record precision |
| **m2** | minor | the unserved-energy table lists every case above 1 kWh instead of silently truncating at twenty | record precision |
| **m3** | minor | `heat_ledger_ws6.csv` carries `ledger_version`, a `basis` column, `components_sum_kW` and the governing run, and a per-component label file for the simulated member | record precision |
| **m4** | minor | the instantaneous peaks `heat_peaks` has always computed are enveloped and exported beside the sustained figure, in the ledger and in the CSVs | record precision |
| **m5** | minor | `all_cases_close_and_within_rating` states exactly what it tests, the simulated member is no longer exempt from the closure, and the resistor row's unfailability by construction is stated rather than left to be discovered | record precision - and the exemption it describes is what B1 came through |
| **m6** | minor | the bus-side/wheel-side slippage on the pack charge ceiling is stated where the number is quoted; the physics is unchanged because it is conservative and changing it would move every margin | record precision - deliberately no number moves |
| **m7** | minor | section 4.2 renders the measured R22(d) charge and its coast-permitting bracket for all five candidates instead of calling the disconnect a deleted tax that nobody pays | record precision |

### 15.2b Raised and closed inside r3, by the extended closure

R3_DIRECTIVE item 1 ordered `heat_closure_check` extended to the simulated member. Extending it meant building a per-sample energy balance for every run, and the balance did not close until six book-keeping errors were found. None of them was in `FINDINGS_WS8_r2.md`; they are listed here because a correction that is not in the changelog is a silent one. The CONSEQUENCE column is measured, not asserted - where a correction has a one-factor row its direction is rendered from it, and where it cannot move a margin the reason is structural and stated.

| what | where | consequence |
|---|---|---|
| S0 was fuelled at the IDLE rate on the first few tenths of a second of every pull-away, because `stopped` is `v <= 0.1 m/s` and a launch begins inside it - the model credited the engine with about 28 kW of launch shaft power on 13.7 kW of fuel | `S0.account` | it moves THE RULER and therefore every margin, so it is switchable and measured rather than called small: FOR S1 (+0.003 pp), S2 (+0.003 pp), S3 (+0.003 pp), S4 (+0.003 pp) |
| S0's clutch-slip heat was booked twice: once inside `p_shaft - aux - p_wheel`, which already contains it, and again as `p_slip_kw` | `S0.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S0's accessory row booked the full accessory load even on samples where the crank was at its full-load curve and could not carry it - r1's finding F3 for S2, surviving in the ruler. The row now books what the crank carried and the shortfall is exported | `S0.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S2's standstill idle fuel was added to the fuel total AFTER the fuel series, so the heat ledger never saw it; and its generator's own loss was priced off the free-speed locus while the crank was locked to the road | `S2.account` heat rows | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it |
| S3's through-the-road path had NO heat rows at all - the engine was charged for the torque and the pack credited with the electricity, with the axle-A box and the e-axle's generating losses booked nowhere - and regen the full pack could not take was dropped with no bookkeeping at all | `S3.account`, `series_dispatch` | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it; and the rows it adds carry 0.000 kWh of through-the-road charge over the whole trial, because the path itself is inert once the B1 gate is applied (ESC-WS8-8) - the correction is real and its measured contribution is zero |
| regen the FULL pack cannot accept is dispatched to the brake resistor by `series_dispatch` and by S3's SOC loop - each says so in its own comment - and r3's first cut of the run closure carried it as an out-term OUTSIDE the component ledger. A real power flow with no component row is r1's F1 and r2's B1 over again. It is now booked to the resistor up to the rating whose mass was charged, and the remainder is exported as a CAPABILITY shortfall | `resistor_and_overcommitment`, `run_closure` | no margin can move: the heat ledger is built from the completed runs (`heat_ledger()` runs after `task3_margins` is fixed) and no margin reads it; worst overcommitment 254.3 kW sustained at `S4/grade_heavy/LH-520/seed8101` - escalated as ESC-WS8-10 |

### 15.3 Verdict stability

| candidate | verdict executed under R25 | verdict the same criteria give on the r3 numbers | headroom to the >= 3% nominal bar |
|---|---|---|---|
| **S1** | KILL | KILL | 3.69 pp short |
| **S2** | KILL | KILL | 2.41 pp short |
| **S3** | KILL | KILL | 4.09 pp short |
| **S4** | KILL | KILL | 6.84 pp short |

WHR on the r3 numbers: S1 DROPPED, S2 DROPPED, S3 DROPPED - unchanged.

**R3_DIRECTIVE item 1's own trip-wire, implemented rather than remembered.** R3_DIRECTIVE item 1: S3's fuel correction is expected to improve it by several percent and to leave it far below the bar. If S3's NOMINAL ENSEMBLE-MIN crosses +3%, the round STOPS and reports and does not touch the verdict. S3's nominal ensemble-min on the r3 numbers is -1.09% against the +3% bar: `crossed = false`. S3 is dead on CAPABILITY regardless of fuel - no fixed ratio both cruises at 105 km/h and holds the 6% grade at 36,300 kg - so this trip-wire is about the fuel number the record carries, not about the verdict's reason.

**`all_unchanged = True`.** If `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3, R3_DIRECTIVE item 1). It carries BOTH tests: the four executed verdicts against the pre-committed criteria, and R3_DIRECTIVE's own trip-wire on S3's nominal ensemble-min.

### 15.4 Environment

r1's artifacts were produced on Python 3.11.15 / numpy 2.4.6 on x86-64 Linux; r2's and r3's are produced on Python 3.14.3 / numpy 2.5.2 on arm64 macOS. The two platforms differ in the last one or two units in the last place of a double - a relative difference around 1e-16, from libm and SIMD reduction order, not from any change here. Byte-stable regeneration (rule 1) is a property of a run reproducing ITSELF on one machine, and it is checked in section 14 on this one. Nothing in the errata depends on that difference, and no reported figure is quoted to anything like that precision.

### 15.5 Inputs, SHA-pinned

Every source file and every read-only object inherited from another workstream is pinned by sha256 in `interface_ws8.inputs_sha256`, so a consumer can tell from the export alone whether the numbers it holds came from these exact inputs. 23 files are pinned, and r3 adds this round's order, the findings file it closes and the baseline it runs against without dropping r2's - the r2 corrections are still live in the code and the verdicts still cite R25.

---
