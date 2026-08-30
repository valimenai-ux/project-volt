"""
Project Volt - WS3 Battery Pack
Cell archetype library and electro-thermal cell models.

Every number here is a [WS3-ASSUMPTION]: datasheet-class figures for the
named cell FAMILIES (not a procurement selection), declared as knobs so the
whole study re-runs when a real cell is characterised. Sources are the
public datasheet classes named in REPORT_WS3.md Assumptions:
  LTO-23 / LTO-10 : Toshiba SCiB(TM) 23 Ah high-energy / 10 Ah high-power
                    class prismatic LTO (same can size, per Toshiba line-up)
  LTO-45          : large-prismatic LTO class (Yinlong/GTX-type)
  LFP-P-20        : A123 AMP20-class high-power LFP pouch
  NMC-P-40        : Kokam SLPB high-power NMC pouch class
  SC-3000         : Maxwell BCAP3000-class supercapacitor (hybrid option)

R9 compliance: resistance and charge acceptance are TABLES in temperature
and SOC, not scalars. Extrema from stochastic inputs are handled by the
8-seed ensemble in run_ws3.py.
"""
import numpy as np

# --------------------------------------------------------------- archetypes
# r_dc_mohm : 10-s DC resistance at 25 C, 50% SOC (charge ~= discharge)
# c_* : C-rate limits at 25 C, BOL (temperature scaling applied separately)
# efc100 : full-DoD equivalent cycles to 80% capacity (throughput model)
# cal_life_yr : {temperature C: years to 80% at that storage temperature}
CELLS = {
    "LTO-23": dict(
        chem="LTO", ah=23.0, v_nom=2.30, v_max_protect=2.70,
        v_chg_ceiling=2.60, v_min=1.50,
        mass_kg=0.550, vol_L=0.28, r_dc_mohm=1.10,
        c_cont_dis=8.0, c_cont_chg=8.0, c_pulse10_dis=15.0, c_pulse10_chg=12.0,
        cp_J_kgK=1000.0, efc100=20000.0,
        cal_life_yr={25: 25.0, 35: 20.0, 45: 14.0, 55: 8.0},
    ),
    "LTO-10": dict(
        chem="LTO", ah=10.0, v_nom=2.30, v_max_protect=2.70,
        v_chg_ceiling=2.60, v_min=1.50,
        mass_kg=0.510, vol_L=0.28, r_dc_mohm=0.65,
        c_cont_dis=15.0, c_cont_chg=15.0, c_pulse10_dis=30.0, c_pulse10_chg=25.0,
        cp_J_kgK=1000.0, efc100=25000.0,
        cal_life_yr={25: 25.0, 35: 20.0, 45: 14.0, 55: 8.0},
    ),
    "LTO-45": dict(
        chem="LTO", ah=45.0, v_nom=2.30, v_max_protect=2.70,
        v_chg_ceiling=2.60, v_min=1.50,
        mass_kg=1.150, vol_L=0.60, r_dc_mohm=0.60,
        c_cont_dis=6.0, c_cont_chg=6.0, c_pulse10_dis=10.0, c_pulse10_chg=8.0,
        cp_J_kgK=1050.0, efc100=16000.0,
        cal_life_yr={25: 25.0, 35: 20.0, 45: 14.0, 55: 8.0},
    ),
    "LFP-P-20": dict(
        chem="LFP", ah=19.5, v_nom=3.30, v_max_protect=3.65,
        v_chg_ceiling=3.60, v_min=2.00,
        mass_kg=0.500, vol_L=0.265, r_dc_mohm=1.80,
        c_cont_dis=10.0, c_cont_chg=4.0, c_pulse10_dis=20.0, c_pulse10_chg=8.0,
        cp_J_kgK=1050.0, efc100=3500.0,
        cal_life_yr={25: 15.0, 35: 11.0, 45: 8.0, 55: 4.5},
    ),
    "NMC-P-40": dict(
        chem="NMC", ah=40.0, v_nom=3.65, v_max_protect=4.15,
        v_chg_ceiling=4.10, v_min=2.80,
        mass_kg=1.100, vol_L=0.55, r_dc_mohm=1.00,
        c_cont_dis=8.0, c_cont_chg=4.0, c_pulse10_dis=15.0, c_pulse10_chg=8.0,
        cp_J_kgK=1050.0, efc100=3000.0,
        cal_life_yr={25: 12.0, 35: 8.0, 45: 5.0, 55: 2.5},
    ),
    # Supercapacitor, used only by the hybrid-option arithmetic.
    # usable_wh assumes discharge to V/2 (75% of stored energy).
    "SC-3000": dict(
        chem="EDLC", v_max=2.85, cap_F=3000.0, mass_kg=0.51, vol_L=0.475,
        r_dc_mohm=0.29,
        usable_wh=0.5 * 3000.0 * (2.85**2 - (2.85 / 2) ** 2) / 3600.0,
    ),
}

