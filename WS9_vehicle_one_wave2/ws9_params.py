"""
Project Volt - WS9 (Vehicle One, wave two: the two walls and the cold wall)
Parameters, provenance tags, and the declared factors of record.

WS9 INHERITS WS8's PIPELINE (assignment: "Inherit the WS8 pipeline
(cycles, S0, mass ledger, electric scaling, pricing of unserved energy AS
CORRECTED by r2) - do not re-derive what is ratified; extend it").
Everything WS8 ratified is IMPORTED read-only from
`../WS8_semi_architecture` (CLAUDE.md rule 10 - the same posture WS8 takes
towards WS2/WS3/WS4). This module declares only what WS9 ADDS.

VINTAGE OF THE INHERITED PIPELINE, stated because the assignment orders it
("build to hot-swap; state vintages"):
  * WS8 code and artifacts: ROUND 1 (the committed state of
    WS8_semi_architecture at the time WS9 ran; see run_ws9.py's
    `inherited_vintage` block, which SHA-pins every inherited source file).
  * WS8 round 2 (R2_DIRECTIVE.md) had NOT landed. WS9 therefore implements
    the r2 corrections itself, from R2_DIRECTIVE.md and FINDINGS_WS8_r1.md,
    inside WS9's own folder - it does not touch WS8. Every such
    implementation is tagged [R2-IMPL] below and enumerated in the report's
    r2 concordance table, so that when r2 lands the two can be compared
    field by field and WS9 re-run against r2's numbers (hot-swap).

PROVENANCE TAGS, used on every number in this file:
  [ASSIGNMENT]  given verbatim in WS9_vehicle_one_wave2/ASSIGNMENT.md
  [BASELINE-v4] fixed by a ruling R25-R33 in ../BASELINE_v4.md
  [WS9-PROV]    WS9-declared, provisional per the E13 precedent
  [WS9-CITED]   external, with the source and its EVIDENCE QUALITY stated
                in CITATIONS below; provisional per E13 precedent
  [R2-IMPL]     WS9's implementation of a WS8 round-2 erratum
  [WS8]/[WS2-r4]/[WS3]/[WS4]  read read-only from a prior workstream

NOTHING here is ratified. The lead ratifies (CLAUDE.md rule 11).
"""
import os
import sys
from dataclasses import dataclass, asdict, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8_DIR = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8_DIR not in sys.path:
    sys.path.insert(0, _WS8_DIR)

from ws8_params import (VEH, ADH, AUX, DL, ML, SC, CY, G,          # noqa: E402
                        LHV_KJ_PER_G, DIESEL_DENSITY_KG_PER_L)

WS8_DIR = os.path.abspath(_WS8_DIR)


