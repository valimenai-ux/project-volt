# PROJECT VOLT — BASELINE v0 (ratified 2026-08-29)

Authoritative program baseline. Workstream sessions read this first and do
not relitigate it. Challenges go in the Escalations section of your report.

## Program intent
Transmissionless hybrid drivetrain for light/medium commercial trucks
(Koenigsegg Direct Drive logic adapted to delivery duty). Prototype and
science program. Economics out of scope. SI units.

## Vehicle Zero
- Isuzu NPR-HD, GVW 6,600 kg
- Tire 215/85R16, dynamic radius 0.37 m
- CdA 4.2 m^2, Crr 0.009
- Stock diesel reference (4HK1-TC): ~700 Nm @ 1,600 rpm, ~150 kW, idle ~700 rpm

## Locked architecture decisions
- No multi-ratio gearbox. Single fixed final drive 2.8:1 (geared for
  ~85 km/h at ~1,700 rpm engine speed).
- No hydraulic slip coupling. Clutch engagement is motor-synchronized
  (generator spins engine to synchronous speed, then lockup closes).
- Two variants on one shared electric spine:
  - V1 "Postal": pure series hybrid (genset + battery + traction motors).
    Engine never mechanically coupled to wheels. Downsized genset (~50 kW
    class, to be confirmed by WS1/WS4).
  - V2 "Trucker": series operation below ~60-70 km/h; lockup clutch into
    the 2.8:1 fixed drive for highway legs (i-MMD-style topology).
- Traction motor provisional spec: 13.5 kN tractive force 0-20 km/h
  (5,000 Nm at wheels via ~10:1 reduction), >=75 kW peak. Continuous
  rating TBD by WS1 -> WS2.
- V2 genset floor ~110 kW: must hold 60 km/h loaded on 6% grade with
  depleted battery.
- Series-path efficiency chain assumed ~83% (gen 94% x PE 97% x
  inverter+motor 92% x reduction 97%); direct mechanical path ~95%.

## Key derived numbers (Stage 1)
- 20% grade launch, full GVW: 13.5 kN = 5,000 Nm at wheels, ~75 kW corner power
- Cruise 85 km/h flat: ~2.0 kN, ~47 kW at wheels
- Diesel-only force through 2.8:1: ~5.0 kN max; zero below ~35 km/h
- Combined capability at 85 km/h: ~8 kN -> holds ~9-10% grade at speed

## Workstream map (dependency order)
1. WS1 Loads & duty cycles -> produces The Four Numbers
2. WS2 Traction motor / inverter / reduction (proposes DC bus voltage)
3. WS3 Battery pack (electrochemistry, C-rates, thermal, buffer sizing)
4. WS4 Genset (engine downsizing, generator, fixed BSFC operating point)
5. WS5 Controls (clutch sync, torque blending, regen blending, faults)
6. WS6 Packaging & integration on NPR-HD frame
7. WS7 Prototype & test plan
WS2-WS4 run in parallel after WS1 ratification. Project lead (main chat)
resolves interface conflicts and ratifies reports.

## Protocol
- Each workstream runs in its own session inside this folder, writes its
  outputs to its WS folder, and ends with a "REPORT WSn" markdown file.
- User pastes (or points the lead chat at) the report for ratification.
- Baseline updates only happen here, by version bump (v0 -> v1 ...).
