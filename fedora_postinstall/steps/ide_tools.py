#!/usr/bin/env python3
# =============================================================================
# steps/ides_tools.py — Instala IDEs e apps
# =============================================================================

import shutil
from pathlib import Path

from .base import Step, StepResult


class IdeToolsInstaller(Step):
    """Instala Google Chrome, ZED, VSCodium, Neovim, IntelliJ, Rider."""

    @property
    def name(self) -> str:
        return "11/26 — IDEs e ferramentas"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Google Chrome
        self._install_chrome(result)

        # Flatpak apps
        self._install_flatpak_apps(result)

        # ZED
        self._install_zed(result)

        # VSCodium
        self.dnf_install("vscodium")

        # Neovim + LazyVim
        self._install_neovim(result)

        # Snap apps (IntelliJ, Rider)
        self._install_snap_apps(result)

        if result.is_success:
            result.mark_success("IDEs e apps instalados")
        return result

    def _install_chrome(self, result: StepResult) -> None:
        if self.command_exists("google-chrome"):
            self.logger.info("Google Chrome já instalado")
            return

        self.logger.info("Instalando Google Chrome...")
        try:
            self.run_shell(
                "sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm"
            )
            self.logger.info("Google Chrome instalado")
        except Exception as e:
            result.mark_warning(f"Chrome falhou: {e}")

    def _install_flatpak_apps(self, result: StepResult) -> None:
        apps = [
            "org.onlyoffice.desktopeditors",
            "md.obsidian.Obsidian",
            "org.mozilla.Thunderbird",
            "org.inkscape.Inkscape",
            "org.gimp.GIMP",
            "com.discordapp.Discord",
            "com.spotify.Client",
            "io.dbeaver.DBeaverCommunity",
            "com.usebruno.Bruno",
            "app.drey.Warp",
        ]

        self.logger.info("Instalando apps via Flatpak...")
        for app in apps:
            if self.flatpak_install(app):
                self.logger.info(f"{app} instalado")
            else:
                result.mark_warning(f"{app} falhou")

    def _install_zed(self, result: StepResult) -> None:
        if self.command_exists("zed"):
            self.logger.info("ZED já instalado")
            return

        self.logger.info("Instalando ZED...")
        try:
            self.run_command(["sudo", "dnf", "copr", "enable", "-y", "eddy/zed"])
            self.dnf_install("zed")
            self.logger.info("ZED instalado")
        except Exception as e:
            result.mark_warning(f"ZED falhou: {e}")

    def _install_neovim(self, result: StepResult) -> None:
        self.logger.info("Instalando Neovim...")
        self.dnf_install("neovim")

        nvim_config = Path.home() / ".config" / "nvim"
        if not nvim_config.exists():
            self.logger.info("Clonando LazyVim...")
            try:
                self.run_command(
                    [
                        "git",
                        "clone",
                        "https://github.com/LazyVim/starter",
                        str(nvim_config),
                    ]
                )
                shutil.rmtree(nvim_config / ".git", ignore_errors=True)
                self.logger.info("LazyVim instalado")
            except Exception as e:
                result.mark_warning(f"LazyVim falhou: {e}")

    def _install_snap_apps(self, result: StepResult) -> None:
        # Instala snapd se não existir
        if not self.command_exists("snap"):
            self.logger.info("Instalando snapd...")
            self.dnf_install("snapd")
            try:
                self.run_command(
                    ["sudo", "systemctl", "enable", "--now", "snapd.socket"]
                )
                self.run_command(
                    ["sudo", "ln", "-s", "/var/lib/snapd/snap", "/snap"], check=False
                )
                self.logger.info("Snapd instalado")
                self.logger.warning(
                    "snapd recém-instalado: pode ser necessário relogar para instalar snaps"
                )
            except Exception as e:
                result.mark_warning(f"Snapd falhou: {e}")
                return

        # IntelliJ IDEA
        self.logger.info("Instalando IntelliJ IDEA...")
        if self.snap_install("intellij-idea", classic=True):
            self.logger.info("IntelliJ IDEA instalado")
        else:
            result.mark_warning("IntelliJ IDEA falhou (pode precisar relogar)")

        # Rider
        self.logger.info("Instalando Rider...")
        if self.snap_install("rider", classic=True):
            self.logger.info("Rider instalado")
        else:
            result.mark_warning("Rider falhou (pode precisar relogar)")
