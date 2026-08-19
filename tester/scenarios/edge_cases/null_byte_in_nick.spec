CLIENTS C1

# Registration attempt with embedded null byte in nickname
C1 SEND PASS 1234
C1 SEND_RAW NICK ali\x00ce\r\n
C1 SEND USER alice 0 * :Alice

# Assert server doesn't segfault or drop connection ungracefully
C1 EXPECT_CONNECTED

# Test valid registration recovery after malformed binary payload
C1 SEND NICK alice
C1 EXPECT 001 * :*
