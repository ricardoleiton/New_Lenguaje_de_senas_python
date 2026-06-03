"""Pantalla para seleccionar la versión activa del modelo."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from services.model_registry import (
    activate_model_version,
    list_model_versions,
    read_latest_model_version,
)


class ModelVersionsScreenMixin:
    def show_model_versions(self) -> None:
        self._clear()
        self._header(
            "Seleccionar modelo",
            "Elegí qué versión entrenada se usará para la predicción en tiempo real.",
        )

        latest = read_latest_model_version()
        active_id = latest.get("version_id") if latest else "-"

        summary = self._card(self.container)
        ttk.Label(summary, text="Modelo activo", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            summary,
            text=f"Versión actual: {active_id}",
            style="CardText.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        versions = list_model_versions()
        if not versions:
            card = self._card(self.container)
            ttk.Label(card, text="No hay versiones entrenadas.", style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(
                card,
                text="Entrená el modelo al menos una vez para generar versiones seleccionables.",
                style="CardText.TLabel",
                wraplength=900,
            ).pack(anchor="w", pady=(8, 0))
            ttk.Button(self.container, text="Volver", command=self.show_dashboard).pack(anchor="w")
            return

        table = ttk.Treeview(
            self.container,
            columns=("version", "active", "classes", "samples", "epochs", "user"),
            show="headings",
            height=10,
        )
        headings = [
            ("version", "Versión"),
            ("active", "Activa"),
            ("classes", "Clases"),
            ("samples", "Muestras"),
            ("epochs", "Epochs"),
            ("user", "Creado por"),
        ]
        for col, label in headings:
            table.heading(col, text=label)
            table.column(col, width=130)
        table.column("classes", width=260)
        table.pack(fill="both", expand=True)

        version_by_item: dict[str, str] = {}
        for metadata in versions:
            version_id = str(metadata.get("version_id", "-"))
            classes = ", ".join(metadata.get("classes", []))
            item = table.insert(
                "",
                "end",
                values=(
                    version_id,
                    "Sí" if version_id == active_id else "",
                    classes,
                    metadata.get("sample_count", "-"),
                    metadata.get("epochs", "-"),
                    metadata.get("created_by", "-"),
                ),
            )
            version_by_item[item] = version_id
            if version_id == active_id:
                table.selection_set(item)
                table.focus(item)

        detail = tk.StringVar(value="Seleccioná una versión para ver el detalle.")
        detail_label = ttk.Label(
            self.container,
            textvariable=detail,
            style="Subtitle.TLabel",
            wraplength=940,
        )
        detail_label.pack(anchor="w", pady=(12, 8))

        def selected_version() -> str | None:
            item = table.focus()
            if not item:
                messagebox.showwarning("Seleccioná una versión", "Elegí una versión de la tabla.")
                return None
            return version_by_item[item]

        def update_detail(_event=None) -> None:
            item = table.focus()
            if not item:
                return
            version_id = version_by_item[item]
            metadata = next(v for v in versions if str(v.get("version_id")) == version_id)
            classes = ", ".join(metadata.get("classes", [])) or "-"
            detail.set(
                f"Versión {version_id} | Clases: {classes} | "
                f"Muestras: {metadata.get('sample_count', '-')} | "
                f"Frames: {metadata.get('frames_per_sequence', '-')} | "
                f"Features: {metadata.get('features', '-')}"
            )

        def activate() -> None:
            version_id = selected_version()
            if not version_id or self.user is None:
                return
            if not messagebox.askyesno(
                "Activar modelo",
                f"¿Usar la versión {version_id} para predicción?",
            ):
                return
            try:
                activate_model_version(version_id, activated_by=self.user.username)
            except OSError as exc:
                messagebox.showerror("No se pudo activar", str(exc))
                return
            messagebox.showinfo("Modelo activo", f"Versión activa: {version_id}")
            self.show_model_versions()

        table.bind("<<TreeviewSelect>>", update_detail)

        buttons = ttk.Frame(self.container)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Volver", command=self.show_dashboard).pack(side="left")
        ttk.Button(
            buttons,
            text="Activar versión",
            style="Primary.TButton",
            command=activate,
        ).pack(side="right")
