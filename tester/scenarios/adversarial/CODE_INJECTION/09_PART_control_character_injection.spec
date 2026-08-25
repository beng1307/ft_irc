# 09_PART_control_character_injection.spec
# Vulnerability: PART reason is relayed without control character filtering,
# permitting terminal escape codes to reach all members of the channel.
# Expected secure behavior: Server strips escape sequences from PART reason.
CLIENTS C1, C2

# Setup Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice User
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob User
C2 EXPECT 001 Bob :*

C1 SEND JOIN #partroom
C1 WAIT_RECV :Alice!* JOIN #partroom

C2 SEND JOIN #partroom
C2 WAIT_RECV :Bob!* JOIN #partroom

# Alice parts with ANSI escape codes in reason
C1 SEND_RAW PART #partroom :\x1b[31;1mLeavingColor\x1b[0m\r\n

# Secure server must deliver clean reason without raw ANSI codes
C2 WAIT_RECV :Alice!* PART #partroom :LeavingColor
