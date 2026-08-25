# 247_QUIT_modes_and_topic_persistence_after_op_quit.spec
# Tests that when the creator/op quits, channel modes (+k, +t) and topic persist for the promoted operator.
CLIENTS C1, C2, C3

# Alice (C1) and Bob (C2)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Alice creates #secure, sets key and topic restriction
C1 SEND JOIN #secure
C1 EXPECT :Alice!* JOIN #secure
C1 SEND MODE #secure +k passkey
C1 EXPECT :Alice!* MODE #secure +k passkey
C1 SEND MODE #secure +t
C1 EXPECT :Alice!* MODE #secure +t
C1 SEND TOPIC #secure :Classified Topic
C1 EXPECT :Alice!* TOPIC #secure :Classified Topic

# Bob joins with key
C2 SEND JOIN #secure passkey
C2 WAIT_RECV :Bob!* JOIN #secure
C1 WAIT_RECV :Bob!* JOIN #secure

# Alice quits -> Bob is auto-promoted to operator
C1 SEND QUIT :Leaving ops to Bob
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

C2 WAIT_RECV :Alice!* QUIT :Leaving ops to Bob

# Charlie tries to join without key -> rejected 475
C3 SEND JOIN #secure
C3 EXPECT 475 Charlie #secure :Cannot join channel (+k)

# Charlie joins with key -> succeeds
C3 SEND JOIN #secure passkey
C3 EXPECT :Charlie!* JOIN #secure
C3 EXPECT 332 Charlie #secure :Classified Topic

# Charlie tries to change topic -> non-op rejected 482
C3 SEND TOPIC #secure :Hijacked Topic
C3 EXPECT 482 Charlie #secure :You're not channel operator
