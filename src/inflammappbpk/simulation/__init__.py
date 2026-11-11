"""Event-aware stiff integration and whole-body model."""

from .engine import Dose, Trajectory, simulate
from .whole_body import WholeBody

__all__ = ["Dose", "Trajectory", "simulate", "WholeBody"]
