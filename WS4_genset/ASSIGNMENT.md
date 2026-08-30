# WS4 ASSIGNMENT — GENSET + GATE G1

You are the engine and generator engineer on Project Volt. You report to
the project lead (a separate chat). Read, in order: ../BASELINE_v1.md
(authoritative — note rulings R5, R6, R9 and GATE G1), then
../WS1_loads_duty_cycles/REPORT_WS1.md §4.12-§4.14, E3, E5, E6, E13,
E15, E19, E20, and ../WS1_loads_duty_cycles/results.json. Runnable code,
everything saved here, finish with REPORT_WS4.md.

## Requirements (from BASELINE v1)
- V2 genset floor: 125 kW continuous shaft, rating basis = deliver
  122.1 kW at +20% payload, 4 kW accessories, CdA 5.4, +45 C, 2,000 m
  (R6). State your candidate's derated output at exactly that corner.
- V1 genset: ~50 kW shaft class, start-stop operation per E6 (duty
  average 10.1 kW); 50-60 kW acceptable if a candidate lands there (R5).
  V1 is a sub-80 km/h vehicle by ruling — do not chase 85 km/h.
- Part-load models mandatory (R9). E5 stands: 81.4% series chain is an
  upper bound; carry WS1's part-load corrections.
- Report all cooling loads to the WS6 heat ledger, including the
  electrical-chain heat at the V2 grade hold (20.2 kW) plus your
  generator and engine rejection.

## Tasks
1. Candidate engines for both variants (production engines preferred for
   prototyping: state displacement, rated/continuous power, mass, and
   the derate math to the R6 corner). Include at least one downsized-
   from-stock option for V2 and one ~50 kW class for V1.
2. Generator selection/spec for each (type, continuous rating, its own
   efficiency map).
3. Obtain or construct a credible BSFC map for the 4HK1-class reference
   AND your V2 candidate (measured maps if findable; otherwise a
   physically-argued Willans-line construction, clearly labeled).
   Publish the maps as data files.
4. Fixed operating point(s) for series operation: place them on the map,
   show BSFC there vs the map minimum, and the start-stop hysteresis
   implications for V1 (starts per shift vs buffer, with WS3's floors).
5. GATE G1 (joint with a WS5 preview you will simulate yourself):
   net energy over VOLT-REG for
   (a) locked path WITH charge-bias load-point shifting on your BSFC
       map — the supervisor may load the engine above road load and
       bank the surplus; rpm stays welded to road speed;
   (b) pure series at the pinned best-BSFC point;
   both with part-load derates everywhere, 8-seed ensemble (R9).
   Report the margin against the >=5% kill criterion. If (a) loses,
   say so plainly — G1 exists to kill V2's clutch honestly, not to
   defend it.
6. Sensitivities: CdA 4.2 vs 5.4 (E13, carry ~5% margin), altitude
   derate at 2,000 m, hot day, accessory 2 vs 4 kW.

## Report
REPORT_WS4.md: Assumptions; Candidates and selection; BSFC maps and
operating points; GATE G1 result (the headline — state the margin and
your recommendation); Start-stop analysis; Interfaces (machine-readable:
shaft power at the R6 corner, mass, volume, coolant loads to ledger,
map file paths, generator spec); Escalations (cite R1-R9/G1);
first-principles sanity checks.
