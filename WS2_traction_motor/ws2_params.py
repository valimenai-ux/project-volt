"""WS2 parameters — every knob in one place.

Conventions
-----------
* SI units unless suffixed. Torques/speeds at the MOTOR SHAFT unless noted.
* dq machine model is AMPLITUDE-INVARIANT: currents are phase-current
  amplitudes (A_pk), Irms = I/sqrt(2); copper loss = 1.5*R*I^2.
* Sign: motoring torque > 0, generating < 0.
* No stochastic inputs are introduced in WS2 (R9: seeds fixed trivially);
  every extremum consumed from WS1 is the published 8-seed ensemble
  envelope, taken from WS1 results.json `requirements_summary`.
"""

import os

SEED = 42  # R9 hygiene; no RNG is actually drawn anywhere in WS2.

HERE = os.path.dirname(os.path.abspath(__file__))
WS1_DIR = os.path.join(os.path.dirname(HERE), "WS1_loads_duty_cycles")
WS1_RESULTS = os.path.join(WS1_DIR, "results.json")
WS1_TRACE_SUB = os.path.join(WS1_DIR, "data", "trace_VOLT-SUB_V1_10Hz.csv")
WS1_TRACE_REG = os.path.join(WS1_DIR, "data", "trace_VOLT-REG_V2_10Hz.csv")
DATA_DIR = os.path.join(HERE, "data")

# ----------------------------------------------------------------- vehicle
# Inherited from BASELINE v1 / WS1 results.json params (not relitigated).
VEH = dict(
    m_gvw=6600.0,           # kg
    m_curb=3700.0,          # kg (operating curb, WS1)
    r_dyn=0.37,             # m
    CdA=4.2,                # m^2 (provisional per baseline)
    CdA_hi=5.4,             # m^2 (E13 case carried by sizing)
    Crr=0.009,
    rho_air=1.20,           # kg/m^3
    g=9.81,
    wheelbase=4.2,          # m
    h_cg_loaded=1.2,        # m
    h_cg_empty=1.0,         # m
    rear_share_gvw=0.65,
    rear_share_curb=0.48,
    F_trac_max=13500.0,     # N, baseline launch spec
    eta_red=0.97,           # motor path reduction efficiency (baseline)
    fd_ratio=2.8,           # engine direct path (shared final drive)
    v_lockup_kmh=65.0,      # lockup speed (WS1 control params: 18.06 m/s)
)

# Ratios evaluated (task 1); RATIO_NOM is the provisional baseline value.
RATIO_SWEEP = [8.0, 9.0, 10.0, 11.0, 12.0]
RATIO_NOM = 10.0

# ---------------------------------------------------- duty triple (R3/R4)
REQ = dict(
    S1_kW=45.0, S1_Nm=180.0,
    S1_gen_kW=50.0,                    # generating continuous (R2 descents)
    S2_10min_kW=95.0, S2_10min_Nm=200.0,
    peak_kW=120.0, peak_target_kW=150.0,
    peak_Nm=515.0, peak_Nm_below_kmh=20.0,
    rpm_max=7200.0,
    gen_env_kW=73.0, gen_env_Nm=370.0,
    hold_6pct_Nm=148.0,                # standstill hold, WS1 handoff (E16)
    crawl_Nm=510.0,                    # 20% grade crawl (E9, WS1 settle cases)
    crawl_v_kmh=(10.6, 23.6),          # V1, V2 settle speeds on 20%
    # R13: the crawl is a CONTINUOUS duty requirement — 515 Nm sustained,
    # no time box, anywhere in the 10-25 km/h band. The band TOP at the
    # window FLOOR is the winding/rating corner (it needs the most volts
    # and the most amps of any continuous case).
    crawl_cont_Nm=515.0,
    crawl_band_kmh=(10.0, 25.0),
)

# --------------------------------------------------------- DC bus (R10, ruled)
# BASELINE v2 R10: pack-native 650 V-class window, 288s LTO string.
# 288 x 1.5 / 2.3 / 2.6 / 2.7 V = 432.0 / 662.4 / 748.8 / 777.6 V.
# This is no longer a WS2 proposal — it is the ruled interface; WS2 r4
# re-spins the spine to it (R4_DIRECTIVE.md).
BUS = dict(
    v_nom=662.4,            # V, pack-native nominal (288s x 2.3 V LTO)
    v_min=432.0,            # V, operating floor (288s x 1.5 V under load)
    v_max=748.8,            # V, operating ceiling (288s x 2.6 V)
    v_transient=777.6,      # V, 10-s charge transients (288s x 2.7 V)
    v_dev_class=1200.0,     # V, semiconductor class (R10)
    v_granularity=27.6,     # V, string granularity: 12 cells x 2.3 V (R10)
    v_margin_ctrl=0.95,     # modulation headroom kept by the controller
)

