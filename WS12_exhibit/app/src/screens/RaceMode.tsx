import { useEffect, useMemo, useRef, useState } from 'react'
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
  TierBadge,
} from '../ui'
import { loadScrub } from '../trace'
import type { Loaded } from '../trace'
import type { Cited, TraceEntry } from '../types'

// LHV 42.8 kJ/g — WS4_genset/ws4_models.py:26, the program constant.
const LHV = 42.8

interface Run {
  km: Float64Array
  kwh: Float64Array
  n: number
  soc: Float64Array | null
  grade: Float64Array
  v: Float64Array
}

function integrate(d: Loaded, dt: number): Run {
  const v = d.col('v_kmh')
  const f = d.col('fuel_g_per_s')
  const km = new Float64Array(d.n)
  const kwh = new Float64Array(d.n)
  let m = 0
  let g = 0
  for (let i = 0; i < d.n; i++) {
    m += (v[i] / 3.6) * dt
    g += f[i] * dt
    km[i] = m / 1000
    kwh[i] = (g * LHV) / 3600
  }
  return {
    km,
    kwh,
    n: d.n,
    soc: d.ix['SOC'] !== undefined ? d.col('SOC') : null,
    grade: d.col('grade_pct'),
    v,
  }
}

function fmt(x: number, dp: number) {
  return x.toFixed(dp)
}

function Counter({
  title,
  value,
  unit,
  sub,
  color,
}: {
  title: string
  value: string
  unit: string
  sub?: string
  color?: string
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      <Label>{title}</Label>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
        <span
          style={{
            font: '400 26px/1 ' + F.mono,
            fontVariantNumeric: 'tabular-nums',
            color: color ?? C.text,
          }}
        >
          {value}
        </span>
        <span style={{ font: '400 10px/1 ' + F.mono, color: C.faint }}>
          {unit}
        </span>
      </div>
      {sub ? (
        <span style={{ font: '300 10px/1.4 ' + F.sans, color: C.faint }}>
          {sub}
        </span>
      ) : null}
    </div>
  )
}

function DecimationBadge({ path, badge }: { path: string; badge: string }) {
  return (
    <div
      style={{
        display: 'flex',
        gap: '10px',
        alignItems: 'center',
        flexWrap: 'wrap',
        padding: '7px 11px',
        border: '1px solid ' + C.mechanicalLine,
        background: C.mechanicalBg,
      }}
    >
      <span
        style={{
          font: '500 9.5px/1.4 ' + F.mono,
          letterSpacing: '.14em',
          color: C.mechanical,
        }}
      >
        {badge.toUpperCase()}
      </span>
      <span style={{ font: '400 9.5px/1.4 ' + F.mono, color: C.faint }}>
        {path}
      </span>
    </div>
  )
}

function RouteStrip({ a, pos }: { a: Run; pos: number }) {
  const W = 900
  const H = 104
  const built = useMemo(() => {
    const total = a.km[a.n - 1] || 1
    const step = Math.max(1, Math.floor(a.n / 900))
    let gmax = 0
    let vmax = 0
    for (let i = 0; i < a.n; i += step) {
      gmax = Math.max(gmax, Math.abs(a.grade[i]))
      vmax = Math.max(vmax, a.v[i])
    }
    gmax = Math.max(gmax, 0.5)
    vmax = Math.max(vmax, 1)
    let g = ''
    let v = ''
    for (let i = 0; i < a.n; i += step) {
      const x = (a.km[i] / total) * W
      g += (g ? ' L ' : 'M ') + x.toFixed(1) + ' ' +
        (H - 14 - (a.grade[i] / gmax) * (H / 2 - 14)).toFixed(1)
      v += (v ? ' L ' : 'M ') + x.toFixed(1) + ' ' +
        (H - 14 - (a.v[i] / vmax) * (H - 26)).toFixed(1)
    }
    return { g, v: v + ' L ' + W + ' ' + (H - 14) + ' L 0 ' + (H - 14) + ' Z',
             vLine: v, gmax, vmax, total }
  }, [a])
  const x = pos * W
  return (
    <div>
      <svg
        viewBox={'0 0 ' + W + ' ' + H}
        style={{ width: '100%', height: H + 'px', display: 'block' }}
        preserveAspectRatio="none"
      >
        <path d={built.v} fill="#141b21" />
        <path d={built.vLine} fill="none" stroke={C.electricalLine} strokeWidth={1} />
        <line
          x1={0}
          x2={W}
          y1={H - 14}
          y2={H - 14}
          stroke={C.ghost}
          strokeDasharray="3 3"
        />
        <path d={built.g} fill="none" stroke={C.mechanical} strokeWidth={1.2} />
        <line x1={x} x2={x} y1={0} y2={H} stroke={C.electrical} strokeWidth={1} />
      </svg>
      <div style={{ display: 'flex', gap: '18px', marginTop: '4px' }}>
        <span style={{ font: '400 9px/1.4 ' + F.mono, color: C.electricalLine }}>
          {'SPEED, PEAK ' + built.vmax.toFixed(1) + ' km/h'}
        </span>
        <span style={{ font: '400 9px/1.4 ' + F.mono, color: C.mechanical }}>
          {'GRADE, PEAK ' + built.gmax.toFixed(2) + ' %'}
        </span>
      </div>
    </div>
  )
}

