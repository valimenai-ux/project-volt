# FINDINGS — WS3 BATTERY PACK — review round 1

Adjudicator, fresh context, 2026-08-29. Basis: BASELINE_v1.md (read in full), WS3_battery/ASSIGNMENT.md, REPORT_WS3.md, results.json, tables_ws3.md, regen_acceptance.csv, run_ws3.py, ws3_cells.py, ws3_pack.py, make_report.py, and the ratified WS1 record (results.json + volt_* modules + REPORT_WS1.md §4.6/§4.15/E6/E8).

## Verification performed

- **Determinism: PASS.** Re-ran the delivered pipeline (`.venv/bin/python run_ws3.py && .venv/bin/python make_report.py`). results.json, tables_ws3.md, regen_acceptance.csv and REPORT_WS3.md regenerate **byte-identical**.
- **Three-way interface check: PASS.** The machine-readable block in REPORT_WS3.md == the block in tables_ws3.md == `json.dumps` of results.json → `interface_WS3`, verbatim (string equality).
- **Independent re-derivations (own implementations / hand calcs, not the worker's code paths):** cold acceptance 67.0 kW bus / 77.4 kW wheel at −10 °C (hand: 66.98 from the declared 4C table, 92 A, 2.6× resistance); voltage-window arithmetic (662.4 / 748.8 / 777.6 / 27.6 V); usable 11.0836 kWh = 15.2352 × 0.75 × 0.97; mass 280.52 kg, volume 185.47 L; literal 50 kW × 24 min at +45 °C → peak 50.3 °C, end heat 1.410 kW, steady 51.8 °C (own integrator, matches to 0.1 K / 1 W); descent 25 km/h split 5.39 / 2.24 / 0.00 kWh, ceiling at 1017 s (own integrator, exact); preconditioning 250 s / 500 s / 1.11 kWh (own integrator, exact); V2 8-seed terminal peaks 90.7–124.6 kW dis, 71.9–72.7 kW chg and V1 start-stop 97.9 kW chg / 84.5 kW dis / 2.1–3.1 starts/h (own supervisor implementation on WS1's modules, exact); life 8.83 / 15.74 yr (independent arithmetic from per-seed damage); chemistry-trade 213.8 / 127.7 kWh cold-match packs (hand); C-rates 9.13C / 210 A, 6.49C, 3.17C / 73 A (hand); R8 temperature gates −5.5 °C / 0.0 °C (hand, from the voltage-limit identities); frontier rows 10.05 / 14.28 / 6.62 / 29.81 kWh (hand); WS1 cross-refs (+48% → 15.005 kW cold N2, 3.612 kWh cold friction, 45.565 kW worst §4.6 row → 39.44 kW at bus, E8's 93–113C, E6's 82 starts, 55% target) all verified against the WS1 record.
- **Compliance:** 8-seed ensemble convention applied to every stochastic extremum (T6/T7); part-load resistance/acceptance/OCV tables plus an efficiency map replace scalars (R9); heat reported to the WS6 ledger by component and case; all five assignment tasks and all three required sensitivities present, plus a 400 V-class bus sensitivity; all five escalations cite rulings (R2/R5/R7/R8/R9). The disclosed single divergence from WS1 (V2 ③ ensemble max 1.367 vs 1.381 kWh, two-pass vs single-pass i-MMD split) is accurately described: WS1's ensemble loop (run_ws1.py §4f) does call `v2_direct_share` without the generator-reserve second pass.

Two findings of consequence (one blocking, one material), then minors.

---

## WS3-r1-F1 — BLOCKING. The exported bus-voltage window is mutually inconsistent with the exported cold-availability gates

**What is wrong.** The interface block hands WS2 two members that cannot both be true:

- `bus_voltage_window.operating_min_V = 532.8 V` (repeated in §5 prose), with rationale "1P string at 650 V class keeps R8 peaks at ~210 A";
- `r8_compliance.dis_120kW_over_SOC_40_90 = −5.5 °C` and `chg_110kW_over_SOC_15_85 = 0.0 °C` (repeated in T5 "dispatch gates"), i.e. the full R8 transients are declared available well below +10 °C.

