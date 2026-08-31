// The TypeScript twin of ws12_sandbox.py. Same two closed forms, same
// program constant. The Sandbox screen shows this function's output for
// the record's own cases beside the record's own values, so a divergence
// between the two implementations would be visible on the page.

export const G = 9.81

export interface Force {
  aero_N: number
  roll_N: number
  grade_N: number
  total_N: number
}

export function roadLoadN(
  m: number,
  CdA: number,
  Crr: number,
  rho: number,
  vMs: number,
  grade: number,
): Force {
  const th = Math.atan(grade)
  const aero = 0.5 * rho * CdA * vMs * vMs
  const roll = Crr * m * G * Math.cos(th)
  const grd = m * G * Math.sin(th)
  return { aero_N: aero, roll_N: roll, grade_N: grd, total_N: aero + roll + grd }
}

/** WS8's published physics bound, in its own words:
 *  ratio <= rpm_ceiling * 2*pi * r_dyn / (60 * v_cruise) */
export function ratioCeiling(
  rpmCeiling: number,
  rDyn: number,
  vCruiseMs: number,
): number {
  return (rpmCeiling * 2 * Math.PI * rDyn) / (60 * vCruiseMs)
}

/** The same statement, inverted: the ratio at which peak torque through
 *  the driveline just balances the road load. */
export function ratioRequired(
  F: number,
  rDyn: number,
  tPeak: number,
  eta: number,
): number {
  return (F * rDyn) / (tPeak * eta)
}

export interface Endpoint {
  m_kg: number
  CdA_m2: number
  Crr: number
  rho_air: number
  r_dyn_m: number
  v_cruise_kmh: number
  eta_driveline: number
  T_peak_Nm: number
  rpm_ceiling: number
  v_climb_kmh: number
}

const LERP_KEYS = [
  'CdA_m2', 'Crr', 'r_dyn_m', 'v_cruise_kmh', 'eta_driveline', 'T_peak_Nm',
  'rpm_ceiling', 'v_climb_kmh',
] as const

export interface Window {
  rMin: number
  rMax: number
  open: boolean
  force: Force
  params: Record<string, number>
}

export function ratioWindow(
  mass: number,
  grade: number,
  rho: number,
  lo: Endpoint,
  hi: Endpoint,
): Window {
  let f = (mass - lo.m_kg) / (hi.m_kg - lo.m_kg)
  f = Math.max(0, Math.min(1, f))
  const p: Record<string, number> = {}
  for (const k of LERP_KEYS) p[k] = lo[k] + (hi[k] - lo[k]) * f
  const F = roadLoadN(mass, p.CdA_m2, p.Crr, rho, p.v_climb_kmh / 3.6, grade)
  const rMax = ratioCeiling(p.rpm_ceiling, p.r_dyn_m, p.v_cruise_kmh / 3.6)
  const rMin = ratioRequired(F.total_N, p.r_dyn_m, p.T_peak_Nm, p.eta_driveline)
  return { rMin, rMax, open: rMin <= rMax, force: F, params: p }
}

export function crossingMass(
  grade: number,
  rho: number,
  lo: Endpoint,
  hi: Endpoint,
): number | null {
  let a = lo.m_kg
  let b = hi.m_kg
  if (ratioWindow(b, grade, rho, lo, hi).open) return null
  if (!ratioWindow(a, grade, rho, lo, hi).open) return a
  for (let k = 0; k < 60; k++) {
    const mid = (a + b) / 2
    if (ratioWindow(mid, grade, rho, lo, hi).open) a = mid
    else b = mid
  }
  return (a + b) / 2
}
