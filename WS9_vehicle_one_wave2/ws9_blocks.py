"""
Project Volt - WS9
The derived blocks: first-principles sanity checks, escalations, the R14
machine-readable interface, the headline, and the CSV exports.

Kept in their own module so that `run_ws9.py --from-checkpoint` can rebuild
every one of them against a saved trial without paying for the simulation
again - the same posture WS8 takes, and the reason a defect in a reporting
block cannot cost an hour.
"""
import os
import sys
from collections import OrderedDict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_candidates as CD8
import ws8_electric as EL8
import ws8_engine as EN8
import ws8_physics as PH8
import ws8_whr as WHR8
from ws8_params import VEH, ADH, AUX, DL, ML, G, LHV_KJ_PER_G

import ws9_candidates as CD9
import ws9_concordance as CN9
import ws9_corrections as CR9
import ws9_duty as DY9
import ws9_engines as E9
import ws9_fuels as F9
import ws9_params as P9
import ws9_walls as W9


# =====================================================================
#  first-principles sanity checks
# =====================================================================
def sanity_checks(R, ns):
    """Independent arithmetic against the model, not a re-run of it.

    Every note that quotes a number is FORMATTED FROM THE COMPUTED VALUE
    (WS8 finding F9: a hand-written note inside the data file contradicted
    the value two lines above it, and no checker could catch it because the
    wrong figure lived inside the record as prose).  [R2-IMPL F9]
    """
    ck = OrderedDict()
    design, control = DY9.DESIGN_DUTY, DY9.CONTROL_DUTY

    # --- 1. closed-form road load ------------------------------------
    v = 95.0 / 3.6
    f_aero = 0.5 * VEH.rho_air * VEH.CdA * v * v
    f_roll = VEH.Crr * VEH.m_gcw * G
    f_model, fa, fr, fg = PH8.road_load_force(np.array([v]), 0.0, VEH.m_gcw)
    ck["road_load_95kmh_flat"] = dict(
        hand_aero_N=f_aero, model_aero_N=float(fa[0]),
        hand_roll_N=f_roll, model_roll_N=float(fr[0]),
        total_N=float(f_model[0]), wheel_kW=float(f_model[0]) * v / 1e3,
        agree=bool(abs(f_aero - float(fa[0])) < 1.0
                   and abs(f_roll - float(fr[0])) < 1.0),
        note=(f"{float(fa[0]):.0f} N of aero and {float(fr[0]):.0f} N of "
              f"rolling at 36.3 t and 95 km/h is the whole line-haul "
              f"problem in two numbers: the air is already the bigger bill, "
              f"which is why every candidate here wins or loses on "
              f"driveline efficiency and mass, not on regenerative braking. "
              f"[formatted from the computed values, per F9]"))

    # --- 2. the two walls, closed form vs sweep -----------------------
    tw = R["two_walls"]
    ck["two_walls_closed_form"] = dict(
        wall1_ratio_ceiling=W9.ratio_ceiling(105.0 / 3.6,
                                             P9.DOGBOX.rpm_ceiling),
        ws8_r1_swept_grid_value=3.60,
        note=("WS8 r1 reported the single-ratio ceiling as 3.60 because "
              "that was the largest entry in its swept grid; the physics "
              "bound is "
              f"{W9.ratio_ceiling(105.0/3.6, P9.DOGBOX.rpm_ceiling):.4f} "
              "and WS9 solves it (F12)"),
        two_speed_feasible={k: v["solve"]["feasible"]
                            for k, v in tw["two_speed_solve"].items()},
        two_speed_holds_6pct={k: v["sweep"]["holds_6pct"]
                              for k, v in tw["two_speed_solve"].items()},
        two_speed_band_contiguous={
            k: v["sweep"]["engine_band_is_contiguous"]
            for k, v in tw["two_speed_solve"].items()},
        single_ratio_feasible={
            k: v["single_ratio_feasible"]
            for k, v in tw["single_ratio_closed_form"].items()},
        all_pass=bool(all(v["solve"]["feasible"]
                          and v["sweep"]["holds_6pct"]
                          and v["sweep"]["engine_band_is_contiguous"]
                          for v in tw["two_speed_solve"].values())
                      and not any(v["single_ratio_feasible"] for v in
                                  tw["single_ratio_closed_form"].values())))

    # --- 3. mass closure ---------------------------------------------
    rows = {}
    for cname, blob in R["trial"]["nominal"].items():
        s = blob["spec"]
        rows[cname] = dict(
            tare_kg=s["tare_common_kg"] + s["powertrain_mass_kg"],
            payload_kg=s["payload_kg"],
            sum_kg=s["tare_common_kg"] + s["powertrain_mass_kg"]
            + s["payload_kg"],
            closes=bool(abs(s["tare_common_kg"] + s["powertrain_mass_kg"]
                            + s["payload_kg"] - VEH.m_gcw) < 1e-6))
    ck["mass_closure"] = dict(
        gcw_kg=VEH.m_gcw, per_candidate=rows,
        all_close=bool(all(r["closes"] for r in rows.values())),
        note="at fixed GCW, powertrain mass IS payload - that is WALL 2 and "
             "it is the denominator of the metric of record")

    # --- 4. S6 is mass-neutral with the ruler, to the kilogram --------
    p0 = R["trial"]["nominal"][CD9.RULER]["spec"]["payload_kg"]
    p6 = R["trial"]["nominal"]["S6"]["spec"]["payload_kg"]
    ck["S6_mass_neutral_with_ruler"] = dict(
        ruler_payload_kg=p0, S6_payload_kg=p6, delta_kg=p6 - p0,
        neutral=bool(abs(p6 - p0) < 1e-9),
        note=("S6 carries the same AMT, the same retarder, the same axles, "
              "the same fuel and the same aftertreatment; its engine is "
              "charged the four-stroke's mass because the cited source "
              "states none. So on a metric that divides by payload its "
              "margin IS its fuel margin, with no payload term at all."))

    # --- 5. primary-energy invariance for diesel-only candidates ------
    inv = {}
    for cname in R["margins"]["nominal"][design]:
        a = R["margins"]["nominal"][design][cname]["ensemble"]["median"]
        b = (R["margins_tank_energy"]["nominal"][design][cname]["ensemble"]
             ["median"])
        grid = R["trial"]["nominal"][cname]["per_duty"][design][
            "ensemble"]["grid_kWh"]["median"] or 0.0
        inv[cname] = dict(primary_margin_pct=a, tank_margin_pct=b,
                          abs_diff_pp=abs(a - b), grid_kWh=grid,
                          diesel_only=bool(grid <= 1e-9),
                          invariant=bool(grid > 1e-9 or abs(a - b) < 1e-9))
    ck["primary_energy_invariance"] = dict(
        per_candidate=inv,
        all_pass=bool(all(v["invariant"] for v in inv.values())),
        note=("the diesel well-to-tank factor multiplies every candidate's "
              "fuel term identically, so for every candidate that imports "
              "no grid energy the primary-energy margin and the "
              "tank-energy margin are the same number. Asserted, not "
              "claimed - and it is what makes the metric change exactly "
              "one thing in this trial."))

    # --- 6. ESC-2 machine gate ----------------------------------------
    gates = {}
    for cname, blob in R["trial"]["nominal"].items():
        g = blob["spec"].get("machine_gate_ESC2")
        if g:
            gates[cname] = dict(k=g["k"], n=g["n_machines"],
                                passes=g["passes"])
    for cname, blob in R.get("brackets", {}).items():
        g = blob["spec"].get("machine_gate_ESC2")
        if g:
            gates[cname] = dict(k=g["k"], n=g["n_machines"],
                                passes=g["passes"])
    ck["machine_basis_gate_ESC2"] = dict(
        gate_k=P9.MACHINE_STRETCH_GATE_K, per_candidate=gates,
        all_pass=bool(all(v["passes"] for v in gates.values())),
        note=("ESC-2 as ruled in R27. WS8's S3 axle-B machine sat at "
              "k=3.60 and would have failed this; no WS9 machine may, and "
              "where a design would have needed more the DESIGN was "
              "changed rather than the gate."))

    # --- 7. the design duty is invariant under the grade_heavy corner --
    idd = {}
    if "grade_heavy" in R["trial"]:
        for cname in R["trial"]["nominal"]:
            a = [r["MJ_primary_per_payload_tkm"] for r in
                 R["trial"]["nominal"][cname]["per_duty"][design]["per_seed"]]
            b = [r["MJ_primary_per_payload_tkm"] for r in
                 R["trial"]["grade_heavy"][cname]["per_duty"][design]
                 ["per_seed"]]
            idd[cname] = dict(max_abs_diff=float(np.max(np.abs(
                np.array(a) - np.array(b)))) if len(a) == len(b) else None)
    ck["design_duty_null_at_grade_heavy_corner"] = dict(
        per_candidate=idd,
        identical=bool(all(
            (v["max_abs_diff"] if v["max_abs_diff"] is not None else 1.0)
            < 1e-12 for v in idd.values())) if idd else None,
        note=("R28's grade-heavy corner is a NULL OPERATION on a design "
              "duty that is already the grade-heavy regional cycle. WS9 "
              "runs it anyway and asserts the identity, which turns a "
              "redundancy into a free self-consistency check on the whole "
              "corner machinery. Escalated as ESC-WS9-3 because whether "
              "R28 wants a HEAVIER terrain corner for this duty is the "
              "lead's to say."))

    # --- 8. predictive energy management is speed-neutral -------------
    pcc = {}
    for cname in ("S6", "S0R-PCC"):
        blob = (R["trial"]["nominal"].get(cname)
                or R.get("brackets", {}).get(cname))
        if blob is None:
            continue
        for duty in DY9.DUTIES:
            rows = blob["per_duty"][duty]["per_seed"]
            base = R["trial"]["nominal"][CD9.RULER]["per_duty"][duty][
                "per_seed"]
            pd_ = [r.get("predictive") for r in rows if r.get("predictive")]
            pcc[f"{cname}/{duty}"] = dict(
                mean_target_preserved_to=float(np.max(
                    [p["mean_preserved_to"] for p in pd_])) if pd_ else None,
                max_target_delta_kmh=float(np.max(
                    [p["max_abs_delta_kmh"] for p in pd_])) if pd_ else None,
                achieved_duration_s_median=float(np.median(
                    [r["duration_s"] for r in rows])),
                ruler_duration_s_median=float(np.median(
                    [r["duration_s"] for r in base])),
                achieved_avg_speed_kmh_median=float(np.median(
                    [r["avg_speed_kmh"] for r in rows])),
                ruler_avg_speed_kmh_median=float(np.median(
                    [r["avg_speed_kmh"] for r in base])))
    ck["predictive_energy_management_is_not_a_speed_reduction"] = dict(
        per_case=pcc,
        note=("the modulated demand trace is renormalised so its "
              "distance-weighted mean equals the unmodulated one and is "
              "clipped to the assignment's 85-105 km/h band. The ACHIEVED "
              "speed and trip time are reported here beside the ruler's, "
              "because achieved speed is the integrator's business: if a "
              "preview candidate were quietly arriving late, this is where "
              "it would show."))

    # --- 9. the cold wall is actually exercised ------------------------
    cold = {}
    if "cold_minus10C" in R["trial"]:
        for cname, blob in R["trial"]["cold_minus10C"].items():
            rows = blob["per_duty"][design]["per_seed"]
            th = [r.get("pack_thermal") for r in rows if r.get("pack_thermal")]
            if not th:
                continue
            cold[cname] = dict(
                t_pack_start_C=th[0]["t_pack_start_C"],
                t_pack_end_C=float(np.median([t["t_pack_end_C"]
                                              for t in th])),
                seconds_to_reach_target=float(np.median(
                    [t["seconds_to_reach_target"] or -1.0 for t in th])),
                seconds_below_target=float(np.median(
                    [t["seconds_below_target"] for t in th])),
                chg_limit_at_ambient_kW=th[0]["chg_limit_at_ambient_kW"],
                chg_limit_warm_kW=th[0]["chg_limit_warm_kW"],
                collapse_factor=(th[0]["chg_limit_at_ambient_kW"]
                                 / max(th[0]["chg_limit_warm_kW"], 1e-9)),
                e_coolant_waste_heat_kWh=float(np.median(
                    [t["e_pack_coolant_waste_heat_kWh"] for t in th])),
                e_electric_heater_kWh=float(np.median(
                    [t["e_pack_electric_heater_kWh"] for t in th])))
    ck["cold_wall_exercised_R30"] = dict(
        per_candidate=cold,
        cold_acceptance_is_wired=bool(
            hasattr(EL8.Pack8, "p_cont_chg_kw_at")),
        note=("WS8 r1's finding F2 was that `p_cont_chg_kw_at` was defined "
              "and never called. WS8 r2 wired it to the CORNER'S AMBIENT. "
              "WS9 goes one step further as R30 requires: the pack "
              "temperature is a STATE, cold-soaked at ambient at the start "
              "of every run and warmed by its own losses, by engine "
              "coolant through a declared heat exchanger, or by an "
              "electric heater that draws from the bus - so the charge "
              "ceiling is evaluated at the pack's ACTUAL temperature "
              "sample by sample. That is stricter than r2 at the start of "
              "a trip and kinder later, and which of those dominates is a "
              "result, not an assumption."))

    # --- 10. the derate is exercised (F11) -----------------------------
    hot = {}
    if "hot_alt_2000m_45C" in R["trial"]:
        for cname, blob in R["trial"]["hot_alt_2000m_45C"].items():
            e = blob["spec"].get("engine", {})
            hot[cname] = dict(derate_applied=e.get("derate_applied"))
    ck["altitude_derate_exercised_F11"] = dict(
        per_candidate=hot,
        derate_factor=float(EN8.derate_factor(P9.ALT_CORNER_M,
                                              P9.ALT_CORNER_T_C)),
        air_density_first_principles=P9.air_density(P9.ALT_CORNER_M,
                                                    P9.ALT_CORNER_T_C),
        air_density_inherited_from_ws8=VEH.rho_air_hot_alt,
        density_agrees=bool(abs(P9.air_density(P9.ALT_CORNER_M,
                                               P9.ALT_CORNER_T_C)
                                - VEH.rho_air_hot_alt) < 1e-3),
        all_derated=bool(all((v["derate_applied"] or 1.0) < 1.0
                             for v in hot.values())) if hot else None,
        note=("R28 orders a 2,000 m / +45 C corner and WS8 r2 supplies the "
              "implementation. WS9's own ISA computation of the air "
              "density is carried alongside as an independent check on the "
              "inherited constant."))

    # --- 11. no WS8 numeric artifact is read ---------------------------
    # A NAME is not a READ. WS9 mentions both artifacts in prose - in the
    # vintage block that hashes them, in this check, and in ESC-WS9-8. What
    # would make the claim false is CONSUMING one: a line that both names an
    # artifact and opens, loads or parses it. That is what is tested.
    reads = []
    # The artifact list FOLLOWS THE PIN rather than being typed here, so a
    # round that adds an artifact to the pin also adds it to this check.
    ART = tuple(R["inherited_vintage"]
                ["ws8_artifacts_hashed_but_not_read"].keys())
    OPENERS = ("open(", "json.load", ".read()", "genfromtxt", "loadtxt",
               "read_csv", "readlines")
    for fn in sorted(n for n in os.listdir(_HERE) if n.endswith(".py")):
        for i, line in enumerate(
                open(os.path.join(_HERE, fn)).read().splitlines(), 1):
            if any(a in line for a in ART) and any(o in line
                                                   for o in OPENERS):
                reads.append(f"{fn}:{i}")
    ck["no_ws8_artifact_read"] = dict(
        artifacts=list(ART),
        lines_that_would_read_one=reads,
        rule="a line that NAMES a WS8 artifact and also opens, loads or "
             "parses it; a bare mention in prose is not a read",
        passes=bool(not reads),
        ws8_source_read_as_text=dict(
            files=list(CN9.WS8_TEXT_FILES),
            by="ws9_concordance, for the ESC-WS9-8 field-by-field "
               "comparison",
            why_this_is_not_a_contradiction=(
                "these are WS8 SOURCE FILES - code, not numbers - and six "
                "of the eight are already imported. `run_ws8.py` is read "
                "as TEXT and never imported, because WS9 re-implements its "
                "correction rule and must be able to compare against it "
                "without executing WS8's entry point. No line above reads "
                "a WS8 numeric artifact, which is what the claim is.")),
        note=(f"WS9 imports WS8's MODELS and reads none of its NUMBERS. "
              f"The {len(ART)} pinned artifacts are named in one place "
              f"only - the vintage block, where they are hashed and not "
              f"opened. So WS8's r1/r2/r3 artifact rounds cannot move a "
              f"WS9 number, and the r3 re-run's measured zero movement is "
              f"the demonstration of that rather than the assumption."))

    # --- 11b. R22(d): what the one spin rule actually costs -------------
    # WS8 r2 makes the same disclosure and WS9 inherits the obligation with
    # the rule: this integrator's driver is almost always either pulling or
    # braking, so a "geared AND unloaded" rule charges very little. That is
    # a property of the DRIVER MODEL, not of the architecture, and it must
    # be said rather than left for a reader to discover.
    spin = {}
    for cname, blob in R["trial"]["nominal"].items():
        rows = blob["per_duty"][design]["per_seed"]
        e_spin = float(np.median([r.get("e_spin_kWh", 0.0) or 0.0
                                  for r in rows]))
        e_bus = float(np.median([r.get("e_bus_traction_kWh", 0.0) or 0.0
                                 for r in rows]))
        if e_bus > 0.0 or e_spin > 0.0:
            spin[cname] = dict(e_spin_charged_kWh=e_spin,
                               e_bus_traction_kWh=e_bus,
                               share_of_bus_traction=(e_spin / e_bus
                                                      if e_bus > 1e-9
                                                      else 0.0))
    ck["spin_drag_R22d_disclosure"] = dict(
        per_candidate=spin,
        rule=f"geared AND the machine's own commanded force <= "
             f"{CD9.SPIN_IDLE_FORCE_N:.1f} N AND v > "
             f"{CD9.SPIN_IDLE_V_MIN_MS:.1f} m/s (WS8 r2's rule and r2's "
             f"thresholds, applied to the machine's shaft)",
        note=("R22(d) cost Vehicle Zero 1.77 pp. It costs almost nothing "
              "here, and the reason is the driver model rather than the "
              "hardware: this integrator's driver is either pulling or "
              "braking on nearly every sample, so the unloaded test is "
              "rarely true. Candidates that fit a disconnect pay nothing "
              "while it is open, and its mass IS charged - so the "
              "disconnect is a mass cost with almost no measured benefit "
              "on this duty, which is itself worth the lead's attention."))

    # --- 11b2. trip time, which the metric of record cannot see ---------
    tt = {}
    for corner, blob in R["trial"].items():
        base = {d: float(np.median(
            [r["duration_s"] for r in
             blob[CD9.RULER]["per_duty"][d]["per_seed"]]))
            for d in DY9.DUTIES}
        # the ruler's own per-seed durations, for the PAIRED statistic -
        # the same convention every margin in this report uses (WS8
        # finding F10: one margin statistic, per-seed paired, then
        # enveloped). R38 does not name a statistic, so both are exported
        # and the lead picks: `delta_pct` is the median-of-medians the
        # round-1 table carried, `paired_pct` is the 8-seed envelope of
        # the per-seed paired ratio (rule 4).
        pair = {d: {x["seed"]: x["duration_s"]
                    for x in blob[CD9.RULER]["per_duty"][d]["per_seed"]}
                for d in DY9.DUTIES}
        for cname, r in blob.items():
            for duty in DY9.DUTIES:
                rows = r["per_duty"][duty]["per_seed"]
                med = float(np.median([x["duration_s"] for x in rows]))
                pd_ = sorted((x["duration_s"] - pair[duty][x["seed"]])
                             / pair[duty][x["seed"]] * 100.0
                             for x in rows if x["seed"] in pair[duty])
                tt[f"{cname}/{corner}/{duty}"] = dict(
                    duration_s_median=med,
                    ruler_duration_s_median=base[duty],
                    delta_pct=(med - base[duty]) / base[duty] * 100.0,
                    paired_pct=dict(
                        n=len(pd_),
                        min=(pd_[0] if pd_ else None),
                        median=(float(np.median(pd_)) if pd_ else None),
                        max=(pd_[-1] if pd_ else None)))
    worst = max(tt, key=lambda k: tt[k]["delta_pct"])
    worst_p = max(tt, key=lambda k: (tt[k]["paired_pct"]["max"]
                                     if tt[k]["paired_pct"]["max"]
                                     is not None else -1e9))
    ck["trip_time_the_metric_cannot_see"] = dict(
        rule="max over the enumerated (candidate, corner, duty) case set "
             "of the trip-time penalty against the ruler on the same duty",
        statistic_note=(
            "TWO STATISTICS, both exported, because R38 names a bar and "
            "not a statistic. `cases` / `value` are the median-of-medians "
            "the round-1 table carried. `paired_cases_max` / "
            "`value_paired_max` are the 8-seed envelope of the PER-SEED "
            "PAIRED ratio - candidate against the ruler on the SAME seed, "
            "then enveloped - which is the convention every margin in this "
            "report uses and which rule 4 asks of a stochastic extremum. "
            "The lead applies R38 on whichever it rules is meant; WS9 "
            "applies neither."),
        cases={k: v["delta_pct"] for k, v in tt.items()},
        paired_cases_max={k: v["paired_pct"]["max"] for k, v in tt.items()},
        paired_cases_median={k: v["paired_pct"]["median"]
                             for k, v in tt.items()},
        value_paired_max=tt[worst_p]["paired_pct"]["max"],
        governing_case_paired_max=worst_p,
        detail=tt, value=tt[worst]["delta_pct"], governing_case=worst,
        note=("the metric of record is energy per payload tonne-km and it "
              "is BLIND TO TIME. A candidate that completes the same "
              "mission 10% slower delivers 10% fewer tonne-km per "
              "driver-day, and nothing in the headline says so. The "
              "integrator charges the extra time in accessory energy, "
              "which is a small fraction of what it actually costs an "
              "operator. Escalated as ESC-WS9-9."))

    # --- 11c. retarding shortfall, where the sink ran out ---------------
    rs = {}
    for corner, blob in R["trial"].items():
        for cname, r in blob.items():
            for duty, d in r["per_duty"].items():
                v = max((x.get("e_retard_shortfall_kWh", 0.0) or 0.0)
                        for x in d["per_seed"])
                if v > 0.0:
                    rs[f"{cname}/{corner}/{duty}"] = v
    ck["retarding_shortfall"] = dict(
        rule="max over the enumerated (candidate, corner, duty) case set",
        cases=rs,
        value=max(rs.values()) if rs else 0.0,
        governing_case=(max(rs, key=lambda k: rs[k]) if rs else None),
        note=("energy the envelope granted as retarding force that neither "
              "the pack nor the resistor could actually absorb. The "
              "resistor sizing rule is written to make this zero at the "
              "enumerated descent case; a non-zero value elsewhere means "
              "the descent-speed governor let the candidate run faster "
              "than its sink supports, and it is reported rather than "
              "absorbed."))

    # --- 12. scaling-law per-unit invariance (inherited check) ---------
    e1 = EL8.ScaledEDrive(1.0, CD9.EDRIVE_RATIO, n_machines=1)
    e2 = EL8.ScaledEDrive(1.8, CD9.EDRIVE_RATIO, n_machines=1)
    rpm, trq = 2000.0, 300.0
    l1 = float(e1._loss_kw(rpm, trq))
    l2 = float(e2._loss_kw(rpm, trq * 1.8))
    p1 = trq * rpm * 2 * np.pi / 60 / 1e3
    ck["scaling_law_per_unit_invariance"] = dict(
        eta_k1=p1 / (p1 + l1), eta_k18=(p1 * 1.8) / (p1 * 1.8 + l2),
        delta_pp=abs(p1 / (p1 + l1) - (p1 * 1.8) / (p1 * 1.8 + l2)) * 100.0,
        agree=bool(abs(p1 / (p1 + l1)
                       - (p1 * 1.8) / (p1 * 1.8 + l2)) < 1e-9),
        note=("loss(k; n, T) = k * loss_ws2(n, T/k) is per-unit invariant "
              "BY CONSTRUCTION, so this confirms the implementation, not "
              "the physics - exactly as WS8 said of the same check"))

    # --- 13. startability -----------------------------------------------
    f_start = CD8.startability_force_N()
    st = {}
    for cname in CD9.FULL_SET:
        cand = CD9.CANDIDATES[cname](ctx=CD9.NOMINAL)
        f_t, _, _ = cand.envelope(2.0 / 3.6)
        st[cname] = dict(F_available_at_2kmh_N=f_t,
                         meets_12pct_start=bool(f_t >= f_start - 1.0))
    ck["startability_12pct"] = dict(
        required_N=f_start, per_candidate=st,
        adhesion_ceiling_dry_N=ADH.mu_dry * VEH.m_axle_drive_tandem_kg * G,
        all_pass=bool(all(v["meets_12pct_start"] for v in st.values())),
        note=("Regulation (EU) No 1230/2012, five starts within five "
              "minutes at >=12% laden to the combination's maximum. WS9 "
              "checks torque and adhesion only; the five-in-five clause is "
              "a THERMAL requirement on the machine and is NOT modelled - "
              "stated, as WS8 stated it."))

    # --- 14. heat-ledger closure and ratings (F1) ------------------------
    hl = R.get("heat_ledger", {}).get("candidates", {})
    closes, ratings, fric = {}, {}, {}
    for cname, blob in hl.items():
        for case, row in blob["cases"].items():
            c = row.get("checks", {})
            if "descent_closes" in c:
                closes[f"{cname}/{case}"] = dict(
                    residual_kW=c["descent_closure_residual_kW"],
                    stored_in_pack_kW=c.get("descent_stored_in_pack_kW",
                                            0.0),
                    closes=c["descent_closes"])
            for key in ("resistor_within_rating", "retarder_within_rating"):
                if key in c and not c[key]:
                    ratings[f"{cname}/{case}/{key}"] = False
            if "friction_within_allowance" in c \
                    and not c["friction_within_allowance"]:
                fric[f"{cname}/{case}"] = row["friction_brake_kW"]
    ck["heat_ledger_closure_and_ratings_F1"] = dict(
        descent_cases=closes,
        all_descents_close=bool(all(v["closes"] for v in closes.values()))
        if closes else None,
        rating_violations=ratings,
        no_rating_violations=bool(not ratings),
        friction_over_allowance_cases=fric,
        friction_allowance_kW=CD9.FRICTION_ALLOWANCE_KW,
        friction_note=(
            "friction above the declared continuous allowance is a "
            "CAPABILITY finding, not a rating breach - it says the "
            "candidate cannot hold that case's speed on its own retarding "
            "hardware and must descend more slowly. Every case listed here "
            "is a PACK-SATURATED descent, which is exactly the case the "
            "resistor sizing rule enumerates and exactly the case WS8's "
            "finding F1 said its own ledger did not contain."),
        note=("F1(c): every descent case must close - the sum of the "
              "component rows equals the retarding power the case demands. "
              "F1(d): every exported component heat is checked against the "
              "rating of the hardware whose mass was charged. WS8 r1's "
              "ledger did neither and exported 210.71 kW of resistor heat "
              "for a candidate whose resistor was rated 200 kW."))

    # --- 15. prime-mover scope -------------------------------------------
    scope = {}
    for cname in CD9.FULL_SET:
        cand = CD9.CANDIDATES[cname](ctx=CD9.NOMINAL)
        scope[cname] = bool(getattr(cand, "line", None) is not None)
    ck["prime_mover_scope"] = dict(
        has_series_element=scope,
        only_S4p=bool(scope.get("S4p") and not any(
            v for k, v in scope.items() if k != "S4p")),
        note=("the assignment scopes the pin task to 'any series element "
              "(S4' sustainer; S7 has none; S5 none)'. Checked in code "
              "rather than accepted: a genset line exists on S4' and on "
              "nothing else."))

    # --- 16. CO2 factors are a carbon balance, not a lookup ---------------
    ck["co2_from_carbon_balance"] = dict(
        derivation=F9.fuels_dump()["_derivation"],
        diesel_g_per_MJ=F9.DIESEL.g_CO2_per_MJ_fuel,
        petrol_g_per_MJ=F9.PETROL_ATKINSON.g_CO2_per_MJ_fuel,
        methane_g_per_MJ=F9.CNG.g_CO2_per_MJ_fuel,
        published_spot_values=dict(diesel_74_1=74.1, petrol_73_0=73.0,
                                   methane_54_9=54.9),
        agree_to_1pct=bool(
            abs(F9.DIESEL.g_CO2_per_MJ_fuel - 74.1) / 74.1 < 0.01
            and abs(F9.CNG.g_CO2_per_MJ_fuel - 54.9) / 54.9 < 0.01),
        note="derived from H:C and LHV; the published spot values are the "
             "CHECK, not the input")

    # --- 17. energy closure on the ruler ---------------------------------
    rows = R["trial"]["nominal"][CD9.RULER]["per_duty"][control]["per_seed"]
    fuel_kwh = float(np.median([r["fuel_g_raw"] for r in rows])) \
        * LHV_KJ_PER_G / 3600.0
    shaft_kwh = float(np.median([r["e_engine_shaft_kWh"] for r in rows]))
    ck["ruler_energy_closure"] = dict(
        fuel_energy_kWh=fuel_kwh, engine_shaft_kWh=shaft_kwh,
        implied_engine_efficiency=shaft_kwh / max(fuel_kwh, 1e-9),
        duty_averaged_bsfc_g_per_kWh=float(np.median(
            [r["mean_bsfc_g_per_kWh"] for r in rows])),
        implied_from_bsfc=3600.0 / (float(np.median(
            [r["mean_bsfc_g_per_kWh"] for r in rows])) * LHV_KJ_PER_G),
        agree=bool(abs(shaft_kwh / max(fuel_kwh, 1e-9)
                       - 3600.0 / (float(np.median(
                           [r["mean_bsfc_g_per_kWh"] for r in rows]))
                           * LHV_KJ_PER_G)) < 0.02))

    # --- 18. envelope tabulation error -----------------------------------
    cand = CD9.CANDIDATES[CD9.RULER](ctx=CD9.NOMINAL)
    tb = PH8.build_env_tables(cand.envelope, cand.lam)
    err = 0.0
    for vv in np.arange(1.0, 30.0, 0.37):
        a = cand.envelope(float(vv))[0]
        b = float(np.interp(vv, tb["v_grid"], tb["F_trac"]))
        if a > 1.0:
            err = max(err, abs(a - b) / a)
    ck["envelope_tabulation"] = dict(
        grid_dv_ms=tb["dv"], worst_relative_error=err,
        acceptable=bool(err < 5e-3))

    # --- 19. ESC-WS9-8: no UNDECLARED difference from WS8 r3 -------------
    cc = R.get("concordance_ws8_r3") or {}
    ck["concordance_with_ws8_r3_ESC_WS9_8"] = dict(
        pinned_round=(R["inherited_vintage"]["ws8_code_round_fingerprint"]
                      ["code_round"]),
        per_implementation={k: v["result"]
                            for k, v in (cc.get("summary") or {}).items()},
        any_undeclared_difference=cc.get("any_undeclared_difference"),
        undeclared_fields=cc.get("undeclared_fields", []),
        import_surface_symbols=(cc.get("import_surface_r2_to_r3") or {})
        .get("n_symbols"),
        import_surface_symbols_changed_r2_to_r3=(
            (cc.get("import_surface_r2_to_r3") or {}).get("n_changed")),
        every_imported_symbol_identical_r2_to_r3=(
            (cc.get("import_surface_r2_to_r3") or {})
            .get("every_imported_symbol_identical")),
        passes=bool(cc and cc.get("any_undeclared_difference") is False),
        note=("ESC-WS9-8 asked for a field-by-field comparison of WS9's "
              "three own implementations against the closed round's. The "
              "comparison is computed by `ws9_concordance` from WS8's "
              "source on disk, and this is its gate: any field where the "
              "two differ AND WS9 did not declare the difference in "
              "advance fails the run. `import_surface_symbols_changed_"
              "r2_to_r3` is the separate, stronger statement - how many of "
              "the WS8 symbols WS9 actually imports moved between the "
              "round it was pinned to and the round it is pinned to now."))

    # --- 20. R34: the 10 Hz traces are on disk ---------------------------
    tr34 = R.get("traces_r34") or {}
    ck["traces_r34_exported"] = dict(
        n_files=tr34.get("n_files", 0),
        all_present=tr34.get("all_present", False),
        all_unchanged_since_written=tr34.get("all_unchanged_since_written",
                                             False),
        selection_rule=tr34.get("selection_rule"),
        passes=bool(tr34.get("all_present") and
                    tr34.get("all_unchanged_since_written")),
        note=("R34 names WS9 RE-RUNS explicitly and this is WS9's next "
              "artifact after that ruling. The files are re-hashed off "
              "disk rather than trusted from the writer."))

    ck["all_pass"] = bool(
        ck["concordance_with_ws8_r3_ESC_WS9_8"]["passes"]
        and ck["traces_r34_exported"]["passes"]
        and ck["road_load_95kmh_flat"]["agree"]
        and ck["two_walls_closed_form"]["all_pass"]
        and ck["mass_closure"]["all_close"]
        and ck["S6_mass_neutral_with_ruler"]["neutral"]
        and ck["primary_energy_invariance"]["all_pass"]
        and ck["machine_basis_gate_ESC2"]["all_pass"]
        and ck["no_ws8_artifact_read"]["passes"]
        and ck["scaling_law_per_unit_invariance"]["agree"]
        and ck["startability_12pct"]["all_pass"]
        and ck["prime_mover_scope"]["only_S4p"]
        and ck["co2_from_carbon_balance"]["agree_to_1pct"]
        and ck["envelope_tabulation"]["acceptable"]
        and (ck["heat_ledger_closure_and_ratings_F1"]["no_rating_violations"])
        and (ck["design_duty_null_at_grade_heavy_corner"]["identical"]
             in (True, None)))
    return ck


