from pydantic import BaseModel
import generate
import rabbitmq
from typing import Optional
import time
from logger import LOGGER

class GeneratePayload(BaseModel):
    theme: str
    prompt: str
    seed: Optional[int]


def do_work(_channel, method, properties, body: bytes):
    session = properties.headers["session"]

    LOGGER.debug(f"New image for: {session}")
    try:
        payload = GeneratePayload.parse_raw(body)
        generate.generate(session, payload.theme, payload.prompt, payload.seed)
        LOGGER.debug("Image complete")
    except Exception as e:
        LOGGER.error(e)
        pass
    except :
        LOGGER.error(e)
        pass
    finally:
        pass


def main():
    rabbitmq.Run(["generate_photos"], do_work)


if __name__ == "__main__":
    main()
