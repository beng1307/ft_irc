#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVER_BIN="${SERVER_BIN:-}"

if [ -z "$SERVER_BIN" ]; then
    if [ -x "${REPO_DIR}/ircserv" ]; then
        SERVER_BIN="${REPO_DIR}/ircserv"
    elif [ -x "${REPO_DIR}/ft_irc" ]; then
        SERVER_BIN="${REPO_DIR}/ft_irc"
    else
        SERVER_BIN="${REPO_DIR}/ft_irc"
    fi
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

# Build server if binary missing
if [ ! -x "$SERVER_BIN" ]; then
    echo -e "${CYAN}Building server binary at ${REPO_DIR}...${NC}"
    make -C "$REPO_DIR" >/dev/null || { echo -e "${RED}Failed to build server${NC}"; exit 1; }
fi

PASSED=0
FAILED=0
TOTAL=0

LAST_STDOUT=""
LAST_STDERR=""
LAST_EXIT_CODE=0

# Executes a command under timeout and captures stdout, stderr, exit code
run_cmd() {
    local timeout_duration="$1"
    shift
    local stdout_file stderr_file
    stdout_file="$(mktemp)"
    stderr_file="$(mktemp)"
    
    LAST_EXIT_CODE=0
    timeout "$timeout_duration" "$@" >"$stdout_file" 2>"$stderr_file" || LAST_EXIT_CODE=$?
    
    LAST_STDOUT="$(cat "$stdout_file")"
    LAST_STDERR="$(cat "$stderr_file")"
    rm -f "$stdout_file" "$stderr_file"
}

# Assertion helper: check exit code
assert_exit_code() {
    local test_name="$1"
    local expected_type="$2" # "nonzero" or exact number e.g. "0"
    
    TOTAL=$((TOTAL + 1))
    
    if [ "$expected_type" = "nonzero" ]; then
        if [ "$LAST_EXIT_CODE" -eq 124 ]; then
            echo -e "${RED}[FAIL] ${test_name} (Process hung/timed out instead of exiting on error)${NC}"
            FAILED=$((FAILED + 1))
            return 1
        elif [ "$LAST_EXIT_CODE" -ne 0 ]; then
            echo -e "${GREEN}[PASS] ${test_name}${NC}"
            PASSED=$((PASSED + 1))
            return 0
        else
            echo -e "${RED}[FAIL] ${test_name} (Expected non-zero exit code, got 0)${NC}"
            FAILED=$((FAILED + 1))
            return 1
        fi
    else
        if [ "$LAST_EXIT_CODE" -eq "$expected_type" ]; then
            echo -e "${GREEN}[PASS] ${test_name}${NC}"
            PASSED=$((PASSED + 1))
            return 0
        else
            echo -e "${RED}[FAIL] ${test_name} (Expected exit code ${expected_type}, got ${LAST_EXIT_CODE})${NC}"
            FAILED=$((FAILED + 1))
            return 1
        fi
    fi
}

# Assertion helper: check that stderr contains expected substring (case-insensitive)
assert_stderr_contains() {
    local test_name="$1"
    local pattern="$2"
    
    TOTAL=$((TOTAL + 1))
    
    if echo "$LAST_STDERR" | grep -qi "$pattern"; then
        echo -e "${GREEN}[PASS] ${test_name} (stderr matched pattern '${pattern}')${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL] ${test_name} (stderr missing pattern '${pattern}'; got: '${LAST_STDERR}')${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Helper to check if a port can be bound (is free)
is_port_free() {
    local port="$1"
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.bind(('127.0.0.1', $port)); s.close()" 2>/dev/null
        return $?
    elif command -v nc >/dev/null 2>&1; then
        nc -z 127.0.0.1 "$port" 2>/dev/null && return 1 || return 0
    else
        return 0
    fi
}

echo -e "\n${BOLD}== IRC Server CLI & Process Lifecycle Tests ==${NC}\n"
echo -e "Testing binary: ${CYAN}${SERVER_BIN}${NC}\n"

# ==============================================================================
# 1. Argument Count Validation Matrix
# ==============================================================================
echo -e "${CYAN}--- Argument Count Validation ---${NC}"

# ./ircserv (0 args) -> exit != 0, usage printed to stderr
run_cmd 1s "$SERVER_BIN"
assert_exit_code "0 args (./ircserv): exit code != 0" "nonzero"
assert_stderr_contains "0 args (./ircserv): usage printed to stderr" "usage"

# ./ircserv 6667 (1 arg) -> exit != 0, usage printed to stderr
run_cmd 1s "$SERVER_BIN" 6667
assert_exit_code "1 arg (./ircserv 6667): exit code != 0" "nonzero"
assert_stderr_contains "1 arg (./ircserv 6667): usage printed to stderr" "usage"

# ./ircserv 6667 1234 extra_arg (3 args) -> exit != 0, usage printed to stderr
run_cmd 1s "$SERVER_BIN" 6667 1234 extra_arg
assert_exit_code "3 args (./ircserv 6667 1234 extra_arg): exit code != 0" "nonzero"
assert_stderr_contains "3 args (./ircserv 6667 1234 extra_arg): usage printed to stderr" "usage"

# ==============================================================================
# 2. Port Number Validation Matrix
# ==============================================================================
echo -e "\n${CYAN}--- Port Number Validation ---${NC}"

# Non-numeric: ./ircserv abc 1234 -> exit != 0
run_cmd 1s "$SERVER_BIN" abc 1234
assert_exit_code "Non-numeric port (./ircserv abc 1234): exit code != 0" "nonzero"
assert_stderr_contains "Non-numeric port: error printed to stderr" "error"

# Negative port: ./ircserv -1 1234 -> exit != 0
run_cmd 1s "$SERVER_BIN" -1 1234
assert_exit_code "Negative port (./ircserv -1 1234): exit code != 0" "nonzero"
assert_stderr_contains "Negative port: error printed to stderr" "error"

# Port zero: ./ircserv 0 1234 -> exit != 0
run_cmd 1s "$SERVER_BIN" 0 1234
assert_exit_code "Port zero (./ircserv 0 1234): exit code != 0" "nonzero"
assert_stderr_contains "Port zero: error printed to stderr" "error"

# Out of range: ./ircserv 70000 1234 -> exit != 0
run_cmd 1s "$SERVER_BIN" 70000 1234
assert_exit_code "Out of range port (./ircserv 70000 1234): exit code != 0" "nonzero"
assert_stderr_contains "Out of range port: error printed to stderr" "error"

# ==============================================================================
# 3. Privileged Port (< 1024 without root)
# ==============================================================================
echo -e "\n${CYAN}--- Privileged Port Validation ---${NC}"

if [ "$(id -u)" -ne 0 ]; then
    run_cmd 1s "$SERVER_BIN" 80 1234
    assert_exit_code "Privileged port without root (./ircserv 80 1234): graceful exit != 0" "nonzero"
    assert_stderr_contains "Privileged port: bind error printed to stderr" "bind"
else
    echo -e "${YELLOW}[SKIP] Running as root; skipping unprivileged port 80 test${NC}"
fi

# ==============================================================================
# 4. Port Collision (EADDRINUSE)
# ==============================================================================
echo -e "\n${CYAN}--- Port Collision (EADDRINUSE) ---${NC}"

COLLISION_PORT=16667
DUMMY_PID=""

# Start background dummy listener on COLLISION_PORT
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import socket, time; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('0.0.0.0', $COLLISION_PORT)); s.listen(1); time.sleep(10)" &
    DUMMY_PID=$!
