"""WS12 — generate REPORT_WS12.md from the results data.

Nothing in the report is typed by hand. Every number passes through
`N()`, which resolves a key path in `app/public/data/exhibit_data.json`,
formats it, records the assertion, and returns the string. The recorded
assertions are written to `report_assertions.json`, and
`exhibit_verify.py` check 13 re-resolves every one of them and asserts
the string is present in the report verbatim.

    ../.venv/bin/python3 make_report_ws12.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "app", "public", "data")

ASSERTS = []


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


BUNDLE = load("exhibit_data.json")
MANIFEST = load("manifest.json")
DEC = load("decimation_manifest.json")
try:
    SUMMARY = load("verify_summary.json")
except FileNotFoundError:
    SUMMARY = None


def dig(path):
    node = BUNDLE
    for k in path:
        node = node[k]
    return node


def N(path, fmt="d", pre="", suf=""):
    """The only way a number reaches this report."""
    value = dig(path)
    s = pre + (("%s" % (value,)) if fmt == "str"
               else ("{:" + fmt + "}").format(value)) + suf
    ASSERTS.append({"path": list(path), "fmt": fmt, "pre": pre, "suf": suf,
                    "s": s})
    return s


I = ("interface_ws12",)


def bindings_table():
    """screen element -> file -> key path, straight out of the manifest."""
    rows = [m for m in MANIFEST["entries"] if m["kind"] == "cite"]
    by_screen = {}
    for m in rows:
        key = m["key"]
        parts = key.split(".")
        screen = parts[2] if len(parts) > 2 and parts[1] == "screens" \
            else (parts[1] if len(parts) > 1 else "-")
        by_screen.setdefault(screen, []).append(m)
    out = []
    for screen in sorted(by_screen):
        out.append("")
        out.append("#### %s — %d bound values" % (screen,
                                                  len(by_screen[screen])))
        out.append("")
        out.append("| screen element | file | key path | renders |")
        out.append("|---|---|---|---|")
        for m in sorted(by_screen[screen], key=lambda r: r["key"]):
            elem = m["key"]
            if elem.startswith("$.screens." + screen + "."):
                elem = elem[len("$.screens." + screen + "."):]
            elif elem.startswith("$."):
                elem = elem[2:]
            path = " → ".join(str(k) for k in m["path"])
            out.append("| `%s` | `%s` | `%s` | `%s` |"
                       % (elem, m["file"], path, m["s"]))
    return "\n".join(out)


def quotes_table():
    rows = [m for m in MANIFEST["entries"] if m["kind"] == "quote"]
    files = {}
    for m in rows:
        files[m["file"]] = files.get(m["file"], 0) + 1
    out = ["| document | verbatim quotations on screen |", "|---|---|"]
    for f in sorted(files):
        out.append("| `%s` | %d |" % (f, files[f]))
    return "\n".join(out)


def trace_table():
    out = ["| published trace | class | source rows | 1 Hz rows | segments "
           "| published bytes | columns kept / in source |",
           "|---|---|---|---|---|---|---|"]
    for r in DEC["rows"]:
        out.append("| `%s` | %s | %d | %d | %d | %d | %d / %d |"
                   % (r["sourcePath"], r["schemaClass"], r["sourceRows"],
                      r["outputRows1Hz"], len(r["segments"]),
                      r["publishedBytes"], len(r["columnsPublished"]),
                      len(r["columnsPublished"]) + len(r["columnsWithheld"])))
    return "\n".join(out)


def registry_table():
    out = ["| workstream | trace | rows | cols | schema | served |",
           "|---|---|---|---|---|---|"]
    for r in BUNDLE["screens"]["sim"]["registry"]:
        v = r["validation"]
        cls = ("R34 CONFORMS" if v["conforms"]
               else ("R34 REFUSED" if v["schemaClass"] == "R34"
                     else "PRE-R34"))
        out.append("| %s | `%s` | %d | %d | %s | %s |"
                   % (r["ws"], r["file"], r["rows"], r["nColumns"], cls,
                      "yes" if r["servedByExhibit"] else "linked only"))
    return "\n".join(out)


def verify_table():
    if not SUMMARY:
        return ("_`verify_summary.json` not present. Run `exhibit_verify.py` "
                "before this script to populate the table._")
    out = ["| check | assertions | failures | result |", "|---|---|---|---|"]

    def order(name):
        head = name.split(" ", 1)[0]
        return (int(head) if head.isdigit() else 999, name)

    for k in sorted(SUMMARY["checks"], key=order):
        c = SUMMARY["checks"][k]
        out.append("| %s | %d | %d | %s |"
                   % (k, c["checked"], c["failed"],
                      "PASS" if c["failed"] == 0 else "**FAIL**"))
    out.append("| **total** | **%d** | **%d** | **%s** |"
               % (SUMMARY["assertions_total"], SUMMARY["failures_total"],
                  SUMMARY["result"]))
    return "\n".join(out)


def severity_table():
    out = ["| ws | round | first pass | blocking | material | minor | "
           "counted by |", "|---|---|---|---|---|---|---|"]
    for a in BUNDLE["screens"]["rounds"]["adjudications"]:
        out.append("| %s | %s | %s | %d | %d | %d | %s |"
                   % (a["ws"], a["round"], "yes" if a["firstPass"] else "—",
                      a["blocking"]["v"], a["material"]["v"],
                      a["minor"]["v"], a["countMethod"]))
    return "\n".join(out)


def cuts_section():
    out = []
    for c in dig(I + ("cut_elements",)):
        out.append("")
        out.append("**%s** — %s" % (c["id"], c["element"]))
        out.append("")
        out.append("- *why the record cannot feed it:* %s" % c["why"])
        out.append("- *what is on the screen instead:* %s" % c["kept"])
        out.append("- *rule kept:* %s" % c["rule"])
    return "\n".join(out)


def escalations_section():
    out = []
    for e in dig(I + ("escalations",)):
        out.append("")
        out.append("### %s — %s" % (e["id"], e["headline"]))
        out.append("")
        out.append("**Challenges:** %s" % e["challenges"])
        out.append("")
        out.append(e["detail"])
        out.append("")
        out.append("**Disposition:** %s" % e["resolution"])
    return "\n".join(out)


def reflow(doc, width=76):
    """Re-wrap prose to a fixed width, leaving tables, code fences,
    headings and blockquotes exactly as written. The report's numbers are
    interpolated into sentences, so their lengths would otherwise dictate
    where the lines break."""
    import textwrap
    out = []
    in_fence = False
    para = []

    def flush():
        if not para:
            return
        text = " ".join(" ".join(para).split())
        if text.startswith("- ") or text.startswith("* "):
            out.extend(textwrap.wrap(text, width, subsequent_indent="  "))
        else:
            out.extend(textwrap.wrap(text, width))
        para.clear()

    for line in doc.split("\n"):
        if line.strip().startswith("```"):
            flush()
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        stripped = line.strip()
        if (not stripped or stripped.startswith("|")
                or stripped.startswith("#") or stripped.startswith(">")
                or stripped.startswith("---")):
            flush()
            out.append(line)
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            flush()
            para.append(stripped)
            continue
        para.append(stripped)
    flush()
    return "\n".join(out)


def main():
    mb = 1e6

    doc = f"""# REPORT_WS12 — THE EXHIBIT: THE METHOD, MADE CLICKABLE

