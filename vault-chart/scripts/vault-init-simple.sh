#!/bin/bash

# Simplified script to initialize Vault using API

set -e

VAULT_NAMESPACE="${VAULT_NAMESPACE:-vault}"
VAULT_ADDR="http://vault.vault.svc.cluster.local:8200"

echo "Getting Vault pod..."
VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

if [ -z "$VAULT_POD" ]; then
    echo "Error: No running Vault pod found"
    exit 1
fi

echo "Using pod: $VAULT_POD"
echo "Initializing Vault via API..."

# Initialize Vault
INIT_RESPONSE=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- sh -c "wget -qO- --post-data='{\"secret_shares\":3,\"secret_threshold\":3}' $VAULT_ADDR/v1/sys/init" 2>/dev/null || \
    kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- sh -c "curl -s -X PUT -d '{\"secret_shares\":3,\"secret_threshold\":3}' $VAULT_ADDR/v1/sys/init" 2>/dev/null)

if [ -z "$INIT_RESPONSE" ] || echo "$INIT_RESPONSE" | grep -q "error"; then
    echo "Trying direct exec method..."
    INIT_OUTPUT=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator init -format=json 2>&1)
else
    echo "Initialized via API"
    INIT_OUTPUT="$INIT_RESPONSE"
fi

# Try to parse JSON (if we have jq in pod, or parse manually)
if command -v jq &> /dev/null; then
    UNSEAL_KEY_1=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[0]')
    UNSEAL_KEY_2=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[1]')
    UNSEAL_KEY_3=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[2]')
    ROOT_TOKEN=$(echo "$INIT_OUTPUT" | jq -r '.root_token')
else
    # Manual parsing
    UNSEAL_KEY_1=$(echo "$INIT_OUTPUT" | grep -o '"unseal_keys_b64":\["[^"]*"' | head -1 | cut -d'"' -f4)
    UNSEAL_KEY_2=$(echo "$INIT_OUTPUT" | grep -o '"unseal_keys_b64":\["[^"]*","[^"]*"' | head -1 | cut -d'"' -f6)
    UNSEAL_KEY_3=$(echo "$INIT_OUTPUT" | grep -o '"unseal_keys_b64":\["[^"]*","[^"]*","[^"]*"' | head -1 | cut -d'"' -f8)
    ROOT_TOKEN=$(echo "$INIT_OUTPUT" | grep -o '"root_token":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ -z "$ROOT_TOKEN" ]; then
    echo "Error: Failed to initialize Vault. Output:"
    echo "$INIT_OUTPUT"
    exit 1
fi

echo "Unsealing Vault..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_1" 2>&1 || true
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_2" 2>&1 || true
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_3" 2>&1 || true

echo "Vault initialized and unsealed!"
echo "Root token: $ROOT_TOKEN"

# Save to file
mkdir -p ../../vault-keys
echo "$ROOT_TOKEN" > ../../vault-keys/root-token.txt
echo "$UNSEAL_KEY_1" > ../../vault-keys/unseal-key-1.txt
echo "$UNSEAL_KEY_2" > ../../vault-keys/unseal-key-2.txt
echo "$UNSEAL_KEY_3" > ../../vault-keys/unseal-key-3.txt

echo "Keys saved to ../../vault-keys/"


