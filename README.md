# `Foodgram` - сайт 'Продуктовый помощник'

![foodgram workflow](https://github.com/ilgiz-n/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

Доcтуп в админку http://foodgram.viewdns.net/admin/:
логин: `admin`
пароль: `cho1ah5No`

#### О проекте:
 Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

 Проект доступен по адресу:
 http://foodgram.viewdns.net/recipes

 
#### Технологии:
- Python
- Django
- Django REST Framework
- PostgreSQL
- Nginx
- Gunicorn
- Docker

#### Как запустить проект:

1. Клонировать репозиторий:

```
https://github.com/ilgiz-n/foodgram-project-react.git
```

2. Перейти в папку с проектом

```
cd foodgram-project-react
```

3. Установить Docker и Docker Compose (на Linux):

```
sudo apt install docker-ce docker-compose -y
```

4. Создайте файл окружения .env в папке infra заполнив его по следующему шаблону

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres (здесь ваш пароль)
DB_HOST=db
DB_PORT=5432
```

5. Запустите контейнеры:

```
docker-compose up -d
```

6. Выполните миграции, заполните базу данных ингридиентами выполнив последовательно следующие команды:

```
sudo docker-compose exec backend python manage.py makemigrations
```
```
sudo docker-compose exec backend python manage.py migrate
```
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
```
sudo docker-compose exec backend python manage.py loadingredients
```

7. Для доступа в админку создайте суперпользователя. 

```
sudo docker-compose exec backend python manage.py createsuperuser
```
Админка будет доступна по адресу: http://<ваш домен или ip>/admin/

8. API проекта доступно по адресу: 
http://foodgram.viewdns.net/api/


Разработка backend части проекта: [Ильгиз Нигматуллин](https://github.com/ilgiz-n)
