"""
Project Volt - WS9
The architectures (assignment, "Ruler" and "Candidates").

  S0R   the RULER: WS8's S0 plus a hydraulic retarder with its mass
        charged (ESC-6), same engine, same AMT
  S5    minimal transmission: 2-speed dog box, motor-synchronised shifts,
        torque-fill through the shift, lean machine + buffer sized for
        launch / regen / the R2-style descent duty only, engine sized to
        cruise-plus-margin
  S6    zero-mass stack: mechanical drive as S0, opposed-piston-class
        engine on a cited efficiency basis, predictive energy management
  S7    marginal-mass electrification: motorise an EXISTING trailer axle;
        tractor untouched; charge everything
  S4p   range-extended BEV re-posed: cited external cell (ESC-1c),
        electricity term (ESC-3)

GCW IS FIXED AT 36,300 kg. The road-load physics is therefore identical for
every candidate and powertrain mass is paid for in PAYLOAD - the
denominator of the metric of record - and nowhere else. That is WALL 2, and
it is why every sizing rule in ws9_storage.py exists.

WHAT IS INHERITED AND NOT RE-DERIVED (assignment: "Inherit the WS8 pipeline
... do not re-derive what is ratified; extend it"): the cycles, the
achieved-speed integrator, the road load, the mass ledger, the WS2 machine
stretch, the WS3 pack construction, the HD Willans engines and the AMT, the
genset line, the startability specification, the sustained-climb rule, the
regen blend-out and the friction-brake allowance all come from
`ws8_*.py` READ-ONLY (CLAUDE.md rule 10).

WHAT WS9 CHANGES, and why each change is ordered rather than chosen:
  [ESC-6]    the ruler gains a hydraulic retarder with its mass charged
  [R30]      pack preconditioning and a waste-heat cab path, modelled
  [R2-IMPL F2]  cold charge acceptance is WIRED into every dispatch path
  [R2-IMPL F5]  ONE spin-drag rule for every candidate
  [R2-IMPL F6]  corrections priced at the run's own DUTY-AVERAGED
                efficiency, not at a locus maximum
  [R2-IMPL F11] the ambient/altitude derate is exercised (R28's new corner)
  [R2-IMPL F12] ratio bounds solved in closed form
  [ESC-2]    every machine is gated at k <= 2.0
  [ESC-4]    genset ratings on the sourced ISO 8528-1 PRP basis
  [ESC-1c/3] S4' carries a cited external cell and an electricity term
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_candidates as CD8                                  # noqa: E402
import ws8_electric as EL8                                    # noqa: E402
import ws8_engine as EN8                                      # noqa: E402
from ws8_params import (VEH, ADH, AUX, DL, ML, G,             # noqa: E402
                        LHV_KJ_PER_G)
from ws8_physics import road_load_force                       # noqa: E402

import ws9_engines as E9                                      # noqa: E402
import ws9_params as P9                                       # noqa: E402
import ws9_storage as ST9                                     # noqa: E402
import ws9_walls as W9                                        # noqa: E402
from ws9_thermal import CabHeat, PackThermal                  # noqa: E402

TRL_SHARE = P9.TRL.axle_load_share
FRICTION_ALLOWANCE_KW = CD8.FRICTION_BRAKE_CONT_ALLOWANCE_KW   # [WS8]
EDRIVE_RATIO = CD8.EDRIVE_RATIO                                # [WS8] 12.0
SUSTAINED_CLIMB_S = CD8.SUSTAINED_CLIMB_S                      # [WS8] 900 s

SPIN_IDLE_FORCE_N = CD8.SPIN_IDLE_FORCE_N          # [WS8 r2] 1.0 N
SPIN_IDLE_V_MIN_MS = CD8.SPIN_IDLE_V_MIN_MS        # [WS8 r2] 0.5 m/s
"""R22(d), on WS8 ROUND 2's rule and WS8 round 2's thresholds.

r2 states the rule as: charge `loss_ws2(n, 0)` when the machine is GEARED
AND UNLOADED, and charge nothing extra when it is loaded because the
measured map already carries the loss there. r1 had three inconsistent
treatments of the same quantity (F5) and r2 unified them.

WS9 CARRIES THE RULE AND THE THRESHOLDS UNCHANGED and changes exactly one
thing, because it must: r2 tests the VEHICLE's three force channels, which
is exact for WS8 where the machine was the only traction path. Two WS9
candidates have a machine that is NOT the only traction path - S5's engine
pulls through a dog box while its machine idles, S7's tractor pulls while
the trailer machine idles - and on those the vehicle-level test would say
"loaded" while the machine itself is doing nothing. So WS9 applies r2's
rule TO THE MACHINE'S OWN SHAFT: geared (its disconnect closed), its own
commanded force below r2's own 1 N threshold, and moving above r2's own
0.5 m/s. Same rule, same numbers, right shaft - and the change is stated
here rather than found later."""

CONNECT_DILATION_S = 10.0        # [WS8] carried unchanged

MACHINE_RPM_MARGIN = 0.98
"""[WS9-PROV] Margin against WS2 r4's carried 7,200 rpm rotor limit. WS8's
own EDRIVE_RATIO of 12.0 leaves about 2% at 105 km/h plus the driver
model's 6% downhill overspeed; a machine ratio solved to land exactly on
the limit would be a design that has no margin, and WS9 does not get to
re-rate another workstream's hardware."""


# =====================================================================
#  Corner context
# =====================================================================
class Ctx9(CD8.Ctx):
    """One corner. SUBCLASSES WS8 round 2's own `Ctx`, so every field the
    inherited objects read - `rho_air`, `t_amb_c`, `cold`, `hot`, `alt_m`,
    `derate()`, `aux_bus_kw`, `aux_mech_kw`, `payload_factor`,
    `grade_heavy`, `as_dict()` - is r2's and not WS9's.

    WS9 adds exactly two things:
      `crr`   the corner's rolling resistance, which WS8 keeps in
              `run_ws8.corner_crr` rather than on the context; WS9 puts it
              on the context so a candidate can be run without WS8's runner.
      `cab`   is built per CANDIDATE, not per corner, because R30's split
              depends on whether the candidate is electrified - see
              ws9_thermal.CabHeat.

    ACCESSORY CONVENTION. `aux_bus_kw` and `aux_mech_kw` remain r2's
    worst-case corner duties and are what the ENVELOPE is tabulated
    against. The per-sample split R30 orders - cab heat from coolant when
    an engine is running, from the bus otherwise, and battery thermal from
    a modelled pack temperature rather than a flat allowance - is applied
    inside each candidate's accounting, where the engine's state is known.
    """

    def __init__(self, name, label, **kw):
        super().__init__(name, label=label, **kw)
        self.crr = VEH.Crr * (P9.COLD_CRR_FACTOR if self.cold else 1.0)


NOMINAL = Ctx9("nominal", "20 C, sea level, nominal payload")


# =====================================================================
#  shared helpers
# =====================================================================
def _moving_average(x, n):
    return CD8._moving_average(x, n)


def spin_drag_kw(edrive, v, connected_mask, f_machine_cmd_N):
    """WS8 r2's rule and thresholds, applied to the machine's own shaft."""
    unloaded = np.abs(f_machine_cmd_N) <= SPIN_IDLE_FORCE_N
    return np.where(connected_mask & unloaded & (v > SPIN_IDLE_V_MIN_MS),
                    edrive.spin_drag_kw(v), 0.0)


def check_machine_gate(edrive, label):
    """[ESC-2] k <= 2.0 or the design changes, not the gate."""
    ok = edrive.k <= P9.MACHINE_STRETCH_GATE_K + 1e-9
    return dict(label=label, k=edrive.k, n_machines=edrive.n,
                gate_k=P9.MACHINE_STRETCH_GATE_K, passes=bool(ok),
                basis=("ESC-2 as ruled in R27: machines scaled <=2.0x from "
                       "WS2's validated range may use WS2 r4's measured "
                       "maps; beyond that a cited external HD machine basis "
                       "with the direction of error stated"))


