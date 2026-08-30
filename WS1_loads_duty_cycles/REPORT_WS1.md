# REPORT WS1 — LOADS & DUTY CYCLES

Project Volt · workstream 1 · against BASELINE v0 (ratified 2026-08-29)
Author: WS1 (duty-cycle & loads). Status: **for ratification**.

Everything below is produced by runnable code in this folder. `run_ws1.py`
regenerates every number, table and figure in ~25 s; `results.json` is the
machine-readable form of all of it, and `tables.md` is generated directly
from `results.json`, so nothing here is transcribed by hand.

> **Independent review.** Before submission the analysis was put through a
> 13-agent adversarial review: seven agents recomputed the headline numbers
> from first principles without using this code, three audited the source
> for physics and numerical defects, two attacked completeness, and one
> adjudicated. **Seventeen defects were found and fixed and nine analysis
> gaps closed** (§9, with what each one moved). Where an objection changed a
> conclusion rather than a number — the descent case, the direct-path grade
> limit, Numbers ③ and ④, and the §5 preamble — the version here is the
> corrected one. Twelve further objections were judged defensible but
> undisclosed and are now disclosed; the rest were reviewer errors and are
> listed as such in §9.4.

---

## 1. Assumptions

### 1.1 Inherited from the baseline (not relitigated)

GVW 6,600 kg · dynamic tyre radius 0.37 m · CdA 4.2 m² · Crr 0.009 ·
fixed final drive 2.8:1 (engine → wheels, V2 only) · traction-motor
reduction 10:1 · 13.5 kN tractive force 0–20 km/h · reference engine
4HK1-TC ~700 Nm @ 1,600 rpm, ~150 kW, idle 700 rpm · efficiency chain
gen 0.94 × PE 0.97 × inverter+motor 0.92 × reduction 0.97, direct
mechanical path 0.95 · V1 pure series, V2 series below ~60–70 km/h then
lockup into 2.8:1.

### 1.2 Added by WS1 (each one is a knob in `volt_params.py`)

| Assumption | Value | Basis |
|---|---|---|
| Air density | 1.20 kg/m³ | *Chosen because it reproduces the baseline's own "85 km/h → 2.0 kN, 47 kW"* (1,988 N / 46.9 kW). This is a fitted input, not an independent one — see Escalation **E13**. |
| Rotating-mass factor λ | 1.04 | wheels/hubs/drums I ≈ 25 kg·m² → 183 kg equivalent; motor rotor 0.08 kg·m² through 10:1 → 58 kg; total 241 kg on 6,600 kg. Engine+flywheel through 2.8:1 adds ~34 kg in lockup. **A transmissionless truck has an unusually low mass factor** — a geared truck in a low gear is 1.2+. |
| Operating curb mass | 3,700 kg | NPR-HD chassis-cab + 16 ft dry-freight body + driver + full fuel/DEF. Implies **payload at GVW = 2,900 kg**, which is what the ±20% sensitivity swings. |
| Accessory load | 2.0 kW at the DC bus (0.5 / 4.0 kW in sensitivity) | EPS ~0.3 + brake boost ~0.3 + cab HVAC ~1.0 + 24 V/ECU ~0.4 kW. The NPR-HD has hydraulic, not air, brakes, so there is no air compressor. **Contains no thermal-management power** — a gap in the two sustained-grade cases, where the whole powertrain runs flat out for 10–20 minutes. |
| Battery round-trip | 0.97 charge / 0.97 discharge | high-power buffer chemistry; **WS3 to confirm**, and see **E8** — the C-rates implied here are severe. |
| Regen blend-out | tapers to zero between 8 and 3 km/h | motor controllability and back-EMF collapse as the vehicle stops. Costs 1.9% of braking energy on VOLT-SUB, 0.8% on VOLT-REG (§4.7) — 4–11× less than the 75 kW cap costs. |
| V2 lockup handover | 65 km/h with ±3 km/h hysteresis; **clutch opened whenever wheel-power demand is negative** (regen priority) | inside the baseline's "60–70 km/h". Consequences in **E11**. |
| V2 lockup power split | engine delivers a 20 s low-pass-filtered version of positive wheel demand, clipped to what it can make at the road-imposed crank speed; motor fills the balance either way | a plausible i-MMD supervisor. Sizing conclusions are not sensitive to the time constant; the split between generator and direct path is. |
| Engine full-load curve | interpolated, anchored on 700 Nm @ 1,600 rpm and ~153 kW peak @ 2,400 rpm | only used for V2 direct-path capability. **This assumption turns out to decide a headline conclusion** — see §4.5 and **E3**. |
| Genset rating basis | "110 kW" and "50 kW" read as **engine shaft** power | the baseline does not say. The alternative reading (generator electrical output) is 6 kW easier — see **E15**. |
| Analysis rate | 10 Hz | 1 Hz sampling understates peak wheel power by 1–2% and peak regen by 5–11% (§4.7). CSVs exported at both rates. |
| Every efficiency | a single **peak-point scalar** | there is no part-load map anywhere in the model, and the study's own results put both machines at part load for most of both cycles. Quantified in §4.14; **every efficiency-derived number in this report is therefore a best case** — see **E22**. |
| Ambient, altitude | **not declared** | ρ = 1.20 kg/m³ implies sea level; nothing else is stated. §4.15 shows a cold pack raises V1's ② by 48% and sends all 3.6 kWh of VOLT-SUB braking to the friction brakes. See **E21**. |
| Chassis geometry (adhesion check only) | wheelbase 4.20 m, CoG 1.20 m loaded / 1.00 m empty, static rear-axle share 0.65 at GVW / 0.48 at curb | needed because regen and launch both act through one axle (§4.16, **E23**). |

### 1.3 Definition of "power at the wheels"

Throughout,

&nbsp;&nbsp;&nbsp;&nbsp;`P_wheel = ( λ·m·a + ½ρ·CdA·v² + Crr·m·g·cosθ + m·g·sinθ ) · v`

with grade quoted as tan θ. It **includes rotating inertia**, so it is the
power the driveline must source at (or absorb from) the hubs — the right
basis for sizing a traction motor, and about 4% above pure road-load power
during acceleration.

Positive = propulsion. Negative = the vehicle is driving the driveline;
its magnitude is the braking power *presented at the wheel*, before any
absorb limit. Where a number describes what the **machine actually sees**,
the 75 kW absorb cap and the low-speed blend-out are applied first; those
are labelled explicitly.

### 1.4 The two reference cycles — and what they do not cover

These are **constructed cycles, not replays of a certified cycle**. Each is
built by forward-integrating a driver model (force-limited at low speed,
power-limited above the corner speed, tapering as the target is approached,
with per-leg variation in launch aggression and braking rate) over an
explicit list of route legs. They are parameterised so their *statistics* —
stop density, average speed, idle fraction, speed range — sit inside the
band spanned by published heavy-vehicle city/parcel and regional cycles
(HTUF Class 4 parcel delivery, CSHVR, HD-UDDS, Orange County Bus, WHVC).
**No published cycle's numbers are quoted here as fact**; those cycles were
used only as a qualitative target band. Everything is seeded and
reproducible.

**Cycle A — "VOLT-SUB"** (suburban postal/parcel, V1 duty). One route block:
3,485 s, 19.82 km, 20.5 km/h average (36.8 km/h moving), max 50 km/h,
30 stops = **1.51 stops/km**, 44.3% stationary. Composition: delivery drops
at 30–50 km/h with 62–78 s dwells, traffic stops at 45 km/h with ~18 s
dwells, collector-road runs and two depot transits. Launch ≈ 1.15 m/s²
tapering with speed; service braking 1.25 m/s² ±28% per stop. Assumed flat.

**Cycle B — "VOLT-REG"** (mixed regional trucker, V2 duty). 6,614 s,
131.96 km, 71.8 km/h average, max 100 km/h, 17 stops = 0.13 stops/km,
8.0% stationary.
Six phases: urban depot egress → rural arterial → highway outbound →
rest stop → highway return → rural → urban delivery drops. The grade
profile is a function of distance (three sinusoids plus four flat-topped
raised-cosine hill features), de-meaned so **net elevation change is exactly
zero** and scaled so the peak is exactly **6%**. Result: −6.00% to +5.87%,
752 m of total climb and 752 m of descent, 2.53 km of continuous grade
steeper than 4% and 5.28 km steeper than 3%. Grade is attenuated ×0.3 in
the urban phases.

**Composition by speed band** (this is what "mixed" actually means here):

| Band | VOLT-SUB time / distance | VOLT-REG time / distance |
|---|---|---|
| stationary | 47.9% / 0.4% | 9.3% / 0.0% |
| 5–50 km/h | 52.1% / 99.6% | 11.2% / 5.4% |
| 50–80 km/h | — | 25.3% / 24.7% |
| 80–100 km/h | — | 54.1% / 69.9% |

**Four limitations to carry forward, none of which is hidden by the
analysis:**

1. **VOLT-SUB is hard-capped at 50 km/h** because the assignment specifies
   0–50 km/h for the postal duty. Real parcel routes include 60–90 km/h
   depot transits, which would raise V1's motor speed range and its
   highway-cruise genset load. See **E14**.
2. **VOLT-REG is highway-dominated** — 70% of its distance is above
   80 km/h and only 5% is urban. That is a legitimate reading of "sustained
   85–100 km/h highway", but it means the cycle under-exercises the series
   path, which is what sizes the genset and the traction motor. A more
   urban-weighted regional duty moves V2's numbers toward the
   forced-series column of §3.
3. **Grade and speed are statistically independent.** The demand trace is
   generated flat and the grade profile layered on afterwards, so the
   driver never lifts for a hill. This is deliberate — the demand trace is
   what the *driver* asks for — and the gap is closed separately by the
   capability-limited forward simulation in §4.9. But it does mean the
   cycles never place a **stop on a grade**, so zero-speed holding torque
   (a real thermal case for a PM machine) is structurally invisible to
   every cycle statistic here. See **E16**.
4. **Every extremum is a draw, not a cycle property.** Across an
   eight-member seed ensemble that includes the published reference cycle,
   VOLT-SUB's peak wheel power runs 64.8–71.4 kW, P99 53.6–59.6 kW, braking
   energy 3.55–3.63 kWh, ③ 0.71–0.87 kWh and ④ 121–133 kW; VOLT-REG's peak
   power runs 163.7–188.1 kW, P99 140.9–147.2 kW, ③ 1.12–1.38 kWh and
   ④ 145–198 kW. **The published reference cycle is the ensemble *minimum*
   for ④ on both cycles and for ③ on VOLT-SUB**, so §3 and §7 report those
   as ensemble envelopes, not as the reference draw. Energy per km, by
   contrast, is stable to ±0.4% — it is the extrema that move.

---

## 2. Results table

All at GVW 6,600 kg, at the wheels, 10 Hz. Figures: `figs/fig01`, `fig02`
(traces), `fig03` (time-at-power), `fig10` (speed–power operating maps).

### 2.1 Power and energy at the wheels

| Quantity | VOLT-SUB | VOLT-REG |
|---|---|---|
| **Peak power** | **67.4 kW** | **163.7 kW** |
| **Average power** (tractive, over the whole cycle) | **9.2 kW** | **42.9 kW** |
| Average power (net of ideal regen) | 5.5 kW | 40.4 kW |
| **95th-percentile power** (time-weighted, whole cycle) | **43.4 kW** | **99.2 kW** |
| 95th percentile over moving time only | 49.4 kW | 100.1 kW |
| 99th percentile | 54.8 kW | 144.2 kW |
| RMS wheel power | 22.5 kW | 56.0 kW |
| Tractive energy | 8.92 kWh | 78.85 kWh |
| **Energy per km** (tractive, at the wheel) | **0.450 kWh/km** | **0.598 kWh/km** |
| Energy per km net of ideal (unlimited, lossless) regen | 0.268 kWh/km | 0.562 kWh/km |
| **Total braking energy** | **3.61 kWh** | **4.65 kWh** |
| — per km | 0.182 kWh/km | 0.035 kWh/km |
| — as % of tractive energy | **40.5%** | **5.9%** |
| Peak braking power presented at the wheel | 121.4 kW | 144.8 kW |
| **Recoverable fraction @ 75 kW absorb limit** (at the wheel) | **91.9%** | **91.0%** |
| — delivered to the DC bus (× 0.866 chain) | 79.5% | 78.8% |
| — recovered energy at the bus | 2.87 kWh | 3.67 kWh |
| — as % of tractive energy | 32.2% | 4.6% |

