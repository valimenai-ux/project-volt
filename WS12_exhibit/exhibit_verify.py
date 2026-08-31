"""WS12 — the verifier. This is the product, not the polish.

An exhibit that displayed one unverifiable number would refute the thing
it exists to demonstrate. `exhibit_verify.py` enumerates every number of
record the app can render — the manifest the build emits — and asserts,
with its own resolver and its own formatter, that each one resolves to
its cited file and key path and formats to the displayed string.

It runs thirteen checks:

  1  MANIFEST/BUNDLE     the manifest is exactly the set of renderable
                         strings in the bundle, re-walked independently
  2  CITATIONS           every cited number re-resolves and re-formats
                         to the displayed string, verbatim
  3  QUOTES              every quotation is lifted from its file again
                         and matches character for character
  4  FILE FACTS          every file fact's sha256 and size re-hash
  5  DERIVED             every derived number names what it came from,
                         and no derived number claims a JSON path
  6  BADGES              no promoted status in any badge position
  7  APP SOURCE          the app's own source contains no numeral of
                         record — the numbers can only come from the data
  8  DECIMATION          one manifest row per published trace, carrying
                         source path, source sha256, stride, row count
  9  SUBSEQUENCE         every 1 Hz file is a strict subsequence of its
                         10 Hz source AND of the published segments
 10  DECIMATION BADGE    the on-screen badge string is present, verbatim
 11  SANDBOX             the sandbox unit test passes
 12  SEVERITIES          every adjudication severity count re-parses from
                         its own findings file
 13  REPORT              every headline number in REPORT_WS12.md resolves
                         to the results data and appears verbatim

Run:  ../.venv/bin/python3 exhibit_verify.py
Exit: 0 on pass, 1 on any failure.
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PUBLIC = os.path.join(HERE, "app", "public")
DATA = os.path.join(PUBLIC, "data")
TRACES = os.path.join(PUBLIC, "traces")
SRC = os.path.join(HERE, "app", "src")

BADGE_ALLOWED = ("FROZEN-PROVISIONAL", "FROZEN-KILL", "FROZEN-RATIFIED",
                 "NOT CONVERGED", "NOT CUT")
BADGE_FORBIDDEN = ("RATIFIED", "PROVISIONAL")
DECIMATION_BADGE = "the replay is decimated; the record is not"

FAILURES = []
COUNTS = {}


def fail(check, msg):
    FAILURES.append((check, msg))


def tick(check, n=1):
    COUNTS[check] = COUNTS.get(check, 0) + n


# ---------------------------------------------------------------- own I/O

_DOCS = {}


def doc(rel):
    if rel not in _DOCS:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
            _DOCS[rel] = json.load(fh)
    return _DOCS[rel]


_TEXTS = {}


def text(rel):
    if rel not in _TEXTS:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
            _TEXTS[rel] = fh.read()
    return _TEXTS[rel]


def dig(obj, keys):
    """This verifier's OWN path resolver. Deliberately not imported from
    the builder: a shared resolver could agree with itself about a wrong
    path."""
    node = obj
    for k in keys:
        node = node[k]
    return node


def shape(value, fmt, pre, suf):
    """This verifier's OWN formatter."""
    if fmt == "str":
        body = "%s" % (value,)
    else:
        body = ("{:" + fmt + "}").format(value)
    return "%s%s%s" % (pre, body, suf)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_map(s):
    dash = {"‐": "-", "‑": "-", "‒": "-", "–": "-",
            "—": "-", "―": "-", "−": "-",
            "‘": "'", "’": "'", "“": '"', "”": '"',
            " ": " "}
    out = []
    idx = []
    prev = True
    for i, ch in enumerate(s):
        c = dash.get(ch, ch)
        if c.isspace():
            if prev:
                continue
            out.append(" ")
            idx.append(i)
            prev = True
        else:
            out.append(c)
            idx.append(i)
            prev = False
    return "".join(out), idx


# ==================================================================== 1
def check_manifest_matches_bundle(bundle, manifest):
    """Re-walk the bundle with an independent walker and require the
    manifest to be exactly the renderable set."""
    seen = []

    def walk(node, path):
        if isinstance(node, dict):
            if "s" in node and "tier" in node:
                seen.append((path, node["s"]))
                return
            for k in sorted(node):
                walk(node[k], path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)

    walk(bundle, "$")
    got = sorted(seen)
    want = sorted((m["key"], m["s"]) for m in manifest["entries"])
    if got != want:
        only_bundle = [x for x in got if x not in set(want)]
        only_man = [x for x in want if x not in set(got)]
        fail("1 MANIFEST/BUNDLE",
             "manifest and bundle disagree: %d only in bundle, %d only in "
             "manifest. First: %r / %r"
             % (len(only_bundle), len(only_man),
                only_bundle[:1], only_man[:1]))
    else:
        tick("1 MANIFEST/BUNDLE", len(got))


