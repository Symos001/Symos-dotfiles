#!/usr/bin/env python3
# =============================================================================
# steps/final_cleanup.py — Limpeza final
# =============================================================================

from .base import Step, StepResult


class FinalCleanup(Step):
    """Limpeza final e mensagens."""

    @property
    def name(self) -> str:
        return "26/26 — Finalização"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        self.logger.info("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🎉 INSTALAÇÃO CONCLUÍDA!                                              ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  📋 PRÓXIMOS PASSOS:                                                   ║
║  1. Reinicie o sistema: sudo reboot                                    ║
║  2. No SDDM, selecione a sessão 'Hyprland'                            ║
║  3. Abra um terminal e execute: help                                  ║
║  4. Configure o Git: git config --global user.name "Seu Nome"        ║
║                                                                        ║
║  📦 LINGUAGENS INSTALADAS:                                             ║
║  Java 21, C/C++, Rust, Elixir, Ruby, Crystal, Go, Node.js, Bun, .NET ║
║                                                                        ║
║  🔧 FERRAMENTAS:                                                       ║
║  Hyprland, Waybar, Wofi, Wlogout, SwayNC, Hyprlock, Hyprpaper        ║
║  Neovim + LazyVim, ZED, VSCodium, IntelliJ IDEA, Rider              ║
║  Docker CE, SDKMan, NVM, Starship                                    ║
║                                                                        ║
║  📝 LOG: ~/fedora-postinstall.log                                    ║
╚══════════════════════════════════════════════════════════════════════════╝
        """)

        result.mark_success("Instalação concluída!")
        return result
