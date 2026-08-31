import { C, F } from '../theme'
import {
  Body,
  Kicker,
  Label,
  Num,
  Panel,
  PanelHead,
  Quote,
  StatusBadge,
  TierBadge,
} from '../ui'
import type { Cited } from '../types'

function Severity({
  b,
  m,
  mi,
}: {
  b: Cited
  m: Cited
  mi: Cited
}) {
  const cells: [string, Cited, string][] = [
    ['BLOCKING', b, C.heat],
    ['MATERIAL', m, C.mechanical],
    ['MINOR', mi, C.muted],
  ]
  return (
    <div style={{ display: 'flex', gap: '14px' }}>
      {cells.map(([k, v, col]) => (
        <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span
            style={{
              font: '400 8px/1 ' + F.mono,
              letterSpacing: '.16em',
              color: C.ghost,
            }}
          >
            {k}
          </span>
          <Num c={v} size={14} color={Number(v.v) > 0 ? col : C.ghost} />
        </div>
      ))}
    </div>
  )
}

function GapCard({ g }: { g: any }) {
  return (
    <Panel accent={C.heat}>
      <PanelHead
        kicker={g.kicker}
        title={g.title}
        right={<StatusBadge s={g.statusBadge} />}
      />
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
        }}
      >
        <div
          style={{
            padding: '18px 20px',
            borderRight: '1px solid ' + C.line,
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <Body>{g.body}</Body>
          <div
            style={{
              padding: '12px 14px',
              border: '1px solid ' + C.heat,
              background: '#1a0e0b',
              font: '500 13px/1.55 ' + F.sans,
              color: '#e8b0a0',
            }}
          >
            {g.controlLine}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
            <Label>WHAT ROUND 2 CLOSED, AND NOTHING CHECKED</Label>
            <Severity b={g.blocking} m={g.material} mi={g.minor} />
          </div>
        </div>
        <div
          style={{
            padding: '18px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <Label>FROM THE PROGRAM LOG, 2026-08-31</Label>
          <Quote c={g.logQuote} />
          <Quote c={g.consequenceQuote} />
          <Quote c={g.gateQuote} />
          <Quote c={g.nightReportQuote} />
        </div>
      </div>
    </Panel>
  )
}

function KXCard({ k }: { k: any }) {
  return (
    <Panel accent={'#5c4a6b'}>
      <PanelHead
        kicker={k.kicker}
        title={k.title}
        right={<StatusBadge s={k.statusBadge} />}
      />
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
        }}
      >
        <div
          style={{
            padding: '18px 20px',
            borderRight: '1px solid ' + C.line,
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))',
              gap: '14px',
            }}
          >
            {[
              ['R20 DESIGN POINT', k.designPoint],
              ['AT AMBIENT', k.designPointAmbient],
              ['R6 CORNER, 2-MIN RADIATOR', k.r6Radiator],
              ['EXCEEDANCE', k.exceedance],
              ['ENGINE REJECTION, 8-SEED MAX', k.r6Reject],
              ['RADIATOR PACKAGE SHARE', k.radiatorShare],
            ].map(([lab, v]) => (
              <div
                key={lab as string}
                style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}
              >
                <Label>{lab as string}</Label>
                <Num c={v as Cited} size={14} />
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <Label>THE CORNER, AS THE RESULTS FILE DEFINES IT</Label>
            <span style={{ font: '300 11.5px/1.55 ' + F.sans, color: C.text3 }}>
              {k.corner.s}
            </span>
          </div>
          <Quote c={k.findingQuote} />
        </div>
        <div
          style={{
            padding: '18px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <Kicker>{k.theCitationPoint.headline}</Kicker>
            <TierBadge tier="DERIVED" />
          </div>
          <Body>{k.theCitationPoint.body}</Body>
          <Quote c={k.theCitationPoint.consumerQuote} />
          <Quote c={k.statusQuote} />
          <Quote c={k.logQuote} />
          <Quote c={k.dispositionQuote} />
        </div>
      </div>
    </Panel>
  )
}

export default function RoundHistory({ d }: { d: any }) {
  const firsts = d.adjudications.filter((a: any) => a.firstPass)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <p
        style={{
          margin: 0,
          maxWidth: '780px',
          font: '300 15px/1.65 ' + F.sans,
          color: C.text3,
        }}
      >
        {d.lede}
      </p>

      <GapCard g={d.gap} />

      <Panel>
        <PanelHead
          kicker="EVERY ADJUDICATION ROUND IN THE PROGRAM"
          title="What the review found, round by round"
        />
        <div style={{ padding: '0' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '70px 70px minmax(220px,1fr) 230px 110px',
              gap: '12px',
              padding: '10px 20px',
              background: C.panelAlt,
              borderBottom: '1px solid ' + C.line,
            }}
          >
            <Label>WS</Label>
            <Label>ROUND</Label>
            <Label>VERDICT, VERBATIM</Label>
            <Label>SEVERITY</Label>
            <Label>FIRST PASS</Label>
          </div>
          {d.adjudications.map((a: any) => (
            <div
              key={a.ws + a.round}
              style={{
                display: 'grid',
                gridTemplateColumns: '70px 70px minmax(220px,1fr) 230px 110px',
                gap: '12px',
                padding: '13px 20px',
                borderBottom: '1px solid ' + C.lineSoft,
                alignItems: 'center',
                background: a.firstPass ? '#12181d' : 'transparent',
              }}
            >
              <span style={{ font: '500 12px/1 ' + F.mono, color: C.text }}>
                {a.ws}
              </span>
              <span style={{ font: '400 12px/1 ' + F.mono, color: C.text3 }}>
                {a.round}
              </span>
              <Quote c={a.verdictQuote} style={{ fontSize: '11.5px' }} />
              <Severity b={a.blocking} m={a.material} mi={a.minor} />
              <span
                style={{
                  font: '500 9px/1 ' + F.mono,
                  letterSpacing: '.14em',
                  color: a.firstPass ? C.electricalLo : C.ghost,
                }}
              >
                {a.firstPass ? 'FIRST PASS' : '—'}
              </span>
            </div>
          ))}
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE DETECTION RATE, WITH BOTH READINGS"
          title={d.defectRate.headline}
          right={<TierBadge tier="DERIVED" />}
        />
        <div
          style={{
            padding: '18px 20px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))',
            gap: '22px',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', gap: '26px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <Label>FIRST-PASS ROUNDS ON DISK</Label>
                <Num c={d.defectRate.firstPassRounds} size={30} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <Label>OF THOSE, FOUND A DEFECT</Label>
                <Num c={d.defectRate.firstPassWithDefects} size={30} />
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {firsts.map((a: any) => (
                <div
                  key={a.ws + a.round}
                  style={{
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'center',
                    font: '400 11px/1.4 ' + F.mono,
                    color: C.text3,
                  }}
                >
                  <span style={{ minWidth: '84px' }}>{a.ws + ' ' + a.round}</span>
                  <Num c={a.blocking} size={11} />
                  <Num c={a.material} size={11} />
                  <Num c={a.minor} size={11} />
                  <span style={{ color: C.faint }}>{a.file}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {d.defectRate.twoReadings.map((r: any) => (
              <div
                key={r.label}
                style={{
                  border: '1px solid ' + C.lineHard,
                  padding: '12px 14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <span
                  style={{
                    font: '500 14px/1.2 ' + F.sans,
                    color: C.text,
                    letterSpacing: '.01em',
                  }}
                >
                  {r.label}
                </span>
                <span style={{ font: '300 11.5px/1.55 ' + F.sans, color: C.text3 }}>
                  {r.scope}
                </span>
                <span style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}>
                  {r.source}
                </span>
              </div>
            ))}
            <Body style={{ fontSize: '12px' }}>{d.defectRate.discrepancyNote}</Body>
            <Body style={{ fontSize: '12px', color: C.faint }}>
              {d.defectRate.notCovered}
            </Body>
            <Quote c={d.defectRate.programClaim} />
          </div>
        </div>
      </Panel>

      <KXCard k={d.kx} />

      <Panel>
        <PanelHead
          kicker="PER WORKSTREAM"
          title="Rounds run, rounds reviewed, and the status each holds at the freeze"
        />
        <div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '70px minmax(160px,1fr) 80px 110px minmax(220px,1.4fr) minmax(200px,1fr)',
              gap: '12px',
              padding: '10px 20px',
              background: C.panelAlt,
              borderBottom: '1px solid ' + C.line,
            }}
          >
            <Label>WS</Label>
            <Label>NAME</Label>
            <Label>ROUNDS</Label>
            <Label>ADJUDICATED</Label>
            <Label>NOTE</Label>
            <Label>STATUS AT FREEZE</Label>
          </div>
          {d.workstreams.map((w: any) => (
            <div
              key={w.ws}
              style={{
                display: 'grid',
                gridTemplateColumns:
                  '70px minmax(160px,1fr) 80px 110px minmax(220px,1.4fr) minmax(200px,1fr)',
                gap: '12px',
                padding: '13px 20px',
                borderBottom: '1px solid ' + C.lineSoft,
                alignItems: 'start',
              }}
            >
              <span style={{ font: '500 12px/1.4 ' + F.mono, color: C.text }}>
                {w.ws}
              </span>
              <span style={{ font: '400 12px/1.4 ' + F.sans, color: C.text3 }}>
                {w.name}
              </span>
              <span style={{ font: '400 12px/1.4 ' + F.mono, color: C.text3 }}>
                {w.rounds}
              </span>
              <span
                style={{
                  font: '400 12px/1.4 ' + F.mono,
                  color: w.adjudications === 0 ? C.heat : C.text3,
                }}
              >
                {w.adjudications}
              </span>
              <span style={{ font: '300 11px/1.5 ' + F.sans, color: C.faint }}>
                {w.note}
              </span>
              <span style={{ font: '400 11px/1.5 ' + F.mono, color: C.text3 }}>
                {w.statusText}
              </span>
            </div>
          ))}
        </div>
      </Panel>

      <Panel accent={C.mechanicalLine}>
        <PanelHead
          kicker="THE HONEST GAP SET"
          title={d.neverAdjudicated.headline}
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '13px' }}>
          {d.neverAdjudicated.rows.map((r: any) => (
            <div
              key={r.ws + r.round}
              style={{
                display: 'grid',
                gridTemplateColumns: '90px 200px 1fr',
                gap: '14px',
                alignItems: 'start',
              }}
            >
              <span style={{ font: '500 12px/1.5 ' + F.mono, color: C.text }}>
                {r.ws}
              </span>
              <span style={{ font: '400 12px/1.5 ' + F.mono, color: C.text3 }}>
                {r.round}
              </span>
              <span style={{ font: '300 12px/1.55 ' + F.sans, color: C.text3 }}>
                {r.why}
              </span>
            </div>
          ))}
          <Body style={{ fontSize: '12px', color: C.faint }}>
            {d.neverAdjudicated.orderedNeverRun}
          </Body>
        </div>
      </Panel>
    </div>
  )
}
