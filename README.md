[![workflow yamdb_final](https://github.com/Nemets87/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)](https://github.com/rusnik49/yamdb_final/actions/workflows/yamdb_workflow.yml)
-
![example workflow](https://myoctocat.com/assets/images/base-octocat.svg)
-

# Проект **foodgram-project-react** 

#### ****
[![docker](https://img.shields.io/docker/automated/rusnik49/infra_sp2)
[![django](https://img.shields.io/badge/Django-2.2-green)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)

# Как запустить проект чeрез Docker:

Должен быть уставлен Docker https://www.docker.com

Клонируем репозиторий и переходим в него:

```
git@github.com:rusnik49/foodgram-project-react.git

```
В директории infra необходимо создать файл .env:
```
cd infra

```
в папке infra создаем файл .env с следующим содержимом:
touch .env

```
DB_ENGINE=django.db.backends.postgresql = указываем, что работаем с postgresql
DB_NAME=postgres = имя базы данных
POSTGRES_USER=postgres = логин для подключения к базе данных
POSTGRES_PASSWORD=postgres = пароль для подключения к БД (установите свой)
DB_HOST=db = название сервиса (контейнера)
DB_PORT=5432 = порт для подключения к БД 
```
- проверяем requirements.txt (должен содержать необходимый минимум,важно наличие самих пакетов, а не версии)

```
asgiref==3.6.0
certifi==2022.12.7
cffi==1.15.1
charset-normalizer==3.1.0
class-registry==2.1.2
coreapi==2.3.3
coreschema==0.0.4
cryptography==39.0.2
defusedxml==0.7.1
Django==3.2.18
django-cors-headers==3.14.0
django-extra-fields==3.0.2
django-filter==22.1
django-templated-mail==1.1.1
djangorestframework==3.14.0
djangorestframework-simplejwt==4.8.0
djoser==2.1.0
filters==1.3.2
flake8==5.0.4
idna==3.4
importlib-metadata==1.7.0
isort==5.11.5
itypes==1.2.0
Jinja2==3.1.2
MarkupSafe==2.1.2
mccabe==0.7.0
oauthlib==3.2.2
Pillow==9.4.0
psycopg2-binary==2.9.5
pycodestyle==2.9.1
pycparser==2.21
pyflakes==2.5.0
PyJWT==2.6.0
python-dateutil==2.8.2
python-dotenv==0.21.1
python3-openid==3.2.0
pytz==2022.7.1
regex==2022.10.31
requests==2.28.2
requests-oauthlib==1.3.1
six==1.16.0
social-auth-app-django==4.0.0
social-auth-core==4.4.0
sqlparse==0.4.3
typing-extensions==4.5.0
uritemplate==4.1.1
urllib3==1.26.15
zipp==3.15.0

```
пока мы проверяем все локально !
frontend мы к каждому url добавляем this._url + и в самом конце 'http://localhost:8000' 
- при отправке на сервер это все нужно будет удалить
и вернуть как было !
пока все локально собираем 
```
sudo su root дает возможность избежать слово sudo,но под рутом сидеть опасно 
- создаем новый ВМ с ubuntu 20.04 (НЕ 22.04!!!!) 
- не заходим на сервер == все локально


- ставим докер и композ
sudo apt update
sudo apt install docker.io
sudo apt install docker-compose
sudo systemctl start docker

- зайти в свой проект на компе, проверить docker-compose.yml
```
В директории infra/, в файле nginx.conf измените адрес(ip/домен), необходимо указать адрес вашего сервера.

Запустите docker compose
```
docker-compose up -d --build
```

Примените миграции
```
docker-compose exec backend python manage.py migrate
(при необходимости наполнения БД можно загрузить базу с помощью:
docker-compose exec backend python manage.py zen)
что такое zen? - это не ручками забить 2000 ингридиетов,
а испытать Дзен от лени и удобства 
```

Создайте суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```

Далее соберите статику
```
docker-compose exec backend python manage.py collectstatic --noinput