# ------------------------------------------- machine (IPM, "VM250-HV", R10)
# ROUND 4: the r1-r3 machine ("VM250-OS") is REWOUND for the R10 window.
# A rewind by turns factor REWIND leaves the machine per-unit invariant:
# psi_m ~ k, Ld/Lq/Rs ~ k^2, currents ~ 1/k at the same torque; copper
# and iron losses, torque capability, thermal behaviour and mass are all
# UNCHANGED at matched per-unit points (same slot fill, finer wire).
# The factor is bound by R13's continuous-crawl corner: 515 Nm must be
# deliverable at 25 km/h (1,792 rpm) at the 432.0 V window floor.
# k = 1.47 puts that corner voltage-exact (v_req = the controller limit;
# run_ws2.py verifies), and — checked, not assumed — keeps the machine
# at >=120 kW 1-min peak everywhere in the 432.0-748.8 V window.
# The nominal-to-nominal factor 662.4/370 = 1.79 that R10's "~x0.56"
# current expectation implies FAILS this corner (crawl infeasible at the
# floor above ~21 km/h); the deviation is documented in REPORT_WS2.md.
REWIND = 1.47
MACH = dict(
    name="VM250-HV (VM250-OS rewound x1.47 for the R10 window; "
         "specified, not vendor-selected)",
    p=4,                    # pole pairs (8 poles)
    psi_m=0.078 * REWIND,           # Wb (PM flux linkage)
    Ld=0.175e-3 * REWIND ** 2,      # H
    Lq=0.400e-3 * REWIND ** 2,      # H
    Rs_20C=6.8e-3 * REWIND ** 2,    # ohm/phase at 20 C
    alpha_cu=3.93e-3,       # /K copper
    T_wind_ref=120.0,       # C — maps are published at this winding temp
    k_ac=0.5,               # Rac/Rdc = 1 + k_ac*(f_e/f_ac_ref)^2 (hairpin;
                            # strand cross-section repartitioned with the
                            # rewind, transposition assumed to hold the
                            # 480 Hz reference — declared, see report s.1)
    f_ac_ref=480.0,         # Hz (electrical frequency at 7,200 rpm)
    k_h=2.3,                # W/Hz   iron loss (hysteresis) at psi_ref
    k_e=0.0036,             # W/Hz^2 iron loss (eddy+excess+magnet) at psi_ref
    psi_ref=0.078 * REWIND, # Wb reference stator flux for iron-loss scaling
    fw_a=0.35,              # W/(rad/s)  bearing/seal drag
    fw_b=4.0e-7,            # W/(rad/s)^3 windage
    I_peak=660.0 / REWIND,  # A_pk, 60 s (inverter+machine peak current)
    rpm_max=7400.0,         # mechanical design speed (spec 7,200 + margin)
    rotor_D=0.180, rotor_L=0.165,   # m (sanity checks only; rotor unchanged)
    stator_OD=0.280, stack_L=0.170, # m
    mass_kg=96.0,           # complete machine incl oil loop internals
    mass_end_kg=18.0,       # non-stack mass (ends, shaft, bearings) for scaling
)
# NOTE: the r1-r3 "I_S2 = 500 A_pk 10-min electrical" tier is retired.
# R13 makes the crawl phase current the CONTINUOUS rating basis, and it
# exceeds every 10-min case — run_ws2.py computes the rating set as an
# explicit max over the enumerated duty cases (R14) instead of a knob.

# -------------------------------------------------------------- inverter
INV = dict(
    name="1200 V SiC MOSFET six-pack, paralleled dies (spec, R10)",
    Rds_on=1.8e-3,          # ohm effective per switch position at Tj=125C
    E_sw_ref=20.0e-3,       # J per leg (Eon+Eoff+Err) at V_ref, I_ref
    V_ref=800.0, I_ref=300.0,
    f_sw=10e3,              # Hz
    P_standby=60.0,         # W control/gate/sensors when enabled
    R_bus=0.2e-3,           # ohm busbar+cap ESR lumped (800 V-class caps)
    mass_kg=16.0,           # 1200 V module + 800 V-class DC-link caps
    Rth_jc_module=0.35,     # K/W per switch position (module to coolant)
)

# --------------------------------------------------------------- thermal
# 3-node lumped model: winding (w), stator+housing (s), rotor (r); coolant
# is a boundary temperature. Two cooling builds are evaluated:
#   'jacket'  — WEG jacket only
#   'oilspray'— WEG jacket + internal oil spray on end windings (RECOMMENDED)
THERM = dict(
    C_w=3800.0,             # J/K winding copper + slot content
    C_s=30000.0,            # J/K stator iron + housing
    C_r=8000.0,             # J/K rotor + magnets + shaft
    G_ws=dict(jacket=45.0, oilspray=90.0),   # W/K winding->stator(+oil)
    G_sc=700.0,             # W/K stator->coolant at 12 L/min WEG50
    G_rs=20.0,              # W/K rotor->stator (airgap+shaft)
    rotor_fe_frac=0.18,     # share of iron loss deposited in rotor
    rotor_fw_frac=0.30,     # share of friction/windage heating rotor
    T_cool_in=65.0,         # C coolant inlet at +45 C ambient (LT loop)
    T_amb_hot=45.0,
    T_wind_max=180.0,       # C class-H hard limit
    T_wind_cont=165.0,      # C continuous design limit (life margin)
    T_mag_max=150.0,        # C magnet limit
    standstill_hotspot=1.6, # multiplier on winding DT at standstill (dc phase)
    coolant_flow_lpm=12.0,  # series: inverter -> motor
)

