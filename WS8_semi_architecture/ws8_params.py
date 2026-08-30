"""
Project Volt - WS8 (Vehicle One, semi-scale architecture trial)
Vehicle, mass-ledger, environment and scaling-law parameters.

CONVENTIONS INHERITED FROM VEHICLE ZERO (binding, CLAUDE.md):
  * SI units throughout; kW/kWh at the DC BUS unless a name says
    otherwise (rule 6).
  * Part-load models everywhere; no peak-point scalars (rule 5).
  * Stochastic extrema are 8-seed ensemble envelopes (rule 4).
  * Every machine-readable worst-case field is an explicit max/min over
    an enumerated case set with the governing case labelled (R14).

PROVENANCE TAGS, used on every number below:
  [ASSIGNMENT]   given verbatim in WS8_semi_architecture/ASSIGNMENT.md
  [WS8-PROV]     WS8-declared, provisional per the E13 precedent named in
                 the assignment ("refine with stated or cited values,
                 flagged per E13 precedent as provisional")
  [WS2-r4]/[WS3]/[WS4]  read read-only from Vehicle Zero exports (rule 10)

NOTHING here is ratified. The lead ratifies in a separate chat (rule 11).
"""
from dataclasses import dataclass, asdict

G = 9.81  # m/s^2

# --------------------------------------------------------------- fuel basis
# Carried unchanged from WS4 so that WS8 fuel arithmetic is chain-comparable
# with Vehicle Zero's. [WS4] ws4_models.py LHV_KJ_PER_G.
LHV_KJ_PER_G = 42.8                     # diesel lower heating value
DIESEL_DENSITY_KG_PER_L = 0.832         # [WS8-PROV] EN590 class, 15 C
BSFC_FROM_ETA = 3600.0 / LHV_KJ_PER_G   # 84.112 / eta_b -> g/kWh


@dataclass(frozen=True)
class Vehicle:
    """Class 8 6x4 tractor + 53 ft van trailer at FIXED gross combination
    weight. GCW is held at 36,300 kg for every candidate (assignment,
    Task 3) - powertrain mass is therefore paid for in PAYLOAD, which is
    why payload tonne-km is the metric of record."""

    # ---- given by the assignment ----
    m_gcw: float = 36300.0        # kg  [ASSIGNMENT] fixed for all candidates
    CdA: float = 5.5              # m^2 [ASSIGNMENT] "~5.5"
    Crr: float = 0.0055           # -   [ASSIGNMENT] "~0.0055"
    r_dyn: float = 0.50           # m   [ASSIGNMENT] "~0.50"

    # ---- environment ----
    rho_air: float = 1.196        # kg/m^3 [WS8-PROV] 20 C, 101.325 kPa dry
    rho_air_cold: float = 1.341   # kg/m^3 [WS8-PROV] -10 C, same pressure

    # ---- rotating inertia referred to the road ------------------------
    # A geared truck in a low gear carries a large engine-side term; at
    # cruise in direct drive it is modest. WS1 argued this member
    # explicitly (volt_params.py Vehicle.lam_rot) and WS8 does the same at
    # semi scale:
    #   10 tyres+hubs+drums, I ~ 155 kg.m^2 -> 155/0.50^2  =  620 kg
    #   driveline/shafts                                   ~   60 kg
    #   engine+flywheel 3.2 kg.m^2 at 3.36:1 direct top    ->  145 kg
    # on 36,300 kg -> 1.023 direct-drive; the e-drive rotor at a ~12:1
    # reduction adds 0.35 kg.m^2 * 12^2 / 0.50^2 = 202 kg -> +0.006.
    lam_rot_direct: float = 1.023      # [WS8-PROV] ICE in direct top
    lam_rot_edrive: float = 1.029      # [WS8-PROV] geared traction machine
    lam_rot_launch: float = 1.10       # [WS8-PROV] deep-reduction launch,
                                       # AMT low gears (engine referred at
                                       # ~15:1 x 3.36:1)

    # ---- chassis geometry, for the adhesion checks (Task 5) ----------
    # 6x4 tractor + tandem-axle van trailer, US legal load split at
    # 36,300 kg GCW (12,000 lb steer / 34,000 lb drive / 34,000 lb
    # trailer = 5,443 / 15,422 / 15,422 kg). This split is what makes the
    # drive-axle adhesion question answerable at all.
    m_axle_steer_kg: float = 5443.0       # [WS8-PROV] US bridge-formula legal
    m_axle_drive_tandem_kg: float = 15422.0
    m_axle_trailer_tandem_kg: float = 15435.0   # balance to GCW
    h_cg_loaded: float = 1.85             # m [WS8-PROV] loaded combination
    wheelbase_tractor: float = 6.10       # m [WS8-PROV] 240 in

    @property
    def drive_axle_load_fraction(self) -> float:
        return self.m_axle_drive_tandem_kg / self.m_gcw


@dataclass(frozen=True)
class Adhesion:
    """Tyre-road friction cases for the drive-axle checks. Enumerated as a
    CASE SET so the worst case can be exported per R14 rather than
    asserted."""
    mu_dry: float = 0.70          # [WS8-PROV] dry asphalt, HD radial drive
    mu_wet: float = 0.45          # [WS8-PROV] wet asphalt
    mu_snow: float = 0.20         # [WS8-PROV] packed snow / hard-packed
    mu_ice: float = 0.10          # [WS8-PROV] ice


@dataclass(frozen=True)
class Aux:
    """Accessory load. On a Class 8 the air compressor, fan, power
    steering and HVAC are real and large; on a conventional truck they are
    parasitic on the crankshaft, on an electrified one they move to the
    bus. Both are charged - the SAME total accessory duty is applied to
    every candidate so the comparison is not decided by bookkeeping.
    [WS8-PROV] class-typical line-haul averages."""
    p_aux_mech_avg_kW: float = 4.0     # crank-driven: fan duty-cycled, air
                                       # compressor, PS pump, alternator base
    p_aux_bus_avg_kW: float = 3.4      # same duty on an electrified truck,
                                       # net of the belt/pump losses deleted
    p_aux_bus_cold_kW: float = 6.6     # -10 C: cab heat + battery thermal
    p_hotel_idle_kW: float = 2.2       # stationary hotel load


@dataclass(frozen=True)
class Driveline:
    """Mechanical driveline efficiencies, stated (assignment Task 2:
    'transmission and axle efficiencies stated').

    An AMT in DIRECT top gear has no countershaft power path, so it is
    ~2 points better than an indirect gear. That is exactly why line-haul
    trucks are specified with a direct-drive top gear, and it is the
    number S0 gets to keep. Candidates that delete the gearbox are
    credited only the difference between this and a single fixed
    reduction - which is small, and is the honest reason the gearbox is
    not where the win is."""
    eta_amt_direct: float = 0.985      # [WS8-PROV] direct top, no countershaft
    eta_amt_indirect: float = 0.965    # [WS8-PROV] geared ratios
    eta_axle_tandem: float = 0.955     # [WS8-PROV] 6x4 hypoid tandem w/
                                       # interaxle diff, at cruise torque
    eta_axle_single_reduction: float = 0.970   # [WS8-PROV] single hypoid,
                                       # no interaxle diff (S3 axle A)
    eta_fixed_ratio_box: float = 0.985 # [WS8-PROV] one constant-mesh
                                       # helical stage, no shifting elements
    eta_edrive_reduction: float = 0.970  # [WS2-r4] carried unchanged: WS2's
                                       # ruled 0.97 reduction member
    eta_driveshaft: float = 0.995      # [WS8-PROV] u-joints, per shaft run


@dataclass(frozen=True)
class MassLedger:
    """Component mass ledger, in kg. Every candidate's payload is
    GCW - (tare + its own powertrain ledger), so this table IS the metric
    of record's denominator. [WS8-PROV] throughout; class-typical
    published figures, to be confirmed at procurement.

    The reference tare below EXCLUDES the powertrain items listed
    separately, so no item is counted twice: the S0 ledger rebuilds a
    complete conventional tractor from `m_glider_tractor` plus its
    powertrain rows, and the total is checked against a published
    conventional curb mass in run_ws8.py's sanity block."""

    # --- structure that every candidate carries unchanged -------------
    m_glider_tractor: float = 5150.0   # 6x4 sleeper tractor less engine,
                                       # gearbox, driveshafts, drive-axle
                                       # carriers, fuel and aftertreatment
    m_trailer_tare: float = 6800.0     # 53 ft dry van, tandem axle
    m_driver_and_effects: float = 100.0
    m_drive_axle_housings: float = 620.0   # tandem housings, wheel ends,
                                       # brakes, suspension - carried by
                                       # every candidate (they all drive
                                       # through axles)

    # --- S0 conventional powertrain -----------------------------------
    m_engine_13L_wet: float = 1215.0   # 12.7-13 L, wet, with flywheel/
                                       # clutch housing and cooling package
    m_aftertreatment: float = 155.0    # DPF/SCR box, DEF tank, piping
    m_amt_12sp: float = 325.0          # 12-speed AMT, direct top
    m_driveshafts: float = 65.0
    m_drive_axle_gearsets_tandem: float = 530.0   # both carriers, interaxle
    m_fuel_full: float = 555.0         # 2 x 400 L usable diesel fill
    m_fuel_small: float = 210.0        # reduced tank where the candidate
                                       # burns much less (S4 sustainer)

    # --- electric path, WS2/WS3 derived (see ws8_electric.py) ---------
    m_hv_cabling: float = 55.0         # [WS2-r4 x scale] 17.9 kg on Vehicle
                                       # Zero, tractor+trailer runs and
                                       # semi-scale current
    m_contactors_precharge: float = 18.0
    m_hv_misc_bms_thermal: float = 95.0   # HV distribution box, pack coolant
                                       # loop, chillers, harness support

    # --- S3-specific -------------------------------------------------
    m_fixed_ratio_box: float = 145.0   # one constant-mesh helical stage in
                                       # a housing, no shift mechanism,
                                       # no synchronisers, no shift air
    m_revmatch_clutch: float = 105.0   # dry single-plate + actuator +
                                       # control, sized to SYNC only (no
                                       # launch slip duty - see ws8_cands)


