

func! vimtk_snippets#insert_python_main() 
    " Imports a python __main__ block 
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub

vimtk.ensure_normalmode()
if vimtk.Python.is_module_pythonfile():

    modinfo = vimtk.Python.current_module_info()
    modpath = modinfo['modpath']

    if ub.WIN32:
        modpath = ub.shrinkuser(modpath, home='%HOME%')
        cmdline_ = 'python -B ' + modpath.replace('\\', '/')
    else:
        modpath = ub.shrinkuser(modpath, home='~')
        cmdline_ = 'python ' + modpath

    test_code = ub.codeblock(
        r'''
        import xdoctest
        xdoctest.doctest_module(__file__)
        ''')
    test_code = ub.indent(test_code) 

    text = ub.codeblock(
        r'''
        if __name__ == '__main__':
            {rr}"""
            CommandLine:
                {cmdline_}
            """
        {test_code}
        '''
    ).format(cmdline_=cmdline_, test_code=test_code, rr='{r}')
    text = text.format(r='r' if '\\' in text else '')

    vimtk.TextInsertor.insert_under_cursor(text)
else:
    print('current file is not a pythonfile')
#L______________
EOF
endfu 

func! vimtk_snippets#insert_python_header(...) 
    " Imports a standard python header
Python2or3 << EOF
mode = vim.eval('(a:0 >= 1) ? a:1 : 0')
import ubelt as ub
import vim
import vimtk
vimtk.ensure_normalmode()
if vimtk.Python.is_module_pythonfile():
    modpath = vim.current.buffer.name
    modname = ub.modpath_to_modname(modpath)
    lines = []
    if mode == 'script':
        lines += ['#!/usr/bin/env python']
    #lines += [
    #    '# -*- coding: utf-8 -*-',
    #    'from __future__ import print_function, division, absolute_import, unicode_literals',
    #]
    text = '\n'.join(lines)
    vimtk.TextInsertor.insert_above_cursor(text)
else:
    print('current file is not a pythonfile')
#L______________
EOF
endfu 



func! vimtk_snippets#insert_timerit(...) range
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub
mode = vim.eval('a:1')
snippet = ub.codeblock(
    '''
    import ubelt as ub
    ti = ub.Timerit(100, bestof=10, verbose=2)
    for timer in ti.reset('time'):
        with timer:
    '''
)
indent = vimtk.TextSelector.current_indent()
newtext = ub.indent(snippet, indent)
if 'v' in mode.lower():
    newtext += '\n' + ub.indent(vimtk.TextSelector.selected_text(), ' ' * 8)
    vimtk.TextInsertor.insert_over_selection(newtext)
else:
    vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc


func! vimtk_snippets#insert_xdev_embed() 
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub

indent = vimtk.TextSelector.current_indent()
snippet = ub.codeblock(
    '''
    import xdev
    xdev.embed()
    ''')
newtext = ub.indent(snippet, indent)
vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc


func! vimtk_snippets#insert_xdev_embed_on_exception_context(...) range
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub

mode = vim.eval('a:1')

indent = vimtk.TextSelector.current_indent()
# import ipdb
# with ipdb.launch_ipdb_on_exception()
snippet = ub.codeblock(
    '''
    import xdev
    with xdev.embed_on_exception_context:
    '''
)
newtext = ub.indent(snippet, indent)
if 'v' in mode.lower():
    newtext += '\n' + ub.indent(vimtk.TextSelector.selected_text())
    vimtk.TextInsertor.insert_over_selection(newtext)
else:
    vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc



func! vimtk_snippets#insert_xdev_global_kwargs() 
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub
funcinfo = vimtk.Python.find_func_above_row(row='current')
callname = funcinfo['callname']
snippet = ub.codeblock(
    '''
    import xdev
    globals().update(xdev.get_func_kwargs({}))
    '''.format(callname)
)
newtext = ub.indent(snippet, indent)
vimtk.TextInsertor.insert_under_cursor(newtext)
EOF
endfunc


