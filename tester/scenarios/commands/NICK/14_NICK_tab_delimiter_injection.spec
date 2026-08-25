# 14_NICK_tab_delimiter_injection.spec
# Malicious actor uses tab characters (\t) instead of spaces (\x20).
# Expected: Server strictly respects space-delimited IRC grammar and rejects tab-delimited commands with ERR_UNKNOWNCOMMAND (421).
CLIENTS C1

C1 SEND PASS 1234
C1 SEND_RAW NICK\tAlice14\r\n
C1 EXPECT 421 * Unknown command.
C1 EXPECT_CONNECTED
