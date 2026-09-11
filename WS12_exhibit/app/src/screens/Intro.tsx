import { C, F } from '../theme'
import { Body, Kicker, Label, Panel } from '../ui'

/**
 * The front door, in plain English.
 *
 * This screen carries no value of record. It has no entry in the data
 * bundle, no provenance row, no citation, no badge and no numeral — by
 * construction, not by omission. It exists so that a visitor arriving
 * cold learns what was asked and what came back before meeting a single
 * margin, and so that the limits of the answer are stated before the
 * answer is admired. Everything it says is argued, with its working
 * shown, on the screens that follow.
 */

function Head({ kicker, title }: { kicker: string; title: string }) {
  return (
    <header
      style={{
        padding: '16px 20px',
        borderBottom: '1px solid ' + C.line,
        display: 'flex',
        flexDirection: 'column',
        gap: '7px',
      }}
    >
      <Kicker>{kicker}</Kicker>
      <h2
        style={{
          margin: 0,
          maxWidth: '780px',
          font: '300 21px/1.25 ' + F.sans,
          letterSpacing: '-.01em',
          color: C.text,
          textWrap: 'pretty',
        }}
      >
        {title}
      </h2>
    </header>
  )
}

function Prose({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: '18px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '13px',
        maxWidth: '820px',
      }}
    >
      {children}
    </div>
  )
}

export default function Intro({
  setScreen,
}: {
  setScreen: (id: string) => void
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <p
        style={{
          margin: 0,
          maxWidth: '820px',
          font: '300 15px/1.65 ' + F.sans,
          color: C.text3,
          textWrap: 'pretty',
        }}
      >
        Project Volt put one question about trucks to a set of AI agents and
        made them answer it in the open. This screen is the question and the
        answer in plain English. Every screen after it is the working.
      </p>

      <Panel accent={C.mechanicalLine}>
        <Head
          kicker="THE QUESTION"
          title="A supercar that does without a gearbox. Does the same trick survive on a truck?"
        />
        <Prose>
          <Body>
            A Koenigsegg road car has no gearbox. An electric motor supplies
            the pull at low speed that a combustion engine cannot make on its
            own, so the engine never needs a set of ratios to hide behind. The
            car leaves a standstill on electricity, and the engine joins in
            once the road speed suits it.
          </Body>
          <Body>
            A truck's transmission is heavy, expensive and universal — every
            commercial truck on the road carries one. So the question was
            whether the supercar's arrangement survives being scaled up and
            put to work: can a truck run with an electric motor covering the
            low-speed pull, a single fixed ratio, and no gearbox at all?
          </Body>
        </Prose>
      </Panel>

      <Panel accent={C.electricalLine}>
        <Head
          kicker="WHAT CAME BACK"
          title="On a small delivery truck it works. On a heavy semi it cannot be made to work — and the reason is weight."
        />
        <Prose>
          <Body>
            On a small stop-go delivery truck the arrangement holds up. That
            duty is almost all pulling away and stopping again, which is what
            an electric motor is good at, and the gearbox turns out to have
            little left to do that the motor cannot do better.
          </Body>
          <Body>
            On a heavy long-haul semi it cannot be made to work at any single
            ratio. One fixed ratio has to serve both a motorway cruise and a
            loaded climb, and nothing sits in both places at once: choose for
            one and the other is out of reach. Covering the gap with more
            electrical machinery means carrying more machinery, and a truck
            that is already at its legal weight limit pays for every added
            kilogram in freight. The weight it gains comes out of the load it
            is paid to carry, and the trade does not close.
          </Body>
        </Prose>
      </Panel>

      <Panel accent={C.recordLine}>
        <Head
          kicker="HOW IT WAS RUN"
          title="By AI agents, inside a structure built to catch them out."
        />
        <Prose>
          <Body>
            The work was done by AI agents. The structure around them is the
            part worth describing.
          </Body>
          <Body>
            What would count as success was written down before any numbers
            existed, so no result could be judged against a bar moved to meet
            it. Each piece of work was then handed to a separate agent that
            had not done it, could not see the reasoning behind it, and had no
            stake in the answer — it read the files off disk and looked for
            reasons to reject them. Where it found one, the work went back
            rather than the objection being argued away.
          </Body>
          <Body>
            Everything the rest of this exhibit shows you resolves to a file
            and to a place inside that file. Click a figure and it tells you
            where it came from. A verifier re-opens the same file, re-derives
            the same figure, and refuses to let the site build if the two
            disagree.
          </Body>
        </Prose>
      </Panel>

      <Panel accent={C.heat}>
        <Head
          kicker="WHAT THIS DOES NOT DO"
          title="The method catches a program contradicting itself. It has never been shown to catch wrong physics."
        />
        <Prose>
          <Body>
            Every check here is a check for internal inconsistency: a claim
            that does not match its file, a bar that moved, a figure that two
            routes through the record do not agree on. If instead a shared
            assumption about the physical world is simply mistaken, every
            agent inherits it, every check still passes, and the answer is
            confidently wrong.
          </Body>
          <Body>
            Nothing here was built and nothing was measured. There is no
            truck, no test cell, no instrument reading. All of it is
            simulation against a model, and the model was never calibrated
            against a real vehicle. Read what follows as an argument with its
            working shown — not as a result from the road.
          </Body>
        </Prose>
      </Panel>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '11px',
          paddingBottom: '4px',
        }}
      >
        <Label>WHERE TO GO NEXT</Label>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setScreen('race')}
            style={{
              all: 'unset',
              cursor: 'pointer',
              padding: '7px 16px',
              border: '1px solid ' + C.electricalLine,
              background: C.electricalBg,
              font: '500 11px/1 ' + F.mono,
              letterSpacing: '.16em',
              color: C.electricalLo,
            }}
          >
            WATCH THE TWO TRUCKS
          </button>
          <button
            onClick={() => setScreen('verdict')}
            style={{
              all: 'unset',
              cursor: 'pointer',
              padding: '7px 14px',
              border: '1px solid ' + C.lineHard,
              font: '500 11px/1 ' + F.mono,
              letterSpacing: '.16em',
              color: C.muted,
            }}
          >
            SEE THE VERDICTS
          </button>
        </div>
      </div>
    </div>
  )
}