# =====================================================================
#  escalations (CLAUDE.md rule 8: cite the ruling, never self-resolve)
# =====================================================================
def _vr(R):
    return R.get("verdict_robustness_ESC3", {}).get(
        "candidates_whose_verdict_moves", [])


def escalations(R):
    design, control = DY9.DESIGN_DUTY, DY9.CONTROL_DUTY
    ak = R["advance_kill"]["candidates"]
    s6 = ak.get("S6", {})
    be = R.get("_s6_break_even", {})
    out = []

    out.append(dict(
        id="ESC-WS9-1",
        title=("S6's verdict rests on a manufacturer's demonstration claim, "
               "and it is the only candidate that clears the bar"),
        cites=("Assignment: 'opposed-piston-class engine on a CITED "
               "efficiency basis (state the BTE claim and its evidence "
               "quality, mass-neutral or better)'; R31; D7 (novelty is not "
               "merit); D5 (nothing kill-bearing is ratified unadjudicated)"),
        finding=(
            "S6's engine is calibrated to a peak brake thermal efficiency of "
            f"{E9.OP_PEAK_BTE_CLAIMED:.3f}, read verbatim from a PRIMARY "
            "document that WS9 fetched and read in full - a strictly better "
            "evidence class than anything external in WS8, whose "
            "environment blocked egress. It is nonetheless a "
            "MANUFACTURER'S document about its own demonstration "
            "programme. WS9 has taken the single peak-BTE number and "
            "NOTHING else from it (see engines.ENG-OP.cited_claim."
            "what_ws9_does_not_take): not the flatter map, not the 30% "
            "lower heat rejection, not the absent pumping loop, not the "
            "measured 4-21% route advantages. Every one of those would "
            "make S6 better. The break-even peak BTE at which S6 exactly "
            "clears the >=3% criterion on the design duty is "
            + (f"{be.get('break_even_peak_BTE', float('nan')):.4f}"
               if be else "reported in the S6 block")
            + ", against the incumbent's 0.4547 - so the lead can see "
              "exactly how much of the claim has to be true."),
        why_not_self_resolved=(
            "Whether a manufacturer's demonstration document is sufficient "
            "evidence to ADVANCE a candidate is an evidence-standard "
            "decision, not a modelling one. WS9 may not set the program's "
            "evidence bar."),
        asks=("Rule on ONE of: (a) the cited peak BTE stands as the basis "
              "and S6 advances on it; (b) S6 advances CONDITIONALLY, "
              "subject to an independent BSFC map before any hardware "
              "decision; (c) the claim is discounted to a stated peak BTE "
              "and S6 is re-read against the break-even figure."),
        materiality="high - it is the difference between the only ADVANCE "
                    "in this trial and no advance at all"))

    out.append(dict(
        id="ESC-WS9-2",
        title=("The grid primary-energy factor and CO2 intensity are "
               "declared, not sourced from a fetched primary document"),
        cites="ESC-3 as ruled in R27; assignment: 'electricity term per "
              "ESC-3 with a declared grid primary-energy factor and a CO2 "
              "lens, factor sensitivity +/-50%'",
        finding=(
            f"WS9 declares PEF_grid = {P9.EA.pef_grid} (the EU Energy "
            "Efficiency Directive default as amended by Directive (EU) "
            "2018/2002) and a grid intensity of "
            f"{P9.EA.co2_grid_kg_per_kWh} kg CO2e/kWh at the meter. Both "
            "are RECALLED, not fetched: the EEA indicator page was "
            "retrieved but publishes its figure only in a chart. The "
            "intensity was chosen to sit BETWEEN the EU average (about "
            "0.21 in 2024) and the US average (about 0.37), and Vehicle "
            "One has no declared market, so the +/-50% sensitivity ESC-3 "
            "orders (0.14 to 0.42) is not decoration here - it spans the "
            "entire geographic question, and S4's CO2 verdict moves with "
            "it."),
        why_not_self_resolved=("Choosing the grid of record is a "
                               "program-level metric decision."),
        asks=("Fix the factors of record, or declare Vehicle One's market "
              "so they can be sourced. THE SWEEP IS NOT DECORATION: WS9 "
              "re-applies the pre-committed criteria unchanged at each end "
              "of it (`verdict_robustness_ESC3`), and the verdict of "
              + (", ".join(_vr(R)) + " MOVES across the swept range."
                 if _vr(R) else
                 "every candidate holds across the swept range.")
              + " Whatever the lead fixes the factor at is therefore not a "
                "reporting convention but part of the verdict."),
        materiality=("high - it does not move any diesel-only candidate, "
                     "and it decides a verdict"
                     if _vr(R) else
                     "medium - it does not move any diesel-only candidate, "
                     "and it decides S4's CO2 lens")))

    out.append(dict(
        id="ESC-WS9-3",
        title=("R28's grade-heavy corner is a null operation on a design "
               "duty that is already grade-heavy"),
        cites="R28 (corner set of record); R29 (design duty)",
        finding=(
            "R28 lists 'grade-heavy' among the corners; R29 makes the "
            "GRADE-HEAVY REGIONAL corridor the design duty. Applying the "
            "grade-heavy terrain construction to a cycle built with it "
            "already on changes nothing, and WS9 asserts the identity "
            "(sanity.design_duty_null_at_grade_heavy_corner) rather than "
            "reporting the same run twice under two names. On the CONTROL "
            "duty the corner is real and is reported. The consequence is "
            "that the design duty is gated on FOUR corners, not five."),
        why_not_self_resolved=("Inventing a heavier-than-specified terrain "
                               "corner would be WS9 writing R28."),
        asks=("Confirm that four corners gate the design duty, or specify "
              "what a heavier terrain corner should be for a duty whose "
              "nominal case already carries 7.9-10.7% grades."),
        materiality="low for the verdicts, medium for the record"))

    out.append(dict(
        id="ESC-WS9-4",
        title=("WS9 has replaced R18's transferred flat-rating ratio with an "
               "ISO 8528-1 prime-power basis, as ESC-4 directed"),
        cites="ESC-4 as ruled in R27: 'the R18 flat-rating transfer stands "
              "as a bracket; WS9 sources a Class 8 prime-power derating "
              "basis'; R18; R24",
        finding=(
            f"WS9 sources PRP = {P9.PRP_OVER_AUTOMOTIVE_PEAK} x automotive "
            "peak from the ISO 8528-1 rating structure (prime: unlimited "
            "hours, 10% overload for one hour in twelve, 70-75% 24-hour "
            "average load factor), corroborated by the Cummins QSX15/X15 "
            "correspondence. R18's transferred ratio is "
            f"{P9.R18_BRACKET_RATIO:.4f} and is carried alongside as the "
            "declared bracket. DIRECTION OF ERROR, stated: PRP is 4.5% MORE "
            "genset power, so it FLATTERS the only candidate it touches "
            "(S4'). The evidence is search-summary plus one fetched "
            "secondary page - the rating STRUCTURE is standard and not in "
            "dispute, the 0.90 ratio is an industry rule of thumb rather "
            "than a figure read out of the standard."),
        why_not_self_resolved="R18 is a ruling; only the lead amends it.",
        asks=("Ratify the PRP basis for Vehicle One, or direct WS9 to "
              "carry R18's 0.861 and re-run S4'. Both numbers are "
              "exported so the bracket is readable either way."),
        materiality="low - it touches one candidate and moves its climb "
                    "rate, not its ranking"))

    pcc = (R.get("bracket_margins", {}).get(design, {}).get("S0R-PCC", {})
           .get("ensemble", {}))
    pcc_c = (R.get("bracket_margins", {}).get(control, {})
             .get("S0R-PCC", {}).get("ensemble", {}))
    pcc_med = pcc.get("median")
    pcc_small = pcc_med is not None and abs(pcc_med) < 0.5
    out.append(dict(
        id="ESC-WS9-5",
        title=("Predictive energy management is a ZERO-MASS lever the "
               "incumbent can fit too - and it turns out to be worth almost "
               "nothing"),
        cites="D8 ('zero-mass levers first'); R29 (the incumbent is "
              "CONCEDED near-optimal on the control duty); assignment "
              "('predictive energy management (zero mass)')",
        finding=(
            "The assignment gives predictive energy management to S6 alone. "
            "It costs no mass, needs no hardware beyond a map and a "
            "controller, and can be fitted to the RULER as easily as to a "
            "new engine - so reporting S6-with-preview against a "
            "ruler-without-preview would compare two control strategies and "
            "call the difference an engine. WS9 therefore measured the same "
            "lever ON THE RULER (bracket S0R-PCC). THE MEASUREMENT DOES NOT "
            "SUPPORT THE CONCERN THAT PROMPTED IT: on the design duty "
            "preview is worth "
            + (f"{pcc.get('median', float('nan')):+.2f}% (median) / "
               f"{pcc.get('min', float('nan')):+.2f}% (ensemble-min), and "
               f"on the control duty "
               f"{pcc_c.get('median', float('nan')):+.2f}% / "
               f"{pcc_c.get('min', float('nan')):+.2f}%"
               if pcc else "the bracket reported in section 4.5")
            + ". The reason is physical and worth recording: this "
              "integrator's driver ALREADY cuts fuel on overrun and already "
              "governs its own descent speed against its retarding "
              "capability, so the crest half of the law is largely already "
              "there; and the pre-boost half buys kinetic energy at an "
              "aerodynamic cost that scales with the cube of speed, which "
              "on a corridor averaging over 90 km/h is a poor trade. The "
              "consequence for the trial is that S6's margin is its ENGINE "
              "and essentially nothing else, which makes ESC-WS9-1 the only "
              "question about S6 that matters."),
        why_not_self_resolved=(
            "Whether the ruler carries preview is a baseline-specification "
            "decision, exactly as ESC-WS8-6 was for the retarder - and the "
            "fact that WS9's particular preview law is worth nothing does "
            "not establish that a better one would be."),
        asks=("Confirm the ruler's control specification: S0R without "
              "preview (as run), or S0R-PCC as the ruler of record - the "
              "two are within "
              + (f"{abs(pcc.get('median') or 0.0):.2f} pp"
                 if pcc else "a fraction of a point")
              + " of each other on the design duty, so the choice is "
                "presentational rather than material AS MODELLED. If the "
                "lead wants preview credited properly, the ask is a "
                "SEPARATE one: a preview law tuned against this duty rather "
                "than the symmetric +/-6% band WS9 declared before "
                "measuring."),
        materiality=("low as measured - the lever is worth under half a "
                     "point on either duty, and it is reported that way "
                     "rather than left as an open worry"
                     if pcc_small else
                     "high - it is the difference between S6's headline and "
                     "S6's engine-only margin")))

    out.append(dict(
        id="ESC-WS9-6",
        title=("R30's waste-heat cab path partially disarms the cold wall "
               "for engine-carrying candidates and not for S4'"),
        cites="R30 (THE COLD WALL); ESC-WS8-6 precedent on accessory "
              "asymmetry; WS8 finding F2",
        finding=(
            "R30 orders preconditioning and a coolant/waste-heat cab path "
            "to be MODELLED, and the conventional truck's free cab heat to "
            "be charged to the others. WS9 models both. The consequence is "
            "an asymmetry that is physical and large: S5, S6 and S7 run an "
            "engine for most of the mission, so their cab heat is free and "
            "their packs are preconditioned from coolant at no fuel cost, "
            "while S4' runs its sustainer for a minority of the mission and "
            "must heat its cab and its pack from the bus. The cold corner "
            "therefore stops being a common-mode penalty and becomes an "
            "architecture-dependent one. That is R30's intended effect - "
            "but the SPLIT of WS8's 3.2 kW cold delta into 2.2 kW of cab "
            "heat and 1.0 kW of battery thermal is WS9-declared, and it "
            "decides how much of the effect there is."),
        why_not_self_resolved=("The split is a modelling convention that "
                               "changes a corner every candidate is judged "
                               "on; WS9 declares it and puts it up."),
        asks=("Confirm the 2.2 / 1.0 kW split, or supply one. Note that "
              "the pack-thermal half is no longer a flat allowance in WS9 - "
              "it is computed from a modelled pack temperature - so only "
              "the cab-heat half is a declared constant."),
        materiality="medium - it moves the cold corner, which was binding "
                    "for all four WS8 candidates"))

    out.append(dict(
        id="ESC-WS9-7",
        title=("S5 has no launch device on the engine side: an inverter or "
               "machine fault is a tow, not a limp-home"),
        cites="R22(c) (Vehicle Zero's genset-or-pack-fault = tow "
              "asymmetry); WS8 section 6.5 and the S3 precedent; "
              "assignment ('2-speed dog box (no synchros, no launch "
              "clutch, no power-shift)')",
        finding=(
            "The assignment specifies S5 with NO LAUNCH CLUTCH. A dog box "
            "cannot slip, so below the low gear's coupling floor "
            f"({R['trial']['nominal']['S5']['spec']['gearbox']['coupling_floor_kmh']:.1f} km/h "
            "for S5 as run) the engine cannot be connected at all and the "
            "machine is the ONLY prime mover. With the machine, its "
            "inverter or its buffer unavailable, the combination cannot be "
            "started from rest and cannot be recovered under its own "
            "power. This is S3's fault-limp finding in a milder form - "
            "milder because S5's engine CAN drive the truck once it is "
            "rolling above the coupling floor, so a fault at speed is a "
            "limp-home and only a fault at rest is a tow."),
        why_not_self_resolved=("Adding a launch device would be WS9 "
                               "rewriting the candidate the assignment "
                               "specified."),
        asks=("Confirm S5's specification, or authorise a launch device "
              "(a slipping clutch or a torque converter) and its mass for "
              "a re-run. Note the direction: a launch device would ADD "
              "mass to a candidate that is already losing on payload."),
        materiality="medium - it is a capability finding, not a fuel one, "
                    "and capability findings outlived fuel findings in WS8"))

    tt = R["sanity"]["trip_time_the_metric_cannot_see"]
    out.append(dict(
        id="ESC-WS9-9",
        title=("The metric of record is blind to trip time, and on the "
               "design duty the spread is not small"),
        cites="Assignment: 'metric = primary energy per PAYLOAD tonne-km'; "
              "ESC-3 as ruled in R27; D13 (per-km efficiency flatters, "
              "per-payload judges)",
        finding=(
            "D13 taught the program that a per-km metric flatters and a "
            "per-payload metric judges. There is a third denominator the "
            "trial does not carry: TIME. Every candidate here completes the "
            "same mission over the same road, but not at the same speed - "
            "the integrator gives a candidate that cannot hold the demanded "
            "force the speed its envelope supports, and charges it the "
            "extra time in accessory energy alone. The worst case in this "
            f"trial is `{tt['governing_case']}` at "
            f"{tt['value']:+.1f}% of the ruler's trip time on the same "
            "duty. An operator paying a driver by the hour and a shipper "
            "paying by the tonne-km are looking at two different numbers, "
            "and only one of them is in this report."),
        why_not_self_resolved=("Adding a time or productivity term to the "
                               "metric of record is a program-level metric "
                               "decision, exactly as ESC-3 was."),
        asks=("Rule on whether Vehicle One's metric acquires a "
              "productivity term (payload tonne-km per hour, or energy per "
              "payload tonne-km at matched trip time), or whether trip "
              "time stays a reported side quantity. The full "
              "(candidate, corner, duty) table is exported at "
              "`sanity.trip_time_the_metric_cannot_see` either way."),
        materiality="medium - it does not move a margin as computed, and "
                    "it would change the RANKING if ruled in"))

    v = R["inherited_vintage"]
    out.append(dict(
        id="ESC-WS9-8",
        title=("WS9 ran against WS8's round-2 CODE before round 2's "
               "ARTIFACTS existed"),
        cites="R26 (errata order: WS8_semi_architecture/R2_DIRECTIVE.md); "
              "assignment ('its r2 outputs when they land (build to "
              "hot-swap; state vintages)')",
        finding=(
            "When WS9 ran, WS8's round-2 corrections were present in its "
            "CODE - the cold-charge-acceptance wiring (F2), the ambient "
            "derate (F11), the one spin rule (F5), the duty-averaged "
            "correction pricing (F6), the errata switches - but "
            "results_ws8.json and REPORT_WS8.md were still at their round-1 "
            "vintage, so round 2 had not regenerated. WS9 therefore "
            "inherits r2's MODELS and none of its NUMBERS, which is "
            "sufficient because WS9 reads no WS8 numeric artifact at all "
            "and re-derives its own ruler "
            "(sanity.no_ws8_artifact_read). Every inherited source file is "
            "sha256-pinned in `inherited_vintage`, and the r2 fingerprint "
            f"records the code round as '{v['ws8_code_round_fingerprint']['code_round']}'."),
        why_not_self_resolved=("Whether WS9's implementations of the r2 "
                               "rules match r2's own is r2's adjudication "
                               "to settle, not WS9's."),
        asks=("When r2 closes, compare the r2 concordance table in section "
              "12 field by field and confirm that WS9's three own "
              "implementations - the spin rule applied to the machine's "
              "shaft rather than the vehicle's force channels, the "
              "correction pricing on WS9's own energy keys, and the pack "
              "temperature as a STATE rather than the corner's ambient - "
              "are consistent with r2's. If any differs, WS9 re-runs "
              "against r2: the pin makes that a one-flag operation."),
        execution=_esc8_execution(R),
        materiality="medium for the record, low for the numbers"))

    fp = v["ws8_code_round_fingerprint"]
    out.append(dict(
        id="ESC-WS9-10",
        title=("the WS8 round WS9 is now pinned to was itself adjudicated "
               "NOT CLEAN, and WS9 pinned it anyway because it was ordered "
               "to"),
        cites=("BASELINE_v5 R39/ESC-8 ('WS9 re-runs against WS8 r3 sources "
               "when they land'); R35 (WS8 r2 numbers PROVISIONAL until r3 "
               "closes); FINDINGS_WS8_r3.md; CLAUDE.md rule 10 (never "
               "modify another workstream's artifacts or findings)"),
        finding=(
            "WS9 is now pinned to WS8 code round "
            f"`{fp['code_round']}`. FINDINGS_WS8_r3.md returns, verbatim: "
            "'NOT CLEAN. Two blocking, six material, twelve minor.' No WS8 "
            "verdict moved and `all_unchanged = True`, and the adjudicator "
            "places BOTH blocking findings in the round's account of "
            "itself rather than its physics - B1, that the changelog's "
            "central claim about what moved is wrong for S3 by 24% of S3's "
            "movement; B2, that a new R14 export names a statistic it does "
            "not carry. WS9's exposure to both is nil on the numbers, and "
            "that is measured rather than argued: every one of the "
            f"{(R.get('concordance_ws8_r3') or {}).get('import_surface_r2_to_r3', {}).get('n_symbols', 0)} "
            "WS8 symbols on WS9's import surface is byte-identical between "
            "r2 and r3 (`concordance_ws8_r3.import_surface_r2_to_r3`), and "
            "WS9 reads no WS8 numeric artifact at all. But the RECORD now "
            "says WS9 is pinned to an adjudicated-NOT-CLEAN round, and "
            "that is a fact about the record the lead has to hold."),
        why_not_self_resolved=(
            "WS9 cannot dispose of another workstream's findings, cannot "
            "judge whether r3's blocking findings are answerable inside r3, "
            "and cannot decide whether WS8 goes to an r4. WS9 also declines "
            "to soften the statement: the order was to pin r3, so r3 is "
            "pinned, and the adjudication status travels with it."),
        asks=("Note that this pin is to an adjudicated-NOT-CLEAN round. IF "
              "THE LEAD BOUNCES WS8 TO AN r4, THIS PIN IS STALE AGAIN and "
              "WS9 must re-run - the same one-flag operation, and this "
              "round is the evidence that it is one. Rule on whether a WS9 "
              "ratification may proceed on a WS8 round that has open "
              "blocking findings, given that none of them reaches a WS9 "
              "number."),
        materiality=("high for the record, nil for the numbers - and the "
                     "second half is measured, not asserted")))

    sib = v.get("sibling_workstream_sources_reached_through_ws8", {})
    out.append(dict(
        id="ESC-WS9-11",
        title=("WS9's round-1 pin did not cover the sibling-workstream "
               "sources its numbers depend on, and one of them changed "
               "under it"),
        cites=("ESC-WS9-8 (the pin as a hot-swap signal); CLAUDE.md rule 1 "
               "(byte-stable regeneration) and rule 10 (read other "
               "workstreams read-only); FINDINGS_WS8_r3.md M6, the same "
               "class of finding against WS8's own pin"),
        finding=(
            "WS9 imports WS8's models, and WS8's models in turn import "
            "WS4's `derate_factor` from `ws4_models.py`, WS4's "
            "`WS2TractionChain` and `load_ws2_exports` from "
            "`ws4_chain.py`, and WS3's `CELLS` from `ws3_cells.py`; that "
            "loader then reads three WS2 export files off disk. WS9's "
            "round-1 pin covered WS8's seven files and none of those, so "
            "a change in a sibling workstream could move a WS9 number with "
            "nothing in the record able to say so. This is not "
            "hypothetical: `ws4_chain.py` CHANGED between WS9's round-1 "
            "run and this one, because WS4's KX rounds landed overnight in "
            "the same tree. This round pins all six "
            f"({len(sib)} rows in "
            "`inherited_vintage.sibling_workstream_sources_reached_through"
            "_ws8`), and `verify_ws9.py` reports drift on them exactly as "
            "it does for WS8's own files."),
        why_not_self_resolved=(
            "Whether WS9 may be re-run against a WS4 tree that is itself "
            "mid-adjudication is a sequencing decision for the lead, not "
            "for WS9. WS9 also cannot rule on whether the WS4 change is "
            "admissible - it can only measure whether it moved anything, "
            "which it does."),
        asks=("Note that this artifact was produced against a WS4 tree "
              "that changed after WS9's round-1 run and that is itself "
              "under adjudication. Rule on whether Vehicle One's pin "
              "should be a whole-tree pin. If WS4's KX round is bounced "
              "again, WS9's pin goes stale for the same reason ESC-WS9-10 "
              "describes, and from a different direction."),
        materiality=("high for the record; the measured effect on the "
                     "numbers is in the re-run's own comparison")))

    tr34 = R.get("traces_r34") or {}
    out.append(dict(
        id="ESC-WS9-12",
        title="R34's 'per run' is read as a declared subset, and WS9 says "
              "so rather than quietly deciding it",
        cites=("BASELINE_v5 R34 ('Every pipeline exports a 10 Hz trace "
               "file per run (feeds the WS10 exhibit/simulator). WS5, WS9 "
               "re-runs, and all later work comply from their next "
               "artifact.'); the WS4, WS5 and WS11 precedents under the "
               "same ruling"),
        finding=(
            "WS9's trial is 6 corners x 6 candidates x 2 duties x 8 seeds "
            "= 576 runs of roughly 74,000 samples each. A literal reading "
            "of 'per run' is some gigabytes of CSV in a git repository. "
            f"WS9 exports {tr34.get('n_files', 0)} traces on a declared "
            "rule - every candidate including the ruler, on the DESIGN "
            "duty, at the NOMINAL corner, on the first seed - which is the "
            "full candidate set on the duty that gates, and which follows "
            "what WS4, WS5 and WS11 each did under this same ruling. "
            "`check_determinism_ws9.py` re-simulates one of these traces "
            "from a fresh process and diffs it byte for byte, so the "
            "unexported runs are reproducible rather than lost."),
        why_not_self_resolved=(
            "R34 is a program-hygiene ruling and its scope is the lead's "
            "to set. WS9 has taken the reading the program's other three "
            "R34-compliant workstreams took; if that reading is wrong it "
            "is wrong for all four, which is a program decision."),
        asks=("Confirm the declared-subset reading of R34, or order the "
              "literal one and WS9 will export all 576 (and the repository "
              "will need to say where they live). Note that the WS10 "
              "exhibit is the consumer R34 names, so the right answer may "
              "be whatever WS10 actually needs."),
        materiality="low for the numbers, medium for WS10's inputs"))

    return out


