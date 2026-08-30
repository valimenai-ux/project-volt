"""
Project Volt - WS1
Variant-level powertrain models (V1 Postal series, V2 Trucker i-MMD),
energy management, and capability-limited forward simulation.
"""
import numpy as np
from volt_params import VEH, DL, AUX, ENG, CTL, G
import volt_physics as vp


def lpf(x, t, tau):
    """Causal first-order low-pass, used for the engine power-command
    smoothing in V2 lockup."""
    x = np.asarray(x, float)
    dt = float(np.median(np.diff(t)))
    a = dt / (tau + dt)
    y = np.empty_like(x)
    acc = x[0]
    for i in range(x.size):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def lockup_mask(v, p_wheel, v_lock=None, hyst=3.0 / 3.6):
    """V2 clutch state. Locked above the handover speed with hysteresis.

    [WS1-ASSUMPTION] The clutch is OPENED whenever wheel power demand is
    negative, so that the full braking event is available to the traction
    motor (regen priority). See Escalations for the engine-drag variant.
    """
    v_lock = CTL.v_lockup if v_lock is None else v_lock
    v = np.asarray(v, float)
    locked = np.zeros(v.size, dtype=bool)
    st = False
    for i in range(v.size):
        if st and v[i] < v_lock - hyst:
            st = False
        elif (not st) and v[i] > v_lock + hyst:
            st = True
        locked[i] = st and (p_wheel[i] > 0.0)
    return locked


def v2_direct_share(t, v, p_wheel, tau=20.0, p_gen_reserve_bus=0.0,
                    veh=VEH, dl=DL):
    """Wheel power supplied mechanically through the locked 2.8:1 path.

    Strategy [WS1-ASSUMPTION]: while locked, the engine delivers a 20 s
    low-pass-filtered version of the positive wheel-power demand, clipped
    to what the engine can produce at the road-imposed crank speed MINUS
    the shaft power the generator needs for `p_gen_reserve_bus` watts at
    the DC bus. The traction motor supplies the balance (either sign).
    """
    p_pos = np.clip(p_wheel, 0, None)
    p_cmd = lpf(p_pos, t, tau)
    p_dir_max, _, rpm = vp.direct_path_wheel_power_max(v, veh, dl)
    # The generator hangs off the same crankshaft, so shaft power routed to
    # the bus is not available to the wheels. Reserve it before clipping.
    p_dir_avail = np.maximum(
        0.0, p_dir_max - p_gen_reserve_bus / dl.eta_gen * dl.eta_direct)
    locked = lockup_mask(v, p_wheel)
    p_dir = np.where(locked, np.minimum(p_cmd, p_dir_avail), 0.0)
    p_dir = np.minimum(p_dir, np.clip(p_wheel, 0, None))   # never overdrive
    return p_dir, locked, rpm, p_dir_max


def energy_management(t, v, p_wheel, p_wheel_direct=None, p_aux=None,
                      cap_wheel=None, dl=DL):
    """Solve the constant genset output that is SOC-neutral over the cycle
    and return the full bus/battery picture."""
    p_bus, p_motor_wheel, p_capt = vp.bus_demand(
        v, p_wheel, p_wheel_direct, cap_wheel, p_aux, dl)
    p_gen = vp.solve_genset_constant(t, p_bus, dl=dl)
    e_batt, p_batt = vp.battery_trace(t, p_bus, p_gen, dl)
    return dict(p_bus=p_bus, p_motor_wheel=p_motor_wheel, p_capt=p_capt,
                p_gen_const=p_gen, e_batt=e_batt, p_batt=p_batt)


