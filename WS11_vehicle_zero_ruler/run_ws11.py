"""
Project Volt - WS11 - VEHICLE ZERO RULER TRIAL (BASELINE_v5 R32)
Single entry point. Deterministic, fixed seeds, byte-stable.

    python run_ws11.py

Writes results_ws11.json, data/*.csv, data/trace_*_10Hz.csv (R34) and
run_output.txt. Nothing outside WS11_vehicle_zero_ruler/ is written.

QUESTION OF RECORD: is the ratified Vehicle Zero design more efficient
than the truck it replaces, on the honest metric?

METRIC OF RECORD: fuel energy per PAYLOAD tonne-km, on the PAIRED
per-seed statistic (R36/D13). Per-km is reported beside it, also paired,
also labelled.
"""
import csv
import dataclasses
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

import ws11_params as P                                        # noqa: E402
import volt_cycles as vc                                       # noqa: E402
from volt_params import VEH                                    # noqa: E402
from ws4_models import (ENG_REF, ENG_V1, ENG_V2, GEN_V1, GEN_V2,  # noqa
                        derate_factor, LHV_KJ_PER_G)
import ws11_ruler as RU                                        # noqa: E402
import ws11_candidates as CA                                   # noqa: E402
import ws11_capability as KP                                   # noqa: E402

T0 = time.time()
LOG = []


def log(msg):
    """Progress goes to stdout WITH elapsed wall-clock, and to the committed
    run_output.txt WITHOUT it. run_output.txt is a committed artefact and a
    committed artefact carrying a timer can never be byte-stable, which is
    the first of CLAUDE.md's binding rules."""
    LOG.append(msg)
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


REG_SEEDS = [23, 3, 4, 5, 6, 7, 8, 9]      # WS1/WS4 ensemble, reference 23
SUB_SEEDS = [11, 3, 4, 5, 6, 7, 8, 9]      # WS1/WS4 ensemble, reference 11
SEEDS = {"VOLT-REG": REG_SEEDS, "VOLT-SUB": SUB_SEEDS}
REF_SEED = {"VOLT-REG": 23, "VOLT-SUB": 11}


# ---------------------------------------------------------------- provenance
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


UPSTREAM = {
    "WS1/results.json": os.path.join(P.WS1_DIR, "results.json"),
    "WS1/volt_cycles.py": os.path.join(P.WS1_DIR, "volt_cycles.py"),
    "WS1/volt_params.py": os.path.join(P.WS1_DIR, "volt_params.py"),
    "WS1/volt_physics.py": os.path.join(P.WS1_DIR, "volt_physics.py"),
    "WS2/results.json": os.path.join(P.WS2_DIR, "results.json"),
    "WS2/data/effmap_motor_inverter_662V.csv":
        os.path.join(P.WS2_DIR, "data", "effmap_motor_inverter_662V.csv"),
    "WS2/data/capability_vs_rpm.csv":
        os.path.join(P.WS2_DIR, "data", "capability_vs_rpm.csv"),
    "WS2/data/cycle_loss_summary.csv":
        os.path.join(P.WS2_DIR, "data", "cycle_loss_summary.csv"),
    "WS3/results.json": os.path.join(P.WS3_DIR, "results.json"),
    "WS3/regen_acceptance.csv": os.path.join(P.WS3_DIR,
                                             "regen_acceptance.csv"),
    "WS4/results_ws4.json": os.path.join(P.WS4_DIR, "results_ws4.json"),
    "WS4/ws4_models.py": os.path.join(P.WS4_DIR, "ws4_models.py"),
    "WS4/ws4_sim.py": os.path.join(P.WS4_DIR, "ws4_sim.py"),
    "WS4/ws4_chain.py": os.path.join(P.WS4_DIR, "ws4_chain.py"),
    "WS4/data/bsfc_map_4HK1_ref.csv":
        os.path.join(P.WS4_DIR, "data", "bsfc_map_4HK1_ref.csv"),
    "sources/isuzucv_npr-hd_diesel_specs.pdf":
        os.path.join(HERE, "sources", "isuzucv_npr-hd_diesel_specs.pdf"),
    "sources/as68rc_transmissionrepaircostguide.md":
        os.path.join(HERE, "sources", "as68rc_transmissionrepaircostguide.md"),
    "sources/fuelly_npr_hd_all.txt":
        os.path.join(HERE, "sources", "fuelly_npr_hd_all.txt"),
}
INPUT_SHA = {k: sha256(v) for k, v in sorted(UPSTREAM.items())}

R = {}
R["_meta"] = dict(
    workstream="WS11 - Vehicle Zero ruler trial",
    executes="BASELINE_v5.md R32",
    baseline="BASELINE_v5.md",
    convention=("SI; kW/kWh at the DC bus unless labelled otherwise (R12); "
                "extrema are 8-seed ensemble envelopes (R9); every "
                "machine-readable worst case is an explicit max/min over an "
                "enumerated case set with the governing case labelled "
                "inline (R14); part-load models everywhere, no peak-point "
                "scalars (R9)"),
    metric_of_record=("fuel energy per PAYLOAD tonne-km, PAIRED per-seed "
                      "statistic (R36/D13). Per-km reported beside it, "
                      "also paired, also labelled."),
    seeds=dict({"VOLT-REG": REG_SEEDS, "VOLT-SUB": SUB_SEEDS}),
    input_sha256=INPUT_SHA,
)
log("provenance pinned")

# --------------------------------------------------------------- inputs
WS3 = CA.load_ws3()
CHAIN, WS2X = CA.load_chain()
CAP_RPM, CAP_TRQ = KP.load_capability_curve(P.WS2_DIR)
with open(UPSTREAM["WS4/results_ws4.json"]) as f:
    WS4J = json.load(f)
SD2 = WS4J["interface_ws4"]["series_duty_v2"]

R["input_vintages"] = dict(
    ws4_series_duty_v2=dict(
        status=SD2["_status"],
        basis=SD2["_basis"][:400],
        cases=sorted(SD2["cases"].keys()),
        seeds=SD2["_inputs"]["seeds"],
        usable_bus_kWh=SD2["_inputs"]["usable_bus_kWh"],
        input_sha256_declared_by_ws4=SD2["input_sha256"],
        consumed_as=("live design input: WS11 calls WS4's own simulator "
                     "(ws4_sim.run_g1_mode, mode 'b') with the same inputs, "
                     "and asserts it reproduces this block's nominal "
                     "ensemble bit-for-bit. That assertion IS the hot-swap "
                     "seam: a corrected WS4 vintage either still satisfies "
                     "it or names the difference, with no WS11 code change."),
        gate_g1_archived_status=WS4J["interface_ws4"]["gate_g1"]["status"],
        gate_g1_consumed=False,
        gate_g1_note=("ARCHIVED, executed_kill_2026-08-30; no field of it is "
                      "consumed as a live requirement"),
        spin_drag_operational_note_r22d_consumed=False,
        spin_drag_note=("R22d's true-coast member is a WS4 export that is "
                        "reported and never charged to fuel; WS11 charges "
                        "it to neither vehicle and does not re-derive it"),
    ),
    ws2_chain_of_record=dict(
        map_file=WS2X["map_file_rel"], map_voltage_V=WS2X["map_voltage_V"],
        ws2_bus_nominal_V=WS2X["ws2_bus_nominal_V"],
        ws2_rework_round=WS2X["ws2_rework_round"],
        ws2_results_date=WS2X["ws2_results_date"], ratio=WS2X["ratio"]),
    ws3_pack=dict(usable_bus_kWh=WS3["usable_bus_kWh"],
                  mass_kg=WS3["pack_mass_kg"],
                  v1_genset_hysteresis_kWh=WS3["v1_genset_hysteresis_kWh"],
                  regen_acceptance_file="../WS3_battery/regen_acceptance.csv",
                  regen_acceptance_column="V2pack_chg_cont_kW_bus"),
    ws1_cycles=dict(source="../WS1_loads_duty_cycles/volt_cycles.py",
                    reused="verbatim, 10 Hz, same seeds as WS4"),
    ruler_engine_map=dict(
        name=ENG_REF.name, label=ENG_REF.label,
        file="../WS4_genset/data/bsfc_map_4HK1_ref.csv",
        island_bsfc_g_per_kWh=WS4J["bsfc_maps"]["4HK1-TC-ref-W"]
        ["map_min"]["bsfc"]),
)

# ------------------------------------------------------------- mass ledgers
LEDGERS = P.build_mass_ledgers()
PAY = {k: float(v["payload_at_gvw_kg"]) for k, v in LEDGERS.items()}
CURB = {k: float(v["curb_kg"]) for k, v in LEDGERS.items()}
R["mass_ledger"] = dict(
    convention=("fixed GVW 6,600 kg (BASELINE v1); payload = GVW - curb. "
                "All entries to the kilogram; the total is the rounded sum."),
    gvw_kg=P.M_GVW_KG,
    sourced_specification=P.RULER_SOURCED,
    sourced_transmission=P.RULER_TRANS_SOURCED,
    chassis_cab_curb_derivation=dict(
        wheelbase_in=P.WB_RULER_IN,
        allowance_lb_at_wheelbase=P.ALLOWANCE_AT_WB_LB,
        allowance_range_lb=P.RULER_SOURCED["body_payload_allowance_lb"],
        chassis_cab_curb_kg=P.CHASSIS_CAB_CURB_KG,
        method="linear interpolation of the sourced allowance in wheelbase"),
    ruler_build=[dict(item=a, kg=b, source=c) for a, b, c in P.RULER_LEDGER],
    deleted_by_both_candidates=[dict(item=a, kg=b, source=c)
                                for a, b, c in P.DELETED_COMMON],
    added_by_both_candidates=[dict(item=a, kg=b, source=c)
                              for a, b, c in P.ADDED_COMMON],
    v1_deleted=[dict(item=a, kg=b, source=c) for a, b, c in P.V1_DELETED],
    v1_added=[dict(item=a, kg=b, source=c) for a, b, c in P.V1_ADDED],
    v2_deleted=[dict(item=a, kg=b, source=c) for a, b, c in P.V2_DELETED],
    v2_added=[dict(item=a, kg=b, source=c) for a, b, c in P.V2_ADDED],
    v2_aftertreatment_bracket_kg=P.V2_AFTERTREATMENT_BRACKET_KG,
    v2_aftertreatment_treatment=(
        "EXCLUDED from the headline: the 4HK1-V2C is the same production "
        "hardware as the ruler's engine, so its aftertreatment is the stock "
        "truck's and cancels. WS4 exports it as `aftertreatment_extra` "
        "separately from total_dry, which is ambiguous - escalated (ESC-3), "
        "and the +60 kg reading is carried as a bracket."),
    totals=LEDGERS,
    payload_ratio_ruler_over_candidate=dict(
        V1=PAY["ruler"] / PAY["V1"], V2=PAY["ruler"] / PAY["V2"],
        V2_aftertreatment_bracket=PAY["ruler"]
        / PAY["V2_aftertreatment_bracket"]),
    break_even_per_km_advantage_pct=dict(
        V1=100.0 * (1.0 - PAY["V1"] / PAY["ruler"]),
        V2=100.0 * (1.0 - PAY["V2"] / PAY["ruler"]),
        V2_aftertreatment_bracket=100.0 * (
            1.0 - PAY["V2_aftertreatment_bracket"] / PAY["ruler"])),
    break_even_note=("the per-km advantage a candidate must win merely to "
                     "DRAW on fuel energy per payload tonne-km"),
)
log(f"mass ledgers: ruler {CURB['ruler']} kg / payload {PAY['ruler']} kg; "
    f"V1 {CURB['V1']}/{PAY['V1']}; V2 {CURB['V2']}/{PAY['V2']}")

