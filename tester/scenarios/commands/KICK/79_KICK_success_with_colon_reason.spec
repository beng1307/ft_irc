# 79_KICK_success_with_colon_reason.spec
# Tests successful KICK with standard colon-prefixed reason.
# Expected: Server broadcasts KICK message to all channel members (including kicked user), and removes target from channel.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby79K (op)
C1 SEND PASS 1234
C1 SEND NICK Ali134
C1 SEND USER ali134 0 * :Ali134
C1 EXPECT 001 Ali134 :*
C1 SEND JOIN #lobby79K
C1 EXPECT :Ali134!* JOIN #lobby79K

# Bob registers and joins #lobby79K
C2 SEND PASS 1234
C2 SEND NICK Bob134
C2 SEND USER bob134 0 * :Bob134
C2 EXPECT 001 Bob134 :*
C2 SEND JOIN #lobby79K
C2 EXPECT :Bob134!* JOIN #lobby79K
C1 WAIT_RECV :Bob134!* JOIN #lobby79K

# Charlie registers and joins #lobby79K
C3 SEND PASS 1234
C3 SEND NICK Cha134
C3 SEND USER cha134 0 * :Cha134
C3 EXPECT 001 Cha134 :*
C3 SEND JOIN #lobby79K
C3 EXPECT :Cha134!* JOIN #lobby79K
C1 WAIT_RECV :Cha134!* JOIN #lobby79K
C2 WAIT_RECV :Cha134!* JOIN #lobby79K

# Alice kicks Bob with colon reason
C1 SEND KICK #lobby79K Bob134 :Bad behavior in channel
C1 EXPECT :Ali134!* KICK #lobby79K Bob134 :Bad behavior in channel
C2 EXPECT :Ali134!* KICK #lobby79K Bob134 :Bad behavior in channel
C3 EXPECT :Ali134!* KICK #lobby79K Bob134 :Bad behavior in channel

# Bob is now no longer on channel, cannot PRIVMSG #lobby79K
C2 SEND PRIVMSG #lobby79K :Am I still here?
C2 EXPECT 404 Bob134 #lobby79K :Cannot send to channel

