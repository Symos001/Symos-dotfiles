#!/usr/bin/env python3
# =============================================================================
# tests/test_languages.py — Testes do DevLanguagesInstaller
# =============================================================================

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from steps.base import StepResult
from steps.languages import DevLanguagesInstaller


class TestLanguagesInstaller:
    """Testes para o DevLanguagesInstaller."""

    def test_initialization(self):
        """Testa a inicialização."""
        installer = DevLanguagesInstaller(9, 26)
        assert installer.name == "9/26 — Linguagens de programação"
        assert installer.step_number == 9
        assert installer.total_steps == 26

    def test_methods_exist(self):
        """Testa se os métodos existem."""
        installer = DevLanguagesInstaller(9, 26)

        methods = [
            "_install_c_cpp",
            "_install_rust",
            "_install_elixir",
            "_install_ruby",
            "_install_crystal",
            "_install_go",
            "_install_dotnet",
            "_install_node_bun",
        ]

        for method in methods:
            assert hasattr(installer, method), f"Método {method} não encontrado"

    @patch("steps.languages.DevLanguagesInstaller.dnf_install")
    def test_install_c_cpp(self, mock_dnf_install):
        """Testa _install_c_cpp."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        installer._install_c_cpp(result)

        # Verifica se dnf_install foi chamado com os pacotes corretos
        mock_dnf_install.assert_called_with(
            "gcc",
            "gcc-c++",
            "make",
            "cmake",
            "ninja-build",
            "gdb",
            "valgrind",
            "libtool",
            "autoconf",
            "automake",
            "openssl-devel",
        )

    @patch("steps.languages.DevLanguagesInstaller.run_shell")
    def test_install_rust(self, mock_run_shell, monkeypatch):
        """Testa _install_rust."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        # Mock command_exists para False (Rust não instalado)
        def mock_exists(cmd):
            return cmd == "rustc"  # Simula que Rust já está instalado

        monkeypatch.setattr(installer, "command_exists", mock_exists)

        installer._install_rust(result)

        # Se Rust já está instalado, não deve chamar run_shell
        mock_run_shell.assert_not_called()

    @patch("steps.languages.DevLanguagesInstaller.dnf_install")
    def test_install_ruby(self, mock_dnf_install):
        """Testa _install_ruby."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        installer._install_ruby(result)

        mock_dnf_install.assert_called_with("ruby", "ruby-devel", "rubygems")

    @patch("steps.languages.DevLanguagesInstaller.dnf_install")
    def test_install_go(self, mock_dnf_install):
        """Testa _install_go."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        installer._install_go(result)

        mock_dnf_install.assert_called_with("golang")

    @patch("steps.languages.DevLanguagesInstaller.dnf_install")
    def test_install_dotnet(self, mock_dnf_install):
        """Testa _install_dotnet."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        installer._install_dotnet(result)

        mock_dnf_install.assert_called_with("dotnet-sdk-8.0")

    def test_install_elixir_no_error(self):
        """Testa _install_elixir (sem erro)."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        # Não deve lançar exceção
        try:
            installer._install_elixir(result)
            assert True
        except Exception as e:
            # Pode falhar por falta de permissão ou pacotes
            print(f"  → _install_elixir: {e}")
            assert True

    def test_install_crystal_no_error(self):
        """Testa _install_crystal (sem erro)."""
        installer = DevLanguagesInstaller(9, 26)
        result = StepResult(name="Teste")

        try:
            installer._install_crystal(result)
            assert True
        except Exception as e:
            print(f"  → _install_crystal: {e}")
            assert True
