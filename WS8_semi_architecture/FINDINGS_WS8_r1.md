# FINDINGS — WS8 (Vehicle One, semi-scale architecture trial) — round 1

Adjudicator, fresh context. Read from disk only; nothing in this folder or
any other was modified. Findings are for the lead (CLAUDE.md rule 9); the
worker does not act on them.

**Verdict: NOT CLEAN. Two blocking findings, five material, six minor.**
None of them overturns the headline outcome — *no candidate advances* —
and none rescues S3, whose kill rests on a capability result I re-derived
independently and confirm. The blocking findings are (1) a machine-readable
heat-ledger export to WS6 that is wrong in both magnitude and attribution,
and (2) an inherited WS3 input the report states it uses and the pipeline
never applies, in the corner that governs every exported worst-case field.

---

## 0. What was independently re-derived, and what checks out

Re-derived from first principles or by re-running the code in a scratch
copy (never in place). All of the following **agree**:

| quantity | report / interface | my re-derivation |
|---|---|---|
| 13 L peak power | 352.0 kW | 352.02 kW (torque curve x omega, max at 1,600 rpm) |
| solved `eta_i0` / island BSFC / island rpm / peak BTE | 0.4788 / 185.0 / 1141 / 0.455 | 0.478753 / 185.0000 / 1141.35 / 0.45466 |
| payloads S0..S4 | 20,785 / 19,397.7 / 19,105.7 / 19,559.2 / 19,343.6 kg | identical (mass ledger summed by hand from `ws8_params.MassLedger` + component models) |
| 12% startability force | 44.4 kN | 44,372.6 N |
| mu required, single axle / 6x4 tandem | 0.587 / 0.293 | 0.5866 / 0.2933 |
| dry tandem adhesion ceiling | 105.9 kN | 105.90 kN |
| road load at 95 km/h flat | 2,290 N aero + 1,959 N roll | 2,290.37 + 1,958.57 N |
| S3 axle A at ratio 3.60 vs 6% demand | 11.7 kN vs 24.0 kN | 11,773 N vs 23,974 N |
| S3 e-axle climb energy vs buffer | 133 vs 21.6 kWh | 132.75 vs 21.602 kWh |
| **every margin, all 4 candidates x 5 corners x (min/median/max)** | interface + section 6.1 | recomputed from per-seed `MJ_per_km`, `payload_kg`: **exact match to 1e-9 in all 60 values** |
| WHR gain curve at 25/55/85/100% load, all three systems | section 5 | reproduced closed-form |

**Interface integrity (three-way).** The JSON block in `REPORT_WS8.md`
is **byte-identical** to `results_ws8.json['interface_ws8']` (checked
independently of `verify_ws8.py`), and the interface agrees with
`data/whr_gate.csv`, `data/heat_ledger_ws6.csv`, `data/s3_fixed_ratio_sweep.csv`
and `data/mass_ledger.csv`. `verify_ws8.py` passes 91 checks.

**Determinism (rule 1) — tested, not accepted.** I did not take
`data/determinism_check.json` on trust.
- `run_ws8.py --from-checkpoint` in a fresh copy: `results_ws8.json`
  **byte-identical** to the committed file, and all seven `data/*.csv`
  **byte-identical**.
- `make_report_ws8.py`: `REPORT_WS8.md` regenerated **byte-identical**.
- `run_ws8.py --only-nominal --jobs 3` from scratch in a separate process
  and a separate worker pool: the nominal trial slice is identical to the
  committed one, **including the exact sha256 prefix `bccb2920a42dfe73`
  the report quotes**; `task1_cycles` and `task2_s0_calibration` identical.

Rule 1 is satisfied. The "not checked" disclosure (four sensitivity
corners and the WHR gate not re-simulated) is stated in the artifact and
is a fair limitation.

**Assignment coverage.** Tasks 0-5 are all executed; every ordered
sensitivity (payload +/-20%, grade-heavy, -10 C) and all three ordered
S3-specific risks are present. All seven escalations cite a ruling or the
assignment clause they challenge, and none is self-resolved. Rule 10 is
respected: nothing outside this folder was written.

---

## BLOCKING

### F1 — The WS6 heat-ledger export understates the resistor sizing case by up to 2.4x and books compression-brake heat as resistor heat

**Severity: blocking.** WS6 is the heat-ledger owner and is RELEASED
(BASELINE_v3). This is the machine-readable field it consumes.

**What is wrong — three separate defects in one export.**

**(a) The governing case is outside the enumerated case set.** The
interface exports `heat_ledger_WS6 -> S1 -> worst_case -> brake_resistor_kW
= 210.71 kW, governing_case "descent_6pct"`, with rule `"max"` over
`{cruise_95kmh_flat, climb_6pct, descent_6pct}`. WS8's own nominal-corner
simulation records, in the same `results_ws8.json`, a resistor bus power
of **314.6 kW for S1, 503.4 kW for S2 and 284.1 kW for S3**
(`task3_trial/*/S*/per_cycle/*/resistor_peak_kW`). The three-case set
prices the descent at 100 km/h with the pack accepting its full 240 kW
throughout; the pack has only 16.8 kWh of headroom from its 0.60 target
and fills in ~4.2 min of a ~9.6 min descent, after which the whole
retarding duty is the resistor's. A cooling package sized on 211 kW is
sized on a third to a half of the real case.

**(b) Compression-brake heat is booked to the brake resistor, and the
exhaust row is explicitly zeroed.** `ws8_candidates.py:964` (S2) and
`:1225` (S3) both `return f_t, f_regen, f_res + f_eb` — the engine-brake
force is bundled into the same envelope channel as the resistor, and
`run_ws8.py:1394` then sets `out["engine_exhaust_kW"] = max(0.0, resistor * 0.0)`
for exactly those two candidates. Measured at the ledger's own descent
speed (100 km/h):

| | resistor rating | retard channel in the envelope | of which compression brake | exported as `brake_resistor_kW` | exported as `engine_exhaust_kW` |
|---|---|---|---|---|---|
| S1 | 340 kW | 340.0 kW | 0.0 kW | 210.71 | 0 |
| S2 | 340 kW | 530.5 kW | **190.5 kW** | 210.71 | **0** |
| S3 | 200 kW | 406.1 kW | **206.1 kW** | 210.71 | **0** |

S1, S2 and S3 all export the identical 210.71 kW despite three different
retarder architectures — the tell that the split is not being tracked.
For S3 the exported resistor heat (210.71 kW) also **exceeds the 200 kW
resistor whose 71.8 kg WS8 charged against S3's payload**. Air-cooled
grid resistors and an exhaust-side compression brake go to different
places in a packaging study; this is the wrong member of the set, and the
report's section 12 prose ("a series candidate holding the 6% grade puts
several hundred kilowatts into a resistor bank that has to reject it to
air") describes the right physics over the wrong number.

**(c) Foundation-brake heat is missing entirely, and S0's descent case
does not close.** `component_heat_kw()` has no friction-brake row, yet
`FRICTION_BRAKE_CONT_ALLOWANCE_KW = 60.0` is a declared, deliberately
used continuous dissipation, and the trial records up to 3.8 kWh of
friction-brake energy per cycle. On the S0 descent case the ledger reports
`case_wheel_power_kW = -317.67` and `total_rejected_kW = 234.05`: **83.6 kW
of rejected heat has no row**. (Same case, a second artefact: `v_cap`
lands exactly on the AMT's gear-jump discontinuity, so the exported
234.0 kW is the *lower* side of a step whose *upper* side, 303.8 kW, is
what actually holds the speed.)

**Evidence.** `run_ws8.py:1330-1400` (`component_heat_kw`), `:1382`,
`:1394-1395`; `ws8_candidates.py:964, 1225`;
`results_ws8.json -> heat_ledger.candidates.*`, `data/heat_ledger_ws6.csv`;
`results_ws8.json -> task3_trial.*.S*.per_cycle.*.resistor_peak_kW`;
`REPORT_WS8.md` section 12.

**What would resolve it.** (i) Split the retard channel so the envelope
and the accounting return resistor and engine-brake force separately, and
book each to its own row. (ii) Add a `pack_saturated` descent case (or
carry SOC into the descent case) to the enumerated set, so the R14 max is
taken over a set that contains the sizing case; alternatively export the
per-run `max(resistor_peak_kW)` over (corner, cycle, seed) as the
governing case with its label. (iii) Add a friction-brake row and assert
that `total_rejected_kW` closes against `case_wheel_power_kW` for every
case. (iv) Assert every exported component heat against the rating of the
hardware whose mass was charged.

---

### F2 — The cold corner does not model WS3 cold charge acceptance, but the report says it does; that corner governs every exported worst-case margin

**Severity: blocking.**

**What is wrong.** `Pack8.p_cont_chg_kw_at()` (`ws8_electric.py:337`) and
`Pack8.COLD_CHG_FACTOR` (`:333`) — the WS3-derived collapse of NMC charge
acceptance at -10 C — are **dead code. Nothing in the pipeline calls
them.** Every envelope and every dispatch uses the warm nameplate
`pack.p_cont_chg_kw` in all five corners
(`ws8_candidates.py` S1 `:803`, S2 `:954`, S3 `:1215`, S4 `:1561`;
`series_dispatch` `:584`; S3's own SOC loop `:1393, :1412`).

I confirmed this numerically rather than by reading: S1's envelope
regen-force channel is *identical* at nominal and at the cold corner
(24,002.4 N at 10 m/s in both), whereas the unused method returns
**30.50 kW against the 240.02 kW the model actually uses — a factor of
7.9**.

The consequences are not confined to a comment:
- `run_ws8.py:73` labels the corner *"-10 C: denser air, electrified
  accessory load up, **WS3 cold charge acceptance**, tyre Crr up 8%"*.
  Only three of those four are implemented.
- `REPORT_WS8.md:1555` lists under Provenance: *"**WS3** cell definitions,
  pack overhead model (1.55 x cell + 35 kg) and **cold charge-acceptance
  figures**"*. The third item is not used.
- `REPORT_WS8.md:403`, Recommendation 5 — the report's principal
  forward-looking instruction to the lead — states: *"The cold corner is
  the one to attack first. It is binding for all four candidates, and its
  cause is specific and fixable: **WS3's cells accept about an eighth of
  their warm charge power at -10 C, so descent regen goes to the resistor
  instead of the pack**"*. That mechanism is not in the model that
  produced the numbers. What the cold corner actually contains is denser
  air (1.341 vs 1.196), Crr x1.08, and bus aux 6.6 vs 3.4 kW.

`cold_minus10C` is the `governing_case` of `worst_case_margin_pct` for
**all four candidates** in the interface block. Applying the real cold
acceptance would push descent energy from the pack into the resistor and
make those margins **worse**, so every exported worst-case margin is
optimistic by an unquantified amount, and the diagnosis attached to it is
unsupported.

**Evidence.** `ws8_electric.py:333-343` (defined, never called — `grep -rn
'p_cont_chg_kw_at' *.py` returns only the definition); envelope equality
at nominal vs cold, measured; `run_ws8.py:68-75`; `REPORT_WS8.md:403,1555`.

**What would resolve it.** Either wire `p_cont_chg_kw_at(ctx.t_amb_c)`
into the regen envelope and into the pack charge limit in
`series_dispatch` and S3's loop, and re-run the cold corner; or delete the
claim from the corner label, from the report's provenance list and from
Recommendation 5, and state plainly that cold charge acceptance is *not*
modelled. Whichever the lead directs, the exported worst-case margins and
Recommendation 5 must move together.

---

## MATERIAL

### F3 — S2's single engine is run mechanically locked to the wheels and as a free-speed genset at the same time

**Severity: material.** Direction: flatters S2, the best-scoring candidate.

**What is wrong.** S2 carries one `engine_13L_wet` in its mass ledger.
Inside the lockup band `S2.account()` computes the mechanical path's fuel
at the road-imposed engine speed (correct), and then calls
`series_dispatch` (`ws8_candidates.py:1032`) on the *same* engine, which
prices genset fuel on `GensetLine`'s **BSFC-optimal free-speed locus** and
adds it (`:1037`). Nothing couples the two, and nothing caps their sum at
the engine's full-load curve.

Measured on LH-520, seed 8101, nominal:
- locked fraction of moving samples **0.681**; genset-on fraction 0.105;
- **3.7% of locked samples have the genset running**, producing
  **15.37 kWh of the trip's 119.19 kWh of genset energy (12.9%)**;
- on **70.6%** of those samples the locked shaft power plus the genset's
  shaft demand **exceeds the engine's full-load torque at the locked
  speed**, by up to **305.7 kW**;
- the genset line asks for a mean **908 rpm** while the engine is
  physically at a mean **1,210 rpm**.

Both errors run the same way: fuel priced at a better operating point than
the engine can be at, and shaft power drawn beyond the full-load curve.
The assignment ordered the opposite for exactly this candidate: *"charge
every remaining tax honestly (re-derive drag when connected, **off-point
engine operation at band edges**)"* — and S2's declared policy, rendered
in report section 4.2, says *"where road speed - not the supervisor - sets
engine speed"*. For that 13% of genset energy the supervisor sets it.

**Evidence.** `ws8_candidates.py:966-1037`; my probe reproducing
`S2.account()` internals step for step on the committed cycle.

**What would resolve it.** While locked, price generator output at the
road-imposed rpm (not `GensetLine.fuel`), and cap `t_mech + t_aux + t_gen`
at `engine.t_max(rpm_lock)`, spilling the remainder to unserved energy;
or forbid genset operation while locked and let the pack carry it. Then
re-run S2 at every corner and re-read section 4.3's bracket, which
inherits S2's fuel.

---

### F4 — The charge-sustaining correction pays S2 a fuel *credit* for finishing with a fuller pack, and that credit decides the S1-vs-S2 ordering

**Severity: material.**

**What is wrong.** `apply_energy_corrections()` (`run_ws8.py:169-177`)
applies `g_soc = -dSOC * usable / (eta * LHV)` **symmetrically**: a pack
that ends *fuller* than it started earns a negative fuel charge. On
LH-520 — 70% of the fleet mission — S2 ends a mean **+0.183 SOC** above
its 0.60 start (range +0.076 to +0.253), earning a mean **-1,726 g** of
fuel, i.e. **-1.13% of its fuel on the dominant cycle**. The surplus was
put there by regenerative braking, not by fuel; S2's dispatch (hysteresis
on above 55 kW, off below 35 kW) has no mechanism to spend a pack that
sits above target, so it ends high every seed.

Effect on the headline, recomputed from the committed per-seed data:

| nominal margin vs S0 | as reported | deficit-only correction | no SOC correction |
|---|---|---|---|
| S1 min / median | -0.66 / **+0.75** | -0.66 / +0.75 | +0.02 / **+1.09** |
| S2 min / median | +0.36 / **+1.70** | +0.06 / +0.88 | +0.41 / **+0.99** |

**About half of S2's headline advantage is the credit, and the ordering of
the two leading candidates reverses when the correction is removed.**

The report does not disclose the credit direction. Section 4 describes the
correction as *"plus the make-up for any pack it finished **flatter** than
it started"*, and the interface's `fuel_correction_share` exports only the
**max** of a signed quantity — for S2 it exports `value 0.0166` while the
LH-520 median share is **-0.0113**, with the accompanying `meaning` string
saying *"A large share means the candidate could not actually do the
mission"*. A reader of the interface cannot see that S2's dominant cycle
carries a credit.

**Evidence.** `run_ws8.py:150-181`, `interface_block` `:1839-1852`;
`results_ws8.json -> task3_trial.nominal.S*.per_cycle.*` (`soc_start`,
`soc_end`, `fuel_g_charge_correction`, `correction_share_of_fuel`);
recomputation above.

**What would resolve it.** Rule on the convention (a J1711-style symmetric
correction is defensible if declared), then: state both directions in
section 4 and in the interface `meaning`; export the correction share
signed, with min *and* max over the (cycle, seed) set rather than max
alone; and either tighten the dispatch so the mission is genuinely
charge-sustaining, or report the credit-free margin alongside so the
S1/S2 ordering is visible for what it is.

---

### F5 — R22(d) spin drag is ~zero where the baseline requires it, larger for the candidate that bought a disconnect to delete it, and double-counted for S3

**Severity: material.** This is the surviving G1(b) member; BASELINE_v3
R22(d) carries it program-wide.

**What is wrong — three inconsistent treatments of one quantity.**

1. **S1 and S4 (permanently geared, no disconnect) are charged nothing.**
   The test is `F_trac<=1 & F_regen<=1 & F_retard<=1 & v>0.5`
   (`ws8_candidates.py:529`). In this integrator the driver is always
   either pulling or braking, so **0.0066% of moving samples** qualify.
   S1's charged spin over LH-520 is **0.0021 kWh**; charged on all moving
   samples it would be **36.8 kWh**. The machine really does drag
   (I measured the model's own `spin_drag_kw`: 5.87 kW at 85 km/h,
   6.83 kW at 95 km/h, bus-side, both machines). S1's declared policy,
   printed in report section 4.2, says the drag *is* charged.
