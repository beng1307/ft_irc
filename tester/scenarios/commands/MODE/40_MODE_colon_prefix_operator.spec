# 40_MODE_colon_prefix_operator.spec
# Tests promoting channel operator with colon prefix on target nickname (e.g. MODE #chan +o :Bob)
# Expected: Server strips the colon prefix and promotes Bob, broadcasting MODE #chan +o Bob.
# Bug: Server searches for client with literal nickname ":Bob" and returns 401 :Bob :No such nick/channel.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob!* JOIN #chan

# Promote Bob with colon prefix
C1 SEND MODE #chan +o :Bob
C1 EXPECT :Alice!* MODE #chan +o Bob
C2 EXPECT :Alice!* MODE #chan +o Bob
