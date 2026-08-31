import { useEffect, useMemo, useRef, useState } from 'react'
import { C, F } from '../theme'
import {
  Body,
  Label,
  Num,
  Panel,
  PanelHead,
  Quote,
  StatusBadge,
  TierBadge,
} from '../ui'
import { loadScrub, loadSegment, validateLoaded } from '../trace'
import type { Loaded, RunCheck } from '../trace'
import type { Cited, RegistryRow, TraceEntry } from '../types'

// ------------------------------------------------------------ BSFC map

interface Bsfc {
  rpm: number[]
  tq: number[][]
  bs: number[][]
  rpmMin: number
  rpmMax: number
  tqMax: number
  bsMin: number
  header: string[]
}

async function loadBsfc(name: string): Promise<Bsfc> {
  const r = await fetch(import.meta.env.BASE_URL + 'maps/' + name)
  const txt = await r.text()
  const header: string[] = []
  const rpm: number[] = []
  const tq: number[][] = []
  const bs: number[][] = []
  let seenHead = false
  let cur = -1
  for (const line of txt.split('\n')) {
    if (!line) continue
    if (line.startsWith('#')) {
      header.push(line.slice(1).trim())
      continue
    }
    if (!seenHead) {
      seenHead = true
      continue
    }
    const f = line.split(',')
    const rp = +f[0]
    if (cur < 0 || rpm[cur] !== rp) {
      rpm.push(rp)
      tq.push([])
      bs.push([])
      cur = rpm.length - 1
    }
    tq[cur].push(+f[1])
    bs[cur].push(+f[2])
  }
  let tqMax = 0
  let bsMin = Infinity
  for (let i = 0; i < rpm.length; i++)
    for (let j = 0; j < tq[i].length; j++) {
      tqMax = Math.max(tqMax, tq[i][j])
      bsMin = Math.min(bsMin, bs[i][j])
    }
  return {
    rpm,
    tq,
    bs,
    rpmMin: rpm[0],
    rpmMax: rpm[rpm.length - 1],
    tqMax,
    bsMin,
    header,
  }
}

function ramp(v: number, lo: number, hi: number) {
  // The BSFC island is where the engine is cheap; everything outside it is
  // progressively expensive. Cyan at the island, slate at the edges, on one
  // scale, with no colour used for emphasis anywhere else on this screen.
  const t = Math.max(0, Math.min(1, (v - lo) / (hi - lo)))
  const e = Math.pow(t, 0.65)
  const r = Math.round(26 + e * 30)
  const g = Math.round(196 - e * 150)
  const b = Math.round(214 - e * 154)
  return 'rgb(' + r + ',' + g + ',' + b + ')'
}

function BsfcMap({
  map,
  rpm,
  tq,
  on,
}: {
  map: Bsfc | null
  rpm: number
  tq: number
  on: boolean
}) {
  const W = 420
  const H = 250
  if (!map)
    return (
      <div style={{ height: H + 'px', display: 'grid', placeItems: 'center' }}>
        <span style={{ font: '400 10px ' + F.mono, color: C.faint }}>
          RESOLVING MAP
        </span>
      </div>
    )
  const x = (r: number) =>
    28 + ((r - map.rpmMin) / (map.rpmMax - map.rpmMin)) * (W - 40)
  const y = (t: number) => H - 26 - (t / map.tqMax) * (H - 40)
  const hi = map.bsMin * 1.28
  const cells: JSX.Element[] = []
  for (let i = 0; i < map.rpm.length; i += 2) {
    const x0 = x(map.rpm[i])
    const x1 = x(map.rpm[Math.min(i + 2, map.rpm.length - 1)])
    const w = Math.max(1, x1 - x0)
    const col = map.tq[i]
    for (let j = 0; j < col.length; j += 3) {
      const y0 = y(col[Math.min(j + 3, col.length - 1)])
      const y1 = y(col[j])
      cells.push(
        <rect
          key={i + '_' + j}
          x={x0}
          y={y0}
          width={w}
          height={Math.max(1, y1 - y0)}
          fill={ramp(map.bs[i][j], map.bsMin, hi)}
        />,
      )
    }
  }
  return (
    <svg
      viewBox={'0 0 ' + W + ' ' + H}
      style={{ width: '100%', height: 'auto', display: 'block' }}
    >
      {cells}
      <line x1={28} x2={W - 12} y1={H - 26} y2={H - 26} stroke={C.lineHard} />
      <line x1={28} x2={28} y1={14} y2={H - 26} stroke={C.lineHard} />
      {on ? (
        <g>
          <circle cx={x(rpm)} cy={y(tq)} r={5} fill={C.mechanical} />
          <circle
            cx={x(rpm)}
            cy={y(tq)}
            r={9}
            fill="none"
            stroke={C.mechanical}
            strokeWidth={0.8}
          />
        </g>
      ) : null}
      <text
        x={W - 12}
        y={H - 10}
        textAnchor="end"
        fill={C.fainter}
        style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
      >
        ENGINE SPEED
      </text>
      <text
        x={30}
        y={12}
        fill={C.fainter}
        style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
      >
        TORQUE
      </text>
      {on ? null : (
        <text
          x={W / 2}
          y={H / 2}
          textAnchor="middle"
          fill={C.faint}
          style={{ font: '400 10px ' + F.mono, letterSpacing: '.2em' }}
        >
          ENGINE OFF
        </text>
      )}
    </svg>
  )
}

