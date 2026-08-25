# 77_INVITE_channel_existence_oracle_leak.spec
# Tests information leakage / oracle behavior: An attacker probes whether channels exist using INVITE.
# Expected: Server sends 403 ERR_NOSUCHCHANNEL if the channel does not exist, and 442 ERR_NOTONCHANNEL if the channel exists but sender is not a member.
CLIENTS C1, C2

# Alice creates secret channel #hidden77
C1 SEND PASS 1234
C1 SEND NICK Ali102
C1 SEND USER ali102 0 * :Ali102
C1 EXPECT 001 Ali102 :*
C1 SEND JOIN #hidden77
C1 EXPECT :Ali102!* JOIN #hidden77

# Attacker Mallory connects
C2 SEND PASS 1234
C2 SEND NICK Mal102
C2 SEND USER mal102 0 * :Mal102
C2 EXPECT 001 Mal102 :*

# Mallory probes non-existent channel -> 403 ERR_NOSUCHCHANNEL
C2 SEND INVITE Ali102 #fakedoor77
C2 EXPECT 403 Mal102 #fakedoor77 :No such channel

# Mallory probes existing channel she is not on -> 442 ERR_NOTONCHANNEL (confirms channel exists)
C2 SEND INVITE Ali102 #hidden77
C2 EXPECT 442 Mal102 #hidden77 :You're not on that channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
