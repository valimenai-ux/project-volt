import { useMemo } from 'react'
import { C, F } from '../theme'
import { Body, Label, Num, StatusBadge, TierBadge } from '../ui'
import type { Cited } from '../types'
import type { Loaded } from '../trace'

/**
 * The route, both lanes.
 *
 * Every position drawn here comes from a trace of record and from nothing
 * else: a conforming file's own `x_m`, or an integration of the file's own
 * `v_kmh` at the file's own step where the schema carries no distance
 * column. No offset is applied to separate the lanes, no easing smooths a
 * truck's motion, and no scale is stretched to make a gap visible. Where
 * the record holds the two vehicles in lockstep the lanes are in lockstep.
 */

export interface LaneRun {
  km: Float64Array
  n: number
  source: string
}

/** Distance along the route, from the record's own columns. */
export function laneDistance(d: Loaded, dt: number): LaneRun {
  if (d.ix['x_m'] !== undefined) {
    const x = d.col('x_m')
    const km = new Float64Array(d.n)
    for (let i = 0; i < d.n; i++) km[i] = x[i] / 1000
    return { km, n: d.n, source: 'x_m' }
  }
  const v = d.col('v_kmh')
  const km = new Float64Array(d.n)
  let m = 0
  for (let i = 0; i < d.n; i++) {
    m += (v[i] / 3.6) * dt
    km[i] = m / 1000
  }
  return { km, n: d.n, source: 'v_kmh' }
}

const TRUCK_W = 34
const TRUCK_H = 13

function Truck({ x, y, color }: { x: number; y: number; color: string }) {
  return (
    <g transform={'translate(' + x.toFixed(2) + ' ' + y + ')'}>
      {/* box body */}
      <rect x={-TRUCK_W} y={-TRUCK_H} width={TRUCK_W - 11} height={TRUCK_H}
            fill={color} opacity={0.9} />
      {/* cab */}
      <path
        d={'M ' + (-11) + ' ' + (-TRUCK_H) + ' L -3 ' + (-TRUCK_H) +
           ' L 0 -6 L 0 0 L -11 0 Z'}
        fill={color}
      />
      <circle cx={-27} cy={1.5} r={2.4} fill={C.canvas} stroke={color}
              strokeWidth={1.2} />
      <circle cx={-6} cy={1.5} r={2.4} fill={C.canvas} stroke={color}
              strokeWidth={1.2} />
    </g>
  )
}

function LaneRow({
  lane,
  run,
  pos,
  color,
  totalKm,
  empty,
}: {
  lane: any
  run: LaneRun | null
  pos: number
  color: string
  totalKm: number
  empty?: { headline: string; body: string }
}) {
  const W = 1000
  const H = 58
  const i = run ? Math.max(0, Math.min(run.n - 1, Math.round(pos * (run.n - 1)))) : 0
  const km = run ? run.km[i] : 0
  const x = totalKm > 0 ? 40 + (km / totalKm) * (W - 80) : 40

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(200px,260px) 1fr minmax(120px,150px)',
        gap: '14px',
        alignItems: 'center',
        padding: '10px 0',
        borderTop: '1px solid ' + C.lineSoft,
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ width: '10px', height: '10px', background: empty ? 'transparent' : color, border: empty ? '1px dashed ' + C.lineHard : 'none' }} />
          <span style={{ font: '500 13px/1.2 ' + F.sans, color: empty ? C.faint : C.text }}>
            {lane.name}
          </span>
          {lane.statusBadge ? <StatusBadge s={lane.statusBadge} small /> : null}
        </div>
        <span style={{ font: '400 8.5px/1.4 ' + F.mono, letterSpacing: '.14em', color: C.ghost }}>
          {lane.roleLabel}
        </span>
        <span style={{ font: '300 9.5px/1.45 ' + F.sans, color: C.faint }}>
          {'position from ' + lane.positionSource}
        </span>
      </div>

      <svg
        viewBox={'0 0 ' + W + ' ' + H}
        preserveAspectRatio="none"
        style={{ width: '100%', height: H + 'px', display: 'block' }}
      >
        {/* the road: a dashed baseline, never a zero line */}
        <line
          x1={40}
          x2={W - 40}
          y1={H - 16}
          y2={H - 16}
          stroke={empty ? C.lineHard : C.line}
          strokeDasharray={empty ? '5 5' : '2 6'}
        />
        <line x1={40} x2={40} y1={H - 24} y2={H - 8} stroke={C.ghost} />
        <line x1={W - 40} x2={W - 40} y1={H - 24} y2={H - 8} stroke={C.ghost} />
        {empty || !run ? null : (
          <Truck x={x} y={H - 16} color={color} />
        )}
      </svg>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {empty ? (
          <span style={{ font: '400 11px/1.4 ' + F.mono, color: C.ghost }}>
            —
          </span>
        ) : (
          <>
            <span
              style={{
                font: '400 15px/1 ' + F.mono,
                fontVariantNumeric: 'tabular-nums',
                color: C.text,
              }}
            >
              {km.toFixed(3) + ' km'}
            </span>
            <span style={{ font: '400 9px/1.4 ' + F.mono, color: C.ghost }}>
              {lane.payload ? 'payload ' + lane.payload.s : ''}
            </span>
          </>
        )}
      </div>
    </div>
  )
}

