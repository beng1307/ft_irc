# 212_QUIT_invited_fd_cleanup.spec
# Tests that when an invited client quits before joining, their pending invite is purged so an unauthorized recycled FD cannot enter.
CLIENTS C1, C2, C3

# Alice creates +i channel
C1 SEND PASS 1234
C1 SEND NICK Ali327
C1 SEND USER ali327 0 * :Ali327
C1 EXPECT 001 Ali327 :*

C1 SEND JOIN #vault
C1 EXPECT :Ali327!* JOIN #vault
C1 SEND MODE #vault +i
C1 EXPECT :Ali327!* MODE #vault +i

# Bob connects
C2 SEND PASS 1234
C2 SEND NICK Bob327
C2 SEND USER bob327 0 * :Bob327
C2 EXPECT 001 Bob327 :*

# Alice invites Bob
C1 SEND INVITE Bob327 #vault
C1 EXPECT 341 Ali327 Bob327 #vault
C2 WAIT_RECV :Ali327!* INVITE Bob327 :#vault

# Bob quits without joining
C2 SEND QUIT :Not interested
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT

# Charlie connects and tries to join #vault without invite -> rejected with 473
C3 SEND PASS 1234
C3 SEND NICK Cha327
C3 SEND USER cha327 0 * :Cha327
C3 EXPECT 001 Cha327 :*

C3 SEND JOIN #vault
C3 EXPECT 473 Cha327 #vault :Cannot join channel (+i)
