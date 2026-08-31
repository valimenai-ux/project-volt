"""
Project Volt - WS5
The supervisor: one causal 10 Hz control loop covering energy management,
genset dispatch, brake blending (R15), traction control (E23), thermal-aware
derating (R16) and fault management (R22c).

Architecture of record (BASELINE_v3/v5): BOTH variants are PURE SERIES.
There is no clutch, no mode selection and no synchronisation in this file.

Conventions
  * 10 Hz throughout (R9); all electrical quantities BUS-SIDE (R12).
  * Traction chain = WS2 measured inverter+motor maps x 0.97 reduction,
    no scalar PE member (R12), consumed through ws5_inputs.CHAIN.
  * Energy books use WS1's ratified flat 0.97 buffer round-trip convention,
    identical to WS4's ratified simulator, so WS5 numbers are directly
    comparable with interface_ws4.series_duty_v2. WS3's electro-thermal pack
    model runs ALONGSIDE as the source of the dispatch limits, the bus
    voltage and the pack heat for the WS6 ledger; the difference between the
    two accountings is exported as a reconciliation line, not hidden.
  * Engine set-points are taken on WS4's best-BSFC locus using WS4's own
    shaft-target convention (P_shaft = P_bus_want x 1.06, clamped), so a
    WS5 run with every policy layer disabled (Cfg.ws4_concordance) is a
    like-for-like reproduction of interface_ws4.series_duty_v2.
  * STRICTLY CAUSAL. No preview, no route lookahead, no oracle. Every
    filter is a one-pole low-pass on measured history.
"""
import math
from dataclasses import dataclass

import numpy as np

import ws5_inputs as I
import ws5_statemachine as SM
# WS4's own asserted scalar fast paths, imported so WS5's set-point
# arithmetic is bit-identical to the ratified simulator's, not a re-write.
from ws4_sim import _bsfc_fast as _ws4_bsfc_fast          # noqa: E402
from ws4_sim import _gen_elec_from_shaft as _ws4_gen_elec  # noqa: E402

BATT_ETA_CHG = 0.97          # WS1 ratified buffer convention (as WS4)
BATT_ETA_DIS = 0.97
START_FUEL_G = 12.0          # WS4's declared per-start series adder (WS1 E6)
MOTOR_RATED_KW = 150.0       # R3 target rating, over-rating counter basis
REGEN_CAP_WHEEL_KW = 75.0    # WS1 ratified 75 kW absorb cap, at the wheel
ETA_RED = 0.97               # R12 reduction stage

# ------------------------------------------------ WS5-DECLARED constants
P_START_RAMP_S = 4.0         # genset load-acceptance ramp (WS1 E6 transient)
GEN_RATE_KW_PER_S = 25.0     # genset bus-power slew limit
TAU_DEMAND_S = 60.0          # two-point notch filter time constant
NOTCH_UP_KW = 5.0            # two-point raise hysteresis (bus kW)
NOTCH_DN_KW = 10.0           # two-point lower hysteresis (bus kW)
RESERVE_MARGIN_KW = 8.0      # ESC-9 power-reserve margin below the pack cap
TAU_RESERVE_S = 2.0          # reserve-trigger filter (fast: it is a limit)
TJ_TAU_S = 30.0              # inverter junction first-order time constant
TJ_K_PER_KW = (130.0 - 65.0) / 10.57   # calibrated on WS2's exported pair:
                             # 130 C junction at the R13 continuous case
                             # (10.57 kW LT-loop heat) with the 65 C max
                             # LT inlet. [WS5-DECLARED lumped calibration]
T_COOLANT_LT_MAX_C = 65.0    # WS2 declared max LT inlet
LT_RISE_K = 20.0             # [WS5-DECLARED] LT coolant rise over ambient;
                             # the loop reaches WS2's 65 C ceiling at the
                             # +45 C corner and sits below it elsewhere
MU_PRIOR_DRY = 0.80          # traction-control mu prior, dry road
COAST_BAND_FACTOR = 1.5      # [WS5-DECLARED] a sample is 'zero-torque
                             # coasting' when |P_wheel| is within this
                             # multiple of the PM drag itself - i.e. the
                             # machine is at essentially zero torque. Scales
                             # with speed, because the drag does.
GEN_LOSS_ALLOWANCE = 1.06    # WS4's shaft-target allowance for gen losses
P_MIN_FOLLOW_KW = 25.0       # WS4's load-following floor
NVH_DPDT_THRESHOLD_KW_PER_S = 5.0   # [WS5-DECLARED] a set-point RATE above
                             # this is counted as an NVH event. Reported as
                             # a diagnostic only - it is NOT a term in the
                             # R22b decision rule, which was fixed first.

LHV = I.LHV_KJ_PER_G
DENSITY_G_PER_L = I.DENSITY_G_PER_L

CONTROL_CONSTANTS = dict(
    P_START_RAMP_S=P_START_RAMP_S, GEN_RATE_KW_PER_S=GEN_RATE_KW_PER_S,
    TAU_DEMAND_S=TAU_DEMAND_S, NOTCH_UP_KW=NOTCH_UP_KW,
    NOTCH_DN_KW=NOTCH_DN_KW, RESERVE_MARGIN_KW=RESERVE_MARGIN_KW,
    TAU_RESERVE_S=TAU_RESERVE_S, TJ_TAU_S=TJ_TAU_S,
    TJ_K_PER_KW=TJ_K_PER_KW, T_COOLANT_LT_MAX_C=T_COOLANT_LT_MAX_C,
    LT_RISE_K=LT_RISE_K,
    MU_PRIOR_DRY=MU_PRIOR_DRY, START_FUEL_G=START_FUEL_G,
    REGEN_CAP_WHEEL_KW=REGEN_CAP_WHEEL_KW,
    SETPOINT_DEADBAND_KW=SM.SETPOINT_DEADBAND_KW,
    INV_TJ_DERATE_C=SM.INV_TJ_DERATE_C, INV_TJ_TRIP_C=SM.INV_TJ_TRIP_C,
    GEN_LOSS_ALLOWANCE=GEN_LOSS_ALLOWANCE, P_MIN_FOLLOW_KW=P_MIN_FOLLOW_KW,
    NVH_DPDT_THRESHOLD_KW_PER_S=NVH_DPDT_THRESHOLD_KW_PER_S,
    COAST_BAND_FACTOR=COAST_BAND_FACTOR,
)


# ------------------------------------------------------- fast pack helpers
_CELL = I.PACK.cell
_NS = I.PACK.ns
_SOC_GRID = np.linspace(0.0, 1.0, 1001)
_OCV_GRID = np.asarray(I.w3c.ocv(_SOC_GRID, _CELL), float)
_RSOC_GRID = np.interp(_SOC_GRID, I.w3c.SOC_GRID_R, I.w3c.R_MULT_SOC)
_R_BASE = _CELL["r_dc_mohm"] * 1e-3


