# Admin_tg - Управление постами через Telegram и FastAPI

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![Telegram](https://img.shields.io/badge/Telegram%20Bot-4.15.0-blue.svg)
![Docker](https://img.shields.io/badge/Docker-20.10.12-blue.svg)

Admin_tg - это комплексное решение для управления контентом через Telegram, состоящее из:
1. FastAPI бэкенда для управления пользователями и постами
2. Telegram бота для взаимодействия с пользователями
3. Docker-контейнеризации для простого развертывания

## Особенности проекта

- 📱 Удобное управление контентом через Telegram
- 🔒 Аутентификация пользователей по токенам
- 📦 Полная контейнеризация с Docker
- 🚀 Асинхронная архитектура (FastAPI + SQLAlchemy)
- 📊 Гибкая фильтрация и сортировка постов
- 🔄 Автоматическое создание схемы базы данных при запуске

## Стек технологий

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy 2.0, AsyncPG
- **Telegram Bot**: pyTelegramBotAPI
- **Containerization**: Docker, Docker Compose
- **API Documentation**: Swagger UI (автогенерация)

## Быстрый старт

### Предварительные требования

- Docker Engine 20.10+
- Docker Compose 1.29+

### Запуск проекта

```bash
git clone https://github.com/DimaChepuchtanov/Admin_tg.git
cd Admin_tg

# Создайте .env файл с вашими настройками
echo PG_USER = 'postgres' PG_PASSWORD = '1q2w3e4r' PG_HOST = "postgres" PG_PORT = "5432" PG_DB = "post_tg" > .env

# Запустите проект
docker-compose up -d --build
```


### Использование Telegram бота
Для использования бота, нужно запустить файл bot.py
Ссылка на бота @hh_token_test_bot

# Используйте команды:

/post - Показать список постов

### Документация
Полная документация API доступна по адресу http://127.0.0.1:5000/docs
