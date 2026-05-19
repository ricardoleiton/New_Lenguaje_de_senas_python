"""Módulo ml: arquitectura del modelo y carga del dataset.

Los imports son diferidos para evitar inicializar TensorFlow cuando solo se
necesita cargar datos.
"""


def __getattr__(name):
    if name == "construir_modelo":
        from .model import construir_modelo

        return construir_modelo
    if name in {"cargar_datos", "DatasetError"}:
        from .data_io import DatasetError, cargar_datos

        return {"cargar_datos": cargar_datos, "DatasetError": DatasetError}[name]
    raise AttributeError(f"module 'ml' has no attribute {name!r}")

__all__ = ["construir_modelo", "cargar_datos", "DatasetError"]
