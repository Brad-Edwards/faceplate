#!/usr/bin/env bash
set -euo pipefail

# Bump version across all project files
# Usage: ./scripts/bump-version.sh 0.1.2

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.2"
    exit 1
fi

VERSION="$1"

# Validate version format (semver)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
    echo "Error: Version must be semver format (e.g., 0.1.2 or 0.1.2-alpha.1)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Bumping version to $VERSION..."

# sonar-project.properties
if [ -f "$ROOT_DIR/sonar-project.properties" ]; then
    sed -i "s/^sonar.projectVersion=.*/sonar.projectVersion=$VERSION/" "$ROOT_DIR/sonar-project.properties"
    echo "  ✓ sonar-project.properties"
fi

# backend/pyproject.toml
if [ -f "$ROOT_DIR/backend/pyproject.toml" ]; then
    sed -i "s/^version = \".*\"/version = \"$VERSION\"/" "$ROOT_DIR/backend/pyproject.toml"
    echo "  ✓ backend/pyproject.toml"
fi

# frontend/package.json
if [ -f "$ROOT_DIR/frontend/package.json" ]; then
    # Use node/npm for reliable JSON editing
    cd "$ROOT_DIR/frontend"
    npm version "$VERSION" --no-git-tag-version --allow-same-version >/dev/null 2>&1
    echo "  ✓ frontend/package.json"
    cd - >/dev/null
fi

echo ""
echo "Version bumped to $VERSION"
echo ""
echo "Remember to:"
echo "  1. Update CHANGELOG.md manually"
echo "  2. Commit changes"
echo "  3. Tag release: git tag v$VERSION"

