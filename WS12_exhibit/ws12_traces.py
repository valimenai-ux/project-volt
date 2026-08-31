"""WS12 — trace loading, TRACE_SCHEMA validation and decimation.

Two rules from the assignment govern this module.

**TRACE_SCHEMA validation.** `../TRACE_SCHEMA.md` (lead-issued 2026-08-31,
07:54) defines the R34 10 Hz trace contract: a `# key: value` header
carrying fourteen mandatory keys, a core column set, an engine column set,
an electrified column set, and the R15 blend-order sum rule. The exhibit
validates every trace it touches and REFUSES a nonconforming file with a
visible reason rather than plotting it.

Two classes exist in the tree and the exhibit does not blur them:

* `R34` — conforms to TRACE_SCHEMA. WS5's duty traces are the only
  conforming files in the repository. They feed the Simulator screen.
* `PRE-R34` — written before the schema was issued. WS11's r2 traces were
  generated at 07:32, twenty-two minutes before TRACE_SCHEMA existed;
  they carry free-text comment headers and ten or eleven columns. They
  are the ordered dataset for Race mode. They are published with the
  exact list of schema elements they lack recorded in the manifest and
  shown on screen, and NOTHING ABSENT IS DRAWN AND NOTHING IS
  ZERO-FILLED.

**Decimated replay (lead ruling, 2026-08-31).** No 10 Hz file is fetched
whole on page load. Every published trace is emitted as

* a 1 Hz whole-trace scrub index, decimated BY STRIDED SAMPLE (never by
  averaging — averaging would invent samples that are not in the record),
  and
* 10 Hz segment chunks, fetched one at a time for the segment in view.

Every emitted field is the VERBATIM field string from the source file.
No value is reformatted, rounded or recomputed on the way out, so the
1 Hz tier is a literal subsequence of the 10 Hz source and
`exhibit_verify.py` can prove it by string equality.
"""

import hashlib
import os

from ws12_record import repo_path

# ---------------------------------------------------------------- schema

# TRACE_SCHEMA.md "Header metadata (mandatory)"
SCHEMA_HEADER_KEYS = (
    "program", "workstream", "round", "vehicle", "architecture", "duty",
    "corner", "seed", "mass_kg", "payload_kg", "baseline_version",
    "results_file", "results_sha256", "generated_utc",
)

# TRACE_SCHEMA.md "Core columns (every vehicle)"
SCHEMA_CORE_COLUMNS = (
    "t_s", "x_m", "v_kmh", "grade_pct", "z_m", "P_wheel_kW", "fuel_g_per_s",
    "fuel_cum_g", "P_friction_brake_kW", "trip_time_flag",
)

# TRACE_SCHEMA.md "Engine-carrying columns"
SCHEMA_ENGINE_COLUMNS = (
    "N_eng_rpm", "T_eng_Nm", "P_shaft_eng_kW", "engine_state", "gear",
    "lockup", "P_comp_brake_kW",
)

# TRACE_SCHEMA.md "Electrified columns"
SCHEMA_ELECTRIFIED_COLUMNS = (
    "P_gen_bus_kW", "P_bus_load_kW", "P_motor_bus_kW", "P_motor_mech_kW",
    "P_regen_pack_kW", "P_heater_kW", "P_resistor_kW", "soc_pct", "T_pack_C",
    "T_motor_C", "genset_state", "motor_disconnect",
)

# The blend-order sum rule, TRACE_SCHEMA.md: "blend order R15: pack ->
# heater -> resistor -> friction; the four must sum to the braking demand
# served electrically plus friction". Two closures, both checked:
#   BUS   : P_regen_pack + P_heater + P_resistor == -P_motor_bus_kW
#   WHEEL : -P_motor_mech_kW + P_friction_brake_kW == -P_wheel_kW
#
# Tolerance is the file's own printing precision, not a fudge factor. The
# conforming traces print six significant figures, so a residual within
# one part in 1e5 of the largest term in the sum is a rounding artefact of
# the printing and nothing more. The floor keeps small-signal samples
# sane. The separation this leaves is five orders of magnitude: the
# conforming files miss by 5e-4 kW at worst on terms of order 100 kW,
# and the fault trace misses by 49 kW.
BLEND_REL_TOLERANCE = 1.0e-5
BLEND_FLOOR_KW = 1.0e-4


def blend_tolerance(max_term_kW):
    return max(BLEND_FLOOR_KW, BLEND_REL_TOLERANCE * abs(max_term_kW))


class TraceError(Exception):
    pass


def read_trace(rel_path, want_columns=None, limit=None):
    """Read a trace file. Returns (header_lines, meta, columns, rows).

    `rows` are lists of the VERBATIM field strings, projected to
    `want_columns` if given. Nothing is parsed to float on this path —
    the published bytes must be the source bytes.
    """
    abs_path = repo_path(rel_path)
    header_lines = []
    columns = None
    rows = []
    with open(abs_path, "r", encoding="utf-8", newline="") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if line.startswith("#"):
                header_lines.append(line[1:].strip())
                continue
            if columns is None:
                columns = line.split(",")
                continue
            if not line:
                continue
            rows.append(line.split(","))
            if limit is not None and len(rows) >= limit:
                break
    if columns is None:
        raise TraceError("%s: no column header row" % rel_path)
    meta = {}
    for h in header_lines:
        if ":" in h:
            k, v = h.split(":", 1)
            k = k.strip()
            if k and " " not in k:
                meta.setdefault(k, v.strip())
    if want_columns is not None:
        idx = []
        for c in want_columns:
            if c not in columns:
                raise TraceError("%s: column %r not present" % (rel_path, c))
            idx.append(columns.index(c))
        rows = [[r[i] for i in idx] for r in rows]
        columns = list(want_columns)
    return header_lines, meta, columns, rows


ALL_SCHEMA_COLUMNS = frozenset(SCHEMA_CORE_COLUMNS + SCHEMA_ENGINE_COLUMNS
                               + SCHEMA_ELECTRIFIED_COLUMNS)


def _declared_absent(header_lines):
    """TRACE_SCHEMA: 'Missing physical quantity = column absent, never
    zero-filled'. A conforming file declares which columns it omits by
    design; those omissions are compliant, silent ones are not.

    The declaration is prose, and the two conforming files word it
    differently, so the parse is deliberately narrow: take the tail of any
    line that says 'columns absent by design' and keep only tokens that
    are actual TRACE_SCHEMA column names. A word that is not a column name
    cannot excuse a missing column.
    """
    out = set()
    for h in header_lines:
        low = h.lower()
        at = low.find("columns absent by design")
        if at < 0:
            continue
        tail = h[at:]
        colon = tail.find(":")
        if colon >= 0:
            tail = tail[colon + 1:]
        for tok in tail.replace("/", " ").replace(";", " ").replace(",", " ") \
                       .split():
            tok = tok.strip(".;,")
            if tok in ALL_SCHEMA_COLUMNS:
                out.add(tok)
    return out


def validate_r34(rel_path, header_lines, meta, columns, rows):
    """Full TRACE_SCHEMA (R34) validation. Returns a findings dict."""
    missing_header = [k for k in SCHEMA_HEADER_KEYS if k not in meta]
    missing_core = [c for c in SCHEMA_CORE_COLUMNS if c not in columns]
    absent_ok = _declared_absent(header_lines)

    has_engine = any(c in columns for c in SCHEMA_ENGINE_COLUMNS)
    has_elec = any(c in columns for c in SCHEMA_ELECTRIFIED_COLUMNS)
    missing_engine = []
    if has_engine:
        missing_engine = [c for c in SCHEMA_ENGINE_COLUMNS
                          if c not in columns and c not in absent_ok]
    missing_elec = []
    if has_elec:
        missing_elec = [c for c in SCHEMA_ELECTRIFIED_COLUMNS
                        if c not in columns and c not in absent_ok]

    blend = blend_order_residuals(columns, rows)

    reasons = []
    if missing_header:
        reasons.append("header keys missing: " + ", ".join(missing_header))
    if missing_core:
        reasons.append("core columns missing: " + ", ".join(missing_core))
    if missing_engine:
        reasons.append("engine columns missing and not declared absent: "
                       + ", ".join(missing_engine))
    if missing_elec:
        reasons.append("electrified columns missing and not declared absent: "
                       + ", ".join(missing_elec))
    if blend["checked"] and not blend["passes"]:
        reasons.append(
            "R15 blend-order sum rule fails: worst bus-cascade residual "
            "%.4f kW against a %.6f kW tolerance over %d braking samples, "
            "worst wheel-closure residual %.4f kW against a %.6f kW "
            "tolerance over %d braking samples"
            % (blend["bus_worst_kW"], blend["bus_tolerance_kW"],
               blend["bus_samples"], blend["wheel_worst_kW"],
               blend["wheel_tolerance_kW"], blend["wheel_samples"]))
    return {
        "schemaClass": "R34",
        "conforms": not reasons,
        "reasons": reasons,
        "missingHeaderKeys": missing_header,
        "missingCoreColumns": missing_core,
        "missingEngineColumns": missing_engine,
        "missingElectrifiedColumns": missing_elec,
        "declaredAbsentByDesign": sorted(absent_ok),
        "blendOrder": blend,
    }


def describe_pre_r34(rel_path, header_lines, meta, columns, rows):
    """A file written before TRACE_SCHEMA existed. Not validated against
    the schema — measured against it, so the screen can state exactly
    what it does not carry."""
    missing_header = [k for k in SCHEMA_HEADER_KEYS if k not in meta]
    missing_core = [c for c in SCHEMA_CORE_COLUMNS if c not in columns]
    has_elec = any(c in columns for c in SCHEMA_ELECTRIFIED_COLUMNS)
    missing_elec = ([c for c in SCHEMA_ELECTRIFIED_COLUMNS
                     if c not in columns] if has_elec else [])
    has_engine = any(c in columns for c in SCHEMA_ENGINE_COLUMNS)
    missing_engine = ([c for c in SCHEMA_ENGINE_COLUMNS
                       if c not in columns] if has_engine else [])
    return {
        "schemaClass": "PRE-R34",
        "conforms": False,
        "reasons": ["written before TRACE_SCHEMA.md was issued; measured "
                    "against it, not validated by it"],
        "missingHeaderKeys": missing_header,
        "missingCoreColumns": missing_core,
        "missingEngineColumns": missing_engine,
        "missingElectrifiedColumns": missing_elec,
        "declaredAbsentByDesign": [],
        "blendOrder": blend_order_residuals(columns, rows),
    }