def _ocv_fast(soc):
    x = min(max(soc, 0.0), 1.0) * 1000.0
    i = int(x)
    if i >= 1000:
        return float(_OCV_GRID[1000])
    f = x - i
    return float(_OCV_GRID[i] * (1 - f) + _OCV_GRID[i + 1] * f)


def _rsoc_fast(soc):
    x = min(max(soc, 0.0), 1.0) * 1000.0
    i = int(x)
    if i >= 1000:
        return float(_RSOC_GRID[1000])
    f = x - i
    return float(_RSOC_GRID[i] * (1 - f) + _RSOC_GRID[i + 1] * f)


def _rmult_T(t_c):
    return float(np.interp(t_c, I.w3c.T_GRID, I.w3c.R_MULT[_CELL["chem"]]))


def pack_electrical(p_term_kw, soc_nameplate, r_mult_t):
    """Scalar mirror of WS3 Pack.solve_current (asserted against it in
    run_ws5). p_term_kw > 0 = discharge. Returns (I_cell, q_pack_W, V_bus)."""
    u = _ocv_fast(soc_nameplate)
    r = _R_BASE * r_mult_t * _rsoc_fast(soc_nameplate)
    p_cell = p_term_kw * 1e3 / _NS
    if p_cell > 0.0:
        disc = max(u * u - 4.0 * r * p_cell, 0.0)
        i = (u - math.sqrt(disc)) / (2.0 * r)
    elif p_cell < 0.0:
        disc = u * u + 4.0 * r * (-p_cell)
        i = -(-u + math.sqrt(disc)) / (2.0 * r)
    else:
        i = 0.0
    return i, i * i * r * _NS, (u - i * r) * _NS


# ------------------------------------------------------- traction control
def rear_axle_share(m):
    f = (m - I.VEH.m_curb_operating) / (I.VEH.m_gvw - I.VEH.m_curb_operating)
    f = min(max(f, 0.0), 1.5)
    return I.VEH.rear_axle_share_curb + f * (I.VEH.rear_axle_share_gvw
                                             - I.VEH.rear_axle_share_curb)


def h_cg(m):
    f = (m - I.VEH.m_curb_operating) / (I.VEH.m_gvw - I.VEH.m_curb_operating)
    f = min(max(f, 0.0), 1.5)
    return I.VEH.h_cg_empty + f * (I.VEH.h_cg_loaded - I.VEH.h_cg_empty)


def adhesion_force_N(mu, m, grade=0.0, braking=False):
    """WS2's exported torque-limit law in force form. At grade 0 this
    reproduces WS2 traction.envelope and traction.mu_required exactly
    (asserted in run_ws5). The grade term carries the pitch transfer, so a
    DESCENT unloads the single driven axle and the electric retarder's
    adhesion ceiling falls with it - the fault case's aggravation."""
    theta = math.atan(grade)
    n_static = m * I.G * (rear_axle_share(m) * math.cos(theta)
                          + math.sin(theta) * h_cg(m) / I.VEH.wheelbase)
    n_static = max(n_static, 0.0)
    k = mu * h_cg(m) / I.VEH.wheelbase
    den = (1.0 + k) if braking else (1.0 - k)
    return mu * n_static / den if den > 0 else float("inf")


def mu_required(F_N, m, grade=0.0, braking=False):
    """Inverse of adhesion_force_N. Note the denominators swap under
    inversion: with r = F/N_rear_static, drive gives mu = r/(1 + r.h/L) and
    braking gives mu = r/(1 - r.h/L). Reproduces WS2's exported
    traction.mu_required to machine precision (asserted in run_ws5)."""
    theta = math.atan(grade)
    n_static = m * I.G * (rear_axle_share(m) * math.cos(theta)
                          + math.sin(theta) * h_cg(m) / I.VEH.wheelbase)
    if n_static <= 0:
        return float("inf")
    r = F_N / n_static
    k = h_cg(m) / I.VEH.wheelbase
    den = (1.0 - r * k) if braking else (1.0 + r * k)
    return r / den if den > 0 else float("inf")


def motoring_absorb_kw(engine, derate=1.0, rpm=None):
    """[WS5-PROPOSED, WS4-anchored] Bus power the crank-mounted ISG can dump
    into the engine by motoring it, fuel off, against its own friction and
    pumping work:  P = FMEP(N) . V_d . (N/60) / 2   (four-stroke).
    Evaluated on WS4's own FMEP coefficients, this expression reproduces
    WS4's declared motoring anchor (10.7 kW at 1,706 rpm) - the member is
    theirs, not invented here (asserted in run_ws5). NOT a ruled
    capability: continuous motoring needs WS4 sign-off and a WS7 test."""
    n = float(engine.rated_cont_rpm if rpm is None else rpm)
    p_mech_kw = (float(engine.fmep_bar(n)) * 1e5 * engine.disp_m3
                 * (n / 60.0) / 2.0) / 1e3
    return max(0.0, p_mech_kw * 0.93)      # generator conversion allowance


# --------------------------------------------------------------- config
@dataclass
class Cfg:
    variant: str = "V2"                 # V2 | V1
    strategy: str = "pin"               # pin | two_point | load_follow
    seed: int = 23
    case: str = "nominal"
    label: str = ""
    veh: object = None
    m_kg: float = None
    derate: float = 1.0
    p_aux_kw: float = 2.0
    t_cell_init_C: float = 25.0
    t_amb_C: float = 25.0
    usable_kwh: float = None
    soc_init: float = None              # None -> WS3's 0.55 target
    ser_band: tuple = None              # (lo, hi) usable-SOC fractions
    emerg_band: tuple = (0.25, 0.40)
    mu_est: float = MU_PRIOR_DRY
    v1_fixed_bus_kw: float = None
    # --- WS5 policy layers (ws4_concordance=True disables all of them)
    ws4_concordance: bool = False
    enable_tc: bool = True
    enable_r15_heater: bool = True
    enable_r15_resistor: bool = True
    enable_r16: bool = True
    enable_dispatch_limit: bool = True  # ESC-9 pack power envelope
    enable_reserve: bool = True         # ESC-9 anticipatory genset raise
    enable_coast_policy: bool = True    # R22d
    enable_thermal_model: bool = True
    enable_gen_rate_limit: bool = True
    enable_motor_sink: bool = False     # WS5-PROPOSED ISG motoring retarder
    stop_on_surplus: bool = False       # SENSITIVITY ONLY (not one of the
                                        # three R22b candidates): stop a
                                        # load-following genset instead of
                                        # holding WS4's 25 kW shaft floor
                                        # while the bus is in surplus
    # --- fault injection
    fault: str = None
    fault_t_s: float = 0.0
    # --- exports
    trace: bool = False
    trace_stride: int = 1

    def __post_init__(self):
        if self.veh is None:
            self.veh = I.VEH
        if self.m_kg is None:
            self.m_kg = self.veh.m_gvw
        if self.usable_kwh is None:
            self.usable_kwh = I.USABLE_BUS_KWH
        if self.ser_band is None:
            self.ser_band = (0.35, 0.75)

    def policy(self):
        return dict(ws4_concordance=self.ws4_concordance,
                    tc=self.enable_tc, r15_heater=self.enable_r15_heater,
                    r15_resistor=self.enable_r15_resistor, r16=self.enable_r16,
                    dispatch_limit=self.enable_dispatch_limit,
                    reserve=self.enable_reserve,
                    coast_policy=self.enable_coast_policy,
                    thermal_model=self.enable_thermal_model,
                    gen_rate_limit=self.enable_gen_rate_limit,
                    motor_sink=self.enable_motor_sink,
                    stop_on_surplus=self.stop_on_surplus)


def band_from_kwh(band_kwh, usable_kwh, target=None):
    target = I.SOC_TARGET if target is None else target
    half = 0.5 * band_kwh / usable_kwh
    return (target - half, target + half)


# ----------------------------------------------------------- genset model
class GensetCmd:
    """Set-point generator for the three R22b dispatch candidates and the
    R19 V1 fixed point. Operating points are taken on WS4's best-BSFC
    locus with WS4's own conventions."""

    def __init__(self, engine, gen, derate, fixed_bus_kw=None,
                 pin_bsfc_on_derated_curve=False):
        self.engine, self.gen, self.derate = engine, gen, derate
        # WS4-CONCORDANCE NOTE. WS4's ratified simulator computes the
        # BSFC load fraction phi = T / T_max against the DERATED full-load
        # curve on its locus branches (_bsfc_fast) but against the
        # UNDERATED curve at the pinned point (WillansEngine.bsfc). At
        # derate 1.0 the two agree exactly. At the 2,000 m / +45 C derate
        # they do not, and the pinned point is the optimistic one.
        # pin_bsfc_on_derated_curve=False mirrors WS4 (concordance);
        # True is the consistent treatment WS5 uses for its own answer.
        # The size of the difference is exported (derate_bsfc_consistency).
        self.pin_bsfc_on_derated_curve = pin_bsfc_on_derated_curve
        loc = engine.opt_locus()
        ok = np.isfinite(loc["bsfc"])
        self.loc_p = loc["p_kw"][ok]
        self.loc_rpm = loc["rpm"][ok]
        self.loc_trq = loc["trq"][ok]
        self.p_cont = engine.rated_cont_kw * derate
        self.p_peak = engine.peak_power_kw() * derate * 0.97
        self.pin = self._pinned_point()
        self.fixed_bus_kw = fixed_bus_kw
        if fixed_bus_kw is not None:
            self.pin = self.point_for_bus(fixed_bus_kw)
        # Two-point HIGH notch: the best-BSFC-locus point at the DERATED
        # CONTINUOUS RATING. Declared from the rating, not fitted to the
        # duty, so the trade is not tuned to its own answer.
        self.notch_hi = self.point_for_shaft(self.p_cont)

    def _pack(self, rpm, trq, p_shaft, derated_curve=True):
        tmax = float(self.engine.t_max(rpm)) * (self.derate if derated_curve
                                                else 1.0)
        bsfc = _ws4_bsfc_fast(self.engine, float(rpm), float(trq), tmax)
        p_bus = float(_ws4_gen_elec(self.gen, float(rpm), float(p_shaft)))
        return dict(rpm=float(rpm), trq_Nm=float(trq),
                    p_shaft_kw=float(p_shaft), bsfc=bsfc, p_bus_kw=p_bus,
                    fuel_gps=bsfc * p_shaft / 3600.0,
                    eta_gen=(p_bus / p_shaft) if p_shaft > 0 else 0.0)

    def _pinned_point(self):
        pin = self.engine.min_bsfc_point(p_cap_kw=self.p_cont)
        trq = min(pin["trq_Nm"],
                  float(self.engine.t_max(pin["rpm"])) * self.derate)
        return self._pack(pin["rpm"], trq,
                          trq * pin["rpm"] * 2 * math.pi / 60 / 1e3,
                          derated_curve=self.pin_bsfc_on_derated_curve)

    def point_for_shaft(self, p_shaft_kw, allow_peak=False):
        """WS4's convention: interpolate the locus at a SHAFT target,
        clamp the torque to the derated full-load curve, recompute."""
        cap = self.p_peak if allow_peak else self.p_cont
        p = min(float(p_shaft_kw), cap)
        rpm = float(np.interp(p, self.loc_p, self.loc_rpm))
        trq = min(float(np.interp(p, self.loc_p, self.loc_trq)),
                  float(self.engine.t_max(rpm)) * self.derate)
        return self._pack(rpm, trq, trq * rpm * 2 * math.pi / 60 / 1e3)

    def point_for_bus(self, p_bus_kw, allow_peak=False):
        p_sh = p_bus_kw * GEN_LOSS_ALLOWANCE
        pt = self.point_for_shaft(p_sh, allow_peak)
        for _ in range(4):
            err = pt["p_bus_kw"] - p_bus_kw
            if abs(err) < 1e-9:
                break
            p_sh -= err
            pt = self.point_for_shaft(p_sh, allow_peak)
        return pt


