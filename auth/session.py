"""Sesión del usuario logueado en memoria.

Stateless por proceso: no persiste entre arranques de ``main.py``.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Usuario:
    """Representación inmutable del usuario actualmente logueado."""

    username: str
    rol: str


_usuario_actual: Optional[Usuario] = None


def set_usuario(u: Usuario) -> None:
    global _usuario_actual
    _usuario_actual = u


def usuario_actual() -> Optional[Usuario]:
    return _usuario_actual


def cerrar_sesion() -> None:
    global _usuario_actual
    _usuario_actual = None
