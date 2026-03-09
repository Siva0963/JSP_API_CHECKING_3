from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =========================
    # DATABASE CONFIGURATION
    # =========================
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # =========================
    # API SECURITY
    # =========================
    API_KEY: str


    # =========================
    # SMTP EMAIL CONFIGURATION
    # =========================
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    # =========================
    # TWILIO SMS CONFIGURATION
    # =========================
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str


    # =========================
    # fast2sms CONFIGURATION
    # =========================
    FAST2SMS_API_KEY: str
    FAST2SMS_URL: str

    # =========================
    # ENV CONFIG
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


settings = Settings()