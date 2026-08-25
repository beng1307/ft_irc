# 271_TOPIC_kicked_user_subsequent_tampering.spec
# Tests that immediately after being kicked, an adversarial client cannot view or modify the channel topic.
# Expected: Server rejects both query and set attempts with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali372
C1 SEND USER ali372 0 * :Ali372
C1 EXPECT 001 Ali372 :*
C1 SEND JOIN #gated
C1 EXPECT :Ali372!* JOIN #gated
C1 SEND TOPIC #gated :Authorized Topic Only
C1 EXPECT :Ali372!* TOPIC #gated :Authorized Topic Only

C2 SEND PASS 1234
C2 SEND NICK Bob372
C2 SEND USER bob372 0 * :Bob372
C2 EXPECT 001 Bob372 :*
C2 SEND JOIN #gated
C2 EXPECT :Bob372!* JOIN #gated
C1 WAIT_RECV :Bob372!* JOIN #gated

# Alice kicks Bob
C1 SEND KICK #gated Bob372 :Rule violation
C1 EXPECT :Ali372!* KICK #gated Bob372 :Rule violation
C2 EXPECT :Ali372!* KICK #gated Bob372 :Rule violation

# Kicked Bob tries to query topic
C2 SEND TOPIC #gated
C2 EXPECT 442 Bob372 #gated :You're not on that channel

# Kicked Bob tries to overwrite topic
C2 SEND TOPIC #gated :Kicked Usr372 Hijack
C2 EXPECT 442 Bob372 #gated :You're not on that channel
