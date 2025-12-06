#!/bin/bash

# Script to package Helm chart

set -e

CHART_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${CHART_DIR}/../helm-releases"

echo "Packaging Helm chart..."
mkdir -p "$OUTPUT_DIR"

helm package "$CHART_DIR" --destination "$OUTPUT_DIR"

echo ""
echo "Chart packaged successfully!"
echo "Package location: $OUTPUT_DIR"

