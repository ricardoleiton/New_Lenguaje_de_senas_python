"""Shared console presentation helpers."""

from __future__ import annotations

from typing import Iterable, Tuple


class ConsoleStyle:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"


LINE_WIDTH = 72


def _label(text: str, color: str) -> str:
    return f"{color}{ConsoleStyle.BOLD}{text:<8}{ConsoleStyle.RESET}"


def title(text: str, subtitle: str | None = None) -> None:
    print()
    print(ConsoleStyle.BLUE + "=" * LINE_WIDTH + ConsoleStyle.RESET)
    print(f"{ConsoleStyle.BOLD}{text.upper():^{LINE_WIDTH}}{ConsoleStyle.RESET}")
    if subtitle:
        print(f"{ConsoleStyle.GRAY}{subtitle:^{LINE_WIDTH}}{ConsoleStyle.RESET}")
    print(ConsoleStyle.BLUE + "=" * LINE_WIDTH + ConsoleStyle.RESET)


def section(text: str) -> None:
    print()
    print(f"{ConsoleStyle.CYAN}{ConsoleStyle.BOLD}{text}{ConsoleStyle.RESET}")
    print(f"{ConsoleStyle.GRAY}{'-' * min(len(text), LINE_WIDTH)}{ConsoleStyle.RESET}")


def step(text: str) -> None:
    print(f"{_label('PASO', ConsoleStyle.CYAN)} {text}")


def info(text: str) -> None:
    print(f"{_label('INFO', ConsoleStyle.BLUE)} {text}")


def success(text: str) -> None:
    print(f"{_label('OK', ConsoleStyle.GREEN)} {text}")


def warning(text: str) -> None:
    print(f"{_label('AVISO', ConsoleStyle.YELLOW)} {text}")


def error(text: str) -> None:
    print(f"{_label('ERROR', ConsoleStyle.RED)} {text}")


def muted(text: str) -> None:
    print(f"{ConsoleStyle.GRAY}{text}{ConsoleStyle.RESET}")


def metric_rows(rows: Iterable[Tuple[str, object]]) -> None:
    for label, value in rows:
        print(f"  {ConsoleStyle.GRAY}{label:<18}{ConsoleStyle.RESET} {value}")


def prompt(text: str) -> str:
    return f"{ConsoleStyle.BOLD}{text}{ConsoleStyle.RESET} "
