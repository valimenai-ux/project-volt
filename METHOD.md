# METHOD — how the trial was run

This is the spine of Project Volt. It is written for people who want to run an
engineering trial with AI agents and have the output be falsifiable rather than
merely fluent. The drivetrain work is the case study; it is in
[FINDINGS.md](FINDINGS.md). This file is about the machinery that produced it.

---

## 0. The claim, and the limitation, first

The method **catches internal inconsistency, never wrong physics**.

That is the whole claim, and it is narrower than it sounds until you look at
what "internal inconsistency" covered in practice. Across the program the
structure caught: mislabelled constructions, statistics standing in for other
statistics, robustness claims asserted without being run, verdicts asserted
beyond their evidence, and machine-readable interface members whose
construction did not match their name. Every one of those was invisible to the
author who wrote it and was found by something else reading the artefact cold.

What the record does **not** demonstrate is catching a wrong physical model. No
hardware was built and nothing was measured. The Vehicle Zero ruler — the stock
truck every Vehicle Zero verdict is scored against — sits **-31.69%** [anchor_resid_all]
below its own sourced in-use anchor, and **-40.10%** [anchor_resid_era] below the
era-correct member of that anchor, and the workstream states plainly that
`calibrate_order_satisfied: false` [calibrate_satisfied]. That residual is
escalation ESC-1 and it was never closed.

**Consistency is not validity.** A pipeline can be perfectly self-consistent,
byte-reproducible, three-way verified and adversarially adjudicated, and still
be modelling the wrong truck. Everything below is a description of how to stop
lying to yourself. It is not a description of how to be right.

The lead recorded the same boundary in the program's own doctrine when the
verdicts were frozen:

> R44: the crowdsourced in-use anchor cannot "calibrate a cycle" [r44_cannot].
> "Verdicts are MODEL-RELATIVE until WS7 measures a" [r44_modelrelative] stock
> NPR-HD on the program cycles — a mandatory task — with no external
> "efficiency claim before it" [r44_noclaim].

---

## 1. What was run

An engineering program on a transmissionless hybrid drivetrain, executed almost
entirely by Claude Code agents between 2026-08-29 and 2026-08-31, directed by
one person with no engineering training.

- **Eight workstreams produced artefacts** — WS1 loads and duty cycles, WS2
  traction motor, WS3 battery, WS4 genset (plus its KX round), WS5 controls,
  WS8 semi architecture, WS9 wave two, WS11 the ruler trial. A ninth (WS6
  packaging) was assigned and never started; two more (WS12 exhibit, WS13 this
  publication) are the close-out.
- **Two vehicle classes** — a 6,600 kg delivery truck and a
  **36,300 kg** [gcw] tractor-trailer.
- **Eleven candidate architectures** — V1 and V2 at Vehicle Zero; S1-S4 at
  Vehicle One wave one; S5, S5-13L, S6, S7 and S4' at wave two — plus three
  waste-heat-recovery modifiers and one prime-mover trial.
- **Seventeen adjudication rounds**, every one of which left a `FINDINGS_*.md`
  file on disk, and two gates with pre-committed kill criteria (G1 and the WHR
  gate).
- **One research freeze**, called by the principal when the returns stopped
  justifying the budget:

> "The trials have mostly validated why the status quo is what it is" [v7_why]
> rather than producing a novel drivetrain.

Every artefact is in this repository. Nothing was deleted to make the story
tidier: the superseded baselines, the findings files that failed the work, the
production log with the foreman's own rule breaches in it, and the rounds that
stopped NOT CONVERGED are all still here, because they are the evidence.

---

## 2. The structure

Six load-bearing pieces. Each exists because something went wrong without it.

### 2.1 Pre-commit, then measure (D1)

> "Pre-commit, then measure. Every gate has a numeric kill criterion" [d1_precommit]
> written BEFORE the computation. ... "The criterion could not be" [d1_notnegotiable]
> negotiated with.