# ==================================================================== 2
def check_citations(manifest):
    for m in manifest["entries"]:
        if m["kind"] != "cite":
            continue
        try:
            value = dig(doc(m["file"]), m["path"])
        except Exception as exc:
            fail("2 CITATIONS", "%s: cannot resolve %s in %s (%s)"
                 % (m["key"], " -> ".join(str(k) for k in m["path"]),
                    m["file"], exc))
            continue
        if value != m["v"]:
            fail("2 CITATIONS", "%s: value on disk is %r, manifest says %r"
                 % (m["key"], value, m["v"]))
            continue
        got = shape(value, m["fmt"], m["pre"], m["suf"])
        if got != m["s"]:
            fail("2 CITATIONS",
                 "%s: %s -> %s formats to %r, screen shows %r"
                 % (m["key"], m["file"],
                    " -> ".join(str(k) for k in m["path"]), got, m["s"]))
            continue
        tick("2 CITATIONS")


# ==================================================================== 3
def check_quotes(manifest, bundle):
    probes = {}

    def walk(node):
        if isinstance(node, dict):
            if node.get("kind") == "quote":
                probes[(node["file"], node["s"])] = node.get("probe", "")
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(bundle)

    for m in manifest["entries"]:
        if m["kind"] != "quote":
            continue
        probe = probes.get((m["file"], m["s"]))
        if probe is None:
            fail("3 QUOTES", "%s: no probe recorded" % m["key"])
            continue
        hay = text(m["file"])
        hn, hidx = norm_map(hay)
        nn, _ = norm_map(probe)
        at = hn.find(nn)
        if at < 0:
            fail("3 QUOTES", "%s: probe not found in %s" % (m["key"],
                                                            m["file"]))
            continue
        start = hidx[at]
        end = hidx[at + len(nn) - 1] + 1
        lifted = " ".join(hay[start:end].split())
        if lifted != m["s"]:
            fail("3 QUOTES", "%s: %s lifts to %r, screen shows %r"
                 % (m["key"], m["file"], lifted, m["s"]))
            continue
        # And the displayed string must itself be present in the file.
        sn, _ = norm_map(m["s"])
        if sn not in hn:
            fail("3 QUOTES", "%s: displayed string is not in %s"
                 % (m["key"], m["file"]))
            continue
        tick("3 QUOTES")


# ==================================================================== 4
def check_file_facts(manifest):
    for m in manifest["entries"]:
        if m["kind"] == "fileref":
            p = os.path.join(ROOT, m["file"])
            if not os.path.exists(p):
                fail("4 FILE FACTS", "%s: %s does not exist"
                     % (m["key"], m["file"]))
                continue
            if m["s"] != os.path.basename(m["file"]):
                fail("4 FILE FACTS", "%s: renders %r, not the file name"
                     % (m["key"], m["s"]))
                continue
            tick("4 FILE FACTS")
            continue
        if m["kind"] != "file":
            continue
        p = os.path.join(ROOT, m["file"])
        if not os.path.exists(p):
            fail("4 FILE FACTS", "%s: %s does not exist" % (m["key"],
                                                            m["file"]))
            continue
        if os.path.getsize(p) != m["bytes"]:
            fail("4 FILE FACTS", "%s: %s is %d bytes, manifest says %d"
                 % (m["key"], m["file"], os.path.getsize(p), m["bytes"]))
            continue
        h = sha256(p)
        if h != m["sha256"]:
            fail("4 FILE FACTS", "%s: %s sha256 is %s, manifest says %s"
                 % (m["key"], m["file"], h, m["sha256"]))
            continue
        want = "%s · sha256 %s…%s" % (os.path.basename(m["file"]), h[:8],
                                      h[-4:])
        if want != m["s"]:
            fail("4 FILE FACTS", "%s: renders %r, should render %r"
                 % (m["key"], m["s"], want))
            continue
        tick("4 FILE FACTS")


