import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail

load_dotenv()

# database config
DATABASE_CONFIG = {
    "connections": {
        "default": os.environ["DATABASE_URL"],
    },
    "apps": {
        "models": {
            "models": [
                "apps.modules.users.schemas",
                "apps.modules.applications.schemas"
            ]
        },
    },
}


class settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]

    # middlewares configuration
    ALLOWED_ORIGINS: list[str] = [
        "127.0.0.1",
        "0.0.0.0",
        "localhost",
        "http://localhost:5173",
    ]
    CORS_CONFIG = {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }

    Mail_CONFIG = ConnectionConfig(
        MAIL_USERNAME = os.environ["MAIL_USERNAME"],
        MAIL_PASSWORD = os.environ["MAIL_PASSWORD"],
        MAIL_FROM= os.environ["MAIL_FROM"],
        MAIL_PORT= os.environ["MAIL_PORT"],
        MAIL_SERVER=os.environ["MAIL_SERVER"],
        USE_CREDENTIALS=os.environ["USE_CREDENTIALS"],
        MAIL_STARTTLS=os.environ["MAIL_STARTTLS"],
        MAIL_SSL_TLS=os.environ["MAIL_SSL_TLS"],
    )
    SEND_MAIL = FastMail(Mail_CONFIG)
