# 25_JOIN_key_colon_prefix.spec
# Tests joining a key-protected channel using colon notation on the key (e.g. JOIN #locked :secretpass)
# Expected: Server strips the leading colon from the key and permits the join.
# Bug: Server parses the key as ':secretpass' which does not equal 'secretpass', failing with 475 (+k).
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali108
C1 SEND USER ali108 0 * :Ali108
C1 EXPECT 001 Ali108 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob108
C2 SEND USER bob108 0 * :Bob108
C2 EXPECT 001 Bob108 :*

# C1 creates channel and sets key 'secretpass'
C1 SEND JOIN #locked
C1 EXPECT 353 Ali108 = #locked :*
C1 EXPECT 366 Ali108 #locked :End of /NAMES list

C1 SEND MODE #locked +k secretpass
C1 EXPECT :Ali108!* MODE #locked +k secretpass

# C2 joins using colon prefix on key parameter
C2 SEND JOIN #locked :secretpass
C2 EXPECT :Bob108!* JOIN #locked
C2 EXPECT 353 Bob108 = #locked :*
C2 EXPECT 366 Bob108 #locked :End of /NAMES list
C1 WAIT_RECV :Bob108!* JOIN #locked