# ------------------------------------------------------------------- cycles
log("building cycles ...")
CYC = {"VOLT-SUB": {s: vc.build_cycle_A(seed=s) for s in SUB_SEEDS},
       "VOLT-REG": {s: vc.build_cycle_B(seed=s) for s in REG_SEEDS}}
CYC_CLIMB = {s: KP.insert_climb(CYC["VOLT-REG"][s]) for s in REG_SEEDS}
R["climb_insert"] = CYC_CLIMB[REF_SEED["VOLT-REG"]]["climb_insert"]
R["climb_insert"]["basis"] = ("WS1 REPORT_WS1.md s4.4, one sustained 10 km "
                              "climb at 6% at GVW, spliced into VOLT-REG at "
                              "30% of route distance; both vehicles face the "
                              "identical inserted demand")

# -------------------------------------------------------------------- cases
ACC = {"nominal": CA.regen_accept_bus_kw(WS3, 25.0),
       "payload_p20_own": CA.regen_accept_bus_kw(WS3, 25.0),
       "payload_m20_own": CA.regen_accept_bus_kw(WS3, 25.0),
       "payload_p20": CA.regen_accept_bus_kw(WS3, 25.0),
       "payload_m20": CA.regen_accept_bus_kw(WS3, 25.0),
       "cold_-10C": CA.regen_accept_bus_kw(WS3, P.CORNER_COLD_C),
       "alt2000m_45C": CA.regen_accept_bus_kw(WS3, P.CORNER_HOT_C),
       "climb_10km_6pct": CA.regen_accept_bus_kw(WS3, 25.0)}
DER_CORNER = derate_factor(P.CORNER_ALT_M, P.CORNER_HOT_C)
RHO_COLD = P.rho_air(0.0, P.CORNER_COLD_C)
RHO_ALT = P.rho_air(P.CORNER_ALT_M, P.CORNER_HOT_C)


def case_spec(name, vehicle):
    """(veh, derate, mass, payload_t, cycle_key, declared_cell_C)"""
    pay_r = PAY["ruler"]
    if name == "nominal":
        return dict(veh=VEH, derate=1.0, m=P.M_GVW_KG,
                    payload_kg=PAY[vehicle], cycle="base",
                    cell_C=25.0, aux=2.0)
    if name == "payload_p20":
        pay = P.PAYLOAD_CORNER_FRACS[0] * pay_r
        return dict(veh=VEH, derate=1.0, m=CURB[vehicle] + pay,
                    payload_kg=pay, cycle="base", cell_C=25.0, aux=2.0)
    if name == "payload_m20":
        pay = P.PAYLOAD_CORNER_FRACS[1] * pay_r
        return dict(veh=VEH, derate=1.0, m=CURB[vehicle] + pay,
                    payload_kg=pay, cycle="base", cell_C=25.0, aux=2.0)
    if name == "payload_p20_own":
        pay = P.PAYLOAD_CORNER_FRACS[0] * PAY[vehicle]
        return dict(veh=VEH, derate=1.0, m=CURB[vehicle] + pay,
                    payload_kg=pay, cycle="base", cell_C=25.0, aux=2.0)
    if name == "payload_m20_own":
        pay = P.PAYLOAD_CORNER_FRACS[1] * PAY[vehicle]
        return dict(veh=VEH, derate=1.0, m=CURB[vehicle] + pay,
                    payload_kg=pay, cycle="base", cell_C=25.0, aux=2.0)
    if name == "cold_-10C":
        return dict(veh=dataclasses.replace(VEH, rho_air=RHO_COLD),
                    derate=1.0, m=P.M_GVW_KG, payload_kg=PAY[vehicle],
                    cycle="base", cell_C=P.CORNER_COLD_C, aux=2.0)
    if name == "alt2000m_45C":
        return dict(veh=dataclasses.replace(VEH, rho_air=RHO_ALT),
                    derate=DER_CORNER, m=P.M_GVW_KG,
                    payload_kg=PAY[vehicle], cycle="base",
                    cell_C=P.CORNER_HOT_C, aux=2.0)
    if name == "climb_10km_6pct":
        return dict(veh=VEH, derate=1.0, m=P.M_GVW_KG,
                    payload_kg=PAY[vehicle], cycle="climb",
                    cell_C=25.0, aux=2.0)
    raise KeyError(name)


CASES = ["nominal", "payload_p20", "payload_m20", "cold_-10C",
         "alt2000m_45C"]
CASES_REG = CASES + ["climb_10km_6pct"]
R["case_definitions"] = dict(
    nominal=("sea level, rho 1.20 kg/m^3 (WS1 fitted), CdA 4.2 m^2, 2 kW "
             "aux, GVW 6,600 kg for BOTH vehicles - payload is what is left "
             "after each vehicle's own curb"),
    payload_p20=(f"payload = 1.20 x the RULER's payload = "
                 f"{1.2 * PAY['ruler']:.0f} kg on every vehicle; total mass "
                 f"= that vehicle's curb + that payload (WS3's own +20% "
                 f"convention: the ruler lands on 7,180 kg)"),
    payload_m20=(f"payload = 0.80 x the RULER's payload = "
                 f"{0.8 * PAY['ruler']:.0f} kg on every vehicle"),
    **{"cold_-10C": (f"-10 C ambient: air density {RHO_COLD:.5f} kg/m^3, and "
                     f"WS3's cold charge-acceptance actually applied - "
                     f"{ACC['cold_-10C']:.3f} kW bus at -10 C cells from "
                     f"regen_acceptance.csv (R16). No cold-engine friction "
                     f"model is applied to either vehicle.")},
    alt2000m_45C=(f"2,000 m / +45 C: air density {RHO_ALT:.4f} kg/m^3, "
                  f"engine derate {DER_CORNER:.4f} on the R6 basis applied "
                  f"to BOTH the candidate genset and the ruler's engine, "
                  f"pack acceptance {ACC['alt2000m_45C']:.3f} kW bus at "
                  f"45 C cells"),
    payload_p20_own=("VARIANT READING, not in the gate: each vehicle "
                     "scales ITS OWN payload by +20%"),
    payload_m20_own=("VARIANT READING, not in the gate: each vehicle "
                     "scales ITS OWN payload by -20%"),
    climb_10km_6pct=("WS1 s4.4's 10 km / 6% sustained climb spliced into "
                     "VOLT-REG (VOLT-REG only; R5 makes VOLT-REG not a V1 "
                     "cycle, so this corner does not apply to V1)"),
)

# ---------------------------------------------------------------- regression
log("regression: reproducing WS4 interface_ws4.series_duty_v2 [nominal] ...")
_reg = []
for sd in REG_SEEDS:
    o = CA.run_candidate("V2", CYC["VOLT-REG"][sd], WS3, CHAIN,
                         m=P.M_GVW_KG, chg_accept_bus_kw=ACC["nominal"])
    _reg.append(o["fuel_energy_kWh_per_km"])
_ens4 = SD2["cases"]["nominal"]["ensemble"]
_chk = dict(min=(min(_reg), _ens4["fuel_energy_kWh_per_km_min"]),
            median=(float(np.median(_reg)),
                    _ens4["fuel_energy_kWh_per_km_median"]),
            max=(max(_reg), _ens4["fuel_energy_kWh_per_km_max"]))
for k, (a, b) in _chk.items():
    assert abs(a - b) < 1e-12, (
        f"WS11 no longer reproduces WS4's live series_duty_v2 {k}: "
        f"{a!r} vs {b!r}. The hot-swap seam has moved - name the difference "
        f"before reporting any margin.")
R["ws4_regression"] = dict(
    statement=("WS11's V2 nominal VOLT-REG ensemble reproduces WS4's live "
               "interface_ws4.series_duty_v2 [nominal] fuel_energy_kWh_per_km "
               "min/median/max exactly (identical floats)"),
    tolerance=1e-12,
    ws11={k: v[0] for k, v in _chk.items()},
    ws4={k: v[1] for k, v in _chk.items()},
    max_abs_difference=max(abs(a - b) for a, b in _chk.values()),
)
log("regression OK - exact float agreement with the live design input")


# --------------------------------------------------------------- run helpers
def run_pair(vehicle, duty, case, seed, trace=False):
    sp = case_spec(case, vehicle)
    spr = case_spec(case, "ruler")
    cyc = (CYC_CLIMB[seed] if sp["cycle"] == "climb"
           else CYC[duty][seed])
    ru = RU.run_ruler(cyc, spr["m"], veh=spr["veh"], engine=ENG_REF,
                      derate=spr["derate"], p_acc_kw=P.P_ACC_CRANK_KW,
                      trace=trace)
    ca = CA.run_candidate(vehicle, cyc, WS3, CHAIN, m=sp["m"], veh=sp["veh"],
                          derate=sp["derate"], p_aux_kw=sp["aux"],
                          chg_accept_bus_kw=ACC[case], trace=trace)
    return ru, ca, sp, spr


