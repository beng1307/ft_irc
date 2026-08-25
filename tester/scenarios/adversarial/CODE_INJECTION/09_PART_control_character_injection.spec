# 09_PART_control_character_injection.spec
# Vulnerability: PART reason is relayed without control character filtering,
# permitting terminal escape codes to reach all members of the channel.
# Expected secure behavior: Server strips escape sequences from PART reason.
CLIENTS C1, C2

# Setup Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali036
C1 SEND USER ali036 0 * :Ali036 Usr036
C1 EXPECT 001 Ali036 :*

C2 SEND PASS 1234
C2 SEND NICK Bob036
C2 SEND USER bob036 0 * :Bob036 Usr036
C2 EXPECT 001 Bob036 :*

C1 SEND JOIN #partroom
C1 WAIT_RECV :Ali036!* JOIN #partroom

C2 SEND JOIN #partroom
C2 WAIT_RECV :Bob036!* JOIN #partroom

# Alice parts with ANSI escape codes in reason
C1 SEND_RAW PART #partroom :\x1b[31;1mLeavingColor\x1b[0m\r\n

# Secure server must deliver clean reason without raw ANSI codes
C2 WAIT_RECV :Ali036!* PART #partroom :LeavingColor
