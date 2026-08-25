# 62_MODE_empty_key_and_whitespace_key_handling.spec
# Edge Case: Attempting to set key with missing parameter or empty string.
# Expected: Server rejects missing key parameter with 461 MODE :Not enough parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice62
C1 SEND USER alice62 0 * :Alice62
C1 EXPECT 001 Alice62 :*

C1 SEND JOIN #emptykey
C1 EXPECT 353 Alice62 = #emptykey :@Alice62
C1 EXPECT 366 Alice62 #emptykey :End of /NAMES list

# Set key without providing key argument
C1 SEND MODE #emptykey +k
C1 EXPECT 461 Alice62 MODE :Not enough parameters

# Verify no key mode was set
C1 SEND MODE #emptykey
C1 EXPECT 324 Alice62 #emptykey +
