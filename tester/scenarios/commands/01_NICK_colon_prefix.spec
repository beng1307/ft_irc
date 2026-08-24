# 01_NICK_colon_prefix.spec
# Tests standard RFC 1459/2812 trailing colon notation on NICK (e.g. NICK :Alice)
# Expected: The server strips the leading colon and registers the client as Alice.
# Bug: The server rejects ':Alice' with 432 Erroneous nickname because ':' is not alphanumeric.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK :Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 EXPECT_CONNECTED