// ---------------------------------------------------------- power flow

interface Flow {
  from: [number, number]
  to: [number, number]
  kW: number
  color: string
  label: string
}

const FLOW_NODES: { x: number; y: number; label: string; anchor: string }[] = [
  { x: 40, y: 60, label: 'TANK', anchor: 'start' },
  { x: 170, y: 60, label: 'ENGINE', anchor: 'middle' },
  { x: 300, y: 40, label: 'PACK', anchor: 'middle' },
  { x: 300, y: 110, label: 'BUS', anchor: 'middle' },
  { x: 430, y: 110, label: 'MOTOR', anchor: 'middle' },
  { x: 575, y: 110, label: 'WHEELS', anchor: 'end' },
  { x: 300, y: 180, label: 'ACCESSORIES', anchor: 'middle' },
  { x: 180, y: 180, label: 'CABIN HEAT', anchor: 'end' },
  { x: 180, y: 225, label: 'BRAKE RESISTOR', anchor: 'end' },
  { x: 575, y: 190, label: 'FRICTION BRAKE', anchor: 'end' },
]

function PowerFlow({ flows, scale }: { flows: Flow[]; scale: number }) {
  const W = 640
  const H = 260
  return (
    <svg
      viewBox={'0 0 ' + W + ' ' + H}
      style={{ width: '100%', height: 'auto', display: 'block' }}
    >
      {flows.map((f, i) => {
        const w = Math.max(0.6, Math.sqrt(Math.abs(f.kW)) * scale * 0.34)
        const live = Math.abs(f.kW) > 0.05
        const mx = (f.from[0] + f.to[0]) / 2
        return (
          <g key={i} opacity={live ? 1 : 0.16}>
            <path
              d={
                'M ' +
                f.from[0] +
                ' ' +
                f.from[1] +
                ' C ' +
                mx +
                ' ' +
                f.from[1] +
                ', ' +
                mx +
                ' ' +
                f.to[1] +
                ', ' +
                f.to[0] +
                ' ' +
                f.to[1]
              }
              fill="none"
              stroke={f.color}
              strokeWidth={w}
              strokeLinecap="butt"
            />
          </g>
        )
      })}
      {flows.map((f, i) => (
        <text
          key={'l' + i}
          x={(f.from[0] + f.to[0]) / 2}
          y={(f.from[1] + f.to[1]) / 2 - 7}
          textAnchor="middle"
          fill={Math.abs(f.kW) > 0.05 ? C.text3 : C.ghost}
          style={{
            font: '400 8.5px ' + F.mono,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {f.label}
        </text>
      ))}
      {FLOW_NODES.map((n) => (
        <g key={n.label}>
          <rect x={n.x - 4} y={n.y - 4} width={8} height={8} fill={C.lineHard} />
          <text
            x={n.x + (n.anchor === 'end' ? -9 : n.anchor === 'start' ? 9 : 0)}
            y={n.y + (n.anchor === 'middle' ? 20 : 3)}
            textAnchor={n.anchor}
            fill={C.muted}
            style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
          >
            {n.label}
          </text>
        </g>
      ))}
    </svg>
  )
}

// ---------------------------------------------------------------- charts

function Profile({
  x,
  y,
  pos,
  color,
  fill,
  height,
}: {
  x: Float64Array
  y: Float64Array
  pos: number
  color: string
  fill?: string
  height?: number
}) {
  const W = 900
  const H = height ?? 110
  const path = useMemo(() => {
    const n = x.length
    if (!n) return { d: '', area: '' }
    const xm = x[n - 1] || 1
    let lo = Infinity
    let hi = -Infinity
    const step = Math.max(1, Math.floor(n / 900))
    for (let i = 0; i < n; i += step) {
      lo = Math.min(lo, y[i])
      hi = Math.max(hi, y[i])
    }
    // A quantity that does not vary is drawn as a flat line down the
    // middle, not squashed onto the axis: an unvarying signal is a fact
    // about the record, and it should be legible as one.
    const flat = hi - lo < 1e-9
    const span = flat ? 1 : hi - lo
    let d = ''
    for (let i = 0; i < n; i += step) {
      const px = (x[i] / xm) * W
      const py = flat ? H / 2 : H - 8 - ((y[i] - lo) / span) * (H - 20)
      d += (d ? ' L ' : 'M ') + px.toFixed(1) + ' ' + py.toFixed(1)
    }
    return { d, area: d + ' L ' + W + ' ' + H + ' L 0 ' + H + ' Z' }
  }, [x, y, H])
  return (
    <svg
      viewBox={'0 0 ' + W + ' ' + H}
      preserveAspectRatio="none"
      style={{ width: '100%', height: H + 'px', display: 'block' }}
    >
      {fill ? <path d={path.area} fill={fill} /> : null}
      <path d={path.d} fill="none" stroke={color} strokeWidth={1.2} />
      <line
        x1={pos * W}
        x2={pos * W}
        y1={0}
        y2={H}
        stroke={C.electrical}
        strokeWidth={1}
      />
    </svg>
  )
}

// ------------------------------------------------------------- registry

function Registry({ rows, note }: { rows: RegistryRow[]; note: string }) {
  const [open, setOpen] = useState(false)
  return (
    <Panel>
      <PanelHead
        kicker="THE TRACE LOADER, APPLIED TO EVERY TRACE IN THE REPOSITORY"
        title="What conforms, what does not, and why"
        right={
          <button
            onClick={() => setOpen(!open)}
            style={{
              all: 'unset',
              cursor: 'pointer',
              padding: '6px 12px',
              border: '1px solid ' + C.lineHard,
              font: '500 10px/1 ' + F.mono,
              letterSpacing: '.16em',
              color: C.muted,
            }}
          >
            {open ? 'COLLAPSE' : 'EXPAND'}
          </button>
        }
      />
      <div style={{ padding: '16px 20px' }}>
        <Body style={{ marginBottom: '14px' }}>{note}</Body>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '60px minmax(240px,2fr) 70px 70px 110px 90px',
            gap: '10px',
            padding: '9px 0',
            borderBottom: '1px solid ' + C.line,
          }}
        >
          <Label>WS</Label>
          <Label>FILE</Label>
          <Label>ROWS</Label>
          <Label>COLS</Label>
          <Label>SCHEMA</Label>
          <Label>SERVED</Label>
        </div>
        {rows.map((r) => (
          <div key={r.file}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns:
                  '60px minmax(240px,2fr) 70px 70px 110px 90px',
                gap: '10px',
                padding: '9px 0',
                borderBottom: '1px solid ' + C.lineSoft,
                alignItems: 'center',
              }}
            >
              <span style={{ font: '400 11px/1 ' + F.mono, color: C.text3 }}>
                {r.ws}
              </span>
              <span
                style={{
                  font: '400 10.5px/1.4 ' + F.mono,
                  color: C.faint,
                  wordBreak: 'break-all',
                }}
              >
                {r.file}
              </span>
              <span style={{ font: '400 11px/1 ' + F.mono, color: C.text3 }}>
                {r.rows}
              </span>
              <span style={{ font: '400 11px/1 ' + F.mono, color: C.text3 }}>
                {r.nColumns}
              </span>
              <span
                style={{
                  font: '500 9px/1.3 ' + F.mono,
                  letterSpacing: '.1em',
                  color: r.validation.conforms ? C.electricalLo : C.mechanical,
                }}
              >
                {r.validation.conforms
                  ? 'R34 CONFORMS'
                  : r.validation.schemaClass === 'R34'
                    ? 'R34 REFUSED'
                    : 'PRE-R34'}
              </span>
              <span
                style={{
                  font: '500 9px/1.3 ' + F.mono,
                  letterSpacing: '.1em',
                  color: r.servedByExhibit ? C.text : C.ghost,
                }}
              >
                {r.servedByExhibit ? 'SERVED' : 'LINKED ONLY'}
              </span>
            </div>
            {open ? (
              <div
                style={{
                  padding: '6px 0 12px 60px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '5px',
                }}
              >
                {r.validation.reasons.map((why, i) => (
                  <span
                    key={i}
                    style={{ font: '300 11px/1.5 ' + F.sans, color: C.text3 }}
                  >
                    {'— ' + why}
                  </span>
                ))}
                {r.validation.missingCoreColumns.length ? (
                  <span
                    style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}
                  >
                    {'core columns absent: ' +
                      r.validation.missingCoreColumns.join(', ')}
                  </span>
                ) : null}
                {r.validation.declaredAbsentByDesign.length ? (
                  <span
                    style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}
                  >
                    {'declared absent by design: ' +
                      r.validation.declaredAbsentByDesign.join(', ')}
                  </span>
                ) : null}
                {r.validation.blendOrder.checked ? (
                  <span
                    style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}
                  >
                    {'R15 blend residual, bus / wheel: ' +
                      (r.validation.blendOrder.bus_worst_kW ?? 0).toFixed(4) +
                      ' / ' +
                      (r.validation.blendOrder.wheel_worst_kW ?? 0).toFixed(4) +
                      ' kW against a ' +
                      (r.validation.blendOrder.tolerance_kW ?? 0).toFixed(4) +
                      ' kW printing tolerance'}
                  </span>
                ) : null}
                {r.resultsShaMatchesDisk === null ||
                r.resultsShaMatchesDisk === undefined ? null : (
                  <span
                    style={{
                      font: '400 10px/1.5 ' + F.mono,
                      color: r.resultsShaMatchesDisk ? C.faint : C.heat,
                    }}
                  >
                    {'header results_sha256 matches the results file on disk: ' +
                      (r.resultsShaMatchesDisk ? 'yes' : 'NO')}
                  </span>
                )}
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </Panel>
  )
}

