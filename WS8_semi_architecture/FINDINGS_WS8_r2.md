# FINDINGS — WS8 (Vehicle One) — round 2

> **Provenance of this file.** Authored by the `ws-adjudicator` agent
> (fresh context, Opus, round 2) launched per CLAUDE.md rule 9. That
> agent's harness blocked it from writing `.md` files to disk, so it
> returned its findings as text and the WS8 worker session persisted
> them here **verbatim and unedited**. The worker neither authored,
> softened, nor acted on any finding below. Nothing else in this folder
> was changed after the adjudicator read it.

**Verdict: NOT CLEAN. One blocking, four material, seven minor.**

Nothing found moves a verdict; `all_unchanged = True` is correct on the r2 numbers. F2 is genuinely and fully closed. The heat-ledger rebuild is a real improvement but is not yet right for S3, and the blocking finding is in the same export r1's F1 was in, at about the same magnitude.

## 0. Independently re-derived, and agreeing

| quantity | report / interface | my re-derivation |
|---|---|---|
| **all 24 corner ensemble-min margins** | interface `worst_case_margin_pct.cases` | recomputed from per-seed `MJ_per_km`/`payload_kg` + 70/30 mix: **max abs error 0.000e+00** |
| all 24 corner medians | section 6.1 | identical |
| `F4_reverted`, `F6_reverted` rows | section 4.4 / CSV | reproduced exactly from `fuel_g_corrected_deficit_only` / `_r1_pricing` |
| S1 pack cold acceptance | 30.5 vs 240.0 kW, factor 7.9 | 30.4968 vs 240.024; factor = 0.50823/4.0 exactly |
| S1 regen envelope nominal vs cold @10 m/s | must differ (r1's tell) | 24,002.4 N vs **3,049.7 N** — tell is gone |
| retard-channel conservation (4 cands × 2 corners × 139 speeds × 2 pack states) | "the sum is the channel the integrator was given" | envelope 3rd channel − (resistor+eb) = **0.000e+00 N everywhere** |
| ratio ceiling / grade ratio | 3.7699 / 6.88 → 3,832 rpm | 3.76991 / 3,832.5 rpm; factor 1.825 |
| 6% grade demand, gravity, power | 24.0 kN, 21.3 kN, 533 kW @90 | 23,974 N, 21,330 N, 533.2 kW |
| 12% startability | 44.4 kN | 44,420 N |
| `derate_factor(2000 m, +45 C)`, rho, aero relief | 0.9312, 0.871, "~27%" | 0.96×0.97; p/(RT)=0.8707; 27.2% |
| S1 pack-saturated descent | 81.4 km/h, 313 kW resistor | by hand: 400.1 kW @22.61 m/s; (400−60)×0.97−17.08 = 312.7 kW |
| WHR load curve, 3 systems, 6 loads | section 5 | reproduced closed-form |
| S0 cross-check at 3 masses | 33.08/32.58/34.34 | tare 15,515 kg; GCWs check; matches r1's independent re-run |
| advance/kill headroom | 3.69/2.52/10.65/6.84 pp | 3.0 − each nominal min |

**Interface integrity (three-way), checked independently of `verify_ws8.py`.** The JSON block extracted from section 13 is **byte-identical** to `results_ws8.json['interface_ws8']` (102,193 bytes) and equal again after parsing. Agrees with all six data CSVs spot-checked. `verify_ws8.py` passes 151 checks (91 in r1).

**Determinism (rule 1) — tested, not accepted.**
- `--from-checkpoint` in a scratch copy: `results_ws8.json` **byte-identical**, all nine CSVs **byte-identical**.
- `make_report_ws8.py`: `REPORT_WS8.md` **and** `CHANGELOG_WS8_r2.md` regenerated **byte-identical**.
- `--only-nominal --jobs 3` **from scratch**, no checkpoint, separate folder/process/pool width: recursive float-by-float comparison of the whole nominal trial slice returns **zero differences**; `task1_cycles` and `task2_s0_calibration` identical.

The disclosed platform difference never surfaced; every figure matched to the last stored digit.

**SHA pinning.** All **20** pins recompute correctly against the files on disk, including the four inherited WS2/WS3/WS4 objects and `../BASELINE_v4.md`.

**F2 genuinely closed.** `pack_chg_limit_kw()` is the single source of the ceiling and is called from every envelope (S1 `:1243`, S2 `:1419`, S3 `:1810`, S4 `:2242`), every `series_dispatch` (`:1257`, `:1581`, `:2259`) and S3's SOC loop (`:1987`, `:2008`, `:2027`, `:2080`).

**F6 is a genuine part-load treatment, and the bounds are inert.** Across all **480** runs: every one uses a duty-averaged basis, **zero** hit the `FALLBACK: genset best point` / `island BSFC` paths, **zero** were clipped by `CORRECTION_ETA_BOUNDS = (0.10, 0.50)`. The clipping cannot distort any margin in this record.

**The S1-vs-S2 ordering claim is sound, including against the variant r1 showed reversed it.** r2's set omits r1's ordering-reversing case (correction removed *entirely*, not just the credit), so I computed it: **S1 +1.08% / S2 +1.33% — S2 still ahead**. Also "no corrections at all": S1 +1.74 / S2 +2.10. Ordering holds in all eight variants I constructed.

**Assignment coverage.** Tasks 0–5 executed; every ordered sensitivity plus R28's corner; all three S3-specific risks. Seven escalations, all citing a ruling, none self-resolved. Directive items 1, 4, 5, 6 fully discharged.

---

## BLOCKING

### B1 — The largest row in the rebuilt WS6 heat ledger is a state one crankshaft cannot be in: S3's engine is simultaneously credited with +220 kW of shaft power and −215 kW of compression braking

**What is wrong.** The r2 split books compression-brake heat to the exhaust row (`ws8_candidates.py:2083-2085` S3; `:1613` S2), which is right. But nothing couples that channel to the engine's own fuelling. S3's SOC loop (`:2006-2016`) permits through-the-road charging whenever the clutch is closed, the pack is below target and axle A has headroom. On a descent axle A's traction force is zero, so the `if f_a[i] > 0.72 * f_a_cap[i]: chg = 0.0` guard never fires and charging runs at the full `p_chg_max`. Meanwhile `_retard_channels` (`:1816-1819`) hands the integrator up to 224 kW of compression braking from the *same* engine through the *same* fixed ratio to the *same* axle. The two are never netted and neither knows about the other.

**Evidence — measured at the exact window the export names.** `heat_ledger_ws6_worst_case.csv` gives `S3,engine_exhaust_kW,396.868,simulated_worst_run,payload_plus20/LH-520/seed8102 @ 105 km/h`. Re-running that run and locating the governing 60 s window:

| at the governing window | value |
|---|---|
| exported `engine_exhaust_kW` | **396.87 kW** (reproduced exactly) |
| of which compression brake | **215.40 kW** |
| of which combustion | **181.47 kW** |
| engine shaft power at the same instants | **+220.05 kW** |
| engine fuel rate | 12.45 g/s = **532.9 kW fuel power** |
| `F_trac` (60 s mean) | **0.0 N** |
| `F_retard` / `F_regen` | 9,809 N / 8,195 N |
| samples with both `p_eb>1 kW` and `p_shaft>1 kW` | **600 of 600** |

Summing the nine ledger rows over that window: 630.5 kW rejected against 1,060.2 kW accounted input — a 429.7 kW residual. The `simulated_worst_run` member is exempt from the closure assertion (m5), so nothing caught it.

Whole-run extent, S3, LH-520:

| corner, seed | samples brake+fuel | S3 fuel on those samples | max simultaneous |
|---|---|---|---|
| nominal 8101 | 0.95% | 1.16% | eb 200.3 / shaft 207.4 kW |
| nominal 8102 | 1.36% | 1.79% | eb 220.2 / shaft 256.0 kW |
| payload_plus20 8102 (governing) | 1.44% | 1.83% | eb 220.2 / shaft 257.7 kW |
| grade_heavy 8102 | 2.24% | 2.56% | eb 219.3 / shaft 222.1 kW |
| cold_minus10C 8101 | 10.94% | 5.96% | eb 200.6 / shaft 43.8 kW |

The underlying control law is worse than the ledger row shows: **5.67% of S3's total fuel on nominal LH-520 seed 8101, and 8.52% at the cold corner, is burned on samples where the truck is braking and no traction is demanded** — at the cold corner the engine is fuelling on 93% of braking samples. The artifact's own `e_ttr_charge_bus_kWh` (38.67 kWh median nominal LH-520; 77.95 grade_heavy; on nominal REG-165 larger than the entire regen harvest) is the same loop from the energy side.

S2 has the same defect at small magnitude (7.75% of cold-corner samples, simultaneous shaft ≤ 25 kW — hotel load — and it governs no exported row). **S0 is clean** — its overrun fuel cut-off (`:666`) makes the two mutually exclusive. S1 and S4 are clean by construction.

**Why blocking.** (i) It is the largest component row in the export and drives S3's 651.4 kW total, the largest total in the ledger; a correct value is at most the larger of the two states alone (~215 kW eb-only or ~225 kW combustion-only), so the export is high by roughly 1.8× — r1's F1 was 2.4×. (ii) It is exactly the "one crankshaft, two simultaneous uses" error that r2's own F3 fix was ordered to remove from S2, surviving in S3 in the retard direction, made visible by the F1(b) split this round introduced. (iii) It touches fuel, not only heat, and the double-booked compression brake is part of the retarding capability that sets S3's descent speed and trip time.

**Resolution.** (i) Make the two mutually exclusive on one rule, as S0 already is, and re-run S3 (and S2). (ii) Gate through-the-road charging on the vehicle not braking, not merely on `f_a` being small. (iii) Extend `heat_closure_check` to `simulated_worst_run`, or at minimum assert per run that no sample carries both compression-brake power and positive engine shaft power.

---

## MATERIAL

### M1 — The changelog's stated DIRECTION for F3 and F6 on S2 is contradicted by the report's own one-factor table, and both are hand-written strings the verifier cannot reach

- **F3 — "AGAINST S2"**. Section 4.4: `r2_as_reported` S2 median **+1.79994**; `F3_reverted_engine_dual_use` (r1's treatment, re-simulated) **+1.75375**. The F3 correction moved S2 **UP 0.046 pp**. It was **FOR S2**.
- **F6 — "slightly FOR S2"**. `F6_reverted_peak_point_pricing` **+1.81335** against **+1.79994**. F6 moved S2 **DOWN 0.013 pp**. It was **AGAINST S2**.

The mechanism for F3 is plain in the code: r1's path returned `g_tot + g_free` (`ws8_candidates.py:1573-1578`) — locked mechanical fuel *plus* a whole free-speed genset's fuel from the same crankshaft — so engine friction was charged twice on locked-and-generating samples. r2's single-crankshaft treatment charges it once. Correcting a double-charge makes the candidate cheaper. The physics of the r2 treatment is right; only the label is wrong.

This matters because F3 was r1's finding that S2 — the leading candidate — was being *flattered*. The record now tells the lead the fix cut against S2 when it helped it, and `CHANGELOG_WS8_r2.md` is internally inconsistent: §1 correctly reports S2 as **BETTER** on the nominal median while §2 labels both of its own corrections against-or-neutral. The strings are literals at `make_report_ws8.py:1500` and `:1516`, so `verify_ws8.py` structurally cannot catch them — r1's F9 failure mode recurring in the round that closed F9.

**Resolution.** Derive the direction column from `one_factor.rows`; state F5/F6 directions for S3 and S4 the same way or mark them not separately measured; add the strings to the verify set as F8 did for class titles.

### M2 — Section 0's per-km headline uses a different statistic from every margin in the report, unlabelled, and the S3 figure contradicts the sentence three lines above it

`make_report_ws8.py:180-190` computes the per-km bullet as a **ratio of medians**, while every margin is the **median of per-seed paired margins**:

| | as printed (ratio of medians) | paired per-seed median | paired min |
|---|---|---|---|
| S1 | +7.184% ("7.2%") | +7.357% | +6.029% |
| S2 | +9.733% | +9.734% | +8.516% |
| **S3** | **−0.301% ("−0.3%")** | **+0.945%** | −1.306% |
| S4 | +5.928% | +5.946% | +3.357% |

For S3 the two statistics **differ in sign**. The paragraph above the bullets asserts, as a hard-coded literal at `make_report_ws8.py:143-144`, "**Every candidate here is more efficient per kilometre than the conventional truck**" — contradicted by the next generated line and by the section 4 table (S3 38.89 vs S0 38.78 L/100 km). On the paired statistic the sentence is true at the median but false on 2 of 8 seeds. BASELINE_v4 R33/D13 carries "Every electrified candidate won 6–10% per km" into WS9 doctrine; S3 won neither.

**Resolution.** Compute the bullet on the paired statistic or label its basis; generate the "every candidate" sentence from data. Flag D13 to the lead.

### M3 — The R28 corner derates the engine and nothing else, and the round draws a conclusion from that corner

At `hot_alt_2000m_45C` the derate is applied correctly to every engine's full-load curve and to the R18 continuous rating (`:380`, `:1183`, `:1335`, `:2178`; mass correctly sized on the un-derated rating). It applies **no thermal derate to anything electric** — machine, inverter, pack charge *and* discharge, air-cooled resistor all run at 20 C values. `Pack8.cold_chg_factor_at()` clamps to 1.0 above 15 C and there is no hot-side model in `ws8_electric.py`. The corner's benefit (27% off the aero bill) goes to everyone; its penalty is charged only to combustion.

The round then concludes "**The R28 corner did not become the worst one, and that is itself a result**" with a table showing S1/S2/S4 gaining there. That conclusion is not supported by a corner that derates only half the fleet's prime movers. The binding corner is not in doubt, but WS9 will inherit the statement. (In fairness, the cab-cooling asymmetry at this corner is handled well and symmetrically — 7.0 kW crank / 6.0 kW bus, both charged — as is the cold corner's mirror image.)

**Resolution.** Either state in the corner label and §15.1 that only the engine is derated, or add a declared hot-side electric derate and re-run; move the conclusion with it.

### M4 — ESC-WS8-1 states only the half of the cell-substitution direction that hurts S4, and R27/ESC-1(c) has already released S4′ into WS9 on that framing

The escalation correctly argues the power-optimised NMC-P-40 penalises S4 on mass. It does not say the same cell hands S4 **600.4 kW continuous charge / 1,200.7 kW continuous discharge** on a 150 kWh pack (4.0 and 8.0 kW/kWh). That charge ceiling is co-binding with the machine at cruise (S4's regen force at 26.4 m/s is 22,741 N = 600 kW at the wheel), so at nominal S4's descent regen is effectively unconstrained by its pack; an energy cell at 1–1.5 C would give 150–225 kW and bind it hard. Substituting the cell moves S4 **both ways**, and only the favourable half is on the record — the half WS9's S4′ will be sized on.

**Resolution.** Add the power-side direction to the finding and materiality line. No number needs to move.

---

## MINOR

**m1 — "6.88 solved in closed form" is a search over two grids.** The ratio *ceiling* (3.7699) genuinely is closed form and that half of F12 is discharged. But 6.88 comes from `ratio_needed_to_hold_6pct`, whose own rule string says "lowest ratio on a **0.01 grid**", and `S3.grade_hold()` (`:1855`) scans speeds on a 0.1 m/s grid. §6.2 nonetheless says "No swept grid is doing any work in that conclusion." Robust at that resolution; the prose claim is the class r1's F12 was raised about.

**m2 — Section 7 says "Cases above 1 kWh" and lists 20 of the 30 it has.** `make_report_ws8.py:904` truncates with `[:20]`. Ten cases between 9.99 and 17.70 kWh (all of S1's, most of S2's) are silently absent, so the table reads as though S1 and S2 have almost no unserved energy outside the cold corner.

**m3 — The `simulated_worst_run` row of `heat_ledger_ws6.csv` does not close and carries no per-component labels.** The construction is right (per-component envelope; total separately maxed as peak-of-sum) and the JSON and `heat_ledger_ws6_worst_case.csv` both carry `_run` labels — but the per-case CSV presents it as one row beside four single-operating-point cases, unlabelled: for S0 the nine components sum to 858.8 kW against a stated total of 569.3 kW.

**m4 — The instantaneous peaks are computed and never exported.** `HEAT_SUSTAINED_WINDOW_S`'s docstring says the instantaneous maximum is "reported alongside so nothing is hidden"; neither `heat_ledger` nor `interface_ws8` contains any key matching `instantaneous`. In this run it conceals nothing (S1 314.57 vs 314.28; largest gap is S0's foundation brakes 834.2 vs 312.8, which is a snub and rightly averaged).

**m5 — `all_cases_close_and_within_rating = True` is weaker than §12's sentence reads.** (a) `heat_closure_check` only examines cases carrying `_closure_residual_kW` — the four analytic ones; `simulated_worst_run`, which governs 34 of the 50 exported component worst cases, is exempt. The JSON convention discloses this; §12's bolded "**Every case closes and every component stays inside the rating**" does not. B1 is what that exemption let through. (b) The resistor rating check cannot fail: `_retard_channels` caps resistor force at `resistor_kw*1e3/v` at the **wheel**, so bus-side resistor heat is ≤ ~0.92 × nameplate by construction (measured maxima 314.57 of 340; 183.45 of 200).

**m6 — The pack charge limit is a bus-side kW applied as a wheel-side force cap.** `f_regen = min(f_gen, chg*1e3/v)*blend` (`:1243`, `:1419`, `:1810`, `:2242`). Confirmed from the ledger: S1's `descent_6pct_pack_accepting` books `pack_kW = 6.601` of loss, which at `1−eta_chg = 0.03` is **220.0 kW into the pack against the 240.02 kW ceiling** the report quotes. `series_dispatch` applies the same number bus-side — one figure at two boundaries. Conservative, flatters no one, but Recommendation 5 and §6.1 quote "30.5 kW against 240.0 kW warm" as though it were the intake. r1 recorded the identical slippage on the resistor.

**m7 — Section 4.2 still describes S2's disconnect as deleting a tax neither candidate pays.** After the F5 fix, R22(d) costs **0.0026–0.0048 kWh** for all four — S1 (no disconnect, policy says it pays) and S2 (42 kg `traction_disconnect`) are within a factor of 1.6 on a number that rounds to zero. The coast-permitting bracket that makes this legible (S1 38.06, S2 13.83, S3 18.16, S4 38.12 kWh) is exported and well explained, but only inside the JSON in §13. §4.2 still reads "the G1(b) tax deleted by hardware".

---

## Things I looked for and did not find

- **Single-draw extrema (rule 4).** Every interface extremum is an 8-seed envelope; I recomputed all 24 minima and 24 medians. F7's restatement is done properly, with three enumerated masses and the reference payload stated, and ESC-WS8-7 softened to match — the "one percent" claim is gone.
- **Peak-point scalars (rule 5).** None survive in a live path (0/480 fallbacks, 0/480 clips). WHR is a genuine load-dependent model and its gate is correctly read against the candidate **without** WHR (`run_ws8.py:1142-1160`) — the right reading of Task 4, not the easier "beat S0 by 2.5%".
- **The retard split's conservation.** Exact to 0.000e+00 N everywhere, both pack states. The split is a real improvement: S2's r1 figure of 503.4 kW — above the 340 kW resistor it was charged for — is now 267.9 kW resistor + ~190 kW exhaust; S3's 210.71 kW against a 200 kW resistor is now 183.0 kW. B1 concerns what the *exhaust* side is added to, not the split.
- **A governing case outside the enumerated set (r1 F1a).** Closed. The pack-saturated descent case correctly re-solves the achievable speed per architecture (81.4 km/h S1/S4, 98.8 S3, 100 S2 — a real architectural difference, not a copied number), and the simulated member brings the trial's own peaks in. The exported resistor case now governs at the cold corner for S1, S3, S4 — the physically right answer once F2 is applied. r1's F1(c) gear-jump artefact is addressed by an exported `speed_step_sensitivity`; S0's step is 8.2 kW on a 321.7 kW case, `on_a_step: false`.
- **Verdict stability.** Re-read the criteria independently: KILL ×4, WHR DROPPED ×3, `all_unchanged = True` correct. The round did not touch a verdict.
- **Escalations (rule 8).** All seven cite a ruling; none self-resolved. ESC-WS8-6 records R27/ESC-6 as closing it *for WS9*, which is citing the lead, not self-resolving. M4 is about completeness of a direction statement, not disposition.
- **S3's kill.** Re-derived and confirmed again: ratio ceiling and grade ratio miss by 1.83×; e-axle-alone climb 132.75 kWh against 21.60 kWh of swing; single-axle launch mu 0.587 vs a 6×4's 0.293. B1 makes S3's fuel *more* favourable than it should be, not less.
- **Mass closure.** tare + payload = 36,300.00 kg for all five, summed independently; every interface payload equals the spec value bit for bit.

## Suggested disposition

- **B1** should close before WS6 consumes the ledger: same export, same class, ~same magnitude as the finding R26 opened this round to fix, and unlike r1's F1 it also touches fuel. The fix is small and cannot move a verdict.
- **M1** and **M2** are cheap and are both the class this round was meant to eliminate — a hand-written string inside a generated artifact that the verifier cannot reach. M1 additionally misdirects the lead about r1's finding against the leading candidate.
- **M3** and **M4** are record and direction-of-error statements WS9 inherits under R28, R31 and R27/ESC-1(c). They change no number here.
- **m1–m7** can travel as a checker-pinned errata set; **m5** and **m6** are the two worth pinning, because both are assertions that read stronger than what they test.

*Findings only. Nothing here rules on an escalation, nothing reopens a verdict, and nothing in the workstream folder was modified.*
