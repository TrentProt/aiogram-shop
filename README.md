# Telegram Bot with Aiogram, SQLAlchemy and Docker

Простой телеграм бот для управления каталогом товаров, корзиной и заказами с админ-панелью.

## 🚀 Технологии

- **Python 3.11+** - основной язык программирования
- **Aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **aiosqlite** - асинхронный драйвер для SQLite
- **Pydantic** - валидация данных и настройки
- **Docker** - контейнеризация приложения
- **SQLite** - база данных


## ⚙️ Установка и запуск

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone https://github.com/TrentProt/aiogram-shop
cd telegram-bot

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка окружения
#### Создайте файл .env на основе .env.example:
```bash
# Скопируйте пример файла окружения
cp .env.example .env
```

```bash
# Токен бота
APP_CONFIG__API__KEY=<КЛЮЧ АПИ>

# Настройки базы данных, можете поставить любой url бд, только надо доустановить библиотеки
APP_CONFIG__DB__URL=sqlite+aiosqlite:///main.db
APP_CONFIG__DB__ECHO=0

# ID администраторов (через запятую)
APP_CONFIG__ADMINS__TG_IDS=[ТГ ID]
```
### 3. Запуск в разработке
```bash
# Запуск бота
python main.py
```

### Тестирование

Запуск тестов:
```bash
#Все тесты
pytest
```

### Схема бд
```bash
┌─────────────────┐         ┌─────────────────┐
│     users       │         │   categories    │
├─────────────────┤         ├─────────────────┤
│ telegram_id (PK)│         │ id (PK)         │
│ username        │         │ name            │
│ role            │         └─────────────────┘
└─────────────────┘                   │
         │                            │
         │ 1:N                        │ 1:N
         │                            │
         ▼                            ▼
┌─────────────────┐         ┌─────────────────┐
│      cart       │         │    products     │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ user_id (FK)    │         │ name            │
│ product_id (FK) │◄────┐   │ price           │
│ qty             │     │   │ description     │
└─────────────────┘     │   │ photo           │
                        │   │ category_id (FK)│
         │              │   └─────────────────┘
         │ 1:N          │           │
         │              │           │ 1:N
         ▼              │           ▼
┌─────────────────┐     │   ┌─────────────────┐
│     orders      │     │   │   order_items   │
├─────────────────┤     │   ├─────────────────┤
│ uuid (PK)       │     │   │ id (PK)         │
│ user_id (FK)    │     └───│ product_id (FK) │
│ customer_name   │         │ order_id (FK)   │
│ customer_phone  │         │ qty             │
│ customer_address│         └─────────────────┘
│ delivery_type   │                 ▲
│ status          │                 │
│ total_amount    │                 │ 1:N
│ created_at      │                 │
└─────────────────┘                 │
                  1:N               │
                            ┌─────────────────┐
                            │     orders      │
                            └─────────────────┘
```
