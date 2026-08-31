"""
Project Volt - WS11
Capability-limited forward simulation: trip time (R38) and the sustained
climb.

The fuel metric of record follows the DEMAND trace - every vehicle is given
the identical wheel-power trace and shortfalls are booked as unserved
energy and fuel-corrected (the WS4/G1 net-energy convention). That
convention deliberately cannot see time. R38 asks for trip time, and the
WS1 s4.4 climb corner asks what speed each vehicle actually settles at, so
both need a second, capability-aware pass. This module is that pass.

It is a REDUCED-ORDER model and produces settled speeds and elapsed times,
never a fuel number. Capability is expressed as available tractive FORCE
vs road speed (power/speed is singular at rest), capped by WS1's 13.5 kN
adhesion/traction limit, which both vehicles share.
"""
import numpy as np

from volt_params import VEH, G
from ws4_models import BATT_ETA_CHG, BATT_ETA_DIS
from ws4_sim import (pinned_point, SER_LO, SER_HI, SOC_START,
                     EMERG_LO)

import ws11_params as P
import ws11_ruler as R

V_TABLE_KMH = np.arange(0.0, 130.0 + 1e-9, 0.25)
_V_MS = V_TABLE_KMH / 3.6


def ruler_force_table(engine, derate, veh, p_acc_kw, eta_gear=None,
                      eta_final=None, pump_kw_at_1800=None,
                      lockup_slip=None):
    """Tractive force [N] and wheel power [kW] the ruler can deliver vs
    road speed, taking the best gear (kickdown) and the converter where it
    helps.

    The four driveline levers default to the HEADLINE (ruler-favourable)
    values, the same defaults `ws11_ruler.run_ruler` uses, so the
    capability pass and the fuel pass are always on one set of
    assumptions."""
    eta_gear_t = P.ETA_GEAR if eta_gear is None else tuple(eta_gear)
    eta_final = P.ETA_FINAL if eta_final is None else float(eta_final)
    pump_k = (P.PUMP_KW_AT_1800 if pump_kw_at_1800 is None
              else float(pump_kw_at_1800))
    slip = (P.LOCKUP_SLIP_LOSS if lockup_slip is None
            else float(lockup_slip))
    w_wheel = np.maximum(_V_MS, 1e-9) / veh.r_dyn
    ratios = np.asarray(P.GEAR_RATIOS, float)
    eta_gear = np.asarray(eta_gear_t, float)
    i_tot = ratios[:, None] * P.AXLE_RATIO
    w_t = w_wheel[None, :] * i_tot
    n_t = w_t * 60.0 / (2 * np.pi)

    def tmax(n):
        return engine.t_max(np.clip(n, engine.rpm_pts[0],
                                    engine.rpm_pts[-1])) * derate

    # locked branch
    lock_ok = np.zeros(w_t.shape, bool)
    lock_ok[P.LOCKUP_MIN_GEAR - 1:, :] = True
    lock_ok &= (V_TABLE_KMH[None, :] >= P.V_LOCKUP_MIN_KMH)
    lock_ok &= (n_t >= engine.idle_rpm) & (n_t <= P.N_MAX_RPM)
    t_par_lock = (R.pump_kw(n_t, pump_k) + p_acc_kw) * 1e3 \
        / np.maximum(w_t, 1e-9)
    t_out_lock = np.clip(tmax(n_t) - t_par_lock, 0.0, None) \
        * (1.0 - slip)
    f_lock = np.where(lock_ok, t_out_lock * i_tot / veh.r_dyn
                      * eta_gear[:, None] * eta_final, 0.0)

    # converter branch at wide-open throttle
    w_lo = engine.idle_rpm * 2 * np.pi / 60.0
    w_hi = P.N_MAX_RPM * 2 * np.pi / 60.0
    w_e = np.maximum(R.tc_wot_omega_e(w_t, engine, derate, w_lo, w_hi), w_lo)
    n_e = w_e * 60.0 / (2 * np.pi)
    sr = np.clip(w_t / np.maximum(w_e, 1e-9), 0.0, 1.0)
    t_par_un = (R.pump_kw(n_e, pump_k) + p_acc_kw) * 1e3 \
        / np.maximum(w_e, 1e-9)
    t_imp = np.minimum(R.tc_capacity(sr) * w_e ** 2,
                       np.clip(tmax(n_e) - t_par_un, 0.0, None))
    t_out_un = R.tc_torque_ratio(sr) * t_imp
    f_un = np.where(n_e <= P.N_MAX_RPM + 1e-6,
                    t_out_un * i_tot / veh.r_dyn
                    * eta_gear[:, None] * eta_final, 0.0)

    f = np.max(np.maximum(f_lock, f_un), axis=0)
    f = np.minimum(f, veh.F_trac_max)
    return f, f * _V_MS / 1e3


