#!/usr/bin/env python3
"""
Project Volt - WS8 - Task 0. Renders PRIOR_ART_WS8.md from the raw scan
output in data/prior_art_scan.json.

The scan was run as a bounded multi-lens sweep: commercial products and
programmes, patents, academic and technical literature, an adversarial
lens whose only job was to REFUTE the S3 premise, and a WHR + component
scaling lens. Each lens returned structured findings; this script merges
them into the claim map the assignment asks for - occupied ground, open
ground, and anything contradicting S3's premise - without editorialising
the underlying records.

    ../.venv/bin/python make_prior_art.py

EVIDENCE QUALITY, stated once here and repeated in the artifact: this
environment's egress policy denies direct HTTPS CONNECT to external
hosts. Patent databases, SAE, NREL, NACFE, UNECE and OEM sites all
return 403 at the gateway. Server-side web SEARCH does work, so the scan
was RUN rather than deferred - but no patent claim text and no primary
document was read verbatim. Everything below is a LEAD, flagged
provisional per the E13 precedent, and is not a freedom-to-operate
opinion.
"""
import json
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "data", "prior_art_scan.json")
SYNTHESIS = os.path.join(HERE, "data", "prior_art_claim_map.md")
OUT = os.path.join(HERE, "PRIOR_ART_WS8.md")

STRENGTH_ORDER = {"decisive": 0, "strong": 1, "suggestive": 2}

SKIP_ITEM_TABLES = [False]

L = []
w = L.append


def lens_key(lens):
    u = lens.upper()
    if u.startswith("PATENT"):
        return "patents"
    if u.startswith("COMMERCIAL"):
        return "products"
    if u.startswith("ADVERSARIAL"):
        return "adversarial"
    if "WHR" in u[:40] or "SCALING" in u[:60]:
        return "whr_scaling"
    return "academic"


LENS_TITLE = OrderedDict([
    ("products", "Commercial products and funded programmes"),
    ("patents", "Patents"),
    ("academic", "Academic and technical literature"),
    ("whr_scaling", "Waste-heat recovery and component scaling"),
    ("adversarial", "Adversarial lens (tasked to refute S3)"),
])


