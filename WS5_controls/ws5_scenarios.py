"""
Project Volt - WS5
Deterministic scenarios beyond the two WS1 duty cycles: the R2/R17 descent
case of record, the R22d coast case, and the E23 traction-control cases.

Every scenario is built at 10 Hz (R9) from declared geometry - no seeds, no
stochastic content - so they are ensemble-free by construction and the
8-seed convention does not apply to them (it applies to the WS1 cycles,
which carry the stochastic driver model).
"""
import numpy as np

import ws5_inputs as I

DT = 0.1


def _ramped_constant(v_kmh, dist_m, grade, ramp_s=20.0):
    """Constant-speed leg over a fixed distance on a constant grade, with a
    raised-cosine speed ramp so the first seconds are physical."""
    v = v_kmh / 3.6
    dur = dist_m / v + ramp_s
    n = int(round(dur / DT)) + 1
    t = np.arange(n) * DT
    vv = np.full(n, v)
    r = t < ramp_s
    vv[r] = v * 0.5 * (1 - np.cos(np.pi * t[r] / ramp_s))
    return dict(name=f"DESCENT-{v_kmh:g}kmh", t=t, v=vv,
                grade=np.full(n, grade))


# ------------------------------------------------------- R2 / R17 descent
# WS3's descent case of record: a 10 km sustained 6% descent (their
# rows_45C / rows_minus10C tables are this case at these speeds). WS5
# re-runs it under the R15 blend order, with the resistor healthy and lost.
DESCENT_DIST_M = 10000.0
DESCENT_GRADE = -0.06
DESCENT_SPEEDS_KMH = [25.0, 40.0, 55.0, 70.0, 85.0]
PAYLOAD120_MASS_KG = 7180.0        # WS3 descent_resistor_bound payload120


def descent(v_kmh, grade=DESCENT_GRADE, dist_m=DESCENT_DIST_M):
    return _ramped_constant(v_kmh, dist_m, grade)


# ------------------------------------------------------------ R22d coast
# The condition R22d is about: the driver lifts off at road speed and the
# permanently-geared PM machine turns at zero torque. Grade chosen so the
# net wheel demand is ~0 at the stated speed and GVW, i.e. a genuine
# sustained TRUE COAST rather than a braking event.
COAST_SPEED_KMH = 85.0
COAST_DURATION_S = 600.0


def coast_neutral_grade(v_kmh=COAST_SPEED_KMH, m=None, veh=None):
    """The (negative) grade at which road load is exactly balanced at
    constant speed - the true-coast condition."""
    veh = I.VEH if veh is None else veh
    m = veh.m_gvw if m is None else m
    v = v_kmh / 3.6
    f_aero = 0.5 * veh.rho_air * veh.CdA * v ** 2
    f_roll = veh.Crr * m * I.G
    # m g sin(theta) = -(f_aero + f_roll)
    s = -(f_aero + f_roll) / (m * I.G)
    theta = np.arcsin(np.clip(s, -1.0, 1.0))
    return float(np.tan(theta))


def coast(v_kmh=COAST_SPEED_KMH, duration_s=COAST_DURATION_S, m=None,
          veh=None):
    g = coast_neutral_grade(v_kmh, m, veh)
    n = int(round(duration_s / DT)) + 1
    t = np.arange(n) * DT
    v = np.full(n, v_kmh / 3.6)
    return dict(name=f"COAST-{v_kmh:g}kmh", t=t, v=v,
                grade=np.full(n, g), neutral_grade=g)


# --------------------------------------------------------------- E23 cases
E23_CASES = {
    "launch_13.5kN_curb": dict(
        m_kg=I.VEH.m_curb_operating, grade=0.0, braking=False,
        F_N=I.VEH.F_trac_max,
        note=("E23 as ruled: '13.5 kN launch ~mu 0.66'. Reproduces WS2 "
              "traction.mu_required.mu_launch_flat_curb exactly.")),
    "launch_13.5kN_gvw": dict(
        m_kg=I.VEH.m_gvw, grade=0.0, braking=False, F_N=I.VEH.F_trac_max,
        note="Reproduces WS2 traction.mu_required.mu_launch_flat_gvw."),
}

# The regen half of E23 is a CYCLE-DERIVED quantity, not a textbook stop:
# WS1 s4.16 defines it as the PEAK REGEN FORCE AT THE WHEEL with the 75 kW
# absorb cap applied, at the operating curb mass, over the duty cycle. WS5
# reproduces that method (and turns its extremum into an 8-seed envelope,
# which R9 requires and WS1's single-number table did not carry).
E23_REGEN_CASES = {
    "empty_truck_regen_stop": dict(
        cycle="VOLT-SUB", m_kg=I.VEH.m_curb_operating, grade_override=None,
        note=("E23 as ruled: 'empty-truck regen ~mu 0.36 per stop'. WS1 "
              "s4.16's method: peak regen force at the wheel with the 75 kW "
              "cap applied, operating curb mass, single driven axle, "
              "braking load transfer OFF the driven axle.")),
    "empty_truck_regen_stop_volt_reg": dict(
        cycle="VOLT-REG", m_kg=I.VEH.m_curb_operating, grade_override=None,
        note="Same method on the regional cycle."),
    "empty_truck_regen_stop_6pct_descent": dict(
        cycle="VOLT-SUB", m_kg=I.VEH.m_curb_operating, grade_override=-0.06,
        note=("The aggravated case WS5 adds, which E23 does not name: the "
              "same peak regen force demanded on a 6% descent, where the "
              "pitch transfer unloads the single driven axle further - so "
              "the electric retarder's adhesion ceiling falls exactly "
              "where retardation is wanted.")),
    "gvw_regen_stop": dict(
        cycle="VOLT-SUB", m_kg=I.VEH.m_gvw, grade_override=None,
        note="WS1 s4.16's GVW column, for the comparison."),
}
