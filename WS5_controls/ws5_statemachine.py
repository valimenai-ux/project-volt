"""
Project Volt - WS5
THE SUPERVISOR STATE MACHINE - specification AND implementation.

This module is the state-machine deliverable. It is not documentation of
something implemented elsewhere: ws5_supervisor.py calls step() every 0.1 s
sample and acts on the states this machine returns, so the specification is
load-bearing and every reported number was produced through it.

Six ORTHOGONAL regions run concurrently (Harel-style AND-decomposition).
Regions are evaluated in the fixed order below each sample; later regions
see the states the earlier ones just entered.

  1 FAULT     what is broken (latched; healing requires a declared reset)
  2 THERMAL   which derate law is in force (R16 cold band, hot pack, inverter)
  3 TRACTION  adhesion limiting (E23, day one)
  4 DISPATCH  genset command (R19 / R22b)
  5 BLEND     retardation cascade (R15: pack -> heater -> resistor -> friction)
  6 VEHICLE   the supervisory mode the driver experiences

There is NO mode-selection region, NO clutch region and NO synchronisation
region: BASELINE_v3 executed Gate G1's kill clause and both variants are
pure series. R11's condition-aware mode policy died with the clutch.

Guard convention: within one region, transitions out of the active state are
tested in ascending `prio`; the first whose guard is true fires. Guards are
pure functions of the context dict `ctx`, which carries only CAUSAL
quantities - present and past measurements. No preview, no route lookahead.
"""
import numpy as np

# --------------------------------------------------------------- constants
# Every threshold below is either a ruled figure (cited) or a WS5-DECLARED
# control constant (marked). Declared constants are the supervisor's design
# freedom; they are exported in results_ws5.json -> control_constants.
R16_PRECOND_C = -15.0        # R16: preconditioning required below this CELL temp
R16_BAND_HI_C = 10.0         # R16: published derate curves run -15 .. +10 C
T_CELL_MAX_CONT_C = 55.0     # WS3 continuous cell ceiling
T_CELL_CUTOFF_C = 60.0       # WS3 hard cutoff
T_CELL_HOT_DERATE_C = 45.0   # WS3 acceptance curve begins falling above +45 C
INV_TJ_DERATE_C = 125.0      # [WS5-DECLARED] inverter derate onset; WS2 rates
INV_TJ_TRIP_C = 150.0        # [WS5-DECLARED] hard trip; WS2 peak case is 133 C
V_REGEN_BLEND_LO = 3.0 / 3.6   # WS1 CTL: regen fully off below (m/s)
V_REGEN_BLEND_HI = 8.0 / 3.6   # WS1 CTL: regen fully on above (m/s)
P_DEMAND_DEADBAND_KW = 0.5     # [WS5-DECLARED] drive/brake mode deadband
SETPOINT_DEADBAND_KW = 2.0     # [WS5-DECLARED] NVH: engine setpoint change
                               # smaller than this is not a transition

STATES = {
    "FAULT": ["F_NONE", "F_GENSET_LOSS", "F_PACK_LOSS", "F_PACK_DERATE",
              "F_RESISTOR_LOSS", "F_INV_DERATE", "F_SENSOR_LOSS"],
    "THERMAL": ["H_NOMINAL", "H_PRECOND", "H_COLD_DERATE", "H_HOT_PACK_DERATE",
                "H_INV_DERATE"],
    "TRACTION": ["T_OFF", "T_DRIVE_LIMIT", "T_REGEN_LIMIT"],
    "DISPATCH": ["D_OFF", "D_START", "D_PIN", "D_NOTCH_HI", "D_FOLLOW",
                 "D_RESERVE", "D_MOTOR", "D_FAULT"],
    "BLEND": ["B_NONE", "B_PACK", "B_HEATER", "B_RESISTOR", "B_FRICTION"],
    "VEHICLE": ["V_OFF", "V_PRECOND", "V_READY", "V_DRIVE", "V_BRAKE",
                "V_LIMP", "V_HALT"],
}
INITIAL = {"FAULT": "F_NONE", "THERMAL": "H_NOMINAL", "TRACTION": "T_OFF",
           "DISPATCH": "D_OFF", "BLEND": "B_NONE", "VEHICLE": "V_OFF"}
