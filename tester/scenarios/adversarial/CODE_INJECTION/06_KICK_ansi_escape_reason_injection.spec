# 06_KICK_ansi_escape_reason_injection.spec
# Vulnerability: KICK reason is broadcast raw with terminal escape sequences,
# corrupting the kicked victim's terminal display or erasing kick logs.
# Expected secure behavior: Server must sanitize kick reasons before broadcasting.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Ali033
C1 SEND USER ali033 0 * :Ali033 Usr033
C1 EXPECT 001 Ali033 :*

C1 SEND JOIN #kickzone
C1 WAIT_RECV :Ali033!* JOIN #kickzone

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob033
C2 SEND USER bob033 0 * :Bob033 Usr033
C2 EXPECT 001 Bob033 :*

C2 SEND JOIN #kickzone
C2 WAIT_RECV :Bob033!* JOIN #kickzone

# Alice kicks Bob with an ANSI clear-screen / conceal sequence in reason
C1 SEND_RAW KICK #kickzone Bob033 :\x1b[2J\x1b[HReasonClean\r\n

# Secure server must strip the escape codes so Bob receives the clean string
C2 WAIT_RECV :Ali033!* KICK #kickzone Bob033 :ReasonClean
