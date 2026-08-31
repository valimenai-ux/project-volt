import { useEffect, useState } from 'react'
import { C, F } from './theme'
import { CitationSheet, CiteProvider, Label } from './ui'
import type { Bundle } from './types'
import VerdictWall from './screens/VerdictWall'
import RaceMode from './screens/RaceMode'
import RoundHistory from './screens/RoundHistory'
import Simulator from './screens/Simulator'
import Sandbox from './screens/Sandbox'
import Method from './screens/Method'

const RAIL = [
  { id: 'verdict', n: '01', name: 'Verdict wall', sub: 'criteria, and what came back' },
  { id: 'race', n: '02', name: 'Race mode', sub: 'two counters, one road' },
  { id: 'rounds', n: '03', name: 'Round history', sub: 'what the review caught' },
  { id: 'sim', n: '04', name: 'Simulator', sub: 'a trace file, played back' },
  { id: 'sandbox', n: '05', name: 'Sandbox', sub: 'where the boundary lies' },
  { id: 'method', n: '06', name: 'Method', sub: 'claims, tiers, sources' },
]

const MODE_BADGE: Record<string, string> = {
  verdict: 'RECORD',
  race: 'RECORD REPLAY · PAIRED SEED',
  rounds: 'RECORD',
  sim: 'RECORD REPLAY · TRACE_SCHEMA',
  sandbox: 'SANDBOX · SIMPLIFIED PHYSICS',
  method: 'REFERENCE',
}

