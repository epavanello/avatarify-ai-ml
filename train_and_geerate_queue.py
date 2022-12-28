import json
from pydantic import BaseModel
from typing import List
import generate
import rabbitmq
import generate_photos_queue
import train_photos_queue

connection = rabbitmq.get_connection()
channel = connection.channel()

# Definire una funzione di callback per il consumer


class Image(BaseModel):
    base64: str
    filename: str


class Images(BaseModel):
    __root__: List[Image]


def callback(channel, method, properties, body):
    if method.routing_key == 'train_photos':
        train_photos_queue.callback(channel, method, properties, body)
    elif method.routing_key == 'generate_photos':
        generate_photos_queue.callback(channel, method, properties, body)


# Consumiamo i messaggi dalla seconda coda in un nuovo thread
channel.basic_consume(queue='train_photos',
                      on_message_callback=callback, auto_ack=True)

# Consumiamo i messaggi dalla seconda coda in un nuovo thread
channel.basic_consume(queue='generate_photos',
                      on_message_callback=callback, auto_ack=True)


# Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
print('In attesa di ricevere messaggi...')
channel.start_consuming()
