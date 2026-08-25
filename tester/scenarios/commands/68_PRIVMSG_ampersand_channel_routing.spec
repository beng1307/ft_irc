# 38_PRIVMSG_ampersand_channel_routing.spec
# Tests PRIVMSG routing to '&' prefixed server-local channels
# Expected: Members of &local receive PRIVMSG sent to &local
# Bug: PRIVMSG only checks target[0] == '#', so '&local' is treated as a user nick and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Both join &local
C1 SEND JOIN &local
C1 EXPECT 353 Alice = &local :*Alice*
C1 EXPECT 366 Alice &local :End of /NAMES list

C2 SEND JOIN &local
C1 WAIT_RECV :Bob!* JOIN &local

# C1 sends PRIVMSG to &local
C1 SEND PRIVMSG &local :Hello local channel
C2 WAIT_RECV :Alice!* PRIVMSG &local :Hello local channel