The pack's own model says delivering 120 kW at the declared cold gates drives the bus far below the declared operating minimum, because the capability at those gates is computed against the **cell floor 1.50 V/cell = 432 V**, not the declared 1.85 V/cell = 532.8 V:

| 120 kW discharge at | pack current | bus voltage |
|---|---|---|
| +25 °C, SOC 0.40 (R8 check point) | 210 A | 571.8 V |
| +10 °C, SOC 0.40 | 223 A | 539.0 V |
| 0 °C, SOC 0.40 | 245 A | 489.3 V |
| −5.5 °C, SOC 0.40 (the exported gate) | 274 A | **437.5 V** |

(Values from the delivered model, `Pack.solve_current`; hand-checked. Even warm, 120 kW at the dispatch-window bottom SOC 0.15 sits at 527.7 V, below the declared minimum — mitigated only by the gate being declared over SOC 40–90.)

If WS2 freezes an inverter/chopper design at V_min = 532.8 V and ~210 A, it cannot execute the cold dispatch the same block declares: enforcing 532.8 V as a hard floor moves the true 120 kW availability gate from −5.5 °C to roughly +5…+10 °C, and honoring the −5.5 °C gate instead requires the electronics to work down to ~435 V at ~275 A (+30% current over the rationale's figure). The 1.85 V/cell basis for 532.8 V appears nowhere in the report — it is an undocumented constant (`run_ws3.py` §11, `operating_min_V=packV2.ns * 1.85`).

**Why it matters.** The voltage window is the single most consumed WS3 output — WS2 is reconciling the DC bus in parallel right now, and the brake-resistor chopper (R2) and WS5's dispatch limits both inherit it. This is the same defect class that was blocking in WS1: a machine-readable interface member that disagrees with the physics the same report establishes.

**What would resolve it.** One self-consistent set, in prose, interface block and results.json together — either (a) lower `operating_min_V` to the true full-power floor at the exported gates (~435 V; the hard cell floor is 432 V) and correct the rationale's current figure for cold, or (b) keep 532.8 V, recompute the `r8_compliance` gates with the 1.85 V/cell floor (which will move the 120 kW gate to ~+5…+10 °C and should be reflected in T3/T5 and ES-2's argument), or (c) declare a separate transient-minimum voltage with an explicit power-vs-bus-voltage derate for WS2/WS5. State which member governs. Note also that the offered `acceptable_series_range` 252–288 shifts every gate/current figure (~+14% current at 252s); one sentence bounding that would spare WS2 a wrong interpolation.

---

## WS3-r1-F2 — MATERIAL. Stored-side and terminal-side battery-power conventions are mixed without disclosure, inside the number ES-4 asks the lead to rule on

**What is wrong.** WS1's `battery_peak_discharge_kW = 120.292` — the origin of R8's "120 kW" — is a **stored-energy-side** rate (WS1 `battery_trace`: discharge `p_batt = net / 0.97`), equivalent to 116.68 kW at the bus terminals. WS3's T6 ensemble peaks (124.6 kW) and ES-4 are **terminal/bus-side** (`terminal_power_from_ws1` correctly multiplies by 0.97). The report reproduces 120.292 in §7.2 and then compares 124.6 against "R8's 120 kW" in T6/ES-4/§7.1 as if they were the same quantity. Like-for-like, the exceedance is either 124.6 vs 116.7 at the bus (+6.8%) or 128.4 vs 120.3 stored-side — not the +3.8% the report's framing suggests.

**Evidence.** WS1 volt_physics.py `battery_trace` (lines 202–211) vs ws3_pack.py `terminal_power_from_ws1`; independent recomputation confirms the reference V2 draw is 116.68 kW at the terminals while the 8-seed terminal max is 124.55 kW.

**Why it matters (and what it does not break).** WS3's pack sizing treated R8's 120 kW as bus-side — conservative, no design impact — and ES-4's recommendation ("WS2/WS5 inherit 125/110 kW as bus-side envelope numbers") is the right number for those consumers. But ES-4 is a request to restate a baseline number; the ruling record should not inherit a comparison that mixes conventions by exactly the 0.97 factor whose ambiguity WS1's ledger was built to kill. There is no peak-discharge field in the interface block, so no machine-readable value is corrupted.

