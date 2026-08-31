#!/usr/bin/env python3
"""WS13 publication verifier.

Asserts, and fails loudly on, everything the publication is not allowed to get
wrong:

  [1] every citation in `citations.json` re-resolves from its own source file
      and still renders the string the ledger records. A line citation whose
      line has moved is accepted only in a declared live source and only where
      the quote occurs on exactly one line; a vanished quote, an ambiguous one,
      or any movement in a frozen source is a hard failure;
  [2] every source file is byte-identical to the one the ledger was built
      against (sha256), so a citation cannot silently drift -- except for the
      sources listed in `_meta.live_sources` (the production log, which the
      foreman appends to while this publication is reviewed), where a hash
      change is reported as a warning and the binding check is [1];
  [3] every `[id]` marker in a publication file names a real citation;
  [4] the citation's rendered string appears in the prose within a bounded
      lookback window before its marker (LOOKBACK characters, about four lines)
      -- i.e. the number printed to the reader is the number on disk, not a
      number retyped near a footnote. Five display strings are shared by two
      citation ids each, so for those the window is tightened to
      LOOKBACK_SHARED, and the widest observed distance is printed on success
      so the slack cannot quietly grow;
  [5] every citation in the ledger is used at least once (the ledger is what
      the publication cites, not a superset);
  [6] guard rail 1: the method claim is stated as "catches internal
      inconsistency", never as "catches wrong physics", in every prose file
      (REPRODUCE.md included), and a short list of measurement-implying labels
      inherited from upstream ("measured map(s)", "measured inverter") may
      appear only inside quotation marks, i.e. quoted as an inherited label and
      never asserted in the publication's own voice. This check tests fixed
      strings; it cannot detect every measurement-implying phrasing;
  [7] guard rail 2: no status is promoted -- each of v7's eight claims is
      rendered with v7's own status text, v7's FROZEN- labels are present, and a
      blacklist of promoted phrasings is absent. This is a string test: it
      cannot detect promotion by framing, juxtaposition or omission, which
      remains a reader's judgement;
  [8] the two REPORT_WS11 facts the assignment names appear in FINDINGS.md and
      LIMITATIONS.md, each with its citation;
  [9] the README's exhibit link is the live page. Post-deploy invariant
      (CLOSEOUT section 7.5): the exhibit URL is present AND survives
      HTML-comment stripping, so it is text a reader actually sees; and the
      pre-deploy caveat is gone -- neither the pending sentence nor the
      PLACEHOLDER marker may reappear. Absence is asserted, not merely
      unchecked, so a stale caveat cannot silently return.

Run:  python3 WS13_publication/verify_ws13.py
Exit 0 = VERIFY OK.  Any failure exits 1 with the reason.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "WS13_publication")
LEDGER = os.path.join(HERE, "citations.json")

PUBLICATION = ["README.md", "METHOD.md", "FINDINGS.md", "LIMITATIONS.md", "REPRODUCE.md"]
# Guard rail 1 is swept over every publication file, REPRODUCE.md included.
PROSE = PUBLICATION

# How far back from a [id] marker the rendered value is allowed to sit. The
# general window is about four lines; where a display string is shared by more
# than one citation id the window is tightened, because there the check is also
# what distinguishes a marker attached to the right sibling from the wrong one.
LOOKBACK = 320
LOOKBACK_SHARED = 120

failures: list[str] = []
checks = 0
live_sources: set[str] = set()
line_moves: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(label + (("\n      " + detail) if detail else ""))


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def sha256(rel: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve(entry: dict) -> str:
    loc = entry["locator"]
    if loc["kind"] == "json":
        with open(os.path.join(ROOT, entry["source"]), encoding="utf-8") as fh:
            node = json.load(fh)
        for key in loc["path"]:
            node = node[key]
        fmt = loc["format"]
        if fmt == "!raw":
            return json.dumps(node)
        if fmt.startswith("!json:"):
            return fmt[len("!json:"):].format(json.dumps(node))
        return fmt.format(node)
    lines = read(entry["source"]).split("\n")
    line, quote, src = loc["line"], loc["quote"], entry["source"]
    if 1 <= line <= len(lines) and quote in lines[line - 1]:
        return quote
    # A declared live source may be written to mid-review. If the quote moved,
    # accept it only where it is UNAMBIGUOUS -- exactly one line carries it.
    hits = [i + 1 for i, text in enumerate(lines) if quote in text]
    if src in live_sources and len(hits) == 1:
        line_moves.append(f"{src}: a cited line moved {line} -> {hits[0]}")
        return quote
    if not hits:
        raise AssertionError(
            f"{src}:{line} no longer contains {quote!r}, and it is nowhere "
            f"else in the file")
    if len(hits) > 1:
        raise AssertionError(
            f"{src}:{line} moved and {quote!r} is now AMBIGUOUS (lines {hits})")
    raise AssertionError(
        f"{src}:{line} does not contain {quote!r}; it is at line {hits[0]}. "
        f"This source is not declared live, so it is not auto-repinned")


def main() -> int:
    with open(LEDGER, encoding="utf-8") as fh:
        ledger = json.load(fh)
    cites = ledger["citations"]

    live_sources.update(ledger["_meta"].get("live_sources", []))

    # ---------------------------------------------------------------- [2]
    live = set(ledger["_meta"].get("live_sources", []))
    warnings: list[str] = []
    for rel, want in ledger["source_sha256"].items():
        got = sha256(rel)
        if rel in live:
            # A live log is appended to while this publication is reviewed.
            # Appends do not move the lines cited here, and check [1] re-reads
            # every cited line and quote, so a hash change is advisory only.
            if got != want:
                warnings.append(
                    f"live source {rel} has changed since the ledger was built "
                    f"(ledger {want[:16]}... disk {got[:16]}...); its cited "
                    f"lines still resolve, checked in [1]")
            continue
        check(got == want, f"[2] source drifted: {rel}",
              f"ledger {want[:16]}... disk {got[:16]}...")

    # ---------------------------------------------------------------- [1]
    for cid, entry in cites.items():
        try:
            got = resolve(entry)
        except Exception as exc:                                # noqa: BLE001
            check(False, f"[1] {cid} did not resolve", str(exc))
            continue
        check(got == entry["display"],
              f"[1] {cid} renders differently now",
              f"ledger {entry['display']!r} disk {got!r}")

    # ---------------------------------------------------------------- [3][4]
    text = {rel: read(rel) for rel in PUBLICATION}
    marker = re.compile(r"\[([a-z0-9_]+)\]")
    used: dict[str, int] = {}

    # display strings carried by more than one citation id
    by_display: dict[str, list[str]] = {}
    for cid, entry in cites.items():
        by_display.setdefault(entry["display"], []).append(cid)
    shared = {d for d, ids in by_display.items() if len(ids) > 1}
    worst_gap = 0
    worst_gap_site = ""

    for rel, body in text.items():
        for m in marker.finditer(body):
            cid = m.group(1)
            if cid not in cites:
                # markdown link labels are [text](url); skip those
                if body[m.end():m.end() + 1] == "(":
                    continue
                # `[marker]` in backticks is prose ABOUT the notation, not a use
                # of it -- the publication's coverage claims say "carries a
                # `[marker]`" and that literal must not be read as an id.
                if (body[max(0, m.start() - 1):m.start()] == "`"
                        and body[m.end():m.end() + 1] == "`"):
                    continue
                check(False, f"[3] {rel}: marker [{cid}] is not a citation id")
                continue
            used[cid] = used.get(cid, 0) + 1
            display = cites[cid]["display"]
            limit = LOOKBACK_SHARED if display in shared else LOOKBACK
            window = body[max(0, m.start() - limit):m.start()]
            check(display in window,
                  f"[4] {rel}: [{cid}] is not preceded by its own value",
                  f"expected {display!r} within {limit} chars before the marker"
                  + (" (tightened: this display string is shared by "
                     f"{len(by_display[display])} citation ids, so proximity is "
                     "what identifies the right one)" if display in shared else ""))
            if display in window:
                gap = len(window) - window.rfind(display) - len(display)
                if gap > worst_gap:
                    worst_gap, worst_gap_site = gap, f"{rel}:[{cid}]"

    # ---------------------------------------------------------------- [5]
    unused = sorted(set(cites) - set(used))
    check(not unused, f"[5] {len(unused)} citations in the ledger are never cited",
          ", ".join(unused[:25]) + (" ..." if len(unused) > 25 else ""))

    # ---------------------------------------------------------------- [6]
    GUARD1 = ("catches internal inconsistency, never wrong physics")
    NOT_VALIDITY = "Consistency is not validity."
    for rel in PROSE:
        body = text[rel]
        check(GUARD1 in body, f"[6] {rel}: guard-rail sentence absent",
              f"expected the phrase {GUARD1!r}")
        check(NOT_VALIDITY in body, f"[6] {rel}: {NOT_VALIDITY!r} absent")
        # 'catches wrong physics' may appear ONLY inside the negation
        for m in re.finditer(re.escape("catches wrong physics"), body):
            pre = body[max(0, m.start() - 8):m.start()]
            check(pre.endswith('never "') or pre.endswith("never "),
                  f"[6] {rel}: 'catches wrong physics' used outside its negation",
                  f"preceded by {pre!r}")
        # Upstream calls WS2's efficiency maps "measured"; they are computed
        # from an analytic loss model and LIMITATIONS §1 says no measurement
        # exists in this program. The label may be QUOTED as inherited, never
        # asserted in the publication's own voice.
        # One regex, longest-match, so "measured maps" is not also flagged as a
        # bare "measured map" whose closing quote is one character further on.
        for m in re.finditer(r"measured (?:loss )?maps?\b|measured inverter\b",
                             body):
                quoted = (body[max(0, m.start() - 1):m.start()] == '"'
                          and body[m.end():m.end() + 1] == '"')
                check(quoted,
                      f"[6] {rel}: {m.group(0)!r} asserted rather than quoted",
                      "the maps are computed from an analytic loss model; if the "
                      "upstream label is used it must sit inside quotation marks "
                      "with the flag beside it")

    # ---------------------------------------------------------------- [7]
    findings = text["FINDINGS.md"]
    claim_ids = [f"v7_claim{i}" for i in range(1, 9)]
    status_ids = [f"v7_claim{i}_status" for i in range(1, 9)]
    for cid in claim_ids + status_ids:
        check(cites[cid]["display"] in findings,
              f"[7] FINDINGS.md does not carry {cid} verbatim from BASELINE_v7_FREEZE.md")

    PROMOTED = [
        "RATIFIED ADVANCE", "ratified ADVANCE", "FINAL ADVANCE", "final ADVANCE",
        "confirmed ADVANCE", "PROVEN", "validated against hardware",
        "measured on a real truck", "verified in hardware", "RATIFIED-FINAL",
        "no longer provisional", "promoted to ratified",
    ]
    for rel, body in text.items():
        for bad in PROMOTED:
            check(bad not in body, f"[7] {rel} contains a promoted-status phrase: {bad!r}")

    # v7's frozen labels must be the ones the publication uses for the verdicts
    for label in ["FROZEN-PROVISIONAL ADVANCE", "FROZEN-KILL", "FROZEN-PROVISIONAL"]:
        check(label in findings, f"[7] FINDINGS.md never uses the frozen label {label!r}")

    # ---------------------------------------------------------------- [8]
    for rel in ["FINDINGS.md", "LIMITATIONS.md"]:
        body = text[rel]
        check(cites["v1_cold_both"]["display"] in body,
              f"[8] {rel} omits V1's governing corner under ESC-2 + ESC-4 "
              f"({cites['v1_cold_both']['display']})")
        check(cites["v1_cold_no_credit"]["display"] in body,
              f"[8] {rel} omits the harshest cab-heat reading "
              f"({cites['v1_cold_no_credit']['display']})")
        check("WS11_vehicle_zero_ruler/REPORT_WS11.md" in body,
              f"[8] {rel} does not cite REPORT_WS11.md for those two facts")

    # ---------------------------------------------------------------- [9]
    # Post-deploy (CLOSEOUT section 7.5). The exhibit is live and verified
    # anonymously, so the invariant inverts: the URL must be there and visible,
    # and the pre-deploy caveat must be GONE. Both absences are asserted rather
    # than left unchecked, because a stale "this link is not live yet" caveat on
    # a public page is the same defect class as a stale number -- prose that the
    # record has moved past.
    EXHIBIT_URL = "https://valimenai-ux.github.io/project-volt/"
    PENDING_CAVEAT = "The exhibit link is pending."
    PLACEHOLDER_MARKER = "PLACEHOLDER"
    readme = text["README.md"]
    rendered = re.sub(r"<!--.*?-->", "", readme, flags=re.DOTALL)
    check(EXHIBIT_URL in readme,
          "[9] README.md does not carry the exhibit URL")
    check(EXHIBIT_URL in rendered,
          "[9] the exhibit URL exists only inside an HTML comment",
          "it must be text a reader actually sees, not a comment")
    check(PENDING_CAVEAT not in readme,
          "[9] README.md still carries the pre-deploy pending caveat",
          f"the exhibit is deployed; {PENDING_CAVEAT!r} must be removed")
    check(PLACEHOLDER_MARKER not in readme,
          "[9] README.md still carries the PLACEHOLDER marker",
          "it was the pre-deploy grep target and must not survive the §7.5 patch")

    # ---------------------------------------------------------------- report
    if failures:
        print(f"VERIFY FAILED — {len(failures)} of {checks} checks failed\n")
        for f in failures:
            print("  - " + f)
        return 1
    for w in warnings + sorted(set(line_moves)):
        print("  ! " + w)
    print(f"  widest value-to-marker gap: {worst_gap} chars at {worst_gap_site} "
          f"(limit {LOOKBACK}, {LOOKBACK_SHARED} for the "
          f"{len(shared)} shared display strings)")
    print(f"VERIFY OK — {checks} checks passed; "
          f"{len(cites)} citations, {sum(used.values())} markers, "
          f"{len(ledger['source_sha256']) - len(warnings)} source files unchanged"
          + (f", {len(warnings)} live source(s) advisory" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
