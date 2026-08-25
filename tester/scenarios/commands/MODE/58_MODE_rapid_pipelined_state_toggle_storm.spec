# 58_MODE_rapid_pipelined_state_toggle_storm.spec
# Stress / Adversarial Pipeline: Rapid storm of alternating MODE flags in a single TCP transmission.
# Expected: Server processes commands sequentially without buffer corruption or dropped state transitions.
CLIENTS C1, C2

# C1 is Alice
C1 SEND PASS 1234
C1 SEND NICK Ali175
C1 SEND USER ali175 0 * :Ali175
C1 EXPECT 001 Ali175 :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob175
C2 SEND USER bob175 0 * :Bob175
C2 EXPECT 001 Bob175 :*

C1 SEND JOIN #storm
C1 EXPECT 353 Ali175 = #storm :@Ali175
C1 EXPECT 366 Ali175 #storm :End of /NAMES list

C2 SEND JOIN #storm
C1 WAIT_RECV :Bob175!* JOIN #storm

# Send pipelined mode toggles
C1 SEND_RAW MODE #storm +i\r\nMODE #storm -i\r\nMODE #storm +t\r\nMODE #storm -t\r\nMODE #storm +k keypass\r\nMODE #storm -k\r\n

# Verify final clean state (all toggles ended in removal)
C1 SEND MODE #storm
C1 EXPECT 324 Ali175 #storm +
