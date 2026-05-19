"""Módulo auth: autenticación, autorización (RBAC), sesión y auditoría."""

from core.console import configure_unicode_output

configure_unicode_output()

from .session import Usuario, usuario_actual, set_usuario, cerrar_sesion
from .rbac import (
    get_rbac,
    tiene_permiso,
    requerir,
    PermissionDenied,
    RBACError,
)
from .login import login_loop, bootstrap_inicial
from .users import (
    crear_usuario,
    eliminar_usuario,
    cambiar_password,
    cambiar_rol,
    listar_usuarios,
    autenticar,
    existe_usuarios,
    UserError,
    UserNotFound,
    UserAlreadyExists,
    WeakPassword,
    InvalidUsername,
)
from .audit import log_event

__all__ = [
    "Usuario",
    "usuario_actual",
    "set_usuario",
    "cerrar_sesion",
    "get_rbac",
    "tiene_permiso",
    "requerir",
    "PermissionDenied",
    "RBACError",
    "login_loop",
    "bootstrap_inicial",
    "crear_usuario",
    "eliminar_usuario",
    "cambiar_password",
    "cambiar_rol",
    "listar_usuarios",
    "autenticar",
    "existe_usuarios",
    "UserError",
    "UserNotFound",
    "UserAlreadyExists",
    "WeakPassword",
    "InvalidUsername",
    "log_event",
]
