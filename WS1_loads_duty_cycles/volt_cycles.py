"""
Project Volt - WS1
Synthetic reference duty cycles, built by forward integration of a
driver model. Deterministic (seeded).

Cycle A - "VOLT-SUB"  suburban postal / parcel delivery      (V1 Postal)
Cycle B - "VOLT-REG"  mixed regional trucker with 6% grades  (V2 Trucker)

These are *constructed* cycles, not replays of a certified cycle. They are
parameterised to the published statistics of heavy-vehicle city/parcel and
regional cycles (see REPORT_WS1.md, Assumptions) so that stop density,
average speed, idle fraction and speed range are representative. Every
construction parameter is exposed here and can be re-tuned.
"""
import numpy as np
from volt_params import VEH, G

DT = 0.1  # s, integration step


# ------------------------------------------------------------ driver model
class DriverParams:
    def __init__(self, a_max=1.15, p_use=75e3, a_brake=1.20,
                 j_accel=1.0, j_brake=1.2, a_creep_taper=1.5,
                 noise_sigma=0.35, noise_tau=25.0, kp_hold=0.45):
        self.a_max = a_max          # m/s^2 launch acceleration
        self.p_use = p_use          # W  habitual max propulsive wheel power
        self.a_brake = a_brake      # m/s^2 service-brake deceleration
        self.j_accel = j_accel      # m/s^3
        self.j_brake = j_brake      # m/s^3
        self.a_creep_taper = a_creep_taper   # m/s, taper braking below this
        self.noise_sigma = noise_sigma       # m/s speed-hold noise
        self.noise_tau = noise_tau           # s  correlation time
        self.kp_hold = kp_hold               # 1/s speed-hold gain


def _res_accel(v, m, lam):
    """Deceleration produced by road load alone (coasting), flat road."""
    f = 0.5 * VEH.rho_air * VEH.CdA * v ** 2 + VEH.Crr * m * G
    return f / (lam * m)


def _accel_capability(v, dp, m, lam, p_use=None, a_max=None, v_tgt=None):
    """Driver-commanded acceleration at speed v (flat road).

    Force-limited at low speed (a_max), power-limited above the corner
    speed (p_use), and tapered as the target speed is approached - real
    drivers ease off rather than holding constant power to the setpoint.
    """
    p_use = dp.p_use if p_use is None else p_use
    a_max = dp.a_max if a_max is None else a_max
    a_pwr = (p_use / max(v, 0.6)) / (lam * m) - _res_accel(v, m, lam)
    a = max(0.0, min(a_max, a_pwr))
    if v_tgt and v_tgt > 0:
        a *= max(0.15, 1.0 - 0.55 * (min(v / v_tgt, 1.0)) ** 3)
    return a


# ------------------------------------------------------------ leg language
def drive(v_kmh, dist_m):
    return {"kind": "drive", "v": v_kmh / 3.6, "dist": float(dist_m)}


def stop(dwell_s):
    return {"kind": "stop", "dwell": float(dwell_s)}


