"""Console helpers for Windows-friendly Unicode output."""

import contextlib
import os
import sys


def configure_unicode_output() -> None:
    """Prefer UTF-8 for stdout/stderr when the host stream supports it."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


@contextlib.contextmanager
def suppress_native_stderr():
    """Temporarily silence native-library stderr noise when possible."""
    try:
        stderr_fd = sys.stderr.fileno()
    except (AttributeError, OSError):
        yield
        return

    saved_fd = os.dup(stderr_fd)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull_fd, stderr_fd)
        yield
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(saved_fd)
        os.close(devnull_fd)
