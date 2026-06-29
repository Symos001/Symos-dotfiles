#!/usr/bin/env python3
# =============================================================================
# main.py — Entry point do post-install
# =============================================================================

import sys
from pathlib import Path

from config import Config
from logger import get_logger
from steps import *

logger = get_logger()
config = Config()


def print_banner() -> None:
    """Mostra banner inicial."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🚀 ZENNIT-OS POST-INSTALL — Fedora Dev Environment                    ║
║                                                                        ║
║  📦 Multi-Linguagem: Java, C/C++, Rust, Elixir, Ruby, Crystal, Go,   ║
║                   Node.js, Bun, .NET                                   ║
║  🎨 Interface: Hyprland + Terafox/Nightfox                            ║
║  🔧 Ferramentas: Waybar, Wofi, Wlogout, SwayNC, Hyprlock             ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)


def main() -> int:
    """Função principal."""
    print_banner()
    logger.info(f"Log: {logger.log_file}")

    # Lista de steps
    steps = [
        PreFlightChecks(1, 26),
        RepositorySetup(2, 26),
        SystemUpdate(3, 26),
        BaseToolsInstaller(4, 26),
        KernelTuning(5, 26),
        ZramSetup(6, 26),
        CpuPowerManagement(7, 26),
        JavaBackendInstaller(8, 26),
        DevLanguagesInstaller(9, 26),
        DockerInstaller(10, 26),
        IdeToolsInstaller(11, 26),
        FontInstaller(12, 26),
        HyprlandSetup(13, 26),
        HyprlandConfig(14, 26),
        HyprshotConfig(15, 26),
        HyprpaperConfig(16, 26),
        WaybarConfig(17, 26),
        WofiConfig(18, 26),
        WlogoutConfig(19, 26),
        SwayNCConfig(20, 26),
        ZshConfig(21, 26),
        DotfilesSetup(22, 26),
        ScriptsSetup(23, 26),
        FinalCleanup(24, 26),
    ]

    # Executa todos os steps
    results = []
    for step in steps:
        result = step.run()
        results.append(result)

    # Resumo
    print(f"\n{'=' * 60}")
    print("  📊 RESUMO DA INSTALAÇÃO")
    print(f"{'=' * 60}")

    success = 0
    warnings = 0
    failed = 0

    for result in results:
        if result.is_success:
            success += 1
        elif result.status == StepStatus.WARNING:
            warnings += 1
        else:
            failed += 1

        status_icon = {
            StepStatus.SUCCESS: "✅",
            StepStatus.WARNING: "⚠️",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⊘",
        }.get(result.status, "?")

        print(f"  {status_icon} {result.name}")
        if result.errors:
            for error in result.errors[:2]:
                print(f"    ↳ {error}")

    print(f"\n  Total: {len(results)}")
    print(f"  ✅ Sucesso: {success}")
    print(f"  ⚠️ Avisos: {warnings}")
    print(f"  ❌ Falhas: {failed}")

    if failed > 0:
        print(f"\n  📝 Verifique o log: {logger.log_file}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Instalação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
