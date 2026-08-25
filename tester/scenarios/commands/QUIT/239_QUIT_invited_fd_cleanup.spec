# 212_QUIT_invited_fd_cleanup.spec
# Tests that when an invited client quits before joining, their pending invite is purged so an unauthorized recycled FD cannot enter.
CLIENTS C1, C2, C3

# Alice creates +i channel
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #vault
C1 EXPECT :Alice!* JOIN #vault
C1 SEND MODE #vault +i
C1 EXPECT :Alice!* MODE #vault +i

# Bob connects
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice invites Bob
C1 SEND INVITE Bob #vault
C1 EXPECT 341 Alice Bob #vault
C2 WAIT_RECV :Alice!* INVITE Bob :#vault

# Bob quits without joining
C2 SEND QUIT :Not interested
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT

# Charlie connects and tries to join #vault without invite -> rejected with 473
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C3 SEND JOIN #vault
C3 EXPECT 473 Charlie #vault :Cannot join channel (+i)
