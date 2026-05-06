export ZSH="/$HOME/.zsh"

# Plugins
source $ZSH/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source $ZSH/zsh-autosuggestions/zsh-autosuggestions.zsh

# Histórico
HISTSIZE=5000
SAVEHIST=5000
HISTFILE=$HOME/.zsh_history

setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY

# Autocomplete
autoload -Uz compinit
compinit

# Starship
eval "$(starship init zsh)"

# Aliases úteis
alias ll='ls -lah'
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias apt='sudo nala'
alias apt-get='sudo nala'


eval "$(direnv hook zsh)"

export PATH="$PATH:/opt/nvim-linux-x86_64/bin"

# proto
export PROTO_HOME="$HOME/.proto";
export PATH="$PROTO_HOME/shims:$PROTO_HOME/bin:$PATH";


export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

source "$HOME/.sdkman/bin/sdkman-init.sh"

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# Created by `pipx` on 2026-04-28 23:40:53
export PATH="$PATH:/home/lucas/.local/bin"
