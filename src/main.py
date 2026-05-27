
import sys
import argparse  # Импортируем для разбора аргументов
import uvicorn   # Импортируем веб-сервер

# ==============================================================
# Здесь должно быть ваше FastAPI приложение
# Если его нет, создадим простейшую "заглушку"
# ==============================================================
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "User Service is running!"}

# ==============================================================


def run_stats_mode():
    """Функция, которая будет работать в режиме сбора статистики."""
    print("Stats Service запущен. Ожидание сообщений...")
    # В реальном приложении здесь будет код, который подключается к RabbitMQ
    # и слушает сообщения. Сейчас мы просто запустим бесконечный цикл,
    # чтобы контейнер не завершал работу.
    import time
    while True:
        time.sleep(3600) # "Спим" час, чтобы не нагружать процессор


if __name__ == "__main__":
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Запуск сервиса.")
    parser.add_argument("--stats", action="store_true", help="Запустить в режиме сбора статистики.")
    args = parser.parse_args()

    # Проверяем, был ли передан флаг --stats
    if args.stats:
        # Если да, запускаем режим статистики
        run_stats_mode()
    else:
        # Если нет, запускаем основной веб-сервер (user-service)
        print("User Service запущен. Запуск веб-сервера Uvicorn...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
