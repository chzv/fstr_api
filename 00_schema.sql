-- 00_schema.sql

-- ====== CREATE TYPE (безопасно для повторных запусков) ======
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'moderation_status') THEN
    CREATE TYPE moderation_status AS ENUM ('new', 'pending', 'accepted', 'rejected');
  END IF;
END$$;

-- Нормализация email для индекса (обрезка пробелов + lower)
CREATE OR REPLACE FUNCTION trim_lower_email(txt text) RETURNS text
LANGUAGE sql IMMUTABLE AS $$ SELECT lower(btrim($1)) $$;

-- ====== USERS ======
CREATE TABLE IF NOT EXISTS public.users (
    id         BIGSERIAL PRIMARY KEY,
    full_name  TEXT        NOT NULL,
    email      TEXT        NOT NULL,
    phone      TEXT        NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique
  ON public.users (trim_lower_email(email));

-- ====== COORDS ======
CREATE TABLE IF NOT EXISTS public.coords (
    id         BIGSERIAL PRIMARY KEY,
    latitude   NUMERIC(9,6)  NOT NULL,
    longitude  NUMERIC(9,6)  NOT NULL,
    height     INTEGER       NOT NULL,
    CONSTRAINT coords_lat_lon_chk
      CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
);

-- ====== LEVELS ======
CREATE TABLE IF NOT EXISTS public.levels (
    id       BIGSERIAL PRIMARY KEY,
    winter   TEXT NOT NULL DEFAULT '',
    summer   TEXT NOT NULL DEFAULT '',
    autumn   TEXT NOT NULL DEFAULT '',
    spring   TEXT NOT NULL DEFAULT ''
);

-- ====== PEREVAL ======
CREATE TABLE IF NOT EXISTS public.pereval (
    id             BIGSERIAL PRIMARY KEY,
    beauty_title   TEXT        NOT NULL,
    title          TEXT        NOT NULL,
    other_titles   TEXT        NOT NULL DEFAULT '',
    connect        TEXT        NOT NULL DEFAULT '',
    add_time       TIMESTAMPTZ NOT NULL,
    user_id        BIGINT      NOT NULL REFERENCES public.users(id)  ON DELETE RESTRICT,
    coords_id      BIGINT      NOT NULL REFERENCES public.coords(id) ON DELETE RESTRICT,
    levels_id      BIGINT      NOT NULL REFERENCES public.levels(id) ON DELETE RESTRICT,
    status         moderation_status NOT NULL DEFAULT 'new',
    moderator_note TEXT        NOT NULL DEFAULT '',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pereval_status    ON public.pereval(status);
CREATE INDEX IF NOT EXISTS idx_pereval_user_id   ON public.pereval(user_id);
CREATE INDEX IF NOT EXISTS idx_pereval_coords_id ON public.pereval(coords_id);
CREATE INDEX IF NOT EXISTS idx_pereval_levels_id ON public.pereval(levels_id);

-- Триггер на автообновление updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_pereval_updated_at ON public.pereval;
CREATE TRIGGER trg_pereval_updated_at
BEFORE UPDATE ON public.pereval
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ====== IMAGES ======
CREATE TABLE IF NOT EXISTS public.images (
    id         BIGSERIAL PRIMARY KEY,
    pereval_id BIGINT   NOT NULL REFERENCES public.pereval(id) ON DELETE CASCADE,
    title      TEXT     NOT NULL,
    data       BYTEA    NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_images_pereval_id ON public.images(pereval_id);
