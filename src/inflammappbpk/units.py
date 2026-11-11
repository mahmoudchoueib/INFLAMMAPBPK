"""Shared units; require explicit molecular mass for mass-to-molar conversion."""

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity
