"""
Project Volt - WS3 Battery Pack - main analysis runner.

    .venv/bin/python run_ws3.py

Reads (read-only) the ratified WS1 record:
    ../WS1_loads_duty_cycles/{volt_params,volt_cycles,volt_physics,volt_variants}.py
    ../WS1_loads_duty_cycles/results.json
Writes (all inside WS3_battery/):
    results.json, tables_ws3.md, regen_acceptance.csv, figs/*.png,
    run_output.txt (via the shell tee in the run command)

Deterministic: the only stochastic inputs are the WS1 cycle seeds, fixed
to the WS1 ensemble convention (reference seed + seeds 3..9, R9).
"""
import json
import os
import sys

sys.dont_write_bytecode = True   # never write .pyc into the WS1 folder

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
WS1 = os.path.abspath(os.path.join(HERE, "..", "WS1_loads_duty_cycles"))
sys.path.insert(0, WS1)
sys.path.insert(0, HERE)

import volt_cycles as vc                     # noqa: E402  (WS1, read-only)
import volt_physics as vp                    # noqa: E402
import volt_variants as vv                   # noqa: E402
from volt_params import VEH, DL, AUX, CTL    # noqa: E402
import ws3_cells as wc                       # noqa: E402
import ws3_pack as wp                        # noqa: E402

FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)

with open(os.path.join(WS1, "results.json")) as f:
    WS1R = json.load(f)

R = {}   # WS3 results tree
TB = []  # generated report tables (markdown)


def tb(line=""):
    TB.append(line)


def kw(x):
    return x / 1e3


# =====================================================================
# 0. PROGRAM CONSTANTS AND DECLARED WS3 ASSUMPTIONS
# =====================================================================
NS_SPINE = 288            # series cells, LTO (24 modules x 12s)
SERIES_STEP = 12          # cell-count granularity offered to WS2
SOC_TARGET = 0.55         # WS1 4.6 supervisor target, kept
SOC_BOT, SOC_TOP = 0.15, 0.90   # dispatch window (end-stops outside)
P_DIS_PK = 120e3          # R8 transient discharge, bus W
P_CHG_PK = 110e3          # R8 transient charge, bus W
P_CHG_CONT = 50e3         # R2/R8 continuous descent charge, bus W
DESCENT_S = 1440.0        # 24-minute descent (WS1 4.6, 25 km/h row)
FLOOR_V2, FLOOR_V1 = 3.5, 1.5   # kWh usable at bus (R8)
P_ON_BUS_V1 = 35e3        # E6 start-stop fixed point at the bus
HYST_BAND_KWH = 3.0       # E7/E6: keeps V1 starts < 20 per shift
SEEDS_SUB = [11] + [x + 3 for x in range(7)]   # WS1 ensemble convention
SEEDS_REG = [23] + [x + 3 for x in range(7)]
V1_HOURS_YR = 2000.0      # 250 shifts x 8 h VOLT-SUB   [WS3-ASSUMPTION]
V2_TRACES_YR = 500.0      # 250 shifts x 2 VOLT-REG     [WS3-ASSUMPTION]
T_CAL_AVG_C = 30.0        # fleet-average cell temp for calendar life
T_NOM = 25.0              # nominal duty-stats temperature

R["params_ws3"] = dict(
    ns_spine=NS_SPINE, series_step=SERIES_STEP,
    soc_target=SOC_TARGET, soc_window=[SOC_BOT, SOC_TOP],
    R8_peaks_bus_kW=dict(discharge=kw(P_DIS_PK), charge=kw(P_CHG_PK),
                         charge_continuous=kw(P_CHG_CONT)),
    buffer_floors_bus_kWh=dict(V2=FLOOR_V2, V1=FLOOR_V1),
    v1_startstop=dict(p_on_bus_kW=kw(P_ON_BUS_V1), band_kWh=HYST_BAND_KWH),
    seeds=dict(VOLT_SUB=SEEDS_SUB, VOLT_REG=SEEDS_REG),
    annualisation=dict(V1_hours_per_year=V1_HOURS_YR,
                       V2_traces_per_year=V2_TRACES_YR,
                       calendar_avg_cell_temp_C=T_CAL_AVG_C),
    packaging=dict(mass_overhead_factor=wp.MASS_OVERHEAD_FACTOR,
                   mass_overhead_fixed_kg=wp.MASS_OVERHEAD_FIXED_KG,
                   vol_overhead_factor=wp.VOL_OVERHEAD_FACTOR),
    thermal=dict(ua_cells_coolant_W_K=wp.UA_CELLS_TO_COOLANT,
                 ua_radiator_W_K=wp.UA_RADIATOR,
                 t_cell_max_cont_C=wp.T_CELL_MAX_CONT,
                 t_cell_cutoff_C=wp.T_CELL_CUTOFF,
                 coupled_structure_kg=wp.COUPLED_STRUCTURE_KG),
    cells={k: {kk: vv_ for kk, vv_ in c.items() if kk != "cal_life_yr"}
           | {"cal_life_yr": c.get("cal_life_yr")} if isinstance(c, dict) else c
           for k, c in wc.CELLS.items()},
)

# =====================================================================
# 1. REBUILD THE RATIFIED CYCLES, VERIFY AGAINST THE WS1 RECORD
# =====================================================================
print("== 1. cycles + verification vs WS1 results.json")
cycA = vc.build_cycle_A()          # seed 11, reference
cycB = vc.build_cycle_B()          # seed 23, reference
for c in (cycA, cycB):
    c["P"] = vp.wheel_power(c["t"], c["v"], c["grade"], VEH.m_gvw)["P_wheel"]

fnA = vv.four_numbers(cycA["t"], cycA["v"], cycA["P"])

p_dir, locked, rpm, _ = vv.v2_direct_share(cycB["t"], cycB["v"], cycB["P"])
_fn0 = vv.four_numbers(cycB["t"], cycB["v"], cycB["P"], p_wheel_direct=p_dir)
p_dir, locked, rpm, _ = vv.v2_direct_share(
    cycB["t"], cycB["v"], cycB["P"],
    p_gen_reserve_bus=_fn0["N2_genset_const_bus_kW"] * 1e3)
fnB = vv.four_numbers(cycB["t"], cycB["v"], cycB["P"], p_wheel_direct=p_dir)

ws1_bat = WS1R["requirements_summary"]["battery_buffer_kWh"]
ws1_reg = WS1R["requirements_summary"]["peak_regen_kW"]
checks = {
    "N3_V1_5min_kWh": (fnA["N3_buffer_5min_kWh"],
                       ws1_bat["cycle_5min_VOLT-SUB_V1_reference"]),
    "N3_V2_5min_kWh": (fnB["N3_buffer_5min_kWh"],
                       ws1_bat["cycle_5min_VOLT-REG_V2_reference"]),
    # WS1 line 1288-1289: max over the V1 and V2 reference draws
    "batt_peak_dis_kW": (max(fnA["batt_peak_dis_kW"], fnB["batt_peak_dis_kW"]),
                         ws1_reg["battery_peak_discharge_kW"]),
    "batt_peak_chg_kW": (max(fnA["batt_peak_chg_kW"], fnB["batt_peak_chg_kW"]),
                         ws1_reg["battery_peak_charge_kW"]),
}
R["verification_vs_ws1"] = {}
for k, (mine, theirs) in checks.items():
    rel = abs(mine - theirs) / max(abs(theirs), 1e-12)
    R["verification_vs_ws1"][k] = dict(ws3=mine, ws1=theirs, rel_err=rel)
    status = "OK" if rel < 1e-9 else "MISMATCH"
    print(f"   {k}: ws3={mine:.9f} ws1={theirs:.9f} [{status}]")
    assert rel < 1e-6, f"failed to reproduce WS1 record for {k}"

# =====================================================================
# 2. PACK DEFINITIONS
# =====================================================================
packV2 = wp.Pack("LTO-23", NS_SPINE, 1)      # recommended, both variants
packV1L = wp.Pack("LTO-10", NS_SPINE, 1)     # V1 light option
packUP = wp.Pack("LTO-45", NS_SPINE, 1)      # sensitivity: one size up
pack400 = wp.Pack("LTO-23", 174, 1)          # sensitivity: 400 V class bus


def pack_dump(p):
    v_lo, v_hi = p.v_window(SOC_BOT, SOC_TOP)
    usable_cells = p.nameplate_kwh * (SOC_TOP - SOC_BOT)
    return dict(
        cell=p.cell_name, series=p.ns, parallel=p.np,
        nameplate_kWh=p.nameplate_kwh,
        usable_kWh_cells=usable_cells,
        usable_kWh_bus=usable_cells * wp.ETA_BATT,
        v_nominal=p.v_nom,
        v_ocv_at_window=[v_lo, v_hi],
        v_charge_ceiling=p.ns * p.cell["v_chg_ceiling"],
        v_protect_max=p.ns * p.cell["v_max_protect"],
        cell_mass_kg=p.cell_mass_kg, pack_mass_kg=p.mass_kg,
        pack_volume_L=p.vol_L, c_th_J_K=p.c_th,
    )


R["pack_designs"] = dict(
    V2_and_V1_recommended=pack_dump(packV2),
    V1_light_option=pack_dump(packV1L),
    sensitivity_cell_up=pack_dump(packUP),
    sensitivity_bus_400V=pack_dump(pack400),
)

# --- SOC allocation (E7 superposition inside the dispatch window)
def soc_alloc(p, hyst, regen_head, grade_res):
    usable_bus = p.nameplate_kwh * (SOC_TOP - SOC_BOT) * wp.ETA_BATT
    margin = usable_bus - (hyst + regen_head + grade_res)
    return dict(usable_bus_kWh=usable_bus,
                genset_hysteresis_kWh=hyst, regen_headroom_kWh=regen_head,
                grade_reserve_kWh=grade_res, unallocated_margin_kWh=margin,
                end_stops_pct_nameplate=[SOC_BOT * 100, (1 - SOC_TOP) * 100])


R["soc_allocation"] = dict(
    V2=soc_alloc(packV2, 3.5, 1.5, 2.0) | dict(floor_kWh=FLOOR_V2),
    V1=soc_alloc(packV2, 3.0, 1.5, 1.0) | dict(floor_kWh=FLOOR_V1),
    V1_light=soc_alloc(packV1L, 3.0, 1.0, 0.8) | dict(floor_kWh=FLOOR_V1),
)
for k, v in R["soc_allocation"].items():
    v["floor_margin_ratio"] = v["usable_bus_kWh"] / v["floor_kWh"]

# =====================================================================
# 3. CAPABILITY MAPS (temperature x SOC), R8 COMPLIANCE
# =====================================================================
print("== 3. capability maps")
T_LIST = [-10.0, 0.0, 10.0, 25.0, 45.0]
SOC_LIST = [0.25, 0.40, 0.55, 0.70, 0.85, 0.90]


def cap_map(p):
    out = dict(T_C=T_LIST, SOC=SOC_LIST, dis_pulse10_kW=[], chg_pulse10_kW=[],
               chg_cont_kW=[])
    for t in T_LIST:
        out["dis_pulse10_kW"].append(
            [kw(float(p.p_dis_pulse10(t, s))) for s in SOC_LIST])
        out["chg_pulse10_kW"].append(
            [kw(float(p.p_chg_pulse10(t, s))) for s in SOC_LIST])
        out["chg_cont_kW"].append(
            [kw(float(p.p_chg_cont(t, s))) for s in SOC_LIST])
    return out


R["capability_maps"] = dict(V2_LTO23=cap_map(packV2), V1_light_LTO10=cap_map(packV1L))

# minimum cell temperature at which each R8 peak is met across the window
tfine = np.arange(-10.0, 45.01, 0.5)


def t_min_for(fn_p, req, socs):
    ok = np.array([all(float(fn_p(t, s)) >= req for s in socs) for t in tfine])
    idx = np.argmax(ok)
    return float(tfine[idx]) if ok.any() and ok[idx] else None


V_FLOOR_CELL = packV2.cell["v_min"]                # 1.50 V/cell
V_FLOOR_PACK = packV2.ns * V_FLOOR_CELL            # 432.0 V, 288s
R["r8_compliance"] = dict(
    note="minimum cell temperature at which the R8 peak is available over "
         f"the stated SOC range, computed against the {V_FLOOR_CELL:.2f} "
         f"V/cell ({V_FLOOR_PACK:.1f} V pack) floor = the exported "
         "operating_min_V (WS3-r1-F1); dispatch gate follows from these. "
         "Higher electronics floors inherit the derated gates in "
         "bus_voltage_window.dis_gate_vs_electronics_floor_V",
    dis_120kW_over_SOC_40_90=t_min_for(packV2.p_dis_pulse10, P_DIS_PK,
                                       [0.40, 0.55, 0.70, 0.90]),
    chg_110kW_over_SOC_15_85=t_min_for(packV2.p_chg_pulse10, P_CHG_PK,
                                       [0.15, 0.40, 0.55, 0.85]),
    chg_cont_50kW_over_SOC_15_85=t_min_for(packV2.p_chg_cont, P_CHG_CONT,
                                           [0.15, 0.40, 0.55, 0.85]),
    dis_120kW_at_soc55_minus10C_kW=kw(float(packV2.p_dis_pulse10(-10, 0.55))),
    chg_110kW_at_soc85_minus10C_kW=kw(float(packV2.p_chg_pulse10(-10, 0.85))),
)

# ---------------------------------------------------------------------
# 3b. BUS-WINDOW / COLD-GATE JOINT CONSISTENCY (WS3-r1-F1, blocking)
# Round 1 exported operating_min_V = 288 x 1.85 V (an undocumented
# allocation) alongside gates computed against the 1.50 V/cell cell
# floor - jointly unsatisfiable. Resolution (options a+c of the
# finding): the exported floor IS the cell floor the gates are computed
# against, and WS2 receives an explicit gate-vs-electronics-floor
# derate table plus the R8 current/voltage operating points.
# ---------------------------------------------------------------------
print("== 3b. bus-window consistency (F1)")


def p_dis_pulse10_vfloor(p, temp_c, soc, v_floor_cell):
    """10-s discharge capability against an ARBITRARY terminal floor
    (the pack model's own physics, cell v_min replaced by the floor)."""
    c = p.cell
    u = float(wc.ocv(soc, c))
    r = float(wc.r_cell(temp_c, soc, c))
    i = max(0.0, min((u - v_floor_cell) / r,
                     float(wc.dis_c_limit(temp_c, c, pulse=True)) * c["ah"]))
    return p.ns * p.np * i * (u - i * r)


def op_point(p, p_w, soc, temp_c):
    """Current and bus voltage while delivering p_w (signed, +discharge)."""
    i, _, vt = p.solve_current(np.array([p_w]), np.array([soc]), temp_c)
    return dict(T_C=float(temp_c), SOC=soc, P_bus_kW=kw(abs(p_w)),
                I_A=abs(float(i[0])), V_bus_V=p.ns * float(vt[0]))


_gate_dis = R["r8_compliance"]["dis_120kW_over_SOC_40_90"]
_gate_chg = R["r8_compliance"]["chg_110kW_over_SOC_15_85"]
_derate = []
for vf in (1.50, 1.60, 1.70, 1.80, 1.85, 1.90):
    g = t_min_for(lambda t, s, _vf=vf: p_dis_pulse10_vfloor(packV2, t, s, _vf),
                  P_DIS_PK, [0.40, 0.55, 0.70, 0.90])
    entry = dict(v_floor_cell_V=vf, v_floor_pack_V=packV2.ns * vf,
                 dis_120kW_gate_C_over_SOC_40_90=g)
    if g is not None:
        opp = op_point(packV2, P_DIS_PK, 0.40, g)
        entry |= dict(I_at_gate_A=opp["I_A"], V_bus_at_gate_V=opp["V_bus_V"])
    _derate.append(entry)

_ops = dict(
    dis_120kW_warm_soc40=op_point(packV2, P_DIS_PK, 0.40, 25.0),
    dis_120kW_at_cold_gate_soc40=op_point(packV2, P_DIS_PK, 0.40, _gate_dis),
    dis_120kW_warm_soc15_info=op_point(packV2, P_DIS_PK, 0.15, 25.0),
    chg_110kW_warm_soc85=op_point(packV2, -P_CHG_PK, 0.85, 25.0),
    chg_110kW_at_gate_soc85=op_point(packV2, -P_CHG_PK, 0.85, _gate_chg),
)

# 252s end of the offered series range: exact bound, not an interpolation
pack252 = wp.Pack("LTO-23", 252, 1)
_g252d = t_min_for(pack252.p_dis_pulse10, P_DIS_PK, [0.40, 0.55, 0.70, 0.90])
_g252c = t_min_for(pack252.p_chg_pulse10, P_CHG_PK, [0.15, 0.40, 0.55, 0.85])
_op252w = op_point(pack252, P_DIS_PK, 0.40, 25.0)
_op252g = (op_point(pack252, P_DIS_PK, 0.40, _g252d)
           if _g252d is not None else None)
_s252 = dict(
    series=252, nameplate_kWh=pack252.nameplate_kwh,
    v_nominal_V=pack252.v_nom,
    operating_min_V=252 * V_FLOOR_CELL,
    operating_max_V=252 * pack252.cell["v_chg_ceiling"],
    transient_max_V=252 * pack252.cell["v_max_protect"],
    dis_120kW_gate_C_over_SOC_40_90=_g252d,
    chg_110kW_gate_C_over_SOC_15_85=_g252c,
    I_120kW_warm_A=_op252w["I_A"], V_bus_120kW_warm_V=_op252w["V_bus_V"],
    I_120kW_at_gate_A=(_op252g["I_A"] if _op252g else None),
    V_bus_120kW_at_gate_V=(_op252g["V_bus_V"] if _op252g else None),
    note=(f"every voltage member scales x252/288 = {252/288:.3f}; per-cell "
          f"power rises x288/252 so the availability gates MOVE WARMER "
          f"({_g252d:+.1f} C discharge / {_g252c:+.1f} C charge, vs "
          f"{_gate_dis:+.1f} / {_gate_chg:+.1f} at 288s) and warm full-power "
          f"current rises to {_op252w['I_A']:.0f} A. Do not linearly "
          "interpolate the 288s figures."),
)

R["bus_window_consistency"] = dict(
    basis=(f"all capability figures and every r8_compliance gate are "
           f"computed against the cell floor {V_FLOOR_CELL:.2f} V/cell = "
           f"{V_FLOOR_PACK:.1f} V pack; the exported operating_min_V equals "
           "this same floor, so the window and the gates are jointly "
           "satisfiable as exported (resolves WS3-r1-F1)"),
    r8_operating_points=_ops,
    soc15_note=(f"120 kW warm at SOC 15 sits at "
                f"{_ops['dis_120kW_warm_soc15_info']['V_bus_V']:.1f} V; the "
                "R8 discharge gate is declared over SOC 40-90 and full "
                "power below SOC 40 is NOT guaranteed - WS5 dispatch limit"),
    chg_transient_note=(f"the 110 kW charge pulse at its "
                        f"{_gate_chg:+.1f} C gate rides the bus to "
                        f"{_ops['chg_110kW_at_gate_soc85']['V_bus_V']:.1f} V "
                        f"- above the {packV2.ns * packV2.cell['v_chg_ceiling']:.1f} V "
                        "continuous charge ceiling, inside the "
                        f"{packV2.ns * packV2.cell['v_max_protect']:.1f} V "
                        "transient/protect ceiling: WS2 rates the "
                        "electronics for the transient ceiling"),
    dis_gate_vs_electronics_floor=_derate,
    series_252_bound=_s252,
)

# =====================================================================
# 4. CHEMISTRY TRADE
# =====================================================================
print("== 4. chemistry trade")
ETA_W2B = DL.eta_wheel_to_bus
REGEN_BUS_FULL = 75e3 * ETA_W2B          # 64.92 kW: full 75 kW wheel cap at bus
DESC_ROWS = WS1R["sensitivity"]["descent_10km_6pc"]["per_speed"]
DESCENT_WHEEL_MAX = max(r_["retardation_required_kW"]
                        for r_ in DESC_ROWS.values()) * 1e3  # worst 4.6 row
DESCENT_BUS_MAX = DESCENT_WHEEL_MAX * ETA_W2B  # worst 4.6 row at bus (39.4 kW)


def chem_min_pack(cell_name, v_bus_nom=660.0):
    """Smallest ns x np pack of this chemistry meeting the R8 power set at
    25 C warm, on a ~660 V nominal string."""
    c = wc.CELLS[cell_name]
    ns = int(round(v_bus_nom / c["v_nom"] / SERIES_STEP) * SERIES_STEP)
    best = None
    for npar in range(1, 30):
        p = wp.Pack(cell_name, ns, npar)
        ok = (float(p.p_dis_pulse10(25, 0.40)) >= P_DIS_PK
              and float(p.p_chg_pulse10(25, 0.85)) >= P_CHG_PK
              and float(p.p_chg_cont(45, 0.85)) >= P_CHG_CONT)
        if ok:
            best = p
            break
    return best


RUNAWAY = {"LTO": "class 1 (no plating, oxide anode, onset >260 C)",
           "LFP": "class 2 (no O2-releasing cathode; graphite plates when cold-charged)",
           "NMC": "class 3 (O2-releasing cathode, onset ~180-210 C)"}

R["chemistry_trade"] = {}
for name in ("LTO-23", "LFP-P-20", "NMC-P-40"):
    p = chem_min_pack(name)
    c = wc.CELLS[name]
    acc_m10 = kw(float(p.p_chg_cont(-10.0, SOC_TARGET)))
    acc_45 = kw(float(p.p_chg_cont(45.0, SOC_TARGET)))
    # pack that would be needed to accept the full regen cap at -10 C cold soak
    if acc_m10 > 1e-9:
        scale = max(1.0, kw(REGEN_BUS_FULL) / acc_m10)
        kwh_for_cold = p.nameplate_kwh * scale
    else:
        kwh_for_cold = None
    R["chemistry_trade"][name] = dict(
        series=p.ns, parallel=p.np, nameplate_kWh=p.nameplate_kwh,
        cell_mass_kg=p.cell_mass_kg, pack_mass_kg=p.mass_kg,
        pack_volume_L=p.vol_L,
        chg_cont_at_minus10C_kW_bus=acc_m10,
        chg_cont_at_45C_kW_bus=acc_45,
        covers_full_regen_cold=bool(acc_m10 >= kw(REGEN_BUS_FULL)),
        covers_descent_cold=bool(acc_m10 >= kw(DESCENT_BUS_MAX)),
        nameplate_needed_to_cover_regen_at_minus10C_kWh=kwh_for_cold,
        efc100=c["efc100"],
        cal_life_45C_yr=c["cal_life_yr"][45],
        thermal_runaway=RUNAWAY[c["chem"]],
    )

# hybrid option: supercap bank sized to the V1 ensemble-max 5-min swing
sc = wc.CELLS["SC-3000"]
sc_target_kwh = ws1_bat["cycle_5min_VOLT-SUB_V1_ensemble_max"]
n_sc = int(np.ceil(sc_target_kwh * 1e3 / sc["usable_wh"]))
R["chemistry_trade"]["hybrid_SC_note"] = dict(
    sc_usable_wh_per_cell=sc["usable_wh"],
    target_buffer_kWh=sc_target_kwh, n_cells=n_sc,
    sc_bank_mass_kg=n_sc * sc["mass_kg"], sc_bank_volume_L=n_sc * sc["vol_L"],
    dcdc_mass_kg=0.35 * kw(P_DIS_PK),   # [WS3-ASSUMPTION] 0.35 kg/kW
    verdict="bank covering only the 5-min swing already outweighs the "
            "entire LTO-23 cell stack; battery still needed for the floors "
            "and the 50 kW continuous descent charge - rejected",
)

# =====================================================================
# 5. DESCENT THERMAL (task 3) + PRECONDITIONING
# =====================================================================
print("== 5. descent thermal + preconditioning")
DT_TH = 1.0
desc_rows = DESC_ROWS
RESISTOR_BUS_RATING_W = 50e3   # R2: >=50 kW continuous dissipation at the bus


