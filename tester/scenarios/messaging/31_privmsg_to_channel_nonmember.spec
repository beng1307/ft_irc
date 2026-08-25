# PRIVMSG to channel without being a member.
# Some servers allow this, others reject with 442.
# This test accepts either behavior.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali437
C1 SEND USER ali437 0 * :Ali437
C1 EXPECT 001 Ali437 :*

C2 SEND PASS 1234
C2 SEND NICK Bob437
C2 SEND USER bob437 0 * :Bob437
C2 EXPECT 001 Bob437 :*

# C2 joins #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob437!* JOIN #channel

# C1 sends message to #channel WITHOUT being a member
# Server behavior is implementation-dependent:
# - Some allow it (RFC liberal interpretation)
# - Others reject with 442 (stricter interpretation)
C1 SEND PRIVMSG #channel :Message from non-member

# Either the message is delivered or error is received
# (Both are acceptable implementations)
# C1 should remain connected regardless
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

# Verify normal messaging still works
C1 SEND JOIN #channel
C1 EXPECT :Ali437!* JOIN #channel
C1 SEND PRIVMSG #channel :Now I'm a member
C2 WAIT_RECV :Ali437!* PRIVMSG #channel :Now I'm a member
