"""Cámara, MediaPipe Holistic y utilidades de GIF.

Cualquier interacción directa con OpenCV/MediaPipe a nivel "device" o
"render" vive acá. Los workflows usan estas funciones, no llaman a
``cv2.VideoCapture`` o ``mp.solutions.holistic`` directamente.
"""

import os
import logging
import warnings
from typing import List, Optional, Tuple

os.environ["ABSL_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
logging.getLogger("tensorflow").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="tensorflow")

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

from core.config import config

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

_selected_camera_index: int = config.CAMERA_INDEX


def get_selected_camera_index() -> int:
    """Devuelve el índice de cámara seleccionado para la sesión actual."""
    return _selected_camera_index


def set_selected_camera_index(index: int) -> None:
    """Configura el índice de cámara usado por captura y predicción."""
    global _selected_camera_index
    if index < 0:
        raise ValueError("El índice de cámara no puede ser negativo")
    _selected_camera_index = index


def discover_cameras(max_index: int = 5) -> List[int]:
    """Busca cámaras disponibles probando índices de OpenCV."""
    available: List[int] = []
    for index in range(max_index + 1):
        cap = cv2.VideoCapture(index)
        try:
            if cap.isOpened():
                ok, _ = cap.read()
                if ok:
                    available.append(index)
        finally:
            cap.release()
    return available


def initialize_holistic():
    """Inicializa MediaPipe Holistic con la configuración del proyecto."""
    return mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=config.DETECTION_CONFIDENCE,
        min_tracking_confidence=config.TRACKING_CONFIDENCE,
    )


def setup_camera(
    index: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> cv2.VideoCapture:
    """Abre la cámara web con la resolución configurada."""
    cap = cv2.VideoCapture(get_selected_camera_index() if index is None else index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width or config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height or config.CAMERA_HEIGHT)
    return cap


def draw_holistic_landmarks(frame, results) -> None:
    """Dibuja face mesh + manos + pose sobre el frame BGR (in-place)."""
    if results.face_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION
        )
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.left_hand_landmarks, mp_hands.HAND_CONNECTIONS
        )
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.right_hand_landmarks, mp_hands.HAND_CONNECTIONS
        )
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS
        )


def generar_gif(
    frames: List[np.ndarray],
    ruta_salida: str,
    size: Tuple[int, int] = (300, 300),
    duration_ms: int = 100,
) -> None:
    """Genera un GIF animado a partir de frames BGR de OpenCV."""
    if not frames:
        return
    imagenes = [
        Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).resize(size)
        for f in frames
    ]
    imagenes[0].save(
        ruta_salida,
        save_all=True,
        append_images=imagenes[1:],
        duration=duration_ms,
        loop=0,
    )


def leer_gif(
    ruta_gif: str,
    size: Tuple[int, int] = (300, 300),
) -> List[np.ndarray]:
    """Carga un GIF y devuelve sus frames como ndarray BGR. Lista vacía si no existe."""
    if not os.path.exists(ruta_gif):
        return []
    gif = Image.open(ruta_gif)
    frames: List[np.ndarray] = []
    try:
        while True:
            frame = gif.convert("RGB")
            arr = np.array(frame)
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            arr = cv2.resize(arr, size)
            frames.append(arr)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames
