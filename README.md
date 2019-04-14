# VimTk - The Vim toolkit 

A set of utilities for Vim.

The tools in this package focus on, but are not exclusive to Python development
with GVim.  This is both a Vim plugin and a pip installable Python module.

## Development Installation with Pathogen

ln -s ~/code/vimtk ~/.vim/bundle/vimtk


## Testing

vim -c ':redir > vimtk_test.output' -c ":echo 'hello' | exit" && cat vimtk_test.output


## Usage

This module defines many helper functions, but does not bind them to keys by
default. However, to use the suggested default mapping you can set this
variable in your vimrc:

```vim
let g:vimtk_default_mappings=1
```

Setting this variable to 1 will execute this exact code when the plugin is loaded.

```vim
noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
noremap <leader>M :call vimtk#ipython_import_all()<CR>
```


Currently this "toolkit" has three functions

* `vimtk#execute_text_in_terminal` ---
    copies the current word, line, or visual selection and executes it in
    your most recently used terminal (perhaps running IPython or bash) without
    needing to alt-tab or copy paste.

* `vimtk#ipython_import_all` --- if you are in a python module, 
    this funciton creates a few lines of code that will import 
    everything in this module into the current namespace. Note, 
    it detects if you need to modify your pythonpath and does that.
    It also completely disregards `__all__`. These lines are then executed in
    your terminal (which should probably be an IPython session)

* `vimtk#copy_current_fpath` --- Copies the path to the current file into the
  clipboard. On non-windows the home drive is replae with `~`.
