# 72_KICK_not_registered_error.spec
# Tests that an unregistered client attempting to execute KICK is rejected with ERR_NOTREGISTERED (451).
CLIENTS C1

# Unregistered client sends KICK immediately upon connection
C1 SEND KICK #lobby72K Ali127
C1 EXPECT 451 * :You have not registered

# Provide PASS and NICK, but still unregistered (no USER)
C1 SEND PASS 1234
C1 SEND NICK Kicker
C1 SEND KICK #lobby72K Ali127
C1 EXPECT 451 * :You have not registered
