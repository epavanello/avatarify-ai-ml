import train
import rabbitmq
from logger import LOGGER

# Definire una funzione di callback per il consumer


def do_work(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    LOGGER.info(f"New Training for: {session}")
    payload = train.TrainPayload.parse_raw(body)
    train.train(session, payload.images)
    LOGGER.info("Training completed")

def main():
    rabbitmq.Run(["train_photos"], do_work)


if __name__ == "__main__":
    main()
