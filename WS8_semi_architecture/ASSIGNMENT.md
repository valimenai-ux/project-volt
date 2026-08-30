# WS8 ASSIGNMENT — VEHICLE ONE: SEMI-SCALE ARCHITECTURE TRIAL

Read CLAUDE.md and the highest-numbered BASELINE first. This opens a
second vehicle program (Vehicle One); touch nothing in Vehicle Zero's
workstream folders. All Vehicle Zero conventions bind: deterministic
pipelines, 8-seed ensembles, part-load everywhere, bus-side electrical
quantities, R14 exports, escalations cite rulings.

Reference vehicle: Class 8 6x4 tractor + van trailer, 36,300 kg gross
combination weight (GCW), CdA ~5.5 m^2, Crr ~0.0055, tire dynamic
radius ~0.50 m — refine with stated or cited values, flagged per E13
precedent as provisional.

TASK 0 — Prior-art scan (bounded): patents, programs, and academic
literature on P4/through-the-road heavy-duty hybrids; e-axle overlay
products (Hyliion 6X4HE lineage, Revoy dolly); any transmissionless or
single-fixed-ratio ICE axle on a truck. Deliver a claim map: occupied
ground, open ground, and anything contradicting S3's premise. If this
environment restricts web access, mark Task 0 DEFERRED with an
explicit stub and continue — physics does not wait on it.

TASK 1 — Duty cycles at 10 Hz, 8-seed ensembles: (a) line-haul
corridor, 500+ km, 85-105 km/h, realistic grade distribution including
sustained 2-3% and one 6% mountain segment with full descent; (b)
regional mixed urban/rural/highway.

TASK 2 — S0 baseline, calibrated: modern 13 L-class diesel
(~330-370 kW) + AMT with direct-drive top gear, Willans/published-BSFC
class engine map, transmission and axle efficiencies stated. Calibrate
fleet fuel to a public reference band and state it (sanity corridor:
30-38 L/100 km loaded line-haul). Every candidate is judged against
S0 — no self-referential comparisons.

TASK 3 — Candidate trial at FIXED 36,300 kg GCW. Metric of record:
fuel energy per PAYLOAD tonne-km — every powertrain kilogram displaces
payload; state each candidate's payload explicitly. Candidates:
- S1 pure series: Vehicle Zero architecture scaled (genset ~330 kW
  class, resistor descent brake, buffer pack).
- S2 single cruise-ratio + torque-fill: lockup band at cruise speeds
  only; traction machine has a DISCONNECT so lockup spin drag is
  zero; charge every remaining tax honestly (re-derive drag when
  connected, off-point engine operation at band edges).
- S3 tandem split: axle A = diesel through one fixed ratio with a
  rev-matched clutch, no gearbox anywhere; axle B = disconnectable
  e-axle owning launch, low-speed, regen, and peak assist; engine
  downsized toward cruise-plus-margin. Both G1 taxes must be shown
  deleted by construction, not assumed away.
- S4 range-extended BEV: large pack + sustainer genset
  (~150-200 kW); pack mass charged honestly against payload.
Electric components scale from WS2 r4 measured maps with stated
scaling laws; battery basis from WS3's cell data; genset accounting
per the ruled chain conventions.

TASK 4 — Waste-heat-recovery modifier on S1-S3's steady engine
operating point (electric turbocompound and/or small ORC). Adoption
gate, pre-committed: >=2.5% net fleet-mission fuel AFTER its mass
charge, else dropped without ceremony.

TASK 5 — Sensitivities: payload +/-20%; grade-heavy corridor; -10 C;
and S3-specific risks: diesel-axle-only adhesion on cruise grades,
fixed-ratio grade-hold floor, e-axle-fault limp capability.

ADVANCE/KILL CRITERIA (pre-committed): a candidate ADVANCES only if it
beats S0 by >=3% fleet-mission fuel per payload tonne-km at nominal
AND is >=0% at every sensitivity corner, margins reported as ensemble
envelopes. Report the numbers; the lead executes or spares.

REPORT_WS8.md: Prior-art map; Cycles; S0 calibration; Candidate
results table (the headline); WHR gate result; Sensitivities;
Recommendation; machine-readable interface per R14; Escalations
citing rulings; first-principles sanity checks. Exit per CLAUDE.md:
launch ws-adjudicator on this folder, then stop.
