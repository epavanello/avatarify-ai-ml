#!/bin/bash

cd /home/ubuntu/avatarify-ai-ml/

python3 train_photos_queue.py > train.log 2>&1

sudo shutdown

exit 0