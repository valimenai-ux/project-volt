# PM_PACKET_KX — WS4 GENSET, KX ROUND (errata + pure-series verification + interface archive)

**STATUS: NOT CONVERGED.** Three rework rounds exhausted; the final
adjudication round is not clean. Per the standing pipeline the workstream
stops here with its full trail and goes to the lead in this state. No fourth
round was run.

Order executed: `WS4_genset/KX_DIRECTIVE.md` (lead-issued, bounded).
Baseline of record: `BASELINE_v5.md`. Prepared by the night-shift foreman
under `NIGHT_SHIFT.md` step B1. **The foreman rules on nothing in this
packet.** Every escalation below is copied complete and verbatim from the
workstream's own report; none is resolved, softened, filtered or
summarised-in-place.

---

## 1. Round trail

| round | worker | foreman gate | adjudication | outcome |
|---|---|---|---|---|
| r1 | delivered 02:20 PDT | **PASS** — 113 artifacts byte-identical, 0 differing, `verify_ws4.py` exit 0 (184 renderings + interface + 413 pins) | `FINDINGS_KX_r1.md` — **NOT CLEAN**, 2 blocking, 3 material, 8 minor | bounced |
| r2 | delivered 04:30 PDT | **PASS** — 116 byte-identical, 0 differing, verify exit 0 (231 renderings + interface + 614 pins) | `FINDINGS_KX_r2.md` — **NOT CLEAN**, 0 blocking, 3 material, 4 minor. All 13 r1 findings closed at root cause; adjudicator states it could not break any of them | bounced (final) |
| r3 | delivered 06:13 PDT | **PASS** — 117 byte-identical, 0 differing, verify exit 0 (252 renderings + interface + 1,585 pins) | `FINDINGS_KX_r3.md` — **NOT CLEAN**, 1 blocking, 3 material, 6 minor | **NOT CONVERGED** |

Commits: `b1c32cd` (r1), `6e429cb` (r1 findings), `479dbce` (r2), `47428e7`
(r2 findings), `90c5bc2` (r3), `afa9cc3` (r3 findings).

Every gate the foreman ran was a sandbox regeneration — the workstream copied
out, the entry point re-run there, and the artifacts byte-diffed against the
committed copies — so no gate could mutate the record.

---

## 2. THE BLOCKING FINDING THE LEAD MUST READ FIRST

`FINDINGS_KX_r3.md` R3-B1, and it has a live downstream consumer.

R20 declares the radiator sizing case to be **the R6 corner**. The case WS4
enumerated as `alt2000m_45C` is the R6 corner's *ambient* (2,000 m / +45 °C)
at GVW, CdA 4.2, 2 kW aux — **not** R6's corner, which is +20 % payload,
CdA 5.4, 4 kW aux. The R20/ESC-12 analysis is therefore enumerated over a
case set that excludes R20's own declared design case.

Round 3 **did run** R6's actual corner — as
`r6_rating_family_probe → cases → r6_rating_corner_full`, for a different
purpose (ESC-10). Its 8-seed radiator-package 2-minute maximum is
**103.522 kW against R20's 95.018 kW design point, at the same +45 °C
ambient: +8.95 %.** No capability model, assumption or ruling is needed for
that comparison — both numbers are already in the workstream.

Folded into WS4's own declared ITD model, per the adjudicator:
- `all_cases_within_capability` goes **true → false at all four declared top tanks** (corner ratio 1.0884–1.0888);
- the **116.8 °C crossover ceases to exist** — the corner governs everywhere;
- the capability break-even moves **158.4 °C → 45.55 °C**, reversing ESC-12's own statement that "on the capability question the r2 conclusion probably is right".

The 103.522 kW figure is **unreachable from `interface_ws4`** (the probe's
projection carries no heat field), **absent from `heat_ledger_ws6`**, absent
from the R20 comparison, and absent from ESC-12.

**WS6 is the named consumer and has not run.** The foreman has held WS6
(NIGHT_SHIFT B4) rather than start it against this block. See §6.

---

## 3. Headline numbers, verbatim, with citations

All values copied from the data file, not transcribed from prose. The foreman
adds no number of his own anywhere in this packet.

**`series_duty_v2` — `_status: live_design_input`**
(`WS4_genset/results_ws4.json:27223`; report block `REPORT_WS4.md:2456`)

