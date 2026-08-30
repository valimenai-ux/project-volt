### T1 — Cycle summary

| | VOLT-SUB (V1 postal) | VOLT-REG (V2 trucker) |
|---|---|---|
| Duration | 3485 s | 6614 s |
| Distance | 19.82 km | 131.96 km |
| Average speed (incl. stops) | 20.5 km/h | 71.8 km/h |
| Average speed (moving) | 36.8 km/h | 78.1 km/h |
| Maximum speed | 50 km/h | 100 km/h |
| Stops | 30 | 17 |
| Stops per km | 1.51 | 0.13 |
| Stationary fraction | 44.3% | 8.0% |

### T2 — Wheel-power and energy metrics (GVW 6,600 kg)

| Quantity | VOLT-SUB | VOLT-REG |
|---|---|---|
| Peak wheel power | 67.4 kW | 163.7 kW |
| Average wheel power (tractive, over whole cycle) | 9.2 kW | 42.9 kW |
| Average wheel power (net of regen) | 5.5 kW | 40.4 kW |
| 95th-percentile wheel power (time-weighted, whole cycle) | 43.4 kW | 99.2 kW |
| 95th-percentile wheel power (moving time only) | 49.4 kW | 100.1 kW |
| 99th-percentile wheel power | 54.8 kW | 144.2 kW |
| RMS wheel power | 22.5 kW | 56.0 kW |
| Tractive energy | 8.92 kWh | 78.85 kWh |
| Energy per km (tractive, at the wheel) | 0.450 kWh/km | 0.598 kWh/km |
| Energy per km (net of ideal regen) | 0.268 kWh/km | 0.562 kWh/km |
| Total braking energy at the wheel | 3.61 kWh | 4.65 kWh |
| Braking energy per km | 0.182 kWh/km | 0.035 kWh/km |
| Braking energy as % of tractive | 40.5% | 5.9% |
| Peak regen power demanded at the wheel | 121.4 kW | 144.8 kW |
| Recoverable fraction @75 kW (at the wheel) | 91.9% | 91.0% |
| Recoverable fraction @75 kW (delivered to DC bus) | 79.5% | 78.8% |
| Regen energy recovered to the DC bus @75 kW | 2.87 kWh | 3.67 kWh |

### T3 — Regen absorb-limit sweep (% of total braking energy recovered)

| Absorb limit at the wheel | VOLT-SUB, at wheel | VOLT-SUB, to bus | VOLT-REG, at wheel | VOLT-REG, to bus |
|---|---|---|---|---|
| 0 kW | 0.0% | 0.0% | 0.0% | 0.0% |
| 20 kW | 36.5% | 31.6% | 43.4% | 37.5% |
| 40 kW | 64.9% | 56.2% | 68.3% | 59.1% |
| 50 kW | 75.4% | 65.3% | 77.0% | 66.7% |
| 60 kW | 83.5% | 72.3% | 83.8% | 72.6% |
| 75 kW | 91.9% | 79.5% | 91.0% | 78.8% |
| 90 kW | 96.3% | 83.3% | 95.5% | 82.7% |
| 100 kW | 97.6% | 84.5% | 97.3% | 84.3% |
| 125 kW | 98.3% | 85.1% | 99.1% | 85.8% |
| 150 kW | 98.3% | 85.1% | 99.3% | 85.9% |
| 200 kW | 98.3% | 85.1% | 99.3% | 85.9% |
| no limit | 98.3% | 85.1% | 99.3% | 85.9% |

### T4 — The Four Numbers

