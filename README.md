# FSTR API — submitData (FastAPI + PostgreSQL)

REST API для приёма, редактирования и получения данных о перевалах ФСТР.

## Возможности
- **База данных PostgreSQL**:
  - Тип статуса модерации: `new | pending | accepted | rejected`.
  - Таблицы: `users`, `coords`, `levels`, `pereval`, `images`.
  - Индексы по FK и триггер `updated_at`.
- **Эндпоинты**:
  - `POST /submitData` — добавление объекта (включая фото в Base64).
  - `GET /submitData/{id}` — получение объекта со статусом модерации.
  - `PATCH /submitData/{id}` — редактирование **только при `status=new`**; запрещено менять ФИО, email и телефон.
  - `GET /submitData/?user__email=<email>` — список всех объектов пользователя со статусами.
- **Конфигурация**:
  - Подключение к БД через переменные окружения `FSTR_DB_*` или `DATABASE_URL`.
- Swagger UI: `/docs`.

---

## Схема БД
Файл [`00_schema.sql`](./00_schema.sql) создаёт тип `moderation_status`, все таблицы, индексы и триггер `updated_at`.

---

## Запуск локально

### 1. Создать и заполнить БД
```bash
createdb fstr
psql -d fstr -f 00_schema.sql

2. Установить зависимости
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

3. Переменные окружения (пример)
export FSTR_DB_HOST=localhost
export FSTR_DB_PORT=5432
export FSTR_LOGIN=kira
export FSTR_PASS=passwd123
export FSTR_DB_NAME=fstr

4. Запустить приложение
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Документация API

Swagger UI:
Локально: http://localhost:8000/docs
Render: https://fstr-api.onrender.com/docs

Примеры запросов

POST /submitData
curl -X POST http://localhost:8000/submitData \
 -H "Content-Type: application/json" \
 -d '{
  "beauty_title": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {"latitude": "45.3842", "longitude": "7.1525", "height": "1200"},
  "level": {"winter": "", "summer": "1А", "autumn": "1А", "spring": ""},
  "images": [
    {"data":"<base64>","title":"Седловина"},
    {"data":"<base64>","title":"Подъём"}
  ]
 }'

Успех:
{"status":200,"message":null,"id":1}

GET /submitData/{id}
curl http://localhost:8000/submitData/1

PATCH /submitData/{id}
curl -X PATCH http://localhost:8000/submitData/1 \
 -H "Content-Type: application/json" \
 -d '{
  "beauty_title": "пер.",
  "title": "Пхия (апдейт)",
  "other_titles": "Триев",
  "connect": "связь",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email":"qwerty@mail.ru",
    "fam":"Пупкин",
    "name":"Василий",
    "otc":"Иванович",
    "phone":"+7 555 55 55"
  },
  "coords": {"latitude":"45.38","longitude":"7.15","height":"1300"},
  "level": {"winter":"","summer":"1А","autumn":"1А","spring":""},
  "images": [{"data":"<base64>","title":"Новая"}]
 }'
Разрешено только при status=new; ФИО/email/телефон должны совпадать с сохранёнными.

GET /submitData/?user__email=<email>
curl "http://localhost:8000/submitData/?user__email=qwerty@mail.ru"

Тесты
# в одном окне — сервер
uvicorn app.main:app --reload
# в другом — тесты
pytest -q

Запуск в Docker
docker compose up -d --build
# API: http://localhost:8000
# Подключение к БД с хоста:
psql -h localhost -p 5433 -U <user> -d <db>

Переменные окружения для Docker
.env (или .env.example):
POSTGRES_USER=fstr_user
POSTGRES_PASSWORD=Strong_Pass_123
POSTGRES_DB=fstr
FSTR_DB_HOST=db
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=fstr_user
FSTR_DB_PASS=Strong_Pass_123
FSTR_DB_NAME=fstr

Структура репозитория
fstr_api/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ repository.py
│  └─ main.py
├─ tests/
│  └─ test_api.py
├─ 00_schema.sql
├─ requirements.txt
├─ docker-compose.yml
├─ Dockerfile
├─ .env.example
├─ .gitignore
└─ README.md