export default function Lanes({
  d,
  ds,
  runs,
  pos,
}: {
  d: any
  ds: any
  runs: (LaneRun | null)[]
  pos: number
}) {
  const totalKm = useMemo(() => {
    let m = 0
    for (const r of runs) if (r && r.n) m = Math.max(m, r.km[r.n - 1])
    return m
  }, [runs])

  const colors = [C.electrical, C.text2]
  const sep = ds.separation
  const liveGap =
    runs.length === 2 && runs[0] && runs[1]
      ? Math.abs(
          runs[0].km[
            Math.max(0, Math.min(runs[0].n - 1, Math.round(pos * (runs[0].n - 1))))
          ] -
            runs[1].km[
              Math.max(0, Math.min(runs[1].n - 1, Math.round(pos * (runs[1].n - 1))))
            ],
        ) * 1000
      : null

  return (
    <div
      style={{
        border: '1px solid ' + C.line,
        background: C.panelAlt,
        padding: '16px 18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', gap: '12px', alignItems: 'baseline', flexWrap: 'wrap' }}>
        <Label>{d.lanes.kicker}</Label>
        <TierBadge tier="DERIVED" />
        <span style={{ flex: 1 }} />
        <span style={{ font: '400 9.5px/1.4 ' + F.mono, color: C.faint }}>
          {ds.schemaClass === 'R34'
            ? 'R34-conforming source'
            : 'pre-R34 source · plotted only from the columns it carries'}
        </span>
      </div>

      <span style={{ font: '300 12px/1.6 ' + F.sans, color: C.text3 }}>
        {d.lanes.rule}
      </span>

      <div>
        {ds.lanes.map((lane: any, k: number) => (
          <LaneRow
            key={lane.traceId + lane.role}
            lane={lane}
            run={runs[k] ?? null}
            pos={pos}
            color={colors[k] ?? C.friction}
            totalKm={totalKm}
          />
        ))}
        {ds.kind === 'single' ? (
          <LaneRow
            lane={{
              name: 'no paired incumbent',
              roleLabel: 'ABSENT',
              positionSource: 'no trace',
            }}
            run={null}
            pos={pos}
            color={C.friction}
            totalKm={totalKm}
            empty={ds.pairAbsence}
          />
        ) : null}
      </div>

      {ds.kind === 'single' ? (
        <div
          style={{
            border: '1px dashed ' + C.lineHard,
            padding: '12px 14px',
            display: 'flex',
            flexDirection: 'column',
            gap: '7px',
          }}
        >
          <Label>{ds.pairAbsence.headline}</Label>
          <Body style={{ fontSize: '12px' }}>{ds.pairAbsence.body}</Body>
        </div>
      ) : (
        <>
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
              ['GAP, LIVE', null],
              ['LARGEST GAP OVER THE RUN', sep.maxSeparation],
              ['GAP AT THE FINISH', sep.finalSeparation],
              ['LARGEST SPEED DIFFERENCE', sep.maxSpeedDifference],
              ['DISTANCE, CANDIDATE', sep.candDistance],
              ['DISTANCE, INCUMBENT', sep.rulerDistance],
            ].map(([k, v]) => (
              <div
                key={k as string}
                style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}
              >
                <Label>{k as string}</Label>
                {v ? (
                  <Num c={v as Cited} size={13} />
                ) : (
                  <span
                    style={{
                      font: '400 13px/1.25 ' + F.mono,
                      fontVariantNumeric: 'tabular-nums',
                      color: C.text,
                      borderBottom: '1px dotted ' + C.electricalLine,
                    }}
                  >
                    {liveGap === null ? '—' : liveGap.toFixed(3) + ' m'}
                  </span>
                )}
              </div>
            ))}
          </div>

          <div
            style={{
              border: '1px solid ' + C.lineHard,
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '7px',
            }}
          >
            <span
              style={{
                font: '500 12.5px/1.45 ' + F.sans,
                color: sep.identical ? C.electricalLo : C.mechanical,
              }}
            >
              {sep.headline}
            </span>
            <Body style={{ fontSize: '12px' }}>{sep.body}</Body>
            <span style={{ font: '400 10px/1.5 ' + F.mono, color: C.faint }}>
              {'compared sample by sample over '}
              <Num c={sep.samples} size={10} />
              {' samples of each file'}
            </span>
          </div>

          {sep.capabilityNote ? (
            <div
              style={{
                border: '1px solid ' + C.mechanicalLine,
                background: C.mechanicalBg,
                padding: '12px 14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <span
                style={{
                  font: '500 12px/1.45 ' + F.sans,
                  color: C.mechanical,
                }}
              >
                {sep.capabilityNote.headline}
              </span>
              <Body style={{ fontSize: '12px' }}>
                {sep.capabilityNote.body}
              </Body>
              <div style={{ display: 'flex', gap: '18px', flexWrap: 'wrap' }}>
                {[
                  ['UNSERVED WHEEL ENERGY', sep.capabilityNote.unservedWheel],
                  ['SECONDS CAPABILITY-LIMITED',
                   sep.capabilityNote.infeasibleSeconds],
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
          ) : null}
        </>
      )}

      <span style={{ font: '300 10.5px/1.55 ' + F.sans, color: C.faint }}>
        {ds.lanes[0].positionBasis}
      </span>
      <span style={{ font: '300 10.5px/1.55 ' + F.sans, color: C.faint }}>
        {d.lanes.postClose}
      </span>
    </div>
  )
}