# --------------------------------------------------------------- resistor
# R4/R15: re-ohmed to the R10 window. R = v_min^2 / 50 kW by construction
# (same rule as r1-r3: full chopper duty at the window FLOOR delivers
# exactly the R2 requirement). Stays FORCED-AIR per R15. Ribbon section
# thinned (0.5 -> 0.4 mm) so the higher resistance does not double the
# element mass; the surface area GROWS, and the design point is the full
# ceiling power (v_max^2/R), computed in ws2_resistor.py.
RES = dict(
    R_ohm=432.0 ** 2 / 50e3,    # ohm = 3.73248 (50 kW at full duty at 432 V)
    P_cont_req=50e3,        # W  R2 requirement at the bus (R17: capability)
    ribbon_thk=0.4e-3,      # m stainless ribbon
    ribbon_w=0.050,         # m ribbon width
    ribbon_resistivity=7.2e-7,  # ohm-m, 304 SS at operating temp
    ribbon_rho=7900.0,      # kg/m^3
    ribbon_cp=500.0,        # J/kgK
    ribbon_T_max=650.0,     # C
    h_forced=60.0,          # W/m^2K forced convection on ribbon
    air_dT=150.0,           # K blower air temperature rise at design point
    blower_dp=800.0,        # Pa
    blower_eta=0.5,
    mass_frame_factor=2.8,  # total/active-ribbon mass (frame, mica, duct, blower)
    chopper_f=2e3,          # Hz
    chopper_Rds=2.5e-3,     # ohm (single 1200 V SiC position, paralleled dies)
    chopper_E_sw=12.0e-3,   # J at chopper_V_ref / chopper_I_ref
    chopper_V_ref=800.0, chopper_I_ref=150.0,
    v_on_default=745.0,     # V droop activation (WS5-configurable 700-760)
    v_hw_backstop=800.0,    # V hardwired analogue overvoltage backstop
                            # (above the 777.6 V R10 charge transient,
                            #  67% of the 1200 V device class)
)

# --------------------------------------------------------- traction control
TRACTION = dict(
    mu_cases=[0.8, 0.5, 0.3],   # dry / wet / low-mu
    v_grid_kmh=[5, 10, 20, 30, 40, 50, 60, 70, 80],
)

# --------------------------------------------------------------- cables
CABLE = dict(
    # continuous ampacity (A) for automotive 105C-rated HV cable, bundled,
    # 85C ambient engine-bay derate  — conservative catalogue values.
    # 185/240 mm2 added in round 3 (F10): floor-voltage sizing of the
    # genset feed needs sizes above 150 mm2.
    ampacity={25: 110, 35: 140, 50: 180, 70: 225, 95: 275, 120: 320,
              150: 370, 185: 430, 240: 505},
    cu_density=8960.0,      # kg/m^3
    build_factor=1.35,      # insulation+shield mass factor over copper
    # short-time transient treatment (round 4): a listed transient is
    # checked by EXCESS-POWER ADIABATIC RISE on the copper thermal mass
    # (insulation mass ignored — conservative) from the steady state at
    # the continuous sizing current, against the insulation's
    # short-term overload class (ISO 19642-type: 105 C continuous /
    # 130 C short-term).
    cu_resistivity_hot=2.19e-8,  # ohm-m at ~90 C conductor
    cu_cp=385.0,            # J/kgK
    T_ambient_derate=85.0,  # C, engine-bay ambient basis of the table
    T_rating_cont=105.0,    # C, insulation continuous rating
    T_shortterm=130.0,      # C, insulation short-term overload class
    runs=dict(              # (length_m, n_conductors)
        genset_to_bus=(2.5, 2),
        pack_to_bus=(2.0, 2),
        inverter_to_motor=(1.5, 3),
        chopper_to_resistor=(1.0, 2),
    ),
)

# ------------------------------------------------------ efficiency map grid
MAP = dict(
    rpm_step=100.0,          # 0..7400
    T_step=15.0,             # -540..540 Nm
    # R10/R4: maps re-derived at the ruled window points 432 / 662 / 749 V
    # (floor / nominal / ceiling); G1-R and WS5 consume these files.
    voltages=[432.0, 662.4, 748.8],
)