> **The peak, P99, braking-energy and peak-regen rows below are single
> realisations of a stochastic route generator.** Their ensemble ranges are
> in §4.8 and the design envelopes are in §3; do not size anything on the
> single draw. Energy per km, average power, P95 and the RMS figures are
> stable across realisations to a few tenths of a percent.

Note the "net of ideal regen" row is a physics bookkeeping figure, not a
consumption figure: over a closed cycle the inertia and grade integrals
cancel, so it is literally just aero + rolling. It assumes no cap, no
blend-out, no efficiency chain and no accessories, and it should not be
compared with a vehicle's quoted energy consumption.

The two cycles are **qualitatively different loads on the same hardware**.
VOLT-SUB throws 40% of its tractive energy into the brakes and almost none
of its power is sustained; VOLT-REG throws away 6% and almost all of its
power is sustained. Any single "average" that mixes them is misleading,
which is why §3 reports each case separately.

**Where the braking energy comes from** matters for WS5. On VOLT-SUB it is
99.99% decelerations (the cycle is flat). On VOLT-REG it is 83%
decelerations and only **17% steady-speed downgrade retardation** — because
at ~95 km/h the aero + rolling drag (≈2.34 kN) already balances gravity on
a **3.6% downgrade**, so every shallower descent needs no braking at all.
Only 4% of VOLT-REG's distance is on a downgrade steeper than neutral.
That is why a 132 km cycle with 752 m of descent yields 4.65 kWh of
braking energy — and it is also why the *sustained* 6% descent of §4.5 is
a completely different problem from the cycle.

### 2.2 Time-at-power histogram

Full tables in `data/time_at_power_VOLT-SUB.csv` and
`data/time_at_power_VOLT-REG.csv` (10 kW bins, seconds and % of cycle
time); plotted on a log scale in `figs/fig03_time_at_power.png`.

| Band | VOLT-SUB | VOLT-REG |
|---|---|---|
| stationary (v < 0.1 m/s) | 44.3% | 8.0% |
| 0 < P ≤ 30 kW | 37.8% | 24.2% |
| P > 30 kW | 8.70% | 60.11% |
| P > 50 kW | 2.58% | 40.25% |
| P > 75 kW | **0.00%** | 16.69% |
| P > 100 kW | 0.00% | 4.71% |
| P > 150 kW | 0.00% | 0.64% |
| P < 0 (braking) | 9.81% | 7.93% |
| P < −50 kW | 3.46% | 1.94% |
| P < −75 kW | 1.55% (54 s) | 0.95% (63 s) |
| P < −100 kW | 0.32% | 0.35% |

Two things fall out. **VOLT-SUB never asks for more than 67 kW of
propulsion but asks for more than 75 kW of *braking* for 54 s of every
hour** — the load is asymmetric, in the direction the electrical path is
worst at. And **VOLT-REG spends 17% of its time above 75 kW**, which is
the entire reason V2 needs a mechanical path.

### 2.3 Regen absorb-limit sweep

`figs/fig04_regen_sensitivity.png`, `data/regen_sweep_*.csv`.

| Absorb limit at the wheel | VOLT-SUB at wheel | VOLT-SUB to bus | VOLT-REG at wheel | VOLT-REG to bus |
|---|---|---|---|---|
| 20 kW | 36.5% | 31.6% | 43.4% | 37.5% |
| 40 kW | 64.9% | 56.2% | 68.3% | 59.1% |
| 50 kW | 75.4% | 65.3% | 77.0% | 66.7% |
| 60 kW | 83.5% | 72.3% | 83.8% | 72.6% |
| **75 kW (baseline)** | **91.9%** | **79.5%** | **91.0%** | **78.8%** |
| 90 kW | 96.3% | 83.3% | 95.5% | 82.7% |
| 100 kW | 97.6% | 84.5% | 97.3% | 84.3% |
| 150 kW | 98.3% | 85.1% | 99.3% | 85.9% |
| no limit | 98.3% | 85.1% | 99.3% | 85.9% |

**75 kW sits on the knee.** Doubling to 150 kW buys 6.4 points on VOLT-SUB
and 8.3 on VOLT-REG. The 1.7% that even an unlimited absorber cannot
recover on VOLT-SUB is the low-speed blend-out. Recommendation: keep 75 kW.
Note that it is the **cap**, not the blend-out, that dominates the loss (by
4.3× on VOLT-SUB and 11× on VOLT-REG), and that on VOLT-REG the cap costs
more the harder the drivers brake — the seed ensemble spans 157–198 kW of
peak demand (§4.8).

---

## 3. The Four Numbers

Three cases, because the shared electric spine has to serve all three: V1 on
its own cycle, V2 on its own cycle with the lockup working, and V2 with the
clutch never closing (limp mode, and also what a *pure*-series V2 looks
like).

| | V1 Postal on VOLT-SUB | V2 Trucker on VOLT-REG (i-MMD) | V2 on VOLT-REG (forced series) |
|---|---|---|---|
| **① Motor continuous** — thermal-equivalent RMS at the motor shaft | **21.7 kW** | **19.9 kW** | **57.2 kW** |
| same, if the machine had to absorb *all* braking (no 75 kW cap) | 22.6 kW | 20.8 kW | 57.5 kW |
| RMS **torque** at the motor shaft | 115 Nm | 71 Nm | 106 Nm |
| worst 60 s rolling RMS power | 35.5 kW | 60.3 kW | 155.9 kW |
| worst 300 s rolling RMS power | 26.6 kW | 34.5 kW | **124.8 kW** |
| worst 600 s rolling RMS power | 25.5 kW | 30.9 kW | 102.3 kW |
| worst 300 s rolling RMS torque | 145 Nm | 149 Nm | 174 Nm |
| **② Genset average** — constant SOC-neutral output at the DC bus | **10.1 kW** | **9.7 kW** | **50.6 kW** |
| same, referred to the engine shaft (÷0.94) | 10.8 kW | 10.4 kW | 53.8 kW |
| average direct-path shaft power (lockup) | — | 36.6 kW | — |
| **total average engine shaft power** | **10.8 kW** | **47.0 kW** | 53.8 kW |
| **③ Battery buffer** — max 5-min swing, this realisation | **0.71 kWh** | **1.29 kWh** | **7.32 kWh** |
| ③ over the 8-seed ensemble (this cycle is the *minimum* on VOLT-SUB) | **0.87 kWh** | **1.38 kWh** | — |
| same, one genset setpoint for the whole cycle | 1.13 kWh | 3.40 kWh | 20.80 kWh |
| **④ Peak regen** — presented at the wheel, this realisation | **121.4 kW** | **144.8 kW** | 144.8 kW |
| ④ design envelope over seeds and braking styles (§4.8) | **161 kW** | **198 kW** | 198 kW |
| absorbed with the 75 kW cap: wheel / DC bus / motor shaft | 75 / 64.9 / 72.8 kW | 75 / 64.9 / 72.8 kW | 75 / 64.9 / 72.8 kW |
| Peak motoring power at the motor shaft | 69.4 kW | 111.0 kW | 168.7 kW |
| Peak wheel power over the 8-seed ensemble | 71.4 kW | 188.1 kW | 188.1 kW |
| Peak battery discharge / charge | 71.9 / 70.8 kW | 120.3 / 70.5 kW | 144.8 / 110.1 kW |

Lockup is closed for **69.2% of the time and 84.7% of the distance** on
VOLT-REG, and **81.1% of the tractive energy (64.0 of 78.9 kWh) goes down
the direct mechanical path** rather than through the electrical spine.
That single fact collapses V2's generator duty from 50.6 kW to 9.7 kW and
its motor RMS from 57.2 kW to 19.9 kW.

### 3.1 ① is computed as asked, and must not be used on its own

`√(mean(P_motor²))` over the whole cycle including stationary time, on the
motor's own shaft power (wheel power ÷ 0.97 motoring, × 0.97 generating),
signed power squared so regen heating counts, and with the 75 kW absorb cap
and blend-out applied first — the friction brakes do the rest of the
braking, so the machine must not be charged with it. **Three separate
things break it as a rating:**

1. **It averages over the wrong horizon.** A liquid-cooled machine of this
   size has a winding time constant of minutes, not the 58 / 110 minutes of
   these cycles. The worst 300 s rolling RMS is 26.6 kW (V1), 34.5 kW (V2
   i-MMD) and **124.8 kW** (V2 forced series) — 1.2×, 1.7× and 2.2× the
   full-cycle figures (`figs/fig06`).
2. **RMS *power* is not a thermal equivalent, and it reverses the ranking.**
   Copper loss scales as torque², and with a fixed 10:1 ratio the motor
   spans 0–3,585 rpm on VOLT-SUB but 0–7,169 rpm on VOLT-REG, so
   `mean(T²ω²)` weights identical copper heating by ω². By RMS power the
   two duties look equal (21.7 vs 19.9 kW). By **RMS torque they are not:
   115 Nm vs 71 Nm — the suburban duty is 61% heavier in copper terms.**
   Referred to the corner speed the baseline itself implies (13.5 kN to
   20 km/h = 1,434 rpm), the copper-equivalent continuous ratings are
   17.2 kW (SUB), 10.7 kW (REG i-MMD) and 15.9 kW (REG series-only).
   **WS2 should size on RMS torque and a real loss model, not on ①.**
3. **The sizing case is not in either cycle.** The baseline requires V2 to
   "hold 60 km/h loaded on 6% grade with a depleted battery". That is a
   *series* operating point (61 km/h is below the lockup speed), it needs
   87.8 kW at the wheel = **90.5 kW / 198 Nm at the motor shaft for the
   ~10 minutes of a 10 km climb**, and no drive-cycle RMS will ever show
   it. For V1 on 6% the same calculation gives 40.2 kW / 177 Nm. At 20%
   grade both variants converge on **~510 Nm at the motor shaft** — exactly
   the baseline's 13.5 kN tractive spec, now demanded *continuously* at
   10.6 km/h (V1) or 23.6 km/h (V2) with almost no cooling airflow.

**WS1's recommendation to WS2 is a duty-rating triple, not a single
number:**

| Rating | Value at the motor shaft | Set by |
|---|---|---|
| S1 continuous (indefinite) | **≥ 45 kW / ≥ 180 Nm** | worst rolling RMS on VOLT-SUB (26.6 kW / 145 Nm) and VOLT-REG i-MMD (34.5 kW / 149 Nm) with margin; V1 6% grade hold (40.2 kW / 177 Nm) |
| S2 10-minute | **≥ 95 kW / ≥ 200 Nm** | V2 6% grade hold in series at 61 km/h (90.5 kW / 198 Nm); worst 600 s rolling RMS in forced series is 102.3 kW |
| S2 1-minute / peak | **≥ 120 kW, target 150 kW; ≥ 515 Nm below 20 km/h; 7,200 rpm max** | VOLT-REG i-MMD peak 111.0 kW; the 13.5 kN launch spec = 515 Nm at the shaft; 100 km/h through 10:1 = 7,169 rpm |
| Generating envelope | **73 kW / 370 Nm** | the 75 kW wheel cap sets the power; peak braking torque (370 Nm at ~8 km/h) occurs where the cap does not bind |

If the spine must also survive a **clutch-open fault** on VOLT-REG, S2-10 min
rises from 95 kW to **125 kW** and the peak to 170 kW. That is undecided —
see **E24**; it is the single choice with the largest effect on the machine.

