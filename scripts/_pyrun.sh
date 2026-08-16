#!/usr/bin/env bash
# Cross-platform Python launcher for AI log hooks.
# Prefers the project venv (it has requirements.txt installed, e.g.
# python-dotenv that submit_log.py needs to read .env), then falls back to
# python3 → python → py -3 on PATH; on Windows, finally probes common Python
# install locations because Git Bash launched by some hooks gets a stripped
# PATH that omits the Windows Python directory.
# Designed to be called as: bash scripts/_pyrun.sh <script> [args...]
#
# Exits 0 silently if no Python is found — hooks must never block the AI tool.
# Keep this launcher intentionally lightweight so local hooks and CI remain resilient.
set -u

is_working_python() {
  "$@" -c "import sys" >/dev/null 2>&1
}

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")/.." && pwd)"

PY=()

# 1. Project venv — the only interpreter guaranteed to have our dependencies.
for cand in \
  "$REPO_ROOT/.venv/Scripts/python.exe" \
  "$REPO_ROOT/.venv/bin/python" \
  "$REPO_ROOT/venv/Scripts/python.exe" \
  "$REPO_ROOT/venv/bin/python"; do
  if [ -x "$cand" ] && is_working_python "$cand"; then PY=("$cand"); break; fi
done

# 2. PATH lookup.
if [ ${#PY[@]} -eq 0 ]; then
  if command -v python3 >/dev/null 2>&1 && is_working_python python3; then
    PY=(python3)
  elif command -v python >/dev/null 2>&1 && is_working_python python; then
    PY=(python)
  elif command -v py >/dev/null 2>&1 && is_working_python py -3; then
    PY=(py -3)
  fi
fi

# 3. Standard Windows install locations.
if [ ${#PY[@]} -eq 0 ]; then
  shopt -s nullglob 2>/dev/null || true
  for cand in \
    /c/Users/*/AppData/Local/Programs/Python/Python*/python.exe \
    "/c/Program Files/Python"*/python.exe \
    "/c/Program Files (x86)/Python"*/python.exe \
    /c/Python*/python.exe; do
    if [ -x "$cand" ] && is_working_python "$cand"; then PY=("$cand"); break; fi
  done
  shopt -u nullglob 2>/dev/null || true
fi

[ ${#PY[@]} -gt 0 ] || exit 0

exec "${PY[@]}" "$@"
