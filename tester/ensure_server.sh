#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

HOST="127.0.0.1"
PORT="6667"
PASSWORD="1234"
PORT_SRC="default"
PASS_SRC="default"

# Source .env if present (relative to repo root or script dir)
ENV_FILE=""
if [ -f "${REPO_DIR}/.env" ]; then
    ENV_FILE="${REPO_DIR}/.env"
elif [ -f "${SCRIPT_DIR}/.env" ]; then
    ENV_FILE="${SCRIPT_DIR}/.env"
fi

if [ -n "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    [ -n "${PORT:-}" ] && PORT_SRC=".env"
    [ -n "${PASSWORD:-}" ] && PASS_SRC=".env"
fi

CMD_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        -p|--password)
            if [ -n "${2:-}" ]; then
                PASSWORD="$2"
                PASS_SRC="arguments"
                CMD_ARGS+=("$1" "$2")
                shift 2
            else
                shift
            fi
            ;;
        --port)
            if [ -n "${2:-}" ]; then
                PORT="$2"
                PORT_SRC="arguments"
                CMD_ARGS+=("$1" "$2")
                shift 2
            else
                shift
            fi
            ;;
        --host)
            if [ -n "${2:-}" ]; then
                HOST="$2"
                CMD_ARGS+=("$1" "$2")
                shift 2
            else
                shift
            fi
            ;;
        --)
            shift
            CMD_ARGS+=("$@")
            break
            ;;
        *)
            CMD_ARGS+=("$1")
            shift
            ;;
    esac
done

format_config_source() {
    if [ "$PORT_SRC" = "$PASS_SRC" ]; then
        case "$PORT_SRC" in
            "arguments") echo "arguments" ;;
            ".env") echo ".env file" ;;
            *) echo "defaults" ;;
        esac
    else
        echo "arguments/defaults/.env (Port from ${PORT_SRC}, Password from ${PASS_SRC})"
    fi
}

SRC_LABEL=$(format_config_source)
echo -e "${CYAN}Using config from ${SRC_LABEL}.${NC}"
echo -e "${CYAN}Port: ${PORT} Password: ${PASSWORD}${NC}"

is_server_listening() {
    if command -v nc >/dev/null 2>&1; then
        nc -z -w 1 "$HOST" "$PORT" 2>/dev/null
    elif (echo >/dev/tcp/"$HOST"/"$PORT") 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

SERVER_PID=""
cleanup() {
    trap - INT TERM EXIT
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup INT TERM EXIT

SERVER_BIN="${SERVER_BIN:-${REPO_DIR}/ircserv}"

if is_server_listening; then
    echo -e "${GREEN}Using existing IRC server at ${HOST}:${PORT}${NC}\n"
else
    # Build server binary if missing
    if [ ! -x "$SERVER_BIN" ]; then
        echo -e "${CYAN}Building server binary at ${REPO_DIR}...${NC}"
        make -C "$REPO_DIR" >/dev/null || {
            echo -e "${RED}${BOLD}Failed to build IRC server at ${REPO_DIR}${NC}"
            exit 1
        }
    fi

    read -r -a EXTRA_ARGS <<< "${SERVER_EXTRA_ARGS:-}"
    "$SERVER_BIN" "$PORT" "${PASSWORD:-}" "${EXTRA_ARGS[@]}" >/dev/null 2>&1 &
    SERVER_PID=$!

    # Wait up to 3 seconds for server to start listening
    started=0
    for (( i=0; i<30; i++ )); do
        if is_server_listening; then
            started=1
            break
        fi
        # If server process died prematurely
        if ! kill -0 "$SERVER_PID" 2>/dev/null; then
            break
        fi
        sleep 0.1
    done

    if [ "$started" -eq 1 ]; then
        echo -e "${GREEN}Started new IRC server (PID: ${SERVER_PID}) at ${HOST}:${PORT}${NC}\n"
    else
        echo -e "${RED}${BOLD}Error: Failed to start IRC server at ${HOST}:${PORT}.${NC}\n"
        exit 1
    fi
fi

# Export config so executed program or script knows them if needed
export HOST PORT PASSWORD

# If command is provided, execute it and forward its exit code
if [ ${#CMD_ARGS[@]} -gt 0 ]; then
    set +e
    "${CMD_ARGS[@]}"
    CMD_EXIT=$?
    cleanup
    exit $CMD_EXIT
fi
