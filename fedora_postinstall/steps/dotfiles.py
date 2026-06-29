#!/usr/bin/env python3
# =============================================================================
# steps/dotfiles.py — Clona e aplica dotfiles
# =============================================================================

import shutil
from datetime import datetime
from pathlib import Path

from config import DOTFILES_DIR, DOTFILES_REPO

from .base import Step, StepResult


class DotfilesSetup(Step):
    """Clona e aplica dotfiles via GNU Stow."""

    @property
    def name(self) -> str:
        return "22/26 — Dotfiles"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Clone/update
        self._clone_dotfiles(result)

        # Stow
        self._stow_dotfiles(result)

        # Tmux plugins
        self._setup_tmux_plugins(result)

        if result.is_success:
            result.mark_success("Dotfiles aplicados")
        return result

    def _clone_dotfiles(self, result: StepResult) -> None:
        if DOTFILES_DIR.exists() and (DOTFILES_DIR / ".git").exists():
            self.logger.info("Atualizando dotfiles...")
            try:
                self.run_command(
                    ["git", "-C", str(DOTFILES_DIR), "pull", "--rebase", "--autostash"]
                )
                self.logger.info("Dotfiles atualizados")
            except Exception as e:
                result.mark_warning(f"Falha ao atualizar dotfiles: {e}")
            return

        self.logger.info("Clonando dotfiles...")
        try:
            self.run_command(
                [
                    "git",
                    "clone",
                    "--recurse-submodules",
                    DOTFILES_REPO,
                    str(DOTFILES_DIR),
                ]
            )
            self.logger.info("Dotfiles clonados")
        except Exception as e:
            result.mark_warning(f"Falha ao clonar dotfiles: {e}")

    def _stow_dotfiles(self, result: StepResult) -> None:
        if not DOTFILES_DIR.exists():
            result.mark_warning("Diretório de dotfiles não encontrado")
            return

        # Verifica se stow está instalado
        if not self.command_exists("stow"):
            self.logger.warning("Stow não encontrado, instalando...")
            self.dnf_install("stow")

        # Backup do .zshrc existente
        zshrc = Path.home() / ".zshrc"
        if zshrc.exists() and not zshrc.is_symlink():
            backup = zshrc.with_suffix(
                f".bak.{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            shutil.move(str(zshrc), str(backup))
            self.logger.info(f".zshrc existente salvo em {backup}")

        self.logger.info("Aplicando dotfiles com Stow...")

        # Lista de pacotes para stow
        stow_packages = []
        for pkg_dir in sorted(DOTFILES_DIR.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
                continue
            stow_packages.append(pkg_dir.name)

        if not stow_packages:
            self.logger.warning("Nenhum pacote para stow encontrado")
            return

        for pkg in stow_packages:
            try:
                self.run_command(
                    ["stow", "--restow", "--target", str(Path.home()), pkg],
                    cwd=DOTFILES_DIR,
                )
                self.logger.info(f"stow: {pkg}")
            except Exception as e:
                result.mark_warning(f"stow: {pkg} falhou: {e}")

    def _setup_tmux_plugins(self, result: StepResult) -> None:
        """Instala Tmux Plugin Manager (TPM)."""
        tpm_dir = Path.home() / ".tmux" / "plugins" / "tpm"

        if tpm_dir.exists():
            self.logger.info("TPM já instalado")
            return

        self.logger.info("Instalando Tmux Plugin Manager...")
        try:
            self.run_command(
                ["git", "clone", "https://github.com/tmux-plugins/tpm", str(tpm_dir)]
            )
            self.logger.info("TPM instalado")

            # Instala plugins automaticamente
            tpm_install = tpm_dir / "bin" / "install_plugins"
            if tpm_install.exists():
                self.run_command([str(tpm_install)])
                self.logger.info("Plugins tmux instalados")
        except Exception as e:
            result.mark_warning(f"TPM falhou: {e}")
