import json
import tempfile
import unittest
from pathlib import Path

from auth import rbac


class RBACTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.roles_path = Path(self.tmp.name) / "roles.json"
        self.roles_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "permisos_disponibles": [
                        "capturar",
                        "entrenar",
                        "predecir",
                        "gestionar_usuarios",
                    ],
                    "roles": {
                        "estudiante": {
                            "descripcion": "Solo prediccion",
                            "permisos": ["predecir"],
                        },
                        "profesor": {
                            "descripcion": "Acceso completo",
                            "permisos": [
                                "capturar",
                                "entrenar",
                                "predecir",
                                "gestionar_usuarios",
                            ],
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        self.previous_instance = rbac._rbac_instance
        rbac._rbac_instance = rbac.RBAC(self.roles_path)

    def tearDown(self):
        rbac._rbac_instance = self.previous_instance
        self.tmp.cleanup()

    def test_loads_roles_and_permissions(self):
        catalog = rbac.RBAC(self.roles_path)

        self.assertTrue(catalog.existe_rol("profesor"))
        self.assertTrue(catalog.existe_rol("estudiante"))
        self.assertEqual(catalog.descripcion_rol("estudiante"), "Solo prediccion")
        self.assertIn("entrenar", catalog.permisos_de_rol("profesor"))
        self.assertNotIn("entrenar", catalog.permisos_de_rol("estudiante"))

    def test_permission_helpers_use_configured_catalog(self):
        self.assertTrue(rbac.tiene_permiso("profesor", "capturar"))
        self.assertTrue(rbac.tiene_permiso("estudiante", "predecir"))
        self.assertFalse(rbac.tiene_permiso("estudiante", "entrenar"))

    def test_requerir_raises_when_permission_is_missing(self):
        rbac.requerir("predecir", "estudiante")

        with self.assertRaises(rbac.PermissionDenied):
            rbac.requerir("entrenar", "estudiante")

    def test_missing_roles_file_raises_error(self):
        with self.assertRaises(rbac.RBACError):
            rbac.RBAC(Path(self.tmp.name) / "missing.json")


if __name__ == "__main__":
    unittest.main()