def _esc8_execution(R):
    """What THIS round did about ESC-WS9-8, stated without disposing of
    it. The escalation stays open: rule 8 says an escalation goes to the
    lead and is never self-resolved, and executing the comparison an
    escalation asks for is not the same as ruling on it."""
    cc = R.get("concordance_ws8_r3") or {}
    d = cc.get("import_surface_r2_to_r3") or {}
    return dict(
        status="EXECUTED, NOT RESOLVED",
        round_compared="WS8 r3 (r2 is superseded - BASELINE_v5 R35, R39/"
                       "ESC-8)",
        what_was_done=(
            "the field-by-field comparison this escalation asks for was "
            "run against WS8 r3's source, computed rather than written "
            "(`ws9_concordance`), and the whole trial was re-run against "
            "r3 - all corners, all candidates, both duties, 8 seeds - "
            "because an unexercised hot-swap is not evidence that the pin "
            "makes it a one-flag operation."),
        per_implementation={k: v["result"]
                            for k, v in (cc.get("summary") or {}).items()},
        any_undeclared_difference=cc.get("any_undeclared_difference"),
        imported_symbols_compared=d.get("n_symbols"),
        imported_symbols_changed_r2_to_r3=d.get("n_changed"),
        still_for_the_lead=(
            "whether WS9's three declared differences from WS8 - the spin "
            "rule on the machine's shaft, the correction pricing on WS9's "
            "own energy keys, and the pack temperature as a state - are "
            "ACCEPTED is the lead's ruling, not WS9's. WS9 has measured "
            "that each is a difference it declared in advance with an "
            "authority cited; it has not ruled that any of them is right. "
            "See also ESC-WS9-10 on the adjudication status of the round "
            "now pinned."))


