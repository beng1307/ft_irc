# 191_PING_pre_registration_after_wrong_pass.spec
# Tests PING after an incorrect PASS attempt.
# Client should get PONG, but channel operations must remain blocked (ERR_NOTREGISTERED 451).
CLIENTS C1

C1 SEND PASS wrongpassword
C1 EXPECT 464 * :Password incorrect

C1 SEND PING probe
C1 EXPECT :localhost PONG localhost :probe

C1 SEND JOIN #testchan
C1 EXPECT 451 * :You have not registered
