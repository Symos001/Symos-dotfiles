#!/usr/bin/env python3
# =============================================================================
# steps/docker.py — Instala Docker CE (Fedora 44)
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class DockerInstaller(Step):
    """Instala Docker CE e Compose."""

    @property
    def name(self) -> str:
        return "10/26 — Docker CE + Compose"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        if self.command_exists("docker"):
            self.logger.info("Docker já instalado")
            result.mark_success("Docker já instalado")
            return result

        self.logger.info("Instalando Docker...")

        # Adiciona repositório Docker (Fedora 44 usa dnf5)
        self._add_docker_repo(result)

        # Instala Docker
        self.dnf_install(
            "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"
        )

        # Inicia serviço
        try:
            self.run_command(["sudo", "systemctl", "enable", "--now", "docker"])
            self.run_command(["sudo", "usermod", "-aG", "docker", self.config.user])
            self.logger.info(f"Usuário {self.config.user} adicionado ao grupo docker")
        except Exception as e:
            result.mark_warning(f"Configuração Docker falhou: {e}")

        # Firewall
        try:
            self.run_command(
                [
                    "sudo",
                    "firewall-cmd",
                    "--permanent",
                    "--zone=trusted",
                    "--add-interface=docker0",
                ],
                check=False,
            )
            self.run_command(["sudo", "firewall-cmd", "--reload"], check=False)
        except:
            pass

        result.mark_success("Docker CE instalado")
        return result

    def _add_docker_repo(self, result: StepResult) -> None:
        """Adiciona o repositório Docker (compatível com Fedora 44)."""

        # Tenta o comando do dnf5
        try:
            self.run_command(
                [
                    "sudo",
                    "dnf",
                    "config-manager",
                    "--add-repo",
                    "https://download.docker.com/linux/fedora/docker-ce.repo",
                ]
            )
            self.logger.info("Repositório Docker adicionado via dnf config-manager")
            return
        except Exception as e:
            self.logger.warning(f"dnf config-manager falhou: {e}")
            self.logger.info("Usando método alternativo...")

        # Fallback: método manual
        self._add_docker_repo_manual(result)

    def _add_docker_repo_manual(self, result: StepResult) -> None:
        """Adiciona o repositório Docker manualmente (fallback)."""
        self.logger.info("Adicionando repositório Docker manualmente...")

        # Obtém a versão do Fedora
        try:
            fedora_ver = self.run_command(
                ["rpm", "-E", "%fedora"], capture=True
            ).stdout.strip()
        except:
            fedora_ver = "44"  # fallback

        repo_content = f"""[docker-ce-stable]
name=Docker CE Stable - $basearch
baseurl=https://download.docker.com/linux/fedora/{fedora_ver}/$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://download.docker.com/linux/fedora/gpg
"""

        repo_path = Path("/etc/yum.repos.d/docker-ce.repo")
        if self.write_file(repo_path, repo_content, as_root=True):
            self.logger.info("Repositório Docker adicionado manualmente")
        else:
            result.mark_warning("Falha ao adicionar repositório Docker manualmente")
            self.logger.info("Tente adicionar manualmente:")
            self.logger.info(f"  sudo tee {repo_path} << 'EOF'")
            self.logger.info(repo_content)
            self.logger.info("EOF")
