"""
Project Volt - WS4 (genset + Gate G1)
Engine, generator, driveline-chain and derate models.

Everything here is deterministic and declared. BSFC maps are WS4-CONSTRUCTED
Willans-line maps (no measured map was available for the exact candidate
calibrations); the construction is physically argued and every coefficient
is a named constant below. Labels carry "-W" (Willans) to make the
provenance impossible to miss downstream.

WS1 parameters are imported read-only from ../WS1_loads_duty_cycles.
SI units unless a name says otherwise. rpm = rev/min, torque = Nm,
BSFC = g/kWh (LHV basis), fuel LHV = 42.8 MJ/kg.
"""
import os
import sys
import numpy as np

WS1_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "WS1_loads_duty_cycles")
if WS1_DIR not in sys.path:
    sys.path.insert(0, WS1_DIR)

from volt_params import VEH, DL, AUX, ENG, CTL, G          # noqa: E402

LHV_KJ_PER_G = 42.8          # diesel lower heating value
BSFC_FROM_ETA = 3600.0 / LHV_KJ_PER_G   # 84.112 / eta_b -> g/kWh


# --------------------------------------------------------------- derate model
def derate_factor(alt_m, t_amb_c):
    """Continuous-power derate for a turbocharged, charge-air-cooled,
    electronically governed diesel [WS4-DECLARED, class-typical ISO 3046 /
    SAE J1349 practice; to be confirmed against the procured candidate's
    datasheet]:
      altitude: none to 1,000 m, then 4 % per 1,000 m
      ambient:  none to 30 C,   then 1 % per 5 C
    Multiplicative."""
    f_alt = 1.0 - 0.04 * max(0.0, alt_m - 1000.0) / 1000.0
    f_tmp = 1.0 - 0.002 * max(0.0, t_amb_c - 30.0)
    return f_alt * f_tmp


R6_CORNER = dict(alt_m=2000.0, t_amb_c=45.0)
R6_CORNER_REQUIRED_KW = 122.1          # ruling R6 rating basis (locked)


