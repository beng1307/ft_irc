# Require lossless delivery after a paused client fills the server send buffer.
CLIENTS C1, C2, C3
TIMEOUT 30s

# Register sender, paused recipient, and independent liveness probe.
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# All clients share the test channel.
C1 SEND JOIN #writequeue
C1 EXPECT :Alice!* JOIN #writequeue
C2 SEND JOIN #writequeue
C2 EXPECT :Bob!* JOIN #writequeue
C1 WAIT_RECV :Bob!* JOIN #writequeue
C3 SEND JOIN #writequeue
C3 EXPECT :Charlie!* JOIN #writequeue

# Stop receiving on C2 and reduce its advertised TCP receive window.
C2 SET_SOCK_RCVBUF 1024
C2 PAUSE

# 10,000 near-maximum IRC lines exceed a normal non-blocking send buffer.
C1 FLOOD 1   PRIVMSG #writequeue :Hello
# more needs longer timeout in testrunner.
# this already takes 30 sec.
C1 FLOOD 500 PRIVMSG #writequeue :ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ
C1 FLOOD 500 PRIVMSG #writequeue :GOOOOOOOOOOOOOOOOO
# A separate client must remain responsive while C2 is backpressured.
C3 SEND   PING   :write-queue-alive
C3 EXPECT PONG * :write-queue-alive

# Once C2 reads again, every broadcast must arrive exactly once.
C2 RESUME
C2 CONSUME :* PRIVMSG #writequeue :Hello

C2 CONSUME_COUNT  500 * PRIVMSG #writequeue :ABCDEFGHIJKLMNOPQRSTUVWXYZ* 
C2 CONSUME_COUNT  500 * PRIVMSG #writequeue :GOOOOO*
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
