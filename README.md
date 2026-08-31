# Project Volt

**A drivetrain research program run end to end by AI agents, directed by
someone with no engineering training, that killed its own best ideas on
criteria written before the numbers existed.**

This repository is the complete record: every baseline, every workstream, all
seventeen adversarial review rounds — the seven first passes, every one of which
returned material or blocking findings, the rework rounds that followed, and the
three rounds that returned nothing — the production log with the foreman's own
rule breaches in it, and the round that stopped NOT CONVERGED after exhausting
its rework budget and was never reopened. Nothing was deleted to make the story
tidier.

| | |
|---|---|
| **The method** | [METHOD.md](METHOD.md) — how the trial was run, the defect record, the failure-modes catalogue |
| **The results** | [FINDINGS.md](FINDINGS.md) — eight claims, each with its status, numbers, evidence and reproduction command |
| **The limits** | [LIMITATIONS.md](LIMITATIONS.md) — read this before you believe anything above |
| **Reproduce it** | [REPRODUCE.md](REPRODUCE.md) — one command per workstream, the verifiers, the determinism checks |
| **The exhibit** | https://valimenai-ux.github.io/project-volt/ — an interactive walk through the verdicts and the 10 Hz traces |

> **The exhibit link is pending.** It is the deploy target, not a confirmed live page: the exhibit publishes at close-out §7 and the link should be treated as unbuilt until that deploy is verified.

<!-- PLACEHOLDER: the exhibit URL above is the deploy target for WS12_exhibit/app/.
     It goes live at the GitHub Pages deploy (CLOSEOUT §7) and is confirmed by the
     foreman then. Until that anonymous 200 check passes, treat the link as unbuilt. -->

---

## The claim, and the limitation, first

**The claim.** You can use AI agents to run trials on novel engineering
concepts without being an engineer, and get output that is falsifiable rather
than merely fluent — if you impose the structure. Pre-registration, kill
criteria written before the computation, fresh-context adversarial review that
cannot be argued with, and verifiers that re-derive every number from the data
file.

**The limitation, which is not a footnote.** The method
**catches internal inconsistency, never wrong physics**. Across the program the
structure caught mislabelled constructions, statistics standing in for other
statistics, robustness claims that were asserted and never run, and interface
members whose construction did not match their name.
It has never been shown to catch a wrong physical model, because nothing here
touched hardware. The reference truck every Vehicle Zero verdict is scored
against sits **-31.69%** [anchor_resid_all] below its own sourced in-use fuel
anchor, and the workstream that built it records
`calibrate_order_satisfied: false` [calibrate_satisfied].
**Consistency is not validity.**

Everything below is stated inside that boundary. The engineering results are
real results — several of them are closed-form and hold regardless of the
model's calibration — and they are model-relative where the record says they
are.

---

## 1. The premise

**In plain terms.** Koenigsegg put a supercar on the road with no gearbox: one
fixed ratio, with electric motors filling in the torque the engine cannot make
at low speed. The question this program asked was whether that logic scales to
commercial trucks, where a gearbox is heavy, expensive and universal. If
electric torque-fill can delete the transmission from a delivery truck, that is
a real simplification. If it cannot, knowing *where* it stops being possible is
also a result.

**The numbers.** Two vehicles. Vehicle Zero is an Isuzu NPR-HD class delivery
truck at 6,600 kg GVW, in two variants on one shared electric spine. Vehicle One
is a tractor-trailer at **36,300 kg** [gcw] GCW. The metric of record for both
is fuel energy per **payload** tonne-km, not per kilometre — at a fixed legal
gross weight every kilogram of powertrain displaces a kilogram of freight, so
per-kilometre efficiency flatters a heavy candidate. "Per-km efficiency flatters; per-payload judges" [d13_perkm].
Advance criteria were pre-committed: **3%** [ws8_bar_nominal] or better at
nominal on the ensemble minimum, and **0%** [ws8_bar_corner] or better at every
corner.

---

## 2. Vehicle Zero

