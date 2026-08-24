# 04_NICK_case_sensitivity_privmsg.spec
# Tests that message routing to nicknames is case-insensitive per RFC 1459/2812.
# Expected: Sending PRIVMSG ALICE routes successfully to registered user 'Alice'.
# Bug: get_client("ALICE") fails with case-sensitive lookup, returning 401 ALICE :No such nick/channel.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C2 sends PRIVMSG with uppercase target 'ALICE'
C2 SEND PRIVMSG ALICE :Hello Alice
C1 WAIT_RECV :Bob!* PRIVMSG ALICE :Hello Alice
