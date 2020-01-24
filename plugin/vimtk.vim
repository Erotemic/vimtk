" vimtk.vim - 
" Author:   Jon Crall
" Version:      0.2.3

" Initialization

if &cp || v:version < 700
  finish
endif

" TODO ensure _VIMTK_VERSION is synced with the python version
" which is defined in: ~/code/vimtk/vimtk/__init__.py
let g:_VIMTK_VERSION = '0.2.2'

"if exists("g:loaded_vimtk") 
"  finish
"endif
let g:loaded_vimtk = 1
"echo "Loading VimTK"


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
  " These functions are defined in 
  " ../autoload/vimtk.vim
  " ~/code/vimtk/autoload/vimtk.vimtk
  noremap <leader>H :call vimtk#helloworld()<Esc>

  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

  noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
  noremap <leader>M :call vimtk#ipython_import_all()<CR>

  command! AutoImport call vimtk#insert_auto_import()

  noremap <leader>pv :call vimtk#insert_print_var_at_cursor("repr")<CR>
  noremap <leader>ps :call vimtk#insert_print_var_at_cursor("repr2")<CR>

  noremap  <c-M-B> :call vimtk#insert_timerit(mode())<CR><Esc>
  vnoremap <c-M-B> :call vimtk#insert_timerit(visualmode())<CR><Esc>

  noremap <leader>es :call vimtk#smart_search_word_at_cursor()<CR>
  noremap <leader>go :call vimtk#open_path_at_cursor("e")<CR>
  noremap <leader>gf :call vimtk#open_path_at_cursor("e")<CR>
  noremap <leader>gi :call vimtk#open_path_at_cursor("split")<CR>
  noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
  noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
  noremap <leader>gt :call vimtk#open_path_at_cursor("tabe")<CR>
  noremap gi :call vimtk#open_path_at_cursor("split")<CR>

  " Doctest editing
  vnoremap gd :call vimtk#py_format_doctest()<CR>
  vnoremap gu :call vimtk#py_unformat_doctest()<CR>

endfunction


function! VimTK_suggested_remap() 
  let mapleader = ","
  let maplocalleader = ","
  noremap \ ,

  call VimTK_default_remap()

  call vimtk#quickopen(',', '~/.vimrc')
  call vimtk#quickopen('5', '~/.bashrc')

endfunction


" Define top-level API commands
"command! AutoImport call vimtk#insert_auto_import()


if exists("g:vimtk_default_mappings") && g:vimtk_default_mappings
  :call VimTK_default_remap()
endif

" Setup the PYTHONPATH for the vimtk python module
Python2or3 << ENDPYTHON
# --------------
import sys
from os.path import dirname 
# We can not call this in a function or we wont get the right filename
thisfile = vim.eval("expand('<sfile>:p')")
repodir = dirname(dirname(thisfile))
sys.path.append(repodir)
# --------------
ENDPYTHON


func! QUICKOPEN_leader_tvio(...)
    " TODO: remove for plugin
    " Maps <leader>t<key> to tab open a filename
    " Maps <leader>s<key> to vsplit open a filename
    " Maps <leader>i<key> to split open a filename
    let key = a:1
    let fname = a:2
    :exec 'noremap <leader>t'.key.' :tabe '.fname.'<CR>'
    :exec 'noremap <leader>v'.key.' :vsplit '.fname.'<CR>'
    :exec 'noremap <leader>i'.key.' :split '.fname.'<CR>'
    :exec 'noremap <leader>o'.key.' :e '.fname.'<CR>'
endfu


"Python2or3 << ENDPYTHON
"# ensure _VIMTK_VERSION is synced with the python version
"import vimtk
"import vim
"print(dir(vim))
"print('vim.vars = {!r}'.format(vim.vars))
"print('vim.vars = {!r}'.format(vim.vvars.keys()))
"vim.eval('let g:_VIMTK_VERSION = {!r}'.format(vimtk.__version__)) 
"ENDPYTHON
""lockvar g:_VIMTK_VERSION



" Reload user's settings
let &cpo = s:cpo_save
" vim:set et sw=2 sts=2:
