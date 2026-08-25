# 08_NICK_embedded_null_byte_truncation.spec
# Vulnerability: Embedded null byte (\x00) inside NICK parameter causes discrepancy
# between binary std::string length and C-string / stream parsing, leading to truncated log inspection.
# Expected secure behavior: Server must reject null bytes in nickname with 432 Erroneous nickname,
# without truncating error reply or corrupting downstream parser state.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND_RAW NICK Alice\x00InjectedSuffix\r\n
C1 EXPECT 432 *

C1 EXPECT_NONE 200ms
