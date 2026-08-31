"""
Project Volt - WS5 (supervisory controls)
Upstream ingestion + provenance. THIS IS THE HOT-SWAP SEAM.

Everything WS5 consumes from another workstream enters through this module,
read-only, at run time - nothing is transcribed by hand. Every consumed file
is SHA256-pinned into the vintage record so a corrected upstream vintage
(e.g. a re-adjudicated WS4 KX round) swaps in by re-running run_ws5.py with
no code change, and the pins in results_ws5.json flip accordingly.

Consumed (read-only):
  WS1  volt_params / volt_physics / volt_cycles  (cycle construction, road
       load, vehicle parameters)                              [BASELINE_v1]
  WS2  results.json interface (bus window, machine, resistor, chopper
       control, traction-control law), effmap_motor_inverter_662V.csv,
       capability_vs_rpm.csv, regen_adhesion_curves.csv,
       traction_envelope.csv                                  [R10/R12/R13]
  WS3  results.json interface (pack, SOC allocation, capability maps,
       thermal), regen_acceptance.csv, ws3_pack/ws3_cells models  [R16/R8]
  WS4  results_ws4.json interface (series_duty_v2 - LIVE design input,
       spin_drag_operational_note_r22d, v1_start_stop, pinned points),
       ws4_models (4HK1-V2C-W and V3307-V1C-W Willans maps, PM generator
       maps), ws4_chain (R12 traction chain), ws4_sim (WS4's own asserted
       scalar fast paths, imported so WS5's set-point arithmetic is
       bit-identical to the ratified simulator's)              [R18/R22b/d]

NOT consumed, by ruling: interface_ws4.gate_g1 is an ARCHIVED record block
carrying status "executed_kill_2026-08-30". No field of it is a live
requirement (BASELINE_v3). There is no gate, no clutch, no mode selection
and no synchronisation anywhere in WS5.
"""
import hashlib
import json
import os
import sys

# WS1/WS2/WS3/WS4 are READ-ONLY to WS5. Importing their modules would
# otherwise write .pyc caches into THEIR folders; this switch stops WS5
# writing anything at all outside WS5_controls/.
sys.dont_write_bytecode = True

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
WS1_DIR = os.path.join(ROOT, "WS1_loads_duty_cycles")
WS2_DIR = os.path.join(ROOT, "WS2_traction_motor")
WS3_DIR = os.path.join(ROOT, "WS3_battery")
WS4_DIR = os.path.join(ROOT, "WS4_genset")

for _d in (WS1_DIR, WS3_DIR, WS4_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import volt_params as vp_params            # noqa: E402  WS1
import volt_physics as vph                 # noqa: E402  WS1
import volt_cycles as vcyc                 # noqa: E402  WS1
import ws3_cells as w3c                    # noqa: E402  WS3
import ws3_pack as w3p                     # noqa: E402  WS3
import ws4_models as w4m                   # noqa: E402  WS4
import ws4_chain as w4c                    # noqa: E402  WS4

VEH = vp_params.VEH
DL = vp_params.DL
AUX = vp_params.AUX
CTL = vp_params.CTL
G = vp_params.G


# ------------------------------------------------------------- provenance
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# Files WS5 reads from other workstreams. Order is fixed so the exported
# pin block is byte-stable.
CONSUMED = [
    ("WS1/volt_params.py", os.path.join(WS1_DIR, "volt_params.py")),
    ("WS1/volt_physics.py", os.path.join(WS1_DIR, "volt_physics.py")),
    ("WS1/volt_cycles.py", os.path.join(WS1_DIR, "volt_cycles.py")),
    ("WS1/results.json", os.path.join(WS1_DIR, "results.json")),
    ("WS2/results.json", os.path.join(WS2_DIR, "results.json")),
    ("WS2/data/effmap_motor_inverter_432V.csv",
     os.path.join(WS2_DIR, "data", "effmap_motor_inverter_432V.csv")),
    ("WS2/data/effmap_motor_inverter_662V.csv",
     os.path.join(WS2_DIR, "data", "effmap_motor_inverter_662V.csv")),
    ("WS2/data/effmap_motor_inverter_749V.csv",
     os.path.join(WS2_DIR, "data", "effmap_motor_inverter_749V.csv")),
    ("WS2/data/capability_vs_rpm.csv",
     os.path.join(WS2_DIR, "data", "capability_vs_rpm.csv")),
    ("WS2/data/regen_adhesion_curves.csv",
     os.path.join(WS2_DIR, "data", "regen_adhesion_curves.csv")),
    ("WS2/data/traction_envelope.csv",
     os.path.join(WS2_DIR, "data", "traction_envelope.csv")),
    ("WS3/results.json", os.path.join(WS3_DIR, "results.json")),
    ("WS3/regen_acceptance.csv", os.path.join(WS3_DIR, "regen_acceptance.csv")),
    ("WS3/ws3_cells.py", os.path.join(WS3_DIR, "ws3_cells.py")),
    ("WS3/ws3_pack.py", os.path.join(WS3_DIR, "ws3_pack.py")),
    ("WS4/results_ws4.json", os.path.join(WS4_DIR, "results_ws4.json")),
    ("WS4/ws4_models.py", os.path.join(WS4_DIR, "ws4_models.py")),
    ("WS4/ws4_chain.py", os.path.join(WS4_DIR, "ws4_chain.py")),
    # ws4_sim.py is imported by ws5_supervisor for WS4's own asserted
    # scalar fast paths (_bsfc_fast, _gen_elec_from_shaft), so it is a
    # consumed input and is pinned like any other.
    ("WS4/ws4_sim.py", os.path.join(WS4_DIR, "ws4_sim.py")),
    ("WS4/data/bsfc_map_V2_candidate.csv",
     os.path.join(WS4_DIR, "data", "bsfc_map_V2_candidate.csv")),
    ("WS4/data/bsfc_map_V1_candidate.csv",
     os.path.join(WS4_DIR, "data", "bsfc_map_V1_candidate.csv")),
    ("WS4/data/gen_eff_map_V2.csv",
     os.path.join(WS4_DIR, "data", "gen_eff_map_V2.csv")),
    ("WS4/data/gen_eff_map_V1.csv",
     os.path.join(WS4_DIR, "data", "gen_eff_map_V1.csv")),
]


def input_pins():
    return {k: sha256(p) for k, p in CONSUMED}


# ------------------------------------------------------------ WS2 exports
with open(os.path.join(WS2_DIR, "results.json")) as _f:
    WS2 = json.load(_f)
WS2_IF = WS2["interface"]

BUS_NOMINAL_V = float(WS2_IF["dc_bus"]["nominal_V"])
BUS_MIN_V, BUS_MAX_V = [float(x) for x in WS2_IF["dc_bus"]["window_V"]]
BUS_TRANSIENT_V = float(WS2_IF["dc_bus"]["transient_10s_V"])
CHOPPER_BACKSTOP_V = float(WS2_IF["dc_bus"]["chopper_hw_overvoltage_backstop_V"])

RES_OHM = float(WS2_IF["resistor"]["R_ohm"])
RES_CEILING_KW = float(WS2_IF["resistor"]["second_stage_ceiling_kW"]["value"])
RES_CEILING_CASE = WS2_IF["resistor"]["second_stage_ceiling_kW"]["governing_case"]
RES_MIN_ANY_V_KW = float(WS2_IF["resistor"]["P_cont_kW_any_bus_V"]["value"])
RES_CONTROL = WS2_IF["resistor"]["control"]
RES_SINK = WS2_IF["resistor"]["sink"]
BLOWER_KW = float(WS2_IF["dc_bus_loads_coexisting"]["resistor_blower_kW"])
HEATER_KW = float(WS2_IF["dc_bus_loads_coexisting"]["pack_heater_kW"])

MOTOR_RATIO = float(WS2_IF["machine"]["ratio"])
MOTOR_S1_KW = float(WS2_IF["machine"]["S1_kW"])
MOTOR_S2_KW = float(WS2_IF["machine"]["S2_10min_kW"])
MOTOR_T_PEAK_NM = float(WS2_IF["machine"]["T_peak_Nm"])
MOTOR_RPM_MAX = float(WS2_IF["machine"]["rpm_max"])
MOTOR_PEAK_1MIN_WORST_KW = float(
    WS2_IF["machine"]["peak_1min_kW"]["worst_case_value"])
MOTOR_PEAK_1MIN_CASES = {k: float(v) for k, v in
                         WS2_IF["machine"]["peak_1min_kW"]["cases"].items()}
INV_TJ_CASES = {k: float(v) for k, v in
                WS2_IF["electrical_ratings"]["inverter_Tj_at_continuous_rating_C"]
                ["cases"].items()}
INV_TJ_WORST_C = float(
    WS2_IF["electrical_ratings"]["inverter_Tj_at_continuous_rating_C"]["value"])
INV_TJ_WORST_CASE = WS2_IF["electrical_ratings"][
    "inverter_Tj_at_continuous_rating_C"]["governing_case"]
TC_LAW = WS2_IF["traction_control"]["torque_limit_law"]

# WS2 capability curve (peak / continuous shaft torque vs rpm)
_CAP = np.genfromtxt(os.path.join(WS2_DIR, "data", "capability_vs_rpm.csv"),
                     delimiter=",", names=True)
CAP_RPM = np.asarray(_CAP["rpm"], float)
CAP_T_PEAK_662 = np.asarray(_CAP["T_peak_662V_Nm"], float)
CAP_T_CONT_OIL = np.asarray(_CAP["T_cont_oilspray_662V_Nm"], float)


def motor_peak_torque(rpm):
    """WS2 measured peak shaft torque envelope at the R10 nominal bus."""
    return np.interp(np.asarray(rpm, float), CAP_RPM, CAP_T_PEAK_662)


def motor_cont_torque(rpm):
    """WS2 spray-cooled continuous shaft torque envelope (R13 build)."""
    return np.interp(np.asarray(rpm, float), CAP_RPM, CAP_T_CONT_OIL)


# WS2 adhesion curves (E23 day-one traction-control input)
def load_adhesion_curves():
    rows = {}
    path = os.path.join(WS2_DIR, "data", "regen_adhesion_curves.csv")
    with open(path) as f:
        hdr = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) != len(hdr):
                continue
            rows.setdefault(p[0], []).append(
                (float(p[1]), float(p[2]), float(p[3]), p[4]))
    return rows


ADHESION = load_adhesion_curves()

WS2_TRACTION_ENVELOPE = WS2["traction"]["envelope"]
WS2_MU_REQUIRED = WS2["traction"]["mu_required"]


# ------------------------------------------------------------ WS3 exports
with open(os.path.join(WS3_DIR, "results.json")) as _f:
    WS3 = json.load(_f)
WS3_IF = WS3["interface_WS3"]

PACK_V2 = WS3_IF["packs"]["V2"]
USABLE_BUS_KWH = float(PACK_V2["usable_bus_kWh"])
NAMEPLATE_KWH = float(PACK_V2["nameplate_kWh"])
SOC_TARGET = float(WS3_IF["soc_strategy"]["target"])
SOC_END_STOPS = [float(x) for x in
                 WS3_IF["soc_strategy"]["allocation"]["V2"]["end_stops_pct_nameplate"]]
GENSET_HYST_V2_KWH = float(
    WS3_IF["soc_strategy"]["allocation"]["V2"]["genset_hysteresis_kWh"])
GENSET_HYST_V1_KWH = float(
    WS3_IF["soc_strategy"]["allocation"]["V1"]["genset_hysteresis_kWh"])
V1_FIXED_POINT_BUS_KW = float(WS3["params_ws3"]["v1_startstop"]["p_on_bus_kW"])
V1_BAND_KWH = float(WS3["params_ws3"]["v1_startstop"]["band_kWh"])
R8_DIS_BUS_KW = 125.0     # R12/ES-4 restatement of R8, bus-side
R8_CHG_BUS_KW = 110.0     # R12/ES-4 restatement of R8, bus-side
R8_CHG_CONT_BUS_KW = float(WS3["params_ws3"]["R8_peaks_bus_kW"]["charge_continuous"])
T_CELL_MAX_CONT_C = float(WS3["params_ws3"]["thermal"]["t_cell_max_cont_C"])
T_CELL_CUTOFF_C = float(WS3["params_ws3"]["thermal"]["t_cell_cutoff_C"])
PACK_LOOP_KW = float(WS3_IF["coolant"]["heat_rejection_cont_kW"])
PACK_FLOW_LPM = float(WS3_IF["coolant"]["flow_L_min"])
WS3_SOC15_NOTE = WS3_IF["bus_voltage_window"]["soc15_note"]

PACK = w3p.Pack("LTO-23", 288, 1)

# WS3 (T_cell, SOC_nameplate) capability maps - the substance of the
# ESC-9 "WS5 dispatch limit" clause.
_CM = WS3["capability_maps"]["V2_LTO23"]
CAP_T_C = np.asarray(_CM["T_C"], float)
CAP_SOC = np.asarray(_CM["SOC"], float)
CAP_DIS_PULSE_KW = np.asarray(_CM["dis_pulse10_kW"], float)
CAP_CHG_PULSE_KW = np.asarray(_CM["chg_pulse10_kW"], float)
CAP_CHG_CONT_KW = np.asarray(_CM["chg_cont_kW"], float)


def _bilinear(tab, t_c, soc):
    """Bilinear lookup on the WS3 (T_C x SOC_nameplate) capability grid,
    coordinates clamped to the grid."""
    t = float(np.clip(t_c, CAP_T_C[0], CAP_T_C[-1]))
    s = float(np.clip(soc, CAP_SOC[0], CAP_SOC[-1]))
    i = int(np.clip(np.searchsorted(CAP_T_C, t) - 1, 0, CAP_T_C.size - 2))
    j = int(np.clip(np.searchsorted(CAP_SOC, s) - 1, 0, CAP_SOC.size - 2))
    ft = (t - CAP_T_C[i]) / (CAP_T_C[i + 1] - CAP_T_C[i])
    fs = (s - CAP_SOC[j]) / (CAP_SOC[j + 1] - CAP_SOC[j])
    return float(tab[i, j] * (1 - ft) * (1 - fs) + tab[i + 1, j] * ft * (1 - fs)
                 + tab[i, j + 1] * (1 - ft) * fs
                 + tab[i + 1, j + 1] * ft * fs)


def soc_usable_to_nameplate(soc_usable):
    """WS3's end-stop convention: usable 0..1 spans nameplate
    end_stop_lo .. (1 - end_stop_hi)."""
    lo = SOC_END_STOPS[0] / 100.0
    hi = SOC_END_STOPS[1] / 100.0
    return lo + float(soc_usable) * (1.0 - lo - hi)


def pack_dis_cap_kw(t_cell_c, soc_usable):
    """WS5 dispatch limit, discharge [kW bus-side]: the tighter of R8's
    restated 125 kW envelope and WS3's own (T, SOC) pulse capability map.
    This is the clause WS3 aimed at WS5 (interface_WS3.bus_voltage_window
    .soc15_note) made operational."""
    return min(R8_DIS_BUS_KW,
               _bilinear(CAP_DIS_PULSE_KW, t_cell_c,
                         soc_usable_to_nameplate(soc_usable)))


def pack_chg_cap_kw(t_cell_c, soc_usable):
    """WS5 dispatch limit, charge [kW bus-side]: R8's restated 110 kW
    envelope against WS3's (T, SOC) pulse map."""
    return min(R8_CHG_BUS_KW,
               _bilinear(CAP_CHG_PULSE_KW, t_cell_c,
                         soc_usable_to_nameplate(soc_usable)))


# R16 charge-acceptance curve (interface of record)
def load_r16_curve(col="V2pack_chg_cont_kW_bus"):
    path = os.path.join(WS3_DIR, "regen_acceptance.csv")
    hdr, T, P = None, [], []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            row = line.strip().split(",")
            if hdr is None:
                hdr = row
                continue
            T.append(float(row[0]))
            P.append(float(row[hdr.index(col)]))
    return np.array(T), np.array(P)


R16_T, R16_P = load_r16_curve()
R16_T_V1, R16_P_V1 = load_r16_curve("V1light_chg_cont_kW_bus")
R16_BAND_C = (-15.0, 10.0)          # R16 published-derate dispatch band
R16_PRECONDITION_BELOW_C = -15.0    # R16 preconditioning threshold (cell)


def r16_accept_kw(t_cell_c):
    return float(np.interp(float(t_cell_c), R16_T, R16_P))


