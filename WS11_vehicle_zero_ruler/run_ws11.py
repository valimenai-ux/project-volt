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
                        derate_factor, LHV_KJ_PER_G, WillansEngine)
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
    # m9: round 1 pinned the NPR-HD spec PDF but not the text extraction a
    # reader actually reads, and left the ZA NPR 400 sheet in sources/
    # unpinned, unreferenced and unmentioned. Every file in sources/ is
    # pinned now and the ZA sheet is used as a cross-check
    # (`ruler_chassis_cab_cross_check`).
    "sources/isuzucv_npr-hd_diesel_specs.txt":
        os.path.join(HERE, "sources", "isuzucv_npr-hd_diesel_specs.txt"),
    "sources/isuzu_za_NPR400_spec_sheet.pdf":
        os.path.join(HERE, "sources", "isuzu_za_NPR400_spec_sheet.pdf"),
    "sources/isuzu_za_NPR400_spec_sheet.txt":
        os.path.join(HERE, "sources", "isuzu_za_NPR400_spec_sheet.txt"),
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


def paired_shift(alt_margins, base_blk, seeds, duty_label):
    """SWEEP (r2): a `shift_pp` must be a PAIRED per-seed difference.

    Round 1's one-factor rows were min-of-A minus min-of-B (adjudication
    r1/M6) and the same construction had crept into every bracket-shift
    field written for this round. Every one of them is formed seed by seed
    here and enveloped afterwards, with the unpaired figure kept beside it
    so the size of the artefact is visible."""
    base_ps = base_blk["margin_pct_per_payload_tkm_paired"]["per_seed"]
    d = [alt_margins[i] - base_ps[str(sd)] for i, sd in enumerate(seeds)]
    e = envelope(d, seeds, duty_label)
    unp = min(alt_margins) - base_blk[
        "margin_pct_per_payload_tkm_paired"]["min"]
    return dict(
        shift_pp=e["min"], shift_pp_paired_min=e["min"],
        shift_pp_paired_median=e["median"], shift_pp_paired_max=e["max"],
        shift_pp_paired_min_governing_case=e["min_governing_case"],
        shift_pp_unpaired_statistic_of_statistics=unp,
        shift_pp_statistic=("PAIRED: differenced seed by seed against the "
                            "ordered run, then enveloped (R36/D13)"))


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
# R34 trace set. m6: round 1 traced nominal and the climb corner and so
# traced V2's governing corner but NOT V1's, which is `cold_-10C` and is
# the corner V1's ADVANCE is decided on. Both governing corners are traced
# now; `verify_ws11.py` asserts that each verdict's governing corner has a
# trace on disk, so this cannot silently regress.
TRACE_CASES = {"V1_on_VOLT-SUB": ("nominal", "cold_-10C"),
               "V2_on_VOLT-REG": ("nominal", "climb_10km_6pct"),
               "V2_on_VOLT-SUB": ("nominal",)}
for vehicle, duty, cases in PRIMARY:
    key = f"{vehicle}_on_{duty}"
    RESULTS[key] = {}
    for case in cases:
        want = (case in TRACE_CASES[key])
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

# ------------------------------------------------ ruler-fuel flip points (B3)
# The exact analogue of break_even_curb_kg, for the axis that THREATENS the
# verdicts instead of the axis that supports them. Round 1 exported the mass
# flip point (which supports V2's KILL: V2 is 195 kg over) and no flip point
# for the ruler's fuel level (which threatens it). Adjudication r1/B3.
#
# Algebra, exact, per seed - no search. With the candidate held fixed and the
# ruler's per-km fuel scaled by k:
#     margin(k) = 100 * (1 - c / (k * r))   where m = 100 * (1 - c/r)
#  => k = (1 - m/100) / (1 - M/100)   for a target margin M [%]
# k > 1 means the real ruler would have to be THIRSTIER than modelled by
# 100*(k-1)% for the candidate to reach M; k < 1 means leaner.
log("ruler-fuel flip points ...")


def _flip_block(blk, seeds, duty_label, targets=(0.0, 3.0)):
    per_seed_m = blk["margin_pct_per_payload_tkm_paired"]["per_seed"]
    ruler_l = blk["ruler"]["l_per_100km"]["per_seed"]
    out = {}
    for M in targets:
        ks, ls = [], []
        for sd in seeds:
            m = per_seed_m[str(sd)]
            k = (1.0 - m / 100.0) / (1.0 - M / 100.0)
            ks.append(k)
            ls.append(k * ruler_l[str(sd)])
        env_k = envelope(ks, seeds, duty_label)
        env_l = envelope(ls, seeds, duty_label)
        # the LEAST ruler-fuel error that reaches the target on any seed of
        # the enumerated 8-seed set: the multiplier closest to 1.0.
        i_near = int(np.argmin([abs(k - 1.0) for k in ks]))
        key = f"to_{M:g}pct".replace(".", "p")
        out[key] = dict(
            target_margin_pct=M,
            multiplier_min=env_k["min"], multiplier_median=env_k["median"],
            multiplier_max=env_k["max"],
            multiplier_min_governing_case=env_k["min_governing_case"],
            multiplier_max_governing_case=env_k["max_governing_case"],
            multiplier_per_seed=env_k["per_seed"],
            least_ruler_fuel_error_multiplier=ks[i_near],
            least_ruler_fuel_error_pct=100.0 * (ks[i_near] - 1.0),
            least_ruler_fuel_error_governing_case=(
                f"seed {seeds[i_near]} of the enumerated 8-seed "
                f"{duty_label} ensemble (multiplier closest to 1.0 over "
                f"the enumerated seed set)"),
            implied_ruler_l_per_100km_min=env_l["min"],
            implied_ruler_l_per_100km_median=env_l["median"],
            implied_ruler_l_per_100km_max=env_l["max"],
            implied_ruler_l_per_100km_governing_case=(
                env_l["min_governing_case"]))
    return out


FLIP = {}
for vehicle, duty, cases in PRIMARY:
    key = f"{vehicle}_on_{duty}"
    seeds = SEEDS[duty]
    FLIP[key] = {}
    for case in cases:
        lbl = duty if case != "climb_10km_6pct" else duty + "+CLIMB"
        FLIP[key][case] = _flip_block(RESULTS[key][case], seeds, lbl)
    v = VERDICTS.get(key)
    if v is not None:
        nom = FLIP[key]["nominal"]
        direction = ("THIRSTIER" if v["verdict"] == "KILL" else "LEANER")
        FLIP[key]["_verdict_reading"] = dict(
            verdict=v["verdict"],
            direction_that_would_overturn_the_verdict=direction,
            multiplier_to_draw=nom["to_0pct"][
                "least_ruler_fuel_error_multiplier"],
            pct_ruler_fuel_error_to_draw=nom["to_0pct"][
                "least_ruler_fuel_error_pct"],
            pct_ruler_fuel_error_to_draw_governing_case=nom["to_0pct"][
                "least_ruler_fuel_error_governing_case"],
            multiplier_to_3pct_bar=nom["to_3pct"][
                "least_ruler_fuel_error_multiplier"],
            pct_ruler_fuel_error_to_3pct_bar=nom["to_3pct"][
                "least_ruler_fuel_error_pct"],
            pct_ruler_fuel_error_to_3pct_bar_governing_case=nom["to_3pct"][
                "least_ruler_fuel_error_governing_case"])
        log(f"  {key} [{v['verdict']}]: draws at ruler fuel "
            f"x{nom['to_0pct']['least_ruler_fuel_error_multiplier']:.4f} "
            f"({nom['to_0pct']['least_ruler_fuel_error_pct']:+.2f}%), "
            f"reaches the 3% bar at "
            f"x{nom['to_3pct']['least_ruler_fuel_error_multiplier']:.4f} "
            f"({nom['to_3pct']['least_ruler_fuel_error_pct']:+.2f}%)")
R["ruler_fuel_flip_points"] = dict(
    rule=("the multiplier k on the RULER's per-km fuel at which each "
          "candidate's per-payload-tonne-km margin reaches a target, "
          "computed per seed on the PAIRED statistic and enveloped over "
          "the enumerated 8-seed set with the governing seed labelled "
          "(R14/R36). Exact algebra, not a search: at fixed GVW the "
          "candidate is untouched and margin(k) = 100*(1 - c/(k*r))."),
    why=("a KILL is not protected by a lower-bound framing. V2's margin is "
          "negative because the ruler is modelled lean; the question the "
          "lead needs answered is how much leaner than the truth that is "
          "allowed to be before the KILL becomes a draw. The mandatory "
          "anchor says the real fleet burns 46% more (all model years) or "
          "67% more (4HK1-era subset) than this ruler does."),
    cases=FLIP)

# ------------------------------------------------------------- one-factor
log("one-factor decomposition (paired per-seed, R36) ...")
ONE = {}


def _paired_worth(base_blk, alt_margins, seeds, duty_label):
    """The worth of a factor as a PAIRED per-seed statistic.

    Round 1 formed every `worth_pp` as min-of-A minus min-of-B, with the
    two minima governed by DIFFERENT seeds - R36's defect class in
    miniature (adjudication r1/M6). The difference is now formed seed by
    seed and only THEN enveloped. The unpaired figure is retained beside
    it, labelled, so round 1's numbers are on the record and the size of
    the artefact is visible."""
    base_ps = base_blk["margin_pct_per_payload_tkm_paired"]["per_seed"]
    diffs = [base_ps[str(sd)] - alt_margins[i] for i, sd in enumerate(seeds)]
    env_d = envelope(diffs, seeds, duty_label)
    env_a = envelope(alt_margins, seeds, duty_label)
    unpaired = (base_blk["margin_pct_per_payload_tkm_paired"]["min"]
                - env_a["min"])
    return dict(
        worth_pp=env_d["min"],
        worth_pp_paired_min=env_d["min"],
        worth_pp_paired_median=env_d["median"],
        worth_pp_paired_max=env_d["max"],
        worth_pp_paired_min_governing_case=env_d["min_governing_case"],
        worth_pp_paired_per_seed=env_d["per_seed"],
        worth_pp_unpaired_r1_statistic_of_statistics=unpaired,
        unpaired_artefact_pp=unpaired - env_d["min"],
        statistic=("PAIRED: the difference is formed on each seed and then "
                   "enveloped over the enumerated 8-seed set (R36/D13). "
                   "`worth_pp` is the ensemble-MIN of the per-seed "
                   "differences."),
        envelope_counterfactual=env_a)


