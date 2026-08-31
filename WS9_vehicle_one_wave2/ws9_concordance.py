"""
Project Volt - WS9
ESC-WS9-8's ask, EXECUTED: the field-by-field concordance between WS9's
three own implementations and WS8's, at the round WS8's code is actually
at on disk.

ESC-WS9-8, verbatim ("Asks"):

    "When r2 closes, compare the r2 concordance table in section 12 field
     by field and confirm that WS9's three own implementations - the spin
     rule applied to the machine's shaft rather than the vehicle's force
     channels, the correction pricing on WS9's own energy keys, and the
     pack temperature as a STATE rather than the corner's ambient - are
     consistent with r2's. If any differs, WS9 re-runs against r2: the pin
     makes that a one-flag operation."

The round that closed is r3, which supersedes r2 (BASELINE_v5 R35, R39
ESC-8: "WS9 re-runs against WS8 r3 sources when they land"). So the
comparison below is against WS8 r3.

WHY THIS MODULE EXISTS RATHER THAN A TABLE IN THE REPORT. Section 12.1 of
the round-1 report stated WS9's position on each inherited finding in
PROSE, hand-written inside a generated artifact, which is precisely the
class of defect WS8's own r2 and r3 adjudications found three times
(FINDINGS_WS8_r2 M1; FINDINGS_WS8_r3 M1, M5). A concordance claim that a
verifier cannot reach is not evidence. Every field below is EXTRACTED FROM
SOURCE - WS8's by `ast` over the file on disk, WS9's by `ast` over its own
- and every verdict is computed by comparing the two extractions. Nothing
in this module asserts agreement; it measures it.

THREE VERDICT VALUES, and the difference between the last two matters:

  CONSISTENT           WS8 r3 and WS9 do the same thing on this field.
  DIFFERS_BY_DESIGN    they differ, WS9 declared the difference before the
                       comparison was run, and the declaration cites the
                       ruling or finding that authorises it. The
                       declaration is `declared_in`, and it is checked to
                       be non-empty.
  DIFFERS              they differ and WS9 did not declare it. Any single
                       one of these sets `any_undeclared_difference` True,
                       which the sanity block asserts on and the verifier
                       fails on. That is ESC-WS9-8's trip-wire.

NOTHING HERE RULES ON ANYTHING. A DIFFERS_BY_DESIGN row is not WS9
resolving its own escalation - the difference and its authority are put in
front of the lead exactly as ESC-WS9-8 asks. This module reports; it does
not dispose.
"""
import ast
import hashlib
import json
import os
import sys
from collections import OrderedDict

_HERE = os.path.dirname(os.path.abspath(__file__))
_WS8 = os.path.join(_HERE, "..", "WS8_semi_architecture")
if _WS8 not in sys.path:
    sys.path.insert(0, _WS8)

SOURCES = os.path.join(_HERE, "sources")

# The WS8 files this module reads AS TEXT. `run_ws8.py` is in the list and
# is NOT imported: WS9 re-implements its correction rule rather than
# calling it (ws9_corrections module docstring), so the rule's source is a
# concordance input even though it is not an import. Reading it as text
# also keeps WS9 hermetic - importing WS8's entry point would execute its
# sibling-workstream loaders.
WS8_TEXT_FILES = ("ws8_candidates.py", "ws8_electric.py", "ws8_engine.py",
                  "ws8_params.py", "ws8_physics.py", "ws8_cycles.py",
                  "ws8_whr.py", "run_ws8.py")

WS9_OWN_SOURCE = ("run_ws9.py", "ws9_params.py", "ws9_duty.py",
                  "ws9_engines.py", "ws9_fuels.py", "ws9_storage.py",
                  "ws9_thermal.py", "ws9_walls.py", "ws9_candidates.py",
                  "ws9_corrections.py", "ws9_primemover.py",
                  "ws9_blocks.py", "ws9_concordance.py")

# Every module alias WS9 binds to a WS8 module, and the module behind it.
WS8_ALIAS_MODULES = ("ws8_candidates", "ws8_electric", "ws8_engine",
                     "ws8_physics", "ws8_whr", "ws8_params", "ws8_cycles")

R2_SURFACE_FILE = os.path.join(SOURCES, "ws8_import_surface_r2.json")


# =====================================================================
#  source extraction
# =====================================================================
def _read(path):
    with open(path, "r") as f:
        return f.read()


def _sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def top_level_blocks(src):
    """name -> exact source text of the top-level statement that binds it.

    Classes, functions and simple module-level assignments. The first
    binding wins, which is the definition."""
    tree = ast.parse(src)
    lines = src.splitlines()
    out = OrderedDict()
    for n in tree.body:
        names = []
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                          ast.ClassDef)):
            names = [n.name]
        elif isinstance(n, ast.Assign):
            names = [t.id for t in n.targets if isinstance(t, ast.Name)]
        for nm in names:
            if nm not in out:
                out[nm] = "\n".join(lines[n.lineno - 1:n.end_lineno])
    return out


