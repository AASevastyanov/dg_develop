#!/bin/bash
# Complete Vault initialization script
# Run this manually after Vault pod is ready

set -e

VAULT_NAMESPACE="${VAULT_NAMESPACE:-vault}"
VAULT_ADDR="http://vault-vault-chart.vault.svc.cluster.local:8200"

echo "=== Vault Initialization Script ==="
echo ""
echo "This script will:"
echo "1. Initialize Vault (if not initialized)"
echo "2. Unseal Vault"
echo "3. Save keys to vault-keys/ directory"
echo ""

# Get Vault pod
VAULT_POD=$(kubectl get pod -n "$VAULT_NAMESPACE" -l app.kubernetes.io/name=vault-chart --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

if [ -z "$VAULT_POD" ]; then
    echo "Error: No running Vault pod found"
    exit 1
fi

echo "Using pod: $VAULT_POD"
echo ""

# Check if initialized
INIT_STATUS=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- vault status -format=json 2>&1 | grep -o '"initialized":[^,]*' | cut -d: -f2 || echo "false")

if [ "$INIT_STATUS" = "false" ]; then
    echo "Initializing Vault..."
    INIT_OUTPUT=$(kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- vault operator init -format=json 2>&1)
    
    # Extract values
    ROOT_TOKEN=$(echo "$INIT_OUTPUT" | sed -n 's/.*"root_token":"\([^"]*\)".*/\1/p' | head -1)
    UNSEAL_KEY_1=$(echo "$INIT_OUTPUT" | sed -n 's/.*"unseal_keys_b64":\["\([^"]*\)".*/\1/p' | head -1)
    UNSEAL_KEY_2=$(echo "$INIT_OUTPUT" | sed -n 's/.*"unseal_keys_b64":\["[^"]*","\([^"]*\)".*/\1/p' | head -1)
    UNSEAL_KEY_3=$(echo "$INIT_OUTPUT" | sed -n 's/.*"unseal_keys_b64":\["[^"]*","[^"]*","\([^"]*\)".*/\1/p' | head -1)
else
    echo "Vault already initialized. You need unseal keys to proceed."
    echo "If you have keys, run:"
    echo "  kubectl exec -n vault $VAULT_POD -c vault -- vault operator unseal <KEY1>"
    echo "  kubectl exec -n vault $VAULT_POD -c vault -- vault operator unseal <KEY2>"
    echo "  kubectl exec -n vault $VAULT_POD -c vault -- vault operator unseal <KEY3>"
    exit 1
fi

echo "Unsealing Vault..."
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- sh -c "echo '$UNSEAL_KEY_1' | vault operator unseal -" || kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- vault operator unseal "$UNSEAL_KEY_1"
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- sh -c "echo '$UNSEAL_KEY_2' | vault operator unseal -" || kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- vault operator unseal "$UNSEAL_KEY_2"
kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- sh -c "echo '$UNSEAL_KEY_3' | vault operator unseal -" || kubectl exec -n "$VAULT_NAMESPACE" "$VAULT_POD" -c vault -- vault operator unseal "$UNSEAL_KEY_3"

echo ""
echo "=== VAULT INITIALIZED AND UNSEALED ==="
echo "Root token: $ROOT_TOKEN"
echo "Unseal key 1: $UNSEAL_KEY_1"
echo "Unseal key 2: $UNSEAL_KEY_2"
echo "Unseal key 3: $UNSEAL_KEY_3"
echo ""

# Save to file
mkdir -p ../../vault-keys
echo "$ROOT_TOKEN" > ../../vault-keys/root-token.txt
echo "$UNSEAL_KEY_1" > ../../vault-keys/unseal-key-1.txt
echo "$UNSEAL_KEY_2" > ../../vault-keys/unseal-key-2.txt
echo "$UNSEAL_KEY_3" > ../../vault-keys/unseal-key-3.txt

echo "Keys saved to ../../vault-keys/"
echo ""
echo "IMPORTANT: Save these keys securely! They are required to unseal Vault after restarts."


