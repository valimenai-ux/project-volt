"""
Project Volt - WS1
Road-load physics, wheel-power computation, cycle metrics, energy
management and The Four Numbers.
"""
import numpy as np
from volt_params import VEH, DL, AUX, ENG, CTL, G


# ---------------------------------------------------------------- road load
def road_load_force(v, grade, m, veh=VEH):
    """Resistive force at the tyre contact patch [N], excluding inertia.
    `grade` is tan(theta) (rise/run)."""
    v = np.asarray(v, dtype=float)
    grade = np.asarray(grade, dtype=float) * np.ones_like(v)
    theta = np.arctan(grade)
    f_aero = 0.5 * veh.rho_air * veh.CdA * v ** 2
    f_roll = veh.Crr * m * G * np.cos(theta) * (v > 0.05)
    f_grade = m * G * np.sin(theta)
    return f_aero + f_roll + f_grade, f_aero, f_roll, f_grade


def wheel_power(t, v, grade, m, lam=None, veh=VEH):
    """Instantaneous power the driveline must deliver to (or absorb from)
    the wheel hubs [W].

    P_wheel = [ lam*m*a  +  F_aero + F_roll + F_grade ] * v

    The lam*m*a term includes rotating inertia (wheels, hubs, rotor), i.e.
    this is *driveline* power at the wheel, not pure road-load power. That
    is the quantity a traction motor has to source, so it is the right
    basis for sizing.
    """
    lam = veh.lam_rot if lam is None else lam
    t = np.asarray(t, float); v = np.asarray(v, float)
    a = np.gradient(v, t)
    f_res, f_aero, f_roll, f_grade = road_load_force(v, grade, m, veh)
    f_inertia = lam * m * a
    f_total = f_inertia + f_res
    p = f_total * v
    return dict(a=a, F_inertia=f_inertia, F_aero=f_aero, F_roll=f_roll,
                F_grade=f_grade, F_total=f_total, P_wheel=p)


# ------------------------------------------------------------------- regen
def regen_split(v, p_wheel, cap_wheel=None, ctl=CTL):
    """Split negative wheel power into captured (electrical path) and
    friction-brake components.

    Two limits are applied at the wheel:
      * absorb cap  (default 75 kW, per assignment)
      * low-speed blend-out (regen tapers to zero as the vehicle stops,
        because motor back-EMF and controllability collapse and the
        service brakes must take over)
    """
    cap = ctl.regen_cap_wheel if cap_wheel is None else cap_wheel
    v = np.asarray(v, float); p_wheel = np.asarray(p_wheel, float)
    p_brake_demand = np.where(p_wheel < 0, -p_wheel, 0.0)   # >= 0
    blend = np.clip((v - ctl.v_regen_blend_lo) /
                    (ctl.v_regen_blend_hi - ctl.v_regen_blend_lo), 0.0, 1.0)
    p_capt = np.minimum(p_brake_demand, cap) * blend
    p_fric = p_brake_demand - p_capt
    return p_brake_demand, p_capt, p_fric


# ----------------------------------------------------------------- metrics
def trapz(y, t):
    return float(np.trapezoid(np.asarray(y, float), np.asarray(t, float)))


