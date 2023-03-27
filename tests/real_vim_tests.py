import ubelt as ub


vim_sleep_seq = '''
    " https://vi.stackexchange.com/questions/3480/viml-sleep-within-a-function
    set cursorline cursorcolumn
    redraw
    sleep 1000m
    set nocursorline nocursorcolumn
'''
vim_sleep_seq


def demo_fpath(text=None, fname=None):
    import ubelt as ub
    dpath = ub.Path.appdir('vimtk/tests/').ensuredir()
    if text is None:
        text = ub.codeblock(
            '''
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
            minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
            ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
            voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
            sint occaecat cupidatat non proident, sunt in culpa qui officia
            deserunt mollit anim id est laborum.

            Sed ut perspiciatis unde omnis iste natus error sit voluptatem
            accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae
            ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt
            explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut
            odit aut fugit, sed quia consequuntur magni dolores eos qui ratione
            voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum
            quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam
            eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat
            voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam
            corporis suscipit laboriosam, nisi ut aliquid ex ea commodi
            consequatur?

            Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse
            quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo
            voluptas nulla pariatur?"
            ''')
        if fname is None:
            fname = 'lorium.txt'
    else:
        if fname is None:
            fname = ub.hash_data(text)[0:8] + '.txt'
    fpath = dpath / fname
    fpath.write_text(text)
    return fpath


def is_interactive():
    import os
    return bool(os.environ.get('VIMTK_TEST_INTERACTIVE', ''))


def execute_vim_script(fpath, commands=None, interactive=False):
    """
    Notes:
        how to write logs to a file [SU_201090]_.

    References:
        [SU_201090] https://superuser.com/questions/201090/write-vim-log-to-a-file
    """
    vim_exe = ub.find_exe('vim')
    args = [vim_exe]
    script_fpath = None
    args.append(str(fpath))
    if commands is not None:
        """
        -c {command}
            {command}  will be executed after the first file has been read.
            {command} is interpreted as an Ex command.  If the {command}
            contains spaces it must be enclosed in double quotes (this
            depends on the shell that is used).  Example: vim "+set si" main.c
            Note: You can use up to 10 "+" or "-c" commands.

        -S {file}
            {file} will be sourced after the first file has been read.  This is
            equivalent to -c "source {file}".  {file} cannot start with '-'.
            If {file}  is  omitted "Session.vim" is used (only works when -S is
            the last argument).
        """
        # Must be the last command
        # import tempfile
        script_fpath = ub.Path.appdir('vimtk/tests/').ensuredir() / 'test_script.vim'
        # script_fpath = ub.Path(tempfile.mktemp(suffix='.vim',
        #                                        prefix='commands'))
        script_fpath.write_text(commands)
        args += ['-c', 'source {}'.format(script_fpath)]

    # Write logs to a file
    import tempfile
    temp_fpath = ub.Path(tempfile.mktemp())
    args += [f'-V0{temp_fpath}']

    if not interactive:
        args += ['-c', 'wqa!']
    # command = ' '.join(args)
    print(commands)
    ub.cmd(args, verbose=3, system=True)

    logs = temp_fpath.read_text()

    print('------')
    print('Result')
    print('------')
    _print_file_state(fpath)
    # print(fpath.read_text())
    print('------')
    print('======')
    print('----')
    print('Logs')
    print('----')
    _print_file_state(temp_fpath)
    # print(logs)
    print('----')
    print('======')
    print('Finished vim execution. If there is an error, try running in '
          'interactive mode via setting the environ VIMTK_TEST_INTERACTIVE=1 '
          'to see what it is.')
    return logs


