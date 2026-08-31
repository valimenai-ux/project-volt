# REPORT WS8 - VEHICLE ONE: SEMI-SCALE ARCHITECTURE TRIAL

Workstream WS8, Vehicle One. Executes `WS8_semi_architecture/ASSIGNMENT.md`, and the errata round ordered by `WS8_semi_architecture/R2_DIRECTIVE.md` under R26, against `BASELINE_v4.md`.

**Numbers version r2.** The verdicts are `executed_kill_2026-08-30` - R25 executed all four kills and the WHR drop on the pre-committed criteria, and **this round does not reopen them**. What r2 does is make the NUMBERS of record correct: the two blocking findings and the eleven material and minor ones from `FINDINGS_WS8_r1.md` are closed here, every corner is re-simulated, and section 15 states which direction each candidate moved and why.

**Nothing here is ratified.** The lead ratifies in a separate chat (CLAUDE.md rule 11). This report states what the physics gave and what it cost; the execute-or-spare decision is the lead's.

**This report is generated**, not written: every number below is formatted out of `results_ws8.json` by `make_report_ws8.py`, and `verify_ws8.py` asserts independently that each rendered figure appears verbatim and that the interface block equals `results_ws8.json['interface_ws8']`. Nothing was transcribed by hand (rule 2).

| | |
|---|---|
| Entry point | `run_ws8.py` (fixed seeds 8101..8108, 8 seeds) |
| Baseline of record | BASELINE_v4.md |
| Python / numpy | 3.14.3 / 2.5.2 |
| Metric of record | fuel energy per **payload** tonne-km [MJ/(t.km)] |
| Fleet mission | 70% LH-520 + 30% REG-165 by distance |

---

## 0. What this trial found

**No candidate advances.** S1, S2, S3, S4 all fail the pre-committed criteria.

The trial is decided by a single structural fact, and it is worth stating before any table: **at fixed gross combination weight, powertrain mass is payload.** Every candidate here is more efficient per kilometre than the conventional truck. Every candidate here is also heavier. The metric of record divides one by the other, and that division is what the assignment ordered precisely because it is where the argument actually lives.

S0, the ruler, burns **38.78 L/100 km** on the fleet mission. That is above the assignment's 30-38 L/100 km corridor, and the reason is the corridor itself rather than the model: run over the same road with the grade zeroed, S0 burns **33.08 L/100 km** median on an 8-seed envelope of 29.82 to 39.36, against a published 32.6 L/100 km for a typical EU tractor-trailer over the regulatory Long Haul cycle - consistent with the public band, with nothing fitted to it (section 3.4 states what that envelope does and does not support). Task 1 ordered 3,704 m of climb over 520 km (8-seed ensemble 3,507 m to 3,838 m); a 30-38 band describes a freeway. Reported, not tuned away, and escalated as ESC-WS8-7.

- **S1** burns 7.2% less fuel per kilometre than S0 and carries 1,387 kg less payload. Net on the metric of record: +0.73% (median), -0.69% (ensemble min). **KILL**.
- **S2** burns 9.7% less fuel per kilometre than S0 and carries 1,679 kg less payload. Net on the metric of record: +1.80% (median), +0.48% (ensemble min). **KILL**.
- **S3** burns -0.3% less fuel per kilometre than S0 and carries 1,226 kg less payload. Net on the metric of record: -5.26% (median), -7.65% (ensemble min). **KILL**.
- **S4** burns 5.9% less fuel per kilometre than S0 and carries 1,441 kg less payload. Net on the metric of record: -1.06% (median), -3.84% (ensemble min). **KILL**.

S3 fails for a reason that has nothing to do with fuel, and it is the most useful result in this report: **no fixed ratio exists that lets a diesel axle both cruise at 105 km/h and hold the 6% mountain grade at 36,300 kg.** The two requirements are not close, and in r2 the gap is stated in closed form rather than off a swept grid (finding F12): the cruise ceiling is **3.77:1** and the grade needs **6.88:1**, a factor of 1.8. That is not a tuning problem, and it is the answer to the question S3 was posed to ask.

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
| **S0** | Conventional 13 L diesel + 12-speed AMT, direct top gear | 20,785 kg | 2,845 kg | 38.78 | 0.6215 / 0.6643 / 0.7064 | - (ruler) | 0.0% | **RULER** |
| **S1** | Pure series - Vehicle Zero's architecture scaled to Class 8 | 19,398 kg | 4,232 kg | 35.99 | 0.6095 / 0.6607 / 0.7113 | -0.69% / +0.73% / +2.57% | 2.7% | **KILL** |
| **S2** | Single cruise-ratio + torque-fill, traction machine on a disconnect | 19,106 kg | 4,524 kg | 35.00 | 0.6025 / 0.6524 / 0.7031 | +0.48% / +1.80% / +3.18% | 2.3% | **KILL** |
| **S3** | Tandem split - diesel axle on ONE fixed ratio (no gearbox anywhere) + disconnectable e-axle | 19,559 kg | 4,071 kg | 38.89 | 0.6225 / 0.7081 / 0.7561 | -7.65% / -5.26% / -0.17% | 29.3% | **KILL** |
| **S4** | Range-extended BEV - large pack + 194 kW-shaft / 185 kW-bus sustainer genset | 19,344 kg | 4,286 kg | 36.48 | 0.6146 / 0.6715 / 0.7336 | -3.84% / -1.06% / +1.98% | 8.8% | **KILL** |

The last column before the verdict is the one to read sceptically. It is the fraction of a candidate's reported fuel that is a **correction** rather than fuel the model watched it burn: energy its prime mover and pack could not deliver, charged back as fuel so that every candidate is compared having completed the same mission at the same speeds, plus the charge-sustaining correction. A small share is bookkeeping. A large positive share means the candidate did not really do the mission, and the fuel number is flattering it - which is why the raw shortfall is reported separately in section 7 rather than left inside a single figure.

**The charge-sustaining correction is SYMMETRIC, and r1 did not say so** (finding F4). A pack that ends the mission FLATTER than it started is charged the make-up; a pack that ends FULLER earns the corresponding **credit**. That is the convention of record - SAE J1711 in spirit - applied identically to every candidate with a pack, and it is declared here rather than left for a reader to discover. It matters:

| | correction share, min / median / max | charge-sustaining direction over the (cycle, seed) set | margin of record | margin with the CREDIT suppressed |
|---|---|---|---|---|
| **S1** | +0.7% / +1.2% / +2.7% | make-up on 16/16 cases | -0.69% / +0.73% | -0.69% / +0.73% |
| **S2** | -1.7% / +0.8% / +2.3% | **credit** on 7/16 (cycle, seed) cases | +0.48% / +1.80% | +0.43% / +0.98% |
| **S3** | +8.6% / +16.3% / +29.3% | **credit** on 5/16 (cycle, seed) cases | -7.65% / -5.26% | -7.86% / -5.30% |
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

**S2** - One fixed reduction (2.60:1 overall) couples the engine to the wheels ONLY inside a cruise lockup band; outside it the truck is pure series. The traction machine sits behind a DISCONNECT, so while locked and not filling it is stationary and its spin drag is zero - the G1(b) tax deleted by hardware. Every remaining tax is charged: the machine's losses whenever it IS connected (measured, from WS2's map, not a scalar), and the engine's off-best-point operation at band edges, where road speed - not the supervisor - sets engine speed. There is ONE crankshaft and it has one speed and one full-load curve: while locked, traction torque is allocated first, then accessories, then the generator gets whatever torque is left and its fuel is priced at the ROAD-IMPOSED speed, not on the free-speed BSFC locus. Accessory duty the crank has no torque left to carry moves to the bus.

