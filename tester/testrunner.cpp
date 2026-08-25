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
#include <netinet/tcp.h>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"

// -----------------------------------------------------------------------------
// Glob Pattern Matching Helper
// -----------------------------------------------------------------------------
static bool glob_match(const char* pat, const char* pat_end, const char* str, const char* str_end) {
    if (pat == pat_end) return str == str_end;
    if (*pat == '*') {
        return glob_match(pat + 1, pat_end, str, str_end) || (str != str_end && glob_match(pat, pat_end, str + 1, str_end));
    }
    if (str != str_end && (*pat == *str)) {
        return glob_match(pat + 1, pat_end, str + 1, str_end);
    }
    return false;
}

static bool match_pattern(const Wire& line, const Wire& pattern) {
    // 1. Direct glob match
    if (glob_match(pattern.data(), pattern.data() + pattern.size(), line.data(), line.data() + line.size())) return true;

    // 2. Glob match with leading wildcard (* + pattern)
    Wire wildcard_prefix = "*" + pattern;
    if (glob_match(wildcard_prefix.data(), wildcard_prefix.data() + wildcard_prefix.size(), line.data(), line.data() + line.size())) return true;

    // 3. Glob match surrounded (* + pattern + *)
    Wire wildcard_both = "*" + pattern + "*";
    if (glob_match(wildcard_both.data(), wildcard_both.data() + wildcard_both.size(), line.data(), line.data() + line.size())) return true;

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

static void trim(Wire& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == Wire::npos) {
        s.clear();
        return;
    }
    size_t end = s.find_last_not_of(" \t\r\n");
    s = s.substr(start, end - start + 1);
}

