// The draft's visual system, preserved. An instrument, not an interface:
// panels divided by hairlines on one grid, nothing floats, nothing rounds,
// nothing glows, numerals hold still.

export const C = {
  page: '#07080a',
  canvas: '#0e1114',
  header: '#111519',
  rail: '#101418',
  panel: '#12171c',
  panelAlt: '#151b21',
  line: '#232a33',
  lineSoft: '#1c232b',
  lineHard: '#2b333d',

  text: '#e6eaef',
  text2: '#c7d0da',
  text3: '#a9b6c6',
  muted: '#8d99a8',
  faint: '#6f7b8a',
  fainter: '#5c6674',
  ghost: '#4b5563',

  // Palette semantics, from the draft's style guide.
  electrical: '#46cfe0',
  electricalLo: '#8ae3ee',
  electricalBg: '#0f2a2e',
  electricalLine: '#2b6f7a',

  mechanical: '#f0c419',
  mechanicalBg: '#221b0c',
  mechanicalLine: '#7a5a2b',

  heat: '#e2603a',
  friction: '#78838f',

  recordLine: '#4a5665',
  recordBg: '#1b222a',
} as const

export const F = {
  sans: 'Chivo, system-ui, -apple-system, sans-serif',
  mono: "'DM Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
} as const

export const TIER_STYLE: Record<
  string,
  { line: string; fill: string; col: string }
> = {
  RECORD: { line: C.recordLine, fill: C.recordBg, col: C.text },
  DERIVED: { line: C.electricalLine, fill: C.electricalBg, col: C.electricalLo },
  SANDBOX: { line: C.mechanicalLine, fill: C.mechanicalBg, col: C.mechanical },
}

export const STATUS_STYLE: Record<
  string,
  { line: string; fill: string; col: string }
> = {
  'FROZEN-RATIFIED': { line: '#3f5a4a', fill: '#111c17', col: '#9fd3b4' },
  'FROZEN-PROVISIONAL': { line: '#5a5330', fill: '#1b1810', col: '#d9c98a' },
  'FROZEN-KILL': { line: '#6b3a30', fill: '#1e120f', col: '#e29a86' },
  'NOT CONVERGED': { line: '#5c4a6b', fill: '#171221', col: '#c3a8dd' },
  'NOT CUT': { line: '#3f5460', fill: '#111a20', col: '#9fc2d3' },
}