| case | fuel energy kWh/km min / median / max | governing case (min) |
|---|---|---|
| `nominal` | 1.7010084250276258 / 1.7153581462494394 / 1.728099220748916 | `seed 23 of the enumerated 8-seed VOLT-REG ensemble [nominal]` |
| `cda_5.4` | 2.018848800489633 / 2.0320008359694812 / 2.0378064476340145 | `seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]` |
| `alt2000m_45C` | 1.4131393969351607 / 1.4217595332112802 / 1.4260734657051741 | `seed 23 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C]` |

Payload companion, per payload tonne-km, min / median / max: `nominal`
0.586554629319871 / 0.5915028090515309 / 0.5958962830168676; `cda_5.4`
0.6961547587895286 / 0.7006899434377523 / 0.7026918784944878;
`alt2000m_45C` 0.48728944721902095 / 0.4902619080038897 / 0.4917494709328187.
**ESC-7 attaches to this companion — see §4.**

**Unserved bus energy** (`results_ws4.json:10651`, mirrored at `:27371`):
`per_case_max_kWh` = `{"nominal": 0.0, "cda_5.4": 0.0, "alt2000m_45C": 0.0}`,
`worst_case_kWh` = `0.0`, `all_cases_zero` = `true`, and
`worst_case_governing_case` = `"no governing case - every ordered case is
exactly zero on all 8 seeds"`.

This headline survived three adjudications and got **stronger** each time.
Round 2's adjudicator ran 160 runs across five unordered cases and four
dispatch configurations — including engine-capped and R16-pack-enforced
simultaneously — and found 0.0000 kWh unserved on every seed.

**`gate_g1`** (`REPORT_WS4.md:2226`): `status` = `executed_kill_2026-08-30`,
archived, frozen by round 3 to the r1 53-key set with 0 value differences.
No field of it may be consumed as a live requirement.

**Other figures the escalations turn on, as printed in the report:**
ESC-10's exposure `287.1 s` (`REPORT_WS4.md:249`, `:251`; ordered-set maximum
`250.0 s` at `:94`); ESC-8(c)'s worst paired seed `+0.249 %` with its full
R14 label (`REPORT_WS4.md:216`, `:1415`); the ESC-12 crossover `116.8 °C`
(`REPORT_WS4.md:182-183`, `:1682-1684`); the R6-family row
`payload+20pct_cda5.4_sea_level ... 185.0–287.1 ... 0.0000` unserved
(`REPORT_WS4.md:1714`).

---

## 4. ESCALATIONS — COMPLETE AND VERBATIM

Copied byte-for-byte from `WS4_genset/REPORT_WS4.md` §12 (lines 6125–6444).
Nothing added, nothing removed, nothing reordered, nothing paraphrased.

## 12. Escalations

- **ESC-1 (cites R6)** *(unchanged r2; R18 has since adopted the
  corner-delivery form)* — R6's label vs rating-basis inconsistency
  under class-typical derates; the candidate is specified at 132 kW
  and clears the corner by +0.82 kW (PROVISIONAL, §2.1).
- **ESC-2 (cites G1, R7, R11) — RESTATED under G1-R.** The r2 ESC-2
  reported a condition-dependent PASS. Under the ruled conventions the
  gate **fails the ≥5% criterion at every condition** (§6 table),
  worst at the R7 corner (-5.90%). The r2 sentence "even where (a)
  misses the criterion it still *beats* series by ~3.8%, so the
  altitude case weakens the clutch's payback, never its sign" is
  **withdrawn on the G1-R record**: at nominal the sign is reversed on
  all eight seeds, at every other condition the ensemble-min is
  negative, and the sole exception to the reversal is CdA 5.4, where
  the ensemble is break-even (min -0.09% / max 0.12%,
  4 of 8 seeds marginally positive — seeds 4, 7, 8, 9). BASELINE_v2's R11 note recording the r2
  reading (and the WS5 condition-aware mode-policy remedy premised on
  it) is contradicted by these numbers — flagged to the lead for
  disposition alongside the kill decision; see ESC-6.
- **ESC-3 (cites R8, R5)** *(unchanged r2; R19 has since ratified the
  disposition)* — V1 start counts at the R8 floor; GEN-V1 specified as
  ISG either way.
- **ESC-4 (cites R9 / WS6 ledger)** *(unchanged r2; R20 recorded the
  seeds)* — radiator design case is the R6 corner, not the grade hold.
