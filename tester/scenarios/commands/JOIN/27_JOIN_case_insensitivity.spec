# 27_JOIN_case_insensitivity.spec
# Tests RFC case-insensitivity of channel names (e.g. #LOBBY27J == #lobby27J)
# Expected: C2 joining #lobby27J joins C1's existing #LOBBY27J channel; C1 receives JOIN broadcast and C2 sees Alice in names list.
# Bug: ChannelMap uses case-sensitive matching, creating two separate disjoint channels (#LOBBY27J and #lobby27J).
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali110
C1 SEND USER ali110 0 * :Ali110
C1 EXPECT 001 Ali110 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob110
C2 SEND USER bob110 0 * :Bob110
C2 EXPECT 001 Bob110 :*

# C1 joins #LOBBY27J (uppercase)
C1 SEND JOIN #LOBBY27J
C1 EXPECT 353 Ali110 = * :*Ali110*
C1 EXPECT 366 Ali110 * :End of /NAMES list

# C2 joins #lobby27J (lowercase) - should join the SAME channel
C2 SEND JOIN #lobby27J
C1 WAIT_RECV :Bob110!* JOIN *

# C2's names reply must contain Alice
C2 EXPECT 353 Bob110 = * :*Ali110*
C2 EXPECT 366 Bob110 * :End of /NAMES list
