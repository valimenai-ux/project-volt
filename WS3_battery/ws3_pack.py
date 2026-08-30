"""
Project Volt - WS3 Battery Pack
Pack-level electro-thermal model, capability maps, duty-trace processing
(current solve, heat, rainflow cycle counting) and the descent /
preconditioning simulations.

Sign convention for pack terminal power P_term (at the DC bus):
  P_term > 0 : discharge (pack delivers to the bus)
  P_term < 0 : charge (bus delivers to the pack)
"""
import numpy as np
import ws3_cells as wc

# ------------------------------------------------- pack packaging overhead
# [WS3-ASSUMPTION] prototype-class liquid-cooled pack: cell mass x 1.55
# plus 35 kg fixed (enclosure, cold plates, busbars, BMS, contactors,
# fusing, coolant fill); volume = cell volume x 2.3 installed envelope.
# WS6 confirms packaging; these are handed over as estimates.
MASS_OVERHEAD_FACTOR = 1.55
MASS_OVERHEAD_FIXED_KG = 35.0
VOL_OVERHEAD_FACTOR = 2.3

# Thermal model [WS3-ASSUMPTION]
COUPLED_STRUCTURE_KG = 45.0       # aluminium plates/busbars riding the cell node
CP_STRUCTURE = 900.0              # J/kgK
UA_CELLS_TO_COOLANT = 500.0       # W/K  (288 cells x ~1.7 W/K via bottom plate)
UA_RADIATOR = 350.0               # W/K  coolant loop to ambient air (spec)
T_CELL_MAX_CONT = 55.0            # C    continuous ceiling
T_CELL_CUTOFF = 60.0              # C    hard cutoff
ETA_BATT = 0.97                   # WS1's scalar, kept ONLY to convert WS1
                                  # stored-energy traces back to terminal power


