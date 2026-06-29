#!/usr/bin/env python3
# =============================================================================
# steps/zram_setup.py — Configura ZRAM
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class ZramSetup(Step):
    """Configura ZRAM como swap comprimido."""

    @property
    def name(self) -> str:
        return "6/26 — ZRAM (swap comprimido)"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Instala zram-generator
        self.dnf_install("zram-generator")

        # Configura
        config = """[zram0]
zram-size = ram / 2
compression-algorithm = zstd
swap-priority = 100
"""
        self.write_file(Path("/etc/systemd/zram-generator.conf"), config, as_root=True)

        try:
            self.run_command(["sudo", "systemctl", "daemon-reload"])
            self.logger.info("ZRAM configurado (50% RAM, zstd)")
            result.mark_success("ZRAM configurado")
        except Exception as e:
            result.mark_failed(f"ZRAM falhou: {e}")

        return result
