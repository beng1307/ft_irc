# 248_QUIT_privmsg_to_just_quitted_client.spec
# Tests that sending PRIVMSG to a client that just sent QUIT yields 401 ERR_NOSUCHNICK without server errors.
CLIENTS C1, C2

# Alice (C1) and Bob (C2)
C1 SEND PASS 1234
C1 SEND NICK Ali336
C1 SEND USER ali336 0 * :Ali336
C1 EXPECT 001 Ali336 :*

C2 SEND PASS 1234
C2 SEND NICK Bob336
C2 SEND USER bob336 0 * :Bob336
C2 EXPECT 001 Bob336 :*

C1 SEND JOIN #dm
C1 EXPECT :Ali336!* JOIN #dm

C2 SEND JOIN #dm
C2 WAIT_RECV :Bob336!* JOIN #dm
C1 WAIT_RECV :Bob336!* JOIN #dm

# Bob quits
C2 SEND QUIT :Leaving chat
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT

C1 WAIT_RECV :Bob336!* QUIT :Leaving chat

# Alice immediately sends direct PRIVMSG to Bob
C1 SEND PRIVMSG Bob336 :Are you still online?
C1 EXPECT 401 Ali336 Bob336 :No such nick/channel
C1 EXPECT_CONNECTED
