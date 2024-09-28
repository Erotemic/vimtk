let g:vimtk_autoload_snippet_fpath=expand("<sfile>")


func! vimtk_snippets#insert_python_main() 
    " Imports a python __main__ block 
python3 << EOF
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
python3 << EOF
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
python3 << EOF
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
python3 << EOF
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
python3 << EOF
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
python3 << EOF
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
python3 << EOF
import vim
import vimtk
import ubelt as ub

if vimtk.Python.is_module_pythonfile():
    modinfo = vimtk.Python.current_module_info()
    funcinfo = vimtk.Python.find_func_above_row(row='current')
    callname = funcinfo['callname']
    modname = modinfo['modname']
    modpath = modinfo['modpath']
    if modinfo['importable']:
        modname_or_path = modinfo['modname']
    else:
        modname_or_path = modinfo['modpath']
    snippet = ub.codeblock(
        f'''
        CommandLine:
            xdoctest -m {modpath} {callname}
            xdoctest -m {modname} {callname}
        ''')
    indent = vimtk.TextSelector.current_indent()
    newtext = ub.indent(snippet, indent)
    vimtk.TextInsertor.insert_under_cursor(newtext)
else:
    print('current file is not a pythonfile')
EOF
endfu 


func! vimtk_snippets#insert_python_scriptconfig_template() 
    " Imports a python __main__ block 
python3 << EOF
import vim
import vimtk
import ubelt as ub

vimtk.ensure_normalmode()
if vimtk.Python.is_module_pythonfile():

    modinfo = vimtk.Python.current_module_info()
    modpath = modinfo['modpath']
    modname = ub.modpath_to_modname(modpath)
        
    cmdline_parts = ['CommandLine:']

    if ub.WIN32:
        modpath = ub.shrinkuser(modpath, home='%HOME%')
        cmdline1 = 'python -B ' + modpath.replace('\\', '/')
    else:
        modpath = ub.shrinkuser(modpath, home='~')
        cmdline1 = 'python ' + modpath

    cmdline_parts.append('    ' + cmdline1)

    rel_modname = modname.split('.')[-1]

    clsname = ''.join([p.capitalize() for p in rel_modname.split('_')]) + 'CLI'
    
    if modname:
        cmdline2 = 'python -m ' + modname
        cmdline_parts.append('    ' + cmdline2)

    cmdline_block = ub.indent('\n'.join(cmdline_parts))

    text = ub.codeblock(
        r'''
        #!/usr/bin/env python3
        import scriptconfig as scfg
        import ubelt as ub


        class {clsname}(scfg.DataConfig):
            # param1 = scfg.Value(None, help='param1')

            @classmethod
            def main(cls, cmdline=1, **kwargs):
                """
                Example:
                    >>> # xdoctest: +SKIP
                    >>> from {modname} import *  # NOQA
                    >>> cmdline = 0
                    >>> kwargs = dict()
                    >>> cls = {clsname}
                    >>> config = cls(**kwargs)
                    >>> cls.main(cmdline=cmdline, **config)
                """
                import rich
                from rich.markup import escape
                config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
                rich.print('config = ' + escape(ub.urepr(config, nl=1)))

        __cli__ = {clsname}

        if __name__ == '__main__':
            {rr}"""

        {cmdline_block}
            """
            __cli__.main()
        '''
    ).format(clsname=clsname, modname=modname, cmdline_block=cmdline_block, rr='{r}')
    text = text.format(r='r' if '\\' in text else '')

    vimtk.TextInsertor.insert_under_cursor(text)
else:
    print('current file is not a pythonfile')
#L______________
EOF
endfu 


""" TODO: requires pyvim_funcs ports


"func! vimtk#InsertDocstr() 
"python3 << EOF
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
"python3 << EOF
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
"python3 << EOF
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
