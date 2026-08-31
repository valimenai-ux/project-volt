"""
Project Volt - WS9
Fuels: properties, tank-system mass, and CO2 - for the metric of record's
primary-energy and CO2 lenses (ESC-3) and for the prime-mover-at-the-pin
task.

TANK-TO-WHEEL CO2 IS DERIVED, NOT CITED. For any hydrocarbon fuel of
declared atomic H:C ratio, every carbon atom leaves as CO2, so

    mass fraction of carbon   f_C = 12.011 / (12.011 + (H:C) x 1.008)
    kg CO2 per kg of fuel         = f_C x 44.009 / 12.011
    g CO2 per MJ of fuel          = 1000 x that / LHV [MJ/kg]

That is a conservation law, not a factor to be looked up, and it is the
reason the three prime movers' CO2 ordering in the pin task does not depend
on anybody's emission-factor table. Only the WELL-TO-TANK multipliers and
the grid intensity are declared, and those are in ws9_params.EnergyAccounting.
"""
from dataclasses import dataclass, asdict

M_C = 12.011
M_H = 1.008
M_CO2 = 44.009


@dataclass(frozen=True)
class Fuel:
    name: str
    lhv_MJ_per_kg: float
    density_kg_per_L: float          # on-board storage density
    hc_atomic_ratio: float           # H per C
    tank_index_kg_per_kg_fuel: float # tank SYSTEM mass per kg of fuel
    tank_basis: str
    pef_well_to_tank: float
    provenance: str

    # ---------------------------------------------------------- derived
    @property
    def carbon_mass_fraction(self) -> float:
        return M_C / (M_C + self.hc_atomic_ratio * M_H)

    @property
    def kg_CO2_per_kg_fuel(self) -> float:
        return self.carbon_mass_fraction * M_CO2 / M_C

    @property
    def g_CO2_per_MJ_fuel(self) -> float:
        return 1000.0 * self.kg_CO2_per_kg_fuel / self.lhv_MJ_per_kg

    @property
    def MJ_per_L(self) -> float:
        return self.lhv_MJ_per_kg * self.density_kg_per_L

    def tank_system_mass_kg(self, fuel_kg):
        """Mass of the fuel PLUS the vessel that holds it."""
        return fuel_kg * (1.0 + self.tank_index_kg_per_kg_fuel)

    def spec(self):
        d = asdict(self)
        d.update(carbon_mass_fraction=self.carbon_mass_fraction,
                 kg_CO2_per_kg_fuel=self.kg_CO2_per_kg_fuel,
                 g_CO2_per_MJ_fuel=self.g_CO2_per_MJ_fuel,
                 MJ_per_L=self.MJ_per_L)
        return d


DIESEL = Fuel(
    name="diesel", lhv_MJ_per_kg=42.8, density_kg_per_L=0.832,
    hc_atomic_ratio=1.85,
    tank_index_kg_per_kg_fuel=0.15,
    tank_basis="aluminium cylindrical tanks, straps, lines and sender "
               "[WS9-PROV]",
    pef_well_to_tank=1.19,
    provenance="LHV and density carried unchanged from WS4/WS8 "
               "(ws8_params.LHV_KJ_PER_G, DIESEL_DENSITY_KG_PER_L) so WS9's "
               "fuel arithmetic is the same object as Vehicle Zero's; H:C "
               "1.85 is class-typical EN590 [WS9-PROV]")

PETROL_ATKINSON = Fuel(
    name="petrol", lhv_MJ_per_kg=43.4, density_kg_per_L=0.745,
    hc_atomic_ratio=1.87,
    tank_index_kg_per_kg_fuel=0.18,
    tank_basis="steel/plastic tanks with vapour recovery; slightly heavier "
               "per kg of fuel than diesel because the fuel is less dense "
               "so the vessel is larger [WS9-PROV]",
    pef_well_to_tank=1.20,
    provenance="[WS9-PROV] class-typical RON95 petrol")

CNG = Fuel(
    name="natural gas (CNG, 250 bar)", lhv_MJ_per_kg=50.0,
    density_kg_per_L=0.215, hc_atomic_ratio=4.0,
    tank_index_kg_per_kg_fuel=15.67,
    tank_basis="Type-4 carbon-fibre-wrapped polymer-liner cylinders at "
               "250 bar, with brackets, shields, valves, lines and "
               "regulator: a 6.0 wt% SYSTEM gravimetric index, i.e. "
               "1/0.060 - 1 = 15.67 kg of vessel per kg of gas "
               "[WS9-PROV, Type-4 vehicle-cylinder class]",
    pef_well_to_tank=1.13,
    provenance="[WS9-PROV] pipeline-quality methane-rich gas; 215 kg/m^3 at "
               "250 bar is the standard CNG storage density")

LNG = Fuel(
    name="natural gas (LNG)", lhv_MJ_per_kg=50.0,
    density_kg_per_L=0.430, hc_atomic_ratio=4.0,
    tank_index_kg_per_kg_fuel=1.60,
    tank_basis="vacuum-jacketed stainless cryogenic vehicle tank, pump, "
               "vaporiser and lines: a 38 wt% system gravimetric index "
               "[WS9-PROV]",
    pef_well_to_tank=1.13,
    provenance="[WS9-PROV] same fuel as CNG, different vessel - carried as "
               "a separate enumerated case because the vessel is the whole "
               "of the difference and R14 requires the case set to be "
               "enumerated")

FUELS = {f.name: f for f in (DIESEL, PETROL_ATKINSON, CNG, LNG)}


# --------------------------------------------------------------- methane
CH4_GWP100 = 29.8
"""[WS9-PROV] IPCC AR6 100-year global-warming potential for FOSSIL methane
(includes the CO2 from its eventual oxidation). Recalled, not fetched."""

CH4_SLIP_FRACTION = 0.010
"""[WS9-PROV] Fraction of fuel mass leaving a stoichiometric heavy-duty
natural-gas engine as unburned methane after the three-way catalyst,
averaged over a duty cycle. Methane conversion over a TWC needs roughly
450 C and is poor at light load and after a cold start, which is exactly
the duty a sustainer genset avoids - so 1.0% is the CONSERVATIVE end for a
pinned-point machine and the optimistic end for a road engine. Stated
because it is the single number that decides whether natural gas keeps its
CO2 advantage."""


def co2e_kg_per_kg_fuel(fuel, slip_fraction=0.0):
    """CO2-equivalent per kg of fuel BURNED, including unburned methane at
    its GWP where the fuel is methane."""
    combusted = (1.0 - slip_fraction) * fuel.kg_CO2_per_kg_fuel
    slip = 0.0
    if fuel.hc_atomic_ratio >= 3.9:      # methane
        slip = slip_fraction * CH4_GWP100
    return combusted + slip


def fuels_dump():
    d = {k: v.spec() for k, v in FUELS.items()}
    d["_methane"] = dict(gwp100=CH4_GWP100, slip_fraction=CH4_SLIP_FRACTION,
                         co2e_kg_per_kg_with_slip=co2e_kg_per_kg_fuel(
                             CNG, CH4_SLIP_FRACTION),
                         co2e_kg_per_kg_no_slip=co2e_kg_per_kg_fuel(CNG, 0.0))
    d["_derivation"] = ("tank-to-wheel CO2 is a carbon balance on the "
                        "declared H:C ratio, not a cited emission factor: "
                        "f_C = 12.011/(12.011 + (H:C)*1.008); "
                        "kgCO2/kg = f_C * 44.009/12.011")
    return d
