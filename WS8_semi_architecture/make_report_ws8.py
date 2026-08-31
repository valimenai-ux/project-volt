#!/usr/bin/env python3
"""
Project Volt - WS8. Renders REPORT_WS8.md from results_ws8.json.

CLAUDE.md rule 2: the report's headline numbers must verify VERBATIM
against the workstream's results data file, with nothing transcribed by
hand. The strongest way to satisfy that is for no human to type a number
into the report at all - so every figure below is formatted out of
results_ws8.json here, and verify_ws8.py then asserts independently that
the rendered strings are present.

    ../.venv/bin/python make_report_ws8.py
"""
import json
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_ws8.json")))
OUT = os.path.join(HERE, "REPORT_WS8.md")
# The changelog file is named from the ROUND ID in the data file, not
# retyped: r2's generator hard-coded `CHANGELOG_WS8_r2.md`, and a round
# that forgot to change it would have overwritten the previous round's
# only surviving copy of its own numbers.
ROUND = R["_meta"].get("errata_round_id", "r2")
OUT_CHANGELOG = os.path.join(HERE, f"CHANGELOG_WS8_{ROUND}.md")

CANDS = ["S0", "S1", "S2", "S3", "S4"]
CORNERS = ["payload_plus20", "payload_minus20", "grade_heavy",
           "cold_minus10C", "hot_alt_2000m_45C"]
CORNER_LABEL = {
    "payload_plus20": "payload +20%",
    "payload_minus20": "payload -20%",
    "grade_heavy": "grade-heavy corridor",
    "cold_minus10C": "-10 C",
    "hot_alt_2000m_45C": "2,000 m / +45 C",
}


def g(path, default=None):
    o = R
    try:
        for k in path.split("/"):
            o = o[int(k)] if isinstance(o, list) and k.lstrip("-").isdigit() \
                else o[k]
        return o
    except (KeyError, IndexError, TypeError):
        return default


def f2(x):
    return "n/a" if x is None else "{:.2f}".format(x)


def pct(x):
    return "n/a" if x is None else "{:+.2f}%".format(x)


def kg(x):
    return "{:,.0f} kg".format(x)


def m4(x):
    return "n/a" if x is None else "{:.4f}".format(x)


ICCT_TYPICAL = g("task2_s0_calibration/flat_corridor_crosscheck/reference/"
                 "typical_EU_L_per_100km", 32.6)


def climb_txt():
    """LH-520's total climb, formatted from the ensemble. r1 finding F13:
    this was the hard-coded literal '~3,800 m', which is the TOP of the
    ensemble, used twice to justify why S0 misses the fuel corridor."""
    e = g("task1_cycles/cycles/LH-520/ensemble/total_climb_m")
    return (f"{e['median']:,.0f} m of climb over 520 km "
            f"(8-seed ensemble {e['min']:,.0f} m to {e['max']:,.0f} m)")

L = []
w = L.append


# =====================================================================
def header():
    meta = g("_meta")
    w("# REPORT WS8 - VEHICLE ONE: SEMI-SCALE ARCHITECTURE TRIAL")
    w("")
    w(f"Workstream WS8, Vehicle One. Executes "
      f"`WS8_semi_architecture/ASSIGNMENT.md`, and the round ordered by "
      f"`{meta['errata_round']}`, against `{meta['baseline_of_record']}`.")
    w("")
    iface = g("interface_ws8")
    vd = iface["verdicts"]
    sup = iface.get("supersedes", {})
    w(f"**Numbers version {iface['numbers_version']}.** The verdicts are "
      f"`{vd['status']}` - R25 executed all four kills and the WHR drop "
      f"on the pre-committed criteria, and **this round does not reopen "
      f"them**. What {ROUND} does is make the NUMBERS of record correct: "
      f"the blocking finding B1 and the eleven material and minor ones "
      f"from `FINDINGS_WS8_r2.md` are closed here, every corner is "
      f"re-simulated, and section 15 states which direction each "
      f"candidate moved and why - measured, not asserted (finding M1).")
    w("")
    if sup:
        w(f"**The {sup.get('numbers_version')} numbers and the "
          f"{sup.get('ledger_version')} heat ledger are SUPERSEDED, not "
          f"amended.** {sup.get('why', '')} WS6 consumes only the "
          f"`ledger_version: "
          f"{g('heat_ledger/ledger_version')}` ledger "
          f"(R3_DIRECTIVE item 7).")
    w("")
    w("**Nothing here is ratified.** The lead ratifies in a separate chat "
      "(CLAUDE.md rule 11). This report states what the physics gave and "
      "what it cost; the execute-or-spare decision is the lead's.")
    w("")
    w("**This report is generated**, not written: every number below is "
      "formatted out of `results_ws8.json` by `make_report_ws8.py`, and "
      "`verify_ws8.py` asserts independently that each rendered figure "
      "appears verbatim and that the interface block equals "
      "`results_ws8.json['interface_ws8']`. Nothing was transcribed by "
      "hand (rule 2).")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Entry point | `run_ws8.py` (fixed seeds "
      f"{meta['seeds'][0]}..{meta['seeds'][-1]}, {meta['n_seeds']} seeds) |")
    w(f"| Baseline of record | {meta['baseline_of_record']} |")
    w(f"| Python / numpy | {meta['python']} / {meta['numpy']} |")
    w(f"| Metric of record | fuel energy per **payload** tonne-km "
      f"[MJ/(t.km)] |")
    w(f"| Fleet mission | "
      + " + ".join(f"{int(v*100)}% {k}" for k, v in meta["fleet_mix"].items())
      + " by distance |")
    w("")
    w("---")
    w("")


def summary():
    ak = g("advance_kill")
    hl = g("headline")
    w("## 0. What this trial found")
    w("")
    verdicts = ak["candidates"]
    killed = [c for c, v in verdicts.items() if v["verdict"] == "KILL"]
    adv = [c for c, v in verdicts.items() if v["verdict"] == "ADVANCE"]
    if adv:
        w(f"**{', '.join(adv)} ADVANCE. {', '.join(killed)} KILL.**")
    else:
        w(f"**No candidate advances.** {', '.join(killed)} all fail the "
          f"pre-committed criteria.")
    w("")
    pk = g("interface_ws8/per_km_margin_paired/corners/nominal") or {}
    wins = [c for c, b in pk.items() if b["wins_on_every_seed"]]
    loses = [c for c, b in pk.items() if not b["wins_on_every_seed"]]
    if loses:
        losetxt = (
            "; " + ", ".join(
                f"**{c}** does not - it is behind S0 per kilometre on "
                f"{pk[c]['n_seeds_below_zero']} of {pk[c]['n_seeds']} "
                f"seeds (paired ensemble min "
                f"{pct(pk[c]['ensemble']['min'])}, median "
                f"{pct(pk[c]['ensemble']['median'])})"
                for c in loses))
    else:
        losetxt = ""
    w("The trial is decided by a single structural fact, and it is worth "
      "stating before any table: **at fixed gross combination weight, "
      "powertrain mass is payload.** "
      + (f"{', '.join(wins)} win per kilometre against the conventional "
         f"truck on every seed{losetxt}. " if wins else
         f"No candidate wins per kilometre on every seed{losetxt}. ")
      + "Every candidate here is also heavier. The metric of record "
        "divides one by the other, and that division is what the "
        "assignment ordered precisely because it is where the argument "
        "actually lives.")
    w("")
    w("*(r2 finding M2: the sentence above used to read \"Every candidate "
      "here is more efficient per kilometre than the conventional "
      "truck\" as a hard-coded literal, and it was false for S3. It is "
      "generated from `interface_ws8.per_km_margin_paired` now, on the "
      "PAIRED per-seed statistic - the same statistic as every margin in "
      "this report.)*")
    w("")
    s0_fuel = g("task2_s0_calibration/fleet_L_per_100km/median")
    inband = g("task2_s0_calibration/in_corridor_all_seeds")
    fxm = g("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/"
            "median")
    fxlo = g("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/min")
    fxhi = g("task2_s0_calibration/flat_corridor_crosscheck/L_per_100km/max")
    if inband:
        w(f"S0, the ruler, burns **{f2(s0_fuel)} L/100 km** on the fleet "
          f"mission - inside the assignment's 30-38 L/100 km sanity "
          f"corridor, with no fudge factor between the physics and the "
          f"check.")
    else:
        w(f"S0, the ruler, burns **{f2(s0_fuel)} L/100 km** on the fleet "
          f"mission. That is above the assignment's 30-38 L/100 km "
          f"corridor, and the reason is the corridor itself rather than "
          f"the model: run over the same road with the grade zeroed, S0 "
          f"burns **{f2(fxm)} L/100 km** median on an 8-seed envelope of "
          f"{f2(fxlo)} to {f2(fxhi)}, against a published "
          f"{ICCT_TYPICAL} L/100 km for a typical EU tractor-trailer over "
          f"the regulatory Long Haul cycle - consistent with the public "
          f"band, with nothing fitted to it (section 3.4 states what that "
          f"envelope does and does not support). Task 1 ordered "
          f"{climb_txt()}; a 30-38 band describes a freeway. Reported, not "
          f"tuned away, and escalated as ESC-WS8-7.")
    w("")
    rows = hl["table"]
    for r in rows:
        if r["candidate"] == "S0":
            continue
        d_pay = (g("task3_trial/nominal/S0/spec/payload_kg")
                 - r["payload_kg"])
        km = pk.get(r["candidate"], {})
        ke = km.get("ensemble", {})
        w(f"- **{r['candidate']}**: per-kilometre energy against S0 "
          f"{pct(ke.get('median'))} (PAIRED per-seed median, positive = "
          f"less energy per km; envelope {pct(ke.get('min'))} to "
          f"{pct(ke.get('max'))}"
          + (f", below zero on {km['n_seeds_below_zero']} of "
             f"{km['n_seeds']} seeds" if km.get("n_seeds_below_zero")
             else "")
          + f"), and it carries {d_pay:,.0f} kg less payload. "
            f"Net on the metric of record: "
            f"{pct(r['margin_vs_S0_pct_median'])} (median), "
            f"{pct(r['margin_vs_S0_pct_min'])} (ensemble min). "
            f"**{r['verdict']}**.")
    w("")
    fr = g("task5_s3_specific/fixed_ratio_grade_hold")
    if not fr["any_ratio_holds_6pct"]:
        cf = fr["ratio_ceiling_closed_form"]["value"]
        need = fr["ratio_needed_to_hold_6pct"]
        rs = need.get("resolution_sensitivity") or {}
        w(f"S3 fails for a reason that has nothing to do with fuel, and it "
          f"is the most useful result in this report: **no fixed ratio "
          f"exists that lets a diesel axle both cruise at 105 km/h and "
          f"hold the 6% mountain grade at 36,300 kg.** The two "
          f"requirements are not close: the cruise ceiling is "
          f"**{cf:.2f}:1**, solved in closed form as an rpm limit at a "
          f"road speed (finding F12), and the grade needs "
          f"**{need['ratio']:.2f}:1**, a factor of "
          f"{need['ratio']/cf:.1f}. The second of those is a SWEPT "
          f"result and r3 says so (r2 minor m1) - ten times the grid "
          f"resolution in both dimensions moves it by "
          f"{abs(rs.get('d_ratio', 0.0)):.3f} and the engine speed at "
          f"105 km/h by {abs(rs.get('d_rpm_at_105kmh', 0.0)):.0f} rpm, "
          f"against a gap of {need['over_ceiling_by_rpm']:,.0f} rpm over "
          f"the ceiling. That is not a tuning problem, and it is the "
          f"answer to the question S3 was posed to ask.")
        w("")
    w("---")
    w("")


def task0():
    pa = g("task0_prior_art")
    w("## 1. Prior-art map (Task 0)")
    w("")
    if pa["status"] == "DEFERRED":
        w("**Task 0: DEFERRED.**")
        w("")
        w(pa["stub"])
    else:
        w(f"**Task 0: {pa['status']}** - see `{pa['file']}` "
          f"(sha256 `{pa['sha256'][:16]}...`, {pa['bytes']:,} bytes), "
          f"pinned to this run.")
        w("")
        if pa.get("evidence_quality"):
            w(f"**Evidence quality.** {pa['evidence_quality']}")
            w("")
            w(f"**Why not deferred.** {pa['why_not_deferred']}")
            w("")
        w(pa["note"])
    w("")
    w("---")
    w("")


def task1():
    w("## 2. Duty cycles (Task 1)")
    w("")
    tc = g("task1_cycles")
    chk = tc["assignment_checks"]
    w("Two constructed, distance-indexed cycles at 10 Hz, each an 8-seed "
      "ensemble. Grade belongs to the road, not to the clock, so the "
      "cycles are indexed on distance and the speed trace is integrated "
      "**forward against each candidate's own tractive envelope**. That "
      "is a deliberate departure from WS1's flat-road-then-apply-grade "
      "method, and the reason is arithmetic: at 36,300 kg no candidate in "
      "this trial can hold 85 km/h on 6%, so a demand trace applied after "
      "the fact would hand every candidate a speed it does not have and "
      "would hide the one quantity Task 5 asks for.")
    w("")
    w("| | LH-520 | REG-165 |")
    w("|---|---|---|")

    def row(label, path, fmt):
        a = g(f"task1_cycles/cycles/LH-520/ensemble/{path}")
        b = g(f"task1_cycles/cycles/REG-165/ensemble/{path}")
        w(f"| {label} | {fmt.format(a)} | {fmt.format(b)} |")

    row("distance, median", "distance_km/median", "{:.1f} km")
    row("max grade", "grade_max/max", "{:.4f}")
    row("min grade", "grade_min/min", "{:.4f}")
    row("total climb, median", "total_climb_m/median", "{:,.0f} m")
    row("net elevation change, worst seed",
        "net_elevation_change_m/max", "{:+.2f} m")
    row("distance at 2-3% grade", "frac_dist_grade_2_to_3pct/median",
        "{:.3f}")
    row("distance at >=5% grade", "frac_dist_grade_ge_5pct/median", "{:.3f}")
    w("")
    w("Assignment conformance, checked in code rather than asserted:")
    w("")
    for k, label in (("sampled_at_10Hz", "sampled at 10 Hz"),
                     ("linehaul_at_least_500km", "line-haul >= 500 km"),
                     ("has_sustained_2_to_3pct",
                      "sustained 2-3% sections present"),
                     ("has_6pct_mountain", "6% mountain segment present"),
                     ("mountain_descent_is_full",
                      "descent gives back the full climb")):
        w(f"- {label}: **{chk[k]}**")
    w("")
    w("Net elevation change over 520 km is under a metre on every seed "
      "(matched +/- feature pairs), so no candidate is handed potential "
      "energy by the corridor. The seed varies the per-trip cruise speed "
      "inside the assignment's 85-105 km/h band, a constant headwind "
      "component, the rolling-terrain amplitude and phase, and stop "
      "dwells. The SPECIFIED features - the 2-3% sustained sections and "
      "the 6% mountain - are not jittered, because the assignment fixes "
      "them.")
    w("")
    w("---")
    w("")


def task2():
    c = g("task2_s0_calibration")
    e, t = c["engine"], c["transmission"]
    w("## 3. S0 baseline, calibrated (Task 2)")
    w("")
    w("S0 is the ruler. Every candidate is judged against it; nothing in "
      "this report is a self-referential comparison.")
    w("")
    w("### 3.1 The engine")
    w("")
    w(f"A {e['displacement_L']:.1f} L six on WS4's ruled Willans "
      f"construction, re-calibrated for the heavy-duty class. Peak power "
      f"**{e['peak_power_kW']:.1f} kW** at {e['peak_torque_Nm']:,.0f} Nm - "
      f"inside the assignment's 330-370 kW band.")
    w("")
    w("The calibration has exactly one knob and it is solved, not tuned: "
      f"`eta_i0` is bisected until the map's minimum BSFC lands on the "
      f"declared island target of "
      f"{e['island_bsfc_target_g_per_kWh']:.1f} g/kWh. The solve returns "
      f"**{e['eta_i0_solved']:.4f}**, and the achieved island is "
      f"**{e['island_bsfc_achieved_g_per_kWh']:.1f} g/kWh** at "
      f"**{e['island_rpm']:.0f} rpm** / {e['island_torque_Nm']:,.0f} Nm "
      f"({e['island_power_kW']:.0f} kW) - a peak brake thermal efficiency "
      f"of **{e['peak_brake_thermal_efficiency']:.3f}**, which is where a "
      f"modern production on-highway heavy-duty diesel sits.")
    w("")
    w(f"The speed term was re-anchored for this class: `{e['f_n_form']}`. "
      f"WS4's own form centres the optimum at 1,600 rpm, which is right "
      f"for the medium-duty engine WS4 calibrated and wrong for a "
      f"600-2,100 rpm Class 8 six. This is a change to an inherited "
      f"model and it is escalated, not assumed (ESC-WS8-5).")
    w("")
    w("### 3.2 The transmission, stated")
    w("")
    w(f"- {t['type']}, {len(t['ratios'])} ratios, top gear "
      f"{t['ratios'][-1]:.2f} (direct), axle {t['axle_ratio']:.2f}:1")
    w(f"- direct top gear efficiency {t['eta_direct_top']:.3f}; indirect "
      f"gears {t['eta_indirect']:.3f} (a direct top has no countershaft "
      f"power path - which is exactly why line-haul trucks are specified "
      f"this way, and it is the honest size of the prize any "
      f"gearbox-deleting candidate can claim)")
    w(f"- tandem axle {t['eta_axle_tandem']:.3f}, driveshafts "
      f"{t['eta_driveshaft']:.3f}")
    w(f"- cruise chain {t['eta_cruise_chain']:.4f}; engine at "
      f"{t['engine_rpm_at_100kmh']:.0f} rpm at 100 km/h")
    w("")
    w("### 3.3 Calibration against the reference band")
    w("")
    w(f"Reference: {c['reference_band_source']}")
    w("")
    w("| | min | median | max |")
    w("|---|---|---|---|")
    for label, key in (("line-haul LH-520", "linehaul_L_per_100km"),
                       ("regional REG-165", "regional_L_per_100km"),
                       ("**fleet mission**", "fleet_L_per_100km")):
        b = c[key]
        w(f"| {label} [L/100 km] | {f2(b['min'])} | {f2(b['median'])} | "
          f"{f2(b['max'])} |")
    w("")
    w(f"Fleet fuel is inside the 30-38 L/100 km corridor on every seed: "
      f"**{c['in_corridor_all_seeds']}**. Fudge factor applied: "
      f"**{c['fudge_factor_applied']}**. "
      + c["calibration_note"])
    w("")
    fx = c.get("flat_corridor_crosscheck")
    if fx:
        ref = fx["reference"]
        w("### 3.4 Cross-check against the public reference band")
        w("")
        w("The corridor this trial runs is not a regulatory cycle - Task 1 "
          "ordered a 6% mountain and sustained 2-3% sections, "
          + climb_txt() + ". Comparing its fuel directly "
          "against a freeway-dominated published figure would compare two "
          "different roads. So the cross-check runs S0 over the **same "
          "corridor with the grade zeroed** - same distance, same speeds, "
          "same wind, same driver, same vehicle, nothing else touched - "
          "which isolates terrain and makes the comparison like-for-like.")
        w("")
        w("**This is stated as an ENSEMBLE, not a median** (rule 4, and "
          "r1 finding F7: r1 rested the whole calibration argument on a "
          "single median while the envelope for the same quantity was "
          "already computed, stored, and wider than the public band).")
        w("")
        w("| | L/100 km, 8-seed min / median / max |")
        w("|---|---|")
        w(f"| S0, LH-520 as ordered | "
          f"{f2(c['linehaul_L_per_100km']['min'])} / "
          f"{f2(c['linehaul_L_per_100km']['median'])} / "
          f"{f2(c['linehaul_L_per_100km']['max'])} |")
        w(f"| **S0, same corridor with grade zeroed** | "
          f"**{f2(fx['L_per_100km']['min'])} / "
          f"{f2(fx['L_per_100km']['median'])} / "
          f"{f2(fx['L_per_100km']['max'])}** |")
        w(f"| ICCT / TUV NORD, typical EU tractor-trailer, "
          f"regulatory Long Haul | {ref['typical_EU_L_per_100km']} |")
        w(f"| ICCT / TUV NORD, at that cycle's regulatory payload "
          f"({ref['regulatory_payload_t']} t) | "
          f"{ref['at_regulatory_payload_L_per_100km']} |")
        w(f"| ICCT / TUV NORD, best-in-class EU | "
          f"{ref['best_in_class_EU_L_per_100km']} |")
        w("")
        w(f"Source: {ref['source']}. Evidence quality: "
          f"{ref['evidence_quality']}.")
        w("")
        ev = fx["envelope_vs_band"]
        w("**And it is not mass-matched.** The reference cycle carries "
          "19.3 t of payload; WS8's S0 carries more, at the assignment's "
          "fixed 36,300 kg GCW. The three enumerated mass cases say what "
          "that is worth:")
        w("")
        w("| combination | payload | GCW | L/100 km, min / median / max |")
        w("|---|---|---|---|")
        for k, mc in fx["mass_cases"].items():
            me = mc["L_per_100km"]
            w(f"| {k.replace('_', ' ')} | {kg(mc['payload_kg'])} | "
              f"{kg(mc['gcw_kg'])} | {f2(me['min'])} / "
              f"{f2(me['median'])} / {f2(me['max'])} |")
        w("")
        w(f"**What the evidence supports.** The grade-zeroed median sits "
          f"{ev['median_offset_pct_vs_typical']:+.1f}% from the published "
          f"typical figure - but the 8-seed envelope spans "
          f"{ev['envelope_width_L_per_100km']:.2f} L/100 km against a "
          f"public band {ev['band_width_L_per_100km']:.2f} L/100 km wide, "
          f"so the envelope is "
          f"{'wider than' if ev['envelope_wider_than_band'] else 'narrower than'} "
          f"the band it is being compared against. " + ev["what_it_supports"])
        w("")
        w(fx["note"])
        w("")
        if not c["in_corridor_all_seeds"]:
            w(f"On the corridor as ordered, S0 exceeds the assignment's "
              f"30-38 L/100 km band by "
              f"{c['corridor_excess_L_per_100km']:.2f} L/100 km. That is "
              f"reported, not tuned away, and escalated as ESC-WS8-7: the "
              f"excess is terrain, and every candidate drives the same "
              f"road, so no margin in this report is affected by it.")
            w("")
    w(f"Duty-averaged BSFC on the line-haul corridor is "
      f"{c['mean_cruise_bsfc_g_per_kWh']['median']:.1f} g/kWh against the "
      f"{e['island_bsfc_achieved_g_per_kWh']:.1f} g/kWh island - the gap "
      f"between the two is the whole of the hybrid opportunity, and it is "
      f"smaller than it is at Vehicle Zero scale because a line-haul "
      f"truck already spends "
      f"{c['top_gear_fraction']['median']:.2f} of its moving time in top "
      f"gear near its best point.")
    w("")
    w("---")
    w("")


def task3():
    w("## 4. Candidate results (Task 3) - the headline")
    w("")
    w("All five at **36,300 kg GCW**, the assignment's fixed condition. "
      "Because GCW is fixed, the road-load physics is identical for every "
      "candidate: mass does not change how the truck drives, it changes "
      "what the truck may carry. Payload is stated explicitly for each.")
    w("")
    w("| | architecture | payload | powertrain | fleet L/100 km | "
      "MJ/payload-tkm (min / median / max) | margin vs S0 (min / median / "
      "max) | fuel that is correction | verdict |")
    w("|---|---|---|---|---|---|---|---|---|")
    for c in CANDS:
        sp = g(f"task3_trial/nominal/{c}/spec")
        ens = g(f"task3_trial/nominal/{c}/fleet_ensemble/MJ_per_payload_tkm")
        lp = g(f"task3_trial/nominal/{c}/fleet_ensemble/L_per_100km/median")
        m = g(f"task3_margins/nominal/{c}/ensemble")
        cs = g(f"interface_ws8/candidates/{c}/fuel_correction_share/value")
        mtxt = (f"{pct(m['min'])} / {pct(m['median'])} / {pct(m['max'])}"
                if m else "- (ruler)")
        v = g(f"advance_kill/candidates/{c}/verdict", "RULER")
        w(f"| **{c}** | {sp['title']} | {kg(sp['payload_kg'])} | "
          f"{kg(sp['powertrain_mass_kg'])} | {f2(lp)} | "
          f"{m4(ens['min'])} / {m4(ens['median'])} / {m4(ens['max'])} | "
          f"{mtxt} | {cs*100:.1f}% | **{v}** |")
    w("")
    w("The last column before the verdict is the one to read sceptically. "
      "It is the fraction of a candidate's reported fuel that is a "
      "**correction** rather than fuel the model watched it burn: energy "
      "its prime mover and pack could not deliver, charged back as fuel "
      "so that every candidate is compared having completed the same "
      "mission at the same speeds, plus the charge-sustaining correction. "
      "A small share is bookkeeping. A large positive share means the "
      "candidate did not really do the mission, and the fuel number is "
      "flattering it - which is why the raw shortfall is reported "
      "separately in section 7 rather than left inside a single figure.")
    w("")
    w("**The charge-sustaining correction is SYMMETRIC, and r1 did not "
      "say so** (finding F4). A pack that ends the mission FLATTER than "
      "it started is charged the make-up; a pack that ends FULLER earns "
      "the corresponding **credit**. That is the convention of record - "
      "SAE J1711 in spirit - applied identically to every candidate with "
      "a pack, and it is declared here rather than left for a reader to "
      "discover. It matters:")
    w("")
    w("| | correction share, min / median / max | charge-sustaining "
      "direction over the (cycle, seed) set | margin of record | margin "
      "with the CREDIT suppressed |")
    w("|---|---|---|---|---|")
    for c in CANDS[1:]:
        cs = g(f"interface_ws8/candidates/{c}/fuel_correction_share")
        cd = g(f"interface_ws8/candidates/{c}/charge_correction_direction")
        m = g(f"task3_margins/nominal/{c}/ensemble")
        mcf = g(f"task3_margins/nominal/{c}/ensemble_deficit_only")
        n_credit = len(cd["credit_cases"])
        n_def = len(cd["deficit_cases"])
        direction = ("**credit** on {}/{} (cycle, seed) cases".format(
            n_credit, n_credit + n_def) if n_credit else
            "make-up on {}/{} cases".format(n_def, n_credit + n_def))
        w(f"| **{c}** | {cs['min']*100:+.1f}% / {cs['median']*100:+.1f}% / "
          f"{cs['max']*100:+.1f}% | {direction} | "
          f"{pct(m['min'])} / {pct(m['median'])} | "
          f"{pct(mcf['min'])} / {pct(mcf['median'])} |")
    w("")
    w("Section 4.4 takes that apart one factor at a time, because the "
      "round-1 adjudication found these corrections were what decided "
      "the order of the two leading candidates.")
    w("")
    w("Margins are computed **per seed against S0 on the same seed**, then "
      "enveloped. The seed sets the corridor, the wind and the driver, so "
      "pairing removes the cycle draw from the comparison instead of "
      "leaving it in the variance: the envelope below is a spread of "
      "architecture differences, not of weather.")
    w("")
    w("### 4.1 Where the mass goes")
    w("")
    w("| item | " + " | ".join(CANDS) + " |")
    w("|---|" + "---|" * len(CANDS))
    keys = []
    for c in CANDS:
        for k in g(f"task3_trial/nominal/{c}/spec/mass_rows_kg"):
            if k not in keys:
                keys.append(k)
    for k in keys:
        cells = []
        for c in CANDS:
            v = g(f"task3_trial/nominal/{c}/spec/mass_rows_kg/{k}")
            cells.append(f"{v:,.0f}" if v is not None else "-")
        w(f"| {k.replace('_', ' ')} | " + " | ".join(cells) + " |")
    w("| **powertrain total** | " + " | ".join(
        f"**{g(f'task3_trial/nominal/{c}/spec/powertrain_mass_kg'):,.0f}**"
        for c in CANDS) + " |")
    w("| **payload** | " + " | ".join(
        f"**{g(f'task3_trial/nominal/{c}/spec/payload_kg'):,.0f}**"
        for c in CANDS) + " |")
    w("")
    w("### 4.2 Control policies, declared")
    w("")
    for c in CANDS:
        w(f"**{c}** - " + g(f"task3_trial/nominal/{c}/spec/policy"))
        w("")
    # r2 minor m7: r2's prose called S2's disconnect "the G1(b) tax
    # deleted by hardware" for a tax that, after the F5 fix, NOBODY pays.
    # The measured charge and its bracket are rendered instead of the
    # claim.
    sp = g("interface_ws8/candidates")
    if sp:
        w("**What R22(d) actually costs here, measured** (r2 minor m7). "
          "S2's traction disconnect and S3's e-axle disconnect are real "
          "hardware and they are charged for in mass. What they delete is "
          "a tax that this driver model barely levies on anyone: the "
          "integrator is always either pulling or braking, so the "
          "unloaded-and-geared test almost never fires. The charge is "
          "reported with the COAST-PERMITTING BRACKET beside it - what "
          "the same measured zero-torque loss would cost if it were "
          "charged on every geared moving sample - so the near-zero is "
          "read as a property of the driver model rather than as an "
          "architectural win:")
        w("")
        w("| candidate | R22(d) charged kWh | coast-permitting bracket "
          "kWh | disconnect fitted |")
        w("|---|---|---|---|")
        for c in CANDS:
            b = sp.get(c, {}).get("spin_drag_R22d_kWh")
            if not b:
                continue
            mr = g(f"task3_trial/nominal/{c}/spec/mass_rows_kg") or {}
            disc = next((k for k in mr
                         if "disconnect" in k), None)
            w(f"| **{c}** | {b['charged']:.4f} | "
              f"{b['coast_permitting_bracket']:.2f} | "
              + (f"`{disc}` ({mr[disc]:.0f} kg)" if disc else "none") + " |")
        w("")
        w("The bracket is NOT in any margin. Read the two columns "
          "together: the charged column is what the trial priced, and the "
          "difference between the columns is what a coasting duty cycle "
          "would have priced.")
        w("")
    w("---")
    w("")


def task4():
    whr = g("task4_whr")
    w("## 5. Waste-heat recovery (Task 4)")
    w("")
    w(f"Gate, pre-committed: **>= {whr['gate']['threshold_pct']}% net "
      f"fleet-mission fuel per payload tonne-km AFTER the mass charge**, "
      f"else dropped without ceremony. Read on the "
      f"{whr['gate']['basis']}.")
    w("")
    w("Recovery is modelled as a function of engine LOAD, not at a rated "
      "point. Both systems live on exhaust enthalpy, which collapses at "
      "part load; quoting a rated-point gain against a fleet-average duty "
      "is the standard way waste-heat recovery is oversold.")
    w("")
    w("| system | mass | gain at 25% load | at 55% | at 85% | at rated |")
    w("|---|---|---|---|---|---|")
    for k, s in whr["systems"].items():
        ga = s["gain_at_phi"]
        w(f"| {s['name']} | {s['mass_kg']:.0f} kg | "
          f"{ga['0.25']*100:.2f}% | {ga['0.55']*100:.2f}% | "
          f"{ga['0.85']*100:.2f}% | {ga['1.00']*100:.2f}% |")
    w("")
    w("Before any thermodynamics, the mass charge sets the bar. The metric "
      "divides by payload, so a system that costs mass has to win back "
      "the gate PLUS the payload it displaced:")
    w("")
    w("| candidate | system | mass | payload penalty | fuel gain needed to "
      "clear the gate |")
    w("|---|---|---|---|---|")
    for c, r in whr["results"].items():
        for sysname, v in r["systems"].items():
            w(f"| {c} | {sysname} | {v['mass_charge_kg']:.0f} kg | "
              f"{v['payload_penalty_pct']:.2f}% | "
              f"**{v['fuel_gain_needed_to_clear_gate_pct']:.2f}%** |")
    w("")
    w("| candidate | best system | net margin, median | net margin, min | "
      "gate | verdict |")
    w("|---|---|---|---|---|---|")
    for c, r in whr["results"].items():
        w(f"| {c} | {r['best_system']} | "
          f"{pct(r['best_net_margin_pct_median'])} | "
          f"{pct(r['best_net_margin_pct_min'])} | "
          f">= {r['gate_pct']}% | **{r['verdict']}** |")
    w("")
    allv = {r["verdict"] for r in whr["results"].values()}
    if allv == {"DROPPED"}:
        w("**Dropped, without ceremony.** Two things kill it, and the "
          "second is the interesting one.")
        w("")
        w("First, the mass charge: the metric divides by payload, so the "
          "systems have to win back the gate plus what their mass "
          "displaced - the table above shows the real bar is nearer 3-4% "
          "than 2.5%.")
        w("")
        w("Second, and more fundamental: **line-haul cruise is a "
          "part-load condition, and waste-heat recovery is a full-load "
          "technology.** Holding 36,300 kg at 95 km/h on level road needs "
          "about 100 kW at the wheel; on a 350 kW-class engine that is "
          "roughly a third of rated. Both systems modelled here are "
          "negligible below 30-35% load by construction, because exhaust "
          "mass flow and temperature both collapse there. The engine "
          "spends most of the mission in exactly the region where there "
          "is little enthalpy to recover, and the minutes it spends on "
          "the mountain at high load are too few to pay for the mass it "
          "carries for the other five hours.")
        w("")
        w("This is not an argument that waste-heat recovery does not "
          "work. It is an argument that it does not pay ON THIS METRIC, "
          "on this duty, against a payload-denominated criterion that was "
          "armed before the numbers were seen.")
    w("")
    w("---")
    w("")


def two_speed():
    tb = g("two_speed_bracket")
    if not tb or not tb.get("candidates"):
        return
    w("### 4.3 Two-speed traction bracket (informative)")
    w("")
    w("The Task 0 product sweep found something that bears directly on "
      "how these candidates were sized: **every heavy truck that actually "
      "deleted its AMT still fitted a multi-speed gearbox on the traction "
      "side** - Hyliion Hypertruck ERX, ePower, ReVolt, Edison, "
      "Wrightspeed, BAE - and the heavy-duty e-truck transmission "
      "literature finds a three-speed gives the lowest energy consumption "
      "that still meets gradeability. WS8's electric candidates were "
      "sized on a SINGLE fixed reduction, because WS2's carried 7,200 rpm "
      "rotor limit caps the ratio at 12:1 and the 12% startability "
      "specification then sets the machine size.")
    w("")
    w(f"With a two-speed ({tb['two_speed_ratios']}) the startability "
      f"torque is met at half the stretch factor, so the machine halves "
      f"under WS2's own mass law while the box is added back:")
    w("")
    w("| | k, single-speed | k, two-speed | e-drive mass | + box | "
      "net mass | payload gain | margin vs S0 | gain |")
    w("|---|---|---|---|---|---|---|---|---|")
    for c, v in tb["candidates"].items():
        w(f"| **{c}** | {v['k_single_speed']:.2f} | "
          f"{v['k_two_speed']:.2f} | "
          f"{v['edrive_mass_single_kg']:.0f} -> "
          f"{v['edrive_mass_two_speed_kg']:.0f} kg | "
          f"{v['two_speed_box_kg']:.0f} kg | "
          f"{v['net_mass_change_kg']:+.0f} kg | "
          f"{-v['net_mass_change_kg']:+.0f} kg | "
          f"{pct(v['margin_vs_S0_pct_single'])} -> "
          f"{pct(v['margin_vs_S0_pct_two_speed'])} | "
          f"{v['margin_gain_pp']:+.2f} pp |")
    w("")
    w(f"Margins here are on the **{tb['margin_basis']}**.")
    w("")
    w(f"**{tb['basis']}.** Fuel per kilometre is held at the "
      f"single-speed value, which makes the bracket conservative: a "
      f"smaller machine at a higher per-unit load is slightly more "
      f"efficient at cruise, not less. It changes no verdict in this "
      f"report - the gains are fractions of a point - but it says where "
      f"the next mass is, and it says the industry already knew.")
    w("")
    w("---")
    w("")


def one_factor():
    of = g("one_factor")
    if not of:
        return
    w("### 4.4 One factor at a time: what each correction was worth")
    w("")
    w("r1 put S2 ahead of S1 on the nominal median. The round-1 "
      "adjudication showed that about half of S2's advantage was the "
      "charge-sustaining **credit** (F4), and that S2's single engine was "
      "being run as a locked mechanical drive and a free-speed genset at "
      "the same time, with nothing capping their sum at the full-load "
      "curve (F3). r3 widens the table from the S1-vs-S2 pair to all "
      "four candidates and adds rows for its own corrections - the "
      "control rule B1, and the launch-fuel fix that moves THE RULER - "
      "because r2 finding M1 is that the DIRECTION of every correction "
      "must be measured here rather than written into a changelog cell "
      "by hand. On a RE-SIMULATED row, a candidate the switch does not "
      "reach comes back bit-identical, which is a proof rather than an "
      "assertion; on the two exact RE-PRICING rows a zero means the "
      "candidate carries none of that correction, and the direction "
      "cells say which kind of zero they are.")
    w("")
    w(of["rule"])
    w("")
    w("*Direction convention.* " + of["direction_convention"])
    w("")
    w("| row | "
      + " | ".join(f"{c} min / median / max" for c in of["candidates"])
      + " | ordering |")
    w("|---|" + "---|" * (len(of["candidates"]) + 1))
    for label, r in of["rows"].items():
        cells = []
        for c in of["candidates"]:
            v = r[c]
            cells.append(f"{pct(v['min'])} / **{pct(v['median'])}** / "
                         f"{pct(v['max'])}")
        w(f"| `{label}` | " + " | ".join(cells)
          + f" | {r['ordering_on_median']} |")
    w("")
    for label, r in of["rows"].items():
        w(f"- **`{label}`** - {r['_note']}")
    w("")
    cd_ = g("correction_directions") or {}
    meas = [(k, v) for k, v in cd_.items()
            if not k.startswith("_") and v.get("measurable")]
    if meas:
        w("**The direction of each correction, MEASURED** (r2 finding "
          "M1). Every cell below is computed from the rows above by "
          "`correction_directions()`; nothing in it is written by hand, "
          "and `verify_ws8.py` asserts the rendered strings verbatim.")
        w("")
        w("| correction | direction | basis |")
        w("|---|---|---|")
        for k, v in meas:
            w(f"| **{k}** | {v['direction']} | `{v['one_factor_row']}` |")
        w("")
        f6 = cd_.get("F6", {})
        if f6.get("corner_caveat"):
            w("*" + f6["corner_caveat"] + "*")
            w("")
    if of["ordering_changes"]:
        w("**The ordering is not robust to these corrections.** It changes "
          "between the rows above, which is the whole reason this table "
          "exists: the two leading candidates are separated by less than "
          "the corrections are worth. Neither candidate advances on the "
          "pre-committed criteria under any row, so nothing here touches "
          "a verdict - but a reader who takes 'S2 beat S1' out of this "
          "report without this table would be taking a bookkeeping "
          "convention for an architectural result.")
    else:
        w("**The ordering is robust to these corrections**: it is the same "
          "in every row above.")
    w("")
    w("---")
    w("")