- **ESC-5 (cites R8, supports the E24/R4 record) — RESTATED under
  G1-R.** Pure series on VOLT-REG with the R8 3.5 kWh floor now needs
  505–631 s/cycle of emergency above-pin operation at
  nominal (1,128–1,400 s at CdA 5.4) and completes the nominal
  cycle with 0.00 kWh unserved (r2: up to 0.12 kWh); at CdA 5.4 it
  still sheds 0.00–0.52 kWh on hard seeds (r2: 0.46–0.77).
  The R12 chain *softens* the fallback's buffer problem but does not
  remove it off-nominal, and the R3 rating exposure
  (42.1–71.5 s nominal) is untouched — if the kill fires, the
  V1-with-125-kW-genset still inherits R4's "spine not sized for
  forced series" record; WS1's 7.32 kWh figure remains the honest
  scale for a buffer that must also cover CdA 5.4.
  **KX disposition (R22a): the ENERGY half is CLOSED.** At the
  delivered 11.08 kWh pack, pure series completes all three
  ordered cases with 0.0000 kWh unserved on every seed (§4-KX).
  The POWER half is not closed and is re-raised as ESC-9; the R3 motor
  rating record is unchanged.
- **ESC-6 (new — cites R11, G1-R; for the lead's kill decision)** —
  G1-R reverses the premise on which R11 recorded the WS5 mode-policy
  remedy ("prefer series at density-derated corners"): under the ruled
  chain, series is the better fuel mode at the ensemble median of
  every tested condition except CdA 5.4 (break-even, 0.02%
  median), by -2.50% at nominal up to -5.66% at the corner. If the
  lead spares the clutch on non-fuel grounds (R1 capability, §6), the
  WS5 mode policy should be re-premised on the G1-R condition table —
  lockup approaches parity only where the welded load fraction is
  high (CdA 5.4), which is a *load*-aware, not altitude-aware, policy.
  If the kill executes, ESC-5's restated fallback record applies.
  Either way R11's "~3.8% even at the corner" figure should be
  corrected on the baseline record to -5.90% (sign reversed).
  **Disposed:** BASELINE_v3 executed the kill and recorded the ESC-6
  contradiction (R11's premise void, "ESC-6 accepted"). Retained as
  history.
- **ESC-7 (new — cites R32, D13/R36; for the lead) — THE VEHICLE ZERO
  METRIC IS STILL PER KM.** The KX directive orders fuel energy **per
  km** and §4-KX exports it. R32 says the payload-denominated metric
  "shall be" applied to Vehicle Zero before any Vehicle Zero result is
  described as an efficiency advantage, and R36/D13 restate that per-km
  numbers flatter. WS4 therefore exports a payload companion alongside
  every per-km figure — fuel energy per payload tonne-km at WS1's
  2.9 t payload at GVW (a WS1 *assumption*: curb 3,700 kg on a 6,600 kg
  GVW). It is a companion, not a ruler: WS4 has no ratified Vehicle
  Zero payload basis and does not invent one, and no candidate
  comparison in this report is denominated on it. The lead should
  either ratify a Vehicle Zero payload basis or hold R32 open; WS4 will
  not describe any Vehicle Zero result as an efficiency advantage on
  the per-km number.
  **RESTATED, KX r2 (adjudication M3).** Two corrections. (i) *Which
  curb the 2.9 t belongs to:* it is WS1's **pre-conversion** operating
  curb — 2,900 kg of payload at GVW behind a 3,700 kg
  [WS1-ASSUMPTION] "NPR-HD chassis-cab + 16 ft dry-freight body + driver
  + full fuel/DEF". The **series conversion's** mass (WS3's pack, WS4's
  genset + generator, WS2's spine, less the deleted engine and gearbox)
  is not charged against it. A denominator that does not charge
  conversion mass cannot discharge R32, whose whole purpose — per
  D13/R36, "won 6–10 % per km and gave 6–8 % back in freight" — is to
  charge exactly that. (ii) *The prose now travels with the JSON:* the
  r1 round exported `fuel_energy_kWh_per_payload_tonne_km` with full
  R14 labels and **no** `payload_t`, basis or caveat anywhere in
  `interface_ws4`, so a machine consumer saw a payload-denominated
  metric with no denominator. `_inputs → payload_metric_basis` now
  carries the tonnage, its WS1 source, the fact that it is identical in
  all three cases, and an explicit caveat that the field is the per-km
  field ÷ 2.9 and is not the R32 metric. WS4 keeps the field rather
  than withdrawing it (withdrawal would silently remove an exported
  member two live consumers are reading), and denominates nothing on it.
- **ESC-8 (cites R16, R15, R2; for WS3/WS5/WS6) — RESTATED IN KX r2 ON
  THE PACK QUANTITY, AND WIDENED TO THE READING ITSELF.** *r1 form: the
  curve's hot end crosses WS3's pack-loop sizing line, stated on peak
  **regen** (69.1 kW bus vs 62.2 kW accepted at 55 °C cells).*
  That form understated its own case by roughly a factor of two, and it
  rested on a choice WS4 had made without recording that a choice
  existed (adjudication B1). Restated:

  **(a) Which quantity the curve limits.** WS3's file header says *"pack
  regen-acceptance"* and the column is `V2pack_chg_cont_kW_bus` — a
  **pack** limit; WS3's REPORT_WS3 §4.2 presents the same curve to WS5
  as a **regen-blend** rule. The r1 simulator implemented the blend
  reading, capping the regen leg only, and added the genset's output to
  the pack afterwards without testing it. On the pack quantity the
  constraint is **active on every ordered case**: 39.1–47.0 /
  41.4–58.6 / 13.6–23.8 s per cycle above continuous acceptance,
  longest single excursion 15.4 s — longer than the 10-s pulse
  window that would excuse it — peak pack charge **147.6 kW bus**
  against 130.8 / 129.1 kW accepted. A pack cannot tell where its
  charge current comes from, and the genset is on for a fraction
  0.582–0.601 of cycle time, so this is structural to the dispatch of
  record, not incidental.

  **(b) The hot end — and, corrected in KX r3, the WHOLE curve.** At
  the 45 °C declared cells the ordered run already charges at
  147.5 kW against 129.1 kW continuous. At 50 °C the
  continuous curve falls to **95.0 kW**. At WS3's 55 °C loop ceiling
  the continuous rating is **62.2 kW** and even the **10-s pulse**
  rating is **128.8 kW** — still below this run's peak charge.
  **The stronger statement, which both earlier rounds missed
  (adjudication KX2-M2): this is not a hot-end problem. WS3's continuous
  column peaks at 135.043 kW bus at 10 °C cells and
  the run's peak pack charge is 147.585 kW, so the acceptance is
  exceeded at EVERY ONE of the 19 tabulated cell temperatures
  (-30 °C to 60 °C), by at least 12.542 kW even at the
  curve's most favourable point — and on every seed of every ordered
  case.** There is no cell temperature at which the pack reading is
  satisfied, only a least-unfavourable one. KX r2 exported a
  `cold_side_binding_cell_C_pack_quantity = 10.0` here, which was an
  `np.interp` right-edge **clamp** and read as a non-binding region
  above 10 °C cells; it is withdrawn (§4-KX.4). This makes the ruling
  question sharper, not softer: if the lead rules for the pack reading,
  no cell-temperature limit can rescue the dispatch of record — only a
  supervisor change or a restated interface rating can.

  **(c) What enforcing the pack reading costs**, measured, not asserted:
  worst shed **0.240 kWh** at case cda_5.4 of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within it, seed 9 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4/R16-pack], up to 59.7 s of
  clipping, and unserved bus energy stays **0.0000 kWh** (§4-KX.4).
  The §4-KX.2 headline is invariant under either reading. **Fuel, on the
  paired per-seed statistic (R36; corrected in KX r3, adjudication
  KX2-M3(b)): paired medians +0.169 / +0.207 /
  +0.100 %, and the worst paired seed anywhere costs
  +0.249 % (case cda_5.4 of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within it, seed 5 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]).** The r2 form of this escalation said
  "fuel penalty **at most +0.20 %**"; that figure was a ratio of two
  independently maximised ensemble numbers, **not a bound**, and at
  nominal it carried the opposite sign to six of its own eight seeds.
  The corrected worst is +0.249 %. Nothing in the disposition turns
  on 0.05 pp of fuel — but the lead should be ruling on the right
  number.

  WS4 cannot resolve this and does not: the semantics of WS3's interface
  are WS3's, the cell-temperature trajectory is WS3/WS6's, and the blend
  order is WS5's. **Requested disposition, three parts:** (1) rule which
  quantity R16's continuous column limits — the regen leg or the pack —
  and, if the pack, whether WS5's supervisor must trim the genset or shed
  to the resistor; (2) a ruled maximum cell temperature for dispatch at
  full charge, or an explicit acceptance that hot-corner descents run on
  the resistor; (3) note that WS4's own load-following companion (b′)
  stays inside the acceptance on every seed of every ordered case
  (§4-KX.6) — reported, not recommended.
