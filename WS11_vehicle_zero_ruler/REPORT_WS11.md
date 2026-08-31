# REPORT_WS11 — VEHICLE ZERO RULER TRIAL

Executes **BASELINE_v5 R32**: *"the payload-denominated metric has not been applied to Vehicle Zero. It shall be … before any Vehicle Zero result is described as an efficiency advantage."*

**Question of record.** Is the ratified Vehicle Zero design more efficient than the truck it replaces, on the honest metric?

**Answer, in one line.** It depends on which variant and which duty, and the two answers have opposite signs. **V1 Postal on VOLT-SUB: ADVANCE at +20.11% ensemble-min against a 3% bar. V2 Trucker on VOLT-REG: KILL at -7.93% — it wins +8.41% per km and hands back 16.34 points of freight to get there.**

Everything below is generated from `results_ws11.json`; `verify_ws11.py` asserts every number in this file against it.

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

**One discrepancy, stated rather than buried.** The assignment orders WS4's reference 4HK1-class map, whose label is *"baseline reference curve 700 Nm @ 1,600 rpm / ~153 kW"*. The sourced 2023 spec sheet rates the truck at 215 hp @ 2500 rpm and 452 lb-ft @ 1850 rpm — a little more peak power and appreciably less low-end torque than the ordered curve. I ran the ordered map. The direction of the difference is mixed and small: the ordered curve gives the ruler MORE torque where a truck lugs (better gradeability, a better-placed BSFC island) and slightly less peak power. Both effects are inside the brackets in §1.3.

> **Every declared choice above is the RULER-FAVOURABLE one.** That is deliberate and it is stated once here so it can be checked everywhere: the candidates' margins in this report are **lower bounds**. Each choice is re-run reversed in §1.3.

### 1.2 The sourced anchor

The assignment makes a sourced public NPR fuel-economy reference mandatory and forbids a fit to the 18–30 L/100 km corridor. **A fit was not used.**

- **Anchor**: Fuelly - Isuzu NPR-HD, all model years (owner fuel logs) — `https://www.fuelly.com/truck/isuzu/npr-hd/all`, retrieved 2026-08-31, page text stored verbatim as `sources/fuelly_npr_hd_all.txt` and SHA-256 pinned in `results_ws11.json`.
- Page statement, verbatim: *"21 Isuzu NPR-HDs have provided 180 thousand miles of real world fuel economy & MPG data."*
- Distance-weighted over the page's own per-model-year table (miles ÷ gallons, not a mean of means): **8.378 mpg = 28.07 L/100 km** over 179,702 miles and 1,044 fuel-ups.
- The 4HK1-era subset alone (MY2014–2016) reads 7.347 mpg = 32.01 L/100 km; MY2002 (the earlier 4HE1 truck) carries 56% of the tracked miles. Full table in `data/ruler_anchor.csv`.

**Model against anchor.** The ruler as specified above returns **19.18 L/100 km** on VOLT-SUB at GVW (8-seed median; range 19.11–19.22), which is inside the assignment's 18–30 L/100 km sanity corridor and -31.69% against the anchor. With every ruler-favourable choice reversed it returns 24.20 L/100 km, i.e. -13.81% against the anchor.

The residual is **in the ruler's favour on both settings**. That is the honest reading and it is the direction that matters: a ruler that burns less than the real fleet makes every candidate margin smaller. The anchor's duty, load, body and driver mix are unknown and it cannot resolve a drive-cycle-specific calibration — **ESC-1**.

### 1.3 Ruler brackets — every favourable choice reversed

VOLT-SUB, 8-seed median L/100 km, and the effect on V1's nominal per-payload margin (`data/ruler_brackets.csv`, `data/bracket_margins.csv`):

