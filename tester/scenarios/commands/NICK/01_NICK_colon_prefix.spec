# 01_NICK_colon_prefix.spec
# Tests standard RFC 1459/2812 trailing colon notation on NICK (e.g. NICK :NickAlice01)
# Expected: The server strips the leading colon and registers the client as NickAlice01.
# Bug: The server rejects ':NickAlice01' with 432 Erroneous nickname because ':' is not alphanumeric.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK :NickAlice01
C1 SEND USER user01 0 * :Nick Alice 01
C1 EXPECT 001 NickAlice01 :*
C1 EXPECT_CONNECTED
C1 SEND QUIT :bye
