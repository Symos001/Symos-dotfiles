return {
  -- Configure conform.nvim for Allman style formatting in Java
  {
    "stevearc/conform.nvim",
    opts = function(_, opts)
      opts.formatters_by_ft = opts.formatters_by_ft or {}
      opts.formatters_by_ft.java = { "clang-format" }

      opts.formatters = opts.formatters or {}
      opts.formatters["clang-format"] = {
        prepend_args = {
          "--style={BasedOnStyle: Google, BreakBeforeBraces: Allman, ColumnLimit: 120, IndentWidth: 4, Language: Java}",
        },
      }
    end,
  },

  -- Ensure clang-format is installed via Mason
  {
    "williamboman/mason.nvim",
    opts = function(_, opts)
      opts.ensure_installed = opts.ensure_installed or {}
      vim.list_extend(opts.ensure_installed, { "clang-format" })
    end,
  },

  -- Add Java to treesitter ensure_installed
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      if type(opts.ensure_installed) == "table" then
        vim.list_extend(opts.ensure_installed, { "java" })
      end
    end,
  },
}
