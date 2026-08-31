# REPORT_WS11 — VEHICLE ZERO RULER TRIAL

Executes **BASELINE_v5 R32**: *"the payload-denominated metric has not been applied to Vehicle Zero. It shall be … before any Vehicle Zero result is described as an efficiency advantage."*

**Question of record.** Is the ratified Vehicle Zero design more efficient than the truck it replaces, on the honest metric?

**Answer, in one line.** It depends on which variant and which duty, and the two answers have opposite signs. **V1 Postal on VOLT-SUB: ADVANCE at +20.11% ensemble-min against a 3% bar. V2 Trucker on VOLT-REG: KILL at -7.93% — it wins +8.41% per km and hands back 16.19 points of freight to get there.**

Everything below is generated from `results_ws11.json` by `make_report_ws11.py`. Every number that reaches this file passes through a formatter that records its JSON path, and `verify_ws11.py` re-resolves each path, re-formats it and asserts the string is present here verbatim. Section numbers, table headings, quoted parameter values that appear in code comments, and figures quoted from another workstream's published report are not in that set and are labelled where they appear. Round 1 claimed the assertion covered *every* number in the file; it did not (adjudication r1/m1).

> **This is round 2.** It reworks every finding in `FINDINGS_WS11_r1.md` — 3 blocking, 8 material, 13 minor. The two verdicts are unchanged in code and unchanged in number. What changed is what the report is entitled to claim about them: see §0.

---

## 0. Round-2 changelog

Round 1 was adjudicated **NOT CLEAN: 3 blocking, 8 material, 13 minor**. Every finding is addressed at root cause below. **Neither verdict moved** — both are computed at the headline settings, which are unchanged, and every round-1 headline number reproduces. What moved is what this report is entitled to claim about them.

| # | finding | what changed | where |
|---|---|---|---|
| **B1** | the bracket named *all ruler-favourable choices reversed* reversed none of the four largest ruler levers, and the KILL's robustness claim was false | all four driveline levers (gear mesh, AT pump, final drive, lock-up slip) added to `BRACKETS` singly and in combination; the combined row renamed and separated from the CdA road change; a genuine *all ruler-modelling choices pessimistic* row exported for both vehicles on both duties; **§1.3's robustness claim withdrawn and restated — V2 goes to a draw** | §1.3, §7.2 |
| **B2** | the R38 capability pass limited acceleration only, never steady-state capability; exported settled-climb speeds contradicted the capability numbers in the same file | `a = min(a_des, a_cap)` enforced on every sample; all three trip-time rows and the settled speeds re-exported; the settled-speed field redefined and only emitted where a sustained grade exists; `verify_ws11.py` asserts it reconciles with `sustained_6pct_capability_kmh`. **Gate outcome unchanged: PASS** | §6 |
| **B3** | the ruler-fuel flip point — the number that threatens the KILL — was neither computed nor exported, while the mass flip point that supports it was | flip points to 0% and to the 3% bar computed per seed with governing seeds, exported as first-class R14 fields and as a CSV; the anchor exported as an R14 two-member set; §1.2's era note restated in the direction the data points; **the calibrate order recorded as NOT satisfied** | §1.2, §7.1 |
| M1 | V1's ADVANCE has ~1 point of headroom once both of its own pending items apply, and the combination was never run | the combined corner run and exported for both vehicles; ESC-2 restated with the figure | §5.1 |
| M2 | no pending-ruling IDs anywhere in the interface block | `pending_rulings_r14` added, naming each ruling, the fields it conditions and the block that prices it; the alternative readings made reachable from the interface | §8 |
| M3 | every WS4 capability and limit counter discarded; V2 exceeds its ratified continuous rating and empties the pack, undisclosed | all counters exported per case; WS4's `emerg_cap_cont_rating` bracket exercised; WS4 KX r3's wider ESC-10 exposure quoted with its vintage pinned; **ESC-9 opened** | §6.2, §6.3 |
| M4 | a JSON note asserted what the data contradicts | note rewritten by bracket `kind`; `verify_ws11.py` now checks the direction of every bracket row rather than trusting prose | §1.3 |
| M5 | the interface exported the milder anchor member and no bracket range | R14 enumerated anchor set with both members and the governing one; ruler L/100 km bracket range added | §1.2, §8 |
| M6 | the one-factor rows were min-of-A minus min-of-B on different seeds, and the operating-point row's description was wrong | every row rebuilt on the paired per-seed statistic with the unpaired figure retained; the description corrected — **idle is absorbed into that row, not left outside it** | §4 |
| M7 | ESC-7 did not say that the gated payload-corner reading is the departure from program convention | ESC-7 now cites WS8's `payload_kg()` and R28/ESC-3 and names the novel reading | §5, ESC-7 |
| M8 | the stop-start thermal asymmetry dismissed as *roughly neutral* on reasoning that addresses a different effect | reclassified as flattering the candidate; the duty-cycle cycling measured; **ESC-8 opened** because the ratified toolchain cannot express it | §10.1, ESC-8 |
| m1–m13 | thirteen minors: the overstated verification claim, the ESC-3 arithmetic, the unrun engine-curve claim, ESC-5's wrong citation, the unstated idle rate, the untraced governing corner, the weak heat-ledger product, the undeclared derate asymmetry, the unpinned sources, the `[SOURCED]` interpolation, the smeared cab heat, the unbracketed climb splice, and dead code | all addressed; each is named at the point it applies | throughout |
| **sweep** | the rework order required a sweep beyond the named findings | six further name/construction defects, two further unrun claims and seven further statistic-of-statistics constructions found — **four of them in code written for this round**. Clean areas recorded too | §13 |

**One previously reported number moved, and it is flagged rather than quietly replaced.** The m11 fix (iterating the cab-heat smear to a fixed point) changes V1's cold-corner-with-cab-heat bracket, because V1 is the start-stop vehicle and the added load changes the engine-off window the load is charged over. Round 1's construction, this round's, and the harshest no-waste-heat-credit reading are all tabulated side by side in §5, and the harshest one takes V1's governing corner negative. Nothing in the gate depends on the bracket — it is not ordered — but the lead should see the width.

**The two verdicts after the rework, restated:**

- **V1 Postal on VOLT-SUB: ADVANCE** at +20.11% ensemble-min, worst corner +19.12%. Unmoved. Robust to every ruler-modelling bracket (it improves to +37.78%). **Conditional** on ESC-2 + ESC-4 together, which take its governing corner to +3.66%.
- **V2 Trucker on VOLT-REG: KILL** at -7.93% ensemble-min, worst corner -9.98%. Unmoved **as computed**. But it is a draw once the ruler is bounded by this workstream's own declared parameter ranges (+0.13% min / +0.59% median), and it flips on a +6.93% ruler-fuel error against a ruler that was never calibrated. Round 1 asserted this KILL was robust to ruler modelling. **It is not, and that correction is the substance of this round.**

---

## 1. The ruler and its calibration

### 1.1 What the ruler is

