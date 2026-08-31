"""
Project Volt - WS9
PRIME-MOVER-AT-THE-PIN TASK.

The assignment, quoted in full because this module executes exactly it and
nothing else:

    "For any series element (S4' sustainer; S7 has none; S5 none): diesel vs
     Atkinson-cycle petrol vs natural-gas SI at the pinned point -
     efficiency at the pin, engine + aftertreatment + tank mass for equal
     range charged to payload, cold behaviour, fixed-point durability.
     Energy and emissions only; price is out of scope."

SCOPE, checked rather than assumed: the only WS9 candidate with a series
element is S4'. S5 drives its wheels mechanically through a dog box and S7
never touches the tractor's engine, so neither has a pinned point and
neither appears here. That is asserted in the sanity block.

WHY THIS IS NOT A ONE-NUMBER ANSWER. Rule 5 forbids judging a duty on a
peak-point scalar, and "the pin" is a peak point. So three efficiencies are
reported for each prime mover: at the pin, over a declared load sweep, and
AT THE BUS POWER S4' ACTUALLY ASKED OF ITS SUSTAINER on each duty class -
the last taken from the simulation, not from a locus.

THE THREE ENGINES ARE TORQUE- AND POWER-MATCHED, deliberately. All three
carry WS8's 7 L sustainer torque curve exactly, so they are identical in
what they can DO and differ only in what they BURN and what they WEIGH. The
displacement each needs to make that torque at its own knock-limited BMEP
is what turns the fuel choice into a MASS, and mass is payload.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_candidates as CD8                                 # noqa: E402
import ws8_electric as EL8                                   # noqa: E402
import ws8_engine as EN8                                     # noqa: E402

import ws9_engines as E9                                     # noqa: E402
import ws9_fuels as F9                                       # noqa: E402
import ws9_params as P9                                      # noqa: E402

RANGE_KM = 800.0
"""[WS9-PROV] The declared range over which "equal range" is priced. A
Class 8 tractor's tank range is 1,500-2,500 km; 800 km is a long day's
driving and is the range at which a range-extended BEV's sustainer is
actually being asked to work. Stated because the CNG answer scales linearly
with it and would otherwise look like a modelling choice."""

LOAD_SWEEP = (0.25, 0.50, 0.75, 1.00)




def _build(engine, fuel, aftertreatment_kg, label, note):
    """One prime mover on WS8's own genset construction: the engine, a
    generator scaled to its PRP rating by WS4's ruled model, and WS8's
    GensetLine solving the BSFC-optimal locus on the map."""
    rating = E9.prp_rated_cont_kw(engine)
    shaft = rating["prp_kW"]
    gen, _ = EL8.scaled_generator(f"GEN-{engine.name}", shaft)
    line = CD8.GensetLine(engine, gen, gen.cont_kw_in * 0.955)
    with np.errstate(divide="ignore", invalid="ignore"):
        eff = np.where(line.p_grid > 1e-9,
                       line.p_grid / (line.fuel_gps * fuel.lhv_MJ_per_kg
                                      + 1e-12), 0.0)
    j = int(np.argmax(eff))
    return dict(
        label=label, note=note, fuel=fuel.name,
        engine=dict(name=engine.name, label=engine.label,
                    displacement_L=engine.disp_m3 * 1e3,
                    peak_power_kW=engine.peak_power_kw(),
                    peak_torque_Nm=float(np.max(engine.trq_pts)),
                    bmep_plateau_bar=E9.BMEP_PLATEAU_BAR[fuel_key(fuel)],
                    mass_kg=engine.mass_kg,
                    island_bsfc_g_per_kWh=engine.min_bsfc_point()["bsfc"],
                    peak_BTE=3600.0 / (engine.min_bsfc_point()["bsfc"]
                                       * fuel.lhv_MJ_per_kg)),
        generator=dict(name=gen.name, cont_kW_in=gen.cont_kw_in,
                       mass_kg=gen.mass_kg),
        rating_ESC4=rating,
        aftertreatment_kg=aftertreatment_kg,
        pin=dict(p_bus_kW=float(line.p_grid[j]),
                 engine_rpm=float(line.rpm_opt[j]),
                 engine_torque_Nm=float(line.trq_opt[j]),
                 engine_shaft_kW=float(line.p_shaft[j]),
                 engine_bsfc_g_per_kWh=float(line.bsfc[j]),
                 load_fraction=float(line.phi_opt[j]),
                 eta_fuel_to_bus=float(eff[j])),
        _line=line, _eff=eff, _fuel=fuel, _engine=engine)


def fuel_key(fuel):
    if fuel.name.startswith("natural gas"):
        return "natural gas"
    return fuel.name


def eta_at_bus_kw(pm, p_kw):
    """Fuel-to-bus efficiency at a stated bus power - part-load, from the
    engine's own map through its own generator (rule 5)."""
    line, eff = pm["_line"], pm["_eff"]
    p = float(np.clip(p_kw, 0.0, line.p_elec_max_kw))
    return float(np.interp(p, line.p_grid, eff))


