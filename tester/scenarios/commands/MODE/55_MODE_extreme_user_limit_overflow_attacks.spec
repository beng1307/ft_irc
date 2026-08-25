# 55_MODE_extreme_user_limit_overflow_attacks.spec
# Adversarial Attack: Sending extreme, negative, overflowing, or malformed numeric parameters for +l.
# Expected: Server validates limits strictly as positive integers, rejects malicious strings with 461, and enforces legitimate limits.
CLIENTS C1, C2, C3, C4

# C1 is Ali055
C1 SEND PASS 1234
C1 SEND NICK Ali055
C1 SEND USER ali055 0 * :Ali055
C1 EXPECT 001 Ali055 :*

# C2 is Bob055
C2 SEND PASS 1234
C2 SEND NICK Bob172
C2 SEND USER bob172 0 * :Bob172
C2 EXPECT 001 Bob172 :*

# C3 is Cha055
C3 SEND PASS 1234
C3 SEND NICK Cha055
C3 SEND USER cha055 0 * :Cha055
C3 EXPECT 001 Cha055 :*

# C4 is Dav055
C4 SEND PASS 1234
C4 SEND NICK Dav055
C4 SEND USER dav055 0 * :Dav055
C4 EXPECT 001 Dav055 :*

C1 SEND JOIN #limitlab55
C1 EXPECT 353 Ali055 = #limitlab55 :@Ali055
C1 EXPECT 366 Ali055 #limitlab55 :End of /NAMES list

# Attack 1: Negative limit
C1 SEND MODE #limitlab55 +l -5
C1 EXPECT 461 Ali055 MODE :Not enough parameters

# Attack 2: Zero limit
C1 SEND MODE #limitlab55 +l 0
C1 EXPECT 461 Ali055 MODE :Not enough parameters

# Attack 3: Leading zeroes / malformed format
C1 SEND MODE #limitlab55 +l 007
C1 EXPECT 461 Ali055 MODE :Not enough parameters

# Attack 4: 64-bit integer overflow string
C1 SEND MODE #limitlab55 +l 99999999999999999999999999999999
C1 EXPECT 461 Ali055 MODE :Not enough parameters

# Bob and Charlie join (occupancy = 3)
C2 SEND JOIN #limitlab55
C1 WAIT_RECV :Bob172!* JOIN #limitlab55

C3 SEND JOIN #limitlab55
C1 WAIT_RECV :Cha055!* JOIN #limitlab55

# Set legitimate limit below current occupancy (+l 2)
C1 SEND MODE #limitlab55 +l 2
C1 EXPECT :Ali055!* MODE #limitlab55 +l 2

# Existing 3 members must remain intact; 4th member Dave must be rejected with 471 (+l)
C4 SEND JOIN #limitlab55
C4 EXPECT 471 Dav055 #limitlab55 :Cannot join channel (+l)