# =====================================================================
#  R14 machine-readable interface
# =====================================================================
def interface_block(R):
    design, control = DY9.DESIGN_DUTY, DY9.CONTROL_DUTY
    iface = OrderedDict()
    iface["_convention"] = (
        "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6); "
        "stochastic extrema are 8-seed ensemble envelopes (rule 4); every "
        "worst-case field is an explicit max/min over an ENUMERATED case "
        "set with the governing case labelled inline (R14)")
    iface["metric_of_record"] = CR9.METRIC_NOTE
    iface["duties"] = dict(
        design=design, control=control,
        gating="ADVANCE/KILL is read on the DESIGN duty; the control duty "
               "is reported alongside and NEVER gates",
        no_fleet_average=P9.FLEET_MIX_IS_FORBIDDEN)
    iface["gcw_kg"] = VEH.m_gcw
    iface["vehicle"] = dict(CdA_m2=VEH.CdA, Crr=VEH.Crr, r_dyn_m=VEH.r_dyn,
                            provisional_per_E13_precedent=True)
    iface["inherited_vintage"] = R["inherited_vintage"]

    # ---- R38's gate input, machine-readable ---------------------------
    # BASELINE_v5 R38: "an ADVANCE additionally requires design-duty trip
    # time <= +5% of S0R. The metric of record stays energy per payload
    # tonne-km; trip time is a gate, not a term. Applied at ratification
    # from the exported `trip_time_the_metric_cannot_see` table."
    #
    # R38 was pre-committed AFTER WS9 ran and it says the LEAD applies it.
    # WS9 therefore exports the input and DOES NOT APPLY THE GATE: no
    # verdict in this artifact reads this block, `verdict` is absent from
    # it by construction, and the advance/kill block is unchanged. What
    # this adds over round 1 is that the gate's input is now in the R14
    # interface instead of only in `sanity`, which is where a consumer
    # looks for a gate quantity - WS8's own r3 adjudication (M4) records
    # what it costs when a gate quantity is missing from the export.
    tt = R["sanity"]["trip_time_the_metric_cannot_see"]
    design_rows = OrderedDict()
    for cname in R["trial"]["nominal"]:
        key = f"{cname}/nominal/{design}"
        if key in tt["cases"]:
            design_rows[cname] = tt["cases"][key]
    over = OrderedDict(
        (k, v) for k, v in sorted(tt["cases"].items())
        if f"/{design}" in k and v > P9.R38_TRIP_TIME_GATE_PCT)
    over_p = OrderedDict(
        (k, v) for k, v in sorted(tt["paired_cases_max"].items())
        if f"/{design}" in k and v is not None
        and v > P9.R38_TRIP_TIME_GATE_PCT)
    design_rows_p = OrderedDict()
    for cname in R["trial"]["nominal"]:
        key = f"{cname}/nominal/{design}"
        if key in tt["paired_cases_max"]:
            design_rows_p[cname] = tt["detail"][key]["paired_pct"]
    iface["trip_time_R38_gate_input"] = dict(
        ruling="BASELINE_v5 R38 (pre-committed before the table was read)",
        gate="design-duty trip time <= +5% of S0R, in addition to the "
             "pre-committed ADVANCE criteria",
        gate_pct=P9.R38_TRIP_TIME_GATE_PCT,
        applied_by="THE LEAD, at ratification. NOT APPLIED IN THIS "
                   "ARTIFACT and not read by any verdict in it.",
        statistic="median trip time over the 8-seed ensemble, against the "
                  "ruler S0R on the SAME duty, corner and seed set",
        design_duty=design,
        design_duty_nominal_pct_vs_ruler=design_rows,
        design_duty_nominal_paired_pct_vs_ruler=design_rows_p,
        statistic_note=tt["statistic_note"],
        rule="max/min over the enumerated (candidate, corner, duty) case "
             "set; the full table is `all_cases_pct` and the detail with "
             "absolute seconds is sanity."
             "trip_time_the_metric_cannot_see.detail",
        worst_case_pct=tt["value"], governing_case=tt["governing_case"],
        design_duty_cases_above_gate=over,
        n_design_duty_cases_above_gate=len(over),
        design_duty_cases_above_gate_paired_max=over_p,
        n_design_duty_cases_above_gate_paired_max=len(over_p),
        worst_case_paired_max_pct=tt["value_paired_max"],
        governing_case_paired_max=tt["governing_case_paired_max"],
        all_cases_pct=tt["cases"],
        all_cases_paired_max_pct=tt["paired_cases_max"],
        note=("this block is the gate's INPUT. It is exported so the lead "
              "can apply R38 in one read; WS9 neither applies it nor "
              "adjusts a verdict for it (R37 keeps WS9's verdicts "
              "PROVISIONAL and its adjudication is the lead-designated "
              "Fable seat). `design_duty_cases_above_gate` is a "
              "measurement, not a verdict."))

    # ---- ESC-WS9-8's answer, machine-readable -------------------------
    cc = R.get("concordance_ws8_r3") or {}
    iface["concordance_with_ws8_r3"] = dict(
        escalation="ESC-WS9-8", ruling="BASELINE_v5 R39/ESC-8",
        pinned_round=(R["inherited_vintage"]["ws8_code_round_fingerprint"]
                      ["code_round"]),
        pinned_round_adjudication=(
            R["inherited_vintage"]["ws8_code_round_fingerprint"]
            .get("r3_adjudication")),
        per_implementation=cc.get("summary"),
        any_undeclared_difference=cc.get("any_undeclared_difference"),
        import_surface_r2_to_r3={
            k: v for k, v in (cc.get("import_surface_r2_to_r3") or {}).items()
            if k != "rows"},
        conclusion=cc.get("conclusion"))

    # ---- R34 ----------------------------------------------------------
    iface["traces_r34"] = R.get("traces_r34")

    cands = OrderedDict()
    for cname, blob in R["trial"]["nominal"].items():
        row = dict(
            title=blob["spec"]["title"],
            payload_kg=blob["spec"]["payload_kg"],
            powertrain_mass_kg=blob["spec"]["powertrain_mass_kg"],
            payload_delta_vs_ruler_kg=(
                blob["spec"]["payload_kg"]
                - R["trial"]["nominal"][CD9.RULER]["spec"]["payload_kg"]))
        for duty in DY9.DUTIES:
            e = blob["per_duty"][duty]["ensemble"]
            m = R["margins"]["nominal"].get(duty, {}).get(cname)
            row[duty] = dict(
                MJ_primary_per_payload_tkm=dict(
                    rule="8-seed ensemble",
                    min=e["MJ_primary_per_payload_tkm"]["min"],
                    median=e["MJ_primary_per_payload_tkm"]["median"],
                    max=e["MJ_primary_per_payload_tkm"]["max"]),
                MJ_tank_per_payload_tkm=dict(
                    min=e["MJ_tank_per_payload_tkm"]["min"],
                    median=e["MJ_tank_per_payload_tkm"]["median"],
                    max=e["MJ_tank_per_payload_tkm"]["max"]),
                g_CO2_per_payload_tkm=dict(
                    min=e["g_CO2_per_payload_tkm"]["min"],
                    median=e["g_CO2_per_payload_tkm"]["median"],
                    max=e["g_CO2_per_payload_tkm"]["max"]),
                fuel_L_per_100km_median=e["fuel_L_per_100km"]["median"],
                grid_kWh_median=e["grid_kWh"]["median"],
                margin_vs_ruler_pct=(dict(
                    min=m["ensemble"]["min"], median=m["ensemble"]["median"],
                    max=m["ensemble"]["max"]) if m else None))
        corner_cases = {}
        for corner, mm in R["margins"].items():
            if cname in mm.get(design, {}):
                corner_cases[corner] = mm[design][cname]["ensemble"]["min"]
        if corner_cases:
            gov = min(corner_cases, key=lambda k: corner_cases[k])
            row["worst_case_margin_pct_design_duty"] = dict(
                rule="min over the enumerated corner set (R28), "
                     "ensemble-min within each corner",
                cases=corner_cases, value=corner_cases[gov],
                governing_case=gov)
        shares = [x["correction_share_of_fuel"]
                  for d in blob["per_duty"].values()
                  for x in d["per_seed"]]
        row["fuel_correction_share"] = dict(
            rule="SIGNED, min AND max over the enumerated (duty, seed) "
                 "case set - r1 finding F4: exporting the max of a signed "
                 "quantity hid a credit",
            min=float(np.min(shares)), max=float(np.max(shares)),
            median=float(np.median(shares)),
            meaning=("fraction of this candidate's reported fuel that is a "
                     "CORRECTION - unserved energy charged back as fuel, "
                     "plus the charge-sustaining make-up (NEGATIVE where "
                     "the pack finished fuller than it started) - rather "
                     "than fuel the model watched it burn. A large "
                     "POSITIVE share means the candidate could not "
                     "actually do the mission and was credited with doing "
                     "it anyway, which is a capability finding."))
        row["verdict"] = R["advance_kill"]["candidates"].get(
            cname, {}).get("verdict", "n/a (S0R is the ruler)")
        cands[cname] = row
    iface["candidates"] = cands

    uns = {}
    for corner, blob in R["trial"].items():
        for cname, r in blob.items():
            for duty, d in r["per_duty"].items():
                uns[f"{cname}/{corner}/{duty}"] = max(
                    x["unserved_kWh"] for x in d["per_seed"])
    gov = max(uns, key=lambda k: uns[k])
    iface["unserved_energy_kWh"] = dict(
        rule="max over the enumerated (candidate, corner, duty) case set",
        value=uns[gov], governing_case=gov,
        cases_over_1kWh={k: v for k, v in sorted(uns.items()) if v > 1.0},
        meaning=("energy the prime movers and the buffer together could "
                 "not deliver. It is charged back as fuel so every "
                 "candidate completes the same mission, priced at the "
                 "run's own DUTY-AVERAGED efficiency per r2's rule, and "
                 "reported here RAW because a large value is a CAPABILITY "
                 "finding, not a fuel one."))

    iface["advance_kill"] = R["advance_kill"]["criteria"]
    iface["advance_kill_result"] = {
        k: v["verdict"] for k, v in R["advance_kill"]["candidates"].items()}
    vr = R["verdict_robustness_ESC3"]
    iface["advance_kill_robustness_ESC3"] = dict(
        rule="the SAME pre-committed criteria applied at each end of the "
             "+/-50% grid-factor sweep ESC-3 orders; a verdict that moves "
             "is reported, not smoothed",
        cases={t: {c: v["verdict"] for c, v in b.items()}
               for t, b in vr["by_factor"].items()},
        candidates_whose_verdict_moves=vr[
            "candidates_whose_verdict_moves"],
        value=vr["all_verdicts_robust"],
        governing_case=(vr["candidates_whose_verdict_moves"][0]
                        if vr["candidates_whose_verdict_moves"] else None))
    iface["etc_gate"] = dict(
        threshold_pct=P9.WHR_GATE_PCT, duty=design,
        net_margin_pct_min=R["etc_gate"]["design_duty_net_margin_pct_min"],
        net_margin_pct_median=R["etc_gate"][
            "design_duty_net_margin_pct_median"],
        mass_charge_kg=R["etc_gate"]["mass_charge_kg"],
        payload_penalty_pct=R["etc_gate"]["payload_penalty_pct"],
        fuel_gain_needed_to_clear_gate_pct=R["etc_gate"][
            "fuel_gain_needed_to_clear_gate_pct"],
        verdict=R["etc_gate"]["verdict"])

    tw = R["two_walls"]
    iface["two_walls"] = dict(
        wall1_single_ratio_infeasible=dict(
            rule="a single fixed ratio is feasible only if it holds 6% at "
                 "GCW AND keeps the engine under 2,100 rpm at 105 km/h; "
                 "solved in CLOSED FORM, not swept (F12)",
            cases={k: v["single_ratio_feasible"]
                   for k, v in tw["single_ratio_closed_form"].items()},
            ratio_ceiling=W9.ratio_ceiling(105.0 / 3.6,
                                           P9.DOGBOX.rpm_ceiling),
            governing_case="6% grade at 36,300 kg GCW",
            value=False),
        wall1_two_speed_feasible=dict(
            rule="the SAME two tests, with two ratios and the contiguity "
                 "constraint that a 2-speed lives or dies by",
            cases={k: bool(v["solve"]["feasible"] and v["sweep"]["holds_6pct"]
                           and v["sweep"]["engine_band_is_contiguous"])
                   for k, v in tw["two_speed_solve"].items()},
            value=True,
            governing_case="6% grade at 36,300 kg GCW, contiguous engine "
                           "band"),
        ratio_law=tw["ratio_law"],
        wall2_payload_delta_kg=dict(
            rule="min over the enumerated candidate set - the biggest "
                 "payload a candidate gives up to the ruler",
            cases={k: v["payload_delta_vs_ruler_kg"]
                   for k, v in cands.items()},
            value=min(v["payload_delta_vs_ruler_kg"]
                      for v in cands.values()),
            governing_case=min(cands,
                               key=lambda k: cands[k]
                               ["payload_delta_vs_ruler_kg"])))

    iface["prime_mover_at_the_pin"] = dict(
        scope=R["prime_mover"]["scope"],
        basis=R["prime_mover"]["basis"],
        worst_case=R["prime_mover"]["worst_case"],
        per_prime_mover={
            k: dict(eta_at_pin=v["efficiency"]["at_the_pin"]
                    ["eta_fuel_to_bus"],
                    engine_kg=v["equal_range"]["engine_kg"],
                    aftertreatment_kg=v["aftertreatment_kg"],
                    fuel_plus_tank_kg=v["equal_range"]["fuel_plus_tank_kg"],
                    total_charged_kg=v["equal_range"]["TOTAL_CHARGED_kg"],
                    g_CO2e_per_bus_kWh=v["emissions"]["g_CO2e_per_bus_kWh"])
            for k, v in R["prime_mover"]["prime_movers"].items()})

    iface["cold_wall_R30"] = dict(
        rule="min over the enumerated candidate set of the pack's charge "
             "acceptance at the -10 C corner's cold-soaked start, as a "
             "fraction of its warm value",
        cases={k: v["collapse_factor"] for k, v in
               R["sanity"]["cold_wall_exercised_R30"]["per_candidate"]
               .items()},
        value=(min(v["collapse_factor"] for v in
                   R["sanity"]["cold_wall_exercised_R30"]["per_candidate"]
                   .values())
               if R["sanity"]["cold_wall_exercised_R30"]["per_candidate"]
               else None),
        governing_case=(min(
            R["sanity"]["cold_wall_exercised_R30"]["per_candidate"],
            key=lambda k: R["sanity"]["cold_wall_exercised_R30"]
            ["per_candidate"][k]["collapse_factor"])
            if R["sanity"]["cold_wall_exercised_R30"]["per_candidate"]
            else None),
        preconditioning=R["sanity"]["cold_wall_exercised_R30"]
        ["per_candidate"],
        note=("R30 modelled, not assumed: the pack temperature is a state, "
              "cold-soaked at ambient and warmed from engine coolant, its "
              "own losses, or a bus-fed heater"))

    iface["retarding_shortfall_kWh"] = dict(
        rule=R["sanity"]["retarding_shortfall"]["rule"],
        cases=R["sanity"]["retarding_shortfall"]["cases"],
        value=R["sanity"]["retarding_shortfall"]["value"],
        governing_case=R["sanity"]["retarding_shortfall"]["governing_case"],
        meaning=R["sanity"]["retarding_shortfall"]["note"])
    iface["power_limited_fraction"] = dict(
        rule="max over the enumerated (candidate, corner, duty) case set - "
             "the fraction of samples on which the candidate could not "
             "deliver the demanded tractive force and took the speed its "
             "envelope allowed instead",
        cases={f"{c}/{corner}/{duty}":
               blob["per_duty"][duty]["ensemble"]["power_limited_fraction"]
               ["max"]
               for corner, cb in R["trial"].items()
               for c, blob in cb.items()
               for duty in DY9.DUTIES},
        meaning=("a capability metric, not a fuel one. The integrator gives "
                 "a candidate that cannot hold the demanded speed the speed "
                 "it CAN hold, charges it the extra time in accessory "
                 "energy, and records the shortfall - so a large value here "
                 "and a good margin together mean the margin was earned on "
                 "a slower truck."))
    iface["heat_ledger_WS6"] = R["heat_ledger"]
    iface["electricity_accounting_ESC3"] = dict(
        pef_diesel=P9.EA.pef_diesel, pef_grid=P9.EA.pef_grid,
        co2_grid_kg_per_kWh=P9.EA.co2_grid_kg_per_kWh,
        eta_charge_grid_to_pack=P9.EA.eta_charge_grid_to_pack,
        sensitivity=P9.EA.factor_sensitivity,
        applies_to=[k for k, v in cands.items()
                    if (v[design]["grid_kWh_median"] or 0.0) > 0.0])
    iface["escalations"] = [e["id"] for e in R["escalations"]]
    iface["ws2_chain_of_record"] = dict(
        map_file=EL8.ScaledEDrive(1.0, 12.0).ws2_map_file,
        map_voltage_V=EL8.ScaledEDrive(1.0, 12.0).ws2_map_voltage_V,
        ws2_rework_round=EL8.ScaledEDrive(1.0, 12.0).ws2_rework_round,
        feasible_cells=EL8.ScaledEDrive(1.0, 12.0).n_feasible_cells,
        loader="WS4 ws4_chain.WS2TractionChain (ruled), read-only",
        machine_gate_ESC2=P9.MACHINE_STRETCH_GATE_K)
    return iface


