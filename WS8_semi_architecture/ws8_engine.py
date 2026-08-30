"""
Project Volt - WS8
Diesel engines and the AMT, at semi scale (assignment Task 2).

PROVENANCE. The BSFC construction is NOT re-invented here. WS8 imports
WS4's ruled `WillansEngine` and `derate_factor` READ-ONLY (CLAUDE.md
rule 10 - the same posture WS4 itself takes towards WS1's volt_params)
and re-calibrates the coefficients for a 13 L-class heavy-duty engine.
That way Vehicle One's fuel arithmetic is the same object as Vehicle
Zero's, and any future amendment to the Willans construction propagates
to both.

The engines:
  ENG_13L   S0 / S2 / S3-large: modern 12.8 L six, ~350 kW, 2,373 Nm
  ENG_11L   S3 downsized "cruise-plus-margin" engine, 10.8 L, ~265 kW
  ENG_GEN   S1 series genset prime mover, 12.8 L held at a fixed point
  ENG_SUST  S4 sustainer, 5.1 L class, ~170 kW

CALIBRATION (assignment Task 2: "Willans/published-BSFC class engine
map ... Calibrate fleet fuel to a public reference band and state it").
Two levels, both explicit:
  (1) eta_i0 is SOLVED, not guessed, so that each engine's map minimum
      lands exactly on a declared best-point BSFC. The declared value is
      the calibration input and is stated in the report.
  (2) the resulting FLEET fuel from the full cycle simulation is then
      compared against the assignment's 30-38 L/100 km sanity corridor.
      No fudge factor sits between (1) and (2): whatever the physics
      gives is what gets reported.
"""
import os
import sys

import numpy as np

_WS4_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "WS4_genset")
if _WS4_DIR not in sys.path:
    sys.path.insert(0, _WS4_DIR)

from ws4_models import WillansEngine, derate_factor  # noqa: E402  (read-only)


class HDWillansEngine(WillansEngine):
    """WS4's Willans construction with the speed term RE-ANCHORED for the
    heavy-duty class.

    WS4's f_N is `1 - 0.06*((rpm - 1600)/1400)^2`: an optimum at
    1,600 rpm with a 6% penalty 1,400 rpm away. That is right for the
    700-3,000 rpm medium-duty engine WS4 calibrated and WRONG for a
    600-2,100 rpm Class 8 six, which is deliberately built to be at its
    best around 1,200-1,300 rpm and which loses efficiency fast above
    1,800. Carrying WS4's centre unchanged would flatter exactly the
    candidate this trial most needs to test honestly - S3, whose fixed
    ratio forces the engine to whatever speed the road dictates.

    HD form: `1 - 0.08*((rpm - 1250)/1000)^2`
      1,250 rpm 1.000   1,800 rpm 0.976   2,100 rpm 0.942   800 rpm 0.984
    [WS8-PROV] class-typical; the SHAPE is what matters here, and eta_i0
    is re-solved against it so the island BSFC target is unmoved.
    """

    @staticmethod
    def _f_n(rpm):
        return 1.0 - 0.08 * ((np.asarray(rpm, float) - 1250.0) / 1000.0) ** 2


# R18 FLAT-RATING RATIO, carried from Vehicle Zero's ruled record: WS4's
# R18 rates 132 kW continuous from a 153.3 kW automotive peak, a ratio of
# 0.861. A genset prime mover is not run at its automotive peak rating;
# the same discount is applied here to the 13 L's peak so the series
# candidates are given a continuous rating they could actually hold.
R18_FLAT_RATING_RATIO = 132.0 / 153.3

from ws8_params import DL, LHV_KJ_PER_G, DIESEL_DENSITY_KG_PER_L  # noqa: E402


# --------------------------------------------------------- torque curves
# [WS8-PROV] class-typical published full-load curves for modern on-highway
# heavy-duty diesels. A 13 L at ~350 kW / 2,373 Nm is the volume seller in
# US line-haul (450 hp / 1,750 lb-ft class); the flat torque plateau from
# 1,000 to 1,400 rpm and the flat power shelf from 1,400 to 1,800 rpm are
# the defining features of the modern "downsped" calibration, and they are
# the reason a direct-drive top gear and a fast rear axle work at all.
RPM_13L = (600, 800, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
           1800, 1900, 2000, 2100)
TRQ_13L = (900, 1700, 2237, 2373, 2373, 2373, 2373, 2237, 2100, 1970,
           1855, 1700, 1550, 1400)

