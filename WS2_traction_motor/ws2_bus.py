"""DC bus implementation on the R10 ruled window: cables, string check.

ROUND 4: the 400 V-vs-800 V class trade of rounds 1-3 is SUPERSEDED by
ruling R10 (BASELINE v2) — the bus is the pack-native 288s LTO window
432.0-748.8 V, nominal 662.4 V, 10-s transients to 777.6 V, 1200 V
semiconductor class. This module now (a) verifies the ruled string
arithmetic and (b) builds the cable table under the R14 export
discipline: every sizing current is an explicit max over an enumerated
case set with the governing case labeled, and the continuous basis for
the motor run is the R13 crawl phase current (NOT a power-derived S2
figure — that omission was WS2-F11).
"""

from ws2_params import BUS, CABLE, RES

# R10 ruled string (WS3 ratified pack): 288s1p SCiB-class LTO.
STRING = dict(
    n_series=288,
    v_cell_min=1.5, v_cell_nom=2.3, v_cell_max=2.6, v_cell_transient=2.7,
    granularity_cells=12,
)


def string_check():
    """Verify the R10 window is the 288s string arithmetic, exactly."""
    s = STRING
    out = dict(
        n_series=s["n_series"],
        v_string_min=round(s["n_series"] * s["v_cell_min"], 1),
        v_string_nom=round(s["n_series"] * s["v_cell_nom"], 1),
        v_string_max=round(s["n_series"] * s["v_cell_max"], 1),
        v_string_transient=round(s["n_series"] * s["v_cell_transient"], 1),
        granularity_V=round(s["granularity_cells"] * s["v_cell_nom"], 1),
    )
    out["matches_R10_window"] = bool(
        abs(out["v_string_min"] - BUS["v_min"]) < 0.05
        and abs(out["v_string_nom"] - BUS["v_nom"]) < 0.05
        and abs(out["v_string_max"] - BUS["v_max"]) < 0.05
        and abs(out["v_string_transient"] - BUS["v_transient"]) < 0.05)
    return out


def pick_cable(i_cont):
    for mm2 in sorted(CABLE["ampacity"]):
        if CABLE["ampacity"][mm2] >= i_cont:
            return mm2
    return -max(CABLE["ampacity"])  # negative = oversize flag


def _run_entry(run, cases, governing, transient_cases=None, note=None):
    """R14 form: sizing current = max over the enumerated CONTINUOUS case
    set; the governing case is labeled. A listed transient (amps,
    duration_s) is checked by excess-power adiabatic rise on the copper
    thermal mass from the steady state at the sizing current, against
    the insulation's short-term overload class — a 1-min event judged
    against a continuous ampacity would be a category error in either
    direction."""
    i_size = max(cases.values())
    assert abs(cases[governing] - i_size) < 1e-9, (run, governing)
    mm2 = pick_cable(i_size)
    length, ncond = CABLE["runs"][run]
    mass = (abs(mm2) * 1e-6) * CABLE["cu_density"] * CABLE["build_factor"] \
        * length * ncond
    amp = CABLE["ampacity"][abs(mm2)]
    # steady conductor temperature at the continuous sizing current
    # (I^2-scaled rise between the derate ambient and the rating)
    T_steady = CABLE["T_ambient_derate"] + (i_size / amp) ** 2 * (
        CABLE["T_rating_cont"] - CABLE["T_ambient_derate"])
    entry = dict(
        rule="max over enumerated continuous cases (R14)",
        cases_A={k: round(v, 1) for k, v in cases.items()},
        i_size_A=round(i_size, 1),
        governing_case=governing,
        mm2=mm2, ampacity_A=amp,
        margin_pct=round((amp / i_size - 1.0) * 100, 1),
        conductor_T_steady_C=round(T_steady, 1),
        mass_kg=round(mass, 2),
    )
    if transient_cases:
        A_m2 = abs(mm2) * 1e-6
        tr = {}
        all_ok = True
        for label, (i_tr, dur_s) in transient_cases.items():
            dT = max(0.0, (i_tr ** 2 - i_size ** 2)) \
                * CABLE["cu_resistivity_hot"] * dur_s \
                / (A_m2 ** 2 * CABLE["cu_density"] * CABLE["cu_cp"])
            T_end = T_steady + dT
            ok = bool(T_end <= CABLE["T_shortterm"])
            all_ok = all_ok and ok
            tr[label] = dict(I_A=round(i_tr, 1), duration_s=dur_s,
                             adiabatic_dT_K=round(dT, 1),
                             conductor_T_end_C=round(T_end, 1),
                             within_130C_shortterm=ok)
        entry["transient_cases"] = tr
        entry["transients_ok"] = all_ok
    if note:
        entry["note"] = note
    return entry, mass


