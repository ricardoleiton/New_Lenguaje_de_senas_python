"""Tema visual compartido por la interfaz Tkinter."""

from __future__ import annotations

from tkinter import ttk


BG = "#f5f7fb"
SURFACE = "#ffffff"
TEXT = "#17202a"
MUTED = "#667085"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
DANGER = "#dc2626"
BORDER = "#d8dee9"


def setup_style(style: ttk.Style) -> None:
    """Configura estilos comunes para todas las pantallas."""
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10), background=BG, foreground=TEXT)
    style.configure("TFrame", background=BG)
    style.configure("Surface.TFrame", background=SURFACE, relief="flat")
    style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), background=BG, foreground=TEXT)
    style.configure("Subtitle.TLabel", font=("Segoe UI", 10), background=BG, foreground=MUTED)
    style.configure("CardTitle.TLabel", font=("Segoe UI", 13, "bold"), background=SURFACE, foreground=TEXT)
    style.configure("CardText.TLabel", font=("Segoe UI", 10), background=SURFACE, foreground=MUTED)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
    style.configure("Primary.TButton", background=PRIMARY, foreground="#ffffff")
    style.map("Primary.TButton", background=[("active", PRIMARY_DARK)])
    style.configure("Danger.TButton", background=DANGER, foreground="#ffffff")
    style.configure("TEntry", padding=8)
    style.configure("TCombobox", padding=8)
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
