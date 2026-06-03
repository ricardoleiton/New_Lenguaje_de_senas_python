"""Protocolo formal para captura de dataset."""

from __future__ import annotations

from dataclasses import dataclass

from core.config import config


@dataclass(frozen=True)
class CaptureProtocol:
    objetivo: str
    preparacion: tuple[str, ...]
    ejecucion: tuple[str, ...]
    criterios_calidad: tuple[str, ...]
    criterios_repeticion: tuple[str, ...]


def get_capture_protocol() -> CaptureProtocol:
    """Devuelve el protocolo vigente de captura."""
    return CaptureProtocol(
        objetivo=(
            "Obtener secuencias limpias, consistentes y comparables para letras, "
            "números y palabras completas."
        ),
        preparacion=(
            "Usar iluminación frontal o lateral suave, evitando contraluz.",
            "Ubicar cámara, manos, rostro y hombros dentro del encuadre.",
            "Mantener fondo simple y sin movimiento detrás del usuario.",
            "Retirar objetos que tapen manos, muñecas, rostro u hombros.",
            "Seleccionar la cámara correcta antes de iniciar si hay más de una.",
        ),
        ejecucion=(
            f"Capturar {config.SEQUENCES_PER_CLASS} secuencias por clase.",
            f"Cada secuencia debe reunir {config.FRAMES_PER_SEQUENCE} frames válidos.",
            f"Usar la cuenta regresiva inicial de {config.CAPTURE_COUNTDOWN_SECONDS} segundos para acomodarse.",
            "Mantener el gesto estable durante cada secuencia.",
            "Presionar Q solo si hay que cancelar o repetir la toma.",
        ),
        criterios_calidad=(
            "La mano o manos principales deben verse completas.",
            "El gesto debe corresponder exactamente a la clase seleccionada.",
            "La postura debe ser natural y repetible.",
            "El movimiento debe ser estable, sin cambios bruscos de posición.",
            "La captura no debe mezclar dos gestos distintos en la misma secuencia.",
        ),
        criterios_repeticion=(
            "Repetir si la cámara pierde manos, rostro u hombros durante la toma.",
            "Repetir si se captura una clase incorrecta.",
            "Repetir si aparece otra persona u objeto tapando el gesto.",
            "Repetir si la iluminación cambia de forma marcada.",
            "Repetir si el contador avanza con una postura incorrecta.",
        ),
    )


def protocol_summary_lines() -> tuple[str, ...]:
    """Resumen corto para mostrar antes de capturar."""
    protocol = get_capture_protocol()
    return (
        f"{config.SEQUENCES_PER_CLASS} secuencias por clase, "
        f"{config.FRAMES_PER_SEQUENCE} frames válidos por secuencia.",
        f"Cuenta regresiva inicial: {config.CAPTURE_COUNTDOWN_SECONDS} segundos.",
        "Manos, rostro y hombros visibles dentro del encuadre.",
        "Gesto estable y clase correcta durante toda la toma.",
        "Repetir si hay pérdida de landmarks, bloqueo visual o iluminación deficiente.",
        protocol.objetivo,
    )
