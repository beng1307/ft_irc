# 210_QUIT_sole_member_channel_destroyed.spec
# Tests that when the sole member of a channel quits, the channel is destroyed and recreated fresh with operator status for the next joiner.
CLIENTS C1, C2

# Alice creates #ephemeral
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #ephemeral
C1 EXPECT :Alice!* JOIN #ephemeral

# Alice quits -> #ephemeral is destroyed
C1 SEND QUIT :bye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob connects and joins #ephemeral -> becomes operator
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C2 SEND JOIN #ephemeral
C2 EXPECT :Bob!* JOIN #ephemeral
C2 EXPECT 353 Bob = #ephemeral :@Bob
C2 EXPECT 366 Bob #ephemeral :End of /NAMES list