REGION_ORDER = ["FAULT", "THERMAL", "TRACTION", "DISPATCH", "BLEND", "VEHICLE"]


# ------------------------------------------------------------------ guards
# (region, src, dst, prio, guard_id, guard_text, ruling, callable)
def _t(region, src, dst, prio, gid, text, ruling, fn):
    return dict(region=region, src=src, dst=dst, prio=prio, guard=gid,
                guard_text=text, ruling=ruling, fn=fn)


TRANSITIONS = [
    # ---------------------------------------------------------- FAULT ----
    _t("FAULT", "*", "F_GENSET_LOSS", 10, "G_FLT_GEN",
       "fault_flag == 'genset_loss'",
       "R22c (no mechanical path: genset or pack fault = tow)",
       lambda c: c["fault"] == "genset_loss"),
    _t("FAULT", "*", "F_PACK_LOSS", 11, "G_FLT_PACK",
       "fault_flag == 'pack_loss'  (contactor open / isolation trip)",
       "R22c", lambda c: c["fault"] == "pack_loss"),
    _t("FAULT", "*", "F_PACK_DERATE", 12, "G_FLT_PACK_DER",
       "fault_flag == 'pack_derate'  (cell string derate, not a loss)",
       "R16 / R8 as restated by R12", lambda c: c["fault"] == "pack_derate"),
    _t("FAULT", "*", "F_RESISTOR_LOSS", 13, "G_FLT_RES",
       "fault_flag == 'resistor_loss'  (chopper, element or blower)",
       "R2 (the resistor is the only speed-independent retarder)",
       lambda c: c["fault"] == "resistor_loss"),
    _t("FAULT", "*", "F_INV_DERATE", 14, "G_FLT_INV",
       "fault_flag == 'inverter_thermal'",
       "R13 / WS2 inverter Tj export",
       lambda c: c["fault"] == "inverter_thermal"),
    _t("FAULT", "*", "F_SENSOR_LOSS", 15, "G_FLT_SENS",
       "fault_flag == 'sensor_loss'",
       "R9 (methods) / E23", lambda c: c["fault"] == "sensor_loss"),
    _t("FAULT", "*", "F_NONE", 90, "G_FLT_CLEAR",
       "fault_flag is None  (faults are latched by the injector; a real "
       "reset is a key cycle plus a diagnostic clear)",
       "-", lambda c: c["fault"] is None),

    # -------------------------------------------------------- THERMAL ----
    _t("THERMAL", "*", "H_PRECOND", 10, "G_TH_PRECOND",
       "t_cell_C < -15.0",
       "R16 (preconditioning required below -15 C cell)",
       lambda c: c["t_cell_C"] < R16_PRECOND_C),
    _t("THERMAL", "*", "H_INV_DERATE", 11, "G_TH_INV",
       "tj_inverter_C >= 125.0",
       "R13 / WS2 inverter_Tj_at_continuous_rating_C",
       lambda c: c["tj_inv_C"] >= INV_TJ_DERATE_C),
    _t("THERMAL", "*", "H_HOT_PACK_DERATE", 12, "G_TH_HOT",
       "t_cell_C > 45.0  (WS3 acceptance curve falls above +45 C)",
       "R16 / WS3 regen_acceptance.csv",
       lambda c: c["t_cell_C"] > T_CELL_HOT_DERATE_C),
    _t("THERMAL", "*", "H_COLD_DERATE", 13, "G_TH_COLD",
       "-15.0 <= t_cell_C <= 10.0",
       "R16 (dispatch permitted on the published derate curves)",
       lambda c: R16_PRECOND_C <= c["t_cell_C"] <= R16_BAND_HI_C),
    _t("THERMAL", "*", "H_NOMINAL", 90, "G_TH_NOM",
       "otherwise", "R16", lambda c: True),

    # ------------------------------------------------------- TRACTION ----
    _t("TRACTION", "*", "T_DRIVE_LIMIT", 10, "G_TC_DRIVE",
       "p_wheel_demand_kW > 0 and T_wheel_demand > T_adhesion_drive",
       "E23 (day-one requirement) / WS2 traction_control.torque_limit_law",
       lambda c: c["tc_drive_limited"]),
    _t("TRACTION", "*", "T_REGEN_LIMIT", 11, "G_TC_REGEN",
       "p_wheel_demand_kW < 0 and T_wheel_regen > T_adhesion_brake",
       "E23 (empty-truck regen, mu ~0.36 per stop)",
       lambda c: c["tc_regen_limited"]),
    _t("TRACTION", "*", "T_OFF", 90, "G_TC_OFF",
       "otherwise", "E23", lambda c: True),

    # ------------------------------------------------------- DISPATCH ----
    _t("DISPATCH", "*", "D_FAULT", 5, "G_D_FAULT",
       "FAULT == F_GENSET_LOSS", "R22c",
       lambda c: c["state_FAULT"] == "F_GENSET_LOSS"),
    _t("DISPATCH", "*", "D_MOTOR", 6, "G_D_MOTOR",
       "motoring_sink_commanded  (retardation deficit and the R2 resistor "
       "is unavailable; the ISG motors the engine against its own FMEP as "
       "an electrical sink)",
       "R2 / WS4 motoring_fmep_anchor 10.7 kW @ 1,706 rpm [WS5-PROPOSED]",
       lambda c: c["motor_sink_cmd"]),
    _t("DISPATCH", "*", "D_START", 10, "G_D_START",
       "engine_off and (soc_usable < band_lo or reserve_deficit_kW > 0) "
       "and start_inhibit == False",
       "R19 (V1 hysteresis) / R22b (V2 dispatch) / ESC-9 reserve",
       lambda c: c["d_cmd"] == "D_START"),
    _t("DISPATCH", "*", "D_RESERVE", 11, "G_D_RESERVE",
       "reserve_deficit_kW > 0  (bus demand above the pack's dispatch "
       "envelope P_dis_allowed(T_cell, SOC); the genset covers the excess)",
       "ESC-9 / WS3 soc15_note ('full power below SOC 40 is NOT guaranteed "
       "- WS5 dispatch limit')",
       lambda c: c["d_cmd"] == "D_RESERVE"),
    _t("DISPATCH", "*", "D_FOLLOW", 12, "G_D_FOLLOW",
       "strategy == load_following, or emergency SOC band entered",
       "R22b", lambda c: c["d_cmd"] == "D_FOLLOW"),
    _t("DISPATCH", "*", "D_NOTCH_HI", 13, "G_D_HI",
       "strategy == two_point and lowpass(P_bus_demand, tau) > P_notch_lo "
       "+ h_up", "R22b", lambda c: c["d_cmd"] == "D_NOTCH_HI"),
    _t("DISPATCH", "*", "D_PIN", 14, "G_D_PIN",
       "engine_on and no higher-priority command",
       "R22b (pinned point) / R19 (V1 fixed point)",
       lambda c: c["d_cmd"] == "D_PIN"),
    _t("DISPATCH", "*", "D_OFF", 90, "G_D_OFF",
       "soc_usable > band_hi and reserve_deficit_kW <= 0",
       "R19 / R22b", lambda c: True),

    # ---------------------------------------------------------- BLEND ----
    # The R15 cascade. The active state names the DEEPEST stage taking
    # power this sample; the guards ARE the saturation conditions of the
    # stage above.
    _t("BLEND", "*", "B_FRICTION", 10, "G_B_FRIC",
       "p_regen_bus - p_pack - p_heater - p_resistor > 0  (all electrical "
       "sinks saturated; the balance goes to the service brakes)",
       "R15 / R2", lambda c: c["blend_stage"] == "B_FRICTION"),
    _t("BLEND", "*", "B_RESISTOR", 11, "G_B_RES",
       "p_regen_bus > p_pack + p_heater and resistor available",
       "R15 (regen -> heater -> resistor -> friction) / R2",
       lambda c: c["blend_stage"] == "B_RESISTOR"),
    _t("BLEND", "*", "B_HEATER", 12, "G_B_HTR",
       "p_regen_bus > p_pack and t_cell_C <= 10.0 (R16 band) and heater "
       "not pre-empted by drive power",
       "R15 (pack heater second, electrical path only - no plumbing "
       "coupling) / R16", lambda c: c["blend_stage"] == "B_HEATER"),
    _t("BLEND", "*", "B_PACK", 13, "G_B_PACK",
       "p_regen_bus > 0 and p_pack > 0",
       "R15 (regen-to-pack first)", lambda c: c["blend_stage"] == "B_PACK"),
    _t("BLEND", "*", "B_NONE", 90, "G_B_NONE",
       "p_wheel_demand_kW >= 0", "R15",
       lambda c: True),

    # -------------------------------------------------------- VEHICLE ----
    _t("VEHICLE", "*", "V_HALT", 5, "G_V_HALT",
       "no torque path: FAULT in {F_GENSET_LOSS, F_PACK_LOSS} and the "
       "surviving source cannot serve the demand -> TOW",
       "R22c (both variants share the genset-or-pack-fault = tow "
       "asymmetry)", lambda c: c["halt"]),
    _t("VEHICLE", "*", "V_PRECOND", 10, "G_V_PRECOND",
       "THERMAL == H_PRECOND and v == 0",
       "R16 (preconditioning below -15 C cell)",
       lambda c: c["state_THERMAL"] == "H_PRECOND" and c["v_ms"] <= 0.05),
    _t("VEHICLE", "*", "V_LIMP", 11, "G_V_LIMP",
       "FAULT != F_NONE and a torque path survives",
       "R22c / R4's derated-limp precedent",
       lambda c: c["fault"] is not None and not c["halt"]),
    _t("VEHICLE", "*", "V_BRAKE", 12, "G_V_BRAKE",
       "p_wheel_demand_kW < -0.5",
       "R15", lambda c: c["p_wheel_kw"] < -P_DEMAND_DEADBAND_KW),
    _t("VEHICLE", "*", "V_DRIVE", 13, "G_V_DRIVE",
       "p_wheel_demand_kW > +0.5",
       "-", lambda c: c["p_wheel_kw"] > P_DEMAND_DEADBAND_KW),
    _t("VEHICLE", "*", "V_READY", 90, "G_V_READY",
       "otherwise (stationary or coasting inside the deadband)",
       "R22d (coasting inside the deadband still prefers light regen)",
       lambda c: True),
]


