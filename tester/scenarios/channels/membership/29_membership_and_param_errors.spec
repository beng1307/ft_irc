# Tests channel membership errors, missing params, bare PART, and channel destruction/re-creation.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali047
C1 SEND USER ali047 0 * :Ali047
C1 EXPECT 001 Ali047 :*

C2 SEND PASS 1234
C2 SEND NICK Bob047
C2 SEND USER bob047 0 * :Bob047
C2 EXPECT 001 Bob047 :*

# CHAN-04: JOIN invalid channel name syntax (missing leading #)
 C1 SEND JOIN invalidchannel
 C1 EXPECT 403 Ali047 * :*

# CHAN-05: JOIN missing parameter
C1 SEND JOIN
C1 EXPECT 461 Ali047 JOIN :*

# CHAN-10: PART channel sender is not on
C2 SEND JOIN #notjoined
C2 EXPECT :Bob047!* JOIN #notjoined
C1 SEND PART #notjoined
C1 EXPECT 442 Ali047 #notjoined :*

# CHAN-11: PART non-existent channel
C1 SEND PART #nonexistent
C1 EXPECT 403 Ali047 #nonexistent :*

# CHAN-12: PART missing parameter
C1 SEND PART
C1 EXPECT 461 Ali047 PART :*

# Join channel
C1 SEND JOIN #membershiptest
C1 EXPECT :Ali047!* JOIN #membershiptest
C2 SEND JOIN #membershiptest
C2 WAIT_RECV :Bob047!* JOIN #membershiptest
C1 WAIT_RECV :Bob047!* JOIN #membershiptest

# CHAN-06: JOIN already joined channel (server should not duplicate or crash)
C1 SEND JOIN #membershiptest
C1 EXPECT_CONNECTED

# CHAN-08: PART without reason
C2 SEND PART #membershiptest
C1 WAIT_RECV :Bob047!* PART #membershiptest*

# CHAN-09: Last user parts channel (channel destroyed) and rejoins (fresh operator)
C1 SEND PART #membershiptest :Bye
C1 WAIT_RECV :Ali047!* PART #membershiptest*

# Bob rejoins empty channel, should become operator (@Bob)
C2 SEND JOIN #membershiptest
C2 EXPECT 353 Bob047 * #membershiptest :*@Bob047*
C2 EXPECT_CONNECTED
