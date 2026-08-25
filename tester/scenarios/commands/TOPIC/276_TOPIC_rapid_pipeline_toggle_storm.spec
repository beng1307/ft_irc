# 276_TOPIC_rapid_pipeline_toggle_storm.spec
# Tests pipelined flood of rapid consecutive TOPIC updates within a single TCP packet.
# Expected: Server processes commands sequentially without state corruption; final topic is accurately set.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #stream
C1 EXPECT :Alice!* JOIN #stream

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #stream
C2 EXPECT :Bob!* JOIN #stream
C1 WAIT_RECV :Bob!* JOIN #stream

# Pipelined burst of topic updates
C1 SEND_RAW TOPIC #stream :Phase 1\r\nTOPIC #stream :Phase 2\r\nTOPIC #stream :Phase 3\r\nTOPIC #stream :Final Phase\r\n
C1 EXPECT :Alice!* TOPIC #stream :Phase 1
C1 EXPECT :Alice!* TOPIC #stream :Phase 2
C1 EXPECT :Alice!* TOPIC #stream :Phase 3
C1 EXPECT :Alice!* TOPIC #stream :Final Phase

# Bob queries final topic
C2 SEND TOPIC #stream
C2 EXPECT 332 Bob #stream :Final Phase
