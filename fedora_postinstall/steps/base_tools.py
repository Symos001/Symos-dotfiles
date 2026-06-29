#!/usr/bin/env python3
# =============================================================================
# steps/base_tools.py — Ferramentas base
# =============================================================================

from pathlib import Path

from config import BASE_PACKAGES, KDE_APPS

from .base import Step, StepResult


class BaseToolsInstaller(Step):
    """Instala ferramentas base, ZSH, Git, serviços."""

    @property
    def name(self) -> str:
        return "4/26 — Ferramentas base"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Instala pacotes
        self._install_packages(result)

        # Configura ZSH
        self._setup_zsh(result)

        # Instala Starship
        self._install_starship(result)

        # Habilita serviços
        self._enable_services(result)

        if result.is_success:
            result.mark_success("Ferramentas base instaladas")
        return result

    def _install_packages(self, result: StepResult) -> None:
        self.logger.info("Instalando pacotes base...")

        # Pacotes principais
        all_packages = BASE_PACKAGES + KDE_APPS
        succeeded, failed = self.dnf_install_resilient(*all_packages)

        if failed:
            result.mark_warning(f"Pacotes indisponíveis: {', '.join(failed)}")

        self.logger.info(f"{len(succeeded)}/{len(all_packages)} pacotes instalados")

    def _setup_zsh(self, result: StepResult) -> None:
        if not self.command_exists("zsh"):
            result.mark_warning("ZSH não encontrado")
            return

        self.logger.info("Configurando ZSH como shell padrão...")
        try:
            self.run_command(["sudo", "chsh", "-s", "/bin/zsh", self.config.user])
            self.logger.info("ZSH definido como padrão")
        except Exception as e:
            result.mark_warning(f"Falha ao definir ZSH: {e}")

    def _install_starship(self, result: StepResult) -> None:
        if self.command_exists("starship"):
            self.logger.info("Starship já instalado")
            return

        self.logger.info("Instalando Starship...")
        try:
            import subprocess

            subprocess.run(
                "curl -sS https://starship.rs/install.sh | sh -s -- --yes",
                shell=True,
                check=True,
            )
            self.logger.info("Starship instalado")
        except Exception as e:
            result.mark_warning(f"Starship falhou: {e}")

    def _enable_services(self, result: StepResult) -> None:
        for service in ("earlyoom", "irqbalance"):
            try:
                self.run_command(["sudo", "systemctl", "enable", "--now", service])
                self.logger.info(f"{service} ativado")
            except Exception as e:
                result.mark_warning(f"Falha ao ativar {service}: {e}")