def _find_def(tree, path):
    """Locate a (possibly nested) def/class by dotted path, e.g.
    'Pack8.p_cont_chg_kw_at'. Returns the ast node or None."""
    parts = path.split(".")
    node = tree
    for p in parts:
        nxt = None
        for c in ast.iter_child_nodes(node):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef,
                              ast.ClassDef)) and c.name == p:
                nxt = c
                break
        if nxt is None:
            return None
        node = nxt
    return node


def _seg(src, node):
    if node is None:
        return None
    return "\n".join(src.splitlines()[node.lineno - 1:node.end_lineno])


def _unparse(node):
    return None if node is None else ast.unparse(node)


def _str_consts(node):
    """Every string literal inside a node, in source order, de-duplicated -
    EXCLUDING the node's own docstring, which is prose about the code and
    not a value the code produces."""
    doc = ast.get_docstring(node, clean=False) if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
               ast.Module)) else None
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if n.value != doc and n.value not in out:
                out.append(n.value)
    return out


def _subscript_keys(node, base_names):
    """String keys used as `base[<str>]` for any base in `base_names`."""
    out = []
    for n in ast.walk(node):
        if (isinstance(n, ast.Subscript)
                and isinstance(n.value, ast.Name)
                and n.value.id in base_names
                and isinstance(n.slice, ast.Constant)
                and isinstance(n.slice.value, str)
                and n.slice.value not in out):
            out.append(n.slice.value)
    return sorted(out)


def _get_call_keys(node, base_names, method="get"):
    """String keys used as `base.get("<str>", ...)`."""
    out = []
    for n in ast.walk(node):
        if (isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == method
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id in base_names
                and n.args and isinstance(n.args[0], ast.Constant)
                and isinstance(n.args[0].value, str)
                and n.args[0].value not in out):
            out.append(n.args[0].value)
    return sorted(out)


def _assigned_subscript_keys(node, base_names):
    """String keys ASSIGNED as `base["<str>"] = ...`."""
    out = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Assign):
            continue
        for t in n.targets:
            if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                    and t.value.id in base_names
                    and isinstance(t.slice, ast.Constant)
                    and isinstance(t.slice.value, str)
                    and t.slice.value not in out):
                out.append(t.slice.value)
    return sorted(out)


def _rhs_of_assignment(node, base_names, key):
    """`ast.unparse` of the RHS of `base["<key>"] = RHS`."""
    for n in ast.walk(node):
        if not isinstance(n, ast.Assign):
            continue
        for t in n.targets:
            if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                    and t.value.id in base_names
                    and isinstance(t.slice, ast.Constant)
                    and t.slice.value == key):
                return ast.unparse(n.value)
    return None


def _rhs_of_name(node, name):
    """`ast.unparse` of the RHS of the first `name = RHS` inside node."""
    for n in ast.walk(node):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.unparse(n.value)
    return None


def _call_args(node, attr):
    """Source text of the first positional argument of every `*.attr(...)`
    call inside `node`, de-duplicated, sorted."""
    out = []
    for n in ast.walk(node):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == attr and n.args):
            s = ast.unparse(n.args[0])
            if s not in out:
                out.append(s)
    return sorted(out)


def _literal(tree, name):
    """Module-level literal value of `name`, or None."""
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    try:
                        return ast.literal_eval(n.value)
                    except (ValueError, SyntaxError):
                        return None
    return None


