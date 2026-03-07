from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # =========================
    # DATABASE
    # =========================
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # =========================
    # API
    # =========================
    API_KEY: str

    # =========================
    # SMTP
    # =========================
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()