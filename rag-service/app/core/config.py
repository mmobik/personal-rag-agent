from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    class Config:
        env_file = ".env"

settings = Settings()
