# PROJECT VOLT — BASELINE v2 (ratified 2026-08-29)

Supersedes BASELINE_v1.md. Ratifies REPORT_WS3.md and REPORT_WS4.md;
disposes WS2 (NOT CONVERGED) into a lead-supervised round 4. Rulings
R1-R9 and Gate G1 definition carry forward from v1 except as amended
here. The program record = this file + the three WS reports +
results.json files + the six findings files + the three PM packets.

## Ruling status of Gate G1: PROVISIONAL PASS
WS4's delivered margins: 6.26% ensemble-min / 6.45% median at nominal
(passes >=5%); 8.22% at CdA 5.4; 6.46% at 4 kW aux; 5.94% hot-alone;
3.75-4.15% at the 2,000 m / +45 C corner (fails). ESC-2's plain reading
is RATIFIED: the gate is judged on VOLT-REG at nominal baseline
parameters. The corner shortfall is a CONTROL consequence, not a
hardware one — even there, lockup beats series by ~3.8%, so the sign
never flips; the remedy is WS5 condition-aware mode policy (prefer
series at density-derated corners), which costs no hardware. A clutch
you may decline to close is the transmissionless thesis working.
HOWEVER: the delivered margin excludes PM spin drag (WS4 line 111
claims mode-neutrality; WS2's measurement says lockup-only tax,
1.49 kWh engine-side + 0.50 kWh bus-side per VOLT-REG) and uses WS1's
scalar chain rather than WS2's measured maps (WS2-E7 quantifies a
+2.1/-1.0% silent-mix swing). Both known corrections lean AGAINST the
clutch. G1-R (recompute, directive in WS4_genset/G1R_DIRECTIVE.md) is
ORDERED; the kill clause stays armed at >=5% nominal ensemble-min on
the G1-R numbers. No WS6 clutch packaging before G1-R closes clean.
ESC-5 stands on the record: if the kill clause ever fires, the
V1-with-125kW fallback inherits a buffer problem at WS1's 7.32 kWh
scale — the fallback is not free.

## New rulings

R10 — DC BUS: 650 V CLASS, PACK-NATIVE. Nominal 662.4 V, operating
432.0-748.8 V, 10-s charge transients to 777.6 V, granularity 12 cells
(27.6 V). Basis: the pack's constraints are electrochemistry, the
spine's are design choices. The 400 V-class alternative fails outright
(174s1p: 110.1 kW warm < 120 kW R8; 40.5 kW cold < 64.9 kW regen
delivery) and the 2P fix doubles pack mass ~281 -> ~560 kg. The 288s
string collapses the R7 cold design case (67.0 kW cold acceptance >
64.9 kW capped regen) and dissolves WS2-F11 by construction (crawl
phase current scales ~x0.56 at 662 V winding). WS2 re-spins to this
window in round 4 (R4_DIRECTIVE.md): rewound machine kV, 1200 V-class
SiC, resistor re-ohmed, cables and maps re-derived at 432/662/749 V.
WS4's generator/rectifier spec follows the same window inside G1-R.
Full R8 power guaranteed at and above 432.0 V; WS3's T12 derate table
governs below.

R11 — G1 disposition as above. WS5 mode policy requirement recorded:
lockup preference must be condition-aware (density-derated corners bias
toward series).

R12 — ONE CHAIN CONVENTION (closes WS2-E7, WS3 ES-4). WS1's 0.97 "PE"
stage is the GENSET-side rectifier/conditioning and moves to WS4's
ledger. Traction side: bus->wheel = WS2 measured inverter+motor maps
x 0.97 reduction; no scalar PE member exists on the traction side.
All cross-workstream electrical quantities are stated BUS-SIDE unless
explicitly labeled otherwise. R8 peaks restated per ES-4:
125 kW discharge / 110 kW charge, bus-side, ensemble-envelope.
Superseded on the record: WS1's 0.8924 shaft-bus chain, its 0.866
bus-wheel chain, the 90.5 kW grade-hold shaft point (WS2 r4 restates at
the R10 voltage), and the 20.2 kW ledger seed (WS4's 17.9 kW recompute
is the seed of record until WS2 r4 maps land).

R13 — 20% CRAWL IS A CONTINUOUS DUTY REQUIREMENT (closes WS2-E1 and
WS1 E9). 515 Nm sustained, no time box, 10-25 km/h band. The
spray-cooled build is mandatory; G_ws >= 90 W/K verified by WS7
heat-run; 75 W/K is the declared continuous-limit floor. Cable and
inverter continuous basis = crawl phase current at the R10 voltage
(WS2 r4 re-derives; the 455 Arms figure was the 370 V symptom).
WS2-E3 accepted: WS1's "300-700 rpm" crawl figure is corrected on
the record to 760-1,692 rpm through 10:1.

