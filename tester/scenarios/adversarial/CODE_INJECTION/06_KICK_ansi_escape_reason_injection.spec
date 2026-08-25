# 06_KICK_ansi_escape_reason_injection.spec
# Vulnerability: KICK reason is broadcast raw with terminal escape sequences,
# corrupting the kicked victim's terminal display or erasing kick logs.
# Expected secure behavior: Server must sanitize kick reasons before broadcasting.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice User
C1 EXPECT 001 Alice :*

C1 SEND JOIN #kickzone
C1 WAIT_RECV :Alice!* JOIN #kickzone

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob User
C2 EXPECT 001 Bob :*

C2 SEND JOIN #kickzone
C2 WAIT_RECV :Bob!* JOIN #kickzone

# Alice kicks Bob with an ANSI clear-screen / conceal sequence in reason
C1 SEND_RAW KICK #kickzone Bob :\x1b[2J\x1b[HReasonClean\r\n

# Secure server must strip the escape codes so Bob receives the clean string
C2 WAIT_RECV :Alice!* KICK #kickzone Bob :ReasonClean
