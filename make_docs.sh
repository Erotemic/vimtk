#!/bin/bash
__heredoc__="""
Requirements:
     pip install -r docs/requirements.txt
     sphinx


Notes:
    mkdir -p ~/code/vimtk/docs
    cd ~/code/vimtk/docs
    touch ~/code/vimtk/docs/requirements.txt
    sphinx-quickstart

Notes:
    cd ~/code/vimtk/docs
    sphinx-apidoc -f -o ~/code/vimtk/docs/source ~/code/vimtk/vimtk --separate
    make html

    cd ~/code/sphinx
    github-add-fork source https://github.com/sphinx-doc/sphinx.git
"""

(cd ~/code/vimtk/docs && make html)
