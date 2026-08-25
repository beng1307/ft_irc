# 63_MODE_unset_modes_when_already_unset.spec
# Edge Case: Attempting to remove modes (-i-t-k-l) on a freshly created channel where none are set.
# Expected: Server processes command as a no-op without crashing, broadcasting empty changes, or corrupting state.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #fresh
C1 EXPECT 353 Alice = #fresh :@Alice
C1 EXPECT 366 Alice #fresh :End of /NAMES list

# Unset modes that are not set
C1 SEND MODE #fresh -i-t-k-l
C1 SEND PING freshping
C1 EXPECT :localhost PONG localhost :freshping

# Verify channel modes remain default
C1 SEND MODE #fresh
C1 EXPECT 324 Alice #fresh +
