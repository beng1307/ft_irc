# 104_KICK_self_kick_co_operator_retention.spec
# Tests that when one operator self-kicks from a channel with multiple operators, the remaining co-operator retains full operator privileges.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby104K
C1 SEND PASS 1234
C1 SEND NICK Ali125
C1 SEND USER ali125 0 * :Ali125
C1 EXPECT 001 Ali125 :*
C1 SEND JOIN #lobby104K
C1 EXPECT :Ali125!* JOIN #lobby104K

# Bob registers and joins #lobby104K
C2 SEND PASS 1234
C2 SEND NICK Bob125
C2 SEND USER bob125 0 * :Bob125
C2 EXPECT 001 Bob125 :*
C2 SEND JOIN #lobby104K
C2 EXPECT :Bob125!* JOIN #lobby104K
C1 WAIT_RECV :Bob125!* JOIN #lobby104K

# Charlie registers
C3 SEND PASS 1234
C3 SEND NICK Cha125
C3 SEND USER cha125 0 * :Cha125
C3 EXPECT 001 Cha125 :*

# Alice makes Bob an operator (+o)
C1 SEND MODE #lobby104K +o Bob125
C1 EXPECT :Ali125!* MODE #lobby104K +o Bob125
C2 EXPECT :Ali125!* MODE #lobby104K +o Bob125

# Alice self-kicks out of #lobby104K
C1 SEND KICK #lobby104K Ali125 :Stepping down
C1 EXPECT :Ali125!* KICK #lobby104K Ali125 :Stepping down
C2 EXPECT :Ali125!* KICK #lobby104K Ali125 :Stepping down

# Bob sets channel +i and invites Charlie
C2 SEND MODE #lobby104K +i
C2 EXPECT :Bob125!* MODE #lobby104K +i
C2 SEND INVITE Cha125 #lobby104K
C2 EXPECT 341 Bob125 Cha125 #lobby104K
C3 WAIT_RECV :Bob125!* INVITE Cha125 :#lobby104K

# Charlie joins #lobby104K successfully
C3 SEND JOIN #lobby104K
C3 EXPECT :Cha125!* JOIN #lobby104K
C2 WAIT_RECV :Cha125!* JOIN #lobby104K
