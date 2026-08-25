# 45_MODE_key_blind_overwrite.spec
# Tests RFC requirement that setting a channel key when one is already active must be rejected with 467 ERR_KEYSET.
# Expected: Server returns 467 ERR_KEYSET :Channel key already set.
# Bug: Server silently overwrites the channel key without returning ERR_KEYSET.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali162
C1 SEND USER ali162 0 * :Ali162
C1 EXPECT 001 Ali162 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali162 = #chan :@Ali162
C1 EXPECT 366 Ali162 #chan :End of /NAMES list

# Set initial key
C1 SEND MODE #chan +k key1
C1 EXPECT :Ali162!* MODE #chan +k key1

# Attempt to overwrite key without removing it first
C1 SEND MODE #chan +k key2
C1 EXPECT 467 Ali162 #chan :Channel key already set