def cable_table(i_crawl_cont_arms, i_crawl_ws1_arms, i_s2_floor_arms,
                i_s2_nom_arms, i_peak_arms):
    """R14 cable table for the ruled window.

    i_crawl_cont_arms: phase current at the R13 continuous corner
        (515 Nm at 25 km/h — computed by the dq solver, the max over the
        crawl band; MTPA current is voltage-independent, so this is the
        same at every window voltage).
    i_crawl_ws1_arms: phase current at the WS1 settle cases (510 Nm).
    i_s2_floor_arms / i_s2_nom_arms: S2 (95 kW / 207.4 Nm) phase current
        at the window floor / nominal.
    i_peak_arms: 60-s peak envelope phase current (transient).
    """
    vlo, vnom = BUS["v_min"], BUS["v_nom"]
    vtr = BUS["v_transient"]
    detail = {}
    total = 0.0

    e, m = _run_entry(
        "genset_to_bus",
        cases={
            "R6 125 kW sustained at the 432.0 V floor "
            "(charge-depleted running)": 125e3 / vlo,
            "R6 125 kW at 662.4 V nominal": 125e3 / vnom,
        },
        governing="R6 125 kW sustained at the 432.0 V floor "
                  "(charge-depleted running)")
    detail["genset_to_bus"] = e
    total += m

    e, m = _run_entry(
        "pack_to_bus",
        cases={
            "R2 50 kW continuous descent charge at the floor": 50e3 / vlo,
            "R8 125 kW discharge 1-min at the floor, x0.5 thermal "
            "derate for repetition": 0.5 * 125e3 / vlo,
            "R8 110 kW charge 1-min at the floor, x0.5 thermal "
            "derate for repetition": 0.5 * 110e3 / vlo,
        },
        governing="R8 125 kW discharge 1-min at the floor, x0.5 thermal "
                  "derate for repetition",
        transient_cases={
            "R8 125 kW discharge at the floor, undegraded, 60 s":
                (125e3 / vlo, 60.0)},
        note="R8 peaks restated bus-side per R12 (125 kW discharge / "
             "110 kW charge); the undegraded 1-min transient is cleared "
             "by adiabatic rise, and the x0.5 continuous-equivalent "
             "derate is thereby substantiated, not asserted")
    detail["pack_to_bus"] = e
    total += m

    e, m = _run_entry(
        "inverter_to_motor",
        cases={
            "R13 continuous crawl corner, 515 Nm at 25 km/h "
            "(band top; MTPA, voltage-independent)": i_crawl_cont_arms,
            "crawl 510 Nm at the WS1 settle speeds": i_crawl_ws1_arms,
            "S2 95 kW / 207.4 Nm at the 432.0 V floor (10-min)":
                i_s2_floor_arms,
            "S2 95 kW / 207.4 Nm at 662.4 V nominal": i_s2_nom_arms,
        },
        governing="R13 continuous crawl corner, 515 Nm at 25 km/h "
                  "(band top; MTPA, voltage-independent)",
        transient_cases={"60-s peak envelope (449 A_pk)":
                         (i_peak_arms, 60.0)},
        note="F11 closure: the continuous basis IS the crawl phase "
             "current (R13); every 10-min case sits below it")
    detail["inverter_to_motor"] = e
    total += m

    res_R = RES["R_ohm"]
    e, m = _run_entry(
        "chopper_to_resistor",
        cases={
            "R2 50 kW continuous, PWM rms sqrt(P/R) "
            "(voltage-independent)": (50e3 / res_R) ** 0.5,
            "full chopper duty at the 748.8 V ceiling, continuous":
                BUS["v_max"] / res_R,
            "full chopper duty during a 777.6 V 10-s transient":
                vtr / res_R,
        },
        governing="full chopper duty during a 777.6 V 10-s transient",
        note="F12 closure: sized at the full hardware ceiling, not the "
             "50 kW requirement — the cable never limits the bank "
             "(cable-limited ceiling reported in results resistor block)")
    detail["chopper_to_resistor"] = e
    total += m

    return dict(
        sizing_convention=(
            "R14: every run's sizing current is an explicit max over the "
            "enumerated continuous case set (governing case labeled); "
            "voltage-dependent cases are taken at the lowest voltage at "
            "which their sustained power must flow (the F10 rule, "
            "carried); the motor-run continuous basis is the R13 crawl "
            "phase current (F11 closure); the chopper run is sized at "
            "the full hardware ceiling (F12 closure)"),
        detail=detail,
        cable_mass_kg=round(total, 1),
    )
