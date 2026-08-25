# 83_KICK_case_insensitive_target_nick.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on target nickname during KICK.
# Expected: Server matches target 'BOB' to registered user 'Bob' case-insensitively, kicking Bob.
# Bug: Server performs case-sensitive nickname lookup, failing with 401 ERR_NOSUCHNICK (BOB :No such nick/channel).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali138
C1 SEND USER ali138 0 * :Ali138
C1 EXPECT 001 Ali138 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali138!* JOIN #lobby

# Bob registers with mixed-case nick 'Bob' and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob138
C2 SEND USER bob138 0 * :Bob138
C2 EXPECT 001 Bob138 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob138!* JOIN #lobby
C1 WAIT_RECV :Bob138!* JOIN #lobby

# Alice kicks Bob using uppercase 'BOB'
C1 SEND KICK #lobby BOB :case test
C1 EXPECT :Ali138!* KICK #lobby Bob138 :case test
C2 EXPECT :Ali138!* KICK #lobby Bob138 :case test
