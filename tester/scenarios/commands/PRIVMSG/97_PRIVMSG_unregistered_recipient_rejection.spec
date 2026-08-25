# 97_PRIVMSG_unregistered_recipient_rejection.spec
# Tests sending PRIVMSG to an unregistered client who only set NICK but not PASS/USER
# Expected: Sender receives 401 ERR_NOSUCHNICK, unregistered client receives nothing
# Bug: Server delivers PRIVMSG to unregistered client because send_message_to_user doesn't check get_register_status()
CLIENTS C1, C2

# Setup C1 (Registered)
C1 SEND PASS 1234
C1 SEND NICK Ali311
C1 SEND USER ali311 0 * :Ali311
C1 EXPECT 001 Ali311 :*

# Setup C2 (Unregistered - only sets NICK)
C2 SEND NICK Bob311

# C1 attempts to send private message to unregistered Bob
C1 SEND PRIVMSG Bob311 :Secret message
C1 EXPECT 401 Ali311 Bob311 :No such nick/channel
C2 NO_RECV :Ali311!* PRIVMSG Bob311 :Secret message