class Pack:
    def __init__(self, cell_name, ns, np_par=1):
        self.cell_name = cell_name
        self.cell = wc.CELLS[cell_name]
        self.ns = int(ns)
        self.np = int(np_par)
        c = self.cell
        self.n_cells = self.ns * self.np
        self.ah = c["ah"] * self.np
        self.nameplate_kwh = self.n_cells * c["ah"] * c["v_nom"] / 1e3
        self.v_nom = self.ns * c["v_nom"]
        self.cell_mass_kg = self.n_cells * c["mass_kg"]
        self.mass_kg = self.cell_mass_kg * MASS_OVERHEAD_FACTOR + MASS_OVERHEAD_FIXED_KG
        self.vol_L = self.n_cells * c["vol_L"] * VOL_OVERHEAD_FACTOR
        self.c_th = self.cell_mass_kg * c["cp_J_kgK"] + \
            COUPLED_STRUCTURE_KG * CP_STRUCTURE          # J/K on the cell node

    # ---------------------------------------------------------- capability
    def v_window(self, soc_lo, soc_hi):
        return (self.ns * float(wc.ocv(soc_lo, self.cell)),
                self.ns * float(wc.ocv(soc_hi, self.cell)))

    def p_dis_pulse10(self, temp_c, soc):
        """Max 10-s discharge power at the terminals [W]."""
        c = self.cell
        u = wc.ocv(soc, c)
        r = wc.r_cell(temp_c, soc, c)
        i_v = (u - c["v_min"]) / r                       # terminal-V floor
        i_c = wc.dis_c_limit(temp_c, c, pulse=True) * c["ah"]
        i = np.minimum(i_v, i_c)
        i = np.maximum(i, 0.0)
        return self.ns * self.np * i * (u - i * r)

    def p_chg_pulse10(self, temp_c, soc):
        """Max 10-s charge power at the terminals [W, positive number]."""
        c = self.cell
        u = wc.ocv(soc, c)
        r = wc.r_cell(temp_c, soc, c)
        i_v = np.maximum(0.0, (c["v_max_protect"] - u) / r)
        i_c = wc.chg_accept_c(temp_c, c, pulse=True) * c["ah"]
        i = np.minimum(i_v, i_c)
        return self.ns * self.np * i * (u + i * r)

    def p_chg_cont(self, temp_c, soc):
        """Continuous charge acceptance at the terminals [W, positive].
        C-limit vs temperature plus the charge-ceiling voltage limit."""
        c = self.cell
        u = wc.ocv(soc, c)
        r = wc.r_cell(temp_c, soc, c)
        i_v = np.maximum(0.0, (c["v_chg_ceiling"] - u) / r)
        i_c = wc.chg_accept_c(temp_c, c, pulse=False) * c["ah"]
        i = np.minimum(i_v, i_c)
        return self.ns * self.np * i * (u + i * r)

    # ------------------------------------------------------- current solve
    def solve_current(self, p_term_w, soc, temp_c):
        """Per-string cell current [A] and per-cell heat [W] for a pack
        terminal power. Vectorised. Discharge: p = I*(U - I R); charge
        (p<0): |p| = I*(U + I R). Returns (I signed +discharge, heat/cell,
        v_cell terminal)."""
        c = self.cell
        p_cell = np.asarray(p_term_w, float) / (self.ns * self.np)
        u = wc.ocv(soc, c)
        r = wc.r_cell(temp_c, soc, c)
        i = np.zeros_like(p_cell)
        dis = p_cell > 0
        chg = p_cell < 0
        # discharge root: I = (U - sqrt(U^2 - 4 R p)) / (2R)
        disc = u**2 - 4.0 * r * np.where(dis, p_cell, 0.0)
        disc = np.maximum(disc, 0.0)   # infeasible demand -> V-floor current
        i = np.where(dis, (u - np.sqrt(disc)) / (2.0 * r), i)
        # charge root: I = (-U + sqrt(U^2 + 4 R |p|)) / (2R)
        disc2 = u**2 + 4.0 * r * np.where(chg, -p_cell, 0.0)
        i = np.where(chg, -(-u + np.sqrt(disc2)) / (2.0 * r), i)
        heat = i**2 * r
        v_t = u - i * r          # discharge sags, charge rises (i<0)
        return i, heat, v_t

    # ------------------------------------------------------------- thermal
    def thermal_step(self, t_cell, q_cells_w, t_amb, dt, cooling=True,
                     heater_w=0.0, ua_rad=UA_RADIATOR):
        """One lumped-node step. Coolant treated quasi-statically: the
        loop temperature settles so that radiator rejection equals the
        heat pulled off the cells; heater power (preconditioning) enters
        the cell node through the same plates."""
        if cooling:
            ua = 1.0 / (1.0 / UA_CELLS_TO_COOLANT + 1.0 / ua_rad)
        else:
            ua = 3.0    # W/K parasitic to ambient, enclosure only
        q_net = q_cells_w + heater_w - ua * (t_cell - t_amb)
        return t_cell + q_net * dt / self.c_th

    def steady_cell_temp(self, q_cells_w, t_amb, ua_rad=UA_RADIATOR):
        ua = 1.0 / (1.0 / UA_CELLS_TO_COOLANT + 1.0 / ua_rad)
        return t_amb + q_cells_w / ua


# ---------------------------------------------------------------- rainflow
def rainflow(series):
    """ASTM E1049 rainflow (four-point) on a 1-D series. Returns list of
    (range, count) with count 1.0 for closed and 0.5 for residual
    half-cycles. Input is reduced to turning points first."""
    x = np.asarray(series, float)
    if x.size < 3:
        return []
    # turning-point extraction
    tps = [x[0]]
    for k in range(1, x.size - 1):
        if (x[k] - tps[-1]) * (x[k + 1] - x[k]) < 0:
            tps.append(x[k])
    tps.append(x[-1])
    stack, out = [], []
    for pt in tps:
        stack.append(pt)
        while len(stack) >= 4:
            x1, x2, x3, x4 = stack[-4], stack[-3], stack[-2], stack[-1]
            r_inner = abs(x3 - x2)
            if r_inner <= abs(x2 - x1) and r_inner <= abs(x4 - x3):
                out.append((r_inner, 1.0))
                del stack[-3:-1]
            else:
                break
    for k in range(len(stack) - 1):
        out.append((abs(stack[k + 1] - stack[k]), 0.5))
    return [(r, c) for (r, c) in out if r > 0.0]


def fatigue_summary(e_batt_j, nameplate_kwh, efc100):
    """Rainflow the stored-energy trace [J]; DoD in fractions of nameplate.
    Throughput damage model N(D) = efc100 / D  =>  damage = sum(n*D)/efc100.
    Returns dict with cycle counts by depth bin and damage per trace."""
    e_kwh = np.asarray(e_batt_j, float) / 3.6e6
    cyc = rainflow(e_kwh)
    if not cyc:
        return dict(n_cycles=0.0, damage=0.0, depth_bins={})
    rng = np.array([r for r, _ in cyc]) / nameplate_kwh    # DoD fraction
    cnt = np.array([c for _, c in cyc])
    damage = float(np.sum(cnt * rng) / efc100)
    edges = np.array([0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 1.00])
    labels = ["<0.5%", "0.5-1%", "1-2%", "2-5%", "5-10%", "10-20%", ">20%"]
    hist = {}
    for k, lab in enumerate(labels):
        m = (rng >= edges[k]) & (rng < edges[k + 1])
        hist[lab] = float(np.sum(cnt[m]))
    return dict(n_cycles=float(np.sum(cnt)), damage=damage, depth_bins=hist)


