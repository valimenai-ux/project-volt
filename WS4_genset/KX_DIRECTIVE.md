# WS4 KX DIRECTIVE — EXECUTE THE KILL'S CONSEQUENCES IN THE RECORD

Lead-issued, bounded order. Read ../BASELINE_v3.md first (the kill is
executed; rulings R22, R23). This directive does three things: corrects
the record (R23 errata), verifies the pure-series consequence (R22a),
and re-states the interface for a program with no gate and no clutch.

## Scope (exhaustive)
1. R23 errata: fix adjudication F1 (CdA 5.4 positive-seed count — four
   of eight — in all four locations), F2 (boundary-convention
   mode-neutrality claim at CdA 5.4, ~0.05 pp), F3 (vintage-spread
   0.63 pp as printed), F4 (traction-map path resolution made
   consistent with sibling fields), F5 (state the 0.9005 chain figure's
   duty weighting and add the series-duty ~0.916 companion). Pin each
   in verify_ws4.py. No re-adjudication; checker verification
   suffices per the adjudicator's characterization.
2. R22a verification run — pure-series V2 at the DELIVERED pack:
   VOLT-REG nominal, CdA 5.4, and the 2,000 m/+45 C corner; 8-seed
   ensembles; 11.08 kWh usable at the bus; R16 cold curves
   (regen_acceptance.csv); R10 window; WS2 r4 maps (SHA-pin the
   inputs as you did for G1-R). Export per seed and envelope:
   unserved bus energy (expected zero — if nonzero, that is a
   finding, not a tuning knob), above-pin duty seconds, SOC
   trajectories, genset on/off or load-point cycling rate, and fuel
   energy per km. These are WS5's design inputs for the highway
   dispatch question (R22b) — label the block `series_duty_v2` in the
   interface.
3. Interface restatement: `gate_g1` becomes an ARCHIVED record block
   (verdict, attribution rows, bracket result, provenance hashes) with
   an explicit `status: executed_kill_2026-08-30`; no field of it may
   be consumed as a live requirement. Add the R22d spin-drag
   operational note as a named member for WS5.
4. Changelog the report (KX section). Deterministic regeneration and
   byte-stability as always.

## Exit
Launch ws-adjudicator on the folder (its scope: the errata pins, the
series_duty_v2 block, and interface consistency — a light round), place
its findings if the harness refuses the write, and STOP.
