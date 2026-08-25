# 51_MODE_parameter_stealing_invalid_limit.spec
# Tests parameter misalignment/stealing when an invalid limit parameter is followed by key parameter (e.g. MODE #chan +l+k invalid_limit mykey)
# Expected: Command fails without setting channel key; subsequent client can join without providing a key.
# Bug: apply_mode_limit sends 461 but apply_mode_key succeeds using mykey, corrupting channel state so regular joins fail with 475 (+k).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

# Issue invalid limit with key
C1 SEND MODE #chan +l+k invalid_limit mykey
C1 EXPECT 461 Alice MODE :Not enough parameters

# Bob attempts to join without key; should succeed since key should not have been set
C2 SEND JOIN #chan
C2 EXPECT 353 Bob = #chan :*Bob*
C2 EXPECT 366 Bob #chan :End of /NAMES list
