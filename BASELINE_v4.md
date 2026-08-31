# PROJECT VOLT — BASELINE v4 (ratified 2026-08-30)

Supersedes BASELINE_v3.md. Adds the Vehicle One section (WS8 ratified
with errata pending), rulings R25-R33, doctrine D13-D15, and releases
WS9. Vehicle Zero content of v3 carries unchanged except R32.

## VEHICLE ONE (Class 8, 36,300 kg GCW) — WS8 RATIFIED, NUMBERS PROVISIONAL

R25 — WS8 verdicts EXECUTED on the pre-committed criteria (>=3% fuel
per payload tonne-km vs S0 at nominal, ensemble-min; >=0% every
corner). S1 pure series: -0.66% min / +0.75% median — KILL. S2 single
cruise-ratio + torque-fill with disconnect: +0.36% / +1.70% — KILL.
S3 tandem split: -6.22% / -3.83% — KILL, and independently killed on
capability: no fixed ratio both cruises at 105 km/h under the rpm
ceiling and holds the 6% grade (3.60:1 delivers 11.7 kN against
24.0 kN); the e-axle-alone climb needs 133 kWh against 21.6 kWh of
usable swing; single-axle launch needs mu 0.587. S4 range-extended
BEV as specified: -3.67% / -0.95% — KILL. WHR modifier at semi scale:
best system ETC+ORC nets +1.54-1.61% min against the >=2.5% gate —
DROPPED. The adjudicator reproduced all 60 margins to 1e-9 and the S3
capability result independently; the two blocking findings (F1 heat-
ledger export, F2 cold-corner dead code) touch no nominal number and
cut against the candidates. Verdicts are final; numbers of record are
PROVISIONAL until R2_DIRECTIVE.md closes (R26).

R26 — Errata order: WS8_semi_architecture/R2_DIRECTIVE.md (F1-F13,
cold-corner re-run, F3-F6 re-run with one-factor rows). WS6 shall not
consume WS8's heat ledger before r2 closes.

R27 — Escalation dispositions.
ESC-1: (c) — S4 is re-posed in WS9 as S4' carrying a cited external
energy-optimised cell as an explicitly non-WS3 bracket. WS3 is not
reopened. ESC-2: the k=3.6 machine stretch stands for the WS8 record
(it moves every candidate's common distance from S0, not ranking);
WS9 rule: machines scaled <=2.0x from WS2's validated range may use
WS2 maps; beyond that, a cited external HD machine basis with
direction of error stated. ESC-3: Vehicle One's metric acquires an
electricity term for any plug-in candidate — primary energy per
payload tonne-km at a declared grid primary-energy factor, with a
CO2-per-payload-tonne-km second lens and a factor sensitivity; S4 as
reported stays killed charge-sustaining. ESC-4: the R18 flat-rating
transfer stands as a bracket; WS9 sources a Class 8 prime-power
derating basis. ESC-5: the HD Willans speed re-anchor is RATIFIED for
Vehicle One. ESC-6: S0 gains a hydraulic retarder in WS9 with its mass
charged — the ruler gets the equipment the duty demands. ESC-7:
accepted; the 30-38 L/100 km corridor is RETIRED (it described a
freeway); calibration of record = grade-zeroed S0 33.08 L/100 km vs
ICCT 32.6 (F7: to be restated as an ensemble).

R28 — Corner set of record for Vehicle One: payload +/-20%, grade-
heavy, -10 C with WS3 cold acceptance actually applied, and 2,000 m /
+45 C (Vehicle Zero precedent: the corner that became worst).

R29 — DESIGN DUTY. Vehicle One is specified for GRADE-HEAVY REGIONAL
duty, with the flat line-haul corridor retained as a control on which
the incumbent is CONCEDED near-optimal (S0 spends 0.72 of moving time
in top gear near its BSFC island; duty-averaged 196.8 vs 185 g/kWh is
the entire hybrid opportunity there). Rationale: S1 spans ~+10% on the
grade-heavy corridor to ~-4% at -10 C; architecture is duty-indexed
and a fleet average hides the sign flip. Advance criteria in WS9 are
read on the design duty at nominal, AND >=0% at every corner.

R30 — THE COLD WALL. Cold was binding for every candidate and the
model understated it (F2). Every WS9 electrified candidate carries
pack preconditioning and a coolant/waste-heat cab-heating path as
requirements, modelled, not assumed; the conventional truck heats
itself for free and the comparison must charge that.

R31 — WS9 candidate set (WS9_vehicle_one_wave2/ASSIGNMENT.md):
S5 minimal 2-speed dog box + lean torque-fill (motor-synchronized
shifts, torque-fill through the shift, motor + buffer sized for
launch/regen/descent only — attacks both walls); S6 zero-mass stack
(mechanical drive, opposed-piston-class engine, predictive energy
management; ETC-only WHR re-tested on the design duty against the
same 2.5% gate, since design-duty load fraction is higher);
S7 marginal-mass electrification of an existing trailer axle;
S4' per ESC-1(c)/ESC-3; plus the prime-mover-at-the-pin task (diesel
vs Atkinson petrol vs natural gas) for any series element, judged on
efficiency and engine+aftertreatment+tank mass. S0 per ESC-6.

R32 — Vehicle Zero consistency flag: the payload-denominated metric
has not been applied to Vehicle Zero. It shall be, at WS7 or the next
Vehicle Zero baseline reissue, before any Vehicle Zero result is
described as an efficiency advantage. Not executed now.

R33 — Doctrine additions.
D13. Per-km efficiency flatters; per-payload judges. Every electrified
     candidate won 6-10% per km and gave 6-8% back in freight.
D14. Waste-heat recovery is a full-load technology; line-haul cruise
     is a part-load condition (~1/3 rated). Its mass is charged for
     five hours to harvest minutes on the mountain.
D15. Architecture is duty-indexed. Name the duty before the number
     means anything.

## Workstream states
Vehicle Zero: WS1-WS4 closed; KX, WS5, WS6 open (foreman tasking per
PM_COWORK.md; WS6 blocked from WS8's ledger until r2). WS7 not cut.
Vehicle One: WS8 RATIFIED-PROVISIONAL, r2 errata open. WS9 RELEASED.

## Model policy (unchanged): WS9 worker Opus; WS9 kill-verdict
adjudication Fable, lead-designated; WS8 r2 adjudication Opus.