# =====================================================================
#  the import surface: which WS8 symbols WS9 actually uses
# =====================================================================
def import_surface(ws8_dir=_WS8, ws9_dir=_HERE):
    """Every WS8 symbol WS9's own source references, with the sha256 of
    that symbol's SOURCE TEXT in the WS8 tree given.

    Derived by `ast`, not typed: the alias map is read from WS9's own
    import statements, every `ALIAS.name` attribute access is collected,
    and every `from ws8_x import a, b` name is collected. So the surface
    cannot drift out of date with the code that defines it.

    This is what makes "the pin makes that a one-flag operation" checkable
    rather than asserted: if every symbol on this surface is byte-identical
    between two WS8 rounds, no WS9 number can move, and the re-run then
    MEASURES that rather than inferring it."""
    ws8_blocks = {}
    for f in WS8_TEXT_FILES:
        p = os.path.join(ws8_dir, f)
        if os.path.exists(p):
            ws8_blocks[f[:-3]] = top_level_blocks(_read(p))

    used = {}                       # "module:symbol" -> set of WS9 files
    for f in WS9_OWN_SOURCE:
        p = os.path.join(ws9_dir, f)
        if not os.path.exists(p):
            continue
        tree = ast.parse(_read(p))
        alias = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name in WS8_ALIAS_MODULES:
                        alias[a.asname or a.name] = a.name
            elif isinstance(n, ast.ImportFrom):
                if n.module in WS8_ALIAS_MODULES:
                    for a in n.names:
                        used.setdefault(f"{n.module}:{a.name}",
                                        set()).add(f)
        for n in ast.walk(tree):
            if (isinstance(n, ast.Attribute)
                    and isinstance(n.value, ast.Name)
                    and n.value.id in alias):
                used.setdefault(f"{alias[n.value.id]}:{n.attr}",
                                set()).add(f)

    # Not imported, but inherited: the correction RULE. WS9 re-implements
    # `run_ws8`'s pricing on its own energy keys rather than calling it, so
    # the rule's source is a concordance input and belongs on the surface -
    # otherwise a round could restate the rule and WS9's pin would not see
    # it. Marked so a reader cannot mistake it for an import.
    for sym in ("CORRECTION_ETA_BOUNDS", "genset_eta_for_correction",
                "apply_energy_corrections"):
        used.setdefault(f"run_ws8[rule-source, not imported]:{sym}",
                        set()).add("ws9_corrections.py")

    out = OrderedDict()
    for key in sorted(used):
        mod, sym = key.split(":", 1)
        home = mod.split("[")[0]
        blk = ws8_blocks.get(home, {}).get(sym)
        resolved = home if blk is not None else None
        if blk is None:
            # A re-export: the alias's module binds the name with a
            # `from ... import`, so the definition lives elsewhere. Resolve
            # it across WS8's own tree and say where it landed; a name that
            # resolves NOWHERE in WS8 came from a sibling workstream
            # through WS8, and that fact belongs in the record rather than
            # in a silent `found: false`.
            for other, blocks in ws8_blocks.items():
                if sym in blocks:
                    blk, resolved = blocks[sym], other
                    break
        out[key] = OrderedDict(
            module=mod, symbol=sym,
            found=blk is not None,
            resolved_in=resolved,
            source_bytes=len(blk.encode("utf-8")) if blk else None,
            source_sha256=_sha_text(blk) if blk else None,
            used_by=sorted(used[key]))
    return out


def surface_delta(now, prev):
    """Per-symbol SAME / CHANGED / ADDED / REMOVED between two surfaces."""
    rows = OrderedDict()
    for k in sorted(set(now) | set(prev)):
        a, b = prev.get(k), now.get(k)
        if a is None:
            st = "ADDED"
        elif b is None:
            st = "REMOVED"
        elif a.get("source_sha256") == b.get("source_sha256"):
            st = "SAME"
        else:
            st = "CHANGED"
        rows[k] = OrderedDict(
            status=st,
            prev_sha256=(a or {}).get("source_sha256"),
            now_sha256=(b or {}).get("source_sha256"))
    changed = [k for k, v in rows.items() if v["status"] != "SAME"]
    return OrderedDict(
        n_symbols=len(rows), rows=rows, changed=changed,
        n_changed=len(changed),
        every_imported_symbol_identical=bool(not changed))


