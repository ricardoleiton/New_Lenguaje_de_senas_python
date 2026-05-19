"""Extracción, normalización y validación de landmarks de MediaPipe Holistic.

Contrato del vector de features (147 floats por frame):
- Mano izquierda  : 21 puntos × (x, y, z) = 63
- Mano derecha    : 21 puntos × (x, y, z) = 63
- Hombros (pose)  : 2 puntos (idx 11, 12) × (x, y, z) = 6
- Cara            : 5 puntos (idx 1, 33, 263, 61, 291) × (x, y, z) = 15
Total: 63 + 63 + 6 + 15 = 147

Si una región no es detectada, se rellenan ceros del tamaño correspondiente
para preservar el contrato.
"""

from typing import Any, Optional

import numpy as np

from .config import config

# Índices de pose y rostro elegidos como referencia mínima del cuerpo/cara.
POSE_SHOULDER_IDX = (11, 12)
FACE_KEY_IDX = (1, 33, 263, 61, 291)


def extract_holistic_landmarks(results: Any) -> np.ndarray:
    """Devuelve un vector ``np.ndarray`` de longitud ``Config.FEATURES``."""
    data: list[float] = []

    for hand in (results.left_hand_landmarks, results.right_hand_landmarks):
        if hand:
            for lm in hand.landmark:
                data.extend([lm.x, lm.y, lm.z])
        else:
            data.extend([0.0] * 63)

    if results.pose_landmarks:
        for idx in POSE_SHOULDER_IDX:
            lm = results.pose_landmarks.landmark[idx]
            data.extend([lm.x, lm.y, lm.z])
    else:
        data.extend([0.0] * 6)

    if results.face_landmarks:
        for idx in FACE_KEY_IDX:
            lm = results.face_landmarks.landmark[idx]
            data.extend([lm.x, lm.y, lm.z])
    else:
        data.extend([0.0] * 15)

    return np.array(data, dtype=np.float64)


def normalize_landmarks(landmarks: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """Centra y escala los landmarks para invariancia a posición y tamaño.

    Si el input no tiene la longitud esperada, se devuelve sin tocar.
    """
    if landmarks is None or len(landmarks) != config.FEATURES:
        return landmarks

    if landmarks.size % 3 != 0:
        return landmarks  # contrato roto, no normalizar

    reshaped = landmarks.reshape(-1, 3)
    center = np.mean(reshaped, axis=0)
    reshaped = reshaped - center
    scale = np.max(np.linalg.norm(reshaped, axis=1))
    if scale > 0:
        reshaped = reshaped / scale
    return reshaped.flatten()


def validate_landmarks(landmarks: Optional[np.ndarray]) -> bool:
    """True si los landmarks pueden usarse para entrenamiento/predicción."""
    if landmarks is None or len(landmarks) != config.FEATURES:
        return False
    if np.allclose(landmarks, 0):
        return False
    if np.any(np.isnan(landmarks)) or np.any(np.isinf(landmarks)):
        return False
    return True
