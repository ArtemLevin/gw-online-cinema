
# Online Cinema

**Сервисы:**
- **gateway** — Nginx reverse-proxy
- **auth_service** — аутентификация/авторизация (FastAPI + PostgreSQL + Redis + JWT)
- **content_api** — фильмы/жанры/персоны (FastAPI + Elasticsearch + Redis)
- **ugc_service** — пользовательские события/рейтинги (FastAPI + ClickHouse HTTP)
- **admin_panel** — контент-админка (Django + PostgreSQL)

## Содержание
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [Структура репозитория](#структура-репозитория)
- [Проверка работоспособности](#проверка-работоспособности)
- [Эндпоинты и примеры](#эндпоинты-и-примеры)
  - [Auth Service](#auth-service)
  - [Content API](#content-api)
  - [UGC Service](#ugc-service)
  - [Admin Panel](#admin-panel)
- [Остановка/пересборка/логи](#остановкапересборкалоги)
- [FAQ и устранение неполадок](#faq-и-устранение-неполадок)
- [Дальнейшее развитие](#дальнейшее-развитие)

---

## Требования

- Docker 24+ и **Docker Compose v2** (`docker compose ...`)
- Для Windows: WSL2
- ~4 ГБ RAM для контейнеров

---

## Быстрый старт

1. Склонируйте/распакуйте репозиторий и перейдите в его корень.

2. Создайте `.env`:
   ```bash
   cp .env.example .env
   ```
   При необходимости измените значения (секцию с переменными см. ниже).

3. **(Важно)** Проверьте конфиг gateway: он должен **не обрезать** префиксы путей `/api/auth`, `/api/content`, `/api/ugc`.  
   В файле `gateway/nginx.conf` у `proxy_pass` для этих локаций **не должно быть завершающего слэша**:
   ```nginx
   # должно быть ТАК (без завершающего /):
   location /api/auth/    { proxy_pass http://auth-service:8001; }
   location /api/content/ { proxy_pass http://content-api:8002; }
   location /api/ugc/     { proxy_pass http://ugc-service:8003; }

   # если у вас стоит слэш в конце (...:8001/), Nginx отрежет префикс и API получит 404.
   ```

4. Запустите всё:
   ```bash
   docker compose up -d --build
   ```

5. Подождите ~30–90 сек., пока поднимутся БД/кэши/поисковый движок.

---

## Переменные окружения

Файл `.env.example` содержит разумные дефолты. Ключевые параметры:

```ini
# Postgres
POSTGRES_USER=cinema
POSTGRES_PASSWORD=cinema
POSTGRES_DB_AUTH=auth_db
POSTGRES_DB_ADMIN=admin_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Elasticsearch
ELASTIC_HOST=elasticsearch
ELASTIC_PORT=9200

# ClickHouse (HTTP)
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_HTTP_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# JWT
JWT_SECRET=supersecretjwt
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRES_MIN=30
REFRESH_TOKEN_EXPIRES_MIN=43200

# Django Admin
DJANGO_SECRET_KEY=django-secret-key
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpass

# Gateway
SERVER_NAME=localhost
```
---

## Структура репозитория

```
.
├─ gateway/
│  └─ nginx.conf
├─ services/
│  ├─ auth_service/           # FastAPI, SQLAlchemy, JWT
│  ├─ content_api/            # FastAPI, ES, Redis
│  ├─ ugc_service/            # FastAPI, ClickHouse HTTP
│  └─ admin_panel/            # Django, PostgreSQL
├─ docker-compose.yml
├─ .env.example
├─ Makefile                   # удобные шорткаты
└─ README.md
```

---

## Проверка работоспособности

После `docker compose up -d --build`:

- Gateway: http://localhost/health → `{"status":"OK"}`
- Auth:    http://localhost/api/auth/health
- Content: http://localhost/api/content/health
- UGC:     http://localhost/api/ugc/health
- Admin:   http://localhost/admin/

Swagger-доки сервисов:
- Auth:    http://localhost/api/auth/openapi
- Content: http://localhost/api/content/openapi
- UGC:     http://localhost/api/ugc/openapi

---

## Эндпоинты и примеры

### Auth Service

- **Регистрация**
  ```http
  POST http://localhost/api/auth/register
  Content-Type: application/json

  {
    "email": "user@example.com",
    "password": "strong_password"
  }
  ```
  **200/201**:
  ```json
  { "id": 1, "email": "user@example.com" }
  ```

- **Логин**
  ```http
  POST http://localhost/api/auth/login
  Content-Type: application/json

  {
    "email": "user@example.com",
    "password": "strong_password"
  }
  ```
  **200**:
  ```json
  {
    "access": "<JWT_ACCESS_TOKEN>",
    "refresh": "<JWT_REFRESH_TOKEN>"
  }
  ```

- **Текущий пользователь (`/me`)**
  ```http
  GET http://localhost/api/auth/me
  Authorization: Bearer <JWT_ACCESS_TOKEN>
  ```
  **200**:
  ```json
  { "id": 1, "email": "user@example.com" }
  ```

### Content API

- **Список фильмов**
  ```http
  GET http://localhost/api/content/films
  ```
  **200**:
  ```json
  [
    { "id": "uuid", "title": "Movie", "description": "..." }
  ]
  ```

- **Фильм по UUID**
  ```http
  GET http://localhost/api/content/films/<film_uuid>
  ```

Аналогично:
- `GET /api/content/genres` и `GET /api/content/genres/<uuid>`
- `GET /api/content/persons` и `GET /api/content/persons/<uuid>`

> Примечание: при чистом старте индексов в Elasticsearch может не быть — сервис вернёт пустые списки.

### UGC Service

- **Отправка события**
  ```http
  POST http://localhost/api/ugc/event
  Content-Type: application/json

  {
    "user_id": "1",
    "movie_id": "uuid",
    "event_type": "view",
    "payload": {"seconds": 120}
  }
  ```
  **200**:
  ```json
  { "ok": true }
  ```

- **Последние события**
  ```http
  GET http://localhost/api/ugc/events?limit=10
  ```
  **200**:
  ```json
  {
    "items": [
      {
        "user_id": "1",
        "movie_id": "uuid",
        "event_type": "view",
        "timestamp": "2025-09-06 12:34:56",
        "payload": "{\"seconds\": 120}"
      }
    ],
    "limit": 10
  }
  ```

### Admin Panel

- Откройте http://localhost/admin/
- Логин/пароль — из `.env` (`DJANGO_SUPERUSER_USERNAME`/`DJANGO_SUPERUSER_PASSWORD`)

---

## Остановка/пересборка/логи

Через `Makefile`:
```bash
make up           # билд и запуск всех сервисов
make down         # остановка и удаление томов
make logs         # потоковые логи всех сервисов
```

Или напрямую:
```bash
docker compose up -d --build
docker compose down -v
docker compose logs -f gateway
```

---

## FAQ и устранение неполадок

**API отдаёт 404 через gateway, но работает внутри сервиса**  
Проверьте `gateway/nginx.conf`. Для локаций `/api/auth/`, `/api/content/`, `/api/ugc/` у `proxy_pass` **не должно** быть завершающего `/`. Должно быть:
```nginx
proxy_pass http://auth-service:8001;
proxy_pass http://content-api:8002;
proxy_pass http://ugc-service:8003;
```
После правки:
```bash
docker compose restart gateway
```

**Elasticsearch не поднимается / падает по памяти**  
Увеличьте доступную память Docker, либо уменьшите JVM-heap через `ES_JAVA_OPTS` в `docker-compose.yml` (уже установлено `-Xms512m -Xmx512m`). Подождите 30–60 сек. и повторите запрос.

**ClickHouse отвечает с задержкой на самом старте**  
`ugc_service` при старте создаёт таблицу; если сразу после запуска POST возвращает 500 — подождите немного и повторите запрос.

**Порты заняты**  
Закройте процессы, уже слушающие `80/5432/6379/9200/8123`, или измените порт-маппинги.

**Хочу видеть Swagger**  
Откройте:
- Auth:    `/api/auth/openapi`
- Content: `/api/content/openapi`
- UGC:     `/api/ugc/openapi`

---

