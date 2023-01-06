#!/bin/bash

cd /home/ubuntu/avatarify-ai-ml/

python3 generate_photos_queue.py > generate.log 2>&1

sudo shutdown

exit 0