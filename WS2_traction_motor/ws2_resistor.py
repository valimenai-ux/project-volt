"""R2 dynamic-brake resistor + chopper, re-ohmed to the R10 window (r4).

Element: folded stainless-steel ribbon grid (locomotive practice),
FORCED AIR per ruling R15 — retardation is brake-critical and shall not
share a failure domain with the pack loop. R = v_min^2 / 50 kW by
construction, so full chopper duty at the 432.0 V window floor delivers
exactly the R2 requirement; the thermal design point is full duty at
the 748.8 V operating ceiling (continuous), with the 777.6 V 10-s
charge transient checked on ribbon thermal mass. WS2-E5's second-stage
ceiling and its cable-limited restatement (F12) are computed here and
in the run entry point under the R14 discipline.
"""

from ws2_params import RES, BUS


def design():
    R = RES["R_ohm"]
    out = dict(R_ohm=round(R, 5))

    # Power at full chopper duty across the ruled window
    out["P_fullduty_at_vmin_kW"] = BUS["v_min"] ** 2 / R / 1e3
    out["P_fullduty_at_vnom_kW"] = BUS["v_nom"] ** 2 / R / 1e3
    out["P_fullduty_at_vmax_kW"] = BUS["v_max"] ** 2 / R / 1e3
    out["P_fullduty_at_vtransient_kW"] = BUS["v_transient"] ** 2 / R / 1e3
    out["meets_50kW_everywhere"] = \
        out["P_fullduty_at_vmin_kW"] >= RES["P_cont_req"] / 1e3 - 1e-9

    # Chopper currents
    out["I_on_at_vmax_A"] = BUS["v_max"] / R
    out["I_on_at_vnom_A"] = BUS["v_nom"] / R
    out["I_on_at_vtransient_A"] = BUS["v_transient"] / R
    out["I_rms_50kW_A"] = (RES["P_cont_req"] / R) ** 0.5

    # Ribbon geometry set by the resistance value
    L = R * RES["ribbon_w"] * RES["ribbon_thk"] / RES["ribbon_resistivity"]
    out["ribbon_length_m"] = L
    A = 2.0 * L * RES["ribbon_w"]          # both faces
    out["ribbon_area_m2"] = A
    m_ribbon = L * RES["ribbon_w"] * RES["ribbon_thk"] * RES["ribbon_rho"]
    out["ribbon_mass_kg"] = m_ribbon
    out["assembly_mass_kg"] = m_ribbon * RES["mass_frame_factor"] + 8.0
    out["assembly_volume_L"] = out["assembly_mass_kg"] / 0.60

    # Thermal design point: full duty at the OPERATING CEILING, continuous
    P = BUS["v_max"] ** 2 / R
    out["P_design_cont_kW"] = P / 1e3
    mdot = P / (1005.0 * RES["air_dT"])           # kg/s
    vdot = mdot / 1.10                            # m^3/s
    out["air_flow_m3_h"] = vdot * 3600.0
    out["blower_W"] = vdot * RES["blower_dp"] / RES["blower_eta"]
    T_air_mean = 45.0 + RES["air_dT"] / 2.0       # inlet +45 C worst case
    out["ribbon_T_at_design_C"] = T_air_mean + P / (RES["h_forced"] * A)
    out["ribbon_T_at_50kW_C"] = T_air_mean + 50e3 / (RES["h_forced"] * A)
    out["ribbon_T_margin_K"] = RES["ribbon_T_max"] - out["ribbon_T_at_design_C"]
    # ribbon-limited continuous power (element temp at the 650 C line)
    out["P_ribbon_limit_sea_kW"] = (RES["ribbon_T_max"] - T_air_mean) \
        * RES["h_forced"] * A / 1e3

    # thermal time constant of the bare ribbon (for WS5 control margins)
    out["ribbon_tau_s"] = (m_ribbon * RES["ribbon_cp"]) / (RES["h_forced"] * A)

    # 777.6 V 10-s charge transient: excess power over the design point
    # rides ribbon thermal mass
    P_tr = BUS["v_transient"] ** 2 / R
    out["transient_10s_dT_K"] = (P_tr - P) * 10.0 / (m_ribbon * RES["ribbon_cp"])

    # R7 altitude corner (F6, carried): 2,000 m at +45 C, same blower speed
    # (constant volume flow -> mass flow scales with density; air dT rises
    # by 1/sigma; forced-convection h ~ (rho*V)^0.8 at constant velocity).
    p_alt = 101325.0 * (1.0 - 2.2558e-5 * 2000.0) ** 5.256
    rho_alt = p_alt / (287.05 * (273.15 + 45.0))
    sigma = rho_alt / 1.10          # vs the hot sea-level inlet density above
    h_alt = RES["h_forced"] * sigma ** 0.8
    dT_alt = RES["air_dT"] / sigma
    T_air_mean_alt = 45.0 + dT_alt / 2.0
    out["alt_2000m_density_ratio"] = round(sigma, 3)
    out["ribbon_T_at_design_2000m_C"] = T_air_mean_alt + P / (h_alt * A)
    out["ribbon_T_at_50kW_2000m_C"] = T_air_mean_alt + 50e3 / (h_alt * A)
    out["ribbon_T_margin_2000m_K"] = (RES["ribbon_T_max"]
                                      - out["ribbon_T_at_design_2000m_C"])
    out["P_ribbon_limit_2000m_kW"] = (RES["ribbon_T_max"] - T_air_mean_alt) \
        * h_alt * A / 1e3
    out["blower_W_2000m"] = out["blower_W"] * sigma  # fan law, constant speed

    # chopper losses at the 50 kW requirement, v_nom (1200 V SiC position)
    D = 50e3 / (BUS["v_nom"] ** 2 / R)
    I_on = BUS["v_nom"] / R
    p_cond = D * I_on ** 2 * RES["chopper_Rds"]
    p_sw = RES["chopper_f"] * RES["chopper_E_sw"] \
        * (BUS["v_nom"] / RES["chopper_V_ref"]) * (I_on / RES["chopper_I_ref"])
    out["chopper_loss_50kW_W"] = p_cond + p_sw
    out["chopper_duty_50kW_at_vnom"] = D
    # chopper at the continuous ceiling (full duty at v_max: D=1, no sw)
    out["chopper_loss_ceiling_W"] = out["I_on_at_vmax_A"] ** 2 \
        * RES["chopper_Rds"]

    # descent duty case (WS1 section 4.6)
    out["descent_24min_energy_kWh"] = 8.82   # 25 km/h row: hardest energy
    out["descent_24min_mean_kW"] = 22.0
    out["descent_worst_steady_kW"] = 45.6    # 70 km/h row: hardest power
    out["margin_over_worst_steady"] = out["P_fullduty_at_vmin_kW"] / 45.6
    return out
