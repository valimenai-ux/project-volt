"""
Project Volt - WS8
The five architectures (assignment Tasks 2 and 3).

  S0  conventional 13 L diesel + 12-speed AMT, direct top      (the ruler)
  S1  pure series - Vehicle Zero's architecture scaled
  S2  single cruise-ratio + torque-fill, traction machine DISCONNECTED
      outside the lockup band
  S3  tandem split - diesel axle on ONE fixed ratio, no gearbox anywhere,
      plus a disconnectable e-axle
  S4  range-extended BEV - large pack + sustainer genset

GCW IS FIXED AT 36,300 kg FOR EVERY CANDIDATE (assignment, Task 3). That
has a consequence worth stating plainly because it shapes the whole
trial: the ROAD-LOAD physics is identical for all five. Powertrain mass
does not change how the truck drives - it changes what the truck may
carry. So every kilogram of powertrain is paid for in the DENOMINATOR of
the metric of record, fuel energy per payload tonne-km, and nowhere else.

CONTROL POLICIES are declared, not tuned to taste. Each candidate's
policy is written in its class docstring, and the report states it.
"""
import numpy as np

from ws8_params import (VEH, ADH, AUX, DL, ML, G, LHV_KJ_PER_G,
                        DIESEL_DENSITY_KG_PER_L)
from ws8_physics import road_load_force
import ws8_engine as EN
import ws8_electric as EL


# =====================================================================
#  shared helpers
# =====================================================================
FRICTION_BRAKE_CONT_ALLOWANCE_KW = 60.0
"""Continuous service-brake dissipation a prudent driver will accept on a
sustained descent [kW]. [WS8-PROV] Foundation brakes on a Class 8 are a
STOPPING device, not a holding device; holding a 36 t combination down a
long grade on the service brakes is how trucks arrive at the bottom with
no brakes at all. 60 kW is a snub-braking allowance, not a rating. It is
applied identically to every candidate, so it cannot decide the trial;
what it does is force each candidate to descend at the speed ITS OWN
retarding capability supports, which is a real architectural difference
and is priced here rather than hidden in an unlimited friction brake."""

V_GRID_ENV = np.arange(0.0, 36.05, 0.05)

# Low-speed regen blend-out, carried from WS1's ratified control
# constants (volt_params.Control.v_regen_blend_lo/hi = 3 / 8 km/h):
# below ~8 km/h back-EMF and controllability collapse and the service
# brakes must take over. Applied to every electric path identically.
V_REGEN_BLEND_LO = 3.0 / 3.6
V_REGEN_BLEND_HI = 8.0 / 3.6


def regen_blend(v):
    return float(np.clip((v - V_REGEN_BLEND_LO)
                         / (V_REGEN_BLEND_HI - V_REGEN_BLEND_LO), 0.0, 1.0))


class Ctx:
    """Corner conditions. One object per (corner) so every candidate sees
    exactly the same environment."""

    def __init__(self, name, rho_air=None, t_amb_c=20.0, aux_bus_kw=None,
                 aux_mech_kw=None, payload_factor=1.0, cold=False,
                 grade_heavy=False, label=""):
        self.name = name
        self.rho_air = VEH.rho_air if rho_air is None else rho_air
        self.t_amb_c = t_amb_c
        self.cold = cold
        self.grade_heavy = grade_heavy
        self.payload_factor = payload_factor
        self.aux_bus_kw = (AUX.p_aux_bus_cold_kW if cold else
                           AUX.p_aux_bus_avg_kW) if aux_bus_kw is None \
            else aux_bus_kw
        # A conventional truck's accessories are crank-driven. In the cold
        # the cab-heat load is served by ENGINE COOLANT, which is free
        # waste heat, so the conventional truck does NOT pay the cold
        # accessory penalty an electrified one pays. Charging both the
        # same would be a bookkeeping gift to the electrified candidates,
        # so it is not done.
        self.aux_mech_kw = AUX.p_aux_mech_avg_kW if aux_mech_kw is None \
            else aux_mech_kw
        self.label = label

    def as_dict(self):
        return dict(name=self.name, rho_air=self.rho_air,
                    t_amb_C=self.t_amb_c, cold=self.cold,
                    grade_heavy=self.grade_heavy,
                    payload_factor=self.payload_factor,
                    aux_bus_kW=self.aux_bus_kw,
                    aux_mech_kW=self.aux_mech_kw, label=self.label)


NOMINAL = Ctx("nominal", label="20 C, sea level, nominal payload")


def _bisect_speed(f, lo=0.5, hi=35.0, n=60):
    """Largest v in [lo,hi] with f(v) >= 0 (f decreasing). Returns hi if
    f(hi)>=0, lo if f(lo)<0."""
    if f(hi) >= 0.0:
        return hi
    if f(lo) < 0.0:
        return lo
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if f(mid) >= 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


class GensetLine:
    """BSFC-optimal operating line of an engine+generator pair.

    For each required BUS-SIDE electrical output, search the engine map
    for the (rpm, torque) that delivers it through the generator at
    least fuel. This IS the series architecture's entire thermodynamic
    argument - the engine speed is free - so it is solved on the map
    rather than asserted at a pinned point.

    R12: the generator + active-rectifier stage lives here, on the
    genset side of the ledger. There is no scalar PE member anywhere.
    """

    def __init__(self, engine, generator, p_elec_max_kw, n=161,
                 rpm_lo=800.0, rpm_hi=2000.0, n_rpm=121):
        self.engine = engine
        self.generator = generator
        self.p_elec_max_kw = float(p_elec_max_kw)
        self.p_grid = np.linspace(0.0, self.p_elec_max_kw, n)
        rpms = np.linspace(rpm_lo, rpm_hi, n_rpm)
        fuel = np.zeros(n)
        rpm_opt = np.zeros(n)
        trq_opt = np.zeros(n)
        shaft = np.zeros(n)
        bsfc = np.zeros(n)
        for i, pe in enumerate(self.p_grid):
            if pe <= 1e-9:
                rpm_opt[i] = engine.idle_rpm
                fuel[i] = 0.0
                continue
            p_shaft = generator.shaft_from_elec(rpms, np.full_like(rpms, pe))
            t_shaft = p_shaft * 1e3 / (rpms * 2 * np.pi / 60.0)
            ok = t_shaft <= engine.t_max(rpms)
            b = np.where(ok, engine.bsfc(rpms, t_shaft), np.inf)
            g_per_s = np.where(ok, b * p_shaft / 3600.0, np.inf)
            j = int(np.argmin(g_per_s))
            if not np.isfinite(g_per_s[j]):
                # cannot make this power at any speed: clamp to the max
                fuel[i] = fuel[i - 1] if i else 0.0
                rpm_opt[i], trq_opt[i] = rpm_opt[i - 1], trq_opt[i - 1]
                shaft[i], bsfc[i] = shaft[i - 1], bsfc[i - 1]
                continue
            fuel[i] = g_per_s[j]
            rpm_opt[i] = rpms[j]
            trq_opt[i] = t_shaft[j]
            shaft[i] = p_shaft[j]
            bsfc[i] = b[j]
        self.fuel_gps = fuel
        self.rpm_opt = rpm_opt
        self.trq_opt = trq_opt
        self.p_shaft = shaft
        self.bsfc = bsfc
        # engine LOAD FRACTION along the optimal locus: what a
        # waste-heat-recovery system actually sees (Task 4).
        with np.errstate(divide="ignore", invalid="ignore"):
            self.phi_opt = np.clip(
                trq_opt / np.maximum(engine.t_max(np.maximum(rpm_opt, 1.0)),
                                     1e-9), 0.0, 1.0)

    def phi(self, p_elec_kw):
        return np.interp(np.clip(np.asarray(p_elec_kw, float), 0.0,
                                 self.p_elec_max_kw),
                         self.p_grid, self.phi_opt)

    def fuel_whr(self, p_elec_kw, whr=None):
        f = self.fuel(p_elec_kw)
        if whr is None:
            return f
        return f * (1.0 - whr.gain(self.phi(p_elec_kw)))

    def fuel(self, p_elec_kw):
        return np.interp(np.clip(np.asarray(p_elec_kw, float), 0.0,
                                 self.p_elec_max_kw),
                         self.p_grid, self.fuel_gps)

    def rpm(self, p_elec_kw):
        return np.interp(np.clip(np.asarray(p_elec_kw, float), 0.0,
                                 self.p_elec_max_kw),
                         self.p_grid, self.rpm_opt)

    def best_point(self):
        with np.errstate(divide="ignore", invalid="ignore"):
            # fuel power [kW] = fuel rate [g/s] * LHV [kJ/g]
            eff = np.where(self.p_grid > 1e-9,
                           self.p_grid / (self.fuel_gps * LHV_KJ_PER_G
                                          + 1e-12), 0.0)
        j = int(np.argmax(eff))
        return dict(p_elec_kW=float(self.p_grid[j]),
                    rpm=float(self.rpm_opt[j]),
                    trq_Nm=float(self.trq_opt[j]),
                    p_shaft_kW=float(self.p_shaft[j]),
                    engine_bsfc_g_per_kWh=float(self.bsfc[j]),
                    genset_eta_fuel_to_bus=float(eff[j]))


