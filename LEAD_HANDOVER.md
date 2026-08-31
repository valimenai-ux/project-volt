# LEAD_HANDOVER — PROJECT VOLT LEAD ROLE TRANSFER (2026-08-30)

To the incoming lead (Cowork session, Fable). This memo transfers the
lead role from the claude.ai lead chat to you: full authority, the
operating doctrine, the state of the board, the open rulings queue,
and the bands currently pre-registered. Read this, then the
highest-numbered BASELINE, then PM_COWORK.md. Vali (the user) is the
principal and final decision-maker on scope; you are the lead.

## 1. Your authority
You ratify workstream reports, rule on escalations (citing and
numbering rulings R25 onward), decide gates and kill clauses, bump
the BASELINE by version, cut ASSIGNMENT.md and *_DIRECTIVE.md files,
set strategy and candidate waves, edit charters (including
PM_COWORK.md — first housekeeping act: change its "the lead is a
separate chat" to "a separate Cowork session, see LEAD_HANDOVER.md"),
and authorize Fable usage. The principal can overrule any ruling.
You do NOT run production: no launching workers, no mechanical gates,
no adjudicator launches except lead-supervised kill reviews you
explicitly designate. The foreman does that and hands you
PM_PACKET_WSn.md files. Never share a session or context with the
foreman or any worker. Disk is the only interface.

## 2. Doctrine — what this program learned, in the order it hurt
D1. Pre-commit, then measure. Every gate has a numeric kill criterion
    written BEFORE the computation. G1 (the V2 lockup clutch) was
    killed by its own pre-committed criterion after the first pass
    "passed" under a flawed convention. The criterion could not be
    negotiated with. Keep it that way.
D2. Pre-register acceptance bands before reading any report, and
    keep them where workers cannot read them. The former lead kept
    them in chat. You live on disk, so use the PRIVATE folder
    ../Project Volt Lead/ (outside the repo, never committed, never
    granted to the foreman): PREREGISTRATION.md, dated entries. The
    bands are a calibration instrument for YOU — misses locate errors
    in your priors; they never override a ratified number.
D3. Convention swaps are level shifts, not perturbations. The lead
    pre-registered G1-R at +4 to +6% and it came in at -2.58%,
    because a chain-convention correction moved the whole baseline of
    the comparison. When a ruling changes how something is counted,
    widen bands drastically and expect sign changes.
D4. Artifacts on disk are the record; prose is not. The lead once
    said "WS8 is cut and on disk" without writing it; a migration
    session's mechanical check caught it. Never claim an artifact
    exists without having verified it. The same rule that binds
    workers binds you.
D5. Every first-pass adjudication in this program (WS1-WS4) found
    material or blocking defects, almost all in interfaces, member
    selection, and definitional blurs, not physics. Nothing kill-
    bearing is ratified unadjudicated. Adjudicators are fresh-context
    and disk-only (see .claude/agents/ws-adjudicator.md).
D6. Program conventions (rulings R9, R12, R14): 8-seed ensembles for
    stochastic extrema; part-load maps, never peak-point scalars;
    electrical quantities bus-side, one chain convention; every
    machine-readable worst-case field is an explicit max/min over an
    enumerated, governing-case-labeled set; escalations cite the
    ruling challenged and are never self-resolved.
D7. Novelty is not merit. Prior-art occupancy answers "has anyone
    done it"; the trial answers "does it beat the incumbent". Never
    confuse them. Also: unoccupied territory sometimes has a physics
    reason (S3).
D8. The two walls at semi scale (from WS8 flight data, pending
    ratification): (i) a single fixed engine ratio cannot span
    105 km/h cruise and a 6% grade at 36.3 t — about a 2:1 ratio span
    is physically mandatory on any engine path; (ii) at fixed gross
    weight every powertrain kilogram displaces payload 1:1, so the
    metric of record is fuel energy per PAYLOAD tonne-km, and the
    objective function is efficiency per added kilogram. Zero-mass
    levers first.
D9. The transmissionless premise has a mass boundary: total electric
    torque-fill won at 6.6 t (Vehicle Zero, both variants pure series
    after the G1 kill); at 36.3 t the same falsifier says at least two
    ratios or full series with its conversion tax. Measuring where the
    boundary lies is itself a program result.
D10. Budget policy of record (Fable was at ~76% on 2026-08-29): lead
    on Fable; foreman Opus; workers Opus; mechanical work Sonnet;
    adjudicators Opus except kill-decision reviews, which you may
    designate Fable. Spend Fable where a missed defect executes a
    wrong verdict, nowhere else.
D11. Product claims get verified before they are relied on. The lead
    twice sent the principal hunting for a "GitHub connector" that
    does not exist. Check docs; test access paths empirically.
D12. Economics is out of scope by the principal's charter; energy,
    emissions, mass, and physics are in. When the principal's
    instinct smuggles in a price argument, keep the physics half and
    say plainly which half was set aside.

## 3. Standing mandate from the principal (2026-08-29)
"Continue to ponder and think about the best solution to iterate to
something that is actually a genuinely more efficient powertrain for
trucks than what's used today. If that's this system, great; if not,
continue thinking outside the box." Candidates go on trial; nothing is
adopted by vibe. The principal flagged two instincts that the lead
ruled SIGNAL: waste-heat recovery (nearly payload-free; a pinned-point
genset is the one truck host where bottoming cycles work) and the
fuel/prime-mover question (a series genset deletes the duty cycle that
mandated diesel; Atkinson petrol likely beats the V1 diesel genset
outright, parity at V2, diesel/gas hold at semi scale and wherever the
engine touches wheels).

## 4. State of the board (2026-08-30)
- Repo: github.com/valimenai-ux/project-volt, PRIVATE, main ==
  origin/main at the WS8 merge. Cloud sessions push branches; the
  foreman owns pull/merge/push hygiene.
- Vehicle Zero (Isuzu NPR-HD, BASELINE_v3): V1 Postal and V2 Trucker
  are both pure series; clutch deleted by G1-R (-2.58% ensemble-min,
  sign reversed, invariant under accounting). WS1-WS4 closed/ratified.
  OPEN and unlaunched: WS4_genset/KX_DIRECTIVE.md, WS5_controls,
  WS6_packaging — foreman's tasking per PM_COWORK.md. WS7 (prototype
  and test plan) not yet cut; its accumulated items are listed in
  BASELINE_v3.
- Vehicle One (Class 8, WS8_semi_architecture): REPORT_WS8.md landed
  (1,588 lines, results_ws8.json, PRIOR_ART_WS8.md); worker headline
  "no candidate advances". NOT ADJUDICATED — FINDINGS_WS8_r1.md is
  missing. A Fable adjudication launch prompt with six lead-priority
  re-derivation targets was issued to the principal; if absent, issue
  it again (targets: S3 infeasibility at both engine torques; payload-
  denominator arithmetic; per-seed reproduction of every advance/kill
  margin vs the >=3% nominal / >=0% corners criteria; S0 calibration
  vs 30-38 L/100 km; WHR gate after mass charge; presence of the
  weight-allowance sensitivity in Escalations).

## 5. Open rulings queue, in order
Q1. WS8 ratification after adjudication: kill or spare S1-S4; the WHR
    gate; disposition of every escalation; BASELINE_v4 with a Vehicle
    One section. Execute kills on the pre-committed criteria only.
Q2. Cut WS9 (Vehicle One, wave two) under the two walls, same
    criteria (>=3% per payload tonne-km nominal, >=0% every corner):
    S5 minimal transmission (2-speed dog box, motor-synchronized
    shifts, torque-fill through the shift, lean motor + buffer sized
    for launch/regen/descent only); S6 zero-mass stack (mechanical
    drive; opposed-piston-class engine, turbocompound WHR, predictive
    energy management; also the control for "how far without
    electrification"); S7 marginal-mass electrification (motorize an
    existing trailer axle; only motor/inverter/small buffer are new
    mass); plus the prime-mover-at-the-pin task (diesel vs Atkinson
    petrol vs natural gas at the pinned point, judged on efficiency
    and engine+aftertreatment+tank mass, energy and emissions only)
    and a weight-allowance policy sensitivity (sensitivity, not
    salvation).
Q3. WS7 for Vehicle Zero when WS5/WS6 packets ratify.
Q4. The former lead's prior: S6 clears the bar; S5 is the live
    question; if both clear, "two gears, lean motors, recovered heat"
    is probably the truck. Treat as a prior to be tested, not a
    conclusion.

## 6. Bands currently on record (former lead, pre-WS8-adjudication)
S0 calibrates to 30-38 L/100 km loaded line-haul; S1 loses to S0 on
line-haul by 2-9%; S3 lands -1 to +8% on the fleet mission (flight
data now says structurally infeasible — the band was wrong for the
right reason, D3); WHR harvests 2-6% gross before mass charge; prior-
art scan finds adjacent filings but no shipped program with a
transmissionless ICE axle. Log your own bands in the private folder
before you open REPORT_WS8.md.

## 7. How the principal works with you
Terse, directive, accepts corrections readily, has a neuroscience
background and no engineering training but reads physics fluently —
explain mechanisms, never hand-wave. Answer status questions from
PM_LOG.md and packet facts. When a ruling is a program fork
(new vehicle class, premise change), present it and ask for
ratification; when it is inside the charter, rule and record. The
former lead chat remains available to the principal as an optional
second opinion on kill decisions; it has no authority over you.
