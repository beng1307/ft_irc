# 54_MODE_special_char_and_control_char_fuzzing.spec
# Adversarial Fuzzing: Sending redundant signs, invalid symbols, and mixed mode characters.
# Expected: Server safely handles arbitrary character sequences, returns 472 for unknown flags, and remains stable.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali171
C1 SEND USER ali171 0 * :Ali171
C1 EXPECT 001 Ali171 :*

C1 SEND JOIN #fuzz
C1 EXPECT 353 Ali171 = #fuzz :@Ali171
C1 EXPECT 366 Ali171 #fuzz :End of /NAMES list

# Fuzz with consecutive signs
C1 SEND MODE #fuzz +++++
# Expected: No mode changes or errors, server remains healthy
C1 SEND PING fuzz1
C1 EXPECT :localhost PONG localhost :fuzz1

# Fuzz with alternating signs and unknown symbols
C1 SEND MODE #fuzz +!-?#$
C1 EXPECT 472 Ali171 ! :is unknown mode char to me

# Fuzz with mixed valid and invalid flags
C1 SEND MODE #fuzz +iz
C1 EXPECT 472 Ali171 z :is unknown mode char to me
# +i was valid and applied
C1 EXPECT :Ali171!* MODE #fuzz +i

# Verify server state is intact
C1 SEND MODE #fuzz
C1 EXPECT 324 Ali171 #fuzz +*i*
