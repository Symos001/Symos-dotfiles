#!/usr/bin/env python3
# =============================================================================
# steps/kernel_tuning.py — Tuning do kernel
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class KernelTuning(Step):
    """Configura sysctl, THP, limites, fstrim."""

    @property
    def name(self) -> str:
        return "5/26 — Tuning de kernel e I/O"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # Sysctl
        self._setup_sysctl(result)

        # Limites de arquivos
        self._setup_limits(result)

        # THP
        self._setup_thp(result)

        # fstrim
        self._setup_fstrim(result)

        # Otimiza btrfs
        self._optimize_btrfs(result)

        if result.is_success:
            result.mark_success("Kernel otimizado")
        return result

    def _setup_sysctl(self, result: StepResult) -> None:
        content = """# Zennit-OS — Dev Tuning
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
kernel.nmi_watchdog = 0
net.core.netdev_max_backlog = 16384
fs.inotify.max_user_watches = 524288
fs.file-max = 2097152
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
"""
        self.write_file(Path("/etc/sysctl.d/99-dev-tuning.conf"), content, as_root=True)
        try:
            self.run_command(["sudo", "sysctl", "--system"])
            self.logger.info("Sysctl aplicado")
        except Exception as e:
            result.mark_warning(f"Sysctl falhou: {e}")

    def _setup_limits(self, result: StepResult) -> None:
        content = "* soft nofile 65536\n* hard nofile 65536\n"
        self.write_file(
            Path("/etc/security/limits.d/99-dev.conf"), content, as_root=True
        )

    def _setup_thp(self, result: StepResult) -> None:
        try:
            self.run_command(
                ["sudo", "tee", "/sys/kernel/mm/transparent_hugepage/enabled"],
                input="madvise\n",
            )
            self.write_file(
                Path("/etc/tmpfiles.d/thp.conf"),
                "w /sys/kernel/mm/transparent_hugepage/enabled - - - - madvise\n",
                as_root=True,
            )
            self.logger.info("THP configurado para madvise")
        except Exception as e:
            result.mark_warning(f"THP falhou: {e}")

    def _setup_fstrim(self, result: StepResult) -> None:
        try:
            self.run_command(["sudo", "systemctl", "enable", "--now", "fstrim.timer"])
            self.logger.info("fstrim.timer ativado")
        except Exception as e:
            result.mark_warning(f"fstrim falhou: {e}")

    def _optimize_btrfs(self, result: StepResult) -> None:
        fstab = Path("/etc/fstab")
        if not fstab.exists():
            return

        content = fstab.read_text()
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