def amt_engine_account(engine, amt, tr, f_engine_N, aux_mech_kw, whr=None,
                       overrun_allowed=True, engine_off_mask=None):
    """Fuel and shaft work for a mechanically-geared diesel through an AMT.

    TRANSCRIBED from `ws8_candidates.S0.account` (CLAUDE.md rule 10 forbids
    WS9 modifying WS8's file, so the shared core is copied here rather than
    edited there) and EXTENDED in exactly two ways:
      * the tractive force demanded OF THE ENGINE is a parameter, so a
        candidate whose traction machine takes part of the load (S7) can use
        the same engine model as the ruler rather than a second one;
      * an `engine_off_mask` lets a candidate shut the engine down.
    Everything else - gear selection, launch clutch slip, overrun fuel cut,
    the idle branch, the BSFC guard against inf*0 - is WS8's, unchanged.
    """
    v = tr["v"]
    dt = tr["dt"]
    f_trac = np.asarray(f_engine_N, float)
    moving = v > 0.1
    aux_kw = np.asarray(aux_mech_kw, float) * np.ones_like(v)

    ov = np.array([amt.overall(i) for i in range(12)])
    eta_g = np.array([amt.eta(i) for i in range(12)])
    rpm_all = v[:, None] / VEH.r_dyn * ov[None, :] * 60.0 / (2 * np.pi)
    t_cap = engine.t_max(rpm_all)
    f_avail = t_cap * ov[None, :] * eta_g[None, :] / VEH.r_dyn
    in_range = (rpm_all >= engine.idle_rpm) & (rpm_all <= 2100.0)
    usable = in_range & (rpm_all >= amt.rpm_lo)
    can = usable & (f_avail >= f_trac[:, None])

    rev = can[:, ::-1]
    any_can = rev.any(axis=1)
    gear = 11 - np.argmax(rev, axis=1)
    f_in_range = np.where(in_range, f_avail, -1.0)
    gear = np.where(any_can, gear, np.argmax(f_in_range, axis=1))

    idx = np.arange(v.size)
    eta_sel = eta_g[gear]
    ov_sel = ov[gear]

    slip = (rpm_all[:, 0] < engine.idle_rpm) & moving
    gear = np.where(slip, 0, gear)
    ov_sel = np.where(slip, ov[0], ov_sel)
    eta_sel = np.where(slip, eta_g[0], eta_sel)
    rpm = np.where(slip, amt.launch_rpm, rpm_all[idx, gear])
    rpm = np.clip(rpm, engine.idle_rpm, 2100.0)

    w_eng = rpm * 2 * np.pi / 60.0
    t_trac = f_trac * VEH.r_dyn / (ov_sel * eta_sel)
    t_aux = aux_kw * 1e3 / np.maximum(w_eng, 1e-6)
    t_tot = t_trac + t_aux

    overrun = ((f_trac <= 1.0) & moving
               & (rpm > engine.idle_rpm * 1.1)) if overrun_allowed \
        else np.zeros_like(moving)
    t_tot = np.where(overrun, 0.0, t_tot)
    t_tot = np.minimum(t_tot, engine.t_max(rpm))

    p_shaft_kw = t_tot * w_eng / 1e3
    fuelling = t_tot > 1e-6
    b = np.full(t_tot.shape, np.inf)
    if fuelling.any():
        with np.errstate(divide="ignore", invalid="ignore"):
            b[fuelling] = engine.bsfc(rpm[fuelling], t_tot[fuelling])
    g_per_s = np.zeros(t_tot.shape)
    ok = fuelling & np.isfinite(b)
    g_per_s[ok] = b[ok] * np.clip(p_shaft_kw[ok], 0, None) / 3600.0
    if whr is not None:
        phi = np.clip(t_tot / np.maximum(engine.t_max(rpm), 1e-9), 0.0, 1.0)
        g_per_s = g_per_s * (1.0 - whr.gain(phi))
    idle_g = EN8.idle_fuel_gps(engine)
    stopped = ~moving
    g_per_s = np.where(stopped, idle_g, g_per_s)
    g_per_s = np.where(overrun, 0.0, g_per_s)
    if engine_off_mask is not None:
        g_per_s = np.where(engine_off_mask, 0.0, g_per_s)
        p_shaft_kw = np.where(engine_off_mask, 0.0, p_shaft_kw)

    p_wheel_kw = f_trac * v / 1e3
    p_slip_kw = np.where(slip, np.clip(
        t_trac * w_eng / 1e3 - p_wheel_kw / eta_sel, 0.0, None), 0.0)

    # what the engine could ACTUALLY deliver in the gear it is in, and the
    # shortfall if the caller demanded more. For S0R and S6 the integrator's
    # envelope IS this force, so the shortfall is interpolation error and
    # near zero - which makes it a free self-consistency check.
    f_deliv = np.minimum(f_trac, np.max(np.where(in_range, f_avail, 0.0),
                                        axis=1))
    e_unserved_wheel = float(
        np.sum(np.clip(f_trac - f_deliv, 0.0, None) * v) * dt) / 3.6e6

    return dict(
        fuel_g=float(np.sum(g_per_s) * dt),
        f_delivered_N=f_deliv, e_unserved_wheel_kWh=e_unserved_wheel,
        g_per_s=g_per_s, rpm=rpm, gear=gear, t_tot=t_tot,
        p_shaft_kw=p_shaft_kw, overrun=overrun, moving=moving,
        e_engine_shaft_kWh=float(np.sum(p_shaft_kw) * dt) / 3600.0,
        e_clutch_slip_kWh=float(np.sum(p_slip_kw) * dt) / 3600.0,
        mean_engine_rpm_moving=float(np.mean(rpm[moving])) if moving.any()
        else 0.0,
        mean_bsfc_g_per_kWh=float(
            np.sum(g_per_s[~overrun & moving]) * 3600.0
            / max(np.sum(np.clip(p_shaft_kw[~overrun & moving], 0, None)),
                  1e-9)) if moving.any() else float("nan"),
        top_gear_fraction=float(np.mean(gear[moving] == 11)) if moving.any()
        else float("nan"),
        idle_fuel_g=float(np.sum(np.where(stopped, idle_g, 0.0)) * dt),
    )


# =====================================================================
#  S0R - the ruler (ESC-6)
# =====================================================================
class S0R(CD8.Candidate):
    """WS8's S0, plus the hydraulic retarder ESC-6 ordered, with its mass
    charged.

    WHY THIS MATTERS MORE THAN IT LOOKS. WS8's ESC-WS8-6 raised it: a ruler
    with only a compression brake must slow to about 62 km/h on the 6%
    descent while every electric candidate holds corridor speed on a
    resistor bank. That is a real architectural difference in WS8's
    specification and an artificial one in the market - a line-haul tractor
    specified for a grade-heavy regional duty is bought WITH a retarder. The
    lead ruled it in (R27, ESC-6). It moves the answer BOTH WAYS: the ruler
    loses 130 kg of payload and gains its descent speed back, and only the
    simulation can say which wins.
    """
    name = "S0R"
    title = ("Conventional 13 L diesel + 12-speed AMT with a direct top "
             "gear, + hydraulic retarder (ESC-6)")
    policy = (
        "AMT selects the highest gear that can deliver the demanded wheel "
        "force above 1,050 rpm; launch on a slipping clutch at 1,200 rpm "
        "with the slip heat charged; overrun fuel cut-off when the wheels "
        "drive the engine; accessories crank-driven; cab heat from engine "
        "coolant, free. DESCENT: the hydraulic retarder is the primary "
        "auxiliary brake and takes the duty first (which is how a "
        "retarder-equipped truck is actually driven, and is the "
        "conservative direction for the coolant circuit in the heat "
        "ledger), the compression brake takes what is left, then the "
        "declared continuous friction allowance.")
    ENGINE_KEY = "ENG-13L"
    P_ENGINE_BRAKE_KW = 290.0
    electrified = False
    predictive = False

    def setup(self):
        self.engine_base = self._base_engine()
        self.engine = E9.derated(self.engine_base, self.ctx)
        self.amt = EN8.AMT(self.engine, r_dyn=VEH.r_dyn)
        self.p_engine_brake_kw = self.P_ENGINE_BRAKE_KW
        self.ret = P9.RET
        self._ret_exp, self._ret_knee_rpm = self._retarder_law()
        self.cab = CabHeat(P9.TH, self.ctx.t_amb_c, self.electrified)

    def _base_engine(self):
        return EN8.ENGINES[self.ENGINE_KEY]

    # ---------------------------------------------------------- retarder
    def _retarder_law(self):
        """Fit the three PUBLISHED torque points on a power law in shaft
        speed and find the speed at which it reaches the published maximum.
        [WS9-CITED VOLVO_RET_TH] - the shape is the manufacturer's, not
        WS9's."""
        r = self.ret
        exp = (np.log(r.t_at_750rpm_Nm / r.t_at_500rpm_Nm)
               / np.log(750.0 / 500.0))
        knee = 750.0 * (r.t_max_propshaft_Nm / r.t_at_750rpm_Nm) ** (1.0 / exp)
        return float(exp), float(knee)

    def prop_rpm(self, v):
        return v / VEH.r_dyn * self.amt.AXLE * 60.0 / (2 * np.pi)

    def retarder_torque_Nm(self, n_prop):
        n = np.asarray(n_prop, float)
        t = self.ret.t_at_500rpm_Nm * np.power(np.maximum(n, 1e-9) / 500.0,
                                               self._ret_exp)
        return np.minimum(t, self.ret.t_max_propshaft_Nm)

    def retarder_force_N(self, v):
        """Wheel-side retarding force, capped by the declared continuous
        (cooling-package-limited) rating."""
        v = np.asarray(v, float)
        t = self.retarder_torque_Nm(self.prop_rpm(v))
        f = t * self.amt.AXLE * DL.eta_axle_tandem * DL.eta_driveshaft \
            / VEH.r_dyn
        f_p = self.ret.p_continuous_kW * 1e3 / np.maximum(v, 0.5)
        return np.minimum(f, f_p) * (v > 0.5)

    def engine_brake_force_N(self, v):
        return self.amt.engine_brake_force(v, self.p_engine_brake_kw)

    # -------------------------------------------------------------- mass
    def engine_row_name(self):
        return "engine_%s_wet" % self.ENGINE_KEY.replace("ENG-", "").lower()

    def aftertreatment_kg(self):
        return ML.m_aftertreatment

    def mass_rows(self):
        return {
            self.engine_row_name(): self.engine_base.mass_kg,
            "aftertreatment": self.aftertreatment_kg(),
            "amt_12sp": ML.m_amt_12sp,
            "hydraulic_retarder": self.ret.mass_kg,
            "driveshafts": ML.m_driveshafts,
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        if v < 6.0:
            return VEH.lam_rot_launch
        if v < 15.0:
            return 0.5 * (VEH.lam_rot_launch + VEH.lam_rot_direct)
        return VEH.lam_rot_direct

    def envelope(self, v):
        f_t = min(self.amt.max_wheel_force(v), self.adhesion_force_N())
        f_ret = float(self.retarder_force_N(v)) + self.engine_brake_force_N(v)
        return f_t, 0.0, min(f_ret, self.adhesion_force_N())

    # -------------------------------------------------------- accounting
    def account(self, tr):
        v = tr["v"]
        dt = tr["dt"]
        aux_mech = np.where(v > 0.1,
                            self.ctx.aux_mech_kw + self.cab.mech_extra_kw(),
                            AUX.p_hotel_idle_kW)
        r = amt_engine_account(self.engine, self.amt, tr, tr["F_trac"],
                               aux_mech, whr=self.whr)
        # retarder first, compression brake second (declared in `policy`)
        f_ret_cap = self.retarder_force_N(v)
        f_ret = np.minimum(tr["F_retard"], f_ret_cap)
        f_eb = np.clip(tr["F_retard"] - f_ret, 0.0, None)
        return dict(
            fuel_g=r["fuel_g"], e_fuel_MJ=EN8.fuel_energy_MJ(r["fuel_g"]),
            e_engine_shaft_kWh=r["e_engine_shaft_kWh"],
            e_wheel_tractive_kWh=float(
                np.sum(np.clip(tr["F_trac"] * v, 0, None)) * dt) / 3.6e6,
            e_engine_wheel_kWh=float(
                np.sum(np.clip(r["f_delivered_N"] * v, 0, None))
                * dt) / 3.6e6,
            e_aux_kWh=float(np.sum(aux_mech) * dt) / 3600.0,
            e_clutch_slip_kWh=r["e_clutch_slip_kWh"],
            e_regen_bus_kWh=0.0, e_resistor_kWh=0.0, e_spin_kWh=0.0,
            e_engine_brake_kWh=float(np.sum(f_eb * v) * dt) / 3.6e6,
            e_hydraulic_retarder_kWh=float(np.sum(f_ret * v) * dt) / 3.6e6,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v) * dt) / 3.6e6,
            retarder_peak_kW=float(np.max(f_ret * v)) / 1e3,
            engine_brake_peak_kW=float(np.max(f_eb * v)) / 1e3,
            friction_brake_peak_kW=float(
                np.max(tr["F_friction"] * v)) / 1e3,
            resistor_peak_kW=0.0,
            unserved_kWh=r["e_unserved_wheel_kWh"], shed_kWh=0.0,
            soc_start=0.0, soc_end=0.0,
            grid_kWh=0.0,
            mean_engine_rpm_moving=r["mean_engine_rpm_moving"],
            mean_bsfc_g_per_kWh=r["mean_bsfc_g_per_kWh"],
            top_gear_fraction=r["top_gear_fraction"],
            idle_fuel_g=r["idle_fuel_g"],
            eta_machine_bus_to_wheel_duty=1.0,
        )

    def spec(self):
        s = CD8.Candidate.spec(self)
        s["engine"] = dict(
            name=self.engine_base.name, label=self.engine_base.label,
            peak_power_kW=self.engine_base.peak_power_kw(),
            island_bsfc_g_per_kWh=self.engine_base.min_bsfc_point()["bsfc"],
            derate_applied=self.ctx.derate())
        s["retarder"] = dict(
            **{k: getattr(self.ret, k) for k in
               ("t_max_propshaft_Nm", "p_continuous_kW",
                "mass_installed_kg", "mass_cooling_delta_kg",
                "heat_destination")},
            mass_charged_kg=self.ret.mass_kg,
            torque_law_exponent=self._ret_exp,
            torque_law_knee_rpm=self._ret_knee_rpm,
            force_at_90kmh_N=float(self.retarder_force_N(25.0)),
            force_at_50kmh_N=float(self.retarder_force_N(13.889)))
        s["predictive_energy_management"] = self.predictive
        s["electrified"] = self.electrified
        s["cab_heat"] = self.cab.record()
        return s


