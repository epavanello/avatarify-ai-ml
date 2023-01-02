import json
from pydantic import parse_obj_as
from typing import List
import train
import rabbitmq
from logger import LOGGER

# Definire una funzione di callback per il consumer


def do_work(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    LOGGER.debug(f"New Training for: {session}")
    try:
        payload = train.TrainPayload.parse_raw(body)
        train.train(session, payload.gender, payload.images)
        LOGGER.debug("Training completed")
    except Exception as e:
        LOGGER.error(e)
        pass
    finally:
        pass


def main():
    rabbitmq.Run(["train_photos"], do_work)


if __name__ == "__main__":
    main()
