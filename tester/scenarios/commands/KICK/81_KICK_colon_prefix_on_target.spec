# 81_KICK_colon_prefix_on_target.spec
# Tests RFC 2812 §2.3.1 trailing parameter colon prefix syntax on target nick (KICK #lobby :Bob).
# Expected: Server strips the leading colon from the target argument, identifies Bob, and kicks him.
# Bug: Server treats ':Bob' as literal nickname, searches for client ':Bob', and returns 401 ERR_NOSUCHNICK (:Bob :No such nick/channel).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali136
C1 SEND USER ali136 0 * :Ali136
C1 EXPECT 001 Ali136 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali136!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob136
C2 SEND USER bob136 0 * :Bob136
C2 EXPECT 001 Bob136 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob136!* JOIN #lobby
C1 WAIT_RECV :Bob136!* JOIN #lobby

# Alice kicks Bob using colon prefix on trailing target argument
C1 SEND KICK #lobby :Bob136
C1 EXPECT :Ali136!* KICK #lobby Bob136 :Ali136
C2 EXPECT :Ali136!* KICK #lobby Bob136 :Ali136