**In plain terms.** A 6.6-tonne delivery truck with no gearbox. Two variants:
"Postal", a pure series hybrid for stop-go suburban delivery, where the engine
never touches the wheels; and "Trucker", which was originally allowed to lock
its engine to the road on the highway through a fixed final drive. Both share
one battery, one motor family and one power electronics spine, all sized by
their own workstreams against duty-cycle requirements.

**The numbers.** Four workstreams produced the components: duty cycles and
loads (WS1), the traction motor, inverter and brake resistor (WS2), a 288-cell
lithium-titanate pack (WS3), and the genset (WS4). Each was adjudicated by a
fresh-context reviewer, and each first pass came back with material or blocking
findings — the full table is [METHOD.md](METHOD.md) §3. WS2 needed four rounds
and stopped once at "3 rounds exhausted, final round not clean" [ws2_notconverged]
before the lead extended it.

---

## 3. The clutch trial

**In plain terms.** The one place a mechanical path might still beat an
electric one is a steady highway cruise, where a clutch could lock the engine
directly to the wheels and skip two energy conversions. The program built that
clutch into the design, then put it on trial against a criterion written months
of program-time earlier: beat pure series by at least 5% or be deleted. The
first pass passed. Then a ruling corrected how the efficiency chain was counted
— replacing a scalar assumption with the motor's modelled loss map — and the
answer changed sign. The clutch was deleted, along with its actuator, its
control code, its fault mode and the topology reference it came from.

**The numbers.** Gate G1, criterion **5%** [g1_criterion] net energy,
pre-committed:

| | ensemble-min over 8 seeds |
|---|---|
| first pass, under the superseded chain convention | **+6.26%** [g1_prior_min] |
| recomputed under the corrected convention | **-2.58%** [g1r_min] |
| missed its own criterion by | **7.58 pp** [g1_missed_pp] |
| seeds on which the locked path still won | **0 of 8** [g1_seeds_positive] |

The reversal is attributable: the modelled loss maps instead of a scalar chain,
**-7.01 pp** [g1_map_vs_scalar_pp]; charging the motor's magnetic drag to the
locked samples, **-1.77 pp** [g1_spin_pp]. Those two rows are the one exception
to this publication's paired-per-seed rule — they are the archived, ratified
differences of ensemble minima, and their paired companions are exported beside
them; see [FINDINGS.md](FINDINGS.md) claim 1. The verdict:
"GATE G1: EXECUTED. THE CLUTCH IS DELETED." [clutch_deleted]

This is the load-bearing event in the whole record. A criterion written before
the numbers killed the program's own favourite feature, and could not be
negotiated with. Detail: [FINDINGS.md](FINDINGS.md) claim 1.

---

## 4. The pivot

**In plain terms.** Deleting the clutch made the premise *more* pure, not less:
both variants became pure series, which is the locomotive lineage rather than
the supercar one — and that is the lineage that scales upward. So the program
took the question to a Class 8 tractor-trailer, where the transmission it wants
to delete is a 12-speed automated manual and the prize is much larger.

**The numbers.** Five architectures were specified against a conventional 13 L
diesel with a direct top gear. The metric of record, exactly as exported:
"fleet-mission fuel energy per PAYLOAD tonne-km [MJ/(t.km)], fleet mission = 70% LH-520 + 30% REG-165 by distance" [ws8_fleet_mix].
The ruler burns **38.78 L/100 km** [s0_fleet_lp100] on that mission and carries
**20,785 kg** [payload_s0] of freight.

---

## 5. The semi walls

**In plain terms.** At 36 tonnes the premise hits three walls, and the first one
is arithmetic rather than engineering. The ratio that lets a diesel cruise at
105 km/h without over-revving is about half the ratio it needs to hold a 6%
grade at full weight. One ratio cannot be both. Give it two ratios and the wall
moves but does not disappear: the low gear's coupling floor — the slowest road
speed at which the engine can stay connected at all — sits above the crawl speed
a steep grade forces, so on the steepest part of the duty the engine
disconnects itself. And underneath all of it is the mass wall: every candidate
won on fuel per kilometre and lost it back in freight.

**The numbers.**

*The ratio span.* Highest ratio under the rpm ceiling at 105 km/h:
**3.7699** [ratio_ceiling], closed form. Lowest ratio that holds the 6% grade:
**6.88** [ratio_needed], which puts the engine **1,732 rpm** [ratio_rpm_over]
over its ceiling at cruise. Feasible single ratios in the swept set:
`any_feasible = false` [ratio_any_feasible].

*The mass wall.* Every wave-one candidate won per kilometre — S1
**+6.03%** [s1_perkm_min], S2 **+8.62%** [s2_perkm_min], S3
**+4.88%** [s3_perkm_min], S4 **+3.36%** [s4_perkm_min] — and every one of them
handed it back as payload. On the metric of record: S1 **-0.69%** [s1_min],
S2 **+0.59%** [s2_min], S3 **-1.09%** [s3_min], S4 **-3.84%** [s4_min], against
a **3%** [ws8_bar_nominal] bar. Four kills.

*The cold wall.* Cold was binding for every candidate. S1's worst corner is
**-12.87%** [s1_cold_corner] at -10 C with the pack's cold charge acceptance
actually applied — against **+7.52%** [s1_gradeheavy] for the same candidate on
the grade-heavy corner. The conventional truck heats its cab from waste heat for
free; an electrified candidate pays for it, and the comparison has to charge
that.

*The third wall.* On a two-speed, the low gear's coupling floor is
**25.4 km/h** [wall3_floor_11l] on the 11 L engine and
**33.5 km/h** [wall3_floor_13l] on the 13 L. The steepest grade a *contiguous*
two-speed can hold is **6%** [wall3_11l] and **8%** [wall3_13l] respectively,
against a design duty whose steepest grade is **10.74%** [duty_grade_max].

Detail: [FINDINGS.md](FINDINGS.md) claims 2, 4 and 5.

---

## 6. The delivery truck on the honest metric

**In plain terms.** Late in the program the lead noticed that Vehicle Zero had
never actually been measured on the payload-denominated metric that had decided
everything at semi scale — a consistency flag the record carried for a day
before it was executed. So a modelled stock NPR-HD was built from its own spec
sheet, given a torque converter, a real six-speed automatic and a fuel-optimal
shift schedule, and both variants were run against it. The two answers have
opposite signs, and the difference is the duty.

**The numbers.**

| | V1 Postal, suburban duty | V2 Trucker, regional duty |
|---|---|---|
| per payload tonne-km, nominal | **+20.11%** [v1_nominal_min] | **-7.93%** [v2_nominal_min] |
| worst corner | **+19.12%** [v1_worst_corner] | **-9.98%** [v2_worst_corner] |
| per kilometre | **+25.29%** [v1_perkm_min] | **+8.41%** [v2_perkm_min] |
| freight given back | **5.11 pp** [v1_mass_cost_pp] | **16.19 pp** [v2_mass_cost_pp] |
| status at freeze | FROZEN-PROVISIONAL ADVANCE | FROZEN-KILL |

V2 wins on fuel and loses on freight: it is **-195 kg** [v2_breakeven_headroom]
past the curb mass at which it would exactly draw. And the kill is not robust —
with the modelled ruler's eight declared levers all at their pessimistic ends it
comes back to **+0.13%** [v2_pessimistic_min], a draw rather than an eight-point
loss, still short of the bar. V1's advance runs the other way: it improves to
**+37.78%** [v1_pessimistic_min] under the same treatment.

**V1's advance is conditional and the conditions were never run.** With the two
pending rulings the workstream itself escalated applied together, V1's governing
corner falls to **+3.66%** [v1_cold_both]; under the harshest defensible
cab-heat reading it goes to **-5.42%** [v1_cold_no_credit], which would fail the
corner bar. Both figures are in
`WS11_vehicle_zero_ruler/REPORT_WS11.md` §0 and neither is in the baseline.
See [FINDINGS.md](FINDINGS.md) §9 and [LIMITATIONS.md](LIMITATIONS.md).

---

## 7. What survived and what didn't

