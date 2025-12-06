#!/bin/bash

# Script to deploy charts using helm-secrets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VAULT_CHART_DIR="$PROJECT_DIR/vault-chart"
TATARLANG_CHART_DIR="$PROJECT_DIR/tatarlang-chart"

RELEASE_NAME_VAULT="vault"
RELEASE_NAME_TATARLANG="tatarlang"
NAMESPACE_VAULT="vault"
NAMESPACE_TATARLANG="tatarlang"

# Check if helm-secrets is installed
if ! helm plugin list | grep -q secrets; then
    echo "Installing helm-secrets plugin..."
    helm plugin install https://github.com/jkroepke/helm-secrets
fi

# Check if vals is installed
if ! command -v vals &> /dev/null; then
    echo "Error: vals is not installed. Please install it first:"
    echo "  brew install vals  # macOS"
    echo "  or visit: https://github.com/helmfile/vals"
    exit 1
fi

# Deploy Vault
echo "Deploying Vault..."
helm secrets upgrade --install "$RELEASE_NAME_VAULT" "$VAULT_CHART_DIR" \
    --namespace "$NAMESPACE_VAULT" \
    --create-namespace \
    --wait

echo "Waiting for Vault to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=vault-chart -n "$NAMESPACE_VAULT" --timeout=300s

# Initialize and setup Vault if needed
if [ ! -f "$PROJECT_DIR/vault-keys/root-token.txt" ]; then
    echo "Initializing Vault..."
    cd "$VAULT_CHART_DIR/scripts"
    ./vault-init.sh
    
    echo "Setting up Vault..."
    ./vault-setup.sh
    cd "$PROJECT_DIR"
fi

# Deploy Tatarlang with vault integration
echo "Deploying Tatarlang application..."
helm secrets upgrade --install "$RELEASE_NAME_TATARLANG" "$TATARLANG_CHART_DIR" \
    --namespace "$NAMESPACE_TATARLANG" \
    --create-namespace \
    --set vault.enabled=true \
    --set vault.address="http://vault.vault.svc.cluster.local:8200" \
    --set-file vault.roleId="$PROJECT_DIR/vault-keys/role-id.txt" \
    --set-file vault.secretId="$PROJECT_DIR/vault-keys/secret-id.txt" \
    --set vault.path="secret/data/tatarlang" \
    --wait

echo "Deployment completed successfully!"