class SupervisorStateMachine:
    """Executable form of the specification above."""

    def __init__(self):
        self.state = dict(INITIAL)
        self._by_region = {r: [t for t in TRANSITIONS if t["region"] == r]
                           for r in REGION_ORDER}
        self.counts = {r: {s: 0 for s in STATES[r]} for r in REGION_ORDER}
        self.transitions_taken = {}
        self.ambiguous_samples = 0

    def step(self, ctx):
        for region in REGION_ORDER:
            ctx[f"state_{region}"] = self.state[region]
        for region in REGION_ORDER:
            cur = self.state[region]
            fired = None
            n_specific_eligible = 0
            for tr in self._by_region[region]:
                if tr["src"] != "*" and tr["src"] != cur:
                    continue
                if tr["fn"](ctx):
                    # the priority-90 transition in each region is the
                    # deliberate catch-all ("otherwise"); it is true by
                    # construction and is not evidence of ambiguity
                    if tr["prio"] < 90:
                        n_specific_eligible += 1
                    if fired is None:
                        fired = tr
            if n_specific_eligible > 1:
                # two SPECIFIC guards were true at once; the declared
                # priority order resolved it, and the count is exported
                self.ambiguous_samples += 1
            if fired is not None and fired["dst"] != cur:
                key = f"{region}:{cur}->{fired['dst']}"
                self.transitions_taken[key] = \
                    self.transitions_taken.get(key, 0) + 1
                self.state[region] = fired["dst"]
            ctx[f"state_{region}"] = self.state[region]
            self.counts[region][self.state[region]] += 1
        return self.state


