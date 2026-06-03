"""Pantalla de captura de letras, números y palabras."""

from __future__ import annotations

import os
import string
import tkinter as tk
from tkinter import messagebox, ttk

from core.config import config
from gui.theme import SURFACE


class CaptureScreenMixin:
    def show_capture(self) -> None:
        from workflows.capturar import clases_capturadas

        self._clear()
        self._header(
            "Capturar letra, número o palabra",
            "Seleccioná el objetivo. La cámara mostrará claramente qué gesto grabar.",
        )

        captured = clases_capturadas()
        summary = self._card(self.container)
        ttk.Label(summary, text="Clases ya capturadas", style="CardTitle.TLabel").pack(anchor="w")
        letters = ", ".join(f"{value} ({count})" for value, count in captured["letras"]) or "Sin letras capturadas"
        numbers = ", ".join(f"{value} ({count})" for value, count in captured["numeros"]) or "Sin números capturados"
        words = ", ".join(f"{value} ({count})" for value, count in captured["palabras"]) or "Sin palabras capturadas"
        ttk.Label(summary, text=f"Letras: {letters}", style="CardText.TLabel", wraplength=900).pack(anchor="w", pady=(8, 2))
        ttk.Label(summary, text=f"Números: {numbers}", style="CardText.TLabel", wraplength=900).pack(anchor="w", pady=(0, 2))
        ttk.Label(summary, text=f"Palabras: {words}", style="CardText.TLabel", wraplength=900).pack(anchor="w")

        card = self._card(self.container)
        capture_type = tk.StringVar(value="letra")
        value = tk.StringVar(value="a")
        overwrite = tk.BooleanVar(value=False)

        row = ttk.Frame(card, style="Surface.TFrame")
        row.pack(fill="x", pady=(0, 12))
        ttk.Radiobutton(row, text="Letra (A-Z)", variable=capture_type, value="letra").pack(side="left", padx=(0, 16))
        ttk.Radiobutton(row, text="Número (0-9)", variable=capture_type, value="número").pack(side="left", padx=(0, 16))
        ttk.Radiobutton(row, text="Palabra", variable=capture_type, value="palabra").pack(side="left")
        self._field(card, "Valor", ttk.Entry(card, textvariable=value, width=12))
        ttk.Checkbutton(card, text="Sobrescribir datos existentes de esta clase", variable=overwrite).pack(anchor="w", pady=(4, 16))

        buttons = ttk.Frame(card, style="Surface.TFrame")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Volver", command=self.show_dashboard).pack(side="left")
        ttk.Button(
            buttons,
            text="Iniciar captura",
            style="Primary.TButton",
            command=lambda: self._start_capture(capture_type.get(), value.get(), overwrite.get()),
        ).pack(side="right")

        self._output_panel(self.container)

    def _start_capture(self, capture_type: str, raw_value: str, overwrite: bool) -> None:
        value = raw_value.strip().lower()
        if capture_type == "letra" and not (len(value) == 1 and value in string.ascii_lowercase):
            messagebox.showerror("Valor inválido", "Ingresá una sola letra entre A y Z.")
            return
        if capture_type == "número" and not (len(value) == 1 and value.isdigit()):
            messagebox.showerror("Valor inválido", "Ingresá un solo número entre 0 y 9.")
            return
        if capture_type == "palabra":
            value = value.replace(" ", "_")
            if not (len(value) >= 2 and value.replace("_", "").isalpha()):
                messagebox.showerror(
                    "Valor inválido",
                    "Ingresá una palabra completa, sin números ni símbolos.",
                )
                return
        class_dir = os.path.join(config.SEQUENCES_DIR, value)
        existing = [f for f in os.listdir(class_dir)] if os.path.isdir(class_dir) else []
        if existing and not overwrite:
            ok = messagebox.askyesno(
                "Datos existentes",
                f"Ya existen datos para '{value}'. ¿Querés sobrescribirlos?",
            )
            if not ok:
                return
            overwrite = True

        from workflows.capturar import ejecutar_captura

        self._run_background(
            f"Captura de {capture_type} {value.upper()}",
            lambda: ejecutar_captura(capture_type, value, sobrescribir=overwrite),
        )
