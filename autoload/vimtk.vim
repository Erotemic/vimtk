" Location:     autoload/vimtk.vim
scriptencoding utf-8


if !exists("g:loaded_vimtk_autoload") && !exists('g:loaded_vimtk')
  finish
endif
let g:loaded_vimtk_autoload = 1

let s:cpo_save = &cpo
set cpo&vim


" Save the path to this file
" Reference: https://stackoverflow.com/questions/4976776/how-to-get-path-to-the-current-vimscript-being-executed
let g:vimtk_autoload_core_fpath=expand("<sfile>")


func! vimtk#helloworld()
echo "hello world from vim!"
python3 << EOF
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
    def sys_executable():
        """
        Find the system executable. For whatever reason, vim messes with it.

        References:
            https://github.com/ycm-core/YouCompleteMe/blob/ba7a9f07a57c657c684edb5dde1f1f1dda1c0c7a/python/ycm/paths.py
            https://github.com/davidhalter/jedi-vim/issues/870
        """
        import re
        import os
        import sys
        from os.path import join, exists
        if sys.platform.startswith('win32'):
            executable = join(sys.exec_prefix, 'python.exe')
        else:
            bin_dpath = join(sys.exec_prefix, 'bin')
            assert exists(bin_dpath)
            pyexe_re = re.compile(r'python([23](\.[5-9])?)?(.exe)?$', re.IGNORECASE )
            candiates = os.listdir(bin_dpath)
            found = []
            for cand in candiates:
                if pyexe_re.match(cand):
                    fpath = join(bin_dpath, cand)
                    if os.path.isfile(fpath):
                        if os.access(fpath, os.X_OK):
                            found.append(fpath)
            assert len(found) > 0
            executable = found[0]
        return executable

    our_executable = sys_executable()
    print('our_executable = {!r}'.format(our_executable))
    print('sys.base_exec_prefix = {!r}'.format(sys.base_exec_prefix))
    print('sys.base_prefix = {!r}'.format(sys.base_prefix))
    print('sys.exec_prefix = {!r}'.format(sys.exec_prefix))
    print('sys.executable = {!r}'.format(sys.executable))
    print('sys.implementation = {!r}'.format(sys.implementation))
    print('sys.prefix = {!r}'.format(sys.prefix))
    print('sys.version = {!r}'.format(sys.version))
    print('sys.path = {!r}'.format(sys.path))
    print('sys.version_info = {!r}'.format(sys.version_info))
    # Hack to try and install deps

    INSTALL_HACK = True
    if INSTALL_HACK:
        print('HACK: VIMTK IS ATTEMPTING TO INSTALL DEPS!')
        print('HACK: THIS WILL REQUIRE A RESTART OF VIM IF IT WORKS')
        commands = [
            our_executable + ' -m pip install ubelt -U --user',
            our_executable + ' -m pip install pyperclip -U --user',
            our_executable + ' -m pip install pyflakes -U --user',
        ]
        for command in commands:
            print('command = {!r}'.format(command))
            ret = os.system(command)
            print('ret = {!r}'.format(ret))
        print('HACK: ATTEMPTED TO INSTALL DEPS')
    raise


#print = vimtk.logger.info
print('hello world from python')

print('Python in Vim Variables')

buf = vim.current.buffer
print('vim.current.buffer = {!r}'.format(vim.current.buffer))

print(' * vim.current.buffer.name = {}'.format(vim.current.buffer.name))
print(' * len(vim.current.buffer) = {}'.format(len(vim.current.buffer)))
print(' * row, col) = vim.current.window.cursor = {}'.format(vim.current.window.cursor))

if len(buf) > 0:
    print('vim.current.buffer[0] = {!r}'.format(buf[0]))
    if len(buf) > 1:
        print('vim.current.buffer[1] = {!r}'.format(buf[1]))
    print('vim.current.buffer[0:2] = {!r}'.format(buf[0:2]))
    print('vim.current.buffer[-1] = {!r}'.format(buf[-1]))

print('buf = {!r}'.format(buf))
print('buf.mark = {!r}'.format(buf.mark))
print('buf.mark(<) = {!r}'.format(buf.mark('<')))
print('buf.mark(>) = {!r}'.format(buf.mark('>')))

print('mark a = {!r}'.format(buf.mark('a')))


our_executable = vimtk.sys_executable()
print('our_executable = {!r}'.format(our_executable))
print('sys.base_exec_prefix = {!r}'.format(sys.base_exec_prefix))
print('sys.base_prefix = {!r}'.format(sys.base_prefix))
print('sys.exec_prefix = {!r}'.format(sys.exec_prefix))
print('sys.executable = {!r}'.format(sys.executable))
print('sys.implementation = {!r}'.format(sys.implementation))
print('sys.prefix = {!r}'.format(sys.prefix))
print('sys.version = {!r}'.format(sys.version))
print('sys.path = {!r}'.format(sys.path))
print('sys.version_info = {!r}'.format(sys.version_info))
# Hack to try and install deps

print('vimtk.__version__ = {!r}'.format(vimtk.__version__))
print('vimtk.__file__ = {!r}'.format(vimtk.__file__))

