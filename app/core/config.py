from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()