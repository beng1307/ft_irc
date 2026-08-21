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
        os.path.join(repo_dir, "ircserv"),
        os.path.join(repo_dir, "ft_irc"),
        os.path.join(script_dir, "ircserv"),
        os.path.join(script_dir, "ft_irc"),
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

def test_outbound_backpressure_and_memory(host, port, password, srv_pid, flood_count=5000, max_latency_ms=150):
    print(f"\n{BOLD}[TEST] Outbound Write Backpressure & Send Buffer Growth Probes ({flood_count} messages){NC}")

    initial_rss = get_process_rss_kb(srv_pid) if srv_pid else None
    if initial_rss is not None:
        print(f"       -> Baseline Server RSS: {initial_rss} KB ({initial_rss / 1024:.2f} MB)")
    else:
        print(f"       -> {YELLOW}Warning: Server PID not monitored, skipping RSS delta calculation.{NC}")

    passed_checks = True

    try:
        # C1: Flooder, C2: Slow/Backpressured client (small rcvbuf, paused reads), C3: Concurrent probe
        c1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        c1.settimeout(5.0)
        c2.settimeout(5.0)
        c3.settimeout(5.0)

        # Connect and register clients
        c1.connect((host, port))
        c1.sendall(f"PASS {password}\r\nNICK bp_alice\r\nUSER bp_alice 0 * :Alice\r\nJOIN #bptest\r\n".encode())

        c2.connect((host, port))
        c2.sendall(f"PASS {password}\r\nNICK bp_bob\r\nUSER bp_bob 0 * :Bob\r\nJOIN #bptest\r\n".encode())

        c3.connect((host, port))
        c3.sendall(f"PASS {password}\r\nNICK bp_charlie\r\nUSER bp_charlie 0 * :Charlie\r\nJOIN #bptest\r\n".encode())

        # Wait for registration and joins to settle
        time.sleep(0.2)
        # Drain initial registration/join bursts
        c1.setblocking(False)
        c2.setblocking(False)
        c3.setblocking(False)
        for c in [c1, c2, c3]:
            try:
                while c.recv(8192):
                    pass
            except Exception:
                pass
        c1.setblocking(True)
        c2.setblocking(True)
        c3.setblocking(True)

        # Throttle C2 TCP receive buffer to 1024 bytes and pause reading on C2
        try:
            c2.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
        except Exception as e:
            print(f"       [{YELLOW}WARN{NC}] setsockopt SO_RCVBUF failed: {e}")

        payload_line = "PRIVMSG #bptest :" + ("A" * 300) + "\r\n"
        payload_bytes = payload_line.encode()

        print(f"       -> Flooding {flood_count} large broadcast messages while C2 receive is paused...")
        messages_sent = 0
        c1_start = time.perf_counter()
        for _ in range(flood_count):
            try:
                c1.sendall(payload_bytes)
                messages_sent += 1
            except Exception as e:
                print(f"       [{YELLOW}WARN{NC}] Flooder sendall error at msg {messages_sent}: {e}")
                break

        # Check server responsiveness on C3 while C2's server send queue is full
        start_c3 = time.perf_counter()
        c3.sendall(b"PING :bp_alive_check\r\n")
        c3_buf = ""
        c3.settimeout(1.5)
        try:
            while True:
                data = c3.recv(4096)
                if not data:
                    break
                c3_buf += data.decode(errors="ignore")
                if "PONG" in c3_buf or ":bp_alive_check" in c3_buf:
                    break
                if time.perf_counter() - start_c3 > 1.5:
                    break
        except Exception as e:
            c3_buf += f" [Error: {e}]"

        c3_latency = (time.perf_counter() - start_c3) * 1000.0

        # Sample memory under full backpressure queue
        post_flood_rss = get_process_rss_kb(srv_pid) if srv_pid else None

        # Resume reading on C2 and drain messages
        c2.settimeout(0.5)
        c2_received_bytes = 0
        c2_drain_start = time.perf_counter()
        while time.perf_counter() - c2_drain_start < 2.0:
            try:
                data = c2.recv(16384)
                if not data:
                    break
                c2_received_bytes += len(data)
            except socket.timeout:
                break
            except Exception:
                break

        # Cleanup test sockets
        try:
            c1.close()
            c2.close()
            c3.close()
        except Exception:
            pass

        time.sleep(0.2)
        final_rss = get_process_rss_kb(srv_pid) if srv_pid else None

        # Evaluate diagnostic results
        print(f"\n{BOLD}--- Backpressure Diagnostic Results ---{NC}")
        print(f"       Messages Broadcast: {messages_sent}/{flood_count} ({messages_sent * len(payload_bytes) // 1024} KB)")
        print(f"       C2 Drained: {c2_received_bytes // 1024} KB after resuming")

        if initial_rss is not None and post_flood_rss is not None:
            delta_kb = post_flood_rss - initial_rss
            delta_mb = delta_kb / 1024.0
            print(f"       Peak Outbound Queue Server RSS: {post_flood_rss} KB ({post_flood_rss / 1024:.2f} MB), Delta: {delta_kb} KB ({delta_mb:.2f} MB)")
            if delta_mb < 20.0:
                print(f"       [{GREEN}PASS{NC}] Check 1: Outbound buffer memory delta {delta_mb:.2f} MB is within threshold (< 20.0 MB)")
            else:
                print(f"       [{RED}FAIL{NC}] Check 1: Excessive memory growth during backpressure: {delta_mb:.2f} MB")
                passed_checks = False

        if "PONG" in c3_buf or ":bp_alive_check" in c3_buf:
            if c3_latency <= max_latency_ms:
                print(f"       [{GREEN}PASS{NC}] Check 2: Independent client C3 responded in {c3_latency:.2f} ms (<= {max_latency_ms} ms)")
            else:
                print(f"       [{YELLOW}WARN{NC}] Check 2: Independent client C3 responded in {c3_latency:.2f} ms (> {max_latency_ms} ms)")
        else:
            print(f"       [{RED}FAIL{NC}] Check 2: Independent client C3 failed to get PONG during backpressure (Latency: {c3_latency:.2f} ms)")
            passed_checks = False

        is_alive = check_server_responsive(host, port, password, timeout=1.5)
        if is_alive:
            print(f"       [{GREEN}PASS{NC}] Server Liveness: Server remains responsive after backpressure drain.")
        else:
            print(f"       [{RED}FAIL{NC}] Server Liveness: Server became unresponsive after backpressure drain!")
            passed_checks = False

        print("----------------------------------------")
        return passed_checks

    except Exception as e:
        print(f"       [{RED}FAIL{NC}] Backpressure test encountered an unexpected exception: {e}")
        return False

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

        # Run inbound stream & memory test
        success_stream = test_unbounded_stream_and_memory(
            host=args.host,
            port=args.port,
            password=args.password,
            srv_pid=srv_pid,
            stream_mb=args.stream_mb,
            max_latency_ms=args.latency_ms
        )

        # Run outbound backpressure & memory test
        success_bp = test_outbound_backpressure_and_memory(
            host=args.host,
            port=args.port,
            password=args.password,
            srv_pid=srv_pid
        )

        if success_stream and success_bp:
            print(f"\n{GREEN}{BOLD}All Memory, Stream & Backpressure Probes Passed Successfully!{NC}\n")
            sys.exit(0)
        else:
            print(f"\n{RED}{BOLD}Memory, Stream & Backpressure Probes Failed.{NC}\n")
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