for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    key = f"{vehicle}_on_{duty}"
    seeds = SEEDS[duty]
    base = RESULTS[key]["nominal"]
    sp = case_spec("nominal", vehicle)
    spr = case_spec("nominal", "ruler")
    rows = {}

    # (a) mass / payload: the freight given back.
    # This row IS paired: at fixed GVW the payload ratio is a constant, so
    # the per-seed difference (per-km margin - per-payload margin) is a
    # monotone function of the per-km margin and the two minima share a
    # seed. It is now formed per seed anyway, so no row in this table is a
    # statistic of statistics.
    _pk = base["margin_pct_per_km_paired"]["per_seed"]
    _pp = base["margin_pct_per_payload_tkm_paired"]["per_seed"]
    _cost = [_pk[str(sd)] - _pp[str(sd)] for sd in seeds]
    env_cost = envelope(_cost, seeds, duty)
    rows["mass_payload_denominator"] = dict(
        description=("the candidate's own curb mass, expressed where it "
                     "acts: the payload denominator. At the fixed 6,600 kg "
                     "GVW both vehicles carry the SAME total mass, so this "
                     "factor moves no energy at all - it moves only the "
                     "freight the energy is divided by."),
        statistic=("PAIRED: formed per seed, then enveloped. `cost_pp` is "
                   "the ensemble-MIN of the per-seed differences."),
        margin_pct_per_km_min=base["margin_pct_per_km_paired"]["min"],
        margin_pct_per_payload_min=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        cost_pp=env_cost["min"],
        cost_pp_paired_min=env_cost["min"],
        cost_pp_paired_median=env_cost["median"],
        cost_pp_paired_max=env_cost["max"],
        cost_pp_paired_min_governing_case=env_cost["min_governing_case"],
        cost_pp_unpaired_r1_statistic_of_statistics=(
            base["margin_pct_per_km_paired"]["min"]
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
    rows["regen"] = dict(
        description=("regen alone: the candidate re-run with the wheel-side "
                     "regen cap set to zero (all braking to friction and the "
                     "R2 resistor), everything else identical."),
        margin_pct_per_payload_min_with_regen=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_without_regen=min(m_no_regen),
        **_paired_worth(base, m_no_regen, seeds, duty))

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
    rows["start_stop_engine_off"] = dict(
        description=("start-stop / engine-off alone: mode (b) pinned "
                     "start-stop against mode (b') - a genset that never "
                     "shuts off and load-follows its best-BSFC locus "
                     "(ser_band forced to (0.999, 1.0) so the engine is "
                     "always on). This is E6's continuous-running "
                     "alternative."),
        margin_pct_per_payload_min_with_start_stop=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_without=min(m_no_ss),
        **_paired_worth(base, m_no_ss, seeds, duty))

    # (d) engine operating point (part load) alone
    m_op = []
    bsfc_pin, bsfc_ruler = [], []
    idle_share = []
    for s in seeds:
        ru, ca, _, _ = run_pair(vehicle, duty, "nominal", s)
        pin_bsfc = ca["pinned"]["bsfc"]
        bsfc_pin.append(pin_bsfc)
        bsfc_ruler.append(ru["mean_bsfc_eff_g_per_kwh"])
        idle_share.append(100.0 * ru["idle_fuel_g"] / ru["fuel_burn_g"])
        # ruler counterfactual: identical shaft-energy demand, but every
        # gramme burned at the candidate's pinned island BSFC
        fuel_alt_g = ru["eng_kwh"] * pin_bsfc + ru["unserved_fuel_g"]
        e_alt = fuel_alt_g * LHV_KJ_PER_G / 3600.0
        mr_alt = e_alt / (ru["distance_km"] * spr["payload_kg"] / 1000.0)
        mc = metrics(ca, sp["payload_kg"])
        m_op.append(100.0 * (mr_alt - mc["per_payload_tkm"]) / mr_alt)
    rows["engine_operating_point"] = dict(
        description=("engine operating point (part load) alone: the ruler "
                     "re-scored with its OWN shaft-energy demand but every "
                     "gramme burned at the candidate's pinned island BSFC. "
                     "The counterfactual re-prices the ruler's WHOLE shaft "
                     "energy at the island, and `eng_kwh` includes the "
                     "shaft work the ruler does at idle - so IDLE IS "
                     "ABSORBED INTO THIS ROW, not left outside it. Round 1 "
                     "said idle was among the things that survive the row; "
                     "it is not (adjudication r1/M6b). What survives is "
                     "the driveline, regen and the payload denominator. On "
                     "this duty idle is "
                     "`ruler_idle_share_of_fuel_pct` of the ruler's fuel, "
                     "so this row conflates two mechanisms and is read as "
                     "an upper bound on the operating-point term alone."),
        ruler_duty_mean_effective_bsfc_g_per_kWh=envelope(
            bsfc_ruler, seeds, duty),
        candidate_pinned_bsfc_g_per_kWh=bsfc_pin[0],
        ruler_idle_share_of_fuel_pct=envelope(idle_share, seeds, duty),
        margin_pct_per_payload_min_actual=(
            base["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_pct_per_payload_min_if_ruler_had_the_island=min(m_op),
        **_paired_worth(base, m_op, seeds, duty))
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
        margin_pct_per_payload_min_without=min(m_no_ss2),
        **_paired_worth(base, m_no_ss2, seeds, duty))
    ONE[key] = rows
    log(f"  {key} one-factor (paired): mass "
        f"{rows['mass_payload_denominator']['cost_pp']:+.2f} pp, "
        f"regen {rows['regen']['worth_pp']:+.2f} pp, "
        f"start-stop {rows['start_stop_engine_off']['worth_pp']:+.2f} pp, "
        f"operating point {rows['engine_operating_point']['worth_pp']:+.2f} pp")
R["one_factor"] = dict(
    statistic_note=("EVERY row is a paired per-seed statistic: the "
                    "counterfactual is differenced against the base on the "
                    "SAME seed and the envelope is taken afterwards "
                    "(R36/D13). Round 1's unpaired figure is retained on "
                    "each row as "
                    "`worth_pp_unpaired_r1_statistic_of_statistics` with "
                    "the artefact size beside it."),
    rows=ONE)

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
    ru_gmin, ca_gmin, ru_lim, ca_lim, ru_run = [], [], [], [], []
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
        ru_gmin.append(rt["min_speed_on_grade_ge_5p5pct_kmh"])
        ca_gmin.append(ct["min_speed_on_grade_ge_5p5pct_kmh"])
        ru_lim.append(rt["capability_limited_s"])
        ca_lim.append(ct["capability_limited_s"])
        ru_run.append(rt["longest_sustained_grade_run_s"])
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
        capability_limited_s_ruler=envelope(ru_lim, seeds, lbl),
        capability_limited_s_candidate=envelope(ca_lim, seeds, lbl),
        longest_sustained_grade_run_s_ruler=envelope(ru_run, seeds, lbl),
        settled_speed_definition=(
            "the speed the vehicle has settled at when it leaves the "
            "longest continuous run of >=5.5% grade, and only when that "
            "run lasts >= 120 s. None means the route carries no sustained "
            "climb. Round 1's field carried the MINIMUM speed on any "
            "sample of >=5.5% grade anywhere in the cycle, sustained or "
            "not, and was reported as a settled speed on cases that have "
            "no sustained climb at all (adjudication r1/B2)."),
        ruler_settled_speed_on_6pct_kmh=(
            envelope(ru_climb, seeds, lbl)
            if all(x is not None for x in ru_climb) else None),
        candidate_settled_speed_on_6pct_kmh=(
            envelope(ca_climb, seeds, lbl)
            if all(x is not None for x in ca_climb) else None),
        ruler_min_speed_on_grade_ge_5p5pct_kmh=(
            envelope(ru_gmin, seeds, lbl)
            if all(x is not None for x in ru_gmin) else None),
        candidate_min_speed_on_grade_ge_5p5pct_kmh=(
            envelope(ca_gmin, seeds, lbl)
            if all(x is not None for x in ca_gmin) else None),
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
# B2 remedy: the two places this results file states a steady speed on a 6%
# grade must agree. In round 1 they did not - the trip-time pass reported
# 88.4 / 94.3 km/h against closed-form values of 82.0 / 74.6 - because the
# pass never enforced capability once the vehicle was tracking demand. With
# the limit enforced they reconcile, and the reconciliation is asserted in
# verify_ws11.py so it cannot drift again.
RECON = dict(
    rule=("on any corner carrying a SUSTAINED 6% grade, the settled speed "
          "from the capability-limited forward pass must agree with the "
          "closed-form `sustained_6pct_capability_kmh` for the same "
          "vehicle."),
    tolerance_kmh=1.0,
    tolerance_basis=("[WS11-DECLARED] the forward pass and the closed-form "
                     "solve are two different reduced-order models: the "
                     "closed-form takes the traction chain's efficiency at "
                     "a single 60 kW tabulation point and gives the pack "
                     "nothing, while the forward pass tabulates the chain "
                     "at half its available bus power and carries a live "
                     "genset dispatch state. The RULER, which has neither "
                     "difference, agrees exactly."),
    rows={})
for k, v in TRIP.items():
    if v["ruler_settled_speed_on_6pct_kmh"] is None:
        continue
    veh_k = v["vehicle"]
    ru_fw = v["ruler_settled_speed_on_6pct_kmh"]["median"]
    ca_fw = v["candidate_settled_speed_on_6pct_kmh"]["median"]
    RECON["rows"][k] = dict(
        ruler_forward_pass_kmh=ru_fw,
        ruler_closed_form_kmh=SUSTAINED["ruler_kmh"],
        ruler_abs_difference_kmh=abs(ru_fw - SUSTAINED["ruler_kmh"]),
        candidate=veh_k,
        candidate_forward_pass_kmh=ca_fw,
        candidate_closed_form_kmh=SUSTAINED[f"{veh_k}_kmh"],
        candidate_abs_difference_kmh=abs(ca_fw
                                         - SUSTAINED[f"{veh_k}_kmh"]))
    log(f"  settled-speed reconciliation {k}: ruler {ru_fw:.2f} vs "
        f"{SUSTAINED['ruler_kmh']:.2f} km/h, {veh_k} {ca_fw:.2f} vs "
        f"{SUSTAINED[f'{veh_k}_kmh']:.2f} km/h")
SUSTAINED["forward_pass_reconciliation"] = RECON
R["sustained_6pct_capability"] = SUSTAINED
log(f"  sustained 6%: ruler {SUSTAINED['ruler_kmh']:.1f} km/h, "
    f"V1 {SUSTAINED['V1_kmh']:.1f}, V2 {SUSTAINED['V2_kmh']:.1f}")

# ------------------------------------------------- ruler calibration + brackets
log("ruler calibration against the sourced anchor, and ruler brackets ...")
ANCHOR_ALL = P.anchor_stats()
ANCHOR_4HK1 = P.anchor_stats(
    [r for r in P.RULER_FUEL_ANCHOR["rows"]
     if r[0] in P.RULER_FUEL_ANCHOR["fourhk1_era_years"]])

# --- the bracket set (rebuilt for adjudication r1/B1) ---------------------
# Round 1 exported a row called `all_ruler_favourable_choices_reversed`
# which reversed FIVE choices and left the four largest ones - gear mesh,
# AT pump, final drive and lock-up slip - at their ruler-favourable values,
# while folding in a CdA change that is not a ruler-modelling choice at
# all. Every declared ruler lever is now a bracket, singly and in
# combination, and the road-load change is separated from the modelling
# changes by an explicit `kind` on every row.
_DRIVELINE_PESSIMISTIC = dict(
    eta_gear=P.ETA_GEAR_PESSIMISTIC,
    pump_kw_at_1800=P.PUMP_KW_AT_1800_PESSIMISTIC,
    eta_final=P.ETA_FINAL_PESSIMISTIC,
    lockup_slip=P.LOCKUP_SLIP_LOSS_PESSIMISTIC)
_ALL_MODELLING_PESSIMISTIC = dict(
    _DRIVELINE_PESSIMISTIC,
    p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL, idle_neutral=False,
    shift_schedule="sequential", charge_rot=True)

BRACKETS = {
    "headline_ruler_favourable": dict(),
    # -- single ruler-modelling levers --
    "gear_mesh_pessimistic": dict(eta_gear=P.ETA_GEAR_PESSIMISTIC),
    "at_pump_pessimistic":
        dict(pump_kw_at_1800=P.PUMP_KW_AT_1800_PESSIMISTIC),
    "final_drive_pessimistic": dict(eta_final=P.ETA_FINAL_PESSIMISTIC),
    "lockup_slip_pessimistic":
        dict(lockup_slip=P.LOCKUP_SLIP_LOSS_PESSIMISTIC),
    "physical_accessories": dict(p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL),
    "converter_stalled_at_idle": dict(idle_neutral=False),
    "sequential_shift_schedule": dict(shift_schedule="sequential"),
    "rotating_inertia_charged": dict(charge_rot=True),
    # -- combinations of ruler-MODELLING choices only (no road change) --
    "four_driveline_levers_pessimistic": dict(_DRIVELINE_PESSIMISTIC),
    "four_driveline_plus_accessories_plus_idle_in_drive": dict(
        _DRIVELINE_PESSIMISTIC, p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL,
        idle_neutral=False),
    "all_ruler_modelling_choices_pessimistic":
        dict(_ALL_MODELLING_PESSIMISTIC),
    # -- road-load change: NOT a ruler-modelling choice --
    "CdA_5.4": dict(cda=5.4),
    "all_ruler_modelling_pessimistic_plus_CdA_5.4_road_change": dict(
        _ALL_MODELLING_PESSIMISTIC, cda=5.4),
    # -- round 1's row, kept under a name that says what it actually was --
    "r1_partial_reversal_plus_CdA_5.4_road_change": dict(
        p_acc_kw=P.P_ACC_CRANK_KW_PHYSICAL, idle_neutral=False, cda=5.4,
        shift_schedule="sequential", charge_rot=True),
}
BRACKET_KIND = {
    "headline_ruler_favourable": "headline",
    "gear_mesh_pessimistic": "ruler_modelling",
    "at_pump_pessimistic": "ruler_modelling",
    "final_drive_pessimistic": "ruler_modelling",
    "lockup_slip_pessimistic": "ruler_modelling",
    "physical_accessories": "ruler_modelling",
    "converter_stalled_at_idle": "ruler_modelling",
    "sequential_shift_schedule": "ruler_modelling",
    "rotating_inertia_charged": "ruler_modelling",
    "four_driveline_levers_pessimistic": "ruler_modelling_combination",
    "four_driveline_plus_accessories_plus_idle_in_drive":
        "ruler_modelling_combination",
    "all_ruler_modelling_choices_pessimistic": "ruler_modelling_combination",
    "CdA_5.4": "road_load_change_applied_to_both_vehicles",
    "all_ruler_modelling_pessimistic_plus_CdA_5.4_road_change":
        "ruler_modelling_combination_PLUS_road_load_change",
    "r1_partial_reversal_plus_CdA_5.4_road_change":
        "SUPERSEDED_round1_partial_reversal_PLUS_road_load_change",
}
BRACKET_NOTE = {
    "all_ruler_modelling_choices_pessimistic": (
        "THE ROW THE ROBUSTNESS CLAIM IS STATED AGAINST. Every one of the "
        "eight ruler-MODELLING choices at the pessimistic end its own "
        "declaration names: gear mesh -2 points, AT pump 2.0 kW at "
        "1,800 rpm, final drive 0.94, lock-up slip 2.0%, physical "
        "belt/alternator accessories, converter stalled in Drive at idle, "
        "single-step shift schedule, engine/flywheel/converter rotating "
        "inertia charged. No road-load change: CdA stays at the ratified "
        "4.2 m^2 for both vehicles."),
    "four_driveline_plus_accessories_plus_idle_in_drive": (
        "the six-lever combination named in adjudication r1/B1 as the one "
        "that takes V2 to a draw; exported so that finding reproduces "
        "against this workstream's own artefacts"),
    "CdA_5.4": (
        "NOT a ruler-modelling choice. CdA is a property of the ROAD LOAD "
        "both vehicles drive and the candidate is re-run at the same CdA; "
        "it moves the comparison AGAINST the candidates. Kept in the table "
        "because ESC-4 asks the lead to schedule the coastdown, not "
        "because reversing it tests the ruler."),
    "r1_partial_reversal_plus_CdA_5.4_road_change": (
        "SUPERSEDED. This is the row round 1 exported as "
        "`all_ruler_favourable_choices_reversed`. It reversed accessories, "
        "idle, shift schedule and rotating inertia, left the four "
        "driveline levers at their ruler-favourable values, and folded in "
        "the CdA road change. Retained under an accurate name so round "
        "1's numbers are not silently dropped; superseded by "
        "`all_ruler_modelling_choices_pessimistic`."),
}


def ruler_bracket_run(duty, seed, spec, cyc=None, m=None, derate=1.0,
                      veh_base=None):
    veh_base = VEH if veh_base is None else veh_base
    veh = veh_base if "cda" not in spec else dataclasses.replace(
        veh_base, CdA=spec["cda"])
    o = RU.run_ruler(CYC[duty][seed] if cyc is None else cyc,
                     P.M_GVW_KG if m is None else m, veh=veh, engine=ENG_REF,
                     derate=derate,
                     p_acc_kw=spec.get("p_acc_kw", P.P_ACC_CRANK_KW),
                     idle_neutral=spec.get("idle_neutral", True),
                     shift_schedule=spec.get("shift_schedule",
                                             "fuel_optimal"),
                     eta_gear=spec.get("eta_gear"),
                     eta_final=spec.get("eta_final"),
                     pump_kw_at_1800=spec.get("pump_kw_at_1800"),
                     lockup_slip=spec.get("lockup_slip"),
                     derate_load_fraction=spec.get("derate_load_fraction",
                                                   False))
    if spec.get("charge_rot"):
        lev = o["levers"]
        eta_marg = (max(lev["eta_gear"]) * lev["eta_final"]
                    * (1.0 - lev["lockup_slip"]))
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
        runs = [ruler_bracket_run(duty, s, spec) for s in seeds]
        vals = [o["l_per_100km"] for o in runs]
        ev = [o["fuel_energy_kWh_per_km"] for o in runs]
        per_duty[duty] = dict(l_per_100km=envelope(vals, seeds, duty),
                              fuel_energy_kWh_per_km=envelope(ev, seeds,
                                                              duty))
    per_duty["kind"] = BRACKET_KIND[name]
    if name in BRACKET_NOTE:
        per_duty["note"] = BRACKET_NOTE[name]
    CAL["brackets"][name] = per_duty
    log(f"  ruler bracket {name} [{BRACKET_KIND[name]}]: VOLT-SUB median "
        f"{per_duty['VOLT-SUB']['l_per_100km']['median']:.2f} L/100km, "
        f"VOLT-REG median "
        f"{per_duty['VOLT-REG']['l_per_100km']['median']:.2f}")

_hl = CAL["brackets"]["headline_ruler_favourable"]
_pess = CAL["brackets"]["all_ruler_modelling_choices_pessimistic"]
_r1rev = CAL["brackets"]["r1_partial_reversal_plus_CdA_5.4_road_change"]


def _anchor_member(stats, label, subset_note):
    return dict(label=label, subset=subset_note, mpg=stats["mpg"],
                l_per_100km=stats["l_per_100km"], miles=stats["miles"],
                fuel_ups=stats["fuel_ups"], vehicles=stats["vehicles"],
                model_years=stats["model_years"],
                residual_vs_model_headline_pct=100.0 * (
                    _hl["VOLT-SUB"]["l_per_100km"]["median"]
                    / stats["l_per_100km"] - 1.0),
                residual_vs_model_pessimistic_pct=100.0 * (
                    _pess["VOLT-SUB"]["l_per_100km"]["median"]
                    / stats["l_per_100km"] - 1.0))


# R14: the anchor is an ENUMERATED SET with two members, and the worst-case
# residual is an explicit min over that set with the governing member
# labelled. Round 1 exported only the milder member (adjudication r1/M5).
_A_ALL = _anchor_member(ANCHOR_ALL, "all model years with data",
                        "2016, 2015, 2014, 2002, 2000")
_A_ERA = _anchor_member(ANCHOR_4HK1, "4HK1-era subset (MY2014-2016)",
                        "the model years that actually carry the 4HK1-TC "
                        "engine this ruler models")
CAL["anchor_set_r14"] = dict(
    rule=("an explicit min/max over the enumerated two-member anchor set, "
          "governing member labelled inline (R14)"),
    members=dict(all_model_years=_A_ALL, fourhk1_era=_A_ERA),
    worst_residual_vs_model_headline_pct=min(
        _A_ALL["residual_vs_model_headline_pct"],
        _A_ERA["residual_vs_model_headline_pct"]),
    worst_residual_governing_member=(
        "fourhk1_era" if _A_ERA["residual_vs_model_headline_pct"]
        < _A_ALL["residual_vs_model_headline_pct"] else "all_model_years"),
    era_note_direction=(
        "MY2002 reads 9.4 mpg, which is the BEST row on the anchor page. "
        "Removing it - which is what restricting the anchor to the "
        "4HK1-era subset does - therefore makes the anchor THIRSTIER and "
        "the model's residual WORSE, from "
        f"{_A_ALL['residual_vs_model_headline_pct']:.2f}% to "
        f"{_A_ERA['residual_vs_model_headline_pct']:.2f}%. Round 1 "
        "presented the era caveat as if it weakened the anchor; it does "
        "not (adjudication r1/B3)."))

CAL["corridor_check"] = dict(
    corridor_l_per_100km=[18.0, 30.0],
    ruler_VOLT_SUB_headline_median=_hl["VOLT-SUB"]["l_per_100km"]["median"],
    ruler_VOLT_SUB_headline_min=_hl["VOLT-SUB"]["l_per_100km"]["min"],
    ruler_VOLT_SUB_headline_max=_hl["VOLT-SUB"]["l_per_100km"]["max"],
    inside_corridor=bool(
        18.0 <= _hl["VOLT-SUB"]["l_per_100km"]["min"] <= 30.0
        and 18.0 <= _hl["VOLT-SUB"]["l_per_100km"]["max"] <= 30.0),
    ruler_VOLT_SUB_all_modelling_pessimistic_median=(
        _pess["VOLT-SUB"]["l_per_100km"]["median"]),
    ruler_VOLT_SUB_r1_partial_reversal_median=(
        _r1rev["VOLT-SUB"]["l_per_100km"]["median"]),
    residual_vs_anchor_pct_headline=100.0 * (
        _hl["VOLT-SUB"]["l_per_100km"]["median"]
        / ANCHOR_ALL["l_per_100km"] - 1.0),
    residual_vs_anchor_pct_all_modelling_pessimistic=100.0 * (
        _pess["VOLT-SUB"]["l_per_100km"]["median"]
        / ANCHOR_ALL["l_per_100km"] - 1.0),
    residual_vs_era_anchor_pct_headline=(
        _A_ERA["residual_vs_model_headline_pct"]),
    residual_vs_era_anchor_pct_all_modelling_pessimistic=(
        _A_ERA["residual_vs_model_pessimistic_pct"]),
    calibrate_order_satisfied=False,
    calibrate_order_statement=(
        "The assignment orders 'Calibrate to a public NPR fuel-economy "
        "reference and state it'. WS11 obtained the reference and did NOT "
        "calibrate to it: no ruler parameter was moved to close the "
        "residual, because the anchor is an in-use aggregate over an "
        "unknown duty, load, body and driver mix and cannot resolve a "
        "cycle-specific level. This is recorded as a NON-SATISFACTION of "
        "the order, not as a treatment choice (adjudication r1/B3). The "
        "consequence for each verdict is priced in "
        "`ruler_fuel_flip_points`: V2's KILL is being put to the lead on "
        "an UNCALIBRATED ruler."),
    reading=("the model reads BELOW the in-use anchor on every setting and "
             "against both members of the anchor set. For V1's ADVANCE "
             "that residual is the safe direction and the margin is a "
             "lower bound. For V2's KILL it is the UNSAFE direction, and "
             "the quantity that matters is not the residual but the flip "
             "point - see `ruler_fuel_flip_points`. Escalated (ESC-1)."),
)
R["ruler_calibration"] = CAL

# effect of the brackets on the headline verdicts. B1 orders this for BOTH
# duties and BOTH vehicles, so it runs over every primary pairing, not only
# each candidate's design duty.
log("bracket effect on the verdicts (both vehicles, both duties) ...")
BRK_MARGIN = {}
BRK_PAIRS = [("V1", "VOLT-SUB"), ("V2", "VOLT-REG"), ("V2", "VOLT-SUB")]
for vehicle, duty in BRK_PAIRS:
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
        e = envelope(mg, seeds, duty)
        e["kind"] = BRACKET_KIND[name]
        rows[name] = e
    BRK_MARGIN[f"{vehicle}_on_{duty}"] = rows
    log(f"  {vehicle}/{duty}: headline min "
        f"{rows['headline_ruler_favourable']['min']:+.2f}%, "
        f"all-ruler-modelling-pessimistic min "
        f"{rows['all_ruler_modelling_choices_pessimistic']['min']:+.2f}% "
        f"median "
        f"{rows['all_ruler_modelling_choices_pessimistic']['median']:+.2f}%")
R["ruler_bracket_effect_on_margin"] = dict(
    note=("per-payload-tonne-km margin, paired per-seed, at nominal, "
          "recomputed with each ruler bracket, for every primary vehicle x "
          "duty pairing. Rows are classified by `kind`: a "
          "`ruler_modelling` row changes only how the RULER is modelled "
          "and every one of them raises the candidate's margin, which is "
          "what 'lower bound' means; a "
          "`road_load_change_applied_to_both_vehicles` row (CdA 5.4) "
          "changes the ROAD, is applied to the candidate as well, and "
          "LOWERS the candidate's margin on both vehicles. Round 1's note "
          "asserted that every non-headline row raises the margin, which "
          "the CdA row contradicts on both vehicles (adjudication "
          "r1/M4)."),
    robustness_row="all_ruler_modelling_choices_pessimistic",
    rows=BRK_MARGIN)

# ---------------------------------------------- cold cab-heat bracket (R30)
# m11: round 1 applied `aux = 2.0 + 3.0*(1 - eng_on_frac)`, a CYCLE-AVERAGE
# adder taken from the BASE run's engine-on fraction and never iterated,
# while describing the treatment as if it were time-resolved. WS4's
# `run_g1_mode` takes `p_aux_kw` as a scalar inside its per-sample loop and
# WS4 is read-only, so a genuinely time-switched cab load is not available
# to WS11 without editing another workstream's simulator. What IS available
# and is now done: (i) the smear is iterated to a fixed point, so the
# engine-on fraction it is computed from is the one the loaded run actually
# has; (ii) the description says plainly that it is an energy-correct,
# timing-approximate smear; and (iii) the no-waste-heat-credit reading
# (3.0 kW charged for the WHOLE cycle) is run as an explicit upper bound,
# so the smear is bracketed rather than trusted.
log("cold corner cab-heat bracket ...")
COLDB = {}
CAB_HEAT_ITERS = 4
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    sp = case_spec("cold_-10C", vehicle)
    spr = case_spec("cold_-10C", "ruler")
    mg, aux_used, onfrac, onfrac_loaded, mg_ub, iters_moved = \
        [], [], [], [], [], []
    mg_r1 = []
    for s in seeds:
        base = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                                m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                                p_aux_kw=sp["aux"],
                                chg_accept_bus_kw=ACC["cold_-10C"])
        # (i) fixed-point on the engine-on fraction
        f_off = 1.0 - base["eng_on_frac"]
        aux = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * f_off
        ca = None
        for _ in range(CAB_HEAT_ITERS):
            ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                                  m=sp["m"], veh=sp["veh"],
                                  derate=sp["derate"], p_aux_kw=aux,
                                  chg_accept_bus_kw=ACC["cold_-10C"])
            aux_new = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * (
                1.0 - ca["eng_on_frac"])
            if abs(aux_new - aux) < 1e-9:
                aux = aux_new
                break
            aux = aux_new
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                              m=sp["m"], veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=aux, chg_accept_bus_kw=ACC["cold_-10C"])
        # (iii) upper bound: no waste-heat credit at all
        # round 1's method, kept so its reported number is not dropped:
        # the adder from the BASE run's engine-on fraction, one pass.
        aux_r1 = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * f_off
        ca_r1 = CA.run_candidate(
            vehicle, CYC[duty][s], WS3, CHAIN, m=sp["m"], veh=sp["veh"],
            derate=sp["derate"], p_aux_kw=aux_r1,
            chg_accept_bus_kw=ACC["cold_-10C"])
        ca_ub = CA.run_candidate(
            vehicle, CYC[duty][s], WS3, CHAIN, m=sp["m"], veh=sp["veh"],
            derate=sp["derate"],
            p_aux_kw=sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10,
            chg_accept_bus_kw=ACC["cold_-10C"])
        ru = RU.run_ruler(CYC[duty][s], spr["m"], veh=spr["veh"],
                          engine=ENG_REF, derate=spr["derate"],
                          p_acc_kw=P.P_ACC_CRANK_KW)
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        mc_ub = metrics(ca_ub, sp["payload_kg"])
        mg.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                  / mr["per_payload_tkm"])
        mg_ub.append(100.0 * (mr["per_payload_tkm"]
                              - mc_ub["per_payload_tkm"])
                     / mr["per_payload_tkm"])
        mc_r1 = metrics(ca_r1, sp["payload_kg"])
        mg_r1.append(100.0 * (mr["per_payload_tkm"]
                              - mc_r1["per_payload_tkm"])
                     / mr["per_payload_tkm"])
        aux_used.append(aux)
        onfrac.append(base["eng_on_frac"])
        onfrac_loaded.append(ca["eng_on_frac"])
        iters_moved.append(abs(aux - (sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10
                                      * f_off)))
    COLDB[f"{vehicle}_on_{duty}"] = dict(
        description=(f"[WS11-DECLARED, NOT ORDERED] the R30 cab-heat member "
                     f"applied to Vehicle Zero: {P.CAB_HEAT_KW_AT_MINUS10} kW "
                     f"of cab heat at -10 C, free from engine coolant on the "
                     f"ruler and free from genset coolant on the candidate "
                     f"WHILE THE GENSET RUNS. In the engine-off windows the "
                     f"candidate must make it electrically, and that "
                     f"electric load is applied as an ENERGY-CORRECT, "
                     f"TIMING-APPROXIMATE cycle-average adder "
                     f"2.0 + 3.0 x (1 - eng_on_frac), iterated to a fixed "
                     f"point in eng_on_frac. It is NOT time-switched: WS4's "
                     f"simulator takes a scalar aux load and WS4 is "
                     f"read-only (adjudication r1/m11). The "
                     f"no-waste-heat-credit reading - 3.0 kW charged across "
                     f"the whole cycle - is exported beside it as the upper "
                     f"bound, so the timing approximation is bracketed. "
                     f"The assignment orders the cold corner as 'WS3 cold "
                     f"acceptance applied', which this exceeds - reported "
                     f"beside the ordered corner, never inside the gate, "
                     f"and escalated (ESC-2)."),
        conditioned_on_ruling="ESC-2 (pending)",
        genset_on_fraction=envelope(onfrac, seeds, duty),
        genset_on_fraction_with_the_load=envelope(onfrac_loaded, seeds, duty),
        aux_kW_used=envelope(aux_used, seeds, duty),
        fixed_point_shift_kW_vs_r1_single_pass=envelope(iters_moved, seeds,
                                                        duty),
        margin_pct_per_payload_tkm_paired=envelope(mg, seeds, duty),
        margin_pct_per_payload_tkm_paired_r1_single_pass_smear=(
            envelope(mg_r1, seeds, duty)),
        r1_single_pass_note=(
            "round 1's construction, retained so its reported number is "
            "not silently dropped: the adder taken from the UNLOADED run's "
            "engine-on fraction, one pass, no iteration. On V1 the fixed "
            "point moves the number, because V1 is the start-stop vehicle "
            "- the added electric load makes its genset run MORE, which "
            "shrinks the engine-off window the load is charged over. That "
            "correction FAVOURS the candidate, which is why the "
            "no-waste-heat-credit worst case is exported beside it. On V2 "
            "the genset runs essentially continuously, so the fixed point "
            "does not move its number at all."),
        # SWEEP (r2): this row is the HARSHEST reading of the cab-heat
        # member, so it is an upper bound on the PENALTY and therefore the
        # LOWEST margin. Round 2's first draft named it
        # `..._upper_bound` attached to a margin field, which reads as an
        # upper bound on the margin - the exact "name promises a bound it
        # does not carry" class. Named for what it is.
        margin_pct_per_payload_tkm_paired_no_waste_heat_credit_worst=(
            envelope(mg_ub, seeds, duty)),
        no_waste_heat_credit_direction=(
            "3.0 kW charged across the WHOLE cycle with no coolant credit "
            "at all: strictly more electric load than the ordered "
            "engine-off-windows-only reading, so this is the UPPER bound "
            "on the cab-heat penalty and the LOWER bound on the margin"),
        margin_ordered_corner=(RESULTS[f"{vehicle}_on_{duty}"]["cold_-10C"]
                               ["margin_pct_per_payload_tkm_paired"]["min"]),
    )
    log(f"  {vehicle} cold + cab heat: min "
        f"{COLDB[f'{vehicle}_on_{duty}']['margin_pct_per_payload_tkm_paired']['min']:+.2f}%"
        f" (no-waste-heat-credit bound "
        f"{COLDB[f'{vehicle}_on_{duty}']['margin_pct_per_payload_tkm_paired_no_waste_heat_credit_worst']['min']:+.2f}%)")
