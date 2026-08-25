# 211_PASS_already_registered_rejection.spec
# Sending PASS after registration is complete must return ERR_ALREADYREGISTRED (462)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK PassAlice211
C1 SEND USER alice211 0 * :Alice Smith
C1 EXPECT 001 PassAlice211 :*

C1 SEND PASS 1234
C1 EXPECT 462 PassAlice211 :You may not reregister
