# 111_PRIVMSG_ctcp_action.spec
# Tests CTCP ACTION message encapsulation transparent delivery
# Expected: CTCP message (\x01ACTION smiles\x01) delivered intact to channel members
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

# Join channel #chan
C1 SEND JOIN #chan
C1 EXPECT 366 Alice #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob!* JOIN #chan

# C1 sends CTCP ACTION
C1 SEND PRIVMSG #chan :\x01ACTION waves hello\x01
C2 WAIT_RECV :Alice!* PRIVMSG #chan :\x01ACTION waves hello\x01
