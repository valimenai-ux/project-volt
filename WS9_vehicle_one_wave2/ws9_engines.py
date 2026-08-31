"""
Project Volt - WS9
Engines WS9 adds to WS8's set, and the ambient/altitude derate wrapper.

WS8's diesels (ENG_13L, ENG_11L, ENG_7L, ENG_5L) and its HD Willans
construction are IMPORTED read-only and unchanged - ESC-5 ratified the HD
speed re-anchor for Vehicle One, so the inherited construction is the
construction of record (CLAUDE.md rule 10; assignment: "do not re-derive
what is ratified").

WS9 adds three things and nothing else:

  ENG_OP     S6's opposed-piston-class engine, on a CITED efficiency basis
  SIWillansEngine + ENG_PETROL / ENG_NG   the two spark-ignition prime
             movers for the prime-mover-at-the-pin task
  DeratedEngine   the wrapper that finally exercises WS4's `derate_factor`
             in the 2,000 m / +45 C corner R28 orders  [R2-IMPL F11]
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_engine as EN8                                    # noqa: E402
from ws8_engine import HDWillansEngine, build_engine, derate_factor  # noqa
from ws8_params import LHV_KJ_PER_G                         # noqa: E402

from ws9_fuels import DIESEL, PETROL_ATKINSON, CNG          # noqa: E402
import ws9_params as P9                                     # noqa: E402


# =====================================================================
#  S6 - the opposed-piston-class engine (assignment: "opposed-piston-class
#  engine on a CITED efficiency basis (state the BTE claim and its evidence
#  quality, mass-neutral or better)")
# =====================================================================
OP_PEAK_BTE_CLAIMED = 0.492
"""[WS9-CITED ACHATES_OP] "peak brake thermal efficiency (BTE) of 49.2%".
Read verbatim out of the primary document; see ws9_params.CITATIONS for the
evidence-quality statement, which is where the argument about how much to
believe belongs."""

OP_ISLAND_BSFC = 3600.0 / (OP_PEAK_BTE_CLAIMED * LHV_KJ_PER_G)

OP_DISPLACEMENT_L = 10.6
"""[WS9-CITED ACHATES_OP] The demonstrated engine's displacement. Recorded
because it is the reason the claim is interesting - it replaces a 15 L
four-stroke - but NOT used to build the map: see WHAT WS9 DOES NOT TAKE."""

WHAT_WS9_DOES_NOT_TAKE = """\
The cited document supports FOUR separate claims. WS9 takes ONE.

  TAKEN     peak brake thermal efficiency 49.2%, applied as the island
            target of an otherwise UNCHANGED WS8 HD Willans map on the
            13 L's own torque curve and displacement. The effect is a
            uniform BSFC improvement of 1 - 185.0/170.98 = -7.6% at every
            speed and load.

  NOT TAKEN 'large areas of the speed/load map above 44% BTE' - a flatter
            map would pay most exactly on the part-load design duty, and
            taking it would be crediting a map shape nobody published.
  NOT TAKEN heat rejection 'on the order of 30% lower' - WS9's heat ledger
            computes rejection from fuel power less brake power on its own
            map, and gets a smaller reduction.
  NOT TAKEN the two-stroke's absent pumping loop and the smaller
            displacement for the same torque, both of which would raise the
            mechanical-efficiency term.
  NOT TAKEN the measured 16% / 4% / 21% real-world route advantages, or the
            10%+ headline. WS9's own answer must come out of its own
            simulation on its own duties, and the cited route numbers are
            used ONLY as an external corroboration check on the sign and
            the duty-dependence, never as an input.

Every one of the four not-taken items would make S6 BETTER. The model is
therefore conservative against the source it cites, and the report says by
how much."""

ENG_OP = build_engine(
    "ENG-OP-W", 12.8, EN8.RPM_13L, EN8.TRQ_13L, EN8.FMEP_HD,
    OP_ISLAND_BSFC, 1215.0,
    "WS9-CONSTRUCTED Willans, opposed-piston-class; island solved to the "
    "cited 49.2% peak BTE, map shape otherwise identical to ENG-13L")
"""S6's prime mover. Mass-neutral with the 13 L four-stroke it replaces
(1,215 kg), which is the FLOOR of the assignment's "mass-neutral or better"
- the cited engine has no cylinder heads and no valvetrain but does have two
crankshafts, a gear train and a supercharger, and the document states no
mass, so WS9 charges it the incumbent's mass and says so."""