R["cold_cab_heat_bracket"] = COLDB

# ------------- M1: both pending items applied to the cold corner at once
# ESC-2 (does R30's cab-heat member extend to Vehicle Zero?) and ESC-4 (is
# CdA 4.2 or 5.4 the right road load?) are BOTH live and BOTH move V1's
# governing corner. Round 1 reported them only separately, so the
# combination - which is the case the lead actually faces if both rulings
# go the way the escalations anticipate - was never run (adjudication
# r1/M1).
log("cold corner with BOTH pending items applied (ESC-2 + ESC-4) ...")
COLD_BOTH = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    sp = case_spec("cold_-10C", vehicle)
    spr = case_spec("cold_-10C", "ruler")
    veh_cold_cda = dataclasses.replace(sp["veh"], CdA=5.4)
    mg, mg_cda_only = [], []
    for s in seeds:
        base = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                                m=sp["m"], veh=veh_cold_cda,
                                derate=sp["derate"], p_aux_kw=sp["aux"],
                                chg_accept_bus_kw=ACC["cold_-10C"])
        aux = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * (1.0
                                                      - base["eng_on_frac"])
        for _ in range(CAB_HEAT_ITERS):
            ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN,
                                  m=sp["m"], veh=veh_cold_cda,
                                  derate=sp["derate"], p_aux_kw=aux,
                                  chg_accept_bus_kw=ACC["cold_-10C"])
            aux_new = sp["aux"] + P.CAB_HEAT_KW_AT_MINUS10 * (
                1.0 - ca["eng_on_frac"])
            if abs(aux_new - aux) < 1e-9:
                aux = aux_new
                break
            aux = aux_new
        ca = CA.run_candidate(vehicle, CYC[duty][s], WS3, CHAIN, m=sp["m"],
                              veh=veh_cold_cda, derate=sp["derate"],
                              p_aux_kw=aux,
                              chg_accept_bus_kw=ACC["cold_-10C"])
        ru = RU.run_ruler(CYC[duty][s], spr["m"], veh=dataclasses.replace(
            spr["veh"], CdA=5.4), engine=ENG_REF, derate=spr["derate"],
            p_acc_kw=P.P_ACC_CRANK_KW)
        mr = metrics(ru, spr["payload_kg"])
        mg.append(100.0 * (mr["per_payload_tkm"]
                           - metrics(ca, sp["payload_kg"])["per_payload_tkm"])
                  / mr["per_payload_tkm"])
        mg_cda_only.append(
            100.0 * (mr["per_payload_tkm"]
                     - metrics(base, sp["payload_kg"])["per_payload_tkm"])
            / mr["per_payload_tkm"])
    COLD_BOTH[f"{vehicle}_on_{duty}"] = dict(
        description=("the cold corner with BOTH of this workstream's own "
                     "pending items applied at once: the R30 cab-heat "
                     "member (ESC-2) AND the E13 CdA 5.4 road load "
                     "(ESC-4), the latter applied to ruler and candidate "
                     "alike. Neither is ordered; both are live rulings."),
        conditioned_on_rulings=["ESC-2 (pending)", "ESC-4 (pending)"],
        margin_pct_per_payload_tkm_paired=envelope(mg, seeds, duty),
        margin_cold_cda_only_pct=envelope(mg_cda_only, seeds, duty),
        margin_ordered_corner=(RESULTS[f"{vehicle}_on_{duty}"]["cold_-10C"]
                               ["margin_pct_per_payload_tkm_paired"]["min"]),
        margin_cold_cab_heat_only=(
            COLDB[f"{vehicle}_on_{duty}"]
            ["margin_pct_per_payload_tkm_paired"]["min"]))
    log(f"  {vehicle} cold + cab heat + CdA 5.4: min "
        f"{COLD_BOTH[f'{vehicle}_on_{duty}']['margin_pct_per_payload_tkm_paired']['min']:+.3f}% "
        f"median "
        f"{COLD_BOTH[f'{vehicle}_on_{duty}']['margin_pct_per_payload_tkm_paired']['median']:+.3f}%")
R["cold_corner_both_pending_items"] = dict(
    why=("V1's ADVANCE is gated on its worst corner and cold_-10C IS that "
         "corner. Both of the pending items WS11 itself escalates move it, "
         "and applied together they take V1 from +19.1% to a little over "
         "+1%. The gated number is the ordered one; this row is what the "
         "lead needs in order to know how conditional the ADVANCE is."),
    rows=COLD_BOTH)

# ------------------- heat ledger for WS6 (R9) + capability/limit counters
# One pass over every vehicle x duty x case collects BOTH the WS6 heat
# ledger and the capability/limit counters WS4's simulator computes on
# every run. Round 1 discarded every one of those counters (adjudication
# r1/M3): a grep of results_ws11.json returned zero occurrences of
# `unserved`, `soc_min`, `emerg_s`, `eng_over_cont`, `starts` or
# `infeasible`. They are exported per case now, because three of them say
# something about the V2 numbers of record that the report did not say.
log("heat ledger + capability/limit counters ...")
LEDGER_ROWS = []
LIMITS = {}
_ruler_rows_done = set()
_SPLIT = dict(exhaust=0.49, coolant_oil=0.38, charge_air_cooler=0.10,
              radiation=0.03)