**② for V2 needs reading carefully.** The generator averages only 9.7 kW
because the mechanical path carries the highway load; the *engine* averages
47.0 kW of shaft power. With the clutch never closing, the genset would
have to average 50.6 kW electrical (53.8 kW shaft) — a five-fold difference
that comes entirely from the lockup decision. **Neither number sizes the
genset**: V2's genset is set by the 6% grade floor and V1's by grade
capability plus how often you are willing to start it (**E6**).

**③ is dominated by grades and by genset duty cycling, not by the cycle**
(§4.4, §4.6, **E6**, **E7**), it is an energy number for a pack whose real
constraint is power (**E8**), and the demands on it are concurrent rather
than alternative (**E7**). Note also that the literal answer to
"the genset at constant output" is the **full-cycle** swing (1.13 / 3.40 /
20.80 kWh); the 5-minute window implicitly assumes the genset setpoint may
be re-trimmed on a ~5-minute SOC loop. Both are tabulated in §4.10, and
the number grows monotonically with the window, so the answer depends on
the control law you assume rather than on the vehicle.

**④ is a *demand*, not an absorbed power, and it is a random variable.**
This realisation presents 121 kW (VOLT-SUB) and 145 kW (VOLT-REG) at the
wheel; across seven route realisations and the braking-style sweep the
design envelope is **161 kW and 198 kW** (§4.8). With the cap the
electrical path never
sees more than 75 kW at the wheel = 72.8 kW at the motor shaft = 64.9 kW at
the DC bus. The difference is friction braking on every hard stop.

---

## 4. Sensitivities

### 4.1 Payload ±20%

Payload at GVW is 2,900 kg, so ±20% is ±580 kg → 6,020 / 7,180 kg. The
empty-curb case (3,700 kg) is included because a delivery truck spends the
back half of its shift there. Speed traces are held fixed; only the loads
change.

**VOLT-SUB**

| Load case | Mass | E/km | Peak | P95 | Braking energy | ① RMS | ② genset | ③ buffer | ④ peak regen |
|---|---|---|---|---|---|---|---|---|---|
| empty curb | 3,700 kg | 0.297 kWh/km | 38.6 kW | 25.6 kW | 1.98 kWh | 13.3 kW | 7.6 kW | 0.53 kWh | 66.0 kW |
| payload −20% | 6,020 kg | 0.419 kWh/km | 61.6 kW | 39.8 kW | 3.29 kWh | 20.2 kW | 9.5 kW | 0.68 kWh | 110.3 kW |
| **GVW** | **6,600 kg** | **0.450 kWh/km** | **67.4 kW** | **43.4 kW** | **3.61 kWh** | **21.7 kW** | **10.1 kW** | **0.71 kWh** | **121.4 kW** |
| payload +20% | 7,180 kg | 0.481 kWh/km | 73.1 kW | 46.9 kW | 3.94 kWh | 23.1 kW | 10.7 kW | 0.74 kWh | 132.5 kW |

**VOLT-REG**

| Load case | Mass | E/km | Peak | P95 | Braking energy | ① RMS | ② genset | ③ buffer | ④ peak regen |
|---|---|---|---|---|---|---|---|---|---|
| empty curb | 3,700 kg | 0.506 kWh/km | 111.6 kW | 77.2 kW | 1.91 kWh | 12.0 kW | 7.1 kW | 1.00 kWh | 69.1 kW |
| payload −20% | 6,020 kg | 0.578 kWh/km | 153.1 kW | 94.7 kW | 4.00 kWh | 18.2 kW | 9.0 kW | 1.23 kWh | 129.6 kW |
| **GVW** | **6,600 kg** | **0.598 kWh/km** | **163.7 kW** | **99.2 kW** | **4.65 kWh** | **19.7 kW** | **9.5 kW** | **1.29 kWh** | **144.8 kW** |
| payload +20% | 7,180 kg | 0.617 kWh/km | 174.3 kW | 103.7 kW | 5.32 kWh | 21.3 kW | 10.1 kW | 1.53 kWh | 159.9 kW |

Reading (`figs/fig08`): **±20% payload is ±3–7% on energy per km, ±6–8% on
peak power and on ①, ±6% on ②, ±10% on ④** — mass moves the inertial terms
linearly while aero does not move at all. **Mass sensitivity is mild; grade
sensitivity (§4.4–4.5) is not.** The empty case is the interesting one:
energy per km drops 34% on VOLT-SUB, so range and fuel figures quoted at
GVW are pessimistic for the second half of a shift.

### 4.2 Accessory load (0.5 / 2.0 / 4.0 kW)

Moves ② one-for-one at the bus (VOLT-SUB 8.6 / 10.1 / 12.1 kW; VOLT-REG
8.1 / 9.5 / 11.5 kW) and leaves ③ untouched (<0.1%), because a constant
load shifts the genset setpoint by the same amount and cancels. On
VOLT-SUB a 4 kW hot-day accessory load is **40% of the entire genset
average** — accessory electrification is a first-order genset-sizing input
for V1, not a detail. It also erodes the V2 grade floor: at 4 kW of
accessories the 110 kW engine holds 60.4 km/h on 6%, not 61.0.

### 4.3 Dwell time (×0.5 … ×2.0 of assumed delivery dwells)

The least certain cycle-construction input, so it gets its own sweep.

| Dwell scale | Duration | Distance | Avg speed | Stationary | E/km | ① | ② | ③ |
|---|---|---|---|---|---|---|---|---|
| ×0.5 | 3,379 s | 23.90 km | 25.5 km/h | 29.7% | 0.456 kWh/km | 24.6 kW | 12.1 kW | 0.59 kWh |
| **×1.0** | 3,485 s | 19.82 km | 20.5 km/h | 44.3% | 0.450 kWh/km | 21.7 kW | 10.1 kW | 0.71 kWh |
| ×1.5 | 3,539 s | 17.22 km | 17.5 km/h | 52.6% | 0.442 kWh/km | 19.5 kW | 8.9 kW | 0.78 kWh |
| ×2.0 | 3,581 s | 15.08 km | 15.2 km/h | 59.8% | 0.428 kWh/km | 17.5 kW | 7.9 kW | 0.98 kWh |

Every row is a route block of comparable duration over the same segment
mix; only the standing time changes, so fewer stops are completed as the
dwell grows (which is what actually happens on a route). **Energy per km is
insensitive to dwell (0.428–0.456 kWh/km, ±3%)** — it is a property of the
driving, not the standing. Every *time-averaged* number is strongly
dwell-sensitive: ② moves +19/−22% and ③ moves +38/−16%. This is the
clearest argument for quoting V1's genset requirement per km and per grade
rather than as a cycle average.

### 4.4 One sustained 10 km climb at 6%, at GVW

Elevation gain 600 m; potential energy alone 10.79 kWh.

| Speed held | Wheel power | DC bus | Engine shaft, series | Engine shaft, direct | Crank rpm locked | Engine capability at that rpm |
|---|---|---|---|---|---|---|
| 40 km/h | 53.0 kW | 61.2 kW | 65.1 kW | 55.8 kW | 803 | 36.6 kW |
| 50 km/h | 68.7 kW | 79.4 kW | 84.4 kW | 72.3 kW | 1,004 | 56.9 kW |
| 60 km/h | 86.0 kW | 99.3 kW | 105.7 kW | 90.5 kW | 1,204 | 79.6 kW |
| 70 km/h | 105.2 kW | 121.6 kW | 129.3 kW | 110.8 kW | 1,405 | 100.9 kW |
| 85 km/h | 138.5 kW | 160.0 kW | 170.2 kW | 145.8 kW | 1,706 | 125.1 kW |
| 100 km/h | 177.9 kW | 205.5 kW | 218.6 kW | 187.2 kW | 2,007 | 143.8 kW |

Forward-simulating the climb with real limits (`figs/fig07`):

| Configuration | Settled speed on the 6% | Time for the 10 km | Buffer exhausted after |
|---|---|---|---|
| V2, 110 kW genset, energy-unlimited battery | 85.0 km/h | 438 s | — |
| V2, 110 kW genset, 2.0 kWh usable buffer | **61.0 km/h** | 555 s | 105 s |
| V2, 110 kW genset, 5.0 kWh usable buffer | 61.0 km/h | 463 s | 330 s |
| V1, 50 kW genset, 2.0 kWh usable buffer | **30.2 km/h** | 1,132 s | 40 s |

The forward simulation settles on **exactly** the closed-form sustained
speeds (61.0 and 30.2 km/h, §6.6) — an independent check that the
capability model and the road-load model agree.

Holding 85 km/h for the whole climb needs 138.5 kW at the wheel. The direct
path can make 118.8 kW, but the accessories are fed off the same crankshaft
through the generator, so 2.0 kW at the bus costs 2.0 kW at the wheel and
only **116.8 kW** reaches the road. The 21.7 kW deficit is **25.0 kW drawn
from the DC bus for 424 s = 2.94 kWh at the bus, 3.04 kWh at the cells**. That is more than a 2 kWh buffer holds,
so **holding 85 km/h up a 10 km 6% grade is not achievable on any buffer
this study contemplates** — which is what the forward simulation shows: the
2 kWh buffer is spent after 105 s, the truck is through the lockup floor
by ~170 s, and it settles at 61.0 km/h in series for the rest of the climb.

### 4.5 Can the 2.8:1 direct path hold 6% at all? It depends on the engine

Comparing the last two columns of the table above, the reference engine
**cannot** meet its own direct-path demand on 6% at any speed — the
smallest deficit is 9.3 kW at ~70 km/h. But that conclusion is knife-edge
and it turns on the shape of the torque curve below 1,600 rpm, which the
baseline does not specify:

| Full-load torque curve | Torque @1,600 rpm | Peak power | Best grade held alone | at | Holds 6%? |
|---|---|---|---|---|---|
| WS1 reference 4HK1 | 700 Nm | 153 kW | 5.25% | 70 km/h | no (short by 9.3 kW) |
| 700 Nm held flat from 1,200 rpm | 700 Nm | 153 kW | 5.81% | 60 km/h | no (short by 2.0 kW) |
| torque peak 750 Nm @ 1,400 rpm | 700 Nm | 152 kW | 6.03% | 60 km/h | **yes, 59–67 km/h** |
| high-rpm biased | 700 Nm | 163 kW | 4.98% | 74 km/h | no (short by 12.8 kW) |

All four curves honour the baseline's two published anchors. **So the
correct statement is not "the direct path cannot hold 6%" but "whether it
can is decided by the engine's torque below 1,600 rpm, and the reference
engine cannot."** That converts a physics claim into an engine
*specification requirement* for WS4 — see **E3**.

### 4.6 The same 10 km at −6% (not asked for; it is the harder half)

| Descent speed | Retardation demanded | Duration | Energy to dissipate | Crank rpm if locked |
|---|---|---|---|---|
| 25 km/h | 22.0 kW | 1,440 s | **8.82 kWh** | 502 — *below idle* |
| 35 km/h | 29.7 kW | 1,029 s | 8.49 kWh | 703 — *at idle* |
| 40 km/h | 33.2 kW | 900 s | 8.29 kWh | 803 |
| 50 km/h | 39.0 kW | 720 s | 7.81 kWh | 1,004 |
| 60 km/h | 43.3 kW | 600 s | 7.21 kWh | 1,204 |
| 70 km/h | 45.6 kW | 514 s | 6.51 kWh | 1,405 |
| 85 km/h | 44.7 kW | 424 s | 5.25 kWh | 1,706 |
| 100 km/h | 37.5 kW | 360 s | 3.75 kWh | 2,007 |

**A slower descent is worse**, because less of the gravitational input goes
into aero drag — and a loaded 6.6 t truck on a sustained 6% grade descends
slowly. The retardation *power* never exceeds 46 kW, comfortably inside the
75 kW absorb limit; the problem is entirely the **energy sink**.

And there is a floor under the remedy. Idle at 700 rpm through 2.8:1 is
**34.9 km/h**; below that the clutch must open, so neither engine drag nor
an exhaust brake exists at all — in exactly the speed range where the
energy to dissipate is largest. A truck descending 6% behind slower traffic
at 30 km/h has **no** retardation available beyond regen and the friction
brakes, and 8.8 kWh to get rid of.