def pack_soc_run(p_bus_net_kw, p_supply_kw, dt, usable_kwh, soc0=0.6,
                 soc_lo=0.15, soc_hi=0.95, eta_chg=0.97, eta_dis=0.97,
                 p_chg_max_kw=None, p_dis_max_kw=None):
    """Sequential SOC integration with hard limits and honest bookkeeping.

    p_bus_net_kw : bus-side demand (positive = the truck needs power,
                   negative = the truck is pushing power back)
    p_supply_kw  : what the prime mover is delivering to the bus
    Returns SOC trace, the ACTUAL supply used, and the unserved energy -
    the same quantity WS4's ESC-5 accounting names. Unserved energy is
    never silently absorbed: if the pack cannot cover the shortfall, it
    is recorded.
    """
    n = p_bus_net_kw.size
    soc = np.empty(n)
    unserved = 0.0
    shed = 0.0
    e = usable_kwh * soc0
    e_lo, e_hi = usable_kwh * soc_lo, usable_kwh * soc_hi
    h = dt / 3600.0
    pcm = np.inf if p_chg_max_kw is None else p_chg_max_kw
    pdm = np.inf if p_dis_max_kw is None else p_dis_max_kw
    for i in range(n):
        net = p_bus_net_kw[i] - p_supply_kw[i]     # >0 pack discharges
        if net > 0.0:
            p = min(net, pdm)
            unserved += (net - p) * h
            de = p * h / eta_dis
            if e - de < e_lo:
                avail = max(0.0, (e - e_lo)) * eta_dis / h
                unserved += (p - avail) * h
                p = avail
                de = max(0.0, e - e_lo)
            e -= de
        else:
            p = min(-net, pcm)
            shed += (-net - p) * h
            de = p * h * eta_chg
            if e + de > e_hi:
                acc = max(0.0, (e_hi - e)) / eta_chg / h
                shed += (p - acc) * h
                de = max(0.0, e_hi - e)
            e += de
        soc[i] = e / usable_kwh if usable_kwh > 0 else 0.0
    return soc, unserved, shed


# =====================================================================
#  base class
# =====================================================================
class Candidate:
    name = "??"
    title = ""
    policy = ""

    def __init__(self, ctx=NOMINAL, whr=None):
        self.ctx = ctx
        self.whr = whr
        self.setup()

    def whr_mass_kg(self):
        return self.whr.mass_kg if self.whr is not None else 0.0

    # -- to be provided by each architecture --------------------------
    def setup(self):
        raise NotImplementedError

    def mass_rows(self):
        raise NotImplementedError

    def envelope(self, v):
        raise NotImplementedError

    def lam(self, v):
        raise NotImplementedError

    def account(self, tr):
        raise NotImplementedError

    # -- shared -------------------------------------------------------
    def powertrain_mass_kg(self):
        return float(sum(self.mass_rows().values())) + self.whr_mass_kg()

    def tare_common_kg(self):
        return (ML.m_glider_tractor + ML.m_trailer_tare
                + ML.m_driver_and_effects + ML.m_drive_axle_housings)

    def payload_kg(self):
        p = VEH.m_gcw - self.tare_common_kg() - self.powertrain_mass_kg()
        return p * self.ctx.payload_factor

    def curb_kg(self):
        """Combination tare = GCW - payload_at_nominal."""
        return self.tare_common_kg() + self.powertrain_mass_kg()

    def adhesion_force_N(self, mu=None, axles="tandem"):
        mu = ADH.mu_dry if mu is None else mu
        m_ax = (VEH.m_axle_drive_tandem_kg if axles == "tandem"
                else VEH.m_axle_drive_tandem_kg / 2.0)
        return mu * m_ax * G

    def v_cap(self, grade):
        """Descent speed cap: the fastest this candidate may descend
        while holding speed on its own retarding capability plus the
        declared friction allowance."""
        if grade >= -0.005:
            return 1e3

        def excess(v):
            f_res, _, _, f_grade = road_load_force(
                np.array([v]), grade, VEH.m_gcw, None, None, self.ctx.rho_air)
            need = -float(f_res[0])          # >0 : gravity is winning
            if need <= 0.0:
                return 1.0
            _, f_rg, f_rt = self.envelope(v)
            allow = FRICTION_BRAKE_CONT_ALLOWANCE_KW * 1e3 / max(v, 0.5)
            return (f_rg + f_rt + allow) - need

        return _bisect_speed(excess, 2.0, 35.0)

    # -- common energy bookkeeping ------------------------------------
    def _aux_bus_kw(self, tr):
        """Bus-side accessory power, with hotel load while stopped."""
        moving = tr["v"] > 0.1
        return np.where(moving, self.ctx.aux_bus_kw, AUX.p_hotel_idle_kW)

    def _aux_mech_kw(self, tr):
        moving = tr["v"] > 0.1
        return np.where(moving, self.ctx.aux_mech_kw, AUX.p_hotel_idle_kW)

    def spec(self):
        rows = self.mass_rows()
        return dict(name=self.name, title=self.title, policy=self.policy,
                    mass_rows_kg=rows,
                    powertrain_mass_kg=self.powertrain_mass_kg(),
                    tare_common_kg=self.tare_common_kg(),
                    combination_tare_kg=self.curb_kg(),
                    payload_kg=self.payload_kg(),
                    gcw_kg=VEH.m_gcw)


# =====================================================================
#  S0 - conventional diesel + AMT (the ruler)
# =====================================================================
class S0(Candidate):
    name = "S0"
    title = "Conventional 13 L diesel + 12-speed AMT, direct top gear"
    policy = ("AMT selects the highest gear that can deliver the demanded "
              "wheel force above 1,050 rpm; launch on a slipping clutch at "
              "1,200 rpm with the slip heat charged; overrun fuel cut-off "
              "when the wheels drive the engine; compression brake on "
              "descents; accessories crank-driven.")

    def setup(self):
        self.engine = EN.ENG_13L
        self.amt = EN.AMT(self.engine, r_dyn=VEH.r_dyn)
        self.p_engine_brake_kw = 290.0     # [WS8-PROV] 13 L compression brake

    def mass_rows(self):
        return {
            "engine_13L_wet": ML.m_engine_13L_wet,
            "aftertreatment": ML.m_aftertreatment,
            "amt_12sp": ML.m_amt_12sp,
            "driveshafts": ML.m_driveshafts,
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        # deep gears carry the engine inertia at a large ratio
        if v < 6.0:
            return VEH.lam_rot_launch
        if v < 15.0:
            return 0.5 * (VEH.lam_rot_launch + VEH.lam_rot_direct)
        return VEH.lam_rot_direct

    def envelope(self, v):
        f_t = self.amt.max_wheel_force(v)
        f_t = min(f_t, self.adhesion_force_N())
        f_ret = self.amt.engine_brake_force(v, self.p_engine_brake_kw)
        f_ret = min(f_ret, self.adhesion_force_N())
        return f_t, 0.0, f_ret

    def account(self, tr):
        v = tr["v"]
        dt = tr["dt"]
        f_trac = tr["F_trac"]
        moving = v > 0.1
        aux_kw = self._aux_mech_kw(tr)

        ov = np.array([self.amt.overall(i) for i in range(12)])
        eta_g = np.array([self.amt.eta(i) for i in range(12)])
        rpm_all = v[:, None] / VEH.r_dyn * ov[None, :] * 60.0 / (2 * np.pi)
        t_cap = self.engine.t_max(rpm_all)
        f_avail = t_cap * ov[None, :] * eta_g[None, :] / VEH.r_dyn
        in_range = (rpm_all >= self.engine.idle_rpm) & (rpm_all <= 2100.0)
        usable = in_range & (rpm_all >= self.amt.rpm_lo)
        can = usable & (f_avail >= f_trac[:, None])

        # highest gear index that can do the job; else the strongest gear
        rev = can[:, ::-1]
        any_can = rev.any(axis=1)
        gear = 11 - np.argmax(rev, axis=1)
        f_in_range = np.where(in_range, f_avail, -1.0)
        gear = np.where(any_can, gear, np.argmax(f_in_range, axis=1))

        idx = np.arange(v.size)
        rpm = rpm_all[idx, gear]
        eta_sel = eta_g[gear]
        ov_sel = ov[gear]

        # launch: below the speed where 1st gear reaches idle the clutch
        # slips and the engine turns at launch_rpm while the output turns
        # slower. The torque still passes; the SPEED difference is heat.
        slip = (rpm_all[:, 0] < self.engine.idle_rpm) & moving
        gear = np.where(slip, 0, gear)
        ov_sel = np.where(slip, ov[0], ov_sel)
        eta_sel = np.where(slip, eta_g[0], eta_sel)
        rpm = np.where(slip, self.amt.launch_rpm, rpm_all[idx, gear])
        rpm = np.clip(rpm, self.engine.idle_rpm, 2100.0)

        w_eng = rpm * 2 * np.pi / 60.0
        t_trac = f_trac * VEH.r_dyn / (ov_sel * eta_sel)
        t_aux = aux_kw * 1e3 / np.maximum(w_eng, 1e-6)
        t_tot = t_trac + t_aux

        # overrun fuel cut: wheels drive the engine, no fuel, accessories
        # are carried by the vehicle's kinetic energy.
        overrun = (f_trac <= 1.0) & moving & (rpm > self.engine.idle_rpm * 1.1)
        t_tot = np.where(overrun, 0.0, t_tot)
        t_tot = np.minimum(t_tot, self.engine.t_max(rpm))

        p_shaft_kw = t_tot * w_eng / 1e3
        # BSFC is infinite at zero torque, so the map is only queried
        # where there IS torque; elsewhere the fuel is the idle/overrun
        # branch below. Guarding with np.where alone would still evaluate
        # inf*0 and produce a nan.
        fuelling = t_tot > 1e-6
        b = np.full(t_tot.shape, np.inf)
        if fuelling.any():
            with np.errstate(divide="ignore", invalid="ignore"):
                b[fuelling] = self.engine.bsfc(rpm[fuelling], t_tot[fuelling])
        g_per_s = np.zeros(t_tot.shape)
        ok = fuelling & np.isfinite(b)
        g_per_s[ok] = b[ok] * np.clip(p_shaft_kw[ok], 0, None) / 3600.0
        if self.whr is not None:
            phi = np.clip(t_tot / np.maximum(self.engine.t_max(rpm), 1e-9),
                          0.0, 1.0)
            g_per_s = g_per_s * (1.0 - self.whr.gain(phi))
        # idle / stopped
        idle_g = EN.idle_fuel_gps(self.engine)
        stopped = ~moving
        g_per_s = np.where(stopped, idle_g + AUX.p_hotel_idle_kW * 0.0,
                           g_per_s)
        g_per_s = np.where(overrun, 0.0, g_per_s)

        fuel_g = float(np.sum(g_per_s) * dt)

        # clutch slip heat: engine shaft work in minus wheel work out
        p_wheel_kw = f_trac * v / 1e3
        p_slip_kw = np.where(slip, np.clip(
            t_trac * w_eng / 1e3 - p_wheel_kw / eta_sel, 0.0, None), 0.0)
        e_slip_kwh = float(np.sum(p_slip_kw) * dt) / 3600.0

        return dict(
            fuel_g=fuel_g,
            e_fuel_MJ=EN.fuel_energy_MJ(fuel_g),
            e_engine_shaft_kWh=float(np.sum(p_shaft_kw) * dt) / 3600.0,
            e_aux_kWh=float(np.sum(aux_kw) * dt) / 3600.0,
            e_clutch_slip_kWh=e_slip_kwh,
            e_regen_bus_kWh=0.0,
            e_resistor_kWh=0.0,
            e_engine_brake_kWh=float(np.sum(tr["F_retard"] * v) * dt) / 3.6e6,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v) * dt) / 3.6e6,
            unserved_kWh=0.0, shed_kWh=0.0,
            soc_start=0.0, soc_end=0.0,
            mean_engine_rpm_moving=float(np.mean(rpm[moving])),
            mean_bsfc_g_per_kWh=float(
                np.sum(g_per_s[~overrun & moving]) * 3600.0
                / max(np.sum(np.clip(p_shaft_kw[~overrun & moving], 0, None)),
                      1e-9)),
            top_gear_fraction=float(np.mean(gear[moving] == 11)),
            idle_fuel_g=float(np.sum(np.where(stopped, idle_g, 0.0)) * dt),
        )


