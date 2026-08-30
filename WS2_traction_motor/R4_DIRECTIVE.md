# WS2 ROUND 4 DIRECTIVE — RE-SPIN TO THE R10 BUS, CLOSE THE OPEN SURFACE

Lead-issued, bounded rework order. Read ../BASELINE_v2.md first (it
supersedes v1; rulings R10-R15 all touch this workstream), then your
own FINDINGS_WS2_r3.md. Your three delivered rounds were not wasted:
the methods, thermal models, trade studies and pipeline all carry —
this round re-derives the numbers at the ruled voltage and closes the
one unreviewed surface.

## Scope (exhaustive — nothing else)
1. R10: re-spin the spine to the pack-native window: nominal 662.4 V,
   operating 432.0-748.8 V, transients 777.6 V. Machine kV rewound for
   full R3 torque at 432.0 V; 1200 V-class SiC selection; resistor
   re-ohmed for 50 kW continuous at any point in the window (state the
   new transient ceiling per WS2-E5's logic); cables re-gauged;
   efficiency maps re-derived at 432 / 662 / 749 V and exported for
   WS4 (G1-R consumes them) and WS5.
2. R13: the 20% crawl is a continuous duty requirement. Cable and
   inverter continuous basis = crawl phase current at the new winding
   (expect ~x0.56 of the 455 Arms figure; compute it, don't inherit
   it). Spray build is mandatory; carry the G_ws >= 90 W/K
   verification requirement forward to WS7 in your interface. Remove
   all WS2-E1 conditioning from exported fields — the ruling has
   landed; fields are re-derived, not relabeled.
3. F11 + F12 closure at the new voltage: cable table, inverter
   continuous/10-min ratings, and the resistor's cable-limited ceiling
   all restated on the R14 discipline.
4. R14: every worst-case interface field = explicit max/min over an
   enumerated case set, governing case labeled inline. Rebuild your
   interface block to this rule.
5. R12: your maps are the traction chain of record (x0.97 reduction).
   Confirm no scalar PE member remains anywhere in your exports; all
   quantities bus-side per R12.
6. R15: resistor stays forced-air. Note the 8 kW pack-heater bus load
   in your ledger as a coexisting member (WS3 owns the heater; you own
   the resistor).
7. Spin drag: re-derive the PM lockup drag at the new winding
   (1,109 W @ 85 km/h was the 370 V machine) and export it as a named
   interface member — G1-R charges it to case (a).

## Exit
Regenerate everything deterministically; update REPORT_WS2.md with a
round-4 changelog; then launch the ws-adjudicator agent on this folder
(round 4) and STOP. The lead reviews the findings file directly. Do
not write a packet; the foreman run is over.
