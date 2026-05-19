"""Carga de secuencias y etiquetas desde ``data/secuencias/``."""

import os
from typing import List, Tuple

import numpy as np

from core.config import config
from core import ui


class DatasetError(Exception):
    """No se pudo cargar el dataset (vacío, mal formado, ausente)."""


def cargar_datos() -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Recorre ``data/secuencias/<clase>/*.npy`` y devuelve ``(X, y, etiquetas)``.

    - Las clases son los nombres de las subcarpetas, ordenadas alfabéticamente.
    - Se aceptan archivos ``.npy`` con ``FEATURES`` columnas.
    - Si una secuencia tiene otra cantidad de frames, se remuestrea a
      ``FRAMES_PER_SEQUENCE`` para poder reutilizar capturas anteriores.
    """
    if not os.path.isdir(config.SEQUENCES_DIR):
        raise DatasetError(
            f"No existe el directorio de secuencias: {config.SEQUENCES_DIR}"
        )

    etiquetas: List[str] = []
    for nombre in sorted(os.listdir(config.SEQUENCES_DIR)):
        ruta = os.path.join(config.SEQUENCES_DIR, nombre)
        if os.path.isdir(ruta):
            etiquetas.append(nombre)

    if not etiquetas:
        raise DatasetError(
            f"No se encontraron clases en {config.SEQUENCES_DIR}. "
            "Capturá secuencias antes de entrenar."
        )

    X: List[np.ndarray] = []
    y: List[int] = []
    expected_shape = (config.FRAMES_PER_SEQUENCE, config.FEATURES)
    descartados = 0
    ajustados = 0

    for idx, clase in enumerate(etiquetas):
        carpeta = os.path.join(config.SEQUENCES_DIR, clase)
        for archivo in sorted(os.listdir(carpeta)):
            if not archivo.endswith(".npy"):
                continue
            ruta_npy = os.path.join(carpeta, archivo)
            secuencia = np.load(ruta_npy)
            if secuencia.shape != expected_shape:
                try:
                    secuencia = ajustar_frames(secuencia)
                    ajustados += 1
                except ValueError:
                    ui.warning(
                        f"Descartado por shape inválido {secuencia.shape}: {ruta_npy}"
                    )
                    descartados += 1
                    continue
            X.append(secuencia)
            y.append(idx)

    if not X:
        raise DatasetError("No se encontraron secuencias válidas para entrenar")

    if descartados > 0:
        ui.info(f"{descartados} secuencias descartadas por formato inválido.")
    if ajustados > 0:
        ui.info(
            f"{ajustados} secuencias remuestreadas a "
            f"{config.FRAMES_PER_SEQUENCE} frames."
        )

    return np.array(X), np.array(y), etiquetas


def ajustar_frames(secuencia: np.ndarray) -> np.ndarray:
    """Remuestrea una secuencia temporal a ``FRAMES_PER_SEQUENCE`` frames."""
    if secuencia.ndim != 2 or secuencia.shape[1] != config.FEATURES:
        raise ValueError("La secuencia no tiene el formato esperado")
    if secuencia.shape[0] <= 0:
        raise ValueError("La secuencia no contiene frames")
    if secuencia.shape[0] == config.FRAMES_PER_SEQUENCE:
        return secuencia

    indices = np.linspace(
        0,
        secuencia.shape[0] - 1,
        config.FRAMES_PER_SEQUENCE,
    ).round().astype(int)
    return secuencia[indices]
