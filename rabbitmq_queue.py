import pika
import train

# Creare una connessione a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Dichiarare una coda a cui il consumer si sottoscriverà
channel.queue_declare(queue='train_photos')

# Definire una funzione di callback per il consumer


def callback(_channel, _method, _properties, body: bytes):
    print(f"Train session: {body.decode()}")
    try:
        train.train(body.decode())
        print("Completed training")
    finally:
        pass


# Sottoscriversi alla coda e specificare la funzione di callback da utilizzare per i messaggi ricevuti
channel.basic_consume(
    queue='train_photos', on_message_callback=callback, auto_ack=True)

# Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
print('In attesa di ricevere messaggi...')
channel.start_consuming()
