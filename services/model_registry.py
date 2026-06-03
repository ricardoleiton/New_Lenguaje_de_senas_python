"""Registro de versiones de modelos entrenados."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from typing import Any

from core.config import config


VERSION_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def generar_model_version_id(now: datetime | None = None) -> str:
    """Genera un identificador estable para una corrida de entrenamiento."""
    current = now or datetime.now()
    return current.strftime(VERSION_TIMESTAMP_FORMAT)


def version_dir(version_id: str) -> str:
    """Devuelve la carpeta de una versión entrenada."""
    return os.path.join(config.MODELS_DIR, "versions", version_id)


def model_version_paths(version_id: str) -> dict[str, str]:
    """Devuelve las rutas de artefactos para una versión."""
    base = version_dir(version_id)
    return {
        "dir": base,
        "model": os.path.join(base, "modelo_lstm.h5"),
        "labels": os.path.join(base, "etiquetas.pkl"),
        "history": os.path.join(base, "history.json"),
        "metadata": os.path.join(base, "metadata.json"),
    }


def latest_model_version_path() -> str:
    """Devuelve la ruta del puntero a la última versión entrenada."""
    return os.path.join(config.MODELS_DIR, "latest_model_version.json")


def ensure_model_version_dir(version_id: str) -> dict[str, str]:
    """Crea la carpeta de versión y devuelve sus rutas."""
    paths = model_version_paths(version_id)
    os.makedirs(paths["dir"], exist_ok=True)
    return paths


def write_json(path: str, data: dict[str, Any]) -> None:
    """Escribe JSON con formato estable."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_latest_model_version(metadata: dict[str, Any]) -> None:
    """Actualiza el puntero a la última versión entrenada."""
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    write_json(latest_model_version_path(), metadata)


def read_latest_model_version() -> dict[str, Any] | None:
    """Lee metadata de la última versión entrenada, si existe."""
    path = latest_model_version_path()
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_model_version_metadata(version_id: str) -> dict[str, Any]:
    """Lee metadata de una versión entrenada."""
    path = model_version_paths(version_id)["metadata"]
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe metadata para la versión {version_id}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_model_versions() -> list[dict[str, Any]]:
    """Lista versiones entrenadas ordenadas de más reciente a más antigua."""
    versions_root = os.path.join(config.MODELS_DIR, "versions")
    if not os.path.isdir(versions_root):
        return []

    versions: list[dict[str, Any]] = []
    for name in sorted(os.listdir(versions_root), reverse=True):
        paths = model_version_paths(name)
        if not os.path.isdir(paths["dir"]) or not os.path.exists(paths["metadata"]):
            continue
        try:
            metadata = read_model_version_metadata(name)
        except (OSError, json.JSONDecodeError):
            continue
        metadata.setdefault("version_id", name)
        versions.append(metadata)
    return versions


def activate_model_version(version_id: str, activated_by: str = "sistema") -> dict[str, Any]:
    """Activa una versión copiando sus artefactos a las rutas usadas por predicción."""
    paths = model_version_paths(version_id)
    required = {
        "model": paths["model"],
        "labels": paths["labels"],
        "history": paths["history"],
        "metadata": paths["metadata"],
    }
    missing = [path for path in required.values() if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError(
            f"La versión {version_id} está incompleta. Faltan: {', '.join(missing)}"
        )

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    shutil.copy2(paths["model"], config.MODEL_PATH)
    shutil.copy2(paths["labels"], config.LABELS_PATH)
    shutil.copy2(paths["history"], config.HISTORY_PATH)

    metadata = read_model_version_metadata(version_id)
    metadata["activated_by"] = activated_by
    metadata["activated_at"] = datetime.now().isoformat(timespec="seconds")
    write_latest_model_version(metadata)
    return metadata
