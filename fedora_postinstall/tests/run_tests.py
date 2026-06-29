#!/usr/bin/env python3
# =============================================================================
# tests/run_tests.py — Executa todos os testes via pytest
# =============================================================================

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Executa todos os testes usando pytest."""
    print("\n" + "=" * 60)
    print("🚀 EXECUTANDO TESTES COM PYTEST")
    print("=" * 60)

    # Verifica se pytest está instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest não está instalado!")
        print("   Execute: pip install pytest pytest-cov")
        return 1

    # Executa pytest
    args = [
        "pytest",
        "-v",
        "--tb=short",
        "--strict-markers",
        str(Path(__file__).parent),
    ]

    # Adiciona cobertura se disponível
    try:
        import pytest_cov

        args.extend(["--cov=steps", "--cov-report=term-missing"])
    except ImportError:
        print("⚠️  pytest-cov não instalado (opcional)")

    return subprocess.call(args)


if __name__ == "__main__":
    sys.exit(main())
