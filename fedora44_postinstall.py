#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          Fedora 44 — Post-Install Setup Script               ║
║          by Lucas  •  github.com/lucas                       ║
╚══════════════════════════════════════════════════════════════╝

Verifica e instala:
  • RPM Fusion (free + nonfree)
  • Flathub
  • SDKMAN → Java (21 LTS) → .NET
  • Rust (rustup oficial)
  • Go (golang)
  • Elixir + Erlang
  • Ruby
  • C/C++ build tools (gcc, g++, make, cmake, gdb, clang, meson…)
  • Starship prompt
  • FiraCode Nerd Font (monospaced)
  • bat  •  eza  •  alias ls com ícones
"""

import os
import shutil
import subprocess
import sys
import textwrap

# ──────────────────────────────────────────────────────────────
# CORES ANSI
# ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"

def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"

# ──────────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────────
LINE = c(DIM, "─" * 62)

def banner():
    print()
    print(c(BOLD + BG_BLUE, " " * 62))
    print(c(BOLD + BG_BLUE, "   🚀  Fedora 44 — Post-Install Setup                       "))
    print(c(BOLD + BG_BLUE, " " * 62))
    print()

def section(title: str):
    print()
    print(LINE)
    print(c(BOLD + CYAN, f"  ▸ {title}"))
    print(LINE)

def info(msg: str):
    print(c(BLUE, "  ℹ  ") + msg)

def ok(msg: str):
    print(c(GREEN, "  ✔  ") + msg)

def warn(msg: str):
    print(c(YELLOW, "  ⚠  ") + msg)

def err(msg: str):
    print(c(RED, "  ✖  ") + msg)

def step(msg: str):
    print(c(MAGENTA, "  →  ") + msg)

def ask(msg: str) -> bool:
    ans = input(c(YELLOW + BOLD, f"\n  ? {msg} [s/N] ")).strip().lower()
    return ans in ("s", "y", "sim", "yes")

def run(cmd: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Roda um comando shell com saída ao vivo ou capturada."""
    kwargs = dict(shell=True, check=check)
    if capture:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return subprocess.run(cmd, **kwargs)

def run_silent(cmd: str) -> bool:
    """Retorna True se o comando sair com código 0."""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def require_root():
    if os.geteuid() != 0:
        err("Execute como root:  sudo python3 fedora44_postinstall.py")
        sys.exit(1)

def get_real_user() -> tuple[str, str]:
    """Retorna (username, home) do usuário real (não root via sudo)."""
    user = os.environ.get("SUDO_USER") or os.environ.get("USER", "")
    if not user or user == "root":
        warn("Não foi possível detectar usuário real. Usando 'root'.")
        return "root", "/root"
    home = os.path.expanduser(f"~{user}")
    return user, home

# ──────────────────────────────────────────────────────────────
# VERIFICAÇÕES
# ──────────────────────────────────────────────────────────────
def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None

