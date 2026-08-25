# 92_KICK_colon_channel_prefix.spec
# Tests RFC 2812 §2.3 leading colon prefix on channel name parameter (KICK :#lobby Bob :reason).
# Expected: Server strips the colon prefix from the channel name and successfully kicks Bob.
# Bug: Server searches for channel ':#lobby' literally, failing with 403 ERR_NOSUCHCHANNEL (:#lobby :No such channel).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali147
C1 SEND USER ali147 0 * :Ali147
C1 EXPECT 001 Ali147 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali147!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob147
C2 SEND USER bob147 0 * :Bob147
C2 EXPECT 001 Bob147 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob147!* JOIN #lobby
C1 WAIT_RECV :Bob147!* JOIN #lobby

# Alice kicks Bob with colon-prefixed channel name
C1 SEND KICK :#lobby Bob147 :colon test
C1 EXPECT :Ali147!* KICK #lobby Bob147 :colon test
C2 EXPECT :Ali147!* KICK #lobby Bob147 :colon test