def cycle_metrics(t, v, grade, p_wheel, cap_wheel=None, dl=DL):
    """Task-2 metric block for one cycle."""
    T = float(t[-1] - t[0])
    dist = trapz(v, t)
    p_pos = np.clip(p_wheel, 0, None)
    p_neg = np.clip(p_wheel, None, 0)

    e_trac = trapz(p_pos, t)          # J, positive wheel energy
    e_brake = -trapz(p_neg, t)        # J, total braking energy at the wheel
    e_net = trapz(p_wheel, t)

    _, p_capt, p_fric = regen_split(v, p_wheel, cap_wheel)
    e_capt_mech = trapz(p_capt, t)
    e_capt_elec = e_capt_mech * dl.eta_wheel_to_bus

    moving = v > 0.1
    p_drive_only = p_pos[moving]

    out = {
        "duration_s": T,
        "distance_km": dist / 1000.0,
        "avg_speed_kmh": dist / T * 3.6,
        "avg_moving_speed_kmh": (dist / trapz(moving.astype(float), t) * 3.6
                                 if trapz(moving.astype(float), t) > 0 else 0.0),
        "stopped_fraction": 1.0 - trapz(moving.astype(float), t) / T,
        "max_speed_kmh": float(np.max(v)) * 3.6,
        "n_stops": count_stops(v),
        "stops_per_km": count_stops(v) / (dist / 1000.0),
        "P_peak_kW": float(np.max(p_wheel)) / 1e3,
        "P_avg_tractive_kW": e_trac / T / 1e3,
        "P_avg_net_kW": e_net / T / 1e3,
        "P_avg_abs_kW": trapz(np.abs(p_wheel), t) / T / 1e3,
        "P95_kW": float(np.percentile(p_pos, 95)) / 1e3,
        "P95_moving_kW": (float(np.percentile(p_drive_only, 95)) / 1e3
                          if p_drive_only.size else 0.0),
        "P99_kW": float(np.percentile(p_pos, 99)) / 1e3,
        "E_tractive_kWh": e_trac / 3.6e6,
        "E_braking_kWh": e_brake / 3.6e6,
        "E_net_kWh": e_net / 3.6e6,
        "E_per_km_kWh": e_trac / 3.6e6 / (dist / 1000.0),
        "E_net_per_km_kWh": e_net / 3.6e6 / (dist / 1000.0),
        "E_brake_per_km_kWh": e_brake / 3.6e6 / (dist / 1000.0),
        "brake_energy_frac_of_tractive": e_brake / e_trac if e_trac else 0.0,
        "E_regen_captured_mech_kWh": e_capt_mech / 3.6e6,
        "E_regen_captured_elec_kWh": e_capt_elec / 3.6e6,
        "regen_recoverable_frac_mech": e_capt_mech / e_brake if e_brake else 0.0,
        "regen_recoverable_frac_elec": e_capt_elec / e_brake if e_brake else 0.0,
        "P_regen_peak_wheel_kW": float(np.max(-p_neg)) / 1e3,
        "P_regen_peak_bus_kW": float(np.max(-p_neg)) * dl.eta_wheel_to_bus / 1e3,
        "P_rms_wheel_kW": float(np.sqrt(np.mean(p_wheel ** 2))) / 1e3,
    }
    return out


def count_stops(v, thresh=0.15):
    """Number of transitions moving -> stopped."""
    moving = np.asarray(v) > thresh
    return int(np.sum((~moving[1:]) & (moving[:-1])))


def power_histogram(t, p_wheel, bin_w=10e3, lo=-300e3, hi=350e3):
    """Time-at-power histogram, seconds per bin.

    Raises if any sample falls outside [lo, hi] rather than silently
    folding it into an edge bin whose label would then be wrong.
    """
    p_wheel = np.asarray(p_wheel, float)
    if p_wheel.min() < lo or p_wheel.max() > hi:
        raise ValueError(
            f"power_histogram range [{lo/1e3:.0f}, {hi/1e3:.0f}] kW does not "
            f"cover the data [{p_wheel.min()/1e3:.1f}, {p_wheel.max()/1e3:.1f}] kW")
    edges = np.arange(lo, hi + bin_w, bin_w)
    dt = np.gradient(np.asarray(t, float))
    idx = np.clip(np.digitize(p_wheel, edges) - 1, 0, len(edges) - 2)
    secs = np.zeros(len(edges) - 1)
    np.add.at(secs, idx, dt)
    return edges, secs


# ------------------------------------------------ thermal-equivalent RMS
def rms_power(p, t):
    """Full-cycle RMS of a power trace (stopped time included -> it
    correctly dilutes the thermal duty)."""
    dt = np.gradient(np.asarray(t, float))
    T = float(np.sum(dt))
    return float(np.sqrt(np.sum(np.asarray(p, float) ** 2 * dt) / T))


def rolling_rms_max(p, t, window_s):
    """Worst rolling-window RMS. Matters when the machine's thermal time
    constant is shorter than the cycle."""
    p = np.asarray(p, float); t = np.asarray(t, float)
    dt = float(np.median(np.diff(t)))
    n = max(1, int(round(window_s / dt)))
    if n >= p.size:
        return rms_power(p, t)
    c = np.concatenate(([0.0], np.cumsum(p ** 2))) * dt
    ms = (c[n:] - c[:-n]) / (n * dt)
    return float(np.sqrt(np.max(ms)))


def motor_shaft_power(p_wheel_motor, dl=DL):
    """Wheel power carried by the e-machine -> power at the motor shaft.
    Motoring: divide by reduction eff.  Generating: multiply."""
    p = np.asarray(p_wheel_motor, float)
    return np.where(p >= 0, p / dl.eta_red, p * dl.eta_red)


