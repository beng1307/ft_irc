# 178_USER_invalid_username_characters.spec
# Tests rejection or sanitization of invalid username characters ('!', '@', control characters)
# Expected: Server rejects username containing '!' or '@' with 432 Erroneous nickname/username,
# or prevents hostmask corruption.
# Bug: Server accepts 'admin!root@evil' directly, generating ':Alice!admin!root@evil@localhost'
# which breaks downstream RFC client parsers.
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob400
C2 SEND USER bob400 0 * :Bob400
C2 EXPECT 001 Bob400 :*
C2 SEND JOIN #security
C2 EXPECT 353 Bob400 = #security :@Bob400

C1 SEND PASS 1234
C1 SEND NICK Ali400
C1 SEND USER admin!root@evil 0 * :Ali400
C1 EXPECT 432 * :Erroneous nickname
