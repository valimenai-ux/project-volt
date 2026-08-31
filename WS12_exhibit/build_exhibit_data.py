"""WS12 — THE EXHIBIT: build the data bundle, the traces and the manifest.

One entry point. Deterministic: no wall clock, no randomness, no network,
sorted keys everywhere, stdlib only. Re-running reproduces every emitted
artifact byte-identically.

    ../.venv/bin/python3 build_exhibit_data.py

It writes, all under `app/public/`:

    data/exhibit_data.json        the bundle every screen renders from
    data/manifest.json            every number of record the app can render
    data/decimation_manifest.json one row per published trace
    traces/<id>/scrub_1hz.csv     1 Hz strided scrub index
    traces/<id>/seg_NNNN.csv      10 Hz segments, fetched per viewed segment
    maps/<name>.csv               the BSFC maps the simulator plots

The app renders `s` strings and nothing else. It contains no numeral of
record in its own source. `exhibit_verify.py` re-opens every cited file
with its own resolver and its own formatter and asserts every string.
"""

import json
import os
import shutil
import sys

from ws12_record import (ALLOWED_STATUS_BADGES, TIER_DERIVED,
                         TIER_RECORD, TIER_SANDBOX, check_badge, cite,
                         load_json, lit, repo_path, resolve, sha256_of,
                         status_badge)
import ws12_sandbox as SB
import ws12_traces as TR

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, "app", "public")
DATA_OUT = os.path.join(PUBLIC, "data")
TRACE_OUT = os.path.join(PUBLIC, "traces")
MAP_OUT = os.path.join(PUBLIC, "maps")

WS1 = "WS1_loads_duty_cycles/results.json"
WS4 = "WS4_genset/results_ws4.json"
WS5 = "WS5_controls/results_ws5.json"
WS8 = "WS8_semi_architecture/results_ws8.json"
WS9 = "WS9_vehicle_one_wave2/results_ws9.json"
WS11 = "WS11_vehicle_zero_ruler/results_ws11.json"
BASELINE = "BASELINE_v7_FREEZE.md"

# Program constants, with the file and line they are declared at. Used by
# the DERIVED race counters; every one is quoted, never guessed.
LHV_KJ_PER_G = 42.8       # WS4_genset/ws4_models.py:26
DENSITY_G_PER_L = 832.0   # WS11_vehicle_zero_ruler/ws11_params.py:37
DT_S = 0.1                # 10 Hz trace step (R34)

_TEXT_CACHE = {}


def text_of(rel):
    if rel not in _TEXT_CACHE:
        with open(repo_path(rel), "r", encoding="utf-8") as fh:
            _TEXT_CACHE[rel] = fh.read()
    return _TEXT_CACHE[rel]


def _norm_map(s):
    """Normalise for searching, and keep a map back to the source index.

    The program's markdown is hard-wrapped and uses typographic dashes and
    quotes inconsistently between documents. Searching on a normalised
    form and then LIFTING THE ORIGINAL SUBSTRING out of the file means
    the string this exhibit renders is literally the file's own bytes —
    the search is tolerant, the quotation is not.
    """
    dash = {"‐": "-", "‑": "-", "‒": "-", "–": "-",
            "—": "-", "―": "-", "−": "-",
            "‘": "'", "’": "'", "“": '"', "”": '"',
            " ": " "}
    out = []
    idx = []
    prev_space = True
    for i, ch in enumerate(s):
        c = dash.get(ch, ch)
        if c.isspace():
            if prev_space:
                continue
            out.append(" ")
            idx.append(i)
            prev_space = True
        else:
            out.append(c)
            idx.append(i)
            prev_space = False
    return "".join(out), idx


def q(rel, text, note=None):
    """A verbatim quotation from a document of record.

    Raises if the passage is not in the file. Returns the file's own
    characters, not the ones typed here. `exhibit_verify.py` repeats the
    lift independently and asserts the result matches.
    """
    hay = text_of(rel)
    hn, hidx = _norm_map(hay)
    nn, _ = _norm_map(text)
    at = hn.find(nn)
    if at < 0:
        raise ValueError("quote not found in %s: %r" % (rel, text))
    start = hidx[at]
    end = hidx[at + len(nn) - 1] + 1
    lifted = " ".join(hay[start:end].split())
    out = {"s": lifted, "file": rel, "kind": "quote", "tier": TIER_RECORD,
           "probe": " ".join(text.split())}
    if note:
        out["note"] = note
    return out


# Files that are still being written while this build runs. They are cited
# by verbatim quotation, which `exhibit_verify.py` re-checks, but they are
# NOT hash-pinned: pinning a living log would make the exhibit's own
# byte-stability depend on whether anyone appended a line in between.
LIVING_FILES = ("PM_LOG.md",)


def ff(rel):
    """A file fact: name, size and sha256 of a file of record."""
    if rel in LIVING_FILES:
        return {"file": rel, "kind": "fileref", "tier": TIER_RECORD,
                "s": os.path.basename(rel),
                "note": ("append-only program log, still being written. "
                         "Cited by verbatim quotation and not hash-pinned, "
                         "because pinning a living file would make this "
                         "exhibit's own byte-stability depend on whether a "
                         "line was appended between two builds.")}
    p = repo_path(rel)
    return {"file": rel, "bytes": os.path.getsize(p), "sha256": sha256_of(rel),
            "kind": "file", "tier": TIER_RECORD,
            "s": "%s · sha256 %s…%s" % (os.path.basename(rel),
                                        sha256_of(rel)[:8],
                                        sha256_of(rel)[-4:])}


# ===================================================================== 1
# Guard rails and the status vocabulary. Bound, not typed in prose.

def build_guard_rails():
    return {
        "methodClaim": {
            "headline": "catches internal inconsistency",
            "neverClaims": "catches wrong physics",
            "why": ("No hardware was built. The ruler is uncalibrated. "
                    "Every verdict in this exhibit is model-relative."),
            "evidence": [
                q(BASELINE, "Ruler uncalibrated\n(ESC-1); all Vehicle Zero "
                            "verdicts are model-relative."),
                cite(WS11, ["interface_ws11", "ruler", "anchor",
                            "calibrate_order_satisfied"], "str",
                     note="the calibration the assignment ordered was not "
                          "performed; WS11 records it as a NON-SATISFACTION"),
                cite(WS11, ["interface_ws11", "ruler", "anchor",
                            "calibrate_order_statement"], "str"),
            ],
        },
        "noPromotion": {
            "headline": "No status is ever promoted",
            "rule": q(BASELINE,
                      "R52 — Every verdict and number keeps the status it "
                      "holds at freeze,\nlabeled FROZEN-<status>. Nothing is "
                      "promoted; nothing is quietly\ndemoted. The public "
                      "record states each status plainly."),
            "allowed": list(ALLOWED_STATUS_BADGES),
            "forbidden": ["RATIFIED", "PROVISIONAL"],
            "forbiddenWhy": ("the v6-era labels. A bare RATIFIED or "
                             "PROVISIONAL in a badge position is a build "
                             "failure, not a style preference."),
        },
    }


# ===================================================================== 2
# Screen 1 — the verdict wall. The front door.

def card_g1():
    g1 = ["interface_ws4", "gate_g1"]
    att = g1 + ["attribution_rows"]
    vd = g1 + ["verdict"]

    prior = cite(WS4, att + ["prior_convention", "min"], "+.2f", suf="%")
    d_map = cite(WS4, att + ["map_vs_scalar_alone", "delta_pp_min"], "+.2f",
                 suf=" pp")
    d_spin = cite(WS4, att + ["spin_drag_alone", "delta_pp_min"], "+.2f",
                  suf=" pp")
    d_both = cite(WS4, att + ["both_g1r", "delta_pp_min"], "+.2f", suf=" pp")
    inter = d_both["v"] - d_map["v"] - d_spin["v"]
    d_int = lit(inter, "+.2f", suf=" pp", tier=TIER_DERIVED,
                source=("both_g1r.delta_pp_min minus map_vs_scalar_alone."
                        "delta_pp_min minus spin_drag_alone.delta_pp_min, "
                        "all three from %s -> %s" % (WS4, " -> ".join(att))))
    final = cite(WS4, vd + ["margin_pct_ensemble_min"], "+.2f", suf="%")

    return {
        "id": "g1",
        "kicker": "GATE G1 · THE PROGRAM'S FAVOURITE IDEA",
        "title": "A pre-committed criterion killed the clutch",
        "statusBadge": status_badge("FROZEN-RATIFIED"),
        "statusQuote": q(BASELINE, "Vehicle Zero: architecture ratified "
                                   "(pure series, both variants)."),
        "gateStatus": cite(WS4, g1 + ["status"], "str"),
        "executedBy": cite(WS4, g1 + ["executed_by"], "str"),
        "archivalNotice": cite(WS4, g1 + ["_archival_notice"], "str"),
        "criterion": cite(WS4, vd + ["kill_criterion_pct"], ".1f", suf="%"),
        "criterionText": q("LEAD_HANDOVER.md",
                           "D1. Pre-commit, then measure. Every gate has a "
                           "numeric kill criterion\n    written BEFORE the "
                           "computation."),
        "passes": cite(WS4, vd + ["passes"], "str"),
        "missedBy": cite(WS4, vd + ["missed_by_pp"], ".2f", suf=" pp"),
        "seedsPositive": cite(WS4, vd + ["seeds_margin_positive_n"], "d"),
        "seedsTotal": cite(WS4, vd + ["seeds_total"], "d"),
        "governingCase": cite(WS4, vd + ["margin_pct_ensemble_min_"
                                         "governing_case"], "str"),
        "convention": cite(WS4, vd + ["convention"], "str"),
        "waterfall": [
            {"label": "Prior convention", "kind": "start", "value": prior,
             "sub": "ratified r2 anchor, reproduced bit-identically"},
            {"label": "Map-vs-scalar swap", "kind": "step", "value": d_map,
             "sub": "measured loss surface replaces one scalar chain "
                    "efficiency"},
            {"label": "Spin-drag member", "kind": "step", "value": d_spin,
             "sub": "permanently geared machines charged on unloaded "
                    "samples"},
            {"label": "Correction interaction", "kind": "step",
             "value": d_int, "sub": "the two members are not additive"},
            {"label": "G1-R, gate of record", "kind": "end", "value": final,
             "sub": "nominal ensemble-min, 8 seeds"},
        ],
        "body": ("The criterion — mode (a) must beat mode (b) by at least "
                 "5% — was written before the number existed. The first "
                 "pass returned +6.26% and passed. A chain-convention "
                 "correction then moved the whole baseline of the "
                 "comparison, the margin came back at -2.58%, and the "
                 "criterion could not be renegotiated with. The clutch, the "
                 "lockup device and actuator, the sync control, the "
                 "condition-aware mode policy and the fault spec are all "
                 "deleted with it."),
    }


WS8_CANDS = ("S1", "S2", "S3", "S4")
WS8_TITLES = {
    "S1": "Pure series",
    "S2": "Single cruise ratio + torque-fill",
    "S3": "Tandem split, no gearbox anywhere",
    "S4": "Range-extended BEV",
}


def card_ws8():
    rows = []
    for s in WS8_CANDS:
        ak = ["advance_kill", "candidates", s]
        pk = ["interface_ws8", "per_km_margin_paired", "corners", "nominal",
              s, "ensemble"]
        rows.append({
            "id": s,
            "title": WS8_TITLES[s],
            "perKmMin": cite(WS8, pk + ["min"], "+.2f", suf="%"),
            "perKmMedian": cite(WS8, pk + ["median"], "+.2f", suf="%"),
            "perPayloadMin": cite(WS8, ak + ["nominal_margin_pct_min"],
                                  "+.2f", suf="%"),
            "perPayloadMedian": cite(WS8, ak + ["nominal_margin_pct_median"],
                                     "+.2f", suf="%"),
            "worstCorner": cite(WS8, ak + ["worst_corner"], "str"),
            "worstCornerMin": cite(WS8, ak + ["worst_corner_margin_pct_min"],
                                   "+.2f", suf="%"),
            "verdict": cite(WS8, ak + ["verdict"], "str"),
            "statusBadge": status_badge("FROZEN-KILL"),
            "bindingReason": cite(WS8, ak + ["binding_reason"], "str"),
        })
    whr = ["interface_ws8", "whr_gate"]
    return {
        "id": "ws8",
        "kicker": "VEHICLE ONE · 36,300 kg · FOUR CANDIDATES",
        "title": "Won on the road, lost on the scale",
        "statusBadge": status_badge("FROZEN-KILL"),
        "numbersBadge": status_badge("FROZEN-PROVISIONAL"),
        "statusQuote": q(BASELINE,
                         "Vehicle One: WS8 S1-S4 KILLED (final), WHR DROPPED "
                         "(final); numbers\nFROZEN-PROVISIONAL at r3 (r3 "
                         "adjudication not clean, r4 ordered and\nnot run)."),
        "adjudicationQuote": q("WS8_semi_architecture/FINDINGS_WS8_r3.md",
                               "**Verdict: NOT CLEAN. Two blocking, six "
                               "material, twelve minor.**"),
        "numbersVersion": cite(WS8, ["interface_ws8", "numbers_version"],
                               "str"),
        "criterionNominal": cite(WS8, ["interface_ws8", "advance_kill",
                                       "nominal_pct"], ".1f", suf="%"),
        "criterionCorner": cite(WS8, ["interface_ws8", "advance_kill",
                                      "every_corner_pct"], ".1f", suf="%"),
        "metric": cite(WS8, ["interface_ws8", "metric_of_record"], "str"),
        "gcw": cite(WS8, ["interface_ws8", "gcw_kg"], ",.0f", suf=" kg"),
        "rows": rows,
        "whr": {
            "threshold": cite(WS8, whr + ["threshold_pct"], ".1f", suf="%"),
            "rows": [{"id": s,
                      "result": cite(WS8, whr + ["result", s], "str"),
                      "best": cite(WS8, whr + ["best_net_margin_pct", s],
                                   "+.2f", suf="%")}
                     for s in ("S1", "S2", "S3")],
        },
        "body": ("Every electrified candidate won on fuel per kilometre and "
                 "gave the win back in freight. At a fixed gross weight "
                 "every powertrain kilogram displaces payload one for one, "
                 "so the pair of bars is the whole argument: the left bar "
                 "is what the road sees, the right bar is what the customer "
                 "ships. The criterion is read on the right one."),
    }


