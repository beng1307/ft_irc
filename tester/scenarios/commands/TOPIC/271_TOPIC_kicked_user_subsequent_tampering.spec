# 271_TOPIC_kicked_user_subsequent_tampering.spec
# Tests that immediately after being kicked, an adversarial client cannot view or modify the channel topic.
# Expected: Server rejects both query and set attempts with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #gated
C1 EXPECT :Alice!* JOIN #gated
C1 SEND TOPIC #gated :Authorized Topic Only
C1 EXPECT :Alice!* TOPIC #gated :Authorized Topic Only

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #gated
C2 EXPECT :Bob!* JOIN #gated
C1 WAIT_RECV :Bob!* JOIN #gated

# Alice kicks Bob
C1 SEND KICK #gated Bob :Rule violation
C1 EXPECT :Alice!* KICK #gated Bob :Rule violation
C2 EXPECT :Alice!* KICK #gated Bob :Rule violation

# Kicked Bob tries to query topic
C2 SEND TOPIC #gated
C2 EXPECT 442 Bob #gated :You're not on that channel

# Kicked Bob tries to overwrite topic
C2 SEND TOPIC #gated :Kicked User Hijack
C2 EXPECT 442 Bob #gated :You're not on that channel
