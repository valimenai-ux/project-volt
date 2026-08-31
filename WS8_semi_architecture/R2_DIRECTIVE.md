# WS8 ROUND 2 DIRECTIVE — ERRATA AND RE-RUN (lead-issued 2026-08-30)

Read ../BASELINE_v4.md first (rulings R25-R33), then FINDINGS_WS8_r1.md
in this folder. The verdicts (all four kills, WHR drop) are EXECUTED
and are not reopened by this round; this round makes the numbers of
record correct. Runnable, deterministic, byte-stable as always.

## Scope (exhaustive)
1. F2 (blocking): wire `Pack8.p_cont_chg_kw_at()` / `COLD_CHG_FACTOR`
   into every dispatch path for the -10 C corner (S1, S2, S3, S4,
   series_dispatch, S3 SOC loop). Re-run the cold corner, 8 seeds.
   Restate every exported worst-case field it governs. State plainly
   in the changelog which direction each candidate moved.
2. F1 (blocking): rebuild `heat_ledger_WS6` per R14 — the case set must
   include the simulated descent peaks (314.6 / 503.4 / 284.1 kW) as
   enumerated members with the governing case labeled; separate
   compression-brake heat from resistor heat by physical location.
   WS6 does not consume this ledger until this round closes.
3. F3, F4, F5, F6 (material): apply the adjudicator's corrections
   (S2 engine dual-use, charge-sustaining credit direction, R22(d)
   spin-drag member placement incl. S3 double-count, part-load
   pricing of unserved/stored energy) and re-run nominal + corners.
   Report the S1-vs-S2 ordering AFTER these corrections with one-
   factor rows, since they decide it. Confirm verdicts unchanged
   against the criteria (expected; if any flips, STOP and report —
   do not touch the verdict).
4. F7 (material): restate the S0 grade-zeroed cross-check as an
   ensemble (min/median/max) against the ICCT band, not a median.
5. F8-F13 (minor): checker-pinned errata set; note F12 — state the
   ratio ceiling as a physics bound (rpm ceiling at 105 km/h), not a
   swept-grid property, and F11 — either exercise `derate_factor` in
   an added 2,000 m / +45 C corner (R28) or remove the provenance
   claim.
6. Interface: verdicts block marked `status: executed_kill_2026-08-30`;
   numbers block versioned r2; SHA-pin inputs.

## Exit
Regenerate; changelog; launch ws-adjudicator (round 2, Opus is
sufficient — verdicts are closed) and STOP.
