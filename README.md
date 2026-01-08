# Foodgram

**Foodgram** — веб-приложение для публикации и обмена кулинарными рецептами.  
Пользователи могут добавлять рецепты, подписываться на авторов, формировать список покупок и сохранять избранное.

## Технологии
- Python 3.9
- Django + Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- Nginx
- Gunicorn

## Локальный запуск проекта
1. Клонируйте репозиторий:
   ```bash
   git clone <ссылка на репозиторий>
   cd foodgram/infra
2. Создайте файл .env в корне проекта и укажите переменные окружения.

3. Перейдите в папку infra/ соберите и запустите контейнеры:

docker compose up --build

Доступы:

Приложение: http://localhost

API-документация: http://localhost/api/docs/


ip: http://89.169.167.79/
Домен: http://foodgram.serveirc.com/
Почта админа: admin.admin@gmail.com
Логин: admin
Пароль: admin


Автор

Dima Shibaev

## Изменения под ТЗ (модуль аутентификации и контроля доступа)

В проект добавлены два модуля:

### 1) Аутентификация (JWT + серверные сессии)
- Заголовок: `Authorization: Bearer <token>`
- Эндпоинты:
  - `POST /api/auth/register/` — регистрация, возвращает токен
    - обязательные поля: email, password, password2, first_name, middle_name, last_name
  - `POST /api/auth/login/` — вход, возвращает токен
  - `POST /api/auth/logout/` — выход (отзыв текущей сессии)
  - `GET /api/auth/me/` — профиль (id, email, username, first_name, middle_name, last_name)
  - `PATCH /api/auth/me/` — обновление профиля
  - `DELETE /api/auth/me/` — мягкое удаление (is_active=False) + отзыв всех сессий

Переменные окружения:
- `JWT_SECRET_KEY` (если не задано, используется `SECRET_KEY`)
- `JWT_TTL_SECONDS` (по умолчанию 7 дней)

### 2) Контроль доступа (RBAC + правила по бизнес-элементам)
Таблицы:
- `Role`
- `BusinessElement`
- `UserRole`
- `AccessRoleRule` (права: read/read_all/create/update/update_all/delete/delete_all)

Администрирование (нужна роль `admin` или superuser):
- `GET/POST/PUT/PATCH/DELETE /api/access/roles/`
- `... /api/access/elements/`
- `... /api/access/user-roles/`
- `... /api/access/rules/`

Мок-ресурсы для демонстрации правил (упрощённые бизнес-объекты):

В рамках демонстрации добавлена таблица `ProtectedObject` (id, element_code, owner, payload). Это не обязательное требование ТЗ, но упрощает проверку owner-based правил на реальных данных.
- `GET /api/mock/` — список доступных мок-элементов
- `GET/POST /api/mock/<element>/`
- `GET/PUT/PATCH/DELETE /api/mock/<element>/<id>/`

Инициализация базовых ролей/элементов/прав выполняется командой:
- `python manage.py init_access_data`
(в Dockerfile команда запускается автоматически при старте backend).