# ==================================================================== 5
def check_srclines(manifest):
    """A constant declared in a Python source line is a fact on disk. This
    verifier re-opens the file, re-reads the line, re-parses the
    declaration and re-formats it, exactly as it does for a JSON field."""
    for m in manifest["entries"]:
        if m["kind"] != "srcline":
            continue
        p = os.path.join(ROOT, m["file"])
        if not os.path.exists(p):
            fail("4 FILE FACTS", "%s: %s missing" % (m["key"], m["file"]))
            continue
        with open(p, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        if m["line"] > len(lines):
            fail("4 FILE FACTS", "%s: %s has no line %d"
                 % (m["key"], m["file"], m["line"]))
            continue
        raw = lines[m["line"] - 1]
        if " ".join(raw.split()) != m["declaration"]:
            fail("4 FILE FACTS", "%s: %s:%d reads %r, manifest says %r"
                 % (m["key"], m["file"], m["line"], " ".join(raw.split()),
                    m["declaration"]))
            continue
        name, _, tail = raw.partition("=")
        if name.strip() != m["name"]:
            fail("4 FILE FACTS", "%s: %s:%d declares %r, not %r"
                 % (m["key"], m["file"], m["line"], name.strip(), m["name"]))
            continue
        try:
            value = float(tail.split("#")[0].strip())
        except ValueError:
            fail("4 FILE FACTS", "%s: cannot parse %r" % (m["key"], tail))
            continue
        if value != m["v"]:
            fail("4 FILE FACTS", "%s: source says %r, manifest says %r"
                 % (m["key"], value, m["v"]))
            continue
        got = shape(value, m["fmt"], m.get("pre", ""), m.get("suf", ""))
        if got != m["s"]:
            fail("4 FILE FACTS", "%s: formats to %r, screen shows %r"
                 % (m["key"], got, m["s"]))
            continue
        tick("4 FILE FACTS")


# The derived values the exhibit's argument rests on. Each is recomputed
# here from the record, independently of the builder (adjudication r1/m1).
def _speed_series(rel):
    """This verifier's own read of a trace's v_kmh column."""
    cols = None
    j = None
    out = []
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if line.startswith("#"):
                continue
            if cols is None:
                cols = line.split(",")
                j = cols.index("v_kmh")
                continue
            if not line:
                continue
            out.append(float(line.split(",")[j]))
    return out


def _rederive(bundle):
    out = {}
    ws4 = doc("WS4_genset/results_ws4.json")

    # --- the G1 waterfall's interaction term
    att = ws4["interface_ws4"]["gate_g1"]["attribution_rows"]
    out["$.screens.verdict.cards[0].waterfall[3].value"] = (
        att["both_g1r"]["delta_pp_min"]
        - att["map_vs_scalar_alone"]["delta_pp_min"]
        - att["spin_drag_alone"]["delta_pp_min"])

    # --- the KX chain: the blocking number and its exceedance
    probe = ws4["series_duty_v2"]["r6_rating_family_probe"]["cases"][
        "r6_rating_corner_full"]["per_seed"]
    reject = max(v["engine_reject_2min_max_kW"] for v in probe.values())
    share = ws4["heat_ledger_ws6"][
        "series_duty_v2_nominal_cycle_average"]["radiator_package_share"]
    design = ws4["heat_ledger_ws6"][
        "series_duty_v2_transient_vs_R20_design_point"][
            "r20_design_point_radiator_package_kW"]
    r6 = reject * share
    out["$.screens.rounds.kx.r6Radiator"] = r6
    out["$.screens.rounds.kx.exceedance"] = 100.0 * (r6 - design) / design

    # --- the sandbox's "about half the grade force"
    ws9 = doc("WS9_vehicle_one_wave2/results_ws9.json")
    cf = ws9["two_walls"]["single_ratio_closed_form"]["ENG-11L"]
    fr = ws9["two_walls"]["two_speed_solve"]["ENG-13L"]["solve"][
        "force_required"]
    out["$.screens.sandbox.s3.forceFraction"] = (
        100.0 * cf["F_available_at_ceiling_kN"] * 1000.0 / fr["total_N"])

    # --- the race screen's record gap, per dataset
    ws11 = doc("WS11_vehicle_zero_ruler/results_ws11.json")
    for i, p in enumerate(bundle["screens"]["race"]["pairs"]):
        base = ws11["results"][
            {"V1": "V1_on_VOLT-SUB", "V2": "V2_on_VOLT-REG"}[p["vehicle"]]
        ][p["case"]]
        seed = p["seed"]
        out["$.screens.race.pairs[%d].record.gapPp" % i] = (
            base["margin_pct_per_km_paired"]["per_seed"][seed]
            - base["margin_pct_per_payload_tkm_paired"]["per_seed"][seed])

    # --- the lane view's separation figures, re-measured from the two
    #     trace files themselves rather than trusted from the bundle
    for k, dset in enumerate(bundle["screens"]["sim"]["datasets"]):
        if dset["kind"] != "paired":
            continue
        base = "$.screens.sim.datasets[%d].separation" % k
        ca = _speed_series(dset["sourceFile"])
        ru = _speed_series(dset["rulerSourceFile"])
        n = min(len(ca), len(ru))
        xa = 0.0
        xb = 0.0
        dv = 0.0
        dx = 0.0
        for i in range(n):
            dv = max(dv, abs(ca[i] - ru[i]))
            xa += ca[i] / 3.6 * 0.1
            xb += ru[i] / 3.6 * 0.1
            dx = max(dx, abs(xa - xb))
        out[base + ".maxSpeedDifference"] = dv
        out[base + ".maxSeparation"] = dx
        out[base + ".finalSeparation"] = abs(xa - xb)
        out[base + ".candDistance"] = xa / 1000.0
        out[base + ".rulerDistance"] = xb / 1000.0
        out[base + ".samples"] = float(n)

    # --- the first-pass detection counts
    adj = bundle["screens"]["rounds"]["adjudications"]
    firsts = [a for a in adj if a["firstPass"]]
    out["$.screens.rounds.defectRate.firstPassRounds"] = float(len(firsts))
    out["$.screens.rounds.defectRate.firstPassWithDefects"] = float(len(
        [a for a in firsts
         if a["blocking"]["v"] + a["material"]["v"] > 0]))
    return out


def check_derived(manifest, bundle):
    want = _rederive(bundle)
    by_key = {m["key"]: m for m in manifest["entries"]}
    for key, value in sorted(want.items()):
        m = by_key.get(key)
        if m is None:
            fail("5 DERIVED", "%s is re-derivable but not in the manifest"
                 % key)
            continue
        if abs(float(m["v"]) - value) > 1e-9:
            fail("5 DERIVED", "%s: re-derived %r, the screen shows %r"
                 % (key, value, m["v"]))
            continue
        # `d` formats an int; a re-derivation that lands on a whole number
        # is re-cast the way the builder's own value is typed.
        recast = int(round(value)) if m["fmt"].endswith("d") else value
        got = shape(recast, m["fmt"], m.get("pre", ""), m.get("suf", ""))
        if got != m["s"]:
            fail("5 DERIVED", "%s: re-derives to %r, the screen shows %r"
                 % (key, got, m["s"]))
            continue
        tick("5 DERIVED")

    for m in manifest["entries"]:
        if m["kind"] != "derived":
            continue
        if not m.get("derivedFrom"):
            fail("5 DERIVED", "%s renders %r with no stated derivation"
                 % (m["key"], m["s"]))
            continue
        if "path" in m:
            fail("5 DERIVED", "%s claims a JSON path but is not a citation"
                 % m["key"])
            continue
        tick("5 DERIVED")


# ==================================================================== 6
def check_badges(bundle, manifest):
    for b in manifest.get("badges", []):
        if b.get("isStatus"):
            if b["badge"] not in BADGE_ALLOWED:
                fail("6 BADGES", "%s renders badge %r, which is not one of "
                     "BASELINE_v7_FREEZE's labels" % (b["key"], b["badge"]))
                continue
        else:
            # A non-status badge string (the decimation sentence, the tier
            # legend). It may not be a status word at all.
            up = b["badge"].upper()
            if any(t in up for t in BADGE_FORBIDDEN):
                fail("6 BADGES", "%s carries a status token in a non-status "
                     "badge: %r" % (b["key"], b["badge"]))
                continue
        tick("6 BADGES")
    # Nothing anywhere in the bundle may put a bare RATIFIED or PROVISIONAL
    # in a badge position. The walk keys on the SUFFIX, not on a list of
    # literal names, so a badge slot cannot escape it by being called
    # something new (adjudication r1/M2).
    hits = []
    seen = []

    def is_badge_key(k):
        return k in ("modeBadge", "tag", "badge") or k.endswith("Badge")

    def walk(node, path):
        if path == "$.interface_ws12":
            return
        if isinstance(node, dict):
            for k, v in node.items():
                if is_badge_key(k) and isinstance(v, str):
                    seen.append(path + "." + k)
                    up = v.upper()
                    for tok in BADGE_FORBIDDEN:
                        if tok in up and v not in BADGE_ALLOWED:
                            hits.append((path + "." + k, v))
                walk(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)

    walk(bundle, "$")
    for path, v in hits:
        fail("6 BADGES", "promoted status %r at %s" % (v, path))

    # Every badge-keyed string the walk finds must also be enumerated in
    # the manifest's badge list. This is the leg that caught nothing when
    # the harvest keyed on one literal name.
    listed = {b["key"] for b in manifest.get("badges", [])}
    for k in seen:
        if k not in listed:
            fail("6 BADGES", "%s is a badge position and is not enumerated "
                             "in the manifest" % k)
    if not hits:
        tick("6 BADGES")

    # And no bare status token may sit in a JSX <Label>, where a walk of
    # the DATA could never see it (adjudication r1/m8).
    if os.path.isdir(SRC):
        label_re = re.compile(r"<Label>([^<{]{1,160})</Label>")
        for base, _, names in os.walk(SRC):
            for n in sorted(names):
                if not n.endswith((".ts", ".tsx")):
                    continue
                with open(os.path.join(base, n), encoding="utf-8") as fh:
                    src = fh.read()
                for hit in label_re.finditer(src):
                    body = hit.group(1)
                    for tok in BADGE_FORBIDDEN:
                        for word in re.findall(r"[A-Za-z-]+", body):
                            if word.upper() == tok:
                                fail("6 BADGES",
                                     "%s renders a bare %s in a Label: %r"
                                     % (n, tok, body.strip()))
        tick("6 BADGES")


# ==================================================================== 7
# A "numeral of record" for this check is a rendered string that carries a
# decimal point, a percent sign or a thousands separator — the shape every
# result in this program takes. A bare integer with a unit ("10 Hz") is
# schema vocabulary, not a result, and is not policed here; the built-bundle
# scan below covers it anyway for anything that is genuinely a result.
DIGIT_UNIT = re.compile(
    r"[-+]?\d+\.\d+\s*(?:%|pp\b|kW|kWh|km\b|kg\b|Nm\b|rpm\b|g/kWh|L/100|"
    r"MB\b|:1|t-km|kN\b)"
)
STRING_LIT = re.compile(r"'([^'\\\n]{0,200})'|\"([^\"\\\n]{0,200})\"")


def _is_number_of_record(s):
    return any(c.isdigit() for c in s) and (
        "." in s or "%" in s or "," in s) and len(s) >= 4


def check_app_source(manifest):
    if not os.path.isdir(SRC):
        fail("7 APP SOURCE", "app/src does not exist")
        return
    files = []
    for base, _, names in os.walk(SRC):
        for n in sorted(names):
            if n.endswith((".ts", ".tsx")):
                files.append(os.path.join(base, n))
    blob = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            blob[f] = fh.read()

    numeric_strings = {m["s"] for m in manifest["entries"]
                       if m["kind"] in ("cite", "derived")
                       and _is_number_of_record(m["s"])}

    # (a) No string the exhibit displays as a number of record may appear
    #     in the app's own source.
    for f, src in blob.items():
        for s in numeric_strings:
            if s in src:
                fail("7 APP SOURCE",
                     "%s hard-codes the rendered string %r"
                     % (os.path.relpath(f, HERE), s))

    # (b) Nor may any string LITERAL in the source carry a decimal with a
    #     physical unit attached — that is what a transcribed result looks
    #     like, and layout geometry never does.
    for f, src in blob.items():
        for lit in STRING_LIT.finditer(src):
            body = lit.group(1) if lit.group(1) is not None else lit.group(2)
            if body is None:
                continue
            hit = DIGIT_UNIT.search(body)
            if hit:
                fail("7 APP SOURCE",
                     "%s has a transcribed result in a string literal: %r"
                     % (os.path.relpath(f, HERE), body[:90]))

    # (c) And the BUILT bundle must not contain them either: the numbers
    #     can only arrive by fetching the data bundle at run time.
    dist = os.path.join(HERE, "app", "dist", "assets")
    n_bundles = 0
    if os.path.isdir(dist):
        for n in sorted(os.listdir(dist)):
            if not n.endswith(".js"):
                continue
            n_bundles += 1
            with open(os.path.join(dist, n), "r", encoding="utf-8",
                      errors="replace") as fh:
                js = fh.read()
            for s in numeric_strings:
                if s in js:
                    fail("7 APP SOURCE",
                         "the built bundle assets/%s contains the rendered "
                         "string %r" % (n, s))
    # The built-bundle scan is the leg that covers what a visitor actually
    # downloads. A missing build made it a silent no-op that still passed
    # (adjudication r1/m3); it is now a failure.
    if n_bundles == 0:
        fail("7 APP SOURCE",
             "app/dist/assets holds no .js - the built-bundle scan cannot "
             "run. Build the app (run_ws12.py builds it by default) before "
             "verifying.")
    tick("7 APP SOURCE", len(files) + n_bundles)


# ==================================================================== 8
def check_decimation(dec, bundle):
    rows = dec["rows"]
    if not rows:
        fail("8 DECIMATION", "no published traces")
        return
    ids = set()
    for r in rows:
        for field in ("sourcePath", "sourceSha256", "stride", "outputRows1Hz",
                      "sourceRows", "decimation"):
            if field not in r:
                fail("8 DECIMATION", "%s: missing %s" % (r.get("id"), field))
        p = os.path.join(ROOT, r["sourcePath"])
        if not os.path.exists(p):
            fail("8 DECIMATION", "%s: source missing" % r["id"])
            continue
        if sha256(p) != r["sourceSha256"]:
            fail("8 DECIMATION", "%s: source sha256 has moved" % r["id"])
            continue
        if "averag" in r["decimation"].lower() \
                and "never" not in r["decimation"].lower():
            fail("8 DECIMATION", "%s: decimation is by averaging" % r["id"])
            continue
        want_1hz = (r["sourceRows"] + r["stride"] - 1) // r["stride"]
        if r["outputRows1Hz"] != want_1hz:
            fail("8 DECIMATION",
                 "%s: 1 Hz row count is %d, stride %d over %d source rows "
                 "gives %d" % (r["id"], r["outputRows1Hz"], r["stride"],
                               r["sourceRows"], want_1hz))
            continue
        if r["id"] in ids:
            fail("8 DECIMATION", "%s: duplicate id" % r["id"])
            continue
        ids.add(r["id"])
        tick("8 DECIMATION")
    served = {r["sourcePath"] for r in rows}
    for tid, t in bundle["traces"].items():
        if t["sourcePath"] not in served:
            fail("8 DECIMATION", "%s is served but has no manifest row" % tid)


# ==================================================================== 9
def read_csv_rows(path):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines[0], lines[1:]


def check_subsequence(dec):
    for r in dec["rows"]:
        d = os.path.join(TRACES, r["id"])
        head1, scrub = read_csv_rows(os.path.join(d, "scrub_1hz.csv"))

        # (a) against the published 10 Hz segments
        seg_rows = []
        for s in r["segments"]:
            h, body = read_csv_rows(os.path.join(d, s["file"]))
            if h != head1:
                fail("9 SUBSEQUENCE", "%s/%s: header differs from scrub"
                     % (r["id"], s["file"]))
            if len(body) != s["rows"]:
                fail("9 SUBSEQUENCE", "%s/%s: %d rows, manifest says %d"
                     % (r["id"], s["file"], len(body), s["rows"]))
            seg_rows.extend(body)
        if len(seg_rows) != r["outputRows10Hz"]:
            fail("9 SUBSEQUENCE", "%s: segments hold %d rows, manifest says "
                 "%d" % (r["id"], len(seg_rows), r["outputRows10Hz"]))
            continue
        i = 0
        for row in seg_rows:
            if i < len(scrub) and scrub[i] == row:
                i += 1
        if i != len(scrub):
            fail("9 SUBSEQUENCE",
                 "%s: the 1 Hz file is NOT a subsequence of the published "
                 "10 Hz segments (matched %d of %d rows)"
                 % (r["id"], i, len(scrub)))
            continue

        # (b) and, independently, against the ORIGINAL file on disk
        src = os.path.join(ROOT, r["sourcePath"])
        cols = None
        want = []
        n = 0
        with open(src, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n").rstrip("\r")
                if line.startswith("#"):
                    continue
                if cols is None:
                    cols = line.split(",")
                    keep = [cols.index(c) for c in head1.split(",")]
                    continue
                if not line:
                    continue
                if n % r["stride"] == 0:
                    f = line.split(",")
                    want.append(",".join(f[k] for k in keep))
                n += 1
        if n != r["sourceRows"]:
            fail("9 SUBSEQUENCE", "%s: source has %d rows, manifest says %d"
                 % (r["id"], n, r["sourceRows"]))
            continue
        if want != scrub:
            bad = next((k for k in range(min(len(want), len(scrub)))
                        if want[k] != scrub[k]), None)
            fail("9 SUBSEQUENCE",
                 "%s: the 1 Hz file is not the strided sample of its source "
                 "(first difference at row %r)" % (r["id"], bad))
            continue
        tick("9 SUBSEQUENCE")


# =================================================================== 10
def check_decimation_badge(bundle, dec):
    blob = json.dumps(bundle, ensure_ascii=False)
    if DECIMATION_BADGE not in blob:
        fail("10 DECIMATION BADGE",
             "the badge string is not in the bundle, verbatim")
        return
    if dec.get("badge") != DECIMATION_BADGE:
        fail("10 DECIMATION BADGE",
             "the decimation manifest's badge is %r" % dec.get("badge"))
        return
    if bundle.get("decimationBadge") != DECIMATION_BADGE:
        fail("10 DECIMATION BADGE", "bundle.decimationBadge is wrong")
        return
    tick("10 DECIMATION BADGE")

    # The directive names this string as verbatim. Checking it three ways
    # in the DATA and never in the RENDERING let an up-casing survive
    # (adjudication r1/m2). The app must render the string as-is; any
    # visual up-casing belongs in CSS.
    for name in ("screens/RaceMode.tsx", "screens/Simulator.tsx"):
        p = os.path.join(SRC, name)
        if not os.path.exists(p):
            fail("10 DECIMATION BADGE", "%s missing" % name)
            continue
        with open(p, encoding="utf-8") as fh:
            src = fh.read()
        bad = re.search(r"(?:decimationBadge|\bbadge)\s*\.toUpperCase\(\)",
                        src)
        if bad:
            fail("10 DECIMATION BADGE",
                 "%s up-cases the badge in JS (%r); render it verbatim and "
                 "use text-transform" % (name, bad.group(0)))
            continue
        if "textTransform: 'uppercase'" not in src:
            fail("10 DECIMATION BADGE",
                 "%s neither up-cases nor declares text-transform; the "
                 "rendered form is unproven" % name)
            continue
        tick("10 DECIMATION BADGE")


# =================================================================== 12
WORDS = {"no": 0, "none": 0, "zero": 0, "one": 1, "two": 2, "three": 3,
         "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
         "fourteen": 14, "fifteen": 15}


def _severities(rel):
    """This verifier's OWN parse of a findings file's severity counts.
    Written separately from the builder's on purpose."""
    body = text(rel)
    if "FINDINGS_WS3_r" in rel:
        rnd = "r1" if "_r1" in rel else "r2"
        pat = r"WS3-" + rnd + r"-[A-Z]\d+\s*[—–-]\s*" \
              r"(BLOCKING|MATERIAL|MINOR)"
        tally = {"BLOCKING": 0, "MATERIAL": 0, "MINOR": 0}
        for hit in re.finditer(pat, body):
            tally[hit.group(1)] += 1
        return tally["BLOCKING"], tally["MATERIAL"], tally["MINOR"]
    flat = " ".join("\n".join(body.splitlines()[:40]).split())
    if re.search(r"\bNo new findings of any severity\b", flat, re.I):
        return 0, 0, 0
    both_zero = bool(re.search(r"\bno blocking or material\b", flat, re.I))

    def grab(word):
        if both_zero and word in ("blocking", "material"):
            return 0
        hit = re.search(r"(\S+)\s+(?:NEW\s+|new\s+)?" + word, flat, re.I)
        if not hit:
            return None
        tok = hit.group(1)
        return int(tok) if tok.isdigit() else WORDS.get(tok.lower())

    return grab("blocking"), grab("material"), grab("minor")


def check_severities(bundle):
    for a in bundle["screens"]["rounds"]["adjudications"]:
        got = _severities(a["file"])
        want = (a["blocking"]["v"], a["material"]["v"], a["minor"]["v"])
        if got != want:
            fail("12 SEVERITIES",
                 "%s %s: this verifier reads %r from %s, the screen shows %r"
                 % (a["ws"], a["round"], got, a["file"], want))
            continue
        tick("12 SEVERITIES")


# =================================================================== 13
def check_report(bundle):
    """Every headline number in REPORT_WS12.md resolves to the results
    data and appears in the report verbatim."""
    rep = os.path.join(HERE, "REPORT_WS12.md")
    asserts = os.path.join(HERE, "report_assertions.json")
    if not (os.path.exists(rep) and os.path.exists(asserts)):
        fail("13 REPORT",
             "REPORT_WS12.md / report_assertions.json not built yet - run "
             "make_report_ws12.py, then this verifier again")
        return
    with open(rep, encoding="utf-8") as fh:
        body = fh.read()
    with open(asserts, encoding="utf-8") as fh:
        rows = json.load(fh)["assertions"]
    for r in rows:
        try:
            value = dig(bundle, r["path"])
        except Exception as exc:
            fail("13 REPORT", "cannot resolve %s in the results data (%s)"
                 % (" -> ".join(str(k) for k in r["path"]), exc))
            continue
        got = shape(value, r["fmt"], r.get("pre", ""), r.get("suf", ""))
        if got != r["s"]:
            fail("13 REPORT", "%s formats to %r, the report says %r"
                 % (" -> ".join(str(k) for k in r["path"]), got, r["s"]))
            continue
        if r["s"] not in body:
            fail("13 REPORT", "%r is not present in REPORT_WS12.md" % r["s"])
            continue
        tick("13 REPORT")


# =================================================================== 11
def check_sandbox():
    sys.path.insert(0, HERE)
    import test_sandbox_ws12 as T
    checks = T.run()
    bad = [c for c in checks if not c["pass"]]
    for c in bad:
        fail("11 SANDBOX", "%s: got %r want %r" % (c["name"], c["got"],
                                                   c["want"]))
    tick("11 SANDBOX", len(checks) - len(bad))


# ==================================================================== go
def main():
    for p in ("exhibit_data.json", "manifest.json",
              "decimation_manifest.json"):
        if not os.path.exists(os.path.join(DATA, p)):
            print("FAIL: %s missing. Run build_exhibit_data.py first." % p)
            return 1
    with open(os.path.join(DATA, "exhibit_data.json"), encoding="utf-8") as f:
        bundle = json.load(f)
    with open(os.path.join(DATA, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(DATA, "decimation_manifest.json"),
              encoding="utf-8") as f:
        dec = json.load(f)

    check_manifest_matches_bundle(bundle, manifest)
    check_citations(manifest)
    check_quotes(manifest, bundle)
    check_file_facts(manifest)
    check_srclines(manifest)
    check_derived(manifest, bundle)
    check_badges(bundle, manifest)
    check_app_source(manifest)
    check_decimation(dec, bundle)
    check_subsequence(dec)
    check_decimation_badge(bundle, dec)
    check_sandbox()
    check_severities(bundle)
    check_report(bundle)

    with open(os.path.join(DATA, "verify_summary.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({
            "checks": {k: {"checked": COUNTS.get(k, 0),
                           "failed": sum(1 for f in FAILURES if f[0] == k)}
                       for k in sorted(set(list(COUNTS)
                                           + [f[0] for f in FAILURES]))},
            "assertions_total": sum(COUNTS.values()),
            "failures_total": len(FAILURES),
            "result": "FAIL" if FAILURES else "PASS",
        }, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("EXHIBIT VERIFY — WS12")
    print("=" * 68)
    def order(name):
        head = name.split(" ", 1)[0]
        return (int(head) if head.isdigit() else 999, name)

    for name in sorted(set(list(COUNTS) + [f[0] for f in FAILURES]),
                       key=order):
        n_fail = sum(1 for f in FAILURES if f[0] == name)
        print("%-22s %6d checked  %6d failed  %s"
              % (name, COUNTS.get(name, 0), n_fail,
                 "PASS" if n_fail == 0 else "FAIL"))
    print("=" * 68)
    if FAILURES:
        print("\n%d FAILURES:" % len(FAILURES))
        for name, msg in FAILURES[:60]:
            print("  [%s] %s" % (name, msg))
        if len(FAILURES) > 60:
            print("  ... and %d more" % (len(FAILURES) - 60))
        print("\nRESULT: FAIL")
        return 1
    total = sum(COUNTS.values())
    print("\n%d assertions, 0 failures." % total)
    print("Traces published: %d, %.2f MB, %d rows at 10 Hz, %d at 1 Hz."
          % (dec["totals"]["traces"],
             dec["totals"]["publishedBytes"] / 1e6,
             dec["totals"]["sourceRows"], dec["totals"]["rows1Hz"]))
    print("Manifest: %d entries (%d cited, %d quoted, %d file facts, "
          "%d file refs, %d derived)."
          % (manifest["counts"]["total"], manifest["counts"]["cite"],
             manifest["counts"]["quote"], manifest["counts"]["file"],
             manifest["counts"].get("fileref", 0),
             manifest["counts"]["derived"]))
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
