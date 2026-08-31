# WS9 ADJUDICATION DIRECTIVE — FABLE ROUND (lead-designated 2026-08-30)

This is the lead-designated Fable adjudication of Vehicle One's first
ADVANCE verdicts (BASELINE_v5 R37). The session running this file is
only the harness: launch the ws-adjudicator agent on
WS9_vehicle_one_wave2/ under FABLE, pass it the lead-priority targets
below on top of its standing mandate, persist its findings verbatim
as FINDINGS_WS9_r1.md if the harness refuses the agent's write, and
STOP. No commits.

## Lead-priority re-derivation targets
1. Every ADVANCE margin on the design duty and at every R28 corner,
   reproduced from per-seed data (paired, ensemble-min) — S6, S4',
   S5-13L, S7 — and the S5-11L kill.
2. S6's dependence on the cited 49.2% peak BTE: re-read the verdict
   at 47.0 / 48.0 / 49.2% against the 0.4688 break-even; confirm
   predictive energy management contributes ~0 so the margin IS the
   engine.
3. S4': reproduce the grid-factor sweep and the exact flip point
   (+50% -> -0.38% is reported); confirm all other candidates are
   invariant to the factor.
4. S5's THIRD WALL: re-derive in closed form the low-gear coupling
   floor vs crawl speed on 6% / 8% / 10.7% grades for the 11 L and
   13 L; confirm the 6%/8% frontier and that S5-13L's fuel result
   on the design duty is earned with the engine disconnected on the
   steepest grades (motors within their buffer), not assumed coupled.
5. B1-CLASS CHECK (from WS8 r2): search S5 and S7 (S7 is through-
   the-road by construction) for any sample carrying both
   compression-brake power and positive engine shaft power, and any
   through-the-road charging during braking. Report the fraction of
   fuel on such samples per candidate and corner.
6. R30 cold wall: confirm preconditioning energy and the 2.2/1.0 kW
   cab-heat split are CHARGED to the candidates that use them, that
   pack temperature is a state, and that S4' (no engine heat) is
   treated consistently.
7. Trip time: extract `sanity.trip_time_the_metric_cannot_see` per
   candidate and duty; the lead has PRE-COMMITTED a trip-time gate of
   <= +5% vs S0R on the design duty as an additional advance
   condition — report each candidate's ratio, do not apply the gate.
8. ESC-WS9-8 concordance: field-by-field against WS8 r2 artifacts;
   note that WS8 r3 (B1 fix) will move the pinned sources again and
   state which WS9 imports are affected.
9. Heat ledger closure, determinism (re-run, do not trust the
   checkpoint), interface three-way integrity, 397-check verifier.
