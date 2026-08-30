# PM_PACKET_WS2 — traction motor, inverter, reduction, brake resistor, DC bus

Foreman packet for lead ratification. Compiled 2026-08-29. All numbers
below are copied verbatim from WS2's own artifacts, cited to file and
line; the foreman adds no numbers of his own.

## Status: NOT CONVERGED (maximum 3 rounds used; final round not clean)

The workstream is stopped per the 3-round limit. The final state is NOT
a broken work product: round 3's adjudication found **no blocking
findings**, verified all round-2 findings genuinely resolved at root
cause, and confirmed the central DC-bus interface re-derives cleanly.
What prevents a READY status is one new **material** finding raised in
round 3 (WS2-F11) that was not reviewed post-fix, plus one new minor
(WS2-F12). The adjudicator judged both "localized, decision-neutral,
and carry their resolution paths" — but ruling on that is the lead's,
not the foreman's.

### Findings trail (full, all three rounds)

- r1 (WS2_traction_motor/FINDINGS_WS2_r1.md): 0 blocking, 2 material
  (F1 — the "+3 points favourable" part-load claim rested on a
  chain-definition mismatch, WS1's 0.97 PE stage silently deleted;
  F2 — coolant interface exported 4.66 kW, neither the S2 point nor
  the loop worst case), 5 minor (F3–F7). Bounced.
- r2 (WS2_traction_motor/FINDINGS_WS2_r2.md): all seven r1 findings
  verified genuinely resolved (F1's resolution called "exemplary");
  1 NEW material (F8 — the reworked `heat_worst_case_kW = 8.75`
  exported the milder V1-speed crawl member while the workstream's own
  V2-speed crawl rejects ~10.2 kW), 2 new minor (F9, F10). Bounced.
- r3 (WS2_traction_motor/FINDINGS_WS2_r3.md, final round): F8/F9/F10
  all verified genuinely resolved at root cause; 0 blocking; 1 NEW
  material (F11 — the cable table and inverter rating exclude the
  crawl's 455 Arms sustained phase current: motor run sized at
  299 Arms / 320 A ampacity, inverter published "500 A 10-min", while
  the 20% crawl draws 644 A_pk indefinitely; resolution path stated:
  size the run to 455 Arms (~+6.5 kg), restate the inverter continuous
  rating, or condition both members on WS2-E1 as the coolant field
  already is), 1 new minor (F12 — the "energy-unlimited" resistor
  claim is cable-limited above ~91 kW continuous at the window top).
- Mechanical verification (foreman, all three rounds): pipeline
  regenerates results.json + all 12 data CSVs byte-identical from the
  entry point every round; interface block parses and is byte-equal to
  `results.json → interface`; worker's check_report.py passes (77 →
  102 → 123 checks); independent prose-number audit clean each round.

### Pattern for the lead's attention (observation, not judgment)

Each round's rework genuinely fixed everything asked and each round's
fresh adjudication then found one new member-selection defect of the
same class in an adjacent export (r1-F2: wrong coolant member → r2-F8:
milder crawl member → r3-F11: cable/inverter duty case). The unreviewed
surface after round 3 is the F11/F12 fix, which does not yet exist.

## Headline numbers (verbatim from the report)

REPORT_WS2.md lines 16–23:

> **The headline (unchanged from round 1 — no finding touched it): DC bus
> nominal 370 V, operating window 300–435 V, full peak performance
> guaranteed down to 320 V, 750 V semiconductor class.**
> One IPM traction machine (530 Nm peak, 154 kW 1-min at 370 V), one 750 V
> SiC inverter, the provisional 10:1 reduction retained (as a 3.571:1 motor
> stage into the shared 2.8:1 final drive), and a 1.8 Ω forced-air brake
> resistor good for 50 kW continuously at any bus voltage and 105 kW at the
> window top.

Interface mass/coolant members as delivered in round 3 (results.json
`interface`, verified byte-equal to the report §9 block; foreman
mechanical check of 2026-08-29 20:50 PDT): `mass_kg.total_kg = 222.4`
(hv_cables 22.8), `coolant.heat_worst_case_kW = 10.22` (V2-speed crawl,
conditioned on WS2-E1), `heat_crawl_V1speed_kW = 8.75`,
`heat_at_S2_rating_kW = 4.9`. Note: r3 finding F11 questions the cable
member inside `mass_kg`; see trail above.

## ESCALATIONS (copied verbatim and complete, REPORT_WS2.md §10, lines 688–757)

* **WS2-E1** *(material; touches R3's crawl heritage, E9)* — The 20%
  crawl (510 Nm for minutes) is **only** closed by the oil-spray cooling:
  146 °C steady with spray vs thermal runaway (118 s / 346 m from warm)
  jacket-only. "Sustainable" is judged at the **165 °C continuous-life
  limit** (F5): the nominal 90 W/K build passes with 19 K margin,
  **75 W/K sits exactly on the limit (164.9 °C) — that is the
  continuous-limit floor of the design** — and 60 W/K fails even the
  180 °C hard limit (196.7 °C asymptote). R3's rating triple is met
  either way; what is at stake is WS1's §3.1 crawl *case*, which is not
  written into any ruling as a duty requirement. **Ask:** baseline text
  should state whether sustained 20% crawl is a requirement (then the
  spray build and a WS7 heat-run verification of G_ws ≥ 90 W/K are
  mandatory) or a 1-min launch case (then jacket-only is a legal
  descope). WS2 has built for the former. *(Round 3, F8:)* the exported
  LT-loop sizing heat — `heat_worst_case_kW = 10.22`, the V2-speed
  crawl member (§8) — is conditioned on this ruling: a descope to a
  1-min case changes the loop-sizing case entirely, and that field must
  then be **re-derived, not relabeled**.
* **WS2-E2** *(material; G1)* — PM lockup spin drag is real and now
  quantified: 1,109 W shaft at 85 km/h, 1.49 kWh engine-side +
  0.50 kWh bus-side per VOLT-REG cycle. **G1's case (a) must include
  it**; it is a structural tax on the direct path that pure series does
  not pay (the motor never spins unloaded in series). If G1's ≥5% margin
  turns out to sit within ~1.5% of the line, this number decides it.
  The induction alternative that would zero this drag loses the crawl
  case (2.4 kW rotor heat, +120 K) — trade recorded in §2.1, not
  recommended.
* **WS2-E3** *(minor; WS1 erratum)* — WS1 §3.1/E9's "510 Nm at
  300–700 rpm" contradicts its own crawl speeds: 10.6 / 23.6 km/h
  through 10:1 is 760 / 1,692 rpm. No thermal consequence
  (copper-dominated); the ratified text should be corrected.
* **WS2-E4** *(informational; R9/E22 — REFRAMED per F1)* — With real
  maps, **no additional part-load derate is needed for the
  machine+inverter member**: energy-weighted motoring lands +0.1 pt /
  +0.9 pt above WS1's like-for-like 0.92 scalar, and generating lands
  about a point below it (0.911 / 0.912). Round 1 called the correction
  "+3 points favourable"; that compared against WS1's 0.8924 chain,
  which embeds the PE stage WS2 does not model — retracted. WS1's
  provisional −7…−8.5% traction derate covered the full chain (PE and
  reduction included): the maps supersede **only its inverter+motor
  member**; the reduction keeps its declared 0.97 and WS1's treatment of
  that member; the PE member goes to WS2-E7. The genset-side +17–22%
  correction (R9) is unaffected.
* **WS2-E5** *(informational; R2)* — The chopper/resistor as designed
  gives 105 kW transient absorb at the window top (ribbon ~478 °C at
  the 2,000 m corner, still compliant — §5). Recommend WS5 use it as
  the second stage of R2's blending order above the pack's charge
  limit, which softens E10's 86–123 kW friction-blend steps on hard
  stops at high SOC. No ruling change needed — R2 already orders
  regen → resistor → friction.
* **WS2-E6** *(minor; R4/E24)* — A single machine and single inverter
  were selected (§2.1); V1's no-mechanical-path fault asymmetry is
  unchanged and stays with WS7 per R4. Recorded so nobody reads
  redundancy into the spine that is not there.
* **WS2-E7** *(material, NEW in round 2; touches R9's heat-ledger
  ownership and Gate G1; raised per F1)* — WS1's operative shaft↔bus
  chain 0.8924 = **PE 0.97 × inverter+motor 0.92**, and its grade-hold
  ledger books a discrete **3.0 kW "power electronics" member** on the
  traction side of the bus. WS2's spine has no such stage: the SiC
  inverter is the only conversion between bus and machine and its loss
  is inside the maps. **Ask (one line): rule where WS1's 0.97 PE stage
  lives.** (a) If it is WS4's rectifier/DC-DC, it moves to the genset
  side — and WS1's 0.866 bus-to-wheel chain, its 90.5 kW grade-hold
  shaft point, and the 20.2 kW ledger seed need re-derivation on the
  record. (b) If it is a real traction-side allocation (EMI filter,
  contactors, distribution), WS2 must carry ~0.97 explicitly and every
  map efficiency quoted here drops by that factor at the bus. Until
  ruled, G1 and WS3 must hold ONE convention on both sides of any
  comparison — §7 quantifies the +2.1% / -1.0% swing a silent mix
  injects, which is more than half of G1's 5% kill criterion.

## CROSS-WS OBSERVATIONS (stated as observations only; the lead rules)

Same set as the WS3/WS4 packets, from WS2's side:

1. **DC bus voltage windows barely overlap.** WS2 (this packet):
   operating 300–435 V, nominal 370 V, 750 V device class, with a
   declared interface hold point that WS3 commit a string inside the
   window before WS4 freezes rectifier design. WS3: operating
   432.0–748.8 V, nominal 662.4 V, with its T12 table pricing WS2
   electronics floors (532.8 V floor ⇒ full 120 kW only from +9 °C).
   Overlap as exported: 432.0–435 V. Each side quantifies the cost of
   the other's class in its own report.
2. **Brake-resistor cooling medium conflict.** WS3's interface requests
   the R2 resistor be mounted on the pack coolant circuit as the
   preconditioning heat source; WS2's delivered resistor is forced-air,
   "deliberately not coolant". Incompatible as delivered.
3. **Chain-convention rulings pending, both feeding G1.** WS2-E7 (PE
   stage ownership) and WS3's ES-4 (bus-side restatement of R8 peaks)
   ask the lead to pin the same class of convention. WS2-E2 separately
   asks that G1 case (a) be charged the PM lockup spin drag; WS4's
   delivered G1 margins (6.26% nominal min) were computed in WS4's own
   part-load models — whether they already include these two WS2 items
   is an integration check for the lead at ratification.
4. **Heat-ledger members at the hot corner** (for WS6, once released):
   WS2 LT-loop worst case 10.22 kW (V2-speed crawl, conditioned on
   WS2-E1) with 12 L/min ≤65 °C request; WS3 pack loop 1.41 kW at
   8 L/min; WS4 radiator package 95.0 kW at the R6 corner in 45 °C air
   plus 17.9 kW electrical chain. Stated as the set only; no
   aggregation by the foreman.

## Paths

- Report: WS2_traction_motor/REPORT_WS2.md
- Data of record: WS2_traction_motor/results.json
- Findings: WS2_traction_motor/FINDINGS_WS2_r1.md, FINDINGS_WS2_r2.md,
  FINDINGS_WS2_r3.md
- Downstream data files: WS2_traction_motor/data/ (efficiency maps at
  300/370/435 V for WS4/WS5, heat_ledger_ws2.csv, traction envelope,
  regen adhesion curves)