COLD_BEHAVIOUR = {
    "diesel": (
        "Worst of the three. Compression ignition needs a hot charge: grid "
        "heaters or glow plugs at start, and a long warm-up during which "
        "combustion is poor. The aftertreatment is the harder half - SCR "
        "needs roughly 200 C before urea can be dosed at all, so a cold "
        "sustainer emits NOx it cannot treat, and the DEF itself freezes at "
        "-11 C and needs heated lines and tank. A PINNED point mitigates "
        "much of this: the engine goes to a high-load point immediately and "
        "gets the catalyst hot fast, which is one of the real arguments for "
        "a series layout."),
    "petrol": (
        "Best of the three. Spark ignition starts cold without assistance; "
        "a three-way catalyst lights off in the order of 20 seconds; there "
        "is no urea to freeze and no filter to regenerate. The cost is "
        "cold-start enrichment - a stoichiometric engine runs rich until "
        "the oxygen sensor is hot - which is a fuel penalty of a few "
        "hundred grams per start, not a capability limit."),
    "natural gas": (
        "Good at the engine, awkward at the catalyst and at the tank. "
        "Spark ignition starts cold; there is no urea and no filter. But "
        "METHANE IS THE HARDEST HYDROCARBON A THREE-WAY CATALYST HAS TO "
        "CONVERT and needs roughly 450 C to do it, so a cold start passes "
        "unburned methane straight through - and methane's GWP makes that "
        "slip count for far more than its mass. On the tank side, CNG "
        "pressure and therefore usable mass fall with temperature, and LNG "
        "in a vehicle tank boils off when the vehicle stands."),
}

FIXED_POINT_DURABILITY = {
    "diesel": (
        "Excellent, and it is the incumbent for a reason. Heavy-duty "
        "diesels are designed for a B10 life measured in the millions of "
        "kilometres under FAR harsher duty than a pinned point: no "
        "transients, no cold cycling once warm, one speed, one load. A "
        "genset diesel is a diesel doing the easiest job it will ever be "
        "asked to do."),
    "petrol": (
        "THE OPEN QUESTION, and it is the finding of this task rather than "
        "an aside. There is no heavy-duty petrol engine in service to point "
        "at. Pinned operation removes the two things that usually kill a "
        "petrol engine in heavy service - knock under transient load, and "
        "valve-seat recession from repeated cold cycling - and a fixed "
        "low-BMEP point is benign. But the absence of a product means the "
        "1,000,000 km claim has no evidence behind it, and WS9 will not "
        "manufacture one. The efficiency numbers below stand; the "
        "durability row is a RISK, stated as one."),
    "natural gas": (
        "Demonstrated in service. Stoichiometric heavy-duty gas engines are "
        "production products (the Cummins ISX12 G lineage and the X15N) "
        "with fleet hours behind them. The known wear mechanisms are "
        "exhaust valve and seat recession at stoichiometric exhaust "
        "temperature, and shorter oil life; both are maintenance items, not "
        "capability limits, and both are milder at a pinned point than on "
        "the road."),
}