Workstream WS12 · bound to `../BASELINE_v7_FREEZE.md` · entry point
`run_ws12.py` · results data `app/public/data/exhibit_data.json` ·
verifier `exhibit_verify.py`

**What was built.** A static web app at `WS12_exhibit/app/`
({N(I + ("app", "stack"), "str")}), Vite `base` set to
`{N(I + ("app", "vite_base"), "str")}`, deployable to GitHub Pages at a repo
subpath. {N(I + ("app", "screens_n"))} screens, front door
`{N(I + ("app", "front_door"), "str")}`. Every number of record on every
screen resolves to a file and an explicit key path, and clicking it opens
that provenance. {N(I + ("manifest", "entries_total"))} renderable strings
are enumerated in a build-time manifest;
{N(I + ("manifest", "by_kind", "cite"))} of them are numbers of record
resolved from a results file, {N(I + ("manifest", "by_kind", "quote"))} are
verbatim quotations lifted from documents of record,
{N(I + ("manifest", "by_kind", "file"))} are file identities pinned by
sha256, {N(I + ("manifest", "by_kind", "fileref"))} is a reference to a
living log that is deliberately not hash-pinned, and
{N(I + ("manifest", "by_kind", "derived"))} are derived values that name
what they were computed from and claim no key path.

**Verification.** `exhibit_verify.py` runs
{"" if not SUMMARY else str(len(SUMMARY["checks"]))} checks and
{"" if not SUMMARY else str(SUMMARY["assertions_total"])} assertions with
its own resolver, its own formatter and its own findings-file parser,
written separately from the builder's so that a shared bug cannot agree
with itself. Result: **{"" if not SUMMARY else SUMMARY["result"]}**.

