#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <pthread.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <poll.h>

struct ConcurrencyConfig {
    std::string host;
    int port;
    std::string password;
    int thread_count;
    std::string suite;

    ConcurrencyConfig()
        : host("127.0.0.1"), port(6667), password("1234"), thread_count(0), suite("all") {}
};

static ConcurrencyConfig g_config;
static pthread_barrier_t g_barrier1;
static pthread_barrier_t g_barrier2;

static int connect_tcp(const std::string& host, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host.c_str(), &addr.sin_addr) <= 0) {
        struct hostent* he = gethostbyname(host.c_str());
        if (!he) { close(fd); return -1; }
        std::memcpy(&addr.sin_addr, he->h_addr_list[0], he->h_length);
    }

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static bool send_all(int fd, const std::string& msg) {
    size_t sent = 0;
    while (sent < msg.length()) {
        ssize_t res = send(fd, msg.c_str() + sent, msg.length() - sent, MSG_NOSIGNAL);
        if (res <= 0) return false;
        sent += static_cast<size_t>(res);
    }
    return true;
}

static std::string read_until_match(int fd, const std::string& target1, const std::string& target2 = "", int timeout_ms = 2000) {
    std::string accumulated;
    char buf[2048];
    int remaining_ms = timeout_ms;

    while (remaining_ms > 0) {
        struct pollfd pfd;
        pfd.fd = fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int step = (remaining_ms > 100) ? 100 : remaining_ms;
        int ret = poll(&pfd, 1, step);
        remaining_ms -= step;

        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = recv(fd, buf, sizeof(buf) - 1, 0);
            if (n <= 0) break;
            buf[n] = '\0';
            accumulated.append(buf, n);

            if (!target1.empty() && accumulated.find(target1) != std::string::npos) {
                break;
            }
            if (!target2.empty() && accumulated.find(target2) != std::string::npos) {
                break;
            }
        } else if (ret < 0) {
            break;
        }
    }
    return accumulated;
}

static std::string read_available_all(int fd, int timeout_ms = 1000) {
    std::string accumulated;
    char buf[2048];
    int remaining_ms = timeout_ms;

    while (remaining_ms > 0) {
        struct pollfd pfd;
        pfd.fd = fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int step = (remaining_ms > 100) ? 100 : remaining_ms;
        int ret = poll(&pfd, 1, step);
        remaining_ms -= step;

        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = recv(fd, buf, sizeof(buf) - 1, 0);
            if (n <= 0) break;
            buf[n] = '\0';
            accumulated.append(buf, n);
        } else if (ret == 0) {
            if (!accumulated.empty()) {
                break;
            }
        } else {
            break;
        }
    }
    return accumulated;
}

// -----------------------------------------------------------------------------
// Test 1: Simultaneous Nickname Collision Race (50 threads)
// -----------------------------------------------------------------------------
struct NickRaceContext {
    int thread_id;
    int result_status; // 1 = 001 registered, 2 = 433 nick collision, -1 = error
};

static void* nick_collision_worker(void* arg) {
    NickRaceContext* ctx = static_cast<NickRaceContext*>(arg);
    ctx->result_status = -1;

    int fd = connect_tcp(g_config.host, g_config.port);
    if (fd < 0) return NULL;

    // Barrier 1: Wait for all threads to establish TCP connection before sending
    pthread_barrier_wait(&g_barrier1);

    // Simultaneously submit registration with the exact same nickname
    std::string payload = "PASS " + g_config.password + "\r\nNICK winner\r\nUSER winner 0 * :winner\r\n";
    send_all(fd, payload);

    std::string response = read_until_match(fd, " 001 ", " 433 ", 2500);
    if (response.find(" 001 ") != std::string::npos) {
        ctx->result_status = 1;
    } else if (response.find(" 433 ") != std::string::npos) {
        ctx->result_status = 2;
    }

    // Barrier 2: Hold all connections open until all threads have completed their registration attempt
    pthread_barrier_wait(&g_barrier2);

    send_all(fd, "QUIT :race finished\r\n");
    close(fd);
    return NULL;
}

