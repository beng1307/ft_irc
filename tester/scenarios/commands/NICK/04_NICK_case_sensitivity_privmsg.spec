# 04_NICK_case_sensitivity_privmsg.spec
# Tests that message routing to nicknames is case-insensitive per RFC 1459/2812.
# Expected: Sending PRIVMSG NICKALICE04 routes successfully to registered user 'NickAlice04'.
# Bug: get_client("NICKALICE04") fails with case-sensitive lookup, returning 401 NICKALICE04 :No such nick/channel.
CLIENTS C1, C2

# C1 registers as NickAlice04
C1 SEND PASS 1234
C1 SEND NICK NickAlice04
C1 SEND USER user04 0 * :Alice 04
C1 EXPECT 001 NickAlice04 :*

# C2 registers as NickBob04
C2 SEND PASS 1234
C2 SEND NICK NickBob04
C2 SEND USER bob04 0 * :Bob 04
C2 EXPECT 001 NickBob04 :*

# C2 sends PRIVMSG with uppercase target 'NICKALICE04'
C2 SEND PRIVMSG NICKALICE04 :Hello Alice
C1 WAIT_RECV :NickBob04!* PRIVMSG NICKALICE04 :Hello Alice
