# WS13 ASSIGNMENT — PUBLICATION: HOW THE TRIAL WAS RUN

**Rebound to BASELINE_v7_FREEZE.md and rescoped by the lead,
2026-08-31, on the principal's ratified thesis change. This
supersedes the earlier version of this file.**

Read `CLAUDE.md` and `../BASELINE_v7_FREEZE.md` first (it is the
governing state and lists the eight publishable claims with their
statuses), then `../LEAD_HANDOVER.md` (doctrine D1–D12),
`../LEAD_HANDOVER_v2.md`, then BASELINE_v0..v6 for the narrative arc,
then the reports, findings files and `../PM_LOG.md` as the citations
require.

---

## The thesis

**Primary claim: you can leverage AI agents to run trials and
experiments on novel engineering concepts without being an engineer —
and produce output that is falsifiable rather than merely fluent.**

The drivetrain work is the case study that gives the method something
real to have been about: actual physics, actual candidates, actual
kills. It is not the headline.

This inverts the previous scoping. **METHOD.md is now the spine and
the primary deliverable; FINDINGS.md is the case study.** README leads
with the method claim and uses the engineering results as evidence
for it.

### Two guard rails, ratified by the principal and binding on every file

1. **The method claim is "catches internal inconsistency" — never
   "catches wrong physics." Lead with this limitation, do not bury
   it.** What the record demonstrably caught: mislabelled
   constructions, statistics standing in for other statistics,
   unrun robustness claims, verdicts asserted beyond their evidence,
   interface members whose construction did not match their name.
   What the record has *not* demonstrated is catching a wrong
   physical model. Nothing here touched hardware; the ruler is
   uncalibrated by 31.69% against its own sourced anchor (ESC-1).
   **Consistency is not validity.** State it plainly and early, and
   the rest becomes credible.
2. **The boundary laws in FINDINGS stand as physics results in their
   own right**, with statuses exactly as v7 labels them. They are not
   demoted to mere illustrations of the method. Claims 1, 2, 5 and 6
   in particular are engineering contributions and are labelled
   RATIFIED (model-relative) by v7; render them as such.

### The honest framing

A program that killed its own favourite ideas on criteria written
before the numbers existed, and mostly explained why the industry
looks the way it does. That is the story. It is also the only framing
that survives a hostile reader.

---

## Deliverables (repo root unless stated)

### 1. METHOD.md — the spine

Written for people building AI-run engineering programs. How the
trial was run:

- pre-registration in a separate context (D2); pre-committed kill
  criteria (D1); foreman/lead separation with disk as the only
  interface; fresh-context disk-only adjudication (cite
  `.claude/agents/ws-adjudicator.md` and `.claude/agents/ws-worker.md`);
  three-way verification and the R14 export discipline; bounded
  rework rounds with NOT CONVERGED as a legitimate outcome.
- **The defect record, with numbers.** Every first-pass adjudication
  in the program — WS1–WS4, WS8, WS9, WS11 — returned material or
  blocking findings. Seven for seven, including on the lead's own
  work. Cite each.
- **The natural experiment.** On 2026-08-31 at 07:40 the principal
  cut the WS11 r2 and WS5 adjudication rounds (`../PM_LOG.md`, final
  entry). WS11 r2 closed 3 blocking + 8 material + 13 minor findings
  and nothing checked that work; the +20.11% headline therefore
  stands on unverified rework. Present this as the **control
  condition**, not as an embarrassment: remove the structure and the
  output is immediately unverified. It is the strongest single piece
  of evidence that the structure is what is doing the work.
- **The role the principal actually played.** Engineering training
  was not required. Physics literacy to read mechanisms was. Most
  importantly, enforcing structure against one's own impatience was:
  separate contexts, no self-ratification, criteria written first,
  adjudicators that cannot be argued with. Say this honestly — the
  strong version of "without being an engineer" is the true one and
  the weak version is not.

### 2. METHOD.md § FAILURE MODES CATALOGUE — required section

Each entry: the failure mode, the instance in this record that
produced it (with file and citation), and the countermeasure that
caught it. At minimum:

