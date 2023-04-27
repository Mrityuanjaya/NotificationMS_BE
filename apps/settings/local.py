import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail

load_dotenv()


class settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]

    # middlewares configuration
    CORS_ORIGIN_REGEX_WHITELIST: str = (
        r"^(http?:\/\/)?([a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]\.)?localhost:[0-9]+$"
    )

    CORS_CONFIG = {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
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
                    "apps.modules.recipients.schemas",
                    "apps.modules.notifications.schemas",
                ]
            },
        },
    }
    Mail_CONFIG = ConnectionConfig(
        MAIL_USERNAME=os.environ["MAIL_USERNAME"],
        MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
        MAIL_FROM=os.environ["MAIL_FROM"],
        MAIL_PORT=os.environ["MAIL_PORT"],
        MAIL_SERVER=os.environ["MAIL_SERVER"],
        USE_CREDENTIALS=os.environ["USE_CREDENTIALS"],
        MAIL_STARTTLS=os.environ["MAIL_STARTTLS"],
        MAIL_SSL_TLS=os.environ["MAIL_SSL_TLS"],
    )
    SEND_MAIL = FastMail(Mail_CONFIG)
