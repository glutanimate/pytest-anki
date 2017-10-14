#!/usr/bin/env bash

anki_dir='anki_root'

if [ ! -e "$anki_dir" ]
then
    echo "$anki_dir not detected, cloning from master"
    git clone https://github.com/dae/anki anki_root
    cd anki_root
    pip install -r requirements.txt
    ./tools/build_ui.sh
    cd ..
fi

python3.6 -m pytest tests

