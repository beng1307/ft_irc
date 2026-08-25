# 96_KICK_early_colon_reason_corruption.spec
# Tests adversarial line construction where ' :' appears on earlier arguments (e.g. KICK #lobby :Bob :Real reason).
# Expected: Server correctly parses the channel as #lobby, target as Bob, and comment as 'Real reason', broadcasting ':Alice!* KICK #lobby Bob :Real reason'.
# Bug: Server extracts reason via line.strAfter(" :"), splitting at the first ' :' before Bob, causing the reason to become 'Bob :Real reason' and corrupting the broadcast.
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

# Alice sends KICK with early colon on target argument
# RFC 2812 §2.3.1 treats ':Bob :Real reason' as a single trailing parameter (target nickname), resulting in 401 ERR_NOSUCHNICK
C1 SEND KICK #lobby :Bob :Real reason
C1 EXPECT 401 Alice Bob :Real reason :No such nick/channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

