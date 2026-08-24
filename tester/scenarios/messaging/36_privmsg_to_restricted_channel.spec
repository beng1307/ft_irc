# PRIVMSG target is a channel with special modes (invite-only, keyed, limited).
# Sender not in channel - can still send, but may need to handle mode restrictions.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Bob creates channel and sets invite-only
C2 SEND JOIN #secret
C2 EXPECT :Bob!* JOIN #secret
C2 SEND MODE #secret +i
C2 EXPECT :Bob MODE #secret +i *

# Alice (non-member, not invited) sends message
C1 SEND PRIVMSG #secret :Can I message an invite-only channel?
C2 WAIT_RECV :Alice!* PRIVMSG #secret :Can I message an invite-only channel?

# Charlie sends message to the same channel
C3 SEND PRIVMSG #secret :Testing from Charlie
C2 WAIT_RECV :Charlie!* PRIVMSG #secret :Testing from Charlie

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
