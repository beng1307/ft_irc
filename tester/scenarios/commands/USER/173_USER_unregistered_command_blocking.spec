# 173_USER_unregistered_command_blocking.spec
# Tests that a client who has only sent USER is blocked from operational commands (JOIN, PRIVMSG, etc.)
CLIENTS C1

C1 SEND USER ali395 0 * :Ali395 Smith

C1 SEND JOIN #chan
C1 EXPECT 451 * :You have not registered

C1 SEND PRIVMSG #chan :hello
C1 EXPECT 451 * :You have not registered
