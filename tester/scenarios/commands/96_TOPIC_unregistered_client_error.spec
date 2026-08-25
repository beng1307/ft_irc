# 96_TOPIC_unregistered_client_error.spec
# Tests TOPIC issued before completing registration (PASS/NICK/USER)
# Expected: Server replies with 451 ERR_NOTREGISTERED
CLIENTS C1

# Unregistered client sends TOPIC
C1 SEND TOPIC #lobby
C1 EXPECT 451 * :You have not registered

# Unregistered client sends TOPIC with payload
C1 SEND TOPIC #lobby :Premature topic
C1 EXPECT 451 * :You have not registered