def descent_sim(p, row, t_amb, t0_cell, soc0=SOC_TARGET):
    """One 4.6 descent row with R2 blending: battery first (up to
    acceptance and the SOC ceiling), resistor next CAPPED AT ITS 50 kW
    R2 RATING, friction last - computed, never assumed (WS3-r1-F6).
    Regen arriving at the bus = wheel retardation x eta_wheel_to_bus."""
    p_bus_in = row["retardation_required_kW"] * 1e3 * ETA_W2B
    dur = row["time_10km_s"]
    n = int(np.ceil(dur / DT_TH))
    soc, t_cell = soc0, t0_cell
    e_np_j = p.nameplate_kwh * 3.6e6
    e_bat = e_res = e_fric = 0.0
    t_peak = t0_cell
    t_fill = None
    p_res_peak = 0.0
    for k in range(n):
        acc = float(p.p_chg_cont(t_cell, soc))
        head = max(0.0, (SOC_TOP - soc)) * e_np_j / DT_TH
        p_bat = min(p_bus_in, acc, head)
        p_left = p_bus_in - p_bat
        p_res = min(p_left, RESISTOR_BUS_RATING_W)   # rating enforced (F6)
        p_fric = p_left - p_res                      # honest overflow (F6)
        p_res_peak = max(p_res_peak, p_res)
        if t_fill is None and p_bat < p_bus_in * 0.999 and head < acc:
            t_fill = k * DT_TH
        _, q_cell, _ = p.solve_current(np.array([-p_bat]),
                                       np.array([soc]), t_cell)
        q = float(q_cell[0]) * p.n_cells
        # stored energy grows by terminal power minus its own I2R share
        soc += (p_bat - q) * DT_TH / e_np_j
        t_cell = p.thermal_step(t_cell, q, t_amb, DT_TH)
        t_peak = max(t_peak, t_cell)
        e_bat += p_bat * DT_TH
        e_res += p_res * DT_TH
        e_fric += p_fric * DT_TH
    return dict(retardation_kW_wheel=row["retardation_required_kW"],
                regen_at_bus_kW=kw(p_bus_in), duration_s=dur,
                E_battery_kWh=e_bat / 3.6e6, E_resistor_kWh=e_res / 3.6e6,
                E_friction_kWh=e_fric / 3.6e6,
                resistor_peak_kW=kw(p_res_peak),
                resistor_rating_kW=kw(RESISTOR_BUS_RATING_W),
                soc_end=soc, t_cell_peak_C=t_peak, t_cell_end_C=t_cell,
                t_soc_ceiling_s=t_fill)


# +20% payload descent rows (WS1 payload convention, run_ws1.py 4a):
# m = curb + 1.2 x payload-at-GVW; retardation from WS1's own road-load
# physics at constant speed on the -6% grade (WS3-r1-F6).
M_PAYLOAD120 = VEH.m_curb_operating + 1.2 * VEH.m_payload_at_gvw   # 7180 kg


def descent_row_at_mass(v_kmh, m):
    v = v_kmh / 3.6
    f_, _, _, _ = vp.road_load_force(np.array([v]), np.array([-0.06]), m)
    return dict(retardation_required_kW=kw(-float(f_[0]) * v),
                time_10km_s=10000.0 / v)


R["descent_thermal"] = {"rows_45C": {}, "rows_minus10C": {},
                        "rows_45C_payload120": {},
                        "rows_minus10C_payload120": {}}
for spd, row in desc_rows.items():
    R["descent_thermal"]["rows_45C"][spd] = descent_sim(packV2, row, 45.0, 45.0)
    R["descent_thermal"]["rows_minus10C"][spd] = descent_sim(packV2, row,
                                                            -10.0, -10.0)
    row20 = descent_row_at_mass(float(spd.replace("kmh", "")), M_PAYLOAD120)
    R["descent_thermal"]["rows_45C_payload120"][spd] = descent_sim(
        packV2, row20, 45.0, 45.0)
    R["descent_thermal"]["rows_minus10C_payload120"][spd] = descent_sim(
        packV2, row20, -10.0, -10.0)

_rows_gvw = (list(R["descent_thermal"]["rows_45C"].values())
             + list(R["descent_thermal"]["rows_minus10C"].values()))
_rows_p20 = (list(R["descent_thermal"]["rows_45C_payload120"].values())
             + list(R["descent_thermal"]["rows_minus10C_payload120"].values()))
_worst_p20_spd = max(R["descent_thermal"]["rows_45C_payload120"],
                     key=lambda s: R["descent_thermal"]
                     ["rows_45C_payload120"][s]["resistor_peak_kW"])
_fric_max = max(d["E_friction_kWh"] for d in _rows_gvw + _rows_p20)
R["descent_thermal"]["resistor_bound"] = dict(
    rating_bus_kW=kw(RESISTOR_BUS_RATING_W),
    max_resistor_kW_gvw=max(d["resistor_peak_kW"] for d in _rows_gvw),
    max_resistor_kW_payload120=max(d["resistor_peak_kW"] for d in _rows_p20),
    margin_at_payload120_kW=(kw(RESISTOR_BUS_RATING_W)
                             - max(d["resistor_peak_kW"] for d in _rows_p20)),
    friction_kWh_max_any_row=_fric_max,
    payload120_mass_kg=M_PAYLOAD120,
    worst_payload120_row=_worst_p20_spd,
    note=("R2 blend order with the resistor RATING enforced as a hard cap; "
          "overflow lands in the friction column and is reported, not "
          "assumed zero. "
          + ("Friction stays 0.00 kWh on every row - GVW and +20% payload, "
             "+45 C and -10 C"
             if _fric_max == 0.0 else
             f"NONZERO friction, worst row {_fric_max:.3f} kWh")
          + " (WS3-r1-F6)."),
)

# literal R2/R8 read: 50 kW at the terminals, held the full 24 minutes,
# +45 C soak - the THERMAL capability demonstration (SOC pinned at the
# 90% ceiling once reached; energy beyond that diverts to the resistor,
# see escalation ES-1)
t_cell = 45.0
soc = SOC_TARGET
e_np_j = packV2.nameplate_kwh * 3.6e6
traj = []
q_hist = []
for k in range(int(DESCENT_S)):
    _, q_cell, _ = packV2.solve_current(np.array([-P_CHG_CONT]),
                                        np.array([soc]), t_cell)
    q = float(q_cell[0]) * packV2.n_cells
    soc = min(SOC_TOP, soc + (P_CHG_CONT - q) / e_np_j * DT_TH)
    t_cell = packV2.thermal_step(t_cell, q, 45.0, DT_TH)
    traj.append(t_cell)
    q_hist.append(q)
traj = np.array(traj)
q_hist = np.array(q_hist)
R["descent_thermal"]["literal_50kW_24min_45C"] = dict(
    p_term_kW=kw(P_CHG_CONT), duration_s=DESCENT_S,
    c_rate=P_CHG_CONT / packV2.v_nom / packV2.ah,
    heat_avg_kW=kw(float(np.mean(q_hist))),
    heat_end_kW=kw(float(q_hist[-1])),
    t_cell_end_C=float(traj[-1]), t_cell_peak_C=float(np.max(traj)),
    t_steady_C=packV2.steady_cell_temp(float(q_hist[-1]), 45.0),
    margin_to_55C=wp.T_CELL_MAX_CONT - float(np.max(traj)),
    soc_ceiling_hit_s=float(np.argmax(np.array(
        [SOC_TARGET + (P_CHG_CONT) * k / e_np_j for k in range(int(DESCENT_S))]
    ) >= SOC_TOP)) if True else None,
)
_t_traj_literal = traj.copy()

# --- preconditioning: -10 C soak, 8 kW heater into the plates
HEATER_W = 8000.0
t_cell = -10.0
times = {}
traj_pre = []
for k in range(7200):
    t_cell = packV2.thermal_step(t_cell, 0.0, -10.0, 1.0, cooling=False,
                                 heater_w=HEATER_W)
    traj_pre.append(t_cell)
    for gate in (0.0, 10.0, 15.0):
        if gate not in times and t_cell >= gate:
            times[gate] = k + 1.0
_e10 = kw(HEATER_W) * times.get(10.0, np.nan) / 3600.0
_e15 = kw(HEATER_W) * times.get(15.0, np.nan) / 3600.0
R["preconditioning"] = dict(
    heater_kW=kw(HEATER_W), ambient_C=-10.0, start_C=-10.0,
    time_to_0C_s=times.get(0.0), time_to_10C_s=times.get(10.0),
    time_to_15C_s=times.get(15.0),
    energy_to_10C_kWh=_e10,
    energy_to_15C_kWh=_e15,
    # WS3-r1-F4: note is now computed from the same fields it annotates
    genset_fuel_note=(f"heater fed from genset at the bus; {_e10:.2f} kWh "
                      f"electrical per -10 C cold start to +10 C "
                      f"({_e15:.2f} kWh to +15 C)"),
    self_heat_credit_kW_at_minus10=None,   # filled after duty ensemble
)

# =====================================================================
# 6. DUTY-TRACE ENSEMBLE (R9: 8 seeds), LIFE, HEAT, EFFICIENCY
# =====================================================================
print("== 6. duty ensemble (8 seeds x 3 modes)")


def process_trace(p, t, p_term, e_batt, temp_c):
    e = np.asarray(e_batt, float)
    soc = SOC_TARGET + (e - e.mean()) / (p.nameplate_kwh * 3.6e6)
    st = wp.duty_stats(p, t, p_term, soc, temp_c)
    fat = wp.fatigue_summary(e, p.nameplate_kwh, p.cell["efc100"])
    return st, fat


ens = {"V1_const_genset": [], "V1_startstop": [], "V2_iMMD": []}
starts_list = []
cold_heat = []
for sd in SEEDS_SUB:
    cyc = vc.build_cycle_A(seed=sd)
    P = vp.wheel_power(cyc["t"], cyc["v"], cyc["grade"], VEH.m_gvw)["P_wheel"]
    fn = vv.four_numbers(cyc["t"], cyc["v"], P, windows=(300,))
    em = fn["_em"]
    dur_h = float(cyc["t"][-1]) / 3600.0
    # -- V1 constant genset (the WS1 (3) convention)
    p_term = wp.terminal_power_from_ws1(em["p_batt"])
    st, fat = process_trace(packV2, cyc["t"], p_term, em["e_batt"], T_NOM)
    st_cold, _ = process_trace(packV2, cyc["t"], p_term, em["e_batt"], -10.0)
    cold_heat.append(st_cold["heat_avg_kW"])
    ens["V1_const_genset"].append(
        dict(seed=sd, dur_h=dur_h, N3_kWh=fn["N3_buffer_5min_kWh"],
             stats=st, fatigue=fat, heat_avg_cold_kW=st_cold["heat_avg_kW"]))
    # -- V1 start-stop genset (E6 design mode)
    p_term_h, e_h, starts = wp.genset_hysteresis(cyc["t"], em["p_bus"],
                                                 P_ON_BUS_V1, HYST_BAND_KWH)
    st_h, fat_h = process_trace(packV2, cyc["t"], p_term_h, e_h, T_NOM)
    starts_list.append(starts / dur_h)
    ens["V1_startstop"].append(
        dict(seed=sd, dur_h=dur_h, starts_per_h=starts / dur_h,
             stats=st_h, fatigue=fat_h))

for sd in SEEDS_REG:
    cyc = vc.build_cycle_B(seed=sd)
    P = vp.wheel_power(cyc["t"], cyc["v"], cyc["grade"], VEH.m_gvw)["P_wheel"]
    pd_, _, _, _ = vv.v2_direct_share(cyc["t"], cyc["v"], P)
    f0 = vv.four_numbers(cyc["t"], cyc["v"], P, p_wheel_direct=pd_,
                         windows=(300,))
    pd_, _, _, _ = vv.v2_direct_share(
        cyc["t"], cyc["v"], P,
        p_gen_reserve_bus=f0["N2_genset_const_bus_kW"] * 1e3)
    fn = vv.four_numbers(cyc["t"], cyc["v"], P, p_wheel_direct=pd_,
                         windows=(300,))
    em = fn["_em"]
    p_term = wp.terminal_power_from_ws1(em["p_batt"])
    st, fat = process_trace(packV2, cyc["t"], p_term, em["e_batt"], T_NOM)
    ens["V2_iMMD"].append(
        dict(seed=sd, dur_h=float(cyc["t"][-1]) / 3600.0,
             N3_kWh=fn["N3_buffer_5min_kWh"], stats=st, fatigue=fat))


def envelope(rows, path):
    vals = []
    for r in rows:
        v = r
        for key in path:
            v = v[key]
        vals.append(v)
    return dict(min=float(np.min(vals)), max=float(np.max(vals)),
                mean=float(np.mean(vals)))


