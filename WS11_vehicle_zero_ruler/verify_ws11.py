"""
Project Volt - WS11
Verifies REPORT_WS11.md against results_ws11.json, verbatim.

For every (json_path, format, rendered) triple recorded by
make_report_ws11.py in data/report_assertions.csv, this script:
  1. re-resolves the path independently out of results_ws11.json,
  2. re-formats it with the recorded format spec,
  3. asserts the result equals the recorded string, and
  4. asserts that string is literally present in REPORT_WS11.md.

Nothing in the report is transcribed by hand, so a drift between the
report and the results file is impossible without this failing.

It also re-checks the structural invariants of the run independently of
run_ws11.py: the WS4 hot-swap regression, the per-km / per-payload
identity on every seed of every case, the mass arithmetic, the verdict
logic against the pre-committed criterion, and R14 export discipline
(every worst-case field carries a governing case).

    python verify_ws11.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)
    return cond


with open("results_ws11.json") as f:
    R = json.load(f)
with open("REPORT_WS11.md") as f:
    REPORT = f.read()


def resolve(path):
    node = R
    for part in path.split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


# ------------------------------------------- 1. every reported number, verbatim
n_ok = 0
with open(os.path.join("data", "report_assertions.csv")) as f:
    rows = list(csv.DictReader(f))
check(len(rows) > 100, f"only {len(rows)} asserted numbers - report is thin")
for r in rows:
    path, spec, rendered = r["json_path"], r["format"], r["rendered"]
    try:
        val = resolve(path)
    except (KeyError, IndexError, ValueError) as exc:
        FAIL.append(f"{path}: not resolvable in results_ws11.json ({exc})")
        continue
    re_rendered = str(val) if spec == "raw" else format(val, spec)
    if not check(re_rendered == rendered,
                 f"{path}: results_ws11.json renders {re_rendered!r} but the "
                 f"report was built from {rendered!r}"):
        continue
    if not check(rendered in REPORT,
                 f"{path}: {rendered!r} is not present verbatim in "
                 f"REPORT_WS11.md"):
        continue
    n_ok += 1
print(f"[1] {n_ok}/{len(rows)} reported values verify verbatim against "
      f"results_ws11.json")

# --------------------------------------------------- 2. WS4 hot-swap seam
reg = R["ws4_regression"]
ws4_path = os.path.join("..", "WS4_genset", "results_ws4.json")
with open(ws4_path) as f:
    ens = json.load(f)["interface_ws4"]["series_duty_v2"]["cases"]["nominal"]\
        ["ensemble"]
for k in ("min", "median", "max"):
    check(reg["ws11"][k] == reg["ws4"][k],
          f"regression {k}: {reg['ws11'][k]!r} vs {reg['ws4'][k]!r}")
    check(reg["ws4"][k] == ens[f"fuel_energy_kWh_per_km_{k}"],
          f"regression {k}: stored WS4 value has drifted from "
          f"WS4/results_ws4.json")
check(reg["max_abs_difference"] < 1e-12,
      "WS4 hot-swap regression exceeds 1e-12")
print(f"[2] WS4 series_duty_v2[nominal] reproduced to "
      f"{reg['max_abs_difference']:.1e} (identical floats)")

# ------------------------------- 3. per-km / per-payload identity, every seed
worst = 0.0
n_seed = 0
for key, blocks in R["results"].items():
    for case, b in blocks.items():
        rr = b["payload_kg_ruler"] / b["payload_kg_candidate"]
        for s, mk in b["margin_pct_per_km_paired"]["per_seed"].items():
            mp = b["margin_pct_per_payload_tkm_paired"]["per_seed"][s]
            worst = max(worst, abs((1 - mp / 100.0)
                                   - (1 - mk / 100.0) * rr))
            n_seed += 1
check(worst < 1e-12, f"per-km/per-payload identity residual {worst:.3e}")
print(f"[3] per-km <-> per-payload identity holds on {n_seed} seed-cases, "
      f"max residual {worst:.3e}")

# -------------------------------------------------- 4. envelopes are paired
n_env = 0
for key, blocks in R["results"].items():
    for case, b in blocks.items():
        for metric in ("margin_pct_per_km_paired",
                       "margin_pct_per_payload_tkm_paired"):
            e = b[metric]
            v = list(e["per_seed"].values())
            check(abs(e["min"] - min(v)) < 1e-12,
                  f"{key}/{case}/{metric}: min is not the min of the "
                  f"per-seed values (a ratio-of-medians artefact would look "
                  f"exactly like this - R36/D13)")
            check(abs(e["max"] - max(v)) < 1e-12,
                  f"{key}/{case}/{metric}: max is not the max of the "
                  f"per-seed values")
            check(len(v) == 8, f"{key}/{case}/{metric}: not an 8-seed "
                               f"ensemble (R9)")
            check("min_governing_case" in e and "max_governing_case" in e,
                  f"{key}/{case}/{metric}: missing governing case (R14)")
            n_env += 1
print(f"[4] {n_env} margin envelopes are paired per-seed, 8 seeds, with "
      f"governing cases (R9/R14/R36)")

# ------------------------------------------------------- 5. mass arithmetic
ml = R["mass_ledger"]
gvw = ml["gvw_kg"]
for k, t in ml["totals"].items():
    check(abs(t["curb_kg"] + t["payload_at_gvw_kg"] - gvw) < 1e-9,
          f"{k}: curb + payload != GVW")
be = ml["break_even_per_km_advantage_pct"]
for k in ("V1", "V2"):
    expect = 100.0 * (1.0 - ml["totals"][k]["payload_at_gvw_kg"]
                      / ml["totals"]["ruler"]["payload_at_gvw_kg"])
    check(abs(be[k] - expect) < 1e-9, f"{k}: break-even bar inconsistent")
print("[5] mass arithmetic closes: curb + payload = GVW on every vehicle, "
      "break-even bars consistent")

# --------------------------------------------------- 6. verdict logic
crit = R["advance_kill"]["criterion"]
for key, v in R["advance_kill"]["verdicts"].items():
    blocks = R["results"][key]
    nom = blocks["nominal"]["margin_pct_per_payload_tkm_paired"]["min"]
    check(v["nominal_margin_pct_min"] == nom,
          f"{key}: verdict nominal margin does not match the results block")
    corners = {c: blocks[c]["margin_pct_per_payload_tkm_paired"]["min"]
               for c in blocks if c != "nominal"}
    check(v["corner_margins_pct_min"] == corners,
          f"{key}: verdict corner set does not match the results blocks")
    check(v["worst_corner_margin_pct"] == min(corners.values()),
          f"{key}: worst corner is not the min over the enumerated set (R14)")
    expect = ("ADVANCE" if (nom >= crit["nominal_threshold_pct"]
                            and min(corners.values())
                            >= crit["corner_threshold_pct"]) else "KILL")
    check(v["verdict"] == expect,
          f"{key}: verdict {v['verdict']} does not follow from the numbers")
print("[6] both verdicts follow mechanically from the pre-committed "
      "criterion: " + ", ".join(f"{k}={v['verdict']}" for k, v in
                                R["advance_kill"]["verdicts"].items()))

# ------------------------------------------------------ 7. R14 export discipline
iface = R["interface_ws11"]
check(iface["_basis"].startswith("mirrors"), "interface missing _basis")
for k, v in iface["verdicts"].items():
    for field in ("nominal_margin_pct_min_governing_case",
                  "worst_corner_governing_case"):
        check(isinstance(v.get(field), str) and len(v[field]) > 10,
              f"interface verdicts.{k}: {field} missing or empty (R14)")
sc = iface["sustained_6pct_capability_kmh"]
check("governing_case" in sc and "worst_case_value" in sc,
      "interface sustained_6pct: missing worst-case/governing pair (R14)")
check(abs(sc["worst_case_value"]
          - min(sc["ruler"], sc["V1"], sc["V2"])) < 1e-12,
      "interface sustained_6pct worst_case_value is not the min over the "
      "enumerated set")
for k, v in iface["trip_time_r38"].items():
    check("ratio_worst_governing_case" in v,
          f"interface trip_time_r38.{k}: missing governing case (R14)")
check(len(iface["input_sha256"]) >= 15,
      "interface input_sha256 does not pin every consumed input")
check(len(iface["traces_r34"]) >= 5,
      "fewer than five 10 Hz traces exported (R34)")
for t in iface["traces_r34"]:
    check(os.path.exists(t["file"]), f"declared trace missing: {t['file']}")
print(f"[7] R14 export discipline: governing cases present, "
      f"{len(iface['input_sha256'])} SHA-256 pins, "
      f"{len(iface['traces_r34'])} 10 Hz traces on disk (R34)")

# ------------------------------------------- 8. escalations cite their rulings
esc = R["escalations"]
check(len(esc) >= 5, "fewer than five escalations")
for e in esc:
    check(all(k in e for k in ("id", "challenges", "title", "text",
                               "requested")),
          f"escalation {e.get('id')}: incomplete")
    check(e["id"] in REPORT, f"escalation {e['id']} missing from the report")
print(f"[8] {len(esc)} escalations, each citing what it challenges, all "
      f"present in the report")

# ------------------------- 9. our SHA pins agree with WS4's own declared pins
mine = R["_meta"]["input_sha256"]
theirs = R["input_vintages"]["ws4_series_duty_v2"]["input_sha256_declared_by_ws4"]
shared = sorted(set(mine) & set(theirs))
check(len(shared) >= 8,
      f"only {len(shared)} pins shared with WS4's declared set - the key "
      f"naming has drifted and the cross-check is not being made")
for k in shared:
    check(mine[k] == theirs[k],
          f"{k}: WS11 read {mine[k][:12]}... but WS4 declares "
          f"{theirs[k][:12]}... - WS11 and WS4 did NOT consume the same file")
print(f"[9] {len(shared)} of WS11's input pins are also declared by WS4's "
      f"series_duty_v2, and every one matches - both workstreams consumed "
      f"byte-identical upstream files")

# ------------- 10. B2: the two statements of steady speed on 6% must agree
recon = R["sustained_6pct_capability"]["forward_pass_reconciliation"]
tol = recon["tolerance_kmh"]
n_rec = 0
for k, row in recon["rows"].items():
    check(row["ruler_abs_difference_kmh"] <= tol,
          f"{k}: the capability pass settles the RULER at "
          f"{row['ruler_forward_pass_kmh']:.2f} km/h on the sustained 6% "
          f"grade but the closed-form sustainable speed is "
          f"{row['ruler_closed_form_kmh']:.2f} km/h. Two fields of one "
          f"results file cannot both be true (adjudication r1/B2).")
    check(row["candidate_abs_difference_kmh"] <= tol,
          f"{k}: the capability pass settles {row['candidate']} at "
          f"{row['candidate_forward_pass_kmh']:.2f} km/h but the "
          f"closed-form sustainable speed is "
          f"{row['candidate_closed_form_kmh']:.2f} km/h")
    n_rec += 1
# and: any trip-time row on a corner carrying a sustained 6% grade MUST
# report a settled speed, and any row that does not carry one MUST NOT.
for k, v in R["trip_time_r38"].items():
    has = v["ruler_settled_speed_on_6pct_kmh"] is not None
    check(has == (v["case"] == "climb_10km_6pct"),
          f"trip_time_r38.{k}: settled_speed_on_sustained_climb is "
          f"{'present' if has else 'absent'} but the case is {v['case']} - "
          f"the field is only meaningful on a corner carrying a SUSTAINED "
          f"6% grade (adjudication r1/B2)")
check(n_rec >= 1, "no sustained-climb corner reconciled at all")
print(f"[10] B2: settled climb speed reconciles with "
      f"sustained_6pct_capability_kmh on {n_rec} corner(s) to within "
      f"{tol:.1f} km/h, and is exported only where a sustained grade exists")

# ---------- 11. B1: every declared ruler lever is in the bracket set, and
# ---------- the robustness row reverses all of them and no road change
brk = R["ruler_calibration"]["brackets"]
for need in ("gear_mesh_pessimistic", "at_pump_pessimistic",
             "final_drive_pessimistic", "lockup_slip_pessimistic",
             "all_ruler_modelling_choices_pessimistic"):
    check(need in brk, f"bracket `{need}` missing - a declared "
                       f"ruler-favourable choice is not bracketed "
                       f"(adjudication r1/B1)")
check(brk["all_ruler_modelling_choices_pessimistic"]["kind"]
      == "ruler_modelling_combination",
      "the robustness row is not classified as a pure ruler-modelling "
      "combination")
check(brk["CdA_5.4"]["kind"].startswith("road_load_change"),
      "CdA 5.4 is not classified as a road-load change")
# M4: the note must not claim what the data contradicts. Check the claim
# directly instead of trusting prose: every ruler_modelling row raises the
# candidate's margin; the road-load row lowers it.
n_kind = 0
for run, rows in R["ruler_bracket_effect_on_margin"]["rows"].items():
    base = rows["headline_ruler_favourable"]["min"]
    for name, e in rows.items():
        if e["kind"] in ("ruler_modelling", "ruler_modelling_combination"):
            check(e["min"] >= base - 1e-9,
                  f"{run}/{name} is classified ruler_modelling but LOWERS "
                  f"the candidate's margin ({e['min']:.4f} < {base:.4f})")
            n_kind += 1
        elif e["kind"].startswith("road_load_change"):
            check(e["min"] <= base + 1e-9,
                  f"{run}/{name} is classified a road-load change but "
                  f"raises the candidate's margin")
            n_kind += 1
check(len(R["ruler_bracket_effect_on_margin"]["rows"]) >= 3,
      "bracket margins were not run for both vehicles on both duties (B1)")
print(f"[11] B1: all four driveline levers bracketed; {n_kind} bracket rows "
      f"move in the direction their `kind` claims, on "
      f"{len(R['ruler_bracket_effect_on_margin']['rows'])} vehicle x duty "
      f"pairings")

# ------------------- 12. B3: the flip points are first-class R14 fields
flip = R["interface_ws11"]["ruler_fuel_flip_points"]
for key, v in R["advance_kill"]["verdicts"].items():
    check(key in flip, f"no ruler-fuel flip point exported for {key} "
                       f"(adjudication r1/B3)")
    f = flip[key]
    for fld in ("pct_ruler_fuel_error_to_draw",
                "pct_ruler_fuel_error_to_3pct_bar"):
        check(isinstance(f.get(fld), float), f"{key}: {fld} missing")
        check(isinstance(f.get(fld + "_governing_case"), str)
              and len(f[fld + "_governing_case"]) > 10,
              f"{key}: {fld} carries no governing case (R14)")
    # the flip point must reproduce from the margin it is derived from
    m = v["nominal_margin_pct_min"]
    ks = list(R["ruler_fuel_flip_points"]["cases"][key]["nominal"]
              ["to_0pct"]["multiplier_per_seed"].values())
    check(abs(max(ks) - (1.0 - m / 100.0)) < 1e-12,
          f"{key}: the 0% flip multiplier does not reproduce from the "
          f"per-seed margins")
check(R["ruler_calibration"]["corridor_check"]["calibrate_order_satisfied"]
      is False,
      "the calibrate order is recorded as satisfied; no ruler parameter was "
      "moved to the anchor, so it was not")
print("[12] B3: ruler-fuel flip points exported for both verdicts with "
      "governing seeds, and they reproduce from the per-seed margins")

# ---------------- 13. M2: pending rulings are reachable from the interface
iface_s = json.dumps(R["interface_ws11"])
check("ESC-" in iface_s,
      "no ruling ID appears anywhere in interface_ws11 (R14 requires "
      "fields conditioned on a pending ruling to carry the ruling ID)")
pend = R["interface_ws11"]["pending_rulings_r14"]
esc_ids = {e["id"].replace("-", "_") for e in R["escalations"]}
for k in pend:
    if k.startswith("_"):
        continue
    check(k in esc_ids, f"interface pending ruling {k} is not an escalation")
    check("priced_by" in pend[k] and "conditions" in pend[k],
          f"pending ruling {k}: missing conditions/priced_by")
for need in ("cold_corner_pending_items", "verdict_robustness",
             "capability_and_limit_worst_case", "ruler_idle"):
    check(need in R["interface_ws11"],
          f"interface is missing `{need}` - a downstream consumer reading "
          f"only the interface cannot reach it")
print(f"[13] M2: {len([k for k in pend if not k.startswith('_')])} pending "
      f"rulings carried in the interface, each naming what it conditions "
      f"and what prices it")

# --------------------- 14. M6: every one-factor row is a paired statistic
n_of = 0
for run, rows in R["one_factor"]["rows"].items():
    for name, d in rows.items():
        key = "cost_pp" if "cost_pp" in d else "worth_pp"
        ps = d.get(key.replace("_pp", "_pp_paired_per_seed"))
        if ps is None and key == "cost_pp":
            ps = None
        check("PAIRED" in d.get("statistic", ""),
              f"one_factor {run}/{name}: not declared paired (R36)")
        if ps:
            check(abs(d[key] - min(ps.values())) < 1e-9,
                  f"one_factor {run}/{name}: {key} is not the min of the "
                  f"per-seed paired differences (R36/D13)")
        n_of += 1
check("idle" in R["one_factor"]["rows"]["V1_on_VOLT-SUB"]
      ["engine_operating_point"]["description"].lower(),
      "the engine-operating-point row does not say what happens to idle")
check("ABSORBED" in R["one_factor"]["rows"]["V1_on_VOLT-SUB"]
      ["engine_operating_point"]["description"],
      "the engine-operating-point row still implies idle survives it "
      "(adjudication r1/M6b)")
print(f"[14] M6: {n_of} one-factor rows are paired per-seed statistics")

# ---------------- 15. M5: the anchor is an enumerated set with both members
a = R["interface_ws11"]["ruler"]["anchor"]
check(set(a["enumerated_member_set"]) == {"all_model_years", "fourhk1_era"},
      "the anchor is not exported as an enumerated two-member set (R14)")
check(a["worst_residual_vs_model_pct"]
      == min(a["all_model_years"]["residual_vs_model_pct"],
             a["fourhk1_era"]["residual_vs_model_pct"]),
      "the anchor's worst residual is not the min over the enumerated set")
check("BEST" in a["era_note_direction"],
      "the era note does not state the direction the data points in "
      "(adjudication r1/B3)")
print(f"[15] M5: anchor exported as a two-member enumerated set; worst "
      f"residual {a['worst_residual_vs_model_pct']:.2f}% governed by "
      f"{a['worst_residual_governing_case']}")

# -------------- 16. m6/R34: each verdict's GOVERNING corner has a trace
traced = {os.path.basename(t["file"]) for t in
          R["interface_ws11"]["traces_r34"]}
for key, v in R["advance_kill"]["verdicts"].items():
    veh, duty = key.split("_on_")
    corner = v["worst_corner_governing_case"].split(" ")[0]
    seed = R["_meta"]["seeds"][duty][0]
    want = {f"trace_{veh}_{duty}_{corner}_seed{seed}_10Hz.csv",
            f"trace_ruler_{duty}_{corner}_seed{seed}_10Hz.csv"}
    for w in want:
        check(w in traced,
              f"{key}: the GOVERNING corner ({corner}) is not traced - "
              f"{w} missing (R34, adjudication r1/m6)")
print(f"[16] R34: {len(traced)} traces on disk, including both verdicts' "
      f"governing corners")

# ------------------------------------------------------------------ result
print()
if FAIL:
    print(f"VERIFY FAILED - {len(FAIL)} problem(s):")
    for m in FAIL:
        print("  - " + m)
    sys.exit(1)
print("VERIFY OK - REPORT_WS11.md verifies verbatim against "
      "results_ws11.json, and every structural invariant holds.")
