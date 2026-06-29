return {
  -- Mantém o Nightfox/Terafox instalado
  {
    "EdenEast/nightfox.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      require("nightfox").setup({
        options = { transparent = false },
      })
    end,
  },

  -- Instala e ativa o OneDark
  {
    "navarasu/onedark.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      require("onedark").setup({
        style = "darker",
        transparent = false,
      })
      -- Carrega explicitamente o OneDark na inicialização
      require("onedark").load()
    end,
  },

  -- Define o OneDark como padrão no LazyVim
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "onedark",
    },
  },
}