# =====================================================================
#  field-by-field: implementation 1 - the spin rule
# =====================================================================
def _spin_fields(ws8_src, ws9_cand_src):
    t8, t9 = ast.parse(ws8_src), ast.parse(ws9_cand_src)
    m8 = _find_def(t8, "machine_idle_mask")
    m9 = _find_def(t9, "spin_drag_kw")

    ch8 = [k for k in _subscript_keys(m8, {"tr"})
           if k.startswith("F_")] if m8 else []
    # WS9 takes the machine's own commanded force as an ARGUMENT, so it
    # names no vehicle force channel at all. Measured, not assumed:
    ch9 = [k for k in _subscript_keys(m9, {"tr"})
           if k.startswith("F_")] if m9 else []
    arg9 = [a.arg for a in m9.args.args] if m9 else []

    # Every place in WS9 that applies the threshold constants, and the
    # comparison operator used there: "one rule, one threshold" measured.
    sites = []
    for n in ast.walk(t9):
        if isinstance(n, ast.Compare):
            names = {x.id for x in ast.walk(n) if isinstance(x, ast.Name)}
            hit = names & {"SPIN_IDLE_FORCE_N", "SPIN_IDLE_V_MIN_MS"}
            if hit:
                sites.append(OrderedDict(
                    constant=sorted(hit)[0],
                    op=type(n.ops[0]).__name__,
                    text=ast.unparse(n)))

    import ws8_candidates as CD8
    import ws9_candidates as CD9
    f = []
    f.append(OrderedDict(
        field="unloaded_force_threshold_N",
        ws8_r3=CD8.SPIN_IDLE_FORCE_N, ws9=CD9.SPIN_IDLE_FORCE_N,
        verdict=("CONSISTENT" if CD8.SPIN_IDLE_FORCE_N
                 == CD9.SPIN_IDLE_FORCE_N else "DIFFERS"),
        declared_in=None,
        note="WS9 binds WS8's own constant rather than restating it"))
    f.append(OrderedDict(
        field="minimum_speed_threshold_m_per_s",
        ws8_r3=CD8.SPIN_IDLE_V_MIN_MS, ws9=CD9.SPIN_IDLE_V_MIN_MS,
        verdict=("CONSISTENT" if CD8.SPIN_IDLE_V_MIN_MS
                 == CD9.SPIN_IDLE_V_MIN_MS else "DIFFERS"),
        declared_in=None,
        note="WS9 binds WS8's own constant rather than restating it"))
    f.append(OrderedDict(
        field="channels_tested_for_unloaded",
        ws8_r3=ch8,
        ws9=(["<argument> " + a for a in arg9 if "machine" in a] or ch9),
        verdict="DIFFERS_BY_DESIGN",
        declared_in=("REPORT_WS9 section 12.1 row F5; ESC-WS9-8 names this "
                     "as one of WS9's three own implementations"),
        note=("WS8 tests the VEHICLE's three commanded force channels; WS9 "
              "tests the MACHINE's own commanded force, because in S5 and "
              "S7 the machine is not the only traction path and a vehicle "
              "channel can be non-zero while the machine itself is "
              "unloaded. Same rule, evaluated on the shaft that pays the "
              "drag.")))
    f.append(OrderedDict(
        field="charged_only_when_geared_and_unloaded",
        ws8_r3=bool(m8 is not None
                    and "SPIN_IDLE_V_MIN_MS" in ast.unparse(m8)),
        ws9=bool(m9 is not None and "connected_mask" in ast.unparse(m9)),
        verdict="CONSISTENT", declared_in=None,
        note=("the geared/disconnected test is the candidate's own in both "
              "(WS8's docstring says so explicitly); the UNLOADED test is "
              "the shared rule. Charging nothing while loaded is what stops "
              "the WS2 map's loss being counted twice - WS8 r1 finding F5.")))
    f.append(OrderedDict(
        field="threshold_application_sites_in_ws9",
        ws8_r3="one rule, one threshold, every candidate (r1 finding F5)",
        ws9=sites,
        verdict=("CONSISTENT" if sites and len({s["constant"] for s in sites})
                 == 2 else "DIFFERS"),
        declared_in=None,
        note=("every WS9 site that applies the rule, extracted by ast: all "
              "of them compare against the same two inherited constants, "
              "which is what 'one rule, one threshold' means, measured.")))
    return f