function Pair({ p, traces, badge }: { p: any; traces: any; badge: string }) {
  const [cand, setCand] = useState<Run | null>(null)
  const [ruler, setRuler] = useState<Run | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [pos, setPos] = useState(0)
  const [playing, setPlaying] = useState(false)
  const raf = useRef(0)
  const t0 = useRef(0)
  const p0 = useRef(0)

  const tc: TraceEntry = traces[p.candTraceId]
  const tr: TraceEntry = traces[p.rulerTraceId]

  useEffect(() => {
    setCand(null)
    setRuler(null)
    setErr(null)
    setPos(0)
    setPlaying(false)
    let live = true
    Promise.all([loadScrub(tc), loadScrub(tr)])
      .then(([a, b]) => {
        if (!live) return
        // The scrub tier is 1 Hz: its own step is stride x the 10 Hz step.
        const dt = tc.stride * 0.1
        setCand(integrate(a, dt))
        setRuler(integrate(b, dt))
      })
      .catch((e) => live && setErr(String(e)))
    return () => {
      live = false
    }
  }, [p.id, tc, tr])

  useEffect(() => {
    if (!playing) return
    t0.current = performance.now()
    p0.current = pos
    const step = () => {
      const dt = (performance.now() - t0.current) / 1000
      const np = Math.min(1, p0.current + dt / 26)
      setPos(np)
      if (np >= 1) setPlaying(false)
      else raf.current = requestAnimationFrame(step)
    }
    raf.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing])

  if (err)
    return (
      <div style={{ padding: '20px', font: '400 12px/1.6 ' + F.mono, color: C.heat }}>
        {'The trace did not load: ' + err}
      </div>
    )
  if (!cand || !ruler)
    return (
      <div
        style={{
          padding: '20px',
          font: '400 10px/1.6 ' + F.mono,
          letterSpacing: '.2em',
          color: C.faint,
        }}
      >
        RESOLVING RECORD
      </div>
    )

  const i = Math.max(0, Math.min(cand.n - 1, Math.round(pos * (cand.n - 1))))
  const j = Math.max(0, Math.min(ruler.n - 1, Math.round(pos * (ruler.n - 1))))
  const payC = Number(p.payloadCand.v) / 1000
  const payR = Number(p.payloadRuler.v) / 1000

  const ckm = cand.km[i] > 0.02 ? cand.kwh[i] / cand.km[i] : 0
  const rkm = ruler.km[j] > 0.02 ? ruler.kwh[j] / ruler.km[j] : 0
  const cpt = cand.km[i] > 0.02 ? cand.kwh[i] / (cand.km[i] * payC) : 0
  const rpt = ruler.km[j] > 0.02 ? ruler.kwh[j] / (ruler.km[j] * payR) : 0
  const mKm = rkm > 0 ? (100 * (rkm - ckm)) / rkm : 0
  const mPt = rpt > 0 ? (100 * (rpt - cpt)) / rpt : 0
  const started = cand.km[i] > 0.05

  const done = pos >= 0.999

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* transport */}
      <div
        style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <button
          onClick={() => {
            if (pos >= 1) setPos(0)
            setPlaying(!playing)
          }}
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
          {playing ? 'PAUSE' : 'RUN'}
        </button>
        <button
          onClick={() => {
            setPlaying(false)
            setPos(0)
          }}
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
          RESET
        </button>
        <button
          onClick={() => {
            setPlaying(false)
            setPos(1)
          }}
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
          FINISH
        </button>
        <input
          type="range"
          min={0}
          max={1000}
          value={Math.round(pos * 1000)}
          onChange={(e) => {
            setPlaying(false)
            setPos(Number(e.target.value) / 1000)
          }}
          style={{ flex: 1, minWidth: '200px' }}
        />
        <span
          style={{
            font: '400 12px/1 ' + F.mono,
            fontVariantNumeric: 'tabular-nums',
            color: C.text3,
            minWidth: '92px',
            textAlign: 'right',
          }}
        >
          {fmt(cand.km[i], 2) + ' km'}
        </span>
      </div>

      <DecimationBadge badge={badge} path={tc.sourcePath} />

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
          <Label>THE ROUTE, FROM v_kmh AND grade_pct</Label>
          <span style={{ font: '300 9.5px/1.4 ' + F.sans, color: C.faint }}>
            {'z_m is absent from this file, so no elevation profile is drawn'}
          </span>
        </div>
        <RouteStrip a={cand} pos={pos} />
      </div>

      {/* the dual counters */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
          gap: '0',
          border: '1px solid ' + C.line,
        }}
      >
        <div
          style={{
            padding: '16px 18px',
            borderRight: '1px solid ' + C.line,
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <Kicker>COUNTER ONE — WHAT THE ROAD SEES</Kicker>
            <TierBadge tier="DERIVED" />
          </div>
          <div style={{ display: 'flex', gap: '26px', flexWrap: 'wrap' }}>
            <Counter
              title="STOCK NPR-HD"
              value={started ? fmt(rkm, 4) : '—'}
              unit="kWh/km"
            />
            <Counter
              title={p.vehicle}
              value={started ? fmt(ckm, 4) : '—'}
              unit="kWh/km"
              color={C.electrical}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Label>MARGIN, LIVE</Label>
              <span
                style={{
                  font: '400 13px/1 ' + F.mono,
                  fontVariantNumeric: 'tabular-nums',
                  color: mKm >= 0 ? C.electrical : C.heat,
                }}
              >
                {started ? (mKm >= 0 ? '+' : '') + fmt(mKm, 2) + '%' : '—'}
              </span>
            </div>
            <MarginBar value={started ? mKm : 0} scale={30} color={C.electrical} bar={16} />
          </div>
        </div>
        <div
          style={{
            padding: '16px 18px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <Kicker>COUNTER TWO — WHAT THE CUSTOMER SHIPS</Kicker>
            <TierBadge tier="DERIVED" />
          </div>
          <div style={{ display: 'flex', gap: '26px', flexWrap: 'wrap' }}>
            <Counter
              title="STOCK NPR-HD"
              value={started ? fmt(rpt, 4) : '—'}
              unit="kWh/t-km"
              sub={'payload ' + p.payloadRuler.s}
            />
            <Counter
              title={p.vehicle}
              value={started ? fmt(cpt, 4) : '—'}
              unit="kWh/t-km"
              color={mPt >= 0 ? C.text : C.heat}
              sub={'payload ' + p.payloadCand.s}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Label>MARGIN, LIVE — THE METRIC OF RECORD</Label>
              <span
                style={{
                  font: '400 13px/1 ' + F.mono,
                  fontVariantNumeric: 'tabular-nums',
                  color: mPt >= 0 ? C.text : C.heat,
                }}
              >
                {started ? (mPt >= 0 ? '+' : '') + fmt(mPt, 2) + '%' : '—'}
              </span>
            </div>
            <MarginBar
              value={started ? mPt : 0}
              scale={30}
              color={mPt >= 0 ? C.text2 : C.heat}
              bar={16}
            />
          </div>
        </div>
      </div>

      {/* the record */}
      <div
        style={{
          border: '1px solid ' + C.line,
          background: C.panelAlt,
          padding: '16px 18px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))',
          gap: '16px',
        }}
      >
        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '10px' }}>
          <Kicker>THE NUMBERS OF RECORD FOR THIS SEED</Kicker>
          <TierBadge tier="RECORD" />
        </div>
        {[
          ['RULER, PER KM', p.record.rulerPerKm],
          ['CANDIDATE, PER KM', p.record.candPerKm],
          ['MARGIN, PER KM', p.record.marginPerKm],
          ['MARGIN, PER PAYLOAD t-KM', p.record.marginPerPayload],
          ['THE GAP BETWEEN THEM', p.record.gapPp],
          ['ENSEMBLE-MIN, PER PAYLOAD', p.record.marginPerPayloadEnsembleMin],
        ].map(([k, v]) => (
          <div
            key={k as string}
            style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}
          >
            <Label>{k as string}</Label>
            <Num c={v as Cited} size={14} />
          </div>
        ))}
      </div>

      {/* reconciliation */}
      {done ? (
        <div
          style={{
            border: '1px solid ' + C.mechanicalLine,
            background: '#14110a',
            padding: '16px 18px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          <Kicker>{p.reconciliation.headline}</Kicker>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))',
              gap: '14px',
            }}
          >
            {[
              ['RULER, LIVE vs RECORD', p.reconciliation.rulerDeltaPct],
              ['CANDIDATE, LIVE vs RECORD', p.reconciliation.candDeltaPct],
              ['NET PACK ENERGY AT THE BUS', p.reconciliation.candNetPackBus],
              ['PACK STATE, START', p.derived.socStart],
              ['PACK STATE, END', p.derived.socEnd],
              ['IMPLIED BSFC FROM THIS FILE', p.reconciliation.candImpliedBsfc],
            ].map(([k, v]) => (
              <div
                key={k as string}
                style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}
              >
                <Label>{k as string}</Label>
                <Num c={v as Cited} size={13} />
              </div>
            ))}
          </div>
          {p.reconciliation.mechanisms.map((m: any) => (
            <div
              key={m.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                borderTop: '1px solid ' + C.lineSoft,
                paddingTop: '11px',
              }}
            >
              <Label>{'MECHANISM — APPLIES TO ' + m.applies}</Label>
              <Body style={{ fontSize: '12px' }}>{m.text}</Body>
              <span style={{ font: '400 10.5px/1.55 ' + F.mono, color: C.mechanical }}>
                {m.exampleLabel}
              </span>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))',
                  gap: '12px',
                }}
              >
                {m.rows.map((r: any) => (
                  <div
                    key={r.k}
                    style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                  >
                    <Label>{r.k}</Label>
                    <Num c={r.v} size={12} />
                  </div>
                ))}
              </div>
            </div>
          ))}
          <Body style={{ fontSize: '12px', color: C.faint }}>
            {p.reconciliation.residual}
          </Body>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))',
              gap: '14px',
              borderTop: '1px solid ' + C.lineSoft,
              paddingTop: '12px',
            }}
          >
            <div style={{ gridColumn: '1 / -1' }}>
              <Kicker>THE FULL 10 Hz INTEGRAL, FOR COMPARISON WITH THE 1 Hz REPLAY ABOVE</Kicker>
            </div>
            {[
              ['RULER, PER KM', p.derived.rulerPerKm],
              ['CANDIDATE, PER KM', p.derived.candPerKm],
              ['MARGIN, PER KM', p.derived.marginPerKm],
              ['MARGIN, PER PAYLOAD t-KM', p.derived.marginPerPayload],
              ['THE GAP BETWEEN THEM', p.derived.gapPp],
              ['DISTANCE', p.derived.candKm],
            ].map(([k, v]) => (
              <div
                key={k as string}
                style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}
              >
                <Label>{k as string}</Label>
                <Num c={v as Cited} size={13} />
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}

function SemiPanel({ s }: { s: any }) {
  return (
    <Panel>
      <PanelHead
        kicker="VEHICLE ONE · WS9"
        title={s.title}
        right={<StatusBadge s={s.statusBadge} />}
      />
      <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div
          style={{
            border: '1px solid ' + C.mechanicalLine,
            background: C.mechanicalBg,
            padding: '14px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '9px',
          }}
        >
          <span
            style={{
              font: '500 11px/1.4 ' + F.mono,
              letterSpacing: '.12em',
              color: C.mechanical,
            }}
          >
            {s.noReplay.headline.toUpperCase()}
          </span>
          <Body style={{ fontSize: '12.5px' }}>{s.noReplay.reason}</Body>
          <Quote c={s.noReplay.traceHeaderQuote} />
          <Body style={{ fontSize: '12px', color: C.faint }}>
            {s.noReplay.alsoAbsent}
          </Body>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {s.noReplay.tracesOnDisk.map((t: Cited) => (
              <Num key={t.file} c={t} size={10} />
            ))}
          </div>
        </div>

        <div style={{ border: '1px solid ' + C.lineSoft }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'minmax(200px,1.6fr) 90px minmax(110px,1fr) 90px 90px minmax(150px,1fr)',
              gap: '10px',
              padding: '9px 12px',
              background: C.panelAlt,
            }}
          >
            <Label>CANDIDATE</Label>
            <Label>DESIGN DUTY</Label>
            <Label>·</Label>
            <Label>CONTROL DUTY</Label>
            <Label>WORST CORNER</Label>
            <Label>STATUS</Label>
          </div>
          {s.rows.map((r: any) => (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'minmax(200px,1.6fr) 90px minmax(110px,1fr) 90px 90px minmax(150px,1fr)',
                gap: '10px',
                padding: '11px 12px',
                alignItems: 'center',
                borderTop: '1px solid ' + C.lineSoft,
              }}
            >
              <span style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <span style={{ font: '500 12px/1.3 ' + F.sans, color: C.text }}>
                  {r.id}
                </span>
                <span style={{ font: '300 10px/1.4 ' + F.sans, color: C.faint }}>
                  {r.title.s}
                </span>
              </span>
              <Num c={r.designMin} size={13} />
              <MarginBar
                value={r.designMin.v}
                scale={16}
                color={r.designMin.v >= 3 ? C.text2 : C.friction}
                threshold={3}
              />
              <Num c={r.controlMin} size={12} />
              <Num c={r.worstCorner} size={12} />
              <StatusBadge s={r.statusBadge} small />
            </div>
          ))}
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))',
            gap: '18px',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            <Label>THE CRITERION AND THE DUTIES</Label>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <Num c={s.criterionNominal} size={13} />
              <Num c={s.criterionCorner} size={13} />
              <Num c={s.designDuty} size={13} />
              <Num c={s.controlDuty} size={13} />
            </div>
            <span style={{ font: '300 11px/1.55 ' + F.sans, color: C.faint }}>
              {s.gatingRule.s}
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            <Label>WHY THESE STAY PROVISIONAL</Label>
            <Quote c={s.statusQuote} />
            <Quote c={s.openFindings} />
          </div>
        </div>
      </div>
    </Panel>
  )
}

