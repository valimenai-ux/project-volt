# PM_PACKET_WS3 — battery pack

Foreman packet for lead ratification. Compiled 2026-08-29. All numbers
below are copied verbatim from WS3's own artifacts, cited to file and
line; the foreman adds no numbers of his own.

## Status: READY

- Rounds used: 2 of 3.
- Findings trail:
  - r1 (WS3_battery/FINDINGS_WS3_r1.md): 1 blocking (F1 — the exported
    532.8 V bus floor and the cold R8 availability gates were jointly
    unsatisfiable), 1 material (F2 — stored-side vs terminal-side power
    conventions mixed inside the ES-4 comparison), 4 minor (F3–F6).
    Bounced.
  - r2 (WS3_battery/FINDINGS_WS3_r2.md): "No blocking or material
    findings." All six r1 findings verified genuinely resolved — F1 by
    full recomputation of the window/gate set from first principles.
    Two new minors (N1, N2) touch no exported interface member; the
    adjudicator's verdict: "The interface block as delivered is safe
    for WS2 to freeze the bus window against." Clean.
- Mechanical verification (foreman, both rounds): pipeline regenerates
  results.json, tables_ws3.md, regen_acceptance.csv, REPORT_WS3.md
  byte-identical from the entry point; interface block parses and
  equals `results.json → interface_WS3`; independent prose-number audit
  clean (all headline numbers trace to the data file).

## Headline numbers (verbatim from the report)

REPORT_WS3.md lines 16–33 (summary):

> **Summary of what WS3 proposes.** One pack serves both variants: a
> **288s1p string of 23 Ah LTO prismatic cells** (SCiB 23 Ah class),
> 15.24 kWh nameplate, 662 V nominal, ~281 kg, ~185 L, liquid-cooled.
> Power-first sizing (R8) plus the 650 V-class bus window means the energy
> comes along for free: 11.08 kWh usable at the bus against floors of 3.5
> (V2) and 1.5 kWh (V1). The R8 peaks land at ~9C pulse / 3.2C continuous
> on this pack — inside power-cell ratings, resolving E8's 93–113C alarm
> by construction. The chemistry is chosen by the cold-charge criterion:
> a cold-soaked LTO pack at −10 °C still accepts 67 kW continuous at the
> bus, which is **more than the full 75 kW wheel-cap regen delivers**
> (64.9 kW), so the R7 cold case — all of VOLT-SUB's braking to friction,
> V1 genset average +48% — collapses to an accessory-load penalty of
> +20–25%.
> The R2 descent-charge duty at +45 °C peaks the cells at 50.3 °C against
> a 55 °C ceiling with a 1.4 kW coolant load. Graphite-anode alternatives
> (high-power LFP, NMC) would need a 128–214 kWh pack to match the cold
> acceptance, or a preconditioning dependency the baseline's own cold case
> warns against.

Voltage window (REPORT_WS3.md §6 ES-3, lines 816–818, matching the
interface block at §5): "662.4 V nominal, operating 432.0–748.8 V (10-s
charge transients to 777.6 V), granularity 12 cells (27.6 V)."

## ESCALATIONS (copied verbatim and complete, REPORT_WS3.md §6, lines 785–857)

### ES-1 — The 24-minute 50 kW charge cannot be an energy requirement *(cites R2, R8; baseline text)*

50 kW × 24 min = 20.0 kWh stored — more than any buffer-scale pack
holds (this one: 11.08 kWh usable). WS3 has implemented the requirement
as a **capability**: the pack sustains 50 kW charge at the terminals,
thermally and electrically, for the full 1,440 s over the whole R7
envelope (T4). Energetically, the SOC ceiling arrives after 384 s
unmanaged (498–1,017 s in the real §4.6 rows) and R2's own blend order
then hands the flow to the resistor, with friction untouched. Requested:
one sentence in the baseline confirming the capability reading, so no
future reviewer scores the pack against 20 kWh.

### ES-2 — R7's preconditioning mandate is over-strict for the selected chemistry *(cites R7)*

R7: "Pack preconditioning required below 0 °C." That sentence was
written against a graphite-anode assumption. The data (T3, T5,
regen_acceptance.csv): a cold-soaked LTO pack at −10 °C accepts 67.0 kW
continuous at the bus — above the 64.9 kW the capped regen path can
deliver — and the R8 transients are fully available from 0 °C (charge)
and −5.5 °C (discharge). Proposed amendment: *preconditioning required
below −15 °C cell temperature (outside the R7 ambient envelope);
between −15 and +10 °C, dispatch permitted with the published derate
curves; heater sized 8 kW either way.* This buys back 4–10 minutes of
availability per cold start and removes a single point of failure (a
truck with a broken heater is currently forbidden to move at −5 °C).
The gate temperatures cited here are valid against the exported
432.0 V operating floor; a higher WS2 electronics floor derates them
per T12. WS3 complies with R7 as written until ruled otherwise.

### ES-3 — Bus voltage window: 650 V class; the full-power floor is 432 V; the 400 V fallback is not benign *(cites R8; for the WS2 reconciliation)*