def test_vim_config():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vim_config
    """
    fpath = demo_fpath()
    commands = ub.codeblock(
        '''
        python3 << EOF
        import vimtk
        import ubelt as ub
        print('<START_CONFIG>')
        print(ub.repr2(vimtk.CONFIG.state, nl=2))
        print('<END_CONFIG>')
        EOF
        ''')
    interactive = is_interactive()
    logs = execute_vim_script(fpath, commands=commands, interactive=interactive)

    startx = logs.find('<START_CONFIG>') + len('<START_CONFIG>')
    stopx = logs.find('<STOP_CONFIG>')
    relevant = logs[startx:stopx]
    print(f'relevant={relevant}')
    # TODO: assert something


def test_auto_import():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_auto_import
    """
    fpath = demo_fpath(fname='foo.py', text=ub.codeblock(
        '''
        blarblar
        spam
        print(math.floor(3.2))
        '''))
    commands = ub.codeblock(
        '''
        python3 << EOF
        import vimtk
        vimtk.CONFIG['vimtk_auto_importable_modules'].update({
            'blarblar': 'import blarblar',
        })
        EOF
        let g:vimtk_auto_importable_modules = {'spam': 'import spam'}
        :call vimtk#insert_auto_import()
        ''')
    interactive = is_interactive()
    execute_vim_script(fpath, commands=commands, interactive=interactive)
    assert 'import math' in fpath.read_text()


def test_format_paragraph():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_format_paragraph
    """
    fpath = demo_fpath()
    commands = ub.codeblock(
        '''
        :1
        :call vimtk#format_paragraph()
        ''')
    interactive = is_interactive()
    execute_vim_script(fpath, commands=commands, interactive=interactive)

    commands = ub.codeblock(
        '''
        :12
        :call vimtk#format_paragraph()
        ''')
    interactive = is_interactive()
    execute_vim_script(fpath, commands=commands, interactive=interactive)

    assert ('  fugit') in fpath.read_text()


def test_vim_buffer_indexing():
    """
    Demonstrates that buffer is zero indexed.
    (It is the cursor that is 1 indexed)

    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vim_buffer_indexing
    """
    commands = ub.codeblock(
        r'''
        if has('python3')
            command! -nargs=1 python3 python3 <args>
        elseif has('python')
            command! -nargs=1 python3 python <args>
        else
            echo "Error: Requires Vim compiled with +python or +python3"
            finish
        endif

        python3 << EOF
        import ubelt as ub
        import vim
        dpath = ub.Path.appdir('vimtk/test').ensuredir()
        debug_fpath = dpath / 'buffer_index_result.txt'
        print('This is a print message')
        import vim
        buf = vim.current.buffer
        line_0 = buf[0]
        line_1 = buf[1]
        line_neg1 = buf[-1]
        line_len_m_1 = buf[len(buf) - 1]
        debug_lines = []
        debug_write = debug_lines.append
        debug_write(f'{buf=}')
        debug_write(f'{len(buf)=}')
        debug_write(f'{line_0      =}')
        debug_write(f'{line_1      =}')
        debug_write(f'{line_neg1   =}')
        debug_write(f'{line_len_m_1=}')
        debug_text = '\n'.join(debug_lines)
        debug_fpath.write_text(debug_text)
        EOF
        ''')
    interactive = is_interactive()
    fpath = demo_fpath()
    dpath = ub.Path.appdir('vimtk/test').ensuredir()
    debug_fpath = dpath / 'buffer_index_result.txt'
    debug_fpath.delete()
    execute_vim_script(fpath, commands=commands, interactive=interactive)

    if debug_fpath.exists():
        print(f'debug_fpath={debug_fpath}')
        print(debug_fpath.read_text())
    else:
        print('debug_fpath not written')


def test_vimtk_reload():
    """
    VIMTK_TEST_INTERACTIVE=1 xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vimtk_reload
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vimtk_reload
    """
    # fpath = demo_fpath()

    # TODO: robust pathing
    fpath = ub.Path('~/code/vimtk/autoload/vimtk.vim').expand()

    # Call the internal_test_reload_state function, note the output
    # modify the function itself, the output should be unchanged
    # call the reload function, now the output should change
    # revert the change
    commands = ub.codeblock(
        '''
        :1
        :call vimtk#internal_test_reload_state()
        :%s/VIMTK_TEST_INITIAL_STATE/VIMTK_TEST_MODIFIED_STATE
        :w
        :call vimtk#internal_test_reload_state()
        :call vimtk#reload()
        :call vimtk#internal_test_reload_state()
        :%s/VIMTK_TEST_MODIFIED_STATE/VIMTK_TEST_INITIAL_STATE
        :w
        :call vimtk#internal_test_reload_state()
        :call vimtk#reload()
        :call vimtk#internal_test_reload_state()
        ''')
    interactive = is_interactive()
    logs = execute_vim_script(fpath, commands=commands, interactive=interactive)
    assert logs.count('VIMTK_TEST_INITIAL_STATE') == 3
    assert logs.count('VIMTK_TEST_MODIFIED_STATE') == 2


def test_open_path_at_cursor_normal():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_open_path_at_cursor
    """
    dpath = ub.Path.appdir('vimtk/tests/open_path').ensuredir()
    fpath1 = dpath / 'path1.rst'
    fpath2 = dpath / 'path2.rst'

    fpath1.write_text('welcome to fpath1')
    fpath2.write_text('welcome to fpath2')

    orig_text = ub.codeblock(
        f'''
        See:

            * {fpath1}

            * {fpath2}
        ''')
    fpath = demo_fpath(fname='foo.rst', text=orig_text)
    commands = ub.codeblock(
        '''
        python3 << END_PYTHON3
        import vimtk
        vimtk.Cursor.move(3, 10)
        END_PYTHON3

        :call vimtk#open_path_at_cursor('e')

        python3 << END_PYTHON3
        import vimtk
        vimtk.TextInsertor.insert_above_cursor('we modified this path')
        END_PYTHON3

        :w
        ''')
    interactive = is_interactive()
    execute_vim_script(fpath, commands=commands, interactive=interactive)

    print('FINAL')
    print('\n\n')
    # _print_file_state(fpath)
    _print_file_state(fpath1)
    _print_file_state(fpath2)

    assert fpath.read_text() == orig_text
    assert 'modified' in fpath1.read_text()


