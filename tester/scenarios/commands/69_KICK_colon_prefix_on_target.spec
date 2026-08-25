# 69_KICK_colon_prefix_on_target.spec
# Tests RFC 2812 §2.3.1 trailing parameter colon prefix syntax on target nick (KICK #lobby :Bob).
# Expected: Server strips the leading colon from the target argument, identifies Bob, and kicks him.
# Bug: Server treats ':Bob' as literal nickname, searches for client ':Bob', and returns 401 ERR_NOSUCHNICK (:Bob :No such nick/channel).
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

# Alice kicks Bob using colon prefix on trailing target argument
C1 SEND KICK #lobby :Bob
C1 EXPECT :Alice!* KICK #lobby Bob :Alice
C2 EXPECT :Alice!* KICK #lobby Bob :Alice
