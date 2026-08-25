# 06_NICK_numeric_first_char_rejection.spec
# Tests RFC 2812 §2.3.1 rule forbidding nicknames starting with a digit or hyphen.
# Expected: Nickname starting with a digit (e.g. 404Bot) is rejected with 432 Erroneous nickname.
# Bug: hasOnlyAlphaNum("_") permits numbers as the first character, allowing numeric-first nicknames that confuse IRC routing and reply parsers.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK 404Bot
C1 EXPECT 432 * 404Bot :Erroneous nickname
