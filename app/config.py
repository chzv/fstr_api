import os

class Settings:
    DB_HOST = os.getenv("FSTR_DB_HOST", "localhost")
    DB_PORT = int(os.getenv("FSTR_DB_PORT", "5432"))
    DB_LOGIN = os.getenv("FSTR_DB_LOGIN", "postgres")
    DB_PASS = os.getenv("FSTR_DB_PASS", "postgres")
    DB_NAME = os.getenv("FSTR_DB_NAME", "fstr")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_LOGIN}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

settings = Settings()
