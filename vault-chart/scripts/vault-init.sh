#!/bin/bash

# Script to initialize and unseal Vault

set -e

VAULT_ADDR="${VAULT_ADDR:-http://vault.vault.svc.cluster.local:8200}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-vault}"

echo "Waiting for Vault pod to be running..."
kubectl wait --for=condition=containersready pod -l app.kubernetes.io/name=vault-chart -n "$VAULT_NAMESPACE" --timeout=300s || true

# Get the pod name (use the first running pod)
VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | awk '{print $1}')
if [ -z "$VAULT_POD" ]; then
    VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart -o jsonpath='{.items[0].metadata.name}')
fi

echo "Initializing Vault using pod: $VAULT_POD"
INIT_OUTPUT=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator init -format=json)

UNSEAL_KEY_1=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[0]')
UNSEAL_KEY_2=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[1]')
UNSEAL_KEY_3=$(echo "$INIT_OUTPUT" | jq -r '.unseal_keys_b64[2]')
ROOT_TOKEN=$(echo "$INIT_OUTPUT" | jq -r '.root_token')

echo "Unsealing Vault..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_1"
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_2"
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -- vault operator unseal "$UNSEAL_KEY_3"

echo "Vault initialized and unsealed!"
echo "Root token: $ROOT_TOKEN"
echo "Unseal keys saved. Please store them securely!"

# Save to file
mkdir -p ../vault-keys
echo "$ROOT_TOKEN" > ../vault-keys/root-token.txt
echo "$UNSEAL_KEY_1" > ../vault-keys/unseal-key-1.txt
echo "$UNSEAL_KEY_2" > ../vault-keys/unseal-key-2.txt
echo "$UNSEAL_KEY_3" > ../vault-keys/unseal-key-3.txt

echo "Keys saved to ../vault-keys/"

