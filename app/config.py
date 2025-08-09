import os
from pydantic import BaseSettings

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    host = os.getenv("FSTR_DB_HOST", "localhost")
    port = os.getenv("FSTR_DB_PORT", "5432")
    user = os.getenv("FSTR_DB_LOGIN", "postgres")
    password = os.getenv("FSTR_DB_PASS", "")
    dbname = os.getenv("FSTR_DB_NAME", "postgres")
    sslmode = os.getenv("FSTR_DB_SSLMODE", "")  # например: 'require'
    tail = f"?sslmode={sslmode}" if sslmode else ""
    DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}{tail}"

class Settings(BaseSettings):
    DATABASE_URL: str = DATABASE_URL

settings = Settings()
