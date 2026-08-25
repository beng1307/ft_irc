# 03_MODE_key_space_injection.spec
# Vulnerability: MODE +k allows setting channel keys containing spaces, which corrupts parameter counts
# when broadcast to clients without quotes/colons.
# Expected secure behavior: Server must reject keys containing spaces (e.g. 525 ERR_INVALIDKEY or 461/error)
# and never broadcast a space-separated unquoted key.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Ali030
C1 SEND USER ali030 0 * :Ali030 Usr030
C1 EXPECT 001 Ali030 :*

C1 SEND JOIN #testchan
C1 WAIT_RECV :Ali030!* JOIN #testchan

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob030
C2 SEND USER bob030 0 * :Bob030 Usr030
C2 EXPECT 001 Bob030 :*

C2 SEND JOIN #testchan
C2 WAIT_RECV :Bob030!* JOIN #testchan

# Alice attempts to set a multi-word key with spaces
C1 SEND MODE #testchan +k :secret pass with spaces
C1 EXPECT 525 * #testchan :*

# Verify Bob did not receive a broken unquoted multi-word MODE message
C2 EXPECT_NONE 200ms

C1 SEND QUIT :bye
C2 SEND QUIT :bye
C1 EXPECT ERROR :*
C2 EXPECT ERROR :*



