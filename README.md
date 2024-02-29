# Сервис базы данных
### Описание приложения
Приложение Sheres Report служит для отслеживанием состояния счета и каждой акции отдельно. Планируемый функционал приложения:
 - отслеживание текущей цены и цены покупки актива
 - отслеживание изменение цены
 - информирование о необходимости балансировки
 - создание графиков цены активов
 - предложение путей балансировки портфеля
 - формирование отчета о состоянии портфеля за период 
 - отслежевание операций по счету

### Развертывание приложения
#### 1. Создание файла окружения 
Создайте файл .env_prod в каталоге /restapi `touch /restapi/.env_prod` \
Файл должен иметь следующую структуру: 
```
DB_HOST=localhost
DB_NAME=db_name
DB_USER=postgres
DB_PASS=db_password

POSTGRES_DB=db_name
POSTGRES_USER=postgres
POSTGRES_PASSWORD=db_password

DB_HOST_TEST=localhost
DB_PORT_TEST=6000
DB_NAME_TEST=postgres
DB_USER_TEST=postgres
DB_PASS_TEST=postgres

SECRET_AUTH= Secret

SMTP_SERVER = smtp.gmail.com
EMAIL = your_email@mail.com
PASSWORD = email_password
```
#### 2. Сборка Docker файла
Из каталога /restapi выполните следующие команды:
```
docker compose build .
docker compose up -d
``` 

Если все прошло успешно то при вызове команды 
`docker ps` вы увидите следующий вывод:
```
CONTAINER ID   IMAGE         COMMAND                  CREATED       STATUS       PORTS                                       NAMES
76588ea96981   restapi-app   "/app/docker/app.sh"     11 days ago   Up 3 hours   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   sheres_report_app
71447ce916e0   postgres:16   "docker-entrypoint.s…"   11 days ago   Up 3 hours   5432/tcp, 8227/tcp                          db
```
На этом развертывание закончено.

### Зависимости:
 - Fastapi
 - SQLAlchemy
 - Alembic
 - Pydantic
 - Gunicorn