def test_open_path_at_cursor_with_special():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_open_path_at_cursor_with_special
    """
    dpath = ub.Path.appdir('vimtk/tests/open_path').ensuredir()
    fpath1 = dpath / 'path1.rst'
    fpath1.write_text('welcome to fpath1')

    orig_text = ub.codeblock(
        f'''
        * `{fpath1}>`
        ''')
    fpath = demo_fpath(fname='foo.rst', text=orig_text)
    commands = ub.codeblock(
        '''
        python3 << END_PYTHON3
        import vimtk
        vimtk.Cursor.move(3, 10)
        END_PYTHON3

        :call vimtk#open_path_at_cursor('e')

        python3 << END_PYTHON3
        import vimtk
        vimtk.TextInsertor.insert_above_cursor('we modified this path')
        END_PYTHON3

        :w
        ''')
    interactive = is_interactive()
    execute_vim_script(fpath, commands=commands, interactive=interactive)
    print('FINAL')
    print('\n\n')
    # _print_file_state(fpath)
    _print_file_state(fpath1)
    assert fpath.read_text() == orig_text
    assert 'modified' in fpath1.read_text()


def _detect_lang(fpath):
    lang = None
    if fpath.suffix == '.sh':
        lang = 'bash'
    elif fpath.suffix == '.py':
        lang = 'python'
    elif fpath.suffix == '.rst':
        lang = 'rst'
    return lang


def _print_file_state(fpath):
    USE_RICH = 1
    lang = _detect_lang(fpath)
    text = fpath.read_text()
    if USE_RICH:
        from rich.panel import Panel
        from rich.syntax import Syntax
        from rich.console import Console
        console = Console(width=80)
        if lang is not None:
            text = Syntax(text, lang)
        console.print(Panel(text, title=str(fpath)))
    else:
        print(ub.highlight_code('# --- ' + str(fpath), 'bash'))
        print(ub.highlight_code(text, lang or 'python'))
