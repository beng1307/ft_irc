# 51_MODE_unregistered_client_flood_attack.spec
# Adversarial Attack: Unregistered client attempts to query and modify modes before authentication.
# Expected: Server rejects all MODE attempts with 451 ERR_NOTREGISTERED without altering channel state.
CLIENTS C1, C2

# C2 creates channel #secure as Alice51
C2 SEND PASS 1234
C2 SEND NICK Ali168
C2 SEND USER ali168 0 * :Ali168
C2 EXPECT 001 Ali168 :*
C2 SEND JOIN #secure51
C2 EXPECT 353 Ali168 = #secure51 :@Ali168
C2 EXPECT 366 Ali168 #secure51 :End of /NAMES list

# C1 is unauthenticated attacker; floods MODE commands
C1 SEND MODE #secure51 +o Atk168
C1 EXPECT 451 * :You have not registered

C1 SEND MODE #secure51
C1 EXPECT 451 * :You have not registered

C1 SEND MODE Ali168 +i
C1 EXPECT 451 * :You have not registered

# Verify Alice51's channel #secure51 remains untouched
C2 SEND MODE #secure51
C2 EXPECT 324 Ali168 #secure51 +
