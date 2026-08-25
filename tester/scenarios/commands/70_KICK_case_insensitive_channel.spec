# 70_KICK_case_insensitive_channel.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on channel names during KICK.
# Expected: Server treats #SecretLobby and #secretlobby as identical channels, successfully kicking Bob.
# Bug: Server performs case-sensitive lookup on channel map, failing with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice registers and creates mixed-case channel
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #SecretLobby
C1 EXPECT :Alice!* JOIN #SecretLobby

# Bob registers and joins mixed-case channel
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #SecretLobby
C2 EXPECT :Bob!* JOIN #SecretLobby
C1 WAIT_RECV :Bob!* JOIN #SecretLobby

# Alice kicks Bob using lowercase channel name #secretlobby
C1 SEND KICK #secretlobby Bob :rules
C1 EXPECT :Alice!* KICK #SecretLobby Bob :rules
C2 EXPECT :Alice!* KICK #SecretLobby Bob :rules
