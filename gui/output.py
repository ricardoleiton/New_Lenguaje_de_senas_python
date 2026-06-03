"""Salida de procesos en segundo plano hacia el panel de la GUI."""

from __future__ import annotations

import io
import queue
import re


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