Friction-brake energy and adiabatic rotor temperature rise (60 kg of iron),
with the buffer starting at the supervisor's 55% SOC target — so only 45%
of it is available as regen headroom — and accessories drawing 2 kW
throughout:

| Usable buffer | 30 km/h, any retarder¹ | 60 km/h, no engine brake | 60 km/h, +30 kW exhaust brake | 85 km/h, no engine brake | 85 km/h, +30 kW exhaust brake |
|---|---|---|---|---|---|
| 2 kWh | **6.83 kWh / 891 K** | 5.75 kWh / 751 K | 0.75 kWh / 98 K | 3.91 kWh / 510 K | 0.38 kWh / 50 K |
| 3 kWh | 6.29 kWh / 821 K | 5.22 kWh / 681 K | 0.22 kWh / 29 K | 3.37 kWh / 440 K | **0 kWh** |
| 4 kWh | 5.76 kWh / 751 K | 4.68 kWh / 611 K | **0 kWh** | 2.84 kWh / 370 K | 0 kWh |
| 6 kWh | 4.68 kWh / 611 K | 3.61 kWh / 471 K | 0 kWh | 1.77 kWh / 230 K | 0 kWh |
| 8 kWh | 3.61 kWh / 471 K | 2.54 kWh / 331 K | 0 kWh | 0.69 kWh / 91 K | 0 kWh |

¹ At 30 km/h the crank would be below idle, so the clutch is open and an
exhaust brake is unavailable — the "with retarder" and "without" columns
are identical, and no plausible buffer closes the gap.

The ΔT figures are adiabatic upper bounds (no convective cooling), so treat
them as an ordering, not a prediction. The ordering is unambiguous: **on any
buffer-sized pack, and without a dedicated retarder, a sustained 6% descent
puts several kWh into the friction brakes.** Reading down the "30 kW
exhaust brake" columns, an exhaust brake plus a 3–4 kWh buffer closes the
problem *above 35 km/h*; nothing else in the current architecture does,
because there is no gearbox to downshift into and at 85 km/h the locked
engine sits at 1,706 rpm where pumping losses alone are worth only ~10 kW.
Below 35 km/h nothing in the architecture helps at all. See **E4**.

### 4.7 Regen blend-out, driver braking style, sampling rate

Blend-out 8→3 km/h costs 1.9% of braking energy on VOLT-SUB and 0.8% on
VOLT-REG; widening to 12→5 km/h costs 4.5% and 2.0%. Not a first-order
lever — the 75 kW cap costs 4.3× to 11× more.

Braking aggression on VOLT-SUB: at 0.9 m/s² nominal, peak regen demand is
89.9 kW and the 75 kW limiter still recovers 98.1% of braking energy; at
1.25 m/s², 121.4 kW and 91.9%; at 1.6 m/s², 161.3 kW and 84.7%. **④ is a
property of the driver, not of the vehicle**, and should be specified as a
design envelope.

1 Hz vs 10 Hz sampling: peak wheel power −2.1% / −1.2% (SUB/REG), peak
regen −10.8% / −5.4%, RMS −2.4% / −0.3%, energy per km −0.7% / −0.1%.
Cycles exchanged at 1 Hz will systematically under-report peaks.

### 4.8 Cycle-construction robustness

Seven seeds (route order reshuffled, driver variation re-drawn): VOLT-SUB
energy per km 0.446–0.451 kWh/km, ① 21.4–21.9 kW, ② 9.96–10.14 kW,
③ 0.72–0.87 kWh, ④ 122–133 kW. VOLT-REG: energy per km 0.600–0.603,
① 19.0–19.6 kW, ② 8.82–9.58 kW, ③ 1.12–1.38 kWh, **④ 157–198 kW**.
Everything except ④ is stable to a few percent. **④ is not a cycle
property at all** — it is set by whichever single hardest stop a
realisation happens to contain, and the reference cycle's draw (145 kW on
VOLT-REG) sits *below* the ensemble. WS1 therefore reports ④ as an
envelope: the maximum over the reference cycle, the seven-seed ensemble and
the braking-style sweep, which is **161 kW (VOLT-SUB)** and **198 kW
(VOLT-REG)** at the wheel. Those are the numbers WS5 should design the
brake blend against.

Adding ±1.5% rolling suburban terrain to VOLT-SUB (net zero) changes energy
per km by −0.3%, ① by +2%, ③ by +3% and ④ by +7%. The flat assumption is
safe.

### 4.9 Can the vehicle actually drive the cycle?

Forward simulation of VOLT-REG with a 110 kW genset, a 120 kW battery and
the SOC-regulating supervisor (`figs/fig09`):

| Configuration | Distance vs demand | Worst speed deficit | Buffer minimum |
|---|---|---|---|
| 150 kW motor, energy-unlimited battery | −0.000% | 0.2 km/h | — |
| 150 kW motor, 2.0 kWh usable buffer | −0.000% | 0.2 km/h | 0.43 kWh |
| **75 kW motor** (baseline minimum), 2.0 kWh buffer | −0.05% | **9.5 km/h** | 0.43 kWh |

VOLT-REG's grades are steep but short (longest continuous run above 4% is
2.53 km), so a 2 kWh buffer survives them with 0.43 kWh to spare. **The
cycle does not expose the sustained-grade problem — §4.4 and §4.6 do.** V1
on VOLT-SUB with a 50 kW genset and a 1.5 kWh buffer tracks its cycle with
a 0.24 km/h worst deficit and never drops below 0.80 kWh.

### 4.10 Buffer vs how often the genset setpoint may move

| Genset re-trim window | V1 on VOLT-SUB | V2 on VOLT-REG (i-MMD) | V2 on VOLT-REG (series only) |
|---|---|---|---|
| 1 min | 0.33 kWh | 0.96 kWh | 2.16 kWh |
| 2 min | 0.48 kWh | 1.04 kWh | 4.02 kWh |
| **5 min (the assignment)** | **0.71 kWh** | **1.29 kWh** | **7.32 kWh** |
| 10 min | 0.82 kWh | 1.46 kWh | 9.90 kWh |
| 20 min | 0.99 kWh | 1.80 kWh | 14.11 kWh |
| whole cycle (literally constant) | 1.13 kWh | 3.40 kWh | 20.80 kWh |

There is no plateau, so ③ is a statement about the control law rather than
about the vehicle. `figs/fig05`.

### 4.11 Road-load coefficients (challenge to a baseline input)

CdA = 4.2 m² and ρ = 1.20 kg/m³ are both at the optimistic end, and ρ was
chosen to reproduce a baseline answer rather than measured. A 16 ft
dry-freight box on an NPR cab plausibly presents CdA 4.6–5.6 m².

| CdA / ρ | 85 km/h cruise | VOLT-SUB E/km | VOLT-REG E/km | VOLT-REG P95 | V2 6% hold speed |
|---|---|---|---|---|---|
| **4.2 / 1.20 (baseline)** | **46.9 kW** | **0.450** | **0.598** | **99.2 kW** | **61.0 km/h** |
| 4.2 / 1.225 | 47.6 kW | 0.452 | 0.605 | 100.2 kW | 60.8 km/h |
| 4.8 / 1.20 | 51.7 kW | 0.464 | 0.652 | 106.0 kW | 60.1 km/h |
| 5.4 / 1.20 | 56.4 kW | 0.479 | 0.707 | 112.8 kW | 59.2 km/h |
| 5.4 / 1.225 | 57.3 kW | 0.482 | 0.717 | 114.2 kW | 59.1 km/h |

A CdA of 5.4 m² costs **+18% on VOLT-REG energy per km and +16% on P95**,
and quietly breaks the baseline's "60 km/h on 6%" claim (59.1 km/h). It
barely touches the city cycle (+7%). See **E13**.

### 4.12 The 6% grade floor, swept — the requirement that actually sizes the genset

§4.1 sweeps payload over the two *cycles*. The requirement that sizes the V2
genset is not in either cycle, so it gets its own sweep. Engine shaft power
needed to hold 60 km/h on 6%, and the speed a 110 kW engine actually holds:

| Condition | Shaft needed | Margin on 110 kW | Speed held |
|---|---|---|---|
| **GVW, 2 kW aux, CdA 4.2 (the quoted case)** | **107.8 kW** | **+2.2 kW** | **61.0 km/h** |
| GVW, 4 kW aux, CdA 4.2 | 109.9 kW | +0.1 kW | 60.0 km/h |
| GVW, 6 kW aux, CdA 4.2 | 112.1 kW | −2.1 kW | 59.1 km/h |
| GVW, 2 kW aux, CdA 5.4 | 111.9 kW | −1.9 kW | 59.2 km/h |
| GVW, 4 kW aux, CdA 5.4 | 114.0 kW | −4.0 kW | 58.3 km/h |
| **+20% payload, 2 kW aux, CdA 4.2** | **115.8 kW** | **−5.8 kW** | **57.5 km/h** |
| +20% payload, 4 kW aux, CdA 5.4 | 122.1 kW | −12.1 kW | 55.2 km/h |
| curb, 2 kW aux, CdA 4.2 | 67.7 kW | +42.3 kW | 82.6 km/h |

**The 110 kW floor is confirmed only at GVW, nominal accessories and the
fitted road load, with 2% margin — and each of this study's own sensitivity
cases consumes all of it.** The +20% payload case that §4.1 treats as
routine misses the requirement by 5.8 kW; a 4 kW hot-day accessory load
leaves exactly zero; CdA 5.4 already fails. See **E19**.

### 4.13 What the engine actually does on the locked path

The whole justification for the 2.8:1 direct path — and therefore for V2's
existence — is that a 95% mechanical path beats an 81.4% electrical one.
That comparison is only valid if the engine is equally efficient at both
operating points, and a single fixed ratio guarantees it is not: in lockup
the crank speed is set by the road.

| Road speed | Crank rpm | Shaft needed (flat, GVW) | Shaft available | Load fraction |
|---|---|---|---|---|
| 60 km/h | 1,204 | 22.5 kW | 79.6 kW | **28%** |
| 70 km/h | 1,405 | 31.4 kW | 100.9 kW | 31% |
| 85 km/h | 1,706 | 49.4 kW | 125.1 kW | 39% |
| 100 km/h | 2,007 | 73.9 kW | 143.8 kW | 51% |

Over the 4,576 s VOLT-REG spends locked, the engine's median load fraction
is **48%**; it is below 50% for 55% of that time and below 30% for 16% of
it, at 1,414–2,005 rpm (5th–95th percentile). A free-running genset can be
pinned to its BSFC island by definition — which is exactly what the
baseline instructs WS4 to do. The locked path cannot. WS1 does not own a
BSFC map, so **the 95% vs 81.4% comparison is a component-efficiency
argument that assumes equal engine efficiency at both operating points, and
the fixed ratio makes that assumption false.** See **E20**.

### 4.14 Part-load efficiency — every efficiency here is a peak-point scalar

`volt_params.py` applies gen 0.94, PE 0.97, inverter+motor 0.92, reduction
0.97 at *every* operating point. The study's own results say the machines
live at part load: the traction motor is below 25% of its rating for
**85% of VOLT-SUB and 93% of VOLT-REG**, and V1's genset averages 10.1 kW
on a ~50 kW installed rating. Applying a crude derate (full efficiency
above 50% load, falling linearly to 0.88 × nominal at 5% load):

| | VOLT-SUB (V1) | VOLT-REG (V2) |
|---|---|---|
| Bus energy, peak-point efficiencies | 10.30 kWh | 17.20 kWh |
| Bus energy, part-load derate | 11.02 kWh | 18.66 kWh |
| Traction energy penalty | **+7.0%** | **+8.5%** |
| Regen delivered to the bus | 2.87 → 2.83 kWh | 3.67 → 3.52 kWh |
| ② at the engine shaft | 10.3 → **12.0 kW** | 10.0 → **12.2 kW** |
| ② penalty | **+16.8%** | **+22.4%** |

