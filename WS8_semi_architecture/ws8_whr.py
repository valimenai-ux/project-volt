"""
Project Volt - WS8
Waste-heat-recovery modifier (assignment Task 4).

    "TASK 4 - Waste-heat-recovery modifier on S1-S3's steady engine
     operating point (electric turbocompound and/or small ORC). Adoption
     gate, pre-committed: >=2.5% net fleet-mission fuel AFTER its mass
     charge, else dropped without ceremony."

The gate is PRE-COMMITTED, so this module exists to test it, not to
argue for it. Two systems are modelled; each is applied to the engine
operating points the candidate actually runs, not to a rated point, and
each is then charged its mass against payload before the gate is read.

WHY LOAD-DEPENDENCE MATTERS AND IS MODELLED. Both recovery systems live
on exhaust enthalpy, which collapses at part load: an ORC that returns
5% at rated returns almost nothing at 25% load, because exhaust mass
flow and temperature have both fallen. Quoting a rated-point gain
against a fleet-average duty is the single most common way WHR is
oversold, so the recovery here is a function of engine load fraction and
is integrated over the duty cycle.

WHAT THIS MODEL DOES NOT CARRY, stated so it is not mistaken for a full
WHR study: no transient thermal inertia (an ORC takes minutes to come up
and does not recover during a descent), no back-pressure penalty
iteration on the engine map beyond the declared net figure, and no
cooling-package growth beyond the declared mass. All three push the same
way - they make WHR look BETTER here than it would in a full study - so
a candidate that fails this gate would fail a stricter one.
"""
import numpy as np


class WHRSystem:
    """Load-dependent net recovery, expressed as a fractional reduction
    in fuel for the same brake work.

    net_gain(phi) = gain_rated * clip((phi - phi_on)/(1 - phi_on), 0, 1)**shape

    phi        engine load fraction (brake torque / full-load torque)
    phi_on     load below which recovery is negligible
    gain_rated fractional fuel saving at full load, NET of back-pressure
    shape      >1 makes the roll-off steeper (exhaust enthalpy falls
               faster than load)
    """

    def __init__(self, name, gain_rated, phi_on, shape, mass_kg,
                 basis, applies_to=("S0", "S1", "S2", "S3")):
        self.name = name
        self.gain_rated = float(gain_rated)
        self.phi_on = float(phi_on)
        self.shape = float(shape)
        self.mass_kg = float(mass_kg)
        self.basis = basis
        self.applies_to = tuple(applies_to)

    def gain(self, phi):
        x = np.clip((np.asarray(phi, float) - self.phi_on)
                    / (1.0 - self.phi_on), 0.0, 1.0)
        return self.gain_rated * x ** self.shape

    def spec(self):
        return dict(name=self.name, gain_rated=self.gain_rated,
                    phi_on=self.phi_on, shape=self.shape,
                    mass_kg=self.mass_kg, basis=self.basis,
                    gain_at_phi=dict(
                        (f"{p:.2f}", float(self.gain(p)))
                        for p in (0.25, 0.40, 0.55, 0.70, 0.85, 1.00)))


# [WS8-PROV] class-typical published figures for on-highway heavy-duty
# demonstrators and low-volume production. Both are NET of back-pressure
# and of the recovery machine's own losses; both masses include the
# recovery machine, its power electronics where electric, and the extra
# cooling capacity the system needs.
#
# ANCHOR, from the Task 0 academic sweep (search-summary level,
# provisional per E13): the DOE SuperTruck programme reports Detroit's
# demonstrator at 48.1% brake thermal efficiency = 46.8% engine + 1.3%
# waste heat recovery. Taken relatively, 1.3 / 48.1 = 2.7% of fuel
# recovered at a DEMONSTRATOR's best point. The rated-load gains declared
# below (3.0% for turbocompound, 4.5% for ORC) therefore sit AT OR ABOVE
# what a funded demonstrator achieved at its best point - deliberately,
# because the gate is pre-committed and a generous input makes a DROPPED
# verdict harder to argue with than a stingy one would.
# https://www.energy.gov/eere/vehicles/articles/supertruck-program-engine-project-review
ETC = WHRSystem(
    "electric turbocompound",
    gain_rated=0.030, phi_on=0.30, shape=1.3, mass_kg=85.0,
    basis=("turbine-generator in the exhaust stream feeding the DC bus; "
           "3.0% net at rated load, negligible below 30% load"))

ORC = WHRSystem(
    "small organic Rankine cycle",
    gain_rated=0.045, phi_on=0.35, shape=1.6, mass_kg=215.0,
    basis=("EGR + exhaust boiler, expander, condenser and its cooling "
           "package; 4.5% net at rated load, steeper roll-off than ETC "
           "because the boiler needs both flow and temperature"))

SYSTEMS = {"ETC": ETC, "ORC": ORC, "ETC+ORC": None}


def combined(a, b, name="ETC+ORC"):
    """Two systems in series on the same exhaust stream do NOT add: the
    second sees the enthalpy the first has already taken. Combined gain
    is treated as 1-(1-g1)(1-g2) with an additional 15% interaction
    penalty on the smaller of the two, and the masses add. [WS8-PROV]"""
    class _Combined(WHRSystem):
        def __init__(self):
            super().__init__(name, 0.0, min(a.phi_on, b.phi_on), 1.0,
                             a.mass_kg + b.mass_kg,
                             basis=(f"{a.name} + {b.name} in series on one "
                                    "exhaust stream; the second recovers "
                                    "only what the first left, with a 15% "
                                    "interaction penalty on the smaller "
                                    "gain"))

        def gain(self, phi):
            g1 = a.gain(phi)
            g2 = b.gain(phi)
            small = np.minimum(g1, g2) * 0.15
            return 1.0 - (1.0 - g1) * (1.0 - g2) - small
    return _Combined()


SYSTEMS["ETC+ORC"] = combined(ETC, ORC)


GATE_PCT = 2.5
"""Pre-committed adoption gate: >=2.5% net fleet-mission fuel per payload
tonne-km improvement AFTER the mass charge. Below it, dropped without
ceremony (assignment, Task 4)."""
