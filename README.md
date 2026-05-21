# Zennit-OS — Fedora 44 · Java Backend Setup

> Script de pós-instalação automatizado para Fedora 44 com foco em desenvolvimento **Java Backend**.
> Configura o sistema do zero: ferramentas, IDEs, performance, tema visual e snapshots automáticos.

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Sistema operacional alvo](#sistema-operacional-alvo)
- [Tecnologias e ferramentas instaladas](#tecnologias-e-ferramentas-instaladas)
- [Pré-requisitos](#pré-requisitos)
- [Como executar](#como-executar)
- [O que o script faz](#o-que-o-script-faz)
- [Estrutura do script](#estrutura-do-script)
- [Após a execução](#após-a-execução)

---

## Sobre o projeto

O **Zennit-OS post-install** automatiza toda a configuração necessária após uma instalação limpa do Fedora 44. Em vez de executar dezenas de comandos manualmente, um único script cuida de repositórios, pacotes, tuning de kernel, ferramentas de desenvolvimento, IDEs, tema e snapshots — com log completo e resumo visual ao final.

---

## Sistema operacional alvo

| Campo          | Detalhe                          |
|----------------|----------------------------------|
| Distro         | **Fedora 44**                    |
| Desktop        | **GNOME** (Wayland)              |
| Sistema de arquivos | **btrfs**               |
| Arquitetura    | x86\_64 (AMD / Intel)            |
| Shell padrão   | **ZSH** + Starship               |

> ⚠️ O script foi desenvolvido e testado exclusivamente no Fedora 44 com btrfs. Outras distros ou versões do Fedora não são suportadas.

---

## Tecnologias e ferramentas instaladas

### ☕ Java Backend
| Ferramenta | Versão / Detalhe |
|---|---|
| Java (Temurin) | 21 (padrão) e 17 |
| Maven | Última via SDKMan |
| Gradle | Última via SDKMan |
| Quarkus CLI | Última via SDKMan |
| SDKMan | Gerenciador de SDKs Java |

### 🐳 Containers e banco de dados
| Ferramenta | Detalhe |
|---|---|
| Docker CE | + Compose Plugin |
| PostgreSQL | Cliente CLI |
| MySQL | Cliente CLI |
| Redis | Cliente CLI |
| SQLite | Cliente CLI |
| DBeaver Community | Via Flatpak |

### 🖥️ IDEs e editores
| Ferramenta | Detalhe |
|---|---|
| IntelliJ IDEA Community | Via Flatpak |
| VS Code | Via Flatpak |
| Bruno | API Client — via Flatpak |
| Neovim | Via dnf |
| OnlyOffice | Via Flatpak |

### ⚙️ Performance e kernel
| Otimização | Detalhe |
|---|---|
| EarlyOOM | Proteção contra OOM — configurado para proteger IDEs e Java |
| ZRAM | Swap comprimido em RAM (50%, zstd, prioridade 100) |
| AMD pstate | Modo `active` via grubby |
| tuned | Perfil `laptop-ac-powersave` |
| auto-cpufreq | Gerenciamento dinâmico de frequência |
| powertop | Auto-tune no boot via systemd |
| sysctl | `vm.swappiness=10`, inotify, TCP fastopen, etc. |
| THP | `madvise` — otimizado para JVM |
| NVMe scheduler | `kyber` via udev |
| btrfs fstab | `noatime`, `compress=zstd:1`, `discard=async` |
| fstrim.timer | TRIM semanal automático |
| Snapper | Snapshots automáticos do sistema com limpeza configurada |

### 🎨 Visual
| Item | Detalhe |
|---|---|
| Tema GTK | Fluent Blue Dark (blur + round) |
| Ícones | Fluent Dark |
| Fontes | FiraCode e JetBrainsMono Nerd Fonts + MS Core Fonts |
| Wallpaper | Firewatch dinâmico (ciclo dia/noite nativo GNOME) |
| Shell prompt | Starship |
| Extensões GNOME | Dash-to-Dock, AppIndicator, Caffeine, Blur My Shell, Magic Lamp, DING |

### 🛠️ CLI e utilitários
`htop` · `btop` · `bat` · `eza` · `fd-find` · `ripgrep` · `fzf` · `zoxide`
`tmux` + TPM · `ncdu` · `fastfetch` · `stow` · `rclone` · `uv` · `irqbalance` · `preload`

---

## Pré-requisitos

- Fedora 44 instalado com partição **btrfs**
- Conexão com a internet
- Usuário **normal com sudo** (não execute como root)
- Python 3.10 ou superior (já incluso no Fedora 44)

Verifique sua versão do Python:

```bash
python3 --version
```

---

## Como executar

### ⚡ Método recomendado — via curl

Baixa e executa diretamente, sem etapas extras:

```bash
curl -sSL https://raw.githubusercontent.com/Symos001/Symos-dotfiles/test/fedora44_post_install_snapper.py | python3
```

### 📥 Método alternativo — download e execução local

Se preferir inspecionar o script antes de rodar:

```bash
# 1. Baixar o script
curl -sSL https://raw.githubusercontent.com/Symos001/Symos-dotfiles/test/fedora44_post_install_snapper.py \
     -o post_install_fedora44.py

# 2. (Opcional) Revisar o conteúdo
less post_install_fedora44.py

# 3. Executar
python3 post_install_fedora44.py
```

### 🐍 Requisitos do ambiente Python

O script usa apenas a **biblioteca padrão** do Python — não é necessário instalar dependências externas com `pip`.

Módulos utilizados: `subprocess`, `pathlib`, `logging`, `dataclasses`, `abc`, `enum`, `textwrap`, `shutil`, `os`, `sys`, `json`, `datetime`.

---

## O que o script faz

O script executa **19 etapas** em sequência, com barra de progresso e tempo de execução por etapa:

```
 1  Verificações iniciais          — checa usuário e conectividade
 2  Repositórios                   — RPM Fusion (free/nonfree), Flathub, COPRs
 3  Atualização do sistema         — dnf upgrade --refresh
 4  Ferramentas base               — CLI, ZSH, git, EarlyOOM, serviços
 5  Tuning de kernel e I/O         — sysctl, THP, NVMe scheduler, btrfs fstab
 6  ZRAM                           — swap comprimido em RAM
 7  CPU: AMD pstate + tuned        — power management completo
 8  Energia: powertop auto-tune    — serviço systemd no boot
 9  Java Backend                   — SDKMan, Java 21/17, Maven, Gradle, Quarkus
10  Docker CE + Compose            — repositório oficial + firewall
11  Ferramentas de banco de dados  — clientes CLI + DBeaver
12  IDEs e ferramentas             — IntelliJ, VS Code, Bruno, uv
13  Fontes                         — Nerd Fonts + MS Core Fonts
14  Tema Fluent Blue Dark          — GTK + ícones + Flatpak overrides
15  Wallpaper Firewatch Dinâmico   — ciclo nativo GNOME
16  Extensões GNOME                — instalação via API + ativação
17  Snapper                        — snapshots btrfs automáticos
18  Dotfiles e ZSH config          — clone + GNU Stow + .zshrc
19  Desativando serviços lentos    — boot mais rápido
```

Ao final, um resumo colorido exibe o status de cada etapa e o tempo total de execução. O log completo é salvo em:

```
~/post-install-fedora44-java.log
```

---

## Estrutura do script

O código é orientado a objetos com uma hierarquia clara:

```
InstallStep (ABC)
├── PreFlightChecks
├── RepositorySetup
├── SystemUpdate
├── BaseToolsInstaller
├── KernelTuning
├── ZramSetup
├── CpuPowerManagement
├── PowertopAutoTune
├── JavaBackendInstaller
├── DockerInstaller
├── DatabaseToolsInstaller
├── IdeToolsInstaller
├── FontInstaller
├── GnomeThemeSetup
├── WallpaperSetup
├── GnomeExtensionsSetup
├── SnapperSetup
├── DotfilesSetup
└── DisableUnnecessaryServices

PostInstallOrchestrator  — orquestra todos os steps e exibe o relatório
```

Exceções customizadas (`CommandError`, `NetworkError`, `PrivilegeError`) garantem que falhas sejam capturadas e reportadas sem interromper as etapas seguintes.

---

## Após a execução

Após a conclusão do script, **reinicie a sessão** (ou o sistema) para que todas as mudanças tenham efeito:

```bash
reboot
```

Itens que requerem atenção pós-reboot:

- **Docker**: faça logout e login novamente para que o grupo `docker` seja reconhecido sem `sudo`
- **amd\_pstate**: o modo `active` entra em efeito apenas após reboot
- **ZSH**: se o shell padrão foi alterado, abrirá automaticamente na próxima sessão
- **Snapper**: verifique os snapshots com `snapper list`
- **Plugins tmux**: na primeira sessão tmux, pressione `prefix + I` para instalar os plugins