# =====================================================================
#  S6 - the zero-mass stack
# =====================================================================
class S6(S0R):
    """Mechanical drive as S0R, an opposed-piston-class engine on a cited
    efficiency basis, and predictive energy management.

    S6 IS MASS-NEUTRAL WITH THE RULER, to the kilogram: the same AMT, the
    same retarder, the same axles, the same fuel, the same aftertreatment
    (the cited document states the engine needs only a conventional one-box
    underfloor system), and an engine charged at the four-stroke's mass
    because the source states none. Its payload is therefore EXACTLY the
    ruler's, and on a metric that divides by payload its margin is exactly
    its fuel margin. That is the whole point of the candidate: it is the
    control for "how far without electrification", and it is the only
    candidate in this trial that pays no payload tax at all.

    PREDICTIVE ENERGY MANAGEMENT is applied to the DEMAND TRACE, not to the
    accounting - see ws9_duty.apply_predictive(). It costs no mass and its
    saving is whatever the simulation gives."""
    name = "S6"
    title = ("Zero-mass stack - opposed-piston-class engine + predictive "
             "energy management, mechanical drive as S0")
    policy = (
        "Driveline, retarder, axles and aftertreatment identical to the "
        "ruler - S6 is mass-neutral with S0R to the kilogram. The engine is "
        "an opposed-piston-class unit whose island BSFC is solved to a "
        "CITED peak brake thermal efficiency of 49.2%, with NO other credit "
        "taken from the source (see ws9_engines.WHAT_WS9_DOES_NOT_TAKE). "
        "Predictive energy management modifies the DEMANDED SPEED with "
        "route preview - slowing before a crest, building speed before a "
        "climb, within a declared +/-6% band, renormalised so the mean "
        "demanded speed is unchanged - so the saving is energy management "
        "and not a speed reduction in disguise.")
    predictive = True

    def _base_engine(self):
        return E9.ENG_OP

    def engine_row_name(self):
        return "engine_opposed_piston_wet"

    def aftertreatment_kg(self):
        return E9.OP_AFTERTREATMENT_KG


class S0R_PCC(S0R):
    """The RULER with predictive energy management fitted.

    WHY THIS EXISTS AND WHY IT IS NOT OPTIONAL. Predictive energy management
    is a ZERO-MASS lever. D8 says zero-mass levers first. A zero-mass lever
    can be fitted to the INCUMBENT as easily as to S6, and if it is, S6's
    margin loses whatever the lever was worth. Reporting S6-with-preview
    against a ruler-without-preview would be comparing two different control
    strategies and calling the difference an engine. So WS9 measures the
    lever on the ruler as well and reports both. Informative bracket at the
    nominal corner; escalated to the lead as ESC-WS9-5 because whether the
    ruler is specified with preview is a baseline-specification decision."""
    name = "S0R-PCC"
    title = "The ruler with predictive energy management (zero-mass bracket)"
    predictive = True


class S6ETC(S6):
    """S6 with electric turbocompound fitted. R31: admitted to S6 ONLY if
    it clears the same 2.5% net gate ON THE DESIGN DUTY, whose load fraction
    is higher than the fleet average WS8 tested against. The gate is
    pre-committed and this class exists to be measured against it, not to
    be adopted."""
    name = "S6-ETC"
    title = "Zero-mass stack + electric turbocompound (gate candidate)"