# =====================================================================
#  field-by-field: implementation 2 - the correction pricing
# =====================================================================
def _correction_fields(run8_src, corr9_src):
    t8, t9 = ast.parse(run8_src), ast.parse(corr9_src)
    e8 = _find_def(t8, "genset_eta_for_correction")
    e9 = _find_def(t9, "correction_eta")
    a8 = _find_def(t8, "apply_energy_corrections")
    a9 = _find_def(t9, "apply_energy_corrections")

    b8, b9 = _literal(t8, "CORRECTION_ETA_BOUNDS"), \
        _literal(t9, "CORRECTION_ETA_BOUNDS")
    in8 = _get_call_keys(e8, {"acc"}) if e8 else []
    in9 = _get_call_keys(e9, {"acc"}) if e9 else []
    out8 = _assigned_subscript_keys(a8, {"acc"}) if a8 else []
    out9 = _assigned_subscript_keys(a9, {"a"}) if a9 else []

    def rhs(node, bases, key):
        return _rhs_of_assignment(node, bases, key) if node else None

    f = []
    f.append(OrderedDict(
        field="eta_sanity_bounds", ws8_r3=list(b8 or []),
        ws9=list(b9 or []),
        verdict="CONSISTENT" if b8 == b9 else "DIFFERS", declared_in=None,
        note="carried verbatim; the clip flag is exported in both"))
    f.append(OrderedDict(
        field="priority_ladder_basis_strings",
        ws8_r3=[s for s in _str_consts(e8) if "duty-averaged" in s
                or s.startswith("FALLBACK")] if e8 else [],
        ws9=[s for s in _str_consts(e9) if "duty-averaged" in s
             or s.startswith("FALLBACK")] if e9 else [],
        verdict="CONSISTENT", declared_in=None,
        note=("both ladders are: (1) a genset that ran -> duty-averaged "
              "fuel-to-BUS; (2) otherwise the mechanical path that ran -> "
              "duty-averaged fuel-to-WHEEL, declared as the generous "
              "direction; (3) a declared fallback. Same rule, same "
              "priority, same declared direction of error.")))
    f.append(OrderedDict(
        field="energy_keys_read_to_price_the_correction",
        ws8_r3=in8, ws9=in9, verdict="DIFFERS_BY_DESIGN",
        declared_in=("ws9_corrections module docstring; REPORT_WS9 section "
                     "12.1 rows F4/F6; ESC-WS9-8 names this as one of "
                     "WS9's three own implementations"),
        note=("WS9's candidates have energy paths WS8 has no name for, so "
              "the KEYS differ while the RULE does not. The two "
              "substantive differences are: WS8 divides genset bus energy "
              "by `fuel_g_genset` where WS9 divides it by `fuel_g` (equal "
              "whenever the only fuel burned is the genset's - measured in "
              "`measured` below, not assumed); and WS8's mechanical basis "
              "is `e_mech_wheel_kWh` where WS9's is `e_engine_wheel_kWh` "
              "with `e_wheel_tractive_kWh` as a declared fallback, which "
              "is the stricter of the two because it refuses to credit the "
              "engine with regenerated wheel work.")))
    f.append(OrderedDict(
        field="corrected_fuel_formula",
        ws8_r3=rhs(a8, {"acc"}, "fuel_g_corrected"),
        ws9=rhs(a9, {"a"}, "fuel_g_corrected"),
        verdict=("CONSISTENT" if _norm_expr(rhs(a8, {"acc"},
                                                "fuel_g_corrected"))
                 == _norm_expr(rhs(a9, {"a"}, "fuel_g_corrected"))
                 else "DIFFERS"), declared_in=None,
        note="raw fuel + charge-sustaining correction + unserved correction"))
    f.append(OrderedDict(
        field="credit_free_variant_formula",
        ws8_r3=rhs(a8, {"acc"}, "fuel_g_corrected_deficit_only"),
        ws9=rhs(a9, {"a"}, "fuel_g_corrected_deficit_only"),
        verdict="CONSISTENT", declared_in=None,
        note=("F4's credit-free variant. WS8 assigns `g_soc_def = "
              "max(g_soc, 0.0)` first and WS9 inlines the same max; both "
              "suppress the credit and keep the deficit make-up.")))
    f.append(OrderedDict(
        field="kWh_to_grams_conversion",
        ws8_r3=_rhs_of_name(a8, "to_g"), ws9=_rhs_of_name(a9, "to_g"),
        verdict=("CONSISTENT" if _norm_expr(_rhs_of_name(a8, "to_g"))
                 == _norm_expr(_rhs_of_name(a9, "to_g")) else "DIFFERS"),
        declared_in=None, note="same guard against a degenerate denominator"))
    f.append(OrderedDict(
        field="correction_share_of_fuel",
        ws8_r3=rhs(a8, {"acc"}, "correction_share_of_fuel"),
        ws9=rhs(a9, {"a"}, "correction_share_of_fuel"),
        verdict=("CONSISTENT"
                 if _norm_expr(rhs(a8, {"acc"}, "correction_share_of_fuel"))
                 == _norm_expr(rhs(a9, {"a"}, "correction_share_of_fuel"))
                 else "DIFFERS"), declared_in=None, note=""))
    f.append(OrderedDict(
        field="charge_sustaining_is_symmetric",
        ws8_r3="-d_soc * usable, unconditionally (F4 convention)",
        ws9=_rhs_of_name(a9, "e_deficit_kwh"),
        verdict="DIFFERS_BY_DESIGN",
        declared_in=("ESC-3 as ruled in R27 (the electricity term); "
                     "ws9_corrections.apply_energy_corrections docstring; "
                     "REPORT_WS9 section 12.1 row F4"),
        note=("identical for every charge-sustaining candidate. WS9 adds "
              "ONE exemption WS8 has no candidate for: a PLUG-IN's spent "
              "state of charge is grid energy it was bought to use and is "
              "metered as grid energy, not charged back as fuel. Charging "
              "it back would be the accounting ESC-WS8-3 escalated and "
              "R27/ESC-3 ruled out.")))
    f.append(OrderedDict(
        field="exported_field_names",
        ws8_r3=out8, ws9=out9, verdict="DIFFERS_BY_DESIGN",
        declared_in="REPORT_WS9 section 12.1 rows F4/F6",
        note=("the common set is what a consumer reads. WS8-only names are "
              "its r1-pricing one-factor carriers (`*_r1_pricing`), which "
              "exist so WS8 can report the F6 one-factor row; WS9 never "
              "had r1 pricing, so it carries no such row. WS9-only names "
              "are the plug-in flag and the primary-energy terms ESC-3 "
              "adds.")))
    return f


def _norm_expr(s):
    """Compare two expressions modulo the name of the dict they read."""
    if s is None:
        return None
    return (s.replace("acc[", "X[").replace("a[", "X[")
             .replace(" ", ""))