The bias is systematic and one-directional on every kWh/km, on ②, on ③ and
on the 79.5%/78.8% regen-to-bus fractions. It also cuts back on **E5**:
81.4% is an *upper bound* on the series chain, not its operating value —
which strengthens **E6**'s case for start-stop over continuous part-load
running. See **E22**.

### 4.15 Environmental envelope — cold, hot, and the absence of a declaration

The Four Numbers are otherwise quoted at a single implied ambient and at
sea level.

| Case | V1 ② | V1 friction-brake energy | V1 regen to bus | V2 ② | V2 friction-brake energy |
|---|---|---|---|---|---|
| **nominal** (2 kW aux, 75 kW regen) | **10.1 kW** | **0.29 kWh** | **2.87 kWh** | **9.7 kW** | **0.42 kWh** |
| cold: regen disabled, 4 kW aux | 15.0 kW (+48%) | **3.61 kWh** | 0 | 13.7 kW (+41%) | **4.65 kWh** |
| cold: regen 25%, 6 kW aux | 15.9 kW (+57%) | 2.37 kWh | 1.07 kWh | 14.8 kW (+52%) | 2.73 kWh |
| hot: regen 40 kW, 4 kW aux | 13.0 kW (+28%) | 1.27 kWh | 2.03 kWh | 12.2 kW (+26%) | 1.47 kWh |

A pack that will not accept charge below ~0 °C **turns the whole of
VOLT-SUB's 3.61 kWh of braking energy into friction-brake heat** — a duty
the service brakes were not sized for on a 1.51 stops/km cycle — and raises
V1's genset average by nearly half. It also removes the buffer headroom
that **E4**'s descent fix depends on, in the season when descents are worst.
On a hot day the pack derates the other way and cuts the 75 kW absorb
authority that §2.3 concludes sits "on the knee", while the 4 kW accessory
case is simultaneously active. See **E21**.

### 4.16 Driven-axle adhesion — regen and launch both act through one axle

Assumed geometry: 4.20 m wheelbase, CoG 1.20 m loaded / 1.00 m empty,
static rear-axle share 0.65 at GVW and 0.48 at the operating curb mass.
Braking transfers load off the driven axle, which makes it worse.

| | at GVW | at operating curb (3,700 kg) |
|---|---|---|
| Peak regen force at the wheel (75 kW cap applied) | 10.3 kN | 5.8 kN |
| μ required, peak | 0.26 | **0.36** |
| μ required, 99th percentile | 0.24 | 0.32 |
| μ required by the 13.5 kN launch spec, flat | 0.29 | **0.66** |
| μ required by the 13.5 kN launch spec on a 20% grade | 0.31 | 0.75 |

At GVW everything is comfortable. **Empty — which is where a delivery truck
spends the back half of its shift — single-axle regen needs μ ≈ 0.36 on
every hard stop, which is marginal on a wet road**, and the 13.5 kN launch
spec is simply not deliverable without spinning the wheels. So the capture
fractions in §2.3 are an upper bound: regen must be derated by axle load and
arbitrated with ABS/ESC before the 75 kW cap ever binds, and traction
control is mandatory from the first prototype, not a later refinement.
See **E23**.

---

## 5. Escalations

Ordered by how much they would change the baseline. Most of these contradict
a *number* in the baseline, or an implicit assumption about what a buffer
battery is for. **One of them — E17 — contradicts a locked architecture
decision, deliberately.** The baseline invites challenges here, and E1, E3
and E4 all trace to the same root cause; presenting them only as three
separate requests to three other workstreams would leave the project lead
unable to see the one trade that resolves all of them.

### E1 — The baseline's own 6% grade requirement is motor-limited, not genset-limited *(blocking, WS2 + baseline text)*

"V2 genset floor ~110 kW: must hold 60 km/h loaded on 6% grade with a
depleted battery" is written as a genset requirement, and the genset half
checks out (§6.6). But 60 km/h is *below* the 65 km/h lockup speed, so the
requirement is a **series** operating point in which the traction motor must
deliver **90.5 kW / 198 Nm at its own shaft, continuously, for the ten
minutes of a 10 km climb**. Against the baseline's provisional "≥75 kW
peak" motor, that requirement is unmeetable **at any genset size**. The
binding constraint is the motor.

Compounding it, the thermal-equivalent RMS the assignment asks for is
21.7 kW (V1) and 19.9 kW (V2 with lockup). **Specifying a ~20 kW continuous
motor from those numbers would produce a vehicle that cannot meet the
baseline's own grade requirement.** Recommendation: replace "continuous
rating TBD by WS1" with the duty triple in §3.1, and size cooling to the
S2-10 min case rather than to the RMS.

### E2 — "≥75 kW peak" is marginal for V1 and short for V2 *(material, WS2)*

VOLT-SUB at GVW already demands 69.4 kW at the motor shaft, and 73.1 kW at
+20% payload — inside 75 kW with 3% margin and no allowance for a hot day,
a headwind or a hurried driver. VOLT-REG with lockup demands 111.0 kW; in
forced series (clutch failure, or the low-speed part of any grade) it
demands 168.7 kW. Simulated with a 75 kW motor, V2 loses **9.5 km/h** at
the worst point of VOLT-REG. **Recommend raising the baseline's motor peak from
≥75 kW to ≥120 kW, target 150 kW.**

### E3 — Whether the direct path can hold 6% is an engine *specification*, not a fact *(material, WS4 + baseline text)*

The reference 4HK1 curve cannot hold 6% at any speed (best 5.25% at
70 km/h). A curve with the same 700 Nm @ 1,600 rpm anchor and the same
~150 kW peak, but its torque peak moved to 1,400 rpm, **can** — over a
narrow 59–67 km/h band, with 0.4 kW of margin (§4.5). The cause is
structural: one fixed ratio welds crank speed to road speed, so at
grade-hold speeds the engine is stuck at 1,200–1,400 rpm where it makes
80–100 kW rather than the ~150 kW it can make at 2,400 rpm.

Two recommendations. (a) **WS4 must specify the V2 engine's full-load
torque below 1,600 rpm as a requirement**, because it decides whether the
direct path is usable on grades at all. (b) The baseline's "key derived
numbers" should record the honest capability statement: *9.7% grade at
85 km/h for ~83 s from a full 2 kWh buffer (~45 s from the supervisor's 55%
SOC setpoint); ~5.3% grade indefinitely on the reference engine alone;
61 km/h on 6% once the buffer is flat.*

### E4 — Sustained downgrade retardation is unsolved, and there is no gearbox to downshift into *(blocking, WS3/WS5/WS6, new)*

The assignment asked for the climb. The descent is harder. 10 km at −6%
releases 10.79 kWh and demands 39–46 kW of *continuous* retardation for
6–12 minutes, and **a slower descent is worse**. Regen *power* is not the
constraint (46 kW is well inside 75 kW); the **energy sink** is. With the
buffer starting at its 55% SOC target, a 2 kWh pack at 60 km/h fills in
94 s and the friction brakes then take **5.75 kWh** — an adiabatic 750 K on
60 kg of rotor iron; at 30 km/h it is 6.83 kWh and 890 K with no retarder
available at all. A conventional truck solves this by downshifting into
an engine or exhaust brake; Volt has deleted the gearbox, and in lockup the
engine sits at 1,204–1,706 rpm where pumping losses alone are worth ~10 kW.

From the table in §4.6, **a 30 kW exhaust brake plus a 3–4 kWh usable buffer
closes the problem above 35 km/h — and nothing closes it below.** Idle at
700 rpm through 2.8:1 is 34.9 km/h; under that the clutch must open and
there is no engine drag and no exhaust brake at all, while the energy to
dissipate is at its largest (8.8 kWh at 30 km/h). A loaded truck descending
6% behind slower traffic is the worst case in the whole study and the
architecture has no answer for it.

Recommend adding "sustained descent retardation" to the workstream map as a
WS3/WS5/WS6 interface item, with an explicit decision between an exhaust
brake, a brake chopper / resistor bank, an oversized pack, a documented
descent speed *floor* as well as a ceiling, and — see **E17** — a splitter
that would restore engine braking at low road speed.

### E5 — The baseline's "~83%" series efficiency is 81.4% *(minor, baseline text)*

0.94 × 0.97 × 0.92 × 0.97 = 0.8137. The 1.6-point difference propagates
directly into genset sizing (≈1.8 kW on the V2 floor). Recommend the
baseline quote 81%, or restate the component values.

### E6 — V1's genset average is 10.1 kW against a ~50 kW installed genset *(material, WS4/WS3)*

A 20% load factor. Either the genset runs continuously at a bad point on the
BSFC map, or it start-stops — and if it start-stops at a fixed efficient
point, **the buffer size *is* the start frequency**:

| Fixed operating point | Buffer 0.7 kWh | Buffer 1.5 kWh | Buffer 3.0 kWh |
|---|---|---|---|
| 25 kW | 8.6 starts/h | 4.0 /h | 2.0 /h |
| 35 kW | 10.3 starts/h | 4.8 /h | 2.4 /h |
| 47 kW | 11.3 starts/h | 5.3 /h | 2.7 /h |

At 35 kW with the cycle-derived 0.7 kWh buffer that is **82 starts per 8 h
shift, ~20,500 per year** — a durability and aftertreatment problem. (A
turbocharged diesel does not step to setpoint either: at a nominal 4 s
load-acceptance transient the buffer covers ~0.02 kWh per start, ~0.2 kWh
per hour. That is small against the buffer itself, but it means the engine
is ramping 8–11 times an hour, which is not the fixed-BSFC-point operation
the baseline hands WS4.) Sizing
the buffer to 3 kWh cuts it to ~19 per shift. Also recommend WS4 revisit
what actually justifies the "~50 kW class", since the cycle does not: at
the engine shaft, 50 kW buys 30.2 km/h on a 6% grade and 78.6 km/h flat;
40 kW buys 24.3 km/h and 71.0 km/h; 30 kW buys 18.1 km/h and 61.7 km/h.
**The V1 genset is a grade-and-top-speed decision, not a duty-cycle one**,
and the baseline should say which of those it is buying.

### E7 — Buffer sizing is set by grades and by genset duty cycling, not by the drive cycle *(material, WS3)*

| Driver of buffer size | Usable energy |
|---|---|
| VOLT-SUB 5-minute swing (the ③ answer) | 0.71 kWh |
| VOLT-REG 5-minute swing, i-MMD | 1.29 kWh |
| VOLT-REG whole-cycle swing at one genset setpoint | 3.40 kWh |
| VOLT-REG 5-minute swing, forced series | 7.32 kWh |
| Hold 85 km/h up 10 km of 6% | 2.67 kWh (not achievable — see §4.4) |
| Take a 10 km 6% descent at 60 km/h with **no** friction braking at all, *with* a 30 kW exhaust brake | 3.4 kWh |
| Same, *without* an exhaust brake | 12.7 kWh |
| Keep V1 genset starts under ~20 per shift | ~3 kWh |

**These demands are concurrent, not alternative.** E6's start-stop scheme
works by swinging the *entire* usable window between genset-on and
genset-off, which by construction leaves no headroom at either end — yet a
truck sitting at the top of its hysteresis cannot accept a hard stop's
regen, and one holding a grade reserve cannot swing its full window. §4.6
does this correctly by reserving headroom around a 55% SOC target; nothing
else in the study does. WS3 needs the **sum**: genset hysteresis window +
regen headroom + grade reserve + SOC end-stops, divided by the usable
fraction of nameplate.

**Recommend usable buffer ≥3.5 kWh for V2 and ≥1.5 kWh for V1 at the DC
bus** (3.6 and 1.5 kWh at the cells), i.e. 2.7–4.9× what the cycle-derived
Number ③ says — and treat that as a floor once the terms above are
superposed rather than maxed, and subject to **E8**, which may make the
energy question moot entirely.

### E8 — The implied battery C-rates are severe enough to size the pack by power *(material, WS3)*

