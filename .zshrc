# =============================================================================
# .zshrc — Zennit-OS Dev Environment
# Zsh + Zinit + Starship
# Multi-Linguagem: Java, C/C++, Rust, Elixir, Ruby, Crystal, Go, Node, Bun, .NET
# Plugins: zsh-syntax-highlighting + zsh-autocomplete
# =============================================================================

# ─── Caminhos do Sistema ──────────────────────────────────────────────────────

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
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # Carrega nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ─── Bun ─────────────────────────────────────────────────────────────────────

export BUN_INSTALL="$HOME/.bun"
[ -s "$BUN_INSTALL/_bun" ] && source "$BUN_INSTALL/_bun"

# ─── Python ──────────────────────────────────────────────────────────────────

export PYTHONUNBUFFERED=1
export PIP_REQUIRE_VIRTUALENV=true

# ─── Configurações de Sistema ──────────────────────────────────────────────

export EDITOR="nvim"
export VISUAL="nvim"
export PAGER="less"
export BROWSER="google-chrome-stable"
export TERMINAL="alacritty"

# Histórico do Zsh
export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=100000
export SAVEHIST=100000
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt SHARE_HISTORY
setopt EXTENDED_HISTORY
setopt HIST_REDUCE_BLANKS

# Opções do Zsh
setopt AUTO_CD              # Digita diretório e entra
setopt AUTO_PUSHD           # Adiciona diretórios ao stack
setopt PUSHD_IGNORE_DUPS    # Remove duplicatas no stack
setopt INTERACTIVE_COMMENTS # Permite comentários no terminal
setopt NO_BG_NICE           # Não nice processos em background
setopt NO_HUP               # Não mata processos ao fechar terminal
setopt LOCAL_OPTIONS        # Permite opções locais em funções
setopt LOCAL_TRAPS          # Permite traps locais em funções

# ─── Zinit (Gerenciador de Plugins) ──────────────────────────────────────────

# Instala Zinit se não existir
if [[ ! -f "$HOME/.zinit/bin/zinit.zsh" ]]; then
    print -P "%F{33}▓▒░ Instalando Zinit...%f"
    command mkdir -p "$HOME/.zinit"
    command git clone https://github.com/zdharma-continuum/zinit "$HOME/.zinit/bin"
fi

source "$HOME/.zinit/bin/zinit.zsh"
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

# ─── Plugins Zinit ───────────────────────────────────────────────────────────

# ============================================================================
# 1. SYNTAX HIGHLIGHTING (Destaque de comandos)
# ============================================================================
# Deve ser carregado por ÚLTIMO para não conflitar com autocomplete
zinit light zsh-users/zsh-syntax-highlighting

# ============================================================================
# 2. AUTOCOMPLETE (Substitui o autosuggestions)
# ============================================================================
# zsh-autocomplete é mais completo que autosuggestions
# - Autocomplete em tempo real
# - Menu de sugestões
# - Histórico com pesquisa
zinit light marlonrichert/zsh-autocomplete

# Configurações do autocomplete
# Tecla Tab para navegar no menu
zstyle ':autocomplete:*' default-context history-incremental-search-backward
zstyle ':autocomplete:*' min-input 1
zstyle ':autocomplete:*' delay 0.1  # Tempo de resposta
zstyle ':autocomplete:*' list-lines 15  # Número de linhas no menu

# Completa com Tab (não Enter)
zstyle ':autocomplete:*' insert-unambiguous yes

# ============================================================================
# 3. OUTROS PLUGINS
# ============================================================================

zinit light zsh-users/zsh-completions           # Completions adicionais
zinit light agkozak/zsh-z                       # Navegação rápida (z)
zinit light marlonrichert/zsh-edit              # Atalhos de edição
zinit light Aloxaf/fzf-tab                      # Completions com fzf
zinit light MichaelAquilina/zsh-you-should-use  # Lembra de aliases
zinit light hlissner/zsh-autopair               # Fecha parênteses/aspas automaticamente

# ============================================================================
# 4. COMPLETIONS DO ZINIT
# ============================================================================

# Carrega completions
autoload -Uz compinit && compinit

# ============================================================================
# 5. CONFIGURAÇÕES DO FZF-TAB
# ============================================================================

# Desabilita o preview para melhor performance
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --icons --color=always $realpath'
zstyle ':fzf-tab:complete:ls:*' fzf-preview 'eza -1 --icons --color=always $realpath'

# ─── Starship Prompt ─────────────────────────────────────────────────────────

# Instala Starship se não existir
if ! command -v starship &> /dev/null; then
    print -P "%F{33}▓▒░ Instalando Starship...%f"
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
alias -- -='cd -'

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
alias gst='git stash'
alias gstp='git stash pop'
alias gr='git rebase'
alias gra='git rebase --abort'
alias grc='git rebase --continue'
alias gri='git rebase -i'

# Docker
alias dc='docker compose'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dstop='docker stop'
alias dstart='docker start'
alias dlog='docker logs'
alias dexec='docker exec -it'

# Desenvolvimento
alias c='clear'
alias nv='nvim'
alias v='nvim'
alias mk='mkdir -p'
alias reload='source ~/.zshrc'

