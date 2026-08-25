# PRIVMSG during backpressure/slow client scenario.
# Client can't receive fast enough; server buffer builds up.
# Ensure PRIVMSG still works and no data is lost.

CLIENTS C1, C2_SLOW

C1 SEND PASS 1234
C1 SEND NICK Ali442
C1 SEND USER ali442 0 * :Ali442
C1 EXPECT 001 Ali442 :*

C2_SLOW SEND PASS 1234
C2_SLOW SEND NICK Bob442
C2_SLOW SEND USER bob442 0 * :Bob442
C2_SLOW EXPECT 001 Bob442 :*

# Send many messages rapidly
C1 SEND PRIVMSG Bob442 :Msg 1
C1 SEND PRIVMSG Bob442 :Msg 2
C1 SEND PRIVMSG Bob442 :Msg 3
C1 SEND PRIVMSG Bob442 :Msg 4
C1 SEND PRIVMSG Bob442 :Msg 5

# Slow client reads them (eventually all should arrive)
C2_SLOW WAIT_RECV :Ali442!* PRIVMSG Bob442 :Msg 1
C2_SLOW WAIT_RECV :Ali442!* PRIVMSG Bob442 :Msg 2
C2_SLOW WAIT_RECV :Ali442!* PRIVMSG Bob442 :Msg 3
C2_SLOW WAIT_RECV :Ali442!* PRIVMSG Bob442 :Msg 4
C2_SLOW WAIT_RECV :Ali442!* PRIVMSG Bob442 :Msg 5

# Verify connection is still alive
C1 SEND PING :test
C1 EXPECT PONG * :test
C2_SLOW EXPECT_CONNECTED
