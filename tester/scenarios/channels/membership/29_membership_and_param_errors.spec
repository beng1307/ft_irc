# Tests channel membership errors, missing params, bare PART, and channel destruction/re-creation.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# CHAN-04: JOIN invalid channel name syntax (missing leading #)
C1 SEND JOIN invalidchannel
C1 EXPECT 403 Alice * :*

# CHAN-05: JOIN missing parameter
C1 SEND JOIN
C1 EXPECT 461 Alice JOIN :*

# CHAN-10: PART channel sender is not on
C1 SEND PART #notjoined
C1 EXPECT 442 Alice #notjoined :*

# CHAN-11: PART non-existent channel
C1 SEND PART #nonexistent
C1 EXPECT 403 Alice #nonexistent :*

# CHAN-12: PART missing parameter
C1 SEND PART
C1 EXPECT 461 Alice PART :*

# Join channel
C1 SEND JOIN #membershiptest
C1 EXPECT :Alice!* JOIN #membershiptest
C2 SEND JOIN #membershiptest
C2 WAIT_RECV :Bob!* JOIN #membershiptest
C1 WAIT_RECV :Bob!* JOIN #membershiptest

# CHAN-06: JOIN already joined channel (server should not duplicate or crash)
C1 SEND JOIN #membershiptest
C1 EXPECT_CONNECTED

# CHAN-08: PART without reason
C2 SEND PART #membershiptest
C1 WAIT_RECV :Bob!* PART #membershiptest*

# CHAN-09: Last user parts channel (channel destroyed) and rejoins (fresh operator)
C1 SEND PART #membershiptest :Bye
C1 WAIT_RECV :Alice!* PART #membershiptest*

# Bob rejoins empty channel, should become operator (@Bob)
C2 SEND JOIN #membershiptest
C2 EXPECT 353 Bob * #membershiptest :*@Bob*
C2 EXPECT_CONNECTED