R["duty_ensemble"] = {}
for mode, rows in ens.items():
    e = dict(
        peak_dis_kW=envelope(rows, ["stats", "peak_dis_kW"]),
        peak_chg_kW=envelope(rows, ["stats", "peak_chg_kW"]),
        peak_c_dis=envelope(rows, ["stats", "peak_c_dis"]),
        peak_c_chg=envelope(rows, ["stats", "peak_c_chg"]),
        heat_avg_kW=envelope(rows, ["stats", "heat_avg_kW"]),
        heat_peak_kW=envelope(rows, ["stats", "heat_peak_kW"]),
        eta_roundtrip=envelope(rows, ["stats", "eta_roundtrip"]),
        rainflow_cycles_per_trace=envelope(rows, ["fatigue", "n_cycles"]),
        damage_per_trace=envelope(rows, ["fatigue", "damage"]),
        throughput_kWh_per_trace=envelope(rows, ["stats", "throughput_kWh"]),
    )
    if mode != "V1_startstop":
        e["N3_kWh"] = envelope(rows, ["N3_kWh"])
    if mode == "V1_startstop":
        e["starts_per_h"] = envelope(rows, ["starts_per_h"])
    R["duty_ensemble"][mode] = e
R["duty_ensemble"]["_seeds"] = dict(VOLT_SUB=SEEDS_SUB, VOLT_REG=SEEDS_REG)
R["duty_ensemble"]["_per_seed"] = {
    m: [{k: v for k, v in r.items() if k != "stats"} |
        {"stats": r["stats"]} for r in rows]
    for m, rows in ens.items()}

R["preconditioning"]["self_heat_credit_kW_at_minus10"] = float(np.mean(cold_heat))

# ---- life projection
def life(mode, rows, traces_per_year, pack):
    dmg = np.array([r["fatigue"]["damage"] for r in rows])
    n_cyc = np.array([r["fatigue"]["n_cycles"] for r in rows])
    d_yr = float(np.max(dmg)) * traces_per_year         # ensemble-max, R9
    cal = wc.cal_life_years(T_CAL_AVG_C, pack.cell)
    cal45 = wc.cal_life_years(45.0, pack.cell)
    cyc_yr = 1.0 / d_yr if d_yr > 0 else np.inf
    return dict(
        micro_cycles_per_year=float(np.max(n_cyc)) * traces_per_year,
        cycle_damage_per_year=d_yr,
        cycle_life_years=cyc_yr,
        calendar_life_years_at_30C=cal,
        calendar_life_years_at_45C_bound=cal45,
        combined_years_at_30C=1.0 / (d_yr + 1.0 / cal),
        combined_years_at_45C_bound=1.0 / (d_yr + 1.0 / cal45),
    )


dur_sub_h = float(np.mean([r["dur_h"] for r in ens["V1_const_genset"]]))
R["life"] = dict(
    V1_startstop=life("V1_startstop", ens["V1_startstop"],
                      V1_HOURS_YR / dur_sub_h, packV2),
    V1_const_genset=life("V1_const_genset", ens["V1_const_genset"],
                         V1_HOURS_YR / dur_sub_h, packV2),
    V2_iMMD=life("V2_iMMD", ens["V2_iMMD"], V2_TRACES_YR, packV2),
)

# ---- part-load efficiency map (replaces the WS1 0.97 scalar, R9)
print("== 7. efficiency map + cold-case recompute")
P_GRID = [5, 10, 20, 40, 60, 80, 100, 120]
eff = dict(P_kW=P_GRID, T_C=[-10.0, 0.0, 25.0, 45.0], dis=[], chg=[])
for tC in eff["T_C"]:
    rd, rccol = [], []
    for pk in P_GRID:
        _, q, vt = packV2.solve_current(np.array([pk * 1e3]),
                                        np.array([SOC_TARGET]), tC)
        u = float(wc.ocv(SOC_TARGET, packV2.cell))
        rd.append(float(vt[0]) / u)
        _, q, vt = packV2.solve_current(np.array([-pk * 1e3]),
                                        np.array([SOC_TARGET]), tC)
        rccol.append(u / float(vt[0]))
    eff["dis"].append(rd)
    eff["chg"].append(rccol)
R["efficiency_map"] = eff
R["efficiency_map"]["ws1_scalar"] = 0.97
R["efficiency_map"]["note"] = ("one-way efficiency at SOC 55%; WS1's 0.97 "
                               "scalar is valid below ~40-50 kW warm and "
                               "optimistic at the R8 peaks and cold")

# ---- cold-case (2) recompute with the LTO acceptance curve (R7 design case)
acc_m10_bus = float(packV2.p_chg_cont(-10.0, SOC_TARGET))
acc_m10_wheel = acc_m10_bus / ETA_W2B
acc_0_bus = float(packV2.p_chg_cont(0.0, SOC_TARGET))
cap_cold_wheel = min(75e3, acc_m10_wheel)
fn_cold = vv.four_numbers(cycA["t"], cycA["v"], cycA["P"],
                          p_aux=4000.0, cap_wheel=cap_cold_wheel,
                          windows=(300,))
fn_cold6 = vv.four_numbers(cycA["t"], cycA["v"], cycA["P"],
                           p_aux=6000.0, cap_wheel=cap_cold_wheel,
                           windows=(300,))
env_ws1 = WS1R["sensitivity"]["environment"]
n2_nom = env_ws1["nominal"]["VOLT-SUB_V1"]["N2_genset_const_bus_kW"]
_, p_capt_cold, p_fric_cold = vp.regen_split(cycA["v"], cycA["P"],
                                             cap_cold_wheel)

# WS3-r1-F3: put the cold resistance model in the loop. First-order
# correction: on the cold reference trace, replace the 0.97/0.97 scalar
# bookkeeping loss with the WS3 -10 C model loss; the difference lands on
# the genset average (feedback through the setpoint is second order).
_em_cold = fn_cold["_em"]
_p_term_cold = wp.terminal_power_from_ws1(_em_cold["p_batt"])
_e_cold_tr = np.asarray(_em_cold["e_batt"], float)
_soc_cold_tr = SOC_TARGET + ((_e_cold_tr - _e_cold_tr.mean())
                             / (packV2.nameplate_kwh * 3.6e6))
_st_cold_n2 = wp.duty_stats(packV2, cycA["t"], _p_term_cold,
                            _soc_cold_tr, -10.0)
_loss_scalar_w = np.where(_p_term_cold > 0,
                          _p_term_cold * (1.0 / wp.ETA_BATT - 1.0),
                          -_p_term_cold * (1.0 - wp.ETA_BATT))
_loss_scalar_kW = float(np.mean(_loss_scalar_w)) / 1e3
_n2_cold_corr = (fn_cold["N2_genset_const_bus_kW"]
                 + _st_cold_n2["heat_avg_kW"] - _loss_scalar_kW)

R["cold_case_recompute"] = dict(
    lto_chg_accept_cont_at_minus10C_bus_kW=kw(acc_m10_bus),
    lto_chg_accept_cont_at_minus10C_wheel_kW=kw(acc_m10_wheel),
    lto_chg_accept_cont_at_0C_bus_kW=kw(acc_0_bus),
    regen_cap_effective_wheel_kW=kw(cap_cold_wheel),
    V1_N2_cold_LTO_aux4_kW=fn_cold["N2_genset_const_bus_kW"],
    V1_N2_cold_LTO_aux6_kW=fn_cold6["N2_genset_const_bus_kW"],
    V1_N2_nominal_kW=n2_nom,
    V1_N2_cold_ws1_regen_disabled_kW=(
        env_ws1["cold_regen_disabled_aux4kW"]["VOLT-SUB_V1"]
        ["N2_genset_const_bus_kW"]),
    V1_friction_cold_LTO_kWh=float(vp.trapz(p_fric_cold, cycA["t"])) / 3.6e6,
    V1_friction_cold_ws1_kWh=(
        env_ws1["cold_regen_disabled_aux4kW"]["VOLT-SUB_V1"]
        ["friction_brake_energy_kWh"]),
    penalty_ws1_pct=100.0 * (env_ws1["cold_regen_disabled_aux4kW"]
                             ["VOLT-SUB_V1"]["N2_genset_const_bus_kW"]
                             / n2_nom - 1.0),
    penalty_lto_aux4_pct=100.0 * (fn_cold["N2_genset_const_bus_kW"]
                                  / n2_nom - 1.0),
    # WS3-r1-F3: cold resistance model in the loop (first-order)
    battery_loss_cold_model_avg_kW=_st_cold_n2["heat_avg_kW"],
    battery_loss_cold_scalar_avg_kW=_loss_scalar_kW,
    V1_N2_cold_LTO_aux4_corrected_kW=_n2_cold_corr,
    penalty_lto_aux4_corrected_pct=100.0 * (_n2_cold_corr / n2_nom - 1.0),
    correction_note=("V1_N2_cold_LTO_aux4_kW keeps WS1's 0.97/0.97 warm "
                     "scalars (like-for-like with WS1's environment table); "
                     "the _corrected_ figure replaces that bookkeeping loss "
                     "with the WS3 -10 C resistance-model loss on the same "
                     "trace (WS3-r1-F3). Headline: +20-25%."),
    note="cold-soaked (unpreconditioned) LTO at -10 C accepts the full "
         "75 kW wheel regen cap on its CONTINUOUS rating; the R7 cold "
         "case collapses to an accessory-load penalty",
)

# =====================================================================
# 8. C-RATE REALITY CHECK vs E8 + POWER/ENERGY FRONTIER (task 4)
# =====================================================================
print("== 8. c-rates + frontier")


def crates(p):
    i120, _, _ = p.solve_current(np.array([P_DIS_PK]),
                                 np.array([0.40]), 25.0)
    i110, _, _ = p.solve_current(np.array([-P_CHG_PK]),
                                 np.array([0.85]), 25.0)
    i50, _, _ = p.solve_current(np.array([-P_CHG_CONT]),
                                np.array([0.70]), 45.0)
    return dict(
        c_at_120kW_dis=float(i120[0]) / p.ah,
        c_at_110kW_chg=float(-i110[0]) / p.ah,
        c_at_50kW_cont_chg=float(-i50[0]) / p.ah,
        i_at_120kW_A=float(i120[0]),
        p_over_nameplate_120kW=kw(P_DIS_PK) / p.nameplate_kwh,
    )


R["c_rate_check"] = dict(
    E8_claim="93-113C on cycle-derived (3); 40C/37C even on 3 kWh",
    V2_LTO23=crates(packV2), V1_light_LTO10=crates(packV1L),
    conclusion="power-sizing at the 650 V window lands the spine at ~8C "
               "peak / ~3C continuous - inside power-cell ratings; E8's "
               "fear was correct for the floors, moot for the built pack",
)

# frontier: minimum nameplate vs each constraint, per LTO cell size
def frontier_cell(name):
    c = wc.CELLS[name]
    p1 = wp.Pack(name, 1, 1)      # single cell
    e_cell = c["ah"] * c["v_nom"] / 1e3
    rows = {}
    for label, fn_p, req in (
            ("dis_pulse_120kW", lambda t, s: p1.p_dis_pulse10(t, s), P_DIS_PK),
            ("chg_pulse_110kW", lambda t, s: p1.p_chg_pulse10(t, s), P_CHG_PK),
            ("chg_cont_50kW_45C", None, P_CHG_CONT)):
        if label == "dis_pulse_120kW":
            pc = float(p1.p_dis_pulse10(25.0, 0.40))
        elif label == "chg_pulse_110kW":
            pc = float(p1.p_chg_pulse10(25.0, 0.85))
        else:
            pc = float(p1.p_chg_cont(45.0, 0.85))
        n_min = int(np.ceil(req / pc))
        rows[label] = dict(per_cell_W=pc, n_cells_min=n_min,
                           kWh_min=n_min * e_cell)
    rows["voltage_window_288s"] = dict(n_cells_min=NS_SPINE,
                                       kWh_min=NS_SPINE * e_cell)
    rows["governing_kWh"] = max(v["kWh_min"] for v in rows.values())
    return rows


R["frontier"] = {n: frontier_cell(n) for n in ("LTO-10", "LTO-23", "LTO-45")}
R["frontier"]["_note"] = (
    "minimum pack energy forced by each requirement at 25 C; the governing "
    "term for every LTO cell size is the 288s voltage window, i.e. the pack "
    "exceeds the R8 buffer floors by construction, not by an energy need")

