"""
Project Volt - WS11
The RULER: stock Isuzu NPR-HD, 4HK1-TC + Aisin A465id 6-speed torque-
converter automatic with lock-up (2nd-6th) + 4.555 rear axle.

The ruler follows the IDENTICAL wheel-power trace the candidates follow
(WS4/G1 net-energy convention: `all modes follow the identical wheel-power
trace`), at the same lam_rot = 1.04, so the comparison is on one road load.
Wheel power comes from WS1's own `volt_physics.wheel_power`.

Fuel comes from WS4's ratified reference Willans map `4HK1-TC-ref-W`
(205.198 g/kWh island) - the map the assignment names. Nothing about the
map is re-fitted here.

Part-load everywhere (R9): the engine is queried at its actual (rpm,
torque) on every 0.1 s sample. No peak-point scalar exists in this file.
"""
import numpy as np

import volt_physics as vp                    # WS1, read-only
from volt_params import VEH, CTL             # WS1, read-only
from ws4_models import (ENG_REF, LHV_KJ_PER_G,  # WS4, read-only
                        BSFC_FROM_ETA)

import ws11_params as P


# ---------------------------------------------------------------- converter
_TC_SR = np.asarray(P.TC_SR, float)
_TC_TR = np.asarray(P.TC_TR, float)
_TC_CR = np.asarray(P.TC_CAP_REL, float)


def tc_torque_ratio(sr):
    return np.interp(np.clip(sr, 0.0, 1.0), _TC_SR, _TC_TR)


def tc_capacity(sr):
    """C(SR) in N.m.s^2/rad^2 such that T_impeller = C * omega_e^2."""
    return P.TC_C0 * np.interp(np.clip(sr, 0.0, 1.0), _TC_SR, _TC_CR)


def tc_solve_omega_e(w_t, t_turb_req, w_lo, w_hi, iters=64):
    """Vectorised bisection for impeller (engine) speed [rad/s].

    Finds w_e such that the converter delivers exactly `t_turb_req` at the
    turbine when the turbine turns at `w_t`:
        T_turb(w_e) = TR(w_t/w_e) * C(w_t/w_e) * w_e^2
    T_turb is monotone increasing in w_e at fixed w_t, so bisection is
    exact to the iteration count.
    """
    lo = np.full_like(w_t, w_lo, dtype=float)
    hi = np.full_like(w_t, w_hi, dtype=float)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        sr = np.where(mid > 1e-9, w_t / np.maximum(mid, 1e-9), 0.0)
        t = tc_torque_ratio(sr) * tc_capacity(sr) * mid ** 2
        too_small = t < t_turb_req
        lo = np.where(too_small, mid, lo)
        hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)


def tc_wot_omega_e(w_t, engine, derate, w_lo, w_hi, iters=64):
    """Wide-open-throttle converter operating point: the engine speed at
    which the full-load curve and the converter capacity balance."""
    lo = np.full_like(w_t, w_lo, dtype=float)
    hi = np.full_like(w_t, w_hi, dtype=float)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        sr = np.where(mid > 1e-9, w_t / np.maximum(mid, 1e-9), 0.0)
        t_cap = tc_capacity(sr) * mid ** 2
        t_av = engine.t_max(mid * 60.0 / (2 * np.pi)) * derate
        # engine accelerates while it makes more than the converter absorbs
        lo = np.where(t_av > t_cap, mid, lo)
        hi = np.where(t_av > t_cap, hi, mid)
    return 0.5 * (lo + hi)


def pump_kw(rpm, kw_at_1800=None):
    """AT pump/churning parasitic [kW] at engine speed `rpm`.

    `kw_at_1800` is a declared lever (adjudication r1/B1): the headline
    value is ruler-favourable and the pessimistic declared end is
    P.PUMP_KW_AT_1800_PESSIMISTIC. Default = headline.
    """
    k = P.PUMP_KW_AT_1800 if kw_at_1800 is None else float(kw_at_1800)
    return k * np.asarray(rpm, float) / 1800.0