export default function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [screen, setScreen] = useState('verdict')

  useEffect(() => {
    const hash = window.location.hash.replace('#', '')
    if (RAIL.some((r) => r.id === hash)) setScreen(hash)
    fetch(import.meta.env.BASE_URL + 'data/exhibit_data.json')
      .then((r) => {
        if (!r.ok) throw new Error('HTTP ' + r.status)
        return r.json()
      })
      .then(setBundle)
      .catch((e) => setErr(String(e)))
  }, [])

  useEffect(() => {
    window.location.hash = screen
  }, [screen])

  if (err)
    return (
      <div style={{ padding: '40px', font: '400 14px/1.6 ' + F.mono }}>
        {'The data bundle did not load: ' + err}
      </div>
    )
  if (!bundle)
    return (
      <div
        style={{
          padding: '40px',
          font: '400 11px/1.6 ' + F.mono,
          letterSpacing: '.2em',
          color: C.faint,
        }}
      >
        RESOLVING RECORD
      </div>
    )

  const S = bundle.screens[screen]
  const prov = bundle.provenance.screens[screen]

  return (
    <CiteProvider>
      <div
        style={{
          minHeight: '100vh',
          background: C.canvas,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* header */}
        <header
          style={{
            flex: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            padding: '0 22px',
            height: '62px',
            borderBottom: '1px solid ' + C.line,
            background: C.header,
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <div
              style={{
                font: '700 14px/1 ' + F.sans,
                letterSpacing: '.22em',
                color: C.text,
              }}
            >
              PROJECT VOLT
            </div>
            <div
              style={{
                font: '400 9px/1 ' + F.mono,
                letterSpacing: '.2em',
                color: C.faint,
              }}
            >
              DRIVETRAIN TRIALS · THE METHOD, MADE CLICKABLE
            </div>
          </div>
          <div style={{ width: '1px', height: '28px', background: C.lineHard }} />
          <div
            style={{
              font: '500 11px/1 ' + F.sans,
              letterSpacing: '.14em',
              color: C.muted,
              textTransform: 'uppercase',
            }}
          >
            {S.title}
          </div>
          <div style={{ flex: 1 }} />
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '7px',
              padding: '5px 11px',
              border: '1px solid ' + C.electricalLine,
              background: C.electricalBg,
            }}
          >
            <span
              style={{
                width: '5px',
                height: '5px',
                background: C.electrical,
                borderRadius: '50%',
              }}
            />
            <span
              style={{
                font: '500 9.5px/1 ' + F.mono,
                letterSpacing: '.18em',
                color: C.electricalLo,
              }}
            >
              {MODE_BADGE[screen]}
            </span>
          </div>
          <div
            style={{
              font: '400 10px/1 ' + F.mono,
              color: C.fainter,
              letterSpacing: '.08em',
            }}
          >
            {bundle.meta.baselineLabel}
          </div>
        </header>

        <div style={{ flex: 1, display: 'flex', minHeight: 0, flexWrap: 'wrap' }}>
          {/* rail */}
          <nav
            style={{
              width: '232px',
              flex: 'none',
              borderRight: '1px solid ' + C.line,
              background: C.rail,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div style={{ padding: '16px 16px 8px' }}>
              <Label>NARRATIVE RAIL</Label>
            </div>
            {RAIL.map((r) => {
              const on = r.id === screen
              return (
                <button
                  key={r.id}
                  onClick={() => setScreen(r.id)}
                  style={{
                    all: 'unset',
                    cursor: 'pointer',
                    display: 'grid',
                    gridTemplateColumns: '24px 1fr',
                    gap: '10px',
                    padding: '11px 16px',
                    borderLeft:
                      '2px solid ' + (on ? C.electrical : 'transparent'),
                    background: on ? '#151d24' : 'transparent',
                  }}
                >
                  <span
                    style={{
                      font: '400 10px/1.4 ' + F.mono,
                      color: on ? C.electrical : C.ghost,
                      paddingTop: '2px',
                    }}
                  >
                    {r.n}
                  </span>
                  <span
                    style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}
                  >
                    <span
                      style={{
                        font: '500 12.5px/1.25 ' + F.sans,
                        color: on ? C.text : C.text3,
                      }}
                    >
                      {r.name}
                    </span>
                    <span
                      style={{
                        font: '400 9.5px/1.35 ' + F.mono,
                        color: C.fainter,
                      }}
                    >
                      {r.sub}
                    </span>
                  </span>
                </button>
              )
            })}
            <div style={{ flex: 1 }} />
            <div
              style={{
                padding: '14px 16px',
                borderTop: '1px solid ' + C.lineSoft,
                display: 'flex',
                flexDirection: 'column',
                gap: '9px',
              }}
            >
              <Label>GUARD RAILS</Label>
              <div
                style={{
                  font: '300 10.5px/1.5 ' + F.sans,
                  color: C.faint,
                }}
              >
                {bundle.guardRails.methodClaim.headline}
                {' — never '}
                {bundle.guardRails.methodClaim.neverClaims}
              </div>
              <div
                style={{
                  font: '300 10.5px/1.5 ' + F.sans,
                  color: C.faint,
                }}
              >
                {bundle.guardRails.noPromotion.headline}
              </div>
            </div>
          </nav>

          {/* main */}
          <main
            style={{
              flex: 1,
              minWidth: '320px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div style={{ flex: 1, padding: '26px 26px 8px' }}>
              {screen === 'verdict' ? <VerdictWall d={S} /> : null}
              {screen === 'race' ? <RaceMode d={S} bundle={bundle} /> : null}
              {screen === 'rounds' ? <RoundHistory d={S} /> : null}
              {screen === 'sim' ? <Simulator d={S} bundle={bundle} /> : null}
              {screen === 'sandbox' ? <Sandbox d={S} /> : null}
              {screen === 'method' ? <Method d={S} bundle={bundle} /> : null}
            </div>

            {/* provenance strip — read from the record, never hard-coded */}
            <footer
              style={{
                flex: 'none',
                borderTop: '1px solid ' + C.line,
                background: C.header,
                padding: '10px 26px',
                display: 'flex',
                gap: '26px',
                flexWrap: 'wrap',
              }}
            >
              {[
                ['BASELINE', bundle.provenance.baseline.label],
                ['RESULTS FILE', prov.resultsFile],
                ['CRITERION', prov.criterion],
                ['SEED', prov.seed],
                ['CORNER', prov.corner],
              ].map(([k, v]) => (
                <div
                  key={k}
                  style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                >
                  <span
                    style={{
                      font: '400 8.5px/1 ' + F.mono,
                      letterSpacing: '.2em',
                      color: C.ghost,
                    }}
                  >
                    {k}
                  </span>
                  <span
                    style={{ font: '400 10.5px/1.3 ' + F.mono, color: C.text3 }}
                  >
                    {v}
                  </span>
                </div>
              ))}
            </footer>
          </main>
        </div>
        <CitationSheet />
      </div>
    </CiteProvider>
  )
}
