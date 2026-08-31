"""
Project Volt - WS9
Storage: the WS3-based buffers, the ESC-1(c) cited external pack, and the
SIZING RULES that build them.

RULES BEFORE NUMBERS. Every pack and every resistor in WS9 is sized by a
rule stated here and evaluated in code, never by a chosen kWh. That is the
difference between a buffer and a battery you happened to like: WS8's S1
carried a 60 kWh buffer with no stated rule, and 736 kg of it was payload.
"""
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_electric as EL8                                   # noqa: E402
from ws8_params import VEH, G                                # noqa: E402
from ws8_physics import road_load_force                      # noqa: E402

import ws9_params as P9                                      # noqa: E402


# =====================================================================
#  ESC-1(c): the cited external energy-optimised pack, and nothing else
# =====================================================================
class CitedPack:
    """A pack on a CITED EXTERNAL energy-optimised cell, used by S4' ALONE.

    ESC-1(c) ruled in R27: WS3 is not reopened; S4 is re-posed carrying a
    cited external cell as an EXPLICITLY NON-WS3 BRACKET. This class exists
    so that bracket is one visible object with one declared density, rather
    than a number filtering into a pack model. It presents exactly the
    interface `ws8_electric.Pack8` presents, so the dispatch code cannot
    tell the difference and nothing downstream has to special-case it.

    The pack-level density is declared at pack level, so no cell-to-pack
    overhead model is applied on top - applying WS3's `1.55 x cell + 35 kg`
    to an already-pack-level figure would double-count the packaging."""

    def __init__(self, nameplate_kwh, cited=None, label=""):
        c = P9.CITED_CELL if cited is None else cited
        self.cited = c
        self.label = label
        self.cell_name = c.label
        self.nameplate_kwh = float(nameplate_kwh)
        self.mass_kg = self.nameplate_kwh * 1000.0 / c.pack_Wh_per_kg
        # For the thermal model: an energy pack is dominated by its cells.
        self.cell_mass_kg = self.mass_kg * 0.70          # [WS9-PROV]
        self.cell = dict(chem=c.chem, cp_J_kgK=c.cp_J_per_kgK)
        self.n_cells = None
        self.usable_frac = c.usable_fraction
        self.usable_kwh = self.nameplate_kwh * self.usable_frac
        self.p_cont_dis_kw = c.c_cont_dis * self.nameplate_kwh
        self.p_cont_chg_kw = c.c_cont_chg * self.nameplate_kwh
        self.p_pulse_dis_kw = c.c_pulse10_dis * self.nameplate_kwh
        self.p_pulse_chg_kw = c.c_pulse10_chg * self.nameplate_kwh
        self.eta_chg = 0.97
        self.eta_dis = 0.97

    def p_cont_chg_kw_at(self, temp_c):
        """Same interpolation shape WS3 gave WS8 (`Pack8.p_cont_chg_kw_at`),
        on this cell's declared cold factor."""
        f = float(np.interp(temp_c, [-10.0, 15.0],
                            [self.cited.cold_chg_factor_minus10C, 1.0]))
        return self.p_cont_chg_kw * min(f, 1.0)

    def spec(self, t_amb_c=None):
        d = dict(label=self.label, cell=self.cell_name,
                    chemistry=self.cited.chem, n_cells=None,
                    nameplate_kWh=self.nameplate_kwh,
                    usable_kWh=self.usable_kwh,
                    usable_fraction=self.usable_frac,
                    cell_mass_kg=self.cell_mass_kg,
                    pack_mass_kg=self.mass_kg,
                    pack_Wh_per_kg=self.cited.pack_Wh_per_kg,
                    p_cont_dis_kW=self.p_cont_dis_kw,
                    p_cont_chg_kW=self.p_cont_chg_kw,
                    p_pulse10_dis_kW=self.p_pulse_dis_kw,
                    p_pulse10_chg_kW=self.p_pulse_chg_kw,
                    p_cont_chg_kW_at_minus10C=self.p_cont_chg_kw_at(-10.0),
                    cold_charge_acceptance_factor_minus10C=(
                        self.cited.cold_chg_factor_minus10C),
                    basis="ESC-1(c): CITED EXTERNAL cell, explicitly NOT a "
                          "WS3 cell; see ws9_params.CITATIONS"
                          "['PACK_WH_PER_KG']")
        if t_amb_c is not None:
            d["t_amb_C"] = float(t_amb_c)
            d["p_cont_chg_kW_at_corner"] = self.p_cont_chg_kw_at(t_amb_c)
        return d


# =====================================================================
#  Buffer sizing rules
# =====================================================================
def braking_energy_from_speed_kWh(v_ms, lam=None, m=None):
    """Kinetic energy recoverable at the WHEEL in one service stop."""
    lam = VEH.lam_rot_edrive if lam is None else lam
    m = VEH.m_gcw if m is None else m
    return 0.5 * lam * m * v_ms ** 2 / 3.6e6


def launch_energy_kWh(v_floor_ms, a_ms2, lam=None, m=None, rho_air=None):
    """Wheel energy to accelerate the combination from rest to `v_floor_ms`
    at a constant `a_ms2`, including the road load it fights on the way."""
    lam = VEH.lam_rot_launch if lam is None else lam
    m = VEH.m_gcw if m is None else m
    ke = 0.5 * lam * m * v_floor_ms ** 2 / 3.6e6
    vs = np.linspace(0.05, v_floor_ms, 200)
    f_res = np.array([float(road_load_force(np.array([x]), 0.0, m, None,
                                            None, rho_air)[0][0])
                      for x in vs])
    # time to traverse each speed increment at constant acceleration
    dv = vs[1] - vs[0]
    e_res = float(np.sum(f_res * vs * (dv / a_ms2))) / 3.6e6
    return ke + e_res


def launch_power_kW(v_floor_ms, a_ms2, lam=None, m=None, rho_air=None):
    """Wheel power at the top of that launch - the peak the buffer must be
    able to feed, and the rule that sets the buffer's C-rate."""
    lam = VEH.lam_rot_launch if lam is None else lam
    m = VEH.m_gcw if m is None else m
    f_res = float(road_load_force(np.array([v_floor_ms]), 0.0, m, None, None,
                                  rho_air)[0][0])
    return (lam * m * a_ms2 + f_res) * v_floor_ms / 1e3


def size_buffer(cell_name, p_bus_required_kW, e_swing_required_kWh,
                usable_frac=None, soc_target=None, soc_floor=None,
                round_up_kwh=1.0, label=""):
    """Build the smallest WS3-cell buffer that satisfies BOTH stated rules.

      POWER  the cell's continuous discharge C-rate must cover
             `p_bus_required_kW`
      ENERGY the swing between the dispatch target and the floor must cover
             `e_swing_required_kWh`

    Returns the pack and the binding rule, so the report can say which of
    the two sized it - which is the interesting half of the answer."""
    usable_frac = P9.BUFFER_USABLE_FRACTION if usable_frac is None \
        else usable_frac
    soc_target = P9.BUFFER_SOC_TARGET if soc_target is None else soc_target
    soc_floor = P9.BUFFER_SOC_FLOOR if soc_floor is None else soc_floor
    cell = EL8.CELLS[cell_name]
    kwh_for_power = p_bus_required_kW / cell["c_cont_dis"]
    kwh_for_energy = e_swing_required_kWh / (usable_frac
                                             * (soc_target - soc_floor))
    kwh = max(kwh_for_power, kwh_for_energy)
    kwh = math.ceil(kwh / round_up_kwh) * round_up_kwh
    pack = EL8.Pack8(cell_name, kwh, usable_frac, label=label)
    return pack, dict(
        rule="max over the enumerated sizing case set {power, energy}",
        cell=cell_name,
        kWh_required_for_power=kwh_for_power,
        kWh_required_for_energy=kwh_for_energy,
        p_bus_required_kW=p_bus_required_kW,
        e_swing_required_kWh=e_swing_required_kWh,
        nameplate_before_rounding_kWh=max(kwh_for_power, kwh_for_energy),
        nameplate_kWh=pack.nameplate_kwh,
        binding_case=("power" if kwh_for_power >= kwh_for_energy
                      else "energy"),
        rounding_kWh=round_up_kwh)


def buffer_chemistry_bracket(pack, alt_cell="NMC-P-40"):
    """What the SAME buffer rule would have built on WS8's cell, so the
    chemistry choice is a stated bracket rather than a preference.

    Arithmetic only - no re-run - because the alternative pack is not the
    pack of record and pretending otherwise would put an unsimulated number
    in a results table."""
    if pack.cell_name == alt_cell:
        return None
    alt = EL8.Pack8(alt_cell, pack.nameplate_kwh, pack.usable_frac,
                    label="chemistry bracket")
    return dict(
        of_record=dict(cell=pack.cell_name, mass_kg=pack.mass_kg,
                       p_cont_chg_kW=pack.p_cont_chg_kw,
                       p_cont_dis_kW=pack.p_cont_dis_kw,
                       cold_factor=EL8.Pack8.COLD_CHG_FACTOR.get(
                           pack.cell["chem"]),
                       efc100=pack.cell.get("efc100")),
        bracket=dict(cell=alt_cell, mass_kg=alt.mass_kg,
                     p_cont_chg_kW=alt.p_cont_chg_kw,
                     p_cont_dis_kW=alt.p_cont_dis_kw,
                     cold_factor=EL8.Pack8.COLD_CHG_FACTOR.get(
                         alt.cell["chem"]),
                     efc100=alt.cell.get("efc100")),
        mass_delta_kg=alt.mass_kg - pack.mass_kg,
        note=("same nameplate, same usable fraction, same sizing rule; "
              "WS8 used NMC-P-40 for every pack because it was the densest "
              "of WS3's three, which is right for an ENERGY pack and wrong "
              "for a buffer - a buffer is bought for charge acceptance, "
              "cold behaviour and cycle life, and this is what each cell "
              "gives on those three"))


# =====================================================================
#  Resistor sizing rule
# =====================================================================
def size_resistor_kW(f_engine_brake_at_v_N, v_ms, grade, m=None,
                     rho_air=None, friction_allowance_kW=60.0,
                     eta_wheel_to_bus=0.93, round_up_kW=10.0):
    """SIZING CASE, enumerated and stated (R14 in spirit): hold `grade` at
    `v_ms` at GCW with THE PACK AT ZERO CHARGE ACCEPTANCE - i.e. full, or
    cold, or both - given the compression brake in the best legal gear and
    the declared continuous friction-brake allowance.

    The pack-saturated descent is the case WS8's finding F1 said its heat
    ledger was missing, and it is the case that actually sizes a resistor:
    a pack with 16.8 kWh of headroom fills in about four minutes of a
    ten-minute descent, after which the whole retarding duty is the
    resistor's.  [R2-IMPL F1]"""
    m = VEH.m_gcw if m is None else m
    f_res = float(road_load_force(np.array([v_ms]), grade, m, None, None,
                                  rho_air)[0][0])
    need_N = -f_res                        # >0: gravity is winning
    f_fric = friction_allowance_kW * 1e3 / v_ms
    remainder_N = max(0.0, need_N - f_engine_brake_at_v_N - f_fric)
    p_wheel_kW = remainder_N * v_ms / 1e3
    p_bus_kW = p_wheel_kW * eta_wheel_to_bus
    kw = math.ceil(p_bus_kW / round_up_kW) * round_up_kW
    return kw, dict(
        rule="hold the enumerated descent case with the pack at ZERO "
             "charge acceptance",
        case=dict(grade=grade, v_kmh=v_ms * 3.6, m_kg=m),
        retard_required_N=need_N,
        retard_required_kW=need_N * v_ms / 1e3,
        engine_brake_N=f_engine_brake_at_v_N,
        engine_brake_kW=f_engine_brake_at_v_N * v_ms / 1e3,
        friction_allowance_kW=friction_allowance_kW,
        resistor_wheel_kW=p_wheel_kW, resistor_bus_kW=p_bus_kW,
        rated_kW=kw, rounding_kW=round_up_kW,
        mass_kg=EL8.resistor_mass_kg(kw))