for vehicle, duty, cases in PRIMARY:
    key = f"{vehicle}_on_{duty}"
    LIMITS[key] = {}
    for case in cases:
        seeds = SEEDS[duty]
        sp = case_spec(case, vehicle)
        spr = case_spec(case, "ruler")
        acc = {k: [] for k in ("ru_eng", "ru_dl", "ru_fric", "ca_eng",
                               "ca_gen", "ca_chain", "ca_fric", "ca_bus")}
        pk = {k: [] for k in ("ru_eng", "ca_eng")}
        r120 = {k: [] for k in ("ru_eng", "ca_eng")}
        r600 = {k: [] for k in ("ru_eng", "ca_eng")}
        dur = []
        cnt = {k: [] for k in (
            "ca_unserved_kwh", "ca_soc_min", "ca_emerg_s",
            "ca_eng_over_cont_s", "ca_eng_over_cont_kwh",
            "ca_eng_over_cont_longest_s", "ca_eng_shaft_peak_kw",
            "ca_above_pin_demand_s", "ca_starts", "ca_over_rating_s",
            "ca_pack_chg_above_r16_s", "ca_pack_chg_above_r16_kwh",
            "ca_regen_shed_r16_kwh", "ca_pack_dis_peak_kw",
            "ca_pack_chg_peak_kw",
            "ru_unserved_wheel_kwh", "ru_unserved_fuel_g",
            "ru_infeasible_s", "ru_n_shifts", "ru_idle_s",
            "ru_idle_fuel_g", "ru_dfco_s")}
        cont_rating = None
        emerg_ceiling = None
        for s_ in seeds:
            ru, ca, _, _ = run_pair(vehicle, duty, case, s_)
            acc["ru_eng"].append(ru["eng_reject_kwh"])
            acc["ru_dl"].append(ru["eng_kwh"] - ru["e_trac_wheel_kwh"])
            acc["ru_fric"].append(ru["e_brake_wheel_kwh"])
            acc["ca_eng"].append(ca["eng_reject_kwh"])
            acc["ca_gen"].append(ca["e_gen_loss_kwh"])
            acc["ca_chain"].append(ca["e_chain_loss_kwh"])
            acc["ca_fric"].append(ca["e_fric_kwh"])
            acc["ca_bus"].append(ca["e_bus_kwh"])
            pk["ru_eng"].append(ru["eng_reject_peak_kw"])
            pk["ca_eng"].append(ca["eng_reject_peak_kw"])
            r120["ru_eng"].append(ru["eng_reject_roll120s_max_kw"])
            r120["ca_eng"].append(ca["eng_reject_roll120s_max_kw"])
            r600["ru_eng"].append(ru["eng_reject_roll600s_max_kw"])
            r600["ca_eng"].append(ca["eng_reject_roll600s_max_kw"])
            dur.append(ru["duration_s"])
            cnt["ca_unserved_kwh"].append(ca["unserved_kwh"])
            cnt["ca_soc_min"].append(ca["soc_min"])
            cnt["ca_emerg_s"].append(ca["emerg_s"])
            cnt["ca_eng_over_cont_s"].append(ca["eng_over_cont_s"])
            cnt["ca_eng_over_cont_kwh"].append(ca["eng_over_cont_kwh"])
            cnt["ca_eng_over_cont_longest_s"].append(
                ca["eng_over_cont_longest_s"])
            cnt["ca_eng_shaft_peak_kw"].append(ca["eng_shaft_peak_kw"])
            cnt["ca_above_pin_demand_s"].append(ca["above_pin_demand_s"])
            cnt["ca_starts"].append(float(ca["starts"]))
            cnt["ca_over_rating_s"].append(ca["over_rating_s"])
            cnt["ca_pack_chg_above_r16_s"].append(ca["pack_chg_above_r16_s"])
            cnt["ca_pack_chg_above_r16_kwh"].append(
                ca["pack_chg_above_r16_kwh"])
            cnt["ca_regen_shed_r16_kwh"].append(ca["regen_shed_r16_kwh"])
            cnt["ca_pack_dis_peak_kw"].append(ca["pack_dis_peak_kw"])
            cnt["ca_pack_chg_peak_kw"].append(ca["pack_chg_peak_kw"])
            cnt["ru_unserved_wheel_kwh"].append(ru["unserved_wheel_kwh"])
            cnt["ru_unserved_fuel_g"].append(ru["unserved_fuel_g"])
            cnt["ru_infeasible_s"].append(ru["infeasible_s"])
            cnt["ru_n_shifts"].append(float(ru["n_shifts"]))
            cnt["ru_idle_s"].append(ru["idle_s"])
            cnt["ru_idle_fuel_g"].append(ru["idle_fuel_g"])
            cnt["ru_dfco_s"].append(ru["dfco_s"])
            cont_rating = ca["eng_cont_rating_kw_derated"]
            emerg_ceiling = ca["emerg_ceiling_kw"]
        # SWEEP (r2): round 1 formed `mean_kW_over_cycle_max` as
        # max(energy over seeds) / median(duration over seeds) - a max
        # divided by a statistic of a different seed. Formed per seed now.
        h = float(np.median(dur)) / 3600.0
        hrs = [d_ / 3600.0 for d_ in dur]
        lbl = duty if case != "climb_10km_6pct" else duty + "+CLIMB"

        def _worst(name, hi=True):
            v = cnt[name]
            i = int(np.argmax(v)) if hi else int(np.argmin(v))
            return dict(
                worst=v[i], median=float(np.median(v)),
                worst_governing_case=(
                    f"seed {seeds[i]} of the enumerated 8-seed {lbl} "
                    f"ensemble ({'max' if hi else 'min'} over the "
                    f"enumerated seed set) [{case}]"),
                per_seed={str(sd): v[k] for k, sd in enumerate(seeds)})

        LIMITS[key][case] = dict(
            candidate=dict(
                unserved_bus_kWh=_worst("ca_unserved_kwh"),
                soc_min=_worst("ca_soc_min", hi=False),
                emergency_band_s=_worst("ca_emerg_s"),
                s_above_continuous_rating=_worst("ca_eng_over_cont_s"),
                kWh_above_continuous_rating=_worst("ca_eng_over_cont_kwh"),
                longest_run_above_continuous_rating_s=_worst(
                    "ca_eng_over_cont_longest_s"),
                engine_shaft_peak_kW=_worst("ca_eng_shaft_peak_kw"),
                above_pin_demand_s=_worst("ca_above_pin_demand_s"),
                genset_starts=_worst("ca_starts"),
                gen_over_rating_s=_worst("ca_over_rating_s"),
                pack_chg_above_r16_s=_worst("ca_pack_chg_above_r16_s"),
                pack_chg_above_r16_kWh=_worst("ca_pack_chg_above_r16_kwh"),
                regen_shed_r16_kWh=_worst("ca_regen_shed_r16_kwh"),
                pack_dis_peak_kW=_worst("ca_pack_dis_peak_kw"),
                pack_chg_peak_kW=_worst("ca_pack_chg_peak_kw"),
                continuous_rating_kW_derated=cont_rating,
                emergency_band_ceiling_kW=emerg_ceiling),
            ruler=dict(
                unserved_wheel_kWh=_worst("ru_unserved_wheel_kwh"),
                unserved_fuel_g=_worst("ru_unserved_fuel_g"),
                capability_infeasible_s=_worst("ru_infeasible_s"),
                shifts=_worst("ru_n_shifts"),
                idle_s=_worst("ru_idle_s"),
                idle_fuel_g=_worst("ru_idle_fuel_g"),
                dfco_s=_worst("ru_dfco_s")))

        comps = [
            ("ruler engine (fuel - shaft)", "ru_eng", "ruler", "ru_eng"),
            ("ruler driveline + accessories (shaft - wheel)", "ru_dl",
             "ruler", None),
            ("ruler friction brakes (all braking energy)", "ru_fric",
             "ruler", None),
            (f"{vehicle} genset engine (fuel - shaft)", "ca_eng", vehicle,
             "ca_eng"),
            (f"{vehicle} generator + rectifier", "ca_gen", vehicle, None),
            (f"{vehicle} traction chain (inverter+motor+reduction)",
             "ca_chain", vehicle, None),
            (f"{vehicle} R15 blend overflow, LUMPED resistor + friction",
             "ca_fric", vehicle, None),
        ]
        for comp, k, owner, hk in comps:
            # m7: the ruler's rows are identical under every candidate pass
            # on the same duty. Round 1 emitted them once per pass, so
            # every ruler row on VOLT-SUB appeared twice in the CSV handed
            # to WS6. Emitted once now.
            if owner == "ruler":
                sig = (duty, case, comp)
                if sig in _ruler_rows_done:
                    continue
                _ruler_rows_done.add(sig)
            v = acc[k]
            row = dict(
                vehicle=owner, duty=duty, case=case, component=comp,
                heat_kWh_per_cycle_min=min(v),
                heat_kWh_per_cycle_median=float(np.median(v)),
                heat_kWh_per_cycle_max=max(v),
                mean_kW_over_cycle_max=max(v[i] / hrs[i]
                                           for i in range(len(v))),
                mean_kW_over_cycle_max_r1_basis=max(v) / h,
                peak_kW=max(pk[hk]) if hk else None,
                roll120s_mean_kW_max=max(r120[hk]) if hk else None,
                roll600s_mean_kW_max=max(r600[hk]) if hk else None,
                max_governing_case=(f"seed {seeds[int(np.argmax(v))]} of the "
                                    f"enumerated 8-seed {duty} ensemble "
                                    f"[{case}]"))
            if hk:
                # engine rejection split on WS4's own declared class-typical
                # MD-diesel energy balance (ws4_models.engine_energy_split)
                for nm, fr in _SPLIT.items():
                    row[f"split_{nm}_kWh_median"] = (
                        float(np.median(v)) * fr)
                row["split_basis"] = ("ws4_models.engine_energy_split, "
                                      "[WS4-DECLARED] class-typical MD "
                                      "diesel balance: exhaust 49%, "
                                      "coolant+oil 38%, CAC 10%, "
                                      "radiation 3%")
            if k == "ca_fric":
                row["resistor_share_lower_bound_kWh_median"] = float(
                    np.median(cnt["ca_regen_shed_r16_kwh"]))
                row["split_basis"] = (
                    "LUMPED. WS4's simulator books R15 blend overflow and "
                    "true friction into one column (`e_fric_kwh`) and does "
                    "not export the split; WS4 is read-only so WS11 cannot "
                    "derive it without reimplementing the regen model. "
                    "This column is an UPPER bound on the brake resistor's "
                    "duty and `regen_shed_r16_kWh` is a lower bound. WS6 "
                    "owns the resistor's 50 kW steady rating as its own "
                    "sizing case and must not read this column as resistor "
                    "duty (adjudication r1/m7).")
            LEDGER_ROWS.append(row)
        c = LIMITS[key][case]["candidate"]
        if (c["s_above_continuous_rating"]["worst"] > 0
                or c["unserved_bus_kWh"]["worst"] > 0):
            log(f"  LIMIT {key}[{case}]: "
                f"{c['s_above_continuous_rating']['worst']:.1f} s above the "
                f"{cont_rating:.1f} kW continuous rating, "
                f"unserved {c['unserved_bus_kWh']['worst']:.3f} kWh, "
                f"SOC min {c['soc_min']['worst']:.3f}")
R["heat_ledger_ws6"] = dict(
    convention=("R9: rejected heat by component and operating case. Energies "
                "are per cycle realisation; mean kW is over the cycle "
                "duration. A cooling owner sizes against a WINDOW, so the "
                "instantaneous peak and the peak 120 s / 600 s rolling "
                "window means are exported for both engines (adjudication "
                "r1/m7, following WS4's own KX-m7). Engine rejection "
                "carries WS4's declared exhaust / coolant+oil / CAC / "
                "radiation split. WS6 sizes to its own steady lines. The "
                "pack loop is WS3's export and is not re-derived here."),
    rows=LEDGER_ROWS)
# WS4's OWN wider exposure statement for the same effect, read read-only
# from the vintage pinned in _meta.input_sha256. WS11 measures the counters
# on WS11's own case set; WS4's KX r3 restated ESC-10 on a wider measured
# set inside R6's own rating family, and that is the number the lead is
# being asked to rule on. Both are carried so neither stands in for the
# other.
_SD2 = WS4J["interface_ws4"]["series_duty_v2"]
_probe = _SD2.get("r6_rating_family_probe")
_bpcap = _SD2.get("companion_bp_capability_comparison", {})
R["ws4_esc10_exposure_as_read"] = dict(
    _source="../WS4_genset/results_ws4.json, interface_ws4.series_duty_v2",
    _vintage_sha256=INPUT_SHA["WS4/results_ws4.json"],
    _consumed_as=("READ-ONLY quotation of another workstream's export. WS11 "
                  "does not re-derive it and does not use it in any margin. "
                  "It is carried because WS11's own M3 disclosure - that "
                  "the V2 numbers of record involve operation above the "
                  "R18-ratified continuous flat-rating - must be stated on "
                  "WS4's current framing, not on a superseded one."),
    present_in_this_vintage=bool(_probe),
    ordered_set_worst_over_rating_s=(
        _probe.get("ordered_set_worst_over_rating_s") if _probe else None),
    union_worst_over_rating_s=(
        _probe.get("union_worst_over_rating_s") if _probe else None),
    union_worst_over_rating_s_governing_case=(
        _probe.get("union_worst_over_rating_s_governing_case")
        if _probe else None),
    union_case_set=(_probe.get("union_case_set") if _probe else None),
    engine_shaft_peak_pct_of_continuous_rating_worst=_bpcap.get(
        "engine_shaft_peak_pct_of_continuous_rating_worst"),
    engine_shaft_peak_pct_governing_case=_bpcap.get(
        "engine_shaft_peak_pct_of_continuous_rating_worst_governing_case"),
    note=("WS4 KX r3 restated ESC-10's exposure as a UNION maximum over "
          "the ordered case set and an R6 rating-family probe set, and "
          "corrected the peak-shaft percentage to be referenced to each "
          "case's OWN rating (the r2 figure divided a max over all three "
          "cases by one case's rating). WS11's own counters below are "
          "measured on WS11's case set, which is a different set for a "
          "different purpose; the two are not comparable and neither is "
          "presented as the other."),
    vintage_pins_slash_free=dict(
        ws4_results_json=INPUT_SHA["WS4/results_ws4.json"],
        ws4_sim_py=INPUT_SHA["WS4/ws4_sim.py"],
        ws4_models_py=INPUT_SHA["WS4/ws4_models.py"],
        ws4_chain_py=INPUT_SHA["WS4/ws4_chain.py"],
        note=("the same values as _meta.input_sha256, keyed without the "
              "'/' so the report generator's dotted-path resolver can "
              "reach them and assert them verbatim")),
    hot_swap_note=("if a later WS4 vintage drops or renames these fields, "
                   "`present_in_this_vintage` goes false and the exported "
                   "values go null rather than silently carrying a stale "
                   "quotation"))

R["capability_and_limit_counters"] = dict(
    why=("WS4's simulator computes a full set of capability and limit "
         "counters on every run and round 1 exported none of them "
         "(adjudication r1/M3). Three of them bear on the V2 numbers of "
         "record: V2 operates ABOVE its R18-ratified 132 kW continuous "
         "flat-rating in most cases including the nominal case that "
         "produces the headline; on the governing climb corner its pack "
         "reaches SOC 0 with unserved bus energy; and the RULER is "
         "capability-infeasible on every VOLT-REG case, with its shortfall "
         "charged to fuel at its own cycle-mean BSFC. All three point "
         "TOWARD the candidate - they make the ruler thirstier and let V2 "
         "deliver more energy at a good BSFC - so none of them changes "
         "either verdict. They are disclosed because the exported V2 "
         "numbers are not achievable inside V2's own ratified rating."),
    emergency_band_note=("the emergency band's engine ceiling is the "
                         "AUTOMOTIVE full-load curve, not the genset's "
                         "continuous flat-rating; that is WS4's own KX-M1 "
                         "issue and WS4 ships an "
                         "`emerg_cap_cont_rating` bracket for it, which "
                         "WS11 now exercises - see "
                         "`emergency_band_at_continuous_rating_bracket`."),
    rows=LIMITS)

# ------------------------------- further declared-choice brackets (r1 minors)
log("declared-choice brackets: engine curve, emergency band, derate "
    "convention, climb splice ...")
DECL = {}

# --- m3: the ruler's engine CURVE. Round 1's s1.1 asserted that the
# difference between the ordered WS4 reference map and the sourced 2023
# spec sheet was "inside the brackets in s1.3"; no bracket varied the
# engine curve, so the claim was asserted and not run. It is run now.
# [WS11-DECLARED] Isuzu publishes no torque curve, so two declared
# constructions bracket it: (a) the spec sheet's own two rated points
# (452 lb-ft = 612.83 Nm, 215 hp = 160.3 kW at 2,500 rpm) read as a flat
# plateau, and (b) the ordered reference curve scaled uniformly to the
# sourced peak power.
_T_SOURCED = 452.0 * 1.35581794833      # lb-ft -> Nm
_P_SOURCED_KW = 215.0 * 0.745699872
_low = _T_SOURCED / 685.0               # ENG_REF's 1,400 rpm torque
_hi_shape = [550.0 / 610.0, 490.0 / 610.0, 430.0 / 610.0]
ENG_SOURCED_CURVE = WillansEngine(
    "4HK1-TC-sourced2023-W", 5.193,
    (700, 1000, 1200, 1400, 1600, 1850, 2200, 2500, 2600, 2800, 3000),
    (380.0 * _low, 540.0 * _low, 630.0 * _low, _T_SOURCED, _T_SOURCED,
     _T_SOURCED, _T_SOURCED, _T_SOURCED, _T_SOURCED * _hi_shape[0],
     _T_SOURCED * _hi_shape[1], _T_SOURCED * _hi_shape[2]),
    eta_i0=ENG_REF.eta_i0, fmep_a=ENG_REF.fmep_a,
    idle_rpm=ENG_REF.idle_rpm, rated_cont_kw=ENG_REF.rated_cont_kw,
    rated_cont_rpm=ENG_REF.rated_cont_rpm, mass_kg=500.0,
    label="[WS11-DECLARED] 2023 NPR-HD spec sheet read as a flat plateau: "
          "612.8 Nm from 1,400 to 2,500 rpm, 160.4 kW peak at 2,500")
_scale = _P_SOURCED_KW / ENG_REF.peak_power_kw()
ENG_SCALED_CURVE = WillansEngine(
    "4HK1-TC-ref-scaled-to-sourced-peak-W", 5.193, ENG_REF.rpm_pts,
    np.asarray(ENG_REF.trq_pts, float) * _scale,
    eta_i0=ENG_REF.eta_i0, fmep_a=ENG_REF.fmep_a,
    idle_rpm=ENG_REF.idle_rpm, rated_cont_kw=ENG_REF.rated_cont_kw,
    rated_cont_rpm=ENG_REF.rated_cont_rpm, mass_kg=500.0,
    label=f"[WS11-DECLARED] the ordered reference curve scaled uniformly by "
          f"{_scale:.6f} so its peak power equals the sourced 215 hp")

ENGINE_CURVES = {"ordered_ws4_reference": ENG_REF,
                 "sourced_2023_spec_sheet_plateau": ENG_SOURCED_CURVE,
                 "reference_scaled_to_sourced_peak_power": ENG_SCALED_CURVE}