def card_duty_flip():
    def m(key, case, stat):
        return cite(WS11, ["results", key, case,
                           "margin_pct_per_payload_tkm_paired", stat],
                    "+.2f", suf="%")

    def k(key, case, stat):
        return cite(WS11, ["results", key, case,
                           "margin_pct_per_km_paired", stat], "+.2f", suf="%")

    return {
        "id": "duty",
        "kicker": "THE SAME TRUCK, TWO DUTIES",
        "title": "The sign flips with the duty, not the design",
        "claimQuote": q(BASELINE,
                        "3. It has a DUTY boundary: the same truck wins +20% "
                        "on stop-go and\n   loses on regional duty (V1 "
                        "provisional, V2 kill)."),
        "rows": [
            {"id": "V2-SUB", "vehicle": "V2 Trucker", "duty": "VOLT-SUB",
             "dutyName": "stop-go suburban delivery",
             "perKm": k("V2_on_VOLT-SUB", "nominal", "min"),
             "perPayload": m("V2_on_VOLT-SUB", "nominal", "min"),
             "note": "COMPARISON — NOT A VERDICT OF RECORD",
             "noteWhy": ("V2 was gated on VOLT-REG, its design duty. This "
                         "row is the same vehicle run on the other duty and "
                         "exported for comparison; no ADVANCE/KILL "
                         "criterion was read on it.")},
            {"id": "V2-REG", "vehicle": "V2 Trucker", "duty": "VOLT-REG",
             "dutyName": "regional mixed duty",
             "perKm": k("V2_on_VOLT-REG", "nominal", "min"),
             "perPayload": m("V2_on_VOLT-REG", "nominal", "min"),
             "statusBadge": status_badge("FROZEN-KILL"),
             "note": "VERDICT OF RECORD",
             "noteWhy": "V2's design duty. This is the gated case."},
            {"id": "V1-SUB", "vehicle": "V1 Postal", "duty": "VOLT-SUB",
             "dutyName": "stop-go suburban delivery",
             "perKm": k("V1_on_VOLT-SUB", "nominal", "min"),
             "perPayload": m("V1_on_VOLT-SUB", "nominal", "min"),
             "statusBadge": status_badge("FROZEN-PROVISIONAL"),
             "note": "VERDICT OF RECORD",
             "noteWhy": "V1's design duty. This is the gated case."},
        ],
        "body": ("One architecture, two duties, opposite signs. On stop-go "
                 "the series chain converts the whole braking energy the "
                 "duty throws away and idles nothing; on regional duty "
                 "there is little to recover and the conversion tax runs "
                 "all day. The mass penalty is identical in both columns."),
    }


def card_ws11_pair():
    def v(key, field, spec, suf="%"):
        return cite(WS11, ["interface_ws11", "verdicts", key, field], spec,
                    suf=suf)

    rb = ["interface_ws11", "verdict_robustness", "rows"]
    fp = ["interface_ws11", "ruler_fuel_flip_points"]
    return {
        "id": "ws11",
        "kicker": "VEHICLE ZERO · 6,600 kg · AGAINST THE TRUCK IT REPLACES",
        "title": "One advance, one kill, one ruler nobody calibrated",
        "criterionNominal": cite(WS11, ["advance_kill", "criterion",
                                        "nominal_threshold_pct"], ".1f",
                                 suf="%"),
        "criterionCorner": cite(WS11, ["advance_kill", "criterion",
                                       "corner_threshold_pct"], ".1f",
                                suf="%"),
        "criterionText": cite(WS11, ["advance_kill", "criterion",
                                     "statement"], "str"),
        "rows": [
            {"id": "V1_on_VOLT-SUB", "title": "V1 Postal vs stock NPR-HD",
             "duty": "VOLT-SUB",
             "verdict": v("V1_on_VOLT-SUB", "verdict", "str", ""),
             "statusBadge": status_badge("FROZEN-PROVISIONAL"),
             "nominalMin": v("V1_on_VOLT-SUB", "nominal_margin_pct_min",
                             "+.2f"),
             "nominalGoverning": v("V1_on_VOLT-SUB",
                                   "nominal_margin_pct_min_governing_case",
                                   "str", ""),
             "worstCorner": v("V1_on_VOLT-SUB", "worst_corner_margin_pct",
                              "+.2f"),
             "worstCornerGoverning": v("V1_on_VOLT-SUB",
                                       "worst_corner_governing_case", "str",
                                       ""),
             "pessimistic": cite(WS11, rb + ["V1_on_VOLT-SUB",
                                             "pessimistic_min"], "+.2f",
                                 suf="%"),
             "flipPoint": cite(WS11, fp + ["V1_on_VOLT-SUB",
                                           "pct_ruler_fuel_error_to_draw"],
                               "+.2f", suf="%"),
             "flipDirection": cite(WS11, fp + ["V1_on_VOLT-SUB",
                                               "direction_that_would_"
                                               "overturn_the_verdict"], "str",
                                   "")},
            {"id": "V2_on_VOLT-REG", "title": "V2 Trucker vs stock NPR-HD",
             "duty": "VOLT-REG",
             "verdict": v("V2_on_VOLT-REG", "verdict", "str", ""),
             "statusBadge": status_badge("FROZEN-KILL"),
             "nominalMin": v("V2_on_VOLT-REG", "nominal_margin_pct_min",
                             "+.2f"),
             "nominalGoverning": v("V2_on_VOLT-REG",
                                   "nominal_margin_pct_min_governing_case",
                                   "str", ""),
             "worstCorner": v("V2_on_VOLT-REG", "worst_corner_margin_pct",
                              "+.2f"),
             "worstCornerGoverning": v("V2_on_VOLT-REG",
                                       "worst_corner_governing_case", "str",
                                       ""),
             "pessimistic": cite(WS11, rb + ["V2_on_VOLT-REG",
                                             "pessimistic_min"], "+.2f",
                                 suf="%"),
             "flipPoint": cite(WS11, fp + ["V2_on_VOLT-REG",
                                           "pct_ruler_fuel_error_to_draw"],
                               "+.2f", suf="%"),
             "flipDirection": cite(WS11, fp + ["V2_on_VOLT-REG",
                                               "direction_that_would_"
                                               "overturn_the_verdict"], "str",
                                   "")},
        ],
        "statusQuote": q(BASELINE,
                         "V1 Postal vs stock NPR: FROZEN-PROVISIONAL "
                         "ADVANCE, +20.11% nominal\nensemble-min per payload "
                         "tonne-km, worst corner +19.12%, robust to\nall "
                         "ruler-modelling brackets"),
        "killQuote": q(BASELINE,
                       "V2 Trucker: FROZEN-KILL, -7.93% headline, a draw at "
                       "the\nruler's pessimistic end, never reaching the "
                       "bar."),
        "esc1": {
            "calibrateOrderSatisfied": cite(WS11, ["interface_ws11", "ruler",
                                                   "anchor",
                                                   "calibrate_order_"
                                                   "satisfied"], "str"),
            "anchorName": cite(WS11, ["interface_ws11", "ruler", "anchor",
                                      "name"], "str"),
            "anchorLper100": cite(WS11, ["interface_ws11", "ruler", "anchor",
                                         "fourhk1_era", "l_per_100km"],
                                  ".2f", suf=" L/100 km"),
            "modelLper100": cite(WS11, ["interface_ws11", "ruler",
                                        "l_per_100km_VOLT_SUB", "median"],
                                 ".2f", suf=" L/100 km"),
            "worstResidual": cite(WS11, ["interface_ws11", "ruler", "anchor",
                                         "worst_residual_vs_model_pct"],
                                  "+.2f", suf="%"),
            "worstResidualGoverning": cite(WS11, ["interface_ws11", "ruler",
                                                  "anchor",
                                                  "worst_residual_governing_"
                                                  "case"], "str"),
        },
        "reworkUnverified": {
            "headline": "Round 2 reworked 24 findings. Nothing checked it.",
            "quote": q("PM_LOG.md",
                       "WS11's round-2 rework closes 3 blocking + 8 material "
                       "+ 13 minor findings and NOTHING WILL HAVE CHECKED "
                       "THAT WORK."),
        },
        "body": ("The two verdicts are not symmetric in their exposure. "
                 "V1's advance improves under every ruler-modelling "
                 "reversal, so its margin is a lower bound. V2's kill does "
                 "the opposite: bound the ruler by the ranges WS11's own "
                 "file declares and the kill becomes a draw. A lower bound "
                 "is the wrong guarantee for a kill."),
    }


def build_verdict_screen():
    return {
        "id": "verdict",
        "title": "Verdict wall",
        "kicker": "THE FRONT DOOR",
        "lede": ("A trial is only worth reading if it could have gone the "
                 "other way. Every card here is a criterion written before "
                 "the number existed, and the number that came back."),
        "cards": [card_g1(), card_ws8(), card_duty_flip(), card_ws11_pair()],
    }


# ===================================================================== 3
# Screen 2 — race mode. Record replay, paired seed, dual counters.

RACE_PAIRS = [
    {"id": "v1-sub-nominal", "vehicle": "V1", "key": "V1_on_VOLT-SUB",
     "duty": "VOLT-SUB", "case": "nominal", "seed": "11",
     "label": "V1 Postal vs stock NPR-HD",
     "sub": "VOLT-SUB · nominal · seed 11",
     "candTrace": "WS11_vehicle_zero_ruler/data/"
                  "trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv",
     "rulerTrace": "WS11_vehicle_zero_ruler/data/"
                   "trace_ruler_VOLT-SUB_nominal_seed11_10Hz.csv"},
    {"id": "v1-sub-cold", "vehicle": "V1", "key": "V1_on_VOLT-SUB",
     "duty": "VOLT-SUB", "case": "cold_-10C", "seed": "11",
     "label": "V1 Postal vs stock NPR-HD",
     "sub": "VOLT-SUB · cold -10 C · seed 11 · V1's governing corner",
     "candTrace": "WS11_vehicle_zero_ruler/data/"
                  "trace_V1_VOLT-SUB_cold_-10C_seed11_10Hz.csv",
     "rulerTrace": "WS11_vehicle_zero_ruler/data/"
                   "trace_ruler_VOLT-SUB_cold_-10C_seed11_10Hz.csv"},
    {"id": "v2-reg-nominal", "vehicle": "V2", "key": "V2_on_VOLT-REG",
     "duty": "VOLT-REG", "case": "nominal", "seed": "23",
     "label": "V2 Trucker vs stock NPR-HD",
     "sub": "VOLT-REG · nominal · seed 23",
     "candTrace": "WS11_vehicle_zero_ruler/data/"
                  "trace_V2_VOLT-REG_nominal_seed23_10Hz.csv",
     "rulerTrace": "WS11_vehicle_zero_ruler/data/"
                   "trace_ruler_VOLT-REG_nominal_seed23_10Hz.csv"},
    {"id": "v2-reg-climb", "vehicle": "V2", "key": "V2_on_VOLT-REG",
     "duty": "VOLT-REG", "case": "climb_10km_6pct", "seed": "23",
     "label": "V2 Trucker vs stock NPR-HD",
     "sub": "VOLT-REG · 10 km 6% climb · seed 23 · V2's governing corner",
     "candTrace": "WS11_vehicle_zero_ruler/data/"
                  "trace_V2_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv",
     "rulerTrace": "WS11_vehicle_zero_ruler/data/"
                   "trace_ruler_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv"},
]

RACE_COLS_CAND = ["t_s", "v_kmh", "grade_pct", "P_wheel_kW", "fuel_g_per_s",
                  "SOC"]
RACE_COLS_RULER = ["t_s", "v_kmh", "grade_pct", "P_wheel_kW", "fuel_g_per_s"]


def integrate_trace(rel, has_soc):
    """Rectangle-rule integration of the trace's own columns at its own
    0.1 s step. This is a DERIVED quantity and is labelled as one."""
    cols = RACE_COLS_CAND if has_soc else RACE_COLS_RULER
    _, _, c, rows = TR.read_trace(rel, want_columns=cols)
    ix = {k: i for i, k in enumerate(c)}
    fuel_g = 0.0
    dist_m = 0.0
    for r in rows:
        fuel_g += float(r[ix["fuel_g_per_s"]]) * DT_S
        dist_m += float(r[ix["v_kmh"]]) / 3.6 * DT_S
    out = {"rows": len(rows), "fuel_g": fuel_g, "km": dist_m / 1000.0,
           "kWh": fuel_g * LHV_KJ_PER_G / 3600.0,
           "litres": fuel_g / DENSITY_G_PER_L,
           "duration_s": float(rows[-1][ix["t_s"]])}
    out["kWh_per_km"] = out["kWh"] / out["km"]
    if has_soc:
        out["soc0"] = float(rows[0][ix["SOC"]])
        out["soc1"] = float(rows[-1][ix["SOC"]])
        # The pack's net bus-side contribution and the engine's own
        # implied efficiency, both from this file's own columns.
        _, _, c2, rows2 = TR.read_trace(rel, want_columns=[
            "P_batt_bus_kW", "P_shaft_eng_kW", "P_gen_bus_kW"])
        j = {k: i for i, k in enumerate(c2)}
        e_batt = 0.0
        e_shaft = 0.0
        e_gen = 0.0
        for r in rows2:
            e_batt += float(r[j["P_batt_bus_kW"]]) * DT_S / 3600.0
            e_shaft += float(r[j["P_shaft_eng_kW"]]) * DT_S / 3600.0
            e_gen += float(r[j["P_gen_bus_kW"]]) * DT_S / 3600.0
        out["e_batt_bus_kWh"] = e_batt
        out["e_shaft_kWh"] = e_shaft
        out["e_gen_bus_kWh"] = e_gen
        out["implied_bsfc"] = fuel_g / e_shaft if e_shaft else 0.0
        out["implied_gen_eta"] = e_gen / e_shaft if e_shaft else 0.0
    return out


