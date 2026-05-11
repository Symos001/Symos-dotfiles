# Caminho base (ajustado)
export ZSH="$HOME/.zsh"

### 1. Instalar/Carregar Zinit
if [[ ! -f $HOME/.local/share/zinit/zinit.git/zinit.zsh ]]; then
    print -P "%F{33}▓▒░ %F{34}Instalando Zinit...%f"
    command mkdir -p "$HOME/.local/share/zinit" && command chmod g-rwX "$HOME/.local/share/zinit"
    command git clone https://github.com/zdharma-continuum/zinit.git "$HOME/.local/share/zinit/zinit.git"
fi

source "$HOME/.local/share/zinit/zinit.git/zinit.zsh"

### 2. Plugins Essenciais (Carregamento imediato para não bugar o prompt)
zinit light zsh-users/zsh-completions
zinit snippet OMZ::lib/git.zsh
zinit snippet OMZ::plugins/git/git.plugin.zsh


zinit wait lucid for \
    atinit"zicompinit; zicdreplay" \
    zdharma-continuum/fast-syntax-highlighting \
    zsh-users/zsh-autosuggestions
### 4. Configurações de Histórico
HISTSIZE=5000
SAVEHIST=5000
HISTFILE=$HOME/.zsh_history
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY

### 5. Starship Prompt (Carregar antes dos aliases)
eval "$(starship init zsh)"

### 6. Aliases (Adicionei o 'ls' para o nala/eza se preferir)
alias ll='ls -lah'
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias apt='sudo nala'
alias apt-get='sudo nala'

### 7. Exports e Variáveis de Ambiente (PATH)
export PATH="$PATH:/opt/nvim-linux-x86_64/bin"
export PATH="$PATH:$HOME/.local/bin"

# Proto
export PROTO_HOME="$HOME/.proto"
export PATH="$PROTO_HOME/shims:$PROTO_HOME/bin:$PATH"

# NVM (Carregamento preguiçoso para não travar o boot)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" --no-use # O --no-use acelera o boot

# SDKMAN
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ]] && source "$SDKMAN_DIR/bin/sdkman-init.sh"bin"
