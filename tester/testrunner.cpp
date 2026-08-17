#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <poll.h>
#include <sys/time.h>
#include <signal.h>
#include <netinet/tcp.h>
#include "../helpers/print.hpp"

// -----------------------------------------------------------------------------
// Glob Pattern Matching Helper
// -----------------------------------------------------------------------------
static bool glob_match(const char* pat, const char* str) {
    if (!*pat) return !*str;
    if (*pat == '*') {
        return glob_match(pat + 1, str) || (*str && glob_match(pat, str + 1));
    }
    if (*str && (*pat == *str)) {
        return glob_match(pat + 1, str + 1);
    }
    return false;
}

static bool match_pattern(const std::string& line, const std::string& pattern) {
    // 1. Direct glob match
    if (glob_match(pattern.c_str(), line.c_str())) return true;

    // 2. Glob match with leading wildcard (* + pattern)
    std::string wildcard_prefix = "*" + pattern;
    if (glob_match(wildcard_prefix.c_str(), line.c_str())) return true;

    // 3. Glob match surrounded (* + pattern + *)
    std::string wildcard_both = "*" + pattern + "*";
    if (glob_match(wildcard_both.c_str(), line.c_str())) return true;

    return false;
}

// -----------------------------------------------------------------------------
// Time & Helper Utilities
// -----------------------------------------------------------------------------
static long get_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec * 1000L) + (tv.tv_usec / 1000L);
}

static void trim(std::string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) {
        s.clear();
        return;
    }
    size_t end = s.find_last_not_of(" \t\r\n");
    s = s.substr(start, end - start + 1);
}

// Parse duration like "500ms" or "2s" or "1000" into milliseconds
static int parse_duration_ms(const std::string& s) {
    std::string str = s;
    trim(str);
    int multiplier = 1;
    if (str.length() > 2 && str.substr(str.length() - 2) == "ms") {
        str = str.substr(0, str.length() - 2);
    } else if (str.length() > 1 && str[str.length() - 1] == 's') {
        str = str.substr(0, str.length() - 1);
        multiplier = 1000;
    }
    return atoi(str.c_str()) * multiplier;
}

// Decode the small escape vocabulary used in .spec files for SEND_RAW.
// Keeping the source specs printable makes fragmented IRC frames readable.
static std::string decode_raw_escapes(const std::string& input) {
    std::string output;
    for (size_t i = 0; i < input.size(); ++i) {
        if (input[i] == '\\' && i + 1 < input.size()) {
            char escaped = input[i + 1];
            if (escaped == 'r') { output += '\r'; ++i; continue; }
            if (escaped == 'n') { output += '\n'; ++i; continue; }
            if (escaped == '\\') { output += '\\'; ++i; continue; }
        }
        output += input[i];
    }
    return output;
}

// -----------------------------------------------------------------------------
// Logger
// -----------------------------------------------------------------------------
class TestLogger {
public:
    std::ofstream log_file;
    std::string spec_name;
    bool verbose;

    TestLogger() : verbose(false) {}

    bool init(const std::string& spec_path, bool v = false) {
        verbose = v;
        size_t last_slash = spec_path.find_last_of("/\\");
        std::string filename = (last_slash == std::string::npos) ? spec_path : spec_path.substr(last_slash + 1);
        size_t last_dot = filename.find_last_of('.');
        spec_name = (last_dot == std::string::npos) ? filename : filename.substr(0, last_dot);
        
        mkdir("logs", 0755);
        std::string log_filename = "logs/" + spec_name + ".log";

        log_file.open(log_filename.c_str(), std::ios::out | std::ios::trunc);
        return log_file.is_open();
    }

    void log(const std::string& client, const std::string& type, const std::string& text) {
        std::string line = client + " " + type + " " + text;
        if (log_file.is_open()) {
            log_file << line << "\n";
            log_file.flush();
        }
        if (verbose) {
            print(line);
        }
    }
};

