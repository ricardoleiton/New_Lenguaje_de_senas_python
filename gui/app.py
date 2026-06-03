"""Aplicación Tkinter principal."""

from __future__ import annotations

import queue
import tkinter as tk
from tkinter import ttk

from auth import existe_usuarios
from auth.session import Usuario
from core.config import config
from gui.screens.auth import AuthScreenMixin
from gui.screens.camera import CameraScreenMixin
from gui.screens.capture import CaptureScreenMixin
from gui.screens.dashboard import DashboardScreenMixin
from gui.screens.model_versions import ModelVersionsScreenMixin
from gui.screens.password import PasswordScreenMixin
from gui.screens.process import ProcessScreenMixin
from gui.screens.users import UsersScreenMixin
from gui.theme import BG, SURFACE, setup_style
from version import __app_name__, __version__


class App(
    AuthScreenMixin,
    DashboardScreenMixin,
    CameraScreenMixin,
    CaptureScreenMixin,
    ProcessScreenMixin,
    ModelVersionsScreenMixin,
    UsersScreenMixin,
    PasswordScreenMixin,
    tk.Tk,
):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{__app_name__} v{__version__}")
        self.geometry("1040x680")
        self.minsize(940, 620)
        self.configure(bg=BG)

        self.user: Usuario | None = None
        self.output_queue: queue.Queue[str] = queue.Queue()
        self.running = False
        self.camera_options = [config.CAMERA_INDEX]

        self._setup_style()
        self.container = ttk.Frame(self, padding=24)
        self.container.pack(fill="both", expand=True)
        self.after(100, self._drain_output)

        if existe_usuarios():
            self.show_login()
        else:
            self.show_bootstrap()

    def _setup_style(self) -> None:
        setup_style(ttk.Style())

    def _clear(self) -> None:
        stop_camera_preview = getattr(self, "_stop_camera_preview", None)
        if callable(stop_camera_preview):
            stop_camera_preview()
        for child in self.container.winfo_children():
            child.destroy()

    def _header(self, title: str, subtitle: str) -> None:
        ttk.Label(self.container, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.container, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 20))

    def _card(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Surface.TFrame", padding=20)
        frame.pack(fill="x", pady=(0, 16))
        return frame

    def _action_card(self, parent, row: int, col: int, title: str, desc: str, command) -> None:
        card = ttk.Frame(parent, style="Surface.TFrame", padding=20)
        card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=desc, style="CardText.TLabel", wraplength=360).pack(anchor="w", pady=(8, 18))
        ttk.Button(card, text="Abrir", style="Primary.TButton", command=command).pack(anchor="e")

    def _field(self, parent, label: str, widget) -> None:
        ttk.Label(parent, text=label, background=SURFACE).pack(anchor="w", pady=(0, 4))
        widget.pack(fill="x", pady=(0, 12))

    def _output_panel(self, parent) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        self.output = tk.Text(
            frame,
            height=12,
            wrap="word",
            font=("Consolas", 10),
            bg="#101828",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
        )
        self.output.pack(fill="both", expand=True)

    def _drain_output(self) -> None:
        if hasattr(self, "output") and self.output.winfo_exists():
            while not self.output_queue.empty():
                self.output.insert("end", self.output_queue.get())
                self.output.see("end")
        self.after(100, self._drain_output)
