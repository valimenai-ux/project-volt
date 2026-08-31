# WS12 ASSIGNMENT — THE EXHIBIT: THE METHOD, MADE CLICKABLE

**Rebound to BASELINE_v7_FREEZE.md, 2026-08-31, by the lead. This
supersedes the v6-era version of this file.** The program's research
track is FROZEN. This workstream and WS13 are the only live work.

Read, in order: `CLAUDE.md`, `../BASELINE_v7_FREEZE.md` (the governing
state — it lists every verdict's frozen status and the eight
publishable claims), `../TRACE_SCHEMA.md`, `../LEAD_HANDOVER.md`
(doctrine D1–D12), and the design draft in `design/`.

The draft ships as `design/Pending replay submission.zip`. Unzip it
in place, then `git rm --cached` the zip and delete it, so `design/`
holds the extracted source and not the archive. The draft is a
dc-runtime prototype ("Project Volt Exhibit.dc.html" + support.js)
with a strong visual system, a three-tier badge discipline (RECORD /
DERIVED / SANDBOX), a provenance strip, and working logic for the
sandbox ratio window, the G1 waterfall and a SYNTHETIC trace
generator. **Keep the look and the discipline; replace everything
synthetic with the record.**

---

## What this exhibit is for

The program's thesis is not "we designed a better truck." It is:
**an engineering trial can be run by AI agents, on a real physical
question, by a principal who is not an engineer — and the output can
be made falsifiable rather than merely fluent.**

The exhibit is that claim made executable. A visitor should be able
to click any number and watch it resolve to a file and a JSON path.
The badge discipline and `exhibit_verify.py` are therefore not
polish — they are the product. An exhibit that displayed one
unverifiable number would refute the thing it exists to demonstrate.

Two guard rails bind every screen and every string of copy:

- **The method claim is "catches internal inconsistency," never
  "catches wrong physics."** No hardware was ever built. The ruler is
  uncalibrated (ESC-1). Any copy that implies validation against
  reality is false and must be cut.
- **No status is ever promoted.** Every verdict renders exactly as
  `BASELINE_v7_FREEZE.md` labels it: `FROZEN-PROVISIONAL`,
  `FROZEN-KILL`, `FROZEN-RATIFIED`, `NOT CONVERGED`, `NOT CUT`. The
  strings `PROVISIONAL` and `RATIFIED` alone are forbidden in badge
  positions; they were the v6-era labels and the record has moved.

## Principle

Every number of record on screen resolves to a JSON path in a results
file; every replay is a trace file on disk; every screen's provenance
strip is READ from the record (baseline version, results sha, seed,
corner), never hard-coded. If a figure is not traceable to a file, it
is not shown as a result. "A dashed baseline, never a zero line."

## Build

Port to a standard static web app (Vite + React + TypeScript, no
server) in `WS12_exhibit/app/`, deployable to GitHub Pages at
`https://valimenai-ux.github.io/project-volt/`. Set Vite's `base` to
`'/project-volt/'` — the app lives at a repo subpath, and a wrong
base is the single most common cause of a blank deployed page.
Preserve the draft's typography, palette, layout, badges, and copy
where the copy is true; correct it where the record has moved (the
draft says BASELINE v4; the record is **v7 and frozen** — bind it,
and this time it will not move again).

---

## Screens

### 1. Verdict wall — THE FRONT DOOR

Promoted from last screen to first by lead ruling, 2026-08-31. This
is what a visitor sees before anything else, because it is the most
persuasive object in the program: a pre-committed criterion killing
the program's favourite idea.

Cards generated from results files, each with its status badge and
file+path citations:

- **The G1 waterfall** (`WS4_genset/results_ws4.json`, archived
  `gate_g1` block, `status: executed_kill_2026-08-30`). Lead with it.
  +6.26% under one convention; −2.58% under the corrected one; the
  clutch deleted. The card's copy must make plain that the criterion
  was written *before* the number existed and could not be
  renegotiated (D1).
- **The WS8 paired-bar chart** (`WS8_semi_architecture/results_ws8.json`)
  — S1–S4 KILLED (final), WHR DROPPED (final), numbers FROZEN at r3
  with r3's adjudication NOT CLEAN and r4 never run. Say so on the
  card.
- **The duty sign-flip** — the same architecture wins on stop-go and
  loses on regional duty.
- **The WS11 pair** (`WS11_vehicle_zero_ruler/results_ws11.json`) —
  V1 Postal FROZEN-PROVISIONAL ADVANCE, V2 Trucker FROZEN-KILL.

### 2. Race mode (RECORD REPLAY, PAIRED SEED) — the metric lesson

Two traces with identical (duty, corner, seed). **First dataset,
WS11:** V1 Postal vs the stock NPR ruler on VOLT-SUB seed 11 nominal,
then cold −10 °C; V2 vs ruler on VOLT-REG seed 23 and the 10 km climb.

**The dual counter is the point of this screen and is mandatory.**
Run a per-km energy counter and a per-payload-tonne-km counter side
by side, live, so the visitor watches them diverge: V2 wins **+8.41%
per km** and hands back **16.19 points of freight** to get there
(`WS11_vehicle_zero_ruler/REPORT_WS11.md` §0). That divergence is the
D13/R36 trap the payload metric exists to catch, and seeing it happen
in real time is worth more than any paragraph about it.

