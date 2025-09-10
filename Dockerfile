# 1. Базовый образ Python
FROM python:3.11-slim

# 2. Системные зависимости для сборки Python-пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    libbz2-dev \
    liblzma-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Запуск Python с отключением буферизации
ENV PYTHONUNBUFFERED=1

# 4. Рабочая директория
WORKDIR /app

# 5. Копируем requirements.txt
COPY requirements.txt .

# 6. Обновляем pip, setuptools и wheel
RUN python -m pip install --upgrade pip setuptools wheel

# 7. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 8. Копируем весь проект
COPY . .

# 9. Запуск бота с авто-перезапуском при изменении кода
#CMD ["python", "-m", "watchgod", "--run", "python main.py"]
CMD ["python", "run_tg_bot.py"]

