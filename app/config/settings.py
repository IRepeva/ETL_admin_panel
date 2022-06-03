import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, RedisDsn, PostgresDsn
from split_settings.tools import include

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

include(
    'components/applications.py',
    'components/database.py',
    'components/localization.py',
    'components/static.py',
    'components/validations.py',
    'components/logging.py',
    'components/celery.py',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'postgres']
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080", ]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
}


class Settings(BaseSettings):

    DB_DSN: PostgresDsn = 'postgres://irepeva:2404IRepeva@127.0.0.1:5432/movies_database'
    REDIS_DSN: RedisDsn = 'redis://127.0.0.1:6379'

    ES_DSN: str = 'http://127.0.0.1:9200'

    class Config:
        env_file = ".env"


settings = Settings()


if DEBUG:
    import os  # only if you haven't already imported this
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1",
                                                                 "10.0.2.2"]

SHOW_TOOLBAR_CALLBACK = True

