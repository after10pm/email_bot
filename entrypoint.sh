#!/bin/bash

# Создаем директорию для данных, если её нет
mkdir -p /email_bot/data/json

# Проверяем, существуют ли файлы с данными
if [ ! -f "/email_bot/data/json/emails.json" ] && [ -f "/email_bot/emails.json" ]; then
    cp /email_bot/emails.json /email_bot/data/json/
fi

if [ ! -f "/email_bot/data/json/subjects.json" ] && [ -f "/email_bot/subjects.json" ]; then
    cp /email_bot/subjects.json /email_bot/data/json/
fi

if [ ! -f "/email_bot/data/json/keywords.json" ] && [ -f "/email_bot/keywords.json" ]; then
    cp /email_bot/keywords.json /email_bot/data/json/
fi

# Запускаем бота
python /email_bot/bot.py 