def build_trace(legs, dp, m=VEH.m_gvw, lam=VEH.lam_rot, seed=0, dt=DT,
                v_cap=None):
    """Integrate the leg list into a speed trace."""
    rng = np.random.default_rng(seed)
    v = 0.0
    vs = [0.0]
    noise = 0.0
    alpha = np.exp(-dt / dp.noise_tau)

    n_legs = len(legs)
    for i, leg in enumerate(legs):
        if leg["kind"] == "stop":
            # decelerate to rest (braking was already anticipated in the
            # preceding drive leg via lookahead), then dwell
            a_brk_stop = dp.a_brake * float(rng.uniform(0.72, 1.28))
            while v > 0.05:
                a = -a_brk_stop * min(1.0, max(v, 0.0) / dp.a_creep_taper)
                a = max(a, -a_brk_stop)
                v = max(0.0, v + a * dt)
                vs.append(v)
            v = 0.0
            for _ in range(int(round(leg["dwell"] / dt))):
                vs.append(0.0)
            continue

        # --- drive leg -------------------------------------------------
        v_tgt = leg["v"]
        # per-leg driver variability: no two pull-aways are identical
        p_use_leg = dp.p_use * float(rng.uniform(0.72, 1.18))
        a_max_leg = dp.a_max * float(rng.uniform(0.80, 1.12))
        a_brk_leg = dp.a_brake * float(rng.uniform(0.72, 1.28))
        s = 0.0
        # lookahead: does this leg end at a stop?
        stops_next = (i + 1 < n_legs and legs[i + 1]["kind"] == "stop")
        guard = 0
        max_steps = int(3600 / dt)
        while s < leg["dist"] and guard < max_steps:
            guard += 1
            noise = alpha * noise + np.sqrt(1 - alpha ** 2) * \
                rng.normal(0.0, dp.noise_sigma)
            v_hold = v_tgt + (noise if v_tgt > 5.0 else 0.0)
            v_hold = max(v_hold, 2.0)
            if v_cap is not None:
                v_hold = min(v_hold, v_cap)

            d_brake = (v ** 2) / (2.0 * a_brk_leg) if stops_next else 0.0
            if stops_next and (leg["dist"] - s) <= d_brake:
                a = -a_brk_leg * min(1.0, max(v, 0.0) / dp.a_creep_taper)
            elif v < v_hold - 1.0:
                # genuine acceleration towards the target
                a = _accel_capability(v, dp, m, lam, p_use_leg, a_max_leg,
                                      v_tgt)
            else:
                # proportional speed hold. A bang-bang hold would inject a
                # spurious +/-0.45 m/s^2 dither and inflate RMS power, P95
                # and the time-at-power tails. The positive side is limited
                # by the same driver power budget as a real acceleration,
                # so the hold branch cannot quietly spend more power than
                # _accel_capability() would allow.
                a = float(np.clip(dp.kp_hold * (v_hold - v), -0.30, 0.40))
                if a > 0.0:
                    a = min(a, _accel_capability(v, dp, m, lam, p_use_leg,
                                                 a_max_leg, None))

            v_new = max(0.0, v + a * dt)
            s += 0.5 * (v + v_new) * dt
            v = v_new
            vs.append(v)
            if stops_next and v <= 0.05:
                break

    v = np.array(vs, dtype=float)
    # jerk-limit the whole trace lightly (moving average, 0.5 s) to remove
    # state-machine discontinuities without changing distance materially
    k = max(1, int(round(0.5 / dt)))
    if k % 2 == 0:          # odd kernel keeps np.convolve(mode="same") centred
        k += 1
    kern = np.ones(k) / k
    v = np.convolve(np.concatenate([np.full(k, v[0]), v, np.full(k, v[-1])]),
                    kern, mode="same")[k:-k]
    v = np.clip(v, 0.0, None)
    if v_cap is not None:
        v = np.minimum(v, v_cap)
    v[v < 0.05] = 0.0
    t = np.arange(v.size) * dt
    return t, v


# ------------------------------------------------------ CYCLE A: VOLT-SUB
# Suburban postal / parcel delivery route block, one hour.
#   segment = (name, cruise km/h, distance to next stop m, dwell s, weight)
SUB_SEGMENTS = [
    ("drop_adjacent", 30, 190, 78, 0.24),   # park-and-loop, next address
    ("drop_block",    40, 430, 72, 0.24),   # next block
    ("drop_street",   50, 820, 62, 0.13),   # few streets over
    ("signal",        45, 330, 18, 0.24),   # traffic light / stop sign
    ("arterial",      50, 1350, 22, 0.11),  # collector road
    ("transit",       50, 2900, 14, 0.04),  # depot in / out
]