# =====================================================================
#  series-path plumbing, shared by S1, S2 (unlocked) and S4
# =====================================================================
def series_bus_demand(edrive, tr, aux_kw, count_spin=True):
    """Bus-side power flows for an electric traction path.

    Returns (p_bus_trac, p_bus_regen, p_bus_resistor, p_spin) in kW,
    all BUS-SIDE (CLAUDE.md rule 6), computed sample-by-sample from
    WS2's measured maps through the stated scaling law - never from a
    scalar chain efficiency (R12; this is the member whose absence cost
    Vehicle Zero 7.01 pp at G1, and it is deleted here BY CONSTRUCTION
    because no scalar chain exists anywhere in WS8).
    """
    v = tr["v"]
    p_wheel_trac = tr["F_trac"] * v / 1e3
    p_wheel_regen = tr["F_regen"] * v / 1e3
    p_wheel_retard = tr["F_retard"] * v / 1e3

    eta_m = edrive.eta_bus_to_wheel(v, p_wheel_trac)
    p_bus_trac = np.where(p_wheel_trac > 0, p_wheel_trac / eta_m, 0.0)

    eta_g_r = edrive.eta_wheel_to_bus(v, p_wheel_regen)
    p_bus_regen = p_wheel_regen * eta_g_r

    eta_g_x = edrive.eta_wheel_to_bus(v, p_wheel_retard)
    p_bus_resistor = p_wheel_retard * eta_g_x

    if count_spin:
        # R22(d) at semi scale: a permanently geared PM machine drags
        # whenever the wheels turn and no torque is commanded. Charged
        # as a bus draw on unloaded samples, following WS4's treatment
        # of the same quantity.
        idle_machine = ((tr["F_trac"] <= 1.0) & (tr["F_regen"] <= 1.0)
                        & (tr["F_retard"] <= 1.0) & (v > 0.5))
        p_spin = np.where(idle_machine, edrive.spin_drag_kw(v), 0.0)
    else:
        p_spin = np.zeros_like(v)

    return p_bus_trac, p_bus_regen, p_bus_resistor, p_spin


def _moving_average(x, n):
    if n <= 1:
        return x.copy()
    k = np.ones(n) / n
    pad = n // 2
    xp = np.concatenate([np.full(pad, x[0]), x, np.full(pad, x[-1])])
    return np.convolve(xp, k, mode="same")[pad:pad + x.size]


def series_dispatch(net_bus_kw, dt, line, pack, p_on_kw=55.0,
                    p_off_kw=35.0, smooth_s=180.0, soc_target=0.60,
                    soc_lo=0.15, soc_hi=0.95, kp_kw_per_soc=260.0,
                    soc0=0.60, whr=None):
    """Genset dispatch for a series path. Sequential, charge-sustaining.

    POLICY, declared:
      * feed-forward: a 180 s centred moving average of bus demand. A
        predictive-cruise genset has the route ahead of it, and a centred
        average is the honest expression of that preview - stated rather
        than smuggled in as clairvoyance about the driver.
      * feedback: a PROPORTIONAL state-of-charge restoring term,
        260 kW per unit SOC. Bounded by construction: the worst-case
        correction over the whole SOC band is +/-155 kW, so the loop
        cannot wind up.
      * start-stop with hysteresis (on above 55 kW, off below 35 kW),
        the same shape R19 ruled for Vehicle Zero's V1.
      * THROTTLE-BACK: if the pack cannot accept the surplus the genset
        is producing, the genset is throttled to what the bus will take.
        A real engine does this; a model that instead "sheds" the
        surplus would burn fuel it never used and would flatter nothing
        but the bookkeeping.

    Unserved energy is recorded, never absorbed silently - the failure
    mode WS4's ESC-5 named. Regen the pack cannot accept is moved to the
    resistor rather than shed, because that is where it physically goes.
    """
    n = net_bus_kw.size
    n_smooth = max(1, int(round(smooth_s / dt)))
    pre = np.clip(_moving_average(net_bus_kw, n_smooth), 0.0,
                  line.p_elec_max_kw)

    h = dt / 3600.0
    usable = max(pack.usable_kwh, 1e-9)
    e = usable * soc0
    e_lo, e_hi = usable * soc_lo, usable * soc_hi
    p_max = line.p_elec_max_kw
    p_chg_max, p_dis_max = pack.p_cont_chg_kw, pack.p_cont_dis_kw
    eta_c, eta_d = pack.eta_chg, pack.eta_dis

    p_out = np.empty(n)
    soc = np.empty(n)
    on = False
    unserved = 0.0
    to_resistor = 0.0
    starts = 0

    for i in range(n):
        soc_now = e / usable
        p_ref = pre[i] + kp_kw_per_soc * (soc_target - soc_now)
        if p_ref < 0.0:
            p_ref = 0.0
        elif p_ref > p_max:
            p_ref = p_max
        if on:
            if p_ref < p_off_kw:
                on = False
        else:
            if p_ref > p_on_kw:
                on = True
                starts += 1
        p = p_ref if on else 0.0

        net = net_bus_kw[i] - p
        if net > 0.0:                      # pack discharges
            pd = net if net < p_dis_max else p_dis_max
            de = pd * h / eta_d
            room = e - e_lo
            if de > room:
                pd = room * eta_d / h if h > 0 else 0.0
                de = max(room, 0.0)
            unserved += (net - pd) * h
            e -= de
        else:                              # pack charges
            surplus = -net
            pc = surplus if surplus < p_chg_max else p_chg_max
            de = pc * h * eta_c
            room = e_hi - e
            if de > room:
                pc = room / eta_c / h if h > 0 else 0.0
                de = max(room, 0.0)
            e += de
            over = surplus - pc
            if over > 0.0:
                # first throttle the genset back, then send whatever is
                # left (that is regen, not fuel) to the resistor
                cut = over if over < p else p
                p -= cut
                over -= cut
                to_resistor += over * h
        p_out[i] = p
        soc[i] = e / usable

    fuel_g = float(np.sum(line.fuel_whr(p_out, whr)) * dt)
    on_mask = p_out > 0.0
    return dict(p_genset_kw=p_out, soc=soc, unserved_kWh=unserved,
                shed_kWh=to_resistor, starts=starts, fuel_g=fuel_g,
                genset_on_fraction=float(np.mean(on_mask)),
                p_genset_mean_on_kW=(float(np.mean(p_out[on_mask]))
                                     if on_mask.any() else 0.0),
                p_genset_max_kW=float(np.max(p_out)))


