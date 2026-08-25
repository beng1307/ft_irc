# 96_PRIVMSG_ampersand_channel_routing.spec
# Tests PRIVMSG routing to '&' prefixed server-local channels
# Expected: Members of &local receive PRIVMSG sent to &local
# Bug: PRIVMSG only checks target[0] == '#', so '&local' is treated as a user nick and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali310
C1 SEND USER ali310 0 * :Ali310
C1 EXPECT 001 Ali310 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob310
C2 SEND USER bob310 0 * :Bob310
C2 EXPECT 001 Bob310 :*

# Both join &local
C1 SEND JOIN &local
C1 EXPECT 353 Ali310 = &local :*Ali310*
C1 EXPECT 366 Ali310 &local :End of /NAMES list

C2 SEND JOIN &local
C1 WAIT_RECV :Bob310!* JOIN &local

# C1 sends PRIVMSG to &local
C1 SEND PRIVMSG &local :Hello local channel
C2 WAIT_RECV :Ali310!* PRIVMSG &local :Hello local channel