def mechanisms_for(p):
    """The mechanisms the RECORD itself names for a live-vs-record gap.

    The charge-neutral figures below are WS4's own reference-seed example
    of the correction — a different vehicle and case from the one on
    screen — and are labelled as such at every point they appear, because
    a correctly cited number in the wrong place still misleads.
    """
    out = [{
        "id": "charge-neutral",
        "applies": "the candidate, on every case",
        "text": ("The record's fuel is charge-neutral: the pipeline "
                 "exports a raw and a corrected fuel mass side by side "
                 "and books the corrected one. The trace carries the raw "
                 "rate only, and this pack does not end where it "
                 "started."),
        "exampleLabel": ("An example of the correction, from a DIFFERENT "
                         "case: WS4's series_duty_v2 nominal reference "
                         "seed 23, mode (b). These are not this "
                         "dataset's numbers; they are the evidence that "
                         "the correction exists and is applied."),
        "rows": [
            {"k": "RAW FUEL, WS4 REF SEED",
             "v": cite(WS4, ["gate_g1", "nominal", "_raw_reference_seed",
                             "b", "fuel_g"], ",.1f", suf=" g")},
            {"k": "CORRECTED FUEL, WS4 REF SEED",
             "v": cite(WS4, ["gate_g1", "nominal", "_raw_reference_seed",
                             "b", "fuel_corrected_g"], ",.1f", suf=" g")},
            {"k": "SOC DRIFT CORRECTED FOR, WS4 REF SEED",
             "v": cite(WS4, ["gate_g1", "nominal", "_raw_reference_seed",
                             "b", "soc_drift_kwh_cells"], ".4f",
                       suf=" kWh")},
        ],
    }]
    if p["case"] == "climb_10km_6pct":
        out.append({
            "id": "unserved",
            "applies": "the ruler, on this corner only",
            "text": ("On the 10 km climb the ruler cannot hold the "
                     "demanded speed. The record charges it for the work "
                     "it could not do; the trace's speed column carries "
                     "the demand, so the live integral does not."),
            "exampleLabel": "These figures are this dataset's own.",
            "rows": [
                {"k": "UNSERVED WHEEL ENERGY",
                 "v": cite(WS11, ["interface_ws11",
                                  "capability_and_limit_worst_case",
                                  "V2_on_VOLT-REG",
                                  "ruler_worst_unserved_wheel_kWh"], ".4f",
                           suf=" kWh")},
                {"k": "SECONDS THE RULER WAS CAPABILITY-LIMITED",
                 "v": cite(WS11, ["interface_ws11",
                                  "capability_and_limit_worst_case",
                                  "V2_on_VOLT-REG",
                                  "ruler_worst_capability_infeasible_s"],
                           ".1f", suf=" s")},
            ],
        })
    return out


def build_race_screen(trace_index):
    pairs = []
    for p in RACE_PAIRS:
        base = ["results", p["key"], p["case"]]
        pay_r = resolve(load_json(WS11), base + ["payload_kg_ruler"])
        pay_c = resolve(load_json(WS11), base + ["payload_kg_candidate"])

        di_c = integrate_trace(p["candTrace"], True)
        di_r = integrate_trace(p["rulerTrace"], False)

        d_perkm_margin = 100.0 * (di_r["kWh_per_km"] - di_c["kWh_per_km"]) \
            / di_r["kWh_per_km"]
        rp_r = di_r["kWh"] / (di_r["km"] * pay_r / 1000.0)
        rp_c = di_c["kWh"] / (di_c["km"] * pay_c / 1000.0)
        d_perpay_margin = 100.0 * (rp_r - rp_c) / rp_r

        rec_km_c = cite(WS11, base + ["candidate", "per_km", "per_seed",
                                      p["seed"]], ".4f", suf=" kWh/km")
        rec_km_r = cite(WS11, base + ["ruler", "per_km", "per_seed",
                                      p["seed"]], ".4f", suf=" kWh/km")
        rec_pk = cite(WS11, base + ["margin_pct_per_km_paired", "per_seed",
                                    p["seed"]], "+.2f", suf="%")
        rec_pp = cite(WS11, base + ["margin_pct_per_payload_tkm_paired",
                                    "per_seed", p["seed"]], "+.2f", suf="%")

        soc_drift_kwh = None
        if "soc0" in di_c:
            usable = 11.083608  # declared in the trace's own header line
            soc_drift_kwh = (di_c["soc0"] - di_c["soc1"]) * usable

        rec_fuel_g_c = rec_km_c["v"] * di_c["km"] * 3600.0 / LHV_KJ_PER_G
        recon_c = 100.0 * (di_c["fuel_g"] - rec_fuel_g_c) / rec_fuel_g_c
        rec_fuel_g_r = rec_km_r["v"] * di_r["km"] * 3600.0 / LHV_KJ_PER_G
        recon_r = 100.0 * (di_r["fuel_g"] - rec_fuel_g_r) / rec_fuel_g_r

        pairs.append({
            "id": p["id"],
            "label": p["label"],
            "sub": p["sub"],
            "vehicle": p["vehicle"],
            "duty": p["duty"],
            "case": p["case"],
            "seed": p["seed"],
            "candTraceId": trace_index[p["candTrace"]],
            "rulerTraceId": trace_index[p["rulerTrace"]],
            "payloadRuler": cite(WS11, base + ["payload_kg_ruler"], ",.0f",
                                 suf=" kg"),
            "payloadCand": cite(WS11, base + ["payload_kg_candidate"], ",.0f",
                                suf=" kg"),
            "massRuler": cite(WS11, base + ["mass_kg_ruler"], ",.0f",
                              suf=" kg"),
            "record": {
                "rulerPerKm": rec_km_r,
                "candPerKm": rec_km_c,
                "rulerPerPayload": cite(WS11, base + ["ruler",
                                                      "per_payload_tkm",
                                                      "per_seed", p["seed"]],
                                        ".4f", suf=" kWh/t-km"),
                "candPerPayload": cite(WS11, base + ["candidate",
                                                     "per_payload_tkm",
                                                     "per_seed", p["seed"]],
                                       ".4f", suf=" kWh/t-km"),
                "marginPerKm": rec_pk,
                "marginPerPayload": rec_pp,
                "marginPerKmEnsembleMin": cite(
                    WS11, base + ["margin_pct_per_km_paired", "min"], "+.2f",
                    suf="%"),
                "marginPerPayloadEnsembleMin": cite(
                    WS11, base + ["margin_pct_per_payload_tkm_paired", "min"],
                    "+.2f", suf="%"),
                "gapPp": lit(rec_pk["v"] - rec_pp["v"], "+.2f", suf=" pp",
                             tier=TIER_DERIVED,
                             source="margin_pct_per_km_paired.per_seed[%s] "
                                    "minus margin_pct_per_payload_tkm_paired."
                                    "per_seed[%s], both from %s -> %s"
                                    % (p["seed"], p["seed"], WS11,
                                       " -> ".join(base))),
            },
            "derived": {
                "_basis": ("rectangle-rule integration of the trace's own "
                           "fuel_g_per_s and v_kmh columns at the file's own "
                           "0.1 s step, LHV 42.8 kJ/g "
                           "(WS4_genset/ws4_models.py:26)"),
                "rulerKm": lit(di_r["km"], ".3f", suf=" km",
                               source=p["rulerTrace"] + " -> v_kmh"),
                "candKm": lit(di_c["km"], ".3f", suf=" km",
                              source=p["candTrace"] + " -> v_kmh"),
                "rulerFuelG": lit(di_r["fuel_g"], ",.1f", suf=" g",
                                  source=p["rulerTrace"] + " -> fuel_g_per_s"),
                "candFuelG": lit(di_c["fuel_g"], ",.1f", suf=" g",
                                 source=p["candTrace"] + " -> fuel_g_per_s"),
                "rulerLitres": lit(di_r["litres"], ".2f", suf=" L",
                                   source="fuel_g / 832 g/L "
                                          "(ws11_params.py:37)"),
                "candLitres": lit(di_c["litres"], ".2f", suf=" L",
                                  source="fuel_g / 832 g/L "
                                         "(ws11_params.py:37)"),
                "rulerPerKm": lit(di_r["kWh_per_km"], ".4f", suf=" kWh/km",
                                  source="integrated"),
                "candPerKm": lit(di_c["kWh_per_km"], ".4f", suf=" kWh/km",
                                 source="integrated"),
                "rulerPerPayload": lit(rp_r, ".4f", suf=" kWh/t-km",
                                       source="integrated / payload of "
                                              "record"),
                "candPerPayload": lit(rp_c, ".4f", suf=" kWh/t-km",
                                      source="integrated / payload of "
                                             "record"),
                "marginPerKm": lit(d_perkm_margin, "+.2f", suf="%",
                                   source="integrated"),
                "marginPerPayload": lit(d_perpay_margin, "+.2f", suf="%",
                                        source="integrated"),
                "gapPp": lit(d_perkm_margin - d_perpay_margin, "+.2f",
                             suf=" pp", source="integrated"),
                "socStart": lit(di_c["soc0"] * 100.0, ".2f", suf="%",
                                source=p["candTrace"] + " -> SOC, first row"),
                "socEnd": lit(di_c["soc1"] * 100.0, ".2f", suf="%",
                              source=p["candTrace"] + " -> SOC, last row"),
                "socDriftKWh": lit(soc_drift_kwh, "+.3f", suf=" kWh",
                                   source="(SOC first - SOC last) x 11.083608 "
                                          "kWh usable, the pack size declared "
                                          "in the trace's own header line"),
            },
            "reconciliation": {
                "headline": "The live counter and the number of record do "
                            "not agree. Here is by how much, and what the "
                            "record says about why.",
                "rulerDeltaPct": lit(recon_r, "+.3f", suf="%",
                                     source="live integral vs the fuel "
                                            "implied by the record's own "
                                            "per-seed kWh/km over the same "
                                            "distance"),
                "candDeltaPct": lit(recon_c, "+.3f", suf="%",
                                    source="live integral vs the fuel "
                                           "implied by the record's own "
                                           "per-seed kWh/km over the same "
                                           "distance"),
                "candNetPackBus": lit(di_c["e_batt_bus_kWh"], "+.3f",
                                      suf=" kWh",
                                      source=p["candTrace"]
                                      + " -> P_batt_bus_kW, integrated"),
                "candImpliedBsfc": lit(di_c["implied_bsfc"], ".1f",
                                       suf=" g/kWh",
                                       source="this file's own fuel_g_per_s "
                                              "over its own P_shaft_eng_kW"),
                "candImpliedGenEta": lit(di_c["implied_gen_eta"], ".4f",
                                         source="this file's own "
                                                "P_gen_bus_kW over its own "
                                                "P_shaft_eng_kW"),
                "mechanisms": mechanisms_for(p),
                "residual": ("Those two mechanisms do not close the gap "
                             "completely. The exhibit states the measured "
                             "difference and stops there rather than "
                             "inventing an explanation; the residual is "
                             "recorded in REPORT_WS12.md as an open item "
                             "against a round that was never adjudicated."),
            },
        })

    v2 = ["results", "V2_on_VOLT-REG", "nominal"]
    return {
        "id": "race",
        "title": "Race mode",
        "kicker": "RECORD REPLAY · PAIRED SEED",
        "lede": ("Two trucks, one duty, one seed, one road. Two counters "
                 "run side by side: fuel per kilometre, and fuel per tonne "
                 "of freight per kilometre. Watch them come apart."),
        "headline": {
            "perKm": cite(WS11, v2 + ["margin_pct_per_km_paired", "min"],
                          "+.2f", suf="%"),
            "perPayload": cite(WS11, v2 + ["margin_pct_per_payload_tkm_"
                                           "paired", "min"], "+.2f", suf="%"),
            "freightGiven": cite(WS11, ["one_factor", "rows",
                                        "V2_on_VOLT-REG",
                                        "mass_payload_denominator",
                                        "cost_pp"], ".2f", suf=" pp"),
            "text": ("V2 wins on the road and loses on the invoice. It is "
                     "the same fuel, the same kilometres and the same "
                     "second-by-second record — only the denominator "
                     "changes."),
            "trapQuote": q("LEAD_HANDOVER.md",
                           "at fixed gross weight every powertrain kilogram "
                           "displaces payload 1:1, so the metric of record "
                           "is fuel energy per PAYLOAD tonne-km"),
        },
        "pairs": pairs,
        "semi": build_semi_panel(),
        "counterNote": ("The two live counters are DERIVED: they integrate "
                        "the trace's own fuel_g_per_s and v_kmh columns in "
                        "front of you. The numbers of record beside them "
                        "are the workstream's charge-neutral figures for the "
                        "same seed. Where the two differ, the difference is "
                        "printed rather than hidden — see the "
                        "reconciliation strip."),
    }


WS9_CANDS = ("S6", "S5-13L", "S7", "S4p", "S5")


def build_semi_panel():
    rows = []
    for c in WS9_CANDS:
        ic = ["interface_ws9", "candidates", c]
        rows.append({
            "id": c,
            "title": cite(WS9, ic + ["title"], "str"),
            "verdict": cite(WS9, ic + ["verdict"], "str"),
            "statusBadge": status_badge(
                "FROZEN-KILL" if resolve(load_json(WS9), ic + ["verdict"])
                == "KILL" else "FROZEN-PROVISIONAL"),
            "designMin": cite(WS9, ic + ["GH-REG-165",
                                         "margin_vs_ruler_pct", "min"],
                              "+.2f", suf="%"),
            "controlMin": cite(WS9, ic + ["LH-520", "margin_vs_ruler_pct",
                                          "min"], "+.2f", suf="%"),
            "worstCorner": cite(WS9, ic + ["worst_case_margin_pct_design_"
                                           "duty", "value"], "+.2f", suf="%"),
            "worstCornerCase": cite(WS9, ic + ["worst_case_margin_pct_design_"
                                               "duty", "governing_case"],
                                    "str"),
            "payload": cite(WS9, ic + ["payload_kg"], ",.0f", suf=" kg"),
        })
    return {
        "id": "semi",
        "title": "The semi race — wired, not replayed",
        "statusBadge": status_badge("FROZEN-PROVISIONAL"),
        "statusQuote": q(BASELINE,
                         "R53 — The Fable adjudication of WS9 is CANCELLED. "
                         "WS9's four ADVANCE\nverdicts remain "
                         "FROZEN-PROVISIONAL, unadjudicated at Fable tier,"),
        "criterionNominal": cite(WS9, ["interface_ws9", "advance_kill",
                                       "nominal_pct"], ".1f", suf="%"),
        "criterionCorner": cite(WS9, ["interface_ws9", "advance_kill",
                                      "every_corner_pct"], ".1f", suf="%"),
        "metric": cite(WS9, ["interface_ws9", "advance_kill", "metric"],
                       "str"),
        "designDuty": cite(WS9, ["interface_ws9", "duties", "design"], "str"),
        "controlDuty": cite(WS9, ["interface_ws9", "duties", "control"],
                            "str"),
        "gatingRule": cite(WS9, ["interface_ws9", "duties", "gating"], "str"),
        "rows": rows,
        "noReplay": {
            "headline": "No dual counter can be replayed for the semi.",
            "reason": ("WS9's 10 Hz traces carry four commanded force "
                       "channels and no fuel column at all. The trace's own "
                       "header says so; the exhibit will not synthesise the "
                       "missing column, so this dataset renders as a verdict "
                       "panel and not as a race."),
            "traceHeaderQuote": q(
                "WS9_vehicle_one_wave2/data/"
                "trace_S6_GH-REG-165_nominal_seed8101_10Hz.csv",
                "electrical quantities are NOT in this file; they are "
                "per-candidate dispatch and live in results_ws9.json"),
            "tracesOnDisk": [
                ff("WS9_vehicle_one_wave2/data/"
                   "trace_S6_GH-REG-165_nominal_seed8101_10Hz.csv"),
                ff("WS9_vehicle_one_wave2/data/"
                   "trace_S0R_GH-REG-165_nominal_seed8101_10Hz.csv"),
            ],
            "alsoAbsent": ("WS9 exports no per-km MARGIN either — only "
                           "per-km levels — so the left-hand counter has no "
                           "number of record to resolve to."),
        },
        "openFindings": q(BASELINE,
                          "with the Opus pre-adjudication's findings "
                          "(PRE-B1..B3) on the record\nagainst them and "
                          "R46's trip-time consequence for S5-13L recorded "
                          "as\nexpected-but-not-executed."),
    }


