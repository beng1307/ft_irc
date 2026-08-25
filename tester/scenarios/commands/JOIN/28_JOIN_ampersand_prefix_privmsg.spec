# 28_JOIN_ampersand_prefix_privmsg.spec
# Tests RFC channel prefix '&' (server-local channels) interoperability with PRIVMSG
# Expected: Clients can join '&local' and exchange PRIVMSG messages within the channel.
# Bug: JOIN accepts '&local', but PRIVMSG only routes '#' channels and treats '&local' as a user nick (401 :No such nick/channel).
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali111
C1 SEND USER ali111 0 * :Ali111
C1 EXPECT 001 Ali111 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob111
C2 SEND USER bob111 0 * :Bob111
C2 EXPECT 001 Bob111 :*

# Both join &local
C1 SEND JOIN &local
C1 EXPECT 353 Ali111 = &local :*Ali111*
C1 EXPECT 366 Ali111 &local :End of /NAMES list

C2 SEND JOIN &local
C1 WAIT_RECV :Bob111!* JOIN &local

# C1 sends a message to &local
C1 SEND PRIVMSG &local :Hello channel
C2 WAIT_RECV :Ali111!* PRIVMSG &local :Hello channel
