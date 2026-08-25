# 05_NICK_rfc_special_characters.spec
# Tests RFC 1459 §2.3.1 allowed special characters in nicknames: []\`_^{}|-
# Expected: Nicknames containing valid brackets, pipes, and hyphens are accepted.
# Bug: is_valid_nickname uses hasOnlyAlphaNum("_"), which rejects valid RFC nicknames with 432 Erroneous nickname.
CLIENTS C1, C2

# C1 registers with brackets and caret
C1 SEND PASS 1234
C1 SEND NICK [Bot05]^1
C1 SEND USER bot05 0 * :Bot 05
C1 EXPECT 001 [Bot05]^1 :*

# C2 registers with pipe and hyphen
C2 SEND PASS 1234
C2 SEND NICK alice|-
C2 SEND USER alice 0 * :Alice
C2 EXPECT 001 alice|- :*

