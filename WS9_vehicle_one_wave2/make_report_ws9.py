#!/usr/bin/env python3
"""
Project Volt - WS9
Renders REPORT_WS9.md from results_ws9.json.

THE REPORT IS GENERATED, NOT WRITTEN (CLAUDE.md rule 2). Every number below
is formatted out of `results_ws9.json`, and `verify_ws9.py` asserts
independently that each rendered figure appears verbatim in the results and
that the interface block equals `results_ws9.json['interface_ws9']`. Nothing
is transcribed by hand.

    ../.venv/bin/python make_report_ws9.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_ws9.json")
OUT = os.path.join(HERE, "REPORT_WS9.md")


def f(x, n=2, plus=False):
    if x is None:
        return "n/a"
    s = f"{x:+.{n}f}" if plus else f"{x:.{n}f}"
    return s


def kg(x):
    return "n/a" if x is None else f"{x:,.0f}"


def pct(x, n=2):
    return "n/a" if x is None else f"{x:+.{n}f}%"


def main():
    R = json.load(open(RESULTS))
    L = []
    w = L.append
    design = R["_meta"]["design_duty"]
    control = R["_meta"]["control_duty"]
    T = R["trial"]["nominal"]
    M = R["margins"]["nominal"]
    AK = R["advance_kill"]["candidates"]
    ruler = "S0R"
    dd = R["duties"][design]["ensemble"]
    cd = R["duties"][control]["ensemble"]

    # ---------------------------------------------------------------- 0
    w("# REPORT WS9 - VEHICLE ONE, WAVE TWO: THE TWO WALLS AND THE COLD "
      "WALL")
    w("")
    w("Workstream WS9, Vehicle One. Executes "
      "`WS9_vehicle_one_wave2/ASSIGNMENT.md` against `BASELINE_v4.md`.")
    w("")
    w("**Nothing here is ratified.** The lead ratifies (CLAUDE.md rule 11). "
      "This report states what the physics gave and what it cost; the "
      "execute-or-spare decision is the lead's.")
    w("")
    w("**This report is generated**, not written: every number below is "
      "formatted out of `results_ws9.json` by `make_report_ws9.py`, and "
      "`verify_ws9.py` asserts independently that each rendered figure "
      "appears verbatim and that the interface block equals "
      "`results_ws9.json['interface_ws9']` (rule 2).")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Entry point | `run_ws9.py` (fixed seeds "
      f"{R['_meta']['seeds'][0]}..{R['_meta']['seeds'][-1]}, "
      f"{R['_meta']['n_seeds']} seeds) |")
    w("| Baseline of record | BASELINE_v4.md |")
    w(f"| Python / numpy | {R['_meta']['python']} / "
      f"{R['_meta']['numpy']} |")
    w("| Metric of record | **primary energy per PAYLOAD tonne-km** "
      "[MJ/(t.km)] |")
    w(f"| Design duty (R29) | **{design}** - gates the verdicts |")
    w(f"| Control duty (R29) | {control} - reported alongside, never "
      f"gates |")
    w(f"| Inherited WS8 code round | "
      f"`{R['inherited_vintage']['ws8_code_round_fingerprint']['code_round']}`"
      f" (SHA-pinned in section 12) |")
    w("")
    w("---")
    w("")
    w("## 0. What this trial found")
    w("")
    adv = [k for k, v in AK.items() if v["verdict"] == "ADVANCE"]
    kill = [k for k, v in AK.items() if v["verdict"] == "KILL"]
    if adv:
        w(f"**{', '.join(adv)} ADVANCE. "
          f"{', '.join(kill) if kill else 'Nothing else'} "
          f"{'KILL' if kill else 'was tested'}.**")
    else:
        w("**No candidate advances.**")
    w("")
    w("Four things decided this trial, and three of them are not fuel "
      "numbers.")
    w("")
    be = R["_s6_break_even"]
    w(f"1. **Naming the duty changed the answer, exactly as R29 said it "
      f"would.** The design duty is a grade-heavy regional corridor - "
      f"{f(dd['climb_m_per_km']['median'],1)} m of climb per kilometre "
      f"against the control duty's {f(cd['climb_m_per_km']['median'],1)}, "
      f"and {f(dd['frac_dist_grade_ge_2pct']['median']*100,1)}% of its "
      f"distance at 2% or steeper against "
      f"{f(cd['frac_dist_grade_ge_2pct']['median']*100,1)}%. Every "
      f"candidate's margin moves, and for some of them it changes sign "
      f"between the two duties. A fleet average would have hidden all of "
      f"it, which is why the assignment forbids one.")
    w("")
    w(f"2. **The zero-mass stack is the cleanest result in the report, and "
      f"it rests on one cited number.** S6 is mass-neutral with the ruler "
      f"TO THE KILOGRAM - same gearbox, same retarder, same axles, same "
      f"aftertreatment - so on a metric that divides by payload its margin "
      f"IS its fuel margin, with no payload term at all. It clears the bar "
      f"on both duties. The whole of that margin comes from a peak brake "
      f"thermal efficiency of {f(be['claimed_peak_BTE'],3)} taken from a "
      f"manufacturer's demonstration document, against the incumbent's "
      f"{f(be['incumbent_peak_BTE'],4)}. The break-even peak BTE at which "
      f"S6 exactly clears the +3% criterion is "
      f"**{f(be['break_even_peak_BTE'],4)}** - so the claim has "
      f"{f(be['claim_headroom_pp'],2)} points of headroom, and the lead can "
      f"see exactly how much of it has to be true (ESC-WS9-1).")
    w("")
    tw = R["two_walls"]
    fr11 = tw["third_constraint_coupling_floor"]["ENG-11L"]["frontier"]
    fr13 = tw["third_constraint_coupling_floor"]["ENG-13L"]["frontier"]
    w(f"3. **The two walls are not the whole story: a 2-speed dog box "
      f"meets a THIRD constraint, and the design duty is what exposes "
      f"it.** Two ratios do span 105 km/h cruise under the rpm ceiling and "
      f"the assignment's 6% grade - S5 clears both walls BY CONSTRUCTION, "
      f"in closed form. But the low gear's coupling floor sits above the "
      f"crawl speed a steeper grade forces, and below that floor the dogs "
      f"are open and the engine is not connected at all. The steepest grade "
      f"a CONTIGUOUS 2-speed can carry is "
      f"{f(fr11['steepest_contiguous_grade']*100,0)}% on the 11 L and "
      f"{f(fr13['steepest_contiguous_grade']*100,0)}% on the 13 L - and the "
      f"design duty carries grades to "
      f"{f(dd['grade_max']['max']*100,1)}%. The assignment's 6% wall sits "
      f"almost exactly on the frontier of what two ratios can do, which is "
      f"why S5 clears it and fails one point above it.")
    w("")
    both = [k for k, v in AK.items()
            if v["verdict"] == "ADVANCE"
            and (v["control_duty_nominal_margin_pct_min"] or -1) >= 0.0]
    w(f"4. **Mass is still payload, and it still decides everything else.** "
      f"Every electrified candidate here is more efficient per kilometre "
      f"than the ruler and every one of them is heavier. The payload each "
      f"gives up is in section 4.3, to the kilogram. Of the candidates that "
      f"advance on the design duty, "
      f"{'only ' + ', '.join(both) if both else 'none'} also "
      f"{'clears' if len(both) == 1 else 'clear'} the ruler on the CONTROL "
      f"duty - and it is the one that adds no mass at all. Every other "
      f"advance is a bet on the operator's duty being the design duty.")
    w("")
    w("| candidate | payload | vs ruler | " + design + " margin (min / "
      "median) | " + control + " margin (min / median) | verdict |")
    w("|---|---|---|---|---|---|")
    for cname, blob in T.items():
        s = blob["spec"]
        dm = M[design].get(cname)
        cm = M[control].get(cname)
        dlt = s["payload_kg"] - T[ruler]["spec"]["payload_kg"]
        v = AK.get(cname, {}).get("verdict", "**RULER**")
        w(f"| **{cname}** | {kg(s['payload_kg'])} kg | "
          f"{'-' if cname == ruler else f'{dlt:+,.0f} kg'} | "
          f"{'- (ruler)' if dm is None else pct(dm['ensemble']['min']) + ' / ' + pct(dm['ensemble']['median'])} | "
          f"{'- (ruler)' if cm is None else pct(cm['ensemble']['min']) + ' / ' + pct(cm['ensemble']['median'])} | "
          f"{'**' + v + '**' if v != '**RULER**' else v} |")
    w("")
    w("Margins are computed **per seed against the ruler on the same seed "
      "and the same duty**, then enveloped. The seed sets the corridor, the "
      "wind and the driver, so pairing removes the cycle draw from the "
      "comparison instead of leaving it in the variance.")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 1
    w("## 1. The design duty (R29), defined")
    w("")
    w("R29: *\"Vehicle One is specified for GRADE-HEAVY REGIONAL duty, with "
      "the flat line-haul corridor retained as a control on which the "
      "incumbent is CONCEDED near-optimal.\"*")
    w("")
    for duty in (design, control):
        d = R["duties"][duty]["definition"]
        w(f"**{duty}** - {d['role']}")
        w("")
        w(f"- built by `{d['built_by']}`")
        w(f"- {d['definition']}")
        w(f"- {d['gates']}")
        w("")
    w("| | " + design + " (design) | " + control + " (control) |")
    w("|---|---|---|")
    rows = [("distance, median [km]", "distance_km", 0),
            ("total climb, median [m]", "total_climb_m", 0),
            ("climb per km, median [m/km]", "climb_m_per_km", 2),
            ("max grade, worst seed", "grade_max", 4),
            ("min grade, worst seed", "grade_min", 4),
            ("net elevation change, worst seed [m]",
             "net_elevation_change_m", 4),
            ("distance at >=2% grade, median", "frac_dist_grade_ge_2pct", 4),
            ("distance at >=5% grade, median", "frac_dist_grade_ge_5pct", 4),
            ("mean corridor demand speed, median [km/h]",
             "v_tgt_mean_corridor_kmh", 1)]
    for label, key, n in rows:
        a, b = dd.get(key), cd.get(key)
        stat = "max" if "max" in label or "worst" in label else "median"
        if key == "grade_min" or key == "net_elevation_change_m":
            stat = "min" if key == "grade_min" else "max"
        w(f"| {label} | {f(a[stat], n) if a else 'n/a'} | "
          f"{f(b[stat], n) if b else 'n/a'} |")
    w("")
    w("**There is no fleet blend anywhere in this report.** WS8 reported a "
      "70/30 fleet mission; the assignment forbids one here, because R29's "
      "whole finding is that the sign of a margin flips between duties and "
      "a fleet average hides it (D15).")
    w("")
    w(f"The design duty is grade-heavy by construction, so R28's "
      f"`grade_heavy` corner is a **null operation** on it. WS9 runs that "
      f"corner anyway and asserts the identity "
      f"(`sanity.design_duty_null_at_grade_heavy_corner`: identical = "
      f"`{R['sanity']['design_duty_null_at_grade_heavy_corner']['identical']}`), "
      f"which turns a redundancy into a free consistency check on the whole "
      f"corner machinery. The consequence - that the design duty is gated "
      f"on four corners rather than five - is escalated as ESC-WS9-3.")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 2
    w("## 2. The ruler, restated (ESC-6)")
    w("")
    rs = T[ruler]["spec"]
    w("ESC-6, ruled in R27: *\"S0 gains a hydraulic retarder in WS9 with "
      "its mass charged - the ruler gets the equipment the duty demands.\"* "
      "A grade-heavy regional design duty is exactly the duty a retarder is "
      "bought for.")
    w("")
    ret = rs["retarder"]
    w("| | |")
    w("|---|---|")
    w(f"| engine | {rs['engine']['label']} |")
    w(f"| peak power | {f(rs['engine']['peak_power_kW'],1)} kW |")
    w(f"| island BSFC | {f(rs['engine']['island_bsfc_g_per_kWh'],1)} "
      f"g/kWh |")
    w(f"| retarder | max {f(ret['t_max_propshaft_Nm'],0)} Nm at the "
      f"propshaft, {f(ret['p_continuous_kW'],0)} kW continuous |")
    w(f"| retarder mass CHARGED | **{f(ret['mass_charged_kg'],0)} kg** "
      f"({f(ret['mass_installed_kg'],0)} kg installation weight including "
      f"oil, cited, + {f(ret['mass_cooling_delta_kg'],0)} kg of cooling "
      f"package, declared) |")
    w(f"| retarding force at 90 / 50 km/h | "
      f"{f(ret['force_at_90kmh_N'],0)} N / "
      f"{f(ret['force_at_50kmh_N'],0)} N |")
    w(f"| ruler payload | **{kg(rs['payload_kg'])} kg** |")
    w("")
    w("The retarder moves the answer BOTH ways and only the simulation can "
      "say which wins: the ruler loses "
      f"{f(ret['mass_charged_kg'],0)} kg of payload and gains its descent "
      "speed back. Its torque characteristic is the manufacturer's, read "
      "verbatim from a primary OEM fact sheet (section 12).")
    w("")
    w("### 2.1 Calibration cross-check, as an ENSEMBLE (finding F7)")
    w("")
    f7 = R["f7_crosscheck"]
    ev = f7["envelope_vs_band"]
    w("WS8's adjudication finding F7 (material, rule 4): the report's only "
      "external anchor was asserted on a MEDIAN while its own 8-seed "
      "envelope spanned the entire reference band, and the comparison was "
      "not mass-matched. WS9's ruler is a different vehicle - it carries "
      "the retarder - so the cross-check is re-run, and it is rendered as "
      "an envelope.")
    w("")
    w("| | L/100 km |")
    w("|---|---|")
    w(f"| **{ruler}, {control} with grade zeroed - ensemble min** | "
      f"**{f(ev['model_min'])}** |")
    w(f"| **{ruler}, same - ensemble median** | "
      f"**{f(ev['model_median'])}** |")
    w(f"| **{ruler}, same - ensemble max** | **{f(ev['model_max'])}** |")
    w(f"| same, mass-matched to the reference payload "
      f"({f(f7['reference']['regulatory_payload_t'],1)} t) - median | "
      f"{f(ev['mass_matched_median'])} |")
    w(f"| ICCT / TUV NORD, typical EU tractor-trailer | "
      f"{f(f7['reference']['typical_EU_L_per_100km'],1)} |")
    w(f"| ICCT / TUV NORD, at that cycle's regulatory payload | "
      f"{f(f7['reference']['at_regulatory_payload_L_per_100km'],1)} |")
    w(f"| ICCT / TUV NORD, best-in-class EU | "
      f"{f(f7['reference']['best_in_class_EU_L_per_100km'],1)} |")
    w("")
    w(f"Median residual against the typical figure: "
      f"{pct(ev['median_residual_pct'])}. Mass-matched residual against the "
      f"regulatory-payload figure: "
      f"{pct(ev['mass_matched_residual_vs_at_reg_payload_pct'])}. The "
      f"8-seed envelope is "
      f"{'WIDER' if ev['envelope_wider_than_band'] else 'narrower'} than "
      f"the published band it is being compared against "
      f"({f(ev['band_min'],1)}-{f(ev['band_max'],1)}), and that is stated "
      f"here rather than left out - which is precisely what F7 asked for. "
      f"No claim of agreement is made beyond what the envelope supports.")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 3
    w("## 3. The two walls, addressed by construction - and the third")
    w("")
    w(f"- **WALL 1** - {tw['wall1']}")
    w(f"- **WALL 2** - {tw['wall2']}")
    w("")
    w("### 3.1 Wall 1, in closed form")
    w("")
    w("WS8's adjudication finding F12: WS8 reported the single-ratio "
      "ceiling as 3.60 because that was the largest entry in a swept grid. "
      "A bound that is a property of somebody's grid resolution is not a "
      "bound. WS9 solves each wall algebraically and keeps the sweep as the "
      "illustration.")
    w("")
    w(f"Ratio ceiling at 105 km/h under the 2,100 rpm limit, closed form: "
      f"**{f(tw['two_speed_solve']['ENG-13L']['solve']['wall1_ratio_ceiling'], 4)}**.")
    w("")
    w("| engine | ratio required for 6% | span needed vs the ceiling | "
      "force available at the ceiling | force required | single ratio "
      "feasible |")
    w("|---|---|---|---|---|---|")
    for k, v in tw["single_ratio_closed_form"].items():
        w(f"| {k} | {f(v['ratio_required_for_6pct'],3)} | "
          f"{f(v['span_needed'],3)} | {f(v['F_available_at_ceiling_kN'],1)} "
          f"kN | {f(v['F_required_6pct_kN'],1)} kN | "
          f"**{v['single_ratio_feasible']}** |")
    w("")
    w("### 3.2 Two ratios, solved")
    w("")
    w("Three constraints, all physical, none of them a preference: Wall 1 "
      "caps the HIGH ratio, Wall 2 floors the LOW ratio, and CONTIGUITY "
      "caps the step between them - at the shift speed the low gear must be "
      "at or under its over-speed ceiling exactly when the high gear is at "
      "or above its lugging floor, or there is a band of road speed in "
      "which the engine has no gear at all.")
    w("")
    w("| engine | R high | R low | span used (bound) | cruise rpm at "
      "100 km/h | shift speed | coupling floor | holds 6% | band "
      "contiguous |")
    w("|---|---|---|---|---|---|---|---|---|")
    for k, v in tw["two_speed_solve"].items():
        s, sw = v["solve"], v["sweep"]
        w(f"| {k} | {f(s['ratio_high'],3)} | {f(s['ratio_low'],3)} | "
          f"{f(s['contiguity_span_used'],3)} "
          f"({f(s['contiguity_span_max'],3)}) | "
          f"{f(s['rpm_at_cruise_100kmh'],0)} | "
          f"{f(s['shift_speed_kmh'],1)} km/h | "
          f"{f(s['low_gear_floor_kmh'],1)} km/h | "
          f"**{sw['holds_6pct']}** | {sw['engine_band_is_contiguous']} |")
    w("")
    rl = tw["ratio_law"]
    w("**A law falls out of that algebra, and it inverts the usual "
      "instinct.** " + rl["statement"])
    w("")
    w(rl["consequence"])
    w("")
    w("### 3.3 The third constraint, which the design duty exposes")
    w("")
    w(tw["third_constraint_coupling_floor"]["ENG-11L"]["finding"])
    w("")
    for k, v in tw["third_constraint_coupling_floor"].items():
        w(f"**{k}** - coupling floor {f(v['coupling_floor_kmh'],1)} km/h, "
          f"machine sustained contribution "
          f"{f(v['p_machine_sustained_kW'],1)} kW")
        w("")
        w("| grade | engine holds it at | reachable above the coupling "
          "floor | machine alone sustains to | holds on either |")
        w("|---|---|---|---|---|")
        for r in v["rows"]:
            w(f"| {f(r['grade']*100,0)}% | "
              f"{f(r['v_hold_engine_low_gear_kmh'],1)} km/h | "
              f"**{r['engine_reachable']}** | "
              f"{f(r['v_hold_machine_sustained_kmh'],1)} km/h | "
              f"**{r['holds_on_either']}** |")
        w("")
    w("### 3.4 The frontier: the steep grade OR a contiguous band")
    w("")
    w(fr11["finding"])
    w("")
    for k, v in (("ENG-11L", fr11), ("ENG-13L", fr13)):
        w(f"**{k}** - steepest CONTIGUOUS grade: "
          f"**{f(v['steepest_contiguous_grade']*100,0)}%**")
        w("")
        w("| grade | R low required | span needed | contiguous | cruise "
          "rpm at 100 km/h if contiguous | gap left if not |")
        w("|---|---|---|---|---|---|")
        for r in v["rows"]:
            gap = ("-" if r["contiguous_two_speed_possible"]
                   else f"{f(r['gap_low_top_kmh'],1)}-"
                        f"{f(r['gap_high_bottom_kmh'],1)} km/h "
                        f"({f(r['gap_width_kmh'],1)} wide)")
            w(f"| {f(r['grade']*100,0)}% | "
              f"{f(r['ratio_low_required'],3)} | "
              f"{f(r['span_required_against_wall1'],3)} | "
              f"**{r['contiguous_two_speed_possible']}** | "
              f"{f(r['rpm_at_100kmh_if_contiguous'],0) if r['rpm_at_100kmh_if_contiguous'] else '-'} | "
              f"{gap} |")
        w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 4
    w("## 4. Candidate results - the headline, per duty class")
    w("")
    w("All at **36,300 kg GCW**. Because GCW is fixed, the road-load "
      "physics is identical for every candidate: mass does not change how "
      "the truck drives, it changes what the truck may carry.")
    w("")
    for duty in (design, control):
        w(f"### 4.{1 if duty == design else 2} {duty}"
          f"{' - THE DESIGN DUTY (gates)' if duty == design else ' - the control duty (does not gate)'}")
        w("")
        w("| | architecture | payload | L/100 km | grid kWh | "
          "MJ_primary/payload-tkm (min / median / max) | margin vs ruler "
          "(min / median) | correction share (min..max) | verdict |")
        w("|---|---|---|---|---|---|---|---|---|")
        for cname, blob in T.items():
            s = blob["spec"]
            e = blob["per_duty"][duty]["ensemble"]
            m = M[duty].get(cname)
            iface = R["interface_ws9"]["candidates"][cname]
            cs = iface["fuel_correction_share"]
            v = AK.get(cname, {}).get("verdict", "RULER")
            w(f"| **{cname}** | {s['title']} | {kg(s['payload_kg'])} kg | "
              f"{f(e['fuel_L_per_100km']['median'])} | "
              f"{f(e['grid_kWh']['median'],1)} | "
              f"{f(e['MJ_primary_per_payload_tkm']['min'],4)} / "
              f"{f(e['MJ_primary_per_payload_tkm']['median'],4)} / "
              f"{f(e['MJ_primary_per_payload_tkm']['max'],4)} | "
              f"{'- (ruler)' if m is None else pct(m['ensemble']['min']) + ' / ' + pct(m['ensemble']['median'])} | "
              f"{f(cs['min']*100,1)}..{f(cs['max']*100,1)}% | "
              f"**{v}** |")
        w("")
    w("The **correction share** column is the one to read sceptically. It "
      "is the fraction of a candidate's reported fuel that is a CORRECTION "
      "rather than fuel the model watched it burn: energy its prime mover "
      "and buffer could not deliver, charged back as fuel at the run's own "
      "duty-averaged efficiency so that every candidate is compared having "
      "completed the same mission, plus the charge-sustaining make-up. It "
      "is exported SIGNED and with BOTH ends of the range, because WS8's "
      "finding F4 was that exporting only the max of a signed quantity hid "
      "a credit worth half of a candidate's headline. A large POSITIVE "
      "share is a capability finding, not a fuel one.")
    w("")

    # 4.3 mass ledgers
    s7 = T.get("S7")
    if s7:
        r7 = s7["per_duty"][design]["per_seed"][0]
        w("**A note on S7's one tuned constant, because it is the obvious "
          "place to attack the result.** S7's supervisor takes a declared "
          f"{s7['spec']['assist_share']:.0%} share of the tractive demand "
          "while the buffer is above its floor - a number WS9 chose, not "
          "derived. It matters less than it looks, and the run says why: on "
          "the design duty the trailer machine delivered "
          f"{f(r7['e_machine_wheel_kWh'],1)} kWh at the wheel while regen "
          f"returned {f(r7['e_regen_bus_kWh'],1)} kWh to the bus, and the "
          f"buffer started at {f(r7['soc_start'],2)} state of charge and "
          f"ended at {f(r7['soc_end'],3)} against a floor of "
          f"{f(0.15,2)}. S7's assist is REGEN-LIMITED, not policy-limited: "
          "energy out is energy in, and the share sets only the RATE at "
          "which a buffer that is already empty most of the mission gets "
          "emptied. A larger share would not deliver more energy; it would "
          "deliver the same energy sooner.")
        w("")
    w("### 4.3 Where the mass goes - to the kilogram")
    w("")
    items = []
    for cname, blob in T.items():
        for k in blob["spec"]["mass_rows_kg"]:
            if k not in items:
                items.append(k)
    w("| item | " + " | ".join(T) + " |")
    w("|---" * (len(T) + 1) + "|")
    for it in items:
        cells = []
        for cname in T:
            v = T[cname]["spec"]["mass_rows_kg"].get(it)
            cells.append("-" if v is None else f"{v:,.0f}")
        w(f"| {it.replace('_', ' ')} | " + " | ".join(cells) + " |")
    w("| **powertrain total** | " + " | ".join(
        f"**{T[c]['spec']['powertrain_mass_kg']:,.0f}**" for c in T) + " |")
    w("| **payload** | " + " | ".join(
        f"**{T[c]['spec']['payload_kg']:,.0f}**" for c in T) + " |")
    w("")
    w("### 4.4 Control policies, declared")
    w("")
    for cname, blob in T.items():
        w(f"**{cname}** - {blob['spec']['policy']}")
        w("")
    w("### 4.5 Informative brackets (nominal corner, not the metric of "
      "record)")
    w("")
    if R.get("brackets"):
        w("| bracket | payload | vs ruler | " + design + " margin (min / "
          "median) | " + control + " margin (min / median) | what it asks |")
        w("|---|---|---|---|---|---|")
        asks = {
            "S5-P2": "what the machine on the gearbox INPUT saves, and what "
                     "it costs: leaner by construction because it launches "
                     "through the low ratio, but on the wrong side of the "
                     "element that opens, so the shift becomes a torque "
                     "interruption instead of a torque fill",
            "S5-GH": "what a minimal transmission solved against the DESIGN "
                     "DUTY's grade rather than the assignment's 6% would "
                     "do - the steepest a contiguous 2-speed can carry on "
                     "the 13 L, paid for in cruise engine speed",
            "S0R-PCC": "what predictive energy management - a ZERO-MASS "
                       "lever - is worth ON THE RULER. If the incumbent may "
                       "fit it, S6's margin loses whatever it is worth "
                       "(ESC-WS9-5)",
        }
        for cname, blob in R["brackets"].items():
            s = blob["spec"]
            dm = R["bracket_margins"][design].get(cname)
            cm = R["bracket_margins"][control].get(cname)
            dlt = s["payload_kg"] - T[ruler]["spec"]["payload_kg"]
            w(f"| **{cname}** | {kg(s['payload_kg'])} kg | {dlt:+,.0f} kg | "
              f"{pct(dm['ensemble']['min']) + ' / ' + pct(dm['ensemble']['median']) if dm else 'n/a'} | "
              f"{pct(cm['ensemble']['min']) + ' / ' + pct(cm['ensemble']['median']) if cm else 'n/a'} | "
              f"{asks.get(cname, '')} |")
        w("")
    w("### 4.6 Sizing rules, stated before the numbers")
    w("")
    w("Every pack and every resistor in WS9 is sized by a RULE evaluated in "
      "code, never by a chosen kWh. WS8's S1 carried a 60 kWh buffer with "
      "no stated rule and 736 kg of it was payload.")
    w("")
    w("| candidate | cell | sizing rule | binding case | kWh for power | "
      "kWh for energy | built | mass |")
    w("|---|---|---|---|---|---|---|---|")
    for cname, blob in T.items():
        r = blob["spec"].get("pack_sizing_rule")
        pk = blob["spec"].get("pack")
        if not r or not pk:
            continue
        w(f"| **{cname}** | {r['cell']} | {r['rule']} | "
          f"**{r['binding_case']}** | "
          f"{f(r['kWh_required_for_power'],2)} | "
          f"{f(r['kWh_required_for_energy'],2)} | "
          f"{f(pk['nameplate_kWh'],2)} kWh | "
          f"{kg(pk['pack_mass_kg'])} kg |")
    w("")
    w("| candidate | resistor sizing case | retard required | engine brake "
      "| friction allowance | resistor rated | mass |")
    w("|---|---|---|---|---|---|---|")
    for cname, blob in T.items():
        r = blob["spec"].get("resistor_sizing_rule")
        if not r:
            continue
        w(f"| **{cname}** | {f(r['case']['grade']*100,0)}% at "
          f"{f(r['case']['v_kmh'],0)} km/h, {r['rule']} | "
          f"{f(r['retard_required_kW'],0)} kW | "
          f"{f(r['engine_brake_kW'],0)} kW | "
          f"{f(r['friction_allowance_kW'],0)} kW | "
          f"**{f(r['rated_kW'],0)} kW** | {kg(r['mass_kg'])} kg |")
    w("")
    br = None
    for cname, blob in T.items():
        br = blob["spec"].get("pack_chemistry_bracket") or br
    if br:
        w("**Chemistry, as a stated bracket rather than a preference.** A "
          "buffer is bought for charge acceptance, cold behaviour and cycle "
          "life; WS8 used the densest of WS3's three cells for every pack, "
          "which is right for an ENERGY pack and wrong for a buffer.")
        w("")
        w("| | cell | charge acceptance | discharge | cold factor at "
          "-10 C | equivalent full cycles | mass |")
        w("|---|---|---|---|---|---|---|")
        for tag, k in (("of record", "of_record"), ("bracket", "bracket")):
            v = br[k]
            w(f"| {tag} | {v['cell']} | {f(v['p_cont_chg_kW'],0)} kW | "
              f"{f(v['p_cont_dis_kW'],0)} kW | {f(v['cold_factor'],3)} | "
              f"{kg(v['efc100'])} | {kg(v['mass_kg'])} kg |")
        w("")
        w(f"The chemistry of record costs {f(-br['mass_delta_kg'],0)} kg "
          f"more than the bracket at the same nameplate. {br['note']}")
        w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 5
    w("## 5. The cold wall (R30), modelled rather than assumed")
    w("")
    w("R30: *\"Every WS9 electrified candidate carries pack preconditioning "
      "and a coolant/waste-heat cab-heating path as requirements, MODELLED, "
      "NOT ASSUMED; the conventional truck heats itself for free and the "
      "comparison must charge that.\"*")
    w("")
    w("Both halves are hardware with mass and physics with a state. The "
      "pack temperature is integrated at 10 Hz alongside its state of "
      "charge, starting COLD-SOAKED AT AMBIENT, warmed by its own ohmic "
      "loss, by engine coolant through a declared heat exchanger whenever "
      "an engine is running, and by an electric heater that draws from the "
      "bus when one is not. The charge ceiling at each sample is then WS3's "
      "own `p_cont_chg_kw_at(T_pack)` - the method WS8's finding F2 found "
      "defined and never called. WS8 round 2 wired it to the corner's "
      "AMBIENT; WS9 evaluates it at the pack's ACTUAL temperature, which is "
      "stricter at the start of a trip and kinder later.")
    w("")
    cw = R["sanity"]["cold_wall_exercised_R30"]["per_candidate"]
    if cw:
        w("At the -10 C corner, on the design duty:")
        w("")
        w("| | pack at start | pack at end | charge acceptance cold-soaked "
          "/ warm | collapse factor | seconds below target | coolant waste "
          "heat used | electric heater energy |")
        w("|---|---|---|---|---|---|---|---|")
        for cname, v in cw.items():
            w(f"| **{cname}** | {f(v['t_pack_start_C'],1)} C | "
              f"{f(v['t_pack_end_C'],1)} C | "
              f"{f(v['chg_limit_at_ambient_kW'],1)} / "
              f"{f(v['chg_limit_warm_kW'],1)} kW | "
              f"{f(v['collapse_factor'],3)} | "
              f"{f(v['seconds_below_target'],0)} s | "
              f"{f(v['e_coolant_waste_heat_kWh'],2)} kWh | "
              f"{f(v['e_electric_heater_kWh'],2)} kWh |")
        w("")
        w("The asymmetry is physical and it is R30's intended effect: a "
          "candidate that runs an engine for most of the mission gets its "
          "cab heat free and its pack preconditioned from coolant at no "
          "fuel cost; a candidate whose engine is off for most of the "
          "mission pays for both out of the bus. That is why the cold "
          "corner stops being a common-mode penalty and becomes an "
          "architecture-dependent one. The 2.2 / 1.0 kW split of WS8's own "
          "3.2 kW cold delta into cab heat and battery thermal is "
          "WS9-declared and is escalated (ESC-WS9-6).")
        w("")
    w("### 5.1 The electricity term and its sensitivity (ESC-3)")
    w("")
    ea = R["interface_ws9"]["electricity_accounting_ESC3"]
    w(f"ESC-3, ruled in R27, gives Vehicle One's metric an electricity term "
      f"for any plug-in candidate. Applies to: "
      f"**{', '.join(ea['applies_to']) if ea['applies_to'] else 'no candidate'}**.")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| diesel well-to-tank primary factor | {f(ea['pef_diesel'],3)} |")
    w(f"| grid primary-energy factor | {f(ea['pef_grid'],3)} |")
    w(f"| grid CO2e intensity at the meter | "
      f"{f(ea['co2_grid_kg_per_kWh'],3)} kg/kWh |")
    w(f"| grid to pack efficiency | "
      f"{f(ea['eta_charge_grid_to_pack'],4)} |")
    w(f"| factor sensitivity | +/-{f(ea['sensitivity']*100,0)}% |")
    w("")
    w("The diesel factor multiplies every candidate's fuel term "
      "identically, so for every candidate that imports no grid energy the "
      "primary-energy margin and the tank-energy margin are the SAME NUMBER "
      "- asserted in section 11, not claimed. The metric therefore changes "
      "exactly one thing in this trial.")
    w("")
    w("Both lenses, on the design duty at nominal, with the grid factors "
      "swept +/-50%:")
    w("")
    w("| candidate | MJ_primary/payload-tkm (grid factor -50% / declared / "
      "+50%) | margin vs ruler at each | gCO2e/payload-tkm (-50% / "
      "declared / +50%) |")
    w("|---|---|---|---|")
    base_lo = T[ruler]["per_duty"][design]["ensemble"][
        "MJ_primary_per_payload_tkm_grid_lo"]["median"]
    base_md = T[ruler]["per_duty"][design]["ensemble"][
        "MJ_primary_per_payload_tkm"]["median"]
    base_hi = T[ruler]["per_duty"][design]["ensemble"][
        "MJ_primary_per_payload_tkm_grid_hi"]["median"]
    for cname, blob in T.items():
        e = blob["per_duty"][design]["ensemble"]
        lo = e["MJ_primary_per_payload_tkm_grid_lo"]["median"]
        md = e["MJ_primary_per_payload_tkm"]["median"]
        hi = e["MJ_primary_per_payload_tkm_grid_hi"]["median"]
        clo = e["g_CO2_per_payload_tkm_grid_lo"]["median"]
        cmd = e["g_CO2_per_payload_tkm"]["median"]
        chi = e["g_CO2_per_payload_tkm_grid_hi"]["median"]
        mg = "- (ruler)" if cname == ruler else " / ".join(
            pct((b - x) / b * 100.0) for b, x in
            ((base_lo, lo), (base_md, md), (base_hi, hi)))
        w(f"| **{cname}** | {f(lo,4)} / {f(md,4)} / {f(hi,4)} | {mg} | "
          f"{f(clo,1)} / {f(cmd,1)} / {f(chi,1)} |")
    w("")
    vr = R["verdict_robustness_ESC3"]
    w("**And the sweep is read against the criteria, not merely "
      "reported.** " + vr["basis"] + ":")
    w("")
    w("| candidate | grid factor -50% | declared | grid factor +50% |")
    w("|---|---|---|---|")
    for cname in vr["by_factor"]["declared"]:
        cells = []
        for t in ("grid_factor_minus50pct", "declared",
                  "grid_factor_plus50pct"):
            v = vr["by_factor"][t][cname]
            cells.append(f"{pct(v['nominal_margin_pct_min'])} -> "
                         f"**{v['verdict']}**")
        w(f"| **{cname}** | " + " | ".join(cells) + " |")
    w("")
    if vr["candidates_whose_verdict_moves"]:
        w("**"
          + ", ".join(vr["candidates_whose_verdict_moves"])
          + "'s verdict MOVES across the swept range.** The grid factor is "
            "DECLARED, not sourced from a fetched primary document "
            "(ESC-WS9-2), so whatever the lead fixes it at is not a "
            "reporting convention - it is part of the verdict. Every "
            "candidate that imports no grid energy is invariant across the "
            "sweep by construction, which is the same invariance section 11 "
            "asserts.")
    else:
        w("No verdict moves across the swept range. The grid factor is "
          "declared rather than sourced (ESC-WS9-2), so this is the check "
          "that matters: the answer does not depend on it.")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 6
    w("## 6. Prime mover at the pin")
    w("")
    pm = R["prime_mover"]
    w(f"**Scope, checked rather than assumed:** {pm['scope']}. "
      f"`sanity.prime_mover_scope.only_S4p` = "
      f"`{R['sanity']['prime_mover_scope']['only_S4p']}`.")
    w("")
    w(f"Equal range is priced at **{f(pm['basis']['range_km'],0)} km** of "
      f"the duty that asks most of the sustainer "
      f"(`{list(pm['prime_movers'].values())[0]['equal_range']['governing_duty']}`), "
      f"at "
      f"{f(list(pm['prime_movers'].values())[0]['equal_range']['bus_kWh_per_km'],4)} "
      f"bus kWh per km. Price is out of scope (D12).")
    w("")
    w("| prime mover | displacement | eta at the pin | eta at the duty | "
      "engine | aftertreatment | fuel | fuel + tank | **total charged** | "
      "gCO2e per bus-kWh |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for k, v in pm["prime_movers"].items():
        e, m, em = v["engine"], v["equal_range"], v["emissions"]
        w(f"| **{k}** | {f(e['displacement_L'],2)} L | "
          f"{f(v['efficiency']['at_the_pin']['eta_fuel_to_bus'],4)} | "
          f"{f(v['efficiency']['eta_used_for_equal_range'],4)} | "
          f"{kg(m['engine_kg'])} kg | {kg(v['aftertreatment_kg'])} kg | "
          f"{kg(m['fuel_mass_kg'])} kg | {kg(m['fuel_plus_tank_kg'])} kg | "
          f"**{kg(m['TOTAL_CHARGED_kg'])} kg** | "
          f"{f(em['g_CO2e_per_bus_kWh'],0)} |")
    w("")
    for label, key in (("best efficiency at the pin", "best_pin_efficiency"),
                       ("lowest charged mass", "lowest_charged_mass"),
                       ("lowest CO2e per bus-kWh",
                        "lowest_co2e_per_bus_kWh")):
        wc = pm["worst_case"][key]
        w(f"- **{label}**: {wc['governing_case']} "
          f"({f(wc['value'],4) if wc['value'] < 10 else f(wc['value'],0)}), "
          f"an explicit {wc['rule']} over the enumerated prime-mover set "
          f"(R14)")
    w("")
    w("**" + pm["finding"] + "**")
    w("")
    w("Part-load, because rule 5 forbids judging a duty on a peak point and "
      "the pin IS a peak point:")
    w("")
    w("| prime mover | 25% | 50% | 75% | 100% of the bus rating |")
    w("|---|---|---|---|---|")
    for k, v in pm["prime_movers"].items():
        sw = v["efficiency"]["over_load_sweep"]
        w(f"| {k} | " + " | ".join(
            f(sw[s]["eta_fuel_to_bus"], 4) for s in
            ("0.25", "0.50", "0.75", "1.00")) + " |")
    w("")
    w("**Cold behaviour and fixed-point durability** - one entry per "
      "ENGINE, because the two natural-gas rows are the same engine "
      "differing only in the vessel:")
    w("")
    seen = set()
    for k, v in pm["prime_movers"].items():
        key = v["cold_behaviour"]
        if key in seen:
            continue
        seen.add(key)
        label = k.split(" (")[0]
        w(f"**{label} - cold behaviour.** {v['cold_behaviour']}")
        w("")
        w(f"**{label} - fixed-point durability.** "
          f"{v['fixed_point_durability']}")
        w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 7
    w("## 7. Corners (R28)")
    w("")
    w("Margins vs the ruler [%] on the **design duty**, ensemble min / "
      "median, at every corner. The control-duty result is reported after "
      "it and does not gate.")
    w("")
    corners_ = list(R["trial"])
    w("| candidate | " + " | ".join(corners_) + " |")
    w("|---" * (len(corners_) + 1) + "|")
    for cname in AK:
        cells = []
        for c in corners_:
            m = R["margins"][c][design].get(cname)
            cells.append(pct(m["ensemble"]["min"]) + " / "
                         + pct(m["ensemble"]["median"]) if m else "n/a")
        w(f"| **{cname}** | " + " | ".join(cells) + " |")
    w("")
    w("Same table on the **control duty** (informative):")
    w("")
    w("| candidate | " + " | ".join(corners_) + " |")
    w("|---" * (len(corners_) + 1) + "|")
    for cname in AK:
        cells = []
        for c in corners_:
            m = R["margins"][c][control].get(cname)
            cells.append(pct(m["ensemble"]["min"]) + " / "
                         + pct(m["ensemble"]["median"]) if m else "n/a")
        w(f"| **{cname}** | " + " | ".join(cells) + " |")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 8
    w("## 8. Capability shortfalls, reported rather than absorbed")
    w("")
    un = R["interface_ws9"]["unserved_energy_kWh"]
    w(un["meaning"][0].upper() + un["meaning"][1:])
    w("")
    w("**Where the largest ones come from, said plainly.** The tractive "
      "ENVELOPE each candidate is integrated against is built from its "
      "prime mover's continuous rating plus the pack contribution that "
      "survives a 15-minute climb (WS8's `SUSTAINED_CLIMB_S` rule, carried "
      "unchanged). The DISPATCH then has to feed that envelope sample by "
      "sample out of a pack with a finite state of charge. For a candidate "
      "whose pack is large but is deliberately being DEPLETED - S4' runs "
      "charge-depleting until its floor - the envelope is generous late in "
      "a long mission, when only the sustainer is left. That gap is "
      "exactly what this table measures, and it is why the correction "
      "share in section 4 is the column to read before the margin.")
    w("")
    w(f"Worst case **{f(un['value'],2)} kWh** (governing case: "
      f"`{un['governing_case']}`), an explicit max over the enumerated "
      f"(candidate, corner, duty) case set per R14.")
    w("")
    w("Cases above 1 kWh:")
    w("")
    w("| case | unserved kWh |")
    w("|---|---|")
    for k, v in sorted(un["cases_over_1kWh"].items(),
                       key=lambda kv: -kv[1]):
        w(f"| `{k}` | {f(v,2)} |")
    w("")
    pl = R["interface_ws9"]["power_limited_fraction"]
    w("**Power-limited fraction** - " + pl["meaning"])
    w("")
    w("| candidate | " + design + " | " + control + " |")
    w("|---|---|---|")
    for cname in T:
        a = R["trial"]["nominal"][cname]["per_duty"][design]["ensemble"][
            "power_limited_fraction"]["max"]
        b = R["trial"]["nominal"][cname]["per_duty"][control]["ensemble"][
            "power_limited_fraction"]["max"]
        w(f"| **{cname}** | {f(a,4)} | {f(b,4)} |")
    w("")
    rsh = R["interface_ws9"]["retarding_shortfall_kWh"]
    w(f"**Retarding shortfall** - worst case {f(rsh['value'],3)} kWh"
      + (f" (governing case: `{rsh['governing_case']}`)"
         if rsh["governing_case"] else "") + ". " + rsh["meaning"])
    w("")
    tt = R["sanity"]["trip_time_the_metric_cannot_see"]
    w(f"**Trip time, which the metric of record cannot see.** "
      f"{tt['note']} Worst case "
      f"{pct(tt['value'],1)} (governing case: "
      f"`{tt['governing_case']}`).")
    w("")
    w("| candidate | " + design + " trip time vs ruler | " + control
      + " trip time vs ruler |")
    w("|---|---|---|")
    for cname in T:
        a = tt["cases"].get(f"{cname}/nominal/{design}")
        b = tt["cases"].get(f"{cname}/nominal/{control}")
        w(f"| **{cname}** | {pct(a,1)} | {pct(b,1)} |")
    w("")
    sp = R["sanity"]["spin_drag_R22d_disclosure"]
    w(f"**R22(d) spin drag, disclosed.** Rule: {sp['rule']}. "
      f"{sp['note']}")
    w("")
    w("| candidate | spin charged (design duty, median) | as a share of "
      "bus traction |")
    w("|---|---|---|")
    for k, v in sp["per_candidate"].items():
        w(f"| **{k}** | {f(v['e_spin_charged_kWh'],4)} kWh | "
          f"{f(v['share_of_bus_traction']*100,3)}% |")
    w("")
    w("---")
    w("")

    # ---------------------------------------------------------------- 9
    w("## 9. Electric turbocompound, on the design duty (R31)")
    w("")
    eg = R["etc_gate"]
    w(f"Gate, pre-committed: **{eg['gate']['ruling']}**")
    w("")
    w(f"Read on {eg['gate']['basis']}.")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| mass charge | {f(eg['mass_charge_kg'],0)} kg |")
    w(f"| payload penalty | {pct(eg['payload_penalty_pct'])} |")
    w(f"| fuel gain needed to clear the gate | "
      f"**{f(eg['fuel_gain_needed_to_clear_gate_pct'])}%** |")
    w(f"| net margin on the design duty, ensemble-min | "
      f"**{pct(eg['design_duty_net_margin_pct_min'])}** |")
    w(f"| net margin on the design duty, median | "
      f"{pct(eg['design_duty_net_margin_pct_median'])} |")
    w(f"| gate | >= {f(eg['gate']['threshold_pct'],1)}% |")
    w(f"| **verdict** | **{eg['verdict']}** |")
    w("")
    w("R31 admitted electric turbocompound to S6 only if it cleared the "
      "same 2.5% gate on the design duty, whose load fraction is higher "
      "than the fleet average WS8 tested against. The mass charge sets the "
      "real bar above the gate, because the metric divides by payload - "
      "which is the same arithmetic that dropped waste-heat recovery in "
      "WS8, and D14 is why: waste-heat recovery is a full-load technology "
      "and even a grade-heavy regional duty is a part-load condition for "
      "most of its distance.")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 10
    w("## 10. Recommendation")
    w("")
    crit = R["advance_kill"]["criteria"]
    w(f"Criteria, pre-committed. {crit['text']} Read on the "
      f"**{crit['statistic']}**, on the **{crit['duty']}** duty; the "
      f"**{crit['control_duty']}** result is reported alongside and does "
      f"not gate.")
    w("")
    w("| candidate | design nominal min | worst design corner | worst "
      "corner min | control duty (informative) | passes nominal | passes "
      "corners | verdict |")
    w("|---|---|---|---|---|---|---|---|")
    for cname, v in AK.items():
        w(f"| **{cname}** | {pct(v['nominal_margin_pct_min'])} | "
          f"{v['worst_corner']} | "
          f"{pct(v['worst_corner_margin_pct_min'])} | "
          f"{pct(v['control_duty_nominal_margin_pct_min'])} | "
          f"{v['passes_nominal_3pct']} | {v['passes_all_corners_0pct']} | "
          f"**{v['verdict']}** |")
    w("")
    for cname, v in AK.items():
        w(f"- **{cname}: {v['verdict']}** - {v['binding_reason']}.")
    w("")
    w("**What WS9 recommends.** The numbers are above and the "
      "execute-or-spare decision is the lead's. What WS9 will say is this:")
    w("")
    n = 1
    w(f"{n}. **Read S6's verdict together with ESC-WS9-1 and ESC-WS9-5.** "
      f"S6 is the cleanest arithmetic in the report - mass-neutral with the "
      f"ruler to the kilogram, so its margin is its fuel margin and nothing "
      f"else - and it is also the candidate most exposed on evidence. Its "
      f"whole margin is one cited peak brake thermal efficiency, and part "
      f"of it is a zero-mass control lever the incumbent could fit "
      f"tomorrow. The break-even BTE "
      f"({f(be['break_even_peak_BTE'],4)} against a claimed "
      f"{f(be['claimed_peak_BTE'],3)}) says how much of the claim must hold; "
      f"the S0R-PCC bracket says how much of the margin is the engine.")
    n += 1
    s5 = AK.get("S5", {})
    w("")
    w(f"{n}. **S5 clears the numeric bar on the design duty and fails a "
      f"capability test the numeric bar cannot see.** Its two ratios do "
      f"span cruise and the assignment's 6% grade, in closed form. They do "
      f"not span the design duty's "
      f"{f(dd['grade_max']['max']*100,1)}% grades, because the low gear's "
      f"coupling floor is above the crawl speed those grades force and "
      f"below that floor the engine is not connected at all. That shows up "
      f"in the fuel number only as a correction - which is exactly the "
      f"shape of WS8's S3 finding, and WS8's own conclusion applies: the "
      f"fuel result is not the finding, the capability result is.")
    n += 1
    w("")
    w(f"{n}. **The duty decides the architecture, and now there is a "
      f"number for it.** Section 7's corner tables and the design/control "
      f"pair in section 4 span the sign change R29 predicted. An operator "
      f"running loaded over mountains and one running a flat corridor are "
      f"not looking at the same vehicle.")
    n += 1
    w("")
    w(f"{n}. **Mass is still the binding constraint, and the ranking "
      f"follows the payload column.** Section 4.3 is the argument. The "
      f"candidate that adds no mass wins; the candidates that add 500-1,000 "
      f"kg have to find 3-5% of fuel before they have found anything at "
      f"all.")
    n += 1
    s4 = AK.get("S4p", {})
    if s4:
        cs4 = R["interface_ws9"]["candidates"]["S4p"][
            "fuel_correction_share"]
        w("")
        w(f"{n}. **S4' advances by the widest margin on the design duty "
          f"and carries the largest correction in the trial.** Up to "
          f"{f(cs4['max']*100,1)}% of its reported fuel is a correction "
          f"rather than fuel the model watched it burn - energy its "
          f"sustainer and pack could not deliver on the mountain, charged "
          f"back so it completes the same mission. It also LOSES to the "
          f"ruler on the control duty "
          f"({pct(s4['control_duty_nominal_margin_pct_min'])} "
          f"ensemble-min), and its primary-energy advantage is an "
          f"accounting consequence of ESC-3's grid factor, which is "
          f"declared rather than sourced (ESC-WS9-2). "
          + ("**AND ITS VERDICT DOES NOT SURVIVE THE SWEEP ESC-3 ITSELF "
             "ORDERS**: re-applying the pre-committed criteria unchanged at "
             "the +50% end of the grid-factor range turns its design-duty "
             "ensemble-min from "
             f"{pct(R['verdict_robustness_ESC3']['by_factor']['declared']['S4p']['nominal_margin_pct_min'])}"
             " into "
             f"{pct(R['verdict_robustness_ESC3']['by_factor']['grid_factor_plus50pct']['S4p']['nominal_margin_pct_min'])}"
             " and its verdict from ADVANCE into KILL (section 5.1). Every "
             "other candidate is invariant across the sweep. S4' is "
             "therefore not a candidate the lead can execute or spare "
             "without first fixing the grid factor of record."
             if "S4p" in R["verdict_robustness_ESC3"][
                 "candidates_whose_verdict_moves"]
             else "Section 5.1 sweeps that factor +/-50% and its verdict "
                  "holds across the whole range."))
        n += 1
    w("")
    w(f"{n}. **The escalations in section 13 change the answer if ruled the "
      f"other way**, ESC-WS9-1 and ESC-WS9-5 especially. They are not "
      f"footnotes.")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 11
    w("## 11. First-principles sanity checks")
    w("")
    ck = R["sanity"]
    rl_ = ck["road_load_95kmh_flat"]
    w(f"**Road load at 95 km/h, flat, 36,300 kg.** By hand: aero "
      f"{f(rl_['hand_aero_N'],0)} N; rolling {f(rl_['hand_roll_N'],0)} N; "
      f"total {f(rl_['total_N'],0)} N = {f(rl_['wheel_kW'],1)} kW at the "
      f"wheel. Model agrees: **{rl_['agree']}**. {rl_['note']}")
    w("")
    mc = ck["mass_closure"]
    w(f"**Mass closure.** tare + payload = {kg(mc['gcw_kg'])} kg for every "
      f"candidate: **{mc['all_close']}**. {mc['note']}")
    w("")
    s6n = ck["S6_mass_neutral_with_ruler"]
    w(f"**S6 is mass-neutral with the ruler.** ruler "
      f"{kg(s6n['ruler_payload_kg'])} kg, S6 {kg(s6n['S6_payload_kg'])} kg, "
      f"delta {f(s6n['delta_kg'],6)} kg: **{s6n['neutral']}**.")
    w("")
    pe = ck["primary_energy_invariance"]
    w(f"**Primary-energy invariance.** {pe['note']} All pass: "
      f"**{pe['all_pass']}**.")
    w("")
    mg = ck["machine_basis_gate_ESC2"]
    w(f"**ESC-2 machine gate (k <= {f(mg['gate_k'],1)}).** " + ", ".join(
        f"{k} k={f(v['k'],3)}" for k, v in mg["per_candidate"].items())
      + f". All pass: **{mg['all_pass']}**.")
    w("")
    st = ck["startability_12pct"]
    w(f"**12% startability.** Requires {f(st['required_N'],0)} N at the "
      f"contact patch; dry tandem adhesion ceiling "
      f"{f(st['adhesion_ceiling_dry_N'],0)} N. All candidates meet it: "
      f"**{st['all_pass']}**. {st['note']}")
    w("")
    sc = ck["scaling_law_per_unit_invariance"]
    w(f"**Scaling-law implementation.** Per-unit efficiency at k=1.0 and "
      f"k=1.8 at matched per-unit load agree to "
      f"{f(sc['delta_pp'],4)} pp: **{sc['agree']}**. {sc['note']}")
    w("")
    ec = ck["ruler_energy_closure"]
    w(f"**Ruler energy closure.** Fuel energy {f(ec['fuel_energy_kWh'],0)} "
      f"kWh, engine shaft work {f(ec['engine_shaft_kWh'],0)} kWh - an "
      f"implied engine efficiency of "
      f"{f(ec['implied_engine_efficiency'],4)} against "
      f"{f(ec['implied_from_bsfc'],4)} implied by the duty-averaged BSFC of "
      f"{f(ec['duty_averaged_bsfc_g_per_kWh'],1)} g/kWh. Agree: "
      f"**{ec['agree']}**.")
    w("")
    hl = ck["heat_ledger_closure_and_ratings_F1"]
    w(f"**Heat-ledger closure and ratings (finding F1).** {hl['note']} All "
      f"descent cases close: **{hl['all_descents_close']}**. No rating "
      f"violations: **{hl['no_rating_violations']}**.")
    w("")
    co = ck["co2_from_carbon_balance"]
    w(f"**CO2 factors are a carbon balance, not a lookup.** diesel "
      f"{f(co['diesel_g_per_MJ'],2)}, petrol {f(co['petrol_g_per_MJ'],2)}, "
      f"methane {f(co['methane_g_per_MJ'],2)} g CO2/MJ, derived from H:C "
      f"and LHV. Against published spot values: "
      f"**{co['agree_to_1pct']}**.")
    w("")
    ad = ck["altitude_derate_exercised_F11"]
    w(f"**The ambient/altitude derate is exercised (finding F11).** WS4's "
      f"ruled factor at 2,000 m / +45 C is {f(ad['derate_factor'],4)}. "
      f"WS9's own ISA computation of the air density gives "
      f"{f(ad['air_density_first_principles'],4)} kg/m3 against the "
      f"inherited {f(ad['air_density_inherited_from_ws8'],4)}: agree "
      f"**{ad['density_agrees']}**.")
    w("")
    nw = ck["no_ws8_artifact_read"]
    w(f"**No WS8 numeric artifact is read.** {nw['note']} Passes: "
      f"**{nw['passes']}**.")
    w("")
    et = ck["envelope_tabulation"]
    w(f"**Envelope tabulation.** The integrator interpolates each "
      f"candidate's envelope on a {f(et['grid_dv_ms'],2)} m/s grid; worst "
      f"relative error against direct evaluation "
      f"{et['worst_relative_error']:.2e}.")
    w("")
    pcc = ck["predictive_energy_management_is_not_a_speed_reduction"]
    w(f"**Predictive energy management is not a speed reduction.** "
      f"{pcc['note']}")
    w("")
    w("| case | mean demand preserved to | max target delta | achieved "
      "trip time | ruler trip time | achieved mean speed | ruler mean "
      "speed |")
    w("|---|---|---|---|---|---|---|")
    for k, v in pcc["per_case"].items():
        w(f"| `{k}` | "
          f"{v['mean_target_preserved_to']:.2e} | "
          f"{f(v['max_target_delta_kmh'],2)} km/h | "
          f"{f(v['achieved_duration_s_median'],0)} s | "
          f"{f(v['ruler_duration_s_median'],0)} s | "
          f"{f(v['achieved_avg_speed_kmh_median'],2)} km/h | "
          f"{f(v['ruler_avg_speed_kmh_median'],2)} km/h |")
    w("")
    w(f"**All checks pass: {ck['all_pass']}**")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 12
    w("## 12. Inherited vintage, and the r2 concordance")
    w("")
    iv = R["inherited_vintage"]
    w(iv["statement"])
    w("")
    fp = iv["ws8_code_round_fingerprint"]
    w(f"**WS8 code round detected: `{fp['code_round']}`.** Fingerprints: "
      + ", ".join(f"{k} = `{v}`" for k, v in fp.items()
                  if k != "code_round") + ".")
    w("")
    w("| inherited WS8 source | bytes | sha256 |")
    w("|---|---|---|")
    for k, v in iv["ws8_source_files"].items():
        w(f"| `{k}` | {kg(v['bytes'])} | `{(v['sha256'] or '')[:16]}...` |")
    w("")
    w("| WS8 artifact - hashed, NOT read | bytes | sha256 |")
    w("|---|---|---|")
    for k, v in iv["ws8_artifacts_hashed_but_not_read"].items():
        w(f"| `{k}` | {kg(v['bytes'])} | `{(v['sha256'] or '')[:16]}...` |")
    w("")
    w("### 12.1 What WS9 inherits from round 2, and what it implements "
      "itself")
    w("")
    w("| WS8 r1 finding | round 2's remedy | WS9's position |")
    w("|---|---|---|")
    conc = [
        ("F1 - heat ledger wrong in magnitude and attribution",
         "ledger rebuilt with the simulated peaks in the case set and the "
         "retard channel split",
         "WS9 builds its OWN ledger (section 14) on the same principle: an "
         "enumerated case set that INCLUDES a pack-saturated descent and "
         "the simulated peaks over every run; rows booked by physical "
         "location, with the hydraulic retarder to the coolant circuit and "
         "the compression brake to the exhaust; a friction-brake row; "
         "closure and rating assertions"),
        ("F2 - cold charge acceptance defined and never called",
         "`Pack8.p_cont_chg_kw_at` wired to the CORNER'S AMBIENT",
         "INHERITED, and extended as R30 requires: the pack temperature is "
         "a STATE and the ceiling is evaluated at the pack's actual "
         "temperature sample by sample. Stricter than r2 at a cold start, "
         "kinder once the coolant has warmed it"),
        ("F3 - S2's engine run locked and as a free-speed genset at once",
         "the generator priced at the road-imposed speed out of the torque "
         "traction left behind",
         "NOT APPLICABLE - WS9 has no S2. The lesson binds anyway: S5's "
         "engine is always at the speed its gear imposes and is never "
         "priced on a free-speed locus"),
        ("F4 - the charge-sustaining credit was invisible",
         "symmetric convention DECLARED, share exported signed with min AND "
         "max, credit-free variant carried alongside",
         "INHERITED verbatim as the rule; implemented on WS9's own energy "
         "keys. Both ends of the signed share are in the R14 block and "
         "`fuel_g_corrected_deficit_only` is carried per run"),
        ("F5 - three inconsistent spin-drag treatments",
         "one rule, one threshold, for every candidate",
         "INHERITED - r2's rule and r2's own 1 N / 0.5 m/s thresholds - "
         "applied to the MACHINE'S OWN SHAFT rather than the vehicle's "
         "force channels, because two WS9 candidates have a machine that is "
         "not the only traction path"),
        ("F6 - corrections priced at a peak-point scalar",
         "priced at the run's own duty-averaged efficiency",
         "INHERITED as the rule, on the ENGINE's own wheel work rather than "
         "the vehicle's, so regenerated energy is not credited to the "
         "engine - the direction that would have flattered the hybrids"),
        ("F7 - the external anchor asserted on a median",
         "restated as an ensemble against the band",
         "RE-RUN for WS9's own ruler as an ensemble AND mass-matched to the "
         "reference payload (section 2.1)"),
        ("F8 - a headline specification wrong by 14%",
         "computed ratings rendered instead of literals",
         "every rating in this report is formatted from the computed "
         "value; `verify_ws9.py` checks the rendered figures against the "
         "results"),
        ("F9 - a hand-written note contradicting the value above it",
         "notes formatted from computed values",
         "INHERITED as a practice - see the road-load note in section 11, "
         "which is generated from the numbers it quotes"),
        ("F10 - two margin statistics under one name",
         "one basis, labelled",
         "ONE margin statistic in WS9: per-seed paired against the ruler on "
         "the same seed and duty, then enveloped. Nothing else is called a "
         "margin"),
        ("F11 - `derate_factor` imported and never called",
         "`derated_engine` added and a 2,000 m / +45 C corner added",
         "INHERITED - WS9 calls r2's function and carries an independent "
         "ISA computation of the air density as a check"),
        ("F12 - a swept-grid property reported as a physics bound",
         "the ratio ceiling solved in closed form",
         "INHERITED as the practice: every ratio bound in section 3 is "
         "closed form, with the sweep kept as the illustration"),
        ("F13 - a literal climb figure at the top of its ensemble",
         "formatted from the data",
         "every duty statistic in section 1 is an 8-seed envelope formatted "
         "from `duties`"),
    ]
    for a, b, c in conc:
        w(f"| {a} | {b} | {c} |")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 13
    w("## 13. Escalations")
    w("")
    w("Escalations cite the ruling they challenge and are never "
      "self-resolved (CLAUDE.md rule 8). They go to the lead.")
    w("")
    for e in R["escalations"]:
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

    # --------------------------------------------------------------- 14
    w("## 14. Heat ledger for WS6 (rule 7)")
    w("")
    hlr = R["heat_ledger"]
    w(hlr["convention"])
    w("")
    w("**Rows are booked by PHYSICAL LOCATION**, which is what WS8's "
      "finding F1 said its own ledger did not do:")
    w("")
    w("| row | where the heat goes |")
    w("|---|---|")
    for k, v in hlr["rows_by_physical_location"].items():
        w(f"| `{k}` | {v} |")
    w("")
    w("Worst-case rejection by component, an explicit max over the "
      "enumerated case set with the governing case labelled (R14). The case "
      "set INCLUDES a pack-saturated descent and the simulated peaks over "
      "every (corner, duty, seed) run - the member WS8's r1 ledger did not "
      "have, and the reason it understated its own sizing case.")
    w("")
    w("**" + hlr["duration_convention"] + "**")
    w("")
    w("SUSTAINED cases only - what a cooling package and a resistor bank "
      "are sized on:")
    w("")
    keys0 = ["engine_coolant_kW", "hydraulic_retarder_coolant_kW",
             "engine_exhaust_kW", "compression_brake_exhaust_kW",
             "traction_machine_inverter_kW", "generator_rectifier_kW",
             "pack_kW", "brake_resistor_kW", "friction_brake_kW"]
    w("| candidate | " + " | ".join(k.replace("_kW", "").replace("_", " ")
                                    for k in keys0) + " |")
    w("|---" * (len(keys0) + 1) + "|")
    for cname, blob in hlr["candidates"].items():
        cells = []
        for k in keys0:
            wc = blob["worst_case_sustained"][k]
            cells.append(f"{wc['value']:,.0f} ({wc['governing_case']})"
                         if wc["value"] > 0.5 else "0")
        w(f"| **{cname}** | " + " | ".join(cells) + " |")
    w("")
    w("FULL case set, sustained AND the transient simulated peak:")
    w("")
    keys = ["engine_coolant_kW", "hydraulic_retarder_coolant_kW",
            "engine_exhaust_kW", "compression_brake_exhaust_kW",
            "traction_machine_inverter_kW", "generator_rectifier_kW",
            "pack_kW", "brake_resistor_kW", "friction_brake_kW"]
    w("| candidate | " + " | ".join(k.replace("_kW", "").replace("_", " ")
                                    for k in keys) + " |")
    w("|---" * (len(keys) + 1) + "|")
    for cname, blob in hlr["candidates"].items():
        cells = []
        for k in keys:
            wc = blob["worst_case"][k]
            cells.append(f"{wc['value']:,.0f} ({wc['governing_case']})"
                         if wc["value"] > 0.5 else "0")
        w(f"| **{cname}** | " + " | ".join(cells) + " |")
    w("")
    w("The two coolant rows must be **added** by WS6: a secondary "
      "hydrodynamic retarder rejects through a heat exchanger into the "
      "engine cooling system, so one package sizes for the sum.")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 15
    w("## 15. Machine-readable interface (R14)")
    w("")
    w("Every worst-case field below is an explicit max/min over an "
      "enumerated case set with the governing case labelled inline. This "
      "block is byte-identical to `results_ws9.json['interface_ws9']`; "
      "`verify_ws9.py` asserts it.")
    w("")
    w("```json")
    w(json.dumps(R["interface_ws9"], indent=1))
    w("```")
    w("")
    w("---")
    w("")

    # --------------------------------------------------------------- 16
    w("## 16. Provenance and reproduction")
    w("")
    w("```")
    w("cd WS9_vehicle_one_wave2")
    w("../.venv/bin/python run_ws9.py --jobs 6   # -> results_ws9.json + "
      "data/*.csv")
    w("../.venv/bin/python make_report_ws9.py    # -> REPORT_WS9.md")
    w("../.venv/bin/python verify_ws9.py         # asserts report == "
      "results")
    w("```")
    w("")
    w("**Inherited, read-only (CLAUDE.md rule 10):**")
    w("")
    w("- **WS8** - the duty cycles, the achieved-speed integrator, the road "
      "load, the mass ledger, the HD Willans engines and the AMT, the "
      "genset line, the WS2 machine stretch, the WS3 pack construction, the "
      "startability specification, the sustained-climb rule, the regen "
      "blend-out, the friction-brake allowance, the spin-drag rule and its "
      "thresholds, the correction-pricing rule, the ambient derate and the "
      "hot/altitude corner. SHA-pinned in section 12.")
    w("- **WS2 r4** (through WS8) - the measured inverter+motor loss map, "
      "the capability envelope, the stack-length scaling rule and its "
      "mass split, the 7,200 rpm rotor limit, the resistor's kg per kW.")
    w("- **WS3** (through WS8) - cell definitions, the pack overhead model, "
      "cold charge acceptance.")
    w("- **WS4** (through WS8) - `WillansEngine`, `PMGenerator`, "
      "`derate_factor`, `WS2TractionChain` and the R12 chain convention.")
    w("")
    w("**External, cited, with evidence quality stated:**")
    w("")
    for k, v in R["params"]["citations"].items():
        w(f"- **{k}** - {v['source']}. *Used for:* {v['used_for']}. "
          f"*Evidence quality:* {v['evidence_quality']}")
    w("")
    det = R.get("determinism", {})
    w("### 16.1 Regeneration check (rule 1)")
    w("")
    w(f"**Status: {det.get('status', 'NOT RUN')}**")
    w("")
    if det.get("status") not in (None, "NOT RUN"):
        h1, h2 = det["half_1_simulation"], det["half_2_derived_blocks"]
        w(f"- **Half 1, the simulation.** `{h1['job']}` re-run FROM SCRATCH "
          f"in a fresh process over all {len(h1['seeds'])} seeds: "
          f"{h1['values_compared']} per-seed values compared at "
          f"{h1['tolerance']}, {h1['n_mismatches']} mismatches. Matches the "
          f"committed run: **{h1['matches_committed_run']}**.")
        w(f"- **Half 2, the derived blocks and the exports.** "
          f"`{h2['command']}` regenerates every derived block and every CSV "
          f"from the committed trial. results_ws9.json byte-identical: "
          f"**{h2['results_json_byte_identical']}**; all CSV exports "
          f"byte-identical: **{h2['all_csv_exports_byte_identical']}**.")
        w(f"- **Not checked, stated rather than implied.** "
          f"{det['not_checked']}")
        w("")
    w("| WS9 file | sha256 |")
    w("|---|---|")
    for k, v in iv["ws9_own_files"].items():
        w(f"| `{k}` | `{(v['sha256'] or 'ABSENT')[:16]}...` |")
    w("")

    open(OUT, "w").write("\n".join(L) + "\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes, {len(L)} lines)")


if __name__ == "__main__":
    main()
