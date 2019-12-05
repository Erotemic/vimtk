#!/bin/bash
__heredoc__='''
Script to publish a new version of this library on PyPI

Args:
    # These environment variables must / should be set
    TWINE_USERNAME : username for pypi
    TWINE_PASSWORD : password for pypi
    USE_GPG : defaults to True
    GPG_IDENTIFIER

Requirements:
     twine

Notes:
    # NEW API TO UPLOAD TO PYPI
    # https://packaging.python.org/tutorials/distributing-packages/

Usage:
    cd <YOUR REPO>

    # Set your variables or load your secrets
    export TWINE_USERNAME=<pypi-username>
    export TWINE_PASSWORD=<pypi-password>

    # Interactive/Dry run
    ./publish.sh 

    # Non-Interactive run
    #./publish.sh yes
    source $(secret_loader.sh)
    DEPLOY_BRANCH=master ./publish.sh yes
'''

# Options
TWINE_USERNAME=${TWINE_USERNAME:="<unknown>"}
TWINE_PASSWORD=${TWINE_PASSWORD:="<unknown>"}
TAG_AND_UPLOAD=${TAG_AND_UPLOAD:=$1}
USE_GPG=${USE_GPG:="True"}

# First tag the source-code
TRAVIS_BRANCH=${TRAVIS_BRANCH:=$(git branch | grep \* | cut -d ' ' -f2)}
DEPLOY_BRANCH=${DEPLOY_BRANCH:=release}
VERSION=$(python -c "import setup; print(setup.version)")
GPG_EXECUTABLE=${GPG_EXECUTABLE:=gpg}
GPG_KEYID=${GPG_KEYID:=D297D757}


echo "
=== PYPI BUILDING SCRIPT ==
TRAVIS_BRANCH='$TRAVIS_BRANCH'
DEPLOY_BRANCH='$DEPLOY_BRANCH'
VERSION='$VERSION'
TWINE_USERNAME='$TWINE_USERNAME'
"


echo "
=== <BUILD WHEEL> ===
"
echo "LIVE BUILDING"
# Build wheel and source distribution
python setup.py bdist_wheel --universal
python setup.py sdist 

BDIST_WHEEL_PATH=$(ls dist/*-$VERSION-*.whl)
SDIST_PATH=$(dir dist/*-$VERSION*.tar.gz)
echo "
echo "VERSION='$VERSION'"
BDIST_WHEEL_PATH='$BDIST_WHEEL_PATH'
SDIST_PATH='$SDIST_PATH'
"
echo "
=== <END BUILD WHEEL> ===
"

echo "
=== <GPG SIGN> ===
"
if [ "$USE_GPG" == "True" ]; then
    # https://stackoverflow.com/questions/45188811/how-to-gpg-sign-a-file-that-is-built-by-travis-ci
    # secure gpg --export-secret-keys > all.gpg

    # REQUIRES GPG >= 2.2
    echo "GPG_KEYID=$GPG_KEYID"

    echo "Removing old signatures"
    rm dist/*.asc

    echo "Signing wheels"
    GPG_SIGN_CMD="$GPG_EXECUTABLE --batch --yes --detach-sign --armor --local-user $GPG_KEYID"
    $GPG_SIGN_CMD --output $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
    $GPG_SIGN_CMD --output $SDIST_PATH.asc $SDIST_PATH

    echo "Checking wheels"
    twine check $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
    twine check $SDIST_PATH.asc $SDIST_PATH

    echo "Verifying wheels"
    gpg --verify $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH 
    gpg --verify $SDIST_PATH.asc $SDIST_PATH 
else
    echo "USE_GPG=False, Skipping GPG sign"
fi
echo "
=== <END GPG SIGN> ===
"


# Verify that we want to publish
if [[ "$TAG_AND_UPLOAD" != "yes" ]]; then
    if [[ "$TAG_AND_UPLOAD" != "no" ]]; then
        read -p "Are you ready to publish version='$VERSION' on branch='$TRAVIS_BRANCH'? (input 'yes' to confirm)" ANS
        echo "ANS = $ANS"
        TAG_AND_UPLOAD="$ANS"
    else
        echo "Ready to publish VERSION='$VERSION' on branch='$TRAVIS_BRANCH'" 
    fi
else
    echo "Not ready to publish VERSION='$VERSION' on branch='$TRAVIS_BRANCH'" 
fi

if [[ "$TAG_AND_UPLOAD" == "yes" ]]; then

    if [[ "$TWINE_USERNAME" == "" ]]; then
        echo "Error TWINE_USERNAME is not set"
        exit 1
    fi
    if [[ "$TWINE_PASSWORD" == "" ]]; then
        echo "Error TWINE_PASSWORD is not set"
        exit 1
    fi

    if [[ "$TRAVIS_BRANCH" == "$DEPLOY_BRANCH" ]]; then
        echo "TRAVIS_BRANCH = $TRAVIS_BRANCH"
        git tag $VERSION -m "tarball tag $VERSION"
        git push --tags origin $DEPLOY_BRANCH
        if [ "$USE_GPG" == "True" ]; then
            twine upload --username $TWINE_USERNAME --password $TWINE_PASSWORD --sign $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
            twine upload --username $TWINE_USERNAME --password $TWINE_PASSWORD --sign $SDIST_PATH.asc $SDIST_PATH
        else
            twine upload --username $TWINE_USERNAME --password $TWINE_PASSWORD $BDIST_WHEEL_PATH 
            twine upload --username $TWINE_USERNAME --password $TWINE_PASSWORD $SDIST_PATH 
        fi
    else
        echo "TRAVIS_BRANCH!=DEPLOY_BRANCH. skipping tag and upload"
        echo "ONLY ABLE TO PUBLISH ON DEPLOY TRAVIS_BRANCH

        TRAVIS_BRANCH = $TRAVIS_BRANCH
        DEPLOY_BRANCH = $DEPLOY_BRANCH
        "
    fi
else  
    echo "Dry run"
    echo "skiping tag and upload"
fi

__notes__="""
Notes:
    # References: https://docs.travis-ci.com/user/deployment/pypi/
    travis encrypt TWINE_PASSWORD=$TWINE_PASSWORD  
    travis encrypt TWINE_USERNAME=$TWINE_USERNAME 
"""
