# WS13 — publication

Executes `ASSIGNMENT.md` against `../BASELINE_v7_FREEZE.md`. This folder holds
the harness; the deliverables live at the repository root.

## Deliverables (repository root)

| file | what it is |
|---|---|
| `../METHOD.md` | the spine — how the trial was run, the defect record, the failure-modes catalogue |
| `../FINDINGS.md` | the case study — the eight publishable claims as results |
| `../README.md` | the front door, two layers per chapter |
| `../LIMITATIONS.md` | what is not established |
| `../REPRODUCE.md` | one command per workstream, the verifiers, the determinism checks |
| `../LICENSE` | Apache-2.0, code |
| `../docs/LICENSE` | CC BY 4.0, prose and data |

## The harness

| file | what it is |
|---|---|
| `build_citations.py` | **the single entry point.** Resolves every number and quoted phrase the publication prints, from the file that owns it. Writes `citations.json` and `CITATIONS.md`. |
| `citations.json` | the results data file: every citation with its rendered string, raw value, source file and locator, plus a SHA-256 of every source. The count is `_meta.n_citations` — read it there rather than from prose, because a number typed here is exactly the defect this harness exists to prevent |
| `CITATIONS.md` | generated index — the reader's map from a `[marker]` in the prose to a file and a JSON path or a line number |
| `verify_ws13.py` | the verifier. Exit 0 = `VERIFY OK`. |
| `requirements.txt` | standard library only |

```
python3 build_citations.py    # or from the repo root: python3 WS13_publication/build_citations.py
python3 verify_ws13.py
```

## What the verifier asserts

1. every citation re-resolves from its own source and still renders the string
   the ledger records;
2. every source file's SHA-256 matches the ledger, so a citation cannot
   silently drift — **with one declared exception**: `PM_LOG.md` is the
   production log and the foreman appends to it, so its hash goes stale by
   design. It is named in `citations.json` → `_meta.live_sources`; a hash change
   on it is reported as an advisory warning while its cited lines stay a hard
   check under [1], because appends do not renumber earlier lines;
3. every `[id]` marker in a publication file names a real citation;
4. the citation's rendered value appears in the prose within a bounded lookback
   window before its marker (`LOOKBACK`, about four lines; tightened to
   `LOOKBACK_SHARED` for the five display strings carried by two citation ids
   each, where proximity is also what identifies the right sibling). The widest
   observed gap is printed on every successful run so the slack cannot quietly
   grow;
5. every citation in the ledger is cited at least once (the ledger is what the
   publication uses, not a superset);
6. **guard rail 1** — the method claim is stated as "catches internal
   inconsistency, never wrong physics" in every publication file including
   `REPRODUCE.md`; the phrase "catches wrong physics" appears nowhere except
   inside that negation; and the upstream label "measured map(s)" / "measured
   inverter" may appear only inside quotation marks, never asserted in the
   publication's own voice (the maps are computed from an analytic loss model).
   These are fixed-string tests and cannot catch every measurement-implying
   phrasing;
7. **guard rail 2** — no status is promoted: each of v7's eight claims is
   rendered with v7's own status text verbatim, v7's `FROZEN-` labels are the
   ones used, and a blacklist of promoted phrasings is absent. This is a string
   test and cannot detect promotion by framing, juxtaposition or omission;
8. the two `REPORT_WS11.md` §0 facts the assignment names — V1's governing
   corner at `+3.66%` under ESC-2 + ESC-4, and the harshest cab-heat reading
   taking it negative — are present in both `FINDINGS.md` and `LIMITATIONS.md`,
   each citing the report;
9. the README's exhibit link is marked as a placeholder pending the Pages
   deploy.

## Determinism

`build_citations.py` reads no clock, uses no randomness and depends on no
environment variable. Re-running it reproduces `CITATIONS.md` byte for byte, and
`citations.json` byte for byte **except for the `PM_LOG.md` hash line** (binding
rule 1, with the live-source exception above). The ledger records source hashes
rather than a build timestamp for exactly that reason — and `PM_LOG.md` is the
one source still being written while this publication is reviewed, so running
the documented command on a tree the foreman has logged to since will rewrite
that single line and nothing else.

## Scope

This is round 1 folded against `FINDINGS_WS13_r1.md` (1 blocking, 4 material,
9 minor) — the single fold permitted by `CLOSEOUT.md` §4. All fourteen findings
were closed by copy or by a strengthening of the verifier; none was deferred to
`LIMITATIONS.md`. No number changed, because none of the fourteen was a number
defect: the adjudicator re-derived 120+ values and the whole 250-citation ledger
independently and found zero mismatches.

This workstream wrote nothing outside `WS13_publication/` and the root
publication deliverables listed above. It edited no baseline, no report, no
findings file and no other workstream's artefacts, and it resolved no
escalation. Discrepancies found in the record while grounding the numbers are
recorded in `../FINDINGS.md` §11 and `../LIMITATIONS.md` §10 and are for the
lead.