- **ESC-9 (new — cites R8 as restated by R12/ES-4, R4/E24; for
  WS5/WS3) — THE DELIVERED PACK HAS THE ENERGY, NOT THE POWER.** The
  ordered R22a run completes every case with 0.0000 kWh unserved
  **because the pack's bus-side power envelope is not enforced**: pack
  discharge peaks at 192.5 kW against R8's 125 kW and charge at
  147.6 kW against R8's 110 kW. Enforced as a wall, the run sheds
  up to **0.613 kWh** at case alt2000m_45C of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within it, seed 6 of the enumerated 8-seed VOLT-REG ensemble [alt2000m_45C/R8-envelope] (§4-KX.3). Two aggravations
  on the same record: the bracket uses the *more permissive* 125 kW of
  the two discharge figures on the record (WS3's own compliance gates
  are at 120 kW), and the run spends 825.0–975.0 s/cycle at CdA 5.4
  below the SOC 0.40-of-nameplate band over which WS3 declares
  the discharge peak at all. WS4 reports all of it
  and tunes none of it. Requested disposition: rule whether R8's bus-side
  peaks are a hard envelope (in which case WS5's dispatch must keep the
  pack off the peak, or WS3 must restate the interface rating), or
  whether short excursions of this duration are accepted — and note
  that the archived gate's mode (a) never posed this question, because
  the engine carried the peaks mechanically **on the pack axis** (in
  mode (b) the engine carries peaks too, above its own rating — see
  ESC-10; the r1 closing sentence was incomplete and is corrected here).
  This is R4/E24's "spine not sized for forced series" record extended
  from the R3 motor rating to the pack.
  **ADDED IN KX r2 (adjudication B2), without recommendation:** the
  load-following companion (b′) that this block already carried for
  R22b **satisfies R8's bus-side envelope in both directions, WS3's R16
  acceptance read on the pack, and the engine's own continuous
  flat-rating — on every seed of every ordered case** (pack discharge
  peak 115.6 kW vs 125; charge peak 100.2 kW vs 110; 0.0 s above
  R16 acceptance; 0.0 s above the continuous rating), at a fuel delta of
  +0.169 % / -0.022 % / +1.789 % on the **paired per-case median**
  — which in KX r3 is genuinely the paired per-seed median (§4-KX.6;
  adjudication KX2-M3(a) found the r2 figure was a ratio of ensemble
  medians carrying this same label, and at nominal it read
  +0.062 % against the true +0.169 %). Worst paired seed anywhere
  +1.829 %. The r1 round named "run the genset earlier so the pack
  never has to cover the peak alone" as an abstract remedy and did not
  report that its own companion demonstrates it. WS4 still does not
  choose the dispatch — that is R22b's, and the table does not price
  start transients, aftertreatment temperature or part-load engine duty
  — but the lead should not be asked to rule on this without the
  measurement.

