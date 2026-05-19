"""Punto de entrada principal: login + menú dinámico filtrado por permisos.

Ejecutar desde la raíz del proyecto:

    python main.py

Si no hay usuarios registrados, el primer arranque crea un profesor inicial
mediante un wizard interactivo.
"""

import getpass
import importlib
import sys
from typing import List, Tuple

from auth import (
    PermissionDenied,
    WeakPassword,
    cambiar_password,
    cerrar_sesion,
    get_rbac,
    log_event,
    login_loop,
    usuario_actual,
)
from core import ui
from version import __app_name__, __version__
from vision.camera import (
    discover_cameras,
    get_selected_camera_index,
    set_selected_camera_index,
)

# Mapping: (etiqueta_visible, permiso_requerido, módulo_a_importar)
WORKFLOWS: List[Tuple[str, str, str]] = [
    ("Capturar letra, número o palabra", "capturar",     "workflows.capturar"),
    ("Entrenar modelo LSTM",      "entrenar",            "workflows.entrenar"),
    ("Predicción en tiempo real", "predecir",            "workflows.predecir"),
    ("Gestionar usuarios",        "gestionar_usuarios",  "workflows.gestion_usuarios"),
]


def _opciones_para_rol(rol: str) -> List[Tuple[str, str, str]]:
    """Filtra los workflows visibles según los permisos del rol."""
    permisos = get_rbac().permisos_de_rol(rol)
    return [item for item in WORKFLOWS if item[1] in permisos]


def _imprimir_menu(usuario) -> List[Tuple[str, str, str]]:
    ui.title(__app_name__, f"v{__version__} | Sesión: {usuario.username} | Rol: {usuario.rol}")
    opciones = _opciones_para_rol(usuario.rol)
    ui.section("Menú principal")
    for i, (etiqueta, _, _) in enumerate(opciones, 1):
        print(f"  {i}. {etiqueta}")
    base = len(opciones)
    print(f"  {base + 1}. Seleccionar cámara (actual: {get_selected_camera_index()})")
    print(f"  {base + 2}. Cambiar mi contraseña")
    print(f"  {base + 3}. Cerrar sesión")
    print(f"  {base + 4}. Salir")
    return opciones


def _seleccionar_camara() -> None:
    ui.section("Seleccionar cámara")
    ui.step("Buscando cámaras disponibles")
    cameras = discover_cameras()
    if not cameras:
        ui.warning("No se detectaron cámaras. Se mantiene la cámara actual.")
        return
    for index in cameras:
        current = " (actual)" if index == get_selected_camera_index() else ""
        print(f"  {index}. Cámara {index}{current}")
    selected = input(ui.prompt("Índice de cámara:")).strip()
    if not selected.isdigit():
        ui.error("Ingresá un índice numérico.")
        return
    index = int(selected)
    if index not in cameras:
        ui.error("Ese índice no aparece entre las cámaras detectadas.")
        return
    set_selected_camera_index(index)
    ui.success(f"Cámara seleccionada: {index}")


def _cambiar_mi_password(usuario) -> None:
    while True:
        try:
            pw1 = getpass.getpass("Nueva contrasena: ")
            pw2 = getpass.getpass("Repetir: ")
        except (KeyboardInterrupt, EOFError):
            ui.warning("Cambio de contraseña cancelado.")
            return
        if pw1 != pw2:
            ui.error("Las contraseñas no coinciden.")
            continue
        try:
            cambiar_password(usuario.username, pw1)
            log_event(usuario.username, "self_password_change")
            ui.success("Contraseña actualizada.")
            return
        except WeakPassword as e:
            ui.error(str(e))


def _ejecutar_modulo(nombre_modulo: str) -> None:
    """Importa y ejecuta el ``main`` del módulo, capturando errores comunes."""
    try:
        mod = importlib.import_module(nombre_modulo)
        mod.main()
    except PermissionDenied as e:
        ui.error(str(e))
    except KeyboardInterrupt:
        ui.warning("Operación interrumpida.")
    except Exception as e:  # noqa: BLE001
        ui.error(f"Error inesperado: {type(e).__name__}: {e}")


def main_loop() -> None:
    while True:
        usuario = usuario_actual()
        if usuario is None:
            usuario = login_loop()
            if usuario is None:
                ui.info("Saliendo del sistema.")
                return

        opciones = _imprimir_menu(usuario)
        try:
            sel = input(ui.prompt("Opción:")).strip()
        except (EOFError, KeyboardInterrupt):
            ui.info("Saliendo del sistema.")
            return

        if not sel.isdigit():
            ui.error("Opción inválida.")
            input("[ENTER para continuar]")
            continue

        idx = int(sel)
        n = len(opciones)

        if 1 <= idx <= n:
            _, _, modulo = opciones[idx - 1]
            _ejecutar_modulo(modulo)
            input("\n[ENTER para volver al menu]")
        elif idx == n + 1:
            _seleccionar_camara()
            input("\n[ENTER para continuar]")
        elif idx == n + 2:
            _cambiar_mi_password(usuario)
            input("\n[ENTER para continuar]")
        elif idx == n + 3:
            log_event(usuario.username, "logout")
            cerrar_sesion()
            ui.success("Sesión cerrada.")
        elif idx == n + 4:
            log_event(usuario.username, "exit_app")
            ui.info("Hasta luego.")
            return
        else:
            ui.error("Opción inválida.")
            input("[ENTER para continuar]")


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        ui.warning("Interrumpido por el usuario.")
        sys.exit(0)
