#!/usr/bin/env python3
# =============================================================================
# steps/waybar.py — Configura Waybar
# =============================================================================

import json
from pathlib import Path

from .base import Step, StepResult


class WaybarConfig(Step):
    """Configura Waybar (config.jsonc e style.css)."""

    @property
    def name(self) -> str:
        return "17/26 — Configuração Waybar"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        waybar_dir = Path.home() / ".config" / "waybar"
        waybar_dir.mkdir(parents=True, exist_ok=True)

        # config.jsonc
        self._write_config(waybar_dir, result)

        # style.css
        self._write_style(waybar_dir, result)

        if result.is_success:
            result.mark_success("Waybar configurado")
        return result

    def _write_config(self, path: Path, result: StepResult) -> None:
        config = {
            "layer": "top",
            "position": "top",
            "height": 34,
            "spacing": 4,
            "modules-left": ["hyprland/workspaces"],
            "modules-center": ["window"],
            "modules-right": [
                "custom/separator",
                "custom/notifications",
                "pulseaudio",
                "network",
                "bluetooth",
                "cpu",
                "memory",
                "temperature",
                "battery",
                "clock",
                "tray",
                "custom/power",
            ],
            "hyprland/workspaces": {
                "format": "{icon}",
                "on-click": "activate",
                "format-icons": {"active": "●", "default": "○", "urgent": "◆"},
                "sort-by-number": True,
            },
            "clock": {
                "format": "{:%H:%M  —  %d/%m/%Y}",
                "tooltip-format": "<big>{:%A, %d de %B de %Y}</big>\\n<tt><small>{calendar}</small></tt>",
                "interval": 10,
            },
            "cpu": {"format": " {usage}%", "tooltip": True, "interval": 2},
            "memory": {
                "format": " {used:.1f}G/{total:.1f}G",
                "tooltip": True,
                "interval": 5,
            },
            "temperature": {
                "critical-threshold": 80,
                "format": " {temperatureC}°C",
                "format-critical": " {temperatureC}°C",
                "interval": 5,
            },
            "pulseaudio": {
                "format": "{icon} {volume}%",
                "format-muted": "🔇 {volume}%",
                "format-icons": {"default": ["🔈", "🔉", "🔊"]},
                "on-click": "pavucontrol",
                "scroll-step": 5,
            },
            "network": {
                "format-wifi": " {essid} ({signalStrength}%)",
                "format-ethernet": " {ipaddr}/{cidr}",
                "format-disconnected": " Desconectado",
                "interval": 5,
            },
            "bluetooth": {
                "format": " {status}",
                "format-disabled": " Desativado",
                "format-off": " Desligado",
                "on-click": "blueman-manager",
            },
            "battery": {
                "states": {"warning": 30, "critical": 15},
                "format": "{icon} {capacity}%",
                "format-charging": "⚡ {capacity}%",
                "format-plugged": "🔌 {capacity}%",
                "format-icons": ["", "", "", "", ""],
                "interval": 30,
            },
            "tray": {"icon-size": 16, "spacing": 8},
            "custom/separator": {"format": "│", "interval": "once"},
            "custom/notifications": {
                "format": "🔔 {}",
                "tooltip": True,
                "return-type": "json",
                "exec": "~/.local/bin/waybar-notifications",
                "interval": 5,
            },
            "custom/power": {
                "format": "⏻",
                "tooltip": True,
                "on-click": "~/.local/bin/powermenu",
                "interval": "once",
            },
        }

        dest = path / "config.jsonc"
        if self.write_file(dest, json.dumps(config, indent=4)):
            self.logger.info("waybar/config.jsonc gerado")
        else:
            result.mark_warning("Falha ao gerar waybar/config.jsonc")

    def _write_style(self, path: Path, result: StepResult) -> None:
        content = """/* ============================================================================
   Waybar — Tema Terafox/Nightfox (Menos Translúcido + Blur)
   ============================================================================ */

* {
    font-family: "JetBrainsMono Nerd Font", "FiraCode Nerd Font", sans-serif;
    font-size: 13px;
    min-height: 0;
}

window#waybar {
    background: rgba(31, 39, 41, 0.78);
    color: #e6eaf2;
    border-radius: 14px;
    border: 1px solid rgba(58, 64, 70, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin: 6px 8px;
    padding: 4px 8px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

#workspaces,
#clock,
#tray,
#pulseaudio,
#network,
#bluetooth,
#battery,
#custom-power,
#custom-notifications,
#cpu,
#memory,
#temperature,
#backlight {
    background: rgba(47, 50, 57, 0.65);
    border-radius: 10px;
    padding: 0 12px;
    margin: 4px 3px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    transition: all 0.15s ease;
}

#workspaces {
    background: rgba(47, 50, 57, 0.65);
    border-radius: 10px;
    margin: 4px 4px 4px 6px;
    padding: 0 6px;
}

#workspaces button {
    color: #71839b;
    padding: 0 10px;
    border-radius: 6px;
    margin: 2px 2px;
    transition: all 0.12s ease;
}

#workspaces button.active {
    color: #1f2729;
    background: #5a93aa;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(90, 147, 170, 0.3);
}

#workspaces button:hover {
    background: rgba(90, 147, 170, 0.25);
    color: #e6eaf2;
}

#window {
    color: #8ebaa9;
    padding: 0 14px;
    font-weight: 500;
}

#clock {
    color: #e6eaf2;
    padding: 0 16px;
    font-weight: 600;
    font-size: 14px;
}

#clock:hover {
    color: #8ebaa9;
}

#pulseaudio {
    color: #8ebaa9;
}

#pulseaudio.muted {
    color: #71839b;
}

#network {
    color: #5a93aa;
}

#network.disconnected {
    color: #c46d72;
}

#bluetooth {
    color: #5a93aa;
}

#bluetooth.disabled,
#bluetooth.off {
    color: #71839b;
}

#battery {
    color: #d6b87b;
}

#battery.warning {
    color: #d6975b;
    animation: blink-warning 1s infinite;
}

#battery.critical {
    color: #c46d72;
    animation: blink-critical 0.5s infinite;
}

#battery.charging {
    color: #8ebaa9;
}

#cpu {
    color: #a093e6;
}

#memory {
    color: #63cdcf;
}

#temperature {
    color: #d6b87b;
}

#temperature.critical {
    color: #c46d72;
}

#custom-power {
    color: #c46d72;
    margin-right: 6px;
    font-size: 16px;
    font-weight: 600;
    padding: 0 14px;
}

#custom-power:hover {
    background: #c46d72;
    color: #1f2729;
    border-color: #c46d72;
}

#custom-notifications {
    color: #63cdcf;
}

#custom-notifications.has-notifications {
    color: #d6b87b;
}

#tray {
    margin-right: 4px;
    padding: 0 8px;
}

#tray > .needs-attention {
    background-color: rgba(196, 109, 114, 0.15);
    border-radius: 6px;
}

tooltip {
    background: rgba(31, 39, 41, 0.92);
    border: 1px solid rgba(90, 147, 170, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    backdrop-filter: blur(8px);
}

tooltip label {
    color: #e6eaf2;
    font-size: 12px;
}

@keyframes blink-warning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

@keyframes blink-critical {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}
"""

        dest = path / "style.css"
        if self.write_file(dest, content):
            self.logger.info("waybar/style.css gerado")
        else:
            result.mark_warning("Falha ao gerar waybar/style.css")
