"""Traction-control envelope (task 5, E23): torque limits vs axle load.

Single driven rear axle. Quasi-static load transfer:
  launch/drive:  N_r = m g (cos(th) s_r) + m g sin(th) h/L + m a h/L
  braking:       N_r = m g (cos(th) s_r) - m |a| h/L   (a = decel from F)
Self-consistent adhesion-limited force (all traction/braking from the
driven axle; aero/rolling ignored -> conservative for braking, slightly
optimistic for drive):
  drive:  F = mu (m g cos s_r + m g sin h/L) / (1 - mu h/L)
  brake:  F = mu  m g cos s_r                / (1 + mu h/L)
"""

import math

from ws2_params import VEH, TRACTION, RATIO_NOM


def _mass_case(name):
    if name == "gvw":
        return VEH["m_gvw"], VEH["rear_share_gvw"], VEH["h_cg_loaded"]
    return VEH["m_curb"], VEH["rear_share_curb"], VEH["h_cg_empty"]


def drive_force_limit(mass_case, mu, grade=0.0):
    m, s_r, h = _mass_case(mass_case)
    L, g = VEH["wheelbase"], VEH["g"]
    th = math.atan(grade)
    num = mu * (m * g * math.cos(th) * s_r + m * g * math.sin(th) * h / L)
    den = 1.0 - mu * h / L
    if den <= 0.05:
        return float("inf")
    return num / den


def brake_force_limit(mass_case, mu, grade=0.0):
    m, s_r, h = _mass_case(mass_case)
    L, g = VEH["wheelbase"], VEH["g"]
    th = math.atan(grade)
    return mu * m * g * math.cos(th) * s_r / (1.0 + mu * h / L)


def wheel_torque(F):
    return F * VEH["r_dyn"]


def motor_torque_drive(F, ratio=RATIO_NOM):
    return wheel_torque(F) / (ratio * VEH["eta_red"])


def motor_torque_brake(F, ratio=RATIO_NOM):
    return wheel_torque(F) * VEH["eta_red"] / ratio


def envelope():
    rows = []
    for mass_case in ("gvw", "curb"):
        m, s_r, h = _mass_case(mass_case)
        for mu in TRACTION["mu_cases"]:
            Fd = drive_force_limit(mass_case, mu)
            Fd20 = drive_force_limit(mass_case, mu, grade=0.20)
            Fb = brake_force_limit(mass_case, mu)
            rows.append(dict(
                mass_case=mass_case, m_kg=m, mu=mu,
                F_drive_flat_N=Fd, F_drive_20pct_N=Fd20, F_brake_N=Fb,
                T_wheel_drive_Nm=wheel_torque(Fd),
                T_wheel_brake_Nm=wheel_torque(Fb),
                T_motor_drive_Nm=motor_torque_drive(Fd),
                T_motor_brake_Nm=motor_torque_brake(Fb),
                launch_spec_ok_flat=Fd >= VEH["F_trac_max"],
                launch_spec_ok_20pct=Fd20 >= VEH["F_trac_max"],
            ))
    return rows


def mu_required():
    """Reproduce/extend WS1 section 4.16 mu-required numbers."""
    out = {}
    for mass_case in ("gvw", "curb"):
        m, s_r, h = _mass_case(mass_case)
        L, g = VEH["wheelbase"], VEH["g"]
        # mu needed to deliver the 13.5 kN launch spec on flat
        F = VEH["F_trac_max"]
        # F = mu (m g s_r)/(1-mu h/L)  ->  mu = F/(m g s_r + F h/L)
        out[f"mu_launch_flat_{mass_case}"] = F / (m * g * s_r + F * h / L)
        out[f"mu_launch_20pct_{mass_case}"] = None  # filled below
        th = math.atan(0.20)
        out[f"mu_launch_20pct_{mass_case}"] = F / (
            m * g * math.cos(th) * s_r + m * g * math.sin(th) * h / L
            + F * h / L)
    return out


def regen_power_curve(mass_case, mu, v_grid_kmh=None, cap_wheel_W=75e3):
    """Adhesion-limited regen power at the wheel vs speed, with the 75 kW cap."""
    if v_grid_kmh is None:
        v_grid_kmh = TRACTION["v_grid_kmh"]
    F = brake_force_limit(mass_case, mu)
    rows = []
    for v in v_grid_kmh:
        P_adh = F * v / 3.6
        rows.append(dict(v_kmh=v, P_adhesion_kW=P_adh / 1e3,
                         P_usable_kW=min(P_adh, cap_wheel_W) / 1e3,
                         binding="adhesion" if P_adh < cap_wheel_W else "75kW cap"))
    return rows
