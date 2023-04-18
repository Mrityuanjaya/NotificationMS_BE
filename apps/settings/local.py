import os
from dotenv import load_dotenv

load_dotenv()


class settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]
    # database config
    DATABASE_CONFIG = {
        "connections": {
            "default": os.environ["DATABASE_URL"],
        },
        "apps": {
            "models": {
                "models": [
                    "apps.modules.users.schemas",
                    "apps.modules.applications.schemas",
                ]
            },
        },
    }

    # middlewares configuration
    ALLOWED_ORIGINS: list[str] = [
        "127.0.0.1",
        "0.0.0.0",
        "localhost",
        "http://localhost:5173",
    ]
    CORS_CONFIG = {
        "allow_origins": ALLOWED_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
