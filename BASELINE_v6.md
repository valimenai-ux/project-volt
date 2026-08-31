# PROJECT VOLT — BASELINE v6 (ratified 2026-08-31, morning after the night shift)

Supersedes BASELINE_v5.md. Ratifies WS11 (Vehicle Zero ruler trial) in
part, disposes WS8 r3, WS9 pre-adjudication, and KX r3, and sequences
the Fable pass. Prior content carries except as amended.

## VEHICLE ZERO — THE HONEST METRIC APPLIED (R32 executed by WS11 r2)
R42 — V2 TRUCKER: KILLED on the pre-committed criterion. Headline
-7.93% ensemble-min / worst corner -9.98% (climb); it wins +8.41% per
km and gives back 16.19 points of freight (195 kg over its break-even
curb). The ruler was modelled at ruler-favourable settings and never
calibrated (ESC-1); at the pessimistic end of every declared ruler
range V2 rises to a DRAW (+0.13% min / +0.59% median) — still below
the 3% bar under every reading the workstream ran. A criterion with
no "draw" state kills it. The record states the honest range, not the
headline alone. ESC-9 independently supports it: the V2 numbers of
record come from runs above V2's ratified continuous rating that
empty the pack on the governing corner. Consequence: the highway-
inclusive delivery duty reverts to the incumbent for now; a mass-lean
candidate for it is posed in Vehicle Zero wave two (R48).
R43 — V1 POSTAL: ADVANCE-PROVISIONAL. +20.11% nominal ensemble-min,
+19.12% worst corner, robust to every ruler-modelling bracket
(improves to +37.78% at the pessimistic end) and to the CdA road
change. Conditions before ratification: (a) ESC-2 ruled — cold corner
charges 2.2 kW cab heat; V1 uses a fuel-fired auxiliary heater when
the genset is off (fuel charged at 0.85) and waste-heat credit only
while the genset runs; V2/ruler waste-heat credit as engine-carrying;
(b) ESC-8 ruled — a warm-up / cold-start fuel model (engine coolant
temperature as a state; enrichment penalty during warm-up) is added,
since 72.58 pp of V1's margin rides on engine-off; (c) ESC-7 ruled —
payload corners follow WS8's `payload_kg()` convention (same cargo on
the road; candidate payload = ruler payload minus curb delta);
(d) ESC-4 — CdA 5.4 bracket exported alongside, provisional until WS7
coastdown. WS11 r3 runs all four (MORNING_DIRECTIVES.md); V1 ratifies
if it clears >=3% nominal and >=0% every corner after them.
R44 — ESC-1 / calibration: the crowdsourced in-use anchor cannot
calibrate a cycle. Verdicts are MODEL-RELATIVE until WS7 measures a
stock NPR-HD on the program cycles (mandatory WS7 task; no external
efficiency claim before it). ESC-3: aftertreatment mass is identical
across diesel ruler and candidates and is not a differentiator; it
becomes one only for a non-diesel genset (R48). ESC-5: R38 gate
applied — both passed; sustained-climb capability is recorded under
ESC-9. ESC-6: accepted as D20.
D20. THE TRANSMISSIONLESS SERIES ARCHITECTURE IS A STOP-GO-DUTY
     ARCHITECTURE. It won +20% on postal duty and lost on regional
     duty at the same mass, because regen and engine-off pay for its
     mass only where stops dominate. The premise's boundary is duty
     as much as mass.
D21. A LOWER-BOUND RULER IS THE WRONG GUARANTEE FOR A KILL. Kills
     require the ruler at its unfavourable end; advances require it
     at its favourable end. WS11 r2's correction of its own r1 claim
     is the reference case.

## VEHICLE ONE — dispositions
R45 — WS8 r3 ACCEPTED as progress; verdicts unchanged (S3 nominal min
-7.65 -> -1.09%, trip-wire not crossed). Round-3 adjudication NOT
CLEAN (B1: throttle-back branch on the pack power ceiling unmeasured,
+1.64 pp of S3's move without a one-factor row; B2: retard_over-
commitment exports the instantaneous max under a "60-second" label,
1.53x high). ESC-WS8-8 accepted (S3's through-the-road path is inert
under the one overrun rule; recorded). ESC-WS8-9: R34 trace export
binds new pipelines and full re-runs, not errata-only rounds.
ESC-WS8-10 is a PHYSICS DEFECT of record: the retard envelope never
re-solves when the buffer fills, so every simulated descent brakes
harder than the resistor can absorb — fix ordered in WS8 r4 and
inherited by WS9 r2 before any Fable pass.
R46 — WS9 pre-adjudication (Opus) accepted: PRE-B1 (concordance
module cannot fire on 10 of 15 fields — hard-coded verdict literals
and tautologies, mutation-proven), PRE-B2 (PEM "exactly 0.0" is an
unmeasured fallback), PRE-B3 (S5-13L 6% climb ledger row on the
motor-only branch of the D16 two-band envelope: 20.1 kW exported,
507.3 kW correct). WS9 r2 ordered. R38 CLARIFIED: the trip-time gate
applies at nominal AND at every corner, the same form as the margin
criterion. On the exported table S5-13L exceeds +5% at payload+20%,
cold and hot/altitude on every statistic; unless the Fable pass moves
those numbers, S5-13L's ADVANCE converts to KILL-ON-TIME at
ratification — the third wall (D16) expressed as time.
R47 — FABLE PASS SEQUENCED: after WS8 r4 and WS9 r2 close clean. It
adjudicates a target with no known defects, once. Budget rationale
unchanged.
R48 — WAVE-TWO CANDIDATES (posed, not cut): Vehicle Zero — V1-P
(Atkinson petrol genset for Postal: deletes DPF/SCR/DEF mass, parity
efficiency at the pin; the prime-mover task at 50 kW) and V2-L (mass-
lean hybrid for regional delivery: small machine, small buffer, stock
AMT retained — the semi lesson applied downward). Cut after WS11 r3.

## VEHICLE ZERO BUILD TRACK
R49 — KX NOT CONVERGED after three rounds; lead-supervised ROUND 4
authorized: R3-B1 — R20's radiator sizing case is the simulated R6
CORNER (103.522 kW two-minute maximum), not its ambient; restate
capability honestly, reverse ESC-12's conclusion on the record; the
two false sweep certifications; materials/minors. WS6 starts only
after KX r4 closes clean, on the Vehicle Zero ledger ONLY — Vehicle
One heat-ledger rows are out of WS6's scope entirely (Vehicle One has
no packaging workstream yet). This removes WS6's dependency on WS9.
R50 — CONCURRENCY / PIN-LOCK: no session modifies a module pinned by
another workstream while that workstream simulates; sha pins are
captured at READ time, not rebuild time (WS8 r3 M6). Foremen check
pins before launching. Commits are scoped to one workstream's files.

## Workstream states
Vehicle Zero: WS11 r3 open (then V1 ratification); KX r4 open; WS5
running; WS6 held on KX r4; WS7 to be cut with the ruler-calibration
task. Vehicle One: WS8 r4 open; WS9 r2 open; Fable pass after both;
WS10 (combination) after WS9 ratifies. Exhibit (WS12) after builds.
