# 62_INVITE_colon_prefix_channel.spec
# Tests RFC trailing colon parameter notation on channel name (e.g. INVITE Bob :#secret).
# Expected: Server strips leading colon on channel parameter and successfully processes invitation.
# Bug: Server tokenizes literally as ':#secret', looks for channel named ':#secret', and fails with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice60 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Ali087
C1 SEND USER ali087 0 * :Ali087
C1 EXPECT 001 Ali087 :*
C1 SEND JOIN #secret60
C1 EXPECT :Ali087!* JOIN #secret60
C1 SEND MODE #secret60 +i
C1 EXPECT :Ali087!* MODE #secret60 +i

# Bob60 registers
C2 SEND PASS 1234
C2 SEND NICK Bob087
C2 SEND USER bob087 0 * :Bob087
C2 EXPECT 001 Bob087 :*

# Alice60 invites Bob60 using colon-prefixed channel name
C1 SEND INVITE Bob087 :#secret60
C1 EXPECT 341 Ali087 Bob087 #secret60
C2 WAIT_RECV :Ali087!* INVITE Bob087 :#secret60
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
