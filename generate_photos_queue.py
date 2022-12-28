import json
from pydantic import BaseModel
from typing import List
import generate
import rabbitmq

connection = rabbitmq.get_connection()
channel = connection.channel()

# Definire una funzione di callback per il consumer


class Image(BaseModel):
    base64: str
    filename: str


class Images(BaseModel):
    __root__: List[Image]


def callback(_channel, method, _properties, body: bytes):
    print(f"Generate image for session: {body.decode()}")
    try:
        generate.generate(body.decode())
        print("Generation complete")
    finally:
        pass


# Consumiamo i messaggi dalla seconda coda in un nuovo thread
channel.basic_consume(queue='generate_photos',
                      on_message_callback=callback, auto_ack=True)


# Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
print('In attesa di ricevere messaggi...')
channel.start_consuming()
