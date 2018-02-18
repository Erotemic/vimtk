" vimtk.vim - 
" Author:   Jon Crall
" Version:      0.0.1

" Initialization

if &cp || v:version < 700
  finish
endif

"if exists("g:loaded_vimtk") 
"  finish
"endif
let g:loaded_vimtk = 1
"echo "Loading VimTK"


let g:_VIMTK_VERSION = '0.0.0'
"lockvar g:_VIMTK_VERSION


" Disable user settings
let s:cpo_save = &cpo
set cpo&vim


if has('python3')
    command! -nargs=1 Python2or3 python3 <args>
elseif has('python')
    command! -nargs=1 Python2or3 python <args>
else
    echo "Error: VimTk requires that Vim be compiled with +python or +python3"
    finish
endif


function! VimTK_default_remap() 
  " copy and execute the current line, word, or visual selection in the terminal 
  "echo "Setting up VimTK default mappings"
  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

  noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
  noremap <leader>M :call vimtk#ipython_import_all()<CR>
endfunction()


if exists("g:vimtk_default_mappings") && g:vimtk_default_mappings
  :call VimTK_default_remap()
endif

" Setup the PYTHONPATH for the vimtk python module
Python2or3 << EOF
# We can not call this in a function or we wont get the right filename
from os.path import dirname 
thisfile = vim.eval("expand('<sfile>:p')")
repodir = dirname(dirname(thisfile))
import sys
sys.path.append(repodir)
EOF




" Reload user's settings
let &cpo = s:cpo_save
" vim:set et sw=2 sts=2:
