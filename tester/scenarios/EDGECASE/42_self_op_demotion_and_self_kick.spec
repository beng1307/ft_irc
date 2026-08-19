# Scenario 42: Self Operator Demotion and Self Kick
# Tests operator demoting themselves (-o) and kicking themselves from a channel
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #selfops and Bob joins
C1 SEND JOIN #selfops
C1 EXPECT :Alice!* JOIN #selfops
C2 SEND JOIN #selfops
C2 WAIT_RECV :Bob!* JOIN #selfops

# Alice removes her own operator status
C1 SEND MODE #selfops -o Alice
C1 EXPECT :Alice!* MODE #selfops -o Alice
C2 WAIT_RECV :Alice!* MODE #selfops -o Alice

# Alice tries to op Bob now that she is un-opped (fails with 482)
C1 SEND MODE #selfops +o Bob
C1 EXPECT 482 Alice #selfops :You're not channel operator

# Case 1: Sole member self-kick results in channel destruction (403 ERR_NOSUCHCHANNEL)
# Bob creates #selfkick (sole member) and kicks himself
C2 SEND JOIN #selfkick
C2 EXPECT :Bob!* JOIN #selfkick
C2 SEND KICK #selfkick Bob :Bye myself
C2 EXPECT :Bob!* KICK #selfkick Bob :Bye myself

# Verify channel #selfkick was destroyed when empty (403 ERR_NOSUCHCHANNEL)
C2 SEND PRIVMSG #selfkick :Hello
C2 EXPECT 403 Bob #selfkick :No such channel

# Case 2: Multi-member channel self-kick leaves channel alive (442 ERR_NOTONCHANNEL)
# Alice creates #sharedkick and Bob joins
C1 SEND JOIN #sharedkick
C1 EXPECT :Alice!* JOIN #sharedkick
C2 SEND JOIN #sharedkick
C2 WAIT_RECV :Bob!* JOIN #sharedkick
C1 WAIT_RECV :Bob!* JOIN #sharedkick

# Alice gives Bob operator privileges
C1 SEND MODE #sharedkick +o Bob
C1 EXPECT :Alice!* MODE #sharedkick +o Bob
C2 WAIT_RECV :Alice!* MODE #sharedkick +o Bob

# Bob kicks himself from #sharedkick
C2 SEND KICK #sharedkick Bob :Bye shared
C2 EXPECT :Bob!* KICK #sharedkick Bob :Bye shared
C1 WAIT_RECV :Bob!* KICK #sharedkick Bob :Bye shared

# Verify #sharedkick still exists (Alice is still in it), so Bob gets 442 ERR_NOTONCHANNEL
C2 SEND PRIVMSG #sharedkick :Hello
C2 EXPECT 442 Bob #sharedkick :You're not on that channel

