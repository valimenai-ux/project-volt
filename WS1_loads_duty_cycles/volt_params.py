"""
Project Volt - WS1 Loads & Duty Cycles
Vehicle, powertrain and environment parameters.

All values traceable to BASELINE_v0.md unless marked [WS1-ASSUMPTION].
SI units throughout.
"""
from dataclasses import dataclass, field, asdict

G = 9.81  # m/s^2


@dataclass(frozen=True)
class Vehicle:
    # ---- from BASELINE_v0.md (authoritative) ----
    m_gvw: float = 6600.0        # kg, GVW Isuzu NPR-HD
    r_dyn: float = 0.37          # m, 215/85R16 dynamic radius
    CdA: float = 4.2             # m^2
    Crr: float = 0.009           # -
    fd_ratio: float = 2.8        # engine -> wheel fixed final drive (V2 direct path)
    motor_ratio: float = 10.0    # motor -> wheel reduction
    F_trac_max: float = 13500.0  # N, 13.5 kN 0-20 km/h

    # ---- WS1 assumptions ----
    # Operating curb mass = NPR-HD chassis-cab + 16 ft dry-freight body
    # + driver + full fuel/DEF. GVWR 6,600 kg => payload at GVW = 2,900 kg.
    m_curb_operating: float = 3700.0   # kg  [WS1-ASSUMPTION]
    rho_air: float = 1.20              # kg/m^3, ~20 C sea level.
                                       # Chosen because it reproduces the
                                       # baseline's "85 km/h -> 2.0 kN / 47 kW".

    # Effective mass factor (rotating inertia referred to the road).
    #   wheels/hubs/drums  I ~ 25 kg.m^2      -> 25/0.37^2   = 183 kg
    #   motor rotor 0.08 kg.m^2 at 10:1       -> 8.0/0.37^2  =  58 kg
    #                                    total ~ 241 kg on 6600 kg -> 1.037
    #   + engine/flywheel 0.60 kg.m^2 at 2.8:1 (V2 lockup only) -> +34 kg
    # A single fixed reduction is why this is so low; a geared truck in a
    # low gear would be 1.2+.
    lam_rot: float = 1.04              # [WS1-ASSUMPTION]
    lam_rot_lockup: float = 1.045      # [WS1-ASSUMPTION]

    # Chassis geometry, needed only for the driven-axle adhesion check.
    # [WS1-ASSUMPTION] 176 in wheelbase (the length that carries a 16 ft
    # body), CoG 1.2 m up loaded / 1.0 m empty, and a static rear-axle
    # share of 65% at GVW falling to 48% at the operating curb mass.
    wheelbase: float = 4.20            # m
    h_cg_loaded: float = 1.20          # m
    h_cg_empty: float = 1.00           # m
    rear_axle_share_gvw: float = 0.65
    rear_axle_share_curb: float = 0.48

    @property
    def m_payload_at_gvw(self) -> float:
        return self.m_gvw - self.m_curb_operating


@dataclass(frozen=True)
class Driveline:
    """Efficiency chain. Component values from BASELINE_v0.md."""
    eta_gen: float = 0.94        # engine shaft -> DC bus (generator + rectifier)
    eta_pe: float = 0.97         # bus / power-electronics distribution
    eta_inv_mot: float = 0.92    # inverter + traction motor
    eta_red: float = 0.97        # 10:1 reduction
    eta_direct: float = 0.95     # V2 lockup: clutch + driveshaft + 2.8:1 axle
    eta_batt_chg: float = 0.97   # [WS1-ASSUMPTION] high-power buffer cell
    eta_batt_dis: float = 0.97   # [WS1-ASSUMPTION]

    @property
    def eta_bus_to_wheel(self) -> float:
        """DC bus -> tyre contact patch (traction)."""
        return self.eta_pe * self.eta_inv_mot * self.eta_red      # 0.8657

    @property
    def eta_wheel_to_bus(self) -> float:
        """Tyre contact patch -> DC bus (regen). Assumed symmetric.
        [WS1-ASSUMPTION] - real machines are typically 1-2 pts worse
        generating at low speed; flagged to WS2."""
        return self.eta_red * self.eta_inv_mot * self.eta_pe      # 0.8657

    @property
    def eta_series_total(self) -> float:
        """Engine shaft -> wheel, series path."""
        return self.eta_gen * self.eta_bus_to_wheel               # 0.8137


@dataclass(frozen=True)
class Aux:
    """Accessory electrical load at the DC bus. [WS1-ASSUMPTION]
    NPR-HD has hydraulic (not air) brakes, so no air compressor.
      electro-hydraulic steering  ~0.3 kW avg
      brake boost / vacuum pump   ~0.3 kW avg
      cab HVAC                    ~1.0 kW avg (2-4 kW hot day, doors open)
      24 V loads, lights, ECUs    ~0.4 kW
    """
    p_aux_nom: float = 2000.0    # W
    p_aux_low: float = 500.0     # W  (mild day, night, no HVAC)
    p_aux_high: float = 4000.0   # W  (hot day, parcel duty, doors open)


@dataclass(frozen=True)
class Engine:
    """Stock 4HK1-TC reference curve. Baseline: ~700 Nm @1600 rpm, ~150 kW,
    idle ~700 rpm. Interpolated full-load torque curve [WS1-ASSUMPTION],
    anchored on those two published points."""
    idle_rpm: float = 700.0
    rpm_pts: tuple = (700, 1000, 1200, 1400, 1600, 1800,
                      2000, 2200, 2400, 2600, 2800, 3000)
    trq_pts: tuple = (380, 540, 630, 685, 700, 700,
                      685, 655, 610, 550, 490, 430)


@dataclass(frozen=True)
class Control:
    """Supervisory-control assumptions used for the loads study."""
    v_lockup: float = 65.0 / 3.6      # m/s, V2 series->direct handover
                                      # (baseline: "series below ~60-70 km/h")
    regen_cap_wheel: float = 75000.0  # W, assignment's 75 kW absorb limit,
                                      # applied AT THE WHEEL
    v_regen_blend_lo: float = 3.0 / 3.6   # m/s, regen fully off below
    v_regen_blend_hi: float = 8.0 / 3.6   # m/s, regen fully on above
    genset_v1_class: float = 50000.0  # W, baseline "~50 kW class"
    genset_v2_floor: float = 110000.0 # W, baseline floor


VEH = Vehicle()
DL = Driveline()
AUX = Aux()
ENG = Engine()
CTL = Control()


def params_dump():
    return {
        "vehicle": asdict(VEH),
        "driveline": asdict(DL),
        "driveline_derived": {
            "eta_bus_to_wheel": DL.eta_bus_to_wheel,
            "eta_wheel_to_bus": DL.eta_wheel_to_bus,
            "eta_series_total": DL.eta_series_total,
        },
        "aux": asdict(AUX),
        "engine": asdict(ENG),
        "control": asdict(CTL),
        "derived": {
            "payload_at_gvw_kg": VEH.m_payload_at_gvw,
        },
    }
