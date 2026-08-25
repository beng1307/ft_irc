# 97_KICK_pipeline_spammer_subsequent_messages_blocked.spec
# Tests that when a malicious spammer has queued messages in the pipeline, executing KICK immediately invalidates channel membership and blocks subsequent pipelined messages.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby (op)
C1 SEND PASS 1234
C1 SEND NICK Ali152
C1 SEND USER ali152 0 * :Ali152
C1 EXPECT 001 Ali152 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali152!* JOIN #lobby

# Charlie registers and joins #lobby (listener)
C3 SEND PASS 1234
C3 SEND NICK Cha152
C3 SEND USER cha152 0 * :Cha152
C3 EXPECT 001 Cha152 :*
C3 SEND JOIN #lobby
C3 EXPECT :Cha152!* JOIN #lobby
C1 WAIT_RECV :Cha152!* JOIN #lobby

# Spammer Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob152
C2 SEND USER bob152 0 * :Bob152
C2 EXPECT 001 Bob152 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob152!* JOIN #lobby
C1 WAIT_RECV :Bob152!* JOIN #lobby
C3 WAIT_RECV :Bob152!* JOIN #lobby

# Spammer sends message 1
C2 SEND PRIVMSG #lobby :Spam 1
C1 WAIT_RECV :Bob152!* PRIVMSG #lobby :Spam 1
C3 WAIT_RECV :Bob152!* PRIVMSG #lobby :Spam 1

# Operator kicks Spammer
C1 SEND KICK #lobby Bob152 :Spamming prohibited
C1 EXPECT :Ali152!* KICK #lobby Bob152 :Spamming prohibited
C2 EXPECT :Ali152!* KICK #lobby Bob152 :Spamming prohibited
C3 EXPECT :Ali152!* KICK #lobby Bob152 :Spamming prohibited

# Spammer sends subsequent messages in pipeline
C2 SEND PRIVMSG #lobby :Spam 2
C2 EXPECT 404 Bob152 #lobby :Cannot send to channel
C2 SEND PRIVMSG #lobby :Spam 3
C2 EXPECT 404 Bob152 #lobby :Cannot send to channel


# Ensure listener Charlie received NO further spam
C3 EXPECT_CONNECTED