def build_cycle_A(duration_s=3600.0, seed=11, dp=None, m=VEH.m_gvw,
                  dwell_scale=1.0):
    dp = dp or DriverParams(a_max=1.15, p_use=72e3, a_brake=1.25,
                            noise_sigma=0.30, noise_tau=22.0)
    rng = np.random.default_rng(seed)
    names = [s[0] for s in SUB_SEGMENTS]
    w = np.array([s[4] for s in SUB_SEGMENTS], float)
    w = w / w.sum()
    legs, chosen = [], []

    def add(seg):
        _, vk, d, dw, _ = seg
        legs.append(drive(vk, d))
        legs.append(stop(dw * dwell_scale))
        chosen.append(seg[0])

    # Deterministic mix, random ORDER only: the route composition is fixed
    # by the segment weights (so the cycle is reproducible and its
    # statistics are stable), while the sequence is shuffled per seed.
    # the dwell scale must go into the leg-count estimate too, otherwise
    # scaling the dwell pushes a variable number of DRIVE legs past the
    # truncation point and the sweep stops being a dwell sensitivity
    t_seg = np.array([sg[2] / (sg[1] / 3.6) * 1.45 + sg[3] * dwell_scale
                      for sg in SUB_SEGMENTS])
    n_tot = (duration_s - 2 * t_seg[5]) / float(np.dot(w, t_seg)) * 1.18
    counts = np.maximum(1, np.round(w * n_tot).astype(int))
    pool = [SUB_SEGMENTS[i] for i, cnt in enumerate(counts) for _ in range(cnt)]
    rng.shuffle(pool)
    add(SUB_SEGMENTS[5])                 # depot egress
    for seg in pool:
        add(seg)
    add(SUB_SEGMENTS[5])                 # depot return
    t, v = build_trace(legs, dp, m=m, seed=seed, v_cap=50.0 / 3.6)
    # Close the block out at the last complete stop at or before the target
    # duration, so the cycle always begins and ends at rest and no segment
    # is cut mid-manoeuvre.
    n_max = int(round(duration_s / DT)) + 1
    if v.size > n_max:
        zeros = np.flatnonzero(v[:n_max] < 0.05)
        cut = int(zeros[-1]) + 1 if zeros.size else n_max
        t, v = t[:cut], v[:cut]
    grade = np.zeros_like(v)
    return dict(name="VOLT-SUB", t=t, v=v, grade=grade, legs=legs,
                mix=chosen, dp=dp)


# ------------------------------------------------------ CYCLE B: VOLT-REG
def build_cycle_B(seed=23, dp=None, m=VEH.m_gvw):
    dp = dp or DriverParams(a_max=1.05, p_use=95e3, a_brake=1.15,
                            noise_sigma=0.45, noise_tau=30.0)
    L = []
    # Phase 1 - depot / urban egress  (~4.1 km)
    for d, vk, dw in [(700, 45, 20), (520, 40, 25), (880, 50, 18),
                      (430, 40, 30), (760, 50, 15), (820, 50, 22)]:
        L += [drive(vk, d), stop(dw)]
    # Phase 2 - rural arterial outbound (~17.5 km)
    L += [drive(70, 3200), drive(80, 4100), stop(18),
          drive(75, 3600), drive(80, 3400), stop(15), drive(70, 3200)]
    # Phase 3 - highway outbound (~50 km) incl. the graded terrain
    L += [drive(90, 6000), drive(100, 9000), drive(95, 7000),
          drive(88, 8000), drive(100, 9500), drive(92, 6500),
          drive(85, 4000)]
    # driver rest / fuel stop
    L += [stop(35)]
    # Phase 4 - highway return (~42 km)
    L += [drive(95, 8000), drive(100, 9000), drive(90, 7500),
          drive(97, 9000), drive(85, 8500)]
    # Phase 5 - rural return (~14 km)
    L += [drive(75, 3800), stop(16), drive(80, 4200),
          drive(70, 3300), stop(14), drive(65, 2600)]
    # Phase 6 - urban delivery drops (~4.4 km)
    for d, vk, dw in [(900, 50, 45), (620, 45, 55), (410, 35, 60),
                      (780, 45, 50), (1050, 50, 35), (640, 40, 40)]:
        L += [drive(vk, d), stop(dw)]

    t, v = build_trace(L, dp, m=m, seed=seed, v_cap=100.0 / 3.6)
    s = np.concatenate(([0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))))
    grade = regional_grade_profile(s)
    return dict(name="VOLT-REG", t=t, v=v, grade=grade, s=s, legs=L, dp=dp)


