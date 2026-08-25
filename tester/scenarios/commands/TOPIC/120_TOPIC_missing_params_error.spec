# 120_TOPIC_missing_params_error.spec
# Tests TOPIC without channel parameter
# Expected: Server replies with 461 ERR_NEEDMOREPARAMS
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali348
C1 SEND USER ali348 0 * :Ali348
C1 EXPECT 001 Ali348 :*

# Alice sends TOPIC with no channel
C1 SEND TOPIC
C1 EXPECT 461 Ali348 TOPIC :Not enough parameters
