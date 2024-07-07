"""Utility methods for the Tuya integration."""

from __future__ import annotations
from .const import (
    DPType,
)

def remap_value(
    value: float,
    from_min: float = 0,
    from_max: float = 255,
    to_min: float = 0,
    to_max: float = 255,
    reverse: bool = False,
) -> float:
    """Remap a value from its current range, to a new range."""
    if reverse:
        value = from_max - value + from_min
    return ((value - from_min) / (from_max - from_min)) * (to_max - to_min) + to_min

def determine_property_type(type, value = None) -> DPType:
        if type == "value":
            return DPType(DPType.INTEGER)
        if type == "bitmap":
            return DPType(DPType.RAW)
        if type == "enum":
            return DPType(DPType.ENUM)
        if type == "bool":
            return DPType(DPType.BOOLEAN)
        if type == "json":
            return DPType(DPType.JSON)
        if type == "string":
            return DPType(DPType.STRING)