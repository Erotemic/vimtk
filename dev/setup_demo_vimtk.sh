
echo "
If you have something like this in your vimrc:

  noremap  <leader>a :call vimtk#execute_text_in_terminal(mode())<CR>
  vnoremap <leader>a :call vimtk#execute_text_in_terminal(visualmode())<CR>
  noremap  <leader>m :call vimtk#execute_text_in_terminal('word')<CR>

Then you can execute lines, visual selections, or just single words.

This works great with Bash and IPython shells.
" | PW=12345 openssl enc -pass env:PW -e -a 

echo "
With VimTK, you can execute blocks of code in a nearby terminal
" | PW=12345 openssl enc -pass env:PW -e -a 

echo "Its pretty cool" | PW=12345 openssl enc -pass env:PW -d -a 
