"""Interfaz gráfica de escritorio para la aplicación.

Ejecutar:

    .\.venv\Scripts\python.exe gui_app.py
"""

from __future__ import annotations

import contextlib
import io
import os
import queue
import re
import string
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from auth import (
    InvalidUsername,
    UserAlreadyExists,
    UserError,
    UserNotFound,
    WeakPassword,
    autenticar,
    cambiar_password,
    cambiar_rol,
    cerrar_sesion,
    crear_usuario,
    eliminar_usuario,
    existe_usuarios,
    get_rbac,
    listar_usuarios,
    log_event,
    set_usuario,
)
from auth.session import Usuario
from core.config import config
from vision.camera import (
    discover_cameras,
    get_selected_camera_index,
    set_selected_camera_index,
)
from version import __app_name__, __version__


BG = "#f5f7fb"
SURFACE = "#ffffff"
TEXT = "#17202a"
MUTED = "#667085"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
DANGER = "#dc2626"
BORDER = "#d8dee9"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class QueueWriter(io.TextIOBase):
    def __init__(self, output_queue: queue.Queue[str]) -> None:
        self.output_queue = output_queue

    def write(self, text: str) -> int:
        if text:
            self.output_queue.put(ANSI_RE.sub("", text))
        return len(text)

    def flush(self) -> None:
        pass


class App(tk.Tk):
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
        style = ttk.Style()
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

    def _clear(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()

    def _header(self, title: str, subtitle: str) -> None:
        ttk.Label(self.container, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.container, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 20))

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

    def run_training(self) -> None:
        from workflows.entrenar import main as train_main

        self.show_process("Entrenamiento del modelo", "El proceso puede tardar varios minutos.")
        self._run_background("Entrenamiento", train_main)

    def run_prediction(self) -> None:
        from workflows.predecir import main as predict_main

        self.show_process("Predicción en tiempo real", "Se abrirá una ventana de cámara. Presioná Q para salir.")
        self._run_background("Predicción", predict_main)

    def show_process(self, title: str, subtitle: str) -> None:
        self._clear()
        self._header(title, subtitle)
        ttk.Button(self.container, text="Volver al panel", command=self.show_dashboard).pack(anchor="w", pady=(0, 12))
        self._output_panel(self.container)

    def _run_background(self, label: str, func) -> None:
        if self.running:
            messagebox.showwarning("Proceso en ejecución", "Esperá a que termine el proceso actual.")
            return
        self.running = True
        self.output_queue.put(f"\n[{label}] Iniciado.\n")

        def worker() -> None:
            writer = QueueWriter(self.output_queue)
            try:
                with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                    func()
                self.output_queue.put(f"\n[{label}] Finalizado.\n")
            except Exception as exc:  # noqa: BLE001
                self.output_queue.put(f"\n[{label}] Error: {type(exc).__name__}: {exc}\n")
            finally:
                self.running = False

        threading.Thread(target=worker, daemon=True).start()

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

    def _logout(self) -> None:
        if self.user:
            log_event(self.user.username, "logout")
        cerrar_sesion()
        self.user = None
        self.show_login()

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
        self.output = tk.Text(frame, height=12, wrap="word", font=("Consolas", 10), bg="#101828", fg="#e5e7eb", insertbackground="#e5e7eb")
        self.output.pack(fill="both", expand=True)

    def _drain_output(self) -> None:
        if hasattr(self, "output") and self.output.winfo_exists():
            while not self.output_queue.empty():
                self.output.insert("end", self.output_queue.get())
                self.output.see("end")
        self.after(100, self._drain_output)


if __name__ == "__main__":
    App().mainloop()