def main():
    lenses = json.load(open(SCAN))
    by_key = OrderedDict()
    for r in lenses:
        by_key.setdefault(lens_key(r["lens"]), []).append(r)

    w("# WS8 TASK 0 - PRIOR-ART CLAIM MAP")
    w("")
    w("Bounded prior-art scan for Vehicle One, covering P4 /"
      " through-the-road heavy-duty hybrids, e-axle overlay products, and"
      " any transmissionless or single-fixed-ratio ICE axle on a truck.")
    w("")
    w("**This file is generated** from `data/prior_art_scan.json` by"
      " `make_prior_art.py`. The JSON is the raw structured output of the"
      " sweep and is committed alongside it, so the claim map can be"
      " re-derived and audited against what the scan actually returned.")
    w("")
    w("## Evidence quality - read this first")
    w("")
    w("This environment's egress policy denies direct HTTPS CONNECT to"
      " external hosts. Patent full-text databases (`patents.google.com`,"
      " Espacenet, FreePatentsOnline, USPTO), `sae.org`, `nrel.gov`,"
      " `nacfe.org`, `unece.org` and OEM product pages all return 403 at"
      " the gateway - verified against the proxy's own status endpoint,"
      " not inferred from a failure.")
    w("")
    w("Server-side web **search** does work. So the scan was RUN rather"
      " than deferred, and it returned substantive, sourced, convergent"
      " results. But:")
    w("")
    w("- **no patent claim text was read verbatim.** Every claim"
      " description below is a paraphrase reconstructed from search-engine"
      " summaries.")
    w("- **no primary document was fetched.** Assignees, dates, figures"
      " and regulatory text are as reported by search summaries.")
    w("")
    w("Consequently this is a **lead list, flagged provisional per the E13"
      " precedent** - not a freedom-to-operate opinion and not a"
      " literature review of record. Any decision that turns on claim"
      " scope needs a re-run with database access, or outside counsel.")
    w("")
    w("**One lens exhausted the session's web-search budget** (200 of 200"
      " searches) before it could run, and returned recalled rather than"
      " searched content, flagging every item accordingly. Items from that"
      " lens marked `[RECALL/UNVERIFIED]` are **not** promoted into any"
      " WS8 artifact as a cited number. Its `[COMPUTED IN-SESSION]` items"
      " are arithmetic, independently reproducible, and are used only"
      " where WS8 re-derived them.")
    w("")
    w("Nothing in `REPORT_WS8.md` section 9 depends on this file. The S3"
      " verdict rests on the physics in Task 5; this scan corroborates it"
      " independently, which is worth something, but it does not carry it.")
    w("")
    w("### Each lens, in its own words")
    w("")
    w("Every lens was asked to state its own method and limits. Those"
      " statements are reproduced here unedited, because a scan's caveats"
      " are part of its result:")
    w("")
    for key, title in LENS_TITLE.items():
        for r in by_key.get(key, []):
            txt = r["lens"].replace("\n", "\n> ").strip()
            w(f"**{title}**")
            w("")
            w("> " + txt)
            w("")
    if os.path.exists(SYNTHESIS):
        w("---")
        w("")
        w("# PART A - CLAIM MAP")
        w("")
        w("What follows is the synthesis across all five lenses, carrying"
          " its own provenance classes. Part B below is the raw per-lens"
          " record it was built from, kept so that any statement here can"
          " be traced to the lens that made it.")
        w("")
        w(open(SYNTHESIS).read().rstrip())
        w("")
        w("---")
        w("")
        w("# PART B - RAW PER-LENS RECORD")
        w("")
        w("Contradictions and open-ground statements exactly as each lens"
          " returned them. The occupied-ground item tables are not"
          " repeated here - Part A covers them and"
          " `data/prior_art_scan.json` holds all 131 records in full, so"
          " reprinting them would add length without adding traceability.")
        w("")
        SKIP_ITEM_TABLES[0] = True
    w("---")
    w("")

    # ---------------- headline ----------------
    w("## 1. Headline")
    w("")
    w("Two findings recur across every lens that looked for them, and they"
      " point the same way:")
    w("")
    w("1. **S3's two constituent ideas are each thoroughly occupied - at"
      " different scales - and no record was found that occupies them"
      " JOINTLY at Class 8 scale.** \"Engine to wheels through a fixed"
      " ratio, electric machine owns launch and low speed\" is light-vehicle"
      " art going back to Severinsky/Paice (US5343970, filed 1992, now"
      " expired). \"Tandem split: engine on one rear axle, electric machine"
      " on the other\" is occupied at heavy-duty scale by BAE, Dana and the"
      " Hyliion through-the-road family. The junction of the two at 36 t is"
      " open ground.")
    w("")
    w("2. **The heavy-duty art teaches away from it, and the industry's own"
      " revealed preference is unanimous.** Across roughly 35 products and"
      " programmes on four continents over 30 years, the number of"
      " on-highway Class 8 vehicles in which a combustion engine drove the"
      " road wheels through a single fixed ratio with no gearbox anywhere"
      " is **zero**. Every parallel or overlay product kept the AMT"
      " untouched - that is the whole commercial proposition of a retrofit"
      " e-axle. Every product that DID delete the AMT did so by going"
      " series, decoupling the engine entirely, and then still fitted a"
      " two-, three- or five-speed gearbox on the traction side.")
    w("")
    w("Open ground and unanimous avoidance are not the same thing as an"
      " opportunity. The physics in `REPORT_WS8.md` section 6.2 says which"
      " one this is.")
    w("")
    w("---")
    w("")

    # ---------------- occupied ground ----------------
    if not SKIP_ITEM_TABLES[0]:
        w("## 2. Occupied ground")
        w("")
    for key, title in ([] if SKIP_ITEM_TABLES[0]
                       else LENS_TITLE.items()):
        rows = by_key.get(key)
        if not rows:
            continue
        items = [it for r in rows for it in r.get("items", [])]
        if not items:
            continue
        w(f"### 2.{list(LENS_TITLE).index(key) + 1} {title}")
        w("")
        w("| name | kind | architecture | quantified result | relevance to"
          " S3 |")
        w("|---|---|---|---|---|")
        for it in items:
            def clean(x, n=300):
                x = (x or "").replace("|", "/").replace("\n", " ").strip()
                return x[:n] + ("..." if len(x) > n else "")
            url = (it.get("url") or "").strip()
            name = clean(it.get("name"), 110)
            name = f"[{name}]({url})" if url.startswith("http") else name
            w(f"| {name} | {clean(it.get('kind'), 30)} | "
              f"{clean(it.get('architecture'), 90)} | "
              f"{clean(it.get('quantified_result'), 260)} | "
              f"{clean(it.get('relevance_to_S3'), 220)} |")
        w("")
    w("---")
    w("")

    # ---------------- contradictions ----------------
    w("## 3. Contradictions to the S3 premise")
    w("")
    w("The premise under test: *on a 36,300 kg GCW Class 8 combination,"
      " delete the gearbox entirely - axle A is the diesel through ONE"
      " fixed ratio with a rev-matched clutch, axle B is a disconnectable"
      " e-axle owning launch, low speed, regen and peak assist, and the"
      " engine is downsized toward cruise-plus-margin.*")
    w("")
    w("One lens was tasked only with refuting it. Findings are graded as"
      " the lens graded them, and the ones it could not substantiate are"
      " reported as dissolved rather than quietly dropped.")
    w("")
    cons = []
    for key, rows in by_key.items():
        for r in rows:
            for c in r.get("contradictions", []):
                cons.append((key, c))
    cons.sort(key=lambda kc: (STRENGTH_ORDER.get(
        (kc[1].get("strength") or "suggestive").lower().split()[0], 3),
        kc[0]))
    seen = set()
    for key, c in cons:
        claim = (c.get("claim") or "").replace("\n", " ").strip()
        sig = claim[:60].lower()
        if sig in seen:
            continue
        seen.add(sig)
        strength = (c.get("strength") or "suggestive").upper()
        w(f"**[{strength}] {claim}**")
        w("")
        ev = (c.get("evidence") or "").replace("\n", "  \n").strip()
        w(ev)
        w("")
        url = (c.get("url") or "").strip()
        if url:
            w(f"Source: {url}  ")
        w(f"Lens: {LENS_TITLE.get(key, key)}")
        w("")
    w("---")
    w("")

    # ---------------- open ground ----------------
    w("## 4. Open ground")
    w("")
    w("Stated as specific, falsifiable gaps. **Absence of evidence from a"
      " bounded, search-only scan is weak evidence of absence** - and in"
      " this case the same scan explains most of the absence, because the"
      " heavy-duty art teaches away from the ground that is open.")
    w("")
    for key, title in LENS_TITLE.items():
        rows = by_key.get(key)
        if not rows:
            continue
        og = [o for r in rows for o in r.get("open_ground", [])]
        if not og:
            continue
        w(f"**{title}**")
        w("")
        for o in og:
            w(f"- {o.strip()}")
        w("")
    w("---")
    w("")

    # ---------------- sources ----------------
    w("## 5. Sources")
    w("")
    srcs = []
    for rows in by_key.values():
        for r in rows:
            srcs.extend(r.get("sources", []))
    uniq = []
    for s in srcs:
        s = s.strip()
        if s and s not in uniq:
            uniq.append(s)
    for s in sorted(uniq):
        w(f"- {s}")
    w("")
    w(f"({len(uniq)} distinct sources across "
      f"{sum(len(v) for v in by_key.values())} lenses. All reached via"
      f" server-side search; none fetched directly.)")
    w("")

    with open(OUT, "w") as f:
        f.write("\n".join(L).rstrip() + "\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes)")


if __name__ == "__main__":
    main()