OP_AFTERTREATMENT_KG = 155.0
"""Unchanged from the 13 L four-stroke. [WS9-CITED ACHATES_OP]: the engine
"only required a conventional under-floor aftertreatment system" - one box,
DOC + DPF + SCR + ASC - "to comply with these stringent standards". So the
aftertreatment is mass-neutral too, on the source's own evidence, and S6
carries exactly the ruler's ledger."""


def op_break_even_island_bsfc(margin_needed_pct, s0_metric, s6_metric_at_op,
                              s0_island_bsfc=185.0):
    """The peak BTE at which S6 exactly clears a given margin.

    S6 is mass-neutral with the ruler, so on the metric of record its margin
    is exactly its fuel margin, and its fuel scales inversely with the
    island BSFC (the map is scaled uniformly). Therefore

        margin(bsfc) = 1 - (metric_at_op * bsfc / OP_ISLAND_BSFC) / s0_metric

    inverts in closed form. This is the number the lead actually needs: it
    says how much of a manufacturer's demonstration claim has to be true
    before the verdict changes."""
    target = 1.0 - margin_needed_pct / 100.0
    bsfc_be = OP_ISLAND_BSFC * target * s0_metric / s6_metric_at_op
    return dict(margin_needed_pct=margin_needed_pct,
                break_even_island_bsfc_g_per_kWh=bsfc_be,
                break_even_peak_BTE=3600.0 / (bsfc_be * LHV_KJ_PER_G),
                claimed_peak_BTE=OP_PEAK_BTE_CLAIMED,
                incumbent_peak_BTE=3600.0 / (s0_island_bsfc * LHV_KJ_PER_G),
                claim_headroom_pp=100.0 * (OP_PEAK_BTE_CLAIMED
                                           - 3600.0 / (bsfc_be
                                                       * LHV_KJ_PER_G)))


def map_area_above_bte(engine, bte, n=240):
    """Fraction of the feasible (rpm, torque) map above a BTE threshold.

    Exists as a cross-check against the cited claim's second sentence
    ("large areas of the speed/load map above 44% BTE"). If WS9's
    conservatively-scaled map has a SMALLER area above 44% than the source
    describes, the model is conservative in the way it claims to be."""
    r = np.linspace(engine.rpm_pts[0], engine.rpm_pts[-1], n)
    tq = np.linspace(1.0, float(engine.trq_pts.max()), n)
    R, T = np.meshgrid(r, tq, indexing="ij")
    ok = T <= engine.t_max(R)
    eb = np.where(ok, engine.eta_b(R, T), 0.0)
    return float(np.sum(eb >= bte) / max(np.sum(ok), 1))


