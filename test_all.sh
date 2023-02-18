#!/bin/zsh

# load env
source ~/.zshrc

python ./test.py --legacy
python ./test.py --nickname
python ./test.py --rebirth
python ./test.py --badge
python ./test.py --farm
python ./test.py --friends