Stated preference per the assignment: 662.4 V nominal, operating
432.0–748.8 V (10-s charge transients to 777.6 V), granularity 12
cells (27.6 V). Round 1 exported a 532.8 V operating floor — an
undocumented 1.85 V/cell allocation — beside cold gates whose physics
run to 437.5 V; the adjudicator correctly scored that jointly
unsatisfiable (WS3-r1-F1). Resolution: the exported floor is now the
cell floor the gates are computed against, and T12 hands WS2 the
explicit floor-vs-availability trade (432 V ⇒ 120 kW from −5.5 °C at
274 A; 532.8 V ⇒ only from +9.0 °C). The reconciliation should still
know the low-voltage alternative fails outright, not gracefully: a
174s1p (400 V-class) string of the same cell delivers 110.1 kW warm
(< 120 kW R8) and accepts 40.5 kW cold (< 64.9 kW cap); the 2P fix
doubles pack energy and cell mass. The 252s end of the offered series
range is a computed bound in the interface block, not an interpolation
— its gates sit warmer (−1.5 / +4.5 °C) at higher current (245 A
warm). If WS2's inverter/chopper prefers < 500 V at full power, the
pack grows ~×2 — that trade belongs on the record before the voltage
is frozen.

### ES-4 — R8's transient peaks should be restated as ensemble envelopes, in a declared convention *(cites R8, R9)*

R8 fixes "120 kW discharge / 110 kW charge" from the reference draw —
a *stored-energy-side* number in WS1's ledger (120.292 kW stored =
116.7 kW at the bus terminals). The 8-seed ensemble (R9's own
convention) reaches **124.6 kW at the bus = 128.4 kW stored-side**: a
like-for-like exceedance of +6.7% at the bus. Round 1 understated this
by comparing across conventions — mixing exactly the 0.97 factor WS1's
ledger exists to kill (WS3-r1-F2, now stated in both conventions
everywhere). The delivered pack covers the envelope either way (182 kW
warm). Recommended restatement, for WS2's inverter and WS5's
supervisor limits: **125 kW discharge / 110 kW charge, explicitly
bus-side**, per R9's rule that extrema from stochastic inputs are
ensemble envelopes, not draws.

### ES-5 — V1 start-stop closes E6 with the delivered pack *(cites R5; information to WS4/WS5)*

Power-sizing hands V1 11.08 kWh usable at no extra cost. A 3.0 kWh
hysteresis band at a 35 kW bus fixed point yields 2.1–3.1 genset starts
per hour (16–25 per shift) against E6's 82 — inside R5's "E6 start-stop
logic applies" with no additional hardware. WS4 can hold the ~50 kW
class and pick its BSFC island; WS5 gets the band and fixed point in the
interface block.

## CROSS-WS OBSERVATIONS (stated as observations only; the lead rules)

Same set as PM_PACKET_WS4.md §CROSS-WS, from WS3's side:

1. **DC bus voltage windows barely overlap.** WS3 (this packet):
   operating 432.0–748.8 V, nominal 662.4 V, with the T12 derate table
   pricing higher electronics floors. WS2: operating 300–435 V, nominal
   370 V, 750 V SiC device class. Overlap as exported: 432.0–435 V.
   Each side's report quantifies the cost of the other's class (WS3
   ES-3: 400 V-class string fails R8 warm and cold; WS2's trade: 800 V
   class forces 190–296 series cells). Reconciliation is the lead's.
2. **V1 buffer / start-count assumptions differ between WS3 and WS4.**
   WS3 ES-5: 16–25 starts/shift on a 3.0 kWh hysteresis band from the
   delivered 11.08 kWh usable. WS4 ESC-3: 57–74 starts/shift at the
   ~0.8 kWh share permitted by R8's 1.5 kWh V1 floor, recommending WS3
   raise V1 usable to ~3.0 kWh. WS4's recommendation (i) appears
   satisfied by WS3's delivered design; the two start counts are
   computed on different hysteresis-band premises.
3. **Brake-resistor cooling medium conflict.** WS3's interface requests
   the R2 brake resistor be mounted on the pack coolant circuit as the
   preconditioning heat source (`coolant.request_to_WS2_WS6`). WS2's
   delivered resistor is forced-air, "deliberately not coolant". The
   two designs are incompatible as delivered.
4. **Convention alignment pending a ruling.** WS3 ES-4 (bus-side
   restatement of R8 peaks) and WS2's E7 (ownership of WS1's 0.97
   power-electronics stage) both ask the lead to pin the same class of
   convention — where on the electrical chain a quantity is stated —
   before WS5 supervisor limits and the G1 record consume them.

## Paths

- Report: WS3_battery/REPORT_WS3.md
- Data of record: WS3_battery/results.json
- Findings: WS3_battery/FINDINGS_WS3_r1.md, WS3_battery/FINDINGS_WS3_r2.md
- Downstream data files: WS3_battery/regen_acceptance.csv (WS5),
  interface block in REPORT_WS3.md §5 / results.json `interface_WS3`
