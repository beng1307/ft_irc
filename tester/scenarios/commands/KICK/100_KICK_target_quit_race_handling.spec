# 100_KICK_target_quit_race_handling.spec
# Tests race condition where target user disconnects/quits immediately before KICK command is processed.
# Expected: Server returns 401 ERR_NOSUCHNICK without crashing on dead client pointer.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Bob quits the server
C2 SEND QUIT :Leaving server
C2 EXPECT ERROR :Closing connection
C1 WAIT_RECV :Bob!* QUIT :Leaving server

# Alice attempts to kick Bob after Bob disconnected
C1 SEND KICK #lobby Bob :Too late
C1 EXPECT 401 Alice Bob :No such nick/channel
