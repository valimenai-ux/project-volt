"""
Project Volt - WS4 - G1-R traction chain (ruling R12) and PM spin-drag
member (G1-R directive 1b), consumed from WS2's exports.

R12 convention implemented here:
  traction side  = WS2 measured inverter+motor maps x 0.97 reduction;
                   NO scalar PE member exists on the traction side.
  genset side    = WS4 generator + active-rectifier loss model (the
                   PE/rectifier stage lives in WS4's ledger).
  All cross-workstream electrical quantities are bus-side.

Hot-swap discipline (G1-R directive preamble): WS2 round 4 re-derives
the maps at 432/662/749 V on the R10 bus. This loader reads WS2's own
results.json interface block, picks the efficiency map keyed nearest
WS2's exported dc_bus.nominal_V, and records the vintage (rework round,
map file, nominal voltage) so the run states which traction chain it
used. When the r4 exports land in ../WS2_traction_motor, re-running
run_ws4.py picks them up with no code change; the vintage fields in
results_ws4.json -> ws2_chain_of_record flip accordingly.

Spin-drag member (directive 1b): WS2 measures the PM traction machine's
unloaded lockup spin as a lockup-only tax (WS2 report section 7 /
cycle_loss_summary.csv): engine-side drag kWh + bus-side draw kWh over
VOLT-REG. Charged to G1 mode (a) during LOCKED samples only, as mean
rates over WS2's own locked time (E_spin / (duration * lockup_frac)),
so each WS4 seed pays proportionally to its actual locked time. Series
operation is loaded operation - its machine losses are in the map, so
modes (b)/(b') carry no spin member (WS2's measurement distinguishes
the two; the old line-111 mode-neutrality claim is superseded).
"""
import csv
import json
import os
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS2_DIR = os.path.join(HERE, "..", "WS2_traction_motor")


# ------------------------------------------------------------ WS2 exports
def load_ws2_exports(ws2_dir=WS2_DIR):
    """Read WS2's results.json + cycle_loss_summary.csv. Returns a dict
    with the chosen efficiency-map path, the vintage record, and the
    spin-drag member (rates + the underlying exported integrals)."""
    with open(os.path.join(ws2_dir, "results.json")) as f:
        j = json.load(f)
    iface = j["interface"]
    vnom = float(iface["dc_bus"]["nominal_V"])
    numeric = {}
    for k, rel in iface["efficiency_maps"].items():
        try:
            numeric[float(k)] = rel
        except ValueError:
            continue
    if not numeric:
        raise RuntimeError("WS2 interface exports no voltage-keyed maps")
    v_key = min(numeric, key=lambda v: abs(v - vnom))
    map_path = os.path.normpath(os.path.join(ws2_dir, numeric[v_key]))
    if not os.path.exists(map_path):
        raise RuntimeError(f"WS2 map file missing: {map_path}")

    # spin-drag member: cycle integrals from cycle_loss_summary.csv
    # (VOLT-REG column; stable export format r3 -> r4)
    cls = {}
    with open(os.path.join(ws2_dir, "data", "cycle_loss_summary.csv")) as f:
        rd = csv.reader(f)
        header = next(rd)
        col = [c for c in range(len(header))
               if "VOLT-REG" in header[c].upper().replace("_", "-")]
        col = col[0] if col else 2
        for row in rd:
            if len(row) > col:
                try:
                    cls[row[0]] = float(row[col])
                except ValueError:
                    pass
    e_spin_shaft = cls["E_spin_shaft_kWh"]
    e_spin_bus = cls["E_spin_bus_kWh"]
    locked_h = cls["duration_h"] * cls["lockup_frac"]
    if locked_h <= 0:
        raise RuntimeError("WS2 cycle_loss_summary has no locked time")

    topo = j.get("topology", {})
    rework = j.get("_meta", {}).get("rework", {})
    return dict(
        eta_mot_avg_VOLT_REG=cls.get("eta_mot_avg"),
        eta_gen_avg_VOLT_REG=cls.get("eta_gen_avg"),
        map_path=map_path,
        map_file_rel=numeric[v_key],
        map_voltage_V=v_key,
        ws2_bus_nominal_V=vnom,
        ws2_rework_round=rework.get("round"),
        ws2_results_date=j.get("_meta", {}).get("date"),
        ratio=float(iface["machine"]["ratio"]),
        spin=dict(
            source=("WS2 data/cycle_loss_summary.csv (VOLT-REG column) + "
                    "results.json topology PM_spin_* members"),
            e_spin_shaft_kWh_per_VOLT_REG=e_spin_shaft,
            e_spin_bus_kWh_per_VOLT_REG=e_spin_bus,
            ws2_locked_hours=locked_h,
            rate_shaft_kW_while_locked=e_spin_shaft / locked_h,
            rate_bus_kW_while_locked=e_spin_bus / locked_h,
            point_check_shaft_drag_85kmh_W=topo.get(
                "PM_spin_shaft_drag_85kmh_W"),
            point_check_bus_draw_85kmh_W=topo.get(
                "PM_spin_bus_draw_85kmh_W")))


