# 36_JOIN_not_registered_error.spec
# Tests that an unauthenticated / unregistered client cannot execute JOIN
# Expected: Server returns 451 :You have not registered.
CLIENTS C1

# Send JOIN immediately upon connecting without PASS, NICK, or USER
C1 SEND JOIN #lobby
C1 EXPECT 451 * :You have not registered

# Provide PASS and NICK, but still missing USER
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND JOIN #lobby
C1 EXPECT 451 * :You have not registered