- **Partial correction.** The same defect family — a machine-readable
  field whose *construction* does not match its *name* — was fixed and
  reintroduced by the fix across three consecutive KX rounds. R36's
  defect class was corrected as `m6` and reappeared in three new
  blocks in the same round (`../PM_LOG.md`, KX ADJ-DONE r2, 05:01).
  *Countermeasure:* order a sweep for the defect **family**, not the
  named instances, and require the sweep to report where it found
  nothing as well as where it found something. The r3 sweep then found
  two further instances the adjudication had not named.
- **Statistic-of-statistics.** Ratios of ensemble statistics labelled
  as paired per-case medians; a bracket figure that flipped sign
  (KX2-M3). *Countermeasure:* R36's paired per-seed rule, and
  verifiers that re-derive the construction rather than trusting the
  label.
- **Self-ratification drift.** The structural failure mode the whole
  foreman/adjudicator architecture exists to prevent: no layer below
  the lead may ratify, filter escalations, or touch the baseline.
- **False clean-certifications.** The KX r3 sweep certified sixteen
  areas examined-and-clean; spot-checking found **two of them false**,
  including one block containing the very defect it certified clean
  (`../PM_LOG.md`, KX ADJ-DONE r3, 06:49). *Countermeasure:* a sweep's
  clean certifications are themselves auditable claims and must be
  sampled, never accepted.
- Any further modes the record supports. Do not invent one to round
  the list out.

### 3. FINDINGS.md — the case study

The eight claims as results: statement, status (**exactly as
`BASELINE_v7_FREEZE.md` labels it** — RATIFIED / PROVISIONAL / KILL,
rendered as FROZEN-<status> where v7 does), evidence files,
reproduction command, and what would change the claim (the pending
conditions or brackets). Written so a drivetrain engineer can check
every line.

Two facts that `BASELINE_v7_FREEZE.md` does not currently carry and
that FINDINGS **must**, both from `../WS11_vehicle_zero_ruler/REPORT_WS11.md` §0:
V1's governing corner falls to **+3.66%** when ESC-2 and ESC-4 apply
together; and the harshest cab-heat reading takes V1's governing
corner **negative**. Do not edit the baseline — carry these in
FINDINGS and LIMITATIONS with their citation.

### 4. README.md — the front door

Two layers per chapter (one plain-language paragraph, then the
numbers). Lead with the method claim and its limitation, then:
Premise → Vehicle Zero → The Clutch Trial (G1: +6.26% under one
convention, −2.58% under the corrected one; the kill executed) → The
Pivot → The Semi Walls (mass, ratio span, cold, the third wall) →
The Delivery Truck on the Honest Metric (V1 +20.11% FROZEN-PROVISIONAL,
V2 FROZEN-KILL) → What Survived and What Didn't → The Open Frontier
(R54). Link the exhibit.

### 5. LIMITATIONS.md — unsparing

No hardware. Uncalibrated ruler (ESC-1, 31.69% below its own sourced
anchor). Model-relative verdicts. Declared brackets. Provisional
statuses at freeze. Single-machine simulation. The frozen open
findings (PRE-B1..B3, WS8 r3 B1/B2, KX radiator sizing 103.5 vs
95.0 kW). The 07:40 unverified rework. And the method's own boundary:
internal consistency, not physical validity.

### 6. REPRODUCE.md

One command per workstream, the verifiers, the determinism checks,
the requirements files.

### 7. Licences and hygiene

`LICENSE` (Apache-2.0 for code) and `docs/LICENSE` (CC BY 4.0 for
prose and data). Strip `.venv/`, `__pycache__/`, and
`data/_checkpoint.json` files from the tree and add them to
`.gitignore`. **No `.gitattributes`/LFS work is required** — the lead
verified GitHub's limits: recommended 1 MB per file, enforced at
100 MB, warning above 50 MiB; the largest file in this tree is
10.22 MB and the working tree is ~139 MB, well inside the ~1 GB
repository recommendation. Keep every findings file, PM log, baseline
and erratum in the tree — they are the evidence.

## Rules

Every number cited to file + JSON path or report line. No adjectives
that do work a number should do. Do not edit any report or baseline.
Nothing you write may promote a status.

**Exit:** launch `ws-adjudicator` (Opus) on this folder for a citation
check only — every claim in README / METHOD / FINDINGS resolves to the
record and carries the right status. This is publication QA, not a
research round; it disposes of nothing. Fold its findings, then stop.