EOF
endfunc


func! vimtk#execute_text_in_terminal(...) range
python3 << EOF
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
python3 << EOF
"""
Copies the absolute path to the current file into your clipboard

Suggested Binding:
    noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
"""

import vimtk
import sys
from os.path import normpath
from vimtk.util import shrinkuser
WIN32   = sys.platform == 'win32'  # type: bool
fpath = vimtk.get_current_fpath()
if not WIN32:
    fpath = shrinkuser(fpath)
vimtk.Clipboard.copy(fpath)
vimtk.logger.info('copied fpath = {!r} to the clipboard'.format(fpath))
EOF
endfunc



func! vimtk#copy_current_module()
python3 << EOF
"""
Assuming the current file is a Python module, this attempts to introspect the
module name and copy it to your clipboard.

Suggested Binding:
    noremap <leader>f :call vimtk#copy_current_module()<Esc>
"""
import vimtk
from vimtk.util import modpath_to_modname
fpath = vimtk.get_current_fpath()
if vimtk.Python.is_module_pythonfile():
    import vim
    modpath = vim.current.buffer.name
    modname = modpath_to_modname(modpath)
    vimtk.Clipboard.copy(modname)
    vimtk.logger.info('copied modname = {!r} to the clipboard'.format(modname))
else:
    vimtk.logger.warn('file is not a python file. Copy the path instead')
    vimtk.Clipboard.copy(fpath)
    vimtk.logger.info('copied filepath = {!r} to the clipboard'.format(modname))
EOF
endfunc



func! vimtk#ipython_import_all()
python3 << EOF
"""
Imports global variables from current module into IPython session

Notes:
    calls vimtk.execute_text_in_terminal, which depends on gVim

Suggested Binding:
    noremap <leader>M :call vimtk#ipython_import_all()<CR>
"""
import vimtk
from vimtk import pyinspect
from vimtk import util
from vimtk.util import modpath_to_modname
from vimtk.util import split_modpath
from os.path import dirname, expanduser
from os.path import basename, splitext
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
    modname = modpath_to_modname(modpath)

    lines = []
    if not pyinspect.in_pythonpath(modname):
        # Module is not in PYTHONPATH, make this happen before we run
        # (note this is based on Vim's python, not the terminals.
        #  this check might not always work)
        # 
        # TODO: allow user to force adding to the pythonpath 
        basepath = split_modpath(modpath)[0]
        #lines.append('import sys')
        #lines.append('sys.path.append(%r)' % (basepath,))

        user_basepath = util.shrinkuser(basepath)
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
python3 << EOF
"""
Introspects the current Python file, and attempts to automatically insert
missing import statements.

Suggested Binding:
    command! AutoImport call vimtk#insert_auto_import()
"""
import vim
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
python3 << EOF
"""
Inserts a line of code that prints the current variable under the cursor

Currently supports the following languages:
    C++, Bash, CMake, Python

Suggested Binding:
    noremap <leader>pv :call vimtk#insert_print_var_at_cursor()<CR>
"""
import vim
import vimtk
from vimtk import util

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
        USE_FORMAT_STRING = sys.version_info[0:2] >= (3, 6)
        if USE_FORMAT_STRING:
            statement = "print(f'%s={%s}')" % (expr, expr,)
            #USE_FORMAT_STRING_EQ = sys.version_info[0:2] >= (3, 8)
            #if USE_FORMAT_STRING_EQ:
            #    # TODO: determine when this is safe
            #    statement = "print(f'%s={%s}')" % (expr, expr,)
            #    #statement = "print(f'{%s=}')" % (expr,)
            #    # = {{!r}}'.format({expr}))".format(expr=expr)
        else:
            statement = "print('{expr} = {{!r}}'.format({expr}))".format(expr=expr)
    elif mode == 'repr2':
        statement = "print('{expr} = {{}}'.format(ub.repr2({expr}, nl=1)))".format(expr=expr)
        statement = "print('{expr} = {{}}'.format(ub.urepr({expr}, nl=1)))".format(expr=expr)
    elif mode == 'urepr':
        USE_F_STRING = sys.version_info[0:2] >= (3, 6)
        if USE_F_STRING:
            statement = "print(f'{expr} = {{ub.urepr({expr}, nl=1)}}')".format(expr=expr)
        else:
            statement = "print('{expr} = {{}}'.format(ub.urepr({expr}, nl=1)))".format(expr=expr)
    else:
        raise KeyError(mode)