ENG_CURVE = {}
for cname, eng in ENGINE_CURVES.items():
    per = {}
    for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
        seeds = SEEDS[duty]
        sp = case_spec("nominal", vehicle)
        spr = case_spec("nominal", "ruler")
        ls, mg = [], []
        for s_ in seeds:
            ru = RU.run_ruler(CYC[duty][s_], spr["m"], veh=spr["veh"],
                              engine=eng, derate=spr["derate"],
                              p_acc_kw=P.P_ACC_CRANK_KW)
            ca = CA.run_candidate(vehicle, CYC[duty][s_], WS3, CHAIN,
                                  m=sp["m"], veh=sp["veh"],
                                  derate=sp["derate"], p_aux_kw=sp["aux"],
                                  chg_accept_bus_kw=ACC["nominal"])
            mr = metrics(ru, spr["payload_kg"])
            mc = metrics(ca, sp["payload_kg"])
            ls.append(mr["l_per_100km"])
            mg.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                      / mr["per_payload_tkm"])
        per[f"{vehicle}_on_{duty}"] = dict(
            ruler_l_per_100km=envelope(ls, seeds, duty),
            margin_pct_per_payload_tkm_paired=envelope(mg, seeds, duty))
    per["engine_label"] = eng.label
    per["peak_power_kW"] = eng.peak_power_kw()
    per["peak_torque_Nm"] = float(np.max(eng.trq_pts))
    ENG_CURVE[cname] = per
    log(f"  engine curve {cname}: peak {eng.peak_power_kw():.1f} kW, "
        f"V2 margin min "
        f"{per['V2_on_VOLT-REG']['margin_pct_per_payload_tkm_paired']['min']:+.3f}%")
_b = ENG_CURVE["ordered_ws4_reference"]
# SWEEP (r2): the worst shift must be a paired per-seed difference, not a
# difference of two independently minimised ensemble numbers.
_ec_shift = {}
for cname in ENGINE_CURVES:
    if cname == "ordered_ws4_reference":
        continue
    for k in ("V1_on_VOLT-SUB", "V2_on_VOLT-REG"):
        duty = k.split("_on_")[1]
        seeds = SEEDS[duty]
        a = ENG_CURVE[cname][k]["margin_pct_per_payload_tkm_paired"][
            "per_seed"]
        b = _b[k]["margin_pct_per_payload_tkm_paired"]["per_seed"]
        d = [a[str(sd)] - b[str(sd)] for sd in seeds]
        _ec_shift[f"{cname}|{k}"] = envelope(d, seeds, duty)
_ec_worst = max(max(abs(e["min"]), abs(e["max"]))
                for e in _ec_shift.values())
DECL["ruler_engine_curve"] = dict(
    issue=("the assignment orders WS4's reference 4HK1-class map "
           "(700 Nm @ 1,600 rpm, ~153 kW). The sourced 2023 spec sheet "
           "rates the truck at 215 hp @ 2,500 and 452 lb-ft @ 1,850 - more "
           "peak power, appreciably less low-end torque. Round 1 stated "
           "the discrepancy and claimed the difference was inside its "
           "brackets; no bracket varied the engine curve. Run now "
           "(adjudication r1/m3)."),
    curves=ENG_CURVE,
    paired_shift_pp=_ec_shift,
    worst_margin_shift_pp=_ec_worst,
    worst_margin_shift_statistic=("PAIRED: the largest absolute per-seed "
                                  "difference, over the enumerated curve "
                                  "set x vehicle set (R36/D13)"),
    reading=("the ordered map is retained as the run of record because the "
             "assignment names it. Neither declared alternative moves "
             "either verdict."))

# --- M3: WS4's own emergency-band bracket, exercised.
log("emergency band capped at the continuous rating (WS4 KX-M1 bracket) ...")
EMB = {}
for vehicle, duty, cases in PRIMARY:
    key = f"{vehicle}_on_{duty}"
    EMB[key] = {}
    seeds = SEEDS[duty]
    spr_n = case_spec("nominal", "ruler")
    for case in cases:
        sp = case_spec(case, vehicle)
        spr = case_spec(case, "ruler")
        mg, uns, ov = [], [], []
        for s_ in seeds:
            cyc = (CYC_CLIMB[s_] if sp["cycle"] == "climb"
                   else CYC[duty][s_])
            ca = CA.run_candidate(vehicle, cyc, WS3, CHAIN, m=sp["m"],
                                  veh=sp["veh"], derate=sp["derate"],
                                  p_aux_kw=sp["aux"],
                                  chg_accept_bus_kw=ACC[case],
                                  emerg_cap_cont_rating=True)
            ru = RU.run_ruler(cyc, spr["m"], veh=spr["veh"], engine=ENG_REF,
                              derate=spr["derate"],
                              p_acc_kw=P.P_ACC_CRANK_KW)
            mr = metrics(ru, spr["payload_kg"])
            mc = metrics(ca, sp["payload_kg"])
            mg.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                      / mr["per_payload_tkm"])
            uns.append(ca["unserved_kwh"])
            ov.append(ca["eng_over_cont_s"])
        lbl = duty if case != "climb_10km_6pct" else duty + "+CLIMB"
        EMB[key][case] = dict(
            margin_pct_per_payload_tkm_paired=envelope(mg, seeds, lbl),
            unserved_bus_kWh_worst=max(uns),
            s_above_continuous_rating_worst=max(ov),
            margin_ordered_pct_min=(
                RESULTS[key][case]
                ["margin_pct_per_payload_tkm_paired"]["min"]),
            **paired_shift(mg, RESULTS[key][case], seeds, lbl))
    log(f"  {key} emerg-capped: nominal margin min "
        f"{EMB[key]['nominal']['margin_pct_per_payload_tkm_paired']['min']:+.3f}% "
        f"(shift {EMB[key]['nominal']['shift_pp']:+.3f} pp)")
DECL["emergency_band_at_continuous_rating_bracket"] = dict(
    issue=("WS4's emergency band lets the series engine follow load up to "
           "the AUTOMOTIVE full-load curve, which for ENG_V2 is well above "
           "the R18-ratified 132 kW continuous flat-rating. WS4 ships "
           "`emerg_cap_cont_rating` for exactly this (its own KX-M1) and "
           "round 1 never exercised it (adjudication r1/M3)."),
    rule=("the emergency band's engine ceiling becomes the genset's "
          "continuous rating x derate. Energy the band can no longer "
          "deliver is booked as unserved and fuel-corrected."),
    rows=EMB)

# --- m8: the derated-load-fraction asymmetry at the altitude corner.
log("derated load-fraction convention (m8) ...")
_dl = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    seeds = SEEDS[duty]
    sp = case_spec("alt2000m_45C", vehicle)
    spr = case_spec("alt2000m_45C", "ruler")
    ls, mg = [], []
    for s_ in seeds:
        ru = RU.run_ruler(CYC[duty][s_], spr["m"], veh=spr["veh"],
                          engine=ENG_REF, derate=spr["derate"],
                          p_acc_kw=P.P_ACC_CRANK_KW,
                          derate_load_fraction=True)
        ca = CA.run_candidate(vehicle, CYC[duty][s_], WS3, CHAIN, m=sp["m"],
                              veh=sp["veh"], derate=sp["derate"],
                              p_aux_kw=sp["aux"],
                              chg_accept_bus_kw=ACC["alt2000m_45C"])
        mr = metrics(ru, spr["payload_kg"])
        mc = metrics(ca, sp["payload_kg"])
        ls.append(mr["l_per_100km"])
        mg.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                  / mr["per_payload_tkm"])
    _dl[f"{vehicle}_on_{duty}"] = dict(
        ruler_l_per_100km=envelope(ls, seeds, duty),
        margin_pct_per_payload_tkm_paired=envelope(mg, seeds, duty),
        margin_ordered_pct_min=(
            RESULTS[f"{vehicle}_on_{duty}"]["alt2000m_45C"]
            ["margin_pct_per_payload_tkm_paired"]["min"]),
        **paired_shift(mg, RESULTS[f"{vehicle}_on_{duty}"]["alt2000m_45C"],
                       seeds, duty))
DECL["derated_load_fraction_convention"] = dict(
    issue=("at the altitude corner WS4's `_bsfc_fast` refers the "
           "candidate's load fraction phi - and hence the smoke-limit term "
           "- to the DERATED full-load curve, while `ws11_ruler` calls "
           "`engine.bsfc`, which refers phi to the UNDERATED curve. The two "
           "vehicles were therefore on different conventions at that "
           "corner, undeclared, and it favoured the ruler (adjudication "
           "r1/m8). Quantified by re-running the ruler on the candidate's "
           "convention."),
    ordered_convention="phi against the underated curve (round-1 behaviour, "
                       "retained as the run of record so no verdict number "
                       "moves silently)",
    rows=_dl)

# --- m12: the climb splice point sets the corner's severity.
log("climb splice bracket at WS1 s4.4's own 85 km/h posing (m12) ...")
CYC_CLIMB85 = {s_: KP.insert_climb(CYC["VOLT-REG"][s_], speed_kmh=85.0)
               for s_ in REG_SEEDS}
_c85 = []
for s_ in REG_SEEDS:
    sp = case_spec("climb_10km_6pct", "V2")
    spr = case_spec("climb_10km_6pct", "ruler")
    ru = RU.run_ruler(CYC_CLIMB85[s_], spr["m"], veh=spr["veh"],
                      engine=ENG_REF, derate=spr["derate"],
                      p_acc_kw=P.P_ACC_CRANK_KW)
    ca = CA.run_candidate("V2", CYC_CLIMB85[s_], WS3, CHAIN, m=sp["m"],
                          veh=sp["veh"], derate=sp["derate"],
                          p_aux_kw=sp["aux"],
                          chg_accept_bus_kw=ACC["climb_10km_6pct"])
    mr = metrics(ru, spr["payload_kg"])
    mc = metrics(ca, sp["payload_kg"])
    _c85.append(100.0 * (mr["per_payload_tkm"] - mc["per_payload_tkm"])
                / mr["per_payload_tkm"])
DECL["climb_splice_speed_bracket"] = dict(
    issue=("splicing at 30% of route distance fixes the demanded climb "
           "speed at "
           f"{R['climb_insert']['demanded_speed_kmh']:.2f} km/h. WS1 s4.4 - "
           "the case the assignment names - poses the same climb at "
           "85 km/h and states that holding 85 km/h up a 10 km 6% grade is "
           "not achievable on any buffer this study contemplates. WS11's "
           "corner is therefore materially HARDER than its own reference. "
           "Round 1 declared the splice but did not bracket it "
           "(adjudication r1/m12)."),
    ordered_reading_demanded_speed_kmh=R["climb_insert"]
    ["demanded_speed_kmh"],
    ws1_posing_demanded_speed_kmh=85.0,
    V2_margin_at_85kmh_climb=envelope(_c85, REG_SEEDS, "VOLT-REG+CLIMB85"),
    V2_margin_at_ordered_climb_min=(
        RESULTS["V2_on_VOLT-REG"]["climb_10km_6pct"]
        ["margin_pct_per_payload_tkm_paired"]["min"]),
    reading=("the 30%-splice reading is retained for the gate because it is "
             "the one round 1 gated on and the corner is not V2's binding "
             "constraint under either reading; the softer, WS1-faithful "
             "reading is exported beside it."))
R["declared_choice_brackets"] = DECL

# --- m9 / m10: the ruler's chassis-cab line, cross-checked and bounded
_ZA_TARE_KG = 2620.0
_body_sens = {}
for vehicle, duty in (("V1", "VOLT-SUB"), ("V2", "VOLT-REG")):
    base = RESULTS[f"{vehicle}_on_{duty}"]["nominal"]
    seeds = SEEDS[duty]
    rows = {}
    for d_kg in (-100.0, 100.0):
        pr = PAY["ruler"] - d_kg
        pc = PAY[vehicle] - d_kg
        mg = []
        for sd in seeds:
            mk = base["margin_pct_per_km_paired"]["per_seed"][str(sd)]
            mg.append(100.0 * (1.0 - (1.0 - mk / 100.0) * pr / pc))
        e = envelope(mg, seeds, duty)
        rows[f"{d_kg:+.0f}kg"] = dict(
            margin_pct_per_payload_tkm_paired=e,
            **paired_shift(mg, base, seeds, duty))
    _body_sens[f"{vehicle}_on_{duty}"] = rows
R["ruler_chassis_cab_cross_check"] = dict(
    issue=("the chassis-cab line is tagged [SOURCED] but is an "
           "INTERPOLATION: the spec sheet publishes a body/payload "
           "allowance RANGE (7,545-8,511 lb) across four wheelbases "
           "without saying which end belongs to which, and ws11_params "
           "assumes it falls linearly with wheelbase. The 545 kg body is "
           "then a residual defined to close to WS1's ratified operating "
           "curb, which is itself a WS1 assumption. Recorded plainly "
           "(adjudication r1/m10)."),
    tag_correction="[SOURCED-RANGE, INTERPOLATED IN WHEELBASE]",
    interpolated_allowance_lb=P.ALLOWANCE_AT_WB_LB,
    chassis_cab_curb_kg=P.CHASSIS_CAB_CURB_KG,
    za_cross_check=dict(
        source="sources/isuzu_za_NPR400_spec_sheet.txt (Isuzu South "
               "Africa NPR 400, print date December 2017)",
        tare_total_kg=_ZA_TARE_KG,
        wheelbase_mm=3815.0,
        wheelbase_in=3815.0 / 25.4,
        differences=("a DIFFERENT truck on the same platform: 7,500 kg GVM "
                     "(not 14,500 lb), Euro 2 4HK1-TCN (no DPF/SCR/DEF), a "
                     "MYY6S manual gearbox (not the A465id automatic and "
                     "converter), and only 15 L of fuel counted in tare. "
                     "At essentially the same wheelbase "
                     "(3,815 mm = 150.2 in) it reads "
                     f"{P.CHASSIS_CAB_CURB_KG - _ZA_TARE_KG:.0f} kg lighter "
                     "than the US-market figure derived here."),
        effect_on_any_number=("NONE. The ruler's ledger is built to WS1's "
                              "ratified 3,700 kg operating curb with the "
                              "16 ft body as the single reconciliation "
                              "item, so a different chassis-cab figure "
                              "moves the chassis/body SPLIT and leaves "
                              "every mass, payload and margin in this "
                              "report unchanged. Round 1 left the sheet in "
                              "sources/ unpinned and unmentioned; it is "
                              "pinned and answered here."),
    ),
    ruler_operating_curb_sensitivity=dict(
        rule=("the quantity that WOULD move margins is the TOTAL operating "
              "curb, because it moves both payload denominators at fixed "
              "GVW. Exact algebra at +/-100 kg (both vehicles keep the "
              "same body, so both payloads move by the same amount)."),
        rows=_body_sens),
)

# --- m2: the aftertreatment bracket's effect on the metric, computed
_pay_at = PAY["V2_aftertreatment_bracket"]
_at = {}
for duty in ("VOLT-REG", "VOLT-SUB"):
    base = RESULTS[f"V2_on_{duty}"]["nominal"]
    seeds = SEEDS[duty]
    mg = []
    for sd in seeds:
        mk = base["margin_pct_per_km_paired"]["per_seed"][str(sd)]
        mg.append(100.0 * (1.0 - (1.0 - mk / 100.0) * PAY["ruler"] / _pay_at))
    e = envelope(mg, seeds, duty)
    _at[f"V2_on_{duty}"] = dict(
        margin_pct_per_payload_tkm_paired=e,
        margin_headline_min=base["margin_pct_per_payload_tkm_paired"]["min"],
        **paired_shift(mg, base, seeds, duty))
R["v2_aftertreatment_bracket_effect"] = dict(
    kg=P.V2_AFTERTREATMENT_BRACKET_KG,
    pct_of_v2_payload=100.0 * P.V2_AFTERTREATMENT_BRACKET_KG / PAY["V2"],
    note=("60 kg is "
          f"{100.0 * P.V2_AFTERTREATMENT_BRACKET_KG / PAY['V2']:.2f}% of "
          "V2's payload but it does NOT move the metric by that many "
          "points: the metric moves by the shift below, because the "
          "payload appears in a ratio against the RULER's payload, not as "
          "a fraction of itself. Round 1's ESC-3 asserted the two were the "
          "same number (adjudication r1/m2)."),
    conditioned_on_ruling="ESC-3 (pending)",
    rows=_at)

# supporting scalars for ESC-8 / ESC-9, computed from the run, never typed
_V1_ON_FRAC = float(np.median(
    [CA.run_candidate("V1", CYC["VOLT-SUB"][s_], WS3, CHAIN,
                      m=P.M_GVW_KG, chg_accept_bus_kw=ACC["nominal"])
     ["eng_on_frac"] for s_ in SUB_SEEDS]))
_v1n = [CA.run_candidate("V1", CYC["VOLT-SUB"][s_], WS3, CHAIN,
                         m=P.M_GVW_KG, chg_accept_bus_kw=ACC["nominal"])
        for s_ in SUB_SEEDS]
