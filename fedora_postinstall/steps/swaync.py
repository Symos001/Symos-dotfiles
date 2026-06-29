#!/usr/bin/env python3
# =============================================================================
# steps/swaync.py — Configura SwayNC
# =============================================================================

import json
from pathlib import Path

from .base import Step, StepResult


class SwayNCConfig(Step):
    """Configura Sway Notification Center."""

    @property
    def name(self) -> str:
        return "20/26 — Configuração SwayNC"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        swaync_dir = Path.home() / ".config" / "swaync"
        swaync_dir.mkdir(parents=True, exist_ok=True)

        # config.json
        self._write_config(swaync_dir, result)

        # style.css
        self._write_style(swaync_dir, result)

        if result.is_success:
            result.mark_success("SwayNC configurado")
        return result

    def _write_config(self, path: Path, result: StepResult) -> None:
        config = {
            "$schema": "/etc/xdg/swaync/config.json",
            "positionX": "right",
            "positionY": "top",
            "layer": "overlay",
            "control-center-layer": "overlay",
            "layer-shell": True,
            "cssPriority": "application",
            "control-center-margin-top": 8,
            "control-center-margin-bottom": 8,
            "control-center-margin-right": 8,
            "control-center-margin-left": 8,
            "notification-window-width": 380,
            "control-center-width": 420,
            "control-center-height": 600,
            "keyboard-shortcuts": True,
            "image-visibility": "when-available",
            "hide-on-clear": False,
            "hide-on-action": True,
            "script-fail-notify": True,
            "widgets": ["title", "dnd", "mpris", "notifications"],
            "widget-config": {
                "title": {
                    "text": "Notificações",
                    "clear-all-button": True,
                    "button-text": "Limpar todas",
                },
                "dnd": {"text": "Não Perturbe"},
                "mpris": {"image-size": 64, "image-radius": 8},
                "notifications": {
                    "icon-size": 32,
                    "icon-theme": "Papirus",
                    "max-visible-notifications": 8,
                },
            },
        }

        dest = path / "config.json"
        if self.write_file(dest, json.dumps(config, indent=4)):
            self.logger.info("swaync/config.json gerado")
        else:
            result.mark_warning("Falha ao gerar swaync/config.json")

    def _write_style(self, path: Path, result: StepResult) -> None:
        content = """/* ============================================================================
   SwayNC — Tema Terafox/Nightfox (Menos Translúcido)
   ============================================================================ */

.control-center {
    background-color: rgba(22, 24, 33, 0.90);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    padding: 16px;
    margin: 8px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.notification-row {
    padding: 4px 0;
}

.notification {
    background-color: rgba(32, 35, 48, 0.85);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 12px 16px;
    margin: 4px 0;
    transition: all 0.15s ease;
}

.notification:hover {
    background-color: rgba(45, 49, 66, 0.92);
    border-color: rgba(113, 156, 214, 0.2);
}

.notification-header .app-name {
    font-weight: 600;
    color: #719cd6;
    font-size: 14px;
}

.notification-header .time {
    color: #8a93a3;
    font-size: 12px;
}

.notification-body {
    color: #c5cdd9;
    font-size: 13px;
    line-height: 1.5;
}

.notification-actions {
    margin-top: 8px;
    gap: 6px;
}

.notification-actions button {
    background-color: rgba(45, 49, 66, 0.92);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 6px 14px;
    color: #c5cdd9;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.12s ease;
}

.notification-actions button:hover {
    background-color: #719cd6;
    color: #1f2729;
    border-color: #719cd6;
}

.notification-icon {
    margin-right: 12px;
    border-radius: 8px;
}

.close-button {
    background: transparent;
    border: none;
    color: #8a93a3;
    font-size: 16px;
    padding: 0 4px;
    transition: all 0.12s ease;
}

.close-button:hover {
    color: #e85c51;
    transform: scale(1.2);
}

.widget-title {
    color: #c5cdd9;
    font-size: 18px;
    font-weight: 700;
    padding: 8px 0 12px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 12px;
}

.widget-title button {
    background-color: rgba(45, 49, 66, 0.92);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 4px 12px;
    color: #8a93a3;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.12s ease;
}

.widget-title button:hover {
    background-color: #e85c51;
    color: #1f2729;
    border-color: #e85c51;
}

.widget-dnd {
    padding: 8px 0;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.widget-dnd > label {
    color: #c5cdd9;
    font-size: 14px;
    font-weight: 500;
}

.widget-dnd switch {
    background-color: rgba(45, 49, 66, 0.92);
    border-radius: 20px;
    min-width: 44px;
    min-height: 24px;
}

.widget-dnd switch:checked {
    background-color: #719cd6;
}

.widget-dnd switch slider {
    background-color: #c5cdd9;
    border-radius: 50%;
    min-width: 20px;
    min-height: 20px;
}

.widget-mpris {
    background-color: rgba(32, 35, 48, 0.85);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 12px 16px;
    margin-bottom: 12px;
}

.widget-mpris .widget-mpris-title {
    color: #c5cdd9;
    font-weight: 600;
    font-size: 14px;
}

.widget-mpris .widget-mpris-artist {
    color: #8a93a3;
    font-size: 12px;
}

.widget-mpris .widget-mpris-player {
    color: #719cd6;
    font-size: 11px;
}

.widget-mpris image {
    border-radius: 8px;
}

scrollbar {
    background: transparent;
    border-radius: 8px;
}

scrollbar slider {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    min-width: 6px;
    min-height: 40px;
}

scrollbar slider:hover {
    background: rgba(255, 255, 255, 0.15);
}
"""

        dest = path / "style.css"
        if self.write_file(dest, content):
            self.logger.info("swaync/style.css gerado")
        else:
            result.mark_warning("Falha ao gerar swaync/style.css")
