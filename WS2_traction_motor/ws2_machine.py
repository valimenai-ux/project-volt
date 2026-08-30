"""IPM machine dq model: MTPA / field weakening, losses, capability, maps.

Amplitude-invariant dq frame. id <= 0 always (no flux boosting used).
Torque sign handled by iq sign; the machine is electromagnetically
symmetric so |generating| solutions mirror motoring solutions.

Approximations (declared in REPORT_WS2.md):
* Fixed (saturated-bulk) Ld, Lq, psi_m — no saturation map.
* Iron/windage loss treated as an electrical-side loss adder, not a load
  torque, except for the zero-torque lockup-spin case where the drag is
  explicitly charged to the shaft.
* Voltage limit includes the resistive drop; controller keeps a 5%
  modulation margin (BUS['v_margin_ctrl']).
"""

import math

from ws2_params import MACH, INV, BUS


def rs_at(T_c):
    return MACH["Rs_20C"] * (1.0 + MACH["alpha_cu"] * (T_c - 20.0))


def rac_factor(f_e):
    return 1.0 + MACH["k_ac"] * (f_e / MACH["f_ac_ref"]) ** 2


def mech_loss(omega_m):
    w = abs(omega_m)
    return MACH["fw_a"] * w + MACH["fw_b"] * w ** 3


def iron_loss(f_e, psi_s):
    f = abs(f_e)
    scale = (psi_s / MACH["psi_ref"]) ** 2
    return (MACH["k_h"] * f + MACH["k_e"] * f * f) * scale


def _v_req(id_, iq, omega_e, Rs):
    vd = Rs * id_ - omega_e * MACH["Lq"] * iq
    vq = Rs * iq + omega_e * (MACH["Ld"] * id_ + MACH["psi_m"])
    return math.hypot(vd, vq)


def torque_dq(id_, iq):
    return 1.5 * MACH["p"] * (MACH["psi_m"] * iq
                              + (MACH["Ld"] - MACH["Lq"]) * id_ * iq)


def mtpa_angle(I):
    """Current angle beta from q-axis (id=-I sin b, iq=I cos b), I>0."""
    dL = MACH["Lq"] - MACH["Ld"]
    if I <= 0.0:
        return 0.0
    s = (-MACH["psi_m"] + math.sqrt(MACH["psi_m"] ** 2 + 8.0 * dL ** 2 * I * I)
         ) / (4.0 * dL * I)
    s = min(max(s, 0.0), 0.999999)
    return math.asin(s)


def mtpa_torque(I):
    b = mtpa_angle(I)
    return torque_dq(-I * math.sin(b), I * math.cos(b))


def mtpa_current_for_torque(T_abs, I_max):
    """Bisect I so that MTPA torque == T_abs. Returns (id, iq_abs) or None."""
    if T_abs <= 0.0:
        return (0.0, 0.0)
    if mtpa_torque(I_max) < T_abs:
        return None
    lo, hi = 0.0, I_max
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if mtpa_torque(mid) < T_abs:
            lo = mid
        else:
            hi = mid
    b = mtpa_angle(hi)
    return (-hi * math.sin(b), hi * math.cos(b))


def _iq_on_torque_curve(T_abs, id_):
    den = 1.5 * MACH["p"] * (MACH["psi_m"] + (MACH["Ld"] - MACH["Lq"]) * id_)
    if den <= 1e-12:
        return None
    return T_abs / den


