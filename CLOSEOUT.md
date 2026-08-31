# CLOSEOUT — PROJECT VOLT, FINAL WAVE

**Issued by the lead, 2026-08-31, on the principal's ratified
close-out decision. This is the last directive of the program.**

You are the close-out foreman. This directive must run **end to end
without the principal**. He has moved to other work. Do not stop to
ask him anything unless you hit a **hard blocker** as defined in §9.

Authority rules from `PM_COWORK.md` and `PM_FOREMAN.md` still bind
with one narrowing and one widening:

- **Narrowing:** you ratify nothing, promote no status, edit no
  baseline, edit no report, and reopen no research. The research track
  is FROZEN by `BASELINE_v7_FREEZE.md`. R51–R54 are absolute.
- **Widening:** the lead has delegated the small calls inside v7's
  rules to this session. You may make design, packaging and sequencing
  decisions and record them. You may **not** make decisions that
  change what the record says.

Model policy: **Opus** for the WS12 and WS13 workers and for both
citation-check adjudicators. **Sonnet** for mechanical work — git
hygiene, stripping, decimation, build plumbing, link verification.
**No Fable, at any point, for any reason.**

Log every step to `PM_LOG.md` in the existing format as you go. If
the run dies partway, `PM_LOG.md` must be enough for a successor to
resume without guessing.

---

## 0. The two guard rails, binding on every step below

1. **The method claim is "catches internal inconsistency," never
   "catches wrong physics."** No hardware was built; the ruler is
   uncalibrated (ESC-1). Any copy in any deliverable implying
   validation against reality is false — cut it.
2. **No status is ever promoted.** Every verdict renders exactly as
   `BASELINE_v7_FREEZE.md` labels it. A bare `RATIFIED` or
   `PROVISIONAL` in a badge position is a build failure, not a style
   preference.

---

## 1. Hygiene first (Sonnet)

1. The design draft has already been staged by the lead at
   `WS12_exhibit/design/Pending replay submission.zip` (moved from
   the repo root with the Filesystem MCP, outside git — git will see
   a root deletion and an untracked addition; stage both). Unzip it
   in place, then delete the zip so `design/` holds extracted source
   only.
2. Strip from the tree and add to `.gitignore`: `.venv/`,
   `__pycache__/`, `*.pyc`, `data/_checkpoint.json`,
   `.DS_Store`. The checkpoints are large
   (`WS9_vehicle_one_wave2/data/_checkpoint.json` is 4.06 MB,
   `WS8_semi_architecture/data/_checkpoint.json` 2.88 MB) and are
   intermediate state, not evidence.
3. **Keep every report, findings file, baseline, PM packet and log.**
   They are the evidence and the publication cites them.
4. Merge every outstanding branch into `main` as one clean history.
   Resolve conflicts in favour of the committed record; if a conflict
   would change a number, stop — that is a hard blocker (§9).
5. Push. Confirm `main == origin/main` before proceeding.

## 2. WS12 — the exhibit (Opus worker)

Launch a `ws-worker` on `WS12_exhibit/ASSIGNMENT.md`, which the lead
rewrote today and which is authoritative. It is bound to
`BASELINE_v7_FREEZE.md`. Non-negotiable elements:

- **Verdict wall is the front door** (G1 waterfall first).
- **Race mode carries the dual counters** — per-km and
  per-payload-tonne-km side by side, diverging live.
- **Round-history screen exists** and renders the 07:40 gap honestly
  as the control condition.
- **Decimated-replay rule** enforced: 1 Hz strided scrub tier, 10 Hz
  per viewed segment, on-screen badge `the replay is decimated; the
  record is not`, and only the traces a screen actually replays get
  published.
- Vite `base` set to `'/project-volt/'`.
- `exhibit_verify.py` passes, including the promoted-status check and
  the 1 Hz-subsequence check.

Gate mechanically (Sonnet): build twice, diff the bundle, run
`exhibit_verify.py`, confirm artifacts byte-identical. Commit scoped
to `WS12_exhibit/`.

## 3. WS13 — the publication (Opus worker)

Launch a `ws-worker` on `WS13_publication/ASSIGNMENT.md`, rewritten
today and authoritative. METHOD.md is the spine; FINDINGS.md is the
case study; the failure-modes catalogue is a required section. Both
guard rails in §0 bind every file.

Commit scoped. WS13 may run in parallel with WS12 — they touch
disjoint paths — but the README's exhibit link cannot be finalised
until §7 gives the live URL, so leave it as a placeholder and patch
it in §7.

## 4. Citation-check adjudications (Opus, both)

