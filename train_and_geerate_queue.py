import json
from pydantic import BaseModel
from typing import List
import generate
import rabbitmq
import generate_photos_queue
import train_photos_queue


def do_work(channel, method, properties, body):
    if method.routing_key == 'train_photos':
        train_photos_queue.do_work(channel, method, properties, body)
    elif method.routing_key == 'generate_photos':
        generate_photos_queue.do_work(channel, method, properties, body)


rabbitmq.Run(["train_photos", "generate_photos"], do_work)