RPM_11L = (600, 800, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
           1800, 1900, 2000, 2100)
TRQ_11L = (700, 1310, 1720, 1800, 1800, 1800, 1800, 1700, 1600, 1500,
           1410, 1300, 1190, 1080)

RPM_5L = (700, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600,
          2800, 3000)
TRQ_5L = (420, 660, 780, 830, 840, 830, 800, 760, 700, 630, 560, 490)

# 7 L-class medium-heavy six, used as S4's SUSTAINER prime mover. The
# assignment specifies a "~150-200 kW" sustainer; the 5 L class flat-rates
# (R18) to only 151 kW, the very bottom of that band, so the trial would be
# testing an under-sized sustainer rather than the architecture. The 7 L
# flat-rates to ~200 kW - the TOP of the specified band - and S4 is given
# that, so a poor S4 result cannot be blamed on picking the weak end of
# the range. [WS8-PROV]
RPM_7L = (600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400)
TRQ_7L = (620, 980, 1230, 1300, 1300, 1270, 1180, 1075, 960, 840)

# Chen-Flynn FMEP coefficients [bar]: a0 + a1*(N/1000) + a2*(N/1000)^2.
# [WS8-PROV] Heavy-duty engines run lower mean piston speeds and larger
# bearings than the 5 L class WS4 calibrated, so the speed-dependent
# terms are smaller; the absolute level (~1.05 bar at 1,200 rpm, ~1.29
# bar at 1,800 rpm) is class-typical for a warm 13 L including pumping.
FMEP_HD = (0.70, 0.22, 0.060)
FMEP_MD = (0.75, 0.28, 0.075)      # WS4's own value, kept for the 5 L class

# Declared best-point BSFC targets [g/kWh]. These are the CALIBRATION
# INPUTS. [WS8-PROV] modern production on-highway HD diesels sit in the
# 182-190 g/kWh island (about 45-46% peak brake thermal efficiency);
# SuperTruck demonstrators go lower but are not production and are not
# used here. The medium-duty sustainer is a smaller, less efficient
# class.
BSFC_ISLAND_TARGET = {
    "ENG-13L": 185.0,
    "ENG-11L": 187.0,
    "ENG-5L": 205.0,
    "ENG-7L": 196.0,
}


def _solve_eta_i0(name, disp_l, rpm_pts, trq_pts, fmep_a, target_bsfc,
                  tol=1e-10):
    """Solve eta_i0 so the map's MINIMUM BSFC equals `target_bsfc`.

    eta_b is linear in eta_i0 and BSFC = 84.112/eta_b, so BSFC scales as
    1/eta_i0 and the solve is a single division - but it is done by
    bisection anyway, against the actual map minimum, so that the
    calibration is verified against the same grid the simulation uses
    rather than against an algebraic shortcut."""
    def island(eta):
        e = HDWillansEngine(name, disp_l, rpm_pts, trq_pts, eta,
                            fmep_a=fmep_a)
        return e.min_bsfc_point()["bsfc"]

    lo, hi = 0.20, 0.90
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if island(mid) > target_bsfc:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def build_engine(name, disp_l, rpm_pts, trq_pts, fmep_a, target_bsfc,
                 mass_kg, label):
    eta_i0 = _solve_eta_i0(name, disp_l, rpm_pts, trq_pts, fmep_a,
                           target_bsfc)
    return HDWillansEngine(name, disp_l, rpm_pts, trq_pts, eta_i0,
                           fmep_a=fmep_a, idle_rpm=600.0,
                           rated_cont_rpm=1800.0, mass_kg=mass_kg,
                           label=label)


ENG_13L = build_engine("ENG-13L-W", 12.8, RPM_13L, TRQ_13L, FMEP_HD,
                       BSFC_ISLAND_TARGET["ENG-13L"], 1215.0,
                       "WS8-CONSTRUCTED Willans, 13 L class")
ENG_11L = build_engine("ENG-11L-W", 10.8, RPM_11L, TRQ_11L, FMEP_HD,
                       BSFC_ISLAND_TARGET["ENG-11L"], 1035.0,
                       "WS8-CONSTRUCTED Willans, 11 L class (S3 downsized)")
ENG_5L = build_engine("ENG-5L-W", 5.1, RPM_5L, TRQ_5L, FMEP_MD,
                      BSFC_ISLAND_TARGET["ENG-5L"], 470.0,
                      "WS8-CONSTRUCTED Willans, 5 L class (S4 sustainer)")

