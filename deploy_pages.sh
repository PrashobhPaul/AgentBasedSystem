#!/usr/bin/env bash
#
# Adds the in-browser (stlite) GitHub Pages demo to PrashobhPaul/AgentBasedSystem,
# plus the Pages + CI workflows, and tidies up the helper scripts that were
# committed earlier. Run from inside this folder with Git Bash / WSL / macOS / Linux:
#
#   bash deploy_pages.sh
#
# After it pushes: enable Pages once in the repo
#   Settings -> Pages -> Build and deployment -> Source: GitHub Actions
# The "Deploy Pages" workflow then publishes to:
#   https://prashobhpaul.github.io/AgentBasedSystem/
set -euo pipefail

REPO_URL="https://github.com/PrashobhPaul/AgentBasedSystem.git"
BRANCH="main"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"

echo "==> Regenerating the static page from current source"
python "$SRC_DIR/scripts/build_pages.py"

echo "==> Cloning $REPO_URL"
git clone --quiet "$REPO_URL" "$WORK/repo"
cd "$WORK/repo"
git checkout -q "$BRANCH"

echo "==> Adding Pages demo, workflows, and config"
mkdir -p docs scripts .github/workflows
cp "$SRC_DIR/docs/index.html"                 docs/index.html
cp "$SRC_DIR/docs/.nojekyll"                  docs/.nojekyll
cp "$SRC_DIR/scripts/build_pages.py"          scripts/build_pages.py
cp "$SRC_DIR/.github/workflows/pages.yml"     .github/workflows/pages.yml
cp "$SRC_DIR/.github/workflows/ci.yml"        .github/workflows/ci.yml
cp "$SRC_DIR/.env.example"                    .env.example

echo "==> Removing helper scripts that were committed earlier (cleanup)"
git rm -q --ignore-unmatch update_repo.sh fix_repo.sh deploy_pages.sh || true

git add -A
git commit -q -m "feat: add in-browser (stlite) GitHub Pages demo + Pages/CI workflows

- docs/index.html runs the Streamlit app fully client-side via stlite (Pyodide/WASM)
- scripts/build_pages.py regenerates the page from source (single source of truth)
- .github/workflows/pages.yml deploys the demo to GitHub Pages
- .github/workflows/ci.yml runs pytest on push (was missing from main)
- add .env.example; remove committed helper scripts"

echo "==> Pushing $BRANCH"
git push -u origin "$BRANCH"

echo
echo "Pushed. Now enable Pages ONCE:"
echo "  Settings -> Pages -> Source: GitHub Actions"
echo "Then watch it deploy:"
echo "  https://github.com/PrashobhPaul/AgentBasedSystem/actions"
echo "Live URL once green:"
echo "  https://prashobhpaul.github.io/AgentBasedSystem/"
