#!/usr/bin/env python3
# =============================================================================
# steps/hyprpaper.py — Configura Hyprpaper
# =============================================================================

from pathlib import Path

from config import WALLPAPER_DIR

from .base import Step, StepResult


class HyprpaperConfig(Step):
    """Configura hyprpaper.conf."""

    @property
    def name(self) -> str:
        return "16/26 — Configuração Hyprpaper"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Cria diretório de wallpapers
        WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

        # Gera wallpaper placeholder
        self._create_placeholder_wallpaper()

        content = f"""# =============================================================================
# Hyprpaper — Wallpaper Engine
# Tema: Terafox/Nightfox
# =============================================================================

preload = {WALLPAPER_DIR}/terafox-dark.jpg
preload = {WALLPAPER_DIR}/galaxiaWallpaper.jpg

wallpaper = HDMI-A-1,{WALLPAPER_DIR}/galaxiaWallpaper.jpg
wallpaper = eDP-1,{WALLPAPER_DIR}/terafox-dark.jpg

splash = false
ipc = on
"""

        dest = Path.home() / ".config" / "hypr" / "hyprpaper.conf"
        if self.write_file(dest, content):
            self.logger.info(f"{dest} gerado")
            result.mark_success("hyprpaper.conf configurado")
        else:
            result.mark_failed("Falha ao gerar hyprpaper.conf")

        return result

    def _create_placeholder_wallpaper(self) -> None:
        """Cria um wallpaper placeholder simples."""
        wallpaper = WALLPAPER_DIR / "terafox-dark.jpg"
        if not wallpaper.exists():
            # Tenta baixar um wallpaper
            try:
                self.run_command(
                    [
                        "curl",
                        "-fLo",
                        str(wallpaper),
                        "https://raw.githubusercontent.com/termux-command/termux-wallpapers/main/wallpapers/terafox-dark.jpg",
                    ],
                    check=False,
                )
                self.logger.info("Wallpaper placeholder criado")
            except:
                self.logger.warning("Não foi possível baixar wallpaper placeholder")
