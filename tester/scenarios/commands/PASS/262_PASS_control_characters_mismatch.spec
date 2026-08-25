# 262_PASS_control_characters_mismatch.spec
# Binary / control characters in PASS payload must mismatch and return 464
CLIENTS C1

C1 SEND_RAW PASS \x01\x02\x03\x04\r\n
C1 EXPECT 464 * :Password incorrect
