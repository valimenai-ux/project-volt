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
| `citations.json` | the results data file: 239 citations, each with its rendered string, raw value, source file and locator, plus a SHA-256 of every source |
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
   silently drift;
3. every `[id]` marker in a publication file names a real citation;
4. the citation's rendered value appears in the prose immediately before its
   marker — the number the reader sees is the number on disk;
5. every citation in the ledger is cited at least once (the ledger is what the
   publication uses, not a superset);
6. **guard rail 1** — the method claim is stated as "catches internal
   inconsistency, never wrong physics" in every prose file, and the phrase
   "catches wrong physics" appears nowhere except inside that negation;
7. **guard rail 2** — no status is promoted: each of v7's eight claims is
   rendered with v7's own status text verbatim, v7's `FROZEN-` labels are the
   ones used, and a list of promoted phrasings is absent;
8. the two `REPORT_WS11.md` §0 facts the assignment names — V1's governing
   corner at `+3.66%` under ESC-2 + ESC-4, and the harshest cab-heat reading
   taking it negative — are present in both `FINDINGS.md` and `LIMITATIONS.md`,
   each citing the report;
9. the README's exhibit link is marked as a placeholder pending the Pages
   deploy.

## Determinism

`build_citations.py` reads no clock, uses no randomness and depends on no
environment variable. Re-running it reproduces `citations.json` and
`CITATIONS.md` byte for byte (binding rule 1). The ledger records source
hashes rather than a build timestamp for exactly that reason.

## Scope

This workstream wrote nothing outside `WS13_publication/` and the root
publication deliverables listed above. It edited no baseline, no report, no
findings file and no other workstream's artefacts, and it resolved no
escalation. Discrepancies found in the record while grounding the numbers are
recorded in `../FINDINGS.md` §11 and `../LIMITATIONS.md` §10 and are for the
lead.
