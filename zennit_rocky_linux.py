#!/usr/bin/env python3
# =============================================================================
# post_install_rocky_java.py — Zennit-OS para Rocky Linux 9+
# Ambiente de desenvolvimento Java Backend com orientação a objetos
# =============================================================================

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Optional

# ─── Constantes ───────────────────────────────────────────────────────────────

LOGFILE = Path.home() / "post-install-rocky-java.log"

JAVA_VERSION   = "21-tem"
DOTNET_CHANNEL = "9.0"
TUNED_PROFILE  = "laptop-ac-powersave"


# ─── Enums ────────────────────────────────────────────────────────────────────

class StepStatus(Enum):
    PENDING  = auto()
    RUNNING  = auto()
    SUCCESS  = auto()
    WARNING  = auto()
    FAILED   = auto()
    SKIPPED  = auto()


# ─── Exceções customizadas ────────────────────────────────────────────────────

class PostInstallError(Exception):
    """Erro base do post-install."""

class CommandError(PostInstallError):
    """Erro ao executar um comando externo."""
    def __init__(self, cmd: list[str], returncode: int, stderr: str = "") -> None:
        self.cmd        = cmd
        self.returncode = returncode
        self.stderr     = stderr
        super().__init__(
            f"Comando falhou (exit {returncode}): {' '.join(cmd)}\n{stderr}"
        )

class NetworkError(PostInstallError):
    """Sem conectividade de rede."""

class PrivilegeError(PostInstallError):
    """Executado como root quando não deveria."""


