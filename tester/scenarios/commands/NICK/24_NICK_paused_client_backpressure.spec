# 24_NICK_paused_client_backpressure.spec
# Slow / suspended client in a shared channel while another client renames.
# Expected: Server buffers the NICK broadcast in the client's output buffer and delivers upon resume without dropping or crashing.
CLIENTS C1, C2

# C1 registers as Alice24
C1 SEND PASS 1234
C1 SEND NICK Alice24
C1 SEND USER user24 0 * :Alice 24
C1 EXPECT 001 Alice24 :*

# C2 registers as Bob24
C2 SEND PASS 1234
C2 SEND NICK Bob24
C2 SEND USER user24 0 * :Bob 24
C2 EXPECT 001 Bob24 :*

# Both join #backpressure24
C1 SEND JOIN #backpressure24
C2 SEND JOIN #backpressure24
C1 WAIT_RECV :Bob24!* JOIN #backpressure24

# C2 suspends receiving
C2 PAUSE

# C1 renames to Alicia24
C1 SEND NICK Alicia24
C1 WAIT_RECV :Alice24!* NICK :Alicia24

# C2 resumes and receives the buffered rename
C2 RESUME
C2 WAIT_RECV :Alice24!* NICK :Alicia24
C2 EXPECT_CONNECTED
