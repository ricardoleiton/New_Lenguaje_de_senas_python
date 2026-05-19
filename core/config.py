"""Configuración central del proyecto.

Toda constante o ruta usada por más de un módulo debe vivir acá.
La instancia ``config`` es inmutable (frozen dataclass).
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # ---- Carpetas del proyecto ----
    SEQUENCES_DIR: str = "data/secuencias"
    MODELS_DIR: str = "models"
    GIFS_DIR: str = "gifs"
    LOGS_DIR: str = "logs"
    CONFIG_DIR: str = "config"

    # ---- Captura ----
    FRAMES_PER_SEQUENCE: int = 10
    SEQUENCES_PER_CLASS: int = 10
    # 2 manos (21*3*2 = 126) + 2 hombros (2*3 = 6) + 5 puntos faciales (5*3 = 15)
    FEATURES: int = 147
    CAPTURE_TIMEOUT_SECONDS: float = 15.0
    CAPTURE_COUNTDOWN_SECONDS: int = 5

    # ---- Cámara ----
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720

    # ---- MediaPipe Holistic ----
    DETECTION_CONFIDENCE: float = 0.7
    TRACKING_CONFIDENCE: float = 0.5
    MODEL_COMPLEXITY: int = 1

    # ---- Modelo entrenado ----
    MODEL_PATH: str = os.path.join("models", "modelo_lstm.h5")
    LABELS_PATH: str = os.path.join("models", "etiquetas.pkl")
    HISTORY_PATH: str = os.path.join("models", "history.json")

    # ---- Entrenamiento ----
    TRAIN_EPOCHS: int = 100
    TRAIN_BATCH_SIZE: int = 16
    TRAIN_RANDOM_SEED: int = 42
    TRAIN_TEST_SIZE: float = 0.15
    TRAIN_VAL_SIZE: float = 0.1765  # de lo que queda tras separar test → ~15% del total

    # ---- Predicción ----
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.6
    PREDICTION_HISTORY: int = 3
    PREDICTION_CONSENSUS: int = 2  # de PREDICTION_HISTORY recientes
    GESTURE_DISPLAY_SECONDS: float = 2.5


# Singleton inmutable accesible como ``from core.config import config``
config = Config()
