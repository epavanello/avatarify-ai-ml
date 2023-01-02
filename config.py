from pydantic import BaseSettings
from supabase import create_client, Client

class Settings(BaseSettings):
    rabbitmq_username: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"


def getSupabase():
    conf = Settings()
    client: Client = create_client(conf.supabase_url, conf.supabase_key)
    return client