**In plain terms.** The program set out to find a genuinely more efficient truck
drivetrain. It found one duty where its architecture wins by twenty points, and
it explained, mostly, why the industry looks the way it does. Almost everything
it liked, it killed.

**Killed, on pre-committed criteria.** The lockup clutch (G1, executed). All
four wave-one semi architectures. Waste-heat recovery at semi scale, on both
waves. V2 Trucker on the honest metric. Predictive energy management as a lever,
once the incumbent was allowed to have it too. Two workstreams hit the
three-round rework cap and stopped NOT CONVERGED rather than being polished
until the reviewer went quiet; one was then reopened by the lead with a stated
reason and closed clean, and one was left exactly where it stopped.

**Survived, at the status the record gives it.** Electric torque-fill replacing
the gearbox at 6.6 t — v7 status "(ratified, model-relative)" [v7_claim1_status].
Two boundary laws that say where the premise stops working and are results in
their own right: the mass boundary, v7 status "ratified" and
"closed-form and simulated)" [v7_claim2_status]; and the duty boundary, v7
status "(V1 provisional, V2 kill)" [v7_claim3_status]. A third wall on two-speed
engine paths, v7 status "coupling floor vs crawl speed (provisional)" [v7_claim4_status].
And one advance carrying v7's own label, FROZEN-PROVISIONAL ADVANCE: V1 Postal at
**+20.11%** [v1_nominal_min], conditional on four rulings that were ordered and
never run. The Vehicle One wave-two advances are FROZEN-PROVISIONAL likewise, and
V2 Trucker is FROZEN-KILL.

**Not settled.** Nothing was measured. The ruler is uncalibrated. Every Vehicle
Zero verdict is model-relative by the program's own ruling, and the workstream
carrying the headline number had its round-1 pass adjudicated NOT CLEAN and its
round-2 rework gated but never adversarially reviewed — which is the single most
instructive event in the record and is written up as a control condition in
[METHOD.md](METHOD.md) §4.

---

## 8. The open frontier

**In plain terms.** The research track was frozen by the principal when the
returns stopped justifying the spend, not because the questions ran out. Five
lines of work were explicitly *not* cut, and are listed so whoever picks this up
knows where the edge is.

**The record.** R54 of the freeze:
"WS6, WS7, WS10, Vehicle Zero wave two (R48) and Vehicle One" [v7_r54] wave
three are NOT CUT. WS6 is packaging and the program heat ledger; WS7 is the
prototype and test plan, and carries the ruler calibration that would make any
Vehicle Zero verdict more than model-relative; WS10 is the combination trial;
R48's wave two poses an Atkinson-petrol genset for the Postal variant and a
mass-lean hybrid for regional delivery. The principal's own stated reason for
stopping: "The trials have mostly validated why the status quo is what it is" [v7_why].

---

## How to read this repository

- `BASELINE_v0.md` … `BASELINE_v7_FREEZE.md` — the program's governing state,
  in version order. **The highest-numbered one is authoritative**; the earlier
  ones are kept because they show which numbers each ruling was written against.
- `WS*/` — one folder per workstream: the assignment it executed, its code, its
  results data file, its report generated from that file, its verifier, and
  every adjudication findings file that failed it.
- `PM_LOG.md` — the production log, one line per launch, gate, bounce and
  packet.
- `NIGHT_REPORT.md`, `PM_PACKET_*.md` — shift and workstream hand-offs.
- `.claude/agents/` — the worker and adjudicator definitions, which are part of
  the record.
- `WS13_publication/CITATIONS.md` — every number and quoted phrase in this
  publication that carries a `[marker]`, with the file and path it came from,
  machine-checked. Declared specification constants and figures restated beside
  their own cited instance are deliberately unmarked; the index says which is
  which.

Statuses are exactly those of `BASELINE_v7_FREEZE.md`. Nothing in this
publication promotes one.

## Licence

Code is Apache-2.0 ([LICENSE](LICENSE)). Prose, data and figures are
CC BY 4.0 ([docs/LICENSE](docs/LICENSE)).