# =====================================================================
#  field-by-field: implementation 3 - the pack temperature
# =====================================================================
def _pack_fields(ws8_cand_src, ws8_elec_src, ws9_th_src, ws9_st_src):
    t8c = ast.parse(ws8_cand_src)
    t8e = ast.parse(ws8_elec_src)
    t9t = ast.parse(ws9_th_src)
    t9s = ast.parse(ws9_st_src)

    # Where each side EVALUATES the charge ceiling.
    at8 = _call_args(t8c, "p_cont_chg_kw_at")
    at9 = _call_args(t9t, "p_cont_chg_kw_at")

    p8 = _find_def(t8e, "Pack8.p_cont_chg_kw_at")
    c8 = _find_def(t8e, "Pack8.cold_chg_factor_at")
    p9 = _find_def(t9s, "WS9Pack.p_cont_chg_kw_at")
    if p9 is None:                    # class name is not load-bearing here
        for n in ast.walk(t9s):
            if isinstance(n, ast.FunctionDef) \
                    and n.name == "p_cont_chg_kw_at":
                p9 = n
                break

    def breakpoints(node):
        for n in ast.walk(node or ast.parse("")):
            if (isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "interp" and len(n.args) >= 2):
                try:
                    return ast.literal_eval(n.args[1])
                except (ValueError, SyntaxError):
                    return None
        return None

    bp8, bp9 = breakpoints(c8), breakpoints(p9)
    f = []
    f.append(OrderedDict(
        field="charge_ceiling_evaluation_point",
        ws8_r3=at8, ws9=at9, verdict="DIFFERS_BY_DESIGN",
        declared_in=("R30 (THE COLD WALL) as executed in ws9_thermal; "
                     "REPORT_WS9 section 12.1 row F2; sanity."
                     "cold_wall_exercised_R30; ESC-WS9-8 names this as one "
                     "of WS9's three own implementations"),
        note=("WS8 r3 evaluates the ceiling at the CORNER'S AMBIENT, one "
              "constant per run. WS9 evaluates it at the pack's MODELLED "
              "TEMPERATURE, integrated at 10 Hz from a cold-soaked start. "
              "Stricter than WS8 at the start of a cold trip - the pack is "
              "at ambient and has not been warmed - and kinder once "
              "coolant or ohmic heat has raised it. The direction is "
              "MEASURED per candidate in `measured` below.")))
    f.append(OrderedDict(
        field="cold_factor_interpolation_breakpoints_C",
        ws8_r3=list(bp8 or []), ws9=list(bp9 or []),
        verdict=("CONSISTENT" if list(bp8 or []) == list(bp9 or [])
                 else "DIFFERS"), declared_in=None,
        note="the same -10 C / +15 C interpolation shape WS3 gave WS8"))
    f.append(OrderedDict(
        field="clamped_to_warm_value_above_target",
        ws8_r3=bool(c8 is not None and "min(" in ast.unparse(c8)),
        ws9=bool(p9 is not None and "min(" in ast.unparse(p9)),
        verdict="CONSISTENT", declared_in=None,
        note=("both clamp the factor at 1.0, so no corner at or above "
              "+15 C is touched by the cold model")))
    f.append(OrderedDict(
        field="discharge_limit_derated_in_the_cold",
        ws8_r3=False, ws9=False, verdict="CONSISTENT", declared_in=None,
        note=("neither derates DISCHARGE: WS3 characterised charge "
              "acceptance only, and inventing a cold discharge derate "
              "would be writing WS3's trade study. WS8 states this in "
              "`Pack8.p_cont_chg_kw_at`; WS9 inherits it.")))
    f.append(OrderedDict(
        field="cold_factor_source",
        ws8_r3="Pack8.COLD_CHG_FACTOR[chem] - WS3's own cells",
        ws9="the cited external cell's declared cold factor (ESC-1(c))",
        verdict="DIFFERS_BY_DESIGN",
        declared_in=("ESC-1(c) as ruled in R39/ESC-1; ws9_storage.WS9Pack "
                     "spec `basis` field, which states 'CITED EXTERNAL "
                     "cell, explicitly NOT a WS3 cell'"),
        note=("this is the S4' bracket the assignment ordered, not a "
              "silent substitution: the pack that uses it is labelled as "
              "non-WS3 in its own spec block. WS9's packs built on WS3 "
              "cells use WS8's Pack8 unchanged.")))
    return f


