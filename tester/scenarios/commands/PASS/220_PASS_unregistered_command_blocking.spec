# 220_PASS_unregistered_command_blocking.spec
# Commands requiring registration sent before PASS must be rejected with ERR_NOTREGISTERED (451)
CLIENTS C1

C1 SEND JOIN #secret
C1 EXPECT 451 * :You have not registered

C1 SEND PRIVMSG Ali248 :hello
C1 EXPECT 451 * :You have not registered

C1 SEND MODE #secret
C1 EXPECT 451 * :You have not registered

C1 SEND TOPIC #secret
C1 EXPECT 451 * :You have not registered

C1 SEND INVITE Bob248 #secret
C1 EXPECT 451 * :You have not registered

C1 SEND KICK #secret Bob248
C1 EXPECT 451 * :You have not registered

C1 SEND PART #secret
C1 EXPECT 451 * :You have not registered
