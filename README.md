Запуск бекенда локально:
1. Нужен python 3.10.11
2. В директории backend созадть .env файл и прописать переменные окружения:
POSTGRES_DB=имя базы
POSTGRES_USER=юзернейм
POSTGRES_PASSWORD=пароль
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
3.
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requrements.txt
python manage.py migrate
python manage.py runserver
```
4. Доступно по адресу 127.0.0.1:8000

Запуск бекенда через docker compose:
1. Установить docker
2. 
```
cd backend
docker-compose up --build
```
3. Доступно по адресу 127.0.0.1:8000, фронтенд по адресу 127.0.0.1:3000
4. Документация по адресу 127.0.0.1:8000/redoc или swagger