# =====================================================================
#  Spark-ignition prime movers (prime-mover-at-the-pin task)
# =====================================================================
class SIWillansEngine(HDWillansEngine):
    """Stoichiometric / Miller-Atkinson spark-ignition, on WS4's Willans
    construction with TWO declared departures - and no others.

    (a) THROTTLING. A diesel has no throttle; an SI engine pumps against
        one below full load. Modelled as an additional pumping mean
        effective pressure added to FMEP:

            PMEP_throttle(phi) = pmep0 * (1 - phi)^1.5   [bar]

        At a genset PIN the engine sits near full load, so this term is
        almost zero - which is the whole reason a pinned-point SI is
        interesting and is precisely what the task is asking. On a road
        duty it would be large, and the task does not put it on a road.

    (b) NO LIGHT-LOAD COMBUSTION DERATE AND NO SMOKE LIMIT. WS4's `_f_phi`
        carries a diesel's light-load combustion deterioration and its
        smoke-limit enrichment near full load. Neither applies to a
        stoichiometric SI engine, which burns the same mixture at every
        load. `_f_phi` is therefore 1.0, and the load dependence lives
        entirely in (a) and in the mechanical term. Direction of error:
        deleting the smoke-limit branch FLATTERS the SI engines near full
        load, which is where the pin sits - stated rather than buried.

    The absolute efficiency level is not asserted: `eta_i0` is SOLVED so the
    map minimum lands on the declared peak BTE, exactly as WS8 does for
    every diesel."""

    def __init__(self, *a, pmep0_bar=0.55, lhv_kJ_per_g=None, **kw):
        super().__init__(*a, **kw)
        self.pmep0_bar = float(pmep0_bar)
        self.lhv_kJ_per_g = (LHV_KJ_PER_G if lhv_kJ_per_g is None
                             else float(lhv_kJ_per_g))

    @staticmethod
    def _f_phi(phi):
        return np.ones_like(np.asarray(phi, float))

    def eta_b(self, rpm, trq):
        rpm = np.asarray(rpm, float)
        trq = np.asarray(trq, float)
        tmax = np.maximum(self.t_max(rpm), 1e-6)
        phi = np.clip(trq / tmax, 0.0, 1.0)
        bmep = self.bmep_bar(trq)
        fmep = self.fmep_bar(rpm) + self.pmep0_bar * (1.0 - phi) ** 1.5
        mech = np.where(bmep > 0, bmep / (bmep + fmep), 0.0)
        return self.eta_i0 * self._f_n(rpm) * mech

    def bsfc(self, rpm, trq):
        """g/kWh ON THIS FUEL. The Willans construction's 84.112/eta_b is
        3600/(eta_b * 42.8) - diesel's LHV. An SI engine burning petrol or
        methane consumes a DIFFERENT mass for the same energy, so the
        constant must move with the fuel or every downstream gram is wrong."""
        eb = self.eta_b(rpm, trq)
        k = 3600.0 / self.lhv_kJ_per_g
        return np.where(eb > 1e-4, k / np.maximum(eb, 1e-4), np.inf)


def _solve_si_eta_i0(name, disp_l, rpm_pts, trq_pts, fmep_a, target_bsfc,
                     pmep0_bar, lhv, tol=1e-10):
    def island(eta):
        e = SIWillansEngine(name, disp_l, rpm_pts, trq_pts, eta,
                            fmep_a=fmep_a, pmep0_bar=pmep0_bar,
                            lhv_kJ_per_g=lhv)
        return e.min_bsfc_point()["bsfc"]
    lo, hi = 0.20, 0.95
    for _ in range(240):
        mid = 0.5 * (lo + hi)
        if island(mid) > target_bsfc:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def build_si_engine(name, disp_l, rpm_pts, trq_pts, fmep_a, peak_bte, fuel,
                    mass_kg, label, pmep0_bar=0.55):
    lhv = fuel.lhv_MJ_per_kg          # MJ/kg == kJ/g
    target_bsfc = 3600.0 / (peak_bte * lhv)
    eta_i0 = _solve_si_eta_i0(name, disp_l, rpm_pts, trq_pts, fmep_a,
                              target_bsfc, pmep0_bar, lhv)
    return SIWillansEngine(name, disp_l, rpm_pts, trq_pts, eta_i0,
                           fmep_a=fmep_a, idle_rpm=600.0,
                           rated_cont_rpm=1800.0, mass_kg=mass_kg,
                           label=label, pmep0_bar=pmep0_bar,
                           lhv_kJ_per_g=lhv)


# --- the three prime movers are TORQUE- AND POWER-MATCHED -------------
# All three carry WS8's 7 L sustainer torque curve EXACTLY (RPM_7L /
# TRQ_7L), so the pin comparison changes one thing at a time: the engines
# are identical in what they can DO and differ only in what they BURN and
# what they WEIGH. Matching the curve is what forces the displacement
# difference to appear as mass rather than hiding as a capability gap.
FMEP_SI = (0.66, 0.20, 0.055)
"""[WS9-PROV] A spark-ignition engine runs lower peak cylinder pressures
than a heavy-duty diesel, so its bearing and ring friction is lower; the
throttling that a diesel does not have is carried SEPARATELY in
SIWillansEngine.eta_b so the two mechanisms are not conflated."""