# ===================================================================== 4
# Screen 3 — round history. The failure record.

ADJUDICATIONS = [
    # (workstream, round, findings file, verdict quote (verbatim),
    #  blocking, material, minor, is-first-pass)
    ("WS2", "r1", "WS2_traction_motor/FINDINGS_WS2_r1.md",
     "**Verdict: no blocking findings. Two material findings (WS2-F1, "
     "WS2-F2), five minor.", 0, 2, 5, True),
    ("WS2", "r2", "WS2_traction_motor/FINDINGS_WS2_r2.md",
     "**Verdict: no blocking findings. One NEW material finding (WS2-F8:",
     0, 1, 2, False),
    ("WS2", "r3", "WS2_traction_motor/FINDINGS_WS2_r3.md",
     "**Verdict: no blocking findings. All three round-2 findings (F8, F9, "
     "F10) are genuinely resolved", 0, 1, 1, False),
    ("WS2", "r4", "WS2_traction_motor/FINDINGS_WS2_r4.md",
     "**Verdict: no blocking or material findings.**", 0, 0, 2, False),
    ("WS3", "r1", "WS3_battery/FINDINGS_WS3_r1.md",
     "Two findings of consequence (one blocking, one material), then minors.",
     1, 1, 4, True),
    ("WS3", "r2", "WS3_battery/FINDINGS_WS3_r2.md",
     "**No blocking or material findings.**", 0, 0, 2, False),
    ("WS4", "r1", "WS4_genset/FINDINGS_WS4_r1.md",
     "**Verdict: no blocking findings. Two material findings (F1, F2) and\n"
     "five minor findings.", 0, 2, 5, True),
    ("WS4", "r2", "WS4_genset/FINDINGS_WS4_r2.md",
     "**Verdict: no blocking or material findings. No new findings of any\n"
     "severity.", 0, 0, 0, False),
    ("WS4", "r3", "WS4_genset/FINDINGS_WS4_r3.md",
     "**Verdict: no blocking findings. One material finding (F1) and four\n"
     "minor findings (F2\u2013F5).", 0, 1, 4, False),
    ("KX", "r1", "WS4_genset/FINDINGS_KX_r1.md",
     "**NOT CLEAN. Two BLOCKING findings, three MATERIAL, eight MINOR.**",
     2, 3, 8, True),
    ("KX", "r2", "WS4_genset/FINDINGS_KX_r2.md",
     "**NOT CLEAN. No blocking findings. Three MATERIAL, four MINOR.**",
     0, 3, 4, False),
    ("KX", "r3", "WS4_genset/FINDINGS_KX_r3.md",
     "**NOT CLEAN. One BLOCKING finding, three MATERIAL, six MINOR.**",
     1, 3, 6, False),
    ("WS8", "r1", "WS8_semi_architecture/FINDINGS_WS8_r1.md",
     "**Verdict: NOT CLEAN. Two blocking findings, five material, six "
     "minor.**", 2, 5, 6, True),
    ("WS8", "r2", "WS8_semi_architecture/FINDINGS_WS8_r2.md",
     "**Verdict: NOT CLEAN. One blocking, four material, seven minor.**",
     1, 4, 7, False),
    ("WS8", "r3", "WS8_semi_architecture/FINDINGS_WS8_r3.md",
     "**Verdict: NOT CLEAN. Two blocking, six material, twelve minor.**",
     2, 6, 12, False),
    ("WS9", "pre-r1", "WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md",
     "**RESULT: NOT CLEAN. Four blocking, six material, nine minor.**",
     4, 6, 9, True),
    ("WS11", "r1", "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md",
     "**Verdict on the round: NOT CLEAN \u2014 3 blocking, 8 material, 13 "
     "minor.**", 3, 8, 13, True),
]

WORKSTREAM_ROWS = [
    {"ws": "WS1", "name": "Loads and duty cycles", "rounds": 1,
     "adjudications": 0,
     "note": "Closed by lead ratification. No findings file exists in the "
             "repository and PM_LOG.md carries no WS1 entry.",
     "statusText": "CLOSED (BASELINE_v3)"},
    {"ws": "WS2", "name": "Traction motor", "rounds": 4, "adjudications": 4,
     "note": "NOT CONVERGED at r3 after three rounds; reopened by a "
             "lead-directed r4 which came back clean.",
     "statusText": "CLOSED-RATIFIED (BASELINE_v3)"},
    {"ws": "WS3", "name": "Battery pack", "rounds": 2, "adjudications": 2,
     "note": "Converged clean at r2.",
     "statusText": "CLOSED-RATIFIED (BASELINE_v2)"},
    {"ws": "WS4", "name": "Genset and Gate G1", "rounds": 3,
     "adjudications": 3,
     "note": "G1's kill clause executed on the pre-committed criterion.",
     "statusText": "RATIFIED EXCEPT G1-R, then G1 EXECUTED (BASELINE_v3)"},
    {"ws": "KX", "name": "Genset KX round", "rounds": 3, "adjudications": 3,
     "note": "Three rework rounds exhausted, final round still not clean. "
             "A fourth round was authorised and stopped by the freeze.",
     "statusText": "NOT CONVERGED"},
    {"ws": "WS5", "name": "Supervisory controls", "rounds": 1,
     "adjudications": 0,
     "note": "Gate PASS. The only workstream in the program with ZERO "
             "adjudication rounds. Its worker wrote its own weakness list "
             "because no adversarial reviewer was coming.",
     "statusText": "GATED BUT UNADJUDICATED"},
    {"ws": "WS8", "name": "Semi architecture", "rounds": 3,
     "adjudications": 3,
     "note": "r3 NOT CLEAN; r4 was ordered and never run.",
     "statusText": "KILLED (final); numbers FROZEN-PROVISIONAL at r3"},
    {"ws": "WS9", "name": "Vehicle One wave two", "rounds": 2,
     "adjudications": 0,
     "note": "Only a pre-adjudication exists, and it disposes of nothing. "
             "The adjudication of record was never run and is cancelled.",
     "statusText": "FROZEN-PROVISIONAL, unadjudicated at Fable tier"},
    {"ws": "WS11", "name": "Vehicle Zero ruler trial", "rounds": 2,
     "adjudications": 1,
     "note": "r1 NOT CLEAN with 24 findings. r2 reworked all of them and "
             "was never checked.",
     "statusText": "FROZEN-PROVISIONAL ADVANCE / FROZEN-KILL"},
]


# The severity counts on the round-history screen are NOT transcribed.
# They are parsed out of each findings file at build time, and the numbers
# declared in ADJUDICATIONS are an assertion the build must satisfy rather
# than the source. `exhibit_verify.py` re-parses each file independently
# with its own implementation and asserts the same three integers.
WORD_N = {
    "no": 0, "none": 0, "zero": 0, "one": 1, "two": 2, "three": 3,
    "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15,
}

# WS3's two findings files state severities on the finding headings rather
# than in the verdict line, so they are counted there instead.
HEADING_COUNTED = {
    "WS3_battery/FINDINGS_WS3_r1.md":
        r"WS3-r1-[A-Z]\d+\s*[—–-]\s*(BLOCKING|MATERIAL|MINOR)",
    "WS3_battery/FINDINGS_WS3_r2.md":
        r"WS3-r2-[A-Z]\d+\s*[—–-]\s*(BLOCKING|MATERIAL|MINOR)",
}


def parse_severities(rel):
    """Read the three severity counts out of a findings file.

    Two methods, chosen per file and named in the citation: count the
    severity-tagged finding headings, or read the verdict line's own words.
    """
    import re
    body = text_of(rel)
    if rel in HEADING_COUNTED:
        got = {"BLOCKING": 0, "MATERIAL": 0, "MINOR": 0}
        for m in re.finditer(HEADING_COUNTED[rel], body):
            got[m.group(1)] += 1
        return (got["BLOCKING"], got["MATERIAL"], got["MINOR"],
                "counted from the severity-tagged finding headings in "
                + rel)

    head = "\n".join(body.splitlines()[:40])
    flat = " ".join(head.split())

    # "No new findings of any severity" zeroes all three at once.
    if re.search(r"\b[Nn]o\s+new\s+findings\s+of\s+any\s+severity\b", flat):
        return (0, 0, 0,
                "read from the verdict line of " + rel
                + " ('no new findings of any severity')")

    def one(word):
        # "no blocking or material findings" zeroes both at once.
        m = re.search(r"\b([Nn]o)\s+blocking\s+or\s+material\b", flat)
        if m and word in ("blocking", "material"):
            return 0
        m = re.search(r"\b(\w+)\s+(?:NEW\s+|new\s+)?" + word, flat,
                      re.IGNORECASE)
        if not m:
            return None
        tok = m.group(1)
        if tok.isdigit():
            return int(tok)
        return WORD_N.get(tok.lower())

    return (one("blocking"), one("material"), one("minor"),
            "read from the verdict line of " + rel)


def build_rounds_screen():
    adj = []
    for ws, rnd, path, quote, b, m, mi, first in ADJUDICATIONS:
        gb, gm, gmi, how = parse_severities(path)
        if (gb, gm, gmi) != (b, m, mi):
            raise ValueError(
                "%s: parsed severities %r do not match the declared %r. "
                "The parse is the source; fix the declaration or the "
                "parse, never the screen." % (path, (gb, gm, gmi),
                                              (b, m, mi)))
        adj.append({
            "ws": ws, "round": rnd, "file": path,
            "firstPass": bool(first),
            "verdictQuote": q(path, quote),
            "countMethod": how,
            "blocking": lit(gb, "d", tier=TIER_RECORD, source=how),
            "material": lit(gm, "d", tier=TIER_RECORD, source=how),
            "minor": lit(gmi, "d", tier=TIER_RECORD, source=how),
            "notClean": gb + gm > 0,
            "fileFact": ff(path),
        })

    firsts = [a for a in adj if a["firstPass"]]
    firsts_with_defects = [a for a in firsts
                           if a["blocking"]["v"] + a["material"]["v"] > 0]

    return {
        "id": "rounds",
        "title": "Round history",
        "kicker": "THE FAILURE RECORD",
        "lede": ("The strongest evidence this program produced is not a "
                 "truck. It is the list of times the review found something "
                 "the workstream had missed — including in the lead's own "
                 "work — and the one time the review was removed."),
        "workstreams": WORKSTREAM_ROWS,
        "adjudications": adj,
        "gap": build_the_gap(),
        "kx": build_kx_card(),
        "defectRate": {
            "headline": "First-pass adjudications that found a blocking or "
                        "material defect",
            "firstPassRounds": lit(len(firsts), "d", tier=TIER_DERIVED,
                                   source="count of first-pass rounds with a "
                                          "findings file on disk"),
            "firstPassWithDefects": lit(
                len(firsts_with_defects), "d", tier=TIER_DERIVED,
                source="count of those whose verdict line records at least "
                       "one blocking or material finding"),
            "programClaim": q(BASELINE,
                              "five-for-five first-pass defect detection, "
                              "including\n   the lead's own errors (ratified "
                              "by its record)."),
            "programClaimRule": q("BASELINE_v5.md",
                                  "first-pass base rate in this program is "
                                  "five for five material-or-\nblocking"),
            "twoReadings": [
                {"label": "five for five",
                 "scope": "the five workstream first-pass rounds — WS2, WS3, "
                          "WS4, WS8, WS11",
                 "source": "BASELINE_v7_FREEZE.md claim 8, and R37 in "
                           "BASELINE_v5.md"},
                {"label": "seven for seven",
                 "scope": "the same five plus the KX round's own first pass "
                          "and the WS9 pre-adjudication",
                 "source": "WS12_exhibit/ASSIGNMENT.md, this exhibit's own "
                           "specification"},
            ],
            "discrepancyNote": ("The program record and this exhibit's "
                                "assignment disagree on the denominator. "
                                "Both readings are printed with their "
                                "scope; neither is promoted over the other, "
                                "and the seven rows they are counted from "
                                "are in the table above. The discrepancy is "
                                "recorded in REPORT_WS12.md."),
            "notCovered": ("Neither figure covers WS1 or WS5: neither "
                           "workstream was ever adjudicated, so neither can "
                           "appear in a detection rate."),
        },
        "neverAdjudicated": {
            "headline": "Rounds that ran and were never adjudicated",
            "rows": [
                {"ws": "WS1", "round": "r1",
                 "why": "No adjudication was ever run and no findings file "
                        "exists. LEAD_HANDOVER.md's doctrine D5 claims the "
                        "first-pass range covers WS1-WS4; the disk does not "
                        "support the WS1 end of that range."},
                {"ws": "WS5", "round": "r1",
                 "why": "Gate PASS, adjudication cut at 07:40, then frozen."},
                {"ws": "WS11", "round": "r2",
                 "why": "Gate PASS, adjudication cut at 07:40, then frozen. "
                        "24 findings closed and unchecked."},
                {"ws": "WS9", "round": "r1 and the r3-concordant re-run",
                 "why": "The Fable adjudication of record was never run and "
                        "is cancelled by R53."},
            ],
            "orderedNeverRun": ("Ordered and never run, so not counted as "
                                "rounds at all: KX r4, WS8 r4, WS9 r2, "
                                "WS11 r3, and R43(a)-(d) on V1's advance."),
        },
    }