Gate G1 is the reference case. The criterion — the locked mechanical path must
beat pure series by at least **5%** [g1_criterion] net energy — was written into
BASELINE_v1 before any number existed. When the corrected computation returned
**-2.58%** [g1r_min], the criterion fired against the program's own favourite
feature and the clutch was deleted. A criterion written after the numbers would
have been argued with. This one could not be.

### 2.2 Pre-registration, in a context the workers cannot read (D2)

> "Pre-register acceptance bands before reading any report" [d2_prereg], and
> "keep them where workers cannot read them" [d2_private].

Bands are a calibration instrument for the lead, not a gate. A miss locates an
error in the lead's priors; it never overrides a ratified number. The value of
the discipline is that it makes the lead's expectation falsifiable too. It
worked exactly once in the most useful way: the lead
"pre-registered G1-R at +4 to +6% and it came in at -2.58%" [d3_band]
(**-2.58%** [g1r_min] as exported), which is how the program learned D3 —
"Convention swaps are level shifts, not perturbations" [d3_convention].

### 2.3 Separation of roles, with disk as the only interface

Four roles, none of which shares a context with another:

| role | may | may not |
|---|---|---|
| principal | set scope, overrule any ruling | — |
| lead | ratify, rule on escalations, own the baseline and the gates | run production |
| foreman | launch workers and adjudicators, run mechanical gates, keep the log | ratify, filter escalations, touch a workstream folder |
| worker / adjudicator | execute one bounded order | anything outside its folder |

The foreman charter states the constraint in the negative, which is the form
that binds:

> "You MAY NOT: ratify or reject work on its merits; resolve, soften," [fm_selfratification]
> "filter, or summarize-in-place any escalation" [fm_selfratification2].

Because no two roles share a context, the only way information moves between
them is a file on disk. That is not an inconvenience; it is the mechanism.
Doctrine D4: "Artifacts on disk are the record; prose is not" [d4_ondisk]. A
claim made in a chat window and not written to a file did not happen — the
program has an instance of exactly that failure recorded against the lead.

### 2.4 Fresh-context, disk-only adjudication

The adjudicator (`.claude/agents/ws-adjudicator.md`) is a separate agent with no
history of the work. It reads

> "only what is on disk. Your mandate comes from how WS1's two blocking" [adj_mandate]
> "defects were found — a wrong machine-readable interface and single-draw" [adj_mandate2]
> stochastic extrema, both invisible to the author.

It re-derives at least five headline numbers independently, verifies that the
machine-readable interface block

> "agrees with the report prose AND the data file — three-way, verbatim." [adj_threeway]

and it is forbidden from doing anything about what it finds:

> "You never fix anything, never soften an escalation, never rule on one," [adj_never]
> and never talk to the worker.

That last constraint is what makes an adjudicator's finding usable. An
adjudicator that can negotiate is a second author.

### 2.5 Three-way verification and R14 export discipline

Every workstream ships a `results_*.json`, a report generated from it, and a
`verify_*.py` that re-resolves every rendered number back to its JSON path and
asserts the string is present verbatim. The worker's own charter forbids the
alternative: every headline number must be generated from

> "your results data file — nothing transcribed by hand." [worker_rule2]

R14 came later, as a structural fix after one workstream failed three rounds on
the same defect class:

> R14 — "EXPORT DISCIPLINE" [r14_export]. "Every machine-readable worst-case field is computed as an" [r14_body]
> "explicit max/min over an enumerated case set, with the governing case" [r14_body2]
> labeled inline in the interface block.

The reason this matters is that "worst case" is not a number, it is a function
of a case set, and a worst case computed over the wrong set is wrong in a way
that reads as authoritative. Two of the program's blocking findings are exactly
that defect.

### 2.6 Bounded rework, and NOT CONVERGED as a legitimate outcome

A workstream gets a maximum of three rework rounds. If the final round is not
clean, it stops and is marked NOT CONVERGED with its full trail. This happened
twice, and neither was treated as a failure of the pipeline:

- **WS2 traction motor** — "3 rounds exhausted, final round not clean" [ws2_notconverged].
  The lead subsequently extended the cap deliberately, on the record and with a
  stated reason (every prior round's fix had held, and R14 addressed the
  structural defect class), and round 4 closed clean. That is the cap working
  as a forcing function rather than as a wall.
