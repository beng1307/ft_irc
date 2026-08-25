# MODE +o on user that's not in channel.
# Tests operator assignment validation.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali060
C1 SEND USER ali060 0 * :Ali060
C1 EXPECT 001 Ali060 :*

C2 SEND PASS 1234
C2 SEND NICK Bob060
C2 SEND USER bob060 0 * :Bob060
C2 EXPECT 001 Bob060 :*

C3 SEND PASS 1234
C3 SEND NICK Cha060
C3 SEND USER cha060 0 * :Cha060
C3 EXPECT 001 Cha060 :*

# Alice creates channel
C1 SEND JOIN #operchannel
C1 EXPECT :Ali060!* JOIN #operchannel

# Alice tries to OP someone not in channel
C1 SEND MODE #operchannel +o Bob060
# Should error: user not in channel (or be ignored)
C1 EXPECT_CONNECTED

# Bob joins
C2 SEND JOIN #operchannel
C2 EXPECT :Bob060!* JOIN #operchannel
C1 WAIT_RECV :Bob060!* JOIN #operchannel

# Now Alice can OP Bob
C1 SEND MODE #operchannel +o Bob060
C1 EXPECT :Ali060!* MODE #operchannel +o Bob060
C2 WAIT_RECV :Ali060!* MODE #operchannel +o Bob060

# Charlie joins
C3 SEND JOIN #operchannel
C3 EXPECT :Cha060!* JOIN #operchannel

# Charlie tries to OP someone (he's not op)
# Now Charlie should get error 482 (not channel operator)
C3 SEND MODE #operchannel +o Ali060
C3 EXPECT 482 Cha060 #operchannel :You're not channel operator

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