def build_the_gap():
    """The 07:40 gap. The control condition. Rendered plainly."""
    return {
        "id": "gap",
        "kicker": "2026-08-31 · 07:40",
        "title": "The control condition",
        "statusBadge": status_badge("FROZEN-PROVISIONAL"),
        "logQuote": q("PM_LOG.md",
                      "PRINCIPAL DECISION - ADJUDICATIONS CUT FOR WS11 AND "
                      "WS5 | The principal (Vali), asked directly how to "
                      "close the night, chose: let WS11 r2 and WS5 finish, "
                      "GATE them, SKIP their adjudication rounds, and write "
                      "NIGHT_REPORT.md marking both GATED BUT UNADJUDICATED."),
        "consequenceQuote": q("PM_LOG.md",
                              "Consequence stated plainly for the lead: "
                              "WS11's round-2 rework closes 3 blocking + 8 "
                              "material + 13 minor findings and NOTHING WILL "
                              "HAVE CHECKED THAT WORK."),
        "gateQuote": q("PM_LOG.md",
                       "a gate PASS on r2 is evidence of reproducibility "
                       "only and is NOT evidence the findings are closed."),
        "nightReportQuote": q("NIGHT_REPORT.md",
                              "**ADJUDICATION NOT RUN.** Cut by the "
                              "principal at 07:40 when closing the\nshift."),
        "blocking": lit(3, "d", tier=TIER_RECORD,
                        source="PM_LOG.md 2026-08-31 07:40 entry, and "
                               "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md"),
        "material": lit(8, "d", tier=TIER_RECORD,
                        source="PM_LOG.md 2026-08-31 07:40 entry, and "
                               "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md"),
        "minor": lit(13, "d", tier=TIER_RECORD,
                     source="PM_LOG.md 2026-08-31 07:40 entry, and "
                            "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md"),
        "body": ("Every other card in this exhibit shows the structure "
                 "working. This one shows what happens when it is removed, "
                 "and it is the only card here that is an experiment rather "
                 "than a result. WS11's round 1 had passed a byte-stable "
                 "mechanical gate and was then found NOT CLEAN, with the "
                 "central robustness claim about its own kill falsified. "
                 "Round 2 reworked all twenty-four findings and passed the "
                 "same mechanical gate. Nothing adversarial has read it. "
                 "The right way to hold round 2's numbers is therefore the "
                 "way round 1's numbers deserved to be held before the "
                 "adjudicator opened the file."),
        "controlLine": ("Remove the adversarial reader and the output is "
                        "immediately unverified. That is the finding."),
    }


def build_kx_card():
    """KX: NOT CONVERGED, and a blocking number that is not exported."""
    probe = ["series_duty_v2", "r6_rating_family_probe", "cases",
             "r6_rating_corner_full"]
    ws4 = load_json(WS4)
    per_seed = resolve(ws4, probe + ["per_seed"])
    seed_max = max(per_seed, key=lambda s: per_seed[s]["engine_reject_2min_"
                                                       "max_kW"])
    share_path = ["heat_ledger_ws6", "series_duty_v2_nominal_cycle_average",
                  "radiator_package_share"]
    share = resolve(ws4, share_path)
    reject = resolve(ws4, probe + ["per_seed", seed_max,
                                   "engine_reject_2min_max_kW"])
    r6_kW = reject * share
    design = cite(WS4, ["heat_ledger_ws6",
                        "series_duty_v2_transient_vs_R20_design_point",
                        "r20_design_point_radiator_package_kW"], ".3f",
                  suf=" kW")
    exceed = 100.0 * (r6_kW - design["v"]) / design["v"]
    return {
        "id": "kx",
        "kicker": "KX ROUND · THREE ROUNDS, NEVER CLEAN",
        "title": "NOT CONVERGED",
        "statusBadge": status_badge("NOT CONVERGED"),
        "statusQuote": q(BASELINE,
                         "KX: NOT CONVERGED after three rounds (radiator "
                         "sizing case\n103.5 vs 95.0 kW)."),
        "dispositionQuote": q("PM_PACKET_KX.md",
                              "**STATUS: NOT CONVERGED.** Three rework "
                              "rounds exhausted; the final\nadjudication "
                              "round is not clean."),
        "logQuote": q("PM_LOG.md",
                      "3 rework rounds exhausted, final round not clean. "
                      "Workstream stopped per the standing mandate. NO "
                      "FOURTH ROUND RUN."),
        "findingQuote": q("WS4_genset/FINDINGS_KX_r3.md",
                          "The R6 corner exceeds R20's design point by "
                          "**+8.95 % on the 2-minute rolling\nwindow** - and "
                          "by the same margin on the instantaneous peak - "
                          "**at the same\n+45 °C ambient the design "
                          "point is stated in**."),
        "designPoint": design,
        "designPointAmbient": cite(WS4, ["heat_ledger_ws6",
                                         "series_duty_v2_transient_vs_R20_"
                                         "design_point",
                                         "r20_design_point_air_"
                                         "temperature_C"], ".1f", suf=" C"),
        "r6Reject": cite(WS4, probe + ["per_seed", seed_max,
                                       "engine_reject_2min_max_kW"], ".5f",
                         suf=" kW"),
        "radiatorShare": cite(WS4, share_path, ".2f"),
        "r6Radiator": lit(r6_kW, ".3f", suf=" kW", tier=TIER_DERIVED,
                          source=("%s -> %s -> per_seed -> %s -> "
                                  "engine_reject_2min_max_kW (max over the "
                                  "8-seed set) x the declared radiator "
                                  "package share"
                                  % (WS4, " -> ".join(probe), seed_max))),
        "exceedance": lit(exceed, "+.2f", suf="%", tier=TIER_DERIVED,
                          source="the derived R6-corner radiator package "
                                 "against the exported R20 design point"),
        "corner": cite(WS4, probe + ["condition"], "str"),
        "theCitationPoint": {
            "headline": "This exhibit cannot cite the blocking number, and "
                        "that is the finding.",
            "body": ("Every other figure on these screens resolves to a "
                     "file and a JSON path. This one does not: the R6 "
                     "corner's radiator package is not exported anywhere in "
                     "results_ws4.json. It is reachable only by taking the "
                     "declared radiator-package share of a per-seed engine "
                     "rejection buried in a probe block. That is exactly "
                     "what makes R3-B1 blocking — the number that overturns "
                     "the workstream's own conclusion is not in the "
                     "interface its consumer would read. It is shown here "
                     "as DERIVED, with its two record inputs named, and it "
                     "is the only number on the verdict-bearing screens "
                     "that had to be."),
            "consumerQuote": q("PM_PACKET_KX.md",
                               "**WS6 has not run and R3-B1 lands squarely "
                               "on what it would consume.**"),
        },
    }


# ===================================================================== 5
# Screen 4 — the simulator. TRACE_SCHEMA replay.

SIM_TRACES = [
    {"id": "ws5-v1-sub", "rel": "WS5_controls/data/"
                                "trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv",
     "label": "V1 Postal · VOLT-SUB · nominal · seed 11",
     "map": "bsfc_map_V1_candidate.csv"},
    {"id": "ws5-v2-reg", "rel": "WS5_controls/data/"
                                "trace_V2_VOLT-REG_nominal_seed23_10Hz.csv",
     "label": "V2 Trucker · VOLT-REG · nominal · seed 23",
     "map": "bsfc_map_V2_candidate.csv"},
]

SIM_COLUMNS = [
    "t_s", "x_m", "v_kmh", "grade_pct", "z_m", "P_wheel_kW", "fuel_g_per_s",
    "fuel_cum_g", "P_friction_brake_kW", "trip_time_flag", "N_eng_rpm",
    "T_eng_Nm", "P_shaft_eng_kW", "engine_state", "P_gen_bus_kW",
    "P_bus_load_kW", "P_motor_bus_kW", "P_motor_mech_kW", "P_regen_pack_kW",
    "P_heater_kW", "P_resistor_kW", "soc_pct", "T_pack_C", "genset_state",
    "P_batt_bus_kW",
]

# Every trace file in the repository, for the conformance registry.
ALL_TRACES = [
    ("WS1", "WS1_loads_duty_cycles/data/trace_VOLT-SUB_V1_10Hz.csv"),
    ("WS1", "WS1_loads_duty_cycles/data/trace_VOLT-REG_V2_10Hz.csv"),
    ("WS4", "WS4_genset/data/trace_series_duty_v2_nominal_seed23_10Hz.csv"),
    ("WS4", "WS4_genset/data/"
            "trace_series_duty_v2_alt2000m_45C_seed23_10Hz.csv"),
    ("WS4", "WS4_genset/data/trace_series_duty_v2_cda_5.4_seed23_10Hz.csv"),
    ("WS5", "WS5_controls/data/trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv"),
    ("WS5", "WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz.csv"),
    ("WS5", "WS5_controls/data/"
            "trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S0R_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S4p_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S5-13L_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S5_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S6_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS9", "WS9_vehicle_one_wave2/data/"
            "trace_S7_GH-REG-165_nominal_seed8101_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_V1_VOLT-SUB_cold_-10C_seed11_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_V2_VOLT-REG_nominal_seed23_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_V2_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_V2_VOLT-SUB_nominal_seed11_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_ruler_VOLT-SUB_nominal_seed11_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_ruler_VOLT-SUB_cold_-10C_seed11_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_ruler_VOLT-REG_nominal_seed23_10Hz.csv"),
    ("WS11", "WS11_vehicle_zero_ruler/data/"
             "trace_ruler_VOLT-REG_climb_10km_6pct_seed23_10Hz.csv"),
]

# Traces written after TRACE_SCHEMA.md was issued are validated against
# it. Everything earlier is measured against it and labelled PRE-R34.
R34_ERA = ("WS5_controls/",)


def build_trace_registry():
    rows = []
    published = set()
    for ws, rel in ALL_TRACES:
        header, meta, cols, rows_ = TR.read_trace(rel)
        is_r34 = any(rel.startswith(p) for p in R34_ERA)
        if is_r34:
            v = TR.validate_r34(rel, header, meta, cols, rows_)
        else:
            v = TR.describe_pre_r34(rel, header, meta, cols, rows_)
        sha_ok = None
        if "results_sha256" in meta and "results_file" in meta:
            rf = os.path.join(os.path.dirname(rel), meta["results_file"])
            rf_alt = os.path.join(os.path.dirname(os.path.dirname(rel)),
                                  meta["results_file"])
            for cand in (rf_alt, rf):
                if os.path.exists(repo_path(cand)):
                    sha_ok = (sha256_of(cand)
                              == meta["results_sha256"].split()[0])
                    break
        rows.append({
            "ws": ws,
            "file": rel,
            "bytes": os.path.getsize(repo_path(rel)),
            "rows": len(rows_),
            "columns": cols,
            "nColumns": len(cols),
            "validation": v,
            "servedByExhibit": False,
            "resultsShaDeclared": meta.get("results_sha256"),
            "resultsShaMatchesDisk": sha_ok,
        })
    return rows, published


def build_sim_screen(trace_index, registry):
    traces = []
    for t in SIM_TRACES:
        info = trace_index["_info"][t["rel"]]
        traces.append({
            "id": trace_index[t["rel"]],
            "label": t["label"],
            "sourceFile": t["rel"],
            "bsfcMap": t["map"],
            "headerLines": info["headerLines"],
            "meta": info["meta"],
        })
    i5 = ["interface_ws5"]
    return {
        "id": "sim",
        "title": "Simulator",
        "kicker": "RECORD REPLAY · TRACE_SCHEMA (R34)",
        "lede": ("A trace file on disk, played back. Elevation from z_m, "
                 "the R15 blend cascade from the four braking channels, the "
                 "engine dot on the map it was actually run against. Nothing "
                 "here is simulated in the browser."),
        "statusBadge": status_badge("NOT CUT"),
        "statusNote": {
            "headline": "WS5 was never adjudicated.",
            "quote": cite(WS5, ["_meta", "adjudication"], "str"),
            "baselineQuote": q(BASELINE,
                               "WS5: status per its packet at freeze."),
            "packetGap": ("BASELINE_v7_FREEZE points WS5's status at a "
                          "packet. No PM_PACKET_WS5.md exists at the "
                          "repository root; the four packets that do exist "
                          "are KX, WS2, WS3 and WS4. Recorded, not "
                          "resolved."),
        },
        "traces": traces,
        "payloadNote": {
            "headline": "The payload this screen divides by comes from the "
                        "trace header, as ordered. It is not the payload "
                        "WS11's ledger gives these vehicles.",
            "body": ("Both WS5 trace headers declare `payload_kg: 2900.0` "
                     "at `mass_kg: 6600.0`. That is the stock NPR-HD's "
                     "payload at gross weight. WS11's ratified mass ledger "
                     "gives V1 2,712 kg and V2 2,461 kg at the same gross "
                     "weight, because both candidates carry powertrain mass "
                     "the ruler does not. Both figures are shown; neither "
                     "is quietly substituted for the other."),
            "ledgerV1": cite(WS11, ["interface_ws11", "masses",
                                    "payload_at_gvw_kg", "V1"], ",.0f",
                             suf=" kg"),
            "ledgerV2": cite(WS11, ["interface_ws11", "masses",
                                    "payload_at_gvw_kg", "V2"], ",.0f",
                             suf=" kg"),
            "ledgerRuler": cite(WS11, ["interface_ws11", "masses",
                                       "payload_at_gvw_kg", "ruler"], ",.0f",
                                suf=" kg"),
        },
        "decimation": {
            "badge": "the replay is decimated; the record is not",
            "rule": ("Scrub tier is 1 Hz, decimated by strided sample and "
                     "never by averaging - averaging would invent samples "
                     "that are not in the record. The detail tier is the "
                     "full 10 Hz record, fetched one segment at a time for "
                     "the segment in view."),
        },
        "ribbon": {
            "present": False,
            "reason": ("An 8-seed ribbon needs eight trace files per case. "
                       "WS5 exports the reference seed only, so the ribbon "
                       "is absent and drawn dashed. It is not filled in from "
                       "anything."),
            "seedsAvailable": 1,
            "seedsNeeded": 8,
        },
        "controlConstants": {
            "loopRateHz": cite(WS5, i5 + ["supervisor", "loop_rate_Hz"],
                               ".0f", suf=" Hz"),
            "chopperRateHz": cite(WS5, i5 + ["supervisor",
                                             "chopper_command_rate_Hz"],
                                  ".0f", suf=" Hz"),
            "v1FixedPoint": cite(WS5, i5 + ["dispatch_v1_r19",
                                            "fixed_point_bus_kW"], ".1f",
                                 suf=" kW"),
            "v2Strategy": cite(WS5, i5 + ["dispatch_v2_r22b", "recommended"],
                               "str"),
            "pinnedBsfc": cite(WS5, i5 + ["dispatch_v2_r22b", "pinned_point",
                                          "bsfc"], ".2f", suf=" g/kWh"),
            "architecture": cite(WS5, i5 + ["_architecture"], "str"),
        },
        "busLoadNote": ("TRACE_SCHEMA describes P_bus_load_kW as "
                        "'accessories + heater'. In these two files it is "
                        "the TOTAL bus load and sits exactly 2.0 kW above "
                        "P_motor_bus_kW at every sample, so the accessory "
                        "term on this diagram is the difference of the two "
                        "columns and is badged DERIVED. The divergence "
                        "between the schema's wording and the file's use is "
                        "stated rather than smoothed over."),
        "blendOrder": {
            "rule": "pack -> heater -> resistor -> friction",
            "citation": "TRACE_SCHEMA.md, Electrified columns",
            "quote": q("TRACE_SCHEMA.md",
                       "blend order R15: pack -> heater ->\nresistor -> "
                       "friction; the four must sum to the braking demand\n"
                       "served electrically plus friction"),
        },
        "registry": registry,
        "registryNote": ("Every 10 Hz trace in the repository, measured "
                         "against TRACE_SCHEMA. The exhibit serves only the "
                         "conforming ones on this screen; the rest are "
                         "linked by path and not plotted."),
    }


# ===================================================================== 6
# Screen 5 — the sandbox.

def build_sandbox_screen():
    ends = SB.resolve_endpoints(load_json)
    ws8 = load_json(WS8)
    ws9 = load_json(WS9)
    fr = resolve(ws9, ["two_walls", "two_speed_solve", "ENG-13L", "solve",
                       "force_required"])
    s3 = resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility"])
    eng11 = resolve(ws9, ["two_walls", "single_ratio_closed_form",
                          "ENG-11L"])

    ceil8 = SB.ratio_ceiling(
        resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility",
                      "ratio_ceiling_closed_form", "rpm_ceiling"]),
        resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility",
                      "ratio_ceiling_closed_form", "r_dyn_m"]),
        resolve(ws8, ["interface_ws8", "S3_fixed_ratio_feasibility",
                      "ratio_ceiling_closed_form", "v_cruise_kmh"]) / 3.6)
    frac = eng11["F_available_at_ceiling_kN"] * 1000.0 / fr["total_N"]

    def endpoint_block(which, spec_map):
        e = ends[which]
        out = {"label": (SB.VEHICLE_ZERO if which == "zero"
                         else SB.VEHICLE_ONE)["label"]}
        for k, v in e.items():
            out[k] = v
        out["citations"] = spec_map
        return out

    zero_cites = {
        "m_kg": cite(WS1, ["params", "vehicle", "m_gvw"], ",.0f", suf=" kg"),
        "CdA_m2": cite(WS1, ["params", "vehicle", "CdA"], ".2f",
                       suf=" m²"),
        "Crr": cite(WS1, ["params", "vehicle", "Crr"], ".4f"),
        "rho_air": cite(WS1, ["params", "vehicle", "rho_air"], ".3f",
                        suf=" kg/m³"),
        "r_dyn_m": cite(WS1, ["params", "vehicle", "r_dyn"], ".3f", suf=" m"),
        "v_cruise_kmh": cite(WS1, ["cycles", "VOLT-REG", "max_speed_kmh"],
                             ".1f", suf=" km/h"),
        "eta_driveline": cite(WS1, ["params", "driveline", "eta_direct"],
                              ".3f"),
    }
    one_cites = {
        "m_kg": cite(WS8, ["params", "vehicle", "m_gcw"], ",.0f", suf=" kg"),
        "CdA_m2": cite(WS8, ["params", "vehicle", "CdA"], ".2f",
                       suf=" m²"),
        "Crr": cite(WS8, ["params", "vehicle", "Crr"], ".4f"),
        "rho_air": cite(WS8, ["params", "vehicle", "rho_air"], ".3f",
                        suf=" kg/m³"),
        "r_dyn_m": cite(WS8, ["params", "vehicle", "r_dyn"], ".3f", suf=" m"),
        "v_cruise_kmh": cite(WS8, ["params", "cycle", "linehaul_v_hi_kmh"],
                             ".1f", suf=" km/h"),
        "T_peak_Nm": cite(WS8, ["task2_s0_calibration", "engine",
                                "peak_torque_Nm"], ",.0f", suf=" Nm"),
        "rpm_ceiling": cite(WS8, ["interface_ws8",
                                  "S3_fixed_ratio_feasibility",
                                  "ratio_ceiling_closed_form",
                                  "rpm_ceiling"], ",.0f", suf=" rpm"),
        "v_climb_kmh": cite(WS9, ["two_walls", "two_speed_solve", "ENG-13L",
                                  "solve", "force_required", "v_ref_kmh"],
                            ".0f", suf=" km/h"),
    }

    return {
        "id": "sandbox",
        "title": "Sandbox",
        "kicker": "SANDBOX — SIMPLIFIED PHYSICS, NOT A TRIAL RESULT",
        "lede": ("The only screen where your input drives the numbers. The "
                 "constants are the program's; the interpolation between "
                 "the two vehicles of record is not, and neither is any "
                 "answer you get here."),
        "disclaimer": ("Nothing on this screen is a verdict, and nothing on "
                       "it may be quoted as one. It exists to show where a "
                       "boundary lies, using the same two closed forms the "
                       "trial used."),
        "model": {
            "roadLoad": "F = 0.5 rho CdA v^2 + Crr m g cos(theta) + "
                        "m g sin(theta),  theta = atan(grade),  g = 9.81",
            "ratioMax": cite(WS8, ["interface_ws8",
                                   "S3_fixed_ratio_feasibility",
                                   "ratio_ceiling_closed_form", "rule"],
                             "str"),
            "ratioMin": "ratio_min = F_grade_hold * r_dyn / "
                        "(T_peak * eta_driveline) - the same statement, "
                        "inverted",
            "gConstant": "9.81 m/s^2, declared identically at "
                         "WS1_loads_duty_cycles/volt_params.py:10 and "
                         "WS8_semi_architecture/ws8_params.py:24",
            "interpolation": ("Between the two endpoints every parameter is "
                              "interpolated linearly in mass. That "
                              "interpolation is a SANDBOX construction and "
                              "appears in no results file."),
        },
        "endpoints": {
            "zero": endpoint_block("zero", zero_cites),
            "one": endpoint_block("one", one_cites),
        },
        "airDensity": {
            "label": "AIR DENSITY",
            "members": [
                {"key": "cold", "label": "cold, -10 C",
                 "value": cite(WS8, ["params", "vehicle", "rho_air_cold"],
                               ".3f", suf=" kg/m³")},
                {"key": "nominal", "label": "nominal",
                 "value": cite(WS8, ["params", "vehicle", "rho_air"], ".3f",
                               suf=" kg/m³")},
                {"key": "hotalt", "label": "hot, 2,000 m / +45 C",
                 "value": cite(WS8, ["params", "vehicle", "rho_air_hot_alt"],
                               ".3f", suf=" kg/m³")},
            ],
            "note": ("The draft's temperature slider multiplied the torque "
                     "demand by an invented cold factor. It is replaced by "
                     "the air density the record actually declares, which "
                     "enters the aero term and nothing else."),
        },
        "anchors": {
            "headline": "The same function, against the record",
            "note": ("These are the values the screen's own model returns "
                     "for the record's own cases. If the model in your "
                     "browser were wrong, these would disagree with the "
                     "column beside them."),
            "rows": [
                {"id": "ws1-cruise85",
                 "label": "Vehicle Zero road load, 85 km/h, flat",
                 "inputs": {"m_kg": 6600.0, "CdA_m2": 4.2, "Crr": 0.009,
                            "rho_air": 1.2, "v_ms": 85.0 / 3.6,
                            "grade": 0.0},
                 "field": "total_N",
                 "record": cite(WS1, ["baseline_crosscheck",
                                      "cruise85_force_N"], ".4f", suf=" N")},
                {"id": "ws1-grade6",
                 "label": "Vehicle Zero road load, 60 km/h, 6% grade",
                 "inputs": {"m_kg": 6600.0, "CdA_m2": 4.2, "Crr": 0.009,
                            "rho_air": 1.2, "v_ms": 60.0 / 3.6,
                            "grade": 0.06},
                 "field": "total_N",
                 "record": cite(WS1, ["sensitivity", "climb_10km_6pc",
                                      "per_speed", "60kmh",
                                      "wheel_force_N"], ".4f", suf=" N")},
                {"id": "ws9-grade6",
                 "label": "Vehicle One road load, 45 km/h, 6% grade",
                 "inputs": {"m_kg": 36300.0, "CdA_m2": 5.5, "Crr": 0.0055,
                            "rho_air": 1.196, "v_ms": 12.5, "grade": 0.06},
                 "field": "total_N",
                 "record": cite(WS9, ["two_walls", "two_speed_solve",
                                      "ENG-13L", "solve", "force_required",
                                      "total_N"], ".4f", suf=" N")},
            ],
            "ceiling": {
                "label": "Ratio ceiling at 2,100 rpm and 105 km/h",
                "inputs": {"rpm_ceiling": 2100.0, "r_dyn_m": 0.5,
                           "v_cruise_ms": 105.0 / 3.6},
                "record": cite(WS8, ["interface_ws8",
                                     "S3_fixed_ratio_feasibility",
                                     "ratio_ceiling_closed_form", "value"],
                               ".6f", suf=":1"),
            },
        },
        "s3": {
            "headline": "The S3 result, out of the same function",
            "ratiosTested": s3["ratios_tested"],
            "ratioNeeded": cite(WS8, ["interface_ws8",
                                      "S3_fixed_ratio_feasibility",
                                      "ratio_needed_to_hold_6pct", "ratio"],
                                ".2f", suf=":1"),
            "maxWithoutOverspeed": cite(WS8, ["interface_ws8",
                                              "S3_fixed_ratio_feasibility",
                                              "max_ratio_without_overspeed"],
                                        ".2f", suf=":1"),
            "anyFeasible": cite(WS8, ["interface_ws8",
                                      "S3_fixed_ratio_feasibility",
                                      "any_feasible"], "str"),
            "overCeilingRpm": cite(WS8, ["interface_ws8",
                                         "S3_fixed_ratio_feasibility",
                                         "ratio_needed_to_hold_6pct",
                                         "over_ceiling_by_rpm"], ",.0f",
                                   suf=" rpm"),
            "forceRequired": cite(WS9, ["two_walls",
                                        "single_ratio_closed_form",
                                        "ENG-11L", "F_required_6pct_kN"],
                                  ".2f", suf=" kN"),
            "forceAvailable": cite(WS9, ["two_walls",
                                         "single_ratio_closed_form",
                                         "ENG-11L",
                                         "F_available_at_ceiling_kN"], ".2f",
                                   suf=" kN"),
            "forceFraction": lit(100.0 * frac, ".2f", suf="%",
                                 tier=TIER_DERIVED,
                                 source="F_available_at_ceiling_kN / "
                                        "force_required.total_N, both "
                                        "exported"),
            "spanNeeded": cite(WS9, ["two_walls", "single_ratio_closed_form",
                                     "ENG-11L", "span_needed"], ".2f",
                               suf=":1"),
            "recomputedCeiling": lit(ceil8, ".6f", suf=":1",
                                     tier=TIER_DERIVED,
                                     source="ws12_sandbox.ratio_ceiling() on "
                                            "the exported rpm ceiling, "
                                            "r_dyn and cruise speed"),
            "body": ("At the highest ratio that keeps the engine under its "
                     "own rpm ceiling at cruise, the tractive force "
                     "available is a little over half what a 6% grade at "
                     "36.3 tonnes demands. Turning the ratio down to hold "
                     "the grade puts the engine 1,732 rpm over its ceiling "
                     "at 105 km/h. There is no single ratio in between. "
                     "That is the first of the two walls, and it comes out "
                     "of the same two lines of arithmetic your sliders are "
                     "driving."),
        },
    }


# ===================================================================== 7
# Screen 6 — method and sources.

def build_method_screen(sources, published_bytes, trace_rows):
    return {
        "id": "method",
        "title": "Method",
        "kicker": "WHAT THIS EXHIBIT CLAIMS, AND WHAT IT DOES NOT",
        "lede": ("The thesis is not that we designed a better truck. It is "
                 "that an engineering trial can be run by AI agents, on a "
                 "real physical question, by a principal who is not an "
                 "engineer, and that the output can be made falsifiable "
                 "rather than merely fluent."),
        "claims": [
            {"n": i + 1, "text": t, "statusText": s}
            for i, (t, s) in enumerate([
                ("Electric torque-fill replaces the gearbox entirely at "
                 "6.6 t.", "ratified, model-relative"),
                ("The transmissionless premise has a MASS boundary between "
                 "~7 and 36 t: no single ratio spans cruise and grade at "
                 "36.3 t.", "ratified, closed-form and simulated"),
                ("It has a DUTY boundary: the same truck wins +20% on "
                 "stop-go and loses on regional duty.",
                 "V1 provisional, V2 kill"),
                ("A 2-speed under torque-fill meets a third wall - the low "
                 "gear's coupling floor vs crawl speed.", "provisional"),
                ("At fixed gross weight, efficiency per added kilogram is "
                 "the objective; every electrified semi candidate won 6-10% "
                 "per km and gave 6-8% back in freight (S3 excepted).",
                 "ratified, r3 numbers"),
                ("Waste-heat recovery is a full-load technology on a "
                 "part-load duty.", "ratified at semi scale"),
                ("Zero-mass levers are symmetric; predictive energy "
                 "management is worth ~0 when the incumbent gets it too.",
                 "provisional, PRE-B2"),
                ("The method: pre-registration, pre-committed kill "
                 "criteria, fresh-context disk-only adjudication, three-way "
                 "verification, export discipline.",
                 "ratified by its record"),
            ])
        ],
        "claimsSource": q(BASELINE,
                          "## What the program found (the publishable "
                          "claims, each with status)"),
        "tiers": [
            {"tag": TIER_RECORD, "name": "On disk, in a results file",
             "desc": "Resolves to a file and an explicit key path. Click it "
                     "and the path appears. Nothing in this tier was typed "
                     "by hand; a verifier re-opens every file and re-formats "
                     "every string before the build is allowed to pass."},
            {"tag": TIER_DERIVED, "name": "Computed here, from the record",
             "desc": "An integration of a trace file's own columns, or an "
                     "arithmetic combination of record values. Faithful to "
                     "what is on disk; not itself a number of record. Every "
                     "one names what it was derived from."},
            {"tag": TIER_SANDBOX, "name": "Your input, our arithmetic",
             "desc": "The sandbox screen only. Carries no verdict and may "
                     "not be quoted as one."},
        ],
        "sources": sources,
        "publishedBytes": published_bytes,
        "traceRows": trace_rows,
        "limitations": [
            {"id": "ESC-1", "text": "The ruler was never calibrated. WS11 "
                                    "obtained a public fuel-economy anchor "
                                    "and moved no ruler parameter to close "
                                    "the residual, and records that as a "
                                    "non-satisfaction of the order it was "
                                    "given. Every Vehicle Zero verdict is "
                                    "therefore model-relative."},
            {"id": "no-hardware", "text": "No hardware was built and no "
                                          "physical test was run at any "
                                          "point in this program. The "
                                          "method demonstrated here catches "
                                          "internal inconsistency. It "
                                          "cannot catch wrong physics."},
            {"id": "unadjudicated", "text": "Two workstreams' final rounds "
                                            "were never adversarially "
                                            "reviewed, one workstream was "
                                            "never reviewed at all, and one "
                                            "round stopped NOT CONVERGED "
                                            "with its blocking finding "
                                            "open. All four are on the "
                                            "round-history screen."},
        ],
    }


