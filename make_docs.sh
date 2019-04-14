#!/bin/bash
__heredoc__="""
Requirements:
     pip install -r docs/requirements.txt
     sphinx

Notes:
    cd ~/code/vimtk/docs
    make html
    sphinx-apidoc -f -o ~/code/vimtk/docs/source ~/code/vimtk/vimtk --separate
    make html

    cd ~/code/sphinx
    github-add-fork source https://github.com/sphinx-doc/sphinx.git
"""

(cd ~/code/vimtk/docs && make html)
