"""Workflow de entrenamiento del modelo LSTM. Requiere permiso 'entrenar'."""

from auth import requerir, usuario_actual
from core import ui
from services.training_service import entrenar_modelo


def main() -> None:
    user = usuario_actual()
    if user is None:
        ui.error("No hay sesión activa")
        return
    requerir("entrenar", user.rol)
    entrenar_modelo(username=user.username)
