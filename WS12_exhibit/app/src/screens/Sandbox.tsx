import { useMemo, useState } from 'react'
import { C, F } from '../theme'
import { Body, Label, Num, Panel, PanelHead, Quote } from '../ui'
import {
  crossingMass,
  ratioCeiling,
  ratioWindow,
  roadLoadN,
} from '../sandboxModel'
import type { Endpoint } from '../sandboxModel'
import type { Cited } from '../types'

function Slider({
  k,
  v,
  min,
  max,
  step,
  on,
}: {
  k: string
  v: string
  min: number
  max: number
  step: number
  on: (n: number) => void
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Label>{k}</Label>
        <span
          style={{
            font: '400 12px/1 ' + F.mono,
            fontVariantNumeric: 'tabular-nums',
            color: C.mechanical,
          }}
        >
          {v}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        onChange={(e) => on(Number(e.target.value))}
        defaultValue={min}
        style={{ width: '100%' }}
      />
    </div>
  )
}

export default function Sandbox({ d }: { d: any }) {
  const lo = d.endpoints.zero as Endpoint
  const hi = d.endpoints.one as Endpoint
  const rhoNom = Number(d.airDensity.members[1].value.v)
  const rhoCold = Number(d.airDensity.members[0].value.v)
  const rhoHot = Number(d.airDensity.members[2].value.v)

  const [mass, setMass] = useState(lo.m_kg)
  const [grade, setGrade] = useState(6)
  const [ratio, setRatio] = useState(3.6)
  const [rho, setRho] = useState(rhoNom)

  const w = ratioWindow(mass, grade / 100, rho, lo, hi)
  const cross = crossingMass(grade / 100, rho, lo, hi)
  const inWin = ratio >= w.rMin && ratio <= w.rMax

  const W = 620
  const H = 260
  const mx = (m: number) =>
    44 + ((m - lo.m_kg) / (hi.m_kg - lo.m_kg)) * (W - 64)
  const ry = (r: number) => H - 30 - (r / 8) * (H - 54)

  const bands = useMemo(() => {
    const pts: { m: number; lo: number; hi: number }[] = []
    for (let k = 0; k <= 80; k++) {
      const m = lo.m_kg + (k * (hi.m_kg - lo.m_kg)) / 80
      const ww = ratioWindow(m, grade / 100, rho, lo, hi)
      pts.push({ m, lo: ww.rMin, hi: ww.rMax })
    }
    let upper = ''
    let lower = ''
    pts.forEach((p, k) => {
      upper += (k ? ' L ' : 'M ') + mx(p.m).toFixed(1) + ' ' + ry(p.hi).toFixed(1)
      lower += (k ? ' L ' : 'M ') + mx(p.m).toFixed(1) + ' ' + ry(p.lo).toFixed(1)
    })
    let band = upper
    for (let k = pts.length - 1; k >= 0; k--)
      band += ' L ' + mx(pts[k].m).toFixed(1) + ' ' + ry(pts[k].lo).toFixed(1)
    return { upper, lower, band: band + ' Z' }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [grade, rho, lo, hi])

  const anchors = d.anchors.rows.map((r: any) => {
    const f = roadLoadN(
      r.inputs.m_kg,
      r.inputs.CdA_m2,
      r.inputs.Crr,
      r.inputs.rho_air,
      r.inputs.v_ms,
      r.inputs.grade,
    )
    return { r, got: f.total_N }
  })
  const ceilGot = ratioCeiling(
    d.anchors.ceiling.inputs.rpm_ceiling,
    d.anchors.ceiling.inputs.r_dyn_m,
    d.anchors.ceiling.inputs.v_cruise_ms,
  )

  const state = w.open
    ? inWin
      ? 'ONE GEAR EXISTS'
      : 'ONE GEAR EXISTS — NOT THIS ONE'
    : 'NO SINGLE GEAR EXISTS'
  const stateCol = w.open ? (inWin ? C.electrical : C.mechanical) : C.heat

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

      <div
        style={{
          padding: '11px 15px',
          border: '1px solid ' + C.mechanicalLine,
          background: C.mechanicalBg,
          font: '500 11.5px/1.5 ' + F.mono,
          letterSpacing: '.1em',
          color: C.mechanical,
        }}
      >
        {d.kicker}
      </div>

      <Panel accent={C.mechanicalLine}>
        <PanelHead
          kicker="THE RATIO WINDOW"
          title="Where a single fixed ratio stops existing"
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px,1.4fr) minmax(260px,1fr)',
          }}
        >
          <div style={{ padding: '18px 20px', borderRight: '1px solid ' + C.line }}>
            <svg
              viewBox={'0 0 ' + W + ' ' + H}
              style={{ width: '100%', height: 'auto', display: 'block' }}
            >
              {[1, 2, 3, 4, 5, 6, 7].map((r) => (
                <g key={r}>
                  <line
                    x1={44}
                    x2={W - 16}
                    y1={ry(r)}
                    y2={ry(r)}
                    stroke={C.lineSoft}
                  />
                  <text
                    x={38}
                    y={ry(r) + 3}
                    textAnchor="end"
                    fill={C.ghost}
                    style={{ font: '400 8px ' + F.mono }}
                  >
                    {r}
                  </text>
                </g>
              ))}
              <path d={bands.band} fill="#14211f" opacity={0.85} />
              <path d={bands.upper} fill="none" stroke={C.electrical} strokeWidth={1.3} />
              <path d={bands.lower} fill="none" stroke={C.heat} strokeWidth={1.3} />
              {cross === null ? null : (
                <line
                  x1={mx(cross)}
                  x2={mx(cross)}
                  y1={14}
                  y2={H - 30}
                  stroke={C.mechanical}
                  strokeDasharray="4 3"
                />
              )}
              <line
                x1={mx(mass)}
                x2={mx(mass)}
                y1={14}
                y2={H - 30}
                stroke={C.lineHard}
              />
              <circle cx={mx(mass)} cy={ry(ratio)} r={5} fill={stateCol} />
              <text
                x={44}
                y={H - 12}
                fill={C.fainter}
                style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
              >
                VEHICLE MASS
              </text>
              <text
                x={W - 16}
                y={H - 12}
                textAnchor="end"
                fill={C.fainter}
                style={{ font: '400 8px ' + F.mono, letterSpacing: '.14em' }}
              >
                RATIO
              </text>
            </svg>
            <div
              style={{
                marginTop: '10px',
                display: 'flex',
                gap: '18px',
                flexWrap: 'wrap',
              }}
            >
              {[
                ['CEILING — RPM AT CRUISE', w.rMax.toFixed(2) + ':1', C.electrical],
                ['FLOOR — TORQUE ON THE GRADE', w.rMin.toFixed(2) + ':1', C.heat],
                ['GRADE FORCE', (w.force.total_N / 1000).toFixed(2) + ' kN', C.text3],
                [
                  'WINDOW CLOSES AT',
                  cross === null ? 'not within range' : (cross / 1000).toFixed(1) + ' t',
                  C.mechanical,
                ],
              ].map(([k, v, col]) => (
                <div
                  key={k}
                  style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                >
                  <Label>{k}</Label>
                  <span
                    style={{
                      font: '400 15px/1 ' + F.mono,
                      fontVariantNumeric: 'tabular-nums',
                      color: col,
                    }}
                  >
                    {v}
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
              gap: '18px',
            }}
          >
            <div
              style={{
                padding: '10px 12px',
                border: '1px solid ' + stateCol,
                font: '500 12px/1.4 ' + F.mono,
                letterSpacing: '.1em',
                color: stateCol,
              }}
            >
              {state}
            </div>
            <Slider
              k="VEHICLE MASS"
              v={(mass / 1000).toFixed(1) + ' t'}
              min={lo.m_kg}
              max={hi.m_kg}
              step={100}
              on={setMass}
            />
            <Slider
              k="GRADE"
              v={grade.toFixed(1) + ' %'}
              min={0}
              max={8}
              step={0.1}
              on={setGrade}
            />
            <Slider
              k="FIXED GEAR RATIO"
              v={ratio.toFixed(2) + ' : 1'}
              min={1}
              max={8}
              step={0.02}
              on={setRatio}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Label>{d.airDensity.label}</Label>
                <span
                  style={{
                    font: '400 12px/1 ' + F.mono,
                    color: C.mechanical,
                  }}
                >
                  {rho.toFixed(3) + ' kg/m3'}
                </span>
              </div>
              <input
                type="range"
                min={rhoHot}
                max={rhoCold}
                step={0.001}
                defaultValue={rhoNom}
                onChange={(e) => setRho(Number(e.target.value))}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                {d.airDensity.members.map((m: any) => (
                  <button
                    key={m.key}
                    onClick={() => setRho(Number(m.value.v))}
                    style={{
                      all: 'unset',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '3px',
                    }}
                  >
                    <Label>{m.label}</Label>
                    <Num c={m.value} size={11} />
                  </button>
                ))}
              </div>
              <Body style={{ fontSize: '11px', color: C.faint }}>
                {d.airDensity.note}
              </Body>
            </div>
          </div>
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE SAME TWO LINES OF ARITHMETIC, AGAINST THE RECORD"
          title={d.anchors.headline}
        />
        <div style={{ padding: '18px 20px' }}>
          <Body style={{ marginBottom: '14px' }}>{d.anchors.note}</Body>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(240px,2fr) 150px 170px 90px',
              gap: '12px',
              padding: '9px 0',
              borderBottom: '1px solid ' + C.line,
            }}
          >
            <Label>CASE</Label>
            <Label>THIS SCREEN'S MODEL</Label>
            <Label>THE RECORD</Label>
            <Label>AGREES</Label>
          </div>
          {anchors.map(({ r, got }: any) => {
            const want = Number(r.record.v)
            const ok = Math.abs(got - want) < 1e-6
            return (
              <div
                key={r.id}
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'minmax(240px,2fr) 150px 170px 90px',
                  gap: '12px',
                  padding: '10px 0',
                  borderBottom: '1px solid ' + C.lineSoft,
                  alignItems: 'center',
                }}
              >
                <span style={{ font: '400 12px/1.4 ' + F.sans, color: C.text3 }}>
                  {r.label}
                </span>
                <span
                  style={{
                    font: '400 12px/1 ' + F.mono,
                    fontVariantNumeric: 'tabular-nums',
                    color: C.mechanical,
                  }}
                >
                  {got.toFixed(4) + ' N'}
                </span>
                <Num c={r.record as Cited} size={12} />
                <span
                  style={{
                    font: '500 9px/1 ' + F.mono,
                    letterSpacing: '.14em',
                    color: ok ? C.electricalLo : C.heat,
                  }}
                >
                  {ok ? 'YES' : 'NO'}
                </span>
              </div>
            )
          })}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(240px,2fr) 150px 170px 90px',
              gap: '12px',
              padding: '10px 0',
              alignItems: 'center',
            }}
          >
            <span style={{ font: '400 12px/1.4 ' + F.sans, color: C.text3 }}>
              {d.anchors.ceiling.label}
            </span>
            <span
              style={{
                font: '400 12px/1 ' + F.mono,
                fontVariantNumeric: 'tabular-nums',
                color: C.mechanical,
              }}
            >
              {ceilGot.toFixed(6) + ':1'}
            </span>
            <Num c={d.anchors.ceiling.record} size={12} />
            <span
              style={{
                font: '500 9px/1 ' + F.mono,
                letterSpacing: '.14em',
                color:
                  Math.abs(ceilGot - Number(d.anchors.ceiling.record.v)) < 1e-9
                    ? C.electricalLo
                    : C.heat,
              }}
            >
              {Math.abs(ceilGot - Number(d.anchors.ceiling.record.v)) < 1e-9
                ? 'YES'
                : 'NO'}
            </span>
          </div>
        </div>
      </Panel>

      <Panel>
        <PanelHead kicker="THE FIRST WALL" title={d.s3.headline} />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
          }}
        >
          <div style={{ padding: '18px 20px', borderRight: '1px solid ' + C.line }}>
            <Body>{d.s3.body}</Body>
          </div>
          <div
            style={{
              padding: '18px 20px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))',
              gap: '14px',
            }}
          >
            {[
              ['RATIO CEILING, CLOSED FORM', d.anchors.ceiling.record],
              ['HIGHEST SWEPT RATIO UNDER IT', d.s3.maxWithoutOverspeed],
              ['RATIO THE 6% GRADE NEEDS', d.s3.ratioNeeded],
              ['OVER THE RPM CEILING BY', d.s3.overCeilingRpm],
              ['FORCE THE GRADE DEMANDS', d.s3.forceRequired],
              ['FORCE AVAILABLE AT THE CEILING', d.s3.forceAvailable],
              ['WHICH IS', d.s3.forceFraction],
              ['RATIO SPAN NEEDED', d.s3.spanNeeded],
              ['FEASIBLE RATIOS IN THE SWEEP', d.s3.anyFeasible],
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
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE CONSTANTS THIS SCREEN INTERPOLATES BETWEEN"
          title="Both endpoints are on disk"
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))',
          }}
        >
          {(['zero', 'one'] as const).map((which) => {
            const e = d.endpoints[which]
            return (
              <div
                key={which}
                style={{
                  padding: '18px 20px',
                  borderRight: '1px solid ' + C.line,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <span style={{ font: '500 13px/1.3 ' + F.sans, color: C.text }}>
                  {e.label}
                </span>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit,minmax(120px,1fr))',
                    gap: '12px',
                  }}
                >
                  {Object.keys(e.citations).map((k) => {
                    const flag = d.endpointFlags.find(
                      (f: any) => f.endpoint === which && f.field === k,
                    )
                    return (
                      <div
                        key={k}
                        style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                      >
                        <Label>{k}</Label>
                        <Num c={e.citations[k]} size={12} />
                        {flag ? (
                          <span
                            style={{
                              font: '500 8px/1.3 ' + F.mono,
                              letterSpacing: '.12em',
                              color: C.mechanical,
                            }}
                          >
                            {flag.flag}
                          </span>
                        ) : null}
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
        {d.endpointFlags.map((f: any) => (
          <div
            key={f.field + f.endpoint}
            style={{
              padding: '14px 20px',
              borderTop: '1px solid ' + C.line,
              background: C.mechanicalBg,
              display: 'flex',
              flexDirection: 'column',
              gap: '9px',
            }}
          >
            <Label>{f.field + ' — ' + f.flag}</Label>
            <Quote c={f.quote} />
            <Body style={{ fontSize: '12px' }}>{f.note}</Body>
            <span style={{ font: '300 11px/1.55 ' + F.sans, color: C.faint }}>
              {'Why this is recorded and not a defect: ' + f.why_minor + '.'}
            </span>
          </div>
        ))}
        <div
          style={{
            padding: '16px 20px',
            borderTop: '1px solid ' + C.line,
            display: 'flex',
            flexDirection: 'column',
            gap: '9px',
          }}
        >
          <Label>THE MODEL, STATED</Label>
          <span style={{ font: '400 11.5px/1.6 ' + F.mono, color: C.text3 }}>
            {d.model.roadLoad}
          </span>
          <span style={{ font: '400 11.5px/1.6 ' + F.mono, color: C.text3 }}>
            {d.model.ratioMax.s}
          </span>
          <span style={{ font: '400 11.5px/1.6 ' + F.mono, color: C.text3 }}>
            {d.model.ratioMin}
          </span>
          <span style={{ font: '400 11px/1.6 ' + F.mono, color: C.faint }}>
            {d.model.gConstant}
          </span>
          <Body style={{ fontSize: '12px', color: C.faint }}>
            {d.model.interpolation}
          </Body>
          <Body style={{ fontSize: '12.5px' }}>{d.disclaimer}</Body>
        </div>
      </Panel>
    </div>
  )
}
