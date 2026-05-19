"""CRUD sobre el archivo de usuarios ``config/users.json``.

El archivo es un JSON con la forma::

    {
      "version": 1,
      "usuarios": [
        {
          "username": "ricardo",
          "password_hash": "$2b$12$...",
          "rol": "profesor",
          "creado": "2026-05-01T15:30:00",
          "ultimo_login": null,
          "activo": true
        }
      ]
    }
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .crypto import hash_password, verify_password
from .rbac import get_rbac

USERS_PATH = Path("config") / "users.json"
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")
MIN_PASSWORD_LENGTH = 8


# ---- Excepciones ----------------------------------------------------------

class UserError(Exception):
    """Error general del módulo users."""


class UserNotFound(UserError):
    pass


class UserAlreadyExists(UserError):
    pass


class WeakPassword(UserError):
    pass


class InvalidUsername(UserError):
    pass


# ---- Validaciones ---------------------------------------------------------

def validar_username(username: str) -> str:
    """Devuelve el username canonicalizado (lowercase) o lanza ``InvalidUsername``."""
    if not isinstance(username, str) or username.strip() == "":
        raise InvalidUsername("El username no puede estar vacío")
    cleaned = username.strip().lower()
    if not USERNAME_RE.match(cleaned):
        raise InvalidUsername(
            "Username debe tener 3-30 caracteres alfanuméricos o '_' (sin espacios ni acentos)"
        )
    return cleaned


def validar_password(password: str) -> None:
    """Lanza ``WeakPassword`` si no cumple la política."""
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise WeakPassword(
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
        )
    if not any(c.isdigit() for c in password):
        raise WeakPassword("La contraseña debe contener al menos un dígito")


# ---- Persistencia ---------------------------------------------------------

def _ensure_dir() -> None:
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)


def cargar_usuarios() -> Dict[str, Any]:
    """Devuelve el contenido completo de users.json. Estructura por defecto si no existe."""
    if not USERS_PATH.exists():
        return {"version": 1, "usuarios": []}
    with USERS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "usuarios" not in data:
        data["usuarios"] = []
    return data


def guardar_usuarios(data: Dict[str, Any]) -> None:
    _ensure_dir()
    tmp = USERS_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(USERS_PATH)


def existe_usuarios() -> bool:
    return USERS_PATH.exists() and len(cargar_usuarios().get("usuarios", [])) > 0


# ---- Búsqueda y operaciones ----------------------------------------------

def buscar_usuario(username: str) -> Optional[Dict[str, Any]]:
    cleaned = validar_username(username)
    for u in cargar_usuarios().get("usuarios", []):
        if u.get("username") == cleaned:
            return u
    return None


def crear_usuario(username: str, password: str, rol: str) -> None:
    cleaned = validar_username(username)
    validar_password(password)
    if not get_rbac().existe_rol(rol):
        raise UserError(
            f"El rol '{rol}' no existe en roles.json. Disponibles: "
            f"{', '.join(get_rbac().listar_roles())}"
        )
    data = cargar_usuarios()
    if any(u["username"] == cleaned for u in data["usuarios"]):
        raise UserAlreadyExists(f"El usuario '{cleaned}' ya existe")
    data["usuarios"].append(
        {
            "username": cleaned,
            "password_hash": hash_password(password),
            "rol": rol,
            "creado": datetime.now().isoformat(timespec="seconds"),
            "ultimo_login": None,
            "activo": True,
        }
    )
    guardar_usuarios(data)


def eliminar_usuario(username: str) -> None:
    cleaned = validar_username(username)
    data = cargar_usuarios()
    nuevos = [u for u in data["usuarios"] if u["username"] != cleaned]
    if len(nuevos) == len(data["usuarios"]):
        raise UserNotFound(f"Usuario '{cleaned}' no encontrado")
    data["usuarios"] = nuevos
    guardar_usuarios(data)


def cambiar_password(username: str, password_nueva: str) -> None:
    cleaned = validar_username(username)
    validar_password(password_nueva)
    data = cargar_usuarios()
    for u in data["usuarios"]:
        if u["username"] == cleaned:
            u["password_hash"] = hash_password(password_nueva)
            guardar_usuarios(data)
            return
    raise UserNotFound(f"Usuario '{cleaned}' no encontrado")


def cambiar_rol(username: str, rol_nuevo: str) -> None:
    cleaned = validar_username(username)
    if not get_rbac().existe_rol(rol_nuevo):
        raise UserError(
            f"El rol '{rol_nuevo}' no existe en roles.json. Disponibles: "
            f"{', '.join(get_rbac().listar_roles())}"
        )
    data = cargar_usuarios()
    for u in data["usuarios"]:
        if u["username"] == cleaned:
            u["rol"] = rol_nuevo
            guardar_usuarios(data)
            return
    raise UserNotFound(f"Usuario '{cleaned}' no encontrado")


def listar_usuarios() -> List[Dict[str, Any]]:
    return cargar_usuarios().get("usuarios", [])


# ---- Autenticación --------------------------------------------------------

def autenticar(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verifica credenciales. Si OK, actualiza ``ultimo_login`` y devuelve el dict.

    Devuelve ``None`` ante cualquier error (usuario inválido, no existe,
    inactivo o password incorrecta). El llamador no debe distinguir
    el motivo para no filtrar info.
    """
    try:
        cleaned = validar_username(username)
    except InvalidUsername:
        return None

    data = cargar_usuarios()
    for u in data.get("usuarios", []):
        if u.get("username") != cleaned:
            continue
        if not u.get("activo", True):
            return None
        if not verify_password(password, u.get("password_hash", "")):
            return None
        u["ultimo_login"] = datetime.now().isoformat(timespec="seconds")
        guardar_usuarios(data)
        return u
    return None
