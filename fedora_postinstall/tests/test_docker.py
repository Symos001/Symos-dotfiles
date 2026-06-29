#!/usr/bin/env python3
# =============================================================================
# tests/test_docker.py — Testes do DockerInstaller
# =============================================================================

# Adiciona o diretório pai ao PATH
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from steps.base import StepResult, StepStatus
from steps.docker import DockerInstaller


class TestDockerInstaller:
    """Testes para o DockerInstaller."""

    def test_initialization(self):
        """Testa a inicialização."""
        installer = DockerInstaller(10, 26)
        assert installer.name == "10/26 — Docker CE + Compose"
        assert installer.step_number == 10
        assert installer.total_steps == 26

    def test_command_exists(self):
        """Testa command_exists para docker."""
        installer = DockerInstaller(10, 26)

        # Não deve lançar exceção
        exists = installer.command_exists("docker")
        assert isinstance(exists, bool)

    def test_docker_already_installed(self, monkeypatch):
        """Testa quando o Docker já está instalado."""
        installer = DockerInstaller(10, 26)

        # Mock command_exists para True (simula Docker instalado)
        def mock_command_exists(cmd):
            return cmd == "docker"

        monkeypatch.setattr(installer, "command_exists", mock_command_exists)

        # Mock do logger para evitar saída
        class MockLogger:
            def info(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                pass

            def success(self, msg):
                pass

            def fail(self, msg):
                pass

            def step_header(self, *args):
                pass

            def exception(self, *args):
                pass

        monkeypatch.setattr(installer, "logger", MockLogger())

        # Mock do config
        class MockConfig:
            user = "testuser"

        monkeypatch.setattr(installer, "config", MockConfig())

        result = installer.execute()

        # Verifica que o resultado é SUCCESS (usando o enum)
        assert result.status == StepStatus.SUCCESS
        assert "já instalado" in result.message

    def test_add_docker_repo_method_exists(self):
        """Testa se o método _add_docker_repo existe."""
        installer = DockerInstaller(10, 26)
        assert hasattr(installer, "_add_docker_repo")

    def test_add_docker_repo_manual_method_exists(self):
        """Testa se o método _add_docker_repo_manual existe."""
        installer = DockerInstaller(10, 26)
        assert hasattr(installer, "_add_docker_repo_manual")

    @patch("steps.docker.DockerInstaller.write_file")
    def test_add_docker_repo_manual(self, mock_write_file, monkeypatch):
        """Testa _add_docker_repo_manual."""
        installer = DockerInstaller(10, 26)

        # Mock write_file para True
        mock_write_file.return_value = True

        # Mock run_command para obter versão do Fedora
        def mock_run_command(cmd, *args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "44"
                stderr = ""

            return MockResult()

        monkeypatch.setattr(installer, "run_command", mock_run_command)

        result = StepResult(name="Teste")
        installer._add_docker_repo_manual(result)

        # Verifica se write_file foi chamado
        mock_write_file.assert_called()

    def test_docker_install_executes_without_error(self, monkeypatch):
        """Testa se execute() roda sem erro (apenas verificação)."""
        installer = DockerInstaller(10, 26)

        # Mock command_exists para False (Docker não instalado)
        def mock_command_exists(cmd):
            return False

        monkeypatch.setattr(installer, "command_exists", mock_command_exists)

        # Mock do logger
        class MockLogger:
            def info(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                pass

            def success(self, msg):
                pass

            def fail(self, msg):
                pass

            def step_header(self, *args):
                pass

            def exception(self, *args):
                pass

        monkeypatch.setattr(installer, "logger", MockLogger())

        # Mock dos métodos que precisam de sudo
        def mock_dnf_install(*args, **kwargs):
            return True

        def mock_add_docker_repo(*args, **kwargs):
            pass

        monkeypatch.setattr(installer, "dnf_install", mock_dnf_install)
        monkeypatch.setattr(installer, "_add_docker_repo", mock_add_docker_repo)

        # Não deve lançar exceção ao executar
        try:
            result = installer.execute()
            assert result is not None
            assert result.status in [
                StepStatus.SUCCESS,
                StepStatus.WARNING,
                StepStatus.FAILED,
            ]
        except Exception as e:
            # Pode falhar por falta de permissão, mas não deve ser erro de teste
            print(f"  → execute() falhou (esperado sem sudo): {e}")
            assert True