# =====================================================================
#  S5 - minimal transmission: the 2-speed dog box
# =====================================================================
class S5(CD8.Candidate):
    """2-speed dog box: no synchronisers, no launch clutch, no power-shift.

    LAYOUT. Engine -> dog box -> propshaft -> tandem axle, with the traction
    machine geared to the PROPSHAFT, downstream of the shifting element.
    That position is what makes "torque-fill through the shift" physically
    possible: during a shift the engine's torque path opens while the
    machine's does not, so the machine holds wheel torque while the engine
    is speed-matched to the new ratio and the dogs re-engage. A machine on
    the gearbox INPUT would be leaner (it would launch through the low
    ratio) but could not fill through the shift, because it would be on the
    wrong side of the element that opens. That trade is reported as the
    S5-P2 bracket rather than argued about.

    THE TWO WALLS, addressed BY CONSTRUCTION (ws9_walls.solve_two_speed):
      WALL 1  the high ratio is solved so the engine stays under its
              over-speed ceiling at 105 km/h - closed form, not a swept grid
      WALL 2  the low ratio is solved so the engine's peak torque puts the
              6% grade force at the contact patch at GCW, with a declared
              margin
      and a third constraint that a 2-speed lives or dies by: CONTIGUITY,
      the ratio step may not exceed rpm_ceiling / rpm_lug, or there is a
      band of road speed in which the engine has no gear at all.

    A RESULT THAT FALLS OUT OF THAT ALGEBRA AND IS WORTH STATING BEFORE ANY
    SIMULATION: with contiguity tight and Wall 2 tight,

        cruise engine speed  x  engine peak torque  =  constant

    at fixed GCW and grade requirement. A minimal transmission therefore
    wants a BIG-TORQUE engine, because torque is what buys back the ratio
    span - which inverts the usual downsizing instinct and is the reason
    WS9 runs S5 on two engines.

    NO LAUNCH DEVICE ON THE ENGINE SIDE. Below the low gear's coupling floor
    the dogs are open and the engine is OFF; the machine launches. This is
    S3's fault-limp asymmetry inherited in a milder form - reported, and
    escalated, not hidden."""
    name = "S5"
    title = ("Minimal transmission - 2-speed dog box, motor-synchronised "
             "shifts, torque-fill through the shift")
    policy = (
        "Below the low gear's coupling floor the dogs are open, the engine "
        "is OFF and the machine launches the combination from the buffer. "
        "Above it the engine drives through whichever ratio is legal and "
        "the machine fills torque through shifts, assists on transients, "
        "regenerates on braking, and is back-driven by the engine to "
        "restore the buffer whenever the engine's load fraction is below "
        "its BSFC-optimal load and the buffer is under target. Shifts are "
        "dog engagements with the ENGINE speed-matched; each is charged its "
        "torque-fill energy. Descent: regen to the buffer up to its "
        "acceptance AT THE PACK'S ACTUAL TEMPERATURE, then the compression "
        "brake, then the resistor, then the declared friction allowance. "
        "Spin drag charged by the one WS9 rule whenever the machine is "
        "connected and unloaded; the disconnect is open otherwise and its "
        "mass is charged.")

    ENGINE_KEY = "ENG-11L"
    P_ENGINE_BRAKE_KW = 240.0
    MACHINE_AT_INPUT = False        # True in the S5-P2 bracket
    GRADE_TARGET = 0.06
    """The grade the low ratio is solved against. 6% is the ASSIGNMENT's
    wall ("the two ratios must span cruise-under-rpm-ceiling and the 6%
    grade at GCW") and is what S5 and S5-13L are built to. The S5-GH
    bracket asks the obvious next question - what if the low ratio were
    solved against the grade the DESIGN DUTY actually carries - and the
    frontier in ws9_walls.two_speed_frontier says what that costs."""
    electrified = True
    predictive = False
    N_MACHINES = 2

    def setup(self):
        self.engine_base = EN8.ENGINES[self.ENGINE_KEY]
        self.engine = E9.derated(self.engine_base, self.ctx)
        self.p_engine_brake_kw = self.P_ENGINE_BRAKE_KW
        self.box = P9.DOGBOX
        self.eta_high = (DL.eta_amt_direct * DL.eta_axle_tandem
                         * DL.eta_driveshaft)
        self.eta_low = (DL.eta_amt_indirect * DL.eta_axle_tandem
                        * DL.eta_driveshaft)
        self.walls = W9.solve_two_speed(
            self.engine_base, 105.0 / 3.6, self.box.rpm_ceiling,
            self.box.rpm_lug_floor, self.eta_high, self.eta_low,
            grade=self.GRADE_TARGET, m=VEH.m_gcw, rho_air=VEH.rho_air,
            margin=P9.S5_GRADE_MARGIN,
            contiguity_margin=self.box.contiguity_margin)
        self.r_high = self.walls["ratio_high"]
        self.r_low = self.walls["ratio_low"]
        self.v_couple_floor = (self.box.rpm_lug_floor
                               / (self.r_low * W9.RPM_PER_RATIO_PER_MS))
        self.v_shift = (self.box.rpm_lug_floor
                        / (self.r_high * W9.RPM_PER_RATIO_PER_MS))

        # ---- traction machine, sized by the regulatory start -----------
        if self.MACHINE_AT_INPUT:
            # geared through the box, so it launches on the LOW ratio;
            # its own reduction is capped by WS2's carried rotor limit at
            # the top of the demand band plus the downhill overspeed.
            rpm_eng_at_vmax = (105.0 / 3.6) * self.r_high \
                * W9.RPM_PER_RATIO_PER_MS
            # 2% inside WS2 r4's carried 7,200 rpm rotor limit at the top
            # of the demand band plus the driver model's 6% downhill
            # overspeed - the same margin WS8's EDRIVE_RATIO = 12.0 leaves.
            r_m = (MACHINE_RPM_MARGIN * EL8.ScaledEDrive.RPM_MAX_WS2
                   / (1.06 * rpm_eng_at_vmax))
            self.machine_ratio_launch = r_m * self.r_low
            self.machine_ratio_cruise = r_m * self.r_high
            eta_m_launch = DL.eta_edrive_reduction * self.eta_low
            k = (CD8.startability_force_N() * VEH.r_dyn
                 / (self.machine_ratio_launch * eta_m_launch)
                 / (self.N_MACHINES * EL8.ScaledEDrive.T_PEAK_WS2_NM))
            # The machine is UPSTREAM of the shifting element, so its
            # overall ratio to the road CHANGES WITH THE GEAR. That is the
            # whole benefit of the position - it launches on the low ratio,
            # which is why k is half what the P3 layout needs - and it has
            # to be modelled with two ratios, not one, or the bracket is
            # not a bracket but a mistake.
            self.edrive = EL8.ScaledEDrive(
                k, self.machine_ratio_cruise, n_machines=self.N_MACHINES,
                label="S5 machine on the gearbox INPUT (P2), HIGH gear")
            self.edrive_low = EL8.ScaledEDrive(
                k, self.machine_ratio_launch, n_machines=self.N_MACHINES,
                label="S5 machine on the gearbox INPUT (P2), LOW gear")
            self.machine_rpm_check = dict(
                r_m=r_m,
                rpm_high_at_105kmh=float(
                    self.edrive.motor_rpm(105.0 / 3.6)),
                rpm_high_at_105kmh_plus_overspeed=float(
                    self.edrive.motor_rpm(1.06 * 105.0 / 3.6)),
                rpm_low_at_shift_speed=float(
                    self.edrive_low.motor_rpm(
                        self.box.rpm_lug_floor
                        / (self.r_high * W9.RPM_PER_RATIO_PER_MS))),
                rpm_max_ws2=EL8.ScaledEDrive.RPM_MAX_WS2)
            self.machine_rpm_check["ok"] = bool(
                max(self.machine_rpm_check[
                        "rpm_high_at_105kmh_plus_overspeed"],
                    self.machine_rpm_check["rpm_low_at_shift_speed"])
                <= EL8.ScaledEDrive.RPM_MAX_WS2)
        else:
            self.machine_ratio_launch = EDRIVE_RATIO
            self.machine_ratio_cruise = EDRIVE_RATIO
            k = CD8.size_edrive_for_startability(EDRIVE_RATIO,
                                                 self.N_MACHINES)
            self.edrive = EL8.ScaledEDrive(
                k, EDRIVE_RATIO, n_machines=self.N_MACHINES,
                label="S5 machine on the gearbox OUTPUT (P3), torque-fill "
                      "capable")
            self.edrive_low = self.edrive
            self.machine_rpm_check = dict(
                r_m=EDRIVE_RATIO,
                rpm_high_at_105kmh=float(
                    self.edrive.motor_rpm(105.0 / 3.6)),
                rpm_high_at_105kmh_plus_overspeed=float(
                    self.edrive.motor_rpm(1.06 * 105.0 / 3.6)),
                rpm_low_at_shift_speed=float(
                    self.edrive.motor_rpm(105.0 / 3.6)),
                rpm_max_ws2=EL8.ScaledEDrive.RPM_MAX_WS2,
                ok=True)
        self.machine_gate = check_machine_gate(self.edrive, self.name)

        # ---- buffer, sized by the two declared rules -------------------
        p_launch_wheel = ST9.launch_power_kW(
            self.v_couple_floor, P9.S5_LAUNCH_ACCEL_MS2, rho_air=VEH.rho_air)
        p_launch_bus = p_launch_wheel / 0.90 + self.ctx.aux_bus_kw
        e_launch = ST9.launch_energy_kWh(self.v_couple_floor,
                                         P9.S5_LAUNCH_ACCEL_MS2,
                                         rho_air=VEH.rho_air) / 0.90
        e_stop = ST9.braking_energy_from_speed_kWh(100.0 / 3.6) * 0.90
        self.pack, self.pack_sizing = ST9.size_buffer(
            P9.BUFFER_CELL, p_launch_bus, e_launch + e_stop,
            label="S5 buffer")
        self.pack_sizing["launch_power_wheel_kW"] = p_launch_wheel
        self.pack_sizing["launch_energy_bus_kWh"] = e_launch
        self.pack_sizing["one_stop_from_100kmh_bus_kWh"] = e_stop
        self.pack_bracket = ST9.buffer_chemistry_bracket(self.pack)

        # ---- resistor, sized by the pack-saturated descent case ---------
        f_eb_90 = self._engine_brake_force_N(25.0)
        self.resistor_kw, self.resistor_sizing = ST9.size_resistor_kW(
            f_eb_90, 25.0, -0.06, rho_air=VEH.rho_air,
            friction_allowance_kW=FRICTION_ALLOWANCE_KW)

        self.cab = CabHeat(P9.TH, self.ctx.t_amb_c, self.electrified)

    # ------------------------------------------------------------ gears
    def _machine_in_low(self, v):
        """Which ratio the machine sees. In the P3 layout the machine is
        downstream of the box and its ratio never changes; in P2 it follows
        the box, which is in LOW below the shift speed."""
        v = np.asarray(v, float)
        if not self.MACHINE_AT_INPUT:
            return np.zeros_like(v, dtype=bool)
        return v < self.v_shift

    def _machine_wheel_force_max(self, v):
        v = np.asarray(v, float)
        hi = self.edrive.wheel_force_max(v)
        if not self.MACHINE_AT_INPUT:
            return hi
        lo = self.edrive_low.wheel_force_max(v)
        return np.where(self._machine_in_low(v), lo, hi)

    def _machine_eta_bus_to_wheel(self, v, p_kw):
        hi = self.edrive.eta_bus_to_wheel(v, p_kw)
        if not self.MACHINE_AT_INPUT:
            return hi
        lo = self.edrive_low.eta_bus_to_wheel(v, p_kw)
        return np.where(self._machine_in_low(v), lo, hi)

    def _machine_eta_wheel_to_bus(self, v, p_kw):
        hi = self.edrive.eta_wheel_to_bus(v, p_kw)
        if not self.MACHINE_AT_INPUT:
            return hi
        lo = self.edrive_low.eta_wheel_to_bus(v, p_kw)
        return np.where(self._machine_in_low(v), lo, hi)

    def _machine_spin_kw(self, v):
        hi = self.edrive.spin_drag_kw(v)
        if not self.MACHINE_AT_INPUT:
            return hi
        lo = self.edrive_low.spin_drag_kw(v)
        return np.where(self._machine_in_low(v), lo, hi)

    def _gear_of(self, v):
        """0 = low, 1 = high, -1 = no engine gear (dogs open)."""
        v = np.asarray(v, float)
        rpm_l = v * self.r_low * W9.RPM_PER_RATIO_PER_MS
        rpm_h = v * self.r_high * W9.RPM_PER_RATIO_PER_MS
        low_ok = (rpm_l >= self.box.rpm_lug_floor) & \
                 (rpm_l <= self.box.rpm_ceiling)
        high_ok = (rpm_h >= self.box.rpm_lug_floor) & \
                  (rpm_h <= self.box.rpm_ceiling)
        # prefer HIGH wherever it is legal (lower engine speed, better BSFC)
        return np.where(high_ok, 1, np.where(low_ok, 0, -1))

    def _engine_force_N(self, v):
        g = self._gear_of(v)
        v = np.asarray(v, float)
        out = np.zeros_like(v)
        for gi, (R, eta) in enumerate(((self.r_low, self.eta_low),
                                       (self.r_high, self.eta_high))):
            m = g == gi
            if not np.any(m):
                continue
            rpm = np.clip(v[m] * R * W9.RPM_PER_RATIO_PER_MS,
                          self.engine.idle_rpm, self.box.rpm_ceiling)
            out[m] = self.engine.t_max(rpm) * R * eta / VEH.r_dyn
        return out

    def _engine_rpm(self, v):
        g = self._gear_of(v)
        v = np.asarray(v, float)
        rpm = np.zeros_like(v)
        rpm = np.where(g == 0, v * self.r_low * W9.RPM_PER_RATIO_PER_MS, rpm)
        rpm = np.where(g == 1, v * self.r_high * W9.RPM_PER_RATIO_PER_MS, rpm)
        return rpm

    def _engine_brake_force_N(self, v):
        """Compression brake through whichever gear is legal, at the engine
        speed that gear imposes - the same rating law WS8's AMT uses."""
        v = np.asarray(v, float)
        rpm = self._engine_rpm(v)
        ok = (rpm > 0) & (rpm <= EN8.AMT.RPM_BRAKE_MAX)
        p = np.where(ok, self.p_engine_brake_kw * rpm
                     / EN8.AMT.RPM_BRAKE_RATED, 0.0)
        return p * 1e3 / np.maximum(v, 0.5) * (v > 0.5)

    # ------------------------------------------------------------- mass
    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "engine_%s_wet" % self.ENGINE_KEY.replace("ENG-", "").lower():
                self.engine_base.mass_kg,
            "aftertreatment": ML.m_aftertreatment,
            "two_speed_dog_box": self.box.mass_kg,
            "driveshafts": ML.m_driveshafts,
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "traction_motors": em["motor_kg"],
            "inverters": em["inverter_kg"],
            "motor_reduction_stages": em["reduction_kg"],
            "traction_disconnect": 42.0,
            "brake_resistor": EL8.resistor_mass_kg(self.resistor_kw),
            "buffer_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal,
            "pack_precondition_and_cab_heat_path": P9.TH.mass_kg,
            "fuel": ML.m_fuel_full,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh
                * (P9.BUFFER_SOC_TARGET - P9.BUFFER_SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def envelope(self, v):
        f_eng = float(self._engine_force_N(np.array([v]))[0])
        f_m = float(self._machine_wheel_force_max(np.array([v]))[0])
        ed_v = (self.edrive_low if (self.MACHINE_AT_INPUT
                                    and v < self.v_shift) else self.edrive)
        if v > 0.5:
            # Below the coupling floor the machine is the only prime mover
            # and the buffer is sized for exactly that duty, so it may use
            # its CONTINUOUS rating. Above it the engine is available and
            # the machine's SUSTAINED contribution is the 15-minute swing
            # (WS8's SUSTAINED_CLIMB_S rule, carried unchanged) - a buffer
            # cannot climb a mountain and is not asked to.
            p_cap = (self.pack.p_cont_dis_kw if v < self.v_couple_floor
                     else self.pack_sustained_kw()) - self.ctx.aux_bus_kw
            if p_cap > 0.0:
                eta = float(ed_v.eta_bus_to_wheel(
                    v, min(p_cap, ed_v.wheel_power_max_kw(v))))
                f_m = min(f_m, p_cap * eta * 1e3 / v)
            else:
                f_m = 0.0
        f_t = min(f_eng + f_m, self.adhesion_force_N())

        f_gen = min(float(self._machine_wheel_force_max(np.array([v]))[0]),
                    self.adhesion_force_N())
        if v > 0.5:
            blend = CD8.regen_blend(v)
            # the envelope grants regen at the PRECONDITIONED acceptance
            # (R30 makes preconditioning a requirement); the dispatch then
            # enforces the pack's ACTUAL temperature and moves whatever the
            # pack refuses to the resistor, which is where it physically
            # goes. The retarding FORCE is the same either way, so the
            # achieved speed is unaffected and only the heat moves.
            f_regen = min(f_gen, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_res = min(max(0.0, f_gen - f_regen),
                        self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_res = 0.0
        f_eb = float(self._engine_brake_force_N(np.array([v]))[0])
        return f_t, f_regen, min(f_res + f_eb, self.adhesion_force_N())

    # ------------------------------------------------------- accounting
    def account(self, tr):
        v = tr["v"]
        dt = tr["dt"]
        n = v.size
        h = dt / 3600.0
        moving = v > 0.1

        gear = self._gear_of(v)
        coupled = (gear >= 0) & moving
        f_eng_cap = self._engine_force_N(v)
        f_eng_cap = np.where(coupled, f_eng_cap, 0.0)
        f_eng = np.minimum(tr["F_trac"], f_eng_cap)
        f_m = np.clip(tr["F_trac"] - f_eng, 0.0, None)

        # --- shift detection and its two charges ------------------------
        shifts = np.flatnonzero(np.diff(gear) != 0)
        shifts = shifts[(gear[shifts] >= 0) & (gear[shifts + 1] >= 0)]
        n_shifts = int(shifts.size)
        e_fill_kWh = 0.0
        e_shift_interrupt_kWh = 0.0
        if n_shifts:
            f_at = tr["F_trac"][shifts]
            v_at = v[shifts]
            if self.MACHINE_AT_INPUT:
                # the machine is on the wrong side of the element that
                # opens: the shift is a TORQUE INTERRUPTION, and the work
                # not done has to be done later
                e_shift_interrupt_kWh = float(
                    np.sum(f_at * v_at) * self.box.shift_time_s) / 3.6e6
            else:
                # torque-fill: the machine holds wheel torque through the
                # shift, out of the buffer
                e_fill_kWh = float(
                    np.sum(f_at * v_at) * self.box.shift_time_s) / 3.6e6 / 0.90

        # --- machine bus flows ------------------------------------------
        p_m_wheel = f_m * v / 1e3
        eta_m = self._machine_eta_bus_to_wheel(v, p_m_wheel)
        p_m_bus = np.where(p_m_wheel > 0, p_m_wheel / eta_m, 0.0)
        p_rg_wheel = tr["F_regen"] * v / 1e3
        eta_g = self._machine_eta_wheel_to_bus(v, p_rg_wheel)
        p_rg_bus = p_rg_wheel * eta_g

        # retard channel: compression brake FIRST (free, no consumable),
        # then the resistor. Split here so the heat ledger books each to
        # its own physical location.  [R2-IMPL F1]
        f_eb_cap = self._engine_brake_force_N(v) * (gear >= 0)
        f_eb = np.minimum(tr["F_retard"], f_eb_cap)
        f_res = np.clip(tr["F_retard"] - f_eb, 0.0, None)
        p_res_wheel = f_res * v / 1e3
        p_res_bus_raw = p_res_wheel * self._machine_eta_wheel_to_bus(
            v, p_res_wheel)
        # THE RESISTOR MAY NOT EXCEED THE RATING WHOSE MASS WAS CHARGED.
        # The envelope caps the resistor's WHEEL force at rating/v and is
        # then tabulated on a 0.05 m/s grid and interpolated; near the gear
        # band boundary, where the compression brake appears and disappears
        # discontinuously, the interpolated retard channel can hand the
        # accounting slightly more than the resistor can physically take.
        # It is clipped here and the excess is recorded as a RETARDING
        # SHORTFALL rather than absorbed - which is finding F1(d) applied
        # to WS9's own export before an adjudicator has to find it.
        p_res_bus = np.minimum(p_res_bus_raw, self.resistor_kw)
        e_res_over_rating = float(np.sum(p_res_bus_raw - p_res_bus)) * h

        # --- machine connection state and the one spin rule -------------
        w = max(1, int(round(CONNECT_DILATION_S / dt)))
        busy = (f_m > 1.0) | (tr["F_regen"] > 1.0) | (p_res_wheel > 0.1)
        connected = _moving_average(busy.astype(float), w) > 1e-9
        f_machine_cmd = f_m + tr["F_regen"] + f_res
        p_spin = np.where(
            connected & (np.abs(f_machine_cmd) <= SPIN_IDLE_FORCE_N)
            & (v > SPIN_IDLE_V_MIN_MS), self._machine_spin_kw(v), 0.0)

        # --- through-the-driveline charging headroom --------------------
        # The machine sits on the propshaft, so the engine can back-drive
        # it through the box WITHOUT going through the tyres: this is a
        # driveline path, not S3's through-the-road path, and it is the
        # reason S5 can keep its buffer full without a generator.
        f_head = np.clip(f_eng_cap - f_eng, 0.0, None)
        f_head = np.minimum(f_head, self._machine_wheel_force_max(v))
        p_chg_head_bus = f_head * v / 1e3 * eta_g

        rpm_e = np.clip(self._engine_rpm(v), self.engine.idle_rpm,
                        self.box.rpm_ceiling)
        t_cap = self.engine.t_max(rpm_e)
        load_frac = np.where(coupled,
                             f_eng / np.maximum(f_eng_cap, 1e-9), 0.0)

        # --- the sequential loop: SOC, pack temperature, charging -------
        th = PackThermal(self.pack, P9.TH, self.ctx.t_amb_c)
        usable = max(self.pack.usable_kwh, 1e-9)
        e = usable * P9.BUFFER_SOC_TARGET
        e_lo = usable * P9.BUFFER_SOC_FLOOR
        e_hi = usable * P9.BUFFER_SOC_CEIL
        soc = np.empty(n)
        f_chg_wheel = np.zeros(n)
        p_heater = np.zeros(n)
        p_res_extra = np.zeros(n)
        unserved = 0.0
        regen_to_resistor = 0.0
        retard_shortfall = e_res_over_rating
        aux_bus = np.zeros(n)
        engine_on_prev = False
        n_restarts = 0

        aux_base = np.where(moving, AUX.p_aux_bus_avg_kW,
                            AUX.p_hotel_idle_kW)
        for i in range(n):
            engine_on = bool(coupled[i])
            if engine_on and not engine_on_prev:
                n_restarts += 1
            extra = self.cab.bus_extra_kw(engine_on)
            heat_kw = th.step(dt, p_m_bus[i] + p_rg_bus[i], engine_on)
            p_heater[i] = heat_kw
            aux_bus[i] = aux_base[i] + extra + heat_kw

            chg = 0.0
            if engine_on and (e / usable) < P9.BUFFER_SOC_TARGET \
                    and p_chg_head_bus[i] > 0.0 and load_frac[i] < 0.72:
                want = (self.pack.p_cont_chg_kw
                        * (P9.BUFFER_SOC_TARGET - e / usable)
                        / (P9.BUFFER_SOC_TARGET - P9.BUFFER_SOC_FLOOR))
                chg = min(want, p_chg_head_bus[i])

            demand = p_m_bus[i] + aux_bus[i] + p_spin[i] - p_rg_bus[i]
            net = demand - chg
            chg_lim = th.chg_limit_kw()
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
                surplus = -net
                pc = min(surplus, chg_lim)
                de = pc * h * self.pack.eta_chg
                room = e_hi - e
                if de > room:
                    pc = room / self.pack.eta_chg / h if h > 0 else 0.0
                    de = max(room, 0.0)
                e += de
                over = surplus - pc
                if over > 0.0:
                    # first give back the charging the engine was doing
                    give = min(over, chg)
                    chg -= give
                    over -= give
                if over > 0.0:
                    # then move refused regen to the resistor, up to its
                    # rating; anything past that is a genuine retarding
                    # shortfall and is recorded, not absorbed
                    head = max(0.0, self.resistor_kw - p_res_bus[i])
                    take = min(over, head)
                    p_res_extra[i] = take
                    regen_to_resistor += take * h
                    retard_shortfall += (over - take) * h
            f_chg_wheel[i] = (chg / max(eta_g[i], 1e-6) * 1e3
                              / max(v[i], 0.5)) if chg > 0 else 0.0
            soc[i] = e / usable
            engine_on_prev = engine_on

        # --- engine fuel -------------------------------------------------
        t_eng = ((f_eng + f_chg_wheel) * VEH.r_dyn
                 / np.where(gear == 1, self.r_high * self.eta_high,
                            np.where(gear == 0,
                                     self.r_low * self.eta_low, 1.0)))
        t_eng = np.minimum(np.where(coupled, t_eng, 0.0), t_cap)
        w_eng = rpm_e * 2 * np.pi / 60.0
        p_shaft = t_eng * w_eng / 1e3
        fuelling = coupled & (t_eng > 1e-6)
        b = np.full(n, np.inf)
        if fuelling.any():
            with np.errstate(divide="ignore", invalid="ignore"):
                b[fuelling] = self.engine.bsfc(rpm_e[fuelling],
                                               t_eng[fuelling])
        g = np.zeros(n)
        okf = fuelling & np.isfinite(b)
        g[okf] = b[okf] * np.clip(p_shaft[okf], 0, None) / 3600.0
        if self.whr is not None:
            phi = np.clip(t_eng / np.maximum(t_cap, 1e-9), 0.0, 1.0)
            g = g * (1.0 - self.whr.gain(phi))
        fuel_g = float(np.sum(g) * dt)

        e_wheel_trac = float(
            np.sum(np.clip(tr["F_trac"] * v, 0, None)) * dt) / 3.6e6
        e_m_bus = float(np.sum(p_m_bus)) * h
        e_m_wheel = float(np.sum(np.clip(p_m_wheel, 0, None))) * h
        eta_m_duty = e_m_wheel / e_m_bus if e_m_bus > 1e-9 else 0.90

        return dict(
            fuel_g=fuel_g, e_fuel_MJ=EN8.fuel_energy_MJ(fuel_g),
            e_engine_shaft_kWh=float(np.sum(p_shaft)) * h,
            e_wheel_tractive_kWh=e_wheel_trac,
            e_engine_wheel_kWh=float(np.sum(f_eng * v)) * dt / 3.6e6,
            e_machine_wheel_kWh=e_m_wheel,
            e_bus_traction_kWh=e_m_bus,
            e_driveline_charge_bus_kWh=float(
                np.sum(f_chg_wheel * v)) * dt / 3.6e6,
            e_aux_kWh=float(np.sum(aux_bus)) * h,
            e_pack_heater_kWh=float(np.sum(p_heater)) * h,
            e_spin_kWh=float(np.sum(p_spin)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg_bus)) * h,
            e_resistor_kWh=(float(np.sum(p_res_bus)) * h
                            + regen_to_resistor),
            e_regen_moved_to_resistor_kWh=regen_to_resistor,
            e_retard_shortfall_kWh=retard_shortfall,
            e_engine_brake_kWh=float(np.sum(f_eb * v)) * dt / 3.6e6,
            e_hydraulic_retarder_kWh=0.0,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v)) * dt / 3.6e6,
            e_torque_fill_kWh=e_fill_kWh,
            e_shift_interruption_kWh=e_shift_interrupt_kWh,
            e_clutch_slip_kWh=0.0,
            n_shifts=n_shifts, n_engine_restarts=n_restarts,
            coupled_fraction_moving=float(np.mean(coupled[moving]))
            if moving.any() else 0.0,
            high_gear_fraction_coupled=float(
                np.mean(gear[coupled] == 1)) if coupled.any() else 0.0,
            machine_connected_fraction_moving=float(
                np.mean(connected[moving])) if moving.any() else 0.0,
            unserved_kWh=unserved, shed_kWh=0.0, grid_kWh=0.0,
            soc_min=float(np.min(soc)), soc_max=float(np.max(soc)),
            soc_start=P9.BUFFER_SOC_TARGET, soc_end=float(soc[-1]),
            resistor_peak_kW=float(np.max(p_res_bus + p_res_extra)),
            engine_brake_peak_kW=float(np.max(f_eb * v)) / 1e3,
            retarder_peak_kW=0.0,
            friction_brake_peak_kW=float(np.max(tr["F_friction"] * v)) / 1e3,
            mean_engine_rpm_moving=float(np.mean(rpm_e[coupled]))
            if coupled.any() else 0.0,
            mean_bsfc_g_per_kWh=float(np.sum(g[okf]) * 3600.0
                                      / max(np.sum(p_shaft[okf]), 1e-9))
            if okf.any() else float("nan"),
            top_gear_fraction=float("nan"),
            idle_fuel_g=0.0,
            eta_machine_bus_to_wheel_duty=eta_m_duty,
            pack_thermal=th.record(),
        )

    def spec(self):
        s = CD8.Candidate.spec(self)
        s["engine"] = dict(
            name=self.engine_base.name, label=self.engine_base.label,
            peak_power_kW=self.engine_base.peak_power_kw(),
            peak_torque_Nm=float(np.max(self.engine_base.trq_pts)),
            island_bsfc_g_per_kWh=self.engine_base.min_bsfc_point()["bsfc"],
            derate_applied=self.ctx.derate())
        s["two_walls"] = self.walls
        s["gearbox"] = dict(
            type="2-speed dog box: no synchronisers, no launch clutch, no "
                 "power-shift",
            ratio_high_overall=self.r_high, ratio_low_overall=self.r_low,
            box_low_step=self.walls["box_low_ratio"],
            axle_ratio=self.walls["axle_ratio"],
            eta_high=self.eta_high, eta_low=self.eta_low,
            mass_kg=self.box.mass_kg,
            shift_speed_kmh=self.v_shift * 3.6,
            coupling_floor_kmh=self.v_couple_floor * 3.6,
            machine_position=("gearbox INPUT (P2) - no torque-fill through "
                              "the shift" if self.MACHINE_AT_INPUT else
                              "gearbox OUTPUT (P3) - torque-fill through "
                              "the shift"))
        s["edrive"] = self.edrive.spec()
        if self.MACHINE_AT_INPUT:
            s["edrive_low_gear"] = self.edrive_low.spec()
        s["machine_rpm_check"] = self.machine_rpm_check
        s["machine_gate_ESC2"] = self.machine_gate
        s["pack"] = self.pack.spec()
        s["pack_sizing_rule"] = self.pack_sizing
        s["pack_chemistry_bracket"] = self.pack_bracket
        s["resistor_sizing_rule"] = self.resistor_sizing
        s["electrified"] = self.electrified
        s["predictive_energy_management"] = self.predictive
        s["cab_heat"] = self.cab.record()
        return s


