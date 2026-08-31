# FINDINGS — WS13 PUBLICATION, ADJUDICATION ROUND 1 (citation-and-status check)

**Verdict on the round: NOT CLEAN — 1 blocking, 4 material, 9 minor.**

Adjudicator: fresh context, disk only, independent re-derivation. Scope is the citation-and-status check permitted under `BASELINE_v7_FREEZE.md` by the lead's ruling in `CLOSEOUT.md` §4. This file disposes of nothing, moves no verdict, opens no research question and proposes no reopening. Nothing in the tree was modified; all regeneration was done on a copy under a scratch directory and the working tree was confirmed clean afterwards.

Artifacts judged, on disk at commit `e52cee3`: `README.md`, `METHOD.md`, `FINDINGS.md`, `LIMITATIONS.md`, `REPRODUCE.md`, `LICENSE`, `docs/LICENSE`, and `WS13_publication/` (`build_citations.py`, `citations.json`, `CITATIONS.md`, `verify_ws13.py`, `README.md`, `requirements.txt`). Governing status source: `BASELINE_v7_FREEZE.md`.

**The headline.** The numbers are in excellent shape. I independently re-derived **120+ rendered values** from the source JSONs and report lines with my own resolver — not `verify_ws13.py`'s — and found **zero** mismatches, zero wrong members of a set, and zero wheel/shaft/bus blurs. Every number the brief named as load-bearing checks out exactly. What is not in good shape is a small set of **claims the publication makes about itself**: a false count in the front door's first paragraph, a construction claim that two of its own numbers do not satisfy, a coverage claim that overstates the ledger, and a determinism claim that fails on the committed tree. Every one is closeable by copy.

---

## BLOCKING

### B1 — README.md line 8-9: "seventeen adversarial reviews **that failed the work**" is false for at least three of the seventeen

**File / line.** `README.md`:8-9 (second paragraph of the front door).

> "This repository is the complete record: every baseline, every workstream, all seventeen adversarial reviews **that failed the work**, …"

**What is wrong.** The count *seventeen* is correct — there are exactly 17 `FINDINGS_*.md` files on disk, and `METHOD.md` §1 states that correctly. The qualifier **"that failed the work"** is not. Three of the seventeen returned no blocking and no material findings:

| file | its own verdict line |
|---|---|
| `WS2_traction_motor/FINDINGS_WS2_r4.md`:3 | "**Verdict: no blocking or material findings.** The R10 re-spin is genuine and complete…" |
| `WS3_battery/FINDINGS_WS3_r2.md`:48 | "**No blocking or material findings.** F1 through F6 are all genuinely resolved…" |
| `WS4_genset/FINDINGS_WS4_r2.md`:10-11 | "**Verdict: no blocking or material findings. No new findings of any severity.**" |

**Why blocking rather than material.** The defect record *is* claim 8, and claim 8 is the publication's primary thesis. `METHOD.md` §3 states the defensible version — "Every **first-pass** review in this program returned material or blocking findings. Seven workstream first passes" — which I verified row by row and found correct. README generalises "seven first passes" to "all seventeen reviews", inflating the evidence for the thesis in the paragraph a hostile reader meets first, and is falsified by opening any of the three files above. A repository about to go public under a `v1.0-findings` tag, whose whole argument is that structure makes output falsifiable, cannot have its front-door evidence claim falsified by three files in its own tree. This also engages close-out guard rail 2: status promotion by framing on claim 8 ("ratified by its record" — but the record is seven for seven on first passes, not seventeen for seventeen on all rounds).

**Evidence.** `find . -name "FINDINGS_*.md"` returns 17 files; the three verdict lines are quoted verbatim from disk. `METHOD.md`:197-199 carries the correct formulation.

**What would resolve it.** A copy fix at `README.md`:8-9 — e.g. "all seventeen adversarial review rounds, including the seven first passes that every one of them failed", or simply "all seventeen adversarial reviews". No number changes, no status moves, no baseline or report touched.

---

## MATERIAL

### M1 — "measured loss map" / "measured inverter+motor maps" contradicts LIMITATIONS §1 and engages guard rail 1

**Files / lines.** `README.md`:106 ("replacing a scalar assumption with the motor's **measured** loss map"); `README.md`:120 ("**measured maps** instead of a scalar chain"); `FINDINGS.md`:69 ("replacing WS1's scalar efficiency chain with WS2's **measured** inverter+motor maps").