def four_numbers(t, v, p_wheel, p_wheel_direct=None, p_aux=None,
                 cap_wheel=None, windows=(60, 120, 300, 600, 1200),
                 dl=DL):
    """The Four Numbers for one variant on one cycle."""
    em = energy_management(t, v, p_wheel, p_wheel_direct, p_aux,
                           cap_wheel, dl)
    # The e-machine only ever absorbs the CAPPED and BLENDED share of a
    # braking event; the friction brakes take the rest. Charging the motor
    # with the full uncapped braking demand inflates its thermal duty and
    # its generating envelope, so N1 and the envelope use the capped trace.
    # The uncapped figure is kept alongside for comparison.
    p_mot_wheel_raw = em["p_motor_wheel"]
    p_mot_wheel = np.where(p_mot_wheel_raw >= 0.0, p_mot_wheel_raw,
                           -em["p_capt"])
    p_mot_shaft = vp.motor_shaft_power(p_mot_wheel, dl)
    p_mot_shaft_uncapped = vp.motor_shaft_power(p_mot_wheel_raw, dl)

    swings = {}
    for w in windows:
        s, tw = vp.max_window_swing(t, em["e_batt"], w)
        swings[f"{w}s"] = dict(kWh=s / 3.6e6, at_t_s=tw,
                               net_drift_kWh=vp.net_window_swing(
                                   t, em["e_batt"], w) / 3.6e6)
    full_swing = float(np.max(em["e_batt"]) - np.min(em["e_batt"]))

    rms_windows = tuple(sorted(set(windows) | {30, 60, 300, 600}))
    rms_win = {f"{w}s": vp.rolling_rms_max(p_mot_shaft, t, w) / 1e3
               for w in rms_windows}

    # RMS *torque* is the better copper-loss proxy: copper loss goes as T^2,
    # and with a fixed ratio the motor speed range differs by 2x between the
    # two cycles, so RMS power weights the same heating by omega^2.
    f_mot = np.where(p_mot_wheel >= 0.0,
                     p_mot_wheel / np.maximum(np.asarray(v, float), 1e-3) / dl.eta_red,
                     p_mot_wheel / np.maximum(np.asarray(v, float), 1e-3) * dl.eta_red)
    f_mot = np.where(np.asarray(v, float) > 0.05, f_mot, 0.0)
    trq = f_mot * VEH.r_dyn / VEH.motor_ratio          # Nm at the motor shaft
    t_rms = float(np.sqrt(np.mean(trq ** 2)))
    t_rms_win = {f"{w}s": float(vp.rolling_rms_max(trq, t, w))
                 for w in rms_windows}

    p_neg = np.clip(p_wheel, None, 0)
    return {
        "N1_motor_rms_wheel_kW": vp.rms_power(p_mot_wheel, t) / 1e3,
        "N1_motor_rms_shaft_kW": vp.rms_power(p_mot_shaft, t) / 1e3,
        "N1_motor_rms_shaft_uncapped_kW":
            vp.rms_power(p_mot_shaft_uncapped, t) / 1e3,
        "N1_rolling_rms_shaft_kW": rms_win,
        "N1_motor_rms_torque_Nm": t_rms,
        "N1_rolling_rms_torque_Nm": t_rms_win,
        "N1_torque_equiv_cont_kW_at_corner_speed":
            t_rms * (20.0 / 3.6 / VEH.r_dyn * VEH.motor_ratio) / 1e3,
        "N2_genset_const_bus_kW": em["p_gen_const"] / 1e3,
        "N2_genset_engine_shaft_kW": em["p_gen_const"] / dl.eta_gen / 1e3,
        "N2_engine_direct_avg_shaft_kW": (
            0.0 if p_wheel_direct is None else
            float(np.mean(np.asarray(p_wheel_direct))) / dl.eta_direct / 1e3),
        "N3_buffer_5min_kWh": (swings["300s"]["kWh"] if "300s" in swings
                               else vp.max_window_swing(
                                   t, em["e_batt"], 300.0)[0] / 3.6e6),
        "N3_buffer_by_window": swings,
        "N3_buffer_fullcycle_kWh": full_swing / 3.6e6,
        "N4_peak_regen_wheel_kW": float(np.max(-p_neg)) / 1e3,
        "N4_peak_regen_bus_kW": float(np.max(em["p_capt"])) * dl.eta_wheel_to_bus / 1e3,
        "N4_peak_regen_motor_shaft_kW": float(np.max(-np.clip(p_mot_shaft, None, 0))) / 1e3,
        "N4_peak_regen_motor_shaft_uncapped_kW":
            float(np.max(-np.clip(p_mot_shaft_uncapped, None, 0))) / 1e3,
        "motor_peak_motoring_shaft_kW": float(np.max(p_mot_shaft)) / 1e3,
        "bus_peak_kW": float(np.max(em["p_bus"])) / 1e3,
        "bus_min_kW": float(np.min(em["p_bus"])) / 1e3,
        "batt_peak_dis_kW": float(np.max(-np.clip(em["p_batt"], None, 0))) / 1e3,
        "batt_peak_chg_kW": float(np.max(np.clip(em["p_batt"], 0, None))) / 1e3,
        "_em": em,
    }