# =====================================================================
# 9. SENSITIVITIES (task 5)
# =====================================================================
print("== 9. sensitivities")
sens = {}
# 9a. buffer floors x1.5
sens["floors_x1.5"] = {}
for var, alloc, floor in (("V2", R["soc_allocation"]["V2"], FLOOR_V2 * 1.5),
                          ("V1", R["soc_allocation"]["V1"], FLOOR_V1 * 1.5),
                          ("V1_light", R["soc_allocation"]["V1_light"],
                           FLOOR_V1 * 1.5)):
    sens["floors_x1.5"][var] = dict(
        floor_kWh=floor, usable_bus_kWh=alloc["usable_bus_kWh"],
        margin_ratio=alloc["usable_bus_kWh"] / floor,
        meets=bool(alloc["usable_bus_kWh"] >= floor))

# 9b. envelope corners
UA_RAD_2000M = wp.UA_RADIATOR * 0.88   # [WS3-ASSUMPTION] ~-12% air-side at 2 km
q_end = float(q_hist[-1])
sens["envelope_corners"] = dict(
    minus10C_0m=dict(
        dis_pulse_soc55_kW=kw(float(packV2.p_dis_pulse10(-10, 0.55))),
        chg_cont_soc55_kW=kw(float(packV2.p_chg_cont(-10, 0.55))),
        descent_50kW_ok=bool(float(packV2.p_chg_cont(-10, 0.55)) >= P_CHG_CONT),
        precondition_to_10C_min=R["preconditioning"]["time_to_10C_s"] / 60.0),
    plus45C_0m=dict(
        t_cell_end_50kW_24min_C=R["descent_thermal"]
        ["literal_50kW_24min_45C"]["t_cell_end_C"],
        margin_to_55C_K=R["descent_thermal"]["literal_50kW_24min_45C"]
        ["margin_to_55C"]),
    plus45C_2000m=dict(
        ua_radiator_W_K=UA_RAD_2000M,
        t_steady_50kW_C=packV2.steady_cell_temp(q_end, 45.0, UA_RAD_2000M),
        creepage_note="750 V class at 2,000 m: clearance/creepage per "
                      "IEC 60664 pollution degree 2 handed to WS6"),
    minus10C_2000m=dict(
        note="cold + altitude concurrent: battery limits are the -10 C "
             "column; altitude affects only the radiator, unused cold"),
)

# 9c. one cell size up / down on the same 288s spine
def cell_sens(p):
    d = pack_dump(p)
    d |= crates(p)
    d["dis_pulse_25C_soc40_kW"] = kw(float(p.p_dis_pulse10(25, 0.40)))
    d["dis_pulse_minus10C_soc55_kW"] = kw(float(p.p_dis_pulse10(-10, 0.55)))
    d["chg_cont_45C_soc85_kW"] = kw(float(p.p_chg_cont(45, 0.85)))
    d["chg_cont_minus10C_soc55_kW"] = kw(float(p.p_chg_cont(-10, 0.55)))
    d["meets_R8_warm"] = bool(
        float(p.p_dis_pulse10(25, 0.40)) >= P_DIS_PK
        and float(p.p_chg_pulse10(25, 0.85)) >= P_CHG_PK
        and float(p.p_chg_cont(45, 0.85)) >= P_CHG_CONT)
    return d


sens["cell_size"] = dict(
    down_LTO10=cell_sens(packV1L),
    baseline_LTO23=cell_sens(packV2),
    up_LTO45=cell_sens(packUP),
)

# 9d. bus-voltage window alternative (400 V class)
sens["bus_400V_class"] = cell_sens(pack400) | dict(
    note="174s1p LTO-23: FAILS the 120 kW warm pulse (C-limit), accepts "
         "only ~40 kW cold vs the 64.9 kW cap; fixing either means 2P and "
         "double the energy/mass - the 650 V window is the right one")
R["sensitivity"] = sens

# =====================================================================
# 10. HEAT LEDGER (R9 -> WS6)
# =====================================================================
lit = R["descent_thermal"]["literal_50kW_24min_45C"]
d25 = R["descent_thermal"]["rows_45C"]["25kmh"]
R["heat_ledger_WS6"] = [
    dict(component="battery pack (V2/V1 spine)",
         case="R2 descent, 50 kW continuous charge, +45 C ambient "
              "(24-min transient AVERAGE; WS6 sizes the loop to the "
              "steady sizing line at the bottom of this ledger)",
         heat_kW=lit["heat_avg_kW"], duration_s=DESCENT_S,
         sink="pack coolant loop -> pack radiator"),
    dict(component="battery pack",
         case="R8 peak 120 kW discharge (10 s)",
         heat_kW=R["duty_ensemble"]["V2_iMMD"]["heat_peak_kW"]["max"],
         duration_s=10.0, sink="cell thermal mass -> coolant"),
    dict(component="battery pack",
         case="VOLT-REG cycle average, V2 i-MMD, 25 C (8-seed max)",
         heat_kW=R["duty_ensemble"]["V2_iMMD"]["heat_avg_kW"]["max"],
         duration_s="continuous", sink="pack coolant loop"),
    dict(component="battery pack",
         case="VOLT-SUB cycle average, V1 start-stop, 25 C (8-seed max)",
         heat_kW=R["duty_ensemble"]["V1_startstop"]["heat_avg_kW"]["max"],
         duration_s="continuous", sink="pack coolant loop"),
    dict(component="battery pack",
         case="VOLT-SUB cycle average at -10 C cell (pre-warm-up)",
         heat_kW=float(np.max(cold_heat)), duration_s="until warm",
         sink="self-heating credit, stays in the pack"),
    dict(component="preconditioning heater",
         case="cold start below 0 C (R7), 8 kW into pack plates",
         heat_kW=-kw(HEATER_W),
         duration_s=R["preconditioning"]["time_to_10C_s"],
         sink="INTO the pack; source = genset via bus (or R2 resistor "
              "loop if WS2/WS6 co-locate it on the pack coolant circuit)"),
    dict(component="pack coolant loop (spec to WS6)",
         case="SIZING LINE (steady state): hold cells <= 55 C at +45 C "
              "with 50 kW cont charge - WS6 sizes the coolant loop to "
              "THIS line",
         heat_kW=lit["heat_end_kW"], duration_s="continuous rating",
         sink=f"pack radiator, UA >= {wp.UA_RADIATOR:.0f} W/K air-side at "
              f"0 m ({UA_RAD_2000M:.0f} W/K at 2,000 m still closes)"),
]

# =====================================================================
# 10b. FIRST-PRINCIPLES SANITY CHECKS + ENSEMBLE-CONVENTION CROSSCHECK
# =====================================================================
ws1_ens = WS1R["sensitivity"]["seed_ensemble"]
R["verification_vs_ws1"]["N3_V1_ensemble_max_kWh"] = dict(
    ws3=R["duty_ensemble"]["V1_const_genset"]["N3_kWh"]["max"],
    ws1=ws1_ens["VOLT-SUB"]["N3_buffer_5min_kWh"]["max"],
    note="exact reproduction expected (same code path)")
R["verification_vs_ws1"]["N3_V2_ensemble_max_kWh_info"] = dict(
    ws3_two_pass=R["duty_ensemble"]["V2_iMMD"]["N3_kWh"]["max"],
    ws1_single_pass=ws1_ens["VOLT-REG"]["N3_buffer_5min_kWh"]["max"],
    note="WS1's ensemble loop used the single-pass i-MMD split (run_ws1.py "
         "line 428); WS3 applies the ratified two-pass generator reserve "
         "to every seed. Method difference, delta ~1%, not a defect.")

# ---- power-convention ledger (WS3-r1-F2): WS1 battery_trace peaks are
# STORED-energy-side (discharge p_stored = p_bus / 0.97); WS3 duty peaks
# are terminal/bus-side. State every comparison in both conventions.
_ens_bus = R["duty_ensemble"]["V2_iMMD"]["peak_dis_kW"]["max"]
_r8_ref_stored = ws1_reg["battery_peak_discharge_kW"]
R["power_convention"] = dict(
    note=("WS1 battery_trace peaks are STORED-energy-side (discharge "
          "p_stored = p_bus / 0.97, volt_physics.py battery_trace); WS3 "
          "duty-ensemble peaks are terminal/bus-side "
          "(ws3_pack.terminal_power_from_ws1). The 0.97 scalar converts. "
          "WS3's capability checks apply R8's 120 kW as a BUS-side "
          "requirement - conservative by the same factor (WS3-r1-F2)."),
    r8_reference_stored_kW=_r8_ref_stored,
    r8_reference_bus_kW=_r8_ref_stored * wp.ETA_BATT,
    ensemble_peak_bus_kW=_ens_bus,
    ensemble_peak_stored_kW=_ens_bus / wp.ETA_BATT,
    exceedance_like_for_like_bus_pct=100.0 * (_ens_bus
                                              / (_r8_ref_stored * wp.ETA_BATT)
                                              - 1.0),
    recommended_restatement_bus_kW=125.0,
    recommended_restatement_chg_bus_kW=110.0,
)

row25 = R["descent_thermal"]["rows_45C"]["25kmh"]
e_in_bus_25 = (desc_rows["25kmh"]["E_to_dissipate_kWh"] * ETA_W2B)
i50, q50c, _ = packV2.solve_current(np.array([-P_CHG_CONT]),
                                    np.array([0.70]), 50.0)
dmg_v2_simple = (np.mean([r["stats"]["throughput_kWh"] for r in ens["V2_iMMD"]])
                 / (2.0 * packV2.nameplate_kwh)
                 / packV2.cell["efc100"] * V2_TRACES_YR)
R["sanity_checks"] = dict(
    nameplate_arithmetic_kWh=dict(
        computed=288 * 23.0 * 2.30 / 1e3, model=packV2.nameplate_kwh),
    descent25_energy_balance_kWh=dict(
        battery_plus_resistor=row25["E_battery_kWh"] + row25["E_resistor_kWh"],
        wheel_energy_at_bus=e_in_bus_25,
        note="battery+resistor absorb the full descent energy delivered to "
             "the bus; friction stays at zero (R2 order)"),
    heat_at_50kW_hand_calc=dict(
        i_cell_A=float(-i50[0]),
        q_pack_kW=float(q50c[0]) * packV2.n_cells / 1e3,
        model_end_kW=lit["heat_end_kW"],
        note="I^2R at SOC 70 / 50 C vs the transient model end point"),
    precondition_energy=dict(
        c_th_MJ_per_20K=packV2.c_th * 20.0 / 1e6,
        heater_time_s_hand=packV2.c_th * 20.0 / HEATER_W,
        model_time_to_10C_s=R["preconditioning"]["time_to_10C_s"]),
    v2_damage_per_year=dict(
        rainflow_model=R["life"]["V2_iMMD"]["cycle_damage_per_year"],
        throughput_shortcut=float(dmg_v2_simple),
        note="linear-throughput shortcut should approximate rainflow "
             "damage under the N(D)=EFC100/D model"),
    r8_exceedance_info=dict(
        convention="kW at the bus terminals unless suffixed _stored "
                   "(see power_convention, WS3-r1-F2)",
        ensemble_peak_dis_kW=R["duty_ensemble"]["V2_iMMD"]["peak_dis_kW"]["max"],
        ensemble_peak_dis_stored_kW=R["power_convention"]
        ["ensemble_peak_stored_kW"],
        r8_design_kW=kw(P_DIS_PK),
        r8_reference_bus_kW=R["power_convention"]["r8_reference_bus_kW"],
        r8_reference_stored_kW=R["power_convention"]["r8_reference_stored_kW"],
        pack_capability_warm_kW=kw(float(packV2.p_dis_pulse10(25.0, 0.40))),
        note=(f"R8's 120 kW descends from WS1's stored-side "
              f"{_r8_ref_stored:.3f} kW = {_r8_ref_stored * wp.ETA_BATT:.1f} "
              "kW at the bus; WS3 applies 120 kW bus-side in every "
              "capability check (conservative). Like-for-like at the bus the "
              "8-seed ensemble exceeds the reference draw by "
              f"+{R['power_convention']['exceedance_like_for_like_bus_pct']:.1f}%; "
              "the pack covers it with margin - see escalation ES-4")),
)