| | V1 Postal on VOLT-SUB (series) | V2 Trucker on VOLT-REG (i-MMD, lockup above 65 km/h) | V2 Trucker on VOLT-REG (forced series, clutch open) |
|---|---|---|---|
| **① Motor continuous** — cycle thermal-equivalent RMS at the motor shaft [kW] | 21.7 | 19.9 | 57.2 |
| 　same, if the machine had to absorb ALL braking (no 75 kW cap) [kW] | 22.6 | 20.8 | 57.5 |
| 　RMS *torque* at the motor shaft [Nm] | 115 | 71 | 106 |
| 　worst 300 s rolling RMS torque [Nm] | 145 | 149 | 174 |
| 　worst 60 s rolling RMS [kW] | 35.5 | 60.3 | 155.9 |
| 　worst 300 s rolling RMS [kW] | 26.6 | 34.5 | 124.8 |
| 　worst 600 s rolling RMS [kW] | 25.5 | 30.9 | 102.3 |
| **② Genset average** — constant SOC-neutral output at the DC bus [kW] | 10.1 | 9.7 | 50.6 |
| 　same, referred to engine shaft [kW] | 10.8 | 10.4 | 53.8 |
| 　plus average direct-path shaft power [kW] | 0.0 | 36.6 | 0.0 |
| 　**total average engine shaft power** [kW] | 10.8 | 47.0 | 53.8 |
| **③ Battery buffer** — max swing over rolling 5-min windows [kWh] | 0.71 | 1.29 | 7.32 |
| 　over the whole cycle (single genset setpoint) [kWh] | 1.13 | 3.40 | 20.80 |
| **④ Peak regen** — demanded at the wheel [kW] | 121.4 | 144.8 | 144.8 |
| 　actually absorbed with the 75 kW cap, at the DC bus [kW] | 64.9 | 64.9 | 64.9 |
| Peak motoring power at the motor shaft [kW] | 69.4 | 111.0 | 168.7 |
| Peak battery discharge [kW] | 71.9 | 120.3 | 144.8 |
| Peak battery charge [kW] | 70.8 | 70.5 | 110.1 |

### T5 — Battery buffer vs how often the genset setpoint may move

| Genset re-trim window | V1 on VOLT-SUB | V2 on VOLT-REG (i-MMD) | V2 on VOLT-REG (series only) |
|---|---|---|---|
| 1 min | 0.33 kWh | 0.96 kWh | 2.16 kWh |
| 2 min | 0.48 kWh | 1.04 kWh | 4.02 kWh |
| 5 min | 0.71 kWh | 1.29 kWh | 7.32 kWh |
| 10 min | 0.82 kWh | 1.46 kWh | 9.90 kWh |
| 20 min | 0.99 kWh | 1.80 kWh | 14.11 kWh |

### T6 — Payload sensitivity (±20% of the 2,900 kg payload at GVW)

**VOLT-SUB**

| Load case | Mass | E/km (wheel) | Peak wheel power | P95 | Braking energy | ① motor RMS | ② genset | ③ buffer 5 min | ④ peak regen |
|---|---|---|---|---|---|---|---|---|---|
| empty curb | 3700 kg | 0.297 kWh/km | 38.6 kW | 25.6 kW | 1.98 kWh | 13.3 kW | 7.6 kW | 0.53 kWh | 66.0 kW |
| payload -20pct | 6020 kg | 0.419 kWh/km | 61.6 kW | 39.8 kW | 3.29 kWh | 20.2 kW | 9.5 kW | 0.68 kWh | 110.3 kW |
| payload nominal GVW | 6600 kg | 0.450 kWh/km | 67.4 kW | 43.4 kW | 3.61 kWh | 21.7 kW | 10.1 kW | 0.71 kWh | 121.4 kW |
| payload +20pct | 7180 kg | 0.481 kWh/km | 73.1 kW | 46.9 kW | 3.94 kWh | 23.1 kW | 10.7 kW | 0.74 kWh | 132.5 kW |

**VOLT-REG**

| Load case | Mass | E/km (wheel) | Peak wheel power | P95 | Braking energy | ① motor RMS | ② genset | ③ buffer 5 min | ④ peak regen |
|---|---|---|---|---|---|---|---|---|---|
| empty curb | 3700 kg | 0.506 kWh/km | 111.6 kW | 77.2 kW | 1.91 kWh | 12.0 kW | 7.1 kW | 1.00 kWh | 69.1 kW |
| payload -20pct | 6020 kg | 0.578 kWh/km | 153.1 kW | 94.7 kW | 4.00 kWh | 18.2 kW | 9.0 kW | 1.23 kWh | 129.6 kW |
| payload nominal GVW | 6600 kg | 0.598 kWh/km | 163.7 kW | 99.2 kW | 4.65 kWh | 19.7 kW | 9.5 kW | 1.29 kWh | 144.8 kW |
| payload +20pct | 7180 kg | 0.617 kWh/km | 174.3 kW | 103.7 kW | 5.32 kWh | 21.3 kW | 10.1 kW | 1.53 kWh | 159.9 kW |

