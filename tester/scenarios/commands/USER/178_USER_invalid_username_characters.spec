# 178_USER_invalid_username_characters.spec
# Tests rejection or sanitization of invalid username characters ('!', '@', control characters)
# Expected: Server rejects username containing '!' or '@' with 432 Erroneous nickname/username,
# or prevents hostmask corruption.
# Bug: Server accepts 'admin!root@evil' directly, generating ':Alice!admin!root@evil@localhost'
# which breaks downstream RFC client parsers.
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #security
C2 EXPECT 353 Bob = #security :@Bob

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER admin!root@evil 0 * :Alice
C1 EXPECT 432 * :Erroneous nickname
