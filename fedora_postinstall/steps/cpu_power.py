#!/usr/bin/env python3
# =============================================================================
# steps/cpu_power.py — Configura CPU e energia
# =============================================================================

import os
import shutil
from pathlib import Path

from .base import Step, StepResult


class CpuPowerManagement(Step):
    """Configura AMD pstate e auto-cpufreq."""

    @property
    def name(self) -> str:
        return "8/26 — CPU: AMD pstate + auto-cpufreq"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Desativa tuned (conflita com auto-cpufreq)
        self._disable_tuned(result)

        # AMD pstate
        self._setup_amd_pstate(result)

        # auto-cpufreq (corrigido)
        self._setup_auto_cpufreq(result)

        # Desativa power-profiles-daemon (pode não existir)
        self._disable_power_profiles(result)

        if result.is_success:
            result.mark_success("CPU configurada (efeito após reboot)")
        return result

    def _disable_tuned(self, result: StepResult) -> None:
        try:
            self.run_command(["sudo", "systemctl", "disable", "--now", "tuned"])
            self.logger.info("tuned desativado")
        except Exception as e:
            self.logger.info("tuned já estava desativado")

    def _setup_amd_pstate(self, result: StepResult) -> None:
        self.dnf_install("grubby")
        try:
            self.run_command(
                ["sudo", "grubby", "--update-kernel=ALL", "--args=amd_pstate=active"]
            )
            self.logger.info("amd_pstate=active aplicado (efeito após reboot)")
        except Exception as e:
            result.mark_warning(f"amd_pstate falhou: {e}")

    def _setup_auto_cpufreq(self, result: StepResult) -> None:
        """Instala auto-cpufreq via script oficial (com limpeza prévia)."""

        # Verifica se já está instalado
        if self.command_exists("auto-cpufreq"):
            self.logger.info("auto-cpufreq já instalado")
            # Garante que o serviço está ativo
            try:
                self.run_command(["sudo", "auto-cpufreq", "--install"])
                self.logger.info("auto-cpufreq serviço configurado")
            except Exception as e:
                result.mark_warning(f"auto-cpufreq --install falhou: {e}")
            return

        self.logger.info("Instalando auto-cpufreq...")

        src_dir = Path("/tmp/auto-cpufreq")

        # LIMPA O DIRETÓRIO SE EXISTIR
        if src_dir.exists():
            self.logger.info(f"Removendo diretório existente: {src_dir}")
            try:
                shutil.rmtree(src_dir)
                self.logger.info("Diretório removido com sucesso")
            except Exception as e:
                self.logger.warning(f"Não foi possível remover {src_dir}: {e}")
                # Tenta clonar em outro local
                src_dir = Path("/tmp/auto-cpufreq-new")
                if src_dir.exists():
                    shutil.rmtree(src_dir, ignore_errors=True)

        # Clona o repositório
        try:
            self.run_command(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "https://github.com/AdnanHodzic/auto-cpufreq.git",
                    str(src_dir),
                ]
            )
            self.logger.info("Repositório clonado")
        except Exception as e:
            result.mark_warning(f"Clone do repositório falhou: {e}")
            self.logger.info("Tentando instalar via Snap como alternativa...")
            self._install_auto_cpufreq_snap(result)
            return

        # Executa o instalador
        try:
            self.run_command(["sudo", "./auto-cpufreq-installer"], cwd=src_dir)
            self.logger.info("auto-cpufreq-installer executado")

            # Limpa o diretório após instalação (opcional)
            # shutil.rmtree(src_dir, ignore_errors=True)
        except Exception as e:
            result.mark_warning(f"auto-cpufreq-installer falhou: {e}")
            self.logger.info("Tentando instalar via Snap como alternativa...")
            self._install_auto_cpufreq_snap(result)
            return

        # Configura o serviço
        try:
            self.run_command(["sudo", "auto-cpufreq", "--install"])
            self.logger.info("auto-cpufreq serviço configurado")
        except Exception as e:
            result.mark_warning(f"auto-cpufreq --install falhou: {e}")

    def _install_auto_cpufreq_snap(self, result: StepResult) -> None:
        """Instala auto-cpufreq via Snap (alternativa mais rápida)."""
        self.logger.info("Instalando auto-cpufreq via Snap...")

        # Verifica se snap está instalado
        if not self.command_exists("snap"):
            self.logger.info("Instalando snapd...")
            self.dnf_install("snapd")
            try:
                self.run_command(
                    ["sudo", "systemctl", "enable", "--now", "snapd.socket"]
                )
                self.logger.info("snapd instalado")
            except Exception as e:
                result.mark_warning(f"Snapd falhou: {e}")
                return

        # Instala auto-cpufreq via Snap
        try:
            self.run_command(["sudo", "snap", "install", "auto-cpufreq"])
            self.logger.info("auto-cpufreq instalado via Snap")

            # Para Fedora (cgroups v2), executa uma vez para configurar
            try:
                self.run_command(["sudo", "snap", "run", "auto-cpufreq"], check=False)
                self.logger.info("auto-cpufreq configurado para cgroups v2")
            except:
                pass

            # Instala o serviço (via snap)
            try:
                self.run_command(["sudo", "auto-cpufreq", "--install"])
                self.logger.info("auto-cpufreq serviço configurado")
            except Exception as e:
                result.mark_warning(f"auto-cpufreq --install falhou: {e}")

        except Exception as e:
            result.mark_warning(f"auto-cpufreq via Snap falhou: {e}")
            self.logger.info("Para instalar manualmente:")
            self.logger.info(
                "  git clone https://github.com/AdnanHodzic/auto-cpufreq.git /tmp/auto-cpufreq"
            )
            self.logger.info("  cd /tmp/auto-cpufreq && sudo ./auto-cpufreq-installer")

    def _disable_power_profiles(self, result: StepResult) -> None:
        """Desativa power-profiles-daemon (pode não existir)."""
        try:
            self.run_command(
                ["sudo", "systemctl", "disable", "--now", "power-profiles-daemon"],
                check=False,
            )
            self.logger.info("power-profiles-daemon desativado")
        except Exception as e:
            self.logger.info("power-profiles-daemon já estava desativado ou não existe")
