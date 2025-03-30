#!/bin/bash

set -e  # Stop on first error

echo "🔨 Cleaning old builds..."
rm -rf build dist *.egg-info || true

echo "📝 Updating version number..."
VERSION=$(grep version setup.py | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | awk -F. '{$3+=1; print $1"."$2"."$3}')
sed -i "s/version=\"[^\"]*\"/version=\"$VERSION\"/" setup.py
echo "→ Updated to version $VERSION"

echo "📦 Building package..."
pipx run build

echo "🚀 Uploading to PyPI..."
pipx run twine upload dist/*

echo "✅ Published ethical-ai-framework version $VERSION"