- **ESC-10 (new, KX r2 — cites R18 and ESC-1; for the lead/WS6) — THE
  GENSET RUNS ABOVE ITS OWN CONTINUOUS FLAT-RATING.** In the emergency
  band the simulator caps the engine at the **automotive** full-load
  curve (153.3 kW × derate — the 4HK1-TC hardware figure §2.1 itself
  identifies as automotive), not at the **132.0 kW continuous
  flat-rating** WS4 specifies. Measured over the ordered run: 0.0–146.5 /
  161.8–250.0 / 55.0–66.1 s per cycle above the rating, worst 250.0 s
  (case cda_5.4 of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within it, seed 8 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]), peak shaft **147.9 kW = 112 %** of that
  case's own continuous rating (tied at 112.034 across cases {nominal, cda_5.4} of the enumerated ordered case set {nominal, cda_5.4, alt2000m_45C}; within them, nominal: seed 3 of the enumerated 8-seed VOLT-REG ensemble [nominal] / cda_5.4: seed 23 of the enumerated 8-seed VOLT-REG ensemble [cda_5.4]; the corner reaches
  108.7 % of its derated rating), and the generator exposed on
  the same samples against its 135.0 kW continuous shaft input
  (§4-KX.3).
  **KX r3 — the exposure the lead is asked to rule on is wider than the
  ordered set (adjudication KX2-m4).** 250.0 s is a correct
  ORDERED-SET maximum, and the directive ordered three cases. But R6 —
  the ruling that sets the 132 kW rating — defines its basis as +20 %
  payload, CdA 5.4, 4 kW aux, +45 °C, 2,000 m, and inside that family
  the exposure is **287.1 s/cycle** (case payload+20pct_cda5.4_sea_level of the enumerated R6 rating-family probe set {payload+20pct_cda5.4_sea_level, aux4kW_cda5.4, aux4kW_nominal, r6_rating_corner_full}; within it, seed 5 of the enumerated 8-seed VOLT-REG ensemble [payload+20pct_cda5.4_sea_level/R6-family]), at +20 %
  payload and CdA 5.4 at **sea level**, where the full automotive
  ceiling is available and the load uses it. **The figure this
  escalation puts to the lead is therefore the union maximum over both
  enumerated sets: 287.1 s/cycle** (case payload+20pct_cda5.4_sea_level of the union of the enumerated ordered case set and the R6 rating-family probe set {nominal, cda_5.4, alt2000m_45C, payload+20pct_cda5.4_sea_level, aux4kW_cda5.4, aux4kW_nominal, r6_rating_corner_full}; within it, seed 5 of the enumerated 8-seed VOLT-REG ensemble [payload+20pct_cda5.4_sea_level/R6-family]); §4-KX.8 carries
  the probe. The probe cases are NOT ordered cases and the ordered-set
  maximum is exported unchanged as such. Every probe case still
  completes with 0.0000 kWh unserved.
  Why it matters to the lead specifically: the 132 kW flat-rating is a
  **blocking** R18 datasheet figure and a WS6 release blocker, specified
  as an unlimited-hours prime/COP-class rating with **+0.82 kW** of
  margin at the R6 corner (ESC-1, PROVISIONAL) — and 112 % for
  ~3 minutes also exceeds the 10 %/1 h overload an ISO 8528-1 prime
  rating allows. **This does not touch the §4-KX.2 headline:** WS4 ran
  the bracket, and with the engine held to its own continuous rating in
  the emergency band the run still completes every ordered case with
  **0.0000 kWh** unserved on every seed. What the over-rating buys is
  SOC margin, not feasibility: the CdA 5.4 SOC minimum deepens from
  0.183 to 0.125 of usable, and **fuel does not rise on a
  single ordered seed** (`fuel_rises_on_no_ordered_seed`: True;
  worst paired seed +0.000 %, best -0.170 %) — every ordered
  seed burns slightly *less*, because the capped engine stays nearer its
  island. *(KX r3: the r2 form quoted -0.0566 % here, a ratio of
  ensemble maxima whose "max" was a maximum over three negatives, i.e.
  the least saving, under a name that says penalty. The conclusion is
  unchanged; the statistic is now the paired one — adjudication
  KX2-M3(c).)*
  `engine_continuous_rating_bracket`. Requested disposition: either
  rule that short excursions to the automotive curve are accepted for a
  genset installation — in which case R18's datasheet task should
  confirm the *automotive* curve too, not only the flat-rating — or rule
  that the supervisor must hold the engine to its continuous rating, in
  which case the emergency band's ceiling is a WS5 constraint and the
  bracket above is the cost. WS4 does not choose.