# =====================================================================
#  S1 - pure series (Vehicle Zero's architecture, scaled)
# =====================================================================
SUSTAINED_CLIMB_S = 900.0
"""Duration over which a traction-power claim must be SUSTAINABLE [s].

The 6% mountain segment is ~16 km of plateau; at the speeds these
candidates actually climb it, that is 15-20 minutes of continuous
above-average power. A buffer pack cannot supply that. So the traction
power ceiling written into every candidate's envelope is the prime
mover's continuous output PLUS only the pack contribution that survives
15 minutes:

    p_pack_sustained = usable_kWh * (soc_target - soc_floor)
                       / (SUSTAINED_CLIMB_S / 3600)

The swing is measured from the DISPATCH TARGET (0.60) down to the FLOOR
(0.15), i.e. 0.45 of usable - not the whole usable band. A pack that
starts a climb at its target SOC has only that much to give, and
claiming the full band would be claiming energy the truck has already
spent. Without this rule
the integrator would let a candidate climb on pack power it does not
have and then report the shortfall as "unserved energy" after the fact -
which is exactly the bookkeeping WS4's ESC-5 was raised about. With it,
the candidate simply climbs at the speed its prime mover supports, which
is the honest architectural consequence and the thing worth reporting."""


STARTABILITY_GRADE = 0.12
"""Grade the combination must start and pull away on at GCW.

NOT a WS8 invention: Regulation (EU) No 1230/2012 requires that vehicles
designed to tow a trailer "shall be capable of starting five times within
five minutes at an up-hill gradient of at least 12%", laden to the
technically permissible maximum laden mass of the COMBINATION. That is
the specification, and it is what sizes every single-speed electric
traction path in this trial - it is the reason those paths are as heavy
as they are. Applied identically to S1, S2, S3-axle-B and S4.

The citation was located by the Task 0 scan at search-summary level; the
primary text could not be fetched in this environment, so it is flagged
provisional per E13 precedent along with everything else that scan
found. The 12% figure itself was WS8's working assumption before the
scan ran and does not depend on it.

The "five times within five minutes" clause is a THERMAL requirement as
much as a torque one, and it is not modelled here: WS8 checks the
torque and the adhesion, not the repeat-duty temperature rise in the
traction machine or the clutch. That gap is stated rather than hidden -
see the e-axle repeat-start note in the S3 risk block."""


def startability_force_N(grade=STARTABILITY_GRADE, m=None):
    m = VEH.m_gcw if m is None else m
    th = np.arctan(grade)
    return float(m * G * np.sin(th) + VEH.Crr * m * G * np.cos(th))


def size_edrive_for_startability(ratio, n_machines, grade=None):
    """Solve the stretch factor k that meets startability."""
    f = startability_force_N(STARTABILITY_GRADE if grade is None else grade)
    t_total = f * VEH.r_dyn / (ratio * DL.eta_edrive_reduction)
    return t_total / (n_machines * EL.ScaledEDrive.T_PEAK_WS2_NM)


EDRIVE_RATIO = 12.0
"""Single-speed reduction for every electric traction path. [WS8-PROV]
Set by WS2 r4's carried 7,200 rpm rotor limit: at the top of the demand
band (105 km/h) plus the 6% downhill overspeed the driver model allows,
12.0:1 puts the machine at ~7,073 rpm - under the limit with ~2%
margin. A numerically higher ratio would buy startability but would
over-speed WS2's rotor, and WS8 does not get to re-rate another
workstream's hardware."""


class S1(Candidate):
    name = "S1"
    title = "Pure series - Vehicle Zero's architecture scaled to Class 8"
    policy = ("No mechanical path. Genset follows a 180 s route-preview "
              "average of bus demand on the engine's BSFC-optimal locus "
              "(engine speed free), start-stop below 45 kW, buffer pack "
              "holds SOC 0.15-0.95 about a 0.60 target. Descent braking: "
              "regen to the pack up to its charge acceptance, then the "
              "brake resistor, then friction. PM spin drag charged on "
              "unloaded samples (R22d) - the machines are permanently "
              "geared and there is no disconnect.")

    PACK_KWH = 60.0
    PACK_CELL = "NMC-P-40"
    RESISTOR_KW = 340.0

    def setup(self):
        self.k_each = size_edrive_for_startability(EDRIVE_RATIO, 2)
        self.edrive = EL.ScaledEDrive(self.k_each, EDRIVE_RATIO,
                                      n_machines=2, label="S1 tandem e-drive")
        self.engine = EN.ENG_13L
        # R18 flat-rating: a genset prime mover is not run at its
        # automotive peak. WS4's ruled ratio (132/153.3 = 0.861) is
        # applied to the 13 L's 352 kW peak -> 303 kW continuous.
        self.genset_shaft_kw = EN.flat_rated_cont_kw(self.engine)
        self.generator, self.gen_scale = EL.scaled_generator(
            "GEN-S1", self.genset_shaft_kw)
        self.pack = EL.Pack8(self.PACK_CELL, self.PACK_KWH, 0.80,
                             label="S1 buffer")
        self.line = GensetLine(self.engine, self.generator,
                               self.generator.cont_kw_in * 0.955)
        self.resistor_kw = self.RESISTOR_KW

    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "engine_13L_wet": ML.m_engine_13L_wet,
            "aftertreatment": ML.m_aftertreatment,
            "generator": self.generator.mass_kg,
            "traction_motors": em["motor_kg"],
            "inverters": em["inverter_kg"],
            "motor_reduction_stages": em["reduction_kg"],
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "driveshafts": ML.m_driveshafts,
            "brake_resistor": EL.resistor_mass_kg(self.resistor_kw),
            "buffer_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive

    SOC_TARGET = 0.60
    SOC_FLOOR = 0.15

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh * (self.SOC_TARGET - self.SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def envelope(self, v):
        f_t = self.edrive.wheel_force_max(v)
        # bus-side power ceiling: genset continuous + the pack
        # contribution that survives a 15-minute climb (SUSTAINED_CLIMB_S)
        p_bus_cap = self.line.p_elec_max_kw + self.pack_sustained_kw() \
            - self.ctx.aux_bus_kw
        if v > 0.5:
            eta = float(self.edrive.eta_bus_to_wheel(v, min(
                p_bus_cap, self.edrive.wheel_power_max_kw(v))))
            f_t = min(f_t, p_bus_cap * eta * 1e3 / v)
        f_t = min(f_t, self.adhesion_force_N())

        f_gen_max = self.edrive.wheel_force_max(v)      # generating capability
        f_gen_max = min(f_gen_max, self.adhesion_force_N())
        if v > 0.5:
            blend = regen_blend(v)
            f_regen = min(f_gen_max, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_resistor = min(max(0.0, f_gen_max - f_regen),
                             self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_resistor = 0.0
        return f_t, f_regen, f_resistor

    def account(self, tr):
        dt = tr["dt"]
        aux = self._aux_bus_kw(tr)
        p_t, p_rg, p_rx, p_sp = series_bus_demand(self.edrive, tr, aux)
        net = p_t + aux + p_sp - p_rg
        d = series_dispatch(net, dt, self.line, self.pack, whr=self.whr)
        h = dt / 3600.0
        return dict(
            fuel_g=d["fuel_g"], e_fuel_MJ=EN.fuel_energy_MJ(d["fuel_g"]),
            e_bus_traction_kWh=float(np.sum(p_t)) * h,
            e_aux_kWh=float(np.sum(aux)) * h,
            e_spin_kWh=float(np.sum(p_sp)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg)) * h,
            e_resistor_kWh=float(np.sum(p_rx)) * h,
            e_engine_brake_kWh=0.0,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * tr["v"])) * dt / 3.6e6,
            e_clutch_slip_kWh=0.0,
            unserved_kWh=d["unserved_kWh"], shed_kWh=d["shed_kWh"],
            genset_starts=d["starts"],
            genset_on_fraction=d["genset_on_fraction"],
            p_genset_mean_on_kW=d["p_genset_mean_on_kW"],
            soc_min=float(np.min(d["soc"])), soc_max=float(np.max(d["soc"])),
            soc_start=float(d["soc"][0]), soc_end=float(d["soc"][-1]),
            mean_bsfc_g_per_kWh=float("nan"),
            top_gear_fraction=float("nan"),
            resistor_peak_kW=float(np.max(p_rx)),
        )


