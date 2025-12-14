# Tatarlang - Инструкция по запуску

Полная инструкция по запуску приложения Tatarlang с использованием Docker и Docker Compose.

## Содержание

1. [Установка Docker](#установка-docker)
2. [Быстрый старт](#быстрый-старт)
3. [Подробная инструкция](#подробная-инструкция)
4. [Проверка работы](#проверка-работы)
5. [Управление приложением](#управление-приложением)
6. [Troubleshooting](#troubleshooting)

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
├── backend/                 # Django backend приложение
│   ├── tatarlang/          # Основное приложение
│   ├── manage.py           # Django management script
│   └── Dockerfile          # Docker образ для backend
├── frontend/                # React frontend приложение
│   ├── src/                # Исходный код
│   ├── public/             # Статические файлы
│   └── Dockerfile          # Docker образ для frontend
├── docker-compose.yaml     # Конфигурация Docker Compose
├── .env                    # Переменные окружения (создается вручную)
└── README.md              # Этот файл
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

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Убедитесь, что все порты свободны
4. Проверьте, что Docker Desktop запущен (macOS/Windows)
5. Проверьте системные требования

---

## Лицензия

[Укажите лицензию проекта]