**S3** - Axle A: downsized diesel through a single fixed reduction and a rev-matched clutch. There is NO gearbox and NO generator, so the engine can do exactly one thing - turn axle A - and only above the road speed at which the fixed ratio puts it above its lugging limit. Below that speed the clutch opens and the engine SHUTS DOWN, because with no generator there is nothing else for it to drive. Axle B: a disconnectable e-axle owning launch, low speed, regen and peak assist, fed by a buffer pack that can only be refilled by regen or by through-the-road charging (engine pushes axle A, e-axle harvests on axle B) - a lossy path taken only when the engine is lightly loaded and the pack is below target.
BOTH G1 TAXES DELETED BY CONSTRUCTION, not by assumption: (a) the map-vs-scalar member cannot recur because no scalar chain efficiency exists anywhere in WS8 - every electric sample goes through WS2 r4's measured loss surface; (b) the spin-drag member is deleted by the e-axle's disconnect, and the code charges spin drag ONLY on samples where that disconnect is closed, so the deletion is auditable rather than asserted.

**S4** - Electric traction only; a small sustainer genset holds charge. Run CHARGE-SUSTAINING over the mission (the pack ends where it started), because the metric of record is FUEL energy and no electricity accounting was ordered: crediting a plug-in start would let S4 import propulsion energy the metric cannot see. That choice is stated, and its consequence - that S4 is judged as a series hybrid with a small engine and a heavy pack, not as a plug-in - is escalated rather than buried.

---

### 4.3 Two-speed traction bracket (informative)

The Task 0 product sweep found something that bears directly on how these candidates were sized: **every heavy truck that actually deleted its AMT still fitted a multi-speed gearbox on the traction side** - Hyliion Hypertruck ERX, ePower, ReVolt, Edison, Wrightspeed, BAE - and the heavy-duty e-truck transmission literature finds a three-speed gives the lowest energy consumption that still meets gradeability. WS8's electric candidates were sized on a SINGLE fixed reduction, because WS2's carried 7,200 rpm rotor limit caps the ratio at 12:1 and the 12% startability specification then sets the machine size.

With a two-speed (24:1 low / 12:1 high) the startability torque is met at half the stretch factor, so the machine halves under WS2's own mass law while the box is added back:

| | k, single-speed | k, two-speed | e-drive mass | + box | net mass | payload gain | margin vs S0 | gain |
|---|---|---|---|---|---|---|---|---|
| **S1** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +0.73% -> +1.19% | +0.46 pp |
| **S2** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | +1.80% -> +2.27% | +0.47 pp |
| **S4** | 1.80 | 0.90 | 484 -> 263 kg | 130 kg | -91 kg | +91 kg | -1.06% -> -0.59% | +0.47 pp |

Margins here are on the **median of per-seed paired margins vs S0, the same statistic as the headline (r1 finding F10: this was a ratio of medians and the basis was not stated)**.

**informative bracket, fuel per km held at the single-speed value; not the metric of record.** Fuel per kilometre is held at the single-speed value, which makes the bracket conservative: a smaller machine at a higher per-unit load is slightly more efficient at cruise, not less. It changes no verdict in this report - the gains are fractions of a point - but it says where the next mass is, and it says the industry already knew.

---

### 4.4 What decides the S1-vs-S2 ordering, one factor at a time

r1 put S2 ahead of S1 on the nominal median. The round-1 adjudication showed that about half of S2's advantage was the charge-sustaining **credit** (F4), and that S2's single engine was being run as a locked mechanical drive and a free-speed genset at the same time, with nothing capping their sum at the full-load curve (F3). Both are corrected in r2, and both move S2 and not S1. So the ordering is shown factor by factor rather than only at the end.

each row reverts EXACTLY ONE r2 correction and leaves the rest applied; margins are the same paired per-seed ensemble as the headline, at the nominal corner. S0 is unaffected by every correction in this set (it has no pack, no traction machine and no corrections), so the ruler is the same in every row.

| row | S1 min / median / max | S2 min / median / max | ordering |
|---|---|---|---|
| `r2_as_reported` | -0.69% / **+0.73%** / +2.57% | +0.48% / **+1.80%** / +3.18% | S2 ahead of S1 |
| `F4_reverted_credit_removed` | -0.69% / **+0.73%** / +2.57% | +0.43% / **+0.98%** / +2.39% | S2 ahead of S1 |
| `F6_reverted_peak_point_pricing` | -0.66% / **+0.75%** / +2.58% | +0.53% / **+1.81%** / +3.19% | S2 ahead of S1 |
| `F3_reverted_engine_dual_use` | -0.69% / **+0.73%** / +2.57% | +0.40% / **+1.75%** / +2.77% | S2 ahead of S1 |
| `F5_reverted_spin_rule` | -0.69% / **+0.73%** / +2.57% | +0.42% / **+1.75%** / +3.13% | S2 ahead of S1 |
| `F3_and_F5_reverted` | -0.69% / **+0.73%** / +2.57% | +0.34% / **+1.71%** / +2.74% | S2 ahead of S1 |

- **`r2_as_reported`** - the margin of record: every r2 correction applied
- **`F4_reverted_credit_removed`** - the symmetric charge-sustaining CREDIT suppressed (the deficit make-up kept). Exact re-pricing of the same run.
- **`F6_reverted_peak_point_pricing`** - corrections priced at r1's peak-point efficiency instead of the candidate's duty average. Exact re-pricing of the same run.
- **`F3_reverted_engine_dual_use`** - S2's single engine run as a locked mechanical drive AND a free-speed genset at the same time, uncapped - r1's treatment. Re-simulated.
- **`F5_reverted_spin_rule`** - R22(d) charged on r1's two different unloaded tests instead of the one program-wide rule. Re-simulated.
- **`F3_and_F5_reverted`** - both re-simulated corrections reverted; F4 and F6 still applied. Re-simulated.

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
| S2 | ETC+ORC | +1.83% | +1.56% | >= 2.5% | **DROPPED** |
| S3 | ETC+ORC | +2.29% | +1.87% | >= 2.5% | **DROPPED** |

**Dropped, without ceremony.** Two things kill it, and the second is the interesting one.

First, the mass charge: the metric divides by payload, so the systems have to win back the gate plus what their mass displaced - the table above shows the real bar is nearer 3-4% than 2.5%.

Second, and more fundamental: **line-haul cruise is a part-load condition, and waste-heat recovery is a full-load technology.** Holding 36,300 kg at 95 km/h on level road needs about 100 kW at the wheel; on a 350 kW-class engine that is roughly a third of rated. Both systems modelled here are negligible below 30-35% load by construction, because exhaust mass flow and temperature both collapse there. The engine spends most of the mission in exactly the region where there is little enthalpy to recover, and the minutes it spends on the mountain at high load are too few to pay for the mass it carries for the other five hours.

This is not an argument that waste-heat recovery does not work. It is an argument that it does not pay ON THIS METRIC, on this duty, against a payload-denominated criterion that was armed before the numbers were seen.

---

## 6. Sensitivities (Task 5)

### 6.1 Corner sweep

Margins vs S0 [%], ensemble min / median, at every corner. Note that at the payload corners GCW moves with payload: the fixed-GCW condition is a Task-3 condition, not a Task-5 one.

**Two things about this table changed in r2.** The **-10 C** corner now applies WS3's cold charge acceptance, which r1 named in the corner label, in the provenance list and in Recommendation 5 but never called: S1's buffer takes 30.5 kW there against 240.0 kW warm, so descent regen goes to the resistor instead of the pack and every cold margin below is worse than r1's. And **2,000 m / +45 C** is a new corner, added under R28: it is the corner that became worst at Vehicle Zero, and it is the one that exercises WS4's ruled `derate_factor` (=0.9312 here), which r1 listed as inherited and never called. Both corrections cut AGAINST the candidates.

