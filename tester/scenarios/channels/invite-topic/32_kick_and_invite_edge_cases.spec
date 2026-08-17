# Tests KICK and INVITE edge cases: missing params, non-member kick, non-op invite on +i, already in channel.
CLIENTS C1, C2, C3

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

# OPCMD-07: KICK missing parameters
C1 SEND KICK
C1 EXPECT 461 Alice KICK :*

# OPCMD-06: KICK non-existent channel
C1 SEND KICK #fakechan Bob
C1 EXPECT 403 Alice #fakechan :*

# OPCMD-05: KICK sender not in channel
C2 SEND JOIN #notjoined
C2 EXPECT :Bob!* JOIN #notjoined
C1 SEND KICK #notjoined Bob
C1 EXPECT 442 Alice #notjoined :*

# Alice creates channel and sets invite-only (+i)
C1 SEND JOIN #inviteops
C1 EXPECT :Alice!* JOIN #inviteops
C1 SEND MODE #inviteops +i
C1 EXPECT :Alice!* MODE #inviteops +i

# Alice invites Bob
C1 SEND INVITE Bob #inviteops
C1 EXPECT 341 Alice Bob #inviteops
C2 WAIT_RECV :Alice!* INVITE Bob :#inviteops

# Bob joins channel
C2 SEND JOIN #inviteops
C2 WAIT_RECV :Bob!* JOIN #inviteops
C1 WAIT_RECV :Bob!* JOIN #inviteops

# OPCMD-11: INVITE user already in channel
C1 SEND INVITE Bob #inviteops
C1 EXPECT 443 Alice Bob #inviteops :*

# OPCMD-10: Bob (non-op) attempts INVITE on +i channel -> 482 ERR_CHANOPRIVSNEEDED
C2 SEND INVITE Charlie #inviteops
C2 EXPECT 482 Bob #inviteops :*

# OPCMD-04: Alice kicks Charlie (who is not in the channel) -> 441 ERR_USERNOTINCHANNEL
C1 SEND KICK #inviteops Charlie
C1 EXPECT 441 Alice Charlie #inviteops :*

# OPCMD-02: Alice kicks Bob without trailing reason parameter -> broadcasts kick
C1 SEND KICK #inviteops Bob
C2 WAIT_RECV :Alice!* KICK #inviteops Bob*
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
