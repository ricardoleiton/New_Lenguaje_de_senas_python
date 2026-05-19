"""Workflow de captura de secuencias. Requiere permiso 'capturar'."""

import os
import string
import time
from typing import Dict, List, Optional, Tuple

os.environ["ABSL_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
import numpy as np

from auth import log_event, requerir, usuario_actual
from core.console import suppress_native_stderr
from core.config import config
from core import ui
from core.landmarks import (
    extract_holistic_landmarks,
    normalize_landmarks,
    validate_landmarks,
)
from vision import overlay
from vision.camera import (
    draw_holistic_landmarks,
    generar_gif,
    initialize_holistic,
    setup_camera,
)


def clases_capturadas() -> Dict[str, List[Tuple[str, int]]]:
    """Lista letras, números y palabras capturados con cantidad de secuencias."""
    resultado: Dict[str, List[Tuple[str, int]]] = {
        "letras": [],
        "numeros": [],
        "palabras": [],
    }
    if not os.path.isdir(config.SEQUENCES_DIR):
        return resultado

    for nombre in sorted(os.listdir(config.SEQUENCES_DIR)):
        ruta = os.path.join(config.SEQUENCES_DIR, nombre)
        if not os.path.isdir(ruta):
            continue
        cantidad = len([f for f in os.listdir(ruta) if f.endswith(".npy")])
        if cantidad <= 0:
            continue
        if len(nombre) == 1 and nombre in string.ascii_lowercase:
            resultado["letras"].append((nombre.upper(), cantidad))
        elif len(nombre) == 1 and nombre.isdigit():
            resultado["numeros"].append((nombre, cantidad))
        elif nombre.replace("_", "").isalpha():
            resultado["palabras"].append((nombre, cantidad))
    return resultado


def imprimir_clases_capturadas() -> None:
    """Muestra un resumen de letras, números y palabras ya capturados."""
    capturadas = clases_capturadas()
    ui.section("Clases ya capturadas")
    if (
        not capturadas["letras"]
        and not capturadas["numeros"]
        and not capturadas["palabras"]
    ):
        ui.info("Todavía no hay letras, números ni palabras capturados.")
        return

    letras = ", ".join(f"{valor} ({cantidad})" for valor, cantidad in capturadas["letras"])
    numeros = ", ".join(f"{valor} ({cantidad})" for valor, cantidad in capturadas["numeros"])
    palabras = ", ".join(
        f"{valor} ({cantidad})" for valor, cantidad in capturadas["palabras"]
    )
    ui.metric_rows(
        [
            ("Letras", letras or "-"),
            ("Números", numeros or "-"),
            ("Palabras", palabras or "-"),
        ]
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


def _esperar_confirmacion(cap, holistic, tipo: str, clase: str) -> bool:
    """Bloquea hasta que el usuario presione 'C' para iniciar o 'Q' para cancelar."""
    ui.info(
        f"Objetivo seleccionado: {tipo} '{clase.upper()}'. "
        "Presioná C para comenzar o Q para cancelar."
    )
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        with suppress_native_stderr():
            results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw_holistic_landmarks(frame, results)

        overlay.draw_top_bar(
            frame,
            "Captura de secuencias",
            "Confirmá que el objetivo sea correcto antes de grabar",
        )
        overlay.draw_capture_target(frame, tipo, clase, "esperando")
        overlay.draw_bottom_bar(frame, "C: comenzar captura   |   Q: cancelar")
        cv2.imshow(overlay.WINDOW_CAPTURE, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return False
        if key == ord("c"):
            return True


def _cuenta_regresiva(cap, holistic, tipo: str, clase: str) -> bool:
    """Muestra una cuenta regresiva antes de comenzar a guardar frames."""
    inicio = time.time()
    while True:
        restante = config.CAPTURE_COUNTDOWN_SECONDS - int(time.time() - inicio)
        if restante <= 0:
            return True

        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        with suppress_native_stderr():
            results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw_holistic_landmarks(frame, results)

        overlay.draw_top_bar(
            frame,
            "Preparar captura",
            "Acomodá la postura antes de grabar la secuencia",
        )
        overlay.draw_capture_target(frame, tipo, clase, f"inicia en {restante}")
        overlay.draw_bottom_bar(frame, "Q: cancelar")
        cv2.imshow(overlay.WINDOW_CAPTURE, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            return False


def _capturar_secuencia(
    holistic, cap, tipo: str, clase: str, indice: int
) -> Tuple[Optional[np.ndarray], Optional[List[np.ndarray]]]:
    """Captura una secuencia de N frames válidos. Devuelve (None, None) si timeout/cancel."""
    secuencia: List[np.ndarray] = []
    gif_frames: List[np.ndarray] = []
    inicio = time.time()

    while len(secuencia) < config.FRAMES_PER_SEQUENCE:
        if time.time() - inicio > config.CAPTURE_TIMEOUT_SECONDS:
            ui.warning(
                f"Timeout: solo {len(secuencia)}/{config.FRAMES_PER_SEQUENCE} frames válidos."
            )
            return None, None

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        with suppress_native_stderr():
            results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Frame "limpio" (sin landmarks dibujados) para el GIF de referencia
        frame_limpio = frame.copy()
        draw_holistic_landmarks(frame, results)

        landmarks = extract_holistic_landmarks(results)
        landmarks = normalize_landmarks(landmarks)
        if validate_landmarks(landmarks):
            secuencia.append(landmarks)
            gif_frames.append(frame_limpio)

        overlay.draw_top_bar(
            frame,
            "Captura de secuencias",
            "Realizá el gesto indicado de forma estable",
        )
        overlay.draw_progress(
            frame,
            "Frames válidos",
            len(secuencia),
            config.FRAMES_PER_SEQUENCE,
        )
        overlay.draw_capture_target(
            frame,
            tipo,
            clase,
            f"{indice}/{config.SEQUENCES_PER_CLASS}",
        )
        overlay.draw_bottom_bar(frame, "Q: interrumpir captura")
        cv2.imshow(overlay.WINDOW_CAPTURE, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            return None, None

    return np.array(secuencia), gif_frames


def ejecutar_captura(tipo: str, clase: str, sobrescribir: bool = False) -> bool:
    """Ejecuta captura para una letra, número o palabra ya validada."""
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return False
    requerir("capturar", user.rol)

    carpeta_clase = os.path.join(config.SEQUENCES_DIR, clase)
    os.makedirs(carpeta_clase, exist_ok=True)
    os.makedirs(config.GIFS_DIR, exist_ok=True)

    ui.metric_rows(
        [
            ("Tipo", tipo),
            ("Clase", clase),
            ("Secuencias", config.SEQUENCES_PER_CLASS),
            ("Frames por sec.", config.FRAMES_PER_SEQUENCE),
        ]
    )

    existentes = [f for f in os.listdir(carpeta_clase) if f.endswith(".npy")]
    if existentes:
        if not sobrescribir:
            ui.warning("Captura cancelada. Los datos existentes se preservaron.")
            return False
        for f in existentes:
            os.remove(os.path.join(carpeta_clase, f))
        ui.warning(f"Se borraron {len(existentes)} secuencias previas.")

    log_event(user.username, "capture_start", f"clase={clase}")

    cap = setup_camera()
    with suppress_native_stderr():
        holistic = initialize_holistic()
    capturadas = 0

    try:
        if not _esperar_confirmacion(cap, holistic, tipo, clase):
            ui.warning("Captura cancelada por el usuario.")
            log_event(user.username, "capture_cancel", f"clase={clase}", exitoso=False)
            return False
        if not _cuenta_regresiva(cap, holistic, tipo, clase):
            ui.warning("Captura cancelada durante la cuenta regresiva.")
            return False

        for i in range(config.SEQUENCES_PER_CLASS):
            ui.step(f"Secuencia {i + 1}/{config.SEQUENCES_PER_CLASS}")
            sec, frames = _capturar_secuencia(holistic, cap, tipo, clase, i + 1)
            if sec is None:
                ui.warning("Captura interrumpida.")
                break
            ruta_npy = os.path.join(carpeta_clase, f"{clase}_{i}.npy")
            np.save(ruta_npy, sec)
            capturadas += 1
            ui.success(f"Secuencia guardada: {ruta_npy}")

            if i == 0 and frames:
                ruta_gif = os.path.join(config.GIFS_DIR, f"{clase}.gif")
                generar_gif(frames, ruta_gif)
                ui.success(f"GIF de referencia guardado: {ruta_gif}")

        log_event(
            user.username,
            "capture_finish",
            f"clase={clase} secuencias={capturadas}",
        )
        ui.section("Resultado")
        ui.success(f"Captura finalizada: {capturadas} secuencias guardadas.")
        return capturadas == config.SEQUENCES_PER_CLASS
    finally:
        cap.release()
        cv2.destroyAllWindows()
        with suppress_native_stderr():
            holistic.close()
            time.sleep(0.2)


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
    seleccion = _seleccionar_clase()
    if seleccion is None:
        ui.warning("Captura cancelada.")
        return
    tipo, clase = seleccion

    # Confirmación explícita antes del borrado destructivo (mitiga R1 del relevamiento)
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

    ejecutar_captura(tipo, clase, sobrescribir=sobrescribir)
