"""Pantalla principal y cierre de sesión."""

from __future__ import annotations

from tkinter import ttk

from auth import cerrar_sesion, get_rbac, log_event
from vision.camera import get_selected_camera_index


class DashboardScreenMixin:
    def show_dashboard(self) -> None:
        self._clear()
        assert self.user is not None
        self._header(
            "Panel principal",
            f"Sesión: {self.user.username} | Rol: {self.user.rol} | Cámara: {get_selected_camera_index()}",
        )

        grid = ttk.Frame(self.container)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1, uniform="cards")

        permisos = set(get_rbac().permisos_de_rol(self.user.rol))
        row = col = 0
        actions = [
            ("Seleccionar cámara", "Detectá cámaras instaladas y elegí cuál usar.", "predecir", self.show_camera_settings),
            ("Capturar gesto", "Elegí letra, número o palabra y grabá las secuencias con cámara.", "capturar", self.show_capture),
            ("Entrenar modelo", "Reentrená el LSTM con el dataset disponible.", "entrenar", self.run_training),
            ("Seleccionar modelo", "Elegí qué versión entrenada se usará para predecir.", "entrenar", self.show_model_versions),
            ("Predicción en tiempo real", "Abrí la cámara y detectá gestos con el modelo actual.", "predecir", self.run_prediction),
            ("Gestionar usuarios", "Crear, eliminar y cambiar roles o contraseñas.", "gestionar_usuarios", self.show_users),
        ]
        for title, desc, perm, command in actions:
            if perm not in permisos:
                continue
            self._action_card(grid, row, col, title, desc, command)
            col += 1
            if col > 1:
                col = 0
                row += 1

        footer = ttk.Frame(self.container)
        footer.pack(fill="x", pady=(16, 0))
        ttk.Button(footer, text="Cambiar mi contraseña", command=self.show_password_change).pack(side="left")
        ttk.Button(footer, text="Cerrar sesión", command=self._logout).pack(side="right")

    def _logout(self) -> None:
        if self.user:
            log_event(self.user.username, "logout")
        cerrar_sesion()
        self.user = None
        self.show_login()
