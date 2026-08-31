# PROJECT VOLT — BASELINE v5 (ratified 2026-08-30)

Supersedes BASELINE_v4.md. Disposes WS8 round 2 (verdicts final,
numbers still provisional, r3 ordered) and receives WS9 (four ADVANCE
verdicts, PROVISIONAL pending the lead-designated Fable adjudication
and the escalation rulings below). Vehicle Zero content carries.

## WS8 round 2 disposition
R35 — WS8 r2 accepted as progress: all thirteen r1 findings closed,
verdicts unchanged in code (S1 +0.73 / S2 +1.80 / S3 -5.26 / S4 -1.06
median; every worst corner deepened by the corrected cold model, S1
to -12.87%). Round-2 adjudication NOT CLEAN: B1 (blocking) — S3's
control law lets the engine fuel and compression-brake simultaneously
(5.67% of S3's nominal fuel burned while braking; ledger row high
~1.8x); M1-M4; seven minors. R3_DIRECTIVE.md issued. Verdicts are
unaffected: S3 is dead on capability and its fuel correction moves it
toward, not past, a bar it misses by >8 points. Numbers of record
remain PROVISIONAL until r3 closes; WS6 consumes only the r3 ledger.
R36 — DOCTRINE CORRECTION (from M2). D13 is restated: "S1, S2 and S4
won 6-10% per km on the paired per-seed statistic and gave 6-8% back
in freight; S3 won nothing per km." The former wording carried a
ratio-of-medians artifact into doctrine. Per-km claims are stated on
the paired statistic only.

## WS9 — VEHICLE ONE WAVE TWO (verdicts PROVISIONAL)
R37 — WS9's verdicts as reported: S6 zero-mass stack +7.50% design /
+7.26% control (0 kg payload cost) ADVANCE; S4' RE-BEV +11.95% /
-6.81% (-521 kg) ADVANCE; S5-13L minimal transmission +5.36% /
-1.38% (-949 kg) ADVANCE; S7 trailer axle +4.51% / -1.45% (-809 kg)
ADVANCE; S5 as ordered (11 L) +1.90% / -5.75% KILL; electric
turbocompound on the design duty +1.67% vs 2.5% DROPPED. These are
NOT ratified: no findings file exists for WS9, and its adjudication
is the lead-designated Fable seat (ADJUDICATION_DIRECTIVE.md). The
first-pass base rate in this program is five for five material-or-
blocking; ADVANCE verdicts get the same treatment as kills.
R38 — TRIP-TIME GATE, pre-committed before reading the table: an
ADVANCE additionally requires design-duty trip time <= +5% of S0R.
The metric of record stays energy per payload tonne-km; trip time
is a gate, not a term. Applied at ratification from the exported
`trip_time_the_metric_cannot_see` table.
R39 — Escalation dispositions (WS9):
ESC-1: (b)+(c). S6 advances CONDITIONALLY — no hardware decision
before an independent BSFC map — and its margin is exported at
47.0 / 48.0 / 49.2% peak BTE against the 0.4688 break-even. The lead
records plainly: S6 is an engine bet with ~2.3 BTE points of
headroom, not a drivetrain result.
ESC-2: Vehicle One's market is declared as the US West (California
corridors — Cajon, Tejon, Grapevine-class terrain); grid primary-
energy and CO2 factors to be sourced for that market; S4' stays
PROVISIONAL-ADVANCE with its flip point on the record.
ESC-3: confirmed — four corners gate the design duty (payload +/-20%,
-10 C with cold acceptance, 2,000 m / +45 C); the null grade-heavy
corner is dropped.
ESC-4: the ISO 8528-1 prime-power basis is RATIFIED for Vehicle One;
R18's transferred ratio is retired at semi scale.
ESC-5: S0R without preview is the ruler of record; predictive energy
management is RETIRED as a lever (D17).
ESC-6: the 2.2 / 1.0 kW cab-heat split is confirmed; S4' cab heating
to be modelled as an explicit electric load with its own bracket.
ESC-7: S5's specification is CONFIRMED without an engine-side launch
device; the fault asymmetry (inverter or machine fault = tow) is
accepted at prototype scope and joins the WS7-class test list
(R22c precedent). No mass added.
ESC-9: handled by R38.
ESC-8: concordance ordered in the adjudication; WS9 re-runs against
WS8 r3 sources when they land (one-flag operation per the pin).

## Doctrine additions
D16. THE THIRD WALL. A 2-speed engine path meets a constraint the
     two walls do not name: the low gear's coupling floor sits above
     the crawl speed a steep grade forces, so below it the engine is
     disconnected. Frontier: 6% grade on the 11 L, 8% on the 13 L,
     against a design duty carrying 10.7%. Vehicle Zero's 35 km/h
     idle floor was the same physics in miniature.
D17. Zero-mass levers are symmetric: anything the incumbent can fit
     must be fitted to the ruler too, and predictive energy
     management measured that way is worth ~0 (-0.09 to +0.03%).
D18. A plug-in candidate's verdict is a function of the declared grid
     factor; the flip point is part of the result, not a footnote.
D19. Preconditioning plus a waste-heat cab path closed the cold wall
     for engine-carrying candidates (all four cleared >=0% at -10 C);
     the lead's pre-registered "cold kills at least two" missed in
     the direction of the remedy working.

## Program hygiene
R34 — Every pipeline exports a 10 Hz trace file per run (feeds the
WS10 exhibit/simulator). WS5, WS9 re-runs, and all later work comply
from their next artifact.
R40 — COMMIT DISCIPLINE: WS8 r2 and WS9 are uncommitted in one tree.
Commit as two separate commits (WS8 r2 artifacts; WS9 artifacts),
each message naming the round and its adjudication status; push
main. Foreman or a Sonnet session. No artifact edits.

## Workstream states
Vehicle Zero: KX, WS5, WS6 open (WS6 waits for the WS8 r3 ledger).
Vehicle One: WS8 r3 open (Opus); WS9 Fable adjudication open;
WS10 (combination trial: S6's engine + S5-13L's two-speed + lean
motors; S6 + S7; interaction expected sub-additive) cut only after
WS9 ratifies. WS10-exhibit (simulator) after both build tracks close.