- **WS4 KX round** — "3 rework rounds exhausted, final round not clean" [kx_notconverged].
  No fourth round was run. It is NOT CONVERGED at the freeze and its open
  blocking finding is in [LIMITATIONS.md](LIMITATIONS.md) §8.

The alternative — rounds until clean — converges on an artefact that has been
polished until the adjudicator stops objecting, which is a different thing from
an artefact that is right. A cap makes "we could not close this" a reportable
result.

---

## 3. The defect record, with numbers

**Every first-pass review in this program returned material or blocking
findings.** Seven workstream first passes; not one came back clean. This is the
single most important number in this file, because it is the measurement of what
the structure is worth.

| # | workstream | first-pass result | source |
|---|---|---|---|
| 1 | WS1 loads & duty cycles | 13-agent adversarial review before submission | `WS1_loads_duty_cycles/REPORT_WS1.md` §9 |
| 2 | WS2 traction motor | 0 blocking, 2 material, 5 minor | `WS2_traction_motor/FINDINGS_WS2_r1.md` |
| 3 | WS3 battery | 1 blocking, 1 material, 4 minor | `WS3_battery/FINDINGS_WS3_r1.md` |
| 4 | WS4 genset | 0 blocking, 2 material, 5 minor | `WS4_genset/FINDINGS_WS4_r1.md` |
| 5 | WS8 semi architecture | 2 blocking, 5 material, 6 minor | `WS8_semi_architecture/FINDINGS_WS8_r1.md` |
| 6 | WS9 wave two | 4 blocking, 6 material, 9 minor | `WS9_vehicle_one_wave2/FINDINGS_WS9_PRE_r1.md` |
| 7 | WS11 ruler trial | 3 blocking, 8 material, 13 minor | `WS11_vehicle_zero_ruler/FINDINGS_WS11_r1.md` |

Verbatim, one line each:

1. **WS1** did not have a `ws-adjudicator` round — the agent did not exist yet.
   It ran a
   "13-agent adversarial review: seven agents recomputed the headline numbers" [ws1_13agent]
   from first principles, three audited the source, two attacked completeness and
   one adjudicated. Its result:
   "Seventeen defects were found and fixed and nine analysis" [ws1_review] gaps
   closed before the report was submitted. There is no `FINDINGS_WS1_r1.md` on
   disk; the record of that review is `REPORT_WS1.md` §9, which lists each
   defect and what it moved. WS1's two blocking defects are what the adjudicator
   agent was subsequently written to catch.
2. **WS2** — "Verdict: no blocking findings. Two material findings (WS2-F1, WS2-F2), five minor." [ws2_r1]
3. **WS3** — "Two findings of consequence (one blocking, one material), then minors." [ws3_r1]
4. **WS4** — "Verdict: no blocking findings. Two material findings (F1, F2) and" [ws4_r1] five minor.
5. **WS8** — "Verdict: NOT CLEAN. Two blocking findings, five material, six minor." [ws8_r1]
6. **WS9** — "RESULT: NOT CLEAN. Four blocking, six material, nine minor." [ws9_pre]
7. **WS11** — "Verdict on the round: NOT CLEAN" [ws11_r1] — 3 blocking, 8 material, 13 minor.

**Three of the seventeen rounds returned nothing, and they are named here so
the count cannot be read as seventeen-for-seventeen.** The claim is about first
passes; three later rounds came back clean:
"Verdict: no blocking or material findings." [ws2_r4_clean] (WS2 r4),
"No blocking or material findings." [ws3_r2_clean] (WS3 r2), and
"Verdict: no blocking or material findings. No new findings of any" [ws4_r2_clean]
severity (WS4 r2). That is what a rework round closing properly looks like, and
it is the reason the seven-for-seven figure is stated of first passes only.

