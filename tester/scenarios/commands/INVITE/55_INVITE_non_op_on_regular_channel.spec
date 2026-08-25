# 55_INVITE_non_op_on_regular_channel.spec
# Tests RFC 2812 §3.2.7 behavior: Regular members may invite users to public (-i) channels.
# Expected: Server sends 341 RPL_INVITING to Bob53 and delivers INVITE to Charlie53.
# Bug: Server unconditionally requires channel operator rights for all INVITEs, rejecting regular members with 482 ERR_CHANOPRIVSNEEDED.
CLIENTS C1, C2, C3

# Alice53 creates public channel (no +i)
C1 SEND PASS 1234
C1 SEND NICK Alice53
C1 SEND USER alice53 0 * :Alice
C1 EXPECT 001 Alice53 :*
C1 SEND JOIN #pubroom53
C1 EXPECT :Alice53!* JOIN #pubroom53

# Bob53 joins #pubroom53 as regular member (non-op)
C2 SEND PASS 1234
C2 SEND NICK Bob53
C2 SEND USER bob53 0 * :Bob
C2 EXPECT 001 Bob53 :*
C2 SEND JOIN #pubroom53
C2 EXPECT :Bob53!* JOIN #pubroom53

# Charlie53 registers
C3 SEND PASS 1234
C3 SEND NICK Charlie53
C3 SEND USER charlie53 0 * :Charlie
C3 EXPECT 001 Charlie53 :*

# Bob53 (non-op on public channel) invites Charlie53
C2 SEND INVITE Charlie53 #pubroom53
C2 EXPECT 341 Bob53 Charlie53 #pubroom53
C3 WAIT_RECV :Bob53!* INVITE Charlie53 :#pubroom53
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
