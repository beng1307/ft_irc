# 89_KICK_multi_target_batch.spec
# Tests RFC 2812 §3.2.8 comma-separated multi-user batch kick (KICK #lobby Bob,Charlie :batch).
# Expected: Server parses the comma-separated user list, kicking both Bob and Charlie.
# Bug: Server treats 'Bob,Charlie' as a single literal nickname, searching for client 'Bob,Charlie' and failing with 401 ERR_NOSUCHNICK.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali144
C1 SEND USER ali144 0 * :Ali144
C1 EXPECT 001 Ali144 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali144!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob144
C2 SEND USER bob144 0 * :Bob144
C2 EXPECT 001 Bob144 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob144!* JOIN #lobby
C1 WAIT_RECV :Bob144!* JOIN #lobby

# Charlie registers and joins #lobby
C3 SEND PASS 1234
C3 SEND NICK Cha144
C3 SEND USER cha144 0 * :Cha144
C3 EXPECT 001 Cha144 :*
C3 SEND JOIN #lobby
C3 EXPECT :Cha144!* JOIN #lobby
C1 WAIT_RECV :Cha144!* JOIN #lobby
C2 WAIT_RECV :Cha144!* JOIN #lobby

# Alice batch-kicks both Bob and Charlie
C1 SEND KICK #lobby Bob144,Cha144 :batch cleanup
C1 EXPECT :Ali144!* KICK #lobby Bob144 :batch cleanup
C1 EXPECT :Ali144!* KICK #lobby Cha144 :batch cleanup
C2 EXPECT :Ali144!* KICK #lobby Bob144 :batch cleanup
C3 EXPECT :Ali144!* KICK #lobby Cha144 :batch cleanup
