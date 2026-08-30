# PROJECT VOLT — BASELINE v3 (ratified 2026-08-30)

Supersedes BASELINE_v2.md. This version executes Gate G1's kill clause
and ratifies the WS2 round-4 and WS4 G1-R records. Rulings R1-R20 carry
forward except as amended.

## GATE G1: EXECUTED. THE CLUTCH IS DELETED.

The record: G1-R nominal ensemble-min -2.58% / median -2.50% / max
-2.37% against the armed >=5% criterion — missed by 7.58 points with
the sign reversed: the locked path trails pure series outright. One-
factor attribution: R12 map-vs-scalar swap -7.01 pp (WS1's scalar chain
understated the electric path by ~8 points once the phantom traction-
side PE stage was removed and WS2's measured maps replaced the
scalar+part-load treatment); spin-drag member -1.77 pp. Every condition
fails; CdA 5.4 is sole break-even (median +0.02%, 4 of 8 seeds
marginally positive per adjudication F1); the 2,000 m/+45 C corner is
now the WORST case (-5.90%) — R11's "still beats series by ~3.8% at
the corner" premise is contradicted on the record (ESC-6 accepted).
Verdict hardening accepted as decisive: float-identical legacy anchor
(6.26/6.45/6.78 reproduced to 1e-9 — the shift is the ruled
corrections, not drift), refuter could not refute, adjudicator
re-derived independently (interpolator rebuilt, 2e-16 agreement, all
4,203 map cells, per-seed ensembles, SHA-pinned WS2 r4 provenance),
vintage-insensitive (r3 maps -2.98), and the rectifier-accounting
bracket reaches at most +0.09% under the most hostile 3%-stacked
genset accounting. The kill outcome is invariant under every
accounting tested. WS2 r4 subsequently adjudicated clean, satisfying
the gate's input-provenance inheritance.

Killed with the clutch: the lockup device and actuator, clutch-sync
control, R11's condition-aware mode policy, fault spec F-1
(clutch-open limp — no clutch, no such fault), and the i-MMD topology
reference. The 6.26% of record from the first G1 pass is archived as
an artifact of the superseded chain convention.

What this is NOT: a failure of the program premise. The premise —
electric torque-fill replaces the gearbox — is now TOTAL rather than
partial. Both variants are pure series; the family tree runs through
the locomotive/Edison lineage, which was always the scaling story
toward semis. The Regera contribution that survives is the fixed-ratio
+ torque-fill logic below the (now nonexistent) coupling, i.e.
everywhere.

## Architecture of record after execution
- V1 "Postal": pure series, ~50 kW class genset (V3307-V1C class),
  sub-80 km/h (R5). Unchanged.
- V2 "Trucker": pure series at all speeds, genset per R18 (4HK1-V2C,
  132 kW flat-rating, corner-delivery >=122.1 kW; datasheet
  confirmation now a FREEZE-hold, not a start-hold — R24). Unchanged
  mechanicals otherwise: 10:1 total reduction retained as built
  (3.571:1 motor stage x 2.8:1 final). The 2.8:1's engine-sync
  rationale is void; the total ratio is a free parameter for future
  revisions but is NOT reopened now.
- Shared spine per WS2 r4: VM250-HV machine (x1.47 rewind, per-unit
  invariant), 1200 V SiC, R10 window 432.0-748.8 V nominal 662.4 V,
  resistor 3.73 ohm / 150.2 kW continuous ceiling (element-limited),
  cables 17.9 kg, spine rollup 230.8 kg.
- Pack per WS3 (unchanged, ratified): 288s1p LTO, 11.08 kWh usable.

## New rulings

R21 — WS2-E8 and WS2-E9 ACCEPTED as baseline amendments; the lead's
sketch is corrected on the record. Crawl continuous basis is
311.7 Arms (x0.685 — the x1.79 winding is infeasible: 515 Nm at the
432.0 V floor binds at ~21 km/h; the x1.47 rewind is voltage-exact at
the R13 band top and restores >=120 kW 1-min at every window voltage:
121/188/213 kW at floor/nominal/ceiling). R13's continuous-limit floor
is 80.1 W/K (was 75); G_ws >= 90 W/K WS7 verification unchanged;
LT-loop sizing member 10.57 kW. WS2-F13/F14 (minor case-set additions)
are DEFERRED-FOLD: mandatory at the next WS2 artifact touch, gating
nothing now. The R13 band-top corner is voltage-exact by construction:
any tolerance work on psi_m or Rs re-checks that corner first (WS7
note).

R22 — KILL CONSEQUENCE SET.
(a) ESC-5 is live: the R8 3.5 kWh V2 floor was sized for i-MMD duty;
pure-series VOLT-REG at that floor sheds unserved energy on hard
seeds. The delivered pack's 11.08 kWh usable covers WS1's 7.32 kWh
honest scale with margin — KX_DIRECTIVE.md orders the verification
run at the delivered pack (expect zero unserved energy; export
above-pin duty, SOC trajectories, genset cycling rate).
(b) V2 highway genset dispatch (pin vs two-point vs load-following on
the 4HK1-V2C map) is a WS5 design question consuming the KX exports.
(c) With no mechanical path, BOTH variants share the genset-or-pack-
fault = tow asymmetry; WS7 test plan carries it (R4's V1 note now
applies program-wide).
(d) PM spin drag at zero torque persists whenever coasting without
regen (motor permanently geared, 1,109 W @ 85 km/h); WS5 supervisor
prefers light regen over true coast. In driving operation the drag is
inside the measured maps.

R23 — ERRATA ORDER (in KX): WS4 adjudication F1 (CdA 5.4 positive-seed
count, four of eight, in all four locations) and F2-F5 corrected with
checker pins; no re-adjudication required beyond checker verification,
per the adjudicator's own "record-precision defects, not cracks"
characterization.

R24 — WS6 RELEASE AMENDED: the R18 datasheet item confirms a rating,
not a geometry; WS6 packaging proceeds at the declared ~500 kg
envelope with the flat-rating carried as a freeze-hold flag.

## Workstream states
WS1 CLOSED. WS2 CLOSED-RATIFIED (r4 clean; F13/F14 deferred-fold).
WS3 CLOSED-RATIFIED. WS4 RATIFIED; KX_DIRECTIVE.md open (errata +
pure-series verification + interface archive of gate_g1).
WS5 RELEASED — WS5_controls/ASSIGNMENT.md (dual-series supervisor).
WS6 RELEASED — WS6_packaging/ASSIGNMENT.md (heat ledger owner).
WS7 accumulating: coastdown (E13), adhesion (E23), crawl heat-run
(G_ws >= 90 W/K vs the 80.1 floor), ISO 3046-1 two-leg dyno
substantiation of the 132 kW flat-rating, program-wide fault-asymmetry
tests, R21 tolerance corner.

## Protocol
Unchanged (v2 additions carry: directives pattern, R14 export
discipline, pre-registration in the lead chat, 8-seed ensembles,
part-load everywhere, bus-side quantities, heat ledger to WS6).
