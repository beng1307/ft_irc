# 274_TOPIC_invalid_channel_characters_injection.spec
# Tests TOPIC with malformed/illegal channel targets containing delimiters like commas or colons.
# Expected: Server rejects with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Comma in channel target
C1 SEND TOPIC #chan,illegal :Test
C1 EXPECT 403 Alice #chan,illegal :No such channel

# Colon in channel name
C1 SEND TOPIC #chan:illegal :Test
C1 EXPECT 403 Alice #chan:illegal :No such channel

# Space inside channel name (should parse as separate tokens)
C1 SEND TOPIC #chan name :Test
C1 EXPECT 403 Alice #chan :No such channel
