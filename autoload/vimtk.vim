" Location:     autoload/vimtk.vim

if !exists("g:loaded_vimtk_autoload")  && !exists('g:loaded_vimtk')
  finish
endif
let g:loaded_vimtk_autoload = 1

let s:cpo_save = &cpo
set cpo&vim


func! vimtk#helloworld()
echo "hello world from vim!"
Python2or3 << EOF
"""
Hello world example. 

Also a useful place for debugging the vim python module.

Suggested Binding:
    noremap <leader>H :call vimtk#helloworld()<Esc>
"""
import vim
try:
    import vimtk
except Exception:
    print('Error using vimtk')
    import sys

    import os
    # Hack to try and install deps
    print('HACK: VIMTK IS ATTEMPTING TO INSTALL DEPS!')
    print('HACK: THIS WILL REQUIRE A RESTART OF VIM IF IT WORKS')
    os.system(sys.prefix + '/bin/python' + str(sys.version_info.major) + ' -m pip install ubelt -U')
    os.system(sys.prefix + '/bin/python' + str(sys.version_info.major) + ' -m pip install pyperclip -U')
    print('sys.prefix = {!r}'.format(sys.prefix))
    print('sys.executable = {!r}'.format(sys.executable))
    print('sys.version_info = {!r}'.format(sys.version_info))
    raise


#print = vimtk.logger.info
print('hello world from python')

print('Python in Vim Variables')

buf = vim.current.buffer
print('vim.current.buffer = {!r}'.format(vim.current.buffer))

print(' * vim.current.buffer.name = {}'.format(vim.current.buffer.name))
print(' * len(vim.current.buffer) = {}'.format(len(vim.current.buffer)))
print(' * row, col) = vim.current.window.cursor = {}'.format(vim.current.window.cursor))

print('vim.current.buffer[0] = {!r}'.format(buf[0]))
print('vim.current.buffer[1] = {!r}'.format(buf[1]))
print('vim.current.buffer[0:2] = {!r}'.format(buf[0:2]))
print('vim.current.buffer[-1] = {!r}'.format(buf[-1]))

print('buf = {!r}'.format(buf))
print('buf.mark = {!r}'.format(buf.mark))
print('buf.mark(<) = {!r}'.format(buf.mark('<')))
print('buf.mark(>) = {!r}'.format(buf.mark('>')))

print('mark a = {!r}'.format(buf.mark('a')))

print('vimtk.__version__ = {!r}'.format(vimtk.__version__))

EOF
endfunc


func! vimtk#execute_text_in_terminal(...) range
Python2or3 << EOF
"""
Interactive scripting function. Takes part of the file you are editing
and pastes it into a terminal and then returns the editor to focus.

Args:
    mode (str): clipboard, word, line, or visual
    return_to_vim (bool): if True, returns focus to vim after we paste
        (defaults to True)

Suggested Binding:
  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

"""
import vimtk

#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#vimtk.reload()

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
endfunc



func! vimtk#copy_current_fpath()
Python2or3 << EOF
"""
Copies the absolute path to the current file into your clipboard

Suggested Binding:
    noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
"""

import vimtk
import ubelt as ub
fpath = vimtk.get_current_fpath()
if not ub.WIN32:
    fpath = ub.compressuser(fpath)
vimtk.Clipboard.copy(fpath)
vimtk.logger.info('fpath = {!r}'.format(fpath))
EOF
endfunc