class S5_13L(S5):
    name = "S5-13L"
    title = ("Minimal transmission with the 13 L engine - the other end of "
             "the ratio law")
    ENGINE_KEY = "ENG-13L"
    P_ENGINE_BRAKE_KW = 290.0


class S5_GH(S5_13L):
    """The obvious next question, asked rather than left to the reader.

    S5 and S5-13L are built to the ASSIGNMENT's 6% wall. The DESIGN DUTY
    R29 specifies carries grades of 7.9-10.7%, and ws9_walls's frontier says
    a 2-speed may have the steep grade OR a contiguous engine band, not
    both, beyond a grade that depends entirely on the engine's peak torque:
    6% for the 11 L, 8% for the 13 L. S5-GH is the 13 L design solved
    against 8% instead of 6% - the steepest a contiguous 2-speed can carry
    on this engine - and it pays for the capability in cruise engine speed,
    which is the ratio law charging its bill.

    Informative bracket at the nominal corner. It is NOT the ordered
    candidate and it does not carry a verdict."""
    name = "S5-GH"
    title = ("Minimal transmission solved against the DESIGN DUTY's grade "
             "(8%) rather than the assignment's 6%")
    GRADE_TARGET = 0.08


class S5_P2(S5):
    name = "S5-P2"
    title = ("Minimal transmission, machine on the gearbox INPUT - leaner, "
             "but the shift becomes a torque interruption")
    MACHINE_AT_INPUT = True
    N_MACHINES = 1


