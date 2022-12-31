from pydantic import BaseModel
import generate
import rabbitmq
from typing import Optional


class GeneratePayload(BaseModel):
    theme: str
    prompt: str
    seed: Optional[int]


def callback(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    print(f"Generate image for session: {session}")
    try:
        payload = GeneratePayload.parse_raw(body)
        generate.generate(session, payload.theme, payload.prompt, payload.seed)
        print("Generation complete")
    except Exception as e:
        print(e)
        pass
    finally:
        pass


def main():
    connection = rabbitmq.get_connection()
    channel = connection.channel()
    # Consumiamo i messaggi dalla seconda coda in un nuovo thread
    channel.basic_consume(queue='generate_photos',
                          on_message_callback=callback, auto_ack=True)

    # Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
    print('In attesa di ricevere messaggi...')
    channel.start_consuming()


if __name__ == "__main__":
    main()