def metrics(out, payload_kg):
    e = out["fuel_energy_kwh"]
    d = out["distance_km"]
    return dict(fuel_energy_kwh=e, distance_km=d,
                per_km=e / d, per_payload_tkm=e / (d * payload_kg / 1000.0),
                l_per_100km=out["fuel_l"] / d * 100.0
                if "fuel_l" in out else out["l_per_100km"])


def envelope(vals, seeds, label, lower_is_better=True):
    v = list(vals)
    i_min = int(np.argmin(v))
    i_max = int(np.argmax(v))
    return {
        "min": v[i_min],
        "median": float(np.median(v)),
        "max": v[i_max],
        "min_governing_case": f"seed {seeds[i_min]} of the enumerated "
                              f"8-seed {label} ensemble",
        "max_governing_case": f"seed {seeds[i_max]} of the enumerated "
                              f"8-seed {label} ensemble",
        "per_seed": {str(s): v[k] for k, s in enumerate(seeds)},
    }


def paired_block(vehicle, duty, case, seeds, trace_seed=None):
    m_ru, m_ca = [], []
    per_km_margin, per_pay_margin = [], []
    ru_ex, ca_ex = None, None
    for s in seeds:
        want_trace = (trace_seed is not None and s == trace_seed)
        ru, ca, sp, spr = run_pair(vehicle, duty, case, s, trace=want_trace)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        m_ru.append(mr)
        m_ca.append(mc)
        per_km_margin.append(100.0 * (mr["per_km"] - mc["per_km"])
                             / mr["per_km"])
        per_pay_margin.append(100.0 * (mr["per_payload_tkm"]
                                       - mc["per_payload_tkm"])
                              / mr["per_payload_tkm"])
        if want_trace:
            ru_ex, ca_ex = ru, ca
    lbl = duty if case != "climb_10km_6pct" else duty + "+CLIMB"
    blk = dict(
        case=case, duty=duty, vehicle=vehicle,
        payload_kg_ruler=case_spec(case, "ruler")["payload_kg"],
        payload_kg_candidate=case_spec(case, vehicle)["payload_kg"],
        mass_kg_ruler=case_spec(case, "ruler")["m"],
        mass_kg_candidate=case_spec(case, vehicle)["m"],
        ruler=dict(
            per_km=envelope([x["per_km"] for x in m_ru], seeds, lbl),
            per_payload_tkm=envelope([x["per_payload_tkm"] for x in m_ru],
                                     seeds, lbl),
            l_per_100km=envelope([x["l_per_100km"] for x in m_ru], seeds,
                                 lbl)),
        candidate=dict(
            per_km=envelope([x["per_km"] for x in m_ca], seeds, lbl),
            per_payload_tkm=envelope([x["per_payload_tkm"] for x in m_ca],
                                     seeds, lbl),
            l_per_100km=envelope([x["l_per_100km"] for x in m_ca], seeds,
                                 lbl)),
        margin_pct_per_km_paired=envelope(per_km_margin, seeds, lbl),
        margin_pct_per_payload_tkm_paired=envelope(per_pay_margin, seeds,
                                                   lbl),
    )
    return blk, ru_ex, ca_ex


# ------------------------------------------------------------- 10 Hz traces
os.makedirs("data", exist_ok=True)
TRACE_FILES = []


def write_trace(name, tr, header_lines):
    path = os.path.join("data", f"trace_{name}_10Hz.csv")
    keys = list(tr.keys())
    n = len(tr[keys[0]])
    with open(path, "w", newline="") as f:
        for h in header_lines:
            f.write("# " + h + "\n")
        f.write(",".join(keys) + "\n")
        cols = [np.asarray(tr[k], float) for k in keys]
        for i in range(n):
            f.write(",".join(f"{c[i]:.4f}" for c in cols) + "\n")
    TRACE_FILES.append(dict(file=f"data/trace_{name}_10Hz.csv", rows=n))
    return path


# ---------------------------------------------------------- headline results
log("headline runs ...")
RESULTS = {}
TRACE_DONE = set()
PRIMARY = [("V1", "VOLT-SUB", CASES),
           ("V2", "VOLT-REG", CASES_REG),
           ("V2", "VOLT-SUB", CASES)]
for vehicle, duty, cases in PRIMARY:
    key = f"{vehicle}_on_{duty}"
    RESULTS[key] = {}
    for case in cases:
        want = (case in ("nominal", "climb_10km_6pct"))
        ts = REF_SEED[duty] if want else None
        blk, ru_ex, ca_ex = paired_block(vehicle, duty, case, SEEDS[duty],
                                         trace_seed=ts)
        RESULTS[key][case] = blk
        log(f"  {key} [{case}] per-payload margin min "
            f"{blk['margin_pct_per_payload_tkm_paired']['min']:+.2f}% "
            f"median "
            f"{blk['margin_pct_per_payload_tkm_paired']['median']:+.2f}%")
        if want and ru_ex is not None:
            tag = f"ruler_{duty}_{case}_seed{ts}"
            if tag not in TRACE_DONE:
                write_trace(tag, ru_ex["trace"], [
                    "Project Volt WS11 - R34 10 Hz trace",
                    f"RULER (stock NPR-HD) / {duty} / {case} / seed {ts}",
                    f"mass {blk['mass_kg_ruler']:.0f} kg, payload "
                    f"{blk['payload_kg_ruler']:.0f} kg, engine "
                    f"{ENG_REF.name}, A465id 6-speed + 4.555 axle"])
                TRACE_DONE.add(tag)
            tag = f"{vehicle}_{duty}_{case}_seed{ts}"
            if tag not in TRACE_DONE:
                write_trace(tag, ca_ex["trace"], [
                    "Project Volt WS11 - R34 10 Hz trace",
                    f"{vehicle} pure series (mode b) / {duty} / {case} / "
                    f"seed {ts}",
                    f"mass {blk['mass_kg_candidate']:.0f} kg, payload "
                    f"{blk['payload_kg_candidate']:.0f} kg; delivered pack "
                    f"{WS3['usable_bus_kWh']:.6f} kWh usable; R16 acceptance "
                    f"{ACC[case]:.3f} kW bus; WS2 r4 662 V map chain; "
                    "all electrical quantities bus-side (R12)"])
                TRACE_DONE.add(tag)
R["results"] = RESULTS

# ------------------------------- payload-corner reading variant + break-even
log("payload-corner reading variant (each vehicle scales its OWN payload) ...")
VARIANT = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    key = f"{vehicle}_on_{duty}"
    VARIANT[key] = {}
    for case in ("payload_p20_own", "payload_m20_own"):
        blk, _, _ = paired_block(vehicle, duty, case, SEEDS[duty])
        VARIANT[key][case] = blk
        log(f"  {key} [{case}] per-payload margin min "
            f"{blk['margin_pct_per_payload_tkm_paired']['min']:+.2f}%")
R["payload_corner_reading_variant"] = dict(
    issue=("'payload +/-20% of ruler payload' has two readings. ORDERED "
           "READING (used for the gate): every vehicle carries the SAME "
           "freight, 1.2 or 0.8 x the RULER's payload, and total mass is "
           "that vehicle's curb + that freight. Under that reading the "
           "payload denominators are equal, so per-payload and per-km "
           "margins COLLAPSE ONTO EACH OTHER at those two corners and the "
           "candidate's curb penalty appears only as extra road load - a "
           "much weaker penalty than the denominator. VARIANT READING: each "
           "vehicle scales ITS OWN payload by +/-20%, which preserves the "
           "denominator penalty and is consistent with the nominal case. "
           "Both are exported; the gate uses the ordered reading; neither "
           "reading changes either verdict. Escalated as ESC-7."),
    ordered_reading_note=("at payload_p20 / payload_m20 the reported per-km "
                          "and per-payload margins are identical BY "
                          "CONSTRUCTION, not by coincidence"),
    variant=VARIANT)

log("break-even curb mass ...")
BREAKEVEN = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    b = RESULTS[f"{vehicle}_on_{duty}"]["nominal"]
    pay_be, curb_be = [], []
    for s in map(str, seeds):
        ratio = (b["candidate"]["per_km"]["per_seed"][s]
                 / b["ruler"]["per_km"]["per_seed"][s])
        pc = PAY["ruler"] * ratio
        pay_be.append(pc)
        curb_be.append(P.M_GVW_KG - pc)
    BREAKEVEN[f"{vehicle}_on_{duty}"] = dict(
        rule=("the candidate curb mass at which the per-payload-tonne-km "
              "margin is exactly zero at nominal, per seed. At fixed GVW the "
              "candidate's curb does not change its energy, so this is "
              "exact, not a search."),
        break_even_payload_kg=envelope(pay_be, seeds, duty),
        break_even_curb_kg=envelope(curb_be, seeds, duty),
        actual_curb_kg=CURB[vehicle],
        headroom_kg_worst=min(curb_be) - CURB[vehicle],
        headroom_kg_worst_governing_case=(
            f"seed {seeds[int(np.argmin(curb_be))]} of the enumerated 8-seed "
            f"{duty} ensemble (min over the enumerated seed set)"))
    log(f"  {vehicle}: break-even curb {min(curb_be):.0f}-{max(curb_be):.0f} kg "
        f"vs actual {CURB[vehicle]} kg "
        f"(headroom {min(curb_be) - CURB[vehicle]:+.0f} kg worst)")
R["break_even_curb"] = BREAKEVEN

# ------------------------------------------------------------------ verdicts
log("verdicts ...")
CRITERION = dict(
    pre_committed=True,
    statement=("ADVANCE only if >= 3% better than the ruler on the "
               "candidate's design duty at nominal, ensemble-min, AND >= 0% "
               "at every corner. Metric: fuel energy per payload tonne-km, "
               "paired per-seed."),
    nominal_threshold_pct=3.0, corner_threshold_pct=0.0,
    form="the same form as Vehicle One's R25/R37 criteria")