# ------------------------------------------------------------------- engines
class WillansEngine:
    """Willans-line BSFC construction.

    eta_b = eta_i0 * f_N(rpm) * f_phi(load) * BMEP/(BMEP+FMEP)
    BSFC  = 84.112 / eta_b   [g/kWh]

    FMEP(bar) = a0 + a1*(N/1000) + a2*(N/1000)^2  (Chen-Flynn style,
    warm engine, includes pumping). f_phi models light-load combustion
    deterioration and the smoke-limit enrichment near full load.
    """

    def __init__(self, name, disp_l, rpm_pts, trq_pts, eta_i0,
                 fmep_a=(0.75, 0.28, 0.075), idle_rpm=700.0,
                 rated_cont_kw=None, rated_cont_rpm=None, mass_kg=None,
                 label=""):
        self.name = name
        self.disp_m3 = disp_l * 1e-3
        self.rpm_pts = np.asarray(rpm_pts, float)
        self.trq_pts = np.asarray(trq_pts, float)
        self.eta_i0 = eta_i0
        self.fmep_a = fmep_a
        self.idle_rpm = idle_rpm
        self.rated_cont_kw = rated_cont_kw
        self.rated_cont_rpm = rated_cont_rpm
        self.mass_kg = mass_kg
        self.label = label

    # -- curves ---------------------------------------------------------
    def t_max(self, rpm):
        return np.interp(rpm, self.rpm_pts, self.trq_pts,
                         left=0.0, right=self.trq_pts[-1])

    def p_max_kw(self, rpm):
        return self.t_max(rpm) * np.asarray(rpm, float) * 2 * np.pi / 60 / 1e3

    def peak_power_kw(self):
        r = np.linspace(self.rpm_pts[0], self.rpm_pts[-1], 500)
        return float(np.max(self.p_max_kw(r)))

    # -- Willans pieces -------------------------------------------------
    def fmep_bar(self, rpm):
        a0, a1, a2 = self.fmep_a
        n = np.asarray(rpm, float) / 1000.0
        return a0 + a1 * n + a2 * n ** 2

    def bmep_bar(self, trq):
        return 4 * np.pi * np.asarray(trq, float) / self.disp_m3 / 1e5

    @staticmethod
    def _f_n(rpm):
        return 1.0 - 0.06 * ((np.asarray(rpm, float) - 1600.0) / 1400.0) ** 2

    @staticmethod
    def _f_phi(phi):
        """Light-load indicated-efficiency derate is MILD for a DI diesel
        (no throttling; the dominant light-load penalty is friction, which
        FMEP already carries): 5% at zero load. The 35%/unit slope above
        85% load is the smoke-limit enrichment. Calibrated so 25% load at
        1,800 rpm lands at ~245 g/kWh (published MD-diesel range 240-255)
        without moving the ~204 island or the ~227 rated point."""
        phi = np.asarray(phi, float)
        lo = 1.0 - 0.05 * np.clip(0.45 - phi, 0.0, None) / 0.45
        hi = 1.0 - 0.35 * np.clip(phi - 0.85, 0.0, None)
        return np.minimum(lo, hi)

    def eta_b(self, rpm, trq):
        rpm = np.asarray(rpm, float)
        trq = np.asarray(trq, float)
        tmax = np.maximum(self.t_max(rpm), 1e-6)
        phi = np.clip(trq / tmax, 0.0, 1.0)
        bmep = self.bmep_bar(trq)
        fmep = self.fmep_bar(rpm)
        mech = np.where(bmep > 0, bmep / (bmep + fmep), 0.0)
        return self.eta_i0 * self._f_n(rpm) * self._f_phi(phi) * mech

    def bsfc(self, rpm, trq):
        """g/kWh; inf at zero torque."""
        eb = self.eta_b(rpm, trq)
        return np.where(eb > 1e-4, BSFC_FROM_ETA / np.maximum(eb, 1e-4),
                        np.inf)

    def fuel_gps(self, rpm, trq):
        """Fuel rate [g/s] at (rpm, trq)."""
        p_kw = np.asarray(trq, float) * np.asarray(rpm, float) \
            * 2 * np.pi / 60 / 1e3
        return self.bsfc(rpm, trq) * np.clip(p_kw, 0.0, None) / 3600.0

    # -- optimisation helpers ------------------------------------------
    def grid(self, n_rpm=93, n_trq=76):
        r = np.linspace(self.rpm_pts[0], self.rpm_pts[-1], n_rpm)
        tq = np.linspace(1.0, float(self.trq_pts.max()), n_trq)
        return r, tq

    def min_bsfc_point(self, p_cap_kw=None):
        """(rpm, trq, kW, bsfc) at the map minimum, optionally capped to a
        continuous power rating."""
        r, tq = self.grid(400, 400)
        R, T = np.meshgrid(r, tq, indexing="ij")
        ok = T <= self.t_max(R)
        if p_cap_kw is not None:
            ok &= (T * R * 2 * np.pi / 60 / 1e3) <= p_cap_kw
        b = np.where(ok, self.bsfc(R, T), np.inf)
        i, j = np.unravel_index(np.argmin(b), b.shape)
        rpm, trq = float(R[i, j]), float(T[i, j])
        return dict(rpm=rpm, trq_Nm=trq,
                    p_kw=trq * rpm * 2 * np.pi / 60 / 1e3,
                    bsfc=float(b[i, j]))

    def t_opt(self, rpm):
        """BSFC-optimal torque at a given (welded) rpm."""
        rpm = float(rpm)
        tq = np.linspace(1.0, self.t_max(rpm), 300)
        b = self.bsfc(rpm, tq)
        return float(tq[np.argmin(b)])

    def opt_locus(self, n=140):
        """Best-BSFC (rpm, trq) for each shaft power - the 'e-line' a
        free-running genset would follow. Returns dict of arrays keyed by
        p_kw plus interpolators."""
        r, tq = self.grid(300, 300)
        R, T = np.meshgrid(r, tq, indexing="ij")
        ok = T <= self.t_max(R)
        P = T * R * 2 * np.pi / 60 / 1e3
        B = np.where(ok, self.bsfc(R, T), np.inf)
        p_grid = np.linspace(3.0, self.peak_power_kw() * 0.98, n)
        rr, tt, bb = [], [], []
        for p in p_grid:
            m = ok & (np.abs(P - p) < (p_grid[1] - p_grid[0]))
            if not m.any():
                rr.append(np.nan); tt.append(np.nan); bb.append(np.inf)
                continue
            bm = np.where(m, B, np.inf)
            i, j = np.unravel_index(np.argmin(bm), bm.shape)
            rr.append(R[i, j]); tt.append(T[i, j]); bb.append(bm[i, j])
        return dict(p_kw=p_grid, rpm=np.array(rr), trq=np.array(tt),
                    bsfc=np.array(bb))

    def export_map_csv(self, path, derate=1.0):
        r, tq = self.grid()
        with open(path, "w") as f:
            f.write("# WS4-CONSTRUCTED Willans-line BSFC map - NOT measured\n")
            f.write(f"# engine: {self.name}  ({self.label})\n")
            f.write(f"# displacement_l: {self.disp_m3*1e3:.3f}, "
                    f"eta_i0: {self.eta_i0}, fmep_bar(a0,a1,a2): "
                    f"{self.fmep_a}, LHV_MJ_per_kg: 42.8, "
                    f"full_load_derate_applied: {derate}\n")
            f.write("# torque printed to 1e-4 Nm so the (torque, BSFC) pair "
                    "is self-consistent for downstream interpolators "
                    "(adjudication r1 F6)\n")
            f.write("rpm,torque_Nm,bsfc_g_per_kWh\n")
            for rpm in r:
                tm = self.t_max(rpm) * derate
                for t in tq:
                    if t > tm:
                        continue
                    f.write(f"{rpm:.0f},{t:.4f},{self.bsfc(rpm, t):.1f}\n")


