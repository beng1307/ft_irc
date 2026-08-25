# Scenario 42: Self Operator Demotion and Self Kick
# Tests operator demoting themselves (-o) and kicking themselves from a channel
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali004
C1 SEND USER ali004 0 * :Ali004
C1 EXPECT 001 Ali004 :*

C2 SEND PASS 1234
C2 SEND NICK Bob004
C2 SEND USER bob004 0 * :Bob004
C2 EXPECT 001 Bob004 :*

# Alice creates #selfops42S and Bob joins
C1 SEND JOIN #selfops42S
C1 EXPECT :Ali004!* JOIN #selfops42S
C2 SEND JOIN #selfops42S
C2 WAIT_RECV :Bob004!* JOIN #selfops42S

# Alice removes her own operator status
C1 SEND MODE #selfops42S -o Ali004
C1 EXPECT :Ali004!* MODE #selfops42S -o Ali004
C2 WAIT_RECV :Ali004!* MODE #selfops42S -o Ali004

# Alice tries to op Bob now that she is un-opped (fails with 482)
C1 SEND MODE #selfops42S +o Bob004
C1 EXPECT 482 Ali004 #selfops42S :You're not channel operator

# Case 1: Sole member self-kick results in channel destruction (403 ERR_NOSUCHCHANNEL)
# Bob creates #selfkick (sole member) and kicks himself
C2 SEND JOIN #selfkick
C2 EXPECT :Bob004!* JOIN #selfkick
C2 SEND KICK #selfkick Bob004 :Bye myself
C2 EXPECT :Bob004!* KICK #selfkick Bob004 :Bye myself

# Verify channel #selfkick was destroyed when empty (403 ERR_NOSUCHCHANNEL)
C2 SEND PRIVMSG #selfkick :Hello
C2 EXPECT 403 Bob004 #selfkick :No such channel

# Case 2: Multi-member channel self-kick leaves channel alive (442 ERR_NOTONCHANNEL)
# Alice creates #sharedkick and Bob joins
C1 SEND JOIN #sharedkick
C1 EXPECT :Ali004!* JOIN #sharedkick
C2 SEND JOIN #sharedkick
C2 WAIT_RECV :Bob004!* JOIN #sharedkick
C1 WAIT_RECV :Bob004!* JOIN #sharedkick

# Alice gives Bob operator privileges
C1 SEND MODE #sharedkick +o Bob004
C1 EXPECT :Ali004!* MODE #sharedkick +o Bob004
C2 WAIT_RECV :Ali004!* MODE #sharedkick +o Bob004

# Bob kicks himself from #sharedkick
C2 SEND KICK #sharedkick Bob004 :Bye shared
C2 EXPECT :Bob004!* KICK #sharedkick Bob004 :Bye shared
C1 WAIT_RECV :Bob004!* KICK #sharedkick Bob004 :Bye shared

# Verify #sharedkick still exists (Alice is still in it), so Bob gets 404 ERR_CANNOTSENDTOCHAN
C2 SEND PRIVMSG #sharedkick :Hello
C2 EXPECT 404 Bob004 #sharedkick :Cannot send to channel

