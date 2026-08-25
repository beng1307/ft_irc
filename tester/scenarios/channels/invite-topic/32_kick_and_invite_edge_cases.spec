# Tests KICK and INVITE edge cases: missing params, non-member kick, non-op invite on +i, already in channel.
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali043
C1 SEND USER ali043 0 * :Ali043
C1 EXPECT 001 Ali043 :*

C2 SEND PASS 1234
C2 SEND NICK Bob043
C2 SEND USER bob043 0 * :Bob043
C2 EXPECT 001 Bob043 :*

C3 SEND PASS 1234
C3 SEND NICK Cha043
C3 SEND USER cha043 0 * :Cha043
C3 EXPECT 001 Cha043 :*

# OPCMD-07: KICK missing parameters
C1 SEND KICK
C1 EXPECT 461 Ali043 KICK :*

# OPCMD-06: KICK non-existent channel
C1 SEND KICK #fakechan Bob043
C1 EXPECT 403 Ali043 #fakechan :*

# OPCMD-05: KICK sender not in channel
C2 SEND JOIN #notjoined
C2 EXPECT :Bob043!* JOIN #notjoined
C1 SEND KICK #notjoined Bob043
C1 EXPECT 442 Ali043 #notjoined :*

# Alice creates channel and sets invite-only (+i)
C1 SEND JOIN #inviteops
C1 EXPECT :Ali043!* JOIN #inviteops
C1 SEND MODE #inviteops +i
C1 EXPECT :Ali043!* MODE #inviteops +i

# Alice invites Bob
C1 SEND INVITE Bob043 #inviteops
C1 EXPECT 341 Ali043 Bob043 #inviteops
C2 WAIT_RECV :Ali043!* INVITE Bob043 :#inviteops

# Bob joins channel
C2 SEND JOIN #inviteops
C2 WAIT_RECV :Bob043!* JOIN #inviteops
C1 WAIT_RECV :Bob043!* JOIN #inviteops

# OPCMD-11: INVITE user already in channel
C1 SEND INVITE Bob043 #inviteops
C1 EXPECT 443 Ali043 Bob043 #inviteops :*

# OPCMD-10: Bob (non-op) attempts INVITE on +i channel -> 482 ERR_CHANOPRIVSNEEDED
C2 SEND INVITE Cha043 #inviteops
C2 EXPECT 482 Bob043 #inviteops :*

# OPCMD-04: Alice kicks Charlie (who is not in the channel) -> 441 ERR_USERNOTINCHANNEL
C1 SEND KICK #inviteops Cha043
C1 EXPECT 441 Ali043 Cha043 #inviteops :*

# OPCMD-02: Alice kicks Bob without trailing reason parameter -> broadcasts kick
C1 SEND KICK #inviteops Bob043
C2 WAIT_RECV :Ali043!* KICK #inviteops Bob043*
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
