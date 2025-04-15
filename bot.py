import os
import logging
import smtplib
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from typing import List
import ssl

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для хранения email-адресов
EMAILS_FILE = 'data/emails.json'
# Файл для хранения тем сообщений
SUBJECTS_FILE = 'data/subjects.json'
# Файл для хранения ключевых слов
KEYWORDS_FILE = 'data/keywords.json'


# Загрузка сохраненных email-адресов
def load_emails():
    if os.path.exists(EMAILS_FILE):
        try:
            with open(EMAILS_FILE, 'r') as f:
                data = json.load(f)
                # Конвертируем ключи обратно в int для chat_id, если они являются числами
                result = {}
                for key, value in data.items():
                    if key.lstrip('-').isdigit():  # Если это число или отрицательное число
                        result[int(key)] = value
                    else:
                        result[key] = value
                logger.info(f"Загружены email-адреса: {result}")
                return result
        except Exception as e:
            logger.error(f"Error loading emails: {str(e)}")
    return {}


# Сохранение email-адресов
def save_emails(emails):
    try:
        # Преобразуем все ключи в строки для сохранения в JSON
        data_to_save = {}
        for key, value in emails.items():
            data_to_save[str(key)] = value

        with open(EMAILS_FILE, 'w') as f:
            json.dump(data_to_save, f)
        logger.info(f"Сохранены email-адреса: {emails}")
    except Exception as e:
        logger.error(f"Error saving emails: {str(e)}")


# Загрузка сохраненных тем
def load_subjects():
    if os.path.exists(SUBJECTS_FILE):
        try:
            with open(SUBJECTS_FILE, 'r') as f:
                data = json.load(f)
                # Конвертируем ключи обратно в int для chat_id, если они являются числами
                result = {}
                for key, value in data.items():
                    if key.lstrip('-').isdigit():  # Если это число или отрицательное число
                        result[int(key)] = value
                    else:
                        result[key] = value
                logger.info(f"Загружены темы: {result}")
                return result
        except Exception as e:
            logger.error(f"Error loading subjects: {str(e)}")
    return {}


# Сохранение тем
def save_subjects(subjects):
    try:
        # Преобразуем все ключи в строки для сохранения в JSON
        data_to_save = {}
        for key, value in subjects.items():
            data_to_save[str(key)] = value

        with open(SUBJECTS_FILE, 'w') as f:
            json.dump(data_to_save, f)
        logger.info(f"Сохранены темы: {subjects}")
    except Exception as e:
        logger.error(f"Error saving subjects: {str(e)}")


# Загрузка сохраненных ключевых слов
def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        try:
            with open(KEYWORDS_FILE, 'r') as f:
                data = json.load(f)
                # Конвертируем ключи обратно в int для chat_id, если они являются числами
                result = {}
                for key, value in data.items():
                    if key.lstrip('-').isdigit():  # Если это число или отрицательное число
                        result[int(key)] = value
                    else:
                        result[key] = value
                logger.info(f"Загружены ключевые слова: {result}")
                return result
        except Exception as e:
            logger.error(f"Error loading keywords: {str(e)}")
    return {}


# Сохранение ключевых слов
def save_keywords(keywords):
    try:
        # Преобразуем все ключи в строки для сохранения в JSON
        data_to_save = {}
        for key, value in keywords.items():
            data_to_save[str(key)] = value

        with open(KEYWORDS_FILE, 'w') as f:
            json.dump(data_to_save, f)
        logger.info(f"Сохранены ключевые слова: {keywords}")
    except Exception as e:
        logger.error(f"Error saving keywords: {str(e)}")


# Словарь для хранения email-адресов для каждого чата
chat_emails = load_emails()
# Словарь для хранения тем для каждого чата
chat_subjects = load_subjects()
# Словарь для хранения ключевых слов для каждого чата
chat_keywords = load_keywords()