| candidate | nominal | payload +20% | payload -20% | grade-heavy corridor | -10 C | 2,000 m / +45 C |
|---|---|---|---|---|---|---|
| **S1** | -0.69% / +0.73% | +0.15% / +1.73% | -2.21% / -0.92% | +7.52% / +9.96% | -12.87% / -12.42% | +1.70% / +3.11% |
| **S2** | +0.48% / +1.80% | +1.36% / +2.89% | -0.92% / +0.20% | +7.75% / +9.16% | -9.62% / -9.08% | +2.50% / +3.34% |
| **S3** | -7.65% / -5.26% | -8.96% / -4.95% | -8.00% / -4.71% | -6.60% / -0.49% | -21.98% / -20.00% | -8.69% / -5.63% |
| **S4** | -3.84% / -1.06% | -2.08% / +0.68% | -6.17% / -3.38% | +5.55% / +9.98% | -17.21% / -16.43% | -0.31% / +2.32% |

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

**And the gap is closed in closed form too.** The lowest ratio at which axle A holds the 6% grade anywhere above its own lugging floor is **6.88**, which puts the engine at **3,832 rpm** at 105 km/h - 1,732 rpm over the 2100 rpm ceiling. The ratio the grade demands and the ratio the cruise permits differ by a factor of about 1.8. No swept grid is doing any work in that conclusion.

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

Worst case **264.55 kWh** (governing case: `S3/cold_minus10C/LH-520`), an explicit max over the enumerated (candidate, corner, cycle) set per R14.

Cases above 1 kWh:

| case | unserved kWh |
|---|---|
| `S3/cold_minus10C/LH-520` | 264.55 |
| `S3/grade_heavy/LH-520` | 190.07 |
| `S3/payload_plus20/LH-520` | 173.23 |
| `S4/cold_minus10C/LH-520` | 170.80 |
| `S3/hot_alt_2000m_45C/LH-520` | 149.73 |
| `S3/nominal/LH-520` | 145.14 |
| `S3/payload_minus20/LH-520` | 123.91 |
| `S3/cold_minus10C/REG-165` | 101.22 |
| `S4/grade_heavy/LH-520` | 93.26 |
| `S4/payload_plus20/LH-520` | 89.63 |
| `S3/grade_heavy/REG-165` | 81.02 |
| `S4/nominal/LH-520` | 67.61 |
| `S4/hot_alt_2000m_45C/LH-520` | 51.68 |
| `S4/payload_minus20/LH-520` | 48.09 |
| `S3/payload_plus20/REG-165` | 45.88 |
| `S3/nominal/REG-165` | 35.91 |
| `S3/hot_alt_2000m_45C/REG-165` | 35.05 |
| `S1/cold_minus10C/LH-520` | 21.45 |
| `S2/cold_minus10C/LH-520` | 19.55 |
| `S2/payload_plus20/LH-520` | 17.70 |

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
| **S1** | -0.69% | cold_minus10C | -12.87% | False | False | **KILL** |
| **S2** | +0.48% | cold_minus10C | -9.62% | False | False | **KILL** |
| **S3** | -7.65% | cold_minus10C | -21.98% | False | False | **KILL** |
| **S4** | -3.84% | cold_minus10C | -17.21% | False | False | **KILL** |

- **S1: KILL** - fails the nominal >=3% criterion.
- **S2: KILL** - fails the nominal >=3% criterion.
- **S3: KILL** - fails the nominal >=3% criterion.
- **S4: KILL** - fails the nominal >=3% criterion.

**What WS8 recommends.** The numbers are above and the execute-or-spare decision is the lead's. What WS8 will say is this:

1. **No candidate clears the bar as specified.** The margins are not catastrophic - several candidates are within a point or two of S0 - but 'within a point or two' is not >= 3%, and the criteria were armed before the numbers were seen.
2. **S3 should be spared further work regardless of its fuel number.** Its fuel result is not the finding; its capability result is. A fixed-ratio diesel axle cannot hold the specified mountain grade at any ratio that also permits highway cruise, and an e-axle fault leaves the combination immobile from rest. Those are structural, not parametric.
3. **The binding constraint on this vehicle is mass, not efficiency.** Every electrified candidate wins on fuel per kilometre and gives it back on payload. Any future work that does not attack the powertrain mass ledger is not attacking the problem.
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
r2 SUPPLIES THE NUMBER. The rebuilt heat ledger carries a foundation-brake row for the first time, and S0's worst sustained 60-second foundation-brake dissipation over the whole trial is 313 kW, against the 60 kW continuous grade-holding allowance the descent governor is built on. That is repeated snub braking on long descents - what a compression-brake-only tractor actually does - and it is reported in the ledger as an ADVISORY exceedance rather than a ledger error, because the allowance is a policy number and not a brake rating. It is the physical evidence for this escalation, and it is a thermal duty WS6 should see.

**Why this is not self-resolved.** Whether the ruler carries a retarder is a baseline-specification decision.

**Asks.** Confirm S0's retarder specification, or direct a re-run with a hydraulic retarder on S0. R27/ESC-6 has already ruled that S0 gains a hydraulic retarder in WS9 with its mass charged; this escalation is therefore CLOSED for Vehicle One's WS9 work and is carried here only because WS8's own numbers were computed before that ruling.

**Materiality:** low - affects trip time and accessory energy, not tractive work

### ESC-WS8-7 - S0's fuel exceeds the assignment's 30-38 L/100 km sanity corridor, and the model is not the reason

**Cites:** Assignment Task 2: 'Calibrate fleet fuel to a public reference band and state it (sanity corridor: 30-38 L/100 km loaded line-haul)'; Task 1: 'realistic grade distribution including sustained 2-3% and one 6% mountain segment with full descent'

**Finding.** S0's fleet-mission fuel is 38.78 L/100 km (ensemble 36.27 to 41.23), above the stated corridor. The calibration is nonetheless sound, and the cross-check says so directly: run over the SAME corridor with the grade zeroed - same distance, same speeds, same wind, same driver, same vehicle, nothing else touched - S0 burns 33.08 L/100 km MEDIAN, on an 8-seed envelope of 29.82 to 39.36 L/100 km, against the ICCT / TUV NORD figures of 29.9-33.1 L/100 km (typical 32.6) for an EU tractor-trailer over the regulatory Long Haul cycle.
WHAT THAT SUPPORTS, restated in r2 (finding F7). r1 read this off the median and called it 'a match to about one percent'. It is not: the ensemble envelope is WIDER than the public band it is being compared against, and the comparison is not mass-matched - WS8's S0 carries 20.8 t of payload at the assignment's fixed GCW against the reference cycle's 19.3 t, and the three enumerated mass cases in section 3.4 show what that is worth. The claim the evidence supports is that the model is CONSISTENT WITH the public band on flat ground, reached with no fitting: the single calibration knob is solved against a declared BSFC island and nothing else is tuned.
The excess is TERRAIN. Task 1 ordered a corridor carrying a 6% mountain and sustained 2-3% sections - 3,704 m of climb over 520 km (8-seed ensemble 3,507 m to 3,838 m) - and a 30-38 L/100 km band describes a freeway-dominated regulatory cycle, not that road. The two orders are in tension, and WS8 has obeyed the one that governs the physics (Task 1's corridor) rather than adjusting the vehicle until Task 2's band was satisfied.

**Why this is not self-resolved.** Reconciling them would mean either flattening a corridor the assignment specified or tuning a vehicle parameter until a band was met - and tuning to a band is exactly what 'no fudge factor' forbids. Either change alters every candidate's result, so it is the lead's to make.

**Asks.** Rule on which governs: (a) the corridor as specified, with S0's fuel reported above the band and the flat cross-check standing as the calibration evidence (WS8's recommendation - it is the honest reading and the comparison between candidates is unaffected, since all five drive the same road); or (b) a flatter reference corridor, which would move every absolute fuel figure and none of the margins. Note that r2 has WEAKENED the evidence this escalation rests on, per F7: the anchor is an envelope consistent with the band, not a one-percent match to a point in it.

**Materiality:** low for the trial, high for the record - it changes no margin, because every candidate drives the same corridor, but it is a stated acceptance criterion not met and must not pass silently

---

## 12. Heat ledger for WS6 (rule 7)

**Rebuilt in r2.** Round 1's blocking finding F1 was three defects in one export: the governing case sat OUTSIDE the enumerated case set (the ledger priced the 6% descent with the pack accepting its full charge power throughout, when the pack fills in about four minutes of a ten-minute descent); compression-brake heat was booked as resistor heat with the exhaust row explicitly zeroed, so S1, S2 and S3 exported the identical figure despite three different retarder architectures; and foundation-brake heat had no row at all, so the S0 descent case did not close. All three are closed here.

component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation; compression-brake heat is booked to the EXHAUST and resistor heat to the RESISTOR, because they go to different places in a packaging study; the simulated member is a sustained 60-second mean, not an instantaneous spike, and it is a MEASURED PEAK rather than a balanced operating point - only the four analytic cases carry a closure residual, and only they are asserted to close.

Enumerated case set (R14): `cruise_95kmh_flat`, `climb_6pct`, `descent_6pct_pack_accepting`, `descent_6pct_pack_saturated`, `simulated_worst_run`.

Worst-case rejection by component [kW], an explicit max over that set with the governing case labelled:

| candidate | engine coolant | engine exhaust | traction machine inverter | generator rectifier | pack | brake resistor | friction brake | total rejected |
|---|---|---|---|---|---|---|---|---|
| **S0** | 208 (simulated_worst_run) | 304 (descent_6pct_pack_accepting) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 0 (cruise_95kmh_flat) | 313 (simulated_worst_run) | 569 (simulated_worst_run) |
| **S1** | 159 (climb_6pct) | 219 (simulated_worst_run) | 32 (simulated_worst_run) | 16 (climb_6pct) | 8 (simulated_worst_run) | 314 (simulated_worst_run) | 205 (simulated_worst_run) | 575 (simulated_worst_run) |
| **S2** | 196 (simulated_worst_run) | 271 (simulated_worst_run) | 32 (simulated_worst_run) | 16 (climb_6pct) | 10 (simulated_worst_run) | 268 (simulated_worst_run) | 66 (simulated_worst_run) | 543 (simulated_worst_run) |
| **S3** | 163 (simulated_worst_run) | 397 (simulated_worst_run) | 24 (simulated_worst_run) | 0 (cruise_95kmh_flat) | 7 (simulated_worst_run) | 183 (simulated_worst_run) | 148 (simulated_worst_run) | 651 (simulated_worst_run) |
| **S4** | 116 (simulated_worst_run) | 160 (simulated_worst_run) | 37 (simulated_worst_run) | 9 (simulated_worst_run) | 18 (simulated_worst_run) | 315 (simulated_worst_run) | 134 (simulated_worst_run) | 461 (simulated_worst_run) |

**The resistor and the compression brake are now separate rows, because they reject to different places.** An air-cooled grid resistor is a packaging and airflow problem; an exhaust-side compression brake is not. On the pack-saturated 6% descent:

| candidate | resistor kW | compression brake kW | foundation brakes kW | resistor rating kW |
|---|---|---|---|---|
| **S0** | 0 | 304 | 14 | - |
| **S1** | 313 | 0 | 60 | 340 |
| **S2** | 255 | 190 | 0 | 340 |
| **S3** | 182 | 204 | 60 | 200 |
| **S4** | 313 | 0 | 60 | 340 |

**Every case closes and every component stays inside the rating of the hardware whose mass was charged**: `all_cases_close_and_within_rating = True`. In r1 S3 exported 210.71 kW of resistor heat against the 200 kW resistor it had been charged 71.8 kg for (`FINDINGS_WS8_r1.md`, F1b); that check now exists and runs.

**5 ADVISORY exceedances, and they are a finding rather than an error.** An ADVISORY exceedance is a declared policy allowance exceeded, not a component rating: it is a finding about the architecture that WS6 needs, not an error in this ledger. S0's foundation brakes are the case that matters - a compression-brake-only tractor snubs repeatedly on a long descent, and the sustained figure is the physical evidence behind ESC-WS8-6.

| candidate | component | declared allowance kW | worst sustained kW | governing case |
|---|---|---|---|---|
| **S0** | foundation_brakes | 60 | 313 | simulated_worst_run |
| **S1** | foundation_brakes | 60 | 205 | simulated_worst_run |
| **S2** | foundation_brakes | 60 | 66 | simulated_worst_run |
| **S3** | foundation_brakes | 60 | 148 | simulated_worst_run |
| **S4** | foundation_brakes | 60 | 134 | simulated_worst_run |

**And every candidate exceeds it, not only S0.** That is the same mechanism F1(a) named, seen from the other end: the descent governor sets the speed a candidate may descend at from the retarding capability of a pack that has not yet filled, so once the buffer saturates part-way down the grade the retarding channel it was counting on is gone and the foundation brakes make up the difference until the truck slows. A pack-saturated governor would have every electrified candidate descending slower. That is a WS9 requirement rather than a WS8 correction - it changes trip time and therefore the metric - and it is flagged here rather than changed under an errata order.

The descent case is the one that matters to WS6: a series candidate holding the 6% grade puts several hundred kilowatts into a resistor bank that has to reject it to air, and that is a packaging and airflow problem, not an electrical one. The number to size on is the PACK-SATURATED one, not the pack-accepting one, because a buffer with a few tens of kWh of headroom does not survive a mountain descent.

---

## 13. Machine-readable interface (R14)

Every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline. This block is byte-identical to `results_ws8.json['interface_ws8']`; `verify_ws8.py` asserts it.

```json
{
 "_convention": "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); stochastic extrema are 8-seed ensemble envelopes (rule 4); every worst-case field is an explicit max/min over an enumerated case set with the governing case labelled (R14)",
 "numbers_version": "r2",
 "numbers_status": "r2 - the errata round ordered by WS8_semi_architecture/R2_DIRECTIVE.md under R26. Every number in this block is regenerated; r1's numbers are superseded, not amended in place.",
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
  "run_ws8.py": "f27d8efb13805b9a49896632e11d49bdc4806996e41166e39f7bd79713f6832a",
  "ws8_params.py": "d729fc7cb7323dbfbe725e839519fcf4987e9fec693dadaa8f8b894304cc6353",
  "ws8_physics.py": "79f93610de6fd1e5d42dfcb50dbc4a3d12ce0b3e2486c84bde14046a95309b9b",
  "ws8_cycles.py": "bd5b444294b5034b35f653f317aa1a710dfcb2c7c21a9085d1820c30ce05e6ff",
  "ws8_engine.py": "61cc29d04c6a56a3076ee34d866a566c0beaa80b14a21881c5ff4ad9f3dd85de",
  "ws8_electric.py": "74a932dbc795698986d32105652cc62dbeb6629bad4c3f6b61364aac538f9f6d",
  "ws8_candidates.py": "e3a741f4097f13d8d79545e9196e660ccec829646431d133f5ddaecce0a07c67",
  "ws8_whr.py": "674f91016f31cd29cac55cfdd71a6470d079b5699532809def2682dea49fdf5f",
  "requirements.txt": "23bf63c77db7c14b9e04f686f9cb9c319c5067d5e6935299b6dcb1ca521f4a7d",
  "ASSIGNMENT.md": "88be8fcce3509764a6e13842ccff09f11eaf397adb26c3452c9aaadf3d8a2b09",
  "R2_DIRECTIVE.md": "e3040204e8f70f0fa431ad4cfdb2af3514a22b4df7dee49a296aece00f25da3d",
  "FINDINGS_WS8_r1.md": "b3db6878367b39f13ce2d430181ffcccd6e8c078308caf5d534b40c8656c3ce8",
  "PRIOR_ART_WS8.md": "469c28c502108e5d56b450ff52991deb25485a18ae9370ddbeed1cf507cf64c3",
  "../BASELINE_v4.md": "6c51f25ab2d4b9fd776a2aa8df8779b94ba40e1558da0fe5e9c52478a5c78fd7",
  "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv": "e0f617eafbcead33a8bb5edc07b95174826bd300be3b43b78b1593aa93c8ba4c",
  "../WS2_traction_motor/data/capability_vs_rpm.csv": "1496c7123355877ed3fa20bc51a6596312c2ee0e56d048f3af2d974b54cbc746",
  "../WS3_battery/ws3_cells.py": "4253ec9d29df101ac2107df469e1b62b710564bef429ddfda7e501a39b0c7f6e",
  "../WS3_battery/ws3_pack.py": "78ca3dfcb8e7f0a9c3733364e724e76fcce947df7920fd66c508937fcf8d79f2",
  "../WS4_genset/ws4_models.py": "33d9b498ec5bb59da92330ad25da7ce3d8899c2e80b1e937b92394e0dc5f9716",
  "../WS4_genset/ws4_chain.py": "7162656aaac5d89ec0fff36d9486406aeaad0f5e84b877737cca48e2cc994bdb"
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
    "min": 0.373016596316284,
    "median": 0.3830015887517402,
    "max": 0.39102802420907073,
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
    "min": 0.621466084068082,
    "median": 0.6643461843959014,
    "max": 0.7064203333218632
   },
   "fleet_L_per_100km": {
    "min": 36.274410713277,
    "median": 38.77728321202376,
    "max": 41.23311305966628
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
    "min": -0.6911738831755881,
    "median": 0.7309169700244529,
    "max": 2.566864270419009
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
    "nominal_min": -0.6911738831755881,
    "nominal_median": 0.7309169700244529,
    "nominal_max": 2.566864270419009
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -0.6911738831755881,
     "payload_plus20": 0.14549720340904326,
     "payload_minus20": -2.2081033260270555,
     "grade_heavy": 7.519078778699198,
     "cold_minus10C": -12.869827153426131,
     "hot_alt_2000m_45C": 1.704812569592679
    },
    "value": -12.869827153426131,
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
    "min": -0.016809182316610344,
    "median": 0.00809876756372977,
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
    "min": 0.43262322033956374,
    "median": 0.9778729184270912,
    "max": 2.3861756795242313
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.3968106376750855,
    "median": 0.4141213170650872,
    "max": 0.4244478090535077,
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
    "min": 0.6024579642428044,
    "median": 0.6523950159993579,
    "max": 0.7030630658338181
   },
   "fleet_L_per_100km": {
    "min": 32.32384690777453,
    "median": 35.003133616239225,
    "max": 37.72164077054837
   },
   "margin_vs_S0_pct": {
    "nominal_min": 0.47525068711682233,
    "nominal_median": 1.7999416901398164,
    "nominal_max": 3.181669267738453
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": 0.47525068711682233,
     "payload_plus20": 1.3611130793282304,
     "payload_minus20": -0.920303096995483,
     "grade_heavy": 7.745390925054488,
     "cold_minus10C": -9.62069915116985,
     "hot_alt_2000m_45C": 2.50418900070523
    },
    "value": -9.62069915116985,
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
    "value": 0.29262319934462216,
    "max": 0.29262319934462216,
    "min": 0.08604249506481004,
    "median": 0.1626208802844369,
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
     "LH-520/seed8103",
     "LH-520/seed8106",
     "LH-520/seed8108"
    ],
    "deficit_cases": [
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
    "min": -7.862133631520564,
    "median": -5.295584901465324,
    "max": -1.3277627514646262
   },
   "correction_eta_fuel_to_bus": {
    "rule": "duty-averaged over the run being corrected, min/median/max over the enumerated (cycle, seed) set (rule 5: r1 used the locus MAXIMUM)",
    "min": 0.2891456884638235,
    "median": 0.3436602897568024,
    "max": 0.37467067553229627,
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
    "value": 145.144137795294
   },
   "fleet_MJ_per_payload_tkm": {
    "rule": "8-seed ensemble",
    "min": 0.6225498963445166,
    "median": 0.7081068305783778,
    "max": 0.7560549155418507
   },
   "fleet_L_per_100km": {
    "min": 34.19470444182634,
    "median": 38.894077289294685,
    "max": 41.52771453428459
   },
   "margin_vs_S0_pct": {
    "nominal_min": -7.654569404832098,
    "nominal_median": -5.26261297644925,
    "nominal_max": -0.1743960457729311
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -7.654569404832098,
     "payload_plus20": -8.958347493938678,
     "payload_minus20": -7.99809112256447,
     "grade_heavy": -6.5988139671969375,
     "cold_minus10C": -21.98286705421671,
     "hot_alt_2000m_45C": -8.688846945162034
    },
    "value": -21.98286705421671,
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
    "min": -3.844606116906859,
    "median": -1.0626174366132541,
    "max": 1.9753358962646956
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
    "nominal_min": -3.844606116906859,
    "nominal_median": -1.0626174366132541,
    "nominal_max": 1.9753358962646956
   },
   "worst_case_margin_pct": {
    "rule": "min over the enumerated corner set, ensemble-min within each corner",
    "cases": {
     "nominal": -3.844606116906859,
     "payload_plus20": -2.0772071676263564,
     "payload_minus20": -6.171694582525213,
     "grade_heavy": 5.547010136298695,
     "cold_minus10C": -17.209305419613294,
     "hot_alt_2000m_45C": -0.30516246863644453
    },
    "value": -17.209305419613294,
    "governing_case": "cold_minus10C"
   },
   "verdict": "KILL"
  }
 },
 "unserved_energy_kWh": {
  "rule": "max over the enumerated (candidate, corner, cycle) case set",
  "value": 264.5515333067464,
  "governing_case": "S3/cold_minus10C/LH-520",
  "cases_over_1kWh": {
   "S1/cold_minus10C/LH-520": 21.4520756174574,
   "S1/grade_heavy/LH-520": 15.826776447536048,
   "S1/hot_alt_2000m_45C/LH-520": 13.548095405017767,
   "S1/nominal/LH-520": 13.315260790597016,
   "S1/payload_minus20/LH-520": 9.99007903188616,
   "S1/payload_plus20/LH-520": 16.614506691847673,
   "S2/cold_minus10C/LH-520": 19.55136364056715,
   "S2/grade_heavy/LH-520": 12.601268461389637,
   "S2/hot_alt_2000m_45C/LH-520": 12.124722944244336,
   "S2/nominal/LH-520": 15.585890940691655,
   "S2/payload_minus20/LH-520": 11.996531882297953,
   "S2/payload_plus20/LH-520": 17.69572262884129,
   "S3/cold_minus10C/LH-520": 264.5515333067464,
   "S3/cold_minus10C/REG-165": 101.21502536365966,
   "S3/grade_heavy/LH-520": 190.07122462811122,
   "S3/grade_heavy/REG-165": 81.01715521559188,
   "S3/hot_alt_2000m_45C/LH-520": 149.72704793429787,
   "S3/hot_alt_2000m_45C/REG-165": 35.054952548562376,
   "S3/nominal/LH-520": 145.144137795294,
   "S3/nominal/REG-165": 35.907547493838706,
   "S3/payload_minus20/LH-520": 123.91249884902919,
   "S3/payload_minus20/REG-165": 1.31550135633209,
   "S3/payload_plus20/LH-520": 173.2296825061617,
   "S3/payload_plus20/REG-165": 45.87652584971558,
   "S4/cold_minus10C/LH-520": 170.7991090899651,
   "S4/grade_heavy/LH-520": 93.2599510393586,
   "S4/hot_alt_2000m_45C/LH-520": 51.67534181033989,
   "S4/nominal/LH-520": 67.6081947764574,
   "S4/payload_minus20/LH-520": 48.091325162940166,
   "S4/payload_plus20/LH-520": 89.63060373535244
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
   "S1": 1.751782303438002,
   "S2": 1.8320289203673816,
   "S3": 2.2912396001087227
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
   "rule": "lowest ratio on a 0.01 grid in [2.0, 12.0] whose axle A balances road load somewhere above its own lugging floor"
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
    "r2_verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "r2_nominal_margin_pct_min": -0.6911738831755881,
    "r2_worst_corner": "cold_minus10C",
    "r2_worst_corner_margin_pct_min": -12.869827153426131,
    "headroom_to_advance_pp": 3.6911738831755883
   },
   "S2": {
    "executed_verdict": "KILL",
    "r2_verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "r2_nominal_margin_pct_min": 0.47525068711682233,
    "r2_worst_corner": "cold_minus10C",
    "r2_worst_corner_margin_pct_min": -9.62069915116985,
    "headroom_to_advance_pp": 2.5247493128831775
   },
   "S3": {
    "executed_verdict": "KILL",
    "r2_verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "r2_nominal_margin_pct_min": -7.654569404832098,
    "r2_worst_corner": "cold_minus10C",
    "r2_worst_corner_margin_pct_min": -21.98286705421671,
    "headroom_to_advance_pp": 10.654569404832099
   },
   "S4": {
    "executed_verdict": "KILL",
    "r2_verdict_on_same_criteria": "KILL",
    "unchanged": true,
    "r2_nominal_margin_pct_min": -3.844606116906859,
    "r2_worst_corner": "cold_minus10C",
    "r2_worst_corner_margin_pct_min": -17.209305419613294,
    "headroom_to_advance_pp": 6.844606116906859
   }
  },
  "whr_executed": "DROPPED",
  "whr_on_r2_numbers": {
   "S1": "DROPPED",
   "S2": "DROPPED",
   "S3": "DROPPED"
  },
  "whr_unchanged": true,
  "all_unchanged": true,
  "note": "if `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3)."
 },
 "one_factor_S1_vs_S2": {
  "rule": "each row reverts EXACTLY ONE r2 correction and leaves the rest applied; margins are the same paired per-seed ensemble as the headline, at the nominal corner. S0 is unaffected by every correction in this set (it has no pack, no traction machine and no corrections), so the ruler is the same in every row.",
  "ordering": {
   "r2_as_reported": "S2 ahead of S1",
   "F4_reverted_credit_removed": "S2 ahead of S1",
   "F6_reverted_peak_point_pricing": "S2 ahead of S1",
   "F3_reverted_engine_dual_use": "S2 ahead of S1",
   "F5_reverted_spin_rule": "S2 ahead of S1",
   "F3_and_F5_reverted": "S2 ahead of S1"
  },
  "rows": {
   "r2_as_reported": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.47525068711682233,
     "median": 1.7999416901398164,
     "max": 3.181669267738453
    }
   },
   "F4_reverted_credit_removed": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.43262322033956374,
     "median": 0.9778729184270912,
     "max": 2.3861756795242313
    }
   },
   "F6_reverted_peak_point_pricing": {
    "S1": {
     "min": -0.6603970160332701,
     "median": 0.749159263367646,
     "max": 2.584407909364554
    },
    "S2": {
     "min": 0.5252827836770543,
     "median": 1.813353116422728,
     "max": 3.1944736419027495
    }
   },
   "F3_reverted_engine_dual_use": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.40117869522095784,
     "median": 1.7537491590169794,
     "max": 2.770436432295551
    }
   },
   "F5_reverted_spin_rule": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.4202694232951887,
     "median": 1.7477386547604514,
     "max": 3.1317566233521847
    }
   },
   "F3_and_F5_reverted": {
    "S1": {
     "min": -0.6911738831755881,
     "median": 0.7309169700244529,
     "max": 2.566864270419009
    },
    "S2": {
     "min": 0.34229284693757633,
     "median": 1.7098930371487548,
     "max": 2.741728041820522
    }
   }
  }
 },
 "heat_ledger_WS6": {
  "convention": "component heat rejection [kW], bus-side electrical quantities per R12; engine heat split 0.42 coolant+CAC / 0.58 exhaust+radiation; compression-brake heat is booked to the EXHAUST and resistor heat to the RESISTOR, because they go to different places in a packaging study; the simulated member is a sustained 60-second mean, not an instantaneous spike, and it is a MEASURED PEAK rather than a balanced operating point - only the four analytic cases carry a closure residual, and only they are asserted to close",
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
  "all_cases_close_and_within_rating": true,
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
      "driveline_kW": 28.29699369400503,
      "pack_kW": 0.0,
      "brake_resistor_kW": 0.0,
      "friction_brake_kW": 312.8381728182537,
      "accessory_kW": 7.000000000000011,
      "total_rejected_kW": 569.2674116972692,
      "engine_coolant_kW_run": "nominal/LH-520/seed8104 @ 85 km/h",
      "engine_exhaust_kW_run": "grade_heavy/REG-165/seed8107 @ 49 km/h",
      "driveline_kW_run": "payload_minus20/LH-520/seed8105 @ 101 km/h",
      "friction_brake_kW_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "accessory_kW_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 52 km/h",
      "total_rejected_kW_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "_governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null
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
      "governing_run": "nominal/LH-520/seed8104 @ 85 km/h"
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
      "governing_run": null
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
      "governing_run": null
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
      "governing_run": null
     },
     "driveline_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 7.6702828125852704,
       "climb_6pct": 29.119826161337528,
       "descent_6pct_pack_accepting": 0.0,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 28.29699369400503
      },
      "value": 29.119826161337528,
      "governing_case": "climb_6pct",
      "governing_run": null
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
      "governing_run": null
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
      "governing_run": null
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
      "governing_run": "payload_plus20/LH-520/seed8102 @ 65 km/h"
     },
     "accessory_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 4.0,
       "climb_6pct": 4.0,
       "descent_6pct_pack_accepting": 4.0,
       "descent_6pct_pack_saturated": 4.0,
       "simulated_worst_run": 7.000000000000011
      },
      "value": 7.000000000000011,
      "governing_case": "simulated_worst_run",
      "governing_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 52 km/h"
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
       "closes": true
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      }
     },
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
      "brake_resistor_kW": 314.2797964192598,
      "friction_brake_kW": 205.16919719822718,
      "accessory_kW": 6.600000000000004,
      "total_rejected_kW": 574.9274100108137,
      "engine_coolant_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "engine_exhaust_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "generator_rectifier_kW_run": "nominal/LH-520/seed8101 @ 92 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "driveline_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "pack_kW_run": "grade_heavy/LH-520/seed8108 @ 87 km/h",
      "brake_resistor_kW_run": "cold_minus10C/LH-520/seed8102 @ 98 km/h",
      "friction_brake_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "accessory_kW_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h",
      "total_rejected_kW_run": "grade_heavy/REG-165/seed8105 @ 94 km/h",
      "_governing_run": "cold_minus10C/LH-520/seed8102 @ 98 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null
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
      "governing_run": null
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
      "governing_run": "nominal/LH-520/seed8101 @ 92 km/h"
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
      "governing_run": null
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
      "governing_run": "grade_heavy/REG-165/seed8106 @ 30 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h"
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
      "governing_run": "grade_heavy/LH-520/seed8108 @ 87 km/h"
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 208.2686210923575,
       "descent_6pct_pack_saturated": 312.7213279257832,
       "simulated_worst_run": 314.2797964192598
      },
      "value": 314.2797964192598,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 98 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 94 km/h"
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
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h"
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
       "worst_case_kW": 314.2797964192598,
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
       "closes": true
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      }
     },
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
      "brake_resistor_kW": 267.8542671380678,
      "friction_brake_kW": 65.55340909899944,
      "accessory_kW": 7.000000000000011,
      "total_rejected_kW": 543.1874630581523,
      "engine_coolant_kW_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "engine_exhaust_kW_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "generator_rectifier_kW_run": "nominal/LH-520/seed8101 @ 51 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 30 km/h",
      "driveline_kW_run": "payload_plus20/LH-520/seed8102 @ 107 km/h",
      "pack_kW_run": "grade_heavy/REG-165/seed8101 @ 53 km/h",
      "brake_resistor_kW_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "friction_brake_kW_run": "cold_minus10C/REG-165/seed8106 @ 97 km/h",
      "accessory_kW_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 80 km/h",
      "total_rejected_kW_run": "grade_heavy/REG-165/seed8105 @ 102 km/h",
      "_governing_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null
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
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h"
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
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 108 km/h"
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
      "governing_run": null
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
      "governing_run": "grade_heavy/REG-165/seed8106 @ 30 km/h"
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
      "governing_run": "payload_plus20/LH-520/seed8102 @ 107 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8101 @ 53 km/h"
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 28.448320123756744,
       "descent_6pct_pack_saturated": 255.18270378649495,
       "simulated_worst_run": 267.8542671380678
      },
      "value": 267.8542671380678,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h"
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
      "governing_run": "cold_minus10C/REG-165/seed8106 @ 97 km/h"
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
      "governing_run": "hot_alt_2000m_45C/LH-520/seed8101 @ 80 km/h"
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 193.15652597176833,
       "climb_6pct": 432.6340090430579,
       "descent_6pct_pack_accepting": 257.6021441112718,
       "descent_6pct_pack_saturated": 471.0379220181041,
       "simulated_worst_run": 543.1874630581523
      },
      "value": 543.1874630581523,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 340.0,
       "worst_case_kW": 267.8542671380678,
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
       "closes": true
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      }
     },
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
      "engine_exhaust_kW": 396.8682168700302,
      "generator_rectifier_kW": 0.0,
      "traction_machine_inverter_kW": 24.395114824094073,
      "driveline_kW": 15.515656550929226,
      "pack_kW": 7.200720000000013,
      "brake_resistor_kW": 182.98084199006357,
      "friction_brake_kW": 147.95195002768787,
      "accessory_kW": 6.600000000000004,
      "total_rejected_kW": 651.390510936324,
      "engine_coolant_kW_run": "payload_plus20/LH-520/seed8105 @ 108 km/h",
      "engine_exhaust_kW_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "traction_machine_inverter_kW_run": "grade_heavy/REG-165/seed8106 @ 5 km/h",
      "driveline_kW_run": "nominal/LH-520/seed8107 @ 88 km/h",
      "pack_kW_run": "nominal/LH-520/seed8101 @ 97 km/h",
      "brake_resistor_kW_run": "cold_minus10C/LH-520/seed8108 @ 88 km/h",
      "friction_brake_kW_run": "grade_heavy/REG-165/seed8105 @ 101 km/h",
      "accessory_kW_run": "cold_minus10C/LH-520/seed8101 @ 33 km/h",
      "total_rejected_kW_run": "grade_heavy/REG-165/seed8102 @ 92 km/h",
      "_governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h",
      "road_speed_kmh": null,
      "case_wheel_power_kW": null
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
      "governing_run": "payload_plus20/LH-520/seed8105 @ 108 km/h"
     },
     "engine_exhaust_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 101.84293333311822,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 206.14354533807398,
       "descent_6pct_pack_saturated": 203.63955824659462,
       "simulated_worst_run": 396.8682168700302
      },
      "value": 396.8682168700302,
      "governing_case": "simulated_worst_run",
      "governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h"
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
      "governing_run": null
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
      "governing_run": "grade_heavy/REG-165/seed8106 @ 5 km/h"
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
      "governing_run": "nominal/LH-520/seed8107 @ 88 km/h"
     },
     "pack_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.10515463917525811,
       "climb_6pct": 2.6467457055313957,
       "descent_6pct_pack_accepting": 6.601106533201006,
       "descent_6pct_pack_saturated": 0.0,
       "simulated_worst_run": 7.200720000000013
      },
      "value": 7.200720000000013,
      "governing_case": "simulated_worst_run",
      "governing_run": "nominal/LH-520/seed8101 @ 97 km/h"
     },
     "brake_resistor_kW": {
      "rule": "max over the enumerated case set ['cruise_95kmh_flat', 'climb_6pct', 'descent_6pct_pack_accepting', 'descent_6pct_pack_saturated', 'simulated_worst_run']; the simulated member is the maximum 60-second mean over every (corner, cycle, seed) run in the trial",
      "cases": {
       "cruise_95kmh_flat": 0.0,
       "climb_6pct": 0.0,
       "descent_6pct_pack_accepting": 13.356705885655021,
       "descent_6pct_pack_saturated": 182.348178763229,
       "simulated_worst_run": 182.98084199006357
      },
      "value": 182.98084199006357,
      "governing_case": "simulated_worst_run",
      "governing_run": "cold_minus10C/LH-520/seed8108 @ 88 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 101 km/h"
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
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 33 km/h"
     },
     "total_rejected_kW": {
      "rule": "max over the enumerated case set; for the simulated member the total is the peak of the per-sample SUM, not the sum of the component peaks, because those do not occur at the same moment",
      "cases": {
       "cruise_95kmh_flat": 184.9142009426307,
       "climb_6pct": 21.1190202743001,
       "descent_6pct_pack_accepting": 257.6021441112718,
       "descent_6pct_pack_saturated": 467.0391060478347,
       "simulated_worst_run": 651.390510936324
      },
      "value": 651.390510936324,
      "governing_case": "simulated_worst_run",
      "governing_run": "grade_heavy/REG-165/seed8102 @ 92 km/h"
     }
    },
    "ratings_check": {
     "rows": [
      {
       "component": "brake_resistor",
       "kind": "hard",
       "rated_kW": 200.0,
       "worst_case_kW": 182.98084199006357,
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
       "closes": true
      },
      "climb_6pct": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.2155433976675523e-16,
       "closes": true
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      }
     },
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
      "case_wheel_power_kW": null
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
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h"
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
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h"
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
      "governing_run": "nominal/LH-520/seed8101 @ 91 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h"
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
      "governing_run": "payload_plus20/LH-520/seed8102 @ 105 km/h"
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
      "governing_run": "cold_minus10C/LH-520/seed8102 @ 105 km/h"
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
      "governing_run": "grade_heavy/REG-165/seed8105 @ 102 km/h"
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
      "governing_run": "cold_minus10C/LH-520/seed8101 @ 52 km/h"
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
       "closes": true
      },
      "climb_6pct": {
       "residual_kW": -5.684341886080802e-14,
       "relative": -1.5666089592909447e-16,
       "closes": true
      },
      "descent_6pct_pack_accepting": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      },
      "descent_6pct_pack_saturated": {
       "residual_kW": 0.0,
       "relative": 0.0,
       "closes": true
      }
     },
     "all_close": true
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
- **WS3** cell definitions, pack overhead model (1.55 x cell + 35 kg) and cold charge-acceptance figures - the last of these APPLIED in r2 at the -10 C corner (30.5 kW against 240.0 kW warm), where in r1 it was listed here and never called (finding F2)
- **WS4** `WillansEngine`, `PMGenerator`, `derate_factor` and the R12 chain conventions; `WS2TractionChain` as the ruled map loader. `derate_factor` is APPLIED in r2 at the added 2,000 m / +45 C corner (R28), where it returns 0.9312 and shrinks every engine's full-load curve and therefore every R18 continuous rating; in r1 it was imported, re-exported and never called (finding F11)

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

