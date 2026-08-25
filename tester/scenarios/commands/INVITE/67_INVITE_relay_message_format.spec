# 67_INVITE_relay_message_format.spec
# Tests RFC 2812 standard wire message format for INVITE relay and RPL_INVITING reply.
# Expected: Inviter receives 341 RPL_INVITING, and target receives :Nick!user@host INVITE Target :#channel.
CLIENTS C1, C2

# Alice65 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Ali092
C1 SEND USER ali092 0 * :Ali092
C1 EXPECT 001 Ali092 :*
C1 SEND JOIN #welcome65
C1 EXPECT :Ali092!* JOIN #welcome65

# Bob65 registers
C2 SEND PASS 1234
C2 SEND NICK Bob092
C2 SEND USER bob092 0 * :Bob092
C2 EXPECT 001 Bob092 :*

# Alice65 invites Bob65
C1 SEND INVITE Bob092 #welcome65
C1 EXPECT 341 Ali092 Bob092 #welcome65
C2 WAIT_RECV :Ali092!ali092@localhost INVITE Bob092 :#welcome65
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
