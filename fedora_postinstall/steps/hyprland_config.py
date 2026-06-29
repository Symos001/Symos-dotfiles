#!/usr/bin/env python3
# =============================================================================
# steps/hyprland_config.py — Configura hyprland.conf
# =============================================================================

import textwrap
from pathlib import Path

from config import Config

from .base import Step, StepResult

config = Config()


class HyprlandConfig(Step):
    """Gera hyprland.conf completo."""

    @property
    def name(self) -> str:
        return "14/26 — Configuração Hyprland"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        content = self._generate_hyprland_conf()
        dest = Path.home() / ".config" / "hypr" / "hyprland.conf"

        if self.write_file(dest, content):
            self.logger.info(f"{dest} gerado")
            result.mark_success("hyprland.conf configurado")
        else:
            result.mark_failed("Falha ao gerar hyprland.conf")

        return result

    def _generate_hyprland_conf(self) -> str:
        """Gera o conteúdo do hyprland.conf."""
        monitors = config.monitor_configs

        return f"""# =============================================================================
# Hyprland.conf — Zennit-OS Dev Environment
# Tema: Terafox/Nightfox
# =============================================================================

# ─── MONITORES ──────────────────────────────────────────────────────────────────

{monitors}

# ─── WORKSPACES POR MONITOR ──────────────────────────────────────────────────

# HDMI-A-1 → Workspaces 1–5
workspace = 1, monitor:HDMI-A-1
workspace = 2, monitor:HDMI-A-1
workspace = 3, monitor:HDMI-A-1
workspace = 4, monitor:HDMI-A-1
workspace = 5, monitor:HDMI-A-1

# eDP-1 → Workspaces 6–10
workspace = 6, monitor:eDP-1
workspace = 7, monitor:eDP-1
workspace = 8, monitor:eDP-1
workspace = 9, monitor:eDP-1
workspace = 10, monitor:eDP-1

# ─── AUTOSTART ─────────────────────────────────────────────────────────────────

exec-once = sh -c 'pkill waybar; sleep 0.5; waybar'
exec-once = hyprpaper
exec-once = hypridle
exec-once = sh -c 'pkill swaync; sleep 0.5; swaync'
exec-once = nm-applet --indicator
exec-once = blueman-applet
exec-once = systemctl --user start xdg-desktop-portal-hyprland
exec-once = dbus-update-activation-environment --systemd --all

# ─── VARIÁVEIS DE AMBIENTE ────────────────────────────────────────────────────

env = XCURSOR_SIZE,24
env = HYPRCURSOR_SIZE,24
env = QT_QPA_PLATFORMTHEME,qt5ct
env = GTK_THEME,Adwaita-dark
env = GDK_BACKEND,wayland,x11
env = QT_AUTO_SCREEN_SCALE_FACTOR,1
env = QT_WAYLAND_DISABLE_WINDOWDECORATION,1
env = CLUTTER_BACKEND,wayland
env = SDL_VIDEODRIVER,wayland
env = _JAVA_AWT_WM_NONREPARENTING,1

# ─── LOOK AND FEEL ────────────────────────────────────────────────────────────

general {{
    gaps_in = 5
    gaps_out = 12
    border_size = 2

    col.active_border = rgba(5a93aaee) rgba(8ebaa9ee) 45deg
    col.inactive_border = rgba(2f323988)

    resize_on_border = true
    allow_tearing = false

    layout = dwindle
}}

decoration {{
    rounding = 10

    active_opacity = 1.0
    inactive_opacity = 0.95

    shadow {{
        enabled = true
        range = 15
        render_power = 3
        color = rgba(1f272999)
    }}

    blur {{
        enabled = true
        size = 8
        passes = 3
        vibrancy = 0.17
        brightness = 1.0
        contrast = 1.0
        noise = 0.02
    }}
}}

animations {{
    enabled = yes

    bezier = myBezier, 0.05, 0.9, 0.1, 1.05

    animation = windows, 1, 5, myBezier
    animation = windowsOut, 1, 5, default, popin 80%
    animation = border, 1, 8, default
    animation = borderangle, 1, 8, default
    animation = fade, 1, 5, default
    animation = workspaces, 1, 5, default
}}

dwindle {{
    preserve_split = true
}}

master {{
    new_status = master
}}

misc {{
    force_default_wallpaper = 0
}}

# ─── INPUT ────────────────────────────────────────────────────────────────────

input {{
    kb_layout = br
    follow_mouse = 1
    sensitivity = 0

    touchpad {{
        natural_scroll = true
    }}
}}

# ─── KEYBINDINGS ──────────────────────────────────────────────────────────────

$mainMod = SUPER
$terminal = alacritty
$fileManager = dolphin
$menu = wofi --show drun
$navigator = google-chrome

# Apps
bind = $mainMod, RETURN, exec, $terminal
bind = $mainMod, E, exec, $fileManager
bind = $mainMod, SPACE, exec, $menu
bind = $mainMod, G, exec, $navigator
bind = $mainMod SHIFT, SPACE, exec, wofi --show run

# Controle de janelas
bind = $mainMod, Q, killactive
bind = $mainMod SHIFT, Q, exit
bind = $mainMod, V, togglefloating
bind = $mainMod, F, fullscreen

# Power Menu (Wlogout)
bind = $mainMod, X, exec, ~/.local/bin/powermenu
bind = SHIFT, E, exec, ~/.local/bin/powermenu

# Lock
bind = $mainMod, L, exec, hyprlock

# Notificações (SwayNC)
bind = $mainMod, N, exec, swaync-client -t
bind = $mainMod SHIFT, N, exec, swaync-client -c
bind = $mainMod, D, exec, swaync-client -d

# Screenshots
bind = , Print, exec, ~/.local/bin/screenshot output
bind = $mainMod, Print, exec, ~/.local/bin/screenshot window
bind = SHIFT, Print, exec, ~/.local/bin/screenshot region
bind = CTRL, Print, exec, ~/.local/bin/screenshot region-copy

# Wallpapers
bind = $mainMod, W, exec, ~/.local/bin/wallpaper-switcher --menu
bind = $mainMod SHIFT, W, exec, ~/.local/bin/wallpaper-switcher --random
bind = $mainMod, Right, exec, ~/.local/bin/wallpaper-switcher --next
bind = $mainMod, Left, exec, ~/.local/bin/wallpaper-switcher --prev

# Foco (Vim-style)
bind = $mainMod, left, movefocus, l
bind = $mainMod, right, movefocus, r
bind = $mainMod, up, movefocus, u
bind = $mainMod, down, movefocus, d

bind = $mainMod, h, movefocus, l
bind = $mainMod, j, movefocus, d
bind = $mainMod, k, movefocus, u
bind = $mainMod, l, movefocus, r

# Workspaces
bind = $mainMod, 1, workspace, 1
bind = $mainMod, 2, workspace, 2
bind = $mainMod, 3, workspace, 3
bind = $mainMod, 4, workspace, 4
bind = $mainMod, 5, workspace, 5
bind = $mainMod, 6, workspace, 6
bind = $mainMod, 7, workspace, 7
bind = $mainMod, 8, workspace, 8
bind = $mainMod, 9, workspace, 9
bind = $mainMod, 0, workspace, 10

bind = $mainMod SHIFT, 1, movetoworkspace, 1
bind = $mainMod SHIFT, 2, movetoworkspace, 2
bind = $mainMod SHIFT, 3, movetoworkspace, 3
bind = $mainMod SHIFT, 4, movetoworkspace, 4
bind = $mainMod SHIFT, 5, movetoworkspace, 5
bind = $mainMod SHIFT, 6, movetoworkspace, 6
bind = $mainMod SHIFT, 7, movetoworkspace, 7
bind = $mainMod SHIFT, 8, movetoworkspace, 8
bind = $mainMod SHIFT, 9, movetoworkspace, 9
bind = $mainMod SHIFT, 0, movetoworkspace, 10

# Workspace especial
bind = $mainMod, S, togglespecialworkspace, magic
bind = $mainMod SHIFT, S, movetoworkspace, special:magic

# Recarregar
bind = $mainMod, R, exec, ~/.local/bin/reload-config
bind = $mainMod CTRL, R, exec, ~/.local/bin/reload-all
bind = $mainMod, PERIOD, exec, $terminal -e nvim ~/.config/hypr/hyprland.conf

# Mouse
bindm = $mainMod, mouse:272, movewindow
bindm = $mainMod, mouse:273, resizewindow

# Áudio e Brilho
bindel = , XF86AudioRaiseVolume, exec, wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+
bindel = , XF86AudioLowerVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bindel = , XF86AudioMute, exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
bindel = , XF86MonBrightnessUp, exec, brightnessctl s 10%+
bindel = , XF86MonBrightnessDown, exec, brightnessctl s 10%-

# Mídia
bindel = , XF86AudioPlay, exec, playerctl play-pause
bindel = , XF86AudioPrev, exec, playerctl previous
bindel = , XF86AudioNext, exec, playerctl next

# ─── WINDOW RULES ─────────────────────────────────────────────────────────────

windowrulev2 = float, class:^(org.gnome.Calculator)$
windowrulev2 = float, class:^(pavucontrol)$
windowrulev2 = float, class:^(blueman-manager)$
windowrulev2 = float, class:^(gnome-disks)$
windowrulev2 = float, class:^(gnome-system-monitor)$
windowrulev2 = float, title:^(Picture-in-Picture)$

# Wlogout
windowrulev2 = center, class:^(wlogout)$
windowrulev2 = float, class:^(wlogout)$
windowrulev2 = noborder, class:^(wlogout)$

# SwayNC
windowrulev2 = float, class:^(swaync)$
windowrulev2 = noborder, class:^(swaync)$

# ─── FIM ──────────────────────────────────────────────────────────────────────
"""
