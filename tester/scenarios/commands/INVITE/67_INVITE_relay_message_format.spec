# 67_INVITE_relay_message_format.spec
# Tests RFC 2812 standard wire message format for INVITE relay and RPL_INVITING reply.
# Expected: Inviter receives 341 RPL_INVITING, and target receives :Nick!user@host INVITE Target :#channel.
CLIENTS C1, C2

# Alice65 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Alice65
C1 SEND USER alice65 0 * :Alice
C1 EXPECT 001 Alice65 :*
C1 SEND JOIN #welcome65
C1 EXPECT :Alice65!* JOIN #welcome65

# Bob65 registers
C2 SEND PASS 1234
C2 SEND NICK Bob65
C2 SEND USER bob65 0 * :Bob
C2 EXPECT 001 Bob65 :*

# Alice65 invites Bob65
C1 SEND INVITE Bob65 #welcome65
C1 EXPECT 341 Alice65 Bob65 #welcome65
C2 WAIT_RECV :Alice65!alice65@localhost INVITE Bob65 :#welcome65
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