**What would resolve it.** One paragraph in §3.3/ES-4 stating both conventions explicitly: R8's 120 kW ⇒ 116.7 kW at the bus; ensemble envelope 124.6 kW at the bus (128.4 kW stored-side); recommended restatement 125 kW bus-side. No recomputation needed.

---

## WS3-r1-F3 — MINOR. The cold genset-average recompute (+20%, 12.11 kW) keeps WS1's warm 0.97 scalars at −10 °C

`cold_case_recompute` runs WS1's `four_numbers` (0.97/0.97 battery scalars) unmodified at the −10 °C design point; the pack's own cold map (T8: 0.90–0.96 one-way at these powers, self-heating 0.92 kW vs 0.34 kW warm) implies a slightly higher cold genset average. Direction: optimistic; magnitude sub-kW on 12.11 kW (a few percent), nowhere near reopening the +48%-vs-+20% conclusion. Resolve with the resistance model in the loop, or by stating the headline as "+20–25%". (Reference-seed-only is acceptable here — a cycle average, not an extremum, and like-for-like with WS1's own environment table.)

## WS3-r1-F4 — MINOR. Stale annotation in results.json: `preconditioning.genset_fuel_note` says "1.6-2.2 kWh electrical per cold start"

The computed fields beside it say 1.111 kWh (to +10 °C) / 1.389 kWh (to +15 °C), and the report correctly uses 1.11. A downstream consumer quoting the note gets a number ~1.6× the record. Fix the string.

## WS3-r1-F5 — MINOR. Housekeeping inconsistencies (bundled)

- Heat-ledger sink text says radiator "310 W/K at 2,000 m"; §4.1 and `sensitivity.envelope_corners` say 308 W/K (350 × 0.88). Same claim, two numbers.
- Ledger line 1 (1.4193 kW, 24-min average) and the coolant-sizing line (1.4096 kW, steady) both render as ~1.41/1.42 kW; the ledger should say explicitly that WS6 sizes to the steady/sizing line.
- T8 footnote says unreachable cells are "shown at the voltage-floor limit"; they are actually shown below it (e.g. 120 kW / −10 °C resolves at 1.434 V/cell against the 1.50 V floor). Wording only.

## WS3-r1-F6 — MINOR. Descent conclusions are GVW-only, and the blend model cannot show a resistor overload

`descent_sim` assigns `p_res = p_bus_in − p_bat` unbounded and hard-codes `E_friction = 0.0`; the "friction stays zero, resistor never sees more than 39.4 kW" conclusion is true only because the worst §4.6 row (45.565 kW wheel, GVW) lands under the 50 kW resistor rating. BASELINE makes +20% payload a design case; a +20%-payload 6% descent adds roughly 7–8 kW at the wheel (~46 kW at the bus with a full pack), shrinking the resistor margin to a few kW — still inside, but never examined, and the model would silently report friction = 0 even if the rating were exceeded. Resolve with an assertion (`p_res <= 50 kW else friction`) and one payload-swept descent row, or a stated bound handed to WS2 with the resistor interface.

---

## Verdict

One **blocking** finding (F1 — the bus-voltage window and the cold R8 availability gates in the machine-readable interface are jointly unsatisfiable; WS2 must not freeze the bus window on this block as delivered) and one **material** finding (F2 — stored-vs-terminal convention mixing inside the ES-4 comparison). Everything else re-derived cleanly: the numbers are reproducible to the byte, the chemistry-trade logic survives independent recomputation, the thermal case closes, and the escalations are well-founded (ES-1's 20 kWh arithmetic and ES-4's envelope exceedance both check out).

---

*Placement note (foreman, for the record): the adjudicator subagent's direct file write was refused by the harness ("Subagents should return findings as text"); the foreman placed this document at the adjudicator's mandated path verbatim and unmodified from the adjudicator's returned text, with HTML entity encoding (`&amp;`, `&lt;`) restored to the literal characters the adjudicator wrote.*
