"""Tests del registro de versiones de modelos."""

from __future__ import annotations

import json
import os
import tempfile
import types
import unittest
from datetime import datetime
from pathlib import Path

from services import model_registry


class ModelRegistryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_config = model_registry.config
        model_registry.config = types.SimpleNamespace(MODELS_DIR=str(Path(self.tmp.name) / "models"))
        self.previous_config_paths = {
            "MODEL_PATH": getattr(model_registry.config, "MODEL_PATH", None),
            "LABELS_PATH": getattr(model_registry.config, "LABELS_PATH", None),
            "HISTORY_PATH": getattr(model_registry.config, "HISTORY_PATH", None),
        }
        model_registry.config.MODEL_PATH = str(Path(self.tmp.name) / "models" / "modelo_lstm.h5")
        model_registry.config.LABELS_PATH = str(Path(self.tmp.name) / "models" / "etiquetas.pkl")
        model_registry.config.HISTORY_PATH = str(Path(self.tmp.name) / "models" / "history.json")

    def tearDown(self) -> None:
        model_registry.config = self.previous_config
        self.tmp.cleanup()

    def test_generar_model_version_id_uses_timestamp_format(self) -> None:
        version_id = model_registry.generar_model_version_id(datetime(2026, 6, 2, 15, 4, 5))

        self.assertEqual(version_id, "20260602_150405")

    def test_ensure_model_version_dir_returns_expected_paths(self) -> None:
        paths = model_registry.ensure_model_version_dir("20260602_150405")

        self.assertTrue(Path(paths["dir"]).is_dir())
        self.assertEqual(Path(paths["model"]).name, "modelo_lstm.h5")
        self.assertEqual(Path(paths["labels"]).name, "etiquetas.pkl")
        self.assertEqual(Path(paths["history"]).name, "history.json")
        self.assertEqual(Path(paths["metadata"]).name, "metadata.json")

    def test_write_latest_model_version_writes_json(self) -> None:
        metadata = {"version_id": "20260602_150405", "classes": ["a", "b"]}

        model_registry.write_latest_model_version(metadata)

        written = json.loads(Path(model_registry.latest_model_version_path()).read_text(encoding="utf-8"))
        self.assertEqual(written, metadata)
        self.assertEqual(model_registry.read_latest_model_version(), metadata)

    def test_list_and_activate_model_version(self) -> None:
        paths = model_registry.ensure_model_version_dir("20260602_150405")
        Path(paths["model"]).write_text("model", encoding="utf-8")
        Path(paths["labels"]).write_text("labels", encoding="utf-8")
        Path(paths["history"]).write_text("history", encoding="utf-8")
        metadata = {
            "version_id": "20260602_150405",
            "classes": ["a", "b"],
            "sample_count": 20,
            "epochs": 3,
        }
        model_registry.write_json(paths["metadata"], metadata)

        versions = model_registry.list_model_versions()
        activated = model_registry.activate_model_version("20260602_150405", activated_by="ricardo")

        self.assertEqual([v["version_id"] for v in versions], ["20260602_150405"])
        self.assertEqual(activated["activated_by"], "ricardo")
        self.assertTrue(os.path.exists(model_registry.config.MODEL_PATH))
        self.assertEqual(model_registry.read_latest_model_version()["version_id"], "20260602_150405")


if __name__ == "__main__":
    unittest.main()
