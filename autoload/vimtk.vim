" Location:     autoload/vimtk.vim

if !exists("g:loaded_vimtk_autoload")  || !exists('g:loaded_vimtk')
  finish
endif
let g:loaded_vimtk_autoload = 1

let s:cpo_save = &cpo
set cpo&vim


function! vimtk#helloworld()
   echo "hello world!"
endfunction


function! vimtk#execute_text_in_terminal(...) range
"╔═════════════════════════════════════════════════
Python2or3 << EOF
"""

------------------------------
vimtk#execute_text_in_terminal
------------------------------

    Interactive scripting function. Takes part of the file you are editing
    and pastes it into a terminal and then returns the editor to focus.

    Args:
        mode (str): clipboard, word, line, or visual
        return_to_vim (bool): if True, returns focus to vim after we paste
            (defaults to True)
"""
import vimtk

#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
vimtk.reload()

argv = vimtk.vim_argv(defaults=['clipboard', '1'])
mode = argv[0]
return_to_vim = argv[1] != '0'

vimtk.logger.debug(('CALL FUNCTION vimtk#execute_text_in_terminal('
                    'mode={mode!r}, return_to_vim={return_to_vim!r}'
                    ')').format(**locals()))

vimtk.logger.debug('Get text from mode={}'.format(mode))
if mode == 'clipboard':
    vimtk.logger.debug('Text is already in clipboard')
    text = vimtk.Clipboard.paste()
    vimtk.logger.debug('got text')
    vimtk.logger.debug('text = %r' % (text,))
else:
    if mode == 'word':
        text = vimtk.TextSelector.word_at_cursor()
    else:
        if 'v' in mode.lower():
            text = vimtk.TextSelector.selected_text()
        else:
            text = vimtk.TextSelector.line_at_cursor()

text = vimtk.preprocess_executable_text(text)
vimtk.execute_text_in_terminal(text, return_to_vim=return_to_vim)

EOF
"╚═════════════════════════════════════════════════
endfunction



func! vimtk#copy_current_fpath()
Python2or3 << EOF
import vimtk
import ubelt as ub
fpath = vimtk.get_current_fpath()
if not ub.WIN32:
    fpath = ub.compressuser(fpath)
print('fpath = {!r}'.format(fpath))
vimtk.Clipboard.copy(fpath)
EOF
endfunc



function! vimtk#ipython_import_all()
"╔═════════════════════════════════════════════════
Python2or3 << EOF
"""
------------------------------
vimtk#ipython_import_all
------------------------------

Imports global variables from current module into IPython session
"""
import vimtk
from vimtk import pyinspect
from os.path import dirname, expanduser
from os.path import basename, splitext
import ubelt as ub
import textwrap

#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#vimtk.reload()
vimtk.reload()

if vimtk.is_module_pythonfile():
    import vim
    modpath = vim.current.buffer.name
    modname = ub.modpath_to_modname(modpath)

    # HACK to add symlinks back into the paths for system uniformity
    special_symlinks = [
        ('/media/joncrall/raid/code', expanduser('~/code')),
    ]
    # Abstract via symlinks
    for real, link in special_symlinks:
        if modpath.startswith(real):
            modpath = join(link, relpath(modpath, real))

    lines = []
    if not pyinspect.in_pythonpath(modname):
        # Module is not in PYTHONPATH, make this happen before we run
        # (note this is based on Vim's python, not the terminals.
        #  this check might not always work)
        # 
        # TODO: allow user to force adding to the pythonpath 
        basepath = ub.split_modpath(modpath)[0]
        lines.append('import sys')
        lines.append('sys.path.append(%r)' % (basepath,))

    lines.append("from {} import *".format(modname))
    # Add private and protected functions, even if they wouldnt be exposed
    try:
        sourcecode = open(modpath, 'r').read()
        # TODO get classes and whatnot
        func_names = pyinspect.parse_function_names(sourcecode)
        if '__all__' in sourcecode:
            # completely disregard __all__
            import_names, modules = pyinspect.parse_import_names(sourcecode, branch=False)
            extra_names = list(func_names) + list(import_names)
        else:
            extra_names = [name for name in func_names if name.startswith('_')]
        if len(extra_names) > 0:
            lines.append("from {} import {}".format(
                modname, ', '.join(extra_names)))
    except Exception as ex:
        #print(repr(ex))
        import traceback
        tbtext = traceback.format_exc()
        vimtk.logger.error(tbtext)
        vimtk.logger.error(repr(ex))
        raise
    # Prepare to send text to xdotool
    text = textwrap.dedent('\n'.join(lines))
    vimtk.execute_text_in_terminal(text)
else:
    print('current file is not a pythonfile')
#L______________
EOF
endfu 

