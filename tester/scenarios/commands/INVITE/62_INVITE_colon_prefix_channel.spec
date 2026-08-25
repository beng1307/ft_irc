# 62_INVITE_colon_prefix_channel.spec
# Tests RFC trailing colon parameter notation on channel name (e.g. INVITE Bob :#secret).
# Expected: Server strips leading colon on channel parameter and successfully processes invitation.
# Bug: Server tokenizes literally as ':#secret', looks for channel named ':#secret', and fails with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice60 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Alice60
C1 SEND USER alice60 0 * :Alice
C1 EXPECT 001 Alice60 :*
C1 SEND JOIN #secret60
C1 EXPECT :Alice60!* JOIN #secret60
C1 SEND MODE #secret60 +i
C1 EXPECT :Alice60!* MODE #secret60 +i

# Bob60 registers
C2 SEND PASS 1234
C2 SEND NICK Bob60
C2 SEND USER bob60 0 * :Bob
C2 EXPECT 001 Bob60 :*

# Alice60 invites Bob60 using colon-prefixed channel name
C1 SEND INVITE Bob60 :#secret60
C1 EXPECT 341 Alice60 Bob60 #secret60
C2 WAIT_RECV :Alice60!* INVITE Bob60 :#secret60
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
