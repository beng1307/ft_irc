# 280_USER_overlength_dos_broadcast_overflow.spec
# Malicious Actor: USERLEN Denial of Service / Message Boundary Overflow
# An attacker supplies a 400-character username to cause downstream broadcasts to exceed 512 bytes.
# Expected: Server enforces USERLEN limit (e.g. max 10 or 32 chars) and rejects or truncates username.
# Bug: 400-char username accepted, causing make_msg to produce lines exceeding MAX_IRC_LINE_CONTENT_LENGTH.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali402
C1 SEND USER aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 0 * :Real
C1 EXPECT 432 Ali402 * :Erroneous nickname
