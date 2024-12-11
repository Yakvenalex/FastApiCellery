import os
import ssl
import redis
from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_HOST: str
    BASE_URL: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, 'app/uploads')
    STATIC_DIR: str = os.path.join(BASE_DIR, 'app/static')
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


# Получаем параметры для загрузки переменных среды
settings = Settings()
redis_url = f"rediss://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
celery_app = Celery("celery_worker", broker=redis_url, backend=redis_url)
ssl_options = {"ssl_cert_reqs": ssl.CERT_NONE}
celery_app.conf.update(broker_use_ssl=ssl_options, redis_backend_use_ssl=ssl_options)
redis_client = redis.Redis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT,
                           db=0, password=settings.REDIS_PASSWORD,
                           ssl=True, ssl_cert_reqs=None)
