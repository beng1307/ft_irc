# PRIVMSG rapid-fire: multiple messages from same sender in quick succession.
# Tests buffer handling and ensures no message loss or reordering.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali439
C1 SEND USER ali439 0 * :Ali439
C1 EXPECT 001 Ali439 :*

C2 SEND PASS 1234
C2 SEND NICK Bob439
C2 SEND USER bob439 0 * :Bob439
C2 EXPECT 001 Bob439 :*

# Send 10 messages rapidly
C1 SEND PRIVMSG Bob439 :Message 1
C1 SEND PRIVMSG Bob439 :Message 2
C1 SEND PRIVMSG Bob439 :Message 3
C1 SEND PRIVMSG Bob439 :Message 4
C1 SEND PRIVMSG Bob439 :Message 5
C1 SEND PRIVMSG Bob439 :Message 6
C1 SEND PRIVMSG Bob439 :Message 7
C1 SEND PRIVMSG Bob439 :Message 8
C1 SEND PRIVMSG Bob439 :Message 9
C1 SEND PRIVMSG Bob439 :Message 10

# All messages must be received in order
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 1
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 2
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 3
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 4
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 5
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 6
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 7
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 8
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 9
C2 WAIT_RECV :Ali439!* PRIVMSG Bob439 :Message 10

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
