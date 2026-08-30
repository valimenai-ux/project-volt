# FINDINGS — WS2 REVIEW, ROUND 1

**Verdict: no blocking findings. Two material findings (WS2-F1, WS2-F2), five minor. The central interface — bus window 300–435 V, nominal 370 V, full-performance floor 320 V, 750 V device class — re-derives cleanly and is safe for WS3/WS4 to consume.**

## What was independently verified (clean)

- **Determinism**: `run_ws2.py` regenerates `results.json` and all 12 `data/*.csv` byte-identical; only timing strings in `run_output.txt` differ. `check_report.py` passes (77 string checks + interface-block deep-equality + ratio table).
- **Three-way interface agreement**: report §9 JSON block deep-equals `results.json interface`; prose headline values (window, floor, backstop 445 V, 154/124 kW, 530 Nm, 43 kg resistor, 217.5 kg total, 12 L/min / 65 °C) match both.
- **Peak power vs bus voltage** (WS3's trade input): re-derived with an independent grid-search dq solver: 123.8 / 132.3 / 153.7 / 181.3 kW at 300/320/370/435 V — matches to 0.1%. Also re-derived at 180 °C winding: 123.2 kW at 300 V, so the ≥120 kW-everywhere claim survives the hot 1-min case (unstated in the report, but it holds).
- **Efficiency maps** (WS4/WS5's input): four spot points of `effmap_motor_inverter_370V.csv` re-derived independently (motoring, generating, crawl corner) — eta and current match to 4 decimals.
- **Torque chain and machine physics**: 515 Nm corner, 7,169 rpm, UCG onsets 73.9/91.2/107.2 km/h, EMF 407 V, characteristic current 446 A, S2 currents 355–358 A (370 V) / 423 A (300 V) — all reproduce.
- **Resistor**: 50.0 / 105.1 kW, ribbon 62.5 m / 12.34 kg, assembly 42.56 kg, blower 1.01 kW at 2,282 m³/h, ribbon 253/400 °C, chopper 65 W — all by hand.
- **Traction envelope** (E23): re-derived by hand — 43.6/27.4 kN at GVW μ0.8, 983.5 and 175.1 Nm motor-side caps, μ required 0.294/0.654 matching WS1 §4.16; WS2's 20%-grade sign disagreement with WS1 is real, disclosed, and correctly deferred to WS1's conservative envelope.
- **Thermal**: crawl oil-spray 146 °C re-derived by hand (~6.4 kW copper at 644 A, ΔT ≈ 70 K over 90 W/K); crawl chain loss 8.75 kW confirmed; stall ~98 s consistent; grade-hold chain heat 4.66 kW confirmed at 197.7 Nm.
- **Heat ledger**: every row re-computed or traced to source (WS1 §4.6's 22.0 kW / 8.82 kWh and 45.6 kW confirmed); V2 cycle mean correctly includes lockup-spin heat.
- **Compliance**: no RNG introduced; consumed extrema are WS1's 8-seed envelopes; reference-trace means justified by WS1 §4.8; all six tasks covered including the 8:1–12:1 sweep and +45 °C cases; all six escalations cite rulings; WS2-E3's erratum claim checks out (WS1's "300–700 rpm" is inconsistent with its own 10.6/23.6 km/h through 10:1 → 760/1,692 rpm).

## WS2-F1 — MATERIAL. The "favourable part-load correction" (§7, WS2-E4) rests on a chain-definition mismatch: WS1's 0.97 PE stage was silently deleted, and its ownership is now ambiguous

**What is wrong.** §7 compares the map's energy-weighted shaft↔bus efficiency (0.921/0.929 motoring) against "WS1 scalar for the same chain 0.892" and concludes the correction is favourable. But WS1's 0.8924 = PE 0.97 × inverter+motor 0.92 (`run_ws2.py` line 532: "eta_pe * eta_inv_mot"). WS2 models inverter+motor only — no PE stage. Like-for-like against WS1's inverter+motor scalar 0.92, the maps are +0.1 pt motoring and **−0.9 pt generating** (0.911): essentially neutral, not "+3 points favourable". The gain is the deleted PE stage, not part-load physics.

**Evidence.**
- WS1 §6.3 and §2: bus-to-wheel chain 0.866 = PE 0.97 × inv+motor 0.92 × reduction 0.97; regen "delivered to the DC bus (× 0.866 chain)". WS1's operative shaft↔bus chain is 0.8924 including PE.
- Independent re-integration of WS1's traces: captured-at-wheel regen 3.318 kWh (SUB) / 4.234 kWh (REG). WS2's to-bus 2.930/3.745 imply chain 0.883/0.884 = 0.97 × 0.911 (no PE); WS1's convention gives 2.873/3.667 — WS1's published 2.87/3.67. The §7/§11.6 "1–2% cross-check agreement" is actually a systematic +2.1% convention change presented as agreement.
- WS1's grade-hold ledger seed: 20.2 kW = generator 6.6 + **power electronics 3.0** + inv+motor 7.9 + reduction 2.7. WS2's §8 note restates only inv+motor and reduction and calls the rest "generator, rectifier ... not WS2's to restate" — implicitly reassigning WS1's 3.0 kW PE row to WS4 without flagging the move, though WS1's own arithmetic put that stage on the traction side of the bus.
- WS2-E4 asks the lead to rule WS1's −7…−8.5% traction derate "superseded by the maps"; the maps supersede only the inv+motor member — WS1's derate also covered PE and reduction, and WS2 keeps reduction as a flat 0.97 scalar.

**Why it matters.** Gate G1's ≥5% kill criterion and WS3's regen bookkeeping consume these chains; a silent 2–3% shift is over half the G1 margin if applied asymmetrically, and WS2-E4 as framed invites the lead to drop a WS1 correction on a mislabeled comparison.

**Resolution.** Restate §7 against the like-for-like 0.92 scalar and reframe WS2-E4 (defensible claim: no *additional* part-load derate for machine+inverter; generating ~1 pt worse than the scalar). Escalate a one-line ownership ruling for WS1's 0.97 PE stage — WS4 rectifier (then WS1's 0.866 chain and the 90.5 kW grade-hold point need re-derivation on the record) or a real traction-side allocation (then WS2 must carry or explicitly justify deleting it). State whether the reduction's 0.97 keeps WS1's part-load derate.

## WS2-F2 — MATERIAL. The coolant interface exports the wrong member of the heat set: `heat_at_S2_kW = 4.66` is neither the S2 point nor the loop-sizing case

`interface.coolant.heat_at_S2_kW` is computed at the 90.5 kW / 197.7 Nm grade-hold point, not the S2 rating point (95 kW / 207.4 Nm → **4.90 kW**, re-derived independently). Worse, the workstream's own LT-loop worst case is the 20% crawl at **8.75 kW** (§8 prose: "loop must absorb 8.75 kW at the crawl worst case"), present in the ledger CSV but absent from the machine-readable coolant block. A WS6 consumer sizing from the interface block alone reads 4.66 kW — 47% below the workstream's own stated loop duty. The assignment requires the block to carry heat-to-ledger by case. **Resolution:** add the crawl worst case (and the true S2-point value) to `interface.coolant`, or rename the field to what it is and add `heat_worst_case_kW = 8.75`.

## WS2-F3 — minor. Ratio-sweep narrative contradicted by its own table
§2.2: "The only ratios that would beat 10:1 on paper (11:1, 12:1) breach R3's 7,200 rpm line." Per `ratio_sweep.csv`, 9:1 also beats 10:1 on total cycle loss (4.021 vs 4.028 kWh) and is inside the rpm line. Noise-level (0.17%) and the decision stands on the stated >5% threshold and mass — but the sentence is false as written.

## WS2-F4 — minor. F-1 checked at CdA 4.2 despite the baseline's "motor sizing carries CdA 5.4" (E13)
`machine.F1_70kmh_shaft_kW = 30.78` uses CdA 4.2. At CdA 5.4 it is ≈36.2 kW — still well inside S1, verdict unchanged, but the recorded number inherits the optimistic input without a flag.

## WS2-F5 — minor. Crawl "sustainable" judged against the 180 °C hard limit while S1/hold cases use the 165 °C continuous limit
At nominal G_ws = 90 W/K the crawl (146.1 °C) passes both, but WS2-E1's "sustainable down to 75 W/K (164.9 °C)" sits at the continuous-life limit while passing only the hard-limit test. WS2-E1 should name which limit defines "sustainable" for a minutes-long crawl.

## WS2-F6 — minor. Altitude effects on the air-cooled resistor unexamined
R7 envelope is 0–2,000 m; the blower design uses sea-level inlet density. Re-derived at 2,000 m the ribbon reaches ~480–500 °C at the 105 kW design point — still under 650 °C, and 50 kW keeps large margin, so the conclusion stands, but the report claims the envelope without showing this case.

## WS2-F7 — minor. Two mislabeled internal quantities
(a) `headline.spin_drag_85 = "1.49 kWh"` holds the per-cycle spin energy, not the 85 km/h drag (1,109 W). (b) `bus.trade.*.I_motor_peak_dc_A = 533 A` = 160 kW / 300 V, a combination the machine cannot produce (peak DC at the floor ≈131 kW ≈ 437 A); conservative for cables, but §4 quotes it as an operating point ("533 A for ≤60 s") rather than a bounding envelope.

---

No blocking findings. WS2-F1 and WS2-F2 should be resolved (or ruled on by the lead, for F1's ownership question) before WS4's G1 study and WS6's loop sizing consume the affected items; nothing here requires reopening the bus-window proposal itself.

**Files referenced:** `/Users/valimenai/Documents/Project Volt/WS2_traction_motor/REPORT_WS2.md` (§7, §8, §9, §2.2), `results.json` (`interface.coolant`, `cycles`, `ratio_sweep`, `bus.trade`, `headline`), `run_ws2.py` (line 532 scalar comment; `thermal_cases()` gradehold vs S2 point), `ws2_cycles.py` (chain conventions), and WS1's `REPORT_WS1.md` §6.3/§4.14/E19 (the 0.866 chain and 20.2 kW breakdown).

---

*Placement note (foreman, for the record): the adjudicator subagent's direct file write was refused by the harness; the foreman placed this document at the adjudicator's mandated path verbatim and unmodified from the adjudicator's returned text, with HTML entity encoding (`&gt;`) restored to the literal character the adjudicator wrote. The adjudicator reported it re-ran the pipeline after backing up as-submitted artifacts and regeneration was byte-identical; the workstream folder is unchanged.*
