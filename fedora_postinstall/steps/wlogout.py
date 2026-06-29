#!/usr/bin/env python3
# =============================================================================
# steps/wlogout.py — Configura Wlogout
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class WlogoutConfig(Step):
    """Configura Wlogout (layout e style.css)."""

    @property
    def name(self) -> str:
        return "19/26 — Configuração Wlogout"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        wlogout_dir = Path.home() / ".config" / "wlogout"
        wlogout_dir.mkdir(parents=True, exist_ok=True)

        # Layout
        self._write_layout(wlogout_dir, result)

        # Style
        self._write_style(wlogout_dir, result)

        if result.is_success:
            result.mark_success("Wlogout configurado")
        return result

    def _write_layout(self, path: Path, result: StepResult) -> None:
        layout = """{
    "layout": [
        {
            "label": "⏻",
            "action": "systemctl poweroff",
            "keybind": "e"
        },
        {
            "label": "⟳",
            "action": "systemctl reboot",
            "keybind": "r"
        },
        {
            "label": "⏾",
            "action": "systemctl suspend",
            "keybind": "s"
        },
        {
            "label": "⇥",
            "action": "hyprctl dispatch exit",
            "keybind": "l"
        },
        {
            "label": "⇶",
            "action": "systemctl hibernate",
            "keybind": "h"
        },
        {
            "label": "🔒",
            "action": "hyprlock",
            "keybind": "b"
        }
    ]
}"""

        dest = path / "layout"
        if self.write_file(dest, layout):
            self.logger.info("wlogout/layout gerado")
        else:
            result.mark_warning("Falha ao gerar wlogout/layout")

    def _write_style(self, path: Path, result: StepResult) -> None:
        content = """/* ============================================================================
   Wlogout — Tema Terafox/Nightfox (Menos Translúcido)
   ============================================================================ */

window {
    background-color: rgba(22, 24, 33, 0.88);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 24px 32px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

#grid {
    margin: 20px 0;
    gap: 16px;
}

button {
    background-color: rgba(32, 35, 48, 0.85);
    border-radius: 16px;
    border: 2px solid transparent;
    padding: 20px 24px;
    min-width: 80px;
    min-height: 80px;
    transition: all 0.15s ease;
    font-size: 32px;
    color: #c5cdd9;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

button:hover {
    background-color: rgba(45, 49, 66, 0.92);
    border-color: #719cd6;
    transform: scale(1.05);
    box-shadow: 0 8px 24px rgba(113, 156, 214, 0.2);
}

button:active {
    transform: scale(0.95);
}

button label {
    font-size: 14px;
    font-weight: 500;
    color: #c5cdd9;
    margin-top: 8px;
    font-family: "JetBrainsMono Nerd Font", sans-serif;
}

button:hover label {
    color: #719cd6;
}

button#shutdown {
    color: #e85c51;
}

button#shutdown:hover {
    border-color: #e85c51;
    background-color: rgba(232, 92, 81, 0.15);
}

button#reboot {
    color: #d6b87b;
}

button#reboot:hover {
    border-color: #d6b87b;
    background-color: rgba(214, 184, 123, 0.15);
}

button#suspend {
    color: #63cdcf;
}

button#suspend:hover {
    border-color: #63cdcf;
    background-color: rgba(99, 205, 207, 0.15);
}

button#logout {
    color: #a093e6;
}

button#logout:hover {
    border-color: #a093e6;
    background-color: rgba(160, 147, 230, 0.15);
}

button#hibernate {
    color: #719cd6;
}

button#hibernate:hover {
    border-color: #719cd6;
    background-color: rgba(113, 156, 214, 0.15);
}

button#lock {
    color: #7cb98a;
}

button#lock:hover {
    border-color: #7cb98a;
    background-color: rgba(124, 185, 138, 0.15);
}

tooltip {
    background-color: rgba(22, 24, 33, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 8px 14px;
    backdrop-filter: blur(8px);
}

tooltip label {
    color: #c5cdd9;
    font-size: 13px;
}
"""

        dest = path / "style.css"
        if self.write_file(dest, content):
            self.logger.info("wlogout/style.css gerado")
        else:
            result.mark_warning("Falha ao gerar wlogout/style.css")
