import { C, F } from '../theme'
import {
  Body,
  Kicker,
  Label,
  MarginBar,
  Num,
  Panel,
  PanelHead,
  Quote,
  StatusBadge,
} from '../ui'
import type { Cited } from '../types'

function Lede({ children }: { children: string }) {
  return (
    <p
      style={{
        margin: '0 0 22px',
        maxWidth: '760px',
        font: '300 15px/1.65 ' + F.sans,
        color: C.text3,
        textWrap: 'pretty',
      }}
    >
      {children}
    </p>
  )
}

function Field({ k, v }: { k: string; v: Cited | undefined }) {
  if (!v) return null
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      <Label>{k}</Label>
      <Num c={v} size={13} />
    </div>
  )
}

// ------------------------------------------------------------- G1 waterfall

function Waterfall({ steps }: { steps: any[] }) {
  const W = 620
  const H = 216
  const base = 132
  const sc = 8.6
  const slot = (W - 40) / steps.length
  let run = 0
  const bars = steps.map((s, k) => {
    const x = 22 + k * slot
    const bw = slot - 26
    let y0: number
    let y1: number
    if (s.kind === 'start') {
      y0 = base
      y1 = base - s.value.v * sc
      run = s.value.v
    } else if (s.kind === 'end') {
      y0 = base
      y1 = base - s.value.v * sc
    } else {
      y0 = base - run * sc
      run += s.value.v
      y1 = base - run * sc
    }
    const top = Math.min(y0, y1)
    const h = Math.max(2, Math.abs(y1 - y0))
    return { x, bw, top, h, y1, s, neg: s.value.v < 0 }
  })
  return (
    <div style={{ overflowX: 'auto' }}>
      <svg
        viewBox={'0 0 ' + W + ' ' + H}
        style={{ width: '100%', minWidth: '520px', height: 'auto', display: 'block' }}
      >
        <line
          x1={12}
          x2={W - 12}
          y1={base}
          y2={base}
          stroke={C.ghost}
          strokeDasharray="3 3"
        />
        <line
          x1={12}
          x2={W - 12}
          y1={base - 5 * sc}
          y2={base - 5 * sc}
          stroke={C.electrical}
          strokeWidth={1}
        />
        <text
          x={W - 14}
          y={base - 5 * sc - 5}
          textAnchor="end"
          fill={C.electrical}
          style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
        >
          KILL CRITERION
        </text>
        {bars.map((b, k) => (
          <g key={k}>
            {k < bars.length - 1 ? (
              <line
                x1={b.x + b.bw}
                x2={b.x + slot}
                y1={b.y1}
                y2={b.y1}
                stroke={C.lineHard}
                strokeDasharray="2 2"
              />
            ) : null}
            <rect
              x={b.x}
              y={b.top}
              width={b.bw}
              height={b.h}
              fill={b.s.kind === 'step' ? '#39434f' : C.text2}
            />
            <text
              x={b.x + b.bw / 2}
              y={b.s.kind === 'step' ? b.top + b.h + 12 : b.top - 7}
              textAnchor="middle"
              fill={b.s.kind === 'step' ? C.text3 : C.text}
              style={{
                font: '400 10.5px ' + F.mono,
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {b.s.value.s}
            </text>
            <text
              x={b.x + b.bw / 2}
              y={H - 8}
              textAnchor="middle"
              fill={C.ghost}
              style={{ font: '400 8px ' + F.mono, letterSpacing: '.16em' }}
            >
              {String(k + 1).padStart(2, '0')}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

function CardG1({ c }: { c: any }) {
  return (
    <Panel accent={C.electricalLine}>
      <PanelHead
        kicker={c.kicker}
        title={c.title}
        right={<StatusBadge s={c.statusBadge} />}
      />
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(320px,1.15fr) minmax(280px,1fr)',
          gap: '0',
        }}
      >
        <div style={{ padding: '18px 20px', borderRight: '1px solid ' + C.line }}>
          <Waterfall steps={c.waterfall} />
          <div
            style={{
              marginTop: '10px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(150px,1fr))',
              gap: '10px 18px',
            }}
          >
            {c.waterfall.map((s: any, i: number) => (
              <div key={i} style={{ display: 'flex', gap: '8px' }}>
                <span
                  style={{
                    font: '400 8.5px/1.6 ' + F.mono,
                    color: C.ghost,
                    minWidth: '16px',
                  }}
                >
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ font: '500 11px/1.4 ' + F.sans, color: C.text2 }}>
                    {s.label}
                  </span>
                  <span
                    style={{ font: '300 10px/1.45 ' + F.sans, color: C.faint }}
                  >
                    {s.sub}
                  </span>
                </span>
              </div>
            ))}
          </div>
        </div>
        <div
          style={{
            padding: '18px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <Body>{c.body}</Body>
          <Quote c={c.criterionText} />
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(120px,1fr))',
              gap: '14px',
              paddingTop: '4px',
              borderTop: '1px solid ' + C.lineSoft,
            }}
          >
            <Field k="KILL CRITERION" v={c.criterion} />
            <Field k="MISSED BY" v={c.missedBy} />
            <Field k="SEEDS ABOVE ZERO" v={c.seedsPositive} />
            <Field k="SEEDS IN ENSEMBLE" v={c.seedsTotal} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <Label>GATE STATUS, AS THE RESULTS FILE RECORDS IT</Label>
            <Num c={c.gateStatus} size={12} />
          </div>
          <Quote c={c.statusQuote} />
        </div>
      </div>
    </Panel>
  )
}

// -------------------------------------------------------------- WS8 bars

function CardWS8({ c }: { c: any }) {
  const scale = 20
  return (
    <Panel>
      <PanelHead
        kicker={c.kicker}
        title={c.title}
        right={
          <>
            <StatusBadge s={c.statusBadge} />
            <StatusBadge s={c.numbersBadge} small />
          </>
        }
      />
      <div style={{ padding: '18px 20px' }}>
        <Body style={{ maxWidth: '740px', marginBottom: '18px' }}>{c.body}</Body>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: '2px',
            border: '1px solid ' + C.lineSoft,
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'minmax(140px,1.4fr) 80px minmax(120px,1fr) 80px minmax(120px,1fr) 90px',
              gap: '10px',
              padding: '9px 12px',
              background: C.panelAlt,
              alignItems: 'center',
            }}
          >
            <Label>CANDIDATE</Label>
            <Label>PER KM</Label>
            <Label>·</Label>
            <Label>PER PAYLOAD t-KM</Label>
            <Label>·</Label>
            <Label>VERDICT</Label>
          </div>
          {c.rows.map((r: any) => (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'minmax(140px,1.4fr) 80px minmax(120px,1fr) 80px minmax(120px,1fr) 90px',
                gap: '10px',
                padding: '11px 12px',
                alignItems: 'center',
                borderTop: '1px solid ' + C.lineSoft,
              }}
            >
              <span style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <span style={{ font: '500 12.5px/1.3 ' + F.sans, color: C.text }}>
                  {r.id + ' · ' + r.title}
                </span>
                <span style={{ font: '300 10px/1.4 ' + F.sans, color: C.faint }}>
                  {'worst corner '}
                  <Num c={r.worstCornerMin} size={10} />
                  {' at ' + r.worstCorner.s}
                </span>
              </span>
              <Num c={r.perKmMin} size={13} />
              <MarginBar value={r.perKmMin.v} scale={scale} color={C.electrical} />
              <Num c={r.perPayloadMin} size={13} />
              <MarginBar
                value={r.perPayloadMin.v}
                scale={scale}
                color={r.perPayloadMin.v >= 0 ? C.text2 : C.heat}
                threshold={c.criterionNominal.v}
              />
              <StatusBadge s={r.statusBadge} small />
            </div>
          ))}
        </div>
        <div
          style={{
            marginTop: '16px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))',
            gap: '18px',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <Label>THE CRITERION, PRE-COMMITTED</Label>
            <div style={{ display: 'flex', gap: '18px' }}>
              <Field k="NOMINAL" v={c.criterionNominal} />
              <Field k="EVERY CORNER" v={c.criterionCorner} />
              <Field k="NUMBERS VERSION" v={c.numbersVersion} />
            </div>
            <Quote c={c.statusQuote} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <Label>THE ROUND THAT PRODUCED THESE NUMBERS</Label>
            <Quote c={c.adjudicationQuote} />
            <Label>WASTE-HEAT RECOVERY GATE</Label>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <Field k="THRESHOLD" v={c.whr.threshold} />
              {c.whr.rows.map((w: any) => (
                <Field key={w.id} k={w.id + ' BEST NET'} v={w.best} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </Panel>
  )
}

// ------------------------------------------------------------- duty flip

function CardDuty({ c }: { c: any }) {
  const scale = 25
  return (
    <Panel>
      <PanelHead kicker={c.kicker} title={c.title} />
      <div style={{ padding: '18px 20px' }}>
        <Body style={{ maxWidth: '740px', marginBottom: '16px' }}>{c.body}</Body>
        <div style={{ border: '1px solid ' + C.lineSoft }}>
          {c.rows.map((r: any, i: number) => (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'minmax(180px,1.3fr) 78px minmax(110px,1fr) 78px minmax(110px,1fr) minmax(160px,0.9fr)',
                gap: '10px',
                padding: '12px',
                alignItems: 'center',
                borderTop: i ? '1px solid ' + C.lineSoft : 'none',
                background: r.statusBadge ? 'transparent' : C.panelAlt,
              }}
            >
              <span style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <span style={{ font: '500 12.5px/1.3 ' + F.sans, color: C.text }}>
                  {r.vehicle + ' on ' + r.duty}
                </span>
                <span style={{ font: '300 10px/1.4 ' + F.sans, color: C.faint }}>
                  {r.dutyName}
                </span>
              </span>
              <Num c={r.perKm} size={13} />
              <MarginBar value={r.perKm.v} scale={scale} color={C.electrical} />
              <Num c={r.perPayload} size={13} />
              <MarginBar
                value={r.perPayload.v}
                scale={scale}
                color={r.perPayload.v >= 0 ? C.text2 : C.heat}
              />
              <span style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                {r.statusBadge ? (
                  <StatusBadge s={r.statusBadge} small />
                ) : (
                  <span
                    style={{
                      font: '500 9px/1.4 ' + F.mono,
                      letterSpacing: '.14em',
                      color: C.mechanical,
                      border: '1px solid ' + C.mechanicalLine,
                      background: C.mechanicalBg,
                      padding: '3px 7px',
                    }}
                  >
                    {r.note}
                  </span>
                )}
                <span style={{ font: '300 9.5px/1.45 ' + F.sans, color: C.faint }}>
                  {r.noteWhy}
                </span>
              </span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: '14px', display: 'flex', gap: '18px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <Label>PER KM</Label>
            <span
              style={{
                width: '28px',
                height: '4px',
                background: C.electrical,
              }}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <Label>PER PAYLOAD TONNE-KM — THE METRIC OF RECORD</Label>
            <span style={{ width: '28px', height: '4px', background: C.text2 }} />
          </div>
        </div>
        <div style={{ marginTop: '16px' }}>
          <Quote c={c.claimQuote} />
        </div>
      </div>
    </Panel>
  )
}

// -------------------------------------------------------------- WS11 pair

function CardWS11({ c }: { c: any }) {
  return (
    <Panel>
      <PanelHead kicker={c.kicker} title={c.title} />
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
        }}
      >
        {c.rows.map((r: any) => (
          <div
            key={r.id}
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
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '12px',
              }}
            >
              <span style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span style={{ font: '500 14px/1.3 ' + F.sans, color: C.text }}>
                  {r.title}
                </span>
                <Kicker>{r.duty}</Kicker>
              </span>
              <StatusBadge s={r.statusBadge} small />
            </div>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit,minmax(110px,1fr))',
                gap: '14px',
              }}
            >
              <Field k="NOMINAL, ENSEMBLE-MIN" v={r.nominalMin} />
              <Field k="WORST CORNER" v={r.worstCorner} />
              <Field k="RULER AT ITS PESSIMISTIC END" v={r.pessimistic} />
              <Field k="RULER FUEL ERROR TO DRAW" v={r.flipPoint} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <Label>GOVERNING CASE</Label>
              <span style={{ font: '300 10.5px/1.5 ' + F.sans, color: C.faint }}>
                {r.worstCornerGoverning.s}
              </span>
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          padding: '18px 20px',
          borderTop: '1px solid ' + C.line,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))',
          gap: '20px',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Body>{c.body}</Body>
          <Quote c={c.statusQuote} />
          <Quote c={c.killQuote} />
        </div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            border: '1px solid ' + C.mechanicalLine,
            background: C.mechanicalBg,
            padding: '13px 15px',
          }}
        >
          <Label>{c.conditionality.headline}</Label>
          <span style={{ font: '400 11px/1.6 ' + F.mono, color: C.text3 }}>
            {c.conditionality.rulings}
          </span>
          <span
            style={{
              font: '500 11px/1.4 ' + F.mono,
              letterSpacing: '.1em',
              color: C.mechanical,
            }}
          >
            {c.conditionality.state}
          </span>
          <Body style={{ fontSize: '12px' }}>{c.conditionality.priced}</Body>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <Field
              k="V1 GOVERNING CORNER, ORDERED GATE"
              v={c.conditionality.orderedGateValue}
            />
            <Field
              k="WITH CAB HEAT AND CdA 5.4 TOGETHER"
              v={c.conditionality.bothPendingItems}
            />
          </div>
          <span style={{ font: '300 10.5px/1.5 ' + F.sans, color: C.faint }}>
            {c.conditionality.conditionedOn.s}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Label>ESC-1 — THE RULER WAS NEVER CALIBRATED</Label>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))',
              gap: '12px',
            }}
          >
            <Field k="MODEL, VOLT-SUB" v={c.esc1.modelLper100} />
            <Field k="PUBLIC ANCHOR, ERA SUBSET" v={c.esc1.anchorLper100} />
            <Field k="WORST RESIDUAL" v={c.esc1.worstResidual} />
            <Field k="CALIBRATION PERFORMED" v={c.esc1.calibrateOrderSatisfied} />
          </div>
          <span style={{ font: '300 11px/1.6 ' + F.sans, color: C.faint }}>
            {c.esc1.anchorName.s}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <Label>{c.reworkUnverified.headline}</Label>
          <Quote c={c.reworkUnverified.quote} />
        </div>
      </div>
    </Panel>
  )
}

export default function VerdictWall({ d }: { d: any }) {
  const map: Record<string, (p: { c: any }) => JSX.Element> = {
    g1: CardG1,
    ws8: CardWS8,
    duty: CardDuty,
    ws11: CardWS11,
  }
  return (
    <div>
      <Lede>{d.lede}</Lede>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
        {d.cards.map((c: any) => {
          const Cmp = map[c.id]
          return <Cmp key={c.id} c={c} />
        })}
      </div>
    </div>
  )
}
