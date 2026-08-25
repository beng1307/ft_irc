# 100_KICK_target_quit_race_handling.spec
# Tests race condition where target user disconnects/quits immediately before KICK command is processed.
# Expected: Server returns 401 ERR_NOSUCHNICK without crashing on dead client pointer.
CLIENTS C1, C2

# Alice registers and creates #lobby100K
C1 SEND PASS 1234
C1 SEND NICK Ali121
C1 SEND USER ali121 0 * :Ali121
C1 EXPECT 001 Ali121 :*
C1 SEND JOIN #lobby100K
C1 EXPECT :Ali121!* JOIN #lobby100K

# Bob registers and joins #lobby100K
C2 SEND PASS 1234
C2 SEND NICK Bob121
C2 SEND USER bob121 0 * :Bob121
C2 EXPECT 001 Bob121 :*
C2 SEND JOIN #lobby100K
C2 EXPECT :Bob121!* JOIN #lobby100K
C1 WAIT_RECV :Bob121!* JOIN #lobby100K

# Bob quits the server
C2 SEND QUIT :Leaving server
C2 EXPECT ERROR :Closing connection
C1 WAIT_RECV :Bob121!* QUIT :Leaving server

# Alice attempts to kick Bob after Bob disconnected
C1 SEND KICK #lobby100K Bob121 :Too late
C1 EXPECT 401 Ali121 Bob121 :No such nick/channel