# ------------------------------------------------------- bus-level balance
def bus_demand(v, p_wheel, p_wheel_direct=None, cap_wheel=None,
               p_aux=None, dl=DL):
    """Net DC-bus power demand [W] (positive = bus must supply).

    p_wheel_direct : wheel power supplied mechanically by the engine through
                     the lockup clutch (V2 only). It bypasses the bus.
    """
    p_aux = AUX.p_aux_nom if p_aux is None else p_aux
    p_wheel = np.asarray(p_wheel, float)
    p_dir = np.zeros_like(p_wheel) if p_wheel_direct is None \
        else np.asarray(p_wheel_direct, float)
    p_motor_wheel = p_wheel - p_dir            # e-machine's share at the wheel
    p_pos = np.clip(p_motor_wheel, 0, None)
    p_neg_mag = np.clip(-p_motor_wheel, 0, None)
    blend = np.clip((v - CTL.v_regen_blend_lo) /
                    (CTL.v_regen_blend_hi - CTL.v_regen_blend_lo), 0.0, 1.0)
    cap = CTL.regen_cap_wheel if cap_wheel is None else cap_wheel
    p_capt = np.minimum(p_neg_mag, cap) * blend
    p_bus = p_pos / dl.eta_bus_to_wheel - p_capt * dl.eta_wheel_to_bus + p_aux
    return p_bus, p_motor_wheel, p_capt


def battery_trace(t, p_bus, p_gen_const, dl=DL):
    """Battery stored-energy trajectory [J] for a constant genset output.
    Positive de/dt = charging."""
    t = np.asarray(t, float)
    net = p_gen_const - np.asarray(p_bus, float)     # + = surplus to battery
    p_batt = np.where(net >= 0, net * dl.eta_batt_chg, net / dl.eta_batt_dis)
    dt = np.gradient(t)
    e = np.concatenate(([0.0], np.cumsum(0.5 * (p_batt[1:] + p_batt[:-1])
                                         * np.diff(t))))
    return e, p_batt


def solve_genset_constant(t, p_bus, lo=0.0, hi=1000e3, tol=1.0, dl=DL):
    """Constant genset output that leaves the battery SOC-neutral over the
    cycle (round-trip losses included).

    Raises if the root is not inside the bracket, rather than silently
    returning a clamped endpoint.
    """
    e_lo, _ = battery_trace(t, p_bus, lo, dl)
    e_hi, _ = battery_trace(t, p_bus, hi, dl)
    if e_lo[-1] > 0 or e_hi[-1] < 0:
        raise ValueError(
            f"SOC-neutral genset output is outside the bracket "
            f"[{lo/1e3:.0f}, {hi/1e3:.0f}] kW: residuals "
            f"{e_lo[-1]/3.6e6:+.3f} / {e_hi[-1]/3.6e6:+.3f} kWh")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        e, _ = battery_trace(t, p_bus, mid, dl)
        if e[-1] > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def net_window_swing(t, e, window_s):
    """Alternative reading of "energy swing over a rolling window":
    max |e(t+W) - e(t)|, i.e. the NET drift across the window rather than
    the peak-to-peak excursion inside it. Always <= max_window_swing."""
    t = np.asarray(t, float); e = np.asarray(e, float)
    dt = float(np.median(np.diff(t)))
    # n-1 sample offset spans the same (n-1)*dt seconds that
    # max_window_swing's n-sample window covers, so the documented
    # "always <= max_window_swing" invariant actually holds.
    n = max(2, int(round(window_s / dt))) - 1
    if n >= e.size:
        return float(np.max(e) - np.min(e))
    return float(np.max(np.abs(e[n:] - e[:-n])))


def max_window_swing(t, e, window_s):
    """Max peak-to-peak of e(t) inside any rolling window of `window_s`."""
    t = np.asarray(t, float); e = np.asarray(e, float)
    dt = float(np.median(np.diff(t)))
    n = max(2, int(round(window_s / dt)))
    if n >= e.size:
        return float(np.max(e) - np.min(e)), 0.0
    # rolling max/min via strided sliding window
    from numpy.lib.stride_tricks import sliding_window_view
    w = sliding_window_view(e, n)
    swing = w.max(axis=1) - w.min(axis=1)
    i = int(np.argmax(swing))
    return float(swing[i]), float(t[i])


# -------------------------------------------------------------- V2 engine
def engine_max_torque(rpm, eng=ENG):
    return np.interp(rpm, eng.rpm_pts, eng.trq_pts,
                     left=0.0, right=eng.trq_pts[-1])


def engine_rpm_from_speed(v, veh=VEH):
    """V2 lockup: engine rpm at road speed v [m/s]."""
    return v / veh.r_dyn * veh.fd_ratio * 60.0 / (2 * np.pi)


def direct_path_wheel_power_max(v, veh=VEH, dl=DL, eng=ENG):
    """Max wheel power available through the locked 2.8:1 path [W]."""
    rpm = engine_rpm_from_speed(v, veh)
    trq = np.where(rpm < eng.idle_rpm, 0.0, engine_max_torque(rpm, eng))
    p_shaft = trq * rpm * 2 * np.pi / 60.0
    return p_shaft * dl.eta_direct, p_shaft, rpm
