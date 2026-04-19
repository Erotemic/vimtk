#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="vimtk"
REPO_DPATH="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
BUNDLE_DPATH="${VIM_BUNDLE_DIR:-$HOME/.vim/bundle}"
LINK_DPATH="${BUNDLE_DPATH}/${PLUGIN_NAME}"
INSTALL_PYTHON_EDITABLE="${INSTALL_PYTHON_EDITABLE:-1}"

mkdir -p "$BUNDLE_DPATH"

if [[ -L "$LINK_DPATH" ]]; then
    CURRENT_TARGET="$(readlink "$LINK_DPATH" || true)"
    if [[ "$CURRENT_TARGET" == "$REPO_DPATH" ]]; then
        echo "Symlink already exists:"
        echo "  $LINK_DPATH -> $CURRENT_TARGET"
    else
        rm "$LINK_DPATH"
        ln -s "$REPO_DPATH" "$LINK_DPATH"
        echo "Updated symlink:"
        echo "  $LINK_DPATH -> $REPO_DPATH"
    fi
elif [[ -e "$LINK_DPATH" ]]; then
    echo "Refusing to overwrite existing non-symlink path:" >&2
    echo "  $LINK_DPATH" >&2
    echo "Move or remove it first, then rerun this script." >&2
    exit 1
else
    ln -s "$REPO_DPATH" "$LINK_DPATH"
    echo "Created symlink:"
    echo "  $LINK_DPATH -> $REPO_DPATH"
fi

if [[ "$INSTALL_PYTHON_EDITABLE" == "1" ]]; then
    if command -v python >/dev/null 2>&1; then
        echo "Installing python package in editable mode"
        python -m pip install -e .
    else
        echo "python not found; skipping editable install" >&2
    fi
fi

echo
echo "Done."
echo "If needed, make sure your vimrc sources:"
echo "  $LINK_DPATH/plugin/vimtk.vim"