# Reference: baseline 4HK1-TC curve exactly as ratified in WS1 params.
ENG_REF = WillansEngine(
    "4HK1-TC-ref-W", 5.193, ENG.rpm_pts, ENG.trq_pts, eta_i0=0.448,
    idle_rpm=ENG.idle_rpm, rated_cont_kw=130.0, rated_cont_rpm=2200.0,
    mass_kg=500.0,
    label="baseline reference curve 700 Nm @ 1,600 rpm / ~153 kW")

# V2 candidate: same production 4HK1-TC hardware, genset/continuous
# recalibration with the torque peak moved to 1,400 rpm (the E3-compliant
# curve WS1 already tested in section 4.5, row 3: same 700 Nm @ 1,600
# anchor, ~152 kW peak, holds 6% directly at 59-67 km/h).
ENG_V2 = WillansEngine(
    "4HK1-V2C-W", 5.193,
    (700, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000),
    (520, 660, 730, 750, 700, 700, 685, 655, 610, 550, 490, 430),
    eta_i0=0.448, idle_rpm=700.0, rated_cont_kw=132.0, rated_cont_rpm=2200.0,
    mass_kg=500.0,
    label="4HK1-TC recalibrated: 750 Nm @ 1,400 rpm, 132 kW continuous")

# V1 candidate: Kubota V3307-CR-T class (3.331 L, 55.4 kW @ 2,600,
# 265 Nm @ 1,500, 305 kg dry, Tier 4F/Stage V production industrial).
ENG_V1 = WillansEngine(
    "V3307-V1C-W", 3.331,
    (900, 1100, 1300, 1500, 1700, 1900, 2100, 2300, 2500, 2600),
    (200, 232, 255, 265, 265, 258, 246, 232, 212, 203.5),
    eta_i0=0.435, fmep_a=(0.90, 0.32, 0.09), idle_rpm=900.0,
    rated_cont_kw=50.0, rated_cont_rpm=2200.0, mass_kg=305.0,
    label="Kubota V3307-CR-T class, 55.4 kW rated")


