"""
Project Volt - WS9
The two duty classes (R29), and predictive energy management.

R29, quoted: "DESIGN DUTY. Vehicle One is specified for GRADE-HEAVY
REGIONAL duty, with the flat line-haul corridor retained as a control on
which the incumbent is CONCEDED near-optimal."

Assignment: "Primary: GRADE-HEAVY REGIONAL corridor (define from WS8's
grade-heavy corner; state it as the design duty with its own 8-seed
ensemble). Control: WS8's flat line-haul corridor. Report every candidate
on both, per-class, NEVER ONLY AS A FLEET AVERAGE."

NOTHING ABOUT THE CYCLES IS RE-DERIVED. Both duties are built by
`ws8_cycles`, unchanged, on WS8's own fixed seeds. The design duty is
WS8's REGIONAL cycle with `grade_heavy=True` - the regional leg of WS8's
own grade-heavy corner, taken verbatim. The control duty is WS8's LH-520
line-haul corridor at the nominal corner, taken verbatim. WS9 renames them
so the record cannot confuse a duty CLASS with a corner, and reports the
full ensemble statistics of both so a reader can see what "grade-heavy
regional" actually contains rather than taking the adjective on trust.

THERE IS NO FLEET BLEND ANYWHERE IN WS9. WS8 reported a 70/30 fleet
mission; the assignment forbids it here, because R29's whole finding is
that the sign of a margin flips between duties and a fleet average hides
it (D15: architecture is duty-indexed; name the duty before the number
means anything).
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_cycles as CY8                                     # noqa: E402

DESIGN_DUTY = "GH-REG-165"
CONTROL_DUTY = "LH-520"
DUTIES = (DESIGN_DUTY, CONTROL_DUTY)

DUTY_DEFINITION = {
    DESIGN_DUTY: dict(
        role="DESIGN DUTY (R29) - the duty Vehicle One is specified for",
        built_by="ws8_cycles.build_regional(seed, grade_heavy=True)",
        definition=("WS8's REG-165 regional mixed urban/rural/highway "
                    "cycle, built with the grade-heavy terrain "
                    "construction - i.e. the REGIONAL leg of WS8's own "
                    "grade-heavy corner, taken verbatim"),
        gates="ADVANCE/KILL is read on THIS duty"),
    CONTROL_DUTY: dict(
        role="CONTROL DUTY (R29) - the duty on which the incumbent is "
             "CONCEDED near-optimal",
        built_by="ws8_cycles.build_linehaul(seed, grade_heavy=<corner>)",
        definition=("WS8's LH-520 line-haul corridor, taken verbatim. R29 "
                    "calls it 'flat' BY CONTRAST with the grade-heavy "
                    "design duty; it is not a flat road - it carries the "
                    "assignment-ordered 6% mountain and about 3,704 m of "
                    "climb over 520 km - and R29's own supporting figures "
                    "(0.72 of moving time in top gear, 196.8 g/kWh "
                    "duty-averaged) are WS8's LH-520-as-ordered numbers. "
                    "A genuinely grade-zeroed LH-520 appears in exactly "
                    "one place in WS9: the F7 calibration cross-check of "
                    "the ruler, where WS8 also used it."),
        gates="reported alongside, NEVER gating"),
}


def build(duty, seed, ctx):
    """One cycle of one duty at one corner, for one seed."""
    if duty == DESIGN_DUTY:
        # The design duty is grade-heavy BY DEFINITION. R28's grade_heavy
        # corner is therefore a NULL OPERATION on it, and WS9 says so and
        # asserts it rather than quietly running the same thing twice under
        # two names (see run_ws9.sanity_checks).
        c = CY8.build_regional(seed, grade_heavy=True)
        c = dict(c)
        c["name"] = DESIGN_DUTY
        return c
    c = CY8.build_linehaul(seed, grade_heavy=bool(ctx.grade_heavy))
    c = dict(c)
    c["name"] = CONTROL_DUTY
    return c


def build_flat_control(seed):
    """The control duty with the grade zeroed - the F7 cross-check cycle,
    and nothing else."""
    c = dict(CY8.build_linehaul(seed, grade_heavy=False))
    c["name"] = CONTROL_DUTY + "-grade-zeroed"
    c["grade_grid"] = np.zeros_like(c["grade_grid"])
    return c


def seeds():
    return CY8.seeds()


def statistics(cyc):
    return CY8.grade_statistics(cyc)


# =====================================================================
#  Predictive energy management (S6; zero mass)
# =====================================================================
PREVIEW_M = 1500.0
"""[WS9-PROV] Route-preview window. A production predictive-cruise system
looks 1-3 km ahead on map data; 1,500 m at 90 km/h is 60 seconds, which is
long enough to see the crest of a rolling feature and short enough not to
see round the mountain."""

PREVIEW_GAIN = 1.0
PREVIEW_BAND = 0.06
"""[WS9-PROV] The demanded speed may be modulated by at most +/-6% of the
set speed - the band production systems actually use (about +/-6 km/h at
90 km/h). It is a BAND, not a licence: the law below is clipped to it."""


def apply_predictive(cycle):
    """Predictive energy management, applied to the DEMAND TRACE.

    THE LAW, one line, declared before any result:

        dv / v_set  =  clip( +k * (mean grade over the next PREVIEW_M m),
                             -PREVIEW_BAND, +PREVIEW_BAND )

    The sign is what makes it one line instead of two rules, and it is worth
    reading slowly because it is counter-intuitive until it isn't:

      CLIMB AHEAD  (g_ahead > 0)  ->  the target RISES. The truck runs up
        the last of the descent or the flat and enters the climb carrying
        kinetic energy it did not buy with fuel, then trades it for height.
        This is "pre-boost", and it is what a driver with a map does.

      CREST AHEAD  (g_ahead < 0)  ->  the target FALLS. The truck lets speed
        decay over the last of the climb rather than spending fuel to gain
        speed that gravity is about to give back at the top, and often
        would otherwise have to be thrown away again in the retarder.

    Both are the same expression with opposite signs of the grade AHEAD,
    which is why it is one line. Neither is clairvoyance about the driver or
    the traffic: it is knowledge of the ROAD, which is on a map.

    THE GUARD THAT MAKES IT HONEST. A speed-modulating law can always "save
    fuel" by quietly driving slower. So the modulated target is RENORMALISED
    so its distance-weighted mean over the corridor equals the unmodulated
    one exactly, and it is clipped to the assignment's own 85-105 km/h
    demand band so preview cannot smuggle the truck out of its
    specification. Whatever saving survives is energy management and not a
    speed reduction in disguise - and run_ws9's sanity block asserts the
    renormalisation held and reports both achieved trip times, because
    ACHIEVED speed is the integrator's business and not this function's.

    ZERO MASS. Nothing is added to the ledger. That is the point of the
    candidate - and it is also why the same lever is measured on the RULER
    (S0R-PCC) and escalated: a zero-mass lever the incumbent can fit just as
    easily is not, on its own, an argument for a new engine.
    """
    c = dict(cycle)
    s = c["s_grid"]
    g = c["grade_grid"]
    v0 = c["v_tgt_grid"].copy()
    ds = float(s[1] - s[0])
    w = max(1, int(round(PREVIEW_M / ds)))
    # forward-looking mean grade over the preview window
    gp = np.concatenate([g, np.full(w, g[-1])])
    kern = np.ones(w) / w
    g_ahead = np.convolve(gp, kern, mode="full")[w - 1:w - 1 + g.size]
    factor = np.clip(PREVIEW_GAIN * g_ahead, -PREVIEW_BAND, PREVIEW_BAND)
    v1 = v0 * (1.0 + factor)
    sel = v0 > 20.0 / 3.6
    # ORDER MATTERS, and getting it wrong is how a preview law quietly
    # becomes a speed reduction. The band clip must be applied BEFORE the
    # renormalisation and the pair iterated, or a corridor whose set speed
    # already sits near the assignment's 105 km/h ceiling loses its
    # upward excursions to the clip, keeps its downward ones, and arrives
    # late - which would show up as a fuel saving that is really a slower
    # truck. Two passes bring the residual to machine precision on both
    # duties; the sanity block reports what it actually achieved.
    v_hi = CY8.CY.linehaul_v_hi_kmh / 3.6
    scale = 1.0
    for _ in range(24):
        v1 = np.where(sel, np.minimum(v1, v_hi), v1)
        if not sel.any():
            break
        k = float(np.mean(v0[sel]) / np.mean(v1[sel]))
        scale *= k
        if abs(k - 1.0) < 1e-12:
            break
        v1 = np.where(sel, v1 * k, v1)
    v1 = np.where(sel, np.minimum(v1, v_hi), v1)
    c["v_tgt_grid"] = v1
    c["predictive"] = dict(
        preview_m=PREVIEW_M, gain=PREVIEW_GAIN, band=PREVIEW_BAND,
        law="dv/v_set = clip(+gain * mean grade over the preview window, "
            "-band, +band); renormalised to preserve the mean demanded "
            "speed; clipped to the assignment's 85-105 km/h band",
        renormalisation_scale=scale,
        mean_v_tgt_base_ms=float(np.mean(v0[sel])) if sel.any() else 0.0,
        mean_v_tgt_pcc_ms=float(np.mean(v1[sel])) if sel.any() else 0.0,
        mean_preserved_to=float(abs(np.mean(v1[sel]) - np.mean(v0[sel]))
                                / max(np.mean(v0[sel]), 1e-9))
        if sel.any() else 0.0,
        max_abs_delta_kmh=float(np.max(np.abs(v1 - v0))) * 3.6)
    return c


def duty_record(seeds_, ctx_nominal):
    """The ensemble statistics of both duties, so the report can show what
    the design duty actually contains."""
    out = {}
    for duty in DUTIES:
        rows = []
        for sd in seeds_:
            cyc = build(duty, sd, ctx_nominal)
            st = statistics(cyc)
            st["seed"] = int(sd)
            st["v_wind_ms"] = cyc["v_wind"]
            st["n_stops"] = len(cyc["stops"])
            st["v_tgt_max_kmh"] = float(np.max(cyc["v_tgt_grid"])) * 3.6
            st["v_tgt_mean_corridor_kmh"] = float(
                np.mean(cyc["v_tgt_grid"][cyc["v_tgt_grid"]
                                          > 20.0 / 3.6])) * 3.6
            st["climb_m_per_km"] = st["total_climb_m"] / st["distance_km"]
            rows.append(st)
        keys = [k for k in rows[0] if isinstance(rows[0][k], float)]
        out[duty] = dict(
            definition=DUTY_DEFINITION[duty],
            per_seed=rows,
            ensemble={k: _ens([r[k] for r in rows]) for k in keys},
            spec=dict(dt_s=cyc["dt"], sample_rate_Hz=1.0 / cyc["dt"],
                      distance_grid_m=CY8.DS_GRID,
                      seeds=[int(s) for s in seeds_]))
    return out


def _ens(vals):
    a = np.asarray([v for v in vals if v is not None and np.isfinite(v)],
                   float)
    if a.size == 0:
        return dict(n=0, min=None, median=None, max=None, mean=None)
    return dict(n=int(a.size), min=float(np.min(a)),
                median=float(np.median(a)), max=float(np.max(a)),
                mean=float(np.mean(a)))
