# 270_TOPIC_excessive_whitespace_padding.spec
# Tests command parsing with excessive consecutive space delimiters between arguments.
# Expected: Server normalizes space padding and extracts parameters properly.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice sends TOPIC with multiple spaces
C1 SEND TOPIC        #lobby        :SpacedOutTopic
C1 EXPECT :Alice!* TOPIC #lobby :SpacedOutTopic

# Query topic with multiple spaces
C1 SEND TOPIC        #lobby
C1 EXPECT 332 Alice #lobby :SpacedOutTopic