// -----------------------------------------------------------------------------
// Virtual Client State
// -----------------------------------------------------------------------------
struct VirtualClient {
    std::string id;
    int fd;
    bool connected;
    std::string recv_buf;
    std::vector<std::string> line_queue;
    bool reading;

    VirtualClient() : fd(-1), connected(false), reading(true) {}
};

// -----------------------------------------------------------------------------
// Directives Enum & Struct
// -----------------------------------------------------------------------------
enum DirectiveType {
    DIR_CLIENTS,
    DIR_SEND,
    DIR_SEND_RAW,
    DIR_EXPECT,
    DIR_WAIT_RECV,
    DIR_WAIT,
    DIR_EXPECT_DISCONNECT,
    DIR_EXPECT_CONNECTED,
    DIR_EXPECT_NONE,
    DIR_EXPECT_COUNT,
    DIR_CLOSE_SOCKET,
    DIR_CLOSE_WRITE,
    DIR_RESET,
    DIR_RECONNECT,
    DIR_PAUSE,
    DIR_RESUME,
    DIR_FLOOD,
    DIR_TIMEOUT,
    DIR_UNKNOWN
};

struct Instruction {
    DirectiveType type;
    std::string client_id;
    std::string payload;
    std::string original_line;
    int line_number;
    Instruction() : type(DIR_UNKNOWN), line_number(0) {}
};

// -----------------------------------------------------------------------------
// TestRunner Engine
// -----------------------------------------------------------------------------
class TestRunner {
private:
    std::string host;
    int port;
    int timeout_ms;
    TestLogger logger;
    std::map<std::string, VirtualClient> clients;
    std::vector<std::string> client_order;

public:
    TestRunner(const std::string& h, int p) : host(h), port(p), timeout_ms(3000) {}

    ~TestRunner() {
        cleanup();
    }

    void cleanup() {
        bool had_connected = false;
        for (std::map<std::string, VirtualClient>::iterator it = clients.begin(); it != clients.end(); ++it) {
            if (it->second.fd != -1) {
                close(it->second.fd);
                it->second.fd = -1;
                had_connected = true;
            }
            it->second.connected = false;
        }
        if (had_connected) {
            usleep(100000);
        }
    }

    bool connect_client(const std::string& client_id) {
        int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_fd < 0) {
            logger.log(client_id, "ERROR", "Failed to create socket");
            return false;
        }

        // Set non-blocking
        int flags = fcntl(socket_fd, F_GETFL, 0);
        if (flags != -1) {
            fcntl(socket_fd, F_SETFL, flags | O_NONBLOCK);
        }