# =====================================================================
# 11. INTERFACE BLOCK (machine-readable)
# =====================================================================
usableV2 = R["pack_designs"]["V2_and_V1_recommended"]["usable_kWh_bus"]
usableV1L = R["pack_designs"]["V1_light_option"]["usable_kWh_bus"]
_bw = R["bus_window_consistency"]
_op_warm = _bw["r8_operating_points"]["dis_120kW_warm_soc40"]
_op_gate = _bw["r8_operating_points"]["dis_120kW_at_cold_gate_soc40"]
R["interface_WS3"] = dict(
    _convention="mirrors WS1 results.json: SI, kW/kWh at the DC bus unless "
                "suffixed _cells or _stored; extrema are 8-seed ensemble "
                "envelopes",
    bus_voltage_window=dict(
        preferred_nominal_V=packV2.v_nom,
        operating_min_V=V_FLOOR_PACK,
        operating_max_V=packV2.ns * packV2.cell["v_chg_ceiling"],
        transient_max_V=packV2.ns * packV2.cell["v_max_protect"],
        protection_max_V=packV2.ns * packV2.cell["v_max_protect"],
        ocv_window_V=list(packV2.v_window(SOC_BOT, SOC_TOP)),
        governs=(f"operating_min_V = {V_FLOOR_PACK:.1f} V "
                 f"({packV2.ns} x {V_FLOOR_CELL:.2f} V/cell) is the SAME "
                 "floor every r8_compliance gate is computed against: the "
                 "window and the gates are jointly satisfiable as exported "
                 "(WS3-r1-F1). Electronics that cannot work down to "
                 f"{V_FLOOR_PACK:.1f} V inherit the derated gates in "
                 "dis_gate_vs_electronics_floor_V. operating_max_V is the "
                 "continuous charge ceiling; 10-s charge pulses ride to "
                 "transient_max_V (see chg_transient_note)."),
        chg_transient_note=_bw["chg_transient_note"],
        soc15_note=_bw["soc15_note"],
        acceptable_series_range=[252, 288],
        series_step_cells=SERIES_STEP,
        module_nominal_V=SERIES_STEP * packV2.cell["v_nom"],
        r8_operating_points=_bw["r8_operating_points"],
        dis_gate_vs_electronics_floor_V=_bw["dis_gate_vs_electronics_floor"],
        series_252_bound=_bw["series_252_bound"],
        rationale=(f"1P string at 650 V class keeps the R8 peaks at "
                   f"~{_op_warm['I_A']:.0f} A / {_op_warm['V_bus_V']:.1f} V "
                   f"warm and {_op_gate['I_A']:.0f} A / "
                   f"{_op_gate['V_bus_V']:.1f} V at the "
                   f"{_op_gate['T_C']:+.1f} C cold gate - size conductors "
                   "and devices to the cold-gate current, not the warm "
                   "figure. A 400 V class 174s1p string FAILS the 120 kW "
                   "pulse warm (110 kW) and accepts only 40 kW cold - "
                   "going 2P to fix it doubles pack energy (see "
                   "sensitivity/bus_400V_class)")),
    descent_resistor_bound=R["descent_thermal"]["resistor_bound"],
    cell=dict(family="LTO 23 Ah prismatic (SCiB 23 Ah class)",
              v_nom=2.30, granularity="12s1p module, 27.6 V nominal"),
    packs=dict(
        V2=dict(config="288s1p LTO-23",
                nameplate_kWh=packV2.nameplate_kwh,
                usable_bus_kWh=usableV2, floor_kWh=FLOOR_V2,
                mass_kg=packV2.mass_kg, volume_L=packV2.vol_L),
        V1=dict(config="288s1p LTO-23 (identical pack, spine commonality)",
                nameplate_kWh=packV2.nameplate_kwh,
                usable_bus_kWh=usableV1L * 0 + usableV2, floor_kWh=FLOOR_V1,
                mass_kg=packV2.mass_kg, volume_L=packV2.vol_L),
        V1_light_option=dict(config="288s1p LTO-10 (same can/module)",
                             nameplate_kWh=packV1L.nameplate_kwh,
                             usable_bus_kWh=usableV1L, floor_kWh=FLOOR_V1,
                             mass_kg=packV1L.mass_kg,
                             volume_L=packV1L.vol_L)),
    soc_strategy=dict(target=SOC_TARGET, dispatch_window=[SOC_BOT, SOC_TOP],
                      allocation=R["soc_allocation"]),
    coolant=dict(type="50/50 EG-water, shared low-temperature circuit "
                      "acceptable", flow_L_min=8.0,
                 heat_rejection_cont_kW=lit["heat_end_kW"],
                 ua_radiator_W_K=wp.UA_RADIATOR,
                 heater_kW=kw(HEATER_W),
                 request_to_WS2_WS6="mount the R2 brake resistor on the "
                 "pack coolant circuit so it doubles as the "
                 "preconditioning heat source"),
    regen_acceptance_curve_file="regen_acceptance.csv",
    heat_to_ledger=R["heat_ledger_WS6"],
    r8_compliance=R["r8_compliance"],
    life_projection_years=dict(
        V1=R["life"]["V1_startstop"]["combined_years_at_30C"],
        V2=R["life"]["V2_iMMD"]["combined_years_at_30C"]),
)

# =====================================================================
# 12. REGEN-ACCEPTANCE CURVE FILE (WS5 interface)
# =====================================================================
tt = np.arange(-30.0, 60.1, 5.0)
rows = []
for t in tt:
    ccont = float(wc.chg_accept_c(t, packV2.cell))
    cpulse = float(wc.chg_accept_c(t, packV2.cell, pulse=True))
    p_cont = float(packV2.p_chg_cont(t, SOC_TARGET))
    p_pulse = float(packV2.p_chg_pulse10(t, SOC_TARGET))
    p_cont_l = float(packV1L.p_chg_cont(t, SOC_TARGET))
    rows.append((t, ccont, cpulse, kw(p_cont), kw(p_pulse),
                 kw(p_cont / ETA_W2B), kw(p_cont_l)))
hdr = ("T_cell_C,chg_accept_cont_C,chg_accept_pulse10s_C,"
       "V2pack_chg_cont_kW_bus,V2pack_chg_pulse10s_kW_bus,"
       "V2pack_chg_cont_kW_wheel_equiv,V1light_chg_cont_kW_bus")
with open(os.path.join(HERE, "regen_acceptance.csv"), "w") as f:
    f.write("# Project Volt WS3 - pack regen-acceptance vs cell temperature\n")
    f.write("# at SOC 55% (target); SOC dependence via capability maps in "
            "results.json\n")
    f.write(hdr + "\n")
    for r_ in rows:
        f.write(",".join(f"{x:.3f}" for x in r_) + "\n")
R["regen_acceptance_table"] = dict(header=hdr.split(","),
                                   rows=[list(r_) for r_ in rows])

# =====================================================================
# 13. FIGURES
# =====================================================================
print("== 13. figures")
plt.rcParams.update({"figure.dpi": 130, "font.size": 8.5, "axes.grid": True,
                     "grid.alpha": 0.3})

fig, ax = plt.subplots(figsize=(6.5, 4))
tt2 = np.arange(-30, 60.1, 1.0)
ax.plot(tt2, [kw(float(packV2.p_dis_pulse10(t, 0.55))) for t in tt2],
        label="discharge 10 s (SOC 55%)")
ax.plot(tt2, [kw(float(packV2.p_chg_pulse10(t, 0.55))) for t in tt2],
        label="charge 10 s (SOC 55%)")
ax.plot(tt2, [kw(float(packV2.p_chg_cont(t, 0.55))) for t in tt2],
        label="charge continuous (SOC 55%)")
ax.plot(tt2, [kw(float(packV2.p_chg_cont(t, 0.85))) for t in tt2], "--",
        label="charge continuous (SOC 85%)")
ax.axhline(kw(P_DIS_PK), color="k", lw=0.8, ls=":")
ax.axhline(kw(P_CHG_PK), color="k", lw=0.8, ls=":")
ax.axhline(kw(P_CHG_CONT), color="k", lw=0.8, ls=":")
for y, s in ((kw(P_DIS_PK), "R8 120 kW dis"), (kw(P_CHG_PK), "R8 110 kW chg"),
             (kw(P_CHG_CONT), "R2 50 kW cont")):
    ax.annotate(s, (59, y), fontsize=7, va="bottom", ha="right")
ax.set_xlabel("cell temperature [C]")
ax.set_ylabel("pack power at bus [kW]")
ax.set_title("288s1p LTO-23 capability vs temperature")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig_ws3_01_capability_vs_T.png"))
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(np.arange(_t_traj_literal.size) / 60.0, _t_traj_literal,
        label="literal: 50 kW held 24 min, +45 C")
for spd in ("25kmh", "60kmh", "85kmh"):
    row = desc_rows[spd]
    d = descent_sim(packV2, row, 45.0, 45.0)
    # rebuild trajectory for plotting
    tc, soc = 45.0, SOC_TARGET
    ys = []
    for k in range(int(np.ceil(row["time_10km_s"]))):
        acc = float(packV2.p_chg_cont(tc, soc))
        head = max(0.0, (SOC_TOP - soc)) * packV2.nameplate_kwh * 3.6e6
        p_bat = min(row["retardation_required_kW"] * 1e3 * ETA_W2B, acc, head)
        _, q_cell, _ = packV2.solve_current(np.array([-p_bat]),
                                            np.array([soc]), tc)
        q = float(q_cell[0]) * packV2.n_cells
        soc += (p_bat - q) / (packV2.nameplate_kwh * 3.6e6)
        tc = packV2.thermal_step(tc, q, 45.0, 1.0)
        ys.append(tc)
    ax.plot(np.arange(len(ys)) / 60.0, ys, "--",
            label=f"4.6 row {spd}, battery-first blend")
ax.axhline(wp.T_CELL_MAX_CONT, color="r", lw=0.8)
ax.annotate("55 C continuous ceiling", (0.5, wp.T_CELL_MAX_CONT + 0.1),
            color="r", fontsize=7)
ax.set_xlabel("time [min]")
ax.set_ylabel("cell temperature [C]")
ax.set_title("descent charging at +45 C ambient - pack temperature")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig_ws3_02_descent_thermal.png"))
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4))
r_arr = np.array(R["regen_acceptance_table"]["rows"])
ax.plot(r_arr[:, 0], r_arr[:, 3], "-o", ms=3, label="V2 pack continuous")
ax.plot(r_arr[:, 0], r_arr[:, 4], "-s", ms=3, label="V2 pack 10 s pulse")
ax.plot(r_arr[:, 0], r_arr[:, 6], "-^", ms=3, label="V1 light (LTO-10) cont")
ax.axhline(kw(REGEN_BUS_FULL), color="k", ls=":", lw=0.8)
ax.annotate("75 kW wheel cap at bus (64.9 kW)", (-29, kw(REGEN_BUS_FULL) + 2),
            fontsize=7)
ax.axhline(kw(DESCENT_BUS_MAX), color="g", ls=":", lw=0.8)
ax.annotate("worst 4.6 descent at bus (39.4 kW)", (-29, kw(DESCENT_BUS_MAX) + 2),
            fontsize=7, color="g")
ax.axvspan(-30, 0, color="b", alpha=0.05)
ax.set_xlabel("cell temperature [C]")
ax.set_ylabel("charge acceptance at bus [kW]")
ax.set_title("regen acceptance vs temperature (SOC 55%)")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig_ws3_03_regen_acceptance.png"))
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4))
colors = {"LTO-10": "tab:blue", "LTO-23": "tab:orange", "LTO-45": "tab:green"}
for name in ("LTO-10", "LTO-23", "LTO-45"):
    fr = R["frontier"][name]
    xs = [fr["dis_pulse_120kW"]["kWh_min"], fr["chg_pulse_110kW"]["kWh_min"],
          fr["chg_cont_50kW_45C"]["kWh_min"], fr["voltage_window_288s"]["kWh_min"]]
    labs = ["120 kW dis", "110 kW chg", "50 kW cont", "288s window"]
    ax.scatter(xs, [name] * 4, c=[colors[name]] * 4, s=25)
    for x, lab in zip(xs, labs):
        ax.annotate(lab, (x, name), fontsize=6, rotation=30,
                    textcoords="offset points", xytext=(2, 5))
    ax.scatter([fr["governing_kWh"]], [name], marker="x", c="r", s=60)
