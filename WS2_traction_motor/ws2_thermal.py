"""3-node lumped thermal model of the machine, and the duty-case runner.

Nodes: winding (w), stator+housing (s), rotor (r). Coolant = boundary.
Loss split per timestep: copper -> winding; iron -> (1-rotor_fe_frac) to
stator, rotor_fe_frac to rotor; friction/windage -> rotor_fw_frac to rotor,
rest to stator. Copper loss is re-evaluated each step at the CURRENT
winding temperature (resistance feedback), which is what makes thermal
runaway visible.
"""

import math

from ws2_params import THERM, MACH
import ws2_machine as mc


def _losses_at(T_shaft, rpm, v_dc, T_wind, standstill=False):
    if abs(rpm) < 1e-6 or standstill:
        # dc currents: same total copper, concentrated in one phase pair
        sol = mc.mtpa_current_for_torque(abs(T_shaft), MACH["I_peak"])
        if sol is None:
            return None
        id_, iq = sol
        I = math.hypot(id_, iq)
        p_cu = 1.5 * mc.rs_at(T_wind) * I * I
        return dict(p_cu=p_cu, p_fe=0.0, p_fw=0.0, I_amp=I,
                    hotspot=THERM["standstill_hotspot"])
    s = mc.solve_point(T_shaft, rpm * 2 * math.pi / 60.0, v_dc,
                       I_max=MACH["I_peak"], T_wind=T_wind)
    if s is None:
        return None
    return dict(p_cu=s["p_cu"], p_fe=s["p_fe"], p_fw=s["p_fw"],
                I_amp=s["I_amp"], hotspot=1.0)


def run_case(T_shaft, rpm, v_dc, build, t_end_s, dt=1.0,
             T0=None, T_cool=None, standstill=False, record_every=10.0):
    """Integrate the 3-node model at a fixed operating point.

    Returns dict with final temps, max temps, time-to-limit (winding
    hitting T_wind_max, None if never), and a decimated trace.
    """
    if T_cool is None:
        T_cool = THERM["T_cool_in"]
    G_ws = THERM["G_ws"][build]
    G_sc = THERM["G_sc"]
    G_rs = THERM["G_rs"]
    Cw, Cs, Cr = THERM["C_w"], THERM["C_s"], THERM["C_r"]
    if T0 is None:
        Tw = Ts = Tr = T_cool
    else:
        Tw, Ts, Tr = T0
    t = 0.0
    t_limit = None
    trace = []
    Tw_max = Ts_max = Tr_max = -1e9
    while t < t_end_s + 1e-9:
        L = _losses_at(T_shaft, rpm, v_dc, Tw, standstill=standstill)
        if L is None:
            return None
        # effective winding heating including standstill hot-spot factor:
        # model the hot phase by inflating the winding-side dissipation
        p_w = L["p_cu"] * L["hotspot"]
        p_s = L["p_fe"] * (1 - THERM["rotor_fe_frac"]) + \
            L["p_fw"] * (1 - THERM["rotor_fw_frac"])
        p_r = L["p_fe"] * THERM["rotor_fe_frac"] + \
            L["p_fw"] * THERM["rotor_fw_frac"]
        dTw = (p_w - G_ws * (Tw - Ts)) / Cw
        dTs = (p_s + G_ws * (Tw - Ts) + G_rs * (Tr - Ts)
               - G_sc * (Ts - T_cool)) / Cs
        dTr = (p_r - G_rs * (Tr - Ts)) / Cr
        Tw += dTw * dt
        Ts += dTs * dt
        Tr += dTr * dt
        t += dt
        Tw_max, Ts_max, Tr_max = max(Tw_max, Tw), max(Ts_max, Ts), max(Tr_max, Tr)
        if t_limit is None and Tw >= THERM["T_wind_max"]:
            t_limit = t
        if abs((t / record_every) - round(t / record_every)) < dt / (2 * record_every):
            trace.append((round(t, 1), round(Tw, 2), round(Ts, 2), round(Tr, 2)))
    return dict(T_final=(Tw, Ts, Tr), T_max=(Tw_max, Ts_max, Tr_max),
                t_limit_s=t_limit, trace=trace,
                loss_last=_losses_at(T_shaft, rpm, v_dc, Tw,
                                     standstill=standstill))


def steady_analytic(T_shaft, rpm, v_dc, build, T_cool=None, standstill=False):
    """Analytic steady state with resistance feedback (fixed-point on Tw).

    Steady balance:  Tr = Ts + p_r/G_rs;  Ts = T_cool + P_total/G_sc;
                     Tw = Ts + p_w/G_ws.
    Returns (Tw, Ts, Tr, losses) or None if the point is infeasible.
    """
    if T_cool is None:
        T_cool = THERM["T_cool_in"]
    G_ws = THERM["G_ws"][build]
    G_sc = THERM["G_sc"]
    G_rs = THERM["G_rs"]
    Tw = T_cool + 40.0
    L = None
    for _ in range(60):
        L = _losses_at(T_shaft, rpm, v_dc, Tw, standstill=standstill)
        if L is None:
            return None
        p_w = L["p_cu"] * L["hotspot"]
        p_s = L["p_fe"] * (1 - THERM["rotor_fe_frac"]) + \
            L["p_fw"] * (1 - THERM["rotor_fw_frac"])
        p_r = L["p_fe"] * THERM["rotor_fe_frac"] + \
            L["p_fw"] * THERM["rotor_fw_frac"]
        Ts = T_cool + (p_w + p_s + p_r) / G_sc
        Tr = Ts + p_r / G_rs
        Tw_new = Ts + p_w / G_ws
        if Tw_new > 400.0:
            return (Tw_new, Ts, Tr, L)  # runaway; caller checks limit
        if abs(Tw_new - Tw) < 0.01:
            return (Tw_new, Ts, Tr, L)
        Tw = 0.5 * Tw + 0.5 * Tw_new
    return (Tw, Ts, Tr, L)


def continuous_torque(rpm, v_dc, build, T_cool=None, T_limit=None,
                      standstill=False):
    """Max torque with steady-state winding temp <= T_limit (bisection)."""
    if T_limit is None:
        T_limit = THERM["T_wind_cont"]
    lo, hi = 0.0, mc.mtpa_torque(MACH["I_peak"])
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        r = steady_analytic(mid, rpm, v_dc, build, T_cool=T_cool,
                            standstill=standstill)
        if r is None or r[0] > T_limit:
            hi = mid
        else:
            lo = mid
    return lo


def hold_time_from(T_shaft, rpm, v_dc, build, T0, T_cool=None,
                   standstill=False, t_cap=3600.0):
    """Seconds until winding hits T_wind_max starting from temps T0."""
    r = run_case(T_shaft, rpm, v_dc, build, t_end_s=t_cap, dt=0.5, T0=T0,
                 T_cool=T_cool, standstill=standstill, record_every=t_cap)
    if r is None:
        return None, None
    return r["t_limit_s"], r
