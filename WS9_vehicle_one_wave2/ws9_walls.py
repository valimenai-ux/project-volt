"""
Project Volt - WS9
THE TWO WALLS, solved in closed form.

BASELINE_v4 doctrine D8, and the assignment's title: the two walls at semi
scale are

  WALL 1  a single fixed engine ratio cannot span 105 km/h cruise under the
          engine's over-speed ceiling AND the 6% grade at 36,300 kg. WS8
          proved this for one ratio (R25: "no fixed ratio both cruises at
          105 km/h under the rpm ceiling and holds the 6% grade; 3.60:1
          delivers 11.7 kN against 24.0 kN").

  WALL 2  at fixed gross combination weight every powertrain kilogram
          displaces payload 1:1, so the objective function is efficiency
          per added kilogram.

The assignment orders S5 to "show both walls addressed BY CONSTRUCTION: the
two ratios must span cruise-under-rpm-ceiling and the 6% grade at GCW with
the mass ledger stated to the kilogram."

This module does the first half. The mass ledger does the second.

WHY CLOSED FORM. WS8's adjudication finding F12 is precisely about this:
WS8 reported the ratio ceiling as 3.60 because that was the largest entry in
a SWEPT GRID, when the physics bound is 3.7699. A bound that is a property
of somebody's grid resolution is not a bound. So WS9 solves each wall
algebraically and keeps the sweep as the ILLUSTRATION, which is what F12
asked for.  [R2-IMPL F12]
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

from ws8_params import VEH, G                        # noqa: E402
from ws8_physics import road_load_force              # noqa: E402

RPM_PER_RATIO_PER_MS = 60.0 / (2.0 * np.pi * VEH.r_dyn)
"""Engine rpm per unit of (overall ratio x road speed in m/s), at the
vehicle's dynamic radius. rpm = v * R * this. For r_dyn = 0.50 m it is
19.0986 rpm per (ratio x m/s)."""


def ratio_ceiling(v_max_ms, rpm_ceiling):
    """WALL 1, closed form. The largest overall ratio that keeps the engine
    at or under `rpm_ceiling` at road speed `v_max_ms`."""
    return rpm_ceiling / (v_max_ms * RPM_PER_RATIO_PER_MS)


def grade_force_required_N(grade, m, rho_air=None, v_ref_ms=12.5):
    """Tractive force at the contact patch needed to HOLD `grade` at GCW.

    Reported at a stated reference speed, because the aerodynamic term
    depends on it: on a 6% grade at 36.3 t, gravity is 21.3 kN and the air
    is under 0.6 kN, so the answer is insensitive to the reference and the
    reference is stated rather than hidden."""
    f, f_aero, f_roll, f_grade = road_load_force(
        np.array([v_ref_ms]), grade, m, None, None, rho_air)
    return dict(total_N=float(f[0]), aero_N=float(f_aero[0]),
                roll_N=float(f_roll[0]), grade_N=float(f_grade[0]),
                v_ref_ms=v_ref_ms, v_ref_kmh=v_ref_ms * 3.6, grade=grade,
                m_kg=float(m))


def ratio_floor(f_required_N, t_peak_Nm, eta_low, margin=0.0):
    """WALL 2's ratio half, closed form. The smallest overall ratio at which
    the engine's peak torque puts `f_required_N` at the contact patch."""
    return f_required_N * (1.0 + margin) * VEH.r_dyn / (t_peak_Nm * eta_low)


