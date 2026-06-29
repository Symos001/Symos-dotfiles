#!/usr/bin/env python3
# =============================================================================
# steps/base.py — Classe base para todos os steps
# =============================================================================

import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, List, Optional

from config import Config
from logger import get_logger

logger = get_logger()
config = Config()


class StepStatus(Enum):
    """Status de execução de um step."""

    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    WARNING = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class StepResult:
    """Resultado da execução de um step."""

    name: str
    status: StepStatus = StepStatus.PENDING
    message: str = ""
    errors: List[str] = field(default_factory=list)

    def mark_success(self, msg: str = "") -> None:
        self.status = StepStatus.SUCCESS
        self.message = msg
        logger.success(msg or "Concluído com sucesso")

    def mark_warning(self, msg: str) -> None:
        self.status = StepStatus.WARNING
        self.errors.append(msg)
        logger.warning(msg)

    def mark_failed(self, msg: str) -> None:
        self.status = StepStatus.FAILED
        self.errors.append(msg)
        logger.fail(msg)

    def mark_skipped(self, msg: str = "") -> None:
        self.status = StepStatus.SKIPPED
        self.message = msg
        logger.info(f"⊘ {msg or 'Pulado'}")

    @property
    def is_success(self) -> bool:
        return self.status in (
            StepStatus.SUCCESS,
            StepStatus.WARNING,
            StepStatus.SKIPPED,
        )


class Step(ABC):
    """Classe base para todos os steps de instalação."""

    def __init__(self, step_number: int, total_steps: int):
        self.step_number = step_number
        self.total_steps = total_steps
        self.result: Optional[StepResult] = None
        self.config = config
        self.logger = logger

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do step."""
        pass

    @abstractmethod
    def execute(self) -> StepResult:
        """Executa o step."""
        pass

    def run(self) -> StepResult:
        """Executa o step com logging."""
        self.logger.step_header(self.name, self.step_number, self.total_steps)
        self.result = StepResult(name=self.name)

        try:
            # Executa e guarda o resultado
            result = self.execute()
            # Se o execute retornou um StepResult, usa ele
            if isinstance(result, StepResult):
                self.result = result
            # Se não, verifica se o resultado foi definido internamente
            elif self.result.status == StepStatus.PENDING:
                self.result.mark_success()
        except Exception as e:
            self.result.mark_failed(f"Erro inesperado: {e}")
            # Usa logger.error em vez de exception() para evitar erro
            self.logger.error(f"Erro em {self.name}: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

        return self.result

    # ─── Métodos auxiliares ──────────────────────────────────────────────────

    def run_command(
        self, cmd: list[str], check: bool = True, **kwargs
    ) -> subprocess.CompletedProcess:
        """Executa um comando."""
        self.logger.debug(f"Executando: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, check=check, capture_output=True, text=True, **kwargs
            )
            if result.stdout:
                self.logger.debug(result.stdout.strip())
            if result.stderr:
                self.logger.debug(result.stderr.strip())
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"Comando falhou: {' '.join(cmd)}\n{e.stderr}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def run_shell(self, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        """Executa um comando shell."""
        return self.run_command(["bash", "-c", cmd], check=check)

    def dnf_install(
        self,
        *packages: str,
        extra_flags: Optional[list[str]] = None,
        skip_unavailable: bool = False,
    ) -> bool:
        """
        Instala pacotes via DNF (compatível com Fedora 44).

        Args:
            *packages: Pacotes para instalar
            extra_flags: Flags adicionais para o DNF
            skip_unavailable: Se True, ignora pacotes indisponíveis
        """
        flags = extra_flags or []
        if skip_unavailable:
            flags.append("--skip-unavailable")

        # Remove pacotes conflitantes se necessário
        if "nodejs" in packages:
            self.run_command(
                ["sudo", "dnf", "remove", "-y", "nodejs22-bin", "nodejs22-npm-bin"],
                check=False,
            )

        try:
            cmd = ["sudo", "dnf", "install", "-y", *flags, *packages]
            self.run_command(cmd)
            return True
        except Exception as e:
            self.logger.warning(f"Falha ao instalar {', '.join(packages)}: {e}")
            return False

    def dnf_install_resilient(self, *packages: str) -> tuple[list[str], list[str]]:
        """Instala pacotes com fallback individual."""
        try:
            self.dnf_install(*packages)
            return list(packages), []
        except:
            succeeded, failed = [], []
            for pkg in packages:
                try:
                    self.dnf_install(pkg)
                    succeeded.append(pkg)
                except:
                    failed.append(pkg)
            return succeeded, failed

    def flatpak_install(self, *app_ids: str) -> bool:
        """Instala apps via Flatpak."""
        try:
            self.run_command(["flatpak", "install", "-y", "flathub", *app_ids])
            return True
        except Exception as e:
            self.logger.warning(f"Falha ao instalar {', '.join(app_ids)}: {e}")
            return False

    def snap_install(self, *packages: str, classic: bool = False) -> bool:
        """Instala pacotes via Snap."""
        cmd = ["sudo", "snap", "install"]
        if classic:
            cmd.append("--classic")
        try:
            self.run_command([*cmd, *packages])
            return True
        except Exception as e:
            self.logger.warning(f"Falha ao instalar {', '.join(packages)}: {e}")
            return False

    def write_file(
        self, path: Path, content: str, mode: str = "644", as_root: bool = False
    ) -> bool:
        """Escreve conteúdo em um arquivo."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if as_root:
                tmp = Path(f"/tmp/_zennit_{path.name}.tmp")
                tmp.write_text(content, encoding="utf-8")
                self.run_command(
                    ["sudo", "install", "-D", "-m", mode, str(tmp), str(path)]
                )
                tmp.unlink(missing_ok=True)
            else:
                path.write_text(content, encoding="utf-8")
                path.chmod(int(mode, 8))
            return True
        except Exception as e:
            self.logger.error(f"Erro ao escrever {path}: {e}")
            return False

    def command_exists(self, name: str) -> bool:
        """Verifica se um comando existe."""
        return shutil.which(name) is not None

    def path_exists(self, path: Path) -> bool:
        """Verifica se um caminho existe."""
        return path.exists()

    def get_user_home(self) -> Path:
        """Retorna o home do usuário."""
        return Path.home()