# =====================================================================
#  0. CITATIONS - every external number WS9 relies on, with its
#     evidence quality stated (assignment: "state the BTE claim and its
#     evidence quality").
# =====================================================================
CITATIONS = {
    "ACHATES_OP": dict(
        claim="peak brake thermal efficiency 49.2% for the 10.6 L "
              "heavy-duty opposed-piston (OP3) diesel; 'large areas of the "
              "speed/load map above 44% BTE'; heat rejection 'on the order "
              "of 30% lower' than a four-stroke; 10%+ fuel-economy "
              "advantage over a best-in-class reference engine in real-"
              "world operation (measured 16% / 4% / 21% on three routes "
              "against a Freightliner Cascadia with a Detroit DD15 Gen 5); "
              "conventional one-box underfloor DOC+DPF+SCR+ASC "
              "aftertreatment only",
        source="Achates Power, 'Opposed-Piston Heavy-Duty Diesel Engine "
               "Performance and Emissions Summary', 2024-05-13",
        url="https://achatespower.com/wp-content/uploads/2024/05/"
            "Heavy-Duty-Diesel-Engine-Performance-and-Emissions-Summary-"
            "5.13.2024.pdf",
        evidence_quality=(
            "PRIMARY DOCUMENT, FETCHED AND READ IN FULL (not a search "
            "summary - this is a strictly better evidence class than any "
            "external figure in WS8, whose environment blocked egress). "
            "It is nonetheless a MANUFACTURER'S document reporting its own "
            "demonstration programme. Mitigating: the programme is led by "
            "CALSTART and supported by CARB, in-use emissions were measured "
            "by UC-Riverside with PEMS, the fleet comparison was run by "
            "Walmart against a competitor's production engine, and "
            "dynamometer testing was independently repeated by Aramco "
            "Services. Aggravating: no peer-reviewed BSFC map is published, "
            "the 49.2% figure is a single peak point, and no engine mass is "
            "stated. WS9 therefore uses ONLY the peak-BTE number, carries "
            "the engine at the four-stroke's mass, and reports the "
            "BREAK-EVEN peak BTE at which S6 exactly clears the gate so the "
            "lead can see how much of the claim must be true."),
        used_for="S6's opposed-piston-class engine island BSFC target"),
    "ICCT_TUV": dict(
        claim="typical EU tractor-trailer 32.6 L/100 km over the EU "
              "regulatory Long Haul cycle; 33.1 L/100 km at that cycle's "
              "regulatory payload of 19.3 t; best-in-class EU 29.9",
        source="ICCT / TUV NORD, fuel consumption testing of tractor-"
               "trailers in the European Union and the United States",
        url="https://theicct.org/publication/fuel-consumption-testing-of-"
            "tractor-trailers-in-the-european-union-and-the-united-states/",
        evidence_quality="INHERITED FROM WS8 unchanged (search-summary "
                         "level there; not re-fetched here). Carried so "
                         "that WS9's F7 ensemble cross-check is against the "
                         "same band WS8 was checked against.",
        used_for="the F7 ensemble cross-check of the ruler"),
    "VOLVO_RET_TH": dict(
        claim="gearbox-mounted hydraulic retarder (Voith), max brake torque "
              "on the propeller shaft 3,250 Nm; 3,000 Nm at 750 r/min; "
              "1,800 Nm at 500 r/min; installation weight including oil "
              "105 kg; oil change volume 5.4 L; combined retarder + engine "
              "brake power up to 825 kW (D13K Euro 6 with VEB+); 'in the "
              "case of continuous operation, effect is reduced when water "
              "and oil temperature increase'",
        source="Volvo Truck Corporation, Fact Sheet 'Retarder RET-TH', "
               "ENG 1(2)-2(2), version 06, 2014-03-10",
        url="https://stpi.it.volvo.com/STPIFiles/Volvo/FactSheet/"
            "RET-TH_Eng_06_1875330.pdf",
        evidence_quality="PRIMARY OEM FACT SHEET, FETCHED AND READ IN FULL. "
                         "Torque figures and mass are the manufacturer's "
                         "own specification for a shipped Class 8 product. "
                         "The CONTINUOUS thermal rating is NOT stated on "
                         "the sheet (only that it falls with coolant "
                         "temperature), so WS9 declares it and flags it.",
        used_for="ESC-6: the ruler's hydraulic retarder (S0R)"),
    "ISO_8528_PRP": dict(
        claim="ISO 8528-1 defines ESP (emergency standby), PRP (prime, "
              "unlimited hours, 10% overload for 1 h in 12, 24-hour average "
              "load factor 70-75%) and COP (continuous, constant load). "
              "For one engine family, prime ratings run about 10% below "
              "standby ratings; the Cummins QSX15 (the industrial sibling "
              "of the on-highway X15) carries generator-drive standby "
              "ratings of roughly 350-500 kW with 'prime ratings about 10% "
              "below', against an on-highway X15 automotive peak of 503 kW "
              "at 2,100 rpm",
        source="ISO 8528-1 rating definitions as summarised by MTU Onsite "
               "Energy (Power Engineering) and by a QSX15 generator-set "
               "ratings guide; Cummins X15 published automotive ratings",
        url="https://www.power-eng.com/operations-maintenance/"
            "understanding-generator-set-ratings-for-maximum-performance-"
            "and-reliability/",
        evidence_quality="SEARCH-SUMMARY plus one FETCHED secondary page. "
                         "The ISO 8528-1 rating STRUCTURE is standard and "
                         "not in dispute; the 0.90 PRP/ESP ratio is an "
                         "industry rule of thumb corroborated by the QSX15 "
                         "guide's 'prime ratings about 10% below', not read "
                         "from the standard itself. Provisional per E13.",
        used_for="ESC-4: WS9's Class 8 prime-power derating basis"),
    "PACK_WH_PER_KG": dict(
        claim="pack-level gravimetric energy density of BEV road-car packs "
              "has tracked ~+3.4 Wh/kg/year since 2019; the 2026 cohort "
              "averages 175 Wh/kg; the 2023 NIO 150 kWh pack reaches "
              "261 Wh/kg; the 2022 Ford F-150 Lightning extended-range "
              "truck pack is 174 Wh/kg",
        source="batterydesign.net, 'Pack Gravimetric Energy Density'",
        url="https://www.batterydesign.net/pack-gravimetric-energy-density/",
        evidence_quality="FETCHED SECONDARY AGGREGATOR. Road-car packs, not "
                         "Class 8 packs. WS9 takes a DISCOUNT to 160 Wh/kg "
                         "for a Class 8 pack (crash structure, larger "
                         "modules, higher-current busbars, more thermal "
                         "hardware), which is the conservative direction "
                         "for S4' - the candidate the cell is being cited "
                         "for. Provisional per E13.",
        used_for="ESC-1(c): S4's cited external energy-optimised cell as an "
                 "explicitly non-WS3 bracket"),
    "ATKINSON_BTE": dict(
        claim="41% peak brake thermal efficiency for a production Atkinson-"
              "cycle naturally aspirated petrol engine (Toyota 2.5 L "
              "Dynamic Force / 2.0 L hybrid Atkinson variant)",
        source="Toyota Motor Corporation engine announcements as reported "
               "by SAE Mobility Engineering and Green Car Congress",
        url="https://www.mobilityengineeringtech.com/component/content/"
            "article/43504-sae-ma-02815",
        evidence_quality="SEARCH-SUMMARY level. The figure is for a 2-2.5 L "
                         "LIGHT-DUTY engine; WS9 applies it to a 7 L-class "
                         "pinned-point prime mover. Bore-scale and a fixed "
                         "operating point both argue the larger engine "
                         "would do at least as well, but no heavy-duty "
                         "Atkinson petrol product exists to check it "
                         "against - which is itself the durability finding "
                         "reported in the prime-mover task.",
        used_for="prime-mover-at-the-pin: Atkinson petrol"),
    "NG_SI_BTE": dict(
        claim="the Cummins X15N stoichiometric spark-ignited natural-gas "
              "engine is 'about 10% more efficient than the ISX12 G', at up "
              "to 500 hp / 1,850 lb-ft",
        source="Cummins X15N product coverage (Fleet Equipment, CCJ, "
               "Cummins Inc.)",
        url="https://www.cummins.com/engines/x15n-2024",
        evidence_quality="SEARCH-SUMMARY level, and the '10% more "
                         "efficient' figure is relative to another gas "
                         "engine rather than an absolute BTE. WS9 declares "
                         "40.5% peak BTE for a pinned-point stoichiometric-"
                         "EGR HD gas engine and states that the number is "
                         "WS9's, corroborated by rather than read from the "
                         "source.",
        used_for="prime-mover-at-the-pin: natural-gas SI"),
}