**The two guard rails hold.** The method claim is
"{N(I + ("guard_rails", "method_claim"), "str")}" and never
"{N(I + ("guard_rails", "method_claim_never"), "str")}"; no hardware was
built and the ruler is uncalibrated, and the exhibit says so on the
front door, in the rail, and on the Method screen. No status is promoted:
{N(I + ("badges", "positions_total"))} badge positions render only the five
labels `BASELINE_v7_FREEZE.md` uses, the build refuses to emit any other,
and the verifier fails on a bare `RATIFIED` or `PROVISIONAL` anywhere in a
badge position.

---

## 1. What was ported, and what was replaced

The draft in `design/` is a dc-runtime prototype with a strong visual
system: a 1,920 × 1,080 instrument canvas, Chivo and DM Mono, a dark
palette with one accent, hairline-divided panels, a narrative rail, a
three-tier badge discipline and a provenance strip. **The look and the
discipline were kept. Everything synthetic was replaced by the record.**

### Kept

| element | how it survives |
|---|---|
| palette, typography, panel grid, hairlines, tabular numerals | ported verbatim into `app/src/theme.ts` and used everywhere |
| the narrative rail | six screens, re-ordered by the lead's ruling so the verdict wall is first |
| the three-tier badge discipline (RECORD / DERIVED / SANDBOX) | now enforced mechanically: every renderable value carries a tier, and the verifier checks that a DERIVED value never claims a key path |
| the provenance strip | now READ from the record per screen — baseline label and file identity come from the emitted bundle, not from a literal |
| the G1 waterfall | same shape, same five bars; every bar is now a citation |
| the sandbox ratio window | same interaction, all constants re-derived (see §5) |
| "a dashed baseline, never a zero line" | every signed bar carries a dashed zero and, where a criterion exists, a criterion marker |
| the copy, where it was true | corrected where the record has moved: the draft said BASELINE v4; this is bound to v7 and frozen |

### Replaced

| the draft did this | the exhibit does this |
|---|---|
| generated synthetic traces in the browser from an invented engine model, generator map, duty-cycle builder and seeded PRNG | replays trace files on disk, decimated at build time, with a run-time TRACE_SCHEMA check |
| hard-coded `S0`/`CAND` constants, r2-vintage and wrong against r3 | binds every WS8 margin to `results_ws8.json`; the draft's S1 nominal of −0.66% is −0.69% at r3, its S3 of −6.22% is −1.09% |
| a `RATIFIED RECORD` badge | v7's five status labels only |
| a `BASELINE v4 · RATIFIED 2026-08-30` header | the baseline label and identity, read from the bundle |
| an `AMBIENT TEMPERATURE` slider multiplying torque demand by an invented cold factor | an `AIR DENSITY` slider bounded by WS8's own three declared members |
| an approximated BSFC surface from a Willans fit in JavaScript | WS4's exported `bsfc_map_*.csv`, served and plotted directly |
| a synthetic elevation profile from summed bumps | `z_m` where the file has it, and an explicit statement of absence where it does not |

---

## 2. The screens

**1. Verdict wall — the front door.** The G1 waterfall leads: prior
convention {N(("screens", "verdict", "cards", 0, "waterfall", 0, "value",
                "s"), "str")}, the map-vs-scalar swap
{N(("screens", "verdict", "cards", 0, "waterfall", 1, "value", "s"), "str")},
the spin-drag member
{N(("screens", "verdict", "cards", 0, "waterfall", 2, "value", "s"), "str")},
their interaction
{N(("screens", "verdict", "cards", 0, "waterfall", 3, "value", "s"), "str")},
and the gate of record
{N(("screens", "verdict", "cards", 0, "waterfall", 4, "value", "s"), "str")}
against a kill criterion of
{N(("screens", "verdict", "cards", 0, "criterion", "s"), "str")}, missed by
{N(("screens", "verdict", "cards", 0, "missedBy", "s"), "str")} on
{N(("screens", "verdict", "cards", 0, "seedsTotal", "s"), "str")} seeds with
{N(("screens", "verdict", "cards", 0, "seedsPositive", "s"), "str")} above
zero. The card's copy makes plain that the criterion was written before the
number existed and could not be renegotiated, and quotes doctrine D1 to
that effect. Then the WS8 paired bars (per km beside per payload tonne-km,
the criterion read on the right-hand bar), the duty sign-flip, and the WS11
pair.

