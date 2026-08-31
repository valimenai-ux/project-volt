"""
Project Volt - WS11
The CANDIDATES: the ratified Vehicle Zero design, nothing new.

  V1 "Postal"  - pure series, V3307-V1C-class genset, R19 start-stop,
                 shared spine (VM250-HV, 1200 V SiC, brake resistor),
                 288s1p LTO pack (11.083608 kWh usable), R15 blend order,
                 R16 cold curve. Judged on VOLT-SUB (R5: VOLT-REG is not a
                 V1 cycle).
  V2 "Trucker" - pure series, 4HK1-V2C flat-rated 132 kW, same spine and
                 pack. Judged on VOLT-REG, VOLT-SUB reported alongside.

Both are run through WS4's OWN ratified simulator (`ws4_sim.run_g1_mode`,
mode "b" - pure series at the pinned best-BSFC point with SOC-hysteresis
start-stop). WS11 writes no series supervisor of its own: the point of this
trial is to measure the ratified design, and the ratified design's
simulator is the one that produced `interface_ws4.series_duty_v2`. The
regression assertion in run_ws11.py reproduces that block's exported
ensemble to 1e-12, which is what makes the hot-swap seam explicit: when a
corrected WS4 vintage lands, this file changes not at all and the
assertion either still holds or names the difference.

R12 everywhere: the traction chain is WS2's measured inverter+motor map at
662 V x 0.97 reduction, no scalar PE member; all electrical quantities are
bus-side.
"""
import csv
import json
import os

import numpy as np

from ws4_chain import WS2TractionChain, load_ws2_exports
from ws4_models import ENG_V1, ENG_V2, GEN_V1, GEN_V2
from ws4_sim import run_g1_mode, SOC_START
from volt_params import VEH

import ws11_params as P

# --------------------------------------------------------------- WS3 inputs
_WS3_RESULTS = os.path.join(P.WS3_DIR, "results.json")
_WS3_REGEN = os.path.join(P.WS3_DIR, "regen_acceptance.csv")


def load_ws3():
    with open(_WS3_RESULTS) as f:
        j = json.load(f)
    iface = j["interface_WS3"]
    rows = []
    with open(_WS3_REGEN) as f:
        for line in f:
            if line.startswith("#"):
                continue
            rows.append(line)
    rd = csv.DictReader(rows)
    tab = [(float(r["T_cell_C"]), float(r["V2pack_chg_cont_kW_bus"]))
           for r in rd]
    tab.sort()
    return dict(
        usable_bus_kWh=float(iface["packs"]["V2"]["usable_bus_kWh"]),
        pack_mass_kg=float(iface["packs"]["V2"]["mass_kg"]),
        v1_genset_hysteresis_kWh=float(
            iface["soc_strategy"]["allocation"]["V1"]["genset_hysteresis_kWh"]),
        regen_accept_T=[x[0] for x in tab],
        regen_accept_kW=[x[1] for x in tab],
    )


def regen_accept_bus_kw(ws3, t_cell_c):
    """R16: WS3's published pack charge-acceptance curve is the interface
    of record. Read at the case's declared cell temperature, no
    extrapolation beyond the table's own ends."""
    return float(np.interp(t_cell_c, ws3["regen_accept_T"],
                           ws3["regen_accept_kW"]))


# ------------------------------------------------------------ chain of record
def load_chain():
    x = load_ws2_exports(P.WS2_DIR)
    chain = WS2TractionChain(x["map_path"], x["ratio"], VEH.r_dyn)
    return chain, x


CANDIDATES = {
    "V1": dict(engine=ENG_V1, gen=GEN_V1, design_duty="VOLT-SUB",
               label="V1 Postal - pure series, V3307-V1C-class genset, "
                     "R19 start-stop"),
    "V2": dict(engine=ENG_V2, gen=GEN_V2, design_duty="VOLT-REG",
               label="V2 Trucker - pure series, 4HK1-V2C flat-rated 132 kW"),
}


def ser_band_for(name, ws3):
    """R19 governs V1's start-stop swing: WS3's allocated 3.0 kWh genset
    hysteresis band on the delivered 11.083608 kWh usable, centred on the
    0.55 SOC target. V2 runs the ratified series_duty_v2 band (the
    simulator default 0.35-0.75), so the V2 nominal run reproduces the
    live design input exactly."""
    if name != "V1":
        return None
    half = 0.5 * ws3["v1_genset_hysteresis_kWh"] / ws3["usable_bus_kWh"]
    return (SOC_START - half, SOC_START + half)


def run_candidate(name, cyc, ws3, chain, m, veh=VEH, derate=1.0,
                  p_aux_kw=2.0, chg_accept_bus_kw=None, regen_cap_kw=75.0,
                  mode="b", ser_band="auto", trace=False):
    c = CANDIDATES[name]
    band = ser_band_for(name, ws3) if ser_band == "auto" else ser_band
    out = run_g1_mode(
        cyc, mode, c["engine"], c["gen"],
        usable_kwh=ws3["usable_bus_kWh"], p_aux_kw=p_aux_kw, veh=veh, m=m,
        derate=derate, regen_cap_kw=regen_cap_kw, chain=chain,
        chg_accept_bus_kw=chg_accept_bus_kw, ser_band=band, trace=trace)
    out["vehicle"] = name
    out["fuel_energy_kwh"] = out["fuel_energy_kwh"]
    return out
