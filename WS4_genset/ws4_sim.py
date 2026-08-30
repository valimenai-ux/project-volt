"""
Project Volt - WS4
Gate G1 simulator (VOLT-REG, modes a / b / bp) and the V1 start-stop
simulator (VOLT-SUB). This is the WS5 preview the assignment asks WS4 to
run itself: a causal, deterministic supervisor, tuned once, identical
settings across all seeds and modes unless a sensitivity says otherwise.

Modes over VOLT-REG (GATE G1, part-load derates everywhere):
  a  : locked 2.8:1 path above the WS1 lockup band, WITH charge-bias
       load-point shifting on the WS4 BSFC map (engine may be loaded above
       road load at the road-welded rpm, up to the min-BSFC torque at that
       rpm; surplus banked through the generator subject to the R2/R8
       50 kW continuous charge acceptance); series pinned-point start-stop
       when unlocked.
  b  : pure series at the pinned best-BSFC point, start-stop hysteresis
       (the only degree of freedom a pinned point leaves).
  bp : sensitivity only, NOT the G1 metric - series load-following along
       the best-BSFC locus (what a V1-with-125-kW-genset would really do).

Energy accounting follows the WS1 four_numbers convention: all modes
follow the identical wheel-power trace (net-energy comparison); seconds
where demanded motor-shaft power exceeds the R3 rating are counted and
reported, not clipped.
"""
import math
import numpy as np

from ws4_models import (VEH, DL, CTL, part_load_factor,
                        BATT_ETA_CHG, BATT_ETA_DIS, CHG_CONT_BUS_KW,
                        MOTOR_RATED_KW, LHV_KJ_PER_G)
import volt_physics as vp          # WS1, read-only import

START_FUEL_G = 12.0    # declared per-start fuel adder for a SERIES start:
                       # ~4 s load-acceptance ramp at roughly half the
                       # pinned-point fuel rate (WS1 E6's 4 s transient)
                       # + cranking. Applied identically in every mode.
SYNC_FUEL_G = 1.5      # declared per-engagement adder for a LOCKUP sync
                       # start: the baseline's motor-synchronised clutch
                       # (WS1 E11: ~4 kJ crank spin-up + ~8 kW x 0.5 s
                       # motoring drag ~ 12 kJ bus ~ 0.8 g fuel-equivalent;
                       # 1.5 g carries margin for clutch slip)
SOC_START = 0.55       # supervisor SOC target (WS1 convention)
SER_LO, SER_HI = 0.35, 0.75    # series start-stop hysteresis (frac usable)
EMERG_LO, EMERG_HI = 0.25, 0.40  # emergency load-follow band: below 25%
                               # SOC the series engine may leave the pinned
                               # point and follow the bus load along the
                               # best-BSFC locus up to its continuous
                               # rating (the vehicle must complete the
                               # cycle; a pinned point that cannot carry
                               # the road is not licence to shed load).
                               # Identical in every mode.
BIAS_LO, BIAS_HI = 0.55, 0.65  # charge-bias band: full 50 kW banking below
                               # 55% SOC, tapering to zero at 65%
DENSITY_G_PER_L = 832.0        # diesel EN590 at 15 C


def wheel_power_trace(cyc, m, veh=VEH):
    wp = vp.wheel_power(cyc["t"], cyc["v"], cyc["grade"], m,
                        lam=veh.lam_rot, veh=veh)
    return wp["P_wheel"]


def lockup_state(v, p_wheel_w, v_lock=CTL.v_lockup, hyst=3.0 / 3.6):
    """WS1's lockup mask: speed hysteresis AND positive wheel demand
    (regen-priority clutch opening)."""
    locked = np.zeros(v.size, dtype=bool)
    st = False
    for i in range(v.size):
        if st and v[i] < v_lock - hyst:
            st = False
        elif (not st) and v[i] > v_lock + hyst:
            st = True
        locked[i] = st and (p_wheel_w[i] > 0.0)
    return locked


