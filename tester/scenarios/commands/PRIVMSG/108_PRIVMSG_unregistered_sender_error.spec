# 108_PRIVMSG_unregistered_sender_error.spec
# Tests PRIVMSG sent by an unregistered client
# Expected: 451 ERR_NOTREGISTERED (:You have not registered)
CLIENTS C1

# C1 attempts to send PRIVMSG before completing registration
C1 SEND PRIVMSG Bob293 :Hello
C1 EXPECT 451 * :You have not registered
