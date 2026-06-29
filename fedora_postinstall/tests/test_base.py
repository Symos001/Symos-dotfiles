#!/usr/bin/env python3
# =============================================================================
# tests/test_base.py — Testes da classe base Step
# =============================================================================

import sys
from pathlib import Path

import pytest

# Adiciona o diretório pai ao PATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from steps.base import Step, StepResult, StepStatus

# ─── Testes do StepResult ──────────────────────────────────────────────────────


class TestStepResult:
    """Testes para a classe StepResult."""

    def test_initial_status(self):
        """Testa status inicial PENDING."""
        result = StepResult(name="Teste")
        assert result.status == StepStatus.PENDING
        assert result.name == "Teste"
        assert result.message == ""
        assert result.errors == []

    def test_mark_success(self):
        """Testa mark_success()."""
        result = StepResult(name="Teste")
        result.mark_success("Sucesso!")
        assert result.status == StepStatus.SUCCESS
        assert result.message == "Sucesso!"

    def test_mark_warning(self):
        """Testa mark_warning()."""
        result = StepResult(name="Teste")
        result.mark_warning("Aviso!")
        assert result.status == StepStatus.WARNING
        assert "Aviso!" in result.errors

    def test_mark_failed(self):
        """Testa mark_failed()."""
        result = StepResult(name="Teste")
        result.mark_failed("Falha!")
        assert result.status == StepStatus.FAILED
        assert "Falha!" in result.errors

    def test_mark_skipped(self):
        """Testa mark_skipped()."""
        result = StepResult(name="Teste")
        result.mark_skipped("Pulado!")
        assert result.status == StepStatus.SKIPPED
        assert result.message == "Pulado!"

    def test_is_success(self):
        """Testa a propriedade is_success."""
        result = StepResult(name="Teste")

        result.status = StepStatus.SUCCESS
        assert result.is_success is True

        result.status = StepStatus.WARNING
        assert result.is_success is True

        result.status = StepStatus.SKIPPED
        assert result.is_success is True

        result.status = StepStatus.FAILED
        assert result.is_success is False

        result.status = StepStatus.PENDING
        assert result.is_success is False


# ─── Testes do Step (classe abstrata) ────────────────────────────────────────


class TestStep:
    """Testes para a classe Step."""

    def test_step_creation(self):
        """Testa criação de um Step."""

        class ConcreteStep(Step):
            @property
            def name(self) -> str:
                return "Concrete Step"

            def execute(self) -> StepResult:
                result = StepResult(name=self.name)
                result.mark_success("OK")
                return result

        step = ConcreteStep(1, 1)
        assert step.name == "Concrete Step"
        assert step.step_number == 1
        assert step.total_steps == 1

    def test_step_run(self):
        """Testa o método run()."""

        class ConcreteStep(Step):
            @property
            def name(self) -> str:
                return "Concrete Step"

            def execute(self) -> StepResult:
                result = StepResult(name=self.name)
                result.mark_success("Executado")
                return result

        step = ConcreteStep(1, 1)
        result = step.run()

        # Verifica que o resultado é SUCCESS
        assert result.status == StepStatus.SUCCESS
        assert result.message == "Executado"
        assert result.is_success is True

    def test_step_run_with_exception(self):
        """Testa run() com exceção."""

        class FailingStep(Step):
            @property
            def name(self) -> str:
                return "Failing Step"

            def execute(self) -> StepResult:
                raise RuntimeError("Erro de teste")

        step = FailingStep(1, 1)
        result = step.run()

        # Verifica que falhou
        assert result.status == StepStatus.FAILED
        assert result.is_success is False
        assert any(
            "Erro de teste" in err or "Erro inesperado" in err for err in result.errors
        )

    def test_command_exists(self, monkeypatch):
        """Testa command_exists."""

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        # Mock shutil.which
        import shutil

        def mock_which(cmd):
            if cmd == "exists":
                return "/usr/bin/exists"
            return None

        monkeypatch.setattr(shutil, "which", mock_which)

        assert step.command_exists("exists") is True
        assert step.command_exists("not_exists") is False

    def test_run_command(self, monkeypatch):
        """Testa run_command."""
        import subprocess

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        # Mock subprocess.run
        def mock_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "test output"
                stderr = ""

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = step.run_command(["echo", "test"])
        assert result.returncode == 0
        assert result.stdout == "test output"


# ─── Testes dos métodos auxiliares ───────────────────────────────────────────


class TestStepHelpers:
    """Testes para métodos auxiliares do Step."""

    def test_dnf_install_success(self, monkeypatch):
        """Testa dnf_install com sucesso."""
        from steps.base import Step

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        # Mock run_command para sucesso
        def mock_success(*args, **kwargs):
            class MockResult:
                returncode = 0

            return MockResult()

        monkeypatch.setattr(step, "run_command", mock_success)

        assert step.dnf_install("test-pkg") is True

    def test_dnf_install_failure(self, monkeypatch):
        """Testa dnf_install com falha."""
        from steps.base import Step

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        # Mock run_command para falha
        def mock_fail(*args, **kwargs):
            raise Exception("Falha de teste")

        monkeypatch.setattr(step, "run_command", mock_fail)

        assert step.dnf_install("test-pkg") is False

    def test_write_file_success(self, temp_dir):
        """Testa write_file com sucesso."""
        from steps.base import Step

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        test_file = temp_dir / "test.txt"
        content = "Hello, World!"

        assert step.write_file(test_file, content) is True
        assert test_file.exists()
        assert test_file.read_text() == content

    def test_write_file_as_root_skip(self, temp_dir):
        """Testa write_file com as_root (pular por falta de permissão)."""
        from steps.base import Step

        class TestStep(Step):
            @property
            def name(self) -> str:
                return "Test Step"

            def execute(self) -> StepResult:
                return StepResult(name=self.name)

        step = TestStep(1, 1)

        # Testa com as_root (não deve falhar, apenas avisar)
        test_file = temp_dir / "test_root_file.txt"
        content = "Test content"

        # Não deve lançar exceção
        result = step.write_file(test_file, content, as_root=True)
        assert isinstance(result, bool)


# ─── Classe TestBase para compatibilidade ────────────────────────────────────


class TestBase:
    """Classe compatível para importação (mantida para compatibilidade)."""

    pass