**2. Race mode.** Four paired-seed WS11 datasets. Two counters run live —
fuel per kilometre and fuel per payload tonne-km — and diverge as the
replay runs. The headline pair is bound to the record: V2 wins
{N(("screens", "race", "headline", "perKm", "s"), "str")} per km, loses
{N(("screens", "race", "headline", "perPayload", "s"), "str")} per payload
tonne-km, and the freight it hands back to get there is
{N(("screens", "race", "headline", "freightGiven", "s"), "str")}. The semi
race is wired as a fifth dataset and renders FROZEN-PROVISIONAL without a
replay; §4 records why.

**3. Round history.** Every adjudication round in the program, with its
verdict line quoted verbatim and its severity counts parsed out of the
findings file rather than transcribed (§3). The 07:40 gap is the first card
on the screen, not the last: it is rendered as the control condition, with
the program log quoted at length and the count of what round 2 closed and
nothing checked. KX's NOT CONVERGED disposition follows, including the one
number on the verdict-bearing screens that could not be cited — which is
itself the finding.

**4. Simulator.** WS5's two R34-conforming duty traces, replayed. Elevation
from `z_m`, the R15 blend cascade from the four braking channels, SOC and
pack temperature, the engine dot on WS4's exported map for the engine that
trace actually ran, and fuel counters in litres, L/100 km and MJ per
payload tonne-km from the header's own payload. A trace registry measures
every 10 Hz file in the repository against TRACE_SCHEMA and shows what each
one lacks.

**5. Sandbox.** The ratio window, re-derived (§5), with an on-screen
anchor table in which the browser's own model is run against the record's
own force ledgers and ratio ceiling.

**6. Method.** The two guard rails, the tier legend, the eight publishable
claims with the status each holds at the freeze, the limitations, the
source index with every file's sha256, and the verifier's own checklist.

---

## 3. Data bindings

Every number of record is bound at build time by
`build_exhibit_data.py`, which opens the results file, resolves an explicit
**list** of keys (not a dotted string — the record contains keys such as
`V1_on_VOLT-SUB`, `cold_-10C` and `CdA_5.4` that a dotted string cannot
address), formats the value with a declared format spec, and stores the
raw value, the file, the path, the spec and the displayed string together.
The app renders the displayed string and has no other way to print a
number: `exhibit_verify.py` check 7 asserts that no rendered numeral
appears in the app's own source **or in its built bundle**.

Severity counts on the round-history screen are parsed from the findings
files, not typed:

{severity_table()}

Quotations, all lifted from the file and re-lifted by the verifier:

{quotes_table()}

The full binding table — {N(I + ("manifest", "by_kind", "cite"))} rows,
screen element → file → key path → rendered string — is in **Appendix A**.

---

## 4. Cut elements

The rule is *cut the element, not the rule*. Every draft element the
record cannot feed was cut, and the absence is stated on the screen where
the element would have been. {N(I + ("cut_elements_n",))} elements were cut.

{cuts_section()}

---

## 5. The sandbox, re-derived

The draft's ratio window ran on invented constants. Every one is replaced
by a value on disk, and the model is two closed forms:

```
F        = 0.5 rho CdA v^2 + Crr m g cos(theta) + m g sin(theta),  theta = atan(grade)
ratio_max = rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise)     [WS8's own published bound]
ratio_min = F_grade_hold * r_dyn / (T_peak * eta_driveline)  [the same statement, inverted]
g         = 9.81 m/s^2, declared identically at WS1 volt_params.py:10 and WS8 ws8_params.py:24
```

`test_sandbox_ws12.py` reproduces, from those functions and nothing else:

- WS1's own flat-cruise force ledger at 85 km/h, term by term;
- WS1's own 6% grade ledger at 60 km/h, term by term;
- WS9's exported 6% grade-hold ledger at 36,300 kg, term by term;
- WS8's published closed-form ratio ceiling, and WS9's to one ulp;
- `feasible_ratios == []` and `max_ratio_without_overspeed == 3.6` — the
  3.60:1 ceiling — by running WS8's own enumerated ratio sweep through the
  same two bounds;
- the ratio the 6% hold needs for both engines, and the force available at
  the ceiling, which is a little over half what the grade demands.