**What is wrong.** `LIMITATIONS.md`:16 states: "Not one physical measurement exists anywhere in this program. No coastdown, no dynamometer run, no thermal soak, no prototype, no component sample." WS2's efficiency maps are **computed**, not measured: `WS2_traction_motor/run_ws2.py`:253-261 writes `data/effmap_motor_inverter_{V}V.csv` from the analytic loss model in `ws2_thermal.steady_analytic()` (fixed-point on winding temperature) and the dq solver in `ws2_bus.py`. The CSV's own columns (`P_cu_kW, P_fe_kW, P_fw_kW, P_inv_kW`) are model loss terms, not instrument channels.

A reader meeting "the motor's measured loss map" in README §3 — the section describing the program's load-bearing kill — will reasonably infer a bench measurement. That is exactly the inference guard rail 1 forbids the copy from supporting.

**Why it survived self-review.** It is an **optimistic label inherited without a flag**. The phrase originates upstream: `WS2_traction_motor/REPORT_WS2.md`:454 ("measured inverter+motor maps × 0.97 reduction"), is carried into `WS4_genset/results_ws4.json` → `interface_ws4.gate_g1.verdict.convention` ("traction = WS2 **measured** map [data/effmap_motor_inverter_662V.csv, 662 V]"), and into ratified `BASELINE_v3.md`:57 ("WS2's measured maps replaced the scalar+part-load treatment"). WS13 inherited it verbatim from a ratified baseline. The publication may not edit the baseline — but it must not repeat an upstream label its own LIMITATIONS file contradicts.

**Evidence.** `WS2_traction_motor/run_ws2.py`:253-261; `WS2_traction_motor/ws2_thermal.py`:87-88 (`def steady_analytic(...)`, docstring "Analytic steady state with resistance feedback"); `head -3 WS2_traction_motor/data/effmap_motor_inverter_662V.csv`; `LIMITATIONS.md`:14-16; `BASELINE_v3.md`:56-58.

**What would resolve it.** Copy fix at the three sites: "modelled loss map" / "WS2's computed inverter+motor loss maps", or keep the inherited wording in quotation marks with the flag. Note `verify_ws13.py` check [6] cannot catch this: it tests only for two fixed sentences and the negation-context of one phrase.

*(Adjacent, not raised separately: `METHOD.md`:353 "The measured difference, from the adjudicator's own re-derivation" uses "measured" of a recomputed statistic. In context that is unambiguous.)*

### M2 — FINDINGS.md's blanket "every margin is a paired per-seed statistic" is false for two of its own rendered numbers, and the data file says so

**File / line.** `FINDINGS.md`:36-38 ("How to read a claim"):

> "**Numbers** are ensemble statistics over 8 seeds unless stated otherwise, and every margin is a *paired per-seed* statistic (formed seed by seed, then enveloped) per ruling R36."

**What is wrong.** Two numbers rendered under that blanket — `-7.01 pp` [`g1_map_vs_scalar_pp`] and `-1.77 pp` [`g1_spin_pp`], at `FINDINGS.md`:69-70 and `README.md`:120-122 — are **not** paired per-seed statistics. They are differences of ensemble minima taken **on different seeds**, which is the statistic-of-statistics family `METHOD.md` FM-2 catalogues and R36 outlawed. The results file states this in the same block the citation reads from:

`WS4_genset/results_ws4.json` → `interface_ws4.gate_g1.attribution_rows.map_vs_scalar_alone`:

```
"delta_pp_min": -7.013618051692167,
"delta_pp_min_governing_case": "difference of ensemble minima over the
  enumerated 8-seed VOLT-REG set: row min at seed 4 … minus prior-convention
  min at seed 5 …"
```

and the paired construction is exported beside it, with different values —
`results_ws4.json` → `construction_sweep_kx_r3.gate_g1_one_factor_paired_companion`:

| row | published (unpaired) | paired companion |
|---|---|---|
| `map_vs_scalar_alone` | **-7.01 pp** | **-7.32 pp** |
| `spin_drag_alone` | **-1.77 pp** | **-1.81 pp** |

**This is not a request to change the number.** The archived rows are BASELINE_v3-ratified record and `PM_LOG.md`:119 records that the round-3 adjudicator confirmed leaving them alone was **correct** ("the archived rows close exactly on the min-to-min shift of record; the paired construction does not close"). The defect is that the publication asserts a construction property its own citations do not satisfy, with no carve-out, while every *other* margin I checked does satisfy it — I confirmed all ten WS11 `one_factor` rows and both `verdict_robustness` rows carry `"statistic": "PAIRED: … (R36/D13)"`, and WS8's `per_km_margin_paired` likewise. The asymmetry is real and undisclosed.

**Evidence.** The `results_ws4.json` paths above (re-read directly); `PM_LOG.md`:110 ("gate_g1_one_factor delta_pp_min: a difference of ensemble minima whose name says so, and BASELINE_v3-ratified record — the worker measured the paired companion outside the archived block"); `PM_LOG.md`:119.

**What would resolve it.** A copy fix at `FINDINGS.md`:36-38 adding the exception, plus a one-clause flag at `FINDINGS.md`:69 and `README.md`:120 naming the archived construction and pointing at the paired companion. Nothing ratified is touched.

### M3 — the "every number is cited" claim is made in four places and is false; at least 21 rendered numbers of record sit outside the ledger

**Files / lines.** `README.md`:289-290 ("**every number in this publication**, with the file and path it came from"); `FINDINGS.md`:611-612 ("**Every number above** is generated by `build_citations.py`"); `REPRODUCE.md`:3 ("**Every number** in FINDINGS.md is regenerable"); `citations.json` → `_meta.purpose` ("**Every number** and quoted phrase used in…"). The assignment's own rule is "Every number cited to file + JSON path or report line."

**What is wrong.** The ledger covers 250 citations over 407 markers. It does not cover the following rendered numbers of record, which are hand-typed and unchecked by any verifier:

| where | uncited number | I verified it against |
|---|---|---|
| `README.md`:68, `METHOD.md`:56, `FINDINGS.md`:51,187 | `6,600 kg` GVW | `interface_ws11.masses.gvw_kg` = 6600.0 ✓ |
| `README.md`:81,244; `FINDINGS.md`:108 | `6.6-tonne` / `6.6 t` | same ✓ |
| `README.md`:151,161; `FINDINGS.md`:110,117,119,142,145 | `105 km/h` | `…ratio_ceiling_closed_form.v_cruise_kmh` = 105.0 ✓ |
| `FINDINGS.md`:117,119,142 | `2,100 rpm` | same block, `rpm_ceiling` = 2100.0 ✓ |
| `FINDINGS.md`:120 | `eleven ratios from 2.4 to 5.0` | `ratios_tested` — exactly 11 members, 2.4…5.0 ✓ |
| `FINDINGS.md`:122 | `about 1.83:1` | 6.88 / 3.7699 = 1.8250 ✓ |
| `FINDINGS.md`:123 | `0.009` | `resolution_sensitivity.d_ratio` = -0.008999… ✓ |
| `FINDINGS.md`:127 | regulatory `12%` start | `…regulatory_startability_adhesion.requirement` ✓ |
| `FINDINGS.md`:54,92 | `2.8:1` top ratio | `BASELINE_v3.md`:52 ✓ |
| `FINDINGS.md`:100 | `36.3 t` | `interface_ws8.gcw_kg` = 36300 ✓ |
| `FINDINGS.md`:192,244 | `195 kg` | `break_even_curb_kg.V2_on_VOLT-REG.headroom_kg_worst` = -195.04 ✓ |
| `LIMITATIONS.md`:113 | CdA `4.2` and `5.4 m²` | `case_definitions.nominal` + the `CdA_5.4` bracket rows ✓ |
| `LIMITATIONS.md`:128 | `about 2.3 BTE points` | `BASELINE_v5.md`:45 ✓ |
| `METHOD.md`:403,415 | `sixteen` areas | `PM_LOG.md`:110,119 ✓ |
| `METHOD.md`:204 | WS1 `13-agent` review | `REPORT_WS1.md`:12 ✓ |
| `METHOD.md`:206 | WS3 r1 "…**4 minor**" | counted F1…F6 in `FINDINGS_WS3_r1.md` ✓ |
| `REPRODUCE.md`:79 | `252 headline renderings` | `PM_LOG.md`:113 ✓ |
| `REPRODUCE.md`:93 | `934 rendered numbers` | `WS5_controls/run_output.txt`:54,56 ✓ |
| `REPRODUCE.md`:119 | `593 checks` | `FINDINGS_WS9_PRE_r1.md`:26 ✓ |
| `REPRODUCE.md`:131 | `609/609`, `16 assertion sections` | `PM_LOG.md`:127 ✓ |
| `REPRODUCE.md`:186,189 | `19 artefacts`, "zero differing" | `WS5_controls/determinism_check.txt`:1; `WS11…/determinism_check.txt` (0 of 33, twice) ✓ |
| `REPRODUCE.md`:205-206 | the two Vehicle Zero seed sets, `[8101 … 8108]` | per-seed keys in `results_ws11.json` / `results_ws9.json` ✓ |