# ===================================================================== 8
# Assembly.

def build_provenance():
    return {
        "baseline": {
            "label": "BASELINE v7 · RESEARCH FREEZE · 2026-08-31",
            "file": ff(BASELINE),
            "quote": q(BASELINE,
                       "Supersedes BASELINE_v6.md as the program's governing "
                       "state. The\nresearch track is FROZEN by the "
                       "principal's decision."),
        },
        "resultsFiles": [ff(p) for p in (WS1, WS4, WS5, WS8, WS9, WS11)],
        "screens": {
            "verdict": {"resultsFile": "results_ws4.json / results_ws8.json "
                                       "/ results_ws11.json",
                        "criterion": ">= 3% nominal, >= 0% every corner "
                                     "(WS8, WS11); G1 >= 5% (WS4)",
                        "seed": "8-seed ensembles, extrema are envelopes",
                        "corner": "per card"},
            "race": {"resultsFile": "results_ws11.json",
                     "criterion": ">= 3% nominal, >= 0% every corner",
                     "seed": "VOLT-SUB seed 11 / VOLT-REG seed 23",
                     "corner": "per dataset"},
            "rounds": {"resultsFile": "FINDINGS_*.md, PM_LOG.md, "
                                      "PM_PACKET_KX.md",
                       "criterion": "n/a", "seed": "n/a", "corner": "n/a"},
            "sim": {"resultsFile": "results_ws5.json",
                    "criterion": "n/a - replay, not a gate",
                    "seed": "seed 11 (V1) / seed 23 (V2)",
                    "corner": "nominal"},
            "sandbox": {"resultsFile": "results.json (WS1) / results_ws8.json "
                                       "/ results_ws9.json",
                        "criterion": "n/a - SANDBOX",
                        "seed": "n/a - closed form",
                        "corner": "your sliders"},
            "method": {"resultsFile": "BASELINE_v7_FREEZE.md",
                       "criterion": "n/a", "seed": "n/a", "corner": "n/a"},
        },
    }


# ===================================================================== 8b
# The machine-readable interface block. Plain numbers, not Cited objects:
# these are facts about the EXHIBIT, and their source of truth is the
# emitted bundle itself, which `exhibit_verify.py` re-derives.

CUT_ELEMENTS = [
    {"id": "semi-race-replay",
     "element": "the WS8/WS9 semi race as a replayed dual counter",
     "why": ("WS9's 10 Hz traces carry four commanded force channels and "
             "no fuel or electrical columns at all - the trace's own header "
             "says the electrical quantities are not in the file - and WS9 "
             "exports no per-km MARGIN anywhere in results_ws9.json, only "
             "per-km levels. Neither counter has a column to integrate or a "
             "number of record to resolve to."),
     "kept": ("the dataset is wired into the same screen and renders as a "
              "verdict panel with FROZEN-PROVISIONAL badges, the criterion, "
              "both duties, and the absence stated on screen with the trace "
              "header quoted."),
     "rule": "cut the element, not the rule"},
    {"id": "sim-elevation-on-VOLT-SUB",
     "element": "an elevation profile with relief on the V1 simulator trace",
     "why": ("VOLT-SUB's z_m column is present and constant: the duty is "
             "flat. Nothing is missing; there is simply no relief."),
     "kept": ("the profile is drawn as a flat line down the middle of its "
              "panel with the measured span printed beside it, rather than "
              "squashed onto the axis where it would read as absent data."),
     "rule": "an unvarying signal is a fact about the record"},
    {"id": "race-elevation",
     "element": "the elevation profile on race mode",
     "why": ("WS11's r2 traces predate TRACE_SCHEMA and carry no z_m "
             "column. The exhibit will not integrate grade into an "
             "elevation it does not have."),
     "kept": ("the route strip plots v_kmh and grade_pct, both present, and "
              "says on screen that z_m is absent from the file."),
     "rule": "never synthesize a missing column"},
    {"id": "eight-seed-ribbon",
     "element": "the 8-seed ribbon on the simulator",
     "why": ("a ribbon needs eight trace files per case; WS5 exports the "
             "reference seed only."),
     "kept": ("the ribbon panel is present, drawn dashed, and states the "
              "seed count it has against the seed count it needs."),
     "rule": "absent (dashed) when not"},
    {"id": "fault-trace-replay",
     "element": "replay of WS5's brake-resistor-loss fault trace",
     "why": ("the file fails TRACE_SCHEMA's own R15 blend-order sum rule by "
             "44.9 kW on the bus cascade and 49.0 kW on the wheel closure, "
             "against a tolerance of about 5e-4 kW."),
     "kept": ("it is listed in the trace registry as REFUSED with the "
              "measured residuals and the tolerance, which is the loader "
              "rule doing exactly what it exists to do. It is not "
              "published."),
     "rule": "refuse nonconforming files with a visible reason rather than "
             "plotting them"},
    {"id": "sandbox-temperature-slider",
     "element": "the draft's AMBIENT TEMPERATURE slider",
     "why": ("it multiplied the torque demand by `1 + max(0, 20 - T) * "
             "0.0022`, a constant with no provenance anywhere in the "
             "record."),
     "kept": ("replaced by an AIR DENSITY slider bounded by WS8's own three "
              "declared members (cold, nominal, hot at altitude), which "
              "enters the aero term and nothing else."),
     "rule": "if a figure is not traceable to a file, it is not shown as a "
             "result"},
    {"id": "draft-synthetic-engine",
     "element": "the draft's synthetic trace generator, engine model, "
                "generator map and duty-cycle builder",
     "why": "every number it produced was invented in the browser.",
     "kept": ("replaced wholesale by record replay: decimated trace files "
              "on disk and WS4's exported BSFC maps."),
     "rule": "replace everything synthetic with the record"},
    {"id": "draft-ratified-record-badge",
     "element": "the draft's RATIFIED RECORD badge",
     "why": ("`RATIFIED` alone in a badge position is a build failure under "
             "BASELINE_v7_FREEZE R52."),
     "kept": ("badges render only v7's five labels, and "
              "`exhibit_verify.py` fails the build on any other."),
     "rule": "no status is ever promoted"},
]