VERDICTS = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    key = f"{vehicle}_on_{duty}"
    blocks = RESULTS[key]
    corners = [c for c in blocks if c != "nominal"]
    corner_vals = {c: blocks[c]["margin_pct_per_payload_tkm_paired"]["min"]
                   for c in corners}
    worst_c = min(corner_vals, key=lambda c: corner_vals[c])
    nom = blocks["nominal"]["margin_pct_per_payload_tkm_paired"]
    ok_nom = nom["min"] >= CRITERION["nominal_threshold_pct"]
    ok_cor = corner_vals[worst_c] >= CRITERION["corner_threshold_pct"]
    VERDICTS[key] = dict(
        vehicle=vehicle, design_duty=duty,
        nominal_margin_pct_min=nom["min"],
        nominal_margin_pct_min_governing_case=nom["min_governing_case"],
        nominal_margin_pct_median=nom["median"],
        nominal_margin_pct_max=nom["max"],
        nominal_test_pass=bool(ok_nom),
        corner_case_set=sorted(corners),
        corner_margins_pct_min=corner_vals,
        worst_corner_margin_pct=corner_vals[worst_c],
        worst_corner_governing_case=(
            f"{worst_c} (min over the enumerated corner set "
            f"{sorted(corners)}), itself at "
            f"{blocks[worst_c]['margin_pct_per_payload_tkm_paired']['min_governing_case']}"),
        corner_test_pass=bool(ok_cor),
        verdict="ADVANCE" if (ok_nom and ok_cor) else "KILL",
        margin_vs_nominal_bar_pp=nom["min"] - CRITERION["nominal_threshold_pct"],
        margin_vs_corner_bar_pp=(corner_vals[worst_c]
                                 - CRITERION["corner_threshold_pct"]),
    )
    log(f"  {key}: {VERDICTS[key]['verdict']} "
        f"(nominal min {nom['min']:+.2f}%, worst corner "
        f"{corner_vals[worst_c]:+.2f}% at {worst_c})")
R["advance_kill"] = dict(criterion=CRITERION, verdicts=VERDICTS)

# ------------------------------------------------------------- one-factor
log("one-factor decomposition ...")
ONE = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    key = f"{vehicle}_on_{duty}"
    seeds = SEEDS[duty]
    base = RESULTS[key]["nominal"]
    sp = case_spec("nominal", vehicle)
    spr = case_spec("nominal", "ruler")
    rows = {}

    # (a) mass / payload: the freight given back
    rows["mass_payload_denominator"] = dict(
        description=("the candidate's own curb mass, expressed where it "
                     "acts: the payload denominator. At the fixed 6,600 kg "
                     "GVW both vehicles carry the SAME total mass, so this "
                     "factor moves no energy at all - it moves only the "
                     "freight the energy is divided by."),
        margin_pct_per_km_min=base["margin_pct_per_km_paired"]["min"],
        margin_pct_per_payload_min=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        cost_pp=(base["margin_pct_per_km_paired"]["min"]
                 - base["margin_pct_per_payload_tkm_paired"]["min"]),
        payload_ratio_ruler_over_candidate=PAY["ruler"] / PAY[vehicle],
        payload_kg_ruler=PAY["ruler"], payload_kg_candidate=PAY[vehicle],
        curb_delta_kg=CURB[vehicle] - CURB["ruler"])

    # (b) regen alone
    m_no_regen = []
    for s in seeds:
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                              m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=sp["aux"],
                              chg_accept_bus_kw=ACC["nominal"],
                              regen_cap_kw=0.0)
        ru, _, _, _ = run_pair(vehicle, duty, "nominal", s)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        m_no_regen.append(100.0 * (mr["per_payload_tkm"]
                                   - mc["per_payload_tkm"])
                          / mr["per_payload_tkm"])
    env_nr = envelope(m_no_regen, seeds, duty)
    rows["regen"] = dict(
        description=("regen alone: the candidate re-run with the wheel-side "
                     "regen cap set to zero (all braking to friction and the "
                     "R2 resistor), everything else identical."),
        margin_pct_per_payload_min_with_regen=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_without_regen=env_nr["min"],
        worth_pp=(base["margin_pct_per_payload_tkm_paired"]["min"]
                  - env_nr["min"]),
        envelope_without_regen=env_nr)

    # (c) start-stop / engine-off alone
    m_no_ss = []
    for s in seeds:
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                              m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=sp["aux"],
                              chg_accept_bus_kw=ACC["nominal"],
                              mode="bp", ser_band=(0.999, 1.0))
        ru, _, _, _ = run_pair(vehicle, duty, "nominal", s)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        m_no_ss.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                       / mr["per_payload_tkm"])
    env_ss = envelope(m_no_ss, seeds, duty)
    rows["start_stop_engine_off"] = dict(
        description=("start-stop / engine-off alone: mode (b) pinned "
                     "start-stop against mode (b') - a genset that never "
                     "shuts off and load-follows its best-BSFC locus "
                     "(ser_band forced to (0.999, 1.0) so the engine is "
                     "always on). This is E6's continuous-running "
                     "alternative."),
        margin_pct_per_payload_min_with_start_stop=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_without=env_ss["min"],
        worth_pp=(base["margin_pct_per_payload_tkm_paired"]["min"]
                  - env_ss["min"]),
        envelope_without_start_stop=env_ss)

    # (d) engine operating point (part load) alone
    m_op = []
    bsfc_pin, bsfc_ruler = [], []
    for s in seeds:
        ru, ca, _, _ = run_pair(vehicle, duty, "nominal", s)
        pin_bsfc = ca["pinned"]["bsfc"]
        bsfc_pin.append(pin_bsfc)
        bsfc_ruler.append(ru["mean_bsfc_eff_g_per_kwh"])
        # ruler counterfactual: identical shaft-energy demand, but every
        # gramme burned at the candidate's pinned island BSFC
        fuel_alt_g = ru["eng_kwh"] * pin_bsfc + ru["unserved_fuel_g"]
        e_alt = fuel_alt_g * LHV_KJ_PER_G / 3600.0
        mr_alt = e_alt / (ru["distance_km"] * spr["payload_kg"] / 1000.0)
        mc = metrics(ca, sp["payload_kg"])
        m_op.append(100.0 * (mr_alt - mc["per_payload_tkm"]) / mr_alt)
    env_op = envelope(m_op, seeds, duty)
    rows["engine_operating_point"] = dict(
        description=("engine operating point (part load) alone: the ruler "
                     "re-scored with its OWN shaft-energy demand but every "
                     "gramme burned at the candidate's pinned island BSFC. "
                     "What survives is everything that is not the operating "
                     "point - driveline, regen, idle and the payload "
                     "denominator."),
        ruler_duty_mean_effective_bsfc_g_per_kWh=envelope(
            bsfc_ruler, seeds, duty),
        candidate_pinned_bsfc_g_per_kWh=bsfc_pin[0],
        margin_pct_per_payload_min_actual=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_if_ruler_had_the_island=env_op["min"],
        worth_pp=(base["margin_pct_per_payload_tkm_paired"]["min"]
                  - env_op["min"]),
        envelope_if_ruler_had_the_island=env_op)
    # (c2) start-stop against a genset held ON at its pinned point
    m_no_ss2 = []
    for s in seeds:
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                              m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=sp["aux"],
                              chg_accept_bus_kw=ACC["nominal"],
                              mode="b", ser_band=(0.999, 1.0))
        ru, _, _, _ = run_pair(vehicle, duty, "nominal", s)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        m_no_ss2.append(100.0 * (mr["per_payload_tkm"]
                                 - mc["per_payload_tkm"])
                        / mr["per_payload_tkm"])
    env_ss2 = envelope(m_no_ss2, seeds, duty)
    rows["start_stop_engine_off_pinned_variant"] = dict(
        description=("second counterfactual for the same factor: the genset "
                     "never shuts off but stays AT ITS PINNED POINT (mode "
                     "(b), ser_band forced to (0.999, 1.0)). The two rows "
                     "bracket the factor from opposite directions: (b') "
                     "lets the engine follow load but cannot go below WS4's "
                     "25 kW floor, while this row holds it at the pinned "
                     "point regardless of demand. On a duty whose bus "
                     "average is far below the pin, the pinned row is the "
                     "harsher of the two. The gap between them is a "
                     "DISPATCH result, not an architectural one - it is "
                     "R22b's question and WS5 owns it."),
        margin_pct_per_payload_min_without=env_ss2["min"],
        worth_pp=(base["margin_pct_per_payload_tkm_paired"]["min"]
                  - env_ss2["min"]),
        envelope_without_start_stop=env_ss2)
    ONE[key] = rows
    log(f"  {key} one-factor: mass {rows['mass_payload_denominator']['cost_pp']:+.2f} pp, "
        f"regen {rows['regen']['worth_pp']:+.2f} pp, "
        f"start-stop {rows['start_stop_engine_off']['worth_pp']:+.2f} pp, "
        f"operating point {rows['engine_operating_point']['worth_pp']:+.2f} pp")
R["one_factor"] = ONE

# ------------------------------------------------------------- trip time R38
log("trip time (R38) ...")
TRIP = {}
CAND_MODELS = {"V1": (ENG_V1, GEN_V1), "V2": (ENG_V2, GEN_V2)}
for vehicle, duty, case in (("V1", "VOLT-SUB", "nominal"),
                            ("V2", "VOLT-REG", "nominal"),
                            ("V2", "VOLT-REG", "climb_10km_6pct")):
    seeds = SEEDS[duty]
    eng, gen = CAND_MODELS[vehicle]
    sp = case_spec(case, vehicle)
    spr = case_spec(case, "ruler")
    ratios, ru_t, ca_t, ru_sf, ca_sf = [], [], [], [], []
    ru_climb, ca_climb = [], []
    for s in seeds:
        cyc = CYC_CLIMB[s] if sp["cycle"] == "climb" else CYC[duty][s]
        rt = KP.ruler_trip(cyc, spr["m"], ENG_REF, spr["derate"], spr["veh"],
                           P.P_ACC_CRANK_KW)
        ct = KP.candidate_trip(cyc, sp["m"], eng, gen, CHAIN, CAP_RPM,
                               CAP_TRQ, sp["veh"], sp["derate"],
                               WS3["usable_bus_kWh"], sp["aux"],
                               ser_band=CA.ser_band_for(vehicle, WS3))
        ratios.append(ct["trip_time_s"] / rt["trip_time_s"])
        ru_t.append(rt["trip_time_s"])
        ca_t.append(ct["trip_time_s"])
        ru_sf.append(rt["distance_shortfall_m"])
        ca_sf.append(ct["distance_shortfall_m"])
        ru_climb.append(rt["settled_speed_on_sustained_climb_kmh"])
        ca_climb.append(ct["settled_speed_on_sustained_climb_kmh"])
    lbl = duty if case != "climb_10km_6pct" else duty + "+CLIMB"
    TRIP[f"{vehicle}_on_{duty}[{case}]"] = dict(
        vehicle=vehicle, duty=duty, case=case,
        basis=("time-parameterised capability run; trip time = demanded "
               "duration + (distance shortfall)/(route demanded average "
               "moving speed). R38 is a GATE, not a term in the metric; the "
               "lead applies the <= +5% test."),
        ratio_candidate_over_ruler=envelope(ratios, seeds, lbl),
        ratio_worst=max(ratios),
        ratio_worst_governing_case=(
            f"seed {seeds[int(np.argmax(ratios))]} of the enumerated 8-seed "
            f"{lbl} ensemble (max over the enumerated seed set)"),
        pct_worse_than_ruler_worst=100.0 * (max(ratios) - 1.0),
        r38_gate_pct=5.0,
        r38_gate_met=bool(100.0 * (max(ratios) - 1.0) <= 5.0),
        ruler_trip_time_s=envelope(ru_t, seeds, lbl),
        candidate_trip_time_s=envelope(ca_t, seeds, lbl),
        ruler_distance_shortfall_m=envelope(ru_sf, seeds, lbl),
        candidate_distance_shortfall_m=envelope(ca_sf, seeds, lbl),
        ruler_settled_speed_on_6pct_kmh=(
            envelope(ru_climb, seeds, lbl)
            if all(x is not None for x in ru_climb) else None),
        candidate_settled_speed_on_6pct_kmh=(
            envelope(ca_climb, seeds, lbl)
            if all(x is not None for x in ca_climb) else None),
    )
    log(f"  {vehicle}/{duty}[{case}] trip-time ratio worst "
        f"{max(ratios):.5f} ({100.0 * (max(ratios) - 1.0):+.3f}%)")