_V1_STARTS = float(np.median([o["starts"] for o in _v1n]))
_V1_DUR_S = float(np.median([o["duration_s"] for o in _v1n]))
_V1_OFF_BLOCK_MIN = ((1.0 - _V1_ON_FRAC) * _V1_DUR_S
                     / max(_V1_STARTS, 1.0) / 60.0)
_v2lim = LIMITS["V2_on_VOLT-REG"]
_N_CASES_TOT = len(_v2lim)
_N_CASES_OVER = sum(
    1 for c in _v2lim
    if _v2lim[c]["candidate"]["s_above_continuous_rating"]["worst"] > 0.0)
_NOM_OVER_S = _v2lim["nominal"]["candidate"][
    "s_above_continuous_rating"]["worst"]
_NOM_OVER_KWH = _v2lim["nominal"]["candidate"][
    "kWh_above_continuous_rating"]["worst"]
_CLIMB_SOC = _v2lim["climb_10km_6pct"]["candidate"]["soc_min"]["worst"]
_CLIMB_UNSERVED = _v2lim["climb_10km_6pct"]["candidate"][
    "unserved_bus_kWh"]["worst"]
R["thermal_and_rating_support"] = dict(
    v1_genset_on_fraction_median=_V1_ON_FRAC,
    v1_genset_starts_per_cycle_median=_V1_STARTS,
    v1_mean_engine_off_block_min=_V1_OFF_BLOCK_MIN,
    v2_cases_above_continuous_rating=_N_CASES_OVER,
    v2_cases_total=_N_CASES_TOT,
    v2_nominal_s_above_continuous_rating=_NOM_OVER_S,
    v2_nominal_kWh_above_continuous_rating=_NOM_OVER_KWH,
    v2_climb_soc_min=_CLIMB_SOC,
    v2_climb_unserved_bus_kWh=_CLIMB_UNSERVED,
    note=("scalars quoted in ESC-8 and ESC-9, exported so they verify "
          "verbatim like every other reported number"))

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
               "declared physics, not on a measured NPR. "
               "I MUST STATE THE CONSEQUENCE PLAINLY, which round 1 did "
               "not: the assignment's word is 'calibrate', and I did not "
               "calibrate. For V1's ADVANCE that is safe - the residual is "
               "in the ruler's favour and the margin is a lower bound. For "
               "V2's KILL it is the unsafe direction, and the quantity "
               "that matters is the flip point, not the residual. V2 draws "
               "with the ruler if the real NPR burns only "
               f"{FLIP['V2_on_VOLT-REG']['_verdict_reading']['pct_ruler_fuel_error_to_draw']:.2f}% "
               "more fuel than modelled, and reaches the 3% ADVANCE bar at "
               f"{FLIP['V2_on_VOLT-REG']['_verdict_reading']['pct_ruler_fuel_error_to_3pct_bar']:.2f}%. "
               "The anchor says the real fleet burns "
               f"{100.0 * (ANCHOR_ALL['l_per_100km'] / _hl['VOLT-SUB']['l_per_100km']['median'] - 1.0):.0f}% "
               "more (all model years) or "
               f"{100.0 * (ANCHOR_4HK1['l_per_100km'] / _hl['VOLT-SUB']['l_per_100km']['median'] - 1.0):.0f}% "
               "more (4HK1-era subset). And the eight ruler-modelling "
               "levers this workstream declares are on their own enough to "
               "close that gap: at their declared pessimistic ends V2's "
               "nominal margin is "
               f"{BRK_MARGIN['V2_on_VOLT-REG']['all_ruler_modelling_choices_pessimistic']['min']:+.2f}% "
               "min / "
               f"{BRK_MARGIN['V2_on_VOLT-REG']['all_ruler_modelling_choices_pessimistic']['median']:+.2f}% "
               "median. The lead is being asked to execute a KILL on an "
               "UNCALIBRATED ruler and should decide with that in front of "
               "it."),
         requested=("a ruling on whether an uncalibrated ruler may carry a "
                    "KILL at all; and either accept the "
                    "validation-not-fit treatment on the record or fund a "
                    "cycle-resolved chassis-dyno or logged-route "
                    "measurement of an NPR-HD as a WS7 item BEFORE V2's "
                    "KILL is executed")),
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
               "becomes the corner of record. "
               "The exposure, which round 1 understated: cold_-10C IS V1's "
               "governing corner. As ordered it is "
               f"{VERDICTS['V1_on_VOLT-SUB']['worst_corner_margin_pct']:+.2f}%. "
               "With the cab-heat member it is "
               f"{COLDB['V1_on_VOLT-SUB']['margin_pct_per_payload_tkm_paired']['min']:+.2f}%. "
               "With the cab-heat member AND ESC-4's CdA 5.4 - both of "
               "which are live rulings and neither of which is mine to "
               "make - it is "
               f"{COLD_BOTH['V1_on_VOLT-SUB']['margin_pct_per_payload_tkm_paired']['min']:+.3f}% "
               "min / "
               f"{COLD_BOTH['V1_on_VOLT-SUB']['margin_pct_per_payload_tkm_paired']['median']:+.3f}% "
               "median, i.e. V1's ADVANCE clears the >=0% corner bar by "
               "about a point. V1's ADVANCE is real but it is CONDITIONAL "
               "on these two rulings."),
         requested=("a ruling extending or not extending R30 to Vehicle "
                    "Zero, taken together with ESC-4, because it is the "
                    "COMBINATION that decides how much headroom V1's "
                    "ADVANCE actually has")),
    dict(id="ESC-3", challenges="WS4 interface_ws4.v2_genset.mass_kg",
         title="WS4's `aftertreatment_extra: 60 kg` is ambiguous and it moves "
               "V2's payload by 60 kg",
         text=("WS4 exports the V2 genset as total_dry 637 kg PLUS a "
               "separate `aftertreatment_extra: 60.0`. The 4HK1-V2C is "
               "declared to be the same production hardware as the ruler's "
               "4HK1-TC, so on one reading its aftertreatment is the stock "
               "truck's aftertreatment and cancels; on the other reading it "
               "is 60 kg the candidate carries and the ruler does not. "
               "60 kg is "
               f"{100.0 * P.V2_AFTERTREATMENT_BRACKET_KG / PAY['V2']:.2f}% "
               "of V2's payload, but it does NOT move the metric by that "
               "many points - the payload enters as a ratio against the "
               "RULER's payload, not as a fraction of itself, and the "
               "measured shift on VOLT-REG is "
               f"{_at['V2_on_VOLT-REG']['shift_pp']:+.2f} pp "
               f"({_at['V2_on_VOLT-REG']['margin_headline_min']:+.3f}% to "
               f"{_at['V2_on_VOLT-REG']['margin_pct_per_payload_tkm_paired']['min']:+.3f}%). "
               "Round 1 asserted the two were the same number "
               "(adjudication r1/m2). I have taken the cancelling reading "
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
    dict(id="ESC-5", challenges="Gate G1's net-energy demand-trace "
                                "convention (BASELINE_v1), inherited by "
                                "WS4's ratified simulator",
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
               "separately so the lead can see what the metric cannot. "
               "Round 1 cited R9 here; that is the ensembles / part-load / "
               "heat-ledger ruling and it is not what this challenges. The "
               "citation is corrected to Gate G1's convention "
               "(adjudication r1/m4). Round 1's capability pass also did "
               "not enforce steady-state capability at all, so the "
               "settled-climb speeds it offered the lead as the remedy "
               "were wrong in the export; that is fixed (r1/B2) and the "
               "forward pass now reconciles with the closed-form "
               "sustainable speeds to "
               f"{max(r['ruler_abs_difference_kmh'] for r in RECON['rows'].values()):.2f} km/h "
               "on the ruler and "
               f"{max(r['candidate_abs_difference_kmh'] for r in RECON['rows'].values()):.2f} km/h "
               "on the candidate."),
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
               "inherit a corner that switches the metric off. "
               "WHICH READING IS THE NOVEL ONE, which round 1 did not say: "
               "the VARIANT reading is the program's established "
               "convention, not the ordered one. "
               "`WS8_semi_architecture/ws8_candidates.py` defines "
               "`payload_kg()` as `(m_gcw - tare_common - powertrain_mass) "
               "* ctx.payload_factor`, i.e. it scales EACH VEHICLE'S OWN "
               "payload, and WS9 inherited that under the R28/ESC-3 corner "
               "set this assignment mirrors. The literal reading I gated "
               "on is therefore a DEPARTURE from the convention the "
               "program has been running, not merely an ambiguity in my "
               "assignment's wording. Note also that "
               "`interface_ws11.verdicts.V2_on_VOLT-REG."
               "corner_margins_pct_min` exports "
               f"payload_p20 {VERDICTS['V2_on_VOLT-REG']['corner_margins_pct_min']['payload_p20']:+.2f} "
               f"and payload_m20 {VERDICTS['V2_on_VOLT-REG']['corner_margins_pct_min']['payload_m20']:+.2f}, "
               "which read on their face as V2 winning at those corners; "
               "they are the per-KM margin under a different name, because "
               "the denominators cancel."),
         requested=("a ruling fixing the payload-corner convention for "
                    "Vehicle Zero and Vehicle One alike, on the record "
                    "that WS8's `payload_kg()` and R28/ESC-3 already fix "
                    "it the other way for Vehicle One")),
    dict(id="ESC-8",
         challenges="R9's part-load convention as it applies to engine "
                    "THERMAL state, and WS4's `fmep_bar()` warm-engine "
                    "friction model",
         title="Nothing in the ratified toolchain can express duty-cycle "
               "thermal cycling, and the one mechanism V1's ADVANCE rests "
               "on is the one that would be charged for it",
         text=("Round 1 classified the missing cold-engine friction / "
               "warm-up model as 'roughly neutral' on the ground that the "
               "ruler and V2 share an engine and V1's is smaller. That "
               "reasoning addresses the INITIAL cold start. It does not "
               "address the asymmetry that matters, which is duty-cycle "
               "thermal cycling: on VOLT-SUB V1's genset is OFF about "
               f"{100.0 * (1.0 - _V1_ON_FRAC):.0f}% of the time in roughly "
               f"{_V1_STARTS:.0f} blocks per cycle, so its off-blocks "
               "average on the order of "
               f"{_V1_OFF_BLOCK_MIN:.0f} minutes, while the ruler's engine "
               "runs continuously and stays hot. WS4's `fmep_bar()` is a "
               "function of rpm only and is documented as a warm-engine "
               "model, so the ratified simulator CANNOT express the "
               "penalty; `START_FUEL_G = 12.0` covers a load-acceptance "
               "ramp, not a thermal state. I cannot quantify this without "
               "a thermal model and I am not going to invent one inside a "
               "ruler trial. The finding I can state is that the omission "
               "is NOT roughly neutral: it systematically flatters the "
               "single mechanism V1's ADVANCE rests on - engine-off is "
               f"worth {ONE['V1_on_VOLT-SUB']['start_stop_engine_off']['worth_pp']:.2f} pp "
               "of V1's margin - and it is larger at -10 C, which is V1's "
               "binding corner (adjudication r1/M8)."),
         requested=("a ruling on whether a cold/warm-up friction member is "
                    "required before a start-stop advantage is ratified, "
                    "and if so an owner for it - it is a WS4 engine-model "
                    "item, not a WS11 one")),
    dict(id="ESC-9",
         challenges="R18's ratified 132 kW continuous flat-rating for the "
                    "4HK1-V2C, and WS4's own KX-M1 emergency-band ceiling",
         title="The V2 numbers of record are produced by runs that operate "
               "above V2's ratified continuous rating, and on the "
               "governing corner they empty the pack",
         text=("WS4's simulator lets the series engine leave its pin in the "
               "emergency band and follow load up to the AUTOMOTIVE "
               "full-load curve, which for ENG_V2 is above the "
               "R18-ratified 132 kW continuous flat-rating. Reading WS4's "
               "own counters, which round 1 discarded entirely: V2 spends "
               "time above its continuous rating in "
               f"{_N_CASES_OVER} of {_N_CASES_TOT} exported cases "
               "INCLUDING the nominal case that produces the headline "
               f"({_NOM_OVER_S:.1f} s, {_NOM_OVER_KWH:.3f} kWh), and on "
               "the governing climb corner the pack reaches SOC "
               f"{_CLIMB_SOC:.3f} with {_CLIMB_UNSERVED:.3f} kWh of "
               "unserved bus energy. WS4's own KX r3 states the same "
               "exposure more widely and more correctly than WS11's case "
               "set can: on the union of its ordered set and an R6 "
               "rating-family probe set the genset spends up to "
               f"{(R['ws4_esc10_exposure_as_read']['union_worst_over_rating_s'] or 0.0):.1f} s "
               "per cycle above its continuous flat-rating (against "
               f"{(R['ws4_esc10_exposure_as_read']['ordered_set_worst_over_rating_s'] or 0.0):.1f} s "
               "over the ordered set alone), with peak shaft at "
               f"{(R['ws4_esc10_exposure_as_read']['engine_shaft_peak_pct_of_continuous_rating_worst'] or 0.0):.2f}% "
               "of that case's OWN rating. That is the framing this "
               "escalation asks the lead to rule on; WS11's counters below "
               "are its own measurement on its own case set and are not "
               "offered as a substitute for it. The direction of every one "
               "of these "
               "is TOWARD the candidate, so none of them changes the KILL "
               "- but the exported V2 numbers are not achievable inside "
               "V2's own ratified rating, and a KILL executed on numbers "
               "that flatter the candidate is at least the safe direction "
               "for the decision while being the wrong basis for the "
               "record. WS4's `emerg_cap_cont_rating` bracket is exercised "
               "and exported (adjudication r1/M3)."),
         requested=("a ruling on which ceiling governs a Vehicle Zero "
                    "series candidate's emergency band - the automotive "
                    "full-load curve or the ratified continuous "
                    "flat-rating - taken together with WS4's KX-M1")),
]

# ---------------------- numbers the report's prose quotes (m1) ------------
# m1: round 1's opening sentence claimed verify_ws11.py asserts every number
# in the report; 105 numeric tokens were outside the assertion set, several
# of them substantive quantities with no JSON home at all. Everything the
# prose quotes now has a home here and therefore verifies verbatim.
log("prose-support numbers ...")
_ru_sub = [RU.run_ruler(CYC["VOLT-SUB"][s_], P.M_GVW_KG, veh=VEH,
                        engine=ENG_REF) for s_ in SUB_SEEDS]
_ru_reg = [RU.run_ruler(CYC["VOLT-REG"][s_], P.M_GVW_KG, veh=VEH,
                        engine=ENG_REF) for s_ in REG_SEEDS]
_RULER_IDLE = dict(
    idle_rpm=_ru_sub[0]["idle_rpm"],
    idle_fuel_g_per_s=_ru_sub[0]["idle_fuel_g_per_s"],
    idle_fuel_l_per_h=_ru_sub[0]["idle_fuel_l_per_h"],
    idle_time_frac_sub=float(np.median([o["idle_time_frac"]
                                        for o in _ru_sub])),
    idle_time_frac_reg=float(np.median([o["idle_time_frac"]
                                        for o in _ru_reg])),
    share_sub_pct=float(np.median([100.0 * o["idle_fuel_g"] / o["fuel_burn_g"]
                                   for o in _ru_sub])),
    share_reg_pct=float(np.median([100.0 * o["idle_fuel_g"] / o["fuel_burn_g"]
                                   for o in _ru_reg])),
)
_ws2j = json.load(open(UPSTREAM["WS2/results.json"]))
R["report_prose_support"] = dict(
    ruler_idle=_RULER_IDLE,
    idle_time_pct_VOLT_SUB=100.0 * _RULER_IDLE["idle_time_frac_sub"],
    idle_time_pct_VOLT_REG=100.0 * _RULER_IDLE["idle_time_frac_reg"],
    braking_pct_of_tractive_VOLT_SUB=float(np.median(
        [100.0 * o["brake_energy_frac_of_tractive"] for o in _ru_sub])),
    braking_pct_of_tractive_VOLT_REG=float(np.median(
        [100.0 * o["brake_energy_frac_of_tractive"] for o in _ru_reg])),
    ws1_v1_sustained_6pct_kmh=30.2,
    ws1_v1_sustained_6pct_source=("WS1 REPORT_WS1.md s4.4 forward "
                                  "simulation, V1 50 kW genset with a "
                                  "2.0 kWh buffer"),
    ws1_climb_posing_speed_kmh=85.0,
    ws1_climb_posing_statement=("WS1 s4.4: holding 85 km/h up a 10 km 6% "
                                "grade is not achievable on any buffer "
                                "this study contemplates"),
    ws2_spine_mass_kg=230.8,
    ws3_pack_mass_kg=280.52,
    ws4_v1_genset_mass_kg=386.0,
    ws4_v2_genset_total_dry_kg=637.0,
    ws4_aftertreatment_extra_kg=60.0,
    chassis_cab_allowance_lb_at_150in=P.ALLOWANCE_AT_WB_LB,
    v2_break_even_overshoot_kg=abs(
        BREAKEVEN["V2_on_VOLT-REG"]["headroom_kg_worst"]),
    r22d_spin_member_pp_of_cycle_fuel=0.0004,
    r22d_spin_member_source=("WS4 R22d true-coast operational note, "
                             "reported by WS4 and charged to fuel by "
                             "nobody"),
    note=("every quantity the report's prose quotes lives here or in one of "
          "the blocks above, so `verify_ws11.py` can assert it verbatim. "
          "The two upstream constants (WS1's 30.2 km/h, WS4's 0.0004 pp) "
          "are quotations of another workstream's published figure and are "
          "labelled as such, not re-derived here."))

