from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    API_GATEWAY_URL: str = "http://api-gateway:8000"

    class Config:
        env_file = ".env"

settings = Settings()
