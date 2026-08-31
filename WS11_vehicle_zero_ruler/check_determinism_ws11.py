"""
Project Volt - WS11
Fast independent recomputation check (~1 min), for a reviewer who does not
want to wait out the full 15-minute pipeline.

It rebuilds the two headline paired blocks from scratch - V1 on VOLT-SUB
and V2 on VOLT-REG, both at nominal, all 8 seeds - and asserts that every
per-seed number reproduces the value stored in results_ws11.json BIT FOR
BIT. It also re-runs one configuration twice inside this process and
asserts the two runs agree bit for bit, which is what "deterministic"
means when nothing is seeded by wall-clock.

    python check_determinism_ws11.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

import ws11_params as P                                   # noqa: E402
import volt_cycles as vc                                  # noqa: E402
from volt_params import VEH                               # noqa: E402
from ws4_models import ENG_REF, LHV_KJ_PER_G              # noqa: E402
import ws11_ruler as RU                                   # noqa: E402
import ws11_candidates as CA                              # noqa: E402

with open("results_ws11.json") as f:
    R = json.load(f)

WS3 = CA.load_ws3()
CHAIN, _ = CA.load_chain()
ACC25 = CA.regen_accept_bus_kw(WS3, 25.0)
LEDGERS = P.build_mass_ledgers()
PAY = {k: float(v["payload_at_gvw_kg"]) for k, v in LEDGERS.items()}

CFG = [("V1", "VOLT-SUB", [11, 3, 4, 5, 6, 7, 8, 9], vc.build_cycle_A),
       ("V2", "VOLT-REG", [23, 3, 4, 5, 6, 7, 8, 9], vc.build_cycle_B)]

fail = []
n = 0
for vehicle, duty, seeds, builder in CFG:
    stored = R["results"][f"{vehicle}_on_{duty}"]["nominal"]
    for s in seeds:
        cyc = builder(seed=s)
        ru = RU.run_ruler(cyc, P.M_GVW_KG)
        ca = CA.run_candidate(vehicle, cyc, WS3, CHAIN, m=P.M_GVW_KG,
                              chg_accept_bus_kw=ACC25)
        # the expressions below must be associated EXACTLY as run_ws11.py's
        # metrics() associates them: a mathematically identical but
        # differently-parenthesised form disagrees in the last two bits and
        # would be reported here as a determinism failure that is really an
        # arithmetic-order difference.
        r_km = ru["fuel_energy_kwh"] / ru["distance_km"]
        c_km = ca["fuel_energy_kwh"] / ca["distance_km"]
        r_pt = ru["fuel_energy_kwh"] / (ru["distance_km"]
                                        * PAY["ruler"] / 1000.0)
        c_pt = ca["fuel_energy_kwh"] / (ca["distance_km"]
                                        * PAY[vehicle] / 1000.0)
        m_km = 100.0 * (r_km - c_km) / r_km
        m_pt = 100.0 * (r_pt - c_pt) / r_pt
        for label, got, want in (
                ("ruler per-km", r_km, stored["ruler"]["per_km"]["per_seed"][str(s)]),
                ("cand per-km", c_km, stored["candidate"]["per_km"]["per_seed"][str(s)]),
                ("margin per-km", m_km,
                 stored["margin_pct_per_km_paired"]["per_seed"][str(s)]),
                ("margin per-payload", m_pt,
                 stored["margin_pct_per_payload_tkm_paired"]["per_seed"][str(s)])):
            n += 1
            if got != want:
                fail.append(f"{vehicle}/{duty}/seed {s}/{label}: "
                            f"recomputed {got!r} != stored {want!r}")
    print(f"  {vehicle} on {duty}: 8 seeds recomputed")

# same configuration twice in this process
c1 = vc.build_cycle_B(seed=23)
c2 = vc.build_cycle_B(seed=23)
a = RU.run_ruler(c1, P.M_GVW_KG)
b = RU.run_ruler(c2, P.M_GVW_KG)
for k in ("fuel_g", "fuel_energy_kwh", "eng_kwh", "distance_km",
          "unserved_wheel_kwh", "n_shifts"):
    n += 1
    if a[k] != b[k]:
        fail.append(f"ruler repeat run differs on {k}: {a[k]!r} vs {b[k]!r}")
x = CA.run_candidate("V2", c1, WS3, CHAIN, m=P.M_GVW_KG,
                     chg_accept_bus_kw=ACC25)
y = CA.run_candidate("V2", c2, WS3, CHAIN, m=P.M_GVW_KG,
                     chg_accept_bus_kw=ACC25)
for k in ("fuel_corrected_g", "fuel_energy_kwh", "distance_km", "starts"):
    n += 1
    if x[k] != y[k]:
        fail.append(f"candidate repeat run differs on {k}: {x[k]!r} vs {y[k]!r}")

print()
if fail:
    print(f"DETERMINISM CHECK FAILED - {len(fail)} problem(s):")
    for m in fail:
        print("  - " + m)
    sys.exit(1)
print(f"DETERMINISM OK - {n} values recomputed from scratch and reproduced "
      f"BIT FOR BIT against results_ws11.json, and repeated runs of the same "
      f"configuration are bit-identical.")