# =====================================================================
#  1. THE TWO DUTIES (R29, assignment "Design duty")
# =====================================================================
DESIGN_DUTY = "GH-REG-165"
"""DESIGN DUTY of record (R29; assignment: "Primary: GRADE-HEAVY REGIONAL
corridor (define from WS8's grade-heavy corner ...)").

DEFINED, not invented: it is WS8's REG-165 regional cycle built with
`grade_heavy=True` - i.e. the REGIONAL leg of WS8's own grade-heavy corner,
taken verbatim from `ws8_cycles.build_regional`. Nothing about its
construction is re-derived here (assignment: "do not re-derive what is
ratified; extend it"). Its 8-seed ensemble statistics are reported in full
so the reader can see what "grade-heavy regional" actually contains."""

CONTROL_DUTY = "LH-520"
"""CONTROL DUTY (R29: "with the flat line-haul corridor retained as a
control on which the incumbent is CONCEDED near-optimal").

WS8's LH-520 line-haul corridor at the NOMINAL corner, taken verbatim.

A NOTE ON THE WORD "FLAT", because it matters and could mislead: LH-520 as
WS8 built it is not a flat road - it carries the assignment-ordered 6%
mountain and ~3,704 m of climb over 520 km. R29 calls it "flat" BY CONTRAST
with the grade-heavy design duty, and R29's own supporting numbers (S0 in
top gear for 0.72 of moving time; duty-averaged 196.8 g/kWh against the
185.0 island) are WS8's LH-520-as-ordered figures, not grade-zeroed ones.
WS9 therefore reads "the flat line-haul corridor" as LH-520 at the nominal
corner and says so here rather than silently choosing. The genuinely
grade-zeroed LH-520 appears in exactly one place - the F7 calibration
cross-check of the ruler - where WS8 also used it."""

FLEET_MIX_IS_FORBIDDEN = (
    "assignment: 'Report every candidate on both, per-class, never only as "
    "a fleet average.' WS9 reports no fleet blend anywhere. Every headline "
    "is per duty class.")