def headline(R):
    design, control = DY9.DESIGN_DUTY, DY9.CONTROL_DUTY
    rows = []
    for cname, blob in R["trial"]["nominal"].items():
        d = blob["per_duty"][design]["ensemble"]
        c = blob["per_duty"][control]["ensemble"]
        md = R["margins"]["nominal"][design].get(cname)
        mc = R["margins"]["nominal"][control].get(cname)
        rows.append(OrderedDict(
            candidate=cname, title=blob["spec"]["title"],
            payload_kg=blob["spec"]["payload_kg"],
            design_MJ_primary_per_payload_tkm_median=d[
                "MJ_primary_per_payload_tkm"]["median"],
            design_margin_pct_min=md["ensemble"]["min"] if md else None,
            design_margin_pct_median=md["ensemble"]["median"] if md else None,
            control_MJ_primary_per_payload_tkm_median=c[
                "MJ_primary_per_payload_tkm"]["median"],
            control_margin_pct_min=mc["ensemble"]["min"] if mc else None,
            control_margin_pct_median=mc["ensemble"]["median"] if mc
            else None,
            verdict=R["advance_kill"]["candidates"].get(
                cname, {}).get("verdict", "RULER")))
    return dict(table=rows,
                any_advance=R["advance_kill"]["any_advance"],
                design_duty=design, control_duty=control,
                etc_gate=R["etc_gate"]["verdict"])