func! vimtk#ipython_import_all()
Python2or3 << EOF
"""
Imports global variables from current module into IPython session

Notes:
    calls vimtk.execute_text_in_terminal, which depends on gVim

Suggested Binding:
    noremap <leader>M :call vimtk#ipython_import_all()<CR>
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

# TODO: mkinit will soon have a generate import * func
# Use that instead.

if vimtk.Python.is_module_pythonfile():
    import vim
    modpath = vim.current.buffer.name
    modname = ub.modpath_to_modname(modpath)

    # HACK to add symlinks back into the paths for system uniformity
    special_symlinks = [
        # ('/media/joncrall/raid/code', expanduser('~/code')),
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
        #lines.append('import sys')
        #lines.append('sys.path.append(%r)' % (basepath,))

        user_basepath = ub.compressuser(basepath)
        if user_basepath != basepath:
            lines.append('import sys, ubelt')
            lines.append('sys.path.append(ubelt.expandpath(%r))' % (user_basepath,))
        else:
            lines.append('import sys')
            lines.append('sys.path.append(%r)' % (basepath,))

    lines.append("from {} import *  # NOQA".format(modname))
    # Add private and protected functions, even if they wouldnt be exposed
    try:
        sourcecode = open(modpath, 'r').read()
        # TODO get classes and whatnot
        try:
            func_names = pyinspect.parse_function_names(sourcecode)
            if '__all__' in sourcecode:
                # completely disregard __all__
                import_names, modules = pyinspect.parse_import_names(sourcecode, branch=False)
                extra_names = list(func_names) + list(import_names)
            else:
                extra_names = [name for name in func_names if name.startswith('_')]
        except SyntaxError as ex:
            vimtk.logger.info('ex = {!r}'.format(ex))
            extra_names = []
            lines.append('# vimtk encountered a syntax error')

        if len(extra_names) > 0:
            extra = ', '.join(extra_names)
            lines.append("from {} import {}".format(modname, extra))

    except Exception as ex:
        #vimtk.logger.info(repr(ex))
        import traceback
        tbtext = traceback.format_exc()
        vimtk.logger.error(tbtext)
        vimtk.logger.error(repr(ex))
        raise
    # Prepare to send text to xdotool
    text = textwrap.dedent('\n'.join(lines))
    vimtk.execute_text_in_terminal(text)
else:
    vimtk.logger.info('current file is not a pythonfile')
EOF
endfunc



func! vimtk#insert_auto_import() 
Python2or3 << EOF
"""
Introspects the current Python file, and attempts to automatically insert
missing import statements.

Suggested Binding:
    command! AutoImport call vimtk#insert_auto_import()
"""
import vim
import ubelt as ub
import vimtk

fpath = vimtk.get_current_fpath()

vimtk.ensure_normalmode()
if vimtk.Python.is_module_pythonfile():
    import_block = vimtk.autogen_imports(fpath)
    offset = import_block.count('\n')
    # FIXME: doesnt work right when row=0
    # Note: row is 1 indexed, and cannot be zero
    with vimtk.CursorContext(offset=offset):
        vimtk.Python.prepend_import_block(import_block)
else:
    vimtk.logger.info('current file is not a pythonfile')

EOF
endfunc


func! vimtk#insert_print_var_at_cursor(...)
Python2or3 << EOF
"""
Inserts a line of code that prints the current variable under the cursor

Currently supports the following languages:
    C++, Bash, CMake, Python

Suggested Binding:
    noremap <leader>pv :call vimtk#insert_print_var_at_cursor()<CR>