# sustainable (buffer-independent) 6% capability - the D16/WS1 s4.4 question
log("sustained 6% capability ...")


def sustained_speed(force_of_v, m, veh, grade):
    lo, hi = 0.1, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_res = KP._road_load_N(mid, grade, m, veh)
        if force_of_v(mid) > f_res:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) * 3.6


_f_ru, _ = KP.ruler_force_table(ENG_REF, 1.0, VEH, P.P_ACC_CRANK_KW)
_f_mot = KP.motor_force_table(CHAIN, CAP_RPM, CAP_TRQ, VEH)
_eta_tab = np.asarray(CHAIN.eta_bus_to_wheel(
    KP._V_MS, np.full_like(KP._V_MS, 60.0)), float)
SUSTAINED = dict(
    basis=("steady speed at which available tractive force equals road load "
           "on a 6% grade at GVW 6,600 kg, sea level. For the candidates the "
           "pack contributes NOTHING - the genset is at its derated "
           "continuous rating, which is the only power available for an "
           "indefinite climb (WS1 s4.4 / D16)."),
    grade_pct=6.0, mass_kg=P.M_GVW_KG,
    ruler_kmh=sustained_speed(
        lambda v: float(np.interp(v * 3.6, KP.V_TABLE_KMH, _f_ru)),
        P.M_GVW_KG, VEH, 0.06))
for vehicle in ("V1", "V2"):
    eng, gen = CAND_MODELS[vehicle]
    p_bus_cont = float(gen.elec_from_shaft(eng.rated_cont_rpm,
                                           eng.rated_cont_kw))

    def f_of_v(v, p_bus_cont=p_bus_cont):
        eta = float(np.interp(v * 3.6, KP.V_TABLE_KMH, _eta_tab))
        return min(max(0.0, p_bus_cont - 2.0) * eta * 1e3 / max(v, 0.5),
                   float(np.interp(v * 3.6, KP.V_TABLE_KMH, _f_mot)),
                   VEH.F_trac_max)
    SUSTAINED[f"{vehicle}_kmh"] = sustained_speed(f_of_v, P.M_GVW_KG, VEH,
                                                  0.06)
    SUSTAINED[f"{vehicle}_genset_bus_kW_continuous"] = p_bus_cont
R["trip_time_r38"] = TRIP
R["sustained_6pct_capability"] = SUSTAINED
log(f"  sustained 6%: ruler {SUSTAINED['ruler_kmh']:.1f} km/h, "
    f"V1 {SUSTAINED['V1_kmh']:.1f}, V2 {SUSTAINED['V2_kmh']:.1f}")

# ------------------------------------------------- ruler calibration + brackets
log("ruler calibration against the sourced anchor, and ruler brackets ...")
ANCHOR_ALL = P.anchor_stats()
ANCHOR_4HK1 = P.anchor_stats(
    [r for r in P.RULER_FUEL_ANCHOR["rows"]
     if r[0] in P.RULER_FUEL_ANCHOR["fourhk1_era_years"]])

BRACKETS = {
    "headline_ruler_favourable": dict(),
    "physical_accessories": dict(p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL),
    "converter_stalled_at_idle": dict(idle_neutral=False),
    "CdA_5.4": dict(cda=5.4),
    "sequential_shift_schedule": dict(shift_schedule="sequential"),
    "rotating_inertia_charged": dict(charge_rot=True),
    "all_ruler_favourable_choices_reversed": dict(
        p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL, idle_neutral=False, cda=5.4,
        shift_schedule="sequential", charge_rot=True),
}


def ruler_bracket_run(duty, seed, spec):
    veh = VEH if "cda" not in spec else dataclasses.replace(
        VEH, CdA=spec["cda"])
    o = RU.run_ruler(CYC[duty][seed], P.M_GVW_KG, veh=veh, engine=ENG_REF,
                     derate=1.0,
                     p_acc_kw=spec.get("p_acc_kw", P.P_ACC_CRANK_KW),
                     idle_neutral=spec.get("idle_neutral", True),
                     shift_schedule=spec.get("shift_schedule",
                                             "fuel_optimal"))
    if spec.get("charge_rot"):
        eta_marg = max(P.ETA_GEAR) * P.ETA_FINAL * (1.0 - P.LOCKUP_SLIP_LOSS)
        add_g = (o["e_rot_extra_wheel_kwh"] / eta_marg
                 * o["mean_bsfc_eff_g_per_kwh"])
        o = dict(o)
        o["fuel_g"] = o["fuel_g"] + add_g
        o["fuel_l"] = o["fuel_g"] / P.DENSITY_G_PER_L
        o["fuel_energy_kwh"] = o["fuel_g"] * LHV_KJ_PER_G / 3600.0
        o["l_per_100km"] = o["fuel_l"] / o["distance_km"] * 100.0
        o["fuel_energy_kWh_per_km"] = (o["fuel_energy_kwh"]
                                       / o["distance_km"])
        o["rot_inertia_fuel_g"] = add_g
    return o


CAL = {"anchor": dict(P.RULER_FUEL_ANCHOR, rows=[list(r) for r in
                                                 P.RULER_FUEL_ANCHOR["rows"]]),
       "anchor_distance_weighted_all_years": ANCHOR_ALL,
       "anchor_distance_weighted_4HK1_era": ANCHOR_4HK1,
       "method": ("NO parameter of the ruler was tuned to the anchor or to "
                  "the assignment's 18-30 L/100 km corridor. Every ruler "
                  "parameter is SOURCED (axle ratio, gear ratios, lock-up "
                  "range, engine, tyre, GVWR, chassis mass) or WS11-DECLARED "
                  "on a physical argument with its direction of error "
                  "stated. The anchor is a validation, not a fit."),
       "brackets": {}}
for name, spec in BRACKETS.items():
    per_duty = {}
    for duty in ("VOLT-SUB", "VOLT-REG"):
        seeds = SEEDS[duty]
        vals = [ruler_bracket_run(duty, s, spec)["l_per_100km"]
                for s in seeds]
        ev = [ruler_bracket_run(duty, s, spec)["fuel_energy_kWh_per_km"]
              for s in seeds]
        per_duty[duty] = dict(l_per_100km=envelope(vals, seeds, duty),
                              fuel_energy_kWh_per_km=envelope(ev, seeds,
                                                              duty))
    CAL["brackets"][name] = per_duty
    log(f"  ruler bracket {name}: VOLT-SUB median "
        f"{per_duty['VOLT-SUB']['l_per_100km']['median']:.2f} L/100km, "
        f"VOLT-REG median "
        f"{per_duty['VOLT-REG']['l_per_100km']['median']:.2f}")

_hl = CAL["brackets"]["headline_ruler_favourable"]
_rev = CAL["brackets"]["all_ruler_favourable_choices_reversed"]
CAL["corridor_check"] = dict(
    corridor_l_per_100km=[18.0, 30.0],
    ruler_VOLT_SUB_headline_median=_hl["VOLT-SUB"]["l_per_100km"]["median"],
    ruler_VOLT_SUB_headline_min=_hl["VOLT-SUB"]["l_per_100km"]["min"],
    ruler_VOLT_SUB_headline_max=_hl["VOLT-SUB"]["l_per_100km"]["max"],
    inside_corridor=bool(
        18.0 <= _hl["VOLT-SUB"]["l_per_100km"]["min"] <= 30.0
        and 18.0 <= _hl["VOLT-SUB"]["l_per_100km"]["max"] <= 30.0),
    ruler_VOLT_SUB_all_reversed_median=(
        _rev["VOLT-SUB"]["l_per_100km"]["median"]),
    residual_vs_anchor_pct_headline=100.0 * (
        _hl["VOLT-SUB"]["l_per_100km"]["median"]
        / ANCHOR_ALL["l_per_100km"] - 1.0),
    residual_vs_anchor_pct_all_reversed=100.0 * (
        _rev["VOLT-SUB"]["l_per_100km"]["median"]
        / ANCHOR_ALL["l_per_100km"] - 1.0),
    reading=("the model reads BELOW the in-use anchor on both settings, and "
             "the residual is in the RULER's favour, so every candidate "
             "margin in this report is a lower bound. The anchor is a "
             "crowdsourced in-use aggregate over an unknown duty, load and "
             "body mix and cannot resolve a drive-cycle-specific "
             "calibration - escalated (ESC-1)."),
)
R["ruler_calibration"] = CAL

