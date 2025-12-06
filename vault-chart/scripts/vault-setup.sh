#!/bin/bash

# Script to setup Vault: enable secret engine, create policies, and configure AppRole

set -e

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

# Get Vault pod name
VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

if [ -z "$VAULT_POD" ]; then
    echo "Error: Vault pod not found"
    exit 1
fi

echo "Setting up Vault with root token using pod: $VAULT_POD..."

# Enable KV v2 secret engine
echo "Enabling KV v2 secret engine..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault secrets enable -path=secret kv-v2"

# Create policy for Tatarlang application
echo "Creating Tatarlang policy..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault policy write tatarlang-policy - <<EOF
path \"secret/data/tatarlang/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"delete\", \"list\"]
}

path \"secret/metadata/tatarlang/*\" {
  capabilities = [\"list\", \"read\", \"delete\"]
}
EOF"

# Enable AppRole authentication
echo "Enabling AppRole authentication..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault auth enable approle"

# Create AppRole for Tatarlang
echo "Creating AppRole for Tatarlang..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault write auth/approle/role/tatarlang-role \
    token_policies=tatarlang-policy \
    token_ttl=1h \
    token_max_ttl=4h"

# Get Role ID
ROLE_ID=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault read -field=role_id auth/approle/role/tatarlang-role/role-id")

# Generate Secret ID
SECRET_ID=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- \
    sh -c "VAULT_ADDR=$VAULT_ADDR VAULT_TOKEN=$ROOT_TOKEN vault write -field=secret_id -f auth/approle/role/tatarlang-role/secret-id")

echo "AppRole created successfully!"
echo "Role ID: $ROLE_ID"
echo "Secret ID: $SECRET_ID"

# Save to file
mkdir -p ../vault-keys
echo "$ROLE_ID" > ../vault-keys/role-id.txt
echo "$SECRET_ID" > ../vault-keys/secret-id.txt

echo "Role ID and Secret ID saved to ../vault-keys/"

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

echo "Vault setup completed!"

