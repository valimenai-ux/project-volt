import type { TraceEntry } from './types'

// TRACE_SCHEMA.md, R34. Re-stated here so the loader validates at run time
// rather than trusting the build.
export const SCHEMA_HEADER_KEYS = [
  'program', 'workstream', 'round', 'vehicle', 'architecture', 'duty',
  'corner', 'seed', 'mass_kg', 'payload_kg', 'baseline_version',
  'results_file', 'results_sha256', 'generated_utc',
]

export const SCHEMA_CORE_COLUMNS = [
  't_s', 'x_m', 'v_kmh', 'grade_pct', 'z_m', 'P_wheel_kW', 'fuel_g_per_s',
  'fuel_cum_g', 'P_friction_brake_kW', 'trip_time_flag',
]

// "pack -> heater -> resistor -> friction; the four must sum to the braking
// demand served electrically plus friction". Tolerance is the file's own
// printing precision, not a fudge factor: the conforming traces print six
// significant figures, so a residual within one part in 1e5 of the largest
// term is a rounding artefact. Same rule as ws12_traces.py.
export const BLEND_REL_TOLERANCE = 1e-5
export const BLEND_FLOOR_KW = 1e-4

export function blendTolerance(maxTerm: number) {
  return Math.max(BLEND_FLOOR_KW, BLEND_REL_TOLERANCE * Math.abs(maxTerm))
}

export interface Loaded {
  cols: string[]
  ix: Record<string, number>
  n: number
  col: (name: string) => Float64Array
  raw: string[][]
}

function parse(textBody: string): { cols: string[]; raw: string[][] } {
  const lines = textBody.split('\n')
  while (lines.length && lines[lines.length - 1] === '') lines.pop()
  const cols = lines[0].split(',')
  const raw: string[][] = []
  for (let i = 1; i < lines.length; i++) raw.push(lines[i].split(','))
  return { cols, raw }
}

function pack(cols: string[], raw: string[][]): Loaded {
  const ix: Record<string, number> = {}
  cols.forEach((c, i) => (ix[c] = i))
  const cache: Record<string, Float64Array> = {}
  return {
    cols,
    ix,
    n: raw.length,
    raw,
    col(name: string) {
      if (!cache[name]) {
        const j = ix[name]
        const a = new Float64Array(raw.length)
        if (j !== undefined) for (let i = 0; i < raw.length; i++) a[i] = +raw[i][j]
        cache[name] = a
      }
      return cache[name]
    },
  }
}

const BASE = import.meta.env.BASE_URL

export async function loadScrub(t: TraceEntry): Promise<Loaded> {
  const r = await fetch(BASE + t.urlBase + '/scrub_1hz.csv')
  if (!r.ok) throw new Error('scrub tier unavailable: HTTP ' + r.status)
  const { cols, raw } = parse(await r.text())
  return pack(cols, raw)
}

const segCache = new Map<string, Loaded>()

export async function loadSegment(t: TraceEntry, i: number): Promise<Loaded> {
  const seg = t.segments[i]
  if (!seg) throw new Error('no such segment')
  const key = t.id + '/' + seg.file
  const hit = segCache.get(key)
  if (hit) return hit
  const r = await fetch(BASE + t.urlBase + '/' + seg.file)
  if (!r.ok) throw new Error('detail tier unavailable: HTTP ' + r.status)
  const { cols, raw } = parse(await r.text())
  const out = pack(cols, raw)
  segCache.set(key, out)
  return out
}

export interface RunCheck {
  ok: boolean
  reasons: string[]
  missingHeaderKeys: string[]
  missingCoreColumns: string[]
  blend: {
    checked: boolean
    busWorst: number
    busSamples: number
    wheelWorst: number
    wheelSamples: number
  }
}

/**
 * The run-time TRACE_SCHEMA check. A file that fails it is not plotted;
 * the screen shows this object instead.
 */
export function validateLoaded(t: TraceEntry, d: Loaded): RunCheck {
  const reasons: string[] = []
  const missingHeaderKeys = SCHEMA_HEADER_KEYS.filter(
    (k) => !(k in (t.meta ?? {})),
  )
  // Only columns the exhibit publishes can be checked here; withheld
  // columns are listed in the trace entry and are not treated as absent
  // from the record.
  const present = new Set([...t.columnsPublished, ...t.columnsWithheld])
  const missingCoreColumns = SCHEMA_CORE_COLUMNS.filter((c) => !present.has(c))

  let busWorst = 0
  let busSamples = 0
  let busFail = false
  let wheelWorst = 0
  let wheelSamples = 0
  let wheelFail = false
  const haveBus =
    d.ix['P_regen_pack_kW'] !== undefined &&
    d.ix['P_heater_kW'] !== undefined &&
    d.ix['P_resistor_kW'] !== undefined &&
    d.ix['P_motor_bus_kW'] !== undefined
  const haveWheel =
    d.ix['P_motor_mech_kW'] !== undefined &&
    d.ix['P_friction_brake_kW'] !== undefined &&
    d.ix['P_wheel_kW'] !== undefined
  if (haveBus) {
    const rg = d.col('P_regen_pack_kW')
    const he = d.col('P_heater_kW')
    const rs = d.col('P_resistor_kW')
    const mb = d.col('P_motor_bus_kW')
    for (let i = 0; i < d.n; i++) {
      if (mb[i] < 0) {
        const res = Math.abs(rg[i] + he[i] + rs[i] + mb[i])
        const tol = blendTolerance(
          Math.max(Math.abs(rg[i]), Math.abs(he[i]), Math.abs(rs[i]), Math.abs(mb[i])),
        )
        if (res > tol) busFail = true
        busWorst = Math.max(busWorst, res)
        busSamples++
      }
    }
  }
  if (haveWheel) {
    const mm = d.col('P_motor_mech_kW')
    const fr = d.col('P_friction_brake_kW')
    const pw = d.col('P_wheel_kW')
    for (let i = 0; i < d.n; i++) {
      if (pw[i] < 0) {
        const res = Math.abs(-mm[i] + fr[i] + pw[i])
        const tol = blendTolerance(
          Math.max(Math.abs(mm[i]), Math.abs(fr[i]), Math.abs(pw[i])),
        )
        if (res > tol) wheelFail = true
        wheelWorst = Math.max(wheelWorst, res)
        wheelSamples++
      }
    }
  }

  if (missingHeaderKeys.length)
    reasons.push(
      'TRACE_SCHEMA header keys missing: ' + missingHeaderKeys.join(', '),
    )
  if (missingCoreColumns.length)
    reasons.push(
      'TRACE_SCHEMA core columns missing: ' + missingCoreColumns.join(', '),
    )
  const blendChecked = haveBus || haveWheel
  if (blendChecked && (busFail || wheelFail))
    reasons.push('the R15 blend-order sum rule does not close on this file')

  return {
    ok: reasons.length === 0,
    reasons,
    missingHeaderKeys,
    missingCoreColumns,
    blend: {
      checked: blendChecked,
      busWorst,
      busSamples,
      wheelWorst,
      wheelSamples,
    },
  }
}
