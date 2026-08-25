# 214_QUIT_pipelined_stream_abort.spec
# Tests that commands pipelined in the same TCP frame following QUIT are aborted.
CLIENTS C1, C2

# Alice (C1) in #stream
C1 SEND PASS 1234
C1 SEND NICK Ali329
C1 SEND USER ali329 0 * :Ali329
C1 EXPECT 001 Ali329 :*

C1 SEND JOIN #stream
C1 EXPECT :Ali329!* JOIN #stream

# Bob sends complete registration, join, QUIT, and subsequent ghost commands in single burst
C2 SEND_RAW PASS 1234\r\nNICK Bob329\r\nUSER bob329 0 * :Bob329\r\nJOIN #stream\r\nQUIT :Pipelined Bye\r\nPRIVMSG #stream :Ghost message\r\n

# Alice sees Bob join and quit
C1 WAIT_RECV :Bob329!* JOIN #stream
C1 WAIT_RECV :Bob329!* QUIT :Pipelined Bye

C2 EXPECT_DISCONNECT

# Alice verifies channel state is healthy
C1 SEND PRIVMSG #stream :Ali329 still here
C1 EXPECT_CONNECTED