# =====================================================================
#  S2 - single cruise-ratio + torque-fill, machine DISCONNECTED
# =====================================================================
class S2(Candidate):
    name = "S2"
    title = ("Single cruise-ratio + torque-fill, traction machine on a "
             "disconnect")
    policy = (
        "One fixed reduction (2.60:1 overall) couples the engine to the "
        "wheels ONLY inside a cruise lockup band; outside it the truck is "
        "pure series. The traction machine sits behind a DISCONNECT, so "
        "while locked and not filling it is stationary and its spin drag "
        "is zero - the G1(b) tax deleted by hardware. Every remaining tax "
        "is charged: the machine's losses whenever it IS connected "
        "(measured, from WS2's map, not a scalar), and the engine's "
        "off-best-point operation at band edges, where road speed - not "
        "the supervisor - sets engine speed.")

    # Fixed cruise ratio: engine at ~1,307 rpm (ENG-13L's BSFC island) at
    # 95 km/h on a 0.50 m radius. [WS8-PROV]
    CRUISE_RATIO = 2.60
    RPM_LOCK_LO = 1000.0
    RPM_LOCK_HI = 1700.0
    PACK_KWH = 60.0
    PACK_CELL = "NMC-P-40"
    RESISTOR_KW = 340.0
    SOC_TARGET = 0.60
    SOC_FLOOR = 0.15
    CONNECT_DILATION_S = 10.0

    def setup(self):
        self.k_each = size_edrive_for_startability(EDRIVE_RATIO, 2)
        self.edrive = EL.ScaledEDrive(self.k_each, EDRIVE_RATIO,
                                      n_machines=2, label="S2 tandem e-drive")
        self.engine = EN.ENG_13L
        self.genset_shaft_kw = EN.flat_rated_cont_kw(self.engine)
        self.generator, _ = EL.scaled_generator("GEN-S2",
                                                self.genset_shaft_kw)
        self.pack = EL.Pack8(self.PACK_CELL, self.PACK_KWH, 0.80,
                             label="S2 buffer")
        self.line = GensetLine(self.engine, self.generator,
                               self.generator.cont_kw_in * 0.955)
        self.resistor_kw = self.RESISTOR_KW
        self.eta_lock = (DL.eta_fixed_ratio_box * DL.eta_axle_tandem
                         * DL.eta_driveshaft)
        self.p_engine_brake_kw = 290.0
        self.v_lock_lo = self._v_at_rpm(self.RPM_LOCK_LO)
        self.v_lock_hi = self._v_at_rpm(self.RPM_LOCK_HI)

    def _v_at_rpm(self, rpm):
        return rpm / self.CRUISE_RATIO * VEH.r_dyn * 2 * np.pi / 60.0

    def _rpm_at_v(self, v):
        return np.asarray(v, float) / VEH.r_dyn * self.CRUISE_RATIO \
            * 60.0 / (2 * np.pi)

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh * (self.SOC_TARGET - self.SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "engine_13L_wet": ML.m_engine_13L_wet,
            "aftertreatment": ML.m_aftertreatment,
            "generator": self.generator.mass_kg,
            "traction_motors": em["motor_kg"],
            "inverters": em["inverter_kg"],
            "motor_reduction_stages": em["reduction_kg"],
            "fixed_cruise_ratio_box": ML.m_fixed_ratio_box,
            "lockup_clutch_and_actuator": ML.m_revmatch_clutch,
            "traction_disconnect": 42.0,
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "driveshafts": ML.m_driveshafts,
            "brake_resistor": EL.resistor_mass_kg(self.resistor_kw),
            "buffer_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive if v < self.v_lock_lo \
            else VEH.lam_rot_edrive + 0.004

    def envelope(self, v):
        # electric path is always available
        f_e = self.edrive.wheel_force_max(v)
        p_bus_cap = self.line.p_elec_max_kw + self.pack_sustained_kw() \
            - self.ctx.aux_bus_kw
        if v > 0.5:
            f_e = min(f_e, p_bus_cap
                      * float(self.edrive.eta_bus_to_wheel(
                          v, min(p_bus_cap,
                                 self.edrive.wheel_power_max_kw(v))))
                      * 1e3 / v)
        f_t = f_e
        # inside the lockup band the engine adds its mechanical output
        if self.v_lock_lo <= v <= self.v_lock_hi:
            rpm = float(self._rpm_at_v(v))
            f_eng = float(self.engine.t_max(rpm)) * self.CRUISE_RATIO \
                * self.eta_lock / VEH.r_dyn
            # engine and machine cannot both have the full bus: while
            # locked the generator is not making traction power, so the
            # fill comes from the pack only.
            f_fill = min(self.edrive.wheel_force_max(v),
                         self.pack_sustained_kw() * 1e3 / max(v, 0.5))
            f_t = max(f_t, f_eng + f_fill)
        f_t = min(f_t, self.adhesion_force_N())

        f_gen = min(self.edrive.wheel_force_max(v), self.adhesion_force_N())
        if v > 0.5:
            blend = regen_blend(v)
            f_regen = min(f_gen, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_res = min(max(0.0, f_gen - f_regen),
                        self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_res = 0.0
        # engine brake is available whenever the engine is coupled
        f_eb = 0.0
        if self.v_lock_lo <= v <= self.v_lock_hi:
            rpm = float(self._rpm_at_v(v))
            f_eb = self.p_engine_brake_kw * (rpm / 2100.0) * 1e3 / max(v, 0.5)
        return f_t, f_regen, f_res + f_eb

    def account(self, tr):
        dt = tr["dt"]
        v = tr["v"]
        aux = self._aux_bus_kw(tr)
        moving = v > 0.1

        rpm_lock = self._rpm_at_v(v)
        locked = ((v >= self.v_lock_lo) & (v <= self.v_lock_hi)
                  & (tr["F_trac"] > 0.0))

        # --- mechanical share while locked ----------------------------
        t_eng_max = self.engine.t_max(np.clip(rpm_lock, 600.0, 2100.0))
        f_eng_max = t_eng_max * self.CRUISE_RATIO * self.eta_lock / VEH.r_dyn
        f_mech = np.where(locked, np.minimum(tr["F_trac"], f_eng_max), 0.0)
        f_fill = np.where(locked, np.clip(tr["F_trac"] - f_mech, 0.0, None),
                          0.0)

        # engine shaft work on the locked path, plus its share of aux
        w_eng = np.clip(rpm_lock, 600.0, 2100.0) * 2 * np.pi / 60.0
        t_mech = f_mech * VEH.r_dyn / (self.CRUISE_RATIO * self.eta_lock)
        # accessories: while locked the engine carries them mechanically
        t_aux_lock = np.where(locked, self.ctx.aux_mech_kw * 1e3
                              / np.maximum(w_eng, 1e-6), 0.0)
        t_lock_tot = np.minimum(t_mech + t_aux_lock,
                                self.engine.t_max(np.clip(rpm_lock, 600.0,
                                                          2100.0)))
        p_lock_shaft_kw = t_lock_tot * w_eng / 1e3
        fuelling = locked & (t_lock_tot > 1e-6)
        b = np.full(v.shape, np.inf)
        if fuelling.any():
            with np.errstate(divide="ignore", invalid="ignore"):
                b[fuelling] = self.engine.bsfc(
                    np.clip(rpm_lock, 600.0, 2100.0)[fuelling],
                    t_lock_tot[fuelling])
        g_lock = np.zeros(v.shape)
        okf = fuelling & np.isfinite(b)
        g_lock[okf] = b[okf] * np.clip(p_lock_shaft_kw[okf], 0, None) / 3600.0
        if self.whr is not None:
            phi_l = np.clip(t_lock_tot / np.maximum(
                self.engine.t_max(np.clip(rpm_lock, 600.0, 2100.0)), 1e-9),
                0.0, 1.0)
            g_lock = g_lock * (1.0 - self.whr.gain(phi_l))

        # --- electric share -------------------------------------------
        # a synthetic trace for the series/fill part of the traction
        tr_e = dict(tr)
        tr_e["F_trac"] = np.where(locked, f_fill, tr["F_trac"])
        p_t, p_rg, p_rx, _ = series_bus_demand(self.edrive, tr_e, aux,
                                               count_spin=False)

        # spin drag: charged ONLY where the machine is connected but
        # unloaded. While locked the disconnect is open unless the
        # machine has been asked to fill within CONNECT_DILATION_S.
        w = max(1, int(round(self.CONNECT_DILATION_S / dt)))
        filling = f_fill > 1.0
        connected_lock = _moving_average(filling.astype(float), w) > 1e-9
        unloaded_connected = (
            (connected_lock & locked & ~filling)
            | (~locked & (tr["F_trac"] <= 1.0) & (tr["F_regen"] <= 1.0)
               & (tr["F_retard"] <= 1.0) & moving))
        p_spin = np.where(unloaded_connected, self.edrive.spin_drag_kw(v), 0.0)

        # bus demand: aux is electric only when NOT locked (locked, the
        # engine carries it mechanically - already charged above)
        aux_bus = np.where(locked, 0.0, aux)
        net = p_t + aux_bus + p_spin - p_rg
        d = series_dispatch(net, dt, self.line, self.pack,
                            soc_target=self.SOC_TARGET,
                            soc_lo=self.SOC_FLOOR, whr=self.whr)

        h = dt / 3600.0
        fuel_g = float(np.sum(g_lock) * dt) + d["fuel_g"]
        idle_g = EN.idle_fuel_gps(self.engine)
        stopped = ~moving
        fuel_g += float(np.sum(np.where(stopped & (d["p_genset_kw"] <= 0.0),
                                        idle_g, 0.0)) * dt)
        return dict(
            fuel_g=fuel_g, e_fuel_MJ=EN.fuel_energy_MJ(fuel_g),
            e_bus_traction_kWh=float(np.sum(p_t)) * h,
            e_mech_traction_kWh=float(np.sum(f_mech * v)) * dt / 3.6e6,
            e_torque_fill_wheel_kWh=float(np.sum(f_fill * v)) * dt / 3.6e6,
            # accessories are served TWO ways in S2 and each is reported
            # where it was actually charged: mechanically off the crank
            # while locked (already inside the locked-path fuel above),
            # and bus-side otherwise. Summing the bus figure over the
            # whole trace would report energy the bus never carried.
            e_aux_bus_kWh=float(np.sum(aux_bus)) * h,
            e_aux_mech_kWh=float(np.sum(
                np.where(locked, self.ctx.aux_mech_kw, 0.0))) * h,
            e_aux_kWh=(float(np.sum(aux_bus))
                       + float(np.sum(np.where(locked,
                                               self.ctx.aux_mech_kw,
                                               0.0)))) * h,
            e_spin_kWh=float(np.sum(p_spin)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg)) * h,
            e_resistor_kWh=float(np.sum(p_rx)) * h,
            e_engine_brake_kWh=float(np.sum(tr["F_retard"] * v)) * dt / 3.6e6,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v)) * dt / 3.6e6,
            e_clutch_slip_kWh=0.0,
            unserved_kWh=d["unserved_kWh"], shed_kWh=d["shed_kWh"],
            genset_starts=d["starts"],
            genset_on_fraction=d["genset_on_fraction"],
            p_genset_mean_on_kW=d["p_genset_mean_on_kW"],
            soc_min=float(np.min(d["soc"])), soc_max=float(np.max(d["soc"])),
            soc_start=float(d["soc"][0]), soc_end=float(d["soc"][-1]),
            locked_fraction_moving=float(np.mean(locked[moving])),
            fill_fraction_of_locked=float(
                np.mean(filling[locked]) if locked.any() else 0.0),
            machine_connected_fraction=float(np.mean(
                (connected_lock | ~locked)[moving])),
            mean_locked_engine_rpm=float(
                np.mean(rpm_lock[locked]) if locked.any() else 0.0),
            mean_locked_bsfc_g_per_kWh=float(
                np.sum(g_lock[okf]) * 3600.0
                / max(np.sum(p_lock_shaft_kw[okf]), 1e-9)) if okf.any()
            else float("nan"),
            mean_bsfc_g_per_kWh=float("nan"),
            top_gear_fraction=float("nan"),
            resistor_peak_kW=float(np.max(p_rx)),
        )


