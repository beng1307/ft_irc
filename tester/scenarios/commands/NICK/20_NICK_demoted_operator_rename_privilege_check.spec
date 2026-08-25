# 20_NICK_demoted_operator_rename_privilege_check.spec
# Demoted channel operator changes nickname and attempts to execute operator commands.
# Expected: Renaming does not restore channel operator privileges (+o); KICK is rejected with 482.
CLIENTS C1, C2

# C1 registers as Alice20
C1 SEND PASS 1234
C1 SEND NICK Alice20
C1 SEND USER user20 0 * :Alice 20
C1 EXPECT 001 Alice20 :*

# C2 registers as Bob20
C2 SEND PASS 1234
C2 SEND NICK Bob20
C2 SEND USER user20 0 * :Bob 20
C2 EXPECT 001 Bob20 :*

# Alice creates channel and makes Bob operator
C1 SEND JOIN #test20
C2 SEND JOIN #test20
C1 WAIT_RECV :Bob20!* JOIN #test20

C1 SEND MODE #test20 +o Bob20
C2 WAIT_RECV :Alice20!* MODE #test20 +o Bob20

# Bob demotes Alice from operator
C2 SEND MODE #test20 -o Alice20
C1 WAIT_RECV :Bob20!* MODE #test20 -o Alice20

# Alice renames to Super20
C1 SEND NICK Super20
C2 WAIT_RECV :Alice20!* NICK :Super20

# Super20 attempts to kick Bob -> MUST FAIL with 482 You're not channel operator
C1 SEND KICK #test20 Bob20 :Sneaky kick
C1 EXPECT 482 Super20 #test20 :You're not channel operator