def solve_two_speed(engine, v_cruise_max_ms, rpm_ceiling, rpm_lug,
                    eta_high, eta_low, grade=0.06, m=None, rho_air=None,
                    margin=0.0, v_ref_ms=12.5, contiguity_margin=1.0):
    """The whole S5 ratio design, in five lines of algebra.

    Constraints, all three physical and none of them a preference:
      (1) WALL 1        R_high <= rpm_ceiling / (v_cruise_max * k)
      (2) WALL 2        R_low  >= F_6% * r_dyn / (T_peak * eta_low)
      (3) CONTIGUITY    R_low / R_high <= rpm_ceiling / rpm_lug

    Constraint (3) is the one a 2-speed lives or dies by and it is easy to
    miss: at the shift speed the LOW gear must be at or below its over-speed
    ceiling exactly when the HIGH gear is at or above its lugging floor,
    or there is a band of road speed in which the engine has NO GEAR. A
    truck with a hole in the middle of its speed range is not a truck; the
    hole would have to be covered by the traction machine indefinitely, from
    a buffer, which is the one thing a buffer cannot do.

    Objective: make R_high as SMALL as the constraints allow, because
    R_high sets cruise engine speed and cruise is where a line-haul truck
    spends its life. The binding solution is therefore

        R_low  = ratio_floor(...)        (WALL 2, tight)
        R_high = R_low / span_max        (CONTIGUITY, tight)

    and the design is FEASIBLE iff that R_high also satisfies WALL 1.
    """
    m = VEH.m_gcw if m is None else m
    req = grade_force_required_N(grade, m, rho_air, v_ref_ms)
    t_peak = float(np.max(engine.trq_pts))
    span_max = rpm_ceiling / rpm_lug
    span_used = span_max * contiguity_margin
    r_low = ratio_floor(req["total_N"], t_peak, eta_low, margin)
    r_high = r_low / span_used
    r_high_max = ratio_ceiling(v_cruise_max_ms, rpm_ceiling)
    feasible = bool(r_high <= r_high_max)
    return dict(
        engine=engine.name, engine_peak_torque_Nm=t_peak,
        grade=grade, force_required=req,
        torque_margin=margin,
        wall1_ratio_ceiling=r_high_max,
        wall1_basis=(f"engine at or under {rpm_ceiling:.0f} rpm at "
                     f"{v_cruise_max_ms*3.6:.0f} km/h; closed form, not a "
                     f"swept-grid property (F12)"),
        wall2_ratio_floor=r_low,
        wall2_basis=(f"engine peak torque {t_peak:.0f} Nm puts "
                     f"{req['total_N']*(1+margin):.0f} N at the contact "
                     f"patch through eta_low = {eta_low:.4f}"),
        contiguity_span_max=span_max,
        contiguity_span_used=span_used,
        contiguity_margin=contiguity_margin,
        contiguity_basis=(f"rpm ceiling {rpm_ceiling:.0f} / lugging floor "
                          f"{rpm_lug:.0f}: any larger step leaves a band of "
                          f"road speed with no engine gear at all"),
        ratio_high=r_high, ratio_low=r_low,
        box_low_ratio=span_used, axle_ratio=r_high,
        feasible=feasible,
        headroom_on_wall1=r_high_max - r_high,
        eta_high=eta_high, eta_low=eta_low,
        rpm_at_cruise_100kmh=(100.0 / 3.6) * r_high * RPM_PER_RATIO_PER_MS,
        rpm_at_cruise_max=v_cruise_max_ms * r_high * RPM_PER_RATIO_PER_MS,
        shift_speed_kmh=(rpm_lug / (r_high * RPM_PER_RATIO_PER_MS)) * 3.6,
        low_gear_floor_kmh=(rpm_lug / (r_low * RPM_PER_RATIO_PER_MS)) * 3.6,
        f_wheel_low_gear_N=t_peak * r_low * eta_low / VEH.r_dyn,
        f_wheel_high_gear_N=t_peak * r_high * eta_high / VEH.r_dyn,
        note=("the traction machine owns every road speed below the low "
              "gear's coupling floor; above it the engine always has a "
              "gear, by construction (3)"))


