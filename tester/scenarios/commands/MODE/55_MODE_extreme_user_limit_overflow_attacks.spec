# 55_MODE_extreme_user_limit_overflow_attacks.spec
# Adversarial Attack: Sending extreme, negative, overflowing, or malformed numeric parameters for +l.
# Expected: Server validates limits strictly as positive integers, rejects malicious strings with 461, and enforces legitimate limits.
CLIENTS C1, C2, C3, C4

# C1 is Alice55
C1 SEND PASS 1234
C1 SEND NICK Alice55
C1 SEND USER alice55 0 * :Alice55
C1 EXPECT 001 Alice55 :*

# C2 is Bob55
C2 SEND PASS 1234
C2 SEND NICK Bob55
C2 SEND USER bob55 0 * :Bob55
C2 EXPECT 001 Bob55 :*

# C3 is Charlie55
C3 SEND PASS 1234
C3 SEND NICK Charlie55
C3 SEND USER charlie55 0 * :Charlie55
C3 EXPECT 001 Charlie55 :*

# C4 is Dave55
C4 SEND PASS 1234
C4 SEND NICK Dave55
C4 SEND USER dave55 0 * :Dave55
C4 EXPECT 001 Dave55 :*

C1 SEND JOIN #limitlab55
C1 EXPECT 353 Alice55 = #limitlab55 :@Alice55
C1 EXPECT 366 Alice55 #limitlab55 :End of /NAMES list

# Attack 1: Negative limit
C1 SEND MODE #limitlab55 +l -5
C1 EXPECT 461 Alice55 MODE :Not enough parameters

# Attack 2: Zero limit
C1 SEND MODE #limitlab55 +l 0
C1 EXPECT 461 Alice55 MODE :Not enough parameters

# Attack 3: Leading zeroes / malformed format
C1 SEND MODE #limitlab55 +l 007
C1 EXPECT 461 Alice55 MODE :Not enough parameters

# Attack 4: 64-bit integer overflow string
C1 SEND MODE #limitlab55 +l 99999999999999999999999999999999
C1 EXPECT 461 Alice55 MODE :Not enough parameters

# Bob and Charlie join (occupancy = 3)
C2 SEND JOIN #limitlab55
C1 WAIT_RECV :Bob55!* JOIN #limitlab55

C3 SEND JOIN #limitlab55
C1 WAIT_RECV :Charlie55!* JOIN #limitlab55

# Set legitimate limit below current occupancy (+l 2)
C1 SEND MODE #limitlab55 +l 2
C1 EXPECT :Alice55!* MODE #limitlab55 +l 2

# Existing 3 members must remain intact; 4th member Dave must be rejected with 471 (+l)
C4 SEND JOIN #limitlab55
C4 EXPECT 471 Dave55 #limitlab55 :Cannot join channel (+l)
