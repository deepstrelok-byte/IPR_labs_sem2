import time
import argparse
import uvicorn
import os
import sys
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# --- Трейсинг ---
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource



# 1. СНАЧАЛА НАСТРАИВАЕМ ТРЕЙСИНГ

def configure_tracing():
    is_stats_mode = "--stats" in sys.argv
    service_name = "stats-service" if is_stats_mode else os.getenv("OTEL_SERVICE_NAME", "user-service")

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    provider = TracerProvider(resource=Resource(attributes={"service.name": service_name}))

    # Всегда выводим в консоль для отладки
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    if otlp_endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))

    trace.set_tracer_provider(provider)
    print(f"--- Трейсинг настроен для сервиса '{service_name}' ---")


configure_tracing()

# 2. СОЗДАЕМ И ИНСТРУМЕНТИРУЕМ ПРИЛОЖЕНИЕ

app = FastAPI(title="Lab7 App")

Instrumentator().instrument(app).expose(app)
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
def read_root():
    print("--- ПОЛУЧЕН ЗАПРОС НА / ---")
    return {"message": "Hello from the FINAL debug version!"}



# 3. ЛОГИКА ЗАПУСКА

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск сервиса.")
    parser.add_argument("--stats", action="store_true", help="Запустить в режиме сбора статистики.")
    args = parser.parse_args()

    port_to_run = 8001 if args.stats else 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port_to_run, reload=False)