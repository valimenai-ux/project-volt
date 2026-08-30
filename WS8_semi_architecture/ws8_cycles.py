"""
Project Volt - WS8
Duty-cycle construction (assignment Task 1).

Two cycles, both DISTANCE-INDEXED (the semi-scale problem is a corridor
problem: grade belongs to the road, not to the clock), sampled at 10 Hz
by the achieved-speed integrator in ws8_physics.py:

  LH-520   line-haul corridor, 520 km, 85-105 km/h demand band, rolling
           terrain with SUSTAINED 2-3% sections and ONE 6% mountain
           segment with its full descent.
  REG-165  regional mixed urban / rural / highway.

Both are CONSTRUCTED cycles, not replays of a certified cycle - the same
posture WS1 took and defended (volt_cycles.py module docstring). Every
construction parameter is exposed here.

8-seed ensembles (CLAUDE.md rule 4). What the seed varies, and why each
is a real source of fleet variance rather than decoration:
  * per-segment cruise-speed draw inside the demand band (traffic, the
    driver's own set speed, and governed-speed policy vary by trip);
  * a constant headwind component per trip (for a 5.5 m^2 CdA at 95 km/h
    this is the single largest real source of trip-to-trip line-haul
    fuel variance, so leaving it out would understate the envelope);
  * rolling-terrain amplitude and phase jitter (the corridor is not the
    same corridor twice) - the SPECIFIED features (2-3% sustained, the
    6% mountain) are NOT jittered, because the assignment fixes them;
  * stop dwell draws.
"""
import numpy as np

from ws8_params import CY

# Distance grid resolution. 25 m over 520 km = 20,801 nodes; the speed
# integrator interpolates within it at 10 Hz (at 105 km/h one 0.1 s step
# is 2.9 m, so the grid is finer than any feature the driver reacts to
# and coarser than the integration step - which is the correct ordering).
DS_GRID = 25.0


def _bump(s, centre, width, amp, plateau=0.0):
    """Flat-topped raised-cosine terrain feature, as WS1's
    regional_grade_profile()._bump. `plateau` is the fraction of the
    half-width held at full amplitude, with cosine tapers either side -
    this is what makes a SUSTAINED grade rather than a spike."""
    x = np.abs(s - centre) / (width / 2.0)
    p = plateau
    y = np.where(x <= p, 1.0,
                 np.where(x < 1.0,
                          0.5 * (1 + np.cos(np.pi * np.clip(
                              (x - p) / max(1e-9, 1 - p), 0, 1))), 0.0))
    return amp * y


def _finish_grade(s, g):
    """Remove any residual net elevation change by a CONSTANT offset.

    A constant offset is used rather than WS1's rescale-to-peak, because
    the assignment SPECIFIES the 6% mountain grade; rescaling would move
    it. The offset needed is ~1e-4 (the features are built in matched
    +/- pairs), so the specified peak survives to four decimals - which
    the caller checks."""
    ds = np.gradient(s)
    off = float(np.sum(g * ds) / np.sum(ds))
    return g - off


