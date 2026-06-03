import tempfile
import unittest
from pathlib import Path

from auth import users


class _FakeRBAC:
    def __init__(self):
        self.roles = ("profesor", "estudiante")

    def existe_rol(self, rol):
        return rol in self.roles

    def listar_roles(self):
        return list(self.roles)


class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_users_path = users.USERS_PATH
        self.previous_get_rbac = users.get_rbac
        users.USERS_PATH = Path(self.tmp.name) / "config" / "users.json"
        users.get_rbac = lambda: _FakeRBAC()

    def tearDown(self):
        users.USERS_PATH = self.previous_users_path
        users.get_rbac = self.previous_get_rbac
        self.tmp.cleanup()

    def test_username_validation_normalizes_and_rejects_invalid_values(self):
        self.assertEqual(users.validar_username(" Ricardo_01 "), "ricardo_01")

        for invalid in ("", "ab", "con espacio", "ácento", "user-name"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(users.InvalidUsername):
                    users.validar_username(invalid)

    def test_password_validation_requires_minimum_length_and_digit(self):
        users.validar_password("password1")

        with self.assertRaises(users.WeakPassword):
            users.validar_password("short1")
        with self.assertRaises(users.WeakPassword):
            users.validar_password("password")

    def test_create_authenticate_change_role_and_delete_user(self):
        users.crear_usuario("Profesor", "Password1", "profesor")

        stored = users.buscar_usuario("profesor")
        self.assertIsNotNone(stored)
        self.assertEqual(stored["username"], "profesor")
        self.assertEqual(stored["rol"], "profesor")
        self.assertNotEqual(stored["password_hash"], "Password1")

        authenticated = users.autenticar("profesor", "Password1")
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated["username"], "profesor")

        self.assertIsNone(users.autenticar("profesor", "wrongpass1"))

        users.cambiar_rol("profesor", "estudiante")
        self.assertEqual(users.buscar_usuario("profesor")["rol"], "estudiante")

        users.cambiar_password("profesor", "Newpass1")
        self.assertIsNone(users.autenticar("profesor", "Password1"))
        self.assertIsNotNone(users.autenticar("profesor", "Newpass1"))

        users.eliminar_usuario("profesor")
        self.assertIsNone(users.buscar_usuario("profesor"))

    def test_duplicate_user_and_unknown_role_are_rejected(self):
        users.crear_usuario("ricardo", "Password1", "profesor")

        with self.assertRaises(users.UserAlreadyExists):
            users.crear_usuario("ricardo", "Password1", "profesor")
        with self.assertRaises(users.UserError):
            users.crear_usuario("otro", "Password1", "admin")


if __name__ == "__main__":
    unittest.main()
