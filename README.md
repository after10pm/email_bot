# Telegram Email Bot

Бот для отправки email-сообщений через Telegram.

## Функции

- Отправка email-сообщений через Telegram
- Настройка списка email-адресов получателей
- Настройка темы сообщения
- Отправка через ключевое слово или прямую команду
- Хранение настроек в папке data

## Требования

- Docker и Docker Compose
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- SMTP-сервер для отправки email

## Установка

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Создайте файл `.env` с необходимыми переменными:
```
TELEGRAM_BOT_TOKEN=your_bot_token
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
EMAIL_LOGIN=your_email@example.com
EMAIL_PASSWORD=your_password
```

3. Создайте директорию для данных:
```bash
mkdir -p data
```

## Запуск с Docker Compose

Запустите бота с помощью Docker Compose:

```bash
docker-compose up -d
```

Для просмотра логов:

```bash
docker-compose logs -f
```

Для остановки бота:

```bash
docker-compose down
```

## Использование

Доступные команды:
- `/start` - информация о боте
- `/set_keyword СЛОВО` - задать ключевое слово
- `/add_email email` - добавить адрес
- `/remove_email email` - удалить адрес
- `/set_emails email1 email2` - задать список
- `/set_subject Тема` - задать тему
- `/send_message Текст` - отправить сообщение
- `/list` - показать настройки

Для отправки сообщения напрямую используйте ключевое слово:
```
КЛЮЧЕВОЕ_СЛОВО текст сообщения
``` 