Peak battery discharge is 120 kW (V2 i-MMD), 145 kW (V2 forced series) and
72 kW (V1); peak charge 70–110 kW. Against the cycle-derived ③ of 0.71–1.29
kWh that is **93–113 C**, and even against a 3 kWh usable pack it is
40 C discharge / 37 C charge. That is supercapacitor or high-power-cell
territory, not an energy cell. **If WS3 comes back with an energy-cell
pack, the pack is sized by power and E7's energy numbers become moot** —
and the resulting pack will be several times larger than any of them.
This also drives the DC bus voltage that WS2 is about to propose.

### E9 — The 13.5 kN spec is a launch spec being used as a crawl spec *(material, WS2)*

13.5 kN at the wheel = 515 Nm at the motor shaft. The baseline derives it
from a 20% grade *launch*. But a 20% grade also has to be *climbed*: V1
settles at 10.6 km/h and V2 at 23.6 km/h on 20%, both drawing ~510 Nm
continuously at 300–700 motor rpm — **the full stall torque, held for
minutes, at near-zero cooling airflow**, against a cycle RMS torque of
115 Nm. WS2 must state the thermal derate curve for this case; it is the
worst thermal point in the programme.

### E10 — Peak regen demand is 1.6–2.5× the absorb limit, on every stop *(material, WS5)*

Not an argument for a bigger absorber (§2.3 shows 75 kW is the knee) but a
controls requirement: on VOLT-SUB the friction brakes must blend in for 54 s
of every hour, at up to **86 kW** above the electrical path's authority
(**123 kW** on VOLT-REG, using the ④ design envelope), and the blend must be transparent to the driver and fail
safe. Note also that ④ is a wide band across cycle realisations (121–133 kW on
VOLT-SUB, 145–198 kW on VOLT-REG) and a function of driver braking style,
not of the vehicle — and that the blend must additionally be arbitrated
against single-axle adhesion, which binds before the 75 kW cap does on an
empty truck (**E23**).

### E11 — The regen-priority clutch strategy cycles the clutch 39 times per 100 km *(minor, WS5)*

With "open the clutch whenever wheel power goes negative", VOLT-REG produces
51 engagements per cycle (39 per 100 km). The energy is trivial — spinning the engine from
idle to the 1,305 rpm sync speed costs 4.0 kJ (~8 kW over 0.5 s) plus ~8 kW
of motoring drag, which **supports the baseline's motor-synchronised clutch
decision** — but the *count* is a wear and NVH item. WS5 should consider
staying locked through shallow braking and using engine drag, which also
helps E4, at the cost of some regen energy.

### E12 — VOLT-SUB and VOLT-REG are not the same load, and one spine serves both *(informational, WS2/WS3)*

VOLT-SUB: 115 Nm RMS torque, 3,585 rpm max, 40% of tractive energy into the
brakes, 44% of the time stationary. VOLT-REG: 71 Nm RMS torque, 7,169 rpm
max, 6% into the brakes, 17% of the time above 75 kW. The machine must be
efficient at low speed and high torque *and* spin to 7,200 rpm — a
field-weakening range of about 2:1 above base speed if base speed is set for
the delivery duty. A real constraint on WS2's DC bus voltage proposal.

### E13 — CdA 4.2 m² and ρ 1.20 kg/m³ are fitted, optimistic inputs *(material, baseline input)*

ρ = 1.20 was chosen by WS1 specifically to reproduce the baseline's
"85 km/h → 2.0 kN / 47 kW"; it is 2% below ISA sea level. CdA = 4.2 m² for
a 16 ft dry-freight box on an NPR cab implies a frontal area × drag
coefficient at the optimistic end of the plausible 4.6–5.6 m² range. At
CdA 5.4 m², VOLT-REG energy per km rises 18%, P95 rises 14%, and the
baseline's own "60 km/h on 6%" claim fails at 59.1 km/h (§4.11).
**Recommend the baseline record CdA and ρ as provisional pending a coastdown
on the prototype**, and that WS4 carry ~5% genset margin against it.

### E14 — VOLT-SUB's 50 km/h ceiling is an assignment constraint, not a duty description *(minor, scope)*

The assignment specifies 0–50 km/h for the postal cycle and the cycle honours
it, but real parcel routes include 60–90 km/h depot transits. Those would
raise V1's motor speed range (50 km/h = 3,585 rpm; 90 km/h would be
6,452 rpm) and add a sustained ~30 kW cruise leg that the current cycle
never sees. **Recommend a V1 "depot transit" variant before WS2 freezes the
motor speed envelope**, or an explicit statement that V1 is speed-limited to
50 km/h.

### E15 — "110 kW genset" has no stated rating basis *(minor, baseline text)*

WS1 has read it as **engine shaft** power, which is the conservative
reading and gives 2.2 kW of margin against the 6% requirement (107.8 kW) and
a 61.0 km/h hold speed. Read as **generator electrical output** it gives
8.7 kW of margin and a 64.0 km/h hold speed. Genset ratings are conventionally
electrical. **Recommend the baseline state which it means**; the two differ
by ~6 kW of engine.

### E16 — No cycle here ever places a stop on a grade *(minor, method)*

Wheel power is `F·v`, so zero-speed holding torque is structurally invisible
to every RMS-power and RMS-torque statistic in this report. On these cycles
that is immaterial (VOLT-SUB is flat; VOLT-REG's stops all occur at
|grade| ≤ 1.9%, worth at most 47 Nm of hold torque). But the same study
designs to sustained 6% grades, where a stop needs **3,885 N = 148 Nm at
zero speed** — comparable to the entire worst-300 s RMS torque — and PM
machines are typically derated to 40–60% of rotating continuous torque at
standstill because the loss localises in one or two phases with no rotor
airflow. **Recommend WS2 specify a standstill hold-torque rating, and WS7
add a hill-hold case to the test plan.**

### E17 — E1, E3 and E4 have one root cause: the deleted gearbox *(challenge to a locked decision, for the lead to resolve)*

The baseline locks "No multi-ratio gearbox" and invites challenges here, so
this is the challenge. WS1's own results, gathered in one place:

- the 2.8:1 direct path holds **no speed at all** on a 6% grade with the
  reference engine (E3), because the crank is welded to the road and sits at
  1,200–1,400 rpm where the engine makes 80–100 kW instead of ~150 kW;
- the same welding means the engine runs at a **median 48% load** on the
  locked path, so the 95%-vs-81.4% argument for the direct path's existence
  is untested and probably overstated (E20);
- V2 collapses from 85 to **61.0 km/h** on a sustained 6% once the buffer is
  flat (§4.4);
- there is **no engine braking of any kind below 34.9 km/h** and no gear to
  downshift into above it, which is why E4 has no answer for a slow loaded
  descent;
- and the traction motor must cover 0–7,169 rpm with 515 Nm at the bottom
  (E9, E12), because it too has only one ratio.

Every one of those is a direct consequence of the single fixed ratio, and a
**2-speed splitter (or even a 2:1 range change on the engine path alone)
would address E3, E4, E20 and part of E12 together** — it would let the
engine reach its power peak at grade-hold speed, restore engine/exhaust
braking down to ~17 km/h, and give the supervisor a second engine operating
line to place on the BSFC map.

WS1 is not asking for the decision to be reversed: the transmissionless
architecture is the programme's reason for existing, and the alternative
costs mass, packaging space (WS6), a shift strategy (WS5) and the very
simplicity being demonstrated. **WS1 is asking that the trade be rejected on
the record rather than by omission**, and that the baseline record what the
single ratio costs: no sustained 6% capability on the engine alone, a
61 km/h grade-hold speed, no low-speed retardation, and an engine that
cannot be held at one operating point in lockup.

### E18 — V1 cannot reach the programme's own 85 km/h design point *(material, WS4 + baseline text)*

A 50 kW-class genset (engine shaft) delivers 39.0 kW at the wheel after the
generator, accessories and the series chain. That charge-sustains
**78.6 km/h flat at GVW**. The baseline's own cruise design point —
"geared for ~85 km/h at ~1,700 rpm", "Cruise 85 km/h flat: ~2.0 kN, ~47 kW"
— needs **59.8 kW of engine shaft**, 20% more than the V1 class. And 39.0 kW
at the wheel is below VOLT-REG's *cycle-average* tractive demand of
42.9 kW (**54.9 kW of shaft in series**), so a V1 truck cannot complete the
regional cycle in any battery state: not degraded performance, a route it
can never finish.

Neither consequence is currently written anywhere. Recommend the baseline
either raise the V1 class to ~60 kW shaft, or state explicitly that **V1 is
a sub-80 km/h vehicle that must never be dispatched on regional work** —
which E14's "real parcel routes include 60–90 km/h depot transits" makes an
operational risk rather than a hypothetical.

### E19 — The 110 kW floor is confirmed at exactly one operating condition *(material, WS4/WS6)*

§4.12 sweeps the requirement that actually sizes the genset. 110 kW clears
it by 2.2 kW at GVW, 2 kW accessories and CdA 4.2, and by nothing at all
anywhere else: −0.1 kW at a 4 kW hot-day accessory load, −1.9 kW at
CdA 5.4, **−5.8 kW at the +20% payload case §4.1 treats as routine**, and
−12.1 kW with all three together.

Two compounding items. First, the 2 kW accessory budget contains **no
thermal-management power**, and this is the case that needs it: at the grade
hold the electrical chain alone rejects **20.2 kW** (generator 6.6, power
electronics 3.0, inverter+motor 7.9, reduction 2.7) into a low-temperature
loop the donor vehicle does not have, behind an engine rejecting ~99 kW
through a stock radiator package — and the pumps and fans for that are
themselves 1.5–3 kW off the same DC bus. Second, no workstream currently
owns full-load heat rejection.

Recommend: restate the floor as "110 kW holds 60 km/h on 6% at GVW, nominal
accessories and the fitted road load, with 2% margin, and misses it at +20%
payload, at 4 kW accessories, and at CdA 5.4"; raise the recommended genset
margin accordingly; and assign heat rejection to WS6 with the 20.2 kW
electrical-chain figure as an input.

### E20 — The case for the direct path has never been tested against a BSFC map *(material, WS4)*

The 95% mechanical vs 81.4% series comparison is a *component* efficiency
argument. It assumes the engine is equally efficient at both operating
points, and the fixed ratio guarantees it is not: §4.13 shows the locked
engine at 28% load at 60 km/h, 39% at 85 and 51% at 100, with a median of
48% over the whole locked portion of VOLT-REG and 16% of that time below
30% load. A free-running genset can be pinned to its BSFC island by
definition — which is what the baseline instructs WS4 to do. At typical
medium-duty diesel BSFC the part-load penalty over that range is of the same
order as the 14-point efficiency advantage the mechanical path is credited
with.

WS1 does not own a BSFC map and cannot settle this. **Recommend WS4 run the
comparison on a real map before the direct path is treated as a decided
advantage**, using the engine speed/load residency in
`results.json → engine_residency_V2_locked`. If it does not survive, V2
collapses toward V1 with a bigger genset — which would be the largest
programme-level finding available from this workstream.

### E21 — No ambient, cold-start or altitude envelope is declared anywhere *(material, baseline text + WS3)*

A duty-cycle workstream owns the environmental envelope, and this one is
first-order rather than a refinement (§4.15). A cold pack that refuses
charge turns **all 3.61 kWh** of VOLT-SUB's braking energy into
friction-brake heat instead of 0.29 kWh, and raises V1's genset average
from 10.1 to 15.0 kW (+48%). It also removes exactly the buffer headroom
E4's descent fix depends on, in the season descents are worst. A hot pack
derates the other way and cuts the 75 kW absorb authority that §2.3
concludes is on the knee, while the 4 kW accessory case is simultaneously
active. Altitude is not considered at all; ρ = 1.20 kg/m³ implies sea level,
and a 1,500 m pass would cut both the naturally-aspirated engine's output
and the aero load in opposite directions.

**Recommend the baseline declare the ambient and altitude envelope the Four
Numbers are valid over, before WS3 sizes the pack.**

### E22 — Every efficiency in this study is a peak-point scalar *(material, WS2/WS4)*

