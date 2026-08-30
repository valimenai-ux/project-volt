"""
Project Volt - WS1 Loads & Duty Cycles - main analysis runner.

    python run_ws1.py

Writes:  data/*.csv, figs/*.png, results.json
"""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from volt_params import VEH, DL, AUX, ENG, CTL, G, params_dump
import volt_cycles as vc
import volt_physics as vp
import volt_variants as vv

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data"); FIGS = os.path.join(HERE, "figs")
os.makedirs(DATA, exist_ok=True); os.makedirs(FIGS, exist_ok=True)
R = {}   # results

plt.rcParams.update({"figure.dpi": 130, "font.size": 8.5,
                     "axes.grid": True, "grid.alpha": 0.3,
                     "axes.titlesize": 9, "figure.autolayout": False})


def kw(x):
    return x / 1e3


# =====================================================================
# 1. CYCLES
# =====================================================================
cycA = vc.build_cycle_A()
cycB = vc.build_cycle_B()

for c in (cycA, cycB):
    c["res"] = vp.wheel_power(c["t"], c["v"], c["grade"], VEH.m_gvw)
    c["P"] = c["res"]["P_wheel"]
    c["s"] = np.concatenate(([0.0], np.cumsum(
        0.5 * (c["v"][1:] + c["v"][:-1]) * np.diff(c["t"]))))

R["params"] = params_dump()

# --- grade-profile statistics for VOLT-REG
_ds = np.gradient(cycB["s"]); _g = cycB["grade"]
def _longest_run(mask, s):
    best = cur = 0.0
    for k in range(1, mask.size):
        if mask[k]:
            cur += s[k] - s[k - 1]
            best = max(best, cur)
        else:
            cur = 0.0
    return best
R["grade_profile_VOLT-REG"] = {
    "max_pct": float(np.max(_g)) * 100, "min_pct": float(np.min(_g)) * 100,
    "net_elevation_change_m": float(np.sum(_g * _ds)),
    "total_climb_m": float(np.sum(np.clip(_g, 0, None) * _ds)),
    "total_descent_m": float(np.sum(np.clip(_g, None, 0) * _ds)),
    "dist_frac_above_4pct": float(np.sum(_ds[_g > 0.04]) / np.sum(_ds)),
    "dist_frac_below_m4pct": float(np.sum(_ds[_g < -0.04]) / np.sum(_ds)),
    "longest_run_above_4pct_km": _longest_run(_g > 0.04, cycB["s"]) / 1000.0,
    "longest_run_below_m4pct_km": _longest_run(_g < -0.04, cycB["s"]) / 1000.0,
    "longest_run_above_3pct_km": _longest_run(_g > 0.03, cycB["s"]) / 1000.0,
}

# --- baseline cross-checks (first-principles, closed form) -------------
def road_power(v_kmh, grade=0.0, m=VEH.m_gvw):
    v = v_kmh / 3.6
    f, fa, fr, fg = vp.road_load_force(np.array([v]), np.array([grade]), m)
    return float(f[0]) , float(f[0]) * v, dict(aero=float(fa[0]),
                                               roll=float(fr[0]),
                                               grade=float(fg[0]))

f85, p85, comp85 = road_power(85.0)
f60g6, p60g6, _ = road_power(60.0, 0.06)
R["baseline_crosscheck"] = {
    "cruise85_force_N": f85, "cruise85_wheel_kW": kw(p85),
    "cruise85_components_N": comp85,
    "baseline_says": "≈2.0 kN, ≈47 kW",
    "grade6_at_60kmh_wheel_kW": kw(p60g6),
    "grade6_at_60kmh_bus_kW": kw(p60g6 / DL.eta_bus_to_wheel),
    "grade6_at_60kmh_engine_shaft_kW": kw(p60g6 / DL.eta_series_total),
    "grade6_at_60kmh_engine_shaft_plus_aux_kW":
        kw(p60g6 / DL.eta_series_total + AUX.p_aux_nom / DL.eta_gen),
    "baseline_v2_genset_floor_kW": kw(CTL.genset_v2_floor),
    "launch_20pc_grade_force_N": float(vp.road_load_force(
        np.array([1.0]), np.array([0.20]), VEH.m_gvw)[0][0]),
    "engine_direct_max_force_N_at_700Nm":
        700.0 * VEH.fd_ratio * DL.eta_direct / VEH.r_dyn,
    "engine_idle_road_speed_kmh":
        ENG.idle_rpm / VEH.fd_ratio * 2 * np.pi / 60 * VEH.r_dyn * 3.6,
    "eta_series_product": DL.eta_series_total,
}


def steady_speed_for_wheel_power(P, grade, m=VEH.m_gvw, veh=VEH):
    """Solve 0.5*rho*CdA*v^3 + (Crr m g cos + m g sin) v = P."""
    th = math.atan(grade)
    k = 0.5 * veh.rho_air * veh.CdA
    c = veh.Crr * m * G * math.cos(th) + m * G * math.sin(th)
    lo, hi = 0.0, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if k * mid ** 3 + c * mid > P:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# =====================================================================
# 2. TASK-2 METRICS
# =====================================================================
R["cycles"] = {}
for c in (cycA, cycB):
    m = vp.cycle_metrics(c["t"], c["v"], c["grade"], c["P"])
    m["dt_s"] = float(np.median(np.diff(c["t"])))
    R["cycles"][c["name"]] = m

# ---- time-at-power histograms
R["power_histogram"] = {}
for c in (cycA, cycB):
    edges, secs = vp.power_histogram(c["t"], c["P"])
    keep = secs > 1e-9
    R["power_histogram"][c["name"]] = {
        "bin_lo_kW": [kw(e) for e in edges[:-1][keep]],
        "bin_hi_kW": [kw(e) for e in edges[1:][keep]],
        "seconds": [float(x) for x in secs[keep]],
        "pct_of_cycle": [float(x) / c["t"][-1] * 100 for x in secs[keep]],
    }

# ---- regen absorb-limit sensitivity
caps = np.array([0, 10, 20, 30, 40, 50, 60, 75, 90, 100, 125,
                 150, 175, 200, 1e4]) * 1e3
R["regen_sensitivity"] = {}
for c in (cycA, cycB):
    rows = []
    e_brake = -vp.trapz(np.clip(c["P"], None, 0), c["t"])
    for cap in caps:
        _, p_capt, _ = vp.regen_split(c["v"], c["P"], cap)
        e_c = vp.trapz(p_capt, c["t"])
        rows.append(dict(cap_kW=kw(cap) if cap < 1e6 else None,
                         cap_label=("uncapped" if cap > 5e3 * 1e3 else f"{kw(cap):.0f}"),
                         E_captured_mech_kWh=e_c / 3.6e6,
                         E_captured_elec_kWh=e_c * DL.eta_wheel_to_bus / 3.6e6,
                         frac_of_braking_mech=e_c / e_brake,
                         frac_of_braking_elec=e_c * DL.eta_wheel_to_bus / e_brake,
                         frac_of_tractive_elec=(e_c * DL.eta_wheel_to_bus /
                                                vp.trapz(np.clip(c["P"], 0, None), c["t"]))))
    R["regen_sensitivity"][c["name"]] = dict(
        E_braking_kWh=e_brake / 3.6e6, rows=rows)

# regen low-speed blend-out sensitivity (how much is lost to the blend)
R["regen_blend_sensitivity"] = {}
for c in (cycA, cycB):
    base = vp.trapz(vp.regen_split(c["v"], c["P"], 75e3)[1], c["t"])
    save = CTL.v_regen_blend_lo, CTL.v_regen_blend_hi
    out = {}
    for lo, hi in [(0.0, 0.0001), (3/3.6, 8/3.6), (5/3.6, 12/3.6)]:
        object.__setattr__(CTL, "v_regen_blend_lo", lo)
        object.__setattr__(CTL, "v_regen_blend_hi", hi)
        e = vp.trapz(vp.regen_split(c["v"], c["P"], 75e3)[1], c["t"])
        out[f"blend_{lo*3.6:.0f}-{hi*3.6:.0f}kmh"] = e / 3.6e6
    object.__setattr__(CTL, "v_regen_blend_lo", save[0])
    object.__setattr__(CTL, "v_regen_blend_hi", save[1])
    R["regen_blend_sensitivity"][c["name"]] = out

# =====================================================================
# 3. THE FOUR NUMBERS
# =====================================================================
R["four_numbers"] = {}

# --- V1 Postal on VOLT-SUB : pure series, motor carries all wheel power
fnA = vv.four_numbers(cycA["t"], cycA["v"], cycA["P"])
R["four_numbers"]["V1_postal_VOLT-SUB"] = {k: v for k, v in fnA.items()
                                           if not k.startswith("_")}

# --- V2 Trucker on VOLT-REG : i-MMD split
# Two passes: the first sizes the constant genset, the second re-runs the
# direct-path split reserving that much crankshaft power for the generator,
# so the same engine is never asked to do both jobs at once.
p_dir, locked, rpm, p_dir_max = vv.v2_direct_share(
    cycB["t"], cycB["v"], cycB["P"])
_fn0 = vv.four_numbers(cycB["t"], cycB["v"], cycB["P"], p_wheel_direct=p_dir)
p_dir, locked, rpm, p_dir_max = vv.v2_direct_share(
    cycB["t"], cycB["v"], cycB["P"],
    p_gen_reserve_bus=_fn0["N2_genset_const_bus_kW"] * 1e3)
fnB = vv.four_numbers(cycB["t"], cycB["v"], cycB["P"], p_wheel_direct=p_dir)
R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"] = {k: v for k, v in fnB.items()
                                                 if not k.startswith("_")}
R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]["lockup_time_frac"] = \
    float(np.mean(locked))
R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]["lockup_distance_frac"] = \
    float(vp.trapz(locked * cycB["v"], cycB["t"]) / vp.trapz(cycB["v"], cycB["t"]))
R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]["E_direct_path_kWh"] = \
    vp.trapz(p_dir, cycB["t"]) / 3.6e6
R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]["direct_share_of_tractive"] = \
    float(vp.trapz(p_dir, cycB["t"]) /
          vp.trapz(np.clip(cycB["P"], 0, None), cycB["t"]))

# --- V2 forced series-only on VOLT-REG (clutch failed open / limp)
fnBs = vv.four_numbers(cycB["t"], cycB["v"], cycB["P"])
R["four_numbers"]["V2_trucker_VOLT-REG_series_only"] = {
    k: v for k, v in fnBs.items() if not k.startswith("_")}

# --- V2 on VOLT-SUB (shared spine must also do city work)
fnBA = vv.four_numbers(cycA["t"], cycA["v"], cycA["P"])
R["four_numbers"]["V2_trucker_VOLT-SUB_series"] = {
    k: v for k, v in fnBA.items() if not k.startswith("_")}

# =====================================================================
# 4. SENSITIVITIES
# =====================================================================
R["sensitivity"] = {}

# ---- 4a payload +/- 20 %
pay = VEH.m_payload_at_gvw
masses = {
    "empty_curb": VEH.m_curb_operating,
    "payload_-20pct": VEH.m_curb_operating + 0.8 * pay,
    "payload_nominal_GVW": VEH.m_gvw,
    "payload_+20pct": VEH.m_curb_operating + 1.2 * pay,
}
R["sensitivity"]["payload"] = {}
for c in (cycA, cycB):
    rows = {}
    for lbl, m in masses.items():
        rr = vp.wheel_power(c["t"], c["v"], c["grade"], m)
        P = rr["P_wheel"]
        met = vp.cycle_metrics(c["t"], c["v"], c["grade"], P)
        pd = (vv.v2_direct_share(c["t"], c["v"], P)[0]
              if c is cycB else None)
        fn = vv.four_numbers(c["t"], c["v"], P, p_wheel_direct=pd)
        rows[lbl] = {
            "mass_kg": m,
            "E_per_km_kWh": met["E_per_km_kWh"],
            "E_net_per_km_kWh": met["E_net_per_km_kWh"],
            "P_peak_kW": met["P_peak_kW"],
            "P95_kW": met["P95_kW"],
            "E_braking_kWh": met["E_braking_kWh"],
            "regen_frac_mech_at75kW": met["regen_recoverable_frac_mech"],
            "N1_motor_rms_shaft_kW": fn["N1_motor_rms_shaft_kW"],
            "N2_genset_const_bus_kW": fn["N2_genset_const_bus_kW"],
            "N3_buffer_5min_kWh": fn["N3_buffer_5min_kWh"],
            "N4_peak_regen_wheel_kW": fn["N4_peak_regen_wheel_kW"],
        }
    R["sensitivity"]["payload"][c["name"]] = rows

# ---- 4b aux load
R["sensitivity"]["aux"] = {}
for c, pd_ in ((cycA, None), (cycB, p_dir)):
    rows = {}
    for lbl, pa in (("0.5kW", AUX.p_aux_low), ("2.0kW", AUX.p_aux_nom),
                    ("4.0kW", AUX.p_aux_high)):
        fn = vv.four_numbers(c["t"], c["v"], c["P"], p_wheel_direct=pd_,
                             p_aux=pa)
        rows[lbl] = {"N2_genset_const_bus_kW": fn["N2_genset_const_bus_kW"],
                     "N3_buffer_5min_kWh": fn["N3_buffer_5min_kWh"]}
    R["sensitivity"]["aux"][c["name"]] = rows

