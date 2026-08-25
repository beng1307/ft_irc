# 39_MODE_colon_prefix_key_and_param.spec
# Tests setting channel key with leading colon prefix (e.g. MODE #chan +k :secret123)
# Expected: Server strips the colon prefix and stores the key as "secret123", allowing clients to join with key "secret123".
# Bug: Server stores key literally as ":secret123". A client attempting to join with "JOIN #chan secret123" is rejected with 475 (+k).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali156
C1 SEND USER ali156 0 * :Ali156
C1 EXPECT 001 Ali156 :*

C2 SEND PASS 1234
C2 SEND NICK Bob156
C2 SEND USER bob156 0 * :Bob156
C2 EXPECT 001 Bob156 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali156 = #chan :@Ali156
C1 EXPECT 366 Ali156 #chan :End of /NAMES list

# Set key with leading colon parameter
C1 SEND MODE #chan +k :secret123
C1 EXPECT :Ali156!* MODE #chan +k secret123

# Bob joins using key without colon
C2 SEND JOIN #chan secret123
C2 EXPECT 353 Bob156 = #chan :*Bob156*
C2 EXPECT 366 Bob156 #chan :End of /NAMES list
