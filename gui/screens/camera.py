"""Pantalla de selección de cámara."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from core.config import config
from gui.theme import SURFACE
from vision.camera import discover_cameras, get_selected_camera_index, set_selected_camera_index


class CameraScreenMixin:
    def show_camera_settings(self) -> None:
        self._clear()
        self._header("Seleccionar cámara", "Elegí qué cámara usar para captura y predicción.")
        card = self._card(self.container)
        selected = tk.StringVar(value=str(get_selected_camera_index()))

        ttk.Label(card, text="Cámara activa", background=SURFACE).pack(anchor="w", pady=(0, 4))
        combo = ttk.Combobox(
            card,
            textvariable=selected,
            values=[str(i) for i in self.camera_options],
            state="readonly",
        )
        combo.pack(fill="x", pady=(0, 12))

        status = ttk.Label(
            card,
            text=f"Cámara seleccionada: {get_selected_camera_index()}",
            style="CardText.TLabel",
        )
        status.pack(anchor="w", pady=(0, 16))

        def refresh() -> None:
            self.output_queue.put("\n[Camara] Buscando cámaras disponibles...\n")
            cameras = discover_cameras()
            if not cameras:
                cameras = [config.CAMERA_INDEX]
                messagebox.showwarning(
                    "Sin cámaras detectadas",
                    "No se detectaron cámaras disponibles. Se mantiene la cámara 0.",
                )
            self.camera_options = cameras
            combo.configure(values=[str(i) for i in cameras])
            if get_selected_camera_index() not in cameras:
                selected.set(str(cameras[0]))
            self.output_queue.put(f"[Camara] Disponibles: {', '.join(map(str, cameras))}\n")

        def save() -> None:
            try:
                index = int(selected.get())
                set_selected_camera_index(index)
                status.configure(text=f"Cámara seleccionada: {index}")
                messagebox.showinfo("Cámara seleccionada", f"Se usará la cámara {index}.")
                self.show_dashboard()
            except ValueError as exc:
                messagebox.showerror("Cámara inválida", str(exc))

        buttons = ttk.Frame(card, style="Surface.TFrame")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Volver", command=self.show_dashboard).pack(side="left")
        ttk.Button(buttons, text="Detectar cámaras", command=refresh).pack(side="left", padx=8)
        ttk.Button(buttons, text="Guardar selección", style="Primary.TButton", command=save).pack(side="right")
        self._output_panel(self.container)