# =====================================================================
#  2. THE RULER (ESC-6): S0 + a hydraulic retarder, mass charged
# =====================================================================
@dataclass(frozen=True)
class Retarder:
    """Secondary (gearbox-output) hydrodynamic retarder on the ruler.

    ESC-6, ruled in R27: "S0 gains a hydraulic retarder in WS9 with its mass
    charged - the ruler gets the equipment the duty demands." A grade-heavy
    regional design duty is exactly the duty a retarder is bought for, and
    WS8's ESC-WS8-6 raised it because a compression-brake-only ruler hands
    the electric candidates a descent-speed advantage they did not earn.

    Characteristic from the Volvo RET-TH fact sheet [WS9-CITED
    VOLVO_RET_TH], read verbatim: braking torque at the PROPELLER SHAFT
    1,800 Nm at 500 r/min, 3,000 Nm at 750 r/min, 3,250 Nm maximum. WS9
    interpolates those three published points on a power law in shaft speed
    and holds 3,250 Nm above the speed at which the law reaches it - which
    is the physical shape of a hydrodynamic brake (torque ~ n^2 until the
    fill control saturates, then constant torque until the thermal limit
    bites).

    The CONTINUOUS rating is not on the fact sheet (it says only that the
    effect falls as coolant and oil temperature rise), so WS9 declares one
    and flags it: a retarder rejects into the ENGINE COOLANT circuit, so its
    continuous capability is set by the cooling package, not by the rotor.
    """
    t_max_propshaft_Nm: float = 3250.0        # [WS9-CITED VOLVO_RET_TH]
    t_at_750rpm_Nm: float = 3000.0            # [WS9-CITED VOLVO_RET_TH]
    t_at_500rpm_Nm: float = 1800.0            # [WS9-CITED VOLVO_RET_TH]
    p_continuous_kW: float = 350.0            # [WS9-PROV] cooling-package
                                              # limited; see docstring
    mass_installed_kg: float = 105.0          # [WS9-CITED VOLVO_RET_TH]
                                              # "installation weight
                                              # including oil"
    mass_cooling_delta_kg: float = 25.0       # [WS9-PROV] the larger
                                              # radiator/oil cooler a
                                              # retarder-equipped tractor
                                              # carries
    heat_destination: str = "engine coolant circuit"

    @property
    def mass_kg(self) -> float:
        return self.mass_installed_kg + self.mass_cooling_delta_kg


RET = Retarder()


# =====================================================================
#  3. S5 - minimal transmission (2-speed dog box)
# =====================================================================
@dataclass(frozen=True)
class DogBox:
    """A 2-speed dog box: no synchronisers, no launch clutch, no
    power-shift. High gear is DIRECT (no countershaft power path), so it
    inherits exactly the ruler's cruise driveline efficiency; low gear runs
    through the countershaft.

    MASS. WS8's ledger prices ONE constant-mesh helical stage in a housing
    at 145 kg (`ML.m_fixed_ratio_box`) and a 12-speed AMT at 325 kg. A
    2-speed dog box is the first plus a second gear pair, a dog ring, one
    shift actuator and its air/electric control - and NOT a launch clutch,
    NOT synchronisers, NOT the 10 extra ratios. 205 kg is that construction,
    itemised below so the number is auditable rather than asserted."""
    m_base_single_stage_kg: float = 145.0     # [WS8] ML.m_fixed_ratio_box
    m_second_gear_pair_kg: float = 38.0       # [WS9-PROV]
    m_dog_ring_and_shifter_kg: float = 14.0   # [WS9-PROV]
    m_shift_actuator_control_kg: float = 8.0  # [WS9-PROV]
    rpm_lug_floor: float = 1000.0             # [WS8] S3's RPM_COUPLE_MIN,
                                              # carried unchanged
    rpm_ceiling: float = 2100.0               # [WS8] AMT over-speed limit
    shift_time_s: float = 0.6                 # [WS9-PROV] dog-shift with
                                              # engine speed matching
    contiguity_margin: float = 0.98           # [WS9-PROV] the ratio step is
                                              # taken 2% inside the physics
                                              # bound so the two gears'
                                              # usable bands OVERLAP by 2%
                                              # of engine speed rather than
                                              # meeting at a single point -
                                              # a design margin, declared,
                                              # and it costs cruise rpm
    eta_high_is_direct: bool = True

    @property
    def mass_kg(self) -> float:
        return (self.m_base_single_stage_kg + self.m_second_gear_pair_kg
                + self.m_dog_ring_and_shifter_kg
                + self.m_shift_actuator_control_kg)

    @property
    def span_max(self) -> float:
        """Largest ratio step that still leaves the engine a gear at EVERY
        road speed: at the shift speed the low gear must be at or below its
        over-speed ceiling exactly when the high gear is at or above its
        lugging floor. This is a physics bound, stated closed-form (WS8
        finding F12 asked for exactly this rather than a swept-grid
        property)."""
        return self.rpm_ceiling / self.rpm_lug_floor

    @property
    def span_used(self) -> float:
        """The step actually built: the physics bound less the declared
        contiguity margin."""
        return self.span_max * self.contiguity_margin


DOGBOX = DogBox()

S5_GRADE_MARGIN = 0.03
"""[WS9-PROV] Torque margin applied to the 6%-grade wall when solving the
low ratio, so the design is not sitting exactly on a cliff edge."""

