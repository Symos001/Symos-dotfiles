#!/usr/bin/env python3
# =============================================================================
# steps/java_backend.py — Configura Java Backend
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class JavaBackendInstaller(Step):
    """Instala SDKMan, Java, Maven, Gradle, Quarkus."""

    @property
    def name(self) -> str:
        return "8/26 — Java Backend"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # SDKMan
        self._install_sdkman(result)

        # Java e ferramentas
        self._install_java_tools(result)

        if result.is_success:
            result.mark_success("Java Backend configurado")
        return result

    def _install_sdkman(self, result: StepResult) -> None:
        sdkman_init = Path.home() / ".sdkman" / "bin" / "sdkman-init.sh"
        if sdkman_init.exists():
            self.logger.info("SDKMan já instalado")
            return

        self.logger.info("Instalando SDKMan...")
        try:
            import subprocess

            subprocess.run(
                'curl -s "https://get.sdkman.io" | bash -s -- -y',
                shell=True,
                check=True,
            )
            self.logger.info("SDKMan instalado")
        except Exception as e:
            result.mark_failed(f"SDKMan falhou: {e}")

    def _install_java_tools(self, result: StepResult) -> None:
        sdkman_init = Path.home() / ".sdkman" / "bin" / "sdkman-init.sh"
        if not sdkman_init.exists():
            result.mark_warning("SDKMan não encontrado")
            return

        self.logger.info("Instalando Java 21...")

        # Comandos via SDKMan
        cmds = [
            'source "{}" && sdk install java 21-tem'.format(sdkman_init),
            'source "{}" && sdk default java 21-tem'.format(sdkman_init),
            'source "{}" && sdk install maven'.format(sdkman_init),
            'source "{}" && sdk install gradle'.format(sdkman_init),
            'source "{}" && sdk install quarkus'.format(sdkman_init),
        ]

        for cmd in cmds:
            try:
                import subprocess

                subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
            except Exception as e:
                result.mark_warning(f"Falha no comando SDKMan: {e}")

        self.logger.info("Java 21 + Maven + Gradle + Quarkus instalados")