static bool test_nick_collision_race(int num_threads) {
    std::cout << "[RUN ] Nickname Collision Race (" << num_threads << " simultaneous threads claiming 'winner')..." << std::endl;

    pthread_barrier_init(&g_barrier1, NULL, num_threads);
    pthread_barrier_init(&g_barrier2, NULL, num_threads);
    std::vector<pthread_t> threads(num_threads);
    std::vector<NickRaceContext> contexts(num_threads);

    for (int i = 0; i < num_threads; ++i) {
        contexts[i].thread_id = i;
        contexts[i].result_status = -1;
        pthread_create(&threads[i], NULL, nick_collision_worker, &contexts[i]);
    }

    int win_count = 0;
    int collision_count = 0;
    int fail_count = 0;

    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
        if (contexts[i].result_status == 1) win_count++;
        else if (contexts[i].result_status == 2) collision_count++;
        else fail_count++;
    }

    pthread_barrier_destroy(&g_barrier1);
    pthread_barrier_destroy(&g_barrier2);

    std::cout << "       Result: " << win_count << " winner(s), " << collision_count
              << " collision (433) rejects, " << fail_count << " error/timeouts" << std::endl;

    if (win_count == 1 && (win_count + collision_count == num_threads)) {
        std::cout << "\033[0;32m[PASS]\033[0m Exactly 1 client claimed the nick, all "
                  << (num_threads - 1) << " others received 433 :Nickname is already in use\n" << std::endl;
        return true;
    } else {
        std::cout << "\033[0;31m[FAIL]\033[0m Race condition detected! Expected 1 winner and "
                  << (num_threads - 1) << " 433 rejects, got " << win_count << " winners and "
                  << collision_count << " 433 rejects\n" << std::endl;
        return false;
    }
}

// -----------------------------------------------------------------------------
// Test 2: Burst Accept Queue Race (100 threads within 10ms window)
// -----------------------------------------------------------------------------
struct BurstAcceptContext {
    int thread_id;
    bool success;
};

static void* burst_accept_worker(void* arg) {
    BurstAcceptContext* ctx = static_cast<BurstAcceptContext*>(arg);
    ctx->success = false;

    // Synchronize BEFORE connecting so all 100 threads initiate connect in a tight burst
    pthread_barrier_wait(&g_barrier1);

    // Stagger slightly within a 10ms window across the worker threads
    if (ctx->thread_id > 0) {
        usleep((ctx->thread_id % 10) * 1000);
    }

    int fd = -1;
    for (int attempt = 0; attempt < 3; ++attempt) {
        fd = connect_tcp(g_config.host, g_config.port);
        if (fd >= 0) break;
        usleep(5000);
    }

    if (fd < 0) return NULL;

    std::ostringstream oss;
    oss << "PASS " << g_config.password << "\r\nNICK burst_" << ctx->thread_id
        << "\r\nUSER burst 0 * :Burst\r\n";
    send_all(fd, oss.str());

    std::string resp = read_until_match(fd, " 001 ", "", 5000);
    if (resp.find(" 001 ") != std::string::npos) {
        ctx->success = true;
    }

    send_all(fd, "QUIT :burst done\r\n");
    close(fd);
    return NULL;
}

static bool test_burst_accept(int num_threads) {
    std::cout << "[RUN ] Burst Accept Queue Race (" << num_threads << " parallel connections within 10ms window)..." << std::endl;

    pthread_barrier_init(&g_barrier1, NULL, num_threads);
    std::vector<pthread_t> threads(num_threads);
    std::vector<BurstAcceptContext> contexts(num_threads);

    for (int i = 0; i < num_threads; ++i) {
        contexts[i].thread_id = i;
        contexts[i].success = false;
        pthread_create(&threads[i], NULL, burst_accept_worker, &contexts[i]);
    }

    int success_count = 0;
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
        if (contexts[i].success) success_count++;
    }

    pthread_barrier_destroy(&g_barrier1);

    std::cout << "       Result: " << success_count << "/" << num_threads << " accepted and registered successfully" << std::endl;

    if (success_count == num_threads) {
        std::cout << "\033[0;32m[PASS]\033[0m All " << num_threads << " burst connections handled without drops or event-loop starvation\n" << std::endl;
        return true;
    } else {
        std::cout << "\033[0;31m[FAIL]\033[0m Accept queue starvation detected! " << (num_threads - success_count) << " connections failed\n" << std::endl;
        return false;
    }
}

// -----------------------------------------------------------------------------
// Test 3: Simultaneous Channel Mode / Join Race (20 threads)
// -----------------------------------------------------------------------------
struct ChannelRaceContext {
    int thread_id;
    int fd;
    bool registered;
    bool joined;
    bool key_or_invite_denied;
    bool op_mode_set;
    bool non_op_rejected;
};

