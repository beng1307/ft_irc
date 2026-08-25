# 02_USER_forbidden_characters_injection.spec
# Vulnerability: USER command allows '@', '!', control codes, and ANSI sequences into username field.
# Expected secure behavior: Server must reject usernames with forbidden characters with error reply (468)
# and prevent spoofing user!host masks.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER evil!admin@attacker.com 0 * :Alice User
C1 EXPECT 468 * * :*

C1 EXPECT_NONE 200ms
