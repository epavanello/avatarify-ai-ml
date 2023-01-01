import json
from pydantic import parse_obj_as
from typing import List
import train
import rabbitmq

# Definire una funzione di callback per il consumer


def do_work(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    print(f"Train session: {session}")
    try:
        images_json = body.decode()
        images_dict = json.loads(images_json)
        images = parse_obj_as(List[train.TrainImage], images_dict)

        train.train(session, images)
        print("Completed training")
    except Exception as e:
        print(e)
        pass
    finally:
        pass


def main():
    rabbitmq.Run(["train_photos"], do_work)


if __name__ == "__main__":
    main()
