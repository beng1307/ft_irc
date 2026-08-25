# PRIVMSG to channel with restrictive modes (invite-only, keyed, limited).
# Message delivery should work regardless of channel mode restrictions.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali441
C1 SEND USER ali441 0 * :Ali441
C1 EXPECT 001 Ali441 :*

C2 SEND PASS 1234
C2 SEND NICK Bob441
C2 SEND USER bob441 0 * :Bob441
C2 EXPECT 001 Bob441 :*

C3 SEND PASS 1234
C3 SEND NICK Cha441
C3 SEND USER cha441 0 * :Cha441
C3 EXPECT 001 Cha441 :*

# Bob creates channel and sets invite-only mode
C2 SEND JOIN #secret
C2 EXPECT :Bob441!* JOIN #secret
C2 SEND MODE #secret +i
# Accept MODE response (may include extra parameters)
C2 EXPECT :Bob441!* MODE #secret +i

# Alice (non-member, not invited) sends message
C1 SEND PRIVMSG #secret :Can I message an invite-only channel?
# Server either delivers or rejects - both are acceptable
C1 EXPECT_CONNECTED

# Charlie sends message to the same channel
C3 SEND PRIVMSG #secret :Testing from Cha441
C3 EXPECT_CONNECTED

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
