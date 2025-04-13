FROM python:3.10-slim

WORKDIR /email_bot

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бота
COPY bot.py .
COPY entrypoint.sh .
COPY .env .

# Создание директории для данных
RUN mkdir -p /email_bot/data
VOLUME /email_bot/data

# Делаем скрипт запуска исполняемым
RUN chmod +x /email_bot/entrypoint.sh

CMD ["/email_bot/entrypoint.sh"] 