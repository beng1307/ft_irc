# 61_INVITE_case_insensitive_nick.spec
# Tests RFC 1459 / 2812 §1.3 case-insensitivity on target nickname during INVITE.
# Expected: Server matches target nickname 'Bob59' when invited as 'bob59', returning 341 RPL_INVITING.
# Bug: Server performs case-sensitive nickname lookup, failing with 401 ERR_NOSUCHNICK.
CLIENTS C1, C2

# Alice59 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Ali086
C1 SEND USER ali086 0 * :Ali086
C1 EXPECT 001 Ali086 :*
C1 SEND JOIN #priv59
C1 EXPECT :Ali086!* JOIN #priv59
C1 SEND MODE #priv59 +i
C1 EXPECT :Ali086!* MODE #priv59 +i

# Bob59 registers as mixed-case 'Bob59'
C2 SEND PASS 1234
C2 SEND NICK Bob086
C2 SEND USER bob086 0 * :Bob086
C2 EXPECT 001 Bob086 :*

# Alice59 invites Bob59 using lowercase nickname 'bob59'
C1 SEND INVITE bob086 #priv59
C1 EXPECT 341 Ali086 bob086 #priv59
C2 WAIT_RECV :Ali086!* INVITE Bob086 :#priv59
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
