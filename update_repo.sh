#!/usr/bin/env bash
#
# One-shot updater for https://github.com/PrashobhPaul/AgentBasedSystem
# Run this from inside the generated project folder (the folder containing this
# script) using Git Bash (Windows), WSL, macOS, or Linux. It uses YOUR local
# git authentication — no credentials are stored or read by anyone else.
#
#   bash update_repo.sh
#
set -euo pipefail

REPO_URL="https://github.com/PrashobhPaul/AgentBasedSystem.git"
BRANCH="refactor/langgraph-rewrite"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"

echo "==> Cloning $REPO_URL"
git clone --quiet "$REPO_URL" "$WORK/repo"
cd "$WORK/repo"

echo "==> Creating branch $BRANCH"
git checkout -q -b "$BRANCH"

echo "==> Removing superseded source (replaced by agent_system/ package)"
git rm -r --quiet --ignore-unmatch agents utils database || true

echo "==> Copying rebuilt project from $SRC_DIR"
( cd "$SRC_DIR" && tar \
    --exclude='./.git' \
    --exclude='./__pycache__' \
    --exclude='*/__pycache__' \
    --exclude='*.pyc' \
    --exclude='./.pytmp' \
    --exclude='./event.db' \
    --exclude='./update_repo.sh' \
    -cf - . ) | tar -xf - -C "$WORK/repo"

echo "==> Staging and committing"
git add -A
git commit -q -m "Refactor into LangGraph-orchestrated package + add CI

- Fix crashing signature mismatch (get_available_sessions) and dead conflict logic
- Unify duplicated FAQ/agent code into a single agent_system/ package
- Add guarded registration flow, typed models, optional provider-agnostic LLM intent layer
- Derive calendar from real registrations; minute-based time comparison
- Add pytest suite (27 tests) and GitHub Actions CI (Python 3.10-3.12)"

echo "==> Pushing branch"
git push -u origin "$BRANCH"

echo
echo "Done. Open the pull request here:"
echo "  https://github.com/PrashobhPaul/AgentBasedSystem/compare/main...$BRANCH?expand=1"
