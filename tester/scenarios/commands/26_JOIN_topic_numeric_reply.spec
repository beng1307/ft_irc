# 26_JOIN_topic_numeric_reply.spec
# Tests RFC 2812 §3.2.1 requirement to send RPL_TOPIC (332) or RPL_NOTOPIC (331) upon successful JOIN
# Expected: Client joining a channel receives the current topic via 332 RPL_TOPIC followed by 353 RPL_NAMREPLY.
# Bug: Server only sends 353/366 replies and never sends topic numerics upon JOIN.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 creates channel and sets a topic
C1 SEND JOIN #topicchan
C1 EXPECT 353 Alice = #topicchan :*
C1 EXPECT 366 Alice #topicchan :End of /NAMES list

C1 SEND TOPIC #topicchan :Welcome to our official channel
C1 EXPECT :Alice!* TOPIC #topicchan :Welcome to our official channel

# C2 joins the channel and expects to receive the channel topic
C2 SEND JOIN #topicchan
C2 EXPECT 332 Bob #topicchan :Welcome to our official channel
C2 EXPECT 353 Bob = #topicchan :*
C2 EXPECT 366 Bob #topicchan :End of /NAMES list

#TODO: Check if it's mandatory