Rework rounds did not converge quickly either. WS8 was still not clean at its
second and third rounds — "Verdict: NOT CLEAN. One blocking, four material, seven minor." [ws8_r2]
and "Verdict: NOT CLEAN. Two blocking, six material, twelve minor." [ws8_r3] —
and the WS4 KX round ran the full three and failed each one:
"NOT CLEAN — 2 blocking, 3 material, 8 minor" [kx_r1_result],
"NOT CLEAN — 0 blocking, 3 material, 4 minor" [kx_r2_result],
"NOT CLEAN — 1 blocking, 3 material, 6 minor" [kx_r3_result].

**Including on the lead's own work.** The lead's doctrine entry says it plainly:

> "Every first-pass adjudication in this program (WS1-WS4) found" [d5_baserate]
> "material or blocking defects, almost all in interfaces, member" [d5_where]
> "selection, and definitional blurs, not physics" [d5_notphysics].

That last clause is the honest reading of the whole record and it is the reason
this file leads with its limitation. The defects were bookkeeping, labelling,
member selection and case enumeration. They were not physics errors, because
nothing in this structure is capable of finding a physics error.

**One inconsistency in the record's own account of itself, stated rather than
smoothed.** `BASELINE_v7_FREEZE.md` describes the method as
"five-for-five first-pass defect detection" [v7_claim8_rate]. That phrasing was
inherited from BASELINE_v5's R37, written when five first passes had been run.
Two more (WS9's pre-adjudication and WS11 r1) were run and returned findings
before v7 was written. The table above enumerates seven. The baseline is frozen
and this publication may not edit it, so both readings are on the record: v7's
label as v7 states it, and the enumerated trail with a citation per row.

---

## 4. The natural experiment

On 2026-08-31 at 07:40 the principal, asked how to close an overrunning night
shift, chose to let two workstreams finish, gate them mechanically, and
**"SKIP their adjudication rounds"** [nx_decision].

The foreman recorded the consequence at the time, before the outcome was known:

> "WS11's round-2 rework closes 3 blocking + 8 material + 13 minor findings and NOTHING WILL HAVE CHECKED THAT WORK" [nx_consequence]

and, in the commit message for that work:

> "a gate PASS on r2 is evidence of reproducibility only and is NOT evidence the findings are closed" [nx_gate_meaning]

**This is the control condition, and it is the strongest single piece of
evidence in the file.** Everything else here is an argument that the structure
does work. This is the one place the structure was removed, deliberately, with
everything else held constant — same models, same worker tier, same mechanical
gate, same byte-stability requirement — and the output immediately became
unverified. The `+20.11%` [v1_nominal_min] headline that Vehicle Zero's whole
result rests on stands on rework that nothing checked.

Three things make it a clean experiment rather than an anecdote:

1. **The base rate is known.** Seven for seven, section 3. The prior that an
   unchecked rework round is clean is low and it is measured, not assumed.
2. **The gate did pass.** WS11 r2 regenerated byte-identically and its verifier
   reported every rendered number verbatim. Round 1 also passed a byte-stable
   gate — and was then found NOT CLEAN with its central robustness claim
   falsified. Reproducibility and correctness are orthogonal, and this pair of
   rounds is the demonstration.
3. **A number moved inside the unchecked work.** The foreman logged
   "ONE NUMBER MOVED: V1's cold+cab-heat bracket" [nx_number_moved] — from
   **+2.64%** [v1_cold_cabheat_r1] to **+4.72%** [v1_cold_cabheat_fp] under the
   fixed-point fix, with the harshest reading at **-5.42%** [v1_cold_no_credit].
   A number moving in a round nothing adjudicated is precisely the situation the
   adjudication round exists for.

A second, weaker control sits beside it: WS5 ran with no adjudication round at
all. "WS5 is the only workstream of the night with ZERO adjudication rounds" [nx_ws5].
Its worker, told no adversarial reviewer was coming, wrote its own weakness list
as report section 14 — which is the correct response and is also not a
substitute, because the failure mode adjudication catches is the one the author
cannot see.

The experiment is not a criticism of the decision. Cutting the rounds was a
defensible call under a budget and a clock, made by the person entitled to make
it, and recorded as his decision rather than laundered as the foreman's. The
point is what it demonstrates: **remove the structure and the output is
immediately unverified.** That is the causal claim the rest of this file can
only assert.

---

## 5. FAILURE MODES CATALOGUE

Each entry: the failure mode, the instance in this record that produced it, and
the countermeasure that caught it. These are the modes an AI-run engineering
program actually exhibits. Eight of the eleven are bookkeeping, labelling or
case-enumeration errors; FM-3 is structural and has no instance, by design; the
tenth is the record contradicting itself across time; and the eleventh is the one
instance the lead labelled a physics defect, which is included precisely so it
can be examined rather than skipped.

### FM-1. Partial correction — the fix reintroduces the defect it fixed

**The instance.** In WS4's KX round 2, a minor finding (`m6`) about a
machine-readable field whose construction did not match its name was closed at
root cause. The same round's rework then introduced the identical defect class
in three new blocks. The adjudicator's own words:

> "construction defect the same round just fixed in the heat ledger under m6" [fm_partial_findings]
> — reintroduced in three new blocks by the same rework.

The production log records it as
"the same construction defect this very round just fixed as m6, reintroduced in three new blocks" [fm_partial_pmlog].
The workstream had by then been caught by this mode in three consecutive rounds.

**The countermeasure.** Order a sweep for the defect **family**, not for the
named instances, and require the sweep to report where it found *nothing* as
well as where it found something. Round 3's sweep, ordered that way,
"found TWO MORE instances of the same defect family the adjudication had not named" [fm_partial_sweep]
— including the one member another workstream was consuming live. WS11's r2
sweep, ordered the same way, went further:

> "six further name/construction defects, two further unrun claims and seven further statistic-of-statistics constructions found" [fm_sweep_ws11]
> — four of them in code written for that round.

The clean-area reporting matters as much as the finding: a sweep that only
reports hits gives you no way to tell a thorough sweep from a lucky one.

### FM-2. Statistic-of-statistics — a ratio of medians wearing a paired label

**The instance.** KX2-M3:
"every fuel delta between paired dispatches in the new blocks is a ratio of ensemble statistics" [fm_statofstat]
rather than the paired per-seed statistic the doctrine mandates — and one of them
was *labelled* "the paired per-case median" in three places. The measured
difference, from the adjudicator's own re-derivation:

```
| nominal | **+0.062 %** | **+0.169 %** | +0.088 % |
```

(`WS4_genset/FINDINGS_KX_r2.md` line 345 — exported figure, paired figure, and
the gap) [fm_statofstat_row]. A companion bracket figure flipped sign between the
two constructions.

**Why it is a whole family and not one slip.** The same defect had already
reached ratified doctrine once. R36 is the correction:

> R36 — "DOCTRINE CORRECTION (from M2). D13 is restated" [fm_r36] ... The former
> wording carried a "ratio-of-medians artifact into doctrine. Per-km claims are stated on" [fm_r36_why]
> the paired statistic only.

**The countermeasure.** Two, and both are needed. (a) A program-wide rule that
every margin is formed seed by seed and only then enveloped — R36. (b) Verifiers
that **re-derive the construction** rather than checking the label: WS11's
verifier confirms its margin envelopes are paired-per-seed over 8 seeds with
governing cases, rather than trusting the field name. A label is a claim about
code, and claims about code are checkable.

### FM-3. Self-ratification drift

**The instance.** This one has no instance, which is the point. It is the
structural failure the whole foreman/lead/adjudicator architecture exists to
prevent: the layer that produced the work deciding whether the work is good. The
charter forbids it in the negative —
"You MAY NOT: ratify or reject work on its merits; resolve, soften," [fm_selfratification]
"filter, or summarize-in-place any escalation" [fm_selfratification2] — and the
adjudicator charter forbids the mirror image:
"You never fix anything, never soften an escalation, never rule on one," [adj_never].

**Why it needs a rule rather than good intentions.** An agent asked to review its
own work will find real defects and will also, reliably, find that its central
claim survives them. Every escalation in this program went to the lead
unresolved, including escalations that the foreman could obviously have
answered. The cost is latency. The benefit is that no verdict in
[FINDINGS.md](FINDINGS.md) was signed off by the thing that produced it.

**The countermeasure.** Separate contexts, enforced by the harness rather than
by instruction — the foreman cannot write inside a workstream folder, the
adjudicator cannot write work product, the worker cannot edit a baseline. Roles
that share a context share a bias.

### FM-4. False clean-certifications

**The instance.** KX round 3's construction sweep certified sixteen areas as
examined and clean. The foreman ordered the round-3 adjudicator to spot-check
those certifications. The result:

> "Two of the sixteen areas the construction sweep certifies as" [fm_falseclean]
> examined and clean are demonstrably not clean — and, per the log,
> "TWO are false, including one block that contains the very defect it certifies clean" [fm_falseclean_pmlog].

**The countermeasure.** A sweep's clean certifications are themselves auditable
claims and must be sampled, never accepted. This is the countermeasure to the
countermeasure for FM-1: asking for clean-area reporting is right, and it
creates a new surface of unverified assertions that has to be audited in turn.
The record states the order and the result; it does not state how many of the
sixteen were sampled, so no claim is made here about how cheap the audit was.

### FM-5. Robustness asserted, not run

**The instance.** WS11 round 1 exported a bracket row named *all ruler-favourable
choices reversed* which reversed five choices and left the four largest levers —
gear mesh, AT pump, final drive, lock-up slip — at their ruler-favourable
values. The report then argued that V2's KILL was robust to ruler modelling. The
adjudicator's finding: "the KILL's robustness claim was false" [fm_unrun].

Run properly in round 2, the eight-lever pessimistic row takes V2 from
**-7.93%** [v2_nominal_min] to **+0.13%** [v2_pessimistic_min] ensemble-min /
**+0.59%** [v2_pessimistic_median] median — across zero, from an eight-point loss
to a draw.

**The countermeasure.** A claim of the form "X does not depend on Y" is a
computation, not a sentence. Require the row to exist in the exported case set,
require the case set to be enumerated in the interface block (R14), and have the
verifier check the *direction* of every bracket row against its declared kind
rather than trusting the prose beside it.

### FM-6. Governing case enumerated outside the ruling's own design case

**The instance.** KX round 3's blocking finding: "the R20/ESC-12 analysis is enumerated over a case set that EXCLUDES R20's own declared design case" [fm_governing_case].
The ruling named a simulated corner; the analysis enumerated that corner's
*ambient*. Included, the comparison reverses the workstream's own conclusion and
turns a machine-readable `all_cases_within_capability: true` into false. The
governing number is absent from the heat ledger the downstream workstream would
have consumed.

**The countermeasure.** R14 again, read strictly: the enumerated case set is
part of the export, and an R14 field whose set omits the ruling's own named case
is a defect even when every member of the set is computed correctly. Machine-check
that the case set named by a ruling is a subset of the case set the field
enumerates.

### FM-7. A measurement that cannot fail

**The instance.** Two, both in WS9's pre-adjudication. First,
"the concordance module cannot fire on two thirds of its fields" [fm_tautology]
— only 5 of 15 were two-sided comparisons; 5 carried hard-coded verdict
literals and 2 were tautologies. Proven by mutation: removing an upstream clamp
produced a real extracted difference while the verdict still read CONSISTENT.
Second, a "measured over 96 runs" difference that was identically zero because
the key it compares is absent from all 576 records, so the fallback fired every
time.

**The countermeasure.** Mutation-test the checker, not just the artefact. A
check that has never been observed to fail has not been shown to be a check. The
adjudicator that found these did its mutation testing on throwaway copies under
a scratch directory and verified the repository was untouched afterwards.

### FM-8. Wrong branch of a non-monotone envelope

**The instance.** WS9's exported heat-ledger row for the 6% climb was evaluated
on the motor-only branch of a two-band envelope:
"exported 20.1 kW total rejection against a correct engine-coupled 507.3 kW" [fm_wrong_branch]
— a factor of about 25, in a machine-readable field whose named consumer had not
yet run.

**The countermeasure.** Where a physical envelope is non-monotone, the export
must label which branch it selected and why. This mode is invisible to any
check that verifies "the number in the report equals the number in the JSON",
because it does — the defect is upstream of the transcription. It is caught only
by someone re-deriving the quantity from the physics.

### FM-9. Inert provenance — an input listed and never called

**The instance.** WS8 round 1, blocking: "an inherited WS3 input the report states it uses and the pipeline" [fm_inert_provenance]
never applies — in the corner that governs every exported worst-case field. A
second instance in the same round (an inherited derate function, imported and
never called) made closing the two of them half of the next round's work.

**The countermeasure.** Every entry in a provenance list must be exercised by
the pipeline, and that must be asserted, not stated. WS8's README now says it in
the form that binds: an inert entry in a provenance list is a false claim about
what the numbers were built from.

### FM-10. The record disagreeing with itself over time

**The instance.** Doctrine and baselines are written from the numbers of the
round in flight. When a later round moves those numbers, the doctrine text does
not follow. Three live instances are catalogued in
[FINDINGS.md](FINDINGS.md) §11 and [LIMITATIONS.md](LIMITATIONS.md) §10,
including v7's claim 5, whose "(S3 excepted)" clause describes round-2 numbers
while the claim is labelled as resting on round-3 numbers, where the exception
does not hold.

**The countermeasure.** Not solved in this program, and stated as unsolved. The
partial countermeasure that did work is versioned, superseding baselines with
the older ones kept in the tree, so a reader can see exactly which numbers a
ruling was written against. What is missing is a checker that re-resolves every
number quoted in a baseline against the workstream's current results file —
the discipline that binds reports but was never extended to baselines.

### FM-11. A model that violates its own declared hardware limit

This is the one entry that has to be argued rather than asserted, because it is
the closest the record comes to catching wrong physics, and the guard rail on
this whole publication says the method does not do that.

**The instance.** The lead's own words, ratifying it:

> "ESC-WS8-10 is a PHYSICS DEFECT of record: the retard envelope never" [escws810_lead]
> re-solves when the buffer fills, so every simulated descent brakes
> "harder than the resistor can absorb — fix ordered in WS8 r4 and" [escws810_effect]
> inherited by WS9 r2.

The workstream that found it states it the same way:
"The retard envelope does not re-solve when the buffer pack fills, so every simulated descent lets a candidate brake harder than its resistor can absorb" [escws810_ws8].
The consequence is that every affected candidate's simulated descent speed is
optimistic, which moves trip time, which is a gate.

**Why it is still an internal inconsistency, not a physics validation.** Three
reasons, in order:

1. **The rating it violates is the model's own declared input.** The brake
   resistor's continuous rating is a parameter whose mass was charged to the
   candidate's payload elsewhere in the same pipeline. What was caught is the
   simulation contradicting a number it was given — not the simulation
   disagreeing with a measurement, because there is no measurement.
2. **It was surfaced by an escalation, not by adversarial review.** The round
   that found it declined to fix it under an order whose scope was declared
   exhaustive, and sent it up unresolved. That is the escalation path doing its
   job, which is a different mechanism from the adjudicator, and worth
   separating in any account of what the structure bought.
3. **It was never fixed.** The correcting round was ordered and then cancelled
   by the freeze. It is in [LIMITATIONS.md](LIMITATIONS.md) §8 as an open
   defect, not in this file as a success.

**The countermeasure.** Assert declared limits inside the integrator, per
sample, as hard failures rather than as post-hoc exports — the pattern WS8 r3
adopted for a different rule when it made a run fail outright if any 10 Hz
sample carried both compression-brake power and positive engine shaft power. A
limit that is only checked in the report is a limit the simulation is free to
break.

**And the honest generalisation.** This mode is the only bridge the record
offers between consistency checking and physical correctness, and it is a short
one: it catches models that break *their own stated* physics. It cannot catch a
model whose stated physics is wrong. That distinction is the whole content of
the guard rail.

---

## 6. The role the principal actually played

The strong version of "without being an engineer" is the true one, and it is
worth saying precisely which parts of the job the training would have covered
and which it would not.

**Engineering training was not required.** No hand calculation, no model, no
parameter choice and no verdict in this repository came from the principal. The
physics is in the workstream code; the criteria are in the baselines; the
verdicts are executed by the criteria.

**Physics literacy to read mechanisms was required.** Not to check arithmetic —
the adjudicators do that better — but to tell a mechanism from a story. When a
workstream reported that engine-off is worth **72.58 pp** [v1_engineoff_pp] against
a load-following genset and **0.25 pp** [v2_engineoff_pp] on the other duty, the
useful response is "those two disagree and the disagreement is a dispatch result,
not an architectural one", and that response requires understanding what a
genset dispatch is. The principal's two flagged instincts — waste-heat recovery
at a pinned genset, and the fuel/prime-mover question once a series path deletes
the duty cycle that mandated diesel — were both mechanism arguments, and both
were put on trial rather than adopted. One of them was subsequently dropped by
its own gate (claim 6 in [FINDINGS.md](FINDINGS.md)).

**Enforcing structure against one's own impatience was the actual job, and it is
the hard one.** In order of how much it cost:

1. **Separate contexts.** The lead never shares a session with the foreman; the
   foreman never shares one with a worker; the adjudicator has no history of the
   work. Every one of those separations costs latency and re-reading, and every
   one of them was worth it.
2. **No self-ratification.** Nothing below the lead ratifies. The lead ratifies
   in a chat that does not run production. This is slower than reading the
   report and saying "looks right", which is what the impulse is.
3. **Criteria written first.** See D1. The temptation to adjust a bar after
   seeing a near miss is strongest exactly when the bar is about to kill
   something you like.
4. **Adjudicators that cannot be argued with.** An adjudicator that could be
   argued with would have been argued with, seven times.

**And the counter-example, which belongs here rather than in a footnote.** The
one time the structure was cut, it was cut by the principal, under time
pressure, for defensible reasons — section 4. That is the honest shape of the
skill: it is not knowledge, it is the willingness to keep paying for a process
whose value only shows up as things you never find out were wrong.

---

## 7. What this method does not do

- It does not validate physics. Nothing here was measured against a real
  vehicle. The method **catches internal inconsistency, never wrong physics**.
  **Consistency is not validity.**
- It does not make an unvalidated model trustworthy by making it reproducible.
  Byte-stable regeneration is a property of the code, not of the world.
- It does not remove the need for domain judgement — it relocates it, into the
  criteria and the case sets, which are written before the numbers and are
  where the remaining human error lives.
- It does not scale down. Most of the cost here is the adjudication rounds and
  the separated contexts, and both are the parts that produced the findings.
- It has not been shown to generalise. One program, one domain, one principal.

---

## 8. If you want to run one of these

The minimum viable version of everything above, in the order it pays off:

1. **Write the kill criterion before the computation.** Numeric, with its
   statistic named. This is the single highest-value item and it is free.
2. **One entry point per workstream, deterministic, fixed seeds, and a verifier
   that re-resolves every reported number to its data file.** Without this the
   adjudicator has nothing to stand on.
3. **A fresh-context adjudicator that cannot edit, cannot be argued with, and
   writes findings to disk.** Budget for it to find things every time; the base
   rate in this program was seven for seven.
4. **Bounded rework with NOT CONVERGED as a legitimate outcome.** Otherwise the
   process optimises for the adjudicator's silence.
5. **Sweep for defect families, require clean-area reporting, then sample the
   clean certifications.** FM-1 and FM-4 together.
6. **Keep the escalation path unbroken.** Anything a worker cannot resolve goes
   up unresolved and unsoftened, and the layer that receives it does not run
   production.

The agent definitions this program used are in `.claude/agents/` and are part of
the record: `ws-worker.md` and `ws-adjudicator.md`. The program's operating rules
are in `CLAUDE.md`. The full production trail, including the foreman's own logged
rule breaches, is `PM_LOG.md`.

---

Statuses in this repository are exactly those of `BASELINE_v7_FREEZE.md`:
"Every verdict and number keeps the status it holds at freeze" [v7_r52],
"Nothing is promoted; nothing is quietly" [v7_r52b] demoted. Nothing in this
publication moves one.
