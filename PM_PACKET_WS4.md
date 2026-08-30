# PM_PACKET_WS4 — genset + Gate G1

Foreman packet for lead ratification. Compiled 2026-08-29. All numbers
below are copied verbatim from WS4's own artifacts, cited to file and
line; the foreman adds no numbers of his own.

## Status: READY

- Rounds used: 2 of 3.
- Findings trail:
  - r1 (WS4_genset/FINDINGS_WS4_r1.md): 0 blocking, 2 material
    (F1 stale 1.9 kWh figure in ESC-5; F2 interface exported an
    unconditional `gate_g1.passes: true` while the report's own R7
    corner case fails the criterion), 5 minor (F3–F7). Bounced.
  - r2 (WS4_genset/FINDINGS_WS4_r2.md): "no blocking or material
    findings. No new findings of any severity. All seven round-1
    findings are genuinely resolved". Clean.
- Mechanical verification (foreman, both rounds): pipeline regenerates
  results_ws4.json, REPORT_WS4.md, all 5 data CSVs byte-identical from
  the entry point; interface block parses and is byte-equal to
  `results_ws4.json → interface_ws4`; worker's verify_ws4.py passes
  (71 checks r2); independent prose-number audit clean.

## Headline numbers (verbatim from the report)

REPORT_WS4.md lines 19–26:

> **Headline: GATE G1 PASSES at the nominal condition — the locked path
> with charge-bias load-point shifting beats pure series at the pinned
> BSFC point by 6.26% (ensemble minimum) / 6.45% (median) / 6.78% (max)
> net fuel energy over VOLT-REG, against the ≥5% kill criterion. The
> clutch survives — but not everywhere: at the R7 envelope corner
> (2,000 m, +45 °C) the margin falls to 3.75%–4.15%, below the
> criterion, while heat alone (sea level, +45 °C) holds 5.94%–6.42%,
> above it. See §4 and Escalation ESC-2.**

REPORT_WS4.md line 125 (V2 candidate row):

> | **4HK1-V2C (SELECTED)** — 4HK1-TC genset recalibration | 5.19 L | 153 kW | **132 kW** | **122.9 kW** | **+0.82 kW** | ~500 kg |

REPORT_WS4.md line 151 and results_ws4.json (interface line 491 of the
report): R6-corner compliance status is **PROVISIONAL** — "the +0.82 kW
margin rests on the WS4-proposed 132 kW continuous flat-rating and the
WS4-declared class-typical derate model, both TBC against the procured
datasheet (ESC-1; adjudication r1 F5). Do not release WS6 packaging
against this margin until both are confirmed."

REPORT_WS4.md lines 364–367 (heat ledger to WS6):

> | | electrical chain — WS4 maps recompute | **17.9 kW** (of which generator 4.6) |
> | | engine radiator package (coolant+oil+CAC) | **77.2 kW** |
> | **V2 R6 corner continuous (THE radiator sizing case: 45 °C, 2,000 m, 122.9 kW shaft)** | engine radiator package | **95.0 kW** |

REPORT_WS4.md lines 315–317 (V1 start-stop):

> 8-seed ensemble at the 0.8 kWh share: **57–74 starts per 8 h shift**
> [...] confirmed, not relieved, at the R8 floor. Start-stop saves **6.2%**

## ESCALATIONS (copied verbatim and complete, REPORT_WS4.md §12, lines 601–646)

- **ESC-1 (cites R6)** — R6's "125 kW continuous shaft" label and its
  own rating basis ("deliver 122.1 kW at the corner") are inconsistent
  under class-typical derates: 125 kW continuous delivers 116.4 kW at
  the corner (factor 0.9312). The rating-basis clause is the real
  requirement; the label should read "≥131 kW continuous (SL), or
  flat-rated to hold ≥122.1 kW at 2,000 m/45 °C". WS4's candidate is
  specified at 132 kW and clears the corner by +0.82 kW. Recommend the
  baseline text adopt the corner-delivery form. (Not a challenge to the
  corner value itself, which is locked and honoured.)
- **ESC-2 (cites G1, R7)** — G1 passes at the nominal condition (6.26%
  ensemble minimum ≥ 5%), at CdA 5.4 (8.22%), at 4 kW aux (6.46%) and
  on the standalone hot day (sea level, +45 °C: 5.94%; added per
  adjudication F4), but at the R7 envelope corner (2,000 m, +45 °C)
  the margin is 3.75%–4.15%, below the criterion — the failure needs
  the altitude+heat combination; heat alone does not produce it. The
  gate as written does not say at which condition it is judged;
  `interface_ws4 → gate_g1` now exports the full condition set (F2).
  WS4 reports PASS on the plain reading (VOLT-REG, nominal baseline
  parameters) and asks the lead to ratify that reading — noting that
  even where (a) misses the criterion it still *beats* series by
  ~3.8%, so the altitude case weakens the clutch's payback, never its
  sign.