# ---------------------------------------------------------------- generators
class PMGenerator:
    """Crank-mounted IPM PM generator + active rectifier, shaft -> DC bus.

    P_loss = fe(N) + k_cu*(T/100)^2 + (pe0 + 1% * P_elec)   [kW]
    fe(N) = c_h*(N/1800) + c_e*(N/1800)^2  (iron + windage; present
    whenever the machine spins, even at zero torque - this is a real
    parasitic on the locked path, and it is charged to the engine there).
    """

    def __init__(self, name, cont_kw_in, peak_kw_in, c_h, c_e, k_cu,
                 pe0=0.15, pe_frac=0.01, mass_kg=None):
        self.name = name
        self.cont_kw_in = cont_kw_in
        self.peak_kw_in = peak_kw_in
        self.c_h, self.c_e, self.k_cu, self.pe0 = c_h, c_e, k_cu, pe0
        self.pe_frac = pe_frac      # rectifier/conditioning proportional
        self.mass_kg = mass_kg      # member (G1-R bracket varies it)

    def fe_kw(self, rpm):
        n = np.asarray(rpm, float) / 1800.0
        return self.c_h * n + self.c_e * n ** 2

    def loss_kw(self, rpm, trq_nm, p_elec_kw):
        return (self.fe_kw(rpm) + self.k_cu * (np.asarray(trq_nm) / 100.0) ** 2
                + self.pe0 + self.pe_frac * np.clip(p_elec_kw, 0.0, None))

    def elec_from_shaft(self, rpm, p_shaft_kw):
        """Electrical output [kW] for a given shaft input at rpm."""
        w = np.asarray(rpm, float) * 2 * np.pi / 60
        t = np.asarray(p_shaft_kw, float) * 1e3 / np.maximum(w, 1e-6)
        p_e = np.asarray(p_shaft_kw, float)
        for _ in range(3):
            p_e = np.asarray(p_shaft_kw, float) - self.loss_kw(rpm, t, p_e)
        return np.clip(p_e, 0.0, None)

    def shaft_from_elec(self, rpm, p_elec_kw):
        """Shaft input [kW] needed for a given electrical output at rpm.
        At p_elec=0 the spinning machine still drags fe(N)+pe0."""
        w = np.asarray(rpm, float) * 2 * np.pi / 60
        p_s = np.asarray(p_elec_kw, float) * 1.06
        for _ in range(4):
            t = p_s * 1e3 / np.maximum(w, 1e-6)
            p_s = np.asarray(p_elec_kw, float) + self.loss_kw(rpm, t, p_elec_kw)
        return p_s

    def eta(self, rpm, p_shaft_kw):
        p_e = self.elec_from_shaft(rpm, p_shaft_kw)
        return np.where(np.asarray(p_shaft_kw) > 0.1,
                        p_e / np.maximum(np.asarray(p_shaft_kw, float), 1e-9),
                        0.0)

    def export_map_csv(self, path):
        rpms = np.arange(600, 3001, 100)
        with open(path, "w") as f:
            f.write("# WS4-CONSTRUCTED PM generator efficiency map "
                    "(shaft -> DC bus, incl. active rectifier) - NOT measured\n")
            f.write(f"# generator: {self.name}, cont {self.cont_kw_in} kW "
                    f"shaft in, loss model c_h={self.c_h}, c_e={self.c_e}, "
                    f"k_cu={self.k_cu} kW/(100Nm)^2, pe0={self.pe0} kW "
                    f"+ 1% of P_elec\n")
            f.write("# G1-R/R10 restatement: DC side on the pack-native "
                    "window (662.4 V nominal, 432.0-748.8 V operating, "
                    "777.6 V 10-s transient), 1200 V-class SiC rectifier "
                    "devices; loss coefficients carried unchanged at the "
                    "new window [WS4-DECLARED, confirm at procurement]. "
                    "Per R12 this genset-side rectifier/conditioning stage "
                    "lives in WS4's ledger; no scalar PE member exists on "
                    "the traction side.\n")
            f.write("rpm,p_shaft_kW,eta_shaft_to_bus\n")
            for rpm in rpms:
                w = rpm * 2 * np.pi / 60
                p_top = min(self.peak_kw_in, 8.5 * w / 1e3 * 100)  # 850 Nm cap
                for p in np.linspace(2.0, p_top, 30):
                    f.write(f"{rpm:.0f},{p:.1f},"
                            f"{float(self.eta(rpm, p)):.4f}\n")


