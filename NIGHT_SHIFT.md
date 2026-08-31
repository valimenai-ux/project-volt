# NIGHT_SHIFT — OVERNIGHT FOREMAN TASKING (lead-issued 2026-08-31)

You are the night-shift foreman: Claude Code at the repo root, Opus.
PM_COWORK.md's authority rules bind you verbatim: you launch, gate,
adjudicate, bounce, package, commit, and log; you never ratify, never
resolve or soften an escalation, never edit BASELINE/ASSIGNMENT/
DIRECTIVE/agent files, never reconcile conflicts, never use Fable.
Workers Opus; mechanical gates and commits Sonnet is fine.

## Track A — Vehicle One (sequential; do not touch WS8 until step A1)
A1. WS8 round 3 is running in another session. Completion = its
    FINDINGS_WS8_r3.md exists AND `pgrep -f run_ws8` is empty AND no
    adjudicator process is alive. Poll every 10 minutes. Until then,
    nothing in WS8_semi_architecture/ is read or written by you.
A2. On completion: commit WS8 (r2 and r3 together if r2 was never
    committed separately — say so in the message). Push.
A3. WS9 re-run against r3 sources — the one-flag re-pin ESC-WS9-8
    describes: update the sha256 pin table, re-run all corners x 8
    seeds, regenerate report, verify, determinism; changelog entry
    "r3-concordant re-run". Commit. This is the WS9 record the
    lead's Fable adjudication will judge in the morning; do not
    launch that adjudication yourself.
A4. If it is before 06:00 local when A3 lands: run ws-adjudicator
    (Opus) on WS9 as a pre-adjudication round, persist findings
    verbatim if the harness refuses the write, commit. Otherwise
    skip.

## Track B — Vehicle Zero (starts immediately; different modules)
B1. KX: ws-worker on WS4_genset/KX_DIRECTIVE.md -> mechanical gate
    -> ws-adjudicator -> bounce with findings, max 3 rounds ->
    PM_PACKET_KX.md.
B2. WS11 (the night's headline): ws-worker on
    WS11_vehicle_zero_ruler/ASSIGNMENT.md, hot-swapping KX's
    series_duty_v2 when available -> gate -> adjudicator -> bounce
    max 3 -> PM_PACKET_WS11.md.
B3. WS5: ws-worker on WS5_controls/ASSIGNMENT.md -> same pipeline ->
    PM_PACKET_WS5.md.
B4. WS6: ws-worker on WS6_packaging/ASSIGNMENT.md, Vehicle Zero
    scope; it may ingest Vehicle One heat-ledger rows only from WS8
    r3 after A2 -> same pipeline -> PM_PACKET_WS6.md.
CPU rule: at most two simulation-heavy jobs at once (B2 and A3 are
heavy). Preferred order: B1 -> B2, then B3 and B4 in parallel; A3
runs when a slot is free.

## Record hygiene
Commit after every gate result, packet, bounce, and log line; push
main. PM_LOG.md timestamped throughout. Before stopping, write
NIGHT_REPORT.md at the root: what completed, what is ready for
ratification, headline numbers copied verbatim with file+line
citations (you add none of your own), every escalation verbatim,
anything NOT CONVERGED with its trail, and every process you leave
running (leave none). Commit, push, stop.