def _bsfc_fast(eng, rpm, trq, tmax):
    """Scalar Willans BSFC, pure-python fast path (must mirror
    WillansEngine.bsfc; asserted against it in run_ws4)."""
    if trq <= 0.0 or tmax <= 0.0:
        return float("inf")
    phi = trq / tmax
    if phi > 1.0:
        phi = 1.0
    bmep = 4 * math.pi * trq / eng.disp_m3 / 1e5
    n = rpm / 1000.0
    a0, a1, a2 = eng.fmep_a
    fmep = a0 + a1 * n + a2 * n * n
    f_n = 1.0 - 0.06 * ((rpm - 1600.0) / 1400.0) ** 2
    lo = 1.0 - 0.05 * max(0.0, 0.45 - phi) / 0.45
    hi = 1.0 - 0.35 * max(0.0, phi - 0.85)
    f_phi = min(lo, hi)
    eta = eng.eta_i0 * f_n * f_phi * bmep / (bmep + fmep)
    return 3600.0 / LHV_KJ_PER_G / eta


def _gen_elec_from_shaft(gen, rpm, p_shaft_kw):
    """Scalar generator forward conversion (elec kW from shaft kW)."""
    if p_shaft_kw <= 0.0:
        return 0.0
    w = rpm * 2 * math.pi / 60.0
    t = p_shaft_kw * 1e3 / w
    fe = gen.c_h * (rpm / 1800.0) + gen.c_e * (rpm / 1800.0) ** 2
    p_e = p_shaft_kw
    for _ in range(3):
        p_e = p_shaft_kw - (fe + gen.k_cu * (t / 100.0) ** 2
                            + gen.pe0 + gen.pe_frac * max(p_e, 0.0))
    return max(0.0, p_e)


def _gen_shaft_from_elec(gen, rpm, p_elec_kw):
    """Scalar generator inversion (shaft kW for elec kW at rpm)."""
    w = rpm * 2 * math.pi / 60.0
    p_s = p_elec_kw * 1.06 + 0.5
    for _ in range(4):
        t = p_s * 1e3 / w
        p_s = p_elec_kw + (gen.c_h * (rpm / 1800.0)
                           + gen.c_e * (rpm / 1800.0) ** 2
                           + gen.k_cu * (t / 100.0) ** 2
                           + gen.pe0 + gen.pe_frac * max(p_elec_kw, 0.0))
    return p_s


def _topt_table(engine, derate):
    rpms = np.arange(float(engine.rpm_pts[0]), float(engine.rpm_pts[-1]) + 1,
                     25.0)
    topt = np.empty_like(rpms)
    for k, N in enumerate(rpms):
        tm = float(engine.t_max(N)) * derate
        tq = np.linspace(1.0, tm, 240)
        topt[k] = float(tq[np.argmin(engine.bsfc(N, tq))])
    return rpms, topt


def pinned_point(engine, gen, derate):
    """Best-BSFC point inside the derated continuous rating and derated
    full-load curve, with the generator conversion at that point."""
    pin = engine.min_bsfc_point(p_cap_kw=engine.rated_cont_kw * derate)
    trq = min(pin["trq_Nm"], float(engine.t_max(pin["rpm"])) * derate)
    p_shaft = trq * pin["rpm"] * 2 * math.pi / 60 / 1e3
    bsfc = float(engine.bsfc(pin["rpm"], trq))
    p_bus = float(gen.elec_from_shaft(pin["rpm"], p_shaft))
    return dict(rpm=pin["rpm"], trq_Nm=trq, p_shaft_kw=p_shaft,
                bsfc=bsfc, p_bus_kw=p_bus,
                fuel_gps=bsfc * p_shaft / 3600.0,
                eta_gen=p_bus / p_shaft)


