To get a list of all scripts sourced by vim (in order)

```vim
:scriptnames
```


vim -V 2> _verbout | grep "vimtk" _verbout


# NOTE:
# https://stackoverflow.com/questions/21322520/why-wont-vim-recognise-a-plugin-command-in-the-vimrc-but-it-will-recognise-it
It seems the vimrc is ALWAYS loaded before the plugins

```bash
vim -e -c ':q' -V 2> _verbout 
cat _verbout | grep vimtk
cat _verbout | grep -i "finished sourcing "
cat _verbout | grep -i "sourcing " | grep "vimtk\|vimrc\|nerdtree" | grep vimrc -C 1000
grep "vimtk" _verbout
grep "vimtk" _verbout
cat _verbout | grep -i "sourcing " | grep "vimtk\|vimrc\|nerdtree" | grep vimrc -C 1000
```



Can you use plugins inside of your vimrc?


I recently learned the very hard way that vim-plug will only load plugins AFTER the vimrc is completely sourced: https://stackoverflow.com/questions/21322520/why-wont-vim-recognise-a-plugin-command-in-the-vimrc-but-it-will-recognise-it

The issue is that I have a plugin where I define functions that I would like to use inside my vimrc. Specifically my plugin is here: https://github.com/Erotemic/vimtk

and I would like to call the lines:

```vim
" Make default vimtk remaps.
:call VimTK_default_remap()

" Swap colon and semicolon
:call vimtk#swap_keys(':', ';')

" Register files you use all the time with quickopen
" (use <leader>i<char> as a shortcut to specific files
:call vimtk#quickopen(',', '~/.vimrc')
:call vimtk#quickopen('5', '~/.bashrc')
```

in my vimrc. These lines define special remappings, so I think it makes sense that they are called on startup time and not via an autocmd. My current workaround is just to explicitly source the plugin file: `source $HOME/.vim/bundle/vimtk/plugin/vimtk.vim` before calling these commands, but that's not very satisfying. 

Is there a way to force plugins to load such that you can call their functions inside your vimrc?

