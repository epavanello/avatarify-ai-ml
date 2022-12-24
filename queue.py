import train
import generate
import rabbitmq

connection = rabbitmq.get_connection()
channel = connection.channel()

# Definire una funzione di callback per il consumer


def callback(_channel, method, _properties, body: bytes):
    if method.routing_key == 'train_photos':
        print(f"Train session: {body.decode()}")
        try:
            train.train(body.decode())
            print("Completed training")
        finally:
            pass
    elif method.routing_key == 'generate_photos':
        print(f"Generate image for session: {body.decode()}")
        try:
            generate.generate(body.decode())
            print("Generation complete")
        finally:
            pass


# Consumiamo i messaggi dalla prima coda
channel.basic_consume(queue='train_photos',
                      on_message_callback=callback, auto_ack=True)

# Consumiamo i messaggi dalla seconda coda in un nuovo thread
channel.basic_consume(queue='generate_photos',
                      on_message_callback=callback, auto_ack=True)


# Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
print('In attesa di ricevere messaggi...')
channel.start_consuming()
