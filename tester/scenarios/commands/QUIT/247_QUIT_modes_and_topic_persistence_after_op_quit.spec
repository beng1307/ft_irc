# 247_QUIT_modes_and_topic_persistence_after_op_quit.spec
# Tests that when the creator/op quits, channel modes (+k, +t) and topic persist for the promoted operator.
CLIENTS C1, C2, C3

# Alice (C1) and Bob (C2)
C1 SEND PASS 1234
C1 SEND NICK Ali335
C1 SEND USER ali335 0 * :Ali335
C1 EXPECT 001 Ali335 :*

C2 SEND PASS 1234
C2 SEND NICK Bob335
C2 SEND USER bob335 0 * :Bob335
C2 EXPECT 001 Bob335 :*

C3 SEND PASS 1234
C3 SEND NICK Cha335
C3 SEND USER cha335 0 * :Cha335
C3 EXPECT 001 Cha335 :*

# Alice creates #secure, sets key and topic restriction
C1 SEND JOIN #secure
C1 EXPECT :Ali335!* JOIN #secure
C1 SEND MODE #secure +k passkey
C1 EXPECT :Ali335!* MODE #secure +k passkey
C1 SEND MODE #secure +t
C1 EXPECT :Ali335!* MODE #secure +t
C1 SEND TOPIC #secure :Classified Topic
C1 EXPECT :Ali335!* TOPIC #secure :Classified Topic

# Bob joins with key
C2 SEND JOIN #secure passkey
C2 WAIT_RECV :Bob335!* JOIN #secure
C1 WAIT_RECV :Bob335!* JOIN #secure

# Alice quits -> Bob is auto-promoted to operator
C1 SEND QUIT :Leaving ops to Bob335
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

C2 WAIT_RECV :Ali335!* QUIT :Leaving ops to Bob335

# Charlie tries to join without key -> rejected 475
C3 SEND JOIN #secure
C3 EXPECT 475 Cha335 #secure :Cannot join channel (+k)

# Charlie joins with key -> succeeds
C3 SEND JOIN #secure passkey
C3 EXPECT :Cha335!* JOIN #secure
C3 EXPECT 332 Cha335 #secure :Classified Topic

# Charlie tries to change topic -> non-op rejected 482
C3 SEND TOPIC #secure :Hijacked Topic
C3 EXPECT 482 Cha335 #secure :You're not channel operator
