# WS12 — THE EXHIBIT

The program's method, made clickable. A static web app in which every
number of record on every screen resolves to a file and an explicit key
path, and a verifier that refuses to let the build pass if one of them
does not.

Bound to `../BASELINE_v7_FREEZE.md`. Read `REPORT_WS12.md` first.

## Run it

```
../.venv/bin/python3 run_ws12.py --with-app     # everything, in order
```

or step by step:

```
../.venv/bin/python3 build_exhibit_data.py      # read the record, emit the bundle
../.venv/bin/python3 exhibit_verify.py          # 13 checks
../.venv/bin/python3 make_report_ws12.py        # render REPORT_WS12.md
../.venv/bin/python3 exhibit_verify.py          # now including check 13
../.venv/bin/python3 check_determinism_ws12.py --with-app
../.venv/bin/python3 test_sandbox_ws12.py       # also runs as verify check 11
```

The web app:

```
cd app && npm ci && npm run build     # dist/, base = /project-volt/
cd app && npx vite preview            # http://localhost:4173/project-volt/
```

## What is here

| path | what it is |
|---|---|
| `app/` | Vite + React + TypeScript, no server. `src/` is the app; `public/` is the emitted payload and IS committed |
| `app/public/data/exhibit_data.json` | the results data file — the bundle every screen renders from |
| `app/public/data/manifest.json` | every renderable string, with the file and key path it resolves to |
| `app/public/data/decimation_manifest.json` | one row per published trace: source path, source sha256, stride, row counts |
| `app/public/traces/<id>/` | 1 Hz strided scrub index + 10 Hz segment chunks |
| `app/public/maps/` | WS4's exported BSFC maps, served as-is |
| `build_exhibit_data.py` | reads the record read-only, emits everything above |
| `exhibit_verify.py` | the thirteen checks. Its own resolver, formatter and parser |
| `make_report_ws12.py` | renders `REPORT_WS12.md` from the results data; records every assertion |
| `ws12_record.py` | citation primitives and the status-badge vocabulary |
| `ws12_traces.py` | TRACE_SCHEMA validation and decimation |
| `ws12_sandbox.py` / `test_sandbox_ws12.py` | the ratio-window model and its unit test against the record |
| `check_determinism_ws12.py` | build twice, diff every artifact |
| `design/` | the original dc-runtime draft, kept as the visual source |

## Two rules this workstream exists to demonstrate

**The method claim is "catches internal inconsistency," never "catches
wrong physics."** No hardware was built. The ruler is uncalibrated.

**No status is ever promoted.** Badges render only the five labels
`BASELINE_v7_FREEZE.md` uses. A bare `RATIFIED` or `PROVISIONAL` in a
badge position is a build failure.

Nothing in this folder ratifies anything, and nothing outside this folder
was modified.
