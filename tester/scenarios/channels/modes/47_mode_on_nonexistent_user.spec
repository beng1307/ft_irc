# MODE +o on user that's not in channel.
# Tests operator assignment validation.

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

# Alice creates channel
C1 SEND JOIN #operchannel
C1 EXPECT :Alice!* JOIN #operchannel

# Alice tries to OP someone not in channel
C1 SEND MODE #operchannel +o Bob
# Should error: user not in channel (or be ignored)
C1 EXPECT_CONNECTED

# Bob joins
C2 SEND JOIN #operchannel
C2 EXPECT :Bob!* JOIN #operchannel
C1 WAIT_RECV :Bob!* JOIN #operchannel

# Now Alice can OP Bob
C1 SEND MODE #operchannel +o Bob
C1 EXPECT :Alice!* MODE #operchannel +o Bob
C2 WAIT_RECV :Alice!* MODE #operchannel +o Bob

# Charlie joins
C3 SEND JOIN #operchannel
C3 EXPECT :Charlie!* JOIN #operchannel

# Charlie tries to OP someone (he's not op)
# Now Charlie should get error 482 (not channel operator)
C3 SEND MODE #operchannel +o Alice
C3 EXPECT 482 Charlie #operchannel :You're not channel operator

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
