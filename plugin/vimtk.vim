" vimtk.vim - 
" Maintainer:   Jon Crall
" Version:      0.0.0
" GetLatestVimScripts: 2120 1 :AutoInstall: vimtk.vim

" Initialization {{{1

if exists("g:loaded_vimtk") || &cp || v:version < 700
  finish
endif
let g:loaded_vimtk = 1
" Disable user settings
let s:cpo_save = &cpo
set cpo&vim
" header gaurd
if exists('g:vimtk')
  finish
endif


nnoremap <silent> <Plug>ExecuteTextInTerminal   :<C-U>call vimtk#execute_text_in_terminal()<CR>


if !exists("g:vimtk_no_mappings") || !g:vimtk_no_mappings
  nmap  <leader-a>     <Plug>ExecuteTextInTerminal
  xmap  <leader-a>     <Plug>ExecuteTextInTerminal
endif



" Prevent re-execution pattern
if exists('g:vimtk_finished')
  finish
endif
let g:vimtk_finished = []


" Reload user's settings
let &cpo = s:cpo_save
" vim:set et sw=2 sts=2:
