"""
Project Volt - WS9
R30 - THE COLD WALL, modelled rather than assumed.

R30, quoted in full because this module exists only to execute it:

    "THE COLD WALL. Cold was binding for every candidate and the model
     understated it (F2). Every WS9 electrified candidate carries pack
     preconditioning and a coolant/waste-heat cab-heating path as
     requirements, MODELLED, NOT ASSUMED; the conventional truck heats
     itself for free and the comparison must charge that."

Two objects, one for each half of that sentence.

`PackThermal`  the pack's temperature is a STATE, integrated at 10 Hz
               through every run alongside its state of charge. It starts
               COLD-SOAKED AT AMBIENT - a truck that has stood overnight at
               -10 C has a -10 C pack, and that is when its charge
               acceptance is at its worst. It is warmed by its own ohmic
               loss, by engine coolant through a declared heat exchanger
               whenever an engine is running, and by an electric heater
               otherwise; it loses heat to ambient through a declared UA.
               The pack's charge acceptance at each sample is then WS3's own
               `Pack8.p_cont_chg_kw_at(T_pack)` - the method WS8's finding
               F2 found DEFINED AND NEVER CALLED, in the corner that
               governed every exported worst-case field.   [R2-IMPL F2]

`CabHeat`      the accessory split. WS8 charged every electrified candidate
               a flat 6.6 kW bus accessory load at -10 C against the
               conventional truck's 4.0 kW crank load, and charged the
               conventional truck nothing extra, because a conventional
               truck heats its cab from engine coolant for free. That was
               the right SIGN and the wrong RESOLUTION: a WS9 candidate
               whose engine is running also has coolant, and R30 orders the
               path to be modelled. So the 3.2 kW delta is split into its
               two real parts and each is served from where it physically
               comes from.

WHAT THIS DOES TO THE ANSWER, said before the numbers so it cannot look
like a result that was arranged: modelling the waste-heat path makes the
cold corner BETTER for every candidate that runs an engine most of the time
(S5, S6, S7) and does almost nothing for one that does not (S4'). That is
not a thumb on the scale - it is the physical asymmetry R30 was written to
expose, and the report states it as the finding it is.
"""
import numpy as np


class PackThermal:
    """First-order lumped thermal model of a traction/buffer pack.

        (m_cell*cp_cell + m_struct*cp_struct) dT/dt
              = Q_ohmic + Q_coolant + Q_heater - UA*(T - T_amb)

    Cell heat capacity is WS3's own `cp_J_kgK` for the cell in the pack
    (1,050 J/(kg.K) for NMC-P-40 and LTO-23, 1,000 for the cited external
    energy cell), so the thermal mass is inherited rather than invented; the
    structure's is declared.

    UA is declared per kilogram of pack, which is the crude but defensible
    scaling for a family of packs of similar shape and insulation.
    """

    def __init__(self, pack, th, t_amb_c, cp_cell_J_per_kgK=None,
                 t_target_c=None):
        self.pack = pack
        self.th = th
        self.t_amb = float(t_amb_c)
        self.t = float(t_amb_c)           # COLD-SOAKED START
        self.t_target = th.t_pack_target_C if t_target_c is None \
            else float(t_target_c)
        cp_cell = (cp_cell_J_per_kgK if cp_cell_J_per_kgK is not None
                   else float(pack.cell.get("cp_J_kgK", 1000.0)))
        m_cell = float(pack.cell_mass_kg)
        m_struct = max(float(pack.mass_kg) - m_cell, 0.0)
        self.C_J_per_K = m_cell * cp_cell + m_struct * th.cp_structure_J_per_kgK
        self.UA_W_per_K = th.ua_W_per_K_per_kg * float(pack.mass_kg)
        self.eta_loss = 1.0 - min(pack.eta_chg, pack.eta_dis)
        # bookkeeping
        self.e_heater_kWh = 0.0
        self.e_coolant_kWh = 0.0
        self.e_ohmic_kWh = 0.0
        self.t_min = self.t
        self.t_max = self.t
        self.s_below_target = 0.0
        self.t_at_target_s = None
        self._t_elapsed = 0.0

    # ------------------------------------------------------------------
    def chg_limit_kw(self):
        """WS3's cold charge acceptance AT THE PACK'S CURRENT TEMPERATURE.
        This single call is the whole of finding F2's remedy."""
        return float(self.pack.p_cont_chg_kw_at(self.t))

    def step(self, dt, p_pack_kw, engine_running, allow_heater=True):
        """Advance one timestep.

        p_pack_kw       magnitude of pack throughput this step [kW, bus]
        engine_running  is there coolant heat available this step?
        allow_heater    may the electric heater draw from the bus?

        Returns the BUS POWER the heater drew [kW], which the caller adds to
        its accessory demand - the heater is not free and is not hidden.
        """
        q_ohm_kw = abs(p_pack_kw) * self.eta_loss
        need_kw = 0.0
        if self.t < self.t_target:
            # power to close the gap in ~120 s, capped by the hardware
            need_kw = self.C_J_per_K * (self.t_target - self.t) / 120.0 / 1e3
        q_cool_kw = 0.0
        q_heat_kw = 0.0
        if need_kw > 0.0:
            if engine_running:
                q_cool_kw = min(need_kw, self.th.q_coolant_to_pack_max_kW)
                need_kw -= q_cool_kw
            if allow_heater and need_kw > 0.0:
                q_heat_kw = min(need_kw, self.th.q_ptc_heater_max_kW)
        q_loss_kw = self.UA_W_per_K * (self.t - self.t_amb) / 1e3
        dT = (q_ohm_kw + q_cool_kw + q_heat_kw - q_loss_kw) * 1e3 * dt \
            / self.C_J_per_K
        self.t += dT
        h = dt / 3600.0
        self.e_ohmic_kWh += q_ohm_kw * h
        self.e_coolant_kWh += q_cool_kw * h
        self.e_heater_kWh += q_heat_kw * h
        if self.t < self.t_min:
            self.t_min = self.t
        if self.t > self.t_max:
            self.t_max = self.t
        self._t_elapsed += dt
        if self.t < self.t_target:
            self.s_below_target += dt
        elif self.t_at_target_s is None:
            self.t_at_target_s = self._t_elapsed
        return q_heat_kw

    def record(self):
        return dict(
            t_amb_C=self.t_amb, t_pack_start_C=self.t_amb,
            t_pack_end_C=self.t, t_pack_min_C=self.t_min,
            t_pack_max_C=self.t_max, t_pack_target_C=self.t_target,
            thermal_capacity_kJ_per_K=self.C_J_per_K / 1e3,
            UA_W_per_K=self.UA_W_per_K,
            e_pack_ohmic_selfheat_kWh=self.e_ohmic_kWh,
            e_pack_coolant_waste_heat_kWh=self.e_coolant_kWh,
            e_pack_electric_heater_kWh=self.e_heater_kWh,
            seconds_below_target=self.s_below_target,
            seconds_to_reach_target=self.t_at_target_s,
            chg_limit_at_end_kW=self.chg_limit_kw(),
            chg_limit_warm_kW=self.pack.p_cont_chg_kw,
            chg_limit_at_ambient_kW=float(
                self.pack.p_cont_chg_kw_at(self.t_amb)))