ESCALATIONS = [
    {"id": "WS12-E1",
     "challenges": "WS12_exhibit/ASSIGNMENT.md, screen 3, and "
                   "BASELINE_v7_FREEZE.md claim 8",
     "headline": "five-for-five or seven-for-seven: the record and this "
                 "assignment disagree on the denominator",
     "detail": ("BASELINE_v7_FREEZE.md claim 8 says 'five-for-five "
                "first-pass defect detection', and R37 in BASELINE_v5.md "
                "states the same base rate; PM_LOG.md repeats it three "
                "times. This workstream's own assignment orders 'the "
                "seven-for-seven first-pass defect rate'. Seven first-pass "
                "adjudication findings files exist on disk (WS2 r1, WS3 r1, "
                "WS4 r1, KX r1, WS8 r1, WS9 pre-r1, WS11 r1) and all seven "
                "record at least one blocking or material finding. The "
                "difference is whether the KX round's own first pass and "
                "the WS9 pre-adjudication count. The exhibit renders BOTH "
                "readings with their scope and their source and promotes "
                "neither."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E2",
     "challenges": "LEAD_HANDOVER.md doctrine D5",
     "headline": "D5's first-pass range names WS1; the disk has no WS1 "
                 "adjudication",
     "detail": ("D5 reads 'Every first-pass adjudication in this program "
                "(WS1-WS4) found material or blocking defects'. No "
                "FINDINGS_WS1_r*.md exists anywhere in the repository and "
                "PM_LOG.md carries no WS1 entry; WS1 was closed by lead "
                "ratification in BASELINE_v1. The exhibit's per-workstream "
                "table records WS1 as one round run and zero adjudications, "
                "and its gap-set panel says so in the same words."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E3",
     "challenges": "BASELINE_v7_FREEZE.md, final research state, WS5 line",
     "headline": "v7 points WS5's status at a packet that was never written",
     "detail": ("v7 reads 'WS5: status per its packet at freeze'. No "
                "PM_PACKET_WS5.md exists at the repository root; the four "
                "packets that do exist are KX, WS2, WS3 and WS4. WS5's own "
                "results file carries its status instead "
                "('gated-but-unadjudicated'), and the exhibit renders that "
                "string rather than inventing a packet."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E4",
     "challenges": "R34 / TRACE_SCHEMA.md, and the WS11 r2 round",
     "headline": "WS11's trace fuel column does not integrate to WS11's own "
                 "per-seed fuel",
     "detail": ("Integrating each WS11 r2 trace's own fuel_g_per_s column "
                "at its own 0.1 s step and dividing by the distance its own "
                "v_kmh column travels gives a fuel energy per kilometre "
                "that differs from the same seed's exported figure by "
                "-12.87% and -13.19% on the two V1 cases, -0.65% and -1.29% "
                "on the two V2 candidate cases, and -0.00%, -0.36% and "
                "-2.93% on the three ruler cases. Two mechanisms the record "
                "itself names account for most of it - the pipeline books "
                "charge-neutral fuel (WS4 exports fuel_g and "
                "fuel_corrected_g side by side) and the ruler is charged "
                "for 3.2582 kWh of work it could not do on the climb - and "
                "they do not close it completely. V1's cold corner is one "
                "of the affected cases and is the corner V1's ADVANCE is "
                "decided on. This exhibit does not attempt to close the "
                "residual; it prints the measured difference on the screen "
                "beside the number of record. The affected round is the one "
                "whose adjudication was cut at 07:40."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for "
                   "LIMITATIONS.md via WS13."},
    {"id": "WS12-E5",
     "challenges": "TRACE_SCHEMA.md, blend-order rule, against WS5's fault "
                   "trace",
     "headline": "the R15 blend-order sum rule does not close on WS5's "
                 "fault trace",
     "detail": ("On `trace_V2_descent6pct-70kmh_resistor-loss_seed0_10Hz."
                "csv` the bus cascade misses by up to 44.8784 kW and the "
                "wheel closure by up to 49.0130 kW, against a tolerance of "
                "about 5e-4 kW; the two conforming duty traces miss by at "
                "most 5.0e-4 kW on terms of order 100 kW. At the worst "
                "sample P_motor_mech_kW still carries the full braking "
                "demand while P_friction_brake_kW carries almost all of it "
                "as well. The exhibit refuses the file, states the "
                "residuals, and does not publish it. This is an "
                "observation against the schema's own rule, not a verdict "
                "on WS5, and WS5 was never adjudicated."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for "
                   "LIMITATIONS.md via WS13."},
    {"id": "WS12-E6",
     "challenges": "TRACE_SCHEMA.md, Electrified columns",
     "headline": "P_bus_load_kW is defined as 'accessories + heater' and "
                 "used as the total bus load",
     "detail": ("In both conforming WS5 traces P_bus_load_kW sits exactly "
                "2.0 kW above P_motor_bus_kW at every sample - it is the "
                "total bus load, not the accessory load the schema names. "
                "The exhibit shows the accessory term as the difference of "
                "the two columns, badged DERIVED, and states the divergence "
                "on the screen."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E7",
     "challenges": "WS12_exhibit/ASSIGNMENT.md, screen 4, decimated-replay "
                   "rule",
     "headline": "the largest trace named in the rule does not exist under "
                 "that name",
     "detail": ("The rule cites 'the largest in the tree is 10.22 MB "
                "(WS5_controls/data/trace_v2_load_follow_nominal_seed23_"
                "10Hz.csv)'. No file of that name exists. The largest trace "
                "in the repository is "
                "`WS5_controls/data/trace_V2_VOLT-REG_nominal_seed23_10Hz."
                "csv` at 14,438,858 bytes. The rule is applied to that "
                "file, which is the one the description clearly means; the "
                "discrepancy is recorded rather than silently corrected."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E8",
     "challenges": "TRACE_SCHEMA.md, 'WS11's r2 traces are the reference "
                   "implementation'",
     "headline": "WS11's r2 traces do not conform to the schema they are "
                 "named as the reference for",
     "detail": ("TRACE_SCHEMA.md was issued at 07:54; WS11's r2 traces were "
                "written at 07:32. They carry free-text comment headers "
                "with none of the fourteen mandatory `# key: value` keys, "
                "and they are missing seven of the ten core columns (x_m, "
                "z_m, fuel_cum_g, P_friction_brake_kW, trip_time_flag among "
                "them) and every electrified column the schema names except "
                "P_gen_bus_kW and P_bus_load_kW. The exhibit classes them "
                "PRE-R34, publishes them for race mode with the exact list "
                "of what they lack, and plots only the columns they carry. "
                "The only R34-conforming trace files in the repository are "
                "WS5's two duty traces."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead."},
    {"id": "WS12-E9",
     "challenges": "TRACE_SCHEMA.md, mandatory header key `payload_kg`",
     "headline": "both WS5 trace headers declare the RULER's payload for a "
                 "candidate vehicle",
     "detail": ("`trace_V1_VOLT-SUB_nominal_seed11_10Hz.csv` and "
                "`trace_V2_VOLT-REG_nominal_seed23_10Hz.csv` both carry "
                "`# payload_kg: 2900.0` at `# mass_kg: 6600.0`. 2,900 kg is "
                "the stock NPR-HD's payload at GVW in WS11's ratified mass "
                "ledger; the same ledger gives V1 2,712 kg and V2 2,461 kg "
                "at the same gross weight, because both candidates carry "
                "powertrain mass the ruler does not. The assignment orders "
                "the simulator's MJ per payload tonne-km counter to run "
                "'from header payload', so it does, and the screen prints "
                "the header value, its key, and WS11's ledger figure for "
                "the same vehicle beside it. Nothing of WS5's turns on it - "
                "WS5 claims no efficiency advantage anywhere - but the "
                "mandatory header field does not agree with the mass ledger "
                "of record, and WS5 was never adjudicated."),
     "resolution": "NOT SELF-RESOLVED. Recorded for the lead and for "
                   "LIMITATIONS.md via WS13."}
]


def build_interface(bundle, manifest, decimation, maps, registry, sources):
    kinds = {}
    tiers = {}
    for m in manifest:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
        tiers[m["tier"]] = tiers.get(m["tier"], 0) + 1
    badges = collect_badges(bundle)
    badge_counts = {}
    for b in badges:
        badge_counts[b["badge"]] = badge_counts.get(b["badge"], 0) + 1
    conforming = [r for r in registry if r["validation"]["conforms"]]
    refused = [r for r in registry
               if r["validation"]["schemaClass"] == "R34"
               and not r["validation"]["conforms"]]
    return {
        "_basis": ("facts about the EXHIBIT, not about the trucks. Every "
                   "number here is derived from the emitted bundle and the "
                   "two manifests, and exhibit_verify.py re-derives each of "
                   "them from the artifacts on disk before the build is "
                   "allowed to pass."),
        "_status": "WS12 exhibit, first pass, bound to BASELINE_v7_FREEZE.md",
        "guard_rails": {
            "method_claim": "catches internal inconsistency",
            "method_claim_never": "catches wrong physics",
            "status_promotion": "none; badges render only v7's five labels",
            "allowed_status_badges": list(ALLOWED_STATUS_BADGES),
            "forbidden_badge_tokens": ["RATIFIED", "PROVISIONAL"],
        },
        "app": {
            "stack": "Vite + React + TypeScript, static, no server",
            "vite_base": "/project-volt/",
            "screens": sorted(bundle["screens"].keys()),
            "screens_n": len(bundle["screens"]),
            "front_door": "verdict",
        },
        "manifest": {
            "entries_total": len(manifest),
            "by_kind": kinds,
            "by_tier": tiers,
        },
        "badges": {
            "positions_total": len(badges),
            "by_label": badge_counts,
        },
        "traces": {
            "published_n": len(decimation),
            "published_bytes": sum(d["publishedBytes"] for d in decimation),
            "source_bytes": sum(d["sourceBytes"] for d in decimation),
            "source_rows_10Hz": sum(d["sourceRows"] for d in decimation),
            "rows_1Hz": sum(d["outputRows1Hz"] for d in decimation),
            "segments_total": sum(len(d["segments"]) for d in decimation),
            "stride": TR.STRIDE,
            "segment_rows": TR.SEGMENT_ROWS,
            "decimation": "strided sample, never averaged",
            "badge": "the replay is decimated; the record is not",
            "registry_total": len(registry),
            "registry_r34_conforming": len(conforming),
            "registry_r34_refused": len(refused),
            "registry_pre_r34": len([r for r in registry
                                     if r["validation"]["schemaClass"]
                                     == "PRE-R34"]),
            "largest_trace_in_tree": {
                "file": max(registry,
                            key=lambda r: r["bytes"])["file"],
                "bytes": max(r["bytes"] for r in registry),
            },
        },
        "maps_published": [m["name"] for m in maps],
        # Traces and maps only. The data bundle and the two manifests are
        # served too, but their size cannot appear here: this field lives
        # INSIDE the bundle, so counting the bundle would make the number
        # depend on its own digits.
        "published_payload_bytes": sum(
            os.path.getsize(os.path.join(base, n))
            for root in (TRACE_OUT, MAP_OUT)
            for base, _, names in os.walk(root) for n in names),
        "published_payload_scope": "app/public/traces + app/public/maps",
        "sources_cited_n": len(sources),
        "cut_elements": CUT_ELEMENTS,
        "cut_elements_n": len(CUT_ELEMENTS),
        "escalations": ESCALATIONS,
        "escalations_n": len(ESCALATIONS),
        "entry_points": {
            "build": "build_exhibit_data.py",
            "report": "make_report_ws12.py",
            "verify": "exhibit_verify.py",
            "determinism": "check_determinism_ws12.py",
            "sandbox_test": "test_sandbox_ws12.py",
            "all": "run_ws12.py",
        },
    }


def collect_manifest(bundle):
    """Every renderable string in the bundle, with its provenance."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            if "s" in node and "tier" in node:
                row = {"key": path, "s": node["s"], "tier": node["tier"]}
                if node.get("kind") == "quote":
                    row["kind"] = "quote"
                    row["file"] = node["file"]
                elif node.get("kind") == "file":
                    row["kind"] = "file"
                    row["file"] = node["file"]
                    row["sha256"] = node["sha256"]
                    row["bytes"] = node["bytes"]
                elif node.get("kind") == "fileref":
                    row["kind"] = "fileref"
                    row["file"] = node["file"]
                elif "file" in node and "path" in node:
                    row["kind"] = "cite"
                    row["file"] = node["file"]
                    row["path"] = node["path"]
                    row["fmt"] = node["fmt"]
                    row["pre"] = node["pre"]
                    row["suf"] = node["suf"]
                    row["v"] = node["v"]
                else:
                    row["kind"] = "derived"
                    row["derivedFrom"] = node.get("derivedFrom", "")
                    row["v"] = node.get("v")
                out.append(row)
                return
            for k in sorted(node):
                walk(node[k], path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)

    walk(bundle, "$")
    return out


def collect_badges(bundle):
    found = []

    def walk(node, path):
        if isinstance(node, dict):
            for k in sorted(node):
                v = node[k]
                if k == "statusBadge" and isinstance(v, str):
                    found.append({"key": path + "." + k, "badge": v})
                walk(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)

    walk(bundle, "$")
    return found


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def main():
    for d in (DATA_OUT, TRACE_OUT, MAP_OUT):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # ---- traces --------------------------------------------------------
    trace_index = {"_info": {}}
    decimation = []
    published_bytes = 0

    to_publish = []
    for p in RACE_PAIRS:
        to_publish.append((p["candTrace"], RACE_COLS_CAND, "race"))
        to_publish.append((p["rulerTrace"], RACE_COLS_RULER, "race"))
    for t in SIM_TRACES:
        to_publish.append((t["rel"], SIM_COLUMNS, "sim"))

    for rel, cols, use in to_publish:
        tid = os.path.basename(rel)[len("trace_"):-len("_10Hz.csv")]
        tid = tid.replace("/", "-")
        ws = rel.split("/")[0].split("_")[0].lower()
        tid = ws + "-" + tid
        out_dir = os.path.join(TRACE_OUT, tid)
        info = TR.emit_trace(rel, out_dir, cols,
                             "traces/" + tid)
        header, meta, all_cols, rows = TR.read_trace(rel)
        is_r34 = any(rel.startswith(p) for p in R34_ERA)
        val = (TR.validate_r34(rel, header, meta, all_cols, rows) if is_r34
               else TR.describe_pre_r34(rel, header, meta, all_cols, rows))
        trace_index[rel] = tid
        trace_index["_info"][rel] = info
        published_bytes += info["publishedBytes"]
        decimation.append({
            "id": tid,
            "use": use,
            "sourcePath": rel,
            "sourceSha256": TR.sha256_file(rel),
            "sourceBytes": os.path.getsize(repo_path(rel)),
            "sourceRows": info["sourceRows"],
            "stride": info["stride"],
            "decimation": info["decimation"],
            "outputRows1Hz": info["scrubRows"],
            "outputRows10Hz": sum(s["rows"] for s in info["segments"]),
            "segmentRows": info["segmentRows"],
            "segments": info["segments"],
            "columnsInSource": all_cols,
            "columnsPublished": info["columnsPublished"],
            "columnsWithheld": [c for c in all_cols
                                if c not in info["columnsPublished"]],
            "publishedBytes": info["publishedBytes"],
            "schemaClass": val["schemaClass"],
            "schemaConforms": val["conforms"],
            "headerLines": info["headerLines"],
            "meta": info["meta"],
            "urlBase": info["urlBase"],
        })
    decimation.sort(key=lambda r: r["id"])

    # ---- BSFC maps -----------------------------------------------------
    maps = []
    for name in ("bsfc_map_V1_candidate.csv", "bsfc_map_V2_candidate.csv"):
        rel = "WS4_genset/data/" + name
        dst = os.path.join(MAP_OUT, name)
        with open(repo_path(rel), "r", encoding="utf-8") as fh:
            body = fh.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        published_bytes += os.path.getsize(dst)
        maps.append({"name": name, "sourcePath": rel,
                     "sha256": sha256_of(rel),
                     "bytes": os.path.getsize(repo_path(rel)),
                     "headerLines": [l[1:].strip() for l in
                                     body.splitlines() if l.startswith("#")]})

    # ---- screens -------------------------------------------------------
    registry, _ = build_trace_registry()
    served = {d["sourcePath"] for d in decimation}
    for r in registry:
        r["servedByExhibit"] = r["file"] in served

    sources = []
    for rel in (BASELINE, WS1, WS4, WS5, WS8, WS9, WS11, "TRACE_SCHEMA.md",
                "LEAD_HANDOVER.md", "PM_LOG.md", "PM_PACKET_KX.md",
                "NIGHT_REPORT.md", "BASELINE_v5.md",
                "WS4_genset/FINDINGS_KX_r3.md",
                "WS8_semi_architecture/FINDINGS_WS8_r3.md",
                "WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md"):
        sources.append(ff(rel))
    for rel, _, _ in to_publish:
        sources.append(ff(rel))
    for m in maps:
        sources.append(ff(m["sourcePath"]))
    seen = set()
    uniq = []
    for s in sources:
        if s["file"] not in seen:
            seen.add(s["file"])
            uniq.append(s)
    sources = sorted(uniq, key=lambda s: s["file"])

    bundle = {
        "meta": {
            "program": "Project Volt",
            "workstream": "WS12",
            "title": "Project Volt — the method, made clickable",
            "baseline": "BASELINE_v7_FREEZE.md",
            "baselineLabel": "BASELINE v7 · RESEARCH FREEZE",
            "generated": "deterministic build; no wall clock is recorded, "
                         "because a wall clock would break byte stability",
            "entryPoint": "build_exhibit_data.py",
            "verifier": "exhibit_verify.py",
        },
        "guardRails": build_guard_rails(),
        "provenance": build_provenance(),
        "screens": {
            "verdict": build_verdict_screen(),
            "race": build_race_screen(trace_index),
            "rounds": build_rounds_screen(),
            "sim": build_sim_screen(trace_index, registry),
            "sandbox": build_sandbox_screen(),
            "method": build_method_screen(sources, published_bytes,
                                          len(decimation)),
        },
        "traces": {d["id"]: {k: d[k] for k in
                             ("id", "use", "sourcePath", "sourceSha256",
                              "sourceRows", "stride", "outputRows1Hz",
                              "segmentRows", "segments", "columnsPublished",
                              "columnsWithheld", "schemaClass",
                              "schemaConforms", "headerLines", "meta",
                              "urlBase")}
                   for d in decimation},
        "maps": maps,
        "decimationBadge": "the replay is decimated; the record is not",
    }

    badges = collect_badges(bundle)
    for b in badges:
        check_badge(b["badge"])

    manifest = collect_manifest(bundle)
    bundle["interface_ws12"] = build_interface(bundle, manifest, decimation,
                                               maps, registry, sources)
    # The interface block is itself part of the bundle, so re-collect.
    manifest = collect_manifest(bundle)

    write_json(os.path.join(DATA_OUT, "exhibit_data.json"), bundle)
    write_json(os.path.join(DATA_OUT, "manifest.json"), {
        "_rule": ("every number of record the app can render, with the file "
                  "and key path it resolves to and the string it formats to. "
                  "exhibit_verify.py re-opens each file with its own "
                  "resolver and its own formatter and asserts the string."),
        "counts": {
            "total": len(manifest),
            "cite": sum(1 for m in manifest if m["kind"] == "cite"),
            "quote": sum(1 for m in manifest if m["kind"] == "quote"),
            "file": sum(1 for m in manifest if m["kind"] == "file"),
            "fileref": sum(1 for m in manifest if m["kind"] == "fileref"),
            "derived": sum(1 for m in manifest if m["kind"] == "derived"),
        },
        "badges": badges,
        "entries": manifest,
    })
    write_json(os.path.join(DATA_OUT, "decimation_manifest.json"), {
        "_rule": ("one row per published trace: source path, source sha256, "
                  "stride, and output row count. Decimation is by strided "
                  "sample, never by averaging."),
        "badge": "the replay is decimated; the record is not",
        "totals": {
            "traces": len(decimation),
            "sourceBytes": sum(d["sourceBytes"] for d in decimation),
            "publishedBytes": sum(d["publishedBytes"] for d in decimation),
            "sourceRows": sum(d["sourceRows"] for d in decimation),
            "rows1Hz": sum(d["outputRows1Hz"] for d in decimation),
        },
        "rows": decimation,
    })

    print("exhibit_data.json   %8d bytes"
          % os.path.getsize(os.path.join(DATA_OUT, "exhibit_data.json")))
    print("manifest.json       %8d bytes, %d entries"
          % (os.path.getsize(os.path.join(DATA_OUT, "manifest.json")),
             len(manifest)))
    print("traces published    %d, %.2f MB"
          % (len(decimation),
             sum(d["publishedBytes"] for d in decimation) / 1e6))
    print("maps published      %d" % len(maps))
    print("badges checked      %d" % len(badges))
    return 0


if __name__ == "__main__":
    sys.exit(main())
