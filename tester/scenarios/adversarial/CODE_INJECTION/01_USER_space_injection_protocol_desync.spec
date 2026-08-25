# 01_USER_space_injection_protocol_desync.spec
# Vulnerability: USER command does not validate username and allows space-injected strings.
# Expected secure behavior: Server must reject usernames with spaces (e.g. 468 or 461)
# and never allow an attacker to forge IRC command prefixes (e.g. ":Attacker!admin PRIVMSG #target@localhost").
CLIENTS C1, C2

# C1 attempts registering with a space-injected username designed to split the prefix
C1 SEND PASS 1234
C1 SEND NICK Infiltrator
C1 SEND USER :admin PRIVMSG #secret 0 * :RealName
C1 EXPECT 468 * * :*

# If server incorrectly accepted it, C1 would be registered, but secure server denies registration.
C1 EXPECT_NONE 200ms