static void* channel_race_worker(void* arg) {
    ChannelRaceContext* ctx = static_cast<ChannelRaceContext*>(arg);
    ctx->registered = false;
    ctx->joined = false;
    ctx->key_or_invite_denied = false;
    ctx->op_mode_set = false;
    ctx->non_op_rejected = false;

    ctx->fd = connect_tcp(g_config.host, g_config.port);
    if (ctx->fd < 0) return NULL;

    // Register unique client
    std::ostringstream reg_oss;
    reg_oss << "PASS " << g_config.password << "\r\nNICK race_user_" << ctx->thread_id
            << "\r\nUSER race 0 * :Race User\r\n";
    send_all(ctx->fd, reg_oss.str());

    std::string reg_resp = read_until_match(ctx->fd, " 001 ", "", 2500);
    if (reg_resp.find(" 001 ") == std::string::npos) {
        close(ctx->fd);
        ctx->fd = -1;
        return NULL;
    }
    ctx->registered = true;

    // Wait at barrier 1: All clients are registered and ready
    pthread_barrier_wait(&g_barrier1);

    // Concurrently join #race and attempt channel modes
    std::ostringstream act_oss;
    act_oss << "JOIN #race\r\n";
    if (ctx->thread_id % 2 == 0) {
        act_oss << "MODE #race +k secret\r\n";
    } else {
        act_oss << "MODE #race +i\r\n";
    }
    send_all(ctx->fd, act_oss.str());

    std::string responses = read_available_all(ctx->fd, 1500);
    if (responses.find("JOIN :#race") != std::string::npos ||
        responses.find(" 353 ") != std::string::npos ||
        responses.find(" 366 ") != std::string::npos) {
        ctx->joined = true;
    }

    if (responses.find(" 473 ") != std::string::npos ||
        responses.find(" 475 ") != std::string::npos) {
        ctx->key_or_invite_denied = true;
    }

    if (responses.find("MODE #race +") != std::string::npos) {
        ctx->op_mode_set = true;
    }
    if (responses.find(" 482 ") != std::string::npos ||
        responses.find(" 442 ") != std::string::npos) {
        ctx->non_op_rejected = true;
    }

    // Wait at barrier 2: Keep connections open while auditor inspects server channel state
    pthread_barrier_wait(&g_barrier2);

    send_all(ctx->fd, "QUIT :race finished\r\n");
    close(ctx->fd);
    ctx->fd = -1;
    return NULL;
}

static bool test_channel_mode_join_race(int num_threads) {
    std::cout << "[RUN ] Simultaneous Channel Mode / Join Race (" << num_threads
              << " threads joining #race and contending on MODE +k / +i)..." << std::endl;

    // num_threads + 1 so main thread coordinates the audit before releasing workers
    pthread_barrier_init(&g_barrier1, NULL, num_threads);
    pthread_barrier_init(&g_barrier2, NULL, num_threads + 1);
    std::vector<pthread_t> threads(num_threads);
    std::vector<ChannelRaceContext> contexts(num_threads);

    for (int i = 0; i < num_threads; ++i) {
        contexts[i].thread_id = i;
        contexts[i].fd = -1;
        pthread_create(&threads[i], NULL, channel_race_worker, &contexts[i]);
    }

    // Auditor verification: Query server health and channel responses from an independent client
    usleep(300000);
    int audit_fd = connect_tcp(g_config.host, g_config.port);
    bool auditor_ok = false;
    if (audit_fd >= 0) {
        send_all(audit_fd, "PASS " + g_config.password + "\r\nNICK race_auditor\r\nUSER auditor 0 * :Auditor\r\n");
        std::string audit_reg = read_until_match(audit_fd, " 001 ", "", 2000);
        if (audit_reg.find(" 001 ") != std::string::npos) {
            // Verify server responds with PONG and channel status replies
            send_all(audit_fd, "PING :healthcheck\r\nNAMES #race\r\nMODE #race\r\n");
            std::string audit_resp = read_until_match(audit_fd, "PONG", " 366 ", 2000);
            if (audit_resp.find("PONG") != std::string::npos ||
                audit_resp.find(" 366 ") != std::string::npos ||
                audit_resp.find(" 442 ") != std::string::npos) {
                auditor_ok = true;
            }
        }
        send_all(audit_fd, "QUIT :auditor done\r\n");
        close(audit_fd);
    }

    // Release worker threads from barrier 2 so they can disconnect
    pthread_barrier_wait(&g_barrier2);

    int reg_count = 0;
    int join_count = 0;
    int denied_count = 0;
    int op_mode_count = 0;
    int non_op_count = 0;

    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
        if (contexts[i].registered) reg_count++;
        if (contexts[i].joined) join_count++;
        if (contexts[i].key_or_invite_denied) denied_count++;
        if (contexts[i].op_mode_set) op_mode_count++;
        if (contexts[i].non_op_rejected) non_op_count++;
    }

    pthread_barrier_destroy(&g_barrier1);
    pthread_barrier_destroy(&g_barrier2);

    std::cout << "       Result: " << reg_count << "/" << num_threads << " registered, "
              << join_count << " joined, " << denied_count << " +k/+i access-denied, "
              << op_mode_count << " op mode applied, " << non_op_count << " non-op rejected, auditor verification: "
              << (auditor_ok ? "OK" : "FAIL") << std::endl;

    bool passed = (reg_count == num_threads &&
                   (join_count + denied_count == num_threads) &&
                   op_mode_count >= 1 &&
                   auditor_ok);

    if (passed) {
        std::cout << "\033[0;32m[PASS]\033[0m Channel join and mode contention preserved consistency without memory corruption or hangs\n" << std::endl;
        return true;
    } else {
        std::cout << "\033[0;31m[FAIL]\033[0m Channel race inconsistency detected!\n" << std::endl;
        return false;
    }
}