"""
import vim
import vimtk
import ubelt as ub

argv = vimtk.vim_argv(defaults=['repr'])

if len(argv) != 1:
    raise Exception('only one argument')
else:
    mode = argv[0]

expr = vimtk.TextSelector.word_at_cursor()
indent = vimtk.TextSelector.current_indent()

filetype = vimtk.get_current_filetype()
if filetype == 'sh':
    language = 'sh'
elif filetype in {'cmake'}:
    language = 'cmake'
elif filetype in {'cpp', 'cxx', 'h'}:
    language = 'cpp'
elif filetype in {'vue', 'js'}:
    language = 'javascript'
elif filetype in {'py'}:
    language = 'py'
else:
    language = 'py'  # Default to python

if language == 'sh':
    statement = 'echo "{expr} = ${expr}"'.format(expr=expr)
elif language == 'cmake':
    statement = 'message(STATUS "{expr} = ${{{expr}}}")'.format(expr=expr)
elif language == 'javascript':
    statement = 'console.log("{expr} = " + {expr});'.format(expr=expr)
    # try to play nice with js linter
    maxlen = 80 - len(indent)
    if len(statement) > maxlen:
        parts = [
            '"{expr} = " + '.format(expr=expr),
            '{expr}'.format(expr=expr),
        ]
        body = '  ' + ''.join(parts)
        header = 'console.log('
        footer = ');'
        if len(body) < maxlen:
            statement = '\n'.join([header, body, footer])
        else:
            statement = '\n'.join([header, '  ' + parts[0], '    ' + parts[1], footer])
elif language == 'py':
    if mode == 'repr':
        statement = "print('{expr} = {{!r}}'.format({expr}))".format(expr=expr)
    elif mode == 'repr2':
        statement = "print('{expr} = {{}}'.format(ub.repr2({expr}, nl=1)))".format(expr=expr)
    else:
        raise KeyError(mode)
elif language == 'cpp':
    current_fpath = vimtk.get_current_fpath()

    # TODO: register a way to use loggers
    REGISTRED_CPP_LOGGING_MODULES = ['kwiver', 'sprokit', 'vital']
    # REGISTRED_CPP_LOGGING_MODULES = []

    if any(n in current_fpath for n in REGISTRED_CPP_LOGGING_MODULES):
        if vimtk.find_pattern_above_row(
            '\s*auto logger = kwiver::vital::get_logger.*') is None:
            statement = ub.codeblock(
                '''
                auto logger = kwiver::vital::get_logger("temp.logger");
                LOG_INFO(logger, "{expr} = " << {expr} );
                '''
            ).format(expr=expr)
        else:
            statement = ub.codeblock(
                '''
                LOG_INFO(logger, "{expr} = " << {expr} );
                '''
            ).format(expr=expr)
    else:
        cout = 'std::cout'
        endl = 'std::endl'
        #statement = '{cout} << "{expr} = \\"" << {expr} << "\\"" << {endl};'.format(
        #    expr=expr, cout=cout, endl=endl)
        statement = '{cout} << "{expr} = " << {expr} << {endl};'.format(
            expr=expr, cout=cout, endl=endl)
else:
    raise KeyError(language)

newline = indent + statement.replace('\n', '\n' + indent)
vimtk.TextInsertor.insert_under_cursor(newline)
EOF
endfunc


func! vimtk#insert_timerit(...) range
Python2or3 << EOF
"""
Suggested Bindings:
    noremap  <c-M-B> :call vimtk#insert_timerit(mode())<CR><Esc>
    vnoremap <c-M-B> :call vimtk#insert_timerit(visualmode())<CR><Esc>
"""
import vim
import ubelt as ub
mode = vim.eval('a:1')
indent = vimtk.TextSelector.current_indent()
newtext = '\n'.join([
    indent + 'import timerit',
    indent + 'ti = timerit.Timerit(100, bestof=10, verbose=2)',
    indent + 'for timer in ti.reset(\'time\'):',
    indent + '    with timer:',
])
if 'v' in mode.lower():
    selected = vimtk.TextSelector.selected_text()
    newtext += '\n' + ub.indent(selected, ' ' * 8)
    vimtk.TextInsertor.insert_over_selection(newtext)
else:
    vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc



func! vimtk#smart_search_word_at_cursor()
Python2or3 << EOF
"""
Determines if the word at the cursor is a url and opens it in a webbrowser

Suggested Binding:
    noremap <leader>es :call vimtk#smart_search_word_at_cursor()<CR>
"""
import vim
import vimtk
word = vimtk.TextSelector.word_at_cursor(url_ok=True)
url = vimtk.extract_url_embeding(word)
print('url = {!r}'.format(url))
import webbrowser
webbrowser.open(url)
EOF
endfunc



func! vimtk#open_path_at_cursor(...) 
Python2or3 << EOF
"""
Does a fancy open of a path at the current cursor position in vim

Args:
    *argv: [command, [path]]
        command is the type of way you open in vim, defaults to 'split'
        path defaults to the current 'word' under cursor

Behavior depends on path:
   * If path isurl: open with OS webbrowser
   * If path isdir: open directory
   * If path isfile: open file
   * If path looks like a python module: 
       try to statically find and open that
   * If path doesnt exist:
       * Look down a few directories to see if its relative to something
         else (really helps for navigating C++).


Suggested Bindings:
    " In current v/split or new tab
    noremap <leader>go :call vimtk#open_path_at_cursor("e")<CR>
    noremap <leader>gf :call vimtk#open_path_at_cursor("e")<CR>
    noremap <leader>gi :call vimtk#open_path_at_cursor("split")<CR>
    noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
    noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
    noremap <leader>gt :call vimtk#open_path_at_cursor("tabe")<CR>
    noremap gi :call vimtk#open_path_at_cursor("split")<CR>

