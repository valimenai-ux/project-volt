# FINDINGS — WS12 (the exhibit), round 1

**Citation-check adjudication under CLOSEOUT.md §4.** Fresh context,
artifacts read from disk only, work product not edited. Scope is strictly
CLOSEOUT §4's four bullets plus REPORT_WS12.md's own claims and a read of
three verifier check-groups. This round disposes of nothing, moves no
verdict, and opens no research question.

Work product reviewed at commit `855730d`, tree state as found.

---

## VERDICT: **NOT CLEAN**

| severity | count |
|---|---|
| BLOCKING | **0** |
| MATERIAL | **4** |
| MINOR | **8** |

No blocking findings. Nothing on any screen renders a wrong number, no
synthetic data survives in the exhibit, the pipeline regenerates
byte-identically, and all 239 citations, 46 quotations and 53 file
identities re-resolve under an independently written resolver and
formatter. The four material findings are: one status badge that does not
match v7's label for the thing it labels; a twentieth badge position that
escapes both the manifest and the verifier, making a machine-readable
interface field wrong; a front-door quotation truncated before the caveat
v7 attaches to it; and a class of rendered numbers that carries neither a
tier badge nor any verifier coverage, against the report's claim that
every renderable value carries a tier.

---

# MATERIAL

## WS12-r1-M1 — MATERIAL. The simulator screen wears a `NOT CUT` badge; v7 does not label WS5 that way, and the quote beside it says the opposite word

**Where.** `WS12_exhibit/app/public/data/exhibit_data.json` →
`$.screens.sim.statusBadge` = `"NOT CUT"`, emitted at
`build_exhibit_data.py:1441`, rendered by `<StatusBadge s={d.statusBadge} />`
at `app/src/screens/Simulator.tsx:711` in the head of the "SELECT A TRACE"
panel. It is the exhibit's only use of `NOT CUT`; the interface block
counts it as `badges.by_label."NOT CUT": 1`.

**What is wrong.** `BASELINE_v7_FREEZE.md` R54 defines the `NOT CUT` set
exhaustively: *"WS6, WS7, WS10, Vehicle Zero wave two (R48) and Vehicle
One wave three are NOT CUT."* WS5 is not in it. v7's line for WS5 is
`"WS5: status per its packet at freeze."` The simulator screen replays
WS5's two R34 traces and its `statusNote` is entirely about WS5's status.
So a v7 label is applied to a workstream v7 does not apply it to.

**Evidence, three ways, all on the same panel.**

1. `$.screens.sim.statusNote.headline` = `"WS5 was never adjudicated."`
2. `$.screens.sim.statusNote.quote` — a RECORD citation to
   `WS5_controls/results_ws5.json → _meta → adjudication`, which reads:
   `"CUT by BASELINE_v7's research freeze. This packet is
   gated-but-unadjudicated; ..."` The badge says NOT CUT; the cited
   record on the same panel says CUT.
3. The exhibit's own per-workstream table disagrees with its own badge:
   `$.screens.rounds.workstreams` WS5 row carries
   `statusText: "GATED BUT UNADJUDICATED"`.

Neither the builder's `status_badge()` guard (`ws12_record.py:167`) nor
`exhibit_verify.py` check 6 can catch this: both test only that the string
is a member of v7's five labels, never that the label is the one v7 gives
the subject.

**What would resolve it.** Either render WS5's status as the exhibit
already renders it elsewhere (`GATED BUT UNADJUDICATED`, sourced from
`results_ws5.json → _meta`), or drop the status badge from that panel head
and let `statusNote` carry the disposition. Not for this adjudicator to
choose; both are copy/binding fixes and neither moves a verdict.

---

## WS12-r1-M2 — MATERIAL. There are twenty badge positions, not nineteen; the twentieth is invisible to the manifest and to the promoted-status check, and the interface block's badge counts are therefore wrong

**Where.** `app/src/screens/VerdictWall.tsx:245-246`:

    <StatusBadge s={c.statusBadge} />
    <StatusBadge s={c.numbersBadge} small />

`$.screens.verdict.cards[1].numbersBadge` = `"FROZEN-PROVISIONAL"`
(`build_exhibit_data.py:287`). It is rendered by the same `StatusBadge`
component, in the same `PanelHead` right-hand badge slot, immediately
beside `cards[1].statusBadge`.

**What is wrong — three consequences.**

1. **The manifest under-enumerates.** `build_exhibit_data.py`'s
   `collect_badges()` harvests only keys named exactly `statusBadge`:
   `if k == "statusBadge" and isinstance(v, str):`
   `numbersBadge` is skipped. `manifest.json → badges` therefore lists 19
   of the app's 20 badge render sites. My own walk of the bundle for keys
   matching `/[Bb]adge$/` returns 20 status labels plus the three
   decimation-badge strings.

2. **The independent check has the same blind spot.**
   `exhibit_verify.py` check 6 loops the manifest's 19, then walks the
   bundle for forbidden tokens keyed on
   `("statusBadge", "badge", "modeBadge", "tag")` — `numbersBadge` is in
   neither list. The one thing CLOSEOUT §0.2 asks to be mechanically
   guaranteed is, for that slot, guaranteed only by the builder's own
   `status_badge()`. That is precisely the "a shared bug could agree with
   itself" failure the verifier's docstring says it exists to prevent.

3. **A machine-readable interface field is wrong.**
   `interface_ws12.badges` exports
   `{"positions_total": 19, "by_label": {..., "FROZEN-PROVISIONAL": 8, ...}}`.
   Measured against the app: 20 positions, `FROZEN-PROVISIONAL` 9.
   `report_assertions.json` asserts `interface_ws12 → badges →
   positions_total => '19'` against the bundle, so check 13 confirms the
   report against the same undercount; REPORT_WS12.md §0 repeats it
   ("19 badge positions render only the five labels"). The three-way
   discipline closes on a number that is wrong about the app.

**Not a promotion.** The emitted value is `FROZEN-PROVISIONAL`, which is
correct for WS8's numbers under v7 ("numbers FROZEN-PROVISIONAL at r3").
Nothing is promoted or demoted today. The defect is the enumeration and
the exported count.

**What would resolve it.** Harvest badges by key suffix rather than exact
name (`k.endswith("Badge")` / `k.endswith("statusBadge")`) in both
`collect_badges()` and check 6's forbidden-token walk, rebuild, and let
`positions_total` and `by_label` land where they land.

---

## WS12-r1-M3 — MATERIAL. The front door quotes v7's V1 sentence up to the semicolon and stops, dropping the conditionality v7 attaches to +20.11%

**Where.** `$.screens.verdict.cards[3].statusQuote`, the WS11 card on the
verdict wall — the front door, and the card that carries the program's
headline `+20.11%`.

**Rendered:**

> V1 Postal vs stock NPR: FROZEN-PROVISIONAL ADVANCE, +20.11% nominal
> ensemble-min per payload tonne-km, worst corner +19.12%, robust to all
> ruler-modelling brackets

**`BASELINE_v7_FREEZE.md` lines 31-35, in full:**

> V1 Postal vs stock NPR: FROZEN-PROVISIONAL ADVANCE, +20.11% nominal
> ensemble-min per payload tonne-km, worst corner +19.12%, robust to
> all ruler-modelling brackets**; conditional on R43(a)-(d) (cab heat,
> warm-up model, corner convention, CdA bracket), which were ordered
> and not run.**

The quote is verbatim as far as it goes and check 3 passes — a truncated
quotation always does, because check 3 only proves the displayed substring
is present in the file. What it drops is the only caveat v7 puts on the
+20.11%, and it drops it at the highest-traffic position in the exhibit.
The card's own body then amplifies the surviving half: *"V1's advance
improves under every ruler-modelling reversal, so its margin is a lower
bound."*

**R43 is not elsewhere on that card.** A repository-wide walk of the
bundle finds `R43` exactly once, on a different screen, in a list:
`$.screens.rounds.neverAdjudicated.orderedNeverRun` — *"Ordered and never
run, so not counted as rounds at all: KX r4, WS8 r4, WS9 r2, WS11 r3, and
R43(a)-(d) on V1's advance."* The four items are never named and the word
"conditional" never appears. `$.screens.method.limitations` has three
entries (ESC-1, no-hardware, unadjudicated) and does not include it.

**Contrast, so this reads as a real asymmetry and not a style note.** The
sibling card handles the same problem correctly: `race.semi.statusQuote`
also stops at a clause boundary, but the exhibit renders
`race.semi.openFindings` immediately beneath it carrying the exact
continuation ("with the Opus pre-adjudication's findings (PRE-B1..B3) on
the record against them and R46's trip-time consequence..."), so nothing
is lost. Card 3 has no such second quote.

**What would resolve it.** Extend `cards[3].statusQuote` to the end of
v7's sentence, or add a second quote beside it carrying the R43 clause —
the pattern `race.semi` already uses. Copy fix; no number moves.

---

## WS12-r1-M4 — MATERIAL. "Every renderable value carries a tier" is not true of the app; a class of rendered numbers with physical units sits outside the manifest, outside the tier discipline and outside every verifier check

**The claim.** REPORT_WS12.md §1: *"the three-tier badge discipline
(RECORD / DERIVED / SANDBOX) | now enforced mechanically: **every
renderable value carries a tier**"*. Method screen, `Method.tsx:115`:
*"Every number on every screen belongs to exactly one"*. Verifier check 1
is described as *"the manifest is exactly the set of renderable strings in
the bundle"*.

**What check 1 actually proves.** Its walker (`exhibit_verify.py:146`)
treats a dict as a renderable leaf iff it has both `"s"` and `"tier"`. So
it proves *manifest == the set of Cited-shaped objects in the bundle* —
not *manifest == the set of strings the app renders*. Any value the app
formats at run time from a raw bundle field, or computes in the browser,
is outside the manifest by construction and is never checked by anything.

**Exemplars, each a number with a physical unit on screen:**

| where | what renders | provenance on screen |
|---|---|---|
| `Simulator.tsx:975-978` | `LITRES`, `L/100 km`, `MJ / PAYLOAD t-km` — three counters the assignment orders by name (screen 4) | none; panel carries **no** TierBadge |
| `Simulator.tsx:653,658` | the constants those counters run on: `/ 832` and `* 42.8`, bare numeric literals | none — and the sim screen's whole subtree contains no occurrence of `42.8`, `832`, `LHV`, `kJ/g` or `g/L` |
| `Simulator.tsx:485-491` | `"R15 blend residual, bus / wheel: 44.8784 kW / 49.0130 kW against a 0.000469 kW printing tolerance"` — the number WS12-E5 is built on | raw bundle field, `.toFixed(4)`, no tier |
| `Simulator.tsx:844,851,854` | elevation span ` m`, `now … m`, `grade … %` | no tier |
| `Simulator.tsx:680-691` | twelve power-flow kW labels | no tier |
| `Method.tsx:215,253` | `"34.60 MB"` published payload; a `KiB` size for each of 28 source files | no tier |
| `RaceMode.tsx:175,178` | `"SPEED, PEAK … km/h"`, `"GRADE, PEAK … %"` | no tier |

**This is a discipline gap, not an error.** I re-derived the load-bearing
members myself and every one is right: the blend residuals reproduce to
the printed digit (44.8784 / 49.0130 kW over 5,158 / 5,178 braking samples
of 5,344 rows) from my own implementation of TRACE_SCHEMA's R15 rule;
`42.8` is `LHV_KJ_PER_G` at `WS4_genset/ws4_models.py:26` and `832` is
`DENSITY_G_PER_L` at `WS11_vehicle_zero_ruler/ws11_params.py:37`, both
exact; `34,602,996` bytes is the measured size of
`app/public/traces` + `app/public/maps`.

**Contrast, again showing the exhibit knows how to do this.** Race mode's
equivalent live counters carry `<TierBadge tier="DERIVED" />`
(`RaceMode.tsx:389,430`) and their constant is declared in the bundle
("LHV 42.8 kJ/g (WS4_genset/ws4_models.py:26)"). The simulator's do
neither.

**What would resolve it.** Put a `DERIVED` TierBadge on the simulator's
fuel-counter and power-flow panels and move `42.8` / `832` into the bundle
as cited constants the way race mode already does; or narrow the report's
and the Method screen's wording from "every renderable value" to "every
value of record", so the claim matches what check 1 proves.

---

# MINOR

## WS12-r1-m1 — MINOR. Check 5 never re-derives a derived number; 149 of the 488 manifest entries (31%) carry no numeric re-check, including the KX blocking figure

`exhibit_verify.py:286-298` asserts only that a `derived` entry has a
non-empty `derivedFrom` and does not claim a `path`. No value is
recomputed. Among the 149 are `rounds.kx.r6Radiator` = `103.522 kW` — the
number `BASELINE_v7_FREEZE` names in its KX line and the number R3-B1
turns on — and `rounds.kx.exceedance` = `+8.95%`.

I re-derived a sample independently and all of it reproduces:
`215.67009662126068 × 0.48 = 103.52164637820512`; seed 3 **is** the
maximum of the enumerated 8-seed set (tied to the last ULP with seeds 4
and 9), so the `derivedFrom` phrase "(max over the 8-seed set)" is
accurate; `103.52164637820512 / 95.01823316663226 − 1 = +8.949243664%`,
matching the `FINDINGS_KX_r3.md` quote rendered beside it. The race
screen's 10 Hz integrals likewise reproduce exactly (see clean-certs C6).

Recorded because the headline "1119 assertions, 0 failures, PASS" reads as
coverage of all 488 rendered strings when it is coverage of 339 of them
plus structural checks on the rest. The report's §0 wording is accurate;
the summary line is what invites the wrong reading.

## WS12-r1-m2 — MINOR. The decimation badge is up-cased before display, so the on-screen string is not the verbatim string CLOSEOUT §4 and the assignment specify

`RaceMode.tsx:112` and `Simulator.tsx:824` both render
`{badge.toUpperCase()}`. On screen the text reads
`THE REPLAY IS DECIMATED; THE RECORD IS NOT`, not
`the replay is decimated; the record is not`.

Check 10 (`exhibit_verify.py:529-542`) asserts the string in
`exhibit_data.json`, in `decimation_manifest.json → badge`, and in
`bundle.decimationBadge` — three assertions about the data, none about the
rendering. The one string the directive names as verbatim is the one the
verifier checks everywhere except where it is displayed. The badge is
present on both screens that display the 1 Hz tier, and its 10 Hz source
path is beside it, as ordered.

**Resolve by** rendering `{badge}` and up-casing in CSS
(`text-transform: uppercase`), or by adding the rendered form to check 10.

## WS12-r1-m3 — MINOR. Check 7's built-bundle scan is a silent no-op on a clean checkout and still reports PASS

`app/.gitignore` excludes `dist/`, and `git ls-files WS12_exhibit/app/dist`
returns 0 — the built bundle is not in the commit. Check 7(c)
(`exhibit_verify.py:394-409`) iterates `app/dist/assets/*.js` if the
directory exists; on a fresh clone `n_bundles = 0`, the loop body never
runs, and the check still `tick`s and passes. The strongest leg of "the
numbers can only arrive by fetching the data bundle" — the one that covers
the artifact a visitor actually downloads — vacuously passes unless
someone has run `npm run build` first. Nothing in the verifier's output
distinguishes the two cases except the assertion count (15 with a bundle,
14 without).

**Resolve by** failing check 7 when `app/dist/assets` holds no `.js`, or
by having `run_ws12.py` refuse the final verify without `--with-app`.

## WS12-r1-m4 — MINOR. The Method screen lists 11 of the verifier's 13 checks

`Method.tsx:268-279` renders eleven items under "What has to pass before
this page is allowed to exist". Checks **12 SEVERITIES** and **13 REPORT**
are absent. Both do real work: 12 re-parses every adjudication severity
count out of its own findings file, and 13 re-resolves the report's own
headline numbers. Under-claiming, but the exhibit's whole argument is that
its self-description is exact.

## WS12-r1-m5 — MINOR. `16.19 pp` is the ensemble-MIN of a cost and the screen does not say so, while its two neighbours do

`$.screens.race.headline.freightGiven` cites
`WS11 results → one_factor → rows → V2_on_VOLT-REG →
mass_payload_denominator → cost_pp` = `16.187444937496835` → `16.19 pp`,
labelled on screen `THE FREIGHT IT HANDED BACK TO GET THERE`
(`RaceMode.tsx:772`).

**The figure is right and I confirm it against the two sources CLOSEOUT
asked me to separate.** `REPORT_WS11.md` §0 says "hands back 16.19 points
of freight"; the assignment orders 16.19 citing that section; and the
exhibit binds to the results file, not to the prose. `16.34` is a
different member of the same set — `cost_pp_paired_max`, identical to
`cost_pp_unpaired_r1_statistic_of_statistics` — and it is correctly not
used. `REPORT_WS11.md` line 234 carries all of them: `16.19 pp (16.24) |
5.18 / 16.34`.

**What is missing** is the statistic. The record's own sibling fields are
`cost_pp_paired_min`, `cost_pp_paired_median` (16.24),
`cost_pp_paired_max` (16.34) and
`cost_pp_paired_min_governing_case: "seed 23 of the enumerated 8-seed
VOLT-REG ensemble"`. `cost_pp` is the *minimum* — the least freight given
back over the ensemble. Neither the label nor the provenance popup's path
text (`… → cost_pp`) says "min" or names the governing case, whereas the
two headline figures beside it resolve through paths ending `→ min`, so
their statistic is visible. Under R14 export discipline the governing case
belongs inline.

*One line, out of scope and left for the lead:* whether the ensemble-MIN
is the conservative member for a quantity that is a cost is a WS11
convention question, frozen under R52, and this round does not open it.

## WS12-r1-m6 — MINOR. "Both endpoints are on disk" — three Vehicle Zero constants that drive the sandbox are not in the citation map, and one is a literal in WS12's own source

`Sandbox.tsx:494` heads the endpoint panel "Both endpoints are on disk"
and renders `Object.keys(e.citations)`. For `endpoints.zero` that is seven
fields. Three more are in the endpoint dict, drive `ratioWindow()`'s
interpolation, and are absent from `citations`:

- `T_peak_Nm: 700.0` and `rpm_ceiling: 3000.0` — `max()` over WS1's
  `params → engine → trq_pts` / `rpm_pts` arrays (`ws12_sandbox.py:176-177`).
  On disk, but reduced by an operation the screen does not show.
- `v_climb_kmh: 60.0` — a **literal in `ws12_sandbox.py:67`**, commented
  "the speed WS1's own 6% cross-check is stated at". Traceable only
  through a JSON *key name* (`per_speed → "60kmh"`), not a value.

Separately, `endpoints.zero.CdA_m2 = 4.20 m²` is cited to WS1's params
with no flag, and the record declares it provisional: `REPORT_WS11.md`
records *"CdA 4.2 m^2 is a WS1 fitted value, declared PROVISIONAL in
BASELINE_v1 pending the WS7 coastdown"*, with CdA 5.4 carried as a sizing
bracket (E13) — an optimistic input inherited without a flag, on the one
screen a visitor drives. Mitigated, and why this is minor: the screen is
badged `SANDBOX — SIMPLIFIED PHYSICS, NOT A TRIAL RESULT` throughout, the
disclaimer says nothing on it may be quoted as a verdict, and the
interpolation is declared a sandbox construction.

## WS12-r1-m7 — MINOR. The draft in `design/` carries a promoted-status badge and a v4 baseline header into a repository about to be made public

`WS12_exhibit/design/Project Volt Exhibit.dc.html` (128,801 bytes, plus
`support.js`) is a self-contained, openable page. It contains, verbatim:
`RATIFIED RECORD` (a badge), `BASELINE v4 · RATIFIED 2026‑08‑30` (a
header), and the mulberry32 constant `0x6D2B79F5` driving the synthetic
trace generator. All three are exactly what R52 and the assignment
required the exhibit to delete, and REPORT_WS12.md §4 records them as cut.

Nothing is served: the file is outside `app/`, Vite never sees it, and the
only `Math.random` in `dist/assets/index-B3QuW4Lz.js` is React's internal
property-key salt. `README.md` calls `design/` "the original dc-runtime
draft, kept as the visual source". The draft itself carries no marker, and
CLOSEOUT §6 makes the repository public.

**Resolve by** a one-line `design/README.md` marking it superseded and
synthetic, or a filename prefix. It is not a defect in the exhibit.

## WS12-r1-m8 — MINOR. A bare `PROVISIONAL` reaches the built bundle, in a Label rather than a badge, where check 6 could not see it if it moved

`RaceMode.tsx:726` renders `<Label>WHY THESE STAY PROVISIONAL</Label>`. It
is the only bare `PROVISIONAL` in `dist/assets/index-B3QuW4Lz.js` (the
other five status tokens are all `FROZEN-*` / `NOT *` inside
`STATUS_STYLE`). It is prose in a section label, above two quotes that
both carry the frozen label, so it is **not** a promoted status in a badge
position and I am not calling it one.

Recorded because it shows the shape of the exposure in M2: check 6's
forbidden-token walk keys on four literal key names, `Label` text lives in
JSX and never enters the bundle as data, and neither the manifest nor the
verifier would notice if a bare status word migrated from a Label into a
badge slot named anything other than those four.

---

# CLEAN CERTIFICATIONS, BY FAMILY, WITH METHOD

Each was established by my own code or my own reading, not by re-running
`exhibit_verify.py` and trusting it. FM-4 in METHOD.md is the reason.

**C1 — All 239 cited numbers resolve and format. CLEAN.**
Wrote an independent resolver and formatter, opened each cited file,
walked each entry's explicit key list, compared the raw value to `v`, then
re-formatted as `pre + format(v, fmt) + suf` and compared to `s`.
**239 of 239 exact, 0 failures.** This is the whole `cite` family, not a
sample — it was cheaper to do all of them than to choose 40.

**C2 — All 46 quotations lift verbatim. CLEAN.**
Independent whitespace-normalised substring search against each source
file. **46 of 46 found.** I then swept all 46 for truncation by printing
the 110 characters that follow each quote in its source: 20 end at a
clause rather than a terminator, 19 of which drop nothing material
(verdict-line excerpts, or the continuation rendered as a second adjacent
quote, as `race.semi` does). The twentieth is M3.

**C3 — All 53 sha-pinned file identities re-hash; the one unpinned
reference is correctly unpinned. CLEAN.**
Re-hashed each file with SHA-256, compared digest and byte length, and
reconstructed the displayed string `basename · sha256 <8>…<4>`
independently. **53 of 53 exact.** The single `fileref` is `PM_LOG.md`,
carries no `sha256` key, and renders as its bare filename — correct for a
living log.

**C4 — The load-bearing headline set, re-derived from first principles.
CLEAN.**
- **G1 waterfall.** From `WS4_genset/results_ws4.json → interface_ws4 →
  gate_g1`: `prior_convention.min` 6.261345943773722 → `+6.26%`;
  `map_vs_scalar_alone.delta_pp_min` −7.013618051692167 → `−7.01 pp`;
  `spin_drag_alone.delta_pp_min` −1.7681550624315525 → `−1.77 pp`;
  interaction, which the exhibit badges DERIVED, computed by me as
  `both_g1r.delta_pp_min − a − b = −0.06121754760556186` → `−0.06 pp`,
  matching its stated derivation exactly; `6.261345943773722 +
  (−8.842990661729281) = −2.5816447179555597`, equal to
  `verdict.margin_pct_ensemble_min` = −2.5816447179555606 → `−2.58%`.
  Criterion 5.0, `missed_by_pp` 7.581644717955561 = 5.0 − (−2.5816…),
  0 of 8 seeds positive, governing case "seed 4 of 8-seed VOLT-REG
  ensemble [nominal]". All five bars and every surrounding field exact.
- **WS11's four verdict-carrying numbers.** +20.11 / +19.12 / −7.93 /
  −9.98 resolve to `interface_ws11 → verdicts → … →
  nominal_margin_pct_min` / `worst_corner_margin_pct`, and independently
  to `results → … → margin_pct_per_payload_tkm_paired → min`. The full
  precision (+20.114012 / +19.124037 / −7.925180 / −9.978769) is confirmed
  against `FINDINGS_WS11_r1.md`'s own three-way line. Every governing case
  is exported and rendered inline.
- **The dual-counter pair.** `+8.41%` = `results → V2_on_VOLT-REG →
  nominal → margin_pct_per_km_paired → min`. `16.19 pp` = `one_factor →
  … → cost_pp`, which the record equals to `cost_pp_paired_min`; the
  competing member `16.34` is `cost_pp_paired_max`, identical to the
  round-1 unpaired statistic-of-statistics, and is correctly not used.
  See m5 for the one thing missing (the statistic is not declared).
- **KX.** `95.018 kW` cites `heat_ledger_ws6 →
  series_duty_v2_transient_vs_R20_design_point →
  r20_design_point_radiator_package_kW` at 45.0 °C. `103.522 kW` is
  DERIVED; I enumerated all eight seeds of
  `series_duty_v2 → r6_rating_family_probe → cases →
  r6_rating_corner_full → per_seed` and confirmed seed 3 carries the
  maximum `engine_reject_2min_max_kW` (215.67009662126068, tied at the
  last ULP with seeds 4 and 9); × 0.48 = 103.52164637820512; exceedance
  +8.949243664%, matching the `FINDINGS_KX_r3.md` quote beside it and
  v7's own "103.5 vs 95.0 kW".
- **Round history, all 17 rows.** I opened every findings file and read
  its verdict line myself. All 17 severity triples match, including
  **WS11 r1 = 3 / 8 / 13** (`"NOT CLEAN — 3 blocking, 8 material, 13
  minor"`) and the two files with no verdict-line counts, WS3 r1 and r2,
  which I counted from severity-tagged headings: F1 BLOCKING, F2
  MATERIAL, F3-F6 MINOR = 1/1/4; N1, N2 MINOR = 0/0/2. Both match.
- **Sandbox.** Re-implemented the two closed forms from the equation as
  written and reproduced, term by term: WS1's 85 km/h flat ledger
  (1987.5751111111113 N), WS1's 6 % @ 60 km/h ledger (5159.454193792384 N),
  WS9's 6 % hold at 36,300 kg (23796.78122556096 N), and the ratio
  ceiling 3.769911184307752. Feeding WS8's own enumerated sweep through
  the bound gives `feasible_ratios == []` and `max(under) == 3.6`. **The
  exhibit does not conflate the two:** it labels 3.60:1 `HIGHEST SWEPT
  RATIO UNDER IT` and 3.769911:1 `RATIO CEILING, CLOSED FORM`, and shows
  both — which is what WS8's own `note` field demands
  ("the swept-set figure … is an illustration, not the limit").

**C5 — Status badges against v7. ONE EXCEPTION (M1); the rest CLEAN.**
Walked the bundle for every key matching `/[Bb]adge$/`, found 20 status
labels + 3 decimation strings, and checked each against v7 by subject, not
just by membership: 4 WS9 ADVANCE rows and the WS9 panel FROZEN-PROVISIONAL
(v7 "S6 / S4' / S5-13L / S7 FROZEN-PROVISIONAL ADVANCE"); S5 FROZEN-KILL
(v7 "S5-11L KILL"); G1 FROZEN-RATIFIED (v7 "architecture ratified");
4 WS8 rows + panel FROZEN-KILL and `numbersBadge` FROZEN-PROVISIONAL
(v7 "S1-S4 KILLED (final) … numbers FROZEN-PROVISIONAL at r3"); duty
sign-flip FROZEN-KILL / FROZEN-PROVISIONAL; WS11 pair
FROZEN-PROVISIONAL / FROZEN-KILL; KX NOT CONVERGED. **No promoted or
demoted status anywhere.** Grepped the built bundle
`dist/assets/index-B3QuW4Lz.js` directly: one occurrence each of
`FROZEN-KILL`, `FROZEN-PROVISIONAL`, `FROZEN-RATIFIED`, `NOT CONVERGED`,
`NOT CUT` (the `STATUS_STYLE` map), and one bare `PROVISIONAL` in a
section Label (m8). The eight publishable claims render v7's own
parenthetical status strings verbatim, in a text column, not as badges.

**C6 — No synthetic data survives. CLEAN, and independently proved for
all ten traces, not a spot-check.**
For each of the 10 published traces I re-hashed the source against
`sourceSha256`; counted its data rows against `sourceRows`; reconstructed
the 1 Hz file by taking source rows `0, stride, 2·stride, …` projected to
the kept columns as **verbatim field strings** and compared the full list
to `scrub_1hz.csv`; separately and independently proved the subsequence
property by greedy match, recording the source index of every matched row
and asserting the indices are strictly increasing; and checked every
segment file's header and row count and that the segments concatenate to
the full source row count.
**10 of 10 pass on every one of those checks. No averaging is possible:
every emitted field is byte-identical to a field in the source.** Totals
independently recomputed and matching the interface block: 512,557 source
rows, 51,263 at 1 Hz, 177 segments, stride 10, segment size 3,000,
54,392,870 source bytes, 34,359,646 published trace bytes, 34,602,996 with
the two maps; largest trace on disk
`WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` at
14,438,858 bytes, exactly as `interface_ws12.traces.largest_trace_in_tree`
records. Registry: 23 files on disk, 20 PRE-R34, 2 R34-conforming,
1 R34-refused — all match. The app source contains no PRNG, no generator
and no `Math.random`; the only two `Math.random` calls in the built bundle
are React's internal property-key salting.
I also re-derived the race screen's build-time 10 Hz integrals from the
source CSVs myself: fuel 2053.6875 g, distance 19.819519761 km,
1.2319199857 kWh/km, 2.468374 L for V1 nominal; 3163.5686 g,
1.8976905432 kWh/km, 3.802366 L for the ruler; SOC 0.5500 → 0.4495 ×
11.083608 kWh = 1.1139026 kWh drift. Every one matches the rendered string
to the last printed digit, and the WS12-E4 residual (−12.87 %) falls out
of them.

**C7 — Guard rail one holds in every screen's copy. CLEAN.**
Extracted every string ≥ 25 characters from the bundle (2,394 lines) and
every JSX string literal and text node from the 14 TS/TSX files, then swept
both for wording implying validation against physical reality
(`valid`, `real-world`, `proves`, `confirm`, `hardware`, `tested on`,
`accurate`, `correct physics`, …). **No hit implies validation.** The only
matches are the guard rail itself stating the opposite: *"No hardware was
built. The ruler is uncalibrated. Every verdict in this exhibit is
model-relative."* and *"No hardware was built and no physical test was run
at any point in this program. The method demonstrated here catches
internal inconsistency. It cannot catch wrong physics."* The Method
screen leads with both guard rails; ESC-1 is a limitation with the
uncalibrated-ruler citation attached; the verdict wall's WS11 card carries
an ESC-1 block with `calibrate_order_satisfied: False`.

**C8 — The 07:40 gap is rendered as the control condition, first and
unsoftened. CLEAN.**
`RoundHistory.tsx:201` renders `<GapCard>` as the first element after the
lede, before the round table and before the KX card, with the heat accent.
Title `"The control condition"`. Body: *"…Round 2 reworked all twenty-four
findings and passed the same mechanical gate. **Nothing adversarial has
read it.**"* A red callout carries `controlLine`: *"Remove the adversarial
reader and the output is immediately unverified. That is the finding."*
The severity block is headed `WHAT ROUND 2 CLOSED, AND NOTHING CHECKED`
(3 / 8 / 13). Four verbatim quotations sit beside it, all of which I
re-lifted from their sources: the principal's decision from `PM_LOG.md`,
*"…closes 3 blocking + 8 material + 13 minor findings and NOTHING WILL
HAVE CHECKED THAT WORK"*, *"a gate PASS on r2 is evidence of
reproducibility only…"*, and `NIGHT_REPORT.md`'s *"ADJUDICATION NOT RUN.
Cut by the principal at 07:40…"*. I found no softening language anywhere
on the card.

**C9 — Determinism and regeneration. CLEAN, verified by regenerating, not
by reading `determinism_check.txt`.**
Built a scratch sandbox outside the repo (symlinks to every root artifact,
a fresh copy of WS12's sources, no `app/public`, no `app/dist`) and ran the
pipeline there. `build_exhibit_data.py` → **all 191 emitted artifacts
byte-identical** to the committed tree (the 192nd, `verify_summary.json`,
is the verifier's output). `exhibit_verify.py` → `verify_summary.json`
byte-identical. `make_report_ws12.py` at the fixed point →
**`REPORT_WS12.md` and `report_assertions.json` byte-identical**. A second
`build_exhibit_data.py` → identical again. `npm run build` in the sandbox
→ **all 194 `dist/` files byte-identical**, including
`assets/index-B3QuW4Lz.js` under the same content hash, confirming the
committed bundle is built from the committed source. Vite `base` is
`'/project-volt/'` and `dist/index.html` emits
`src="/project-volt/assets/index-B3QuW4Lz.js"`, as CLOSEOUT §2 requires.
(Note for the foreman, not a finding: `app/dist/traces/` in the working
tree carries ten **empty** duplicate directories with macOS `" 2"` / `" 3"`
suffixes. `dist/` is gitignored and `git ls-files WS12_exhibit/app/dist`
returns 0, so none of it is in the commit and none of it can deploy.)

**C10 — Three-way verification of the machine-readable interface. CLEAN.**
Parsed the fenced JSON out of REPORT_WS12.md §9 and compared it to
`exhibit_data.json → interface_ws12`: structurally equal **and**
byte-identical when re-dumped under the builder's own
`indent=1, sort_keys=True, ensure_ascii=False`. Separately parsed all 239
rows of Appendix A and matched each `(screen element, file, key path,
rendered string)` against the manifest: **239 of 239 matched, 0
mismatches** — so report prose, manifest and the values I read off disk in
C1 agree three ways. Every scalar count in the interface block was
re-measured from the artifacts and matches, with the single exception in
M2: 6 screens, front door `verdict`, 488 / 239 / 46 / 53 / 1 / 149
manifest entries, 8 cut elements, 9 escalations, 28 sources, and the full
trace block in C6.

**C11 — Three verifier check-groups read against what they claim.**
- **Check 9 SUBSEQUENCE** — *stronger* than its claim. It reconstructs the
  strided sample from the original file on disk and compares full lists,
  and separately checks the 1 Hz file against the published segments. My
  own implementation agrees with it on all ten traces. Certified sound.
- **Check 12 SEVERITIES** — does what it claims. Its `_severities()`
  parser is genuinely written apart from the builder's, with a special
  case for WS3's two files, which carry no counts in their verdict lines
  and must be counted from severity-tagged headings. I re-read all 17
  files myself and agree with all 17 triples. Certified sound.
- **Check 6 BADGES** — does **not** do what it claims. Its first loop
  validates only the 19 manifest badges; its second walk inspects only
  keys named `statusBadge`, `badge`, `modeBadge`, `tag`. The app's
  twentieth badge position is named `numbersBadge` and is inspected by
  neither. This is M2.
- (Also read, and recorded above: check 1's leaf rule is narrower than
  "renderable strings" (M4); check 5 is a presence check, not a
  re-derivation (m1); check 7(c) is vacuous without a build (m3);
  check 10 checks the data, not the rendering (m2); check 13 resolves
  against the bundle, which is how M2's wrong count survives.)

**C12 — Assignment coverage. CLEAN.**
Verdict wall is the front door and leads with the G1 waterfall; race mode
carries the dual counters live, on four paired-seed WS11 datasets, with
the counters badged DERIVED and the numbers of record badged RECORD
beside them; the round-history screen exists and carries the 07:40 gap,
KX's NOT CONVERGED with 103.522 vs 95.018 kW, WS11 r1's 3/8/13, and the
detection rate under both readings; the simulator has play/pause/scrub and
a speed control (`Simulator.tsx:530,773`), the elevation profile, the R15
cascade, SOC and pack temperature, the engine dot on WS4's exported map,
and the ribbon drawn dashed with its seed shortfall stated; the sandbox
keeps the ratio window with re-derived constants and a unit test that
reproduces the S3 result; the decimated-replay rule is enforced on both
tiers with the badge present wherever the 1 Hz tier displays (case aside,
m2); and only the 10 traces the exhibit replays are published.
Escalations: **all 9 carry a `challenges` field naming the ruling they
challenge and all 9 read `NOT SELF-RESOLVED`.** The 8 cut elements each
state why the record cannot feed them, what is on the screen instead, and
the rule kept. I independently confirmed the semi-race cut's premise:
`results_ws9.json` contains no per-km margin key of any kind — its
`per_km` keys (`MJ_primary_per_km`, `bus_kWh_per_km`) are levels, and
every `margin` key is per payload tonne-km. WS13 consumes no
`interface_ws12` field, so M2's wrong count has not propagated.

---

*Placement note: the harness refused this adjudicator's direct file write
("Subagents should return findings as text"); the text above is returned
verbatim for the foreman to place at the adjudicator's mandated path, per
the precedent at PM_LOG.md:116. Nothing in `WS12_exhibit/` was opened
other than read-only, and nothing anywhere in the repository was modified
(`git status --short WS12_exhibit` is empty). This round disposes of
nothing.*

*Foreman placement note (close-out session, 2026-08-31).* Placed here
verbatim by the foreman from the adjudicator's returned text, unchanged
except HTML entity un-escaping introduced by transport. The foreman
authored none of the content above this note.