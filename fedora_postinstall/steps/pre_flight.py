#!/usr/bin/env python3
# =============================================================================
# steps/pre_flight.py — Verificações iniciais
# =============================================================================

import os
import subprocess
from pathlib import Path

from .base import Step, StepResult


class PreFlightChecks(Step):
    """Verifica pré-condições: não root, internet, sudo."""

    @property
    def name(self) -> str:
        return "1/26 — Verificações iniciais"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Verifica se não é root
        if os.geteuid() == 0:
            result.mark_failed(
                "Não execute como root. Use seu usuário normal com sudo."
            )
            return result

        self.logger.info("Verificando conectividade...")
        try:
            subprocess.run(
                ["ping", "-c", "1", "-W", "3", "8.8.8.8"],
                check=True,
                capture_output=True,
            )
            self.logger.info("Conectividade OK")
        except subprocess.CalledProcessError:
            result.mark_failed("Sem acesso à internet. Verifique sua conexão.")
            return result

        # Autentica sudo
        self.logger.info("Autenticando sudo (pode pedir sua senha)...")
        try:
            subprocess.run(["sudo", "-v"], check=True)
            self.logger.info("Sudo autenticado")
        except subprocess.CalledProcessError:
            result.mark_failed("Falha ao autenticar sudo. Verifique sua senha.")
            return result

        # Mantém sudo ativo
        self._keep_sudo_alive()

        result.mark_success("Pré-condições verificadas")
        return result

    def _keep_sudo_alive(self) -> None:
        """Mantém sudo ativo durante a execução."""
        import threading
        import time

        def keep_alive():
            while True:
                try:
                    subprocess.run(["sudo", "-n", "true"], check=True)
                    time.sleep(60)
                except:
                    break

        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
