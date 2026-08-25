# 52_MODE_unauthorized_non_operator_privilege_escalation.spec
# Adversarial Attack: Regular channel member attempts to escalate privileges by executing unauthorized MODE changes.
# Expected: Server rejects every unauthorized attempt with 482 ERR_CHANOPRIVSNEEDED without modifying channel state.
CLIENTS C1, C2

# C1 is operator Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 is regular member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #vault
C1 EXPECT 353 Alice = #vault :@Alice
C1 EXPECT 366 Alice #vault :End of /NAMES list

C2 SEND JOIN #vault
C1 WAIT_RECV :Bob!* JOIN #vault

# Bob attempts unauthorized self-promotion
C2 SEND MODE #vault +o Bob
C2 EXPECT 482 Bob #vault :You're not channel operator

# Bob attempts unauthorized operator demotion
C2 SEND MODE #vault -o Alice
C2 EXPECT 482 Bob #vault :You're not channel operator

# Bob attempts unauthorized key lock
C2 SEND MODE #vault +k hackpass
C2 EXPECT 482 Bob #vault :You're not channel operator

# Bob attempts unauthorized invite-only flag
C2 SEND MODE #vault +i
C2 EXPECT 482 Bob #vault :You're not channel operator

# Bob attempts unauthorized user limit
C2 SEND MODE #vault +l 1
C2 EXPECT 482 Bob #vault :You're not channel operator

# Bob attempts unauthorized topic restriction
C2 SEND MODE #vault +t
C2 EXPECT 482 Bob #vault :You're not channel operator

# Alice verifies that no modes were altered
C1 SEND MODE #vault
C1 EXPECT 324 Alice #vault +
