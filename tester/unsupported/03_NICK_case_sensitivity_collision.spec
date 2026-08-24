# 03_NICK_case_sensitivity_collision.spec
# Tests RFC 1459/2812 case-insensitivity collision rules (Alice == alice).
# Expected: C2 receives 433 Nickname is already in use when requesting 'alice' while C1 is registered as 'Alice'.
# Bug: The server uses case-sensitive comparison (c.get_nickname() == nick), allowing both Alice and alice to register simultaneously.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 attempts to register as lowercase 'alice'
C2 SEND PASS 1234
C2 SEND NICK alice
C2 EXPECT 433 * alice :Nickname is already in use
