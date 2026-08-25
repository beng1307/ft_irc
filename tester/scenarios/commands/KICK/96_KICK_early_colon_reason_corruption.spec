# 96_KICK_early_colon_reason_corruption.spec
# Tests adversarial line construction where ' :' appears on earlier arguments (e.g. KICK #lobby96K :Bob :Real reason).
# Expected: Server correctly parses the channel as #lobby96K, target as Bob, and comment as 'Real reason', broadcasting ':Alice!* KICK #lobby96K Bob :Real reason'.
# Bug: Server extracts reason via line.strAfter(" :"), splitting at the first ' :' before Bob, causing the reason to become 'Bob :Real reason' and corrupting the broadcast.
CLIENTS C1, C2

# Alice registers and creates #lobby96K
C1 SEND PASS 1234
C1 SEND NICK Ali151
C1 SEND USER ali151 0 * :Ali151
C1 EXPECT 001 Ali151 :*
C1 SEND JOIN #lobby96K
C1 EXPECT :Ali151!* JOIN #lobby96K

# Bob registers and joins #lobby96K
C2 SEND PASS 1234
C2 SEND NICK Bob151
C2 SEND USER bob151 0 * :Bob151
C2 EXPECT 001 Bob151 :*
C2 SEND JOIN #lobby96K
C2 EXPECT :Bob151!* JOIN #lobby96K
C1 WAIT_RECV :Bob151!* JOIN #lobby96K

# Alice sends KICK with early colon on target argument
# RFC 2812 §2.3.1 treats ':Bob :Real reason' as a single trailing parameter (target nickname), resulting in 401 ERR_NOSUCHNICK
C1 SEND KICK #lobby96K :Bob151 :Real reason
C1 EXPECT 401 Ali151 Bob151 :Real reason :No such nick/channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