def prime_mover_at_the_pin(s4p_blob=None):
    from collections import OrderedDict as OD
    pms = OD()
    pms["diesel"] = _build(
        EN8.ENG_7L, F9.DIESEL, E9.AFTERTREATMENT_KG["diesel"],
        "compression-ignition diesel (the incumbent sustainer)",
        "WS8's own 7 L sustainer, inherited unchanged")
    pms["petrol"] = _build(
        E9.ENG_PETROL, F9.PETROL_ATKINSON, E9.AFTERTREATMENT_KG["petrol"],
        "boosted Atkinson/Miller-cycle petrol",
        "torque-matched to the diesel; displacement follows from a "
        "knock-limited 18 bar BMEP")
    pms["natural gas (CNG)"] = _build(
        E9.ENG_NG, F9.CNG, E9.AFTERTREATMENT_KG["natural gas"],
        "stoichiometric + cooled-EGR natural-gas spark ignition, "
        "compressed gas at 250 bar",
        "torque-matched to the diesel; displacement follows from 20 bar "
        "BMEP, which methane's ~120 RON permits and petrol does not")
    pms["natural gas (LNG)"] = _build(
        E9.ENG_NG, F9.LNG, E9.AFTERTREATMENT_KG["natural gas"],
        "the SAME engine, liquefied gas in a cryogenic vehicle tank",
        "identical engine, identical fuel, identical combustion - only the "
        "VESSEL differs. It is enumerated separately because the vessel is "
        "the whole of the difference and R14 requires the case set to be "
        "enumerated rather than represented by one member")

    # --- the duty the sustainer actually did, from the simulation --------
    duty_points = OD()
    if s4p_blob is not None:
        for duty, d in s4p_blob["per_duty"].items():
            rows = d["per_seed"]
            e_bus = float(np.median([r.get("e_genset_bus_kWh", 0.0) or 0.0
                                     for r in rows]))
            dist = float(np.median([r["distance_km"] for r in rows]))
            p_on = float(np.median([r.get("p_genset_mean_on_kW", 0.0) or 0.0
                                    for r in rows]))
            frac = float(np.median([r.get("genset_on_fraction", 0.0) or 0.0
                                    for r in rows]))
            duty_points[duty] = dict(
                e_genset_bus_kWh_median=e_bus,
                distance_km_median=dist,
                bus_kWh_per_km=e_bus / max(dist, 1e-9),
                mean_on_bus_kW_median=p_on,
                genset_on_fraction_median=frac)
    e_per_km = max((v["bus_kWh_per_km"] for v in duty_points.values()),
                   default=0.0)
    gov_duty = max(duty_points, key=lambda d: duty_points[d]["bus_kWh_per_km"]) \
        if duty_points else None
    e_range_kwh = e_per_km * RANGE_KM

    rows = OD()
    for key, pm in pms.items():
        fuel = pm["_fuel"]
        eta_pin = pm["pin"]["eta_fuel_to_bus"]
        sweep = OD()
        for f in LOAD_SWEEP:
            p = f * pm["_line"].p_elec_max_kw
            sweep[f"{f:.2f}"] = dict(p_bus_kW=p,
                                     eta_fuel_to_bus=eta_at_bus_kw(pm, p))
        at_duty = OD()
        for duty, v in duty_points.items():
            at_duty[duty] = dict(
                p_bus_kW=v["mean_on_bus_kW_median"],
                eta_fuel_to_bus=eta_at_bus_kw(pm,
                                              v["mean_on_bus_kW_median"]))
        eta_use = (at_duty[gov_duty]["eta_fuel_to_bus"]
                   if gov_duty else eta_pin)
        e_fuel_MJ = e_range_kwh * 3.6 / max(eta_use, 1e-9)
        m_fuel = e_fuel_MJ / fuel.lhv_MJ_per_kg
        m_tank_sys = fuel.tank_system_mass_kg(m_fuel)
        m_total = (pm["_engine"].mass_kg + pm["aftertreatment_kg"]
                   + m_tank_sys)
        slip = (F9.CH4_SLIP_FRACTION if key.startswith("natural gas")
                else 0.0)
        co2e_per_kg = F9.co2e_kg_per_kg_fuel(fuel, slip)
        rows[key] = dict(
            label=pm["label"], note=pm["note"], fuel=fuel.name,
            engine=pm["engine"], generator=pm["generator"],
            rating_ESC4=pm["rating_ESC4"],
            aftertreatment_kg=pm["aftertreatment_kg"],
            efficiency=dict(
                at_the_pin=pm["pin"],
                over_load_sweep=sweep,
                at_the_duty_the_sustainer_actually_did=at_duty,
                eta_used_for_equal_range=eta_use,
                eta_basis=("at the median on-load bus power S4' asked of "
                           f"its sustainer on {gov_duty}" if gov_duty
                           else "at the pin (no simulated duty available)")),
            equal_range=dict(
                range_km=RANGE_KM,
                bus_kWh_per_km=e_per_km,
                governing_duty=gov_duty,
                bus_energy_kWh=e_range_kwh,
                fuel_energy_MJ=e_fuel_MJ,
                fuel_mass_kg=m_fuel,
                fuel_volume_L=m_fuel / fuel.density_kg_per_L,
                tank_index_kg_per_kg=fuel.tank_index_kg_per_kg_fuel,
                tank_basis=fuel.tank_basis,
                fuel_plus_tank_kg=m_tank_sys,
                engine_kg=pm["_engine"].mass_kg,
                TOTAL_CHARGED_kg=m_total),
            emissions=dict(
                g_CO2_per_MJ_fuel=fuel.g_CO2_per_MJ_fuel,
                methane_slip_fraction=slip,
                co2e_kg_per_kg_fuel=co2e_per_kg,
                g_CO2e_per_bus_kWh=(co2e_per_kg * 1000.0
                                    / (eta_use * fuel.lhv_MJ_per_kg / 3.6)),
                co2e_over_range_kg=m_fuel * co2e_per_kg,
                derivation=("tank-to-wheel CO2 from a carbon balance on the "
                            "declared H:C ratio, not a cited emission "
                            "factor; methane slip at its AR6 GWP100 where "
                            "the fuel is methane")),
            cold_behaviour=COLD_BEHAVIOUR[fuel_key(fuel)],
            fixed_point_durability=FIXED_POINT_DURABILITY[fuel_key(fuel)])

    # R14 exports: explicit max/min over the enumerated prime-mover set
    def _wc(field, path, rule):
        vals = {k: _dig(rows[k], path) for k in rows}
        g = (max(vals, key=lambda k: vals[k]) if rule == "max"
             else min(vals, key=lambda k: vals[k]))
        return dict(rule=rule, cases=vals, value=vals[g], governing_case=g)

    return dict(
        scope=("the only WS9 candidate with a series element is S4'; S5 "
               "drives mechanically through a dog box and S7 never touches "
               "the tractor's engine, so neither has a pinned point"),
        basis=dict(
            range_km=RANGE_KM,
            torque_matched="all three carry WS8's 7 L sustainer torque "
                           "curve exactly; displacement follows from each "
                           "fuel's knock-limited BMEP",
            price="OUT OF SCOPE (assignment; D12)",
            duty_points=duty_points),
        prime_movers=rows,
        worst_case=dict(
            best_pin_efficiency=_wc("eta", ["efficiency", "at_the_pin",
                                            "eta_fuel_to_bus"], "max"),
            lowest_charged_mass=_wc("mass", ["equal_range",
                                             "TOTAL_CHARGED_kg"], "min"),
            lowest_co2e_per_bus_kWh=_wc("co2", ["emissions",
                                                "g_CO2e_per_bus_kWh"],
                                        "min")),
        finding=(
            "read the three rows together, not the efficiency column "
            "alone: the pin rewards the diesel on efficiency, the "
            "aftertreatment rewards both spark-ignition engines, and the "
            "TANK decides the answer - because at fixed gross combination "
            "weight a tank is payload, and compressed methane's vessel "
            "weighs many times the fuel it holds."))


def _dig(d, path):
    for p in path:
        d = d[p]
    return float(d)
