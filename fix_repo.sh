#!/usr/bin/env bash
#
# Corrective updater for https://github.com/PrashobhPaul/AgentBasedSystem
#
# The previous update flattened the agent_system/ package onto the repo root,
# dropped several files (.github CI, requirements, tests, run_cli, .env.example),
# and left stale old files (agents/bot_agent.py, utils/). This repairs main by
# laying down the correct, verified tree from this folder.
#
# Run with Git Bash / WSL / macOS / Linux from inside this folder:
#   bash fix_repo.sh
#
# Default target is main (main is currently broken, so we repair it directly).
# To go via a PR instead, set BRANCH to something like fix/restore-package-layout.
set -euo pipefail

REPO_URL="https://github.com/PrashobhPaul/AgentBasedSystem.git"
BRANCH="main"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"

echo "==> Cloning $REPO_URL"
git clone --quiet "$REPO_URL" "$WORK/repo"
cd "$WORK/repo"
git checkout -q "$BRANCH" 2>/dev/null || git checkout -q -b "$BRANCH"

echo "==> Removing flattened/stale source"
git rm -r --quiet --ignore-unmatch \
  agents utils database repository \
  config.py graph.py intent.py models.py __init__.py || true

echo "==> Laying down the correct tree from $SRC_DIR"
( cd "$SRC_DIR" && tar \
    --exclude='./.git' \
    --exclude='./__pycache__' \
    --exclude='*/__pycache__' \
    --exclude='*.pyc' \
    --exclude='./.pytmp' \
    --exclude='./event.db' \
    --exclude='./update_repo.sh' \
    --exclude='./fix_repo.sh' \
    -cf - . ) | tar -xf - -C "$WORK/repo"

echo "==> Sanity check: package imports before committing"
( cd "$WORK/repo" && python -c "import agent_system.graph" ) \
  && echo "    import OK" || { echo "    import FAILED — aborting"; exit 1; }

echo "==> Staging and committing"
git add -A
git commit -q -m "fix: restore agent_system package layout and missing files

The prior commit flattened the agent_system/ package onto the repo root,
breaking every 'from agent_system...' import (ModuleNotFoundError). It also
omitted CI, requirements.txt, tests/, run_cli.py and .env.example, and left
stale agents/bot_agent.py and utils/ files behind.

- Restore the agent_system/ package layout so imports resolve
- Add .github/workflows/ci.yml, requirements.txt, pytest.ini, tests/ (27),
  run_cli.py and .env.example
- Remove stale agents/bot_agent.py, utils/db.py, utils/helpers.py"

echo "==> Pushing $BRANCH"
git push -u origin "$BRANCH"

echo
echo "Done. View main: https://github.com/PrashobhPaul/AgentBasedSystem"
echo "Actions/CI:      https://github.com/PrashobhPaul/AgentBasedSystem/actions"