# --------------------------------------------------------------- LH-520
def linehaul_grade(s, mountain_grade=None, sustained_amp=None, seed_rng=None,
                   grade_heavy=False):
    """Grade (rise/run) vs cumulative distance for the line-haul corridor.

    Layout over 520 km:
       0- 12 km  depot egress / interchange, terrain attenuated
      12-186 km  rolling corridor with THREE sustained 2-3% pairs
     186-238 km  THE MOUNTAIN: 6% climb, summit, full 6% descent
     238-500 km  rolling corridor with THREE more sustained pairs
     500-520 km  arrival, terrain attenuated

    Every sustained feature is laid down as a matched +/- pair so that
    net elevation change over the corridor is zero BY CONSTRUCTION and
    the residual offset in _finish_grade() is numerical, not structural.
    A line-haul corridor that gained 900 m net would hand a fuel
    advantage or penalty to whichever candidate happened to be measured
    on it; zero net is the only neutral choice.
    """
    s = np.asarray(s, float)
    S = float(s[-1])
    mg = CY.mountain_grade if mountain_grade is None else mountain_grade
    amp = 0.025 if sustained_amp is None else sustained_amp
    if grade_heavy:
        # Task 5 corner: same corridor, heavier terrain. The mountain is
        # unchanged (it is already the specified 6%); the SUSTAINED
        # sections go to the top of the assignment's 2-3% band and the
        # rolling background is doubled.
        amp = 0.030

    # rolling background (three wavelengths, as WS1)
    if seed_rng is None:
        a1, a2, a3 = 0.0090, 0.0055, 0.0028
        p1, p2, p3 = 0.0, 1.1, 2.3
    else:
        a1 = 0.0090 * float(seed_rng.uniform(0.85, 1.15))
        a2 = 0.0055 * float(seed_rng.uniform(0.85, 1.15))
        a3 = 0.0028 * float(seed_rng.uniform(0.85, 1.15))
        p1 = float(seed_rng.uniform(0, 2 * np.pi))
        p2 = float(seed_rng.uniform(0, 2 * np.pi))
        p3 = float(seed_rng.uniform(0, 2 * np.pi))
    if grade_heavy:
        a1, a2, a3 = 2.0 * a1, 2.0 * a2, 2.0 * a3

    bg = (a1 * np.sin(2 * np.pi * s / 21000.0 + p1)
          + a2 * np.sin(2 * np.pi * s / 8600.0 + p2)
          + a3 * np.sin(2 * np.pi * s / 3100.0 + p3))

    km = 1000.0
    # --- ENGINEERED FEATURES ------------------------------------------
    # Sustained 2-3% pairs and the 6% mountain, laid down in matched
    # +/- pairs so net elevation change is zero BY CONSTRUCTION.
    feat = np.zeros_like(s)
    # first corridor (12-186 km)
    feat = (feat + _bump(s, 34 * km, 13000.0, +amp, 0.62)
                 + _bump(s, 58 * km, 13000.0, -amp, 0.62)
                 + _bump(s, 92 * km, 11000.0, +amp * 0.85, 0.58)
                 + _bump(s, 116 * km, 11000.0, -amp * 0.85, 0.58)
                 + _bump(s, 146 * km, 15000.0, +amp * 0.92, 0.66)
                 + _bump(s, 172 * km, 15000.0, -amp * 0.92, 0.66))
    # THE MOUNTAIN (186-238 km): 6% climb, summit, full 6% descent.
    # ~16 km of plateau at 6% is ~960 m of elevation, given back in
    # full on the descent. This is the segment that turns descent
    # braking from a footnote into an architecture question.
    feat = (feat + _bump(s, 200 * km, 22000.0, +mg, 0.72)
                 + _bump(s, 226 * km, 22000.0, -mg, 0.72))
    # second corridor (238-500 km)
    feat = (feat + _bump(s, 268 * km, 14000.0, +amp * 0.88, 0.60)
                 + _bump(s, 296 * km, 14000.0, -amp * 0.88, 0.60)
                 + _bump(s, 340 * km, 12000.0, +amp, 0.62)
                 + _bump(s, 366 * km, 12000.0, -amp, 0.62)
                 + _bump(s, 412 * km, 16000.0, +amp * 0.80, 0.64)
                 + _bump(s, 444 * km, 16000.0, -amp * 0.80, 0.64))

    # Engineered grades are SMOOTH: a highway department that cuts a 6%
    # pass does not leave 1% ripple on top of it. The rolling background
    # is therefore attenuated in proportion to the engineered feature it
    # sits on, which is both physically right and what keeps the
    # SPECIFIED grades (2-3% sustained, 6% mountain) actually at their
    # specified values instead of 1-2 points above them.
    fmax = float(np.max(np.abs(feat))) or 1.0
    bg_win = 1.0 - 0.97 * (np.abs(feat) / fmax) ** 1.5
    g = bg * bg_win + feat

    # attenuate terrain in the urban ends
    win = np.ones_like(s)
    win[s < 12 * km] = 0.30
    win[s > 500 * km] = 0.30
    g = g * win
    return _finish_grade(s, g)


