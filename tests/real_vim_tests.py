import ubelt as ub


vim_sleep_seq = '''
    " https://vi.stackexchange.com/questions/3480/viml-sleep-within-a-function
    set cursorline cursorcolumn
    redraw
    sleep 1000m
    set nocursorline nocursorcolumn
'''
vim_sleep_seq


def execute_vim_script(fpath, commands=None, interactive=False):
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

    if not interactive:
        args += ['-c', 'wqa!']
    # command = ' '.join(args)
    print(commands)
    ub.cmd(args, verbose=3, system=True)
    print('Result')
    print('------')
    print(fpath.read_text())
    print('------')
    print('Finished vim execution. If there is an error, try running in '
          'interactive mode to see what it is.')


def test_vim_config():
    """
    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vim_config
    """
    fpath = demo_fpath()
    commands = ub.codeblock(
        '''
        Python2or3 << EOF
        import vimtk
        print(vimtk.CONFIG.state)
        EOF
        ''')
    interactive = 0
    execute_vim_script(fpath, commands=commands, interactive=interactive)


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
        Python2or3 << EOF
        import vimtk
        vimtk.CONFIG['vimtk_auto_importable_modules'].update({
            'blarblar': 'import blarblar',
        })
        EOF
        let g:vimtk_auto_importable_modules = {'spam': 'import spam'}
        :call vimtk#insert_auto_import()
        ''')
    interactive = 0
    execute_vim_script(fpath, commands=commands, interactive=interactive)


def test_format_paragraph():
    fpath = demo_fpath()
    commands = ub.codeblock(
        '''
        :1
        :call vimtk#format_paragraph()
        ''')
    interactive = 0
    execute_vim_script(fpath, commands=commands, interactive=interactive)

    commands = ub.codeblock(
        '''
        :12
        :call vimtk#format_paragraph()
        ''')
    interactive = 0
    execute_vim_script(fpath, commands=commands, interactive=interactive)


def test_vim_buffer_indexing():
    """
    Demonstrates that buffer is zero indexed.
    (It is the cursor that is 1 indexed)

    xdoctest ~/code/vimtk/tests/real_vim_tests.py test_vim_buffer_indexing
    """
    commands = ub.codeblock(
        r'''
        if has('python3')
            command! -nargs=1 Python2or3 python3 <args>
        elseif has('python')
            command! -nargs=1 Python2or3 python <args>
        else
            echo "Error: Requires Vim compiled with +python or +python3"
            finish
        endif

        Python2or3 << EOF
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
    interactive = 0
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
