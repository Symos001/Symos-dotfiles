#!/usr/bin/env python3
# =============================================================================
# steps/zsh.py — Configura ZSH + Starship
# =============================================================================

import textwrap
from pathlib import Path

from .base import Step, StepResult


class ZshConfig(Step):
    """Configura .zshrc com Zinit + Starship."""

    @property
    def name(self) -> str:
        return "21/26 — Configuração ZSH"

    def execute(self) -> StepResult:
        result = StepResult(name=self.name)

        # .zshrc
        self._write_zshrc(result)

        # starship.toml
        self._write_starship_config(result)

        if result.is_success:
            result.mark_success("ZSH configurado")
        return result

    def _write_zshrc(self, result: StepResult) -> None:
        content = """# =============================================================================
# .zshrc — Zennit-OS Dev Environment
# Zsh + Zinit + Starship
# =============================================================================

# ─── Caminhos ──────────────────────────────────────────────────────────────────

export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"
export PATH="$HOME/.bun/bin:$PATH"
export PATH="$HOME/.dotnet:$HOME/.dotnet/tools:$PATH"
export PATH="$HOME/.local/share/nvim/mason/bin:$PATH"

# ─── Java (SDKMan) ────────────────────────────────────────────────────────────

export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
export JAVA_HOME="$HOME/.sdkman/candidates/java/current"
export PATH="$JAVA_HOME/bin:$PATH"

# ─── Golang ──────────────────────────────────────────────────────────────────

export GOROOT="/usr/lib/golang"
export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# ─── Rust ────────────────────────────────────────────────────────────────────

export RUSTUP_HOME="$HOME/.rustup"
export CARGO_HOME="$HOME/.cargo"
source "$HOME/.cargo/env" 2>/dev/null

# ─── .NET ────────────────────────────────────────────────────────────────────

export DOTNET_ROOT="/usr/lib/dotnet"
export DOTNET_CLI_TELEMETRY_OPTOUT=1

# ─── Node.js (NVM) ──────────────────────────────────────────────────────────

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ─── Bun ─────────────────────────────────────────────────────────────────────

export BUN_INSTALL="$HOME/.bun"
[ -s "$BUN_INSTALL/_bun" ] && source "$BUN_INSTALL/_bun"

# ─── Configurações do Zsh ────────────────────────────────────────────────────

export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=100000
export SAVEHIST=100000
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt SHARE_HISTORY
setopt EXTENDED_HISTORY
setopt AUTO_CD
setopt AUTO_PUSHD
setopt INTERACTIVE_COMMENTS
setopt NO_BG_NICE
setopt NO_HUP

# ─── Zinit ────────────────────────────────────────────────────────────────────

if [[ ! -f "$HOME/.zinit/bin/zinit.zsh" ]]; then
    print -P "%F{33}▓▒░ Instalando Zinit...%f"
    command mkdir -p "$HOME/.zinit"
    command git clone https://github.com/zdharma-continuum/zinit "$HOME/.zinit/bin"
fi

source "$HOME/.zinit/bin/zinit.zsh"
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

# ─── Plugins ──────────────────────────────────────────────────────────────────

zinit light marlonrichert/zsh-autocomplete
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light agkozak/zsh-z
zinit light marlonrichert/zsh-edit
zinit light Aloxaf/fzf-tab
zinit light MichaelAquilina/zsh-you-should-use
zinit light hlissner/zsh-autopair

autoload -Uz compinit && compinit

# ─── Starship ─────────────────────────────────────────────────────────────────

if ! command -v starship &> /dev/null; then
    curl -sS https://starship.rs/install.sh | sh -s -- --yes
fi

eval "$(starship init zsh)"

# ─── Aliases ──────────────────────────────────────────────────────────────────

# Navegação
alias ll='ls -lah'
alias la='ls -A'
alias l='ls -lah'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Git
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gd='git diff'
alias gl='git log --oneline --graph'
alias gp='git push'
alias gpl='git pull'
alias gco='git checkout'
alias gb='git branch'
alias gm='git merge'

# Docker
alias dc='docker compose'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dstop='docker stop'

# Java
alias mci='mvn clean install'
alias mct='mvn clean test'
alias mcp='mvn clean package'
alias gw='./gradlew'

# Rust
alias cb='cargo build'
alias cr='cargo run'
alias ct='cargo test'
alias cw='cargo watch'

# Node/Bun
alias ni='npm install'
alias ns='npm start'
alias nd='npm run dev'
alias nb='npm run build'
alias bi='bun install'
alias br='bun run'
alias bd='bun dev'

# Sistema
alias update='sudo dnf update -y && sudo dnf upgrade -y'
alias cleanup='sudo dnf autoremove -y && sudo dnf clean all'
alias ports='sudo netstat -tulpn | grep LISTEN'
alias reload='source ~/.zshrc'

# Utilitários modernos
alias cat='bat'
alias ls='eza --icons'
alias tree='eza --tree --icons'
alias find='fd'
alias grep='rg'
alias du='ncdu'
alias top='btop'

# ─── Funções ──────────────────────────────────────────────────────────────────

function mkcd() {
    mkdir -p "$1" && cd "$1"
}

function extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz)  tar xzf "$1" ;;
            *.bz2)     bunzip2 "$1" ;;
            *.rar)     unrar x "$1" ;;
            *.gz)      gunzip "$1" ;;
            *.tar)     tar xf "$1" ;;
            *.zip)     unzip "$1" ;;
            *.7z)      7z x "$1" ;;
            *)         echo "'$1' não pode ser extraído" ;;
        esac
    else
        echo "'$1' não é um arquivo válido"
    fi
}

function new-java() {
    mkdir -p "$1"
    cd "$1" || return
    cat > pom.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>$1</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
</project>
EOF
    mkdir -p src/main/java/com/example
    echo "✅ Projeto Java criado em $1"
}

function new-rust() {
    cargo new "$1"
    cd "$1" || return
    echo "✅ Projeto Rust criado em $1"
}

function new-go() {
    mkdir -p "$1"
    cd "$1" || return
    go mod init "$1"
    cat > main.go << EOF
package main
import "fmt"
func main() {
    fmt.Println("Hello, World!")
}
EOF
    echo "✅ Projeto Go criado em $1"
}

function new-node() {
    mkdir -p "$1"
    cd "$1" || return
    npm init -y
    cat > index.js << EOF
console.log('Hello, Node.js!');
EOF
    echo "✅ Projeto Node.js criado em $1"
}

# ─── FZF ──────────────────────────────────────────────────────────────────────

export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

export FZF_DEFAULT_OPTS="
--layout=reverse
--border
--height=40%
--preview 'bat --style=numbers --color=always {} 2>/dev/null || cat {}'
--preview-window=right:60%
"

# ─── Help ────────────────────────────────────────────────────────────────────

function help() {
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  🚀 Comandos úteis do Zennit-OS Dev Environment     ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "📁 CRIAÇÃO DE PROJETOS:"
    echo "  new-java <nome>    → Projeto Java (Maven)"
    echo "  new-rust <nome>    → Projeto Rust"
    echo "  new-go <nome>      → Projeto Go"
    echo "  new-node <nome>    → Projeto Node.js"
    echo ""
    echo "📦 ALIASES:"
    echo "  update      → Atualiza sistema"
    echo "  cleanup     → Limpa sistema"
    echo "  reload      → Recarrega .zshrc"
    echo "  ports       → Portas abertas"
    echo ""
    echo "🔍 ALIASES MODERNOS:"
    echo "  cat → bat    |  ls → eza    |  find → fd"
    echo "  grep → rg    |  du → ncdu   |  top → btop"
}

# ─── Motd ────────────────────────────────────────────────────────────────────

if command -v fastfetch &> /dev/null; then
    fastfetch --logo none --color
fi

echo "🚀 Zennit-OS Dev Environment carregado!"
echo "💡 Digite 'help' para comandos úteis"
"""

        dest = Path.home() / ".zshrc"
        if self.write_file(dest, content):
            self.logger.info(".zshrc gerado")
        else:
            result.mark_warning("Falha ao gerar .zshrc")

    def _write_starship_config(self, result: StepResult) -> None:
        content = '''# =============================================================================
# starship.toml — Tema Terafox/Nightfox
# =============================================================================

format = """
$username\\
$hostname\\
$directory\\
$git_branch\\
$git_status\\
$package\\
$c\\
$rust\\
$golang\\
$java\\
$nodejs\\
$python\\
$ruby\\
$elixir\\
$dotnet\\
$bun\\
$cmd_duration\\
$line_break\\
$jobs\\
$battery\\
$character
"""

[username]
format = "[$user]($style) "
style_user = "white bold"
style_root = "red bold"
show_always = true

[hostname]
format = "at [$hostname]($style) "
style = "gray dimmed"
ssh_only = false

[directory]
format = "in [$path]($style) "
style = "blue bold"
truncation_length = 3
truncation_symbol = "…/"
home_symbol = "~"

[git_branch]
format = "on [$branch]($style) "
style = "magenta bold"

[git_status]
format = "([$all_status$ahead_behind]($style))"
style = "magenta"
staged = " +"
modified = " ~"
deleted = " -"
renamed = " »"
untracked = " …"
ahead = " ⇡"
behind = " ⇣"

[c]
format = "via [$symbol($version)]($style) "
style = "blue"
symbol = "C "

[rust]
format = "via [$symbol($version)]($style) "
style = "red"
symbol = "R "

[golang]
format = "via [$symbol($version)]($style) "
style = "blue"
symbol = "G "

[java]
format = "via [$symbol($version)]($style) "
style = "red"
symbol = "☕ "

[nodejs]
format = "via [$symbol($version)]($style) "
style = "green"
symbol = "Node "

[python]
format = "via [$symbol($version)]($style) "
style = "yellow"
symbol = "🐍 "

[ruby]
format = "via [$symbol($version)]($style) "
style = "red"
symbol = "💎 "

[elixir]
format = "via [$symbol($version)]($style) "
style = "magenta"
symbol = "💧 "

[dotnet]
format = "via [$symbol($version)]($style) "
style = "blue"
symbol = ".NET "

[bun]
format = "via [$symbol($version)]($style) "
style = "white"
symbol = "🥟 "

[package]
format = "[$symbol$version]($style) "
style = "green"
symbol = "📦 "

[cmd_duration]
format = "took [$duration]($style) "
style = "yellow"
min_time = 2000

[character]
format = "$symbol "
success_symbol = "[❯](green)"
error_symbol = "[❯](red)"
vicmd_symbol = "[❮](gray)"

[battery]
format = "[$percentage]($style) "
style = "green"
full_symbol = "🔋"
charging_symbol = "⚡"
discharging_symbol = "🔋"
threshold = 20
'''

        starship_dir = Path.home() / ".config"
        starship_dir.mkdir(parents=True, exist_ok=True)
        dest = starship_dir / "starship.toml"

        if self.write_file(dest, content):
            self.logger.info("starship.toml gerado")
        else:
            result.mark_warning("Falha ao gerar starship.toml")
