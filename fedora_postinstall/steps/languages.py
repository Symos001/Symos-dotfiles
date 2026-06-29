#!/usr/bin/env python3
# =============================================================================
# steps/languages.py — Instala linguagens de programação (SEM SNAP)
# =============================================================================

import os
from pathlib import Path

from .base import Step, StepResult


class DevLanguagesInstaller(Step):
    """Instala C/C++, Rust, Elixir, Ruby, Crystal, Go, Node, Bun, .NET."""

    @property
    def name(self) -> str:
        return "9/26 — Linguagens de programação"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # C/C++
        self._install_c_cpp(result)

        # Rust
        self._install_rust(result)

        # Elixir + Erlang (via RPM Fusion)
        self._install_elixir(result)

        # Ruby
        self._install_ruby(result)

        # Crystal (via script oficial)
        self._install_crystal(result)

        # Golang
        self._install_go(result)

        # .NET
        self._install_dotnet(result)

        # Node.js + Bun (corrigido)
        self._install_node_bun(result)

        if result.is_success:
            result.mark_success("Linguagens instaladas")
        return result

    def _install_c_cpp(self, result: StepResult) -> None:
        self.logger.info("Instalando C/C++ compilers...")
        self.dnf_install(
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
        self.logger.info("C/C++ compilers instalados")

    def _install_rust(self, result: StepResult) -> None:
        if self.command_exists("rustc"):
            self.logger.info("Rust já instalado")
            return

        self.logger.info("Instalando Rust...")
        try:
            self.run_shell(
                'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
            )

            cargo_bin = Path.home() / ".cargo" / "bin"
            if cargo_bin.exists():
                os.environ["PATH"] = f"{cargo_bin}:{os.environ.get('PATH', '')}"

            self.run_shell(
                'source "$HOME/.cargo/env" && cargo install cargo-edit cargo-watch 2>/dev/null || true'
            )
            self.logger.info("Rust instalado")
        except Exception as e:
            result.mark_warning(f"Rust falhou: {e}")

    def _install_elixir(self, result: StepResult) -> None:
        """Instala Elixir/Erlang via RPM Fusion."""
        self.logger.info("Instalando Elixir/Erlang via RPM Fusion...")

        try:
            # Erlang
            self.logger.info("Instalando Erlang...")
            if self.dnf_install("erlang"):
                self.logger.info("Erlang instalado")
            else:
                result.mark_warning("Erlang não encontrado")
                return

            # Elixir
            self.logger.info("Instalando Elixir...")
            if self.dnf_install("elixir"):
                self.logger.info("Elixir instalado")

                try:
                    self.run_shell("mix local.hex --force")
                    self.run_shell("mix local.rebar --force")
                    self.logger.info("Hex e Rebar configurados")
                except Exception as e:
                    result.mark_warning(f"Hex/Rebar falhou: {e}")
            else:
                result.mark_warning("Elixir não encontrado")
        except Exception as e:
            result.mark_warning(f"Elixir/Erlang falhou: {e}")

    def _install_ruby(self, result: StepResult) -> None:
        self.logger.info("Instalando Ruby...")
        self.dnf_install("ruby", "ruby-devel", "rubygems")
        self.logger.info("Ruby instalado")

    def _install_crystal(self, result: StepResult) -> None:
        """Instala Crystal via script oficial (já que COPR não existe para Fedora 44)."""
        self.logger.info("Instalando Crystal via script oficial...")

        # Tenta instalar via script oficial
        try:
            self.run_shell("curl -fsSL https://crystal-lang.org/install.sh | sudo bash")
            self.logger.info("Crystal instalado via script oficial")
        except Exception as e:
            result.mark_warning(f"Crystal script oficial falhou: {e}")
            self.logger.info(
                "Para instalar manualmente: https://crystal-lang.org/install/on_fedora/"
            )

    def _install_go(self, result: StepResult) -> None:
        self.logger.info("Instalando Golang...")
        self.dnf_install("golang")
        self.logger.info("Golang instalado")

    def _install_dotnet(self, result: StepResult) -> None:
        self.logger.info("Instalando .NET SDK 8.0...")
        self.dnf_install("dotnet-sdk-8.0")
        self.logger.info(".NET SDK 8.0 instalado")

    def _install_node_bun(self, result: StepResult) -> None:
        """Instala Node.js e Bun (evitando conflito com pacote nativo)."""

        # Node.js via NVM (evita conflitos com o pacote nativo)
        self.logger.info("Instalando Node.js via NVM...")

        nvm_dir = Path.home() / ".nvm"
        if not nvm_dir.exists():
            self.logger.info("Instalando NVM...")
            try:
                self.run_shell(
                    "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
                )
                self.logger.info("NVM instalado")
            except Exception as e:
                result.mark_warning(f"NVM falhou: {e}")
                return

        # Carrega NVM e instala Node.js LTS
        try:
            # Remove pacotes Node.js nativos do Fedora (se existirem)
            self.run_command(
                [
                    "sudo",
                    "dnf",
                    "remove",
                    "-y",
                    "nodejs",
                    "nodejs22-bin",
                    "nodejs22-npm-bin",
                ],
                check=False,
            )

            # Instala Node.js LTS via NVM
            self.run_shell(
                'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm install --lts'
            )
            self.run_shell(
                'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm alias default "lts/*"'
            )
            self.logger.info("Node.js LTS instalado via NVM")
        except Exception as e:
            result.mark_warning(f"Node.js via NVM falhou: {e}")
            self.logger.info("Tentando instalar via NodeSource...")
            try:
                # NodeSource
                self.run_shell(
                    "curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -"
                )
                self.dnf_install("nodejs")
                self.logger.info("Node.js instalado via NodeSource")
            except Exception as e2:
                result.mark_warning(f"Node.js falhou: {e2}")

        # Bun
        if not self.command_exists("bun"):
            self.logger.info("Instalando Bun...")
            try:
                self.run_shell("curl -fsSL https://bun.sh/install | bash")
                self.logger.info("Bun instalado")
            except Exception as e:
                result.mark_warning(f"Bun falhou: {e}")