def build_linehaul(seed, grade_heavy=False, dist_km=None):
    """LH-520 demand cycle for one seed."""
    dist_km = CY.linehaul_km if dist_km is None else dist_km
    S = dist_km * 1000.0
    s = np.arange(0.0, S + DS_GRID, DS_GRID)
    rng = np.random.default_rng(seed)

    # --- per-trip cruise speed, inside the assignment's 85-105 band ---
    # A trip has a set speed; segments deviate around it for traffic and
    # road class. Both the trip draw and the segment draws are clipped to
    # the band so the cycle cannot leave the specification.
    v_trip = float(rng.uniform(88.0, 102.0))
    lo, hi = CY.linehaul_v_lo_kmh, CY.linehaul_v_hi_kmh

    km = 1000.0
    # (start_km, end_km, target km/h) - the corridor in road-class blocks
    blocks = [(0, 2.0, 50.0), (2.0, 6.0, 65.0), (6.0, 12.0, 80.0)]
    edges = [12.0, 48.0, 88.0, 130.0, 186.0, 238.0, 282.0, 330.0,
             380.0, 432.0, 480.0, 500.0]
    for i in range(len(edges) - 1):
        seg = float(np.clip(v_trip + rng.normal(0.0, 3.2), lo, hi))
        blocks.append((edges[i], edges[i + 1], seg))
    blocks += [(500.0, 512.0, 75.0), (512.0, 518.0, 55.0),
               (518.0, dist_km, 40.0)]

    v_tgt = np.zeros_like(s)
    for a, b, vk in blocks:
        sel = (s >= a * km) & (s <= b * km)
        v_tgt[sel] = vk / 3.6
    # smooth the block edges over ~300 m so the demand is drivable
    k = int(round(300.0 / DS_GRID))
    if k % 2 == 0:
        k += 1
    kern = np.ones(k) / k
    v_tgt = np.convolve(np.concatenate([np.full(k, v_tgt[0]), v_tgt,
                                        np.full(k, v_tgt[-1])]),
                        kern, mode="same")[k:-k]

    grade = linehaul_grade(s, seed_rng=rng, grade_heavy=grade_heavy)

    stops = [(2.2 * km, float(rng.uniform(25.0, 55.0))),
             (255.0 * km, float(rng.uniform(540.0, 900.0))),
             (S - 30.0, float(rng.uniform(60.0, 120.0)))]

    # per-trip headwind component along the direction of travel [m/s]
    v_wind = float(rng.normal(0.0, 2.4))

    return dict(name="LH-520", dt=CY.dt, s_grid=s, grade_grid=grade,
                v_tgt_grid=v_tgt, stops=stops, seed=int(seed),
                v_wind=v_wind, t_max_s=90000.0,
                spec=dict(dist_km=dist_km, v_trip_kmh=v_trip,
                          grade_heavy=bool(grade_heavy)))


# -------------------------------------------------------------- REG-165
def regional_grade(s, seed_rng=None, grade_heavy=False):
    """Rolling regional terrain, +/-3% class, net zero elevation."""
    s = np.asarray(s, float)
    if seed_rng is None:
        a1, a2, a3, p1, p2, p3 = 0.012, 0.008, 0.004, 0.0, 1.1, 2.3
    else:
        a1 = 0.012 * float(seed_rng.uniform(0.85, 1.15))
        a2 = 0.008 * float(seed_rng.uniform(0.85, 1.15))
        a3 = 0.004 * float(seed_rng.uniform(0.85, 1.15))
        p1 = float(seed_rng.uniform(0, 2 * np.pi))
        p2 = float(seed_rng.uniform(0, 2 * np.pi))
        p3 = float(seed_rng.uniform(0, 2 * np.pi))
    f = 2.0 if grade_heavy else 1.0
    g = (f * a1 * np.sin(2 * np.pi * s / 9000.0 + p1)
         + f * a2 * np.sin(2 * np.pi * s / 3700.0 + p2)
         + f * a3 * np.sin(2 * np.pi * s / 1500.0 + p3))
    km = 1000.0
    amp = 0.030 * f
    g = (g + _bump(s, 42 * km, 9000.0, +amp, 0.50)
           + _bump(s, 62 * km, 9000.0, -amp, 0.50)
           + _bump(s, 104 * km, 7000.0, +amp * 0.8, 0.45)
           + _bump(s, 122 * km, 7000.0, -amp * 0.8, 0.45))
    S = float(s[-1])
    win = np.ones_like(s)
    win[s < 0.06 * S] = 0.30
    win[s > 0.94 * S] = 0.30
    return _finish_grade(s, g * win)


