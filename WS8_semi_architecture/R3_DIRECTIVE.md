# WS8 ROUND 3 DIRECTIVE — CLOSE B1 AND THE STATISTIC DEFECTS (lead-issued 2026-08-30)

Read ../BASELINE_v5.md, then FINDINGS_WS8_r2.md in this folder. The
four kills and the WHR drop are EXECUTED and closed; this round makes
the numbers and the heat ledger correct. Opus is sufficient.

## Scope (exhaustive)
1. B1 (blocking): make combustion and compression braking mutually
   exclusive on ONE rule for every candidate (S0's overrun cut-off is
   the template); gate through-the-road charging on the VEHICLE NOT
   BRAKING, not on axle-A force being small; extend
   `heat_closure_check` to `simulated_worst_run` and assert per run
   that no sample carries both compression-brake power and positive
   shaft power. Re-run S3 and S2 on all corners, 8 seeds. Report S3's
   fuel change with a one-factor row (expected: S3 improves by
   several percent and remains far below the bar; it is dead on
   capability regardless — if its nominal ensemble-min crosses +3%,
   STOP and report, do not touch the verdict).
2. M1: delete every hand-written direction string; generate F3/F6
   directions from the one-factor table.
3. M2: per-km bullets on the PAIRED per-seed statistic, labeled;
   generate the "every candidate" sentence from data (it is false for
   S3 on 2 of 8 seeds and at the ratio-of-medians).
4. M3: state explicitly what the R28 corner derates (engine only) and
   scope any conclusion drawn from it accordingly.
5. M4: restate ESC-WS8-1 with both halves of the cell-substitution
   direction; note that S4' has already run in WS9 on energy cells.
6. Minors as a checker-pinned errata set.
7. Interface: numbers block versioned r3; verdicts block unchanged
   (`status: executed_kill_2026-08-30`); heat ledger versioned r3 —
   WS6 consumes ONLY the r3 ledger.

## Exit
Regenerate; changelog generated, not written; launch ws-adjudicator
(round 3, Opus) and STOP. Do not commit — the foreman commits.