// -----------------------------------------------------------------------------
// CLI Main
// -----------------------------------------------------------------------------
static void print_usage(const char* prog) {
    std::cout << "Usage: " << prog << " [OPTIONS]\n\n"
              << "Options:\n"
              << "  --host <host>          Target server host (default: 127.0.0.1)\n"
              << "  --port <port>          Target server port (default: 6667)\n"
              << "  --password, -p <pass>  Server password (default: 1234)\n"
              << "  --threads <count>      Thread count override for test suites\n"
              << "  --suite <name>         Run specific suite: nick, burst, channel, all (default: all)\n"
              << "  -h, --help             Show this help message\n"
              << std::endl;
}

int main(int argc, char* argv[]) {
    const char* env_host = std::getenv("HOST");
    if (env_host) g_config.host = env_host;

    const char* env_port = std::getenv("PORT");
    if (env_port) g_config.port = std::atoi(env_port);

    const char* env_pass = std::getenv("PASSWORD");
    if (env_pass) g_config.password = env_pass;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--host" && i + 1 < argc) g_config.host = argv[++i];
        else if (arg == "--port" && i + 1 < argc) g_config.port = std::atoi(argv[++i]);
        else if ((arg == "--password" || arg == "-p") && i + 1 < argc) g_config.password = argv[++i];
        else if (arg == "--threads" && i + 1 < argc) g_config.thread_count = std::atoi(argv[++i]);
        else if (arg == "--suite" && i + 1 < argc) g_config.suite = argv[++i];
        else if (arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            return 0;
        }
    }

    std::cout << "\n\033[1m== Multi-Threaded IRC Concurrency & Race Condition Suite ==\033[0m\n" << std::endl;
    std::cout << "Target: " << g_config.host << ":" << g_config.port << std::endl;
    std::cout << "--------------------------------------------------------\n" << std::endl;

    // Check if server is running
    int probe_fd = connect_tcp(g_config.host, g_config.port);
    if (probe_fd < 0) {
        std::cerr << "\033[0;31mError: Server unreachable at " << g_config.host << ":" << g_config.port
                  << ". Please start the server first.\033[0m\n" << std::endl;
        return 1;
    }
    close(probe_fd);

    int passed = 0;
    int total = 0;

    int nick_threads = (g_config.thread_count > 0) ? g_config.thread_count : 50;
    int burst_threads = (g_config.thread_count > 0) ? g_config.thread_count : 100;
    int chan_threads = (g_config.thread_count > 0) ? g_config.thread_count : 20;

    if (g_config.suite == "all" || g_config.suite == "nick") {
        total++;
        if (test_nick_collision_race(nick_threads)) passed++;
        usleep(300000);
    }

    if (g_config.suite == "all" || g_config.suite == "burst") {
        total++;
        if (test_burst_accept(burst_threads)) passed++;
        usleep(300000);
    }

    if (g_config.suite == "all" || g_config.suite == "channel") {
        total++;
        if (test_channel_mode_join_race(chan_threads)) passed++;
    }

    std::cout << "--------------------------------------------------------" << std::endl;
    if (passed == total && total > 0) {
        std::cout << "\033[0;32mSummary: " << passed << "/" << total << " concurrency suites passed.\033[0m\n" << std::endl;
        return 0;
    } else {
        std::cout << "\033[0;31mSummary: " << passed << "/" << total << " concurrency suites passed, "
                  << (total - passed) << " failed.\033[0m\n" << std::endl;
        return 1;
    }
}
