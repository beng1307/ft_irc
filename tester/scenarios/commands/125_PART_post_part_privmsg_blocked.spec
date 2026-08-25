# 125_PART_post_part_privmsg_blocked.spec
# Tests that messages sent to a channel after parting are blocked with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice parts #lobby
C1 SEND PART #lobby :Bye
C1 EXPECT :Alice!* PART #lobby :Bye
C2 EXPECT :Alice!* PART #lobby :Bye

# Alice tries to send PRIVMSG to #lobby
C1 SEND PRIVMSG #lobby :Can you hear me?
C1 EXPECT 442 Alice #lobby :You're not on that channel