# ------------------------------------------------------------ the run loop
def run(cfg, cyc):
    veh = cfg.veh
    m = cfg.m_kg
    t = np.asarray(cyc["t"], float)
    v = np.asarray(cyc["v"], float)
    grade = np.asarray(cyc["grade"], float) * np.ones_like(v)
    dt = float(np.median(np.diff(t)))
    n = v.size
    conc = cfg.ws4_concordance

    p_wheel = I.vph.wheel_power(t, v, grade, m, lam=veh.lam_rot,
                                veh=veh)["P_wheel"] / 1e3      # kW

    engine = I.ENG_V2 if cfg.variant == "V2" else I.ENG_V1
    gen = I.GEN_V2 if cfg.variant == "V2" else I.GEN_V1
    G = GensetCmd(engine, gen, cfg.derate, cfg.v1_fixed_bus_kw,
                  pin_bsfc_on_derated_curve=(not conc))
    pin = G.pin
    motor_sink_kw = motoring_absorb_kw(engine, cfg.derate)
    p_follow_floor_bus = G.point_for_shaft(P_MIN_FOLLOW_KW)["p_bus_kw"]

    # ---------------- precomputed per-sample vectors ----------------------
    rpm_motor = v / veh.r_dyn * I.MOTOR_RATIO * 60.0 / (2 * np.pi)
    blend = np.clip((v - SM.V_REGEN_BLEND_LO)
                    / (SM.V_REGEN_BLEND_HI - SM.V_REGEN_BLEND_LO), 0.0, 1.0)
    p_brk_demand = np.clip(-p_wheel, 0.0, None)
    p_drive_demand = np.clip(p_wheel, 0.0, None)

    if cfg.enable_tc and not conc:
        _th = np.arctan(grade)
        _hl = h_cg(m) / I.VEH.wheelbase
        _n = np.maximum(m * I.G * (rear_axle_share(m) * np.cos(_th)
                                   + np.sin(_th) * _hl), 0.0)
        _k = cfg.mu_est * _hl
        p_adh_drive = cfg.mu_est * _n / (1.0 - _k) * v / 1e3
        p_adh_brake = cfg.mu_est * _n / (1.0 + _k) * v / 1e3
        p_drive_cmd = np.minimum(p_drive_demand, p_adh_drive)
        tc_drive_lim = p_drive_demand > p_adh_drive + 1e-9
        p_capt_adh = np.minimum(p_brk_demand, p_adh_brake)
        tc_regen_lim = p_brk_demand > p_adh_brake + 1e-9
    else:
        p_drive_cmd = p_drive_demand
        tc_drive_lim = np.zeros(n, bool)
        p_capt_adh = p_brk_demand
        tc_regen_lim = np.zeros(n, bool)

    if conc:
        p_capt0 = np.minimum(p_brk_demand, REGEN_CAP_WHEEL_KW) * blend
    else:
        w_motor = np.maximum(rpm_motor * 2 * np.pi / 60.0, 1e-6)
        p_motor_env = I.motor_peak_torque(rpm_motor) * w_motor / 1e3 * ETA_RED
        p_capt0 = np.minimum(np.minimum(p_capt_adh, REGEN_CAP_WHEEL_KW),
                             p_motor_env) * blend

    eta_rg = I.CHAIN.eta_wheel_to_bus(v, p_capt0)
    eta_tr = I.CHAIN.eta_bus_to_wheel(v, p_drive_cmd)
    coast_shaft_kw = I.COAST_DRAG_SHAFT_W_85 / 1e3 * (v / (85.0 / 3.6))
    coast_bus_kw = I.COAST_DRAG_BUS_W_85 / 1e3 * (v / (85.0 / 3.6))
    dist_cum = np.concatenate(([0.0], np.cumsum(0.5 * (v[1:] + v[:-1])
                                                * np.diff(t)))) / 1e3

    # ------------------------------- state ---------------------------------
    sm = SM.SupervisorStateMachine()
    e_cap = cfg.usable_kwh * 3.6e6
    soc_ref = I.SOC_TARGET if cfg.soc_init is None else float(cfg.soc_init)
    e = e_cap * soc_ref
    ser_lo, ser_hi = cfg.ser_band
    em_lo, em_hi = cfg.emerg_band
    ser_on = emerg = eng_prev = notch_hi_on = False
    p_gen_prev = setpoint_prev = 0.0
    ramp_left = 0.0
    fuel_g = 0.0
    starts = 0
    t_cell = cfg.t_cell_init_C
    r_mult_t = _rmult_T(t_cell)
    t_cool_lt = min(T_COOLANT_LT_MAX_C, cfg.t_amb_C + LT_RISE_K)
    tj = t_cool_lt
    v_bus = _ocv_fast(I.soc_usable_to_nameplate(soc_ref)) * _NS
    dem_lp = res_lp = 0.0
    fault_active = None
    dstate_prev = "D_OFF"
    above_pin_prev = False
    soc_min = soc_max = soc_ref
    t_first_unserved = None
    dist_first_unserved = None

    A = {k: 0.0 for k in (
        "e_fric_kwh", "e_res_kwh", "e_htr_kwh", "e_pack_chg_kwh",
        "e_regen_bus_kwh", "e_chain_loss_kwh", "e_gen_loss_kwh", "eng_kwh",
        "eng_on_s", "eng_reject_kwh", "e_bus_kwh", "unserved_kwh", "emerg_s",
        "over_rating_s", "eng_stops", "above_pin_demand_s",
        "above_pin_demand_kwh", "above_pin_engine_s", "above_pin_transitions",
        "setpoint_transitions", "dispatch_state_changes", "pack_chg_peak_kw",
        "pack_dis_peak_kw", "pack_chg_over_r8_110kW_s",
        "pack_dis_over_r8_125kW_s", "regen_bus_peak_kw", "regen_shed_r16_kwh",
        "dispatch_limit_clip_s", "dispatch_limit_shed_kwh", "reserve_s",
        "reserve_energy_kwh", "coast_no_regen_s", "coast_spin_shaft_kwh",
        "coast_spin_bus_kwh", "coast_recovered_bus_kwh",
        "coast_band_s", "coast_band_spin_shaft_kwh",
        "coast_band_spin_bus_kwh", "coast_band_recovered_bus_kwh",
        "tc_drive_limited_s", "tc_regen_limited_s", "tc_drive_shed_kwh",
        "tc_regen_shed_kwh", "precond_s", "precond_kwh", "heater_s",
        "resistor_s", "friction_s", "res_peak_kw", "blower_kwh",
        "pack_heat_kwh", "motor_sink_kwh", "motor_sink_s", "halt_s", "limp_s",
        "thermal_drive_shed_kwh", "unserved_wheel_kwh",
        "unserved_wheel_bus_kwh", "unserved_wheel_s",
        "fric_peak_kw", "dpdt_abs_sum", "dpdt_n", "regen_bus_kwh_to_pack",
        "pack_chg_peak_kw_actual", "regen_to_pack_peak_kw",
        "pack_chg_over_r16_accept_s", "pack_chg_over_r16_accept_kwh",
        "nvh_events")}
    nvh_prev = False
    A["tj_peak_C"] = tj
    A["t_coolant_lt_C"] = t_cool_lt
    A["t_cell_peak_C"] = t_cell
    A["t_cell_min_C"] = t_cell
    A["v_bus_min_V"] = v_bus
    A["v_bus_max_V"] = v_bus

    dpdt_arr = np.zeros(n)
    tr = [] if cfg.trace else None
    fuel_cum_g = 0.0
    # cumulative elevation: dz = grade * ds along the same trapezoid the
    # distance integral uses, so z_m and x_m are consistent by construction
    # dist_cum is in km; ds in metres is 1e3 * diff(dist_cum)
    z_cum = np.concatenate(([0.0], np.cumsum(
        0.5 * (grade[1:] + grade[:-1]) * np.diff(dist_cum) * 1e3)))

    for i in range(n):
        ti = float(t[i])
        pw = float(p_wheel[i])
        vi = float(v[i])
        soc_u = e / e_cap
        soc_np = I.soc_usable_to_nameplate(soc_u)

        if cfg.fault is not None and ti >= cfg.fault_t_s:
            fault_active = cfg.fault
        gen_ok = fault_active != "genset_loss"
        pack_ok = fault_active != "pack_loss"
        res_ok = fault_active != "resistor_loss"

        # ---------------- pack dispatch envelope (ESC-9) -----------------
        if not pack_ok:
            dis_cap = chg_cap = 0.0
        elif cfg.enable_dispatch_limit and not conc:
            dis_cap = I.pack_dis_cap_kw(t_cell, soc_u)
            chg_cap = I.pack_chg_cap_kw(t_cell, soc_u)
        else:
            dis_cap = chg_cap = float("inf")
        if fault_active == "pack_derate":
            dis_cap = min(dis_cap, 0.5 * I.R8_DIS_BUS_KW)
            chg_cap = min(chg_cap, 0.5 * I.R8_CHG_BUS_KW)

        p_bus_load = cfg.p_aux_kw
        p_fric_wheel = 0.0
        p_res = p_htr = p_motor_sink = p_regen_bus = 0.0
        p_motor_mech = p_motor_bus = p_pack_trace = 0.0
        trip_limited = 0.0
        blend_stage = "B_NONE"

        derate_tj = 1.0
        if cfg.enable_thermal_model and not conc:
            if tj >= SM.INV_TJ_TRIP_C:
                derate_tj = 0.0
            elif tj >= SM.INV_TJ_DERATE_C:
                derate_tj = max(0.0, 1.0 - (tj - SM.INV_TJ_DERATE_C)
                                / (SM.INV_TJ_TRIP_C - SM.INV_TJ_DERATE_C))
        if fault_active == "inverter_thermal":
            derate_tj = min(derate_tj, 0.60)

        if pw > 0.0:
            p_adh_cmd = float(p_drive_cmd[i])
            p_cmd = p_adh_cmd * derate_tj
            eta_c = float(eta_tr[i])
            p_bus_load += p_cmd / eta_c
            p_motor_mech = p_cmd
            p_motor_bus = p_cmd / eta_c
            A["e_chain_loss_kwh"] += p_cmd * (1 / eta_c - 1) * dt / 3600.0
            # Wheel work the supervisor could NOT deliver is a capability
            # shortfall, not a saving: it is booked here and charged to
            # fuel in the roll-up, exactly as unserved bus energy is.
            if p_adh_cmd < pw - 1e-12:
                A["tc_drive_shed_kwh"] += (pw - p_adh_cmd) * dt / 3600.0
            if p_cmd < p_adh_cmd - 1e-12:
                A["thermal_drive_shed_kwh"] += (p_adh_cmd - p_cmd) \
                    * dt / 3600.0
            if p_cmd < pw - 1e-12:
                trip_limited = 1.0
                A["unserved_wheel_kwh"] += (pw - p_cmd) * dt / 3600.0
                A["unserved_wheel_bus_kwh"] += (pw - p_cmd) / eta_c \
                    * dt / 3600.0
                A["unserved_wheel_s"] += dt
            if tc_drive_lim[i]:
                A["tc_drive_limited_s"] += dt
            if pw / ETA_RED > MOTOR_RATED_KW:
                A["over_rating_s"] += dt
        elif pw < 0.0:
            p_capt = float(p_capt0[i]) * derate_tj
            if tc_regen_lim[i]:
                A["tc_regen_limited_s"] += dt
                A["tc_regen_shed_kwh"] += (float(p_brk_demand[i])
                                           - float(p_capt_adh[i])) * dt / 3600.0
            p_regen_bus = p_capt * float(eta_rg[i])
            p_motor_mech = -p_capt
            p_motor_bus = -p_regen_bus
            p_fric_wheel = float(p_brk_demand[i]) - p_capt
            if p_capt / ETA_RED > MOTOR_RATED_KW:
                A["over_rating_s"] += dt

        # ---------------- R15 blend cascade (bus-side) --------------------
        if p_regen_bus > 0.0:
            A["regen_bus_peak_kw"] = max(A["regen_bus_peak_kw"], p_regen_bus)
            A["e_regen_bus_kwh"] += p_regen_bus * dt / 3600.0
            remaining = p_regen_bus
            head_rate = max(0.0, (e_cap - e)) / dt / 1e3 / BATT_ETA_CHG
            allow = max(0.0, head_rate - cfg.p_aux_kw)
            if cfg.enable_r16:
                t_ref = t_cell if not conc else cfg.t_cell_init_C
                allow_r16 = min(allow, I.r16_accept_kw(t_ref))
            else:
                allow_r16 = allow
            A["regen_shed_r16_kwh"] += (min(remaining, allow)
                                        - min(remaining, allow_r16)) \
                * dt / 3600.0
            allow = min(allow_r16, chg_cap)
            p_pack = min(remaining, max(allow, 0.0))
            if p_pack > 0:
                blend_stage = "B_PACK"
            remaining -= p_pack
            if (remaining > 0 and cfg.enable_r15_heater and not conc
                    and t_cell <= SM.R16_BAND_HI_C):
                p_htr = min(remaining, I.HEATER_KW)
                if p_htr > 0:
                    blend_stage = "B_HEATER"
                remaining -= p_htr
            if remaining > 0 and cfg.enable_r15_resistor and res_ok \
                    and not conc:
                res_avail = min(v_bus * v_bus / I.RES_OHM / 1e3,
                                I.RES_CEILING_KW)
                p_res = min(remaining, res_avail)
                if p_res > 0:
                    blend_stage = "B_RESISTOR"
                    A["res_peak_kw"] = max(A["res_peak_kw"], p_res)
                remaining -= p_res
            if remaining > 0 and cfg.enable_motor_sink and gen_ok and not conc:
                p_motor_sink = min(remaining, motor_sink_kw)
                if p_motor_sink > 0:
                    A["motor_sink_s"] += dt
                    A["motor_sink_kwh"] += p_motor_sink * dt / 3600.0
                remaining -= p_motor_sink
            if remaining > 1e-12:
                blend_stage = "B_FRICTION"
                back = remaining / float(eta_rg[i]) if eta_rg[i] > 0 else 0.0
                p_fric_wheel += back
            p_regen_used = p_regen_bus - max(remaining, 0.0)
            p_bus_load -= p_regen_used
            p_pack_trace = p_pack
            A["e_pack_chg_kwh"] += p_pack * dt / 3600.0
            A["regen_bus_kwh_to_pack"] += p_pack * dt / 3600.0
            A["regen_to_pack_peak_kw"] = max(A["regen_to_pack_peak_kw"],
                                             p_pack)
            A["e_htr_kwh"] += p_htr * dt / 3600.0
            A["e_res_kwh"] += p_res * dt / 3600.0
            if p_res > 0:
                A["resistor_s"] += dt
                A["blower_kwh"] += I.BLOWER_KW * dt / 3600.0
                p_bus_load += I.BLOWER_KW
            if p_htr > 0:
                A["heater_s"] += dt
            if eta_rg[i] > 0:
                A["e_chain_loss_kwh"] += p_regen_used * (1 - eta_rg[i]) \
                    / eta_rg[i] * dt / 3600.0
        if p_fric_wheel > 1e-12:
            A["friction_s"] += dt
            A["fric_peak_kw"] = max(A["fric_peak_kw"], p_fric_wheel)
        A["e_fric_kwh"] += p_fric_wheel * dt / 3600.0

        # ---------------- R16 preconditioning (cold) ---------------------
        if cfg.enable_r16 and not conc and t_cell < SM.R16_PRECOND_C \
                and p_htr <= 0.0:
            share = 1.0 if p_bus_load < I.MOTOR_S1_KW else 0.35
            p_pc = I.HEATER_KW * share
            p_bus_load += p_pc
            A["precond_s"] += dt
            A["precond_kwh"] += p_pc * dt / 3600.0
            p_htr += p_pc

        # ---------------- dispatch (R19 / R22b / ESC-9) -------------------
        dem_lp += (max(p_bus_load, 0.0) - dem_lp) * dt / TAU_DEMAND_S
        res_lp += (max(p_bus_load, 0.0) - res_lp) * dt / TAU_RESERVE_S
        if e < ser_lo * e_cap:
            ser_on = True
        elif e > ser_hi * e_cap:
            ser_on = False
        if e < em_lo * e_cap:
            emerg = True
        elif e > em_hi * e_cap:
            emerg = False

        reserve_deficit = 0.0
        if cfg.enable_reserve and not conc and pack_ok and gen_ok:
            reserve_deficit = max(0.0, res_lp - (dis_cap - RESERVE_MARGIN_KW))

        if not gen_ok:
            d_cmd = "D_OFF"
        elif emerg:
            d_cmd = "D_FOLLOW"
        elif cfg.strategy == "load_follow" and ser_on:
            if (cfg.stop_on_surplus and dem_lp < p_follow_floor_bus
                    and soc_u > I.SOC_TARGET):
                d_cmd = "D_OFF"
            else:
                d_cmd = "D_FOLLOW"
        elif reserve_deficit > 0.0 and cfg.strategy != "load_follow":
            d_cmd = "D_RESERVE"
        elif ser_on:
            if cfg.strategy == "two_point":
                if dem_lp > pin["p_bus_kw"] + NOTCH_UP_KW:
                    notch_hi_on = True
                elif dem_lp < pin["p_bus_kw"] - NOTCH_DN_KW:
                    notch_hi_on = False
                d_cmd = "D_NOTCH_HI" if notch_hi_on else "D_PIN"
            else:
                d_cmd = "D_PIN"
        else:
            d_cmd = "D_OFF"
        eng_running = d_cmd != "D_OFF"
        if eng_running and not eng_prev:
            d_cmd_sm = "D_START"
            ramp_left = P_START_RAMP_S if (cfg.enable_gen_rate_limit
                                           and not conc) else 0.0
        else:
            d_cmd_sm = d_cmd

        # commanded operating point (WS4 shaft-target conventions)
        if not eng_running:
            pt = None
        elif emerg:
            trim = (em_hi * e_cap - e) / 120.0 / 1e3
            p_sh = min(G.p_peak, max(pin["p_shaft_kw"],
                                     (max(p_bus_load, 0.0) + trim)
                                     * GEN_LOSS_ALLOWANCE))
            pt = G.point_for_shaft(p_sh, allow_peak=True)
            A["emerg_s"] += dt
        elif cfg.strategy == "load_follow":
            trim = (soc_ref - soc_u) * e_cap / 240.0 / 1e3
            p_sh = min(max(P_MIN_FOLLOW_KW,
                           (max(p_bus_load, 0.0) + trim) * GEN_LOSS_ALLOWANCE),
                       G.p_cont)
            pt = G.point_for_shaft(p_sh)
        elif d_cmd == "D_RESERVE":
            p_sh = min(max(pin["p_shaft_kw"],
                           (res_lp + RESERVE_MARGIN_KW) * GEN_LOSS_ALLOWANCE),
                       G.p_cont)
            pt = G.point_for_shaft(p_sh)
        elif d_cmd == "D_NOTCH_HI":
            pt = G.notch_hi
        else:
            pt = pin

        p_gen_elec = p_shaft_eng = f_gps = 0.0
        eng_rpm = eng_trq = 0.0
        if pt is not None:
            p_target = pt["p_bus_kw"]
            if cfg.enable_gen_rate_limit and not conc:
                if ramp_left > 0.0:
                    frac = max(0.0, 1.0 - ramp_left / P_START_RAMP_S)
                    p_target = min(p_target, pt["p_bus_kw"] * frac)
                    ramp_left = max(0.0, ramp_left - dt)
                dmax = GEN_RATE_KW_PER_S * dt
                p_target = min(max(p_target, p_gen_prev - dmax),
                               p_gen_prev + dmax)
            if p_target < pt["p_bus_kw"] - 1e-9:
                pt_eff = G.point_for_bus(max(p_target, 0.5),
                                         allow_peak=emerg)
            else:
                pt_eff = pt
            p_gen_elec = pt_eff["p_bus_kw"]
            p_shaft_eng = pt_eff["p_shaft_kw"]
            f_gps = pt_eff["fuel_gps"]
            eng_rpm = pt_eff["rpm"]
            eng_trq = pt_eff["trq_Nm"]
            A["eng_reject_kwh"] += (f_gps * LHV - p_shaft_eng) * dt / 3600.0
            A["e_gen_loss_kwh"] += (p_shaft_eng - p_gen_elec) * dt / 3600.0

        dpdt = abs(p_gen_elec - p_gen_prev) / dt
        dpdt_arr[i] = dpdt
        A["dpdt_abs_sum"] += dpdt
        A["dpdt_n"] += 1.0
        nvh_now = dpdt > NVH_DPDT_THRESHOLD_KW_PER_S
        if nvh_now and not nvh_prev:
            A["nvh_events"] += 1.0
        nvh_prev = nvh_now
        if abs(p_gen_elec - setpoint_prev) > SM.SETPOINT_DEADBAND_KW:
            A["setpoint_transitions"] += 1.0
            setpoint_prev = p_gen_elec
        p_gen_prev = p_gen_elec

        # ---------------- bus balance / buffer ---------------------------
        p_batt = p_gen_elec - p_bus_load        # + = charge
        p_batt_raw = p_batt
        if p_batt < 0.0 and -p_batt > dis_cap:
            trip_limited = 1.0
            A["unserved_kwh"] += (-p_batt - dis_cap) * dt / 3600.0
            A["dispatch_limit_clip_s"] += dt
            p_batt = -dis_cap
            if t_first_unserved is None:
                t_first_unserved = ti
                dist_first_unserved = float(dist_cum[i])
        if p_batt > 0.0 and p_batt > chg_cap:
            A["dispatch_limit_shed_kwh"] += (p_batt - chg_cap) * dt / 3600.0
            p_batt = chg_cap
        if reserve_deficit > 0.0:
            A["reserve_s"] += dt
            A["reserve_energy_kwh"] += reserve_deficit * dt / 3600.0

        if p_batt >= 0.0:
            de = p_batt * 1e3 * BATT_ETA_CHG * dt
            if e + de > e_cap:
                de = e_cap - e
            e += de
        else:
            de = p_batt * 1e3 / BATT_ETA_DIS * dt
            if e + de < 0.0:
                A["unserved_kwh"] += -(e + de) * BATT_ETA_DIS / 3.6e6
                if t_first_unserved is None:
                    t_first_unserved = ti
                    dist_first_unserved = float(dist_cum[i])
                de = -e
            e += de

        fuel_g += f_gps * dt
        if eng_running and not eng_prev:
            starts += 1
            fuel_g += START_FUEL_G
        if eng_prev and not eng_running:
            A["eng_stops"] += 1.0
        eng_prev = eng_running

        A["eng_kwh"] += p_shaft_eng * dt / 3600.0
        A["eng_on_s"] += dt if eng_running else 0.0
        A["e_bus_kwh"] += max(0.0, p_bus_load) * dt / 3600.0

        if p_bus_load > pin["p_bus_kw"]:
            A["above_pin_demand_s"] += dt
            A["above_pin_demand_kwh"] += (p_bus_load - pin["p_bus_kw"]) \
                * dt / 3600.0
        ap_now = p_shaft_eng > pin["p_shaft_kw"] + 1e-9
        if ap_now:
            A["above_pin_engine_s"] += dt
        if ap_now != above_pin_prev:
            A["above_pin_transitions"] += 1.0
        above_pin_prev = ap_now
        if p_batt_raw >= 0.0:
            A["pack_chg_peak_kw"] = max(A["pack_chg_peak_kw"], p_batt_raw)
            if p_batt_raw > I.R8_CHG_BUS_KW:
                A["pack_chg_over_r8_110kW_s"] += dt
        if p_batt > 0.0:
            A["pack_chg_peak_kw_actual"] = max(A["pack_chg_peak_kw_actual"],
                                               p_batt)
            _acc_now = I.r16_accept_kw(t_cell)
            if p_batt > _acc_now:
                A["pack_chg_over_r16_accept_s"] += dt
                A["pack_chg_over_r16_accept_kwh"] += (p_batt - _acc_now) \
                    * dt / 3600.0
        else:
            A["pack_dis_peak_kw"] = max(A["pack_dis_peak_kw"], -p_batt_raw)
            if -p_batt_raw > I.R8_DIS_BUS_KW:
                A["pack_dis_over_r8_125kW_s"] += dt

        # (a) WS4's exact true-coast test, kept verbatim for comparability
        true_coast = (vi > 1.0 / 3.6 and pw <= 0.0
                      and float(p_capt0[i]) <= 1e-9)
        if true_coast:
            A["coast_no_regen_s"] += dt
            A["coast_spin_shaft_kwh"] += float(coast_shaft_kw[i]) * dt / 3600.0
            A["coast_spin_bus_kwh"] += float(coast_bus_kw[i]) * dt / 3600.0
        # (b) WS5's zero-torque band: the machine is at essentially zero
        # torque whenever the wheel demand is within a small multiple of
        # the PM drag itself. This is the set of samples R22d is about;
        # WS4's test only catches those where the demand is exactly
        # non-positive AND the regen blend-out has already zeroed capture,
        # which on a road-load-neutral coast is a measure-zero condition.
        drag_band = COAST_BAND_FACTOR * float(coast_shaft_kw[i])
        if vi > 1.0 / 3.6 and abs(pw) <= drag_band:
            A["coast_band_s"] += dt
            A["coast_band_spin_shaft_kwh"] += float(coast_shaft_kw[i]) \
                * dt / 3600.0
            A["coast_band_spin_bus_kwh"] += float(coast_bus_kw[i]) \
                * dt / 3600.0
            if cfg.enable_coast_policy and not conc:
                rec = (float(coast_shaft_kw[i]) * float(eta_rg[i])
                       + float(coast_bus_kw[i]))
                A["coast_band_recovered_bus_kwh"] += rec * dt / 3600.0
                A["coast_recovered_bus_kwh"] += rec * dt / 3600.0

        if cfg.enable_thermal_model and not conc:
            _, q_pack_w, v_bus_new = pack_electrical(-p_batt, soc_np, r_mult_t)
            v_bus = min(max(v_bus_new, I.BUS_MIN_V), I.BUS_TRANSIENT_V)
            A["v_bus_min_V"] = min(A["v_bus_min_V"], v_bus)
            A["v_bus_max_V"] = max(A["v_bus_max_V"], v_bus)
            A["pack_heat_kwh"] += q_pack_w / 1e3 * dt / 3600.0
            t_cell = I.PACK.thermal_step(t_cell, q_pack_w, cfg.t_amb_C, dt,
                                         cooling=True, heater_w=p_htr * 1e3)
            r_mult_t = _rmult_T(t_cell)
            A["t_cell_peak_C"] = max(A["t_cell_peak_C"], t_cell)
            A["t_cell_min_C"] = min(A["t_cell_min_C"], t_cell)
            if pw > 0:
                p_chain_loss = pw * (1 / max(float(eta_tr[i]), 1e-3) - 1)
            else:
                p_chain_loss = p_regen_bus * (1 - float(eta_rg[i])) \
                    / max(float(eta_rg[i]), 1e-3)
            tj += (t_cool_lt + TJ_K_PER_KW * max(p_chain_loss, 0.0)
                   - tj) * dt / TJ_TAU_S
            A["tj_peak_C"] = max(A["tj_peak_C"], tj)

        halt = (fault_active in ("genset_loss", "pack_loss")
                and t_first_unserved is not None)
        ctx = dict(fault=fault_active, t_cell_C=t_cell, tj_inv_C=tj,
                   tc_drive_limited=bool(tc_drive_lim[i]),
                   tc_regen_limited=bool(tc_regen_lim[i]),
                   d_cmd=d_cmd_sm, blend_stage=blend_stage, halt=halt,
                   v_ms=vi, p_wheel_kw=pw, motor_sink_cmd=p_motor_sink > 0.0)
        st = sm.step(ctx)
        if st["DISPATCH"] != dstate_prev:
            A["dispatch_state_changes"] += 1.0
            dstate_prev = st["DISPATCH"]
        if st["VEHICLE"] == "V_LIMP":
            A["limp_s"] += dt
        elif st["VEHICLE"] == "V_HALT":
            A["halt_s"] += dt

        soc_u = e / e_cap
        soc_min = min(soc_min, soc_u)
        soc_max = max(soc_max, soc_u)

        fuel_cum_g += f_gps * dt
        if tr is not None and (i % cfg.trace_stride == 0):
            # TRACE_SCHEMA engine_state: 0 off / 1 idle / 2 loaded /
            # 3 overrun. A pure-series engine is never driven by the road,
            # so state 3 (overrun) cannot occur and never appears.
            eng_state = (0.0 if not eng_running
                         else 2.0 if p_shaft_eng > 1e-9 else 1.0)
            # TRACE_SCHEMA genset_state: 0 off / 1 warm-up / 2 pinned /
            # 3 above-pin. "warm-up" is WS5's load-acceptance ramp.
            gen_state = (0.0 if not eng_running
                         else 1.0 if ramp_left > 0.0
                         else 3.0 if p_shaft_eng > pin["p_shaft_kw"] + 1e-9
                         else 2.0)
            tr.append((ti, float(dist_cum[i]) * 1e3, vi * 3.6,
                       float(grade[i]) * 100.0, float(z_cum[i]), pw,
                       f_gps, fuel_cum_g, p_fric_wheel, trip_limited,
                       eng_rpm, eng_trq, p_shaft_eng, eng_state,
                       p_gen_elec, p_bus_load, p_motor_bus, p_motor_mech,
                       p_pack_trace, p_htr, p_res, soc_u * 100.0, t_cell,
                       gen_state, p_batt, tj, v_bus, dis_cap, chg_cap,
                       st["DISPATCH"], st["BLEND"], st["VEHICLE"],
                       st["THERMAL"], st["TRACTION"], st["FAULT"]))

    # -------------------------------- corrections & rollup ----------------
    drift_kwh = (e - e_cap * soc_ref) / 3.6e6
    if drift_kwh < 0:
        corr_g = (-drift_kwh) / BATT_ETA_CHG / pin["eta_gen"] * pin["bsfc"]
    else:
        corr_g = -drift_kwh * BATT_ETA_DIS / pin["eta_gen"] * pin["bsfc"]
    corr_uns_g = A["unserved_kwh"] / (BATT_ETA_CHG * BATT_ETA_DIS
                                      * pin["eta_gen"]) * pin["bsfc"]
    # unserved WHEEL work (adhesion-limited or thermally derated torque the
    # supervisor could not deliver) is charged on the same marginal
    # buffered-series basis, referred to the bus through the R12 chain
    corr_uw_g = A["unserved_wheel_bus_kwh"] / (BATT_ETA_CHG * BATT_ETA_DIS
                                               * pin["eta_gen"]) * pin["bsfc"]
    fuel_corr_g = fuel_g + corr_g + corr_uns_g + corr_uw_g

    dur = float(t[-1] - t[0])
    dist_km = float(I.vph.trapz(v, t)) / 1e3
    hours = dur / 3600.0
    out = dict(A)
    out.update(
        strategy=cfg.strategy, variant=cfg.variant, case=cfg.case,
        label=cfg.label, seed=cfg.seed, fault=cfg.fault,
        fuel_g=fuel_g, fuel_corrected_g=fuel_corr_g, soc_drift_kwh=drift_kwh,
        fuel_corr_soc_drift_g=corr_g, fuel_corr_unserved_bus_g=corr_uns_g,
        fuel_corr_unserved_wheel_g=corr_uw_g,
        fuel_energy_kWh=fuel_corr_g * LHV / 3600.0,
        fuel_l=fuel_corr_g / DENSITY_G_PER_L,
        distance_km=dist_km, duration_s=dur,
        genset_starts=starts, genset_stops=A["eng_stops"],
        genset_starts_per_h=starts / hours,
        genset_starts_per_8h_shift=starts / hours * 8.0,
        genset_on_frac=A["eng_on_s"] / dur,
        soc_init=soc_ref, soc_min=soc_min, soc_max=soc_max,
        soc_end=e / e_cap,
        above_pin_transitions_per_h=A["above_pin_transitions"] / hours,
        setpoint_transitions_per_h=A["setpoint_transitions"] / hours,
        dispatch_state_changes_per_h=A["dispatch_state_changes"] / hours,
        dpdt_mean_kW_per_s=A["dpdt_abs_sum"] / max(A["dpdt_n"], 1.0),
        dpdt_p95_kW_per_s=float(np.percentile(dpdt_arr, 95)),
        dpdt_max_kW_per_s=float(np.max(dpdt_arr)),
        nvh_events_per_h=A["nvh_events"] / hours,
        pinned_point=pin, notch_hi_point=G.notch_hi,
        motor_sink_available_kW=motor_sink_kw,
        t_first_unserved_s=t_first_unserved,
        dist_first_unserved_km=dist_first_unserved,
        state_counts={r: dict(sm.counts[r]) for r in sm.counts},
        state_transitions=dict(sm.transitions_taken),
        ambiguous_samples=sm.ambiguous_samples,
        policy=cfg.policy(),
    )
    out["fuel_energy_kWh_per_km"] = out["fuel_energy_kWh"] / dist_km
    out["fuel_energy_kWh_per_payload_tonne_km"] = (
        out["fuel_energy_kWh_per_km"] / (I.VEH.m_payload_at_gvw / 1000.0))
    out["l_per_100km"] = out["fuel_l"] / dist_km * 100.0
    out["mean_bsfc_eff_g_per_kWh"] = (fuel_corr_g / A["eng_kwh"]
                                      if A["eng_kwh"] > 0 else float("inf"))
    out["fric_mean_kw"] = A["e_fric_kwh"] * 3600.0 / dur
    out["res_mean_kw"] = A["e_res_kwh"] * 3600.0 / dur
    if tr is not None:
        out["trace"] = tr
    return out


