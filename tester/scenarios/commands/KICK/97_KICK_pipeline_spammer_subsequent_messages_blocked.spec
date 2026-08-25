# 97_KICK_pipeline_spammer_subsequent_messages_blocked.spec
# Tests that when a malicious spammer has queued messages in the pipeline, executing KICK immediately invalidates channel membership and blocks subsequent pipelined messages.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby (op)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Charlie registers and joins #lobby (listener)
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #lobby
C3 EXPECT :Charlie!* JOIN #lobby
C1 WAIT_RECV :Charlie!* JOIN #lobby

# Spammer Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby
C3 WAIT_RECV :Bob!* JOIN #lobby

# Spammer sends message 1
C2 SEND PRIVMSG #lobby :Spam 1
C1 WAIT_RECV :Bob!* PRIVMSG #lobby :Spam 1
C3 WAIT_RECV :Bob!* PRIVMSG #lobby :Spam 1

# Operator kicks Spammer
C1 SEND KICK #lobby Bob :Spamming prohibited
C1 EXPECT :Alice!* KICK #lobby Bob :Spamming prohibited
C2 EXPECT :Alice!* KICK #lobby Bob :Spamming prohibited
C3 EXPECT :Alice!* KICK #lobby Bob :Spamming prohibited

# Spammer sends subsequent messages in pipeline
C2 SEND PRIVMSG #lobby :Spam 2
C2 EXPECT 404 Bob #lobby :Cannot send to channel
C2 SEND PRIVMSG #lobby :Spam 3
C2 EXPECT 404 Bob #lobby :Cannot send to channel


# Ensure listener Charlie received NO further spam
C3 EXPECT_CONNECTED