S5_LAUNCH_ACCEL_MS2 = 0.35
"""[WS9-PROV] Launch acceleration the buffer must be able to feed, from
rest to the low gear's coupling floor. NOT the driver model's comfortable
0.55 m/s^2: a minimal-transmission truck launches on its machine and its
buffer, and sizing the buffer to the driver's wish rather than to a stated
duty is how buffers become packs. 0.35 m/s^2 takes 36.3 t to the coupling
floor in about 26 s over about 120 m, which is a brisk launch for a loaded
combination. Where the driver asks for more, the integrator gives the truck
the speed its envelope actually supports and charges it the extra time."""


# =====================================================================
#  4. S7 - marginal-mass electrification of an existing trailer axle
# =====================================================================
@dataclass(frozen=True)
class TrailerAxle:
    """Motorising ONE axle of the existing trailer tandem.

    "no new axle" (assignment) is read as: the combination does not gain an
    axle. It does NOT mean the hardware that turns a dead beam into a driven
    axle is free - the assignment's next clause is "Charge everything", so
    the carrier delta is charged."""
    m_carrier_delta_kg: float = 230.0     # [WS9-PROV] hypoid carrier,
                                          # halfshafts and a heavier beam,
                                          # over a dead trailer axle
    m_disconnect_kg: float = 42.0         # [WS8] the same dog disconnect
                                          # WS8 priced for S2/S3
    m_trailer_hv_interface_kg: float = 38.0   # [WS9-PROV] tractor-trailer
                                          # HV coupler, cable reel, trailer
                                          # junction box and its controller
    axle_load_share: float = 0.5          # one axle of the trailer tandem


TRL = TrailerAxle()


# =====================================================================
#  5. R30 - THE COLD WALL: preconditioning and the waste-heat cab path
# =====================================================================
@dataclass(frozen=True)
class ThermalR30:
    """R30, quoted: "Every WS9 electrified candidate carries pack
    preconditioning and a coolant/waste-heat cab-heating path as
    REQUIREMENTS, MODELLED, NOT ASSUMED; the conventional truck heats itself
    for free and the comparison must charge that."

    Both halves are modelled here as hardware with mass and as physics with
    a state:

    (a) PACK PRECONDITIONING. The pack carries a coolant loop with a
        heat exchanger to the engine circuit and a PTC heater for when no
        engine heat is available. Pack temperature is a STATE integrated
        through every run (ws9_thermal.PackThermal), starting cold-soaked
        at ambient, warmed by its own ohmic loss, by engine waste heat when
        an engine is running, and by the heater otherwise, and losing heat
        to ambient through a declared UA. The pack's charge acceptance at
        each sample is then WS3's own `Pack8.p_cont_chg_kw_at(T_pack)` -
        which is the method WS8's finding F2 found defined and never called.
        [R2-IMPL F2]

    (b) THE WASTE-HEAT CAB PATH. WS8 charged every electrified candidate a
        flat cold accessory load of 6.6 kW against the conventional truck's
        4.0 kW crank load, because a conventional truck heats its cab from
        engine coolant for free. WS9 splits that penalty into its two real
        parts and serves each from where it physically comes from: cab heat
        from ENGINE COOLANT whenever an engine is running (free), from the
        bus otherwise; battery thermal from the model in (a) rather than
        from a flat allowance. The split sums to WS8's own 3.2 kW delta, so
        nothing is invented - it is the same energy, sourced honestly."""
    cab_heat_kW_at_minus10C: float = 2.2      # [WS9-PROV] of WS8's 3.2 kW
    battery_thermal_kW_at_minus10C: float = 1.0   # [WS9-PROV] balance of it
    cab_heat_kW_at_plus45C: float = 0.0
    ac_load_bus_kW_at_plus45C: float = 4.0    # [WS9-PROV] electrified A/C
    ac_load_mech_kW_at_plus45C: float = 4.5   # [WS9-PROV] belt A/C, less
                                              # efficient, on the crank

    t_pack_target_C: float = 15.0             # [WS3] the temperature at
                                              # which WS3's cold charge-
                                              # acceptance interpolation
                                              # reaches its warm value
    ua_W_per_K_per_kg: float = 0.05           # [WS9-PROV] insulated HD pack
    cp_structure_J_per_kgK: float = 900.0     # [WS9-PROV] aluminium and
                                              # steel pack structure
    q_coolant_to_pack_max_kW: float = 12.0    # [WS9-PROV] heat-exchanger
                                              # rating on the engine loop
    q_ptc_heater_max_kW: float = 10.0         # [WS9-PROV] electric heater

    m_pack_thermal_loop_kg: float = 35.0      # [WS9-PROV] coolant loop,
                                              # PTC heater, valves, pump,
                                              # pack insulation
    m_cab_waste_heat_path_kg: float = 15.0    # [WS9-PROV] coolant-to-cab
                                              # heat exchanger and plumbing

    @property
    def mass_kg(self) -> float:
        return self.m_pack_thermal_loop_kg + self.m_cab_waste_heat_path_kg


