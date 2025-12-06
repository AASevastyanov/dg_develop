#!/bin/bash

# Script to validate Helm chart

set -e

CHART_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE_NAME="tatarlang"

echo "Validating Helm chart..."
helm lint "$CHART_DIR"

echo ""
echo "Running dry-run installation..."
helm install "$RELEASE_NAME" "$CHART_DIR" --dry-run --debug

echo ""
echo "Chart validation completed successfully!"

