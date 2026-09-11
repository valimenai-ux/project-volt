import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import { C, F, STATUS_STYLE, TIER_STYLE } from './theme'
import type { Cited } from './types'

// ---------------------------------------------------------------- citation

interface CiteState {
  open: Cited | null
  show: (c: Cited) => void
  hide: () => void
}

export const CiteCtx = createContext<CiteState>({
  open: null,
  show: () => undefined,
  hide: () => undefined,
})

export function CiteProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState<Cited | null>(null)
  return (
    <CiteCtx.Provider
      value={{ open, show: (c) => setOpen(c), hide: () => setOpen(null) }}
    >
      {children}
    </CiteCtx.Provider>
  )
}

/**
 * The only way a number reaches the screen. Renders `s`, verbatim, and
 * opens its provenance on click. There is no code path that prints a
 * number this component was not handed.
 */
export function Num({
  c,
  size,
  weight,
  color,
  mono,
}: {
  c: Cited | undefined
  size?: number
  weight?: number
  color?: string
  mono?: boolean
}) {
  const { show } = useContext(CiteCtx)
  if (!c) return null
  const t = TIER_STYLE[c.tier] ?? TIER_STYLE.RECORD
  return (
    <button
      onClick={() => show(c)}
      title={
        c.tier === 'RECORD'
          ? 'click to resolve to its file and key path'
          : 'click to see what this was derived from'
      }
      style={{
        all: 'unset',
        cursor: 'pointer',
        fontFamily: mono === false ? F.sans : F.mono,
        fontVariantNumeric: 'tabular-nums',
        fontSize: (size ?? 13) + 'px',
        fontWeight: weight ?? 400,
        color: color ?? (c.tier === 'RECORD' ? C.text : t.col),
        borderBottom: '1px dotted ' + t.line,
        lineHeight: 1.25,
      }}
    >
      {c.s}
    </button>
  )
}

/**
 * The quoted text is stored verbatim, asterisks and backticks included,
 * and the verifier asserts it character for character against the source
 * document. Here the markdown emphasis those characters ENCODE is
 * rendered as emphasis. Nothing is added and nothing is removed.
 */
function renderMarkdownish(raw: string) {
  // A quotation often starts inside a bold span and ends before the
  // closing marker. Closing it for RENDERING only leaves the stored
  // string untouched; the verifier still sees the source characters.
  const odd = (raw.match(/\*\*/g) ?? []).length % 2 === 1
  const s = odd ? raw + '**' : raw
  const out: React.ReactNode[] = []
  const re = /\*\*([\s\S]+?)\*\*|`([^`]+)`/g
  let last = 0
  let m: RegExpExecArray | null
  let k = 0
  while ((m = re.exec(s)) !== null) {
    if (m.index > last) out.push(s.slice(last, m.index))
    if (m[1] !== undefined)
      out.push(
        <strong key={k++} style={{ fontWeight: 600, color: C.text }}>
          {m[1]}
        </strong>,
      )
    else
      out.push(
        <code key={k++} style={{ fontFamily: F.mono, fontSize: '0.92em' }}>
          {m[2]}
        </code>,
      )
    last = re.lastIndex
  }
  if (last < s.length) out.push(s.slice(last))
  return out
}

export function Quote({ c, style }: { c: Cited; style?: React.CSSProperties }) {
  const { show } = useContext(CiteCtx)
  return (
    <button
      onClick={() => show(c)}
      style={{
        all: 'unset',
        cursor: 'pointer',
        display: 'block',
        font: '300 12.5px/1.6 ' + F.sans,
        color: C.text3,
        borderLeft: '2px solid ' + C.lineHard,
        paddingLeft: '12px',
        ...style,
      }}
    >
      {'“'}
      {renderMarkdownish(c.s)}
      {'”'}
    </button>
  )
}

export function CitationSheet() {
  const { open, hide } = useContext(CiteCtx)
  if (!open) return null
  const t = TIER_STYLE[open.tier] ?? TIER_STYLE.RECORD
  const rows: [string, string][] = []
  rows.push(['TIER', open.tier])
  if (open.kind === 'quote') {
    rows.push(['KIND', 'verbatim quotation'])
    rows.push(['FILE', open.file ?? ''])
  } else if (open.kind === 'file') {
    rows.push(['KIND', 'file identity'])
    rows.push(['FILE', open.file ?? ''])
    rows.push(['SHA-256', open.sha256 ?? ''])
    rows.push(['BYTES', String(open.bytes ?? '')])
  } else if (open.file && open.pathText) {
    rows.push(['FILE', open.file])
    rows.push(['KEY PATH', open.pathText])
    rows.push(['RAW VALUE', JSON.stringify(open.v)])
    rows.push(['FORMAT', (open.pre ?? '') + '{:' + open.fmt + '}' + (open.suf ?? '')])
  } else {
    rows.push(['DERIVED FROM', open.derivedFrom ?? ''])
    rows.push(['RAW VALUE', JSON.stringify(open.v)])
  }
  if (open.note) rows.push(['NOTE', open.note])

  return (
    <div
      onClick={hide}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(4,6,8,0.72)',
        zIndex: 90,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '760px',
          width: '100%',
          background: C.panel,
          border: '1px solid ' + t.line,
          maxHeight: '80vh',
          overflow: 'auto',
        }}
      >
        <div
          style={{
            padding: '14px 18px',
            borderBottom: '1px solid ' + C.line,
            background: t.fill,
            display: 'flex',
            alignItems: 'baseline',
            gap: '14px',
            flexWrap: 'wrap',
          }}
        >
          <span
            style={{
              font: '500 10px/1 ' + F.mono,
              letterSpacing: '.18em',
              color: t.col,
            }}
          >
            {'RESOLVING ' + open.tier}
          </span>
          <span
            style={{
              font: '400 17px/1.3 ' + F.mono,
              fontVariantNumeric: 'tabular-nums',
              color: C.text,
            }}
          >
            {open.s}
          </span>
        </div>
        <div style={{ padding: '4px 0' }}>
          {rows.map(([k, v]) => (
            <div
              key={k}
              style={{
                display: 'grid',
                gridTemplateColumns: '128px 1fr',
                gap: '14px',
                padding: '9px 18px',
                borderBottom: '1px solid ' + C.lineSoft,
              }}
            >
              <span
                style={{
                  font: '400 9.5px/1.5 ' + F.mono,
                  letterSpacing: '.16em',
                  color: C.fainter,
                }}
              >
                {k}
              </span>
              <span
                style={{
                  font: '400 12px/1.6 ' + F.mono,
                  color: C.text3,
                  wordBreak: 'break-word',
                }}
              >
                {v}
              </span>
            </div>
          ))}
        </div>
        <div
          style={{
            padding: '12px 18px',
            font: '300 11.5px/1.6 ' + F.sans,
            color: C.faint,
          }}
        >
          {open.tier === 'RECORD'
            ? 'exhibit_verify.py re-opens this file with its own resolver and its own formatter and asserts this string before the build is allowed to pass.'
            : 'A derived value. It is not a number of record and resolves to no key path; what it was computed from is named above.'}
        </div>
        <button
          onClick={hide}
          style={{
            all: 'unset',
            cursor: 'pointer',
            display: 'block',
            width: '100%',
            textAlign: 'center',
            padding: '11px',
            borderTop: '1px solid ' + C.line,
            font: '500 10px/1 ' + F.mono,
            letterSpacing: '.2em',
            color: C.muted,
          }}
        >
          CLOSE
        </button>
      </div>
    </div>
  )
}

// ------------------------------------------------------------------ badges

export function StatusBadge({ s, small }: { s: string; small?: boolean }) {
  const t = STATUS_STYLE[s] ?? {
    line: C.lineHard,
    fill: C.panelAlt,
    col: C.text3,
  }
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: small ? '3px 8px' : '5px 11px',
        border: '1px solid ' + t.line,
        background: t.fill,
        font: '500 ' + (small ? '9px' : '10px') + '/1 ' + F.mono,
        letterSpacing: '.16em',
        color: t.col,
        whiteSpace: 'nowrap',
      }}
    >
      {s}
    </span>
  )
}

export function TierBadge({ tier }: { tier: string }) {
  const t = TIER_STYLE[tier] ?? TIER_STYLE.RECORD
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 9px',
        border: '1px solid ' + t.line,
        background: t.fill,
        font: '500 9px/1 ' + F.mono,
        letterSpacing: '.16em',
        color: t.col,
      }}
    >
      {tier}
    </span>
  )
}

export function Kicker({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        font: '400 9.5px/1.4 ' + F.mono,
        letterSpacing: '.22em',
        color: C.fainter,
      }}
    >
      {children}
    </div>
  )
}

export function Label({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        font: '400 9px/1.4 ' + F.mono,
        letterSpacing: '.2em',
        color: C.fainter,
      }}
    >
      {children}
    </div>
  )
}

export function Body({
  children,
  style,
}: {
  children: ReactNode
  style?: React.CSSProperties
}) {
  return (
    <p
      style={{
        margin: 0,
        font: '300 13px/1.65 ' + F.sans,
        color: C.text3,
        textWrap: 'pretty',
        ...style,
      }}
    >
      {children}
    </p>
  )
}

export function Panel({
  children,
  style,
  accent,
}: {
  children: ReactNode
  style?: React.CSSProperties
  accent?: string
}) {
  return (
    <section
      style={{
        border: '1px solid ' + C.line,
        borderTop: accent ? '2px solid ' + accent : '1px solid ' + C.line,
        background: C.panel,
        ...style,
      }}
    >
      {children}
    </section>
  )
}

export function PanelHead({
  kicker,
  title,
  right,
}: {
  kicker?: string
  title: ReactNode
  right?: ReactNode
}) {
  return (
    <header
      style={{
        padding: '16px 20px',
        borderBottom: '1px solid ' + C.line,
        display: 'flex',
        gap: '18px',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
        {kicker ? <Kicker>{kicker}</Kicker> : null}
        <h2
          style={{
            margin: 0,
            font: '300 21px/1.2 ' + F.sans,
            letterSpacing: '-.01em',
            color: C.text,
          }}
        >
          {title}
        </h2>
      </div>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        {right}
      </div>
    </header>
  )
}

/** A signed horizontal bar on a shared scale with a dashed zero line.
 *  "A dashed baseline, never a zero line." */
export function MarginBar({
  value,
  scale,
  color,
  bar,
  threshold,
}: {
  value: number
  scale: number
  color?: string
  bar?: number
  threshold?: number
}) {
  const w = Math.min(50, (Math.abs(value) / scale) * 50)
  const pos = value >= 0
  const th =
    threshold === undefined
      ? null
      : 50 + (Math.min(50, (threshold / scale) * 50) * (threshold >= 0 ? 1 : -1))
  return (
    <div
      style={{
        position: 'relative',
        height: (bar ?? 12) + 'px',
        background: C.canvas,
        border: '1px solid ' + C.lineSoft,
      }}
    >
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: 0,
          bottom: 0,
          width: '1px',
          background: 'transparent',
          borderLeft: '1px dashed ' + C.ghost,
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: '2px',
          bottom: '2px',
          left: pos ? '50%' : 50 - w + '%',
          width: w + '%',
          background: color ?? (pos ? C.text2 : C.friction),
        }}
      />
      {th === null ? null : (
        <div
          style={{
            position: 'absolute',
            left: th + '%',
            top: '-2px',
            bottom: '-2px',
            width: '1px',
            background: C.electrical,
          }}
        />
      )}
    </div>
  )
}

// ---------------------------------------------------------- plain English

/**
 * The guide's voice, above the program's.
 *
 * Every screen already opens with a lede written from inside the program.
 * Those ledes are good, and they are the record's own words — but they
 * assume the reader knows what a ruler, a corner, a seed and a duty are.
 * A `Primer` is the sentence that makes the lede legible to someone who
 * does not, and it carries no numeral and no status label, so it stays
 * outside the citation manifest exactly as screen 01 does.
 */
export function Primer({ children }: { children: ReactNode }) {
  return (
    <p
      style={{
        margin: '0 0 14px',
        maxWidth: '820px',
        font: '300 15px/1.65 ' + F.sans,
        color: C.text2,
        textWrap: 'pretty',
      }}
    >
      {children}
    </p>
  )
}

/**
 * What the five frozen labels mean, in English.
 *
 * The labels themselves are read from the record's own allow-list, never
 * typed here, so this can never render a sixth. The glosses say what each
 * label meant at the freeze and nothing more: none of them upgrades a
 * result, and the two that describe unfinished work say so plainly.
 */
const STATUS_GLOSS: Record<string, string> = {
  'FROZEN-RATIFIED':
    'checked, challenged and agreed. The strongest thing this project says.',
  'FROZEN-PROVISIONAL':
    'it passed the test written for it, but the review that would have confirmed it was never run. Frozen as it stood.',
  'FROZEN-KILL':
    'it failed a test that was written down before anyone knew the answer.',
  'NOT CONVERGED':
    'asked more than once, and the answers did not agree. No result.',
  'NOT CUT':
    'never ruled out and never finished — work that was planned when the project stopped.',
}

export function StatusLegend({ allowed }: { allowed: string[] }) {
  return (
    <div
      style={{
        border: '1px solid ' + C.lineSoft,
        background: C.panelAlt,
        padding: '13px 16px',
        marginBottom: '18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}
    >
      <Label>THE LABELS ON THIS SCREEN, IN PLAIN ENGLISH</Label>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit,minmax(230px,1fr))',
          gap: '10px 20px',
        }}
      >
        {allowed.map((a) => (
          <div
            key={a}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '6px',
            }}
          >
            <StatusBadge s={a} small />
            <span
              style={{
                font: '300 11.5px/1.5 ' + F.sans,
                color: C.faint,
              }}
            >
              {STATUS_GLOSS[a] ?? ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * The handful of words each screen borrows from the program's own
 * vocabulary, defined where they are first met. Each screen passes only
 * the terms it actually uses.
 */
const TERM_GLOSS: Record<string, string> = {
  ruler: 'the ordinary diesel truck every design was measured against',
  corner:
    'a harsher version of the same trip — cold, hot and high, or carrying more — used to check the answer holds',
  seed: 'one run of the simulation with its own random variation; every case was run several times',
  duty: 'the kind of driving: stop-start town deliveries, or longer regional runs',
  pp: 'percentage points — the gap between two percentages',
  'per tonne-km':
    'fuel for carrying one tonne of goods one kilometre — the measure the trial judged on',
  'kWh/km': 'energy used per kilometre driven',
  BSFC: 'how much fuel an engine burns for the work it does, at a given speed and load',
  SOC: 'how full the battery is',
}

export function Terms({ of }: { of: string[] }) {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '6px 22px',
        marginBottom: '18px',
        paddingBottom: '14px',
        borderBottom: '1px solid ' + C.lineSoft,
      }}
    >
      {of.map((k) => (
        <span
          key={k}
          style={{
            font: '300 11.5px/1.5 ' + F.sans,
            color: C.faint,
            maxWidth: '330px',
          }}
        >
          <span style={{ fontFamily: F.mono, color: C.text3 }}>{k}</span>
          {' — ' + (TERM_GLOSS[k] ?? '')}
        </span>
      ))}
    </div>
  )
}