# effect of the brackets on the headline verdicts, on each design duty
log("bracket effect on the verdicts ...")
BRK_MARGIN = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    sp = case_spec("nominal", vehicle)
    spr = case_spec("nominal", "ruler")
    cand = {}
    for s in seeds:
        cand[s] = metrics(CA.run_candidate(
            vehicle, CYC[duty][s], WS3, CHAIN, m=sp["m"], veh=sp["veh"],
            derate=sp["derate"], p_aux_kw=sp["aux"],
            chg_accept_bus_kw=ACC["nominal"]), sp["payload_kg"])
    rows = {}
    for name, spec in BRACKETS.items():
        mg = []
        for s in seeds:
            ru = ruler_bracket_run(duty, s, spec)
            # a CdA bracket changes the ROAD, so the candidate must see it too
            if "cda" in spec:
                ca = CA.run_candidate(
                    vehicle, CYC[duty][s], WS3, CHAIN, m=sp["m"],
                    veh=dataclasses.replace(VEH, CdA=spec["cda"]),
                    derate=sp["derate"], p_aux_kw=sp["aux"],
                    chg_accept_bus_kw=ACC["nominal"])
                mc = metrics(ca, sp["payload_kg"])
            else:
                mc = cand[s]
            mr_pp = ru["fuel_energy_kwh"] / (ru["distance_km"]
                                             * spr["payload_kg"] / 1000.0)
            mg.append(100.0 * (mr_pp - mc["per_payload_tkm"]) / mr_pp)
        rows[name] = envelope(mg, seeds, duty)
    BRK_MARGIN[f"{vehicle}_on_{duty}"] = rows
    log(f"  {vehicle}/{duty}: headline min "
        f"{rows['headline_ruler_favourable']['min']:+.2f}%, all-reversed min "
        f"{rows['all_ruler_favourable_choices_reversed']['min']:+.2f}%")
R["ruler_bracket_effect_on_margin"] = dict(
    note=("per-payload-tonne-km margin, paired per-seed, at nominal on each "
          "candidate's design duty, recomputed with each ruler bracket. The "
          "headline row is the RULER-FAVOURABLE setting used everywhere "
          "else in this report; every other row raises the candidate's "
          "margin, which is what 'lower bound' means."),
    rows=BRK_MARGIN)

# ---------------------------------------------- cold cab-heat bracket (R30)
log("cold corner cab-heat bracket ...")
COLDB = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    sp = case_spec("cold_-10C", vehicle)
    spr = case_spec("cold_-10C", "ruler")
    mg, aux_used, onfrac = [], [], []
    for s in seeds:
        base = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                                m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                                p_aux_kw=sp["aux"],
                                chg_accept_bus_kw=ACC["cold_-10C"])
        f_off = 1.0 - base["eng_on_frac"]
        aux = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * f_off
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                              m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=aux,
                              chg_accept_bus_kw=ACC["cold_-10C"])
        ru = RU.run_ruler(CYC[duty][s], spr["m"], veh=spr["veh"],
                          engine=ENG_REF, derate=spr["derate"],
                          p_acc_kw=P.P_ACC_CRANK_KW)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        mg.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                  / mr["per_payload_tkm"])
        aux_used.append(aux)
        onfrac.append(base["eng_on_frac"])
    COLDB[f"{vehicle}_on_{duty}"] = dict(
        description=(f"[WS11-DECLARED, NOT ORDERED] the R30 cab-heat member "
                     f"applied to Vehicle Zero: {P.CAB_HEAT_KW_AT_MINUS10} kW "
                     f"of cab heat at -10 C, free from engine coolant on the "
                     f"ruler and free from genset coolant on the candidate "
                     f"WHILE THE GENSET RUNS, electric at the bus otherwise. "
                     f"The assignment orders the cold corner as 'WS3 cold "
                     f"acceptance applied', which this exceeds - reported "
                     f"beside the ordered corner, never inside the gate, and "
                     f"escalated (ESC-2)."),
        genset_on_fraction=envelope(onfrac, seeds, duty),
        aux_kW_used=envelope(aux_used, seeds, duty),
        margin_pct_per_payload_tkm_paired=envelope(mg, seeds, duty),
        margin_ordered_corner=(RESULTS[f"{vehicle}_on_{duty}"]["cold_-10C"]
                               ["margin_pct_per_payload_tkm_paired"]["min"]),
    )
    log(f"  {vehicle} cold + cab heat: min "
        f"{COLDB[f'{vehicle}_on_{duty}']['margin_pct_per_payload_tkm_paired']['min']:+.2f}%")
R["cold_cab_heat_bracket"] = COLDB

# --------------------------------------------------- heat ledger for WS6 (R9)
log("heat ledger ...")
LEDGER_ROWS = []
for vehicle, duty, cases in PRIMARY:
    for case in cases:
        seeds = SEEDS[duty]
        sp = case_spec(case, vehicle)
        spr = case_spec(case, "ruler")
        acc = {k: [] for k in ("ru_eng", "ru_dl", "ru_fric", "ca_eng",
                               "ca_gen", "ca_chain", "ca_fric", "ca_bus")}
        dur = []
        for s in seeds:
            ru, ca, _, _ = run_pair(vehicle, duty, case, s)
            acc["ru_eng"].append(ru["eng_reject_kwh"])
            acc["ru_dl"].append(ru["eng_kwh"] - ru["e_trac_wheel_kwh"])
            acc["ru_fric"].append(ru["e_brake_wheel_kwh"])
            acc["ca_eng"].append(ca["eng_reject_kwh"])
            acc["ca_gen"].append(ca["e_gen_loss_kwh"])
            acc["ca_chain"].append(ca["e_chain_loss_kwh"])
            acc["ca_fric"].append(ca["e_fric_kwh"])
            acc["ca_bus"].append(ca["e_bus_kwh"])
            dur.append(ru["duration_s"])
        h = float(np.median(dur)) / 3600.0
        for comp, key, owner in (
                ("ruler engine (fuel - shaft)", "ru_eng", "ruler"),
                ("ruler driveline + accessories (shaft - wheel)", "ru_dl",
                 "ruler"),
                ("ruler friction brakes (all braking energy)", "ru_fric",
                 "ruler"),
                (f"{vehicle} genset engine (fuel - shaft)", "ca_eng",
                 vehicle),
                (f"{vehicle} generator + rectifier", "ca_gen", vehicle),
                (f"{vehicle} traction chain (inverter+motor+reduction)",
                 "ca_chain", vehicle),
                (f"{vehicle} R15 blend overflow (resistor + friction)",
                 "ca_fric", vehicle)):
            v = acc[key]
            LEDGER_ROWS.append(dict(
                vehicle=owner, duty=duty, case=case, component=comp,
                heat_kWh_per_cycle_min=min(v),
                heat_kWh_per_cycle_median=float(np.median(v)),
                heat_kWh_per_cycle_max=max(v),
                mean_kW_over_cycle_max=max(v) / h,
                max_governing_case=(f"seed {seeds[int(np.argmax(v))]} of the "
                                    f"enumerated 8-seed {duty} ensemble "
                                    f"[{case}]")))
R["heat_ledger_ws6"] = dict(
    convention=("R9: rejected heat by component and operating case. Energies "
                "are per cycle realisation; mean kW is over the cycle "
                "duration. WS6 sizes to its own steady lines, not to these "
                "cycle averages. The pack loop is WS3's export and is not "
                "re-derived here."),
    rows=LEDGER_ROWS)