**Every one of the above is accurate** — I re-derived each. The defect is not correctness but honesty of the coverage claim: the publication tells the reader the ledger covers every number, and it does not. Under the program's own FM-4 ("a sweep's clean certifications are themselves auditable claims and must be sampled, never accepted") this is exactly the class of assertion that must be either true or narrowed. I sampled it; it is not true.

**What would resolve it.** Either extend the ledger, or — cheaper and equally honest — narrow the four claims to what is enforced: "every number carrying a `[marker]`". No verifier change needed.

### M4 — the determinism claim fails on the committed tree, and the live-source exception is missing from both places a reader looks

**Files / lines.** `REPRODUCE.md`:190 ("`build_citations.py` writes no timestamp and reads no clock; **re-running reproduces `citations.json` byte for byte**"); `WS13_publication/README.md`:59-62 (same claim, "(binding rule 1)"); `WS13_publication/README.md`:37-38 ("every source file's SHA-256 matches the ledger, so a citation cannot silently drift").

**What is wrong.** I copied the 39 relevant files into a scratch tree and ran `python3 WS13_publication/build_citations.py`. `CITATIONS.md` regenerated byte-identically. `citations.json` **did not**:

```
35c35
<   "PM_LOG.md": "e15c3cdff495075406e2fd41cf52c3870cf41e991f7ee8aafa8a17da309f1fa5",
---
>   "PM_LOG.md": "a5cb2c4271c83a8b29f99dd9a64f51b75f765c96f797458dcd2ef2e1a2fbd40c",
```

`PM_LOG.md` is a live source the foreman appends to, so the ledger's hash of it goes stale by design. `citations.json` → `_meta.live_sources_note` documents this honestly, `verify_ws13.py`'s docstring [2] documents it honestly, and the commit message says "deterministic regeneration (PM_LOG live-source exception only)". The two files a **reader** consults do not. Running the documented command dirties the working tree — the first check a reviewer performs and the cheapest one in the repository.

**Evidence.** The diff above, reproduced on an isolated copy; `verify_ws13.py`:105-120 (the `live` set and warning branch); `_meta.live_sources` = `["PM_LOG.md"]`. On the real tree today: `VERIFY OK — 783 checks passed; 250 citations, 407 markers, 28 source files unchanged, 1 live source(s) advisory`.

**What would resolve it.** One clause in each of the three sentences, matching what `_meta` and the commit message already say.

---

## MINOR

**m1 — README §7's "at the status the record gives it" paragraph omits three statuses and drops v7's `FROZEN-` prefix.** `README.md`:243-248. The heading announces statuses, then gives claim 1's verbatim — "(ratified, model-relative)" — but **none** for the two boundary laws (claim 2 is v7-RATIFIED "closed-form and simulated"; claim 3's duty boundary) or the third wall (claim 4, provisional), and renders V1 as "one **provisional advance**" where v7 line 31 reads `FROZEN-PROVISIONAL ADVANCE`. R52 requires `FROZEN-<status>`; `CLOSEOUT.md` §0.2 calls a bare `PROVISIONAL` in a badge position a build failure, and a paragraph announcing statuses is a badge position. Mitigating: README §6's table and all of FINDINGS render the labels correctly. *Resolution:* add the labels.

