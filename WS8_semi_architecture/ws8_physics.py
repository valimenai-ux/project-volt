"""
Project Volt - WS8
Road load and the achieved-speed integrator.

Method mirrors WS1's (volt_physics.py road_load_force / wheel_power) at
semi scale, with ONE deliberate change that the semi-scale problem forces:

  WS1 built a flat-road speed trace and applied grade afterwards. At
  6,600 kg that is defensible. At 36,300 kg it is NOT: a loaded
  combination on a 6% grade cannot hold 85 km/h with any powertrain in
  this trial, so a demand trace applied post hoc would silently hand
  every candidate a speed it cannot achieve and would hide exactly the
  quantity Task 5 asks for (the fixed-ratio grade-hold floor).

  WS8 therefore integrates the ACHIEVED speed forward against each
  candidate's own tractive envelope and the grade at the current
  distance. Candidates that cannot hold the demanded speed fall back to
  the speed they can hold, take longer, and are charged the extra time
  in aux energy. The demand trace is common to all candidates; the
  achieved trace is not.
"""
import math

import numpy as np

from ws8_params import VEH, G


# ---------------------------------------------------------------- road load
def road_load_force(v, grade, m, cda=None, crr=None, rho=None, v_wind=0.0):
    """Resistive force at the tyre contact patch [N], excluding inertia.
    `grade` is tan(theta) (rise/run). Signature and decomposition follow
    WS1's road_load_force so the two are directly comparable.

    `v_wind` is the head-on air-speed component [m/s]: the aerodynamic
    term sees (v + v_wind) while the power it costs is still F*v. A
    tailwind is a negative v_wind and the term is signed, so a strong
    tailwind at low road speed correctly produces a small NEGATIVE aero
    force rather than a spurious positive one."""
    v = np.asarray(v, dtype=float)
    grade = np.asarray(grade, dtype=float) * np.ones_like(v)
    cda = VEH.CdA if cda is None else cda
    crr = VEH.Crr if crr is None else crr
    rho = VEH.rho_air if rho is None else rho
    theta = np.arctan(grade)
    v_air = v + v_wind
    f_aero = 0.5 * rho * cda * v_air * np.abs(v_air)
    f_roll = crr * m * G * np.cos(theta) * (v > 0.05)
    f_grade = m * G * np.sin(theta)
    return f_aero + f_roll + f_grade, f_aero, f_roll, f_grade


def wheel_power_from_trace(t, v, grade, m, lam, cda=None, crr=None,
                           rho=None, v_wind=0.0):
    """Post-hoc wheel power for an ALREADY-ACHIEVED trace [W].

    P_wheel = [ lam*m*a + F_aero + F_roll + F_grade ] * v
    """
    t = np.asarray(t, float)
    v = np.asarray(v, float)
    a = np.gradient(v, t)
    f_res, f_aero, f_roll, f_grade = road_load_force(v, grade, m, cda, crr,
                                                     rho, v_wind)
    f_inertia = lam * m * a
    f_total = f_inertia + f_res
    return dict(a=a, F_inertia=f_inertia, F_aero=f_aero, F_roll=f_roll,
                F_grade=f_grade, F_total=f_total, P_wheel=f_total * v)


