# Используем официальный Python образ
FROM python:3.11-slim as builder

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
COPY pyproject.toml .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt


# ---------------------------
# Финальный образ
# ---------------------------
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /app/requirements.txt .

# Копируем исходный код
COPY src/ ./src/

# Создаем пользователя без привилегий
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Точка входа
ENTRYPOINT ["python", "-m", "src.main"]