class CabHeat:
    """The accessory split R30 orders, applied identically to every
    candidate so it cannot decide the trial by bookkeeping.

    base       the warm bus/crank accessory duty (WS8's 3.4 / 4.0 kW)
    cab        the extra CAB HEAT the corner demands (0 warm, 2.2 kW at
               -10 C); served from ENGINE COOLANT when an engine is
               running, from the bus otherwise
    ac         the extra AIR-CONDITIONING the hot corner demands; always
               served from where it is fitted (bus on an electrified truck,
               crank on a conventional one) because there is no waste COLD

    The pack's own thermal demand is NOT in here - it is in PackThermal,
    where it is a physical state rather than a flat allowance."""

    def __init__(self, th, t_amb_c, electrified):
        self.th = th
        self.t_amb = float(t_amb_c)
        self.electrified = bool(electrified)
        if t_amb_c <= -5.0:
            self.cab_kw = th.cab_heat_kW_at_minus10C
            self.ac_kw = 0.0
        elif t_amb_c >= 40.0:
            self.cab_kw = 0.0
            self.ac_kw = (th.ac_load_bus_kW_at_plus45C if electrified
                          else th.ac_load_mech_kW_at_plus45C)
        else:
            self.cab_kw = 0.0
            self.ac_kw = 0.0

    def bus_extra_kw(self, engine_running):
        """Extra BUS accessory power this sample, over the warm base."""
        if not self.electrified:
            return 0.0
        cab = 0.0 if engine_running else self.cab_kw
        return cab + self.ac_kw

    def mech_extra_kw(self):
        """Extra CRANK accessory power for a conventional truck. Cab heat is
        zero because it is coolant - which is the free lunch R30 says the
        comparison must charge the others for."""
        return 0.0 if self.electrified else self.ac_kw

    def record(self):
        return dict(t_amb_C=self.t_amb, electrified=self.electrified,
                    cab_heat_kW_when_engine_off=self.cab_kw,
                    cab_heat_kW_when_engine_on=0.0,
                    ac_kW=self.ac_kw,
                    convention=("cab heat is served from engine coolant "
                                "whenever an engine is running (R30's "
                                "waste-heat path, modelled) and from the "
                                "bus otherwise; a conventional truck is "
                                "never charged for cab heat because it "
                                "genuinely does not pay for it"))
