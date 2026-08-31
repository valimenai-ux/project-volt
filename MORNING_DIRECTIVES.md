# MORNING_DIRECTIVES — 2026-08-31 (lead-issued; each section is one bounded order)

Read ../BASELINE_v6.md first. A worker executes ONE section, named in
its launch line, exactly as written; everything else is out of scope.
All rounds: deterministic, byte-stable, changelog generated not
written, R14 exports, escalations cite rulings, exit by launching
ws-adjudicator (Opus) on the folder, then stop. No commits — the
foreman commits, scoped to the workstream.

## SECTION WS8-R4 (WS8_semi_architecture, Opus)
1. B1: measure the throttle-back branch on the pack POWER ceiling as
   its own one-factor row; restate §15.2b; keep the branch only if it
   is physically justified (charging cannot exceed acceptance) and
   say so.
2. B2: `retard_overcommitment` = the sustained 60-second quantity the
   R14 rule string names (it is computed and discarded); relabel the
   governing case.
3. ESC-WS8-10 (physics): the retard envelope RE-SOLVES against buffer
   state and resistor ceiling on every sample; no simulated descent
   brakes harder than regen + resistor + friction can deliver; report
   which candidates' descent speeds and trip times move, with rows.
4. M1-M6 and minors per FINDINGS_WS8_r3.md. Verdicts are closed; the
   STOP trip-wire stays implemented.

## SECTION WS9-R2 (WS9_vehicle_one_wave2, Opus; after WS8-R4 lands)
1. Re-pin to WS8 r4 sources and re-run all corners x 8 seeds (the
   one-flag operation), inheriting the ESC-WS8-10 fix.
2. PRE-B1: rebuild the concordance module so every field is a two-
   sided comparison of independently computed values; no verdict
   literals; mutation-test it and commit the test.
3. PRE-B2: measure PEM on both S0R and S6 with fuel_g_genset actually
   populated; report the number, not the fallback.
4. PRE-B3: the heat ledger's climb rows select the governing branch of
   the D16 two-band envelope (engine-coupled where the engine can
   couple); re-export with the governing branch labeled.
5. R38 at every corner: export trip-time ratio vs S0R per candidate
   per corner, paired statistic labeled; do not apply the gate.
6. Materials/minors per FINDINGS_WS9_pre.md.

## SECTION KX-R4 (WS4_genset, Opus; lead-authorized round 4)
1. R3-B1: R20's radiator sizing case = the simulated R6 corner
   (103.522 kW two-minute maximum); re-evaluate
   `all_cases_within_capability` and the top-tank crossover honestly;
   reverse ESC-12's conclusion on the record if the data reverses it.
2. Re-certify the two sweep blocks whose "clean" certification was
   false; state what the sweep certification now means.
3. Materials/minors per FINDINGS_KX_r3.md.
4. Export the Vehicle Zero heat ledger of record for WS6 (R49).

## SECTION WS11-R3 (WS11_vehicle_zero_ruler, Opus; after its r2 adjudication)
1. R43(a): cold corner charges 2.2 kW cab heat; V1 fuel-fired
   auxiliary heater (fuel at 0.85) while the genset is off, waste-heat
   credit only while it runs; ruler and V2 as engine-carrying.
2. R43(b): warm-up / cold-start fuel model — coolant temperature as a
   state, enrichment penalty during warm-up, applied to ruler and both
   candidates; one-factor row for it.
3. R43(c): payload corners on WS8's `payload_kg()` convention.
4. R43(d): CdA 5.4 bracket exported alongside for both vehicles.
5. Re-run V1 (design duty VOLT-SUB) and V2 (record only; killed) at
   nominal and every corner; report V1 against the criterion with the
   combined-condition corner as the governing case. Findings of its r2
   adjudication folded in.
