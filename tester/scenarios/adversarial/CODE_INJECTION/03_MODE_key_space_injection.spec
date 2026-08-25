# 03_MODE_key_space_injection.spec
# Vulnerability: MODE +k allows setting channel keys containing spaces, which corrupts parameter counts
# when broadcast to clients without quotes/colons.
# Expected secure behavior: Server must reject keys containing spaces (e.g. 525 ERR_INVALIDKEY or 461/error)
# and never broadcast a space-separated unquoted key.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice User
C1 EXPECT 001 Alice :*

C1 SEND JOIN #testchan
C1 WAIT_RECV :Alice!* JOIN #testchan

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob User
C2 EXPECT 001 Bob :*

C2 SEND JOIN #testchan
C2 WAIT_RECV :Bob!* JOIN #testchan

# Alice attempts to set a multi-word key with spaces
C1 SEND MODE #testchan +k :secret pass with spaces
C1 EXPECT 525 * #testchan :*

# Verify Bob did not receive a broken unquoted multi-word MODE message
C2 EXPECT_NONE 200ms
