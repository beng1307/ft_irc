# 270_TOPIC_excessive_whitespace_padding.spec
# Tests command parsing with excessive consecutive space delimiters between arguments.
# Expected: Server normalizes space padding and extracts parameters properly.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali371
C1 SEND USER ali371 0 * :Ali371
C1 EXPECT 001 Ali371 :*
C1 SEND JOIN #lobby270T
C1 EXPECT :Ali371!* JOIN #lobby270T

# Alice sends TOPIC with multiple spaces
C1 SEND TOPIC        #lobby270T        :SpacedOutTopic
C1 EXPECT :Ali371!* TOPIC #lobby270T :SpacedOutTopic

# Query topic with multiple spaces
C1 SEND TOPIC        #lobby270T
C1 EXPECT 332 Ali371 #lobby270T :SpacedOutTopic
