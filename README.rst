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

  " Doctest editing
  vnoremap gd :call vimtk#py_format_doctest()<CR>
  vnoremap gu :call vimtk#py_unformat_doctest()<CR>


Obviously you can modify the exact key bindings however you would like.


Here is what some of these functions do:

- ``vimtk#execute_text_in_terminal`` - copies the current word, line, or visual
  selection and executes it in your most recently used terminal (perhaps
  running IPython or bash) without needing to alt-tab or copy paste.
  Default binding is ``<leader>a`` for the current line or visual selection and
  ``<leader>m`` for a word.

- ``vimtk#ipython_import_all`` - if you are in a python module, this funciton
  creates a few lines of code that will import everything in this module into
  the current namespace. Note, it detects if you need to modify your pythonpath
  and does that.  It also completely disregards ``__all__``. These lines are
  then executed in your terminal (which should probably be an IPython session). 
  Default binding is ``<leader>M``.

- ``vimtk#copy_current_fpath`` - Copies the path to the current file into the
  clipboard. On non-windows the home drive is replaced with ``~``. Default
  binding is ``<leader>C``.

- ``vimtk#auto_import`` - Automatically inserts missing Python imports. 

- ``vimtk#insert_print_var_at_cursor`` - Insert a print statement around the
  current variable your cursor is on (supports python, bash, cmake, and C++)
  Default binding is ``<leader>pv`` for a repr representation and
  ``<leader>ps`` for a ubelt repr2 representation.

- ``vimtk#insert_timerit`` - Make a stub timerit and insert it at the current
  position

- ``vimtk#open_path_at_cursor`` - Open a file path or web url at your cursor. 

- ``vimtk#quickopen(char, fpath)`` - Use ``<leader>[tvio]``` to open predefined
  files / directories

- ``vimtk#py_format_doctest`` - Default binding to <visual-select> ``gd``.
  Inserts the doctest `` >>> `` prefix before the visually selected code.

- ``vimtk#vimtk#py_unformat_doctest`` - Default binding to <visual-select> ``gu``.
      Removes the doctest `` >>> `` prefix before the visually selected code.


Alternate VIMRC 
---------------

Note to get all the features, you need the following packages:

.. code:: bash

    # The <leader>a ability requires xdotool and wmctrl on linux systems
    sudo apt install xdotool wmctrl ctags

    # vimtk requires ubelt in whichever environment it is running
    pip install ubelt --user

.. code:: vim

    " VimTK Recommended VimRC: 
    " References: https://github.com/Erotemic/vimtk
    
    """""""""""""""
    " # Install vim-plug into your autoload directory
    " " See: https://github.com/junegunn/vim-plug
    " curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    """""""""""""""

    " Enable normal windows hotkeys like: ctrl+c, ctrl+v, ctrl+a, etc...
    source $VIMRUNTIME/mswin.vim
    behave mswin

    set nocompatible
    filetype off
    "source $VIMRUNTIME/mswin.vim
    "behave mswin
    set encoding=utf8
    
    call plug#begin('~/.vim/bundle')
    Plug 'sjl/badwolf'
    Plug 'scrooloose/nerdcommenter'
    Plug 'scrooloose/nerdtree'
    Plug 'vim-syntastic/syntastic'
    Plug 'majutsushi/tagbar'
    Plug 'ervandew/supertab'
    Plug 'Erotemic/vimtk'
    call plug#end()            " required

    filetype plugin indent on
    syntax on

    """" The above code should be among the first things in your vimrc

    scriptencoding utf-8
    set encoding=utf-8

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

    " Disable swap files, which prevents annoying messages when you open the
    " same file twice
    set noswapfile

    " Use a colorscheme (murphy is builtin, but I like badwolf)
    colorscheme badwolf
    "colorscheme murphy
    
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

    " Fast nerd tree access
    noremap <C-T> :NERDTree<CR>
    noremap <leader>. :NERDTree<CR>
    noremap <leader>h :NERDTreeToggle<CR>
    "noremap <leader>h :Tlist<CR>
    noremap <leader>j :Tagbar<CR>

    "set autochdir
    " better version of autochdir that changes cwd to be at the current file
    autocmd BufEnter * silent! lcd %:p:h
    
    " Note: to use vimtk I think we need to have ubelt installed
    " or get some sort of install-hook pip install command to happen
    " We can hack around this by explicitly sourcing the vimtk plugin
    source $HOME/.vim/bundle/vimtk/plugin/vimtk.vim
    
    " Make default vimtk remaps. 
    :call VimTK_default_remap()

    " Swap colon and semicolon
    :call vimtk#swap_keys(':', ';')

    " Register files you use all the time with quickopen
    " (use <leader>i<char> as a shortcut to specific files
    :call vimtk#quickopen(',', '~/.vimrc')
    :call vimtk#quickopen('5', '~/.bashrc')

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