def load_capability_curve(ws2_dir):
    raw = np.genfromtxt(ws2_dir + "/data/capability_vs_rpm.csv",
                        delimiter=",", names=True)
    return np.asarray(raw["rpm"], float), \
        np.asarray(raw["T_peak_662V_Nm"], float)


def motor_force_table(chain, cap_rpm, cap_trq, veh):
    """Tractive force [N] at the traction machine's 1-min peak envelope
    (WS2 capability_vs_rpm.csv, 662 V column) through the 10:1 reduction."""
    n_m = _V_MS / veh.r_dyn * chain.ratio * 60.0 / (2 * np.pi)
    t_m = np.interp(n_m, cap_rpm, cap_trq)
    t_m = np.where(n_m <= cap_rpm[-1], t_m, 0.0)
    f = t_m * chain.ratio / veh.r_dyn * chain.eta_red
    return np.minimum(f, veh.F_trac_max)


def _road_load_N(v, grade, m, veh):
    theta = np.arctan(grade)
    f_aero = 0.5 * veh.rho_air * veh.CdA * v * v
    f_roll = veh.Crr * m * G * np.cos(theta) if v > 0.05 else 0.0
    f_grade = m * G * np.sin(theta)
    return f_aero + f_roll + f_grade


def _route(cyc):
    t = cyc["t"]
    v = cyc["v"]
    dt = float(np.median(np.diff(t)))
    s = np.concatenate(([0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))))
    g = np.asarray(cyc["grade"], float) * np.ones_like(v)
    return t, v, s, g, dt


# [WS11-DECLARED] a grade counts as SUSTAINED once the vehicle has been on
# it continuously for this long. Below it a grade is a transient feature of
# the synthesised route and the vehicle never reaches a settled speed on it.
SUSTAINED_GRADE_MIN_S = 120.0
SUSTAINED_GRADE_MIN = 0.055


def _loop(cyc, m, veh, force_fn, energy_fn=None):
    """Time-parameterised capability run.

    The vehicle is given the demanded speed profile as a function of TIME
    and tracks it exactly wherever capability allows; where it does not,
    the vehicle falls behind and never recovers the lost distance (it
    never exceeds the demanded speed). The grade is read at the vehicle's
    OWN position, so a vehicle that has fallen behind is on the piece of
    road it is actually on.

    CAPABILITY IS ENFORCED ON EVERY SAMPLE: `a = min(a_des, a_cap)`.
    Round 1 consulted `a_cap` only while the vehicle was accelerating, so
    once it was tracking the demanded speed it held that speed however
    negative `a_cap` had become - on the inserted 6% climb the ruler held
    94.95 km/h for all 3,791 samples with a 983 N force deficit
    (adjudication r1/B2). With the limit enforced the vehicle decelerates
    onto its own capability curve, which is what makes
    `settled_speed_on_sustained_climb_kmh` a settled speed rather than a
    restatement of the demand.

    Trip time = the demanded duration + (distance shortfall) / (the route's
    demanded average moving speed). The make-up term uses a property of the
    ROUTE, so it is identical in form for every vehicle [WS11-DECLARED].
    """
    t, v_dem, s_dem, g_ref, dt = _route(cyc)
    s_end = float(s_dem[-1])
    lam = veh.lam_rot
    n = v_dem.size
    moving = v_dem > 0.1
    t_moving = float(np.sum(moving) * dt)
    v_avg_moving = s_end / t_moving if t_moving > 0 else 1.0
    v = float(v_dem[0])
    s = 0.0
    n_limited = 0
    v_min = 1e9
    v_grade_min = 1e9
    deficit_max = 0.0
    # sustained-grade run tracking: (duration, speed at the end of the run)
    run_s = 0.0
    run_v_end = 0.0
    best_run_s = 0.0
    best_run_v_end = None
    for i in range(n):
        v_tgt = float(v_dem[i])
        grade = float(np.interp(s, s_dem, g_ref))
        f_res = _road_load_N(v, grade, m, veh)
        f_av = force_fn(v)
        a_cap = (f_av - f_res) / (lam * m)
        a_des = (v_tgt - v) / dt
        # capability is a ceiling on acceleration at EVERY sample, not only
        # while accelerating. On a sustained grade a_cap goes negative and
        # the vehicle must slow to its own capability curve.
        if a_cap < a_des:
            a = a_cap
            n_limited += 1
        else:
            a = a_des
        v_new = max(0.0, min(v + a * dt, v_tgt))
        v_bar = 0.5 * (v + v_new)
        if energy_fn is not None:
            p_used = max(0.0, (lam * m * (v_new - v) / dt + f_res) * v_bar
                         / 1e3)
            energy_fn(p_used, v_bar, dt)
        s += v_bar * dt
        v = v_new
        if grade >= SUSTAINED_GRADE_MIN and v_tgt > 30.0 / 3.6:
            run_s += dt
            run_v_end = v
            if v < v_grade_min:
                v_grade_min = v
        else:
            if run_s > best_run_s:
                best_run_s = run_s
                best_run_v_end = run_v_end
            run_s = 0.0
        if v_tgt > 30.0 / 3.6:
            if v < v_min:
                v_min = v
            if (v_tgt - v) > deficit_max:
                deficit_max = v_tgt - v
    if run_s > best_run_s:
        best_run_s = run_s
        best_run_v_end = run_v_end
    sustained = best_run_s >= SUSTAINED_GRADE_MIN_S
    t_dem = float(t[-1] - t[0])
    shortfall_m = max(0.0, s_end - s)
    t_extra = shortfall_m / v_avg_moving
    return dict(
        demanded_duration_s=t_dem,
        demanded_distance_m=s_end,
        distance_reached_m=s,
        distance_shortfall_m=shortfall_m,
        makeup_time_s=t_extra,
        trip_time_s=t_dem + t_extra,
        capability_limited_s=n_limited * dt,
        min_speed_above_30kmh_demand_kmh=(v_min * 3.6 if v_min < 1e8
                                          else 0.0),
        max_speed_deficit_kmh=deficit_max * 3.6,
        # the speed the vehicle has SETTLED at when it leaves the longest
        # continuous run of >=5.5% grade, and only when that run is long
        # enough to settle on. None when the route carries no such run.
        settled_speed_on_sustained_climb_kmh=(best_run_v_end * 3.6
                                              if sustained else None),
        longest_sustained_grade_run_s=best_run_s,
        # round 1's field, correctly named: the MINIMUM speed reached on
        # any sample whose grade is >=5.5%, sustained or not. Exported so
        # no previously reported quantity is dropped.
        min_speed_on_grade_ge_5p5pct_kmh=(v_grade_min * 3.6
                                          if v_grade_min < 1e8 else None),
        route_avg_moving_speed_kmh=v_avg_moving * 3.6,
        sustained_climb_present=bool(sustained))


