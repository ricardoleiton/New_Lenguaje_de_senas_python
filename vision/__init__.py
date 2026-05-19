"""Módulo vision: cámara, dibujo de landmarks y manejo de GIFs."""

from .camera import (
    initialize_holistic,
    setup_camera,
    draw_holistic_landmarks,
    generar_gif,
    leer_gif,
)

__all__ = [
    "initialize_holistic",
    "setup_camera",
    "draw_holistic_landmarks",
    "generar_gif",
    "leer_gif",
]