| item | value | provenance |
|---|---|---|
| vehicle | 2023 ISUZU N-SERIES NPR-HD spec sheet (14,500 lbs. GVWR, Class 4) | `https://www.isuzucv.com/pdfs/npr-hd_diesel_specs.pdf`, stored as `sources/isuzucv_npr-hd_diesel_specs.pdf` |
| GVWR | 14,500 lb (6,600 kg used, per BASELINE v1) | SOURCED |
| engine | Isuzu 4HK1-TC turbocharged intercooled diesel, 5.2 L | SOURCED |
| engine map | WS4 `4HK1-TC-ref-W` Willans map, island 205.198 g/kWh | PROGRAM (the map the assignment names) |
| transmission | Aisin A465id 6-speed auto with double overdrive and lock-up 2nd-6th gears | SOURCED |
| gear ratios | 3.74, 1.96, 1.34, 1.0, 0.77, 0.63 | `https://www.transmissionrepaircostguide.com/as68rc/` |
| rear axle | 4.555:1 | SOURCED |
| tyres | 215/85R16E (10-pr) | SOURCED (matches WS1's 215/85R16, r_dyn 0.37 m) |
| alternator | 140 A | SOURCED |

**Converter and gear efficiencies, and the shift logic** — all `[WS11-DECLARED]`, all stated in `ws11_params.py` with a direction of error:

- **Torque converter**: single-stage three-element, torque ratio 2.00 at stall falling to 1.00 at coupling (SR ≈ 0.90), capacity constant set so the converter stalls at ~2,000 rpm against the reference full-load curve. Converter efficiency is SR × TR, solved per 0.1 s sample by bisection — not a scalar.
- **Lock-up**: available in 2nd–6th (SOURCED) above 20 km/h. Below that the converter is live, which is where a 30-stop delivery cycle lives.
- **Gear mesh**: 0.960 / 0.965 / 0.970 / 0.985 (direct) / 0.965 / 0.960; hypoid final drive × propshaft 0.960; AT pump/churning 1.2 kW at 1,800 rpm scaling with speed; 0.5% lock-up slip debit.
- **Shift schedule**: fuel-optimal gear selection among feasible gears (engine 1,100–2,600 rpm, 10% torque reserve), 1.0 s minimum dwell, 3% hysteresis. This is a *best-case* automatic; a production schedule is worse.
- **Idle**: modelled from the same Willans map at 700 rpm carrying the accessory torque. Headline uses **neutral idle**; the stalled-converter alternative is a bracket.
- **DFCO**: fuel cut on overrun above 1,000 rpm with the driveline coupled — the ruler pays nothing to coast.
- **Accessories**: 2.0 kW **at the crank**, i.e. the ruler's belt-driven pumps and its 140 A alternator are credited with the same efficiency as the candidates' bus-side loads.

**One discrepancy, stated rather than buried.** The assignment orders WS4's reference 4HK1-class map, whose label is *"baseline reference curve 700 Nm @ 1,600 rpm / ~153 kW"*. The sourced 2023 spec sheet rates the truck at 215 hp @ 2500 rpm and 452 lb-ft @ 1850 rpm — a little more peak power and appreciably less low-end torque than the ordered curve. I ran the ordered map. The direction of the difference is mixed and small: the ordered curve gives the ruler MORE torque where a truck lugs (better gradeability, a better-placed BSFC island) and slightly less peak power. Round 1 asserted that both effects were *"inside the brackets in §1.3"*; no bracket varied the engine curve, so that was an assertion and not a run (adjudication r1/m3). It is run now. Two declared reconstructions — the spec sheet's own rated points read as a flat 612.8 Nm plateau to 160.3 kW, and the ordered curve scaled uniformly to the same sourced peak power — move the worst margin by 0.230 pp on either vehicle. The claim stands; it now carries its run.

> **Every declared choice above is the RULER-FAVOURABLE one.** That is deliberate and it is stated once here so it can be checked everywhere: with respect to **ruler-modelling choices**, the candidates' margins in this report are lower bounds, and §1.3 now reverses *all eight* of them rather than five. The qualifier matters and round 1 omitted it: the claim is **not** true of the CdA road-load change, which lowers both candidates' margins, nor of ESC-3's aftertreatment reading. A lower bound is also the wrong guarantee for a KILL — see §7.1.

### 1.2 The sourced anchor

The assignment makes a sourced public NPR fuel-economy reference mandatory and forbids a fit to the 18–30 L/100 km corridor. **A fit was not used.**

- **Anchor**: Fuelly - Isuzu NPR-HD, all model years (owner fuel logs) — `https://www.fuelly.com/truck/isuzu/npr-hd/all`, retrieved 2026-08-31, page text stored verbatim as `sources/fuelly_npr_hd_all.txt` and SHA-256 pinned in `results_ws11.json`.
- Page statement, verbatim: *"21 Isuzu NPR-HDs have provided 180 thousand miles of real world fuel economy & MPG data."*
- Distance-weighted over the page's own per-model-year table (miles ÷ gallons, not a mean of means): **8.378 mpg = 28.07 L/100 km** over 179,702 miles and 1,044 fuel-ups.
- The 4HK1-era subset alone (MY2014–2016) reads 7.347 mpg = 32.01 L/100 km. Full table in `data/ruler_anchor.csv`.

**The era caveat points the other way, and round 1 framed it backwards.** MY2002 — the earlier 4HE1 truck — carries most of the tracked miles, and round 1 presented that as a reason to discount the anchor. But MY2002 reads **9.4 mpg, the best row on the page**. Removing it makes the anchor *thirstier* and the model's residual *worse*, not better: from -31.69% against the all-years anchor to -40.10% against the era-correct one (adjudication r1/B3). The anchor is exported as an **R14 enumerated set with both members**, and the governing member is the era-correct subset, not the milder one.

**Model against anchor.** The ruler as specified above returns **19.18 L/100 km** on VOLT-SUB at GVW (8-seed median; range 19.11–19.22), which is inside the assignment's 18–30 L/100 km sanity corridor and -31.69% against the all-years anchor, -40.10% against the era-correct one. With every ruler-MODELLING choice at its declared pessimistic end (§1.3, no road-load change) it returns 24.62 L/100 km, i.e. -12.32% and -23.11% against the two anchor members respectively.

**The assignment ordered a calibration and did not get one. Stated as a non-satisfaction, not as a treatment choice.** The order reads *"Calibrate to a public NPR fuel-economy reference and state it"*. I obtained the reference and moved no ruler parameter to close the residual, because the anchor is an in-use aggregate over an unknown duty, load, body and driver mix and cannot resolve a cycle-specific level. That is a defensible modelling position and it is *not* compliance with the order.

The residual is in the ruler's favour on every setting. For V1's ADVANCE that is the safe direction and the margin is a lower bound. **For V2's KILL it is the unsafe direction, and the residual is the wrong statistic** — what the lead needs is the flip point, which §7.1 now carries as a first-class export. **ESC-1.**

### 1.3 Ruler brackets — every declared choice at its pessimistic end

> **This section is the round-2 correction of the report's central robustness claim.** Round 1 exported a row called *all ruler-favourable choices reversed* which reversed five choices, left the four largest ones — gear mesh, AT pump, final drive, lock-up slip — at their ruler-favourable values, and folded in a CdA change that is not a ruler-modelling choice at all. `ws11_params.py` declares all four of those levers ruler-favourable and states where the true value lies, and none of them entered the bracket set (adjudication r1/B1). All eight ruler-modelling levers are bracketed now, singly and together, and the road-load change is separated out.

8-seed median L/100 km, and the effect on each candidate's nominal per-payload margin (`data/ruler_brackets.csv`, `data/bracket_margins.csv`). **`kind` matters**: a *modelling* row changes only how the RULER is described and always raises the candidate's margin; the *road* row changes the road both vehicles drive and lowers it on both.

| ruler setting | kind | VOLT-SUB L/100 km | VOLT-REG L/100 km | V1 margin min % | V2 margin min % |
|---|---|---|---|---|---|
| **headline (ruler-favourable)** | headline | 19.18 | 19.03 | +20.11 | -7.93 |
| gear mesh −2 points (0.940…0.965) | modelling | 19.43 | 19.35 | +21.14 | -6.07 |
| AT pump 2.0 kW @ 1,800 rpm | modelling | 19.45 | 19.24 | +21.22 | -6.78 |
| final drive 0.94 | modelling | 19.43 | 19.36 | +21.15 | -6.06 |
| lock-up slip debit 2.0% | modelling | 19.36 | 19.26 | +20.86 | -6.58 |
| belt/alternator accessory model | modelling | 19.83 | 19.21 | +22.76 | -6.91 |
| converter stalled in Drive at idle | modelling | 22.50 | 19.21 | +31.93 | -6.96 |
| single-step shift schedule | modelling | 19.19 | 19.03 | +20.16 | -7.91 |
| engine/flywheel/converter inertia charged | modelling | 19.51 | 19.07 | +21.50 | -7.72 |
| *the four driveline levers together* | modelling | 20.14 | 20.14 | +23.96 | -1.86 |
| *those four + accessories + idle-in-Drive* | modelling | 24.26 | 20.50 | +36.87 | -0.07 |
| **ALL EIGHT ruler-modelling choices, no road change** | **modelling** | 24.62 | 20.54 | +37.78 | +0.13 |
| CdA 5.4 m² (E13 case, applied to both vehicles) | **road** | 19.90 | 21.92 | +18.06 | -10.52 |
| all eight + the CdA road change | modelling+road | 25.38 | 23.72 | +35.77 | -2.15 |
| *round 1's row, renamed: partial reversal + CdA* | SUPERSEDED | 24.20 | 22.31 | +32.62 | -8.57 |

V2 on VOLT-SUB is run against the same bracket set and is in `data/bracket_margins.csv`; at the pessimistic end it goes from +21.71% to +39.06%.

**What this does to the two verdicts.**

**V1's ADVANCE is confirmed by it.** Every ruler-modelling reversal moves V1 further from the bar: at the pessimistic end V1's nominal margin goes from +20.11% to +37.78%. The lower-bound framing is real and it works in V1's favour.

**V2's KILL does not survive it, and round 1 said it did.** Round 1's sentence was: *"The most V2-favourable single bracket in the table is the belt/alternator accessory model, and it leaves V2 at −6.91% … V2's KILL does not turn on how the ruler was modelled."* That sentence argued robustness from **single** levers while four larger levers were missing from the table entirely. With all eight ruler-modelling choices at the pessimistic end each one's own declaration names — every one of them inside the plausible range, merely at the other end of it — V2's nominal per-payload margin is **+0.13% ensemble-min / +0.59% median** — a shift of 7.84 pp that carries it across zero — **a draw, not a 7.9-point kill**. It is still not an ADVANCE: it does not reach the 3% bar. But the difference between "loses by eight points" and "is level" is the difference between a decision and a coin toss.

So the honest statement, replacing round 1's, is:

> **V2's KILL as computed is a KILL. V2's KILL as bounded by this workstream's own declared parameter ranges is a draw.** The KILL survives the ruler *as modelled at its most favourable settings*. It does not survive the ruler *as bounded by the ranges the same file declares*. The lead should execute or spare on that record, not on round 1's.

The single-lever rows are in the table so any one lever the lead disputes can be discounted individually, and the four-driveline-lever and six-lever intermediate combinations are exported for the same reason: the six-lever row is the exact combination the adjudication named, and it lands at -0.07% min / +0.40% median, reproducing that finding against this workstream's own artefacts. No claim in this paragraph is asserted rather than run.

(The CdA 5.4 row moves V2 the other way, to -10.52%, because a bigger frontal area is a change to the ROAD that both vehicles drive, not a ruler modelling choice, and the aero work it adds is served through the series chain's lower efficiency. Round 1's prose said this correctly and its JSON note said the opposite; the note is corrected and `verify_ws11.py` now checks the direction of every bracket row against its declared `kind` rather than trusting prose — adjudication r1/M4.)

## 2. Mass ledgers, to the kilogram

Fixed GVW **6,600 kg**; payload = GVW − curb. Full ledger with per-item sources in `data/mass_ledger.csv`.

### 2.1 The ruler

| item | kg | source |
|---|---|---|
| chassis-cab curb, 150 in WB | 2985 | [SOURCED] GVWR 14,500 lb minus body/payload allowance interpolated to the 150 in wheelbase (7,920 lb) |
| 16 ft dry-freight body + subframe + rear door | 545 | [WS11-DECLARED] reconciliation item to WS1's ratified operating curb |
| driver + kit | 90 | [WS11-DECLARED] |
| fuel to full (30 gal tank), increment over chassis tare | 75 | [WS11-DECLARED] |
| DEF, tools, spare | 5 | [WS11-DECLARED] |
| **operating curb** | **3700** | equals WS1's ratified `m_curb_operating` |
| **payload at GVW** | **2900** | equals WS1's ratified `payload_at_gvw_kg` |

The chassis-cab figure is derived from the manufacturer's own body/payload allowance (7,545–8,511 lb across four wheelbases) interpolated to the 150 in wheelbase that carries a 16 ft body: 7920 lb allowance, 2984.70 kg chassis-cab curb. **The 16 ft body mass is the single reconciliation item** to WS1's ratified 3,700 kg, and it is declared as such rather than hidden.

**Two honesty corrections to that line (adjudication r1/m9, r1/m10).**

1. The `[SOURCED]` tag oversells it. The spec sheet publishes a *range* across four wheelbases without saying which end belongs to which; WS11 assumes the allowance falls linearly with wheelbase — physically right, but an interpolation. The line is retagged **[SOURCED-RANGE, INTERPOLATED IN WHEELBASE]**. The 545 kg body is then a residual by construction, closing to a WS1 figure that is itself marked `[WS1-ASSUMPTION]`.
2. A second sourced tare was sitting unused in `sources/`: the Isuzu South Africa NPR 400 sheet, which publishes a chassis-cab tare of **2620 kg** at a 3815 mm wheelbase — essentially the same 150 in. Round 1 left it unpinned, unreferenced and unmentioned. It is pinned now, and it is a different truck: 7,500 kg GVM, Euro 2 with no DPF/SCR/DEF, a manual gearbox in place of the automatic and converter, and only 15 L of fuel in tare. **It moves nothing in this report**: the ruler's ledger is built to WS1's ratified 3,700 kg operating curb with the body as the single reconciliation item, so a different chassis-cab figure moves the chassis/body *split* and leaves every mass, payload and margin unchanged.

What *would* move margins is the operating curb TOTAL, because it moves both payload denominators at fixed GVW. At ±100 kg of ruler operating curb (both vehicles keep the same body, so both payloads move together) V2's nominal margin moves by -0.69 pp and V1's by -0.20 pp.

### 2.2 The candidates

| | ruler | V1 Postal | V2 Trucker |
|---|---|---|---|
| curb, kg | 3700 | 3888 | 4139 |
| **payload at GVW, kg** | **2900** | **2712** | **2461** |
| freight lost vs ruler, kg | — | 188 | 439 |
| payload ratio ruler/candidate | 1.000000 | 1.069322 | 1.178383 |
| **per-km advantage needed merely to DRAW, %** | — | **6.48** | **15.14** |

Deleted by both candidates: Aisin A465id 6-speed AT + torque converter + fluid (227 kg), transmission oil cooler + lines (5 kg), alternator, 140 A (10 kg), starter motor + solenoid (8 kg). V1 additionally deletes the 4HK1-TC engine (500 kg) and fits the V3307-V1C genset package (386 kg).

Added by both: WS2's spine rollup 230.8 kg, WS3's pack 280.52 kg, 35 kg of added cooling and a 6 kg DC-DC converter. V2 additionally carries GEN-V2 (90 kg), its rectifier (12 kg) and mounts (35 kg) **on top of the engine it keeps** — which is the whole story of its ledger.

WS4's `aftertreatment_extra: 60 kg` is EXCLUDED from the headline (the reading favourable to V2) and carried as a bracket: V2 curb 4199 kg, payload 2401 kg, break-even bar 17.21%. On VOLT-REG the bracket moves V2's nominal margin from -7.93% to -10.62%, i.e. -2.70 pp — **not** the 2.44% that 60 kg is of V2's payload, which is what round 1's ESC-3 asserted (adjudication r1/m2): the payload enters as a ratio against the ruler's payload, not as a fraction of itself. **ESC-3.**

### 2.3 Break-even curb mass

At fixed GVW a candidate's curb does not change its energy, only its denominator, so the curb at which each candidate exactly draws is exact, not a search:

| | actual curb, kg | break-even curb, kg (worst seed) | headroom, kg |
|---|---|---|---|
| V1 on VOLT-SUB | 3888 | 4433 | +545 |
| V2 on VOLT-REG | 4139 | 3944 | -195 |

V1 could gain another 545 kg before it stopped beating the ruler — more than its whole pack again. V2 is over its break-even curb by 195 kg, which it has nowhere to find: deleting the entire 280.5 kg pack would also delete the architecture.

> **This is a flip point on the axis that SUPPORTS the KILL.** Round 1 exported it and exported no flip point on the axis that threatens the KILL — the ruler's own fuel level. That asymmetry is corrected in **§7.1**, which carries the exact analogue of this table for ruler fuel (adjudication r1/B3).

## 3. Headline results

Metric of record: **fuel energy per PAYLOAD tonne-km**, computed as a **paired per-seed statistic** (R36/D13) — the margin is formed seed by seed and *then* enveloped, never as a ratio of medians. Per-km is given beside it on the same paired basis. Ensemble = 8 seeds (VOLT-REG 23,3,4,5,6,7,8,9; VOLT-SUB 11,3,4,5,6,7,8,9 — WS1/WS4's own sets). Full per-seed values in `data/per_seed_margins.csv`.

### 3.1 V1 Postal on VOLT-SUB — its design duty

| case | ruler kWh/km | cand kWh/km | **per-km margin, paired** min / med / max % | **per-payload-t-km margin, paired** min / med / max % |
|---|---|---|---|---|
| nominal | 1.8969 | 1.4051 | +25.29 / +25.96 / +26.24 | **+20.11** / +20.83 / +21.13 |
| payload_p20 | 1.9775 | 1.5132 | +22.84 / +23.34 / +23.91 | **+22.84** / +23.34 / +23.91 |
| payload_m20 | 1.8165 | 1.3528 | +24.66 / +25.44 / +25.61 | **+24.66** / +25.44 / +25.61 |
| cold_-10C | 1.9266 | 1.4467 | +24.37 / +25.01 / +25.25 | **+19.12** / +19.81 / +20.07 |
| alt2000m_45C | 1.8282 | 1.3161 | +27.31 / +28.02 / +28.12 | **+22.27** / +23.03 / +23.14 |

Ruler 19.18 L/100 km vs V1 14.20 L/100 km at nominal (8-seed medians).

### 3.2 V2 Trucker on VOLT-REG — its design duty

| case | ruler kWh/km | cand kWh/km | **per-km margin, paired** min / med / max % | **per-payload-t-km margin, paired** min / med / max % |
|---|---|---|---|---|
| nominal | 1.8827 | 1.7154 | +8.41 / +8.96 / +9.25 | **-7.93** / -7.27 / -6.93 |
| payload_p20 | 1.9307 | 1.8076 | +6.27 / +6.38 / +6.55 | **+6.27** / +6.38 / +6.55 |
| payload_m20 | 1.8364 | 1.7014 | +7.21 / +7.27 / +7.58 | **+7.21** / +7.27 / +7.58 |
| cold_-10C | 1.9976 | 1.8413 | +7.69 / +7.86 / +8.21 | **-8.77** / -8.58 / -8.17 |
| alt2000m_45C | 1.6202 | 1.4218 | +12.15 / +12.24 / +12.42 | **-3.52** / -3.42 / -3.20 |
| climb_10km_6pct | 2.1117 | 1.9639 | +6.67 / +7.04 / +7.27 | **-9.98** / -9.55 / -9.27 |

Ruler 19.03 L/100 km vs V2 17.34 L/100 km at nominal. **V2 wins on fuel and loses on freight.**

### 3.3 V2 Trucker on VOLT-SUB — reported alongside, not its duty

| case | ruler kWh/km | cand kWh/km | **per-km margin, paired** min / med / max % | **per-payload-t-km margin, paired** min / med / max % |
|---|---|---|---|---|
| nominal | 1.8969 | 1.2544 | +33.56 / +33.87 / +34.05 | **+21.71** / +22.07 / +22.29 |
| payload_p20 | 1.9775 | 1.3740 | +30.00 / +30.56 / +30.92 | **+30.00** / +30.56 / +30.92 |
| payload_m20 | 1.8165 | 1.2385 | +31.51 / +31.81 / +31.99 | **+31.51** / +31.81 / +31.99 |
| cold_-10C | 1.9266 | 1.2883 | +32.81 / +33.14 / +33.37 | **+20.82** / +21.21 / +21.48 |
| alt2000m_45C | 1.8282 | 1.1770 | +35.31 / +35.55 / +35.79 | **+23.77** / +24.05 / +24.33 |

The same vehicle, the same ruler, the same code: +21.71% on the suburban duty against -7.93% on the regional one. **D15 is not a slogan.**

## 4. One-factor decomposition

Each row is a real re-run, not an algebraic split, at nominal on the candidate's design duty (`data/one_factor.csv`).

> **Every row is now a PAIRED per-seed statistic.** Round 1 formed each `worth_pp` as *min-of-base minus min-of-counterfactual*, with the two minima governed by different seeds — R36's defect class in miniature (adjudication r1/M6a). The difference is formed seed by seed and only then enveloped. The unpaired figure and the size of the artefact are kept on every row in the JSON so round 1's numbers are not dropped; the artefact ran to 2.3 pp on the worst row.

| factor | V1 on VOLT-SUB, paired min (median) | V2 on VOLT-REG, paired min (median) | round-1 unpaired V1 / V2 |
|---|---|---|---|
| **mass penalty alone** (the freight given back) | 5.11 pp (5.13) | 16.19 pp (16.24) | 5.18 / 16.34 |
| **regen alone** (worth, vs regen cap = 0) | 23.59 pp (23.81) | 4.32 pp (4.90) | 24.02 / 4.38 |
| **engine-off alone**, vs a load-following genset that never stops (mode b′, carries WS4's 25 kW floor) | 72.58 pp (74.39) | 0.25 pp (0.90) | 74.88 / 0.31 |
| **engine-off alone**, vs a genset held ON at the pinned point | 101.80 pp (102.64) | 63.42 pp (64.68) | 103.84 / 65.75 |
| **engine operating point alone** (ruler re-scored at the candidate's pinned island BSFC) | 11.15 pp (11.36) | 12.34 pp (12.49) | 11.41 / 12.59 |

Supporting numbers: the ruler's duty-mean effective BSFC is 261.35 g/kWh on VOLT-SUB and 227.43 g/kWh on VOLT-REG, against pinned island points of 228.72 g/kWh (V1) and 203.62 g/kWh (V2).

**The engine-operating-point row absorbs idle; it does not leave it outside.** Round 1's exported description said *"what survives is everything that is not the operating point — driveline, regen, **idle** and the payload denominator"*. That is wrong (adjudication r1/M6b). The counterfactual re-prices the ruler's WHOLE shaft energy at the candidate's island, and the ruler's shaft energy includes the work it does at idle — which on VOLT-SUB is 13.70% of its fuel, burned at roughly 500 g/kWh at 700 rpm. So this row conflates the operating point with idle and is read as an **upper bound** on the operating-point term alone.

**These rows are independent counterfactuals and they do not sum.** Each is the full model re-run with one thing changed; there is no algebraic decomposition here and none is claimed. The term that has no row is the series path's own conversion penalty — engine → generator → bus → inverter → motor → 10:1, against the ruler's geared path — which is what the four positive rows are spending their winnings on.

**Reading.** On VOLT-SUB the series architecture wins on three independent mechanisms — regen on a 30-stop cycle, engine-off across a 44.64%-idle duty, and an engine that never leaves its island — and the freight give-back is small because V1 deletes a 500 kg engine as well as a gearbox.

On VOLT-REG regen is nearly worthless (braking is 5.84% of tractive energy), the operating-point win survives, and the freight give-back is almost twice the entire per-km gain. **The single term that kills V2 is the one D13 named.**

The two engine-off rows deserve a sentence of their own, because they disagree and the disagreement is informative. Against a genset that can follow load, engine-off is worth 0.25 pp on VOLT-REG — nothing. Against a genset stuck at its pinned point it is worth 63.42 pp — everything. **That gap is a dispatch result, not an architectural one**, and it is precisely R22b's open question, which BASELINE_v3 assigns to WS5. WS11 measures both ends and claims neither.

**One caveat on the engine-off row that round 1 dismissed on the wrong grounds.** V1's ADVANCE rests mainly on this mechanism (72.58 pp), and no cold-engine friction or warm-up model exists on either vehicle. Round 1 called that omission *"roughly neutral"* on the ground that the ruler and V2 share an engine. That addresses the initial cold start, not the asymmetry that matters. On VOLT-SUB V1's genset runs only 0.335 of the time, in about 2 blocks per cycle — off-blocks averaging roughly 19 minutes — while the ruler's engine runs continuously and stays hot. See **§10.1** and **ESC-8**, where the classification is corrected and an owner is requested.

## 5. Corners

Corner set: payload ±20% of the ruler's payload; −10 C with WS3's cold acceptance actually applied; 2,000 m / +45 C on the R6 derate basis; and WS1 §4.4's 10 km / 6% climb spliced into VOLT-REG. Definitions in `results_ws11.json → case_definitions`.

| corner | V1 on VOLT-SUB | V2 on VOLT-REG |
|---|---|---|
| payload +20% (3,480 kg freight) | +22.84% | +6.27% |
| payload −20% (2,320 kg freight) | +24.66% | +7.21% |
| −10 C, WS3 cold acceptance applied | +19.12% | -8.77% |
| 2,000 m / +45 C, R6 derate | +22.27% | -3.52% |
| 10 km / 6% climb inserted into VOLT-REG | n/a (R5: VOLT-REG is not a V1 cycle) | -9.98% |

**The −10 C corner uses the actual curve, not an assumption.** Pack charge acceptance at −10 C cells is read from WS3's `regen_acceptance.csv` column `V2pack_chg_cont_kW_bus`; air density is recomputed for the corner. No cold-engine friction or warm-up model is applied to *either* vehicle. Round 1 classified that omission as roughly neutral; it is not, and it is largest at exactly this corner, which is V1's governing one — see **§10.1** and **ESC-8**.

**Two payload corners, two readings.** Read literally — and the gate uses the literal reading — both vehicles carry the *same* freight at those corners, so the payload denominators cancel and the per-payload metric becomes the per-km metric. That is why V2 scores +6.27% at +20% while scoring -7.93% at nominal on the same metric. Under the variant reading (each vehicle scales its own payload) V2 returns -7.73% and -7.57%, and V1 returns +19.44% and +20.51%. **Neither verdict changes under either reading.** **ESC-7.**

**Which reading is the novel one — round 1 did not say.** The VARIANT reading is the program's established convention, not the ordered one: `WS8_semi_architecture/ws8_candidates.py` defines `payload_kg()` as each vehicle's own payload times the corner factor, and WS9 inherited that under the R28/ESC-3 corner set this assignment mirrors. The literal reading gated on here is therefore a **departure from the convention the program has been running** (adjudication r1/M7). Note too that `interface_ws11.verdicts.V2_on_VOLT-REG.corner_margins_pct_min` exports the two payload corners as positive numbers, which read on their face as V2 winning there; they are the per-km margin under another name, because the denominators cancel.

**Cab-heat bracket at −10 C (R30's Vehicle One member, not ordered here).** Charging the candidate 3.81 kW of aux (3.0 kW of cab heat during the engine-off windows only; the ruler and the running genset both give it away free) moves V1's cold corner from +19.12% to +4.72% and V2's from -8.77% to -11.58%. **V1's ADVANCE survives it; V2's KILL deepens.** **ESC-2.**

The adder is applied as a cycle-average `2.0 + 3.0 × (1 − engine-on fraction)`, **iterated to a fixed point** in the engine-on fraction. It is energy-correct and timing-approximate: WS4's simulator takes a scalar aux load and WS4 is read-only, so a genuinely time-switched cab load is not available to WS11. Round 1 described it as if it were time-resolved and did not iterate (adjudication r1/m11).

**The fixed point moves V1's number, and it moves it in the direction that flatters the candidate, so all three readings are on the record.** V1 is the start-stop vehicle: the added electric load makes its genset run *more*, which shrinks the engine-off window the load is charged over. V2's genset runs essentially continuously, so its number does not move at all.

| V1, cold −10 °C with the R30 cab-heat member | ensemble-min |
|---|---|
| round 1's single-pass smear (the number round 1 reported) | +2.64% |
| fixed-point smear (this round) | +4.72% |
| **no waste-heat credit at all** (3.0 kW across the whole cycle) — the harshest defensible reading | **-5.42%** |

**That bottom row matters and it must not be buried: under the harshest cab-heat reading V1's governing corner goes NEGATIVE**, which is a fail against the ≥0% corner bar. The reading is not ordered — the assignment orders no cab-heat member at all, and both candidates carry a running diesel whose coolant genuinely is free while it runs, so charging the full 3.0 kW electrically for the whole cycle is deliberately pessimistic. But the span from -5.42% to +4.72% is the honest width of a member that is not modelled at the right time resolution, on the corner V1's ADVANCE is gated on. **ESC-2** is the ruling that closes it.

The same three readings on V2 are -11.58% / -11.58% / -15.62% — every one of them deepens its KILL.

### 5.1 The cold corner with BOTH pending items applied

`cold_-10C` **is** V1's governing corner, and two live rulings this workstream itself escalates both move it: ESC-2 (does R30's cab-heat member extend to Vehicle Zero?) and ESC-4 (CdA 4.2 or 5.4?). Round 1 reported them only separately and never ran the combination — which is the case the lead actually faces if both rulings land the way the escalations anticipate (adjudication r1/M1).

| V1, cold −10 °C | ensemble-min | median |
|---|---|---|
| as ordered — **the gated number** | **+19.12%** | +19.81% |
| + R30 cab-heat member (ESC-2), round 1's single-pass smear | +2.64% | +3.53% |
| + R30 cab-heat member (ESC-2), fixed point | +4.72% | +5.01% |
| + R30 cab-heat member with NO waste-heat credit | -5.42% | -4.61% |
| + CdA 5.4 (ESC-4 / E13) instead | +16.56% | +17.15% |
| **+ both** | **+3.66%** | +4.05% |

**V1's ADVANCE is real, and it is conditional.** With both pending items applied on the fixed-point cab-heat treatment it still clears the ≥0% corner bar, by a few points rather than the double digits the ordered corner shows. The adjudication reproduced round 1's single-pass smear and put the combination at about +1%; the fixed-point correction (r1/m11) moves it up, and the no-waste-heat-credit reading moves it below zero. All three are in the table above so the lead can see the width rather than a single number. The same combination on V2 gives -13.65%, which deepens its KILL. Both figures are exported from the interface block under `cold_corner_pending_items`, each carrying its ruling IDs.

## 6. Trip time (R38) and sustained capability

R38 is a **gate, not a term**: the metric of record stays energy per payload tonne-km and the lead applies the ≤ +5% test from this table. Trip time comes from a separate capability-limited forward pass (the fuel convention follows the demanded trace and by construction cannot see time).

> **These three rows are re-exported in round 2 because round 1's were produced by a model that did not do what its own docstring said.** The capability limit was consulted only while the vehicle was *accelerating*; once it was tracking the demanded speed it held that speed however negative the available acceleration had become. On the inserted 6% climb the ruler simply held the demanded 94.95 km/h throughout, and the "settled" climb speeds round 1 exported contradicted the closed-form sustainable speeds — 82.01 and 74.63 km/h — in the same results file. (The adjudication measured round 1's defect precisely: `a_cap < 0` on 3,752 of 3,791 inserted samples, a 983 N force deficit, and exported settled speeds of 88.4 / 94.3 km/h. Those four figures are the adjudication's measurements of round-1 code and are quoted, not re-derived here.) `a = min(a_des, a_cap)` is applied on every sample now (adjudication r1/B2). **The gate outcome does not change — PASS on all three rows either way — but the numbers do.**

| run | ruler trip time, s (median) | candidate, s (median) | ratio cand/ruler, worst | vs ruler | ≤ +5%? |
|---|---|---|---|---|---|
| V1 / VOLT-SUB nominal | 3490.80 | 3490.80 | 1.00000 | +0.000% | PASS |
| V2 / VOLT-REG nominal | 6582.39 | 6577.05 | 0.99934 | -0.066% | PASS |
| V2 / VOLT-REG + 10 km 6% climb | 7029.65 | 7026.81 | 0.99985 | -0.015% | PASS |

**Settled speed on the inserted sustained 6% climb**, from the same pass, now reconciling with the closed-form capability numbers below:

| | forward pass | closed form | difference |
|---|---|---|---|
| ruler | 82.01 km/h | 82.01 km/h | 0.000 km/h |
| V2 | 74.93 km/h | 74.63 km/h | 0.302 km/h |

`verify_ws11.py` asserts this agreement to 1.0 km/h on any corner carrying a sustained 6% grade, and asserts that the field is exported **only** on such corners — round 1 reported an identical "settled climb speed" on the nominal cases, which carry no sustained climb at all.

**What the trip-time gate does not catch.** Sustained speed on a 6% grade at GVW, with **no** buffer contribution — the only power available for an indefinite climb:

- ruler: **82.01 km/h**
- V2: **74.63 km/h** (genset 126.91 kW bus continuous)
- V1: **31.76 km/h** — against WS1 §4.4's independently-derived 30.2 km/h for the 50 kW class, reproduced here from a completely different code path

**A sentence of round 1's §6 has to be withdrawn.** It said *"V2 passes the 10 km climb because its buffer lasts almost exactly 10 km"*. The trip-time pass never exercised that mechanism, because it never asked V2 to hold a speed it could not hold. With capability enforced, what the pass actually shows is that **both** vehicles run off their capability curves through the insert: the ruler settles at 82.01 km/h and V2 at 74.93 km/h, and V2's trip time comes out marginally the shorter of the two — the two are within -0.02% of each other and the gate is not close either way. On the fuel side V2's buffer does not last the climb at all — the pack reaches SOC 0.000 with 1.720 kWh of unserved bus energy (§6.2). Extend the climb and the sign of the capability comparison flips. **ESC-5.**

### 6.1 The severity of the climb corner is a WS11 choice

Splicing at 30% of route distance fixes the demanded climb speed at 94.95 km/h. WS1 §4.4 — the case the assignment names — poses the same climb at 85.0 km/h and states plainly that holding it is not achievable on any buffer this study contemplates. **WS11's corner is therefore materially harder than its own reference**, which is why both vehicles run off their capability curves in it. Round 1 declared the splice and did not bracket it (adjudication r1/m12). At WS1's own 85 km/h posing V2's climb-corner margin is -10.09% against -9.98% as gated. The harder reading is retained for the gate; the softer, WS1-faithful one is on the record beside it.

### 6.2 Capability and limit counters — what the runs actually did

> WS4's simulator computes a full set of capability and limit counters on every run. **Round 1 exported none of them** — a grep of `results_ws11.json` returned zero occurrences of `unserved`, `soc_min`, `emerg_s`, `eng_over_cont`, `starts` or `infeasible` (adjudication r1/M3). They are exported per case now, in `data/limit_counters.csv` and `results_ws11.json → capability_and_limit_counters`.

Three of them bear on the V2 numbers of record:

1. **V2 operates above its R18-ratified 132 kW continuous flat-rating in 6 of 6 exported cases, including the nominal case that produces the headline number** — 146.5 s and 0.624 kWh at nominal, on the full 8-seed envelope R9 requires. (The adjudication reported 4 of 6 cases over two seeds; this is the same effect measured over all eight, which finds it in every case.) The emergency band's ceiling is the *automotive* full-load curve (148.7 kW), which is WS4's own KX-M1 issue. WS4 ships an `emerg_cap_cont_rating` bracket for exactly this and round 1 never exercised it; it is exercised in §6.3.
2. **On the governing climb corner V2's pack reaches SOC 0.000 with 1.720 kWh of unserved bus energy.** The buffer is exhausted and the emergency band carries the remainder.
3. **The ruler is capability-infeasible on every VOLT-REG case** — up to 555.6 s, with 3.258 kWh of unserved wheel energy charged to fuel at its own cycle-mean BSFC.

**The direction of all three is TOWARD the candidate** — they make the ruler thirstier and let V2 deliver more energy at a good BSFC — so **none of them changes the KILL**. They are disclosed because they were not, and because they mean the exported V2 numbers are **not achievable inside V2's own ratified rating**. **ESC-9.**

### 6.3 The emergency band capped at the ratified continuous rating

WS4's `emerg_cap_cont_rating` bracket, run across every case. With the emergency band's ceiling set to the genset's continuous rating × derate instead of the automotive full-load curve, no case gains any unserved energy and the margin moves in V2's favour by a fraction of a point.

| V2 on VOLT-REG | as ordered | emergency band capped | **paired** shift min / median / max, pp | unpaired min-to-min, pp |
|---|---|---|---|---|
| nominal | -7.93% | -7.74% | 0.000 / 0.028 / 0.183 | 0.183 |
| 10 km 6% climb | -9.98% | -9.26% | 0.580 / 0.604 / 0.724 | 0.724 |

**The nominal row's paired minimum is exactly zero, and that is informative rather than a rounding artefact**: on some seeds V2 never enters the emergency band at all, so capping it changes nothing whatever. The unpaired min-to-min figure of 0.183 pp overstates the effect by comparing two minima governed by different seeds — which is precisely the construction M6 named, caught here by this round's own sweep. Full table in `results_ws11.json → declared_choice_brackets.emergency_band_at_continuous_rating_bracket`. **Neither verdict moves, and the ordered run remains the run of record** — WS11 does not choose between WS4's two readings of its own emergency band; ESC-9 puts that to the lead.

## 7. ADVANCE / KILL against the pre-committed criterion

**Criterion (pre-committed, same form as Vehicle One's R25/R37):** ADVANCE only if >= 3% better than the ruler on the candidate's design duty at nominal, ensemble-min, AND >= 0% at every corner. Metric: fuel energy per payload tonne-km, paired per-seed.

### V1 Postal on VOLT-SUB — **ADVANCE**

- nominal, ensemble-min: **+20.11%** (governing: seed 4 of the enumerated 8-seed VOLT-SUB ensemble); median +20.83%, max +21.13%. Against the 3% bar: **+17.11 pp** — PASS.
- worst corner: **+19.12%**, governing case *cold_-10C (min over the enumerated corner set ['alt2000m_45C', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 4 of the enumerated 8-seed VOLT-SUB ensemble*. Against the 0% bar: **+19.12 pp** — PASS.
- R38 trip-time gate: PASS (+0.000% worst).

### V2 Trucker on VOLT-REG — **KILL**

- nominal, ensemble-min: **-7.93%** (governing: seed 5 of the enumerated 8-seed VOLT-REG ensemble); median -7.27%, max -6.93%. Against the 3% bar: **-10.93 pp** — FAIL.
- worst corner: **-9.98%**, governing case *climb_10km_6pct (min over the enumerated corner set ['alt2000m_45C', 'climb_10km_6pct', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 5 of the enumerated 8-seed VOLT-REG+CLIMB ensemble*. Against the 0% bar: **-9.98 pp** — FAIL.
- R38 trip-time gate: PASS (-0.066% worst).

**Neither verdict moved in round 2.** Both are computed at the headline settings, which are unchanged; every round-1 headline number reproduces. What moved is what the report is entitled to claim about them, and that is §7.1 and §7.2.

### 7.1 Ruler-fuel flip points — the axis that threatens the verdicts

§2.3 exports the flip point on the MASS axis, which supports the KILL (V2 is 195 kg over its break-even curb). Round 1 exported no flip point on the axis that **threatens** it — the ruler's own fuel level — while the ruler sits -31.69% to -40.10% below its own mandatory anchor and was never calibrated to it (adjudication r1/B3). The analogue is computed now, on the paired per-seed statistic with the governing seed labelled, exactly as `break_even_curb_kg` is.

Exact algebra, not a search: with the candidate held fixed and the ruler's per-km fuel scaled by *k*, `margin(k) = 100 × (1 − c/(k·r))`.

| | multiplier to DRAW (0%) | ruler fuel error | multiplier to the 3% bar | ruler fuel error |
|---|---|---|---|---|
| V1 on VOLT-SUB (ADVANCE) | 0.7989 | -20.11% | 0.8236 | -17.64% |
| V2 on VOLT-REG (KILL) | 1.0693 | +6.93% | 1.1024 | +10.24% |

**Read plainly: V2's KILL requires only that the real NPR-HD not be more than +6.93% thirstier than this ruler models it.** The anchor says the real fleet is 46% thirstier (all model years) or 67% thirstier (the era-correct 4HK1 subset). §1.3 shows that the eight ruler-modelling levers this workstream itself declares are, on their own, enough to close that +6.93%. V1's ADVANCE runs the other way: the ruler would have to be about 18% **leaner** than modelled before V1 fell to the 3% bar, and nothing in the evidence points that way.

Per-corner flip points, and the implied ruler L/100 km at each, are in `data/ruler_fuel_flip_points.csv`. Both flip points are first-class R14 fields in `interface_ws11.ruler_fuel_flip_points`, each with its governing seed.

### 7.2 What each verdict is conditional on

| verdict | survives | conditional on |
|---|---|---|
| **V1 ADVANCE** | every ruler-modelling bracket (it goes to +37.78% at the pessimistic end); the CdA road change; the payload-corner reading; the engine-curve reconstructions | **ESC-2 + ESC-4 together**: its governing corner falls to +3.66% (§5.1), and under the harshest defensible cab-heat reading — no waste-heat credit at all — that same corner goes NEGATIVE at -5.42%, which would fail the ≥0% corner bar. **ESC-8**: the mechanism carrying 72.58 pp of its margin has an unmodelled thermal asymmetry |
| **V2 KILL** | the mass axis by 195 kg; every corner; the CdA road change; the cab-heat member; the emergency-band bracket; the aftertreatment reading | **the ruler being modelled at its most favourable settings.** At the declared pessimistic end it is a draw (§1.3), and it flips on a +6.93% ruler-fuel error against an uncalibrated ruler (§7.1) |

The lead executes or spares. WS11 reports the numbers, and reports which of them the decision actually turns on.

## 8. Machine-readable interface (R14)

Authoritative copy: `results_ws11.json → interface_ws11`. Every worst-case field below is an explicit max/min over an enumerated case set with the governing case labelled inline.

The block is machine-readable and lives in the JSON; inlining it here would create exactly the hand-transcription risk R14 exists to prevent. Key fields:

| field | value |
|---|---|
| `verdicts.V1_on_VOLT-SUB.verdict` | ADVANCE |
| `verdicts.V1_on_VOLT-SUB.nominal_margin_pct_min` | 20.114012 |
| `verdicts.V1_on_VOLT-SUB.worst_corner_margin_pct` | 19.124037 |
| `verdicts.V2_on_VOLT-REG.verdict` | KILL |
| `verdicts.V2_on_VOLT-REG.nominal_margin_pct_min` | -7.925180 |
| `verdicts.V2_on_VOLT-REG.worst_corner_margin_pct` | -9.978769 |
| `masses.payload_at_gvw_kg.ruler` | 2900 |
| `masses.payload_at_gvw_kg.V1` | 2712 |
| `masses.payload_at_gvw_kg.V2` | 2461 |
| `sustained_6pct_capability_kmh.worst_case_value` | 31.76 (V1) |
| `ws4_hot_swap_seam.max_abs_difference` | 0.0e+00 |
| `verdict_robustness.V2_on_VOLT-REG.pessimistic_min` | 0.132394 |
| `ruler_fuel_flip_points.V2_on_VOLT-REG.pct_ruler_fuel_error_to_draw` | 6.933008 |
| `ruler_fuel_flip_points.V1_on_VOLT-SUB.pct_ruler_fuel_error_to_3pct_bar` | -17.643311 |
| `ruler.anchor.worst_residual_vs_model_pct` | -40.0986 (fourhk1_era (min over the enumerated two-member anchor set)) |
| `ruler.anchor.calibrate_order_satisfied` | False |
| `cold_corner_pending_items.V1_on_VOLT-SUB.with_cab_heat_and_CdA_5p4_pct` | 3.662211 |
| `capability_and_limit_worst_case.V2_on_VOLT-REG.candidate_worst_unserved_bus_kWh` | 1.7204 |
| `ruler_idle.fuel_l_per_h` | 1.202 |

**Pending rulings are now carried in the block (R14).** Round 1's interface contained the string `ESC` nowhere at all, while at least four exported fields were conditioned on live rulings (adjudication r1/M2). `interface_ws11.pending_rulings_r14` names each ruling, the fields it conditions and the block that prices it, and the alternative readings — the cab-heat corner, the combined corner, the bracket range, the limit counters, the flip points — are all reachable from the interface rather than only from the results file.

## 9. Input vintages and the hot-swap seam

| input | vintage |
|---|---|
| WS4 `interface_ws4.series_duty_v2` | `live_design_input`, cases alt2000m_45C, cda_5.4, nominal, seeds [23, 3, 4, 5, 6, 7, 8, 9], usable 11.083608 kWh |
| WS4 `interface_ws4.gate_g1` | `executed_kill_2026-08-30` — **ARCHIVED, not consumed**, no field of it used as a live requirement |
| WS4 `spin_drag_operational_note_r22d` | reported by WS4, charged to fuel by nobody; WS11 charges it to neither vehicle |
| WS2 traction chain | round 4, `data/effmap_motor_inverter_662V.csv` at 662 V, ratio 10.0 |
| WS3 pack | 11.083608 kWh usable, 280.52 kg, V1 hysteresis 3.00 kWh (R19) |
| WS1 cycles | reused verbatim at 10 Hz, WS4's own seed sets |

**The hot-swap seam is an assertion, not a promise, and it was exercised for real this round.** WS11 does not reimplement the series supervisor: it calls WS4's own `ws4_sim.run_g1_mode` in mode (b), and `run_ws11.py` asserts that the V2 nominal VOLT-REG ensemble reproduces WS4's exported `series_duty_v2[nominal]` `fuel_energy_kWh_per_km` min / median / max to 0.0e+00 — identical floats.

**WS4 KX round 3 landed while this rework was in progress.** The vintage of record for this report is the one pinned in `_meta.input_sha256["WS4/results_ws4.json"]`:

- `b02a6c82fbbe8d3e006fb1d756fbee51b2cb04f50e4281c65e04c97e63876d0b` — WS4 KX r3.
- `ws4_sim.py` is byte-identical across the change (`de25e3da1fd2bb1ae5c8be3b590bd7f51c7cbba3143306957e0965b87a191632`), as are `ws4_chain.py` and `ws4_models.py`.
- Zero values changed inside `series_duty_v2 → cases`, so the seam assertion above holds unchanged and **no number in this report moved because of it**. Only the file hash moved, and the pin recorded it — which is the pin doing exactly its job.

KX r3 also restated **ESC-10** on a wider measured set inside R6's own rating family, and that restatement bears on §6.2: the genset's exposure above its continuous flat-rating is a **union maximum of 287.1 s per cycle** (against 250.0 s over WS4's ordered case set alone), with peak shaft at 112.03% of **that case's own** rating. WS11 quotes those figures read-only from the pinned vintage and does not re-derive them; its own counters in §6.2 are measured on WS11's case set, which is a different set for a different purpose, and neither is offered as a substitute for the other. **ESC-9** is written on KX r3's framing.

9 of WS11's input pins are files WS4 also pins inside `series_duty_v2.input_sha256`. **Every one matches**, which is checked in `verify_ws11.py`: WS11 and WS4 did not merely name the same upstream artefacts, they consumed byte-identical files. (Round 1 typed that count into prose; it is derived from the run now — sweep.)

SHA-256 pins for all 21 consumed inputs (upstream artefacts and the retrieved public sources) are in `results_ws11.json → _meta.input_sha256`.

### 9.1 R34 traces

One 10 Hz trace per primary run configuration, at that duty's reference seed: ruler and candidate on each design duty at nominal, V2 on VOLT-SUB, and — added in round 2 — **both verdicts' governing corners**. Round 1 traced V2's governing corner (the climb) and not V1's (`cold_-10C`), which is the corner V1's ADVANCE is actually decided on (adjudication r1/m6). `verify_ws11.py` now asserts that each verdict's governing corner has a trace on disk, so this cannot silently regress. Column sets differ by vehicle (the ruler's carries gear, lock-up state, engine speed and torque; the candidates' carry bus, generator, battery and SOC), and every file is listed with its row count in `results_ws11.json → interface_ws11.traces_r34`. The remaining seeds and corners are exported as per-seed rows in `data/per_seed_margins.csv` rather than traced — WS4's own R34 precedent (one full-rate trace, summary exports for the rest), which keeps the committed artefact set to a size a reviewer can actually open.

## 10. First-principles sanity checks

| check | WS11 | reference |
|---|---|---|
| 85 km/h flat cruise, wheel power | 46.93 kW | WS1 baseline crosscheck 46.93 kW ("~2.0 kN, ~47 kW") |
| engine speed at 85 km/h in top gear | 1749 rpm | a real NPR-HD cruises there; the sourced 4.555 × 0.63 driveline reproduces it with no fitting |
| engine speed at 100 km/h in top gear | 2057 rpm | as above |
| V1 sustained speed on 6% at GVW | 31.76 km/h | WS1 §4.4's forward simulation: 30.2 km/h |
| ruler idle fuel at 700 rpm carrying 2.0 kW of accessories | 0.2778 g/s = 1.202 L/h | 13.70% of the ruler's VOLT-SUB fuel across 44.64% of the cycle time — the ruler's single most consequential number on a stop-start duty, and round 1 never stated it (r1/m5) |
| settled 6% climb speed, forward pass vs closed form | agree to 0.302 km/h (worst) | asserted in `verify_ws11.py` (r1/B2) |
| curb + payload = GVW | exact | by construction |
| per-km ↔ per-payload identity on every seed of every case | max residual 4.441e-16 | `1 − m_payload = (1 − m_km) × pay_ruler/pay_cand` |
| V2 nominal VOLT-REG vs WS4's live export | 0.0e+00 | identical floats |

### 10.1 Known omissions and the direction each one leans

| omission | who it flatters | size |
|---|---|---|
| WS2's brake-resistor blower (1.45 kW, WS2's figure) is not charged to the candidate bus during R15 blend overflow | candidate | the overflow column is small but **not** zero — round 1 said *near zero*, which is loose. Per-case values are in `data/heat_ledger_ws6.csv`, and the column is the lumped one discussed two rows below, so WS6 should size the blower against that file rather than against this sentence |
| WS3's 8 kW pack heater is not run at −10 C | candidate | none at this corner: R16 permits dispatch on the published derate curves down to −15 C *cell*, and the −10 C acceptance value is the one applied |
| **no cold-engine friction / warm-up model on either vehicle** | **the candidate, and specifically V1** | **not quantifiable here, and NOT "roughly neutral" — see below and ESC-8** |
| the ruler's standard exhaust brake is not modelled | neither | it is a retarder, and DFCO already puts the ruler's overrun fuel at zero |
| the ruler's engine/flywheel/converter rotating inertia is not charged in the headline | ruler | bracketed in §1.3 as a declared lever |
| R22d's true-coast PM spin member is charged to neither vehicle | candidate | WS4 measures it at ≤0.0004 pp of cycle fuel (WS4's figure, quoted) |
| the ruler's load fraction φ is referred to the UNDERATED full-load curve while WS4 refers the candidate's to the DERATED one, at the altitude corner only | ruler | measured: 0.098 pp on V2, -0.088 pp on V1. Immaterial, but it was undeclared in round 1 (r1/m8) |
| the R15 blend overflow column lumps the brake resistor with friction | neither | WS4's simulator does not export the split and WS4 is read-only; the column is an UPPER bound on resistor duty and `regen_shed_r16_kWh` a lower bound. WS6 must not read it as resistor duty (r1/m7) |

**The thermal item, restated (adjudication r1/M8).** Round 1 called the missing cold-engine friction model *"roughly neutral"* because the ruler and V2 share an engine and V1's is smaller. That addresses the initial cold start. The asymmetry that matters is duty-cycle thermal cycling: on VOLT-SUB V1's genset runs only 0.335 of the time in about 2 blocks, so its off-blocks average roughly 19 minutes, while the ruler's engine runs continuously and stays hot. WS4's `fmep_bar()` is a function of rpm only and is documented as a warm-engine model, so the ratified simulator **cannot express** the penalty; `START_FUEL_G = 12.0` covers a load-acceptance ramp, not a thermal state. I cannot quantify it without a thermal model and I will not invent one inside a ruler trial. What I can state is that the omission systematically flatters the single mechanism V1's ADVANCE rests on, and that it is larger at −10 C, which is V1's binding corner. **ESC-8** asks for a ruling and an owner.

Heat rejected by component and case, for the WS6 ledger (R9), is in `data/heat_ledger_ws6.csv` and `results_ws11.json → heat_ledger_ws6`. Round 2 adds what WS4's own KX-m7 finding asked for and round 1 discarded: the **instantaneous peak** and the peak **120 s / 600 s rolling-window means** for both engines, because a cooling owner sizes against a window and not a cycle mean; the exhaust / coolant+oil / CAC / radiation split on WS4's own declared balance; and the ruler rows emitted **once** per duty × case instead of once per candidate pass, which was duplicating every VOLT-SUB ruler row in the file handed to WS6 (r1/m7).

## 11. Escalations

Every escalation cites the ruling it challenges. None is self-resolved.

### ESC-1 — The only public NPR fuel-economy reference I could obtain is a crowdsourced in-use aggregate, and it cannot calibrate a drive cycle

*Challenges:* the assignment's ruler-anchor requirement

The assignment makes a sourced public anchor mandatory and forbids a corridor fit. I obtained one: Fuelly's Isuzu NPR-HD page (owner fuel logs), distance-weighted over its own per-model-year table to 8.378 mpg = 28.07 L/100 km over 179,702 miles. I also obtained the manufacturer's own 2023 NPR-HD specification sheet, which fixes the axle ratio, transmission, lock-up range, engine, tyre, GVWR and chassis mass - but publishes NO fuel economy, because US medium-duty trucks are not fuel-economy rated. What I could NOT obtain is a cycle-resolved NPR measurement. The anchor's duty, load, body and driver mix are unknown; 56% of its tracked miles are a MY2002 truck with the earlier 4HE1 engine. Its 4HK1-era subset alone reads 32.01 L/100 km. I have therefore used it as a VALIDATION with the residual stated, not as a calibration target, and tuned nothing to it. The lead should know that the ruler's absolute level rests on declared physics, not on a measured NPR. I MUST STATE THE CONSEQUENCE PLAINLY, which round 1 did not: the assignment's word is 'calibrate', and I did not calibrate. For V1's ADVANCE that is safe - the residual is in the ruler's favour and the margin is a lower bound. For V2's KILL it is the unsafe direction, and the quantity that matters is the flip point, not the residual. V2 draws with the ruler if the real NPR burns only 6.93% more fuel than modelled, and reaches the 3% ADVANCE bar at 10.24%. The anchor says the real fleet burns 46% more (all model years) or 67% more (4HK1-era subset). And the eight ruler-modelling levers this workstream declares are on their own enough to close that gap: at their declared pessimistic ends V2's nominal margin is +0.13% min / +0.59% median. The lead is being asked to execute a KILL on an UNCALIBRATED ruler and should decide with that in front of it.

*Requested:* a ruling on whether an uncalibrated ruler may carry a KILL at all; and either accept the validation-not-fit treatment on the record or fund a cycle-resolved chassis-dyno or logged-route measurement of an NPR-HD as a WS7 item BEFORE V2's KILL is executed

### ESC-2 — The cold corner as ordered does not charge cab heat; I have bracketed it rather than smuggling it into the gate

*Challenges:* R30 / D19 (Vehicle One doctrine) as applied to Vehicle Zero

BASELINE_v4 R30 makes pack preconditioning and a coolant/waste-heat cab path a modelled requirement for every Vehicle One electrified candidate, on the ground that 'the conventional truck heats itself for free and the comparison must charge that'. My assignment orders the Vehicle Zero cold corner as '-10 C with WS3 cold acceptance applied' and orders no cab-heat member. Vehicle Zero's candidates are not BEVs - both carry a running diesel, so the cab path is free whenever the genset runs and electric only in the engine-off windows. I have run the corner exactly as ordered for the gate and exported the cab-heat member as a declared bracket beside it. The lead should rule whether R30 extends to Vehicle Zero; if it does, the bracket becomes the corner of record. The exposure, which round 1 understated: cold_-10C IS V1's governing corner. As ordered it is +19.12%. With the cab-heat member it is +4.72%. With the cab-heat member AND ESC-4's CdA 5.4 - both of which are live rulings and neither of which is mine to make - it is +3.662% min / +4.052% median, i.e. V1's ADVANCE clears the >=0% corner bar by about a point. V1's ADVANCE is real but it is CONDITIONAL on these two rulings.

*Requested:* a ruling extending or not extending R30 to Vehicle Zero, taken together with ESC-4, because it is the COMBINATION that decides how much headroom V1's ADVANCE actually has

### ESC-3 — WS4's `aftertreatment_extra: 60 kg` is ambiguous and it moves V2's payload by 60 kg

*Challenges:* WS4 interface_ws4.v2_genset.mass_kg

WS4 exports the V2 genset as total_dry 637 kg PLUS a separate `aftertreatment_extra: 60.0`. The 4HK1-V2C is declared to be the same production hardware as the ruler's 4HK1-TC, so on one reading its aftertreatment is the stock truck's aftertreatment and cancels; on the other reading it is 60 kg the candidate carries and the ruler does not. 60 kg is 2.44% of V2's payload, but it does NOT move the metric by that many points - the payload enters as a ratio against the RULER's payload, not as a fraction of itself, and the measured shift on VOLT-REG is -2.70 pp (-7.925% to -10.622%). Round 1 asserted the two were the same number (adjudication r1/m2). I have taken the cancelling reading for the headline (the reading FAVOURABLE to the candidate) and exported the other as a bracket. V2's verdict does not turn on it, but the lead should close the ambiguity before any later candidate does.

*Requested:* a ruling on whether `aftertreatment_extra` is incremental to a stock 4HK1 installation

### ESC-4 — The whole Vehicle Zero comparison is being run at a CdA that the baseline itself calls provisional, and the ruler is the vehicle that suffers

*Challenges:* BASELINE_v1 vehicle parameters (CdA 4.2, PROVISIONAL pending WS7 coastdown)

CdA 4.2 m^2 is a WS1 fitted value, declared PROVISIONAL in BASELINE_v1 pending the WS7 coastdown, and the program already carries CdA 5.4 as a sizing case (E13). A 16 ft dry-freight box on an NPR-HD cab is a 5-6 m^2 object. Aero work is the one load a series hybrid cannot recover, so a larger CdA moves the comparison AGAINST the candidates. My CdA 5.4 bracket is exported for both duties. The coastdown is not a nicety here: it is the single input most able to move a Vehicle Zero verdict.

*Requested:* WS7 coastdown scheduled before any Vehicle Zero efficiency claim is ratified

### ESC-5 — The metric of record cannot see time, and on the sustained climb that hides the real difference between these vehicles

*Challenges:* Gate G1's net-energy demand-trace convention (BASELINE_v1), inherited by WS4's ratified simulator

Every fuel number here follows the identical demanded wheel-power trace, with shortfalls booked as unserved energy and fuel-corrected - the convention WS4's ratified simulator uses, adopted so the two vehicles are differenced without a convention step. It is the right convention for energy and the wrong one for capability. On WS1 s4.4's 10 km 6% climb the ruler settles at 82.0 km/h and holds it indefinitely; V2 holds the demanded speed only while its buffer lasts and its genset-only sustainable speed is 74.6 km/h. Make the climb 20 km instead of 10 and the sign of that comparison changes. R38's trip-time gate catches some of this; it does not catch a candidate that passes a 10 km climb and fails a 20 km one. I have exported the sustained-capability numbers separately so the lead can see what the metric cannot. Round 1 cited R9 here; that is the ensembles / part-load / heat-ledger ruling and it is not what this challenges. The citation is corrected to Gate G1's convention (adjudication r1/m4). Round 1's capability pass also did not enforce steady-state capability at all, so the settled-climb speeds it offered the lead as the remedy were wrong in the export; that is fixed (r1/B2) and the forward pass now reconciles with the closed-form sustainable speeds to 0.00 km/h on the ruler and 0.30 km/h on the candidate.

*Requested:* a ruling on whether a sustained-gradeability floor joins the Vehicle Zero criteria, as D16 did for Vehicle One

### ESC-6 — R32 asks whether the Vehicle Zero design is more efficient than the truck it replaces; the answer is duty-indexed and the two variants land on opposite sides

*Challenges:* R32's own framing

D15 says architecture is duty-indexed. This trial confirms it inside a single vehicle programme: V1 on its suburban duty and V2 on its regional duty return verdicts of opposite sign on the same criterion, the same ruler and the same code. Any sentence of the form 'Vehicle Zero is more efficient than an NPR-HD' is false without the duty and the variant attached. I ask that the baseline record the answer to R32 as a pair of duty-indexed results, not as a programme-level claim.

*Requested:* baseline wording that names the duty and the variant

### ESC-7 — 'payload +/-20% of ruler payload' erases the metric's own penalty at two of the four corners

*Challenges:* the assignment's corner definition

Read literally - and I have gated on the literal reading - the payload corners put the SAME freight on the ruler and on the candidate. The payload denominators are then equal, so at those two corners the per-payload metric IS the per-km metric and the candidate's curb penalty shows up only as extra road load, which is several times weaker. The visible symptom is that V2 scores +6.27% and +7.21% at the two payload corners while scoring -7.93% at nominal on the same metric. I have exported the variant reading (each vehicle scales its own payload), which preserves the denominator and is consistent with the nominal convention. Neither verdict changes under either reading, so nothing here is load-bearing tonight - but the next candidate set should not inherit a corner that switches the metric off. WHICH READING IS THE NOVEL ONE, which round 1 did not say: the VARIANT reading is the program's established convention, not the ordered one. `WS8_semi_architecture/ws8_candidates.py` defines `payload_kg()` as `(m_gcw - tare_common - powertrain_mass) * ctx.payload_factor`, i.e. it scales EACH VEHICLE'S OWN payload, and WS9 inherited that under the R28/ESC-3 corner set this assignment mirrors. The literal reading I gated on is therefore a DEPARTURE from the convention the program has been running, not merely an ambiguity in my assignment's wording. Note also that `interface_ws11.verdicts.V2_on_VOLT-REG.corner_margins_pct_min` exports payload_p20 +6.27 and payload_m20 +7.21, which read on their face as V2 winning at those corners; they are the per-KM margin under a different name, because the denominators cancel.

*Requested:* a ruling fixing the payload-corner convention for Vehicle Zero and Vehicle One alike, on the record that WS8's `payload_kg()` and R28/ESC-3 already fix it the other way for Vehicle One

### ESC-8 — Nothing in the ratified toolchain can express duty-cycle thermal cycling, and the one mechanism V1's ADVANCE rests on is the one that would be charged for it

*Challenges:* R9's part-load convention as it applies to engine THERMAL state, and WS4's `fmep_bar()` warm-engine friction model

Round 1 classified the missing cold-engine friction / warm-up model as 'roughly neutral' on the ground that the ruler and V2 share an engine and V1's is smaller. That reasoning addresses the INITIAL cold start. It does not address the asymmetry that matters, which is duty-cycle thermal cycling: on VOLT-SUB V1's genset is OFF about 66% of the time in roughly 2 blocks per cycle, so its off-blocks average on the order of 19 minutes, while the ruler's engine runs continuously and stays hot. WS4's `fmep_bar()` is a function of rpm only and is documented as a warm-engine model, so the ratified simulator CANNOT express the penalty; `START_FUEL_G = 12.0` covers a load-acceptance ramp, not a thermal state. I cannot quantify this without a thermal model and I am not going to invent one inside a ruler trial. The finding I can state is that the omission is NOT roughly neutral: it systematically flatters the single mechanism V1's ADVANCE rests on - engine-off is worth 72.58 pp of V1's margin - and it is larger at -10 C, which is V1's binding corner (adjudication r1/M8).

*Requested:* a ruling on whether a cold/warm-up friction member is required before a start-stop advantage is ratified, and if so an owner for it - it is a WS4 engine-model item, not a WS11 one

### ESC-9 — The V2 numbers of record are produced by runs that operate above V2's ratified continuous rating, and on the governing corner they empty the pack

*Challenges:* R18's ratified 132 kW continuous flat-rating for the 4HK1-V2C, and WS4's own KX-M1 emergency-band ceiling

WS4's simulator lets the series engine leave its pin in the emergency band and follow load up to the AUTOMOTIVE full-load curve, which for ENG_V2 is above the R18-ratified 132 kW continuous flat-rating. Reading WS4's own counters, which round 1 discarded entirely: V2 spends time above its continuous rating in 6 of 6 exported cases INCLUDING the nominal case that produces the headline (146.5 s, 0.624 kWh), and on the governing climb corner the pack reaches SOC 0.000 with 1.720 kWh of unserved bus energy. WS4's own KX r3 states the same exposure more widely and more correctly than WS11's case set can: on the union of its ordered set and an R6 rating-family probe set the genset spends up to 287.1 s per cycle above its continuous flat-rating (against 250.0 s over the ordered set alone), with peak shaft at 112.03% of that case's OWN rating. That is the framing this escalation asks the lead to rule on; WS11's counters below are its own measurement on its own case set and are not offered as a substitute for it. The direction of every one of these is TOWARD the candidate, so none of them changes the KILL - but the exported V2 numbers are not achievable inside V2's own ratified rating, and a KILL executed on numbers that flatter the candidate is at least the safe direction for the decision while being the wrong basis for the record. WS4's `emerg_cap_cont_rating` bracket is exercised and exported (adjudication r1/M3).

*Requested:* a ruling on which ceiling governs a Vehicle Zero series candidate's emergency band - the automotive full-load curve or the ratified continuous flat-rating - taken together with WS4's KX-M1

---

## 12. Construction sweep

The rework order requires a sweep beyond the named findings, in three directions, **and requires the clean areas to be reported as well as the dirty ones**. The auditable record is `results_ws11.json → construction_sweep_r2`; this is its summary.

### (a) Fields whose construction may not match their name

Eight were named by the adjudication (B1, B2, M4, M5, M6a, M6b, m7, m10). **Six more were found here:**

| field | what the name promised | what it was |
|---|---|---|
| `capability_limited_s` | samples where capability bound the vehicle | samples where it bound *acceleration* only — it read zero through a sustained climb the vehicle could not hold. Separate defect from B2's physics error, in the same line of code |
| `eng_reject_kwh` (ruler) | heat rejected by the engine | fuel energy *including the unserved-work fuel correction* minus shaft — heat from fuel never burned. WS4's candidate-side field is accumulated from the real burn, so the two vehicles' WS6 rows were not on one basis |
| `mean_kW_over_cycle_max` | the worst cycle-mean rejection | max energy over seeds divided by *median* duration over seeds |
| `per_km_vs_per_payload_identity.checked` | that the check was made | a hard-coded `true` beside a computed residual |
| `..._no_waste_heat_credit_worst` | an upper bound on the margin | an upper bound on the *penalty*, i.e. a **lower** bound on the margin. Introduced in this round's own first draft, and the same class WS4's KX r3 sweep found in its own workstream |
| `ruler_available_wheel_kw` | — | a second, never-called statement of the capability physics that could drift from the model of record. Deleted |

**Checked and clean:** `break_even_curb_kg`; every paired margin envelope; `ratio_worst` and `pct_worse_than_ruler_worst`; `sustained_6pct_capability_kmh` and its interface worst-case field; `break_even_per_km_advantage_pct`; every governing-case string; `ws4_regression`; `payload_corner_variant_margin_pct_min`; `min_speed_above_30kmh_demand_kmh`; `max_speed_deficit_kmh`; heat-ledger case coverage.

### (b) Claims of robustness or boundedness that were not run

Four were named (B1, m3, B2/M3, M8). **Two more were found here:**

- **§1.2's *"every candidate margin in this report is a lower bound"*** was unqualified and is not true of the CdA road-load row, which lowers both candidates' margins, nor of ESC-3's aftertreatment reading. It is now stated with respect to ruler-**modelling** choices only, which is what the evidence supports.
- **§9's *"Nine of WS11's input pins…"*** was a count typed into prose. Three source pins were added this round. It is derived from the run now.

**Checked and clean:** *"A fit was not used"* (independently confirmed by the adjudication); *"neither verdict changes under either payload-corner reading"* (both run); the mass ledgers *"to the kilogram"* (independently re-derived); V1's 6% capability against WS1's independent figure; §2.3's *"more than its whole pack again"*; and the R38 gate outcome, which is PASS on all three rows both before and after the B2 correction.

### (c) Statistics of statistics standing in for paired ones

One family was named (M6). **Seven more were found here — four of them in code written for this round:**

- `emergency_band_at_continuous_rating_bracket.*.shift_pp` — new this round, was min-minus-min
- `derated_load_fraction_convention.*.shift_pp` — new this round, same
- `ruler_engine_curve.worst_margin_shift_pp` — new this round, a max over differences of independently minimised numbers
- `interface_ws11.verdict_robustness.*.shift_pp` — new this round, **and it carries the headline correction of §1.3**, so it is exactly the field that must not be a statistic of statistics
- `v2_aftertreatment_bracket_effect.*.shift_pp` and `ruler_chassis_cab_cross_check.*.shift_pp` — exact algebra on the same per-seed values so the artefact is zero, formed per seed anyway
- `heat_ledger_ws6.mean_kW_over_cycle_max` — see (a)

Every one is now formed seed by seed and enveloped afterwards, with the unpaired figure retained beside it. **No row in `results_ws11.json` is a statistic of statistics.**

**Checked and clean:** every headline and corner margin (the adjudication independently re-derived all 128 seed-cases and found no ratio-of-medians artefact); the bracket-margin rows; both cold-corner blocks; `break_even_curb`; the flip points; the trip-time ratios; and the anchor residuals, which compare a median ruler level against a scalar anchor and have no pairing to do.

**Reading.** The sweep found fifteen further constructions beyond the twenty-four findings the adjudication named, four of them in code written for this round — which is the argument for sweeping *after* fixing rather than before. **None of them moves a verdict.**

---

## 13. Reproduction

```
cd WS11_vehicle_zero_ruler
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python run_ws11.py          # ~10 min, writes results_ws11.json + data/
python make_report_ws11.py  # regenerates this file from that JSON
python verify_ws11.py       # asserts every number here against the JSON
```

Fixed seeds throughout; no randomness outside the seeded WS1 cycle builders. `run_output.txt` deliberately carries no elapsed times — a committed artefact stamped with a timer can never be byte-stable, and that is the first of CLAUDE.md's binding rules.

**Byte stability is re-measured every round, not carried forward.** Round 1's claim rested on round-1 code; this round's rests on this round's. Two consecutive full runs of the round-2 pipeline were hashed file by file — `results_ws11.json`, `REPORT_WS11.md`, `run_output.txt`, every CSV in `data/` and every 10 Hz trace — and the result is recorded in `determinism_check.txt` beside this report: **every file byte-identical, zero differing hashes.** The measurement was made twice on this round's code — once mid-rework and once on the final state — and both passes were clean.

One caveat the lead should hear plainly, and it is now a *demonstrated* one rather than a warning: WS4_genset was being reworked concurrently and **WS4 KX round 3 landed during this rework**. The vintage this report ran against is pinned in §9, `ws4_sim.py` is byte-identical across the change, no value inside `series_duty_v2 → cases` moved, and the hot-swap assertion passed against the new vintage without a line of WS11 changing. That is the seam working as designed.

`check_determinism_ws11.py` recomputes the two headline blocks from scratch in about a minute and asserts they reproduce the stored values bit for bit, for a reviewer who does not want to wait out the pipeline.

### 13.1 A provenance note on the baseline

This report executes **BASELINE_v5 R32**, which is the baseline named in `ASSIGNMENT.md` and the one authoritative when the round was run and when every number in it was produced. **`BASELINE_v6.md` was ratified at the repository root while this rework was being written**, and it disposes this round — it quotes these numbers, rules on several of the escalations below, and orders a WS11 r3 with a fresh scope. Nothing here has been rewritten to chase it: the numbers in this file are the numbers v6 read, the escalations are stated as they were put, and re-pointing the citations after the fact would make the artefact circular. Where v6 rules on an escalation, **the ruling governs and this report's bracket does not** — in particular the cold-corner cab-heat member of §5, which v6 rules on with a different specification from the one bracketed here. The r3 order implements the rulings; this round records what was true before them.