async def send_email(to_emails: List[str], subject: str, message: str) -> bool:
    """Отправка email"""
    try:
        logger.info(f"Начинаем отправку email на адреса: {to_emails}")
        logger.info(f"Тема: {subject}")
        logger.info(f"Тело сообщения: {message}")

        # Проверяем настройки SMTP
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = os.getenv('SMTP_PORT')
        email_login = os.getenv('EMAIL_LOGIN')
        email_password = os.getenv('EMAIL_PASSWORD')

        if not all([smtp_server, smtp_port, email_login, email_password]):
            logger.error("Не все настройки SMTP установлены")
            return False

        logger.info(f"SMTP сервер: {smtp_server}, порт: {smtp_port}")
        logger.info(f"Отправитель: {email_login}")

        # Создаем сообщение
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = email_login
        msg['To'] = ', '.join(to_emails)

        # Подключаемся к SMTP-серверу
        logger.info("Создаем SSL контекст")
        context = ssl.create_default_context()

        logger.info("Подключаемся к SMTP серверу")
        with smtplib.SMTP_SSL(smtp_server, int(smtp_port), context=context) as server:
            logger.info("Выполняем вход")
            server.login(email_login, email_password)

            logger.info("Отправляем сообщение")
            server.send_message(msg)

        logger.info("Сообщение успешно отправлено")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке email: {str(e)}")
        logger.exception("Подробная информация об ошибке:")
        return False


