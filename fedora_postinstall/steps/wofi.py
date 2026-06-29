#!/usr/bin/env python3
# =============================================================================
# steps/wofi.py — Configura Wofi
# =============================================================================

from pathlib import Path

from .base import Step, StepResult


class WofiConfig(Step):
    """Configura Wofi (style.css)."""

    @property
    def name(self) -> str:
        return "18/26 — Configuração Wofi"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        wofi_dir = Path.home() / ".config" / "wofi"
        wofi_dir.mkdir(parents=True, exist_ok=True)

        content = """/* ============================================================================
   Wofi — Tema Terafox/Nightfox (Menos Translúcido)
   ============================================================================ */

window {
    background-color: rgba(22, 24, 33, 0.88);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 20px 24px;
    margin: 60px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    min-width: 540px;
    max-width: 720px;
    backdrop-filter: blur(12px);
}

#input {
    background-color: rgba(32, 35, 48, 0.85);
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 22px;
    font-weight: 500;
    color: #c5cdd9;
    border: 2px solid transparent;
    caret-color: #719cd6;
    transition: all 0.15s ease;
}

#input:focus {
    border-color: #719cd6;
    background-color: rgba(45, 49, 66, 0.92);
    outline: none;
}

#input:placeholder {
    color: #8a93a3;
    font-weight: 400;
}

#input image {
    margin-right: 10px;
    color: #8a93a3;
}

#inner-box {
    margin-top: 16px;
}

#entry {
    padding: 12px 16px;
    margin: 2px 0;
    font-size: 16px;
    color: #c5cdd9;
    border-radius: 10px;
    transition: all 0.08s ease;
}

#entry:selected {
    background-color: rgba(113, 156, 214, 0.15);
    color: #719cd6;
    font-weight: 500;
}

#entry:hover:not(:selected) {
    background-color: rgba(32, 35, 48, 0.85);
}

#entry image {
    margin-right: 14px;
    opacity: 0.7;
}

#entry:selected image {
    opacity: 1;
}

scrollbar {
    background: transparent;
    border-radius: 8px;
}

scrollbar slider {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    min-width: 6px;
    min-height: 40px;
}

scrollbar slider:hover {
    background: rgba(255, 255, 255, 0.15);
}

#grid {
    margin-top: 16px;
}

#grid #entry {
    margin: 4px;
    padding: 20px 16px;
    min-width: 80px;
    text-align: center;
    border-radius: 12px;
    background: rgba(32, 35, 48, 0.85);
}

#grid #entry:selected {
    background: rgba(113, 156, 214, 0.15);
    color: #719cd6;
}

#grid #entry image {
    margin: 0 0 8px 0;
    font-size: 28px;
}
"""

        dest = wofi_dir / "style.css"
        if self.write_file(dest, content):
            self.logger.info("wofi/style.css gerado")
            result.mark_success("Wofi configurado")
        else:
            result.mark_failed("Falha ao gerar wofi/style.css")

        return result