- **ESC-3 (cites R8, R5)** — At R8's 1.5 kWh V1 floor, the start-stop
  hysteresis share that R8's own superposition permits (~0.8 kWh)
  yields 57–74 engine starts per 8 h shift (~14,000–18,500/year).
  Recommend either (i) WS3 raises V1 usable to ~3.0 kWh (33
  starts/shift), or (ii) the programme accepts the count and GEN-V1 +
  engine are specified for ≥20,000 warm ISG starts/year. WS4 has
  specified the generator-as-starter either way.
- **ESC-4 (cites R9 / WS6 ledger)** — Replace the ledger's "~99 kW
  engine rejection" placeholder: the energy balance gives 77.2 kW
  radiator package at the grade hold, and the true radiator sizing case
  is the R6 corner at 95.0 kW **in 45 °C air**, concurrent with
  17.9 kW of low-temperature electrical-chain heat (WS4 map recompute
  of WS1's 20.2 kW, which stays of-record until WS2's measured maps
  land).
- **ESC-5 (cites R8, supports the E24/R4 record)** — Pure series on
  VOLT-REG with the R8 3.5 kWh floor needs 484–805 s/cycle of emergency
  above-pin operation at nominal (1,504–1,734 s at CdA 5.4) and still
  sheds unserved bus energy on hard seeds: up to 0.12 kWh at nominal
  and up to 0.77 kWh at CdA 5.4 (8-seed range 0.46–0.77 kWh; the
  1.9 kWh previously quoted here was a stale pre-D2 number and is
  withdrawn — changelog F1). If the lead ever exercises G1's kill
  clause, the V1-with-125-kW-genset inherits a buffer problem R8's
  floor does not cover — WS1's 7.32 kWh forced-series figure is the
  honest scale.

## CROSS-WS OBSERVATIONS (stated as observations only; the lead rules)

Compiled against the WS2/WS3 round-2 reports on disk (their round-2
adjudications were still in flight when this packet was written; see
PM_LOG.md for their final state and the other packets for the mirror
view).

1. **DC bus voltage windows barely overlap.** WS2 proposes operating
   300–435 V, nominal 370 V (REPORT_WS2.md §9 interface `dc_bus`).
   WS3's r2 interface declares operating 432.0–748.8 V, preferred
   nominal 662.4 V (REPORT_WS3.md §5 interface `bus_voltage_window`).
   The overlap is 432.0–435 V. WS3's ES-3 argues a 400 V-class string
   fails its warm 120 kW pulse; WS2's trade argues 800 V-class forces
   190–296 cells in series. WS4's rectifier/generator design inherits
   whichever window the lead reconciles; WS4's report declares its
   generator spec basis in its interface block.
2. **V1 buffer / start-count assumptions differ between WS4 and WS3.**
   WS4's ESC-3 computes 57–74 starts/shift at the ~0.8 kWh hysteresis
   share permitted by R8's 1.5 kWh V1 floor, and recommends WS3 raise
   V1 usable to ~3.0 kWh. WS3's delivered pack already allocates
   3.0 kWh of genset hysteresis for V1 within 11.08 kWh usable
   (REPORT_WS3.md §5, `soc_strategy.allocation.V1`), and its ES-5
   reports 16–25 starts/shift on that band. The two workstreams'
   start counts are computed on different hysteresis bands; WS4's
   recommendation (i) appears satisfied by WS3's delivered design,
   pending the lead's reconciliation.
3. **Electrical-chain heat ownership is unsettled across three
   ledgers.** WS1's 20.2 kW grade-hold figure stays of-record; WS4
   recomputes 17.9 kW; WS2's r2 ledger carries its chain members and
   its new escalation WS2-E7 asks who owns WS1's 3.0 kW
   power-electronics stage (WS2 traction side vs WS4 rectifier side).
   The WS6 ledger will inherit whichever allocation the lead rules.
4. **Brake-resistor cooling medium conflict.** WS3's interface
   requests "mount the R2 brake resistor on the pack coolant circuit
   so it doubles as the preconditioning heat source"
   (REPORT_WS3.md §5, `coolant.request_to_WS2_WS6`). WS2's delivered
   resistor design is forced-air, "deliberately not coolant"
   (REPORT_WS2.md §5). The two designs are incompatible as delivered.
5. **Coolant/radiator concurrency at the hot corner.** At +45 °C the
   ledger entries that coexist are WS4's 95.0 kW radiator package (R6
   corner) + 17.9 kW electrical chain, WS2's LT-loop worst case
   10.22 kW (V2-speed crawl, per WS2's round-3 interface, conditioned
   on WS2-E1) with 12 L/min ≤65 °C request, and WS3's pack loop
   1.41 kW at 8 L/min. Stated here only as the set WS6 will inherit;
   no aggregation performed by the foreman. (This observation was
   updated after WS2's round 3 superseded its earlier 8.75 kW member;
   see PM_PACKET_WS2.md.)

## Paths

- Report: WS4_genset/REPORT_WS4.md
- Data of record: WS4_genset/results_ws4.json
- Findings: WS4_genset/FINDINGS_WS4_r1.md, WS4_genset/FINDINGS_WS4_r2.md
- Maps: WS4_genset/data/ (BSFC + generator maps, labeled constructed)
