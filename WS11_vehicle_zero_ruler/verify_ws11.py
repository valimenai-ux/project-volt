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

# ------------------------------------------------------------------ result
print()
if FAIL:
    print(f"VERIFY FAILED - {len(FAIL)} problem(s):")
    for m in FAIL:
        print("  - " + m)
    sys.exit(1)
print("VERIFY OK - REPORT_WS11.md verifies verbatim against "
      "results_ws11.json, and every structural invariant holds.")
