# WS6 ASSIGNMENT — PACKAGING, INTEGRATION, AND THE HEAT LEDGER

You are the integration engineer on Project Volt and the owner of the
program heat ledger (R9). You report to the project lead (a separate
chat). Read, in order: ../BASELINE_v3.md (authoritative — pure series,
no clutch; note R20, R22, R24), then the interface blocks of WS2 (r4),
WS3, WS4 (post-KX when it lands), and WS5 when available (build to
hot-swap its control-driven heat cases; state vintages). Runnable
code/CAD-surrogate models as appropriate, everything in this folder,
finish with REPORT_WS6.md.

## Scope
Package the ratified system on the NPR-HD frame; own mass, volume, CG,
cooling, and HV routing. There is no clutch and no lockup driveline to
package.

## Requirements
- Components of record: WS3 pack (281 kg / 185 L, liquid loop 8 L/min,
  8 kW heater), WS2 spine (230.8 kg rollup: VM250-HV machine, 1200 V
  SiC inverter, 3.73 ohm forced-air resistor — placement options per
  WS2 §5 — cables 17.9 kg), WS4 genset (4HK1-V2C ~500 kg envelope,
  R24: flat-rating datasheet confirmation is a FREEZE-hold flag, not a
  start-hold; V1 variant V3307-V1C class), 10:1 reduction as built.
- HEAT LEDGER of record (you aggregate; nobody else has): R20 seeds —
  95.0 kW engine radiator package at the R6 corner in +45 C air,
  concurrent 17.9 kW LT electrical chain, WS2 LT-loop 10.57 kW (R21),
  pack loop 1.41 kW, resistor rejection by placement case, heater
  8 kW bus draw. Deliver loop architecture (HT/LT split, flows,
  temperatures, radiator/fan sizing) at the R7 envelope corners, with
  the concurrency matrix stated per R14.
- Mass and CG budget: deletion credit for the stock gearbox, clutch,
  and driveline modifications vs additions; axle-load shifts empty
  and at GVW (feeds E23 traction control and WS7 adhesion tests);
  target statement vs the 6,600 kg GVW basis and the +20% payload
  case.
- HV routing at the R10 window (749 V operating / 777.6 V transient):
  creepage/clearance class, connector and contactor placement,
  service disconnect, crash zones kept qualitative at prototype
  scope.
- Serviceability: pack extraction path, resistor element access,
  genset service side.

## Deliverables
Layout drawings (SVG or rendered from code), the heat-ledger workbook
as THE program artifact of record, mass/CG interface block, cooling
architecture spec, and a WS7 handoff list (instrumentation points,
coastdown ballast plan).

## Report
REPORT_WS6.md: Assumptions; Layout with alternatives considered; Heat
ledger and cooling architecture; Mass/CG budget; HV routing;
Interfaces (machine-readable); Escalations; first-principles sanity
checks.
