# 45_MODE_key_blind_overwrite.spec
# Tests RFC requirement that setting a channel key when one is already active must be rejected with 467 ERR_KEYSET.
# Expected: Server returns 467 ERR_KEYSET :Channel key already set.
# Bug: Server silently overwrites the channel key without returning ERR_KEYSET.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

# Set initial key
C1 SEND MODE #chan +k key1
C1 EXPECT :Alice!* MODE #chan +k key1

# Attempt to overwrite key without removing it first
C1 SEND MODE #chan +k key2
C1 EXPECT 467 Alice #chan :Channel key already set