- **ESC-11 (new, KX r2 — cites R34; a clarification request, for the
  lead) — WHAT "ONE TRACE PER RUN" MEANS.** R34 reads "every pipeline
  exports a 10 Hz trace file per run". This pipeline executes
  24 ordered mode-(b) runs plus their (b′) companions plus the
  brackets and sensitivities; the per-**simulated**-run reading would be
  ~132 MB of committed artefact for the ordered set alone, and the
  per-**pipeline**-run reading is satisfied by a single file. The r1
  round emitted one trace and asserted "one per run" without saying
  which reading it meant (adjudication m4). WS4 now **declares** the
  per-pipeline-run reading and, rather than sit on the ambiguity, emits
  3 traces — one per **ordered case** at the reference seed — so
  R34's stated consumer (the WS10 exhibit/simulator) has a full-rate
  witness of each ordered case, with all 24 ordered runs
  covered at 5 s in `data/series_duty_v2_soc_trajectories.csv`. Requested disposition: confirm the
  reading. If the per-simulated-run reading is intended,
  `run_ws4.py`'s `R34_TRACE_ALL_ORDERED_RUNS` constant emits all
  24 with no other change, and the lead should say whether ~132 MB
  of trace belongs in the repository.

- **ESC-12 (new, KX r3 — cites R20 / ESC-4; for the lead and WS6) —
  WS4 CANNOT ESTABLISH THAT THE R6 CORNER IS STILL THE RADIATOR DESIGN
  CASE, AND WILL NOT ASSERT IT.** On absolute HT-package kW the ordered
  pure-series duty does **not** stay inside R20's declared design point
  of 95.0 kW: the 2-minute rolling maximum reaches
  **115.119 kW** — **+21.2 %** above it — at 2
  of the three ordered cases (`nominal`, `cda_5.4`), and the instantaneous peak
  exceeds it at all three (§4-KX.7). The corner case, the only ordered
  case in R20's own +45 °C air, stays under at 86.3 kW.
  **The honest position:** whether R20/ESC-4 survives is a question
  about **capability at each case's own ambient**, and WS4 exports no
  ratified radiator capability-versus-ambient model — it measures duty.
  The KX r2 round resolved this gap by exporting a boolean built from a
  max over a single filtered case, with the scoping argument asserted in
  prose and never quantified (adjudication KX2-M1); that field is
  withdrawn. WS4 has instead **quantified** the argument as a declared
  linear-ITD sensitivity (§4-KX.7): at a 105 °C top tank the worst
  ordered case sits at 0.908 of capability, and the **capability
  break-even** is a **158 °C** top tank, far above any
  physical diesel HT cap — so on the capability question the r2
  conclusion probably *is* right. **The sensitivity also says something
  the r2 round never asked, and it points the other way.** R20/ESC-4
  rules which case *sizes* the radiator, and the ordered cases'
  ambient-normalised ratios **cross at a 116.8 °C top tank**: below
  it `alt2000m_45C` is the design case, above it `cda_5.4` is,
  while every case is still inside capability. 116.8 °C is **inside
  the range a pressurised heavy-duty coolant system can run**, so
  ESC-4's design case is live rather than settled — and a sensitivity
  built on four WS4-declared assumptions is not a basis for a
  machine-readable verdict on a standing ruling either way. WS4 does not
  self-resolve it.
  **Requested disposition, three parts:** (1) rule whether R20/ESC-4's
  "radiator design case = the R6 corner" is retained on the
  ambient-normalised reading, or whether the sea-level high-load cases
  become the sizing case on absolute duty; (2) direct WS6 to publish a
  radiator capability-versus-ambient (and versus air density) curve for
  the declared package, against which this duty can be compared properly
  — WS4's ITD sensitivity is a placeholder for exactly that curve and
  should be replaced by it; (3) rule whether the **2-minute** window is
  the right one for this package, or whether the peak
  (103.5 kW at the corner) or a thermal-mass model governs. Until
  (1) is ruled, WS6 should size against the **absolute** rows in
  `heat_ledger_ws6 → series_duty_v2_transient_vs_R20_design_point →
  cases`, which are exported per case with their governing seeds, and
  **not** against any survival boolean.


