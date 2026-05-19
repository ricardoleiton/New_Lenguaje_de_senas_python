"""Role-Based Access Control.

Las definiciones de roles y permisos viven en ``config/roles.json``.
Para sumar un rol nuevo, se edita ese JSON sin tocar código Python.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROLES_PATH = Path("config") / "roles.json"


class RBACError(Exception):
    """Error en la carga o uso del RBAC."""


class PermissionDenied(RBACError):
    """El rol del usuario no tiene el permiso requerido."""


@dataclass(frozen=True)
class Role:
    nombre: str
    descripcion: str
    permisos: Tuple[str, ...]


class RBAC:
    """Carga y consulta los roles definidos en ``config/roles.json``."""

    def __init__(self, path: Path = ROLES_PATH) -> None:
        self.path = path
        self.roles: Dict[str, Role] = {}
        self.permisos_disponibles: Tuple[str, ...] = ()
        self.recargar()

    def recargar(self) -> None:
        if not self.path.exists():
            raise RBACError(f"No se encontró el archivo de roles: {self.path}")
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RBACError(f"roles.json mal formado: {e}") from e

        self.permisos_disponibles = tuple(data.get("permisos_disponibles", []))
        self.roles = {
            nombre: Role(
                nombre=nombre,
                descripcion=info.get("descripcion", ""),
                permisos=tuple(info.get("permisos", [])),
            )
            for nombre, info in data.get("roles", {}).items()
        }

    def existe_rol(self, nombre: str) -> bool:
        return nombre in self.roles

    def permisos_de_rol(self, nombre: str) -> Tuple[str, ...]:
        rol = self.roles.get(nombre)
        return rol.permisos if rol else ()

    def listar_roles(self) -> List[str]:
        return list(self.roles.keys())

    def descripcion_rol(self, nombre: str) -> Optional[str]:
        rol = self.roles.get(nombre)
        return rol.descripcion if rol else None


_rbac_instance: Optional[RBAC] = None


def get_rbac() -> RBAC:
    """Singleton del RBAC (lazy-loaded)."""
    global _rbac_instance
    if _rbac_instance is None:
        _rbac_instance = RBAC()
    return _rbac_instance


def tiene_permiso(rol: str, permiso: str) -> bool:
    return permiso in get_rbac().permisos_de_rol(rol)


def requerir(permiso: str, rol: str) -> None:
    """Lanza PermissionDenied si el rol no tiene el permiso. Defense in depth."""
    if not tiene_permiso(rol, permiso):
        raise PermissionDenied(
            f"El rol '{rol}' no tiene el permiso requerido: '{permiso}'"
        )
