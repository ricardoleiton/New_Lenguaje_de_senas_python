"""Módulo core: configuración central y procesamiento de landmarks."""

from .config import config, Config
from .landmarks import (
    extract_holistic_landmarks,
    normalize_landmarks,
    validate_landmarks,
)

__all__ = [
    "config",
    "Config",
    "extract_holistic_landmarks",
    "normalize_landmarks",
    "validate_landmarks",
]
