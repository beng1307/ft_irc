# 187_PING_multi_word_without_colon.spec
# Tests multi-word PING without leading colon (e.g. PING token1 remote.server)
# Token1 is treated as the origin cookie; server replies with token1
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali273
C1 SEND USER ali273 0 * :Ali273 Smith
C1 EXPECT 001 Ali273 :*

C1 SEND PING cookie1 remote.server
C1 EXPECT :localhost PONG localhost :cookie1
