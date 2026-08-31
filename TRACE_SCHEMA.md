# TRACE_SCHEMA — R34 10 Hz TRACE CONTRACT (lead-issued 2026-08-31)

Binds every pipeline from its next artifact (R34). The exhibit (WS12)
consumes ONLY files that conform. WS11's r2 traces are the reference
implementation; this schema generalises them.

## File
`data/trace_<vehicle>_<duty>_<corner>_seed<N>_10Hz.csv`, one per
(vehicle, duty, corner, seed). ALL 8 seeds per case (the ribbon needs
them), all corners. Comment header lines (`# key: value`) then CSV.

## Header metadata (mandatory)
program, workstream, round, vehicle, architecture, duty, corner, seed,
mass_kg, payload_kg, baseline_version, results_file, results_sha256,
generated_utc. Free-text notes allowed after these.

## Core columns (every vehicle)
t_s, x_m (cumulative distance), v_kmh, grade_pct, z_m (elevation,
cumulative), P_wheel_kW (signed: negative = braking demand),
fuel_g_per_s, fuel_cum_g, P_friction_brake_kW (signed positive as
heat), trip_time_flag (0/1 when capability-limited).

## Engine-carrying columns (ruler, S0, any engine)
N_eng_rpm, T_eng_Nm, P_shaft_eng_kW, engine_state (0 off / 1 idle /
2 loaded / 3 overrun), gear, lockup (ruler/AMT only), P_comp_brake_kW.

## Electrified columns (series, hybrid, BEV)
P_gen_bus_kW, P_bus_load_kW (accessories + heater), P_motor_bus_kW
(signed: negative = generating), P_motor_mech_kW, P_regen_pack_kW,
P_heater_kW, P_resistor_kW (blend order R15: pack -> heater ->
resistor -> friction; the four must sum to the braking demand served
electrically plus friction), soc_pct, T_pack_C, T_motor_C,
genset_state (0 off / 1 warm-up / 2 pinned / 3 above-pin),
motor_disconnect (0/1, where the architecture has one).

## Rules
All electrical quantities bus-side (R12). Missing physical quantity =
column absent, never zero-filled ("an absent trace must not read as a
measured zero"). Every column that reaches a screen must be traceable
to a pipeline variable named in the workstream's report. A trace file
is an artifact under the same three-way discipline as results.json.