func! vimtk_snippets#insert_docstr_commandline() 
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub

if vimtk.Python.is_module_pythonfile():
    modinfo = vimtk.Python.current_module_info()
    funcinfo = vimtk.Python.find_func_above_row(row='current')
    callname = funcinfo['callname']
    if modinfo['importable']:
        modname_or_path = modinfo['modname']
    else:
        modname_or_path = modinfo['modpath']
    snippet = ub.codeblock(
        '''
        CommandLine:
            xdoctest -m {modname_or_path} {callname}
        ''').format(callname=callname, modname_or_path=modname_or_path)
    indent = vimtk.TextSelector.current_indent()
    newtext = ub.indent(snippet, indent)
    vimtk.TextInsertor.insert_under_cursor(newtext)
else:
    print('current file is not a pythonfile')
EOF
endfu 


func! vimtk_snippets#insert_python_scriptconfig_template() 
    " Imports a python __main__ block 
Python2or3 << EOF
import vim
import vimtk
import ubelt as ub

vimtk.ensure_normalmode()
if vimtk.Python.is_module_pythonfile():

    modinfo = vimtk.Python.current_module_info()
    modpath = modinfo['modpath']
    modname = ub.modpath_to_modname(modpath)

    if ub.WIN32:
        modpath = ub.shrinkuser(modpath, home='%HOME%')
        cmdline1 = 'python -B ' + modpath.replace('\\', '/')
    else:
        modpath = ub.shrinkuser(modpath, home='~')
        cmdline1 = 'python ' + modpath
    
    if modname:
        cmdline2 = 'python -m ' + modname

    text = ub.codeblock(
        r'''
        import scriptconfig as scfg
        import ubelt as ub

        class MyNewConfig(scfg.DataConfig):
            ...

        def main(cmdline=1, **kwargs):
            """
            Example:
                >>> # xdoctest: +SKIP
                >>> cmdline = 0
                >>> kwargs = {
                >>> }
                >>> main(cmdline=cmdline, **kwargs)
            """
            config = MyNewConfig.legacy(cmdline=cmdline, data=kwargs)
            print('config = {}'.format(ub.urepr(dict(config), nl=1)))

        if __name__ == '__main__':
            {rr}"""
            CommandLine:
                {cmdline1}
                {cmdline2}
            """
            main()
        '''
    ).format(cmdline_=cmdline_, rr='{r}')
    text = text.format(r='r' if '\\' in text else '')

    vimtk.TextInsertor.insert_under_cursor(text)
else:
    print('current file is not a pythonfile')
#L______________
EOF
endfu 


""" TODO: requires pyvim_funcs ports


"func! vimtk#InsertDocstr() 
"Python2or3 << EOF
"import vim
"import vimtk

"if vimtk.Python.is_module_pythonfile():
"    print('building docstr')
"    text = pyvim_funcs.auto_docstr()
"    vimtk.TextInsertor.insert_under_cursor(text)
"else:
"    print('current file is not a pythonfile')
"#L______________
"EOF
"endfu 


"func! vimtk#InsertKWargsDoc() 
"Python2or3 << EOF
"import vim
"import vimtk
"#vim.command(':echom %r' % ('dbmsg: ' + dbgmsg,))
"if vimtk.Python.is_module_pythonfile():
"    print('building docstr')
"    text = pyvim_funcs.auto_docstr()
"    vimtk.TextInsertor.insert_under_cursor(text)
"else:
"    print('current file is not a pythonfile')
"#L______________
"EOF
"endfu 


"func! vimtk#InsertDocstrOnlyArgs() 
"Python2or3 << EOF
"import vim
"import vimtk

"if vimtk.is_module_pythonfile():
"    print('building docstr')
"    text = pyvim_funcs.auto_docstr( 
"        with_args=True,
"        with_ret=False,
"        with_commandline=False,
"        with_example=False,
"        with_header=False)
"    vimtk.TextInsertor.insert_under_cursor(text)
"else:
"    print('current file is not a pythonfile')
"#L______________
"EOF
"endfu 
