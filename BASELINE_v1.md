# PROJECT VOLT — BASELINE v1 (ratified 2026-08-29)

Supersedes BASELINE_v0.md. Ratifies REPORT_WS1.md with the amendments and
rulings below. Workstream sessions read this file plus
WS1_loads_duty_cycles/REPORT_WS1.md and results.json; those three files are
the program record. Challenges go in your report's Escalations section.

## Program intent (unchanged)
Transmissionless hybrid drivetrain for light/medium commercial trucks.
The single fixed ratio + electric torque-fill is the EXPERIMENTAL VARIABLE
of this program, not an oversight. Prototype and science program;
economics out of scope. SI units.

## Vehicle Zero (amended)
- Isuzu NPR-HD, GVW 6,600 kg; payload sweeps to +20% are design cases
- Tire 215/85R16, dynamic radius 0.37 m
- CdA 4.2 m^2 and rho 1.20 kg/m^3 are PROVISIONAL fitted values pending
  coastdown (WS7). Genset and motor sizing carry the CdA 5.4 case (E13).
- Environmental envelope (R7, was E21): ambient -10 to +45 C, altitude
  0-2,000 m. Pack preconditioning required below 0 C. All Four Numbers
  and all downstream sizing are valid over this envelope only.

## Ratified WS1 outputs
The Four Numbers are envelopes, not scalars (8-seed ensemble convention).
Authoritative values live in WS1_loads_duty_cycles/results.json
`requirements_summary`; headline: V1 cycle RMS 21.7 kW / genset avg
10.1 kW / buffer 0.71-0.87 kWh / regen demand envelope 161 kW;
V2 i-MMD 19.9 kW / engine avg 47.0 kW / 1.29-1.38 kWh / 198 kW.
75 kW regen absorb cap RETAINED (sits on the knee, §2.3).

## Rulings on WS1 escalations

R1 (E17) — Splitter/range-change: REJECTED ON THE RECORD. A 2-speed
splitter would resolve E3, E4, E20 and part of E12, at the cost of the
program's reason for existing. Recorded costs of the single ratio, per
WS1: no sustained 6% capability on the engine path alone; 61.0 km/h
grade-hold; no engine retardation below 34.9 km/h; locked-path rpm welded
to road speed. Remedies R2, R3, R6 address the symptoms inside the
architecture. Anyone may reopen E17 only with data that defeats those
remedies.

R2 (E4) — Descent retardation: ADOPT DYNAMIC-BRAKE RESISTOR on the DC bus
(locomotive/Edison precedent). WS1's own table shows steady 6% descent
retardation power never exceeds 46 kW at any speed; the deficit is the
energy sink, and a dissipative sink is speed-independent — it works below
34.9 km/h where nothing else in the architecture does. Spec: >=50 kW
continuous dissipation at the bus, energy-unlimited; blending order regen
-> resistor -> friction (WS5). WS2 owns chopper+resistor; WS6 owns the
heat. Exhaust brake on V2 is optional secondary, not the answer of record.
Consequence for E7: the 12.7 kWh no-retarder descent line is DELETED from
the buffer stack.

R3 (E1/E2/E9) — Traction motor spec: the v0 ">=75 kW peak" is SUPERSEDED
by the WS1 §3.1 duty triple, now baseline:
- S1 continuous: >=45 kW / >=180 Nm at shaft; PLUS generating S1 >=50 kW
  continuous (feeds R2 resistor for full-length descents)
- S2 10-min: >=95 kW / >=200 Nm (6% grade hold in series at 61 km/h)
- Peak (1-min): >=120 kW, target 150 kW; >=515 Nm below 20 km/h;
  7,200 rpm
- Generating envelope: 73 kW / 370 Nm
Size cooling to S2-10min, not cycle RMS. Size copper on RMS torque with a
real loss model (§3.1.2), not RMS power.

R4 (E24) — Clutch-open fault: DERATED LIMP, not full performance. The
spine is NOT sized for the forced-series column. Fault spec F-1: with
clutch open, V2 shall sustain 70 km/h flat at GVW and complete a 6% grade
at 61 km/h using the S2-10min rating. S2-10min stays 95 kW. V1's fault
asymmetry (no mechanical path: genset or pack fault = tow) goes to the
WS7 test plan.