# ------------------------------------------------------------- escalations
R["escalations"] = [
    dict(id="ESC-1", challenges="the assignment's ruler-anchor requirement",
         title="The only public NPR fuel-economy reference I could obtain is "
               "a crowdsourced in-use aggregate, and it cannot calibrate a "
               "drive cycle",
         text=("The assignment makes a sourced public anchor mandatory and "
               "forbids a corridor fit. I obtained one: Fuelly's Isuzu "
               "NPR-HD page (owner fuel logs), distance-weighted over its "
               "own per-model-year table to "
               f"{ANCHOR_ALL['mpg']:.3f} mpg = "
               f"{ANCHOR_ALL['l_per_100km']:.2f} L/100 km over "
               f"{ANCHOR_ALL['miles']:,} miles. I also obtained the "
               "manufacturer's own 2023 NPR-HD specification sheet, which "
               "fixes the axle ratio, transmission, lock-up range, engine, "
               "tyre, GVWR and chassis mass - but publishes NO fuel "
               "economy, because US medium-duty trucks are not fuel-economy "
               "rated. What I could NOT obtain is a cycle-resolved NPR "
               "measurement. The anchor's duty, load, body and driver mix "
               "are unknown; 56% of its tracked miles are a MY2002 truck "
               "with the earlier 4HE1 engine. Its 4HK1-era subset alone "
               f"reads {ANCHOR_4HK1['l_per_100km']:.2f} L/100 km. I have "
               "therefore used it as a VALIDATION with the residual stated, "
               "not as a calibration target, and tuned nothing to it. The "
               "lead should know that the ruler's absolute level rests on "
               "declared physics, not on a measured NPR."),
         requested=("either accept the validation-not-fit treatment on the "
                    "record, or fund a cycle-resolved chassis-dyno or "
                    "logged-route measurement of an NPR-HD as a WS7 item")),
    dict(id="ESC-2", challenges="R30 / D19 (Vehicle One doctrine) as applied "
                                "to Vehicle Zero",
         title="The cold corner as ordered does not charge cab heat; I have "
               "bracketed it rather than smuggling it into the gate",
         text=("BASELINE_v4 R30 makes pack preconditioning and a "
               "coolant/waste-heat cab path a modelled requirement for every "
               "Vehicle One electrified candidate, on the ground that 'the "
               "conventional truck heats itself for free and the comparison "
               "must charge that'. My assignment orders the Vehicle Zero "
               "cold corner as '-10 C with WS3 cold acceptance applied' and "
               "orders no cab-heat member. Vehicle Zero's candidates are not "
               "BEVs - both carry a running diesel, so the cab path is free "
               "whenever the genset runs and electric only in the "
               "engine-off windows. I have run the corner exactly as "
               "ordered for the gate and exported the cab-heat member as a "
               "declared bracket beside it. The lead should rule whether "
               "R30 extends to Vehicle Zero; if it does, the bracket "
               "becomes the corner of record."),
         requested="a ruling extending or not extending R30 to Vehicle Zero"),
    dict(id="ESC-3", challenges="WS4 interface_ws4.v2_genset.mass_kg",
         title="WS4's `aftertreatment_extra: 60 kg` is ambiguous and it moves "
               "V2's payload by 60 kg",
         text=("WS4 exports the V2 genset as total_dry 637 kg PLUS a "
               "separate `aftertreatment_extra: 60.0`. The 4HK1-V2C is "
               "declared to be the same production hardware as the ruler's "
               "4HK1-TC, so on one reading its aftertreatment is the stock "
               "truck's aftertreatment and cancels; on the other reading it "
               "is 60 kg the candidate carries and the ruler does not. "
               "60 kg is 2.4% of V2's payload and therefore 2.4 points of "
               "the metric of record. I have taken the cancelling reading "
               "for the headline (the reading FAVOURABLE to the candidate) "
               "and exported the other as a bracket. V2's verdict does not "
               "turn on it, but the lead should close the ambiguity before "
               "any later candidate does."),
         requested="a ruling on whether `aftertreatment_extra` is incremental "
                   "to a stock 4HK1 installation"),
    dict(id="ESC-4", challenges="BASELINE_v1 vehicle parameters (CdA 4.2, "
                                "PROVISIONAL pending WS7 coastdown)",
         title="The whole Vehicle Zero comparison is being run at a CdA that "
               "the baseline itself calls provisional, and the ruler is the "
               "vehicle that suffers",
         text=("CdA 4.2 m^2 is a WS1 fitted value, declared PROVISIONAL in "
               "BASELINE_v1 pending the WS7 coastdown, and the program "
               "already carries CdA 5.4 as a sizing case (E13). A 16 ft "
               "dry-freight box on an NPR-HD cab is a 5-6 m^2 object. Aero "
               "work is the one load a series hybrid cannot recover, so a "
               "larger CdA moves the comparison AGAINST the candidates. My "
               "CdA 5.4 bracket is exported for both duties. The coastdown "
               "is not a nicety here: it is the single input most able to "
               "move a Vehicle Zero verdict."),
         requested="WS7 coastdown scheduled before any Vehicle Zero "
                   "efficiency claim is ratified"),
    dict(id="ESC-5", challenges="R9 (ensembles) and the demand-trace "
                                "convention inherited from Gate G1",
         title="The metric of record cannot see time, and on the sustained "
               "climb that hides the real difference between these vehicles",
         text=("Every fuel number here follows the identical demanded "
               "wheel-power trace, with shortfalls booked as unserved energy "
               "and fuel-corrected - the convention WS4's ratified simulator "
               "uses, adopted so the two vehicles are differenced without a "
               "convention step. It is the right convention for energy and "
               "the wrong one for capability. On WS1 s4.4's 10 km 6% climb "
               f"the ruler settles at {SUSTAINED['ruler_kmh']:.1f} km/h and "
               f"holds it indefinitely; V2 holds the demanded speed only "
               f"while its buffer lasts and its genset-only sustainable "
               f"speed is {SUSTAINED['V2_kmh']:.1f} km/h. Make the climb "
               "20 km instead of 10 and the sign of that comparison "
               "changes. R38's trip-time gate catches some of this; it does "
               "not catch a candidate that passes a 10 km climb and fails a "
               "20 km one. I have exported the sustained-capability numbers "
               "separately so the lead can see what the metric cannot."),
         requested="a ruling on whether a sustained-gradeability floor joins "
                   "the Vehicle Zero criteria, as D16 did for Vehicle One"),
    dict(id="ESC-6", challenges="R32's own framing",
         title="R32 asks whether the Vehicle Zero design is more efficient "
               "than the truck it replaces; the answer is duty-indexed and "
               "the two variants land on opposite sides",
         text=("D15 says architecture is duty-indexed. This trial confirms "
               "it inside a single vehicle programme: V1 on its suburban "
               "duty and V2 on its regional duty return verdicts of "
               "opposite sign on the same criterion, the same ruler and the "
               "same code. Any sentence of the form 'Vehicle Zero is more "
               "efficient than an NPR-HD' is false without the duty and the "
               "variant attached. I ask that the baseline record the answer "
               "to R32 as a pair of duty-indexed results, not as a "
               "programme-level claim."),
         requested="baseline wording that names the duty and the variant"),
    dict(id="ESC-7", challenges="the assignment's corner definition",
         title="'payload +/-20% of ruler payload' erases the metric's own "
               "penalty at two of the four corners",
         text=("Read literally - and I have gated on the literal reading - "
               "the payload corners put the SAME freight on the ruler and on "
               "the candidate. The payload denominators are then equal, so "
               "at those two corners the per-payload metric IS the per-km "
               "metric and the candidate's curb penalty shows up only as "
               "extra road load, which is several times weaker. The visible "
               "symptom is that V2 scores +6.27% and +7.21% at the two "
               "payload corners while scoring -7.93% at nominal on the same "
               "metric. I have exported the variant reading (each vehicle "
               "scales its own payload), which preserves the denominator and "
               "is consistent with the nominal convention. Neither verdict "
               "changes under either reading, so nothing here is load-"
               "bearing tonight - but the next candidate set should not "
               "inherit a corner that switches the metric off."),
         requested="a ruling fixing the payload-corner convention for "
                   "Vehicle Zero and Vehicle One alike"),
]

# ------------------------------------------------------- R14 interface block
log("interface block ...")


def _v(vehicle, duty, case, metric="margin_pct_per_payload_tkm_paired"):
    return RESULTS[f"{vehicle}_on_{duty}"][case][metric]


INTERFACE = dict(
    _basis=("mirrors WS1/WS4 results.json conventions; extrema are 8-seed "
            "ensemble envelopes (R9); every worst-case field is an explicit "
            "max/min over an enumerated case set with the governing case "
            "labelled inline (R14); electrical quantities bus-side (R12); "
            "the metric of record is fuel energy per PAYLOAD tonne-km on the "
            "PAIRED per-seed statistic (R36/D13)"),
    _status="ruler_trial_result_pending_adjudication_and_ratification",
    question_of_record=("is the ratified Vehicle Zero design more efficient "
                        "than the truck it replaces, on the honest metric?"),
    ruler=dict(
        identity="stock Isuzu NPR-HD, 4HK1-TC + Aisin A465id 6-speed "
                 "torque-converter automatic (lock-up 2nd-6th) + 4.555 axle",
        engine_map="WS4 4HK1-TC-ref-W Willans map, "
                   f"{WS4J['bsfc_maps']['4HK1-TC-ref-W']['map_min']['bsfc']:.3f}"
                   " g/kWh island",
        sourced_specification_url=P.RULER_SOURCED["url"],
        anchor=dict(
            name=P.RULER_FUEL_ANCHOR["name"],
            url=P.RULER_FUEL_ANCHOR["url"],
            distance_weighted_mpg=ANCHOR_ALL["mpg"],
            distance_weighted_l_per_100km=ANCHOR_ALL["l_per_100km"],
            miles=ANCHOR_ALL["miles"],
            fuel_ups=ANCHOR_ALL["fuel_ups"],
            vehicles_on_page=21,
            is_a_fit=False,
            residual_vs_model_pct=CAL["corridor_check"]
            ["residual_vs_anchor_pct_headline"]),
        curb_kg=CURB["ruler"], payload_at_gvw_kg=PAY["ruler"],
        l_per_100km_VOLT_SUB=_hl["VOLT-SUB"]["l_per_100km"],
        l_per_100km_VOLT_REG=_hl["VOLT-REG"]["l_per_100km"],
        declared_choices_are_ruler_favourable=True),
    masses=dict(gvw_kg=P.M_GVW_KG,
                curb_kg={k: CURB[k] for k in CURB},
                payload_at_gvw_kg={k: PAY[k] for k in PAY}),
    verdicts=VERDICTS,
    trip_time_r38={k: dict(
        ratio_worst=v["ratio_worst"],
        ratio_worst_governing_case=v["ratio_worst_governing_case"],
        pct_worse_than_ruler_worst=v["pct_worse_than_ruler_worst"],
        gate_met=v["r38_gate_met"]) for k, v in TRIP.items()},
    sustained_6pct_capability_kmh=dict(
        rule="steady speed on a 6% grade at GVW with NO buffer contribution",
        ruler=SUSTAINED["ruler_kmh"], V1=SUSTAINED["V1_kmh"],
        V2=SUSTAINED["V2_kmh"],
        worst_case_value=min(SUSTAINED["ruler_kmh"], SUSTAINED["V1_kmh"],
                             SUSTAINED["V2_kmh"]),
        governing_case=min(
            (("ruler", SUSTAINED["ruler_kmh"]), ("V1", SUSTAINED["V1_kmh"]),
             ("V2", SUSTAINED["V2_kmh"])), key=lambda x: x[1])[0]),
    break_even_curb_kg={k: dict(
        worst=v["break_even_curb_kg"]["min"],
        worst_governing_case=v["break_even_curb_kg"]["min_governing_case"],
        median=v["break_even_curb_kg"]["median"],
        actual=v["actual_curb_kg"],
        headroom_kg_worst=v["headroom_kg_worst"])
        for k, v in BREAKEVEN.items()},
    payload_corner_variant_margin_pct_min={
        k: {c: b["margin_pct_per_payload_tkm_paired"]["min"]
            for c, b in v.items()} for k, v in VARIANT.items()},
    ws4_hot_swap_seam=R["ws4_regression"],
    input_sha256=INPUT_SHA,
    traces_r34=TRACE_FILES,
)
R["interface_ws11"] = INTERFACE

