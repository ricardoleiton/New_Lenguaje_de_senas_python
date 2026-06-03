"""Pantalla para cambio de contraseña propia."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth import WeakPassword, cambiar_password, log_event


class PasswordScreenMixin:
    def show_password_change(self) -> None:
        self._clear()
        self._header("Cambiar contraseña", "Actualizá la contraseña de tu usuario.")
        card = self._card(self.container)
        pw1 = tk.StringVar()
        pw2 = tk.StringVar()
        self._field(card, "Nueva contraseña", ttk.Entry(card, textvariable=pw1, show="*"))
        self._field(card, "Repetir contraseña", ttk.Entry(card, textvariable=pw2, show="*"))
        ttk.Button(card, text="Volver", command=self.show_dashboard).pack(side="left", pady=(12, 0))
        ttk.Button(card, text="Guardar", style="Primary.TButton", command=lambda: self._save_my_password(pw1.get(), pw2.get())).pack(side="right", pady=(12, 0))

    def _save_my_password(self, pw1: str, pw2: str) -> None:
        if self.user is None:
            return
        if pw1 != pw2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        try:
            cambiar_password(self.user.username, pw1)
            log_event(self.user.username, "self_password_change")
            messagebox.showinfo("Listo", "Contraseña actualizada.")
            self.show_dashboard()
        except WeakPassword as exc:
            messagebox.showerror("Error", str(exc))