# Java
alias mvn='mvn'
alias mci='mvn clean install'
alias mct='mvn clean test'
alias mcp='mvn clean package'
alias gradle='gradle'
alias gw='./gradlew'
alias j='java'
alias javac='javac'
alias jshell='jshell'

# Rust
alias c='cargo'
alias cb='cargo build'
alias cr='cargo run'
alias ct='cargo test'
alias cw='cargo watch'
alias ccl='cargo clean'
alias cdoc='cargo doc --open'

# Elixir
alias iex='iex -S mix'
alias mix='mix'
alias phx='mix phx'
alias mxs='mix run --no-halt'
alias mxd='mix deps.get'

# Ruby
alias be='bundle exec'
alias bi='bundle install'
alias bu='bundle update'
alias rs='rails s'
alias rc='rails c'
alias rg='rails g'
alias rd='rails db:migrate'

# Golang
alias gob='go build'
alias gor='go run'
alias got='go test'
alias gof='go fmt'
alias gom='go mod tidy'
alias gog='go get'
alias goi='go install'

# Node/Bun
alias ni='npm install'
alias ns='npm start'
alias nd='npm run dev'
alias nb='npm run build'
alias nt='npm test'
alias nid='npm install -D'
alias bi='bun install'
alias br='bun run'
alias bd='bun dev'
alias bb='bun build'
alias bt='bun test'

# Sistema
alias update='sudo dnf update -y && sudo dnf upgrade -y'
alias upgrade='sudo dnf upgrade -y'
alias cleanup='sudo dnf autoremove -y && sudo dnf clean all'
alias ports='sudo netstat -tulpn | grep LISTEN'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias psg='ps aux | grep -v grep | grep -i'
alias sysinfo='fastfetch'
alias reboot='sudo reboot'
alias shutdown='sudo shutdown -h now'

# Utilitários
alias cat='bat'          # bat = cat com syntax highlighting
alias ls='eza --icons'   # eza = ls moderno
alias tree='eza --tree --icons'
alias find='fd'          # fd = find moderno
alias grep='rg'          # ripgrep = grep moderno
alias du='ncdu'          # ncdu = du interativo
alias top='btop'         # btop = top moderno
alias h='history'
alias path='echo $PATH | tr ":" "\n"'

# KDE/Hyprland
alias env='env | sort'
alias wm='hyprctl'

# ─── Funções Úteis ────────────────────────────────────────────────────────────

# Cria e entra no diretório
function mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Extrai arquivos automaticamente
function extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz)  tar xzf "$1" ;;
            *.bz2)     bunzip2 "$1" ;;
            *.rar)     unrar x "$1" ;;
            *.gz)      gunzip "$1" ;;
            *.tar)     tar xf "$1" ;;
            *.tbz2)    tar xjf "$1" ;;
            *.tgz)     tar xzf "$1" ;;
            *.zip)     unzip "$1" ;;
            *.Z)       uncompress "$1" ;;
            *.7z)      7z x "$1" ;;
            *)         echo "'$1' não pode ser extraído" ;;
        esac
    else
        echo "'$1' não é um arquivo válido"
    fi
}

# Cria projeto Java
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

# Cria projeto Java com Spring Boot
function new-spring() {
    local group="${2:-com.example}"
    local artifact="$1"
    curl -s https://start.spring.io/starter.zip \
        -d dependencies=web,data-jpa,postgresql \
        -d groupId="$group" \
        -d artifactId="$artifact" \
        -d javaVersion=21 \
        -o "$artifact.zip"
    unzip "$artifact.zip" -d "$artifact"
    rm "$artifact.zip"
    cd "$artifact" || return
    echo "✅ Projeto Spring Boot criado em $artifact"
}

# Cria projeto Rust
function new-rust() {
    cargo new "$1"
    cd "$1" || return
    echo "✅ Projeto Rust criado em $1"
}

# Cria projeto Rust com Axum (web)
function new-rust-web() {
    cargo new "$1"
    cd "$1" || return
    cargo add axum tokio serde serde_json
    cat > src/main.rs << EOF
use axum::{Router, routing::get};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "Hello, World!" }));

    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
EOF
    echo "✅ Projeto Rust Axum criado em $1"
}

# Cria projeto Go
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

# Cria projeto C++ (CMake)
function new-cpp() {
    mkdir -p "$1"
    cd "$1" || return
    cat > CMakeLists.txt << EOF
cmake_minimum_required(VERSION 3.20)
project($1)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable($1 main.cpp)
EOF
    cat > main.cpp << EOF
#include <iostream>

int main() {
    std::cout << "Hello, C++20!" << std::endl;
    return 0;
}
EOF
    mkdir -p build
    echo "✅ Projeto C++ criado em $1"
}

# Cria projeto Elixir (Phoenix)
function new-elixir() {
    mix phx.new "$1"
    cd "$1" || return
    echo "✅ Projeto Elixir Phoenix criado em $1"
}

# Cria projeto Ruby (Rails)
function new-rails() {
    rails new "$1"
    cd "$1" || return
    echo "✅ Projeto Ruby on Rails criado em $1"
}