export default function RaceMode({ d, bundle }: { d: any; bundle: any }) {
  const [sel, setSel] = useState<string>(d.pairs[0].id)
  const pair = d.pairs.find((p: any) => p.id === sel)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <div>
        <p
          style={{
            margin: '0 0 18px',
            maxWidth: '760px',
            font: '300 15px/1.65 ' + F.sans,
            color: C.text3,
          }}
        >
          {d.lede}
        </p>
        <Panel accent={C.electricalLine}>
          <div
            style={{
              padding: '18px 20px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))',
              gap: '20px',
              alignItems: 'start',
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <Label>V2 WINS, PER KILOMETRE</Label>
              <Num c={d.headline.perKm} size={30} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <Label>V2 LOSES, PER PAYLOAD TONNE-KM</Label>
              <Num c={d.headline.perPayload} size={30} color={C.heat} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <Label>THE FREIGHT IT HANDED BACK TO GET THERE</Label>
              <Num c={d.headline.freightGiven} size={30} color={C.mechanical} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <Body style={{ fontSize: '12.5px' }}>{d.headline.text}</Body>
              <Quote c={d.headline.trapQuote} />
            </div>
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelHead
          kicker="SELECT A PAIRED-SEED DATASET"
          title={pair.label}
          right={
            <span style={{ font: '400 10px/1.4 ' + F.mono, color: C.faint }}>
              {pair.sub}
            </span>
          }
        />
        <div
          style={{
            display: 'flex',
            gap: '8px',
            padding: '12px 20px',
            borderBottom: '1px solid ' + C.line,
            flexWrap: 'wrap',
          }}
        >
          {d.pairs.map((p: any) => {
            const on = p.id === sel
            return (
              <button
                key={p.id}
                onClick={() => setSel(p.id)}
                style={{
                  all: 'unset',
                  cursor: 'pointer',
                  padding: '6px 12px',
                  border: '1px solid ' + (on ? C.electricalLine : C.lineHard),
                  background: on ? C.electricalBg : 'transparent',
                  font: '400 10.5px/1.3 ' + F.mono,
                  color: on ? C.electricalLo : C.muted,
                }}
              >
                {p.vehicle + ' · ' + p.duty + ' · ' + p.case}
              </button>
            )
          })}
        </div>
        <div style={{ padding: '18px 20px' }}>
          <Pair
            key={pair.id}
            p={pair}
            traces={bundle.traces}
            badge={bundle.decimationBadge}
          />
        </div>
        <div
          style={{
            padding: '14px 20px',
            borderTop: '1px solid ' + C.line,
            font: '300 12px/1.65 ' + F.sans,
            color: C.faint,
          }}
        >
          {d.counterNote}
        </div>
      </Panel>

      <SemiPanel s={d.semi} />
    </div>
  )
}
