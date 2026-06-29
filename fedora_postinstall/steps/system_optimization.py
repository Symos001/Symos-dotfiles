#!/usr/bin/env python3
# =============================================================================
# steps/system_optimization.py — Otimizações de sistema (AMD APU | NVMe)
# =============================================================================

import shutil
from datetime import datetime
from pathlib import Path

from .base import Step, StepResult


class SystemOptimization(Step):
    """Aplica otimizações de sistema: sysctl, ZRAM, CPU, I/O, boot, RAM, energia."""

    @property
    def name(self) -> str:
        return "7/27 — Otimizações de sistema"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Backup das configurações originais
        backup_dir = (
            Path.home() / f".config-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Backup das configs originais em: {backup_dir}")

        # 1. sysctl
        self._setup_sysctl(result, backup_dir)

        # 2. Transparent HugePage
        self._setup_thp(result)

        # 3. ZRAM
        self._setup_zram(result, backup_dir)

        # 4. CPU — AMD pstate + tuned + auto-cpufreq
        self._setup_cpu(result, backup_dir)

        # 5. I/O — SSD NVMe + btrfs
        self._setup_io(result, backup_dir)

        # 6. Boot — desativar serviços lentos
        self._setup_boot(result)

        # 7. RAM — earlyoom + preload
        self._setup_ram(result)

        # 8. Energia — powertop auto-tune
        self._setup_powertop(result)

        if result.is_success:
            result.mark_success(
                "Sistema otimizado (reinicie para aplicar todas as mudanças)"
            )
        return result

    # ─── 1. sysctl ──────────────────────────────────────────────────────────────

    def _setup_sysctl(self, result: StepResult, backup_dir: Path) -> None:
        self.logger.info("Configurando parâmetros de kernel (sysctl)...")

        sysctl_file = Path("/etc/sysctl.d/99-lucas-performance.conf")

        # Backup
        if sysctl_file.exists():
            shutil.copy2(sysctl_file, backup_dir / sysctl_file.name)

        content = """# ── Memória e swap ──────────────────────────────────────────────────
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5

# ── CPU e energia ───────────────────────────────────────────────────
kernel.nmi_watchdog = 0

# ── Rede (dev local: Docker, APIs, Spring Boot) ─────────────────────
net.core.netdev_max_backlog = 16384
net.core.somaxconn = 8192
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_slow_start_after_idle = 0

# ── Segurança (manter) ──────────────────────────────────────────────
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
"""

        if self.write_file(sysctl_file, content, as_root=True):
            try:
                self.run_command(["sudo", "sysctl", "--system"])
                self.logger.info("Parâmetros de kernel aplicados")
            except Exception as e:
                result.mark_warning(f"sysctl --system falhou: {e}")
        else:
            result.mark_warning("Falha ao escrever sysctl.conf")

    # ─── 2. Transparent HugePage ──────────────────────────────────────────────

    def _setup_thp(self, result: StepResult) -> None:
        self.logger.info("Configurando Transparent HugePage para madvise (JVM)...")

        try:
            # Aplica imediatamente
            self.run_command(
                ["sudo", "tee", "/sys/kernel/mm/transparent_hugepage/enabled"],
                input="madvise\n",
            )
            # Persiste via tmpfiles
            self.write_file(
                Path("/etc/tmpfiles.d/thp.conf"),
                "w /sys/kernel/mm/transparent_hugepage/enabled - - - - madvise\n",
                as_root=True,
            )
            self.logger.info("Transparent HugePage configurado para madvise")
        except Exception as e:
            result.mark_warning(f"THP falhou: {e}")

    # ─── 3. ZRAM ──────────────────────────────────────────────────────────────

    def _setup_zram(self, result: StepResult, backup_dir: Path) -> None:
        self.logger.info("Verificando ZRAM...")

        zram_conf = Path("/etc/systemd/zram-generator.conf")

        # Backup
        if zram_conf.exists():
            shutil.copy2(zram_conf, backup_dir / zram_conf.name)

        # Verifica se ZRAM já está ativo
        try:
            cmd_result = self.run_command(
                ["systemctl", "is-active", "--quiet", "swap.img.swap"], check=False
            )
            if cmd_result.returncode == 0:
                self.logger.info("ZRAM já ativo")
                return
        except:
            pass

        # Configura ZRAM
        content = """[zram0]
zram-size = ram / 2
compression-algorithm = zstd
swap-priority = 100
"""

        if self.write_file(zram_conf, content, as_root=True):
            try:
                self.run_command(["sudo", "systemctl", "daemon-reload"])
                self.logger.info("ZRAM configurado: 50% RAM, zstd")
            except Exception as e:
                result.mark_warning(f"ZRAM daemon-reload falhou: {e}")
        else:
            result.mark_warning("Falha ao configurar ZRAM")

        # Aviso sobre swap em disco
        try:
            cmd_result = self.run_command(["swapon", "--show"], capture=True)
            if "swapfile" in cmd_result.stdout or "/dev/" in cmd_result.stdout:
                result.mark_warning(
                    "Swap em disco detectado. Considere remover para priorizar ZRAM.\n"
                    "  Execute: sudo swapoff /swapfile && sudo rm /swapfile"
                )
        except:
            pass

    # ─── 4. CPU — AMD pstate + tuned + auto-cpufreq ──────────────────────────

    def _setup_cpu(self, result: StepResult, backup_dir: Path) -> None:
        self.logger.info("Configurando CPU: AMD pstate + tuned + auto-cpufreq...")

        # AMD pstate
        self._setup_amd_pstate(result, backup_dir)

        # tuned
        self._setup_tuned(result)

        # auto-cpufreq
        self._setup_auto_cpufreq(result)

    def _setup_amd_pstate(self, result: StepResult, backup_dir: Path) -> None:
        # Verifica driver atual
        try:
            cmd_result = self.run_command(
                ["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver"],
                capture=True,
                check=False,
            )
            if cmd_result.returncode == 0 and "amd_pstate" in cmd_result.stdout:
                self.logger.info(f"amd_pstate já ativo ({cmd_result.stdout.strip()})")
                return
        except:
            pass

        self.logger.info("Adicionando amd_pstate=active ao GRUB...")

        grub_file = Path("/etc/default/grub")
        if grub_file.exists():
            shutil.copy2(grub_file, backup_dir / "grub.bak")

        try:
            # Verifica se já existe
            content = grub_file.read_text() if grub_file.exists() else ""
            if "amd_pstate=active" not in content:
                # Adiciona ao GRUB_CMDLINE_LINUX
                self.run_command(
                    [
                        "sudo",
                        "sed",
                        "-i",
                        r's/GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="\1 amd_pstate=active"/',
                        str(grub_file),
                    ]
                )
                self.run_command(
                    ["sudo", "grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"]
                )
                self.logger.info("amd_pstate=active adicionado (ativo após reboot)")
            else:
                self.logger.info("amd_pstate=active já está configurado")
        except Exception as e:
            result.mark_warning(f"amd_pstate falhou: {e}")

    def _setup_tuned(self, result: StepResult) -> None:
        if not self.command_exists("tuned-adm"):
            self.logger.warning("tuned não encontrado")
            return

        try:
            self.run_command(["sudo", "systemctl", "enable", "--now", "tuned"])
            self.run_command(["sudo", "tuned-adm", "profile", "laptop-ac-powersave"])
            self.logger.info("tuned ativo com perfil laptop-ac-powersave")
        except Exception as e:
            result.mark_warning(f"tuned falhou: {e}")

    def _setup_auto_cpufreq(self, result: StepResult) -> None:
        if self.command_exists("auto-cpufreq"):
            try:
                self.run_command(["sudo", "auto-cpufreq", "--install"])
                self.logger.info("auto-cpufreq instalado como serviço")
            except Exception as e:
                result.mark_warning(f"auto-cpufreq --install falhou: {e}")
        else:
            self.logger.warning("auto-cpufreq não encontrado")
            self.logger.info("Instale com: sudo dnf install auto-cpufreq")

        # Desativa power-profiles-daemon (conflito)
        try:
            self.run_command(
                ["sudo", "systemctl", "disable", "--now", "power-profiles-daemon"],
                check=False,
            )
            self.logger.info("power-profiles-daemon desativado")
        except:
            pass

    # ─── 5. I/O — SSD NVMe + btrfs ────────────────────────────────────────────

    def _setup_io(self, result: StepResult, backup_dir: Path) -> None:
        self.logger.info("Configurando I/O: SSD NVMe + btrfs...")

        # NVMe scheduler
        self._setup_nvme_scheduler(result)

        # btrfs fstab
        self._setup_btrfs(result, backup_dir)

        # fstrim
        self._setup_fstrim(result)

        # irqbalance
        self._setup_irqbalance(result)

    def _setup_nvme_scheduler(self, result: StepResult) -> None:
        # Encontra dispositivo NVMe
        nvme_dev = None
        for dev in Path("/sys/block").iterdir():
            if dev.name.startswith("nvme"):
                nvme_dev = dev.name
                break

        if not nvme_dev:
            self.logger.info("Nenhum dispositivo NVMe encontrado")
            return

        scheduler_file = Path(f"/sys/block/{nvme_dev}/queue/scheduler")
        try:
            current = scheduler_file.read_text().strip()
            self.logger.info(f"Scheduler atual ({nvme_dev}): {current}")

            if "[none]" in current or "[kyber]" in current:
                self.logger.info("Scheduler já otimizado para NVMe")
            else:
                # Aplica kyber
                self.run_command(["sudo", "tee", str(scheduler_file)], input="kyber\n")
                self.logger.info("Scheduler alterado para kyber")

            # Persiste via udev
            udev_rule = """ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="kyber"
"""
            self.write_file(
                Path("/etc/udev/rules.d/60-nvme-scheduler.rules"),
                udev_rule,
                as_root=True,
            )
            self.logger.info("Regra udev criada para persistir scheduler")
        except Exception as e:
            result.mark_warning(f"NVMe scheduler falhou: {e}")

    def _setup_btrfs(self, result: StepResult, backup_dir: Path) -> None:
        fstab = Path("/etc/fstab")
        if not fstab.exists():
            return

        # Backup
        shutil.copy2(fstab, backup_dir / "fstab.bak")

        try:
            content = fstab.read_text()
            if "btrfs" not in content:
                self.logger.info("Sistema não usa btrfs")
                return

            if "noatime" in content and "compress=zstd" in content:
                self.logger.info("fstab btrfs já otimizado")
                return

            self.logger.info("Otimizando fstab btrfs...")
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if line.startswith("#") or "btrfs" not in line:
                    new_lines.append(line)
                    continue
                if "defaults" in line and "noatime" not in line:
                    line = line.replace(
                        "defaults",
                        "defaults,noatime,compress=zstd:1,space_cache=v2,discard=async",
                    )
                new_lines.append(line)

            self.write_file(fstab, "\n".join(new_lines) + "\n", as_root=True)
            self.logger.info("fstab btrfs otimizado")
        except Exception as e:
            result.mark_warning(f"btrfs otimização falhou: {e}")

    def _setup_fstrim(self, result: StepResult) -> None:
        try:
            self.run_command(["sudo", "systemctl", "enable", "--now", "fstrim.timer"])
            self.logger.info("fstrim.timer ativado (TRIM semanal)")
        except Exception as e:
            result.mark_warning(f"fstrim falhou: {e}")

    def _setup_irqbalance(self, result: StepResult) -> None:
        try:
            self.run_command(["sudo", "systemctl", "enable", "--now", "irqbalance"])
            self.logger.info("irqbalance ativado")
        except Exception as e:
            result.mark_warning(f"irqbalance falhou: {e}")

    # ─── 6. Boot — desativar serviços lentos ──────────────────────────────────

    def _setup_boot(self, result: StepResult) -> None:
        self.logger.info("Desativando serviços lentos no boot...")

        # Plymouth preservado
        self.logger.info("Plymouth preservado")

        services = [
            "NetworkManager-wait-online.service",
            "avahi-daemon",
            "ModemManager",
        ]

        for service in services:
            try:
                self.run_command(
                    ["sudo", "systemctl", "disable", "--now", service], check=False
                )
                self.logger.info(f"{service} desativado")
            except:
                self.logger.info(f"{service} já estava desativado")

        # Mostra tempo de boot
        try:
            cmd_result = self.run_command(
                ["systemd-analyze"], capture=True, check=False
            )
            if cmd_result.returncode == 0:
                self.logger.info(f"Tempo de boot atual: {cmd_result.stdout.strip()}")
        except:
            pass

    # ─── 7. RAM — earlyoom + preload ──────────────────────────────────────────

    def _setup_ram(self, result: StepResult) -> None:
        self.logger.info("Configurando RAM: earlyoom + preload...")

        # earlyoom
        if self.command_exists("earlyoom"):
            try:
                self.run_command(["sudo", "systemctl", "enable", "--now", "earlyoom"])
                self.logger.info("earlyoom ativo")
            except Exception as e:
                result.mark_warning(f"earlyoom falhou: {e}")
        else:
            self.dnf_install("earlyoom")
            try:
                self.run_command(["sudo", "systemctl", "enable", "--now", "earlyoom"])
                self.logger.info("earlyoom instalado e ativo")
            except Exception as e:
                result.mark_warning(f"earlyoom instalação falhou: {e}")

        # preload
        if self.command_exists("preload"):
            try:
                self.run_command(["sudo", "systemctl", "enable", "--now", "preload"])
                self.logger.info("preload ativo")
            except Exception as e:
                result.mark_warning(f"preload falhou: {e}")
        else:
            if self.dnf_install("preload"):
                try:
                    self.run_command(
                        ["sudo", "systemctl", "enable", "--now", "preload"]
                    )
                    self.logger.info("preload instalado e ativo")
                except Exception as e:
                    result.mark_warning(f"preload ativação falhou: {e}")

    # ─── 8. Energia — powertop auto-tune ──────────────────────────────────────

    def _setup_powertop(self, result: StepResult) -> None:
        self.logger.info("Configurando powertop auto-tune...")

        if not self.command_exists("powertop"):
            self.dnf_install("powertop")

        service_content = """[Unit]
Description=PowerTop auto-tune — AMD notebook power savings
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/powertop --auto-tune
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""

        service_file = Path("/etc/systemd/system/powertop.service")
        if self.write_file(service_file, service_content, as_root=True):
            try:
                self.run_command(["sudo", "systemctl", "daemon-reload"])
                self.run_command(
                    ["sudo", "systemctl", "enable", "--now", "powertop.service"]
                )
                self.logger.info("powertop.service criado e ativado")
            except Exception as e:
                result.mark_warning(f"powertop.service falhou: {e}")
        else:
            result.mark_warning("Falha ao criar powertop.service")
