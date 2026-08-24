# PRIVMSG during backpressure/slow client scenario.
# Client can't receive fast enough; server buffer builds up.
# Ensure PRIVMSG still works and no data is lost.

CLIENTS C1, C2_SLOW

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2_SLOW SEND PASS 1234
C2_SLOW SEND NICK Bob
C2_SLOW SEND USER bob 0 * :Bob
C2_SLOW EXPECT 001 Bob :*

# Send many messages rapidly
C1 SEND PRIVMSG Bob :Msg 1
C1 SEND PRIVMSG Bob :Msg 2
C1 SEND PRIVMSG Bob :Msg 3
C1 SEND PRIVMSG Bob :Msg 4
C1 SEND PRIVMSG Bob :Msg 5

# Slow client reads them (eventually all should arrive)
C2_SLOW WAIT_RECV :Alice!* PRIVMSG Bob :Msg 1
C2_SLOW WAIT_RECV :Alice!* PRIVMSG Bob :Msg 2
C2_SLOW WAIT_RECV :Alice!* PRIVMSG Bob :Msg 3
C2_SLOW WAIT_RECV :Alice!* PRIVMSG Bob :Msg 4
C2_SLOW WAIT_RECV :Alice!* PRIVMSG Bob :Msg 5

# Verify connection is still alive
C1 SEND PING :test
C1 EXPECT PONG * :test
C2_SLOW EXPECT_CONNECTED