TH = ThermalR30()


# =====================================================================
#  6. R28 - the corner set of record
# =====================================================================
ALT_CORNER_M = 2000.0        # [BASELINE-v4] R28
ALT_CORNER_T_C = 45.0        # [BASELINE-v4] R28
COLD_CORNER_T_C = -10.0      # [BASELINE-v4] R28
COLD_CRR_FACTOR = 1.08       # [WS8] carried unchanged

R_SPECIFIC_AIR = 287.05      # J/(kg.K)
P_SEA_LEVEL_PA = 101325.0


def air_density(alt_m, t_amb_c):
    """ISA pressure lapse to `alt_m`, then the ideal gas law at the actual
    ambient temperature. This is the member WS8's corner set had no case
    for (finding F11's "things I looked for": no altitude and no hot
    ambient), and R28 now orders one."""
    p = P_SEA_LEVEL_PA * (1.0 - 2.25577e-5 * alt_m) ** 5.25588
    return p / (R_SPECIFIC_AIR * (t_amb_c + 273.15))


# =====================================================================
#  7. ESC-4 - the Class 8 prime-power derating basis
# =====================================================================
PRP_OVER_AUTOMOTIVE_PEAK = 0.90
"""ESC-4, ruled in R27: "the R18 flat-rating transfer stands as a bracket;
WS9 SOURCES a Class 8 prime-power derating basis."

THE BASIS WS9 SOURCES [WS9-CITED ISO_8528_PRP]. ISO 8528-1 rates
reciprocating-engine generating sets in classes: ESP (emergency standby),
PRP (prime, unlimited hours, 10% overload for one hour in twelve, 24-hour
average load factor 70-75%) and COP (continuous, constant load). Within one
engine family, prime ratings run about 10% below standby ratings. For the
15 L class the correspondence is direct: the on-highway Cummins X15 peaks at
503 kW at 2,100 rpm, and the industrial QSX15 - the same engine family -
carries generator-drive STANDBY ratings of roughly 350-500 kW with prime
about 10% below. Taking the automotive peak as the standby-equivalent point
gives PRP = 0.90 x automotive peak.

WHY PRP AND NOT COP. A series genset in a truck sees a VARIABLE load with a
24-hour average load factor far below 70% and needs short overload
capability on grades - which is the PRP duty definition, not COP's constant
load. Choosing COP (0.90 x PRP = 0.81 x peak) would rate the genset for a
duty it does not do.

DIRECTION OF ERROR, stated: R18's transferred ratio is 132/153.3 = 0.8611.
PRP at 0.90 is 4.5% MORE genset power, which makes series candidates climb
slightly faster and leaves them slightly less unserved energy - i.e. it
FLATTERS them. R18's ratio is carried alongside as the declared bracket
(`R18_BRACKET_RATIO`), and both are exported."""

R18_BRACKET_RATIO = 132.0 / 153.3      # [WS4] R18, carried as the bracket


