import argparse
import uvicorn
import sys
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# 1. СОЗДАЕМ И ИНСТРУМЕНТИРУЕМ ПРИЛОЖЕНИЕ
app = FastAPI(title="Lab7 App")

# Инструментация метрик. Библиотека сама создаст эндпоинт /metrics
# и стандартные метрики, такие как http_requests_total.
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    # Просто возвращаем ответ. Библиотека сама посчитает запрос.
    return {"message": "Service is running with Prometheus metrics!"}


# 2. ЛОГИКА ЗАПУСКА
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск сервиса.")
    parser.add_argument("--stats", action="store_true", help="Запустить в режиме сбора статистики.")
    args = parser.parse_args()

    port_to_run = 8001 if args.stats else 8000
    print(f"Запускаю веб-сервер на порту {port_to_run}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port_to_run, reload=False)