# SWEEP (r2): the robustness shift must be a PAIRED per-seed difference.
_ROBUST_ROWS = {}
for _k, _v in BRK_MARGIN.items():
    _duty = _k.split("_on_")[1]
    _sd = SEEDS[_duty]
    _hlp = _v["headline_ruler_favourable"]["per_seed"]
    _pep = _v["all_ruler_modelling_choices_pessimistic"]["per_seed"]
    _d = [_pep[str(x)] - _hlp[str(x)] for x in _sd]
    _e = envelope(_d, _sd, _duty)
    _ROBUST_ROWS[_k] = dict(
        headline_min=_v["headline_ruler_favourable"]["min"],
        pessimistic_min=_v["all_ruler_modelling_choices_pessimistic"]["min"],
        pessimistic_median=_v["all_ruler_modelling_choices_pessimistic"][
            "median"],
        pessimistic_min_governing_case=_v[
            "all_ruler_modelling_choices_pessimistic"]["min_governing_case"],
        shift_pp=_e["min"],
        shift_pp_paired_min=_e["min"],
        shift_pp_paired_median=_e["median"],
        shift_pp_paired_max=_e["max"],
        shift_pp_paired_min_governing_case=_e["min_governing_case"],
        shift_pp_unpaired_statistic_of_statistics=(
            _v["all_ruler_modelling_choices_pessimistic"]["min"]
            - _v["headline_ruler_favourable"]["min"]),
        shift_pp_statistic=("PAIRED: differenced seed by seed, then "
                            "enveloped (R36/D13)"))

# ------------------------------------------------- construction sweep (r2)
# The rework order requires a sweep beyond the named findings, in three
# directions, and requires the CLEAN areas to be reported as well as the
# dirty ones. This block is that record. It is auditable so the clean areas
# do not have to be re-swept.
R["construction_sweep_r2"] = dict(
    _purpose=("sweep for (a) machine-readable fields whose CONSTRUCTION "
              "does not match their NAME, (b) claims of robustness or "
              "boundedness anywhere in the report that were asserted "
              "rather than run, and (c) statistics-of-statistics standing "
              "in for paired ones. The program's stated repeat failure "
              "mode is the partial correction."),
    _rulings="BASELINE_v5 R36; R14; R9",
    a_name_vs_construction=dict(
        found_by_the_adjudication=[
            dict(field="ruler_calibration.brackets."
                       "all_ruler_favourable_choices_reversed",
                 finding="B1",
                 was="reversed five choices, left the four largest ruler "
                     "levers untouched, and folded in a road-load change",
                 now="renamed `r1_partial_reversal_plus_CdA_5.4_road_"
                     "change` and superseded by "
                     "`all_ruler_modelling_choices_pessimistic`; every "
                     "bracket row carries an explicit `kind`"),
            dict(field="trip_time_r38.*.settled_speed_on_6pct_kmh",
                 finding="B2",
                 was="the MINIMUM demanded speed on any sample of >=5.5% "
                     "grade anywhere in the cycle, reported as a settled "
                     "speed, on cases with no sustained climb at all",
                 now="the speed the vehicle has settled at leaving the "
                     "longest continuous >=5.5% run, only where that run "
                     "lasts >=120 s; round 1's quantity retained under "
                     "`min_speed_on_grade_ge_5p5pct_kmh`"),
            dict(field="ruler_bracket_effect_on_margin.note",
                 finding="M4",
                 was="asserted that every non-headline row raises the "
                     "candidate's margin; false for CdA_5.4 on both "
                     "vehicles",
                 now="note rewritten by `kind`, and verify_ws11.py checks "
                     "the DIRECTION of every row against its kind instead "
                     "of trusting the note"),
            dict(field="interface_ws11.ruler.anchor.residual_vs_model_pct",
                 finding="M5",
                 was="the milder of two anchor members, exported as if it "
                     "were the anchor",
                 now="R14 enumerated two-member set with the worst "
                     "residual and its governing member"),
            dict(field="one_factor.*.worth_pp", finding="M6a",
                 was="min-of-base minus min-of-counterfactual, governed by "
                     "different seeds",
                 now="paired per-seed difference, then enveloped"),
            dict(field="one_factor.engine_operating_point.description",
                 finding="M6b",
                 was="said idle SURVIVES the row; idle is absorbed into it",
                 now="description corrected and the idle share exported"),
            dict(field="mass_ledger.ruler_build[0] tag `[SOURCED]`",
                 finding="m10",
                 was="tagged SOURCED; it is an interpolation of a "
                     "published range",
                 now="retagged [SOURCED-RANGE, INTERPOLATED IN WHEELBASE]"),
            dict(field="heat_ledger_ws6 `R15 blend overflow "
                       "(resistor + friction)`",
                 finding="m7",
                 was="offered to WS6, which owns the resistor separately, "
                     "as one column",
                 now="renamed LUMPED, bounded above by itself and below by "
                     "`regen_shed_r16_kWh`, with the reason WS11 cannot "
                     "split it stated"),
        ],
        found_by_this_sweep=[
            dict(field="ws11_capability._loop.capability_limited_s",
                 was="counted only samples where the vehicle was trying to "
                     "ACCELERATE and could not, while the name says "
                     "capability-limited. On a sustained grade the "
                     "counter read zero while the vehicle was capability "
                     "limited on every sample.",
                 now="counts every sample where a_cap < a_des; fixed by "
                     "the same change as B2 but the NAME defect is "
                     "separate from B2's physics defect and is recorded "
                     "separately"),
            dict(field="ws11_ruler.run_ruler.eng_reject_kwh",
                 was="fuel_energy_kwh - shaft, where fuel_energy_kwh "
                     "carries the unserved-wheel-energy FUEL CORRECTION - "
                     "heat from fuel the engine never burned, for work it "
                     "never did. WS4's candidate-side eng_reject_kwh is "
                     "accumulated per sample from the real burn, so the "
                     "ruler's and the candidate's WS6 ledger rows were "
                     "not on one basis.",
                 now="integrated per sample from the actual burn; round "
                     "1's quantity retained as "
                     "`eng_reject_kwh_incl_unserved_correction_r1_basis` "
                     "with the correction itself exported"),
            dict(field="heat_ledger_ws6.mean_kW_over_cycle_max",
                 was="max(energy over seeds) / median(duration over "
                     "seeds) - a max divided by a statistic of a "
                     "different seed",
                 now="per-seed mean kW, then max; round 1's basis retained "
                     "as `mean_kW_over_cycle_max_r1_basis`"),
            dict(field="sanity_checks.per_km_vs_per_payload_identity."
                       "checked",
                 was="a hard-coded True sitting beside a computed residual "
                     "- a claim the run did not make",
                 now="derived from the measured residual, with the number "
                     "of seed-cases checked exported"),
            dict(field="cold_cab_heat_bracket.*_no_waste_heat_credit_"
                       "upper_bound (introduced in this round's own first "
                       "draft)",
                 was="a bound attached to a MARGIN field whose name "
                     "promised an upper bound on the margin while the "
                     "construction is an upper bound on the PENALTY, i.e. "
                     "a LOWER bound on the margin - the same class WS4's "
                     "KX r3 sweep found in its own workstream",
                 now="renamed `..._no_waste_heat_credit_worst` with the "
                     "direction stated in its own field"),
            dict(field="ws11_ruler.ruler_available_wheel_kw",
                 was="a second, never-called statement of the capability "
                     "physics that could drift from "
                     "`ws11_capability.ruler_force_table`, the model of "
                     "record",
                 now="deleted"),
        ],
        checked_and_CLEAN=[
            "break_even_curb_kg / break_even_payload_kg - exact per-seed "
            "algebra, min labelled, name matches construction",
            "margin_pct_per_km_paired and margin_pct_per_payload_tkm_"
            "paired on every block - genuinely paired, verified "
            "independently at [4]",
            "trip_time_r38.ratio_worst and pct_worse_than_ruler_worst - "
            "max over per-seed ratios, not a ratio of maxima",
            "sustained_6pct_capability.*_kmh - genset-only by "
            "construction; the reduced-order chain tabulation point is "
            "now declared in the reconciliation tolerance basis",
            "interface_ws11.sustained_6pct_capability_kmh.worst_case_"
            "value - min over the enumerated vehicle set with governing "
            "case",
            "mass_ledger.break_even_per_km_advantage_pct - recomputed "
            "independently at [5]",
            "envelope() governing-case strings - name the seed and the "
            "enumerated set they are extrema over",
            "ws4_regression.max_abs_difference - identical floats, "
            "re-checked against WS4's file at [2]",
            "payload_corner_variant_margin_pct_min - the variant reading, "
            "labelled as such and excluded from the gate",
            "min_speed_above_30kmh_demand_kmh / max_speed_deficit_kmh - "
            "name matches construction",
            "heat ledger case coverage - every vehicle x duty x case, and "
            "the ruler rows are now emitted once rather than once per "
            "candidate pass",
        ]),
    b_claims_asserted_not_run=dict(
        found=[
            dict(claim="s1.3: 'V2's KILL does not turn on how the ruler "
                       "was modelled'", finding="B1",
                 status="FALSIFIED and withdrawn; restated against the "
                        "all-eight-levers row, which is a draw"),
            dict(claim="s1.1: 'Both effects are inside the brackets in "
                       "s1.3' (the engine curve)", finding="m3",
                 status="was true but unrun; two declared engine-curve "
                        "reconstructions are run and exported"),
            dict(claim="s6: 'V2 passes the 10 km climb because its buffer "
                       "lasts almost exactly 10 km'", finding="B2/M3",
                 status="WITHDRAWN. The trip-time pass never exercised "
                        "the buffer, and on the fuel side the pack is "
                        "exhausted with unserved energy"),
            dict(claim="s10.1: the missing cold-engine friction model is "
                       "'roughly neutral'", finding="M8",
                 status="reclassified; it flatters the candidate, and "
                        "specifically V1. ESC-8 opened"),
            dict(claim="s1.2: 'every candidate margin in this report is a "
                       "lower bound'",
                 finding="FOUND BY THIS SWEEP",
                 status="unqualified, and not true of the CdA road-load "
                        "row (which lowers both candidates' margins) nor "
                        "of ESC-3's aftertreatment reading. Now stated as "
                        "a lower bound with respect to RULER-MODELLING "
                        "choices only, which is what the evidence "
                        "supports"),
            dict(claim="s9: 'Nine of WS11's input pins are files WS4 also "
                       "pins ... Every one matches'",
                 finding="FOUND BY THIS SWEEP",
                 status="the count was typed into prose while three more "
                        "source pins were added this round. It is derived "
                        "from the run now"),
            dict(claim="the opening sentence, 'verify_ws11.py asserts "
                       "every number in this file'", finding="m1",
                 status="narrowed to what is true, and the substantive "
                        "quantities that had no JSON home were given one"),
        ],
        checked_and_CLEAN=[
            "s1.2 'A fit was not used' - independently confirmed by the "
            "adjudication; every free parameter is declared with a "
            "direction of error and none was moved to the corridor",
            "s5 'Neither verdict changes under either payload-corner "
            "reading' - both readings are run and exported",
            "s2 mass ledgers 'to the kilogram, with sources' - "
            "independently re-derived by the adjudication, arithmetic "
            "closes",
            "s10 'reproduced here from a completely different code path' "
            "(V1's 6% capability against WS1's) - true, and both figures "
            "are exported",
            "s2.3 'more than its whole pack again' - V1's headroom "
            "exceeds the pack mass",
            "the R38 gate outcome - PASS on all three rows before and "
            "after the B2 correction",
        ]),
    c_statistic_of_statistics=dict(
        found=[
            "one_factor.*.worth_pp and .cost_pp (M6) - now paired",
            "declared_choice_brackets.emergency_band_at_continuous_"
            "rating_bracket.*.shift_pp - FOUND BY THIS SWEEP in this "
            "round's own new code; now paired",
            "declared_choice_brackets.derated_load_fraction_convention."
            "*.shift_pp - FOUND BY THIS SWEEP; now paired",
            "declared_choice_brackets.ruler_engine_curve."
            "worst_margin_shift_pp - FOUND BY THIS SWEEP; now the largest "
            "absolute PER-SEED difference",
            "interface_ws11.verdict_robustness.*.shift_pp - FOUND BY THIS "
            "SWEEP; now paired",
            "v2_aftertreatment_bracket_effect.*.shift_pp and "
            "ruler_chassis_cab_cross_check.*.shift_pp - FOUND BY THIS "
            "SWEEP; exact algebra on the same per-seed values, so the "
            "artefact is zero, but they are formed per seed anyway so no "
            "row in this file is a statistic of statistics",
            "heat_ledger_ws6.mean_kW_over_cycle_max - FOUND BY THIS "
            "SWEEP; max energy over median duration",
        ],
        checked_and_CLEAN=[
            "every headline margin and every corner margin - the "
            "adjudication re-derived all 128 seed-cases and found no "
            "ratio-of-medians artefact",
            "ruler_bracket_effect_on_margin rows - formed per seed, then "
            "enveloped",
            "cold_cab_heat_bracket and cold_corner_both_pending_items - "
            "formed per seed",
            "break_even_curb - formed per seed",
            "ruler_fuel_flip_points - formed per seed by construction",
            "trip_time_r38 ratios - formed per seed",
            "ruler_calibration.corridor_check residuals - a median ruler "
            "level against a scalar anchor; there is no pairing to do and "
            "the fields name the median",
        ]),
    _reading=("The sweep found six further name/construction defects, two "
              "further unrun claims and seven further statistic-of-"
              "statistics constructions beyond the twenty-four findings "
              "the adjudication named. Four of them were in code written "
              "for THIS round, which is the point of sweeping after "
              "fixing rather than before. None of them moves a verdict."))

# ------------------------------------------------------- R14 interface block
log("interface block ...")


def _v(vehicle, duty, case, metric="margin_pct_per_payload_tkm_paired"):
    return RESULTS[f"{vehicle}_on_{duty}"][case][metric]


# R14: "Fields conditioned on a pending ruling carry the ruling ID."
# Round 1's interface block contained the string "ESC" nowhere at all
# (adjudication r1/M2). Every field below that a live ruling can move now
# names the ruling, and the alternative reading is reachable FROM the
# interface rather than only from the results file.
PENDING = dict(
    _rule=("R14: fields conditioned on a pending ruling carry the ruling "
           "ID. A consumer reading only this interface block must be able "
           "to see which numbers are conditional and on what."),
    ESC_1=dict(
        ruling_sought="may an UNCALIBRATED ruler carry a KILL?",
        conditions=["ruler.l_per_100km_VOLT_SUB", "ruler.l_per_100km_VOLT_REG",
                    "ruler.anchor", "verdicts.*", "every margin in this "
                    "block"],
        priced_by="ruler_fuel_flip_points"),
    ESC_2=dict(
        ruling_sought="does R30's cab-heat member extend to Vehicle Zero?",
        conditions=["verdicts.V1_on_VOLT-SUB.worst_corner_margin_pct",
                    "verdicts.V2_on_VOLT-REG.corner_margins_pct_min."
                    "cold_-10C"],
        priced_by="cold_cab_heat_bracket / cold_corner_both_pending_items"),
    ESC_3=dict(
        ruling_sought="is WS4's `aftertreatment_extra` 60 kg incremental to "
                      "a stock 4HK1 installation?",
        conditions=["masses.curb_kg.V2", "masses.payload_at_gvw_kg.V2",
                    "every V2 margin"],
        priced_by="v2_aftertreatment_bracket_effect"),
    ESC_4=dict(
        ruling_sought="CdA 4.2 (provisional) or 5.4 (E13) pending the WS7 "
                      "coastdown?",
        conditions=["every margin in this block"],
        priced_by="ruler_bracket_effect_on_margin.rows.*.CdA_5.4 / "
                  "cold_corner_both_pending_items"),
    ESC_5=dict(
        ruling_sought="does a sustained-gradeability floor join the Vehicle "
                      "Zero criteria?",
        conditions=["sustained_6pct_capability_kmh", "trip_time_r38"],
        priced_by="sustained_6pct_capability"),
    ESC_7=dict(
        ruling_sought="which payload-corner convention governs?",
        conditions=["verdicts.*.corner_margins_pct_min.payload_p20",
                    "verdicts.*.corner_margins_pct_min.payload_m20"],
        priced_by="payload_corner_variant_margin_pct_min"),
    ESC_9=dict(
        ruling_sought="which ceiling governs the emergency band - the "
                      "automotive full-load curve or the ratified 132 kW "
                      "continuous flat-rating?",
        conditions=["every V2 margin"],
        priced_by="declared_choice_brackets."
                  "emergency_band_at_continuous_rating_bracket"),
)

