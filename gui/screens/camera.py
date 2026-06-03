"""Pantalla de selección de cámara."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import cv2
from PIL import Image, ImageTk

from core.config import config
from gui.theme import SURFACE
from vision.camera import discover_cameras, get_selected_camera_index, set_selected_camera_index


class CameraScreenMixin:
    def _stop_camera_preview(self) -> None:
        after_id = getattr(self, "_camera_preview_after_id", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except tk.TclError:
                pass
            self._camera_preview_after_id = None

        cap = getattr(self, "_camera_preview_cap", None)
        if cap is not None:
            cap.release()
            self._camera_preview_cap = None

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

        preview_frame = ttk.Frame(card, style="Surface.TFrame")
        preview_frame.pack(fill="x", pady=(0, 16))
        preview_label = ttk.Label(
            preview_frame,
            text="Seleccioná una cámara y presioná Vista previa.",
            anchor="center",
            background="#101828",
            foreground="#e5e7eb",
        )
        preview_label.pack(fill="x", ipady=110)

        def render_preview() -> None:
            cap = getattr(self, "_camera_preview_cap", None)
            if cap is None:
                return

            ok, frame = cap.read()
            if ok:
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image.thumbnail((640, 360))
                photo = ImageTk.PhotoImage(image)
                preview_label.configure(image=photo, text="")
                preview_label.image = photo
            else:
                preview_label.configure(
                    image="",
                    text="No se pudo leer imagen de esta cámara.",
                )
                preview_label.image = None

            self._camera_preview_after_id = self.after(60, render_preview)

        def start_preview() -> None:
            self._stop_camera_preview()
            try:
                index = int(selected.get())
            except ValueError:
                messagebox.showerror("Cámara inválida", "Seleccioná un índice de cámara válido.")
                return

            cap = cv2.VideoCapture(index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
            if not cap.isOpened():
                cap.release()
                preview_label.configure(image="", text=f"No se pudo abrir la cámara {index}.")
                preview_label.image = None
                messagebox.showwarning("Cámara no disponible", f"No se pudo abrir la cámara {index}.")
                return

            self._camera_preview_cap = cap
            status.configure(text=f"Vista previa activa: cámara {index}")
            render_preview()

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
            start_preview()

        def save() -> None:
            try:
                index = int(selected.get())
                set_selected_camera_index(index)
                status.configure(text=f"Cámara seleccionada: {index}")
                messagebox.showinfo("Cámara seleccionada", f"Se usará la cámara {index}.")
                self._stop_camera_preview()
                self.show_dashboard()
            except ValueError as exc:
                messagebox.showerror("Cámara inválida", str(exc))

        def back() -> None:
            self._stop_camera_preview()
            self.show_dashboard()

        combo.bind("<<ComboboxSelected>>", lambda _event: start_preview())

        buttons = ttk.Frame(card, style="Surface.TFrame")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Volver", command=back).pack(side="left")
        ttk.Button(buttons, text="Detectar cámaras", command=refresh).pack(side="left", padx=8)
        ttk.Button(buttons, text="Vista previa", command=start_preview).pack(side="left")
        ttk.Button(buttons, text="Guardar selección", style="Primary.TButton", command=save).pack(side="right")
        self._output_panel(self.container)
        self.after(100, start_preview)