# =====================================================================
#  S7 - marginal-mass electrification of an existing trailer axle
# =====================================================================
class S7(S0R):
    """The tractor is the RULER, untouched: same engine, same AMT, same
    retarder, same axles. One axle of the EXISTING trailer tandem is
    motorised.

    "no new axle" is read as: the combination does not gain an axle. It is
    NOT read as: the hardware that turns a dead beam into a driven axle is
    free - the assignment's next clause is "Charge everything", so the
    carrier delta, the disconnect, the tractor-trailer HV interface and the
    longer cabling are all in the ledger.

    SIZING RULE, stated: the machine is sized to the buffer's 10-second
    PULSE charge acceptance at the control duty's corridor speed. There is
    no point buying machine beyond what the buffer can absorb, and no point
    buying buffer beyond one service stop - which is the whole content of
    the phrase "marginal-mass electrification"."""
    name = "S7"
    title = ("Marginal-mass electrification - one EXISTING trailer axle "
             "motorised, tractor untouched")
    policy = (
        "The tractor drives exactly as the ruler does and is never told "
        "anything. The trailer machine assists whenever the tractor's "
        "demanded wheel force exceeds what the engine can deliver in the "
        "gear it is in, and otherwise takes a declared share of the "
        "tractive demand while the buffer is above its floor; it "
        "regenerates on every braking event up to the buffer's acceptance "
        "AT THE PACK'S ACTUAL TEMPERATURE. It has a disconnect and its mass "
        "is charged; spin drag is charged by the one WS9 rule whenever it "
        "is connected and unloaded. There is no resistor: the tractor's "
        "retarder and compression brake own the descent, which is the "
        "point of leaving the tractor untouched.")
    electrified = True
    ASSIST_SHARE = 0.35
    """[WS9-PROV] Fraction of the tractive demand the trailer machine takes
    while the buffer is above its floor and the machine is inside its
    envelope. Chosen, and declared, because an overlay product with no
    access to the tractor's engine controller cannot know the engine's
    operating point: it can only follow wheel torque. A larger share would
    empty a 10 kWh buffer in minutes; a smaller one would not be worth the
    mass. Reported as a sensitivity rather than defended."""

    def setup(self):
        S0R.setup(self)
        self.pack, self.pack_sizing = ST9.size_buffer(
            P9.BUFFER_CELL,
            0.0,                       # power is not the binding rule here
            ST9.braking_energy_from_speed_kWh(90.0 / 3.6) * 0.90,
            label="S7 trailer buffer")
        self.pack_sizing["one_stop_from_90kmh_bus_kWh"] = \
            ST9.braking_energy_from_speed_kWh(90.0 / 3.6) * 0.90
        self.pack_bracket = ST9.buffer_chemistry_bracket(self.pack)
        v_ref = 90.0 / 3.6
        f_target = self.pack.p_pulse_chg_kw * 1e3 / v_ref / 0.93
        k = f_target * VEH.r_dyn / (EDRIVE_RATIO * DL.eta_edrive_reduction
                                    * EL8.ScaledEDrive.T_PEAK_WS2_NM)
        self.edrive = EL8.ScaledEDrive(
            k, EDRIVE_RATIO, n_machines=1, label="S7 trailer e-axle")
        self.machine_gate = check_machine_gate(self.edrive, self.name)
        self.machine_sizing = dict(
            rule="sized to the buffer's 10-second PULSE charge acceptance "
                 "at the control duty's corridor speed",
            v_ref_kmh=90.0, pack_pulse_chg_kW=self.pack.p_pulse_chg_kw,
            target_wheel_force_N=f_target, k=k,
            eta_wheel_to_bus_assumed=0.93)
        self.cab = CabHeat(P9.TH, self.ctx.t_amb_c, self.electrified)

    def adhesion_trailer_axle_N(self, mu=None):
        mu = ADH.mu_dry if mu is None else mu
        return mu * VEH.m_axle_trailer_tandem_kg * TRL_SHARE * G

    def mass_rows(self):
        rows = S0R.mass_rows(self)
        em = self.edrive.mass_kg()
        rows.update({
            "trailer_axle_carrier_delta": P9.TRL.m_carrier_delta_kg,
            "trailer_traction_motor": em["motor_kg"],
            "trailer_inverter": em["inverter_kg"],
            "trailer_motor_reduction": em["reduction_kg"],
            "trailer_eaxle_disconnect": P9.TRL.m_disconnect_kg,
            "trailer_hv_interface": P9.TRL.m_trailer_hv_interface_kg,
            "buffer_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling * 1.6,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal,
            "pack_precondition_and_cab_heat_path": P9.TH.mass_kg,
        })
        return rows

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh
                * (P9.BUFFER_SOC_TARGET - P9.BUFFER_SOC_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def envelope(self, v):
        f_t, _, f_ret = S0R.envelope(self, v)
        f_m = self.edrive.wheel_force_max(v)
        f_m = min(f_m, self.adhesion_trailer_axle_N())
        if v > 0.5:
            p_cap = self.pack_sustained_kw() - self.ctx.aux_bus_kw
            if p_cap > 0.0:
                eta = float(self.edrive.eta_bus_to_wheel(
                    v, min(p_cap, self.edrive.wheel_power_max_kw(v))))
                f_m = min(f_m, p_cap * eta * 1e3 / v)
            else:
                f_m = 0.0
        f_regen = 0.0
        if v > 0.5:
            blend = CD8.regen_blend(v)
            f_regen = min(self.edrive.wheel_force_max(v),
                          self.adhesion_trailer_axle_N(),
                          self.pack.p_cont_chg_kw * 1e3 / v) * blend
        return (min(f_t + f_m, self.adhesion_force_N()
                    + self.adhesion_trailer_axle_N()),
                f_regen, f_ret)

    def account(self, tr):
        v = tr["v"]
        dt = tr["dt"]
        n = v.size
        h = dt / 3600.0
        moving = v > 0.1

        f_m_env = np.minimum(self.edrive.wheel_force_max(v),
                             self.adhesion_trailer_axle_N())
        f_m_want = np.minimum(tr["F_trac"] * self.ASSIST_SHARE, f_m_env)
        p_m_wheel = f_m_want * v / 1e3
        eta_m = self.edrive.eta_bus_to_wheel(v, p_m_wheel)
        p_m_bus = np.where(p_m_wheel > 0, p_m_wheel / eta_m, 0.0)
        p_rg_wheel = tr["F_regen"] * v / 1e3
        eta_g = self.edrive.eta_wheel_to_bus(v, p_rg_wheel)
        p_rg_bus = p_rg_wheel * eta_g

        w = max(1, int(round(CONNECT_DILATION_S / dt)))
        busy = (f_m_want > 1.0) | (tr["F_regen"] > 1.0)
        connected = _moving_average(busy.astype(float), w) > 1e-9
        f_machine_cmd = f_m_want + tr["F_regen"]
        p_spin = spin_drag_kw(self.edrive, v, connected, f_machine_cmd)

        th = PackThermal(self.pack, P9.TH, self.ctx.t_amb_c)
        usable = max(self.pack.usable_kwh, 1e-9)
        e = usable * P9.BUFFER_SOC_TARGET
        e_lo = usable * P9.BUFFER_SOC_FLOOR
        e_hi = usable * P9.BUFFER_SOC_CEIL
        soc = np.empty(n)
        f_m = np.zeros(n)
        p_m_served = np.zeros(n)
        p_heater = np.zeros(n)
        aux_bus = np.zeros(n)
        unserved_assist = 0.0
        regen_refused = 0.0
        aux_base = np.where(moving, AUX.p_aux_bus_avg_kW,
                            AUX.p_hotel_idle_kW)
        for i in range(n):
            engine_on = bool(moving[i])          # the tractor engine runs
            extra = self.cab.bus_extra_kw(engine_on)
            heat_kw = th.step(dt, p_m_bus[i] + p_rg_bus[i], engine_on)
            p_heater[i] = heat_kw
            # NOTE: the base accessory duty stays on the TRACTOR's crank -
            # the tractor is untouched - so only the R30 terms and the
            # trailer's own losses are bus-side here.
            aux_bus[i] = extra + heat_kw
            want = p_m_bus[i] + aux_bus[i] + p_spin[i] - p_rg_bus[i]
            if want > 0.0:
                pd = min(want, self.pack.p_cont_dis_kw)
                de = pd * h / self.pack.eta_dis
                room = e - e_lo
                if de > room:
                    pd = room * self.pack.eta_dis / h if h > 0 else 0.0
                    de = max(room, 0.0)
                e -= de
                # the trailer's own bus loads are served first; whatever is
                # left is assist, and what the pack could not feed is simply
                # not delivered - the tractor's engine picks it up
                deliv_bus = max(0.0, pd - aux_bus[i] - p_spin[i]
                                + p_rg_bus[i])
                served_bus = (min(deliv_bus, p_m_bus[i])
                              if p_m_bus[i] > 0 else 0.0)
                p_m_served[i] = served_bus
                f_m[i] = (served_bus * eta_m[i] * 1e3
                          / max(v[i], 0.5)) if served_bus > 0 else 0.0
                unserved_assist += max(0.0, want - pd) * h
            else:
                surplus = -want
                pc = min(surplus, th.chg_limit_kw())
                de = pc * h * self.pack.eta_chg
                room = e_hi - e
                if de > room:
                    pc = room / self.pack.eta_chg / h if h > 0 else 0.0
                    de = max(room, 0.0)
                e += de
                regen_refused += (surplus - pc) * h
                f_m[i] = 0.0
            soc[i] = e / usable

        # the tractor engine carries whatever the trailer did not
        f_eng = np.clip(tr["F_trac"] - f_m, 0.0, None)
        aux_mech = np.where(moving,
                            self.ctx.aux_mech_kw + self.cab.mech_extra_kw(),
                            AUX.p_hotel_idle_kW)
        r = amt_engine_account(self.engine, self.amt, tr, f_eng, aux_mech,
                               whr=self.whr)

        f_ret_cap = self.retarder_force_N(v)
        f_ret = np.minimum(tr["F_retard"], f_ret_cap)
        f_eb = np.clip(tr["F_retard"] - f_ret, 0.0, None)

        e_m_bus = float(np.sum(p_m_served)) * h
        e_m_bus_wanted = float(np.sum(p_m_bus)) * h
        e_m_wheel = float(np.sum(np.clip(f_m * v / 1e3, 0, None))) * h
        eta_m_duty = e_m_wheel / e_m_bus if e_m_bus > 1e-9 else 0.90

        return dict(
            fuel_g=r["fuel_g"], e_fuel_MJ=EN8.fuel_energy_MJ(r["fuel_g"]),
            e_engine_shaft_kWh=r["e_engine_shaft_kWh"],
            e_wheel_tractive_kWh=float(
                np.sum(np.clip(tr["F_trac"] * v, 0, None)) * dt) / 3.6e6,
            e_engine_wheel_kWh=float(
                np.sum(np.clip(r["f_delivered_N"] * v, 0, None))
                * dt) / 3.6e6,
            e_machine_wheel_kWh=e_m_wheel,
            e_bus_traction_kWh=e_m_bus,
            e_bus_traction_requested_kWh=e_m_bus_wanted,
            e_aux_kWh=float(np.sum(aux_mech) * dt) / 3600.0
            + float(np.sum(aux_bus)) * h,
            e_pack_heater_kWh=float(np.sum(p_heater)) * h,
            e_spin_kWh=float(np.sum(p_spin)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg_bus)) * h,
            e_regen_refused_kWh=regen_refused,
            e_resistor_kWh=0.0,
            e_engine_brake_kWh=float(np.sum(f_eb * v)) * dt / 3.6e6,
            e_hydraulic_retarder_kWh=float(
                np.sum(f_ret * v)) * dt / 3.6e6,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v)) * dt / 3.6e6,
            e_clutch_slip_kWh=r["e_clutch_slip_kWh"],
            unserved_kWh=r["e_unserved_wheel_kWh"],
            e_assist_not_delivered_kWh=unserved_assist,
            shed_kWh=0.0, grid_kWh=0.0,
            soc_min=float(np.min(soc)), soc_max=float(np.max(soc)),
            soc_start=P9.BUFFER_SOC_TARGET, soc_end=float(soc[-1]),
            assist_fraction_of_tractive=float(
                np.sum(f_m * v) / max(np.sum(np.clip(tr["F_trac"] * v,
                                                     0, None)), 1e-9)),
            machine_connected_fraction_moving=float(
                np.mean(connected[moving])) if moving.any() else 0.0,
            resistor_peak_kW=0.0,
            retarder_peak_kW=float(np.max(f_ret * v)) / 1e3,
            engine_brake_peak_kW=float(np.max(f_eb * v)) / 1e3,
            friction_brake_peak_kW=float(np.max(tr["F_friction"] * v)) / 1e3,
            mean_engine_rpm_moving=r["mean_engine_rpm_moving"],
            mean_bsfc_g_per_kWh=r["mean_bsfc_g_per_kWh"],
            top_gear_fraction=r["top_gear_fraction"],
            idle_fuel_g=r["idle_fuel_g"],
            eta_machine_bus_to_wheel_duty=eta_m_duty,
            pack_thermal=th.record(),
        )

    def spec(self):
        s = S0R.spec(self)
        s["edrive"] = self.edrive.spec()
        s["machine_gate_ESC2"] = self.machine_gate
        s["machine_sizing_rule"] = self.machine_sizing
        s["pack"] = self.pack.spec()
        s["pack_sizing_rule"] = self.pack_sizing
        s["pack_chemistry_bracket"] = self.pack_bracket
        s["assist_share"] = self.ASSIST_SHARE
        s["trailer_axle"] = dict(
            axle_load_kg=VEH.m_axle_trailer_tandem_kg * TRL_SHARE,
            adhesion_dry_N=self.adhesion_trailer_axle_N(),
            carrier_delta_kg=P9.TRL.m_carrier_delta_kg)
        s["electrified"] = self.electrified
        s["cab_heat"] = self.cab.record()
        return s