# --------------------------------------------------------- traction chain
class WS2TractionChain:
    """R12 traction chain: WS2 measured inverter+motor loss map (bus <->
    motor shaft) x flat 0.97 reduction. No scalar PE member, no
    part_load_factor - the map IS the part-load reality.

    Loss-surface convention: the map's per-cell electrical+iron+mech+
    inverter losses (P_cu+P_fe+P_fw+P_inv) are bilinearly interpolated
    over (rpm, signed torque); infeasible cells are filled from the
    nearest feasible neighbour and query coordinates are clamped to the
    grid, so demands beyond the map's FEASIBLE ENVELOPE reuse the
    boundary loss.

    KX/R23 erratum F2: that convention is NOT mode-neutral in general.
    It is mode-neutral at the reference seed (where the exposure is all
    unlocked launch samples both G1 modes drive identically), but at
    CdA 5.4 the exposure sits predominantly on ~94-98 km/h cruise
    samples, which are LOCKED in mode (a) (served by the engine) and
    clamp-served only in mode (b) - i.e. one-sided in (b)'s favour.
    `boundary_exposure()` below measures it per condition and
    `boundary_excess_loss_kw()` bounds the understated loss by
    extrapolating the loss surface past the feasible boundary with its
    own one-sided torque gradient [WS4-DECLARED extrapolation]. The
    measured magnitudes are exported in results_ws4.json ->
    chain_boundary_exposure and rendered in REPORT_WS4.md s4.1.

    Note the R3 over-RATING counter (>150 kW motor shaft) is a
    different, stricter boundary: those samples lie INSIDE the map
    envelope (feasible to ~175-185 kW at cruise rpm) and receive true
    interpolated losses; they stay counted and energy-bookkept, not
    clipped.
    """

    def __init__(self, map_path, ratio, r_dyn, eta_red=0.97):
        self.map_path = map_path
        self.ratio = float(ratio)
        self.r_dyn = float(r_dyn)
        self.eta_red = float(eta_red)
        raw = np.genfromtxt(map_path, delimiter=",", names=True)
        rpms = np.unique(raw["rpm"])
        trqs = np.unique(raw["T_shaft_Nm"])
        loss = np.full((rpms.size, trqs.size), np.nan)
        ir = np.searchsorted(rpms, raw["rpm"])
        it = np.searchsorted(trqs, raw["T_shaft_Nm"])
        feas = raw["feasible"] == 1
        total = (raw["P_cu_kW"] + raw["P_fe_kW"] + raw["P_fw_kW"]
                 + raw["P_inv_kW"])
        loss[ir[feas], it[feas]] = total[feas]
        self.n_feasible = int(feas.sum())
        # nearest-neighbour fill of infeasible cells (iterative dilation)
        for _ in range(max(rpms.size, trqs.size)):
            nan = np.isnan(loss)
            if not nan.any():
                break
            padded = np.full((loss.shape[0] + 2, loss.shape[1] + 2), np.nan)
            padded[1:-1, 1:-1] = loss
            neigh = np.stack([padded[0:-2, 1:-1], padded[2:, 1:-1],
                              padded[1:-1, 0:-2], padded[1:-1, 2:]])
            with np.errstate(all="ignore"), warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                fill = np.nanmean(neigh, axis=0)
            loss[nan] = fill[nan]
        self.rpms, self.trqs, self.loss = rpms, trqs, loss
        # --- KX/F2 instrumentation: which grid cells were ORIGINALLY
        # feasible, and the feasible torque envelope per rpm column.
        # Pure bookkeeping - it touches no interpolated value, so every
        # ratified number is reproduced bit-identically.
        feas_grid = np.zeros((rpms.size, trqs.size), dtype=bool)
        feas_grid[ir[feas], it[feas]] = True
        self.feas_grid = feas_grid
        big = float(trqs[-1] - trqs[0]) + 1.0
        tmax_col = np.where(feas_grid.any(axis=1),
                            np.max(np.where(feas_grid, trqs[None, :],
                                            -big), axis=1), 0.0)
        tmin_col = np.where(feas_grid.any(axis=1),
                            np.min(np.where(feas_grid, trqs[None, :],
                                            big), axis=1), 0.0)
        self.t_feas_max_col, self.t_feas_min_col = tmax_col, tmin_col

    def _cell_index(self, rpm, trq):
        """Grid cell (i, j) used by the bilinear stencil, plus the
        clamped coordinates - mirrors _interp_loss exactly."""
        r = np.clip(np.asarray(rpm, float), self.rpms[0], self.rpms[-1])
        t = np.clip(np.asarray(trq, float), self.trqs[0], self.trqs[-1])
        i = np.clip(np.searchsorted(self.rpms, r) - 1, 0, self.rpms.size - 2)
        j = np.clip(np.searchsorted(self.trqs, t) - 1, 0, self.trqs.size - 2)
        return i, j, r, t

    def boundary_exposure(self, rpm, trq):
        """Boolean mask: query used at least one ORIGINALLY-INFEASIBLE
        grid cell in its bilinear stencil, or had a coordinate clamped
        to the grid - i.e. it is served at the boundary loss rather than
        at a measured one (KX/F2)."""
        i, j, r, t = self._cell_index(rpm, trq)
        stencil_ok = (self.feas_grid[i, j] & self.feas_grid[i + 1, j]
                      & self.feas_grid[i, j + 1] & self.feas_grid[i + 1, j + 1])
        clamped = ((np.asarray(rpm, float) != r)
                   | (np.asarray(trq, float) != t))
        return (~stencil_ok) | clamped

    def boundary_exposure_strict(self, rpm, trq):
        """Stricter boundary test: the query torque lies OUTSIDE the
        feasible torque envelope of its nearest rpm column (or a
        coordinate is clamped). This is the criterion the r3 adjudicator
        measured against; `boundary_exposure` is a superset of it,
        because a stencil can straddle an infeasible cell while the
        query itself is still inside the envelope."""
        rpm = np.asarray(rpm, float)
        trq = np.asarray(trq, float)
        k = self._nearest_rpm_col(rpm)
        clamped = ((rpm < self.rpms[0]) | (rpm > self.rpms[-1])
                   | (trq < self.trqs[0]) | (trq > self.trqs[-1]))
        return ((trq > self.t_feas_max_col[k])
                | (trq < self.t_feas_min_col[k]) | clamped)

    def _nearest_rpm_col(self, rpm):
        rpm = np.asarray(rpm, float)
        k = np.clip(np.searchsorted(self.rpms, rpm), 0, self.rpms.size - 1)
        return np.where((k > 0)
                        & (np.abs(self.rpms[np.clip(k - 1, 0, None)] - rpm)
                           <= np.abs(self.rpms[k] - rpm)), k - 1, k)

    def boundary_excess_loss_kw(self, rpm, trq):
        """[WS4-DECLARED bound] Additional loss [kW] the clamped
        convention does NOT book, obtained by extending the loss surface
        past the feasible torque boundary of the nearest rpm column with
        that column's own one-sided torque gradient. Zero inside the
        envelope. Copper loss grows as T^2, so a linear extension is a
        LOWER bound on the true understatement; the hostile variant in
        run_ws4.py doubles the gradient."""
        rpm = np.asarray(rpm, float)
        trq = np.asarray(trq, float)
        k = self._nearest_rpm_col(rpm)
        t_hi = self.t_feas_max_col[k]
        t_lo = self.t_feas_min_col[k]
        dt = float(self.trqs[1] - self.trqs[0])
        # one-sided gradients at each column's feasible boundary
        j_hi = np.clip(np.searchsorted(self.trqs, t_hi), 1, self.trqs.size - 1)
        j_lo = np.clip(np.searchsorted(self.trqs, t_lo), 0,
                       self.trqs.size - 2)
        g_hi = np.maximum((self.loss[k, j_hi] - self.loss[k, j_hi - 1]) / dt,
                          0.0)
        g_lo = np.maximum((self.loss[k, j_lo] - self.loss[k, j_lo + 1]) / dt,
                          0.0)
        over_hi = np.clip(trq - t_hi, 0.0, None)
        over_lo = np.clip(t_lo - trq, 0.0, None)
        return g_hi * over_hi + g_lo * over_lo

    def motor_rpm_and_torque(self, v, p_wheel_kw, motoring=True):
        """The (rpm, signed torque) the chain actually queries for a
        wheel-power demand - exposed so the boundary diagnostics use the
        identical coordinates as the loss lookup."""
        v = np.asarray(v, float)
        p = np.asarray(p_wheel_kw, float)
        w, rpm = self._motor_speed(v)
        if motoring:
            p_ms = np.where(p > 0.0, p, 0.0) / self.eta_red
            trq = np.where(w > 1e-6, p_ms * 1e3 / np.maximum(w, 1e-6), 0.0)
        else:
            p_ms = np.where(p > 1e-9, p, 0.0) * self.eta_red
            trq = np.where(w > 1e-6, -p_ms * 1e3 / np.maximum(w, 1e-6), 0.0)
        return rpm, trq

    def _interp_loss(self, rpm, trq):
        """Bilinear interpolation of the loss surface [kW], coordinates
        clamped to the grid (boundary-loss extension, see class doc)."""
        r = np.clip(np.asarray(rpm, float), self.rpms[0], self.rpms[-1])
        t = np.clip(np.asarray(trq, float), self.trqs[0], self.trqs[-1])
        i = np.clip(np.searchsorted(self.rpms, r) - 1, 0, self.rpms.size - 2)
        j = np.clip(np.searchsorted(self.trqs, t) - 1, 0, self.trqs.size - 2)
        fr = (r - self.rpms[i]) / (self.rpms[i + 1] - self.rpms[i])
        ft = (t - self.trqs[j]) / (self.trqs[j + 1] - self.trqs[j])
        z = (self.loss[i, j] * (1 - fr) * (1 - ft)
             + self.loss[i + 1, j] * fr * (1 - ft)
             + self.loss[i, j + 1] * (1 - fr) * ft
             + self.loss[i + 1, j + 1] * fr * ft)
        return z

    def _motor_speed(self, v):
        w = np.asarray(v, float) / self.r_dyn * self.ratio     # rad/s
        return w, w * 60.0 / (2 * np.pi)

    def eta_bus_to_wheel(self, v, p_wheel_kw):
        """Chain efficiency bus->wheel (motoring) per sample; 1.0 where
        p_wheel <= 0 (unused there)."""
        v = np.asarray(v, float)
        pw = np.asarray(p_wheel_kw, float)
        w, rpm = self._motor_speed(v)
        drive = pw > 0.0
        p_ms = np.where(drive, pw, 0.0) / self.eta_red
        trq = np.where(w > 1e-6, p_ms * 1e3 / np.maximum(w, 1e-6), 0.0)
        loss = self._interp_loss(rpm, trq)
        p_dc = p_ms + loss
        eta = np.where(drive & (p_dc > 1e-9),
                       np.where(drive, pw, 0.0) / np.maximum(p_dc, 1e-9),
                       1.0)
        return np.clip(eta, 1e-3, 1.0)

    def eta_wheel_to_bus(self, v, p_capt_kw):
        """Chain efficiency wheel->bus (generating) per sample; 0.0 where
        nothing is captured (matches the sim's eta_rg>0 guards)."""
        v = np.asarray(v, float)
        pc = np.asarray(p_capt_kw, float)
        w, rpm = self._motor_speed(v)
        gen = pc > 1e-9
        p_ms = np.where(gen, pc, 0.0) * self.eta_red
        trq = np.where(w > 1e-6, -p_ms * 1e3 / np.maximum(w, 1e-6), 0.0)
        loss = self._interp_loss(rpm, trq)
        p_dc = np.clip(p_ms - loss, 0.0, None)
        eta = np.where(gen, p_dc / np.maximum(pc, 1e-9), 0.0)
        return np.clip(eta, 0.0, 1.0)

    def eta_bus_to_wheel_scalar(self, v, p_wheel_kw):
        return float(self.eta_bus_to_wheel(np.array([v]),
                                           np.array([p_wheel_kw]))[0])

    def eta_bus_to_wheel_marginal_scalar(self, v, p_wheel_kw):
        """Marginal chain efficiency for torque-fill DURING lockup, where
        the machine's no-load losses are already charged through the
        spin-drag member: the map loss is taken as loss(rpm, T) -
        loss(rpm, 0), so the no-load member is not double-counted
        (G1-R pre-adjudication fix; the full-loss form overcharged mode
        (a) by ~0.03-0.06 pp)."""
        w, rpm = self._motor_speed(np.array([float(v)]))
        p_ms = float(p_wheel_kw) / self.eta_red
        trq = p_ms * 1e3 / max(float(w[0]), 1e-6)
        loss = float(self._interp_loss(rpm, np.array([trq]))[0]
                     - self._interp_loss(rpm, np.array([0.0]))[0])
        p_dc = p_ms + max(loss, 0.0)
        return float(np.clip(float(p_wheel_kw) / max(p_dc, 1e-9),
                             1e-3, 1.0))
