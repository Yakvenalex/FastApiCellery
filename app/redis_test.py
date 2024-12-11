import redis
from app.config import settings


# Подключение к Redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,  # Стандартный порт Redis
    password=settings.REDIS_PASSWORD,
    ssl=True,  # Включаем SSL
    ssl_cert_reqs=None  # Отключаем проверку сертификата, если нужно
)

# Проверка подключения
try:
    # Попытка выполнить команду PING
    response = r.ping()
    if response:
        print("Подключение к Redis успешно!")
    else:
        print("Не удалось подключиться к Redis.")
except Exception as e:
    print(f"Произошла неизвестная ошибка: {e}")
