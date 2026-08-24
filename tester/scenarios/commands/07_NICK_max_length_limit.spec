# 07_NICK_max_length_limit.spec
# Tests RFC nickname length limitation (RFC 1459 max 9 chars, RFC 2812 bounded length).
# Expected: A 50-character nickname is rejected with 432 Erroneous nickname or truncated.
# Bug: The server has no length check, accepting unbounded nicknames that can overflow 512-byte IRC message buffers during broadcast.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK SuperLongNicknameThatExceedsTheRFCMaxLimitOfNineChars
C1 EXPECT 432 * SuperLongNicknameThatExceedsTheRFCMaxLimitOfNineChars :Erroneous nickname
