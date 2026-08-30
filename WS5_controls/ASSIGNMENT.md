# WS5 ASSIGNMENT — SUPERVISORY CONTROLS FOR A DUAL-SERIES PROGRAM

You are the controls engineer on Project Volt. You report to the
project lead (a separate chat). Read, in order: ../BASELINE_v3.md
(authoritative — the clutch is deleted; note R15, R16, R21, R22),
then the interface blocks of WS2 (r4), WS3, and WS4 (post-KX if it has
landed; if not, build to hot-swap the `series_duty_v2` block and state
the vintage you ran). Runnable code, everything in this folder, finish
with REPORT_WS5.md. Escalations cite rulings.

## Scope
The supervisor for both variants: energy management, genset dispatch,
brake blending, traction control, thermal-aware derating, fault
management. There is no clutch, no mode selection, no synchronization —
do not reintroduce any.

## Requirements
- Blend order (R15): regen-to-pack -> pack heater (if cell temp in the
  R16 band) -> brake resistor -> friction. Consume WS2's chopper
  control interface and WS3's regen_acceptance.csv as the pack limit.
- Genset dispatch: V1 = start-stop on WS3's 3.0 kWh hysteresis band at
  the 35 kW fixed point (R19; 16-25 starts/shift is the ratified
  scale). V2 = design question (R22b): pinned point vs two-point vs
  load-following on the 4HK1-V2C map, judged on fuel energy per km,
  cycling counts, and NVH-relevant transition rates, using KX's
  `series_duty_v2` exports. 8-seed ensembles, part-load everywhere.
- Traction control (E23, day-one): torque limiting vs estimated axle
  load; empty-truck regen (~mu 0.36 per stop) and 13.5 kN launch
  (~mu 0.66) cases; consume WS2's exported adhesion curves.
- Cold dispatch (R16): between -15 and +10 C run the published derate
  curves; preconditioning below -15 C cell temp; heater arbitration
  with drive power.
- Coast policy (R22d): prefer light regen over true coast (1,109 W
  PM drag at 85 km/h otherwise unrecovered).
- Fault matrix: genset loss, pack loss or derate, resistor loss,
  inverter thermal derate, sensor loss. Both variants are
  no-mechanical-path (R22c): define limp capabilities honestly and
  hand WS7 the test list. Resistor-loss + descent is the case to
  treat with the most care (R2's sink is the only speed-independent
  retarder).
- Interfaces at 10 Hz; all quantities bus-side (R12); R14 export
  discipline for every worst-case field.

## Deliverables
State-machine specification (states, transitions, guards — as code
and as a rendered diagram), supervisor simulation closed over VOLT-SUB
and VOLT-REG for both variants with the WS1 cycles at 10 Hz,
energy/cycling/thermal results tables, fault-injection results, and a
machine-readable interface for WS6 (control-driven heat cases) and WS7
(test vectors).

## Report
REPORT_WS5.md: Assumptions; Dispatch trade (V2) with recommendation;
Blending and traction results; Fault matrix; Interfaces
(machine-readable); Escalations; first-principles sanity checks.