# =====================================================================
#  CSV exports
# =====================================================================
def _w(data_dir, path, header, rows):
    with open(os.path.join(data_dir, path), "w") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join((f"{x:.6g}" if isinstance(x, float)
                              else str(x)) for x in r) + "\n")


def write_csvs(R, data_dir):
    rows = []
    for corner, blob in R["trial"].items():
        for cname, r in blob.items():
            for duty, d in r["per_duty"].items():
                for x in d["per_seed"]:
                    rows.append([
                        corner, cname, duty, int(x.get("seed", 0) or 0),
                        x["distance_km"], x["duration_s"],
                        x["avg_speed_kmh"], x["power_limited_fraction"],
                        x["payload_kg"], x["gcw_kg"], x["fuel_g_raw"],
                        x["fuel_g_corrected"], x["fuel_L_per_100km"],
                        x.get("grid_kWh", 0.0) or 0.0,
                        x["MJ_primary_per_payload_tkm"],
                        x["MJ_tank_per_payload_tkm"],
                        x["g_CO2_per_payload_tkm"], x["unserved_kWh"],
                        x["charge_sustain_deficit_kWh"],
                        x["correction_share_of_fuel"],
                        x["correction_eta"]])
    _w(data_dir, "candidate_runs.csv",
       ["corner", "candidate", "duty", "seed", "distance_km", "duration_s",
        "avg_speed_kmh", "power_limited_frac", "payload_kg", "gcw_kg",
        "fuel_g_raw", "fuel_g_corrected", "fuel_L_per_100km", "grid_kWh",
        "MJ_primary_per_payload_tkm", "MJ_tank_per_payload_tkm",
        "g_CO2_per_payload_tkm", "unserved_kWh", "charge_deficit_kWh",
        "correction_share", "correction_eta"], rows)

    rows = []
    for corner, m in R["margins"].items():
        for duty, d in m.items():
            for cname, blob in d.items():
                for p in blob["per_seed"]:
                    rows.append([corner, duty, cname, p["seed"],
                                 p["margin_pct"]])
    _w(data_dir, "margins.csv",
       ["corner", "duty", "candidate", "seed", "margin_vs_ruler_pct"], rows)

    rows = []
    for duty, blob in R["duties"].items():
        for s in blob["per_seed"]:
            rows.append([duty, s["seed"], s["distance_km"], s["grade_max"],
                         s["grade_min"], s["net_elevation_change_m"],
                         s["total_climb_m"], s["climb_m_per_km"],
                         s["frac_dist_grade_ge_2pct"],
                         s["frac_dist_grade_ge_5pct"], s["v_wind_ms"],
                         s["n_stops"]])
    _w(data_dir, "duty_stats.csv",
       ["duty", "seed", "distance_km", "grade_max", "grade_min",
        "net_elev_m", "total_climb_m", "climb_m_per_km", "frac_ge_2pct",
        "frac_ge_5pct", "v_wind_ms", "n_stops"], rows)

    rows = []
    for cname, blob in R["trial"]["nominal"].items():
        for k, v in blob["spec"]["mass_rows_kg"].items():
            rows.append([cname, k, v])
        rows.append([cname, "TOTAL_powertrain",
                     blob["spec"]["powertrain_mass_kg"]])
        rows.append([cname, "tare_common", blob["spec"]["tare_common_kg"]])
        rows.append([cname, "PAYLOAD", blob["spec"]["payload_kg"]])
    _w(data_dir, "mass_ledger.csv", ["candidate", "item", "kg"], rows)

    rows = []
    for cname, blob in R["heat_ledger"]["candidates"].items():
        for case, comp in blob["cases"].items():
            rows.append([cname, case,
                         comp.get("road_speed_kmh") or 0.0,
                         comp.get("case_wheel_power_kW") or 0.0]
                        + [comp.get(k, 0.0) or 0.0
                           for k in ["engine_coolant_kW",
                                     "hydraulic_retarder_coolant_kW",
                                     "engine_exhaust_kW",
                                     "compression_brake_exhaust_kW",
                                     "traction_machine_inverter_kW",
                                     "generator_rectifier_kW", "pack_kW",
                                     "brake_resistor_kW",
                                     "friction_brake_kW", "driveline_kW",
                                     "total_rejected_kW"]])
    _w(data_dir, "heat_ledger_ws6.csv",
       ["candidate", "case", "road_speed_kmh", "wheel_power_kW",
        "engine_coolant_kW", "hydraulic_retarder_coolant_kW",
        "engine_exhaust_kW", "compression_brake_exhaust_kW",
        "machine_inverter_kW", "generator_rectifier_kW", "pack_kW",
        "brake_resistor_kW", "friction_brake_kW", "driveline_kW",
        "total_rejected_kW"], rows)

    rows = []
    for k, v in R["prime_mover"]["prime_movers"].items():
        e, m, em = v["engine"], v["equal_range"], v["emissions"]
        rows.append([k, v["fuel"], e["displacement_L"], e["peak_power_kW"],
                     e["peak_BTE"],
                     v["efficiency"]["at_the_pin"]["eta_fuel_to_bus"],
                     v["efficiency"]["eta_used_for_equal_range"],
                     m["engine_kg"], v["aftertreatment_kg"],
                     m["fuel_mass_kg"], m["fuel_plus_tank_kg"],
                     m["TOTAL_CHARGED_kg"], em["g_CO2e_per_bus_kWh"]])
    _w(data_dir, "prime_mover_at_the_pin.csv",
       ["prime_mover", "fuel", "displacement_L", "peak_power_kW",
        "peak_BTE", "eta_at_pin", "eta_at_duty", "engine_kg",
        "aftertreatment_kg", "fuel_kg", "fuel_plus_tank_kg",
        "TOTAL_CHARGED_kg", "g_CO2e_per_bus_kWh"], rows)

    rows = []
    for key, v in R["two_walls"]["two_speed_solve"].items():
        for r in v["sweep"]["grade_sweep"]:
            rows.append([key, v["solve"]["ratio_high"],
                         v["solve"]["ratio_low"], r["grade"], r["status"],
                         r["gear"], r["v_hold_kmh"], r["F_available_kN"],
                         r["F_required_kN"]])
    _w(data_dir, "two_walls_sweep.csv",
       ["engine", "ratio_high", "ratio_low", "grade", "status", "gear",
        "v_hold_kmh", "F_available_kN", "F_required_kN"], rows)

    # --- R38's gate input. The gate is the LEAD's to apply (R38); this
    # file carries the measurement and the bar side by side and says so in
    # the column name, and it contains no verdict column.
    tt = R["sanity"]["trip_time_the_metric_cannot_see"]["detail"]
    rows = []
    for key in sorted(tt):
        cname, corner, duty = key.split("/")
        v = tt[key]
        p = v["paired_pct"]
        rows.append([cname, corner, duty, v["duration_s_median"],
                     v["ruler_duration_s_median"], v["delta_pct"],
                     p["min"], p["median"], p["max"],
                     P9.R38_TRIP_TIME_GATE_PCT,
                     duty == DY9.DESIGN_DUTY,
                     "LEAD_APPLIES_R38"])
    _w(data_dir, "trip_time_r38.csv",
       ["candidate", "corner", "duty", "trip_time_s_median",
        "ruler_trip_time_s_median", "pct_vs_ruler_median_of_medians",
        "paired_pct_min", "paired_pct_median", "paired_pct_max",
        "r38_gate_pct", "is_design_duty", "gate_applied_by"], rows)

    # --- ESC-WS9-8's answer, one row per compared field.
    cc = R.get("concordance_ws8_r3") or {}
    rows = []
    for impl, blob in (cc.get("implementations") or {}).items():
        for fld in blob["fields"]:
            rows.append([impl, fld["field"], fld["verdict"],
                         (fld.get("declared_in") or "").replace(",", ";"),
                         str(fld["ws8_r3"]).replace(",", ";")[:180],
                         str(fld["ws9"]).replace(",", ";")[:180]])
    _w(data_dir, "concordance_ws8_r3.csv",
       ["implementation", "field", "verdict", "declared_in",
        "ws8_r3", "ws9"], rows)

    # --- the import surface, and what moved between r2 and r3.
    d = cc.get("import_surface_r2_to_r3") or {}
    surf = cc.get("import_surface") or {}
    rows = []
    for key in sorted(surf):
        v = surf[key]
        dr = (d.get("rows") or {}).get(key, {})
        rows.append([key, v["module"], v["symbol"], v.get("resolved_in"),
                     v["found"], v["source_bytes"],
                     (v["source_sha256"] or "")[:16],
                     dr.get("status", "NOT_COMPARED"),
                     ";".join(v["used_by"])])
    _w(data_dir, "ws8_import_surface.csv",
       ["key", "ws8_module", "symbol", "resolved_in", "found",
        "source_bytes", "source_sha256_16", "status_r2_to_r3", "used_by"],
       rows)


