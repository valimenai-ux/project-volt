# PROJECT VOLT — CLOSED

Project Volt is closed as of 2026-08-31 by the principal's ratified
close-out decision (`CLOSEOUT.md`). The research track froze at
`BASELINE_v7_FREEZE.md`; nothing after that file reopens a verdict,
moves a number, or promotes a status. This document restates the
frozen record for whoever finds the repository next. It ratifies
nothing — ratification happens in the principal's own chat
(`CLAUDE.md`, "The project lead ratifies in a separate chat").

## Repository and exhibit

- Repository: **https://github.com/valimenai-ux/project-volt** —
  public, verified (`gh repo view` reported `visibility: PUBLIC`, not
  assumed; `PM_LOG.md`, entry 2026-08-31 13:26 PDT | -- | §6 DONE —
  REPO PUBLIC (VERIFIED), TAG v1.0-findings PUSHED).
- Exhibit: **https://valimenai-ux.github.io/project-volt/** — live,
  anonymous 200-verification on the index page, one hashed JS asset
  pulled from the served HTML, and one published trace file, all
  fetched with no credentials and no cookies
  (`PM_LOG.md`, entry 2026-08-31 13:35 PDT | -- | §7.3-7.4 DONE — RUN
  GREEN, ANONYMOUS VERIFICATION 200/200/200).
- Tag **`v1.0-findings`** points at commit `af52981` — the §7.5 commit
  that patched the exhibit link into `README.md` and re-triggered a
  green Pages deploy on the same commit
  (`PM_LOG.md`, entry 2026-08-31 13:47 PDT | -- | §7 COMPLETE —
  COMMITTED af52981, TAG RE-POINTED, REDEPLOY GREEN).

## Final state per workstream

