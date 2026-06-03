"""Tests de estructura para la separación workflow/servicio."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ServicesStructureTestCase(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_operational_services_exist(self) -> None:
        for path in [
            "services/capture_service.py",
            "services/training_service.py",
            "services/prediction_service.py",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_workflows_delegate_to_services(self) -> None:
        expected = {
            "workflows/capturar.py": "services.capture_service",
            "workflows/entrenar.py": "services.training_service",
            "workflows/predecir.py": "services.prediction_service",
        }
        for workflow_path, service_import in expected.items():
            with self.subTest(workflow=workflow_path):
                self.assertIn(service_import, self._read(workflow_path))

    def test_services_do_not_require_permissions_directly(self) -> None:
        for path in [
            "services/capture_service.py",
            "services/training_service.py",
            "services/prediction_service.py",
        ]:
            with self.subTest(service=path):
                source = self._read(path)
                self.assertNotIn("usuario_actual", source)
                self.assertNotIn("requerir(", source)


if __name__ == "__main__":
    unittest.main()
