# 58_MODE_rapid_pipelined_state_toggle_storm.spec
# Stress / Adversarial Pipeline: Rapid storm of alternating MODE flags in a single TCP transmission.
# Expected: Server processes commands sequentially without buffer corruption or dropped state transitions.
CLIENTS C1, C2

# C1 is Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #storm
C1 EXPECT 353 Alice = #storm :@Alice
C1 EXPECT 366 Alice #storm :End of /NAMES list

C2 SEND JOIN #storm
C1 WAIT_RECV :Bob!* JOIN #storm

# Send pipelined mode toggles
C1 SEND_RAW MODE #storm +i\r\nMODE #storm -i\r\nMODE #storm +t\r\nMODE #storm -t\r\nMODE #storm +k keypass\r\nMODE #storm -k\r\n

# Verify final clean state (all toggles ended in removal)
C1 SEND MODE #storm
C1 EXPECT 324 Alice #storm +
