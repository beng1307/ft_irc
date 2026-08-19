CLIENTS C1

# Send registration with embedded null byte and control chars in nick
C1 SEND PASS 1234
C1 SEND_RAW NICK al\x00ice\r\n
C1 SEND_RAW USER ali\x00ce 0 * :Alice\r\n

# Server should reject invalid nick or sanitize without crashing
C1 EXPECT_CONNECTED

# Test valid registration recovery after malformed binary payload
C1 SEND NICK alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 * :*