# =====================================================================
#  8. ESC-3 - the electricity term, the metric of record, and the lenses
# =====================================================================
@dataclass(frozen=True)
class EnergyAccounting:
    """ESC-3, ruled in R27: "Vehicle One's metric acquires an electricity
    term for any plug-in candidate - PRIMARY ENERGY per payload tonne-km at
    a declared grid primary-energy factor, with a CO2-per-payload-tonne-km
    second lens and a factor sensitivity."

    The assignment restates it as the metric for the whole trial: "metric =
    primary energy per PAYLOAD tonne-km".

    CONSEQUENCE WORTH STATING BEFORE ANY NUMBER. `pef_diesel` multiplies
    every candidate's fuel term identically, so for every candidate that
    burns only diesel it is a COMMON FACTOR and cannot move a margin by one
    part in 10^12. WS9 asserts that in its sanity block rather than claiming
    it. The primary-energy metric therefore changes exactly one thing in
    this trial: how S4' - the only candidate that imports grid energy - is
    scored against the rest.

    CO2 FACTORS ARE DERIVED, NOT CITED. Diesel, petrol and methane
    tank-to-wheel CO2 follow from a carbon balance on a declared H:C ratio
    and the fuel's LHV, computed in ws9_fuels.py. Only the WELL-TO-TANK
    multipliers and the grid intensity are declared."""

    pef_diesel: float = 1.19          # [WS9-PROV] well-to-tank primary
                                      # energy per unit of diesel LHV
                                      # (extraction, refining, distribution)
    pef_petrol: float = 1.20          # [WS9-PROV]
    pef_natural_gas: float = 1.13     # [WS9-PROV] pipeline gas, compression
    pef_grid: float = 2.1             # [WS9-PROV] EU Energy Efficiency
                                      # Directive default primary-energy
                                      # factor for electricity as amended
                                      # by Directive (EU) 2018/2002.
                                      # RECALLED, NOT FETCHED - escalated
                                      # (ESC-WS9-2) and carried with the
                                      # +/-50% sensitivity ESC-3 orders.
    eta_charge_grid_to_pack: float = 0.9215   # [WS9-PROV] 0.95 off-board
                                      # charger and cabling x 0.97 pack
                                      # charge acceptance

    co2_grid_kg_per_kWh: float = 0.28
    """[WS9-PROV] grid CO2e intensity at the meter. Chosen to sit BETWEEN
    the EU average (about 0.21 kg/kWh in 2024, after an 11% year-on-year
    fall) and the US average (about 0.37 kg/kWh), because Vehicle One has no
    declared market. The +/-50% sensitivity ESC-3 orders spans 0.14-0.42,
    which BRACKETS BOTH - so the sensitivity is not decoration here, it is
    the whole geographic question. Escalated as ESC-WS9-2."""

    factor_sensitivity: float = 0.50   # [ASSIGNMENT] "factor sensitivity
                                       # +/-50%"


EA = EnergyAccounting()


# =====================================================================
#  9. ESC-1(c) - the cited external energy-optimised cell (S4' only)
# =====================================================================
@dataclass(frozen=True)
class CitedCell:
    """ESC-1(c), ruled in R27: "S4 is re-posed in WS9 as S4' carrying a
    cited external energy-optimised cell as an explicitly NON-WS3 bracket.
    WS3 is not reopened."

    This object exists so the non-WS3 bracket is a single, visible,
    replaceable declaration rather than a number smuggled into a pack model.
    It is used by S4' AND BY NOTHING ELSE - S5's and S7's buffers stay on
    WS3's own characterised cells, where WS3's power-oriented selection is
    exactly right for a buffer duty (ESC-WS8-1's own reasoning)."""
    label: str = "cited external energy-optimised Class 8 traction pack"
    pack_Wh_per_kg: float = 160.0
    """[WS9-CITED PACK_WH_PER_KG] PACK level, not cell level. The cited
    tracker puts the 2026 BEV road-car cohort at 175 Wh/kg pack-level and
    the best 2023 pack at 261. WS9 DISCOUNTS to 160 for a Class 8 pack. For
    scale: WS3's NMC-P-40 asymptotes to 85.6 Wh/kg pack-level, so the
    bracket is 1.87x WS3's basis - which is what ESC-WS8-1 predicted when it
    said energy-optimised automotive cells sit at "roughly double this
    pack-level density"."""
    c_cont_dis: float = 2.0        # [WS9-PROV] an energy cell, not a power
    c_cont_chg: float = 1.0        # cell: 2 C out, 1 C in continuous,
    c_pulse10_dis: float = 4.0     # 4 C / 2 C for 10 s
    c_pulse10_chg: float = 2.0
    cold_chg_factor_minus10C: float = 0.15
    """[WS9-PROV] An energy-optimised NMC/NCA cell is at least as cold-shy
    as WS3's power NMC (WS3 measures 0.127). 0.15 is a shade kinder, which
    is the CONSERVATIVE direction for the incumbent and the generous
    direction for S4' - stated so it cannot be mistaken for a finding."""
    cp_J_per_kgK: float = 1000.0
    usable_fraction: float = 0.85  # [WS9-PROV] an energy pack is cycled
                                   # deeper than a buffer
    chem: str = "NMC-energy(external)"


CITED_CELL = CitedCell()


# =====================================================================
# 10. Buffer sizing rules (stated BEFORE any pack is built)
# =====================================================================
BUFFER_CELL = "LTO-23"
"""[WS3] The buffer cell for S5 and S7.

WHY LTO AND NOT WS8's NMC-P-40, stated as a rule rather than a preference:
a buffer is bought for POWER, COLD ACCEPTANCE and CYCLE LIFE, and WS3
characterised a cell that is better than NMC on all three -
  charge acceptance   8 C continuous / 12 C pulse   vs NMC's 4 C / 8 C
  cold acceptance     4.3967 kW/kWh at -10 C against ~4.0 warm, i.e. a
                      factor of 1.10 - LTO DOES NOT COLLAPSE IN THE COLD,
                      which is R30's wall attacked at the chemistry rather
                      than at the heater
  cycle life          20,000 equivalent full cycles vs NMC's 3,000, on a
                      duty that cycles the buffer many times per trip
and worse on exactly one thing, gravimetric energy - which is what a buffer
does not need. WS8 used NMC for every pack because it was the densest of
WS3's three; that is the right choice for S4's ENERGY pack and the wrong one
for a buffer. The mass difference is reported as an arithmetic bracket.

This is a WS3-characterised cell, so ESC-WS8-1 does not apply to it."""

