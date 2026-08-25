# 213_QUIT_immediate_nick_reuse.spec
# Tests that as soon as a client sends QUIT, their nickname is immediately freed and available for a new client.
CLIENTS C1, C2

# Alice connects
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Alice quits
C1 SEND QUIT :Freeing my nick
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob connects and claims "Alice"
C2 SEND PASS 1234
C2 SEND NICK Alice
C2 SEND USER alice2 0 * :Alice2
C2 EXPECT 001 Alice :*
