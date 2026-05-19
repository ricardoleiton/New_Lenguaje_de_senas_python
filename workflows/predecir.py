"""Workflow de predicción en tiempo real. Requiere permiso 'predecir'."""

import os
import pickle
import time
import logging
import warnings
from collections import deque

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ.setdefault("ABSL_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")
logging.getLogger("tensorflow").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="tensorflow")

import cv2
import numpy as np
from tensorflow.keras.models import load_model

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
    initialize_holistic,
    leer_gif,
    setup_camera,
)

try:
    from absl import logging as absl_logging

    absl_logging.set_verbosity(absl_logging.ERROR)
except ImportError:
    pass

GIF_WINDOW_NAME = overlay.WINDOW_GIF
MAIN_WINDOW_NAME = overlay.WINDOW_PREDICTION
REFERENCE_WIDTH = 420
REFERENCE_HEIGHT = 520


def _reference_canvas(title: str = "Referencia", subtitle: str = "") -> np.ndarray:
    """Crea el panel derecho de referencia."""
    frame = np.full(
        (REFERENCE_HEIGHT, REFERENCE_WIDTH, 3),
        overlay.BG,
        dtype=np.uint8,
    )
    overlay.draw_top_bar(frame, title, subtitle)
    return frame


def _fit_into_canvas(canvas: np.ndarray, image: np.ndarray) -> None:
    """Inserta una imagen centrada dentro del panel de referencia."""
    max_w = REFERENCE_WIDTH - 64
    max_h = REFERENCE_HEIGHT - 170
    h, w = image.shape[:2]
    scale = min(max_w / w, max_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = cv2.resize(image, (new_w, new_h))
    x = (REFERENCE_WIDTH - new_w) // 2
    y = 112 + (max_h - new_h) // 2
    canvas[y : y + new_h, x : x + new_w] = resized


def _draw_reference_frame(
    frames_gif: list,
    gif_idx: int,
    gesto: str,
    confianza: float,
) -> np.ndarray:
    """Devuelve el frame de la ventana derecha: vacío o con referencia."""
    if not gesto:
        return _reference_canvas("Referencia", "")

    canvas = _reference_canvas(
        "Referencia guardada",
        f"{gesto.upper()} - {confianza:.0%}",
    )
    if frames_gif:
        _fit_into_canvas(canvas, frames_gif[gif_idx % len(frames_gif)])
    overlay.draw_bottom_bar(canvas, f"Detectado: {gesto.upper()} | {confianza:.0%}")
    return canvas


def main() -> None:
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return
    requerir("predecir", user.rol)

    if not os.path.exists(config.MODEL_PATH):
        ui.error(f"No se encontró el modelo en {config.MODEL_PATH}")
        ui.info("Ejecutá primero el entrenamiento con un usuario profesor.")
        return
    if not os.path.exists(config.LABELS_PATH):
        ui.error(f"No se encontraron etiquetas en {config.LABELS_PATH}")
        return

    ui.title("Predicción en tiempo real", "MediaPipe Holistic + modelo LSTM")
    ui.step("Cargando modelo y etiquetas")
    model = load_model(config.MODEL_PATH)
    model_frames = model.input_shape[1]
    if model_frames != config.FRAMES_PER_SEQUENCE:
        ui.error(
            "El modelo actual fue entrenado con "
            f"{model_frames} frames, pero la configuración usa "
            f"{config.FRAMES_PER_SEQUENCE}."
        )
        ui.info("Reentrená el modelo antes de usar predicción en tiempo real.")
        return
    with open(config.LABELS_PATH, "rb") as f:
        etiquetas = pickle.load(f)
    ui.metric_rows(
        [
            ("Modelo", config.MODEL_PATH),
            ("Clases", ", ".join(etiquetas)),
            ("Confianza mín.", f"{config.PREDICTION_CONFIDENCE_THRESHOLD:.0%}"),
        ]
    )

    log_event(user.username, "predict_start")

    ui.step("Inicializando cámara")
    cap = setup_camera()
    with suppress_native_stderr():
        holistic = initialize_holistic()

    buffer = deque(maxlen=config.FRAMES_PER_SEQUENCE)
    pred_buffer = deque(maxlen=config.PREDICTION_HISTORY)

    gesto_actual = ""
    confianza_actual = 0.0
    ultimo_tiempo = 0.0
    frames_gif = []
    gif_idx = 0

    cv2.namedWindow(MAIN_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.namedWindow(GIF_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(GIF_WINDOW_NAME, REFERENCE_WIDTH, REFERENCE_HEIGHT)
    cv2.moveWindow(MAIN_WINDOW_NAME, 40, 80)
    cv2.moveWindow(GIF_WINDOW_NAME, 760, 80)
    cv2.imshow(GIF_WINDOW_NAME, _reference_canvas())

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            with suppress_native_stderr():
                results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw_holistic_landmarks(frame, results)
            landmarks = extract_holistic_landmarks(results)
            landmarks = normalize_landmarks(landmarks)

            if validate_landmarks(landmarks):
                buffer.append(landmarks)

            if len(buffer) == config.FRAMES_PER_SEQUENCE:
                secuencia = np.array(buffer).reshape(
                    1, config.FRAMES_PER_SEQUENCE, config.FEATURES
                )
                pred = model.predict(secuencia, verbose=0)[0]
                idx = int(np.argmax(pred))
                confianza = float(pred[idx])
                pred_buffer.append(idx)

                if (
                    confianza > config.PREDICTION_CONFIDENCE_THRESHOLD
                    and pred_buffer.count(idx) >= config.PREDICTION_CONSENSUS
                ):
                    nuevo_gesto = etiquetas[idx]
                    if nuevo_gesto != gesto_actual:
                        log_event(
                            user.username,
                            "predict_gesture",
                            f"gesto={nuevo_gesto} conf={confianza:.2f}",
                        )
                        pred_buffer.clear()
                    gesto_actual = nuevo_gesto
                    confianza_actual = confianza
                    ultimo_tiempo = time.time()
                    ui.success(f"Gesto detectado: {gesto_actual.upper()} ({confianza:.0%})")
                    ruta_gif = os.path.join(config.GIFS_DIR, f"{gesto_actual}.gif")
                    frames_gif = leer_gif(ruta_gif)
                    gif_idx = 0
                buffer.clear()

            overlay.draw_top_bar(
                frame,
                "Predicción en tiempo real",
                "Mantené el gesto estable dentro del encuadre",
            )
            overlay.draw_progress(
                frame,
                "Frames válidos",
                len(buffer),
                config.FRAMES_PER_SEQUENCE,
            )
            if gesto_actual and (
                time.time() - ultimo_tiempo < config.GESTURE_DISPLAY_SECONDS
            ):
                overlay.draw_prediction(
                    frame,
                    gesto_actual,
                    confianza_actual,
                )
            else:
                if gesto_actual:
                    gesto_actual = ""
                    frames_gif = []

            overlay.draw_bottom_bar(frame, "Q: salir")
            cv2.imshow(MAIN_WINDOW_NAME, frame)

            reference = _draw_reference_frame(
                frames_gif,
                gif_idx,
                gesto_actual,
                confianza_actual,
            )
            cv2.imshow(GIF_WINDOW_NAME, reference)
            if frames_gif:
                gif_idx += 1

            if cv2.waitKey(30) & 0xFF == ord("q"):
                break

        log_event(user.username, "predict_finish")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        with suppress_native_stderr():
            holistic.close()
            time.sleep(0.2)
