" Location:     autoload/speeddating.vim

" Initialization {{{1

if !exists("g:loaded_speeddating") || &cp || v:version < 700
  finish
endif

let s:cpo_save = &cpo
set cpo&vim


function! vimtk#execute_text_in_terminal(...) range
    " Interactive scripting function. Takes part of the file you are editing
    " and pastes it into a terminal and then returns the editor to focus.
Python2or3 << EOF
import vimtk  #, imp; imp.reload(vimtk)

argv = vimtk.vim_argv(defaults=['clipboard', '1'])
#L______________
EOF
endfunction

