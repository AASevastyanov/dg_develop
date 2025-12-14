# Tatarlang - Инструкция по развертыванию

Полная пошаговая инструкция по развертыванию приложения Tatarlang с использованием Helm-чартов и Vault для управления секретами.

## Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Локальный запуск через Docker Compose](#локальный-запуск-через-docker-compose)
3. [Развертывание в Kubernetes с Helm](#развертывание-в-kubernetes-с-helm)
4. [Настройка Vault для управления секретами](#настройка-vault-для-управления-секретами)
5. [Интеграция приложения с Vault](#интеграция-приложения-с-vault)

---

## Предварительные требования

### Необходимое ПО

- **Docker** и **Docker Compose** (для локального запуска)
- **Kubernetes кластер** (minikube, kind, или Docker Desktop с Kubernetes)
- **Helm 3.0+**
- **kubectl** (для работы с Kubernetes)
- **Python 3.10.11** (для локальной разработки backend)

### Установка инструментов

#### macOS

```bash
# Homebrew
brew install docker docker-compose helm kubectl minikube

# Или установите Docker Desktop, который включает Kubernetes
```

#### Linux

```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

## Локальный запуск через Docker Compose

### Шаг 1: Подготовка окружения

```bash
# Перейдите в директорию проекта
cd /path/to/dg_develop

# Создайте .env файл в корне проекта (опционально, если нужны кастомные настройки)
# По умолчанию используются значения из docker-compose.yaml
```

### Шаг 2: Запуск всех сервисов

```bash
# Запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### Шаг 3: Проверка работы

- **Backend API**: http://127.0.0.1:8000
- **Frontend**: http://127.0.0.1:3000
- **API Документация**: 
  - Swagger: http://127.0.0.1:8000/swagger
  - ReDoc: http://127.0.0.1:8000/redoc
- **RabbitMQ Management**: http://127.0.0.1:15672 (admin/admin)
- **Flower (Celery)**: http://127.0.0.1:5555

### Шаг 4: Остановка

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

---

## Развертывание в Kubernetes с Helm

### Шаг 1: Запуск Kubernetes кластера

#### Вариант A: Minikube (рекомендуется для локальной разработки)

```bash
# Запуск minikube
minikube start

# Проверка статуса
minikube status
kubectl get nodes
```

#### Вариант B: Docker Desktop

1. Откройте Docker Desktop
2. Перейдите в Settings → Kubernetes
3. Включите "Enable Kubernetes"
4. Дождитесь запуска кластера

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

### Шаг 3: Установка приложения

```bash
# Установка чарта
helm install tatarlang ./tatarlang-chart

# Или с указанием namespace
helm install tatarlang ./tatarlang-chart --namespace tatarlang --create-namespace

# Проверка установки
helm list
kubectl get pods -n tatarlang
```

### Шаг 4: Сборка Docker-образов для Minikube

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

### Шаг 5: Проверка работы приложения

```bash
# Проверить статус подов
kubectl get pods -n tatarlang

# Проверить сервисы
kubectl get svc -n tatarlang

# Просмотр логов
kubectl logs -n tatarlang -l tier=backend
kubectl logs -n tatarlang -l tier=frontend
```

### Шаг 6: Обновление приложения

```bash
# Обновление чарта
helm upgrade tatarlang ./tatarlang-chart

# С кастомными значениями
helm upgrade tatarlang ./tatarlang-chart -f my-values.yaml
```

### Шаг 7: Удаление приложения

```bash
# Удаление release
helm uninstall tatarlang

# С удалением namespace
helm uninstall tatarlang --namespace tatarlang
kubectl delete namespace tatarlang
```

---

## Настройка Vault для управления секретами

### Шаг 1: Установка необходимых инструментов

```bash
# Установка helm-secrets плагина
helm plugin install https://github.com/jkroepke/helm-secrets --verify=false

# Установка vals (для работы с Vault)
brew install vals  # macOS
# или скачайте с https://github.com/helmfile/vals/releases
```

### Шаг 2: Развертывание Vault

```bash
# Установка Vault
helm install vault ./vault-chart --namespace vault --create-namespace --set persistence.enabled=false

# Ожидание готовности (может занять 1-2 минуты)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=vault-chart -n vault --timeout=300s

# Проверка статуса
kubectl get pods -n vault
```

### Шаг 3: Инициализация Vault

```bash
# Получить имя пода Vault
VAULT_POD=$(kubectl get pod -n vault -l app.kubernetes.io/name=vault-chart --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Инициализировать Vault
kubectl exec -n vault "$VAULT_POD" -c vault -- vault operator init

# ⚠️ ВАЖНО: Сохраните выведенные ключи!
# Вам понадобятся:
# - Root Token (один)
# - Unseal Keys (минимум 3 из 5)
```

### Шаг 4: Unseal Vault

```bash
# Выполните unseal (замените KEY1, KEY2, KEY3 на реальные ключи из предыдущего шага)
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

# Скрипт выполнит:
# - Включение KV v2 secret engine
# - Создание политики доступа (tatarlang-policy)
# - Включение AppRole аутентификации
# - Создание AppRole (tatarlang-role)
# - Сохранение секретов в Vault
```

После выполнения скрипта будут сохранены:
- `vault-keys/role-id.txt` - Role ID для AppRole
- `vault-keys/secret-id.txt` - Secret ID для AppRole

### Шаг 7: Проверка секретов в Vault

```bash
# Получить имя пода
VAULT_POD=$(kubectl get pod -n vault -l app.kubernetes.io/name=vault-chart --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Получить root token
ROOT_TOKEN=$(cat vault-keys/root-token.txt)

# Просмотр секретов
kubectl exec -n vault "$VAULT_POD" -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=$ROOT_TOKEN vault kv list secret/tatarlang"

# Просмотр конкретного секрета
kubectl exec -n vault "$VAULT_POD" -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=$ROOT_TOKEN vault kv get secret/tatarlang/db"
```

---

## Интеграция приложения с Vault

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
# Вариант 1: Используя helm-secrets (если настроен)
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

---

## Структура проекта

```
dg_develop/
├── backend/                 # Django backend приложение
├── frontend/                # React frontend приложение
├── k8s/                     # Оригинальные Kubernetes манифесты
├── tatarlang-chart/         # Helm-чарт приложения
│   ├── charts/              # Subcharts (postgresql, rabbitmq)
│   ├── templates/           # Helm шаблоны
│   ├── scripts/             # Скрипты валидации
│   ├── Chart.yaml
│   ├── values.yaml          # Значения по умолчанию
│   └── values-vault.yaml    # Значения для Vault интеграции
├── vault-chart/             # Helm-чарт Vault
│   ├── templates/
│   ├── scripts/             # Скрипты инициализации Vault
│   ├── Chart.yaml
│   └── values.yaml
├── vault-keys/              # Ключи Vault (не в git!)
│   ├── root-token.txt
│   ├── unseal-key-*.txt
│   ├── role-id.txt
│   └── secret-id.txt
├── scripts/
│   └── deploy.sh           # Скрипт автоматического деплоя
├── docker-compose.yaml      # Docker Compose конфигурация
├── env-example              # Пример env файла с vault refs
└── README.md               # Этот файл
```

---

## Полезные команды

### Kubernetes

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
```

### Vault

```bash
# Статус Vault
kubectl exec -n vault <vault-pod> -c vault -- vault status

# Unseal после перезапуска
kubectl exec -n vault <vault-pod> -c vault -- vault operator unseal <KEY>

# Просмотр политик
kubectl exec -n vault <vault-pod> -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=<ROOT_TOKEN> vault policy list"

# Просмотр AppRole
kubectl exec -n vault <vault-pod> -c vault -- \
  sh -c "VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=<ROOT_TOKEN> vault list auth/approle/role"
```

### Helm

```bash
# Список установленных release
helm list -A

# История изменений
helm history tatarlang

# Откат к предыдущей версии
helm rollback tatarlang <revision-number>

# Просмотр значений
helm get values tatarlang
```

---

## Troubleshooting

### Проблема: Minikube не запускается (API server не стартует)

**Симптомы:**
- Ошибки типа `K8S_APISERVER_MISSING: wait 6m0s for node: wait for apiserver proc: apiserver process never appeared`
- Ошибки `connection refused` при попытке подключиться к API server
- Addons не могут примениться из-за недоступности API server

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

### Проблема: Поды не запускаются (ImagePullBackOff)

**Решение:**
```bash
# Для minikube - собрать образы в контексте minikube
eval $(minikube docker-env)
docker build -t tatarlang-backend:latest ./backend
docker build -t tatarlang-frontend:latest ./frontend
```

### Проблема: Vault не отвечает

**Решение:**
```bash
# Проверить логи
kubectl logs -n vault -l app.kubernetes.io/name=vault-chart

# Проверить статус
kubectl exec -n vault <vault-pod> -c vault -- vault status

# Если Sealed: true - выполнить unseal
```

### Проблема: helm-secrets не работает

**Решение:**
```bash
# Переустановить плагин
helm plugin uninstall secrets
helm plugin install https://github.com/jkroepke/helm-secrets --verify=false

# Или использовать vals напрямую
vals eval -f values-vault.yaml | helm install ...
```

### Проблема: Namespace не удаляется

**Решение:**
```bash
# Принудительное удаление
kubectl delete namespace <namespace> --force --grace-period=0
```

---

## Дополнительная информация

### Переменные окружения

Пример файла `env-example` с vault refs:
```
VAULT_ADDR=http://vault.vault.svc.cluster.local:8200
POSTGRES_USER=ref+vault://secret/tatarlang/db#POSTGRES_USER
POSTGRES_PASSWORD=ref+vault://secret/tatarlang/db#POSTGRES_PASSWORD
```

### Безопасность

- ⚠️ **Никогда не коммитьте ключи Vault в git!**
- ⚠️ Храните `vault-keys/` в безопасном месте
- ⚠️ Используйте разные ключи для разных окружений
- ⚠️ Регулярно ротируйте секреты

### Поддержка

При возникновении проблем:
1. Проверьте логи: `kubectl logs -n <namespace> <pod-name>`
2. Проверьте статус ресурсов: `kubectl get all -n <namespace>`
3. Проверьте события: `kubectl get events -n <namespace>`

---

## Лицензия

[Укажите лицензию проекта]