**m2 — README §7 says WS11 "was gated but never adversarially reviewed"; WS11 r1 was.** `README.md`:252-254. `FINDINGS_WS11_r1.md`:3 — "**Verdict on the round: NOT CLEAN — 3 blocking, 8 material, 13 minor**". It is round **2** that nothing checked; `METHOD.md` §4 and `LIMITATIONS.md` §9 state it correctly. Runs against the publication's interest, so not a promotion — but the front door misstates the record's own control condition. *Resolution:* "…whose round-2 rework was gated but never adversarially reviewed".

**m3 — FINDINGS §10's header claims a source that does not carry four of its nine rows.** `FINDINGS.md`:537 — "Exactly as `BASELINE_v7_FREEZE.md` records it." Four rows are not in v7: WS1 is `BASELINE_v1.md`:119; WS2 and WS3 are `BASELINE_v3.md`:104-105; WS6 ("blocked on two upstream blocking findings") is `PM_LOG.md`:123. All four are accurate — I checked each — but attributed to a file that does not contain them.

**m4 — FINDINGS §9 embeds a quote about one cab-heat reading inside a sentence about a different one.** `FINDINGS.md`:524-527: "charging the full *'3.0 kW of cab heat **during the engine-off windows only**'* as an electric load **across the whole cycle**". The quote (`REPORT_WS11.md`:272) describes the ESC-2 bracket that yields +4.72%, not the whole-cycle reading that yields -5.42%. Substance right; quote contradicts its own sentence. The correct quote is at `REPORT_WS11.md`:284, or `cold_cab_heat_bracket.V1_on_VOLT-SUB.no_waste_heat_credit_direction`.

**m5 — METHOD §5's preamble miscategorises FM-3.** `METHOD.md`:316-319, "Nine of the eleven are bookkeeping, labelling or case-enumeration errors". FM-3 is not: `METHOD.md`:380 says "This one has no instance, which is the point. It is the structural failure…". Eight of eleven.

**m6 — METHOD FM-4 asserts a sample size the record does not carry.** `METHOD.md`:415, "Sampling two of sixteen was enough to find both." `PM_LOG.md`:119 records the order and result — "spot-check the r3 sweep's sixteen examined-and-clean certifications … TWO are false". Nothing says only two were sampled. It makes the countermeasure sound cheaper than the record shows, in the one catalogue entry about not accepting unverified certifications.

**m7 — `WS13_publication/README.md`:23 renders "239 citations"; the ledger holds 250.** (`_meta.n_citations: 250`; my count: 250; `verify_ws13.py` reports 250.) A hand-transcribed count the ledger moved past — the exact defect family the harness exists to prevent, in the harness's own README. Nothing consumes it.

**m8 — verify_ws13.py's self-description overstates three of its checks.** Spot-checked by reading the code, as the brief directs.
- **[4]** docstring (`:26-28`) says the value appears "**immediately before**" its marker; the code is `body[max(0, m.start() - LOOKBACK):m.start()]` with `LOOKBACK = 320` (`:51`) — four lines of slack. Five display strings are shared by two citation ids each (`+0.59%` → `s2_min`/`v2_pessimistic_median`; `+19.12%` → `v1_cold_ordered`/`v1_worst_corner`; `-0.09%` → `g1_cda54_min`/`pem_design_min`; `2.5%` → `whr_gate`/`etc_gate`; `20,655 kg` → `payload_s0r`/`payload_s6`), so the check cannot alone distinguish a marker attached to the wrong sibling. **I tested it:** exactly one of 407 markers has its value more than 40 chars back (`METHOD.md`:361, the deliberate code-fence quote, 94 chars — correct), and all ten duplicate-display usages resolve to the right member. Passes in fact; described more strongly than it is.
- **[7]** the promotion test is v7's sixteen quotes present in FINDINGS, a 12-phrase blacklist, and three `FROZEN-` labels present *somewhere*. It cannot detect promotion by framing, juxtaposition or omission — m1 passes it cleanly, and so does B1.
- **[6]** guard rail 1 is swept over `PROSE = [README, METHOD, FINDINGS, LIMITATIONS]`; `REPRODUCE.md` is excluded (`:48`). I read REPRODUCE's copy independently and it holds ("It does not prove the function is right", `:195-196`), so no live defect — only an uncovered file. The check tests two fixed sentences plus one phrase's negation context, which is why M1 passed.

