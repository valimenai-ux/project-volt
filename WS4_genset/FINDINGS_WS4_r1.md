# FINDINGS — WS4 (genset + Gate G1) — review round 1

Adjudicator: fresh-context adversarial review against BASELINE_v1.md.
Artifacts judged: ASSIGNMENT.md, REPORT_WS4.md, results_ws4.json,
run_ws4.py / ws4_models.py / ws4_sim.py / make_report_ws4.py /
verify_ws4.py, data/*.csv, figs/*.png, run_output.txt, on disk as of
2026-08-29.

**Verdict: no blocking findings. Two material findings (F1, F2) and
five minor findings. The G1 headline, the R6 corner numbers, the maps,
the heat ledger, and the V1 start-stop numbers all reproduce
independently; the interface block is three-way verbatim-consistent.
The material findings concern one unsupported number inside an
escalation and the machine-readable gate record omitting a
condition-dependence the report itself calls out.**

---

## Verification record (what was re-derived, independently)

- **Determinism**: full pipeline re-run (`.venv/bin/python run_ws4.py`,
  then `make_report_ws4.py`, then `verify_ws4.py`, exit 0).
  `results_ws4.json`, `REPORT_WS4.md`, all five `data/*.csv`, and all
  three `figs/*.png` regenerate **byte-identical**. `run_output.txt`
  differs only in its final wall-clock line ("elapsed 27s" vs "28s") —
  cosmetic, see F7.
- **GATE G1** (the number blocking for WS6): per-seed margins recomputed
  from the raw corrected fuels for all five configurations
  ((b−a)/b·100); ensemble min/median/max recomputed; nominal
  6.261 / 6.445 / 6.784 % confirmed exactly, alt-corner
  3.751 / 3.916 / 4.151 % confirmed, CdA 5.4 8.22 / 8.36 %, aux-4kW
  6.46 / 6.63 %, reference-curve 6.58 / 6.76 % confirmed. The
  disclosed mode-(b) energy-accounting fix (§9 D2) was audited at the
  code level: unserved bus energy is tracked at battery-empty, asserted
  <0.3 kWh at nominal, and fuel-corrected at the marginal buffered-
  series rate bsfc_pin/(eta_chg·eta_dis·eta_gen); the correction was
  reconstructed by hand for the nominal reference seed (both modes) and
  the CdA-5.4 seed 23 mode (b) (drift −82.29 g + unserved +139.42 g on
  24,454.85 g raw = 24,512.00 g) — all match to <1e-6 g. The correction
  is applied symmetrically across modes; its rate choice differs from a
  direct emergency-serve rate by ≲0.04 % of mode-(b) fuel at CdA 5.4
  and ≲0.003 % at nominal — immaterial to the verdict. The emergency
  load-follow band is present identically in modes (a) and (b). The
  8-seed ensembles use exactly WS1's convention (ref seed 23 + 3–9 for
  VOLT-REG; 11 + 3–9 for VOLT-SUB; confirmed against WS1 run_ws1.py).
- **R6 corner**: derate 0.96 × 0.97 = 0.9312 re-derived from the
  declared model; 132.0 × 0.9312 = 122.9184 kW, margin +0.8184 kW;
  corner rows for all seven candidates recomputed exactly. A "125 kW
  continuous" label delivering 116.4 kW at the corner (ESC-1's
  arithmetic) confirmed.
- **BSFC maps**: the Willans construction was re-implemented from the
  declared formula (own code, not WS4's); the V2 pinned point
  (1,288 rpm / 628.0 Nm / 84.700 kW / 203.617 g/kWh), the V1 pinned
  point (228.720 g/kWh), and the reference map minimum reproduce to
  <1e-6 g/kWh; an independent 400×400 grid search finds the same map
  minimum. Published `data/bsfc_map_V2_candidate.csv` rows match the
  independent formula to 0.05 g/kWh once the file's 0.1-Nm torque
  rounding is accounted for (see F6). The 10.7 kW motoring-drag anchor
  at 1,706 rpm reproduces exactly from FMEP × displacement. All map
  headers carry the "WS4-CONSTRUCTED … NOT measured" label.
- **Generators**: eta at both pinned points re-derived from the declared
  loss model (0.95176 / 0.93944, <1e-9); spin losses 1.2 / 0.7 kW at
  1,800 rpm confirmed.
- **Heat ledger**: R6-corner entry re-derived end to end (BSFC 219.571
  incl. the 2 % altitude adder → 320.873 kW fuel → 95.018 kW radiator
  package / 96.998 kW exhaust, 48 %/49 % of 197.95 kW rejected); grade-
  hold entry (77.206 / 78.815 kW, electrical chain 17.900 = generator
  4.551 + 99.34 kW bus × chain loss) confirmed; V1 duty-averaged
  radiator 10.058 kW and the G1(a) cycle averages confirmed.
- **V1 start-stop**: 66.11 starts/8 h ref seed, ensemble 57.41–74.35,
  fuel saving vs continuous 6.198 %, cold case +41.7 % (report's
  "+42 %"), duty 0.413 → 0.595 — all recomputed from the underlying
  counts and durations.
- **Capability numbers**: V1 charge-sustaining top speed (76.5 km/h)
  and both series grade-hold speeds (71.3 / 63.6 km/h) re-solved with
  an independent road-load implementation using WS1's parameters —
  agree to <0.3 km/h. WS1's 107.808 kW grade-floor regression
  reproduces to <1e-6 with independent math.
- **Interface, three-way**: the report §11 JSON block, extracted and
  compared, is **byte-identical** to `results_ws4.json →
  interface_ws4`; the gate figures inside it equal the nominal
  ensemble; the report prose values covered by `verify_ws4.py` (49
  renderings) all check, plus independent spot-checks of §4.2 (starts
  46–62, banking 1.5–3.3 kWh, emergency 484–805 s, unserved ≤0.12 kWh,
  over-rating 42–72 s), §3, §6, §7 and §10 against the JSON.
- **Compliance**: part-load models everywhere (WS1's ratified
  `part_load_factor` carried unchanged — verified against WS1
  run_ws1.py; generator loss maps; load-dependent direct-path model —
  no peak-point scalars found); heat reported by component and case;
  escalations all cite rulings; assignment tasks 1–6 present (with the
  coverage caveat in F4).

---

## F1 — MATERIAL — ESC-5 cites an unserved-energy magnitude the data does not support

**What is wrong.** ESC-5 states pure series at CdA 5.4 "still sheds up
to 0.12 kWh on hard seeds (up to **1.9 kWh at CdA 5.4**)". The data
file's worst unserved energy at CdA 5.4 is **0.768 kWh** (seed 5,
`gate_g1/cda_5.4/per_seed/5/b/unserved_kWh`; full 8-seed range
0.463–0.768 kWh). No quantity near 1.9 kWh exists anywhere in
`results_ws4.json`. The number most plausibly survives from the
pre-D2-fix state of the code (§9 D2: "flattering pure series by up to
2 kWh/cycle at CdA 5.4"). `verify_ws4.py` does not cover ESC-5's
figures, which is how it slipped through.

**Why it matters.** ESC-5 is a decision input to the lead on R8's
buffer floor under a G1 kill scenario; it overstates the current
model's shortfall by ~2.5×.

**Resolution.** Correct ESC-5 to the on-disk value (0.77 kWh, or
0.46–0.77 kWh across seeds), or produce the run that yields 1.9 kWh
and publish it; add the escalation's numbers to `verify_ws4.py`'s
check list.

## F2 — MATERIAL — the machine-readable gate record exports an unconditional pass the prose itself qualifies

**What is wrong.** `interface_ws4 → gate_g1` exports
`{margin min/median/max (nominal), kill_criterion_pct: 5.0, passes:
true}` with no condition field. The report's own headline and ESC-2
say the margin falls to 3.75–4.15 % — below the criterion — at the
2,000 m / +45 °C corner, which is *inside* the R7 operating envelope
over which the baseline declares "all downstream sizing" valid. The
report describes the set {nominal: pass, R7 corner: fail} correctly in
prose; the interface exports only one member of it, unlabeled. G1 is
blocking for WS6, and the report itself designates `interface_ws4` as
"the block downstream parses" — a consumer of the interface alone sees
a clean pass and never learns of the corner failure or of ESC-2's
pending ratification question.

**Why it matters.** This is precisely the WS1-era failure class
(machine-readable interface disagreeing in substance with the prose)
on the program's highest-stakes bit this round.

**Resolution.** Add condition metadata to `gate_g1` in the interface —
e.g. `"condition": "nominal (sea level, CdA 4.2, 2 kW aux)"`, plus the
corner ensemble (`margin_pct_ensemble_min_at_2000m_45C: 3.75`,
`passes_at_2000m_45C: false`) or an explicit `see: ESC-2` marker — so
the interface carries the same information set as the prose. No
recomputation needed; the numbers are already in
`gate_g1/alt2000m_45C/ensemble`.

## F3 — MINOR — findings-register F-4 quotes a motor over-rating range with no stated basis, inconsistent with §4.2

**What is wrong.** §4.2 reports mode (b) exceeding the 150 kW motor
rating "for 42–72 s per cycle" (correct: the nominal 8-seed range is
42.1–71.5 s). F-4 states "61–136 s per VOLT-REG cycle". 61.0 s is the
nominal *reference seed*; 136.3 s is the CdA-5.4 *reference seed* —
the range spans two configurations without saying so and matches
neither ensemble (nominal 42.1–71.5 s; CdA 5.4 110.4–137.5 s). An
R9-convention lapse inside the findings register.

**Resolution.** Restate F-4 as either the nominal ensemble (42–72 s)
or explicitly "42–72 s nominal, 110–138 s at CdA 5.4" (8-seed
envelopes).

## F4 — MINOR — assignment task 6's "hot day" sensitivity exists only merged into the combined altitude corner

**What is wrong.** Task 6 enumerates "altitude derate at 2,000 m, hot
day" as sensitivities. For G1, only the combined 2,000 m + 45 °C case
was run. There is no standalone hot-day (sea-level, +45 °C) G1 case on
disk, so the record cannot say whether heat alone — the far more
common dispatch condition — keeps the margin above 5 %. (The R6-corner
*delivery* math does separate the two factors, 0.96 × 0.97, and the
combined case bounds the envelope worst corner; the gap is in the G1
sensitivity set only.)

**Resolution.** One additional `g1_config` run (derate 0.97, sea-level
density at 45 °C) closes it; report min/median alongside §6's table.

## F5 — MINOR — the R6 corner margin (+0.82 kW, 0.67 %) rests on two stacked WS4-declared, unverified values

**What is wrong.** Corner compliance is achieved only by (i) the
132 kW "genset recalibration" continuous rating — a WS4-proposed
respec; the stock datasheet-class 130 kW fails the corner by 1.0 kW —
and (ii) the class-typical (not datasheet) derate model, 0.9312. A
derate slope 1 % different, or a confirmed continuous rating 1 kW
lower, flips `meets_R6_corner`. The report is honest about both (TBC
flags, ESC-1), so this is recorded, not newly discovered: the +0.82 kW
margin is inside the uncertainty of its own inputs.

**Resolution.** Nothing to recompute. The lead should treat R6
compliance as provisional until the procured engine's datasheet
derate and the 132 kW continuous flat-rating are confirmed; carry that
condition into any WS6 release.

## F6 — MINOR — small prose/data drifts not covered by verify_ws4.py, and a rounding artifact in the published maps

**What is wrong.**
1. §5 table, "3.0 kWh usable, 1.6 kWh share" row: fuel is printed
   **3.41 L/h**; the data says 3.365 → **3.37 L/h**
   (`v1_start_stop/usable_3.0_hyst_1.6/fuel_l_per_h`). The starts
   figure (33) is verified, the fuel figure is not, and it is wrong as
   printed (it repeats the 0.8/1.1 kWh rows' value).
2. §3 table: V1 "at rated continuous" printed "~247 g/kWh"; data says
   249.29 (`bsfc_maps/V3307-V1C-W/bsfc_at_rated_continuous`).
3. `data/bsfc_map_*.csv` print torque rounded to 0.1 Nm while the BSFC
   column corresponds to the unrounded grid torque: at near-zero
   torque rows the printed pair is inconsistent by up to ~2 g/kWh
   (0.1 % relative; ≤0.05 g/kWh against the exact grid). Harmless at
   any operating torque, but a downstream interpolator re-deriving
   fuel from the printed pairs inherits the noise.

**Resolution.** Fix the two table values and add them to
`verify_ws4.py`; either print unrounded torque in the map CSVs or note
the rounding in the header.

## F7 — MINOR — two accounting/reproducibility nits

**What is wrong.**
1. `over_rating_s` (R3 rating exposure) is accumulated only on
   *unlocked* samples; motor assist during locked samples
   (`deficit_wheel` torque-fill) is never checked against the 150 kW
   rating. On VOLT-REG the locked-assist deficit cannot practically
   reach the rating (engine near full load leaves ≲100 kW wheel
   deficit), so mode (a)'s reported 0.0 s is almost certainly right —
   but the ledger cannot show it.
2. `run_output.txt` embeds a wall-clock "elapsed NNs" line, so the
   committed artifact tree is not byte-stable under re-run (everything
   else, including PNGs, is byte-identical).

**Resolution.** Extend the over-rating check to locked-sample deficit
fill; drop or fix the elapsed line.

---

## Notes for the lead (not findings)

- ESC-3 recommends WS3 raise V1 usable to ~3.0 kWh. WS3's parallel
  report already proposes 11.08 kWh usable with a 3.0 kWh V1
  hysteresis allocation; the two workstreams converge, and ESC-3 is
  likely already satisfied by WS3's proposal — an integration check at
  ratification, not a WS4 defect (WS4 correctly used R8's floors as
  assigned).
- §4.3's decomposition (chain advantage mostly cancelled by the ~9–10 %
  welded-rpm BSFC penalty; load-point shifting worth only ~0.5 pt) is
  internally consistent and reproduced by the report's own two-ratio
  hand check (246 vs 263 g/kWh → ~6.3 %); the b' robustness run
  (within 0.2 % of b) supports the claim that the margin is not a
  supervisor-tuning artifact.
