# 04_NICK_case_sensitivity_privmsg.spec
# Tests that message routing to nicknames is case-insensitive per RFC 1459/2812.
# Expected: Sending PRIVMSG NICKALICE04 routes successfully to registered user 'NickAlice04'.
# Bug: get_client("NICKALICE04") fails with case-sensitive lookup, returning 401 NICKALICE04 :No such nick/channel.
CLIENTS C1, C2

# C1 registers as Alice04
C1 SEND PASS 1234
C1 SEND NICK Alice04
C1 SEND USER user04 0 * :Alice 04
C1 EXPECT 001 Alice04 :*

# C2 registers as Bob04
C2 SEND PASS 1234
C2 SEND NICK Bob04
C2 SEND USER bob04 0 * :Bob 04
C2 EXPECT 001 Bob04 :*

# C2 sends PRIVMSG with uppercase target 'ALICE04'
C2 SEND PRIVMSG ALICE04 :Hello Alice
C1 WAIT_RECV :Bob04!* PRIVMSG ALICE04 :Hello Alice