def steady_speed_on_grade(p_wheel_avail_kw, grade, m, cda=None, crr=None,
                          rho=None, v_hi=35.0, v_wind=0.0):
    """Highest speed [m/s] at which `p_wheel_avail_kw` at the contact patch
    balances road load on a constant grade. Bisection on a monotone
    function; returns 0.0 if the powertrain cannot move the vehicle at
    all (grade-hold floor = 0, i.e. it stalls)."""
    def excess(v):
        f, _, _, _ = road_load_force(np.array([v]), grade, m, cda, crr, rho,
                                     v_wind)
        return p_wheel_avail_kw * 1e3 - float(f[0]) * v

    if excess(0.05) <= 0.0:
        return 0.0
    lo, hi = 0.05, v_hi
    if excess(hi) > 0.0:
        return hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if excess(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def adhesion_limit_N(mu, m_drive_axle_kg):
    """Tractive force ceiling set by drive-axle adhesion [N].

    Static axle load only. Load transfer under acceleration adds to the
    drive axle on a tractor and subtracts on the steer axle; at the
    accelerations in this trial (<0.6 m/s^2 loaded) the transfer is
    ~3% of drive load, and IGNORING it is the conservative direction for
    a traction check, so it is ignored and said so."""
    return mu * m_drive_axle_kg * G


# ------------------------------------------------------- achieved-speed sim
class DriverParams:
    """Line-haul driver. Cruise-control-like speed hold, gentle service
    braking, lookahead to stops. Same structure as WS1's DriverParams so
    the two workstreams' driver models are recognisably the same object.
    """

    def __init__(self, a_max=0.55, a_brake=0.85, kp_hold=0.55,
                 noise_sigma=0.30, noise_tau=40.0, a_creep_taper=2.0,
                 v_downhill_over=1.06):
        self.a_max = a_max                  # m/s^2 comfortable launch
        self.a_brake = a_brake              # m/s^2 service brake target
        self.kp_hold = kp_hold              # 1/s speed-hold gain
        self.noise_sigma = noise_sigma      # m/s speed-hold noise
        self.noise_tau = noise_tau          # s correlation time
        self.a_creep_taper = a_creep_taper  # m/s, taper braking below this
        # A real driver lets the truck run slightly above set speed
        # downhill before the retarder catches it.
        self.v_downhill_over = v_downhill_over


V_TABLE_MAX = 36.0      # m/s, top of the envelope lookup grid (129.6 km/h)
V_TABLE_DV = 0.05       # m/s resolution


def build_env_tables(envelope, lam_fn, v_max=V_TABLE_MAX, dv=V_TABLE_DV):
    """Tabulate a candidate's envelope and inertia factor on a speed grid.

    The integrator runs 10 Hz over 500+ km, so a Python call per step per
    quantity dominates the run. Every candidate's envelope is a smooth
    function of road speed alone, so it is tabulated ONCE at 0.05 m/s
    (0.18 km/h) resolution and linearly interpolated in the loop. The
    tabulation error is bounded by the curvature of the envelope over
    0.05 m/s, which is far below the modelling uncertainty in the
    envelope itself; run_ws8.py's sanity block reports the maximum
    tabulation error against direct evaluation."""
    v_grid = np.arange(0.0, v_max + dv, dv)
    ft = np.empty_like(v_grid)
    fr = np.empty_like(v_grid)
    fx = np.empty_like(v_grid)
    lm = np.empty_like(v_grid)
    for i, vv in enumerate(v_grid):
        a, b, c = envelope(float(vv))
        ft[i], fr[i], fx[i] = a, b, c
        lm[i] = lam_fn(float(vv))
    return dict(v_grid=v_grid, dv=float(dv), F_trac=ft, F_regen=fr,
                F_retard=fx, lam=lm)


def integrate_achieved(cycle, envelope, m, lam_fn, dp, seed,
                       cda=None, crr=None, rho=None, v_abs_max=None,
                       v_wind=None, v_cap_fn=None, env_tables=None):
    """Forward-integrate the achieved speed for ONE candidate.

    Parameters
    ----------
    cycle : dict with 's_grid' (m), 'grade_of_s' (callable or array on
        s_grid), 'v_tgt_of_s' (array on s_grid, m/s), 'stops' (list of
        (s_position_m, dwell_s)), 'dt', 'name'.
    envelope : callable(v) -> (F_trac_max_N, F_brake_regen_max_N,
        F_brake_retard_max_N). The candidate's tractive and retarding
        force at the contact patch at speed v. This is where the
        architectures actually differ.
    m : combination mass [kg] (GCW - it is fixed across candidates).
    lam_fn : callable(v) -> effective mass factor (an ICE in a low gear
        carries far more rotating inertia than one in direct top).
    dp : DriverParams
    seed : int, for the speed-hold noise (deterministic)

    Returns dict of arrays at 10 Hz: t, v, s, grade, a, and the force
    decomposition, plus per-sample flags.
    """
    dt = cycle["dt"]
    s_grid = cycle["s_grid"]
    grade_grid = cycle["grade_grid"]
    v_tgt_grid = cycle["v_tgt_grid"]
    stops = cycle["stops"]
    s_end = float(s_grid[-1])

    # The distance grid is UNIFORM by construction (ws8_cycles builds it
    # with np.arange), so the inner loop indexes it directly instead of
    # calling np.interp 2N times. Asserted, not assumed.
    ds_grid = float(s_grid[1] - s_grid[0])
    if not np.allclose(np.diff(s_grid), ds_grid, rtol=0, atol=1e-9):
        raise ValueError("integrate_achieved requires a uniform s_grid")
    n_grid = s_grid.size

    # DESCENT SPEED GOVERNOR. On a long descent a real driver does not
    # hold the corridor speed on the service brakes - the brakes are for
    # stopping, the retarder is for holding, and a driver who confuses
    # the two arrives at the bottom with no brakes. So the demanded speed
    # is capped at the speed this candidate can hold with its own
    # retarding capability plus a declared continuous friction-brake
    # allowance. Candidates with more retarding power descend faster and
    # spend less trip time; candidates with less descend slower. That is
    # a real architectural consequence and it is priced here rather than
    # hidden in an unlimited friction brake.
    #
    # Evaluated once per grade node, not per timestep.
    if v_cap_fn is None:
        cap_grid = None
    else:
        cap_grid = np.array([float(v_cap_fn(float(g))) for g in grade_grid])

    cda_l = VEH.CdA if cda is None else cda
    crr_l = VEH.Crr if crr is None else crr
    rho_l = VEH.rho_air if rho is None else rho
    k_aero = 0.5 * rho_l * cda_l
    k_roll = crr_l * m * G
    vw = float(cycle.get("v_wind", 0.0)) if v_wind is None else float(v_wind)

    # envelope lookup tables (built here if the caller did not supply
    # them; supplying them lets one build serve many seeds)
    tb = build_env_tables(envelope, lam_fn) if env_tables is None \
        else env_tables
    tv_dv = tb["dv"]
    t_ft, t_fr, t_fx, t_lm = (tb["F_trac"], tb["F_regen"], tb["F_retard"],
                              tb["lam"])
    n_tab = t_ft.size

    rng = np.random.default_rng(seed)
    alpha = np.exp(-dt / dp.noise_tau)
    sig_step = dp.noise_sigma * np.sqrt(1 - alpha ** 2)
    noise = 0.0

    # stop bookkeeping: sorted positions, each consumed once
    stop_s = np.array([p for p, _ in stops], float)
    stop_dwell = np.array([d for _, d in stops], float)
    next_stop = 0

    v = 0.0
    s = 0.0
    T_MAX = int(round(cycle.get("t_max_s", 60000.0) / dt))

    out_v, out_s, out_g, out_a = [], [], [], []
    out_ft, out_fb_regen, out_fb_ret, out_fb_fric = [], [], [], []
    out_limited = []
    dwell_left = 0.0

    for _ in range(T_MAX):
        # uniform-grid lookup with linear interpolation
        x = s / ds_grid
        i0 = int(x)
        if i0 >= n_grid - 1:
            i0 = n_grid - 2
            fx = 1.0
        elif i0 < 0:
            i0, fx = 0, 0.0
        else:
            fx = x - i0
        grade = grade_grid[i0] + fx * (grade_grid[i0 + 1] - grade_grid[i0])

        out_g.append(grade)
        out_s.append(s)
        out_v.append(v)

        if dwell_left > 0.0:
            dwell_left -= dt
            out_a.append(0.0)
            out_ft.append(0.0); out_fb_regen.append(0.0)
            out_fb_ret.append(0.0); out_fb_fric.append(0.0)
            out_limited.append(0)
            continue

        v_tgt = v_tgt_grid[i0] + fx * (v_tgt_grid[i0 + 1] - v_tgt_grid[i0])
        if v_abs_max is not None and v_tgt > v_abs_max:
            v_tgt = v_abs_max
        if cap_grid is not None:
            cap = cap_grid[i0] + fx * (cap_grid[i0 + 1] - cap_grid[i0])
            if v_tgt > cap:
                v_tgt = cap

        noise = alpha * noise + sig_step * rng.standard_normal()
        v_cmd = v_tgt + (noise if v_tgt > 5.0 else 0.0)
        if v_cmd < 0.0:
            v_cmd = 0.0

        # envelope + inertia by table lookup
        xv = v / tv_dv
        j0 = int(xv)
        if j0 >= n_tab - 1:
            j0, fv = n_tab - 2, 1.0
        else:
            fv = xv - j0
        lam = t_lm[j0] + fv * (t_lm[j0 + 1] - t_lm[j0])
        f_trac_max = t_ft[j0] + fv * (t_ft[j0 + 1] - t_ft[j0])
        f_regen_max = t_fr[j0] + fv * (t_fr[j0 + 1] - t_fr[j0])
        f_retard_max = t_fx[j0] + fv * (t_fx[j0 + 1] - t_fx[j0])

        # scalar road load, same decomposition as road_load_force()
        theta = math.atan(grade)
        v_air = v + vw
        f_res = (k_aero * v_air * abs(v_air)
                 + (k_roll * math.cos(theta) if v > 0.05 else 0.0)
                 + m * G * math.sin(theta))

        # --- stop lookahead ------------------------------------------
        braking_for_stop = False
        if next_stop < stop_s.size:
            d_to_stop = stop_s[next_stop] - s
            if d_to_stop <= 0.0:
                v = 0.0
                dwell_left = float(stop_dwell[next_stop])
                next_stop += 1
                out_a.append(0.0)
                out_ft.append(0.0); out_fb_regen.append(0.0)
                out_fb_ret.append(0.0); out_fb_fric.append(0.0)
                out_limited.append(0)
                continue
            d_brake = v ** 2 / (2.0 * dp.a_brake)
            if d_to_stop <= d_brake:
                braking_for_stop = True

        if braking_for_stop:
            a_dem = -dp.a_brake * min(1.0, max(v, 0.0) / dp.a_creep_taper)
        elif v < v_cmd - 0.5:
            a_dem = min(dp.a_max, (v_cmd - v) / max(dt * 10.0, 0.5))
        else:
            a_dem = float(np.clip(dp.kp_hold * (v_cmd - v), -0.55, 0.35))
            # allow a small downhill overspeed before retarding
            if a_dem < 0 and v < v_cmd * dp.v_downhill_over:
                a_dem = 0.0

        f_dem = lam * m * a_dem + f_res

        limited = 0
        if f_dem >= 0.0:
            f_trac = min(f_dem, f_trac_max)
            if f_trac < f_dem - 1.0:
                limited = 1
            f_regen = f_ret = f_fric = 0.0
            f_net = f_trac - f_res
        else:
            f_trac = 0.0
            need = -f_dem                      # >= 0, retarding force wanted
            f_regen = min(need, f_regen_max)
            f_ret = min(need - f_regen, f_retard_max)
            f_fric = max(0.0, need - f_regen - f_ret)
            f_net = -(f_regen + f_ret + f_fric) - f_res

        a = f_net / (lam * m)
        v_new = max(0.0, v + a * dt)
        s += 0.5 * (v + v_new) * dt
        v = v_new

        out_a.append(a)
        out_ft.append(f_trac); out_fb_regen.append(f_regen)
        out_fb_ret.append(f_ret); out_fb_fric.append(f_fric)
        out_limited.append(limited)

        if s >= s_end:
            break

    n = len(out_v)
    t = np.arange(n) * dt
    return dict(
        name=cycle["name"], dt=dt, t=t,
        v=np.array(out_v), s=np.array(out_s), grade=np.array(out_g),
        a=np.array(out_a),
        F_trac=np.array(out_ft), F_regen=np.array(out_fb_regen),
        F_retard=np.array(out_fb_ret), F_friction=np.array(out_fb_fric),
        power_limited=np.array(out_limited, dtype=np.int8),
        distance_m=float(s), duration_s=float(t[-1] if n else 0.0))


def trace_metrics(res, m, cda=None, crr=None, rho=None):
    """Cycle metrics for an achieved trace. Mirrors WS1's cycle_metrics
    naming so the two workstreams' tables read the same way."""
    t, v = res["t"], res["v"]
    dist = res["distance_m"]
    T = res["duration_s"]
    p_wheel = (res["F_trac"] - res["F_regen"] - res["F_retard"]
               - res["F_friction"]) * v
    moving = v > 0.1
    tm = float(np.trapezoid(moving.astype(float), t))
    return {
        "duration_s": T,
        "distance_km": dist / 1000.0,
        "avg_speed_kmh": dist / T * 3.6 if T > 0 else 0.0,
        "avg_moving_speed_kmh": (dist / tm * 3.6) if tm > 0 else 0.0,
        "max_speed_kmh": float(np.max(v)) * 3.6,
        "min_moving_speed_kmh": (float(np.min(v[moving])) * 3.6
                                 if moving.any() else 0.0),
        "stopped_fraction": 1.0 - tm / T if T > 0 else 0.0,
        "power_limited_fraction": float(np.mean(res["power_limited"])),
        "E_tractive_kWh": float(np.trapezoid(
            np.clip(res["F_trac"] * v, 0, None), t)) / 3.6e6,
        "E_regen_wheel_kWh": float(np.trapezoid(res["F_regen"] * v, t))
        / 3.6e6,
        "E_retarder_wheel_kWh": float(np.trapezoid(res["F_retard"] * v, t))
        / 3.6e6,
        "E_friction_brake_kWh": float(np.trapezoid(res["F_friction"] * v, t))
        / 3.6e6,
        "P_peak_wheel_kW": float(np.max(res["F_trac"] * v)) / 1e3,
        "P_peak_brake_kW": float(np.max(
            (res["F_regen"] + res["F_retard"] + res["F_friction"]) * v)) / 1e3,
        "P_avg_wheel_kW": float(np.trapezoid(p_wheel, t)) / T / 1e3
        if T > 0 else 0.0,
    }