def dnf_repo_enabled(repo_id: str) -> bool:
    result = subprocess.run(
        f"dnf5 repolist --enabled 2>/dev/null | grep -qi '{repo_id}'",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def flatpak_remote_exists(name: str) -> bool:
    return run_silent(f"flatpak remotes 2>/dev/null | grep -qi '{name}'")

def font_installed(pattern: str) -> bool:
    return run_silent(f"fc-list | grep -qi '{pattern}'")

def file_contains(filepath: str, pattern: str) -> bool:
    try:
        with open(filepath) as f:
            return pattern in f.read()
    except FileNotFoundError:
        return False

# ──────────────────────────────────────────────────────────────
# STATUS REPORT
# ──────────────────────────────────────────────────────────────
STATUS_ROWS: list[tuple[str, bool, str]] = []

def record(label: str, present: bool, note: str = ""):
    STATUS_ROWS.append((label, present, note))

def print_status_table():
    section("Relatório Final de Status")
    col_w = 32
    print(f"  {c(BOLD, 'Componente'):<{col_w+10}}  {c(BOLD, 'Status'):<18}  {c(BOLD, 'Obs')}")
    print(c(DIM, "  " + "─" * 60))
    for label, present, note in STATUS_ROWS:
        status_str = c(GREEN, "✔ instalado") if present else c(RED, "✖ ausente")
        note_str   = c(DIM, note) if note else ""
        print(f"  {label:<{col_w}}  {status_str:<28}  {note_str}")
    print()

# ──────────────────────────────────────────────────────────────
# INSTALAÇÕES
# ──────────────────────────────────────────────────────────────

def setup_rpm_fusion():
    section("RPM Fusion (free + nonfree)")
    free_ok   = dnf_repo_enabled("rpmfusion-free")
    nonfree_ok = dnf_repo_enabled("rpmfusion-nonfree")

    if free_ok and nonfree_ok:
        ok("RPM Fusion já está habilitado.")
    else:
        info("Habilitando RPM Fusion para Fedora 44…")
        run("dnf5 install -y "
            "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm "
            "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")
        ok("RPM Fusion habilitado.")

    record("RPM Fusion free",   dnf_repo_enabled("rpmfusion-free"))
    record("RPM Fusion nonfree", dnf_repo_enabled("rpmfusion-nonfree"))


def setup_flathub():
    section("Flathub")
    if flatpak_remote_exists("flathub"):
        ok("Flathub já está configurado.")
    else:
        if not cmd_exists("flatpak"):
            info("Instalando flatpak…")
            run("dnf5 install -y flatpak")
        info("Adicionando remote Flathub…")
        run("flatpak remote-add --if-not-exists flathub "
            "https://dl.flathub.org/repo/flathub.flatpakrepo")
        ok("Flathub adicionado.")
    record("Flathub remote", flatpak_remote_exists("flathub"))


def setup_sdkman_java_dotnet(real_user: str, home: str):
    section("SDKMAN + Java 21 LTS + .NET")

    sdkman_dir = os.path.join(home, ".sdkman")
    sdkman_init = os.path.join(sdkman_dir, "bin", "sdkman-init.sh")

    # ── SDKMAN ──
    if os.path.isfile(sdkman_init):
        ok(f"SDKMAN já instalado em {sdkman_dir}")
    else:
        info("Instalando SDKMAN…")
        run(f'su -c "curl -s https://get.sdkman.io | bash" {real_user}')
        ok("SDKMAN instalado.")
    record("SDKMAN", os.path.isfile(sdkman_init))

    sdk_cmd = f'source "{sdkman_init}" && sdk'

    # ── Java ──
    java_ok = cmd_exists("java")
    if java_ok:
        ok("Java já encontrado no PATH.")
    else:
        info("Instalando Java 21 (Temurin) via SDKMAN…")
        run(f'su -c \'bash -c "{sdk_cmd} install java 21.0.3-tem"\' {real_user}')
        ok("Java 21 instalado.")
    record("Java (sdk)", cmd_exists("java") or
           run_silent(f'su -c \'bash -c "source {sdkman_init} && java -version"\' {real_user}'))

    # ── .NET ──
    dotnet_ok = cmd_exists("dotnet")
    if dotnet_ok:
        ok(".NET SDK já encontrado no PATH.")
    else:
        info("Instalando .NET 8 via SDKMAN…")
        run(f'su -c \'bash -c "{sdk_cmd} install dotnet 8.0.100"\' {real_user}', check=False)
        # Fallback: pacote do sistema
        if not run_silent(f'su -c \'bash -c "source {sdkman_init} && dotnet --version"\' {real_user}'):
            warn(".NET não encontrado via SDKMAN — tentando dotnet-sdk-8.0 do repositório…")
            run("dnf5 install -y dotnet-sdk-8.0", check=False)
        ok(".NET instalado.")
    record(".NET SDK", cmd_exists("dotnet") or
           run_silent(f'su -c \'bash -c "source {sdkman_init} && dotnet --version"\' {real_user}'))


def setup_rust(real_user: str, home: str):
    section("Rust (rustup — método oficial)")
    cargo_bin = os.path.join(home, ".cargo", "bin", "cargo")

    if os.path.isfile(cargo_bin) or cmd_exists("rustc"):
        ok("Rust já instalado.")
    else:
        info("Instalando Rust via rustup.rs…")
        run(f'su -c "curl --proto=https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y" {real_user}')
        ok("Rust instalado.")

    record("Rust (rustc)", os.path.isfile(cargo_bin) or cmd_exists("rustc"))
    record("Cargo",        os.path.isfile(cargo_bin) or cmd_exists("cargo"))


def setup_golang():
    section("Go (Golang)")
    if cmd_exists("go"):
        ver = subprocess.getoutput("go version 2>/dev/null").split()
        ok(f"Go já instalado: {' '.join(ver[2:3])}")
    else:
        info("Instalando golang via DNF5…")
        run("dnf5 install -y golang")
        ok("Go instalado.")
    record("Go", cmd_exists("go"))


def setup_elixir():
    section("Elixir + Erlang")
    elixir_ok = cmd_exists("elixir")
    erl_ok    = cmd_exists("erl")

    if elixir_ok and erl_ok:
        ok("Elixir e Erlang já instalados.")
    else:
        info("Instalando Erlang e Elixir via DNF5…")
        run("dnf5 install -y erlang elixir")
        ok("Elixir + Erlang instalados.")

    record("Erlang (erl)",   cmd_exists("erl"))
    record("Elixir",         cmd_exists("elixir"))


def setup_ruby():
    section("Ruby")
    if cmd_exists("ruby"):
        ver = subprocess.getoutput("ruby --version 2>/dev/null")
        ok(f"Ruby já instalado: {ver}")
    else:
        info("Instalando Ruby via DNF5…")
        run("dnf5 install -y ruby ruby-devel")
        ok("Ruby instalado.")
    record("Ruby", cmd_exists("ruby"))


def setup_c_cpp_tools():
    section("Ferramentas de Desenvolvimento C/C++")
    pkgs = [
        "gcc", "gcc-c++", "make", "cmake", "gdb",
        "clang", "lldb", "meson", "ninja-build",
        "valgrind", "binutils", "autoconf", "automake",
        "libtool", "pkgconf-pkg-config",
    ]
    info("Instalando grupo 'Development Tools' e pacotes C/C++…")
    run('dnf5 group install -y "Development Tools"', check=False)
    run(f"dnf5 install -y {' '.join(pkgs)}")
    ok("Ferramentas C/C++ instaladas.")

    for tool in ("gcc", "g++", "make", "cmake", "gdb", "clang", "meson", "ninja"):
        record(f"C/C++: {tool}", cmd_exists(tool))


def setup_starship(real_user: str, home: str):
    section("Starship Prompt")
    if cmd_exists("starship"):
        ok("Starship já instalado.")
    else:
        info("Instalando Starship via script oficial…")
        run('curl -sS https://starship.rs/install.sh | sh -s -- --yes')
        ok("Starship instalado.")

    # Adicionar ao shell do usuário
    for shell_rc in [".bashrc", ".zshrc", ".config/fish/config.fish"]:
        rc_path = os.path.join(home, shell_rc)
        if not os.path.isfile(rc_path):
            continue
        is_fish = shell_rc.endswith("config.fish")
        init_line = (
            'starship init fish | source'
            if is_fish
            else 'eval "$(starship init bash)"'
            if "bash" in shell_rc
            else 'eval "$(starship init zsh)"'
        )
        if not file_contains(rc_path, "starship init"):
            with open(rc_path, "a") as f:
                f.write(f'\n# Starship prompt\n{init_line}\n')
            step(f"Starship adicionado a {rc_path}")

    record("Starship", cmd_exists("starship"))


def setup_firacode(real_user: str):
    section("Fontes FiraCode Nerd Font (monospaced)")

    if font_installed("FiraCode"):
        ok("FiraCode já instalada.")
    else:
        info("Instalando fontes FiraCode via DNF5…")
        run("dnf5 install -y fira-code-fonts", check=False)

    # Tenta também via Nerd Fonts (zip do GitHub releases)
    if not font_installed("FiraCode Nerd"):
        info("Baixando FiraCode Nerd Font do GitHub…")
        nerd_dir = "/usr/local/share/fonts/FiraCodeNerd"
        os.makedirs(nerd_dir, exist_ok=True)
        run(
            "curl -fLo /tmp/FiraCode.zip "
            "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip"
        )
        run(f"unzip -o /tmp/FiraCode.zip -d {nerd_dir}")
        run("fc-cache -fv")
        ok("FiraCode Nerd Font instalada.")

    record("FiraCode (sistema)", font_installed("FiraCode"))
    record("FiraCode Nerd Font", font_installed("FiraCode Nerd") or font_installed("FiraCode"))


def setup_bat_eza(real_user: str, home: str):
    section("bat  •  eza  •  alias ls com ícones")

    # ── bat ──
    if cmd_exists("bat"):
        ok("bat já instalado.")
    else:
        info("Instalando bat…")
        run("dnf5 install -y bat")
        ok("bat instalado.")

    # ── eza ──
    if cmd_exists("eza"):
        ok("eza já instalado.")
    else:
        info("Instalando eza…")
        run("dnf5 install -y eza", check=False)
        if not cmd_exists("eza"):
            # fallback: cargo install
            cargo = os.path.join(home, ".cargo", "bin", "cargo")
            if os.path.isfile(cargo) or cmd_exists("cargo"):
                warn("eza não encontrado via DNF — instalando via cargo…")
                run(f'su -c "cargo install eza" {real_user}')
        ok("eza instalado.")

    # ── aliases ──
    alias_block = textwrap.dedent("""
        # ── eza aliases (ls com ícones) ──────────────────────────────
        alias ls='eza --icons=always --group-directories-first'
        alias ll='eza -lh --icons=always --group-directories-first --git'
        alias la='eza -lah --icons=always --group-directories-first --git'
        alias lt='eza --tree --icons=always --level=2'
        alias l='eza -1 --icons=always'
    """)

    for shell_rc in [".bashrc", ".zshrc"]:
        rc_path = os.path.join(home, shell_rc)
        if not os.path.isfile(rc_path):
            continue
        if not file_contains(rc_path, "eza aliases"):
            with open(rc_path, "a") as f:
                f.write(alias_block)
            step(f"Aliases adicionados a {rc_path}")
        else:
            ok(f"Aliases já presentes em {rc_path}")

    record("bat",            cmd_exists("bat"))
    record("eza",            cmd_exists("eza") or run_silent(f'su -c "~/.cargo/bin/eza --version" {real_user}'))
    record("aliases ls/eza", file_contains(os.path.join(home, ".bashrc"), "eza aliases") or
                              file_contains(os.path.join(home, ".zshrc"), "eza aliases"))


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    banner()
    require_root()

    real_user, home = get_real_user()
    info(f"Usuário detectado: {c(BOLD, real_user)}  •  Home: {c(BOLD, home)}")
    info(f"Fedora: {subprocess.getoutput('rpm -E %fedora')}")

    if not ask("Iniciar configuração pós-instalação?"):
        print(c(YELLOW, "\n  Cancelado pelo usuário.\n"))
        sys.exit(0)

    tasks = [
        ("RPM Fusion",             lambda: setup_rpm_fusion()),
        ("Flathub",                lambda: setup_flathub()),
        ("SDKMAN + Java + .NET",   lambda: setup_sdkman_java_dotnet(real_user, home)),
        ("Rust",                   lambda: setup_rust(real_user, home)),
        ("Go",                     lambda: setup_golang()),
        ("Elixir + Erlang",        lambda: setup_elixir()),
        ("Ruby",                   lambda: setup_ruby()),
        ("Ferramentas C/C++",      lambda: setup_c_cpp_tools()),
        ("Starship",               lambda: setup_starship(real_user, home)),
        ("FiraCode Nerd Font",     lambda: setup_firacode(real_user)),
        ("bat + eza + aliases",    lambda: setup_bat_eza(real_user, home)),
    ]

    for title, task_fn in tasks:
        try:
            task_fn()
        except subprocess.CalledProcessError as e:
            err(f"Falha em [{title}]: {e}")
        except KeyboardInterrupt:
            warn("\nInterrompido. Pulando para o próximo passo…")

    print_status_table()

    print(c(BOLD + GREEN, "  ✨  Setup concluído!"))
    print(c(DIM, "      Reinicie o terminal (ou faça logout/login) para aplicar todas as mudanças.\n"))


if __name__ == "__main__":
    main()
