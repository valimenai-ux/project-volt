"""
Project Volt - WS9
Pricing of unserved and stored energy - the r2 rule, applied to WS9's
candidates - and the primary-energy / CO2 metric of record.

THE ASSIGNMENT IS EXPLICIT ABOUT WHERE THIS COMES FROM: "Inherit the WS8
pipeline (cycles, S0, mass ledger, electric scaling, PRICING OF UNSERVED
ENERGY AS CORRECTED BY R2)". WS8's round-2 rule (r1 finding F6, material,
rule 5) is:

    price the correction at the candidate's OWN DUTY-AVERAGED efficiency
    over the run being corrected, not at the maximum of its efficiency
    locus - a peak-point scalar is forbidden by rule 5 and r1 had one
    sitting on the largest single correction in the trial

together with r1 finding F4's disposition:

    the charge-sustaining correction is SYMMETRIC (SAE J1711 in spirit) and
    the credit direction is DECLARED, the share is exported SIGNED with min
    AND max, and the credit-free variant is reported ALONGSIDE the margin
    of record so an ordering that depends on the credit is visible

WS9 does not import `run_ws8.apply_energy_corrections` because WS9's
candidates have energy paths WS8 has no name for - a mechanically-geared
engine that also back-drives a machine (S5), a tractor engine that is never
told about the trailer's machine (S7) - so the keys differ. The RULE is
r2's, restated here, and the r2 concordance table in the report lists field
by field which WS8 r2 export each WS9 field corresponds to, so the two can
be compared when r2's numbers land.

WS9 ADDS ONE THING R2 HAS NO NEED FOR: an electricity term. ESC-3, ruled in
R27, gives Vehicle One's metric a grid term for any plug-in candidate, and
the assignment makes PRIMARY ENERGY PER PAYLOAD TONNE-KM the metric of
record for the whole trial. For every candidate that burns only diesel the
diesel primary-energy factor is a COMMON MULTIPLIER and cannot move a
margin; that is asserted, not claimed.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_engine as EN8                                     # noqa: E402
from ws8_params import LHV_KJ_PER_G                          # noqa: E402

import ws9_params as P9                                      # noqa: E402
from ws9_fuels import DIESEL                                 # noqa: E402

CORRECTION_ETA_BOUNDS = (0.10, 0.50)
"""Carried verbatim from WS8 r2 (`run_ws8.CORRECTION_ETA_BOUNDS`). Sanity
bounds on the duty-averaged correction efficiency: a marginal duty average
can be noisy on a run where a path barely ran, and the bounds stop a
degenerate denominator from turning a small correction into a large one.
Every clipped case is flagged in the record."""


def correction_eta(acc):
    """The r2 rule: the candidate's own duty-averaged efficiency over THIS
    run, at the boundary where the shortfall occurred.

    Priority, exactly r2's:
      1. a genset exists and ran -> duty-averaged genset FUEL-TO-BUS
      2. otherwise, the mechanical path it actually has -> duty-averaged
         FUEL-TO-WHEEL. Note the direction, as r2 notes it: the shortfall
         being priced is bus-side, so a fuel-to-wheel efficiency is the
         GENEROUS end - and it is still far below any island BSFC.
      3. fallbacks, declared rather than silently substituted, used only
         where the candidate's own path did not run at all on this cycle.
    """
    lo, hi = CORRECTION_ETA_BOUNDS
    f_gen = acc.get("fuel_g", 0.0) or 0.0
    e_bus = acc.get("e_genset_bus_kWh", 0.0) or 0.0
    if e_bus > 1e-6 and f_gen > 1.0:
        eta = e_bus * 3600.0 / (f_gen * LHV_KJ_PER_G)
        return (float(np.clip(eta, lo, hi)),
                "duty-averaged genset fuel-to-bus over this run",
                bool(eta < lo or eta > hi))
    # The ENGINE'S OWN wheel work, not the vehicle's. On a hybrid a share
    # of the wheel work came out of recovered braking energy rather than
    # out of fuel, and dividing TOTAL wheel work by fuel would credit the
    # engine with the regeneration - which inflates the efficiency and
    # therefore UNDER-prices the correction. Direction of error stated
    # because it is the direction that would have flattered the candidate.
    e_wheel = acc.get("e_engine_wheel_kWh")
    basis_txt = ("duty-averaged ENGINE fuel-to-wheel over this run (no "
                 "genset ran; a bus-side shortfall priced on the "
                 "wheel-side path, the generous direction)")
    if e_wheel is None:
        e_wheel = acc.get("e_wheel_tractive_kWh", 0.0) or 0.0
        basis_txt = ("duty-averaged vehicle fuel-to-wheel over this run "
                     "(the candidate has no separable engine wheel work)")
    f_tot = acc.get("fuel_g", 0.0) or 0.0
    if e_wheel > 1e-6 and f_tot > 1.0:
        eta = e_wheel * 3600.0 / (f_tot * LHV_KJ_PER_G)
        return (float(np.clip(eta, lo, hi)), basis_txt,
                bool(eta < lo or eta > hi))
    return 0.40, "FALLBACK: default (no path ran on this cycle)", False


def apply_energy_corrections(cand, acc):
    """Apply r2's two corrections plus ESC-3's electricity term.

    1. CHARGE-SUSTAINING, symmetric and declared. A pack that ends flatter
       than it started imported propulsion energy the fuel figure never
       saw; a pack that ends fuller earns the corresponding credit. The
       share is exported SIGNED and the credit-free variant is carried
       alongside (F4).

       NOT APPLIED TO A PLUG-IN. For S4' the state of charge the mission
       spent is not a bookkeeping error - it is the GRID ENERGY the vehicle
       was bought to use, and it is metered as such below. Charging it back
       as fuel would be exactly the accounting WS8's ESC-WS8-3 escalated
       and that ESC-3 has now ruled out.

    2. UNSERVED ENERGY, priced at r2's duty-averaged efficiency. The raw
       shortfall is reported alongside, because a large one is a CAPABILITY
       finding and must not disappear into a fuel number.

    3. THE ELECTRICITY TERM (ESC-3). Grid energy enters the metric of
       record as primary energy at a declared factor and carries the CO2
       second lens, both swept +/-50%.
    """
    eta, eta_basis, eta_clipped = correction_eta(acc)
    is_plug_in = bool(getattr(cand, "PLUG_IN", False))
    usable = getattr(getattr(cand, "pack", None), "usable_kwh", 0.0)
    d_soc = acc.get("soc_end", 0.0) - acc.get("soc_start", 0.0)
    e_deficit_kwh = 0.0 if is_plug_in else -d_soc * usable
    e_unserved_kwh = acc.get("unserved_kWh", 0.0) or 0.0

    to_g = 3600.0 / max(eta * LHV_KJ_PER_G, 1e-9)
    g_soc = e_deficit_kwh * to_g
    g_uns = e_unserved_kwh * to_g

    a = dict(acc)
    a["fuel_g_raw"] = a["fuel_g"]
    a["charge_sustain_deficit_kWh"] = e_deficit_kwh
    a["fuel_g_charge_correction"] = g_soc
    a["fuel_g_charge_correction_is_credit"] = bool(g_soc < 0.0)
    a["fuel_g_unserved_correction"] = g_uns
    a["correction_eta"] = eta
    a["correction_eta_basis"] = eta_basis
    a["correction_eta_clipped"] = eta_clipped
    a["fuel_g_corrected"] = a["fuel_g"] + g_soc + g_uns
    a["fuel_g_corrected_deficit_only"] = (a["fuel_g"] + max(g_soc, 0.0)
                                          + g_uns)
    a["e_fuel_MJ_corrected"] = EN8.fuel_energy_MJ(a["fuel_g_corrected"])
    a["e_fuel_MJ_corrected_deficit_only"] = EN8.fuel_energy_MJ(
        a["fuel_g_corrected_deficit_only"])
    a["correction_share_of_fuel"] = (
        (g_soc + g_uns) / a["fuel_g_corrected"]
        if a["fuel_g_corrected"] > 0 else 0.0)
    a["is_plug_in"] = is_plug_in
    return a


# =====================================================================
#  The metric of record: primary energy per payload tonne-km
# =====================================================================
def primary_and_co2(acc, ea=None, pef_grid=None, co2_grid=None):
    """Primary energy [MJ] and CO2e [kg] for one run.

    Diesel: tank energy x the well-to-tank primary factor; CO2 from the
    carbon balance in ws9_fuels (derived, not cited) x the same well-to-tank
    multiplier for the well-to-wheel lens.
    Grid: delivered kWh x 3.6 x the declared grid primary factor; CO2 at the
    declared grid intensity.
    """
    ea = P9.EA if ea is None else ea
    pef_grid = ea.pef_grid if pef_grid is None else pef_grid
    co2_grid = ea.co2_grid_kg_per_kWh if co2_grid is None else co2_grid
    e_fuel_MJ = acc["e_fuel_MJ_corrected"]
    fuel_kg = acc["fuel_g_corrected"] / 1000.0
    grid_kWh = acc.get("grid_kWh", 0.0) or 0.0
    e_prim_fuel = e_fuel_MJ * ea.pef_diesel
    e_prim_grid = grid_kWh * 3.6 * pef_grid
    co2_fuel = fuel_kg * DIESEL.kg_CO2_per_kg_fuel * ea.pef_diesel
    co2_grid_kg = grid_kWh * co2_grid
    return dict(
        e_tank_MJ=e_fuel_MJ, grid_kWh=grid_kWh,
        e_primary_fuel_MJ=e_prim_fuel, e_primary_grid_MJ=e_prim_grid,
        e_primary_MJ=e_prim_fuel + e_prim_grid,
        co2_fuel_kg=co2_fuel, co2_grid_kg=co2_grid_kg,
        co2_kg=co2_fuel + co2_grid_kg,
        pef_diesel=ea.pef_diesel, pef_grid=pef_grid,
        co2_grid_kg_per_kWh=co2_grid,
        co2_diesel_kg_per_kg_wtw=DIESEL.kg_CO2_per_kg_fuel * ea.pef_diesel)


def metrics_for_run(acc, payload_kg, distance_km, ea=None):
    """The metric of record and the two lenses, per run."""
    ea = P9.EA if ea is None else ea
    pt = payload_kg / 1000.0
    pc = primary_and_co2(acc, ea)
    out = dict(pc)
    out["MJ_primary_per_payload_tkm"] = pc["e_primary_MJ"] / pt / distance_km
    out["MJ_tank_per_payload_tkm"] = pc["e_tank_MJ"] / pt / distance_km
    out["g_CO2_per_payload_tkm"] = pc["co2_kg"] * 1000.0 / pt / distance_km
    out["MJ_primary_per_km"] = pc["e_primary_MJ"] / distance_km
    # +/-50% factor sensitivity (ESC-3), on BOTH lenses
    s = ea.factor_sensitivity
    for tag, mult in (("lo", 1.0 - s), ("hi", 1.0 + s)):
        p = primary_and_co2(acc, ea, pef_grid=ea.pef_grid * mult,
                            co2_grid=ea.co2_grid_kg_per_kWh * mult)
        out[f"MJ_primary_per_payload_tkm_grid_{tag}"] = (
            p["e_primary_MJ"] / pt / distance_km)
        out[f"g_CO2_per_payload_tkm_grid_{tag}"] = (
            p["co2_kg"] * 1000.0 / pt / distance_km)
    return out


METRIC_NOTE = (
    "metric of record: PRIMARY ENERGY per payload tonne-km "
    "[MJ_primary/(t.km)] (assignment; ESC-3 as ruled in R27). The diesel "
    "well-to-tank factor multiplies every candidate's fuel term "
    "identically, so for every candidate that burns only diesel the "
    "primary-energy margin and the tank-energy margin are the same number "
    "to machine precision - asserted in the sanity block, not claimed. The "
    "metric therefore changes exactly one thing in this trial: how S4', "
    "the only candidate that imports grid energy, is scored against the "
    "rest. Tank energy per payload tonne-km is reported alongside "
    "throughout, so every WS9 number is directly comparable with WS8's.")
