"""Pantallas para procesos largos: entrenamiento y predicción."""

from __future__ import annotations

import contextlib
import threading
from tkinter import messagebox, ttk

from gui.output import QueueWriter


class ProcessScreenMixin:
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