*(End of verbatim escalation text from `REPORT_WS4.md` §12, lines 6125–6444.)*

---

## 5. Findings trail — what each round found and what happened to it

**Round 1 — `FINDINGS_KX_r1.md`, NOT CLEAN (2 blocking, 3 material, 8 minor).**
KX-B1: R16's charge-acceptance cap sat inside the regen branch only; the
genset's contribution was added afterwards and never tested, so the pack was
charged above WS3's continuous limit for up to 59 s/cycle (peak 147.6 kW vs
130.8) while the interface exported `bound_any_sample: false`. KX-B2: the (b′)
companion omitted every axis R22b turns on. KX-M1 genset above its 132 kW
continuous rating up to 250 s/cycle, un-exported. KX-M2 the live block could
not resolve its own chain of record. KX-M3 payload metric exported with no
denominator or caveat. Plus m1–m8, one of which (m2) solved the D5
reconciliation the r3 round of this workstream had left open: WS4's headline
F2 exposure figure was ~80 % an artifact of one degenerate `rpm = 0` column in
WS2's map. **All thirteen were closed at root cause in round 2, verified.**

**Round 2 — `FINDINGS_KX_r2.md`, NOT CLEAN (0 blocking, 3 material, 4 minor).**
The adjudicator confirmed every r1 finding genuinely resolved and could not
break any of them. It established, two independent ways, that a blocking R16
correction which moved no exported value was not a contradiction: the counters
read post-hoc, so dispatch cannot move. One of those ways used **only the
committed 10 Hz traces, with no simulator in the loop**. Its three new
materials were all one family — a machine-readable summary whose construction
does not match its name — and **KX2-M3 was an R36 regression**: a ratio of
medians labelled "the paired per-case median" (+0.062 % exported vs +0.169 %
paired), and a bracket figure that flipped sign. **All seven closed at root
cause in round 3, independently re-derived, except KX2-m1 (partial) and
KX2-M1 (resolved as named, but its remedy carries R3-B1 and R3-M1).**

**Round 3 — `FINDINGS_KX_r3.md`, NOT CLEAN (1 blocking, 3 material, 6 minor).**
R3-B1 is §2 above. R3-M1: the ambient-normalised sensitivity exists on the
2-minute window only, its verdict fields carry no window in their names, and
on windows ≤ 60 s the ordered corner is 8.87 % over capability at every top
tank. R3-M2: the sea-level cases' air temperature is 21.006 °C in the R20
block and 25.0 °C in the R16 block, whose basis string says "declared equal to
ambient". R3-M3: the round's own tie-handling helper was not applied to every
case-set extremum — 8 fields / 19 occurrences still emit raw first-key
tie-breaks, two of them full three-case ties at exactly 0.0, in a block the
round's sweep certifies CLEAN.