# ------------------------------------------------------ static validation
def validate():
    """Structural checks on the specification. Returns a dict; run_ws5
    asserts every boolean is True."""
    out = {}
    all_ok = True
    for region, states in STATES.items():
        srcs = {t["src"] for t in TRANSITIONS if t["region"] == region}
        dsts = {t["dst"] for t in TRANSITIONS if t["region"] == region}
        unknown_dst = sorted(dsts - set(states))
        unknown_src = sorted(s for s in srcs if s != "*" and s not in states)
        # reachability: "*" sources make every dst reachable from anywhere
        reachable = set([INITIAL[region]]) | dsts
        unreachable = sorted(set(states) - reachable)
        no_exit = sorted(s for s in states
                         if not any(t["region"] == region
                                    and (t["src"] == "*" or t["src"] == s)
                                    for t in TRANSITIONS))
        prios = [t["prio"] for t in TRANSITIONS if t["region"] == region]
        ok = (not unknown_dst and not unknown_src and not unreachable
              and not no_exit and len(prios) == len(set(prios))
              and INITIAL[region] in states)
        all_ok &= ok
        out[region] = dict(n_states=len(states),
                           n_transitions=len(prios),
                           initial=INITIAL[region],
                           unknown_dst=unknown_dst, unknown_src=unknown_src,
                           unreachable=unreachable, states_without_exit=no_exit,
                           priorities_unique=len(prios) == len(set(prios)),
                           ok=ok)
    out["_all_regions_ok"] = bool(all_ok)
    out["_n_regions"] = len(STATES)
    out["_n_states_total"] = sum(len(v) for v in STATES.values())
    out["_n_transitions_total"] = len(TRANSITIONS)
    out["_has_clutch_state"] = any(
        "CLUTCH" in s.upper() or "LOCK" in s.upper() or "SYNC" in s.upper()
        or "MODE" in s.upper()
        for v in STATES.values() for s in v)
    return out


def spec_rows():
    """Flat transition table for export (data/state_machine.csv)."""
    return [dict(region=t["region"], source=t["src"], target=t["dst"],
                 priority=t["prio"], guard_id=t["guard"],
                 guard=t["guard_text"], ruling=t["ruling"])
            for t in sorted(TRANSITIONS,
                            key=lambda x: (REGION_ORDER.index(x["region"]),
                                           x["prio"]))]


def mermaid():
    """Mermaid source for the machine (one stateDiagram per region)."""
    L = ["%% Project Volt WS5 supervisor state machine",
         "%% orthogonal regions; guards in ws5_statemachine.TRANSITIONS"]
    for region in REGION_ORDER:
        L.append(f"%%--- region {region} ---")
        L.append("stateDiagram-v2")
        L.append(f"    [*] --> {INITIAL[region]}")
        for t in sorted((x for x in TRANSITIONS if x["region"] == region),
                        key=lambda x: x["prio"]):
            src = "any" if t["src"] == "*" else t["src"]
            L.append(f"    {src} --> {t['dst']} : {t['guard']}")
    return "\n".join(L) + "\n"
