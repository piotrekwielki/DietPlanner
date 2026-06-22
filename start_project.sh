#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

NO_BROWSER=0
SETUP_ONLY=0
PORT=8010
BIND_ADDRESS="127.0.0.1"

print_help() {
    cat <<'EOF'
Diet Planner - start script for Linux/macOS

Usage:
  ./start_project.sh [options]
  bash start_project.sh [options]

Options:
  --setup-only           Prepare venv, install dependencies and run migrations, then exit.
  --no-browser           Do not open the browser automatically.
  --port PORT            Run Django on a custom port. Default: 8010.
  --bind-address ADDRESS Run Django on a custom address. Default: 127.0.0.1.
  -h, --help             Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --setup-only)
            SETUP_ONLY=1
            shift
            ;;
        --no-browser)
            NO_BROWSER=1
            shift
            ;;
        --port)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --port." >&2
                exit 1
            fi
            PORT="$2"
            shift 2
            ;;
        --bind-address)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --bind-address." >&2
                exit 1
            fi
            BIND_ADDRESS="$2"
            shift 2
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            print_help
            exit 1
            ;;
    esac
done

VENV_DIR="$PROJECT_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
MANAGE_PY="$PROJECT_ROOT/manage.py"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
SERVER_ADDRESS="${BIND_ADDRESS}:${PORT}"
PROJECT_URL="http://${SERVER_ADDRESS}/"

write_step() {
    printf '\n==> %s\n' "$1"
}

find_base_python() {
    local candidates=("python3.12" "python3" "python")
    local candidate

    for candidate in "${candidates[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
            then
                printf '%s\n' "$candidate"
                return 0
            fi
        fi
    done

    echo "Python 3.11 or newer was not found. Install Python 3.12 and try again." >&2
    return 1
}

ensure_venv() {
    if [[ -x "$VENV_PYTHON" ]]; then
        return
    fi

    write_step "Creating .venv"
    local base_python
    base_python="$(find_base_python)"
    "$base_python" -m venv "$VENV_DIR"

    if [[ ! -x "$VENV_PYTHON" ]]; then
        echo "Could not create .venv." >&2
        exit 1
    fi
}

ensure_requirements() {
    if "$VENV_PYTHON" -c "import django" >/dev/null 2>&1; then
        write_step "Django is already installed"
        return
    fi

    write_step "Installing dependencies from requirements.txt"
    "$VENV_PYTHON" -m pip install -r "$REQUIREMENTS_FILE"
}

manage() {
    "$VENV_PYTHON" "$MANAGE_PY" "$@"
}

server_available() {
    "$VENV_PYTHON" - "$PROJECT_URL" <<'PY' >/dev/null 2>&1
import sys
from urllib.request import urlopen

try:
    with urlopen(sys.argv[1], timeout=2) as response:
        raise SystemExit(0 if response.status >= 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

open_browser() {
    if [[ "$NO_BROWSER" -eq 1 ]]; then
        return
    fi

    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$PROJECT_URL" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "$PROJECT_URL" >/dev/null 2>&1 || true
    fi
}

wait_for_server() {
    local timeout="${1:-15}"
    local elapsed=0

    while [[ "$elapsed" -lt "$timeout" ]]; do
        if server_available; then
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done

    return 1
}

FRESH_DATABASE=0
if [[ ! -f "$PROJECT_ROOT/db.sqlite3" ]]; then
    FRESH_DATABASE=1
fi

write_step "Preparing project"
ensure_venv
ensure_requirements

write_step "Running migrations"
manage migrate --noinput

if [[ "$FRESH_DATABASE" -eq 1 ]]; then
    write_step "Adding seed data"
    manage seed_data
fi

if [[ "$SETUP_ONLY" -eq 1 ]]; then
    write_step "Environment is ready"
    exit 0
fi

if server_available; then
    write_step "Server already runs at $PROJECT_URL"
    open_browser
    exit 0
fi

write_step "Starting Django server at $PROJECT_URL"
manage runserver "$SERVER_ADDRESS" &
SERVER_PID=$!

cleanup() {
    if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
        kill "$SERVER_PID" >/dev/null 2>&1 || true
    fi
}
trap cleanup INT TERM EXIT

if wait_for_server 15; then
    write_step "Application is available at $PROJECT_URL"
    open_browser
else
    echo "Server is taking longer than usual to start. Watch the Django logs below." >&2
fi

wait "$SERVER_PID"
