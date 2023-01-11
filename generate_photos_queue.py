from pydantic import BaseModel
import generate
import rabbitmq
from typing import Optional
from logger import LOGGER


class GeneratePayload(BaseModel):
    theme: str
    prompt: str
    negative_prompt: str
    seed: Optional[int]


def do_work(_channel, method, properties, body: bytes):
    session = properties.headers["session"]
    LOGGER.info(f"New image for: {session}")
    payload = GeneratePayload.parse_raw(body)
    generate.generate(session, payload.theme, payload.prompt,
                      payload.negative_prompt, payload.seed)
    LOGGER.info("Image complete")


def main():
    rabbitmq.Run(["generate_photos"], do_work)


if __name__ == "__main__":
    main()
