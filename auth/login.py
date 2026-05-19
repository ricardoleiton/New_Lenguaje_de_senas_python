"""Wizard de bootstrap inicial y loop de login con anti-bruteforce."""

import getpass
import time
from typing import Optional

from .audit import log_event
from .session import Usuario, set_usuario
from .users import (
    autenticar,
    crear_usuario,
    existe_usuarios,
    validar_password,
    validar_username,
    InvalidUsername,
    WeakPassword,
)

# Delays incrementales tras logins fallidos (segundos)
FAILED_DELAYS = (1, 2, 4, 8, 16)


def bootstrap_inicial() -> Optional[Usuario]:
    """Crea el primer usuario con rol 'profesor' cuando no existen usuarios."""
    print("\n" + "=" * 60)
    print("  PRIMERA EJECUCIÓN — CREAR PROFESOR INICIAL")
    print("=" * 60)
    print("\nNo se encontraron usuarios registrados.")
    print("Vas a crear el primer usuario con rol 'profesor'.\n")

    while True:
        try:
            username = input("Nuevo username (3-30 caracteres, a-z 0-9 _): ").strip()
            validar_username(username)
            break
        except InvalidUsername as e:
            print(f"❌ {e}")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠ Bootstrap cancelado")
            return None

    while True:
        try:
            pw1 = getpass.getpass("Password (mín. 8 caracteres, al menos 1 dígito): ")
            validar_password(pw1)
            pw2 = getpass.getpass("Repetir password: ")
            if pw1 != pw2:
                print("❌ Las contraseñas no coinciden")
                continue
            break
        except WeakPassword as e:
            print(f"❌ {e}")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠ Bootstrap cancelado")
            return None

    crear_usuario(username, pw1, "profesor")
    log_event(username, "bootstrap_initial_user", "rol=profesor")
    print(f"\n✅ Usuario '{username}' creado con rol 'profesor'")

    usuario = Usuario(username=username, rol="profesor")
    set_usuario(usuario)
    return usuario


def login_loop() -> Optional[Usuario]:
    """Pide credenciales y devuelve ``Usuario`` si se logueó, ``None`` si canceló."""
    if not existe_usuarios():
        return bootstrap_inicial()

    print("\n" + "=" * 60)
    print("  LOGIN")
    print("=" * 60)

    intentos_fallidos = 0
    while True:
        try:
            username = input("\nUsername (o 'q' para salir): ").strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if username.lower() == "q":
            return None

        try:
            password = getpass.getpass("Password: ")
        except (KeyboardInterrupt, EOFError):
            return None

        user_data = autenticar(username, password)
        if user_data is not None:
            log_event(user_data["username"], "login")
            usuario = Usuario(username=user_data["username"], rol=user_data["rol"])
            set_usuario(usuario)
            print(f"\n✅ Bienvenido, {usuario.username} (rol: {usuario.rol})")
            return usuario

        log_event(username if username else "(empty)", "login", exitoso=False)
        print("❌ Credenciales inválidas")
        delay = FAILED_DELAYS[min(intentos_fallidos, len(FAILED_DELAYS) - 1)]
        intentos_fallidos += 1
        print(f"   Esperá {delay}s antes del próximo intento...")
        time.sleep(delay)
