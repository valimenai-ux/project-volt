# WS9 ASSIGNMENT — VEHICLE ONE, WAVE TWO: THE TWO WALLS AND THE COLD WALL

Read CLAUDE.md, ../BASELINE_v4.md (R25-R33 and D13-D15 govern this
work), ../WS8_semi_architecture/REPORT_WS8.md, its FINDINGS_WS8_r1.md,
and its r2 outputs when they land (build to hot-swap; state vintages).
Inherit the WS8 pipeline (cycles, S0, mass ledger, electric scaling,
pricing of unserved energy AS CORRECTED by r2) — do not re-derive
what is ratified; extend it. Vehicle Zero folders are untouchable.

## What WS8 established (do not relitigate)
Mass is payload. No fixed engine ratio spans cruise and grade at
36.3 t. Cold is binding. WHR is part-load-starved on fleet-average
duty. S1-S4 are dead as specified; the incumbent is conceded near-
optimal on flat corridor duty (R29).

## Design duty (R29)
Primary: GRADE-HEAVY REGIONAL corridor (define from WS8's grade-heavy
corner; state it as the design duty with its own 8-seed ensemble).
Control: WS8's flat line-haul corridor. Report every candidate on
both, per-class, never only as a fleet average.

## Ruler
S0 per WS8, plus a hydraulic retarder with mass charged (ESC-6) and
the F7 ensemble cross-check. Same engine, same AMT.

## Candidates (fixed 36,300 kg GCW; metric = primary energy per
PAYLOAD tonne-km; corners per R28 incl. -10 C with WS3 cold
acceptance applied and 2,000 m / +45 C)
S5 — Minimal transmission: 2-speed dog box (no synchros, no launch
     clutch, no power-shift), motor-synchronized shifts, torque-fill
     through the shift; lean traction machine + buffer sized for
     launch, regen, and the R2-style descent duty only; engine sized
     to cruise-plus-margin. Show both walls addressed by construction:
     the two ratios must span cruise-under-rpm-ceiling and the 6%
     grade at GCW with the mass ledger stated to the kilogram.
S6 — Zero-mass stack: mechanical drive as S0; opposed-piston-class
     engine on a cited efficiency basis (state the BTE claim and its
     evidence quality, mass-neutral or better); predictive energy
     management (zero mass); electric turbocompound ONLY if it clears
     the 2.5% net gate on the design duty. The control for "how far
     without electrification".
S7 — Marginal-mass electrification: motorize an EXISTING trailer axle
     (new mass = motor, inverter, small buffer, cabling; no new axle);
     regen and assist; tractor untouched. Charge everything.
S4' — Range-extended BEV re-posed: cited external energy-optimised
     cell as a non-WS3 bracket (ESC-1c); electricity term per ESC-3
     with a declared grid primary-energy factor and a CO2 lens, factor
     sensitivity +/-50%.
All electrified candidates: preconditioning + waste-heat cab-heating
path modelled (R30). Machine basis rule per ESC-2. Genset rating
basis per ESC-4. Willans HD anchor per ESC-5.

## Prime-mover-at-the-pin task
For any series element (S4' sustainer; S7 has none; S5 none): diesel
vs Atkinson-cycle petrol vs natural-gas SI at the pinned point —
efficiency at the pin, engine + aftertreatment + tank mass for equal
range charged to payload, cold behaviour, fixed-point durability.
Energy and emissions only; price is out of scope.

## Advance/kill criteria (pre-committed, unchanged in form)
ADVANCE only if >=3% better than S0 on the DESIGN DUTY at nominal,
ensemble-min, AND >=0% at every R28 corner; report the control-duty
result alongside without it gating. Report the numbers; the lead
executes or spares.

## Report
REPORT_WS9.md: design duty definition; ruler restatement; candidate
table (headline, per duty class); prime-mover task; corners; mass
ledgers to the kilogram; recommendation; R14 interface; escalations
citing rulings; first-principles sanity checks. Exit: launch
ws-adjudicator on this folder, then stop.
