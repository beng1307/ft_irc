# 42_MODE_colon_prefix_key_and_param.spec
# Tests setting channel key with leading colon prefix (e.g. MODE #chan +k :secret123)
# Expected: Server strips the colon prefix and stores the key as "secret123", allowing clients to join with key "secret123".
# Bug: Server stores key literally as ":secret123". A client attempting to join with "JOIN #chan secret123" is rejected with 475 (+k).
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

# Set key with leading colon parameter
C1 SEND MODE #chan +k :secret123
C1 EXPECT :Alice!* MODE #chan +k secret123

# Bob joins using key without colon
C2 SEND JOIN #chan secret123
C2 EXPECT 353 Bob = #chan :*Bob*
C2 EXPECT 366 Bob #chan :End of /NAMES list
