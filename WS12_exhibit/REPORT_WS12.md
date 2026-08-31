# REPORT_WS12 — THE EXHIBIT: THE METHOD, MADE CLICKABLE

Workstream WS12 · bound to `../BASELINE_v7_FREEZE.md` · entry point
`run_ws12.py` · results data `app/public/data/exhibit_data.json` · verifier
`exhibit_verify.py`

**What was built.** A static web app at `WS12_exhibit/app/` (Vite + React +
TypeScript, static, no server), Vite `base` set to `/project-volt/`,
deployable to GitHub Pages at a repo subpath. 6 screens, front door
`verdict`. Every number of record on every screen resolves to a file and an
explicit key path, and clicking it opens that provenance. 488 renderable
strings are enumerated in a build-time manifest; 239 of them are numbers of
record resolved from a results file, 46 are verbatim quotations lifted from
documents of record, 53 are file identities pinned by sha256, 1 is a
reference to a living log that is deliberately not hash-pinned, and 149 are
derived values that name what they were computed from and claim no key path.

**Verification.** `exhibit_verify.py` runs 13 checks and 1119 assertions
with its own resolver, its own formatter and its own findings-file parser,
written separately from the builder's so that a shared bug cannot agree with
itself. Result: **PASS**.

**The two guard rails hold.** The method claim is "catches internal
inconsistency" and never "catches wrong physics"; no hardware was built and
the ruler is uncalibrated, and the exhibit says so on the front door, in the
rail, and on the Method screen. No status is promoted: 19 badge positions
render only the five labels `BASELINE_v7_FREEZE.md` uses, the build refuses
to emit any other, and the verifier fails on a bare `RATIFIED` or
`PROVISIONAL` anywhere in a badge position.

---

## 1. What was ported, and what was replaced

The draft in `design/` is a dc-runtime prototype with a strong visual
system: a 1,920 × 1,080 instrument canvas, Chivo and DM Mono, a dark palette
with one accent, hairline-divided panels, a narrative rail, a three-tier
badge discipline and a provenance strip. **The look and the discipline were
kept. Everything synthetic was replaced by the record.**

### Kept

| element | how it survives |
|---|---|
| palette, typography, panel grid, hairlines, tabular numerals | ported verbatim into `app/src/theme.ts` and used everywhere |
| the narrative rail | six screens, re-ordered by the lead's ruling so the verdict wall is first |
| the three-tier badge discipline (RECORD / DERIVED / SANDBOX) | now enforced mechanically: every renderable value carries a tier, and the verifier checks that a DERIVED value never claims a key path |
| the provenance strip | now READ from the record per screen — baseline label and file identity come from the emitted bundle, not from a literal |
| the G1 waterfall | same shape, same five bars; every bar is now a citation |
| the sandbox ratio window | same interaction, all constants re-derived (see §5) |
| "a dashed baseline, never a zero line" | every signed bar carries a dashed zero and, where a criterion exists, a criterion marker |
| the copy, where it was true | corrected where the record has moved: the draft said BASELINE v4; this is bound to v7 and frozen |

### Replaced

| the draft did this | the exhibit does this |
|---|---|
| generated synthetic traces in the browser from an invented engine model, generator map, duty-cycle builder and seeded PRNG | replays trace files on disk, decimated at build time, with a run-time TRACE_SCHEMA check |
| hard-coded `S0`/`CAND` constants, r2-vintage and wrong against r3 | binds every WS8 margin to `results_ws8.json`; the draft's S1 nominal of −0.66% is −0.69% at r3, its S3 of −6.22% is −1.09% |
| a `RATIFIED RECORD` badge | v7's five status labels only |
| a `BASELINE v4 · RATIFIED 2026-08-30` header | the baseline label and identity, read from the bundle |
| an `AMBIENT TEMPERATURE` slider multiplying torque demand by an invented cold factor | an `AIR DENSITY` slider bounded by WS8's own three declared members |
| an approximated BSFC surface from a Willans fit in JavaScript | WS4's exported `bsfc_map_*.csv`, served and plotted directly |
| a synthetic elevation profile from summed bumps | `z_m` where the file has it, and an explicit statement of absence where it does not |

---

## 2. The screens

**1. Verdict wall — the front door.** The G1 waterfall leads: prior
convention +6.26%, the map-vs-scalar swap -7.01 pp, the spin-drag member
-1.77 pp, their interaction -0.06 pp, and the gate of record -2.58% against
a kill criterion of 5.0%, missed by 7.58 pp on 8 seeds with 0 above zero.
The card's copy makes plain that the criterion was written before the number
existed and could not be renegotiated, and quotes doctrine D1 to that
effect. Then the WS8 paired bars (per km beside per payload tonne-km, the
criterion read on the right-hand bar), the duty sign-flip, and the WS11
pair.

**2. Race mode.** Four paired-seed WS11 datasets. Two counters run live —
fuel per kilometre and fuel per payload tonne-km — and diverge as the replay
runs. The headline pair is bound to the record: V2 wins +8.41% per km, loses
-7.93% per payload tonne-km, and the freight it hands back to get there is
16.19 pp. The semi race is wired as a fifth dataset and renders FROZEN-
PROVISIONAL without a replay; §4 records why.

**3. Round history.** Every adjudication round in the program, with its
verdict line quoted verbatim and its severity counts parsed out of the
findings file rather than transcribed (§3). The 07:40 gap is the first card
on the screen, not the last: it is rendered as the control condition, with
the program log quoted at length and the count of what round 2 closed and
nothing checked. KX's NOT CONVERGED disposition follows, including the one
number on the verdict-bearing screens that could not be cited — which is
itself the finding.

**4. Simulator.** WS5's two R34-conforming duty traces, replayed. Elevation
from `z_m`, the R15 blend cascade from the four braking channels, SOC and
pack temperature, the engine dot on WS4's exported map for the engine that
trace actually ran, and fuel counters in litres, L/100 km and MJ per payload
tonne-km from the header's own payload. A trace registry measures every 10
Hz file in the repository against TRACE_SCHEMA and shows what each one
lacks.

**5. Sandbox.** The ratio window, re-derived (§5), with an on-screen anchor
table in which the browser's own model is run against the record's own force
ledgers and ratio ceiling.

**6. Method.** The two guard rails, the tier legend, the eight publishable
claims with the status each holds at the freeze, the limitations, the source
index with every file's sha256, and the verifier's own checklist.

---

## 3. Data bindings

Every number of record is bound at build time by `build_exhibit_data.py`,
which opens the results file, resolves an explicit **list** of keys (not a
dotted string — the record contains keys such as `V1_on_VOLT-SUB`,
`cold_-10C` and `CdA_5.4` that a dotted string cannot address), formats the
value with a declared format spec, and stores the raw value, the file, the
path, the spec and the displayed string together. The app renders the
displayed string and has no other way to print a number: `exhibit_verify.py`
check 7 asserts that no rendered numeral appears in the app's own source
**or in its built bundle**.

Severity counts on the round-history screen are parsed from the findings
files, not typed:

| ws | round | first pass | blocking | material | minor | counted by |
|---|---|---|---|---|---|---|
| WS2 | r1 | yes | 0 | 2 | 5 | read from the verdict line of WS2_traction_motor/FINDINGS_WS2_r1.md |
| WS2 | r2 | — | 0 | 1 | 2 | read from the verdict line of WS2_traction_motor/FINDINGS_WS2_r2.md |
| WS2 | r3 | — | 0 | 1 | 1 | read from the verdict line of WS2_traction_motor/FINDINGS_WS2_r3.md |
| WS2 | r4 | — | 0 | 0 | 2 | read from the verdict line of WS2_traction_motor/FINDINGS_WS2_r4.md |
| WS3 | r1 | yes | 1 | 1 | 4 | counted from the severity-tagged finding headings in WS3_battery/FINDINGS_WS3_r1.md |
| WS3 | r2 | — | 0 | 0 | 2 | counted from the severity-tagged finding headings in WS3_battery/FINDINGS_WS3_r2.md |
| WS4 | r1 | yes | 0 | 2 | 5 | read from the verdict line of WS4_genset/FINDINGS_WS4_r1.md |
| WS4 | r2 | — | 0 | 0 | 0 | read from the verdict line of WS4_genset/FINDINGS_WS4_r2.md ('no new findings of any severity') |
| WS4 | r3 | — | 0 | 1 | 4 | read from the verdict line of WS4_genset/FINDINGS_WS4_r3.md |
| KX | r1 | yes | 2 | 3 | 8 | read from the verdict line of WS4_genset/FINDINGS_KX_r1.md |
| KX | r2 | — | 0 | 3 | 4 | read from the verdict line of WS4_genset/FINDINGS_KX_r2.md |
| KX | r3 | — | 1 | 3 | 6 | read from the verdict line of WS4_genset/FINDINGS_KX_r3.md |
| WS8 | r1 | yes | 2 | 5 | 6 | read from the verdict line of WS8_semi_architecture/FINDINGS_WS8_r1.md |
| WS8 | r2 | — | 1 | 4 | 7 | read from the verdict line of WS8_semi_architecture/FINDINGS_WS8_r2.md |
| WS8 | r3 | — | 2 | 6 | 12 | read from the verdict line of WS8_semi_architecture/FINDINGS_WS8_r3.md |
| WS9 | pre-r1 | yes | 4 | 6 | 9 | read from the verdict line of WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md |
| WS11 | r1 | yes | 3 | 8 | 13 | read from the verdict line of WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md |

Quotations, all lifted from the file and re-lifted by the verifier:

| document | verbatim quotations on screen |
|---|---|
| `BASELINE_v5.md` | 1 |
| `BASELINE_v7_FREEZE.md` | 14 |
| `LEAD_HANDOVER.md` | 2 |
| `NIGHT_REPORT.md` | 1 |
| `PM_LOG.md` | 5 |
| `PM_PACKET_KX.md` | 2 |
| `TRACE_SCHEMA.md` | 1 |
| `WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md` | 1 |
| `WS2_traction_motor/FINDINGS_WS2_r1.md` | 1 |
| `WS2_traction_motor/FINDINGS_WS2_r2.md` | 1 |
| `WS2_traction_motor/FINDINGS_WS2_r3.md` | 1 |
| `WS2_traction_motor/FINDINGS_WS2_r4.md` | 1 |
| `WS3_battery/FINDINGS_WS3_r1.md` | 1 |
| `WS3_battery/FINDINGS_WS3_r2.md` | 1 |
| `WS4_genset/FINDINGS_KX_r1.md` | 1 |
| `WS4_genset/FINDINGS_KX_r2.md` | 1 |
| `WS4_genset/FINDINGS_KX_r3.md` | 2 |
| `WS4_genset/FINDINGS_WS4_r1.md` | 1 |
| `WS4_genset/FINDINGS_WS4_r2.md` | 1 |
| `WS4_genset/FINDINGS_WS4_r3.md` | 1 |
| `WS8_semi_architecture/FINDINGS_WS8_r1.md` | 1 |
| `WS8_semi_architecture/FINDINGS_WS8_r2.md` | 1 |
| `WS8_semi_architecture/FINDINGS_WS8_r3.md` | 2 |
| `WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md` | 1 |
| `WS9_vehicle_one_wave2/data/trace_S6_GH-REG-165_nominal_seed8101_10Hz.csv` | 1 |

The full binding table — 239 rows, screen element → file → key path →
rendered string — is in **Appendix A**.

---

## 4. Cut elements

The rule is *cut the element, not the rule*. Every draft element the record
cannot feed was cut, and the absence is stated on the screen where the
element would have been. 8 elements were cut.


**semi-race-replay** — the WS8/WS9 semi race as a replayed dual counter

- *why the record cannot feed it:* WS9's 10 Hz traces carry four commanded
  force channels and no fuel or electrical columns at all - the trace's own
  header says the electrical quantities are not in the file - and WS9
  exports no per-km MARGIN anywhere in results_ws9.json, only per-km levels.
  Neither counter has a column to integrate or a number of record to resolve
  to.
- *what is on the screen instead:* the dataset is wired into the same screen
  and renders as a verdict panel with FROZEN-PROVISIONAL badges, the
  criterion, both duties, and the absence stated on screen with the trace
  header quoted.
- *rule kept:* cut the element, not the rule

**sim-elevation-on-VOLT-SUB** — an elevation profile with relief on the V1
simulator trace

- *why the record cannot feed it:* VOLT-SUB's z_m column is present and
  constant: the duty is flat. Nothing is missing; there is simply no relief.
- *what is on the screen instead:* the profile is drawn as a flat line down
  the middle of its panel with the measured span printed beside it, rather
  than squashed onto the axis where it would read as absent data.
- *rule kept:* an unvarying signal is a fact about the record

**race-elevation** — the elevation profile on race mode

- *why the record cannot feed it:* WS11's r2 traces predate TRACE_SCHEMA and
  carry no z_m column. The exhibit will not integrate grade into an
  elevation it does not have.
- *what is on the screen instead:* the route strip plots v_kmh and
  grade_pct, both present, and says on screen that z_m is absent from the
  file.
- *rule kept:* never synthesize a missing column

**eight-seed-ribbon** — the 8-seed ribbon on the simulator

- *why the record cannot feed it:* a ribbon needs eight trace files per
  case; WS5 exports the reference seed only.
- *what is on the screen instead:* the ribbon panel is present, drawn
  dashed, and states the seed count it has against the seed count it needs.
- *rule kept:* absent (dashed) when not

**fault-trace-replay** — replay of WS5's brake-resistor-loss fault trace

- *why the record cannot feed it:* the file fails TRACE_SCHEMA's own R15
  blend-order sum rule by 44.9 kW on the bus cascade and 49.0 kW on the
  wheel closure, against a tolerance of about 5e-4 kW.
- *what is on the screen instead:* it is listed in the trace registry as
  REFUSED with the measured residuals and the tolerance, which is the loader
  rule doing exactly what it exists to do. It is not published.
- *rule kept:* refuse nonconforming files with a visible reason rather than
  plotting them

**sandbox-temperature-slider** — the draft's AMBIENT TEMPERATURE slider

- *why the record cannot feed it:* it multiplied the torque demand by `1 +
  max(0, 20 - T) * 0.0022`, a constant with no provenance anywhere in the
  record.
- *what is on the screen instead:* replaced by an AIR DENSITY slider bounded
  by WS8's own three declared members (cold, nominal, hot at altitude),
  which enters the aero term and nothing else.
- *rule kept:* if a figure is not traceable to a file, it is not shown as a
  result

**draft-synthetic-engine** — the draft's synthetic trace generator, engine
model, generator map and duty-cycle builder

- *why the record cannot feed it:* every number it produced was invented in
  the browser.
- *what is on the screen instead:* replaced wholesale by record replay:
  decimated trace files on disk and WS4's exported BSFC maps.
- *rule kept:* replace everything synthetic with the record

**draft-ratified-record-badge** — the draft's RATIFIED RECORD badge

- *why the record cannot feed it:* `RATIFIED` alone in a badge position is a
  build failure under BASELINE_v7_FREEZE R52.
- *what is on the screen instead:* badges render only v7's five labels, and
  `exhibit_verify.py` fails the build on any other.
- *rule kept:* no status is ever promoted

---

## 5. The sandbox, re-derived

The draft's ratio window ran on invented constants. Every one is replaced by
a value on disk, and the model is two closed forms:

```
F        = 0.5 rho CdA v^2 + Crr m g cos(theta) + m g sin(theta),  theta = atan(grade)
ratio_max = rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)     [WS8's own published bound]
ratio_min = F_grade_hold * r_dyn / (T_peak * eta_driveline)  [the same statement, inverted]
g         = 9.81 m/s^2, declared identically at WS1 volt_params.py:10 and WS8 ws8_params.py:24
```

`test_sandbox_ws12.py` reproduces, from those functions and nothing else:

- WS1's own flat-cruise force ledger at 85 km/h, term by term;
- WS1's own 6% grade ledger at 60 km/h, term by term;
- WS9's exported 6% grade-hold ledger at 36,300 kg, term by term;
- WS8's published closed-form ratio ceiling, and WS9's to one ulp;
- `feasible_ratios == []` and `max_ratio_without_overspeed == 3.6` — the
  3.60:1 ceiling — by running WS8's own enumerated ratio sweep through the
  same two bounds;
- the ratio the 6% hold needs for both engines, and the force available at
  the ceiling, which is a little over half what the grade demands.

All of it runs as check 11 of the verifier. The same model is implemented in
TypeScript for the browser, and the Sandbox screen prints its output beside
the record's for each anchor so a divergence between the two implementations
would be visible on the page.

---

## 6. Traces and the decimated-replay rule

No 10 Hz file is fetched whole on page load. Every published trace is
emitted as a 1 Hz whole-trace scrub index, decimated **by strided sample and
never by averaging**, plus 10 Hz segment chunks fetched one at a time for
the segment in view. Every emitted field is the **verbatim field string**
from the source file, so the 1 Hz tier is a literal subsequence of the
source and the verifier can prove it by string equality — against the
published segments and, independently, against the original file on disk.

- Traces published: **10**
- Stride: **10** (10 Hz → 1 Hz), segment size **3000** rows
- Source rows at 10 Hz: **512,557**; 1 Hz index rows: **51,263**; segments:
  **177**
- Source bytes: **54,392,870** → published bytes: **34,359,646** (34.36 MB),
  by projecting each file to the columns its screen actually plots at the
  source's own precision
- On-screen badge, verbatim, whenever the 1 Hz tier is displayed: **the
  replay is decimated; the record is not**, with the full 10 Hz source path
  beside it
- Every other trace in the repository is linked by path and not served

| published trace | class | source rows | 1 Hz rows | segments | published bytes | columns kept / in source |
|---|---|---|---|---|---|---|
| `WS11_vehicle_zero_ruler/data/trace_V1_VOLT-SUB_cold_-10C_seed11_10Hz.csv` | PRE-R34 | 34852 | 3486 | 12 | 1754858 | 6 / 11 |
| `WS11_vehicle_zero_ruler/data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` | PRE-R34 | 34852 | 3486 | 12 | 1754558 | 6 / 11 |
| `WS11_vehicle_zero_ruler/data/trace_V2_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv` | PRE-R34 | 69934 | 6994 | 24 | 3636098 | 6 / 11 |
| `WS11_vehicle_zero_ruler/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` | PRE-R34 | 66143 | 6615 | 23 | 3435903 | 6 / 11 |
| `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv` | PRE-R34 | 69934 | 6994 | 24 | 3097502 | 5 / 10 |
| `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-REG_nominal_seed23_10Hz.csv` | PRE-R34 | 66143 | 6615 | 23 | 2926501 | 5 / 10 |
| `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-SUB_cold_-10C_seed11_10Hz.csv` | PRE-R34 | 34852 | 3486 | 12 | 1486440 | 5 / 10 |
| `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-SUB_nominal_seed11_10Hz.csv` | PRE-R34 | 34852 | 3486 | 12 | 1486140 | 5 / 10 |
| `WS5_controls/data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` | R34 | 34852 | 3486 | 12 | 4016156 | 25 / 35 |
| `WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` | R34 | 66143 | 6615 | 23 | 10765490 | 25 / 35 |

Adding the two BSFC maps, the served payload (app/public/traces +
app/public/maps) is **34,602,996 bytes** (34.60 MB). The data bundle and the
two manifests are served alongside it and add well under a megabyte; their
size is deliberately not stated as a bound field, because the field would
live inside the bundle it was measuring.

### The trace registry

The loader validates TRACE_SCHEMA at build time and again at run time in the
browser, and refuses a nonconforming file with a visible reason rather than
plotting it. Of 23 trace files in the repository, 2 conform to R34, 1 is
refused, and 20 predate the schema and are measured against it rather than
validated by it.

| workstream | trace | rows | cols | schema | served |
|---|---|---|---|---|---|
| WS1 | `WS1_loads_duty_cycles/data/trace_VOLT-SUB_V1_10Hz.csv` | 34852 | 7 | PRE-R34 | linked only |
| WS1 | `WS1_loads_duty_cycles/data/trace_VOLT-REG_V2_10Hz.csv` | 66143 | 9 | PRE-R34 | linked only |
| WS4 | `WS4_genset/data/trace_series_duty_v2_nominal_seed23_10Hz.csv` | 66143 | 11 | PRE-R34 | linked only |
| WS4 | `WS4_genset/data/trace_series_duty_v2_alt2000m_45C_seed23_10Hz.csv` | 66143 | 11 | PRE-R34 | linked only |
| WS4 | `WS4_genset/data/trace_series_duty_v2_cda_5.4_seed23_10Hz.csv` | 66143 | 11 | PRE-R34 | linked only |
| WS5 | `WS5_controls/data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` | 34852 | 35 | R34 CONFORMS | yes |
| WS5 | `WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` | 66143 | 35 | R34 CONFORMS | yes |
| WS5 | `WS5_controls/data/trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv` | 5344 | 35 | R34 REFUSED | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S0R_GH-REG-165_nominal_seed8101_10Hz.csv` | 99417 | 8 | PRE-R34 | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S4p_GH-REG-165_nominal_seed8101_10Hz.csv` | 96453 | 8 | PRE-R34 | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S5-13L_GH-REG-165_nominal_seed8101_10Hz.csv` | 103823 | 8 | PRE-R34 | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S5_GH-REG-165_nominal_seed8101_10Hz.csv` | 110535 | 8 | PRE-R34 | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S6_GH-REG-165_nominal_seed8101_10Hz.csv` | 99655 | 8 | PRE-R34 | linked only |
| WS9 | `WS9_vehicle_one_wave2/data/trace_S7_GH-REG-165_nominal_seed8101_10Hz.csv` | 99138 | 8 | PRE-R34 | linked only |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` | 34852 | 11 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_V1_VOLT-SUB_cold_-10C_seed11_10Hz.csv` | 34852 | 11 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` | 66143 | 11 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_V2_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv` | 69934 | 11 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_V2_VOLT-SUB_nominal_seed11_10Hz.csv` | 34852 | 11 | PRE-R34 | linked only |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-SUB_nominal_seed11_10Hz.csv` | 34852 | 10 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-SUB_cold_-10C_seed11_10Hz.csv` | 34852 | 10 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-REG_nominal_seed23_10Hz.csv` | 66143 | 10 | PRE-R34 | yes |
| WS11 | `WS11_vehicle_zero_ruler/data/trace_ruler_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv` | 69934 | 10 | PRE-R34 | yes |

---

## 7. Verification results

| check | assertions | failures | result |
|---|---|---|---|
| 1 MANIFEST/BUNDLE | 488 | 0 | PASS |
| 2 CITATIONS | 239 | 0 | PASS |
| 3 QUOTES | 46 | 0 | PASS |
| 4 FILE FACTS | 54 | 0 | PASS |
| 5 DERIVED | 149 | 0 | PASS |
| 6 BADGES | 20 | 0 | PASS |
| 7 APP SOURCE | 15 | 0 | PASS |
| 8 DECIMATION | 10 | 0 | PASS |
| 9 SUBSEQUENCE | 10 | 0 | PASS |
| 10 DECIMATION BADGE | 1 | 0 | PASS |
| 11 SANDBOX | 27 | 0 | PASS |
| 12 SEVERITIES | 17 | 0 | PASS |
| 13 REPORT | 43 | 0 | PASS |
| **total** | **1119** | **0** | **PASS** |

Determinism: `check_determinism_ws12.py --with-app` builds the data pipeline
twice and the app twice and compares every emitted artifact by sha256.
Result recorded in `determinism_check.txt`.

---

## 8. Escalations

Under the freeze there is no workstream to escalate to. Each item below is
recorded here and, per the assignment, is for `LIMITATIONS.md` via WS13.
**None is self-resolved.** 9 items.


### WS12-E1 — five-for-five or seven-for-seven: the record and this assignment disagree on the denominator

**Challenges:** WS12_exhibit/ASSIGNMENT.md, screen 3, and
BASELINE_v7_FREEZE.md claim 8

BASELINE_v7_FREEZE.md claim 8 says 'five-for-five first-pass defect
detection', and R37 in BASELINE_v5.md states the same base rate; PM_LOG.md
repeats it three times. This workstream's own assignment orders 'the seven-
for-seven first-pass defect rate'. Seven first-pass adjudication findings
files exist on disk (WS2 r1, WS3 r1, WS4 r1, KX r1, WS8 r1, WS9 pre-r1, WS11
r1) and all seven record at least one blocking or material finding. The
difference is whether the KX round's own first pass and the WS9 pre-
adjudication count. The exhibit renders BOTH readings with their scope and
their source and promotes neither.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E2 — D5's first-pass range names WS1; the disk has no WS1 adjudication

**Challenges:** LEAD_HANDOVER.md doctrine D5

D5 reads 'Every first-pass adjudication in this program (WS1-WS4) found
material or blocking defects'. No FINDINGS_WS1_r*.md exists anywhere in the
repository and PM_LOG.md carries no WS1 entry; WS1 was closed by lead
ratification in BASELINE_v1. The exhibit's per-workstream table records WS1
as one round run and zero adjudications, and its gap-set panel says so in
the same words.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E3 — v7 points WS5's status at a packet that was never written

**Challenges:** BASELINE_v7_FREEZE.md, final research state, WS5 line

v7 reads 'WS5: status per its packet at freeze'. No PM_PACKET_WS5.md exists
at the repository root; the four packets that do exist are KX, WS2, WS3 and
WS4. WS5's own results file carries its status instead ('gated-but-
unadjudicated'), and the exhibit renders that string rather than inventing a
packet.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E4 — WS11's trace fuel column does not integrate to WS11's own per-seed fuel

**Challenges:** R34 / TRACE_SCHEMA.md, and the WS11 r2 round

Integrating each WS11 r2 trace's own fuel_g_per_s column at its own 0.1 s
step and dividing by the distance its own v_kmh column travels gives a fuel
energy per kilometre that differs from the same seed's exported figure by
-12.87% and -13.19% on the two V1 cases, -0.65% and -1.29% on the two V2
candidate cases, and -0.00%, -0.36% and -2.93% on the three ruler cases. Two
mechanisms the record itself names account for most of it - the pipeline
books charge-neutral fuel (WS4 exports fuel_g and fuel_corrected_g side by
side) and the ruler is charged for 3.2582 kWh of work it could not do on the
climb - and they do not close it completely. V1's cold corner is one of the
affected cases and is the corner V1's ADVANCE is decided on. This exhibit
does not attempt to close the residual; it prints the measured difference on
the screen beside the number of record. The affected round is the one whose
adjudication was cut at 07:40.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead and for
LIMITATIONS.md via WS13.

### WS12-E5 — the R15 blend-order sum rule does not close on WS5's fault trace

**Challenges:** TRACE_SCHEMA.md, blend-order rule, against WS5's fault trace

On `trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv` the bus cascade
misses by up to 44.8784 kW and the wheel closure by up to 49.0130 kW,
against a tolerance of about 5e-4 kW; the two conforming duty traces miss by
at most 5.0e-4 kW on terms of order 100 kW. At the worst sample
P_motor_mech_kW still carries the full braking demand while
P_friction_brake_kW carries almost all of it as well. The exhibit refuses
the file, states the residuals, and does not publish it. This is an
observation against the schema's own rule, not a verdict on WS5, and WS5 was
never adjudicated.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead and for
LIMITATIONS.md via WS13.

### WS12-E6 — P_bus_load_kW is defined as 'accessories + heater' and used as the total bus load

**Challenges:** TRACE_SCHEMA.md, Electrified columns

In both conforming WS5 traces P_bus_load_kW sits exactly 2.0 kW above
P_motor_bus_kW at every sample - it is the total bus load, not the accessory
load the schema names. The exhibit shows the accessory term as the
difference of the two columns, badged DERIVED, and states the divergence on
the screen.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E7 — the largest trace named in the rule does not exist under that name

**Challenges:** WS12_exhibit/ASSIGNMENT.md, screen 4, decimated-replay rule

The rule cites 'the largest in the tree is 10.22 MB
(WS5_controls/data/trace_v2_load_follow_nominal_seed23_10Hz.csv)'. No file
of that name exists. The largest trace in the repository is
`WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` at 14,438,858
bytes. The rule is applied to that file, which is the one the description
clearly means; the discrepancy is recorded rather than silently corrected.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E8 — WS11's r2 traces do not conform to the schema they are named as the reference for

**Challenges:** TRACE_SCHEMA.md, 'WS11's r2 traces are the reference
implementation'

TRACE_SCHEMA.md was issued at 07:54; WS11's r2 traces were written at 07:32.
They carry free-text comment headers with none of the fourteen mandatory `#
key: value` keys, and they are missing seven of the ten core columns (x_m,
z_m, fuel_cum_g, P_friction_brake_kW, trip_time_flag among them) and every
electrified column the schema names except P_gen_bus_kW and P_bus_load_kW.
The exhibit classes them PRE-R34, publishes them for race mode with the
exact list of what they lack, and plots only the columns they carry. The
only R34-conforming trace files in the repository are WS5's two duty traces.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead.

### WS12-E9 — both WS5 trace headers declare the RULER's payload for a candidate vehicle

**Challenges:** TRACE_SCHEMA.md, mandatory header key `payload_kg`

`trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` and `trace_V2_VOLT-
REG_nominal_seed23_10Hz.csv` both carry `# payload_kg: 2900.0` at `#
mass_kg: 6600.0`. 2,900 kg is the stock NPR-HD's payload at GVW in WS11's
ratified mass ledger; the same ledger gives V1 2,712 kg and V2 2,461 kg at
the same gross weight, because both candidates carry powertrain mass the
ruler does not. The assignment orders the simulator's MJ per payload tonne-
km counter to run 'from header payload', so it does, and the screen prints
the header value, its key, and WS11's ledger figure for the same vehicle
beside it. Nothing of WS5's turns on it - WS5 claims no efficiency advantage
anywhere - but the mandatory header field does not agree with the mass
ledger of record, and WS5 was never adjudicated.

**Disposition:** NOT SELF-RESOLVED. Recorded for the lead and for
LIMITATIONS.md via WS13.

---

## 9. Machine-readable interface block

Every field below is `app/public/data/exhibit_data.json` → `interface_ws12`,
verbatim.

```json
{
 "_basis": "facts about the EXHIBIT, not about the trucks. Every number here is derived from the emitted bundle and the two manifests, and exhibit_verify.py re-derives each of them from the artifacts on disk before the build is allowed to pass.",
 "_status": "WS12 exhibit, first pass, bound to BASELINE_v7_FREEZE.md",
 "app": {
  "front_door": "verdict",
  "screens": [
   "method",
   "race",
   "rounds",
   "sandbox",
   "sim",
   "verdict"
  ],
  "screens_n": 6,
  "stack": "Vite + React + TypeScript, static, no server",
  "vite_base": "/project-volt/"
 },
 "badges": {
  "by_label": {
   "FROZEN-KILL": 8,
   "FROZEN-PROVISIONAL": 8,
   "FROZEN-RATIFIED": 1,
   "NOT CONVERGED": 1,
   "NOT CUT": 1
  },
  "positions_total": 19
 },
 "cut_elements": [
  {
   "element": "the WS8/WS9 semi race as a replayed dual counter",
   "id": "semi-race-replay",
   "kept": "the dataset is wired into the same screen and renders as a verdict panel with FROZEN-PROVISIONAL badges, the criterion, both duties, and the absence stated on screen with the trace header quoted.",
   "rule": "cut the element, not the rule",
   "why": "WS9's 10 Hz traces carry four commanded force channels and no fuel or electrical columns at all - the trace's own header says the electrical quantities are not in the file - and WS9 exports no per-km MARGIN anywhere in results_ws9.json, only per-km levels. Neither counter has a column to integrate or a number of record to resolve to."
  },
  {
   "element": "an elevation profile with relief on the V1 simulator trace",
   "id": "sim-elevation-on-VOLT-SUB",
   "kept": "the profile is drawn as a flat line down the middle of its panel with the measured span printed beside it, rather than squashed onto the axis where it would read as absent data.",
   "rule": "an unvarying signal is a fact about the record",
   "why": "VOLT-SUB's z_m column is present and constant: the duty is flat. Nothing is missing; there is simply no relief."
  },
  {
   "element": "the elevation profile on race mode",
   "id": "race-elevation",
   "kept": "the route strip plots v_kmh and grade_pct, both present, and says on screen that z_m is absent from the file.",
   "rule": "never synthesize a missing column",
   "why": "WS11's r2 traces predate TRACE_SCHEMA and carry no z_m column. The exhibit will not integrate grade into an elevation it does not have."
  },
  {
   "element": "the 8-seed ribbon on the simulator",
   "id": "eight-seed-ribbon",
   "kept": "the ribbon panel is present, drawn dashed, and states the seed count it has against the seed count it needs.",
   "rule": "absent (dashed) when not",
   "why": "a ribbon needs eight trace files per case; WS5 exports the reference seed only."
  },
  {
   "element": "replay of WS5's brake-resistor-loss fault trace",
   "id": "fault-trace-replay",
   "kept": "it is listed in the trace registry as REFUSED with the measured residuals and the tolerance, which is the loader rule doing exactly what it exists to do. It is not published.",
   "rule": "refuse nonconforming files with a visible reason rather than plotting them",
   "why": "the file fails TRACE_SCHEMA's own R15 blend-order sum rule by 44.9 kW on the bus cascade and 49.0 kW on the wheel closure, against a tolerance of about 5e-4 kW."
  },
  {
   "element": "the draft's AMBIENT TEMPERATURE slider",
   "id": "sandbox-temperature-slider",
   "kept": "replaced by an AIR DENSITY slider bounded by WS8's own three declared members (cold, nominal, hot at altitude), which enters the aero term and nothing else.",
   "rule": "if a figure is not traceable to a file, it is not shown as a result",
   "why": "it multiplied the torque demand by `1 + max(0, 20 - T) * 0.0022`, a constant with no provenance anywhere in the record."
  },
  {
   "element": "the draft's synthetic trace generator, engine model, generator map and duty-cycle builder",
   "id": "draft-synthetic-engine",
   "kept": "replaced wholesale by record replay: decimated trace files on disk and WS4's exported BSFC maps.",
   "rule": "replace everything synthetic with the record",
   "why": "every number it produced was invented in the browser."
  },
  {
   "element": "the draft's RATIFIED RECORD badge",
   "id": "draft-ratified-record-badge",
   "kept": "badges render only v7's five labels, and `exhibit_verify.py` fails the build on any other.",
   "rule": "no status is ever promoted",
   "why": "`RATIFIED` alone in a badge position is a build failure under BASELINE_v7_FREEZE R52."
  }
 ],
 "cut_elements_n": 8,
 "entry_points": {
  "all": "run_ws12.py",
  "build": "build_exhibit_data.py",
  "determinism": "check_determinism_ws12.py",
  "report": "make_report_ws12.py",
  "sandbox_test": "test_sandbox_ws12.py",
  "verify": "exhibit_verify.py"
 },
 "escalations": [
  {
   "challenges": "WS12_exhibit/ASSIGNMENT.md, screen 3, and BASELINE_v7_FREEZE.md claim 8",
   "detail": "BASELINE_v7_FREEZE.md claim 8 says 'five-for-five first-pass defect detection', and R37 in BASELINE_v5.md states the same base rate; PM_LOG.md repeats it three times. This workstream's own assignment orders 'the seven-for-seven first-pass defect rate'. Seven first-pass adjudication findings files exist on disk (WS2 r1, WS3 r1, WS4 r1, KX r1, WS8 r1, WS9 pre-r1, WS11 r1) and all seven record at least one blocking or material finding. The difference is whether the KX round's own first pass and the WS9 pre-adjudication count. The exhibit renders BOTH readings with their scope and their source and promotes neither.",
   "headline": "five-for-five or seven-for-seven: the record and this assignment disagree on the denominator",
   "id": "WS12-E1",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "LEAD_HANDOVER.md doctrine D5",
   "detail": "D5 reads 'Every first-pass adjudication in this program (WS1-WS4) found material or blocking defects'. No FINDINGS_WS1_r*.md exists anywhere in the repository and PM_LOG.md carries no WS1 entry; WS1 was closed by lead ratification in BASELINE_v1. The exhibit's per-workstream table records WS1 as one round run and zero adjudications, and its gap-set panel says so in the same words.",
   "headline": "D5's first-pass range names WS1; the disk has no WS1 adjudication",
   "id": "WS12-E2",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "BASELINE_v7_FREEZE.md, final research state, WS5 line",
   "detail": "v7 reads 'WS5: status per its packet at freeze'. No PM_PACKET_WS5.md exists at the repository root; the four packets that do exist are KX, WS2, WS3 and WS4. WS5's own results file carries its status instead ('gated-but-unadjudicated'), and the exhibit renders that string rather than inventing a packet.",
   "headline": "v7 points WS5's status at a packet that was never written",
   "id": "WS12-E3",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "R34 / TRACE_SCHEMA.md, and the WS11 r2 round",
   "detail": "Integrating each WS11 r2 trace's own fuel_g_per_s column at its own 0.1 s step and dividing by the distance its own v_kmh column travels gives a fuel energy per kilometre that differs from the same seed's exported figure by -12.87% and -13.19% on the two V1 cases, -0.65% and -1.29% on the two V2 candidate cases, and -0.00%, -0.36% and -2.93% on the three ruler cases. Two mechanisms the record itself names account for most of it - the pipeline books charge-neutral fuel (WS4 exports fuel_g and fuel_corrected_g side by side) and the ruler is charged for 3.2582 kWh of work it could not do on the climb - and they do not close it completely. V1's cold corner is one of the affected cases and is the corner V1's ADVANCE is decided on. This exhibit does not attempt to close the residual; it prints the measured difference on the screen beside the number of record. The affected round is the one whose adjudication was cut at 07:40.",
   "headline": "WS11's trace fuel column does not integrate to WS11's own per-seed fuel",
   "id": "WS12-E4",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for LIMITATIONS.md via WS13."
  },
  {
   "challenges": "TRACE_SCHEMA.md, blend-order rule, against WS5's fault trace",
   "detail": "On `trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv` the bus cascade misses by up to 44.8784 kW and the wheel closure by up to 49.0130 kW, against a tolerance of about 5e-4 kW; the two conforming duty traces miss by at most 5.0e-4 kW on terms of order 100 kW. At the worst sample P_motor_mech_kW still carries the full braking demand while P_friction_brake_kW carries almost all of it as well. The exhibit refuses the file, states the residuals, and does not publish it. This is an observation against the schema's own rule, not a verdict on WS5, and WS5 was never adjudicated.",
   "headline": "the R15 blend-order sum rule does not close on WS5's fault trace",
   "id": "WS12-E5",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for LIMITATIONS.md via WS13."
  },
  {
   "challenges": "TRACE_SCHEMA.md, Electrified columns",
   "detail": "In both conforming WS5 traces P_bus_load_kW sits exactly 2.0 kW above P_motor_bus_kW at every sample - it is the total bus load, not the accessory load the schema names. The exhibit shows the accessory term as the difference of the two columns, badged DERIVED, and states the divergence on the screen.",
   "headline": "P_bus_load_kW is defined as 'accessories + heater' and used as the total bus load",
   "id": "WS12-E6",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "WS12_exhibit/ASSIGNMENT.md, screen 4, decimated-replay rule",
   "detail": "The rule cites 'the largest in the tree is 10.22 MB (WS5_controls/data/trace_v2_load_follow_nominal_seed23_10Hz.csv)'. No file of that name exists. The largest trace in the repository is `WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` at 14,438,858 bytes. The rule is applied to that file, which is the one the description clearly means; the discrepancy is recorded rather than silently corrected.",
   "headline": "the largest trace named in the rule does not exist under that name",
   "id": "WS12-E7",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "TRACE_SCHEMA.md, 'WS11's r2 traces are the reference implementation'",
   "detail": "TRACE_SCHEMA.md was issued at 07:54; WS11's r2 traces were written at 07:32. They carry free-text comment headers with none of the fourteen mandatory `# key: value` keys, and they are missing seven of the ten core columns (x_m, z_m, fuel_cum_g, P_friction_brake_kW, trip_time_flag among them) and every electrified column the schema names except P_gen_bus_kW and P_bus_load_kW. The exhibit classes them PRE-R34, publishes them for race mode with the exact list of what they lack, and plots only the columns they carry. The only R34-conforming trace files in the repository are WS5's two duty traces.",
   "headline": "WS11's r2 traces do not conform to the schema they are named as the reference for",
   "id": "WS12-E8",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead."
  },
  {
   "challenges": "TRACE_SCHEMA.md, mandatory header key `payload_kg`",
   "detail": "`trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` and `trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` both carry `# payload_kg: 2900.0` at `# mass_kg: 6600.0`. 2,900 kg is the stock NPR-HD's payload at GVW in WS11's ratified mass ledger; the same ledger gives V1 2,712 kg and V2 2,461 kg at the same gross weight, because both candidates carry powertrain mass the ruler does not. The assignment orders the simulator's MJ per payload tonne-km counter to run 'from header payload', so it does, and the screen prints the header value, its key, and WS11's ledger figure for the same vehicle beside it. Nothing of WS5's turns on it - WS5 claims no efficiency advantage anywhere - but the mandatory header field does not agree with the mass ledger of record, and WS5 was never adjudicated.",
   "headline": "both WS5 trace headers declare the RULER's payload for a candidate vehicle",
   "id": "WS12-E9",
   "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for LIMITATIONS.md via WS13."
  }
 ],
 "escalations_n": 9,
 "guard_rails": {
  "allowed_status_badges": [
   "FROZEN-PROVISIONAL",
   "FROZEN-KILL",
   "FROZEN-RATIFIED",
   "NOT CONVERGED",
   "NOT CUT"
  ],
  "forbidden_badge_tokens": [
   "RATIFIED",
   "PROVISIONAL"
  ],
  "method_claim": "catches internal inconsistency",
  "method_claim_never": "catches wrong physics",
  "status_promotion": "none; badges render only v7's five labels"
 },
 "manifest": {
  "by_kind": {
   "cite": 239,
   "derived": 149,
   "file": 53,
   "fileref": 1,
   "quote": 46
  },
  "by_tier": {
   "DERIVED": 95,
   "RECORD": 393
  },
  "entries_total": 488
 },
 "maps_published": [
  "bsfc_map_V1_candidate.csv",
  "bsfc_map_V2_candidate.csv"
 ],
 "published_payload_bytes": 34602996,
 "published_payload_scope": "app/public/traces + app/public/maps",
 "sources_cited_n": 28,
 "traces": {
  "badge": "the replay is decimated; the record is not",
  "decimation": "strided sample, never averaged",
  "largest_trace_in_tree": {
   "bytes": 14438858,
   "file": "WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv"
  },
  "published_bytes": 34359646,
  "published_n": 10,
  "registry_pre_r34": 20,
  "registry_r34_conforming": 2,
  "registry_r34_refused": 1,
  "registry_total": 23,
  "rows_1Hz": 51263,
  "segment_rows": 3000,
  "segments_total": 177,
  "source_bytes": 54392870,
  "source_rows_10Hz": 512557,
  "stride": 10
 }
}
```

---

## Appendix A — the full binding table

Screen element → file → key path → the string the screen renders. Every row
is re-resolved and re-formatted by `exhibit_verify.py` before the build is
allowed to pass.


#### guardRails — 2 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `guardRails.methodClaim.evidence[1]` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → calibrate_order_satisfied` | `False` |
| `guardRails.methodClaim.evidence[2]` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → calibrate_order_statement` | `The assignment orders 'Calibrate to a public NPR fuel-economy reference and state it'. WS11 obtained the reference and did NOT calibrate to it: no ruler parameter was moved to close the residual, because the anchor is an in-use aggregate over an unknown duty, load, body and driver mix and cannot resolve a cycle-specific level. This is recorded as a NON-SATISFACTION of the order, not as a treatment choice (adjudication r1/B3). The consequence for each verdict is priced in `ruler_fuel_flip_points`: V2's KILL is being put to the lead on an UNCALIBRATED ruler.` |

#### race — 102 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `headline.freightGiven` | `WS11_vehicle_zero_ruler/results_ws11.json` | `one_factor → rows → V2_on_VOLT-REG → mass_payload_denominator → cost_pp` | `16.19 pp` |
| `headline.perKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_km_paired → min` | `+8.41%` |
| `headline.perPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_payload_tkm_paired → min` | `-7.93%` |
| `pairs[0].massRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → mass_kg_ruler` | `6,600 kg` |
| `pairs[0].payloadCand` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → payload_kg_candidate` | `2,712 kg` |
| `pairs[0].payloadRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → payload_kg_ruler` | `2,900 kg` |
| `pairs[0].reconciliation.mechanisms[0].rows[0].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_g` | `19,130.2 g` |
| `pairs[0].reconciliation.mechanisms[0].rows[1].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_corrected_g` | `19,037.0 g` |
| `pairs[0].reconciliation.mechanisms[0].rows[2].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → soc_drift_kwh_cells` | `0.4491 kWh` |
| `pairs[0].record.candPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → candidate → per_km → per_seed → 11` | `1.4139 kWh/km` |
| `pairs[0].record.candPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → candidate → per_payload_tkm → per_seed → 11` | `0.5214 kWh/t-km` |
| `pairs[0].record.marginPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_km_paired → per_seed → 11` | `+25.49%` |
| `pairs[0].record.marginPerKmEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_km_paired → min` | `+25.29%` |
| `pairs[0].record.marginPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_payload_tkm_paired → per_seed → 11` | `+20.33%` |
| `pairs[0].record.marginPerPayloadEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_payload_tkm_paired → min` | `+20.11%` |
| `pairs[0].record.rulerPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → ruler → per_km → per_seed → 11` | `1.8977 kWh/km` |
| `pairs[0].record.rulerPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → ruler → per_payload_tkm → per_seed → 11` | `0.6544 kWh/t-km` |
| `pairs[1].massRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → mass_kg_ruler` | `6,600 kg` |
| `pairs[1].payloadCand` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → payload_kg_candidate` | `2,712 kg` |
| `pairs[1].payloadRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → payload_kg_ruler` | `2,900 kg` |
| `pairs[1].reconciliation.mechanisms[0].rows[0].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_g` | `19,130.2 g` |
| `pairs[1].reconciliation.mechanisms[0].rows[1].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_corrected_g` | `19,037.0 g` |
| `pairs[1].reconciliation.mechanisms[0].rows[2].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → soc_drift_kwh_cells` | `0.4491 kWh` |
| `pairs[1].record.candPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → candidate → per_km → per_seed → 11` | `1.4542 kWh/km` |
| `pairs[1].record.candPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → candidate → per_payload_tkm → per_seed → 11` | `0.5362 kWh/t-km` |
| `pairs[1].record.marginPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → margin_pct_per_km_paired → per_seed → 11` | `+24.55%` |
| `pairs[1].record.marginPerKmEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → margin_pct_per_km_paired → min` | `+24.37%` |
| `pairs[1].record.marginPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → margin_pct_per_payload_tkm_paired → per_seed → 11` | `+19.32%` |
| `pairs[1].record.marginPerPayloadEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → margin_pct_per_payload_tkm_paired → min` | `+19.12%` |
| `pairs[1].record.rulerPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → ruler → per_km → per_seed → 11` | `1.9274 kWh/km` |
| `pairs[1].record.rulerPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → cold_-10C → ruler → per_payload_tkm → per_seed → 11` | `0.6646 kWh/t-km` |
| `pairs[2].massRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → mass_kg_ruler` | `6,600 kg` |
| `pairs[2].payloadCand` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → payload_kg_candidate` | `2,461 kg` |
| `pairs[2].payloadRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → payload_kg_ruler` | `2,900 kg` |
| `pairs[2].reconciliation.mechanisms[0].rows[0].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_g` | `19,130.2 g` |
| `pairs[2].reconciliation.mechanisms[0].rows[1].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_corrected_g` | `19,037.0 g` |
| `pairs[2].reconciliation.mechanisms[0].rows[2].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → soc_drift_kwh_cells` | `0.4491 kWh` |
| `pairs[2].record.candPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → candidate → per_km → per_seed → 23` | `1.7010 kWh/km` |
| `pairs[2].record.candPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → candidate → per_payload_tkm → per_seed → 23` | `0.6912 kWh/t-km` |
| `pairs[2].record.marginPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_km_paired → per_seed → 23` | `+9.25%` |
| `pairs[2].record.marginPerKmEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_km_paired → min` | `+8.41%` |
| `pairs[2].record.marginPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_payload_tkm_paired → per_seed → 23` | `-6.93%` |
| `pairs[2].record.marginPerPayloadEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_payload_tkm_paired → min` | `-7.93%` |
| `pairs[2].record.rulerPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → ruler → per_km → per_seed → 23` | `1.8745 kWh/km` |
| `pairs[2].record.rulerPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → ruler → per_payload_tkm → per_seed → 23` | `0.6464 kWh/t-km` |
| `pairs[3].massRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → mass_kg_ruler` | `6,600 kg` |
| `pairs[3].payloadCand` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → payload_kg_candidate` | `2,461 kg` |
| `pairs[3].payloadRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → payload_kg_ruler` | `2,900 kg` |
| `pairs[3].reconciliation.mechanisms[0].rows[0].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_g` | `19,130.2 g` |
| `pairs[3].reconciliation.mechanisms[0].rows[1].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → fuel_corrected_g` | `19,037.0 g` |
| `pairs[3].reconciliation.mechanisms[0].rows[2].v` | `WS4_genset/results_ws4.json` | `gate_g1 → nominal → _raw_reference_seed → b → soc_drift_kwh_cells` | `0.4491 kWh` |
| `pairs[3].reconciliation.mechanisms[1].rows[0].v` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → capability_and_limit_worst_case → V2_on_VOLT-REG → ruler_worst_unserved_wheel_kWh` | `3.2582 kWh` |
| `pairs[3].reconciliation.mechanisms[1].rows[1].v` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → capability_and_limit_worst_case → V2_on_VOLT-REG → ruler_worst_capability_infeasible_s` | `555.6 s` |
| `pairs[3].record.candPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → candidate → per_km → per_seed → 23` | `1.9516 kWh/km` |
| `pairs[3].record.candPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → candidate → per_payload_tkm → per_seed → 23` | `0.7930 kWh/t-km` |
| `pairs[3].record.marginPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → margin_pct_per_km_paired → per_seed → 23` | `+7.27%` |
| `pairs[3].record.marginPerKmEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → margin_pct_per_km_paired → min` | `+6.67%` |
| `pairs[3].record.marginPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → margin_pct_per_payload_tkm_paired → per_seed → 23` | `-9.27%` |
| `pairs[3].record.marginPerPayloadEnsembleMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → margin_pct_per_payload_tkm_paired → min` | `-9.98%` |
| `pairs[3].record.rulerPerKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → ruler → per_km → per_seed → 23` | `2.1047 kWh/km` |
| `pairs[3].record.rulerPerPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → climb_10km_6pct → ruler → per_payload_tkm → per_seed → 23` | `0.7258 kWh/t-km` |
| `semi.controlDuty` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → duties → control` | `LH-520` |
| `semi.criterionCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → advance_kill → every_corner_pct` | `0.0%` |
| `semi.criterionNominal` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → advance_kill → nominal_pct` | `3.0%` |
| `semi.designDuty` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → duties → design` | `GH-REG-165` |
| `semi.gatingRule` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → duties → gating` | `ADVANCE/KILL is read on the DESIGN duty; the control duty is reported alongside and NEVER gates` |
| `semi.metric` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → advance_kill → metric` | `primary energy per payload tonne-km` |
| `semi.rows[0].controlMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → LH-520 → margin_vs_ruler_pct → min` | `+7.26%` |
| `semi.rows[0].designMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → GH-REG-165 → margin_vs_ruler_pct → min` | `+7.50%` |
| `semi.rows[0].payload` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → payload_kg` | `20,655 kg` |
| `semi.rows[0].title` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → title` | `Zero-mass stack - opposed-piston-class engine + predictive energy management, mechanical drive as S0` |
| `semi.rows[0].verdict` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → verdict` | `ADVANCE` |
| `semi.rows[0].worstCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → worst_case_margin_pct_design_duty → value` | `+7.29%` |
| `semi.rows[0].worstCornerCase` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S6 → worst_case_margin_pct_design_duty → governing_case` | `payload_minus20` |
| `semi.rows[1].controlMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → LH-520 → margin_vs_ruler_pct → min` | `-1.38%` |
| `semi.rows[1].designMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → GH-REG-165 → margin_vs_ruler_pct → min` | `+5.36%` |
| `semi.rows[1].payload` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → payload_kg` | `19,706 kg` |
| `semi.rows[1].title` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → title` | `Minimal transmission with the 13 L engine - the other end of the ratio law` |
| `semi.rows[1].verdict` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → verdict` | `ADVANCE` |
| `semi.rows[1].worstCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → worst_case_margin_pct_design_duty → value` | `+3.93%` |
| `semi.rows[1].worstCornerCase` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5-13L → worst_case_margin_pct_design_duty → governing_case` | `cold_minus10C` |
| `semi.rows[2].controlMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → LH-520 → margin_vs_ruler_pct → min` | `-1.45%` |
| `semi.rows[2].designMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → GH-REG-165 → margin_vs_ruler_pct → min` | `+4.51%` |
| `semi.rows[2].payload` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → payload_kg` | `19,846 kg` |
| `semi.rows[2].title` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → title` | `Marginal-mass electrification - one EXISTING trailer axle motorised, tractor untouched` |
| `semi.rows[2].verdict` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → verdict` | `ADVANCE` |
| `semi.rows[2].worstCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → worst_case_margin_pct_design_duty → value` | `+3.58%` |
| `semi.rows[2].worstCornerCase` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S7 → worst_case_margin_pct_design_duty → governing_case` | `cold_minus10C` |
| `semi.rows[3].controlMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → LH-520 → margin_vs_ruler_pct → min` | `-6.81%` |
| `semi.rows[3].designMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → GH-REG-165 → margin_vs_ruler_pct → min` | `+11.95%` |
| `semi.rows[3].payload` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → payload_kg` | `20,134 kg` |
| `semi.rows[3].title` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → title` | `Range-extended BEV re-posed - cited external energy cell (ESC-1c), electricity term (ESC-3)` |
| `semi.rows[3].verdict` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → verdict` | `ADVANCE` |
| `semi.rows[3].worstCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → worst_case_margin_pct_design_duty → value` | `+7.40%` |
| `semi.rows[3].worstCornerCase` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S4p → worst_case_margin_pct_design_duty → governing_case` | `cold_minus10C` |
| `semi.rows[4].controlMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → LH-520 → margin_vs_ruler_pct → min` | `-5.75%` |
| `semi.rows[4].designMin` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → GH-REG-165 → margin_vs_ruler_pct → min` | `+1.90%` |
| `semi.rows[4].payload` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → payload_kg` | `19,970 kg` |
| `semi.rows[4].title` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → title` | `Minimal transmission - 2-speed dog box, motor-synchronised shifts, torque-fill through the shift` |
| `semi.rows[4].verdict` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → verdict` | `KILL` |
| `semi.rows[4].worstCorner` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → worst_case_margin_pct_design_duty → value` | `+0.27%` |
| `semi.rows[4].worstCornerCase` | `WS9_vehicle_one_wave2/results_ws9.json` | `interface_ws9 → candidates → S5 → worst_case_margin_pct_design_duty → governing_case` | `cold_minus10C` |

#### rounds — 5 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `kx.corner` | `WS4_genset/results_ws4.json` | `series_duty_v2 → r6_rating_family_probe → cases → r6_rating_corner_full → condition` | `the full R6 rating corner: +20% payload, CdA 5.4, 4 kW aux, 2,000 m / +45 C` |
| `kx.designPoint` | `WS4_genset/results_ws4.json` | `heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point → r20_design_point_radiator_package_kW` | `95.018 kW` |
| `kx.designPointAmbient` | `WS4_genset/results_ws4.json` | `heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point → r20_design_point_air_temperature_C` | `45.0 C` |
| `kx.r6Reject` | `WS4_genset/results_ws4.json` | `series_duty_v2 → r6_rating_family_probe → cases → r6_rating_corner_full → per_seed → 3 → engine_reject_2min_max_kW` | `215.67010 kW` |
| `kx.radiatorShare` | `WS4_genset/results_ws4.json` | `heat_ledger_ws6 → series_duty_v2_nominal_cycle_average → radiator_package_share` | `0.48` |

#### sandbox — 31 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `airDensity.members[0].value` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → rho_air_cold` | `1.341 kg/m³` |
| `airDensity.members[1].value` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → rho_air` | `1.196 kg/m³` |
| `airDensity.members[2].value` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → rho_air_hot_alt` | `0.871 kg/m³` |
| `anchors.ceiling.record` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → ratio_ceiling_closed_form → value` | `3.769911:1` |
| `anchors.rows[0].record` | `WS1_loads_duty_cycles/results.json` | `baseline_crosscheck → cruise85_force_N` | `1987.5751 N` |
| `anchors.rows[1].record` | `WS1_loads_duty_cycles/results.json` | `sensitivity → climb_10km_6pc → per_speed → 60kmh → wheel_force_N` | `5159.4542 N` |
| `anchors.rows[2].record` | `WS9_vehicle_one_wave2/results_ws9.json` | `two_walls → two_speed_solve → ENG-13L → solve → force_required → total_N` | `23796.7812 N` |
| `endpoints.one.citations.CdA_m2` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → CdA` | `5.50 m²` |
| `endpoints.one.citations.Crr` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → Crr` | `0.0055` |
| `endpoints.one.citations.T_peak_Nm` | `WS8_semi_architecture/results_ws8.json` | `task2_s0_calibration → engine → peak_torque_Nm` | `2,373 Nm` |
| `endpoints.one.citations.m_kg` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → m_gcw` | `36,300 kg` |
| `endpoints.one.citations.r_dyn_m` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → r_dyn` | `0.500 m` |
| `endpoints.one.citations.rho_air` | `WS8_semi_architecture/results_ws8.json` | `params → vehicle → rho_air` | `1.196 kg/m³` |
| `endpoints.one.citations.rpm_ceiling` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → ratio_ceiling_closed_form → rpm_ceiling` | `2,100 rpm` |
| `endpoints.one.citations.v_climb_kmh` | `WS9_vehicle_one_wave2/results_ws9.json` | `two_walls → two_speed_solve → ENG-13L → solve → force_required → v_ref_kmh` | `45 km/h` |
| `endpoints.one.citations.v_cruise_kmh` | `WS8_semi_architecture/results_ws8.json` | `params → cycle → linehaul_v_hi_kmh` | `105.0 km/h` |
| `endpoints.zero.citations.CdA_m2` | `WS1_loads_duty_cycles/results.json` | `params → vehicle → CdA` | `4.20 m²` |
| `endpoints.zero.citations.Crr` | `WS1_loads_duty_cycles/results.json` | `params → vehicle → Crr` | `0.0090` |
| `endpoints.zero.citations.eta_driveline` | `WS1_loads_duty_cycles/results.json` | `params → driveline → eta_direct` | `0.950` |
| `endpoints.zero.citations.m_kg` | `WS1_loads_duty_cycles/results.json` | `params → vehicle → m_gvw` | `6,600 kg` |
| `endpoints.zero.citations.r_dyn_m` | `WS1_loads_duty_cycles/results.json` | `params → vehicle → r_dyn` | `0.370 m` |
| `endpoints.zero.citations.rho_air` | `WS1_loads_duty_cycles/results.json` | `params → vehicle → rho_air` | `1.200 kg/m³` |
| `endpoints.zero.citations.v_cruise_kmh` | `WS1_loads_duty_cycles/results.json` | `cycles → VOLT-REG → max_speed_kmh` | `100.0 km/h` |
| `model.ratioMax` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → ratio_ceiling_closed_form → rule` | `PHYSICS BOUND, solved in closed form: ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)` |
| `s3.anyFeasible` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → any_feasible` | `False` |
| `s3.forceAvailable` | `WS9_vehicle_one_wave2/results_ws9.json` | `two_walls → single_ratio_closed_form → ENG-11L → F_available_at_ceiling_kN` | `12.44 kN` |
| `s3.forceRequired` | `WS9_vehicle_one_wave2/results_ws9.json` | `two_walls → single_ratio_closed_form → ENG-11L → F_required_6pct_kN` | `23.80 kN` |
| `s3.maxWithoutOverspeed` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → max_ratio_without_overspeed` | `3.60:1` |
| `s3.overCeilingRpm` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → ratio_needed_to_hold_6pct → over_ceiling_by_rpm` | `1,732 rpm` |
| `s3.ratioNeeded` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → S3_fixed_ratio_feasibility → ratio_needed_to_hold_6pct → ratio` | `6.88:1` |
| `s3.spanNeeded` | `WS9_vehicle_one_wave2/results_ws9.json` | `two_walls → single_ratio_closed_form → ENG-11L → span_needed` | `1.91:1` |

#### sim — 10 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `controlConstants.architecture` | `WS5_controls/results_ws5.json` | `interface_ws5 → _architecture` | `pure series, both variants. No clutch, no mode selection, no synchronisation (BASELINE_v3).` |
| `controlConstants.chopperRateHz` | `WS5_controls/results_ws5.json` | `interface_ws5 → supervisor → chopper_command_rate_Hz` | `100 Hz` |
| `controlConstants.loopRateHz` | `WS5_controls/results_ws5.json` | `interface_ws5 → supervisor → loop_rate_Hz` | `10 Hz` |
| `controlConstants.pinnedBsfc` | `WS5_controls/results_ws5.json` | `interface_ws5 → dispatch_v2_r22b → pinned_point → bsfc` | `203.62 g/kWh` |
| `controlConstants.v1FixedPoint` | `WS5_controls/results_ws5.json` | `interface_ws5 → dispatch_v1_r19 → fixed_point_bus_kW` | `35.0 kW` |
| `controlConstants.v2Strategy` | `WS5_controls/results_ws5.json` | `interface_ws5 → dispatch_v2_r22b → recommended` | `load_follow` |
| `payloadNote.ledgerRuler` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → masses → payload_at_gvw_kg → ruler` | `2,900 kg` |
| `payloadNote.ledgerV1` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → masses → payload_at_gvw_kg → V1` | `2,712 kg` |
| `payloadNote.ledgerV2` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → masses → payload_at_gvw_kg → V2` | `2,461 kg` |
| `statusNote.quote` | `WS5_controls/results_ws5.json` | `_meta → adjudication` | `CUT by BASELINE_v7's research freeze. This packet is gated-but-unadjudicated; REPORT_WS5.md section 14 is WS5's own statement of what is weak in its own work, written because no adversarial reviewer will supply one.` |

#### verdict — 89 bound values

| screen element | file | key path | renders |
|---|---|---|---|
| `cards[0].archivalNotice` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → _archival_notice` | `ARCHIVED. Gate G1's kill clause was EXECUTED in BASELINE_v3 (ratified 2026-08-30): the clutch, the lockup device and actuator, clutch-sync control, R11's condition-aware mode policy, fault spec F-1 and the i-MMD topology reference are all deleted with it. Both variants are pure series. This block is retained as the record of the decision and its provenance. NO FIELD OF THIS BLOCK MAY BE CONSUMED AS A LIVE REQUIREMENT - consume interface_ws4 -> series_duty_v2 instead. Mode (a) does not exist in any live architecture. FROZEN MEMBER SET (KX r3, adjudication KX2-m3): results_ws4.json -> gate_g1 -> <case> -> _raw_reference_seed is projected through the explicit 53-member key list of record (run_ws4.py G1_RAW_KEYS_OF_RECORD), in the record's own key order, so the archive cannot grow when the simulator gains a field. KX r2 let 234 such members leak in - including mode-(a) over-rating counters that did not exist when the gate was run - with 0 values changed; they are withdrawn here. Every diagnostic added after 2026-08-30 belongs to the LIVE block.` |
| `cards[0].convention` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → convention` | `G1-R (R12): traction = WS2 measured map [data/effmap_motor_inverter_662V.csv, 662 V] x 0.97 reduction, no scalar PE member, no part_load_factor; PM spin drag charged to (a) locked samples at 1.1532 kW shaft + 0.3896 kW bus (WS2 export)` |
| `cards[0].criterion` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → kill_criterion_pct` | `5.0%` |
| `cards[0].executedBy` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → executed_by` | `BASELINE_v3.md, GATE G1: EXECUTED. THE CLUTCH IS DELETED.` |
| `cards[0].gateStatus` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → status` | `executed_kill_2026-08-30` |
| `cards[0].governingCase` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → margin_pct_ensemble_min_governing_case` | `seed 4 of 8-seed VOLT-REG ensemble [nominal]` |
| `cards[0].missedBy` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → missed_by_pp` | `7.58 pp` |
| `cards[0].passes` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → passes` | `False` |
| `cards[0].seedsPositive` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → seeds_margin_positive_n` | `0` |
| `cards[0].seedsTotal` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → seeds_total` | `8` |
| `cards[0].waterfall[0].value` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → attribution_rows → prior_convention → min` | `+6.26%` |
| `cards[0].waterfall[1].value` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → attribution_rows → map_vs_scalar_alone → delta_pp_min` | `-7.01 pp` |
| `cards[0].waterfall[2].value` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → attribution_rows → spin_drag_alone → delta_pp_min` | `-1.77 pp` |
| `cards[0].waterfall[4].value` | `WS4_genset/results_ws4.json` | `interface_ws4 → gate_g1 → verdict → margin_pct_ensemble_min` | `-2.58%` |
| `cards[1].criterionCorner` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → advance_kill → every_corner_pct` | `0.0%` |
| `cards[1].criterionNominal` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → advance_kill → nominal_pct` | `3.0%` |
| `cards[1].gcw` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → gcw_kg` | `36,300 kg` |
| `cards[1].metric` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → metric_of_record` | `fleet-mission fuel energy per PAYLOAD tonne-km [MJ/(t.km)], fleet mission = 70% LH-520 + 30% REG-165 by distance` |
| `cards[1].numbersVersion` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → numbers_version` | `r3` |
| `cards[1].rows[0].bindingReason` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → binding_reason` | `fails the nominal >=3% criterion` |
| `cards[1].rows[0].perKmMedian` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S1 → ensemble → median` | `+7.36%` |
| `cards[1].rows[0].perKmMin` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S1 → ensemble → min` | `+6.03%` |
| `cards[1].rows[0].perPayloadMedian` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → nominal_margin_pct_median` | `+0.73%` |
| `cards[1].rows[0].perPayloadMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → nominal_margin_pct_min` | `-0.69%` |
| `cards[1].rows[0].verdict` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → verdict` | `KILL` |
| `cards[1].rows[0].worstCorner` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → worst_corner` | `cold_minus10C` |
| `cards[1].rows[0].worstCornerMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S1 → worst_corner_margin_pct_min` | `-12.87%` |
| `cards[1].rows[1].bindingReason` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → binding_reason` | `fails the nominal >=3% criterion` |
| `cards[1].rows[1].perKmMedian` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S2 → ensemble → median` | `+9.81%` |
| `cards[1].rows[1].perKmMin` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S2 → ensemble → min` | `+8.62%` |
| `cards[1].rows[1].perPayloadMedian` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → nominal_margin_pct_median` | `+1.89%` |
| `cards[1].rows[1].perPayloadMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → nominal_margin_pct_min` | `+0.59%` |
| `cards[1].rows[1].verdict` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → verdict` | `KILL` |
| `cards[1].rows[1].worstCorner` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → worst_corner` | `cold_minus10C` |
| `cards[1].rows[1].worstCornerMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S2 → worst_corner_margin_pct_min` | `-9.23%` |
| `cards[1].rows[2].bindingReason` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → binding_reason` | `fails the nominal >=3% criterion` |
| `cards[1].rows[2].perKmMedian` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S3 → ensemble → median` | `+7.44%` |
| `cards[1].rows[2].perKmMin` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S3 → ensemble → min` | `+4.88%` |
| `cards[1].rows[2].perPayloadMedian` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → nominal_margin_pct_median` | `+1.64%` |
| `cards[1].rows[2].perPayloadMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → nominal_margin_pct_min` | `-1.09%` |
| `cards[1].rows[2].verdict` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → verdict` | `KILL` |
| `cards[1].rows[2].worstCorner` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → worst_corner` | `cold_minus10C` |
| `cards[1].rows[2].worstCornerMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S3 → worst_corner_margin_pct_min` | `-14.17%` |
| `cards[1].rows[3].bindingReason` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → binding_reason` | `fails the nominal >=3% criterion` |
| `cards[1].rows[3].perKmMedian` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S4 → ensemble → median` | `+5.95%` |
| `cards[1].rows[3].perKmMin` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → per_km_margin_paired → corners → nominal → S4 → ensemble → min` | `+3.36%` |
| `cards[1].rows[3].perPayloadMedian` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → nominal_margin_pct_median` | `-1.06%` |
| `cards[1].rows[3].perPayloadMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → nominal_margin_pct_min` | `-3.84%` |
| `cards[1].rows[3].verdict` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → verdict` | `KILL` |
| `cards[1].rows[3].worstCorner` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → worst_corner` | `cold_minus10C` |
| `cards[1].rows[3].worstCornerMin` | `WS8_semi_architecture/results_ws8.json` | `advance_kill → candidates → S4 → worst_corner_margin_pct_min` | `-17.21%` |
| `cards[1].whr.rows[0].best` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → best_net_margin_pct → S1` | `+1.75%` |
| `cards[1].whr.rows[0].result` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → result → S1` | `DROPPED` |
| `cards[1].whr.rows[1].best` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → best_net_margin_pct → S2` | `+1.83%` |
| `cards[1].whr.rows[1].result` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → result → S2` | `DROPPED` |
| `cards[1].whr.rows[2].best` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → best_net_margin_pct → S3` | `+2.38%` |
| `cards[1].whr.rows[2].result` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → result → S3` | `DROPPED` |
| `cards[1].whr.threshold` | `WS8_semi_architecture/results_ws8.json` | `interface_ws8 → whr_gate → threshold_pct` | `2.5%` |
| `cards[2].rows[0].perKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-SUB → nominal → margin_pct_per_km_paired → min` | `+33.56%` |
| `cards[2].rows[0].perPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-SUB → nominal → margin_pct_per_payload_tkm_paired → min` | `+21.71%` |
| `cards[2].rows[1].perKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_km_paired → min` | `+8.41%` |
| `cards[2].rows[1].perPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V2_on_VOLT-REG → nominal → margin_pct_per_payload_tkm_paired → min` | `-7.93%` |
| `cards[2].rows[2].perKm` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_km_paired → min` | `+25.29%` |
| `cards[2].rows[2].perPayload` | `WS11_vehicle_zero_ruler/results_ws11.json` | `results → V1_on_VOLT-SUB → nominal → margin_pct_per_payload_tkm_paired → min` | `+20.11%` |
| `cards[3].criterionCorner` | `WS11_vehicle_zero_ruler/results_ws11.json` | `advance_kill → criterion → corner_threshold_pct` | `0.0%` |
| `cards[3].criterionNominal` | `WS11_vehicle_zero_ruler/results_ws11.json` | `advance_kill → criterion → nominal_threshold_pct` | `3.0%` |
| `cards[3].criterionText` | `WS11_vehicle_zero_ruler/results_ws11.json` | `advance_kill → criterion → statement` | `ADVANCE only if >= 3% better than the ruler on the candidate's design duty at nominal, ensemble-min, AND >= 0% at every corner. Metric: fuel energy per payload tonne-km, paired per-seed.` |
| `cards[3].esc1.anchorLper100` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → fourhk1_era → l_per_100km` | `32.01 L/100 km` |
| `cards[3].esc1.anchorName` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → name` | `Fuelly - Isuzu NPR-HD, all model years (owner fuel logs)` |
| `cards[3].esc1.calibrateOrderSatisfied` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → calibrate_order_satisfied` | `False` |
| `cards[3].esc1.modelLper100` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → l_per_100km_VOLT_SUB → median` | `19.18 L/100 km` |
| `cards[3].esc1.worstResidual` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → worst_residual_vs_model_pct` | `-40.10%` |
| `cards[3].esc1.worstResidualGoverning` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler → anchor → worst_residual_governing_case` | `fourhk1_era (min over the enumerated two-member anchor set)` |
| `cards[3].rows[0].flipDirection` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler_fuel_flip_points → V1_on_VOLT-SUB → direction_that_would_overturn_the_verdict` | `LEANER` |
| `cards[3].rows[0].flipPoint` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler_fuel_flip_points → V1_on_VOLT-SUB → pct_ruler_fuel_error_to_draw` | `-20.11%` |
| `cards[3].rows[0].nominalGoverning` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V1_on_VOLT-SUB → nominal_margin_pct_min_governing_case` | `seed 4 of the enumerated 8-seed VOLT-SUB ensemble` |
| `cards[3].rows[0].nominalMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V1_on_VOLT-SUB → nominal_margin_pct_min` | `+20.11%` |
| `cards[3].rows[0].pessimistic` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdict_robustness → rows → V1_on_VOLT-SUB → pessimistic_min` | `+37.78%` |
| `cards[3].rows[0].verdict` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V1_on_VOLT-SUB → verdict` | `ADVANCE` |
| `cards[3].rows[0].worstCorner` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V1_on_VOLT-SUB → worst_corner_margin_pct` | `+19.12%` |
| `cards[3].rows[0].worstCornerGoverning` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V1_on_VOLT-SUB → worst_corner_governing_case` | `cold_-10C (min over the enumerated corner set ['alt2000m_45C', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 4 of the enumerated 8-seed VOLT-SUB ensemble` |
| `cards[3].rows[1].flipDirection` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler_fuel_flip_points → V2_on_VOLT-REG → direction_that_would_overturn_the_verdict` | `THIRSTIER` |
| `cards[3].rows[1].flipPoint` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → ruler_fuel_flip_points → V2_on_VOLT-REG → pct_ruler_fuel_error_to_draw` | `+6.93%` |
| `cards[3].rows[1].nominalGoverning` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V2_on_VOLT-REG → nominal_margin_pct_min_governing_case` | `seed 5 of the enumerated 8-seed VOLT-REG ensemble` |
| `cards[3].rows[1].nominalMin` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V2_on_VOLT-REG → nominal_margin_pct_min` | `-7.93%` |
| `cards[3].rows[1].pessimistic` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdict_robustness → rows → V2_on_VOLT-REG → pessimistic_min` | `+0.13%` |
| `cards[3].rows[1].verdict` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V2_on_VOLT-REG → verdict` | `KILL` |
| `cards[3].rows[1].worstCorner` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V2_on_VOLT-REG → worst_corner_margin_pct` | `-9.98%` |
| `cards[3].rows[1].worstCornerGoverning` | `WS11_vehicle_zero_ruler/results_ws11.json` | `interface_ws11 → verdicts → V2_on_VOLT-REG → worst_corner_governing_case` | `climb_10km_6pct (min over the enumerated corner set ['alt2000m_45C', 'climb_10km_6pct', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 5 of the enumerated 8-seed VOLT-REG+CLIMB ensemble` |
