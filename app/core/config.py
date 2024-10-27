from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    EXTERNAL_API_URL: str
    CELERY_FETCH_EVENTS_SCHEDULE: float

    class Config:
        env_file = ".env"


settings = Settings()