ENG_7L = build_engine("ENG-7L-W", 7.0, RPM_7L, TRQ_7L, FMEP_HD,
                      BSFC_ISLAND_TARGET["ENG-7L"], 640.0,
                      "WS8-CONSTRUCTED Willans, 7 L class (S4 sustainer)")

ENGINES = {"ENG-13L": ENG_13L, "ENG-11L": ENG_11L, "ENG-5L": ENG_5L,
           "ENG-7L": ENG_7L}


# ------------------------------------------------------------ idle fuel
def idle_fuel_gps(engine, rpm=None):
    """Fuel rate at idle [g/s].

    At zero brake torque BSFC is infinite, so idle fuel cannot come from
    the BSFC map - it is the FMEP work the engine does on itself. That
    work is computed from the same Chen-Flynn friction line the map uses,
    burned at the indicated efficiency, so idle is not a separate
    assumption bolted on the side."""
    rpm = engine.idle_rpm if rpm is None else rpm
    fmep_bar = float(engine.fmep_bar(rpm))
    # P_friction = FMEP * V_d * N/2  (four-stroke)
    p_fric_w = fmep_bar * 1e5 * engine.disp_m3 * (rpm / 60.0) / 2.0
    eta_ind = engine.eta_i0 * float(engine._f_n(rpm)) * 0.86
    return p_fric_w / 1e3 / eta_ind / LHV_KJ_PER_G