ax.axvline(FLOOR_V2, color="k", ls=":", lw=0.8)
ax.annotate("V2 floor 3.5 kWh", (FLOOR_V2 + 0.1, 0.1), fontsize=7)
ax.axvline(FLOOR_V1, color="k", ls=":", lw=0.8)
ax.annotate("V1 floor 1.5 kWh", (FLOOR_V1 + 0.1, 1.6), fontsize=7)
ax.set_xlabel("minimum pack nameplate forced by each constraint [kWh]")
ax.set_title("power-vs-energy frontier: what actually sizes the pack "
             "(red x = governing)")
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig_ws3_04_frontier.png"))
plt.close(fig)

# =====================================================================
# 14. GENERATED REPORT TABLES + WRITE-OUT
# =====================================================================
print("== 14. tables + results.json")


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


tb("<!-- AUTO-GENERATED by run_ws3.py - paste verbatim into REPORT_WS3.md -->")
tb()
tb("### T1. Chemistry trade (minimum ~660 V pack meeting the R8 power set "
   "warm)")
tb()
tb("| Criterion | LTO-23 | LFP-P-20 | NMC-P-40 |")
tb("|---|---|---|---|")
ct = R["chemistry_trade"]
tb("| min pack (s x p) | " + " | ".join(
    f"{ct[n]['series']}s{ct[n]['parallel']}p" for n in
    ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| nameplate kWh | " + " | ".join(
    f2(ct[n]["nameplate_kWh"]) for n in ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| pack mass kg | " + " | ".join(
    f1(ct[n]["pack_mass_kg"]) for n in ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| charge accept at -10 C, kW at bus | " + " | ".join(
    f1(ct[n]["chg_cont_at_minus10C_kW_bus"]) for n in
    ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| covers 64.9 kW full regen cold | " + " | ".join(
    str(ct[n]["covers_full_regen_cold"]) for n in
    ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| nameplate needed for full cold regen, kWh | " + " | ".join(
    f1(ct[n]["nameplate_needed_to_cover_regen_at_minus10C_kWh"]) for n in
    ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| full-DoD cycle life (EFC) | " + " | ".join(
    f"{ct[n]['efc100']:.0f}" for n in ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| calendar life at +45 C, yr | " + " | ".join(
    f1(ct[n]["cal_life_45C_yr"]) for n in ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb("| thermal-runaway class | " + " | ".join(
    ct[n]["thermal_runaway"].split(" (")[0] for n in
    ("LTO-23", "LFP-P-20", "NMC-P-40")) + " |")
tb()
hy = ct["hybrid_SC_note"]
tb(f"Hybrid option: {hy['n_cells']} SC-3000 cells "
   f"({hy['sc_bank_mass_kg']:.0f} kg, {hy['sc_bank_volume_L']:.0f} L) to "
   f"cover only the {hy['target_buffer_kWh']:.2f} kWh 5-min swing, plus a "
   f"~{hy['dcdc_mass_kg']:.0f} kg 120 kW DC/DC - rejected.")
tb()

pd_ = R["pack_designs"]["V2_and_V1_recommended"]
pl = R["pack_designs"]["V1_light_option"]
tb("### T2. Pack designs on the shared spine")
tb()
tb("| Quantity | V2 = V1 (recommended) | V1 light option |")
tb("|---|---|---|")
tb(f"| cell / config | LTO-23, 288s1p | LTO-10, 288s1p |")
tb(f"| nameplate | {f2(pd_['nameplate_kWh'])} kWh | {f2(pl['nameplate_kWh'])} kWh |")
tb(f"| usable (15-90%) at bus | {f2(pd_['usable_kWh_bus'])} kWh | "
   f"{f2(pl['usable_kWh_bus'])} kWh |")
tb(f"| nominal voltage | {f1(pd_['v_nominal'])} V | {f1(pl['v_nominal'])} V |")
tb(f"| operating window (OCV 15-90%) | {f1(pd_['v_ocv_at_window'][0])}-"
   f"{f1(pd_['v_ocv_at_window'][1])} V | same |")
tb(f"| charge ceiling / protect | {f1(pd_['v_charge_ceiling'])} / "
   f"{f1(pd_['v_protect_max'])} V | same |")
tb(f"| pack mass (est.) | {f1(pd_['pack_mass_kg'])} kg | {f1(pl['pack_mass_kg'])} kg |")
tb(f"| pack volume (est.) | {f1(pd_['pack_volume_L'])} L | {f1(pl['pack_volume_L'])} L |")
cr = R["c_rate_check"]["V2_LTO23"]
crl = R["c_rate_check"]["V1_light_LTO10"]
tb(f"| C-rate at 120 kW dis | {f2(cr['c_at_120kW_dis'])}C "
   f"({cr['i_at_120kW_A']:.0f} A) | {f2(crl['c_at_120kW_dis'])}C |")
tb(f"| C-rate at 110 kW chg | {f2(cr['c_at_110kW_chg'])}C | "
   f"{f2(crl['c_at_110kW_chg'])}C |")
tb(f"| C-rate at 50 kW cont chg | {f2(cr['c_at_50kW_cont_chg'])}C | "
   f"{f2(crl['c_at_50kW_cont_chg'])}C |")
tb()

tb("### T3. Capability vs temperature (SOC 55%, kW at bus, V2 pack)")
tb()
tb("| Cell T | dis 10 s | chg 10 s | chg cont | R8 met? |")
tb("|---|---|---|---|---|")
for i, t in enumerate(T_LIST):
    cm = R["capability_maps"]["V2_LTO23"]
    j = SOC_LIST.index(0.55)
    d, cpu, cc = (cm["dis_pulse10_kW"][i][j], cm["chg_pulse10_kW"][i][j],
                  cm["chg_cont_kW"][i][j])
    met = "yes" if (d >= 120 and cpu >= 110 and cc >= 50) else \
        ("50 kW cont yes; peaks derated" if cc >= 50 else "no")
    tb(f"| {t:+.0f} C | {f1(d)} | {f1(cpu)} | {f1(cc)} | {met} |")
tb()

lit = R["descent_thermal"]["literal_50kW_24min_45C"]
tb("### T4. Descent thermal (+45 C ambient, battery-first blend, R2 order)")
tb()
tb("| Case | E to battery | E to resistor | E to friction | peak cell T | "
   "SOC ceiling hit |")
tb("|---|---|---|---|---|---|")
for spd in ("25kmh", "35kmh", "40kmh", "50kmh", "60kmh", "70kmh", "85kmh",
            "100kmh"):
    d = R["descent_thermal"]["rows_45C"][spd]
    tfill = f"{d['t_soc_ceiling_s']:.0f} s" if d["t_soc_ceiling_s"] else "-"
    tb(f"| 4.6 row {spd} | {f2(d['E_battery_kWh'])} kWh | "
       f"{f2(d['E_resistor_kWh'])} kWh | {f2(d['E_friction_kWh'])} kWh | "
       f"{f1(d['t_cell_peak_C'])} C | {tfill} |")
tb(f"| literal 50 kW x 24 min | (SOC-pinned capability run) | - | - | "
   f"{f1(lit['t_cell_peak_C'])} C | "
   f"{lit['soc_ceiling_hit_s']:.0f} s unmanaged |")
tb()
tb(f"Steady heat at 50 kW continuous charge, +45 C: "
   f"{f2(lit['heat_end_kW'])} kW; steady cell temperature "
   f"{f1(lit['t_steady_C'])} C (ceiling 55 C).")
tb()
rb_ = R["descent_thermal"]["resistor_bound"]
dworst = R["descent_thermal"]["rows_45C_payload120"][rb_["worst_payload120_row"]]
tb(f"+20% payload sweep (WS3-r1-F6; {rb_['payload120_mass_kg']:.0f} kg, "
   f"WS1 payload convention), all 8 rows at +45 C and -10 C: worst "
   f"resistor power {rb_['max_resistor_kW_payload120']:.1f} kW vs the "
   f"{rb_['rating_bus_kW']:.0f} kW R2 rating "
   f"({rb_['margin_at_payload120_kW']:.1f} kW margin; GVW worst "
   f"{rb_['max_resistor_kW_gvw']:.1f} kW); worst-row friction "
   f"{rb_['friction_kWh_max_any_row']:.2f} kWh - the blend model now "
   f"enforces the rating and books overflow to friction instead of "
   f"assuming it zero. Worst +20% row ({rb_['worst_payload120_row']}, "
   f"+45 C): battery {dworst['E_battery_kWh']:.2f} kWh, resistor "
   f"{dworst['E_resistor_kWh']:.2f} kWh, friction "
   f"{dworst['E_friction_kWh']:.2f} kWh, peak cell "
   f"{dworst['t_cell_peak_C']:.1f} C.")
tb()

pre = R["preconditioning"]
tb("### T5. Cold strategy")
tb()
tb(f"- Preconditioning (R7, below 0 C): {f1(pre['heater_kW'])} kW into the "
   f"plates; -10 C to +10 C in {pre['time_to_10C_s']/60:.1f} min, "
   f"{f2(pre['energy_to_10C_kWh'])} kWh electrical from the genset.")
cc_ = R["cold_case_recompute"]
tb(f"- Cold-soaked (unpreconditioned) LTO at -10 C accepts "
   f"{f1(cc_['lto_chg_accept_cont_at_minus10C_bus_kW'])} kW continuous at "
   f"the bus = {f1(cc_['lto_chg_accept_cont_at_minus10C_wheel_kW'])} kW at "
   f"the wheel - above the 75 kW cap. The WS1 4.15 cold case "
   f"(regen disabled) does not occur with this chemistry.")
tb(f"- V1 genset average, cold, 4 kW aux: WS1 assumption "
   f"{f1(cc_['V1_N2_cold_ws1_regen_disabled_kW'])} kW "
   f"(+{cc_['penalty_ws1_pct']:.0f}%); with LTO acceptance "
   f"{f2(cc_['V1_N2_cold_LTO_aux4_kW'])} kW "
   f"(+{cc_['penalty_lto_aux4_pct']:.0f}% with WS1's warm 0.97 scalars) / "
   f"{f2(cc_['V1_N2_cold_LTO_aux4_corrected_kW'])} kW "
   f"(+{cc_['penalty_lto_aux4_corrected_pct']:.0f}% with the cold "
   f"resistance model in the loop, WS3-r1-F3) - headline +20-25%. "
   f"Friction-brake energy on VOLT-SUB stays "
   f"{f2(cc_['V1_friction_cold_LTO_kWh'])} kWh instead of "
   f"{f2(cc_['V1_friction_cold_ws1_kWh'])} kWh.")
r8c = R["r8_compliance"]
tb(f"- Dispatch gates: full 120 kW discharge from cell T >= "
   f"{r8c['dis_120kW_over_SOC_40_90']:.1f} C; full 110 kW charge from "
   f"{r8c['chg_110kW_over_SOC_15_85']:.1f} C; 50 kW continuous descent "
   f"charge available over the whole R7 envelope including -10 C "
   f"cold soak. Gates are computed against the {V_FLOOR_PACK:.1f} V pack "
   f"floor = the exported operating_min_V; a higher WS2 electronics floor "
   f"derates them per T12 (WS3-r1-F1).")
tb()

de = R["duty_ensemble"]
tb("### T6. Duty ensemble (8 seeds, R9) - battery at the bus, 25 C")
tb()
tb("| Quantity | V1 const genset | V1 start-stop | V2 i-MMD |")
tb("|---|---|---|---|")
tb("| peak discharge kW | " + " | ".join(
    f"{de[m]['peak_dis_kW']['min']:.1f}-{de[m]['peak_dis_kW']['max']:.1f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
tb("| peak charge kW | " + " | ".join(
    f"{de[m]['peak_chg_kW']['min']:.1f}-{de[m]['peak_chg_kW']['max']:.1f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
tb("| peak C discharge | " + " | ".join(
    f"{de[m]['peak_c_dis']['max']:.2f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
tb("| cycle-avg heat kW (max) | " + " | ".join(
    f"{de[m]['heat_avg_kW']['max']:.3f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
tb("| round-trip eff (min) | " + " | ".join(
    f"{de[m]['eta_roundtrip']['min']:.4f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
tb("| rainflow cycles/trace (max) | " + " | ".join(
    f"{de[m]['rainflow_cycles_per_trace']['max']:.0f}"
    for m in ("V1_const_genset", "V1_startstop", "V2_iMMD")) + " |")
st_env = de["V1_startstop"]["starts_per_h"]
tb(f"| genset starts/h (start-stop) | - | "
   f"{st_env['min']:.1f}-{st_env['max']:.1f} | - |")
tb()
pc_ = R["power_convention"]
tb(f"Convention ledger (WS3-r1-F2): R8's 120 kW descends from WS1's "
   f"STORED-side {pc_['r8_reference_stored_kW']:.3f} kW = "
   f"{pc_['r8_reference_bus_kW']:.1f} kW at the bus terminals; the V2 "
   f"ensemble peak above is bus-side {pc_['ensemble_peak_bus_kW']:.1f} kW "
   f"= {pc_['ensemble_peak_stored_kW']:.1f} kW stored-side. Like-for-like "
   f"at the bus the exceedance is "
   f"+{pc_['exceedance_like_for_like_bus_pct']:.1f}%; recommended "
   f"restatement (ES-4): {pc_['recommended_restatement_bus_kW']:.0f} kW "
   f"discharge / {pc_['recommended_restatement_chg_bus_kW']:.0f} kW "
   f"charge, explicitly bus-side.")
tb()
lf = R["life"]
tb("### T7. Life projection (ensemble-max damage, throughput model)")
tb()
tb("| Quantity | V1 start-stop | V2 i-MMD |")
tb("|---|---|---|")
tb(f"| micro-cycles/year | {lf['V1_startstop']['micro_cycles_per_year']:.2e} "
   f"| {lf['V2_iMMD']['micro_cycles_per_year']:.2e} |")
tb(f"| cycle damage/year | {lf['V1_startstop']['cycle_damage_per_year']:.2e} "
   f"| {lf['V2_iMMD']['cycle_damage_per_year']:.2e} |")
tb(f"| cycle life, years | {lf['V1_startstop']['cycle_life_years']:.0f} | "
   f"{lf['V2_iMMD']['cycle_life_years']:.0f} |")
tb(f"| calendar life at 30 C avg, years | "
   f"{lf['V1_startstop']['calendar_life_years_at_30C']:.1f} | "
   f"{lf['V2_iMMD']['calendar_life_years_at_30C']:.1f} |")
tb(f"| combined, years (30 C avg / always-45 C bound) | "
   f"{lf['V1_startstop']['combined_years_at_30C']:.1f} / "
   f"{lf['V1_startstop']['combined_years_at_45C_bound']:.1f} | "
   f"{lf['V2_iMMD']['combined_years_at_30C']:.1f} / "
   f"{lf['V2_iMMD']['combined_years_at_45C_bound']:.1f} |")
tb()

em_ = R["efficiency_map"]
tb("### T8. One-way efficiency vs power and temperature (SOC 55%, replaces "
   "the 0.97 scalar per R9)")
tb()
tb("| P at bus | " + " | ".join(f"{t:+.0f} C dis" for t in em_["T_C"]) +
   " | " + " | ".join(f"{t:+.0f} C chg" for t in em_["T_C"]) + " |")
tb("|---|" + "---|" * 8)
for j, pkw in enumerate(em_["P_kW"]):
    row = [f"| {pkw} kW "]
    for i in range(4):
        row.append(f"| {em_['dis'][i][j]:.4f} ")
    for i in range(4):
        row.append(f"| {em_['chg'][i][j]:.4f} ")
    tb("".join(row) + "|")
tb()

fr = R["frontier"]
tb("### T9. Power-vs-energy frontier (minimum nameplate kWh forced by each "
   "constraint, 25 C)")
tb()
tb("| Constraint | LTO-10 | LTO-23 | LTO-45 |")
tb("|---|---|---|---|")
for lab, key in (("120 kW discharge pulse", "dis_pulse_120kW"),
                 ("110 kW charge pulse", "chg_pulse_110kW"),
                 ("50 kW continuous charge at 45 C", "chg_cont_50kW_45C"),
                 ("288s voltage window (1P)", "voltage_window_288s")):
    tb(f"| {lab} | " + " | ".join(
        f2(fr[n][key]["kWh_min"]) for n in ("LTO-10", "LTO-23", "LTO-45")) + " |")
tb("| **governing** | " + " | ".join(
    f"**{f2(fr[n]['governing_kWh'])}**" for n in
    ("LTO-10", "LTO-23", "LTO-45")) + " |")
tb()

tb("### T10. Heat to the WS6 ledger (battery workstream slice)")
tb()
tb("| Component | Case | Heat | Duration | Sink |")
tb("|---|---|---|---|---|")
for h in R["heat_ledger_WS6"]:
    d = h["duration_s"]
    ds = f"{d:.0f} s" if isinstance(d, float) else str(d)
    tb(f"| {h['component']} | {h['case']} | {h['heat_kW']:+.2f} kW | {ds} | "
       f"{h['sink']} |")
tb()

sc_ = R["sanity_checks"]
tb("### T11. First-principles sanity checks")
tb()
tb("| Check | Hand calculation | Model | Verdict |")
tb("|---|---|---|---|")
tb(f"| nameplate 288 x 23 Ah x 2.30 V | "
   f"{sc_['nameplate_arithmetic_kWh']['computed']:.3f} kWh | "
   f"{sc_['nameplate_arithmetic_kWh']['model']:.3f} kWh | exact |")
tb(f"| descent 25 km/h energy balance | "
   f"{sc_['descent25_energy_balance_kWh']['wheel_energy_at_bus']:.2f} kWh "
   f"at bus | battery+resistor "
   f"{sc_['descent25_energy_balance_kWh']['battery_plus_resistor']:.2f} kWh "
   f"| closes |")
tb(f"| heat at 50 kW cont charge | I^2R = "
   f"{sc_['heat_at_50kW_hand_calc']['q_pack_kW']:.2f} kW "
   f"({sc_['heat_at_50kW_hand_calc']['i_cell_A']:.0f} A) | "
   f"{sc_['heat_at_50kW_hand_calc']['model_end_kW']:.2f} kW | agrees |")
tb(f"| preconditioning -10 to +10 C | C_th x 20 K / 8 kW = "
   f"{sc_['precondition_energy']['heater_time_s_hand']:.0f} s | "
   f"{sc_['precondition_energy']['model_time_to_10C_s']:.0f} s | agrees |")
tb(f"| V2 cycle damage/yr | throughput shortcut "
   f"{sc_['v2_damage_per_year']['throughput_shortcut']:.2e} | rainflow "
   f"{sc_['v2_damage_per_year']['rainflow_model']:.2e} | same order |")
tb(f"| R8 vs ensemble (like-for-like at bus, F2) | R8 reference "
   f"{sc_['r8_exceedance_info']['r8_reference_stored_kW']:.1f} kW stored = "
   f"{sc_['r8_exceedance_info']['r8_reference_bus_kW']:.1f} kW bus | "
   f"8-seed max {sc_['r8_exceedance_info']['ensemble_peak_dis_kW']:.1f} kW "
   f"bus ({sc_['r8_exceedance_info']['ensemble_peak_dis_stored_kW']:.1f} "
   f"stored), capability "
   f"{sc_['r8_exceedance_info']['pack_capability_warm_kW']:.1f} kW | "
   f"see ES-4 |")
tb()

bw_ = R["bus_window_consistency"]
tb("### T12. R8 120 kW availability vs the WS2 electronics voltage floor "
   "(resolves WS3-r1-F1)")
tb()
tb("| electronics floor (V/cell) | pack floor V | 120 kW gate "
   "(SOC 40-90) | I at gate | bus V at gate |")
tb("|---|---|---|---|---|")
for e_ in bw_["dis_gate_vs_electronics_floor"]:
    if e_["dis_120kW_gate_C_over_SOC_40_90"] is not None:
        tb(f"| {e_['v_floor_cell_V']:.2f} | {e_['v_floor_pack_V']:.1f} | "
           f"{e_['dis_120kW_gate_C_over_SOC_40_90']:+.1f} C | "
           f"{e_['I_at_gate_A']:.0f} A | {e_['V_bus_at_gate_V']:.1f} V |")
    else:
        tb(f"| {e_['v_floor_cell_V']:.2f} | {e_['v_floor_pack_V']:.1f} | "
           f"not available in envelope | - | - |")
tb()
opw_ = bw_["r8_operating_points"]["dis_120kW_warm_soc40"]
opg_ = bw_["r8_operating_points"]["dis_120kW_at_cold_gate_soc40"]
op15_ = bw_["r8_operating_points"]["dis_120kW_warm_soc15_info"]
opc_ = bw_["r8_operating_points"]["chg_110kW_at_gate_soc85"]
_r185 = [e_ for e_ in bw_["dis_gate_vs_electronics_floor"]
         if abs(e_["v_floor_cell_V"] - 1.85) < 1e-9][0]
tb(f"Reading: the 1.50 V/cell row IS the exported window - operating_min_V "
   f"{V_FLOOR_PACK:.1f} V and the {opg_['T_C']:+.1f} C gate are computed "
   f"against the same floor, so window and gates are jointly satisfiable. "
   f"Round 1's {_r185['v_floor_pack_V']:.1f} V operating_min_V (an "
   f"undocumented 1.85 V/cell allocation) is retained as the 1.85 row: "
   f"enforcing it as a hard floor moves the 120 kW gate from "
   f"{opg_['T_C']:+.1f} C to "
   f"{_r185['dis_120kW_gate_C_over_SOC_40_90']:+.1f} C. Operating points: "
   f"120 kW warm (25 C, SOC 40) = {opw_['I_A']:.0f} A at "
   f"{opw_['V_bus_V']:.1f} V; at the cold gate = {opg_['I_A']:.0f} A at "
   f"{opg_['V_bus_V']:.1f} V; warm at SOC 15 the bus sits at "
   f"{op15_['V_bus_V']:.1f} V (full power below SOC 40 is not guaranteed - "
   f"WS5 dispatch limit). Charge side: the 110 kW pulse at its "
   f"{r8c['chg_110kW_over_SOC_15_85']:+.1f} C gate rides the bus to "
   f"{opc_['V_bus_V']:.1f} V - above the "
   f"{packV2.ns * packV2.cell['v_chg_ceiling']:.1f} V continuous ceiling, "
   f"inside the {packV2.ns * packV2.cell['v_max_protect']:.1f} V "
   f"transient/protect ceiling.")
tb()
s252_ = bw_["series_252_bound"]
tb(f"252s end of the offered series range (exact, not interpolated): "
   f"{s252_['nameplate_kWh']:.2f} kWh nameplate, nominal "
   f"{s252_['v_nominal_V']:.1f} V, window {s252_['operating_min_V']:.1f}-"
   f"{s252_['operating_max_V']:.1f} V (transient "
   f"{s252_['transient_max_V']:.1f} V); the gates move WARMER - 120 kW "
   f"discharge from {s252_['dis_120kW_gate_C_over_SOC_40_90']:+.1f} C, "
   f"110 kW charge from {s252_['chg_110kW_gate_C_over_SOC_15_85']:+.1f} C - "
   f"and warm 120 kW current rises to {s252_['I_120kW_warm_A']:.0f} A "
   f"({s252_['V_bus_120kW_warm_V']:.1f} V), reaching "
   f"{s252_['I_120kW_at_gate_A']:.0f} A "
   f"({s252_['V_bus_120kW_at_gate_V']:.1f} V) at its own gate.")
tb()

tb("### Machine-readable interface block")
tb()
tb("```json")
tb(json.dumps(R["interface_WS3"], indent=1, default=float))
tb("```")

with open(os.path.join(HERE, "tables_ws3.md"), "w") as f:
    f.write("\n".join(TB) + "\n")

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(R, f, indent=1, default=float)

print("\nDone. Wrote results.json, tables_ws3.md, regen_acceptance.csv, "
      "figs/*.png")
print(f"V2 pack: {packV2.nameplate_kwh:.2f} kWh, {packV2.mass_kg:.0f} kg; "
      f"usable at bus {usableV2:.2f} kWh vs floor {FLOOR_V2} kWh")
print(f"Descent 50 kW/24 min at +45 C: peak cell "
      f"{lit['t_cell_peak_C']:.1f} C (ceiling 55 C)")
print(f"Cold -10 C acceptance: {kw(acc_m10_bus):.1f} kW bus "
      f"({kw(acc_m10_bus / ETA_W2B):.1f} kW wheel-equivalent)")