elif language == 'cpp':
    current_fpath = vimtk.get_current_fpath()

    # TODO: register a way to use loggers
    REGISTRED_CPP_LOGGING_MODULES = ['kwiver', 'sprokit', 'vital']
    # REGISTRED_CPP_LOGGING_MODULES = []

    if any(n in current_fpath for n in REGISTRED_CPP_LOGGING_MODULES):
        if vimtk.find_pattern_above_row(
            '\\s*auto logger = kwiver::vital::get_logger.*') is None:
            statement = util.codeblock(
                '''
                auto logger = kwiver::vital::get_logger("temp.logger");
                LOG_INFO(logger, "{expr} = " << {expr} );
                '''
            ).format(expr=expr)
        else:
            statement = util.codeblock(
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
python3 << EOF
"""
Suggested Bindings:
    noremap  <c-M-B> :call vimtk#insert_timerit(mode())<CR><Esc>
    vnoremap <c-M-B> :call vimtk#insert_timerit(visualmode())<CR><Esc>
"""
import vim
from vimtk import util
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
    newtext += '\n' + util.indent(selected, ' ' * 8)
    vimtk.TextInsertor.insert_over_selection(newtext)
else:
    vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc



func! vimtk#smart_search_word_at_cursor()
python3 << EOF
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
python3 << EOF
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
#print('argv = {!r}'.format(argv))

if len(argv) >= 2:
    path = argv[1]
else:
    path = vimtk.TextSelector.word_at_cursor(url_ok=True)

#print = vimtk.logger.info
#print('vimtk#open_path_at_cursor path = {!r}'.format(path))
#print('exists = {!r}'.format(exists(path)))

vimtk.find_and_open_path(path, mode=mode, verbose=0)
EOF
endfunc


func! vimtk#quickopen(...)
    " TODO: better heredoc
"python3 << EOF
""""
"This is a shortcut for opening commonly used files

"Use <leader> -> t, v, i, or o -> your key to quickly open a file

"Previously called QUICKOPEN_leader_tvio


"Maps <leader>t<key> to tab open a filename
"Maps <leader>s<key> to vsplit open a filename
"Maps <leader>i<key> to split open a filename

"Suggested Bindings:
"    " Map leader key to comma (in all contexts)
"    let mapleader = ","
"    let maplocalleader = ","
"    noremap \ ,

"    call vimtk#quickopen(',', '~/.vimrc')
"    call vimtk#quickopen(',', '~/.vimrc')

""""
"EOF
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
    " TODO: i forgot what "the right thing is' and why this is important
    :exec 'noremap r'.a:lhs.' r'.a:rhs
    :exec 'noremap f'.a:lhs.' r'.a:rhs
endfu


func! vimtk#swap_keys(lhs, rhs)
    " Swaps the functionality of two keys
    :call vimtk#remap_all_modes(a:lhs, a:rhs)
    :call vimtk#remap_all_modes(a:rhs, a:lhs)
endfu


func! vimtk#py_format_doctest() range
python3 << EOF
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
python3 << EOF
"""
Removes docstring chevrons
"""
import vim
text = vimtk.TextSelector.selected_text()
text2 = vimtk.Python.unformat_text_as_docstr(text)
vimtk.TextInsertor.insert_over_selection(text2)
EOF
endfunc


func! vimtk#format_paragraph(...) 

python3 << EOF
import vim
import vimtk
from vimtk import util

nargs = int(vim.eval('a:0'))
# Simulate kwargs with cfgdict-like strings
default_config = {
    'max_width': 80,
    'myprefix': True,
    'sentence_break': True,
}
if nargs == 1:
    import ast
    cfgstr = vim.eval('a:1')
    kwargs = ast.literal_eval(cfgstr) if cfgstr else {}
    #cfgdict = ut.parse_cfgstr3(cfgstr)
    #kwargs = ut.update_existing(default_kwargs, cfgdict, assert_exists=True)
else:
    kwargs = {}

assert not util.dict_diff(kwargs, default_config), 'unknown args'
config = util.dict_union(default_config, kwargs)

# Remember curor location as best as possible
(row, col) = vim.current.window.cursor

row1, row2 = vimtk.TextSelector.paragraph_range_at_cursor()
text = vimtk.TextSelector.text_between_lines(row1, row2)
text = util.ensure_unicode(text)

from vimtk._dirty import format_multiple_paragraph_sentences
wrapped_text = format_multiple_paragraph_sentences(text, **kwargs)

vimtk.TextInsertor.insert_between_lines(wrapped_text, row1, row2)

# Reset cursor position as best as possible
vimtk.Cursor.move(row, col)
EOF

endfunc


""" For unit tests
func! vimtk#internal_test_reload_state()
    :echo "I am in the VIMTK_TEST_INITIAL_STATE"
endfunc
"""


" Source helpers relative to this file
"execute 'source ' . expand('<sfile>:p:h') . '/vimtk_snippets.vim'
" Secondary guard flags that we never unset
if exists("g:loaded_vimtk_autoload_final")
  finish
endif
let g:loaded_vimtk_autoload_final = 1


func! vimtk#reload()
let __doc__ =<< trim __DOC__

Reloads the functions in this file and your VIMRC.

The one exception is that this function is not reloaded, due to
the issue described in [ReloadIssue]_.

Refrences:

  .. [ReloadIssue] https://vi.stackexchange.com/questions/26479/refreshing-vim-file-from-within-a-function
__DOC__

" Unset the guard flags
let g:loaded_vimtk_autoload = 0
let g:loaded_vimtk = 0

python3 << EOF
import vimtk
vimtk.reload()
EOF

" NOTE: this does not work!
" Resource this file.
:source $MYVIMRC
:exec "source " . g:vimtk_autoload_core_fpath
":exec "source " . g:vimtk_autoload_snippet_fpath

endfunc
