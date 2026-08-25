# 24_NICK_paused_client_backpressure.spec
# Slow / suspended client in a shared channel while another client renames.
# Expected: Server buffers the NICK broadcast in the client's output buffer and delivers upon resume without dropping or crashing.
CLIENTS C1, C2

# C1 registers as Alice24
C1 SEND PASS 1234
C1 SEND NICK Ali206
C1 SEND USER u206 0 * :Ali206 24
C1 EXPECT 001 Ali206 :*

# C2 registers as Bob24
C2 SEND PASS 1234
C2 SEND NICK Bob206
C2 SEND USER u206 0 * :Bob206 24
C2 EXPECT 001 Bob206 :*

# Both join #backpressure24
C1 SEND JOIN #backpressure24
C2 SEND JOIN #backpressure24
C1 WAIT_RECV :Bob206!* JOIN #backpressure24

# C2 suspends receiving
C2 PAUSE

# C1 renames to Alicia24
C1 SEND NICK Ali206
C1 WAIT_RECV :Ali206!* NICK :Ali206

# C2 resumes and receives the buffered rename
C2 RESUME
C2 WAIT_RECV :Ali206!* NICK :Ali206
C2 EXPECT_CONNECTED