Status quoted verbatim from `BASELINE_v7_FREEZE.md` ("Final research
state at freeze") where it carries the row. Where v7 defers to a
workstream's own packet, or does not carry the row at all, the source
that does is cited.

| workstream | state at freeze |
|---|---|
| Vehicle Zero architecture | "architecture ratified (pure series, both variants)" (`BASELINE_v7_FREEZE.md`) |
| WS1 loads & duty cycles | closed, ratified with amendments (`BASELINE_v1.md`, Workstream map) — v7 does not carry this row |
| WS2 traction motor | closed-ratified at round 4; round 3 had stopped NOT CONVERGED (`BASELINE_v3.md`, Workstream states) — v7 does not carry this row |
| WS3 battery | closed-ratified (`BASELINE_v3.md`, Workstream states) — v7 does not carry this row |
| WS4 genset / Gate G1 | gate executed; "KX: NOT CONVERGED after three rounds (radiator sizing case 103.5 vs 95.0 kW)" (`BASELINE_v7_FREEZE.md`) |
| WS5 controls | "status per its packet at freeze" (`BASELINE_v7_FREEZE.md`). No `PM_PACKET_WS5.md` exists on disk. What the record itself says: **gated-but-unadjudicated**, the only workstream of the night with zero adjudication rounds (`results_ws5.json` → `_meta` → `adjudication`; `PM_LOG.md`, entry 2026-08-31 09:08 PDT \| WS5 \| COMMITTED — GATED BUT UNADJUDICATED) |
| WS6 packaging | never started; blocked on two upstream blocking findings — KX R3-B1 and WS9 PRE-B3 — landing on exactly what it would consume (`PM_LOG.md`, entry 2026-08-31 06:52 PDT \| WS6 \| B4 HELD — REASON RECORDED) — v7 does not carry this row |
| WS8 semi architecture (Vehicle One) | "WS8 S1-S4 KILLED (final), WHR DROPPED (final); numbers FROZEN-PROVISIONAL at r3 (r3 adjudication not clean, r4 ordered and not run)" (`BASELINE_v7_FREEZE.md`) |
| WS9 Vehicle One wave two | "S6 / S4' / S5-13L / S7 FROZEN-PROVISIONAL ADVANCE on grade-heavy regional duty, S5-11L KILL, ETC dropped; known open findings PRE-B1..B3; S5-13L expected to convert to KILL-ON-TIME under R46" (`BASELINE_v7_FREEZE.md`) |
| WS11 Vehicle Zero ruler trial | V1 Postal: "FROZEN-PROVISIONAL ADVANCE, +20.11% nominal ensemble-min per payload tonne-km, worst corner +19.12%, robust to all ruler-modelling brackets; conditional on R43(a)-(d) (cab heat, warm-up model, corner convention, CdA bracket), which were ordered and not run." V2 Trucker: "FROZEN-KILL, -7.93% headline, a draw at the ruler's pessimistic end, never reaching the bar." "Ruler uncalibrated (ESC-1); all Vehicle Zero verdicts are model-relative." (`BASELINE_v7_FREEZE.md`) |
| WS12 exhibit | **delivered close-out workstream, not a research verdict.** Built, gated, citation-check adjudicated **NOT CLEAN — 0 blocking / 4 material / 8 minor**; all twelve findings folded; `exhibit_verify.py` — 1,187 assertions, 0 failures, PASS (`WS12_exhibit/REPORT_WS12.md` §0, §7; `WS12_exhibit/FINDINGS_WS12_r1.md`) |
| WS13 publication | **delivered close-out workstream, not a research verdict.** Gated, citation-check adjudicated **NOT CLEAN — 1 blocking / 4 material / 9 minor**; all fourteen findings folded, no number moved; `verify_ws13.py` — 853 checks, PASS (`WS13_publication/FINDINGS_WS13_r1.md`; `PM_LOG.md`, entry 2026-08-31 11:27 PDT \| WS13 \| FOLD-DONE (THE ONE §4 FOLD)) |

Doctrine D1-D21 stands as the program's contribution
(`BASELINE_v7_FREEZE.md`, "Final research state at freeze").

## The eight publishable claims

Verbatim from `BASELINE_v7_FREEZE.md`, "What the program found," each
with its status parenthetical exactly as written there:

1. Electric torque-fill replaces the gearbox entirely at 6.6 t
   (ratified, model-relative).
2. The transmissionless premise has a MASS boundary between ~7 and
   36 t: no single ratio spans cruise and grade at 36.3 t (ratified,
   closed-form and simulated).
3. It has a DUTY boundary: the same truck wins +20% on stop-go and
   loses on regional duty (V1 provisional, V2 kill).
4. A 2-speed under torque-fill meets a third wall — the low gear's
   coupling floor vs crawl speed (provisional).
5. At fixed gross weight, efficiency per added kilogram is the
   objective; every electrified semi candidate won 6-10% per km and
   gave 6-8% back in freight (S3 excepted) (ratified, r3 numbers).
6. Waste-heat recovery is a full-load technology on a part-load duty
   (ratified at semi scale).
7. Zero-mass levers are symmetric; predictive energy management is
   worth ~0 when the incumbent gets it too (provisional, PRE-B2).
8. The method: pre-registration, pre-committed kill criteria, fresh-
   context disk-only adjudication, three-way verification, export
   discipline — five-for-five first-pass defect detection, including
   the lead's own errors (ratified by its record).

`FINDINGS.md` carries the fuller statements of all eight and, in its
§11 "Where the record disagrees with itself," the record-vs-record
observations against four of them, including that claim 8's own
denominator is disputed on disk (see "Known open findings" below).

## The open frontier (R54) — NOT CUT

`BASELINE_v7_FREEZE.md` R54: "WS6, WS7, WS10, Vehicle Zero wave two
(R48) and Vehicle One wave three are NOT CUT." None of these was
executed; none is disposed. Intent, as recorded on disk:

- **WS6 — packaging and the program heat ledger.** Owns mass, volume,
  CG, cooling and HV routing for the ratified pure-series system on
  the NPR-HD frame, and aggregates the program's heat ledger
  (`WS6_packaging/ASSIGNMENT.md`). Never started; see the WS6 row
  above for why.
- **WS7 — the prototype and test plan.** Accumulated scope: coastdown
  (E13), adhesion (E23), a crawl heat-run (G_ws ≥ 90 W/K vs. the
  80.1 W/K floor), ISO 3046-1 two-leg dyno substantiation of the
  132 kW flat-rating, program-wide fault-asymmetry tests, and the R21
  tolerance corner (`BASELINE_v3.md`, Workstream states). It also
  carries the mandatory ruler-calibration task — measuring a stock
  NPR-HD on the program cycles — without which no Vehicle Zero verdict
  is more than model-relative (`BASELINE_v6.md` R44; `FINDINGS.md`
  §10).
- **WS10 — the combination trial.** S6's engine paired with
  S5-13L's two-speed and lean motors (`FINDINGS.md` §10), scheduled to
  run "after WS9 ratifies" (`BASELINE_v6.md`, Workstream states). WS9
  never ratified.
- **Vehicle Zero wave two (R48).** Posed, not cut: V1-P, an
  Atkinson-petrol genset for Postal that deletes DPF/SCR/DEF mass at
  parity efficiency near the pin; and V2-L, a mass-lean hybrid for
  regional delivery — small machine, small buffer, stock AMT retained,
  the semi-scale lesson applied downward (`BASELINE_v6.md` R48).
- **Vehicle One wave three.** Never scoped. `FINDINGS.md` §10 states
  this plainly: "Vehicle One wave three was never scoped." No
  assignment file exists for it anywhere in the tree.

## The standing post-freeze exception

Per `CLOSEOUT.md` §8.2, named by the principal: if a reviewer or OEM
ever needs the +20.11% (WS11 V1 Postal) hardened against its
conditions (R43(a)-(d)), that is a future, labelled, post-freeze
**WS11 r3** — not now, and not by this session.

## Known open findings, never closed

- **PRE-B1..B3** (WS9 pre-adjudication) — on the record against WS9's
  four FROZEN-PROVISIONAL ADVANCE verdicts
  (`WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md`;
  `BASELINE_v6.md` R46). PRE-B1: the concordance module cannot fire on
  10 of 15 fields — hard-coded verdict literals and tautologies,
  mutation-proven. PRE-B2: the PEM "exactly 0.0" reading is an
  unmeasured fallback (`fuel_g_genset` is absent from all 576 per-seed
  records, so the fallback fires every time). PRE-B3: S5-13L's 6%
  climb ledger row lands on the wrong branch of the two-band envelope
  (D16) — 20.1 kW exported against a correct 507.3 kW, roughly 25x
  understated; WS6 never ran and would have consumed that row.
- **WS8 r3 B1/B2** (`WS8_semi_architecture/FINDINGS_WS8_r3.md`). B1:
  an unmeasured control-law change to S3's charge throttle-back is
  worth +1.64 pp of S3's +6.90 pp movement; the changelog states the
  change does not exist. B2: `retard_overcommitment` exports an
  instantaneous spike under an R14 rule string labelled "sustained
  60-second," 1.53x high, and the case it labels is not the case
  governing the statistic it names.
- **KX radiator sizing** — 103.522 kW vs. the 95.018 kW design point,
  +8.95%, **NOT CONVERGED** after three rounds
  (`WS4_genset/FINDINGS_KX_r3.md`; `BASELINE_v7_FREEZE.md`).
- **The unverified WS11 r2 rework — the control condition.** The
  principal cut WS11 r2's and WS5's adjudication rounds at 07:40 to
  close the night. WS11 round 2 closed 3 blocking + 8 material + 13
  minor findings from round 1, and nothing adversarial has read that
  work since (`PM_LOG.md`, entry 2026-08-31 07:40 PDT | -- | PRINCIPAL
  DECISION — ADJUDICATIONS CUT FOR WS11 AND WS5: "a gate PASS on r2 is
  evidence of reproducibility only … is NOT evidence the findings are
  closed"). The WS12 exhibit's round-history screen renders this gap
  first and unsoftened, as the control condition
  (`WS12_exhibit/REPORT_WS12.md` §2).

Also standing and undisposed: **WS12's nine escalations, E1-E9**
(`WS12_exhibit/REPORT_WS12.md` §8) — spanning a disputed denominator
in claim 8's defect-detection rate, a doctrine citing a WS1
adjudication file that does not exist, v7's dangling
`PM_PACKET_WS5.md` pointer, a WS11 trace-fuel column that does not
integrate to WS11's own exported per-seed fuel, a WS5 fault trace that
fails the blend-order sum rule, a schema/data mismatch on
`P_bus_load_kW`, a named trace file that does not exist under that
name, WS11's r2 traces predating the schema they anchor, and WS5 trace
headers carrying the ruler's payload for a candidate vehicle. And
**WS13's four v7-vs-artifact observations** (`FINDINGS.md` §11) —
claim 5's "(S3 excepted)" clause reading as a round-2 fact under a
round-3 label, claim 8's "five-for-five" predating two of the seven
first-pass reviews it describes, claim 7's PRE-B2 citation pointing at
a different measurement than the one it is attached to, and v7's WS5
line pointing at a packet that was never written. None of the above is
self-resolved; all are for the lead.

## Close

The program's method contribution: pre-registration of criteria before
a result exists, pre-committed kill criteria that cannot be
renegotiated after the fact, fresh-context disk-only adjudication,
three-way verification between report prose, machine-readable
interface and source data, and export discipline (every worst-case
field an explicit max/min over an enumerated case set, the governing
case labelled inline). `BASELINE_v7_FREEZE.md` claim 8 states the
result as **"five-for-five first-pass defect detection."** Seven
first-pass adjudication findings files exist on disk (WS2 r1, WS3 r1,
WS4 r1, KX r1, WS8 r1, WS9 pre-r1, WS11 r1) and all seven record at
least one blocking or material finding; whether that is "five-for-five"
or "seven-for-seven" turns on whether KX's first pass and the WS9
pre-adjudication count in the denominator, and the record disagrees
with itself on that question — this workstream's own assignment orders
the seven-for-seven reading against v7's five-for-five, both are
rendered without promoting either in the exhibit
(`WS12_exhibit/REPORT_WS12.md` §8, WS12-E1), and this document does
not adjudicate it either. The limitation is stated plainly,
not as a footnote: **the method demonstrated here catches internal
inconsistency. It cannot catch wrong physics.** No hardware was built
anywhere in this program; the one ruler used to size Vehicle Zero's
claims against a real truck was never calibrated and sits -31.69%
below its own sourced anchor (ESC-1). Every verdict in this repository
is model-relative.

## Post-close amendments

- 2026-08-31, principal-ordered, visualization only: the exhibit's
  simulator gained a side-by-side lane view — both trucks on a shared
  route axis, positions derived exclusively from each truck's own
  trace of record. The record's answer: every paired speed column is
  byte-identical, 0.000 m separation on all four pairs; the climb's
  shortfall is booked in the energy ledger (ruler capability-limited
  555.6 s, 3.2582 kWh unserved wheel energy), not the position axis.
  No verdict, number, status, baseline or report of the research
  record was touched (`WS12_exhibit/REPORT_WS12.md` §0b;
  `PM_LOG.md`, entries 2026-08-31 14:21-14:47 PDT). Tag
  `v1.0-findings` remains at `af52981`, the findings release.
