"""
Project Volt - WS8
Electric traction, generation and storage at semi scale.

EVERYTHING here is scaled from Vehicle Zero's MEASURED or RULED exports,
read-only (CLAUDE.md rule 10), under the scaling law declared once in
ws8_params.Scaling and applied nowhere else:

  traction machine + inverter : WS2 r4 measured loss map
                                (data/effmap_motor_inverter_662V.csv,
                                 4,203 feasible cells) via WS4's RULED
                                loader WS2TractionChain, then stretched
  generator + active rectifier: WS4's PMGenerator loss model, stretched
  battery                     : WS3's cell definitions and pack overhead
  brake resistor              : WS2's element-limited resistor, stretched

R12 CHAIN CONVENTION (inherited, not re-litigated): the traction side is
the WS2 measured inverter+motor map times the 0.97 reduction, with NO
scalar PE member; the genset-side rectifier/conditioning stage lives in
the generator model. Every electrical quantity below is BUS-SIDE
(CLAUDE.md rule 6).
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS2_DIR = os.path.join(_HERE, "..", "WS2_traction_motor")
_WS3_DIR = os.path.join(_HERE, "..", "WS3_battery")
_WS4_DIR = os.path.join(_HERE, "..", "WS4_genset")
for _d in (_WS4_DIR, _WS3_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from ws4_chain import WS2TractionChain, load_ws2_exports   # noqa: E402
from ws4_models import PMGenerator                          # noqa: E402
from ws3_cells import CELLS                                 # noqa: E402
from ws3_pack import (MASS_OVERHEAD_FACTOR,                 # noqa: E402
                      MASS_OVERHEAD_FIXED_KG)

from ws8_params import DL, SC, VEH                          # noqa: E402


# ---------------------------------------------------------------------
# WS2's loss surface is identical for every machine WS8 builds - only the
# stretch factor differs - and rebuilding it means re-reading a 5,475-row
# CSV and re-running the nearest-neighbour dilation fill. It is therefore
# loaded once and shared. The cache is keyed on the arguments that would
# change the surface, so it cannot silently serve the wrong map.
# ---------------------------------------------------------------------
_CHAIN_CACHE = {}
_EXPORT_CACHE = {}
_CAP_CACHE = {}


def _ws2_exports():
    if "e" not in _EXPORT_CACHE:
        _EXPORT_CACHE["e"] = load_ws2_exports(_WS2_DIR)
    return _EXPORT_CACHE["e"]


def _ws2_chain(map_path, ratio, r_dyn, eta_red):
    key = (map_path, round(ratio, 9), round(r_dyn, 9), round(eta_red, 9))
    if key not in _CHAIN_CACHE:
        _CHAIN_CACHE[key] = WS2TractionChain(map_path, ratio, r_dyn, eta_red)
    return _CHAIN_CACHE[key]


def _ws2_capability():
    if "c" not in _CAP_CACHE:
        _CAP_CACHE["c"] = np.genfromtxt(
            os.path.join(_WS2_DIR, "data", "capability_vs_rpm.csv"),
            delimiter=",", names=True)
    return _CAP_CACHE["c"]


# =====================================================================
#  Traction machine: WS2 r4, axially stretched
# =====================================================================
class ScaledEDrive:
    """WS2's VM250-HV stretched by factor k, driving through `ratio`.

    THE LAW (ws8_params.Scaling, restated here where it is applied):
        T(k)        = k * T_ws2
        loss(k;n,T) = k * loss_ws2(n, T/k)
        mass(k)     = k * m_active + m_fixed
    The speed axis is untouched: an axial stretch does not move the
    field-weakening boundary or rpm_max, so the machine keeps WS2's
    7,200 rpm ceiling and that ceiling sets the maximum reduction ratio
    the drive may use at 105 km/h. That constraint is CHECKED, not
    assumed (see `check_ratio`).
    """

    # WS2 r4 exports, read-only
    M_MOTOR_WS2_KG = 96.0
    M_MOTOR_END_WS2_KG = 18.0      # ws2_params.py: "non-stack mass (ends,
                                   # shaft, bearings) for scaling"
    M_INVERTER_WS2_KG = 16.0
    M_REDUCTION_WS2_KG = 32.0
    T_PEAK_WS2_NM = 529.5          # data/capability_vs_rpm.csv, 662 V
    T_CONT_WS2_NM = 515.1          # continuous-electrical, 662 V
    RPM_MAX_WS2 = 7200.0

    def __init__(self, k, ratio, r_dyn=None, n_machines=1,
                 eta_red=None, label=""):
        self.k = float(k)
        self.ratio = float(ratio)
        self.r_dyn = VEH.r_dyn if r_dyn is None else float(r_dyn)
        self.n = int(n_machines)
        self.eta_red = DL.eta_edrive_reduction if eta_red is None \
            else float(eta_red)
        self.label = label
        exp = _ws2_exports()
        self.ws2_map_file = exp["map_file_rel"]
        self.ws2_map_voltage_V = exp["map_voltage_V"]
        self.ws2_rework_round = exp["ws2_rework_round"]
        self.ws2_bus_nominal_V = exp["ws2_bus_nominal_V"]
        # The chain is constructed at WS8's OWN ratio and radius; only
        # the loss surface comes from WS2.
        self._chain = _ws2_chain(exp["map_path"], self.ratio,
                                 self.r_dyn, self.eta_red)
        self.n_feasible_cells = self._chain.n_feasible
        # capability envelope vs rpm, WS2 r4 measured
        cap = _ws2_capability()
        self._cap_rpm = np.asarray(cap["rpm"], float)
        self._cap_tpk = np.asarray(cap["T_peak_662V_Nm"], float)
        self._cap_tct = np.asarray(cap["T_contelec_662V_Nm"], float)

    # ---------------------------------------------------------- geometry
    def motor_rpm(self, v):
        return np.asarray(v, float) / self.r_dyn * self.ratio * 60.0 \
            / (2 * np.pi)

    def check_ratio(self, v_max_ms):
        """rpm at the top of the speed band vs WS2's carried rpm_max."""
        rpm = float(self.motor_rpm(v_max_ms))
        return dict(rpm_at_v_max=rpm, rpm_max=self.RPM_MAX_WS2,
                    ok=bool(rpm <= self.RPM_MAX_WS2),
                    headroom_frac=1.0 - rpm / self.RPM_MAX_WS2)

    # -------------------------------------------------------- capability
    def t_peak_motor(self, rpm):
        """Per-machine peak shaft torque [Nm] after the stretch."""
        return self.k * np.interp(np.asarray(rpm, float), self._cap_rpm,
                                  self._cap_tpk, left=self._cap_tpk[0],
                                  right=0.0)

    def t_cont_motor(self, rpm):
        return self.k * np.interp(np.asarray(rpm, float), self._cap_rpm,
                                  self._cap_tct, left=self._cap_tct[0],
                                  right=0.0)

    def wheel_force_max(self, v, continuous=False):
        """Tractive force at the contact patch from ALL machines [N].
        Scalar in, scalar out; array in, array out."""
        rpm = self.motor_rpm(v)
        t = self.t_cont_motor(rpm) if continuous else self.t_peak_motor(rpm)
        f = np.asarray(t) * self.n * self.ratio * self.eta_red / self.r_dyn
        return float(f) if np.ndim(v) == 0 else f

    def wheel_power_max_kw(self, v, continuous=False):
        f = self.wheel_force_max(v, continuous)
        return f * np.asarray(v, float) / 1e3 if np.ndim(v) else \
            f * float(v) / 1e3

    # ------------------------------------------------------- efficiency
    def _loss_kw(self, rpm, trq_per_machine):
        """Scaled loss [kW] for ONE machine: k * loss_ws2(n, T/k)."""
        return self.k * self._chain._interp_loss(
            rpm, np.asarray(trq_per_machine, float) / self.k)

    def eta_bus_to_wheel(self, v, p_wheel_kw):
        """Bus -> contact patch efficiency, per sample (motoring)."""
        v = np.asarray(v, float)
        pw = np.asarray(p_wheel_kw, float)
        rpm = self.motor_rpm(v)
        w = np.asarray(v, float) / self.r_dyn * self.ratio      # rad/s
        drive = pw > 0.0
        p_ms_total = np.where(drive, pw, 0.0) / self.eta_red
        p_ms_each = p_ms_total / self.n
        trq = np.where(w > 1e-6, p_ms_each * 1e3 / np.maximum(w, 1e-6), 0.0)
        loss = self._loss_kw(rpm, trq) * self.n
        p_dc = p_ms_total + loss
        eta = np.where(drive & (p_dc > 1e-9),
                       np.where(drive, pw, 0.0) / np.maximum(p_dc, 1e-9), 1.0)
        return np.clip(eta, 1e-3, 1.0)

    def eta_wheel_to_bus(self, v, p_capt_kw):
        """Contact patch -> bus efficiency, per sample (generating)."""
        v = np.asarray(v, float)
        pc = np.asarray(p_capt_kw, float)
        rpm = self.motor_rpm(v)
        w = np.asarray(v, float) / self.r_dyn * self.ratio
        gen = pc > 1e-9
        p_ms_total = np.where(gen, pc, 0.0) * self.eta_red
        p_ms_each = p_ms_total / self.n
        trq = np.where(w > 1e-6, -p_ms_each * 1e3 / np.maximum(w, 1e-6), 0.0)
        loss = self._loss_kw(rpm, trq) * self.n
        p_dc = np.clip(p_ms_total - loss, 0.0, None)
        eta = np.where(gen, p_dc / np.maximum(pc, 1e-9), 0.0)
        return np.clip(eta, 0.0, 1.0)

    def spin_drag_kw(self, v):
        """Zero-torque spin loss of a PERMANENTLY GEARED machine [kW],
        both machines, bus-side.

        This is R22(d) at semi scale: a PM machine that cannot be
        disconnected drags whenever the wheels turn. It is read from the
        SAME map as everything else (loss at zero torque), scaled by k,
        so it is measured rather than asserted. Candidates whose
        traction machine HAS a disconnect (S2, S3 axle B) pay zero here
        when open - which is exactly the tax S2's disconnect is
        specified to delete."""
        rpm = self.motor_rpm(v)
        return self._loss_kw(rpm, np.zeros_like(np.asarray(rpm, float))) \
            * self.n

    # -------------------------------------------------------------- mass
    def mass_kg(self):
        # WS2's OWN mass-scaling rule, not a WS8 invention:
        #   run_ws2.py:595  mass = mass_end_kg + (mass_kg - mass_end_kg) * s
        # with mass_end_kg = 18.0 declared in ws2_params.py:126 as
        # "non-stack mass (ends, shaft, bearings) for scaling". WS8 uses
        # it verbatim, so the traction-machine mass law carries WS2's
        # provenance rather than a WS8 assumption.
        m_motor = (self.M_MOTOR_END_WS2_KG
                   + (self.M_MOTOR_WS2_KG - self.M_MOTOR_END_WS2_KG) * self.k)
        aif = SC.inverter_active_fraction
        m_inv = (self.M_INVERTER_WS2_KG * aif * self.k
                 + self.M_INVERTER_WS2_KG * (1 - aif))
        # The reduction stage carries the machine's torque, so it scales
        # with k directly (no fixed fraction: a gear set that must pass
        # k times the torque is k times the gear volume).
        m_red = self.M_REDUCTION_WS2_KG * self.k
        return dict(motor_kg=m_motor * self.n, inverter_kg=m_inv * self.n,
                    reduction_kg=m_red * self.n,
                    total_kg=(m_motor + m_inv + m_red) * self.n)

    def spec(self):
        rr = self.check_ratio(105.0 / 3.6)
        return dict(
            label=self.label, k=self.k, ratio=self.ratio,
            n_machines=self.n, eta_reduction=self.eta_red,
            T_peak_per_machine_Nm=float(self.t_peak_motor(0.0)),
            T_cont_per_machine_Nm=float(self.t_cont_motor(0.0)),
            F_wheel_peak_kN=self.wheel_force_max(1.0) / 1e3,
            P_wheel_peak_at_85kmh_kW=self.wheel_power_max_kw(85 / 3.6),
            rpm_at_105kmh=rr["rpm_at_v_max"], rpm_max=rr["rpm_max"],
            ratio_ok=rr["ok"],
            ws2_map_file=self.ws2_map_file,
            ws2_map_voltage_V=self.ws2_map_voltage_V,
            ws2_rework_round=self.ws2_rework_round,
            ws2_map_feasible_cells=self.n_feasible_cells,
            **self.mass_kg())


# =====================================================================
#  Generator: WS4's PMGenerator, stretched
# =====================================================================
def scaled_generator(name, kw_shaft_in, base=None):
    """Scale WS4's GEN_V2 loss model to `kw_shaft_in` continuous.

    PER-UNIT-INVARIANT SCALING, stated: with a stretch factor
    kg = kw_shaft_in / base.cont_kw_in,
        c_h, c_e, pe0  ->  x kg    (iron/windage/conditioning scale with
                                    machine size)
        k_cu           ->  / kg    (copper loss is k_cu*(T/100)^2 and
                                    torque scales with kg, so k_cu must
                                    fall as 1/kg to keep copper loss
                                    proportional to size)
        pe_frac        ->  unchanged (it is already per-unit)
        mass           ->  x kg
    The fixed point of this construction is that the machine's
    efficiency at the SAME per-unit load is unchanged, which is the same
    claim the traction-side stretch makes and is checked in run_ws8.py's
    sanity block.
    """
    from ws4_models import GEN_V2
    base = GEN_V2 if base is None else base
    kg = float(kw_shaft_in) / base.cont_kw_in
    return PMGenerator(name,
                       cont_kw_in=base.cont_kw_in * kg,
                       peak_kw_in=base.peak_kw_in * kg,
                       c_h=base.c_h * kg, c_e=base.c_e * kg,
                       k_cu=base.k_cu / kg,
                       pe0=base.pe0 * kg, pe_frac=base.pe_frac,
                       mass_kg=(base.mass_kg or 90.0) * kg), kg


# =====================================================================
#  Battery: WS3 cells, WS3 pack overhead
# =====================================================================
class Pack8:
    """A pack built on a WS3 cell, with WS3's own packaging overhead.

    WS3's overhead model is `cell_mass * 1.55 + 35 kg`. The fixed 35 kg
    was sized for a Vehicle Zero pack; at semi scale it amortises, and
    WS8 carries it unchanged rather than inventing a better one - the
    conservative direction for the small buffer packs and a rounding
    error for the large one.
    """

    def __init__(self, cell_name, nameplate_kwh, usable_frac,
                 label=""):
        self.cell_name = cell_name
        self.cell = CELLS[cell_name]
        self.label = label
        wh_per_cell = self.cell["ah"] * self.cell["v_nom"]
        self.n_cells = int(np.ceil(nameplate_kwh * 1000.0 / wh_per_cell))
        self.nameplate_kwh = self.n_cells * wh_per_cell / 1000.0
        self.usable_frac = float(usable_frac)
        self.usable_kwh = self.nameplate_kwh * self.usable_frac
        self.cell_mass_kg = self.n_cells * self.cell["mass_kg"]
        self.mass_kg = (self.cell_mass_kg * MASS_OVERHEAD_FACTOR
                        + MASS_OVERHEAD_FIXED_KG)
        self.p_cont_dis_kw = (self.cell["c_cont_dis"] * self.nameplate_kwh)
        self.p_cont_chg_kw = (self.cell["c_cont_chg"] * self.nameplate_kwh)
        self.p_pulse_dis_kw = (self.cell["c_pulse10_dis"] * self.nameplate_kwh)
        self.p_pulse_chg_kw = (self.cell["c_pulse10_chg"] * self.nameplate_kwh)
        # round-trip: WS3's scalar, kept only where a map is not needed
        self.eta_chg = 0.97
        self.eta_dis = 0.97

    # WS3's own cold charge-acceptance figures, per kWh of nameplate at
    # SOC 0.55 (WS3 results.json chemistry/frontier exports):
    #     LTO 4.3967 kW/kWh   NMC 0.50823 kW/kWh   LFP 0.30364 kW/kWh
    # at -10 C, against ~4.0 kW/kWh (NMC) warm. The NMC cold factor is
    # therefore 0.127 - a 7.9x collapse. This is the single most
    # consequential number WS3 hands WS8 for the -10 C corner, because it
    # decides whether descent braking goes into the pack or into the
    # resistor.
    COLD_CHG_FACTOR = {"NMC": 0.50823 / 4.0,
                       "LFP": 0.30364 / 2.0,
                       "LTO": 4.3967 / 4.0}

    def p_cont_chg_kw_at(self, temp_c):
        """Continuous charge acceptance at temperature [kW, bus-side]."""
        f_cold = self.COLD_CHG_FACTOR.get(self.cell["chem"], 0.3)
        f = float(np.interp(temp_c, [-10.0, 15.0], [f_cold, 1.0]))
        return self.p_cont_chg_kw * min(f, 1.0)

    def spec(self):
        return dict(label=self.label, cell=self.cell_name,
                    chemistry=self.cell["chem"], n_cells=self.n_cells,
                    nameplate_kWh=self.nameplate_kwh,
                    usable_kWh=self.usable_kwh,
                    usable_fraction=self.usable_frac,
                    cell_mass_kg=self.cell_mass_kg,
                    pack_mass_kg=self.mass_kg,
                    pack_Wh_per_kg=self.nameplate_kwh * 1000.0 / self.mass_kg,
                    p_cont_dis_kW=self.p_cont_dis_kw,
                    p_cont_chg_kW=self.p_cont_chg_kw,
                    p_pulse10_dis_kW=self.p_pulse_dis_kw,
                    p_pulse10_chg_kW=self.p_pulse_chg_kw)


# =====================================================================
#  Brake resistor: WS2's element-limited sink, stretched
# =====================================================================
# WS2 r4: 3.73 ohm, 150.2 kW continuous ceiling (element-limited),
# 53.9 kg assembly. The sink scales with dissipation: mass per kW is the
# invariant (grid area and airflow, not voltage).
RESISTOR_WS2_KW = 150.2
RESISTOR_WS2_KG = 53.9
RESISTOR_KG_PER_KW = RESISTOR_WS2_KG / RESISTOR_WS2_KW      # 0.3589 kg/kW


def resistor_mass_kg(kw_continuous):
    return RESISTOR_KG_PER_KW * float(kw_continuous)


__all__ = ["ScaledEDrive", "scaled_generator", "Pack8", "resistor_mass_kg",
           "RESISTOR_KG_PER_KW", "CELLS"]
