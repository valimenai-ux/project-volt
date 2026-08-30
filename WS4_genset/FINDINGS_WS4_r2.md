# FINDINGS — WS4 (genset + Gate G1) — review round 2

Adjudicator: fresh-context adversarial review against BASELINE_v1.md.
Artifacts judged: ASSIGNMENT.md, REPORT_WS4.md (rework r2),
results_ws4.json, run_ws4.py / ws4_models.py / ws4_sim.py /
make_report_ws4.py / verify_ws4.py, data/*.csv, figs/*.png,
run_output.txt, FINDINGS_WS4_r1.md, on disk as of 2026-08-29.

**Verdict: no blocking or material findings. No new findings of any
severity. All seven round-1 findings are genuinely resolved (F5
recorded as agreed, per its own resolution text), not cosmetically:
each fix was verified at the code level, the data level, and by
independent recomputation. The rework introduced no new defect that
this review could find. The nominal G1 headline, the R6 corner, the
pinned points, the heat ledger, and the V1 start-stop numbers are
unchanged to full precision from round 1.**

---

## Round-1 finding disposition (independently verified, not taken from §0)

- **F1 (material — stale 1.9 kWh in ESC-5): RESOLVED.** The 1.9 kWh
  claim is withdrawn in ESC-5 with an explicit provenance note (stale
  pre-D2 value) — a correction on the record, not a silent deletion.
  ESC-5 now reads "up to 0.12 kWh at nominal and up to 0.77 kWh at
  CdA 5.4 (8-seed range 0.46–0.77 kWh)". Recomputed from
  `gate_g1/*/per_seed/*/b/unserved_kWh`: nominal max 0.1240 kWh,
  CdA 5.4 range 0.4632–0.7677 kWh — the renderings are correct. The
  values are now exported as ensemble envelopes
  (`b_unserved_kwh_min/max`) and covered by `verify_ws4.py` (checks
  "b unserved max nom", "b unserved min/max cda"). ESC-5's other
  figures also verify: emergency 484–805 s nominal (483.90–804.90),
  1,504–1,734 s at CdA 5.4 (1504.50–1733.60), both now exported and
  checked.
- **F2 (material — unconditional gate pass in the interface):
  RESOLVED.** `interface_ws4 → gate_g1` now carries a `condition`
  string ("nominal: sea level, rho 1.20 kg/m^3, CdA 4.2 m^2, 2 kW aux,
  GVW, VOLT-REG") and a `condition_dependence` block with the R7
  corner (min 3.7512%, `passes_at_2000m_45C: false`), the new hot-day
  case (min 5.9360%, passes true), CdA 5.4 (8.2247, passes), aux 4 kW
  (6.4565, passes), and `see: ESC-2`. Every one of those eight values
  was compared against the corresponding `gate_g1/<case>/ensemble`
  entry: all equal to full float precision. An interface-only consumer
  now sees the corner failure. This closes the WS1-era failure class
  the finding named.
- **F3 (minor — F-4 spliced two configurations): RESOLVED.** F-4 now
  states "42.1–71.5 s per VOLT-REG cycle at nominal and 110.4–137.5 s
  at CdA 5.4 (8-seed envelopes)", with the old "61–136 s" withdrawn on
  the record. Recomputed from per-seed `over_rating_s`: nominal
  42.10–71.50 s, CdA 5.4 110.40–137.50 s — exact. §4.2 restates the
  nominal envelope at one decimal from the same data; both ranges are
  verify-covered.
- **F4 (minor — no standalone hot-day G1 case): RESOLVED.** A sixth
  `g1_config` (`hot_45C_sea_level`) runs sea level at +45 °C.
  Independently re-derived: ρ = 101325/(287 × 318.15) = 1.1097 kg/m³
  (ideal gas, exact); derate_factor(0, 45) = 1 − 0.002·15 = 0.97
  (exact); the pinned point is unchanged under the 0.97 derate (the
  84.7 kW pin sits inside both the 128.04 kW derated continuous cap
  and the derated full-load curve — confirmed: hot `pinned_point` ==
  nominal `pinned_point` verbatim). Margins recomputed from per-seed
  corrected fuels: 5.9360 min (seed 5) / 6.0812 median / 6.4175 max —
  matches the report's 5.94 / 6.08 / 6.42 renderings. The reference-
  seed fuel correction was reconstructed by hand for both modes
  (drift +0.41826 / +0.41678 kWh, unserved 0 / 0.18660 kWh, at the
  pinned marginal rates): reproduces the stored `fuel_corrected_g` to
  0 g in both modes. The report's reading — heat alone passes, the
  failure needs altitude+heat combined — is supported by the data.
- **F5 (minor — R6 margin inside its input uncertainty): RECORDED, as
  the finding itself prescribed.** Nothing recomputed (correct); §2
  now carries "Compliance status: PROVISIONAL" and
  `interface_ws4 → v2_genset → r6_corner → status` carries the same
  condition with an explicit "do not release WS6 packaging" clause.
  The corner numbers are unchanged: 0.96 × 0.97 = 0.9312,
  132.0 × 0.9312 = 122.9184 kW, margin +0.8184 kW (re-derived from
  first principles).
- **F6 (minor — prose/data drifts, map rounding): RESOLVED.** §5's
  3.0 kWh row now prints 3.37 L/h (data: 3.3652 — correct rendering;
  the 0.8 kWh row's 3.41 is separately correct at 3.4088); §3 prints
  249.3 g/kWh (data: 249.29). Both are in `verify_ws4.py`. The map
  CSVs print torque at 1e-4 Nm with a header note; an independent
  re-implementation of the declared Willans formula recomputing BSFC
  from the *printed* (rpm, torque) pairs finds worst-case disagreement
  0.053 g/kWh on the V2 map and 0.050 g/kWh on the reference map
  across all ~6,000 rows each — the printed pairs are now
  self-consistent as the fix intended.
- **F7 (minor — accounting/reproducibility nits): RESOLVED.** (i) The
  locked-sample torque-fill rating check exists in `ws4_sim.py`
  (deficit-fill motor-shaft power `deficit_wheel / eta_red` vs the
  150 kW rating, same convention as the unlocked branch);
  `a/over_rating_s` was checked across all 6 configurations × 8 seeds:
  0.0 s everywhere — the changelog's "every seed and configuration"
  claim is true of the data, and the nominal value is verify-covered.
  (ii) `run_output.txt` no longer embeds wall-clock text and is
  byte-identical under re-run (verified by hash).

## Verification record (round 2)

- **Determinism**: full pipeline re-run from the entry point
  (`.venv/bin/python run_ws4.py`, then `make_report_ws4.py`, then
  `verify_ws4.py`, exit 0, 71 renderings + interface block).
  `results_ws4.json`, `REPORT_WS4.md`, `run_output.txt`, all five
  `data/*.csv`, and all three `figs/*.png` regenerate
  **byte-identical** (SHA-256 compared). The committed tree is now
  fully byte-stable — the r1 wall-clock exception is gone.
- **Interface, three-way**: the §11 JSON block was extracted
  independently and compared to `json.dumps(results_ws4.json →
  interface_ws4)`: **byte-identical**. The gate figures inside it
  equal the nominal ensemble to full precision; every
  `condition_dependence` entry equals its source case ensemble to full
  precision; report prose renderings spot-checked throughout §0, §2–§7,
  F-4, ESC-2 and ESC-5 against the JSON.
- **Unchanged numbers preserved** (the silent-drop check): G1 nominal
  6.261346 / 6.445177 / 6.784075 % — identical to round 1's
  independently recomputed values; R6 corner 0.9312 / 122.9184 kW /
  +0.8184 kW — identical; both pinned points, all four candidate
  corner rows (121.06 / 122.92 / 120.12 / 102.43 kW), the heat-ledger
  entries (77.206 / 78.815 / 95.018 / 96.998 / 17.900 / 24.354 /
  10.058 / 77.954 kW — corner balance re-derived: 219.571 g/kWh →
  320.873 kW fuel → 197.955 kW rejected → 0.48/0.49 split, sums
  close), and the V1 set (66.11 starts ref, 57.41–74.35 ensemble,
  6.198 % saving, cold 4.83 L/h = +41.7 %, duty 0.4130 → 0.5948) all
  match round 1's verification record exactly. Every declared change
  in §0 lists its old value; no previously reported number was found
  dropped or altered without declaration.
- **Ensemble recomputation**: per-seed margins ((b−a)/b·100) and
  min/median/max recomputed from raw corrected fuels for all six
  configurations — nominal, CdA 5.4 (8.2247/8.3633/8.5520), aux 4 kW
  (6.4565/6.6308), hot day (5.9360/6.0812/6.4175), alt corner
  (3.7512/3.9162/4.1506), reference curve (6.5823/6.7550) — all match
  the stored ensembles and the report to the printed precision,
  including the headline's "3.75%–4.15%" and "5.94%–6.42%". The b′
  robustness figures verify (a beats b′ by 6.19–6.75 %; b within
  −0.08/+0.18 % of b′, i.e. "within 0.2 %"). Reference-seed prose
  (19.41/20.72 kg, 17.68/18.87 L/100 km, 69.2 % locked, 46 starts of
  which 42 sync, banks 1.5–3.3 kWh, starts 46–62) all verified.
- **Compliance**: 8-seed ensemble convention everywhere extrema are
  quoted, including (new this round) the secondary quantities in §4.2,
  F-4 and ESC-5; part-load models unchanged and everywhere; heat
  reported by component and case; all five escalations cite rulings
  (R6; G1/R7; R8/R5; R9; R8); assignment tasks 1–6 now fully covered —
  the r1 F4 coverage gap (standalone hot day) was the last one.
- **New-defect hunt** (the rework's changed surface): the new `_mm`
  ensemble exports, the locked-sample rating check, the hot-day
  configuration, the `condition_dependence` block, the CSV torque
  format, and the 22 new verify checks were each read and re-verified;
  the per-seed unserved assertion limits (0.3 kWh nominal / 2.0 kWh
  off-nominal) still bound every case (hot worst seed 0.199 kWh).
  Nothing rose to a finding.

## Observations (not findings)

1. The V1 map CSV's near-zero-torque rows still disagree with the
   declared formula by up to 2.45 g/kWh — but only where BSFC is
   ~13,000 g/kWh (0.02 % relative), and the cause is the integer-
   rounded *rpm* column, not the torque column F6 addressed. Far below
   any materiality threshold; noted only so the residual is on the
   record.
2. A few `verify_ws4.py` renderings are short strings ("46", "484",
   "33") whose verbatim-substring test has weak discriminating power.
   All were independently confirmed correct this round; this is a note
   on the harness's sensitivity, not on any number.
3. ESC-2's request that the lead ratify the nominal-condition reading
   of G1 remains open and is now faithfully mirrored in the interface.
   That is a decision for the lead, not a WS4 defect; the record the
   lead needs (nominal pass 6.26 %, corner fail 3.75 %, hot-day pass
   5.94 %, sign never flips) is complete and verified.

---

Key paths: `/Users/valimenai/Documents/Project Volt/WS4_genset/REPORT_WS4.md`, `/Users/valimenai/Documents/Project Volt/WS4_genset/results_ws4.json`, `/Users/valimenai/Documents/Project Volt/WS4_genset/verify_ws4.py` (71 checks, exit 0), `/Users/valimenai/Documents/Project Volt/WS4_genset/FINDINGS_WS4_r1.md` (all dispositions above verified against it).

---

*Placement note (foreman, for the record): the adjudicator subagent's direct file write was refused by the harness; the foreman placed this document at the adjudicator's mandated path verbatim and unmodified from the adjudicator's returned text, with HTML entity encoding (`&lt;`, `&gt;`) restored to the literal characters the adjudicator wrote.*