# =====================================================================
#  S4' - range-extended BEV re-posed (ESC-1c + ESC-3)
# =====================================================================
class S4p(CD8.Candidate):
    """WS8's S4, re-posed on the two things the lead ruled.

    ESC-1(c): the pack is built on a CITED EXTERNAL energy-optimised cell as
    an explicitly non-WS3 bracket. Same nameplate as WS8's S4 (150 kWh), so
    the bracket is the ONLY change to the pack and the effect is isolated.

    ESC-3: S4' is judged as what it is - a PLUG-IN. It starts full, runs
    CHARGE-DEPLETING until the pack reaches its floor and CHARGE-SUSTAINING
    thereafter, and the grid energy it consumed enters the metric of record
    as PRIMARY ENERGY at a declared factor, with a CO2 second lens and a
    +/-50% factor sensitivity. WS8 had to run it charge-sustaining because
    the metric could not see electricity; it now can, and that is the
    difference between judging the architecture and judging the accounting.
    """
    name = "S4p"
    title = ("Range-extended BEV re-posed - cited external energy cell "
             "(ESC-1c), electricity term (ESC-3)")
    policy = (
        "Electric traction only. The pack starts at its plug-in ceiling and "
        "the sustainer stays OFF while the pack is above its charge-"
        "depleting floor; below it the sustainer holds charge on the "
        "engine's BSFC-optimal locus with start-stop hysteresis. The grid "
        "energy consumed is metered as the state-of-charge the mission "
        "actually spent and is charged at a declared primary-energy factor "
        "and CO2 intensity, both swept +/-50%. Descent braking: regen to "
        "the pack up to its acceptance AT THE PACK'S ACTUAL TEMPERATURE, "
        "then the resistor, then friction. Pack preconditioning is served "
        "from the sustainer's coolant when it is running and from an "
        "electric heater when it is not - which, for a candidate whose "
        "engine is off most of the mission, is the cold wall's sharpest "
        "edge and is modelled rather than assumed.")

    PACK_KWH = 150.0
    PLUG_IN = True
    SOC_CD_START = 0.95
    SOC_CD_FLOOR = 0.15
    SOC_CS_TARGET = 0.20
    electrified = True
    predictive = False

    def setup(self):
        self.engine_base = EN8.ENG_7L
        self.engine = E9.derated(self.engine_base, self.ctx)
        self.rating = E9.prp_rated_cont_kw(self.engine_base)
        self.sustainer_shaft_kw = self.rating["prp_kW"] * self.ctx.derate()
        self.generator, _ = EL8.scaled_generator("GEN-S4p",
                                                 self.sustainer_shaft_kw)
        self.pack = ST9.CitedPack(self.PACK_KWH,
                                  label="S4' traction pack (ESC-1c)")
        self.line = CD8.GensetLine(self.engine, self.generator,
                                   self.generator.cont_kw_in * 0.955)
        k = CD8.size_edrive_for_startability(EDRIVE_RATIO, 2)
        self.edrive = EL8.ScaledEDrive(k, EDRIVE_RATIO, n_machines=2,
                                       label="S4' tandem e-drive")
        self.machine_gate = check_machine_gate(self.edrive, self.name)
        f_none = 0.0
        self.resistor_kw, self.resistor_sizing = ST9.size_resistor_kW(
            f_none, 25.0, -0.06, rho_air=VEH.rho_air,
            friction_allowance_kW=FRICTION_ALLOWANCE_KW)
        self.cab = CabHeat(P9.TH, self.ctx.t_amb_c, self.electrified)

    def mass_rows(self):
        em = self.edrive.mass_kg()
        return {
            "sustainer_engine_wet": self.engine_base.mass_kg,
            "aftertreatment": 90.0,
            "generator": self.generator.mass_kg,
            "traction_motors": em["motor_kg"],
            "inverters": em["inverter_kg"],
            "motor_reduction_stages": em["reduction_kg"],
            "drive_axle_gearsets": ML.m_drive_axle_gearsets_tandem,
            "driveshafts": ML.m_driveshafts,
            "brake_resistor": EL8.resistor_mass_kg(self.resistor_kw),
            "traction_pack": self.pack.mass_kg,
            "hv_cabling": ML.m_hv_cabling,
            "contactors_precharge": ML.m_contactors_precharge,
            "hv_misc_bms_thermal": ML.m_hv_misc_bms_thermal + 60.0,
            "pack_precondition_and_cab_heat_path": P9.TH.mass_kg,
            "fuel": ML.m_fuel_small,
        }

    def lam(self, v):
        return VEH.lam_rot_edrive

    def pack_sustained_kw(self):
        return (self.pack.usable_kwh * (self.SOC_CD_START - self.SOC_CD_FLOOR)
                / (SUSTAINED_CLIMB_S / 3600.0))

    def envelope(self, v):
        f_t = self.edrive.wheel_force_max(v)
        p_bus_cap = (self.line.p_elec_max_kw
                     + min(self.pack.p_cont_dis_kw, self.pack_sustained_kw())
                     - self.ctx.aux_bus_kw)
        if v > 0.5:
            eta = float(self.edrive.eta_bus_to_wheel(
                v, min(p_bus_cap, self.edrive.wheel_power_max_kw(v))))
            f_t = min(f_t, p_bus_cap * eta * 1e3 / v)
        f_t = min(f_t, self.adhesion_force_N())
        f_gen = min(self.edrive.wheel_force_max(v), self.adhesion_force_N())
        if v > 0.5:
            blend = CD8.regen_blend(v)
            f_regen = min(f_gen, self.pack.p_cont_chg_kw * 1e3 / v) * blend
            f_res = min(max(0.0, f_gen - f_regen),
                        self.resistor_kw * 1e3 / v) * blend
        else:
            f_regen = f_res = 0.0
        return f_t, f_regen, f_res

    def account(self, tr):
        v = tr["v"]
        dt = tr["dt"]
        n = v.size
        h = dt / 3600.0
        moving = v > 0.1
        p_t, p_rg, p_rx_raw, _ = CD8.series_bus_demand(
            self.edrive, tr, np.zeros_like(v), count_spin=False)
        # the resistor may not exceed the rating whose mass was charged
        p_rx = np.minimum(p_rx_raw, self.resistor_kw)
        e_res_over_rating = float(np.sum(p_rx_raw - p_rx)) * h
        # S4' is permanently geared: no disconnect, so `connected` is
        # always true and the machine pays the tax whenever it is unloaded.
        p_spin = spin_drag_kw(self.edrive, v,
                              np.ones_like(v, dtype=bool),
                              tr["F_trac"] + tr["F_regen"] + tr["F_retard"])

        th = PackThermal(self.pack, P9.TH, self.ctx.t_amb_c)
        usable = max(self.pack.usable_kwh, 1e-9)
        e = usable * self.SOC_CD_START
        e_lo = usable * 0.05
        e_hi = usable * self.SOC_CD_START
        soc = np.empty(n)
        p_gen = np.zeros(n)
        p_heater = np.zeros(n)
        p_res_extra = np.zeros(n)
        aux_bus = np.zeros(n)
        unserved = 0.0
        regen_to_resistor = 0.0
        retard_shortfall = e_res_over_rating
        starts = 0
        on = False
        n_smooth = max(1, int(round(180.0 / dt)))
        pre = np.clip(_moving_average(p_t + p_spin, n_smooth), 0.0,
                      self.line.p_elec_max_kw)
        aux_base = np.where(moving, AUX.p_aux_bus_avg_kW,
                            AUX.p_hotel_idle_kW)
        for i in range(n):
            soc_now = e / usable
            extra = self.cab.bus_extra_kw(on)
            heat_kw = th.step(dt, p_t[i] + p_rg[i], on)
            p_heater[i] = heat_kw
            aux_bus[i] = aux_base[i] + extra + heat_kw

            if soc_now > self.SOC_CD_FLOOR:
                p_ref = 0.0                      # CHARGE-DEPLETING
            else:                                # CHARGE-SUSTAINING
                p_ref = pre[i] + 260.0 * (self.SOC_CS_TARGET - soc_now)
                p_ref = float(np.clip(p_ref, 0.0, self.line.p_elec_max_kw))
            if on:
                if p_ref < 15.0:
                    on = False
            else:
                if p_ref > 25.0:
                    on = True
                    starts += 1
            p = p_ref if on else 0.0

            net = p_t[i] + aux_bus[i] + p_spin[i] - p_rg[i] - p
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
                surplus = -net
                pc = min(surplus, th.chg_limit_kw())
                de = pc * h * self.pack.eta_chg
                room = e_hi - e
                if de > room:
                    pc = room / self.pack.eta_chg / h if h > 0 else 0.0
                    de = max(room, 0.0)
                e += de
                over = surplus - pc
                if over > 0.0:
                    cut = min(over, p)
                    p -= cut
                    over -= cut
                if over > 0.0:
                    head = max(0.0, self.resistor_kw - p_rx[i])
                    take = min(over, head)
                    p_res_extra[i] = take
                    regen_to_resistor += take * h
                    retard_shortfall += (over - take) * h
            p_gen[i] = p
            soc[i] = e / usable

        fuel_g = float(np.sum(self.line.fuel_whr(p_gen, self.whr)) * dt)
        e_m_bus = float(np.sum(p_t)) * h
        e_m_wheel = float(
            np.sum(np.clip(tr["F_trac"] * v, 0, None)) * dt) / 3.6e6
        eta_m_duty = e_m_wheel / e_m_bus if e_m_bus > 1e-9 else 0.90
        soc_spent = self.SOC_CD_START - float(soc[-1])
        grid_kwh = max(0.0, soc_spent) * usable / P9.EA.eta_charge_grid_to_pack

        return dict(
            fuel_g=fuel_g, e_fuel_MJ=EN8.fuel_energy_MJ(fuel_g),
            e_bus_traction_kWh=e_m_bus,
            e_wheel_tractive_kWh=e_m_wheel,
            e_engine_wheel_kWh=0.0,
            e_genset_bus_kWh=float(np.sum(p_gen)) * h,
            e_aux_kWh=float(np.sum(aux_bus)) * h,
            e_pack_heater_kWh=float(np.sum(p_heater)) * h,
            e_spin_kWh=float(np.sum(p_spin)) * h,
            e_regen_bus_kWh=float(np.sum(p_rg)) * h,
            e_resistor_kWh=float(np.sum(p_rx)) * h + regen_to_resistor,
            e_regen_moved_to_resistor_kWh=regen_to_resistor,
            e_retard_shortfall_kWh=retard_shortfall,
            e_engine_brake_kWh=0.0, e_hydraulic_retarder_kWh=0.0,
            e_friction_brake_kWh=float(
                np.sum(tr["F_friction"] * v)) * dt / 3.6e6,
            e_clutch_slip_kWh=0.0,
            genset_starts=starts,
            genset_on_fraction=float(np.mean(p_gen > 0.0)),
            p_genset_mean_on_kW=(float(np.mean(p_gen[p_gen > 0.0]))
                                 if (p_gen > 0.0).any() else 0.0),
            unserved_kWh=unserved, shed_kWh=0.0,
            soc_min=float(np.min(soc)), soc_max=float(np.max(soc)),
            soc_start=self.SOC_CD_START, soc_end=float(soc[-1]),
            soc_spent=soc_spent,
            grid_kWh=grid_kwh,
            charge_depleting_fraction=float(
                np.mean(soc > self.SOC_CD_FLOOR)),
            resistor_peak_kW=float(np.max(p_rx + p_res_extra)),
            retarder_peak_kW=0.0, engine_brake_peak_kW=0.0,
            friction_brake_peak_kW=float(np.max(tr["F_friction"] * v)) / 1e3,
            mean_bsfc_g_per_kWh=float("nan"),
            top_gear_fraction=float("nan"),
            idle_fuel_g=0.0,
            eta_machine_bus_to_wheel_duty=eta_m_duty,
            pack_thermal=th.record(),
        )

    def spec(self):
        s = CD8.Candidate.spec(self)
        s["engine"] = dict(
            name=self.engine_base.name, label=self.engine_base.label,
            peak_power_kW=self.engine_base.peak_power_kw(),
            island_bsfc_g_per_kWh=self.engine_base.min_bsfc_point()["bsfc"],
            derate_applied=self.ctx.derate())
        s["sustainer_rating_ESC4"] = dict(
            **self.rating, shaft_kW_used=self.sustainer_shaft_kw,
            bus_kW_max=self.line.p_elec_max_kw)
        s["edrive"] = self.edrive.spec()
        s["machine_gate_ESC2"] = self.machine_gate
        s["pack"] = self.pack.spec()
        s["resistor_sizing_rule"] = self.resistor_sizing
        s["plug_in_policy"] = dict(
            soc_charge_depleting_start=self.SOC_CD_START,
            soc_charge_depleting_floor=self.SOC_CD_FLOOR,
            soc_charge_sustaining_target=self.SOC_CS_TARGET,
            basis="ESC-3 as ruled in R27: the metric acquires an "
                  "electricity term for a plug-in candidate")
        s["electrified"] = self.electrified
        s["predictive_energy_management"] = self.predictive
        s["cab_heat"] = self.cab.record()
        return s


CANDIDATES = {
    "S0R": S0R, "S5": S5, "S5-13L": S5_13L, "S5-P2": S5_P2,
    "S6": S6, "S6-ETC": S6ETC, "S7": S7, "S4p": S4p,
    "S0R-PCC": S0R_PCC, "S5-GH": S5_GH,
}

FULL_SET = ("S0R", "S5", "S5-13L", "S6", "S7", "S4p")
BRACKET_SET = ("S5-P2", "S5-GH", "S6-ETC", "S0R-PCC")
RULER = "S0R"
