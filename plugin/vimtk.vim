" vimtk.vim - 
" Author:   Jon Crall
" Version:      0.2.5

" Initialization

if &cp || v:version < 700
  finish
endif

" TODO ensure _VIMTK_VERSION is synced with the python version
" which is defined in: ~/code/vimtk/vimtk/__init__.py
let g:_VIMTK_VERSION = '0.4.0'

"if exists("g:loaded_vimtk") 
"  finish
"endif
let g:loaded_vimtk = 1


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
  " ~/code/vimtk/autoload/vimtk.vim
  noremap <leader>H :call vimtk#helloworld()<Esc>

  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

  noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
  noremap <leader>f :call vimtk#copy_current_module()<Esc>

  noremap <leader>M :call vimtk#ipython_import_all()<CR>

  command! AutoImport call vimtk#insert_auto_import()

  noremap <leader>pv :call vimtk#insert_print_var_at_cursor("repr")<CR>
  noremap <leader>ps :call vimtk#insert_print_var_at_cursor("urepr")<CR>

  noremap  <c-M-B> :call vimtk#insert_timerit(mode())<CR><Esc>
  vnoremap <c-M-B> :call vimtk#insert_timerit(visualmode())<CR><Esc>

  " This is cool, but dont use it by default
  "noremap <leader>es :call vimtk#smart_search_word_at_cursor()<CR>

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


" This is a good idea, but ultimately unused.
" and the user should probably do it themselves.
"function! VimTK_suggested_remap() 
"  let mapleader = ","
"  let maplocalleader = ","
"  noremap \ ,

"  call VimTK_default_remap()

"  call vimtk#quickopen(',', '~/.vimrc')
"  call vimtk#quickopen('5', '~/.bashrc')

"endfunction


" Define top-level API commands
"command! AutoImport call vimtk#insert_auto_import()


" We may want to discourage this in favor of explicitly defining the mappings.
" Not sure.
if exists("g:vimtk_default_mappings") && g:vimtk_default_mappings
  :call VimTK_default_remap()
endif

" Setup the PYTHONPATH for the vimtk python module
python3 << ENDPYTHON
# --------------
import sys
from os.path import dirname 
# We can not call this in a function or we wont get the right filename
vimtk_plugin_fpath = vim.eval("expand('<sfile>:p')")
vimtk_repodir = dirname(dirname(vimtk_plugin_fpath))
# Ensure that Python uses the vimtk module inside this repo.
sys.path.insert(0, vimtk_repodir)
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


"python3 << ENDPYTHON
"# ensure _VIMTK_VERSION is synced with the python version
"import vimtk
"import vim
"print(dir(vim))
"print('vim.vars = {!r}'.format(vim.vars))
"print('vim.vars = {!r}'.format(vim.vvars.keys()))
"vim.eval('let g:_VIMTK_VERSION = {!r}'.format(vimtk.__version__)) 
"ENDPYTHON
""lockvar g:_VIMTK_VERSION


"func! Vimtk_Reload()
"let __doc__ =<< trim __DOC__
"FIXME: broken, is there any way to do this?
"A workaround is to define this function in your vimrc
"Reloads vimtk after changes are made or it is updated
"__DOC__
"" Unset the guard flags
"let g:loaded_vimtk_autoload = 0
"let g:loaded_vimtk = 0
"":source $MYVIMRC
":exec "source " . g:vimtk_autoload_fpath
"endfunc



" Reload user's settings
let &cpo = s:cpo_save
" vim:set et sw=2 sts=2:
