"""Shared OpenCV overlay primitives for camera workflows."""

from __future__ import annotations

import unicodedata

import cv2


WINDOW_CAPTURE = "Lengua de Senas | Captura"
WINDOW_PREDICTION = "Lengua de Senas | Prediccion"
WINDOW_GIF = "Lengua de Senas | Referencia"

FONT = cv2.FONT_HERSHEY_SIMPLEX

# BGR palette
BG = (22, 24, 29)
PANEL = (32, 36, 43)
PRIMARY = (80, 190, 255)
SUCCESS = (74, 222, 128)
WARNING = (80, 210, 245)
TEXT = (245, 247, 250)
MUTED = (178, 186, 196)
SHADOW = (0, 0, 0)


def _opencv_text(text: str) -> str:
    """OpenCV Hershey fonts are ASCII-only; normalize UI text before drawing."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.replace("  ", " ").strip()


def _blend_rect(frame, x1: int, y1: int, x2: int, y2: int, color, alpha: float) -> None:
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def put_text(
    frame,
    text: str,
    origin: tuple[int, int],
    scale: float = 0.65,
    color=TEXT,
    thickness: int = 2,
) -> None:
    text = _opencv_text(text)
    x, y = origin
    cv2.putText(frame, text, (x + 1, y + 1), FONT, scale, SHADOW, thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), FONT, scale, color, thickness, cv2.LINE_AA)


def draw_top_bar(frame, title: str, subtitle: str = "") -> None:
    h, w = frame.shape[:2]
    bar_h = 74
    _blend_rect(frame, 0, 0, w, bar_h, BG, 0.82)
    cv2.rectangle(frame, (0, bar_h - 2), (w, bar_h), PRIMARY, -1)
    put_text(frame, title.upper(), (24, 31), 0.76, TEXT, 2)
    if subtitle:
        put_text(frame, subtitle, (24, 58), 0.48, MUTED, 1)


def draw_bottom_bar(frame, text: str = "Q: salir") -> None:
    h, w = frame.shape[:2]
    bar_h = 44
    _blend_rect(frame, 0, h - bar_h, w, h, BG, 0.78)
    put_text(frame, text, (24, h - 16), 0.52, MUTED, 1)


def draw_progress(frame, label: str, current: int, total: int) -> None:
    h, w = frame.shape[:2]
    x, y = 24, 96
    width = min(440, w - 48)
    height = 78
    _blend_rect(frame, x, y, x + width, y + height, PANEL, 0.84)
    ratio = 0 if total <= 0 else min(current / total, 1)
    put_text(frame, label.upper(), (x + 16, y + 28), 0.55, TEXT, 2)
    put_text(frame, f"{current}/{total}", (x + width - 86, y + 28), 0.55, MUTED, 1)
    track_y = y + 50
    cv2.rectangle(frame, (x + 16, track_y), (x + width - 16, track_y + 10), (60, 65, 74), -1)
    cv2.rectangle(
        frame,
        (x + 16, track_y),
        (x + 16 + int((width - 32) * ratio), track_y + 10),
        SUCCESS,
        -1,
    )


def draw_capture_target(frame, kind: str, value: str, sequence: str = "") -> None:
    h, w = frame.shape[:2]
    box_w = min(420, w - 48)
    box_h = 140
    x, y = 24, 188
    _blend_rect(frame, x, y, x + box_w, y + box_h, PANEL, 0.86)
    cv2.rectangle(frame, (x, y), (x + 5, y + box_h), PRIMARY, -1)
    put_text(frame, "CAPTURAR", (x + 20, y + 30), 0.5, MUTED, 1)
    put_text(frame, kind.upper(), (x + 20, y + 60), 0.54, TEXT, 1)
    put_text(frame, value.upper(), (x + 20, y + 118), 1.75, PRIMARY, 4)
    if sequence:
        put_text(frame, sequence, (x + box_w - 116, y + 118), 0.58, MUTED, 1)


def draw_prediction(frame, label: str, confidence: float) -> None:
    h, w = frame.shape[:2]
    text = label.upper()
    conf = f"{confidence:.0%}"
    box_w = min(520, w - 48)
    box_h = 108
    x, y = 24, 188
    _blend_rect(frame, x, y, x + box_w, y + box_h, PANEL, 0.86)
    cv2.rectangle(frame, (x, y), (x + 5, y + box_h), SUCCESS, -1)
    put_text(frame, "GESTO DETECTADO", (x + 20, y + 30), 0.5, MUTED, 1)
    put_text(frame, text, (x + 20, y + 78), 1.35, SUCCESS, 3)
    put_text(frame, conf, (x + box_w - 96, y + 78), 0.75, TEXT, 2)
