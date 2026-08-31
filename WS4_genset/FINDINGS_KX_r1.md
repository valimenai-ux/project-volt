# FINDINGS — WS4 (genset) — KX round, review round 1 (`FINDINGS_KX_r1.md`)

Adjudicator: fresh context, disk only, independent re-derivation. Judged
against **BASELINE_v5.md** (authoritative; R34, and the R14/R9/rule-7
conventions carried from v2/v3), **BASELINE_v3.md** (R22, R23 — the
executed kill), and `WS4_genset/KX_DIRECTIVE.md`. Artifacts: `REPORT_WS4.md`,
`results_ws4.json`, `run_ws4.py` / `ws4_sim.py` / `ws4_chain.py` /
`ws4_models.py` / `make_report_ws4.py` / `verify_ws4.py`, `data/*.csv`,
`figs/*.png`, `run_output.txt`, plus the read-only WS1/WS2/WS3 imports, on
disk as of 2026-08-31. Prior rounds `FINDINGS_WS4_r1/r2/r3.md` read in full.

Scope honoured as fixed by the lead: the R23 errata pins (F1–F5), the
`series_duty_v2` block, and interface consistency. **The G1 gate decision is
not reopened** — it is an executed kill (BASELINE_v3 R22/R23) and `gate_g1`
is treated only as an archived record block. Per the directive, F1–F5 were
checked for closure-at-root-cause rather than re-adjudicated.

---

## Verdict

**NOT CLEAN. Two BLOCKING findings, three MATERIAL, eight MINOR.**

Every ordered headline number in `series_duty_v2` re-derives exactly — I
reproduced all three cases × 8 seeds from the source models, and reproduced
the nominal reference seed a second way straight off the R34 trace. The
errata F1, F3, F4 and F5 are closed at root cause and machine-pinned. The
zero-unserved result is real and is *more* robust than claimed (see V7).

The two blocking findings are both interface-correctness defects on the
block labelled `_status: live_design_input`, in the class the program's own
history names: a machine-readable field that asserts a constraint is
inactive when it is violated (B1), and an export set that omits the
measurements the escalation it raises depends on (B2). Neither moves an
ordered number; both would mislead WS5 and the lead.

---

## Verification record — what I re-derived independently

- **V1 — full re-run of the ordered case set.** Rebuilt the run from
  `ws4_models` / `ws4_sim` / `ws4_chain` + WS1's `volt_cycles` outside
  `run_ws4.py`, all 3 cases × 8 seeds, mode (b). Reproduced **every**
  envelope printed in §4-KX.2 exactly: kWh/km 1.701–1.728 / 2.019–2.038 /
  1.413–1.426; SOC minima 0.228 / 0.183 / 0.246; genset starts 5–6 / 4 / 6;
  emergency-band 405 / 645 / 222 s max; pack discharge peaks 184.5 / 142.2 /
  **192.5** kW; unserved 0.0000 everywhere.
- **V2 — the R34 trace as an independent witness.** Recomputed the nominal
  seed-23 scalars from `data/trace_series_duty_v2_nominal_seed23_10Hz.csv`
  alone (66,143 rows, 0.1 s step confirmed), with no simulator in the loop:
  distance 131.958668 km ✓, fuel 18.8800 kg ✓, fuel energy 224.4628 kWh ✓,
  **1.701008 kWh/km ✓**, SOC 0.257187–0.754873 ✓, pack charge/discharge peaks
  147.5056 / 120.2723 kW ✓, above-pin demand 1,214.7 s and 8.1022 kWh ✓,
  starts 5 ✓, charge-over-110 kW 68.5 s ✓, SOC drift −0.2848 kWh ✓. The trace
  is genuine and correct.
- **V3 — first-principles energy closure on that trace.** `gen − load` equals
  `chg − dis` to the printed precision (1.6505 kWh both ways); the SOC delta
  from bus flows at 0.97/0.97 reproduces the SOC channel (−0.2848 vs −0.2847
  kWh); **shaft + engine rejection = raw fuel energy exactly** (223.0027 kWh);
  cycle generator efficiency 0.951761 = the pinned `eta_gen`; implied BSFC
  203.6 g/kWh = the pinned BSFC; motoring wheel energy 78.8549 kWh = the F5
  block's `wheel_kWh` 78.85485. The books balance.
- **V4 — ensembles and R14 labels, recomputed from per-seed.** For all three
  cases I recomputed min/median/max for every one of the 120 exported
  ensemble fields from `per_seed` and re-derived every governing seed by
  argmin/argmax: **0 mismatches**.
- **V5 — three-way interface check.** The §11 JSON block extracted from
  `REPORT_WS4.md` is **byte-identical** to `json.dumps(results_ws4.json →
  interface_ws4, indent=1)`. `interface_ws4 → series_duty_v2 → cases[*].
  ensemble` is a strict, value-identical subset of `results_ws4.json →
  series_duty_v2 → cases[*].ensemble` (120 of 200 fields, 0 differing).
  `verify_ws4.py` exit 0 (184 headline renderings + interface block + 413
  structural/errata pins).
- **V6 — the brackets and the companion, re-run.** R8 envelope bracket
  (125/110 kW enforced) reproduces exactly: unserved 0.0000–0.0021 /
  0.0000–0.0149 / **0.5194–0.6129** kWh; clip 0.0–2.8 / 0.2–8.9 / 82.2–94.2 s;
  charge shed 0.376–0.472 / 0.492–0.672 / 0.202–0.347 kWh; fuel 18.98–19.16 /
  22.51–22.75 / 15.75–15.89 kg. Companion (b′) reproduces exactly:
  1.706–1.722 / 2.018–2.038 / 1.438–1.451 kWh/km, starts 1/1/2, unserved 0.
- **V7 — the zero-unserved claim, stress-tested beyond the ordered set.**
  I ran three cases the directive did not order, to hunt a governing case
  outside the reference set: the **compound corner** (CdA 5.4 × 2,000 m /
  +45 °C), the **full R6 rating corner** (+20 % payload, CdA 5.4, 4 kW aux,
  2,000 m / +45 °C) and aux 4 kW at nominal. All complete with **0.0000 kWh
  unserved on all 8 seeds** (worst SOC minimum 0.167 of usable, at the R6
  rating corner). Separately, capping the engine at its 132 kW continuous
  flat-rating in the emergency band also leaves unserved at **0.0000 kWh** on
  every seed of every ordered case (SOC minimum falls 0.183 → 0.127 at
  CdA 5.4). **The headline is not fragile and is not bought by the
  over-rating in M1.** Recorded for the lead as a positive result.
- **V8 — errata F1, F3, F5 re-derived.** F1: `gate_g1/cda_5.4/per_seed`
  margins are positive on seeds 4 (+0.087), 7 (+0.103), 8 (+0.119), 9
  (+0.048) — **four of eight**, matching the exported
  `seeds_margin_positive_n = 4` / `[4,7,8,9]` and mirrored correctly into
  `interface_ws4 → gate_g1 → verdict`. Corrected phrase occurs exactly 4×
  in the flattened report; all three superseded wordings occur 0×. F3:
  0.5148607848 pp (432–749 V) and 0.6324177501 pp (incl. r3-interim)
  recomputed from the member lists ✓. F5: 78.85485/86.08404 = 0.9160218 ✓;
  both fuel-to-wheel rates ✓. F4: every `*_file` field in `interface_ws4`
  resolves from the WS4 folder, structurally pinned in `verify_ws4.py`.
- **V9 — archived-gate spot checks (not re-adjudicated).** Nominal per-seed
  margins recomputed from the stored fuels as (b−a)/b·100 reproduce all eight
  stored values and the min/median/max −2.5816/−2.5037/−2.3727 exactly; every
  `condition_dependence` entry equals its source case ensemble to full float
  precision.
- **V10 — the D5 reconciliation the round left open.** Solved; see m2.

---

# BLOCKING

## KX-B1 — BLOCKING — R16's charge-acceptance curve is applied to the regen leg only, not to the pack; the interface therefore exports `bound_any_sample: false` while the pack is charged above its own acceptance curve for up to 59 s/cycle

**What is wrong.** `ws4_sim.run_g1_mode` applies `chg_accept_bus_kw` inside
the `elif pw < 0.0:` regen branch, as a cap on `p_rg_bus` only. The genset's
`p_gen_elec` is added afterwards, at `p_batt_bus = p_gen_elec - p_bus_load`,
and is never tested against the curve. The pack therefore takes
regen + genset simultaneously, unchecked.

WS3's file is `regen_acceptance.csv`, header line 1: *"pack regen-acceptance
vs cell temperature"*, column `V2pack_chg_cont_kW_bus` — a **pack** charge
limit, bus-side. A pack cannot tell where its charge current comes from.

**Evidence (measured, 8 seeds × 3 cases, from the shipped models):**

| | nominal | cda_5.4 | alt2000m_45C |
|---|---|---|---|
| R16 continuous acceptance at the declared cells | 130.752 kW | 130.752 kW | 129.144 kW |
| **pack charge above that acceptance** | **39.1–47.0 s/cycle** | **41.4–58.6 s/cycle** | **13.6–23.8 s/cycle** |
| longest single excursion | 15.4 s | 15.0 s | 11.6 s |
| excess energy (worst seed) | 0.181 kWh | 0.238 kWh | 0.098 kWh |
| pack charge peak | 147.6 kW | 147.6 kW | 147.5 kW |

Every excursion is **longer than the 10-s pulse window**, so WS3's pulse
column (204.173 / 200.553 kW) does not cover them. WS4 never consulted that
column. The mechanism is exactly the one WS4 identifies correctly on the R8
axis (§4-KX.3: *"the charge peak because regen and the genset can charge the
pack at the same time"*) — the workstream saw the event and missed it on the
R16 axis.

**Why it is blocking.** `interface_ws4 → series_duty_v2 →
r16_binding_analysis` exports `bound_any_sample: false`,
`peak_regen_to_pack_kW_bus: 69.1038`, and per-seed
`regen_shed_by_r16_kWh: 0.0` — the machine-readable statement that WS3's
charge-acceptance constraint is inactive on this duty. Against the pack's
actual charge power it is active on every case. The genset is on for
0.582–0.685 of cycle time, so regen-while-charging is **structural** to the
dispatch of record, not incidental. WS5 reading this block for R22b is told a
binding constraint does not exist.

It also mis-scopes an open escalation. **ESC-8** is built entirely on peak
*regen* (69.1 kW) vs 62.2 kW at 55 °C cells. On the pack quantity the hot end
is far worse: at 45 °C cells the run already charges at 147.5 kW against
129.1 kW continuous; at 50 °C the curve falls to 95.0 kW; at 55 °C the
**10-s pulse** rating is 128.8 kW, still below the run's peak. ESC-8 as
written understates its own case by roughly a factor of two, and the lead is
about to rule on it.

**The counter-reading, stated fairly.** WS3's REPORT_WS3 §4.2 says *"regen
follows the acceptance curve at all temperatures with the resistor as
overflow"* and *"WS5 should drive the blend from it directly"* — i.e. WS3
does present the curve to WS5 as a regen-blend rule. Under that reading WS4
did what it was told. The two readings differ measurably and WS4 chose the
permissive one **without recording that a choice existed**. The physical
quantity the curve names is the pack's; the conservative reading is the pack
one.

**Resolution.** Either (i) apply the curve to `p_batt_bus` when charging,
re-run, and export the shed energy and exceedance seconds per case with R14
labels; or (ii) keep the regen-leg application, but rename the field
(`regen_leg_bound_any_sample`), export `pack_charge_above_r16_accept_s` and
`_kWh` per case alongside it, state the two readings in `r16_binding_analysis
→ note`, and restate ESC-8 on the pack quantity with the 50 °C and 55 °C
continuous *and* pulse values. Either way, `bound_any_sample: false` must not
stand unqualified in a live design-input block.

---

## KX-B2 — BLOCKING — the (b′) companion, built "so R22b has both endpoints", exports only fuel and starts; measured, (b′) satisfies every capability envelope that (b) violates — and ESC-9 asks the lead to rule without that measurement

**What is wrong.** §4-KX.6 and `cases[*].companion_bp` compare the pinned
mode (b) and the load-following mode (b′) on **fuel kWh/km, genset starts and
unserved energy only**. The two dispatches differ qualitatively on three
capability axes, none of which is exported for (b′) and two of which are the
entire substance of ESC-9.

**Evidence (my re-run, 8 seeds × 3 cases):**

| axis | mode (b) — the block of record | mode (b′) — the companion |
|---|---|---|
| pack discharge peak, bus | 184.5 / 142.2 / **192.5** kW (vs R8 125) | **92.1 / 96.9 / 115.6 kW — inside R8** |
| pack charge peak, bus | 147.6 / 147.6 / 147.5 kW (vs R8 110) | **100.2 / 99.3 / 91.6 kW — inside R8** |
| pack charge above R16 acceptance | 39–47 / 41–59 / 14–24 s/cycle | **0.0 s on every seed of every case** |
| engine above its 132 kW continuous rating | 0–146.5 / 161.8–250.0 / 55.0–66.1 s | **0.0 s; peak shaft 131.1 / 131.1 / 121.9 kW** |
| genset starts per cycle | 5–6 / 4 / 6 | 1 / 1 / 2 |
| fuel kWh/km (WS4's own table) | 1.701–1.728 / 2.019–2.038 / 1.413–1.426 | 1.706–1.722 / 2.018–2.038 / 1.438–1.451 |

At nominal and CdA 5.4 the fuel difference is inside the ensemble spread —
WS4's own §4-KX.6 says so ("within a fraction of a percent"). The corner
costs (b′) ~1.8 %.

**Why it is blocking.** ESC-9 puts a three-way choice to the lead:
*"rule whether R8's bus-side peaks are a hard envelope (in which case WS5's
dispatch must keep the pack off the peak, or WS3 must restate the interface
rating), or whether short excursions of this duration are accepted"*. WS4
already ran a dispatch that keeps the pack off the peak on every seed of
every ordered case, and did not report that it does. §4-KX.3 names the
remedy in the abstract ("run the genset earlier so the pack never has to
cover the peak alone") without saying that its own companion demonstrates
it, at essentially no nominal fuel cost. An escalation that withholds the
measurement that answers it is not a neutral escalation, and R22b — the
question this block exists to feed — turns on exactly these rows.

This is **not** a request that WS4 choose the dispatch. WS4 is right not to.
It is a request that the companion carry the axes on which the choice is
made.

**Resolution.** Extend `companion_bp` (per seed and ensemble, R14-labelled)
with the same capability exports mode (b) already carries — `pack_dis_peak_kW`,
`pack_chg_peak_kW`, `pack_*_over_r8_*_s`, the R16 exceedance from B1, and the
new engine-over-rating counter from M1 — restate the §4-KX.6 table with those
rows, and add one sentence to ESC-9 recording, without recommending, that the
load-following endpoint satisfies R8 and R16 on every ordered seed at the
fuel deltas already printed.

---

# MATERIAL

## KX-M1 — MATERIAL — the genset runs above its own 132 kW continuous flat-rating for up to 250 s/cycle; no counter is exported, no prose says so, and §4-KX.3's enumeration of exceedances omits the component this workstream owns

**What is wrong.** In the emergency band (`ws4_sim.run_g1_mode`, mode "a"/"b"
branch) the engine is capped at `p_peak_kw * derate * 0.97`, where
`p_peak_kw = ENG_V2.peak_power_kw() = 153.300 kW` — the **automotive** peak of
the 4HK1-TC hardware, which §2.1 itself identifies as automotive and *not* the
continuous rating. Measured over the ordered run:

| | nominal | cda_5.4 | alt2000m_45C |
|---|---|---|---|
| continuous flat-rating (× derate) | 132.0 kW | 132.0 kW | 122.9 kW |
| **seconds above it** | **0.0–146.5** | **161.8–250.0** | **55.0–66.1** |
| longest continuous excursion | 139.9 s | 188.5 s | 64.1 s |
| peak engine shaft | 147.9 kW (112 % of continuous, 96 % of the automotive peak) | 147.9 kW | 133.6 kW (109 %) |
| energy delivered above the rating | 0.62 kWh | 1.00 kWh | 0.19 kWh |

Nothing in `results_ws4.json` or `interface_ws4` counts this.
`above_pin_engine_s` counts time above the **pin** (84.7 kW), not above the
**rating**; at nominal, more than half of that time (146.5 of 274.3 s) is also
above the rating, and no exported field distinguishes them. §4-KX.3, headed
*"What the run does NOT establish"*, enumerates the R3 motor rating and the R8
pack envelope and reads as a complete list. ESC-9's closing sentence —
*"the archived gate's mode (a) never posed this question, because the engine
carried the peaks mechanically"* — is incomplete: in mode (b) the engine also
carries peaks, above its rating.

**Why it matters.** The 132 kW continuous flat-rating is a **blocking** R18
datasheet figure and a WS6 release blocker, specified as *"an unlimited-hours
prime/COP-class rating"* with **+0.82 kW** of margin at the R6 corner (ESC-1,
PROVISIONAL). 112 % for ~3 minutes also exceeds the 10 %/1 h overload an
ISO 8528-1 prime rating allows. The generator is exposed on the same samples
(up to 241.8 s above GEN-V2's 135 kW continuous shaft input, peak 147.9 kW
against its 155 kW peak). And the same excursion drives the heat finding in
m7. The workstream that owns the engine exported over-rating counters for
two components it does not own and none for the one it does.

**What this finding is NOT.** It does **not** undermine the zero-unserved
headline: I re-ran all three cases with the engine capped at 132 kW
continuous in the emergency band and unserved stayed **0.0000 kWh on every
seed** (V7). The defect is an unexported capability exposure and a
mis-scoped "what this does not establish", not a wrong headline.

**Resolution.** Add `engine_over_continuous_rating_s` and `_kWh` per seed with
8-seed R14 envelopes for both (b) and (b′); state in §4-KX.1 that the
emergency band's ceiling is the automotive full-load curve, not the genset
rating; add the row to §4-KX.3 alongside the motor and pack rows; and either
fold it into ESC-9 or raise it as its own escalation against R18/ESC-1.

## KX-M2 — MATERIAL — the live block cannot resolve its own chain of record: the traction-map path and reduction factor exist only inside the archived `gate_g1` block, whose notice forbids consumption

**What is wrong.** `interface_ws4 → gate_g1 → traction_chain_of_record`
carries `map_file: "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv"`,
`reduction_flat: 0.97`, `map_voltage_V`, `ws2_rework_round` — the F4 erratum's
fix, correctly WS4-relative. That block's own `_archival_notice` reads:
**"NO FIELD OF THIS BLOCK MAY BE CONSUMED AS A LIVE REQUIREMENT — consume
interface_ws4 → series_duty_v2 instead."**

`interface_ws4 → series_duty_v2` carries no resolvable map path and no
reduction factor. Its `_inputs.traction_chain` is prose ("R12: WS2 r4 measured
inverter+motor map x 0.97 reduction, both directions, no scalar PE member");
its `input_sha256` has the key `"WS2/data/effmap_motor_inverter_662V.csv"`,
which is a hash-table label, not a path, and resolves from neither folder. A
consumer that obeys the archival notice cannot resolve the chain the live
numbers were produced with.

The same applies to the boundary-convention caveat: `boundary_convention_exposure`
lives only inside the archived block, yet the convention it describes is
active in the live `series_duty_v2` run (same map, same chain, same
`_interp_loss` clamping). `series_duty_v2` exports no boundary-exposure field
at all.

`verify_ws4.py`'s new structural pin resolves every `*_file` field that
exists; it cannot catch a field that is absent from the block that needs it.
This is the F4 defect class, reintroduced by the archival restructure the
same round fixed it in.

**Resolution.** Duplicate `traction_chain_of_record` (or a
`chain_of_record` member: map path, voltage, reduction, WS2 round, SHA) into
`interface_ws4 → series_duty_v2 → _inputs`, and attach the boundary-exposure
figures for the three ordered cases there too. Extend the verifier to assert
that the live block resolves without reading `gate_g1`.

## KX-M3 — MATERIAL — the exported payload-denominated metric uses the *pre-conversion* payload and carries no denominator, basis or caveat into the interface, so it is the per-km number rescaled by a constant

**What is wrong.** `interface_ws4 → series_duty_v2 → cases[*].ensemble`
exports `fuel_energy_kWh_per_payload_tonne_km_{min,max,median}` with full
R14 governing-case labels — and **no** `payload_t` field, no basis string, no
caveat, anywhere in `interface_ws4`. Grep confirms: the only payload
provenance in the whole artifact set is report prose in §12 ESC-7.

The denominator is `VEH.m_payload_at_gvw = 2,900 kg`, and it is identical in
all three cases (all run at GVW). The exported values are therefore the
per-km values divided by 2.9 exactly — 1.7010084250276258 / 2.9 =
0.586554629319871, the exported minimum, to the last digit. The field carries
zero information the per-km field does not.

Worse, the 2,900 kg is WS1's payload for the **conventional** truck:
`volt_params.py` defines `m_curb_operating = 3700.0` as *"NPR-HD chassis-cab
+ 16 ft dry-freight body + driver + full fuel/DEF"*. The series conversion's
mass (WS3 pack 280.5 kg, genset ~500 kg + 90 kg generator, WS2 spine rollup
230.8 kg, less the deleted engine/gearbox) is not charged against it. R32 and
D13/R36 exist precisely because *"every electrified candidate won 6–10 % per
km and gave 6–8 % back in freight"* — a payload denominator that does not
charge the powertrain's mass cannot discharge that ruling, and R36 is on the
record because a denominator artifact reached doctrine once already.

ESC-7's prose is careful and correct ("a companion, not a ruler"; "WS4 has no
ratified Vehicle Zero payload basis and does not invent one"). **The prose
does not travel with the JSON.**

**Resolution.** Add `payload_basis_t`, `payload_basis_source` and an explicit
`_caveat` ("pre-conversion WS1 curb; does not charge the series powertrain's
mass; not the R32 metric") next to the exported field, or withdraw the field
from `interface_ws4` until a Vehicle Zero payload basis is ratified. Restate
ESC-7 to say which curb the 2.9 t belongs to.

---

# MINOR

## m1 — §4.1's F2 restatement contains a hard-coded prose claim its own rendered number refutes

`make_report_ws4.py:941-942` emits, at nominal: *"the exposed samples top out
at @BEXNV@ km/h, i.e. they are launch samples."* `BEXNV` is
`chain_boundary_exposure.nominal.envelope.exposed_speed_kmh_max_max` = **98.4**.
Samples at 98.4 km/h are not launch samples; the same sentence has just
reported 0.0–6.0 s of *locked* exposure at nominal, and the r3 finding this
erratum closes specifically recorded nominal seeds with ~4 s of exposure at
93–98 km/h. This is a hand-written prose claim about a current number in the
report generator — the exact construction F1 was raised about. **Resolution:**
render the claim from the data (e.g. the fraction of exposure below the regen
blend floor), or delete the "i.e." clause.

## m2 — D5 is reconcilable in ten lines, and the reconciliation shows WS4's headline exposure figure is ~80 % an artifact of one degenerate map column

D5 states that WS4's F2 counter (22.7–31.3 s stencil / 18.9–24.5 s strict at
nominal) exceeds the r3 adjudicator's 3.6–7.6 s, that "the two criteria are
not the same test", and that reconciling "is not this round's scope". I
reconciled it exactly:

- Evaluating the feasible-torque envelope by **linear interpolation between
  bracketing rpm columns** gives **3.6–7.6 s at nominal** and **7.4–20.6 s at
  CdA 5.4** — the r3 adjudicator's two published figures, to the digit.
- `ws4_chain.boundary_exposure_strict` instead uses the **nearest** rpm
  column (`_nearest_rpm_col`). WS2's 662 V map begins at **rpm = 0**, and that
  column has exactly **one** feasible cell, at T = 0 — so `t_feas_max_col[0] =
  t_feas_min_col[0] = 0.0`. Every motoring sample below 50 rpm (**v < 0.70
  km/h**) is therefore tested against a zero-width envelope and flagged.
- Excluding that one degenerate column, WS4's nearest-column count falls to
  **0.0–3.4 s at nominal** and 3.8–18.6 s at CdA 5.4. The entire 15–21 s/cycle
  gap is that column.

Nothing moves: those samples book **zero** unbooked loss
(`unbooked_bus_kWh_linear` equals `..._locked_only` in both cases, confirming
the unlocked launch exposure contributes nothing), and both counts leave the
shape of the finding intact. But §4.1 and F-9 print 22.7–31.3 s/cycle as the
measured exposure without saying that four fifths of it is a boundary
artifact of the grid's first column. **Resolution:** carry the interpolated-
envelope count alongside the nearest-column one, note the rpm = 0 degeneracy,
and close D5.

## m3 — R14 governing-case labels missing on worst-case fields whose siblings have them

In `interface_ws4`, these min/max fields over enumerated case sets carry no
`_governing_case`, inconsistently with adjacent fields that do:
`gate_g1/boundary_convention_exposure/nominal_one_sided_pp_max` (its
`cda_5.4` sibling has one); `gate_g1/chain_weighting_convention/
series_duty_weighted/eta_bus_to_wheel_max` (its `_min` has one);
`series_duty_v2/r22d_coast_spin_member/{coast_no_regen_s_max,
coast_spin_shaft_kWh_max, coast_spin_bus_kWh_max}` and the same three
duplicated under `spin_drag_operational_note_r22d/measured_on_series_duty_v2`
(the block's `unbooked_pp_max` does carry one); plus, in the archived block,
`gate_g1/verdict/margin_pct_ensemble_max` and the three
`attribution_rows/*/delta_pp_min`. Per-run temporal extrema (`soc_min`,
`soc_max`, `soc_usable_min`) are correctly out of scope for R14 and are not
counted here. `unserved_energy_verdict.worst_case_governing_case`'s "no
governing case — every ordered case is exactly zero on all 8 seeds" is an
acceptable degenerate-tie label. **Resolution:** label the eight fields
above.

## m4 — R34 compliance is asserted as "one per run" while one trace covers 24 ordered runs, and the interpretation is never stated

BASELINE_v5 R34: *"Every pipeline exports a 10 Hz trace file per run."* The
trace file's own header line reads *"R34 10 Hz trace, one per run."* and §13
repeats it — but there is exactly one trace, for `nominal / seed 23 / mode
(b)`, out of 24 ordered mode-(b) runs (72+ simulated runs in the KX section).
R34's stated consumer is the WS10 exhibit/simulator, which suggests per
simulated run; the per-pipeline-run reading is also available; WS4 states
neither. The trace itself is correct and complete (V2). **Resolution:** state
the interpretation in `trace_files`, and if the per-simulated-run reading is
intended, emit the remaining 23 (or a decimated set) — the 5 s SOC
trajectories already cover all 24 at lower rate.

## m5 — the two changelogs name different sets of four F1 locations, and the occurrence pin counts occurrences without checking locations

§0-KX says the F1 phrase was "corrected in all four (headline, §0-R, §6 table,
ESC-2)". §0-R says "corrected in the headline, §6, ESC-2 **and ESC-6**".
ESC-6 contains no seed count; the fourth occurrence is in §0-R itself. The
new `verify_ws4.py` pin asserts `FLAT.count(phrase) == 4` — it would pass
identically if one occurrence sat in the wrong section. The r3 failure mode
was a correction landing in three of four *places*; a count is not a place
check. **Resolution:** reconcile the two changelog sentences, and pin the
phrase per section (e.g. count within the §6 table slice, the ESC-2 slice,
etc.).

## m6 — the WS6 ledger rows divide an 8-seed maximum energy by the reference seed's duration, and carry one governing label for a row of independently-maximised components

`run_ws4.py` builds each `series_duty_v2_*_cycle_average` row as
`ensemble[X_max] / (per_seed["23"].duration_s / 3600)`. The maximum energy
comes from whichever seed maximises it; the divisor is always seed 23's
duration. Recomputing each seed's own average and taking the maximum gives
73.0408 / 86.8728 / 59.9516 kW against the exported 72.5516 / 86.2949 /
59.7385 — the rows understate the true 8-seed maximum cycle average by
0.4–0.7 %. The label "(8-seed max, reference-seed duration)" discloses the
construction but not that it is not the maximum of the quantity. Separately,
each row's single `governing_case` is `engine_reject_kWh_max_governing_case`,
applied to generator, chain and friction figures that may be maximised by
different seeds. **Resolution:** take the maximum of the per-seed averages,
or label each component's governing seed.

## m7 — the duty's transient heat never reaches the ledger rows WS6 is told to size against

§4-KX.7 tells WS6 these rows "are the Vehicle Zero V2 rows WS6 should size
against" and exports **cycle averages only**: engine rejection 72.6 / 86.3 /
59.7 kW. Measured on the same runs, peak engine rejection is **239.8 / 239.8 /
215.7 kW**, with 2-minute rolling maxima of 239.8 / 239.8 / 179.9 kW and
10-minute maxima of 153.9 / 175.3 / 133.0 kW — the same M1 excursions. At the
corner the implied radiator package peak is ~103.5 kW against R20's declared
design point of **95.0 kW in +45 °C air**, in the same ambient; the 2-minute
average there (86.4 kW) stays under it, so **R20/ESC-4's "radiator design
case = R6 corner" survives** — but a cooling owner reading a 59.7 kW row for
this case would not know a 216 kW transient is in the duty. Program rule 7
asks for heat by component **and case**; a cycle mean is not the case.
**Resolution:** add peak and a rolling-window (e.g. 2-min and 10-min) maximum
rejection per case to `heat_ledger_ws6`, with R14 labels.

## m8 — the hysteresis sensitivity is single-seed for a stochastic quantity

§4-KX.6's genset-hysteresis table (simulator band vs WS3's allocated 3.5 kWh
band) is run on the reference seed only and reports genset starts 5/4/6 vs
6/6/9. Starts are a stochastic output — the ordered 8-seed set spans 5–6 at
nominal for the simulator band alone — and R9 requires 8-seed envelopes for
stochastic extrema. The conclusion drawn ("neither band changes any
conclusion above") rests on one draw. The table is honestly labelled
"Reference seed 23". **Resolution:** run the WS3 band over the 8-seed
ensemble, or state explicitly that the sensitivity is indicative and not an
envelope.

---

## Notes for the lead (not findings)

1. **The escalations, on their merits.** ESC-9 is correctly characterised
   and correctly not self-resolved; every number in it re-derives (192.5 kW
   discharge, 147.6 kW charge, 0.6129 kWh at `alt2000m_45C`, 825–975 s/cycle
   below the SOC gate at CdA 5.4), the R12/ES-4 125 kW figure is the right
   citation, the SOC nameplate↔usable mapping is arithmetically correct
   against WS3's `end_stops_pct_nameplate` [15, 10] and `dispatch_window`
   [0.15, 0.90], and WS4 is right that 125 kW is the more permissive of the
   two figures on the record. Its defect is B2, not its numbers. ESC-8 is
   correctly raised and correctly not self-resolved but **understates itself**
   (B1). ESC-7 is correctly not self-resolved and WS4 is right to refuse to
   invent a payload basis — but note it does not *challenge* a ruling (R32
   itself says "Not executed now"), and its exported companion cannot serve
   R32's purpose (M3).
2. **`gate_g1`'s archival is otherwise complete and well done.** `status:
   executed_kill_2026-08-30`, an unambiguous archival notice, the four
   directive members present, the lockup spin member correctly quarantined
   with an explicit double-count warning in the live R22d note, and mode (a)
   declared non-existent. The one leak is the reverse of the one the
   directive feared: not a dead field being consumed, but a live need served
   only from the dead block (M2).
3. **Wheel / shaft / bus discipline checks out** where I probed it. WS2
   exports `PM_spin_total_85kmh_W = 1480 = 1109 shaft + 371 bus`, and WS4's
   R22d pricing adds `shaft / eta_chain + bus`, which is the correct
   composition of the two members; the coast counter fires only at 1–3 km/h
   (below `v_regen_blend_lo = 3.0 km/h`), so §4-KX.5's "walking pace" claim is
   exact. `bus_energy_kWh` (gross positive bus load, 89.51 kWh seed 23) and
   the F5 block's `bus_kWh` (86.08 kWh, motoring chain only) are different
   quantities with different names — no mismatch, but neither is defined in
   the interface.
4. **The three-case set is not hiding a governing case on the energy
   question** (V7): the compound corner and the full R6 rating corner both
   complete with zero unserved. The genuinely worst pack-power case
   (`alt2000m_45C`, 192.5 kW) *is* inside the ordered set, because thin air
   keeps the genset off and leaves the pack covering transients alone.
5. **Determinism.** `verify_ws4.py` exits 0 on the committed artifacts
   (184 renderings + interface block + 413 pins), the interface block is
   byte-identical to the JSON at `indent=1`, the SOC CSV contains all 24 runs
   and reproduces `soc_window_check` exactly, and the R34 trace reproduces its
   run's scalars from first principles. I did not repeat the foreman's
   byte-stability gate.
6. **None of the findings above touches the archived G1 verdict**, which
   reproduces exactly (V9) and is not reopened here.

---

Key paths (absolute):
`/Users/valimenai/Documents/Project Volt/WS4_genset/REPORT_WS4.md`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/results_ws4.json`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/ws4_sim.py`
(B1: the R16 cap sits inside the `pw < 0.0` regen branch; M1: the emergency
branch caps on `p_peak_kw` = the automotive peak),
`/Users/valimenai/Documents/Project Volt/WS4_genset/ws4_chain.py`
(m2: `boundary_exposure_strict` / `_nearest_rpm_col`),
`/Users/valimenai/Documents/Project Volt/WS4_genset/run_ws4.py`
(M3: `PAYLOAD_T`; m6: the ledger-row divisor),
`/Users/valimenai/Documents/Project Volt/WS4_genset/make_report_ws4.py`
(m1: lines 205, 941-942),
`/Users/valimenai/Documents/Project Volt/WS4_genset/verify_ws4.py`
(m5: the F1 occurrence pin, ~line 357).