@dataclass(frozen=True)
class Scaling:
    """Stated scaling laws for the electric components (assignment Task 3:
    'Electric components scale from WS2 r4 measured maps with stated
    scaling laws').

    THE LAW, stated once and applied everywhere:

      Axial stretch by factor k of the WS2 r4 VM250-HV electromagnetic
      design, at unchanged pole count, unchanged electric loading, and
      unchanged per-unit winding design (the x1.47 rewind that WS2 ruled
      per-unit invariant fixes the voltage; the stretch fixes the
      torque):

        torque    T(k)      = k * T_ws2
        power     P(k, n)   = k * P_ws2(n)          (same speed axis)
        LOSS      L(k;n,T)  = k * L_ws2(n, T/k)     <- per-unit invariant
        mass      m(k)      = k * m_active + m_fixed

      The loss law is the whole point: it says a machine twice as long
      has twice the loss AT TWICE THE TORQUE, i.e. the same per-unit
      efficiency map. That holds to first order because copper and iron
      loss both scale with active volume, while the map's speed axis -
      which sets iron loss per unit volume and the field-weakening
      boundary - is untouched by an axial stretch.

      WHERE IT IS OPTIMISTIC, stated so the adjudicator does not have to
      find it: end-winding copper scales sub-linearly (favours the big
      machine, so the law is CONSERVATIVE there), bearing and windage
      losses scale roughly linearly (neutral), and the thermal path
      scales with jacket area ~ linearly in k for a stretch at constant
      diameter (neutral). The genuinely optimistic member is that a
      2-3x stretch of a 96 kg machine is treated as buildable without a
      rotor dynamics or shaft-stiffness penalty; WS8 charges no such
      penalty and FLAGS it (ESC-WS8-2).

      m_active/m_fixed split: WS2's 96 kg motor is taken as 80% active
      (stack, copper, magnets, shaft) and 20% structure (end bells,
      jacket, terminal box) that does not stretch."""
    motor_active_fraction: float = 0.80     # [WS8-PROV] of WS2's 96 kg
    inverter_active_fraction: float = 0.80  # [WS8-PROV] of WS2's 16 kg
    # An axial stretch cannot raise the map's speed axis; rpm_max is a
    # rotor-mechanical limit and is carried unchanged from WS2 r4.
    rpm_max_carried_from_ws2: float = 7200.0


@dataclass(frozen=True)
class Cycle:
    """Duty-cycle construction constants (assignment Task 1)."""
    dt: float = 0.1                    # s  [ASSIGNMENT] 10 Hz
    n_seeds: int = 8                   # [CLAUDE.md rule 4]
    seed0: int = 8101                  # fixed base seed; seeds are
                                       # seed0 + 0..7 (deterministic)
    linehaul_km: float = 520.0         # [ASSIGNMENT] "500+ km"
    linehaul_v_lo_kmh: float = 85.0    # [ASSIGNMENT] 85-105 km/h band
    linehaul_v_hi_kmh: float = 105.0
    mountain_grade: float = 0.06       # [ASSIGNMENT] "one 6% mountain
                                       # segment with full descent"
    sustained_grade_lo: float = 0.02   # [ASSIGNMENT] "sustained 2-3%"
    sustained_grade_hi: float = 0.03
    regional_km: float = 165.0         # [WS8-PROV] mixed urban/rural/hwy


VEH = Vehicle()
ADH = Adhesion()
AUX = Aux()
DL = Driveline()
ML = MassLedger()
SC = Scaling()
CY = Cycle()


def params_dump():
    return {
        "vehicle": asdict(VEH),
        "vehicle_derived": {
            "drive_axle_load_fraction": VEH.drive_axle_load_fraction,
            "axle_load_sum_kg": (VEH.m_axle_steer_kg
                                 + VEH.m_axle_drive_tandem_kg
                                 + VEH.m_axle_trailer_tandem_kg),
        },
        "adhesion": asdict(ADH),
        "aux": asdict(AUX),
        "driveline": asdict(DL),
        "mass_ledger": asdict(ML),
        "scaling": asdict(SC),
        "cycle": asdict(CY),
        "fuel": {
            "LHV_kJ_per_g": LHV_KJ_PER_G,
            "density_kg_per_L": DIESEL_DENSITY_KG_PER_L,
            "bsfc_from_eta": BSFC_FROM_ETA,
        },
    }
