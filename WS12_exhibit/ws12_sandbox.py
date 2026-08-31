"""WS12 — the sandbox ratio-window model, re-derived from the record.

The draft's ratio window ran on invented constants (`rdyn=0.37+f*0.13`,
`Tpk=700+f*1800`, a `cold` multiplier of `1+max(0,20-T)*0.0022` with no
provenance). This module replaces every one of them.

Road load is the program's own equation:

    F = 0.5 rho CdA v^2  +  Crr m g cos(theta)  +  m g sin(theta)
    theta = atan(grade)                       g = 9.81 m/s^2

`g = 9.81` is the program constant (`WS1_loads_duty_cycles/volt_params.py`
line 10 and `WS8_semi_architecture/ws8_params.py` line 24, identical).

The window is bounded by two closed forms:

    ratio_max  = rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)
    ratio_min  = F_grade_hold * r_dyn / (T_peak * eta_driveline)

`ratio_max` is WS8's own published physics bound, quoted verbatim from
`results_ws8.json` -> `interface_ws8` -> `S3_fixed_ratio_feasibility` ->
`ratio_ceiling_closed_form` -> `rule`. `ratio_min` is the inverse of the
same statement: the ratio at which peak torque, through the driveline,
just balances the grade force.

Every endpoint constant is a value on disk. `test_sandbox_ws12.py`
re-derives four exported force ledgers and three exported ratios from
the functions below and asserts they reproduce, which is what makes the
S3 feasibility result come out of the same function the visitor's
sliders drive.

The screen stays badged SANDBOX throughout. Between the two endpoints
the parameters are interpolated linearly in mass; that interpolation is
a declared sandbox construction and is NOT a result.
"""

import math

G = 9.81  # WS1 volt_params.py:10 == WS8 ws8_params.py:24

# ------------------------------------------------------------- endpoints
# Vehicle Zero: WS1's ratified road-load set. Vehicle One: WS8's.
# Every field carries the file and path it came from; build_exhibit_data.py
# cites them on screen.

VEHICLE_ZERO = {
    "label": "Vehicle Zero — Isuzu NPR-HD class",
    "m_kg": ("WS1_loads_duty_cycles/results.json",
             ["params", "vehicle", "m_gvw"]),
    "CdA_m2": ("WS1_loads_duty_cycles/results.json",
               ["params", "vehicle", "CdA"]),
    "Crr": ("WS1_loads_duty_cycles/results.json",
            ["params", "vehicle", "Crr"]),
    "rho_air": ("WS1_loads_duty_cycles/results.json",
                ["params", "vehicle", "rho_air"]),
    "r_dyn_m": ("WS1_loads_duty_cycles/results.json",
                ["params", "vehicle", "r_dyn"]),
    "v_cruise_kmh": ("WS1_loads_duty_cycles/results.json",
                     ["cycles", "VOLT-REG", "max_speed_kmh"]),
    "eta_driveline": ("WS1_loads_duty_cycles/results.json",
                      ["params", "driveline", "eta_direct"]),
    # T_peak and rpm_ceiling come from WS1's own engine curve arrays.
    "T_peak_Nm_from": ("WS1_loads_duty_cycles/results.json",
                       ["params", "engine", "trq_pts"]),
    "rpm_ceiling_from": ("WS1_loads_duty_cycles/results.json",
                         ["params", "engine", "rpm_pts"]),
    "v_climb_kmh": 60.0,   # the speed WS1's own 6% cross-check is stated at
}

VEHICLE_ONE = {
    "label": "Vehicle One — Class 8 tractor-semitrailer",
    "m_kg": ("WS8_semi_architecture/results_ws8.json",
             ["params", "vehicle", "m_gcw"]),
    "CdA_m2": ("WS8_semi_architecture/results_ws8.json",
               ["params", "vehicle", "CdA"]),
    "Crr": ("WS8_semi_architecture/results_ws8.json",
            ["params", "vehicle", "Crr"]),
    "rho_air": ("WS8_semi_architecture/results_ws8.json",
                ["params", "vehicle", "rho_air"]),
    "r_dyn_m": ("WS8_semi_architecture/results_ws8.json",
                ["params", "vehicle", "r_dyn"]),
    "v_cruise_kmh": ("WS8_semi_architecture/results_ws8.json",
                     ["params", "cycle", "linehaul_v_hi_kmh"]),
    "T_peak_Nm": ("WS8_semi_architecture/results_ws8.json",
                  ["task2_s0_calibration", "engine", "peak_torque_Nm"]),
    "rpm_ceiling": ("WS8_semi_architecture/results_ws8.json",
                    ["interface_ws8", "S3_fixed_ratio_feasibility",
                     "ratio_ceiling_closed_form", "rpm_ceiling"]),
    "v_climb_kmh": ("WS9_vehicle_one_wave2/results_ws9.json",
                    ["two_walls", "two_speed_solve", "ENG-13L", "solve",
                     "force_required", "v_ref_kmh"]),
}

# The Vehicle One driveline chain, as three exported members whose
# product is the efficiency WS9's own closed form uses.
VEHICLE_ONE_ETA_MEMBERS = (
    ("WS8_semi_architecture/results_ws8.json",
     ["params", "driveline", "eta_amt_indirect"]),
    ("WS8_semi_architecture/results_ws8.json",
     ["params", "driveline", "eta_axle_tandem"]),
    ("WS8_semi_architecture/results_ws8.json",
     ["params", "driveline", "eta_driveshaft"]),
)


