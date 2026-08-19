#!/usr/bin/env python3

import sys
import os
import time
import socket
import subprocess
import argparse
import threading
import signal

# ANSI Colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

def get_process_rss_kb(pid):
    """Read VmRSS in KB from /proc/<pid>/status or /proc/<pid>/statm."""
    if not pid:
        return None
    # Method 1: /proc/<pid>/status
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass

    # Method 2: /proc/<pid>/statm (pages * page_size)
    try:
        with open(f"/proc/{pid}/statm", "r") as f:
            pages = int(f.read().split()[1])
            page_size = os.sysconf("SC_PAGESIZE")
            return (pages * page_size) // 1024
    except Exception:
        pass

    return None

def find_server_pid_by_port(port):
    """Locate the server PID listening on the given port."""
    try:
        out = subprocess.check_output(
            ["ss", "-tlnp", f"sport = :{port}"],
            stderr=subprocess.DEVNULL
        ).decode()
        for line in out.splitlines():
            if f":{port}" in line and "pid=" in line:
                pid_part = line.split("pid=")[1].split(",")[0]
                return int(pid_part)
    except Exception:
        pass
    return None

def find_server_binary(custom_path=None):
    """Locate the ircserv / ft_irc binary."""
    if custom_path and os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
        return os.path.abspath(custom_path)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    for candidate in [
        os.path.join(repo_dir, "ft_irc"),
        os.path.join(repo_dir, "ircserv"),
        os.path.join(script_dir, "ft_irc"),
        os.path.join(script_dir, "ircserv"),
    ]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None

