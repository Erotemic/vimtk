VimTk - The (mostly) Python (g)Vim toolkit 
==========================================

|CircleCI| |Codecov| |Pypi| |Downloads| |ReadTheDocs|


Description 
-----------

The tools in this package focus on, but are not exclusive to Python development
with gVim.  This is both a Vim plugin and a pip installable Python module.


Usage 
-----

We suggest using vim-plug to manage plugins. Install vim plug like this:

.. code:: bash

    # Install vim-plug into your autoload directory
    " See: https://github.com/junegunn/vim-plug
    curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim


We suggest the following vimrc as a template:

.. code:: vim

    " DEMO_VIMRC: 

    call plug#begin('~/.vim/bundle')

    Plug 'sjl/badwolf'
    Plug 'Erotemic/vimtk'

    call plug#end()            " required

    filetype plugin indent on
    syntax on

    """" The above code should be among the first things in your vimrc


    " Map your leader key to comma (much easier to hit)
    let mapleader = ","
    let maplocalleader = ","
    noremap \ ,

    " Make default vimtk remaps
    :call VimTK_default_remap()

    " Register files you use all the time with quickopen
    " (use <leader>i<char> as a shortcut to specific files
    call vimtk#quickopen(',', '~/.vimrc')
    call vimtk#quickopen('5', '~/.bashrc')


This module defines many helper functions, but does not bind them to keys by
default unless ``VimTK_default_remap`` is called. The default bindings are as
follows:

.. code:: vim

  noremap <leader>H :call vimtk#helloworld()<Esc>

  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

  noremap <leader>C :call vimtk#copy_current_fpath()<Esc>
  noremap <leader>M :call vimtk#ipython_import_all()<CR>

  command! AutoImport call vimtk#insert_auto_import()
  noremap <leader>pv :call vimtk#insert_print_var_at_cursor()<CR>
  noremap  <c-M-B> :call vimtk#insert_timerit(mode())<CR><Esc>
  vnoremap <c-M-B> :call vimtk#insert_timerit(visualmode())<CR><Esc>

  noremap <leader>es :call vimtk#smart_search_word_at_cursor()<CR>
  noremap <leader>go :call vimtk#open_path_at_cursor("e")<CR>
  noremap <leader>gf :call vimtk#open_path_at_cursor("e")<CR>
  noremap <leader>gi :call vimtk#open_path_at_cursor("split")<CR>
  noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
  noremap <leader>gv :call vimtk#open_path_at_cursor("vsplit")<CR>
  noremap <leader>gt :call vimtk#open_path_at_cursor("tabe")<CR>
  noremap gi :call vimtk#open_path_at_cursor("split")<CR>


Obviously you can modify the exact key bindings however you would like.


Here is what some of these functions do:

- ``vimtk#execute_text_in_terminal`` - copies the current word, line, or visual
  selection and executes it in your most recently used terminal (perhaps
  running IPython or bash) without needing to alt-tab or copy paste.

- ``vimtk#ipython_import_all`` - if you are in a python module, this funciton
  creates a few lines of code that will import everything in this module into
  the current namespace. Note, it detects if you need to modify your pythonpath
  and does that.  It also completely disregards ``__all__``. These lines are
  then executed in your terminal (which should probably be an IPython session)

- ``vimtk#copy_current_fpath`` - Copies the path to the current file into the
  clipboard. On non-windows the home drive is replaced with ``~``.

- ``vimtk#auto_import`` - Automatically inserts missing Python imports

- ``vimtk#insert_print_var_at_cursor`` - Insert a print statement around the
  current variable your cursor is on (supports python, bash, cmake, and C++)

- ``vimtk#insert_timerit`` - Make a stub timerit and insert it at the current
  position

- ``vimtk#open_path_at_cursor`` - Open a file path or web url at your cursor

- ``vimtk#quickopen(char, fpath)`` - Use <leader>[tvio] to open predefined files / directories


Alternate VIMRC 
---------------

.. code:: vim

    " VimTK Recommended VimRC: 
    " References: https://github.com/Erotemic/vimtk
    
    """""""""""""""
    " # Install vim-plug into your autoload directory
    " " See: https://github.com/junegunn/vim-plug
    " curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    """""""""""""""

    call plug#begin('~/.vim/bundle')

    Plug 'sjl/badwolf'
    Plug 'Erotemic/vimtk'
    Plug 'scrooloose/nerdcommenter'
    Plug 'scrooloose/nerdtree'
    Plug 'vim-syntastic/syntastic'

    call plug#end()            " required

    filetype plugin indent on
    syntax on

    """" The above code should be among the first things in your vimrc

    scriptencoding utf-8
    set encoding=utf-8

    " allow backspacing over everything in insert mode
    set backspace=indent,eol,start

    " In many terminal emulators the mouse works just fine, thus enable it.
    if has('mouse')
      set mouse=a
    endif

    set fileformat=unix
    set fileformats=unix,dos

    colorscheme badwolf

    set nomousehide

    set shellslash
    set grepprg=grep\ -nH\ $*

    set autoread
    set ruler

    " References: https://vi.stackexchange.com/questions/13034/automatic-whitespace-in-python
    " ---- Minimal configuration:
    set smartindent   " Do smart autoindenting when starting a new line
    set shiftwidth=4  " Set number of spaces per auto indentation
    set expandtab     " When using <Tab>, put spaces instead of a <tab> character

    " ---- Good to have for consistency
    set tabstop=4   " Number of spaces that a <Tab> in the file counts for
    set smarttab    " At <Tab> at beginning line inserts spaces set in shiftwidth

    " Highlight search regexes
    set incsearch
    set hlsearch
    

    " https://unix.stackexchange.com/questions/196098/copy-paste-in-xfce4-terminal-adds-0-and-1
    " fix terminal spacing issue
    set t_BE=

    "set cino='{1s'

    " Map your leader key to comma (much easier to hit)
    let mapleader = ","
    let maplocalleader = ","
    noremap \ ,

    " Search and replace under cursor
    noremap <leader>ss :%s/\<<C-r><C-w>\>/
    "Surround word with quotes
    noremap <leader>qw ciw'<C-r>"'<Esc>
    noremap <leader>qc ciw`<C-r>"`<Esc>

    " Window navication
    " Alt + jklh
    map <silent><A-j> <c-w>j
    map <silent><A-k> <c-w>k
    map <silent><A-l> <c-w>l
    map <silent><A-h> <c-w>h
    " Control + jklh
    map <c-j> <c-w>j
    map <c-k> <c-w>k
    map <c-l> <c-w>l
    " Move in split windows
    " Press leader twice to move between windows
    noremap <leader>, <C-w>w
    map <c-h> <c-w>h


    " Make default vimtk remaps
    :call VimTK_default_remap()

    " Swap colon and semicolon
    :call vimtk#swap_keys(':', ';')

    " Register files you use all the time with quickopen
    " (use <leader>i<char> as a shortcut to specific files
    call vimtk#quickopen(',', '~/.vimrc')
    call vimtk#quickopen('5', '~/.bashrc')

.. |CircleCI| image:: https://circleci.com/gh/Erotemic/vimtk.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/vimtk
.. |Travis| image:: https://img.shields.io/travis/Erotemic/vimtk/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/vimtk?branch=master
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Erotemic/vimtk?branch=master&svg=True
   :target: https://ci.appveyor.com/project/Erotemic/vimtk/branch/master
.. |Codecov| image:: https://codecov.io/github/Erotemic/vimtk/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/vimtk?branch=master
.. |Pypi| image:: https://img.shields.io/pypi/v/vimtk.svg
   :target: https://pypi.python.org/pypi/vimtk
.. |Downloads| image:: https://img.shields.io/pypi/dm/vimtk.svg
   :target: https://pypistats.org/packages/vimtk
.. |ReadTheDocs| image:: https://readthedocs.org/projects/vimtk/badge/?version=latest
    :target: http://vimtk.readthedocs.io/en/latest/