async def send_email_with_attachment(to_emails, subject, message, attachment, filename):
    """Отправка email-сообщения с вложением"""
    try:
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_LOGIN')
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Добавляем вложение
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)

        # Подключаемся к SMTP-серверу через SSL
        server = smtplib.SMTP_SSL(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
        server.login(os.getenv('EMAIL_LOGIN'), os.getenv('EMAIL_PASSWORD'))

        # Отправляем сообщение
        for email in to_emails:
            msg['To'] = email
            server.send_message(msg)
            logger.info(f"Email with attachment sent to {email}")

        server.quit()
        return True
    except Exception as e:
        logger.error(f"Error sending email with attachment: {str(e)}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Бот для отправки email-сообщений\n\n'
        'Команды:\n'
        '/set_keyword СЛОВО - задать ключевое слово\n'
        '/add_email email - добавить адрес\n'
        '/remove_email email - удалить адрес\n'
        '/set_emails email1 email2 - задать список\n'
        '/set_subject Тема - задать тему\n'
        '/send_message Текст - отправить сообщение\n'
        '/list - показать настройки\n\n'
        'Для отправки: КЛЮЧЕВОЕ_СЛОВО текст сообщения'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    # Получаем ID чата и преобразуем его в строку, а также сохраняем оригинальный ID
    original_chat_id = update.effective_chat.id
    chat_id = str(original_chat_id)
    message_text = update.message.text

    logger.info(f"Получено сообщение: '{message_text}' от чата {chat_id} (оригинальный ID: {original_chat_id})")
    logger.info(f"Тип ID чата: {type(chat_id)}, тип оригинального ID: {type(original_chat_id)}")
    logger.info(f"Все ключевые слова: {chat_keywords}")
    logger.info(f"Все email-адреса: {chat_emails}")
    logger.info(f"Ключи в словаре ключевых слов: {list(chat_keywords.keys())}")
    logger.info(f"Ключи в словаре email: {list(chat_emails.keys())}")

    # Проверяем, есть ли ключевое слово для этого чата (проверяем обе формы ID)
    if chat_id not in chat_keywords and original_chat_id not in chat_keywords:
        logger.info(f"Для чата {chat_id} не настроено ключевое слово")
        return

    # Определяем, какой ключ использовать
    key_to_use = chat_id if chat_id in chat_keywords else original_chat_id
    logger.info(f"Используем ключ {key_to_use} для доступа к словарям")

    # Проверяем, начинается ли сообщение с ключевого слова
    keyword = chat_keywords[key_to_use]
    logger.info(f"Ключевое слово для чата {key_to_use}: '{keyword}'")

    # Дополнительная проверка на совпадение в разных форматах
    starts_with = message_text.startswith(keyword)
    starts_with_case_insensitive = message_text.lower().startswith(keyword.lower())
    exact_match = keyword in message_text

    logger.info(f"Проверка startswith: {starts_with}")
    logger.info(f"Проверка startswith (case insensitive): {starts_with_case_insensitive}")
    logger.info(f"Проверка exact_match: {exact_match}")

    if starts_with:
        logger.info(f"Сообщение начинается с ключевого слова '{keyword}'")

        # Проверяем, настроены ли email-адреса (проверяем обе формы ID)
        if (chat_id not in chat_emails or not chat_emails.get(chat_id)) and (
                original_chat_id not in chat_emails or not chat_emails.get(original_chat_id)):
            logger.warning(f"Для чата {key_to_use} не настроены email-адреса")
            await update.message.reply_text("Сначала настройте email: /set_emails email1 email2")
            return

        # Определяем, какой ключ использовать для email
        email_key = chat_id if chat_id in chat_emails else original_chat_id
        logger.info(f"Используем ключ {email_key} для доступа к email-адресам")
        logger.info(f"Email-адреса для чата {email_key}: {chat_emails[email_key]}")

        # Получаем текст сообщения без ключевого слова
        email_text = message_text[len(keyword):].strip()
        logger.info(f"Текст для отправки: '{email_text}'")

        # Проверяем, установлена ли тема
        subject_key = chat_id if chat_id in chat_subjects else original_chat_id
        subject = chat_subjects.get(subject_key, "Без темы")
        logger.info(f"Тема сообщения: '{subject}'")

        # Отправляем email
        try:
            await update.message.reply_text("Отправляю...")
            success = await send_email(chat_emails[email_key], subject, email_text)

            if success:
                await update.message.reply_text("Отправлено!")
            else:
                await update.message.reply_text("Ошибка отправки. Проверьте логи.")
        except Exception as e:
            logger.exception(f"Исключение при отправке сообщения: {str(e)}")
            await update.message.reply_text(f"Ошибка: {str(e)}")
    # Если сообщение начинается с ключевого слова без учета регистра
    elif starts_with_case_insensitive:
        logger.info(f"Сообщение начинается с ключевого слова '{keyword}' (без учета регистра)")
        await update.message.reply_text(f"Используйте точное ключевое слово: {keyword}")
    else:
        logger.info(f"Сообщение не начинается с ключевого слова '{keyword}'")
        logger.info(
            f"Проверка: '{message_text[:len(keyword) if len(keyword) <= len(message_text) else len(message_text)]}' == '{keyword}'")
        # Если сообщение не начинается с ключевого слова, игнорируем его


async def add_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавление email-адреса в список"""
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    # Получаем email из текста команды
    if not context.args:
        await update.message.reply_text('Используйте: /add_email email')
        return

    email = context.args[0]

    logger.info(f"Добавляем email '{email}' для чата {chat_id}")

    # Проверяем формат email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await update.message.reply_text('Неверный формат email')
        return

    # Инициализируем список email-адресов для чата, если его нет
    if chat_id not in chat_emails:
        chat_emails[chat_id] = []

    # Проверяем, есть ли уже такой email в списке
    if email in chat_emails[chat_id]:
        await update.message.reply_text('Email уже в списке')
        return

    # Добавляем email в список
    chat_emails[chat_id].append(email)
    save_emails(chat_emails)

    await update.message.reply_text(f'Email добавлен: {", ".join(chat_emails[chat_id])}')


async def list_emails(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ списка email-адресов и настроек"""
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    logger.info(f"Выводим список настроек для чата {chat_id}")

    message = []

    if chat_id in chat_emails and chat_emails[chat_id]:
        message.append(f'Email: {", ".join(chat_emails[chat_id])}')
    else:
        message.append('Email: не настроены')

    if chat_id in chat_subjects:
        message.append(f'Тема: {chat_subjects[chat_id]}')
    else:
        message.append('Тема: не задана')

    if chat_id in chat_keywords:
        message.append(f'Ключевое слово: {chat_keywords[chat_id]}')
    else:
        message.append('Ключевое слово: не задано')

    await update.message.reply_text('\n'.join(message))


async def set_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /set_keyword"""
    # Получаем ключевое слово из текста команды
    if not context.args:
        await update.message.reply_text('Используйте: /set_keyword СЛОВО')
        return

    keyword = context.args[0]
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    logger.info(f"Устанавливаем ключевое слово '{keyword}' для чата {chat_id}")

    chat_keywords[chat_id] = keyword
    save_keywords(chat_keywords)

    await update.message.reply_text(f'Ключевое слово: {keyword}')


async def set_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Установка темы сообщения"""
    # Получаем тему из текста команды
    if not context.args:
        await update.message.reply_text('Используйте: /set_subject Тема')
        return

    subject = ' '.join(context.args)
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    logger.info(f"Устанавливаем тему '{subject}' для чата {chat_id}")

    chat_subjects[chat_id] = subject
    save_subjects(chat_subjects)

    await update.message.reply_text(f'Тема: {subject}')


async def set_emails(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Установка списка email-адресов"""
    # Получаем список email из текста команды
    if not context.args:
        await update.message.reply_text('Используйте: /set_emails email1 email2')
        return

    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)
    email_list = context.args

    logger.info(f"Устанавливаем список email-адресов {email_list} для чата {chat_id}")

    # Проверяем формат каждого email
    for email in email_list:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            await update.message.reply_text(f'Неверный формат: {email}')
            return

    chat_emails[chat_id] = email_list
    save_emails(chat_emails)

    await update.message.reply_text(f'Email-адреса: {", ".join(email_list)}')


async def remove_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удаление email-адреса из списка"""
    # Получаем email из текста команды
    if not context.args:
        await update.message.reply_text('Используйте: /remove_email email')
        return

    email = context.args[0]
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    logger.info(f"Удаляем email '{email}' для чата {chat_id}")

    if chat_id not in chat_emails or not chat_emails[chat_id]:
        await update.message.reply_text('Список пуст')
        return

    if email not in chat_emails[chat_id]:
        await update.message.reply_text('Email не найден в списке')
        return

    chat_emails[chat_id].remove(email)
    save_emails(chat_emails)

    await update.message.reply_text(f'Email удален, текущий список почт: {", ".join(chat_emails[chat_id])}')


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения на email напрямую через команду"""
    chat_id = update.effective_chat.id  # Используем исходный ID чата (integer)

    # Получаем текст сообщения из команды
    if not context.args:
        await update.message.reply_text('Используйте: /send_message Текст')
        return

    message_text = ' '.join(context.args)
    logger.info(f"Отправка сообщения: '{message_text}' из чата {chat_id}")

    # Проверяем, настроены ли email-адреса
    if chat_id not in chat_emails or not chat_emails[chat_id]:
        logger.warning(f"Для чата {chat_id} не настроены email-адреса")
        await update.message.reply_text("Сначала настройте email: /set_emails email1 email2")
        return

    logger.info(f"Email-адреса для чата {chat_id}: {chat_emails[chat_id]}")

    # Проверяем, установлена ли тема
    subject = chat_subjects.get(chat_id, "Без темы")
    logger.info(f"Тема сообщения: '{subject}'")

    # Отправляем email
    try:
        await update.message.reply_text("Отправляю...")
        success = await send_email(chat_emails[chat_id], subject, message_text)

        if success:
            await update.message.reply_text("Отправлено!")
        else:
            await update.message.reply_text("Ошибка отправки. Проверьте логи.")
    except Exception as e:
        logger.exception(f"Исключение при отправке сообщения: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")


def main() -> None:
    """Запуск бота"""
    # Загружаем данные из файлов
    global chat_emails, chat_subjects, chat_keywords
    chat_emails = load_emails()
    chat_subjects = load_subjects()
    chat_keywords = load_keywords()

    # Перезаписываем файлы с правильными типами ключей, если это необходимо
    save_emails(chat_emails)
    save_subjects(chat_subjects)
    save_keywords(chat_keywords)

    logger.info(f"Загруженные email-адреса: {chat_emails}")
    logger.info(f"Загруженные темы: {chat_subjects}")
    logger.info(f"Загруженные ключевые слова: {chat_keywords}")
    logger.info(f"Типы ключей в словаре email: {[type(k) for k in chat_emails.keys()]}")
    logger.info(f"Типы ключей в словаре тем: {[type(k) for k in chat_subjects.keys()]}")
    logger.info(f"Типы ключей в словаре ключевых слов: {[type(k) for k in chat_keywords.keys()]}")

    # Создаем приложение
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_keyword", set_keyword))
    application.add_handler(CommandHandler("list", list_emails))
    application.add_handler(CommandHandler("add_email", add_email))
    application.add_handler(CommandHandler("remove_email", remove_email))
    application.add_handler(CommandHandler("set_emails", set_emails))
    application.add_handler(CommandHandler("set_subject", set_subject))
    application.add_handler(CommandHandler("send_message", send_message))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Настраиваем меню команд
    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands([
            BotCommand("start", "Начать работу с ботом"),
            BotCommand("set_keyword", "Установить ключевое слово"),
            BotCommand("set_emails", "Настроить список email-адресов"),
            BotCommand("set_subject", "Настроить тему сообщения"),
            BotCommand("list", "Показать текущие настройки"),
            BotCommand("add_email", "Добавить email в список"),
            BotCommand("remove_email", "Удалить email из списка"),
            BotCommand("send_message", "Отправить сообщение на email")
        ])

    # Запускаем бота
    print("Запуск бота...")
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    print("Бот остановлен")


if __name__ == '__main__':
    main()
