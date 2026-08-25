# 22_NICK_null_byte_truncation_injection.spec
# Malicious actor attempts null-byte injection (\0) inside the NICK parameter.
# Expected: Server rejects binary/null payload with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND_RAW NICK Ali204\x00Hacker22\r\n
C1 EXPECT 432 * * :Erroneous nickname