BUFFER_USABLE_FRACTION = 0.80      # [WS8] carried unchanged
BUFFER_SOC_TARGET = 0.60           # [WS8] carried unchanged
BUFFER_SOC_FLOOR = 0.15            # [WS8] carried unchanged
BUFFER_SOC_CEIL = 0.95             # [WS8] carried unchanged


# =====================================================================
# 11. Machine-basis gate (ESC-2, ruled in R27)
# =====================================================================
MACHINE_STRETCH_GATE_K = 2.0
"""ESC-2, ruled in R27: "WS9 rule: machines scaled <=2.0x from WS2's
validated range may use WS2 maps; beyond that, a cited external HD machine
basis with direction of error stated."

WS9 treats this as a HARD GATE, checked in code for every machine every
candidate builds, and exported. WS8's S3 axle-B machine sat at k=3.60 and
would have failed it; no WS9 machine may. Where a design would need more,
the design is changed rather than the gate."""


# =====================================================================
# 12. R14 export discipline / advance-kill criteria
# =====================================================================
ADVANCE_NOMINAL_PCT = 3.0
ADVANCE_CORNER_PCT = 0.0
ADVANCE_STATISTIC = "ensemble_min"
ADVANCE_DUTY = DESIGN_DUTY
ADVANCE_TEXT = (
    "assignment, quoted verbatim: 'ADVANCE only if >=3% better than S0 on "
    "the DESIGN DUTY at nominal, ensemble-min, AND >=0% at every R28 "
    "corner; report the control-duty result alongside without it gating.'")

WHR_GATE_PCT = 2.5
"""[BASELINE-v4] R31 / assignment: electric turbocompound is admitted to S6
"ONLY if it clears the 2.5% net gate on the design duty"."""


def params_dump():
    return dict(
        inherited_from_ws8=dict(
            vehicle=asdict(VEH), adhesion=asdict(ADH), aux=asdict(AUX),
            driveline=asdict(DL), mass_ledger=asdict(ML),
            scaling=asdict(SC), cycle=asdict(CY),
            fuel=dict(LHV_kJ_per_g=LHV_KJ_PER_G,
                      diesel_density_kg_per_L=DIESEL_DENSITY_KG_PER_L)),
        ws9_added=dict(
            retarder=asdict(RET), retarder_mass_kg=RET.mass_kg,
            dog_box=asdict(DOGBOX), dog_box_mass_kg=DOGBOX.mass_kg,
            dog_box_span_max=DOGBOX.span_max,
            dog_box_span_used=DOGBOX.span_used,
            trailer_axle=asdict(TRL),
            thermal_R30=asdict(TH), thermal_R30_mass_kg=TH.mass_kg,
            energy_accounting=asdict(EA),
            cited_cell=asdict(CITED_CELL),
            buffer_cell=BUFFER_CELL,
            buffer_usable_fraction=BUFFER_USABLE_FRACTION,
            s5_grade_margin=S5_GRADE_MARGIN,
            s5_launch_accel_ms2=S5_LAUNCH_ACCEL_MS2,
            prp_over_automotive_peak=PRP_OVER_AUTOMOTIVE_PEAK,
            r18_bracket_ratio=R18_BRACKET_RATIO,
            machine_stretch_gate_k=MACHINE_STRETCH_GATE_K,
            altitude_corner=dict(alt_m=ALT_CORNER_M, t_amb_C=ALT_CORNER_T_C,
                                 rho_air=air_density(ALT_CORNER_M,
                                                     ALT_CORNER_T_C)),
            cold_corner=dict(t_amb_C=COLD_CORNER_T_C,
                             crr_factor=COLD_CRR_FACTOR,
                             rho_air=VEH.rho_air_cold)),
        duties=dict(design=DESIGN_DUTY, control=CONTROL_DUTY,
                    no_fleet_average=FLEET_MIX_IS_FORBIDDEN),
        advance_kill=dict(nominal_pct=ADVANCE_NOMINAL_PCT,
                          every_corner_pct=ADVANCE_CORNER_PCT,
                          statistic=ADVANCE_STATISTIC, duty=ADVANCE_DUTY,
                          text=ADVANCE_TEXT),
        whr_gate_pct=WHR_GATE_PCT,
        citations=CITATIONS,
    )
