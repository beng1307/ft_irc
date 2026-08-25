# 15_NICK_ansi_escape_control_injection.spec
# Malicious actor attempts terminal escape injection / ANSI control sequences in nickname.
# Expected: Server rejects non-printable / escape characters with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND_RAW NICK \x1b[31mHacker15\r\n
C1 EXPECT 432 * * :Erroneous nickname
