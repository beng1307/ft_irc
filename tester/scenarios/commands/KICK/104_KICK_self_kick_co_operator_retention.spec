# 104_KICK_self_kick_co_operator_retention.spec
# Tests that when one operator self-kicks from a channel with multiple operators, the remaining co-operator retains full operator privileges.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Charlie registers
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Alice makes Bob an operator (+o)
C1 SEND MODE #lobby +o Bob
C1 EXPECT :Alice!* MODE #lobby +o Bob
C2 EXPECT :Alice!* MODE #lobby +o Bob

# Alice self-kicks out of #lobby
C1 SEND KICK #lobby Alice :Stepping down
C1 EXPECT :Alice!* KICK #lobby Alice :Stepping down
C2 EXPECT :Alice!* KICK #lobby Alice :Stepping down

# Bob sets channel +i and invites Charlie
C2 SEND MODE #lobby +i
C2 EXPECT :Bob!* MODE #lobby +i
C2 SEND INVITE Charlie #lobby
C2 EXPECT 341 Bob Charlie #lobby
C3 WAIT_RECV :Bob!* INVITE Charlie :#lobby

# Charlie joins #lobby successfully
C3 SEND JOIN #lobby
C3 EXPECT :Charlie!* JOIN #lobby
C2 WAIT_RECV :Charlie!* JOIN #lobby
