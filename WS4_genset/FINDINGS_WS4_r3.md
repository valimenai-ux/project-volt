# FINDINGS — WS4 (genset + Gate G1) — review round 3 (G1-R rework)

Adjudicator: fresh-context adversarial review against BASELINE_v2.md and
G1R_DIRECTIVE.md. Artifacts judged: REPORT_WS4.md (G1-R revision, §0-R),
results_ws4.json, run_ws4.py / ws4_models.py / ws4_sim.py / ws4_chain.py /
make_report_ws4.py / verify_ws4.py, data/*.csv, figs/*.png,
run_output.txt, plus the read-only WS2 inputs (results.json,
data/cycle_loss_summary.csv, data/effmap_motor_inverter_662V.csv), on
disk as of 2026-08-30.

**Verdict: no blocking findings. One material finding (F1) and four
minor findings (F2–F5). The G1-R headline — nominal ensemble margin
-2.58% min / -2.50% median / -2.37% max, kill criterion ≥5% FAILED by
7.58 points, sign reversed — reproduces independently from the per-seed
fuels, the one-factor attribution closes arithmetically, the
prior-convention anchor equals the ratified r2 margins to 1e-9, the
genset-conditioning bracket confirms the kill outcome is invariant
(worst-case break-even +0.09% min is still 4.91 points short), the
pipeline regenerates every artifact byte-identically, and the interface
block is three-way verbatim-consistent. None of the findings below
moves the kill verdict. The material finding is a prose/data
contradiction on the one condition that resists the reversal: the data
shows FOUR of eight CdA 5.4 seeds positive, the report says two, in
four places including the headline and ESC-2.**

---

## Verification record (what was re-derived, independently)

- **Determinism**: full pipeline re-run from the entry point
  (`.venv/bin/python run_ws4.py`, then `make_report_ws4.py`, then
  `verify_ws4.py`, exit 0, 101 renderings + interface block).
  `REPORT_WS4.md`, `results_ws4.json`, `run_output.txt`, all five
  `data/*.csv` and all three `figs/*.png` regenerate **byte-identical**
  (SHA-256 compared before/after). The runtime assertions (prior-
  convention anchor to 1e-9, pinned points unmoved under the R10
  restatement, per-seed unserved limits, BSFC fast-path, WS1
  regression) all passed live during the re-run.
- **Chain-of-record provenance**: the SHA-256 hashes recorded in
  `results_ws4.json → ws2_chain_of_record → input_sha256` match the
  on-disk WS2 files exactly (map, results.json, cycle_loss_summary.csv);
  WS2's `_meta.rework.round` = 4 and `dc_bus.nominal_V` = 662.4, so the
  loader's nearest-key selection of the 662 V map is correct — the
  "WS2 round-4 / R10 bus chain of record" vintage claim is verified at
  the byte level, not by mtime.
- **Gate ensembles**: per-seed margins ((b−a)/b·100) and min/median/max
  recomputed from the stored per-seed corrected fuels for all six
  conditions — nominal (-2.5816/-2.5037/-2.3727), CdA 5.4
  (-0.0907/+0.0168/+0.1192), aux 4 kW (-2.2528/-1.9841), hot
  (-3.4927/-3.3110/-3.0590), 2,000 m+45 °C (-5.8971/-5.6624),
  reference curve (-2.2282/-2.0165) — all match the stored ensembles
  and the printed renderings exactly, including the governing-case
  labels (nominal min = seed 4, verified by argmin; R14 labels equal
  the recomputed governing seeds in all six cases). Kill arithmetic:
  5 − (−2.5816) = 7.58 points ✓.
- **One-factor attribution (directive 3)**: deltas recomputed from the
  stored row margins: spin alone −1.7682 pp, map swap alone −7.0136 pp,
  both −8.8430 pp; interaction −0.0612 pp (min) / −0.1001 pp (median) —
  the report's −1.77/−7.01/−8.84 and "-0.06/-0.10" renderings are
  exact. The prior-convention anchor equals the r2 ratified
  6.261345943773722 / 6.445177253781505 / 6.78407493099628 verbatim.
- **Genset-conditioning bracket**: stored rows verified
  (declared −2.5816; 3%-replacement −0.7916; stacked +0.0908/+0.1468/
  max +0.3442); "4.91 points short" = 5 − 0.0908 ✓; the bracket
  generators' loss parameters in run_ws4.py match their descriptions
  (pe0=0, pe_frac=0.03; pe0=0.15, pe_frac=0.04), and the pinned point
  re-derives inside each bracket config so mode (b) pays the stressed
  conversion too — verified in code.
- **R12 chain, independent re-implementation**: WS2's 662 V map was
  parsed with independent code; the per-cell identity
  P_dc = P_shaft + (P_cu+P_fe+P_fw+P_inv) holds on all 4,203 feasible
  cells in both quadrants to the CSV's printed precision (worst 1e-3
  kW). An independently written bilinear interpolator agrees with
  `ws4_chain.WS2TractionChain` to machine precision (2e-16) at 600
  random (v, P) points in both directions, and WS4's interpolator
  reproduces exact feasible cells to 9e-16 kW.
- **Spin member (directive 1b)**: rates re-derived from WS2's raw
  exports — 1.4851/(1.8373 × 0.7009) = 1.153240 kW shaft,
  0.5017/1.28776 = 0.389590 kW bus — equal to the stored rates to full
  precision; WS2's REPORT §7 and `interface.spin_drag`
  (`E_engine_side_VOLTREG_kWh`) explicitly label the shaft member
  **engine-side**, so WS4's charging convention (added to engine shaft
  torque during locked samples) is definitionally consistent with the
  producer's export — no wheel/shaft/bus mismatch. The per-seed energy
  actually charged (1.4581–1.4953 kWh shaft, 0.4926–0.5051 kWh bus)
  recomputed from per-seed values ✓; the 85 km/h point check
  (1.1532 vs 1.109 kW, ~4%) ✓. The D4 double-count fix (marginal map
  loss on locked torque-fill when the spin member is active) is
  present in `ws4_chain.eta_bus_to_wheel_marginal_scalar` and wired in
  `ws4_sim.run_g1_mode` exactly as described.
- **Directive 1c**: R10 window figures in both generator blocks match
  the ruling (662.4 / 432.0–748.8 / 777.6 V, 12-cell granularity);
  pinned points re-derived with an independent Willans + generator-loss
  implementation: V2 pin BSFC 203.616656 g/kWh, shaft 84.699696 kW,
  gen eta 0.95176128, bus 80.613895 kW — all to ≤5e-8 of stored; the
  unmoved-pin assertion ran live.
- **Secondary envelopes** (all recomputed from per-seed data): banking
  2.312–2.986, starts 46–62 (ref 46 / 42 sync), b emergency
  505.5–630.9 s nominal / 1,128.1–1,399.7 s CdA 5.4, b unserved
  0.0000 nominal / 0.000–0.522 CdA 5.4, b over-rating 42.1–71.5 /
  110.4–137.5 s (unchanged from r2, as claimed trace-determined),
  a over-rating 0.0, a locked fraction 0.692, a fuel-weighted BSFC
  221.9–223.3 g/kWh, a vs b′ −2.80..−2.48%, b vs b′ −0.36..+0.05% —
  every §0-R/§4.2/ESC-5 rendering is the correct rendering.
- **Hand checks**: ref-seed tractive wheel energy 78.85 kWh reproduced
  through WS1's physics (independent call); 19.04/78.85 = 241.5 and
  19.51/78.85 = 247.4 g/kWh at the wheel ✓; 203.6/(0.952 × 0.9005) =
  237.6 ✓; banking redeploy 0.952 × 0.97² × 0.9005 = 0.8065 ✓.
- **Interface, three-way**: the §11 JSON block extracted from the
  report is **byte-identical** to `json.dumps(results_ws4.json →
  interface_ws4)`; every `condition_dependence` entry equals its source
  case ensemble minimum to full float precision; `one_factor_sensitivity`
  and `genset_conditioning_bracket` mirror their `results` blocks
  verbatim; `passes: false` ✓.
- **Heat ledger**: the restated G1-R(a) row recomputed from the raw
  reference seed — engine rejection 78.31 kW avg, gen/chain/direct
  losses 1.08/0.76/1.73 kW, spin 1.466/0.495 kWh, friction 0.417 kWh —
  matches the §7 renderings (78.3, 1.1+0.8+1.7, 1.47/0.50, 0.42). All
  other rows verified unchanged from the ratified r2 record.
- **Compliance**: 8-seed envelopes everywhere extrema are quoted; G1
  quantities use maps only (no `part_load_factor` in any chain-mode
  path — verified in code); escalations cite the rulings they
  challenge (ESC-2: G1/R7/R11; ESC-6: R11/G1-R); directive items 1a,
  1b, 1c, 2, 3, 4 and the vintage statement are each executed and
  verifiable; the r3-interim historical block is carried as a JSON
  literal, rendered (not hand-typed) into the report, and honestly
  labeled non-regenerable.

---

## F1 — MATERIAL — the CdA 5.4 positive-seed count is wrong: the data shows four, the report says two, in four places including the headline and an escalation

**What is wrong.** `gate_g1/cda_5.4/per_seed` margins are: seed 23
−0.077, 3 −0.058, 4 **+0.087**, 5 −0.015, 6 −0.091, 7 **+0.103**,
8 **+0.119**, 9 **+0.048** — **four of eight seeds positive** (and the
median is positive, +0.0168, consistent with a 4/4 split). The report
states "two seeds marginally positive" in the headline, "two
marginally positive seeds" in §0-R, "two of eight seeds marginally
positive" in §6, and "two seeds marginally positive" in ESC-2. No
reading of "marginal" rescues the count: all four positives are ≤ the
printed max 0.12%. The claim is hard-coded prose in
`make_report_ws4.py` (lines 195, 302, 653, 855) — a hand-transcribed
current number, contrary to the report's own preamble discipline —
and no positive-seed count is exported, so `verify_ws4.py` had nothing
to check it against. Ironically the wording was introduced by the
disclosed pre-adjudication fix (iii), which corrected the categorical
"sign reversed everywhere" language into a new, also-wrong claim.

**Why it matters.** CdA 5.4 is the single condition that resists the
reversal, and ESC-6 builds the WS5 mode-policy re-premise ("lockup
approaches parity only where the welded load fraction is high") on
exactly this ensemble. Understating 4/8 as 2/8 understates how often
lockup actually wins at high road load — an error leaning toward the
report's own kill conclusion, in the decision-relevant escalation. It
does not move the verdict: the min/median/max renderings are correct,
the criterion fails by ≥4.91 points under every accounting, and a
correct count (4/8) if anything *strengthens* the "break-even"
reading and ESC-6's load-aware policy argument.

**Resolution.** Correct all four occurrences to the on-disk count
(four of eight, or "half the seeds"), export the count (or the
per-seed signs) machine-readably, and add it to `verify_ws4.py`.

## F2 — MINOR — the boundary-convention mode-neutrality claim (§4.1) is measured true only for the reference seed; at CdA 5.4 the exposure is 7–21 s/cycle, mostly on locked cruise samples, and one-sided in mode (b)'s favor

**What is wrong.** §4.1 (and the `ws4_chain.py` class doc) states:
"demands beyond the map's feasible envelope reuse the nearest boundary
loss — measured exposure is a few seconds per cycle, on unlocked
launch samples both modes drive identically through this same chain,
so the convention is mode-neutral and negligible (~0.001 kWh)."
Independently measured against the WS2 662 V map's feasibility
boundary: at **nominal**, exposure is 3.6–7.6 s/cycle and on the
reference seed it is indeed all launch samples (0–1 km/h) — but seeds
3/5/7/8/9 also have up to ~4 s of exposure at 93–98 km/h, samples that
are **locked** in mode (a) and therefore clamp-served only in mode
(b). At **CdA 5.4** the exposure is 7.4–20.6 s/cycle and
predominantly on locked ~94–98 km/h cruise samples (56–168 samples
per seed) — there the convention is not mode-neutral at all: it books
infeasible mode-(b) motor operation at clamped (understated) losses
while mode (a) serves those samples on the engine. Bounded magnitude:
over-boundary wheel energy ≤0.007 kWh (nominal) / ≤0.04 kWh
(CdA 5.4), so the fuel effect is order 0.01 pp nominal and a few
hundredths of a pp at CdA 5.4 — immaterial to the kill verdict, but
the same order as the ±0.09% per-seed margins the report
characterizes to two decimals at CdA 5.4, and its direction (flatters
pure series) leans toward the report's conclusion.

**Resolution.** Measure and state exposure per condition (a one-line
counter in the chain); restate §4.1 as "mode-neutral at the reference
seed, one-sided ≤~0.05 pp in (b)'s favor at CdA 5.4"; or extend the
map with a declared extrapolation beyond the feasible envelope. Note
the F-4 over-rating record already flags the same samples as
capability violations (R4).

## F3 — MINOR — the map-vintage "spread under 0.6 pp" claim is 0.63 pp on the printed record when the r3-interim figure it sweeps in is included

**What is wrong.** §4.2: "across the full 432–749 V window (and the
superseded r3 maps, §0-R) the spread is under 0.6 pp". The 432–749 V
window alone spans −2.8623 to −2.3474 = 0.51 pp ✓; but including the
r3-interim −2.9798 the parenthetical claims cover, the spread is
**0.63 pp**. The r3-interim figure is pre-D4-fix (like-for-like it
would be ≈ −2.89, keeping the claim true), but the number on the
record is −2.98. Materiality nil against the 7.58-point shortfall.

**Resolution.** Restate as "~0.6 pp", or scope the sentence to the
432–749 V maps and cite the r3-interim comparison separately (as §0-R
already does, correctly, as "within ~0.4 pp").

## F4 — MINOR — the interface's traction-map path is relative to WS2's folder while every other file path in `interface_ws4` is relative to WS4's

**What is wrong.** `interface_ws4 → gate_g1 → traction_chain_of_record
→ map_file` = `"data/effmap_motor_inverter_662V.csv"` — resolvable
only against `../WS2_traction_motor/`. Every other `*_file` field in
the same interface (`bsfc_map_file`, `gen_map_file`, …) resolves
against the WS4 folder, which contains no `effmap_*` file. A
downstream consumer resolving uniformly gets a missing file; one
resolving against WS4's data/ silently has no chain of record. The
prose (§13) and the SHA-pinned `ws2_chain_of_record` block make the
intent recoverable, but the interface field itself is ambiguous — the
machine-readable-interface failure class this program watches, in its
mildest form.

**Resolution.** Qualify the path (`../WS2_traction_motor/data/…`) or
add an explicit root/owner field to `traction_chain_of_record`.

## F5 — MINOR — §4.3's "energy-weighted bus→wheel chain of 0.9005 … on the same trace" carries WS2's i-MMD duty weighting, not the series-duty weighting the narrative applies it to

**What is wrong.** 0.9005 = 0.97 × WS2's exported `eta_mot_avg`
(0.9284), which is energy-weighted over WS2's i-MMD VOLT-REG run —
i.e. over the traction energy the motor handles when mostly unlocked
(launch-heavy, low-load). Recomputing the energy-weighted chain for
the full-trace series duty (what mode (b) actually realises, wheel
energy / bus energy through the same map) gives **0.916** on the
reference seed; the ideal series fuel-to-wheel is then ≈233.5 g/kWh,
not 237.6. The simulation itself is unaffected (it uses the map
per-sample; the sim's (b) delivers 241.5 g/kWh); the code labels the
number honestly ("the honest single-number stand-in"), and the
direction of the imprecision *understates* the series advantage —
conservative toward the clutch. But §4.3 presents 0.9005 as the
trace-weighted chain, and §10 check 5's banking argument then
compares the redeploy rate (where 0.9005, launch-weighted, *is* the
right weighting) against a series wheel rate built on the same
understated number — the two-ratio story lands on the right
conclusion with a slightly misattributed middle step.

**Resolution.** Label 0.9005 as WS2's cycle-share weighting and quote
the series-duty weighted value (~0.916) alongside it in §4.3, or
derive the sanity chain from the sim's own (b) energy totals.

---

## Notes for the lead (not findings)

1. **The reversal itself withstood adversarial re-derivation.** The
   −7.01 pp map-swap dominance is real: the ruled chain is ~0.90–0.92
   bus→wheel where the r2 convention charged ~0.84, series banks that
   improvement over ~100% of its traction energy while the locked path
   collects it only on the ~30% unlocked share plus torque-fill, and
   the measured spin member is a pure lockup tax. The hand
   reconstruction (241.5 vs 247.4 g/kWh at the wheel from two stored
   totals) reproduces the reference-seed sign with no simulation in
   the loop. F1–F5 are record-precision defects, not cracks in the
   verdict.
2. **The chain of record is an unadjudicated WS2 export.** G1-R runs
   on WS2 round-4 outputs; no FINDINGS_WS2_r4 exists on disk yet. The
   directive ordered exactly this consumption and WS4 SHA-pinned the
   inputs, so this is sequencing, not a WS4 defect — but the gate
   verdict formally inherits WS2 r4's correctness. Mitigation already
   on the record: the verdict is insensitive across all three exported
   maps (0.51 pp) and across the r3→r4 vintage change (~0.4 pp), and
   the kill margin is 7.58 points; a WS2-r4 defect large enough to
   change the outcome would have to be enormous.
3. WS2 quotes the spin shaft member at the 120 °C winding convention
   and notes it books ~5% higher at 170 °C; WS4 consumed the 120 °C
   figure, which is the convention consistent with the maps it also
   consumed. A hostile +5% on the member is ≈0.09 pp *against* the
   clutch — the choice is internally consistent and does not flatter
   the losing side.
4. ESC-2/ESC-6 correctly flag that BASELINE_v2's R11 note ("even at
   the corner lockup beats series by ~3.8%") is contradicted by the
   G1-R record (corner −5.90%, sign reversed) — that correction to
   the baseline record is the lead's to make, and the numbers behind
   it verify.

---

Key paths: `/Users/valimenai/Documents/Project Volt/WS4_genset/REPORT_WS4.md`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/results_ws4.json`,
`/Users/valimenai/Documents/Project Volt/WS4_genset/make_report_ws4.py`
(F1: lines 195, 302, 653, 855), `/Users/valimenai/Documents/Project Volt/WS4_genset/ws4_chain.py`
(F2 basis claim; F4 field assembled in run_ws4.py §8),
`/Users/valimenai/Documents/Project Volt/WS4_genset/verify_ws4.py`
(exit 0, 101 renderings + interface block).