# ------------------------------------------------------------ WS4 exports
with open(os.path.join(WS4_DIR, "results_ws4.json")) as _f:
    WS4 = json.load(_f)
WS4_IF = WS4["interface_ws4"]
SERIES_DUTY_V2 = WS4_IF["series_duty_v2"]
R22D_NOTE = WS4_IF["spin_drag_operational_note_r22d"]
V1_START_STOP_WS4 = WS4_IF["v1_start_stop"]

# R22d coast-policy figures (named interface member)
COAST_DRAG_SHAFT_W_85 = float(R22D_NOTE["ws2_point_drag_85kmh_W_shaft"])
COAST_DRAG_BUS_W_85 = float(R22D_NOTE["ws2_point_draw_85kmh_W_bus"])

ENG_V2 = w4m.ENG_V2
ENG_V1 = w4m.ENG_V1
GEN_V2 = w4m.GEN_V2
GEN_V1 = w4m.GEN_V1
LHV_KJ_PER_G = w4m.LHV_KJ_PER_G
DENSITY_G_PER_L = 832.0
derate_factor = w4m.derate_factor

# R12 traction chain (WS2 measured maps x 0.97 reduction; no scalar PE)
WS2X = w4c.load_ws2_exports(WS2_DIR)
CHAIN = w4c.WS2TractionChain(WS2X["map_path"], WS2X["ratio"], VEH.r_dyn)

REG_SEEDS = [23, 3, 4, 5, 6, 7, 8, 9]      # WS1 VOLT-REG ensemble (R9)
SUB_SEEDS = [11, 3, 4, 5, 6, 7, 8, 9]      # WS1 VOLT-SUB ensemble (R9)


def vintage_record():
    """The vintage WS5 ran against, stated so a corrected upstream round
    can be swapped in and diffed."""
    return {
        "_seam": ("all upstream consumption is through ws5_inputs.py; "
                  "re-running run_ws5.py against a corrected upstream "
                  "vintage requires no WS5 code change and flips the pins "
                  "below"),
        "WS2": {
            "rework_round": WS2X["ws2_rework_round"],
            "results_date": WS2X["ws2_results_date"],
            "traction_map_file": WS2X["map_file_rel"],
            "traction_map_voltage_V": WS2X["map_voltage_V"],
            "bus_nominal_V": WS2X["ws2_bus_nominal_V"],
            "status": "CLOSED-RATIFIED (BASELINE_v3; r4 clean)",
        },
        "WS3": {
            "results_date": WS3.get("_meta", {}).get("date"),
            "pack": PACK_V2["config"],
            "status": "CLOSED-RATIFIED (BASELINE_v2)",
        },
        "WS4": {
            "results_date": WS4.get("_meta", {}).get("date"),
            "rework": WS4.get("_meta", {}).get("rework"),
            "series_duty_v2_status": SERIES_DUTY_V2["_status"],
            "series_duty_v2_input_sha256": SERIES_DUTY_V2["input_sha256"],
            "series_duty_v2_seeds": SERIES_DUTY_V2["_inputs"]["seeds"],
            "series_duty_v2_cases": sorted(SERIES_DUTY_V2["cases"].keys()),
            "gate_g1_status": WS4_IF["gate_g1"]["status"],
            "gate_g1_consumption": ("NONE. Archived record block; no field "
                                    "consumed as a live requirement "
                                    "(BASELINE_v3 executed the kill)."),
            "kx_round": ("KX round 3. WS4's results_ws4.json moved twice "
                         "during this WS5 session; this artifact pins the "
                         "KX r3 vintage, and its concordance assertion is "
                         "exact against it. KX r3 changed exactly one value "
                         "WS5 reads live - the R22d unbooked-pp member - "
                         "and changed nothing inside series_duty_v2 -> "
                         "cases, so no WS5 dispatch, blending, traction, "
                         "thermal or fault number moved with it."),
            "adjudication_state_at_WS5_run": (
                "KX round gated (mechanical gate passed, byte-stable, "
                "verify exit 0) but NOT yet adjudicated. WS5 consumes "
                "series_duty_v2 across a single explicit seam "
                "(ws5_inputs.SERIES_DUTY_V2) so a corrected vintage swaps "
                "in without re-architecting."),
        },
        "input_sha256": input_pins(),
    }