def solve_point(T_shaft, omega_m, v_dc, I_max=None, T_wind=None):
    """Find min-copper currents delivering |T_shaft| at omega_m under the
    voltage/current limits. Returns dict or None if infeasible.

    T_shaft signed; omega_m >= 0 (rad/s mech).
    """
    if I_max is None:
        I_max = MACH["I_peak"]
    if T_wind is None:
        T_wind = MACH["T_wind_ref"]
    Rs = rs_at(T_wind)
    omega_e = MACH["p"] * omega_m
    f_e = omega_e / (2.0 * math.pi)
    v_lim = BUS["v_margin_ctrl"] * v_dc / math.sqrt(3.0)
    T_abs = abs(T_shaft)

    sol = mtpa_current_for_torque(T_abs, I_max)
    if sol is None:
        return None
    id_m, iq_m = sol
    if _v_req(id_m, iq_m, omega_e, Rs) <= v_lim:
        id_, iq = id_m, iq_m
    else:
        # field weaken along the constant-torque curve: id in [id_lb, id_m]
        id_lb = -I_max
        # find bracket: v decreases as id goes negative until MTPV
        n = 120
        prev_id, prev_v = id_m, _v_req(id_m, iq_m, omega_e, Rs)
        found = None
        best_v = prev_v
        for k in range(1, n + 1):
            idk = id_m + (id_lb - id_m) * k / n
            iqk = _iq_on_torque_curve(T_abs, idk)
            if iqk is None or math.hypot(idk, iqk) > I_max:
                break
            vk = _v_req(idk, iqk, omega_e, Rs)
            if vk <= v_lim:
                found = (prev_id, idk)
                break
            if vk > best_v + 1e-9 and vk > prev_v:
                # past MTPV, voltage rising again: infeasible on this curve
                break
            prev_id, prev_v = idk, vk
            best_v = min(best_v, vk)
        if found is None:
            return None
        lo, hi = found  # v(lo) > v_lim >= v(hi)
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            iqm = _iq_on_torque_curve(T_abs, mid)
            if iqm is None or math.hypot(mid, iqm) > I_max:
                lo = mid
                continue
            if _v_req(mid, iqm, omega_e, Rs) > v_lim:
                lo = mid
            else:
                hi = mid
        id_ = hi
        iq = _iq_on_torque_curve(T_abs, id_)
        if iq is None or math.hypot(id_, iq) > I_max * 1.0001:
            return None

    if T_shaft < 0:
        iq = -iq

    I_amp = math.hypot(id_, iq)
    psi_s = math.hypot(MACH["Ld"] * id_ + MACH["psi_m"], MACH["Lq"] * iq)
    p_cu = 1.5 * Rs * rac_factor(f_e) * I_amp ** 2
    p_fe = iron_loss(f_e, psi_s)
    p_fw = mech_loss(omega_m)
    return dict(id=id_, iq=iq, I_amp=I_amp, psi_s=psi_s,
                p_cu=p_cu, p_fe=p_fe, p_fw=p_fw,
                f_e=f_e, v_req=_v_req(id_, iq, omega_e, Rs))


def max_torque(omega_m, v_dc, I_max=None):
    """Max |shaft torque| available at omega_m, v_dc, I_max (bisection)."""
    if I_max is None:
        I_max = MACH["I_peak"]
    T_hi = mtpa_torque(I_max)
    if solve_point(T_hi, omega_m, v_dc, I_max) is not None:
        return T_hi
    lo, hi = 0.0, T_hi
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        if solve_point(mid, omega_m, v_dc, I_max) is None:
            hi = mid
        else:
            lo = mid
    return lo


def spin_loss(omega_m, v_dc, T_wind=None):
    """Zero-torque spin (lockup): min over id of total drag+standby-side loss.

    Returns dict with the shaft drag power the locked engine must supply
    (p_fe + p_fw) plus the copper spent on flux weakening (drawn from bus).
    The optimiser trades copper (bus) against iron (shaft) to minimise
    TOTAL loss; both components are reported separately.
    """
    if T_wind is None:
        T_wind = MACH["T_wind_ref"]
    Rs = rs_at(T_wind)
    omega_e = MACH["p"] * omega_m
    f_e = omega_e / (2.0 * math.pi)
    v_lim = BUS["v_margin_ctrl"] * v_dc / math.sqrt(3.0)
    best = None
    n = 400
    for k in range(n + 1):
        id_ = -MACH["I_peak"] * k / n
        if _v_req(id_, 0.0, omega_e, Rs) > v_lim:
            continue
        psi_s = abs(MACH["Ld"] * id_ + MACH["psi_m"])
        p_cu = 1.5 * Rs * rac_factor(f_e) * id_ * id_
        p_fe = iron_loss(f_e, psi_s)
        tot = p_cu + p_fe
        if best is None or tot < best["p_cu"] + best["p_fe"]:
            best = dict(id=id_, p_cu=p_cu, p_fe=p_fe)
    p_fw = mech_loss(omega_m)
    best["p_fw"] = p_fw
    best["shaft_drag_W"] = best["p_fe"] + p_fw
    best["bus_draw_W"] = best["p_cu"] + INV["P_standby"]
    best["total_W"] = best["shaft_drag_W"] + best["bus_draw_W"]
    return best


