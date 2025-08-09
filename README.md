# FSTR API — submitData (FastAPI + PostgreSQL)

REST API для приёма, редактирования и получения данных о перевалах ФСТР.

## Что реализовано
- PostgreSQL-схема: тип статуса модерации `new | pending | accepted | rejected`, таблицы `users`, `coords`, `levels`, `pereval`, `images`, индексы по FK, триггер `updated_at`.
- `POST /submitData` — добавление объекта (включая фото в base64).
- `GET /submitData/{id}` — получение объекта со статусом модерации.
- `PATCH /submitData/{id}` — редактирование **только при `status=new`**; запрещено менять ФИО, email и телефон.
- `GET /submitData/?user__email=<email>` — список всех объектов пользователя со статусами.
- Подключение к БД через переменные окружения `FSTR_DB_*`.
- Swagger UI: `/docs`.

## Схема БД
Файл `00_schema.sql` создаёт тип `moderation_status`, таблицы `users`, `coords`, `levels`, `pereval`, `images`, индексы и триггер `updated_at`.

### Быстрый старт БД (локально без Docker)
```bash
createdb fstr
psql -d fstr -f 00_schema.sql
Установка и запуск (локально)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

# Переменные окружения (пример)
export FSTR_DB_HOST=localhost
export FSTR_DB_PORT=5432
export FSTR_DB_LOGIN=kira
export FSTR_DB_PASS=passwd123
export FSTR_DB_NAME=fstr

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Примеры вызовов

POST /submitData
curl -X POST http://localhost:8000/submitData \
 -H "Content-Type: application/json" \
 -d '{
  "beauty_title": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {"email": "qwerty@mail.ru", "fam": "Пупкин", "name": "Василий", "otc": "Иванович", "phone": "+7 555 55 55"},
  "coords": {"latitude": "45.3842", "longitude": "7.1525", "height": "1200"},
  "level": {"winter": "", "summer": "1А", "autumn": "1А", "spring": ""},
  "images": [
    {"data":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ek9nYQAAAAASUVORK5CYII=","title":"Седловина"},
    {"data":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ek9nYQAAAAASUVORK5CYII=","title":"Подъём"}
  ]
}'

Успех:
{"status":200,"message":null,"id":1}

GET /submitData/{id}
curl http://localhost:8000/submitData/1

PATCH /submitData/{id}
(разрешено только при status=new; ФИО/email/телефон должны совпадать с сохранёнными)
curl -X PATCH http://localhost:8000/submitData/1 \
 -H "Content-Type: application/json" \
 -d '{
  "beauty_title": "пер.",
  "title": "Пхия (апдейт)",
  "other_titles": "Триев",
  "connect": "связь",
  "add_time": "2021-09-22 13:18:13",
  "user": {"email":"qwerty@mail.ru","fam":"Пупкин","name":"Василий","otc":"Иванович","phone":"+7 555 55 55"},
  "coords": {"latitude":"45.38","longitude":"7.15","height":"1300"},
  "level": {"winter":"","summer":"1А","autumn":"1А","spring":""},
  "images": [{"data":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ek9nYQAAAAASUVORK5CYII=","title":"Новая"}]
 }'

Ответ:
{"state":1,"message":null}

GET /submitData/?user__email=<email>
curl "http://localhost:8000/submitData/?user__email=qwerty@mail.ru"

Swagger / OpenAPI

После запуска:
http://localhost:8000/docs

Тесты
# в одном окне — сервер
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# в другом — тесты
pytest -q

Запуск в Docker
docker compose up -d --build
# API: http://localhost:8000
# БД с хоста: psql -h localhost -p 5433 -U <user> -d <db>
Переменные окружения (Docker)

Создайте .env рядом с docker-compose.yml (или используйте .env.example):

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