# WS4 G1-R DIRECTIVE — RECOMPUTE THE GATE UNDER THE RULED CONVENTIONS

Lead-issued, bounded rework order. Read ../BASELINE_v2.md first
(rulings R10, R11, R12, R18 and the G1 provisional status), then
WS2_traction_motor/REPORT_WS2.md §7 and its r4 outputs when they land
(the r4 maps at 432/662/749 V are your traction chain of record — if
you start before r4 finishes, build the pipeline to hot-swap the map
files and state which vintage you ran).

## Scope (exhaustive)
1. Recompute all G1 margins (nominal, CdA 5.4, 4 kW aux, hot-alone,
   2,000 m + 45 C corner; 8-seed ensemble) with:
   a. R12 chain convention on BOTH modes: genset-side PE/rectifier in
      your ledger; traction side = WS2 measured maps x 0.97 reduction;
      no scalar PE member; all quantities bus-side. Your line-111
      exclusion set shrinks accordingly — document each removal.
   b. PM spin drag CHARGED TO CASE (a): use WS2's exported r4 member
      (their r3 figure was 1.49 kWh engine-side + 0.50 kWh bus-side
      per VOLT-REG at 370 V; expect the r4 value to differ). Your
      mode-neutrality claim is superseded — WS2's measurement
      distinguishes unloaded lockup spin from loaded series operation.
   c. Generator/rectifier spec restated on the R10 window (662.4 V
      nominal); pinned points re-placed if the rectifier stage moves
      them.
2. Report margins in the same condition table as before, ensemble
   envelopes (R9), interface exporting the full condition set (your
   F2 fix pattern). The kill criterion is unchanged: >=5% nominal
   ensemble-min. Report the number; the lead executes or spares.
3. Sensitivity of the margin to the spin-drag member alone and to the
   map-vs-scalar swap alone (two one-factor rows), so the record shows
   which correction moved it.
4. Datasheet confirmation task (R18 blocker): state precisely which
   figures on the 4HK1-V2C require procured-datasheet confirmation and
   what test substantiates the 132 kW flat-rating if the datasheet is
   silent.

## Exit
Deterministic regeneration; REPORT_WS4.md updated with a G1-R
changelog; launch ws-adjudicator on this folder and STOP. The lead
reviews findings directly.