Permitted under the freeze by lead ruling: **publication QA is not a
research round.** Launch `ws-adjudicator` on `WS12_exhibit/` and on
`WS13_publication/`, scoped strictly to:

- every rendered or cited number resolves to its cited file and path
  and formats to the displayed string;
- every status matches v7's label exactly, nothing promoted;
- no synthetic data survives in the exhibit;
- both guard rails in §0 hold in the copy.

They dispose of nothing, move no verdict, and open no research
question. Fold their findings, re-run the verifiers, commit. **One
fold each. Do not enter a bounce cycle** — if a finding cannot be
closed by a copy or binding fix, record it in `LIMITATIONS.md` and
move on.

## 5. Licences

`LICENSE` (Apache-2.0), `docs/LICENSE` (CC BY 4.0). No LFS,
no `.gitattributes` — the lead verified the limits and this tree is
well inside them.

## 6. Visibility flip and tag (Sonnet, in this order)

Order matters: GitHub Pages on a private repository is not available
on a free plan, so **public first, then Pages**.

1. Final commit of everything above; push.
2. Flip:
   `gh repo edit valimenai-ux/project-volt --visibility public --accept-visibility-change-consequences`
   The consequences flag is **required** when `--visibility` is used
   non-interactively; the command fails without it.
3. **Verify, do not assume** — this has silently failed before:
   `gh repo view valimenai-ux/project-volt --json nameWithOwner,visibility`
   must report `PUBLIC`.
4. Tag the final commit `v1.0-findings`, annotated, and push the tag.

## 7. Deploy the exhibit (Sonnet)

1. Set the Pages source to GitHub Actions (Vite needs a build step,
   so a branch source will not serve it). Do it via the API so no UI
   click is required:
   `gh api -X POST repos/valimenai-ux/project-volt/pages -f build_type=workflow`
   (if Pages already exists, `-X PUT` the same field).
2. Add `.github/workflows/deploy-pages.yml` building
   `WS12_exhibit/app/` and publishing `dist/` via
   `actions/upload-pages-artifact` + `actions/deploy-pages`, with
   `permissions: pages: write, id-token: write`.
3. Push; wait for the run to go green.
4. **Anonymous verification, mandatory.** Fetch
   `https://valimenai-ux.github.io/project-volt/` with no
   credentials — `curl -sS -o /dev/null -w '%{http_code}'` in a clean
   environment with no `gh` auth and no cookies. Require `200`. Then
   fetch one hashed JS asset and one published trace file the same
   way and require `200` on both — a 200 on the index alone does not
   prove the assets resolve, and a wrong Vite `base` produces exactly
   that failure. Record all three status codes in `PM_LOG.md`.
5. Patch the live URL into `README.md`, commit, push. **Re-point the
   tag** to this final commit so `v1.0-findings` is the state a
   visitor actually gets.

## 8. Close (Sonnet)

1. Kill every process this session started. `pgrep` for `run_ws*`,
   `node`, `vite`, and any polling loops. **Leave none** — the night
   shift left five orphaned pollers and it is in the log.
2. Write `PROJECT_CLOSED.md` at the root:
   - final state per workstream, statuses exactly as v7 labels them;
   - the repo link and the exhibit link;
   - the eight publishable claims with statuses;
   - **the open frontier (R54)**: WS6, WS7, WS10, Vehicle Zero wave
     two, Vehicle One wave three — NOT CUT, with each assignment's
     intent stated, for whoever picks this up someday;
   - the standing post-freeze exception the principal named: if a
     reviewer or OEM ever needs the +20.11% hardened, that is a
     future, labelled, post-freeze WS11 r3 — **not now, and not by
     this session**;
   - the known open findings that were never closed: PRE-B1..B3,
     WS8 r3 B1/B2, KX radiator sizing (103.522 vs 95.018 kW), and the
     unverified WS11 r2 rework.
3. Final commit, push, confirm the tag points where §7.5 left it,
   stop.

## 9. Hard blockers — the only reasons to stop and surface

Everything else you decide yourself and record.

- A merge conflict whose resolution would change a number of record.
- `gh` lacks admin rights to flip visibility, or an account policy
  blocks it.
- Anonymous verification returns anything but 200 after one
  workflow re-run and one `base`-path correction.
- A worker or adjudicator proposes moving a verdict, promoting a
  status, or reopening a frozen question. **Refuse it, log it, do not
  negotiate** — then continue; this is only a blocker if it recurs
  after refusal.
- Anything that would require writing a number not already on disk.

Surface a hard blocker by writing it at the top of `PM_LOG.md` and
stopping cleanly with every process killed. Do not improvise past it.

---

**On completion:** the lead reports to the principal the repo link,
the exhibit link, and a ten-line final state. That closes Project
Volt.
