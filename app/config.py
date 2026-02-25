import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "change_me")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = os.getenv("DATABASE_URL") or os.getenv(
        "DATABASE_url",
        "postgresql://postgres:password@localhost:5432/mydatabase",
    )


settings = Settings()
