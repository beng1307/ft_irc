# 71_KICK_case_insensitive_target_nick.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on target nickname during KICK.
# Expected: Server matches target 'BOB' to registered user 'Bob' case-insensitively, kicking Bob.
# Bug: Server performs case-sensitive nickname lookup, failing with 401 ERR_NOSUCHNICK (BOB :No such nick/channel).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers with mixed-case nick 'Bob' and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice kicks Bob using uppercase 'BOB'
C1 SEND KICK #lobby BOB :case test
C1 EXPECT :Alice!* KICK #lobby Bob :case test
C2 EXPECT :Alice!* KICK #lobby Bob :case test