def verify_walls_sweep(engine, r_high, r_low, eta_high, eta_low,
                       rpm_ceiling, rpm_lug, m=None, rho_air=None,
                       grades=(0.0, 0.02, 0.03, 0.04, 0.06),
                       v_lo=1.0, v_hi=33.0, dv=0.05):
    """The ILLUSTRATION that the closed-form solve is right (F12: keep the
    sweep as the illustration, not as the bound).

    Scans road speed and reports, for each enumerated grade, the fastest
    speed at which the engine ALONE can balance road load in a gear it may
    legally be in. `no_solution` means the diesel path cannot hold that
    grade at any speed - which is exactly the verdict WS8 returned for a
    single fixed ratio, and which a correctly-solved 2-speed must not
    return for 6%."""
    m = VEH.m_gcw if m is None else m
    vs = np.arange(v_lo, v_hi, dv)
    out = {}
    band = {}
    for label, R, eta in (("high", r_high, eta_high), ("low", r_low, eta_low)):
        rpm = vs * R * RPM_PER_RATIO_PER_MS
        ok_band = (rpm >= rpm_lug) & (rpm <= rpm_ceiling)
        f = np.where(ok_band,
                     engine.t_max(np.clip(rpm, engine.rpm_pts[0],
                                          rpm_ceiling)) * R * eta / VEH.r_dyn,
                     0.0)
        band[label] = dict(force=f, in_band=ok_band, rpm=rpm)
        vb = vs[ok_band]
        out[f"{label}_gear_band_kmh"] = [float(vb[0] * 3.6),
                                         float(vb[-1] * 3.6)] if vb.size \
            else [0.0, 0.0]
    f_best = np.maximum(band["high"]["force"], band["low"]["force"])
    covered = band["high"]["in_band"] | band["low"]["in_band"]
    # the contiguity check, measured rather than asserted
    v_low_top = vs[band["low"]["in_band"]][-1] if band["low"]["in_band"].any() \
        else 0.0
    v_high_bot = vs[band["high"]["in_band"]][0] if \
        band["high"]["in_band"].any() else 0.0
    out["engine_gear_available_above_kmh"] = float(
        vs[covered][0] * 3.6) if covered.any() else None
    out["engine_band_is_contiguous"] = bool(v_high_bot <= v_low_top + dv)
    out["low_gear_top_kmh"] = float(v_low_top * 3.6)
    out["high_gear_bottom_kmh"] = float(v_high_bot * 3.6)
    rows = []
    for g in grades:
        f_res = np.array([
            float(road_load_force(np.array([x]), g, m, None, None,
                                  rho_air)[0][0]) for x in vs])
        ok = covered & (f_best >= f_res)
        if ok.any():
            v_hold = float(vs[ok][-1])
            status = "holds"
            gear = "low" if band["low"]["force"][ok][-1] >= \
                band["high"]["force"][ok][-1] else "high"
        else:
            v_hold, status, gear = 0.0, "no_solution", "-"
        i_ref = int(np.argmin(np.abs(vs - max(v_hold, 3.0))))
        rows.append(dict(grade=g, status=status, gear=gear,
                         v_hold_kmh=v_hold * 3.6,
                         F_available_kN=float(f_best[i_ref]) / 1e3,
                         F_required_kN=float(f_res[i_ref]) / 1e3))
    out["grade_sweep"] = rows
    out["holds_6pct"] = bool(
        any(r["grade"] == 0.06 and r["status"] == "holds" for r in rows))
    return out


def coupling_floor_vs_grade(engine, r_low, eta_low, rpm_lug, rpm_ceiling,
                            p_machine_sustained_kW, grades, m=None,
                            rho_air=None, v_lo=1.0, v_hi=33.0, dv=0.02):
    """THE THIRD CONSTRAINT, which the DESIGN DUTY exposes and neither wall
    names.

    Wall 1 and Wall 2 are about the 6% grade the assignment specifies. The
    grade-heavy REGIONAL corridor R29 makes the design duty carries grades
    of 7.9-10.7%, and on those a loaded combination must CRAWL. A 12-speed
    AMT crawls happily - that is what first gear is for. A 2-speed dog box
    cannot: below its low gear's coupling floor the dogs are open and the
    engine is not connected at all, so the machine is the only prime mover
    and a buffer cannot climb a mountain.

    So for each enumerated grade this asks two questions and reports both:

      v_hold_engine   the fastest speed at which the engine in LOW gear can
                      balance road load. If that speed is BELOW the coupling
                      floor, the engine cannot be connected where it would
                      be needed and the grade is unreachable on the engine.
      v_hold_machine  the fastest speed at which the machine's SUSTAINED
                      power (the 15-minute buffer swing, not its peak) can
                      balance road load. If both fail, the combination
                      cannot hold that grade at all.

    This is not a defect in the solve; it is a property of two ratios. It is
    reported here because a candidate that clears both stated walls and then
    cannot climb the duty it was specified for is exactly the kind of result
    this program exists to find, and it is a CAPABILITY finding rather than
    a fuel one - which is the class of finding that outlived every fuel
    finding in WS8.
    """
    m = VEH.m_gcw if m is None else m
    vs = np.arange(v_lo, v_hi, dv)
    rpm = vs * r_low * RPM_PER_RATIO_PER_MS
    in_band = (rpm >= rpm_lug) & (rpm <= rpm_ceiling)
    f_eng = np.where(in_band,
                     engine.t_max(np.clip(rpm, engine.rpm_pts[0],
                                          rpm_ceiling))
                     * r_low * eta_low / VEH.r_dyn, 0.0)
    v_floor = rpm_lug / (r_low * RPM_PER_RATIO_PER_MS)
    rows = []
    for g in grades:
        f_res = np.array([
            float(road_load_force(np.array([x]), g, m, None, None,
                                  rho_air)[0][0]) for x in vs])
        ok_e = in_band & (f_eng >= f_res)
        v_e = float(vs[ok_e][-1]) if ok_e.any() else 0.0
        # the machine's sustained contribution, wheel-side at 0.90
        f_m = p_machine_sustained_kW * 1e3 * 0.90 / np.maximum(vs, 0.5)
        ok_m = f_m >= f_res
        v_m = float(vs[ok_m][-1]) if ok_m.any() else 0.0
        rows.append(dict(
            grade=g,
            v_hold_engine_low_gear_kmh=v_e * 3.6,
            engine_reachable=bool(ok_e.any()),
            v_hold_machine_sustained_kmh=v_m * 3.6,
            machine_can_sustain=bool(ok_m.any()),
            holds_on_either=bool(ok_e.any() or ok_m.any()),
            F_required_at_floor_kN=float(np.interp(v_floor, vs, f_res))
            / 1e3,
            F_engine_at_floor_kN=float(np.interp(v_floor, vs, f_eng)) / 1e3))
    return dict(
        coupling_floor_kmh=v_floor * 3.6,
        p_machine_sustained_kW=p_machine_sustained_kW,
        rows=rows,
        steepest_grade_held_on_the_engine=max(
            [r["grade"] for r in rows if r["engine_reachable"]],
            default=0.0),
        grades_that_fail=[r["grade"] for r in rows
                          if not r["holds_on_either"]],
        finding=("a 2-speed dog box clears the specified 6% grade by "
                 "construction and then meets a THIRD constraint on the "
                 "design duty: the low gear's coupling floor sits above the "
                 "crawl speed a grade steeper than about 6-7% forces, and "
                 "below that floor the engine is not connected at all"))


