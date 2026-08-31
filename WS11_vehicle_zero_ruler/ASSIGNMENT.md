# WS11 ASSIGNMENT — VEHICLE ZERO RULER TRIAL (executes BASELINE_v5 R32)

Read CLAUDE.md, ../BASELINE_v5.md (R32, R34, R38 and the R14/R9
conventions), ../WS1_loads_duty_cycles/REPORT_WS1.md (cycles VOLT-SUB
and VOLT-REG at 10 Hz — reuse them verbatim), the interface blocks of
WS2 (r4), WS3, WS4, and WS4's KX outputs when they land (build to
hot-swap `series_duty_v2`; state the vintage you ran). Runnable,
deterministic, byte-stable. Vehicle One folders are untouchable.

QUESTION OF RECORD: is the ratified Vehicle Zero design more efficient
than the truck it replaces, on the honest metric? This has never been
tested.

RULER — stock Isuzu NPR-HD: 4HK1-TC (WS4's reference 4HK1-class map,
205.2 g/kWh island), 6-speed torque-converter automatic with lockup
(state converter and gear efficiencies and shift logic), rear axle
ratio stated, curb mass sourced or declared, idle fuel modelled.
Calibrate to a public NPR fuel-economy reference and state it (sanity
corridor 18-30 L/100 km on VOLT-SUB, wide on purpose; a sourced anchor
is mandatory, a fit to the corridor is not).

CANDIDATES (the ratified design, nothing new): V1 Postal — pure
series, V3307-V1C-class genset with R19 start-stop, shared spine
(VM250-HV, 1200 V SiC, resistor), 288s LTO pack 11.08 kWh usable, R15
blend order, R16 cold curves — judged on VOLT-SUB (its design duty;
VOLT-REG is not a V1 cycle per R5). V2 Trucker — pure series,
4HK1-V2C 132 kW flat-rated, same spine and pack — judged on VOLT-REG,
VOLT-SUB reported alongside.

METRIC OF RECORD: fuel energy per PAYLOAD tonne-km at fixed 6,600 kg
GVW. Payload = GVW - curb. Build each candidate's curb from ratified
masses (spine rollup 230.8 kg, pack 281 kg, genset per WS4) minus the
deleted stock parts (transmission, converter, alternator/starter as
applicable), to the kilogram, with sources. State the ruler's payload
and each candidate's. Report per-km AND per-payload, both on the
PAIRED per-seed statistic, labeled.

CORNERS: payload +/-20% of ruler payload; -10 C with WS3 cold
acceptance applied; 2,000 m / +45 C (genset derate per R6 basis); and
the WS1 §4.4 10 km / 6% climb inserted into VOLT-REG.

ONE-FACTOR ROWS: mass penalty alone; regen alone; start-stop/engine-
off alone; engine operating-point (part-load) alone. Trip time per
R38 (report the ratio; the lead applies the <= +5% gate).

ADVANCE/KILL (pre-committed, same form as Vehicle One): ADVANCE only
if >= 3% better than the ruler on the candidate's design duty at
nominal, ensemble-min, AND >= 0% at every corner. Report the numbers;
the lead executes or spares.

TRACES (R34): export a 10 Hz trace file per run.

REPORT_WS11.md: ruler calibration; mass ledgers; results table per
duty (headline); one-factor decomposition; corners; trip time; R14
interface; escalations citing rulings; first-principles sanity
checks. Exit: launch ws-adjudicator (Opus) on this folder, then stop.
Do not commit; the night shift commits.
