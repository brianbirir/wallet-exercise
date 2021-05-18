import os
from dotenv import load_dotenv


class Config:
    """Aggregates configuration variables for the application"""

    env_file_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
    env_file = env_file_path + "/" + ".env"
    load_dotenv(dotenv_path=env_file)

    SECRET_KEY = str(os.getenv("SECRET_KEY"))
    SQLALCHEMY_DATABASE_URI = str(os.getenv("DATABASE_URI"))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = os.getenv("JWT_BLACKLIST_ENABLED")
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    DEFAULT_USER_PASSWORD = os.environ.get("DEFAULT_USER_PASSWORD")


class ProductionConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://wallet_admin:zDVj5mMdLfWPLeup@wallet_web_db/wallet_db"
    )


class TestingConfig(Config):
    db_base_dir = os.path.abspath(os.path.dirname(__file__))
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(db_base_dir, "testing.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