def build_regional(seed, grade_heavy=False):
    """REG-165: urban egress, rural arterial, highway, rural, urban
    delivery. Stop-dense at both ends, which is where an electrified
    launch path earns its keep and a fixed-ratio diesel axle does not."""
    dist_km = CY.regional_km
    S = dist_km * 1000.0
    s = np.arange(0.0, S + DS_GRID, DS_GRID)
    rng = np.random.default_rng(seed + 500)

    km = 1000.0
    blocks = []
    stops = []
    # urban egress 0-14 km, frequent stops
    pos = 0.0
    while pos < 14.0:
        seg = float(rng.uniform(1.0, 2.2))
        blocks.append((pos, min(pos + seg, 14.0),
                       float(rng.uniform(40.0, 58.0))))
        pos += seg
        if pos < 14.0:
            stops.append((pos * km, float(rng.uniform(18.0, 50.0))))
    # rural arterial 14-50 km
    for a, b in [(14, 26), (26, 38), (38, 50)]:
        blocks.append((a, b, float(rng.uniform(72.0, 86.0))))
    stops.append((30.0 * km, float(rng.uniform(15.0, 40.0))))
    # highway 50-118 km
    for a, b in [(50, 70), (70, 92), (92, 118)]:
        blocks.append((a, b, float(rng.uniform(88.0, 100.0))))
    stops.append((100.0 * km, float(rng.uniform(120.0, 300.0))))
    # rural return 118-150 km
    for a, b in [(118, 134), (134, 150)]:
        blocks.append((a, b, float(rng.uniform(70.0, 84.0))))
    stops.append((140.0 * km, float(rng.uniform(15.0, 45.0))))
    # urban delivery 150-165 km
    pos = 150.0
    while pos < dist_km:
        seg = float(rng.uniform(1.2, 2.4))
        blocks.append((pos, min(pos + seg, dist_km),
                       float(rng.uniform(38.0, 55.0))))
        pos += seg
        if pos < dist_km:
            stops.append((pos * km, float(rng.uniform(40.0, 110.0))))

    v_tgt = np.zeros_like(s)
    for a, b, vk in blocks:
        sel = (s >= a * km) & (s <= b * km)
        v_tgt[sel] = vk / 3.6
    v_tgt[v_tgt <= 0] = 40.0 / 3.6
    k = int(round(250.0 / DS_GRID))
    if k % 2 == 0:
        k += 1
    kern = np.ones(k) / k
    v_tgt = np.convolve(np.concatenate([np.full(k, v_tgt[0]), v_tgt,
                                        np.full(k, v_tgt[-1])]),
                        kern, mode="same")[k:-k]

    stops = sorted(stops)
    grade = regional_grade(s, seed_rng=rng, grade_heavy=grade_heavy)
    v_wind = float(rng.normal(0.0, 2.4))
    return dict(name="REG-165", dt=CY.dt, s_grid=s, grade_grid=grade,
                v_tgt_grid=v_tgt, stops=stops, seed=int(seed),
                v_wind=v_wind, t_max_s=60000.0,
                spec=dict(dist_km=dist_km, grade_heavy=bool(grade_heavy)))


def seeds():
    return [CY.seed0 + i for i in range(CY.n_seeds)]


def build_all(grade_heavy=False):
    """The full 8-seed ensemble of both cycles."""
    out = {"LH-520": [], "REG-165": []}
    for sd in seeds():
        out["LH-520"].append(build_linehaul(sd, grade_heavy=grade_heavy))
        out["REG-165"].append(build_regional(sd, grade_heavy=grade_heavy))
    return out


def grade_statistics(cyc):
    """Descriptive statistics the report needs to show the cycle really
    carries what the assignment ordered."""
    s, g = cyc["s_grid"], cyc["grade_grid"]
    ds = np.gradient(s)
    elev = np.concatenate(([0.0], np.cumsum(0.5 * (g[1:] + g[:-1])
                                            * np.diff(s))))
    frac = lambda lo, hi: float(np.sum(ds[(g >= lo) & (g < hi)]) / np.sum(ds))
    return {
        "distance_km": float(s[-1]) / 1000.0,
        "grade_max": float(np.max(g)),
        "grade_min": float(np.min(g)),
        "net_elevation_change_m": float(elev[-1]),
        "total_climb_m": float(np.sum(np.clip(np.diff(elev), 0, None))),
        "total_descent_m": float(-np.sum(np.clip(np.diff(elev), None, 0))),
        "frac_dist_grade_ge_2pct": frac(0.02, 1.0),
        "frac_dist_grade_2_to_3pct": frac(0.02, 0.03),
        "frac_dist_grade_ge_5pct": frac(0.05, 1.0),
        "frac_dist_grade_le_minus5pct": frac(-1.0, -0.05),
        "frac_dist_grade_ge_1pct": frac(0.01, 1.0),
    }