CLAUDE.md rule 1 requires that re-running the pipeline reproduces every committed artifact byte-identically. Checked in two independent halves, because the pipeline has two independent sources of possible drift: the simulation, and the derived blocks built on top of it. The check cannot run inside the process it is checking - it compares two independent runs - so it is performed outside and its result committed alongside the run it certifies.

**Half 1 - the simulation.** the full 8-seed nominal corner re-simulated FROM SCRATCH in a separate copy of the folder, a separate process and a separate worker pool at a different width (run_ws8.py --only-nominal --jobs 3, against the committed run's --jobs 5), then its trial slice compared against the committed run. Result: trial slice **byte-identical** (sha256 `84609e4cffa6308a...`); cycle ensemble identical; S0 calibration identical.

Wall-clock fields are excluded from the comparison and from the committed artifact alike: per-candidate and total runtimes are the only values in this structure that cannot reproduce, and _strip_runtimes removes them before the record is written.

**Half 2 - the derived blocks.** THREE-WAY in r2, where r1 compared two rebuilds only. (a) the full run's own results_ws8.json and its nine CSV exports were snapshotted; (b) run_ws8.py --from-checkpoint was then run over that run's checkpoint and its outputs compared against the snapshot, which tests that the derived blocks do not depend on whether they were built inside the simulating process or rebuilt afterwards; (c) --from-checkpoint was run a second time and compared against (b). All ten artifacts were byte-identical across all three. Result: `results_ws8.json` **byte-identical**, and all 9 CSV exports byte-identical.

**Not checked:** the five sensitivity corners, the WHR gate and the three one-factor re-runs were not re-simulated from scratch — they are the same code path as the nominal corner with different Ctx constants or a different errata set, and re-running them would have cost several more hours of compute for no additional class of evidence. Stated rather than implied.

## 15. r2 changelog - what moved, and which way

This round executed `R2_DIRECTIVE.md` against `FINDINGS_WS8_r1.md`. The verdicts were **not** reopened: R25 executed all four kills and the WHR drop on the pre-committed criteria, and the directive's instruction was to make the numbers of record correct and to STOP and report if any verdict flipped. None did.

### 15.1 Which direction each candidate moved

Against r1's numbers of record as quoted in R25 (BASELINE_v4):

| candidate | nominal min, r1 -> r2 | nominal median, r1 -> r2 | worst corner, r1 -> r2 | direction | verdict |
|---|---|---|---|---|---|
| **S1** | -0.66% -> -0.69% | +0.75% -> +0.73% (-0.02 pp) | -4.37% -> -12.87% (-8.50 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |
| **S2** | +0.36% -> +0.48% | +1.70% -> +1.80% (+0.10 pp) | -1.90% -> -9.62% (-7.72 pp, now at `cold_minus10C`) | **BETTER** on the nominal median | **KILL** |
| **S3** | -6.22% -> -7.65% | -3.83% -> -5.26% (-1.43 pp) | -11.17% -> -21.98% (-10.81 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |
| **S4** | -3.67% -> -3.84% | -0.95% -> -1.06% (-0.11 pp) | -8.26% -> -17.21% (-8.95 pp, now at `cold_minus10C`) | **WORSE** on the nominal median | **KILL** |

The worst-corner column is not like-for-like and should not be read as one: r1's worst corner was -10 C for every candidate, and r2 both made that corner harder (F2, the cold charge acceptance that was never applied) and added a corner that did not exist (R28's 2,000 m / +45 C). Both changes can only move a worst corner down.

**The R28 corner did not become the worst one, and that is itself a result.** R28 named 2,000 m / +45 C on the Vehicle Zero precedent that the altitude/hot corner became worst there. At Vehicle One it does not: the thin air at 2,000 m takes about 27% off the aerodynamic bill, which is the dominant term on a line-haul corridor, and that outweighs the 6.9% engine derate it also imposes.

| candidate | nominal min | 2,000 m / +45 C min | -10 C min |
|---|---|---|---|
| **S1** | -0.69% | +1.70% | -12.87% |
| **S2** | +0.48% | +2.50% | -9.62% |
| **S3** | -7.65% | -8.69% | -21.98% |
| **S4** | -3.84% | -0.31% | -17.21% |

S1, S2, S4 gain at the R28 corner relative to nominal; S3 loses there, because the derate falls on a mechanical path that has no genset behind it and pushes the shortfall onto the pack. Either way the R28 corner is nowhere near the -10 C column. **The cold wall is Vehicle One's binding corner, and nothing in this round moved that** - it deepened it. R30 already reads it that way.

### 15.2 The findings, and what each one did

| finding | severity | what r2 did | direction |
|---|---|---|---|
| **F1** | blocking | heat ledger rebuilt: a pack-saturated descent case and the simulated worst run added to the enumerated set, the retard channel split so compression-brake heat is booked to the exhaust and resistor heat to the resistor, foundation-brake and accessory rows added, every case closed against the energy that entered it, and every component asserted against the rating of the hardware whose mass was charged | no fuel number moves; the exported sink case rises substantially and the attribution changes for S2 and S3 |
| **F2** | blocking | `Pack8.p_cont_chg_kw_at()` / `COLD_CHG_FACTOR` wired into every regen envelope, every dispatch charge limit and S3's own SOC loop, at the corner's ambient | AGAINST every electrified candidate, at the cold corner only |
| **F3** | material | S2's single engine given one crankshaft: traction torque first, then accessories, then the generator on what is left, priced at the road-imposed speed; accessory duty the crank cannot carry moves to the bus | AGAINST S2 |
| **F4** | material | the symmetric charge-sustaining convention declared, the correction share exported signed with min AND max, and the credit-free margin reported alongside (section 4.4) | disclosure only - no number of record moves |
| **F5** | material | R22(d) charged on one rule for every candidate - geared AND unloaded - which removes S3's double count, and the coast-permitting bracket reported so the near-zero charge is not mistaken for a result | FOR S3 (it was paying twice); negligible elsewhere |
| **F6** | material | unserved and stored energy priced at the candidate's own duty-averaged fuel-to-bus efficiency over the run being corrected, not at the locus maximum (rule 5) | AGAINST S1, S3 and S4; slightly FOR S2, whose correction is a credit |
| **F7** | material | the S0 grade-zeroed cross-check restated as an 8-seed envelope against the public band, with three enumerated combination masses and the reference payload stated | weakens the evidence ESC-WS8-7 rests on; no margin moves |
| **F8** | minor | S4's headline specification rendered from the rating the model built, and class titles and policies added to the verify set | record precision |
| **F9** | minor | the road-load sanity note formatted from the computed values instead of hand-written prose inside the data file | record precision |
| **F10** | minor | the two-speed bracket computed on paired per-seed margins, the same statistic as the headline, with the basis stated | record precision |
| **F11** | minor | `derate_factor` exercised in an added 2,000 m / +45 C corner (R28) rather than removed from the provenance list | AGAINST every candidate with an engine on the load |
| **F12** | minor | the ratio ceiling solved in closed form as a physics bound, with the swept set kept as the illustration, and the ratio the 6% grade demands solved too | record precision; S3's conclusion is unchanged and now rests on no grid at all |
| **F13** | minor | the LH-520 climb figure formatted from the ensemble everywhere it appears | record precision |

### 15.3 Verdict stability

| candidate | verdict executed under R25 | verdict the same criteria give on the r2 numbers | headroom to the >= 3% nominal bar |
|---|---|---|---|
| **S1** | KILL | KILL | 3.69 pp short |
| **S2** | KILL | KILL | 2.52 pp short |
| **S3** | KILL | KILL | 10.65 pp short |
| **S4** | KILL | KILL | 6.84 pp short |

WHR on the r2 numbers: S1 DROPPED, S2 DROPPED, S3 DROPPED - unchanged.

**`all_unchanged = True`.** If `all_unchanged` were false the round would STOP and report rather than touch a verdict the lead has executed (R2_DIRECTIVE item 3).

### 15.4 Environment

r1's artifacts were produced on Python 3.11.15 / numpy 2.4.6 on x86-64 Linux; r2's are produced on Python 3.14.3 / numpy 2.5.2 on arm64 macOS. The two platforms differ in the last one or two units in the last place of a double - a relative difference around 1e-16, from libm and SIMD reduction order, not from any change here. Byte-stable regeneration (rule 1) is a property of a run reproducing ITSELF on one machine, and it is checked in section 14 on this one. Nothing in the errata depends on that difference, and no reported figure is quoted to anything like that precision.

### 15.5 Inputs, SHA-pinned

Every source file and every read-only object inherited from another workstream is pinned by sha256 in `interface_ws8.inputs_sha256`, so a consumer can tell from the export alone whether the numbers it holds came from these exact inputs. 20 files are pinned.

---
