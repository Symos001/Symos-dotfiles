#!/usr/bin/env python3
# =============================================================================
# logger.py — Sistema de logging com cores
# =============================================================================

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── Cores ────────────────────────────────────────────────────────────────────


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class LogIcons:
    INFO = "✓"
    WARNING = "⚠"
    ERROR = "✗"
    DEBUG = "·"
    SUCCESS = "✅"
    FAIL = "❌"
    SKIP = "⊘"


# ─── Formatter ────────────────────────────────────────────────────────────────


class ColorFormatter(logging.Formatter):
    """Formatter com cores para terminal."""

    COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: f"{Colors.RED}{Colors.BOLD}",
    }

    ICONS = {
        logging.DEBUG: LogIcons.DEBUG,
        logging.INFO: LogIcons.INFO,
        logging.WARNING: LogIcons.WARNING,
        logging.ERROR: LogIcons.ERROR,
        logging.CRITICAL: LogIcons.FAIL,
    }

    def __init__(self):
        super().__init__("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        icon = self.ICONS.get(record.levelno, "")
        msg = super().format(record)
        return f"  {color}{icon}{Colors.RESET} {msg}"


# ─── Logger ──────────────────────────────────────────────────────────────────


class Logger:
    """Logger singleton com arquivo e console."""

    _instance: Optional["Logger"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = logging.getLogger("fedora-postinstall")
        self.logger.setLevel(logging.DEBUG)

        # Log file
        log_file = Path.home() / "fedora-postinstall.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        self.logger.addHandler(file_handler)

        # Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColorFormatter())
        self.logger.addHandler(console_handler)

        # Store log file path
        self.log_file = log_file

    # ─── Métodos principais ──────────────────────────────────────────────────

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg)

    def exception(self, msg: str) -> None:
        """Loga uma exceção com stack trace."""
        self.logger.exception(msg)

    # ─── Métodos com ícones ──────────────────────────────────────────────────

    def success(self, msg: str) -> None:
        self.logger.info(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

    def fail(self, msg: str) -> None:
        self.logger.error(f"{Colors.RED}❌ {msg}{Colors.RESET}")

    def warn(self, msg: str) -> None:
        """Alias para warning."""
        self.warning(msg)

    # ─── Métodos de formato ──────────────────────────────────────────────────

    def step_header(self, title: str, step: int, total: int) -> None:
        """Mostra cabeçalho de passo."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌{'─' * 54}┐{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {step}/{total} {title:<50}│{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}└{'─' * 54}┘{Colors.RESET}")

    def section(self, title: str) -> None:
        """Mostra seção."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}─── {title} ───{Colors.RESET}")

    def sub_step(self, msg: str) -> None:
        """Mostra sub-passo."""
        self.info(f"  → {msg}")


# ─── Função global ───────────────────────────────────────────────────────────


def get_logger() -> Logger:
    """Retorna instância do logger."""
    return Logger()