GEN_V2 = PMGenerator("GEN-V2 IPM 135", cont_kw_in=135.0, peak_kw_in=155.0,
                     c_h=0.5, c_e=0.7, k_cu=0.0612, mass_kg=90.0)
GEN_V1 = PMGenerator("GEN-V1 IPM 60", cont_kw_in=60.0, peak_kw_in=70.0,
                     c_h=0.3, c_e=0.4, k_cu=0.199, mass_kg=48.0)


# ------------------------------------------- electric traction chain (WS1 R9)
MOTOR_RATED_KW = 150.0     # R3 target rating; part-load fraction basis


def part_load_factor(p_frac, floor_=0.88, knee=0.5):
    """WS1's ratified crude derate (run_ws1.py): full efficiency above
    `knee` of rating, falling linearly to `floor_` x nominal at 5% load.
    Carried unchanged per R9 ('WS1's +17-22% penalty ... stands as the
    reference correction')."""
    x = np.clip(np.asarray(p_frac, float), 0.0, 1.0)
    return np.where(x >= knee, 1.0,
                    floor_ + (1.0 - floor_) * np.clip((x - 0.05) /
                                                      (knee - 0.05), 0, 1))


def chain_bus_to_wheel(p_wheel_kw):
    """Efficiency bus->wheel for the e-machine share, with part-load derate
    on the nominal 0.97*0.92*0.97 chain."""
    k = part_load_factor(np.abs(np.asarray(p_wheel_kw)) / MOTOR_RATED_KW)
    return DL.eta_bus_to_wheel * k


# ------------------------------------------------------ direct (locked) path
def direct_shaft_from_wheel(p_wheel_kw, rpm):
    """Engine shaft power [kW] needed at the clutch for p_wheel through the
    2.8:1 locked path. Loss model [WS4-DECLARED]: 2.8% load-proportional
    mesh/clutch loss + 0.9 kW * (rpm/1800) churning, calibrated to the
    baseline's 0.95 scalar at the 85 km/h cruise point (46.9 kW wheel ->
    eta 0.955... see sanity checks)."""
    spin = 0.9 * np.asarray(rpm, float) / 1800.0
    return (np.asarray(p_wheel_kw, float) + spin) / 0.972


def direct_wheel_from_shaft(p_shaft_kw, rpm):
    spin = 0.9 * np.asarray(rpm, float) / 1800.0
    return np.clip(np.asarray(p_shaft_kw, float) * 0.972 - spin, 0.0, None)


# ----------------------------------------------------------------- batteries
BATT_ETA_CHG = DL.eta_batt_chg
BATT_ETA_DIS = DL.eta_batt_dis
USABLE_V2_KWH = 3.5       # R8 floor at the bus
USABLE_V1_KWH = 1.5       # R8 floor at the bus
CHG_CONT_BUS_KW = 50.0    # R2/R8 continuous charge acceptance for banking


# --------------------------------------------------------- candidate summary
def engine_energy_split(p_shaft_kw, bsfc_g_kwh):
    """Heat-rejection split [WS4-DECLARED, class-typical MD diesel energy
    balance at medium-high load]: of (fuel - shaft), exhaust 49%,
    coolant+oil 38%, charge-air cooler 10%, convection/radiation 3%."""
    p_fuel = bsfc_g_kwh * p_shaft_kw / 3600.0 * LHV_KJ_PER_G  # kW
    q = p_fuel - p_shaft_kw
    return dict(fuel_kW=p_fuel, reject_total_kW=q,
                exhaust_kW=0.49 * q, coolant_oil_kW=0.38 * q,
                cac_kW=0.10 * q, radiation_kW=0.03 * q,
                radiator_package_kW=0.48 * q)