def ruler_trip(cyc, m, engine, derate, veh, p_acc_kw, **levers):
    f_tab, _ = ruler_force_table(engine, derate, veh, p_acc_kw,
                                 **levers)

    def force(v):
        return float(np.interp(v * 3.6, V_TABLE_KMH, f_tab))
    return _loop(cyc, m, veh, force)


def candidate_trip(cyc, m, engine, gen, chain, cap_rpm, cap_trq, veh,
                   derate, usable_kwh, p_aux_kw, ser_band=None,
                   dis_cap_bus_kw=125.0):
    """Reduced-order capability model for a pure-series candidate: pinned
    genset with SOC hysteresis, pack at the R8 bus-side discharge envelope
    over the delivered usable energy, chain at WS2's measured map, machine
    at its 1-min peak envelope.

    [WS11-DECLARED] the chain efficiency used here is tabulated once at the
    fully-available bus power rather than re-solved per sample; it moves
    trip time, not fuel, and the same table is used for both directions.
    """
    pin = pinned_point(engine, gen, derate)
    # emergency band: below EMERG_LO the series engine leaves the pin and
    # follows load up to its derated continuous rating - the same rule the
    # ratified fuel simulator applies.
    p_bus_emerg = float(gen.elec_from_shaft(engine.rated_cont_rpm,
                                            engine.rated_cont_kw * derate))
    f_mot = motor_force_table(chain, cap_rpm, cap_trq, veh)
    p_bus_max = max(pin["p_bus_kw"] + dis_cap_bus_kw - p_aux_kw, 1.0)
    eta_tab = np.asarray(chain.eta_bus_to_wheel(
        _V_MS, np.full_like(_V_MS, p_bus_max * 0.5)), float)
    lo, hi = (SER_LO, SER_HI) if ser_band is None else ser_band
    e_cap = usable_kwh * 3.6e6
    st = {"e": e_cap * SOC_START, "on": False, "soc_min": SOC_START,
          "gen_on_s": 0.0}

    def force(v):
        e = st["e"]
        if e < lo * e_cap:
            st["on"] = True
        elif e > hi * e_cap:
            st["on"] = False
        p_gen = pin["p_bus_kw"] if st["on"] else 0.0
        if e < EMERG_LO * e_cap:
            p_gen = max(p_gen, p_bus_emerg)
        dt = 0.1
        p_pack = min(dis_cap_bus_kw, max(0.0, e) / dt / 1e3 * BATT_ETA_DIS)
        p_bus = max(0.0, p_gen + p_pack - p_aux_kw)
        eta = float(np.interp(v * 3.6, V_TABLE_KMH, eta_tab))
        p_wheel = p_bus * eta
        f_pow = p_wheel * 1e3 / max(v, 0.5)
        return min(f_pow, float(np.interp(v * 3.6, V_TABLE_KMH, f_mot)),
                   veh.F_trac_max)

    def energy(p_wheel_kw, v, dt):
        eta = float(np.interp(v * 3.6, V_TABLE_KMH, eta_tab))
        p_bus_load = p_wheel_kw / max(eta, 1e-3) + p_aux_kw
        p_gen = pin["p_bus_kw"] if st["on"] else 0.0
        if st["e"] < EMERG_LO * e_cap:
            p_gen = max(p_gen, p_bus_emerg)
        if p_gen > 0.0:
            st["gen_on_s"] += dt
        p_batt = p_gen - p_bus_load
        if p_batt >= 0.0:
            st["e"] = min(e_cap, st["e"] + p_batt * 1e3 * BATT_ETA_CHG * dt)
        else:
            st["e"] = max(0.0, st["e"] + p_batt * 1e3 / BATT_ETA_DIS * dt)
        st["soc_min"] = min(st["soc_min"], st["e"] / e_cap)

    out = _loop(cyc, m, veh, force, energy)
    out["soc_min"] = st["soc_min"]
    out["p_bus_pinned_kW"] = pin["p_bus_kw"]
    out["p_bus_emergency_kW"] = p_bus_emerg
    out["genset_on_s"] = st["gen_on_s"]
    return out


