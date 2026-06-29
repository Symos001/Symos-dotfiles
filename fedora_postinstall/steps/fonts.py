#!/usr/bin/env python3
# =============================================================================
# steps/fonts.py — Instala Nerd Fonts
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class FontInstaller(Step):
    """Instala Nerd Fonts e MS Core Fonts."""

    @property
    def name(self) -> str:
        return "12/26 — Fontes (Nerd Fonts + MS Core)"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # MS Core Fonts
        self._install_ms_core(result)

        # Nerd Fonts
        self._install_nerd_fonts(result)

        # Atualiza cache
        self._update_font_cache(result)

        if result.is_success:
            result.mark_success("Fontes instaladas")
        return result

    def _install_ms_core(self, result: StepResult) -> None:
        self.dnf_install("curl", "cabextract", "xorg-x11-font-utils", "fontconfig")
        try:
            import subprocess

            subprocess.run(
                "sudo rpm -i --force https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm",
                shell=True,
                check=True,
            )
            self.logger.info("MS Core Fonts instaladas")
        except Exception as e:
            result.mark_warning(f"MS Core Fonts falhou: {e}")

    def _install_nerd_fonts(self, result: StepResult) -> None:
        font_dir = Path.home() / ".local" / "share" / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)

        for font in ["FiraCode", "JetBrainsMono"]:
            dest = font_dir / font
            if (dest / f"{font}NerdFont-Regular.ttf").exists():
                self.logger.info(f"{font} já instalado")
                continue

            self.logger.info(f"Baixando {font}...")
            zip_file = Path(f"/tmp/{font}.zip")
            try:
                self.run_command(
                    [
                        "curl",
                        "-fLo",
                        str(zip_file),
                        f"https://github.com/ryanoasis/nerd-fonts/releases/latest/download/{font}.zip",
                    ]
                )
                dest.mkdir(exist_ok=True)
                self.run_command(["unzip", "-q", str(zip_file), "-d", str(dest)])
                zip_file.unlink()
                self.logger.info(f"{font} Nerd Font instalada")
            except Exception as e:
                result.mark_warning(f"{font} falhou: {e}")

    def _update_font_cache(self, result: StepResult) -> None:
        try:
            self.run_command(["fc-cache", "-fv"], check=False)
            self.logger.info("Cache de fontes atualizado")
        except Exception as e:
            result.mark_warning(f"fc-cache falhou: {e}")