def blend_order_residuals(columns, rows):
    """The R15 blend-order sum rule, measured."""
    need_bus = ("P_regen_pack_kW", "P_heater_kW", "P_resistor_kW",
                "P_motor_bus_kW")
    need_wheel = ("P_motor_mech_kW", "P_friction_brake_kW", "P_wheel_kW")
    have_bus = all(c in columns for c in need_bus)
    have_wheel = all(c in columns for c in need_wheel)
    if not (have_bus or have_wheel):
        return {"checked": False,
                "why": "the columns the rule is written over are absent"}
    ix = {c: columns.index(c) for c in columns}
    bus_worst = 0.0
    bus_n = 0
    bus_tol = BLEND_FLOOR_KW
    wheel_worst = 0.0
    wheel_n = 0
    wheel_tol = BLEND_FLOOR_KW
    bus_fail = False
    wheel_fail = False
    for r in rows:
        if have_bus:
            pmb = float(r[ix["P_motor_bus_kW"]])
            if pmb < 0.0:
                a = float(r[ix["P_regen_pack_kW"]])
                b = float(r[ix["P_heater_kW"]])
                c = float(r[ix["P_resistor_kW"]])
                res = abs((a + b + c) - (-pmb))
                tol = blend_tolerance(max(abs(a), abs(b), abs(c), abs(pmb)))
                if res > tol:
                    bus_fail = True
                if res > bus_worst:
                    bus_worst = res
                    bus_tol = tol
                bus_n += 1
        if have_wheel:
            pw = float(r[ix["P_wheel_kW"]])
            if pw < 0.0:
                a = float(r[ix["P_motor_mech_kW"]])
                b = float(r[ix["P_friction_brake_kW"]])
                res = abs((-a + b) - (-pw))
                tol = blend_tolerance(max(abs(a), abs(b), abs(pw)))
                if res > tol:
                    wheel_fail = True
                if res > wheel_worst:
                    wheel_worst = res
                    wheel_tol = tol
                wheel_n += 1
    return {
        "checked": True,
        "passes": not (bus_fail or wheel_fail),
        "bus_worst_kW": bus_worst,
        "bus_tolerance_kW": bus_tol,
        "bus_samples": bus_n,
        "wheel_worst_kW": wheel_worst,
        "wheel_tolerance_kW": wheel_tol,
        "wheel_samples": wheel_n,
        "tolerance_rule": ("half the last significant figure the file prints: "
                           "%g of the largest term in the sum, floored at "
                           "%g kW" % (BLEND_REL_TOLERANCE, BLEND_FLOOR_KW)),
        "rule": ("pack -> heater -> resistor -> friction; the four must sum "
                 "to the braking demand served electrically plus friction "
                 "(TRACE_SCHEMA.md)"),
    }


def sha256_file(rel_path):
    h = hashlib.sha256()
    with open(repo_path(rel_path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------- decimation

STRIDE = 10          # 10 Hz -> 1 Hz. Strided sample, never averaged.
SEGMENT_ROWS = 3000  # 300 s of 10 Hz record per fetched chunk.


def emit_trace(rel_path, out_dir, columns, url_base):
    """Write the 1 Hz scrub index and the 10 Hz segments.

    Every field written is the verbatim source field string.
    """
    header_lines, meta, cols, rows = read_trace(rel_path,
                                                want_columns=columns)
    os.makedirs(out_dir, exist_ok=True)

    head = ",".join(cols) + "\n"

    scrub_rows = rows[::STRIDE]
    scrub_path = os.path.join(out_dir, "scrub_1hz.csv")
    with open(scrub_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(head)
        for r in scrub_rows:
            fh.write(",".join(r) + "\n")

    segments = []
    n_seg = (len(rows) + SEGMENT_ROWS - 1) // SEGMENT_ROWS
    for s in range(n_seg):
        chunk = rows[s * SEGMENT_ROWS:(s + 1) * SEGMENT_ROWS]
        name = "seg_%04d.csv" % s
        with open(os.path.join(out_dir, name), "w", encoding="utf-8",
                  newline="") as fh:
            fh.write(head)
            for r in chunk:
                fh.write(",".join(r) + "\n")
        segments.append({"i": s, "file": name, "rows": len(chunk),
                         "row0": s * SEGMENT_ROWS})

    published_bytes = os.path.getsize(scrub_path)
    for s in segments:
        published_bytes += os.path.getsize(os.path.join(out_dir, s["file"]))

    return {
        "headerLines": header_lines,
        "meta": meta,
        "columnsPublished": cols,
        "sourceRows": len(rows),
        "scrubRows": len(scrub_rows),
        "stride": STRIDE,
        "decimation": "strided sample (every %dth row), never averaged"
                      % STRIDE,
        "segmentRows": SEGMENT_ROWS,
        "segments": segments,
        "urlBase": url_base,
        "publishedBytes": published_bytes,
    }