def back_emf_ll_peak(rpm):
    """Open-circuit line-to-line peak voltage (UCG check)."""
    omega_e = MACH["p"] * rpm * 2.0 * math.pi / 60.0
    return omega_e * MACH["psi_m"] * math.sqrt(3.0)


def char_current():
    return MACH["psi_m"] / MACH["Ld"]


# ------------------------------------------------------------- inverter

def inverter_loss(I_amp, v_dc, enabled=True):
    """Two-level SiC inverter loss (W) at phase-current amplitude I_amp."""
    if not enabled:
        return 0.0
    irms = I_amp / math.sqrt(2.0)
    p_cond = 3.0 * irms * irms * (INV["Rds_on"] + INV["R_bus"])
    i_avg = 2.0 / math.pi * I_amp
    p_sw = 3.0 * INV["f_sw"] * INV["E_sw_ref"] * (v_dc / INV["V_ref"]) * (
        i_avg / INV["I_ref"])
    return p_cond + p_sw + INV["P_standby"]


def point_full(T_shaft, rpm, v_dc, I_max=None, T_wind=None):
    """Machine + inverter losses and efficiencies at one operating point.

    Returns None if infeasible. Efficiencies: motoring eta = P_shaft/P_dc,
    generating eta = P_dc_out/|P_shaft| (clamped at 0).
    """
    omega_m = rpm * 2.0 * math.pi / 60.0
    s = solve_point(T_shaft, omega_m, v_dc, I_max=I_max, T_wind=T_wind)
    if s is None:
        return None
    p_mech = T_shaft * omega_m
    p_loss_mach = s["p_cu"] + s["p_fe"] + s["p_fw"]
    p_inv = inverter_loss(s["I_amp"], v_dc)
    if T_shaft >= 0:
        p_dc = p_mech + p_loss_mach + p_inv
        eta = p_mech / p_dc if p_dc > 1e-9 else 0.0
    else:
        p_dc = p_mech + p_loss_mach + p_inv   # negative = into bus
        eta = (-p_dc) / (-p_mech) if p_mech < -1e-9 else 0.0
    eta = max(0.0, min(1.0, eta))
    return dict(T=T_shaft, rpm=rpm, P_shaft_W=p_mech, P_dc_W=p_dc,
                P_cu_W=s["p_cu"], P_fe_W=s["p_fe"], P_fw_W=s["p_fw"],
                P_inv_W=p_inv, I_amp=s["I_amp"], eta=eta,
                v_req=s["v_req"], psi_s=s["psi_s"])


def peak_power_curve(v_dc, I_max=None, rpm_lo=200.0, rpm_hi=None, n=73):
    """(rpm, T_max, P_max) over speed; returns list of dicts and the max P."""
    if rpm_hi is None:
        rpm_hi = MACH["rpm_max"]
    out = []
    p_best = 0.0
    for k in range(n):
        rpm = rpm_lo + (rpm_hi - rpm_lo) * k / (n - 1)
        omega = rpm * 2.0 * math.pi / 60.0
        t = max_torque(omega, v_dc, I_max)
        p = t * omega
        p_best = max(p_best, p)
        out.append(dict(rpm=rpm, T_max=t, P_max=p))
    return out, p_best