# TRACE_SCHEMA (lead-issued 2026-08-31) core + electrified columns first,
# in the schema's own names, then the WS5-specific extras. Quantities this
# architecture does not have (gear, lockup, motor_disconnect,
# P_comp_brake_kW) and one it does not model (T_motor_C) are ABSENT
# columns, never zero-filled - the schema's rule, and the honest reading.
TRACE_COLUMNS = ["t_s", "x_m", "v_kmh", "grade_pct", "z_m", "P_wheel_kW",
                 "fuel_g_per_s", "fuel_cum_g", "P_friction_brake_kW",
                 "trip_time_flag",
                 "N_eng_rpm", "T_eng_Nm", "P_shaft_eng_kW", "engine_state",
                 "P_gen_bus_kW", "P_bus_load_kW", "P_motor_bus_kW",
                 "P_motor_mech_kW", "P_regen_pack_kW", "P_heater_kW",
                 "P_resistor_kW", "soc_pct", "T_pack_C", "genset_state",
                 "P_batt_bus_kW", "Tj_inv_C", "V_bus_V", "P_dis_cap_kW",
                 "P_chg_cap_kW", "state_DISPATCH", "state_BLEND",
                 "state_VEHICLE", "state_THERMAL", "state_TRACTION",
                 "state_FAULT"]