# ------------------------------------------------------- climb-inserted cycle
def insert_climb(cyc, at_frac=0.30, dist_m=None, grade=None,
                 speed_kmh=None):
    """Splice WS1 s4.4's sustained climb into a cycle at `at_frac` of the
    route distance. The demanded speed through the insert is the demanded
    speed at the splice point; the grade is constant. Both vehicles face
    the identical inserted demand.

    `speed_kmh` overrides the demanded speed through the insert
    (adjudication r1/m12). The splice point at 30% of route distance
    happens to sit at 94.95 km/h, which is a HARDER corner than WS1 s4.4's
    own posing of the same climb (its table runs 40-100 km/h and its
    forward simulation is run at 85 km/h, of which WS1 says "holding
    85 km/h up a 10 km 6% grade is not achievable on any buffer this study
    contemplates"). The 85 km/h reading is exported as a bracket so the
    severity of WS11's choice is on the record instead of implicit.
    """
    dist_m = P.CLIMB_KM * 1000.0 if dist_m is None else dist_m
    grade = P.CLIMB_GRADE if grade is None else grade
    t, v, s, g, dt = _route(cyc)
    i0 = int(np.searchsorted(s, at_frac * s[-1]))
    v_c = float(v[i0])
    if v_c < 5.0:
        i0 = int(np.argmax(v))
        v_c = float(v[i0])
    v_at_splice = v_c
    if speed_kmh is not None:
        v_c = float(speed_kmh) / 3.6
    n_ins = int(round(dist_m / v_c / dt))
    v_new = np.concatenate([v[:i0], np.full(n_ins, v_c), v[i0:]])
    g_new = np.concatenate([g[:i0], np.full(n_ins, grade), g[i0:]])
    t_new = np.arange(v_new.size) * dt
    out = dict(cyc)
    out["t"] = t_new
    out["v"] = v_new
    out["grade"] = g_new
    out["name"] = cyc.get("name", "cycle") + "+CLIMB"
    out["s"] = np.concatenate(([0.0], np.cumsum(
        0.5 * (v_new[1:] + v_new[:-1]) * np.diff(t_new))))
    out["climb_insert"] = dict(at_distance_m=float(s[i0]),
                               demanded_speed_kmh=v_c * 3.6,
                               demanded_speed_at_splice_point_kmh=(
                                   v_at_splice * 3.6),
                               demanded_speed_overridden=bool(
                                   speed_kmh is not None),
                               inserted_distance_m=dist_m,
                               grade_pct=grade * 100.0,
                               inserted_samples=n_ins,
                               elevation_gain_m=dist_m * grade)
    return out
