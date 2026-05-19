"""Submenú de gestión de usuarios. Requiere permiso 'gestionar_usuarios'.

Operaciones disponibles:
- Listar usuarios
- Crear usuario (con rol del catálogo)
- Eliminar usuario
- Cambiar rol de usuario
- Resetear password de usuario
"""

import getpass

from auth import (
    InvalidUsername,
    UserAlreadyExists,
    UserError,
    UserNotFound,
    WeakPassword,
    cambiar_password,
    cambiar_rol,
    crear_usuario,
    eliminar_usuario,
    get_rbac,
    listar_usuarios,
    log_event,
    requerir,
    usuario_actual,
)

MENU = """
==================================
 GESTIÓN DE USUARIOS
==================================
1. Listar usuarios
2. Crear usuario
3. Eliminar usuario
4. Cambiar rol de usuario
5. Resetear contraseña de usuario
6. Volver al menú principal
"""


def _listar() -> None:
    usuarios = listar_usuarios()
    if not usuarios:
        print("(no hay usuarios registrados)")
        return
    print(f"\n{'Username':<20} {'Rol':<15} {'Activo':<8} {'Último login':<25}")
    print("-" * 70)
    for u in usuarios:
        print(
            f"{u['username']:<20} "
            f"{u['rol']:<15} "
            f"{str(u.get('activo', True)):<8} "
            f"{str(u.get('ultimo_login', '-')):<25}"
        )


def _crear(actor: str) -> None:
    rbac = get_rbac()
    print(f"\nRoles disponibles: {', '.join(rbac.listar_roles())}")
    username = input("Nuevo username: ").strip()
    rol = input("Rol: ").strip().lower()
    if not rbac.existe_rol(rol):
        print(f"❌ Rol '{rol}' no existe")
        return
    pw1 = getpass.getpass("Contraseña: ")
    pw2 = getpass.getpass("Repetir contraseña: ")
    if pw1 != pw2:
        print("❌ Las contraseñas no coinciden")
        return
    try:
        crear_usuario(username, pw1, rol)
        log_event(actor, "user_create", f"target={username} rol={rol}")
        print(f"✅ Usuario '{username}' creado con rol '{rol}'")
    except (WeakPassword, InvalidUsername, UserAlreadyExists, UserError) as e:
        print(f"❌ {e}")


def _eliminar(actor: str) -> None:
    username = input("Username a eliminar: ").strip()
    if not username:
        print("Cancelado")
        return
    if username.lower() == actor:
        print("❌ No te podés autoeliminar")
        return
    confirm = (
        input(f"⚠ ¿Eliminar definitivamente a '{username}'? [s/N]: ").strip().lower()
    )
    if confirm != "s":
        print("Cancelado")
        return
    try:
        eliminar_usuario(username)
        log_event(actor, "user_delete", f"target={username}")
        print(f"✅ Eliminado '{username}'")
    except (UserNotFound, InvalidUsername) as e:
        print(f"❌ {e}")


def _cambiar_rol(actor: str) -> None:
    rbac = get_rbac()
    username = input("Username: ").strip()
    print(f"Roles disponibles: {', '.join(rbac.listar_roles())}")
    rol = input("Nuevo rol: ").strip().lower()
    try:
        cambiar_rol(username, rol)
        log_event(actor, "user_change_role", f"target={username} new_rol={rol}")
        print(f"✅ Rol de '{username}' cambiado a '{rol}'")
    except (UserNotFound, UserError, InvalidUsername) as e:
        print(f"❌ {e}")


def _reset_password(actor: str) -> None:
    username = input("Username: ").strip()
    pw1 = getpass.getpass("Nueva contraseña: ")
    pw2 = getpass.getpass("Repetir: ")
    if pw1 != pw2:
        print("❌ Las contraseñas no coinciden")
        return
    try:
        cambiar_password(username, pw1)
        log_event(actor, "user_reset_password", f"target={username}")
        print(f"✅ Contraseña de '{username}' actualizada")
    except (UserNotFound, WeakPassword, InvalidUsername) as e:
        print(f"❌ {e}")


def main() -> None:
    user = usuario_actual()
    if user is None:
        print("❌ No hay sesión activa")
        return
    requerir("gestionar_usuarios", user.rol)

    while True:
        print(MENU)
        try:
            op = input("Opción: ").strip()
        except (KeyboardInterrupt, EOFError):
            return

        if op == "1":
            _listar()
        elif op == "2":
            _crear(user.username)
        elif op == "3":
            _eliminar(user.username)
        elif op == "4":
            _cambiar_rol(user.username)
        elif op == "5":
            _reset_password(user.username)
        elif op == "6":
            return
        else:
            print("❌ Opción inválida")

        try:
            input("\n[ENTER para continuar]")
        except (KeyboardInterrupt, EOFError):
            return
