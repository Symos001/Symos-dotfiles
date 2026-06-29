#!/usr/bin/env python3
# =============================================================================
# steps/__init__.py — Exporta todos os steps
# =============================================================================

from .base import Step, StepResult, StepStatus
from .base_tools import BaseToolsInstaller
from .cpu_power import CpuPowerManagement
from .docker import DockerInstaller
from .dotfiles import DotfilesSetup
from .final_cleanup import FinalCleanup
from .fonts import FontInstaller
from .hyprland import HyprlandSetup
from .hyprland_config import HyprlandConfig
from .hyprpaper import HyprpaperConfig
from .hyprshot import HyprshotConfig
from .ide_tools import IdeToolsInstaller
from .java_backend import JavaBackendInstaller
from .kernel_tunning import KernelTuning
from .languages import DevLanguagesInstaller
from .pre_flight import PreFlightChecks
from .repositories import RepositorySetup
from .scripts import ScriptsSetup
from .swaync import SwayNCConfig
from .system_optimization import SystemOptimization  # NOVO
from .system_update import SystemUpdate
from .waybar import WaybarConfig
from .wlogout import WlogoutConfig
from .wofi import WofiConfig
from .zram_setup import ZramSetup
from .zsh import ZshConfig

__all__ = [
    "Step",
    "StepResult",
    "StepStatus",
    "PreFlightChecks",
    "RepositorySetup",
    "SystemUpdate",
    "BaseToolsInstaller",
    "KernelTuning",
    "ZramSetup",
    "CpuPowerManagement",
    "SystemOptimization",  # NOVO
    "JavaBackendInstaller",
    "DevLanguagesInstaller",
    "DockerInstaller",
    "IdeToolsInstaller",
    "FontInstaller",
    "HyprlandSetup",
    "HyprlandConfig",
    "HyprshotConfig",
    "HyprpaperConfig",
    "WaybarConfig",
    "WofiConfig",
    "WlogoutConfig",
    "SwayNCConfig",
    "ZshConfig",
    "DotfilesSetup",
    "ScriptsSetup",
    "FinalCleanup",
]
