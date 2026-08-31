# DAY_SHIFT — FOREMAN TASKING, 2026-08-31 (lead-issued)

Same foreman, same authority rules as NIGHT_SHIFT.md and PM_COWORK.md
(no ratifying, no escalation filtering, no baseline edits, no Fable,
flag conflicts). Read ../BASELINE_v6.md and MORNING_DIRECTIVES.md.

## First, hygiene
1. Commit WS8 r3 SCOPED to WS8_semi_architecture/ (15 modified + 4
   new files per the r3 session's own list). Commit anything else
   uncommitted per workstream, one commit each, messages naming round
   and adjudication status. Push.
2. Pin-lock check (R50) before every launch below: no worker may start
   while another workstream is simulating against a module the worker
   will modify.

## Then, in this order
3. WS8-R4 (MORNING_DIRECTIVES section) -> gate -> adjudicator ->
   bounce max 3 -> packet.
4. WS9-R2 only after WS8-R4 is clean and committed (it re-pins to
   those sources) -> gate -> adjudicator -> bounce max 3 -> packet.
   Do NOT launch the Fable adjudication; the lead launches it.
5. KX-R4 in parallel with 3 (different modules; check pins) ->
   gate -> adjudicator -> packet. On clean: launch WS6 on the KX r4
   Vehicle Zero ledger only.
6. WS11: if its r2 adjudication has not run, run it (Opus). Then
   WS11-R3 -> gate -> adjudicator -> packet.
7. WS5: continue its pipeline to packet.
CPU rule: at most two simulation-heavy jobs at once.

## Report
PM_LOG.md throughout; DAY_REPORT.md at the root when everything above
is packeted or NOT CONVERGED: status per workstream, headline numbers
verbatim with citations, every escalation verbatim, processes left
running (none). Commit, push, stop.