| ruler setting | VOLT-SUB L/100 km | VOLT-REG L/100 km | V1 margin min % | V2 margin min % |
|---|---|---|---|---|
| **headline (ruler-favourable)** | 19.18 | 19.03 | +20.11 | -7.93 |
| belt/alternator accessory model | 19.83 | 19.21 | +22.76 | -6.91 |
| converter stalled in Drive at idle | 22.50 | 19.21 | +31.93 | -6.96 |
| CdA 5.4 m² (E13 case, applied to both vehicles) | 19.90 | 21.92 | +18.06 | -10.52 |
| single-step shift schedule | 19.19 | 19.03 | +20.16 | -7.91 |
| engine/flywheel/converter inertia charged | 19.51 | 19.07 | +21.50 | -7.72 |
| **all of the above at once** | 24.20 | 22.31 | +32.62 | -8.57 |

**The lower-bound framing protects the ADVANCE. It does not protect the KILL, so the KILL needs the opposite test.** Modelling the ruler generously makes a candidate's margin smaller — the safe direction for V1's ADVANCE and the *unsafe* direction for V2's KILL. The question for V2 is therefore the reverse one: how does it fare when the ruler is modelled as badly as this study can justify? The most V2-favourable single bracket in the table is the belt/alternator accessory model, and it leaves V2 at -6.91% — still negative at nominal before a single corner is applied, and still far below the 3% bar. **V2's KILL does not turn on how the ruler was modelled.** (The CdA 5.4 row moves V2 the other way, to -10.52%, because a bigger frontal area is a change to the ROAD that both vehicles drive, not a ruler modelling choice, and the aero work it adds is served through the series chain's lower efficiency.)

Every ruler-modelling reversal moves V1's verdict further from the bar and V2's slightly toward it. Neither verdict changes under any of them.

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

WS4's `aftertreatment_extra: 60 kg` is EXCLUDED from the headline (the reading favourable to V2) and carried as a bracket: V2 curb 4199 kg, payload 2401 kg, break-even bar 17.21%. **ESC-3.**

### 2.3 Break-even curb mass

At fixed GVW a candidate's curb does not change its energy, only its denominator, so the curb at which each candidate exactly draws is exact, not a search:

| | actual curb, kg | break-even curb, kg (worst seed) | headroom, kg |
|---|---|---|---|
| V1 on VOLT-SUB | 3888 | 4433 | +545 |
| V2 on VOLT-REG | 4139 | 3944 | -195 |

V1 could gain another 545 kg before it stopped beating the ruler — more than its whole pack again. V2 is over its break-even curb by 195 kg, which it has nowhere to find: deleting the entire 280.5 kg pack would also delete the architecture.

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

Each row is a real re-run, not an algebraic split, at nominal on the candidate's design duty, ensemble-min of the paired per-payload margin (`data/one_factor.csv`).

| factor | V1 on VOLT-SUB | V2 on VOLT-REG |
|---|---|---|
| **mass penalty alone** (the freight given back) | 5.18 pp | 16.34 pp |
| **regen alone** (worth, vs regen cap = 0) | 24.02 pp | 4.38 pp |
| **engine-off alone**, vs a load-following genset that never stops (mode b′, carries WS4's 25 kW floor) | 74.88 pp | 0.31 pp |
| **engine-off alone**, vs a genset held ON at the pinned point | 103.84 pp | 65.75 pp |
| **engine operating point alone** (ruler re-scored at the candidate's pinned island BSFC) | 11.41 pp | 12.59 pp |

Supporting numbers: the ruler's duty-mean effective BSFC is 261.35 g/kWh on VOLT-SUB and 227.43 g/kWh on VOLT-REG, against pinned island points of 228.72 g/kWh (V1) and 203.62 g/kWh (V2).

**These rows are independent counterfactuals and they do not sum.** Each is the full model re-run with one thing changed; there is no algebraic decomposition here and none is claimed. The term that has no row is the series path's own conversion penalty — engine → generator → bus → inverter → motor → 10:1, against the ruler's geared path — which is what the four positive rows are spending their winnings on.

**Reading.** On VOLT-SUB the series architecture wins on three independent mechanisms — regen on a 30-stop cycle, engine-off across a 44%-idle duty, and an engine that never leaves its island — and the freight give-back is small because V1 deletes a 500 kg engine as well as a gearbox.

On VOLT-REG regen is nearly worthless (braking is 5.9% of tractive energy), the operating-point win survives, and the freight give-back is almost twice the entire per-km gain. **The single term that kills V2 is the one D13 named.**

The two engine-off rows deserve a sentence of their own, because they disagree and the disagreement is informative. Against a genset that can follow load, engine-off is worth 0.31 pp on VOLT-REG — nothing. Against a genset stuck at its pinned point it is worth 65.75 pp — everything. **That gap is a dispatch result, not an architectural one**, and it is precisely R22b's open question, which BASELINE_v3 assigns to WS5. WS11 measures both ends and claims neither.

## 5. Corners

Corner set: payload ±20% of the ruler's payload; −10 C with WS3's cold acceptance actually applied; 2,000 m / +45 C on the R6 derate basis; and WS1 §4.4's 10 km / 6% climb spliced into VOLT-REG. Definitions in `results_ws11.json → case_definitions`.

| corner | V1 on VOLT-SUB | V2 on VOLT-REG |
|---|---|---|
| payload +20% (3,480 kg freight) | +22.84% | +6.27% |
| payload −20% (2,320 kg freight) | +24.66% | +7.21% |
| −10 C, WS3 cold acceptance applied | +19.12% | -8.77% |
| 2,000 m / +45 C, R6 derate | +22.27% | -3.52% |
| 10 km / 6% climb inserted into VOLT-REG | n/a (R5: VOLT-REG is not a V1 cycle) | -9.98% |

**The −10 C corner uses the actual curve, not an assumption.** Pack charge acceptance at −10 C cells is read from WS3's `regen_acceptance.csv` column `V2pack_chg_cont_kW_bus`; air density is recomputed for the corner. No cold-engine friction model is applied to *either* vehicle — the ruler and V2 share an engine, so that omission is close to neutral, and it is declared.

**Two payload corners, two readings.** Read literally — and the gate uses the literal reading — both vehicles carry the *same* freight at those corners, so the payload denominators cancel and the per-payload metric becomes the per-km metric. That is why V2 scores +6.27% at +20% while scoring -7.93% at nominal on the same metric. Under the variant reading (each vehicle scales its own payload) V2 returns -7.73% and -7.57%, and V1 returns +19.44% and +20.51%. **Neither verdict changes under either reading.** **ESC-7.**

**Cab-heat bracket at −10 C (R30's Vehicle One member, not ordered here).** Charging the candidate 4.00 kW of aux (3.0 kW of cab heat during the engine-off windows only; the ruler and the running genset both give it away free) moves V1's cold corner from +19.12% to +2.64% and V2's from -8.77% to -11.58%. **V1's ADVANCE survives it; V2's KILL deepens.** **ESC-2.**

## 6. Trip time (R38) and sustained capability

R38 is a **gate, not a term**: the metric of record stays energy per payload tonne-km and the lead applies the ≤ +5% test. Trip time comes from a separate capability-limited forward pass (the fuel convention follows the demanded trace and by construction cannot see time).

| run | ruler trip time, s (median) | candidate, s (median) | ratio cand/ruler, worst | vs ruler | ≤ +5%? |
|---|---|---|---|---|---|
| V1 / VOLT-SUB nominal | 3490.80 | 3490.80 | 1.00000 | +0.000% | PASS |
| V2 / VOLT-REG nominal | 6582.27 | 6577.05 | 0.99936 | -0.064% | PASS |
| V2 / VOLT-REG + 10 km 6% climb | 6963.13 | 6963.39 | 1.00044 | +0.044% | PASS |

**What the trip-time gate does not catch.** Sustained speed on a 6% grade at GVW, with **no** buffer contribution — the only power available for an indefinite climb:

- ruler: **82.01 km/h**
- V2: **74.63 km/h** (genset 126.91 kW bus continuous)
- V1: **31.76 km/h** — WS1 §4.4's independently-derived 30.2 km/h for the 50 kW class, reproduced here from a completely different code path

V2 passes the 10 km climb because its buffer lasts almost exactly 10 km. Extend the climb and the sign of the capability comparison flips. **ESC-5.**

## 7. ADVANCE / KILL against the pre-committed criterion

**Criterion (pre-committed, same form as Vehicle One's R25/R37):** ADVANCE only if >= 3% better than the ruler on the candidate's design duty at nominal, ensemble-min, AND >= 0% at every corner. Metric: fuel energy per payload tonne-km, paired per-seed.

### V1 Postal on VOLT-SUB — **ADVANCE**

- nominal, ensemble-min: **+20.11%** (governing: seed 4 of the enumerated 8-seed VOLT-SUB ensemble); median +20.83%, max +21.13%. Against the 3% bar: **+17.11 pp** — PASS.
- worst corner: **+19.12%**, governing case *cold_-10C (min over the enumerated corner set ['alt2000m_45C', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 4 of the enumerated 8-seed VOLT-SUB ensemble*. Against the 0% bar: **+19.12 pp** — PASS.
- R38 trip-time gate: PASS (+0.000% worst).

### V2 Trucker on VOLT-REG — **KILL**

- nominal, ensemble-min: **-7.93%** (governing: seed 5 of the enumerated 8-seed VOLT-REG ensemble); median -7.27%, max -6.93%. Against the 3% bar: **-10.93 pp** — FAIL.
- worst corner: **-9.98%**, governing case *climb_10km_6pct (min over the enumerated corner set ['alt2000m_45C', 'climb_10km_6pct', 'cold_-10C', 'payload_m20', 'payload_p20']), itself at seed 5 of the enumerated 8-seed VOLT-REG+CLIMB ensemble*. Against the 0% bar: **-9.98 pp** — FAIL.
- R38 trip-time gate: PASS (-0.064% worst).

The lead executes or spares. WS11 reports the numbers.

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

## 9. Input vintages and the hot-swap seam

| input | vintage |
|---|---|
| WS4 `interface_ws4.series_duty_v2` | `live_design_input`, cases alt2000m_45C, cda_5.4, nominal, seeds [23, 3, 4, 5, 6, 7, 8, 9], usable 11.083608 kWh |
| WS4 `interface_ws4.gate_g1` | `executed_kill_2026-08-30` — **ARCHIVED, not consumed**, no field of it used as a live requirement |
| WS4 `spin_drag_operational_note_r22d` | reported by WS4, charged to fuel by nobody; WS11 charges it to neither vehicle |
| WS2 traction chain | round 4, `data/effmap_motor_inverter_662V.csv` at 662 V, ratio 10.0 |
| WS3 pack | 11.083608 kWh usable, 280.52 kg, V1 hysteresis 3.00 kWh (R19) |
| WS1 cycles | reused verbatim at 10 Hz, WS4's own seed sets |

**The hot-swap seam is an assertion, not a promise.** WS11 does not reimplement the series supervisor: it calls WS4's own `ws4_sim.run_g1_mode` in mode (b), and `run_ws11.py` asserts that the V2 nominal VOLT-REG ensemble reproduces WS4's exported `series_duty_v2[nominal]` `fuel_energy_kWh_per_km` min / median / max to 0.0e+00 — identical floats. KX was gated but **not yet adjudicated** when this ran. If the adjudicator forces a corrected vintage, no WS11 code changes: re-running `run_ws11.py` either satisfies the same assertion or fails it and names the difference.

Nine of WS11's input pins are files WS4 also pins inside `series_duty_v2.input_sha256`. **Every one matches**, which is checked in `verify_ws11.py`: WS11 and WS4 did not merely name the same upstream artefacts, they consumed byte-identical files.

SHA-256 pins for all 18 consumed inputs (upstream artefacts and the retrieved public sources) are in `results_ws11.json → _meta.input_sha256`.

### 9.1 R34 traces

One 10 Hz trace per primary run configuration, at that duty's reference seed: ruler and candidate on each design duty at nominal, V2 on VOLT-SUB, and both vehicles on the climb corner. Column sets differ by vehicle (the ruler's carries gear, lock-up state, engine speed and torque; the candidates' carry bus, generator, battery and SOC), and every file is listed with its row count in `results_ws11.json → interface_ws11.traces_r34`. The remaining seeds and corners are exported as per-seed rows in `data/per_seed_margins.csv` rather than traced — WS4's own R34 precedent (one full-rate trace, summary exports for the rest), which keeps the committed artefact set to a size a reviewer can actually open.

## 10. First-principles sanity checks

| check | WS11 | reference |
|---|---|---|
| 85 km/h flat cruise, wheel power | 46.93 kW | WS1 baseline crosscheck 46.93 kW ("~2.0 kN, ~47 kW") |
| engine speed at 85 km/h in top gear | 1749 rpm | a real NPR-HD cruises there; the sourced 4.555 × 0.63 driveline reproduces it with no fitting |
| engine speed at 100 km/h in top gear | 2057 rpm | as above |
| V1 sustained speed on 6% at GVW | 31.76 km/h | WS1 §4.4's forward simulation: 30.2 km/h |
| curb + payload = GVW | exact | by construction |
| per-km ↔ per-payload identity on every seed of every case | max residual 4.441e-16 | `1 − m_payload = (1 − m_km) × pay_ruler/pay_cand` |
| V2 nominal VOLT-REG vs WS4's live export | 0.0e+00 | identical floats |

### 10.1 Known omissions and the direction each one leans

| omission | who it flatters | size |
|---|---|---|
| WS2's 1.45 kW brake-resistor blower is not charged to the candidate bus during R15 blend overflow | candidate | small: the overflow column is near zero on both duties (`data/heat_ledger_ws6.csv`) |
| WS3's 8 kW pack heater is not run at −10 C | candidate | none at this corner: R16 permits dispatch on the published derate curves down to −15 C *cell*, and the −10 C acceptance value is the one applied |
| no cold-engine friction/warm-up model on either vehicle | roughly neutral | the ruler and V2 share an engine; V1's is smaller and would warm faster |
| the ruler's standard exhaust brake is not modelled | neither | it is a retarder, and DFCO already puts the ruler's overrun fuel at zero |
| the ruler's engine/flywheel/converter rotating inertia is not charged | ruler | bracketed in §1.3; worth ~0.3 L/100 km on VOLT-SUB |
| R22d's true-coast PM spin member is charged to neither vehicle | candidate | WS4 measures it at ≤0.0004 pp of cycle fuel |

Heat rejected by component and case, for the WS6 ledger (R9), is in `data/heat_ledger_ws6.csv` and `results_ws11.json → heat_ledger_ws6` — engine, generator+rectifier, traction chain and the R15 blend overflow for each candidate, and engine, driveline+accessories and friction brakes for the ruler, on every case.

## 11. Escalations

Every escalation cites the ruling it challenges. None is self-resolved.

### ESC-1 — The only public NPR fuel-economy reference I could obtain is a crowdsourced in-use aggregate, and it cannot calibrate a drive cycle

*Challenges:* the assignment's ruler-anchor requirement

The assignment makes a sourced public anchor mandatory and forbids a corridor fit. I obtained one: Fuelly's Isuzu NPR-HD page (owner fuel logs), distance-weighted over its own per-model-year table to 8.378 mpg = 28.07 L/100 km over 179,702 miles. I also obtained the manufacturer's own 2023 NPR-HD specification sheet, which fixes the axle ratio, transmission, lock-up range, engine, tyre, GVWR and chassis mass - but publishes NO fuel economy, because US medium-duty trucks are not fuel-economy rated. What I could NOT obtain is a cycle-resolved NPR measurement. The anchor's duty, load, body and driver mix are unknown; 56% of its tracked miles are a MY2002 truck with the earlier 4HE1 engine. Its 4HK1-era subset alone reads 32.01 L/100 km. I have therefore used it as a VALIDATION with the residual stated, not as a calibration target, and tuned nothing to it. The lead should know that the ruler's absolute level rests on declared physics, not on a measured NPR.

*Requested:* either accept the validation-not-fit treatment on the record, or fund a cycle-resolved chassis-dyno or logged-route measurement of an NPR-HD as a WS7 item

### ESC-2 — The cold corner as ordered does not charge cab heat; I have bracketed it rather than smuggling it into the gate

*Challenges:* R30 / D19 (Vehicle One doctrine) as applied to Vehicle Zero

BASELINE_v4 R30 makes pack preconditioning and a coolant/waste-heat cab path a modelled requirement for every Vehicle One electrified candidate, on the ground that 'the conventional truck heats itself for free and the comparison must charge that'. My assignment orders the Vehicle Zero cold corner as '-10 C with WS3 cold acceptance applied' and orders no cab-heat member. Vehicle Zero's candidates are not BEVs - both carry a running diesel, so the cab path is free whenever the genset runs and electric only in the engine-off windows. I have run the corner exactly as ordered for the gate and exported the cab-heat member as a declared bracket beside it. The lead should rule whether R30 extends to Vehicle Zero; if it does, the bracket becomes the corner of record.

*Requested:* a ruling extending or not extending R30 to Vehicle Zero

### ESC-3 — WS4's `aftertreatment_extra: 60 kg` is ambiguous and it moves V2's payload by 60 kg

*Challenges:* WS4 interface_ws4.v2_genset.mass_kg

WS4 exports the V2 genset as total_dry 637 kg PLUS a separate `aftertreatment_extra: 60.0`. The 4HK1-V2C is declared to be the same production hardware as the ruler's 4HK1-TC, so on one reading its aftertreatment is the stock truck's aftertreatment and cancels; on the other reading it is 60 kg the candidate carries and the ruler does not. 60 kg is 2.4% of V2's payload and therefore 2.4 points of the metric of record. I have taken the cancelling reading for the headline (the reading FAVOURABLE to the candidate) and exported the other as a bracket. V2's verdict does not turn on it, but the lead should close the ambiguity before any later candidate does.

*Requested:* a ruling on whether `aftertreatment_extra` is incremental to a stock 4HK1 installation

### ESC-4 — The whole Vehicle Zero comparison is being run at a CdA that the baseline itself calls provisional, and the ruler is the vehicle that suffers

*Challenges:* BASELINE_v1 vehicle parameters (CdA 4.2, PROVISIONAL pending WS7 coastdown)

CdA 4.2 m^2 is a WS1 fitted value, declared PROVISIONAL in BASELINE_v1 pending the WS7 coastdown, and the program already carries CdA 5.4 as a sizing case (E13). A 16 ft dry-freight box on an NPR-HD cab is a 5-6 m^2 object. Aero work is the one load a series hybrid cannot recover, so a larger CdA moves the comparison AGAINST the candidates. My CdA 5.4 bracket is exported for both duties. The coastdown is not a nicety here: it is the single input most able to move a Vehicle Zero verdict.

*Requested:* WS7 coastdown scheduled before any Vehicle Zero efficiency claim is ratified

### ESC-5 — The metric of record cannot see time, and on the sustained climb that hides the real difference between these vehicles

*Challenges:* R9 (ensembles) and the demand-trace convention inherited from Gate G1

Every fuel number here follows the identical demanded wheel-power trace, with shortfalls booked as unserved energy and fuel-corrected - the convention WS4's ratified simulator uses, adopted so the two vehicles are differenced without a convention step. It is the right convention for energy and the wrong one for capability. On WS1 s4.4's 10 km 6% climb the ruler settles at 82.0 km/h and holds it indefinitely; V2 holds the demanded speed only while its buffer lasts and its genset-only sustainable speed is 74.6 km/h. Make the climb 20 km instead of 10 and the sign of that comparison changes. R38's trip-time gate catches some of this; it does not catch a candidate that passes a 10 km climb and fails a 20 km one. I have exported the sustained-capability numbers separately so the lead can see what the metric cannot.

*Requested:* a ruling on whether a sustained-gradeability floor joins the Vehicle Zero criteria, as D16 did for Vehicle One

### ESC-6 — R32 asks whether the Vehicle Zero design is more efficient than the truck it replaces; the answer is duty-indexed and the two variants land on opposite sides

*Challenges:* R32's own framing

D15 says architecture is duty-indexed. This trial confirms it inside a single vehicle programme: V1 on its suburban duty and V2 on its regional duty return verdicts of opposite sign on the same criterion, the same ruler and the same code. Any sentence of the form 'Vehicle Zero is more efficient than an NPR-HD' is false without the duty and the variant attached. I ask that the baseline record the answer to R32 as a pair of duty-indexed results, not as a programme-level claim.

*Requested:* baseline wording that names the duty and the variant

### ESC-7 — 'payload +/-20% of ruler payload' erases the metric's own penalty at two of the four corners

*Challenges:* the assignment's corner definition

Read literally - and I have gated on the literal reading - the payload corners put the SAME freight on the ruler and on the candidate. The payload denominators are then equal, so at those two corners the per-payload metric IS the per-km metric and the candidate's curb penalty shows up only as extra road load, which is several times weaker. The visible symptom is that V2 scores +6.27% and +7.21% at the two payload corners while scoring -7.93% at nominal on the same metric. I have exported the variant reading (each vehicle scales its own payload), which preserves the denominator and is consistent with the nominal convention. Neither verdict changes under either reading, so nothing here is load-bearing tonight - but the next candidate set should not inherit a corner that switches the metric off.

*Requested:* a ruling fixing the payload-corner convention for Vehicle Zero and Vehicle One alike

---

## 12. Reproduction

```
cd WS11_vehicle_zero_ruler
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python run_ws11.py          # ~10 min, writes results_ws11.json + data/
python make_report_ws11.py  # regenerates this file from that JSON
python verify_ws11.py       # asserts every number here against the JSON
```

Fixed seeds throughout; no randomness outside the seeded WS1 cycle builders. `run_output.txt` deliberately carries no elapsed times — a committed artefact stamped with a timer can never be byte-stable, and that is the first of CLAUDE.md's binding rules.

**Byte stability, measured not asserted.** Two consecutive full runs were hashed file by file — `results_ws11.json`, `REPORT_WS11.md`, `run_output.txt`, all nine CSVs in `data/` and all seven 10 Hz traces. **Every file was byte-identical**, and a structural key-by-key diff of the two `results_ws11.json` files returned **zero differing leaf values**.

One caveat the lead should hear plainly: WS4_genset was being rewritten by a concurrent night-shift session throughout this work, and several distinct vintages of `results_ws4.json` passed under WS11 while it ran. The `series_duty_v2[nominal]` ensemble WS11 consumes was byte-identical in every vintage checked and the §9 hot-swap assertion passed against each, so no number here moved — but `_meta.input_sha256["WS4/results_ws4.json"]` records which vintage each run actually read, and it is the field that will move first if a corrected KX lands. That is the pin doing its job.

`check_determinism_ws11.py` recomputes the two headline blocks from scratch in about a minute and asserts they reproduce the stored values bit for bit, for a reviewer who does not want to wait out the pipeline.
