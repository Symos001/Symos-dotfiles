#!/usr/bin/env python3
# =============================================================================
# config.py — Configurações globais
# =============================================================================

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# ─── Caminhos ──────────────────────────────────────────────────────────────────

HOME = Path.home()
CONFIG_DIR = HOME / ".config"
LOCAL_BIN = HOME / ".local" / "bin"
PICTURES = HOME / "Pictures"
SCREENSHOTS_DIR = PICTURES / "Screenshots"
WALLPAPER_DIR = PICTURES / "wallpapers"
DOTFILES_DIR = HOME / ".dotfiles"

# ─── URLs ─────────────────────────────────────────────────────────────────────

RPM_FUSION_FREE = (
    "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{}.noarch.rpm"
)
RPM_FUSION_NONFREE = "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{}.noarch.rpm"
NODE_SOURCE = "https://rpm.nodesource.com/setup_20.x"
RUSTUP = "https://sh.rustup.rs"
SDKMAN = "https://get.sdkman.io"
STARSHIP = "https://starship.rs/install.sh"
BUN = "https://bun.sh/install"
DOTFILES_REPO = "https://github.com/Symos001/Symos-dotfiles.git"
NERD_FONTS_BASE = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download"

# ─── Pacotes ──────────────────────────────────────────────────────────────────

BASE_PACKAGES = [
    "htop",
    "btop",
    "bat",
    "eza",
    "fd-find",
    "ripgrep",
    "fzf",
    "zoxide",
    "tmux",
    "ncdu",
    "fastfetch",
    "stow",
    "git",
    "zsh",
    "curl",
    "wget",
    "unzip",
    "jq",
    "make",
    "gcc",
    "gcc-c++",
    "firewalld",
    "rclone",
    "earlyoom",
    "irqbalance",
    "neovim",
    "python3",
    "python3-pip",
    "powertop",
    "dolphin",
    "kate",
    "keepassxc",
    "ark",
    "gwenview",
    "gparted",
]

HYPR_PACKAGES = [
    "hyprland",
    "hyprpaper",
    "hyprlock",
    "hypridle",
    "hyprpicker",
    "waybar",
    "rofi-wayland",
    "xdg-desktop-portal-hyprland",
    "qt5-qtwayland",
    "qt6-qtwayland",
    "polkit-gnome",
    "grim",
    "slurp",
    "wl-clipboard",
    "brightnessctl",
]

KDE_APPS = [
    "dolphin",
    "kate",
    "keepassxc",
    "ark",
    "gwenview",
]

JAVA_PACKAGES = ["java-17-openjdk", "java-21-openjdk"]


# ─── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass
class MonitorConfig:
    name: str
    resolution: str
    refresh: str
    position: str
    scale: int = 1


@dataclass
class ThemeColors:
    bg: str = "rgba(22, 24, 33, 0.88)"
    bg_alt: str = "rgba(32, 35, 48, 0.85)"
    bg_hover: str = "rgba(45, 49, 66, 0.92)"
    fg: str = "#c5cdd9"
    fg_dim: str = "#8a93a3"
    blue: str = "#719cd6"
    purple: str = "#a093e6"
    cyan: str = "#63cdcf"
    green: str = "#7cb98a"
    red: str = "#e85c51"
    yellow: str = "#d6b87b"
    border: str = "rgba(255, 255, 255, 0.06)"


# ─── Configuração Principal ──────────────────────────────────────────────────


class Config:
    """Configuração global do post-install."""

    def __init__(self):
        self.theme = ThemeColors()
        self.monitors = self._get_monitors()
        self.user = HOME.name

    def _get_monitors(self) -> List[MonitorConfig]:
        """Detecta monitores ou usa configuração padrão."""
        # Tenta detectar monitores
        try:
            import subprocess

            result = subprocess.run(
                ["hyprctl", "monitors"], capture_output=True, text=True
            )
            # Parsing simples
            monitors = []
            for line in result.stdout.splitlines():
                if "Monitor" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1].replace("(ID", "")
                        monitors.append(
                            MonitorConfig(
                                name=name,
                                resolution="1366x768",
                                refresh="60",
                                position="0x0",
                                scale=1,
                            )
                        )
            if monitors:
                return monitors
        except:
            pass

        # Fallback: monitores padrão
        return [
            MonitorConfig("HDMI-A-1", "1366x768", "59.79", "0x0"),
            MonitorConfig("eDP-1", "1366x768", "60.06", "1366x0"),
        ]

    @property
    def monitor_configs(self) -> str:
        """Retorna configuração de monitores para hyprland.conf."""
        return "\n".join(
            [
                f"monitor = {m.name},{m.resolution}@{m.refresh},{m.position},{m.scale}"
                for m in self.monitors
            ]
        )