2. **S2, which buys a 42 kg `traction_disconnect` specifically to delete
   this tax, pays 140x more of it than S1, which has no disconnect**
   (0.2949 vs 0.0021 kWh). `unloaded_connected` (`:1022`) charges spin on
   locked-but-connected samples. The model and the declared architecture
   disagree in sign; the report's section 4.2 claim that S2's disconnect
   deletes "the G1(b) tax ... by hardware" describes a benefit the
   comparison never gave S1 in the first place.
3. **S3 double-counts it.** `if connected[i]: demand += spin_rate[i]`
   (`:1387-1389`) adds the zero-torque loss on **every** connected sample,
   including those where the machine is delivering torque or regenerating
   — on top of the WS2 measured loss already evaluated at that operating
   point. Of S3's 16.28 kWh of charged spin on LH-520, **14.80 kWh
   (91%) falls on loaded samples**. At S3's own correction efficiency
   that is ~125 MJ on a 6,826 MJ cycle, i.e. roughly **1.8 pp of S3's
   margin charged twice**.

**Evidence.** `ws8_candidates.py:526-534, 1018-1027, 1385-1390`;
`results_ws8.json -> task3_trial.nominal.S*.per_cycle.LH-520[*].e_spin_kWh`
(S1 0.0021, S2 0.2949, S3 16.279, S4 0.0023); probe measuring the
loaded/idle split and the idle-sample fraction.

**What would resolve it.** One rule for all candidates: charge
`loss_ws2(n, 0)` whenever the machine is geared to the road and the
commanded torque is below a stated threshold, and charge *nothing extra*
when it is loaded (the map already has it). Then re-run. If the integrator
genuinely produces no coasting, say so explicitly and quantify what R22(d)
would cost under a coast-permitting driver, because at Vehicle Zero this
member was worth -1.77 pp.

---

### F6 — Unserved and stored energy are priced back into fuel at the genset's *best-point* efficiency — a peak-point scalar (rule 5) applied to up to 23% of a candidate's fuel

**Severity: material.**

**What is wrong.** `genset_eta_for_correction()` (`run_ws8.py:129-141`)
returns `line.best_point()["genset_eta_fuel_to_bus"]` — the maximum of the
fuel-to-bus efficiency curve (S1 0.4279 at 260.5 kW; S4 0.4059 at
142.3 kW) — and for S3, which has no genset, the engine's **island BSFC**
times the axle-A driveline (0.4276). That single scalar prices:

| candidate | correction as share of reported fuel (max over cycle,seed) | unserved kWh, worst case |
|---|---|---|
| S3 | **23.4%** | 204.56 (S3/grade_heavy/LH-520) |
| S4 | 8.6% | 112.51 |
| S1 | 2.6% | 16.61 |

For S3 the scalar is doubly generous: section 6.2 of the same report
proves the mechanical path *cannot deliver that energy on the grade at
any ratio*, yet the shortfall is charged as though it had been delivered
through that path at the engine's best point. Rule 5 forbids peak-point
scalars; this is one, sitting on the largest single correction in the
trial.

Sensitivity, recomputed from the committed per-seed data — pricing both
corrections 10% worse than the best point:

| nominal median margin | as reported | corrections priced 10% worse |
|---|---|---|
| S1 | +0.75 | +0.64 |
| S3 | **-3.83** | **-5.66** |
| S4 | -0.95 | -1.42 |

**Evidence.** `run_ws8.py:129-181`; `results_ws8.json ->
interface_ws8.candidates.*.fuel_correction_share`; recomputation above.

**What would resolve it.** Price corrections at the candidate's own
**duty-averaged** fuel-to-bus efficiency over the run being corrected, not
at the locus maximum; for S3, price them at the efficiency of the path
that would actually have had to supply them (which for the mountain
segment does not exist — that is a capability statement, and the report
should carry it as one rather than converting it to fuel at an island
BSFC). Report the correction efficiency used, per candidate, in the
interface — at present it is in the per-run rows but nowhere in the
report or the interface block.

---

### F7 — The S0 calibration cross-check, the report's only external evidence, is asserted on a median while its own ensemble spans the entire reference band

**Severity: material.** Rule 4.

**What is wrong.** Section 3.4 and ESC-WS8-7 rest the whole calibration
argument on one number: *"S0, same corridor with grade zeroed (median)
33.08 L/100 km"* against ICCT 32.6 / 33.1 / 29.9, concluding *"The model
lands on the public band to about one percent, with nothing fitted to
it."* The 8-seed envelope for that same quantity is already computed and
stored — `results_ws8.json ->
task2_s0_calibration.flat_corridor_crosscheck.L_per_100km` = **min 29.82,
median 33.08, max 39.36** — and is not rendered anywhere in the report.
The envelope is wider than the entire public band it is being compared
against (29.9 to 33.1). In a program whose rule 4 exists because a
single-draw extremum was a blocking WS1 defect, the one externally-anchored
claim in this report is made on a point statistic with the envelope
suppressed.

Second, the comparison is **not mass-matched and the reference mass is
never stated**. Re-running the same flat corridor in a scratch copy:

| combination mass | flat-corridor median |
|---|---|
| 36,300 kg (as reported) | 33.08 L/100 km |
| 40,000 kg (EU regulatory GCW) | **34.34 L/100 km** |
| WS8 tare at ICCT's 19.3 t payload | 32.58 L/100 km |

A 10% GCW difference moves the number by 3.8% — several times the claimed
one-percent agreement — and the report compares a 20.8 t-payload result
against a 19.3 t-payload reference without saying so.

**Evidence.** `REPORT_WS8.md` section 3.4 and ESC-WS8-7;
`results_ws8.json -> task2_s0_calibration.flat_corridor_crosscheck`;
`run_ws8.py:823-853`; my re-run at three masses.

**What would resolve it.** Render the cross-check as an ensemble envelope
(min/median/max) like every other stochastic quantity in the report;
state the reference combination's GCW and payload and either mass-match
the cross-check to it or state the residual; and soften ESC-WS8-7's
"match to about one percent" to what the envelope supports.

---

## MINOR

### F8 — S4's headline specification is wrong by ~14%
`ws8_candidates.py:1490` titles S4 *"~170 kW sustainer genset"*, and that
string is rendered verbatim in the report's headline table (section 4) and
in section 0. The model uses `ENG_7L` flat-rated to **193.9 kW shaft /
185.1 kW bus**; the code comment three lines below the title says
*"~200 kW, the TOP of the assignment's 150-200 kW band"*. `verify_ws8.py`
does not check class titles, so this passed. **Resolve:** render the
computed rating instead of a literal, and add title/spec strings to the
verify set.

### F9 — A hand-written note in `results_ws8.json` contradicts the value computed two lines above it
`run_ws8.py:1424` stores `note="2,533 N of aero and 1,959 N of rolling..."`
in the same `sanity.road_load_95kmh_flat` block whose computed
`model_aero_N` is **2,290.37**. 2,533 N is the 100 km/h value. The report
prints both, four lines apart, in section 10 — the section whose purpose
is first-principles checking. Because the wrong figure lives inside the
data file as prose, `verify_ws8.py` cannot catch it. **Resolve:** format
the note from the computed value.

### F10 — Section 4.3's "margin vs S0" column uses a different statistic from the headline, unlabelled
`two_speed_bracket` (`run_ws8.py:987`) computes
`(s0_median - cand_median)/s0_median`, i.e. a ratio of medians, while
every other margin in the report is the median of per-seed *paired*
margins. The same quantity therefore appears as **+0.57%** in section 4.3
and **+0.75%** in section 4 for S1, and **-0.99%** vs **-0.95%** for S4.
The basis is not stated. **Resolve:** compute the bracket on paired
per-seed margins, or label the column's basis.

### F11 — Provenance claims two inherited objects the pipeline never exercises
Report section 14 lists *"WS4 `WillansEngine`, `PMGenerator`,
**`derate_factor`** and the R12 chain conventions"*. `derate_factor` is
imported (`ws8_engine.py:40`) and re-exported (`:361`) but **never
called**: no candidate's engine or genset is derated for ambient in any
corner, including -10 C. Together with F2's cold charge acceptance, two of
the listed inherited inputs are inert. **Resolve:** apply them or remove
them from the provenance list.

### F12 — `max_ratio_without_overspeed = 3.60` is a property of the swept grid, not of the physics
The interface's `S3_fixed_ratio_feasibility.max_ratio_without_overspeed`
is 3.60 because the next ratio in the enumerated sweep, 3.77, lands at
**2,100.05 rpm** — 0.05 rpm over the ceiling. The physical limit is
3.7699. The interface's `rule` string does say "enumerated over the swept
ratio set", but the report's section 6.2 prose states it flatly:
*"Highest ratio that does not over-speed the engine at 105 km/h: 3.60."*
The S3 conclusion is unaffected — I checked that holding 6% at the
coupling floor needs about **7.2:1**, which is ~4,000 rpm at 105 km/h, so
no ratio closes the gap. **Resolve:** solve the ratio ceiling in closed
form and report it, keeping the sweep as the illustration.

### F13 — "~3,800 m of climb" is a literal, and it is the top of the ensemble
Hard-coded at `make_report_ws8.py:141` and `:328`, and used twice to
justify why S0 misses the fuel corridor. The committed ensemble is
**min 3,507 / median 3,704 / max 3,838 m**. **Resolve:** format from
`task1_cycles`.

---

## Things I looked for and did not find

Recorded so the lead knows the ground was covered.

- **Single-draw extrema (the WS1 defect).** Every stochastic extremum in
  the interface is an 8-seed envelope. Checked all 60 margin values.
- **Wheel / shaft / bus confusion.** The traction chain is bus-side
  throughout, with no scalar PE member anywhere; the R12 convention is
  honoured. The one place a boundary is crossed silently is the resistor
  rating, which is applied at the **wheel** (`min(f_gen - f_regen,
  resistor_kW*1e3/v)`) so the resistor actually dissipates ~0.93 of its
  nameplate; conservative, and it does not affect fuel.
- **Optimistic inputs inherited without flags.** The two largest — the
  k=3.6 machine stretch and the R18 flat-rating transfer — are both
  escalated (ESC-WS8-2, ESC-WS8-4) with the direction of error stated.
  WS2's map, WS3's cells and WS4's Willans construction are used through
  their own ruled loaders; the scaling laws are declared in one place and
  applied in one place, and the per-unit-invariance check is a genuine
  implementation check (correctly labelled as *not* a physics check).
- **A governing case outside the reference cycles.** Vehicle Zero's
  precedent (the 2,000 m / +45 C corner becoming worst) has no WS8
  analogue in the *ordered* corner set, and Task 5 did not order one. Not
  a compliance failure, but worth the lead's attention: WS8's corner set
  contains no altitude and no hot-ambient case, and `derate_factor` — the
  tool for both — is imported and unused (F11).
- **Escalations.** All seven cite a ruling or the assignment clause they
  challenge; none is self-resolved. ESC-WS8-7 states a WS8 preference but
  still puts the ruling to the lead, which is within rule 8.
- **S3's kill.** Re-derived independently and **confirmed**: no fixed
  ratio both cruises at 105 km/h under 2,100 rpm and holds the 6% grade;
  the e-axle-alone climb needs 132.75 kWh against 21.60 kWh of usable
  swing; single-axle launch needs mu 0.587 against a 6x4's 0.293. None of
  the findings above touches that result, and F5(3) and F6 both mean S3's
  *fuel* number is more pessimistic than the model warrants — which
  strengthens, not weakens, the report's own argument that S3's fuel is
  not the finding.

---

## Suggested disposition

- **F1** and **F2** should be closed before WS6 consumes the heat ledger
  or before any WS8 number is ratified.
- **F3**, **F4**, **F5**, **F6** all move margins by fractions of a point
  to ~2 points and, between them, decide the S1-vs-S2 ordering. They do
  not change any ADVANCE/KILL verdict at the pre-committed thresholds
  (I re-ran every one of them against the criteria), so the lead may
  reasonably rule them as errata-with-re-run rather than a re-adjudication.
- **F7** is small in the numbers and large in the record: it is the only
  external anchor the report has.
- **F8-F13** are record-precision defects and can travel as a checker-pinned
  errata set.

*Findings only. Nothing here rules on an escalation, and nothing in this
folder was modified.*
