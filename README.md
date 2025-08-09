# FSTR API — submitData (FastAPI + PostgreSQL)

REST API для приёма данных о перевалах (координаты, высота, название, фото, данные пользователя).
Ключевой метод: `POST /submitData`.

## Стек
- Python 3.11+
- FastAPI 0.115
- SQLAlchemy 2.0
- PostgreSQL 14+
- psycopg2-binary
- Pydantic 1.10 + email-validator

## Схема БД
Файл **00_schema.sql** лежит в репозитории и создаёт все объекты:
- `users`, `coords`, `levels`, `pereval`, `images`
- тип enum `moderation_status` = `new|pending|accepted|rejected`
- `pereval.status` (DEFAULT `new`) + индекс
- индексы по FK
- триггер `updated_at` для `pereval`

### Накатить схему
```bash
createdb fstr
psql -d fstr -f 00_schema.sql
