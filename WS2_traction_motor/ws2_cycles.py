"""Run WS1's published 10 Hz reference traces through the WS2 loss model.

Purpose (R9 / E22): replace the peak-point scalar chain 0.97x0.92 with
map-based part-load losses, and quantify the lockup spin drag for G1.

Conventions:
* Motoring shaft torque = wheel torque / (ratio * eta_red)   (WS1 s.1.3)
* Generating shaft torque uses the CAPTURED regen power column (cap and
  blend-out already applied by WS1), wheel->shaft with eta_red gain.
* V2 lockup: v >= 65 km/h and P_wheel > 0 -> machine spins at zero
  torque; iron+windage drag is charged to the ENGINE shaft (G1 input),
  flux-weakening copper + inverter standby to the bus.
* Standstill: inverter standby only.
"""

import csv
import math

from ws2_params import VEH, MACH, INV
import ws2_machine as mc


def read_trace(path, decimate=1):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            if i % decimate:
                continue
            rows.append((float(row["t_s"]), float(row["v_kmh"]),
                         float(row["P_wheel_kW"]) * 1e3,
                         float(row["P_regen_capt_kW"]) * 1e3))
    return rows


def _spin_table(ratio, v_dc, rpm_lo=50.0, rpm_hi=7500.0, n=31):
    pts = []
    for k in range(n):
        rpm = rpm_lo + (rpm_hi - rpm_lo) * k / (n - 1)
        s = mc.spin_loss(rpm * 2 * math.pi / 60.0, v_dc)
        pts.append((rpm, s["shaft_drag_W"], s["bus_draw_W"]))
    return pts


def _interp(pts, rpm):
    if rpm <= pts[0][0]:
        return pts[0][1], pts[0][2]
    for a, b in zip(pts, pts[1:]):
        if rpm <= b[0]:
            f = (rpm - a[0]) / (b[0] - a[0])
            return (a[1] + f * (b[1] - a[1]), a[2] + f * (b[2] - a[2]))
    return pts[-1][1], pts[-1][2]


def cycle_losses(path, variant, v_dc, ratio, decimate=1, lockup=False):
    """variant: 'V1' or 'V2'. Returns aggregate loss/energy statistics."""
    rows = read_trace(path, decimate=decimate)
    dt = rows[1][0] - rows[0][0]
    v_lock = VEH["v_lockup_kmh"]
    spin = _spin_table(ratio, v_dc)   # also used for rolling zero-torque drag

    agg = dict(t_total=0.0, t_stand=0.0, t_lock=0.0, t_mot=0.0, t_gen=0.0,
               E_shaft_mot=0.0, E_dc_mot=0.0, E_shaft_gen=0.0, E_dc_gen=0.0,
               E_loss_mach=0.0, E_loss_inv=0.0, E_spin_shaft=0.0,
               E_spin_bus=0.0, E_rollspin_shaft=0.0, E_rollspin_bus=0.0,
               n_infeasible=0)

    for t, v_kmh, p_wheel, p_capt in rows:
        agg["t_total"] += dt
        v = v_kmh / 3.6
        if v < 0.3:
            agg["t_stand"] += dt
            agg["E_loss_inv"] += INV["P_standby"] * dt
            continue
        omega_w = v / VEH["r_dyn"]
        rpm = omega_w * ratio * 60.0 / (2 * math.pi)
        if p_wheel > 0.0:
            if lockup and v_kmh >= v_lock:
                drag, busd = _interp(spin, rpm)
                agg["t_lock"] += dt
                agg["E_spin_shaft"] += drag * dt
                agg["E_spin_bus"] += busd * dt
                continue
            T_wheel = p_wheel / omega_w
            T_shaft = T_wheel / (ratio * VEH["eta_red"])
            r = mc.point_full(T_shaft, rpm, v_dc)
            if r is None:
                # torque beyond envelope in this cell (rare; count and clamp)
                agg["n_infeasible"] += 1
                omega_m = rpm * 2 * math.pi / 60.0
                T_shaft = mc.max_torque(omega_m, v_dc) * 0.999
                r = mc.point_full(T_shaft, rpm, v_dc)
            agg["t_mot"] += dt
            agg["E_shaft_mot"] += r["P_shaft_W"] * dt
            agg["E_dc_mot"] += r["P_dc_W"] * dt
            agg["E_loss_mach"] += (r["P_cu_W"] + r["P_fe_W"] + r["P_fw_W"]) * dt
            agg["E_loss_inv"] += r["P_inv_W"] * dt
        elif p_capt > 1.0:
            T_wheel = p_capt / omega_w
            T_shaft = -T_wheel * VEH["eta_red"] / ratio
            r = mc.point_full(T_shaft, rpm, v_dc)
            if r is None:
                agg["n_infeasible"] += 1
                continue
            agg["t_gen"] += dt
            agg["E_shaft_gen"] += -r["P_shaft_W"] * dt   # >0, into machine
            agg["E_dc_gen"] += -r["P_dc_W"] * dt         # >0, into bus
            agg["E_loss_mach"] += (r["P_cu_W"] + r["P_fe_W"] + r["P_fw_W"]) * dt
            agg["E_loss_inv"] += r["P_inv_W"] * dt
        else:
            # coasting / friction-only braking: machine spins at zero torque;
            # iron+windage drag decelerates the vehicle (charged here), flux
            # weakening copper + standby drawn from the bus
            drag, busd = _interp(spin, rpm)
            agg["E_rollspin_shaft"] += drag * dt
            agg["E_rollspin_bus"] += busd * dt

    J2kWh = 1.0 / 3.6e6
    res = dict(
        variant=variant, v_dc=v_dc, ratio=ratio, decimate=decimate,
        duration_h=agg["t_total"] / 3600.0,
        stand_frac=agg["t_stand"] / agg["t_total"],
        lockup_frac=agg["t_lock"] / agg["t_total"],
        E_shaft_mot_kWh=agg["E_shaft_mot"] * J2kWh,
        E_dc_mot_kWh=agg["E_dc_mot"] * J2kWh,
        E_shaft_gen_kWh=agg["E_shaft_gen"] * J2kWh,
        E_dc_gen_kWh=agg["E_dc_gen"] * J2kWh,
        E_loss_mach_kWh=agg["E_loss_mach"] * J2kWh,
        E_loss_inv_kWh=agg["E_loss_inv"] * J2kWh,
        E_spin_shaft_kWh=agg["E_spin_shaft"] * J2kWh,
        E_spin_bus_kWh=agg["E_spin_bus"] * J2kWh,
        E_rollspin_shaft_kWh=agg["E_rollspin_shaft"] * J2kWh,
        E_rollspin_bus_kWh=agg["E_rollspin_bus"] * J2kWh,
        n_infeasible=agg["n_infeasible"],
    )
    res["eta_mot_avg"] = (res["E_shaft_mot_kWh"] / res["E_dc_mot_kWh"]
                          if res["E_dc_mot_kWh"] > 0 else 0.0)
    res["eta_gen_avg"] = (res["E_dc_gen_kWh"] / res["E_shaft_gen_kWh"]
                          if res["E_shaft_gen_kWh"] > 0 else 0.0)
    res["mean_heat_kW"] = (res["E_loss_mach_kWh"] + res["E_loss_inv_kWh"]
                           + res["E_spin_shaft_kWh"] + res["E_spin_bus_kWh"]
                           + res["E_rollspin_shaft_kWh"]
                           + res["E_rollspin_bus_kWh"]) / res["duration_h"]
    return res