R14 — EXPORT DISCIPLINE (structural fix for the WS2 three-round
pattern). Every machine-readable worst-case field is computed as an
explicit max/min over an enumerated case set, with the governing case
labeled inline in the interface block. Fields conditioned on a pending
ruling carry the ruling ID. Applies program-wide, retroactively to r4.

R15 — RESISTOR COOLING (closes cross-WS conflict). The R2 resistor
stays FORCED-AIR (WS2's delivery): retardation is brake-critical and
shall not share a failure domain with the pack loop. WS3's functional
goal is GRANTED electrically: the 8 kW pack heater (WS3-sized) feeds
from the DC bus, so descent regen warms a cold pack through the
electrical path once the SOC ceiling hands flow to heater + resistor.
WS5 blending order becomes: regen-to-pack -> pack heater (if cold) ->
resistor -> friction. No plumbing coupling. WS6 packages both.

R16 — COLD OPERATION (amends R7 per ES-2; LTO earned it).
Preconditioning required below -15 C CELL temperature (outside the R7
ambient envelope). Between -15 and +10 C: dispatch permitted on the
published derate curves (regen_acceptance.csv is the interface of
record). 8 kW heater retained. R8 transients fully available from 0 C
(charge) / -5.5 C (discharge) at the 432.0 V floor.

R17 — R2's "50 kW continuous charge" is a CAPABILITY requirement
(terminal power sustainable over the full 1,440 s descent), not an
energy requirement (per ES-1). The blend order owns the energy.

R18 — V2 GENSET (closes ESC-1). Baseline label adopts the
corner-delivery form: "flat-rated to deliver >=122.1 kW shaft at
2,000 m / +45 C". SELECTED: 4HK1-V2C (4HK1-TC genset recalibration,
5.19 L, 132 kW continuous flat-rating, 122.9 kW at the corner,
+0.82 kW margin, ~500 kg) — PROVISIONAL pending procured-datasheet
confirmation of the 132 kW flat-rating and derate model. That
confirmation plus G1-R are the two blockers on WS6 release.
V1: V3307-V1C class per report; V1 charge-sustain of record is
76.5 km/h (real chains), inside the R5 sub-80 ruling.

R19 — V1 STARTS (closes ESC-3 x ES-5). WS3's delivered 3.0 kWh
hysteresis band on 11.08 kWh usable governs: 16-25 starts/shift at the
35 kW bus fixed point. WS4's generator-as-starter ISG spec (>=20,000
warm starts/yr) retained as margin. E6 is closed.

R20 — HEAT LEDGER SEEDS for WS6 (per ESC-4): radiator sizing case =
R6 corner, 95.0 kW engine package in +45 C air, concurrent with
17.9 kW LT electrical chain (WS4 recompute, of record), WS2 LT-loop
(r4 re-derives; 10.22 kW is the 370 V placeholder), pack loop 1.41 kW
at 8 L/min. Foreman performed no aggregation; WS6 will.

## Ratified pack (WS3, READY)
288s1p SCiB-class 23 Ah LTO: 15.24 kWh nameplate / 11.08 kWh usable at
the bus, 662 V nominal, ~281 kg, ~185 L, liquid-cooled; R8 peaks at
~9C pulse / 3.2C continuous; descent-charge duty peaks cells at 50.3 C
vs 55 C ceiling, 1.41 kW loop. E8 is closed by construction.

## Workstream states
WS1 CLOSED (v1). WS3 CLOSED-RATIFIED. WS4 RATIFIED EXCEPT G1-R
(directive issued). WS2 ROUND 4 AUTHORIZED under lead supervision
(directive issued) — the 3-round foreman cap was procedural, and the
lead extends it deliberately: every prior round's fix held; the defect
class is structural and R14 addresses it. WS5 HELD until WS2-r4 +
G1-R close (its inputs: R12 conventions, R15 blend order, R11 mode
policy, regen_acceptance.csv, WS2 r4 maps). WS6 HELD on the two R18
blockers. WS7 accumulating: coastdown (E13), V1 fault asymmetry (R4),
adhesion (E23), crawl heat-run (R13), G_ws verification.

## Protocol addition
Directives (R4_DIRECTIVE.md, G1R_DIRECTIVE.md pattern) are
lead-issued, bounded re-work orders: the executing session finishes by
launching ws-adjudicator on its own folder and stops; the lead reviews
findings directly. Pre-registration discipline continues in the lead
chat.
