# 210_QUIT_sole_member_channel_destroyed.spec
# Tests that when the sole member of a channel quits, the channel is destroyed and recreated fresh with operator status for the next joiner.
CLIENTS C1, C2

# Alice creates #ephemeral
C1 SEND PASS 1234
C1 SEND NICK Ali325
C1 SEND USER ali325 0 * :Ali325
C1 EXPECT 001 Ali325 :*

C1 SEND JOIN #ephemeral
C1 EXPECT :Ali325!* JOIN #ephemeral

# Alice quits -> #ephemeral is destroyed
C1 SEND QUIT :bye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob connects and joins #ephemeral -> becomes operator
C2 SEND PASS 1234
C2 SEND NICK Bob325
C2 SEND USER bob325 0 * :Bob325
C2 EXPECT 001 Bob325 :*

C2 SEND JOIN #ephemeral
C2 EXPECT :Bob325!* JOIN #ephemeral
C2 EXPECT 353 Bob325 = #ephemeral :@Bob325
C2 EXPECT 366 Bob325 #ephemeral :End of /NAMES list
