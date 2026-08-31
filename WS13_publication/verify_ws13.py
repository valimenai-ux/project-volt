#!/usr/bin/env python3
"""WS13 publication verifier.

Asserts, and fails loudly on, everything the publication is not allowed to get
wrong:

  [1] every citation in `citations.json` re-resolves from its own source file
      and still renders the string the ledger records;
  [2] every source file is byte-identical to the one the ledger was built
      against (sha256), so a citation cannot silently drift -- except for the
      sources listed in `_meta.live_sources` (the production log, which the
      foreman appends to while this publication is reviewed), where a hash
      change is reported as a warning and the binding check is [1];
  [3] every `[id]` marker in a publication file names a real citation;
  [4] the citation's rendered string appears in the prose immediately before
      its marker -- i.e. the number printed to the reader is the number on
      disk, not a number retyped near a footnote;
  [5] every citation in the ledger is used at least once (the ledger is what
      the publication cites, not a superset);
  [6] guard rail 1: the method claim is stated as "catches internal
      inconsistency", never as "catches wrong physics", in every prose file;
  [7] guard rail 2: no status is promoted -- each of v7's eight claims is
      rendered with v7's own status text, and a list of promoted phrasings is
      absent;
  [8] the two REPORT_WS11 facts the assignment names appear in FINDINGS.md and
      LIMITATIONS.md, each with its citation;
  [9] the README's exhibit link is marked as a placeholder until the Pages
      deploy fills it in -- both as the machine-readable HTML comment the
      foreman greps for and as render-visible text a reader actually sees.

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
PROSE = ["README.md", "METHOD.md", "FINDINGS.md", "LIMITATIONS.md"]

# how far back from a [id] marker the rendered value is allowed to sit
LOOKBACK = 320

failures: list[str] = []
checks = 0


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
    text = lines[loc["line"] - 1]
    if loc["quote"] not in text:
        raise AssertionError(
            f'{entry["source"]}:{loc["line"]} no longer contains {loc["quote"]!r}; '
            f'line reads {text!r}')
    return loc["quote"]


def main() -> int:
    with open(LEDGER, encoding="utf-8") as fh:
        ledger = json.load(fh)
    cites = ledger["citations"]

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

    for rel, body in text.items():
        for m in marker.finditer(body):
            cid = m.group(1)
            if cid not in cites:
                # markdown link labels are [text](url); skip those
                if body[m.end():m.end() + 1] == "(":
                    continue
                check(False, f"[3] {rel}: marker [{cid}] is not a citation id")
                continue
            used[cid] = used.get(cid, 0) + 1
            window = body[max(0, m.start() - LOOKBACK):m.start()]
            check(cites[cid]["display"] in window,
                  f"[4] {rel}: [{cid}] is not preceded by its own value",
                  f"expected {cites[cid]['display']!r} within {LOOKBACK} chars before the marker")

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
    readme = text["README.md"]
    check("PLACEHOLDER" in readme,
          "[9] README.md does not mark the exhibit link as a placeholder "
          "(the machine-readable marker the foreman greps for in close-out §7)")
    check("https://valimenai-ux.github.io/project-volt/" in readme,
          "[9] README.md does not carry the exhibit's target URL")
    # The HTML comment above is invisible in rendered markdown, so the caveat
    # must ALSO exist as rendered text: between the repository going public and
    # the deploy being verified, a reader would otherwise see an apparently
    # live link with no visible qualification. Strip comments, then require it.
    VISIBLE_CAVEAT = "The exhibit link is pending."
    rendered = re.sub(r"<!--.*?-->", "", readme, flags=re.DOTALL)
    check(VISIBLE_CAVEAT in rendered,
          "[9] README.md's exhibit caveat is not render-visible",
          f"expected {VISIBLE_CAVEAT!r} outside any HTML comment")
    check("https://valimenai-ux.github.io/project-volt/" in rendered,
          "[9] the exhibit URL exists only inside an HTML comment")

    # ---------------------------------------------------------------- report
    if failures:
        print(f"VERIFY FAILED — {len(failures)} of {checks} checks failed\n")
        for f in failures:
            print("  - " + f)
        return 1
    for w in warnings:
        print("  ! " + w)
    print(f"VERIFY OK — {checks} checks passed; "
          f"{len(cites)} citations, {sum(used.values())} markers, "
          f"{len(ledger['source_sha256']) - len(warnings)} source files unchanged"
          + (f", {len(warnings)} live source(s) advisory" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