BMEP_PLATEAU_BAR = {
    "diesel": 23.3,   # WS8's 7 L: 1,300 Nm from 7.0 L
    "petrol": 18.0,   # [WS9-PROV] boosted Miller petrol; knock-limited well
                      # below a diesel even with cooled EGR and Miller
                      # timing, because petrol's octane rating is ~95 RON
    "natural gas": 20.0,  # [WS9-PROV] methane's ~120 RON lets a
                      # stoichiometric + cooled-EGR gas engine run close to
                      # diesel BMEP, which is why the Cummins X15N reaches
                      # 2,508 Nm from 15 L (about 21 bar) and the petrol
                      # engine cannot
}

SI_BLOCK_KG_PER_L = (640.0 - 20.0) / 7.0
"""[WS9-PROV] 88.6 kg/L. WS8 prices the 7 L diesel sustainer at 640 kg
(91.4 kg/L). A heavy-duty spark-ignition engine is a CONVERTED DIESEL BLOCK
- that is how every production heavy-duty gas engine is built - so it keeps
the block, the crank and the bottom end, loses the high-pressure common
rail and its injectors (about 35 kg) and gains ignition, a throttle body and
a mixer (about 15 kg): a net 20 kg lighter AT THE SAME DISPLACEMENT. The
mass penalty that follows is therefore entirely a DISPLACEMENT penalty, not
an assumed one."""


def _si_displacement_L(peak_trq_Nm, bmep_bar):
    """Displacement needed to make a torque at a declared BMEP:
    BMEP = 4*pi*T/V_d for a four-stroke."""
    return 4.0 * np.pi * peak_trq_Nm / (bmep_bar * 1e5) * 1e3


PEAK_TRQ_PIN_NM = float(max(EN8.TRQ_7L))
DISP_PETROL_L = _si_displacement_L(PEAK_TRQ_PIN_NM,
                                   BMEP_PLATEAU_BAR["petrol"])
DISP_NG_L = _si_displacement_L(PEAK_TRQ_PIN_NM,
                               BMEP_PLATEAU_BAR["natural gas"])

PETROL_PEAK_BTE = 0.410     # [WS9-CITED ATKINSON_BTE]
NG_PEAK_BTE = 0.405         # [WS9-PROV, corroborated by NG_SI_BTE]

ENG_PETROL = build_si_engine(
    "ENG-ATK-W", DISP_PETROL_L, EN8.RPM_7L, EN8.TRQ_7L, FMEP_SI,
    PETROL_PEAK_BTE, PETROL_ATKINSON, DISP_PETROL_L * SI_BLOCK_KG_PER_L,
    "WS9-CONSTRUCTED Willans, boosted Atkinson/Miller-cycle petrol, "
    "pinned-point genset prime mover, torque-matched to WS8's 7 L diesel")

ENG_NG = build_si_engine(
    "ENG-NG-W", DISP_NG_L, EN8.RPM_7L, EN8.TRQ_7L, FMEP_SI, NG_PEAK_BTE,
    CNG, DISP_NG_L * SI_BLOCK_KG_PER_L,
    "WS9-CONSTRUCTED Willans, stoichiometric + cooled-EGR natural-gas SI, "
    "pinned-point genset prime mover, torque-matched to WS8's 7 L diesel")

AFTERTREATMENT_KG = {
    "diesel": 90.0,      # [WS8] S4's row: DOC/DPF/SCR + DEF tank, MD class
    "petrol": 30.0,      # [WS9-PROV] three-way catalyst and its can only
    "natural gas": 35.0,  # [WS9-PROV] TWC with a higher precious-metal
                          # loading, because methane is the hardest
                          # hydrocarbon a three-way catalyst has to convert
}


# =====================================================================
#  Ambient / altitude derate - INHERITED from WS8 r2, not re-derived
# =====================================================================
# WS8 round 2 implemented finding F11 in `ws8_engine.derated_engine`: WS4's
# ruled `derate_factor(alt_m, t_amb_c)` shrinks the FULL-LOAD TORQUE CURVE
# and leaves the Willans calibration untouched, so every R18/PRP continuous
# rating derates with it. WS9 calls that function and does not write its
# own - "do not re-derive what is ratified" (assignment).
#
# WS9's only addition is that it also applies the derate to the two
# SPARK-IGNITION prime movers in the pin task, where WS8 has no engines.
# Since the pin task is evaluated at sea level and 20 C by construction (a
# pinned point is a pinned point), that path is never exercised in the run
# of record and is asserted to be so in the sanity block.