# ------------------------------------------------- WS1-trace post-processing
def terminal_power_from_ws1(p_batt_stored):
    """WS1's battery_trace() returns d(stored)/dt with its 0.97 scalars
    already applied. Undo them to get terminal (bus-side) power, then use
    the WS3 resistance model for real losses. +discharge convention."""
    p = -np.asarray(p_batt_stored, float)      # WS1: +charging
    return np.where(p > 0, p * ETA_BATT, p / ETA_BATT)


def duty_stats(pack, t, p_term, soc_trace, temp_c):
    """Electro-thermal statistics of one duty trace at fixed cell temp."""
    i, heat_cell, v_t = pack.solve_current(p_term, soc_trace, temp_c)
    dt = np.gradient(np.asarray(t, float))
    q_pack = heat_cell * pack.n_cells
    e_loss = float(np.sum(q_pack * dt))                    # J
    thru_dis = float(np.sum(np.clip(p_term, 0, None) * dt))
    thru_chg = float(np.sum(-np.clip(p_term, None, 0) * dt))
    # energy-weighted one-way efficiencies (loss split by direction)
    loss_dis = float(np.sum(q_pack * dt * (p_term > 0)))
    loss_chg = float(np.sum(q_pack * dt * (p_term < 0)))
    eta_dis = thru_dis / (thru_dis + loss_dis) if thru_dis > 0 else 1.0
    eta_chg = 1.0 - loss_chg / thru_chg if thru_chg > 0 else 1.0
    c_rate = i / pack.cell["ah"]
    return dict(
        peak_dis_kW=float(np.max(np.clip(p_term, 0, None))) / 1e3,
        peak_chg_kW=float(np.max(-np.clip(p_term, None, 0))) / 1e3,
        peak_c_dis=float(np.max(np.clip(c_rate, 0, None))),
        peak_c_chg=float(np.max(-np.clip(c_rate, None, 0))),
        rms_c=float(np.sqrt(np.mean(c_rate**2))),
        heat_avg_kW=float(np.mean(q_pack)) / 1e3,
        heat_peak_kW=float(np.max(q_pack)) / 1e3,
        E_loss_kWh=e_loss / 3.6e6,
        throughput_kWh=(thru_dis + thru_chg) / 3.6e6,
        eta_oneway_dis=eta_dis, eta_oneway_chg=eta_chg,
        eta_roundtrip=eta_dis * eta_chg,
        v_cell_min=float(np.min(v_t)), v_cell_max=float(np.max(v_t)),
    )


# --------------------------------------------------- V1 start-stop genset
def genset_hysteresis(t, p_bus, p_on_bus_w, band_kwh):
    """E6-style start-stop supervisor: genset OFF until the buffer has
    fallen band_kwh/2 below the 55% centre, then ON at p_on_bus_w until it
    has risen band_kwh/2 above. Returns terminal battery power
    (+discharge), stored-energy trace [J] and start count."""
    t = np.asarray(t, float)
    p_bus = np.asarray(p_bus, float)
    dt = np.diff(t, prepend=t[0] - (t[1] - t[0]))
    half = band_kwh / 2.0 * 3.6e6
    e = 0.0
    on = False
    starts = 0
    p_term = np.zeros_like(p_bus)
    e_hist = np.zeros_like(p_bus)
    for k in range(p_bus.size):
        if (not on) and e < -half:
            on = True
            starts += 1
        elif on and e > half:
            on = False
        pg = p_on_bus_w if on else 0.0
        net = pg - p_bus[k]                     # + = charge into pack
        p_term[k] = -net
        # stored-energy bookkeeping with the WS1 scalar (bookkeeping only;
        # real losses come from the WS3 resistance model downstream)
        de = net * ETA_BATT if net >= 0 else net / ETA_BATT
        e += de * dt[k]
        e_hist[k] = e
    return p_term, e_hist, starts
