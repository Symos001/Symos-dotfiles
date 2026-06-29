#!/usr/bin/env python3
# =============================================================================
# tests/conftest.py — Fixtures compartilhadas para pytest
# =============================================================================

import sys
from pathlib import Path
from typing import Any, Generator

import pytest

# Adiciona o diretório pai ao PATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importa apenas o necessário para as fixtures
from config import Config
from logger import get_logger
from steps.base import Step, StepResult


@pytest.fixture
def logger():
    """Fixture para o logger."""
    return get_logger()


@pytest.fixture
def config():
    """Fixture para a configuração."""
    return Config()


@pytest.fixture
def step_result():
    """Fixture para um StepResult vazio."""
    return StepResult(name="Teste")


@pytest.fixture
def mock_step():
    """Cria um Step mock para testes."""

    class MockStep(Step):
        @property
        def name(self) -> str:
            return "Mock Step"

        def execute(self) -> StepResult:
            result = StepResult(name=self.name)
            result.mark_success("Mock executado")
            return result

    return MockStep(1, 1)


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Cria um diretório temporário para testes."""
    return tmp_path


@pytest.fixture
def mock_command_success(monkeypatch):
    """Mock para run_command que simula sucesso."""

    def mock_success(*args, **kwargs):
        class MockResult:
            returncode = 0
            stdout = "Mock output"
            stderr = ""

        return MockResult()

    return mock_success


@pytest.fixture
def mock_command_failure(monkeypatch):
    """Mock para run_command que simula falha."""

    def mock_failure(*args, **kwargs):
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "Mock error"

        return MockResult()

    return mock_failure
