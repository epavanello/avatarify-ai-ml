from pydantic import BaseSettings


class Settings(BaseSettings):
    rabbitmq_username: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"
