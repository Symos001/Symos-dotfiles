#!/usr/bin/env python3
# =============================================================================
# tests/conftest.py — Fixtures compartilhadas para pytest
# =============================================================================

import sys
from pathlib import Path
from typing import Any, Generator

import pytest

# Adiciona o diretório pai ao PATH
sys.path.insert(0, str(Path(__file__).parent.parent))

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
