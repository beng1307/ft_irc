# 275_TOPIC_spoofed_client_prefix_rejection.spec
# Tests client attempting to forge a server or client prefix on TOPIC command line.
# Expected: Server rejects command starting with colon as 421 ERR_UNKNOWNCOMMAND or invalid command.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali376
C1 SEND USER ali376 0 * :Ali376
C1 EXPECT 001 Ali376 :*
C1 SEND JOIN #lobby275T
C1 EXPECT :Ali376!* JOIN #lobby275T

# Alice attempts to spoof prefix
C1 SEND :FakePrefix TOPIC #lobby275T :SpoofedTopic
C1 EXPECT 421 Ali376 Unknown command.
