# 286_USER_ansi_escape_injection.spec
# Malicious Actor: ANSI Escape Sequence / Terminal Hijack Injection
# An attacker embeds ANSI escape sequences (\x1b[31;1m) into the username.
# Expected: Server rejects non-alphanumeric characters with 432 Erroneous username or sanitizes them.
# Bug: ANSI sequences are stored raw in username, injecting escape codes into recipient terminals on broadcast.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER \x1b[31;1mRoot\x1b[0m 0 * :Real
C1 EXPECT 432 * :Erroneous username
