"""Tests del protocolo formal de captura."""

from __future__ import annotations

import unittest

from services.capture_protocol import get_capture_protocol, protocol_summary_lines


class CaptureProtocolTestCase(unittest.TestCase):
    def test_protocol_contains_operational_sections(self) -> None:
        protocol = get_capture_protocol()

        self.assertTrue(protocol.objetivo)
        self.assertGreaterEqual(len(protocol.preparacion), 3)
        self.assertGreaterEqual(len(protocol.ejecucion), 3)
        self.assertGreaterEqual(len(protocol.criterios_calidad), 3)
        self.assertGreaterEqual(len(protocol.criterios_repeticion), 3)

    def test_summary_mentions_capture_parameters(self) -> None:
        summary = "\n".join(protocol_summary_lines())

        self.assertIn("secuencias", summary)
        self.assertIn("frames", summary)
        self.assertIn("Cuenta regresiva", summary)


if __name__ == "__main__":
    unittest.main()
