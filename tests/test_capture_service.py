"""Tests livianos del servicio de captura."""

from __future__ import annotations

import contextlib
import io
import tempfile
import types
import unittest
from pathlib import Path

from services import capture_service


class CaptureServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_config = capture_service.config
        self.sequences_dir = Path(self.tmp.name) / "secuencias"
        self.sequences_dir.mkdir()
        capture_service.config = types.SimpleNamespace(
            SEQUENCES_DIR=str(self.sequences_dir),
            GIFS_DIR=str(Path(self.tmp.name) / "gifs"),
            SEQUENCES_PER_CLASS=10,
            FRAMES_PER_SEQUENCE=10,
            CAPTURE_COUNTDOWN_SECONDS=5,
        )

    def tearDown(self) -> None:
        capture_service.config = self.previous_config
        self.tmp.cleanup()

    def test_imprimir_clases_capturadas_handles_empty_dataset(self) -> None:
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            capture_service.imprimir_clases_capturadas()

        self.assertIn("Todavía no hay", output.getvalue())

    def test_imprimir_protocolo_captura_does_not_depend_on_class_summary(self) -> None:
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            capture_service.imprimir_protocolo_captura()

        self.assertIn("Protocolo formal de captura", output.getvalue())


if __name__ == "__main__":
    unittest.main()
