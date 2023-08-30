__doc__="
Test that vimtk is functional inside of a fresh docker container
"

DOCKER_IMAGE=${DOCKER_IMAGE:="ubuntu:18.04"}
echo "DOCKER_IMAGE = $DOCKER_IMAGE"

if [ "$_INSIDE_DOCKER" != "YES" ]; then
    # If we aren't in docker start running in docker
    set -e
    docker run --rm \
        -v "$PWD":/io \
        -e _INSIDE_DOCKER="YES" \
        "$DOCKER_IMAGE" bash -c 'cd /io && ./test_in_docker.sh'

    __interactive__='''
    DOCKER_IMAGE=ubuntu:18.04
    docker run --rm \
        -v $HOME/code:/root/code \
        -v $PWD:/io \
        -e _INSIDE_DOCKER="YES" \
        -it $DOCKER_IMAGE bash
    '''
    exit 0;
fi


apt update -y
apt install vim git curl python3 python3-pip -y
ln -s /io/recommended_vimrc.vim "$HOME"/.vimrc

# Run vim once to install plugins
vim -en -c ":q"
vim -en -c ":PlugInstall | qa"

if [ -d "$HOME/code/vimtk" ]; then
    # Use the dev version of vimtk
    rm -rf "$HOME"/.vim/bundle/vimtk
    ln -s "$HOME"/code/vimtk "$HOME"/.vim/bundle/vimtk
fi

ls -al ~/.vim/bundle/


rm -rf "$HOME"/.vim
vim -c ':q'
vim -e -c ':q'
vim -c ':q'

vim -c ':call vimtk#helloworld()'


python3 -c "import sys;print(sys.exec_prefix)"

vim -e -c ':q' -V 2> _verbout
cat _verbout
grep "vimtk" _verbout

/io/test.py