# Cria projeto Crystal
function new-crystal() {
    mkdir -p "$1"
    cd "$1" || return
    cat > src.cr << EOF
puts "Hello, Crystal!"
EOF
    echo "✅ Projeto Crystal criado em $1"
}

# Inicializa projeto Node.js
function new-node() {
    mkdir -p "$1"
    cd "$1" || return
    npm init -y
    cat > index.js << EOF
console.log('Hello, Node.js!');
EOF
    echo "✅ Projeto Node.js criado em $1"
}

# Inicializa projeto Bun
function new-bun() {
    mkdir -p "$1"
    cd "$1" || return
    bun init -y
    cat > index.ts << EOF
console.log('Hello, Bun!');
EOF
    echo "✅ Projeto Bun criado em $1"
}

# ─── fzf Configurações ───────────────────────────────────────────────────────

# Usa fzf para navegação de diretórios
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# Preview de arquivos no fzf
export FZF_DEFAULT_OPTS="
--layout=reverse
--border
--height=40%
--preview 'bat --style=numbers --color=always {} 2>/dev/null || cat {}'
--preview-window=right:60%
--prompt='❯ '
--pointer='➜'
--marker='✓'
"

# ─── Autocomplete do Docker ─────────────────────────────────────────────────

# Compila autocomplete do Docker
if [[ -f /usr/share/bash-completion/completions/docker ]]; then
    source /usr/share/bash-completion/completions/docker
fi

# ─── Autocomplete do kubectl ─────────────────────────────────────────────────

if command -v kubectl &> /dev/null; then
    source <(kubectl completion zsh)
fi

# ─── Alias para Zsh ──────────────────────────────────────────────────────────

# Correção automática de comandos
setopt CORRECT

# Autocomplete case-insensitive
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# ─── Motd Personalizado ──────────────────────────────────────────────────────

# Mostra informações do sistema ao abrir terminal
if command -v fastfetch &> /dev/null; then
    fastfetch --logo none --color
fi

# ─── Início da Sessão ────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🚀 Zennit-OS Dev Environment                       ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  📦 Linguagens: Java 21, C/C++, Rust, Elixir,      ║"
echo "║               Ruby, Crystal, Go, Node, Bun, .NET    ║"
echo "║  🔌 Plugins: syntax-highlighting + autocomplete     ║"
echo "║  💡 Digite 'help' para comandos úteis               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ─── Help ────────────────────────────────────────────────────────────────────

function help() {
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  🚀 Comandos úteis do Zennit-OS Dev Environment     ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "📁 CRIAÇÃO DE PROJETOS:"
    echo "  new-java <nome>          → Projeto Java (Maven)"
    echo "  new-spring <nome> [grupo] → Projeto Spring Boot"
    echo "  new-rust <nome>          → Projeto Rust"
    echo "  new-rust-web <nome>      → Projeto Rust Axum (web)"
    echo "  new-go <nome>            → Projeto Go"
    echo "  new-cpp <nome>           → Projeto C++ (CMake)"
    echo "  new-elixir <nome>        → Projeto Elixir Phoenix"
    echo "  new-rails <nome>         → Projeto Ruby on Rails"
    echo "  new-crystal <nome>       → Projeto Crystal"
    echo "  new-node <nome>          → Projeto Node.js"
    echo "  new-bun <nome>           → Projeto Bun"
    echo ""
    echo "🔍 ALIASES MODERNOS:"
    echo "  cat → bat    |  ls → eza        |  find → fd"
    echo "  grep → rg    |  du → ncdu       |  top → btop"
    echo ""
    echo "📦 ALIASES GIT:"
    echo "  gs, ga, gc, gd, gl, gp, gpl, gco, gb, gm, gst"
    echo ""
    echo "🐳 ALIASES DOCKER:"
    echo "  dc, dps, di, drm, dstop, dstart, dlog, dexec"
    echo ""
    echo "☕ JAVA:"
    echo "  mci = mvn clean install    | mct = mvn clean test"
    echo "  mcp = mvn clean package    | gw = ./gradlew"
    echo ""
    echo "🦀 RUST:"
    echo "  cb = cargo build           | cr = cargo run"
    echo "  ct = cargo test            | cw = cargo watch"
    echo ""
    echo "⚡ NODE/BUN:"
    echo "  ni, ns, nd, nb, nt         | bi, br, bd, bb, bt"
    echo ""
    echo "🔄 SISTEMA:"
    echo "  update      → Atualiza sistema"
    echo "  cleanup     → Limpa sistema"
    echo "  ports       → Portas abertas"
    echo "  reload      → Recarrega .zshrc"
    echo ""
    echo "⌨️  ATALHOS DO ZSH-AUTOCOMPLETE:"
    echo "  Tab         → Completa com menu"
    echo "  Ctrl+Space  → Mostra menu de completions"
    echo "  Ctrl+P/N    → Navega no menu"
    echo "  Ctrl+R      → Busca no histórico"
}

# ─── Fim do .zshrc ───────────────────────────────────────────────────────────
