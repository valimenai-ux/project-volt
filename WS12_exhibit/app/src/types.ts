// Shapes emitted by build_exhibit_data.py. The app renders `s` and only
// `s`; every other field exists so a visitor can see where `s` came from.

export type Tier = 'RECORD' | 'DERIVED' | 'SANDBOX'

export interface Cited {
  s: string
  tier: Tier
  v?: number | string | boolean
  file?: string
  path?: (string | number)[]
  pathText?: string
  fmt?: string
  pre?: string
  suf?: string
  kind?: 'quote' | 'file'
  sha256?: string
  bytes?: number
  derivedFrom?: string
  note?: string
  probe?: string
}

export interface Segment {
  i: number
  file: string
  rows: number
  row0: number
}

export interface TraceEntry {
  id: string
  use: string
  sourcePath: string
  sourceSha256: string
  sourceRows: number
  stride: number
  outputRows1Hz: number
  segmentRows: number
  segments: Segment[]
  columnsPublished: string[]
  columnsWithheld: string[]
  schemaClass: string
  schemaConforms: boolean
  headerLines: string[]
  meta: Record<string, string>
  urlBase: string
}

export interface BlendOrder {
  checked: boolean
  passes?: boolean
  bus_worst_kW?: number
  bus_samples?: number
  wheel_worst_kW?: number
  wheel_samples?: number
  tolerance_kW?: number
  rule?: string
  why?: string
}

export interface Validation {
  schemaClass: string
  conforms: boolean
  reasons: string[]
  missingHeaderKeys: string[]
  missingCoreColumns: string[]
  missingEngineColumns: string[]
  missingElectrifiedColumns: string[]
  declaredAbsentByDesign: string[]
  blendOrder: BlendOrder
}

export interface RegistryRow {
  ws: string
  file: string
  bytes: number
  rows: number
  columns: string[]
  nColumns: number
  validation: Validation
  servedByExhibit: boolean
  resultsShaDeclared?: string | null
  resultsShaMatchesDisk?: boolean | null
}

// The bundle is walked structurally by the screens; typing it exhaustively
// would duplicate the builder without adding a check the verifier does not
// already make, so the screens read it through narrow local types.
export type Bundle = any
