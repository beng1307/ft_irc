# 143_PART_not_registered_error.spec
# Tests ERR_NOTREGISTERED (451) when unauthenticated/unregistered client executes PART
CLIENTS C1

# Unregistered client sends PART immediately
C1 SEND PART #lobby143P
C1 EXPECT 451 * :You have not registered

# Client provides PASS and NICK, but still unregistered
C1 SEND PASS 1234
C1 SEND NICK Ali212
C1 SEND PART #lobby143P
C1 EXPECT 451 * :You have not registered
