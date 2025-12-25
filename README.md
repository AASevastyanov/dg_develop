# Tatarlang - Инструкция по запуску

Полная инструкция по запуску приложения Tatarlang с использованием Docker и Docker Compose.

## Содержание

1. [Установка Docker](#установка-docker)
2. [Быстрый старт](#быстрый-старт)
3. [Подробная инструкция](#подробная-инструкция)
4. [Проверка работы](#проверка-работы)
5. [Управление приложением](#управление-приложением)
6. [RabbitMQ Producer/Consumer](#rabbitmq-producerconsumer)
7. [Celery задачи и API интеграции](#celery-задачи-и-api-интеграции)
8. [Troubleshooting](#troubleshooting)
9. [Развертывание в Kubernetes с Helm](#развертывание-в-kubernetes-с-helm)
10. [Настройка Vault для управления секретами](#настройка-vault-для-управления-секретами)
11. [Интеграция приложения с Vault](#интеграция-приложения-с-vault)

---

## Установка Docker

### macOS

#### Вариант 1: Docker Desktop (рекомендуется)

1. Скачайте Docker Desktop с официального сайта: https://www.docker.com/products/docker-desktop/
2. Установите приложение, перетащив его в папку Applications
3. Запустите Docker Desktop из Applications
4. Дождитесь полного запуска (иконка Docker в строке меню перестанет мигать)

#### Вариант 2: Через Homebrew

```bash
brew install --cask docker
```

После установки запустите Docker Desktop из Applications.

### Linux (Ubuntu/Debian)

```bash
# Обновление списка пакетов
sudo apt-get update

# Установка необходимых пакетов
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавление официального GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Настройка репозитория
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker Engine и Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавление текущего пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Перелогиньтесь или выполните:
newgrp docker
```

### Linux (Fedora/RHEL/CentOS)

```bash
# Установка необходимых пакетов
sudo dnf install -y dnf-plugins-core

# Добавление репозитория Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Установка Docker Engine и Docker Compose
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запуск Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### Windows

1. Скачайте Docker Desktop с официального сайта: https://www.docker.com/products/docker-desktop/
2. Запустите установщик `Docker Desktop Installer.exe`
3. Следуйте инструкциям установщика
4. После установки перезагрузите компьютер
5. Запустите Docker Desktop из меню Пуск
6. Дождитесь полного запуска (иконка Docker в системном трее)

**Требования:**
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 15063 или выше)
- Windows 11 64-bit: Home или Pro версия 21H2 или выше
- WSL 2 включен и обновлен

---

## Быстрый старт

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd dg_develop
```

### Шаг 2: Создание файла .env

Создайте файл `.env` в корне проекта:

```bash
# Для Linux/macOS
cat > .env << EOF
POSTGRES_DB=tatarlang
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
EOF
```

```powershell
# Для Windows (PowerShell)
@"
POSTGRES_DB=tatarlang
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
"@ | Out-File -FilePath .env -Encoding utf8
```

### Шаг 3: Запуск приложения

```bash
docker-compose up --build
```

Или в фоновом режиме:

```bash
docker-compose up -d --build
```

### Шаг 4: Проверка работы

Откройте в браузере:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/swagger
- **RabbitMQ Management**: http://localhost:15672 (логин: `admin`, пароль: `admin`)
- **Flower (Celery)**: http://localhost:5555

---

## Подробная инструкция

### Шаг 1: Проверка установки Docker

Убедитесь, что Docker установлен и работает:

```bash
docker --version
docker-compose --version
```

Ожидаемый вывод:
```
Docker version 24.x.x, build ...
Docker Compose version v2.x.x
```

Проверьте, что Docker запущен:

```bash
docker ps
```

Если команда выполняется без ошибок, Docker работает корректно.

### Шаг 2: Подготовка проекта

1. **Перейдите в директорию проекта:**

```bash
cd /path/to/dg_develop
```

2. **Создайте файл `.env`** (если его еще нет):

**Linux/macOS:**
```bash
cat > .env << 'EOF'
POSTGRES_DB=tatarlang
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
EOF
```

**Windows (PowerShell):**
```powershell
@"
POSTGRES_DB=tatarlang
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
"@ | Out-File -FilePath .env -Encoding utf8
```

**Windows (CMD):**
```cmd
echo POSTGRES_DB=tatarlang > .env
echo POSTGRES_USER=postgres >> .env
echo POSTGRES_PASSWORD=postgres >> .env
echo RABBITMQ_USER=admin >> .env
echo RABBITMQ_PASS=admin >> .env
```

### Шаг 3: Запуск приложения

#### Первый запуск (с пересборкой образов)

```bash
docker-compose up --build
```

Эта команда:
- Соберет Docker-образы для backend и frontend
- Создаст необходимые volumes
- Запустит все сервисы

#### Запуск в фоновом режиме

```bash
docker-compose up -d --build
```

Флаг `-d` запускает контейнеры в фоновом режиме (detached mode).

#### Последующие запуски (без пересборки)

```bash
docker-compose up
```

или

```bash
docker-compose up -d
```

### Шаг 4: Выполнение миграций базы данных

После первого запуска выполните миграции:

```bash
docker-compose exec backend python manage.py migrate
```

### Шаг 5: Создание суперпользователя (опционально)

Для доступа к админ-панели Django:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Следуйте инструкциям для создания учетной записи администратора.

---

## Проверка работы

### Проверка статуса контейнеров

```bash
docker-compose ps
```

Все сервисы должны быть в статусе `Up`:

```
NAME                COMMAND                  STATUS          PORTS
backend             "python manage.py..."     Up              0.0.0.0:8000->8000/tcp
db                  "docker-entrypoint..."    Up (healthy)    0.0.0.0:5433->5432/tcp
frontend            "docker-entrypoint..."    Up              0.0.0.0:3000->3000/tcp
rabbitmq            "docker-entrypoint..."    Up              0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
celery_worker       "celery -A..."           Up
celery_beat         "celery -A..."           Up
flower              "celery -A..."           Up              0.0.0.0:5555->5555/tcp
```

### Проверка логов

Просмотр логов всех сервисов:

```bash
docker-compose logs
```

Логи конкретного сервиса:

```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

Логи в реальном времени:

```bash
docker-compose logs -f backend
```

### Проверка доступности сервисов

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8000
3. **API Документация (Swagger)**: http://localhost:8000/swagger
4. **API Документация (ReDoc)**: http://localhost:8000/redoc
5. **RabbitMQ Management**: http://localhost:15672
   - Логин: `admin`
   - Пароль: `admin`
6. **Flower (Celery Monitoring)**: http://localhost:5555

---

## Управление приложением

### Остановка приложения

```bash
docker-compose stop
```

Останавливает контейнеры, но не удаляет их.

### Запуск остановленных контейнеров

```bash
docker-compose start
```

### Перезапуск приложения

```bash
docker-compose restart
```

Перезапуск конкретного сервиса:

```bash
docker-compose restart backend
```

### Остановка и удаление контейнеров

```bash
docker-compose down
```

### Остановка с удалением volumes (удаление данных БД)

⚠️ **Внимание**: Эта команда удалит все данные из базы данных!

```bash
docker-compose down -v
```

### Пересборка образов

Если вы изменили код и нужно пересобрать образы:

```bash
docker-compose build
```

Или для конкретного сервиса:

```bash
docker-compose build backend
```

### Выполнение команд в контейнерах

Выполнение команды в контейнере backend:

```bash
docker-compose exec backend python manage.py <command>
```

Примеры:
```bash
# Миграции
docker-compose exec backend python manage.py migrate

# Создание миграций
docker-compose exec backend python manage.py makemigrations

# Django shell
docker-compose exec backend python manage.py shell

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

Доступ к shell контейнера:

```bash
docker-compose exec backend sh
```

---

## Troubleshooting

### Проблема: Docker не запускается

**macOS/Windows:**
- Убедитесь, что Docker Desktop запущен
- Проверьте системные требования
- Перезапустите Docker Desktop

**Linux:**
```bash
# Проверка статуса Docker
sudo systemctl status docker

# Запуск Docker
sudo systemctl start docker

# Автозапуск при загрузке
sudo systemctl enable docker
```

### Проблема: Порт уже занят

Если порт 8000, 3000 или другой уже занят:

1. Найдите процесс, использующий порт:

**Linux/macOS:**
```bash
lsof -i :8000
# или
netstat -tulpn | grep 8000
```

**Windows:**
```powershell
netstat -ano | findstr :8000
```

2. Остановите процесс или измените порт в `docker-compose.yaml`

### Проблема: Ошибка подключения к базе данных

```bash
# Проверьте статус контейнера БД
docker-compose ps db

# Проверьте логи БД
docker-compose logs db

# Перезапустите БД
docker-compose restart db
```

### Проблема: Backend не запускается

```bash
# Проверьте логи
docker-compose logs backend

# Проверьте, что БД запущена
docker-compose ps db

# Выполните миграции
docker-compose exec backend python manage.py migrate
```

### Проблема: Frontend не компилируется

```bash
# Проверьте логи
docker-compose logs frontend

# Пересоберите образ frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Проблема: Контейнеры постоянно перезапускаются

```bash
# Проверьте логи всех сервисов
docker-compose logs

# Проверьте использование ресурсов
docker stats

# Увеличьте лимиты ресурсов в docker-compose.yaml или Docker Desktop
```

### Очистка системы Docker

Если возникли проблемы, можно очистить систему:

```bash
# Остановка всех контейнеров
docker-compose down

# Удаление неиспользуемых образов
docker image prune -a

# Удаление неиспользуемых volumes
docker volume prune

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

---

## Структура проекта

```
dg_develop/
├── backend/                    # Django backend приложение
│   ├── api/                    # API приложение
│   │   ├── tasks.py           # Celery задачи для API
│   │   ├── views.py           # API views (включая endpoints для задач)
│   │   └── urls.py            # URL маршруты
│   ├── events/                 # Приложение событий
│   │   └── tasks.py           # Celery задачи для событий
│   ├── tatarlang/             # Основное приложение
│   │   ├── celery.py          # Конфигурация Celery
│   │   └── settings.py        # Настройки Django
│   ├── rabbitmq_producer.py    # Producer для RabbitMQ
│   ├── rabbitmq_consumer.py    # Consumer для RabbitMQ
│   ├── celeryconfig.py        # Конфигурация Celery
│   ├── manage.py              # Django management script
│   ├── requirements.txt       # Python зависимости
│   └── Dockerfile             # Docker образ для backend
├── frontend/                   # React frontend приложение
│   ├── src/                   # Исходный код
│   ├── public/                # Статические файлы
│   └── Dockerfile             # Docker образ для frontend
├── tatarlang-chart/           # Helm chart для основного приложения
│   ├── charts/                # Subcharts
│   │   ├── postgresql/        # PostgreSQL subchart
│   │   └── rabbitmq/         # RabbitMQ subchart (использует Bitnami)
│   ├── templates/             # Kubernetes манифесты
│   │   ├── backend-deployment.yaml
│   │   ├── celery-deployment.yaml
│   │   ├── rabbitmq-secret.yaml
│   │   └── ...
│   ├── values.yaml            # Значения по умолчанию
│   └── values-vault.yaml      # Значения для Vault интеграции
├── flower-chart/              # Helm chart для Flower
│   ├── templates/             # Kubernetes манифесты для Flower
│   └── values.yaml
├── vault-chart/                # Helm chart для Vault
│   ├── scripts/               # Скрипты настройки Vault
│   │   └── vault-setup.sh    # Скрипт настройки политик и секретов
│   └── templates/
├── docker-compose.yaml        # Конфигурация Docker Compose
├── .env                       # Переменные окружения (создается вручную)
└── README.md                  # Этот файл
```

---

## Дополнительная информация

### Переменные окружения

Основные переменные в файле `.env`:

- `POSTGRES_DB` - имя базы данных PostgreSQL
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `RABBITMQ_USER` - пользователь RabbitMQ
- `RABBITMQ_PASS` - пароль RabbitMQ
- `CELERY_BROKER_URL` - URL брокера для Celery (например: `amqp://admin:admin@rabbitmq:5672//`)
- `WEATHER_API_KEY` - API ключ для OpenWeatherMap (опционально)
- `NEWS_API_KEY` - API ключ для NewsAPI (опционально)

### Полезные команды Docker

```bash
# Просмотр всех контейнеров
docker ps -a

# Просмотр всех образов
docker images

# Просмотр volumes
docker volume ls

# Просмотр сетей
docker network ls

# Использование ресурсов
docker stats
```

---

## RabbitMQ Producer/Consumer

Приложение включает Producer и Consumer для работы с RabbitMQ брокером сообщений.

### Producer

Producer отправляет сообщения в RabbitMQ exchange для выполнения задач интеграции с внешними API.

**Использование:**

```python
from backend.rabbitmq_producer import RabbitMQProducer, send_weather_task, send_news_task

# Простой способ
send_weather_task(city="Kazan", country="RU")
send_news_task(query="technology", language="en")

# Продвинутый способ
producer = RabbitMQProducer()
producer.send_api_task(
    api_alias="weather",
    task_params={"city": "Moscow", "country": "RU"},
    routing_key="weather"
)
producer.close()
```

### Consumer

Consumer обрабатывает сообщения из очередей RabbitMQ и выполняет задачи.

**Запуск через CLI:**

```bash
# Запуск consumer для очереди weather
docker-compose exec backend python rabbitmq_consumer.py weather_queue weather

# Запуск consumer для очереди news
docker-compose exec backend python rabbitmq_consumer.py news_queue news
```

**Параметры:**
- `queue_name` - имя очереди для создания/подключения
- `routing_key` - ключ маршрутизации для привязки к exchange

**Особенности:**
- Создает durable очередь
- Привязывает очередь к direct exchange
- Сохраняет результаты API запросов в JSON файлы в `/app/api_responses/`
- Поддерживает acknowledgement сообщений

### Настройка API ключей

Для работы с внешними API необходимо настроить ключи:

**Через переменные окружения:**
```bash
# В .env файле
WEATHER_API_KEY=your_openweathermap_api_key
NEWS_API_KEY=your_newsapi_key
```

**Через Vault (в Kubernetes):**
```bash
# Ключи сохраняются в vault-setup.sh
# Путь: secret/tatarlang/api/weather и secret/tatarlang/api/news
```

---

## Celery задачи и API интеграции

Приложение использует Celery для асинхронного выполнения задач, включая интеграции с внешними API.

### Доступные задачи

#### 1. Weather API Task
Получение данных о погоде через OpenWeatherMap API.

**Эндпоинт:** `POST /api/v1/tasks/weather`

**Тело запроса:**
```json
{
  "city": "Kazan",
  "country": "RU"
}
```

**Ответ:**
```json
{
  "task_id": "abc123-def456-...",
  "status": "PENDING",
  "message": "Weather task has been queued"
}
```

#### 2. News API Task
Получение новостей через NewsAPI.

**Эндпоинт:** `POST /api/v1/tasks/news`

**Тело запроса:**
```json
{
  "query": "technology",
  "language": "en"
}
```

**Ответ:**
```json
{
  "task_id": "xyz789-abc123-...",
  "status": "PENDING",
  "message": "News task has been queued"
}
```

### Проверка статуса задачи

**Эндпоинт:** `GET /api/v1/tasks/<task_id>/status`

**Пример запроса:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/tasks/abc123-def456-/status
```

**Возможные статусы:**
- `PENDING` - задача ожидает выполнения
- `PROGRESS` - задача выполняется
- `SUCCESS` - задача выполнена успешно
- `FAILURE` - задача завершилась с ошибкой

**Пример ответа (SUCCESS):**
```json
{
  "task_id": "abc123-def456-...",
  "state": "SUCCESS",
  "result": {
    "status": "success",
    "city": "Kazan",
    "country": "RU",
    "data": { ... },
    "file": "/app/api_responses/weather_Kazan_RU.json"
  }
}
```

### Мониторинг через Flower

Flower предоставляет веб-интерфейс для мониторинга Celery задач.

**Доступ:**
- Docker Compose: http://localhost:5555
- Kubernetes: http://flower.tatarlang.local (через ingress)

**Возможности:**
- Просмотр активных задач
- История выполненных задач
- Мониторинг воркеров
- Статистика производительности

### Использование через API

**Пример с curl:**

```bash
# 1. Получить токен авторизации
TOKEN=$(curl -X POST http://localhost:8000/api/v1/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access')

# 2. Запустить задачу погоды
TASK_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/tasks/weather \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"city":"Kazan","country":"RU"}')

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')

# 3. Проверить статус
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/tasks/$TASK_ID/status
```

### Результаты выполнения

Результаты API запросов сохраняются в JSON файлы:
- Weather: `/app/api_responses/weather_<city>_<country>.json`
- News: `/app/api_responses/news_<query>_<language>.json`

В Kubernetes файлы сохраняются в volume пода.

---

## Развертывание в Kubernetes с Helm

Этот раздел описывает развертывание приложения в Kubernetes кластере с использованием Helm-чартов.

### Предварительные требования

- **Kubernetes кластер** (minikube, kind, или Docker Desktop с Kubernetes)
- **Helm 3.0+**
- **kubectl** (для работы с Kubernetes)

### Установка инструментов

#### macOS

```bash
# Homebrew
brew install helm kubectl minikube
```

#### Linux (Ubuntu/Debian)

```bash
# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

#### Windows

1. Установите Helm: https://helm.sh/docs/intro/install/
2. Установите kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
3. Установите Minikube: https://minikube.sigs.k8s.io/docs/start/

### Шаг 1: Запуск Kubernetes кластера

#### Вариант A: Minikube (рекомендуется для локальной разработки)

```bash
# Запуск minikube
minikube start

# Проверка статуса
minikube status
kubectl get nodes
```

Если возникли проблемы с запуском:

```bash
# Удалить и пересоздать кластер
minikube delete
minikube start --driver=docker
```

#### Вариант B: Docker Desktop

1. Откройте Docker Desktop
2. Перейдите в Settings → Kubernetes
3. Включите "Enable Kubernetes"
4. Дождитесь запуска кластера (может занять несколько минут)

#### Вариант C: Kind

```bash
# Установка kind
brew install kind  # macOS
# или скачайте с https://kind.sigs.k8s.io/

# Создание кластера
kind create cluster

# Проверка
kubectl cluster-info
```

### Шаг 2: Проверка Helm-чарта

```bash
# Перейдите в директорию проекта
cd /path/to/dg_develop

# Проверка синтаксиса чарта
cd tatarlang-chart
helm lint .

# Генерация манифестов (без установки)
helm template tatarlang .
```

### Шаг 3: Сборка Docker-образов для Minikube

Если используете minikube, нужно собрать образы в контексте minikube:

```bash
# Настроить Docker для использования minikube
eval $(minikube docker-env)

# Собрать образы
cd backend
docker build -t tatarlang-backend:latest .

cd ../frontend
docker build -t tatarlang-frontend:latest .

# Вернуться к обычному Docker (опционально)
eval $(minikube docker-env -u)
```

**Примечание**: Если используете Docker Desktop с Kubernetes, образы можно собрать обычным способом, но нужно убедиться, что они доступны в кластере.

### Шаг 4: Установка зависимостей Helm чарта

Перед установкой необходимо обновить зависимости:

```bash
# Перейти в директорию чарта
cd tatarlang-chart

# Обновить зависимости (включая Bitnami RabbitMQ chart)
helm dependency update

# Вернуться в корень проекта
cd ..
```

### Шаг 5: Установка приложения

```bash
# Установка чарта с указанием namespace
helm install tatarlang ./tatarlang-chart \
  --namespace tatarlang \
  --create-namespace \
  --set vault.enabled=false

# Проверка установки
helm list -n tatarlang
kubectl get pods -n tatarlang
```

**Примечание:** RabbitMQ развертывается через Bitnami Helm chart. Для использования Cloud Pirates chart измените зависимость в `tatarlang-chart/Chart.yaml`.

### Шаг 6: Установка Flower (опционально)

Flower можно установить отдельным чартом:

```bash
# Установка Flower чарта
helm install flower ./flower-chart \
  --namespace tatarlang \
  --create-namespace \
  --set vault.enabled=false

# Проверка
kubectl get pods -n tatarlang | grep flower
```

### Шаг 7: Проверка работы приложения

```bash
# Проверить статус подов
kubectl get pods -n tatarlang

# Проверить сервисы
kubectl get svc -n tatarlang

# Просмотр логов
kubectl logs -n tatarlang -l tier=backend
kubectl logs -n tatarlang -l tier=frontend

# Получить доступ к приложению через port-forward
kubectl port-forward -n tatarlang svc/backend 8000:8000
kubectl port-forward -n tatarlang svc/frontend 3000:3000
```

После этого приложение будет доступно:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- RabbitMQ Management: через ingress на `rabbitmq.tatarlang.local` или через port-forward
- Flower: через ingress на `flower.tatarlang.local` или через port-forward

**Port-forward для доступа:**
```bash
# RabbitMQ Management
kubectl port-forward -n tatarlang svc/tatarlang-rabbitmq 15672:15672

# Flower
kubectl port-forward -n tatarlang svc/flower 5555:5555
```

### Шаг 8: Обновление приложения

```bash
# Обновление чарта
helm upgrade tatarlang ./tatarlang-chart -n tatarlang

# С кастомными значениями
helm upgrade tatarlang ./tatarlang-chart -n tatarlang -f my-values.yaml
```

### Шаг 9: Удаление приложения

```bash
# Удаление release
helm uninstall tatarlang -n tatarlang

# С удалением namespace
kubectl delete namespace tatarlang
```

### Troubleshooting Kubernetes/Helm

#### Проблема: Minikube не запускается (API server не стартует)

**Симптомы:**
- Ошибки типа `K8S_APISERVER_MISSING: wait 6m0s for node: wait for apiserver proc: apiserver process never appeared`
- Ошибки `connection refused` при попытке подключиться к API server

**Решение:**
```bash
# Вариант 1: Остановить и перезапустить minikube
minikube stop
minikube start

# Вариант 2: Если не помогло - удалить и пересоздать кластер
minikube delete
minikube start --driver=docker

# Вариант 3: Проверить статус Docker
docker ps  # Убедитесь, что Docker работает

# Вариант 4: Запуск с явным указанием драйвера и дополнительными ресурсами
minikube delete
minikube start --driver=docker --memory=4096 --cpus=2
```

**Проверка после запуска:**
```bash
minikube status  # Все компоненты должны быть Running
kubectl get nodes  # Узел должен быть Ready
```

#### Проблема: Поды не запускаются (ImagePullBackOff)

**Решение:**
```bash
# Для minikube - собрать образы в контексте minikube
eval $(minikube docker-env)
docker build -t tatarlang-backend:latest ./backend
docker build -t tatarlang-frontend:latest ./frontend
eval $(minikube docker-env -u)
```

#### Проблема: Backend не может подключиться к БД

**Решение:**
```bash
# Проверить, что сервис БД существует
kubectl get svc -n tatarlang | grep db

# Проверить логи backend
kubectl logs -n tatarlang -l tier=backend

# Проверить, что БД запущена
kubectl get pods -n tatarlang | grep db

# Проверить переменные окружения
kubectl exec -n tatarlang <backend-pod> -- env | grep POSTGRES
```

#### Проблема: Namespace не удаляется

**Решение:**
```bash
# Принудительное удаление
kubectl delete namespace <namespace> --force --grace-period=0
```

#### Полезные команды Kubernetes

```bash
# Просмотр всех ресурсов
kubectl get all -n tatarlang

# Просмотр логов
kubectl logs -n tatarlang <pod-name>
kubectl logs -n tatarlang -l tier=backend --tail=100

# Подключение к поду
kubectl exec -it -n tatarlang <pod-name> -- /bin/sh

# Описание ресурса
kubectl describe pod -n tatarlang <pod-name>

# Просмотр событий
kubectl get events -n tatarlang --sort-by='.lastTimestamp'

# Просмотр истории Helm release
helm history tatarlang -n tatarlang

# Откат к предыдущей версии
helm rollback tatarlang <revision-number> -n tatarlang
```

---

## Настройка Vault для управления секретами

Vault используется для безопасного хранения и управления секретами приложения (пароли БД, ключи API и т.д.).

### Предварительные требования

- Работающий Kubernetes кластер
- Helm 3.0+
- kubectl

### Шаг 1: Установка необходимых инструментов

```bash
# Установка helm-secrets плагина
helm plugin install https://github.com/jkroepke/helm-secrets --verify=false

# Установка vals (для работы с Vault)
# macOS
brew install vals

# Linux
curl -LO https://github.com/helmfile/vals/releases/latest/download/vals_linux_amd64.tar.gz
tar -xzf vals_linux_amd64.tar.gz
sudo mv vals /usr/local/bin/

# Windows
# Скачайте с https://github.com/helmfile/vals/releases
```

### Шаг 2: Развертывание Vault

```bash
# Перейдите в директорию проекта
cd /path/to/dg_develop

# Установка Vault
helm install vault ./vault-chart \
  --namespace vault \
  --create-namespace \
  --set persistence.enabled=false

# Ожидание готовности (может занять 1-2 минуты)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=vault-chart -n vault --timeout=300s

# Проверка статуса
kubectl get pods -n vault
```

### Шаг 3: Инициализация Vault

```bash
# Получить имя пода Vault
VAULT_POD=$(kubectl get pod -n vault -l app.kubernetes.io/name=vault-chart \
  --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Инициализировать Vault
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator init

# ⚠️ ВАЖНО: Сохраните выведенные ключи!
# Вам понадобятся:
# - Root Token (один)
# - Unseal Keys (минимум 3 из 5)
```

**Пример вывода:**
```
Unseal Key 1: abc123...
Unseal Key 2: def456...
Unseal Key 3: ghi789...
Unseal Key 4: jkl012...
Unseal Key 5: mno345...

Initial Root Token: s.xyz789...
```

### Шаг 4: Распечатывание Vault (Unseal)

Vault по умолчанию запечатан (sealed) для безопасности. Нужно распечатать его:

```bash
# Выполните unseal (замените KEY1, KEY2, KEY3 на реальные ключи)
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal <KEY1>
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal <KEY2>
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal <KEY3>

# Проверка статуса (должно быть Sealed: false)
kubectl exec -n vault "$VAULT_POD" -c vault -- vault status
```

### Шаг 5: Сохранение ключей

```bash
# Создать директорию для ключей
mkdir -p vault-keys

# Сохранить ключи (замените значения на реальные)
echo "<ROOT_TOKEN>" > vault-keys/root-token.txt
echo "<KEY1>" > vault-keys/unseal-key-1.txt
echo "<KEY2>" > vault-keys/unseal-key-2.txt
echo "<KEY3>" > vault-keys/unseal-key-3.txt

# ⚠️ ВАЖНО: Не коммитьте эти файлы в git! Они уже в .gitignore
```

### Шаг 6: Настройка Vault (политики, AppRole, секреты)

```bash
# Перейти в директорию скриптов
cd vault-chart/scripts

# Настроить Vault
export VAULT_ROOT_TOKEN=$(cat ../../vault-keys/root-token.txt)
./vault-setup.sh
```

Скрипт выполнит:
- Включение KV v2 secret engine
- Создание политики доступа (tatarlang-policy)
- Создание политики для API ключей (api-keys-policy)
- Включение AppRole аутентификации
- Создание AppRole (tatarlang-role) с поддержкой нескольких политик
- Сохранение секретов в Vault:
  - PostgreSQL (db)
  - RabbitMQ (rabbitmq)
  - Celery (celery)
  - API ключи (api/weather, api/news)

После выполнения скрипта будут сохранены:
- `vault-keys/role-id.txt` - Role ID для AppRole
- `vault-keys/secret-id.txt` - Secret ID для AppRole

### Шаг 7: Проверка секретов в Vault

```bash
# Получить имя пода
VAULT_POD=$(kubectl get pod -n vault -l app.kubernetes.io/name=vault-chart \
  --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Получить root token
ROOT_TOKEN=$(cat vault-keys/root-token.txt)

# Просмотр секретов
kubectl exec -n vault "$VAULT_POD" -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=$ROOT_TOKEN vault kv list secret/tatarlang"

# Просмотр конкретного секрета
kubectl exec -n vault "$VAULT_POD" -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=$ROOT_TOKEN vault kv get secret/tatarlang/db"
```

### Важные замечания

1. **Vault запечатывается при перезапуске**: После перезапуска пода Vault нужно снова выполнить unseal
2. **Автоматический unseal**: Для продакшена рекомендуется настроить автоматический unseal (AWS KMS, Azure Key Vault и т.д.)
3. **Безопасность ключей**: Никогда не коммитьте ключи Vault в git!

---

## Интеграция приложения с Vault

После настройки Vault можно интегрировать его с приложением для автоматического получения секретов.

### Шаг 1: Настройка переменных окружения для vals

```bash
# Установить переменные окружения для работы с Vault
export VAULT_ADDR=http://vault-vault-chart.vault.svc.cluster.local:8200
export VAULT_ROLE_ID=$(cat vault-keys/role-id.txt)
export VAULT_SECRET_ID=$(cat vault-keys/secret-id.txt)
```

### Шаг 2: Переустановка приложения с Vault интеграцией

```bash
# Удалить текущую установку (если есть)
helm uninstall tatarlang --namespace tatarlang

# Установить с Vault интеграцией
# Вариант 1: Используя helm-secrets
helm secrets install tatarlang ./tatarlang-chart \
  --namespace tatarlang \
  --create-namespace \
  -f tatarlang-chart/values-vault.yaml

# Вариант 2: Используя vals напрямую
vals eval -f tatarlang-chart/values-vault.yaml | \
  helm install tatarlang ./tatarlang-chart \
  --namespace tatarlang \
  --create-namespace \
  -f -

# Вариант 3: Без Vault (используя обычные секреты)
helm install tatarlang ./tatarlang-chart \
  --namespace tatarlang \
  --create-namespace \
  --set vault.enabled=false
```

### Шаг 3: Проверка работы

```bash
# Проверить статус подов
kubectl get pods -n tatarlang

# Проверить секреты
kubectl get secrets -n tatarlang

# Проверить логи приложения
kubectl logs -n tatarlang -l tier=backend
```

### Формат ссылок на секреты в Vault

В файле `values-vault.yaml` используются ссылки на секреты в формате:

```yaml
vault:
  enabled: true
  refs:
    postgres:
      user: "ref+vault://secret/tatarlang/db#POSTGRES_USER"
      password: "ref+vault://secret/tatarlang/db#POSTGRES_PASSWORD"
    rabbitmq:
      user: "ref+vault://secret/tatarlang/rabbitmq#RABBITMQ_USER"
      password: "ref+vault://secret/tatarlang/rabbitmq#RABBITMQ_PASS"
    celery:
      brokerUrl: "ref+vault://secret/tatarlang/celery#CELERY_BROKER_URL"
```

**API ключи в Vault:**
- `secret/tatarlang/api/weather#WEATHER_API_KEY` - ключ OpenWeatherMap
- `secret/tatarlang/api/news#NEWS_API_KEY` - ключ NewsAPI

### Troubleshooting Vault

#### Проблема: Vault не отвечает

```bash
# Проверить логи
kubectl logs -n vault -l app.kubernetes.io/name=vault-chart

# Проверить статус
kubectl exec -n vault <vault-pod> -c vault -- vault status

# Если Sealed: true - выполнить unseal
```

#### Проблема: Vault запечатан после перезапуска

```bash
# Получить ключи unseal
KEY1=$(cat vault-keys/unseal-key-1.txt)
KEY2=$(cat vault-keys/unseal-key-2.txt)
KEY3=$(cat vault-keys/unseal-key-3.txt)

# Выполнить unseal
VAULT_POD=$(kubectl get pod -n vault -l app.kubernetes.io/name=vault-chart \
  --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal "$KEY1"
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal "$KEY2"
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator unseal "$KEY3"
```

#### Проблема: helm-secrets не работает

```bash
# Переустановить плагин
helm plugin uninstall secrets
helm plugin install https://github.com/jkroepke/helm-secrets --verify=false

# Или использовать vals напрямую
vals eval -f values-vault.yaml | helm install ...
```

---

## Дополнительные возможности

### Использование RabbitMQ Producer/Consumer в коде

```python
# В Django view или management command
from backend.rabbitmq_producer import RabbitMQProducer

producer = RabbitMQProducer()
try:
    producer.send_api_task(
        api_alias="weather",
        task_params={"city": "Kazan", "country": "RU"},
        routing_key="weather"
    )
finally:
    producer.close()
```

### Запуск Consumer в Kubernetes

```bash
# Создать Job для consumer
kubectl create job -n tatarlang weather-consumer \
  --image=tatarlang-backend:latest \
  -- python rabbitmq_consumer.py weather_queue weather

# Проверить логи
kubectl logs -n tatarlang job/weather-consumer
```

### Мониторинг Celery через Flower

Flower предоставляет:
- Список активных задач
- История выполненных задач
- Статистику по воркерам
- Графики производительности
- Управление воркерами

### Настройка RabbitMQ в Kubernetes

RabbitMQ развертывается через Bitnami Helm chart с:
- LoadBalancer сервисом для внешнего доступа
- Ingress для веб-интерфейса управления
- Persistent storage для данных
- Аутентификацией через секреты из Vault

**Для Yandex Cloud:**
Добавьте аннотации в `values.yaml`:
```yaml
rabbitmq:
  service:
    annotations:
      yandex.cloud/load-balancer-type: "external"
      yandex.cloud/subnet-id: "your-subnet-id"
```

---

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Убедитесь, что все порты свободны
4. Проверьте, что Docker Desktop запущен (macOS/Windows)
5. Проверьте системные требования
6. Для RabbitMQ: проверьте подключение через Management UI
7. Для Celery: проверьте статус воркеров через Flower
8. Для задач: проверьте логи через `docker-compose logs celery_worker`

### Полезные команды для отладки

```bash
# Проверка RabbitMQ
docker-compose exec rabbitmq rabbitmqctl status

# Проверка Celery воркеров
docker-compose exec celery_worker celery -A tatarlang.celery inspect active

# Просмотр результатов API задач
docker-compose exec backend ls -la /app/api_responses/

# Проверка подключения к RabbitMQ
docker-compose exec backend python -c "import pika; print('OK')"
```

---

## Лицензия

[Укажите лицензию проекта]