# ---------------------------------------------------------------- the AMT
class AMT:
    """12-speed automated manual with a DIRECT top gear.

    Ratios are a classic direct-drive 12-speed (top = 1.000, no
    countershaft power path in top). The rear-axle ratio is the modern
    "downsped" spec: 2.47:1 puts the engine at ~1,310 rpm at 100 km/h on
    a 0.50 m dynamic radius, right on the torque plateau, which is
    precisely the operating point the flat-torque calibration exists to
    exploit. [WS8-PROV]

    Efficiency is gear-dependent, not a scalar: direct top has no
    countershaft, indirect gears do. This matters, because it is the
    honest size of the prize a gearbox-deleting candidate can claim.
    """
    RATIOS = (14.94, 11.73, 9.04, 7.09, 5.54, 4.35,
              3.44, 2.70, 2.08, 1.63, 1.27, 1.00)
    AXLE = 2.47
    # compression-brake rating point and over-speed ceiling [WS8-PROV]
    RPM_BRAKE_RATED = 2100.0
    RPM_BRAKE_MAX = 2200.0

    def __init__(self, engine, r_dyn=0.50, rpm_lo=1050.0, rpm_hi=1750.0,
                 rpm_shift_up=1500.0, rpm_shift_dn=1150.0,
                 launch_rpm=1200.0):
        self.engine = engine
        self.r_dyn = r_dyn
        self.rpm_lo = rpm_lo
        self.rpm_hi = rpm_hi
        self.rpm_shift_up = rpm_shift_up
        self.rpm_shift_dn = rpm_shift_dn
        # Below the road speed at which first gear reaches idle, a truck
        # LAUNCHES ON A SLIPPING CLUTCH: the engine holds `launch_rpm`
        # while the output turns slower. The torque still gets through
        # (that is the whole point of a friction clutch), but the engine
        # burns fuel at engine speed while the wheel only receives wheel
        # speed - the difference is clutch heat, and it is charged to the
        # candidate in ws8_candidates.py rather than quietly dropped.
        self.launch_rpm = launch_rpm

    def slipping(self, v):
        """True when first gear cannot reach idle at this road speed."""
        return self.rpm_at(v, 0) < self.engine.idle_rpm

    def engine_rpm(self, v, gear_idx):
        """Engine speed [rpm], accounting for clutch slip at launch."""
        rpm = self.rpm_at(v, gear_idx)
        if gear_idx == 0 and rpm < self.launch_rpm and self.slipping(v):
            return self.launch_rpm
        return max(rpm, self.engine.idle_rpm) if rpm < self.engine.idle_rpm \
            else rpm

    def overall(self, gear_idx):
        return self.RATIOS[gear_idx] * self.AXLE

    def eta(self, gear_idx):
        return (DL.eta_amt_direct if self.RATIOS[gear_idx] == 1.0
                else DL.eta_amt_indirect) * DL.eta_axle_tandem \
            * DL.eta_driveshaft

    def rpm_at(self, v, gear_idx):
        return v / self.r_dyn * self.overall(gear_idx) * 60.0 / (2 * np.pi)

    def wheel_force_available(self, v, gear_idx):
        """Tractive force at the contact patch in this gear [N]."""
        rpm = self.rpm_at(v, gear_idx)
        if rpm > 2100.0:
            return 0.0
        if rpm < self.engine.idle_rpm:
            # only first gear may launch on a slipping clutch; the rest
            # of the box has nothing to offer below its idle speed.
            if gear_idx != 0:
                return 0.0
            rpm = self.launch_rpm
        t_eng = float(self.engine.t_max(rpm))
        return t_eng * self.overall(gear_idx) * self.eta(gear_idx) / self.r_dyn

    def select_gear(self, v, f_demand_N):
        """Pick the gear an AMT would actually be in.

        Rule: the HIGHEST gear (lowest engine speed) whose engine speed is
        above `rpm_lo` and which can deliver the demanded wheel force with
        the full-load curve. If none can, take the gear giving the most
        force. This is a torque-and-speed rule, not a lookup table, so it
        stays honest on grades.
        """
        best_idx, best_force = 0, -1.0
        for i in range(len(self.RATIOS) - 1, -1, -1):
            rpm = self.rpm_at(v, i)
            if rpm > 2100.0 or rpm < self.engine.idle_rpm:
                f = self.wheel_force_available(v, i)
                if f > best_force:
                    best_force, best_idx = f, i
                continue
            f = self.wheel_force_available(v, i)
            if f > best_force:
                best_force, best_idx = f, i
            if rpm >= self.rpm_lo and f >= f_demand_N:
                return i, f
        return best_idx, max(best_force, 0.0)

    def max_wheel_force(self, v):
        """Best tractive force any gear can give at this speed [N]."""
        return max(self.wheel_force_available(v, i)
                   for i in range(len(self.RATIOS)))

    def engine_brake_force(self, v, p_engine_brake_kw=290.0):
        """Compression-brake retarding force at the contact patch [N].

        A modern 13 L compression brake is rated at its HIGH-SPEED point
        (~2,100 rpm) and its retarding power falls roughly in proportion
        to engine speed. On a descent the AMT does not sit in top gear -
        it DOWNSHIFTS to spin the engine up, which is the whole technique.
        So the available brake is evaluated at the gear that puts the
        engine as close as possible to the brake's rated speed without
        over-speeding it, exactly as a real AMT descent mode does.

        This is why the retarding capability is strong at 50 km/h and
        weak at 90 km/h: at 90 km/h even a downshift cannot spin the
        engine much past 2,100 rpm without over-revving, so the brake
        runs out of grade before it runs out of speed.
        """
        if v < 1.0:
            return 0.0
        best_rpm = 0.0
        for i in range(len(self.RATIOS)):
            rpm = self.rpm_at(v, i)
            if rpm <= self.RPM_BRAKE_MAX and rpm > best_rpm:
                best_rpm = rpm
        if best_rpm < self.engine.idle_rpm:
            return 0.0
        p = p_engine_brake_kw * (best_rpm / self.RPM_BRAKE_RATED)
        return p * 1e3 / v

    def engine_brake_rpm(self, v):
        """The engine speed the AMT would hold for descent braking."""
        best_rpm = 0.0
        for i in range(len(self.RATIOS)):
            rpm = self.rpm_at(v, i)
            if rpm <= self.RPM_BRAKE_MAX and rpm > best_rpm:
                best_rpm = rpm
        return best_rpm


def fuel_L_per_100km(fuel_g, distance_m):
    if distance_m <= 0:
        return float("nan")
    return (fuel_g / DIESEL_DENSITY_KG_PER_L / 1000.0) / (distance_m / 1e5)


def fuel_energy_MJ(fuel_g):
    return fuel_g * LHV_KJ_PER_G / 1000.0


def flat_rated_cont_kw(engine):
    """Continuous genset rating from an automotive peak, per R18."""
    return engine.peak_power_kw() * R18_FLAT_RATING_RATIO


__all__ = ["ENG_13L", "ENG_11L", "ENG_5L", "ENG_7L", "ENGINES", "AMT", "idle_fuel_gps",
           "fuel_L_per_100km", "fuel_energy_MJ", "derate_factor",
           "BSFC_ISLAND_TARGET", "HDWillansEngine", "flat_rated_cont_kw",
           "R18_FLAT_RATING_RATIO"]
