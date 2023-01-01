from pydantic import BaseModel
import generate
import rabbitmq
from typing import Optional


class GeneratePayload(BaseModel):
    theme: str
    prompt: str
    seed: Optional[int]


def do_work(_channel, method, properties, body: bytes):
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
    rabbitmq.Run(["generate_photos"], do_work)


if __name__ == "__main__":
    main()