        struct sockaddr_in serv_addr;
        std::memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);

        if (inet_pton(AF_INET, host.c_str(), &serv_addr.sin_addr) <= 0) {
            struct hostent* he = gethostbyname(host.c_str());
            if (!he) {
                logger.log(client_id, "ERROR", "Invalid address: " + host);
                close(socket_fd);
                return false;
            }
            std::memcpy(&serv_addr.sin_addr, he->h_addr_list[0], he->h_length);
        }

        int res = connect(socket_fd, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
        if (res < 0 && errno != EINPROGRESS) {
            logger.log(client_id, "ERROR", "Connection failed to " + host);
            close(socket_fd);
            return false;
        }

        // Poll to confirm non-blocking connection
        struct pollfd pfd;
        pfd.fd = socket_fd;
        pfd.events = POLLOUT;
        int poll_res = poll(&pfd, 1, timeout_ms);
        if (poll_res <= 0) {
            logger.log(client_id, "ERROR", "Connection timed out to " + host);
            close(socket_fd);
            return false;
        }

        int err = 0;
        socklen_t len = sizeof(err);
        getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &err, &len);
        if (err != 0) {
            logger.log(client_id, "ERROR", "Socket error on connect: " + std::string(strerror(err)));
            close(socket_fd);
            return false;
        }

        VirtualClient& vc = clients[client_id];
        vc.id = client_id;
        vc.fd = socket_fd;
        vc.connected = true;
        std::ostringstream oss;
        oss << port;
        logger.log(client_id, "SYS", "Connected to " + host + ":" + oss.str());
        return true;
    }

    void poll_all_clients(int wait_ms) {
        long start_time = get_time_ms();
        while (true) {
            std::vector<struct pollfd> pfds;
            std::vector<std::string> ids;

            for (std::map<std::string, VirtualClient>::iterator it = clients.begin(); it != clients.end(); ++it) {
                if (it->second.connected && it->second.fd != -1 && it->second.reading) {
                    struct pollfd pfd;
                    pfd.fd = it->second.fd;
                    pfd.events = POLLIN;
                    pfd.revents = 0;
                    pfds.push_back(pfd);
                    ids.push_back(it->first);
                }
            }

            if (pfds.empty()) {
                long elapsed = get_time_ms() - start_time;
                if (elapsed < wait_ms) {
                    usleep((wait_ms - elapsed) * 1000);
                }
                break;
            }

            long elapsed = get_time_ms() - start_time;
            long remaining = wait_ms - elapsed;
            if (remaining <= 0) remaining = 0;

            int ret = poll(&pfds[0], pfds.size(), remaining);
            if (ret > 0) {
                for (size_t i = 0; i < pfds.size(); ++i) {
                    if (pfds[i].revents & (POLLIN | POLLHUP | POLLERR)) {
                        read_client(clients[ids[i]]);
                    }
                }
            }

            if (get_time_ms() - start_time >= wait_ms) {
                break;
            }
            if (ret == 0 && remaining == 0) {
                break;
            }
        }
    }

    void read_client(VirtualClient& vc) {
        if (!vc.connected || vc.fd == -1 || !vc.reading) return;

        char buf[1024];
        ssize_t bytes = recv(vc.fd, buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            vc.recv_buf.append(buf, bytes);

            size_t pos;
            while ((pos = vc.recv_buf.find('\n')) != std::string::npos) {
                std::string line = vc.recv_buf.substr(0, pos);
                vc.recv_buf.erase(0, pos + 1);
                trim(line);
                if (!line.empty()) {
                    vc.line_queue.push_back(line);
                    logger.log(vc.id, "RECV", line);
                }
            }
        } else if (bytes == 0 || (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) {
            vc.connected = false;
            logger.log(vc.id, "SYS", "Disconnected");
        }
    }

    bool pop_next_line(VirtualClient& vc, std::string& line, int max_wait_ms) {
        long start = get_time_ms();
        while (true) {
            if (!vc.line_queue.empty()) {
                line = vc.line_queue.front();
                vc.line_queue.erase(vc.line_queue.begin());
                return true;
            }
            read_client(vc);
            if (!vc.line_queue.empty()) {
                line = vc.line_queue.front();
                vc.line_queue.erase(vc.line_queue.begin());
                return true;
            }
            if (!vc.connected) return false;

            long elapsed = get_time_ms() - start;
            if (elapsed >= max_wait_ms) break;

            poll_all_clients(50);
        }
        return false;
    }

    bool wait_for_pattern(VirtualClient& vc, const std::string& pattern, int max_wait_ms) {
        long start = get_time_ms();
        while (true) {
            poll_all_clients(10);

            for (size_t i = 0; i < vc.line_queue.size(); ++i) {
                if (match_pattern(vc.line_queue[i], pattern)) {
                    vc.line_queue.erase(vc.line_queue.begin(), vc.line_queue.begin() + i + 1);
                    return true;
                }
            }

            if (!vc.connected) return false;

            long elapsed = get_time_ms() - start;
            if (elapsed >= max_wait_ms) break;
        }
        return false;
    }

    bool send_raw(VirtualClient& vc, const std::string& data) {
        if (!vc.connected || vc.fd == -1) {
            logger.log(vc.id, "ERROR", "Cannot send data: socket not connected");
            return false;
        }
        size_t sent = 0;
        while (sent < data.length()) {
            ssize_t res = send(vc.fd, data.c_str() + sent, data.length() - sent, MSG_NOSIGNAL);
            if (res > 0) { sent += static_cast<size_t>(res); continue; }
            if (res < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
                struct pollfd pfd; pfd.fd = vc.fd; pfd.events = POLLOUT; pfd.revents = 0;
                if (poll(&pfd, 1, timeout_ms) <= 0) res = -1;
                else continue;
            }
            logger.log(vc.id, "ERROR", "Failed to send data: " + std::string(strerror(errno)));
            vc.connected = false;
            return false;
        }
        return true;
    }

    void close_client(VirtualClient& vc, bool reset) {
        if (vc.fd == -1) return;
        if (reset) {
            struct linger linger_opt; linger_opt.l_onoff = 1; linger_opt.l_linger = 0;
            setsockopt(vc.fd, SOL_SOCKET, SO_LINGER, &linger_opt, sizeof(linger_opt));
        }
        close(vc.fd); vc.fd = -1; vc.connected = false; vc.reading = true;
        logger.log(vc.id, "SYS", reset ? "Peer reset" : "Peer closed");
    }

    bool assert_none(VirtualClient& vc, int quiet_ms) {
        poll_all_clients(quiet_ms);
        if (!vc.line_queue.empty()) return false;
        return vc.connected;
    }

    int count_matching(VirtualClient& vc, const std::string& pattern) {
        int count = 0;
        for (size_t i = 0; i < vc.line_queue.size(); ++i)
            if (match_pattern(vc.line_queue[i], pattern)) ++count;
        return count;
    }

    bool run_spec(const std::string& spec_path, bool verbose = false) {
        if (!logger.init(spec_path, verbose)) {
            printErr("Error: Could not create log file for ", spec_path);
            return false;
        }

        std::ifstream spec_file(spec_path.c_str());
        if (!spec_file.is_open()) {
            printErr("Error: Could not open spec file ", spec_path);
            return false;
        }

        std::vector<Instruction> instructions;
        std::string line;
        int line_num = 0;

        while (std::getline(spec_file, line)) {
            line_num++;
            std::string trimmed = line;
            trim(trimmed);
            if (trimmed.empty() || trimmed[0] == '#') continue;

            Instruction inst;
            inst.original_line = line;
            inst.line_number = line_num;

            std::istringstream iss(trimmed);
            std::string token1;
            iss >> token1;

            if (token1 == "CLIENTS") {
                inst.type = DIR_CLIENTS;
                std::string rest;
                std::getline(iss, rest);
                inst.payload = rest;
            } else if (token1 == "WAIT") {
                inst.type = DIR_WAIT;
                iss >> inst.payload;
            } else if (token1 == "TIMEOUT") {
                inst.type = DIR_TIMEOUT;
                iss >> inst.payload;
            } else {
                inst.client_id = token1;
                std::string token2;
                iss >> token2;

                if (token2 == "EXPECT_DISCONNECT") {
                    inst.type = DIR_EXPECT_DISCONNECT;
                } else if (token2 == "EXPECT_CONNECTED") {
                    inst.type = DIR_EXPECT_CONNECTED;
                } else if (token2 == "EXPECT_NONE") {
                    inst.type = DIR_EXPECT_NONE;
                    iss >> inst.payload;
                    if (inst.payload.empty()) inst.payload = "200ms";
                } else if (token2 == "EXPECT_COUNT") {
                    inst.type = DIR_EXPECT_COUNT;
                    std::getline(iss, inst.payload); trim(inst.payload);
                } else if (token2 == "SEND_RAW") {
                    inst.type = DIR_SEND_RAW;
                    std::getline(iss, inst.payload); if (!inst.payload.empty() && inst.payload[0] == ' ') inst.payload.erase(0, 1);
                } else if (token2 == "CLOSE_SOCKET" || token2 == "CLOSE_WRITE" || token2 == "RESET" || token2 == "RECONNECT" || token2 == "PAUSE" || token2 == "RESUME") {
                    inst.type = token2 == "CLOSE_SOCKET" ? DIR_CLOSE_SOCKET : token2 == "CLOSE_WRITE" ? DIR_CLOSE_WRITE : token2 == "RESET" ? DIR_RESET : token2 == "RECONNECT" ? DIR_RECONNECT : token2 == "PAUSE" ? DIR_PAUSE : DIR_RESUME;
                } else if (token2 == "FLOOD") {
                    inst.type = DIR_FLOOD;
                    std::getline(iss, inst.payload); trim(inst.payload);
                } else if (token2 == "EXPECT") {
                    inst.type = DIR_EXPECT;
                    std::string rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else if (token2 == "WAIT_RECV") {
                    inst.type = DIR_WAIT_RECV;
                    std::string rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else if (token2 == "SEND") {
                    inst.type = DIR_SEND;
                    std::string rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else {
                    inst.type = DIR_UNKNOWN;
                }
            }
            instructions.push_back(inst);
        }

        // Execute instructions
        for (size_t i = 0; i < instructions.size(); ++i) {
            Instruction& inst = instructions[i];

            if (inst.type == DIR_CLIENTS) {
                std::istringstream css(inst.payload);
                std::string cid;
                while (std::getline(css, cid, ',')) {
                    trim(cid);
                    if (!cid.empty()) {
                        client_order.push_back(cid);
                        clients[cid] = VirtualClient();
                        if (!connect_client(cid)) {
                            printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": Failed to connect client ", cid);
                            return false;
                        }
                    }
                }
            } else if (inst.type == DIR_WAIT) {
                int duration = parse_duration_ms(inst.payload);
                poll_all_clients(duration);
            } else if (inst.type == DIR_TIMEOUT) {
                timeout_ms = parse_duration_ms(inst.payload);
                if (timeout_ms <= 0) timeout_ms = 1;
            } else if (inst.type == DIR_EXPECT_DISCONNECT) {
                VirtualClient& vc = clients[inst.client_id];
                poll_all_clients(200);
                if (vc.connected) {
                    logger.log(inst.client_id, "ERROR", "Expected socket disconnect, but socket is still connected");
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " expected disconnect but is connected");
                    return false;
                }
                logger.log(inst.client_id, "SYS", "Asserted DISCONNECTED successfully");
            } else if (inst.type == DIR_EXPECT_CONNECTED) {
                VirtualClient& vc = clients[inst.client_id];
                poll_all_clients(200);
                if (!vc.connected) {
                    logger.log(inst.client_id, "ERROR", "Expected socket connected, but socket is closed");
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " expected connected but is disconnected");
                    return false;
                }
                logger.log(inst.client_id, "SYS", "Asserted CONNECTED successfully");
            } else if (inst.type == DIR_SEND_RAW) {
                VirtualClient& vc = clients[inst.client_id];
                logger.log(inst.client_id, "SEND_RAW", inst.payload);
                if (!send_raw(vc, decode_raw_escapes(inst.payload))) {
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": SEND_RAW failed for ", inst.client_id);
                    return false;
                }
            } else if (inst.type == DIR_CLOSE_SOCKET || inst.type == DIR_RESET) {
                close_client(clients[inst.client_id], inst.type == DIR_RESET);
            } else if (inst.type == DIR_CLOSE_WRITE) {
                VirtualClient& vc = clients[inst.client_id];
                if (vc.fd != -1) { shutdown(vc.fd, SHUT_WR); logger.log(vc.id, "SYS", "Write half-closed"); }
            } else if (inst.type == DIR_RECONNECT) {
                VirtualClient& vc = clients[inst.client_id];
                close_client(vc, false);
                if (!connect_client(inst.client_id)) {
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": Failed to reconnect client ", inst.client_id);
                    return false;
                }
            } else if (inst.type == DIR_PAUSE || inst.type == DIR_RESUME) {
                clients[inst.client_id].reading = (inst.type == DIR_RESUME);
                logger.log(inst.client_id, "SYS", inst.type == DIR_RESUME ? "Reading resumed" : "Reading paused");
            } else if (inst.type == DIR_FLOOD) {
                VirtualClient& vc = clients[inst.client_id];
                std::istringstream fs(inst.payload); int count = 0; fs >> count;
                std::string payload; std::getline(fs, payload); trim(payload);
                if (count < 1 || count > 10000 || payload.empty()) {
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": Invalid FLOOD parameters: ", inst.payload);
                    return false;
                }
                for (int n = 0; n < count; ++n) {
                    if (!send_raw(vc, payload + "\r\n")) {
                        printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": FLOOD send failed for ", inst.client_id);
                        return false;
                    }
                }
                logger.log(inst.client_id, "FLOOD", payload);
            } else if (inst.type == DIR_SEND) {
                VirtualClient& vc = clients[inst.client_id];
                logger.log(inst.client_id, "SEND", inst.payload);
                if (!send_raw(vc, inst.payload + "\r\n")) {
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": Send failed for ", inst.client_id);
                    return false;
                }
            } else if (inst.type == DIR_EXPECT) {
                VirtualClient& vc = clients[inst.client_id];
                if (!wait_for_pattern(vc, inst.payload, timeout_ms)) {
                    logger.log(inst.client_id, "ERROR", "EXPECT assertion failed for pattern: " + inst.payload);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": EXPECT assertion failed for ", inst.client_id, " pattern: ", inst.payload);
                    return false;
                }
            } else if (inst.type == DIR_EXPECT_NONE) {
                VirtualClient& vc = clients[inst.client_id];
                if (!assert_none(vc, parse_duration_ms(inst.payload))) {
                    logger.log(inst.client_id, "ERROR", "EXPECT_NONE observed queued data or disconnect");
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": EXPECT_NONE observed queued data or disconnect");
                    return false;
                }
            } else if (inst.type == DIR_EXPECT_COUNT) {
                VirtualClient& vc = clients[inst.client_id]; std::istringstream es(inst.payload);
                int expected = 0; es >> expected; std::string pattern; std::getline(es, pattern); trim(pattern);
                poll_all_clients(timeout_ms);
                if (count_matching(vc, pattern) != expected) {
                    logger.log(inst.client_id, "ERROR", "EXPECT_COUNT mismatch: " + inst.payload);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": EXPECT_COUNT mismatch: ", inst.payload);
                    return false;
                }
            } else if (inst.type == DIR_WAIT_RECV) {
                VirtualClient& vc = clients[inst.client_id];
                if (!wait_for_pattern(vc, inst.payload, timeout_ms)) {
                    logger.log(inst.client_id, "ERROR", "WAIT_RECV timeout matching pattern: " + inst.payload);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": WAIT_RECV timeout for ", inst.client_id, " pattern: ", inst.payload);
                    return false;
                }
            }
        }

        print("PASS [", logger.spec_name, "]");
        return true;
    }
};

// -----------------------------------------------------------------------------
// CLI Main
// -----------------------------------------------------------------------------
int main(int argc, char* argv[]) {
    std::string host = "127.0.0.1";
    int port = 6667;
    std::string spec_path = "";
    bool verbose = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--host" && i + 1 < argc) {
            host = argv[++i];
        } else if (arg == "--port" && i + 1 < argc) {
            port = atoi(argv[++i]);
        } else if (arg == "--v" || arg == "-v" || arg == "--verbose") {
            verbose = true;
        } else if (arg[0] != '-') {
            spec_path = arg;
        }
    }

    if (spec_path.empty()) {
        print("Usage: testrunner [--host <host>] [--port <port>] [--v] <spec_file>");
        return 1;
    }

    TestRunner runner(host, port);
    if (!runner.run_spec(spec_path, verbose)) {
        return 1;
    }
    return 0;
}