# ------------------------------------------------------- sanity checks (R9)
log("first-principles sanity checks ...")
_v85 = 85.0 / 3.6
_f85 = (0.5 * VEH.rho_air * VEH.CdA * _v85 ** 2 + VEH.Crr * P.M_GVW_KG * 9.81)
_n6 = _v85 / VEH.r_dyn * P.AXLE_RATIO * P.GEAR_RATIOS[5] * 60.0 / (2 * np.pi)
SANITY = dict(
    cruise_85kmh_force_N=_f85,
    cruise_85kmh_wheel_kW=_f85 * _v85 / 1e3,
    ws1_baseline_says="~2.0 kN, ~47 kW",
    ws1_crosscheck_wheel_kW=json.load(open(UPSTREAM["WS1/results.json"]))
    ["baseline_crosscheck"]["cruise85_wheel_kW"],
    ruler_engine_rpm_at_85kmh_top_gear=_n6,
    ruler_engine_rpm_at_100kmh_top_gear=_n6 * 100.0 / 85.0,
    comment_rpm=("a 4.555 axle through the 0.63 top gear puts the 4HK1 at "
                 "the speeds a real NPR-HD cruises at - the sourced "
                 "driveline reproduces the sourced vehicle without any "
                 "fitting"),
    payload_arithmetic=dict(
        gvw_kg=P.M_GVW_KG, ruler_curb=CURB["ruler"],
        ruler_payload=PAY["ruler"],
        check=bool(abs(CURB["ruler"] + PAY["ruler"] - P.M_GVW_KG) < 1e-9)),
    per_km_vs_per_payload_identity=dict(
        rule=("1 - margin_payload = (1 - margin_km) x payload_ruler / "
              "payload_candidate, exactly, on every seed"),
        checked=True),
    energy_scale=dict(
        volt_sub_tractive_wheel_kWh_ws1=json.load(
            open(UPSTREAM["WS1/results.json"]))["cycles"]["VOLT-SUB"]
        ["E_tractive_kWh"],
        volt_reg_tractive_wheel_kWh_ws1=json.load(
            open(UPSTREAM["WS1/results.json"]))["cycles"]["VOLT-REG"]
        ["E_tractive_kWh"]),
)
# verify the per-km / per-payload identity numerically on every stored block
_worst_id = 0.0
for key, blocks in RESULTS.items():
    veh = key.split("_on_")[0]
    for case, blk in blocks.items():
        rr = blk["payload_kg_ruler"] / blk["payload_kg_candidate"]
        for s, mk in blk["margin_pct_per_km_paired"]["per_seed"].items():
            mp = blk["margin_pct_per_payload_tkm_paired"]["per_seed"][s]
            lhs = 1.0 - mp / 100.0
            rhs = (1.0 - mk / 100.0) * rr
            _worst_id = max(_worst_id, abs(lhs - rhs))
SANITY["per_km_vs_per_payload_identity"]["max_abs_residual"] = _worst_id
assert _worst_id < 1e-12, "per-km / per-payload identity broken"
R["sanity_checks"] = SANITY
log(f"  per-km/per-payload identity residual {_worst_id:.3e}")

# ------------------------------------------------------------------- CSVs
log("writing CSVs ...")


def write_csv(name, header, rows):
    with open(os.path.join("data", name), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


rows = []
for item, kg, src in P.RULER_LEDGER:
    rows.append(["ruler", "build", item, f"{kg}", src])
for item, kg, src in P.DELETED_COMMON:
    rows.append(["V1+V2", "deleted", item, f"-{kg}", src])
for item, kg, src in P.V1_DELETED:
    rows.append(["V1", "deleted", item, f"-{kg}", src])
for item, kg, src in P.ADDED_COMMON:
    rows.append(["V1+V2", "added", item, f"+{kg}", src])
for item, kg, src in P.V1_ADDED:
    rows.append(["V1", "added", item, f"+{kg}", src])
for item, kg, src in P.V2_ADDED:
    rows.append(["V2", "added", item, f"+{kg}", src])
for k in ("ruler", "V1", "V2", "V2_aftertreatment_bracket"):
    rows.append([k, "TOTAL curb", "", f"{CURB[k]:.0f}", ""])
    rows.append([k, "TOTAL payload at GVW 6600", "", f"{PAY[k]:.0f}", ""])
write_csv("mass_ledger.csv",
          ["vehicle", "kind", "item", "kg", "source"], rows)

rows = []
for key, blocks in RESULTS.items():
    for case, b in blocks.items():
        rows.append([
            b["vehicle"], b["duty"], case,
            f"{b['mass_kg_ruler']:.1f}", f"{b['mass_kg_candidate']:.1f}",
            f"{b['payload_kg_ruler']:.1f}", f"{b['payload_kg_candidate']:.1f}",
            f"{b['ruler']['per_km']['median']:.6f}",
            f"{b['candidate']['per_km']['median']:.6f}",
            f"{b['ruler']['per_payload_tkm']['median']:.6f}",
            f"{b['candidate']['per_payload_tkm']['median']:.6f}",
            f"{b['margin_pct_per_km_paired']['min']:.4f}",
            f"{b['margin_pct_per_km_paired']['median']:.4f}",
            f"{b['margin_pct_per_km_paired']['max']:.4f}",
            f"{b['margin_pct_per_payload_tkm_paired']['min']:.4f}",
            f"{b['margin_pct_per_payload_tkm_paired']['median']:.4f}",
            f"{b['margin_pct_per_payload_tkm_paired']['max']:.4f}"])
write_csv("headline_margins.csv",
          ["vehicle", "duty", "case", "mass_ruler_kg", "mass_cand_kg",
           "payload_ruler_kg", "payload_cand_kg",
           "ruler_kWh_per_km_median", "cand_kWh_per_km_median",
           "ruler_kWh_per_payload_tkm_median",
           "cand_kWh_per_payload_tkm_median",
           "margin_per_km_min_pct", "margin_per_km_median_pct",
           "margin_per_km_max_pct", "margin_per_payload_min_pct",
           "margin_per_payload_median_pct", "margin_per_payload_max_pct"],
          rows)

rows = []
for key, blocks in RESULTS.items():
    for case, b in blocks.items():
        for s in b["margin_pct_per_km_paired"]["per_seed"]:
            rows.append([b["vehicle"], b["duty"], case, s,
                         f"{b['ruler']['per_km']['per_seed'][s]:.8f}",
                         f"{b['candidate']['per_km']['per_seed'][s]:.8f}",
                         f"{b['ruler']['per_payload_tkm']['per_seed'][s]:.8f}",
                         f"{b['candidate']['per_payload_tkm']['per_seed'][s]:.8f}",
                         f"{b['margin_pct_per_km_paired']['per_seed'][s]:.6f}",
                         f"{b['margin_pct_per_payload_tkm_paired']['per_seed'][s]:.6f}"])
write_csv("per_seed_margins.csv",
          ["vehicle", "duty", "case", "seed", "ruler_kWh_per_km",
           "cand_kWh_per_km", "ruler_kWh_per_payload_tkm",
           "cand_kWh_per_payload_tkm", "margin_per_km_pct",
           "margin_per_payload_pct"], rows)

rows = []
for key, r_ in ONE.items():
    for factor, d in r_.items():
        val = d.get("cost_pp", d.get("worth_pp"))
        rows.append([key, factor, f"{val:+.4f}", d["description"][:180]])
write_csv("one_factor.csv", ["run", "factor", "pp", "description"], rows)

rows = []
for key, v in TRIP.items():
    rows.append([key,
                 f"{v['ruler_trip_time_s']['median']:.2f}",
                 f"{v['candidate_trip_time_s']['median']:.2f}",
                 f"{v['ratio_candidate_over_ruler']['min']:.6f}",
                 f"{v['ratio_candidate_over_ruler']['median']:.6f}",
                 f"{v['ratio_worst']:.6f}",
                 f"{v['pct_worse_than_ruler_worst']:+.4f}",
                 "PASS" if v["r38_gate_met"] else "FAIL"])
write_csv("trip_time_r38.csv",
          ["run", "ruler_trip_time_s_median", "cand_trip_time_s_median",
           "ratio_min", "ratio_median", "ratio_worst", "worst_pct_vs_ruler",
           "r38_gate_le_5pct"], rows)

rows = [[r["vehicle"], r["duty"], r["case"], r["component"],
         f"{r['heat_kWh_per_cycle_min']:.4f}",
         f"{r['heat_kWh_per_cycle_median']:.4f}",
         f"{r['heat_kWh_per_cycle_max']:.4f}",
         f"{r['mean_kW_over_cycle_max']:.4f}", r["max_governing_case"]]
        for r in LEDGER_ROWS]
write_csv("heat_ledger_ws6.csv",
          ["vehicle", "duty", "case", "component", "kWh_min", "kWh_median",
           "kWh_max", "mean_kW_max", "max_governing_case"], rows)

rows = []
for name, per_duty in CAL["brackets"].items():
    for duty, d in per_duty.items():
        rows.append([name, duty, f"{d['l_per_100km']['min']:.4f}",
                     f"{d['l_per_100km']['median']:.4f}",
                     f"{d['l_per_100km']['max']:.4f}"])
write_csv("ruler_brackets.csv",
          ["bracket", "duty", "l_per_100km_min", "l_per_100km_median",
           "l_per_100km_max"], rows)

rows = []
for key, r_ in BRK_MARGIN.items():
    for name, e in r_.items():
        rows.append([key, name, f"{e['min']:+.4f}", f"{e['median']:+.4f}",
                     f"{e['max']:+.4f}"])
write_csv("bracket_margins.csv",
          ["run", "bracket", "margin_per_payload_min_pct",
           "margin_per_payload_median_pct", "margin_per_payload_max_pct"],
          rows)

rows = [[y, mpg, veh, fu, mi, f"{P.MPG_TO_L_PER_100KM / mpg:.3f}"]
        for (y, mpg, veh, fu, mi) in P.RULER_FUEL_ANCHOR["rows"]]
rows.append(["ALL (distance-weighted)", f"{ANCHOR_ALL['mpg']:.4f}",
             21, ANCHOR_ALL["fuel_ups"], ANCHOR_ALL["miles"],
             f"{ANCHOR_ALL['l_per_100km']:.3f}"])
rows.append(["4HK1 era 2014-2016 (distance-weighted)",
             f"{ANCHOR_4HK1['mpg']:.4f}", ANCHOR_4HK1["vehicles"],
             ANCHOR_4HK1["fuel_ups"], ANCHOR_4HK1["miles"],
             f"{ANCHOR_4HK1['l_per_100km']:.3f}"])
write_csv("ruler_anchor.csv",
          ["model_year", "avg_mpg_us", "vehicles", "fuel_ups",
           "miles_tracked", "l_per_100km"], rows)

# ------------------------------------------------------------------- output
def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return [jsonable(v) for v in o.tolist()]
    return o


with open("results_ws11.json", "w") as f:
    json.dump(jsonable(R), f, indent=1)
    f.write("\n")
log("results_ws11.json written")
with open("run_output.txt", "w") as f:
    f.write("Project Volt WS11 - Vehicle Zero ruler trial - run log\n")
    f.write("Elapsed times are printed to stdout but deliberately NOT "
            "written here: this file is a committed artefact and must "
            "regenerate byte-identically.\n")
    f.write("=" * 72 + "\n")
    for line in LOG:
        f.write(line + "\n")
log("done")