# --------------------------------------------- capability-limited forward sim
def simulate_achievable(t, v_demand, grade, m, mode="V2",
                        p_gen_bus=None, p_batt_pk=120e3, p_motor_pk=150e3,
                        p_aux=None, batt_kwh=None, batt_start_frac=0.55,
                        soc_target=0.55, tau_soc=240.0,
                        cap_wheel=None, veh=VEH, dl=DL, eng=ENG):
    """Forward-integrate the speed the vehicle can actually hold while
    chasing a demand trace, subject to powertrain limits.

    mode      : "V1" (series only) or "V2" (series + 2.8:1 lockup)
    batt_kwh  : usable buffer energy. None = energy-unlimited battery
                (pure peak-power check). A number = a finite buffer that
                starts at `batt_start_frac` of usable and can be driven
                flat, after which the genset/engine is on its own.
    The genset supervisor is load-following with proportional SOC
    regulation back to `soc_target` on a `tau_soc` time constant - i.e. it
    deliberately holds the buffer part-full so there is always headroom to
    accept regen. [WS1-ASSUMPTION]
    Returns the achieved speed plus the full energy-management picture.
    """
    p_gen_bus = (CTL.genset_v2_floor if mode == "V2" else CTL.genset_v1_class) \
        * dl.eta_gen if p_gen_bus is None else p_gen_bus
    p_aux = AUX.p_aux_nom if p_aux is None else p_aux
    cap = CTL.regen_cap_wheel if cap_wheel is None else cap_wheel

    t = np.asarray(t, float); v_dem = np.asarray(v_demand, float)
    grade = np.asarray(grade, float) * np.ones_like(v_dem)
    dt = float(np.median(np.diff(t)))
    n = v_dem.size
    lam = veh.lam_rot

    v = np.zeros(n); locked = np.zeros(n, bool)
    p_wheel = np.zeros(n); p_dir = np.zeros(n); p_bus = np.zeros(n)
    p_gen_a = np.zeros(n); p_batt = np.zeros(n); e_hist = np.zeros(n)
    p_fric = np.zeros(n)
    e_cap = None if batt_kwh is None else batt_kwh * 3.6e6
    e = 0.0 if e_cap is None else e_cap * batt_start_frac
    e_hist[0] = e
    st = False

    for i in range(1, n):
        vi = v[i - 1]
        if mode == "V2":
            if st and vi < CTL.v_lockup - 3 / 3.6:
                st = False
            elif (not st) and vi > CTL.v_lockup + 3 / 3.6:
                st = True
        locked[i] = st

        p_dm = float(vp.direct_path_wheel_power_max(np.array([vi]), veh, dl)[0][0]) \
            if st else 0.0
        # battery availability is ENERGY-limited as well as power-limited:
        # a buffer with 6 J left cannot supply 120 kW for the next step.
        # energy-limited as well as power-limited, and referred to the BUS
        # (the discharge clamp later applies the same eta_batt_dis)
        batt_avail = (p_batt_pk if e_cap is None
                      else min(p_batt_pk,
                               max(0.0, e) * dl.eta_batt_dis / max(dt, 1e-9)))

        if st:
            # engine drives the wheels; it must also carry the accessories
            # through the generator, so discount that from the direct path
            p_dm_net = max(0.0, p_dm - p_aux / dl.eta_gen * dl.eta_direct)
            p_avail = p_dm_net + min(p_motor_pk, batt_avail * dl.eta_bus_to_wheel)
            f_cap = veh.F_trac_max + 700.0 * veh.fd_ratio * dl.eta_direct / veh.r_dyn
        else:
            p_elec = max(0.0, p_gen_bus - p_aux) + batt_avail
            p_avail = min(p_motor_pk, p_elec * dl.eta_bus_to_wheel)
            f_cap = veh.F_trac_max

        f_res = float(vp.road_load_force(np.array([vi]), np.array([grade[i]]),
                                         m, veh)[0][0])
        f_avail = min(f_cap, p_avail / max(vi, 0.5))
        a_cap = (f_avail - f_res) / (lam * m)
        a_dem = (v_dem[i] - vi) / dt
        a = max(min(a_dem, a_cap), -2.5)
        vn = max(0.0, vi + a * dt)
        v[i] = vn
        a_act = (vn - vi) / dt

        # --- actual power flows at the achieved operating point
        vm = 0.5 * (vi + vn)
        f_res_m = float(vp.road_load_force(np.array([vm]), np.array([grade[i]]),
                                           m, veh)[0][0])
        pw = (lam * m * a_act + f_res_m) * vm
        p_wheel[i] = pw
        pdir = min(max(pw, 0.0), p_dm) if st else 0.0
        p_dir[i] = pdir
        p_mot_wheel = pw - pdir
        if p_mot_wheel >= 0:
            pb = p_mot_wheel / dl.eta_bus_to_wheel + p_aux
            p_fric[i] = 0.0
        else:
            blend = min(max((vm - CTL.v_regen_blend_lo) /
                            (CTL.v_regen_blend_hi - CTL.v_regen_blend_lo), 0.0), 1.0)
            head = 1e18 if e_cap is None else max(0.0, (e_cap - e)) / max(dt, 1e-6)
            p_capt_w = min(-p_mot_wheel, cap) * blend
            p_capt_w = min(p_capt_w, head / dl.eta_wheel_to_bus / dl.eta_batt_chg)
            p_fric[i] = -p_mot_wheel - p_capt_w
            pb = -p_capt_w * dl.eta_wheel_to_bus + p_aux
        p_bus[i] = pb
        # genset supervisor: follow the bus load, and trim SOC back to the
        # target so that regen headroom is preserved
        pg_cap = p_gen_bus
        if st:
            # the generator shares the crankshaft with the direct path
            spare_shaft = max(0.0, (p_dm - pdir) / dl.eta_direct)
            pg_cap = min(p_gen_bus, spare_shaft * dl.eta_gen)
        if e_cap is None:
            pg = max(0.0, min(pg_cap, pb))
        else:
            soc_err = (e_cap * soc_target - e) / tau_soc     # W
            pg = float(np.clip(pb + soc_err, 0.0, pg_cap))
        p_gen_a[i] = pg
        net = pg - pb
        pbat = net * dl.eta_batt_chg if net >= 0 else net / dl.eta_batt_dis
        if e_cap is not None:
            if pbat < 0.0:
                pbat = max(pbat, -e / max(dt, 1e-9))   # cannot over-draw
            e = min(e_cap, max(0.0, e + pbat * dt))
        p_batt[i] = pbat
        e_hist[i] = e

    return dict(v=v, locked=locked, p_wheel=p_wheel, p_direct=p_dir,
                p_bus=p_bus, p_gen=p_gen_a, p_batt=p_batt,
                # e_batt is only meaningful when batt_kwh was given
                e_batt=(e_hist if e_cap is not None else None),
                p_friction=p_fric)
