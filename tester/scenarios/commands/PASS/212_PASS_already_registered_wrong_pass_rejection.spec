# 212_PASS_already_registered_wrong_pass_rejection.spec
# Sending wrong password after registration must still return 462 and NOT de-register or change client state
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK PAlice212
C1 SEND USER alice212 0 * :Alice Smith
C1 EXPECT 001 PAlice212 :*

C1 SEND PASS wrongpass
C1 EXPECT 462 PAlice212 :You may not reregister

# Verify client is still registered and functional
C1 SEND JOIN #test212
C1 EXPECT :PAlice212!alice212@localhost JOIN #test212