There is no part-load map anywhere in the model, and both machines live at
part load: the traction motor is below 25% of rating for 85% of VOLT-SUB and
93% of VOLT-REG, and V1's genset runs at a 20% load factor. A crude derate
(§4.14) costs 7.0–8.5% on traction energy and **16.8–22.4% on ②**, and the
bias is one-directional on every kWh/km, on ②, on ③ and on the regen-to-bus
fractions. It also means **E5**'s 81.4% is an upper bound rather than an
operating value.

Recommend WS2 supply a speed- and load-dependent efficiency map for the
machine and inverter (generating as well as motoring, since the study
currently assumes the regen chain is symmetric), and WS4 the same for the
generator — and that every efficiency-derived number in this report be
treated as a best case until they arrive.

### E23 — Regen and launch both act through one axle, and the empty truck is the binding case *(material, WS2/WS5/WS7)*

The 75 kW absorb limit is treated throughout as a machine limit. On a 4×2
light truck the binding limit is often the driven axle (§4.16). At GVW the
peak regen event needs μ ≈ 0.26 — comfortable. **At the operating curb mass,
where a delivery truck spends the back half of its shift, the same stop
needs μ ≈ 0.36 on a 1.51 stops/km cycle** — marginal in the wet. And the
13.5 kN launch spec needs μ ≈ 0.29 at GVW but **μ ≈ 0.66 empty**, i.e. it is
simply not deliverable without wheelspin.

Consequences: the §2.3 capture fractions are an upper bound; single-axle
regen must be derated by axle load and arbitrated with ABS/ESC before the
cap ever binds; and **traction control is a day-one requirement, not a later
refinement**. Recommend WS7 add a wet-surface regen and launch case to the
test plan.

### E24 — The forced-series column is an analysis case; nobody has decided whether it is a requirement *(material, WS2/WS3/WS7)*

The two variants have opposite failure asymmetries and neither is escalated.
**V1 is pure series with no mechanical path: a genset or pack fault
immobilises it — there is no degraded mode, only a tow.** V2 can limp on the
direct path above ~35 km/h with a dead pack, but its forced-series column is
the most demanding case in this entire study — 168.7 kW peak motor shaft,
57.2 kW cycle RMS, **124.8 kW worst 300 s rolling RMS**, 7.32 kWh of
five-minute buffer swing, 145 kW battery discharge. Since V2's limp mode is
more demanding than its normal mode, that choice decides whether E2's
"≥120 kW, target 150 kW" is a *peak* rating or a *fault-mode continuous*
rating — a very different machine and a very different cooling system.

**Recommend the lead decide explicitly whether the spine is sized for the
clutch-open fault or whether a derated limp-home speed is declared**, and
that the answer be written into §3.1's duty triple. Add V1's "no mechanical
path in any fault state" asymmetry to WS7's test plan.

---

## 6. First-principles sanity check of each headline number

Each of these is an independent back-of-envelope reconstruction, not a
restatement of the model.

### 6.1 Energy per km — 0.450 (VOLT-SUB) and 0.600 (VOLT-REG) kWh/km

Decompose the wheel work per km into its three physical sources:

| | rolling | aero | positive inertia | Σ | model's tractive E/km |
|---|---|---|---|---|---|
| VOLT-SUB | 0.162 | 0.106 | 0.214 | 0.482 | **0.450** |
| VOLT-REG | 0.162 | 0.402 | 0.071 | 0.635 | **0.600** |

Rolling is exact and identical for both (0.009 × 6,600 × 9.81 × 1,000 m =
583 kJ = 0.162 kWh/km) — a check that the integration is sane. Aero follows
from the distance-weighted mean square speed (151 m²/s² for VOLT-SUB, 574
for VOLT-REG → 381 N and 1,447 N of mean drag). The inertia term is the
kinetic energy rebuilt after every stop, and it flips from being the
*largest* term in city work to the *smallest* on the highway — the whole
reason the two cycles behave differently. Each Σ sits ~6% above the model's
tractive energy, and it should: during braking the vehicle's own kinetic
energy pays the road load, so the driveline never sources it. Grade
contributes exactly zero over VOLT-REG because the profile is a closed
loop. **The decomposition reproduces both numbers to within the amount it
is expected to be wrong by.**

### 6.2 ① Motor continuous — 21.7 kW RMS (V1), 115 Nm RMS torque, 90.5 kW grade hold

Three checks. *The RMS power:* the mean of |P_shaft| over VOLT-SUB is
12.8 kW, and for a spiky, mostly-zero signal the RMS/mean-absolute ratio
should sit around 1.5–2. It is 1.69, giving 21.7 kW. On VOLT-REG with
lockup the mean falls to ~10.5 kW but the ratio *rises* to ~1.9 (the motor
now only sees transients), giving 19.9 kW — the right qualitative
behaviour in both directions. *The RMS torque:* mean |T| is 61.4 Nm on
VOLT-SUB against a 353 Nm peak, ratio 1.87 to the 115 Nm RMS; on VOLT-REG
mean |T| is 30.4 Nm and the ratio 2.33 to 71 Nm — a spikier torque
signature on the highway cycle, which is exactly what "the engine carries
the steady load and the motor fills transients" should produce. *The grade
hold:* a 110 kW engine gives 110 × 0.94 = 103.4 kW at the bus, less 2 kW of
accessories, times the 0.866 bus-to-wheel chain = 87.8 kW at the wheel, or
90.5 kW at the motor shaft after the 0.97 reduction. That the motor-shaft
figure is *larger* than the wheel figure is the correct direction — the
motor must overcome the reduction's losses on the way out.

### 6.3 ② Genset average — 10.1 kW (V1)

Close the energy balance at the DC bus by hand. Tractive energy 8.92 kWh
over 3,485 s is 9.21 kW at the wheel; divide by the 0.866 bus-to-wheel
chain → 10.64 kW must leave the bus. Regen returns 2.87 kWh = 2.97 kW.
Accessories add 2.00 kW. Net = 10.64 − 2.97 + 2.00 = **9.67 kW**, against
the model's 10.11 kW. The 0.44 kW gap is the battery round trip: of the
12.66 kWh entering the bus over the block, 7.19 kWh goes in and out of the
battery rather than straight to the wheels, and 0.97 × 0.97 on that is a
0.425 kWh loss = **0.44 kW** — the gap, to three figures. The same
arithmetic on VOLT-REG gives 49.86 kW against the model's 50.6 kW for the
forced-series case.

### 6.4 ③ Battery buffer — 0.71 kWh over 5 minutes (V1)

Bound it from both sides. In any 300 s window the genset delivers
10.1 kW × 300 s = 0.84 kWh. A window made entirely of driving (bus load
~25 kW) would run a 15 kW deficit = 1.25 kWh; a window made entirely of
delivery dwells (bus load 2 kW) would run an 8 kW surplus = 0.67 kWh. The
answer must lie between and nearer the lower bound, because VOLT-SUB's
longest single dwell is 78 s so no five-minute window is purely one mode.
0.71 kWh sits exactly there. (That is the reference realisation, which is
also the ensemble *minimum*; the eight-seed maximum is 0.87 kWh, and §7
hands the ensemble figure downstream.) Two further checks: the alternative reading of
"energy swing" (net drift across the window rather than peak-to-peak inside
it) gives 0.62 kWh, so the number is not an artefact of how the question is
read; and the swing grows monotonically with window length (0.33 / 0.48 /
0.71 / 0.82 / 0.99 / 1.13 kWh at 1 / 2 / 5 / 10 / 20 minutes and the whole
cycle), which is the only shape a rolling peak-to-peak can have — and is
also why ③ is a statement about the control law rather than the vehicle.

### 6.5 ④ Peak regen — 121 kW (VOLT-SUB) and 145 kW (VOLT-REG) this realisation, 161 / 198 kW as an envelope

These are ordinary stops. VOLT-SUB's worst is a stop from 44 km/h at
1.59 m/s² (0.16 g): inertial force λma = 1.04 × 6,600 × 1.587 = 10,892 N,
of which the road load already absorbs 376 N of aero and 583 N of rolling,
leaving 9,933 N for the driveline × 12.2 m/s = **121.4 kW**. VOLT-REG's
worst in this realisation is a stop from ~72 km/h at ~1.35 m/s² on a slight
downgrade, giving **144.8 kW**; the hardest stop across seven realisations
gives **197.6 kW**, which is the number to design to. Neither is
emergency braking — 0.14–0.16 g is what a driver does approaching a red
light. The corollary is that a 6.6 t truck cannot regeneratively brake a
normal stop with less than ~150 kW of absorb capability, which is why the
75 kW limit costs only 8–12% of the *energy* while missing 40–60% of the
*power*.

### 6.6 The baseline's 110 kW V2 genset floor, and the 61 km/h that follows

Forwards: at 60 km/h on 6%, grade force = 6,600 × 9.81 × sin(arctan 0.06)
= 3,878 N, rolling = 0.009 × 6,600 × 9.81 × cos θ = 582 N, aero =
½ × 1.2 × 4.2 × 16.67² = 700 N. Total 5,160 N × 16.67 m/s = 86.0 kW at the
wheel → 99.3 kW at the bus → 105.7 kW of engine shaft, plus 2 kW of
accessories through the generator = **107.8 kW**. Backwards: a 110 kW
engine yields 87.8 kW at the wheel, and solving 2.52 v³ + 4,460 v = 87,800
gives v = 16.94 m/s = **61.0 km/h**. Confirmed from both directions with
~2 kW of margin — and the capability-limited forward simulation, which
knows nothing about either calculation, settles on 60.97 km/h. (That
margin does not survive a 4 kW accessory load, or CdA 5.4 m² — E13, E15.)

### 6.7 Every baseline number, checked

| Baseline statement | WS1 recomputation | Verdict |
|---|---|---|
| Cruise 85 km/h flat: ~2.0 kN, ~47 kW at the wheel | 1,988 N, 46.9 kW | confirmed (and it is what fixes ρ = 1.20 — E13) |
| 20% grade launch, full GVW: 13.5 kN | 13,272 N | confirmed; the baseline rounds up, margin 1.7% |
| ~75 kW corner power at that launch | 13.5 kN × 5.6 m/s = 75 kW at 20 km/h | confirmed |
| Diesel-only force through 2.8:1: ~5.0 kN max | 700 × 2.8 × 0.95 / 0.37 = 5,032 N | confirmed |
| Diesel-only force zero below ~35 km/h | idle 700 rpm ⇒ 34.9 km/h | confirmed |
| Combined ~8 kN at 85 km/h → holds 9–10% grade | 8.21 kN → 9.7% | confirmed — but only for ~83 s on a full 2 kWh buffer |
| V2 genset floor ~110 kW to hold 60 km/h on 6% loaded | 107.8 kW engine shaft incl. accessories → 61.0 km/h | confirmed with 2.2 kW of margin; **but see E1 — the motor, not the genset, is the binding constraint** |
| Series-path efficiency ~83% | 0.94 × 0.97 × 0.92 × 0.97 = 81.4% | **discrepancy — E5** |
| Geared for ~85 km/h at ~1,700 rpm | 85 km/h ⇒ 1,706 rpm through 2.8:1 and r = 0.37 m | confirmed |
| Motor 5,000 Nm at the wheels via ~10:1 | 13.5 kN × 0.37 = 4,995 Nm; 515 Nm at the motor shaft | confirmed |

---

## 7. What WS1 hands to WS2–WS4

