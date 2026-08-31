"""
Project Volt - WS11 (Vehicle Zero ruler trial, BASELINE_v5 R32)

Declared parameters for the RULER (stock Isuzu NPR-HD) and the mass
ledgers for the ruler and the two ratified candidates.

Provenance discipline:
  [SOURCED]        - taken from a public document retrieved and stored in
                     sources/ ; the exact figure and its file are named.
  [PROGRAM]        - taken from a ratified Project Volt artefact
                     (BASELINE, WS1/WS2/WS3/WS4 results.json).
  [WS11-DECLARED]  - a WS11 modelling choice with no external source. Every
                     one of these carries a stated direction of error.

Convention on declared choices (stated once, applied everywhere): where a
declared value could be argued either way, WS11 takes the RULER-FAVOURABLE
reading, so the candidates' reported margins are LOWER bounds. The
alternatives are re-run as brackets and exported.

SI units. Masses in kg. Electrical quantities bus-side (R12).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS1_DIR = os.path.normpath(os.path.join(HERE, "..", "WS1_loads_duty_cycles"))
WS2_DIR = os.path.normpath(os.path.join(HERE, "..", "WS2_traction_motor"))
WS3_DIR = os.path.normpath(os.path.join(HERE, "..", "WS3_battery"))
WS4_DIR = os.path.normpath(os.path.join(HERE, "..", "WS4_genset"))
for _d in (WS1_DIR, WS4_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

LB_TO_KG = 0.45359237
DENSITY_G_PER_L = 832.0        # diesel EN590 at 15 C (WS4 convention)
LHV_KJ_PER_G = 42.8            # WS4 convention
G = 9.81

# ---------------------------------------------------------------------------
# 1. RULER - stock Isuzu NPR-HD, sourced specification
# ---------------------------------------------------------------------------
# sources/isuzucv_npr-hd_diesel_specs.pdf  (2023 ISUZU N-SERIES NPR-HD,
# 14,500 LBS. GVWR, CLASS 4), retrieved from
# https://www.isuzucv.com/pdfs/npr-hd_diesel_specs.pdf
RULER_SOURCED = {
    "document": "2023 ISUZU N-SERIES NPR-HD spec sheet (14,500 lbs. GVWR, "
                "Class 4)",
    "url": "https://www.isuzucv.com/pdfs/npr-hd_diesel_specs.pdf",
    "local_copy": "sources/isuzucv_npr-hd_diesel_specs.pdf",
    "gvwr_lb": 14500.0,
    "gcwr_lb": 20500.0,
    "body_payload_allowance_lb": [7545.0, 8511.0],
    "gawr_front_lb": 5360.0,
    "gawr_rear_lb": 9880.0,
    "rear_axle_ratio": 4.555,
    "transmission": "Aisin A465id 6-speed auto with double overdrive and "
                    "lock-up 2nd-6th gears",
    "engine": "Isuzu 4HK1-TC turbocharged intercooled diesel",
    "displacement_l": 5.2,
    "rated_power_hp_at_rpm": [215.0, 2500.0],
    "rated_torque_lbft_at_rpm": [452.0, 1850.0],
    "alternator_A": 140.0,
    "tires": "215/85R16E (10-pr)",
    "wheelbases_in": [109.0, 132.5, 150.0, 176.0],
    "fuel_tank_gal_standard": 30.0,
}

# Aisin A465 / AS68RC gear ratios and mass.
# sources/as68rc_transmissionrepaircostguide.md, retrieved from
# https://www.transmissionrepaircostguide.com/as68rc/
RULER_TRANS_SOURCED = {
    "document": "AS68RC Transmission: Specs & Updates "
                "(Aisin A465 family, as fitted to the Isuzu NPR)",
    "url": "https://www.transmissionrepaircostguide.com/as68rc/",
    "local_copy": "sources/as68rc_transmissionrepaircostguide.md",
    "gear_ratios": [3.74, 1.96, 1.34, 1.00, 0.77, 0.63],
    "reverse_ratio": 3.54,
    "mass_lb_incl_converter": 500.0,
    "max_input_torque_lbft": 730.0,
}

GEAR_RATIOS = tuple(RULER_TRANS_SOURCED["gear_ratios"])       # [SOURCED]
AXLE_RATIO = RULER_SOURCED["rear_axle_ratio"]                 # [SOURCED]
N_GEARS = len(GEAR_RATIOS)

# --- ruler driveline efficiencies -----------------------------------------
# [WS11-DECLARED] Planetary-AT mesh efficiency by gear. 4th is the direct
# (1:1) gear and is the most efficient; the two overdrives and the deep
# reduction gears carry an extra mesh. Direction of error: these are at the
# generous end of published MD planetary-AT figures, i.e. RULER-FAVOURABLE.
ETA_GEAR = (0.960, 0.965, 0.970, 0.985, 0.965, 0.960)
# [WS11-DECLARED] hypoid final drive x propshaft/UJs. WS1's ratified
# `eta_direct` = 0.95 covered clutch + driveshaft + 2.8:1 axle; 0.96 here is
# the axle + shaft share of that, i.e. RULER-FAVOURABLE.
ETA_FINAL = 0.96
# [WS11-DECLARED, matched to WS4] transmission pump/churning parasitic.
# WS4's ratified direct-path model charges 0.9 kW x (rpm/1800) churning to a
# clutch + 2.8:1 axle. A torque-converter automatic with a high-pressure
# pump is lossier; 1.2 kW at 1,800 rpm is the WS11 value. Direction of
# error: a real A465 pump at line pressure is 1.5-2.5 kW at 1,800 rpm, so
# this is RULER-FAVOURABLE.
PUMP_KW_AT_1800 = 1.2
# [WS11-DECLARED] lockup slip/pump-drag debit while locked (fraction of
# input power). RULER-FAVOURABLE: 0 would be unphysical, 0.5% is at the
# optimistic end.
LOCKUP_SLIP_LOSS = 0.005

# --- torque converter ------------------------------------------------------
# [WS11-DECLARED] class-typical single-stage three-element converter matched
# to a 5.2 L MD diesel. Stall speed ~2,000 rpm against the reference
# full-load curve; torque ratio 2.0 at stall, coupling near SR = 0.90.
# Direction of error: a higher stall ratio or a lower coupling point would
# make the ruler WORSE, so this set is RULER-FAVOURABLE.
TC_SR = (0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80,
         0.90, 0.95, 1.00)
TC_TR = (2.00, 1.87, 1.74, 1.61, 1.48, 1.35, 1.23, 1.12, 1.04,
         1.00, 1.00, 1.00)
TC_CAP_REL = (1.00, 1.00, 1.00, 1.00, 1.01, 1.03, 1.05, 1.03, 0.88,
              0.55, 0.30, 0.00)
# capacity constant C0 [N.m.s^2/rad^2]: T_impeller = C(SR) * omega_e^2.
# 685 Nm (reference full-load torque at 2,000 rpm) at 2,000 rpm stall.
TC_C0 = 685.0 / (2000.0 * 2 * np.pi / 60.0) ** 2

# --- shift schedule --------------------------------------------------------
# [WS11-DECLARED] fuel-optimal gear selection among feasible gears, with a
# minimum dwell and a hysteresis margin so the schedule cannot hunt. This is
# a BEST-CASE automatic-transmission shift schedule; a production schedule
# is worse. RULER-FAVOURABLE by construction.
SHIFT_MIN_DWELL_S = 1.0
SHIFT_HYSTERESIS_FRAC = 0.03      # new gear must beat current by 3% fuel
N_LUG_MIN_RPM = 1100.0            # lowest steady-drive engine speed
N_MAX_RPM = 2600.0                # highest scheduled engine speed
TORQUE_RESERVE_FRAC = 0.10        # keep 10% of full-load torque in hand
V_LOCKUP_MIN_KMH = 20.0           # lock-up available from 2nd gear upward
LOCKUP_MIN_GEAR = 2               # [SOURCED] "lock-up 2nd-6th gears"
V_STOPPED_KMH = 0.5               # below this the vehicle is "stopped"
N_DFCO_RPM = 1000.0               # deceleration fuel cut-off threshold

# --- ruler accessories -----------------------------------------------------
# WS1's ratified accessory budget is 2.0 kW at the DC bus (electro-hydraulic
# steering 0.3, brake boost 0.3, cab HVAC 1.0, 24 V loads 0.4).
# HEADLINE [WS11-DECLARED, RULER-FAVOURABLE]: the ruler is charged the same
# 2.0 kW AT THE CRANK, i.e. its belt-driven pumps and its 140 A alternator
# are credited with the same efficiency as the candidates' bus-side loads.
P_ACC_CRANK_KW = 2.0
# BRACKET: the physical belt/alternator model. Mechanical services
# (steering + brake boost + HVAC compressor = 1.6 kW) through a belt/pump
# path at 0.85, and the 0.4 kW of 24 V load through a 140 A alternator at
# 0.55 system efficiency.
P_ACC_CRANK_KW_PHYSICAL = 1.6 / 0.85 + 0.4 / 0.55

# --- ruler idle ------------------------------------------------------------
# HEADLINE [WS11-DECLARED, RULER-FAVOURABLE]: neutral idle. At a standstill
# the engine turns at its idle speed carrying accessories only; the
# converter is unloaded. BRACKET: converter stalled in Drive, which is what
# a truck without a neutral-idle function actually does.
IDLE_NEUTRAL = True

# --- ruler rotating inertia ------------------------------------------------
# [PROGRAM] WS1 uses lam_rot = 1.04 for the electric path. The ruler's
# engine + flywheel + converter, referred to the road through a low gear,
# is a much larger member (WS1's own note: "a geared truck in a low gear
# would be 1.2+"). The comparison of record follows the IDENTICAL wheel-power
# trace for every vehicle at lam_rot = 1.04 (the WS4/G1 net-energy
# convention), so this member is NOT charged in the headline. It is computed
# and exported as a ruler bracket. RULER-FAVOURABLE.
I_ENG_FLYWHEEL_CONV_KGM2 = 0.60

# ---------------------------------------------------------------------------
# 2. MASS LEDGERS
# ---------------------------------------------------------------------------
# Chassis-cab curb at the 150 in wheelbase (the wheelbase that carries a
# 16 ft body), derived from the SOURCED body/payload allowance range by
# linear interpolation in wheelbase.
_WB = RULER_SOURCED["wheelbases_in"]
_ALLOW = RULER_SOURCED["body_payload_allowance_lb"]
WB_RULER_IN = 150.0
_frac = (WB_RULER_IN - _WB[0]) / (_WB[-1] - _WB[0])
ALLOWANCE_AT_WB_LB = _ALLOW[1] - _frac * (_ALLOW[1] - _ALLOW[0])
CHASSIS_CAB_CURB_KG = (RULER_SOURCED["gvwr_lb"] - ALLOWANCE_AT_WB_LB) \
    * LB_TO_KG

# The remaining items build the WS1-ratified 3,700 kg OPERATING curb. The
# 16 ft dry-freight body is the single reconciliation item and is declared
# as such; 545 kg is inside the published range for a 16 ft aluminium
# dry-freight body with subframe and rear door.
RULER_LEDGER = [
    ("chassis-cab curb, 150 in WB", round(CHASSIS_CAB_CURB_KG),
     "[SOURCED] GVWR 14,500 lb minus body/payload allowance interpolated "
     "to the 150 in wheelbase (7,920 lb)"),
    ("16 ft dry-freight body + subframe + rear door", 545,
     "[WS11-DECLARED] reconciliation item to WS1's ratified operating curb"),
    ("driver + kit", 90, "[WS11-DECLARED]"),
    ("fuel to full (30 gal tank), increment over chassis tare", 75,
     "[WS11-DECLARED]"),
    ("DEF, tools, spare", 5, "[WS11-DECLARED]"),
]

# Stock parts DELETED by both candidates.
DELETED_COMMON = [
    ("Aisin A465id 6-speed AT + torque converter + fluid", 227,
     "[SOURCED] ~500 lb including the torque converter"),
    ("transmission oil cooler + lines", 5, "[WS11-DECLARED]"),
    ("alternator, 140 A", 10, "[WS11-DECLARED]"),
    ("starter motor + solenoid", 8,
     "[WS11-DECLARED] the generator is the starter (R19 ISG)"),
]

# Additions common to both candidates.
ADDED_COMMON = [
    ("WS2 spine rollup (motor 96, inverter 16, motor-stage reduction 32, "
     "brake resistor assembly 53.9, chopper 6, HV cables 17.9, "
     "contactors/precharge 9)", 230.8,
     "[PROGRAM] WS2 results.json interface.mass_kg.total_kg"),
    ("WS3 288s1p LTO-23 pack", 280.52,
     "[PROGRAM] WS3 results.json interface_WS3.packs.V2.mass_kg"),
    ("added cooling: LT loop radiator/pump/lines + pack loop", 35,
     "[WS11-DECLARED]"),
    ("DC-DC converter, 24 V supply (replaces the alternator)", 6,
     "[WS11-DECLARED]"),
]

V1_DELETED = [("Isuzu 4HK1-TC engine, dry", 500,
               "[PROGRAM] WS4 interface_ws4.v2_genset.mass_kg.engine_dry - "
               "the same figure is used on both sides so it cancels for V2")]
V1_ADDED = [
    ("V3307-V1C engine, dry", 305, "[PROGRAM] WS4 v1_genset.mass_kg"),
    ("GEN-V1 IPM 60 generator", 48, "[PROGRAM] WS4 v1_genset.mass_kg"),
    ("active rectifier", 8, "[PROGRAM] WS4 v1_genset.mass_kg"),
    ("mounts / adaptation", 25, "[PROGRAM] WS4 v1_genset.mass_kg"),
]
V2_DELETED = []
V2_ADDED = [
    ("GEN-V2 IPM 135 generator", 90, "[PROGRAM] WS4 v2_genset.mass_kg"),
    ("active rectifier", 12, "[PROGRAM] WS4 v2_genset.mass_kg"),
    ("mounts / adaptation", 35, "[PROGRAM] WS4 v2_genset.mass_kg"),
]
# WS4 exports `aftertreatment_extra: 60.0` separately from the V2 genset's
# 637 kg total_dry. The 4HK1-V2C is the SAME production hardware as the
# ruler's engine, so its aftertreatment is the stock truck's aftertreatment
# and cancels. Headline excludes it; the +60 kg reading is exported as a
# bracket and escalated (ESC-3).
V2_AFTERTREATMENT_BRACKET_KG = 60

M_GVW_KG = 6600.0              # [PROGRAM] BASELINE v1


def _sum(rows):
    return float(sum(r[1] for r in rows))


def build_mass_ledgers():
    ruler_curb = round(_sum(RULER_LEDGER))
    v1_curb = round(ruler_curb - _sum(DELETED_COMMON) - _sum(V1_DELETED)
                    + _sum(ADDED_COMMON) + _sum(V1_ADDED))
    v2_curb = round(ruler_curb - _sum(DELETED_COMMON) - _sum(V2_DELETED)
                    + _sum(ADDED_COMMON) + _sum(V2_ADDED))
    v2_curb_bracket = v2_curb + V2_AFTERTREATMENT_BRACKET_KG
    return {
        "ruler": dict(curb_kg=ruler_curb,
                      payload_at_gvw_kg=round(M_GVW_KG) - ruler_curb),
        "V1": dict(curb_kg=v1_curb,
                   payload_at_gvw_kg=round(M_GVW_KG) - v1_curb),
        "V2": dict(curb_kg=v2_curb,
                   payload_at_gvw_kg=round(M_GVW_KG) - v2_curb),
        "V2_aftertreatment_bracket": dict(
            curb_kg=v2_curb_bracket,
            payload_at_gvw_kg=round(M_GVW_KG) - v2_curb_bracket),
    }


# ---------------------------------------------------------------------------
# 3. CORNER SET (assignment; R28 Vehicle-Zero analogue)
# ---------------------------------------------------------------------------
# Air density from the standard atmosphere at the corner's altitude and
# temperature (the same construction WS4 used: 1.1097 at 45 C sea level,
# 0.8706 at 2,000 m / 45 C).
def rho_air(alt_m, t_c):
    p = 101325.0 * (1.0 - 2.25577e-5 * alt_m) ** 5.2559
    return p / (287.0 * (t_c + 273.15))


PAYLOAD_CORNER_FRACS = (1.20, 0.80)     # of the RULER's payload
CORNER_COLD_C = -10.0
CORNER_ALT_M = 2000.0
CORNER_HOT_C = 45.0
CLIMB_KM = 10.0                          # WS1 section 4.4
CLIMB_GRADE = 0.06

# [WS11-DECLARED] cab-heat asymmetry bracket at -10 C (the R30 member, which
# BASELINE_v5 imposes on Vehicle One and which the assignment does not order
# for Vehicle Zero). Thermal demand at the cab; the ruler takes it free from
# engine coolant, the candidate takes it free from genset coolant WHILE THE
# GENSET RUNS and electrically otherwise.
CAB_HEAT_KW_AT_MINUS10 = 3.0


# ---------------------------------------------------------------------------
# 4. THE SOURCED RULER ANCHOR (mandatory per the assignment)
# ---------------------------------------------------------------------------
# Public, model-specific, in-use fuel-economy reference for the Isuzu NPR-HD.
# Retrieved 2026-08-31; the retrieved page text is stored verbatim in
# sources/fuelly_npr_hd_all.txt and pinned by SHA-256 in results_ws11.json.
# Page header, verbatim: "21 Isuzu NPR-HDs have provided 180 thousand miles
# of real world fuel economy & MPG data."
# Model years with zero fuel-ups are listed on the page with 0.0 Avg MPG and
# are excluded here (they carry no data).
RULER_FUEL_ANCHOR = {
    "name": "Fuelly - Isuzu NPR-HD, all model years (owner fuel logs)",
    "url": "https://www.fuelly.com/truck/isuzu/npr-hd/all",
    "local_copy": "sources/fuelly_npr_hd_all.txt",
    "retrieved": "2026-08-31",
    "page_statement": "21 Isuzu NPR-HDs have provided 180 thousand miles of "
                      "real world fuel economy & MPG data.",
    "rows": [
        # (model year, avg mpg (US), vehicles, fuel-ups, miles tracked)
        (2016, 8.7, 4, 63, 11670),
        (2015, 7.0, 5, 401, 54646),
        (2014, 8.1, 1, 71, 9638),
        (2002, 9.4, 1, 491, 100361),
        (2000, 7.8, 2, 18, 3387),
    ],
    "excluded_rows_zero_fuelups": [2013, 2012, 2007, 2006, 2005],
    "engine_era_note": "the 4HK1-TC is the MY2008+ engine; MY2002 (56% of "
                       "the tracked miles) is the earlier 4HE1-TC truck, so "
                       "the 4HK1-era subset is reported separately",
    "fourhk1_era_years": [2016, 2015, 2014],
}
MPG_TO_L_PER_100KM = 235.2145833


def anchor_stats(rows=None):
    """Distance-weighted in-use fuel consumption from the anchor's own
    per-model-year table (miles / gallons, not a mean of means)."""
    rows = RULER_FUEL_ANCHOR["rows"] if rows is None else rows
    miles = sum(r[4] for r in rows)
    gal = sum(r[4] / r[1] for r in rows)
    mpg = miles / gal
    return dict(miles=miles, gallons=gal, mpg=mpg,
                l_per_100km=MPG_TO_L_PER_100KM / mpg,
                vehicles=sum(r[2] for r in rows),
                fuel_ups=sum(r[3] for r in rows),
                model_years=[r[0] for r in rows])