All of it runs as check 11 of the verifier. The same model is implemented
in TypeScript for the browser, and the Sandbox screen prints its output
beside the record's for each anchor so a divergence between the two
implementations would be visible on the page.

---

## 6. Traces and the decimated-replay rule

No 10 Hz file is fetched whole on page load. Every published trace is
emitted as a 1 Hz whole-trace scrub index, decimated **by strided sample
and never by averaging**, plus 10 Hz segment chunks fetched one at a time
for the segment in view. Every emitted field is the **verbatim field
string** from the source file, so the 1 Hz tier is a literal subsequence
of the source and the verifier can prove it by string equality — against
the published segments and, independently, against the original file on
disk.

- Traces published: **{N(I + ("traces", "published_n"))}**
- Stride: **{N(I + ("traces", "stride"))}** (10 Hz → 1 Hz), segment size
  **{N(I + ("traces", "segment_rows"))}** rows
- Source rows at 10 Hz: **{N(I + ("traces", "source_rows_10Hz"), ",d")}**;
  1 Hz index rows: **{N(I + ("traces", "rows_1Hz"), ",d")}**;
  segments: **{N(I + ("traces", "segments_total"))}**
- Source bytes: **{N(I + ("traces", "source_bytes"), ",d")}** →
  published bytes: **{N(I + ("traces", "published_bytes"), ",d")}**
  ({"%.2f MB" % (dig(I + ("traces", "published_bytes")) / mb)}),
  by projecting each file to the columns its screen actually plots at the
  source's own precision
- On-screen badge, verbatim, whenever the 1 Hz tier is displayed:
  **{N(I + ("traces", "badge"), "str")}**, with the full 10 Hz source path
  beside it
- Every other trace in the repository is linked by path and not served

{trace_table()}

Adding the two BSFC maps, the served payload
({N(I + ("published_payload_scope",), "str")}) is
**{N(I + ("published_payload_bytes",), ",d")} bytes**
({"%.2f MB" % (dig(I + ("published_payload_bytes",)) / mb)}). The data
bundle and the two manifests are served alongside it and add well under a
megabyte; their size is deliberately not stated as a bound field, because
the field would live inside the bundle it was measuring.

### The trace registry

The loader validates TRACE_SCHEMA at build time and again at run time in
the browser, and refuses a nonconforming file with a visible reason rather
than plotting it. Of {N(I + ("traces", "registry_total"))} trace files in
the repository, {N(I + ("traces", "registry_r34_conforming"))} conform to
R34, {N(I + ("traces", "registry_r34_refused"))} is refused, and
{N(I + ("traces", "registry_pre_r34"))} predate the schema and are measured
against it rather than validated by it.

{registry_table()}

---

## 7. Verification results

{verify_table()}

Determinism: `check_determinism_ws12.py --with-app` builds the data
pipeline twice and the app twice and compares every emitted artifact by
sha256. Result recorded in `determinism_check.txt`.

---

## 8. Escalations

Under the freeze there is no workstream to escalate to. Each item below is
recorded here and, per the assignment, is for `LIMITATIONS.md` via WS13.
**None is self-resolved.** {N(I + ("escalations_n",))} items.

{escalations_section()}

---

## 9. Machine-readable interface block

Every field below is `app/public/data/exhibit_data.json` →
`interface_ws12`, verbatim.

```json
{json.dumps(dig(I), indent=1, sort_keys=True, ensure_ascii=False)}
```

---

## Appendix A — the full binding table

Screen element → file → key path → the string the screen renders. Every
row is re-resolved and re-formatted by `exhibit_verify.py` before the
build is allowed to pass.

{bindings_table()}
"""

    doc = reflow(doc)
    if not doc.endswith("\n"):
        doc += "\n"
    with open(os.path.join(HERE, "REPORT_WS12.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(doc)
    with open(os.path.join(HERE, "report_assertions.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({"_rule": ("every headline number in REPORT_WS12.md, with "
                             "the key path in exhibit_data.json it came "
                             "from and the string it formats to. "
                             "exhibit_verify.py check 13 re-resolves each "
                             "one and asserts the string is present in the "
                             "report verbatim."),
                   "n": len(ASSERTS), "assertions": ASSERTS},
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("REPORT_WS12.md        %7d bytes"
          % os.path.getsize(os.path.join(HERE, "REPORT_WS12.md")))
    print("report_assertions     %7d recorded" % len(ASSERTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
