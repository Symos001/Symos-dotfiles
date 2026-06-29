#!/usr/bin/env python3
# =============================================================================
# steps/hyprland.py — Instala Hyprland + SDDM
# =============================================================================

from pathlib import Path

from config import HYPR_PACKAGES

from .base import Step, StepResult


class HyprlandSetup(Step):
    """Instala Hyprland, SDDM e pacotes relacionados."""

    @property
    def name(self) -> str:
        return "13/26 — Hyprland + SDDM"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Pacotes Hyprland
        self._install_hypr_packages(result)

        # Hyprshot
        self._install_hyprshot(result)

        # SDDM
        self._setup_sddm(result)

        if result.is_success:
            result.mark_success("Hyprland instalado")
        return result

    def _install_hypr_packages(self, result: StepResult) -> None:
        self.logger.info("Instalando pacotes Hyprland...")
        succeeded, failed = self.dnf_install_resilient(*HYPR_PACKAGES)

        if failed:
            result.mark_warning(f"Pacotes Hyprland indisponíveis: {', '.join(failed)}")

        self.logger.info(f"{len(succeeded)}/{len(HYPR_PACKAGES)} pacotes instalados")

    def _install_hyprshot(self, result: StepResult) -> None:
        if self.command_exists("hyprshot"):
            self.logger.info("hyprshot já instalado")
            return

        self.logger.info("Instalando hyprshot...")
        try:
            self.run_command(
                [
                    "curl",
                    "-fLo",
                    "/tmp/hyprshot",
                    "https://raw.githubusercontent.com/Gustash/hyprshot/main/hyprshot",
                ]
            )
            self.run_command(
                [
                    "sudo",
                    "install",
                    "-m",
                    "755",
                    "/tmp/hyprshot",
                    "/usr/local/bin/hyprshot",
                ]
            )
            self.logger.info("hyprshot instalado")
        except Exception as e:
            result.mark_warning(f"hyprshot falhou: {e}")

    def _setup_sddm(self, result: StepResult) -> None:
        self.dnf_install("sddm", "sddm-themes")

        try:
            self.run_command(["sudo", "systemctl", "disable", "gdm"], check=False)
            self.run_command(["sudo", "systemctl", "enable", "sddm"])
            self.logger.info("SDDM habilitado (GDM desativado)")
        except Exception as e:
            result.mark_warning(f"SDDM falhou: {e}")
