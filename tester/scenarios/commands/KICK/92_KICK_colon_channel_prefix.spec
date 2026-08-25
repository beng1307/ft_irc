# 92_KICK_colon_channel_prefix.spec
# Tests RFC 2812 §2.3 leading colon prefix on channel name parameter (KICK :#lobby Bob :reason).
# Expected: Server strips the colon prefix from the channel name and successfully kicks Bob.
# Bug: Server searches for channel ':#lobby' literally, failing with 403 ERR_NOSUCHCHANNEL (:#lobby :No such channel).
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

# Alice kicks Bob with colon-prefixed channel name
C1 SEND KICK :#lobby Bob :colon test
C1 EXPECT :Alice!* KICK #lobby Bob :colon test
C2 EXPECT :Alice!* KICK #lobby Bob :colon test