INTERFACE = dict(
    _basis=("mirrors WS1/WS4 results.json conventions; extrema are 8-seed "
            "ensemble envelopes (R9); every worst-case field is an explicit "
            "max/min over an enumerated case set with the governing case "
            "labelled inline (R14); electrical quantities bus-side (R12); "
            "the metric of record is fuel energy per PAYLOAD tonne-km on the "
            "PAIRED per-seed statistic (R36/D13)"),
    _status="ruler_trial_result_pending_adjudication_and_ratification",
    _round="r2 (rework against FINDINGS_WS11_r1.md)",
    question_of_record=("is the ratified Vehicle Zero design more efficient "
                        "than the truck it replaces, on the honest metric?"),
    pending_rulings_r14=PENDING,
    ruler=dict(
        identity="stock Isuzu NPR-HD, 4HK1-TC + Aisin A465id 6-speed "
                 "torque-converter automatic (lock-up 2nd-6th) + 4.555 axle",
        engine_map="WS4 4HK1-TC-ref-W Willans map, "
                   f"{WS4J['bsfc_maps']['4HK1-TC-ref-W']['map_min']['bsfc']:.3f}"
                   " g/kWh island",
        sourced_specification_url=P.RULER_SOURCED["url"],
        conditioned_on_rulings=["ESC-1 (pending)", "ESC-4 (pending)"],
        anchor=dict(
            name=P.RULER_FUEL_ANCHOR["name"],
            url=P.RULER_FUEL_ANCHOR["url"],
            enumerated_member_set=["all_model_years", "fourhk1_era"],
            all_model_years=dict(
                mpg=_A_ALL["mpg"], l_per_100km=_A_ALL["l_per_100km"],
                miles=_A_ALL["miles"], fuel_ups=_A_ALL["fuel_ups"],
                residual_vs_model_pct=_A_ALL[
                    "residual_vs_model_headline_pct"]),
            fourhk1_era=dict(
                mpg=_A_ERA["mpg"], l_per_100km=_A_ERA["l_per_100km"],
                miles=_A_ERA["miles"], fuel_ups=_A_ERA["fuel_ups"],
                residual_vs_model_pct=_A_ERA[
                    "residual_vs_model_headline_pct"]),
            worst_residual_vs_model_pct=CAL["anchor_set_r14"][
                "worst_residual_vs_model_headline_pct"],
            worst_residual_governing_case=(
                CAL["anchor_set_r14"]["worst_residual_governing_member"]
                + " (min over the enumerated two-member anchor set)"),
            era_note_direction=CAL["anchor_set_r14"]["era_note_direction"],
            vehicles_on_page=21,
            is_a_fit=False,
            calibrate_order_satisfied=False,
            calibrate_order_statement=CAL["corridor_check"][
                "calibrate_order_statement"],
            # round 1 exported only the all-years residual under this key
            residual_vs_model_pct=CAL["corridor_check"]
            ["residual_vs_anchor_pct_headline"]),
        curb_kg=CURB["ruler"], payload_at_gvw_kg=PAY["ruler"],
        l_per_100km_VOLT_SUB=_hl["VOLT-SUB"]["l_per_100km"],
        l_per_100km_VOLT_REG=_hl["VOLT-REG"]["l_per_100km"],
        l_per_100km_bracket_range=dict(
            rule=("explicit min/max over the enumerated ruler-MODELLING "
                  "bracket set, governing bracket labelled (R14). The "
                  "headline setting is the ruler-FAVOURABLE end of that "
                  "range on both duties, which is why it is also the "
                  "minimum."),
            VOLT_SUB=dict(
                headline=_hl["VOLT-SUB"]["l_per_100km"]["median"],
                pessimistic=_pess["VOLT-SUB"]["l_per_100km"]["median"],
                governing_bracket_for_pessimistic=(
                    "all_ruler_modelling_choices_pessimistic (max over the "
                    "enumerated ruler-modelling bracket set)")),
            VOLT_REG=dict(
                headline=_hl["VOLT-REG"]["l_per_100km"]["median"],
                pessimistic=_pess["VOLT-REG"]["l_per_100km"]["median"],
                governing_bracket_for_pessimistic=(
                    "all_ruler_modelling_choices_pessimistic (max over the "
                    "enumerated ruler-modelling bracket set)"))),
        declared_choices_are_ruler_favourable=True),
    masses=dict(gvw_kg=P.M_GVW_KG,
                curb_kg={k: CURB[k] for k in CURB},
                payload_at_gvw_kg={k: PAY[k] for k in PAY},
                conditioned_on_rulings=["ESC-3 (pending): the V2 rows move "
                                        "by 60 kg on the other reading"]),
    verdicts=VERDICTS,
    verdict_robustness=dict(
        rule=("the verdict recomputed with EVERY ruler-modelling choice at "
              "the pessimistic end its own declaration names, no road-load "
              "change. This is the row the robustness claim is stated "
              "against; round 1 stated it against a partial reversal that "
              "left the four largest levers untouched (adjudication "
              "r1/B1)."),
        bracket="all_ruler_modelling_choices_pessimistic",
        rows=_ROBUST_ROWS,
        conditioned_on_rulings=["ESC-1 (pending)"]),
    ruler_fuel_flip_points={
        k: v["_verdict_reading"] for k, v in FLIP.items()
        if "_verdict_reading" in v},
    trip_time_r38={k: dict(
        ratio_worst=v["ratio_worst"],
        ratio_worst_governing_case=v["ratio_worst_governing_case"],
        pct_worse_than_ruler_worst=v["pct_worse_than_ruler_worst"],
        gate_met=v["r38_gate_met"],
        ruler_trip_time_s_median=v["ruler_trip_time_s"]["median"],
        candidate_trip_time_s_median=v["candidate_trip_time_s"]["median"],
        settled_speed_on_sustained_climb_kmh_ruler=(
            v["ruler_settled_speed_on_6pct_kmh"]["median"]
            if v["ruler_settled_speed_on_6pct_kmh"] else None),
        settled_speed_on_sustained_climb_kmh_candidate=(
            v["candidate_settled_speed_on_6pct_kmh"]["median"]
            if v["candidate_settled_speed_on_6pct_kmh"] else None))
        for k, v in TRIP.items()},
    sustained_6pct_capability_kmh=dict(
        rule="steady speed on a 6% grade at GVW with NO buffer contribution",
        ruler=SUSTAINED["ruler_kmh"], V1=SUSTAINED["V1_kmh"],
        V2=SUSTAINED["V2_kmh"],
        worst_case_value=min(SUSTAINED["ruler_kmh"], SUSTAINED["V1_kmh"],
                             SUSTAINED["V2_kmh"]),
        governing_case=min(
            (("ruler", SUSTAINED["ruler_kmh"]), ("V1", SUSTAINED["V1_kmh"]),
             ("V2", SUSTAINED["V2_kmh"])), key=lambda x: x[1])[0],
        forward_pass_agreement_kmh_worst=max(
            [max(r["ruler_abs_difference_kmh"],
                 r["candidate_abs_difference_kmh"])
             for r in RECON["rows"].values()] or [0.0]),
        conditioned_on_rulings=["ESC-5 (pending)"]),
    break_even_curb_kg={k: dict(
        worst=v["break_even_curb_kg"]["min"],
        worst_governing_case=v["break_even_curb_kg"]["min_governing_case"],
        median=v["break_even_curb_kg"]["median"],
        actual=v["actual_curb_kg"],
        headroom_kg_worst=v["headroom_kg_worst"])
        for k, v in BREAKEVEN.items()},
    capability_and_limit_worst_case={
        k: dict(
            candidate_worst_unserved_bus_kWh=max(
                c["candidate"]["unserved_bus_kWh"]["worst"]
                for c in v.values()),
            candidate_worst_unserved_governing_case=max(
                v.items(),
                key=lambda kv: kv[1]["candidate"]["unserved_bus_kWh"][
                    "worst"])[0] + " (max over the enumerated case set)",
            candidate_worst_soc_min=min(
                c["candidate"]["soc_min"]["worst"] for c in v.values()),
            candidate_worst_soc_min_governing_case=min(
                v.items(),
                key=lambda kv: kv[1]["candidate"]["soc_min"]["worst"])[0]
            + " (min over the enumerated case set)",
            candidate_cases_above_continuous_rating=sum(
                1 for c in v.values()
                if c["candidate"]["s_above_continuous_rating"]["worst"] > 0),
            candidate_cases_total=len(v),
            candidate_continuous_rating_kW=list(
                v.values())[0]["candidate"]["continuous_rating_kW_derated"],
            candidate_emergency_ceiling_kW=list(
                v.values())[0]["candidate"]["emergency_band_ceiling_kW"],
            ruler_worst_capability_infeasible_s=max(
                c["ruler"]["capability_infeasible_s"]["worst"]
                for c in v.values()),
            ruler_worst_unserved_wheel_kWh=max(
                c["ruler"]["unserved_wheel_kWh"]["worst"]
                for c in v.values()),
            conditioned_on_rulings=["ESC-9 (pending)"])
        for k, v in LIMITS.items()},
    cold_corner_pending_items={
        k: dict(
            ordered_gate_value_pct=v["margin_ordered_corner"],
            with_cab_heat_pct=COLDB[k][
                "margin_pct_per_payload_tkm_paired"]["min"],
            with_cab_heat_and_CdA_5p4_pct=v[
                "margin_pct_per_payload_tkm_paired"]["min"],
            with_cab_heat_and_CdA_5p4_median_pct=v[
                "margin_pct_per_payload_tkm_paired"]["median"],
            conditioned_on_rulings=["ESC-2 (pending)", "ESC-4 (pending)"])
        for k, v in COLD_BOTH.items()},
    payload_corner_variant_margin_pct_min={
        k: {c: b["margin_pct_per_payload_tkm_paired"]["min"]
            for c, b in v.items()} for k, v in VARIANT.items()},
    ruler_idle=dict(
        rpm=_RULER_IDLE["idle_rpm"],
        fuel_g_per_s=_RULER_IDLE["idle_fuel_g_per_s"],
        fuel_l_per_h=_RULER_IDLE["idle_fuel_l_per_h"],
        share_of_VOLT_SUB_fuel_pct=_RULER_IDLE["share_sub_pct"],
        share_of_VOLT_REG_fuel_pct=_RULER_IDLE["share_reg_pct"],
        time_fraction_VOLT_SUB=_RULER_IDLE["idle_time_frac_sub"],
        note=("the ruler's single most consequential number on a stop-start "
              "duty; round 1 never stated it (adjudication r1/m5)")),
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
        # `checked` is set from the measured residual below, not asserted
        # as a literal (SWEEP r2: a hard-coded True beside a computed
        # residual is a claim the run does not make).
        checked=None),
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
SANITY["per_km_vs_per_payload_identity"]["checked"] = bool(_worst_id < 1e-12)
SANITY["per_km_vs_per_payload_identity"]["seed_cases_checked"] = sum(
    len(b["margin_pct_per_km_paired"]["per_seed"])
    for bl in RESULTS.values() for b in bl.values())
assert _worst_id < 1e-12, "per-km / per-payload identity broken"
# SWEEP (r2): the count of pins shared with WS4 was typed into the report's
# prose. Derived from the run now.
_theirs = SD2["input_sha256"]
_shared = sorted(set(INPUT_SHA) & set(_theirs))
SANITY["upstream_pin_crosscheck"] = dict(
    rule=("pins WS11 read that WS4 also declares inside "
          "series_duty_v2.input_sha256; every one must match, which means "
          "the two workstreams consumed byte-identical files, not merely "
          "files with the same name"),
    shared_pin_count=len(_shared),
    shared_pins=_shared,
    all_match=all(INPUT_SHA[k] == _theirs[k] for k in _shared),
    ws11_total_pin_count=len(INPUT_SHA))
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
        unp = d.get("cost_pp_unpaired_r1_statistic_of_statistics",
                    d.get("worth_pp_unpaired_r1_statistic_of_statistics"))
        med = d.get("cost_pp_paired_median", d.get("worth_pp_paired_median"))
        rows.append([key, factor, f"{val:+.4f}", f"{med:+.4f}",
                     f"{unp:+.4f}", f"{unp - val:+.4f}",
                     d["description"][:180]])
write_csv("one_factor.csv",
          ["run", "factor", "pp_paired_min", "pp_paired_median",
           "pp_unpaired_r1", "unpaired_artefact_pp", "description"], rows)

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

def _o(x, spec=".4f"):
    return "" if x is None else format(x, spec)


rows = [[r["vehicle"], r["duty"], r["case"], r["component"],
         f"{r['heat_kWh_per_cycle_min']:.4f}",
         f"{r['heat_kWh_per_cycle_median']:.4f}",
         f"{r['heat_kWh_per_cycle_max']:.4f}",
         f"{r['mean_kW_over_cycle_max']:.4f}",
         _o(r.get("peak_kW")), _o(r.get("roll120s_mean_kW_max")),
         _o(r.get("roll600s_mean_kW_max")),
         _o(r.get("split_exhaust_kWh_median")),
         _o(r.get("split_coolant_oil_kWh_median")),
         _o(r.get("split_charge_air_cooler_kWh_median")),
         _o(r.get("resistor_share_lower_bound_kWh_median")),
         r["max_governing_case"]]
        for r in LEDGER_ROWS]
write_csv("heat_ledger_ws6.csv",
          ["vehicle", "duty", "case", "component", "kWh_min", "kWh_median",
           "kWh_max", "mean_kW_max", "peak_kW", "roll120s_mean_kW_max",
           "roll600s_mean_kW_max", "split_exhaust_kWh_median",
           "split_coolant_oil_kWh_median", "split_cac_kWh_median",
           "resistor_share_lower_bound_kWh_median",
           "max_governing_case"], rows)

# capability / limit counters per case (M3)
rows = []
for key, per_case in LIMITS.items():
    for case, d in per_case.items():
        c, r_ = d["candidate"], d["ruler"]
        rows.append([
            key, case,
            f"{c['unserved_bus_kWh']['worst']:.4f}",
            f"{c['soc_min']['worst']:.4f}",
            f"{c['emergency_band_s']['worst']:.1f}",
            f"{c['s_above_continuous_rating']['worst']:.1f}",
            f"{c['kWh_above_continuous_rating']['worst']:.4f}",
            f"{c['engine_shaft_peak_kW']['worst']:.2f}",
            f"{c['continuous_rating_kW_derated']:.2f}",
            f"{c['emergency_band_ceiling_kW']:.2f}",
            f"{c['genset_starts']['worst']:.0f}",
            f"{r_['unserved_wheel_kWh']['worst']:.4f}",
            f"{r_['capability_infeasible_s']['worst']:.1f}",
            f"{r_['idle_fuel_g']['worst']:.1f}",
            c["unserved_bus_kWh"]["worst_governing_case"]])
write_csv("limit_counters.csv",
          ["run", "case", "cand_unserved_bus_kWh_worst",
           "cand_soc_min_worst", "cand_emergency_band_s_worst",
           "cand_s_above_cont_rating_worst",
           "cand_kWh_above_cont_rating_worst",
           "cand_eng_shaft_peak_kW_worst", "cand_cont_rating_kW",
           "cand_emerg_ceiling_kW", "cand_genset_starts_worst",
           "ruler_unserved_wheel_kWh_worst", "ruler_infeasible_s_worst",
           "ruler_idle_fuel_g_worst", "governing_case"], rows)

# ruler-fuel flip points (B3)
rows = []
for key, per_case in FLIP.items():
    for case, d in per_case.items():
        if case.startswith("_"):
            continue
        for tgt, v in d.items():
            rows.append([
                key, case, f"{v['target_margin_pct']:.1f}",
                f"{v['multiplier_min']:.6f}", f"{v['multiplier_median']:.6f}",
                f"{v['multiplier_max']:.6f}",
                f"{v['least_ruler_fuel_error_multiplier']:.6f}",
                f"{v['least_ruler_fuel_error_pct']:+.4f}",
                f"{v['implied_ruler_l_per_100km_min']:.4f}",
                f"{v['implied_ruler_l_per_100km_max']:.4f}",
                v["least_ruler_fuel_error_governing_case"]])
write_csv("ruler_fuel_flip_points.csv",
          ["run", "case", "target_margin_pct", "multiplier_min",
           "multiplier_median", "multiplier_max",
           "least_error_multiplier", "least_error_pct",
           "implied_ruler_l_per_100km_min", "implied_ruler_l_per_100km_max",
           "governing_case"], rows)

rows = []
for name, per_duty in CAL["brackets"].items():
    for duty in ("VOLT-SUB", "VOLT-REG"):
        d = per_duty[duty]
        rows.append([name, per_duty["kind"], duty,
                     f"{d['l_per_100km']['min']:.4f}",
                     f"{d['l_per_100km']['median']:.4f}",
                     f"{d['l_per_100km']['max']:.4f}"])
write_csv("ruler_brackets.csv",
          ["bracket", "kind", "duty", "l_per_100km_min",
           "l_per_100km_median", "l_per_100km_max"], rows)

rows = []
for key, r_ in BRK_MARGIN.items():
    for name, e in r_.items():
        rows.append([key, name, e["kind"], f"{e['min']:+.4f}",
                     f"{e['median']:+.4f}", f"{e['max']:+.4f}"])
write_csv("bracket_margins.csv",
          ["run", "bracket", "kind", "margin_per_payload_min_pct",
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