def derated(engine, ctx):
    """The corner's derate, through WS8 r2's own implementation."""
    return EN8.derated_engine(engine, getattr(ctx, "alt_m", 0.0),
                              getattr(ctx, "t_amb_c", 20.0))


def prp_rated_cont_kw(engine):
    """ESC-4: the Class 8 prime-power rating WS9 sources (ISO 8528-1 PRP at
    0.90 of the automotive peak), with R18's transferred 0.861 carried
    alongside as the declared bracket."""
    peak = engine.peak_power_kw()
    return dict(automotive_peak_kW=peak,
                prp_kW=peak * P9.PRP_OVER_AUTOMOTIVE_PEAK,
                r18_bracket_kW=peak * P9.R18_BRACKET_RATIO,
                prp_ratio=P9.PRP_OVER_AUTOMOTIVE_PEAK,
                r18_bracket_ratio=P9.R18_BRACKET_RATIO,
                basis="ISO 8528-1 PRP (prime, unlimited hours, 10% overload "
                      "1 h in 12, 70-75% 24-hour average load factor); see "
                      "ws9_params.CITATIONS['ISO_8528_PRP']")


def engines_dump():
    out = {}
    for name, eng, fuel in (("ENG-OP", ENG_OP, DIESEL),
                            ("ENG-ATK", ENG_PETROL, PETROL_ATKINSON),
                            ("ENG-NG", ENG_NG, CNG)):
        isl = eng.min_bsfc_point()
        out[name] = dict(
            label=eng.label, displacement_L=eng.disp_m3 * 1e3,
            eta_i0_solved=eng.eta_i0,
            peak_power_kW=eng.peak_power_kw(),
            peak_torque_Nm=float(max(eng.trq_pts)),
            island_bsfc_g_per_kWh=isl["bsfc"], island_rpm=isl["rpm"],
            island_torque_Nm=isl["trq_Nm"], island_power_kW=isl["p_kw"],
            peak_brake_thermal_efficiency=3600.0 / (isl["bsfc"]
                                                    * fuel.lhv_MJ_per_kg),
            fuel=fuel.name, fmep_coefficients_bar=list(eng.fmep_a),
            **({"pmep0_bar": eng.pmep0_bar}
               if isinstance(eng, SIWillansEngine) else {}))
    out["ENG-OP"]["cited_claim"] = dict(
        peak_BTE=OP_PEAK_BTE_CLAIMED,
        island_bsfc_target_g_per_kWh=OP_ISLAND_BSFC,
        demonstrated_displacement_L=OP_DISPLACEMENT_L,
        what_ws9_does_not_take=WHAT_WS9_DOES_NOT_TAKE,
        map_fraction_above_44pct_BTE=map_area_above_bte(ENG_OP, 0.44),
        incumbent_map_fraction_above_44pct_BTE=map_area_above_bte(
            EN8.ENG_13L, 0.44),
        uniform_bsfc_improvement_pct=100.0 * (
            1.0 - OP_ISLAND_BSFC
            / EN8.BSFC_ISLAND_TARGET["ENG-13L"]))
    out["_inherited_unchanged"] = {
        k: dict(label=v.label, peak_power_kW=v.peak_power_kw(),
                island_bsfc_g_per_kWh=v.min_bsfc_point()["bsfc"])
        for k, v in EN8.ENGINES.items()}
    out["_derate"] = dict(
        rule="WS4 derate_factor(alt_m, t_amb_c): none to 1,000 m then 4% "
             "per 1,000 m; none to 30 C then 1% per 5 C; multiplicative",
        at_R28_corner=float(derate_factor(P9.ALT_CORNER_M,
                                          P9.ALT_CORNER_T_C)),
        applies_to="full-load torque curve only; BSFC at a given "
                   "(rpm, torque) carried unchanged",
        implementation="INHERITED: ws8_engine.derated_engine (WS8 r2's own "
                       "implementation of its finding F11); WS9 calls it "
                       "and does not re-derive it")
    out["_prime_power_basis"] = prp_rated_cont_kw(EN8.ENG_13L)
    return out