# ---- 4c sustained 10 km climb at 6 %
climb = {}
gr = 0.06
for v_kmh in (40, 50, 60, 70, 85, 100):
    f, p, comp = road_power(v_kmh, gr)
    climb[f"{v_kmh}kmh"] = {
        "wheel_force_N": f, "wheel_kW": kw(p),
        "components_N": comp,
        "bus_kW": kw(p / DL.eta_bus_to_wheel),
        "series_engine_shaft_kW": kw(p / DL.eta_series_total),
        "direct_engine_shaft_kW": kw(p / DL.eta_direct),
        "engine_rpm_locked": float(vp.engine_rpm_from_speed(np.array([v_kmh / 3.6]))[0]),
        "engine_max_shaft_kW_at_that_rpm": kw(float(
            vp.direct_path_wheel_power_max(np.array([v_kmh / 3.6]))[1][0])),
        "time_for_10km_s": 10000.0 / (v_kmh / 3.6),
        "E_wheel_10km_kWh": p * (10000.0 / (v_kmh / 3.6)) / 3.6e6,
    }
p_av_v1 = (CTL.genset_v1_class * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel
p_av_v2 = (CTL.genset_v2_floor * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel
R["sensitivity"]["climb_10km_6pc"] = {
    "per_speed": climb,
    "elevation_gain_m": 10000.0 * gr,
    "potential_energy_kWh": VEH.m_gvw * G * 10000.0 * gr / 3.6e6,
    "V1_genset_50kW_wheel_kW_available": kw(p_av_v1),
    "V1_sustained_speed_kmh": steady_speed_for_wheel_power(p_av_v1, gr) * 3.6,
    "V2_genset_110kW_series_wheel_kW_available": kw(p_av_v2),
    "V2_series_sustained_speed_kmh": steady_speed_for_wheel_power(p_av_v2, gr) * 3.6,
}
# V2 direct-path sustained speed: solve v where engine direct power == demand
vs = np.linspace(5, 30, 2500)
pd_max, _, _ = vp.direct_path_wheel_power_max(vs)
p_need = np.array([vp.road_load_force(np.array([x]), np.array([gr]), VEH.m_gvw)[0][0] * x
                   for x in vs])
ok = pd_max >= p_need
imin = int(np.argmin(p_need - pd_max))
R["sensitivity"]["climb_10km_6pc"]["V2_direct_path_alone"] = {
    "any_speed_sustainable": bool(ok.any()),
    "best_speed_kmh": float(vs[imin] * 3.6),
    "min_deficit_at_wheel_kW": kw(float((p_need - pd_max)[imin])),
    "note": ("With a single 2.8:1 ratio the crank speed is tied to road "
             "speed, so the engine cannot reach its power peak at grade-"
             "hold speeds. The direct path alone holds no speed on 6%."),
}
# max grade the direct path alone can hold, per speed
gr_hold_direct = {}
def grade_holdable(f_avail, v, m=VEH.m_gvw):
    """tan(theta) the vehicle can hold at speed v with f_avail at the wheel."""
    fa = 0.5 * VEH.rho_air * VEH.CdA * v ** 2
    lo_th, hi_th = -0.6, 0.6
    for _ in range(200):
        mth = 0.5 * (lo_th + hi_th)
        need = fa + VEH.Crr * m * G * math.cos(mth) + m * G * math.sin(mth)
        if need > f_avail:
            hi_th = mth
        else:
            lo_th = mth
    return math.tan(0.5 * (lo_th + hi_th))


for v_kmh in (50, 60, 70, 85, 100):
    vq = v_kmh / 3.6
    pdq = float(vp.direct_path_wheel_power_max(np.array([vq]))[0][0])
    gr_hold_direct[f"{v_kmh}kmh"] = 100 * grade_holdable(pdq / vq, vq)
R["sensitivity"]["max_grade_direct_path_pct"] = gr_hold_direct
# battery drain to hold 85 km/h on the 10 km climb (V2, engine at max direct)
v85 = 85 / 3.6
p_need85 = float(vp.road_load_force(np.array([v85]), np.array([gr]), VEH.m_gvw)[0][0]) * v85
pd85_raw = float(vp.direct_path_wheel_power_max(np.array([v85]))[0][0])
# the accessories are fed off the same crankshaft through the generator,
# so they come out of the direct path's wheel power (B2 and §6.6 apply the
# same 2 kW; dropping it here would be an inconsistent boundary)
pd85 = pd85_raw - AUX.p_aux_nom / DL.eta_gen * DL.eta_direct
deficit = max(0.0, p_need85 - pd85)
t85 = 10000.0 / v85
R["sensitivity"]["climb_10km_6pc"]["hold_85kmh_V2"] = {
    "wheel_need_kW": kw(p_need85),
    "engine_direct_available_kW_before_aux": kw(pd85_raw),
    "engine_direct_available_kW_after_aux": kw(pd85),
    "deficit_at_wheel_kW": kw(deficit), "duration_s": t85,
    "battery_energy_at_bus_kWh": deficit / DL.eta_bus_to_wheel * t85 / 3.6e6,
    "battery_energy_at_cells_kWh": (deficit / DL.eta_bus_to_wheel
                                    / DL.eta_batt_dis * t85 / 3.6e6),
}
# descent counterpart
desc = {}
for v_kmh in (60, 85, 100):
    v = v_kmh / 3.6
    f, _, _, _ = vp.road_load_force(np.array([v]), np.array([-gr]), VEH.m_gvw)
    p = float(f[0]) * v          # negative -> retardation demand
    desc[f"{v_kmh}kmh"] = {
        "net_wheel_kW": kw(p),
        "retardation_required_kW": kw(-p),
        "time_10km_s": 10000.0 / v,
        "E_to_dissipate_kWh": -p * (10000.0 / v) / 3.6e6,
    }
R["sensitivity"]["descent_10km_6pc"] = {
    "per_speed": desc,
    "potential_energy_released_kWh": VEH.m_gvw * G * 600.0 / 3.6e6}

# ---- 4d driver aggressiveness on VOLT-SUB
R["sensitivity"]["driver_braking"] = {}
for ab in (0.9, 1.25, 1.6):
    dp = vc.DriverParams(a_max=1.15, p_use=72e3, a_brake=ab,
                         noise_sigma=0.30, noise_tau=22.0)
    ca = vc.build_cycle_A(dp=dp)
    P = vp.wheel_power(ca["t"], ca["v"], ca["grade"], VEH.m_gvw)["P_wheel"]
    met = vp.cycle_metrics(ca["t"], ca["v"], ca["grade"], P)
    R["sensitivity"]["driver_braking"][f"a_brake_{ab}"] = {
        "P_regen_peak_wheel_kW": met["P_regen_peak_wheel_kW"],
        "regen_frac_mech_at75kW": met["regen_recoverable_frac_mech"],
        "E_braking_kWh": met["E_braking_kWh"],
        "E_per_km_kWh": met["E_per_km_kWh"],
        "distance_km": met["distance_km"],
    }

# ---- 4d2 dwell-time sensitivity on VOLT-SUB (the least certain cycle input)
R["sensitivity"]["dwell_scale"] = {}
for sc in (0.5, 1.0, 1.5, 2.0):
    ca = vc.build_cycle_A(dwell_scale=sc)
    Pd = vp.wheel_power(ca["t"], ca["v"], ca["grade"], VEH.m_gvw)["P_wheel"]
    md = vp.cycle_metrics(ca["t"], ca["v"], ca["grade"], Pd)
    fnd = vv.four_numbers(ca["t"], ca["v"], Pd)
    R["sensitivity"]["dwell_scale"][f"x{sc}"] = {
        "duration_s": md["duration_s"], "distance_km": md["distance_km"],
        "avg_speed_kmh": md["avg_speed_kmh"],
        "stopped_fraction": md["stopped_fraction"],
        "E_per_km_kWh": md["E_per_km_kWh"],
        "N1_motor_rms_shaft_kW": fnd["N1_motor_rms_shaft_kW"],
        "N2_genset_const_bus_kW": fnd["N2_genset_const_bus_kW"],
        "N3_buffer_5min_kWh": fnd["N3_buffer_5min_kWh"],
    }

# ---- 4e time-resolution sensitivity (1 Hz vs 10 Hz)
R["sensitivity"]["time_resolution"] = {}
for c in (cycA, cycB):
    out = {}
    for step, lbl in ((1, "10Hz"), (10, "1Hz")):
        t1, v1, g1 = c["t"][::step], c["v"][::step], c["grade"][::step]
        P1 = vp.wheel_power(t1, v1, g1, VEH.m_gvw)["P_wheel"]
        met = vp.cycle_metrics(t1, v1, g1, P1)
        out[lbl] = {"P_peak_kW": met["P_peak_kW"], "P95_kW": met["P95_kW"],
                    "P_rms_wheel_kW": met["P_rms_wheel_kW"],
                    "E_per_km_kWh": met["E_per_km_kWh"],
                    "P_regen_peak_wheel_kW": met["P_regen_peak_wheel_kW"]}
    R["sensitivity"]["time_resolution"][c["name"]] = out

# ---- 4f seed ensemble (cycle-construction robustness)
# Extrema (peak power, P99, braking energy, peak regen, buffer swing) are
# properties of ONE draw of the route generator, not of the duty. The
# ensemble includes the reference seed so that the envelope reported to
# downstream workstreams can never sit below the cycle actually published.
R["sensitivity"]["seed_ensemble"] = {}
ENS_KEYS = ("E_per_km_kWh", "stops_per_km", "avg_speed_kmh", "P_peak_kW",
            "P95_kW", "P99_kW", "E_braking_kWh",
            "N1_motor_rms_shaft_kW", "N2_genset_const_bus_kW",
            "N3_buffer_5min_kWh", "N4_peak_regen_wheel_kW")
for builder, nm, ref_seed in ((vc.build_cycle_A, "VOLT-SUB", 11),
                              (vc.build_cycle_B, "VOLT-REG", 23)):
    acc = {}
    for sd in [ref_seed] + [x + 3 for x in range(7)]:
        cc = builder(seed=sd)
        Pc = vp.wheel_power(cc["t"], cc["v"], cc["grade"], VEH.m_gvw)["P_wheel"]
        met = vp.cycle_metrics(cc["t"], cc["v"], cc["grade"], Pc)
        pdd = (vv.v2_direct_share(cc["t"], cc["v"], Pc)[0]
               if nm == "VOLT-REG" else None)
        fn = vv.four_numbers(cc["t"], cc["v"], Pc, p_wheel_direct=pdd)
        row = dict(met)
        row.update({k: fn[k] for k in ("N1_motor_rms_shaft_kW",
                                       "N2_genset_const_bus_kW",
                                       "N3_buffer_5min_kWh",
                                       "N4_peak_regen_wheel_kW")})
        for k in ENS_KEYS:
            acc.setdefault(k, []).append(row[k])
    R["sensitivity"]["seed_ensemble"][nm] = {
        k: {"mean": float(np.mean(v)), "min": float(np.min(v)),
            "max": float(np.max(v)), "std": float(np.std(v)),
            "n": len(v)}
        for k, v in acc.items()}

# ---- 4g VOLT-SUB with rolling suburban terrain (+/-1.5 %)
sA = cycA["s"]
gA = 0.015 * np.sin(2 * np.pi * sA / 1400.0)
gA = gA - np.sum(gA * np.gradient(sA)) / np.sum(np.gradient(sA))
PA_g = vp.wheel_power(cycA["t"], cycA["v"], gA, VEH.m_gvw)["P_wheel"]
metAg = vp.cycle_metrics(cycA["t"], cycA["v"], gA, PA_g)
fnAg = vv.four_numbers(cycA["t"], cycA["v"], PA_g)
R["sensitivity"]["VOLT-SUB_rolling_terrain_1.5pc"] = {
    "E_per_km_kWh": metAg["E_per_km_kWh"],
    "E_braking_kWh": metAg["E_braking_kWh"],
    "P_peak_kW": metAg["P_peak_kW"],
    "N1_motor_rms_shaft_kW": fnAg["N1_motor_rms_shaft_kW"],
    "N2_genset_const_bus_kW": fnAg["N2_genset_const_bus_kW"],
    "N3_buffer_5min_kWh": fnAg["N3_buffer_5min_kWh"],
    "N4_peak_regen_wheel_kW": fnAg["N4_peak_regen_wheel_kW"],
}

# ---- 4h WORST SUSTAINED DUTY POINT (the number that actually sizes the
#      traction motor - a cycle-average RMS hides it)
sust = {}
for lbl, p_gen_kw in (("V1_genset_50kW", 50.0), ("V2_genset_110kW", 110.0)):
    rows = {}
    p_wheel_av = (p_gen_kw * 1e3 * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel
    for g in (0.0, 0.02, 0.04, 0.06, 0.08, 0.12, 0.20):
        vsus = steady_speed_for_wheel_power(p_wheel_av, g)
        rows[f"grade_{g*100:.0f}pct"] = {
            "wheel_force_at_that_speed_N": p_wheel_av / max(vsus, 1e-6),
            "sustained_speed_kmh": vsus * 3.6,
            "motor_wheel_kW": kw(p_wheel_av),
            "motor_shaft_kW": kw(p_wheel_av / DL.eta_red),
            "motor_torque_Nm_at_shaft": (p_wheel_av / DL.eta_red) /
                                        max(vsus / VEH.r_dyn * VEH.motor_ratio, 1e-6),
            "duration_10km_s": 10000.0 / vsus if vsus > 0.1 else None,
        }
    sust[lbl] = rows
R["sensitivity"]["sustained_series_duty"] = sust

# ---- 4i capability-limited "achieved" traces
scen = {}
# (a) energy-unlimited battery -> pure peak-power check
ach = vv.simulate_achievable(cycB["t"], cycB["v"], cycB["grade"], VEH.m_gvw,
                             mode="V2", p_batt_pk=120e3, p_motor_pk=150e3)
# (b) finite 2.0 kWh usable buffer -> the real derate
ach2 = vv.simulate_achievable(cycB["t"], cycB["v"], cycB["grade"], VEH.m_gvw,
                              mode="V2", p_batt_pk=120e3, p_motor_pk=150e3,
                              batt_kwh=2.0)
# (c) baseline minimum motor (75 kW peak) with the same finite buffer
ach3 = vv.simulate_achievable(cycB["t"], cycB["v"], cycB["grade"], VEH.m_gvw,
                              mode="V2", p_batt_pk=120e3, p_motor_pk=75e3,
                              batt_kwh=2.0)
d_dem = R["cycles"]["VOLT-REG"]["distance_km"]
for lbl, a in (("battery_unlimited_motor150kW", ach),
               ("buffer_2kWh_motor150kW", ach2),
               ("buffer_2kWh_motor75kW", ach3)):
    dv = (cycB["v"] - a["v"]) * 3.6
    scen[lbl] = {
        "distance_km": float(np.trapezoid(a["v"], cycB["t"]) / 1000.0),
        "shortfall_pct": float(100 * (1 - np.trapezoid(a["v"], cycB["t"]) / 1000.0 / d_dem)),
        "max_speed_deficit_kmh": float(np.max(dv)),
        "time_deficit_gt_5kmh_pct": float(np.mean(dv > 5.0) * 100),
        "min_speed_where_grade_gt_4pct_kmh":
            float(np.min(a["v"][cycB["grade"] > 0.04]) * 3.6)
            if np.any(cycB["grade"] > 0.04) else None,
        "friction_brake_energy_kWh": vp.trapz(a["p_friction"], cycB["t"]) / 3.6e6,
        "batt_min_kWh": (None if a["e_batt"] is None
                         else float(np.min(a["e_batt"])) / 3.6e6),
        "batt_flat_time_pct": (None if a["e_batt"] is None
                               else float(np.mean(a["e_batt"] <= 1e-6) * 100)),
        "regen_refused_to_friction_kWh": vp.trapz(a["p_friction"], cycB["t"]) / 3.6e6,
    }
R["achieved_VOLT-REG_V2"] = {"demand_distance_km": d_dem, "scenarios": scen}
achB_plot = ach2

# V1 capability on VOLT-SUB with a 50 kW genset and a 1.5 kWh buffer
achA = vv.simulate_achievable(cycA["t"], cycA["v"], cycA["grade"], VEH.m_gvw,
                              mode="V1",
                              p_gen_bus=CTL.genset_v1_class * DL.eta_gen,
                              p_batt_pk=120e3, p_motor_pk=150e3, batt_kwh=1.5)
dvA = (cycA["v"] - achA["v"]) * 3.6
R["achieved_VOLT-SUB_V1"] = {
    "distance_demand_km": R["cycles"]["VOLT-SUB"]["distance_km"],
    "distance_achieved_km": float(np.trapezoid(achA["v"], cycA["t"]) / 1000.0),
    "max_speed_deficit_kmh": float(np.max(dvA)),
    "time_deficit_gt_2kmh_pct": float(np.mean(dvA > 2.0) * 100),
    "batt_min_kWh": float(np.min(achA["e_batt"])) / 3.6e6,
    "friction_brake_energy_kWh": vp.trapz(achA["p_friction"], cycA["t"]) / 3.6e6,
}

# ---- 4j sustained 10 km climb, forward-simulated with a finite buffer
climb_dem = vc.build_climb(10.0, 0.06, 85.0, duration_s=1800.0)
climb_sims = {}
for lbl, kwargs in (
        ("V2_buffer2kWh", dict(mode="V2", batt_kwh=2.0, p_motor_pk=150e3)),
        ("V2_buffer5kWh", dict(mode="V2", batt_kwh=5.0, p_motor_pk=150e3)),
        ("V2_battery_unlimited", dict(mode="V2", batt_kwh=None, p_motor_pk=150e3)),
        ("V1_50kW_buffer2kWh", dict(mode="V1", batt_kwh=2.0, p_motor_pk=150e3,
                                    p_gen_bus=CTL.genset_v1_class * DL.eta_gen))):
    a = vv.simulate_achievable(climb_dem["t"], climb_dem["v"],
                               climb_dem["grade"], VEH.m_gvw,
                               p_batt_pk=120e3, **kwargs)
    dt_c = float(np.median(np.diff(climb_dem["t"])))
    sdist = np.cumsum(a["v"]) * dt_c
    idx = int(np.searchsorted(sdist, 10000.0))
    eb = a["e_batt"]
    # "exhausted" = below 2% of usable; an asymptotic approach to exactly
    # zero would otherwise be reported minutes late
    _thr = (kwargs.get("batt_kwh") or 0.0) * 3.6e6 * 0.02
    flat = ((eb <= _thr) & (np.arange(a["v"].size) > 10)
            if eb is not None else np.zeros(a["v"].size, bool))
    climb_sims[lbl] = {
        "settled_speed_kmh": float(np.mean(a["v"][-int(120 / dt_c):]) * 3.6),
        "time_to_climb_10km_s": float(climb_dem["t"][idx]) if idx < a["v"].size else None,
        "avg_speed_over_10km_kmh": (10000.0 / float(climb_dem["t"][idx]) * 3.6
                                    if idx < a["v"].size else None),
        "battery_exhausted_after_s": (float(climb_dem["t"][int(np.argmax(flat))])
                                      if (kwargs.get("batt_kwh") and flat.any()) else None),
        "speed_still_held_at_that_time_kmh":
            (float(a["v"][int(np.argmax(flat))] * 3.6)
             if (kwargs.get("batt_kwh") and flat.any()) else None),
        "battery_energy_used_kWh": (None if eb is None else
                                    float(eb[0] - np.min(eb)) / 3.6e6),
    }
R["sensitivity"]["climb_10km_6pc"]["forward_sim"] = climb_sims
climb_plot = vv.simulate_achievable(climb_dem["t"], climb_dem["v"],
                                    climb_dem["grade"], VEH.m_gvw, mode="V2",
                                    batt_kwh=2.0, p_batt_pk=120e3,
                                    p_motor_pk=150e3)
climb_plot_v1 = vv.simulate_achievable(
    climb_dem["t"], climb_dem["v"], climb_dem["grade"], VEH.m_gvw, mode="V1",
    batt_kwh=2.0, p_batt_pk=120e3, p_motor_pk=150e3,
    p_gen_bus=CTL.genset_v1_class * DL.eta_gen)

# ---- 4k descent: buffer saturation + brake thermal (proper model)
#
# Corrections over a naive calculation, all of which make it worse or
# change the answer:
#   * the buffer starts at the supervisor's SOC target (55%), not empty,
#     so only 45% of it is available as regen headroom;
#   * the accessories keep drawing from the bus during the descent;
#   * once the buffer is full the electrical path can still absorb exactly
#     the accessory load and no more;
#   * a slower descent is WORSE, because less energy goes into aero drag;
#   * engine braking through the locked 2.8:1 path is credited explicitly
#     rather than ignored.
def descent_case(v_kmh, buffer_kwh, soc_start=0.55, p_eng_brake=0.0,
                 grade=-0.06, dist_m=10000.0, p_aux=AUX.p_aux_nom,
                 m=VEH.m_gvw, m_rotor=60.0):
    v = v_kmh / 3.6
    f = float(vp.road_load_force(np.array([v]), np.array([grade]), m)[0][0])
    p_ret = -f * v                      # W of retardation the driveline must take
    if p_ret <= 0:
        return None
    t_tot = dist_m / v
    # Below the idle-speed road speed the crank would be under idle, so the
    # clutch must open: no engine drag and no exhaust brake are available.
    v_floor = ENG.idle_rpm / VEH.fd_ratio * 2 * np.pi / 60 * VEH.r_dyn * 3.6
    eng_available = v_kmh >= v_floor
    p_eng_brake = p_eng_brake if eng_available else 0.0
    p_after_eng = max(0.0, p_ret - p_eng_brake)
    p_capt_w = min(p_after_eng, CTL.regen_cap_wheel)
    p_to_bus = p_capt_w * DL.eta_wheel_to_bus
    p_into_batt = (p_to_bus - p_aux) * DL.eta_batt_chg
    head = buffer_kwh * 3.6e6 * (1.0 - soc_start)
    t_fill = head / p_into_batt if p_into_batt > 0 else float("inf")
    # before the buffer fills: friction takes whatever regen cannot
    e_fric = max(0.0, p_after_eng - p_capt_w) * min(t_fill, t_tot)
    if t_fill < t_tot:
        # afterwards the electrical path absorbs only the accessory load
        p_capt_after = min(p_after_eng, p_aux / DL.eta_wheel_to_bus)
        e_fric += (p_after_eng - p_capt_after) * (t_tot - t_fill)
    return {
        "speed_kmh": v_kmh,
        "retardation_demanded_kW": kw(p_ret),
        "engine_brake_credit_kW": kw(p_eng_brake),
        "engine_braking_available": bool(eng_available),
        "regen_captured_at_wheel_kW": kw(p_capt_w),
        "descent_duration_s": t_tot,
        "energy_to_dissipate_kWh": p_ret * t_tot / 3.6e6,
        "regen_headroom_kWh": head / 3.6e6,
        "time_to_fill_headroom_s": t_fill,
        "buffer_fills": bool(t_fill < t_tot),
        "friction_brake_energy_kWh": e_fric / 3.6e6,
        "adiabatic_dT_K": e_fric / (m_rotor * 460.0),
    }


desc = {}
for v_kmh in (25, 35, 40, 50, 60, 70, 85, 100):
    v = v_kmh / 3.6
    f, _, _, _ = vp.road_load_force(np.array([v]), np.array([-0.06]), VEH.m_gvw)
    p = float(f[0]) * v
    desc[f"{v_kmh}kmh"] = {
        "net_wheel_kW": kw(p), "retardation_required_kW": kw(-p),
        "time_10km_s": 10000.0 / v,
        "E_to_dissipate_kWh": -p * (10000.0 / v) / 3.6e6,
        "engine_rpm_if_locked": float(vp.engine_rpm_from_speed(np.array([v]))[0]),
    }
R["sensitivity"]["descent_10km_6pc"] = {
    "per_speed": desc,
    "potential_energy_released_kWh": VEH.m_gvw * G * 600.0 / 3.6e6,
    "note": ("A slower descent dissipates MORE energy in the driveline, "
             "because aero drag - which scales with v^2 - takes a smaller "
             "share of the gravitational input."),
    "engine_brake_speed_floor_kmh": float(
        ENG.idle_rpm / VEH.fd_ratio * 2 * np.pi / 60 * VEH.r_dyn * 3.6),
    "floor_note": ("Below that road speed the crank would be under idle, so "
                   "the clutch must open and NEITHER engine drag NOR an "
                   "exhaust brake is available - in exactly the speed range "
                   "where the energy to dissipate is largest."),
}
therm = {}
for buf in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
    for veh_kmh in (30, 60, 85):
        for eb, ebl in ((0.0, "no_engine_brake"),
                        (10e3, "engine_drag_10kW"),
                        (30e3, "exhaust_brake_30kW")):
            r_ = descent_case(veh_kmh, buf, p_eng_brake=eb)
            if r_:
                therm[f"buffer{buf}kWh_{veh_kmh}kmh_{ebl}"] = r_
R["sensitivity"]["descent_10km_6pc"]["thermal"] = therm

# ---- 4l cross-check baseline "combined ~8 kN at 85 km/h -> 9-10 % grade"
v85 = 85 / 3.6
f_dir85 = float(vp.direct_path_wheel_power_max(np.array([v85]))[0][0]) / v85
out85 = {}
for p_mot in (75e3, 100e3, 150e3):
    f_tot = f_dir85 + p_mot / v85
    fa = 0.5 * VEH.rho_air * VEH.CdA * v85 ** 2
    # solve f_tot = fa + Crr*m*g*cos(th) + m*g*sin(th) for th, then report
    # grade = tan(th) - consistent with road_load_force elsewhere
    lo_th, hi_th = 0.0, 0.6
    for _ in range(200):
        mth = 0.5 * (lo_th + hi_th)
        need = fa + VEH.Crr * VEH.m_gvw * G * math.cos(mth) + \
            VEH.m_gvw * G * math.sin(mth)
        if need > f_tot:
            hi_th = mth
        else:
            lo_th = mth
    g_hold = math.tan(0.5 * (lo_th + hi_th))
    out85[f"motor_{p_mot/1e3:.0f}kW"] = {
        "combined_force_kN": f_tot / 1e3,
        "grade_holdable_pct": 100 * float(g_hold),
        "wheel_power_kW": kw(f_tot * v85),
        "battery_draw_kW": kw(p_mot / DL.eta_bus_to_wheel),
        "minutes_on_2kWh_buffer": 2.0 / (p_mot / DL.eta_bus_to_wheel / 1e3) * 60,
    }
R["baseline_crosscheck"]["combined_at_85kmh"] = out85


# ---- 4l2 the 6% grade FLOOR swept over mass, accessories and road load.
# The payload sweep in 4a only moves the two cycles; the requirement that
# actually sizes the V2 genset was never swept at all.
def genset_shaft_for_grade_hold(m, p_aux, v_kmh=60.0, grade=0.06,
                                cda=None, rho=None):
    cda0, rho0 = VEH.CdA, VEH.rho_air
    if cda is not None:
        object.__setattr__(VEH, "CdA", cda)
    if rho is not None:
        object.__setattr__(VEH, "rho_air", rho)
    v = v_kmh / 3.6
    pw = float(vp.road_load_force(np.array([v]), np.array([grade]), m)[0][0]) * v
    shaft = pw / DL.eta_series_total + p_aux / DL.eta_gen
    object.__setattr__(VEH, "CdA", cda0)
    object.__setattr__(VEH, "rho_air", rho0)
    return shaft


floor = {}
for mlbl, mval in (("curb", VEH.m_curb_operating),
                   ("GVW", VEH.m_gvw),
                   ("+20%_payload", VEH.m_curb_operating + 1.2 * pay)):
    for albl, aval in (("aux2kW", AUX.p_aux_nom), ("aux4kW", AUX.p_aux_high),
                       ("aux6kW", 6000.0)):
        for clbl, cval in (("CdA4.2", 4.2), ("CdA4.8", 4.8), ("CdA5.4", 5.4)):
            req = genset_shaft_for_grade_hold(mval, aval, cda=cval)
            # and the speed a 110 kW engine actually holds in that condition
            cda0 = VEH.CdA
            object.__setattr__(VEH, "CdA", cval)
            vhold = steady_speed_for_wheel_power(
                (CTL.genset_v2_floor * DL.eta_gen - aval) * DL.eta_bus_to_wheel,
                0.06, mval) * 3.6
            object.__setattr__(VEH, "CdA", cda0)
            floor[f"{mlbl}_{albl}_{clbl}"] = {
                "engine_shaft_required_kW": kw(req),
                "margin_on_110kW_kW": 110.0 - kw(req),
                "speed_held_by_110kW_kmh": vhold,
            }
R["sensitivity"]["grade_floor_6pct_60kmh"] = floor

# ---- 4m robustness of the "direct path cannot hold 6%" conclusion
#      against alternative engine full-load curves
RPM_PTS = np.array(ENG.rpm_pts, float)
ALT_CURVES = {
    "WS1_baseline_4HK1": np.array(ENG.trq_pts, float),
    # 700 Nm held flat from 1,200 rpm - the most low-end-rich curve that
    # still honours the baseline's "700 Nm @ 1,600 rpm" anchor
    "flat_700Nm_from_1200": np.array([450, 660, 700, 700, 700, 700,
                                      700, 660, 610, 550, 490, 430], float),
    # torque peak moved below the anchor (750 Nm @ 1,400)
    "lowend_rich_750Nm_at_1400": np.array([460, 650, 720, 750, 700, 690,
                                           670, 645, 605, 550, 490, 430], float),
    # high-rpm-biased: less below 1,600, ~155 kW peak at 2,600
    "highrpm_biased": np.array([330, 480, 580, 660, 700, 710,
                                705, 690, 650, 570, 510, 450], float),
}
alt = {}
vs2 = np.linspace(9.0, 30.0, 2200)
for nm_c, trq_alt in ALT_CURVES.items():
    rpm_alt = vs2 / VEH.r_dyn * VEH.fd_ratio * 60 / (2 * np.pi)
    tq_alt = np.where(rpm_alt < ENG.idle_rpm, 0.0,
                      np.interp(rpm_alt, RPM_PTS, trq_alt))
    p_dir_alt = tq_alt * rpm_alt * 2 * np.pi / 60.0 * DL.eta_direct
    need = np.array([float(vp.road_load_force(np.array([x]), np.array([0.06]),
                                              VEH.m_gvw)[0][0]) * x for x in vs2])
    ok_ = p_dir_alt >= need
    gmax = np.array([grade_holdable(p_dir_alt[i] / vs2[i], vs2[i])
                     for i in range(vs2.size)])
    j = int(np.argmax(gmax))
    alt[nm_c] = {
        "peak_power_kW": kw(float(np.max(trq_alt * RPM_PTS * 2 * np.pi / 60.0))),
        "torque_at_1600rpm_Nm": float(np.interp(1600, RPM_PTS, trq_alt)),
        "holds_6pct_anywhere": bool(ok_.any()),
        "speed_range_holding_6pct_kmh": ([float(vs2[ok_].min() * 3.6),
                                          float(vs2[ok_].max() * 3.6)]
                                         if ok_.any() else None),
        "best_grade_pct": 100 * float(gmax[j]),
        "at_speed_kmh": float(vs2[j] * 3.6),
        "min_deficit_kW": kw(float(np.min(need - p_dir_alt))),
    }
R["sensitivity"]["direct_path_vs_engine_curve"] = alt

# ---- 4n road-load-coefficient sensitivity (CdA and air density)
rl = {}
_CdA0, _rho0 = VEH.CdA, VEH.rho_air
for cda in (4.2, 4.8, 5.4):
    for rho in (1.20, 1.225):
        object.__setattr__(VEH, "CdA", cda)
        object.__setattr__(VEH, "rho_air", rho)
        PA = vp.wheel_power(cycA["t"], cycA["v"], cycA["grade"], VEH.m_gvw)["P_wheel"]
        PB = vp.wheel_power(cycB["t"], cycB["v"], cycB["grade"], VEH.m_gvw)["P_wheel"]
        mA = vp.cycle_metrics(cycA["t"], cycA["v"], cycA["grade"], PA)
        mB = vp.cycle_metrics(cycB["t"], cycB["v"], cycB["grade"], PB)
        p85 = float(vp.road_load_force(np.array([85 / 3.6]), np.array([0.0]),
                                       VEH.m_gvw)[0][0]) * 85 / 3.6
        rl[f"CdA{cda}_rho{rho}"] = {
            "cruise85_wheel_kW": kw(p85),
            "SUB_E_per_km_kWh": mA["E_per_km_kWh"],
            "REG_E_per_km_kWh": mB["E_per_km_kWh"],
            "REG_P95_kW": mB["P95_kW"],
            "REG_peak_kW": mB["P_peak_kW"],
            "V2_6pct_hold_speed_kmh":
                steady_speed_for_wheel_power(
                    (CTL.genset_v2_floor * DL.eta_gen - AUX.p_aux_nom)
                    * DL.eta_bus_to_wheel, 0.06) * 3.6,
        }
object.__setattr__(VEH, "CdA", _CdA0)
object.__setattr__(VEH, "rho_air", _rho0)
R["sensitivity"]["road_load_coefficients"] = rl

# ---- 4o VOLT-REG composition: how "mixed" is it really?
bands = [(0, 5, "stationary"), (5, 50, "urban 5-50"), (50, 80, "rural 50-80"),
         (80, 101, "highway 80-100")]
vb = cycB["v"] * 3.6
dsB = cycB["v"] * 0.1
comp = {}
for lo, hi, lbl in bands:
    m_ = (vb >= lo) & (vb < hi)
    comp[lbl] = {"time_pct": float(m_.mean() * 100),
                 "distance_pct": float(dsB[m_].sum() / dsB.sum() * 100),
                 "distance_km": float(dsB[m_].sum() / 1000.0)}
R["cycle_composition_VOLT-REG"] = comp
vaA = cycA["v"] * 3.6; dsA = cycA["v"] * 0.1
R["cycle_composition_VOLT-SUB"] = {
    lbl: {"time_pct": float(((vaA >= lo) & (vaA < hi)).mean() * 100),
          "distance_pct": float(dsA[(vaA >= lo) & (vaA < hi)].sum() / dsA.sum() * 100)}
    for lo, hi, lbl in bands}

# ---- 4p where does the braking energy actually come from?
for c, nm_ in ((cycA, "VOLT-SUB"), (cycB, "VOLT-REG")):
    a_ = c["res"]["a"]; P_ = c["P"]
    neg = P_ < 0
    decel = neg & (a_ < -0.15)          # the driver is slowing down
    hold = neg & (a_ >= -0.15)          # steady speed, gravity doing the work
    tot = -vp.trapz(np.clip(P_, None, 0), c["t"])
    R.setdefault("braking_attribution", {})[nm_] = {
        "total_kWh": tot / 3.6e6,
        "from_decelerations_kWh": -vp.trapz(np.where(decel, P_, 0.0), c["t"]) / 3.6e6,
        "from_steady_downgrade_kWh": -vp.trapz(np.where(hold, P_, 0.0), c["t"]) / 3.6e6,
        "decel_share": (-vp.trapz(np.where(decel, P_, 0.0), c["t"])) / tot,
    }

# ---- 4q genset rating basis: electrical output vs engine shaft
_need_shaft = R["baseline_crosscheck"]["grade6_at_60kmh_engine_shaft_plus_aux_kW"]
_need_elec = R["baseline_crosscheck"]["grade6_at_60kmh_bus_kW"] + AUX.p_aux_nom / 1e3
R["genset_rating_basis"] = {
    "requirement_engine_shaft_kW": _need_shaft,
    "requirement_electrical_at_bus_kW": _need_elec,
    "if_baseline_110kW_is_engine_shaft": {
        "margin_kW": 110.0 - _need_shaft,
        "hold_speed_on_6pct_kmh": steady_speed_for_wheel_power(
            (110e3 * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel, 0.06) * 3.6},
    "if_baseline_110kW_is_electrical_output": {
        "margin_kW": 110.0 - _need_elec,
        "hold_speed_on_6pct_kmh": steady_speed_for_wheel_power(
            (110e3 - AUX.p_aux_nom) * DL.eta_bus_to_wheel, 0.06) * 3.6},
    "note": ("The baseline does not state whether '110 kW' is engine shaft "
             "power or generator electrical output. WS1 has taken it as "
             "engine shaft (the conservative reading). WS4 must pin this "
             "down; the two readings differ by ~6 kW of engine."),
}

# --------------------------------- Number 4 as an envelope, not a draw
# The single hardest stop in one route realisation is a random variable, so
# the reference cycle's peak regen is reported together with the spread over
# the seed ensemble and over the braking-style sweep, and the design number
# is the maximum of all of them.
_ens = R["sensitivity"]["seed_ensemble"]
_db = R["sensitivity"]["driver_braking"]
R["N4_envelope"] = {
    "VOLT-SUB": {
        "reference_realisation_kW": R["cycles"]["VOLT-SUB"]["P_regen_peak_wheel_kW"],
        "seed_ensemble_min_max_kW": [_ens["VOLT-SUB"]["N4_peak_regen_wheel_kW"]["min"],
                                     _ens["VOLT-SUB"]["N4_peak_regen_wheel_kW"]["max"]],
        "braking_style_0.9_to_1.6_ms2_kW": [_db["a_brake_0.9"]["P_regen_peak_wheel_kW"],
                                            _db["a_brake_1.6"]["P_regen_peak_wheel_kW"]],
        "design_envelope_kW": max(R["cycles"]["VOLT-SUB"]["P_regen_peak_wheel_kW"],
                                  _ens["VOLT-SUB"]["N4_peak_regen_wheel_kW"]["max"],
                                  _db["a_brake_1.6"]["P_regen_peak_wheel_kW"]),
    },
    "VOLT-REG": {
        "reference_realisation_kW": R["cycles"]["VOLT-REG"]["P_regen_peak_wheel_kW"],
        "seed_ensemble_min_max_kW": [_ens["VOLT-REG"]["N4_peak_regen_wheel_kW"]["min"],
                                     _ens["VOLT-REG"]["N4_peak_regen_wheel_kW"]["max"]],
        "design_envelope_kW": max(R["cycles"]["VOLT-REG"]["P_regen_peak_wheel_kW"],
                                  _ens["VOLT-REG"]["N4_peak_regen_wheel_kW"]["max"]),
    },
}


# ---- 4r engine speed/load residency on the V2 locked path.
# The whole justification for the direct path is 95% mechanical vs 81.4%
# series. That comparison is only valid if the engine is equally efficient
# at both operating points, and a single fixed ratio guarantees it is not:
# in lockup the crank speed is set by the road, so the engine runs wherever
# the road puts it.
_lk = locked & (cycB["v"] > 1.0)
_rpm_l = rpm[_lk]
_shaft_l = (p_dir[_lk] / DL.eta_direct
            + fnB["N2_genset_const_bus_kW"] * 1e3 / DL.eta_gen)
_cap_l = np.array([float(vp.direct_path_wheel_power_max(np.array([x]))[1][0])
                   for x in cycB["v"][_lk]])
_load_l = np.clip(_shaft_l / np.maximum(_cap_l, 1.0), 0, 1.5)
dt_ = 0.1
R["engine_residency_V2_locked"] = {
    "locked_time_s": float(_lk.sum() * dt_),
    "rpm_p05_p50_p95": [float(np.percentile(_rpm_l, q)) for q in (5, 50, 95)],
    "shaft_kW_p05_p50_p95": [kw(float(np.percentile(_shaft_l, q))) for q in (5, 50, 95)],
    "load_fraction_p05_p50_p95": [float(np.percentile(_load_l, q)) for q in (5, 50, 95)],
    "time_below_30pct_load": float(np.mean(_load_l < 0.30) * 100),
    "time_below_50pct_load": float(np.mean(_load_l < 0.50) * 100),
    "time_above_80pct_load": float(np.mean(_load_l > 0.80) * 100),
    "at_fixed_speeds": {
        f"{vk}kmh": {
            "rpm": float(vp.engine_rpm_from_speed(np.array([vk / 3.6]))[0]),
            "shaft_needed_kW": kw(float(vp.road_load_force(
                np.array([vk / 3.6]), np.array([0.0]), VEH.m_gvw)[0][0])
                * (vk / 3.6) / DL.eta_direct),
            "shaft_available_kW": kw(float(vp.direct_path_wheel_power_max(
                np.array([vk / 3.6]))[1][0])),
        } for vk in (60, 70, 85, 100)},
    "note": ("A free-running genset can be pinned to its BSFC island by "
             "definition. The locked direct path cannot. WS1 does not own a "
             "BSFC map, so the 95% vs 81.4% comparison is a COMPONENT "
             "efficiency argument that assumes equal engine efficiency at "
             "both operating points - an assumption the fixed ratio makes "
             "false. WS4 must settle it before the direct path is treated "
             "as a decided advantage."),
}
for k, d in R["engine_residency_V2_locked"]["at_fixed_speeds"].items():
    d["load_fraction"] = d["shaft_needed_kW"] / d["shaft_available_kW"]

# ---- 4s part-load efficiency sensitivity.
# Every efficiency in volt_params is a single peak-point scalar, and the
# study's own results put both machines at part load for most of the cycle.
def part_load_factor(p_frac, floor_=0.88, knee=0.5):
    """Crude derate: full efficiency above `knee` of rating, falling
    linearly to `floor_` x nominal at 5% load. [WS1-ASSUMPTION]"""
    x = np.clip(np.asarray(p_frac, float), 0.0, 1.0)
    return np.where(x >= knee, 1.0,
                    floor_ + (1.0 - floor_) * np.clip((x - 0.05) /
                                                      (knee - 0.05), 0, 1))


pl = {}
for lbl, (mot_rated, gen_rated) in (("V1_VOLT-SUB", (110e3, 50e3 * DL.eta_gen)),
                                    ("V2_VOLT-REG", (150e3, 110e3 * DL.eta_gen))):
    c = cycA if lbl.endswith("SUB") else cycB
    pdx = None if lbl.endswith("SUB") else p_dir
    p_mot_wheel = c["P"] - (0.0 if pdx is None else pdx)
    frac = np.abs(p_mot_wheel) / mot_rated
    k = part_load_factor(frac)
    # traction: worse chain when the motor is lightly loaded
    eta_pos = DL.eta_bus_to_wheel * k
    e_bus_ideal = vp.trapz(np.clip(p_mot_wheel, 0, None) / DL.eta_bus_to_wheel, c["t"])
    e_bus_pl = vp.trapz(np.clip(p_mot_wheel, 0, None) / eta_pos, c["t"])
    _, p_capt_pl, _ = vp.regen_split(c["v"], p_mot_wheel, CTL.regen_cap_wheel)
    e_rg_ideal = vp.trapz(p_capt_pl * DL.eta_wheel_to_bus, c["t"])
    e_rg_pl = vp.trapz(p_capt_pl * DL.eta_wheel_to_bus * k, c["t"])
    T = c["t"][-1]
    p2_ideal = (e_bus_ideal - e_rg_ideal) / T + AUX.p_aux_nom
    p2_pl = (e_bus_pl - e_rg_pl) / T + AUX.p_aux_nom
    # genset itself also runs part load
    kg = float(part_load_factor(np.array([p2_pl / gen_rated]))[0])
    pl[lbl] = {
        "motor_time_below_25pct_rating_pct": float(np.mean(frac < 0.25) * 100),
        "bus_energy_ideal_kWh": e_bus_ideal / 3.6e6,
        "bus_energy_partload_kWh": e_bus_pl / 3.6e6,
        "traction_energy_penalty_pct": 100 * (e_bus_pl / e_bus_ideal - 1),
        "regen_to_bus_ideal_kWh": e_rg_ideal / 3.6e6,
        "regen_to_bus_partload_kWh": e_rg_pl / 3.6e6,
        "genset_bus_avg_ideal_kW": kw(p2_ideal),
        "genset_bus_avg_partload_kW": kw(p2_pl),
        "genset_shaft_ideal_kW": kw(p2_ideal / DL.eta_gen),
        "genset_shaft_partload_kW": kw(p2_pl / DL.eta_gen / kg),
        "genset_shaft_penalty_pct": 100 * ((p2_pl / kg) / p2_ideal - 1),
    }
R["sensitivity"]["part_load_efficiency"] = pl

# ---- 4t environmental envelope (the Four Numbers are otherwise quoted at
#      one implied ambient)
env = {}
for lbl, (cap, aux_) in (("nominal", (CTL.regen_cap_wheel, AUX.p_aux_nom)),
                         ("cold_regen_disabled_aux4kW", (0.0, AUX.p_aux_high)),
                         ("cold_regen_25pct_aux6kW", (18.75e3, 6000.0)),
                         ("hot_regen_40kW_aux4kW", (40e3, AUX.p_aux_high))):
    row = {}
    for c, pdx, nm_ in ((cycA, None, "VOLT-SUB_V1"), (cycB, p_dir, "VOLT-REG_V2")):
        fn = vv.four_numbers(c["t"], c["v"], c["P"], p_wheel_direct=pdx,
                             p_aux=aux_, cap_wheel=cap)
        _, pcap, pfric = vp.regen_split(c["v"], c["P"], cap)
        row[nm_] = {
            "N2_genset_const_bus_kW": fn["N2_genset_const_bus_kW"],
            "N3_buffer_5min_kWh": fn["N3_buffer_5min_kWh"],
            "friction_brake_energy_kWh": vp.trapz(pfric, c["t"]) / 3.6e6,
            "regen_to_bus_kWh": vp.trapz(pcap, c["t"]) * DL.eta_wheel_to_bus / 3.6e6,
        }
    env[lbl] = row
R["sensitivity"]["environment"] = env

# ---- 4u driven-axle adhesion. Regen and launch both act through ONE axle.
def mu_required(force_N, m, a_ms2, rear_share, h_cg, grade=0.0, veh=VEH):
    """Friction coefficient the driven axle needs. Braking transfers load
    OFF the rear (a<0 convention: pass a>0 for decel)."""
    N_static = m * G * rear_share * math.cos(math.atan(grade))
    dN = m * a_ms2 * h_cg / veh.wheelbase
    return force_N / max(N_static - dN, 1.0)


adh = {}
for mlbl, mval, share, hcg in (("GVW", VEH.m_gvw, VEH.rear_axle_share_gvw, VEH.h_cg_loaded),
                               ("curb", VEH.m_curb_operating, VEH.rear_axle_share_curb, VEH.h_cg_empty)):
    Pm = vp.wheel_power(cycA["t"], cycA["v"], cycA["grade"], mval)["P_wheel"]
    _, pcap, _ = vp.regen_split(cycA["v"], Pm, CTL.regen_cap_wheel)
    f_regen = pcap / np.maximum(cycA["v"], 0.5)
    a_dec = np.clip(-vp.wheel_power(cycA["t"], cycA["v"], cycA["grade"], mval)["a"], 0, None)
    mu = np.array([mu_required(f_regen[i], mval, a_dec[i], share, hcg)
                   for i in range(0, f_regen.size, 5)])
    adh[mlbl] = {
        "peak_regen_force_at_wheel_N": float(np.max(f_regen)),
        "mu_required_peak": float(np.max(mu)),
        "mu_required_p99": float(np.percentile(mu, 99)),
        "launch_13.5kN_flat_mu": mu_required(VEH.F_trac_max, mval,
                                             -VEH.F_trac_max / (1.04 * mval),
                                             share, hcg),
        "launch_13.5kN_on_20pct_grade_mu": mu_required(
            VEH.F_trac_max, mval, -1.0, share, hcg, 0.20),
    }
R["sensitivity"]["driven_axle_adhesion"] = adh

# ---- 4v heat rejection at the sizing point (6% grade hold, V2 series).
# Section 1.2 flags that the 2 kW accessory budget contains no thermal
# management; this is what it would have to cover.
_p_wheel_hold = (CTL.genset_v2_floor * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel
_p_bus_hold = CTL.genset_v2_floor * DL.eta_gen - AUX.p_aux_nom
R["thermal_at_grade_hold"] = {
    "condition": "V2 series, 6% grade, 61.0 km/h, ~10 minutes, GVW",
    "engine_shaft_kW": kw(CTL.genset_v2_floor),
    "generator_loss_kW": kw(CTL.genset_v2_floor * (1 - DL.eta_gen)),
    "power_electronics_loss_kW": kw(_p_bus_hold * (1 - DL.eta_pe)),
    "inverter_motor_loss_kW": kw(_p_bus_hold * DL.eta_pe * (1 - DL.eta_inv_mot)),
    "reduction_loss_kW": kw(_p_bus_hold * DL.eta_pe * DL.eta_inv_mot * (1 - DL.eta_red)),
    "total_electrical_chain_heat_kW": kw(
        CTL.genset_v2_floor * (1 - DL.eta_gen)
        + _p_bus_hold * (1 - DL.eta_pe * DL.eta_inv_mot * DL.eta_red)),
    "engine_heat_rejection_kW_approx": kw(CTL.genset_v2_floor * 0.9),
    "note": ("The electrical-chain heat goes into a low-temperature loop "
             "the donor vehicle does not have. Pumps and fans for it are "
             "themselves 1.5-3 kW off the same DC bus - and the 4 kW "
             "accessory case already consumes the whole 110 kW margin "
             "(sensitivity/grade_floor_6pct_60kmh). Unassigned: WS6."),
}

# ---- 4w V1's capability boundary, stated as a conclusion
_v1_wheel = (CTL.genset_v1_class * DL.eta_gen - AUX.p_aux_nom) * DL.eta_bus_to_wheel
_p85_wheel = float(vp.road_load_force(np.array([85 / 3.6]), np.array([0.0]),
                                      VEH.m_gvw)[0][0]) * 85 / 3.6
R["V1_capability_boundary"] = {
    "genset_class_kW_shaft": kw(CTL.genset_v1_class),
    "wheel_power_available_kW": kw(_v1_wheel),
    "charge_sustaining_top_speed_flat_GVW_kmh":
        steady_speed_for_wheel_power(_v1_wheel, 0.0) * 3.6,
    "shaft_needed_for_85kmh_kW": kw(_p85_wheel / DL.eta_series_total
                                    + AUX.p_aux_nom / DL.eta_gen),
    "shaft_needed_for_VOLT-REG_cycle_average_kW": kw(
        R["cycles"]["VOLT-REG"]["P_avg_tractive_kW"] * 1e3 / DL.eta_series_total
        + AUX.p_aux_nom / DL.eta_gen),
    "note": ("A 50 kW-class V1 cannot charge-sustain at the programme's own "
             "85 km/h design point, and cannot even meet VOLT-REG's cycle "
             "AVERAGE tractive demand in any battery state. V1 is a "
             "sub-80 km/h vehicle; that has to be written down."),
}

# ------------------------------------------- genset duty cycling (WS4/WS5)
def genset_cycling(p_avg_kw, buffer_kwh, p_on_kw, ramp_s=4.0):
    """If the genset refuses part-load and instead runs at a fixed
    BSFC-optimal point P_on and stops otherwise, how often does it start?

    `ramp_s` is the load-acceptance transient of a turbocharged diesel
    driving a generator [WS1-ASSUMPTION]. During the ramp the genset
    averages roughly half its setpoint, so the buffer covers the shortfall;
    that energy is charged to nobody in the idealised version.
    """
    if p_on_kw <= p_avg_kw:
        return None
    t_on = buffer_kwh * 3600.0 / (p_on_kw - p_avg_kw)
    t_off = buffer_kwh * 3600.0 / p_avg_kw
    per_h = 3600.0 / (t_on + t_off)
    ramp_kwh = 0.5 * p_on_kw * ramp_s / 3600.0        # per start
    return {"on_s": t_on, "off_s": t_off, "duty": t_on / (t_on + t_off),
            "starts_per_hour": per_h, "starts_per_8h_shift": per_h * 8,
            "starts_per_year_250d": per_h * 8 * 250,
            "ramp_energy_per_start_kWh": ramp_kwh,
            "ramp_buffer_adder_kWh": ramp_kwh,
            "ramp_energy_per_hour_kWh": ramp_kwh * per_h}


_v1n = R["four_numbers"]["V1_postal_VOLT-SUB"]
R["genset_duty_cycling_V1"] = {
    f"P_on_{po}kW_buffer_{bf}kWh": genset_cycling(_v1n["N2_genset_const_bus_kW"], bf, po)
    for po in (25, 35, 47) for bf in (0.7, 1.5, 3.0)}
R["genset_duty_cycling_V1"]["note"] = (
    "V1's cycle-average bus load is only "
    f"{_v1n['N2_genset_const_bus_kW']:.1f} kW against a ~50 kW installed "
    "genset. Either the genset runs at ~20% load (bad BSFC) or it "
    "start-stops, and the start count is set by the buffer size.")

# --------------------------------------- clutch engagement duty (V2, WS5)
_sw = np.diff(locked.astype(int))
R["clutch_duty_V2_VOLT-REG"] = {
    "engagements_per_cycle": int(np.sum(_sw > 0)),
    "engagements_per_100km": float(np.sum(_sw > 0)) /
                             (R["cycles"]["VOLT-REG"]["distance_km"] / 100.0),
    "locked_time_frac": float(np.mean(locked)),
    "locked_distance_frac": float(vp.trapz(locked * cycB["v"], cycB["t"]) /
                                  vp.trapz(cycB["v"], cycB["t"])),
    "sync_rpm_at_handover": float(vp.engine_rpm_from_speed(
        np.array([CTL.v_lockup]))[0]),
    # generator spin-up work: engine+flywheel I ~ 0.6 kg.m^2 [WS1-ASSUMPTION]
    "spin_up_kinetic_energy_kJ": 0.5 * 0.6 * (
        (CTL.v_lockup / VEH.r_dyn * VEH.fd_ratio) ** 2 -
        (ENG.idle_rpm * 2 * np.pi / 60) ** 2) / 1e3,
    "spin_up_power_kW_over_0.5s": 0.5 * 0.6 * (
        (CTL.v_lockup / VEH.r_dyn * VEH.fd_ratio) ** 2 -
        (ENG.idle_rpm * 2 * np.pi / 60) ** 2) / 0.5 / 1e3,
    "motoring_drag_power_kW_at_sync": 60.0 * (CTL.v_lockup / VEH.r_dyn *
                                              VEH.fd_ratio) / 1e3,
}

# ---------------------------------------------------------------- envelope
R["motor_envelope"] = {}
for c, pdx, lbl in ((cycA, None, "VOLT-SUB_V1"),
                    (cycB, p_dir, "VOLT-REG_V2_iMMD"),
                    (cycB, None, "VOLT-REG_V2_series_only")):
    p_mot_raw = c["P"] - (0.0 if pdx is None else pdx)
    # the machine only absorbs the capped, blended share of braking
    _, _p_capt, _ = vp.regen_split(c["v"], p_mot_raw, CTL.regen_cap_wheel)
    p_mot_wheel = np.where(p_mot_raw >= 0, p_mot_raw, -_p_capt)
    p_shaft = vp.motor_shaft_power(p_mot_wheel)
    p_shaft_unc = vp.motor_shaft_power(p_mot_raw)
    w_shaft = c["v"] / VEH.r_dyn * VEH.motor_ratio          # rad/s
    # torque from FORCE, not P/omega, so the launch region (highest torque,
    # lowest speed) is retained rather than divided away
    f_mot = np.where(p_mot_wheel >= 0,
                     p_mot_wheel / np.maximum(c["v"], 1e-3) / DL.eta_red,
                     p_mot_wheel / np.maximum(c["v"], 1e-3) * DL.eta_red)
    f_mot = np.where(c["v"] > 0.05, f_mot, 0.0)
    trq = f_mot * VEH.r_dyn / VEH.motor_ratio
    R["motor_envelope"][lbl] = {
        "max_shaft_speed_rpm": float(np.max(w_shaft)) * 60 / (2 * np.pi),
        "max_motoring_torque_Nm": float(np.max(trq)),
        "max_braking_torque_Nm": float(-np.min(trq)),
        "T_rms_Nm": float(np.sqrt(np.mean(trq ** 2))),
        "max_motoring_kW": float(np.max(p_shaft)) / 1e3,
        "max_braking_kW_capped": float(-np.min(p_shaft)) / 1e3,
        "max_braking_kW_uncapped_demand": float(-np.min(p_shaft_unc)) / 1e3,
        "torque_at_stall_spec_Nm": VEH.F_trac_max * VEH.r_dyn /
                                   VEH.motor_ratio / DL.eta_red,
    }

R["buffer_vs_window"] = {
    "VOLT-SUB_V1": R["four_numbers"]["V1_postal_VOLT-SUB"]["N3_buffer_by_window"],
    "VOLT-REG_V2_iMMD": R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]["N3_buffer_by_window"],
    "VOLT-REG_V2_series_only": R["four_numbers"]["V2_trucker_VOLT-REG_series_only"]["N3_buffer_by_window"],
}

# ---- V2 total prime-mover average power over VOLT-REG
_fn = R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]
_fn["N2_engine_total_avg_shaft_kW"] = (_fn["N2_genset_engine_shaft_kW"] +
                                       _fn["N2_engine_direct_avg_shaft_kW"])
_fn["E_engine_total_kWh"] = (_fn["N2_engine_total_avg_shaft_kW"] *
                             R["cycles"]["VOLT-REG"]["duration_s"] / 3600.0)

# ------------------------------------------------- consolidated requirements
# This block is the machine-readable interface WS2-WS4 will parse, so it
# must agree with the report's prose. In particular: extremum-derived
# requirements are taken from the SEED ENSEMBLE (a single realisation is a
# draw, not a requirement), the governing buffer excludes the case the
# report declares unachievable, and battery energies are given at the CELLS
# as well as at the DC bus.
_v1 = R["four_numbers"]["V1_postal_VOLT-SUB"]
_v2 = R["four_numbers"]["V2_trucker_VOLT-REG_iMMD"]
_v2s = R["four_numbers"]["V2_trucker_VOLT-REG_series_only"]
_gh = R["sensitivity"]["sustained_series_duty"]
_ensA = R["sensitivity"]["seed_ensemble"]["VOLT-SUB"]
_ensB = R["sensitivity"]["seed_ensemble"]["VOLT-REG"]
_dsc = R["sensitivity"]["descent_10km_6pc"]
_e4_no_brake = _dsc["thermal"]["buffer3.0kWh_60kmh_no_engine_brake"]
_climb85 = R["sensitivity"]["climb_10km_6pc"]["hold_85kmh_V2"]

# buffer needed to take the 10 km 6% descent at 60 km/h with a 30 kW
# exhaust brake and no friction braking (the achievable version of E4)
_v_d = 60 / 3.6
_f_d = float(vp.road_load_force(np.array([_v_d]), np.array([-0.06]), VEH.m_gvw)[0][0])
_p_ret = -_f_d * _v_d
_into = max(1.0, ((_p_ret - 30e3) * DL.eta_wheel_to_bus - AUX.p_aux_nom)
            * DL.eta_batt_chg)
_buf_desc_exhaust = _into * (10000.0 / _v_d) / 3.6e6 / 0.45
_into_no = max(1.0, (min(_p_ret, CTL.regen_cap_wheel) * DL.eta_wheel_to_bus
                     - AUX.p_aux_nom) * DL.eta_batt_chg)
_buf_desc_none = _into_no * (10000.0 / _v_d) / 3.6e6 / 0.45

R["requirements_summary"] = {
    "_basis": ("Extremum-derived numbers are the MAXIMUM over an 8-member "
               "seed ensemble that includes the published reference cycle, "
               "not the reference draw. Sustained-duty numbers are "
               "closed-form. See REPORT_WS1.md sections 3.1, 4.8 and 5."),
    "motor_continuous_kW_shaft": {
        "cycle_RMS_V1_VOLT-SUB": _v1["N1_motor_rms_shaft_kW"],
        "cycle_RMS_V2_VOLT-REG_iMMD": _v2["N1_motor_rms_shaft_kW"],
        "cycle_RMS_V2_VOLT-REG_series_only": _v2s["N1_motor_rms_shaft_kW"],
        "worst_300s_rolling_RMS_any_case": max(
            _v1["N1_rolling_rms_shaft_kW"]["300s"],
            _v2["N1_rolling_rms_shaft_kW"]["300s"],
            _v2s["N1_rolling_rms_shaft_kW"]["300s"]),
        "RMS_torque_Nm": {"V1_VOLT-SUB": _v1["N1_motor_rms_torque_Nm"],
                          "V2_VOLT-REG_iMMD": _v2["N1_motor_rms_torque_Nm"],
                          "V2_VOLT-REG_series": _v2s["N1_motor_rms_torque_Nm"]},
        "grade_hold_6pct_V2_series_10min_kW": _gh["V2_genset_110kW"]["grade_6pct"]["motor_shaft_kW"],
        "grade_hold_6pct_V2_series_10min_Nm": _gh["V2_genset_110kW"]["grade_6pct"]["motor_torque_Nm_at_shaft"],
        "grade_hold_6pct_V1_series_kW": _gh["V1_genset_50kW"]["grade_6pct"]["motor_shaft_kW"],
        "grade_crawl_20pct_torque_Nm": _gh["V2_genset_110kW"]["grade_20pct"]["motor_torque_Nm_at_shaft"],
        "RECOMMENDED_S1_kW": 45.0, "RECOMMENDED_S1_Nm": 180.0,
        "RECOMMENDED_S2_10min_kW": 95.0, "RECOMMENDED_S2_10min_Nm": 200.0,
        "note_fault_mode": ("If the spine must also survive a clutch-open "
                            "fault on VOLT-REG, S2-10min rises to "
                            f"{_v2s['N1_rolling_rms_shaft_kW']['300s']:.0f} kW. "
                            "Undecided - see REPORT_WS1.md E24."),
    },
    "motor_peak_kW_shaft": {
        "VOLT-SUB_V1": _v1["motor_peak_motoring_shaft_kW"],
        "VOLT-REG_V2_iMMD": _v2["motor_peak_motoring_shaft_kW"],
        "VOLT-REG_V2_series_only": _v2s["motor_peak_motoring_shaft_kW"],
        "max_shaft_speed_rpm": R["motor_envelope"]["VOLT-REG_V2_iMMD"]["max_shaft_speed_rpm"],
        "stall_torque_spec_Nm": R["motor_envelope"]["VOLT-SUB_V1"]["torque_at_stall_spec_Nm"],
        "generating_envelope_kW": R["motor_envelope"]["VOLT-SUB_V1"]["max_braking_kW_capped"],
        "generating_envelope_Nm": R["motor_envelope"]["VOLT-SUB_V1"]["max_braking_torque_Nm"],
        "baseline_provisional": 75.0,
        "RECOMMENDED_kW": 120.0, "RECOMMENDED_TARGET_kW": 150.0,
    },
    "genset_kW": {
        "V1_cycle_average_bus": _v1["N2_genset_const_bus_kW"],
        "V1_cycle_average_engine_shaft": _v1["N2_genset_engine_shaft_kW"],
        "V1_charge_sustaining_top_speed_kmh":
            R["V1_capability_boundary"]["charge_sustaining_top_speed_flat_GVW_kmh"],
        "V1_shaft_needed_for_85kmh": R["V1_capability_boundary"]["shaft_needed_for_85kmh_kW"],
        "V2_cycle_average_engine_shaft_total": _v2["N2_engine_total_avg_shaft_kW"],
        "V2_series_only_cycle_average_bus": _v2s["N2_genset_const_bus_kW"],
        "V1_baseline_class": 50.0,
        "V2_baseline_floor": 110.0,
        "V2_floor_recomputed_engine_shaft_at_GVW_2kW_aux":
            R["baseline_crosscheck"]["grade6_at_60kmh_engine_shaft_plus_aux_kW"],
        "V2_floor_at_+20pct_payload_2kW_aux":
            R["sensitivity"]["grade_floor_6pct_60kmh"]["+20%_payload_aux2kW_CdA4.2"]["engine_shaft_required_kW"],
        "V2_floor_at_GVW_4kW_aux":
            R["sensitivity"]["grade_floor_6pct_60kmh"]["GVW_aux4kW_CdA4.2"]["engine_shaft_required_kW"],
        "V2_floor_at_GVW_2kW_aux_CdA5.4":
            R["sensitivity"]["grade_floor_6pct_60kmh"]["GVW_aux2kW_CdA5.4"]["engine_shaft_required_kW"],
        "rating_basis": "engine shaft (see genset_rating_basis)",
    },
    "battery_buffer_kWh": {
        "_note": ("'usable' is at the DC bus; the cell-side figure divides "
                  "by the 0.97 discharge factor. The 85 km/h grade-hold case "
                  "is EXCLUDED because REPORT_WS1.md section 4.4 shows it is "
                  "not achievable - the truck derates to 61 km/h instead."),
        "cycle_5min_VOLT-SUB_V1_reference": _v1["N3_buffer_5min_kWh"],
        "cycle_5min_VOLT-SUB_V1_ensemble_max": _ensA["N3_buffer_5min_kWh"]["max"],
        "cycle_5min_VOLT-REG_V2_reference": _v2["N3_buffer_5min_kWh"],
        "cycle_5min_VOLT-REG_V2_ensemble_max": _ensB["N3_buffer_5min_kWh"]["max"],
        "cycle_5min_VOLT-REG_V2_series_only": _v2s["N3_buffer_5min_kWh"],
        "whole_cycle_single_setpoint_VOLT-REG_V2": _v2["N3_buffer_fullcycle_kWh"],
        "descent_10km_6pct_60kmh_with_30kW_exhaust_brake": _buf_desc_exhaust,
        "descent_10km_6pct_60kmh_no_engine_braking": _buf_desc_none,
        "genset_start_stop_20_per_shift": 3.0,
        "EXCLUDED_hold_85kmh_on_6pct_not_achievable_bus":
            _climb85["battery_energy_at_bus_kWh"],
        "GOVERNING_at_bus": max(_ensB["N3_buffer_5min_kWh"]["max"],
                                _buf_desc_exhaust, 3.0),
        "GOVERNING_at_cells": max(_ensB["N3_buffer_5min_kWh"]["max"],
                                  _buf_desc_exhaust, 3.0) / DL.eta_batt_dis,
        "RECOMMENDED_usable_V2_at_bus": 3.5,
        "RECOMMENDED_usable_V1_at_bus": 1.5,
    },
    "peak_regen_kW": {
        "VOLT-SUB_reference_draw": _v1["N4_peak_regen_wheel_kW"],
        "VOLT-REG_reference_draw": _v2["N4_peak_regen_wheel_kW"],
        "VOLT-SUB_DESIGN_ENVELOPE": R["N4_envelope"]["VOLT-SUB"]["design_envelope_kW"],
        "VOLT-REG_DESIGN_ENVELOPE": R["N4_envelope"]["VOLT-REG"]["design_envelope_kW"],
        "absorbed_at_wheel_with_75kW_cap": CTL.regen_cap_wheel / 1e3,
        "absorbed_at_bus_with_75kW_cap": _v1["N4_peak_regen_bus_kW"],
        "friction_blend_authority_needed_VOLT-SUB":
            R["N4_envelope"]["VOLT-SUB"]["design_envelope_kW"] - CTL.regen_cap_wheel / 1e3,
        "friction_blend_authority_needed_VOLT-REG":
            R["N4_envelope"]["VOLT-REG"]["design_envelope_kW"] - CTL.regen_cap_wheel / 1e3,
        "battery_peak_charge_kW": max(_v1["batt_peak_chg_kW"], _v2["batt_peak_chg_kW"]),
        "battery_peak_discharge_kW": max(_v1["batt_peak_dis_kW"], _v2["batt_peak_dis_kW"]),
    },
    "peak_wheel_power_kW": {
        "VOLT-SUB_reference": R["cycles"]["VOLT-SUB"]["P_peak_kW"],
        "VOLT-SUB_ensemble_max": _ensA["P_peak_kW"]["max"],
        "VOLT-REG_reference": R["cycles"]["VOLT-REG"]["P_peak_kW"],
        "VOLT-REG_ensemble_max": _ensB["P_peak_kW"]["max"],
    },
    "validity_envelope": {
        "ambient": "NOT DECLARED - see sensitivity/environment and E21",
        "altitude": "sea level implied by rho_air = 1.20 kg/m^3",
        "efficiencies": "peak-point scalars; see sensitivity/part_load_efficiency and E22",
        "thermal_management": "excluded from the 2 kW accessory budget; see thermal_at_grade_hold",
    },
}

# =====================================================================
# 5. OUTPUT FILES
# =====================================================================
def write_cycle_csv(c, name, extra=None):
    step = 10   # 1 Hz export
    t, v, g, P = c["t"][::step], c["v"][::step], c["grade"][::step], c["P"][::step]
    s = c["s"][::step]
    hdr = "t_s,v_kmh,v_ms,grade_pct,dist_m,P_wheel_kW"
    cols = [t, v * 3.6, v, g * 100, s, P / 1e3]
    if extra:
        for k, arr in extra.items():
            hdr += "," + k
            cols.append(np.asarray(arr)[::step])
    np.savetxt(os.path.join(DATA, name), np.column_stack(cols),
               delimiter=",", header=hdr, comments="", fmt="%.4f")


# time-at-power histograms as CSV (task-2 deliverable)
for c in (cycA, cycB):
    e_, sec_ = vp.power_histogram(c["t"], c["P"], bin_w=10e3)
    with open(os.path.join(DATA, f"time_at_power_{c['name']}.csv"), "w") as f:
        f.write("bin_lo_kW,bin_hi_kW,seconds,pct_of_cycle_time\n")
        for lo, hi, sv in zip(e_[:-1], e_[1:], sec_):
            if sv > 1e-9:
                f.write(f"{lo/1e3:.0f},{hi/1e3:.0f},{sv:.2f},"
                        f"{sv/c['t'][-1]*100:.4f}\n")

# regen absorb-limit sweep as CSV
for nm in ("VOLT-SUB", "VOLT-REG"):
    with open(os.path.join(DATA, f"regen_sweep_{nm}.csv"), "w") as f:
        f.write("cap_kW,E_captured_mech_kWh,E_captured_elec_kWh,"
                "frac_of_braking_mech,frac_of_braking_elec\n")
        for r in R["regen_sensitivity"][nm]["rows"]:
            f.write(f"{r['cap_label']},{r['E_captured_mech_kWh']:.4f},"
                    f"{r['E_captured_elec_kWh']:.4f},"
                    f"{r['frac_of_braking_mech']:.4f},"
                    f"{r['frac_of_braking_elec']:.4f}\n")

write_cycle_csv(cycA, "cycle_VOLT-SUB_1Hz.csv")
write_cycle_csv(cycB, "cycle_VOLT-REG_1Hz.csv",
                extra={"P_direct_kW": p_dir / 1e3,
                       "lockup": locked.astype(float),
                       "eng_rpm_locked": rpm})

# 10 Hz full traces with the energy-management channels
emA = fnA["_em"]; emB = fnB["_em"]
np.savetxt(os.path.join(DATA, "trace_VOLT-SUB_V1_10Hz.csv"),
           np.column_stack([cycA["t"], cycA["v"] * 3.6, cycA["P"] / 1e3,
                            emA["p_bus"] / 1e3, emA["p_batt"] / 1e3,
                            emA["e_batt"] / 3.6e6, emA["p_capt"] / 1e3]),
           delimiter=",", fmt="%.4f", comments="",
           header="t_s,v_kmh,P_wheel_kW,P_bus_kW,P_batt_kW,E_batt_kWh,P_regen_capt_kW")
np.savetxt(os.path.join(DATA, "trace_VOLT-REG_V2_10Hz.csv"),
           np.column_stack([cycB["t"], cycB["v"] * 3.6, cycB["grade"] * 100,
                            cycB["P"] / 1e3, p_dir / 1e3,
                            emB["p_bus"] / 1e3, emB["p_batt"] / 1e3,
                            emB["e_batt"] / 3.6e6, emB["p_capt"] / 1e3]),
           delimiter=",", fmt="%.4f", comments="",
           header="t_s,v_kmh,grade_pct,P_wheel_kW,P_direct_kW,P_bus_kW,"
                  "P_batt_kW,E_batt_kWh,P_regen_capt_kW")

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(R, f, indent=1, default=float)

# ---- four-numbers summary CSV
rows = [("variant_cycle", "N1_motor_cont_RMS_shaft_kW", "N2_genset_const_bus_kW",
         "N2_genset_engine_shaft_kW", "N3_buffer_5min_kWh",
         "N4_peak_regen_wheel_kW")]
for k, fnx in R["four_numbers"].items():
    rows.append((k, f"{fnx['N1_motor_rms_shaft_kW']:.1f}",
                 f"{fnx['N2_genset_const_bus_kW']:.1f}",
                 f"{fnx['N2_genset_engine_shaft_kW']:.1f}",
                 f"{fnx['N3_buffer_5min_kWh']:.3f}",
                 f"{fnx['N4_peak_regen_wheel_kW']:.1f}"))
with open(os.path.join(DATA, "four_numbers.csv"), "w") as f:
    f.write("\n".join(",".join(str(x) for x in r) for r in rows) + "\n")

# =====================================================================
# 6. FIGURES
# =====================================================================
def _sv(fig, name):
    fig.savefig(os.path.join(FIGS, name), bbox_inches="tight")
    plt.close(fig)


# --- Fig 1: VOLT-SUB speed + power
fig, ax = plt.subplots(3, 1, figsize=(9.5, 6.4), sharex=True)
ax[0].plot(cycA["t"], cycA["v"] * 3.6, lw=0.7, color="#1f77b4")
ax[0].set_ylabel("speed [km/h]"); ax[0].set_title(
    "Cycle A  VOLT-SUB  (suburban postal/parcel, V1) — "
    f"{R['cycles']['VOLT-SUB']['distance_km']:.1f} km, "
    f"{R['cycles']['VOLT-SUB']['stops_per_km']:.2f} stops/km, "
    f"{R['cycles']['VOLT-SUB']['stopped_fraction']*100:.0f}% stopped")
ax[1].plot(cycA["t"], cycA["P"] / 1e3, lw=0.5, color="#333")
ax[1].axhline(75, color="r", ls="--", lw=0.8)
ax[1].axhline(-75, color="r", ls="--", lw=0.8, label="±75 kW regen absorb limit")
ax[1].set_ylabel("wheel power [kW]"); ax[1].legend(loc="upper right", fontsize=7)
ax[2].plot(cycA["t"], emA["e_batt"] / 3.6e6, lw=0.8, color="#2ca02c")
ax[2].set_ylabel("battery energy [kWh]\n(genset at const. "
                 f"{fnA['N2_genset_const_bus_kW']:.1f} kW)")
ax[2].set_xlabel("time [s]")
_sv(fig, "fig01_VOLT-SUB_trace.png")

# --- Fig 2: VOLT-REG speed + grade + power + split
fig, ax = plt.subplots(4, 1, figsize=(9.5, 8.0), sharex=True)
ax[0].plot(cycB["t"], cycB["v"] * 3.6, lw=0.6, color="#1f77b4")
ax[0].set_ylabel("speed [km/h]"); ax[0].set_title(
    "Cycle B  VOLT-REG  (mixed regional trucker, V2) — "
    f"{R['cycles']['VOLT-REG']['distance_km']:.0f} km, "
    f"{R['cycles']['VOLT-REG']['avg_speed_kmh']:.0f} km/h avg, grades to ±6%")
ax[1].plot(cycB["t"], cycB["grade"] * 100, lw=0.6, color="#8c564b")
ax[1].set_ylabel("grade [%]")
ax[2].plot(cycB["t"], cycB["P"] / 1e3, lw=0.4, color="#333", label="wheel power")
ax[2].plot(cycB["t"], p_dir / 1e3, lw=0.6, color="#d62728",
           label="engine direct (2.8:1 lockup)")
ax[2].axhline(75, color="r", ls="--", lw=0.7)
ax[2].axhline(-75, color="r", ls="--", lw=0.7)
ax[2].set_ylabel("power [kW]"); ax[2].legend(loc="upper right", fontsize=7)
ax[3].plot(cycB["t"], emB["e_batt"] / 3.6e6, lw=0.8, color="#2ca02c")
ax[3].set_ylabel("battery energy [kWh]\n(genset at const. "
                 f"{fnB['N2_genset_const_bus_kW']:.1f} kW)")
ax[3].set_xlabel("time [s]")
_sv(fig, "fig02_VOLT-REG_trace.png")

# --- Fig 3: time-at-power histograms
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for k, (c, a) in enumerate(((cycA, ax[0]), (cycB, ax[1]))):
    e, sec = vp.power_histogram(c["t"], c["P"], bin_w=10e3)
    ctr = 0.5 * (e[:-1] + e[1:]) / 1e3
    m = sec > 0
    a.bar(ctr[m], sec[m] / c["t"][-1] * 100, width=9.4,
          color=np.where(ctr[m] < 0, "#d62728", "#1f77b4"))
    a.set_xlabel("wheel power [kW]"); a.set_ylabel("% of cycle time")
    a.set_title(f"{c['name']} time-at-power (10 kW bins)")
    a.axvline(75, color="k", ls="--", lw=0.7); a.axvline(-75, color="k", ls="--", lw=0.7)
    a.set_yscale("log")
_sv(fig, "fig03_time_at_power.png")

# --- Fig 4: regen absorb-limit sensitivity
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for a, nm in zip(ax, ("VOLT-SUB", "VOLT-REG")):
    rows = [r for r in R["regen_sensitivity"][nm]["rows"] if r["cap_kW"] is not None]
    x = [r["cap_kW"] for r in rows]
    a.plot(x, [100 * r["frac_of_braking_mech"] for r in rows], "o-",
           label="captured at the wheel")
    a.plot(x, [100 * r["frac_of_braking_elec"] for r in rows], "s-",
           label="delivered to the DC bus")
    a.axvline(75, color="r", ls="--", lw=0.9, label="75 kW baseline limit")
    a.set_xlabel("regen absorb limit at the wheel [kW]")
    a.set_ylabel("% of total braking energy")
    a.set_title(f"{nm}: braking energy = "
                f"{R['regen_sensitivity'][nm]['E_braking_kWh']:.2f} kWh")
    a.legend(fontsize=7); a.set_ylim(0, 100)
_sv(fig, "fig04_regen_sensitivity.png")

# --- Fig 5: buffer energy vs averaging window
fig, ax = plt.subplots(figsize=(6.2, 3.6))
for nm, d in R["buffer_vs_window"].items():
    xs = [int(k[:-1]) for k in d]; ys = [d[k]["kWh"] for k in d]
    ax.plot(xs, ys, "o-", label=nm)
ax.axvline(300, color="r", ls="--", lw=0.9, label="5 min (assignment)")
ax.set_xscale("log")
ax.set_xticks([60, 120, 300, 600, 1200])
ax.set_xticklabels(["1 min", "2 min", "5 min", "10 min", "20 min"])
ax.minorticks_off()
ax.set_xlabel("genset re-trim window")
ax.set_ylabel("max energy swing [kWh]")
ax.set_title("Number 3: battery buffer vs how often the genset setpoint may move")
ax.legend(fontsize=7)
_sv(fig, "fig05_buffer_vs_window.png")

# --- Fig 6: rolling RMS of motor shaft power vs window
fig, ax = plt.subplots(figsize=(6.2, 3.6))
for nm, key in (("VOLT-SUB (V1 series)", "V1_postal_VOLT-SUB"),
                ("VOLT-REG (V2 i-MMD)", "V2_trucker_VOLT-REG_iMMD"),
                ("VOLT-REG (V2 series only)", "V2_trucker_VOLT-REG_series_only")):
    d = R["four_numbers"][key]["N1_rolling_rms_shaft_kW"]
    xs = [int(k[:-1]) for k in d]; ys = [d[k] for k in d]
    ax.plot(xs, ys, "o-", label=nm)
    ax.axhline(R["four_numbers"][key]["N1_motor_rms_shaft_kW"], ls=":", lw=0.7)
gh = R["sensitivity"]["sustained_series_duty"]["V2_genset_110kW"]["grade_6pct"]["motor_shaft_kW"]
ax.axhline(gh, color="r", ls="--", lw=1.0,
           label=f"6% grade hold, series ({gh:.0f} kW, ~10 min)")
ax.set_xscale("log")
ax.set_xticks([30, 60, 120, 300, 600])
ax.set_xticklabels(["30 s", "1 min", "2 min", "5 min", "10 min"])
ax.minorticks_off()
ax.set_xlabel("thermal averaging window")
ax.set_ylabel("worst rolling RMS motor shaft power [kW]")
ax.set_title("Number 1: cycle RMS understates the sizing duty")
ax.legend(fontsize=7)
_sv(fig, "fig06_motor_rms_vs_window.png")

# --- Fig 7: 10 km 6% climb, forward simulated
t_c = climb_dem["t"]
fig, ax = plt.subplots(3, 1, figsize=(8.5, 6.0), sharex=True)
ax[0].plot(t_c, climb_dem["v"] * 3.6, lw=0.9, ls="--", color="#999", label="demand 85 km/h")
ax[0].plot(t_c, climb_plot["v"] * 3.6, lw=1.1, color="#1f77b4",
           label="V2 achieved (110 kW genset, 2 kWh buffer)")
ax[0].plot(t_c, climb_plot_v1["v"] * 3.6, lw=1.1, color="#d62728",
           label="V1 achieved (50 kW genset, 2 kWh buffer)")
ax[0].set_ylabel("speed [km/h]"); ax[0].legend(fontsize=7)
ax[0].set_title("Sustained 10 km climb at 6%, GVW 6,600 kg")
ax[1].plot(t_c, climb_plot["p_wheel"] / 1e3, lw=0.8, label="wheel")
ax[1].plot(t_c, climb_plot["p_direct"] / 1e3, lw=0.8, label="engine direct")
ax[1].set_ylabel("power [kW]"); ax[1].legend(fontsize=7)
ax[2].plot(t_c, climb_plot["e_batt"] / 3.6e6, lw=1.0, color="#2ca02c")
ax[2].set_ylabel("buffer [kWh]"); ax[2].set_xlabel("time [s]")
_sv(fig, "fig07_climb_10km_6pct.png")

# --- Fig 8: payload sensitivity
fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
labels = list(masses.keys())
for j, key in enumerate(("E_per_km_kWh", "N1_motor_rms_shaft_kW", "N3_buffer_5min_kWh")):
    for nm, mk in (("VOLT-SUB", "o-"), ("VOLT-REG", "s-")):
        d = R["sensitivity"]["payload"][nm]
        ax[j].plot([d[l]["mass_kg"] for l in labels], [d[l][key] for l in labels],
                   mk, label=nm)
    ax[j].set_xlabel("vehicle mass [kg]"); ax[j].set_title(key, fontsize=8)
    ax[j].axvline(VEH.m_gvw, color="r", ls="--", lw=0.8)
    ax[j].legend(fontsize=7)
_sv(fig, "fig08_payload_sensitivity.png")

# --- Fig 9: VOLT-REG demand vs achieved (finite buffer)
fig, ax = plt.subplots(2, 1, figsize=(9.5, 4.8), sharex=True)
ax[0].plot(cycB["t"], cycB["v"] * 3.6, lw=0.6, color="#999", label="demand")
ax[0].plot(cycB["t"], achB_plot["v"] * 3.6, lw=0.6, color="#1f77b4",
           label="achieved (110 kW genset, 2 kWh buffer, 150 kW motor)")
ax[0].set_ylabel("speed [km/h]"); ax[0].legend(fontsize=7)
ax[0].set_title("VOLT-REG: commanded vs achievable speed")
ax[1].plot(cycB["t"], achB_plot["e_batt"] / 3.6e6, lw=0.7, color="#2ca02c")
ax[1].set_ylabel("buffer [kWh]"); ax[1].set_xlabel("time [s]")
_sv(fig, "fig09_VOLT-REG_achievable.png")

# --- Fig 10: speed-power operating map
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for a, c in zip(ax, (cycA, cycB)):
    h = a.hist2d(c["v"] * 3.6, c["P"] / 1e3, bins=[60, 60],
                 cmap="viridis", norm=matplotlib.colors.LogNorm())
    a.set_xlabel("speed [km/h]"); a.set_ylabel("wheel power [kW]")
    a.set_title(f"{c['name']} operating map (time density)")
    a.axhline(75, color="w", ls="--", lw=0.7); a.axhline(-75, color="w", ls="--", lw=0.7)
    fig.colorbar(h[3], ax=a, label="samples")
_sv(fig, "fig10_operating_map.png")

print("==== CYCLE METRICS ====")
for nm, m in R["cycles"].items():
    print(f"{nm}: {m['distance_km']:.2f} km in {m['duration_s']:.0f} s | "
          f"avg {m['avg_speed_kmh']:.1f} km/h | max {m['max_speed_kmh']:.0f} | "
          f"{m['stops_per_km']:.2f} stops/km | idle {m['stopped_fraction']*100:.0f}%")
    print(f"   Ppeak {m['P_peak_kW']:.1f} kW | Pavg_trac {m['P_avg_tractive_kW']:.1f} | "
          f"P95 {m['P95_kW']:.1f} | P99 {m['P99_kW']:.1f} | Prms {m['P_rms_wheel_kW']:.1f}")
    print(f"   E/km {m['E_per_km_kWh']:.3f} kWh (net {m['E_net_per_km_kWh']:.3f}) | "
          f"Ebrake {m['E_braking_kWh']:.2f} kWh ({m['brake_energy_frac_of_tractive']*100:.0f}% of tractive) | "
          f"regen@75kW {m['regen_recoverable_frac_mech']*100:.0f}% mech / "
          f"{m['regen_recoverable_frac_elec']*100:.0f}% elec | regen peak {m['P_regen_peak_wheel_kW']:.0f} kW")
print("\n==== THE FOUR NUMBERS ====")
for k, fnx in R["four_numbers"].items():
    print(f"{k}")
    print(f"   N1 motor RMS  {fnx['N1_motor_rms_shaft_kW']:6.1f} kW shaft "
          f"| rolling: {[f'{w}={fnx['N1_rolling_rms_shaft_kW'][w]:.0f}' for w in fnx['N1_rolling_rms_shaft_kW']]}")
    print(f"   N2 genset     {fnx['N2_genset_const_bus_kW']:6.1f} kW bus / "
          f"{fnx['N2_genset_engine_shaft_kW']:.1f} kW shaft"
          + (f" | engine direct avg {fnx['N2_engine_direct_avg_shaft_kW']:.1f} kW"
             f" | TOTAL engine {fnx.get('N2_engine_total_avg_shaft_kW', 0):.1f} kW"
             if fnx['N2_engine_direct_avg_shaft_kW'] > 0 else ""))
    print(f"   N3 buffer     {fnx['N3_buffer_5min_kWh']:6.3f} kWh (5 min window) "
          f"| full cycle {fnx['N3_buffer_fullcycle_kWh']:.2f} kWh")
    print(f"   N4 peak regen {fnx['N4_peak_regen_wheel_kW']:6.1f} kW wheel / "
          f"{fnx['N4_peak_regen_bus_kW']:.1f} kW bus (capped)")
    print(f"   motor peak motoring {fnx['motor_peak_motoring_shaft_kW']:.1f} kW shaft | "
          f"batt peak dis/chg {fnx['batt_peak_dis_kW']:.0f}/{fnx['batt_peak_chg_kW']:.0f} kW")
print("\n==== SUSTAINED SERIES DUTY (motor continuous driver) ====")
print(json.dumps(R["sensitivity"]["sustained_series_duty"], indent=1, default=float))
print("\n==== BASELINE CROSS-CHECK ====")
print(json.dumps(R["baseline_crosscheck"], indent=1, default=float))
print("\n==== 10 km @ 6% CLIMB ====")
cc = R["sensitivity"]["climb_10km_6pc"]
print(json.dumps({k: v for k, v in cc.items() if k != "per_speed"}, indent=1, default=float))
print("\n==== DESCENT ====")
print(json.dumps(R["sensitivity"]["descent_10km_6pc"], indent=1, default=float))
print("\n==== ACHIEVABLE ====")
print(json.dumps(R["achieved_VOLT-REG_V2"], indent=1, default=float))
print(json.dumps(R["achieved_VOLT-SUB_V1"], indent=1, default=float))
print("\n==== SEED ENSEMBLE ====")
print(json.dumps(R["sensitivity"]["seed_ensemble"], indent=1, default=float))
print("\n==== PAYLOAD ====")
print(json.dumps(R["sensitivity"]["payload"], indent=1, default=float))
print("\n==== N4 ENVELOPE ====")
print(json.dumps(R["N4_envelope"], indent=1, default=float))
print("\n==== GENSET DUTY CYCLING (V1) / CLUTCH DUTY (V2) ====")
print(json.dumps({"genset": R["genset_duty_cycling_V1"],
                  "clutch": R["clutch_duty_V2_VOLT-REG"]}, indent=1, default=float))
print("\n==== REQUIREMENTS SUMMARY ====")
print(json.dumps(R["requirements_summary"], indent=1, default=float))
print("\n==== MOTOR ENVELOPE ====")
print(json.dumps(R["motor_envelope"], indent=1, default=float))
print("\nwrote:", len(os.listdir(FIGS)), "figures,", len(os.listdir(DATA)), "data files")