**On the round-3 sweep, which the foreman had specifically ordered.** It
worked: it found two defects the round-2 adjudication had not named, one of
them `r22d_coast_spin_member.unbooked_pp_max` — built from three
independently extremised quantities, rendered as "at most X pp", and the one
member WS5 consumes live. But the foreman also asked the r3 adjudicator to
spot-check the sweep's own sixteen "examined and clean" certifications, and
**two of those certifications are false**:
`companion_bp_capability_comparison.axes[*]` contains the very defect it
certifies clean, and "make_report_ws4.py arithmetic: exactly three
expressions" understates by more than half, one of them dividing by a
hand-transcribed literal `78.85`.

**One act of restraint, confirmed correct.** Round 3 declined to "fix"
`gate_g1_one_factor.*.delta_pp_min`, arguing the name honestly says it is a
difference of ensemble minima and the values are BASELINE_v3-ratified record.
The r3 adjudicator confirms the restraint was right, for a stronger reason
than the round gave: the archived rows close exactly on the min-to-min shift
of record (6.261346 − 8.842991 = −2.5816447) while the paired construction
gives −2.9416 and does not close.

---

## 6. CROSS-WORKSTREAM OBSERVATIONS (observations, not rulings)

1. **WS6 has not run and R3-B1 lands squarely on what it would consume.**
   `§4-KX.7` tells WS6 to size against this block, WS4 has withdrawn its R20
   survival verdict (ESC-12) rather than assert it, and the R6-corner figure
   that the r3 adjudicator says changes the answer (103.522 kW vs the
   95.018 kW design point) is absent from `heat_ledger_ws6` and unreachable
   from `interface_ws4`. The foreman held WS6 rather than start it against
   this block. Starting it is a lead decision, not a foreman one.
2. **WS11 consumed this workstream live and is unaffected numerically.**
   WS11's recorded pins are `ws4_sim.py` `de25e3da1fd2bb1ae5c8be3b590bd7f51c7cbba3143306957e0965b87a191632`
   and `results_ws4.json` `29d4a425795656ec9d32f066af17e92472b72e51596825c7475652b8771ae0e9`.
   `ws4_sim.py` is **byte-identical after round 3**, so WS11's hot-swap
   assertion (that it reproduces `series_duty_v2[nominal]` at 0.0e+00) still
   holds. `results_ws4.json` has since re-hashed to
   `b02a6c82fbbe8d3e006fb1d756fbee51b2cb04f50e4281c65e04c97e63876d0b`;
   WS11's r2 worker was notified in flight to re-pin.
3. **WS5 consumed a member that round 3 corrected, and was notified in
   flight.** `WS5_controls/run_ws5.py:1031` reads
   `R22D_NOTE["measured_on_series_duty_v2"]["unbooked_pp_max"]`, which moved
   from `0.000336470735977268` to `0.00033954581949763416` when round 3
   re-priced it per seed. The foreman handed WS5 the corrected vintage while
   its worker was still running rather than bouncing it afterwards.
4. **Round 3 restated two escalations onto numbers that had been wrong.**
   ESC-10's exposure rose `250.0 s → 287.1 s` on a measured union set, and
   ESC-8(c)'s bound moved `+0.20 % → +0.249 %` with its nominal figure
   flipping sign from a saving to a cost on 6 of 8 seeds. The lead is now
   ruling on the worst numbers available rather than the first ones reported.
5. **WS9's pre-adjudication independently flagged this workstream as a moving
   target.** `WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md` PRE-M1 records
   that `WS4_genset/ws4_chain.py` changed under WS9 between its two runs, and
   that WS9's pin table does not cover every sibling source it reaches.
   Recorded here as an observation because it concerns this workstream's
   volatility during the night, not its content.

---

## 7. What the foreman did NOT do

- Did not run a fourth round. The pipeline caps rework at three.
- Did not resolve, soften, filter or summarise-in-place any escalation.
  §4 is byte-for-byte from the report.
- Did not rule on R3-B1, on ESC-12, or on whether NOT CONVERGED here is
  ratifiable in part.
- Did not start WS6 against the disputed block.
- Did not add a single number of his own to this packet.

**Ratification-ready? No.** This packet is trail-complete, not
ratification-ready. The lead takes it from here.