R5 (E18) — V1 speed envelope: V1 is formally a sub-80 km/h vehicle.
Charge-sustaining ceiling 78.6 km/h at the 50 kW class; V1 shall not be
dispatched on regional/highway work, and VOLT-REG is not a V1 cycle.
Genset class stays ~50 kW shaft (duty average is 10.1 kW; E6 start-stop
logic applies); WS4 may propose 50-60 kW if a candidate engine lands
there.

R6 (E19/E3/E15/E20) — V2 genset floor RAISED 110 -> 125 kW continuous
shaft, rating basis: deliver 122.1 kW at +20% payload, 4 kW accessories,
CdA 5.4, +45 C, 2,000 m (worst sweep row, §4.12). On E20: WS1's locked-
path load fractions assume the engine carries road load only. The
architecture has a generator on the crank: in lockup the supervisor can
bias engine load upward and bank the surplus (load-point shifting,
i-MMD-standard). Road speed welds RPM, not torque. E20's concern is real
but understated in the architecture's favor — resolve at Gate G1.

R7 (E21) — Envelope declared above. Cold case (all regen to friction,
V1 genset avg +48%) is a WS3 design case, not a corner note.

R8 (E7/E8) — Pack sizing: POWER FIRST. Design peaks from normal
operations: 120 kW discharge / 110 kW charge (transient), plus R2's 50 kW
continuous charge during descents. Usable buffer floors: >=3.5 kWh (V2),
>=1.5 kWh (V1) at the bus, built as the SUM of genset hysteresis + regen
headroom + grade reserve + SOC end-stops (E7 superposition, minus the
deleted descent line). Expect power cells (LTO / high-power LFP); if
energy cells appear, the pack is power-sized and E7 energies are moot.

R9 — Program-wide methods (from E22, §4.7-4.8, and the 20.2 kW orphan):
- Extrema from stochastic inputs are 8-seed ensemble envelopes.
- No peak-point efficiency scalars: every WS models part-load (maps or
  declared derates). WS1's +17-22% penalty on genset average stands as
  the reference correction.
- Cycles exchanged at 10 Hz.
- WS6 owns the program HEAT LEDGER. Every workstream reports rejected
  heat by component and operating case (start with: 20.2 kW electrical-
  chain heat at the V2 grade hold; 50 kW resistor; genset cooling).
- Traction control is a day-one requirement (E23): empty-truck regen
  mu ~0.36 per stop, 13.5 kN launch mu ~0.66, single driven axle.

## GATE G1 — the direct path on trial (from E20, blocking for WS6)
WS4 + WS5 joint deliverable: net energy over VOLT-REG for (a) locked path
WITH charge-bias load-point shifting on a real BSFC map vs (b) pure
series at the pinned BSFC point, both with part-load derates. KILL
CRITERION: if (a) does not beat (b) by >=5% net energy, V2 collapses to
V1-with-125-kW-genset and the clutch is deleted. No WS6 packaging
commitment to the clutch before G1 closes.

## Workstream map
WS1 CLOSED (ratified with amendments above).
WS2 traction motor / inverter / reduction / brake resistor / DC bus
    proposal — RELEASED, WS2_traction_motor/ASSIGNMENT.md
WS3 battery pack — RELEASED, WS3_battery/ASSIGNMENT.md
WS4 genset + Gate G1 (with WS5 preview) — RELEASED,
    WS4_genset/ASSIGNMENT.md
WS5 controls — HELD until WS2/WS4 interface proposals land
WS6 packaging + heat ledger — HELD until G1
WS7 prototype & test plan — HELD; owns coastdown (E13), V1 fault
    asymmetry (E24), adhesion tests (E23)

## Protocol (unchanged from v0, plus)
Reports are REPORT_WSn.md in the workstream folder, with a machine-
readable interface block mirroring results.json conventions. Escalations
cite the ruling they challenge (R1-R9, G1). The lead pre-registers
acceptance bands in the lead chat before reading any report.
