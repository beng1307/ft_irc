# 128_TOPIC_restricted_channel_clear_blocked.spec
# Tests that clearing a topic (TOPIC #chan :) is blocked for non-ops in +t channel
# Expected: Server replies with 482 ERR_CHANOPRIVSNEEDED and topic remains set.
CLIENTS C1, C2

# Alice creates channel, sets +t and topic
C1 SEND PASS 1234
C1 SEND NICK Ali356
C1 SEND USER ali356 0 * :Ali356
C1 EXPECT 001 Ali356 :*
C1 SEND JOIN #restricted
C1 EXPECT :Ali356!* JOIN #restricted
C1 SEND MODE #restricted +t
C1 EXPECT :Ali356!* MODE #restricted +t
C1 SEND TOPIC #restricted :Permanent Notice
C1 EXPECT :Ali356!* TOPIC #restricted :Permanent Notice

# Bob joins
C2 SEND PASS 1234
C2 SEND NICK Bob356
C2 SEND USER bob356 0 * :Bob356
C2 EXPECT 001 Bob356 :*
C2 SEND JOIN #restricted
C2 EXPECT :Bob356!* JOIN #restricted
C1 WAIT_RECV :Bob356!* JOIN #restricted

# Bob attempts to clear topic
C2 SEND TOPIC #restricted :
C2 EXPECT 482 Bob356 #restricted :You're not channel operator

# Verify topic is still intact
C2 SEND TOPIC #restricted
C2 EXPECT 332 Bob356 #restricted :Permanent Notice
