# EPOLL vs. POLL: Architecture & Implementation Guide

This document explains the conceptual differences, architectural changes, and implementation details of transitioning the `ft_irc` server from POSIX `poll()` to Linux `epoll`.

---

## 1. Conceptual Architecture & Overview

### How `poll()` Works
- **User-Space Controlled & Stateless**: The application maintains a contiguous array of `struct pollfd` structures in user space.
- **Copying Overhead ($O(N)$)**: On every event loop iteration, the entire array is passed to the kernel via the `poll()` syscall.
- **Full Scans ($O(N)$)**: The kernel iterates through all $N$ file descriptors in the array to check their state, populates the `revents` field, and copies the array back to user space. User space must then loop through the entire array again to identify which descriptors triggered events.
- **Linear Removal**: When a socket disconnects, removing it from a `std::vector<pollfd>` requires a linear search ($O(N)$) and element shifting ($O(N)$).

### How `epoll` Works
- **Kernel-Managed Interest List & Stateful**: The kernel maintains the set of monitored descriptors internally inside an epoll instance (using a Red-Black tree for $O(\log N)$ registration/lookup).
- **Zero Redundant Copies**: Descriptors are registered once via `epoll_ctl()`. Subsequent wait calls do not pass or copy descriptor lists back and forth between kernel and user space.
- **Direct Ready List ($O(K)$)**: When an I/O event occurs on a socket, the kernel places that socket onto a ready list. Calling `epoll_wait()` only copies the $K$ active events directly into a fixed-size event buffer.
- **Simplified Lifecycle**: Client removal is handled directly in the kernel via `epoll_ctl(..., EPOLL_CTL_DEL, ...)` or automatically when the last open file descriptor for the socket is closed.

---

## 2. Comparison Table

| Feature / Metric | POSIX `poll()` | Linux `epoll` |
| :--- | :--- | :--- |
| **System Call Complexity** | $O(N)$ where $N$ is total monitored sockets | $O(K)$ where $K$ is number of ready events |
| **User Space Loop Complexity** | $O(N)$ scan across all `pollfd` items | $O(K)$ iteration over active `events[]` only |
| **Kernel State** | Stateless (interest list rebuilt every call) | Stateful (managed inside kernel epoll object) |
| **Data Structures** | `std::vector<pollfd>` in user space | `epoll_fd` descriptor pointing to kernel RB-Tree |
| **Socket Registration** | `push_back()` to vector | `epoll_ctl(..., EPOLL_CTL_ADD, ...)` |
| **Socket Deregistration** | Vector search and `erase()` (shifts array) | `epoll_ctl(..., EPOLL_CTL_DEL, ...)` |
| **Triggering Modes** | Level-Triggered (LT) only | Level-Triggered (LT) or Edge-Triggered (ET) |
| **Portability** | Standard POSIX (Linux, macOS, BSD, Solaris) | Linux-specific (`<sys/epoll.h>`) |
| **Scalability (10k+ Connections)** | Poor (high CPU usage scanning idle sockets) | Excellent (scales with activity, not connections) |

---

## 3. Implementation Details in `ft_irc`

### 1. `Server.hpp`
- **Header**: `#include <sys/epoll.h>` replaces `#include <poll.h>`.
- **Member Variable**: Replaced `Vector<pollfd> fds` with a single file descriptor `int epoll_fd`.
- **Helper Signatures**:
  - Added `void add_epoll_fd(int fd, uint32_t events);`
  - Added `void remove_epoll_fd(int fd);`
  - Added `int get_epoll_fd() const;` and `void set_epoll_fd(int epoll_fd);`

### 2. `Server.cpp`
- **Lifecycle & RAII**:
  - Initialized `epoll_fd(-1)` in all constructor overloads.
  - In `~Server()`, added clean closing of `epoll_fd` if valid (`epoll_fd >= 0`) to prevent kernel resource leaks.
  - Implemented getter/setter for `epoll_fd`.

### 3. `ServerHelper.cpp`
- **Socket Registration (`add_epoll_fd`)**:
  ```cpp
  void Server::add_epoll_fd(int fd, uint32_t events) {
      struct epoll_event ev;
      std::memset(&ev, 0, sizeof(ev));
      ev.events = events;       // e.g., EPOLLIN
      ev.data.fd = fd;          // Associate the target socket fd with event

      // epoll_ctl arguments:
      // 1. get_epoll_fd(): The epoll instance file descriptor
      // 2. EPOLL_CTL_ADD: Operation to register a new descriptor
      // 3. fd: The socket descriptor being registered
      // 4. &ev: Event filter configuration and associated user data
      if (epoll_ctl(get_epoll_fd(), EPOLL_CTL_ADD, fd, &ev) == -1) {
          printErr("Error: epoll_ctl ADD failed!");
      }
  }
  ```
- **Socket Deregistration (`remove_epoll_fd`)**:
  ```cpp
  void Server::remove_epoll_fd(int fd) {
      if (get_epoll_fd() >= 0 && fd >= 0) {
          // EPOLL_CTL_DEL removes fd from monitoring (NULL event in Linux >= 2.6.9)
          epoll_ctl(get_epoll_fd(), EPOLL_CTL_DEL, fd, NULL);
      }
  }
  ```

### 4. `ServerLoop.cpp`
- **Instance Initialization**:
  - Creates the epoll instance via `int epfd = epoll_create1(0);`.
  - Adds the master listening `server_socket` with `EPOLLIN`.
- **Event Loop Dispatch**:
  - Calls `epoll_wait(get_epoll_fd(), events, MAX_EVENTS, -1)` which sleeps indefinitely until activity occurs.
  - Unblocks on POSIX signals (`EINTR`) allowing graceful shutdown on `SIGINT` / `SIGTERM`.
  - Iterates only from `0` to `nfds` (active descriptors), avoiding any vector reshuffling or iterator invalidation issues.
  - Disconnects / errors are caught via `(ev & (EPOLLERR | EPOLLHUP))`.
  - New connections and client data are processed under `ev & EPOLLIN`.

---

## 4. Portability & 42 Subject Considerations

- **42 School ft_irc Subject**: The standard 42 curriculum specifies using `poll()` (or `select`/`kqueue` depending on OS evaluation constraints).
- **Target OS Compatibility**: `epoll` is native to Linux. For macOS or FreeBSD environments, `kqueue` is the equivalent event multiplexing subsystem.
