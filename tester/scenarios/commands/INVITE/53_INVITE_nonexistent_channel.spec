# 53_INVITE_nonexistent_channel.spec
# Tests INVITE issued to a non-existent channel.
# Expected: Server rejects with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali078
C1 SEND USER ali078 0 * :Ali078
C1 EXPECT 001 Ali078 :*

# Invite to non-existent channel
C1 SEND INVITE Bob078 #nonexistent
C1 EXPECT 403 Ali078 #nonexistent :No such channel
C1 EXPECT_CONNECTED
