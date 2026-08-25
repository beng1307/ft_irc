# 128_TOPIC_restricted_channel_clear_blocked.spec
# Tests that clearing a topic (TOPIC #chan :) is blocked for non-ops in +t channel
# Expected: Server replies with 482 ERR_CHANOPRIVSNEEDED and topic remains set.
CLIENTS C1, C2

# Alice creates channel, sets +t and topic
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #restricted
C1 EXPECT :Alice!* JOIN #restricted
C1 SEND MODE #restricted +t
C1 EXPECT :Alice!* MODE #restricted +t
C1 SEND TOPIC #restricted :Permanent Notice
C1 EXPECT :Alice!* TOPIC #restricted :Permanent Notice

# Bob joins
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #restricted
C2 EXPECT :Bob!* JOIN #restricted
C1 WAIT_RECV :Bob!* JOIN #restricted

# Bob attempts to clear topic
C2 SEND TOPIC #restricted :
C2 EXPECT 482 Bob #restricted :You're not channel operator

# Verify topic is still intact
C2 SEND TOPIC #restricted
C2 EXPECT 332 Bob #restricted :Permanent Notice
