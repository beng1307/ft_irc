# 27_JOIN_case_insensitivity.spec
# Tests RFC case-insensitivity of channel names (e.g. #LOBBY == #lobby)
# Expected: C2 joining #lobby joins C1's existing #LOBBY channel; C1 receives JOIN broadcast and C2 sees Alice in names list.
# Bug: ChannelMap uses case-sensitive matching, creating two separate disjoint channels (#LOBBY and #lobby).
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 joins #LOBBY (uppercase)
C1 SEND JOIN #LOBBY
C1 EXPECT 353 Alice = * :*Alice*
C1 EXPECT 366 Alice * :End of /NAMES list

# C2 joins #lobby (lowercase) - should join the SAME channel
C2 SEND JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN *

# C2's names reply must contain Alice
C2 EXPECT 353 Bob = * :*Alice*
C2 EXPECT 366 Bob * :End of /NAMES list