# ------------------------------------------------------------------ the sim
def run_ruler(cyc, m, veh=VEH, engine=ENG_REF, derate=1.0,
              p_acc_kw=None, idle_neutral=None, lam=None, trace=False,
              shift_schedule="fuel_optimal", eta_gear=None, eta_final=None,
              pump_kw_at_1800=None, lockup_slip=None,
              derate_load_fraction=False):
    """One ruler run over one cycle realisation.

    Returns the same shape of totals block the candidate runs return, so
    the two are differenced without any unit or convention step in between.

    The four driveline levers `eta_gear`, `eta_final`, `pump_kw_at_1800`
    and `lockup_slip` default to the HEADLINE (ruler-favourable) values in
    ws11_params.py. Each has a declared pessimistic end in the same file
    and each is exercised as a bracket (adjudication r1/B1: in round 1
    none of the four entered the bracket set).

    `derate_load_fraction` (adjudication r1/m8): when True the engine's
    load fraction phi - and hence the smoke-limit term of the BSFC map -
    is referenced to the DERATED full-load curve, which is the convention
    WS4's `_bsfc_fast` applies to the candidates. Default False = the
    round-1 behaviour (phi against the underated curve), kept as the
    headline so no verdict number moves silently; the difference is
    measured and exported.
    """
    p_acc_kw = P.P_ACC_CRANK_KW if p_acc_kw is None else float(p_acc_kw)
    idle_neutral = P.IDLE_NEUTRAL if idle_neutral is None else idle_neutral
    lam = veh.lam_rot if lam is None else lam
    eta_gear_t = P.ETA_GEAR if eta_gear is None else tuple(eta_gear)
    eta_final = P.ETA_FINAL if eta_final is None else float(eta_final)
    pump_k = (P.PUMP_KW_AT_1800 if pump_kw_at_1800 is None
              else float(pump_kw_at_1800))
    slip = (P.LOCKUP_SLIP_LOSS if lockup_slip is None
            else float(lockup_slip))

    def _pump(rpm):
        return pump_kw(rpm, pump_k)

    def bsfc(n, t):
        """BSFC lookup [g/kWh].

        Default = `engine.bsfc`, whose load fraction phi is referred to
        the UNDERATED full-load curve. With `derate_load_fraction` the
        smoke-limit term is referred to the DERATED curve instead, which
        is what WS4's `_bsfc_fast(engine, rpm, trq, tmax)` does for the
        candidates when it is handed the derated `tmax`. Only phi moves;
        bmep and fmep are properties of the actual (rpm, torque) and are
        untouched. Adjudication r1/m8."""
        if not (derate_load_fraction and derate != 1.0):
            return engine.bsfc(n, t)
        n = np.asarray(n, float)
        t = np.asarray(t, float)
        tmax_d = np.maximum(engine.t_max(n) * derate, 1e-6)
        phi = np.clip(t / tmax_d, 0.0, 1.0)
        bmep = engine.bmep_bar(t)
        fmep = engine.fmep_bar(n)
        mech = np.where(bmep > 0, bmep / (bmep + fmep), 0.0)
        eta = engine.eta_i0 * engine._f_n(n) * engine._f_phi(phi) * mech
        return np.where(eta > 1e-4, BSFC_FROM_ETA / np.maximum(eta, 1e-4),
                        np.inf)

    t = cyc["t"]
    v = cyc["v"]
    dt = float(np.median(np.diff(t)))
    n = v.size

    wp = vp.wheel_power(t, v, cyc["grade"], m, lam=lam, veh=veh)
    p_wheel = wp["P_wheel"] / 1e3                       # kW

    w_wheel = np.maximum(v, 1e-9) / veh.r_dyn                 # rad/s
    moving = v >= P.V_STOPPED_KMH / 3.6

    # ---- locked-gear candidate operating points, all gears, vectorised ---
    ratios = np.asarray(P.GEAR_RATIOS, float)
    eta_gear = np.asarray(eta_gear_t, float)
    w_e_lock = w_wheel[None, :] * P.AXLE_RATIO * ratios[:, None]   # rad/s
    n_e_lock = w_e_lock * 60.0 / (2 * np.pi)

    def tmax(n):
        """Derated full-load torque, rpm clamped to the curve's own
        support so a floating-point 699.9999999 does not fall off the
        left edge of np.interp and read as zero torque."""
        return engine.t_max(np.clip(n, engine.rpm_pts[0],
                                    engine.rpm_pts[-1])) * derate

    p_drive = np.clip(p_wheel, 0.0, None)
    # wheel -> transmission output -> transmission input (turbine)
    p_turb = (p_drive[None, :] / eta_final) / eta_gear[:, None]
    p_turb = p_turb / (1.0 - slip)
    p_shaft_lock = p_turb + _pump(n_e_lock) + p_acc_kw
    t_e_lock = p_shaft_lock * 1e3 / np.maximum(w_e_lock, 1e-9)
    t_av_lock = tmax(n_e_lock)

    feas = ((n_e_lock >= P.N_LUG_MIN_RPM) & (n_e_lock <= P.N_MAX_RPM)
            & (t_e_lock <= t_av_lock * (1.0 - P.TORQUE_RESERVE_FRAC)))
    # lock-up is only offered from 2nd gear and above V_LOCKUP_MIN_KMH
    lock_ok = np.zeros_like(feas)
    lock_ok[P.LOCKUP_MIN_GEAR - 1:, :] = True
    lock_ok &= (v[None, :] * 3.6 >= P.V_LOCKUP_MIN_KMH)
    feas &= lock_ok
    feas &= moving[None, :]

    fuel_lock = bsfc(n_e_lock, np.clip(t_e_lock, 1e-9, None)) \
        * np.clip(p_shaft_lock, 0.0, None) / 3600.0        # g/s
    fuel_lock = np.where(feas, fuel_lock, np.inf)

    # ---- unlocked (converter) branch, all gears, vectorised --------------
    w_lo = engine.idle_rpm * 2 * np.pi / 60.0
    w_hi = P.N_MAX_RPM * 2 * np.pi / 60.0
    w_t = w_e_lock                                          # turbine speed
    # turbine torque required to deliver p_turb at the turbine
    t_turb_req = p_turb * 1e3 / np.maximum(w_t, 1e-9)
    w_e_un = tc_solve_omega_e(w_t, t_turb_req, w_lo, w_hi)
    w_e_un = np.maximum(w_e_un, w_lo)                       # idle floor
    sr_un = np.clip(w_t / np.maximum(w_e_un, 1e-9), 0.0, 1.0)
    t_imp_un = tc_capacity(sr_un) * w_e_un ** 2
    n_e_un = w_e_un * 60.0 / (2 * np.pi)
    p_shaft_un = (t_imp_un * w_e_un / 1e3) + _pump(n_e_un) + p_acc_kw
    t_e_un = p_shaft_un * 1e3 / np.maximum(w_e_un, 1e-9)
    t_av_un = tmax(n_e_un)
    t_turb_del = tc_torque_ratio(sr_un) * t_imp_un
    delivers = (t_turb_del >= t_turb_req - 1e-9) | (t_turb_req <= 1e-9)
    feas_un = ((n_e_un <= P.N_MAX_RPM)
               & (t_e_un <= t_av_un * (1.0 - P.TORQUE_RESERVE_FRAC))
               & delivers & moving[None, :])
    fuel_un = bsfc(n_e_un, np.clip(t_e_un, 1e-9, None)) \
        * np.clip(p_shaft_un, 0.0, None) / 3600.0
    fuel_un = np.where(feas_un, fuel_un, np.inf)

    # ---- capability envelope (used for the shortfall book and by the
    # ---- trip-time simulator), all gears, both branches -------------------
    p_w_av_lock = np.clip(
        (t_av_lock * w_e_lock / 1e3) - _pump(n_e_lock) - p_acc_kw,
        0.0, None) * (1.0 - slip) \
        * eta_gear[:, None] * eta_final
    p_w_av_lock = np.where(lock_ok & (n_e_lock >= engine.idle_rpm)
                           & (n_e_lock <= P.N_MAX_RPM), p_w_av_lock, 0.0)
    w_e_wot = np.maximum(tc_wot_omega_e(w_t, engine, derate, w_lo, w_hi),
                         w_lo)
    sr_wot = np.clip(w_t / np.maximum(w_e_wot, 1e-9), 0.0, 1.0)
    n_e_wot = w_e_wot * 60.0 / (2 * np.pi)
    t_imp_wot = np.minimum(
        tc_capacity(sr_wot) * w_e_wot ** 2,
        np.clip(tmax(n_e_wot) - _pump(n_e_wot) * 1e3
                / np.maximum(w_e_wot, 1e-9)
                - p_acc_kw * 1e3 / np.maximum(w_e_wot, 1e-9), 0.0, None))
    p_w_av_un = tc_torque_ratio(sr_wot) * t_imp_wot * w_t / 1e3 \
        * eta_gear[:, None] * eta_final
    p_w_av_un = np.where(n_e_wot <= P.N_MAX_RPM + 1e-6, p_w_av_un, 0.0)
    p_wheel_avail = np.max(np.maximum(p_w_av_lock, p_w_av_un), axis=0)

    # ---- gear state machine ---------------------------------------------
    gear = np.zeros(n, dtype=np.int8)
    locked = np.zeros(n, dtype=bool)
    g_cur = 0
    t_last_shift = -1e9
    n_shifts = 0
    # per-sample selection: best over {locked gear g} U {unlocked gear g}
    best_fuel = np.minimum(fuel_lock, fuel_un)
    best_is_lock = fuel_lock <= fuel_un
    if shift_schedule == "sequential":
        # realistic single-step schedule: only the adjacent gears are
        # reachable at each sample (bracket, not the headline)
        pass
    for i in range(n):
        if not moving[i]:
            g_cur = 0
            gear[i] = 0
            locked[i] = False
            continue
        col = best_fuel[:, i]
        if shift_schedule == "sequential" and g_cur >= 1:
            mask = np.full(P.N_GEARS, np.inf)
            for g in (g_cur - 2, g_cur - 1, g_cur):
                if 0 <= g < P.N_GEARS:
                    mask[g] = col[g]
            col = mask
        if not np.isfinite(col).any():
            # nothing feasible: hold the lowest gear, converter slipping
            g_new = 0
        else:
            g_new = int(np.argmin(col))
        if g_cur >= 1 and g_new != g_cur - 1:
            can_shift = (t[i] - t_last_shift) >= P.SHIFT_MIN_DWELL_S
            cur_f = col[g_cur - 1]
            new_f = col[g_new]
            better = np.isfinite(new_f) and (
                not np.isfinite(cur_f)
                or new_f < cur_f * (1.0 - P.SHIFT_HYSTERESIS_FRAC))
            if not (can_shift and better):
                g_new = g_cur - 1
            else:
                t_last_shift = t[i]
                n_shifts += 1
        gear[i] = g_new + 1
        g_cur = g_new + 1
        locked[i] = bool(best_is_lock[g_new, i]) and np.isfinite(
            fuel_lock[g_new, i])

    idx = np.clip(gear - 1, 0, P.N_GEARS - 1)
    cols = np.arange(n)
    n_eng = np.where(locked, n_e_lock[idx, cols], n_e_un[idx, cols])
    t_eng = np.where(locked, t_e_lock[idx, cols], t_e_un[idx, cols])
    p_shaft = np.where(locked, p_shaft_lock[idx, cols], p_shaft_un[idx, cols])
    f_gps = np.where(locked, fuel_lock[idx, cols], fuel_un[idx, cols])
    # infeasible samples: the engine is on its full-load curve and the truck
    # falls short. Book the shortfall, do not silently clip fuel.
    # Samples with no feasible scheduled gear. The engine is put on its
    # full-load curve in the gear that delivers the most wheel power (a
    # kickdown), and the shortfall against demand is booked, not clipped.
    infeasible = ~np.isfinite(f_gps)
    stacked = np.maximum(p_w_av_lock, p_w_av_un)
    gbest = np.argmax(stacked, axis=0)
    lock_best = p_w_av_lock[gbest, cols] >= p_w_av_un[gbest, cols]
    n_cap = np.where(lock_best, n_e_lock[gbest, cols], n_e_wot[gbest, cols])
    t_cap = tmax(n_cap)
    p_cap = t_cap * n_cap * 2 * np.pi / 60.0 / 1e3
    f_cap = np.where(p_cap > 1e-9,
                     bsfc(n_cap, np.maximum(t_cap, 1e-9))
                     * np.clip(p_cap, 0.0, None) / 3600.0, 0.0)
    gear = np.where(infeasible & moving, gbest + 1, gear)
    locked = np.where(infeasible & moving, lock_best, locked)
    n_eng = np.where(infeasible, n_cap, n_eng)
    t_eng = np.where(infeasible, t_cap, t_eng)
    p_shaft = np.where(infeasible, p_cap, p_shaft)
    f_gps = np.where(infeasible, f_cap, f_gps)
    idx = np.clip(gear - 1, 0, P.N_GEARS - 1)

    # ---- braking / coasting: DFCO, and standing idle ---------------------
    # On a non-positive wheel demand the road drives the engine through the
    # locked path, so the engine speed is road-welded, not the speed the
    # driving solve returns. Hold the highest gear whose locked speed is
    # inside the schedule; below the lock-up speed the converter uncouples
    # and the engine falls to idle.
    braking = (p_wheel <= 0.0) & moving
    ok_b = lock_ok & (n_e_lock >= P.N_LUG_MIN_RPM) & (n_e_lock <= P.N_MAX_RPM)
    any_b = ok_b.any(axis=0)
    gb = (P.N_GEARS - 1) - np.argmax(ok_b[::-1, :], axis=0)
    gb = np.where(any_b, gb, 0)
    n_b = n_e_lock[gb, cols]
    coupled = braking & any_b
    gear = np.where(coupled, gb + 1, gear)
    locked = np.where(coupled, True, locked)
    n_eng = np.where(coupled, n_b, n_eng)
    dfco = coupled & (n_b >= P.N_DFCO_RPM)
    # engine driven by the road: no fuel, accessories carried by the wheels
    f_gps = np.where(dfco, 0.0, f_gps)
    p_shaft = np.where(dfco, 0.0, p_shaft)
    t_eng = np.where(dfco, 0.0, t_eng)
    # Coupled-but-fuelled would be the overrun case below the fuel-cut
    # threshold. It cannot occur: `coupled` requires a gear whose locked
    # engine speed is >= N_LUG_MIN_RPM (1,100 rpm) and the fuel-cut
    # threshold N_DFCO_RPM is 1,000 rpm, so coupled implies dfco by
    # construction. Round 1 carried an unreachable branch here
    # (adjudication r1/m13); it is replaced by the invariant it assumed.
    coupled_fuelled_s = float(np.sum(coupled & ~dfco) * dt)
    assert coupled_fuelled_s == 0.0, (
        "coupled-but-fuelled overrun occurred: N_LUG_MIN_RPM has fallen "
        "below N_DFCO_RPM and the ruler now needs an overrun fuelling "
        "branch")
    # uncoupled braking (below the lock-up speed): idle fuel with accessories
    brake_idle = braking & ~coupled
    n_idle = engine.idle_rpm
    w_idle = n_idle * 2 * np.pi / 60.0
    t_acc_idle = p_acc_kw * 1e3 / w_idle
    f_idle = float(bsfc(n_idle, t_acc_idle) * p_acc_kw / 3600.0)
    f_gps = np.where(brake_idle, f_idle, f_gps)
    p_shaft = np.where(brake_idle, p_acc_kw, p_shaft)
    n_eng = np.where(brake_idle, n_idle, n_eng)

    # standing: neutral idle (headline) or converter stalled in Drive
    stopped = ~moving
    if idle_neutral:
        f_stop = f_idle
        p_stop = p_acc_kw
        t_stop = t_acc_idle
    else:
        t_stall = float(tc_capacity(0.0) * w_idle ** 2)
        p_stop = float((t_stall + t_acc_idle) * w_idle / 1e3
                       + float(_pump(n_idle)))
        t_stop = p_stop * 1e3 / w_idle
        f_stop = float(bsfc(n_idle, t_stop) * p_stop / 3600.0)
    f_gps = np.where(stopped, f_stop, f_gps)
    p_shaft = np.where(stopped, p_stop, p_shaft)
    n_eng = np.where(stopped, n_idle, n_eng)
    t_eng = np.where(stopped, t_stop, t_eng)

    # ---- integrate --------------------------------------------------------
    fuel_burn_g = float(np.sum(f_gps) * dt)
    fuel_g = fuel_burn_g
    e_shaft_kwh = float(np.sum(np.clip(p_shaft, 0.0, None)) * dt / 3600.0)
    dist_km = float(vp.trapz(v, t)) / 1e3
    duration_s = float(t[-1] - t[0])

    # unserved wheel energy: demand the capability envelope cannot meet.
    # Charged to fuel at the ruler's own marginal geared rate so the energy
    # books balance - the same treatment WS4's simulator gives the
    # candidates' unserved bus energy - and also reported raw.
    short = np.clip(np.where(moving, p_drive - p_wheel_avail, 0.0), 0.0, None)
    unserved_wheel_kwh = float(np.sum(short) * dt / 3600.0)
    eta_marginal = float(max(eta_gear)) * eta_final \
        * (1.0 - slip)
    bsfc_marginal = (fuel_g / e_shaft_kwh if e_shaft_kwh > 0 else 0.0)
    unserved_fuel_g = unserved_wheel_kwh / eta_marginal * bsfc_marginal
    fuel_g = fuel_g + unserved_fuel_g

    # rotating-inertia bracket: the extra kinetic energy the ruler's engine,
    # flywheel and converter absorb on every launch, referred to the road
    # through the gear actually engaged, net of what is given back on
    # deceleration through DFCO (which recovers none of it as fuel).
    i_tot = np.where(gear >= 1, ratios[idx] * P.AXLE_RATIO, 0.0)
    m_eq = P.I_ENG_FLYWHEEL_CONV_KGM2 * (i_tot / veh.r_dyn) ** 2
    a = wp["a"]
    p_rot_extra = np.clip(m_eq * a * v, 0.0, None) / 1e3       # kW at wheel
    e_rot_extra_wheel_kwh = float(np.sum(p_rot_extra) * dt / 3600.0)

    fuel_energy_kwh = fuel_g * LHV_KJ_PER_G / 3600.0
    out = dict(
        vehicle="ruler_NPR-HD",
        fuel_g=fuel_g,
        fuel_l=fuel_g / P.DENSITY_G_PER_L,
        fuel_energy_kwh=fuel_energy_kwh,
        distance_km=dist_km,
        duration_s=duration_s,
        l_per_100km=fuel_g / P.DENSITY_G_PER_L / dist_km * 100.0,
        fuel_energy_kWh_per_km=fuel_energy_kwh / dist_km,
        eng_kwh=e_shaft_kwh,
        mean_bsfc_eff_g_per_kwh=(fuel_burn_g / e_shaft_kwh
                                 if e_shaft_kwh > 0 else float("inf")),
        fuel_burn_g=fuel_burn_g,
        unserved_wheel_kwh=unserved_wheel_kwh,
        unserved_fuel_g=unserved_fuel_g,
        infeasible_s=float(np.sum(infeasible & moving) * dt),
        n_shifts=int(n_shifts),
        idle_s=float(np.sum(stopped) * dt),
        idle_fuel_g=float(np.sum(np.where(stopped, f_gps, 0.0)) * dt),
        dfco_s=float(np.sum(dfco) * dt),
        locked_s=float(np.sum(locked) * dt),
        converter_s=float(np.sum(moving & ~locked) * dt),
        gear_time_frac=[float(np.sum(gear == g) * dt / duration_s)
                        for g in range(0, P.N_GEARS + 1)],
        e_rot_extra_wheel_kwh=e_rot_extra_wheel_kwh,
        e_brake_wheel_kwh=float(np.sum(np.clip(-p_wheel, 0.0, None))
                                * dt / 3600.0),
        e_trac_wheel_kwh=float(np.sum(p_drive) * dt / 3600.0),
        p_wheel_avail_min_moving_kW=float(
            np.min(p_wheel_avail[moving])) if moving.any() else 0.0,
        p_acc_crank_kw=p_acc_kw,
        idle_neutral=bool(idle_neutral),
        derate=float(derate),
        m_total_kg=float(m),
        idle_fuel_g_per_s=f_idle,
        idle_fuel_l_per_h=f_idle * 3600.0 / P.DENSITY_G_PER_L,
        idle_rpm=float(n_idle),
        idle_time_frac=float(np.sum(stopped) / n),
        brake_energy_frac_of_tractive=(
            float(np.sum(np.clip(-p_wheel, 0.0, None)))
            / float(np.sum(p_drive)) if float(np.sum(p_drive)) > 0 else 0.0),
        coupled_fuelled_s=coupled_fuelled_s,
        levers=dict(eta_gear=list(eta_gear_t), eta_final=eta_final,
                    pump_kw_at_1800=pump_k, lockup_slip=slip,
                    shift_schedule=shift_schedule,
                    derate_load_fraction=bool(derate_load_fraction)),
    )
    # heat rejected by the engine, for the WS6 ledger (R9).
    # m7: a cooling owner sizes against a WINDOW, not a cycle mean. The
    # instantaneous peak and the peak rolling-window means are exported on
    # the same basis WS4 exports them for the candidates, from the same
    # per-sample rejection rate that already feeds eng_reject_kwh.
    p_rej = np.clip(f_gps * LHV_KJ_PER_G - np.clip(p_shaft, 0.0, None),
                    0.0, None)                                    # kW
    # SWEEP (r2): this must be the heat of the fuel ACTUALLY BURNED minus
    # the shaft work actually done. Round 1 used `fuel_energy_kwh`, which
    # carries the unserved-wheel-energy fuel CORRECTION - fuel the engine
    # never burned, for work it never did - so the ruler's ledger row was
    # inflated by that correction while WS4's candidate-side
    # `eng_reject_kwh` is accumulated per sample from the real burn. The
    # two vehicles' rows were not on one basis. The correction is exported
    # separately so nothing is lost.
    out["eng_reject_kwh"] = float(np.sum(p_rej) * dt / 3600.0)
    out["eng_reject_kwh_incl_unserved_correction_r1_basis"] = (
        fuel_energy_kwh - e_shaft_kwh)
    out["eng_reject_unserved_correction_kwh"] = (
        (fuel_energy_kwh - e_shaft_kwh) - out["eng_reject_kwh"])
    out["eng_reject_peak_kw"] = float(np.max(p_rej)) if n else 0.0
    for _w in (120.0, 600.0):
        nn = max(1, int(round(_w / dt)))
        key = f"eng_reject_roll{int(_w)}s_max_kw"
        if nn >= p_rej.size:
            out[key] = min(float(np.mean(p_rej)), out["eng_reject_peak_kw"])
            continue
        xb = float(p_rej.mean())
        cs = np.concatenate(([0.0], np.cumsum(p_rej - xb)))
        out[key] = min(float(np.max(cs[nn:] - cs[:-nn]) / nn + xb),
                       out["eng_reject_peak_kw"])
    if trace:
        out["trace"] = dict(
            t_s=t, v_kmh=v * 3.6, grade_pct=cyc["grade"] * 100.0,
            P_wheel_kW=p_wheel, gear=gear.astype(float),
            lockup=locked.astype(float), N_eng_rpm=n_eng,
            T_eng_Nm=t_eng, P_shaft_eng_kW=p_shaft, fuel_g_per_s=f_gps)
    return out


# NOTE (adjudication r1 sweep): `ruler_available_wheel_kw` lived here and
# was never called by any module in this workstream - it duplicated
# `ws11_capability.ruler_force_table`, which is the capability model of
# record. It has been deleted rather than left as a second, unexercised
# statement of the same physics.