# =====================================================================
#  S3 - tandem split: fixed-ratio diesel axle + disconnectable e-axle
# =====================================================================
class S3(Candidate):
    name = "S3"
    title = ("Tandem split - diesel axle on ONE fixed ratio (no gearbox "
             "anywhere) + disconnectable e-axle")
    policy = (
        "Axle A: downsized diesel through a single fixed reduction and a "
        "rev-matched clutch. There is NO gearbox and NO generator, so the "
        "engine can do exactly one thing - turn axle A - and only above "
        "the road speed at which the fixed ratio puts it above its "
        "lugging limit. Below that speed the clutch opens and the engine "
        "SHUTS DOWN, because with no generator there is nothing else for "
        "it to drive. Axle B: a disconnectable e-axle owning launch, low "
        "speed, regen and peak assist, fed by a buffer pack that can only "
        "be refilled by regen or by through-the-road charging (engine "
        "pushes axle A, e-axle harvests on axle B) - a lossy path taken "
        "only when the engine is lightly loaded and the pack is below "
        "target.\n"
        "BOTH G1 TAXES DELETED BY CONSTRUCTION, not by assumption: "
        "(a) the map-vs-scalar member cannot recur because no scalar "
        "chain efficiency exists anywhere in WS8 - every electric sample "
        "goes through WS2 r4's measured loss surface; (b) the spin-drag "
        "member is deleted by the e-axle's disconnect, and the code "
        "charges spin drag ONLY on samples where that disconnect is "
        "closed, so the deletion is auditable rather than asserted.")

    RATIO_A = 3.40                 # swept in run_ws8.py
    RPM_COUPLE_MIN = 1000.0        # lugging limit [WS8-PROV]
    RPM_MAX = 2100.0
    PACK_KWH = 60.0
    PACK_CELL = "NMC-P-40"
    SOC_TARGET = 0.60
    SOC_FLOOR = 0.15
    SOC_CEIL = 0.95
    RESISTOR_KW = 200.0

    def __init__(self, ctx=NOMINAL, whr=None, ratio_a=None,
                 engine_name="ENG-11L"):
        self.ratio_a = self.RATIO_A if ratio_a is None else float(ratio_a)
        self.engine_name = engine_name
        super().__init__(ctx, whr)

    def setup(self):
        self.k_axleB = size_edrive_for_startability(EDRIVE_RATIO, 1)
        self.edrive = EL.ScaledEDrive(self.k_axleB, EDRIVE_RATIO,
                                      n_machines=1, label="S3 e-axle (axle B)")
        self.engine = EN.ENGINES[self.engine_name]
        self.pack = EL.Pack8(self.PACK_CELL, self.PACK_KWH, 0.80,
                             label="S3 buffer")
        self.eta_A = (DL.eta_fixed_ratio_box * DL.eta_axle_single_reduction
                      * DL.eta_driveshaft)
        self.p_engine_brake_kw = 240.0        # 11 L compression brake
        self.resistor_kw = self.RESISTOR_KW
        self.v_couple_min = self._v_at_rpm(self.RPM_COUPLE_MIN)
        self.v_couple_max = self._v_at_rpm(self.RPM_MAX)

    def _v_at_rpm(self, rpm):
        return rpm / self.ratio_a * VEH.r_dyn * 2 * np.pi / 60.0

    def _rpm_at_v(self, v):
        return np.asarray(v, float) / VEH.r_dyn * self.ratio_a \
            * 60.0 / (2 * np.pi)

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh * (self.SOC_TARGET - self.SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def adhesion_axleA(self, mu=None):
        return self.adhesion_force_N(mu, axles="single")

    def adhesion_axleB(self, mu=None):
        return self.adhesion_force_N(mu, axles="single")

    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "engine_%s_wet" % self.engine_name.replace("ENG-", "").lower():
                self.engine.mass_kg,
            "aftertreatment": ML.m_aftertreatment,
            "fixed_ratio_box_axleA": ML.m_fixed_ratio_box,
            "revmatch_clutch": ML.m_revmatch_clutch,
            "traction_motor_axleB": em["motor_kg"],
            "inverter_axleB": em["inverter_kg"],
            "motor_reduction_axleB": em["reduction_kg"],
            "eaxle_disconnect": 42.0,
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "driveshafts": ML.m_driveshafts,
            "brake_resistor": EL.resistor_mass_kg(self.resistor_kw),
            "buffer_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive

    def f_axleA_max(self, v):
        if not (self.v_couple_min <= v <= self.v_couple_max):
            return 0.0
        rpm = float(self._rpm_at_v(v))
        f = float(self.engine.t_max(rpm)) * self.ratio_a * self.eta_A \
            / VEH.r_dyn
        return min(f, self.adhesion_axleA())

    def f_axleB_max(self, v):
        f = self.edrive.wheel_force_max(v)
        p_cap = self.pack_sustained_kw() - self.ctx.aux_bus_kw
        if v > 0.5 and p_cap > 0:
            eta = float(self.edrive.eta_bus_to_wheel(
                v, min(p_cap, self.edrive.wheel_power_max_kw(v))))
            f = min(f, p_cap * eta * 1e3 / v)
        elif v > 0.5:
            f = 0.0
        return min(f, self.adhesion_axleB())

    def envelope(self, v):
        f_t = self.f_axleA_max(v) + self.f_axleB_max(v)
        f_t = min(f_t, self.adhesion_force_N())

        f_gen = min(self.edrive.wheel_force_max(v), self.adhesion_axleB())
        if v > 0.5:
            blend = regen_blend(v)
            f_regen = min(f_gen, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_res = min(max(0.0, f_gen - f_regen),
                        self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_res = 0.0
        f_eb = 0.0
        if self.v_couple_min <= v <= self.v_couple_max:
            rpm = float(self._rpm_at_v(v))
            f_eb = min(self.p_engine_brake_kw * (rpm / 2100.0) * 1e3
                       / max(v, 0.5), self.adhesion_axleA())
        return f_t, f_regen, f_res + f_eb

    def grade_hold(self, grade, mu=None):
        """The fixed-ratio grade-hold question, answered directly.

        Scans the road speeds at which the clutch may be CLOSED at all
        (engine between its lugging limit and its over-speed limit) and
        asks whether axle A alone can balance road load at any of them.
        There are three distinct outcomes and they are reported as
        different things, because they mean different things:

          holds        - axle A balances road load somewhere in the
                         coupled band; the reported speed is the fastest
                         such speed.
          below_floor  - axle A could balance road load, but only at a
                         speed BELOW the coupling floor, where the fixed
                         ratio would lug the engine to a stall. The
                         clutch cannot be closed there, so the capability
                         is unreachable.
          no_solution  - axle A cannot balance road load anywhere,
                         reachable or not.

        `below_floor` and `no_solution` both mean the diesel axle is
        unusable on that grade and the truck is on its pack.
        """
        vs = np.arange(1.0, 33.0, 0.1)
        f_res = np.array([float(road_load_force(np.array([x]), grade,
                                                VEH.m_gcw, None, None,
                                                self.ctx.rho_air)[0][0])
                          for x in vs])
        rpm = self._rpm_at_v(vs)
        in_band = (rpm >= self.RPM_COUPLE_MIN) & (rpm <= self.RPM_MAX)
        f_av = np.minimum(self.engine.t_max(np.clip(rpm, 600.0, self.RPM_MAX))
                          * self.ratio_a * self.eta_A / VEH.r_dyn,
                          self.adhesion_axleA(mu))
        ok_band = in_band & (f_av >= f_res)
        ok_any = f_av >= f_res
        if ok_band.any():
            v_hold = float(vs[ok_band][-1])
            status = "holds"
        elif ok_any.any():
            v_hold = float(vs[ok_any][-1])
            status = "below_floor"
        else:
            v_hold = 0.0
            status = "no_solution"
        i_ref = int(np.argmin(np.abs(vs - max(v_hold, self.v_couple_min))))
        return dict(grade=grade, status=status,
                    v_hold_diesel_axle_kmh=v_hold * 3.6,
                    v_couple_floor_kmh=self.v_couple_min * 3.6,
                    v_couple_ceiling_kmh=self.v_couple_max * 3.6,
                    diesel_axle_usable=bool(status == "holds"),
                    F_axleA_at_ref_kN=float(f_av[i_ref]) / 1e3,
                    F_required_at_ref_kN=float(f_res[i_ref]) / 1e3,
                    adhesion_limited=bool(
                        f_av[i_ref] >= self.adhesion_axleA(mu) - 1.0))

    def cruise_overspeed_check(self, v_max_kmh=105.0):
        """A fixed ratio that lowers the grade-hold floor raises cruise
        rpm. This is the constraint that closes the S3 design space."""
        rpm = float(self._rpm_at_v(v_max_kmh / 3.6))
        return dict(ratio_A=self.ratio_a, v_max_kmh=v_max_kmh,
                    engine_rpm_at_v_max=rpm, rpm_ceiling=self.RPM_MAX,
                    ok=bool(rpm <= self.RPM_MAX))

    def climb_energy_check(self, grade=0.06, length_km=16.0):
        """If the diesel axle cannot hold the grade, the e-axle must -
        from the pack. This asks whether the pack contains that energy."""
        gh = self.grade_hold(grade)
        if gh["status"] == "holds":
            return dict(grade=grade, length_km=length_km,
                        pack_must_carry_climb=False,
                        e_required_bus_kWh=0.0,
                        e_pack_available_kWh=self.pack.usable_kwh
                        * (self.SOC_TARGET - self.SOC_FLOOR),
                        feasible=True, v_climb_kmh=gh[
                            "v_hold_diesel_axle_kmh"])
        # e-axle alone: settle where its sustained force balances load
        vs = np.arange(1.0, 33.0, 0.1)
        f_res = np.array([float(road_load_force(np.array([x]), grade,
                                                VEH.m_gcw, None, None,
                                                self.ctx.rho_air)[0][0])
                          for x in vs])
        f_b = np.array([self.f_axleB_max(float(x)) for x in vs])
        ok = f_b >= f_res
        v_climb = float(vs[ok][-1]) if ok.any() else 0.0
        if v_climb <= 0.0:
            return dict(grade=grade, length_km=length_km,
                        pack_must_carry_climb=True, e_required_bus_kWh=None,
                        e_pack_available_kWh=self.pack.usable_kwh
                        * (self.SOC_TARGET - self.SOC_FLOOR),
                        feasible=False, v_climb_kmh=0.0,
                        note="e-axle cannot balance road load at any speed")
        t_h = (length_km * 1000.0 / v_climb) / 3600.0
        p_wheel = f_res[int(np.argmin(np.abs(vs - v_climb)))] * v_climb / 1e3
        eta = float(self.edrive.eta_bus_to_wheel(v_climb, p_wheel))
        e_req = (p_wheel / eta + self.ctx.aux_bus_kw) * t_h
        e_av = self.pack.usable_kwh * (self.SOC_TARGET - self.SOC_FLOOR)
        return dict(grade=grade, length_km=length_km,
                    pack_must_carry_climb=True,
                    v_climb_kmh=v_climb * 3.6,
                    climb_duration_min=t_h * 60.0,
                    e_required_bus_kWh=e_req,
                    e_pack_available_kWh=e_av,
                    shortfall_kWh=e_req - e_av,
                    feasible=bool(e_req <= e_av))

    def account(self, tr):
        dt = tr["dt"]
        v = tr["v"]
        n = v.size
        aux = self._aux_bus_kw(tr)
        moving = v > 0.1
        h = dt / 3600.0

        rpm_a = np.clip(self._rpm_at_v(v), 600.0, self.RPM_MAX)
        coupled = ((v >= self.v_couple_min) & (v <= self.v_couple_max)
                   & moving)
        t_a_max = self.engine.t_max(rpm_a)
        f_a_cap = np.minimum(t_a_max * self.ratio_a * self.eta_A / VEH.r_dyn,
                             self.adhesion_axleA())
        f_a_cap = np.where(coupled, f_a_cap, 0.0)
        f_a = np.minimum(tr["F_trac"], f_a_cap)
        f_b = np.clip(tr["F_trac"] - f_a, 0.0, None)

        p_b_wheel = f_b * v / 1e3
        eta_m = self.edrive.eta_bus_to_wheel(v, p_b_wheel)
        p_b_bus = np.where(p_b_wheel > 0, p_b_wheel / eta_m, 0.0)
        p_rg_wheel = tr["F_regen"] * v / 1e3
        eta_g = self.edrive.eta_wheel_to_bus(v, p_rg_wheel)
        p_rg_bus = p_rg_wheel * eta_g
        p_rx_wheel = np.where(coupled, 0.0, tr["F_retard"] * v / 1e3)
        p_rx_bus = p_rx_wheel * self.edrive.eta_wheel_to_bus(v, p_rx_wheel)

        # e-axle disconnect: open whenever the machine has no job. Spin
        # drag is charged ONLY when it is closed - this is the auditable
        # deletion of the G1(b) tax.
        w = max(1, int(round(10.0 / dt)))
        busy = (f_b > 1.0) | (tr["F_regen"] > 1.0) | (p_rx_wheel > 0.1)
        connected = _moving_average(busy.astype(float), w) > 1e-9
        spin_rate = self.edrive.spin_drag_kw(v)

        # through-the-road charging headroom on axle A
        f_a_head = np.clip(f_a_cap - f_a, 0.0, None)
        f_a_head = np.minimum(f_a_head, self.edrive.wheel_force_max(v))
        p_chg_head_bus = f_a_head * v / 1e3 * eta_g

        idle_g = EN.idle_fuel_gps(self.engine)
        usable = max(self.pack.usable_kwh, 1e-9)
        e = usable * self.SOC_TARGET
        e_lo, e_hi = usable * self.SOC_FLOOR, usable * self.SOC_CEIL
        soc = np.empty(n)
        f_chg_wheel = np.zeros(n)
        p_spin = np.zeros(n)
        unserved = 0.0
        e_uncoupled_traction = 0.0
        n_engine_off = 0
        prev_on = False

        for i in range(n):
            soc_now = e / usable
            demand = p_b_bus[i] + aux[i] - p_rg_bus[i]
            if connected[i]:
                demand += spin_rate[i]
                p_spin[i] = spin_rate[i]
            chg = 0.0
            if coupled[i] and soc_now < self.SOC_TARGET \
                    and p_chg_head_bus[i] > 0.0:
                want = (self.pack.p_cont_chg_kw
                        * (self.SOC_TARGET - soc_now)
                        / (self.SOC_TARGET - self.SOC_FLOOR))
                chg = min(want, p_chg_head_bus[i])
                # only charge while the engine is lightly loaded, where
                # loading it actually improves BSFC
                if f_a[i] > 0.72 * max(f_a_cap[i], 1e-9):
                    chg = 0.0
            net = demand - chg
            if net > 0.0:
                pd = min(net, self.pack.p_cont_dis_kw)
                de = pd * h / self.pack.eta_dis
                room = e - e_lo
                if de > room:
                    pd = room * self.pack.eta_dis / h if h > 0 else 0.0
                    de = max(room, 0.0)
                unserved += (net - pd) * h
                e -= de
            else:
                pc = min(-net, self.pack.p_cont_chg_kw)
                de = pc * h * self.pack.eta_chg
                room = e_hi - e
                if de > room:
                    pc = room / self.pack.eta_chg / h if h > 0 else 0.0
                    de = max(room, 0.0)
                    chg = max(0.0, chg - ((-net) - pc))
                e += de
            f_chg_wheel[i] = (chg / max(eta_g[i], 1e-6) * 1e3
                              / max(v[i], 0.5)) if chg > 0 else 0.0
            soc[i] = e / usable
            if coupled[i] and not prev_on:
                n_engine_off += 1
            prev_on = coupled[i]
            if not coupled[i]:
                e_uncoupled_traction += p_b_bus[i] * h

        # engine fuel: only while coupled
        t_a = (f_a + f_chg_wheel) * VEH.r_dyn / (self.ratio_a * self.eta_A)
        t_a = np.minimum(t_a, t_a_max)
        w_eng = rpm_a * 2 * np.pi / 60.0
        p_a_shaft = t_a * w_eng / 1e3
        fuelling = coupled & (t_a > 1e-6)
        b = np.full(n, np.inf)
        if fuelling.any():
            with np.errstate(divide="ignore", invalid="ignore"):
                b[fuelling] = self.engine.bsfc(rpm_a[fuelling], t_a[fuelling])
        g = np.zeros(n)
        okf = fuelling & np.isfinite(b)
        g[okf] = b[okf] * np.clip(p_a_shaft[okf], 0, None) / 3600.0
        if self.whr is not None:
            phi_a = np.clip(t_a / np.maximum(t_a_max, 1e-9), 0.0, 1.0)
            g = g * (1.0 - self.whr.gain(phi_a))
        fuel_g = float(np.sum(g) * dt)

        return dict(
            fuel_g=fuel_g, e_fuel_MJ=EN.fuel_energy_MJ(fuel_g),
            ratio_A=self.ratio_a,
            e_axleA_wheel_kWh=float(np.sum(f_a * v)) * dt / 3.6e6,
            e_axleB_bus_kWh=float(np.sum(p_b_bus)) * h,
            e_ttr_charge_bus_kWh=float(np.sum(f_chg_wheel * v)) * dt / 3.6e6,
            e_aux_kWh=float(np.sum(aux)) * h,
            e_spin_kWh=float(np.sum(p_spin)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg_bus)) * h,
            e_resistor_kWh=float(np.sum(p_rx_bus)) * h,
            e_engine_brake_kWh=float(
                np.sum(np.where(coupled, tr["F_retard"] * v, 0.0)))
            * dt / 3.6e6,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v)) * dt / 3.6e6,
            e_clutch_slip_kWh=0.0,
            e_uncoupled_traction_bus_kWh=e_uncoupled_traction,
            unserved_kWh=unserved, shed_kWh=0.0,
            coupled_fraction_moving=float(np.mean(coupled[moving])),
            eaxle_connected_fraction_moving=float(np.mean(connected[moving])),
            clutch_engagements=n_engine_off,
            v_couple_floor_kmh=self.v_couple_min * 3.6,
            soc_min=float(np.min(soc)), soc_max=float(np.max(soc)),
            soc_start=float(soc[0]), soc_end=float(soc[-1]),
            mean_coupled_engine_rpm=float(
                np.mean(rpm_a[coupled])) if coupled.any() else 0.0,
            mean_bsfc_g_per_kWh=float(np.sum(g[okf]) * 3600.0
                                      / max(np.sum(p_a_shaft[okf]), 1e-9))
            if okf.any() else float("nan"),
            top_gear_fraction=float("nan"),
            genset_starts=0, genset_on_fraction=float(np.mean(coupled)),
            p_genset_mean_on_kW=float("nan"),
            resistor_peak_kW=float(np.max(p_rx_bus)),
            idle_fuel_g=0.0,
        )



# =====================================================================
#  S4 - range-extended BEV (large pack + sustainer genset)
# =====================================================================
class S4(Candidate):
    name = "S4"
    title = "Range-extended BEV - large pack + ~170 kW sustainer genset"
    policy = (
        "Electric traction only; a small sustainer genset holds charge. "
        "Run CHARGE-SUSTAINING over the mission (the pack ends where it "
        "started), because the metric of record is FUEL energy and no "
        "electricity accounting was ordered: crediting a plug-in start "
        "would let S4 import propulsion energy the metric cannot see. "
        "That choice is stated, and its consequence - that S4 is judged "
        "as a series hybrid with a small engine and a heavy pack, not as "
        "a plug-in - is escalated rather than buried.")

    PACK_KWH = 150.0
    PACK_CELL = "NMC-P-40"
    RESISTOR_KW = 340.0
    SOC_TARGET = 0.60
    SOC_FLOOR = 0.15

    def setup(self):
        self.k_each = size_edrive_for_startability(EDRIVE_RATIO, 2)
        self.edrive = EL.ScaledEDrive(self.k_each, EDRIVE_RATIO,
                                      n_machines=2, label="S4 tandem e-drive")
        # 7 L class: flat-rates (R18) to ~200 kW, the TOP of the
        # assignment's 150-200 kW sustainer band.
        self.engine = EN.ENG_7L
        self.sustainer_shaft_kw = EN.flat_rated_cont_kw(self.engine)
        self.generator, _ = EL.scaled_generator("GEN-S4",
                                                self.sustainer_shaft_kw)
        self.pack = EL.Pack8(self.PACK_CELL, self.PACK_KWH, 0.80,
                             label="S4 traction pack")
        self.line = GensetLine(self.engine, self.generator,
                               self.generator.cont_kw_in * 0.955)
        self.resistor_kw = self.RESISTOR_KW

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh * (self.SOC_TARGET - self.SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "sustainer_engine_wet": self.engine.mass_kg,
            "aftertreatment": 90.0,
            "generator": self.generator.mass_kg,
            "traction_motors": em["motor_kg"],
            "inverters": em["inverter_kg"],
            "motor_reduction_stages": em["reduction_kg"],
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "driveshafts": ML.m_driveshafts,
            "brake_resistor": EL.resistor_mass_kg(self.resistor_kw),
            "traction_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal + 60.0,
            "fuel": ML.m_fuel_small,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive

    def envelope(self, v):
        f_t = self.edrive.wheel_force_max(v)
        p_bus_cap = self.line.p_elec_max_kw + self.pack_sustained_kw() \
            - self.ctx.aux_bus_kw
        if v > 0.5:
            eta = float(self.edrive.eta_bus_to_wheel(
                v, min(p_bus_cap, self.edrive.wheel_power_max_kw(v))))
            f_t = min(f_t, p_bus_cap * eta * 1e3 / v)
        f_t = min(f_t, self.adhesion_force_N())
        f_gen = min(self.edrive.wheel_force_max(v), self.adhesion_force_N())
        if v > 0.5:
            blend = regen_blend(v)
            f_regen = min(f_gen, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_res = min(max(0.0, f_gen - f_regen),
                        self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_res = 0.0
        return f_t, f_regen, f_res

    def account(self, tr):
        dt = tr["dt"]
        aux = self._aux_bus_kw(tr)
        p_t, p_rg, p_rx, p_sp = series_bus_demand(self.edrive, tr, aux)
        net = p_t + aux + p_sp - p_rg
        d = series_dispatch(net, dt, self.line, self.pack,
                            p_on_kw=25.0, p_off_kw=15.0,
                            soc_target=self.SOC_TARGET,
                            soc_lo=self.SOC_FLOOR, whr=self.whr)
        h = dt / 3600.0
        soc = d["soc"]
        return dict(
            fuel_g=d["fuel_g"], e_fuel_MJ=EN.fuel_energy_MJ(d["fuel_g"]),
            e_bus_traction_kWh=float(np.sum(p_t)) * h,
            e_aux_kWh=float(np.sum(aux)) * h,
            e_spin_kWh=float(np.sum(p_sp)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg)) * h,
            e_resistor_kWh=float(np.sum(p_rx)) * h,
            e_engine_brake_kWh=0.0,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * tr["v"])) * dt / 3.6e6,
            e_clutch_slip_kWh=0.0,
            unserved_kWh=d["unserved_kWh"], shed_kWh=d["shed_kWh"],
            genset_starts=d["starts"],
            genset_on_fraction=d["genset_on_fraction"],
            p_genset_mean_on_kW=d["p_genset_mean_on_kW"],
            soc_min=float(np.min(soc)), soc_max=float(np.max(soc)),
            soc_start=float(soc[0]), soc_end=float(soc[-1]),
            soc_drift=float(soc[-1] - soc[0]),
            charge_sustaining_error_kWh=float(
                (soc[-1] - soc[0]) * self.pack.usable_kwh),
            mean_bsfc_g_per_kWh=float("nan"),
            top_gear_fraction=float("nan"),
            resistor_peak_kW=float(np.max(p_rx)),
        )


CANDIDATES = {"S0": S0, "S1": S1, "S2": S2, "S3": S3, "S4": S4}
