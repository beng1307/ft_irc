# 35_JOIN_channel_name_invalid_chars.spec
# Tests RFC channel name validation rules:
# 1. Reject channel names containing colons, commas, or control characters.
# 2. Reject channel names exceeding max allowed length (50 characters).
# Expected: Server rejects malformed channel names with 403 No such channel or 479 Illegal channel name.
# Bug: Server accepts arbitrary channel names with unprintable characters or 1000+ length.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali118
C1 SEND USER ali118 0 * :Ali118
C1 EXPECT 001 Ali118 :*

# Attempt to join channel containing colon inside name
C1 SEND JOIN #invalid:name
C1 EXPECT 403 Ali118 #invalid:name :*

# Attempt to join channel containing bell control char
C1 SEND_RAW JOIN #bell\x07chan\r\n
C1 EXPECT 403 Ali118 #bell* :*

# Attempt to join excessively long channel name (> 50 chars)
C1 SEND JOIN #ThisChannelNameIsFarTooLongAndExceedsTheMaximumAllowedLengthOfFiftyCharactersPerRFC2812Specification
C1 EXPECT 403 Ali118 #* :*
