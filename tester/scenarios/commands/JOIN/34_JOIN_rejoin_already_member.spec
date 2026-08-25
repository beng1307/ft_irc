# 34_JOIN_rejoin_already_member.spec
# Tests re-sending JOIN for a channel the client is already joined to
# Expected: Server sends names list (353 / 366) to resync state without duplicate broadcast to other members.
# Bug: Server silently returns early, omitting names list replies.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Both join #syncchan
C1 SEND JOIN #syncchan
C1 EXPECT 353 Alice = #syncchan :*
C1 EXPECT 366 Alice #syncchan :End of /NAMES list

C2 SEND JOIN #syncchan
C1 WAIT_RECV :Bob!* JOIN #syncchan

# C1 re-sends JOIN #syncchan to refresh member list
C1 SEND JOIN #syncchan
C1 EXPECT 353 Alice = #syncchan :*
C1 EXPECT 366 Alice #syncchan :End of /NAMES list

# C2 should NOT receive a duplicate JOIN broadcast
C2 EXPECT_NONE 200ms