Ignore:
call vimtk#open_path_at_cursor('split', '~/local/vim/vimfiles/bundle/vimtk/autoload/vimtk.vim')
call vimtk#open_path_at_cursor('split', '~')
call vimtk#open_path_at_cursor('split', 'google.com')
"""
import vim
import re
from os.path import exists, expanduser
import vimtk

argv = vimtk.vim_argv(defaults=['split'])
mode = argv[0]
print('argv = {!r}'.format(argv))

if len(argv) >= 2:
    path = argv[1]
else:
    path = vimtk.TextSelector.word_at_cursor(url_ok=True)

#print = vimtk.logger.info
print('vimtk#open_path_at_cursor path = {!r}'.format(path))
print('exists = {!r}'.format(exists(path)))

vimtk.find_and_open_path(path, mode=mode, verbose=1)
EOF
endfunc


func! vimtk#quickopen(...)
Python2or3 << EOF
"""
This is a shortcut for opening commonly used files

Use <leader> -> t, v, i, or o -> your key to quickly open a file

Previously called QUICKOPEN_leader_tvio


Maps <leader>t<key> to tab open a filename
Maps <leader>s<key> to vsplit open a filename
Maps <leader>i<key> to split open a filename

Suggested Bindings:
    " Map leader key to comma (in all contexts)
    let mapleader = ","
    let maplocalleader = ","
    noremap \ ,

    call vimtk#quickopen(',', '~/.vimrc')
    call vimtk#quickopen(',', '~/.vimrc')

"""
EOF
    let key = a:1
    let fname = a:2
    :exec 'noremap <leader>t'.key.' :tabe '.fname.'<CR>'
    :exec 'noremap <leader>v'.key.' :vsplit '.fname.'<CR>'
    :exec 'noremap <leader>i'.key.' :split '.fname.'<CR>'
    :exec 'noremap <leader>o'.key.' :e '.fname.'<CR>'
endfu



func! vimtk#remap_all_modes(lhs, rhs)
    " Function which remaps keys in all modes
    "
    ":echom 'inoremap '.a:lhs.' '.a:rhs
    "http://vim.wikia.com/wiki/Mapping_keys_in_Vim_-_Tutorial_(Part_1)
    "  CHAR	MODE	~
    " <Space>	Normal, Visual, Select and Operator-pending
	"n	Normal
	"v	Visual and Select
	"s	Select
	"x	Visual
	"o	Operator-pending
	"!	Insert and Command-line
	"i	Insert
	"l	":lmap" mappings for Insert, Command-line and Lang-Arg
	"c	Command-line
    "--------------
    " Normal Mode
    :exec 'noremap '.a:lhs.' '.a:rhs
    " Visual and Select Mode
    :exec 'vnoremap '.a:lhs.' '.a:rhs
    " Display select mode map
    :exec 'snoremap '.a:lhs.' '.a:rhs
    " Display visual mode maps
    :exec 'xnoremap '.a:lhs.' '.a:rhs
    " Operator Pending Mode
    :exec 'onoremap '.a:lhs.' '.a:rhs
    " Insert and Replace Mode
    :exec 'inoremap '.a:lhs.' '.a:rhs
    " Language Mode
    :exec 'lnoremap '.a:lhs.' '.a:rhs
    " Command Line Mode
    :exec 'cnoremap '.a:lhs.' '.a:rhs
    " Make r<lhs> do the right thing
    :exec 'noremap r'.a:lhs.' r'.a:rhs
    :exec 'noremap f'.a:lhs.' r'.a:rhs
endfu


func! vimtk#swap_keys(lhs, rhs)
    " Swaps the functionality of two keys
    :call vimtk#remap_all_modes(a:lhs, a:rhs)
    :call vimtk#remap_all_modes(a:rhs, a:lhs)
endfu


func! vimtk#py_format_doctest() range
Python2or3 << EOF
"""
Inserts docstring chevrons
"""
import vim
import vimtk
text = vimtk.TextSelector.selected_text()
text2 = vimtk.Python.format_text_as_docstr(text)
vimtk.TextInsertor.insert_over_selection(text2)
EOF
endfunc


func! vimtk#py_unformat_doctest() range
Python2or3 << EOF
"""
Removes docstring chevrons
"""
import vim
import pyvim_funcs; pyvim_funcs.reload(pyvim_funcs)
text = vimtk.TextSelector.selected_text()
text2 = vimtk.Python.unformat_text_as_docstr(text)
vimtk.TextInsertor.insert_over_selection(text2)
EOF
endfunc



" Source helpers relative to this file
"execute 'source ' . expand('<sfile>:p:h') . '/vimtk_snippets.vim'
