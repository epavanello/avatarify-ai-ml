import json
from pydantic import parse_obj_as
from typing import List
import train
import rabbitmq

connection = rabbitmq.get_connection()
channel = connection.channel()

# Definire una funzione di callback per il consumer


def callback(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    print(f"Train session: {session}")
    try:
        images_json = body.decode()
        images_dict = json.loads(images_json)
        images = parse_obj_as(List[train.TrainImage], images_dict)

        train.train(session, images)
        print("Completed training")
    finally:
        pass


# Consumiamo i messaggi dalla prima coda
channel.basic_consume(queue='train_photos',
                      on_message_callback=callback, auto_ack=True)


# Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
print('In attesa di ricevere messaggi...')
channel.start_consuming()