### T7 — Sustained 10 km climb at 6%, GVW

| Speed held | Wheel power | DC bus | Engine shaft (series) | Engine shaft (direct) | Engine crank rpm (locked) | Engine capability at that rpm |
|---|---|---|---|---|---|---|
| 40 km/h | 53.0 kW | 61.2 kW | 65.1 kW | 55.8 kW | 803 | 36.6 kW |
| 50 km/h | 68.7 kW | 79.4 kW | 84.4 kW | 72.3 kW | 1004 | 56.9 kW |
| 60 km/h | 86.0 kW | 99.3 kW | 105.7 kW | 90.5 kW | 1204 | 79.6 kW |
| 70 km/h | 105.2 kW | 121.6 kW | 129.3 kW | 110.8 kW | 1405 | 100.9 kW |
| 85 km/h | 138.5 kW | 160.0 kW | 170.2 kW | 145.8 kW | 1706 | 125.1 kW |
| 100 km/h | 177.9 kW | 205.5 kW | 218.6 kW | 187.2 kW | 2007 | 143.8 kW |

| Configuration | Settled speed on the 6% | Time for the 10 km | Buffer exhausted after |
|---|---|---|---|
| V2_buffer2kWh | 61.0 km/h | 555 s | 105 s |
| V2_buffer5kWh | 61.0 km/h | 463 s | 330 s |
| V2_battery_unlimited | 85.0 km/h | 438 s | — |
| V1_50kW_buffer2kWh | 30.2 km/h | 1132 s | 40 s |

### T8 — The same 10 km at −6% (descent), GVW

| Descent speed | Retardation demanded | Duration | Energy to dissipate |
|---|---|---|---|
| 25 km/h | 22.0 kW | 1440 s | 8.82 kWh |
| 35 km/h | 29.7 kW | 1029 s | 8.49 kWh |
| 40 km/h | 33.2 kW | 900 s | 8.29 kWh |
| 50 km/h | 39.0 kW | 720 s | 7.81 kWh |
| 60 km/h | 43.3 kW | 600 s | 7.21 kWh |
| 70 km/h | 45.6 kW | 514 s | 6.51 kWh |
| 85 km/h | 44.7 kW | 424 s | 5.25 kWh |
| 100 km/h | 37.5 kW | 360 s | 3.75 kWh |

Friction-brake energy and adiabatic rotor temperature rise (60 kg of iron), buffer starting at the supervisor's 55% SOC target and accessories drawing 2 kW throughout:

| Usable buffer | 60 km/h, no engine brake | 60 km/h, +10 kW engine drag | 60 km/h, +30 kW exhaust brake | 85 km/h, no engine brake | 85 km/h, +30 kW exhaust brake |
|---|---|---|---|---|---|
| 1 kWh | 6.29 kWh / 820 K | 4.62 kWh / 603 K | 1.29 kWh / 168 K | 4.45 kWh / 580 K | 0.92 kWh / 120 K |
| 2 kWh | 5.75 kWh / 751 K | 4.09 kWh / 533 K | 0.75 kWh / 98 K | 3.91 kWh / 510 K | 0.38 kWh / 50 K |
| 3 kWh | 5.22 kWh / 681 K | 3.55 kWh / 463 K | 0.22 kWh / 29 K | 3.37 kWh / 440 K | 0.00 kWh / 0 K |
| 4 kWh | 4.68 kWh / 611 K | 3.02 kWh / 393 K | 0.00 kWh / 0 K | 2.84 kWh / 370 K | 0.00 kWh / 0 K |
| 6 kWh | 3.61 kWh / 471 K | 1.94 kWh / 254 K | 0.00 kWh / 0 K | 1.77 kWh / 230 K | 0.00 kWh / 0 K |
| 8 kWh | 2.54 kWh / 331 K | 0.87 kWh / 114 K | 0.00 kWh / 0 K | 0.69 kWh / 91 K | 0.00 kWh / 0 K |

### T8b — Does the 2.8:1 direct path hold 6% at all? Engine-curve sensitivity

| Full-load torque curve | Torque @1,600 rpm | Peak power | Best grade held (alone) | at | Holds 6%? |
|---|---|---|---|---|---|
| WS1 baseline 4HK1 | 700 Nm | 153 kW | 5.25% | 70 km/h | no (short by 9.3 kW) |
| flat 700Nm from 1200 | 700 Nm | 153 kW | 5.81% | 60 km/h | no (short by 2.0 kW) |
| lowend rich 750Nm at 1400 | 700 Nm | 152 kW | 6.03% | 60 km/h | **yes**, 59–67 km/h |
| highrpm biased | 700 Nm | 163 kW | 4.98% | 74 km/h | no (short by 12.8 kW) |

### T9 — Baseline cross-checks

| Baseline statement | WS1 recomputation | Verdict |
|---|---|---|
| Cruise 85 km/h flat: ~2.0 kN, ~47 kW at the wheel | 1988 N, 46.9 kW | confirmed |
| 20% grade launch: 13.5 kN | 13272 N | confirmed (baseline rounds up) |
| Diesel-only force through 2.8:1: ~5.0 kN | 5032 N | confirmed |
| Diesel-only force zero below ~35 km/h | idle (700 rpm) = 34.9 km/h | confirmed |
| V2 genset floor ~110 kW to hold 60 km/h on 6% loaded | 107.8 kW engine shaft incl. accessories | confirmed |
| Combined ~8 kN at 85 km/h → holds 9–10% grade | 8.21 kN → 9.7% | confirmed, but only for 1.4 min on a 2 kWh buffer |
| Series-path efficiency ~83% | 0.8137 = 81.4% from the quoted components | **discrepancy** |

### T10 — Motor envelope demanded by the cycles (at the motor shaft, 10:1)

| | VOLT-SUB_V1 | VOLT-REG_V2_iMMD | VOLT-REG_V2_series_only |
|---|---|---|---|
| Max shaft speed | 3585 rpm | 7169 rpm | 7169 rpm |
| Max motoring torque | 353 Nm | 344 Nm | 344 Nm |
| Max braking torque | 370 Nm | 324 Nm | 324 Nm |
| RMS torque | 115 Nm | 71 Nm | 106 Nm |
| Max motoring power | 69.4 kW | 111.0 kW | 168.7 kW |
| Max braking power the machine sees (75 kW cap) | 72.8 kW | 72.8 kW | 72.8 kW |
| Max braking power demanded (uncapped) | 117.7 kW | 140.4 kW | 140.4 kW |

### T11 — Road-load coefficient sensitivity (CdA and air density)

| CdA / ρ | 85 km/h cruise | VOLT-SUB E/km | VOLT-REG E/km | VOLT-REG P95 | V2 6% hold speed |
|---|---|---|---|---|---|
| 4.2 m² / 1.2 kg/m³ | 46.9 kW | 0.450 kWh/km | 0.598 kWh/km | 99.2 kW | 61.0 km/h |
| 4.2 m² / 1.225 kg/m³ | 47.6 kW | 0.452 kWh/km | 0.605 kWh/km | 100.2 kW | 60.8 km/h |
| 4.8 m² / 1.2 kg/m³ | 51.7 kW | 0.464 kWh/km | 0.652 kWh/km | 106.0 kW | 60.1 km/h |
| 4.8 m² / 1.225 kg/m³ | 52.5 kW | 0.467 kWh/km | 0.661 kWh/km | 107.1 kW | 59.9 km/h |
| 5.4 m² / 1.2 kg/m³ | 56.4 kW | 0.479 kWh/km | 0.707 kWh/km | 112.8 kW | 59.2 km/h |
| 5.4 m² / 1.225 kg/m³ | 57.3 kW | 0.482 kWh/km | 0.717 kWh/km | 114.2 kW | 59.1 km/h |

### T12 — Cycle composition by speed band

| Band | VOLT-SUB time | VOLT-SUB distance | VOLT-REG time | VOLT-REG distance |
|---|---|---|---|---|
| stationary km/h | 47.9% | 0.4% | 9.3% | 0.0% |
| urban 5-50 km/h | 52.1% | 99.6% | 11.2% | 5.4% |
| rural 50-80 km/h | 0.0% | 0.0% | 25.3% | 24.7% |
| highway 80-100 km/h | 0.0% | 0.0% | 54.1% | 69.9% |


Baseline stall spec (13.5 kN at the wheel) = 515 Nm at the motor shaft.

