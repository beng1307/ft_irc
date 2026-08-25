# 51_INVITE_nonexistent_channel.spec
# Tests INVITE issued to a non-existent channel.
# Expected: Server rejects with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice51
C1 SEND USER alice51 0 * :Alice
C1 EXPECT 001 Alice51 :*

# Invite to non-existent channel
C1 SEND INVITE Bob51 #nonexistent
C1 EXPECT 403 Alice51 #nonexistent :No such channel
C1 EXPECT_CONNECTED