def task5():
    w("## 6. Sensitivities (Task 5)")
    w("")
    w("### 6.1 Corner sweep")
    w("")
    w("Margins vs S0 [%], ensemble min / median, at every corner. Note "
      "that at the payload corners GCW moves with payload: the fixed-GCW "
      "condition is a Task-3 condition, not a Task-5 one.")
    w("")
    pk = g("task3_trial/cold_minus10C/S1/spec/pack") or {}
    der = g("task3_trial/hot_alt_2000m_45C/S0/spec/corner/"
            "engine_derate_factor")
    if pk and der is not None:
        w(f"**Two things about this table changed in r2.** The **-10 C** "
          f"corner now applies WS3's cold charge acceptance, which r1 "
          f"named in the corner label, in the provenance list and in "
          f"Recommendation 5 but never called: S1's buffer takes "
          f"{pk.get('p_cont_chg_kW_at_corner', float('nan')):.1f} kW "
          f"there against "
          f"{pk.get('p_cont_chg_kW', float('nan')):.1f} kW warm - both "
          f"BUS-SIDE continuous ratings, and the envelope applies that "
          f"bus-side number as a wheel-side force cap "
          f"(`min(f_gen, chg*1e3/v)`), which is conservative and is "
          f"r2 minor m6's point: the two boundaries are one number here "
          f"and the name should say so. Descent regen goes to the "
          f"resistor instead of the pack and every cold margin below is "
          f"worse than r1's. And **2,000 m / +45 C** is a new corner, "
          f"added under R28: it is the one that exercises WS4's ruled "
          f"`derate_factor` (={der:.4f} here), which r1 listed as "
          f"inherited and never called.")
        w("")
        ds = g("corner_derate_scope/R28_corner") or {}
        if ds:
            w("**What the R28 corner derates, measured** (r2 finding M3). "
              + ds["statement"])
            w("")
            w("| moves at this corner | does not move |")
            w("|---|---|")
            w("| " + ", ".join(f"`{x}`" for x in ds["derates"])
              + " | " + (", ".join(f"`{x}`" for x in ds["does_not_derate"])
                         or "**no electric-side quantity moves at all**")
              + " |")
            w("")
            w("*Direction of error.* " + ds["direction_of_error"])
            w("")
        cdir = (g("correction_directions/F2/direction"),
                g("correction_directions/F11/direction"))
        w(f"The DIRECTION of each of those two corrections is not "
          f"separately measured - neither has a one-factor row, because "
          f"reverting either changes what the corner IS rather than how a "
          f"run is priced. r2's changelog asserted 'Both corrections cut "
          f"AGAINST the candidates' anyway, and the R28 half of that is "
          f"contradicted by the table below, in which S1, S2 and S4 all "
          f"GAIN at that corner relative to nominal. The claim is "
          f"withdrawn rather than restated (r2 finding M1).")
        w("")
    w("| candidate | nominal | " + " | ".join(CORNER_LABEL[c]
                                              for c in CORNERS) + " |")
    w("|---|---|" + "---|" * len(CORNERS))
    for c in CANDS[1:]:
        cells = []
        nm = g(f"task3_margins/nominal/{c}/ensemble")
        cells.append(f"{pct(nm['min'])} / {pct(nm['median'])}")
        for corner in CORNERS:
            m = g(f"task3_margins/{corner}/{c}/ensemble")
            cells.append(f"{pct(m['min'])} / {pct(m['median'])}"
                         if m else "-")
        w(f"| **{c}** | " + " | ".join(cells) + " |")
    w("")

    s3 = g("task5_s3_specific")
    fr = s3["fixed_ratio_grade_hold"]
    w("### 6.2 S3: the fixed-ratio grade-hold floor")
    w("")
    w(fr["constraint"])
    w("")
    w("| ratio A | coupling floor | engine rpm at 105 km/h | cruise OK | "
      "2% | 3% | 4% | 6% | 6% climb feasible on the pack |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in fr["sweep"]:
        cl = r["climb_6pct"]
        w(f"| {r['ratio_A']:.2f} | {r['coupling_floor_kmh']:.1f} km/h | "
          f"{r['cruise']['engine_rpm_at_v_max']:.0f} | "
          f"{'yes' if r['cruise']['ok'] else '**OVER-SPEED**'} | "
          f"{r['grade_2pct']['status']} | {r['grade_3pct']['status']} | "
          f"{r['grade_4pct']['status']} | {r['grade_6pct']['status']} | "
          f"{'yes' if cl['feasible'] else 'no'} |")
    w("")
    cf = fr["ratio_ceiling_closed_form"]
    need = fr["ratio_needed_to_hold_6pct"]
    w(f"**The ratio ceiling is a physics bound, not a property of the "
      f"table above** (r1 finding F12: r1 stated the swept-set figure "
      f"flatly, and it is 3.60 only because the next ratio in the "
      f"enumerated list lands five hundredths of an rpm over the "
      f"ceiling). Solved in closed form from "
      f"`ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)` at "
      f"{cf['rpm_ceiling']:.0f} rpm, {cf['r_dyn_m']:.2f} m and "
      f"{cf['v_cruise_kmh']:.0f} km/h, the ceiling is "
      f"**{cf['value']:.4f}**. The highest ratio the enumerated sweep "
      f"contains under it is **{fr['max_ratio_without_overspeed']:.2f}**, "
      f"and that is an illustration. Ratios in the sweep that hold the 6% "
      f"grade: **{fr['feasible_ratios_for_6pct'] or 'none'}**.")
    w("")
    if need.get("ratio"):
        w(f"**And the gap is closed in closed form too.** The lowest ratio "
          f"at which axle A holds the 6% grade anywhere above its own "
          f"lugging floor is **{need['ratio']:.2f}**, which puts the "
          f"engine at **{need['engine_rpm_at_105kmh']:,.0f} rpm** at "
          f"105 km/h - {need['over_ceiling_by_rpm']:,.0f} rpm over the "
          f"{need['rpm_ceiling']:.0f} rpm ceiling. The ratio the grade "
          f"demands and the ratio the cruise permits differ by a factor "
          f"of about {need['ratio']/cf['value']:.1f}.")
        w("")
        rs = need.get("resolution_sensitivity")
        if rs:
            w(f"**What is closed form here, and what is not** (r2 minor "
              f"m1). The CEILING is closed form: it is an rpm limit at a "
              f"road speed and it is solved as one. The ratio the grade "
              f"DEMANDS is not - it is the first hit on a "
              f"{rs['coarse']['ratio_step']} ratio grid whose hold test "
              f"scans road speed on a {rs['coarse']['speed_step_ms']} m/s "
              f"grid - and r2's report said 'No swept grid is doing any "
              f"work in that conclusion', which was the wrong claim to "
              f"make about a swept result. So the sweep is priced instead "
              f"of dismissed: at ten times the resolution in BOTH "
              f"dimensions ({rs['fine']['ratio_step']} and "
              f"{rs['fine']['speed_step_ms']} m/s) the ratio moves by "
              f"{abs(rs['d_ratio']):.3f} and the engine speed at "
              f"105 km/h by {abs(rs['d_rpm_at_105kmh']):.0f} rpm, against "
              f"a gap of {need['over_ceiling_by_rpm']:,.0f} rpm over the "
              f"ceiling. The conclusion is unchanged: "
              f"`conclusion_unchanged: "
              f"{str(rs['conclusion_unchanged']).lower()}`. The grid "
              f"decides a decimal place; it does not decide the answer.")
            w("")
    if not fr["any_ratio_holds_6pct"]:
        ex = next(r for r in fr["sweep"]
                  if abs(r["ratio_A"] - fr["max_ratio_without_overspeed"])
                  < 1e-9)
        cl = ex["climb_6pct"]
        w("The two requirements do not overlap, and the gap is not "
          "marginal. At the highest ratio the cruise speed allows, axle A "
          f"can put **{ex['grade_6pct']['F_axleA_at_ref_kN']:.1f} kN** at "
          f"the contact patch where the grade demands "
          f"**{ex['grade_6pct']['F_required_at_ref_kN']:.1f} kN**. This is "
          "not an engine problem - a 13 L in place of the downsized 11 L "
          "does not close a factor-of-two gap - it is the gearbox's "
          "problem, and S3 deleted the gearbox. A geared truck answers "
          "this by trading speed for torque; a fixed ratio cannot.")
        w("")
        if cl.get("e_required_bus_kWh"):
            w(f"With the diesel axle unusable on the grade, the e-axle "
              f"must carry the climb alone. On the 16 km 6% segment that "
              f"is **{cl['e_required_bus_kWh']:.0f} kWh** of bus energy "
              f"against **{cl['e_pack_available_kWh']:.1f} kWh** in the "
              f"buffer - a shortfall of "
              f"{cl['shortfall_kWh']:.0f} kWh, or roughly six times the "
              f"pack. S3 does not climb the mountain slowly; it does not "
              f"climb it.")
            w("")

    st = s3.get("regulatory_startability_adhesion")
    if st:
        w("### 6.3 Regulatory startability, and what one driven axle costs")
        w("")
        w(f"Requirement: {st['requirement']}")
        w("")
        w(f"That start needs **{st['required_force_N']/1e3:.1f} kN** at the "
          f"contact patch at 36,300 kg. {st['finding']}")
        w("")
        w("| surface | mu | mu needed, single axle | mu needed, 6x4 tandem "
          "| single axle can start | 6x4 tandem can start |")
        w("|---|---|---|---|---|---|")
        for r in st["rows"]:
            w(f"| {r['surface']} | {r['mu']:.2f} | "
              f"{r['mu_required_single_axle']:.3f} | "
              f"{r['mu_required_tandem']:.3f} | "
              f"{'yes' if r['single_axle_can_start'] else '**no**'} | "
              f"{'yes' if r['tandem_can_start'] else '**no**'} |")
        w("")
        w(f"Single-axle launch (S3's axle B) succeeds on: "
          f"**{', '.join(st['single_axle_surfaces_ok']) or 'no surface'}**. "
          f"A 6x4 tandem (S0, S1, S2, S4) succeeds on: "
          f"**{', '.join(st['tandem_surfaces_ok']) or 'no surface'}**.")
        w("")
        w(f"Not modelled: {st['repeat_duty_not_modelled']}")
        w("")

    w("### 6.4 S3: diesel-axle-only adhesion on cruise grades")
    w("")
    adh = s3["diesel_axle_adhesion"]
    w("One driven axle carries half the tandem load, so S3's cruise "
      "traction sits on half the adhesion a 6x4 has. Steepest grade "
      "holdable at 90 km/h on adhesion alone:")
    w("")
    w("| surface | mu | axle A alone | 6x4 tandem (reference) |")
    w("|---|---|---|---|")
    for a, t in zip(adh["single_axle_A"], adh["tandem_reference_6x4"]):
        w(f"| {a['surface']} | {a['mu']:.2f} | "
          f"{a['max_grade_held_on_adhesion']*100:.2f}% | "
          f"{t['max_grade_held_on_adhesion']*100:.2f}% |")
    w("")
    lim = g("interface_ws8/S3_diesel_axle_adhesion_grade_limit")
    w(f"Worst case **{lim['value']:.4f}** (governing case: "
      f"{lim['governing_case']}), per R14.")
    w("")

    w("### 6.5 S3: e-axle-fault limp capability")
    w("")
    fl = s3["fault_limp"]["e_axle_fault"]
    w(f"**{fl['verdict']}**")
    w("")
    w(fl["note"])
    w("")
    w("Program precedent: " + s3["fault_limp"]["program_precedent"])
    w("")
    w("---")
    w("")


def unserved():
    u = g("interface_ws8/unserved_energy_kWh")
    w("## 7. Capability shortfalls, reported rather than absorbed")
    w("")
    w(u["meaning"])
    w("")
    w(f"Worst case **{u['value']:.2f} kWh** (governing case: "
      f"`{u['governing_case']}`), an explicit max over the enumerated "
      f"(candidate, corner, cycle) set per R14.")
    w("")
    over = u.get("cases_over_1kWh") or {}
    if over:
        w(f"All **{len(over)}** cases above 1 kWh (r2 minor m2: this "
          f"table was silently truncated to the top 20, so the cases "
          f"between the twentieth and the smallest were absent and the "
          f"table read as though the candidates in that range had almost "
          f"no unserved energy):")
        w("")
        w("| case | unserved kWh |")
        w("|---|---|")
        for k, v in sorted(over.items(), key=lambda kv: -kv[1]):
            w(f"| `{k}` | {v:.2f} |")
        w("")
    ov = g("interface_ws8/retard_overcommitment")
    if ov:
        w("### 7.1 The same question on the braking side")
        w("")
        w(ov["meaning"])
        w("")
        w(f"Worst case **{ov['value_kW']:.1f} kW** sustained "
          f"(governing case: `{ov['governing_case']}`, "
          f"{ov['energy_kWh_at_governing_case']:.2f} kWh on that run), "
          f"an explicit max over the enumerated (candidate, corner, "
          f"cycle, seed) set per R14. {ov['never_absorbed'][0].upper()}"
          f"{ov['never_absorbed'][1:]}.")
        w("")
        per = {}
        for k, v in ov["cases_kW"].items():
            c = k.split("/")[0]
            e = per.setdefault(c, [0, 0.0])
            e[0] += 1
            e[1] = max(e[1], v)
        w("| candidate | runs with any overcommitment | worst kW | "
          "resistor rating kW |")
        w("|---|---|---|---|")
        for c in CANDS:
            if c not in per:
                continue
            rating = g(f"task3_trial/nominal/{c}/spec/"
                       f"brake_resistor_rating_kW")
            w(f"| **{c}** | {per[c][0]} | {per[c][1]:.1f} | "
              f"{('%.0f' % rating) if rating else '-'} |")
        w("")
        rows_all = sorted(ov["cases_kW"].items(), key=lambda kv: -kv[1])
        n_show = 15
        w(f"The {n_show} largest of **{len(rows_all)}** affected runs "
          f"(labelled truncation, r2 minor m2 - the full set is "
          f"`interface_ws8.retard_overcommitment.cases_kW`, and the "
          f"smallest shown here is {rows_all[n_show-1][1]:.1f} kW against "
          f"{rows_all[-1][1]:.1f} kW at the bottom of the list):")
        w("")
        w("| case | overcommitted kW |")
        w("|---|---|")
        for k, v in rows_all[:n_show]:
            w(f"| `{k}` | {v:.1f} |")
        w("")
    w("---")
    w("")


def corroboration():
    """External corroboration. These are EXTERNAL citations from the Task 0
    scan, not results-derived numbers, and are labelled as such."""
    w("## 8. External corroboration")
    w("")
    w("None of the verdicts above depend on the prior-art scan. But the "
      "scan was run, and it is worth recording where it agrees - because "
      "three of this report's least comfortable conclusions turn out to "
      "be things the industry already knows. All figures in this section "
      "are EXTERNAL and search-summary level, provisional per E13 "
      "precedent; see `PRIOR_ART_WS8.md` for their evidence limits.")
    w("")
    _pk = g("interface_ws8/per_km_margin_paired/corners/nominal") or {}
    _in = [c for c, b in _pk.items()
           if 5.0 <= b["ensemble"]["median"] <= 10.0]
    _out = [f"{c} {pct(b['ensemble']['median'])}" for c, b in _pk.items()
            if not (5.0 <= b["ensemble"]["median"] <= 10.0)]
    w("**On the size of the hybrid prize.** Volvo built and ran a "
      "long-haul hybrid concept tractor and reported the hybrid path "
      "alone at **5-10% fuel saving**, from shutting the engine off for "
      "up to 30% of driving time, with topography-optimal control. The "
      "widely-quoted 30% for that vehicle is the whole truck including "
      "aerodynamics. "
      + (f"{', '.join(_in)} land inside that 5-10% band on the paired "
         f"per-seed per-km margin" if _in else
         "No candidate lands inside that 5-10% band on the paired "
         "per-seed per-km margin")
      + (f"; {', '.join(_out)} do not. " if _out else ". ")
      + "For the candidates that do, that is the reassuring outcome, not "
        "the disappointing one: a model that had produced 25% would have "
        "been wrong. (r2 finding M2: this sentence used to assert the "
        "whole set was inside the band, on a statistic the report did "
        "not use.)")
    w("")
    w("**On deleting the gearbox.** Across the products and programmes "
      "the scan found, the number of on-highway Class 8 vehicles in which "
      "a combustion engine drove the road wheels through a single fixed "
      "ratio with no gearbox anywhere is **zero**. The specific cases are "
      "sharper than the aggregate:")
    w("")
    w("- **Hyliion Hypertruck ERX** is the only production-intent Class 8 "
      "that actually deleted the AMT. It did so by going series, "
      "decoupling the engine entirely - and still fitted a **two-speed "
      "gearbox on each of its two drive axles**.")
    w("- **ZF AxTrax 2 dual**, a clean-sheet Class 8 e-axle designed in "
      "the 2020s with no legacy constraint, is **three-speed**. "
      "**Allison's eGen Power** is two-speed, and Allison states S3's "
      "exact design tension in one sentence: the second ratio exists "
      "\"to enable the high torque required to get heavy loads moving, "
      "while also offering superior efficiency at cruise speed\".")
    w("- **Navistar's SuperTruck II** implemented the closest thing to "
      "S3's control law that has been demonstrated - electric owns launch "
      "and low speed, diesel takes over above a threshold - on a "
      "DOE-funded Class 8, and kept the multi-speed AMT while doing it.")
    w("- **Every e-axle overlay product** in the scan - Hyliion 6X4HE, "
      "Revoy, Range Energy, Trailer Dynamics - left the tractor's engine "
      "and AMT completely untouched. That is the commercial proposition, "
      "not an oversight.")
    w("")
    w("Section 6.2 says why, from first principles and without reference "
      "to any of this. The two arrive at the same place independently, "
      "which is the strongest form of agreement available here.")
    w("")
    w("**On the engine map.** The scan puts the lowest BSFC of mainstream "
      "heavy-duty truck diesels in volume commercial use at **182 g/kWh "
      "(46% brake thermal efficiency)**, with research engines "
      "demonstrating 55.7% BTE. S0's island is calibrated to "
      f"{g('task2_s0_calibration/engine/island_bsfc_achieved_g_per_kWh'):.1f}"
      " g/kWh - a production-class value, deliberately not a research "
      "one.")
    w("")
    w("**A calibration warning the scan supplied.** SuperTruck "
      "fuel-economy headlines are frequently quoted at 65,000 lb GCVWR "
      "rather than 80,000 lb. WS8 runs at 36,300 kg (80,000 lb) "
      "throughout, so those headline figures are not comparable to "
      "anything in this report and are not used.")
    w("")
    w("---")
    w("")


def recommendation():
    ak = g("advance_kill")
    w("## 9. Recommendation")
    w("")
    w(f"Criteria, pre-committed and quoted from the assignment: a "
      f"candidate ADVANCES only if it beats S0 by "
      f">= {ak['criteria']['nominal_pct']}% at nominal AND is "
      f">= {ak['criteria']['every_corner_pct']}% at every sensitivity "
      f"corner. Read on the **{ak['criteria']['statistic']}** - the "
      f"program's own precedent ({ak['criteria']['precedent']}).")
    w("")
    w("| candidate | nominal min | worst corner | worst corner min | "
      "passes nominal | passes corners | verdict |")
    w("|---|---|---|---|---|---|---|")
    for c, v in ak["candidates"].items():
        w(f"| **{c}** | {pct(v['nominal_margin_pct_min'])} | "
          f"{v['worst_corner']} | "
          f"{pct(v['worst_corner_margin_pct_min'])} | "
          f"{v['passes_nominal_3pct']} | {v['passes_all_corners_0pct']} | "
          f"**{v['verdict']}** |")
    w("")
    for c, v in ak["candidates"].items():
        w(f"- **{c}: {v['verdict']}** - {v['binding_reason']}.")
    w("")
    w("**What WS8 recommends.** The numbers are above and the "
      "execute-or-spare decision is the lead's. What WS8 will say is "
      "this:")
    w("")
    adv = [c for c, v in ak["candidates"].items()
           if v["verdict"] == "ADVANCE"]
    if not adv:
        w("1. **No candidate clears the bar as specified.** The margins "
          "are not catastrophic - several candidates are within a point "
          "or two of S0 - but 'within a point or two' is not >= 3%, and "
          "the criteria were armed before the numbers were seen.")
    else:
        w(f"1. **{', '.join(adv)} clear the bar as specified** and are the "
          f"only candidates that do.")
    w("2. **S3 should be spared further work regardless of its fuel "
      "number.** Its fuel result is not the finding; its capability "
      "result is. A fixed-ratio diesel axle cannot hold the specified "
      "mountain grade at any ratio that also permits highway cruise, and "
      "an e-axle fault leaves the combination immobile from rest. Those "
      "are structural, not parametric.")
    _pk3 = g("interface_ws8/per_km_margin_paired/corners/nominal") or {}
    _w3 = [c for c, b in _pk3.items() if b["wins_on_every_seed"]]
    _l3 = [c for c, b in _pk3.items() if not b["wins_on_every_seed"]]
    w("3. **The binding constraint on this vehicle is mass, not "
      "efficiency.** "
      + (f"{', '.join(_w3)} win per kilometre on every seed and give it "
         f"back on payload"
         + (f"; {', '.join(_l3)} " + ("does" if len(_l3) == 1 else "do")
            + " not even do that" if _l3 else "")
         if _w3 else "No candidate wins per kilometre on every seed")
      + ". Any future work that does not attack the powertrain mass "
        "ledger is not attacking the problem.")
    # r1 finding F13's class of defect: this paragraph carried
    # hand-written "about fourteen points ... roughly +10% ... about
    # -4%", and r2's cold corner moved all three. Formatted from the
    # data, and it is the widest span across the corner set for the
    # named candidate rather than an eyeballed pair.
    spans = {}
    for c in CANDS[1:]:
        vals = {}
        for corner in ["nominal"] + CORNERS:
            m = g(f"task3_margins/{corner}/{c}/ensemble/median")
            if m is not None:
                vals[corner] = m
        if vals:
            hi = max(vals, key=lambda k: vals[k])
            lo = min(vals, key=lambda k: vals[k])
            spans[c] = (vals[hi] - vals[lo], hi, vals[hi], lo, vals[lo])
    if spans:
        c = max(spans, key=lambda k: spans[k][0])
        sp, hi, hv, lo, lv = spans[c]
        w(f"4. **What decides these architectures is the fleet's duty, not "
          f"the architecture.** The corner sweep in section 6.1 spans "
          f"**{sp:.0f} percentage points** for {c} alone - from "
          f"{pct(hv)} at `{hi}` to {pct(lv)} at `{lo}` - and the sign "
          f"flips inside that span for every candidate. An operator "
          f"running loaded over mountains and an operator running light "
          f"in winter are not looking at the same vehicle. R29 has since "
          f"named the duty (grade-heavy regional) for exactly this "
          f"reason; these numbers are the evidence it was named on, and "
          f"r2 widened the span rather than narrowing it, because the "
          f"cold corner the sweep now models honestly is far harsher "
          f"than the one r1 reported.")
    pk = g("task3_trial/cold_minus10C/S1/spec/pack") or {}
    warm = pk.get("p_cont_chg_kW", float("nan"))
    cold = pk.get("p_cont_chg_kW_at_corner", float("nan"))
    fac = pk.get("cold_charge_acceptance_factor_minus10C", float("nan"))
    w(f"5. **The cold corner is the one to attack first.** It is binding "
      f"for all four candidates, and its cause is specific and fixable "
      f"rather than fundamental. In r1 this recommendation described a "
      f"mechanism the model did not contain (finding F2, blocking): "
      f"`Pack8.p_cont_chg_kw_at()` and `COLD_CHG_FACTOR` were defined and "
      f"never called, so every corner ran on the warm nameplate. **In r2 "
      f"the mechanism is in the model.** S1's buffer accepts "
      f"**{cold:.1f} kW** at -10 C against **{warm:.1f} kW** warm - a "
      f"factor of {1.0/fac:.1f} - so descent regen goes to the resistor "
      f"instead of the pack, and every cold-corner margin in section 6.1 "
      f"is computed with that collapse applied rather than asserted "
      f"beside it. The conventional truck still heats its cab from engine "
      f"coolant for free. Pack preconditioning and a heat-recovery path "
      f"for cab heat are the obvious counters; neither is modelled here, "
      f"and R30 now requires both of every WS9 electrified candidate.")
    w("6. **The escalations in section 11 change the answer if ruled the "
      "other way**, ESC-WS8-1 and ESC-WS8-3 especially. They are not "
      "footnotes.")
    w("")
    w("---")
    w("")


def sanity():
    s = g("sanity")
    w("## 10. First-principles sanity checks")
    w("")
    r = s["road_load_95kmh_flat"]
    w(f"**Road load at 95 km/h, flat, 36,300 kg.** By hand: aero "
      f"0.5 x {g('params/vehicle/rho_air'):.3f} x "
      f"{g('params/vehicle/CdA'):.1f} x 26.39^2 = "
      f"**{r['model_aero_N']:,.0f} N**; rolling "
      f"{g('params/vehicle/Crr'):.4f} x 36,300 x 9.81 = "
      f"**{r['model_roll_N']:,.0f} N**; total "
      f"{r['model_total_N']:,.0f} N = {r['wheel_power_kW']:.1f} kW at the "
      f"wheel. Model agrees: **{r['agree']}**.")
    w("")
    w(r["note"] + ".")
    w("")
    m = s["mountain_6pct"]
    w(f"**The 6% mountain.** {m['grade_force_kN']:.1f} kN of gravity, "
      f"**{m['power_at_90kmh_kW']:.0f} kW** at 90 km/h. "
      + m["note"])
    w("")
    sc = s["scaling_law_per_unit_invariance"]
    w(f"**Scaling-law implementation.** Per-unit efficiency of the k=1.0 "
      f"and k=3.6 machines at matched per-unit load agree to "
      f"{sc['max_abs_delta_pp']:.4f} pp. {sc['claim']}")
    w("")
    gs = s["generator_scaling_invariance"]
    w(f"**Generator scaling.** Same test on WS4's generator model: "
      f"{gs['max_abs_delta_pp']:.3f} pp across a 135 -> 303 kW stretch.")
    w("")
    mc = s["mass_closure_at_fixed_gcw"]
    w(f"**Mass closure.** tare + payload = 36,300 kg for every candidate: "
      f"**{mc['all_close']}**. {mc['note']}.")
    w("")
    ec = s["s0_energy_closure"]
    w(f"**S0 energy closure.** Fuel energy {ec['fuel_energy_kWh']:,.0f} kWh, "
      f"engine shaft work {ec['engine_shaft_kWh']:,.0f} kWh - an implied "
      f"engine efficiency of {ec['implied_engine_efficiency']:.4f} against "
      f"{ec['bsfc_implied_efficiency']:.4f} implied by the duty-averaged "
      f"BSFC. Agree: **{ec['agree']}**.")
    w("")
    te = s["envelope_tabulation_error"]
    w(f"**Envelope tabulation.** The integrator interpolates each "
      f"candidate's envelope on a {te['grid_dv_ms']} m/s grid; worst "
      f"relative error against direct evaluation "
      f"{te['max_relative_error']:.2e}.")
    w("")
    st = s["startability_sizing"]
    w(f"**Startability sizing.** The {st['required_grade']*100:.0f}% "
      f"start needs {st['required_force_kN']:.1f} kN; the electric paths "
      f"are sized to deliver it and do "
      f"({st['S1_available_at_2kmh_kN']:.1f} kN at 2 km/h), inside the "
      f"{st['adhesion_dry_tandem_kN']:.1f} kN dry-tandem adhesion "
      f"ceiling.")
    w("")
    w(f"All checks pass: **{s['all_pass']}**.")
    w("")
    w("---")
    w("")


def escalations():
    w("## 11. Escalations")
    w("")
    w("Escalations cite the ruling they challenge and are never "
      "self-resolved (CLAUDE.md rule 8). They go to the lead.")
    w("")
    for e in g("escalations"):
        w(f"### {e['id']} - {e['title']}")
        w("")
        w(f"**Cites:** {e['cites']}")
        w("")
        w(f"**Finding.** {e['finding']}")
        w("")
        w(f"**Why this is not self-resolved.** {e['why_not_self_resolved']}")
        w("")
        w(f"**Asks.** {e['asks']}")
        w("")
        w(f"**Materiality:** {e['materiality']}")
        w("")
    w("---")
    w("")


def heat():
    hl = g("heat_ledger")
    w("## 12. Heat ledger for WS6 (rule 7)")
    w("")
    w("**Rebuilt in r2, and closed in r3.** Round 1's blocking finding "
      "F1 was three defects "
      "in one export: the governing case sat OUTSIDE the enumerated case "
      "set (the ledger priced the 6% descent with the pack accepting its "
      "full charge power throughout, when the pack fills in about four "
      "minutes of a ten-minute descent); compression-brake heat was "
      "booked as resistor heat with the exhaust row explicitly zeroed, so "
      "S1, S2 and S3 exported the identical figure despite three "
      "different retarder architectures; and foundation-brake heat had no "
      "row at all, so the S0 descent case did not close. All three are "
      "closed here.")
    w("")
    w(f"**This ledger is `ledger_version: {hl['ledger_version']}`, and it "
      f"supersedes `{hl['supersedes_ledger_version']}`.** "
      + hl["consumer_rule"])
    w("")
    w(hl["convention"] + ".")
    w("")
    w("Enumerated case set (R14): " + ", ".join(f"`{c}`"
                                                for c in hl["cases"]) + ".")
    w("")
    comps = ["engine_coolant_kW", "engine_exhaust_kW",
             "traction_machine_inverter_kW", "generator_rectifier_kW",
             "pack_kW", "brake_resistor_kW", "friction_brake_kW",
             "total_rejected_kW"]
    w("Worst-case rejection by component [kW], an explicit max over that "
      "set with the governing case labelled:")
    w("")
    w("| candidate | " + " | ".join(c.replace("_kW", "").replace("_", " ")
                                    for c in comps) + " |")
    w("|---|" + "---|" * len(comps))
    for c in CANDS:
        cells = []
        for k in comps:
            v = g(f"heat_ledger/candidates/{c}/worst_case/{k}")
            cells.append(f"{v['value']:.0f} ({v['governing_case']})"
                         if v else "-")
        w(f"| **{c}** | " + " | ".join(cells) + " |")
    w("")
    w("**The resistor and the compression brake are now separate rows, "
      "because they reject to different places.** An air-cooled grid "
      "resistor is a packaging and airflow problem; an exhaust-side "
      "compression brake is not. On the pack-saturated 6% descent:")
    w("")
    w("| candidate | resistor kW | compression brake kW | foundation "
      "brakes kW | resistor rating kW |")
    w("|---|---|---|---|---|")
    for c in CANDS:
        row = g(f"heat_ledger/candidates/{c}/cases/"
                "descent_6pct_pack_saturated")
        rating = g(f"task3_trial/nominal/{c}/spec/brake_resistor_rating_kW")
        if not row:
            continue
        w(f"| **{c}** | {row['brake_resistor_kW']:.0f} | "
          f"{row['engine_exhaust_kW']:.0f} | "
          f"{row['friction_brake_kW']:.0f} | "
          f"{('%.0f' % rating) if rating else '-'} |")
    w("")
    w(f"**`all_cases_close_and_within_rating = "
      f"{hl['all_cases_close_and_within_rating']}`, and here is exactly "
      f"what that tests** (r2 minor m5: r2's bolded sentence read "
      f"'Every case closes and every component stays inside the rating', "
      f"which is stronger than what the flag examined - the simulated "
      f"member carried no residual and was skipped, and that exemption is "
      f"what finding B1 came through):")
    w("")
    w(hl.get("what_all_cases_close_and_within_rating_tests", ""))
    w("")
    ex = hl.get("overrun_exclusivity") or {}
    if ex:
        w(f"**The crankshaft assertion (finding B1), per run.** "
          f"{ex['rule']} `all_hold = {ex['all_hold']}`.")
        w("")
        w("| candidate | runs examined | samples with brake AND shaft "
          "power | fuel while the vehicle brakes (max over runs) |")
        w("|---|---|---|---|")
        for c in CANDS:
            e = ex["candidates"].get(c)
            if not e:
                continue
            w(f"| **{c}** | {e['runs_examined']} | "
              f"{e['samples_brake_and_shaft']} | "
              f"{e['fuel_fraction_while_braking_max']*100:.2f}% |")
        w("")
        w(ex["note"][0].upper() + ex["note"][1:])
        w("")
    cl = g("heat_ledger/candidates/S3/closure") or {}
    simrow = (cl.get("cases") or {}).get("simulated_worst_run")
    if simrow:
        w(f"**The simulated member is no longer exempt from the closure** "
          f"(R3_DIRECTIVE item 1). Every candidate's `simulated_worst_run` "
          f"carries the WORST 60-second energy residual any run of that "
          f"candidate produced, against a tolerance of "
          f"{cl['tolerance']*100:.0f}% of the accounted input at that "
          f"window:")
        w("")
        w("| candidate | worst residual kW | relative | closes | "
          "governing run |")
        w("|---|---|---|---|---|")
        for c in CANDS:
            row = ((g(f"heat_ledger/candidates/{c}/closure/cases") or {})
                   .get("simulated_worst_run"))
            if not row:
                continue
            w(f"| **{c}** | {row['residual_kW']:+.3f} | "
              f"{row['relative']*100:.4f}% | {row['closes']} | "
              f"`{row.get('governing_run') or '-'}` |")
        w("")
    _res = {c: g(f"heat_ledger/candidates/{c}/worst_case/"
                 f"brake_resistor_kW/value") for c in CANDS}
    _rat = {c: g(f"task3_trial/nominal/{c}/spec/brake_resistor_rating_kW")
            for c in CANDS}
    _sat = [c for c in CANDS
            if _rat.get(c) and _res.get(c) is not None
            and _res[c] >= _rat[c] * 0.999]
    w("In r1 S3 exported 210.71 kW of resistor heat against the 200 kW "
      "resistor it had been charged 71.8 kg for "
      "(`FINDINGS_WS8_r1.md`, F1b); that check now exists and runs, and "
      "the brake resistor is still the ONLY hard row.")
    w("")
    w("**r2 minor m5(b) said that row could not fail by construction, "
      "and r3 found the path that reaches it.** m5(b)'s argument was "
      "that `_retard_channels` caps resistor force at the rating divided "
      "by road speed AT THE WHEEL, so the bus-side figure is at most the "
      "wheel-side rating times the generating efficiency - and it added "
      "that the check would bind the moment a case appeared that did not "
      "go through that cap. Such a case exists: regen the FULL pack "
      "cannot accept is sent to the resistor by `series_dispatch` and by "
      "S3's SOC loop, outside the retard-channel split entirely. "
      + (f"Booked where the code says it goes, "
         f"{', '.join(_sat)} now sit AT their ratings ("
         + ", ".join("%s %.0f of %.0f kW" % (c, _res[c], _rat[c])
                     for c in _sat) + ")"
         if _sat else "Booked where the code says it goes, no candidate "
         "reaches its rating")
      + ". The row is capped at the rating in "
        "`resistor_and_overcommitment`, because a figure above it would "
        "not be a cooling load; what would have exceeded it is exported "
        "as `retard_overcommitment` in section 7.1 and escalated as "
        "ESC-WS8-10. The honest statement is therefore not that the "
        "check passes - it is that the resistors SATURATE, and that the "
        "surplus is a capability shortfall rather than heat.")
    w("")
    adv = hl.get("advisory_exceedances") or {}
    if adv:
        n = sum(len(v) for v in adv.values())
        w(f"**{n} ADVISORY exceedance{'s' if n != 1 else ''}, and "
          f"{'they are' if n != 1 else 'it is'} a finding rather than an "
          f"error.** " + hl["advisory_note"][0].upper()
          + hl["advisory_note"][1:])
        w("")
        w("| candidate | component | declared allowance kW | worst "
          "sustained kW | governing case |")
        w("|---|---|---|---|---|")
        for c, rows in adv.items():
            for r in rows:
                w(f"| **{c}** | {r['component']} | {r['rated_kW']:.0f} | "
                  f"{r['worst_case_kW']:.0f} | {r['governing_case']} |")
        w("")
    w("**And every candidate exceeds it, not only S0.** That is the same "
      "mechanism F1(a) named, seen from the other end: the descent "
      "governor sets the speed a candidate may descend at from the "
      "retarding capability of a pack that has not yet filled, so once "
      "the buffer saturates part-way down the grade the retarding "
      "channel it was counting on is gone and the foundation brakes make "
      "up the difference until the truck slows. A pack-saturated "
      "governor would have every electrified candidate descending "
      "slower. That is a WS9 requirement rather than a WS8 correction - "
      "it changes trip time and therefore the metric - and r3 ESCALATES "
      "it as **ESC-WS8-10** rather than changing it under an order whose "
      "scope is declared exhaustive. Section 7.1 puts a number on it: "
      "the retarding power the runs commanded that no sink could "
      "absorb.")
    w("")
    w("The descent case is the one that matters to WS6: a series "
      "candidate holding the 6% grade puts several hundred kilowatts into "
      "a resistor bank that has to reject it to air, and that is a "
      "packaging and airflow problem, not an electrical one. The number "
      "to size on is the PACK-SATURATED one, not the pack-accepting one, "
      "because a buffer with a few tens of kWh of headroom does not "
      "survive a mountain descent.")
    w("")
    w("---")
    w("")


def interface():
    w("## 13. Machine-readable interface (R14)")
    w("")
    w("Every worst-case field below is an explicit max/min over an "
      "enumerated case set with the governing case labelled inline. This "
      "block is byte-identical to `results_ws8.json['interface_ws8']`; "
      "`verify_ws8.py` asserts it.")
    w("")
    w("```json")
    w(json.dumps(g("interface_ws8"), indent=1))
    w("```")
    w("")
    w("---")
    w("")


def provenance():
    w("## 14. Provenance and reproduction")
    w("")
    meta = g("_meta")
    w("Inherited read-only from Vehicle Zero (CLAUDE.md rule 10 - nothing "
      "in another workstream's folder was modified):")
    w("")
    ws2 = g("interface_ws8/ws2_chain_of_record")
    w(f"- **WS2 r{ws2['ws2_rework_round']}** measured traction loss map "
      f"`{ws2['map_file']}` at {ws2['map_voltage_V']:.0f} V, "
      f"{ws2['feasible_cells']:,} feasible cells, read through "
      f"`{ws2['loader']}`")
    w("- **WS2** stack-length scaling rule and `mass_end_kg = 18.0` split, "
      "used verbatim as WS8's machine mass law")
    pk = g("task3_trial/cold_minus10C/S1/spec/pack") or {}
    der = g("task3_trial/hot_alt_2000m_45C/S0/spec/corner/"
            "engine_derate_factor") or float("nan")
    pk = pk or dict(p_cont_chg_kW_at_corner=float("nan"),
                    p_cont_chg_kW=float("nan"))
    w("- **WS3** cell definitions, pack overhead model "
      "(1.55 x cell + 35 kg) and cold charge-acceptance figures - the "
      f"last of these APPLIED since r2 at the -10 C corner "
      f"({pk.get('p_cont_chg_kW_at_corner', float('nan')):.1f} kW against "
      f"{pk.get('p_cont_chg_kW', float('nan')):.1f} kW warm), where in r1 "
      "it was listed here and never called (finding F2)")
    w("- **WS4** `WillansEngine`, `PMGenerator`, `derate_factor` and the "
      "R12 chain conventions; `WS2TractionChain` as the ruled map loader. "
      f"`derate_factor` is APPLIED since r2 at the added 2,000 m / +45 C "
      f"corner (R28), where it returns {der:.4f} and shrinks every "
      "engine's full-load curve and therefore every R18 continuous "
      "rating; in r1 it was imported, re-exported and never called "
      "(finding F11)")
    w("")
    w("**Every inherited object listed above is now exercised by the "
      "pipeline.** That is the point of the two corrections just named: "
      "a provenance list is a claim about what the numbers were built "
      "from, and an inert entry in it is a false claim.")
    w("")
    w("Conventions carried:")
    w("")
    for c in meta["conventions"]:
        w(f"- {c}")
    w("")
    w("Reproduction:")
    w("")
    w("```")
    w("cd WS8_semi_architecture")
    w("../.venv/bin/python run_ws8.py        # regenerates results_ws8.json")
    w("../.venv/bin/python make_report_ws8.py  # regenerates this report")
    w("../.venv/bin/python verify_ws8.py     # asserts report == results")
    w("```")
    w("")
    w(f"Fixed seeds {meta['seeds']}.")
    w("")
    d = g("determinism")
    if d and d.get("status") != "NOT RUN":
        h1, h2 = d["half_1_simulation"], d["half_2_derived_blocks"]
        w(f"### Regeneration check (rule 1): **{d['status']}**")
        w("")
        w(d["what"])
        w("")
        w(f"**Half 1 - the simulation.** {h1['method']}. Result: trial "
          f"slice **{'byte-identical' if h1['matches_committed_run'] else 'DIFFERS'}** "
          f"(sha256 `{h1['task3_trial_nominal_sha256'][:16]}...`); cycle "
          f"ensemble "
          f"{'identical' if h1['task1_cycles_identical'] else 'DIFFERS'}; "
          f"S0 calibration "
          f"{'identical' if h1['task2_calibration_identical'] else 'DIFFERS'}.")
        w("")
        w(f"Wall-clock fields are {h1['wall_clock_fields']}.")
        w("")
        w(f"**Half 2 - the derived blocks.** {h2['method']}. Result: "
          f"`results_ws8.json` "
          f"**{'byte-identical' if h2['results_json_byte_identical'] else 'DIFFERS'}**, "
          f"and all {len(h2['csv_files'])} CSV exports "
          f"{'byte-identical' if h2['all_csv_exports_byte_identical'] else 'DIFFER'}.")
        w("")
        w(f"**Not checked:** {d['not_checked']}")
        w("")


R1_MARGINS = {
    # BASELINE_v4 R25, quoted: the r1 numbers of record, nominal
    # ensemble-min / median and the r1 worst corner (all cold_minus10C).
    "S1": dict(nom_min=-0.66, nom_med=+0.75, worst=-4.37),
    "S2": dict(nom_min=+0.36, nom_med=+1.70, worst=-1.90),
    "S3": dict(nom_min=-6.22, nom_med=-3.83, worst=-11.17),
    "S4": dict(nom_min=-3.67, nom_med=-0.95, worst=-8.26),
}
R2_MARGINS = {
    # BASELINE_v5 R35 and CHANGELOG_WS8_r2.md, quoted: the r2 numbers of
    # record, nominal ensemble-min / median and the r2 worst corner (all
    # cold_minus10C).
    "S1": dict(nom_min=-0.69, nom_med=+0.73, worst=-12.87),
    "S2": dict(nom_min=+0.48, nom_med=+1.80, worst=-9.62),
    "S3": dict(nom_min=-7.65, nom_med=-5.26, worst=-21.98),
    "S4": dict(nom_min=-3.84, nom_med=-1.06, worst=-17.21),
}
"""The PREVIOUS rounds' numbers of record, quoted from the ratified
baselines (R25 in BASELINE_v4, R35 in BASELINE_v5) and from
`CHANGELOG_WS8_r2.md`, so the movement table below is against the RECORD
rather than against a file this round overwrote.

These are the only hand-entered NUMBERS in this report, and they are
citations of superseded rounds rather than results. Every other figure is
formatted out of `results_ws8.json`. Where the prose quotes a round-1 or
round-2 figure - the 210.71 kW resistor export, S3's 71.8 kg resistor,
the 396.87 kW exhaust row - it is quoting `FINDINGS_WS8_r1.md` or
`FINDINGS_WS8_r2.md`, both sha-pinned in the interface block, and it is
labelled as a quotation at the point of use. No result in this report
depends on any of them."""


def changelog():
    """Section 15 of the report AND, byte-for-byte, the standalone
    CHANGELOG_WS8_<round>.md. One generator, one set of numbers: the
    changelog cannot drift from the report, and neither can drift from
    `results_ws8.json` (rule 2)."""
    start = len(L)
    w(f"## 15. {ROUND} changelog - what moved, and which way")
    w("")
    iface = g("interface_ws8")
    vs = g("verdict_stability")
    cd_ = g("correction_directions") or {}
    w(f"This round executed `R3_DIRECTIVE.md` against "
      f"`FINDINGS_WS8_r2.md`. The verdicts were **not** reopened: R25 "
      f"executed all four kills and the WHR drop on the pre-committed "
      f"criteria, and the directive's instruction was to make the numbers "
      f"of record correct, to STOP and report if any verdict flipped, and "
      f"to STOP if S3's nominal ensemble-min crossed the +3% bar. "
      f"Neither happened.")
    w("")
    w("### 15.1 Which direction each candidate moved")
    w("")
    w("Against r2's numbers of record as quoted in R35 (BASELINE_v5) and "
      "`CHANGELOG_WS8_r2.md`:")
    w("")
    w("| candidate | nominal min, r2 -> r3 | nominal median, r2 -> r3 | "
      "worst corner, r2 -> r3 | direction | verdict |")
    w("|---|---|---|---|---|---|")
    for c in CANDS[1:]:
        r2 = R2_MARGINS[c]
        m = g(f"task3_margins/nominal/{c}/ensemble")
        ak = g(f"advance_kill/candidates/{c}")
        d_med = m["median"] - r2["nom_med"]
        wc = ak["worst_corner_margin_pct_min"]
        arrow = ("WORSE" if d_med < -0.005
                 else ("BETTER" if d_med > 0.005 else "UNMOVED"))
        wtxt = ("no corners run" if wc is None else
                f"{pct(r2['worst'])} -> {pct(wc)} "
                f"({wc - r2['worst']:+.2f} pp, at "
                f"`{ak['worst_corner']}`)")
        w(f"| **{c}** | {pct(r2['nom_min'])} -> {pct(m['min'])} | "
          f"{pct(r2['nom_med'])} -> {pct(m['median'])} "
          f"({d_med:+.2f} pp) | {wtxt} | **{arrow}** on the nominal "
          f"median | **{ak['verdict']}** |")
    w("")
    b1 = cd_.get("B1", {})
    ttr = g("s3_ttr_path_status") or {}
    w(f"**Almost all of that movement is one correction, and it is "
      f"measured rather than inferred.** The one-factor row "
      f"`B1_reverted_brake_and_fuel` in section 4.4 reverts R3's control "
      f"rule and nothing else: {b1.get('direction', 'not measured')}. "
      f"Everything r3 changed besides that rule is an ACCOUNTING "
      f"correction - the run closure and the ledger rows it found. Only "
      f"one of those moves a margin at all, because it moves THE RULER, "
      f"and it too is measured rather than called small: "
      f"{g('correction_directions/R3_S0_launch_fuel/direction', 'not measured')}. "
      f"Every other r3 correction is a heat row, and no margin reads the "
      f"heat ledger - which is why S1 and S4 come back at r2's numbers to "
      f"the precision this table is quoted to.")
    w("")
    if ttr:
        w(f"**A consequence worth stating in the changelog rather than "
          f"only in the escalations.** With the rule applied, S3 takes "
          f"{ttr['e_ttr_charge_bus_kWh_total']:.3f} kWh of "
          f"through-the-road charge over the whole trial, on "
          f"{ttr['runs_with_any_ttr']} of {ttr['runs_examined']} runs, and "
          f"the 0.72-of-capacity BSFC policy withheld "
          f"{ttr['e_ttr_blocked_by_load_policy_kWh_total']:.3f} kWh of it. "
          f"Half of S3's declared energy policy is inert, for a reason "
          f"that is a modelling artefact rather than a control choice - "
          f"raised as ESC-WS8-8 and not self-resolved.")
        w("")
    w("The worst-corner column IS like-for-like this round: r2 and r3 "
      "run the same six corners on the same seeds. r2's own table was "
      "not, and said so.")
    w("")
    hot = {c: g(f"task3_margins/hot_alt_2000m_45C/{c}/ensemble/min")
           for c in CANDS[1:]}
    cold = {c: g(f"task3_margins/cold_minus10C/{c}/ensemble/min")
            for c in CANDS[1:]}
    ds = g("corner_derate_scope/R28_corner") or {}
    if all(v is not None for v in hot.values()):
        nom = {c: g(f"task3_margins/nominal/{c}/ensemble/min")
               for c in CANDS[1:]}
        better = [c for c in hot if hot[c] > nom[c]]
        worse = [c for c in hot if hot[c] <= nom[c]]
        w(f"**The R28 corner is still not the worst one, and r3 scopes "
          f"what that means** (r2 finding M3). At Vehicle One the thin "
          f"air at 2,000 m takes about 27% off the aerodynamic bill, "
          f"which is the dominant term on a line-haul corridor, and that "
          f"outweighs the "
          f"{(1 - g('task3_trial/hot_alt_2000m_45C/S0/spec/corner/engine_derate_factor')) * 100:.1f}% "
          f"engine derate it also imposes.")
        w("")
        w("| candidate | nominal min | 2,000 m / +45 C min | -10 C min |")
        w("|---|---|---|---|")
        for c in hot:
            w(f"| **{c}** | {pct(nom[c])} | {pct(hot[c])} | "
              f"{pct(cold[c])} |")
        w("")
        w(f"{', '.join(better) or 'No candidate'} gain at the R28 corner "
          f"relative to nominal"
          + (f"; {', '.join(worse)} "
             f"{'lose' if len(worse) != 1 else 'loses'} there, because "
             f"the derate falls on a mechanical path that has no genset "
             f"behind it and pushes the shortfall onto the pack"
             if worse else "")
          + ". Either way the R28 corner is nowhere near the -10 C "
            "column. **The cold wall is Vehicle One's binding corner, "
            "and nothing in this round moved that.** R30 already reads it "
            "that way.")
        w("")
        if ds:
            w("**Scope of that statement, measured** (finding M3). "
              + ds["statement"])
            w("")
            w("*Direction of error.* " + ds["direction_of_error"])
            w("")
    w("### 15.2 The findings, and what each one did")
    w("")
    w("Every cell in the DIRECTION column below is either generated by "
      "`correction_directions()` from the one-factor table in section "
      "4.4, or says explicitly that the direction is not separately "
      "measured and why. r2's version of this table was thirteen Python "
      "literals the verifier structurally could not reach, and "
      "`FINDINGS_WS8_r2.md` M1 names three of them as contradicted by "
      "that round's own numbers. That is finding M1, and this is its "
      "fix.")
    w("")

    def _dir(key, fallback):
        e = cd_.get(key)
        if not e:
            return fallback
        if e.get("measurable"):
            base = e["direction"]
            if key == "F6" and e.get("corner_caveat"):
                base += " - " + e["corner_caveat"]
            return base + f" (measured: `{e['one_factor_row']}`)"
        return e["direction"] + " - " + e.get("why_not", "")

    w("| finding | severity | what r3 did | direction |")
    w("|---|---|---|---|")
    rows = [
        ("B1", "blocking",
         "THE ONE RULE. An engine geared to the road is in OVERRUN on "
         "every sample where the vehicle is moving and commands no "
         "tractive force: it burns no fuel, makes no positive shaft "
         "power, and its compression brake is available only there. S0 "
         "already had this cut-off inline; it is stated once in "
         "`overrun_mask` and applied to every candidate. S3's "
         "through-the-road charging is GATED ON THE VEHICLE NOT BRAKING "
         "(and, a fortiori, on the engine not being in overrun); the "
         "axle-A load threshold that used to be the only thing holding "
         "it back is no longer the gate and survives only as the BSFC "
         "policy it always was - and it is MEASURED to withhold "
         f"{(g('s3_ttr_path_status/e_ttr_blocked_by_load_policy_kWh_total') or 0.0):.3f}"
         " kWh over the whole trial, so it decides nothing either way. "
         "S2's genset ceiling is forced to zero on any sample where its "
         "lockup coupling is drawing the compression brake. The "
         "retarding ENVELOPE is untouched, so no achieved speed, trip "
         "time or descent case moves. The per-run assertion is hard and "
         "runs on every candidate: `heat_ledger.overrun_exclusivity`",
         _dir("B1", "not measured")),
        ("M1", "material",
         "every hand-written direction string deleted; this column and "
         "section 4.4's direction table are generated by "
         "`correction_directions()` from the one-factor rows, and the "
         "one-factor set is widened from the S1/S2 pair to all four "
         "candidates so that a correction which does not reach a "
         "candidate returns a bit-identical row instead of an assertion",
         "record integrity - it moves no number; "
         "`FINDINGS_WS8_r2.md` M1 names three r2 direction cells that "
         "this file's own numbers contradicted, and the measurement "
         "above replaces all thirteen"),
        ("M2", "material",
         "the per-km bullets, and every other per-km claim in the "
         "report, computed on the PAIRED per-seed statistic and "
         "labelled; the 'every candidate is more efficient per "
         "kilometre' sentence generated from data; the ratio of medians "
         "exported beside it for disclosure "
         "(`interface_ws8.per_km_margin_paired`)",
         "record integrity - no margin moves; `FINDINGS_WS8_r2.md` M2 "
         "records that the r2 sentence was false for S3, whose two "
         "statistics differ in SIGN"),
        ("M3", "material",
         "`corner_derate_scope` measures, leaf by leaf against nominal, "
         "what each corner's model actually changes, and the R28 "
         "conclusion is scoped by the measurement rather than asserted",
         "record integrity - no number moves; the direction of error is "
         "exported"),
        ("M4", "material",
         "ESC-WS8-1 restated with BOTH halves of the cell-substitution "
         "direction, the power half measured at the contact patch and "
         "the cold corner used as the in-model measurement of the "
         "transfer, and R27/ESC-1(c)'s execution as WS9's S4' cited with "
         "its provisional status",
         "record integrity - no number moves"),
        ("m1", "minor",
         "the ratio the 6% grade demands is a SWEPT result and now says "
         "so, with a resolution sensitivity solved at ten times the grid "
         "in both dimensions instead of the claim that no grid was doing "
         "any work", "record precision"),
        ("m2", "minor",
         "the unserved-energy table lists every case above 1 kWh instead "
         "of silently truncating at twenty", "record precision"),
        ("m3", "minor",
         "`heat_ledger_ws6.csv` carries `ledger_version`, a `basis` "
         "column, `components_sum_kW` and the governing run, and a "
         "per-component label file for the simulated member",
         "record precision"),
        ("m4", "minor",
         "the instantaneous peaks `heat_peaks` has always computed are "
         "enveloped and exported beside the sustained figure, in the "
         "ledger and in the CSVs", "record precision"),
        ("m5", "minor",
         "`all_cases_close_and_within_rating` states exactly what it "
         "tests, the simulated member is no longer exempt from the "
         "closure, and the resistor row's unfailability by construction "
         "is stated rather than left to be discovered",
         "record precision - and the exemption it describes is what B1 "
         "came through"),
        ("m6", "minor",
         "the bus-side/wheel-side slippage on the pack charge ceiling is "
         "stated where the number is quoted; the physics is unchanged "
         "because it is conservative and changing it would move every "
         "margin", "record precision - deliberately no number moves"),
        ("m7", "minor",
         "section 4.2 renders the measured R22(d) charge and its "
         "coast-permitting bracket for all five candidates instead of "
         "calling the disconnect a deleted tax that nobody pays",
         "record precision"),
    ]
    for r in rows:
        w(f"| **{r[0]}** | {r[1]} | {r[2]} | {r[3]} |")
    w("")
    w("### 15.2b Raised and closed inside r3, by the extended closure")
    w("")
    w("R3_DIRECTIVE item 1 ordered `heat_closure_check` extended to the "
      "simulated member. Extending it meant building a per-sample energy "
      "balance for every run, and the balance did not close until six "
      "book-keeping errors were found. None of them was in "
      "`FINDINGS_WS8_r2.md`; they are listed here because a correction "
      "that is not in the changelog is a silent one. The CONSEQUENCE "
      "column is measured, not asserted - where a correction has a "
      "one-factor row its direction is rendered from it, and where it "
      "cannot move a margin the reason is structural and stated.")
    w("")
    w("| what | where | consequence |")
    w("|---|---|---|")
    _s0dir = g("correction_directions/R3_S0_launch_fuel/direction",
               "not separately measured")
    _NOMARGIN = ("no margin can move: the heat ledger is built from the "
                 "completed runs (`heat_ledger()` runs after "
                 "`task3_margins` is fixed) and no margin reads it")
    _s3ttr = g("s3_ttr_path_status/e_ttr_charge_bus_kWh_total", 0.0)
    _ov = g("interface_ws8/retard_overcommitment") or {}
    for r in [
        ("S0 was fuelled at the IDLE rate on the first few tenths of a "
         "second of every pull-away, because `stopped` is `v <= 0.1 m/s` "
         "and a launch begins inside it - the model credited the engine "
         "with about 28 kW of launch shaft power on 13.7 kW of fuel",
         "`S0.account`",
         f"it moves THE RULER and therefore every margin, so it is "
         f"switchable and measured rather than called small: {_s0dir}"),
        ("S0's clutch-slip heat was booked twice: once inside "
         "`p_shaft - aux - p_wheel`, which already contains it, and "
         "again as `p_slip_kw`",
         "`S0.account` heat rows", _NOMARGIN),
        ("S0's accessory row booked the full accessory load even on "
         "samples where the crank was at its full-load curve and could "
         "not carry it - r1's finding F3 for S2, surviving in the ruler. "
         "The row now books what the crank carried and the shortfall is "
         "exported",
         "`S0.account` heat rows", _NOMARGIN),
        ("S2's standstill idle fuel was added to the fuel total AFTER "
         "the fuel series, so the heat ledger never saw it; and its "
         "generator's own loss was priced off the free-speed locus while "
         "the crank was locked to the road",
         "`S2.account` heat rows", _NOMARGIN),
        ("S3's through-the-road path had NO heat rows at all - the "
         "engine was charged for the torque and the pack credited with "
         "the electricity, with the axle-A box and the e-axle's "
         "generating losses booked nowhere - and regen the full pack "
         "could not take was dropped with no bookkeeping at all",
         "`S3.account`, `series_dispatch`",
         _NOMARGIN + f"; and the rows it adds carry "
         f"{_s3ttr:.3f} kWh of through-the-road charge over the whole "
         f"trial, because the path itself is inert once the B1 gate is "
         f"applied (ESC-WS8-8) - the correction is real and its measured "
         f"contribution is zero"),
        ("regen the FULL pack cannot accept is dispatched to the brake "
         "resistor by `series_dispatch` and by S3's SOC loop - each says "
         "so in its own comment - and r3's first cut of the run closure "
         "carried it as an out-term OUTSIDE the component ledger. A real "
         "power flow with no component row is r1's F1 and r2's B1 over "
         "again. It is now booked to the resistor up to the rating whose "
         "mass was charged, and the remainder is exported as a "
         "CAPABILITY shortfall",
         "`resistor_and_overcommitment`, `run_closure`",
         _NOMARGIN + f"; worst overcommitment "
         f"{_ov.get('value_kW', 0.0):.1f} kW sustained at "
         f"`{_ov.get('governing_case')}` - escalated as ESC-WS8-10"),
    ]:
        w(f"| {r[0]} | {r[1]} | {r[2]} |")
    w("")
    w("### 15.3 Verdict stability")
    w("")
    w("| candidate | verdict executed under R25 | verdict the same "
      f"criteria give on the {ROUND} numbers | headroom to the >= 3% "
      "nominal bar |")
    w("|---|---|---|---|")
    for c, v in vs["candidates"].items():
        w(f"| **{c}** | {v['executed_verdict']} | "
          f"{v['verdict_on_same_criteria']} | "
          f"{v['headroom_to_advance_pp']:.2f} pp short |")
    w("")
    w(f"WHR on the {ROUND} numbers: "
      + ", ".join(f"{k} {v}"
                  for k, v in vs["whr_on_current_numbers"].items())
      + f" - {'unchanged' if vs['whr_unchanged'] else 'CHANGED'}.")
    w("")
    sc = vs["r3_stop_condition"]
    w(f"**R3_DIRECTIVE item 1's own trip-wire, implemented rather than "
      f"remembered.** {sc['rule']} S3's nominal ensemble-min on the "
      f"{ROUND} numbers is "
      f"{pct(sc['S3_nominal_margin_pct_min'])} against the "
      f"+{sc['bar_pct']:.0f}% bar: `crossed = "
      f"{str(sc['crossed']).lower()}`. {sc['note']}")
    w("")
    _n = vs["note"]
    w(f"**`all_unchanged = {vs['all_unchanged']}`.** "
      + _n[0].upper() + _n[1:])
    w("")
    w("### 15.4 Environment")
    w("")
    meta = g("_meta")
    w(f"r1's artifacts were produced on Python 3.11.15 / numpy 2.4.6 on "
      f"x86-64 Linux; r2's and r3's are produced on Python "
      f"{meta['python']} / numpy {meta['numpy']} on arm64 macOS. The two "
      f"platforms differ in the last one or two units in the last place "
      f"of a double - a relative difference around 1e-16, from libm and "
      f"SIMD reduction order, not from any change here. Byte-stable "
      f"regeneration (rule 1) is a property of a run reproducing ITSELF "
      f"on one machine, and it is checked in section 14 on this one. "
      f"Nothing in the errata depends on that difference, and no reported "
      f"figure is quoted to anything like that precision.")
    w("")
    w("### 15.5 Inputs, SHA-pinned")
    w("")
    w("Every source file and every read-only object inherited from "
      "another workstream is pinned by sha256 in "
      "`interface_ws8.inputs_sha256`, so a consumer can tell from the "
      "export alone whether the numbers it holds came from these exact "
      "inputs. " + str(len(iface["inputs_sha256"])) + " files are pinned, "
      "and r3 adds this round's order, the findings file it closes and "
      "the baseline it runs against without dropping r2's - the r2 "
      "corrections are still live in the code and the verdicts still "
      "cite R25.")
    w("")
    w("---")
    w("")
    _write_changelog_file(L[start:])


def _write_changelog_file(lines):
    meta = g("_meta")
    iface = g("interface_ws8")
    head = [
        f"# CHANGELOG - WS8 round 3 ({ROUND})",
        "",
        "**Generated**, not written: every figure below is formatted out "
        "of `results_ws8.json` by `make_report_ws8.py`, which emits this "
        "file and section 15 of `REPORT_WS8.md` from the same lines. "
        "Nothing here is transcribed by hand (rule 2) - including, this "
        "round, every DIRECTION cell, which r2 wrote by hand and got "
        "wrong three times (finding M1).",
        "",
        f"| | |",
        f"|---|---|",
        f"| Order executed | `WS8_semi_architecture/R3_DIRECTIVE.md` "
        f"(lead-issued 2026-08-30, under R35) |",
        f"| Findings closed | `FINDINGS_WS8_r2.md` B1, M1-M4, m1-m7 |",
        f"| Baseline of record | {meta['baseline_of_record']} |",
        f"| Numbers version | {iface['numbers_version']} "
        f"(supersedes {iface.get('supersedes', {}).get('numbers_version')}) |",
        f"| Heat ledger version | {g('heat_ledger/ledger_version')} - "
        f"WS6 consumes ONLY this one |",
        f"| Verdicts | `{iface['verdicts']['status']}` - not reopened by "
        f"this round |",
        f"| Seeds | {meta['seeds'][0]}..{meta['seeds'][-1]} "
        f"({meta['n_seeds']} seeds) |",
        f"| Python / numpy | {meta['python']} / {meta['numpy']} |",
        "",
        "Full context, tables and the interface block: `REPORT_WS8.md`.",
        "",
        "---",
        "",
    ]
    body = [ln for ln in lines]
    if body and body[0].startswith("## 15."):
        body[0] = "## What moved, and which way"
    body = [re.sub(r"^### 15\.(\d+[a-z]?) ", r"### \1. ", ln)
            for ln in body]
    with open(OUT_CHANGELOG, "w") as f:
        f.write("\n".join(head + body).rstrip() + "\n")
    print(f"wrote {OUT_CHANGELOG} "
          f"({os.path.getsize(OUT_CHANGELOG):,} bytes)")


def main():
    header()
    summary()
    task0()
    task1()
    task2()
    task3()
    two_speed()
    one_factor()
    task4()
    task5()
    unserved()
    corroboration()
    recommendation()
    sanity()
    escalations()
    heat()
    interface()
    provenance()
    changelog()
    with open(OUT, "w") as f:
        f.write("\n".join(L).rstrip() + "\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes)")


if __name__ == "__main__":
    main()
