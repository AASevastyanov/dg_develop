#!/bin/bash

# Script to setup Vault: enable secret engine, create policies, and configure AppRole

# Don't exit on error for individual commands - we'll handle errors explicitly
set +e

VAULT_ADDR="${VAULT_ADDR:-http://vault-vault-chart.vault.svc.cluster.local:8200}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-vault}"
ROOT_TOKEN="${VAULT_ROOT_TOKEN}"

if [ -z "$ROOT_TOKEN" ]; then
    if [ -f "../../vault-keys/root-token.txt" ]; then
        ROOT_TOKEN=$(cat ../../vault-keys/root-token.txt)
    else
        echo "Error: VAULT_ROOT_TOKEN not set and root-token.txt not found"
        exit 1
    fi
fi

# Get Vault pod name - wait for pod to be available
echo "Waiting for Vault pod to be available..."
for i in {1..30}; do
    VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$VAULT_POD" ]; then
        # Check if container is ready (even if pod is in CrashLoopBackOff, container might be running briefly)
        if kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- echo "test" >/dev/null 2>&1; then
            break
        fi
    fi
    sleep 2
done

if [ -z "$VAULT_POD" ]; then
    echo "Error: Vault pod not found"
    exit 1
fi

echo "Setting up Vault with root token using pod: $VAULT_POD..."

# Wait a moment for container to be ready
sleep 2

# Enable KV v2 secret engine (if not already enabled)
echo "Checking KV v2 secret engine..."
if ! kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault secrets list -format=json" 2>/dev/null | \
    grep -q '"secret/"'; then
    echo "Enabling KV v2 secret engine..."
    kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
        sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault secrets enable -path=secret kv-v2" || \
        echo "Warning: Failed to enable KV v2 (may already be enabled)"
else
    echo "KV v2 secret engine already enabled"
fi

# Create policy for Tatarlang application (if not exists)
echo "Creating/updating Tatarlang policy..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault policy write tatarlang-policy - <<EOF
path \"secret/data/tatarlang/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"delete\", \"list\"]
}

path \"secret/metadata/tatarlang/*\" {
  capabilities = [\"list\", \"read\", \"delete\"]
}
EOF" || echo "Warning: Failed to create policy (may already exist)"

# Create policy for API keys (if not exists)
echo "Creating/updating API keys policy..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault policy write api-keys-policy - <<EOF
path \"secret/data/tatarlang/api/*\" {
  capabilities = [\"read\", \"list\"]
}

path \"secret/metadata/tatarlang/api/*\" {
  capabilities = [\"list\", \"read\"]
}
EOF" || echo "Warning: Failed to create API keys policy (may already exist)"

# Enable AppRole authentication (if not already enabled)
echo "Checking AppRole authentication..."
if ! kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault auth list -format=json" 2>/dev/null | \
    grep -q '"approle/"'; then
    echo "Enabling AppRole authentication..."
    kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
        sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault auth enable approle" || \
        echo "Warning: Failed to enable AppRole (may already be enabled)"
else
    echo "AppRole authentication already enabled"
fi

# Create AppRole for Tatarlang with multiple policies (if not exists)
echo "Creating/updating AppRole for Tatarlang..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault write auth/approle/role/tatarlang-role \
    token_policies=tatarlang-policy,api-keys-policy \
    token_ttl=1h \
    token_max_ttl=4h" || echo "Warning: Failed to create AppRole (may already exist)"

# Get Role ID (create if doesn't exist)
echo "Getting Role ID..."
ROLE_ID=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault read -field=role_id auth/approle/role/tatarlang-role/role-id" 2>/dev/null)

if [ -z "$ROLE_ID" ]; then
    echo "Error: Failed to get Role ID. AppRole may not be created properly."
    exit 1
fi

# Generate Secret ID
echo "Generating Secret ID..."
SECRET_ID=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault write -field=secret_id -f auth/approle/role/tatarlang-role/secret-id" 2>/dev/null)

if [ -z "$SECRET_ID" ]; then
    echo "Error: Failed to generate Secret ID."
    exit 1
fi

echo "AppRole created successfully!"
echo "Role ID: $ROLE_ID"
echo "Secret ID: $SECRET_ID"

# Save to file (use the same directory as root-token.txt)
VAULT_KEYS_DIR="../../vault-keys"
mkdir -p "$VAULT_KEYS_DIR"
echo "$ROLE_ID" > "$VAULT_KEYS_DIR/role-id.txt"
echo "$SECRET_ID" > "$VAULT_KEYS_DIR/secret-id.txt"

echo "Role ID and Secret ID saved to $VAULT_KEYS_DIR/"

# Store secrets in Vault
echo "Storing secrets in Vault..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault kv put secret/tatarlang/db \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres"

kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault kv put secret/tatarlang/rabbitmq \
    RABBITMQ_USER=admin \
    RABBITMQ_PASS=admin"

kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault kv put secret/tatarlang/celery \
    CELERY_BROKER_URL=amqp://admin:admin@rabbitmq:5672//"

# Store API keys for external APIs (OpenWeatherMap and NewsAPI)
echo "Storing API keys in Vault..."
# Note: Replace with actual API keys
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault kv put secret/tatarlang/api/weather \
    WEATHER_API_KEY=your_openweathermap_api_key_here" || echo "Warning: Failed to store weather API key"

kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault kv put secret/tatarlang/api/news \
    NEWS_API_KEY=your_newsapi_key_here" || echo "Warning: Failed to store news API key"

echo "Vault setup completed!"

# Re-enable exit on error for final verification
set -e

