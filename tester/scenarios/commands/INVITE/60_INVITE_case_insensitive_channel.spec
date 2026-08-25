# 60_INVITE_case_insensitive_channel.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on channel names during INVITE.
# Expected: Server treats #SecretChan58 and #secretchan58 as identical channels, returning 341 RPL_INVITING.
# Bug: Server performs case-sensitive lookup on channel map, failing with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice58 registers and creates mixed-case invite-only channel
C1 SEND PASS 1234
C1 SEND NICK Ali085
C1 SEND USER ali085 0 * :Ali085
C1 EXPECT 001 Ali085 :*
C1 SEND JOIN #SecretChan58
C1 EXPECT :Ali085!* JOIN #SecretChan58
C1 SEND MODE #SecretChan58 +i
C1 EXPECT :Ali085!* MODE #SecretChan58 +i

# Bob58 registers
C2 SEND PASS 1234
C2 SEND NICK Bob085
C2 SEND USER bob085 0 * :Bob085
C2 EXPECT 001 Bob085 :*

# Alice58 invites Bob58 using lowercase channel name
C1 SEND INVITE Bob085 #secretchan58
C1 EXPECT 341 Ali085 Bob085 #secretchan58
C2 WAIT_RECV :Ali085!* INVITE Bob085 :#secretchan58

# Bob58 joins using mixed-case name
C2 SEND JOIN #SecretChan58
C2 WAIT_RECV :Bob085!* JOIN #SecretChan58
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
