# 03_NICK_case_sensitivity_collision.spec
# Tests RFC 1459/2812 case-insensitivity collision rules (NickAlice03 == nickalice03).
# Expected: C2 receives 433 Nickname is already in use when requesting 'nickalice03' while C1 is registered as 'NickAlice03'.
# Bug: The server uses case-sensitive comparison (c.get_nickname() == nick), allowing both NickAlice03 and nickalice03 to register simultaneously.
CLIENTS C1, C2

# C1 registers as Alice03
C1 SEND PASS 1234
C1 SEND NICK Ali185
C1 SEND USER u185 0 * :Ali185 03
C1 EXPECT 001 Ali185 :*

# C2 attempts to register as lowercase 'alice03'
C2 SEND PASS 1234
C2 SEND NICK ali185
C2 EXPECT 433 * ali185 :Nickname is already in use

