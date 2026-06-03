"""Pantalla de administración de usuarios."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth import (
    InvalidUsername,
    UserAlreadyExists,
    UserError,
    UserNotFound,
    WeakPassword,
    cambiar_password,
    cambiar_rol,
    crear_usuario,
    eliminar_usuario,
    get_rbac,
    listar_usuarios,
    log_event,
)
from gui.theme import SURFACE


class UsersScreenMixin:
    def show_users(self) -> None:
        self._clear()
        self._header("Gestionar usuarios", "Administración de usuarios y roles.")
        ttk.Button(self.container, text="Volver al panel", command=self.show_dashboard).pack(anchor="w", pady=(0, 12))

        table = ttk.Treeview(self.container, columns=("username", "role", "active", "last"), show="headings", height=10)
        for col, label in [("username", "Usuario"), ("role", "Rol"), ("active", "Activo"), ("last", "Último login")]:
            table.heading(col, text=label)
            table.column(col, width=160)
        table.pack(fill="both", expand=True)

        def refresh() -> None:
            table.delete(*table.get_children())
            for user in listar_usuarios():
                table.insert(
                    "",
                    "end",
                    values=(
                        user["username"],
                        user["rol"],
                        "Sí" if user.get("activo", True) else "No",
                        user.get("ultimo_login") or "-",
                    ),
                )

        def selected_username() -> str | None:
            item = table.focus()
            if not item:
                messagebox.showwarning("Seleccioná usuario", "Elegí un usuario de la tabla.")
                return None
            return str(table.item(item, "values")[0])

        form = self._card(self.container)
        username = tk.StringVar()
        password = tk.StringVar()
        role = tk.StringVar(value=get_rbac().listar_roles()[0])
        self._field(form, "Usuario", ttk.Entry(form, textvariable=username))
        self._field(form, "Contraseña", ttk.Entry(form, textvariable=password, show="*"))
        self._field(form, "Rol", ttk.Combobox(form, textvariable=role, values=get_rbac().listar_roles(), state="readonly"))

        buttons = ttk.Frame(form, style="Surface.TFrame")
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Crear", style="Primary.TButton", command=lambda: self._user_create(username, password, role, refresh)).pack(side="left")
        ttk.Button(buttons, text="Cambiar rol", command=lambda: self._user_change_role(selected_username(), role.get(), refresh)).pack(side="left", padx=8)
        ttk.Button(buttons, text="Resetear contraseña", command=lambda: self._user_reset_password(selected_username(), password.get())).pack(side="left")
        ttk.Button(buttons, text="Eliminar", style="Danger.TButton", command=lambda: self._user_delete(selected_username(), refresh)).pack(side="right")
        refresh()

    def _user_create(self, username, password, role, refresh) -> None:
        try:
            crear_usuario(username.get(), password.get(), role.get())
            log_event(self.user.username, "user_create", f"target={username.get()} rol={role.get()}")
            refresh()
            messagebox.showinfo("Usuario creado", "Usuario creado correctamente.")
        except (WeakPassword, InvalidUsername, UserAlreadyExists, UserError) as exc:
            messagebox.showerror("Error", str(exc))

    def _user_change_role(self, username: str | None, role: str, refresh) -> None:
        if not username:
            return
        try:
            cambiar_rol(username, role)
            log_event(self.user.username, "user_change_role", f"target={username} new_rol={role}")
            refresh()
        except (UserNotFound, UserError, InvalidUsername) as exc:
            messagebox.showerror("Error", str(exc))

    def _user_reset_password(self, username: str | None, password: str) -> None:
        if not username:
            return
        try:
            cambiar_password(username, password)
            log_event(self.user.username, "user_reset_password", f"target={username}")
            messagebox.showinfo("Contraseña actualizada", "Contraseña actualizada correctamente.")
        except (UserNotFound, WeakPassword, InvalidUsername) as exc:
            messagebox.showerror("Error", str(exc))

    def _user_delete(self, username: str | None, refresh) -> None:
        if not username or self.user is None:
            return
        if username == self.user.username:
            messagebox.showerror("No permitido", "No podés eliminar tu propio usuario.")
            return
        if not messagebox.askyesno("Confirmar eliminación", f"¿Eliminar definitivamente a '{username}'?"):
            return
        try:
            eliminar_usuario(username)
            log_event(self.user.username, "user_delete", f"target={username}")
            refresh()
        except (UserNotFound, InvalidUsername) as exc:
            messagebox.showerror("Error", str(exc))