// ------------------------------------------------------------------ main

export default function Simulator({ d, bundle }: { d: any; bundle: any }) {
  const [sel, setSel] = useState(d.traces[0].id)
  const t: TraceEntry = bundle.traces[sel]
  const meta = d.traces.find((x: any) => x.id === sel)

  const [scrub, setScrub] = useState<Loaded | null>(null)
  const [check, setCheck] = useState<RunCheck | null>(null)
  const [seg, setSeg] = useState<Loaded | null>(null)
  const [segIx, setSegIx] = useState(-1)
  const [map, setMap] = useState<Bsfc | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [pos, setPos] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const raf = useRef(0)
  const t0 = useRef(0)
  const p0 = useRef(0)

  useEffect(() => {
    setScrub(null)
    setSeg(null)
    setSegIx(-1)
    setErr(null)
    setPos(0)
    setPlaying(false)
    let live = true
    loadScrub(t)
      .then((s) => {
        if (!live) return
        setScrub(s)
        setCheck(validateLoaded(t, s))
      })
      .catch((e) => live && setErr(String(e)))
    loadBsfc(meta.bsfcMap)
      .then((m) => live && setMap(m))
      .catch(() => undefined)
    return () => {
      live = false
    }
  }, [sel, t, meta.bsfcMap])

  useEffect(() => {
    if (!playing) return
    t0.current = performance.now()
    p0.current = pos
    const step = () => {
      const dt = (performance.now() - t0.current) / 1000
      const np = Math.min(1, p0.current + (dt * speed) / 40)
      setPos(np)
      if (np >= 1) setPlaying(false)
      else raf.current = requestAnimationFrame(step)
    }
    raf.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, speed])

  // detail tier: fetch only the segment in view
  const wantSeg = scrub
    ? Math.min(
        t.segments.length - 1,
        Math.floor((pos * (t.sourceRows - 1)) / t.segmentRows),
      )
    : -1
  useEffect(() => {
    if (wantSeg < 0 || wantSeg === segIx) return
    let live = true
    loadSegment(t, wantSeg)
      .then((s) => {
        if (!live) return
        setSeg(s)
        setSegIx(wantSeg)
      })
      .catch(() => undefined)
    return () => {
      live = false
    }
  }, [wantSeg, segIx, t])

  if (err)
    return (
      <div style={{ padding: '20px', font: '400 12px/1.6 ' + F.mono, color: C.heat }}>
        {'The trace did not load: ' + err}
      </div>
    )
  if (!scrub)
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

  if (check && !check.ok)
    return (
      <Panel accent={C.heat}>
        <PanelHead
          kicker="TRACE REFUSED"
          title="This file does not satisfy TRACE_SCHEMA, so it is not plotted"
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {check.reasons.map((r, i) => (
            <span key={i} style={{ font: '400 12px/1.6 ' + F.mono, color: C.text3 }}>
              {'— ' + r}
            </span>
          ))}
        </div>
      </Panel>
    )

  const iScrub = Math.max(0, Math.min(scrub.n - 1, Math.round(pos * (scrub.n - 1))))
  const rowAbs = Math.round(pos * (t.sourceRows - 1))
  const iSeg = seg ? Math.max(0, Math.min(seg.n - 1, rowAbs - segIx * t.segmentRows)) : -1
  const detail = seg && iSeg >= 0 && iSeg < seg.n
  const src = detail ? seg! : scrub
  const iSrc = detail ? iSeg : iScrub

  const g = (name: string) => {
    const a = src.col(name)
    return a ? a[iSrc] : 0
  }

  const x = scrub.col('x_m')
  const z = scrub.col('z_m')
  const socAll = scrub.col('soc_pct')
  const tpAll = scrub.col('T_pack_C')
  const fuelAll = scrub.col('fuel_cum_g')

  const engOn = g('engine_state') >= 2 || g('P_shaft_eng_kW') > 0.5
  const kmNow = g('x_m') / 1000
  const litres = g('fuel_cum_g') / 832
  const l100 = kmNow > 0.05 ? (litres / kmNow) * 100 : 0
  const payloadKg = Number(t.meta.payload_kg ?? 0)
  const mjPtkm =
    kmNow > 0.05 && payloadKg > 0
      ? ((g('fuel_cum_g') * 42.8) / 1000) / (kmNow * (payloadKg / 1000))
      : 0

  const P = {
    gen: g('P_gen_bus_kW'),
    bus: g('P_bus_load_kW'),
    mot: g('P_motor_bus_kW'),
    motMech: g('P_motor_mech_kW'),
    regen: g('P_regen_pack_kW'),
    heat: g('P_heater_kW'),
    res: g('P_resistor_kW'),
    fric: g('P_friction_brake_kW'),
    batt: g('P_batt_bus_kW'),
    wheel: g('P_wheel_kW'),
    shaft: g('P_shaft_eng_kW'),
  }
  // TRACE_SCHEMA describes P_bus_load_kW as "accessories + heater"; in
  // these files it is the TOTAL bus load and runs exactly 2.0 kW above
  // P_motor_bus_kW at every sample. The accessory term is therefore shown
  // as the difference of the two columns rather than read off either one.
  const acc = P.bus - P.mot
  const flows: Flow[] = [
    { from: [40, 60], to: [170, 60], kW: P.shaft, color: C.mechanical, label: P.shaft.toFixed(1) },
    { from: [170, 60], to: [300, 110], kW: P.gen, color: C.electrical, label: P.gen.toFixed(1) },
    { from: [300, 110], to: [300, 40], kW: Math.max(0, -P.batt), color: C.electrical, label: Math.max(0, -P.batt).toFixed(1) },
    { from: [300, 40], to: [300, 110], kW: Math.max(0, P.batt), color: C.electrical, label: Math.max(0, P.batt).toFixed(1) },
    { from: [300, 110], to: [430, 110], kW: Math.max(0, P.mot), color: C.electrical, label: Math.max(0, P.mot).toFixed(1) },
    { from: [430, 110], to: [300, 110], kW: Math.max(0, -P.mot), color: C.electrical, label: Math.max(0, -P.mot).toFixed(1) },
    { from: [430, 110], to: [575, 110], kW: Math.abs(P.motMech), color: C.electrical, label: Math.abs(P.motMech).toFixed(1) },
    { from: [300, 110], to: [300, 180], kW: acc, color: C.electricalLo, label: acc.toFixed(1) },
    { from: [300, 110], to: [180, 180], kW: P.heat, color: C.heat, label: P.heat.toFixed(1) },
    { from: [300, 110], to: [180, 225], kW: P.res, color: C.heat, label: P.res.toFixed(1) },
    { from: [575, 110], to: [575, 190], kW: P.fric, color: C.friction, label: P.fric.toFixed(1) },
    { from: [300, 40], to: [430, 40], kW: P.regen, color: C.electrical, label: P.regen.toFixed(1) },
  ]

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

      <Panel accent={C.electricalLine}>
        <PanelHead
          kicker="SELECT A TRACE"
          title={meta.label}
          right={<StatusBadge s={d.statusBadge} />}
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
          {d.traces.map((x2: any) => {
            const on = x2.id === sel
            return (
              <button
                key={x2.id}
                onClick={() => setSel(x2.id)}
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
                {x2.label}
              </button>
            )
          })}
        </div>

        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* transport */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
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
              {playing ? 'PAUSE' : 'PLAY'}
            </button>
            {[1, 4, 16].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                style={{
                  all: 'unset',
                  cursor: 'pointer',
                  padding: '7px 11px',
                  border: '1px solid ' + (speed === s ? C.electricalLine : C.lineHard),
                  font: '500 10px/1 ' + F.mono,
                  color: speed === s ? C.electricalLo : C.muted,
                }}
              >
                {'x' + s}
              </button>
            ))}
            <input
              type="range"
              min={0}
              max={1000}
              value={Math.round(pos * 1000)}
              onChange={(e) => {
                setPlaying(false)
                setPos(Number(e.target.value) / 1000)
              }}
              style={{ flex: 1, minWidth: '180px' }}
            />
            <span
              style={{
                font: '400 12px/1 ' + F.mono,
                fontVariantNumeric: 'tabular-nums',
                color: C.text3,
                minWidth: '150px',
                textAlign: 'right',
              }}
            >
              {kmNow.toFixed(3) + ' km · ' + g('t_s').toFixed(1) + ' s'}
            </span>
          </div>

          {/* the decimation badge, verbatim */}
          <div
            style={{
              display: 'flex',
              gap: '12px',
              alignItems: 'center',
              flexWrap: 'wrap',
              padding: '8px 12px',
              border: '1px solid ' + C.mechanicalLine,
              background: C.mechanicalBg,
            }}
          >
            <span
              style={{
                font: '500 10px/1.4 ' + F.mono,
                letterSpacing: '.14em',
                color: C.mechanical,
              }}
            >
              {bundle.decimationBadge.toUpperCase()}
            </span>
            <span style={{ font: '400 10px/1.4 ' + F.mono, color: C.faint }}>
              {t.sourcePath}
            </span>
            <span style={{ font: '400 10px/1.4 ' + F.mono, color: C.fainter }}>
              {detail
                ? 'showing the 10 Hz detail tier for the segment in view'
                : 'showing the 1 Hz scrub tier'}
            </span>
          </div>

          {/* elevation */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <Label>ELEVATION FROM z_m</Label>
              <Label>
                {'STRIDED 1 Hz WHOLE-TRACE INDEX · ' +
                  t.outputRows1Hz +
                  ' ROWS · SPAN ' +
                  (Math.max(...z) - Math.min(...z)).toFixed(1) +
                  ' m'}
              </Label>
            </div>
            <Profile x={x} y={z} pos={pos} color={C.friction} fill="#131a20" />
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ font: '400 9px/1.4 ' + F.mono, color: C.faint }}>
                {'now ' + g('z_m').toFixed(2) + ' m'}
              </span>
              <span style={{ font: '400 9px/1.4 ' + F.mono, color: C.faint }}>
                {'grade ' + g('grade_pct').toFixed(2) + ' %'}
              </span>
            </div>
          </div>

          {/* power flow + bsfc */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))',
              gap: '18px',
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Label>POWER FLOW — WIDTH IS THE SQUARE ROOT OF KILOWATTS, ONE SCALE</Label>
              <PowerFlow flows={flows} scale={1} />
              <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
                {[
                  ['P_shaft_eng_kW', P.shaft],
                  ['P_gen_bus_kW', P.gen],
                  ['P_motor_bus_kW', P.mot],
                  ['P_motor_mech_kW', P.motMech],
                  ['P_batt_bus_kW', P.batt],
                  ['P_bus_load_kW', P.bus],
                  ['ACCESSORIES, DERIVED', acc],
                  ['P_regen_pack_kW', P.regen],
                  ['P_heater_kW', P.heat],
                  ['P_resistor_kW', P.res],
                  ['P_friction_brake_kW', P.fric],
                  ['P_wheel_kW', P.wheel],
                ].map(([k, v]) => (
                  <span
                    key={k as string}
                    style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}
                  >
                    <span
                      style={{
                        font: '400 8px/1 ' + F.mono,
                        letterSpacing: '.14em',
                        color: C.ghost,
                      }}
                    >
                      {k as string}
                    </span>
                    <span
                      style={{
                        font: '400 12px/1 ' + F.mono,
                        fontVariantNumeric: 'tabular-nums',
                        color: C.text3,
                      }}
                    >
                      {(v as number).toFixed(2)}
                    </span>
                  </span>
                ))}
              </div>
              <span style={{ font: '300 10.5px/1.5 ' + F.sans, color: C.faint }}>
                {d.blendOrder.rule + ' · ' + d.blendOrder.citation}
              </span>
              <span style={{ font: '300 10.5px/1.5 ' + F.sans, color: C.faint }}>
                {d.busLoadNote}
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Label>{'BSFC MAP — ' + meta.bsfcMap}</Label>
              <BsfcMap map={map} rpm={g('N_eng_rpm')} tq={g('T_eng_Nm')} on={engOn} />
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                {[
                  ['ENGINE SPEED', g('N_eng_rpm').toFixed(0) + ' rpm'],
                  ['TORQUE', g('T_eng_Nm').toFixed(0) + ' Nm'],
                  ['GENSET STATE', g('genset_state').toFixed(0)],
                ].map(([k, v]) => (
                  <span
                    key={k}
                    style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}
                  >
                    <span
                      style={{
                        font: '400 8px/1 ' + F.mono,
                        letterSpacing: '.14em',
                        color: C.ghost,
                      }}
                    >
                      {k}
                    </span>
                    <span style={{ font: '400 12px/1 ' + F.mono, color: C.text3 }}>
                      {v}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* soc / temp / fuel */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))',
              gap: '18px',
            }}
          >
            <div>
              <Label>PACK STATE OF CHARGE, soc_pct</Label>
              <Profile x={x} y={socAll} pos={pos} color={C.electrical} height={80} />
              <span style={{ font: '400 13px/1.6 ' + F.mono, color: C.text }}>
                {g('soc_pct').toFixed(2) + ' %'}
              </span>
            </div>
            <div>
              <Label>PACK TEMPERATURE, T_pack_C</Label>
              <Profile x={x} y={tpAll} pos={pos} color={C.heat} height={80} />
              <span style={{ font: '400 13px/1.6 ' + F.mono, color: C.text }}>
                {g('T_pack_C').toFixed(2) + ' C'}
              </span>
            </div>
            <div>
              <Label>CUMULATIVE FUEL, fuel_cum_g</Label>
              <Profile x={x} y={fuelAll} pos={pos} color={C.mechanical} height={80} />
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                {[
                  ['LITRES', litres.toFixed(3)],
                  ['L/100 km', l100.toFixed(2)],
                  ['MJ / PAYLOAD t-km', mjPtkm.toFixed(3)],
                  ['HEADER payload_kg', payloadKg.toFixed(1)],
                ].map(([k, v]) => (
                  <span
                    key={k}
                    style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}
                  >
                    <span
                      style={{
                        font: '400 8px/1 ' + F.mono,
                        letterSpacing: '.14em',
                        color: C.ghost,
                      }}
                    >
                      {k}
                    </span>
                    <span style={{ font: '400 12px/1 ' + F.mono, color: C.text3 }}>
                      {v}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* the payload the counter divides by, and the ledger's */}
          <div
            style={{
              border: '1px solid ' + C.mechanicalLine,
              background: C.mechanicalBg,
              padding: '13px 15px',
              display: 'flex',
              flexDirection: 'column',
              gap: '9px',
            }}
          >
            <span
              style={{
                font: '500 11px/1.5 ' + F.mono,
                letterSpacing: '.06em',
                color: C.mechanical,
              }}
            >
              {d.payloadNote.headline}
            </span>
            <Body style={{ fontSize: '12px' }}>{d.payloadNote.body}</Body>
            <div style={{ display: 'flex', gap: '18px', flexWrap: 'wrap' }}>
              {[
                ["WS11 LEDGER, RULER", d.payloadNote.ledgerRuler],
                ['WS11 LEDGER, V1', d.payloadNote.ledgerV1],
                ['WS11 LEDGER, V2', d.payloadNote.ledgerV2],
              ].map(([k, v]) => (
                <div
                  key={k as string}
                  style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                >
                  <Label>{k as string}</Label>
                  <Num c={v as Cited} size={12} />
                </div>
              ))}
            </div>
          </div>

          {/* ribbon */}
          <div
            style={{
              border: '1px dashed ' + C.lineHard,
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <Label>8-SEED RIBBON — ABSENT</Label>
            <span style={{ font: '300 11.5px/1.55 ' + F.sans, color: C.faint }}>
              {d.ribbon.reason}
            </span>
          </div>

          {/* trace header, from the file itself */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
            <Label>THIS FILE'S OWN HEADER, VERBATIM</Label>
            <div
              style={{
                border: '1px solid ' + C.lineSoft,
                padding: '11px 13px',
                display: 'flex',
                flexDirection: 'column',
                gap: '3px',
                maxHeight: '190px',
                overflow: 'auto',
              }}
            >
              {meta.headerLines.map((h: string, i: number) => (
                <span
                  key={i}
                  style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}
                >
                  {'# ' + h}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Panel>

      <Panel accent={C.mechanicalLine}>
        <PanelHead
          kicker="THE WORKSTREAM THIS TRACE COMES FROM"
          title={d.statusNote.headline}
          right={<TierBadge tier="RECORD" />}
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Num c={d.statusNote.quote as Cited} size={12} />
          <Quote c={d.statusNote.baselineQuote} />
          <Body style={{ fontSize: '12.5px' }}>{d.statusNote.packetGap}</Body>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(150px,1fr))',
              gap: '14px',
              borderTop: '1px solid ' + C.lineSoft,
              paddingTop: '12px',
            }}
          >
            {[
              ['LOOP RATE', d.controlConstants.loopRateHz],
              ['CHOPPER RATE', d.controlConstants.chopperRateHz],
              ['V1 DISPATCH FIXED POINT', d.controlConstants.v1FixedPoint],
              ['V2 STRATEGY', d.controlConstants.v2Strategy],
              ['PINNED-POINT BSFC', d.controlConstants.pinnedBsfc],
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
          <Quote c={d.blendOrder.quote} />
        </div>
      </Panel>

      <Registry rows={d.registry} note={d.registryNote} />
    </div>
  )
}