**m9 — two of the eight "Status (v7, verbatim)" lines are neither quoted nor cited.** `FINDINGS.md`:106 (claim 2) and `:476` (claim 8) render v7's parenthetical without quotation marks and without a `[marker]`, unlike claims 1/3/4/5/6/7, so no verifier check touches them. Both are substantively correct against `BASELINE_v7_FREEZE.md`:51-52 and `:67`. *Resolution:* use the existing `v7_claim2_status` / `v7_claim8_status` ids.

---

## Out of scope — recorded, not adjudicated

- Whether the KX radiator-sizing case, WS8 r3, the WS9 PRE findings or WS11 r2's unverified rework are *correctly disposed* is a merits question under the freeze. Not touched.
- Whether v7's own "five-for-five" wording, claim 5's "(S3 excepted)" clause, claim 7's PRE-B2 citation and v7's `PM_PACKET_WS5.md` pointer are *wrong* is a merits question for the lead. The publication records all four, resolves none, edits no baseline — which is what `CLOSEOUT.md` §0 and the assignment require. I confirmed each of the four is real and take no position on disposition.

---

## Clean-certifications — what I checked and found clean, by family

These are auditable claims. Each names the method, so the lead can sample them.

**F1. Independent re-resolution of the whole ledger (250/250 clean).** I wrote my own resolver from scratch — I did **not** call `verify_ws13.py`'s `resolve()` — walked each `locator.path` into the source JSON, applied each `format` spec myself (including the `!raw` and `!json:` forms), and for line citations read `lines[line-1]` and asserted the quote is a substring. **250 of 250 render exactly the ledger's `display` string.** All 29 source SHA-256s match except `PM_LOG.md`, the declared live source (M4).

**F2. Load-bearing numbers re-derived from the results files, not the ledger (clean).** Every number the brief named, plus the surrounding block so I could see whether the cited field was the right *member*:
- `+20.11%`, `+19.12%`, `-7.93%`, `-9.98%` — `interface_ws11.verdicts`. Governing cases checked: V1's worst corner is `cold_-10C` (both files label it "cold -10 C" ✓); V2's is `climb_10km_6pct` (both label it "6% climb" ✓). Corner sets enumerated per R14 ✓.
- `+3.66%` — `cold_corner_pending_items.V1_on_VOLT-SUB.with_cab_heat_and_CdA_5p4_pct` = 3.662210971402807, `conditioned_on_rulings: ["ESC-2 (pending)","ESC-4 (pending)"]` ✓, and it is V1's **governing** corner, confirmed against `cold_corner_both_pending_items.why` ✓.
- `-5.42%`, `+4.72%`, `+2.64%`, `+19.12%` (ordered) — all four `cold_cab_heat_bracket.V1_on_VOLT-SUB` members read side by side; `FINDINGS.md`:514-519 labels each with the right construction ✓.
- `+6.26%`, `-2.58%`, `-2.50%`, `7.58 pp`, `0 of 8`, `-0.09%`, `4 of 8`, `-5.90%`, `5%` — `interface_ws4.gate_g1`, cross-checked against ratified `BASELINE_v3.md`:8-19 ✓. (`-7.01`/`-1.77 pp` — see M2.) `gate_g1.status` = `executed_kill_2026-08-30` ✓ exactly as REPRODUCE describes.
- `-31.69%`, `-40.10%`, `19.18`, `28.07`, `32.01 L/100 km`, `179,702 miles`, `1,044 fuel-ups`, `calibrate_order_satisfied: false` — `interface_ws11.ruler.anchor` and `…l_per_100km_VOLT_SUB.median` ✓. The era-correct member is correctly identified as governing ✓.
- `103.522` / `95.018 kW` — rendered at v7's precision ("103.5 vs 95.0 kW)", `BASELINE_v7_FREEZE.md`:44) plus v6's measured figure ("CORNER (103.522 kW two-minute maximum)", `BASELINE_v6.md`:90); both resolve ✓, cross-read against `PM_LOG.md`:119 which carries both and the +8.95% ✓.
- Claim 5's whole table: `+6.03/+8.62/+4.88/+3.36%` per-km; `-0.69/+0.59/-1.09/-3.84%` per-payload min; `+0.73/+1.89/+1.64/-1.06%` median; payloads `20,785/19,398/19,106/19,559/19,344 kg`; `38.78 L/100 km`; bars `3%`/`0%`; `+11.06%`; `wins_on_every_seed = true` ✓.
- Claim 2: `3.7699` — and I re-solved it, 2100 × 2π × 0.5 / (60 × 105/3.6) = 3.76991 ✓ — plus `6.88`, `1,732 rpm`, `any_feasible = false`, `0.587`, `0.293`, `0.5 m` ✓; span 6.88/3.7699 = 1.825 vs the prose's "about 1.83:1" ✓.
- Claim 4: `25.4`/`33.5 km/h`, `6%`/`8%`, `2.058`, `10.74%` ✓ — `duty_grade_max` cites `.max` over the 8-seed ensemble, the correct member for "steepest grade over the ensemble" ✓.
- Claim 6: `2.5%` (both gates), `+1.75/+1.83/+2.38%`, `+1.67%`, `85 kg`, `0.41%`, `2.91%` ✓ — 2.5 + 0.4132 = 2.9132 ✓ arithmetic closes.
- Claim 7: `-0.09/+0.03/-0.35/-0.22%` from `bracket_margins.*.S0R-PCC.ensemble` ✓; `+7.50/+7.26%`, `20,655 kg` ✓.
- §10 wave-two roll-up: `+11.95/-6.81`, `+5.36/-1.38`, `+4.51/-1.45`, payloads `20,134/19,706/19,846/20,655 kg`, S5 `+1.90/-5.75` ✓.
- Masses close arithmetically: 3,888+2,712 = 4,139+2,461 = 3,700+2,900 = 6,600 ✓; 3,944 − 4,139 = −195 ✓; 3,888 + 545 = 4,433.49 = `break_even.V1.worst` ✓.
- **Sign-convention trap, clean:** `+6.93%` carries `direction_that_would_overturn_the_verdict: "THIRSTIER"` and `-17.64%` carries `"LEANER"` — the prose says "thirstier" and "leaner" respectively ✓.
- Capability: `31.76`/`82.01 km/h` under the rule "steady speed on a 6% grade at GVW with **NO buffer contribution**", exactly the prose's wording ✓; `1.7204 kWh` is `candidate_worst_unserved_**bus**_kWh` and the prose says "unserved **bus** energy" ✓ (CLAUDE.md rule 6 satisfied — the ruler's companion field is a *wheel* quantity, 3.2582 kWh, and is correctly not mixed in); `governing_case: climb_10km_6pct` matches "on its governing corner" ✓; `candidate_worst_soc_min = 0.0` supports "it empties the pack" ✓.
- `0.0e+00` seam: `ws4_hot_swap_seam.max_abs_difference` = 0.0, WS11's and WS4's min/median/max identical floats ✓.

