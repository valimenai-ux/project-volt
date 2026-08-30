# Project Volt — orientation for fresh clones

This repository is the program record of Project Volt. If you are a
Claude Code session (local or cloud) starting work here, orient as
follows before touching anything.

## Authority

- The **highest-numbered `BASELINE_v*.md` at the repository root is
  authoritative**. Read it in full before any work. Lower-numbered
  baselines are history, superseded except where the current baseline
  says otherwise.
- Work arrives as **`WSn_*/ASSIGNMENT.md`** or **`*_DIRECTIVE.md`**
  files. Execute them **exactly as written** — assignments and
  directives are bounded orders: do what is ordered, nothing else.

## Binding program rules

1. **Deterministic pipelines.** Fixed seeds, one entry point per
   workstream (`run_wsN.py` pattern), a `requirements.txt`, and
   byte-stable regeneration: re-running the pipeline must reproduce
   every committed artifact byte-identically.
2. **Reports.** Each workstream reports as `REPORT_WSn.md`, carrying a
   machine-readable interface block whose headline numbers verify
   **verbatim** against the workstream's results data file (a
   `verify_*.py` asserts this; nothing is transcribed by hand).
3. **R14 export discipline.** Every machine-readable worst-case field
   is an explicit max/min over an enumerated case set, with the
   governing case labeled inline.
4. **Ensembles.** Stochastic extrema are 8-seed ensemble envelopes.
5. **Part-load models, never peak-point scalars.**
6. **Electrical quantities are stated bus-side** unless explicitly
   labeled otherwise.
7. **Rejected heat** is reported by component and case for the WS6
   ledger.
8. **Escalations** cite the ruling they challenge and are **never
   self-resolved** — they go to the lead.
9. **Exit protocol.** Finish by launching the **ws-adjudicator** agent
   on your own workstream folder, then **stop**. The adjudicator's
   findings file is for the lead; do not act on it yourself.
10. **Never modify** BASELINE files, other workstreams' artifacts, or
    findings files. Read other workstreams' exports read-only.
11. **The project lead ratifies in a separate chat.** Nothing in this
    repository is ratified by a workstream session.

## Agents

`.claude/agents/ws-worker.md` (executes one workstream assignment
exactly as written) and `.claude/agents/ws-adjudicator.md`
(fresh-context adversarial reviewer; reads artifacts from disk only,
never edits work product) are part of the program record and must be
present in every clone.
