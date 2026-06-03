"""Tests mínimos de estructura de la GUI."""

from __future__ import annotations

import unittest

import gui_app
from gui import App


class GUIStructureTestCase(unittest.TestCase):
    def test_app_class_is_importable_from_gui_package(self) -> None:
        self.assertEqual(App.__name__, "App")

    def test_gui_app_keeps_legacy_entrypoint(self) -> None:
        self.assertIs(gui_app.App, App)


if __name__ == "__main__":
    unittest.main()
