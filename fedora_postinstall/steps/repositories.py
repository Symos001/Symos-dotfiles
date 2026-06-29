#!/usr/bin/env python3
# =============================================================================
# steps/repositories.py — Configura repositórios
# =============================================================================

import subprocess
from pathlib import Path

from .base import Step, StepResult


class RepositorySetup(Step):
    """Configura RPM Fusion, Flathub e COPR."""

    @property
    def name(self) -> str:
        return "2/26 — Repositórios (RPM Fusion + Flathub + COPR)"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # RPM Fusion
        self._setup_rpmfusion(result)

        # Flathub
        self._setup_flathub(result)

        # COPR Hyprland
        self._setup_copr(result)

        if result.is_success:
            result.mark_success("Repositórios configurados")
        return result

    def _setup_rpmfusion(self, result: StepResult) -> None:
        self.logger.info("Instalando RPM Fusion...")
        try:
            fedora_ver = subprocess.run(
                ["rpm", "-E", "%fedora"], capture_output=True, text=True
            ).stdout.strip()

            for variant in ("free", "nonfree"):
                url = f"https://mirrors.rpmfusion.org/{variant}/fedora/rpmfusion-{variant}-release-{fedora_ver}.noarch.rpm"
                self.run_command(["sudo", "dnf", "install", "-y", url])
                self.logger.info(f"RPM Fusion ({variant}) instalado")
        except Exception as e:
            result.mark_warning(f"RPM Fusion pode já estar instalado: {e}")

    def _setup_flathub(self, result: StepResult) -> None:
        self.logger.info("Configurando Flathub...")
        try:
            self.run_command(
                [
                    "flatpak",
                    "remote-add",
                    "--if-not-exists",
                    "flathub",
                    "https://dl.flathub.org/repo/flathub.flatpakrepo",
                ]
            )
            self.logger.info("Flathub configurado")
        except Exception as e:
            result.mark_warning(f"Flathub falhou: {e}")

    def _setup_copr(self, result: StepResult) -> None:
        self.logger.info("Habilitando COPR Hyprland...")
        try:
            self.run_command(
                ["sudo", "dnf", "copr", "enable", "-y", "ashbuk/Hyprland-Fedora"]
            )
            self.logger.info("COPR Hyprland habilitado")
        except Exception as e:
            result.mark_warning(f"COPR Hyprland pode já estar habilitado: {e}")