// Parse duration like "500ms" or "2s" or "1000" into milliseconds
static int parse_duration_ms(const Wire& s) {
    Wire str = s;
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

// Decode the escape vocabulary used in .spec files for SEND_RAW.
// Keeping the source specs printable makes fragmented and binary IRC frames readable.
static Wire decode_raw_escapes(const Wire& input) {
    Wire output;
    for (size_t i = 0; i < input.size(); ++i) {
        if (input[i] == '\\' && i + 1 < input.size()) {
            char next = input[i + 1];
            if (next == 'r') { output.append(1, '\r'); ++i; continue; }
            if (next == 'n') { output.append(1, '\n'); ++i; continue; }
            if (next == 't') { output.append(1, '\t'); ++i; continue; }
            if (next == '\\') { output.append(1, '\\'); ++i; continue; }
            if (next == 'x') {
                if (i + 2 < input.size() && isxdigit(static_cast<unsigned char>(input[i + 2]))) {
                    int val = 0;
                    char h1 = input[i + 2];
                    if (h1 >= '0' && h1 <= '9') val = h1 - '0';
                    else if (h1 >= 'a' && h1 <= 'f') val = h1 - 'a' + 10;
                    else if (h1 >= 'A' && h1 <= 'F') val = h1 - 'A' + 10;

                    if (i + 3 < input.size() && isxdigit(static_cast<unsigned char>(input[i + 3]))) {
                        char h2 = input[i + 3];
                        val = (val << 4);
                        if (h2 >= '0' && h2 <= '9') val += (h2 - '0');
                        else if (h2 >= 'a' && h2 <= 'f') val += (h2 - 'a' + 10);
                        else if (h2 >= 'A' && h2 <= 'F') val += (h2 - 'A' + 10);
                        output.append(1, static_cast<char>(val));
                        i += 3;
                        continue;
                    } else {
                        output.append(1, static_cast<char>(val));
                        i += 2;
                        continue;
                    }
                }
            }
            if (next >= '0' && next <= '7') {
                int val = 0;
                size_t count = 0;
                while (count < 3 && (i + 1 + count) < input.size() && input[i + 1 + count] >= '0' && input[i + 1 + count] <= '7') {
                    val = (val << 3) + (input[i + 1 + count] - '0');
                    count++;
                }
                output.append(1, static_cast<char>(val));
                i += count;
                continue;
            }
        }
        output.append(1, input[i]);
    }
    return output;
}

static Wire apply_password_substitution(const Wire& input, const Wire& custom_pwd) {
    if (custom_pwd.empty()) return input;

    if (input.toUpper().find("PASS") == 0 || input.toUpper().find("PASS ") != Wire::npos ||
        input.toUpper().find("SS ") == 0 || input.toUpper().find("SS\\X20") == 0) {
        Wire w(input);
        return w.replaceAll("1234", custom_pwd);
    }
    return input;
}

// -----------------------------------------------------------------------------
// Logger
// -----------------------------------------------------------------------------
class TestLogger {
public:
    std::ofstream log_file;
    Wire spec_name;
    bool verbose;

    TestLogger() : verbose(false) {}

    bool init(const Wire& spec_path, bool v = false) {
        verbose = v;
        size_t last_slash = spec_path.find_last_of("/\\");
        Wire filename = (last_slash == Wire::npos) ? spec_path : spec_path.substr(last_slash + 1);
        size_t last_dot = filename.find_last_of('.');
        spec_name = (last_dot == Wire::npos) ? filename : filename.substr(0, last_dot);
        
        mkdir("logs", 0755);
        Wire log_filename = "logs/" + spec_name + ".log";

        log_file.open(log_filename.c_str(), std::ios::out | std::ios::trunc);
        return log_file.is_open();
    }

    void log(const Wire& client, const Wire& type, const Wire& text) {
        Wire line = client + " " + type + " " + text;
        if (log_file.is_open()) {
            log_file << line << "\n";
            log_file.flush();
        }
        if (verbose) {
            const size_t MAX_LEN = 120;
            if (line.length() > MAX_LEN) {
                print(line.substr(0, MAX_LEN), "...");
            } else {
                print(line);
            }
        }
    }
};

// -----------------------------------------------------------------------------
// Virtual Client State
// -----------------------------------------------------------------------------
struct VirtualClient {
    Wire id;
    int fd;
    bool connected;
    Wire recv_buf;
    std::vector<Wire> line_queue;
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
    DIR_REPEAT_RAW,
    DIR_EXPECT,
    DIR_CONSUME,
    DIR_WAIT_RECV,
    DIR_WAIT,
    DIR_EXPECT_DISCONNECT,
    DIR_EXPECT_CONNECTED,
    DIR_EXPECT_NONE,
    DIR_EXPECT_COUNT,
    DIR_CONSUME_COUNT,
    DIR_CLOSE_SOCKET,
    DIR_CLOSE_WRITE,
    DIR_RESET,
    DIR_RECONNECT,
    DIR_PAUSE,
    DIR_RESUME,
    DIR_FLOOD,
    DIR_SET_SOCK_RCVBUF,
    DIR_TIMEOUT,
    DIR_UNKNOWN
};

struct Instruction {
    DirectiveType type;
    Wire client_id;
    Wire payload;
    Wire original_line;
    int line_number;
    Instruction() : type(DIR_UNKNOWN), line_number(0) {}
};

// -----------------------------------------------------------------------------
// TestRunner Engine
// -----------------------------------------------------------------------------
class TestRunner {
private:
    Wire host;
    int port;
    Wire password;
    int timeout_ms;
    TestLogger logger;
    std::map<Wire, VirtualClient> clients;
    std::vector<Wire> client_order;

public:
    TestRunner(const Wire& h, int p, const Wire& pwd = "") : host(h), port(p), password(pwd), timeout_ms(3000) {}

    ~TestRunner() {
        cleanup();
    }

    void cleanup() {
        bool had_connected = false;
        for (std::map<Wire, VirtualClient>::iterator it = clients.begin(); it != clients.end(); ++it) {
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

    bool connect_client(const Wire& client_id) {
        int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_fd < 0) {
            logger.log(client_id, "ERROR", "Failed to create socket");
            return false;
        }

        fcntl(socket_fd, F_SETFL, O_NONBLOCK);

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
            logger.log(client_id, "ERROR", "Socket error on connect: " + Wire(strerror(err)));
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
            std::vector<Wire> ids;

            for (std::map<Wire, VirtualClient>::iterator it = clients.begin(); it != clients.end(); ++it) {
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
            while ((pos = vc.recv_buf.find('\n')) != Wire::npos) {
                Wire line = vc.recv_buf.substr(0, pos);
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

    bool pop_next_line(VirtualClient& vc, Wire& line, int max_wait_ms) {
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

    bool wait_for_pattern(VirtualClient& vc, const Wire& pattern, int max_wait_ms) {
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

    bool consume_pattern(VirtualClient& vc, const Wire& pattern, int max_wait_ms) {
        long start = get_time_ms();
        while (true) {
            poll_all_clients(10);

            for (size_t i = 0; i < vc.line_queue.size(); ++i) {
                if (match_pattern(vc.line_queue[i], pattern)) {
                    vc.line_queue.erase(vc.line_queue.begin() + i);
                    return true;
                }
            }

            if (!vc.connected) return false;

            long elapsed = get_time_ms() - start;
            if (elapsed >= max_wait_ms) break;
        }
        return false;
    }

    bool send_raw(VirtualClient& vc, const Wire& data) {
        if (!vc.connected || vc.fd == -1) {
            logger.log(vc.id, "ERROR", "Cannot send data: socket not connected");
            return false;
        }
        size_t sent = 0;
        while (sent < data.size()) {
            ssize_t res = send(vc.fd, data.data() + sent, data.size() - sent, MSG_NOSIGNAL);
            if (res > 0) { sent += static_cast<size_t>(res); continue; }
            if (res < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
                struct pollfd pfd; pfd.fd = vc.fd; pfd.events = POLLOUT; pfd.revents = 0;
                if (poll(&pfd, 1, timeout_ms) <= 0) res = -1;
                else continue;
            }
            logger.log(vc.id, "ERROR", "Failed to send data: " + Wire(strerror(errno)));
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

    static Wire format_queue_dump(const VirtualClient& vc) {
        std::ostringstream oss;
        oss << " [Queue (" << vc.line_queue.size() << " lines): ";
        if (vc.line_queue.empty()) {
            oss << "<empty>";
        } else {
            const size_t max_items = 5;
            size_t count = std::min(vc.line_queue.size(), max_items);
            for (size_t i = 0; i < count; ++i) {
                if (i > 0) oss << " | ";
                Wire msg = vc.line_queue[i];
                if (msg.length() > 60) {
                    msg = msg.substr(0, 57) + "...";
                }
                oss << "\"" << msg << "\"";
            }
            if (vc.line_queue.size() > max_items) {
                oss << " | ... (" << (vc.line_queue.size() - max_items) << " more)";
            }
        }
        oss << "]";
        return Wire(oss.str());
    }

    bool assert_none(VirtualClient& vc, int quiet_ms, size_t start_index) {
        poll_all_clients(quiet_ms);
        if (vc.line_queue.size() > start_index) return false;
        return vc.connected;
    }

    int count_matching(const VirtualClient& vc, const Wire& pattern, size_t start_index = 0) {
        int count = 0;
        for (size_t i = start_index; i < vc.line_queue.size(); ++i)
            if (match_pattern(vc.line_queue[i], pattern)) ++count;
        return count;
    }

    bool run_spec(const Wire& spec_path, bool verbose = false) {
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
        Wire line;
        int line_num = 0;

        while (std::getline(spec_file, line)) {
            line_num++;
            Wire trimmed = line;
            trim(trimmed);
            if (trimmed.empty() || trimmed[0] == '#') continue;

            Instruction inst;
            inst.original_line = line;
            inst.line_number = line_num;

            std::istringstream iss(trimmed);
            Wire token1;
            iss >> token1;

            if (token1 == "CLIENTS") {
                inst.type = DIR_CLIENTS;
                Wire rest;
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
                Wire token2;
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
                } else if (token2 == "CONSUME_COUNT") {
                    inst.type = DIR_CONSUME_COUNT;
                    std::getline(iss, inst.payload); trim(inst.payload);
                } else if (token2 == "SEND_RAW") {
                    inst.type = DIR_SEND_RAW;
                    std::getline(iss, inst.payload); if (!inst.payload.empty() && inst.payload[0] == ' ') inst.payload.erase(0, 1);
                } else if (token2 == "REPEAT_RAW") {
                    inst.type = DIR_REPEAT_RAW;
                    std::getline(iss, inst.payload); trim(inst.payload);
                } else if (token2 == "CLOSE_SOCKET" || token2 == "CLOSE_WRITE" || token2 == "RESET" || token2 == "RECONNECT" || token2 == "PAUSE" || token2 == "RESUME") {
                    inst.type = token2 == "CLOSE_SOCKET" ? DIR_CLOSE_SOCKET : token2 == "CLOSE_WRITE" ? DIR_CLOSE_WRITE : token2 == "RESET" ? DIR_RESET : token2 == "RECONNECT" ? DIR_RECONNECT : token2 == "PAUSE" ? DIR_PAUSE : DIR_RESUME;
                } else if (token2 == "SET_SOCK_RCVBUF") {
                    inst.type = DIR_SET_SOCK_RCVBUF;
                    iss >> inst.payload;
                } else if (token2 == "FLOOD") {
                    inst.type = DIR_FLOOD;
                    std::getline(iss, inst.payload); trim(inst.payload);
                } else if (token2 == "EXPECT") {
                    inst.type = DIR_EXPECT;
                    Wire rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else if (token2 == "CONSUME") {
                    inst.type = DIR_CONSUME;
                    Wire rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else if (token2 == "WAIT_RECV") {
                    inst.type = DIR_WAIT_RECV;
                    Wire rest;
                    std::getline(iss, rest);
                    trim(rest);
                    inst.payload = rest;
                } else if (token2 == "SEND") {
                    inst.type = DIR_SEND;
                    Wire rest;
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
                Wire cid;
                while (std::getline(css, cid, ',')) {
                    trim(cid);
                    if (!cid.empty()) {
                        client_order.push_back(cid);
                        clients[cid] = VirtualClient();
                        if (!connect_client(cid)) {
                            logger.log(cid, "ERROR", "CLIENTS directive failed to connect client " + cid);
                            printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": CLIENTS failed to connect client ", cid);
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
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "EXPECT_DISCONNECT failed: socket is still connected" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " EXPECT_DISCONNECT failed: socket is still connected", dump);
                    return false;
                }
                logger.log(inst.client_id, "SYS", "Asserted DISCONNECTED successfully");
            } else if (inst.type == DIR_EXPECT_CONNECTED) {
                VirtualClient& vc = clients[inst.client_id];
                poll_all_clients(200);
                if (!vc.connected) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "EXPECT_CONNECTED failed: socket is closed" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " EXPECT_CONNECTED failed: socket is closed", dump);
                    return false;
                }
                logger.log(inst.client_id, "SYS", "Asserted CONNECTED successfully");
            } else if (inst.type == DIR_SEND_RAW) {
                VirtualClient& vc = clients[inst.client_id];
                Wire actual_payload = apply_password_substitution(inst.payload, password);
                logger.log(inst.client_id, "SEND_RAW", actual_payload);
                if (!send_raw(vc, decode_raw_escapes(actual_payload))) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "SEND_RAW failed for payload: " + actual_payload + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " SEND_RAW failed for payload \"", actual_payload, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_REPEAT_RAW) {
                VirtualClient& vc = clients[inst.client_id];
                std::istringstream rs(inst.payload);
                int count = 0;
                rs >> count;
                Wire payload;
                std::getline(rs, payload);
                trim(payload);
                Wire decoded_payload = decode_raw_escapes(payload);
                if (count < 1 || count > 10000 || decoded_payload.empty()) {
                    logger.log(inst.client_id, "ERROR", "REPEAT_RAW invalid parameters: " + inst.payload);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " REPEAT_RAW invalid parameters: \"", inst.payload, "\"");
                    return false;
                }
                for (int n = 0; n < count; ++n) {
                    if (!send_raw(vc, decoded_payload)) {
                        Wire dump = format_queue_dump(vc);
                        logger.log(inst.client_id, "ERROR", "REPEAT_RAW send failed at iteration " + Wire(n) + dump);
                        printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " REPEAT_RAW send failed at iteration ", n, dump);
                        return false;
                    }
                }
                logger.log(inst.client_id, "REPEAT_RAW", inst.payload);
            } else if (inst.type == DIR_CLOSE_SOCKET || inst.type == DIR_RESET) {
                close_client(clients[inst.client_id], inst.type == DIR_RESET);
            } else if (inst.type == DIR_CLOSE_WRITE) {
                VirtualClient& vc = clients[inst.client_id];
                if (vc.fd != -1) { shutdown(vc.fd, SHUT_WR); logger.log(vc.id, "SYS", "Write half-closed"); }
            } else if (inst.type == DIR_RECONNECT) {
                VirtualClient& vc = clients[inst.client_id];
                close_client(vc, false);
                if (!connect_client(inst.client_id)) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "RECONNECT failed for client " + inst.client_id + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " RECONNECT failed to reconnect client ", inst.client_id, dump);
                    return false;
                }
            } else if (inst.type == DIR_PAUSE || inst.type == DIR_RESUME) {
                clients[inst.client_id].reading = (inst.type == DIR_RESUME);
                logger.log(inst.client_id, "SYS", inst.type == DIR_RESUME ? "Reading resumed" : "Reading paused");
            } else if (inst.type == DIR_SET_SOCK_RCVBUF) {
                VirtualClient& vc = clients[inst.client_id];
                int buf_size = atoi(inst.payload.c_str());
                if (vc.fd != -1 && buf_size > 0) {
                    int res = setsockopt(vc.fd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));
                    if (res < 0) {
                        logger.log(inst.client_id, "ERROR", "Failed to set SO_RCVBUF: " + Wire(strerror(errno)));
                    } else {
                        logger.log(inst.client_id, "SYS", "Set SO_RCVBUF to " + inst.payload);
                    }
                }
            } else if (inst.type == DIR_FLOOD) {
                VirtualClient& vc = clients[inst.client_id];
                std::istringstream fs(inst.payload); int count = 0; fs >> count;
                Wire payload; std::getline(fs, payload); trim(payload);
                if (count < 1 || count > 10000 || payload.empty()) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "FLOOD invalid parameters: " + inst.payload + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " FLOOD invalid parameters: \"", inst.payload, "\"", dump);
                    return false;
                }
                for (int n = 0; n < count; ++n) {
                    if (!send_raw(vc, payload + "\r\n")) {
                        Wire dump = format_queue_dump(vc);
                        logger.log(inst.client_id, "ERROR", "FLOOD send failed at iteration " + Wire(n) + dump);
                        printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " FLOOD send failed at iteration ", n, dump);
                        return false;
                    }
                }
                logger.log(inst.client_id, "FLOOD", payload);
            } else if (inst.type == DIR_SEND) {
                VirtualClient& vc = clients[inst.client_id];
                Wire actual_payload = apply_password_substitution(inst.payload, password);
                logger.log(inst.client_id, "SEND", actual_payload);
                if (!send_raw(vc, actual_payload + "\r\n")) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "SEND failed for payload: " + actual_payload + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " SEND failed for payload \"", actual_payload, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_EXPECT) {
                VirtualClient& vc = clients[inst.client_id];
                if (!wait_for_pattern(vc, inst.payload, timeout_ms)) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "EXPECT assertion failed for pattern: \"" + inst.payload + "\"" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " EXPECT pattern: \"", inst.payload, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_CONSUME) {
                VirtualClient& vc = clients[inst.client_id];
                if (!consume_pattern(vc, inst.payload, timeout_ms)) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "CONSUME assertion failed for pattern: \"" + inst.payload + "\"" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " CONSUME pattern: \"", inst.payload, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_EXPECT_NONE) {
                VirtualClient& vc = clients[inst.client_id];
                int quiet_ms = parse_duration_ms(inst.payload);
                size_t start_index = vc.line_queue.size();
                if (!assert_none(vc, quiet_ms, start_index)) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "EXPECT_NONE observed queued data or disconnect" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " EXPECT_NONE observed queued data or disconnect", dump);
                    return false;
                }
            } else if (inst.type == DIR_EXPECT_COUNT) {
                VirtualClient& vc = clients[inst.client_id]; std::istringstream es(inst.payload);
                int expected = 0; es >> expected; Wire pattern; std::getline(es, pattern); trim(pattern);
                size_t start_index = vc.line_queue.size();
                long start_time = get_time_ms();
                while (true) {
                    poll_all_clients(50);
                    int current_matches = count_matching(vc, pattern, start_index);
                    if (expected > 0 && current_matches >= expected) {
                        poll_all_clients(50);
                        break;
                    }
                    if (!vc.connected) break;
                    long elapsed = get_time_ms() - start_time;
                    if (elapsed >= timeout_ms) break;
                }
                int actual = count_matching(vc, pattern, start_index);
                if (actual != expected) {
                    Wire dump = format_queue_dump(vc);
                    std::ostringstream oss;
                    oss << "Expected count " << expected << " but got " << actual << " for pattern: \"" << pattern << "\"";
                    logger.log(inst.client_id, "ERROR", Wire(oss.str()) + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " EXPECT_COUNT (expected ", expected, ", got ", actual, ") for \"", pattern, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_CONSUME_COUNT) {
                VirtualClient& vc = clients[inst.client_id]; std::istringstream es(inst.payload);
                Wire op_or_num; es >> op_or_num;
                Wire op = "==";
                int target_val = 0;
                if (op_or_num.rfind(">=", 0) == 0) {
                    op = ">=";
                    Wire num_str = op_or_num.substr(2);
                    if (num_str.empty()) es >> target_val;
                    else target_val = atoi(num_str.c_str());
                } else if (op_or_num.rfind("<=", 0) == 0) {
                    op = "<=";
                    Wire num_str = op_or_num.substr(2);
                    if (num_str.empty()) es >> target_val;
                    else target_val = atoi(num_str.c_str());
                } else if (op_or_num.rfind(">", 0) == 0) {
                    op = ">";
                    Wire num_str = op_or_num.substr(1);
                    if (num_str.empty()) es >> target_val;
                    else target_val = atoi(num_str.c_str());
                } else if (op_or_num.rfind("<", 0) == 0) {
                    op = "<";
                    Wire num_str = op_or_num.substr(1);
                    if (num_str.empty()) es >> target_val;
                    else target_val = atoi(num_str.c_str());
                } else if (op_or_num.rfind("==", 0) == 0) {
                    op = "==";
                    Wire num_str = op_or_num.substr(2);
                    if (num_str.empty()) es >> target_val;
                    else target_val = atoi(num_str.c_str());
                } else {
                    op = "==";
                    target_val = atoi(op_or_num.c_str());
                }

                Wire pattern; std::getline(es, pattern); trim(pattern);
                long start_time = get_time_ms();
                while (true) {
                    poll_all_clients(50);
                    int current_matches = count_matching(vc, pattern, 0);
                    bool satisfied = false;
                    if (op == ">=" && current_matches >= target_val) satisfied = true;
                    else if (op == ">" && current_matches > target_val) satisfied = true;
                    else if (op == "==" && target_val > 0 && current_matches >= target_val) satisfied = true;

                    if (satisfied) {
                        poll_all_clients(50);
                        break;
                    }
                    if (!vc.connected) break;
                    long elapsed = get_time_ms() - start_time;
                    if (elapsed >= timeout_ms) break;
                }
                int actual = 0;
                for (size_t i = 0; i < vc.line_queue.size(); ) {
                    if (match_pattern(vc.line_queue[i], pattern)) {
                        ++actual;
                        vc.line_queue.erase(vc.line_queue.begin() + i);
                    } else {
                        ++i;
                    }
                }

                bool pass = false;
                if (op == ">=") pass = (actual >= target_val);
                else if (op == "<=") pass = (actual <= target_val);
                else if (op == ">") pass = (actual > target_val);
                else if (op == "<") pass = (actual < target_val);
                else pass = (actual == target_val);

                if (!pass) {
                    Wire dump = format_queue_dump(vc);
                    std::ostringstream oss;
                    oss << "Expected count " << op << " " << target_val << " but got " << actual << " for pattern: \"" << pattern << "\"";
                    logger.log(inst.client_id, "ERROR", Wire(oss.str()) + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " CONSUME_COUNT (expected ", op, " ", target_val, ", got ", actual, ") for \"", pattern, "\"", dump);
                    return false;
                }
            } else if (inst.type == DIR_WAIT_RECV) {
                VirtualClient& vc = clients[inst.client_id];
                if (!wait_for_pattern(vc, inst.payload, timeout_ms)) {
                    Wire dump = format_queue_dump(vc);
                    logger.log(inst.client_id, "ERROR", "WAIT_RECV timeout matching pattern: \"" + inst.payload + "\"" + dump);
                    printErr("FAIL [", logger.spec_name, "] Line ", inst.line_number, ": ", inst.client_id, " WAIT_RECV pattern: \"", inst.payload, "\"", dump);
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
    Wire host = "127.0.0.1";
    int port = 6667;
    Wire password = "";
    Wire spec_path = "";
    bool verbose = false;

    for (int i = 1; i < argc; ++i) {
        Wire arg = argv[i];
        if (arg == "--host" && i + 1 < argc) {
            host = argv[++i];
        } else if (arg == "--port" && i + 1 < argc) {
            port = atoi(argv[++i]);
        } else if ((arg == "--password" || arg == "-p") && i + 1 < argc) {
            password = argv[++i];
        } else if (arg == "--v" || arg == "-v" || arg == "--verbose") {
            verbose = true;
        } else if (arg[0] != '-') {
            spec_path = arg;
        }
    }

    if (spec_path.empty()) {
        print("Usage: testrunner [--host <host>] [--port <port>] [--password <pwd>] [--v] <spec_file>");
        return 1;
    }

    TestRunner runner(host, port, password);
    if (!runner.run_spec(spec_path, verbose)) {
        return 1;
    }
    return 0;
}