# ─── Logger customizado ───────────────────────────────────────────────────────

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG:    "\033[0;36m",   # cyan
        logging.INFO:     "\033[0;32m",   # green
        logging.WARNING:  "\033[1;33m",   # yellow
        logging.ERROR:    "\033[0;31m",   # red
        logging.CRITICAL: "\033[1;31m",   # bold red
    }
    RESET = "\033[0m"
    ICONS = {
        logging.DEBUG:    "·",
        logging.INFO:     "✓",
        logging.WARNING:  "⚠",
        logging.ERROR:    "✗",
        logging.CRITICAL: "✗✗",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        icon  = self.ICONS.get(record.levelno, " ")
        msg   = super().format(record)
        return f"  {color}{icon}{self.RESET} {msg}"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("zennit")
    logger.setLevel(logging.DEBUG)

    # Console — colorido
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(ColorFormatter("%(message)s"))

    # Arquivo — sem cores
    fh = logging.FileHandler(LOGFILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


log = _build_logger()


# ─── Utilitário de execução ───────────────────────────────────────────────────

def run(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: Optional[dict] = None,
    cwd: Optional[Path] = None,
    shell: bool = False,
) -> subprocess.CompletedProcess:
    """Executa um comando com tratamento de erro padronizado."""
    merged_env = {**os.environ, **(env or {})}
    log.debug("Executando: %s", " ".join(cmd) if not shell else cmd)
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=True,
            env=merged_env,
            cwd=cwd,
            shell=shell,
        )
        return result
    except subprocess.CalledProcessError as exc:
        raise CommandError(
            cmd if isinstance(cmd, list) else [cmd],
            exc.returncode,
            exc.stderr or "",
        ) from exc
    except FileNotFoundError as exc:
        raise CommandError(
            cmd if isinstance(cmd, list) else [cmd],
            -1,
            str(exc),
        ) from exc


def run_shell(cmd: str, *, check: bool = True) -> subprocess.CompletedProcess:
    """Wrapper para comandos shell em string."""
    return run(cmd, shell=True, check=check)


def dnf(*packages: str, extra_flags: list[str] | None = None) -> None:
    """Instala pacotes via dnf."""
    flags   = extra_flags or []
    command = ["sudo", "dnf", "install", "-y", *flags, *packages]
    run(command)


def flatpak_install(*app_ids: str) -> None:
    """Instala aplicações via Flatpak."""
    run(["flatpak", "install", "-y", "flathub", *app_ids])


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def path_exists(p: str | Path) -> bool:
    return Path(p).exists()


# ─── Dataclass de resultado ───────────────────────────────────────────────────

@dataclass
class StepResult:
    name:    str
    status:  StepStatus = StepStatus.PENDING
    message: str        = ""
    errors:  list[str]  = field(default_factory=list)

    def mark_success(self, msg: str = "") -> None:
        self.status  = StepStatus.SUCCESS
        self.message = msg

    def mark_warning(self, msg: str) -> None:
        self.status = StepStatus.WARNING
        self.errors.append(msg)

    def mark_failed(self, msg: str) -> None:
        self.status = StepStatus.FAILED
        self.errors.append(msg)

    def mark_skipped(self, msg: str = "") -> None:
        self.status  = StepStatus.SKIPPED
        self.message = msg


# ─── Classe base dos Steps ────────────────────────────────────────────────────

class InstallStep(ABC):
    """Passo de instalação — cada subclasse representa uma etapa."""

    label: str = "Step"

    def __init__(self) -> None:
        self.result = StepResult(name=self.label)

    @abstractmethod
    def execute(self) -> None:
        """Lógica principal do passo."""

    def run(self) -> StepResult:
        self.result.status = StepStatus.RUNNING
        _header(self.label)
        try:
            self.execute()
            if self.result.status == StepStatus.RUNNING:
                self.result.mark_success()
        except CommandError as exc:
            self.result.mark_failed(str(exc))
            log.error("Erro de comando: %s", exc)
        except PostInstallError as exc:
            self.result.mark_failed(str(exc))
            log.error("Erro: %s", exc)
        except Exception as exc:  # noqa: BLE001
            self.result.mark_failed(f"Erro inesperado: {exc}")
            log.exception("Erro inesperado em '%s'", self.label)
        return self.result

    # helpers de logging
    def ok(self, msg: str)   -> None: log.info(msg)
    def warn(self, msg: str) -> None:
        log.warning(msg)
        self.result.mark_warning(msg)
    def info(self, msg: str) -> None: log.debug("  → %s", msg)


def _header(title: str) -> None:
    print(f"\n\033[1m\033[34m{'─' * 56}\033[0m")
    print(f"\033[1m\033[34m  {title}\033[0m")
    print(f"\033[1m\033[34m{'─' * 56}\033[0m")


# ═══════════════════════════════════════════════════════════════════════════════
# STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class PreFlightChecks(InstallStep):
    """Verifica pré-condições: não root, internet disponível."""

    label = "1/18 — Verificações iniciais"

    def execute(self) -> None:
        if os.geteuid() == 0:
            raise PrivilegeError("Não execute como root. Use seu usuário normal com sudo.")

        self.info("Verificando conectividade...")
        result = run(["ping", "-c", "1", "-W", "3", "8.8.8.8"], check=False)
        if result.returncode != 0:
            raise NetworkError("Sem acesso à internet. Verifique sua conexão.")

        self.ok("Usuário normal confirmado")
        self.ok("Conectividade OK")


# ──────────────────────────────────────────────────────────────────────────────

class RepositorySetup(InstallStep):
    """Configura EPEL, CRB, RPM Fusion e Flathub."""

    label = "2/18 — Repositórios (EPEL, CRB, RPM Fusion, Flathub)"

    def execute(self) -> None:
        self._setup_epel()
        self._setup_crb()
        self._setup_rpmfusion()
        self._setup_flathub()

    def _setup_epel(self) -> None:
        self.info("Instalando EPEL...")
        try:
            dnf("epel-release")
            self.ok("EPEL instalado")
        except CommandError:
            self.warn("EPEL pode já estar instalado")

    def _setup_crb(self) -> None:
        self.info("Habilitando CRB (CodeReady Builder)...")
        for flag in ("crb", "powertools"):
            result = run(
                ["sudo", "dnf", "config-manager", "--set-enabled", flag],
                check=False,
            )
            if result.returncode == 0:
                self.ok(f"CRB habilitado via '{flag}'")
                return
        self.warn("Não foi possível habilitar CRB/Powertools")

    def _setup_rpmfusion(self) -> None:
        self.info("Instalando RPM Fusion...")
        result = run(
            ["rpm", "-E", "%rhel"],
            capture=True,
            check=False,
        )
        rhel_ver = result.stdout.strip() if result.returncode == 0 else "9"

        for variant in ("free", "nonfree"):
            url = (
                f"https://mirrors.rpmfusion.org/{variant}/el/"
                f"rpmfusion-{variant}-release-{rhel_ver}.noarch.rpm"
            )
            try:
                dnf(url, extra_flags=["--nogpgcheck"])
                self.ok(f"RPM Fusion ({variant}) instalado")
            except CommandError:
                self.warn(f"RPM Fusion ({variant}) pode já estar instalado")

    def _setup_flathub(self) -> None:
        self.info("Configurando Flathub...")
        run([
            "flatpak", "remote-add", "--if-not-exists",
            "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo",
        ])
        self.ok("Flathub configurado")


# ──────────────────────────────────────────────────────────────────────────────

class SystemUpdate(InstallStep):
    """Atualização completa do sistema."""

    label = "3/18 — Atualização do sistema"

    def execute(self) -> None:
        self.info("Executando dnf upgrade --refresh (pode demorar)...")
        run(["sudo", "dnf", "upgrade", "-y", "--refresh"])
        self.ok("Sistema atualizado")


# ──────────────────────────────────────────────────────────────────────────────

class BaseToolsInstaller(InstallStep):
    """Ferramentas base de CLI, ZSH, git e utilitários."""

    label = "4/18 — Ferramentas base (CLI, ZSH, git)"

    PACKAGES = [
        "htop", "btop", "bat", "eza", "fd-find", "ripgrep", "fzf", "zoxide",
        "tmux", "ncdu", "neofetch", "stow", "git", "zsh",
        "curl", "wget", "unzip", "jq", "make", "gcc", "gcc-c++",
        "gnome-tweaks", "dconf-editor",
        "firewalld", "rclone",
        "earlyoom", "irqbalance", "preload",
        "neovim", "python3", "python3-pip",
    ]

    def execute(self) -> None:
        self._install_packages()
        self._enable_services()
        self._set_zsh_default()
        self._install_starship()

    def _install_packages(self) -> None:
        self.info("Instalando pacotes base...")
        try:
            dnf(*self.PACKAGES)
            self.ok("Pacotes base instalados")
        except CommandError as exc:
            self.warn(f"Alguns pacotes falharam: {exc}")

    def _enable_services(self) -> None:
        for service in ("earlyoom", "irqbalance", "preload"):
            try:
                run(["sudo", "systemctl", "enable", "--now", service])
                self.ok(f"{service} ativado")
            except CommandError:
                self.warn(f"Falha ao ativar {service}")

    def _set_zsh_default(self) -> None:
        zsh_path = shutil.which("zsh")
        if not zsh_path:
            self.warn("ZSH não encontrado no PATH")
            return
        result = run(
            ["getent", "passwd", os.environ["USER"]],
            capture=True, check=False,
        )
        current_shell = result.stdout.strip().split(":")[-1] if result.returncode == 0 else ""
        if zsh_path not in current_shell:
            try:
                run(["sudo", "chsh", "-s", zsh_path, os.environ["USER"]])
                self.ok("ZSH definido como shell padrão")
            except CommandError as exc:
                self.warn(f"Não foi possível definir ZSH: {exc}")
        else:
            self.ok("ZSH já é o shell padrão")

    def _install_starship(self) -> None:
        if command_exists("starship"):
            self.ok("Starship já instalado")
            return
        self.info("Instalando Starship...")
        try:
            run_shell("curl -sS https://starship.rs/install.sh | sh -s -- --yes")
            self.ok("Starship instalado")
        except CommandError as exc:
            self.warn(f"Starship falhou: {exc}")


# ──────────────────────────────────────────────────────────────────────────────

class KernelTuning(InstallStep):
    """Parâmetros sysctl de performance, THP, NVMe scheduler, fstrim."""

    label = "5/18 — Tuning de kernel e I/O (sysctl, THP, NVMe)"

    SYSCTL_CONF = Path("/etc/sysctl.d/99-zennit-java-dev.conf")

    SYSCTL_PARAMS = textwrap.dedent("""\
        # Zennit-OS — Java Backend Dev tuning
        vm.swappiness = 10
        vm.vfs_cache_pressure = 50
        vm.dirty_ratio = 10
        vm.dirty_background_ratio = 5
        kernel.nmi_watchdog = 0
        net.core.netdev_max_backlog = 16384
        net.core.somaxconn = 8192
        net.ipv4.tcp_fastopen = 3
        net.ipv4.tcp_slow_start_after_idle = 0
        # Aumenta limite de watchers para IDEs (IntelliJ, VS Code)
        fs.inotify.max_user_watches = 524288
        # Aumenta limite de aberturas de arquivo para servidores Java
        fs.file-max = 2097152
        # Segurança adicional
        kernel.kptr_restrict = 2
        kernel.dmesg_restrict = 1
    """)

    THP_TMPFILE = Path("/etc/tmpfiles.d/thp.conf")
    THP_CONTENT = "w /sys/kernel/mm/transparent_hugepage/enabled - - - - madvise\n"
    UDEV_RULE = Path("/etc/udev/rules.d/60-nvme-scheduler.rules")
    UDEV_CONTENT = 'ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="kyber"\n'

    def execute(self) -> None:
        self._write_sysctl()
        self._apply_sysctl()
        self._setup_transparent_hugepage()
        self._setup_nvme_scheduler()
        self._setup_fstrim()
        self._setup_limits()

    def _write_sysctl(self) -> None:
        self.info("Escrevendo parâmetros sysctl...")
        run_shell(f"echo '{self.SYSCTL_PARAMS}' | sudo tee {self.SYSCTL_CONF} > /dev/null")
        self.ok(f"Arquivo {self.SYSCTL_CONF} criado")

    def _apply_sysctl(self) -> None:
        try:
            run(["sudo", "sysctl", "--system"])
            self.ok("Parâmetros de kernel aplicados")
        except CommandError as exc:
            self.warn(f"sysctl --system falhou: {exc}")

    def _setup_transparent_hugepage(self) -> None:
        self.info("Configurando Transparent HugePage para madvise (JVM)...")
        run_shell("echo madvise | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null")
        run_shell(f"echo '{self.THP_CONTENT}' | sudo tee {self.THP_TMPFILE} > /dev/null")
        self.ok("Transparent HugePage configurado para madvise (JVM)")

    def _setup_nvme_scheduler(self) -> None:
        self.info("Verificando scheduler NVMe...")
        nvme_dev = None
        for dev in Path("/sys/block").iterdir():
            if dev.name.startswith("nvme"):
                nvme_dev = dev.name
                break
        if not nvme_dev:
            self.info("Nenhum dispositivo NVMe encontrado — pulando")
            return

        sched_file = f"/sys/block/{nvme_dev}/queue/scheduler"
        try:
            current = Path(sched_file).read_text().strip()
        except Exception:
            self.warn("Não foi possível ler scheduler NVMe")
            return

        if "[none]" in current or "[kyber]" in current:
            self.ok(f"Scheduler {nvme_dev} já otimizado: {current}")
        else:
            run_shell(f"echo kyber | sudo tee {sched_file} > /dev/null")
            self.ok(f"Scheduler {nvme_dev} alterado para kyber")

        run_shell(f"echo '{self.UDEV_CONTENT}' | sudo tee {self.UDEV_RULE} > /dev/null")
        self.ok("Regra udev para scheduler NVMe criada")

    def _setup_fstrim(self) -> None:
        self.info("Ativando fstrim.timer para TRIM semanal...")
        run(["sudo", "systemctl", "enable", "--now", "fstrim.timer"])
        self.ok("fstrim.timer ativado")

    def _setup_limits(self) -> None:
        limits_entry = (
            "\n# Zennit-OS — limites para Java\n"
            "* soft nofile 65536\n"
            "* hard nofile 65536\n"
        )
        limits_path = Path("/etc/security/limits.d/99-zennit-java.conf")
        try:
            run_shell(f"echo '{limits_entry}' | sudo tee {limits_path} > /dev/null")
            self.ok("Limites de arquivo para JVM configurados")
        except CommandError as exc:
            self.warn(f"Limites de arquivo falharam: {exc}")


# ──────────────────────────────────────────────────────────────────────────────

class ZramSetup(InstallStep):
    """Configura ZRAM como swap comprimido em RAM (50% da RAM, zstd)."""

    label = "6/18 — ZRAM (swap comprimido em RAM)"

    ZRAM_CONF = Path("/etc/systemd/zram-generator.conf")

    def execute(self) -> None:
        self._install_zram_generator()
        self._configure_zram()
        self._check_disk_swap()

    def _install_zram_generator(self) -> None:
        self.info("Instalando zram-generator...")
        try:
            dnf("zram-generator")
            self.ok("zram-generator instalado")
        except CommandError as exc:
            self.warn(f"zram-generator falhou: {exc}")

    def _configure_zram(self) -> None:
        if self.ZRAM_CONF.exists():
            self.ok("Configuração ZRAM já existe")
            return
        self.info("Criando configuração do ZRAM...")
        config = textwrap.dedent("""\
            [zram0]
            zram-size = ram / 2
            compression-algorithm = zstd
            swap-priority = 100
        """)
        run_shell(f"echo '{config}' | sudo tee {self.ZRAM_CONF} > /dev/null")
        self.ok("ZRAM configurado (50% RAM, zstd, prioridade 100)")
        run(["sudo", "systemctl", "daemon-reload"])

    def _check_disk_swap(self) -> None:
        result = run(["swapon", "--show"], capture=True, check=False)
        if result.stdout.strip():
            if any(("swapfile" in line or "/dev/" in line) for line in result.stdout.splitlines()):
                self.warn("Swap em disco detectado. Considere removê-lo para priorizar ZRAM.")
                self.info("Execute: sudo swapoff <swap> && sudo rm <swapfile>")


# ──────────────────────────────────────────────────────────────────────────────

class CpuPowerManagement(InstallStep):
    """CPU: amd_pstate, tuned, auto-cpufreq, desativa power-profiles-daemon."""

    label = "7/18 — CPU: AMD pstate + tuned + auto-cpufreq"

    def execute(self) -> None:
        self._configure_amd_pstate()
        self._setup_tuned()
        self._setup_auto_cpufreq()
        self._disable_power_profiles_daemon()

    def _configure_amd_pstate(self) -> None:
        result = run_shell(
            "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver 2>/dev/null || echo unknown",
            capture=True, check=False,
        )
        driver = result.stdout.strip() if result.returncode == 0 else "unknown"
        if driver == "amd_pstate_epp":
            self.ok(f"amd_pstate_epp já ativo ({driver})")
            return

        self.info(f"Driver atual: {driver} — tentando ativar amd_pstate=active")
        grub_file = Path("/etc/default/grub")
        if not grub_file.exists():
            self.warn("Arquivo /etc/default/grub não encontrado. Adicione amd_pstate=active manualmente.")
            return

        content = grub_file.read_text()
        if "amd_pstate=active" in content:
            self.ok("amd_pstate=active já presente no GRUB")
            return

        self.info("Adicionando amd_pstate=active ao GRUB...")
        new_content = content.replace(
            'GRUB_CMDLINE_LINUX="', 'GRUB_CMDLINE_LINUX="amd_pstate=active '
        )
        run_shell(f"echo '{new_content}' | sudo tee {grub_file} > /dev/null")
        run(["sudo", "grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"])
        self.ok("amd_pstate=active adicionado ao GRUB (efeito após reboot)")

    def _setup_tuned(self) -> None:
        if not command_exists("tuned-adm"):
            self.info("Instalando tuned...")
            dnf("tuned", "powertop")
        run(["sudo", "systemctl", "enable", "--now", "tuned"])
        run(["sudo", "tuned-adm", "profile", TUNED_PROFILE])
        self.ok(f"tuned ativo com perfil '{TUNED_PROFILE}'")

    def _setup_auto_cpufreq(self) -> None:
        if command_exists("auto-cpufreq"):
            self.ok("auto-cpufreq já instalado")
        else:
            self.info("Instalando auto-cpufreq...")
            try:
                dnf("auto-cpufreq")
                self.ok("auto-cpufreq instalado via dnf")
            except CommandError:
                self.warn("auto-cpufreq não disponível via dnf. Instale manualmente se desejar.")
                return

        result = run(["sudo", "auto-cpufreq", "--install"], check=False)
        if result.returncode == 0:
            self.ok("auto-cpufreq instalado como serviço")
        else:
            self.warn("auto-cpufreq --install pode já estar configurado")

    def _disable_power_profiles_daemon(self) -> None:
        result = run(
            ["sudo", "systemctl", "disable", "--now", "power-profiles-daemon"],
            check=False,
        )
        if result.returncode == 0:
            self.ok("power-profiles-daemon desativado")
        else:
            self.info("power-profiles-daemon já estava desativado")


# ──────────────────────────────────────────────────────────────────────────────

class PowertopAutoTune(InstallStep):
    """Cria e ativa serviço powertop --auto-tune no boot."""

    label = "8/18 — Energia: powertop auto-tune"

    SERVICE_FILE = Path("/etc/systemd/system/powertop.service")
    SERVICE_CONTENT = textwrap.dedent("""\
        [Unit]
        Description=PowerTop auto-tune — AMD notebook power savings
        After=multi-user.target

        [Service]
        Type=oneshot
        ExecStart=/usr/sbin/powertop --auto-tune
        RemainAfterExit=yes

        [Install]
        WantedBy=multi-user.target
    """)

    def execute(self) -> None:
        if not command_exists("powertop"):
            self.warn("powertop não encontrado. Instale o pacote primeiro.")
            return

        self.info("Criando serviço powertop...")
        run_shell(f"echo '{self.SERVICE_CONTENT}' | sudo tee {self.SERVICE_FILE} > /dev/null")
        run(["sudo", "systemctl", "daemon-reload"])
        run(["sudo", "systemctl", "enable", "--now", "powertop.service"])
        self.ok("powertop.service criado e ativado")


# ──────────────────────────────────────────────────────────────────────────────

class JavaBackendInstaller(InstallStep):
    """Instala o ecossistema Java Backend: SDKMan, Java, Maven, Gradle, Quarkus CLI."""

    label = "9/18 — Java Backend (SDKMan, Java 21, Maven, Gradle, Quarkus)"

    SDKMAN_INIT = Path.home() / ".sdkman" / "bin" / "sdkman-init.sh"

    SDK_PACKAGES = [
        ("java",   JAVA_VERSION),
        ("java",   "17-tem"),
        ("maven",  ""),
        ("gradle", ""),
        ("quarkus",""),
    ]

    def execute(self) -> None:
        self._install_deps()
        self._install_sdkman()
        self._install_sdk_packages()
        self._install_build_tools_native()

    def _install_deps(self) -> None:
        self.info("Instalando dependências nativas...")
        try:
            dnf(
                "zip", "unzip", "curl", "sed", "which",
                "fontconfig", "freetype", "libstdc++",
            )
            self.ok("Dependências nativas OK")
        except CommandError as exc:
            self.warn(f"Algumas dependências falharam: {exc}")

    def _install_sdkman(self) -> None:
        if self.SDKMAN_INIT.exists():
            self.ok("SDKMan já instalado")
            return
        self.info("Instalando SDKMan...")
        try:
            run_shell('curl -s "https://get.sdkman.io" | bash -s -- -y')
            self.ok("SDKMan instalado")
        except CommandError as exc:
            self.warn(f"SDKMan falhou: {exc}")

    def _sdk_cmd(self, *args: str) -> bool:
        if not self.SDKMAN_INIT.exists():
            return False
        init = str(self.SDKMAN_INIT)
        cmd  = f'source "{init}" && sdk {" ".join(args)}'
        result = run_shell(cmd, check=False)
        return result.returncode == 0

    def _install_sdk_packages(self) -> None:
        for pkg, version in self.SDK_PACKAGES:
            label = f"{pkg} {version}".strip()
            self.info(f"Instalando {label} via SDKMan...")
            ok = self._sdk_cmd("install", pkg, version) if version else self._sdk_cmd("install", pkg)
            if ok:
                self.ok(f"{label} instalado")
            else:
                self.warn(f"{label} pode já estar instalado ou falhou")

        self._sdk_cmd("default", "java", JAVA_VERSION)
        self.ok(f"Java {JAVA_VERSION} definido como padrão")

    def _install_build_tools_native(self) -> None:
        if not command_exists("mvn"):
            self.warn("Maven não encontrado no PATH após SDKMan. Verifique sua sessão.")
        else:
            self.ok("Maven disponível no PATH")


# ──────────────────────────────────────────────────────────────────────────────

class DockerInstaller(InstallStep):
    """Instala Docker CE e configura firewall."""

    label = "10/18 — Docker CE + Compose"

    def execute(self) -> None:
        if command_exists("docker"):
            self.ok("Docker já instalado")
        else:
            self._install_docker()
        self._configure_firewall()

    def _install_docker(self) -> None:
        self.info("Adicionando repositório Docker...")
        try:
            run([
                "sudo", "dnf", "config-manager", "--add-repo",
                "https://download.docker.com/linux/rhel/docker-ce.repo",
            ])
            dnf(
                "docker-ce", "docker-ce-cli",
                "containerd.io", "docker-compose-plugin",
            )
            run(["sudo", "systemctl", "enable", "--now", "docker"])

            user = os.environ.get("USER", "")
            if user:
                run(["sudo", "usermod", "-aG", "docker", user])
                self.ok(f"Usuário '{user}' adicionado ao grupo docker")

            self.ok("Docker CE instalado (reinicie a sessão para efeito do grupo)")
        except CommandError as exc:
            self.warn(f"Docker falhou: {exc}")

    def _configure_firewall(self) -> None:
        self.info("Configurando firewall para Docker...")
        cmds = [
            ["sudo", "firewall-cmd", "--permanent",
             "--zone=trusted", "--add-interface=docker0"],
            ["sudo", "firewall-cmd", "--reload"],
        ]
        for cmd in cmds:
            result = run(cmd, check=False)
            if result.returncode != 0:
                self.warn(f"Firewall: {' '.join(cmd)} falhou (pode ser normal)")
        self.ok("Firewall configurado para Docker")


# ──────────────────────────────────────────────────────────────────────────────

class DatabaseToolsInstaller(InstallStep):
    """Instala ferramentas de banco de dados: DBeaver, clientes CLI."""

    label = "11/18 — Ferramentas de banco de dados"

    CLI_PACKAGES = [
        "postgresql",
        "mysql",
        "redis",
        "sqlite",
    ]

    def execute(self) -> None:
        self._install_cli_clients()
        self._install_dbeaver()

    def _install_cli_clients(self) -> None:
        self.info("Instalando clientes CLI de banco de dados...")
        for pkg in self.CLI_PACKAGES:
            try:
                dnf(pkg)
                self.ok(f"{pkg} instalado")
            except CommandError:
                self.warn(f"{pkg} não disponível — verifique o repositório")

    def _install_dbeaver(self) -> None:
        self.info("Instalando DBeaver Community via Flatpak...")
        try:
            flatpak_install("io.dbeaver.DBeaverCommunity")
            self.ok("DBeaver instalado")
        except CommandError as exc:
            self.warn(f"DBeaver falhou: {exc}")


# ──────────────────────────────────────────────────────────────────────────────

class IdeToolsInstaller(InstallStep):
    """Instala IDEs e ferramentas de desenvolvimento: VS Code, IntelliJ, etc."""

    label = "12/18 — IDEs e ferramentas de desenvolvimento"

    FLATPAK_TOOLS = [
        ("com.visualstudio.code",           "VS Code"),
        ("com.usebruno.Bruno",              "Bruno (API Client)"),
        ("org.onlyoffice.desktopeditors",   "OnlyOffice"),
    ]

    def execute(self) -> None:
        self._install_flatpak_tools()
        self._install_intellij()
        self._install_uv()

    def _install_flatpak_tools(self) -> None:
        for app_id, name in self.FLATPAK_TOOLS:
            self.info(f"Instalando {name}...")
            try:
                flatpak_install(app_id)
                self.ok(f"{name} instalado")
            except CommandError as exc:
                self.warn(f"{name} falhou: {exc}")

    def _install_intellij(self) -> None:
        self.info("Instalando IntelliJ IDEA Community...")
        try:
            flatpak_install("com.jetbrains.IntelliJ-IDEA-Community")
            self.ok("IntelliJ IDEA Community instalado")
        except CommandError:
            self.warn(
                "IntelliJ Flatpak falhou. Instale manualmente em: "
                "https://www.jetbrains.com/idea/download/"
            )

    def _install_uv(self) -> None:
        if command_exists("uv"):
            self.ok("uv já instalado")
            return
        self.info("Instalando uv (Python package manager)...")
        try:
            run_shell("curl -LsSf https://astral.sh/uv/install.sh | sh")
            self.ok("uv instalado")
        except CommandError as exc:
            self.warn(f"uv falhou: {exc}")


# ──────────────────────────────────────────────────────────────────────────────

class FontInstaller(InstallStep):
    """Instala Nerd Fonts (FiraCode, JetBrainsMono) e MS Core Fonts."""

    label = "13/18 — Fontes (Nerd Fonts + MS Core)"

    FONT_DIR = Path.home() / ".local" / "share" / "fonts"

    NERD_FONTS = [
        ("FiraCode",      "FiraCodeNerdFont-Regular.ttf"),
        ("JetBrainsMono", "JetBrainsMonoNerdFont-Regular.ttf"),
    ]

    def execute(self) -> None:
        self.FONT_DIR.mkdir(parents=True, exist_ok=True)
        self._install_ms_core()
        for font_name, check_file in self.NERD_FONTS:
            self._install_nerd_font(font_name, check_file)
        self._refresh_font_cache()

    def _install_ms_core(self) -> None:
        self.info("Instalando MS Core Fonts...")
        try:
            dnf("curl", "cabextract", "xorg-x11-font-utils", "fontconfig")
            run_shell(
                "sudo rpm -i --force "
                "https://downloads.sourceforge.net/project/mscorefonts2/rpms/"
                "msttcore-fonts-installer-2.6-1.noarch.rpm 2>/dev/null || true"
            )
            self.ok("MS Core Fonts instaladas")
        except CommandError as exc:
            self.warn(f"MS Core Fonts falhou: {exc}")

    def _install_nerd_font(self, name: str, check_file: str) -> None:
        dest = self.FONT_DIR / name
        if (dest / check_file).exists():
            self.ok(f"{name} Nerd Font já presente")
            return
        self.info(f"Baixando {name} Nerd Font...")
        tmp_zip = Path(f"/tmp/{name}.zip")
        try:
            run([
                "curl", "-fLo", str(tmp_zip),
                f"https://github.com/ryanoasis/nerd-fonts/releases/latest/download/{name}.zip",
            ])
            dest.mkdir(parents=True, exist_ok=True)
            run(["unzip", "-q", str(tmp_zip), "-d", str(dest)])
            tmp_zip.unlink(missing_ok=True)
            self.ok(f"{name} Nerd Font instalada")
        except CommandError as exc:
            self.warn(f"Falha ao baixar {name}: {exc}")
            tmp_zip.unlink(missing_ok=True)

    def _refresh_font_cache(self) -> None:
        try:
            run(["fc-cache", "-fv", str(self.FONT_DIR)],
                capture=True, check=False)
            self.ok("Cache de fontes atualizado")
        except CommandError as exc:
            self.warn(f"fc-cache falhou: {exc}")


# ──────────────────────────────────────────────────────────────────────────────

class GnomeThemeSetup(InstallStep):
    """Tema Fluent Blue Dark + ícones + Folder Color."""

    label = "14/18 — Tema Fluent Blue Dark + ícones"

    THEME_DIR = Path.home() / ".local" / "share" / "themes"
    ICON_DIR  = Path.home() / ".local" / "share" / "icons"

    def execute(self) -> None:
        self._install_dependencies()
        self._install_fluent_gtk_theme()
        self._install_fluent_icon_theme()
        self._install_folder_color()
        self._apply_gnome_settings()
        self._apply_flatpak_overrides()

    def _install_dependencies(self) -> None:
        self.info("Instalando dependências para temas...")
        try:
            dnf("git", "unzip", "python3-setuptools", "python3-pip")
            self.ok("Dependências de tema instaladas")
        except CommandError as exc:
            self.warn(f"Algumas dependências podem já estar presentes: {exc}")

    def _install_fluent_gtk_theme(self) -> None:
        if (self.THEME_DIR / "Fluent-Dark").exists():
            self.ok("Fluent GTK Theme já presente")
            return
        self.info("Clonando e instalando Fluent GTK Theme...")
        tmp_dir = Path("/tmp/fluent-gtk-theme")
        try:
            run(["git", "clone", "--depth=1",
                 "https://github.com/vinceliuice/Fluent-gtk-theme", str(tmp_dir)])
            run_shell(
                f"./install.sh --dest {self.THEME_DIR} --name Fluent --theme default "
                "--color dark --size standard --tweaks blur round --icon fedora --libadwaita",
                cwd=tmp_dir,
            )
            self.ok("Fluent GTK Theme instalado")
        except CommandError as exc:
            self.warn(f"Fluent GTK Theme falhou: {exc}")

    def _install_fluent_icon_theme(self) -> None:
        if (self.ICON_DIR / "Fluent-dark").exists():
            self.ok("Fluent Icon Theme já presente")
            return
        self.info("Clonando e instalando Fluent Icon Theme...")
        tmp_dir = Path("/tmp/fluent-icon-theme")
        try:
            run(["git", "clone", "--depth=1",
                 "https://github.com/vinceliuice/Fluent-icon-theme", str(tmp_dir)])
            run_shell(
                f"./install.sh --dest {self.ICON_DIR} --theme default --color dark",
                cwd=tmp_dir,
            )
            self.ok("Fluent Icon Theme instalado")
        except CommandError as exc:
            self.warn(f"Fluent Icon Theme falhou: {exc}")

    def _install_folder_color(self) -> None:
        if command_exists("folder-color"):
            self.ok("Folder Color já instalado")
            return
        self.info("Instalando Folder Color (pastas coloridas)...")
        tmp_dir = Path("/tmp/folder-color")
        try:
            run(["git", "clone", "--depth=1",
                 "https://github.com/costales/folder-color", str(tmp_dir)])
            run(["python3", "setup.py", "install", "--prefix", str(Path.home() / ".local")],
                cwd=tmp_dir, check=False)
            # Reiniciar Nautilus se estiver rodando
            run(["nautilus", "-q"], check=False)
            self.ok("Folder Color instalado")
        except CommandError as exc:
            self.warn(f"Folder Color falhou: {exc}")

    def _apply_gnome_settings(self) -> None:
        self.info("Aplicando configurações GNOME...")
        settings = [
            ("org.gnome.desktop.interface", "gtk-theme", "Fluent-Dark"),
            ("org.gnome.desktop.interface", "icon-theme", "Fluent-dark"),
            ("org.gnome.desktop.interface", "color-scheme", "prefer-dark"),
            ("org.gnome.desktop.wm.preferences", "theme", "Fluent-Dark"),
            ("org.gnome.desktop.interface", "monospace-font-name", "FiraCode Nerd Font 11"),
        ]
        for schema, key, value in settings:
            run(["gsettings", "set", schema, key, value], check=False)
        self.ok("Tema e fontes aplicados")

    def _apply_flatpak_overrides(self) -> None:
        self.info("Configurando Flatpak para enxergar os temas...")
        run(["sudo", "flatpak", "override", "--filesystem=" + str(self.THEME_DIR)], check=False)
        run(["sudo", "flatpak", "override", "--filesystem=" + str(self.ICON_DIR)], check=False)
        run(["sudo", "flatpak", "override", "--env=GTK_THEME=Fluent-Dark"], check=False)
        run(["sudo", "flatpak", "override", "--env=ICON_THEME=Fluent-dark"], check=False)
        self.ok("Overrides Flatpak aplicados")


# ──────────────────────────────────────────────────────────────────────────────

class WallpaperSetup(InstallStep):
    """Wallpaper dinâmico Firewatch (nativo GNOME)."""

    label = "15/18 — Wallpaper Firewatch Dinâmico"

    WP_DIR   = Path.home() / ".local" / "share" / "backgrounds" / "firewatch"
    PROP_DIR = Path.home() / ".local" / "share" / "gnome-background-properties"

    IMAGES = [f"https://raw.githubusercontent.com/adi1090x/dynamic-wallpaper/master/images/firewatch/firewatch_{i}.jpg" for i in range(1, 5)]

    def execute(self) -> None:
        self._create_directories()
        self._download_images()
        self._create_wallpaper_xml()
        self._create_properties_xml()

    def _create_directories(self) -> None:
        self.WP_DIR.mkdir(parents=True, exist_ok=True)
        self.PROP_DIR.mkdir(parents=True, exist_ok=True)
        self.ok("Diretórios de wallpaper criados")

    def _download_images(self) -> None:
        self.info("Baixando imagens do Firewatch...")
        for url in self.IMAGES:
            filename = Path(url).name
            dest = self.WP_DIR / filename
            if dest.exists():
                continue
            try:
                run(["curl", "-fLo", str(dest), url])
                self.ok(f"{filename} baixada")
            except CommandError as exc:
                self.warn(f"Falha ao baixar {filename}: {exc}")

    def _create_wallpaper_xml(self) -> None:
        xml_content = textwrap.dedent(f"""\
            <background>
              <starttime>
                <year>2026</year><month>01</month><day>01</day>
                <hour>00</hour><minute>00</minute><second>00</second>
              </starttime>
              <static><duration>21600.0</duration><file>{self.WP_DIR}/firewatch_4.jpg</file></static>
              <transition><duration>3600.0</duration><from>{self.WP_DIR}/firewatch_4.jpg</from><to>{self.WP_DIR}/firewatch_1.jpg</to></transition>
              <static><duration>32400.0</duration><file>{self.WP_DIR}/firewatch_1.jpg</file></static>
              <transition><duration>3600.0</duration><from>{self.WP_DIR}/firewatch_1.jpg</from><to>{self.WP_DIR}/firewatch_2.jpg</to></transition>
              <static><duration>3600.0</duration><file>{self.WP_DIR}/firewatch_2.jpg</file></static>
              <transition><duration>3600.0</duration><from>{self.WP_DIR}/firewatch_2.jpg</from><to>{self.WP_DIR}/firewatch_3.jpg</to></transition>
              <static><duration>10800.0</duration><file>{self.WP_DIR}/firewatch_3.jpg</file></static>
              <transition><duration>3600.0</duration><from>{self.WP_DIR}/firewatch_3.jpg</from><to>{self.WP_DIR}/firewatch_4.jpg</to></transition>
            </background>
        """)
        xml_file = self.WP_DIR / "firewatch.xml"
        xml_file.write_text(xml_content)
        self.ok("firewatch.xml criado")

    def _create_properties_xml(self) -> None:
        prop_content = textwrap.dedent(f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
            <wallpapers>
              <wallpaper deleted="false">
                <name>Firewatch Dinâmico</name>
                <filename>{self.WP_DIR}/firewatch.xml</filename>
                <options>zoom</options>
              </wallpaper>
            </wallpapers>
        """)
        prop_file = self.PROP_DIR / "firewatch.xml"
        prop_file.write_text(prop_content)
        self.ok("Propriedades do wallpaper registradas (aparecerá nas configurações)")


# ──────────────────────────────────────────────────────────────────────────────

class GnomeExtensionsSetup(InstallStep):
    """Instala e habilita extensões GNOME via API."""

    label = "16/18 — Extensões GNOME"

    EXT_DIR = Path.home() / ".local" / "share" / "gnome-shell" / "extensions"
    EXTENSIONS = [
        ("dash-to-dock@micxgx.gmail.com",              "dash-to-dock"),
        ("appindicatorsupport@rgcjonas.gmail.com",      "appindicator"),
        ("caffeine@patapon.info",                       "caffeine"),
        ("compiz-alike-magic-lamp-effect@hermes81.github.com", "magic-lamp"),
        ("add-to-desktop@bobsilverberg",                "add-to-desktop"),
        ("ding@rastersoft.com",                         "desktop-icons"),
        ("blur-my-shell@aunetx",                        "blur-my-shell"),
    ]

    def execute(self) -> None:
        self._install_deps()
        self._install_extensions()
        self._enable_extensions()

    def _install_deps(self) -> None:
        try:
            dnf("unzip", "jq", "gnome-shell-extension-common")
        except CommandError:
            self.warn("Algumas dependências de extensão já podem estar presentes")

    def _get_gnome_shell_version(self) -> str:
        result = run(["gnome-shell", "--version"], capture=True, check=False)
        if result.returncode == 0:
            # output: "GNOME Shell 40.4" — extrair número
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                return parts[2].split(".")[0]
        # fallback: tentar via pkg-config ou retornar valor padrão
        self.warn("Não foi possível detectar versão do GNOME Shell, usando fallback 40")
        return "40"

    def _install_extensions(self) -> None:
        self.EXT_DIR.mkdir(parents=True, exist_ok=True)
        shell_ver = self._get_gnome_shell_version()

        for uuid, _ in self.EXTENSIONS:
            if (self.EXT_DIR / uuid).exists():
                self.ok(f"Extensão {uuid} já instalada")
                continue

            self.info(f"Instalando extensão: {uuid}...")
            # Tentar obter URL de download via API
            try:
                # Primeiro, consulta com search
                query_url = f"https://extensions.gnome.org/extension-query/?search={uuid.split('@')[0]}"
                result = run(["curl", "-s", query_url], capture=True, check=False)
                download_url = None
                if result.returncode == 0:
                    import json
                    data = json.loads(result.stdout)
                    for ext in data.get("extensions", []):
                        if ext.get("uuid") == uuid:
                            version_map = ext.get("shell_version_map", {})
                            download_url = version_map.get(shell_ver, {}).get("download_url")
                            if not download_url:
                                # fallback: pegar o primeiro disponível
                                for ver, info in version_map.items():
                                    download_url = info.get("download_url")
                                    break
                            break
                if not download_url:
                    # Tentar endpoint de info direta
                    info_result = run(
                        ["curl", "-s", f"https://extensions.gnome.org/extension-info/?uuid={uuid}"],
                        capture=True, check=False,
                    )
                    if info_result.returncode == 0:
                        ext_info = json.loads(info_result.stdout)
                        download_url = ext_info.get("download_url")

                if download_url and download_url != "null":
                    zip_path = f"/tmp/{uuid}.zip"
                    run(["curl", "-sL", f"https://extensions.gnome.org{download_url}", "-o", zip_path])
                    dest_dir = self.EXT_DIR / uuid
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    run(["unzip", "-q", zip_path, "-d", str(dest_dir)])
                    Path(zip_path).unlink(missing_ok=True)
                    self.ok(f"Extensão {uuid} instalada")
                else:
                    self.warn(f"URL de download não encontrada para {uuid}")
            except Exception as exc:
                self.warn(f"Falha ao instalar {uuid}: {exc}")

    def _enable_extensions(self) -> None:
        uuids = [uuid for uuid, _ in self.EXTENSIONS]
        enabled_list = str(uuids).replace("'", '"')
        run(["gsettings", "set", "org.gnome.shell", "enabled-extensions", enabled_list], check=False)
        self.ok("Extensões habilitadas no GNOME")


# ──────────────────────────────────────────────────────────────────────────────

class DotfilesSetup(InstallStep):
    """Clona e aplica dotfiles via GNU Stow."""

    label = "17/18 — Dotfiles e ZSH config"

    DOTFILES_REPO = "https://github.com/Symos001/Symos-dotfiles.git"
    DOTFILES_DIR  = Path.home() / ".dotfiles"
    ZSHRC         = Path.home() / ".zshrc"
    TPM_DIR       = Path.home() / ".tmux" / "plugins" / "tpm"

    ZSHRC_BLOCK = textwrap.dedent("""\

        # zennit-os — Java Backend paths
        export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$HOME/.bun/bin"
        export PATH="$HOME/.dotnet:$HOME/.dotnet/tools:$PATH"
        export JAVA_HOME="$HOME/.sdkman/candidates/java/current"
        export PATH="$JAVA_HOME/bin:$PATH"

        [[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

        eval "$(fnm env 2>/dev/null)"
        eval "$(starship init zsh 2>/dev/null)"
        eval "$(zoxide init zsh 2>/dev/null)"
    """)

    def execute(self) -> None:
        self._clone_or_update()
        self._stow_packages()
        self._setup_tmux_plugins()
        self._patch_zshrc()

    def _clone_or_update(self) -> None:
        if (self.DOTFILES_DIR / ".git").exists():
            self.info("Atualizando dotfiles...")
            result = run(
                ["git", "-C", str(self.DOTFILES_DIR),
                 "pull", "--rebase", "--autostash"],
                check=False,
            )
            if result.returncode != 0:
                self.warn("Atualização do repositório falhou — continuando com versão local")
        else:
            self.info("Clonando dotfiles...")
            try:
                run([
                    "git", "clone", "--recurse-submodules",
                    self.DOTFILES_REPO, str(self.DOTFILES_DIR),
                ])
                self.ok("Dotfiles clonados")
            except CommandError as exc:
                self.warn(f"Clone de dotfiles falhou: {exc}")
                return

    def _stow_packages(self) -> None:
        if not self.DOTFILES_DIR.exists():
            self.warn("Diretório de dotfiles ausente — stow ignorado")
            return

        if self.ZSHRC.exists() and not self.ZSHRC.is_symlink():
            ts  = datetime.now().strftime("%Y%m%d-%H%M%S")
            bak = self.ZSHRC.with_suffix(f".bak.{ts}")
            self.ZSHRC.rename(bak)
            self.info(f".zshrc existente salvo em {bak}")

        for pkg_dir in sorted(self.DOTFILES_DIR.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
                continue
            result = run(
                ["stow", "--restow", "--target", str(Path.home()), pkg_dir.name],
                cwd=self.DOTFILES_DIR,
                check=False,
            )
            if result.returncode == 0:
                self.ok(f"stow: {pkg_dir.name}")
            else:
                self.warn(f"stow: {pkg_dir.name} falhou")

    def _setup_tmux_plugins(self) -> None:
        if not self.TPM_DIR.exists():
            try:
                run(["git", "clone",
                     "https://github.com/tmux-plugins/tpm",
                     str(self.TPM_DIR)])
                self.ok("TPM (Tmux Plugin Manager) instalado")
            except CommandError as exc:
                self.warn(f"TPM falhou: {exc}")
        tpm_install = self.TPM_DIR / "bin" / "install_plugins"
        if tpm_install.exists():
            result = run([str(tpm_install)], check=False)
            if result.returncode != 0:
                self.info("Plugins tmux: rode prefix+I na primeira sessão")

    def _patch_zshrc(self) -> None:
        zshrc_text = self.ZSHRC.read_text(encoding="utf-8") if self.ZSHRC.exists() else ""
        if "zennit-os — Java Backend paths" in zshrc_text:
            self.ok(".zshrc já possui os paths do Zennit-OS")
            return
        with self.ZSHRC.open("a", encoding="utf-8") as f:
            f.write(self.ZSHRC_BLOCK)
        self.ok("Paths do Zennit-OS adicionados ao .zshrc")


# ──────────────────────────────────────────────────────────────────────────────

class DisableUnnecessaryServices(InstallStep):
    """Desativa serviços desnecessários para reduzir boot time."""

    label = "18/18 — Desativando serviços lentos"

    SERVICES_TO_DISABLE = [
        "NetworkManager-wait-online.service",
        "avahi-daemon",
        "ModemManager",
    ]

    def execute(self) -> None:
        for service in self.SERVICES_TO_DISABLE:
            result = run(
                ["sudo", "systemctl", "disable", "--now", service],
                check=False,
            )
            if result.returncode == 0:
                self.ok(f"{service} desativado")
            else:
                self.info(f"{service} já estava desativado ou não existe")
        result = run(["systemd-analyze"], capture=True, check=False)
        if result.returncode == 0:
            log.info(f"Tempo de boot: {result.stdout.strip()}")


# ═══════════════════════════════════════════════════════════════════════════════
# ORQUESTRADOR
# ═══════════════════════════════════════════════════════════════════════════════

class PostInstallOrchestrator:
    """Orquestra todos os passos de instalação e exibe o relatório final."""

    BANNER = """\
\033[1m\033[36m
╔══════════════════════════════════════════════════════╗
║   Zennit-OS — Rocky Linux  ·  Java Backend Setup    ║
╚══════════════════════════════════════════════════════╝
\033[0m"""

    def __init__(self) -> None:
        self.steps: list[InstallStep] = [
            PreFlightChecks(),
            RepositorySetup(),
            SystemUpdate(),
            BaseToolsInstaller(),
            KernelTuning(),
            ZramSetup(),
            CpuPowerManagement(),
            PowertopAutoTune(),
            JavaBackendInstaller(),
            DockerInstaller(),
            DatabaseToolsInstaller(),
            IdeToolsInstaller(),
            FontInstaller(),
            GnomeThemeSetup(),
            WallpaperSetup(),
            GnomeExtensionsSetup(),
            DotfilesSetup(),
            DisableUnnecessaryServices(),
        ]
        self.results: list[StepResult] = []

    def run(self) -> int:
        print(self.BANNER)
        log.info("Log completo em: %s", LOGFILE)

        start = datetime.now()

        for step in self.steps:
            result = step.run()
            self.results.append(result)

            if isinstance(step, PreFlightChecks) and result.status == StepStatus.FAILED:
                log.error("Pré-condições não atendidas. Abortando.")
                self._print_summary(elapsed=datetime.now() - start)
                return 1

        self._print_summary(elapsed=datetime.now() - start)
        return 0 if self._all_passed() else 1

    def _all_passed(self) -> bool:
        return all(
            r.status in (StepStatus.SUCCESS, StepStatus.WARNING, StepStatus.SKIPPED)
            for r in self.results
        )

    def _print_summary(self, elapsed) -> None:
        STATUS_ICON = {
            StepStatus.SUCCESS: ("\033[0;32m", "✓"),
            StepStatus.WARNING: ("\033[1;33m", "⚠"),
            StepStatus.FAILED:  ("\033[0;31m", "✗"),
            StepStatus.SKIPPED: ("\033[0;36m", "⊘"),
            StepStatus.PENDING: ("\033[0;37m", "·"),
            StepStatus.RUNNING: ("\033[0;34m", "→"),
        }
        NC = "\033[0m"

        print(f"\n\033[1m{'═' * 56}\033[0m")
        print("\033[1m  Resumo da instalação\033[0m")
        print(f"\033[1m{'═' * 56}\033[0m")

        for r in self.results:
            color, icon = STATUS_ICON.get(r.status, ("", "?"))
            print(f"  {color}{icon}{NC}  {r.name}")
            for err in r.errors:
                print(f"       \033[1;33m↳  {err}\033[0m")

        total   = len(self.results)
        success = sum(1 for r in self.results if r.status == StepStatus.SUCCESS)
        warns   = sum(1 for r in self.results if r.status == StepStatus.WARNING)
        failed  = sum(1 for r in self.results if r.status == StepStatus.FAILED)

        print(f"\n  Total: {total}  |  "
              f"\033[0;32m✓ {success}\033[0m  |  "
              f"\033[1;33m⚠ {warns}\033[0m  |  "
              f"\033[0;31m✗ {failed}\033[0m  |  "
              f"Tempo: {elapsed}")

        if self._all_passed():
            print("\n\033[1m\033[32m"
                  "╔══════════════════════════════════════════════════════╗\n"
                  "║   Instalação concluída! Reinicie a sessão.           ║\n"
                  "╚══════════════════════════════════════════════════════╝"
                  "\033[0m")
        else:
            print("\n\033[1m\033[31m"
                  "╔══════════════════════════════════════════════════════╗\n"
                  "║   Instalação concluída com erros. Veja o log.        ║\n"
                  "╚══════════════════════════════════════════════════════╝"
                  "\033[0m")

        print(f"\n  Log: \033[1m{LOGFILE}\033[0m\n")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    orchestrator = PostInstallOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())
