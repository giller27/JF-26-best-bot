FROM python:3.12-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо список залежностей
COPY requirements.txt .

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проекту (включаючи папку src)
COPY . .

# Відкриваємо порт для адмінки
EXPOSE 8000

# Запуск головного файлу
CMD ["python", "main.py"]