# ------------------------------------------------------------- the model

def road_load_N(m_kg, CdA_m2, Crr, rho_air, v_ms, grade):
    """The program's road-load equation. Returns the four terms."""
    theta = math.atan(grade)
    aero = 0.5 * rho_air * CdA_m2 * v_ms * v_ms
    roll = Crr * m_kg * G * math.cos(theta)
    grd = m_kg * G * math.sin(theta)
    return {"aero_N": aero, "roll_N": roll, "grade_N": grd,
            "total_N": aero + roll + grd}


def ratio_ceiling(rpm_ceiling, r_dyn_m, v_cruise_ms):
    """WS8's published physics bound, in its own words:
    'ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)'."""
    return rpm_ceiling * 2.0 * math.pi * r_dyn_m / (60.0 * v_cruise_ms)


def ratio_required(F_N, r_dyn_m, T_peak_Nm, eta_driveline):
    """The ratio at which peak torque, through the driveline, balances
    the road load. The inverse statement of the ceiling."""
    return F_N * r_dyn_m / (T_peak_Nm * eta_driveline)


def lerp(a, b, f):
    return a + (b - a) * f


def ratio_window(mass_kg, grade, rho_air, ends):
    """The sandbox window at one slider position.

    `ends` is the resolved endpoint dict (floats, not path tuples).
    Parameters are interpolated linearly in mass between the two
    vehicles of record. That interpolation is a SANDBOX construction.
    """
    lo, hi = ends["zero"], ends["one"]
    f = (mass_kg - lo["m_kg"]) / (hi["m_kg"] - lo["m_kg"])
    f = max(0.0, min(1.0, f))
    p = {k: lerp(lo[k], hi[k], f) for k in
         ("CdA_m2", "Crr", "r_dyn_m", "v_cruise_kmh", "eta_driveline",
          "T_peak_Nm", "rpm_ceiling", "v_climb_kmh")}
    F = road_load_N(mass_kg, p["CdA_m2"], p["Crr"], rho_air,
                    p["v_climb_kmh"] / 3.6, grade)
    r_max = ratio_ceiling(p["rpm_ceiling"], p["r_dyn_m"],
                          p["v_cruise_kmh"] / 3.6)
    r_min = ratio_required(F["total_N"], p["r_dyn_m"], p["T_peak_Nm"],
                           p["eta_driveline"])
    return {"rMin": r_min, "rMax": r_max, "force": F, "params": p,
            "open": r_min <= r_max}


def resolve_endpoints(load_json):
    """Turn the (file, path) endpoint spec into floats. `load_json` is a
    callable taking a repo-relative path and returning the parsed doc."""
    def get(spec):
        f, p = spec
        doc = load_json(f)
        cur = doc
        for k in p:
            cur = cur[k]
        return cur

    zero = {
        "m_kg": get(VEHICLE_ZERO["m_kg"]),
        "CdA_m2": get(VEHICLE_ZERO["CdA_m2"]),
        "Crr": get(VEHICLE_ZERO["Crr"]),
        "rho_air": get(VEHICLE_ZERO["rho_air"]),
        "r_dyn_m": get(VEHICLE_ZERO["r_dyn_m"]),
        "v_cruise_kmh": get(VEHICLE_ZERO["v_cruise_kmh"]),
        "eta_driveline": get(VEHICLE_ZERO["eta_driveline"]),
        "T_peak_Nm": float(max(get(VEHICLE_ZERO["T_peak_Nm_from"]))),
        "rpm_ceiling": float(max(get(VEHICLE_ZERO["rpm_ceiling_from"]))),
        "v_climb_kmh": VEHICLE_ZERO["v_climb_kmh"],
    }
    eta_one = 1.0
    for spec in VEHICLE_ONE_ETA_MEMBERS:
        eta_one *= get(spec)
    one = {
        "m_kg": get(VEHICLE_ONE["m_kg"]),
        "CdA_m2": get(VEHICLE_ONE["CdA_m2"]),
        "Crr": get(VEHICLE_ONE["Crr"]),
        "rho_air": get(VEHICLE_ONE["rho_air"]),
        "r_dyn_m": get(VEHICLE_ONE["r_dyn_m"]),
        "v_cruise_kmh": get(VEHICLE_ONE["v_cruise_kmh"]),
        "eta_driveline": eta_one,
        "T_peak_Nm": get(VEHICLE_ONE["T_peak_Nm"]),
        "rpm_ceiling": get(VEHICLE_ONE["rpm_ceiling"]),
        "v_climb_kmh": get(VEHICLE_ONE["v_climb_kmh"]),
    }
    return {"zero": zero, "one": one}


def crossing_mass(grade, rho_air, ends, iters=60):
    """The mass at which the window closes (rMin crosses rMax)."""
    lo, hi = ends["zero"]["m_kg"], ends["one"]["m_kg"]
    if ratio_window(hi, grade, rho_air, ends)["open"]:
        return None
    if not ratio_window(lo, grade, rho_air, ends)["open"]:
        return lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if ratio_window(mid, grade, rho_air, ends)["open"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