**F3. Member-selection sweep (clean).** The error class the brief told me to hunt. Every place the results files export more than one plausible member:
- `one_factor…start_stop_engine_off` (72.58 pp, load-following counterfactual) vs `…_pinned_variant` (101.80 pp, pinned counterfactual). The publication renders 72.58 pp and **names the counterfactual** — "against a load-following genset" (`FINDINGS.md`:198, `METHOD.md`:574) ✓.
- `anchor.all_model_years` vs `anchor.fourhk1_era` — both rendered, the era one labelled "the governing member" ✓ (this is the member WS11 r1's M5 got wrong; the publication gets it right).
- `ratio_ceiling_closed_form.value` (3.7699, physics bound) vs `max_ratio_without_overspeed` (3.6, which the JSON itself calls "an illustration, not the limit"). The publication renders the closed-form bound and calls it "closed form" ✓.
- `pct_ruler_fuel_error_to_draw` vs `…_to_3pct_bar` — V2 uses *to_draw* ("flips to a draw" ✓), V1 uses *to_3pct_bar* ("before V1 fell to the 3% bar" ✓).
- WHR `best_net_margin_pct` per candidate — prose says "Best system per candidate" ✓.
- All five duplicated display strings resolve to the right site; `v1_cold_ordered` and `v1_worst_corner` both render `+19.12%` from different fields and each is used where its own construction belongs ✓.

**F4. Marker adjacency and ledger hygiene (clean).** 407 markers, all naming real citation ids; every ledger entry used at least once (0 unused); every marker's value adjacent except the one deliberate code-fence quote.

**F5. Guard rail 1 in the copy, read sentence by sentence (one defect: M1).** I read all five files in full rather than grepping. The negation is stated in all four PROSE files and in REPRODUCE's equivalent form. `LIMITATIONS.md`:33-34 ("it was validated — not fitted — against a public in-use fuel-economy aggregate. **It failed that validation by a wide margin**") uses "validated" of an attempt then reported as failed — the opposite of a validity claim; not a defect. `METHOD.md` FM-11 and `LIMITATIONS.md` §11 argue the one lead-labelled "physics defect" back to the consistency side with three stated reasons; I checked the underlying quotes at `BASELINE_v6.md`:63-66 and `WS8_semi_architecture/REPORT_WS8.md`:600 and the argument is faithful. `README.md`:51-53 ("several of them are closed-form and hold regardless of the model's calibration") is true of claim 2, whose bound is kinematic. Only breach is M1.

**F6. Guard rail 2 — status fidelity, all eight claims (one defect: m1; B1 is framing).** All sixteen v7 claim/status quotes in FINDINGS checked character-for-character against `BASELINE_v7_FREEZE.md`:48-67. **Nothing is promoted anywhere in the five files.** Per the brief: claim 1 renders "(ratified, model-relative)" ✓ **not demoted**; claim 2 renders "ratified, closed-form and simulated" ✓ **not demoted** (m9 on formatting; m1 on README §7's omission); claim 5 renders "(ratified, r3 numbers)" ✓ **not demoted** — the "(S3 excepted)" note is recorded as a wording discrepancy and explicitly says "The claim's substance … holds on every row of the table", which does not lower the status; claim 6 renders "(ratified at semi scale)" ✓ **not demoted**, and the distinction the copy must get right is got right — README §7 lists WHR under "Killed" as a *candidate technology* (both gates dropped it) while the *claim* about part-load stays RATIFIED in FINDINGS. V1 is `FROZEN-PROVISIONAL ADVANCE` and V2 `FROZEN-KILL` in FINDINGS and README's table ✓. `NOT CONVERGED` and `NOT CUT` carry v7's meanings ✓. R54's five open-frontier items are listed complete ✓.

**F7. The two REPORT_WS11 §0 facts the assignment names (clean).** Verified against `WS11_vehicle_zero_ruler/REPORT_WS11.md` itself, not via the ledger. Fact 1: line **39** reads "**Conditional** on ESC-2 + ESC-4 together, which take its governing corner to **+3.66%**" — carried in `FINDINGS.md`:498-505 and `LIMITATIONS.md`:86-91, both citing §0 line 39 and both giving the exported JSON path, which resolves ✓. Fact 2: line **35** reads "the harshest one takes V1's governing corner negative" and line **284** (confirmed inside §5, headed at line 254) reads "under the harshest cab-heat reading V1's governing corner goes NEGATIVE" — carried in `FINDINGS.md`:507-519 and `LIMITATIONS.md`:92-98, both citing the report, both giving -5.42% ✓. Both files state explicitly that the status does not move. Requirement met in full (m4 is a quote-choice nit inside Fact 2's supporting sentence, not a failure of the fact).

**F8. Determinism and scope (one defect: M4).** `build_citations.py` regenerates `CITATIONS.md` byte-identically and `citations.json` identically but for the `PM_LOG.md` hash line; run on an isolated copy, repository untouched. `git status --porcelain` for all reviewed paths empty at the end of this review. `verify_ws13.py` exits 0. `LICENSE` is Apache-2.0 (220 lines) and `docs/LICENSE` is CC BY 4.0 (83 lines), as `CLOSEOUT.md` §5 requires. Every file path, entry point, verifier, determinism artefact and requirements file named in `REPRODUCE.md` exists on disk (36 of 36 checked), and every `requirements.txt` matches REPRODUCE's table exactly. The README exhibit link carries both the machine-readable `PLACEHOLDER` comment and a render-visible caveat ✓.

---

*Adjudicator note.* This review fixed nothing, softened nothing, ruled on nothing, and spoke to no worker. Findings are for the lead.

*Foreman placement note (close-out session, 2026-08-31).* The adjudicator's harness refused the findings-file write ("Subagents should return findings as text") — same refusal as the WS9 pre-adjudication, `PM_LOG.md`:116. Placed here verbatim by the foreman from the adjudicator's returned text, unchanged except HTML entity un-escaping introduced by transport. The foreman authored none of the content above this note.