def run_g1_mode(cyc, mode, engine, gen, usable_kwh, p_aux_kw=2.0,
                veh=VEH, m=None, derate=1.0, regen_cap_kw=75.0,
                chain=None, spin_shaft_kw=0.0, spin_bus_kw=0.0):
    """Simulate one mode over one cycle realisation. Returns totals.

    G1-R additions (both default OFF so the ratified r2 configuration is
    reproduced bit-identically as the regression anchor):
      chain         : None -> legacy WS1 scalar chain (0.8656 x
                      part_load_factor); a ws4_chain.WS2TractionChain ->
                      R12 convention (WS2 measured maps x 0.97 reduction,
                      no scalar PE member, no part_load_factor). Applied
                      to BOTH modes identically (directive 1a).
      spin_shaft_kw : PM traction-machine unloaded spin drag charged to
      spin_bus_kw     the engine shaft / drawn from the bus during LOCKED
                      samples only (WS2's measured lockup-only tax,
                      directive 1b). Modes (b)/(b') never lock, so they
                      carry no spin member by construction.
    """
    m = veh.m_gvw if m is None else m
    t = cyc["t"]; v = cyc["v"]
    dt = float(np.median(np.diff(t)))
    p_wheel = wheel_power_trace(cyc, m, veh) / 1e3          # kW
    rpm_locked = v / veh.r_dyn * veh.fd_ratio * 60.0 / (2 * np.pi)

    locked_arr = (lockup_state(v, p_wheel * 1e3) if mode == "a"
                  else np.zeros(v.size, bool))

    pin = pinned_point(engine, gen, derate)
    p_peak_kw = engine.peak_power_kw()

    # precomputed per-step vectors
    tmax_arr = engine.t_max(rpm_locked) * derate
    tg_rpms, tg_topt = _topt_table(engine, derate)
    topt_arr = np.interp(rpm_locked, tg_rpms, tg_topt)
    spin_dl_arr = 0.9 * rpm_locked / 1800.0                # kW churning
    w_arr = rpm_locked * 2 * np.pi / 60.0
    # regen precompute (wheel-side captured, before battery headroom)
    blend = np.clip((v - CTL.v_regen_blend_lo) /
                    (CTL.v_regen_blend_hi - CTL.v_regen_blend_lo), 0.0, 1.0)
    p_capt0 = np.minimum(np.clip(-p_wheel, 0.0, None), regen_cap_kw) * blend
    if chain is None:
        k_rg = part_load_factor(p_capt0 / MOTOR_RATED_KW)
        eta_rg = DL.eta_wheel_to_bus * k_rg                # wheel->bus
        # traction chain (unlocked positive)
        k_tr = part_load_factor(np.clip(p_wheel, 0.0, None) / MOTOR_RATED_KW)
        eta_tr = DL.eta_bus_to_wheel * k_tr
    else:
        # R12: WS2 measured maps x 0.97 reduction, both directions;
        # no scalar PE member, no part_load_factor
        eta_rg = chain.eta_wheel_to_bus(v, p_capt0)
        eta_tr = chain.eta_bus_to_wheel(v, np.clip(p_wheel, 0.0, None))

    loc = engine.opt_locus()
    okm = np.isfinite(loc["bsfc"])
    loc_p, loc_rpm, loc_trq = (loc["p_kw"][okm], loc["rpm"][okm],
                               loc["trq"][okm])
    p_min_bp = 25.0

    e_cap = usable_kwh * 3.6e6
    e = e_cap * SOC_START
    ser_on = False
    emerg = False
    eng_running_prev = False
    fuel_g = 0.0
    starts = 0
    sync_starts = 0

    agg = dict(e_fric_kwh=0.0, e_gen_loss_kwh=0.0, e_chain_loss_kwh=0.0,
               e_dl_loss_kwh=0.0, eng_kwh=0.0, eng_on_s=0.0, locked_s=0.0,
               bank_kwh=0.0, over_rating_s=0.0, e_bus_kwh=0.0,
               eng_reject_kwh=0.0, e_dir_wheel_kwh=0.0, emerg_s=0.0,
               unserved_kwh=0.0, e_spin_shaft_kwh=0.0, e_spin_bus_kwh=0.0)

    for i in range(v.size):
        pw = float(p_wheel[i])
        # motor-shaft overload bookkeeping (R3 rating), e-machine share only
        if not locked_arr[i]:
            p_ms = abs(pw) / DL.eta_red if pw >= 0 else min(abs(pw),
                                                            regen_cap_kw)
            if p_ms > MOTOR_RATED_KW:
                agg["over_rating_s"] += dt

        # series on/off hysteresis (SOC), evolves continuously
        if e < SER_LO * e_cap:
            ser_on = True
        elif e > SER_HI * e_cap:
            ser_on = False
        # emergency band (all modes): below EMERG_LO the series engine may
        # leave the pin / continuous cap and follow load up to the full-
        # load curve - the same curve mode (a) uses when locked
        if e < EMERG_LO * e_cap:
            emerg = True
        elif e > EMERG_HI * e_cap:
            emerg = False

        p_bus_load = p_aux_kw
        p_fric = 0.0
        eng_running = False
        f_gps = 0.0
        p_shaft_eng = 0.0
        p_gen_elec = 0.0
        p_gen_loss = 0.0

        if locked_arr[i]:
            # ---------------- locked direct path ----------------------
            eng_running = True
            N = float(rpm_locked[i]); w = float(w_arr[i])
            tmax = float(tmax_arr[i])
            # PM spin drag (G1-R 1b): the unloaded traction machine's
            # shaft drag is coupled to the driveline - the engine carries
            # it with priority (it cannot be shed) - and its standby/
            # flux-weakening draw lands on the bus. Zero when unlocked
            # and in modes (b)/(b') (never locked).
            p_shaft_road = (pw + float(spin_dl_arr[i])) / 0.972
            t_road = (p_shaft_road + spin_shaft_kw) * 1e3 / w
            deficit_wheel = 0.0
            if t_road > tmax:
                p_shaft_road = max(0.0, tmax * w / 1e3 - spin_shaft_kw)
                p_w_dir = max(0.0, p_shaft_road * 0.972 - float(spin_dl_arr[i]))
                deficit_wheel = pw - p_w_dir
                t_road = tmax
            p_bus_load += spin_bus_kw
            agg["e_spin_shaft_kwh"] += spin_shaft_kw * dt / 3600.0
            agg["e_spin_bus_kwh"] += spin_bus_kw * dt / 3600.0
            agg["e_dl_loss_kwh"] += (p_shaft_road - (pw - deficit_wheel)) \
                * dt / 3600.0
            agg["e_dir_wheel_kwh"] += (pw - deficit_wheel) * dt / 3600.0
            if deficit_wheel > 0.0:
                if chain is None:
                    eta_c = DL.eta_bus_to_wheel * float(
                        part_load_factor(deficit_wheel / MOTOR_RATED_KW))
                elif spin_shaft_kw > 0.0:
                    # spin member already charges the machine's no-load
                    # losses on this locked sample - fill at marginal
                    # map loss to avoid double-counting them
                    eta_c = chain.eta_bus_to_wheel_marginal_scalar(
                        float(v[i]), deficit_wheel)
                else:
                    eta_c = chain.eta_bus_to_wheel_scalar(float(v[i]),
                                                          deficit_wheel)
                p_bus_load += deficit_wheel / eta_c
                agg["e_chain_loss_kwh"] += deficit_wheel * (1 / eta_c - 1) \
                    * dt / 3600.0
                # R3 rating exposure of the torque-fill motor while locked
                # (adjudication r1 F7: locked-sample deficit fill is now
                # checked against the rating, same motor-shaft convention
                # as the unlocked branch)
                if deficit_wheel / DL.eta_red > MOTOR_RATED_KW:
                    agg["over_rating_s"] += dt

            # charge-bias load-point shifting
            soc = e / e_cap
            bias = min(max((BIAS_HI - soc) / (BIAS_HI - BIAS_LO), 0.0), 1.0)
            head_rate = max(0.0, (e_cap - e)) / dt / 1e3 / BATT_ETA_CHG  # kW
            p_bank_want = min(CHG_CONT_BUS_KW * bias, head_rate)
            # generator caps: serve (aux + motor deficit) may use torque up
            # to tmax; banking must not push total torque past t_opt
            t_budget_serve = max(0.0, tmax - t_road)
            ge_cap_serve = _gen_elec_from_shaft(gen, N,
                                                t_budget_serve * w / 1e3)
            ge_cont_elec = _gen_elec_from_shaft(gen, N, gen.cont_kw_in)
            p_ge_serve = min(p_bus_load, ge_cap_serve, ge_cont_elec)
            t_budget_bank = max(0.0, float(topt_arr[i]) - t_road)
            ge_cap_bank_total = _gen_elec_from_shaft(gen, N,
                                                     t_budget_bank * w / 1e3)
            p_ge = min(p_ge_serve + p_bank_want,
                       max(p_ge_serve, ge_cap_bank_total), ge_cont_elec)
            p_shaft_gen = _gen_shaft_from_elec(gen, N, p_ge) if p_ge > 0.0 \
                else (gen.c_h * N / 1800.0 + gen.c_e * (N / 1800.0) ** 2)
            t_e = t_road + p_shaft_gen * 1e3 / w
            if t_e > tmax:                      # final safety clip
                t_e = tmax
                p_shaft_gen = max(0.0, t_e * w / 1e3 - p_shaft_road
                                  - spin_shaft_kw)
                p_ge = float(gen.elec_from_shaft(N, p_shaft_gen))
            p_shaft_eng = p_shaft_road + spin_shaft_kw + p_shaft_gen
            p_gen_elec = p_ge
            p_gen_loss = p_shaft_gen - p_ge
            f_gps = _bsfc_fast(engine, N, t_e, tmax) * p_shaft_eng / 3600.0
            agg["eng_reject_kwh"] += (f_gps * LHV_KJ_PER_G - p_shaft_eng) \
                * dt / 3600.0
        else:
            # ---------------- unlocked: motor handles the wheel --------
            if pw > 0.0:
                eta_c = float(eta_tr[i])
                p_bus_load += pw / eta_c
                agg["e_chain_loss_kwh"] += pw * (1 / eta_c - 1) * dt / 3600.0
            elif pw < 0.0:
                p_rg_bus = float(p_capt0[i] * eta_rg[i])
                p_fric = -pw - float(p_capt0[i])
                head_rate = max(0.0, (e_cap - e)) / dt / 1e3 / BATT_ETA_CHG
                spill = max(0.0, p_rg_bus - max(0.0, head_rate - p_aux_kw))
                p_rg_bus -= spill
                p_fric += spill / float(eta_rg[i]) if eta_rg[i] > 0 else 0.0
                p_bus_load -= p_rg_bus
                if eta_rg[i] > 0:
                    agg["e_chain_loss_kwh"] += p_rg_bus \
                        * (1 - eta_rg[i]) / eta_rg[i] * dt / 3600.0

            if mode in ("a", "b"):
                if ser_on:
                    eng_running = True
                    if emerg:
                        # load-follow along the locus, >= pin, up to the
                        # full-load curve (same curve mode a uses locked)
                        trim = (EMERG_HI * e_cap - e) / 120.0 / 1e3   # kW
                        p_sh = min(p_peak_kw * derate * 0.97,
                                   max(pin["p_shaft_kw"],
                                       (max(p_bus_load, 0.0) + trim) * 1.06))
                        rpm_e = float(np.interp(p_sh, loc_p, loc_rpm))
                        trq_e = min(float(np.interp(p_sh, loc_p, loc_trq)),
                                    float(engine.t_max(rpm_e)) * derate)
                        p_sh = trq_e * rpm_e * 2 * math.pi / 60 / 1e3
                        p_gen_elec = _gen_elec_from_shaft(gen, rpm_e, p_sh)
                        p_gen_loss = p_sh - p_gen_elec
                        p_shaft_eng = p_sh
                        tm_e = float(engine.t_max(rpm_e)) * derate
                        f_gps = _bsfc_fast(engine, rpm_e, trq_e, tm_e) \
                            * p_sh / 3600.0
                        agg["emerg_s"] += dt
                    else:
                        p_gen_elec = pin["p_bus_kw"]
                        p_gen_loss = pin["p_shaft_kw"] - pin["p_bus_kw"]
                        p_shaft_eng = pin["p_shaft_kw"]
                        f_gps = pin["fuel_gps"]
                    agg["eng_reject_kwh"] += (f_gps * LHV_KJ_PER_G
                                              - p_shaft_eng) * dt / 3600.0
            else:                                     # bp
                if ser_on:
                    eng_running = True
                    soc = e / e_cap
                    trim = (SOC_START - soc) * e_cap / 240.0 / 1e3   # kW
                    p_bus_want = max(p_bus_load, 0.0) + trim
                    p_cap_bp = (p_peak_kw * derate * 0.97
                                if emerg else engine.rated_cont_kw * derate)
                    if emerg:
                        agg["emerg_s"] += dt
                    p_sh = min(max(p_min_bp, p_bus_want * 1.06), p_cap_bp)
                    rpm_bp = float(np.interp(p_sh, loc_p, loc_rpm))
                    trq_bp = min(float(np.interp(p_sh, loc_p, loc_trq)),
                                 float(engine.t_max(rpm_bp)) * derate)
                    p_sh = trq_bp * rpm_bp * 2 * math.pi / 60 / 1e3
                    p_gen_elec = float(gen.elec_from_shaft(rpm_bp, p_sh))
                    p_gen_loss = p_sh - p_gen_elec
                    p_shaft_eng = p_sh
                    tm_bp = float(engine.t_max(rpm_bp)) * derate
                    f_gps = _bsfc_fast(engine, rpm_bp, trq_bp, tm_bp) \
                        * p_sh / 3600.0
                    agg["eng_reject_kwh"] += (f_gps * LHV_KJ_PER_G - p_sh) \
                        * dt / 3600.0

        p_batt_bus = p_gen_elec - p_bus_load          # + = charge
        if locked_arr[i]:
            agg["bank_kwh"] += max(0.0, p_batt_bus) * dt / 3600.0

        # battery update
        if p_batt_bus >= 0.0:
            de = p_batt_bus * 1e3 * BATT_ETA_CHG * dt
            if e + de > e_cap:
                de = e_cap - e
            e += de
        else:
            de = p_batt_bus * 1e3 / BATT_ETA_DIS * dt
            if e + de < 0.0:
                # bus demand the battery could not serve - tracked, and it
                # must stay ~zero or the mode failed to follow the cycle
                agg["unserved_kwh"] += -(e + de) * BATT_ETA_DIS / 3.6e6
                de = -e
            e += de

        fuel_g += f_gps * dt
        if eng_running and not eng_running_prev:
            starts += 1
            if locked_arr[i]:
                fuel_g += SYNC_FUEL_G       # motor-synchronised bump start
                sync_starts += 1
            else:
                fuel_g += START_FUEL_G      # genset load-acceptance ramp
        eng_running_prev = eng_running
        agg["e_fric_kwh"] += p_fric * dt / 3600.0
        agg["e_gen_loss_kwh"] += p_gen_loss * dt / 3600.0
        agg["eng_kwh"] += p_shaft_eng * dt / 3600.0
        agg["eng_on_s"] += dt if eng_running else 0.0
        agg["locked_s"] += dt if locked_arr[i] else 0.0
        agg["e_bus_kwh"] += max(0.0, p_bus_load) * dt / 3600.0

    # SOC-drift correction at the pinned point's marginal rate
    drift_kwh_cells = (e - e_cap * SOC_START) / 3.6e6
    if drift_kwh_cells < 0:
        corr_g = (-drift_kwh_cells) / BATT_ETA_CHG / pin["eta_gen"] \
            * pin["bsfc"]
    else:
        corr_g = -drift_kwh_cells * BATT_ETA_DIS / pin["eta_gen"] \
            * pin["bsfc"]
    # unserved bus energy (buffer hit empty - the buffer, not the engine,
    # was the limit) is charged to fuel at the marginal buffered-series
    # rate so the energy books balance; it is also reported raw, because
    # a non-zero value means the mode could not follow the cycle
    corr_unserved_g = agg["unserved_kwh"] \
        / (BATT_ETA_CHG * BATT_ETA_DIS * pin["eta_gen"]) * pin["bsfc"]
    fuel_corr_g = fuel_g + corr_g + corr_unserved_g

    out = dict(mode=mode, fuel_g=fuel_g, fuel_corrected_g=fuel_corr_g,
               soc_drift_kwh_cells=drift_kwh_cells,
               fuel_energy_kwh=fuel_corr_g * LHV_KJ_PER_G / 3600.0,
               fuel_l=fuel_corr_g / DENSITY_G_PER_L,
               starts=starts, sync_starts=sync_starts,
               ramp_starts=starts - sync_starts,
               duration_s=float(t[-1] - t[0]),
               distance_km=float(vp.trapz(v, t)) / 1e3,
               pinned=pin, **agg)
    out["l_per_100km"] = out["fuel_l"] / out["distance_km"] * 100.0
    out["mean_bsfc_eff_g_per_kwh"] = (fuel_corr_g / agg["eng_kwh"]
                                      if agg["eng_kwh"] > 0 else float("inf"))
    return out