def regional_grade_profile(s, g_peak=0.06):
    """Grade (rise/run) vs cumulative distance for VOLT-REG.

    Rolling terrain built from three sinusoids plus FOUR flat-topped
    raised-cosine hill features (a long and a short climb outbound, and a
    matching long and short descent on the return). The profile is
    de-meaned (distance-weighted) so that net elevation change over the
    cycle is ZERO - the truck returns to the depot - and then scaled so
    peak |grade| is exactly `g_peak` (6%). Grade amplitude is attenuated
    to 30% over the first and last 4.5% of the route distance (the urban
    phases).
    """
    s = np.asarray(s, float)
    S = s[-1] if s[-1] > 0 else 1.0
    g = (0.016 * np.sin(2 * np.pi * s / 9000.0)
         + 0.008 * np.sin(2 * np.pi * s / 3700.0 + 1.1)
         + 0.004 * np.sin(2 * np.pi * s / 1500.0 + 2.3))

    def bump(centre, width, amp, plateau=0.0):
        """Flat-topped raised-cosine hill feature. `plateau` is the
        fraction of `width` held at full amplitude, with cosine tapers
        either side - this is what makes a *sustained* grade rather than
        a spike."""
        x = np.abs(s - centre) / (width / 2.0)
        p = plateau
        y = np.where(x <= p, 1.0,
                     np.where(x < 1.0,
                              0.5 * (1 + np.cos(np.pi * np.clip(
                                  (x - p) / max(1e-9, 1 - p), 0, 1))), 0.0))
        return amp * y

    # Sustained features, deliberately symmetric so that de-meaning does
    # not bias one sign: a long climb outbound, the matching descent on
    # the return leg, plus a shorter pair.
    g = (g + bump(0.30 * S, 8000.0, +0.048, 0.55)
           + bump(0.47 * S, 3500.0, +0.026, 0.35)
           + bump(0.68 * S, 8000.0, -0.048, 0.55)
           + bump(0.81 * S, 3500.0, -0.026, 0.35))

    # attenuate in urban phases (first 4 % and last 4 % of distance)
    win = np.ones_like(s)
    win[s < 0.045 * S] = 0.30
    win[s > 0.955 * S] = 0.30
    g = g * win

    ds = np.gradient(s)
    g = g - np.sum(g * ds) / np.sum(ds)          # net elevation change = 0
    g = g * (g_peak / np.max(np.abs(g)))         # peak grade = 6 %
    return g


# -------------------------------------------------------- climb scenario
def build_climb(dist_km=10.0, grade=0.06, v_kmh=85.0, dt=DT,
                duration_s=1800.0):
    """Constant-grade sustained climb, constant target speed (demand).

    The demand trace runs for `duration_s` (long enough for the achieved
    speed to settle) even though the graded section is `dist_km` long;
    the analysis reports the settled speed and the time actually taken to
    cover `dist_km`.
    """
    n = int(round(duration_s / dt)) + 1
    t = np.arange(n) * dt
    v = np.full(n, v_kmh / 3.6)
    # smooth launch from rest so the first seconds are physical
    tr = 25.0
    ramp = t < tr
    v[ramp] = (v_kmh / 3.6) * 0.5 * (1 - np.cos(np.pi * t[ramp] / tr))
    return dict(name=f"CLIMB-{dist_km:g}km-{grade*100:g}pc",
                t=t, v=v, grade=np.full_like(v, grade),
                dist_target_m=dist_km * 1000.0)