def check_server_responsive(host, port, password, timeout=1.0):
    """Assert server responds to PING within given timeout."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.sendall(f"PASS {password}\r\nNICK chk_resp\r\nUSER chk 0 * :Check\r\n".encode())
        time.sleep(0.05)
        s.sendall(b"PING :alive\r\n")
        resp = s.recv(4096).decode(errors="ignore")
        s.close()
        return ("PONG" in resp or "001" in resp)
    except Exception:
        return False

def test_unbounded_stream_and_memory(host, port, password, srv_pid, stream_mb=50, max_latency_ms=100):
    print(f"{BOLD}[TEST] Unbounded Stream & Server Memory Growth Probes ({stream_mb}MB payload without CRLF){NC}")

    initial_rss = get_process_rss_kb(srv_pid) if srv_pid else None
    if initial_rss is not None:
        print(f"       -> Baseline Server RSS: {initial_rss} KB ({initial_rss / 1024:.2f} MB)")
    else:
        print(f"       -> {YELLOW}Warning: Server PID not monitored, skipping RSS delta calculation.{NC}")

    stream_results = {
        "bytes_sent": 0,
        "disconnected_by_server": False,
        "error": None,
        "streaming_active": False,
        "finished": False
    }

    concurrent_results = {
        "success": False,
        "latency_ms": None,
        "response": None,
        "error": None
    }

    stream_started_evt = threading.Event()

    def flooder_worker():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((host, port))
            # Send initial registration header
            s.sendall(f"PASS {password}\r\nNICK flood_c1\r\nUSER flood 0 * :Flood\r\n".encode())
            time.sleep(0.05)

            stream_results["streaming_active"] = True
            stream_started_evt.set()

            # Stream payload without \r\n in 64KB blocks
            chunk = b"X" * 65536
            target_bytes = stream_mb * 1024 * 1024

            while stream_results["bytes_sent"] < target_bytes:
                try:
                    s.sendall(chunk)
                    stream_results["bytes_sent"] += len(chunk)
                except (socket.error, BrokenPipeError, ConnectionResetError) as e:
                    stream_results["disconnected_by_server"] = True
                    stream_results["error"] = str(e)
                    break

            try:
                s.close()
            except Exception:
                pass
        except Exception as e:
            stream_results["error"] = str(e)
        finally:
            stream_results["streaming_active"] = False
            stream_results["finished"] = True
            stream_started_evt.set()

    def concurrent_probe_worker():
        # Wait until flooder is actively streaming
        stream_started_evt.wait(timeout=2.0)
        time.sleep(0.05)  # Let flood saturate TCP buffers

        start_time = time.perf_counter()
        try:
            c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c2.settimeout(1.0)
            c2.connect((host, port))
            c2.sendall(f"PASS {password}\r\nNICK c2_probe\r\nUSER c2 0 * :Probe\r\n".encode())
            c2.sendall(b"PING :probe_ping\r\n")

            buf = ""
            while True:
                data = c2.recv(4096)
                if not data:
                    break
                buf += data.decode(errors="ignore")
                if "PONG" in buf or ":probe_ping" in buf:
                    break
                if time.perf_counter() - start_time > 1.0:
                    break

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            concurrent_results["latency_ms"] = elapsed_ms
            concurrent_results["response"] = buf

            if "PONG" in buf or ":probe_ping" in buf or "001" in buf:
                concurrent_results["success"] = True
            else:
                concurrent_results["error"] = f"No PONG received. Received: {repr(buf)}"
            c2.close()
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            concurrent_results["latency_ms"] = elapsed_ms
            concurrent_results["error"] = str(e)

    # Launch threads
    t_flood = threading.Thread(target=flooder_worker, daemon=True)
    t_probe = threading.Thread(target=concurrent_probe_worker, daemon=True)

    t_flood.start()
    t_probe.start()

    t_flood.join(timeout=15.0)
    t_probe.join(timeout=5.0)

    # Post-flood memory sample
    time.sleep(0.2)
    post_rss = get_process_rss_kb(srv_pid) if srv_pid else None

    # Evaluate checks
    passed_checks = True
    print(f"\n{BOLD}--- Probe Diagnostic Results ---{NC}")

    # Check 1 & Check 2: Stream containment & Memory bounds
    sent_kb = stream_results["bytes_sent"] // 1024
    if stream_results["disconnected_by_server"]:
        print(f"       [{GREEN}PASS{NC}] Check 1: Server actively dropped/disconnected flooding client after {sent_kb} KB (Safety Ceiling)")
    else:
        print(f"       [{CYAN}INFO{NC}] Server buffered/received {sent_kb} KB of continuous stream.")

    if initial_rss is not None and post_rss is not None:
        delta_kb = post_rss - initial_rss
        delta_mb = delta_kb / 1024.0
        print(f"       Post-Stream Server RSS: {post_rss} KB ({post_rss / 1024:.2f} MB), Delta: {delta_kb} KB ({delta_mb:.2f} MB)")
        
        # Memory Threshold: Server RSS delta must not exceed 5MB
        if delta_mb < 5.0:
            print(f"       [{GREEN}PASS{NC}] Check 2: Server memory delta {delta_mb:.2f} MB is within safety threshold (< 5.0 MB)")
        else:
            print(f"       [{RED}FAIL{NC}] Check 2: Server memory grew by {delta_mb:.2f} MB (Threshold: < 5.0 MB, unbounded growth detected)")
            passed_checks = False
    elif initial_rss is not None and post_rss is None:
        print(f"       [{RED}FAIL{NC}] Server crashed during memory test!")
        passed_checks = False

    # Concurrent Responsiveness Check
    if concurrent_results["success"]:
        lat = concurrent_results["latency_ms"]
        if lat <= max_latency_ms:
            print(f"       [{GREEN}PASS{NC}] Concurrency Check: Connection C2 registered and executed PING/PONG in {lat:.2f} ms (<= {max_latency_ms} ms)")
        else:
            print(f"       [{YELLOW}WARN{NC}] Concurrency Check: Connection C2 responded in {lat:.2f} ms (> {max_latency_ms} ms threshold under flood)")
    else:
        print(f"       [{RED}FAIL{NC}] Concurrency Check: Connection C2 failed to execute PING/PONG during flood: {concurrent_results['error']}")
        passed_checks = False

    # Server post-test liveness verification
    is_alive = check_server_responsive(host, port, password, timeout=1.5)
    if is_alive:
        print(f"       [{GREEN}PASS{NC}] Server Liveness: Server remains responsive after stream probe execution.")
    else:
        print(f"       [{RED}FAIL{NC}] Server Liveness: Server became unresponsive after stream probe!")
        passed_checks = False

    print("----------------------------------------")
    return passed_checks

def main():
    parser = argparse.ArgumentParser(description="IRC Server Memory & Slowloris Probe")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=6667, help="Server port (default: 6667)")
    parser.add_argument("--password", "-p", default="1234", help="Server password (default: 1234)")
    parser.add_argument("--pid", type=int, default=None, help="Server PID (detected via port if omitted)")
    parser.add_argument("--stream-mb", type=int, default=50, help="Continuous payload size in MB without CRLF (default: 50)")
    parser.add_argument("--latency-ms", type=int, default=100, help="Max allowed latency in ms for concurrent connection C2 (default: 100)")
    parser.add_argument("--server-bin", default=None, help="Path to server binary to launch if not running")
    args = parser.parse_args()

    print(f"\n{BOLD}== IRC Server Memory & Stream Flood Probes =={NC}\n")

    launched_process = None
    srv_pid = args.pid or find_server_pid_by_port(args.port)

    try:
        # If server is not running, launch it automatically
        if not srv_pid and not check_server_responsive(args.host, args.port, args.password, timeout=0.3):
            server_bin = find_server_binary(args.server_bin)
            if not server_bin:
                print(f"{RED}Error: Server is not running and no server binary was found to launch.{NC}")
                print("Please build the server or specify --server-bin <path>.")
                sys.exit(1)

            print(f"Launching server: {server_bin} {args.port} {args.password}")
            launched_process = subprocess.Popen(
                [server_bin, str(args.port), args.password],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            srv_pid = launched_process.pid
            time.sleep(0.3)

            # Wait for server to become responsive
            started = False
            for _ in range(20):
                if check_server_responsive(args.host, args.port, args.password, timeout=0.2):
                    started = True
                    break
                time.sleep(0.1)

            if not started:
                print(f"{RED}Error: Launched server process (PID {srv_pid}) failed to respond on port {args.port}.{NC}")
                sys.exit(1)

        if srv_pid:
            print(f"Monitoring server PID: {srv_pid}")
        else:
            print(f"{YELLOW}Warning: Server PID could not be determined; RSS delta checks will be skipped.{NC}")

        # Run test
        success = test_unbounded_stream_and_memory(
            host=args.host,
            port=args.port,
            password=args.password,
            srv_pid=srv_pid,
            stream_mb=args.stream_mb,
            max_latency_ms=args.latency_ms
        )

        if success:
            print(f"{GREEN}{BOLD}Memory & Stream Probes Passed Successfully!{NC}\n")
            sys.exit(0)
        else:
            print(f"{RED}{BOLD}Memory & Stream Probes Failed.{NC}\n")
            sys.exit(1)

    finally:
        if launched_process:
            print(f"Terminating test server instance (PID {launched_process.pid})...")
            try:
                launched_process.terminate()
                launched_process.wait(timeout=1.0)
            except Exception:
                launched_process.kill()

if __name__ == "__main__":
    main()
