" VimTK Recommended VimRC: 
" References: https://github.com/Erotemic/vimtk

"""""""""""""""
" # Automatically install vim-plug into your autoload directory
" " See: https://github.com/junegunn/vim-plug
"""""""""""""""
if has("win32") || has("win16")
    let $HOME_DPATH = $USERPROFILE
    let $VIMFILES_DPATH = $HOME_DPATH . "/vimfiles"
else
    let $HOME_DPATH = $HOME
    let $VIMFILES_DPATH = $HOME_DPATH . "/.vim"
endif
if !filereadable($VIMFILES_DPATH . "/autoload/plug.vim")
  " Automatic installation if vim plug does not exist
  echo "Installing Vim Plug"
  execute 'silent !curl -fLo ' . $VIMFILES_DPATH . '/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif


" Enable normal windows hotkeys like: ctrl+c, ctrl+v, ctrl+a, etc...
source $VIMRUNTIME/mswin.vim
behave mswin

call plug#begin('~/.vim/bundle')
Plug 'sjl/badwolf'
Plug 'scrooloose/nerdcommenter'
Plug 'scrooloose/nerdtree'
Plug 'vim-syntastic/syntastic'
Plug 'majutsushi/tagbar'
Plug 'ervandew/supertab'
Plug 'Erotemic/vimtk'
call plug#end()            " required

"""" The above code should be among the first things in your vimrc


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
try 
  colorscheme badwolf
  catch
  try 
    echo "badwolf is not installed, fallback to murphy"
    colorscheme murphy
    catch
  endtry
endtry


" Map your leader key to comma (much easier to hit)
let mapleader = ","
let maplocalleader = ","
noremap \ ,

" Search and replace under cursor
noremap <leader>ss :%s/\<<C-r><C-w>\>/
"Surround word with quotes
noremap <leader>qw ciw'<C-r>"'<Esc>
noremap <leader>qc ciw`<C-r>"`<Esc>

" Reload your vimrc
noremap <leader>R :source ~/.vimrc<CR>

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


" HACKS!
" Note: to use vimtk I think we need to have ubelt installed
" or get some sort of install-hook pip install command to happen
" We can hack around this by explicitly sourcing the vimtk plugin
source $VIMFILES_DPATH/bundle/vimtk/plugin/vimtk.vim

" Make default vimtk remaps. 
:call VimTK_default_remap()

" Swap colon and semicolon
:call vimtk#swap_keys(':', ';')

" Register files you use all the time with quickopen
" (use <leader>i<char> as a shortcut to specific files
:call vimtk#quickopen(',', '~/.vimrc')
:call vimtk#quickopen('5', '~/.bashrc')
