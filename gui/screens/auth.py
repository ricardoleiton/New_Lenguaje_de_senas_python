"""Pantallas de autenticación."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth import (
    InvalidUsername,
    UserAlreadyExists,
    UserError,
    WeakPassword,
    autenticar,
    crear_usuario,
    get_rbac,
    log_event,
    set_usuario,
)
from auth.session import Usuario


class AuthScreenMixin:
    def show_bootstrap(self) -> None:
        self._clear()
        self._header("Crear profesor inicial", "No hay usuarios registrados. Creá el primer usuario administrador.")
        card = self._card(self.container)
        fields = self._auth_fields(card, include_role=False)
        ttk.Button(
            card,
            text="Crear profesor",
            style="Primary.TButton",
            command=lambda: self._create_initial_user(fields),
        ).pack(fill="x", pady=(12, 0))

    def show_login(self) -> None:
        self._clear()
        self._header("Iniciar sesión", "Ingresá con tu usuario para acceder a las funciones disponibles por rol.")
        card = self._card(self.container)
        fields = self._auth_fields(card, include_role=False)
        ttk.Button(
            card,
            text="Entrar",
            style="Primary.TButton",
            command=lambda: self._login(fields),
        ).pack(fill="x", pady=(12, 0))

    def _auth_fields(self, parent, include_role: bool) -> dict[str, tk.StringVar]:
        values = {
            "username": tk.StringVar(),
            "password": tk.StringVar(),
            "password2": tk.StringVar(),
            "role": tk.StringVar(value="estudiante"),
        }
        self._field(parent, "Usuario", ttk.Entry(parent, textvariable=values["username"]))
        self._field(parent, "Contraseña", ttk.Entry(parent, textvariable=values["password"], show="*"))
        if include_role:
            roles = get_rbac().listar_roles()
            values["role"].set(roles[0] if roles else "")
            self._field(parent, "Rol", ttk.Combobox(parent, textvariable=values["role"], values=roles, state="readonly"))
        return values

    def _create_initial_user(self, fields: dict[str, tk.StringVar]) -> None:
        try:
            crear_usuario(fields["username"].get(), fields["password"].get(), "profesor")
            log_event(fields["username"].get(), "bootstrap_initial_user", "rol=profesor")
            messagebox.showinfo("Usuario creado", "Profesor inicial creado correctamente.")
            self.show_login()
        except (WeakPassword, InvalidUsername, UserAlreadyExists, UserError) as exc:
            messagebox.showerror("No se pudo crear", str(exc))

    def _login(self, fields: dict[str, tk.StringVar]) -> None:
        data = autenticar(fields["username"].get(), fields["password"].get())
        if data is None:
            messagebox.showerror("Login inválido", "Usuario o contraseña incorrectos.")
            return
        self.user = Usuario(username=data["username"], rol=data["rol"])
        set_usuario(self.user)
        log_event(self.user.username, "login")
        self.show_dashboard()