| To | Number | Value |
|---|---|---|
| WS2 | Motor S1 continuous | ≥ 45 kW / 180 Nm at the motor shaft |
| WS2 | Motor S2 10-minute | ≥ 95 kW / 200 Nm |
| WS2 | Motor peak | ≥ 120 kW (target 150 kW), 515 Nm below 20 km/h — **170 kW if the clutch-open fault is a requirement (E24)** |
| WS2 | Motor speed range | 0 – 7,200 rpm (100 km/h through 10:1) |
| WS2 | Generating envelope | 73 kW / 370 Nm (the 75 kW wheel cap sets the power) |
| WS2 | Size on RMS **torque** (115 / 71 / 106 Nm), not on RMS power | §3.1 |
| WS2 | Worst thermal point | ~510 Nm at 300–700 rpm for minutes, no airflow (20% grade crawl) |
| WS2 | Standstill hold torque | 148 Nm on a 6% grade — specify a derated rating (E16) |
| WS3 | Usable buffer energy | ≥ 3.5 kWh at the bus / 3.6 kWh at the cells (V2), ≥ 1.5 kWh (V1) — set by the 6% descent with an exhaust brake and by genset duty cycling, not by the cycle; and a **floor**, because the demands superpose (E7) |
| WS3 | Peak discharge / charge | 120 kW / 110 kW ⇒ 40 C / 37 C on a 3 kWh usable pack; the pack is probably power-sized (E8) |
| WS3 | Regen energy throughput | 2.9 kWh per hour of VOLT-SUB; 3.7 kWh per 132 km of VOLT-REG — **zero on a cold pack, which then puts 3.6 kWh into the brakes (E21)** |
| WS3 | Cold/hot charge-acceptance envelope | must be declared before the pack is sized (E21) |
| WS4 | V1 genset average | 10.1 kW electrical at the bus (10.8 kW shaft) over a 1 h postal block |
| WS4 | V1 genset load factor | 20% of a 50 kW class unit ⇒ start-stop, ~10 starts/h at a 0.7 kWh buffer |
| WS4 | V2 engine average shaft power | 47.0 kW over VOLT-REG with lockup; 53.8 kW if forced series |
| WS4 | V2 genset floor | 107.8 kW engine shaft at GVW / 2 kW aux / CdA 4.2 — the baseline's 110 kW stands **only there**: 115.8 kW at +20% payload, 109.9 kW at 4 kW aux, 111.9 kW at CdA 5.4 (E19) |
| WS4 | Engine speed/load residency on the locked path | median 48% load, 16% of locked time below 30% — needed to settle whether the direct path actually beats series (E20) |
| WS4 | Part-load efficiency map | ② rises 17–22% under a crude derate; the 81.4% chain is an upper bound (E22) |
| WS6 | Full-load heat rejection | 20.2 kW from the electrical chain at the 6% grade hold, plus ~99 kW from the engine, into a loop the donor vehicle does not have (E19) |
| WS4 | **New requirement** | specify engine full-load torque below 1,600 rpm; it decides whether the direct path works on grades (E3) |
| WS5 | Friction-brake blending authority | up to 86 kW (V1) / 123 kW (V2) above the electrical path at the ④ envelope; 54–63 s per cycle above 75 kW; and arbitrated against single-axle adhesion, which binds first when empty (E23) |
| WS7 | Test-plan additions | wet-surface regen and launch (E23), hill-hold at standstill on 6% (E16), cold-pack regen (E21), and V1's no-mechanical-path fault asymmetry (E24) |
| WS5 | Clutch engagements | 39 per 100 km under a regen-priority strategy |
| WS5 | Regen absorb limit | keep 75 kW; it is the knee of the curve |
| WS5/WS6 | **Unresolved** | sustained downgrade retardation (E4) — and nothing in the architecture helps below 34.9 km/h |
| **Lead** | **Decision requested** | reject the 2-speed splitter trade on the record, or take it (E17); decide whether the spine is sized for the clutch-open fault (E24); declare the ambient/altitude envelope (E21) |

## 8. Artefacts in this folder

- `REPORT_WS1.md` (this file), `tables.md` (auto-generated tables)
- `results.json` — every number above, machine-readable. `requirements_summary` is the interface WS2–WS4 should parse; it uses ensemble envelopes rather than single draws and gives battery energies at the cells as well as at the DC bus
- `run_output.txt` — console summary of the last run
- `run_ws1.py`, `volt_params.py`, `volt_cycles.py`, `volt_physics.py`,
  `volt_variants.py`, `make_tables.py`, `requirements.txt`, `README.md`
- `data/cycle_VOLT-{SUB,REG}_1Hz.csv` — the two reference cycles
- `data/trace_VOLT-{SUB,REG}_*_10Hz.csv` — full traces with bus/battery channels
- `data/time_at_power_*.csv`, `data/regen_sweep_*.csv`, `data/four_numbers.csv`
- `figs/fig01…fig10` — traces, histograms, sensitivity sweeps, operating maps

## 9. What the independent review changed

Thirteen agents: seven recomputing headline numbers from first principles
without this code, three auditing the source, two attacking completeness,
one adjudicating. Their findings are grouped below by what happened to them.

### 9.1 Defects fixed (numbers or conclusions moved)

| # | Defect | Effect | Status |
|---|---|---|---|
| 1 | ① charged the traction motor with the *full uncapped* braking demand, although the study insists the machine absorbs at most 75 kW at the wheel. Braking supplied 44% of mean(P²) on VOLT-SUB. | ① overstated by 4% (V1), 5% (V2 i-MMD) | fixed — ① uses the capped, blended trace; the uncapped value is reported alongside |
| 2 | The motor envelope reported a generating capability of 118 kW (V1) and 140 kW (V2) at the shaft — impossible under the same 75 kW cap. | would have oversized the inverter's regenerating rating by 1.6–1.9× | fixed — 72.8 kW; braking *torque* was unaffected |
| 3 | RMS torque was computed as P/ω and zeroed below 0.5 m/s, deleting the highest-torque instants of every launch. | T_rms understated by ~1% | fixed — torque now from wheel force |
| 4 | "Combined force at 85 km/h" and "max grade the direct path holds" used a small-angle grade, inconsistent with the road-load model. | ~0.1 pt on the holdable grade | fixed — both solve for tan θ |
| 5 | The descent case started the buffer empty, ignored the 2 kW accessory draw, credited no engine braking, and was evaluated only at 85 km/h — near the speed that *minimises* friction-brake duty. | friction-brake energy understated ~2× | fixed — §4.6 sweeps speed, buffer and engine braking from the 55% SOC start |
| 6 | "The direct path cannot hold 6% at any speed" was asserted robust to an alternative torque curve without testing. | the conclusion flips for a curve peaking below 1,600 rpm | fixed — §4.5 tests four curves; E3 restates it as an engine *specification* requirement |
| 7 | The driver model's speed-hold branch ignored the driver's own power budget. | VOLT-REG peak wheel power −6% | fixed — the hold branch is limited by `_accel_capability()` |
| 8 | `simulate_achievable`'s energy-unlimited branch omitted the locked-mode engine clamp, so one crankshaft could drive the wheels *and* a 110 kW generator load. | over-optimistic unlimited-battery capability | fixed — the clamp applies in both branches |
| 9 | The V2 i-MMD split let the direct path use the engine's full capability and then added a constant genset on top of the same engine. | 0.33 of 78.9 kWh double-booked | fixed — two-pass split reserving the generator's shaft power |
| 10 | `solve_genset_constant` bisected inside a hard bracket with no residual check; `power_histogram` folded out-of-range samples into edge bins. | neither triggered, but both would fail silently | fixed — both now raise |
| 11 | ④ was quoted from a single realisation whose draw sits *below* the seed ensemble. | ④ understated by up to 27% as a design number | fixed — ④ is an envelope over seeds and braking styles |
| 12 | Smaller items: `net_window_swing` used a window one sample longer than `max_window_swing`; `build_climb` accepted and ignored `dp`/`m`; `four_numbers` ignored its `windows` argument; the grade-profile docstring described two hill features where the code applies four. | cosmetic to <1% | fixed |
| 13 | **③, peak power, P99 and braking energy were also single draws**, and the published cycle is the ensemble *minimum* for ③ on VOLT-SUB. | ③ understated 19% as a requirement | fixed — the ensemble now includes the reference seed and reports 8-member ranges; §3 and §7 hand over the envelope |
| 14 | **`requirements_summary` contradicted the report's own prose**: it handed WS3 a governing buffer of 2.67 kWh — the case §4.4 declares unachievable — while 4.55 kWh sat unselected in the same object, and exported the reference regen draws rather than the design envelope. | the machine-readable interface, which downstream workstreams will trust, was wrong in the unsafe direction | fixed — governing case excludes the unachievable one, extrema come from the ensemble, and energies are given at the cells as well as the bus |
| 15 | The 10 km 6% climb dropped the 2 kW accessory load that §6.6 includes for the same vehicle on the same grade. | battery draw understated 11% (2.67 → 2.94 kWh) | fixed — accessories applied consistently through the direct-path cases |
| 16 | The `dwell_scale` sweep computed its leg count from the *unscaled* dwell, so scaling the dwell pushed a variable number of drive legs past the truncation point. | part of the quoted ±26% was route composition, not dwell | fixed — the leg count now uses the scaled dwell; every row is a comparable block |
| 17 | The descent model credited an exhaust brake at speeds where the crank would be below idle. | 30 km/h looked solvable when it is not | fixed — engine braking is zeroed below 34.9 km/h, which is now E4's sharpest case |

### 9.2 Gaps closed (analysis that was missing, not wrong)

| Added | Why it mattered | Where |
|---|---|---|
| Grade-floor sweep over mass × accessories × road load | the payload sweep only moved the cycles; the requirement that sizes the genset was never swept | §4.12, **E19** |
| Engine speed/load residency on the locked path | the 95%-vs-81.4% case for the direct path had never been tested against how the engine actually runs | §4.13, **E20** |
| Part-load efficiency sensitivity | every efficiency was a peak-point scalar while both machines live at part load | §4.14, **E22** |
| Cold and hot environmental cases | "cold", "ambient" and "altitude" appeared zero times | §4.15, **E21** |
| Driven-axle adhesion | regen and launch both act through one axle, and the empty truck binds first | §4.16, **E23** |
| Heat rejection at the sizing point | §1.2 flagged the gap in the accessory budget and never applied it | **E19** |
| V1's capability boundary | the 78.6 km/h number existed; neither consequence was drawn | **E18** |
| Fault-mode sizing question | the forced-series column was computed but never converted into a requirement | **E24** |
| The gearbox trade | E1, E3 and E4 were presented as three separate requests to three workstreams | **E17** |

### 9.3 Judgement calls, now disclosed rather than changed

The RMS-power metric itself (§3.1); the 5-minute window versus a literally
constant genset (§4.10); including 44% stopped time in VOLT-SUB's
denominators (both reported); VOLT-SUB's 50 km/h ceiling (**E14**);
VOLT-REG's highway dominance (§1.4); grade/speed independence in the cycle
construction (§1.4); the fitted CdA and ρ (**E13**); the genset rating basis
(**E15**); the "0.268 kWh/km net" bookkeeping figure (§2.1); the
regen-priority clutch strategy (**E11**); the absence of a sourced published-
cycle comparison table; and the genset load-acceptance transient, which
turns out to cost ~0.02 kWh per start and is reported in **E6** as small.

### 9.4 Reviewer findings judged not real

Roughly a dozen "the report disagrees with results.json" findings were
against a snapshot of the cycle statistics that the fixes above then moved
by 3–9%; the report is now generated from `results.json` and every headline
matches. One reviewer computed an empty-truck regen adhesion requirement of
μ 0.61–0.69 by applying GVW braking torque to an empty rear axle; the
correct figure is μ ≈ 0.36 (§4.16) — the gap is real but it is a wet-road
margin issue, not a dry-road impossibility. One flagged the bus-to-wheel
chain as 0.8656 rather than 0.8657; the code uses the exact product. One
claimed the motor-shaft power divides by the reduction efficiency in the
wrong direction; two independent routes agree it does not.

### 9.5 Independently reconfirmed

The 85 km/h cruise load (1,988 N / 46.9 kW), the 20% grade launch force
(13.3 kN), the 5.0 kN direct-path force and its 34.9 km/h floor, the 81.4%
series-efficiency product, the 3.6% neutral downgrade at 95 km/h, the 92%
regen capture at 75 kW on VOLT-SUB, both energy-per-km figures, the 107.8 kW
genset floor, and the 30.2 / 61.0 km/h sustained speeds on a 6% grade — all
recomputed from first principles without this code and matching.
