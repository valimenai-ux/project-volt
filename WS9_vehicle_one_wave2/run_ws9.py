#!/usr/bin/env python3
"""
Project Volt - WS9 - Vehicle One, wave two: the two walls and the cold wall.
SINGLE ENTRY POINT (CLAUDE.md rule 1).

    ../.venv/bin/python run_ws9.py            full deterministic run
    ../.venv/bin/python run_ws9.py --quick    2 seeds, nominal only (dev)
    ../.venv/bin/python run_ws9.py --jobs 6   parallel across candidates

Writes results_ws9.json plus data/*.csv. Fixed seeds throughout (WS8's own
8101..8108); re-running reproduces every artifact byte-identically, which
verify_ws9.py checks along with the report's headline numbers.

WHAT WS9 READS FROM WS8, AND WHAT IT DOES NOT. It imports WS8's MODELS
read-only (cycles, integrator, road load, mass ledger, engines, machines,
packs, genset line, spin rule, correction rule) and SHA-pins every one of
them into the record. It reads NO WS8 NUMERIC ARTIFACT - not
results_ws8.json, not REPORT_WS8.md, not a single exported figure - and
asserts that in the sanity block. WS9 re-derives its own ruler (S0R) from
the same models and compares everything to that. So the r1/r2 split in
WS8's ARTIFACTS cannot touch a WS9 number; only the r1/r2 state of WS8's
CODE can, and that is pinned and reported.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
from collections import OrderedDict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

import ws8_candidates as CD8
import ws8_electric as EL8
import ws8_engine as EN8
import ws8_physics as PH8
import ws8_whr as WHR8
from ws8_params import (VEH, ADH, AUX, DL, ML, G, LHV_KJ_PER_G,
                        ENGINE_HEAT_TO_COOLANT_FRAC)

import ws9_candidates as CD9
import ws9_concordance as CN9
import ws9_corrections as CR9
import ws9_duty as DY9
import ws9_engines as E9
import ws9_fuels as F9
import ws9_params as P9
import ws9_storage as ST9
import ws9_walls as W9
from ws9_primemover import prime_mover_at_the_pin

DATA = os.path.join(_HERE, "data")
os.makedirs(DATA, exist_ok=True)
CHECKPOINT = os.path.join(DATA, "_checkpoint.json")

RULER = CD9.RULER


# =====================================================================
#  Inherited vintage - SHA-pinned (assignment: "state vintages")
# =====================================================================
INHERITED_FILES = (
    "ws8_params.py", "ws8_physics.py", "ws8_cycles.py", "ws8_engine.py",
    "ws8_electric.py", "ws8_candidates.py", "ws8_whr.py",
)
WS8_RULE_SOURCES = ("run_ws8.py",)
"""Hashed, NOT imported. WS9 re-implements WS8's correction pricing on its
own energy keys rather than calling it (ws9_corrections' docstring), so
`run_ws8.py` is the source of an inherited RULE without being an import. A
round could restate that rule and the seven-file pin above would not see
it; this row is what closes that. `ws9_concordance` compares the three
correction blocks field by field and fingerprints them by source text."""

SIBLING_SOURCES = (
    "../WS4_genset/ws4_models.py",
    "../WS4_genset/ws4_chain.py",
    "../WS3_battery/ws3_cells.py",
    "../WS2_traction_motor/results.json",
    "../WS2_traction_motor/data/effmap_motor_inverter_662V.csv",
    "../WS2_traction_motor/data/cycle_loss_summary.csv",
)
"""SIBLING-WORKSTREAM SOURCES WS9'S NUMBERS ACTUALLY DEPEND ON, reached
THROUGH WS8 and pinned here from the r3-concordant re-run onwards.

The round-1 pin covered WS8's seven files and stopped there, which was
incomplete: `ws8_engine` imports WS4's `derate_factor` from
`ws4_models.py`, `ws8_electric` imports WS4's `WS2TractionChain` and
`load_ws2_exports` from `ws4_chain.py` and WS3's `CELLS` from
`ws3_cells.py`, and that loader then reads three WS2 export files off
disk. `ws9_concordance.import_surface()` finds those two names by `ast`
and reports them as unresolved inside WS8's own tree - which is how the
gap was found rather than assumed.

This is not hypothetical. `ws4_chain.py` CHANGED between WS9's round-1 run
and this one (WS4's KX rounds landed overnight), and round 1 had no pin
that could say so. Raised as ESC-WS9-11; the WS4 change is additive
instrumentation and the re-run measures whether it moved anything."""

WS8_ARTIFACTS = ("results_ws8.json", "REPORT_WS8.md",
                 "R2_DIRECTIVE.md", "R3_DIRECTIVE.md",
                 "CHANGELOG_WS8_r2.md", "CHANGELOG_WS8_r3.md",
                 "FINDINGS_WS8_r1.md", "FINDINGS_WS8_r2.md",
                 "FINDINGS_WS8_r3.md")
OWN_FILES = (
    "run_ws9.py", "ws9_params.py", "ws9_duty.py", "ws9_engines.py",
    "ws9_fuels.py", "ws9_storage.py", "ws9_thermal.py", "ws9_walls.py",
    "ws9_candidates.py", "ws9_corrections.py", "ws9_primemover.py",
    "ws9_blocks.py", "ws9_concordance.py", "make_report_ws9.py",
    "verify_ws9.py", "check_determinism_ws9.py",
)

DETERMINISM_FILE = os.path.join(DATA, "determinism_check.json")


def load_determinism():
    """The rule-1 regeneration evidence, recorded as an artifact.

    The check cannot run inside the process it is checking - it compares two
    independent runs - so it is performed by `check_determinism_ws9.py` and
    its result committed alongside the run it certifies, exactly as WS8
    does."""
    if not os.path.exists(DETERMINISM_FILE):
        return dict(status="NOT RUN",
                    note="data/determinism_check.json absent; run "
                         "check_determinism_ws9.py")
    return json.load(open(DETERMINISM_FILE))


def _sha(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def inherited_vintage():
    """The pin. Every inherited WS8 source file, hashed; every WS8 artifact,
    hashed but NOT READ.

    The assignment says: read WS8's report, its r1 findings, "and its r2
    outputs WHEN THEY LAND (build to hot-swap; state vintages)". This block
    is the vintage statement, and it is machine-readable so a later
    adjudication can tell exactly which WS8 it was run against."""
    src = OrderedDict()
    for f in INHERITED_FILES:
        p = os.path.join(_WS8, f)
        src[f] = dict(sha256=_sha(p),
                      bytes=os.path.getsize(p) if os.path.exists(p) else None)
    for f in WS8_RULE_SOURCES:
        p = os.path.join(_WS8, f)
        src[f + " [rule source, NOT imported]"] = dict(
            sha256=_sha(p),
            bytes=os.path.getsize(p) if os.path.exists(p) else None)
    sib = OrderedDict()
    for rel in SIBLING_SOURCES:
        p = os.path.join(_HERE, rel)
        sib[rel] = dict(sha256=_sha(p),
                        bytes=os.path.getsize(p) if os.path.exists(p)
                        else None)
    art = OrderedDict()
    for f in WS8_ARTIFACTS:
        p = os.path.join(_WS8, f)
        art[f] = dict(sha256=_sha(p),
                      bytes=os.path.getsize(p) if os.path.exists(p) else None)
    # r2 fingerprints: things that exist in WS8's code ONLY after round 2
    r2 = OrderedDict(
        cold_charge_acceptance_wired=hasattr(EL8.Pack8, "cold_chg_factor_at"),
        derated_engine_present=hasattr(EN8, "derated_engine"),
        one_spin_rule_present=hasattr(CD8, "machine_idle_mask"),
        errata_switches_present=hasattr(CD8, "ERRATA_ALL"),
        hot_altitude_corner_present=hasattr(VEH, "rho_air_hot_alt"),
        heat_split_in_params=("ENGINE_HEAT_TO_COOLANT_FRAC"
                              in dir(sys.modules["ws8_params"])),
    )
    # r3 fingerprints: things that exist in WS8's code ONLY after ROUND
    # THREE. Every one of them is a NEW OBJECT r3 introduced to close
    # FINDINGS_WS8_r2's blocking finding B1 and the run-closure work that
    # came with it - THE OVERRUN RULE (`overrun_mask` and its two
    # thresholds), the braking mask it is tested against, the per-run
    # exclusivity assertion, the per-sample run closure and the resistor
    # overcommitment booking, and the two r3 errata switches. None of them
    # is an r2 name re-labelled: `git show 4d29aaa^` has none of these
    # names at top level in `ws8_candidates.py`, and the r2 errata tuple is
    # two entries long where r3's is four.
    r3 = OrderedDict(
        overrun_rule_present=hasattr(CD8, "overrun_mask"),
        overrun_thresholds_present=(hasattr(CD8, "OVERRUN_F_TRAC_EPS_N")
                                    and hasattr(CD8, "OVERRUN_RPM_MARGIN")),
        braking_mask_present=hasattr(CD8, "braking_mask"),
        exclusivity_report_present=hasattr(CD8, "exclusivity_report"),
        run_closure_present=hasattr(CD8, "run_closure"),
        resistor_overcommitment_present=hasattr(
            CD8, "resistor_and_overcommitment"),
        b1_errata_switch_present=("b1_overrun_exclusivity"
                                  in getattr(CD8, "ERRATA_ALL", ())),
        s0_launch_fuel_errata_switch_present=(
            "r3_s0_launch_fuel" in getattr(CD8, "ERRATA_ALL", ())),
    )
    fp = OrderedDict(r2_features=r2, r3_features=r3)
    fp["code_round"] = ("r3" if (all(r2.values()) and all(r3.values()))
                        else "r2" if all(r2.values()) else "r1")
    fp["ladder"] = ("r1 -> r2 -> r3. The round reported is the highest one "
                    "ALL of whose features are present; a partial r3 "
                    "reports r2, which is the conservative direction.")
    fp["r3_adjudication"] = (
        "NOT CLEAN - FINDINGS_WS8_r3.md: 'NOT CLEAN. Two blocking, six "
        "material, twelve minor.' No WS8 verdict moved and "
        "`all_unchanged = True`; the adjudicator places both blocking "
        "findings in the round's ACCOUNT OF ITSELF rather than its "
        "physics. WS9 pins this round because BASELINE_v5 R39/ESC-8 orders "
        "it, not because it is clean. IF THE LEAD BOUNCES WS8 TO AN r4 "
        "THIS PIN IS STALE AGAIN. WS9 neither resolves nor softens any WS8 "
        "finding (ESC-WS9-10).")
    # r2 fingerprint values, for the record, unchanged by the ladder above
    for k, v in r2.items():
        fp[k] = v
    return OrderedDict(
        ws8_source_files=src,
        sibling_workstream_sources_reached_through_ws8=sib,
        ws8_artifacts_hashed_but_not_read=art,
        ws8_code_round_fingerprint=fp,
        ws9_own_files={f: dict(sha256=_sha(os.path.join(_HERE, f)))
                       for f in OWN_FILES},
        statement=(
            "WS9 imports WS8's MODELS read-only and reads NO WS8 numeric "
            "artifact (asserted in sanity.no_ws8_artifact_read). The "
            "hashes above pin exactly which WS8 the models came from, "
            "which round the code is at, and - new in the r3-concordant "
            "re-run - the sibling-workstream sources WS9 reaches THROUGH "
            "WS8, which the round-1 pin did not cover. If WS8 regenerates "
            "its ARTIFACTS, none of WS9's numbers move: WS9 re-derives its "
            "own ruler from the same models. If WS8 or a pinned sibling "
            "changes its CODE after this run, the hashes above will not "
            "match and verify_ws9.py says so - that is the hot-swap signal "
            "the assignment asks for, and ESC-WS9-8's 'one-flag' claim is "
            "what this re-run exercised."),
    )


# =====================================================================
#  Corners - R28's set of record, built on WS8 r2's own contexts
# =====================================================================
def corners(quick=False):
    c = OrderedDict()
    c["nominal"] = CD9.Ctx9("nominal", "20 C, sea level, nominal payload")
    if quick:
        return c
    c["payload_plus20"] = CD9.Ctx9(
        "payload_plus20",
        "payload +20% (GCW rises with it: fixed GCW is the trial's "
        "condition, not the corner set's)", payload_factor=1.20)
    c["payload_minus20"] = CD9.Ctx9("payload_minus20", "payload -20%",
                                    payload_factor=0.80)
    c["grade_heavy"] = CD9.Ctx9(
        "grade_heavy",
        "grade-heavy terrain (R28). On the CONTROL duty this turns LH-520 "
        "into WS8's grade-heavy corridor. On the DESIGN duty it is a NULL "
        "OPERATION - the design duty is already the grade-heavy regional "
        "cycle - and WS9 asserts the identity rather than reporting the "
        "same run twice under two names.", grade_heavy=True)
    c["cold_minus10C"] = CD9.Ctx9(
        "cold_minus10C",
        "-10 C (R28): denser air, tyre Crr up 8%, WS3 cold charge "
        "acceptance applied AT THE PACK'S MODELLED TEMPERATURE (R30), cab "
        "heat served from engine coolant when an engine is running and "
        "from the bus when it is not",
        rho_air=VEH.rho_air_cold, t_amb_c=-10.0, cold=True)
    c["hot_alt_2000m_45C"] = CD9.Ctx9(
        "hot_alt_2000m_45C",
        "2,000 m / +45 C (R28): WS4 derate_factor 0.9312 on every engine's "
        "full-load curve and therefore on every continuous rating, thinner "
        "air (rho 0.871), cab COOLING charged to crank and bus alike",
        rho_air=VEH.rho_air_hot_alt, t_amb_c=VEH.t_amb_c_hot_alt,
        alt_m=VEH.alt_m_hot_alt, hot=True)
    return c


def candidate_gcw(cand):
    return (cand.tare_common_kg() + cand.powertrain_mass_kg()
            + cand.payload_kg())


# =====================================================================
#  one (candidate, corner, duty, seed) run
# =====================================================================
def run_one(cand, cycle, seed, tables=None):
    m = candidate_gcw(cand)
    crr = cand.ctx.crr
    dp = PH8.DriverParams()
    tr = PH8.integrate_achieved(
        cycle, cand.envelope, m, cand.lam, dp, seed,
        cda=VEH.CdA, crr=crr, rho=cand.ctx.rho_air,
        v_wind=cycle["v_wind"], v_cap_fn=cand.v_cap, env_tables=tables)
    met = PH8.trace_metrics(tr, m, cda=VEH.CdA, crr=crr,
                            rho=cand.ctx.rho_air)
    acc = cand.account(tr)
    acc = CR9.apply_energy_corrections(cand, acc)
    out = dict(met)
    out.update(acc)
    out["gcw_kg"] = m
    out["payload_kg"] = cand.payload_kg()
    out["fuel_L_per_100km"] = EN8.fuel_L_per_100km(acc["fuel_g_corrected"],
                                                   tr["distance_m"])
    out.update(CR9.metrics_for_run(acc, cand.payload_kg(),
                                   met["distance_km"]))
    return out


def ensemble(vals):
    a = np.asarray([v for v in vals
                    if v is not None and np.isfinite(v)], float)
    if a.size == 0:
        return dict(n=0, min=None, median=None, max=None, mean=None)
    return dict(n=int(a.size), min=float(np.min(a)),
                median=float(np.median(a)), max=float(np.max(a)),
                mean=float(np.mean(a)))


# =====================================================================
#  R34 - the 10 Hz trace export (BASELINE_v5 program hygiene)
# =====================================================================
TRACE_COLS = ("t", "v", "s", "grade", "F_trac", "F_regen", "F_retard",
              "F_friction")

TRACE_SELECTION = tuple(
    ("nominal", c, None, None) for c in
    ("S0R", "S5", "S5-13L", "S6", "S7", "S4p"))
"""WHICH RUNS ARE TRACED, and why it is a declared set rather than all of
them. R34: "Every pipeline exports a 10 Hz trace file per run (feeds the
WS10 exhibit/simulator). WS5, WS9 re-runs, and all later work comply from
their next artifact." WS9's trial is 6 corners x 6 candidates x 2 duties x
8 seeds = 576 runs; at ~74,000 samples each a literal reading is some
gigabytes of CSV, and the program's own three R34 precedents - WS4, WS5 and
WS11, all under this same ruling - each export a declared handful. WS9
follows them and declares its rule: EVERY CANDIDATE INCLUDING THE RULER, on
the DESIGN DUTY (the duty that gates), at the NOMINAL corner, on the FIRST
SEED of the ensemble. That is the full candidate set on the gating duty,
which is what a WS10 exhibit needs to show the trial; the remaining corners
and seeds are reproducible from `run_ws9.py` at zero tolerance, which
`check_determinism_ws9.py` half 3 demonstrates on these very files.
Escalated as ESC-WS9-12 so the lead can order the literal reading if that
is what R34 means."""


def trace_run(corner_name, cname, duty=None, seed=None, whr_name=None):
    """Re-simulate ONE (corner, candidate, duty, seed) run and return
    (candidate, cycle, trace). Deterministic and self-contained, exactly as
    `run_candidate` is, so the determinism checker can call it from a fresh
    process and diff the bytes."""
    duty = DY9.DESIGN_DUTY if duty is None else duty
    seed = int(DY9.seeds()[0]) if seed is None else int(seed)
    ctx = corners(quick=False)[corner_name]
    whr = WHR8.SYSTEMS[whr_name] if whr_name else None
    cand = CD9.CANDIDATES[cname](ctx=ctx, whr=whr)
    tables = PH8.build_env_tables(cand.envelope, cand.lam)
    cyc = DY9.build(duty, seed, ctx)
    if getattr(cand, "predictive", False):
        cyc = DY9.apply_predictive(cyc)
    tr = PH8.integrate_achieved(
        cyc, cand.envelope, candidate_gcw(cand), cand.lam,
        PH8.DriverParams(), seed, cda=VEH.CdA, crr=cand.ctx.crr,
        rho=cand.ctx.rho_air, v_wind=cyc["v_wind"], v_cap_fn=cand.v_cap,
        env_tables=tables)
    return cand, cyc, tr


def write_trace(path, tr, header_lines):
    cols = [np.asarray(tr[k], float) for k in TRACE_COLS]
    n = int(cols[0].size)
    with open(path, "w") as f:
        for h in header_lines:
            f.write("# " + h + "\n")
        f.write(",".join(TRACE_COLS) + "\n")
        for i in range(n):
            f.write(",".join(f"{c[i]:.4f}" for c in cols) + "\n")
    return n


def traces_record(recs, outdir=None):
    """Re-hash every trace on disk and state the R34 position from what is
    actually there, not from what was written."""
    outdir = DATA if outdir is None else outdir
    rows = []
    for r in recs:
        p = os.path.join(outdir, os.path.basename(r["file"]))
        now = _sha(p)
        rows.append(dict(r, present=bool(now is not None),
                         bytes=(os.path.getsize(p) if os.path.exists(p)
                                else None),
                         sha256_on_disk=now,
                         unchanged=bool(now == r.get("sha256"))))
    return OrderedDict(
        rule=("R34 (BASELINE_v5 program hygiene): every pipeline exports a "
              "10 Hz trace file per run, feeding the WS10 exhibit and "
              "simulator; WS5, WS9 RE-RUNS and all later work comply from "
              "their next artifact. This is WS9's next artifact."),
        selection_rule=(
            "every candidate INCLUDING THE RULER, on the DESIGN duty (the "
            "duty that gates), at the NOMINAL corner, on the FIRST seed of "
            "the ensemble - the full candidate set on the gating duty. A "
            "declared subset, following WS4's, WS5's and WS11's precedent "
            "under this same ruling; the literal reading is 576 files and "
            "some gigabytes. Escalated as ESC-WS9-12 rather than decided "
            "here."),
        columns=list(TRACE_COLS),
        sample_rate_Hz=10.0,
        n_files=len(rows),
        total_bytes=sum(r["bytes"] or 0 for r in rows),
        all_present=bool(rows and all(r["present"] for r in rows)),
        all_unchanged_since_written=bool(rows and all(r["unchanged"]
                                                      for r in rows)),
        files=rows)


def export_traces_r34(outdir, selection=TRACE_SELECTION, verbose=True):
    """Write the declared R34 set and return one record per file."""
    out = []
    for corner_name, cname, duty, seed in selection:
        duty = DY9.DESIGN_DUTY if duty is None else duty
        seed = int(DY9.seeds()[0]) if seed is None else int(seed)
        cand, cyc, tr = trace_run(corner_name, cname, duty, seed)
        fn = (f"trace_{cname}_{duty}_{corner_name}_seed{seed}_10Hz.csv")
        n = write_trace(
            os.path.join(outdir, fn), tr,
            ["Project Volt WS9 - R34 10 Hz trace",
             f"{cname} ({cand.spec()['title']}) / duty {duty} / corner "
             f"{corner_name} / seed {seed}",
             f"GCW {candidate_gcw(cand):.1f} kg, payload "
             f"{cand.payload_kg():.1f} kg, powertrain "
             f"{cand.powertrain_mass_kg():.1f} kg",
             "columns: t [s], v [m/s], s [m], grade [-], and the four "
             "commanded force channels at the CONTACT PATCH [N] - "
             "traction, regenerative braking, retarder, friction brake. "
             "The integrator never commands traction and a braking "
             "channel on the same sample.",
             "electrical quantities are NOT in this file; they are "
             "per-candidate dispatch and live in results_ws9.json"])
        rec = dict(file=f"data/{fn}", candidate=cname, duty=duty,
                   corner=corner_name, seed=seed, rows=n,
                   dt_s=float(tr["dt"]), distance_m=float(tr["distance_m"]),
                   duration_s=float(tr["duration_s"]),
                   sha256=_sha(os.path.join(outdir, fn)))
        out.append(rec)
        if verbose:
            print(f"    R34 trace {fn} ({n:,} rows)", flush=True)
    return out


def run_candidate(corner_name, cname, whr_name, seeds):
    """One (corner, candidate) job, over BOTH duty classes.

    Self-contained and deterministic so it can run in a worker process
    without changing a digit: it rebuilds its own context and candidate from
    names and every draw is seeded."""
    ctx = corners(quick=False)[corner_name]
    whr = WHR8.SYSTEMS[whr_name] if whr_name else None
    cand = CD9.CANDIDATES[cname](ctx=ctx, whr=whr)
    tables = PH8.build_env_tables(cand.envelope, cand.lam)
    per_duty = OrderedDict()
    for duty in DY9.DUTIES:
        rows = []
        for sd in seeds:
            cyc = DY9.build(duty, sd, ctx)
            if getattr(cand, "predictive", False):
                cyc = DY9.apply_predictive(cyc)
            r = run_one(cand, cyc, sd, tables=tables)
            r["seed"] = int(sd)
            r["duty"] = duty
            if "predictive" in cyc:
                r["predictive"] = cyc["predictive"]
            rows.append(r)
        per_duty[duty] = dict(
            per_seed=rows,
            ensemble={
                k: ensemble([x[k] for x in rows])
                for k in ("MJ_primary_per_payload_tkm",
                          "MJ_tank_per_payload_tkm",
                          "g_CO2_per_payload_tkm", "MJ_primary_per_km",
                          "fuel_L_per_100km", "payload_kg", "duration_s",
                          "avg_speed_kmh", "unserved_kWh",
                          "correction_share_of_fuel", "grid_kWh",
                          "power_limited_fraction",
                          "MJ_primary_per_payload_tkm_grid_lo",
                          "MJ_primary_per_payload_tkm_grid_hi",
                          "g_CO2_per_payload_tkm_grid_lo",
                          "g_CO2_per_payload_tkm_grid_hi")})
    return cname, dict(spec=cand.spec(), per_duty=per_duty)


def _job(args):
    return run_candidate(*args)


def run_corner(corner_name, seeds, cand_names, whr_name=None, pool=None,
               verbose=True):
    jobs = [(corner_name, c, whr_name, tuple(seeds)) for c in cand_names]
    if pool is not None:
        results = dict(pool.map(_job, jobs))
    else:
        results = dict(_job(j) for j in jobs)
    out = OrderedDict()
    for cname in cand_names:
        if cname not in results:
            continue
        out[cname] = results[cname]
        if verbose:
            e = out[cname]["per_duty"][DY9.DESIGN_DUTY]["ensemble"]
            e2 = out[cname]["per_duty"][DY9.CONTROL_DUTY]["ensemble"]
            print(f"    {cname:8s}: payload "
                  f"{out[cname]['spec']['payload_kg']:8.1f} kg   design "
                  f"{e['MJ_primary_per_payload_tkm']['median']:.4f}   "
                  f"control "
                  f"{e2['MJ_primary_per_payload_tkm']['median']:.4f} "
                  f"MJ_primary/payload-tkm", flush=True)
    return out


def margins_vs_ruler(corner_result, metric="MJ_primary_per_payload_tkm"):
    """Per-seed margin against the RULER on the SAME seed and the SAME duty,
    then the ensemble. Paired by seed deliberately: the seed sets the
    corridor, the wind and the driver, so pairing removes the cycle draw
    from the comparison instead of leaving it in the variance."""
    if RULER not in corner_result:
        return {}
    out = OrderedDict()
    for duty in DY9.DUTIES:
        base = {r["seed"]: r[metric]
                for r in corner_result[RULER]["per_duty"][duty]["per_seed"]}
        d = OrderedDict()
        for cname, blob in corner_result.items():
            if cname == RULER:
                continue
            per_seed = []
            for r in blob["per_duty"][duty]["per_seed"]:
                b = base.get(r["seed"])
                if b:
                    per_seed.append(dict(
                        seed=r["seed"],
                        margin_pct=(b - r[metric]) / b * 100.0))
            d[cname] = dict(per_seed=per_seed,
                            ensemble=ensemble([p["margin_pct"]
                                               for p in per_seed]))
        out[duty] = d
    return out


# =====================================================================
#  advance / kill - read on the DESIGN duty (assignment)
# =====================================================================
def advance_kill(margins_by_corner):
    """The criteria, quoted from the assignment: 'ADVANCE only if >=3%
    better than S0 on the DESIGN DUTY at nominal, ensemble-min, AND >=0% at
    every R28 corner; report the control-duty result alongside without it
    gating.'"""
    design, control = DY9.DESIGN_DUTY, DY9.CONTROL_DUTY
    cands = sorted({c for m in margins_by_corner.values()
                    for c in m.get(design, {})})
    out = OrderedDict()
    for cname in cands:
        nom = margins_by_corner.get("nominal", {}).get(design, {}).get(cname)
        if nom is None:
            continue
        nom_min = nom["ensemble"]["min"]
        rows = []
        for corner, m in margins_by_corner.items():
            if corner == "nominal" or cname not in m.get(design, {}):
                continue
            e = m[design][cname]["ensemble"]
            rows.append(dict(corner=corner, **{k: e[k]
                                               for k in ("min", "median",
                                                         "max")}))
        worst = min(rows, key=lambda r: r["min"]) if rows else None
        pass_nom = nom_min >= P9.ADVANCE_NOMINAL_PCT
        pass_cor = (worst is None) or (worst["min"]
                                       >= P9.ADVANCE_CORNER_PCT)
        ctrl = margins_by_corner.get("nominal", {}).get(control,
                                                        {}).get(cname)
        out[cname] = dict(
            design_duty=design,
            nominal_margin_pct_min=nom_min,
            nominal_margin_pct_median=nom["ensemble"]["median"],
            nominal_margin_pct_max=nom["ensemble"]["max"],
            corners=rows,
            worst_corner=worst["corner"] if worst else None,
            worst_corner_margin_pct_min=worst["min"] if worst else None,
            control_duty_nominal_margin_pct_min=(
                ctrl["ensemble"]["min"] if ctrl else None),
            control_duty_nominal_margin_pct_median=(
                ctrl["ensemble"]["median"] if ctrl else None),
            control_duty_gates=False,
            passes_nominal_3pct=bool(pass_nom),
            passes_all_corners_0pct=bool(pass_cor),
            verdict="ADVANCE" if (pass_nom and pass_cor) else "KILL",
            binding_reason=(
                "meets both criteria" if (pass_nom and pass_cor)
                else ("fails the nominal >=3% criterion on the design duty"
                      if not pass_nom
                      else f"fails the >=0% corner criterion at "
                           f"{worst['corner']}")))
    return dict(
        criteria=dict(nominal_pct=P9.ADVANCE_NOMINAL_PCT,
                      every_corner_pct=P9.ADVANCE_CORNER_PCT,
                      statistic=P9.ADVANCE_STATISTIC,
                      duty=P9.ADVANCE_DUTY,
                      metric="primary energy per payload tonne-km",
                      pre_committed=True, text=P9.ADVANCE_TEXT,
                      control_duty=control,
                      control_duty_gates=False),
        candidates=out,
        any_advance=bool(any(v["verdict"] == "ADVANCE"
                             for v in out.values())))


def verdict_robustness(R):
    """Would the verdicts survive the sensitivity ESC-3 itself orders?

    ESC-3 requires the grid primary-energy factor and CO2 intensity to be
    swept +/-50%, and the factors are DECLARED rather than sourced
    (ESC-WS9-2). A sensitivity that is reported but never read against the
    criteria is decoration. So the pre-committed criteria are re-applied,
    unchanged, to the same runs priced at each end of the sweep - and the
    result is reported whether or not it is convenient.

    For every candidate that imports no grid energy the three verdicts are
    IDENTICAL by construction, which is the same invariance the sanity
    block asserts. Only a plug-in can move."""
    design = DY9.DESIGN_DUTY
    out = OrderedDict()
    for tag, key in (("grid_factor_minus50pct", "margins_grid_lo"),
                     ("declared", "margins"),
                     ("grid_factor_plus50pct", "margins_grid_hi")):
        ak = advance_kill(R[key])
        out[tag] = OrderedDict(
            (c, dict(nominal_margin_pct_min=v["nominal_margin_pct_min"],
                     worst_corner=v["worst_corner"],
                     worst_corner_margin_pct_min=v[
                         "worst_corner_margin_pct_min"],
                     verdict=v["verdict"]))
            for c, v in ak["candidates"].items())
    cands = list(out["declared"])
    flips = {c: sorted({out[t][c]["verdict"] for t in out})
             for c in cands}
    return dict(
        duty=design,
        basis=("the SAME pre-committed criteria, unchanged, applied to the "
               "same runs priced at each end of the +/-50% grid-factor "
               "sweep ESC-3 orders"),
        by_factor=out,
        verdict_set_per_candidate=flips,
        candidates_whose_verdict_moves=[c for c, v in flips.items()
                                        if len(v) > 1],
        all_verdicts_robust=bool(not [c for c, v in flips.items()
                                      if len(v) > 1]))


# =====================================================================
#  The two walls, addressed by construction (assignment, S5)
# =====================================================================
def two_walls_block():
    eta_h = DL.eta_amt_direct * DL.eta_axle_tandem * DL.eta_driveshaft
    eta_l = DL.eta_amt_indirect * DL.eta_axle_tandem * DL.eta_driveshaft
    out = OrderedDict()
    for key, eng in (("ENG-11L", EN8.ENG_11L), ("ENG-13L", EN8.ENG_13L)):
        w = W9.solve_two_speed(
            eng, 105.0 / 3.6, P9.DOGBOX.rpm_ceiling, P9.DOGBOX.rpm_lug_floor,
            eta_h, eta_l, grade=0.06, m=VEH.m_gcw, rho_air=VEH.rho_air,
            margin=P9.S5_GRADE_MARGIN,
            contiguity_margin=P9.DOGBOX.contiguity_margin)
        v = W9.verify_walls_sweep(
            eng, w["ratio_high"], w["ratio_low"], eta_h, eta_l,
            P9.DOGBOX.rpm_ceiling, P9.DOGBOX.rpm_lug_floor,
            rho_air=VEH.rho_air)
        out[key] = dict(solve=w, sweep=v)
    # THE THIRD CONSTRAINT, exposed by the design duty
    third = OrderedDict()
    for key, cname in (("ENG-11L", "S5"), ("ENG-13L", "S5-13L")):
        cand = CD9.CANDIDATES[cname](ctx=CD9.NOMINAL)
        third[key] = W9.coupling_floor_vs_grade(
            cand.engine_base, cand.r_low, cand.eta_low,
            P9.DOGBOX.rpm_lug_floor, P9.DOGBOX.rpm_ceiling,
            cand.pack_sustained_kw(),
            grades=(0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11),
            rho_air=VEH.rho_air)
        third[key]["frontier"] = W9.two_speed_frontier(
            cand.engine_base, 105.0 / 3.6, P9.DOGBOX.rpm_ceiling,
            P9.DOGBOX.rpm_lug_floor, cand.eta_high, cand.eta_low,
            contiguity_margin=P9.DOGBOX.contiguity_margin,
            rho_air=VEH.rho_air, margin=P9.S5_GRADE_MARGIN)

    # WS8's single-ratio result, re-derived here on the same algebra, so
    # the WS9 answer and the WS8 kill are visibly the same physics
    single = OrderedDict()
    r_ceiling = W9.ratio_ceiling(105.0 / 3.6, P9.DOGBOX.rpm_ceiling)
    for key, eng in (("ENG-11L", EN8.ENG_11L), ("ENG-13L", EN8.ENG_13L)):
        req = W9.grade_force_required_N(0.06, VEH.m_gcw, VEH.rho_air)
        t_peak = float(np.max(eng.trq_pts))
        f_at_ceiling = t_peak * r_ceiling * eta_l / VEH.r_dyn
        single[key] = dict(
            ratio_ceiling_closed_form=r_ceiling,
            F_available_at_ceiling_kN=f_at_ceiling / 1e3,
            F_required_6pct_kN=req["total_N"] / 1e3,
            ratio_required_for_6pct=W9.ratio_floor(req["total_N"], t_peak,
                                                   eta_l),
            span_needed=W9.ratio_floor(req["total_N"], t_peak, eta_l)
            / r_ceiling,
            single_ratio_feasible=bool(f_at_ceiling >= req["total_N"]))
    return dict(
        wall1=("a single fixed engine ratio cannot span 105 km/h cruise "
               "under the 2,100 rpm ceiling AND the 6% grade at 36,300 kg "
               "(R25, D8)"),
        wall2=("at fixed GCW every powertrain kilogram displaces payload "
               "1:1, so the objective function is efficiency per added "
               "kilogram (D8)"),
        single_ratio_closed_form=single,
        two_speed_solve=out,
        third_constraint_coupling_floor=third,
        ratio_law=dict(
            statement=("with contiguity tight and Wall 2 tight, cruise "
                       "engine speed x engine peak torque is a CONSTANT "
                       "at fixed GCW and grade requirement: "
                       "n_cruise = v * k * F_6% * (1+margin) * r_dyn / "
                       "(T_peak * eta_low * span)"),
            constant_at_100kmh=(100.0 / 3.6) * W9.RPM_PER_RATIO_PER_MS
            * W9.grade_force_required_N(0.06, VEH.m_gcw,
                                        VEH.rho_air)["total_N"]
            * (1.0 + P9.S5_GRADE_MARGIN) * VEH.r_dyn
            / (eta_l * P9.DOGBOX.span_used),
            consequence=("a minimal transmission wants a BIG-TORQUE "
                         "engine: torque is what buys back the ratio span, "
                         "so downsizing the engine of a 2-speed truck "
                         "raises its cruise engine speed in exact "
                         "proportion. That inverts the usual downsizing "
                         "instinct and is why S5 is run on two engines.")),
        mass_ledger_note=("Wall 2 is addressed by the mass ledger, stated "
                          "to the kilogram in section 4.1 and exported in "
                          "data/mass_ledger.csv"))


# =====================================================================
#  F7 - the ruler's calibration cross-check, AS AN ENSEMBLE
# =====================================================================
ICCT_TYPICAL_L_PER_100KM = 32.6
ICCT_BEST_IN_CLASS_L_PER_100KM = 29.9
ICCT_AT_REG_PAYLOAD_L_PER_100KM = 33.1
ICCT_REG_PAYLOAD_T = 19.3


def f7_crosscheck(seeds, ctx):
    """WS8 finding F7, material: the report's only external anchor was
    asserted on a MEDIAN while its own 8-seed envelope spanned the entire
    reference band, and the comparison was not mass-matched.

    WS9's ruler is a different vehicle from WS8's S0 - it carries 130 kg of
    retarder - so the cross-check has to be re-run anyway. It is re-run HERE
    as an ENSEMBLE (rule 4), at the reference's OWN payload as well as at
    WS9's, with the residual stated either way.  [R2-IMPL F7]"""
    out = OrderedDict()
    for tag, payload_factor in (("as_specified", None),
                                ("mass_matched_to_reference", "icct")):
        c = CD9.Ctx9("nominal", "F7 cross-check")
        cand = CD9.S0R(ctx=c)
        if payload_factor == "icct":
            # hold the reference cycle's regulatory payload instead of ours
            base = cand.payload_kg()
            c2 = CD9.Ctx9("nominal", "F7 cross-check, mass-matched",
                          payload_factor=ICCT_REG_PAYLOAD_T * 1000.0 / base)
            cand = CD9.S0R(ctx=c2)
        tables = PH8.build_env_tables(cand.envelope, cand.lam)
        rows = []
        for sd in seeds:
            cyc = DY9.build_flat_control(sd)
            rows.append(run_one(cand, cyc, sd, tables=tables))
        out[tag] = dict(
            payload_kg=cand.payload_kg(),
            gcw_kg=candidate_gcw(cand),
            L_per_100km=ensemble([r["fuel_L_per_100km"] for r in rows]),
            avg_speed_kmh=ensemble([r["avg_speed_kmh"] for r in rows]))
    ens = out["as_specified"]["L_per_100km"]
    mm = out["mass_matched_to_reference"]["L_per_100km"]
    band_lo, band_hi = (ICCT_BEST_IN_CLASS_L_PER_100KM,
                        ICCT_AT_REG_PAYLOAD_L_PER_100KM)
    return dict(
        cycle="LH-520 with grade zeroed (terrain isolated), ruler S0R",
        results=out,
        reference=dict(
            source=P9.CITATIONS["ICCT_TUV"]["source"],
            url=P9.CITATIONS["ICCT_TUV"]["url"],
            typical_EU_L_per_100km=ICCT_TYPICAL_L_PER_100KM,
            best_in_class_EU_L_per_100km=ICCT_BEST_IN_CLASS_L_PER_100KM,
            at_regulatory_payload_L_per_100km=(
                ICCT_AT_REG_PAYLOAD_L_PER_100KM),
            regulatory_payload_t=ICCT_REG_PAYLOAD_T,
            evidence_quality=P9.CITATIONS["ICCT_TUV"]["evidence_quality"]),
        envelope_vs_band=dict(
            rule="the 8-seed ENVELOPE against the published band, not a "
                 "point statistic against a point (F7)",
            model_min=ens["min"], model_median=ens["median"],
            model_max=ens["max"],
            band_min=band_lo, band_max=band_hi,
            envelope_wider_than_band=bool(
                (ens["max"] - ens["min"]) > (band_hi - band_lo)),
            median_residual_pct=100.0 * (ens["median"]
                                         - ICCT_TYPICAL_L_PER_100KM)
            / ICCT_TYPICAL_L_PER_100KM,
            mass_matched_median=mm["median"],
            mass_matched_residual_vs_at_reg_payload_pct=100.0 * (
                mm["median"] - ICCT_AT_REG_PAYLOAD_L_PER_100KM)
            / ICCT_AT_REG_PAYLOAD_L_PER_100KM),
        statement=(
            "F7's disposition, executed: the cross-check is rendered as an "
            "8-seed envelope like every other stochastic quantity in this "
            "report; the reference combination's payload is stated and the "
            "check is ALSO run mass-matched to it; and no claim of "
            "agreement is made beyond what the envelope supports."))


# =====================================================================
#  The electric-turbocompound gate on the DESIGN duty (R31)
# =====================================================================
def etc_gate(seeds, base_trial, pool=None):
    """R31: electric turbocompound is admitted to S6 ONLY if it clears the
    same 2.5% net gate ON THE DESIGN DUTY, whose load fraction is higher
    than the fleet average WS8 tested against. Pre-committed; measured, not
    argued."""
    trial = run_corner("nominal", seeds, ["S6-ETC"], whr_name="ETC",
                       pool=pool, verbose=False)
    if "S6-ETC" not in trial:
        return dict(status="NOT RUN")
    out = OrderedDict()
    for duty in DY9.DUTIES:
        base = {r["seed"]: r["MJ_primary_per_payload_tkm"]
                for r in base_trial["S6"]["per_duty"][duty]["per_seed"]}
        per_seed = []
        for r in trial["S6-ETC"]["per_duty"][duty]["per_seed"]:
            b = base.get(r["seed"])
            if b:
                per_seed.append(dict(
                    seed=r["seed"],
                    net_margin_pct=(b - r["MJ_primary_per_payload_tkm"])
                    / b * 100.0))
        out[duty] = dict(per_seed=per_seed,
                         ensemble=ensemble([p["net_margin_pct"]
                                            for p in per_seed]))
    pay0 = base_trial["S6"]["spec"]["payload_kg"]
    pay1 = trial["S6-ETC"]["spec"]["payload_kg"]
    pen = (pay0 - pay1) / pay1 * 100.0
    e = out[DY9.DESIGN_DUTY]["ensemble"]
    passes = bool(e["min"] is not None and e["min"] >= P9.WHR_GATE_PCT)
    return dict(
        gate=dict(threshold_pct=P9.WHR_GATE_PCT,
                  basis="net PRIMARY energy per payload tonne-km on the "
                        "DESIGN DUTY, AFTER the mass charge, ensemble-min "
                        "against the threshold (the statistic G1 and WS8's "
                        "own WHR gate were read on)",
                  pre_committed=True, duty=DY9.DESIGN_DUTY,
                  ruling="R31 / assignment: 'electric turbocompound ONLY "
                         "if it clears the 2.5% net gate on the design "
                         "duty'"),
        system=WHR8.SYSTEMS["ETC"].spec(),
        mass_charge_kg=WHR8.SYSTEMS["ETC"].mass_kg,
        payload_before_kg=pay0, payload_after_kg=pay1,
        payload_penalty_pct=pen,
        fuel_gain_needed_to_clear_gate_pct=P9.WHR_GATE_PCT + pen,
        by_duty=out,
        design_duty_net_margin_pct_min=e["min"],
        design_duty_net_margin_pct_median=e["median"],
        passes_gate=passes,
        verdict="ADOPT" if passes else "DROPPED",
        spec=trial["S6-ETC"]["spec"], trial=trial["S6-ETC"])


# =====================================================================
#  Heat ledger for WS6 (rule 7) - rebuilt per finding F1
# =====================================================================
HEAT_ROWS = ("engine_coolant_kW", "hydraulic_retarder_coolant_kW",
             "engine_exhaust_kW", "compression_brake_exhaust_kW",
             "traction_machine_inverter_kW", "generator_rectifier_kW",
             "pack_kW", "brake_resistor_kW", "friction_brake_kW",
             "driveline_kW")


def _steady_climb_speed(cand, grade, m):
    lo, hi = 1.0, 33.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f_t, _, _ = cand.envelope(mid)
        f_r, _, _, _ = PH8.road_load_force(np.array([mid]), grade, m,
                                           rho=cand.ctx.rho_air)
        if f_t >= float(f_r[0]):
            lo = mid
        else:
            hi = mid
    return lo


def component_heat_kw(cand, v, grade, m, pack_saturated=False):
    """Heat rejected by each component at one (speed, grade) case, booked
    BY PHYSICAL LOCATION.

    WS8's finding F1 (blocking) named four defects in its own ledger and
    all four are addressed here:
      (a) the governing case was outside the enumerated set -> a
          PACK-SATURATED descent case is enumerated, and the SIMULATED
          peaks over every (candidate, corner, duty, seed) are exported
          alongside as their own enumerated member;
      (b) compression-brake heat was booked to the brake resistor and the
          exhaust row was zeroed -> the retard channel is SPLIT into
          hydraulic retarder (-> ENGINE COOLANT), compression brake (->
          EXHAUST) and resistor (-> AIR), each to its own row;
      (c) foundation-brake heat had no row at all -> it has one;
      (d) nothing was asserted against the rating of the hardware whose
          mass was charged -> every row is checked against its rating and
          the closure of the case is asserted.
    """
    ctx = cand.ctx
    f_res, _, _, _ = PH8.road_load_force(np.array([v]), grade, m,
                                         rho=ctx.rho_air)
    p_wheel_kw = float(f_res[0]) * v / 1e3
    out = OrderedDict((k, 0.0) for k in HEAT_ROWS)
    out["case_wheel_power_kW"] = p_wheel_kw
    out["road_speed_kmh"] = v * 3.6
    ed = getattr(cand, "edrive", None)
    pack = getattr(cand, "pack", None)
    line = getattr(cand, "line", None)
    amt = getattr(cand, "amt", None)

    if p_wheel_kw >= 0.0:                    # ---------------- driving
        if amt is not None:                  # S0R / S6 / S7 tractor
            gi, _ = amt.select_gear(v, float(f_res[0]))
            rpm = amt.engine_rpm(v, gi)
            p_shaft = p_wheel_kw / max(amt.eta(gi), 1e-6) + ctx.aux_mech_kw
            trq = min(p_shaft * 1e3 / (rpm * 2 * np.pi / 60.0),
                      float(cand.engine.t_max(rpm)))
            b = float(cand.engine.bsfc(rpm, trq))
            p_fuel = b * p_shaft / 3600.0 * LHV_KJ_PER_G
            q = max(p_fuel - p_shaft, 0.0)
            out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
            out["engine_exhaust_kW"] = q * (1 - ENGINE_HEAT_TO_COOLANT_FRAC)
            out["driveline_kW"] = p_shaft - p_wheel_kw - ctx.aux_mech_kw
        elif line is not None:               # S4' series
            eta = float(ed.eta_bus_to_wheel(v, p_wheel_kw))
            p_bus = p_wheel_kw / max(eta, 1e-6) + ctx.aux_bus_kw
            out["traction_machine_inverter_kW"] = (p_wheel_kw
                                                   / max(eta, 1e-6)
                                                   - p_wheel_kw)
            p_e = min(p_bus, line.p_elec_max_kw)
            rpm = float(line.rpm(p_e))
            p_shaft = float(line.generator.shaft_from_elec(
                np.array([rpm]), np.array([p_e]))[0])
            out["generator_rectifier_kW"] = max(p_shaft - p_e, 0.0)
            b = float(np.interp(p_e, line.p_grid, line.bsfc))
            p_fuel = b * p_shaft / 3600.0 * LHV_KJ_PER_G
            q = max(p_fuel - p_shaft, 0.0)
            out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
            out["engine_exhaust_kW"] = q * (1 - ENGINE_HEAT_TO_COOLANT_FRAC)
            out["driveline_kW"] = p_wheel_kw * (1.0 - DL.eta_axle_tandem)
            if pack is not None:
                out["pack_kW"] = abs(p_bus) * (1.0 - pack.eta_dis) * 0.5
        else:                                # S5: engine through the box
            f_eng = float(cand._engine_force_N(np.array([v]))[0])
            f_eng = min(f_eng, float(f_res[0]))
            rpm = float(np.clip(cand._engine_rpm(np.array([v]))[0],
                                cand.engine.idle_rpm,
                                cand.box.rpm_ceiling))
            g_of = int(cand._gear_of(np.array([v]))[0])
            eta_g = (cand.eta_high if g_of == 1
                     else cand.eta_low if g_of == 0 else 1.0)
            p_eng_wheel = f_eng * v / 1e3
            p_shaft = p_eng_wheel / max(eta_g, 1e-6)
            if rpm > 0 and p_shaft > 0:
                trq = min(p_shaft * 1e3 / (rpm * 2 * np.pi / 60.0),
                          float(cand.engine.t_max(rpm)))
                b = float(cand.engine.bsfc(rpm, trq))
                q = max(b * p_shaft / 3600.0 * LHV_KJ_PER_G - p_shaft, 0.0)
            else:
                q = 0.0
            out["engine_coolant_kW"] = q * ENGINE_HEAT_TO_COOLANT_FRAC
            out["engine_exhaust_kW"] = q * (1 - ENGINE_HEAT_TO_COOLANT_FRAC)
            out["driveline_kW"] = max(p_shaft - p_eng_wheel, 0.0)
            p_m_wheel = max(p_wheel_kw - p_eng_wheel, 0.0)
            if p_m_wheel > 0 and ed is not None:
                eta = float(ed.eta_bus_to_wheel(v, p_m_wheel))
                out["traction_machine_inverter_kW"] = (p_m_wheel
                                                       / max(eta, 1e-6)
                                                       - p_m_wheel)
    else:                                    # --------------- descending
        need_kw = -p_wheel_kw
        f_t, f_rg, f_rx = cand.envelope(v)
        # retarder first (S0R/S7 policy), then compression brake, then the
        # resistor; each to its own physical destination
        p_ret = 0.0
        if hasattr(cand, "retarder_force_N"):
            p_ret = min(need_kw, float(cand.retarder_force_N(v)) * v / 1e3)
        rest = max(need_kw - p_ret, 0.0)
        p_eb = 0.0
        if amt is not None:
            p_eb = min(rest, amt.engine_brake_force(
                v, cand.p_engine_brake_kw) * v / 1e3)
        elif hasattr(cand, "_engine_brake_force_N"):
            p_eb = min(rest, float(cand._engine_brake_force_N(
                np.array([v]))[0]) * v / 1e3)
        rest = max(rest - p_eb, 0.0)
        p_rg = 0.0
        if not pack_saturated and pack is not None and ed is not None:
            p_rg = min(rest, f_rg * v / 1e3)
        rest = max(rest - p_rg, 0.0)
        p_res = 0.0
        if ed is not None:
            p_res = min(rest, getattr(cand, "resistor_kw", 0.0))
        rest = max(rest - p_res, 0.0)
        p_fric = rest
        out["hydraulic_retarder_coolant_kW"] = p_ret
        out["compression_brake_exhaust_kW"] = p_eb
        out["friction_brake_kW"] = p_fric
        if ed is not None:
            eta = float(ed.eta_wheel_to_bus(v, max(p_rg + p_res, 1e-9)))
            out["traction_machine_inverter_kW"] = (p_rg + p_res) * (1.0
                                                                    - eta)
            out["brake_resistor_kW"] = p_res * eta
            if pack is not None:
                out["pack_kW"] = p_rg * eta * (1.0 - pack.eta_chg)
                # energy that goes INTO the pack is stored, not rejected -
                # so the closure test below must count it separately or a
                # correct ledger would look as though it had lost heat
                out["pack_stored_not_rejected_kW"] = (p_rg * eta
                                                      * pack.eta_chg)
    out.setdefault("pack_stored_not_rejected_kW", 0.0)
    out["total_rejected_kW"] = sum(out[k] for k in HEAT_ROWS)
    # (d) rating checks against the hardware whose mass was charged
    checks = dict(
        resistor_rating_kW=float(getattr(cand, "resistor_kw", 0.0)),
        resistor_within_rating=bool(
            out["brake_resistor_kW"]
            <= float(getattr(cand, "resistor_kw", 0.0)) + 1e-6),
        retarder_rating_kW=(P9.RET.p_continuous_kW
                            if hasattr(cand, "retarder_force_N") else 0.0),
        retarder_within_rating=bool(
            out["hydraulic_retarder_coolant_kW"]
            <= (P9.RET.p_continuous_kW
                if hasattr(cand, "retarder_force_N") else 0.0) + 1e-6),
        friction_allowance_kW=CD9.FRICTION_ALLOWANCE_KW,
        friction_within_allowance=bool(
            out["friction_brake_kW"] <= CD9.FRICTION_ALLOWANCE_KW + 1e-6),
        friction_note=(
            "friction above the declared continuous allowance is a "
            "CAPABILITY finding, not a rating breach: it says the "
            "candidate cannot hold the case's speed on its own retarding "
            "hardware and must descend more slowly. It is reported as such "
            "and is NOT counted among the rating violations, which are "
            "about hardware whose mass was charged."))
    if p_wheel_kw < 0.0:
        # F1(c): the case must CLOSE. On a descent the retarding power the
        # case demands leaves as heat through the enumerated rows OR is
        # stored in the pack; nothing else may absorb it.
        closed = abs(out["total_rejected_kW"]
                     + out["pack_stored_not_rejected_kW"] - (-p_wheel_kw))
        checks["descent_closure_residual_kW"] = closed
        checks["descent_stored_in_pack_kW"] = out[
            "pack_stored_not_rejected_kW"]
        checks["descent_closes"] = bool(closed < 1.0)
    out["checks"] = checks
    return out


def heat_ledger(ctx, trial_all):
    """Enumerated case set, per candidate, with the governing case labelled
    (R14) and the simulated peaks INSIDE the set (F1(a))."""
    cases = OrderedDict([
        ("cruise_95kmh_flat", dict(v=95 / 3.6, grade=0.0, sat=False)),
        ("climb_6pct", dict(v=None, grade=0.06, sat=False)),
        ("descent_6pct_pack_capable", dict(v=None, grade=-0.06, sat=False)),
        ("descent_6pct_pack_saturated", dict(v=None, grade=-0.06,
                                             sat=True)),
    ])
    SUSTAINED = tuple(cases)
    TRANSIENT = ("simulated_peak_over_all_runs",)
    out = OrderedDict()
    for cname in CD9.FULL_SET:
        cand = CD9.CANDIDATES[cname](ctx=ctx)
        m = candidate_gcw(cand)
        rows = OrderedDict()
        for case, spec in cases.items():
            grade = spec["grade"]
            if spec["v"] is not None:
                v = spec["v"]
            elif grade > 0:
                v = _steady_climb_speed(cand, grade, m)
            else:
                v = min(cand.v_cap(grade), 100.0 / 3.6)
            rows[case] = component_heat_kw(cand, v, grade, m,
                                           pack_saturated=spec["sat"])
            rows[case]["duration_class"] = "sustained"
        # (a) the SIMULATED peaks, as their own enumerated member
        peaks = OrderedDict((k, 0.0) for k in HEAT_ROWS)
        gov = {}
        for corner, blob in trial_all.items():
            r = blob.get(cname)
            if r is None:
                continue
            for duty, d in r["per_duty"].items():
                for row in d["per_seed"]:
                    for key, field in (
                            ("brake_resistor_kW", "resistor_peak_kW"),
                            ("hydraulic_retarder_coolant_kW",
                             "retarder_peak_kW"),
                            ("compression_brake_exhaust_kW",
                             "engine_brake_peak_kW"),
                            ("friction_brake_kW",
                             "friction_brake_peak_kW")):
                        val = float(row.get(field, 0.0) or 0.0)
                        if val > peaks[key]:
                            peaks[key] = val
                            gov[key] = (f"{corner}/{duty}/"
                                        f"seed{row['seed']}")
        peaks["case_wheel_power_kW"] = None
        peaks["road_speed_kmh"] = None
        peaks["total_rejected_kW"] = sum(
            v for v in (peaks[k] for k in HEAT_ROWS) if v)
        peaks["governing_run"] = gov
        peaks["duration_class"] = "transient peak"
        peaks["checks"] = dict(
            resistor_rating_kW=float(getattr(cand, "resistor_kw", 0.0)),
            resistor_within_rating=bool(
                peaks["brake_resistor_kW"]
                <= float(getattr(cand, "resistor_kw", 0.0)) + 1e-6),
            retarder_rating_kW=(P9.RET.p_continuous_kW
                                if hasattr(cand, "retarder_force_N")
                                else 0.0),
            retarder_within_rating=bool(
                peaks["hydraulic_retarder_coolant_kW"]
                <= (P9.RET.p_continuous_kW
                    if hasattr(cand, "retarder_force_N") else 0.0) + 1e-6))
        rows["simulated_peak_over_all_runs"] = peaks
        worst, worst_sus = {}, {}
        for k in HEAT_ROWS:
            vals = {c: float(rows[c].get(k, 0.0) or 0.0) for c in rows}
            g = max(vals, key=lambda c: vals[c])
            worst[k] = dict(rule="max over the FULL enumerated case set, "
                                 "sustained cases AND the transient "
                                 "simulated peak",
                            cases=vals, value=vals[g], governing_case=g,
                            duration_class=rows[g].get("duration_class"),
                            governing_run=(rows["simulated_peak_over_all_"
                                                "runs"]["governing_run"]
                                           .get(k)
                                           if g == "simulated_peak_over_"
                                           "all_runs" else None))
            sv = {c: vals[c] for c in SUSTAINED}
            gs = max(sv, key=lambda c: sv[c])
            worst_sus[k] = dict(
                rule="max over the SUSTAINED case set only - the number a "
                     "cooling package is sized on",
                cases=sv, value=sv[gs], governing_case=gs,
                duration_class="sustained")
        out[cname] = dict(cases=rows, worst_case=worst,
                          worst_case_sustained=worst_sus)
    return dict(
        convention=(
            "component heat rejection [kW], bus-side electrical quantities "
            f"per R12; engine heat split {ENGINE_HEAT_TO_COOLANT_FRAC:.2f} "
            f"coolant+CAC / {1-ENGINE_HEAT_TO_COOLANT_FRAC:.2f} "
            "exhaust+radiation (inherited from ws8_params, r2)"),
        rows_by_physical_location=dict(
            engine_coolant_kW="radiator / charge-air cooler",
            hydraulic_retarder_coolant_kW=(
                "the SAME coolant circuit - a secondary hydrodynamic "
                "retarder rejects through a heat exchanger into the engine "
                "cooling system, so WS6 must add this row to the coolant "
                "one and size one package for the sum"),
            engine_exhaust_kW="exhaust and surface radiation",
            compression_brake_exhaust_kW=(
                "exhaust - a compression brake is an exhaust-side device "
                "and its heat does NOT go to the resistor bank (F1(b))"),
            traction_machine_inverter_kW="machine jacket and inverter "
                                         "cold plate",
            generator_rectifier_kW="generator jacket and rectifier",
            pack_kW="pack coolant loop",
            brake_resistor_kW="air, through a grid resistor bank",
            friction_brake_kW=(
                "foundation brakes, to air - a row WS8's ledger did not "
                "have at all (F1(c))"),
            driveline_kW="gearbox and axle oil"),
        cases=list(cases) + ["simulated_peak_over_all_runs"],
        sustained_cases=list(SUSTAINED),
        transient_cases=list(TRANSIENT),
        duration_convention=(
            "THE TWO CLASSES ARE NOT INTERCHANGEABLE AND WS6 MUST NOT SIZE "
            "ONE THING ON BOTH. The four analytic cases are SUSTAINED - the "
            "vehicle holds that speed on that grade indefinitely, and they "
            "are what a cooling package and a resistor bank are sized on. "
            "`simulated_peak_over_all_runs` is a TRANSIENT PEAK taken over "
            "every (corner, duty, seed) run: the friction-brake row there "
            "is a single service stop lasting seconds, not a duty. Both are "
            "exported - `worst_case` over the full set and "
            "`worst_case_sustained` over the sustained set alone - so WS6 "
            "can size thermal capacity on the second and structural or "
            "energy limits on the first. WS8 r1's finding F1 was that its "
            "ledger's governing case sat OUTSIDE its enumerated set; the "
            "answering risk is putting a transient inside it without "
            "saying so, and this is where that is said."),
        for_workstream="WS6 heat ledger (CLAUDE.md rule 7)",
        candidates=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--from-checkpoint", action="store_true")
    args = ap.parse_args()
    t0 = time.time()

    from ws9_blocks import (sanity_checks, escalations, interface_block,
                            headline, write_csvs, rebuild_derived)

    if args.from_checkpoint:
        R = json.load(open(CHECKPOINT), object_pairs_hook=OrderedDict)
        print("== rebuilding derived blocks from the checkpoint ==",
              flush=True)
        R["inherited_vintage"] = inherited_vintage()
        R["params"] = P9.params_dump()
        R["fuels"] = F9.fuels_dump()
        R["engines"] = E9.engines_dump()
        R["margins"] = OrderedDict(
            (c, margins_vs_ruler(R["trial"][c])) for c in R["trial"])
        R["margins_tank_energy"] = OrderedDict(
            (c, margins_vs_ruler(R["trial"][c],
                                 metric="MJ_tank_per_payload_tkm"))
            for c in R["trial"])
        R["margins_co2"] = OrderedDict(
            (c, margins_vs_ruler(R["trial"][c],
                                 metric="g_CO2_per_payload_tkm"))
            for c in R["trial"])
        merged = OrderedDict(R["trial"]["nominal"])
        merged.update(R.get("brackets", {}))
        R["bracket_margins"] = margins_vs_ruler(merged)
        # R34 traces are SIMULATION output, so they are not re-simulated
        # here - that is the whole point of --from-checkpoint. They are
        # RE-HASHED from disk, so a record that claims a trace it does not
        # have cannot survive this path either.
        if R.get("traces_r34", {}).get("files"):
            R["traces_r34"] = traces_record(R["traces_r34"]["files"])
        R["concordance_ws8_r3"] = CN9.concordance_block(R)
        R = rebuild_derived(R, globals())
        _write(R)
        return

    seeds = DY9.seeds()
    if args.quick:
        seeds = seeds[:2]
    if args.seeds:
        seeds = seeds[:args.seeds]

    pool = None
    if args.jobs and args.jobs > 1:
        import multiprocessing as mp
        pool = mp.get_context("fork").Pool(args.jobs)

    ckpt = {}
    if args.resume and os.path.exists(CHECKPOINT):
        try:
            ckpt = json.load(open(CHECKPOINT), object_pairs_hook=OrderedDict)
            print(f"== resuming; corners on disk: "
                  f"{list(ckpt.get('trial', {}))} ==", flush=True)
        except (ValueError, OSError):
            ckpt = {}

    R = OrderedDict()
    R["_meta"] = OrderedDict(
        workstream="WS9",
        vehicle="Vehicle One (Class 8 6x4 tractor + van trailer)",
        assignment="WS9_vehicle_one_wave2/ASSIGNMENT.md",
        assignment_baseline="BASELINE_v4.md",
        baseline_of_record="BASELINE_v5.md",
        round="r3-concordant re-run",
        round_note=(
            "ASSIGNMENT.md was written against BASELINE_v4 and its rulings "
            "R25-R33 / D13-D15 govern the trial unchanged. BASELINE_v5 is "
            "the baseline of record for THIS artifact: it receives WS9 at "
            "R37-R39, it adds R34 (the 10 Hz trace export, which names WS9 "
            "RE-RUNS explicitly and which this artifact complies with) and "
            "R38 (the trip-time gate, pre-committed AFTER WS9 ran, applied "
            "BY THE LEAD at ratification from "
            "`sanity.trip_time_the_metric_cannot_see` - NOT applied here), "
            "and R39/ESC-8 is the order this re-run executes. WS9's "
            "verdicts are PROVISIONAL under R37 and this round reopens "
            "none of them."),
        python=platform.python_version(), numpy=np.__version__,
        seeds=[int(s) for s in seeds], n_seeds=len(seeds),
        quick=bool(args.quick),
        design_duty=DY9.DESIGN_DUTY, control_duty=DY9.CONTROL_DUTY,
        no_fleet_average=P9.FLEET_MIX_IS_FORBIDDEN,
        metric_of_record=CR9.METRIC_NOTE,
        conventions=[
            "SI; kW/kWh BUS-SIDE unless a name says otherwise (rule 6)",
            "part-load models everywhere, no peak-point scalars (rule 5)",
            "stochastic extrema are 8-seed ensemble envelopes (rule 4)",
            "R14: every machine-readable worst-case field is an explicit "
            "max/min over an enumerated case set with the governing case "
            "labelled inline",
            "R12 chain: traction side = WS2 r4 measured maps x 0.97 "
            "reduction, no scalar PE member",
            "rule 7: rejected heat by component AND case, for WS6",
            "escalations cite the ruling they challenge and are never "
            "self-resolved (rule 8)",
        ])
    R["inherited_vintage"] = inherited_vintage()
    R["params"] = P9.params_dump()
    R["fuels"] = F9.fuels_dump()
    R["engines"] = E9.engines_dump()

    print("== DUTIES (R29) ==", flush=True)
    R["duties"] = DY9.duty_record(seeds, CD9.NOMINAL)
    for d, r in R["duties"].items():
        e = r["ensemble"]
        print(f"   {d}: {e['distance_km']['median']:.0f} km, climb "
              f"{e['total_climb_m']['median']:.0f} m "
              f"({e['climb_m_per_km']['median']:.1f} m/km), grade max "
              f"{e['grade_max']['max']:+.4f}, "
              f"{e['frac_dist_grade_ge_2pct']['median']*100:.1f}% of "
              f"distance at >=2%", flush=True)

    print("== THE TWO WALLS ==", flush=True)
    R["two_walls"] = two_walls_block()
    for k, v in R["two_walls"]["two_speed_solve"].items():
        s = v["solve"]
        print(f"   {k}: Rh {s['ratio_high']:.3f} / Rl "
              f"{s['ratio_low']:.3f}  feasible {s['feasible']}  cruise "
              f"{s['rpm_at_cruise_100kmh']:.0f} rpm at 100 km/h  holds 6% "
              f"{v['sweep']['holds_6pct']}", flush=True)

    cs = corners(quick=args.quick)
    trial = OrderedDict()
    margins = OrderedDict()
    _ck = ckpt.get("trial", {})
    print("== TRIAL ==", flush=True)
    for cname, ctx in cs.items():
        if cname in _ck:
            print(f"  corner {cname} [from checkpoint]", flush=True)
            trial[cname] = _ck[cname]
        else:
            print(f"  corner {cname}", flush=True)
            trial[cname] = run_corner(cname, seeds, list(CD9.FULL_SET),
                                      pool=pool)
        margins[cname] = margins_vs_ruler(trial[cname])
        R["trial"] = trial
        R["margins"] = margins
        _save(R)

    R["margins_tank_energy"] = OrderedDict(
        (c, margins_vs_ruler(trial[c], metric="MJ_tank_per_payload_tkm"))
        for c in trial)
    R["margins_co2"] = OrderedDict(
        (c, margins_vs_ruler(trial[c], metric="g_CO2_per_payload_tkm"))
        for c in trial)
    R["margins_grid_lo"] = OrderedDict(
        (c, margins_vs_ruler(
            trial[c], metric="MJ_primary_per_payload_tkm_grid_lo"))
        for c in trial)
    R["margins_grid_hi"] = OrderedDict(
        (c, margins_vs_ruler(
            trial[c], metric="MJ_primary_per_payload_tkm_grid_hi"))
        for c in trial)

    print("== BRACKETS (informative, nominal corner) ==", flush=True)
    brackets = ckpt.get("brackets") or run_corner(
        "nominal", seeds, ["S5-P2", "S5-GH", "S0R-PCC"], pool=pool)
    R["brackets"] = brackets
    merged = OrderedDict(trial["nominal"])
    merged.update(brackets)
    R["bracket_margins"] = margins_vs_ruler(merged)
    _save(R)

    print("== ELECTRIC TURBOCOMPOUND GATE (design duty, R31) ==", flush=True)
    R["etc_gate"] = ckpt.get("etc_gate") or etc_gate(seeds, trial["nominal"],
                                                     pool=pool)
    print(f"   design duty net min "
          f"{R['etc_gate']['design_duty_net_margin_pct_min']:+.2f}% vs gate "
          f">= {P9.WHR_GATE_PCT}% -> {R['etc_gate']['verdict']}", flush=True)
    _save(R)

    print("== F7 CROSS-CHECK (ensemble) ==", flush=True)
    R["f7_crosscheck"] = ckpt.get("f7_crosscheck") or f7_crosscheck(
        seeds, cs["nominal"])
    _f = R["f7_crosscheck"]["envelope_vs_band"]
    print(f"   S0R grade-zeroed: min {_f['model_min']:.2f} / median "
          f"{_f['model_median']:.2f} / max {_f['model_max']:.2f} L/100 km "
          f"vs band {_f['band_min']}-{_f['band_max']}", flush=True)

    print("== PRIME MOVER AT THE PIN ==", flush=True)
    R["prime_mover"] = prime_mover_at_the_pin(trial["nominal"].get("S4p"))

    print("== ADVANCE / KILL (design duty) ==", flush=True)
    R["advance_kill"] = advance_kill(margins)
    R["verdict_robustness_ESC3"] = verdict_robustness(R)
    for k, v in R["advance_kill"]["candidates"].items():
        wc = v["worst_corner_margin_pct_min"]
        wtxt = (f"{wc:+.2f}% @ {v['worst_corner']}" if wc is not None
                else "no corners run")
        ctrl = v["control_duty_nominal_margin_pct_min"]
        ctxt = f"{ctrl:+.2f}%" if ctrl is not None else "n/a"
        print(f"   {k:8s}: {v['verdict']:8s} design nominal min "
              f"{v['nominal_margin_pct_min']:+.2f}%, worst corner {wtxt}, "
              f"control duty {ctxt}", flush=True)

    # S6's break-even peak BTE: the number the lead actually needs, because
    # S6 is mass-neutral so its margin is exactly its fuel margin and its
    # fuel scales inversely with the island BSFC.
    _s0 = trial["nominal"][RULER]["per_duty"][DY9.DESIGN_DUTY][
        "ensemble"]["MJ_primary_per_payload_tkm"]
    _s6 = trial["nominal"]["S6"]["per_duty"][DY9.DESIGN_DUTY][
        "ensemble"]["MJ_primary_per_payload_tkm"]
    R["_s6_break_even"] = OrderedDict(
        duty=DY9.DESIGN_DUTY, statistic="ensemble_min",
        **E9.op_break_even_island_bsfc(P9.ADVANCE_NOMINAL_PCT,
                                       _s0["min"], _s6["min"]))
    R["_s6_break_even"]["at_median"] = E9.op_break_even_island_bsfc(
        P9.ADVANCE_NOMINAL_PCT, _s0["median"], _s6["median"])
    R["_s6_break_even"]["map_fraction_above_44pct_BTE"] = (
        E9.map_area_above_bte(E9.ENG_OP, 0.44))
    R["_s6_break_even"]["cited_claim_says"] = (
        "'large areas of the speed/load map above 44% BTE' - WS9's "
        "conservatively-scaled map is checked against that phrase rather "
        "than credited with it")
    print(f"   S6 break-even peak BTE for +{P9.ADVANCE_NOMINAL_PCT}% "
          f"(ensemble-min): "
          f"{R['_s6_break_even']['break_even_peak_BTE']:.4f} against a "
          f"claimed {E9.OP_PEAK_BTE_CLAIMED:.4f}", flush=True)

    print("== HEAT LEDGER (rule 7, for WS6) ==", flush=True)
    R["heat_ledger"] = heat_ledger(cs["nominal"], trial)

    print("== R34 10 Hz TRACES ==", flush=True)
    R["traces_r34"] = traces_record(export_traces_r34(DATA))

    print("== ESC-WS9-8 CONCORDANCE AGAINST WS8 r3 ==", flush=True)
    R["concordance_ws8_r3"] = CN9.concordance_block(R)
    _c = R["concordance_ws8_r3"]
    for k, v in _c["summary"].items():
        print(f"   {k}: {v['n_consistent']} consistent, "
              f"{v['n_differs_by_design']} declared differences, "
              f"{v['n_differs_undeclared']} undeclared -> {v['result']}",
              flush=True)
    _d = _c["import_surface_r2_to_r3"]
    if _d:
        print(f"   import surface r2 -> r3: {_d['n_symbols']} symbols, "
              f"{_d['n_changed']} changed", flush=True)

    _save(R)
    R["determinism"] = load_determinism()
    R["sanity"] = sanity_checks(R, globals())
    R["escalations"] = escalations(R)
    R["interface_ws9"] = _clean(interface_block(R))
    R["headline"] = headline(R)
    write_csvs(R, DATA)
    if pool is not None:
        pool.close()
        pool.join()
    _write(R, elapsed=time.time() - t0)


def _save(R):
    with open(CHECKPOINT, "w") as f:
        json.dump(_clean(R), f, default=_jsonable, allow_nan=False)


def _write(R, elapsed=None):
    path = os.path.join(_HERE, "results_ws9.json")
    R = _strip_runtimes(_clean(R))
    with open(path, "w") as f:
        json.dump(R, f, indent=1, sort_keys=False, default=_jsonable,
                  allow_nan=False)
        f.write("\n")
    msg = f"== wrote {path} ({os.path.getsize(path)/1e6:.2f} MB"
    if elapsed is not None:
        msg += f", {elapsed:.0f} s"
    print(msg + ") ==", flush=True)


def _strip_runtimes(o):
    drop = {"runtime_s"}
    if isinstance(o, dict):
        return {k: _strip_runtimes(v) for k, v in o.items() if k not in drop}
    if isinstance(o, list):
        return [_strip_runtimes(v) for v in o]
    return o


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float):
        return None if (o != o or o in (float("inf"), float("-inf"))) else o
    if isinstance(o, np.floating):
        f = float(o)
        return None if (f != f or f in (float("inf"), float("-inf"))) else f
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    return o


def _jsonable(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serialisable: {type(o)}")


if __name__ == "__main__":
    main()