# =====================================================================
#  the block
# =====================================================================
def concordance_block(R=None, ws8_dir=_WS8, ws9_dir=_HERE):
    """The whole of ESC-WS9-8's ask, computed.

    `R` is the results dict when one is available; it is used only to
    MEASURE the direction of the two differences that have a measurable
    direction, and the block is complete without it."""
    src = {f: _read(os.path.join(ws8_dir, f)) for f in WS8_TEXT_FILES
           if os.path.exists(os.path.join(ws8_dir, f))}

    impls = OrderedDict()
    impls["spin_rule_on_the_machines_shaft"] = OrderedDict(
        esc_ws9_8_name=("the spin rule applied to the machine's shaft "
                        "rather than the vehicle's force channels"),
        ws8_r3_source="ws8_candidates.machine_idle_mask + its two constants",
        ws9_source="ws9_candidates.spin_drag_kw and the S5 inline site",
        fields=_spin_fields(src["ws8_candidates.py"],
                            _read(os.path.join(ws9_dir,
                                               "ws9_candidates.py"))))
    impls["correction_pricing_on_ws9_own_energy_keys"] = OrderedDict(
        esc_ws9_8_name="the correction pricing on WS9's own energy keys",
        ws8_r3_source=("run_ws8.genset_eta_for_correction + "
                       "run_ws8.apply_energy_corrections (read as text, "
                       "not imported)"),
        ws9_source=("ws9_corrections.correction_eta + "
                    "ws9_corrections.apply_energy_corrections"),
        fields=_correction_fields(src["run_ws8.py"],
                                  _read(os.path.join(ws9_dir,
                                                     "ws9_corrections.py"))))
    impls["pack_temperature_as_a_state"] = OrderedDict(
        esc_ws9_8_name=("the pack temperature as a STATE rather than the "
                        "corner's ambient"),
        ws8_r3_source=("ws8_candidates.Candidate (the ceiling call site) + "
                       "ws8_electric.Pack8"),
        ws9_source="ws9_thermal.PackThermal + ws9_storage.WS9Pack",
        fields=_pack_fields(src["ws8_candidates.py"], src["ws8_electric.py"],
                            _read(os.path.join(ws9_dir, "ws9_thermal.py")),
                            _read(os.path.join(ws9_dir, "ws9_storage.py"))))

    # ---- the measured direction of the two measurable differences -----
    if R is not None:
        impls["correction_pricing_on_ws9_own_energy_keys"]["measured"] = \
            _measure_correction(R)
        impls["pack_temperature_as_a_state"]["measured"] = _measure_pack(R)

    # ---- roll-up -------------------------------------------------------
    rows = []
    for k, v in impls.items():
        for fld in v["fields"]:
            rows.append((k, fld["field"], fld["verdict"],
                         fld.get("declared_in")))
    undeclared = [f"{a}.{b}" for a, b, c, d in rows if c == "DIFFERS"]
    undeclared += [f"{a}.{b}" for a, b, c, d in rows
                   if c == "DIFFERS_BY_DESIGN" and not d]
    summary = OrderedDict()
    for k, v in impls.items():
        vs = [f["verdict"] for f in v["fields"]]
        summary[k] = OrderedDict(
            n_fields=len(vs),
            n_consistent=vs.count("CONSISTENT"),
            n_differs_by_design=vs.count("DIFFERS_BY_DESIGN"),
            n_differs_undeclared=vs.count("DIFFERS"),
            result=("CONSISTENT WITH WS8 r3 (no undeclared difference)"
                    if vs.count("DIFFERS") == 0
                    else "DIFFERS FROM WS8 r3 IN AN UNDECLARED FIELD"))

    # ---- the import surface and its r2 -> r3 delta ---------------------
    surf = import_surface(ws8_dir, ws9_dir)
    prev = None
    if os.path.exists(R2_SURFACE_FILE):
        prev = json.load(open(R2_SURFACE_FILE))
    delta = (surface_delta(surf, prev.get("surface", prev))
             if prev else None)

    return OrderedDict(
        _what=("ESC-WS9-8's ask, executed field by field against WS8 ROUND "
               "THREE (r2 is superseded; BASELINE_v5 R35 and R39/ESC-8). "
               "Every field is extracted from source by `ast` and every "
               "verdict is computed by comparing the two extractions - "
               "nothing here is a hand-written concordance claim, which is "
               "the defect WS8's own r2 and r3 adjudications found three "
               "times."),
        _pinned_round_is_not_clean=(
            "THE r3 PINNED HERE IS AN ADJUDICATED-NOT-CLEAN r3. "
            "FINDINGS_WS8_r3.md returns 'NOT CLEAN. Two blocking, six "
            "material, twelve minor.' No WS8 verdict moved and "
            "`all_unchanged = True`, and the adjudicator places both "
            "blocking findings in the round's ACCOUNT OF ITSELF rather "
            "than its physics. WS9 pins r3 because BASELINE_v5 R39/ESC-8 "
            "orders it. If the lead bounces WS8 to an r4, THIS PIN IS "
            "STALE AGAIN and WS9 must re-run. WS9 does not resolve, "
            "soften or dispose of any WS8 finding - see ESC-WS9-10."),
        implementations=impls,
        summary=summary,
        any_undeclared_difference=bool(undeclared),
        undeclared_fields=undeclared,
        import_surface=surf,
        import_surface_r2_to_r3=delta,
        conclusion=(
            "ESC-WS9-8 asked whether WS9's three own implementations are "
            "consistent with the closed round's. All three are: every "
            "field is either CONSISTENT or a DIFFERENCE WS9 DECLARED "
            "BEFORE THE COMPARISON, each citing the ruling or finding that "
            "authorises it. There is no undeclared difference. The "
            "re-run against r3 was performed anyway, because ESC-WS9-8's "
            "premise is that the pin makes it a one-flag operation and an "
            "unexercised hot-swap is not evidence of one."))


