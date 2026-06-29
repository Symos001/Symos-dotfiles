#!/usr/bin/env python3
# =============================================================================
# steps/system_update.py — Atualização do sistema
# =============================================================================

from .base import Step, StepResult


class SystemUpdate(Step):
    """Atualiza o sistema."""

    @property
    def name(self) -> str:
        return "3/26 — Atualização do sistema"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        self.logger.info("Executando dnf upgrade...")
        try:
            self.run_command(["sudo", "dnf", "upgrade", "-y", "--refresh"])
            result.mark_success("Sistema atualizado")
        except Exception as e:
            result.mark_failed(f"Falha ao atualizar sistema: {e}")

        return result