# --------------------------------------------------- V1 start-stop (VOLT-SUB)
def run_v1_startstop(cyc, engine, gen, usable_kwh, hyst_kwh,
                     p_aux_kw=2.0, regen_cap_kw=75.0, veh=VEH, m=None,
                     strategy="startstop"):
    """V1 series start-stop on VOLT-SUB. The hysteresis band `hyst_kwh` is
    centred on the 55% SOC target inside `usable_kwh` (R8: the rest of the
    window is regen headroom / grade reserve / end-stops and is NOT
    available to the start-stop swing).

    strategy 'startstop' : engine ON at its pinned point, OFF otherwise.
    strategy 'continuous': engine always on, load-following along the
    best-BSFC locus (the 20%-load-factor alternative E6 warns about)."""
    m = veh.m_gvw if m is None else m
    t = cyc["t"]; v = cyc["v"]
    dt = float(np.median(np.diff(t)))
    p_wheel = wheel_power_trace(cyc, m, veh) / 1e3

    pin = pinned_point(engine, gen, 1.0)

    loc = engine.opt_locus()
    okm = np.isfinite(loc["bsfc"])
    loc_p, loc_rpm, loc_trq = loc["p_kw"][okm], loc["rpm"][okm], loc["trq"][okm]

    blend = np.clip((v - CTL.v_regen_blend_lo) /
                    (CTL.v_regen_blend_hi - CTL.v_regen_blend_lo), 0.0, 1.0)
    p_capt0 = np.minimum(np.clip(-p_wheel, 0.0, None), regen_cap_kw) * blend
    eta_rg = DL.eta_wheel_to_bus * part_load_factor(p_capt0 / MOTOR_RATED_KW)
    eta_tr = DL.eta_bus_to_wheel * part_load_factor(
        np.clip(p_wheel, 0.0, None) / MOTOR_RATED_KW)

    e_cap = usable_kwh * 3.6e6
    e = e_cap * SOC_START
    lo = e_cap * SOC_START - hyst_kwh * 3.6e6 / 2.0
    hi = e_cap * SOC_START + hyst_kwh * 3.6e6 / 2.0
    on = False
    on_prev = False
    fuel_g = 0.0; starts = 0
    eng_kwh = 0.0; on_s = 0.0; fric_kwh = 0.0; gen_loss_kwh = 0.0
    eng_reject_kwh = 0.0
    forced_starts = 0
    unserved_kwh = 0.0

    for i in range(v.size):
        pw = float(p_wheel[i])
        if e < lo:
            if not on and e <= 1e3:
                forced_starts += 1
            on = True
        elif e > hi:
            on = False
        p_bus_load = p_aux_kw
        p_fric = 0.0
        if pw > 0:
            p_bus_load += pw / float(eta_tr[i])
        elif pw < 0:
            p_rg = float(p_capt0[i] * eta_rg[i])
            p_fric = -pw - float(p_capt0[i])
            head_rate = max(0.0, (e_cap - e)) / dt / 1e3 / BATT_ETA_CHG
            spill = max(0.0, p_rg - max(0.0, head_rate - p_aux_kw))
            p_rg -= spill
            if eta_rg[i] > 0:
                p_fric += spill / float(eta_rg[i])
            p_bus_load -= p_rg
        f_gps = 0.0; p_ge = 0.0; p_sh = 0.0; gl = 0.0
        if strategy == "startstop":
            if on:
                p_ge = pin["p_bus_kw"]; p_sh = pin["p_shaft_kw"]
                f_gps = pin["fuel_gps"]; gl = p_sh - p_ge
        else:
            on = True
            soc = e / e_cap
            trim = (SOC_START - soc) * e_cap / 240.0 / 1e3
            want = max(2.0, p_bus_load + trim)
            p_sh = float(np.clip(want * 1.10, 6.0, pin["p_shaft_kw"]))
            rpm_ = float(np.interp(p_sh, loc_p, loc_rpm))
            trq_ = min(float(np.interp(p_sh, loc_p, loc_trq)),
                       float(engine.t_max(rpm_)))
            p_sh = trq_ * rpm_ * 2 * math.pi / 60 / 1e3
            p_ge = float(gen.elec_from_shaft(rpm_, p_sh))
            gl = p_sh - p_ge
            f_gps = float(engine.fuel_gps(rpm_, trq_))
        if on and p_sh > 0:
            eng_reject_kwh += (f_gps * LHV_KJ_PER_G - p_sh) * dt / 3600.0
        p_batt_bus = p_ge - p_bus_load
        if p_batt_bus >= 0:
            de = min(p_batt_bus * 1e3 * BATT_ETA_CHG * dt, e_cap - e)
        else:
            de = p_batt_bus * 1e3 / BATT_ETA_DIS * dt
            if e + de < 0.0:
                unserved_kwh += -(e + de) * BATT_ETA_DIS / 3.6e6
                de = -e
        e += de
        fuel_g += f_gps * dt
        if on and not on_prev:
            starts += 1
            fuel_g += START_FUEL_G
        on_prev = on
        eng_kwh += p_sh * dt / 3600.0
        on_s += dt if on else 0.0
        fric_kwh += p_fric * dt / 3600.0
        gen_loss_kwh += gl * dt / 3600.0

    T = float(t[-1] - t[0])
    drift_kwh = (e - e_cap * SOC_START) / 3.6e6
    corr_g = (-drift_kwh / BATT_ETA_CHG / pin["eta_gen"] * pin["bsfc"]
              if drift_kwh < 0
              else -drift_kwh * BATT_ETA_DIS / pin["eta_gen"] * pin["bsfc"])
    fuel_c = fuel_g + corr_g
    return dict(strategy=strategy, fuel_corrected_g=fuel_c,
                fuel_g_per_h=fuel_c / T * 3600.0,
                fuel_l_per_h=fuel_c / T * 3600.0 / DENSITY_G_PER_L,
                soc_drift_kwh=drift_kwh,
                starts=starts, starts_per_h=starts / T * 3600.0,
                starts_per_8h_shift=starts / T * 3600.0 * 8.0,
                forced_starts_at_empty=forced_starts,
                unserved_kwh=unserved_kwh,
                duty=on_s / T, eng_kwh=eng_kwh,
                distance_km=float(vp.trapz(v, t)) / 1e3, duration_s=T,
                fric_kwh=fric_kwh, gen_loss_kwh=gen_loss_kwh,
                eng_reject_kwh=eng_reject_kwh,
                mean_reject_when_on_kw=(eng_reject_kwh / (on_s / 3600.0)
                                        if on_s > 0 else 0.0),
                pinned=pin)