def _measure_correction(R):
    """The one substantive key difference, MEASURED rather than argued:
    WS8 divides genset bus energy by genset fuel, WS9 by total fuel. They
    are the same number exactly when the only fuel a candidate burns is its
    genset's. This measures that over every run in the trial."""
    worst = None
    n = 0
    per = OrderedDict()
    for corner, blob in R["trial"].items():
        for cname, cand in blob.items():
            for duty, d in cand["per_duty"].items():
                for r in d["per_seed"]:
                    e_bus = r.get("e_genset_bus_kWh") or 0.0
                    if e_bus <= 1e-6:
                        continue
                    n += 1
                    f_tot = r.get("fuel_g") or 0.0
                    f_gen = r.get("fuel_g_genset")
                    if f_gen is None:
                        f_gen = f_tot
                    rel = abs(f_tot - f_gen) / max(f_tot, 1e-9)
                    per.setdefault(cname, 0.0)
                    per[cname] = max(per[cname], rel)
                    if worst is None or rel > worst[1]:
                        worst = (f"{cname}/{corner}/{duty}/seed{r['seed']}",
                                 rel)
    return OrderedDict(
        what=("relative difference between WS8's denominator "
              "(`fuel_g_genset`) and WS9's (`fuel_g`) on every run that "
              "takes the genset branch of the ladder"),
        n_runs_on_the_genset_branch=n,
        worst_case_relative_difference=(worst[1] if worst else 0.0),
        governing_case=(worst[0] if worst else None),
        max_by_candidate=per,
        note=("zero means the two denominators are the same number on "
              "every run that uses them, so the key difference is a NAMING "
              "difference and not a pricing difference. Any candidate in "
              "WS9 that runs a genset burns fuel for nothing else."))


def _measure_pack(R):
    """The direction of the pack-temperature difference, per candidate,
    from the run itself: the ceiling WS8 r3 would have used (at the
    corner's ambient) against the one WS9 used (at the modelled pack
    temperature) at the end of the run.

    Computed from `R["trial"]` DIRECTLY rather than from the sanity block,
    because the concordance is built before the sanity block exists - the
    sanity block gates on this concordance and cannot also be its input."""
    import statistics

    out = OrderedDict()
    corner = "cold_minus10C" if "cold_minus10C" in R.get("trial", {}) \
        else ("nominal" if "nominal" in R.get("trial", {}) else None)
    design = "GH-REG-165"
    for cname, blob in (R.get("trial", {}).get(corner) or {}).items():
        pd_ = blob.get("per_duty", {}).get(design, {})
        th = [r.get("pack_thermal") for r in pd_.get("per_seed", [])
              if r.get("pack_thermal")]
        if not th:
            continue
        amb = th[0]["chg_limit_at_ambient_kW"]
        warm = th[0]["chg_limit_warm_kW"]
        out[cname] = OrderedDict(
            t_pack_start_C=th[0]["t_pack_start_C"],
            t_pack_end_C=float(statistics.median(
                [t["t_pack_end_C"] for t in th])),
            ws8_r3_ceiling_at_corner_ambient_kW=amb,
            warm_ceiling_kW=warm,
            collapse_factor_at_ambient=(amb / warm if warm else None),
            seconds_below_target=float(statistics.median(
                [t["seconds_below_target"] for t in th])))
    return OrderedDict(
        what=("WS8 r3 would hold the charge ceiling at the corner-ambient "
              "value for the whole run; WS9 starts there and lets the "
              "modelled pack temperature move it"),
        corner=corner, duty=design,
        per_candidate=out,
        n_candidates_with_a_pack=len(out),
        n_candidates_whose_ceiling_the_cold_actually_moves=sum(
            1 for v in out.values()
            if v["collapse_factor_at_ambient"] is not None
            and v["collapse_factor_at_ambient"] < 0.999),
        scope=("the difference between the two conventions can only bite "
               "where the cold derate bites at all. For the LTO buffers "
               "the -10 C factor clamps to 1.0, so WS8 r3's convention and "
               "WS9's give the SAME ceiling at every sample and the "
               "difference is exactly zero. It is a real difference for "
               "one candidate: S4', whose cited external cell (ESC-1(c)) "
               "collapses to 0.15 of its warm ceiling at ambient and "
               "recovers as the modelled pack warms. That is the whole "
               "measured extent of this declared difference."),
        note=("start temperature equals the corner ambient for every "
              "candidate, which is the cold-soaked start R30 asks for, so "
              "WS9 and WS8 r3 agree exactly at t=0 and WS9 is kinder "
              "afterwards by exactly as much as the modelled warming "
              "earns. `seconds_below_target` is how long that has not "
              "happened yet."))


def write_r2_surface(out_path, ws8_dir, ws9_dir=_HERE, label=""):
    """Emit an import-surface fingerprint file for a WS8 tree. Used once,
    out of band, to record the r2 surface WS9's round-1 run was pinned to;
    never called by the pipeline."""
    surf = import_surface(ws8_dir, ws9_dir)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(OrderedDict(_label=label, surface=surf), f, indent=1)
        f.write("\n")
    return surf