def rebuild_derived(R, ns):
    """Rebuild every derived block from a saved trial.

    Exists so that a defect in a REPORTING block cannot cost a simulation:
    `run_ws9.py --from-checkpoint` regenerates results_ws9.json and every
    CSV without re-running a single cycle, and the numbers it produces are
    exactly the numbers a full run would produce, because the trial itself
    is read from disk rather than recomputed."""
    P9_ = sys.modules["ws9_params"]
    E9_ = sys.modules["ws9_engines"]
    R["margins_grid_lo"] = OrderedDict(
        (c, ns["margins_vs_ruler"](
            R["trial"][c],
            metric="MJ_primary_per_payload_tkm_grid_lo"))
        for c in R["trial"])
    R["margins_grid_hi"] = OrderedDict(
        (c, ns["margins_vs_ruler"](
            R["trial"][c],
            metric="MJ_primary_per_payload_tkm_grid_hi"))
        for c in R["trial"])
    R["two_walls"] = ns["two_walls_block"]()
    R["advance_kill"] = ns["advance_kill"](R["margins"])
    R["verdict_robustness_ESC3"] = ns["verdict_robustness"](R)
    _s0 = R["trial"]["nominal"][CD9.RULER]["per_duty"][
        DY9.DESIGN_DUTY]["ensemble"]["MJ_primary_per_payload_tkm"]
    _s6 = R["trial"]["nominal"]["S6"]["per_duty"][
        DY9.DESIGN_DUTY]["ensemble"]["MJ_primary_per_payload_tkm"]
    R["_s6_break_even"] = OrderedDict(
        duty=DY9.DESIGN_DUTY, statistic="ensemble_min",
        **E9_.op_break_even_island_bsfc(P9_.ADVANCE_NOMINAL_PCT,
                                        _s0["min"], _s6["min"]))
    R["_s6_break_even"]["at_median"] = E9_.op_break_even_island_bsfc(
        P9_.ADVANCE_NOMINAL_PCT, _s0["median"], _s6["median"])
    R["_s6_break_even"]["map_fraction_above_44pct_BTE"] = (
        E9_.map_area_above_bte(E9_.ENG_OP, 0.44))
    R["_s6_break_even"]["cited_claim_says"] = (
        "'large areas of the speed/load map above 44% BTE' - WS9's "
        "conservatively-scaled map is checked against that phrase rather "
        "than credited with it")
    R["heat_ledger"] = ns["heat_ledger"](ns["corners"]()["nominal"],
                                         R["trial"])
    R["determinism"] = ns["load_determinism"]()
    R["sanity"] = sanity_checks(R, ns)
    R["escalations"] = escalations(R)
    R["interface_ws9"] = ns["_clean"](interface_block(R))
    R["headline"] = headline(R)
    write_csvs(R, ns["DATA"])
    return R
