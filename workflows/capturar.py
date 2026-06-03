"""Workflow de captura de secuencias. Requiere permiso 'capturar'."""

import os
import string
from typing import Optional, Tuple

from auth import requerir, usuario_actual
from core import ui
from core.config import config
from services.capture_service import (
    clases_capturadas,
    ejecutar_captura as ejecutar_captura_servicio,
    imprimir_clases_capturadas,
    imprimir_protocolo_captura,
)

__all__ = [
    "clases_capturadas",
    "ejecutar_captura",
    "imprimir_clases_capturadas",
    "imprimir_protocolo_captura",
    "main",
]


def ejecutar_captura(tipo: str, clase: str, sobrescribir: bool = False) -> bool:
    """Valida sesión/permisos y delega la captura al servicio operativo."""
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return False
    requerir("capturar", user.rol)
    return ejecutar_captura_servicio(
        tipo,
        clase,
        sobrescribir=sobrescribir,
        username=user.username,
    )


def _seleccionar_clase() -> Optional[Tuple[str, str]]:
    """Devuelve (tipo, clase) para letras, números o palabras."""
    imprimir_clases_capturadas()
    ui.section("Tipo de captura")
    print("  1. Letra (A-Z)")
    print("  2. Número (0-9)")
    print("  3. Palabra completa")
    print("  0. Cancelar")

    while True:
        opcion = input(ui.prompt("Elegí una opción:")).strip()
        if opcion == "0":
            return None
        if opcion == "1":
            valor = input(ui.prompt("Letra a capturar (A-Z):")).strip().lower()
            if len(valor) == 1 and valor in string.ascii_lowercase:
                return "letra", valor
            ui.error("Ingresá una sola letra entre A y Z.")
            continue
        if opcion == "2":
            valor = input(ui.prompt("Número a capturar (0-9):")).strip()
            if len(valor) == 1 and valor.isdigit():
                return "número", valor
            ui.error("Ingresá un solo número entre 0 y 9.")
            continue
        if opcion == "3":
            valor = input(ui.prompt("Palabra a capturar (sin espacios):")).strip().lower()
            valor = valor.replace(" ", "_")
            if len(valor) >= 2 and valor.replace("_", "").isalpha():
                return "palabra", valor
            ui.error("Ingresá una palabra completa, sin números ni símbolos.")
            continue
        ui.error(
            "Opción inválida. Usá 1 para letra, 2 para número, "
            "3 para palabra o 0 para cancelar."
        )


def main() -> None:
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return
    requerir("capturar", user.rol)

    ui.title(
        "Captura de letras, números y palabras",
        "MediaPipe Holistic + dataset local",
    )
    imprimir_protocolo_captura()
    seleccion = _seleccionar_clase()
    if seleccion is None:
        ui.warning("Captura cancelada.")
        return
    tipo, clase = seleccion

    carpeta_clase = os.path.join(config.SEQUENCES_DIR, clase)
    os.makedirs(carpeta_clase, exist_ok=True)
    existentes = [f for f in os.listdir(carpeta_clase) if f.endswith(".npy")]
    sobrescribir = False
    if existentes:
        resp = (
            input(
                ui.prompt(
                    f"Ya existen {len(existentes)} secuencias para '{clase}'. ¿Sobrescribir? [s/N]:"
                )
            )
            .strip()
            .lower()
        )
        if resp != "s":
            ui.warning("Captura cancelada. Los datos existentes se preservaron.")
            return
        sobrescribir = True

    ejecutar_captura_servicio(
        tipo,
        clase,
        sobrescribir=sobrescribir,
        username=user.username,
    )
