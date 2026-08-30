# WS2 ASSIGNMENT — TRACTION MOTOR, INVERTER, REDUCTION, BRAKE RESISTOR, DC BUS

You are the traction-machine engineer on Project Volt. You report to the
project lead (a separate chat). Read, in order: ../BASELINE_v1.md
(authoritative — note rulings R2, R3, R4, R9 and Gate G1), then
../WS1_loads_duty_cycles/REPORT_WS1.md §3.1, §4.16, E2, E8, E9, E12, E22,
E23, and ../WS1_loads_duty_cycles/results.json `requirements_summary`.
Do the work with runnable code where computation is involved, save
everything in this folder, and finish with REPORT_WS2.md.

## Scope
Size and select the traction machine(s), inverter, fixed reduction, and
the R2 dynamic-brake resistor + chopper. Propose the DC bus voltage —
this is the program's central interface and WS3/WS4 will inherit it.

## Requirements (from BASELINE v1)
- Duty triple R3: S1 >=45 kW / 180 Nm motoring AND >=50 kW generating
  continuous; S2-10min >=95 kW / 200 Nm; peak >=120 kW (target 150),
  >=515 Nm below 20 km/h, 7,200 rpm max; generating envelope 73 kW /
  370 Nm. Fault spec F-1 uses S2 ratings (R4) — do NOT size for the
  forced-series column.
- Cooling sized to S2-10min at +45 C (not cycle RMS). Copper sized on
  RMS torque with a real loss model (WS1 §3.1.2): 115 Nm RMS on
  VOLT-SUB is the heavier copper duty despite lower RMS power.
- Brake resistor: >=50 kW continuous at the bus, energy-unlimited,
  duty case = 24-min descent (WS1 §4.6). Report its heat to the WS6
  ledger.
- Part-load efficiency MAPS, not scalars (R9). Deliver the maps as data
  files — WS4's Gate G1 study and WS5 will consume them.
- Envelope: -10 to +45 C, 0-2,000 m.

## Tasks
1. Machine topology trade (PMSM / induction / others), one motor vs two,
   and the reduction ratio — 10:1 is provisional, challenge it: it sets
   the 515 Nm / 7,200 rpm corner. Evaluate 8:1-12:1.
2. Select or specify a machine + inverter meeting the triple; show
   thermal model results for S1, S2-10min at +45 C, and the 20% grade
   crawl (510 Nm at 10.6-23.6 km/h, near-zero airflow — WS1 §3.1.3).
3. Propose DC bus voltage with rationale (machine, inverter device
   class, cable mass, WS3 cell-count granularity, 50 kW chopper). State
   the allowed voltage window, not just a nominal.
4. Design the brake resistor + chopper (element type, mass, placement
   options for WS6, control interface for WS5).
5. Traction-control envelope with numbers (E23): torque limits vs
   estimated axle load, empty-truck regen and launch cases.
6. Efficiency maps (motoring + generating) over the full speed-torque
   plane, exported to data/.

## Report
REPORT_WS2.md: Assumptions; Trades and selection; Thermal results;
DC bus proposal (the headline); Resistor design; Traction-control
envelope; Interfaces (machine-readable block: bus voltage window, mass,
volume, coolant flow/temp, heat-to-ledger by case, efficiency-map file
paths); Escalations (cite rulings R1-R9/G1 if challenged);
first-principles sanity checks.
