"""Audit log de eventos de seguridad y acciones privilegiadas.

Formato de cada línea::

    YYYY-MM-DDTHH:MM:SS | INFO | user=<u> | action=<a> | <OK|FAIL> | <detalle>

Sin rotación automática en esta versión. Si el archivo crece, se puede
sumar ``RotatingFileHandler`` sin cambiar la API pública.
"""

import logging
from pathlib import Path
from typing import Optional

LOG_DIR = Path("logs")
LOG_PATH = LOG_DIR / "audit.log"

_logger: Optional[logging.Logger] = None


def _get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("audit")
    log.setLevel(logging.INFO)
    log.propagate = False  # no propagar al root logger / consola

    # Evitar handlers duplicados si _get_logger se llama varias veces
    if not log.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                "%Y-%m-%dT%H:%M:%S",
            )
        )
        log.addHandler(handler)

    _logger = log
    return _logger


def log_event(
    usuario: str,
    accion: str,
    detalle: str = "",
    exitoso: bool = True,
) -> None:
    """Registra un evento de auditoría."""
    estado = "OK" if exitoso else "FAIL"
    msg = f"user={usuario} | action={accion} | {estado}"
    if detalle:
        msg += f" | {detalle}"
    _get_logger().info(msg)