# ------------------------------------------------ temperature dependencies
# DC-resistance multiplier vs cell temperature (Arrhenius-shaped tables).
T_GRID = np.array([-30.0, -20.0, -10.0, 0.0, 10.0, 25.0, 45.0, 60.0])
R_MULT = {
    "LTO": np.array([5.0, 3.6, 2.6, 1.9, 1.4, 1.0, 0.85, 0.80]),
    "LFP": np.array([8.0, 5.5, 3.8, 2.6, 1.7, 1.0, 0.85, 0.80]),
    "NMC": np.array([6.0, 4.2, 3.0, 2.2, 1.5, 1.0, 0.85, 0.80]),
}
# SOC multiplier on DC resistance (same shape all Li chemistries here).
SOC_GRID_R = np.array([0.0, 0.10, 0.20, 0.50, 0.80, 0.90, 1.00])
R_MULT_SOC = np.array([1.60, 1.25, 1.05, 1.00, 1.00, 1.10, 1.30])

# Continuous CHARGE acceptance (C-rate) vs cell temperature. This is the
# criterion that decides the chemistry trade: LTO plates no lithium and
# keeps accepting charge below 0 C; graphite-anode cells (LFP, NMC) must
# not be fast-charged cold. 10-s pulse acceptance = min(2x cont, c_pulse10).
# Above 45 C acceptance is cut back to protect calendar life / reach the
# 55-60 C cutoffs.
CHG_ACCEPT_C = {
    "LTO": (np.array([-30, -20, -10, 0, 10, 25, 45, 50, 55, 60], float),
            np.array([1.0, 2.0, 4.0, 6.0, 8.0, 8.0, 8.0, 6.0, 4.0, 0.0])),
    "LFP": (np.array([-30, -20, -10, 0, 10, 25, 45, 50, 55, 60], float),
            np.array([0.0, 0.0, 0.30, 0.50, 2.0, 4.0, 4.0, 3.0, 1.5, 0.0])),
    "NMC": (np.array([-30, -20, -10, 0, 10, 25, 45, 50, 55, 60], float),
            np.array([0.0, 0.0, 0.50, 1.0, 3.0, 4.0, 4.0, 3.0, 1.5, 0.0])),
}

# Open-circuit voltage vs SOC. Only LTO carries a real curve (it is the
# selected chemistry); LFP/NMC enter the trade at nominal voltage only.
OCV_SOC = np.array([0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50,
                    0.60, 0.70, 0.80, 0.90, 0.95, 1.00])
OCV_LTO = np.array([1.80, 1.95, 2.03, 2.09, 2.15, 2.19, 2.22, 2.25,
                    2.28, 2.31, 2.35, 2.42, 2.49, 2.67])


def ocv(soc, cell):
    """Open-circuit voltage [V] at SOC (fraction of nameplate)."""
    if cell["chem"] == "LTO":
        return np.interp(np.asarray(soc, float), OCV_SOC, OCV_LTO)
    return np.full_like(np.asarray(soc, float), cell["v_nom"])


def r_cell(temp_c, soc, cell):
    """10-s DC resistance [ohm] at temperature and SOC."""
    m_t = np.interp(np.asarray(temp_c, float), T_GRID, R_MULT[cell["chem"]])
    m_s = np.interp(np.asarray(soc, float), SOC_GRID_R, R_MULT_SOC)
    return cell["r_dc_mohm"] * 1e-3 * m_t * m_s


def chg_accept_c(temp_c, cell, pulse=False):
    """Charge-acceptance C-rate limit at cell temperature.
    pulse=True -> 10-s acceptance = min(2x continuous, c_pulse10_chg)."""
    tg, cg = CHG_ACCEPT_C[cell["chem"]]
    c = np.interp(np.asarray(temp_c, float), tg, cg)
    c = np.minimum(c, cell["c_cont_chg"])
    if pulse:
        c = np.minimum(2.0 * c, cell["c_pulse10_chg"])
    return c


def dis_c_limit(temp_c, cell, pulse=False):
    """Discharge C-rate limit vs temperature. Discharge is not
    plating-limited; apply the datasheet C-limit with a mild cold taper
    (electrolyte transport) and the 60 C cutoff."""
    base = cell["c_pulse10_dis"] if pulse else cell["c_cont_dis"]
    tg = np.array([-30, -20, -10, 0, 10, 25, 45, 55, 60], float)
    fr = np.array([0.5, 0.7, 0.85, 1.0, 1.0, 1.0, 1.0, 0.7, 0.0])
    return base * np.interp(np.asarray(temp_c, float), tg, fr)


def cal_life_years(temp_c, cell):
    """Calendar life to 80% at a constant storage temperature [years].
    Log-linear interpolation in the declared table."""
    tt = np.array(sorted(cell["cal_life_yr"].keys()), float)
    yy = np.array([cell["cal_life_yr"][k] for k in sorted(cell["cal_life_yr"])])
    return float(np.exp(np.interp(float(temp_c), tt, np.log(yy))))
