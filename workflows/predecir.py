"""Workflow de predicción en tiempo real. Requiere permiso 'predecir'."""

from auth import requerir, usuario_actual
from core import ui
from services.prediction_service import ejecutar_prediccion


def main() -> None:
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return
    requerir("predecir", user.rol)
    ejecutar_prediccion(username=user.username)