elif command -v nc >/dev/null 2>&1; then
    nc -l -p "$COLLISION_PORT" &>/dev/null &
    DUMMY_PID=$!
fi

sleep 0.3

run_cmd 1s "$SERVER_BIN" "$COLLISION_PORT" 1234
if [ -n "$DUMMY_PID" ]; then
    kill -9 "$DUMMY_PID" 2>/dev/null || true
    wait "$DUMMY_PID" 2>/dev/null || true
fi

assert_exit_code "Port collision (EADDRINUSE): exit code != 0" "nonzero"
assert_stderr_contains "Port collision: bind error printed to stderr" "bind"

# ==============================================================================
# 5. Signal Handling & Clean Teardown Matrix (SIGINT & SIGTERM)
# ==============================================================================
echo -e "\n${CYAN}--- Signal Handling & Clean Teardown ---${NC}"

test_signal_lifecycle() {
    local sig_name="$1"
    local sig_num="$2"
    local port="$3"
    
    TOTAL=$((TOTAL + 1))
    
    # Start server in background
    "$SERVER_BIN" "$port" 1234 >/dev/null 2>&1 &
    local srv_pid=$!
    sleep 0.3
    
    if ! kill -0 "$srv_pid" 2>/dev/null; then
        echo -e "${RED}[FAIL] Signal ${sig_name}: Server failed to start on port ${port}${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Send termination signal
    kill -s "$sig_num" "$srv_pid" 2>/dev/null || true
    
    # Wait for process exit up to 2 seconds
    local exited=0
    for _ in {1..20}; do
        if ! kill -0 "$srv_pid" 2>/dev/null; then
            exited=1
            break
        fi
        sleep 0.1
    done
    
    local exit_status=0
    wait "$srv_pid" 2>/dev/null || exit_status=$?
    
    if [ "$exited" -eq 1 ]; then
        # Check that process didn't crash / dump core (clean exit: code 0 or 128+signum)
        if [ "$exit_status" -eq 0 ] || [ "$exit_status" -eq $((128 + sig_num)) ] || [ "$exit_status" -le 128 ]; then
            echo -e "${GREEN}[PASS] Clean process exit on ${sig_name} (exit status ${exit_status})${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}[FAIL] Abnormal process termination on ${sig_name} (status ${exit_status})${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        kill -9 "$srv_pid" 2>/dev/null || true
        wait "$srv_pid" 2>/dev/null || true
        echo -e "${RED}[FAIL] Server did not terminate within timeout on ${sig_name}${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    # Verify socket is immediately released (SO_REUSEADDR check)
    TOTAL=$((TOTAL + 1))
    if is_port_free "$port"; then
        echo -e "${GREEN}[PASS] Listening socket port ${port} immediately released after ${sig_name}${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}[FAIL] Port ${port} still occupied after ${sig_name} termination${NC}"
        FAILED=$((FAILED + 1))
    fi
}

test_signal_lifecycle "SIGINT" 2 16698
test_signal_lifecycle "SIGTERM" 15 16699

# ==============================================================================
# Summary
# ==============================================================================
echo -e "\n----------------------------------------"
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}Lifecycle Tests: All ${PASSED}/${TOTAL} passed.${NC}\n"
    exit 0
else
    echo -e "${RED}Lifecycle Tests: ${PASSED}/${TOTAL} passed, ${FAILED} failed.${NC}\n"
    exit 1
fi
