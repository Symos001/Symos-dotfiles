#!/usr/bin/env python3
# =============================================================================
# steps/scripts.py — Cria scripts auxiliares
# =============================================================================

from pathlib import Path

from config import LOCAL_BIN

from .base import Step, StepResult


class ScriptsSetup(Step):
    """Cria scripts auxiliares (powermenu, screenshot, etc)."""

    @property
    def name(self) -> str:
        return "23/26 — Scripts auxiliares"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        LOCAL_BIN.mkdir(parents=True, exist_ok=True)

        scripts = [
            ("powermenu", self._powermenu_script()),
            ("screenshot", self._screenshot_script()),
            ("wallpaper-switcher", self._wallpaper_switcher_script()),
            ("reload-config", self._reload_config_script()),
            ("reload-all", self._reload_all_script()),
            ("waybar-notifications", self._waybar_notifications_script()),
        ]

        for name, content in scripts:
            dest = LOCAL_BIN / name
            if self.write_file(dest, content):
                dest.chmod(0o755)
                self.logger.info(f"{name} criado")
            else:
                result.mark_warning(f"Falha ao criar {name}")

        if result.is_success:
            result.mark_success("Scripts auxiliares criados")
        return result

    def _powermenu_script(self) -> str:
        return """#!/bin/bash
# Menu de power usando Wlogout
pkill wlogout 2>/dev/null
wlogout --protocol layer-shell
"""

    def _screenshot_script(self) -> str:
        return """#!/bin/bash
# Screenshot com Hyprshot + SwayNC

SCREENSHOT_DIR="$HOME/Pictures/Screenshots"
mkdir -p "$SCREENSHOT_DIR"
FILENAME="screenshot_$(date +%Y-%m-%d_%H-%M-%S).png"
FILEPATH="$SCREENSHOT_DIR/$FILENAME"

send_notification() {
    swaync-client -R
    notify-send "📸 Screenshot" "$1" -t 3000 -i camera-photo
}

case "$1" in
    output)
        hyprshot -m output -o "$SCREENSHOT_DIR" -f "$FILENAME"
        send_notification "Screenshot da tela salvo: $FILENAME"
        ;;
    window)
        hyprshot -m window -o "$SCREENSHOT_DIR" -f "$FILENAME"
        send_notification "Screenshot da janela salvo: $FILENAME"
        ;;
    region)
        hyprshot -m region -o "$SCREENSHOT_DIR" -f "$FILENAME"
        send_notification "Screenshot da região salvo: $FILENAME"
        ;;
    region-copy)
        hyprshot -m region -o "$SCREENSHOT_DIR" -f "$FILENAME" -c
        send_notification "Screenshot da região copiado para área de transferência"
        ;;
    output-copy)
        hyprshot -m output -o "$SCREENSHOT_DIR" -f "$FILENAME" -c
        send_notification "Screenshot da tela copiado para área de transferência"
        ;;
    window-copy)
        hyprshot -m window -o "$SCREENSHOT_DIR" -f "$FILENAME" -c
        send_notification "Screenshot da janela copiado para área de transferência"
        ;;
    *)
        echo "Uso: $0 {output|window|region|region-copy|output-copy|window-copy}"
        exit 1
        ;;
esac

if [[ "$1" != *-copy ]] && [[ -f "$FILEPATH" ]]; then
    gwenview "$FILEPATH" &
fi
"""

    def _wallpaper_switcher_script(self) -> str:
        return """#!/bin/bash
# Wallpaper Switcher

WALLPAPER_DIR="$HOME/Imagens/wallpaper"
CURRENT_WALLPAPER="$HOME/.cache/current_wallpaper"

set_wallpaper() {
    local file="$1"
    hyprctl hyprpaper preload "$file"
    hyprctl hyprpaper wallpaper ",$file"
    echo "$file" > "$CURRENT_WALLPAPER"
    notify-send "🖼️ Wallpaper" "Alterado para: $(basename "$file")" -t 2000
}

list_wallpapers() {
    find "$WALLPAPER_DIR" -type f \\( -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" \\) | sort
}

if [[ "$1" == "--menu" ]]; then
    SELECTED=$(list_wallpapers | wofi --dmenu --prompt "Selecione wallpaper:" --lines 10)
    [[ -n "$SELECTED" ]] && set_wallpaper "$SELECTED"
    exit 0
fi

if [[ "$1" == "--random" ]]; then
    RANDOM_WALLPAPER=$(list_wallpapers | shuf -n 1)
    [[ -n "$RANDOM_WALLPAPER" ]] && set_wallpaper "$RANDOM_WALLPAPER"
    exit 0
fi

if [[ "$1" == "--next" ]] || [[ "$1" == "--prev" ]]; then
    CURRENT=$(cat "$CURRENT_WALLPAPER" 2>/dev/null)
    ALL_WALLPAPERS=($(list_wallpapers))
    [[ -z "$CURRENT" ]] && set_wallpaper "${ALL_WALLPAPERS[0]}" && exit 0

    current_index=-1
    for i in "${!ALL_WALLPAPERS[@]}"; do
        [[ "${ALL_WALLPAPERS[$i]}" == "$CURRENT" ]] && current_index=$i && break
    done

    if [[ "$1" == "--next" ]]; then
        next_index=$(( (current_index + 1) % ${#ALL_WALLPAPERS[@]} ))
    else
        next_index=$(( (current_index - 1 + ${#ALL_WALLPAPERS[@]}) % ${#ALL_WALLPAPERS[@]} ))
    fi

    set_wallpaper "${ALL_WALLPAPERS[$next_index]}"
    exit 0
fi

echo "Uso: $0 {--menu|--random|--next|--prev}"
"""

    def _reload_config_script(self) -> str:
        return """#!/bin/bash
# Recarrega configurações do Hyprland
hyprctl reload
notify-send "Hyprland" "Configurações recarregadas!" -t 2000
"""

    def _reload_all_script(self) -> str:
        return """#!/bin/bash
# Recarrega todos os serviços

echo "🔄 Recarregando todos os serviços..."

pkill hyprpaper 2>/dev/null
hyprpaper &
echo "  ✅ Hyprpaper recarregado"

hyprctl reload
echo "  ✅ Hyprland recarregado"

pkill waybar 2>/dev/null
sleep 0.5
waybar &
echo "  ✅ Waybar recarregado"

pkill swaync 2>/dev/null
sleep 0.5
swaync &
echo "  ✅ SwayNC recarregado"

pkill hypridle 2>/dev/null
hypridle &
echo "  ✅ Hypridle recarregado"

notify-send "🔄 Zennit-OS" "Todos os serviços recarregados!" -t 3000
echo "✅ Todos os serviços recarregados!"
"""

    def _waybar_notifications_script(self) -> str:
        return """#!/bin/bash
# Contagem de notificações para Waybar

COUNT=$(swaync-client --count 2>/dev/null || echo "0")
if [[ $COUNT -gt 0 ]]; then
    echo "{\\"text\\":\\"🔔 $COUNT\\", \\"tooltip\\":\\"$COUNT notificações\\"}"
else
    echo "{\\"text\\":\\"🔔 0\\", \\"tooltip\\":\\"Sem notificações\\"}"
fi
"""
