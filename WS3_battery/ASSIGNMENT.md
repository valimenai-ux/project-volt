# WS3 ASSIGNMENT — BATTERY PACK

You are the pack engineer and electrochemist on Project Volt. You report
to the project lead (a separate chat). Read, in order: ../BASELINE_v1.md
(authoritative — note rulings R2, R7, R8, R9), then
../WS1_loads_duty_cycles/REPORT_WS1.md §4.6, §4.10, §4.15, E6, E7, E8,
E10, and ../WS1_loads_duty_cycles/results.json. WS2 is proposing the DC
bus voltage in parallel; treat voltage as a window (state your preferred
range and cell-count granularity — the lead reconciles). Runnable code,
everything saved here, finish with REPORT_WS3.md.

## Requirements (from BASELINE v1)
- POWER FIRST (R8): transient 120 kW discharge / 110 kW charge, PLUS
  50 kW CONTINUOUS charge for a full 24-minute descent (R2 blending
  puts battery ahead of the resistor in the regen order).
- Usable buffer floors: V2 >=3.5 kWh, V1 >=1.5 kWh at the bus, built as
  the SUM of genset hysteresis + regen headroom + grade reserve + SOC
  end-stops (E7 superposition; the 12.7 kWh descent line is deleted by
  R2).
- Environmental envelope R7: -10 to +45 C, 0-2,000 m. Cold case is a
  DESIGN case: define the preconditioning strategy and the regen-
  acceptance curve vs temperature (WS1 §4.15: a cold pack sends all
  3.61 kWh of VOLT-SUB braking to friction and lifts V1 genset average
  +48%).
- Part-load / temperature-dependent efficiency and resistance models,
  not scalars (R9). Report heat by case to the WS6 ledger.

## Tasks
1. Chemistry trade for a power-dominant duty: LTO vs high-power LFP vs
   high-power NMC vs hybrid (cells + supercap). Criteria: C-rate at
   -10 C and +45 C, cycle life under shallow high-rate cycling (genset
   hysteresis + regen chop, ~10^5-10^6 shallow cycles/year), calendar
   life at +45 C, thermal runaway class, mass, volume.
2. Size packs for V1 and V2 on the shared spine: cell, series/parallel
   count, nameplate vs usable window, SOC strategy (the 55% target from
   WS1 §4.6 is a starting point).
3. Thermal system: continuous 50 kW charge during descent at +45 C is
   the sizing case; show pack temperature trajectory over the WS1 §4.6
   descent table. Preconditioning below 0 C: energy source, time, and
   what the truck may not do until warm.
4. C-rate reality check vs E8: state the actual C-rates of your sized
   packs at the R8 peaks; if you conclude the pack must grow beyond the
   buffer floors, show the power-vs-energy frontier that forces it.
5. Sensitivity: buffer floor x1.5, envelope corners, one cell size up
   and down.

## Report
REPORT_WS3.md: Assumptions; Chemistry trade; Pack designs (V1, V2);
Thermal and cold strategy; Interfaces (machine-readable: voltage window
preference, cell count granularity, mass, volume, coolant needs,
heat-to-ledger, regen-acceptance curve file); Escalations (cite
R1-R9/G1); first-principles sanity checks.
