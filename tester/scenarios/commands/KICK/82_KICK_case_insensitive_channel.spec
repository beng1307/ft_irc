# 82_KICK_case_insensitive_channel.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on channel names during KICK.
# Expected: Server treats #SecretLobby and #secretlobby as identical channels, successfully kicking Bob.
# Bug: Server performs case-sensitive lookup on channel map, failing with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice registers and creates mixed-case channel
C1 SEND PASS 1234
C1 SEND NICK Ali137
C1 SEND USER ali137 0 * :Ali137
C1 EXPECT 001 Ali137 :*
C1 SEND JOIN #SecretLobby
C1 EXPECT :Ali137!* JOIN #SecretLobby

# Bob registers and joins mixed-case channel
C2 SEND PASS 1234
C2 SEND NICK Bob137
C2 SEND USER bob137 0 * :Bob137
C2 EXPECT 001 Bob137 :*
C2 SEND JOIN #SecretLobby
C2 EXPECT :Bob137!* JOIN #SecretLobby
C1 WAIT_RECV :Bob137!* JOIN #SecretLobby

# Alice kicks Bob using lowercase channel name #secretlobby
C1 SEND KICK #secretlobby Bob137 :rules
C1 EXPECT :Ali137!* KICK #SecretLobby Bob137 :rules
C2 EXPECT :Ali137!* KICK #SecretLobby Bob137 :rules
