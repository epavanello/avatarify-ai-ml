#!/bin/bash

cd /home/ubuntu/avatarify-ai-ml/

python3 train_and_geerate_queue.py > train_and_geerate.log 2>&1

sudo shutdown

exit 0