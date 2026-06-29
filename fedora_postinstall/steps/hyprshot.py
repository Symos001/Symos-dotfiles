#!/usr/bin/env python3
# =============================================================================
# steps/hyprshot.py — Configura Hyprshot
# =============================================================================

from pathlib import Path

from config import SCREENSHOTS_DIR

from .base import Step, StepResult


class HyprshotConfig(Step):
    """Configura hyprshot.conf."""

    @property
    def name(self) -> str:
        return "15/26 — Configuração Hyprshot"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Cria diretório de screenshots
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        content = f"""# =============================================================================
# Hyprshot — Screenshot Tool
# =============================================================================

output_directory = {SCREENSHOTS_DIR}
output_file_template = screenshot_%Y-%m-%d_%H-%M-%S

notify = true
notification_icon = camera-photo
notification_message = Screenshot salvo: {{file}}

mode = output
mode = window
mode = region

freeze = true
delay = 0.5
"""

        dest = Path.home() / ".config" / "hypr" / "hyprshot.conf"
        if self.write_file(dest, content):
            self.logger.info(f"{dest} gerado")
            result.mark_success("hyprshot.conf configurado")
        else:
            result.mark_failed("Falha ao gerar hyprshot.conf")

        return result
