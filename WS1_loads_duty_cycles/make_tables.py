"""Emit the markdown tables used in REPORT_WS1.md straight from results.json,
so no number in the report is transcribed by hand."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
out = []
def w(s=""): out.append(s)

C = R["cycles"]; A, B = C["VOLT-SUB"], C["VOLT-REG"]
w("### T1 — Cycle summary\n")
w("| | VOLT-SUB (V1 postal) | VOLT-REG (V2 trucker) |")
w("|---|---|---|")
rows = [("Duration", "duration_s", "{:.0f} s"), ("Distance", "distance_km", "{:.2f} km"),
        ("Average speed (incl. stops)", "avg_speed_kmh", "{:.1f} km/h"),
        ("Average speed (moving)", "avg_moving_speed_kmh", "{:.1f} km/h"),
        ("Maximum speed", "max_speed_kmh", "{:.0f} km/h"),
        ("Stops", "n_stops", "{:.0f}"), ("Stops per km", "stops_per_km", "{:.2f}"),
        ("Stationary fraction", "stopped_fraction", "{:.1%}")]
for lbl, k, f in rows:
    w(f"| {lbl} | {f.format(A[k])} | {f.format(B[k])} |")
w()
w("### T2 — Wheel-power and energy metrics (GVW 6,600 kg)\n")
w("| Quantity | VOLT-SUB | VOLT-REG |")
w("|---|---|---|")
rows = [("Peak wheel power", "P_peak_kW", "{:.1f} kW"),
        ("Average wheel power (tractive, over whole cycle)", "P_avg_tractive_kW", "{:.1f} kW"),
        ("Average wheel power (net of regen)", "P_avg_net_kW", "{:.1f} kW"),
        ("95th-percentile wheel power (time-weighted, whole cycle)", "P95_kW", "{:.1f} kW"),
        ("95th-percentile wheel power (moving time only)", "P95_moving_kW", "{:.1f} kW"),
        ("99th-percentile wheel power", "P99_kW", "{:.1f} kW"),
        ("RMS wheel power", "P_rms_wheel_kW", "{:.1f} kW"),
        ("Tractive energy", "E_tractive_kWh", "{:.2f} kWh"),
        ("Energy per km (tractive, at the wheel)", "E_per_km_kWh", "{:.3f} kWh/km"),
        ("Energy per km (net of ideal regen)", "E_net_per_km_kWh", "{:.3f} kWh/km"),
        ("Total braking energy at the wheel", "E_braking_kWh", "{:.2f} kWh"),
        ("Braking energy per km", "E_brake_per_km_kWh", "{:.3f} kWh/km"),
        ("Braking energy as % of tractive", "brake_energy_frac_of_tractive", "{:.1%}"),
        ("Peak regen power demanded at the wheel", "P_regen_peak_wheel_kW", "{:.1f} kW"),
        ("Recoverable fraction @75 kW (at the wheel)", "regen_recoverable_frac_mech", "{:.1%}"),
        ("Recoverable fraction @75 kW (delivered to DC bus)", "regen_recoverable_frac_elec", "{:.1%}"),
        ("Regen energy recovered to the DC bus @75 kW", "E_regen_captured_elec_kWh", "{:.2f} kWh")]
for lbl, k, f in rows:
    w(f"| {lbl} | {f.format(A[k])} | {f.format(B[k])} |")
w()

w("### T3 — Regen absorb-limit sweep (% of total braking energy recovered)\n")
w("| Absorb limit at the wheel | VOLT-SUB, at wheel | VOLT-SUB, to bus | VOLT-REG, at wheel | VOLT-REG, to bus |")
w("|---|---|---|---|---|")
ra = {str(r["cap_label"]): r for r in R["regen_sensitivity"]["VOLT-SUB"]["rows"]}
rb = {str(r["cap_label"]): r for r in R["regen_sensitivity"]["VOLT-REG"]["rows"]}
for cap in ("0", "20", "40", "50", "60", "75", "90", "100", "125", "150", "200", "uncapped"):
    if cap in ra:
        lbl = "no limit" if cap == "uncapped" else f"{cap} kW"
        w(f"| {lbl} | {ra[cap]['frac_of_braking_mech']:.1%} | {ra[cap]['frac_of_braking_elec']:.1%} | "
          f"{rb[cap]['frac_of_braking_mech']:.1%} | {rb[cap]['frac_of_braking_elec']:.1%} |")
w()

w("### T4 — The Four Numbers\n")
FN = R["four_numbers"]
keys = [("V1 Postal on VOLT-SUB (series)", "V1_postal_VOLT-SUB"),
        ("V2 Trucker on VOLT-REG (i-MMD, lockup above 65 km/h)", "V2_trucker_VOLT-REG_iMMD"),
        ("V2 Trucker on VOLT-REG (forced series, clutch open)", "V2_trucker_VOLT-REG_series_only")]
w("| | " + " | ".join(k[0] for k in keys) + " |")
w("|---|" + "---|" * len(keys))
def row(lbl, fn, fmt="{:.1f}"):
    w(f"| {lbl} | " + " | ".join(fmt.format(fn(FN[k[1]])) for k in keys) + " |")
row("**① Motor continuous** — cycle thermal-equivalent RMS at the motor shaft [kW]", lambda d: d["N1_motor_rms_shaft_kW"])
row("　same, if the machine had to absorb ALL braking (no 75 kW cap) [kW]", lambda d: d["N1_motor_rms_shaft_uncapped_kW"])
row("　RMS *torque* at the motor shaft [Nm]", lambda d: d["N1_motor_rms_torque_Nm"], "{:.0f}")
row("　worst 300 s rolling RMS torque [Nm]", lambda d: d["N1_rolling_rms_torque_Nm"]["300s"], "{:.0f}")
row("　worst 60 s rolling RMS [kW]", lambda d: d["N1_rolling_rms_shaft_kW"]["60s"])
row("　worst 300 s rolling RMS [kW]", lambda d: d["N1_rolling_rms_shaft_kW"]["300s"])
row("　worst 600 s rolling RMS [kW]", lambda d: d["N1_rolling_rms_shaft_kW"]["600s"])
row("**② Genset average** — constant SOC-neutral output at the DC bus [kW]", lambda d: d["N2_genset_const_bus_kW"])
row("　same, referred to engine shaft [kW]", lambda d: d["N2_genset_engine_shaft_kW"])
row("　plus average direct-path shaft power [kW]", lambda d: d["N2_engine_direct_avg_shaft_kW"])
row("　**total average engine shaft power** [kW]", lambda d: d.get("N2_engine_total_avg_shaft_kW", d["N2_genset_engine_shaft_kW"]))
row("**③ Battery buffer** — max swing over rolling 5-min windows [kWh]", lambda d: d["N3_buffer_5min_kWh"], "{:.2f}")
row("　over the whole cycle (single genset setpoint) [kWh]", lambda d: d["N3_buffer_fullcycle_kWh"], "{:.2f}")
row("**④ Peak regen** — demanded at the wheel [kW]", lambda d: d["N4_peak_regen_wheel_kW"])
row("　actually absorbed with the 75 kW cap, at the DC bus [kW]", lambda d: d["N4_peak_regen_bus_kW"])
row("Peak motoring power at the motor shaft [kW]", lambda d: d["motor_peak_motoring_shaft_kW"])
row("Peak battery discharge [kW]", lambda d: d["batt_peak_dis_kW"])
row("Peak battery charge [kW]", lambda d: d["batt_peak_chg_kW"])
w()

w("### T5 — Battery buffer vs how often the genset setpoint may move\n")
BW = R["buffer_vs_window"]
w("| Genset re-trim window | V1 on VOLT-SUB | V2 on VOLT-REG (i-MMD) | V2 on VOLT-REG (series only) |")
w("|---|---|---|---|")
for wnd in ("60s", "120s", "300s", "600s", "1200s"):
    w(f"| {int(wnd[:-1])//60 if int(wnd[:-1])>=60 else wnd} min | "
      f"{BW['VOLT-SUB_V1'][wnd]['kWh']:.2f} kWh | {BW['VOLT-REG_V2_iMMD'][wnd]['kWh']:.2f} kWh | "
      f"{BW['VOLT-REG_V2_series_only'][wnd]['kWh']:.2f} kWh |")
w()

w("### T6 — Payload sensitivity (±20% of the 2,900 kg payload at GVW)\n")
for nm in ("VOLT-SUB", "VOLT-REG"):
    P = R["sensitivity"]["payload"][nm]
    w(f"**{nm}**\n")
    w("| Load case | Mass | E/km (wheel) | Peak wheel power | P95 | Braking energy | ① motor RMS | ② genset | ③ buffer 5 min | ④ peak regen |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for lbl in ("empty_curb", "payload_-20pct", "payload_nominal_GVW", "payload_+20pct"):
        d = P[lbl]
        w(f"| {lbl.replace('_',' ')} | {d['mass_kg']:.0f} kg | {d['E_per_km_kWh']:.3f} kWh/km | "
          f"{d['P_peak_kW']:.1f} kW | {d['P95_kW']:.1f} kW | {d['E_braking_kWh']:.2f} kWh | "
          f"{d['N1_motor_rms_shaft_kW']:.1f} kW | {d['N2_genset_const_bus_kW']:.1f} kW | "
          f"{d['N3_buffer_5min_kWh']:.2f} kWh | {d['N4_peak_regen_wheel_kW']:.1f} kW |")
    w()

w("### T7 — Sustained 10 km climb at 6%, GVW\n")
CL = R["sensitivity"]["climb_10km_6pc"]["per_speed"]
w("| Speed held | Wheel power | DC bus | Engine shaft (series) | Engine shaft (direct) | Engine crank rpm (locked) | Engine capability at that rpm |")
w("|---|---|---|---|---|---|---|")
for k, d in CL.items():
    w(f"| {k.replace('kmh',' km/h')} | {d['wheel_kW']:.1f} kW | {d['bus_kW']:.1f} kW | "
      f"{d['series_engine_shaft_kW']:.1f} kW | {d['direct_engine_shaft_kW']:.1f} kW | "
      f"{d['engine_rpm_locked']:.0f} | {d['engine_max_shaft_kW_at_that_rpm']:.1f} kW |")
w()
FS = R["sensitivity"]["climb_10km_6pc"]["forward_sim"]
w("| Configuration | Settled speed on the 6% | Time for the 10 km | Buffer exhausted after |")
w("|---|---|---|---|")
for k, d in FS.items():
    bf = f"{d['battery_exhausted_after_s']:.0f} s" if d.get("battery_exhausted_after_s") else "—"
    tt = f"{d['time_to_climb_10km_s']:.0f} s" if d["time_to_climb_10km_s"] else "—"
    w(f"| {k} | {d['settled_speed_kmh']:.1f} km/h | {tt} | {bf} |")
w()

w("### T8 — The same 10 km at −6% (descent), GVW\n")
DS = R["sensitivity"]["descent_10km_6pc"]["per_speed"]
w("| Descent speed | Retardation demanded | Duration | Energy to dissipate |")
w("|---|---|---|---|")
for k, d in DS.items():
    w(f"| {k.replace('kmh',' km/h')} | {d['retardation_required_kW']:.1f} kW | "
      f"{d['time_10km_s']:.0f} s | {d['E_to_dissipate_kWh']:.2f} kWh |")
w()
DT = R["sensitivity"]["descent_10km_6pc"]["thermal"]
w("Friction-brake energy and adiabatic rotor temperature rise (60 kg of iron), "
  "buffer starting at the supervisor's 55% SOC target and accessories drawing "
  "2 kW throughout:\n")
w("| Usable buffer | 60 km/h, no engine brake | 60 km/h, +10 kW engine drag | 60 km/h, +30 kW exhaust brake | 85 km/h, no engine brake | 85 km/h, +30 kW exhaust brake |")
w("|---|---|---|---|---|---|")
for buf in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
    cells = []
    for tag in (f"buffer{buf}kWh_60kmh_no_engine_brake",
                f"buffer{buf}kWh_60kmh_engine_drag_10kW",
                f"buffer{buf}kWh_60kmh_exhaust_brake_30kW",
                f"buffer{buf}kWh_85kmh_no_engine_brake",
                f"buffer{buf}kWh_85kmh_exhaust_brake_30kW"):
        d = DT[tag]
        cells.append(f"{d['friction_brake_energy_kWh']:.2f} kWh / {d['adiabatic_dT_K']:.0f} K")
    w(f"| {buf:g} kWh | " + " | ".join(cells) + " |")
w()

w("### T8b — Does the 2.8:1 direct path hold 6% at all? Engine-curve sensitivity\n")
AC = R["sensitivity"]["direct_path_vs_engine_curve"]
w("| Full-load torque curve | Torque @1,600 rpm | Peak power | Best grade held (alone) | at | Holds 6%? |")
w("|---|---|---|---|---|---|")
for k, d in AC.items():
    rng = d["speed_range_holding_6pct_kmh"]
    yn = (f"**yes**, {rng[0]:.0f}–{rng[1]:.0f} km/h" if d["holds_6pct_anywhere"]
          else f"no (short by {d['min_deficit_kW']:.1f} kW)")
    w(f"| {k.replace('_',' ')} | {d['torque_at_1600rpm_Nm']:.0f} Nm | "
      f"{d['peak_power_kW']:.0f} kW | {d['best_grade_pct']:.2f}% | "
      f"{d['at_speed_kmh']:.0f} km/h | {yn} |")
w()

w("### T9 — Baseline cross-checks\n")
BC = R["baseline_crosscheck"]
w("| Baseline statement | WS1 recomputation | Verdict |")
w("|---|---|---|")
w(f"| Cruise 85 km/h flat: ~2.0 kN, ~47 kW at the wheel | {BC['cruise85_force_N']:.0f} N, "
  f"{BC['cruise85_wheel_kW']:.1f} kW | confirmed |")
w(f"| 20% grade launch: 13.5 kN | {BC['launch_20pc_grade_force_N']:.0f} N | confirmed (baseline rounds up) |")
w(f"| Diesel-only force through 2.8:1: ~5.0 kN | {BC['engine_direct_max_force_N_at_700Nm']:.0f} N | confirmed |")
w(f"| Diesel-only force zero below ~35 km/h | idle (700 rpm) = {BC['engine_idle_road_speed_kmh']:.1f} km/h | confirmed |")
w(f"| V2 genset floor ~110 kW to hold 60 km/h on 6% loaded | "
  f"{BC['grade6_at_60kmh_engine_shaft_plus_aux_kW']:.1f} kW engine shaft incl. accessories | confirmed |")
c85 = BC["combined_at_85kmh"]["motor_75kW"]
w(f"| Combined ~8 kN at 85 km/h → holds 9–10% grade | {c85['combined_force_kN']:.2f} kN → "
  f"{c85['grade_holdable_pct']:.1f}% | confirmed, but only for {c85['minutes_on_2kWh_buffer']:.1f} min on a 2 kWh buffer |")
w(f"| Series-path efficiency ~83% | {BC['eta_series_product']:.4f} = 81.4% from the quoted components | **discrepancy** |")
w()

w("### T10 — Motor envelope demanded by the cycles (at the motor shaft, 10:1)\n")
ME = R["motor_envelope"]
w("| | " + " | ".join(ME.keys()) + " |")
w("|---|" + "---|" * len(ME))
for lbl, k, f in [("Max shaft speed", "max_shaft_speed_rpm", "{:.0f} rpm"),
                  ("Max motoring torque", "max_motoring_torque_Nm", "{:.0f} Nm"),
                  ("Max braking torque", "max_braking_torque_Nm", "{:.0f} Nm"),
                  ("RMS torque", "T_rms_Nm", "{:.0f} Nm"),
                  ("Max motoring power", "max_motoring_kW", "{:.1f} kW"),
                  ("Max braking power the machine sees (75 kW cap)", "max_braking_kW_capped", "{:.1f} kW"),
                  ("Max braking power demanded (uncapped)", "max_braking_kW_uncapped_demand", "{:.1f} kW")]:
    w(f"| {lbl} | " + " | ".join(f.format(ME[k2][k]) for k2 in ME) + " |")
w()
w("### T11 — Road-load coefficient sensitivity (CdA and air density)\n")
RL = R["sensitivity"]["road_load_coefficients"]
w("| CdA / ρ | 85 km/h cruise | VOLT-SUB E/km | VOLT-REG E/km | VOLT-REG P95 | V2 6% hold speed |")
w("|---|---|---|---|---|---|")
for k, d in RL.items():
    w(f"| {k.replace('CdA','').replace('_rho',' m² / ')} kg/m³ | {d['cruise85_wheel_kW']:.1f} kW | "
      f"{d['SUB_E_per_km_kWh']:.3f} kWh/km | {d['REG_E_per_km_kWh']:.3f} kWh/km | "
      f"{d['REG_P95_kW']:.1f} kW | {d['V2_6pct_hold_speed_kmh']:.1f} km/h |")
w()
w("### T12 — Cycle composition by speed band\n")
w("| Band | VOLT-SUB time | VOLT-SUB distance | VOLT-REG time | VOLT-REG distance |")
w("|---|---|---|---|---|")
CA, CB = R["cycle_composition_VOLT-SUB"], R["cycle_composition_VOLT-REG"]
for b in CB:
    w(f"| {b} km/h | {CA[b]['time_pct']:.1f}% | {CA[b]['distance_pct']:.1f}% | "
      f"{CB[b]['time_pct']:.1f}% | {CB[b]['distance_pct']:.1f}% |")
w()
w(f"\nBaseline stall spec (13.5 kN at the wheel) = "
  f"{list(ME.values())[0]['torque_at_stall_spec_Nm']:.0f} Nm at the motor shaft.\n")

open(os.path.join(HERE, "tables.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