def two_speed_frontier(engine, v_cruise_max_ms, rpm_ceiling, rpm_lug,
                       eta_high, eta_low, contiguity_margin=1.0,
                       grades=(0.06, 0.07, 0.08, 0.09, 0.10, 0.11),
                       m=None, rho_air=None, margin=0.0, v_ref_ms=12.5):
    """What a 2-speed CAN and CANNOT be asked to do, in closed form.

    For each target grade: the low ratio Wall 2 requires, the ratio SPAN
    that implies against the high ratio Wall 1 permits, and - when that span
    exceeds the contiguity bound - the band of road speed left with NO
    ENGINE GEAR AT ALL.

    The result is a frontier, not a design: a 2-speed dog box may have the
    steep grade OR a contiguous engine band, and beyond about 6-7% at
    36,300 kg it cannot have both. That is the honest statement of what two
    ratios buy, and it is what the specified 6% grade conceals - the
    assignment's wall is exactly at the edge of what two ratios can do."""
    m = VEH.m_gcw if m is None else m
    t_peak = float(np.max(engine.trq_pts))
    span_bound = rpm_ceiling / rpm_lug * contiguity_margin
    r_high_max = ratio_ceiling(v_cruise_max_ms, rpm_ceiling)
    rows = []
    for g in grades:
        req = grade_force_required_N(g, m, rho_air, v_ref_ms)
        r_low = ratio_floor(req["total_N"], t_peak, eta_low, margin)
        r_high_contig = r_low / span_bound
        contiguous_possible = bool(r_high_contig <= r_high_max)
        rpm_cruise = ((100.0 / 3.6) * r_high_contig * RPM_PER_RATIO_PER_MS
                      if contiguous_possible else None)
        # if contiguity is impossible, take the highest ratio Wall 1 allows
        # and report the hole it leaves
        v_low_top = rpm_ceiling / (r_low * RPM_PER_RATIO_PER_MS)
        v_high_bot = rpm_lug / (r_high_max * RPM_PER_RATIO_PER_MS)
        rows.append(dict(
            grade=g,
            F_required_kN=req["total_N"] / 1e3,
            ratio_low_required=r_low,
            span_required_against_wall1=r_low / r_high_max,
            span_bound=span_bound,
            contiguous_two_speed_possible=contiguous_possible,
            ratio_high_if_contiguous=(r_high_contig if contiguous_possible
                                      else None),
            rpm_at_100kmh_if_contiguous=rpm_cruise,
            gap_low_top_kmh=(v_low_top * 3.6 if not contiguous_possible
                             else None),
            gap_high_bottom_kmh=(v_high_bot * 3.6
                                 if not contiguous_possible else None),
            gap_width_kmh=((v_high_bot - v_low_top) * 3.6
                           if not contiguous_possible else 0.0)))
    return dict(
        wall1_ratio_ceiling=r_high_max,
        contiguity_span_bound=span_bound,
        rows=rows,
        steepest_contiguous_grade=max(
            [r["grade"] for r in rows
             if r["contiguous_two_speed_possible"]], default=0.0),
        finding=("a 2-speed dog box may have the steep grade OR a "
                 "contiguous engine band. The assignment's 6% wall sits "
                 "almost exactly on the frontier, which is why S5 clears "
                 "it by construction and fails one point above it."))