Verdict resolves at the finish line from `results_ws11.json`'s paired
per-seed margin for that seed, with the ensemble-min verdict of record
beside it and its frozen status badge read from the interface block.
The semi race (WS8/WS9) is wired but renders FROZEN-PROVISIONAL.
Never show a verdict the baseline has not executed as if final.

### 3. Round history — NEW SCREEN, mandatory

The failure record is the program's strongest evidence, and it has no
screen. Build one. Per workstream, from the findings files and
`../PM_LOG.md`:

- rounds run; the adjudication verdict each round (CLEAN / NOT CLEAN
  with counts by severity); what closed at root cause; what did not.
- **KX: NOT CONVERGED after three rounds.** Its blocking R3-B1 shown
  with the number — 103.522 kW two-minute radiator maximum against
  R20's 95.018 kW design point at the same ambient, +8.95%.
- **WS11 r1: NOT CLEAN, 3 blocking / 8 material / 13 minor**, with
  the fact that the adjudicator falsified the report's own robustness
  sentence about its own KILL.
- **WS11 r2: reworked, UNCHECKED.** Render the 07:40 gap honestly and
  prominently: on 2026-08-31 the principal cut the r2 adjudication;
  r2 closed 3 blocking + 8 material + 13 minor findings and nothing
  verified that work. Label it what it is — **the control condition**:
  remove the structure and the output is immediately unverified. This
  card is not an embarrassment to be minimised. It is the experiment.
- The seven-for-seven first-pass defect rate, including defects found
  in the lead's own work.

An exhibit that displays its own weakest joint is doing the thing the
program claims. If any instinct arises to soften this screen, that
instinct is the failure mode; render it plainly.

### 4. Simulator (RECORD REPLAY)

Loads TRACE_SCHEMA files; play/pause/scrub/speed; elevation profile
from `z_m`; power-flow diagram with width = sqrt(kW) driven by the
trace's electrical columns and the R15 blend order; SOC and pack
temperature; the engine dot on the BSFC map (rpm × torque from the
trace, map from WS4's exported maps at `WS4_genset/data/bsfc_map_*.csv`);
fuel counters (litres, L/100 km running, MJ per payload tonne-km
running from header payload); 8-seed ribbon when all seeds exist,
absent (dashed) when not.

**Decimated-replay rule (lead ruling, 2026-08-31).** The traces are
2.6–10.2 MB each; the largest in the tree is 10.22 MB
(`WS5_controls/data/trace_v2_load_follow_nominal_seed23_10Hz.csv`).
No such file may be fetched whole on page load. Therefore:

- **Scrub tier: 1 Hz.** Decimate at build time to a 1 Hz whole-trace
  index. Decimation is by strided sample, never by averaging —
  averaging would invent samples that are not in the record.
- **Detail tier: 10 Hz, fetched per viewed segment.** Pre-split the
  10 Hz traces into segment chunks at build time; fetch only the
  segment in view.
- **On-screen badge, verbatim, whenever the 1 Hz tier is displayed:**
  `the replay is decimated; the record is not`. It must cite the full
  10 Hz file path beside it.
- **Only the traces the exhibit actually replays are published** —
  the WS11 set (~35 MB) plus any others a screen genuinely needs.
  Every other trace stays in the repo, linked by path, not served.
  Publishing 123 MB of traces to Pages is not required and will not
  be done.

### 5. Sandbox

Keep the draft's ratio-window logic, but re-derive its constants from
WS1's ratified road-load parameters and WS8's engine-rpm ceiling,
with a unit test that reproduces the S3 feasibility result (3.60:1
ceiling, ~half the grade force) from the same function. Badge and
disclaimer unchanged. This is the only screen where the visitor's
input drives the numbers, and it must stay marked SANDBOX throughout.

---

## Verification (the part that makes it ours)

`exhibit_verify.py`: enumerates every number-of-record rendered by the
app (a manifest the app emits at build time) and asserts each resolves
to its cited JSON path and formats to the displayed string — the same
discipline as `verify_ws11.py`. It must additionally assert that **no
badge string in the manifest is a promoted status**: any occurrence of
a bare `RATIFIED` or `PROVISIONAL` in a badge position fails the
build.

Trace loader validates TRACE_SCHEMA (header keys, column presence,
blend-order sum rule) and refuses nonconforming files with a visible
reason rather than plotting them. The decimation step emits a
manifest row per trace recording source path, source sha256, stride,
and output row count, and `exhibit_verify.py` checks every 1 Hz file
is a strict subsequence of its 10 Hz source.

Determinism: build twice, diff the bundle.

## Report

`REPORT_WS12.md`: what was ported and what was replaced; data
bindings table (screen element → file → path); verify results; a list
of every draft element that had to be cut because the record cannot
feed it (**cut the element, not the rule**); escalations citing
rulings. Under the freeze there is no workstream to escalate to — so
record any such item in the report and in `LIMITATIONS.md` via WS13,
and **never synthesize a missing column**.

**Exit:** launch `ws-adjudicator` (Opus) on this folder for a
citation and artifact check only — every rendered number resolves to
its cited path, every status matches v7's label, no synthetic data
survives, the decimation manifest checks out. This is publication QA,
not a research round; the adjudicator disposes of nothing and moves
no verdict. Fold its findings, re-run verify, then stop.
